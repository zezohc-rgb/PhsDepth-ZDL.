# CE-2 Soul — original MS-70CDR

Experimental chorus inspired by the **mono Boss CE-2 (1979)**. Original DSP, not a renamed Zoom effect or a claimed indistinguishable clone. Target: blue Zoom MS-70CDR, reported firmware 2.10. **This chorus has not been physically tested on the pedal or compared against a physical CE-2.**

Download: [build/CE2Soul.ZDL](build/CE2Soul.ZDL). Display name: `CE-2 Soul`, version `0.21`. Only **RATE** and **DEPTH**, 0–100, defaults 50/50. RATE models approximately 0.321–3.561 Hz; DEPTH changes clock/delay modulation, never mix. Internal nominal full-depth delay is approximately 8.5–10.75 ms, explicitly provisional. The first 23.2 ms primes the ring, followed by a 5.8 ms wet fade.

Use **L/Mono input**. Enabled processing ignores R input and duplicates the same mono result to both outputs. Bypass preserves both incoming channels. This is intentional: no stereo phase inversion, widening or separate modulation.

## Build and test

From the repository root:

```sh
python3 -m pip install -r ce2soul/requirements-test.txt
./ce2soul/tools/build.sh
./ce2soul/tools/test.sh
python3 ce2soul/tools/emulator/run.py --ziddle /path/to/ziddle-1793487371
```

Build bootstraps the same official TI C6000 8.5.0.LTS compiler and pinned `repeat98/ZoomMultistompZDL` linker as PhaserZeh. It needs network on first run; no compiler is invented or bundled. Python filter dependencies are for tests/design only, not DSP execution. Coefficients are checked in; regenerate with `python3 ce2soul/tools/design.py`. Rust/cargo is needed only for the optional binary emulator (see [compatibility](docs/COMPATIBILITY.md)).

A byte-identical check: `./ce2soul/tools/build.sh --output-dir work/rebuilt-ce2` from root, then `cmp ce2soul/build/CE2Soul.ZDL ce2soul/work/rebuilt-ce2/CE2Soul.ZDL` (the relative output path resolves from `ce2soul/`).

## Screen and official plugin reference

Version 0.21 adds a CE-2-inspired monochrome cover with two knobs, central indicator, Chorus/CE-2 lettering and a rectangular SOUL pad. [Preview](build/CE2Soul-cover.png). Audio DSP is identical to 0.20. [Official plugin research and capture procedure](docs/PLUGIN_REFERENCE.md) documents why no Boss-plugin measurements have been made here and supplies original test signals for a future authorized comparison.

Run `python3 ce2soul/tools/inspect_cover.py` from root to decode the linked image, verify all 8192 pixels and two control-overlay coordinates, and regenerate the PNG without extra image libraries.

## What is modeled

One mono fractional delay with four-point Lagrange interpolation, integrated BBD clock transport over 512 two-phase clock periods, triangle LFO with loaded Rate/Depth pots and the schematic's 220k/10nF lowpass, smooth parameter edits, matched circuit-derived emphasis and de-emphasis, and pre/post coupled capacitor/lowpass networks. Equal dry/wet branch gains are fixed; a common 0.5 gain normalizes their sum for digital headroom. No feedback, compander, noise injection, arbitrary saturation, mix control or extra modes.

Version 0.20 corrects the Rate taper and models filter loading, including the mixer load on the wet coupling capacitor. Existing RATE values now run faster in the middle of the range; check saved presets. See [refinement details](docs/REFINEMENT_020.md).

The transistor stages are idealized; BBD charge transfer, noise, clock feedthrough, input loading and headroom-dependent nonlinearities are not calibrated. Absolute gain is normalized, not a reproduction of the CE-2's analog output gain. [Research and assumptions](docs/RESEARCH.md), [limitations/install checklist](docs/COMPATIBILITY.md), [test results](docs/VALIDATION.md).

## Files

- `src/`: shared DSP, opaque-state host API and generated coefficients.
- `zoom/`: real C674x wrapper, manifest, procedural two-knob cover and builder.
- `tests/`, `tools/`: reproducible host, sanitizer, frequency-response and binary execution checks.
- `build/`: actual ZDL, cover, hashes and reports. No proprietary effect/firmware code.

Candidate identity `0x060003B4` (gid 6, fxid 948) differs from PhaserZeh and audited stock/community files. There is no global registry: check the installed inventory before writing. Use the owner's existing original-MS ZDL installation workflow, add this as a **new custom effect**, and keep all factory effects. No script flashes firmware or communicates with the pedal.

This project is independent of Boss/Roland and Zoom. Their names identify references/targets only. Original new source is MIT; upstream runtime/compiler notices are in the repository's `licenses/` directory. PhaserZeh files and binary remain unchanged in the repository root.
