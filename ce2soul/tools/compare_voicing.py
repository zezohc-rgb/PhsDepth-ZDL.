import ctypes as C,subprocess,sys,json,re,hashlib
from pathlib import Path
import numpy as np
from scipy import signal
from scipy.io import wavfile
import argparse
p=argparse.ArgumentParser(description='Compare wet voicing candidates using one clean recording and a mono reference; no time-varying transfer-function identification.')
p.add_argument('--clean',type=Path,required=True);p.add_argument('--reference',type=Path,required=True);p.add_argument('--output-dir',type=Path,required=True);args=p.parse_args()
repo=Path(__file__).resolve().parents[1];work=args.output_dir.resolve();work.mkdir(parents=True,exist_ok=True)
def read(name):
 fs,x=wavfile.read(args.clean if name=='limpo' else args.reference)
 if not np.issubdtype(x.dtype,np.signedinteger):raise ValueError('Expected signed PCM WAV')
 scale=2**(np.iinfo(x.dtype).bits-1);x=x.astype(float)/scale
 return fs,x.mean(axis=1) if x.ndim==2 else x
fs,x=read('limpo');ref_fs,target=read('brainworx');assert fs==ref_fs==44100;assert len(target)>=len(x);x=x.astype(np.float32);target=target[:len(x)]
bands=[(80,160),(160,315),(315,630),(630,1250),(1250,2500),(2500,5000)]
def levels(x):
 f,p=signal.welch(x,fs,nperseg=8192)
 return np.array([10*np.log10(np.trapezoid(p[(f>=lo)&(f<hi)],f[(f>=lo)&(f<hi)])) for lo,hi in bands])-20*np.log10(np.sqrt(np.mean(x.astype(float)**2)))
base=(repo/'src/coefficients.h').read_text();rows=[]
for bass,high in [(1,-4),(1,-3),(1,-2.5),(1,-2),(1,-1)]:
 b=np.polymul([10**(high/20)/(2*np.pi*2000),1],[1/(2*np.pi*180),10**(bass/20)])
 a=np.polymul([1/(2*np.pi*2000),1],[1/(2*np.pi*180),1]);bz,az=signal.bilinear(b,a,fs=fs);sos=signal.tf2sos(bz,az)[0]
 row=sos[[0,1,2,4,5]].astype(np.float32);lit=lambda v:format(float(v),'.9e')+'f'
 hdr=re.sub(r'static const float CE_WARM\[1\]\[5\]=.*?;', 'static const float CE_WARM[1][5]={{'+','.join(map(lit,row))+'}};',base)
 (work/'coefficients.h').write_text(hdr)
 for name in ('ce2_core.h','ce2_dsp.c','ce2_dsp.h'):(work/name).write_bytes((repo/'src'/name).read_bytes())
 so=work/f'b{bass}h{high}.so';subprocess.run(['cc','-O2','-ffp-contract=off','-shared','-fPIC',str(work/'ce2_dsp.c'),'-o',str(so)],check=True)
 lib=C.CDLL(str(so));lib.ce2_state_size.restype=C.c_size_t;lib.ce2_init.argtypes=[C.c_void_p,C.c_float,C.c_float];lib.ce2_process.argtypes=[C.c_void_p,C.c_void_p,C.c_void_p,C.c_uint,C.c_float,C.c_float]
 s=C.create_string_buffer(lib.ce2_state_size());y=np.zeros_like(x);lib.ce2_init(s,.5,.5);lib.ce2_process(s,x.ctypes.data,y.ctypes.data,len(x),.5,.5)
 err=levels(y)-levels(target);rows.append({'bass_db':bass,'high_db':high,'rms_band_error_db':float(np.sqrt(np.mean(err**2))),'host_minus_plugin_bands_db':err.tolist()})
print(json.dumps(rows,indent=2));(work/'report.json').write_text(json.dumps({'sample_rate':fs,'rate':50,'depth':50,'clean_sha256':hashlib.sha256(args.clean.read_bytes()).hexdigest(),'reference_sha256':hashlib.sha256(args.reference.read_bytes()).hexdigest(),'metric':'unweighted RMS error of six Welch band energies relative to total RMS, 80–5000 Hz','bands':bands,'scope':'host rendering, same clean input, LFO phase not aligned; not measured revised hardware','candidates':rows},indent=2))
