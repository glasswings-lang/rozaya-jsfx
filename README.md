# Rozaya JSFX Plugin Suite

A collection of audio synthesis and effect plugins for [REAPER](https://www.reaper.fm/), designed by Rozaya.

## Plugins

**Synthesizers**
- `Heartbeat Generator` — stereo binaural heartbeat simulator with S1/S2 sounds
- `Breath Generator` — synthesized breathing with inhale/exhale cycles
- `Womb Sound Generator` — multi-layered intrauterine soundscape (heartbeat, breath, bloodflow)
- `Binaural Polyrhythm Oscillator` — up to 8 voices with tremolo and pan modulation

**Effects**
- `Resonant Lowpass Filter with Shaped LFO Sweep` — resonant lowpass with shaped LFO sweep
- `Resonant Sweeping Filter with Shaped LFO and Pan Modes` — advanced sweep filter with stereo phase and pan modes
- `Resonant Filter with Segmented LFO and Pan Modes` — four-segment LFO-driven lowpass filter
- `Tremolo with Shaped Envelope, Stereo Phase, and Pan Modulation` — amplitude modulation with shaped envelope and pan system

**Utilities**
- `Rhythm Track` — synthesized metronome with swing and pan distribution
- `Risset Rhythm Generator` — auditory illusion of perpetual rhythmic acceleration
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
