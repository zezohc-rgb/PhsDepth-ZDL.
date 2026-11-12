# 0.43: recording-informed wet clarity

The owner supplied clean, Brainworx Blue Chorus and Zoom files, confirmed the same clean take was replayed and RATE/DEPTH were 50/50. The Zoom version was the latest then supplied, 0.42. All files are 44.1 kHz PCM, stereo with identical L/R samples (mono duplicated). Raw audio is not committed or redistributed. Analysis is specific to this guitar passage and recording chain; it is not a physical Boss CE-2 measurement.

## Recorded comparison

After matching total RMS, the supplied Zoom has about 1.93 dB more energy at 80–160 Hz than the plugin; the plugin has about 0.56 dB more at 160–315 Hz, 1.51 dB more at 315–630 Hz, and 0.44–0.77 dB more across the three bands 630–5000 Hz. These are integrated Welch band energies, not an LTI transfer response. Below 80 Hz there is little input energy. Zoom total RMS is about 0.26 dB above the plugin for the compared interval.

A fixed-lag waveform match of the Zoom to clean is weak; the smoothed energy envelope matches much better (about 0.966 correlation at approximately 0.22 s offset). The plugin aligns well to the clean input. The same-take confirmation rules out separate playing, but does not identify the remaining contributions of capture clocks, signal chain, effect delay and LFO phase. No correction of clock drift or recovered instantaneous plugin delay is claimed.

## Candidate experiment and decision

Render the provided clean take through the native DSP at 50/50, varying only the existing wet voicing. Integrate six Welch bands (80–160, 160–315, 315–630, 630–1250, 1250–2500, 2500–5000 Hz), relative to total RMS, and compare with the plugin. The full native model is used: direct/wet phase cancellation matters. Reducing the bass shelf did not improve the aggregate metric, so retain +1 dB bass. LFO phase is not aligned and the recording chain is not modeled. This is a candidate screen, not a prediction of calibrated hardware equality.

Selected 0.43 changes only wet high-frequency asymptotic gain from −4 to −2.5 dB, keeping the 2 kHz analog pole. For this render, absolute 2500–5000 Hz band error falls from about 0.177 dB to 0.019 dB; 1250–2500 Hz error falls from 0.425 to 0.286 dB. However, six-band RMS error barely changes (1.010 to 1.006 dB) and the 315–630 Hz deficit slightly increases. Do not characterize this as a broad spectral match. The remaining low/mid discrepancy requires more investigation, especially modulation and cancellation, rather than an aggressive EQ fit to one passage.

Direct filters, delay law, Rate/Depth, mono routing, output guard, state size, identity and cleared cover stay unchanged. No new controls. The change is original voicing inspired by the supplied recordings, not extracted plugin code or proprietary data.

## Reproduce

With private recordings available locally:

```sh
python3 ce2soul/tools/compare_voicing.py --clean /path/limpo.wav --reference /path/brainworx.wav --output-dir ce2soul/work/recording-comparison
```

Requires the test dependencies and a native C compiler. Supports signed PCM WAV at 44.1 kHz, converts stereo to mono, and compares the clean-length prefix of the plugin file (supplied plugin starts aligned). Results, input hashes and explicit caveats: [recording-voicing-043.json](recording-voicing-043.json). No FFT-bin curve is blindly applied to the effect.

Offline validation is in [VALIDATION.md](VALIDATION.md). 0.43 still needs a new physical recording at 50/50 using the same clean take, same input/output gains and routing. Compare at matched listening level. Keep [0.42](https://github.com/zezohc-rgb/PhsDepth-ZDL./raw/bc54c58e5aaeb354ea6394d44e1888716d134b13/ce2soul/build/CE2Soul.ZDL) for A/B; replace the same custom effect rather than installing duplicate IDs.
