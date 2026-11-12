# TRM-1 community research — 2026-11-12

Search scope: original Diamond Tremolo / TRM1 / TRM-1 with schematic, clone, traced, VTL5C, and targeted searches for FreeStompboxes, DIYStompboxes, PedalPCB and Madbean. No verified complete TRM-1 schematic or clone build document was located in these results. This is a bounded search result, not proof none exists. Do not substitute Diamond Compressor clone schematics.

## First-hand owner report

The Tremolo Project, May 4, 2018:
https://tremolo-project.blogspot.com/2018/05/diamond-trm1-tremolo.html

The author reports a slowest period of 1520 ms and fastest of approximately 86 ms. Reciprocals are approximately 0.658 Hz and 11.63 Hz. The page does not establish mode, DBL state, measurement procedure or error bounds for those endpoints. Treat them as provisional observations of that unit, not guaranteed base-rate knob specifications. Do not extrapolate other mode limits from them without identifying the test conditions.

## Repair lead

https://www.reddit.com/r/diypedals/comments/whxihc/diamond_tremolo_repair_help/

An owner posts an internal-photo album, https://imgur.com/a/Ijr4Lae . A commenter identifies U4 as an LED/photoresistor optocoupler. The owner says its marking is difficult to read. No complete schematic or confirmed optocoupler part number was established from the thread. The linked album has not been visually verified in this research; do not infer component values from this note.

## Consequences for implementation

A recovered analog schematic could constrain gain stages and the optical transfer model. It would not alone establish the original microcontroller's waveform tables, tap weighting, chaos generator or ramp law. Those need firmware documentation, measurements, or explicitly identified approximations. Owner demos can supply additional observations if settings and audio processing are known; uncalibrated demos cannot establish exact transfer curves.

Proceed with documented behavior and expose uncertain optical/timing constants for later calibration. Keep provisional numerical assumptions separate from manufacturer specifications. This note adds evidence; it does not claim a working tremolo or ZDL build.
