#!/usr/bin/env python3
"""Create original test signals for a future authorized reference capture.
Does not install, authenticate, execute or extract any third-party plugin.
"""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from scipy.io import wavfile
from scipy.signal import chirp,butter,sosfilt
FS=44100

def make(output):
 output=Path(output);output.mkdir(parents=True,exist_ok=True)
 impulse=np.zeros(FS*32,dtype=np.float32)
 # 20 probes/sec, after a two-second warmup; one second trailing silence.
 impulse[np.arange(2*FS,31*FS,FS//20)]=.125
 rng=np.random.default_rng(1979)
 noise=sosfilt(butter(4,12000,fs=FS,output='sos'),rng.standard_normal(FS*12))
 noise*=.025/np.sqrt(np.mean(noise**2));noise[:FS]=0;noise[-FS:]=0
 t=np.arange(FS*8)/FS;sweep=np.zeros(FS*11)
 sweep[FS:9*FS]=.1*chirp(t,20,8,15000,method='logarithmic')
 files={}
 for name,data in [('impulses.wav',impulse),('noise.wav',noise),('sweep.wav',sweep)]:
  data=np.asarray(data,dtype=np.float32);wavfile.write(output/name,FS,data)
  files[name]={'seconds':len(data)/FS,'peak':float(np.max(abs(data))),'sha256':hashlib.sha256((output/name).read_bytes()).hexdigest()}
 report={'sample_rate':FS,'format':'mono IEEE float32 WAV','reference_plugin_run':False,'files':files,
  'instructions':'See docs/PLUGIN_REFERENCE.md. Generated signals are our own, not Boss captures.'}
 (output/'manifest.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=Path('work/reference-probes'));a=p.parse_args();print(json.dumps(make(a.output),indent=2))
