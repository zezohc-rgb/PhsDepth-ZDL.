#!/usr/bin/env python3
"""Compile a real C674x PhsDepth ZDL using a pinned ZoomMultistompZDL linker."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM_COMMIT = '32f3d6877d892409c6defeeeec57040ad004d31f'


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--upstream', default=os.environ.get('ZOOM_ZDL_ROOT'))
    ap.add_argument('--ti-root', default=os.environ.get('TI_C6000_ROOT'))
    ap.add_argument('--output-dir', type=Path, default=ROOT / 'dist')
    ap.add_argument('--ui-only', action='store_true', help='separate diagnostic; NEVER install alongside the DSP build')
    args = ap.parse_args()
    if not args.upstream or not args.ti_root:
        ap.error('provide --upstream / --ti-root or ZOOM_ZDL_ROOT / TI_C6000_ROOT')
    upstream, ti = Path(args.upstream).expanduser().resolve(), Path(args.ti_root).expanduser().resolve()
    head = subprocess.check_output(['git', '-C', str(upstream), 'rev-parse', 'HEAD'], text=True).strip()
    if head != UPSTREAM_COMMIT:
        ap.error(f'upstream must be checked out at {UPSTREAM_COMMIT}; got {head}')
    cl6x = ti / 'bin' / 'cl6x'
    if not cl6x.is_file():
        ap.error(f'missing TI compiler: {cl6x}')
    revision = subprocess.check_output([str(cl6x), '--compiler_revision'], text=True).strip()
    if revision != '8.5.0':
        ap.error(f'tested compiler is TI C6000 8.5.0; got {revision}')
    # own_runtime.py reads this at import; use one compiler for both C and ASM.
    os.environ['TI_CGT'] = str(ti)
    # Explicit build variants, unaffected by upstream's ambient diagnostic flags.
    for name in ('ZDL_MATERIALIZE_INIT', 'ZDL_SELECTOR_OUTPUT_DIR', 'ZDL_MATERIALIZE_INIT_MAX_CALLS'):
        if name in os.environ:
            ap.error(f'unset upstream diagnostic override {name} for a reproducible build')
    m = json.loads((ROOT / 'zoom/manifest_pedal.json').read_text())
    if (m['gid'], m['fxid']) != (6, 947) or m['audio_nop'] or not m['own_runtime']:
        ap.error('unexpected identity/runtime/audio mode; review the ID audit and build script')
    audit = json.loads((ROOT / 'docs/id-audit.json').read_text())
    if audit['candidate'] != {'gid': m['gid'], 'fxid': m['fxid']} or not audit['clear_in_audited_sources']:
        ap.error('ID audit does not clear this identity')
    sys.path.insert(0, str(upstream / 'build'))
    sys.path.insert(0, str(upstream / 'src/airwindows/common'))
    from linker import LinkerConfig, link, params_from_manifest, ObjFile
    from cover import make_cover, save_pbm
    from zdl_size_guard import check
    work = ROOT / 'work' / 'build'
    work.mkdir(parents=True, exist_ok=True)
    outdir = args.output_dir.resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    obj = work / 'phsdepth.obj'
    subprocess.run([str(cl6x), '--c99', '--opt_level=2', '-mv6740', '--abi=eabi',
                    '--mem_model:data=far', '--keep_asm', f'--include_path={ti / "include"}',
                    f'--define=PHSDEPTH_AUDIO_FUNC={m["audio_func_name"]}',
                    '-c', str(ROOT / 'zoom/phsdepth.c'), f'--output_file={obj}'], check=True, cwd=work)
    parsed = ObjFile(obj)
    undefined = [s['name'] for s in parsed.symbols if s['shndx'] == 0 and s['name']]
    if undefined:
        raise RuntimeError(f'unexpected DSP helper calls: {undefined}')
    for section in parsed.sections:
        if section['size'] and section['name'] in ('.bss', '.far', '.fardata', '.text'):
            raise RuntimeError(f'unexpected DSP storage/outlined helpers: {section["name"]}')
    out = outdir / 'PhsDepth.ZDL'
    cfg = LinkerConfig(effect_name=m['effect_name'], audio_func_name=m['audio_func_name'],
                       gid=m['gid'], fxid=m['fxid'], params=params_from_manifest(m['params']),
                       obj_path=obj, output_path=out,
                       screen_image=make_cover(),
                       fxid_version=m['fxid_version'].encode('ascii'), flags_byte=m['flags_byte'],
                       audio_nop=args.ui_only, own_runtime=True,
                       materialize_init=m['materialize_init'], dsp_cost=m['dsp_cost'],
                       use_object_edit_handlers=False)
    link(cfg)
    size, code_data = check(out)
    save_pbm(outdir / "PhsDepth-cover.pbm")
    report = {'artifact': out.name, 'sha256': hashlib.sha256(out.read_bytes()).hexdigest(),
              'bytes': size, 'code_data_bytes': code_data, 'upstream_commit': head,
              'ti_compiler': revision,
              'gid': m['gid'], 'fxid': m['fxid'], 'audio_nop': args.ui_only,
              'own_runtime': True, 'materialize_init': cfg.materialize_init,
              'dsp_cost_declared': m['dsp_cost'], 'dsp_cost_measured_on_pedal': False,
              'physically_tested': False,
              'dsp_undefined_symbols': undefined,
              'cover': 'PhsDepth-cover.pbm',
              'cover_sha256': hashlib.sha256((outdir / 'PhsDepth-cover.pbm').read_bytes()).hexdigest()}
    (outdir / 'build-report.json').write_text(json.dumps(report, indent=2)+'\n')
    (outdir / 'SHA256SUMS').write_text(f'{report["sha256"]}  {out.name}\n')
    print(f'Generated experimental {"UI-only" if args.ui_only else "phaser"}: {out} (NOT hardware tested)')


if __name__ == '__main__':
    main()
