# TRM-1 original: evidence and implementation limits

Primary reference: Diamond Tremolo user manual v1.03, November 17, 2009.
https://cdn.shopify.com/s/files/1/0716/1387/4479/files/Manual-Diamond_Tremolo_v1.03.pdf?v=1678928380

This is an original digital approximation. No original TRM-1 was measured. A passing emulator comparison verifies our implementation across architectures, NOT equality with a Diamond pedal.

| Original behavior | DmTrem 0.31 | Remaining difference |
|---|---|---|
| Sharkfin, Sine, optical Square, JFET Chop | All four wave choices | Sharkfin curve and optical response not measured |
| Rounded optical Square, sharp full-mute Chop | Separate stateful and hard-gate paths | Real transition shapes and leakage unknown |
| Chop Depth controls duty; center 50%; clockwise less on-time | Implemented and tested | 95/5% endpoints are provisional |
| Quarter base rate; Eighth 2x with accents; DBL 4x with four-pulse accents | Implemented | Exact accent ratio unknown |
| Triplet three pulses/two base beats; DBL six-pulse accents | Implemented | Exact accent ratio unknown |
| Rhythm eighth/eighth/quarter; DBL four sixteenths/two eighths | Implemented final patterns | Morph during DBL ramp not established |
| Chaos varies speed around nominal | Deterministic per-cycle random rates | Distribution and random timing law unknown |
| Manual engages optical modulation with synchronized start; Chop mutes while held | Implemented with Hold parameter | UI latch substitutes for original momentary footswitch |
| Hold >=300 ms initiates DBL; release can freeze intermediate speed | Core supports ramp and freeze; Zoom DBL is a parameter with automatic ramp | Physical switch timing unavailable; no 300 ms detector in ZDL |
| Complete DBL hold approximately 2.5 seconds | Candidate linear ramp of 2.2 seconds, inferred after 300 ms recognition | Curve and exact timing not measured; parameter ramp starts immediately |
| Tap tempo | Host quarter-period service integrated and emulated; see TAP_TEMPO.md | Physical Zoom tap test pending; Diamond averaging, timeout and knob arbitration not reproduced |
| Underlying rate retained across modes | Speed control retained | Pattern phase continuity during mode changes not measured |
| Analog mono pedal, true bypass | L/Mono processed and copied to both outputs; bypass leaves both input channels untouched | Zoom's conversion/latency/hardware bypass cannot become TRM-1 analog true bypass |
| Vol compensates apparent loudness; clean boost possible | Independent gain, no automatic normalization | Original gain range and taper unknown; current 0–2 linear; factory Vol 63 compensates the default pulse only |

## Provisional sonic constants

Optical stage is a one-pole GAIN-domain approximation, with 5 ms attack and 40 ms release, not a reconstructed resistance-divider circuit. It does not model light-history, intensity-dependent time constants, analog bandwidth or headroom. No arbitrary EQ or saturation is added.

Sharkfin uses a 25/75 smoothstep envelope. Accent strength is 20%; Chop accented on-time widens by 2 percentage points. Chaos chooses per-cycle multipliers in [0.75,1.25]; time-average rate need not exactly equal its center. These are engineering choices, not manufacturer data.

An owner's reported periods imply approximately 0.658–11.628 Hz, but mode/DBL settings and measurement procedure were not reported. Speed uses those endpoints with provisional linear taper. Source: https://tremolo-project.blogspot.com/2018/05/diamond-trm1-tremolo.html

Rate changes now settle with a candidate 40 ms filter; its exact law remains unmeasured.

## Precision improvements

32-bit phase accumulation avoids accumulated float drift. The native oracle tests phase error over ten seconds against a sample-period tolerance, and Sine against libm cosine independently of the implementation. TI DSP has no unresolved helper symbols or calls to outlined DSP routines. Display callbacks are the only allowed object functions outside .audio.

Original waveform captures, circuit trace or firmware evidence are still required to calibrate the above unknowns. The code deliberately exposes them rather than representing another pedal's constants as Diamond measurements.
