# DmTrem 0.30 — original Diamond TRM-1-inspired ZDL

Experimental build for original blue Zoom MS-70CDR, firmware 2.10.
Real TI C674x binary and portable reference DSP. Tap follows the host tempo through a STATE service, validated in emulation; physical MS-70CDR tap behavior and measured Diamond equivalence remain unverified. See [fidelity matrix](docs/FIDELITY.md) for the exact scope.

## Files and controls

`build/DmTrem.ZDL` is the actual effect, with checksum and build/validation/emulator reports alongside it. It is not renamed source code. Existing phaser and CE-2 projects are preserved.

| Control | Meaning |
|---|---|
| Speed | Base rate in Tap=Free; provisional range/taper |
| Depth | Modulation depth; in Chop, on/off ratio with 50% at center |
| Vol | Independent output gain; 50 = unity before modulation |
| Wave | Shark, Sine, Squar (optical Square), Chop |
| Mode | Qtr, 8th, Trip, Rhyth, Chaos, Man |
| DBL | Doubled rate/alternate accent or rhythmic pattern; gradual rate change |
| Hold | In Manual: optical modulation active while On; Chop mutes while On |
| Tap | Host (default): Zoom global tap tempo; Free: Speed knob |

The original pedal is mono: enabled DmTrem uses L/Mono and sends identical output to L/R. Bypass preserves the incoming channels. Hold is a parameter adaptation, not access to a physical momentary switch. [Tap tempo setup and test instructions](docs/TAP_TEMPO.md) use Zoom's global tempo entry; Diamond-specific tap averaging is not reproduced. DBL freezing is supported in the portable API through `ramp_hold`, but not exposed by the eight-control adapter.

## Evidence versus approximation

Documented rhythm ratios, Chop behavior and Manual behavior guide the implementation. Sonic constants, Sharkfin curve, gain/speed tapers, accent strengths and Chaos law remain provisional. The optical stage is gain smoothing rather than a measured LED/LDR circuit model. Abrupt parameter changes and hard Chop can click. No exact-clone claim is made.

## Reproduce

```sh
sh tremolo/tools/test.sh
sh tremolo/tools/build.sh --output-dir work/rebuilt
cmp tremolo/build/DmTrem.ZDL tremolo/work/rebuilt/DmTrem.ZDL
python3 tremolo/render_demo.py
```

The build bootstrap downloads official TI 8.5.0 with a pinned SHA-256 and upstream linker commit `32f3d6877d892409c6defeeeec57040ad004d31f`. Alternatively:

```sh
python3 tremolo/zoom/build.py --upstream /path/to/ZoomMultistompZDL --ti-root /path/to/ti-cgt-c6000_8.5.0.LTS
```

The native tests cover duty cycle, rhythmic pulse counts, manual gating, independent sine/frequency oracles, DBL ramp/freeze, block continuity and finite output. The emulator executes the real C674x instructions and compares audio with the exact adapter compiled natively; it also exercises saved parameters, all edit callbacks, selector strings and bypass. It does not simulate the real firmware loader, converter sound, physical CPU scheduling or the Diamond circuit.

Emulator: unpack the SHA-pinned Ziddle source specified in `build/emulator-report.json`, put Rust/cargo on PATH and run:

```sh
python3 tremolo/tools/emulator/run.py --ziddle /path/to/ziddle-1793487371
```

The renderer produces ignored WAV files under `dist/` from synthetic plucked harmonics. They are previews of this algorithm, not Diamond captures.

## Identity and remaining device checks

MOD group 6, ID 949, checked against public collections and existing PhaserZeh 947 / CE2Soul 948; evidence is in `docs/id-audit.json`. This is a bounded check, not a worldwide reservation or a scan of the user's pedal.

Before use on the MS-70CDR: back up patches/effects, check for that identity in the installed inventory, and test loading/reloading, all controls, mono routing, bypass, multiple instances and CPU load. Declared DSP cost 40 is provisional, not measured hardware usage. No installation was performed from this environment.

Runtime/TI notices are included under `licenses/`.

## Appearance

The embedded 128x64 monochrome image uses a horizontal enclosure, four top knobs, central toggle, a faceted diamond motif and two illustrated footswitches inspired by the original TRM-1. `build/DmTrem.png` is a dark-green external thumbnail; `build/DmTrem-LCD.png` previews the actual monochrome design. The MS-70CDR LCD cannot display the green enclosure color. These are original procedural drawings, not copied vendor image assets.

## Manual em português

[Baixar manual em PDF — DmTrem 0.30](build/DmTrem-0.30-Manual-PT.pdf). Seis páginas com instalação, controles, tap tempo, regulagens e solução de problemas. Para gerar novamente: `python3 tremolo/tools/manual_pdf.py` (ReportLab e fontes Liberation Sans).
