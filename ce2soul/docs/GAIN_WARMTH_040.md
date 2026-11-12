# 0.40 — mono level correction, warm voicing and LCD captions

## Owner feedback and cause

The owner ran 0.30 on the Zoom, confirmed **mono** input, reported a level drop when engaged, and requested a warmer/more immersive chorus. They also reported that the lettering under the knobs overlapped on the real display. This is user hardware feedback, not our own calibrated hardware measurement. Version 0.40 still needs a new physical test.

The previous DSP scaled the direct-plus-delayed sum by 0.5. That was an earlier digital headroom choice, not a resistor ratio taken from the CE-2 schematic. It imposed a 6.02 dB scalar attenuation and reduced the nominal direct path below bypass. The analog equal-resistor summer model supports a nominal gain of one for each input branch. Version 0.40 removes that 0.5 factor, retaining equal fixed branch coefficients and the existing filters.

The measured input/output **host-software RMS** ranges for 18 identical moderate-level fixtures are:

| Version | Gain relative to input |
|---|---|
| 0.30 | −5.10 to −4.30 dB |
| 0.40 | +0.87 to +1.44 dB |

Fixtures are deterministic bandlimited noise and synthetic plucked harmonics at three Rate and three Depth settings. They are not recorded guitars, perceived-loudness tests or proof of hardware gain matching for every note/patch. Chorus interference necessarily changes level by frequency and modulation phase. These moderate fixtures remain below the output guard knee; their improvement is not automatic gain control or compression.

Reproduce with `python3 ce2soul/tools/measure_gain.py`. The pre-change results are frozen in `tests/gain-v030.json`, identifying the original commit/artifact. Current results and artifact hash are in [gain-report.json](../build/gain-report.json). The original 0.30 download remains available at commit `d6a72c598b66c55d5a3f6b137c407bfb5396b4a9`; do not install two versions with the same ID simultaneously.

## Warmth and immersion

A fixed **wet-only** high-frequency shelving filter has unity DC gain, a 2 kHz pole and a high-frequency asymptote of −4 dB. It gently darkens the delayed layer while retaining its body; the direct branch has no new tone filter. This is a deliberate response to the owner's tonal preference, **not a newly measured component of a Japanese CE-2**. No exact subjective match or audible superiority is claimed.

The 4.65 ms center, evidence-informed Depth span, Rate law and mono routing remain unchanged. No additional wet/dry control, feedback, stereo spread or modulation modes are added. The restored wet level and darker delayed layer are the intended basis for a fuller impression; the owner's listening test must judge that result.

## Peak headroom

Removing a gain cut increases peak level. A fixed digital soft knee preserves unity up to 0.78 full scale, then smoothly compresses high peaks to a 0.98 ceiling. The knee has a continuous first derivative. It uses bounded arithmetic without a DSP math-library division. This is **digital peak protection**, not a calibrated analog/BBD distortion model. It can compress hot signals; no unlimited headroom is claimed.

Tests cover low-level linearity, odd symmetry, monotonicity, slope/ceiling, full-scale tones/impulses and actual C674x execution of additional hot-input cases. The independent impulse-response test stays below the knee and verifies the nominal direct-path gain separately before wet audio arrives.

## Display and release

Static RATE/DEPTH captions are removed from the cover, leaving the knob drawings and numeric overlay positions. Descriptor parameter names remain RATE/DEPTH so editing and saved controls retain their identity. All 8192 linked-image pixels are verified; the physical firmware overlay still needs the owner's confirmation. The body/Chorus/CE-2/SOUL design is retained.

Output remains `CE2Soul.ZDL`, gid 6/fxid 948, two controls, version 0.40. State version increments for the added filter history. No factory effect or firmware was altered. See [VALIDATION.md](VALIDATION.md) for checks and remaining limits.
