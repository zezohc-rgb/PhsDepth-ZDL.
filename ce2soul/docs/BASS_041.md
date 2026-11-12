# 0.41: subtle wet bass adjustment

The owner physically tested 0.40 on the Zoom, liked the chorus and described the tone as very close to Brainworx Blue Chorus, with slightly less bass. This is subjective feedback: no recorded, gain-matched plugin capture or physical Boss CE-2 measurement was supplied.

0.41 multiplies the existing wet voicing transfer by `(s + G*w)/(s + w)`, where `G = 10^(1/20)` and `w = 2*pi*180`. Thus the change is +1 dB at DC, about +0.84 dB at 80 Hz, +0.53 dB at 180 Hz and below +0.04 dB at 1 kHz. These are gains of the added shelf alone, not the total chorus. Existing wet AC coupling still rejects DC. The bilinear transform is applied at 44.1 kHz and the product fits one second-order section with the same two states. Direct-path filters, delay, LFO, nominal branch gains, output protection, art and two controls are unchanged.

This is an intentionally conservative listening adjustment, not a measured correction or a claim of a Brainworx/Boss circuit component. Chorus cancellation can make the total audible difference depend on Rate, Depth and note frequency.

## Reverting and comparing

The exact known-good 0.40 remains in commit `cb22d78ee0d6235f6cbe4c9e2c76dda8a214b653`:
[download 0.40](https://github.com/zezohc-rgb/PhsDepth-ZDL./raw/cb22d78ee0d6235f6cbe4c9e2c76dda8a214b653/ce2soul/build/CE2Soul.ZDL).
SHA256: `ee0dcd5c01ec787db4d560bcb35c99633a0c228a8ca3496d729344b80143283b`.

Replace the same custom CE2Soul effect when comparing versions; do not install duplicate effect IDs or replace factory effects. Use the same mono routing, Rate/Depth and playing level. Listen for bass body, low-note clarity and unwanted hot-input compression. Only the owner can confirm the desired subjective balance on the Zoom.

## Offline verification

`tools/test.sh` checks stability, memory/parameter limits, independent circuit response, guard, mono wrapper and 18 gain fixtures, with sanitizers. `tests/test_volume.py` independently isolates the added shelf against the exact mathematical 0.40 voicing and verifies its frequency-localized boost and unchanged direct attack. Binary, emulator and gain evidence for the new version are in `build/`; see [VALIDATION.md](VALIDATION.md). These tests do not establish measured plugin equivalence or physical verification of 0.41.
