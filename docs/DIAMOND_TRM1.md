# Diamond TRM-1 original: fidelity specification

Status: initial research specification. DmTrem 0.31 now has a TI-built experimental ZDL and emulator validation; see ../tremolo/README.md and ../tremolo/docs/FIDELITY.md. No physical hardware test or measured Diamond equivalence.
Target: original Zoom MS-70CDR, firmware 2.10, per existing hardware documentation.

## Primary reference

Diamond Tremolo user manual v1.03, November 17, 2009, linked by the manufacturer's Legacy Support page:
https://www.diamondpedals.com/pages/legacy-support
https://cdn.shopify.com/s/files/1/0716/1387/4479/files/Manual-Diamond_Tremolo_v1.03.pdf?v=1678928380

## Documented behavior (manual pages 2–8)

- Analog optical modulation; separate JFET Chop path.
- Sharkfin is asymmetric; Sine symmetric; Square is rounded by the optocoupler. Chop fully cuts audio. Depth controls Chop duty, with equal on/off at center and shorter on-time clockwise.
- Modes: quarter, eighth, triplet, rhythmic, chaotic, manual. Eighth accents groups of two, or four with DBL. Triplet is three pulses per two base beats, or six with DBL. Rhythmic durations: eighth/eighth/quarter; DBL: four sixteenths/two eighths.
- Manual starts synchronized modulation while held; Chop instead mutes while held.
- DBL starts after 300 ms; ramp completion takes approximately 2.5 s of holding. Releasing early freezes intermediate speed.
- Tap averaging favors recent taps; approximately 2 s idle ends a series. Base tempo survives mode changes.

## Measurements required before claiming sonic equivalence

The manual does not specify numerical speed limits, knob taper, optical response constants, exact Sharkfin curve, accent ratios, tap weights, ramp curve, chaos distribution, gain range, or frequency response. Do not invent these as measured values.

Capture a real TRM-1 with a stable power supply, recording dry reference and output through the same calibrated interface. Document unit identity, knob positions, sample rate, input level and interface gain. Measure interface latency first.

1. Use a steady test tone to recover gain envelopes for each waveform at multiple speeds and depths; retain raw recordings and extraction scripts.
2. Fit attack and release separately from optical Square recordings. Cross-validate against speeds and settings excluded from fitting. Check whether one-pole behavior is adequate before selecting that model.
3. Measure Chop duty endpoints and midpoint, transition duration and residual signal. Keep its model separate from optical smoothing.
4. Measure timing and accent envelopes in every mode, including DBL and interrupted ramps. Repeat chaos recordings to characterize statistics.
5. Sweep input frequency and level at minimum modulation to measure gain, coloration, headroom and distortion. Do not add arbitrary saturation or EQ.
6. Compare output envelopes, timing, spectrum and level against held-out recordings. Set numerical tolerances from measurement repeatability before evaluating; publish errors rather than asserting identity.

## Zoom integration gates

Verify actual DSP callback ABI, sample format, sample rate, stereo routing and available parameter count against upstream examples. Verify whether effect code receives switch press/release timing and host tempo; Manual and partial DBL ramps require these events. A parameter substitution must be labeled as an interface adaptation.

The existing zoom/build.py describes a pass-through build. Its presence does not validate tremolo processing. Establish compiler, required handler blobs, unique effect ID, binary validation and pedal audio/CPU testing before producing an installation candidate.

No measured reference unit data is currently available in this repository. No claim of an exact TRM-1 clone is supported yet.
