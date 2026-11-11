"""128x64 one-bit LCD artwork inspired by the supplied MS-70CDR+ Phaser.

The generated stompbox motif is stored as a small PBM sprite, not a dependency
on an image service at build time. Layout coordinates match the linker UI.
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent


def cover_canvas():
    from screen_image import Canvas
    c = Canvas()
    c.rect(0, 0, 127, 63)
    c.draw_text('PHSDEPTH', 5, 2, scale=2, spacing=1)
    c.hline(1, 126, 13)
    # Plain PBM: black is 1, white is 0, matching Zoom's monochrome canvas.
    tokens = []
    for line in (HERE / 'art/pedal.pbm').read_text().splitlines():
        tokens.extend(line.split('#', 1)[0].split())
    if tokens[:3] != ['P1', '32', '22'] or len(tokens[3:]) != 32 * 22:
        raise ValueError('expected an exact 32x22 plain PBM stompbox sprite')
    for i, bit in enumerate(tokens[3:]):
        if bit not in ('0', '1'):
            raise ValueError('PBM must contain only monochrome pixels')
        if bit == '1':
            c.px(48 + i % 32, 15 + i // 32)
    # Labels stay above the three firmware-owned 20x15 value boxes.
    for label, x in [('RATE', 14), ('COLOR', 55), ('LEVEL', 96)]:
        width = len(label) * 4 - 1
        c.draw_text(label, x + (20 - width) // 2, 38)
        c.rect(x, 46, x + 19, 60)
    return c


def make_cover():
    from screen_image import encode_zoom_rle
    return encode_zoom_rle(cover_canvas())


def save_pbm(path):
    c = cover_canvas()
    Path(path).write_text('P1\n128 64\n' + '\n'.join(' '.join(map(str, row)) for row in c.pixels) + '\n')
