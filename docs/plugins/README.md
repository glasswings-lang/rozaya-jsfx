# Rozaya JSFX Plugin Suite — Manual

*Designed by Rozaya — Developed with Claude (Anthropic). Public domain (CC0).*

Each plugin has its **own page** here. The plugins install one file at a time
(copy a `.jsfx` from `src/` into your REAPER `Effects` folder), so the docs work
the same way: **grab the plugin you want, read its page, done.** You never have
to wade through docs for plugins you don't have.

Each page is self-contained: it covers that plugin's own controls, including
how shared features like Drift and Speed Ramp behave *for that plugin*. There's
nothing else to open.

---

## Plugins

### Synthesizers

| Plugin | Source file | Page |
|---|---|---|
| Heartbeat Generator | `heartbeat gen.jsfx` | [heartbeat-generator.md](heartbeat-generator.md) |
| Breath Generator | `breath_gen.jsfx` | [breath-generator.md](breath-generator.md) |
| Womb Sound Generator | `womb_sound_generator_v3.jsfx` | [womb.md](womb.md) |
| Polyrhythm Phase | `polyrhythm_phase.jsfx` | [polyrhythm-phase.md](polyrhythm-phase.md) |
| Polyrhythm Phase (Note Names) | `polyrhythm_notes.jsfx` | [polyrhythm-notes.md](polyrhythm-notes.md) |
| Melody Phase | `melody_phase.jsfx` | [melody-phase.md](melody-phase.md) |
| Harmonic Sculptor | `harmonic_sculptor.jsfx` | [harmonic-sculptor.md](harmonic-sculptor.md) |
| Dapple | `dapple.jsfx` | [dapple.md](dapple.md) |

### Effects

| Plugin | Source file | Page |
|---|---|---|
| Resonant Sweeping Filter | `full-feature-sweeping-filter.jsfx` | [sweeping-filter.md](sweeping-filter.md) |
| Sweep Dwell Filter | `sweep-dwell-filter.jsfx` | [sweep-dwell-filter.md](sweep-dwell-filter.md) |
| Full Feature Tremolo | `Full_Feature_Tremolo.jsfx` | [tremolo.md](tremolo.md) |
| Resonance Bank | `resonance_bank.jsfx` | [resonance-bank.md](resonance-bank.md) |
| Stereo Phaser | `stereo-phaser.jsfx` | [stereo-phaser.md](stereo-phaser.md) |
| Bubbler | `bubbler.jsfx` | [bubbler.md](bubbler.md) |
| Veil | `veil.jsfx` | [veil.md](veil.md) |

### Samplers

| Plugin | Source file | Page |
|---|---|---|
| Sustain Looper | `sustain_looper.jsfx` | [sustain-looper.md](sustain-looper.md) |
| Spectral Vowel Morpher | `spectral_vowel_morpher.jsfx` | [spectral-vowel-morpher.md](spectral-vowel-morpher.md) |
| Spectral Vowel Morpher v2 | `spectral_vowel_morpher_v2.jsfx` | [spectral-vowel-morpher-v2.md](spectral-vowel-morpher-v2.md) |

### Utilities

| Plugin | Source file | Page |
|---|---|---|
| Rhythm Track | `rhythm-track.jsfx` | [rhythm-track.md](rhythm-track.md) |
| Shepard Scale Generator | `shepard-scale.jsfx` | [shepard-scale.md](shepard-scale.md) |
| Shepard Tone Generator | `shepard-tone.jsfx` | [shepard-tone.md](shepard-tone.md) |

---

# Acknowledgements

## Authorship

All plugins in this suite were designed by Rozaya. Code was written by Claude (Anthropic) under Rozaya's direction. Rozaya determined the concept, feature set, signal architecture, parameter design, and all creative and functional decisions for each plugin. Claude implemented those decisions in JSFX.

## Inspirations and Prior Art

Several plugins in this suite were developed with reference to existing implementations in common DAW tools. In all cases, the code was written independently — no source code was copied or derived from any external implementation. The conceptual influence is acknowledged here:

- **Rhythm Track** — rhythmic metronome generation concepts drawn from existing DAW metronome implementations.
- **Resonant Sweeping Filter** and **Sweep Dwell Filter** — filter sweep concepts informed by resonant lowpass filter implementations found in standard DAW effect libraries.
- **Full Feature Tremolo** — tremolo concepts informed by existing DAW tremolo implementations, substantially expanded with shaped envelopes, stereo phase control, and pan modulation.

The **Heartbeat Generator**, **Womb Sound Generator**, **Breath Generator**, **Polyrhythm Phase**, **Shepard Tone Generator**, and **Shepard Scale Generator** plugins are original concepts with no direct external inspiration for their architecture or feature sets.

## Technical Notes

The Cockos state-variable resonant lowpass filter topology used in several plugins is a well-known open implementation documented in the REAPER JSFX ecosystem. Its use here follows standard practice for the platform.
