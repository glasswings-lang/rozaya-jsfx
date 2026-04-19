# Rozaya JSFX Plugin Suite

A collection of audio synthesis and effect plugins for [REAPER](https://www.reaper.fm/), designed by Rozaya.

## Plugins

**Synthesizers**
- `Heartbeat Generator` — stereo binaural heartbeat simulator with S1/S2 sounds
- `Breath Generator` — synthesized breathing with inhale/exhale cycles
- `Womb Sound Generator` — multi-layered intrauterine soundscape (heartbeat, breath, bloodflow)
- `Binaural Polyrhythm Oscillator` — up to 8 voices with tremolo and pan modulation

**Effects**
- `Resonant Sweeping Filter with Shaped LFO and Pan Modes` — resonant lowpass sweep with LFO start phase, stereo phase control, and pan modes
- `Sweep Dwell Filter` — lowpass sweep driven by independent hold and transition times, with stereo phase and pan modes
- `Tremolo with Shaped Envelope, Stereo Phase, and Pan Modulation` — amplitude modulation with shaped envelope and pan system

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
