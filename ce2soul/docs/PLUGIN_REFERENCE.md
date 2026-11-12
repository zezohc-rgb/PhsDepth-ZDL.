# Official BOSS CE-2 software reference

Research date: 2026-11-12. The official [BOSS Effects Pedals product page](https://www.roland.com/us/products/rc_boss_effects_pedals/) lists **CE-2 Chorus** in its expanded model library. This is the Roland/Boss product, distinct from third-party CE-2-inspired plugins or UAD's CE-1-derived Brigade Chorus.

## What the public information establishes

Roland describes a mono CE-2 model, with extended plugin-level input/output controls and tempo-sync features. Those extensions must not be confused with the original two-knob pedal. The public [PX-1 CE-2 parameter page](https://static.roland.com/manuals/px-1/en-US/306473995381637515.html) gives RATE/DEPTH 0–100 for that hardware ecosystem, not Hz or a calibrated delay law for the software plugin. It is corroborating interface information, not a plugin measurement.

The official software specifications list Windows/macOS, VST3/AU/AAX, 44.1 kHz support and online authentication. [Installation instructions](https://support.roland.com/hc/en-us/articles/38172727842075-BOSS-Effects-Pedals-How-do-I-download-install-and-start-BOSS-Effects-Pedals) require Roland Cloud Manager and account sign-in. The product page advertises Ultimate membership, a trial and a function-limited demo. Public text does not establish whether every CE-2 function is available in that demo.

This task's execution environment is Linux; no authorized Roland Cloud session or installed BOSS plugin was available. The plugin was **not installed, run, measured, copied or embedded**. No account/trial was created. No audio parameters in CE-2 Soul 0.21 were changed based on screenshots, marketing claims or imagined plugin output. Version 0.21 changes the cover only; the compiled DSP object matches 0.20 byte for byte.

## Useful next comparison

With an authorized working copy in a supported host, the plugin could provide repeatable **software-reference** captures without borrowing a physical CE-2. It would remain a comparison with Boss's contemporary algorithm, not proof of equality to all original 1979 units. Record the plugin version, host, settings, sample rate, input/output gain, tempo-sync state and any trial limitations. Verify that the intended measurement/use is permitted by the applicable software terms before sharing results.

An original-signal generator is provided:

```sh
python3 ce2soul/tools/make_reference_probes.py --output ce2soul/work/reference-probes
```

It makes mono float32 WAVs at 44100 Hz, with a manifest and hashes. No vendor audio is included:

- `impulses.wav`: 32 seconds, two-second silent lead, impulses every 50 ms, trailing silence. Useful for tracking wet-delay movement separately from the direct impulse.
- `noise.wav`: deterministic low-level, bandlimited noise with silent lead/tail. Useful for transfer/correlation comparisons; preserve its original level.
- `sweep.wav`: logarithmic 20 Hz–15 kHz sweep with lead/tail, for static DEPTH=0 checks. A modulated effect is time-varying: do not interpret an ordinary sweep at nonzero Depth as a fixed transfer function.

Use only the CE-2 model in the signal chain, disable tempo sync, and start with neutral plugin input/output gain. Export a bypass baseline and outputs at RATE 0/25/50/75/100 with DEPTH 0/50/100. Use lossless WAV at 44100 Hz without normalization, added effects or MP3/video compression. Preserve channels, latency and silence; mark clips with settings. Confirm mono operation rather than silently collapsing stereo output.

No capture results exist yet. The generator's successful run only verifies the test WAVs, not the plugin or a CE-2 sound match. Source signals can also support an eventual physical-pedal measurement with separately calibrated reamp/ADC levels.

## Screen appearance

The public [Roland CE-2 pedal image](https://static.roland.com/products/rc_boss_effects_pedals/images/new/ce-2-pedal.jpg) was visually inspected as a layout reference. The ZDL contains a new procedural 128×64 one-bit drawing, not that photograph. Two top knobs, center indicator, Chorus/CE-2 lettering and a rectangular lower pad evoke the original. The pad reads SOUL to identify this independent implementation. The monochrome Zoom LCD cannot reproduce the blue enclosure color.

The photo is not redistributed in the repository. Actual dynamic numeric overlays and firmware rendering still need inspection on the original blue MS-70CDR.
