# Software references — 2026-11-12

No explicitly documented Diamond TRM-1 software emulation was verified in the searches performed. Queries covered Diamond Tremolo with plugin, VST, emulation, software and model, and mentions of Helix, Fractal and Headrush. This does not prove no such product exists.

## Inspectable optical model: Guitarix Tremolo

Primary source inspected:
https://github.com/brummer10/guitarix/blob/master/trunk/src/LV2/faust/tremolo.dsp
Blob SHA: 93aa03471edf7ea1fb56c38c72fc64db00d71222

The source credits a vactrol tremolo model to transmogrify and references transmogrifox. It applies nonlinear control shaping, a stateful low-pass response, resistance mapping and a resistor-divider gain calculation. Its control-dependent time constant spans 60 ms to 5 ms. The file specifies R1=2700, Ra=1e6 and Rb=300, with sine or triangle drive.

These are Guitarix model constants, NOT measured Diamond constants. The inspected file does not implement the TRM-1's Sharkfin, separate Chop path, accents, chaos or switch behavior. Useful as an inspectable modeling approach, not a sonic ground truth. No code has been copied into this repository; check applicable licensing before reuse.

## Configurable comparison: Soundtoys Tremolator

Manufacturer reference:
https://www.soundtoys.com/product/tremolator/

Soundtoys identifies Fender Vibrolux and Wurlitzer as hardware references and provides waveform/rhythm editing and rhythmic chopping. The inspected product page does not establish Diamond TRM-1 modeling. This is a possible comparison tool for generic modulation behaviors, not evidence of Diamond transfer curves. No binary was installed or tested.

## Engineering decision

Retain the original Diamond manual as the authority on functionality. Use inspectable optical models to evaluate candidate DSP structures. Do not import another effect's constants or call a generic optical plugin an exact Diamond emulation. Keep uncertain parameters explicit until supported by TRM-1-specific evidence.
