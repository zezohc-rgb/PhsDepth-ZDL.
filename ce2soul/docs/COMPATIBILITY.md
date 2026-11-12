# Compatibility and hardware test procedure

Target is **original blue MS-70CDR**, reported firmware **2.10**. ZDL, not ZD2; not MS-70CDR+. CE-2 Soul 0.20 is a real C674x executable built for the known original-MS ABI. Structural and emulator checks do **not** confirm firmware-loader, real-time or physical audio behavior. The owner's successful PhaserZeh test validates that earlier effect, not this new chorus.

Version 0.20 changes the middle of the Rate curve and wet bass filtering. RATE=50 is now approximately 1.89 Hz, compared with 0.59 Hz in 0.10. Review saved presets. Identity, two controls and artwork are unchanged; update the same custom effect, never install two conflicting IDs.

## Limits

- Physical installation/boot, displayed two knobs, edit callback initialization, repeated activation and patch recall are pending.
- DSP instruction target is C674x; no claim is made about the exact commercial DSP part inside Zoom's custom chip.
- 8308 bytes of per-instance descriptor state, with ring priming rather than global arrays. Arena bounds are checked; insufficient memory produces dry passthrough. Hardware allocation and simultaneous instances still need testing.
- CPU cost descriptor is provisionally 40.0. Emulator cycles are reported only as emulator counts; actual scheduling margin in a six-effect chain is unknown.
- RATE minimum/maximum and taper, DEPTH sweep and BBD voltage/clock response remain approximations. This is not a verified CE-2 clone.
- Only L/Mono input is used when enabled. The same mono output appears at L and R; R-only input is silent, and a stereo effect before it loses its right input. Use it before stereo processing. Bypass preserves incoming L/R unchanged.
- Fixed equal branch weights with common 0.5 normalization. No output hard limiter: filter ringing can exceed input peaks. Start with moderate signal level; normalized full scale is not mapped to CE-2 input volts. Analog overdrive/noise is intentionally uncalibrated.
- Wet startup delay: about 23.2 ms prime plus 5.8 ms fade. Bypass pauses the internal clock/history; re-engagement can briefly include old wet history. Silent initialization and control changes are tested offline; bypass switching must be auditioned physically.
- No global ID reservation exists. Public audit is time-limited and cannot inspect a disconnected pedal's inventory.

## Installation — manual only

1. Back up patches and the existing setup using the same trusted original-MS tool/workflow already used for PhaserZeh.
2. Verify `build/SHA256SUMS` and confirm the installer reads name `CE-2 Soul`, gid 6 / fxid 948 (`0x060003B4`). Check no installed effect already uses this pair. PhaserZeh uses a different ID and must remain intact.
3. Add `CE2Soul.ZDL` as a new custom effect in an available slot. **Keep all original effects.** If there is no free space, stop rather than replacing/removing a factory effect. This project provides no automatic flashing/updater command.
4. Test initially in a simple patch with one CE-2 Soul, L/Mono input and moderate output level. Observe boot, knob UI, default recall, parameter edits and on/off.
5. Try RATE 0/50/100 and DEPTH 0/50/100 on sustained chords. Depth 0 should have static delay coloration, not a mix change. Output should be identical on L/R; no intentional stereo spread.
6. Save/recall a patch, power-cycle, then test multiple instances and typical effect chains for dropouts/DSP limits. Record firmware and binary SHA with results.

No firmware, factory effect, hardware setting or USB MIDI state was modified during development. Do not regard the existence of a `.ZDL` or a passing emulator as a physical compatibility certificate.

## Fidelity validation still needed

Use a known original CE-2, calibrated reamp and the same dry recording. Capture dry/effect impulses or sweeps, single tones, transient guitar and chords at documented knob positions and levels. Measure wet delay extrema, LFO period and shape, wet/dry ratio, frequency response and distortion versus input level. Account for polarity, ADC/DAC latency and level before listening comparisons. Avoid confusing CE-2W/CE-1 modes or the CE-2B bass revision with the 1979 reference. These measurements can then replace the provisional constants and knob law.
