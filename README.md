# PhsDepth — custom phaser for Zoom MS-70CDR (original)

**Goal:** Create a new installable `PhsDepth.ZDL` phaser without replacing the factory phaser.

## Requested controls
- **Rate:** sweep speed
- **Color:** 4-stage / 8-stage, normal / inverted (four modes)
- **Level:** output gain
- **Depth:** width of the all-pass frequency sweep, not wet/dry mix

## Current state
The `src/` folder contains a **portable C DSP reference implementation**. It is **not a pedal-ready effect**. No working `.ZDL` has been generated or verified. The algorithm uses cascaded first-order all-pass filters, a sine LFO, and fixed 50/50 dry/wet blending.

Next: integrate the DSP with the Zoom runtime/parameter ABI; package effect metadata and unique ID; compile for the pedal DSP; test CPU usage and audio on the original MS-70CDR.

Reference tooling: [ZoomMultistompZDL](https://github.com/repeat98/ZoomMultistompZDL).

**Safety:** Back up pedal patches and effects before installing experimental effects. Never rename a C file to `.ZDL` and install it.

## DmTrem development

The original Diamond TRM-1-inspired tremolo now has an experimental TI-built ZDL, native tests and C674x emulator validation. See [tremolo/README.md](tremolo/README.md) for controls, downloads and the [fidelity limits](tremolo/docs/FIDELITY.md). Host tap-tempo integration and TRM-1-inspired artwork are included in version 0.31. Physical Zoom testing and calibration against a real Diamond remain pending.
