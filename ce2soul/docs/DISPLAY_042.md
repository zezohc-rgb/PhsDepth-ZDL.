# 0.42: live knob clearance

The owner supplied a photograph showing ring/marker clutter at the two knob locations. The likely cause is firmware-rendered live knobs overlaid on the static circles and scale marks. Prior removal of text alone did not address this overlap.

Remove all static circles, pointers and scale marks in the top knob panels; retain the CHECK light, enclosure and lower lettering/pad. Preserve parameter positions `(2,42,9)` and `(3,73,9)`, names RATE/DEPTH and the empty third slot. Firmware is expected to draw the live controls in the cleared area. This interpretation still needs a new hardware photograph to confirm.

The decoded executable bitmap is checked pixel-for-pixel and both reserved rectangles (x36–61 and x67–91, y7–26) must be blank. The generated PNG shows only static art; the firmware controls are not present in that preview. No fabricated full-screen hardware preview is supplied.

Audio source, coefficients, controls, state and identity remain unchanged from 0.41. All 18 deterministic host gain fixture results are exactly equal. Native tests, sanitizers, structural checks, a byte-identical rebuild and C674x emulator checks are repeated for the new packaging. The resulting ZDL has different linked constant addresses and is not expected to have byte-identical executable sections to 0.41.
