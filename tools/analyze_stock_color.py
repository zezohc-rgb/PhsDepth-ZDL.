#!/usr/bin/env python3
"""Read labels/metadata from a LOCAL stock PHASER.ZDL; never modifies/ships it.
Usage: python3 tools/analyze_stock_color.py /path/to/PHASER.ZDL
TI dis6x is separately needed to trace the table references in color_edit.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct


def analyze(path):
    data=Path(path).read_bytes()
    if data[:8]!=b'\0\0\0\0SIZE' or data[76:83]!=b'\x7fELF\x01\x01\x01':
        raise ValueError('expected plain original-family ZDL with ELF32 at byte 76')
    e=data[76:];offset=struct.unpack_from('<I',e,32)[0]
    stride,count,_=struct.unpack_from('<HHH',e,46)
    sections=[struct.unpack_from('<10I',e,offset+i*stride) for i in range(count)]
    sym=next(s for s in sections if s[1]==11);st=sections[sym[6]]
    strings=e[st[4]:st[4]+st[5]];symbols={}
    for i in range(0,sym[5],16):
        s=struct.unpack_from('<IIIBBH',e,sym[4]+i)
        name=strings[s[0]:].split(b'\0')[0].decode('ascii');symbols[name]=s
    def raw(name,size):
        s=symbols[name];section=sections[s[5]];o=section[4]+s[1]-section[3]
        return e[o:o+size]
    b=raw('disp_prm_phaserColor',32)
    labels=[b[i:i+8].split(b'\0')[0].decode('ascii') for i in range(0,32,8)]
    d=raw('Phaser',240);parameters={}
    for i in range(2,5):
        name=d[i*48:i*48+12].split(b'\0')[0].decode('ascii')
        maximum,default=struct.unpack_from('<II',d,i*48+12)
        parameters[name]={'max':maximum,'default':default}
    tables={}
    for name,width in [('Fx_Mod_Pha_color_Mix_tbl',12),('Fx_Mod_Pha_color_FB_tbl',12),('Fx_Mod_Pha_color_LFO_tbl',8)]:
        b=raw(name,4*width)
        tables[name]={'va':hex(symbols[name][1]),'row_bytes':width,
                      'distinct_rows':len({b[i:i+width] for i in range(0,len(b),width)})}
    return {'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'labels':labels,
            'parameters':parameters,'tables':tables,
            'scope':'Static metadata facts only. Does not establish equivalent audio or firmware matching.'}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('stock_zdl',type=Path)
    print(json.dumps(analyze(p.parse_args().stock_zdl),indent=2))
