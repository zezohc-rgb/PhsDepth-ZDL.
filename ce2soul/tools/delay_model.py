"""Convert published BBD output clocks to an explicitly approximate model."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def fit():
 source=json.loads((ROOT/'docs/clock-observations.json').read_text())['sources'][0]
 center=512/source['depth_zero_clock_hz_approx']*1000
 low=512/source['depth_middle_clock_max_hz']*1000
 high=512/source['depth_middle_clock_min_hz']*1000
 # Preserve the one reported DC anchor. Infer a linear excursion from span
 # at half depth, without fitting asymmetry to three rough observations.
 amplitude=high-low
 mid=[center-amplitude*.5,center+amplitude*.5]
 predicted=[512000/mid[1],512000/mid[0]]
 observed=[source['depth_middle_clock_min_hz'],source['depth_middle_clock_max_hz']]
 return {'center_ms':center,'full_depth_amplitude_ms_estimated':amplitude,
  'depth_middle_delay_ms_observed_derived':[low,high],
  'depth_middle_delay_ms_model':mid,'depth_middle_clock_hz_model':predicted,
  'middle_clock_max_relative_residual':max(abs(a/b-1) for a,b in zip(predicted,observed)),
  'full_depth_delay_ms_extrapolated':[center-amplitude,center+amplitude],
  'sample_rate':44100,'center_samples':center*44.1,'amplitude_samples':amplitude*44.1,
  'status':'Approximate software tuning to partial published observations. Full Depth is extrapolated, not measured.',
  'basis':'MN3007: 1024/(2*f_output_clock); no additional MN3101 divide-by-two at these observed pins'}
if __name__=='__main__':print(json.dumps(fit(),indent=2))
