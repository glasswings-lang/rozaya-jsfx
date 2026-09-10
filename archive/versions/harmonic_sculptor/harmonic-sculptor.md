# Harmonic Sculptor

**Designed by Rozaya — Developed with Claude (Anthropic)**

---

## Overview

Harmonic Sculptor is an additive synthesizer. It builds its sound from up to 64 individual sine harmonics of a single fundamental and lets you set the level of each one by ear. Pick a base wave and the plugin analyses it into its 64 harmonics and loads those as your starting point ("stamp this wave, then sculpt"); from there you push and pull individual harmonics to shape the timbre.

It is the suite's primary tool for *designing source material*. Sculpt a timbre — including vowel-like tones, by emphasising the harmonics that fall near a vowel's formants — then render it to a WAV and feed it to the Sustain Looper for an endlessly sustained pad (see "The render-and-loop pipeline" in the Sustain Looper section).

The output is band-limited by construction — any harmonic above half the sample rate is simply not played — so it never aliases, even at high fundamentals.

---

## Signal Architecture

### Additive engine

Each of the 64 harmonics is a pure sine oscillator at an integer multiple of the Fundamental (harmonic 1 = the fundamental, harmonic 2 = one octave up, and so on). Each harmonic has its own target level (what you set) and a smoothed current level (what is actually playing), so level changes and base-wave reloads never click.

### Base-wave analysis

Choosing a Base Wave renders one cycle of that wave and measures the magnitude of each of its 64 harmonics (a single-bin DFT per harmonic), loading those magnitudes as the starting recipe. The twelve base waves match the suite's other oscillator plugins' waveform set, so a sculpted Saw starts from the same harmonic content as a Saw elsewhere in the suite. Re-choosing a base wave reloads its recipe, discarding manual edits.

### Constant-loudness normalization

With Normalize on (default), the plugin scales the whole spectrum so the playing set of harmonics hits a fixed target loudness, recomputed as you sculpt. Pulling a harmonic out raises the gain to compensate, so the overall level stays roughly constant and only the *character* changes, not the volume. Boost is capped at +12 dB so a near-silent spectrum cannot blast.

### Stereo

Left and right play the same harmonics at the same levels but with decorrelated per-harmonic phases. Phase does not affect the timbre of a steady tone, so this produces genuine diffuse stereo width rather than a lateralized offset, and the decorrelation is bounded so it stays mono-compatible (no harmonic cancels in a mono sum).

---

## Parameters

### Base wave

**Base Wave (load recipe)** `Sine / Triangle / Saw / Golden TS / Golden SG / Golden GS / Bell / Wavefold / Half-sine / Phi-cascade / Phi Triangle / Phi Sine / Square / Pulse, default Saw`
Choosing one analyses it into the 64 harmonics and loads them as your starting point. Re-choosing reloads the recipe and discards manual edits — "stamp this wave, then sculpt." Waveform definitions match the suite's other oscillator plugins.

### Harmonic editor (two-slider selector)

**Harmonic Select** `H1 … H64`
Picks WHICH harmonic you are editing. Each value names the musical interval that harmonic lands on above the fundamental (e.g. "H5 +maj3rd (flat)") rather than a bare number — many upper harmonics drift away from equal temperament, and that drift is where a wave's character lives. Moving Harmonic Select snaps the Harmonic Level slider to show the selected harmonic's current level.

**Harmonic Level dB (of selected)** `-60 to +12, default 0`
Sets the level of the currently-selected harmonic; -60 dB is off. Move Harmonic Select, then adjust Harmonic Level and it writes back into that harmonic.

> **Screen-reader note:** the Level slider always reads as "Harmonic Level" — it does NOT announce which harmonic number you are on (JSFX cannot relabel a slider live). Keep track of the Harmonic Select value; that is the one you are editing.

### Global

**Fundamental Hz** `20 to 2000, default 110`
Pitch of harmonic 1. Every harmonic is an integer multiple of this.

**Master Gain dB** `-60 to 0, default -12`
Final output level, applied on top of normalization.

**Normalize loudness** `Off / On, default On`
Keeps overall loudness roughly constant as you sculpt (see Signal Architecture). Off plays the raw, un-leveled sum — educational, but it can get loud when many harmonics stack (Master Gain still applies as a safety).

**Attack (sec)** `0 to 10, default 0.5`
Time for harmonics to fade up to their levels (e.g. on transport start). 0 = instant.

**Release (sec)** `0 to 10, default 1.5`
Time for harmonics to fade down when their level is lowered or they pass above the Nyquist ceiling.

**Output mode** `Mono / Stereo, default Stereo`
Mono sends one channel to both outputs (identical L/R). Stereo gives diffuse width via decorrelated per-harmonic phase (see Signal Architecture). Mono is handy when you want a centred source, or when rendering material that the Sustain Looper's ensemble will widen anyway.

**Pulse width % (Pulse wave only)** `5 to 95, default 25`
Duty cycle of the Pulse base wave — 50% is a square, narrower is thinner and more nasal. Changing it re-stamps the Pulse recipe (like re-choosing a base wave, so it discards manual harmonic edits). Hidden, and without effect, unless the Base Wave is Pulse.

---

## Usage Notes

- **It is a sound-design tool, not a played instrument.** There is no MIDI input — it generates one sustained tone at the Fundamental. The intended use is: design a timbre, render it, loop it.
- **Make vowels by ear.** At a fixed Fundamental, boost the harmonics that land near a vowel's formant regions until the tone reads as "aah", "ooh", and so on. Because formants sit at fixed frequencies, which harmonics you boost depends on the Fundamental — so sculpt the vowel at the pitch you intend to use it.
- **The render-and-loop pipeline.** Sculpt → render to a WAV in the samples folder → load into Sustain Looper → sustain forever, optionally with ensemble. This is the suite's route to sustained vocal/choir pads. Rendering also freezes the CPU cost: you pay for the additive engine once, then looper playback is cheap.
- **Band-limited and clean.** Harmonics above half the sample rate are dropped, so sculpted saws/squares never alias and are cleaner than phase-generated ones, even at high fundamentals.
- **Stereo is switchable** via Output mode — Stereo gives built-in diffuse width (decorrelated per-harmonic phase), Mono collapses to a centred single channel. You do not need a chorus after it for width in Stereo, though you can still add one for movement.

---

*Harmonic Sculptor is part of the Rozaya JSFX plugin suite.*
*Designed by Rozaya — Developed with Claude (Anthropic)*


---

