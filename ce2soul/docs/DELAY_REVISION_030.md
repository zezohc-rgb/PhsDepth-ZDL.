# Delay revision 0.30

## Evidence and its limits

[Fender3D's post #6, 2011-01-05](https://www.diystompboxes.com/smfforum/index.php?topic=89044.0) reports a CE-2 received for repair: approximately 110 kHz at minimum Depth, and 100–128 kHz at middle Depth, at MN3007 clock pins. Instrument, supply, unit condition and uncertainty are unspecified. The preceding request asks for slow Rate; the reply does not confirm it. A full original-unit calibration cannot be inferred.

[Rob Strand's post #14, 2022-03-30](https://www.diystompboxes.com/smfforum/index.php?topic=128962.0) independently recalls previous CE-2/analog CH-1 center-delay measurements around 4.5–5 ms, without the notes. This is corroboration, not a second numeric dataset. These reports support revisiting our earlier 9.625 ms center.

Structured observations and retrieval limitations: [clock-observations.json](clock-observations.json). The relevant original posts were available through indexed search despite direct-page 403 responses. No unavailable trace, maximum-Depth reading or instrument tolerance is invented.

## Reproducible engineering choice

The observed points are **already BBD output clocks**, so `delay=1024/(2*fclock)`. Do not apply the MN3101 oscillator divide-by-two again.

- Minimum Depth anchor: `512/110000 = 4.654545... ms`.
- Middle Depth endpoints: `512/128000 = 4.00 ms`, `512/100000 = 5.12 ms`.
- Infer a linear full-scale modulation amplitude from the middle-span width: `5.12-4.00 = 1.12 ms`.
- Retain the DC anchor, rather than force a nonlinear fit through three rough readings. Proposed nominal delay: `4.654545 + 1.12 * filtered_depth_triangle` ms.

At half Depth the linear model spans 4.0945–5.2145 ms (approximately 98.19–125.04 kHz), rather than exactly matching 100–128 kHz. Maximum clock residual is about 2.31%. The 3% test acceptance is an engineering choice, **not** an instrument uncertainty quoted by the source. Pot noon is assumed to mean normalized 0.5; real taper/position can differ.

Full Depth nominal range **3.5345–5.7745 ms is extrapolated**, not measured. The lowpass and actual integrated BBD transit round the extremes. `tools/delay_model.py` and `tools/design.py` regenerate all constants and fit diagnostics directly from the observation file. Internal floating-point precision does not imply measurement precision.

## What the DSP actually produced offline

At slow Rate, the host delay test measured the software's transport interval:

| Depth | Software delay extrema | Evidence status |
|---|---|---|
| 0 | 4.6545 ms, static | Proposed anchor derived from approximate clock report |
| 50 | 4.0960–5.2130 ms | Approximate match to partial published span |
| 100 | 3.5371–5.7715 ms | Extrapolation with RC/transit smoothing |

These are software results, not new hardware measurements. The report is [build/delay-validation.json](../build/delay-validation.json). Existing filters, Rate law, fixed relative mix, level normalization, mono routing, two controls, artwork and identity remain unchanged. Depth remains modulation amplitude.

## Correctness fixes and verification

The higher clock range requires new initial reciprocal estimates for both sample delay and per-sample clock count. Tests check convergence throughout both domains. Instance version is incremented to reset stale state.

Long sanitizer runs exposed a wrap boundary: adding 1024 to a tiny negative floating-point read position can round to exactly 1024. The read coordinate is now explicitly wrapped at the upper bound, and its ring index is masked. UBSan now halts immediately on any error, so a diagnostic cannot be overlooked in a nominally successful test command.

All host/sanitizer tests, 13 Python tests, structure/cover checks, actual C674x emulation and byte-identical rebuild are rerun for this release. No Boss plugin or physical pedal was used. Exact vintage-CE-2 fidelity, real Zoom CPU margin and hardware installation remain unconfirmed.
