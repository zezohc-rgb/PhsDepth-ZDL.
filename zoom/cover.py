"""Full-size stock-style stompbox artwork for the original MS-70CDR LCD.

The 128x64 PBM is a fixed one-bit asset, generated from the owner's hardware
photo reference. The build never depends on an image-generation service.
The three value overlays are aligned to its top-row knobs.
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent
KNOB_POSITIONS = [(2, 30, 11), (3, 54, 11), (4, 78, 11)]


def cover_canvas():
    from screen_image import Canvas
    tokens = []
    for line in (HERE / 'art/stock-style.pbm').read_text().splitlines():
        tokens.extend(line.split('#', 1)[0].split())
    if tokens[:3] != ['P1', '128', '64'] or len(tokens[3:]) != 128 * 64:
        raise ValueError('expected an exact 128x64 plain PBM cover')
    c = Canvas()
    for i, bit in enumerate(tokens[3:]):
        if bit not in ('0', '1'):
            raise ValueError('PBM must contain only monochrome pixels')
        if bit == '1':
            c.px(i % 128, i // 128)
    return c


def make_cover():
    from screen_image import encode_zoom_rle
    return encode_zoom_rle(cover_canvas())


def save_pbm(path):
    c = cover_canvas()
    Path(path).write_text('P1\n128 64\n' + '\n'.join(' '.join(map(str, row)) for row in c.pixels) + '\n')
