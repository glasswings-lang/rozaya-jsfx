# Rozaya JSFX Plugin Suite

A collection of audio synthesis and effect plugins for [REAPER](https://www.reaper.fm/), designed by Rozaya.

They were built for ambient, sleep and entrainment listening — long, slow,
gentle sound you can leave running. Nothing here is a playable instrument in the
keyboard sense; they are sources and shapers you set going and then live with.

## Plugins

Twenty-one plugins. Each installs on its own and has its own page, so you only
ever read about the one you took.

### Synthesizers — they make sound from nothing

| Plugin | What it is |
|---|---|
| **[Heartbeat Generator](docs/plugins/heartbeat-generator.md)**<br>`heartbeat gen.jsfx` | A synthesized heartbeat. Two resonant voices, a "near" and a "far", give it depth; the rate wanders the way a real one does rather than looping mechanically. |
| **[Breath Generator](docs/plugins/breath-generator.md)**<br>`breath_gen.jsfx` | A breathing cycle — inhale, pause, exhale, pause — with the length, tone and envelope of each phase set separately. |
| **[Womb Sound Generator](docs/plugins/womb.md)**<br>`womb_sound_generator_v3.jsfx` | Heartbeat, breath and bloodflow together as one body, heard from inside. Any of seven things can be set drifting slowly, and it sighs on its own every so often. |
| **[Polyrhythm Phase](docs/plugins/polyrhythm-phase.md)**<br>`polyrhythm_phase.jsfx` | Up to eight tuned voices at once, each pulsing at its own rate so the pattern between them never quite repeats. Each voice is a stereo pair slightly detuned against itself — the binaural beat. |
| **[Polyrhythm Phase v3](docs/plugins/polyrhythm-phase-v3.md)**<br>`polyrhythm_phase_v3.jsfx` | The same engine, but voices are picked **by note name** instead of by counting semitones from a root. This is where new work happens; see *Two Polyrhythms* below. |
| **[Melody Phase](docs/plugins/melody-phase.md)**<br>`melody_phase.jsfx` | The sequencer sibling. The same eight voices, but they play one after another instead of together — each holding for its own length before handing over. Notes are picked by name, with glide and legato. |
| **[Harmonic Sculptor](docs/plugins/harmonic-sculptor.md)**<br>`harmonic_sculptor.jsfx` | Builds a sound from 64 sine harmonics, each set by ear. The suite's tool for *designing source material* — sculpt a timbre, render it, loop it. |
| **[Dapple](docs/plugins/dapple.md)**<br>`dapple.jsfx` | Scattered droplets that pop on irregular timing and chirp upward as they fade. Somewhere between rain on glass and a pointillist wash. It started as an attempt at water and became its own thing. |

### Samplers — they work from sound you give them

| Plugin | What it is |
|---|---|
| **[Sustain Looper](docs/plugins/sustain-looper.md)**<br>`sustain_looper.jsfx` | Turns a piece of a WAV into an endless pad. The crossfade is the point: loop points don't have to be matched by eye, you set the region roughly and raise the crossfade until the seam disappears. |
| **[Spectral Vowel Morpher](docs/plugins/spectral-vowel-morpher.md)**<br>`spectral_vowel_morpher.jsfx` | Play audio into it, catch moments you like, and it resynthesizes them — as a recognizable voice, an evolving wash, or any blend — morphing between them. Captures are saved with the project. |
| **[Spectral Vowel Passage](docs/plugins/spectral-vowel-passage.md)**<br>`spectral_vowel_passage.jsfx` | The same engine arranged as a *passage* instead of a morph: every captured moment carries its own timing and its own character, and the plugin walks through them. |

### Effects — they change sound coming in

| Plugin | What it is |
|---|---|
| **[Resonant Sweeping Filter](docs/plugins/sweeping-filter.md)**<br>`full-feature-sweeping-filter.jsfx` | A resonant lowpass whose sweep is a shaped envelope rather than a plain sine, with stereo phase and pan modes. Movement is its subject. |
| **[Sweep Dwell Filter](docs/plugins/sweep-dwell-filter.md)**<br>`sweep-dwell-filter.jsfx` | The same idea told in time instead of rate: hold high, fall, hold low, rise. You set the four durations and the cycle length follows from them. |
| **[Full Feature Tremolo](docs/plugins/tremolo.md)**<br>`Full_Feature_Tremolo.jsfx` | Amplitude modulation with a shaped, gated envelope rather than a sine, plus a pan block that can move with the tremolo or against it. |
| **[Resonance Bank](docs/plugins/resonance-bank.md)**<br>`resonance_bank.jsfx` | Sixteen bands, each of which can drift on several of its own parameters at once and at different speeds. A few bands wandering independently is an evolving windscape. |
| **[Stereo Phaser](docs/plugins/stereo-phaser.md)**<br>`stereo-phaser.jsfx` | A swept-allpass phaser, 2 to 64 stages. Low, it's a normal musical phaser; high, it's a dense curtain of notches for sound design. |
| **[Veil](docs/plugins/veil.md)**<br>`veil.jsfx` | Muffles a **mono** voice the way the womb does — a steep lowpass near 500 Hz, speech from behind a heavy curtain. Its two channels are filtered independently, so it manufactures stereo width from a mono source and the width itself breathes. |
| **[Bubbler](docs/plugins/bubbler.md)**<br>`bubbler.jsfx` | Scatters your input into rising pitched droplets *made of your own sound*. For **tonal** sources — pads, drones, voices. Pitch it down for underwater. Dapple is its sibling for noise. |

### Utilities

| Plugin | What it is |
|---|---|
| **[Rhythm Track](docs/plugins/rhythm-track.md)**<br>`rhythm-track.jsfx` | A metronome with swing and stereo pan distribution — a strong beat on the downbeat, weak beats elsewhere, both shapeable. |
| **[Shepard Scale Generator](docs/plugins/shepard-scale.md)**<br>`shepard-scale.jsfx` | The Shepard scale illusion as a step sequencer: every note sounds higher than the last, and after twelve steps you are back where you began. |
| **[Shepard Tone Generator](docs/plugins/shepard-tone.md)**<br>`shepard-tone.jsfx` | The same illusion made continuous — the Shepard-Risset glissando, sliding forever without arriving. Up to eight voices, each rooted on its own pitch class. |

### Two Polyrhythms, and which to use

Both are current and both are shipped. **Polyrhythm Phase v3 is where new work
happens**; v1 gets only what keeps it working. The difference that matters when
choosing is how a voice is pitched — v1 counts semitones from a root note, v3
picks a note by name. Existing v1 projects are untouched and safe; a migration
across is planned but not written, so **v1 stays until it exists.**

Womb v1 and v2, and Melody Phase v2, are no longer shipped. They are frozen in
[`archive/versions/`](archive/versions/) with their manuals, so an old project
that needs one can still open it.

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
