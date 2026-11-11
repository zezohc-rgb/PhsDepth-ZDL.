#!/usr/bin/env python3
"""Independent structural checks, NOT a firmware/hardware compatibility proof."""
import argparse
import hashlib
import json
from pathlib import Path
import struct

ROOT=Path(__file__).resolve().parents[1]


def validate(data, manifest):
    def require(condition,message):
        if not condition:raise ValueError(message)
    require(len(data)>=128,'truncated ZDL')
    require(data[:8]==b'\0\0\0\0SIZE' and data[20:24]==b'INFO','bad ZDL header')
    require(struct.unpack_from('<II',data,8)==(8,56),'unexpected SIZE shape')
    require(struct.unpack_from('<I',data,24)[0]==48,'unexpected INFO size')
    require(struct.unpack_from('<I',data,16)[0]+76==len(data),'SIZE length mismatch')
    require(data[28:60].startswith(b'ZOOM EFFECT DLL SYSTEM VER 1.00'),'bad version')
    require(data[60]==manifest['gid'] and struct.unpack_from('<H',data,64)[0]==manifest['fxid'],'effect identity mismatch')
    require(data[68:72]==manifest['fxid_version'].encode(),'effect version mismatch')
    require(len(data)<=32126,'over upstream proven file size cap')
    e=data[76:]
    require(e[:7]==b'\x7fELF\x01\x01\x01','not ELF32 little-endian')
    require(struct.unpack_from('<HH',e,16)==(3,140),'not C6000 shared object')
    off=struct.unpack_from('<I',e,32)[0];sz,n,idx=struct.unpack_from('<HHH',e,46)
    require(sz==40 and 0<idx<n and off+sz*n<=len(e),'bad section table')
    sections=[struct.unpack_from('<10I',e,off+i*sz) for i in range(n)]
    def contents(s):
        require(s[4]+s[5]<=len(e),'section outside file')
        return e[s[4]:s[4]+s[5]]
    strings=contents(sections[idx])
    def cstr(b,o):return b[o:].split(b'\0')[0].decode('ascii')
    named={cstr(strings,s[0]):s for s in sections}
    for s in sections:
        contents(s)
    for name in ('.text','.const','.fardata','.dynsym','.dynstr','.dynamic','.rela.dyn','.c6xabi.attributes'):
        require(name in named,f'missing {name}')
    require(not any(s[1]==8 and s[5] for s in sections),'BSS requires unavailable C startup')
    require(named['.text'][8]==32,'code fetch alignment')
    require(named['.text'][5]+named['.const'][5]<=29576,'over upstream code+const cap')
    require(named['.fardata'][5]<=512,'oversized writable globals')
    syms={};st=contents(named['.dynstr']);tab=contents(named['.dynsym'])
    require(len(tab)%16==0,'malformed dynsym')
    for i in range(0,len(tab),16):
        x=struct.unpack_from('<IIIBBH',tab,i);name=cstr(st,x[0]);syms[name]=x
        require(not(name and x[5]==0 and x[3]>>4 in (1,2)),'undefined dynamic symbol')
    audio=manifest['audio_func_name']
    for name in (audio,audio+'_init',audio+'_onf','Dll_PhsDepth','SonicStomp','effectTypeImageInfo'):
        require(name in syms,f'missing export {name}')
    require(struct.unpack_from('<I',e,24)[0]==syms['Dll_PhsDepth'][1],'entrypoint is not Dll_PhsDepth')
    def symbol_bytes(name):
        s=syms[name];sec=sections[s[5]];offset=s[1]-sec[3]
        require(0<=offset<=sec[5] and offset+s[2]<=sec[5],f'{name} outside section')
        return contents(sec)[offset:offset+s[2]]
    d=symbol_bytes('SonicStomp')
    require(len(d)==(len(manifest['params'])+2)*48,'descriptor count mismatch')
    require(cstr(d,0)=='OnOff' and cstr(d,48)==manifest['effect_name'],'descriptor identity')
    require(struct.unpack_from('<f',d,48+40)[0]==manifest['dsp_cost'],'DSP cost mismatch')
    for i,p in enumerate(manifest['params']):
        row=d[(i+2)*48:(i+3)*48]
        require(cstr(row,0)==p['name'],'control order/name mismatch')
        require(struct.unpack_from('<II',row,12)==(p['max'],p['default']),'control range/default mismatch')
        target=struct.unpack_from('<I',row,28)[0]
        require(target==syms[audio+'_'+p['name']+'_edit'][1],'missing real edit handler')
        flags=struct.unpack_from('<I',row,44)[0]
        require(bool(flags&4)==(i==len(manifest['params'])-1),'bad descriptor sentinel')
    require(len(symbol_bytes('effectTypeImageInfo'))==212,'bad image info')
    for name in ('.rela.dyn','.rela.plt'):
        rel=contents(named[name]);require(len(rel)%12==0,'malformed relocations')
        for i in range(0,len(rel),12):
            addr,info,_=struct.unpack_from('<IIi',rel,i)
            require(info&255 in (1,9,10),'unsupported/unsafe dynamic relocation')
            require(info>>8<len(tab)//16,'relocation symbol out of range')
            require(any(s[2]&2 and s[3]<=addr and addr+4<=s[3]+s[5] for s in sections),'relocation target outside allocated sections')
    return {'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'controls':[p['name'] for p in manifest['params']],
            'gid':manifest['gid'],'fxid':manifest['fxid'],'sections':len(sections),'structurally_valid':True,'physically_tested':False}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('zdl',type=Path,nargs='?',default=ROOT/'dist/PhsDepth.ZDL')
    args=ap.parse_args()
    print(json.dumps(validate(args.zdl.read_bytes(),json.loads((ROOT/'zoom/manifest_pedal.json').read_text())),indent=2))


if __name__=='__main__':main()
