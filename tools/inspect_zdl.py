#!/usr/bin/env python3
"""Strict read-only ZDL/ELF32 structural inspector. Not a hardware validator."""
import argparse
import hashlib
import json
import struct
from pathlib import Path


def bounded(data, offset, size):
    if offset < 0 or size < 0 or offset + size > len(data):
        raise ValueError('range outside file')
    return data[offset:offset+size]


def string(data, offset):
    if not 0 <= offset < len(data):
        raise ValueError('invalid string offset')
    end = data.find(b'\0', offset)
    if end < 0:
        raise ValueError('unterminated string')
    return data[offset:end].decode('ascii')


def inspect(data):
    if len(data) < 76 or data[:8] != b'\0\0\0\0SIZE':
        raise ValueError('invalid ZDL prefix')
    payload_size, header_size, elf_size = struct.unpack_from('<III', data, 8)
    if payload_size != 8 or header_size < 56 or data[20:24] != b'INFO':
        raise ValueError('invalid SIZE/INFO')
    if struct.unpack_from('<I', data, 24)[0] != 48:
        raise ValueError('unsupported INFO size')
    elf_offset = 20 + header_size
    if elf_offset + elf_size != len(data):
        raise ValueError('ELF size mismatch or trailing bytes')
    elf = bounded(data, elf_offset, elf_size)
    if elf[:7] != b'\x7fELF\x01\x01\x01' or len(elf) < 52:
        raise ValueError('expected ELF32 little-endian version 1')
    typ, machine = struct.unpack_from('<HH', elf, 16)
    if typ != 3 or machine != 140:
        raise ValueError('expected C6000 shared object')
    entry, phoff, shoff = struct.unpack_from('<III', elf, 24)
    ehsize, phentsize, phnum, shentsize, shnum, shstrndx = struct.unpack_from('<6H', elf, 40)
    if ehsize != 52 or shentsize != 40 or phentsize != 32 or shstrndx >= shnum:
        raise ValueError('invalid ELF table dimensions')
    bounded(elf, shoff, shnum*40)
    bounded(elf, phoff, phnum*32)
    sections = []
    for i in range(shnum):
        fields = struct.unpack_from('<10I', elf, shoff+i*40)
        n,t,f,a,o,s,l,inf,al,en = fields
        if t != 8:
            bounded(elf,o,s)
        if al and al & (al-1):
            raise ValueError('invalid section alignment')
        sections.append(dict(index=i, name_offset=n, type=t, flags=f, address=a,
                             offset=o, size=s, link=l, info=inf, alignment=al, entsize=en))
    names = bounded(elf, sections[shstrndx]['offset'], sections[shstrndx]['size'])
    for s in sections:
        s['name'] = string(names,s.pop('name_offset'))
    programs=[]
    for i in range(phnum):
        t,o,v,p,fs,ms,f,al=struct.unpack_from('<8I',elf,phoff+i*32)
        bounded(elf,o,fs)
        if t == 1 and fs > ms:
            raise ValueError('PT_LOAD filesz exceeds memsz')
        programs.append(dict(type=t, offset=o, address=v, filesz=fs, memsz=ms, flags=f, alignment=al))
    if not any(p['type']==1 and p['flags']&1 and p['address']<=entry<p['address']+p['memsz'] for p in programs):
        raise ValueError('entry point outside executable segment')
    def contents(s): return bounded(elf,s['offset'],s['size'])
    symbol_tables={}
    for s in sections:
        if s['type'] not in (2,11): continue
        if s['entsize'] != 16 or s['size']%16 or s['link']>=shnum:
            raise ValueError('invalid symbol table')
        strs=contents(sections[s['link']]); syms=[]
        for off in range(0,s['size'],16):
            n,v,sz,info,other,idx=struct.unpack_from('<IIIBBH',contents(s),off)
            if idx < 0xff00 and idx >= shnum: raise ValueError('invalid symbol section')
            syms.append(dict(name=string(strs,n),value=v,size=sz,info=info,section=idx))
        symbol_tables[s['index']]=syms
    dyn=next((v for k,v in symbol_tables.items() if sections[k]['type']==11),None)
    if dyn is None: raise ValueError('missing dynamic symbols')
    relocations=[]
    for s in sections:
        if s['name'] != '.rela.dyn': continue
        if s['entsize'] != 12 or s['size']%12 or s['link'] not in symbol_tables:
            raise ValueError('invalid relocations')
        for off in range(0,s['size'],12):
            addr,info,addend=struct.unpack_from('<IIi',contents(s),off)
            idx=info>>8; kind=info&255
            syms=symbol_tables[s['link']]
            if idx>=len(syms): raise ValueError('invalid relocation symbol')
            if not any(p['type']==1 and p['address']<=addr and addr+4<=p['address']+p['memsz'] for p in programs):
                raise ValueError('relocation destination outside loaded memory')
            relocations.append(dict(address=addr,type=kind,symbol=syms[idx]['name'],value=syms[idx]['value'],addend=addend))
    const=next((s for s in sections if s['name']=='.const' and s['size']),None)
    if const is None: raise ValueError('missing const section')
    raw=contents(const)
    candidates=[i for i in range(0,len(raw)-95,4) if raw[i:i+6]==b'OnOff\0'
                and struct.unpack_from('<I',raw,i+12)[0]==1
                and struct.unpack_from('<I',raw,i+60)[0]==0xffffffff]
    if len(candidates)!=1: raise ValueError('ambiguous descriptor')
    start=candidates[0]; rows=[]
    for i in range(18):
        off=start+48*i; row=bounded(raw,off,48); w=struct.unpack('<12I',row)
        va=const['address']+off
        refs={r['address']-va:r for r in relocations if va<=r['address']<va+48}
        rows.append(dict(index=i,name=string(row,0),max=w[3],default=w[4],pedal_max=w[5],
                         flags=w[11],handler=refs.get(28,{}).get('symbol'),
                         audio=refs.get(32,{}).get('symbol'),formatter=refs.get(36,{}).get('symbol'),
                         cost=struct.unpack_from('<f',row,40)[0] if i==1 else None))
        if w[11]&4: break
    else: raise ValueError('descriptor end sentinel missing')
    if len(rows)<3 or any(r['default']>r['max'] for r in rows[2:]):
        raise ValueError('invalid parameter bounds')
    allsyms=[s for ss in symbol_tables.values() for s in ss]
    symbols={s['name']:{k:s[k] for k in ('value','size','section')} for s in allsyms if s['name']}
    ui=symbols.get('effectTypeImageInfo'); ui_count=None
    if ui:
        ui_off=ui['value']-const['address']+32
        ui_count=struct.unpack('<I',bounded(raw,ui_off,4))[0]
        # Stock FilterDly has 3 here and 8 parameters: this counts visible UI slots.
        if not 0 < ui_count <= 9: raise ValueError('invalid UI slot count')
    return dict(sha256=hashlib.sha256(data).hexdigest(),size=len(data),elf_offset=elf_offset,
                elf_size=elf_size,entry=entry,gid=data[60],fxid=int.from_bytes(data[64:66],'little'),
                version=string(data[68:76],0),sections=sections,programs=programs,
                descriptor_address=const['address']+start,descriptor=rows,ui_field_at_0x20=ui_count,
                dynamic_relocations=relocations,symbols=symbols,
                compatibility='structural inspection only; no execution or hardware validation')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('zdl',type=Path); p.add_argument('--output',type=Path)
    a=p.parse_args()
    try: result=inspect(a.zdl.read_bytes())
    except (ValueError,struct.error,UnicodeDecodeError) as e: p.exit(1,f'INVALID: {e}\n')
    report=json.dumps(result,indent=2)+'\n'
    if a.output: a.output.write_text(report)
    else: print(report,end='')

if __name__=='__main__': main()
