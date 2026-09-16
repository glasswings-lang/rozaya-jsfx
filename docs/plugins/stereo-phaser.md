# Stereo Phaser

**Designed by Rozaya — Developed with Claude (Anthropic)**

---

## Overview

A classic swept-allpass phaser with a stereo spread and a very wide stage range. A chain of allpass filters is swept by an LFO; summing the swept signal with the dry input carves moving notches in the spectrum — the phaser "whoosh." Feedback deepens and resonates the notches. The stereo image comes from an LFO phase offset between the two channels, so the sweep swirls across the field rather than moving in lockstep.

At the low end of its stage range it's a normal musical phaser; pushed toward its maximum it turns into a dense, dozens-of-notches "curtain" for sound design.

## Signal Architecture

- **Allpass chain.** Each channel runs a cascade of first-order allpass stages (`y = coef·(y_prev + x) − x_prev`), the Cockos 4-Tap Phaser topology reimplemented and generalised to a selectable number of stages. The coefficient `coef = (1 − d)/(1 + d)`, with `d = 2·fc/srate`, places the phase transition at the audible sweep frequency.
- **LFO sweep.** A sine LFO moves the allpass corner between the Range Min and Range Max endpoints. The notches sweep with it.
- **Stereo spread.** The right channel's LFO is offset from the left by the Stereo Spread angle, so the two channels' sweeps diverge.
- **Feedback.** The last stage's output is fed back into the chain input, resonating the notches (the hollow, vocal character).
- **Mix.** Dry and wet are summed; 50% gives the deepest notches (equal cancellation).

## Parameters

**Range end** `Both (keeps the gap) / Bottom / Top, default Both (keeps the gap)` —
which end of the sweep the five controls below are editing. Both ends are always
live; this only chooses the view.

**`Both` is not the usual `All`.** Everywhere else in the suite, a picker on All
writes the same value to every option. The gap between the two ends IS the
sweep — how far the notches travel — so instead Both shows the midpoint and
applies your CHANGE to both ends, holding the span. Nudge it up 100 and 300/1500
become 400/1600: the whole sweep slides, the width stays. At the end of the range
it stops rather than letting the two squeeze together.

**Range pitch mode** `Hz / Semitones / Cents, default Hz`

**Range note name** `C-1 to G9` — a real control in every mode, and it reads back
from the value both ways.

**Range frequency (Hz / semitones / cents)** `0–20000, default 900` — the selected
end of the sweep. Bottom opens at 300 and Top at 1500, so Both opens showing 900.
(The two auto-sort, so which is higher does not matter.)

**Range fine tune unit** `Hz / Semitones / Cents, default Cents`

**Range fine tune** `-1000 to 1000, default 0`

**Tuning reference (Hz, all ends)** `20–2000, default 440` — what the note names
are counted from. One for the plugin.

**Feedback** `0–0.95, default 0.6` — resonance around the allpass chain. This is the hollow "whoosh." Push toward 0.9 for the dramatic jet-sweep; 0 for a soft, notches-only phase.

**Stages** `2–64 (even), default 6` — number of allpass stages. Each **2 stages adds one notch**. 4–6 is the classic musical phaser; the teens–20s thicken it; toward 64 it becomes a dense static "curtain" (dozens of notches) for sound design.

**Rate mode** `BPM / Seconds / Hz / Every N beats / N per beat, default Hz` —
the mode comes before the value it qualifies. The beat modes mean beats per
cycle, never a multiplier.

**Rate value** `0.001–1000, default 0.3` — LFO speed, in whatever the mode says.

**Stereo Spread (degrees)** `0–180, default 90` — LFO phase offset between channels. 0 = mono motion, 90 = wide swirl, 180 = fully counter-rotating.

**Wet/Dry Mix** `0–1, default 0.5` — 0.5 gives the deepest notches; lower for subtler phasing.

### Transport

New in the 2026-09-16 layout; the Phaser had none before.

**Transport unit** `Cycles / Seconds / Beats, default Cycles` — one unit for the
three below. Cycles, because this plugin has a turn of its own to count.

**Start delay (in transport units)** `0–1000, default 0` — hold everything still
this long after play. It holds the drift AND the ramp.

**Play for (in transport units, 0 = always)** and **Rest for (in transport units,
0 = always)** `0–1000, default 0` — works for one, rests for the other, repeats.
Both must be above zero or the gate is off, which is what it always did.

**Output at rest** `Pass-through / Silence, default Pass-through` — what you hear
during a rest. Crossfaded over 3 ms either way, so neither edge clicks.

### Drift and Ramp

**Drift amount unit** and **Ramp by unit** `Target default / Hz / Semitones / Cents / Milliseconds / Seconds / Minutes / BPM / Beats / Cycles / dB / Percent / Degrees, default Target default` — what the
amounts are typed in, for the selected target. `Target default` is what the amount
always meant, so nothing already set changes; a unit that cannot fit its target
falls back to it.

**Drift target** `Range frequency (both ends), Bottom frequency, Top frequency, Range fine tune (both ends), Bottom fine tune, Top fine tune, Tuning reference, Feedback, Rate value, Stereo spread, Wet/dry mix, Play for, Rest for` — which control the drift moves. Drift and Ramp share one list.

**Ramp target** `Range frequency (both ends), Bottom frequency, Top frequency, Range fine tune (both ends), Bottom fine tune, Top fine tune, Tuning reference, Feedback, Rate value, Stereo spread, Wet/dry mix, Play for, Rest for`

**Drift up amount (in the Drift amount unit)** and **Drift down amount (in the
Drift amount unit)** `0–20000, default 0` — how far it wanders each way.

**Drift period unit** `Cycles / Seconds / Beats, default Cycles`, per target, and
**Drift period (0 = off)** `0–1000, default 20` — how long one full wander takes.

**Drift shape** `Sine / Triangle / Random, default Sine`

**Drift play for (periods, 0 = always)** and **Drift rest for (periods, 0 =
always)** `0–1000, default 0` — the drift wanders for one, freezes where it
stands for the other, and repeats. Counted in drift periods, so no second unit.

**Ramp by (in the Ramp by unit)** `-20000 to 20000, default 0` — the signed amount
to ride to.

**Ramp time unit** `Cycles / Seconds / Minutes / Beats, default
Minutes`, per target, and **Ramp duration (in ramp time units)** `0–1000, default 0` — how
long the ride takes.

**Ramp play for (0 = smooth)** and **Ramp rest for (0 = smooth)** `0–1000, default
0` — the staircase: the ramp advances for one, holds for the other. The holds
come OUT of the duration, they do not extend it.

**Ramp engage (all targets)** `Off / On, default Off` — one switch arms every
configured target.

**Ramp start delay (in ramp time units)** `0–1000, default 0` — wait this long
after engage before THIS target moves, so targets can be staggered.

**Rest mode (for Drift)** and **Rest mode (for Ramp)** `Walk through / Freeze in
place, default Walk through` — what each does during a transport rest. Each sits
in the block it freezes; drift and ramp are their own things.

## Usage Notes

- **Classic phaser:** Stages 4–6, Feedback 0.5–0.7, Rate ~0.3 Hz, Spread 90°, Range ~300–1500 Hz.
- **Sound-design curtain / "traffic":** Stages up in the 30s–60s, high Feedback — the notches get so dense they merge into a continuous swept resonant wash.
- **Stacking for complex motion (Bi-Phase trick):** two instances in series with *different* Rates drift against each other and beat — richer, evolving motion a single phaser can't make.
- **REAPER auto-mute warning.** One instance is safe at any setting. But **several identical copies on one track at very high Feedback** stay phase-locked (each LFO starts at the same point), so their resonant peaks line up and multiply in series — the level can spike hard enough that REAPER auto-mutes the track to protect your speakers. If that happens: drop Feedback (~0.5 is safe), **vary** the Rate/Range between the copies so they drift apart, or add a limiter after them.

---

*Stereo Phaser is part of the Rozaya JSFX plugin suite.*
*Designed by Rozaya — Developed with Claude (Anthropic).*


### Host tempo sync

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
and behaves identically; anything you had saved on it is untouched.)* (**default Hz**) — the suite's
canonical four, in the suite's canonical order, as of 2026-09-05 (R20).

**BPM** is sweeps per minute. **Seconds** is seconds per sweep. **Hz** is the
original free-running behaviour, sweeps per second, project tempo ignored.
**Host x** locks the sweep to the project, and Rate then means **every N beats**:
set it to 4 and one full sweep takes four beats. Tempo changes apply live.

**Why this one defaults to Hz when the rest of the suite defaults to BPM.** All
three saved instances in `strangeness.RPP` store *nothing* for this control, so
they take whatever the declared default is. It used to be `Own Hz` at position
one; putting Hz at the default lands them on exactly the behaviour they had, and
meant this change needed no edit to your project at all. The enum ORDER is
canonical; only which one starts selected differs.

This page used to say "Seconds and BPM would be meaningless here". That was
wrong — seconds per sweep is an ordinary way to say a speed — and consistency
across the suite outranks a per-plugin guess anyway.

**Beats per cycle is a plain number, not a menu.** 4 is every four beats. 3.7 is
every three and seven tenths of a beat — which no note-division grid can express,
and which is exactly the kind of thing this suite exists for. Bigger is slower.

> **Switching modes changes what Rate means, and nothing rescales it.** A rate of
> 0.3 is a slow sweep in Own Hz and just over a third of a beat per cycle — very
> fast — in Host x. Set the mode first, then the value.

**Host ratio (retired)** — hidden, and does nothing.
It used to be a menu of ratios (*every 4 beats*, *2 per beat* …) that wrote a
**multiplier** into Rate. The multiplier is gone, so the menu that translated it has
no job left: "every 4 beats" is now typing 4. The slider itself stays in the file
only because this plugin has no reorder pending. It gets deleted when it does have
one. (An earlier version of this page said it *could not* be deleted, which mixed up
two different things: **renumbering** a slider is dangerous, because REAPER restores
by position and everything above it shifts. **Deleting** one is not — the id is
written out explicitly, so removing it just leaves that number unused, and Heartbeat
has carried such gaps harmlessly since v2.14.)

---

#### Why the multiplier went, and why nothing hides any more

A multiplier is a number you cannot hear without doing arithmetic against the project
tempo — `0.25` is not a speed, it is a sum you have to finish. Because it was
illegible, the rate slider had to be **hidden** in Host x and the menu shown instead;
because it was hidden, entering Host x had to **stamp** a landing value into it so you
were not left on something arbitrary. That stamp is the bug that cost a session
elsewhere in the suite, where a saved project had its hand-set rate overwritten on
every load.

Beats per cycle is legible on its own, so the whole chain unwinds: nothing is hidden,
nothing is stamped, and the rate slider is always visible showing the value it is
actually running at. (Suite rule R13-revised, 2026-09-02.)

---

## Drift and Ramp

**Added 2026-09-05.** Until then the Phaser had neither — it was built after the
suite's drift sweep and never joined it, which meant three plugins simply could not do
a thing the rest of them can. The block is copied from **Veil**, which is the
built-and-heard reference for the complete set, rather than written fresh.

**The six targets, on both Drift and Ramp:**

| Target | What moving it does |
|---|---|
| **Rate** | the sweep speeds up and slows down |
| **Range min Hz** | the bottom of the swept window travels |
| **Range max Hz** | the top of it travels |
| **Feedback** | the notches deepen and shallow |
| **Stereo spread** | the swirl opens and closes across the field |
| **Wet/dry mix** | mostly a Ramp target — the hour-long fade in or out |

**Stages is deliberately not a target.** It is a whole number of allpass sections, and
adding or removing one mid-play makes a filter appear from nowhere, which clicks. Same
reason Voices is off the Sustain Looper's list.

**Rate amounts are in BPM, in every rate mode.** So a Drift up of `30` means the same
wander whether the sweep is set in Hz, seconds or beats — the plugin converts, you
never do. Every other target's amount is in that target's own unit: Hz for the range
edges, degrees for spread, and the raw 0–1 for feedback and mix.

**Each target remembers its own settings.** Pick a target, set its amounts, pick
another — the first one keeps running. That is the same nested-selector behaviour Drift
and Ramp have everywhere else in the suite, and it now saves with the project, which
required giving this plugin save/restore for the first time.

### What the numbers do, simulated rather than reasoned

- **Drift up 30 / down 15 BPM on Rate**, from a baseline of 0.3 Hz: the sweep runs
  between **0.05 Hz** (one pass every 20 seconds) and **0.8 Hz** (one every 1.25), and
  the up and down halves are asymmetric in exactly the 2:1 you asked for.
- **Drift period unit** is `Cycles / Seconds / Beats`, Cycles by default. A cycle
  is one full sweep, so the wander stretches when you slow the sweep down;
  Seconds ignores the rate; Beats follows the project tempo. It is referenced
  against the rate BEFORE drift, so drifting the rate cannot modulate its own
  drift period.

**Setting the period to 0 switches that target's drift off**, which is the quick
disable. Until 2026-09-08 the control's minimum was 1 and 0 was unreachable, so
the only way to stop a drift was zeroing both amounts.
- **Drift period unit set to Beats**, period 4 at 90 BPM: one wander every 2.67
  seconds, and it stretches and shrinks live when the project tempo changes.
- **Drift play/rest**: the wander runs for a while and then FREEZES WHERE IT STANDS
  rather than returning to centre. Where it parks depends on the fraction you use — a
  **whole number parks at no-change every single time and is nearly inaudible**, while
  `1.2` cycles through four different park points, two of them partial. An awkward
  fraction is the interesting one.
- **Ramp play/rest** turns the ramp into a staircase — climb, hold, climb. The holds
  come out of the duration rather than extending it, so a 32-beat ramp stepping 2 and
  holding 2 still arrives at beat 32 and then stands on the landing.

### One thing that had to change underneath

The Phaser locks its sweep to the project's bar position in Host x, so it lands the
same way at the same bar however you got there. Its own source comment used to say
that needed no safety check *because nothing in this plugin can modulate the rate*.
Drift and Ramp made that false, so the lock now hands over to free-running the moment
either one touches the rate — no jump at the handover, and it stays free until the next
transport start rather than lurching back onto the grid mid-play. Same behaviour the
Tremolo and the Sweeping Filter already have.

**None of this has been heard yet.**
