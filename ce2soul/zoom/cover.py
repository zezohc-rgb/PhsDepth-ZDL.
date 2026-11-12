"""Procedural 1-bit CE-2-inspired LCD artwork, drawn from primitives.

Reference: public Roland CE-2 pedal image. No vendor photo/bitmap is embedded.
The lower pad says SOUL to identify this independent custom effect.
"""
from pathlib import Path
# Values sit in the light knob centers; only RATE and DEPTH have overlays.
KNOB_POSITIONS=[(2,42,9),(3,73,9)]

def cover_canvas():
 from screen_image import Canvas
 c=Canvas()
 # Boss-style enclosure with clipped corners and a recessed top panel.
 c.hline(35,92,0);c.hline(35,92,63)
 c.vline(32,3,60);c.vline(95,3,60)
 for x,y in ((34,1),(33,2),(93,1),(94,2),(33,61),(34,62),(94,61),(93,62)):c.px(x,y)
 c.vline(34,3,59);c.vline(93,3,59)
 c.hline(35,92,28);c.hline(35,92,29)
 # CHECK light, two silver-center black knobs and small scale marks.
 c.circle(64,4,2);c.px(64,4)
 for x in (48,79):
  c.filled_circle(x,13,8);c.filled_circle(x,13,6,0)
  c.vline(x,5,8)
  for dx,dy in ((-7,-7),(7,-7),(-8,7),(8,7)):c.px(x+dx,13+dy)
 # Static knob captions omitted: owner reported overlap on the real LCD.
 # Side sockets and small direction marks.
 c.rect(29,30,31,35);c.rect(96,30,98,35)
 c.hline(37,41,31);c.px(37,30);c.px(37,32)
 c.hline(86,90,31);c.px(88,30);c.px(88,32)
 # A small custom mixed-case wordmark, not the vendor's image/font.
 glyphs={
 'C':['01111','11000','11000','11000','11000','11000','01111'],
 'h':['11000','11000','11000','11110','11011','11011','11011'],
 'o':['00000','00000','01110','11011','11011','11011','01110'],
 'r':['0000','0000','1110','1101','1100','1100','1100'],
 'u':['00000','00000','11011','11011','11011','11011','01111'],
 's':['00000','00000','01111','11000','01110','00011','11110']}
 x=43
 for ch in 'Chorus':
  for y,row in enumerate(glyphs[ch]):
   for dx,bit in enumerate(row):
    if bit=='1':c.px(x+dx,33+y)
  x+=len(glyphs[ch][0])+2
 c.draw_text('CE-2',76,41)
 # Large rectangular hinged rubber pad, with an original SOUL identity.
 c.rect(36,47,91,60)
 for y in range(49,59):c.hline(38,89,y)
 # Clear lettering out of the black pad to render it reversed.
 for ci,ch in enumerate('SOUL'):
  for yi,row in enumerate(c._FONT[ch]):
   for xi,bit in enumerate(row):
    c.px(56+ci*4+xi,51+yi,0 if bit=='1' else 1)
 c.hline(41,86,57,0)
 c.rect(60,61,67,62)
 return c

def make_cover():
 from screen_image import encode_zoom_rle
 return encode_zoom_rle(cover_canvas())

def save_pbm(path):
 c=cover_canvas();Path(path).write_text('P1\n128 64\n'+'\n'.join(' '.join(map(str,r)) for r in c.pixels)+'\n')
