# Rozaya JSFX Plugin Suite

A collection of audio synthesis and effect plugins for [REAPER](https://www.reaper.fm/), designed by Rozaya.

## Plugins

**Synthesizers**
- `Heartbeat Generator` — stereo binaural heartbeat simulator with S1/S2 sounds
- `Breath Generator` — synthesized breathing with inhale/exhale cycles
- `Womb Sound Generator` (v1) — multi-layered intrauterine soundscape (heartbeat, breath, bloodflow); original architecture, kept available for projects built on it
- `Womb Sound Generator v2` — Womb variant with intrauterine-perspective tuning (muffled lowpass, amplitude-modulated bloodflow, continuous floors) and an independent HRV/drift architecture; recommended for new projects
- `Polyrhythm Phase` — up to 8 binaural-pitched voices with polyrhythmic tremolo and pan modulation, per-voice semitones and phase offsets, Direction & Reverse modes (single-layer or 16-voice Both), Play/Rest gating per voice, Speed Ramp, musical and slow drift
- `Polyrhythm Phase (Note Names)` — same engine as Polyrhythm Phase, but each voice picks its note **by name** (C2–C6) with a separate fine-tune in cents, instead of counting semitone offsets from a base note. No music theory and no arithmetic; a separate plugin, so existing Polyrhythm projects are untouched
- `Melody Phase` — step-sequencer sibling to Polyrhythm Phase. 8 voices play in sequence rather than in parallel; configurable Next-voice-in / Note duration per voice for overlapping or rest-between phrasing, with glide / portamento and legato modes
- `Dapple` — scattered-droplet texture generator: random pitched plinks that chirp upward, over a resonant noise fizz, blendable from gurgle to plink (32-voice polyphonic)

- `Spectral Vowel Morpher` — capture-based instrument: grab moments of live audio into slots and resynthesize them as a recognizable voice, an evolving wash, or any blend, morphing between the captured moments
- `Spectral Vowel Morpher v2` — the Morpher with two changes: short Wash grain settings work (the synthesis FFT is sized to the grain), and every setting that describes a capture — Texture, Pitch, Spread, Stereo width, Low cut, Denoise, Voice level, plus how long the morph lingers on it — belongs to the slot rather than being one global setting flattening them all
- `Harmonic Sculptor` — additive resynthesis over a 64-harmonic selector, each harmonic level-adjustable, for building or carving a spectrum by hand
- `Sustain Looper` — loads a sample and builds a clean crossfaded sustain loop, with an ensemble layer

**Effects**
- `Resonant Sweeping Filter with Shaped LFO and Pan Modes` — resonant lowpass sweep with LFO start phase, stereo phase control, and pan modes
- `Sweep Dwell Filter` — lowpass sweep driven by independent hold and transition times, with stereo phase and pan modes
- `Tremolo with Shaped Envelope, Stereo Phase, and Pan Modulation` — amplitude modulation with shaped envelope and pan system
- `Resonance Bank` — 16-band parallel-bandpass or serial-peaking-EQ effect with per-band multi-target drift modulation and cascade rolloff. Vowel-flavored breath shaping, dynamic windscapes, evolving noise textures
- `Stereo Phaser` — swept-allpass phaser with stereo spread and feedback; 2–64 stages (classic phaser through dense sound-design "curtain")
- `Veil` — soft spectral haze
- `Bubbler` — granular "bubble" effect: scatters a tonal input into rising pitched droplets made of your own sound (pitch down for underwater). Sibling to Dapple, for tonal sources

**Utilities**
- `Rhythm Track` — synthesized metronome with swing and pan distribution
- `Shepard Scale Generator` — infinite ascending/descending pitch illusion, step sequencer
- `Shepard Tone Generator` — continuous Shepard-Risset glissando

## Documentation

Full parameter reference and usage notes — **one page per plugin**, so you can
read just the plugin you installed: [docs/plugins/](docs/plugins/README.md)

## Tools

Small helper scripts that live alongside the suite — they do the jobs a plugin
structurally can't. Full usage and flags: **[tools/README.md](tools/README.md)**

- **`rate_calc.py`** — works out the base rate for a second plugin instance so a
  chosen voice lands exactly where you want it relative to the first. Prints the
  answer *and the working*. (One instance can't see another, so this can't be a
  control.)
- **`loop_finder.py`** — finds loop-ready material in a recording and writes
  clean looping WAVs, so loop points don't have to be hunted by eye.


```
python tools/rate_calc.py --help
```

Every tool is stdlib-only unless its entry says otherwise, and every one prints
its full flag list with `--help`.

## Installation

1. Copy the `.jsfx` files from `src/` into your REAPER `Effects` folder (or a subfolder of it).
2. In REAPER, add an FX to a track and search for the plugin by name.

The default REAPER Effects folder locations are:
- **Windows:** `%APPDATA%\REAPER\Effects`
- **macOS:** `~/Library/Application Support/REAPER/Effects`
- **Linux:** `~/.config/REAPER/Effects`

## License

[CC0 1.0 Universal](LICENSE) — public domain dedication. No rights reserved.
