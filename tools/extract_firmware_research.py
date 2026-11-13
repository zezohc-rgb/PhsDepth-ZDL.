#!/usr/bin/env python3
"""Extract TIPA DSP segments from the hash-locked official 2.10 updater.
Read-only; never executes an updater or writes a pedal. Outputs remain local.
TIPA records independently checked against Ziddle's tipa.rs.
"""
import argparse
import hashlib
import json
import struct
from pathlib import Path

UPDATER_SHA='7b39a612537f86a24a08fff6972f7b615a9a1dbb6b18905f71174d3556d01829'

def parse_tipa(data,offset):
    if data[offset:offset+4]!=b'TIPA':raise ValueError('TIPA signature missing')
    first=data.find(b'\x01YSX',offset+4)
    if not offset+4<=first<offset+512:raise ValueError('TIPA record not found in header')
    pos=first;segments=[]
    while data[pos:pos+4]==b'\x01YSX':
        if pos+12>len(data):raise ValueError('truncated TIPA header')
        address,size=struct.unpack_from('<II',data,pos+4)
        if not size or pos+12+size>len(data):raise ValueError('TIPA segment exceeds input')
        if address+size>2**32:raise ValueError('TIPA virtual range overflow')
        segments.append({'address':address,'size':size,'file_offset':pos+12})
        pos+=12+size
    if data[pos:pos+4]!=b'\x06YSX' or pos+8>len(data):raise ValueError('TIPA entry record missing')
    entry=struct.unpack_from('<I',data,pos+4)[0]
    if not any(s['address']<=entry<s['address']+s['size'] for s in segments):raise ValueError('entry outside segments')
    spans=sorted((s['address'],s['address']+s['size']) for s in segments)
    if any(a[1]>b[0] for a,b in zip(spans,spans[1:])):raise ValueError('overlapping TIPA segments')
    return {'tipa_offset':offset,'tipa_end':pos+8,'entry':entry,'segments':segments}

def wrap_code_elf(code,address,entry,attributes):
    # Minimal ELF32 C6000 image for TI dis6x static analysis, not a Zoom plugin.
    shstr=b'\0.text\0.shstrtab\0.c6xabi.attributes\0';fileoff=96;stroff=fileoff+len(code);attroff=stroff+len(shstr);shoff=(attroff+len(attributes)+3)&~3
    out=bytearray(shoff+160)
    ident=b'\x7fELF\x01\x01\x01\x40'+bytes(8)
    out[:52]=struct.pack('<16sHHIIIIIHHHHHH',ident,2,140,1,entry,52,shoff,0,52,32,1,40,4,2)
    struct.pack_into('<8I',out,52,1,fileoff,address,address,len(code),len(code),5,32)
    out[fileoff:fileoff+len(code)]=code;out[stroff:stroff+len(shstr)]=shstr
    struct.pack_into('<10I',out,shoff+40,1,1,6,address,fileoff,len(code),0,0,32,0)
    struct.pack_into('<10I',out,shoff+80,7,3,0,0,stroff,len(shstr),0,0,1,0)
    out[attroff:attroff+len(attributes)]=attributes
    struct.pack_into('<10I',out,shoff+120,17,0x70000003,0,0,attroff,len(attributes),0,0,0,0)
    return bytes(out)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('updater',type=Path)
    p.add_argument('--out-dir',type=Path,default=Path('original/firmware'))
    p.add_argument('--report',type=Path,default=Path('docs/filter-delay-boost/firmware-provenance.json'))
    a=p.parse_args();data=a.updater.read_bytes()
    if hashlib.sha256(data).hexdigest()!=UPDATER_SHA:raise ValueError('unrecognized updater hash')
    images=[];at=0
    while True:
        at=data.find(b'TIPA',at)
        if at<0:break
        try:images.append(parse_tipa(data,at))
        except ValueError:pass
        at+=4
    if len(images)!=2:raise ValueError('expected exactly two valid TIPA program images')
    main_image=next(i for i in images if i['entry']==0xc00dd800)
    a.out_dir.mkdir(parents=True,exist_ok=True)
    for idx,image in enumerate(images):
        payload=data[image['tipa_offset']:image['tipa_end']]
        image['sha256']=hashlib.sha256(payload).hexdigest()
        (a.out_dir/f'image-{idx}.tipa').write_bytes(payload)
        for s in image['segments']:
            b=data[s['file_offset']:s['file_offset']+s['size']]
            s['sha256']=hashlib.sha256(b).hexdigest()
            (a.out_dir/f'{s["address"]:08x}.bin').write_bytes(b)
    code=next(s for s in main_image['segments'] if s['address']<=main_image['entry']<s['address']+s['size'])
    payload=data[code['file_offset']:code['file_offset']+code['size']]
    from zdl_elf import Elf
    reference=Path('original/FLTRDLY.ZDL').read_bytes()
    if hashlib.sha256(reference).hexdigest()!='19ea42ed3b37783abfb4440a527e12a6f7ef92f31ed24d881bbb5eed09364c8e': raise ValueError('original ZDL reference required')
    attributes=Elf(reference[76:]).section('.c6xabi.attributes')['data']
    (a.out_dir/'Main-code.out').write_bytes(wrap_code_elf(payload,code['address'],main_image['entry'],attributes))
    report={'updater_sha256':UPDATER_SHA,'source_url':'https://zoomcorp.com/documents/93/MS-70CDR_v2.10_Win_E.zip',
            'method':'TIPA record walk, boundaries and entry verified; updater never executed','images':images,'hardware_io':False}
    a.report.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'images':len(images),'code_address':hex(code['address']),'code_bytes':code['size']},indent=2))
if __name__=='__main__':main()
