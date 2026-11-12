# 0.20 refinement: evidence and consequences

The goal was to replace identifiable circuit simplifications with reproducible calculations, while looking for actual CE-2 measurements. This improves the model's basis; no audible superiority or exact vintage-pedal match is claimed without listening/measurement.

## Actual implementation changes

1. Corrected RATE from a reciprocal taper to the loaded square-wave divider feeding the integrator. At 50 the ideal model now gives 1.89 Hz, rather than 0.59 Hz. Published oscilloscope work supports roughly 0.3–3.5 Hz endpoints, but does not supply a full original-unit taper dataset.
2. Included the Depth pot's Thevenin resistance in LFO filtering, and placed depth amplitude before that RC. Frequency and depth remain independent controls.
3. Included input C2 and solved the C5/C10 coupling/lowpass interactions. New filters are generated as stable second-order sections.
4. Corrected wet C14's load: R22 to the op-amp virtual reference acts in parallel with R20. Approximate ideal wet highpass corner changes from 4.82 to 107.44 Hz. Absolute output gain is still normalized with a shared 0.5 factor, rather than calibrated in analog volts.
5. Added a separately testable clock-charge sensitivity model. It documents the MN3101 oscillator/output divide-by-two and uncertainty in switching/discharge voltages; its uncalibrated predictions are not substituted into the release.

## Evidence that remains missing

A calibrated, known-original CE-2 delay sweep across Rate/Depth positions, recorded transfer functions and distortion versus input level were not found. Retrieved clone observations, incomplete forum excerpts, generic chorus delay ranges and circuit simulations do not establish these. The service-note Synfo URL still returned 404; a mirror's extracted text is not treated as a verified full schematic inspection. The previously inspected schematic scan remains the component source.

The 8.5–10.75 ms span remains provisional. No distortion/noise model was invented to fill the measurement gap. Future improvements should prioritize a traceable original-unit clock trace and level-matched audio; the user does not need to purchase a Boss pedal for the software work to continue.

## Presets and delivery

The effect keeps gid 6/fxid 948, `CE2Soul.ZDL`, two knobs and its artwork. Update the existing custom effect and review RATE presets. PhaserZeh and all factory effects remain unchanged. The prior 0.10 artifact remains available in commit `1f986513e0848f8f6a0d71808142eaf4a47d493f` for comparison; never install both versions under the same ID.

Research/equations: [RESEARCH.md](RESEARCH.md). Reproducible source: `tools/design.py`, `tools/clock_reference.py` and tests. Structural checks and emulator results are in `build/`; neither confirms real pedal boot, CPU scheduling or physical audio behavior.
