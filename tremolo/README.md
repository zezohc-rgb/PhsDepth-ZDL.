# DmTrem: original Diamond TRM-1-inspired experiment

Status: working portable audio DSP, host tests and an uncompiled Zoom adapter.
No installable ZDL or verified sonic equivalence. Previous phaser files are preserved.

## Implemented

- Sharkfin candidate, sine, optical-style square and separate hard Chop.
- Optical gain smoothing with separate adjustable attack/release.
- Depth changes modulation depth; in Chop it changes on-time, centered at 50%.
- Quarter, accented eighth, accented triplet, rhythmic, approximate chaos and manual modes in the portable API.
- DBL selects the final doubled subdivision/pattern. Manual uses an explicit held event in the portable API.
- Shared stereo envelope, independent per-instance state, bounded parameters, no heap or external math calls in DSP.

## Explicit approximations and omissions

The optical stage currently smooths a gain target with a one-pole response; it is NOT a component-level LED/LDR circuit simulation. Defaults of 5 ms attack and 40 ms release are engineering placeholders. Light-dependent dynamics, nonlinear resistance and light-history effects remain future calibration work. No Guitarix code was copied.

Sharkfin uses an arbitrary 25/75 asymmetric smoothstep envelope, not a recovered Diamond wavetable. Accent strength 20%, Chop duty endpoints 95/5%, and chaos multipliers uniformly distributed from 0.75 to 1.25 are provisional. Chaos varies per cycle; its time-domain average is not guaranteed to equal the nominal rate. Sine uses a polynomial approximation. Floating-point phase timing has numerical error.

Tap averaging, knob/tap arbitration, switch hold recognition, partial DBL ramps, parameter-change smoothing and host tempo synchronization are not implemented. DBL is an instantaneous parameter in this version. No coloration, clipping model or automatic loudness compensation is added. Abrupt parameter changes and hard Chop can produce clicks; transition calibration is outstanding.

## Zoom adaptation

Six controls across two pages: Speed, Depth, Level, Wave, Mode, DBL. Wave order: Shark/Sine/Square/Chop. Mode order: Quarter/Eighth/Triplet/Rhythmic/Chaos. Manual is not exposed on the Zoom because press/release event access is unverified. DBL is a parameter, not a reproduction of the original pedal's footswitch ramp.

Speed is provisionally linear from 0.658 to 11.628 Hz using an owner's reported period endpoints; test conditions and original taper are unknown. Level spans 0–2 linear gain, an implementation choice. The adapter assumes normalized host parameters, planar stereo blocks of eight frames, 44.1 kHz, and the upstream ctx[3] state arena. Native C syntax checks cannot validate those ABI assumptions on hardware.

## Reproduce checks

From repository root:

```sh
cc -std=c99 -Wall -Wextra -Werror -O2 tremolo/dm_trem.c tremolo/test_dm_trem.c -lm -o /tmp/dm-test
/tmp/dm-test
cc -std=c99 -Wall -Wextra -Werror -fsyntax-only tremolo/zoom/dmtrem.c
python3 tremolo/render_demo.py
```

The renderer writes four stereo WAVs into ignored `tremolo/dist/`. These use synthetic plucked harmonics: they are previews of this algorithm, never captures of a Diamond pedal.

## Experimental ZDL build

```sh
ZOOM_ZDL_ROOT=/path/to/ZoomMultistompZDL TI_C6000_ROOT=/path/to/ti-cgt-c6000 python3 tremolo/zoom/build.py
```

Upstream inspected at commit `32f3d6877d892409c6defeeeec57040ad004d31f`. The build selects `own_runtime=True`, with source runtime handlers instead of extracted Zoom handler blobs. Compiler installation and its generated helper/relocation compatibility remain unverified. No cl6x exists in the current environment. `fxid=0` deliberately blocks packaging until an unused MOD-group ID is checked against current stock and custom collections. MOD group is 6.

Before any installation candidate: compile for TI, inspect .audio/.text and relocations for unintended outlined calls/runtime dependencies, validate ZDL structure and ID, verify saved parameter initialization and all six knob handlers, then test bypass/reload, stereo, multiple instances, CPU cost and audio on the actual MS-70CDR 2.10. The upstream DSP-cost default is a placeholder, not a measurement.

## Further research

PerkinElmer's AOI application notes describe light-level-dependent speed, asymmetric turn-on/turn-off and light-history effects. This supports investigating a richer optical model, but does not identify which device or topology Diamond used:
https://www.alldatasheet.jp/html-pdf/84389/PERKINELMER/VTL5C3/23785/39/VTL5C3.html

The upstream state/tempo research still lists custom access to host tap tempo as unresolved:
https://github.com/repeat98/ZoomMultistompZDL/blob/32f3d6877d892409c6defeeeec57040ad004d31f/docs/STATE-ABI-PROGRESS.md

Original-pedal behavior and community/software evidence are tracked separately in `docs/DIAMOND_TRM1*.md`.
