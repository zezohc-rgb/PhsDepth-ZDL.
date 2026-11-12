#!/usr/bin/env python3
"""Decode the actual linked LCD image, verify pixels/overlays, render preview."""
from pathlib import Path
import hashlib,json,struct,zlib
ROOT=Path(__file__).resolve().parents[1]

def inspect():
 data=(ROOT/'build/CE2Soul.ZDL').read_bytes();e=data[76:]
 shoff=struct.unpack_from('<I',e,32)[0];size,count,names=struct.unpack_from('<HHH',e,46)
 sec=[struct.unpack_from('<10I',e,shoff+i*size) for i in range(count)]
 def body(s):return e[s[4]:s[4]+s[5]]
 def string(b,i):return b[i:].split(b'\0')[0].decode('ascii')
 ns=body(sec[names]);sections={string(ns,s[0]):s for s in sec}
 ds=body(sections['.dynstr']);st=body(sections['.dynsym']);symbols={}
 for i in range(0,len(st),16):
  s=struct.unpack_from('<IIIBBH',st,i);symbols[string(ds,s[0])]=s
 def at(va,n):
  for s in sec:
   if s[3]<=va and va+n<=s[3]+s[5] and s[2]&2:return body(s)[va-s[3]:va-s[3]+n]
  raise ValueError('image pointer outside allocated sections')
 info=at(symbols['effectTypeImageInfo'][1],212)
 assert struct.unpack_from('<II',info,12)==(128,64)
 picture=struct.unpack_from('<I',info,20)[0];raw=[];pos=0
 while len(raw)<1024:
  a=at(picture+pos,1)[0];pos+=1
  if len(raw)<1023 and a==at(picture+pos,1)[0]:
   n=at(picture+pos+1,1)[0];raw.extend([a]*(n+2));pos+=2
  else:raw.append(a)
 assert len(raw)==1024
 pixels=[[((raw[(y//8)*128+x]>>(y%8))&1) for x in range(128)] for y in range(64)]
 tokens=(ROOT/'build/CE2Soul-cover.pbm').read_text().split()
 assert tokens[:3]==['P1','128','64'];assert list(map(int,tokens[3:]))==[v for row in pixels for v in row]
 positions=[struct.unpack_from('<III',info,36+i*16) for i in range(2)]
 assert positions==[(2,42,9),(3,73,9)]
 assert struct.unpack_from('<III',info,68)==(0,0,0),'unexpected third knob'
 # Grayscale PNG magnifies the decoded one-bit device pixels using integer replication.
 scale=8;scan=bytearray()
 for row in pixels:
  line=bytes(v for b in row for v in [0 if b else 255]*scale)
  for _ in range(scale):scan.extend(b'\0'+line)
 def chunk(name,payload):return struct.pack('>I',len(payload))+name+payload+struct.pack('>I',zlib.crc32(name+payload)&0xffffffff)
 png=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',128*scale,64*scale,8,0,0,0,0))+chunk(b'IDAT',zlib.compress(scan,9))+chunk(b'IEND',b'')
 (ROOT/'build/CE2Soul-cover.png').write_bytes(png)
 report={'artifact_sha256':hashlib.sha256(data).hexdigest(),'pixels_verified':8192,'parameter_positions':positions,'visible_controls':['RATE','DEPTH'],'source':'decoded from executable ZDL; compared against source PBM','preview':'CE2Soul-cover.png','hardware_display_test':False}
 (ROOT/'build/cover-validation.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(json.dumps(inspect(),indent=2))
