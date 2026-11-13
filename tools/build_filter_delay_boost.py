#!/usr/bin/env python3
"""Compile the gain primitive, never mislabel it as a Zoom effect."""
import argparse
import json
import subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--ti-root', type=Path)
p.add_argument('--zdl', action='store_true', help='Report why final integration is blocked')
a = p.parse_args()
if a.zdl:
    p.exit(2, 'BLOCKED: original DSP callback wrapper, BOOST edit/init handler, coefficient allocation,\n'
              'descriptor/relocation rebuild and unique effect ID are not verified/implemented.\n'
              'No FLTRDLY_BOOST.ZDL was produced. See docs/filter-delay-boost/INTEGRATION.md.\n')
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
