# Fast track to first pedal test

Goal: test a new custom phaser on the **original** MS-70CDR, without replacing a factory effect.

## Critical findings from upstream
- The upstream custom-effect workflow starts with a pass-through (`audio_nop: true`) using the final parameter descriptor, then adds DSP incrementally.
- Its safe-DSP guide forbids desktop math calls such as `sinf`, `tanf` and `powf` in pedal code. **Our current `src/phsdepth_dsp.c` uses these and must NOT be copied directly into a pedal build.**
- Use a unique effect ID and a filename basename no longer than 8 characters; for a first candidate use `PhsDepth.ZDL` (8 characters before the extension).
- Preserve the context shuttle `ctx[11]`/`ctx[12]` required by upstream.
- Check generated file size and declared DSP cost before installation.

## Fastest safe milestones
1. Select a small upstream effect as a template and determine its build dependencies.
2. Create an initial four-parameter pass-through ZDL and validate its packaging.
3. Implement the phaser using a lightweight LFO and low-rate all-pass coefficient updates; avoid runtime math-library dependencies.
4. Run build checks, back up pedal patches and effects, then test on hardware.

This is a plan, **not a compiled or verified ZDL**.
References:
- https://github.com/repeat98/ZoomMultistompZDL
- https://github.com/repeat98/ZoomMultistompZDL/blob/main/docs/SAFE-DSP-RULES.md
