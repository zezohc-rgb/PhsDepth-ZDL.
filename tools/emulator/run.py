#!/usr/bin/env python3
"""Build the PhaserZeh binary differential test against unpacked Ziddle 1793487371.
Requires Rust/cargo on PATH. No firmware, stock handlers or pedal needed.
"""
import argparse
import ctypes as C
import hashlib
import json
import re
from pathlib import Path
import shutil
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[2]


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--ziddle',required=True,type=Path)
    args=ap.parse_args()
    zroot=args.ziddle.resolve()
    manifest=json.loads((ROOT/'zoom/manifest_pedal.json').read_text())
    artifact=ROOT/'dist'/(manifest['output_basename']+'.ZDL')
    work=ROOT/'work/emulator';work.mkdir(parents=True,exist_ok=True)
    (work/'src').mkdir(exist_ok=True)
    shutil.copy2(Path(__file__).with_name('main.rs'),work/'src/main.rs')
    (work/'Cargo.toml').write_text('[package]\nname="phsdepth-binary-test"\nversion="0.1.0"\nedition="2021"\n[workspace]\n[dependencies]\n'+
        f'ziddle-effect-emulator={{path="{zroot}/ziddle/runtime/effect-emulator"}}\n'+
        f'ziddle-effect-runtime={{path="{zroot}/ziddle/runtime/effect-runtime"}}\n')
    subprocess.run(['cc','-std=c99','-O2','-ffp-contract=off','-fPIC','-shared',str(ROOT/'src/phsdepth_dsp.c'),'-o',str(work/'host.so')],check=True)
    class State(C.Structure):
        _fields_=[('filters',C.c_float*16),('phase',C.c_float),('rate',C.c_float),('depth',C.c_float),('level',C.c_float),('color',C.c_int),('wave',C.c_int),('random_state',C.c_uint32),('random_value',C.c_float),('random_previous',C.c_float),('coefficient',C.c_float)]
    lib=C.CDLL(str(work/'host.so'))
    lib.phsdepth_init.argtypes=[C.POINTER(State)]
    lib.phsdepth_set.argtypes=[C.POINTER(State),C.c_float,C.c_int,C.c_float,C.c_float]
    lib.phsdepth_process.argtypes=[C.POINTER(State)]+[C.POINTER(C.c_float)]*4+[C.c_uint,C.c_float]
    lib.phsdepth_set_wave.argtypes=[C.POINTER(State),C.c_int]
    cases=[]
    for wave in range(7):
        for mode in range(4):
            cases.append((35,mode,50,50,wave))
            for rate in [0,100]:
                for depth in [0,100]:
                    for level in [0,100]:cases.append((rate,mode,level,depth,wave))
    # Exact binary rational input: both channels, impulse, deterministic noise and tail.
    # Some zero runs verify decay without asking libm for a matched test signal.
    rand=0x12345678
    vector=bytearray(struct.pack('<I',len(cases)))
    for rate,mode,level,depth,wave in cases:
        blocks=4096 if rate==35 else 2048
        vector.extend(struct.pack('<5fI',rate,mode,level,depth,wave,blocks))
        s=State();lib.phsdepth_init(C.byref(s));lib.phsdepth_set(C.byref(s),C.c_float(.08+rate*.0592),mode,level*.02,depth*.01)
        lib.phsdepth_set_wave(C.byref(s),wave)
        for block in range(blocks):
            l=(C.c_float*8)();r=(C.c_float*8)();ol=(C.c_float*8)();orr=(C.c_float*8)()
            for i in range(8):
                rand=(1664525*rand+1013904223)&0xffffffff
                l[i]=((rand>>16)-32768)/131072 if block<blocks*3//4 else 0
                r[i]=.5 if block==0 and i==0 else 0
            lib.phsdepth_process(C.byref(s),l,r,ol,orr,8,44100)
            vector.extend(struct.pack('<32f',*l,*r,*ol,*orr))
    vectors=work/'vectors.bin';vectors.write_bytes(vector)
    shutil.copy2(Path(__file__).with_name('Cargo.lock'),work/'Cargo.lock')
    subprocess.run(['cargo','build','--locked','--release','--manifest-path',str(work/'Cargo.toml')],check=True)
    result=subprocess.run([str(work/'target/release/phsdepth-binary-test'),str(artifact),str(vectors)],text=True,capture_output=True)
    log=result.stdout+result.stderr
    (work/'result.txt').write_text(log);print(log)
    summary=re.search(r'PASS: (\d+) cases, (\d+) channel samples; max TI/host error ([0-9.]+); max packets/block (\d+), emulator cycles/block (\d+)',log)
    metrics={} if not summary else dict(zip(('cases','channel_samples','max_abs_error','max_packets_per_block','max_emulator_cycles_per_block'),(int(summary[1]),int(summary[2]),float(summary[3]),int(summary[4]),int(summary[5]))))
    report={'metrics':metrics,'ziddle_source':'https://berbasoft.com/ziddle/ziddle-1793487371.zip','ziddle_zip_sha256':hashlib.sha256((zroot.parent/'ziddle.zip').read_bytes()).hexdigest() if (zroot.parent/'ziddle.zip').exists() else None,
            'artifact_sha256':hashlib.sha256((artifact).read_bytes()).hexdigest(),
            'passed':result.returncode==0,'cases':len(cases),'result':log,
            'physical_hardware_test':False,'scope':'C674x instruction execution and host audio parity; hermetic runtime callbacks, not MS-70CDR firmware scheduling or loader compatibility'}
    (ROOT/'dist/emulator-report.json').write_text(json.dumps(report,indent=2)+'\n')
    raise SystemExit(result.returncode)


if __name__=='__main__':main()
