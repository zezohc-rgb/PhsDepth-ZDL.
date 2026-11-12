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

The target wrapper processes planar float L[8]/R[8] at 44100 Hz and preserves the runtime shuttle ABI. State lives in guarded `ctx[3]` per-instance descriptor memory, not large `.fardata`/BSS. This DSP needs **8300 bytes**, including two 1024-float rings (audio and clock counts). Ring startup never reads unwritten historical cells, avoiding an initialization clearing burst. Upstream reports a much larger descriptor arena on its test hardware, but actual allocation on this owner's firmware is not independently confirmed; insufficient memory returns dry without writing outside the arena. File/code caps are upstream-tested limits (32126 / 29576 bytes), not claimed silicon-wide specifications. Declared cost 40 is provisional; emulated cycles are not measured DSP utilization.

The candidate ID audit reads only public header/manifest data: [id-audit.json](id-audit.json). `0x060003B4` has no conflict in these pinned sources and differs from PhaserZeh `0x060003B3`. Also reviewed upstream's retired-ID registry; no worldwide reservation or inventory of this pedal is implied.

## CE-2 evidence

Primary schematic inspected visually: [Boss CE-2 circuit scan](https://www.experimentalistsanonymous.com/diy/Schematics/Chorus/BOSS%20CE-2.pdf). The scan identifies the component network; it does not establish that every 1979 unit used identical tolerances or revisions. Local research PDFs are ignored, not redistributed.

Manufacturer reference: [Roland CE-2 technical specifications](https://support.roland.com/hc/en-us/articles/201927549-CE-2-Technical-Specifications). Confirms two controls and mono input/output; gives input/headroom specifications at particular frequencies. These cannot be translated to digital full scale without calibrating Zoom ADC and signal levels.

An original service-note scan was located at a Synfo URL, but retrieval returned 404; it is **not claimed as an inspected source**. The accessible circuit scan, manufacturer specifications and independently derived small-signal models are the working references.

The schematic shows MN3007 1024-stage BBD, MN3101 clock, TL022-based LFO, two emphasis/summing op-amp stages and transistor lowpass networks. A BBD clock does not simply choose an instantaneous digital delay: audio exits after 512 full two-phase clock cycles. The implementation integrates clock counts between input/output times. [Tom Wiltshire's updated BBD study](https://electricdruid.net/weird-wiggles-bbd-clock-modulation/) derives this transit-window method and discusses period modulation. The earlier article is marked superseded by its author; its simple instantaneous-delay treatment is not used as an exact model.

## Component calculations (idealized)

The following values were read from the circuit scan, not invented:

- Pre-emphasis R4/R6 47k, R5 10k, C3 6.8nF, C4 100pF. Positive-polarity equivalent transfer: `(1+s*57000*6.8n)/( (1+s*10000*6.8n)*(1+s*47000*100p) )`. Two analog inversions cancel through the complete effect.
- De-emphasis/summing R21/R22/R24 47k, R23 10k, C15 6.8nF, C16 100pF. Transfer for each branch: `(1+s*10000*6.8n)/(1+s*(57000*6.8n+47000*100p)+s²*10000*47000*6.8n*100p)`. Dry is taken **after pre-emphasis**, and de-emphasis acts on the summed branches. We do not put a generic lowpass across the entire dry signal.
- Each pre/post BBD lowpass: three series 10k resistors, C6/C11 3.3nF to reference, C7/C12 8.2nF from middle node to follower output, C8/C13 470pF at the follower input. Assuming unity follower and negligible loading, nodal equations give `1/[1+s*R*(C6+3*C8)+s²*2*R²*C8*(C6+C7)+s³*R³*C6*C7*C8]`. Tests solve the three-node equations separately from this polynomial.
- Coupling highpasses modeled as isolated RC: 100k/33nF (48.2 Hz), 330k/33nF (14.6 Hz), 1M/33nF (4.82 Hz). Real impedances interact; treating them independently is an approximation.
- LFO output RC 220k and 10nF gives approximately 72.34 Hz smoothing. Triangle control is supported by the oscillator topology. 20 ms knob smoothing is a digital artifact-prevention choice, not a CE-2 component.

`tools/design.py` applies the bilinear transform at 44100 Hz and rounds coefficients to float32. No prewarping: tests compare with the corresponding warped analog response, not an unwarped claim of identical 6–7kHz behavior. The ideal follower ignores finite transistor gain, loading, tolerances and bias. Input/output buffers and all coupling capacitors are not fully modeled.

## Provisional modulation and gain

- RATE: ideal maximum `47000/(4*.1uF*33000*1M) = 3.5606 Hz`. A 100k rate pot / 10k fixed-divider approximation sets the range to 0.3237–3.5606 Hz, using a 101-point interpolated lookup. **This is a modeled knob law, not a measured full knob sweep**, and must be calibrated against an actual unit.
- DEPTH: linear control of nominal delay excursion about 9.625 ms, full span 8.5–10.75 ms. This tentative span appears in a [first-person CE-2 circuit-analysis comment](https://electricdruid.net/investigations-into-what-a-bbd-chorus-unit-really-does/#comments), not a calibrated factory specification or a 1979 pedal measurement. It is used as a starting estimate only. The general MN3007 datasheet delay capability is not substituted for a measured CE-2 sweep.
- The clock model maps this nominal period-modulation approximation to clock frequency, then integrates actual transport. It omits the detailed Q4/Q5/MN3101 voltage-to-period nonlinearity and chip charge dynamics. No synthetic stereo or modulation mode is added.
- R21/R22 equality supports equal dry/wet **relative** weights. A shared 0.5 scaling supplies digital headroom and changes absolute output gain versus the analog summer; this is deliberate and disclosed.
- No arbitrary soft clipping or noise was added. Analog distortion depends on input volts, bias and frequency; absent measurements, adding a generic waveshaper would assert detail not supported by the evidence. This release models clean small-signal behavior only.

## What fidelity is not established

No measured CE-2 impulse/transfer recordings, clock/LFO traces, level-calibrated reamp or ABX comparison were available. Tests establish agreement with the **documented idealized model**, artifact bounds and executable DSP behavior. They do not establish perceptual equivalence, original component tolerances, exact analog distortion or physical MS-70CDR compatibility.
