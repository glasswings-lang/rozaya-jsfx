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

- In **Hz**, it is average events per second. In **BPM** it is events per minute, and in **Seconds** it is the average gap between events.
- In **Host x**, it is **beats per bubble**. Set 4 and you get one bubble every four beats; 0.5 gives two per beat. It follows the project tempo.

Fractions are free — *every 3.7 beats* is as reachable as *every 4*.

**Rate Mode** `BPM / Seconds / Hz / Host x` (**default Hz**) — the suite's canonical four, in the suite's canonical order, as of 2026-09-05 (R20). Bubble rate carries the mode's unit. In **Host x** it means every N beats, so a bubble every four beats is `4`; bigger is slower.

This used to be `Own rate / Host x`, where "Own rate" meant per second. It defaults to Hz rather than the suite's usual BPM because every saved instance relies on that default meaning per second — five in `the-sound-of-a-drain` had it stored explicitly and were migrated; the five in the two `birdsong` projects store nothing and take the default.

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

## The 2026-09-05 layout change

Every control moved into the suite's canonical reading order: what the plugin
**is**, then its **rate**, then the **shape of its movement**, then **stereo**,
then **output**, then **transport**, then **drift**, then **ramp**. **Rate mode came home to slider 2**, nine places from the rate it defines, and the retired **Host ratio** picker was deleted rather than left hidden.

**Bubble length is read when a bubble is born**, so drifting or ramping it changes new bubbles rather than ones already sounding — the effect arrives over about one bubble.

**Your saved projects were migrated** — 10 instances across birdsong, birdsong-2 and the-sound-of-a-drain. Verified by
decoding every stored value against the control NAME it belongs to, before and
after, rather than against the table the migration used.

## Transport

**Added 2026-09-05.** **Start delay**, **Play for**, **Rest for**, and
**Output at rest**.

A **cycle** here is one mean bubble interval — whatever Bubble rate is set to.
Timing randomness still scatters the individual bubbles inside it. Start delay is
in rate mode units, so in Seconds it is seconds and otherwise it is cycles.

The gate stops new bubbles being **born**. Ones already sounding decay away
naturally, which is what makes entering a rest sound smooth instead of cut off.
While it is resting the timers are held at a full interval, so resuming does not
fire a burst of bubbles that queued up during the silence.

**Output at rest** is Pass-through or Silence. Pass-through leaves your input
alone and just stops the bubbles; Silence mutes everything, faded over about
three milliseconds so the boundary is not a click.

There is no "LFO at rest" here, unlike the Tremolo and the filters — this plugin
has no LFO to freeze. Drift carries its own play/rest, which is the equivalent.


---

## Drift and Ramp

**Added 2026-09-05.** Bubbler was built after the suite's 2026-06 drift sweep and never joined it, so until now it could not do a thing most of the suite can. The block is copied from **Veil**, which is the
built-and-heard reference for the complete set.

**Targets, on both Drift and Ramp:** Bubble rate, Timing randomness, Transpose, Pitch spread, Rise, Bubble length, Stereo width, Dry/wet, and Output — everything continuous the plugin has.

Each target remembers its own settings — pick one, set its amounts, pick another,
and the first keeps running. Switching the selector edits one without stopping
any of the others.

**Amounts are in each target's own unit**, with one exception: **Bubble rate** is in
BPM whatever the rate mode says, because that is the suite's rule everywhere —
the plugin converts, you never do.

**Drift period** can be counted in **seconds or beats**. In Beats it stretches
and shrinks live with the project tempo.

**Drift play/rest** makes the wander come and go. It runs for a while and then
**freezes where it stands** rather than returning to centre. Where it parks
depends on the fraction you use: a **whole number parks at no-change every single
time and is nearly inaudible**, while something like `1.2` cycles through four
different park points, two of them partial. The awkward fraction is the
interesting one.

**Ramp** states a destination and takes its time getting there. **Ramp time unit**
counts the duration in minutes or beats. **Ramp play/rest** turns the climb into a
**staircase** — climb, hold, climb — and the holds come out of the duration rather
than extending it, so a 32-beat ramp stepping 2 and holding 2 still arrives at
beat 32 and then stands on the landing.

**None of this has been heard yet.**

