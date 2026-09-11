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

**Rate Mode** `BPM / Seconds / Hz / Every N beats / N per beat`

**The two host modes are the same idea from opposite ends, and both follow the
project tempo.** *Every N beats* means one cycle takes that many beats — `4` is
one per bar in 4/4. *N per beat* means that many cycles fit in a beat — `8` is
eight per beat.

They are reciprocals, so whichever you pick decides which end of your music is a
whole number and which needs a decimal. Slow, drifting, phase-music settings are
whole in *Every N beats*; dense, fast ones are whole in *N per beat*. They agree
exactly at `1`, which is one cycle per beat either way.

*(Renamed and extended 2026-09-05. `Host x` was the old name for `Every N beats`
and behaves identically; anything you had saved on it is untouched.)* (**default Hz**) — the suite's canonical four, in the suite's canonical order, as of 2026-09-05 (R20). Bubble rate carries the mode's unit. In **Host x** it means every N beats, so a bubble every four beats is `4`; bigger is slower.

This used to be `Own rate / Host x`, where "Own rate" meant per second. It defaults to Hz rather than the suite's usual BPM because every saved instance relies on that default meaning per second — five in `the-sound-of-a-drain` had it stored explicitly and were migrated; the five in the two `birdsong` projects store nothing and take the default.

**Host ratio** — *retired 2026-09-02.* It spared you arithmetic when Host x made Bubble rate a multiplier; in beats, *every 4 beats* is typing 4. Hidden and inert; it stays in the parameter list only because slider IDs can never be renumbered.

**Timing randomness %** `0–100, default 70` — spacing irregularity. High = naturally scattered.

**Transpose** *(the block, new 2026-09-09)* — how far each grain is shifted.

- **Source note (where zero is)** `{None, C-1 … G9}, default None` — you tell it what
  note the incoming audio is. It cannot work that out for itself. At **None** nothing
  below changes and the semitone number is simply the control, exactly as before.
- **Target note** — only appears once Source note is set. Pick the note you want to
  hear and the shift is worked out for you, so you never do the subtraction yourself.
- **Transpose value (Hz / semitones / cents)** — **the shift**, always, whatever else
  is set. Nothing hides it or takes it over.
- **Transpose unit** `{Hz, Semitones, Cents}, default Semitones`.
- **Fine tune** and **Fine tune unit** `default Cents` — the one fine tune.
- **Tuning reference (Hz)** `default 440` — what an Hz shift is measured from. Without
  an anchor, "shift by 30 Hz" would not name an interval at all.

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

**Targets, on both Drift and Ramp, in the order of the controls:** Bubble rate, Timing randomness, Transpose, Fine tune, Tuning reference, Pitch spread, Rise, Bubble length, Stereo width, Dry/wet, Output, Play for, and Rest for — everything continuous the plugin has. *(Fine tune, Tuning reference, Play for and Rest for joined 2026-09-11. Saved setups were carried across by the plugin itself.)* Tuning reference only matters to a Transpose said in Hz. Play for and Rest for move how long each lasts; the gate still needs both controls above zero.

Each target remembers its own settings — pick one, set its amounts, pick another,
and the first keeps running. Switching the selector edits one without stopping
any of the others.

**Amounts are in each target's own unit**, with one exception: **Bubble rate** is in
BPM whatever the rate mode says, because that is the suite's rule everywhere —
the plugin converts, you never do.

### Whose turn it is (2026-09-09)

Some drift targets are read by the engine **once per event** rather than
continuously. Those now advance their wander by exactly one step of
`1 / period` at that moment, and not at all in between — so a period of 8 is
eight of that event, and it stays eight however much the other targets move.

Before this they were sampled out of a wander that never stopped spinning:
almost all the motion was thrown away, the period did not count what it said,
and the targets were not independent of each other. Rozaya found it, 2026-09-09.

**It is a switch now, not a rule (2026-09-09).** `Drift movement`, next to the
period controls, is per target: `With the target` or `On a clock`. Rozaya: it
*"should have been a switch from the very beginning"* — both are ordinary
artistic choices and neither is the plugin's to make.

**Defaults to `With the target`:** **Timing randomness**, **Transpose** and
**Pitch spread**. All three are read at the moment a bubble is born and then
belong to that bubble, so they step once per bubble.

**`With the target` in Seconds or Beats (2026-09-10).** The first unit counts turns. In Seconds or Beats the drift's clock runs in that unit only while the target's own thing is happening — and a bubble is an instant, so each birth adds that bubble's own **Bubble length** — and freezes in between, picking up where it stopped at the next turn. Rozaya: *"stop mid-cycle, freeze the clock mid-whatever unit, then pick up on the next cycle from wherever the clock was last."* Until then those two units were silently ignored for such a target.

**Every birth counts, on either channel.** An earlier build counted the left
stream only; that tie-break is gone, and needing it at all was the sign the
first attempt was wrong.

**Defaults to `On a clock`:** Bubble rate, Rise, Bubble length, Stereo width, Dry/wet and
Output, all of which are read every sample.

A stepped wander is a staircase with as many steps as its period has events.
Long periods sound much as they did; short ones are more obviously
event-to-event.

**Drift period** can be counted in **cycles, seconds or beats** — and cycles is
the default. A cycle is this plugin's own: twenty cycles means twenty of whatever
it is doing, so the wander stretches when you slow the plugin down. Seconds is
wall clock and ignores the rate. Beats follows the project tempo live.

**Setting the period to 0 switches that target's drift off**, which is the quick
disable. Until 2026-09-08 the control's minimum was 1 and 0 was unreachable, so
the only way to stop a drift was zeroing both amounts.

It is referenced against the rate BEFORE drift is applied, so drifting the rate
cannot modulate its own drift period.

**Drift play/rest** makes the wander come and go. It runs for a while and then
**freezes where it stands** rather than returning to centre. Where it parks
depends on the fraction you use: a **whole number parks at no-change every single
time and is nearly inaudible**, while something like `1.2` cycles through four
different park points, two of them partial. The awkward fraction is the
interesting one.

**Ramp** states a destination and takes its time getting there. **Ramp time unit**
counts the duration in **cycles, seconds, minutes or beats** — minutes by default,
which is what a long sleep fade is usually thought in. Cycles counts this
plugin's own, referenced against the rate before drift and ramp touch it.
**Ramp play/rest** turns the climb into a
**staircase** — climb, hold, climb — and the holds come out of the duration rather
than extending it, so a 32-beat ramp stepping 2 and holding 2 still arrives at
beat 32 and then stands on the landing.

**None of this has been heard yet.**

### Changing the rate now takes effect immediately

**Fixed 2026-09-05.** The gap to the next bubble used to be decided the moment
the previous one was born, so if you set a slow rate and then sped it up, you sat
through the whole old interval before anything changed — set it to one every six
seconds, change your mind, and you wait six seconds wondering whether you
actually moved the control.

It now counts *up* to a target it recalculates every sample, which is what
Heartbeat and Womb have always done. Speed it up and the next bubble arrives at
once.

**The timing randomness is unchanged.** It used to be rolled as a length; it is
now rolled as a proportion — *this bubble waits 1.3× the normal gap* — so the
random spread is identical and only what it is measured against has changed.
Simulated over sixty seconds at 70% randomness: same number of bubbles, same
shortest gap, same average, same longest.

**Drift and Ramp aimed at Bubble rate are the real winners.** They move the rate
continuously, and until now a gap you were already inside could not hear them.

