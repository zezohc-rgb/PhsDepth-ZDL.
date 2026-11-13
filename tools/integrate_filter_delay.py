#!/usr/bin/env python3
"""Build a LOCAL EXPERIMENTAL Filter Delay + BOOST from the official original.
Not hardware validated. The copyrighted result is never committed by default.
"""
import argparse
import hashlib
import json
import math
import struct
import subprocess
from pathlib import Path
from zdl_elf import Elf, align
from inspect_zdl import inspect
ROOT=Path(__file__).resolve().parents[1]
ORIGINAL_SHA='19ea42ed3b37783abfb4440a527e12a6f7ef92f31ed24d881bbb5eed09364c8e'


def build(original, ti_root, fxid, output, dsp_cost=40.0):
    if original.resolve()==output.resolve(): raise ValueError('refusing to overwrite the original')
    raw=original.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=ORIGINAL_SHA: raise ValueError('unrecognized original SHA256')
    if not 400<=fxid<=0xffff: raise ValueError('experimental ID must be >= 400; audit pedal inventory separately')
    original_report=inspect(raw)
    elf=Elf(raw[76:]); text=elf.section('.text'); const=elf.section('.const')
    stocksyms={s['name']:s['words'][1] for s in elf.symbols()}
    desc_off=align(len(const['data']),8); desc_va=0x80000000+desc_off
    desc=bytearray(const['data'][0x270:0x450]);desc[48:60]=b'FltrDlyB\0\0\0\0'
    struct.pack_into('<I',desc,9*48+44,0) # Tail keeps its handler/formatter.
    if not math.isfinite(dsp_cost) or dsp_cost < 26.46: raise ValueError('DSP cost must not understate the stock declaration')
    struct.pack_into('<f',desc,48+40,dsp_cost) # Conservative experimental reservation, not measured CPU.
    desc.extend(struct.pack('<12s9I',b'BOOST',12,0,0,0,0,0,0,0,4))
    coe_off=align(desc_off+len(desc),8); coe_va=0x80000000+coe_off
    gains_off=align(coe_off+192,8); gains_va=0x80000000+gains_off
    work=ROOT/'build';work.mkdir(exist_ok=True)
    obj=work/'zoom_adapter.obj'; linked=work/'zoom_adapter_linked.out'; cmd=work/'zoom_adapter.cmd'
    subprocess.run([str(ti_root/'bin/cl6x'),'--c99','-mv6740','--abi=eabi','--mem_model:data=far','--no_compress','-O2',
                    '--include_path='+str(ti_root/'include'),'-c',str(ROOT/'src/filter_delay_boost/zoom_adapter.c'),
                    '--output_file='+str(obj)],check=True)
    code_va=align(len(text['data']),32)
    externs={k:v for k,v in stocksyms.items() if k.startswith('Fx_DLY_FilterDly')}
    externs.update(FDB_descriptor=desc_va,FDB_Coe=coe_va,effectTypeImageInfo=stocksyms['effectTypeImageInfo'])
    script='\n'.join(f'{k} = 0x{v:08x};' for k,v in externs.items())
    script+=f'\nSECTIONS {{ .text 0x{code_va:x}: {{ *(.text) }}\n .const 0x{gains_va:x}: {{ *(.const*) }} }}\n'
    cmd.write_text(script)
    subprocess.run([str(ti_root/'bin/lnk6x'),'--rom_model','--disable_auto_rts','--entry_point=FDB_Dll',
                    '--output_file='+str(linked),'--map_file='+str(work/'zoom_adapter.map'),str(obj),str(cmd)],check=True)
    linkedelf=Elf(linked.read_bytes());lsyms={s['name']:s['words'][1] for s in linkedelf.symbols()}
    extension=linkedelf.section('.text')['data'];gainbytes=linkedelf.section('.const')['data']
    if len(gainbytes)!=52: raise ValueError('unexpected linked gain layout')
    text['data'].extend(bytes(code_va-len(text['data']))+extension)
    const['data'].extend(bytes(desc_off-len(const['data']))+desc)
    # The old descriptor is no longer referenced by the DLL or by the
    # relocated FilterDly symbol. Legacy installers scan the FIRST OnOff
    # marker instead of following the DLL, so remove that inactive marker.
    # Preserve the rest of its bytes/relocations and all executable code.
    const['data'][0x270:0x27c] = bytes(12)
    const['data'].extend(bytes(coe_off-len(const['data'])))
    const['data'].extend(const['data'][0x524:0x524+188]+struct.pack('<f',1))
    const['data'].extend(bytes(gains_off-len(const['data']))+gainbytes)
    far=elf.section('.fardata');old_far=far['words'][3];far['words'][3]=align(0x80000000+len(const['data']),4)
    far_delta=far['words'][3]-old_far
    # New dynamic symbols go before the original exported DLL entry.
    dyn=elf.symbols('.dynsym'); olddll=next(i for i,s in enumerate(dyn) if s['name']=='Dll_FilterDly')
    strings=elf.section('.dynstr')['data']
    def addstr(s):
        offset=len(strings);strings.extend(s.encode('ascii')+b'\0');return offset
    additions=[]
    for name,va,sz,sec in [('FDB_edit',lsyms['FDB_edit'],0,4),('FDB_init',lsyms['FDB_init'],0,4),
                           ('FDB_audio',lsyms['FDB_audio'],0,4),('FDB_Coe',coe_va,192,13),
                           ('fdb_gains',gains_va,52,13)]:
        additions.append({'name':name,'words':[addstr(name),va,sz,2 if sec==4 else 1,2,sec]})
    dyn[olddll:olddll]=additions
    for s in dyn:
        w=s['words']
        if w[5]==far['index']:w[1]+=far_delta
        if s['name']=='FilterDly':w[1]=desc_va;w[2]=528
        if s['name']=='Dll_FilterDly':
            s['name']='Dll_FltrDlyB';w[0]=addstr(s['name']);w[1]=lsyms['FDB_Dll']
    ids={s['name']:i for i,s in enumerate(dyn)}
    rels=elf.relocations('.rela.dyn')
    for r in rels:
        if r[1]>>8>=olddll:r[1]+=len(additions)<<8
    # Duplicate stock descriptor relocations, preserving all original handler mappings.
    copied=[]
    for addr,info,addend in rels:
        if 0x80000270<=addr<0x80000450:
            newaddr=desc_va+(addr-0x80000270)
            if addr==0x800002bc:info=(ids['FDB_init']<<8)|1
            if addr==0x800002c0:info=(ids['FDB_audio']<<8)|1
            copied.append([newaddr,info,addend])
    rels+=copied+[[desc_va+10*48+28,(ids['FDB_edit']<<8)|1,0]]
    # Reuse each original dynsym target for adapter relocations when possible.
    objelf=Elf(obj.read_bytes());osyms=objelf.symbols()
    for sec in objelf.sections:
        if sec['name']!='.rela.text':continue
        for i in range(0,len(sec['data']),12):
            off,info,addend=struct.unpack_from('<IIi',sec['data'],i);kind=info&255
            name=osyms[info>>8]['name']
            if kind not in (9,10):raise ValueError('unexpected adapter address relocation')
            if name=='FDB_descriptor':name='FilterDly'
            if name not in ids:raise ValueError('missing dynamic target '+name)
            rels.append([code_va+off,(ids[name]<<8)|kind,addend])
    # Patch all relocated initial contents as well as retaining loader relocations.
    for addr,info,addend in rels:
        target=dyn[info>>8]['words'][1]+addend;kind=info&255
        section=text if addr<0x80000000 else const
        off=addr-section['words'][3]
        if not 0<=off<=len(section['data'])-4:raise ValueError('relocation destination outside text/const')
        old=struct.unpack_from('<I',section['data'],off)[0]
        if kind==1:value=target
        elif kind in (9,10):value=(old&~(0xffff<<7))|(((target if kind==9 else target>>16)&0xffff)<<7)
        else:raise ValueError('unsupported stock relocation')
        struct.pack_into('<I',section['data'],off,value)
    elf.section('.rela.dyn')['data']=bytearray(b''.join(struct.pack('<IIi',*r) for r in rels))
    elf.replace_symbols('.dynsym',dyn);elf.section('.dynsym')['words'][7]=olddll+len(additions)
    # Preserve debugging symbols, update relocated objects and exported entry.
    syms=elf.symbols();strs=elf.section('.strtab')['data']
    for s in syms:
        w=s['words']
        if w[5]==far['index']:w[1]+=far_delta
        if s['name']=='FilterDly':w[1]=desc_va;w[2]=528
        if s['name']=='Dll_FilterDly':
            w[0]=len(strs);strs.extend(b'Dll_FltrDlyB\0');w[1]=lsyms['FDB_Dll']
    for s in additions:
        copy={'name':s['name'],'words':s['words'][:]};copy['words'][0]=len(strs)
        strs.extend(s['name'].encode()+b'\0');copy['words'][3]|=16;syms.append(copy)
    elf.replace_symbols('.symtab',syms)
    # SysV hash uses the rebuilt dynamic names and indices.
    buckets=[0]*max(17,len(dyn));chains=[0]*len(dyn)
    def elfhash(name):
        h=0
        for c in name.encode():
            h=(h<<4)+c;g=h&0xf0000000
            if g:h^=g>>24
            h&=~g
        return h
    for i,s in enumerate(dyn[1:],1):
        b=elfhash(s['name'])%len(buckets);chains[i]=buckets[b];buckets[b]=i
    elf.section('.hash')['data']=bytearray(struct.pack('<'+'I'*(2+len(buckets)+len(chains)),len(buckets),len(chains),*buckets,*chains))
    dynamic=elf.section('.dynamic');entries=[list(struct.unpack_from('<II',dynamic['data'],i)) for i in range(0,len(dynamic['data']),8)]
    soname=addstr('ZDL_DLY_FltrDlyB.out')
    # First pack establishes file offsets used by the TI dynamic table.
    elf.pack(lsyms['FDB_Dll'])
    tags={4:elf.section('.hash')['words'][4],5:elf.section('.dynstr')['words'][4],6:elf.section('.dynsym')['words'][4],
          7:elf.section('.rela.dyn')['words'][4],8:len(elf.section('.rela.dyn')['data']),10:len(strings),14:soname,
          23:elf.section('.rela.plt')['words'][4] if any(s['name']=='.rela.plt' and s['words'][5] for s in elf.sections) else elf.section('.rela.dyn')['words'][4]+len(elf.section('.rela.dyn')['data']),
          0x6000000d:ids['Dll_FltrDlyB']*16,0x6000000f:dyn[ids['Dll_FltrDlyB']]['words'][0]}
    for e in entries:
        if e[0] in tags:e[1]=tags[e[0]]
    dynamic['data']=bytearray(b''.join(struct.pack('<II',*e) for e in entries))
    payload=elf.pack(lsyms['FDB_Dll']);header=bytearray(raw[:76]);struct.pack_into('<I',header,16,len(payload))
    header[64:66]=struct.pack('<H',fxid)
    result=bytes(header)+payload
    # Original DSP code 0..0x820 has no relocations and MUST remain byte-identical.
    assert text['data'][:0x820]==raw[76+0x40:76+0x40+0x820]
    checked=inspect(result)
    if len(checked['descriptor'])!=11: raise ValueError('rebuilt descriptor count mismatch')
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_bytes(result)
    report={'status':'experimental; not hardware validated','original_sha256':ORIGINAL_SHA,'output_sha256':hashlib.sha256(result).hexdigest(),
            'output_size':len(result),'experimental_fxid':fxid,'stock_audio_bytes_preserved':0x820,
            'coefficient_bytes':192,'parameter_count':9,'declared_experimental_dsp_cost':dsp_cost,'dynamic_relocation_count':len(rels),
            'adapter_text_bytes':len(extension),'entry':lsyms['FDB_Dll'],'descriptor_address':desc_va,
            'coe_address':coe_va,'gains_address':gains_va,'far_address':far['words'][3],
            'firmware_coefficient_allocation_verified':False,'hardware_tested':False}
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--original',type=Path,default=ROOT/'original/FLTRDLY.ZDL')
    p.add_argument('--ti-root',type=Path,required=True)
    p.add_argument('--experimental-fxid',type=lambda x:int(x,0),required=True)
    p.add_argument('--experimental-dsp-cost',type=float,default=40.0)
    p.add_argument('--output',type=Path,default=ROOT/'build/FLTRDLY_BOOST.ZDL')
    a=p.parse_args();r=build(a.original,a.ti_root,a.experimental_fxid,a.output,a.experimental_dsp_cost)
    (ROOT/'build/integration-report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':main()
