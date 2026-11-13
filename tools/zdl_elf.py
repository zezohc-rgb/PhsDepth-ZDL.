"""Small ELF32 reader/repacker for hash-locked ZDL research (little endian)."""
import struct


def align(n, a): return (n + max(a,1)-1) & ~(max(a,1)-1)


class Elf:
    def __init__(self, data):
        self.header=bytearray(data[:52]); self.sections=[]
        if data[:7]!=b'\x7fELF\x01\x01\x01': raise ValueError('expected ELF32 LE')
        off=struct.unpack_from('<I',data,32)[0]
        ents,num,names=struct.unpack_from('<HHH',data,46)
        if ents!=40: raise ValueError('bad section headers')
        for i in range(num):
            w=list(struct.unpack_from('<10I',data,off+40*i))
            self.sections.append({'index':i,'words':w,'data':bytearray(data[w[4]:w[4]+w[5]]) if w[1]!=8 else bytearray()})
        strings=self.sections[names]['data']
        for s in self.sections: s['name']=self.cstr(strings,s['words'][0])

    @staticmethod
    def cstr(raw, off): return bytes(raw[off:raw.index(0,off)]).decode('ascii')

    def section(self,name):
        return next(s for s in self.sections if s['name']==name and s['words'][5])

    def symbols(self, name='.symtab'):
        s=self.section(name); strings=self.sections[s['words'][6]]['data']; out=[]
        for off in range(0,len(s['data']),16):
            w=list(struct.unpack_from('<IIIBBH',s['data'],off))
            out.append({'name':self.cstr(strings,w[0]),'words':w})
        return out

    def relocations(self, name):
        return [list(struct.unpack_from('<IIi',self.section(name)['data'],i)) for i in range(0,len(self.section(name)['data']),12)]

    def replace_symbols(self,name,syms):
        self.section(name)['data']=bytearray(b''.join(struct.pack('<IIIBBH',*s['words']) for s in syms))

    def pack(self,entry):
        # Retain section indices and links, regenerate offsets and program headers.
        out=bytearray(64)
        for s in self.sections[1:]:
            w=s['words']
            if w[1]==8: w[4]=0; continue
            out.extend(bytes(align(len(out),w[8])-len(out)))
            w[4]=len(out);w[5]=len(s['data']);out.extend(s['data'])
        out.extend(bytes(align(len(out),4)-len(out)));phoff=len(out)
        for name,flags in [('.text',5),('.const',4),('.fardata',6)]:
            s=self.section(name);w=s['words']
            out.extend(struct.pack('<8I',1,w[4],w[3],w[3],w[5],w[5],flags,w[8]))
        w=self.section('.dynamic')['words']
        out.extend(struct.pack('<8I',2,w[4],0,0,w[5],0,6,0))
        shoff=len(out)
        for s in self.sections: out.extend(struct.pack('<10I',*s['words']))
        h=self.header;struct.pack_into('<III',h,24,entry,phoff,shoff)
        struct.pack_into('<HH',h,42,32,4)
        out[:52]=h
        return bytes(out)
