# DmTrem 0.30: host tap-tempo integration

Implemented against the ZDL service ABI documented in the pinned Ziddle source archive, SHA-256 `c45f11a0ffa51c327169c3c8c6965043882d39b4a8f5f0ac624603e5941579a3`:
https://berbasoft.com/ziddle/ziddle-1793487371.zip

Relevant source files inside that archive:

- `ziddle/runtime/effect-runtime/host-abi.txt`: ZDL audio gets CTX; edit/init entries get STATE. TempoPhase is STATE[23]; TempoCentiMs is STATE[24].
- `ziddle/runtime/effect-runtime/src/abi/profiles.rs`: ZDL STATE[24] is modeled as TempoCentiMs, with a note-division witness test named as evidence.
- `ziddle/runtime/effect-runtime/src/abi/tempo.rs`: quarter note is NOTE_HEAD[6].
- `ziddle/runtime/effect-runtime/src/tempo.rs`: units and integer truncation.

This is more specific than the older upstream TEMPO-SYNC notes, which mix uncertain callback targets and a secondary-table hypothesis. This implementation does not use their fixed-address probes or search firmware RAM.

## Implementation

A custom `Tap_edit` handler captures the host-provided STATE[24] function pointer into unused parameter word 16. It reads user knob 9 (eighth user parameter) through STATE[31] and commits its ordinary UI/100 value through STATE[7]. Initialization materializes the handler before audio.

With Tap=Host, the audio callback queries the captured service every eight-frame block with `(quarter_note=6, ceiling_ms=8000)`. The returned integer is in 1/100 milliseconds. Base frequency is `100000 / returned_value`, using a locally inlined reciprocal. Diamond Mode and DBL subdivisions then apply to this base rate. No guessed slot index, hard-coded firmware address or global memory scan is involved.

Tap=Free uses the Speed knob. The default is Host. Speed is ignored while Host is selected. A candidate 40 ms rate settling filter avoids abrupt changes; the original Diamond transition law is not measured. An absent service or implausible returned duration retains the free-speed fallback; the physical pedal must confirm that the service is supplied as expected.

## What was and was not tested

The real TI-compiled binary is run in the C674x emulator. Tests capture the function pointer through the actual handler, change host tempo after initialization without running any edit callback, and compare audio against a native adapter with independent integer quarter-period calculation. An additional output-edge oracle checks quarter-note Chop periods at 60, 120 and 180 BPM within two samples.

The emulator's tempo service is a model: its success does not establish that the MS-70CDR 2.10 service table, firmware scheduling or tap UI behaves identically. Physical host tap testing is pending. No Diamond-specific tap weighting, two-second tap-series timeout or speed-knob hysteresis is implemented; this integration inherits Zoom's global tempo entry behavior.

## Using the original blue MS-70CDR

1. Keep DmTrem's Tap control at Host.
2. In the Zoom SETTINGS menu choose HOLD FOR TUNER/TAP and select TAP TEMPO.
3. Hold the footswitch for one second to open Tap Tempo, tap at least twice, then hold for one second to leave.
4. Start with Mode=Qtr, DBL=Off. Test slow and fast tapping first; Wave=Chop and Depth=50 make the period easy to hear.
5. Select Tap=Free to use Speed directly.

These footswitch steps follow the original MS-70CDR manual, pages 16 and 18:
https://zoomcorp.com/documents/87/MS-70CDR_operationManual_English.pdf

The first hardware observation needed is whether Qtr follows two distinct global tempos without touching any effect knob. Do not interpret the printed TAP/DBL artwork as a second physical switch on the Zoom.
