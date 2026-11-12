"""Independent frequency-domain circuit oracle and offline DSP measurements."""
import ctypes as C
import importlib.util
import json, math, pathlib, subprocess, unittest
import numpy as np
from scipy import signal
ROOT=pathlib.Path(__file__).resolve().parents[1]
class DesignTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  (ROOT/'work').mkdir(exist_ok=True)
  subprocess.run(['cc','-O2','-ffp-contract=off','-shared','-fPIC',str(ROOT/'src/ce2_dsp.c'),'-o',str(ROOT/'work/host.so')],check=True)
  cls.lib=C.CDLL(str(ROOT/'work/host.so'));cls.lib.ce2_state_size.restype=C.c_size_t
  cls.lib.ce2_init.argtypes=[C.c_void_p,C.c_float,C.c_float]
  cls.lib.ce2_process.argtypes=[C.c_void_p,C.c_void_p,C.c_void_p,C.c_uint,C.c_float,C.c_float]
  cls.lib.ce2_rate.argtypes=[C.c_float];cls.lib.ce2_rate.restype=C.c_float
  cls.models=json.loads((ROOT/'docs/design.json').read_text())['filters']
 def render(self,x,rate=.5,depth=.5):
  x=np.asarray(x,dtype=np.float32);out=np.empty_like(x);s=C.create_string_buffer(self.lib.ce2_state_size());self.lib.ce2_init(s,rate,depth)
  self.lib.ce2_process(s,x.ctypes.data,out.ctypes.data,len(x),rate,depth);return out
 def test_filters_against_nodal_and_analog(self):
  errors={}
  for name,m in self.models.items():
   # BLT maps digital omega to analog 2*fs*tan(omega/2).
   f=np.geomspace(20,16000,400);w=2*np.pi*f/44100;s=2j*44100*np.tan(w/2)
   expected=np.polyval(m['analog_b'],s)/np.polyval(m['analog_a'],s)
   _,actual=signal.sosfreqz(m['sos'],worN=w)
   err=np.max(np.abs(20*np.log10(abs(actual/expected))));errors[name]=float(err)
   self.assertLess(err,.02)
   for section in m['sos']:self.assertLess(max(abs(np.roots(section[3:]))),1)
  # Independent four-node KCL: C5/C10 + shunt R + all three LP nodes.
  for name,r0 in [('BBD_IN',100000),('BBD_OUT',330000)]:
   for hz in (20,100,1000,5000,10000):
    v=2j*np.pi*hz;g=1/1e4;c0=33e-9
    nodal=np.array([[v*c0+1/r0+g,-g,0,0],[-g,2*g+v*3.3e-9,-g,0],[0,-g,2*g+v*8.2e-9,-g-v*8.2e-9],[0,0,-g,g+v*470e-12]])
    value=np.linalg.solve(nodal,[v*c0,0,0,0])[3]
    m=self.models[name];self.assertLess(abs(value-np.polyval(m['analog_b'],v)/np.polyval(m['analog_a'],v)),1e-12)
  # Independent impedance expression includes input C2 and wet R22 load.
  for hz in (20,100,1000,10000):
   v=2j*np.pi*hz
   zi=1/(1/47000+1/(10000+1/(v*6.8e-9)))
   zf=1/(1/47000+v*100e-12)
   value=zf/(1/(v*.47e-6)+zi)
   m=self.models['PRE'];self.assertLess(abs(value-np.polyval(m['analog_b'],v)/np.polyval(m['analog_a'],v)),1e-12)
  self.assertAlmostEqual(json.loads((ROOT/'docs/design.json').read_text())['wet_coupling_hz'],107.4373,places=3)
  self.metrics={'filter_max_db_error':errors}
 def test_rate_curve(self):
  rate=np.array([self.lib.ce2_rate(i/100) for i in range(101)])
  # Wiper voltage solved from upper/lower pot conductances and R32.
  x=np.arange(101)/100;top=(1-x)*100000;bottom=10000+x*100000
  expected=(47000/(4*.1e-6*33000*1e6))*bottom/(top+bottom+top*bottom/1e6)
  self.assertLess(np.max(abs(rate/expected-1)),1e-6);self.assertTrue(np.all(np.diff(rate)>0))
 def test_loaded_pots(self):
  data=json.loads((ROOT/'docs/design.json').read_text())
  fmax=47000/(4*.1e-6*33000*1e6)
  for raw in (0,1,25,50,75,99):
   x=raw/100;rt=(1-x)*100000;rb=10000+x*100000
   # KCL at the loaded Rate wiper, square voltage=1, reference=0.
   voltage=(1/rt)/(1/rt+1/rb+1/1000000)
   self.assertAlmostEqual(self.lib.ce2_rate(x)/fmax,voltage,places=6)
  for raw in range(101):
   d=raw/100;thevenin=(100000*d)*(100000*(1-d))/100000
   tau=(220000+thevenin)*10e-9
   self.assertAlmostEqual(data['lfo_alpha'][raw],1-math.exp(-1/(44100*tau)),places=14)
 def test_static_response(self):
  # Compare rendered, frozen Depth=0 impulse response to independent
  # circuit transfer including cubic fractional-delay response.
  n=16384;x=np.zeros(n,dtype=np.float32);x[2048]=.1;y=self.render(x,depth=0)
  H=np.fft.rfft(y)/np.fft.rfft(x);f=np.fft.rfftfreq(n,1/44100);w=2*np.pi*f/44100
  h={k:signal.sosfreqz(m['sos'],worN=w)[1] for k,m in self.models.items()}
  delay=424.4625;i=int(math.floor(delay));t=delay-i
  # cubic read of delayed signal at n-i-t, taps i-1..i+2.
  taps=np.array([-t*(t-1)*(t-2)/6,(t+1)*(t-1)*(t-2)/2,-(t+1)*t*(t-2)/2,(t+1)*t*(t-1)/6])
  D=sum(taps[j]*np.exp(-1j*w*(i-1+j)) for j in range(4))
  expected=.5*h['PRE']*h['POST']*(1+h['BBD_IN']*h['BBD_OUT']*h['HP_WET']*D)
  mask=(f>30)&(f<14000)&(abs(expected)>.05)
  err=np.max(abs(H[mask]-expected[mask]));self.assertLess(err,.004)
 def test_modulation_and_linearity(self):
  n=44100*5;t=np.arange(n)/44100;x=.1*np.sin(2*np.pi*997*t)
  a=self.render(x);b=self.render(x*.5)
  self.assertLess(np.max(abs(a*.5-b)),1e-6);self.assertTrue(np.isfinite(a).all());self.assertLess(np.max(abs(a)),.2)
  # Depth changes phase modulation, not the fixed mixing coefficients.
  static=self.render(x,depth=0);self.assertGreater(np.sqrt(np.mean((a[44100:]-static[44100:])**2)),.01)
 def test_headroom(self):
  peaks={}
  n=32768;t=np.arange(n)/44100
  for rate,depth in ((0,0),(0,1),(1,0),(1,1),(.5,.5)):
   peak=0
   for hz in np.geomspace(60,12000,24):
    y=self.render(.9*np.sin(2*np.pi*hz*t),rate,depth)
    self.assertTrue(np.isfinite(y).all());peak=max(peak,float(np.max(abs(y))))
   peaks[f'{rate},{depth}']=peak
   self.assertLess(peak,1.0) # representative .9FS sine tests, not arbitrary input proof
  impulse=np.zeros(n);impulse[2048]=1
  self.assertLess(np.max(abs(self.render(impulse))),1)
  (ROOT/'build/headroom-report.json').write_text(json.dumps({'input_sine_peak':.9,'frequencies_hz':[60,12000],'frequencies_per_setting':24,'peaks_by_rate_depth':peaks,'physical_reference':False},indent=2)+'\n')
 def test_clock_transport_oracle(self):
  # Double-precision accumulated clock, inverted independently to locate
  # the original input time. Includes transit through LFO corners.
  n=50000;rate=self.lib.ce2_rate(1);phase=(.25+rate*(np.arange(n)+1)/44100)%1
  tri=np.where(phase<.5,4*phase-1,3-4*phase)
  alpha=1-np.exp(-1/(44100*220000*.01e-6))
  lfo=signal.lfilter([alpha],[1,-(1-alpha)],tri)
  clocks=512/(424.4625+49.6125*lfo);cumulative=np.cumsum(clocks)
  source=np.interp(cumulative-512,cumulative,np.arange(n))
  state=C.create_string_buffer(self.lib.ce2_state_size());self.lib.ce2_init(state,1,1)
  self.lib.ce2_delay.argtypes=[C.c_void_p];self.lib.ce2_delay.restype=C.c_float
  inp=(C.c_float*8)();out=(C.c_float*8)();errors=[];steps=[];prev=None
  for block in range(n//8):
   self.lib.ce2_process(state,inp,out,8,1,1);j=block*8+7
   if j>2048:
    actual=self.lib.ce2_delay(state);errors.append(abs(actual-(j-source[j])))
    if prev is not None:steps.append(abs(actual-prev))
    prev=actual
  self.assertLess(max(errors),.03) # float clock interpolation/quantization is included
  self.assertLess(max(steps),.4)
 def test_interpolation_spectrum(self):
  # Fractional delay amplitude error over the wet passband, all fractions.
  worst=0
  for t in np.linspace(0,1,101):
   taps=[-t*(t-1)*(t-2)/6,(t+1)*(t-1)*(t-2)/2,-(t+1)*t*(t-2)/2,(t+1)*t*(t-1)/6]
   _,h=signal.freqz(taps,worN=np.linspace(0,2*np.pi*6600/44100,200));worst=max(worst,float(np.max(abs(20*np.log10(abs(h))))))
  self.assertLess(worst,.16)
if __name__=='__main__':unittest.main()
