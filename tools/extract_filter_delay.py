#!/usr/bin/env python3
"""Read-only extraction from the official Windows MS-70CDR firmware updater.
Filesystem layout verified against Zoom-Firmware-Editor; no updater is executed.
"""
import argparse
import hashlib
import json
import struct
from pathlib import Path


def extract(data, name='FLTRDLY.ZDL'):
    magic = bytes.fromhex('55aa00010400')
    starts = [i for i in range(len(data)) if data.startswith(magic, i)]
    if len(starts) != 1:
        raise ValueError('expected exactly one firmware filesystem signature')
    base = starts[0]
    blocks, = struct.unpack_from('<H', data, base + 8)
    if blocks < 11 or base + blocks * 4096 > len(data):
        raise ValueError('filesystem exceeds input bounds')
    active = []
    for i in range(4):
        off = base + (3 + i * 2) * 4096
        if data[off+1] == 0xa5 and data[off+4:off+8] == b'\xff'*4:
            active.append(off)
    if len(active) != 1:
        raise ValueError('expected one unambiguous active file table')
    entries = []
    for pos in range(active[0]+8, active[0]+8192-31, 32):
        if data[pos+8:pos+20].split(b'\0')[0].rstrip(b'\xff') == name.encode('ascii'):
            entries.append(pos)
    if len(entries) != 1:
        raise ValueError('target not unique in active table')
    entry = entries[0]
    address, = struct.unpack_from('<H', data, entry)
    size, = struct.unpack_from('<I', data, entry+4)
    if data[entry+2:entry+4] != b'\x01\xff' or size > blocks*4090:
        raise ValueError('invalid file table entry')
    output = bytearray()
    previous = 0xffff
    visited = set()
    while address != 0xffff:
        if address in visited or not 1 <= address < blocks-10:
            raise ValueError('cyclic or out-of-range block chain')
        visited.add(address)
        off = base + (10 + address)*4096
        prev, nxt, used = struct.unpack_from('<HHH', data, off)
        if prev != previous or used > 4090 or len(output)+used > size:
            raise ValueError('invalid block linkage or data size')
        output.extend(data[off+6:off+6+used])
        previous, address = address, nxt
    if len(output) != size or output[:8] != b'\0\0\0\0SIZE':
        raise ValueError('size or ZDL signature mismatch')
    return bytes(output), {'filesystem_offset': base, 'filesystem_blocks': blocks,
                          'active_table_offset': active[0], 'entry_offset': entry,
                          'data_blocks': sorted(visited), 'size': size}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('updater', type=Path)
    p.add_argument('--output', type=Path, default=Path('original/FLTRDLY.ZDL'))
    p.add_argument('--report', type=Path, default=Path('docs/filter-delay-boost/provenance.json'))
    args = p.parse_args()
    data = args.updater.read_bytes()
    effect, report = extract(data)
    report.update(updater_sha256=hashlib.sha256(data).hexdigest(),
                  effect_sha256=hashlib.sha256(effect).hexdigest(),
                  source_url='https://zoomcorp.com/documents/93/MS-70CDR_v2.10_Win_E.zip')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(effect)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))

if __name__ == '__main__':
    main()
