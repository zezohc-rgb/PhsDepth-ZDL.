#!/usr/bin/env python3
"""Offline, uncalibrated MN3101/Q4 charge-model sensitivity experiment.

Not the released DSP's clock calibration. All unknown semiconductor voltages
are named assumptions. The manufacturer's divide-by-two must be accounted for.
"""
from pathlib import Path
import json,math
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
def astable_period(control,supply=9.,threshold=4.5,vbe=.65,diode=.65,reset=0.):
 # R36=R37=4.7k, Q4 ideal emitter follower minus Vbe, D1 offset.
 start=max(0.,(control-vbe)/2-diode)
 if not 0<=start<threshold<supply:raise ValueError('invalid oscillator voltage assumptions')
 return 150000*47e-12*math.log((supply-start)/(supply-threshold))+reset

def experiment():
 cases=[]
 # Plausible illustrative values, NOT measured tolerances or guaranteed specs.
 for threshold in (3.8,4.5,5.2):
  for reset in (0.,1e-6):
   periods=[astable_period(v,threshold=threshold,reset=reset) for v in np.linspace(2.,7.,101)]
   # MN3101 outputs fosc/2; MN3007 delay = 512/fclock = 1024*Tosc.
   cases.append({'threshold_v_assumed':threshold,'reset_us_assumed':reset*1e6,
                 'delay_ms_predicted':[1024*min(periods)*1000,1024*max(periods)*1000]})
 return {'status':'uncalibrated sensitivity experiment; NOT CE-2 measurements and NOT release delay calibration',
  'fixed_schematic_components':{'R38_ohm':150000,'C22_farad':47e-12,'R36_ohm':4700,'R37_ohm':4700},
  'assumptions':{'supply_v':9,'Q4_vbe_v':.65,'D1_drop_v':.65,'control_v_range':[2,7],
   'unmodeled':'Q5 finite discharge, inverter thresholds/hysteresis/propagation, load currents, component tolerances'},
  'datasheet_reference':'https://media.digikey.com/pdf/Data%20Sheets/Panasonic%20Semiconductors%20ICs%20PDFs/MN3101.pdf',
  'oscillator_to_output_frequency_ratio':2,'cases':cases}
if __name__=='__main__':
 report=experiment();(ROOT/'docs/clock-sensitivity.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
