# Compatibility and hardware test procedure

Target is **original blue MS-70CDR**, reported firmware **2.10**. ZDL, not ZD2; not MS-70CDR+. CE-2 Soul 0.43 is a real C674x executable built for the known original-MS ABI. Structural and emulator checks do **not** confirm firmware-loader, real-time or physical audio behavior. The owner reports successful use of 0.40 and a close subjective comparison to Brainworx Blue Chorus, with slightly less bass. Version 0.43 still requires physical verification; this is not a calibrated CE-2 comparison.

Version 0.20 changes the middle of the Rate curve and wet bass filtering. RATE=50 is now approximately 1.89 Hz, compared with 0.59 Hz in 0.10. Review saved presets. Identity, two controls and artwork are unchanged; update the same custom effect, never install two conflicting IDs.

Version 0.21 changes only the cover and numeric overlay positions. The DSP matches 0.20. A rendered preview is supplied; legibility and overlays on the real Zoom LCD still need physical testing.

Version 0.30 revises the delay model from partial published clock observations: center approximately 4.65 ms, nominal full-Depth span 3.53–5.77 ms (extrapolated). Review saved Depth settings. This remains approximate tuning, not a complete calibration; see [DELAY_REVISION_030.md](DELAY_REVISION_030.md).

Version 0.40 restores nominal direct/wet gain, adds wet-only warmth and a soft output guard, and removes the static captions under the knobs. See [GAIN_WARMTH_040.md](GAIN_WARMTH_040.md). Review levels at moderate monitoring volume when updating from the quieter 0.30.

## Limits

- Version 0.43 physical installation/boot, display overlays, audio, repeated activation and patch recall remain pending.
- DSP instruction target is C674x; no claim is made about the exact commercial DSP part inside Zoom's custom chip.
- 8316 bytes of per-instance descriptor state, with ring priming rather than global arrays. Arena bounds are checked; insufficient memory produces dry passthrough. Hardware allocation and simultaneous instances still need testing.
- CPU cost descriptor is provisionally 40.0. Emulator cycles are reported only as emulator counts; actual scheduling margin in a six-effect chain is unknown.
- RATE minimum/maximum and taper, DEPTH sweep and BBD voltage/clock response remain approximations. This is not a verified CE-2 clone.
- Only L/Mono input is used when enabled. The same mono output appears at L and R; R-only input is silent, and a stereo effect before it loses its right input. Use it before stereo processing. Bypass preserves incoming L/R unchanged.
- Nominal equal branch gains are one; a wet-only shelf changes the delayed high-frequency response. A digital soft knee above 0.78 full scale bounds output peaks at 0.98 and can compress hot signals. Normalized full scale is not mapped to CE-2 input volts; analog distortion/noise is uncalibrated.
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

Version 0.41 adds a +1 dB low-frequency wet shelf (180 Hz pole), folded into the existing two-state voicing filter. No additional memory or controls. See [BASS_041.md](BASS_041.md).

Version 0.42 reserves blank bitmap panels for live firmware knobs, removing overlapping fixed rings and ticks. Hardware appearance still needs verification. Audio matches 0.41.

The owner supplied a 0.42 Zoom recording from the same clean take as the plugin, at RATE/DEPTH 50. Version 0.43 retains that cover and opens the wet high shelf; physical testing of this revision is pending. See [RECORDINGS_043.md](RECORDINGS_043.md).
