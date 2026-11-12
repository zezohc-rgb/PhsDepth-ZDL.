# Research and implementation decisions

Research date: 2026-11-12. This document separates observed source facts, circuit calculations and provisional choices. No physical CE-2, captures at known knob positions or this user's firmware image were available.

## MultiStomp feasibility

| Project | Verified scope / relevance | Used here |
|---|---|---|
| [mungewell/zoom-zt2](https://github.com/mungewell/zoom-zt2/blob/master/readme.md) | README explicitly distinguishes G1Four/G3n/G5n and MS-plus **ZD2** from original MultiStomp **ZDL**, calling them incompatible. MIDI uploader and newer metadata are not an original-MS DSP toolchain. | Research only; no ZD2 converted, no uploader invoked. |
| [ELynx/zoom-fx-modding](https://github.com/ELynx/zoom-fx-modding) | Original Effect DLL System Ver 1.0 research, MS-70CDR-relevant modifications, ABI/extraction resources and IPS patch approach; not proof that a renamed chorus is a CE-2 model. Archived repository. | Format/engineering reference only; no stock assembly or firmware redistributed. |
| [repeat98/ZoomMultistompZDL](https://github.com/repeat98/ZoomMultistompZDL/tree/32f3d6877d892409c6defeeeec57040ad004d31f) | Actual new-C DSP compilation/linking for original MS series, own runtime, ELF relocations, descriptor arena, loader safety and ID audit. | Pinned compiler/linker path and existing tested PhaserZeh integration. |
| [Zoom Firmware Editor](https://github.com/Barsik-Barbosik/Zoom-Firmware-Editor) | Extraction/repacking original-MS firmware/effects; a way to obtain compatible originals locally, not an analog modeling algorithm. | Not needed: executable new DSP is feasible. No firmware changed. |
| [Ziddle](https://berbasoft.com/ziddle/) | Public C674x effect emulator. Its emulated host callbacks are not a full MS-70CDR firmware loader or a hardware CPU benchmark. | Pinned `ziddle-1793487371.zip`, SHA256 `c45f11a0ffa51c327169c3c8c6965043882d39b4a8f5f0ac624603e5941579a3`. |

The supported **instruction target** is TI C674x/C6000, little-endian, ELF32 machine 140; Zoom's custom ZFX chip branding is not proof of a particular retail TI chip model. Build uses official **TI C6000 CGT 8.5.0.LTS**, `cl6x -mv6740 --abi=eabi --mem_model:data=far --opt_level=2`. No ARM, ZD2 or generic desktop executable is relabeled as ZDL.

ZDL uses a 76-byte SIZE/INFO wrapper identifying Effect DLL System 1.00 around a relocatable C6000 shared ELF. Sections include code/constants, tiny writable metadata, dynamic exports and relocation records. `Dll_`, `SonicStomp`, control edit handlers, initialization and encoded LCD data are provided by the pinned linker/own runtime. The shared independent structural validator checks lengths, exports, identity, descriptors, relocations and size caps. SHA256SUMS is an artifact integrity hash, **not an invented device checksum**.

The target wrapper processes planar float L[8]/R[8] at 44100 Hz and preserves the runtime shuttle ABI. State lives in guarded `ctx[3]` per-instance descriptor memory, not large `.fardata`/BSS. This DSP needs **8316 bytes**, including two 1024-float rings (audio and clock counts). Ring startup never reads unwritten historical cells, avoiding an initialization clearing burst. Upstream reports a much larger descriptor arena on its test hardware, but actual allocation on this owner's firmware is not independently confirmed; insufficient memory returns dry without writing outside the arena. File/code caps are upstream-tested limits (32126 / 29576 bytes), not claimed silicon-wide specifications. Declared cost 40 is provisional; emulated cycles are not measured DSP utilization.

The candidate ID audit reads only public header/manifest data: [id-audit.json](id-audit.json). `0x060003B4` has no conflict in these pinned sources and differs from PhaserZeh `0x060003B3`. Also reviewed upstream's retired-ID registry; no worldwide reservation or inventory of this pedal is implied.

## CE-2 evidence

Primary schematic inspected visually: [Boss CE-2 circuit scan](https://www.experimentalistsanonymous.com/diy/Schematics/Chorus/BOSS%20CE-2.pdf). The scan identifies the component network; it does not establish that every 1979 unit used identical tolerances or revisions. Local research PDFs are ignored, not redistributed.

Manufacturer reference: [Roland CE-2 technical specifications](https://support.roland.com/hc/en-us/articles/201927549-CE-2-Technical-Specifications). Confirms two controls and mono input/output; gives input/headroom specifications at particular frequencies. These cannot be translated to digital full scale without calibrating Zoom ADC and signal levels.

An original service-note scan was located at a Synfo URL, but retrieval returned 404; it is **not claimed as an inspected source**. The accessible circuit scan, manufacturer specifications and independently derived small-signal models are the working references.

The schematic shows MN3007 1024-stage BBD, MN3101 clock, TL022-based LFO, two emphasis/summing op-amp stages and transistor lowpass networks. A BBD clock does not simply choose an instantaneous digital delay: audio exits after 512 full two-phase clock cycles. The implementation integrates clock counts between input/output times. [Tom Wiltshire's updated BBD study](https://electricdruid.net/weird-wiggles-bbd-clock-modulation/) derives this transit-window method and discusses period modulation. The earlier article is marked superseded by its author; its simple instantaneous-delay treatment is not used as an exact model.

## Refinement 0.20: loading-aware circuit model

The inspected [circuit scan](https://www.experimentalistsanonymous.com/diy/Schematics/Chorus/BOSS%20CE-2.pdf) remains the component reference. These are **ideal small-signal calculations**, not recordings of a 1979 unit. Transistor followers have unity gain/infinite input impedance; bias networks, finite beta, clipping, clock feedthrough and pickup loading remain uncalibrated.

The first version's separate coupling highpasses omitted interactions. Version 0.20 solves the complete passive network around each ideal follower and uses float32 second-order sections to avoid a fragile high-order direct form. `tools/design.py` gives the complete coefficients; tests independently solve nodal impedances.

- Input C2 (0.47uF) is now included in series with `Zin = R4 || (R5 + 1/(s*C3))`, with R4=R6=47k, R5=10k, C3=6.8nF, C4=100pF across R6. Pre-emphasis is `Zf/(1/(s*C2)+Zin)` (positive polarity equivalent; two analog inversions cancel overall). The numerator/denominator are expanded by the generator, checked against the impedance expression in tests.
- Anti-alias and reconstruction networks each include the coupling capacitor (C5/C10=33nF), its shunt R8=100k or R15=330k, the three series 10k resistors and 3.3nF/8.2nF/470pF network **in one four-node solution**. The feedback capacitor terminates at the ideal follower output, not ground. Four-node KCL provides an independent test oracle.
- C14=33nF feeds both R20=1M and R22=47k. The latter ends at the mix op-amp's virtual reference and **loads this coupling capacitor**. The resulting ideal corner is about **107.44 Hz**, versus the incorrectly isolated 4.82 Hz estimate in 0.10. This changes the wet low-frequency response; it is not a new Tone control.
- De-emphasis and the R21/R22/R24 47k equal-weight summing stage remain as before. Both branches pass through the same de-emphasis stage; 0.20/0.30 used common 0.5 normalization for headroom. Owner feedback led 0.40 to restore nominal unity branch gains and use a soft peak guard instead; see GAIN_WARMTH_040.md.

Digital filters use a 44100 Hz bilinear transform without prewarping. The frequency-domain tests explicitly compare with the warped analog model. Real analog bandwidth versus frequency in Hz, emitter loading, buffer response and input/output coupling outside the modeled network still require calibration. We do not silently equate model agreement with hardware agreement.

## RATE and DEPTH correction

The schematic's VR1 changes how much comparator square-wave amplitude reaches the R32/C19 integrator; it is not a variable resistance placed in the oscillator timing denominator. The previous reciprocal knob taper was inappropriate between the endpoints.

Let `x=RATE/100`, `Rt=100k*(1-x)`, `Rb=10k+100k*x`. Including the integrator R32=1M loading, the ideal fraction of square-wave amplitude is:

`A = Rb / (Rt + Rb + Rt*Rb/1M)`.

For the symmetric ideal Schmitt trigger/integrator, `fmax=47k/(4*0.1uF*33k*1M)` and `f=fmax*A`. This yields about **0.321, 1.107, 1.891, 2.699, 3.561 Hz** at RATE 0/25/50/75/100. Tests also solve the loaded wiper voltage independently. It remains an ideal component law, not a measured knob-position calibration. Older saved Rate=50 now runs about three times faster; check and resave presets.

[Anasounds' first-hand oscilloscope study](https://anasounds.com/working-analog-chorus-effect-boss-ce2/) reports a CE-2-circuit LFO around 3.5 Hz at maximum and roughly 0.3 Hz at minimum, and shows Depth altering amplitude while preserving frequency. This supports the order of magnitude and control roles, **not** the whole taper or a traceable original-1979 production-unit calibration. The article's printed unit `300 mhz` is interpreted as 300 millihertz from the low-frequency context, not megahertz. No raw waveform dataset, uncertainty budget or serial-numbered original unit is provided.

DEPTH is applied before the R35/C21 LFO lowpass. The 100k linear pot contributes a position-dependent Thevenin resistance `100k*d*(1-d)`, added to R35=220k before C21=10nF. The RC is therefore 2.2–2.45 ms in this ideal unloaded-buffer model. A lookup interpolates the corresponding sample coefficient; 20 ms digital knob smoothing prevents edit artifacts. No artificial wave modes are introduced.

## Clock/BBD: what can and cannot yet be improved

The DSP integrates 512 full BBD clock cycles with four-point Lagrange interpolation. Version 0.30 replaces the earlier provisional 8.5–10.75 ms nominal range. A more complete indexed first-person repair report and a separate technician's recollection now support a center around 4.65 ms. The resulting full-Depth 3.53–5.77 ms nominal range remains extrapolated. No complete, calibrated original-unit sweep was obtained. [DELAY_REVISION_030.md](DELAY_REVISION_030.md) records sources, conflicting details, calculations and residuals; [clock-observations.json](clock-observations.json) is the reproducible source input.

The linear modulation law deliberately does not fit unsupported nonlinear detail to rough observations. This is evidence-informed approximate tuning, not certification of a factory range. Clone observations and general BBD capabilities remain separate from actual original-unit reports.

The [Panasonic MN3101 datasheet](https://media.digikey.com/pdf/Data%20Sheets/Panasonic%20Semiconductors%20ICs%20PDFs/MN3101.pdf) distinguishes oscillator frequency from the BBD output clock: the output is divided by two. Confusing the two can create a factor-of-two delay error. This is relevant when interpreting published frequency readings; it does **not** mean the current 512-cycle transport should be divided by two again.

`tools/clock_reference.py` provides a separate RC-charge experiment using the schematic's R38=150k, C22=47pF and R36/R37=4.7k. It solves capacitor charge time and accounts for the divider. Supply, inverter switching voltage, transistor/diode drops, control-voltage span and reset time are **named assumptions**, not hidden Boss specifications. [clock-sensitivity.json](clock-sensitivity.json) shows how substantially predictions move when these unknowns change. Tests verify the charging equation, divider and invalid-voltage handling. **These predictions are not shipped as a new delay calibration.** This prevents replacing one uncertain estimate with a more complicated but unverified one.

No calibrated analog saturation/noise model is available: ADC-to-volts mapping, BBD bias/headroom and level-dependent distortion have not been measured. Version 0.40 separately adds an explicitly digital peak guard; it is not presented as an analog nonlinear emulation. [Refinement summary](REFINEMENT_020.md) records practical changes and remaining evidence gaps.

## Owner-driven refinement 0.40

Mono hardware feedback identified level loss from the added 0.5 normalization. Version 0.40 restores nominal branch gain, adds a wet-only shelf and explicit digital peak protection, and removes static knob captions. These are transparent user-driven choices, not newly measured Japanese CE-2 components or a calibrated analog distortion model. [Evidence and tests](GAIN_WARMTH_040.md).
