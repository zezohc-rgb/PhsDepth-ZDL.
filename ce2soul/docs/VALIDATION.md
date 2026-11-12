# CE-2 Soul 0.43 validation

The owner reports successful physical use of 0.40 and a subjective close comparison with Brainworx Blue Chorus, with slightly less bass. **Version 0.43 has not yet been physically tested or compared to a physical CE-2.** Results below cover the digital model and emulated ABI.

## Reproduce

From root: `./ce2soul/tools/build.sh`, then `./ce2soul/tools/test.sh`. Numerical dependencies are in `ce2soul/requirements-test.txt`. `python3 ce2soul/tools/design.py` regenerates coefficients. `python3 ce2soul/tools/measure_gain.py` regenerates the level report against original deterministic test signals.

For the actual binary emulator, fetch and verify the pinned source, then run:

```sh
mkdir -p work
curl -fL https://berbasoft.com/ziddle/ziddle-1793487371.zip -o work/ziddle.zip
echo 'c45f11a0ffa51c327169c3c8c6965043882d39b4a8f5f0ac624603e5941579a3  work/ziddle.zip' | sha256sum -c -
unzip -q work/ziddle.zip -d work
python3 ce2soul/tools/emulator/run.py --ziddle work/ziddle-1793487371
```

The emulator supplies hermetic host callbacks; it is not the pedal's firmware loader, ADC/DAC or CPU scheduler. Reports: [build](../build/build-report.json), [structure](../build/validation.json), [emulator](../build/emulator-report.json), [gain](../build/gain-report.json), [headroom](../build/headroom-report.json), [delay](../build/delay-validation.json), [cover](../build/cover-validation.json).

## Completed checks

- **25 Rate/Depth combinations x12 seconds**: finite output, ring bounds, continuous delay, LFO cycles and silence decay. Sine/noise fixture peak 0.382859; max adjacent sample difference 0.116532. These are fixture-specific observations.
- **Three-minute** static-delay run with NaN-poisoned unused history, two independent instances and live control edits. Delay drift within 0.003 sample. Both reciprocal domains are checked across the revised delay range.
- **Actual wrapper**: mono L input duplicated to L/R, different R input ignored, bypass preservation, shuttle, buffer guards, invalid controls, null/short arenas. State uses **8316 bytes** and a bumped version tag.
- **ASan/UBSan** pass with immediate halt on any undefined behavior. The previously corrected wrap-to-1024 case remains covered by long runs.
- **15 Python tests** cover rate/divider, loaded pots, stable SOS filters, independent four-node/impedance response, impulse/comb response, clock transport, delay observations/extrema, linearity at moderate levels, cubic interpolation, headroom, clock-charge sensitivity, nominal direct attack, wet shelf and level regression against frozen 0.30 results.
- Circuit/SOS error stays below 0.02 dB over 20 Hz–16 kHz against the bilinear-warped ideal model. Interpolation magnitude error stays below 0.16 dB through 6.6 kHz. Neither establishes analog-hardware equality.
- **Level regression**: 18 synthetic plucked-harmonic/noise cases. 0.30 gain was −5.10 to −4.30 dB relative to input; 0.43 gives +0.99 to +1.57 dB. These moderate signals remain below the output knee. Frequency-dependent chorus cancellation and perceived/hardware loudness are not universally bounded by these fixtures.
- **Output guard**: low-level unity, odd symmetry, monotonicity, continuous knee/slope, no overshoot and 0.98 ceiling under strong drive. At 24 sine frequencies 60 Hz–12 kHz, five settings and 0.9 input peak, max output is approximately **0.98**. This includes intended soft compression of hot peaks, not unlimited linear headroom. Full-scale impulse remains below full scale.
- **C674x execution**: **12 cases / 1179648 channel samples**, including three additional hot ±1.25 square-wave cases and live edits/tails/bypass. Max TI/host absolute difference **0.000022173**, **zero unsupported instructions**. Max 3668 packets and 4855 emulated cycles per block; not actual pedal DSP cost. All enabled outputs are checked against the guard ceiling.
- **Structure**: real 8026-byte C6000 ELF ZDL, correct exports/identity/relocations and two controls, no undefined DSP helper calls/BSS/large writable globals. Code/constants fit upstream limits. Pinned TI/compiler/linker rebuild is byte-identical.
- **Cover**: all **8192 decoded pixels**, two overlay positions and empty third slot match the source. Static captions under knobs are removed. The PNG comes from linked pixels, not an imagined pedal screenshot; firmware rendering still needs a new physical check.

SHA256: `be95021ef2aa7634ba29ecfb5b8b34dc29674c805224a569613f67a16733f9fa`.

## Scope and remaining evidence

[GAIN_WARMTH_040.md](GAIN_WARMTH_040.md) documents user feedback, gain restoration, the intentional wet-only voicing and digital peak guard. The latter two are engineering choices, not measured Japanese CE-2 components/distortion. The [delay model](DELAY_REVISION_030.md) still relies on partial published observations with an extrapolated maximum Depth range.

Still pending: current build on the real Zoom (level/voicing/overlays/patches/chains/CPU), calibrated original-CE-2 response and distortion, and a permitted reference-plugin capture. See [COMPATIBILITY.md](COMPATIBILITY.md). Previous versions remain available at their recorded commits for comparison; never install duplicate IDs together.

[BASS_041.md](BASS_041.md) documents the +1 dB / 180 Hz wet-only bass shelf and a pinned download of the owner-tested 0.40 for comparison. The response regression isolates this shelf from the previous voicing; state size and cover stay unchanged.

0.42 is an artwork-only correction: static rings and scale marks removed from the live knob regions. Decoded pixels in both reserved panels must be blank. All 18 host gain fixture results exactly match 0.41. DSP source and coefficients are unchanged; linked addresses can change when cover data size changes. See [DISPLAY_042.md](DISPLAY_042.md).

0.43 changes only the wet high-shelf asymptote to −2.5 dB. New native/sanitizer, 15 Python, build/structure/cover, deterministic rebuild and 12-case C674x runs pass. Recording-informed candidate screening is documented separately in [RECORDINGS_043.md](RECORDINGS_043.md); the narrow high-band improvement is not a full plugin match. Owner supplied physical 0.42 recordings, but no physical 0.43 recording is available yet.
