import importlib.util,pathlib,unittest
P=pathlib.Path(__file__).resolve().parents[1]/'tools/clock_reference.py'
spec=importlib.util.spec_from_file_location('clock_reference',P);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class ClockReferenceTests(unittest.TestCase):
 def test_charging_equation(self):
  # Independent RC charging trace reaches the requested threshold.
  import math
  for control in (2,4.5,7):
   t=m.astable_period(control);start=max(0,(control-.65)/2-.65)
   final=9-(9-start)*math.exp(-t/(150000*47e-12))
   self.assertAlmostEqual(final,4.5,places=12)
 def test_divider_and_sensitivity(self):
  report=m.experiment();self.assertEqual(report['oscillator_to_output_frequency_ratio'],2)
  low,high=report['cases'][0]['delay_ms_predicted'];self.assertGreater(high,low)
  self.assertNotEqual(report['cases'][0]['delay_ms_predicted'],report['cases'][-1]['delay_ms_predicted'])
  for control in (2,4.5,7):self.assertAlmostEqual(m.astable_period(control,reset=1e-6)-m.astable_period(control),1e-6)
 def test_invalid_assumptions(self):
  with self.assertRaises(ValueError):m.astable_period(7,threshold=1)
