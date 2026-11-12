# Volume verification and factory-preset correction — 0.31

The 0.30 default (Shark, Depth 50, Vol 50, Qtr) attenuated the measured L/Mono RMS by about 1.99 dB at 100 BPM. Depth 0 with Vol 50 has unity gain. The lost average energy is from modulation, not a hidden extra mixer attenuation or mono summing.

Version 0.31 changes the factory Vol from 50 to 63. This adds about 2.007 dB to the selected preset. The DSP gain law, waveform and depth behavior remain unchanged; no compressor, limiter, automatic makeup or input-dependent gain was added.

At 120 BPM:

| Input witness | Vol 50 | Vol 63 |
|---|---:|---:|
| Constant gain probe | −1.930 dB | +0.078 dB |
| 440 Hz sine | −1.930 dB | +0.078 dB |
| Harmonic signal with exponential note envelope | −1.871 dB | +0.136 dB |

At 100 BPM the constant probe changed from −1.986 dB to +0.022 dB. Across the tested default-preset cases at 60, 100, 120 and 180 BPM, corrected RMS stayed within ±0.25 dB. This tolerance describes these witnesses, not all musical playing or settings.

## Scope and limits

`tools/volume_audit.py` compiles and exercises the exact native Zoom adapter. It measures after two seconds settling, for ten seconds per case, and records input/output peaks and RMS. Signals include a constant probe, a sine and a note-like three-harmonic signal. Measurements use L/Mono only, consistent with this mono effect; summing two channels could produce an unrelated stereo-comparison difference.

The emulator also checks the real TI binary's factory descriptor default, restored Vol 63 and RMS output against bypass, independently of the native parity vectors. The tests do not constitute a physical ADC/DAC or perceived-loudness measurement.

Tremolo intentionally makes instantaneous volume fall and rise. Matching average energy cannot preserve the dry peak at the same time: the added 2.007 dB raises peaks by a factor of 1.26. A hot source can need lower Vol elsewhere in a chain. No claim of universal clipping-free headroom is made.

Vol 63 is NOT a universal setting. For example, Chop / Depth 50 / Qtr at 120 BPM has about −3.01 dB RMS at Vol 50; Vol 71 gives about +0.035 dB. Extremely short Chop duty cycles still lower average energy substantially even with Vol 100. Wave, depth, mode, rate and the timing of played notes can require manual volume adjustment.

## Existing patches

Installing the new binary does not rewrite saved patches. If a saved patch still has Vol 50, set Vol to 63 for the initial Shark / Depth 50 / Qtr preset and save it. New effect instances use the corrected factory default.

This follows the reference pedal's independent volume-control approach rather than adding a new auto-gain behavior. No physical Diamond unit was measured. Full measurements and artifact SHA-256 are in `build/volume-report.json`.
