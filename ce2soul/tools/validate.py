#!/usr/bin/env python3
import importlib.util,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('validate_zdl',ROOT.parent/'tools/validate_zdl.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
m=json.loads((ROOT/'zoom/manifest.json').read_text());report=v.validate((ROOT/'build/CE2Soul.ZDL').read_bytes(),m)
(ROOT/'build/validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
