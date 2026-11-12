"""Original LCD cover; no copied Diamond artwork."""
from pathlib import Path
KNOB_POSITIONS=[(2,29,11),(3,60,11),(4,91,11)]
def canvas():
 from screen_image import Canvas
 c=Canvas();c.rect(6,0,121,63)
 for x,label in ((29,'SPD'),(60,'DEP'),(91,'VOL')):
  c.draw_text(label,x-10,2);c.circle(x+1,23,9);c.vline(x+1,16,23)
 c.rect(15,39,112,54);c.draw_text('DM TREM',36,43)
 return c
def make_cover():
 from screen_image import encode_zoom_rle
 return encode_zoom_rle(canvas())
def save_pbm(path):
 c=canvas();Path(path).write_text('P1\n128 64\n'+'\n'.join(' '.join(map(str,row)) for row in c.pixels)+'\n')
