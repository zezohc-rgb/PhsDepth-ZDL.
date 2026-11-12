#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
from validate_zdl import validate
root=Path(__file__).resolve().parents[1]
m=json.loads((root/'zoom/manifest.json').read_text())
report=validate((root/'build/DmTrem.ZDL').read_bytes(),m)
build=json.loads((root/'build/build-report.json').read_text())
assert report['sha256']==build['sha256']
assert (root/'build/SHA256SUMS').read_text()==report['sha256']+'  DmTrem.ZDL\n'
(root/'build/validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
