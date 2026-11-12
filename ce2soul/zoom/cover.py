"""Original procedural two-control LCD cover, no vendor bitmap."""
from pathlib import Path
KNOB_POSITIONS=[(2,42,11),(3,76,11)]
def cover_canvas():
 from screen_image import Canvas
 c=Canvas();c.rect(24,0,99,63);c.draw_text('RATE',35,2);c.draw_text('DEPTH',69,2)
 for x in (46,80):c.circle(x,21,9);c.circle(x,21,7);c.vline(x,15,21)
 c.rect(28,34,95,48);c.draw_text('CE-2 SOUL',35,38);c.rect(42,53,82,60)
 return c
def make_cover():
 from screen_image import encode_zoom_rle
 return encode_zoom_rle(cover_canvas())
def save_pbm(path):
 c=cover_canvas();Path(path).write_text('P1\n128 64\n'+'\n'.join(' '.join(map(str,r)) for r in c.pixels)+'\n')
