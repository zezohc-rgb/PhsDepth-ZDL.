#!/usr/bin/env python3
"""Build a four-knob pass-through ZDL with upstream ZoomMultistompZDL tools.
Run from a local clone of the upstream repo, after providing required local
TI compiler and stock handler blobs (see upstream docs/STOCK-FILES.md).
This script does NOT work in plain GitHub Actions as shipped.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
UPSTREAM = Path(os.environ.get("ZOOM_ZDL_ROOT", "")).expanduser()
if not os.environ.get("ZOOM_ZDL_ROOT") or not (UPSTREAM / "build" / "linker.py").is_file():
    sys.exit("Set ZOOM_ZDL_ROOT to a local ZoomMultistompZDL checkout.")
TI_ROOT = Path(os.environ.get("TI_C6000_ROOT", "")).expanduser()
CL6X = TI_ROOT / "bin" / "cl6x"
if not CL6X.is_file():
    sys.exit("Set TI_C6000_ROOT to a local TI C6000 compiler installation.")
manifest = json.loads((HERE / "manifest_pedal.json").read_text())
if not 1 <= manifest["fxid"] <= 65535:
    sys.exit("STOP: set a verified unused fxid in manifest_pedal.json first.")
sys.path.insert(0, str(UPSTREAM / "build"))
sys.path.insert(0, str(UPSTREAM / "src" / "airwindows" / "common"))
from linker import LinkerConfig, link, params_from_manifest
from custom_covers import make_cover
src = HERE / "phsdepth.c"
obj = HERE / "phsdepth.obj"
out = HERE.parent / "dist" / "PhsDepth.ZDL"
out.parent.mkdir(exist_ok=True)
subprocess.run([
    str(CL6X), "--c99", "--opt_level=2", "-mv6740", "--abi=eabi",
    "--mem_model:data=far", f"--include_path={TI_ROOT / 'include'}",
    "-c", str(src), f"--output_file={obj}"
], check=True, cwd=HERE)
cfg = LinkerConfig(
    effect_name=manifest["effect_name"],
    screen_image=make_cover(manifest["effect_name"], [p["name"] for p in manifest["params"]]),
    audio_func_name=manifest["audio_func_name"],
    gid=manifest["gid"], fxid=manifest["fxid"],
    params=params_from_manifest(manifest["params"]),
    obj_path=obj, output_path=out,
    fxid_version=manifest["fxid_version"].encode("ascii"),
    flags_byte=manifest["flags_byte"],
    audio_nop=manifest["audio_nop"],
)
link(cfg)
print("Generated experimental pass-through:", out)
