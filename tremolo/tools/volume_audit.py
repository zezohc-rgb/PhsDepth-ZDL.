#!/usr/bin/env python3
"""RMS/peak audit of the exact adapter. Does not infer perceived loudness parity."""
import hashlib,json,math,subprocess,tempfile
from pathlib import Path
r=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as work:
 exe=Path(work)/'volume-audit'
 subprocess.run(['cc','-std=c99','-O2','-ffp-contract=off',str(r/'tools/volume_audit.c'),'-lm','-o',str(exe)],check=True)
 p=subprocess.run([str(exe)],check=True,capture_output=True,text=True)
rows=[json.loads(line) for line in p.stdout.splitlines()]
steady=[v for v in rows if v['wave']==0 and v['depth']==50 and v['vol']==63 and v['mode']==0 and v['signal']<=2]
assert steady and max(abs(v['rms_delta_db']) for v in steady)<.25
assert all(math.isfinite(v['rms_delta_db']) and v['output_peak']<=.5001 for v in rows)
assert all(abs(v['rms_delta_db'])<.0001 for v in rows if v['wave']<3 and v['depth']==0 and v['vol']==50)
report={'artifact_sha256':hashlib.sha256((r/'build/DmTrem.ZDL').read_bytes()).hexdigest(),'passed':True,
 'measurement':'L/Mono RMS after 2 s settling; 10 s measurement per case; native exact adapter',
 'signals':{'0':'constant gain probe, amplitude .25','1':'440 Hz sine, peak .2','2':'three-harmonic 110 Hz signal with repeated exponential note envelope'},
 'default_change':{'old_vol':50,'new_vol':63,'shark_depth':50,'mode':'Qtr','nominal_bpm':120},
 'limits':'RMS over a window is not perceived loudness. Tremolo intentionally changes instantaneous volume. Strong Chop and correlated note envelopes need manual trim. No hardware or ADC test.',
 'cases':len(rows),'results':rows}
(r/'build/volume-report.json').write_text(json.dumps(report,indent=2)+'\n')
for v in rows:
 if v['wave']==0 and v['depth']==50 and v['mode']==0 and v['bpm']==120:
  print(f"signal {v['signal']} Vol {v['vol']}: {v['rms_delta_db']:+.3f} dB RMS; peak {v['output_peak']:.3f}")
print(f'PASS: {len(rows)} measured cases; corrected default carrier RMS within 0.25 dB')
