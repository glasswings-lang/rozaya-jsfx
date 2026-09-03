# Bubbler

**Designed by Rozaya — Developed with Claude (Anthropic)**

---

## Overview

Bubbles whatever you feed it. Bubbler is an **effect** — it takes your input and scatters it into rising pitched droplets *made of your own sound*. Each bubble grabs a short grain of the incoming audio, throws it to a random transposition, and chirps it upward as it fades — the collapsing-bubble rise, but built from your material instead of synthesized noise.

**Bubbler is for *tonal* sources** — pads, drones, voices, sustained tones, anything with a clear pitch to transpose. For bubbling *noise / broadband* material, or generating bubble texture from nothing, use its sibling **[Dapple](dapple.md)** (a generator) instead. Feeding noise into Bubbler or a tonal source into Dapple gets janky results — they're tuned for opposite material.

Pitch a clean tone **down** (negative Transpose) and it turns deeply, wonderfully underwater.

## Signal Architecture

- **Input history.** The last ~300 ms of input is kept in a per-channel circular buffer.
- **Random events.** A timer fires bubbles at the set rate, with adjustable timing irregularity. Each event captures the current grain and picks a random transposition.
- **Granular resample with rising pitch.** Each voice replays its captured grain at a playback rate = the random transposition, climbing over the bubble's life by the Rise amount — so the grain's pitch sweeps upward.
- **Seamless-loop playback.** Each voice loops its grain with a **two-tap triangular crossfade**, so a bubble sustains the full Bubble-length envelope and completes its full rise at *any* pitch — it never runs out of grain material. Linear interpolation on the reads.
- **Polyphonic — 16 voices per channel.** Overlapping bubbles each ring on their own voice; a new bubble takes the quietest voice.
- **Stereo** from two independent event streams. **Soft-clip** on the wet output bounds it to ±1 (can't spike into REAPER's auto-mute). **Dry/Wet** blends against the original.

## Parameters

**Bubble rate** `0.001–1000, default 6` — what this means depends on Rate Mode.

- In **Own rate**, it is average events per second.
- In **Host x**, it is **beats per bubble**. Set 4 and you get one bubble every four beats; 0.5 gives two per beat. It follows the project tempo.

Fractions are free — *every 3.7 beats* is as reachable as *every 4*.

**Rate Mode** `Own rate / Host x` — whether the bubbles run on their own clock or follow the project tempo. Bubble rate carries the mode's unit.

**Host ratio** — *retired 2026-09-02.* It spared you arithmetic when Host x made Bubble rate a multiplier; in beats, *every 4 beats* is typing 4. Hidden and inert; it stays in the parameter list only because slider IDs can never be renumbered.

**Timing randomness %** `0–100, default 70` — spacing irregularity. High = naturally scattered.

**Transpose (semitones)** `-36 to +36, default +12` — base pitch shift for each grain. Positive = up (bright droplets); **negative = down (deep, underwater)**. −24 to −36 on a sustained tone is the submerged sound.

**Pitch spread (semitones)** `0–24, default 7` — random pitch variation per bubble. 0 = all land on the same transposition; up = shimmering variety.

**Rise (semitones)** `0–36, default 12` — how far each bubble's pitch climbs over its life. This is the chirp. 0 = no rise (steady-pitch grains).

**Bubble length (ms)** `5–1000, default 150` — how long each bubble sounds (amplitude envelope); the full rise completes over this time. Long = swelling droplets; short = rapid plips.

**Stereo width %** `0–100, default 80` — 0 = mono, 100 = fully independent L/R streams.

**Dry/Wet %** `0–100, default 100` — blend of bubbled signal against the untouched original.

**Output (dB)** `-24 to +12, default 0` — wet level trim.

## Usage Notes

- **Feed it tonal material** — pads, drones, sustained vocals, single tones. That's what it's built for (see the Dapple note above).
- **Underwater:** a clean sustained tone + deep negative Transpose (−24 to −36) + a longer Bubble length + a little Pitch spread = submerged, swelling depth.
- **Rain / droplets:** positive Transpose, moderate Rise, higher rate, high Pitch spread.
- **Bubble length caps at 1 s** for long swelling droplets; short values give rapid plips. The rise always completes over whatever length you set, at any pitch.
- **It's an effect, not a generator** — it needs input. Dry/Wet at 100% is pure bubbles; pull it back to layer bubbles over the dry source.

---

*Bubbler is part of the Rozaya JSFX plugin suite.*
*Designed by Rozaya — Developed with Claude (Anthropic).*
