# Dapple

**Designed by Rozaya — Developed with Claude (Anthropic)**

---

## Overview

A scattered-droplet texture **generator**. It makes its own sound — no input needed — from random pitched events that pop on irregular timing, each ringing and chirping upward as it fades, piling up into a pointillist wash. It lands somewhere between rain on glass, plinking droplets, and a resonant fizz.

It began as an attempt to synthesize water and never quite got there — it became its own thing instead, which is why it's called Dapple rather than "Water."

Each event blends two voices, set by the **Tone vs Noise** knob: a **noise** burst through a resonant lowpass (fizz, gurgle, steam) and a clean **sine** that chirps upward (a bright droplet "plink" — bubbles are little resonators that rise in pitch as they collapse, the tonal approach to water synthesis after Andy Farnell / Minnaert).

**Generator or effect.** By default Dapple generates from internal noise. Turn up **Excite from input** and its noise voice is driven by the audio on the track instead — feed it a noisescape or any broadband texture and it bubbles *that*. (For *tonal* sources, use [Bubbler](bubbler.md); Dapple's engine wants broadband material.)

## Signal Architecture

- **Random events.** A timer fires bubbles at the set rate, with adjustable timing randomness (irregular spacing is what makes it read as natural rather than metronomic). Each event picks a new random low pitch within the spread.
- **Polyphonic — 32 voices per channel.** Each event takes its own voice, so overlapping bubbles ring out independently instead of cutting each other off. A new event grabs the *quietest* voice, so it never truncates one that's still audibly ringing.
- **Per-event pitch rise.** As a bubble's amplitude envelope decays, its pitch sweeps upward — the collapsing-bubble chirp. This drives both voices.
- **Noise voice.** Noise (Park-Miller, independent per channel) gated by the envelope, through a resonant state-variable lowpass tuned to the (rising) pitch. Its ring-out comes from the filter resonance.
- **Tonal voice.** A sine oscillator at the (rising) pitch, enveloped — the clean plink.
- **Stereo.** Two fully independent event streams (L/R), blended toward mono by the Stereo width control.
- **Output** adds to whatever's on the track, so it layers over existing audio; put it on an empty track for the texture alone.

## Parameters

**Bubble rate** `0.001–1000, default 6` — what this means depends on Rate Mode.

- In **Hz**, it is average events per second. Low = distinct drips; high = they overlap into a continuous gurgle. In **BPM** it is events per minute, and in **Seconds** it is the average gap between drips.
- In **Host x**, it is **beats per bubble**. Set 4 and you get one bubble every four beats; set 0.5 and you get two per beat. It follows the project tempo, so changing the tempo carries the setting with it.

Fractions are free — *every 3.7 beats* is as reachable as *every 4*. Nothing forces you onto a note grid.

**Rate Mode** `BPM / Seconds / Hz / Host x` (**default Hz**) — the suite's canonical four, in the suite's canonical order, as of 2026-09-05 (R20). Bubble rate carries the mode's unit. In **Host x** it means every N beats; bigger is slower.

This used to be `Own rate / Host x`, where "Own rate" meant per second. It defaults to Hz so that every saved instance keeps that meaning — all fourteen in the library store nothing for this control, so no project needed editing.

**Host ratio** — *retired 2026-09-02.* It existed to spare you arithmetic back when Host x made Bubble rate a multiplier of the tempo; now that the control is in beats, *every 4 beats* is simply typing 4. It is hidden and does nothing, and stays in the parameter list only because slider IDs can never be renumbered without scrambling saved projects.

**Timing randomness %** `0–100, default 70` — spacing irregularity. 0 = metronomic; high = naturally scattered.

**Pitch (Hz)** `40–1500, default 150` — base resonant pitch. Low = big slow bubbles; higher = small fizzy ones.

**Pitch spread %** `0–100, default 50` — how far each event's pitch varies from the base (up to ±3 octaves). 0 = all one pitch; up = watery variety.

**Resonance (noise voice)** `0–0.97, default 0.85` — ring/tone of the noise voice. Low = soft filtered blips; high = pingy, near-singing. (Only affects the noise voice; the tonal voice is a clean sine.)

**Bubble length (ms)** `5–1000, default 120` — envelope decay; how long each event rings.

**Rise %** `0–100, default 40` — how far each event's pitch sweeps upward as it fades. This is the chirp — the tonal voice needs some Rise to sound like a drop rather than a static beep.

**Stereo width %** `0–100, default 80` — 0 = mono, 100 = fully independent L/R streams.

**Output (dB)** `-24 to +12, default 0` — level. Dense settings stack up loud; pull this down if it distorts.

**Tone vs Noise %** `0–100, default 50` — blend between the two voices. 0 = noise gurgle bed, 100 = pure sine plinks, in between = the dappled mix.

**Excite from input %** `0–100, default 0` — where the noise voice gets its excitation. 0 = internal noise (pure generator, the default). Up = the audio on the track drives the noise voice instead, so it bubbles *your* sound (feed it a noisescape/broadband texture). A safety clamp keeps it bounded if a hot or tonal source is fed in. Only affects the noise voice; the tonal voice stays synthetic.

## Usage Notes

- **Dapple is for noise / broadband texture.** It generates from internal noise by default, and with **Excite from input** it can bubble a *noise / broadband source you feed it* (a noisescape, wind, breath, cymbals, hiss). To bubble a *tonal* source (pad, voice, drone, sustained tone), use its sibling **[Bubbler](bubbler.md)** instead — a granular effect that transposes your input into rising droplets. The two are tuned for opposite material; crossing them (a pure tone into Dapple, or noise into Bubbler) gets janky.
- **Bubble a noisescape:** set Excite from input to 100, Tone vs Noise low (so the input-driven noise voice dominates), and dial Pitch / Resonance to taste — the resonant droplets pick up the character of whatever broadband texture you feed it.
- **Droplets / cave:** Tone ~80, Rise ~50, Pitch ~120–200, low rate, high Timing randomness, longish Bubble length.
- **Babbling brook:** Tone ~30–40, high rate, high Pitch spread — mostly gurgle with a sparkle of plink.
- **Full dappled mix:** Tone ~50–60, moderate everything.
- **It's a generator, not an effect** — it needs no input and adds its sound on top of the track. Empty track = texture alone; track with audio = that audio *plus* the texture layered over it.
- **Dense = loud.** Pushing rate and length way up stacks many voices; if it distorts, lower Output. It stays stable — it's a level thing, not a blow-up.
- The tonal voice needs some **Rise** to chirp; with Rise at 0 it's a static tone.

---

*Dapple is part of the Rozaya JSFX plugin suite.*
*Designed by Rozaya — Developed with Claude (Anthropic).*

## The 2026-09-05 layout change

Every control moved into the suite's canonical reading order: what the plugin
**is**, then its **rate**, then the **shape of its movement**, then **stereo**,
then **output**, then **transport**, then **drift**, then **ramp**. **Rate mode came home to slider 2**, eleven places from the rate it defines, and the retired **Host ratio** picker was deleted.

**Pitch and Bubble length are read when a bubble is born**, so moving them changes new bubbles rather than ones already sounding.

**Your saved projects were migrated** — 14 instances across bubbles and womb-bubbles-proto. Verified by
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

**Added 2026-09-05.** Dapple was built after the suite's 2026-06 drift sweep and never joined it. The block is copied from **Veil**, which is the
built-and-heard reference for the complete set.

**Targets, on both Drift and Ramp:** Bubble rate, Timing randomness, Pitch, Pitch spread, Resonance, Bubble length, Rise, Tone vs noise, Excite from input, Stereo width, and Output.

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

