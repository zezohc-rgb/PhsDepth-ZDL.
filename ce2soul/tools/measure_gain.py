#!/usr/bin/env python3
"""Reproducible synthetic input/output level checks; not physical pedal audio."""
from pathlib import Path
import ctypes as C,json,subprocess,argparse,hashlib
import numpy as np
from scipy.signal import butter,sosfilt
ROOT=Path(__file__).resolve().parents[1];FS=44100

def signals():
 t=np.arange(FS*10)/FS
 rng=np.random.default_rng(1979)
 noise=sosfilt(butter(3,[80,6000],fs=FS,btype='bandpass',output='sos'),rng.standard_normal(len(t)))
 noise*=.05/np.sqrt(np.mean(noise**2))
 pluck=np.zeros_like(t)
 notes=[82.4069,110,146.8324,195.9977,246.9417,329.6276]
 for i in range(12):
  begin=int(i*.8*FS);end=min(begin+int(1.6*FS),len(t));tt=np.arange(end-begin)/FS
  f=notes[i%len(notes)]
  env=(1-np.exp(-tt/.004))*np.exp(-tt/.35)
  for h in range(1,25):
   if f*h<6500:pluck[begin:end]+=env*np.sin(2*np.pi*f*h*tt+h*.37)/(h**1.3)
 pluck*=.08/np.sqrt(np.mean(pluck**2))
 return {'bandlimited_noise':noise.astype(np.float32),'synthetic_plucks':pluck.astype(np.float32)}

def measure():
 (ROOT/'work').mkdir(exist_ok=True)
 subprocess.run(['cc','-O2','-ffp-contract=off','-shared','-fPIC',str(ROOT/'src/ce2_dsp.c'),'-o',str(ROOT/'work/gain.so')],check=True)
 lib=C.CDLL(str(ROOT/'work/gain.so'));lib.ce2_state_size.restype=C.c_size_t
 lib.ce2_init.argtypes=[C.c_void_p,C.c_float,C.c_float]
 lib.ce2_process.argtypes=[C.c_void_p,C.c_void_p,C.c_void_p,C.c_uint,C.c_float,C.c_float]
 rows=[]
 for name,x in signals().items():
  for rate in (0,.5,1):
   for depth in (0,.5,1):
    state=C.create_string_buffer(lib.ce2_state_size());lib.ce2_init(state,rate,depth);out=np.zeros_like(x)
    lib.ce2_process(state,x.ctypes.data,out.ctypes.data,len(x),rate,depth)
    xx=x[FS:];yy=out[FS:]
    rms=lambda v:float(np.sqrt(np.mean(v.astype(np.float64)**2)))
    rows.append({'signal':name,'rate':rate,'depth':depth,'input_rms':rms(xx),'output_rms':rms(yy),
     'gain_db':20*np.log10(rms(yy)/rms(xx)),'input_peak':float(np.max(abs(xx))),'output_peak':float(np.max(abs(yy)))})
 return {'artifact_sha256':hashlib.sha256((ROOT/'build/CE2Soul.ZDL').read_bytes()).hexdigest(),'effect_version':json.loads((ROOT/'zoom/manifest.json').read_text())['fxid_version'],'scope':'synthetic host DSP fixtures, not physical or perceptual loudness measurement','sample_rate':FS,'physical_reference':False,'results':rows}
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=ROOT/'build/gain-report.json');a=p.parse_args();r=measure();a.output.write_text(json.dumps(r,indent=2)+'\n')
 print('gain dB range:',min(x['gain_db'] for x in r['results']),max(x['gain_db'] for x in r['results']))
