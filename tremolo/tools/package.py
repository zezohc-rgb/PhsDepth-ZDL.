#!/usr/bin/env python3
"""Deterministic test bundle with the matching validation reports and notices."""
import hashlib,json,zipfile
from pathlib import Path
r=Path(__file__).resolve().parents[1]
m=json.loads((r/'zoom/manifest.json').read_text())
build=r/'build';binary=build/'DmTrem.ZDL'
sha=hashlib.sha256(binary.read_bytes()).hexdigest()
reports=[json.loads((build/name).read_text()) for name in ('build-report.json','validation.json','emulator-report.json')]
assert reports[0]['sha256']==reports[1]['sha256']==reports[2]['artifact_sha256']==sha
assert reports[2]['passed'] and reports[2]['independent_tap_period_oracle_passed']
version=m['fxid_version'];out=build/f'DmTrem-{version}-experimental.zip'
files=[binary,r/'README.md',r/'LEIA-ME-PT.md',r/'LICENSE',r/'docs/FIDELITY.md',r/'docs/TAP_TEMPO.md',*sorted((r/'licenses').glob('*')),*[build/p for p in ('DmTrem.png','DmTrem-LCD.png','DmTrem-0.30-Manual-PT.pdf','SHA256SUMS','build-report.json','validation.json','emulator-report.json')]]
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
 for p in files:
  info=zipfile.ZipInfo(str(p.relative_to(r)),(2026,11,12,0,0,0))
  info.external_attr=0o100644<<16;info.compress_type=zipfile.ZIP_DEFLATED
  z.writestr(info,p.read_bytes())
print(out,hashlib.sha256(out.read_bytes()).hexdigest())
