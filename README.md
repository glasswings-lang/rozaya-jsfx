# Rozaya JSFX Plugin Suite

A collection of audio synthesis and effect plugins for [REAPER](https://www.reaper.fm/), designed by Rozaya.

## Plugins

**Synthesizers**
- `Heartbeat Generator` — stereo binaural heartbeat simulator with S1/S2 sounds
- `Breath Generator` — synthesized breathing with inhale/exhale cycles
- `Womb Sound Generator` (v1) — multi-layered intrauterine soundscape (heartbeat, breath, bloodflow); original architecture, kept available for projects built on it
- `Womb Sound Generator v2` — Womb variant with intrauterine-perspective tuning (muffled lowpass, amplitude-modulated bloodflow, continuous floors) and an independent HRV/drift architecture; recommended for new projects
- `Polyrhythm Phase` — up to 8 binaural-pitched voices with polyrhythmic tremolo and pan modulation, per-voice semitones and phase offsets, Direction & Reverse modes (single-layer or 16-voice Both), Play/Rest gating per voice, Speed Ramp, musical and slow drift
- `Melody Phase` — step-sequencer sibling to Polyrhythm Phase. 8 voices play in sequence rather than in parallel; configurable Next-voice-in / Note duration per voice for overlapping or rest-between phrasing, with glide / portamento and legato modes

**Effects**
- `Resonant Sweeping Filter with Shaped LFO and Pan Modes` — resonant lowpass sweep with LFO start phase, stereo phase control, and pan modes
- `Sweep Dwell Filter` — lowpass sweep driven by independent hold and transition times, with stereo phase and pan modes
- `Tremolo with Shaped Envelope, Stereo Phase, and Pan Modulation` — amplitude modulation with shaped envelope and pan system
- `Resonance Bank` — 16-band parallel-bandpass or serial-peaking-EQ effect with per-band multi-target drift modulation and cascade rolloff. Vowel-flavored breath shaping, dynamic windscapes, evolving noise textures

**Utilities**
- `Rhythm Track` — synthesized metronome with swing and pan distribution
- `Shepard Scale Generator` — infinite ascending/descending pitch illusion, step sequencer
- `Shepard Tone Generator` — continuous Shepard-Risset glissando

## Documentation

Full parameter reference and usage notes: [docs/rozaya_jsfx_manual.md](docs/rozaya_jsfx_manual.md)

## Installation

1. Copy the `.jsfx` files from `src/` into your REAPER `Effects` folder (or a subfolder of it).
2. In REAPER, add an FX to a track and search for the plugin by name.

The default REAPER Effects folder locations are:
- **Windows:** `%APPDATA%\REAPER\Effects`
- **macOS:** `~/Library/Application Support/REAPER/Effects`
- **Linux:** `~/.config/REAPER/Effects`

## License

[CC0 1.0 Universal](LICENSE) — public domain dedication. No rights reserved.
