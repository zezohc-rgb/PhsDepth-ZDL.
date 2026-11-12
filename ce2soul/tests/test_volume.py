"""Regression for owner-reported mono volume loss and requested wet warmth."""
import ctypes as C,importlib.util,json,pathlib,unittest
import numpy as np
from scipy import signal
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('measure_gain',ROOT/'tools/measure_gain.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
class VolumeTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.report=g.measure()
 def test_gain_against_tested_release(self):
  report=self.report;baseline=json.loads((ROOT/'tests/gain-v030.json').read_text())
  before=baseline['results'];after=report['results'];self.assertEqual(len(after),18)
  for old,new in zip(before,after):
   for field in ('signal','rate','depth'):self.assertEqual(old[field],new[field])
   self.assertAlmostEqual(old['input_rms'],new['input_rms'],places=6)
   self.assertGreater(new['gain_db'],-.5);self.assertLess(new['gain_db'],2.5)
   self.assertGreater(new['gain_db']-old['gain_db'],5)
   self.assertLess(new['output_peak'],1)
  report['baseline_version']='0.30';report['baseline_gain_db_range']=[min(v['gain_db'] for v in before),max(v['gain_db'] for v in before)]
  report['gain_db_range']=[min(v['gain_db'] for v in after),max(v['gain_db'] for v in after)]
  (ROOT/'build/gain-report.json').write_text(json.dumps(report,indent=2)+'\n')
 def test_dry_attack_gain_and_wet_shelf(self):
  # First 140 samples after an impulse precede even the shortest wet delay.
  # Compare that dry attack to the circuit's independent unity-gain path.
  lib=C.CDLL(str(ROOT/'work/gain.so'));lib.ce2_state_size.restype=C.c_size_t
  lib.ce2_init.argtypes=[C.c_void_p,C.c_float,C.c_float]
  lib.ce2_process.argtypes=[C.c_void_p,C.c_void_p,C.c_void_p,C.c_uint,C.c_float,C.c_float]
  x=np.zeros(4096,dtype=np.float32);x[2048]=.1;out=np.zeros_like(x)
  state=C.create_string_buffer(lib.ce2_state_size());lib.ce2_init(state,.5,1)
  lib.ce2_process(state,x.ctypes.data,out.ctypes.data,len(x),.5,1)
  filters=json.loads((ROOT/'docs/design.json').read_text())['filters']
  dry=signal.sosfilt(filters['POST']['sos'],signal.sosfilt(filters['PRE']['sos'],x))
  self.assertLess(np.max(abs(out[2048:2188]-dry[2048:2188])),1e-6)
  shelf=filters['WARM'];w=2*np.pi*np.array([20,2000,6000,20000])/44100
  _,h=signal.sosfreqz(shelf['sos'],worN=w);db=20*np.log10(abs(h))
  self.assertGreater(db[0],-.01);self.assertLess(db[-1],-3.95)
  self.assertTrue(np.all(np.diff(db)<0));self.assertLess(db[2],-3)
