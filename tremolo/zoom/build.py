#!/usr/bin/env python3
"""Experimental own-runtime ZDL build. Requires TI C6000 + pinned upstream.
No automatic ID selection or hardware-validation claim.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
HERE = Path(__file__).resolve().parent

def main():
    upstream = Path(os.environ.get('ZOOM_ZDL_ROOT', '/workspace/ZoomMultistompZDL'))
    ti = Path(os.environ.get('TI_C6000_ROOT', '/opt/ti-cgt-c6000'))
    manifest = json.loads((HERE / 'manifest.json').read_text())
    missing = []
    if not (ti / 'bin/cl6x').is_file():
        missing.append('TI C6000 compiler: set TI_C6000_ROOT (bin/cl6x missing)')
    if not (upstream / 'build/own_runtime.py').is_file():
        missing.append('upstream own runtime: set ZOOM_ZDL_ROOT')
    if not 1 <= manifest['fxid'] <= 65535:
        missing.append('verified unused effect ID: manifest fxid is deliberately 0')
    if missing:
        sys.exit('Build blocked:\n- ' + '\n- '.join(missing))
    # own_runtime.py uses TI_CGT; keep both components on the same compiler.
    os.environ['TI_CGT'] = str(ti)
    sys.path[:0] = [str(upstream/'build'),str(upstream/'src/airwindows/common')]
    from linker import LinkerConfig, link, params_from_manifest
    from custom_covers import make_cover
    obj = HERE/'dmtrem.obj'
    subprocess.run([str(ti/'bin/cl6x'),'--c99','--opt_level=2','-mv6740',
        '--abi=eabi','--mem_model:data=far',f'--include_path={ti / "include"}',
        '-c',str(HERE/'dmtrem.c'),f'--output_file={obj}'],check=True,cwd=HERE)
    out = HERE.parent/'dist/DmTrem.ZDL'
    out.parent.mkdir(exist_ok=True)
    cfg = LinkerConfig(effect_name=manifest['effect_name'],
        audio_func_name=manifest['audio_func_name'],gid=manifest['gid'],
        fxid=manifest['fxid'],params=params_from_manifest(manifest['params']),
        obj_path=obj,output_path=out,fxid_version=b'0.10',flags_byte=1,
        screen_image=make_cover('DmTrem',[p['name'] for p in manifest['params']]),
        own_runtime=True,audio_nop=False)
    link(cfg)
    print(f'Experimental binary only, not hardware validated: {out}')

if __name__ == '__main__':
    main()
