#!/usr/bin/env python3
"""Render a synthetic test signal through four waves. Not a Diamond recording."""
import ctypes as C
import math
from pathlib import Path
import struct
import subprocess
import tempfile
import wave
ROOT = Path(__file__).resolve().parent
class Params(C.Structure):
    _fields_ = [(n,C.c_float) for n in ('rate_hz','depth','level','attack_ms','release_ms','accent','duty_min')] + [(n,C.c_int) for n in ('wave','mode','doubled','held')]
class State(C.Structure):
    _fields_ = [(n,C.c_float) for n in ('inv_sr','phase','optical','last_gain','chaos')] + [('rng',C.c_uint32),('cycle',C.c_uint32),('previous_held',C.c_int)]
def main():
    out=ROOT/'dist';out.mkdir(exist_ok=True)
    sr=44100
    with tempfile.TemporaryDirectory() as tmp:
        libpath=Path(tmp)/'dm.so'
        subprocess.run(['cc','-std=c99','-O2','-shared','-fPIC',str(ROOT/'dm_trem.c'),'-o',str(libpath)],check=True)
        lib=C.CDLL(str(libpath));lib.dm_defaults.restype=Params
        lib.dm_init.argtypes=[C.POINTER(State),C.c_float]
        lib.dm_process.argtypes=[C.POINTER(State),C.POINTER(Params),C.POINTER(C.c_float),C.POINTER(C.c_float),C.c_uint]
        for index,name in enumerate(('shark','sine','square','chop')):
            n=sr*4;arr=C.c_float*n
            signal=[0.35*math.exp(-2.5*(i/sr%1))*sum(math.sin(2*math.pi*110*h*i/sr)/h for h in range(1,7)) for i in range(n)]
            left=arr(*signal);right=arr(*signal);s=State();p=lib.dm_defaults()
            p.wave=index;p.rate_hz=4;p.depth=0.5 if index==3 else 1
            lib.dm_init(C.byref(s),sr);lib.dm_process(C.byref(s),C.byref(p),left,right,n)
            with wave.open(str(out/f'{name}.wav'),'wb') as wav:
                wav.setparams((2,2,sr,0,'NONE','not compressed'))
                wav.writeframes(b''.join(struct.pack('<hh',round(max(-1,min(1,left[i]))*32767),round(max(-1,min(1,right[i]))*32767)) for i in range(n)))
    print(f'Synthetic previews (not reference-pedal captures): {out}')
if __name__=='__main__': main()
