"""TRM-1-inspired horizontal enclosure, four knobs, toggle and twin switches.
Embedded artwork is 128x64 monochrome. Color PNG is an external thumbnail only.
"""
from pathlib import Path
import struct
import zlib
KNOB_POSITIONS=[(2,30,12),(3,54,12),(4,78,12)]
def line(c,x0,y0,x1,y1):
 dx=abs(x1-x0);sx=1 if x0<x1 else -1;dy=-abs(y1-y0);sy=1 if y0<y1 else -1;error=dx+dy
 while True:
  c.px(x0,y0)
  if x0==x1 and y0==y1:break
  twice=2*error
  if twice>=dy:error+=dy;x0+=sx
  if twice<=dx:error+=dx;y0+=sy

def canvas():
 from screen_image import Canvas
 c=Canvas();c.rect(23,0,126,63);c.rect(25,2,124,61)
 for x,label in ((36,'SPD'),(60,'DEP'),(84,'VOL'),(110,'MODE')):
  c.draw_text(label,x-(len(label)*4-1)//2,4)
  c.filled_circle(x,18,7);c.circle(x,18,5,0);line(c,x,18,x+4,14)
 # Toggle centered under depth/volume, as on the horizontal original.
 c.circle(72,29,2);line(c,72,29,74,25)
 # A simple faceted diamond motif rather than a copied vendor bitmap.
 for a,b in (((34,38),(40,31)),((40,31),(46,38)),((46,38),(40,45)),((40,45),(34,38)),((40,31),(40,45)),((34,38),(46,38))):
  line(c,*a,*b)
 c.draw_text('DM TREM',54,34);c.draw_text('OPTICAL',54,42)
 # LEDs and metal footswitch rings.
 for x in (42,111):
  c.filled_circle(x,49,1);c.circle(x,56,4);c.circle(x,56,2)
 c.draw_text('TAP/DBL',49,54);c.draw_text('ON',98,48)
 return c

def make_cover():
 from screen_image import encode_zoom_rle
 return encode_zoom_rle(canvas())

def png(c,path,ink,paper,scale=1):
 def chunk(kind,data):return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)
 rows=b''
 for row in c.pixels:
  rgb=b''.join(bytes(ink if bit else paper)*scale for bit in row)
  rows+=(b'\0'+rgb)*scale
 header=struct.pack('>IIBBBBB',128*scale,64*scale,8,2,0,0,0)
 Path(path).write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',header)+chunk(b'IDAT',zlib.compress(rows,9))+chunk(b'IEND',b''))

def save_pbm(path):
 c=canvas();path=Path(path)
 path.write_text('P1\n128 64\n'+'\n'.join(' '.join(map(str,row)) for row in c.pixels)+'\n')
 png(c,path.with_name('DmTrem.png'),(239,243,223),(15,69,47))
 png(c,path.with_name('DmTrem-LCD.png'),(18,28,18),(223,235,197),4)
