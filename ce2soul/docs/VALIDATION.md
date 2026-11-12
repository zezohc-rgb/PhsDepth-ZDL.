# CE-2 Soul 0.20 validation

No physical pedal or reference CE-2 was tested. Results apply to the documented digital model and ABI under the test conditions below.

## Reproduce

Run `./ce2soul/tools/build.sh` and `./ce2soul/tools/test.sh` from the repository root. Install `ce2soul/requirements-test.txt` for numerical checks. Build dependencies are pinned in the existing repository bootstrap. Regenerate coefficients with `python3 ce2soul/tools/design.py`; the shipped coefficients require no numerical library on DSP.

Binary emulation uses Rust and the pinned public Ziddle source:

```sh
mkdir -p work
curl -fL https://berbasoft.com/ziddle/ziddle-1793487371.zip -o work/ziddle.zip
echo 'c45f11a0ffa51c327169c3c8c6965043882d39b4a8f5f0ac624603e5941579a3  work/ziddle.zip' | sha256sum -c -
unzip -q work/ziddle.zip -d work
python3 ce2soul/tools/emulator/run.py --ziddle work/ziddle-1793487371
```

The script supplies hermetic host callbacks and executes the **actual compiled ZDL**. It does not load proprietary firmware. Reports: [build report](../build/build-report.json), [structural report](../build/validation.json), [emulator report](../build/emulator-report.json), [headroom report](../build/headroom-report.json).

## Completed checks

- **25 combinations** of RATE/DEPTH (0/25/50/75/100), each 12 seconds: finite output, ring bounds, delay bounds/continuity and LFO cycles; excitation followed by four seconds of silence. Peak of the mixed sine/noise fixture: 0.191377, max adjacent sample change 0.059755. These are fixture results, not universal audio bounds.
- **Three minutes** of Depth=0 at slow Rate, with NaN-poisoned stale memory: output remains zero and delay drift stays within 0.003 sample of the static model. Two independent states also produce identical output without shared globals.
- **Actual host wrapper**: L-only mono duplication, different R input ignored, bypass preserves both inputs, shuttle transfer, guard cells, invalid controls and null/short arenas. Live Rate/Depth edits are smoothed without restarting the oscillator.
- The same C checks pass **AddressSanitizer and UndefinedBehaviorSanitizer**.
- **Eleven Python tests**: full rate curve, stable float32 poles, independent four-node coupled filter and impedance checks, loaded-pot calculations, static rendered impulse/comb response, modulation/linearity, fractional interpolation, headroom and integrated clock transport, plus three clock-reference sensitivity tests. Clock oracle uses double-precision cumulative clock inversion independently of the C read-pointer implementation; max timing discrepancy stays below 0.03 sample over 50000 samples. Filter response deviation from the bilinear-warped ideal model stays below 0.02 dB across 20 Hz–16 kHz; not an unwarped analog/pedal match. Cubic interpolation passband magnitude error stays below 0.16 dB through 6.6 kHz.
- **Headroom fixture**: 24 sine frequencies from 60 Hz–12 kHz at 0.9 full-scale peak, five control pairs. Highest observed output peak 0.803552; no sample clipping in these fixtures. A full-scale impulse also remains below full scale. Arbitrary input/transient peaks and analog voltage calibration are not covered.
- **Structural ZDL checks**: 7794-byte real C6000 ELF shared object, 13 sections, exact RATE/DEPTH descriptors, exports/entry point/relocations/header sizes and identity. No undefined DSP helper calls, BSS or large writable globals. 8308 bytes of guarded instance state. Compiled code/constants fit the upstream caps.
- **C674x binary execution**: 9 parameter cases, **786432 channel samples**, including startup, defaults, live edits, mono output and bypass. Maximum TI/host absolute audio difference **0.000002122**, **zero unsupported instructions**. Maximum 3279 instruction packets and 4393 emulated cycles per block; these are not real pedal DSP utilization.
- **Byte-identical rebuild** with the pinned linker/compiler and reproducible coefficients. Artifact SHA256: `cce85ee86094fe69cddf2b73ef72c93a1ad7ba2992c564fee0a81ae38d27db04`.
- **ID audit** across seven public collections, recorded at pinned commits, plus retired-ID registry review. Candidate gid 6/fxid 948 is clear in these sources. Existing PhaserZeh binary/ID remain unchanged.

Version 0.20 adds loaded filter/pot tests; the current reports correspond to the corrected Rate and filter model. The separate clock-charge experiment validates equations, not a measured calibration. See [REFINEMENT_020.md](REFINEMENT_020.md).

During 0.10 development, the clock-oracle check initially exposed float phase accumulation drift. The oscillator now uses a 31-bit fixed-point phase accumulator, preserving continuous phase with much smaller timing error. The final tests and binary-emulator report correspond to that correction.

## Missing evidence

Physical MS-70CDR boot/loader tests, sustained real-time chains and CPU load, USB installer presentation, actual I/O levels, repeated save/recall/on-off, and recorded comparison against an original CE-2. The fixed mixing/filters and provisional clock/depth/rate parameters are **model comparisons**, not measured vintage-pedal fidelity. Follow [COMPATIBILITY.md](COMPATIBILITY.md) for the physical test sequence.
