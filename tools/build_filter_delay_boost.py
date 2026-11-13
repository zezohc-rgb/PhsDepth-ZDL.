#!/usr/bin/env python3
"""Compile the gain primitive, never mislabel it as a Zoom effect."""
import argparse
import json
import subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--ti-root', type=Path)
p.add_argument('--zdl', action='store_true', help='Point to the separate experimental integration builder')
a = p.parse_args()
if a.zdl:
    p.exit(2, 'Use tools/integrate_filter_delay.py with the hash-locked original, --ti-root and\n'
              '--experimental-fxid to generate the local experimental ZDL. This script builds only the primitive.\n')
out = ROOT/'build'
out.mkdir(exist_ok=True)
if a.ti_root:
    cmd = [str(a.ti_root/'bin/cl6x'), '--c99', '-mv6740', '--abi=eabi',
           '--mem_model:data=far', '--opt_level=2', '--include_path='+str(a.ti_root/'include'), '-c',
           str(ROOT/'src/filter_delay_boost/boost.c'),
           '--output_file='+str(out/'filter_delay_boost.obj')]
    artifact = 'filter_delay_boost.obj'
else:
    cmd = ['cc', '-std=c99', '-O2', '-Wall', '-Wextra', '-Werror', '-fPIC', '-shared',
           str(ROOT/'src/filter_delay_boost/boost.c'), '-o', str(out/'filter_delay_boost.so')]
    artifact = 'filter_delay_boost.so'
subprocess.run(cmd, check=True)
print(json.dumps({'artifact': artifact, 'installable_zdl': False, 'command': cmd}, indent=2))
