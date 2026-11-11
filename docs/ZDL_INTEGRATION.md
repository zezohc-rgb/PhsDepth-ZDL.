# ZDL integration checklist

The GitHub Actions workflow in this repository **only tests portable C code**. It does not compile a Zoom effect or produce a ZDL.

## Required engineering work

1. Identify a compatible, documented custom-effect example and its DSP callback/parameter layout in [ZoomMultistompZDL](https://github.com/repeat98/ZoomMultistompZDL).
2. Adapt `src/phsdepth_dsp.c` to the pedal's actual sample/block format and memory/CPU constraints. Avoid expensive per-sample `powf`/`tanf` in a pedal build: calculate coefficients at a lower control rate and interpolate.
3. Map four controls: Rate, Color (four modes), Level, Depth (sweep width).
4. Assign a unique custom effect ID and appropriate effect metadata/cover.
5. Use a verified ZDL packaging/build path, then validate the binary format before installing.
6. Back up patches/effects and test on the original MS-70CDR, checking bypass, knob behavior, stereo, audio artifacts and DSP load.

**No pedal-ready ZDL exists yet.** Do not install a renamed C file or an unverified binary.
