# Breath Generator — authored target layout

**Status: AUTHORED 2026-09-08. NOT BUILT. NOT HEARD.**

Written before touching the file, per the standing rule: author the whole layout
first, then build and migrate once. Breath Generator has never had a session of
its own — every change it carries arrived as part of a suite-wide pass — so this
is the first time its order has been decided rather than accumulated.

**Cost: 32 sliders → 40, and every one of them moves.** 27 instances across 20
projects need a slider-line migration. Rozaya, 2026-09-08, on accepting that:
*"I'd reach for the controls being in places that make fucking sence, migration
again be damned."*

**The reference is Womb, not a blank page.** Womb v3 carries the same breath —
four segments whose sum is the cycle, a rate that is emergent from them, the two
filter frequencies, four fades — and its layout has been heard and approved
(2026-09-06, *"Everything else, though, passes. :)"*). Where Womb has already
answered a question, this copies the answer rather than re-deriving it. That is
the whole point of the suite being consistent: a thing learned on one plugin
should be true of its twin.

## One open question for Rozaya

**Breath Generator has no output level control of any kind.** Not Output dB, not
Volume, nothing — verified against all 32 sliders. Womb has `Breath Volume`.
Every other plugin in the suite has an output. Slider 21 below is a proposal,
not a decision, and it is the only thing here that is not already settled by a
rule or by Womb.

## The order

Canonical reading order: what the plugin IS → its rate → the shape of its
movement → stereo → output → transport → drift → ramp.

### Rate — 1–2

The breath has **no rate mode**, and that is deliberate. Its rate is EMERGENT
from its four segments, so there is no rate value for a five-option mode to
qualify. This is the same principled R20 exception Womb was granted on
2026-09-06, and it was granted because forcing the five options on a breath
produces `N per beat`, and eight breaths per beat is not a thing anyone wants.

| # | control | note |
|---|---|---|
| 1 | `Set breath rate (per minute, or beats per breath; 0 = off)` | **NEW.** A one-shot, exactly as Womb's. Writes the four segments, preserving their ratio. This is the whole point of the change: today, ten breaths a minute has to be worked out as four durations by hand. |
| 2 | `Breath unit` `{Seconds, Beats}` | **NEW.** What the four segments below are counted in. |

### The shape of the breath — 3–6

Absolute durations, always, in the unit above. Their sum IS the cycle, which is
why halving the inhale genuinely shortens the breath.

| # | control | from |
|---|---|---|
| 3 | `Inhale (in breath units)` | was 1, `Inhale Duration (sec)` |
| 4 | `Top pause (in breath units)` | was 2 |
| 5 | `Exhale (in breath units)` | was 3, `Exhale Duration (sec)` |
| 6 | `Bottom pause (in breath units)` | was 4 |

**The rename is required, not cosmetic.** Once `Breath unit` exists, these are no
longer always seconds, and the suite's rule is that a control may never change
what it MEANS without saying so on the control itself. Gate on one visible
switch, and name it in every affected slider — this is that.

**`Bottom pause` also gets its range fixed.** It is declared `0..20` where its
three siblings are `0..1000`, which is the odd one out for no reason anyone
recorded, and `breathscapes.RPP` already has 8 typed into a sibling.

### Pitch — 7–13

R22, one block behind a target. **Not two blocks** — the backlog table said two
and was corrected 2026-09-08; Rozaya settled it as *"target, then select from 2,
that way you're able to extend it later if needed, also less sliders."*

Placed here because Womb puts `Inhale/Exhale Frequency Hz` exactly here, between
the segments and the fades.

These are **filter centres, not generated tones**, and they get the block anyway
— Rozaya, 2026-09-08: *"Filters: yes, they should. Musicality integration, not
exclusivity, is the idea here."* Breath Generator makes its own sound, so the
block carries a `Note` picker.

| # | control | note |
|---|---|---|
| 7 | `Pitch target` `{All, Inhale, Exhale}` | **NEW.** `All` at position 0. |
| 8 | `Note` (C-1 … G9) | **NEW.** Full MIDI range — a standard, not a measurement of what these projects happen to use. |
| 9 | `Pitch value (Hz / semitones / cents)` | replaces sliders 5 and 6 |
| 10 | `Pitch mode` `{Hz, Semitones, Cents}` | **NEW.** |
| 11 | `Fine tune value (Hz / semitones / cents)` | **NEW.** A second complete pair, always present. |
| 12 | `Fine tune mode` `{Hz, Semitones, Cents}` | **NEW.** |
| 13 | `Tuning reference (Hz)` | **NEW.** One per plugin. |

**Migration note: the two frequencies are 800 and 600 Hz by default and are real
values in 27 instances.** They move into the per-target bank behind the selector,
with `Pitch mode` seeded to `Hz` so every stored number keeps meaning exactly
what it means today. Nothing is converted to semitones on the way in.

### Fades — 14–18

Unchanged in content, order preserved from both the current file and Womb.

| # | control |
|---|---|
| 14 | `Inhale fade in` |
| 15 | `Inhale fade out` |
| 16 | `Exhale fade in` |
| 17 | `Exhale fade out` |
| 18 | `Fade mode` `{Linear, Cosine, Exponential, Natural}` |

Names go to sentence case (R5): `Inhale Fade In` → `Inhale fade in`.

### Stereo — 19–20

| # | control |
|---|---|
| 19 | `Stereo width` |
| 20 | `Stereo flip` `{Normal, Flipped}` |

### Output — 21

| # | control | note |
|---|---|---|
| 21 | `Output (dB)` | **NEW, AND THE ONE OPEN QUESTION.** Proposed default 0 dB, range −60…+12. Not built until Rozaya says so. |

### Transport — 22–24

| # | control | from |
|---|---|---|
| 22 | `Start delay (seconds)` | was 14 |
| 23 | `Play for (breaths)` | was 15 |
| 24 | `Rest for (breaths)` | was 16 |

### Drift — 25–32

Order unchanged; the block moves as a unit from 17–24.

| # | control | change |
|---|---|---|
| 25 | `Drift target` `{Inhale, Top pause, Exhale, Bottom pause, Breaths/min}` | — |
| 26 | `Drift up amount (units match target)` | **LABEL FIX.** Currently reads `(seconds)`. |
| 27 | `Drift down amount (units match target)` | **LABEL FIX.** |
| 28 | `Drift period (0 = off)` | — |
| 29 | `Drift period unit` `{Cycles, Seconds, Beats}` | — |
| 30 | `Drift shape` `{Sine, Triangle, Random}` | — |
| 31 | `Drift play for (periods, 0 = always)` | — |
| 32 | `Drift rest for (periods, 0 = always)` | — |

**Why the label fix is not cosmetic.** Breath Generator is the ONLY plugin in the
suite whose drift amounts say `(seconds)`; the other eighteen say `(units match
target)`. Its own target list includes `Breaths/min`, so the label is wrong for
one of its five targets — and it is wrong in the direction that silently
mis-states a unit, which the suite has a standing rule against.

### Ramp — 33–40

Order unchanged; the block moves as a unit from 25–32. Note that `Ramp start
delay` is currently slider **32**, detached from its own block by seven places —
it was appended later, as the append-only rule required at the time. It rejoins
the block here.

| # | control |
|---|---|
| 33 | `Ramp target` |
| 34 | `Ramp by` |
| 35 | `Ramp time unit` `{Cycles, Seconds, Minutes, Beats}` |
| 36 | `Ramp duration (in ramp time units)` |
| 37 | `Ramp play for (0 = smooth)` |
| 38 | `Ramp rest for (0 = smooth)` |
| 39 | `Ramp engage` `{Off, On}` |
| 40 | `Ramp start delay (in ramp time units)` |

## What this deliberately does NOT do

Each of these is in scope for the suite but out of scope for this migration, and
naming them here is what stops a later session folding one in on the way past.

- **No Solo.** Solo is for auditioning one of several things; Breath Generator
  has one breath. Womb has one because Womb has three layers.
- **No high-pass or post-filter.** Womb's breath carries `Breath High-pass Hz`,
  `Breath Post-filter Hz` and `Breath Post-filter Q`. Breath Generator has none
  of them. That is a real difference and it may well be worth closing, but it is
  a new capability rather than a placement question, and folding it in here would
  make this migration two jobs.
- **No sigh.** Same reasoning.
- **No new drift or ramp targets.** The pitch controls do not become modulation
  targets in this pass. Adding sliders does not require adding targets.

## Build order

1. Rozaya answers the output-level question.
2. Build the file at 40 sliders, every new control defaulting to off or to what
   the plugin already means: `Set breath rate` 0 (= off), `Breath unit` Seconds,
   `Pitch mode` and `Fine tune mode` Hz, `Fine tune value` 0.
3. **Bump the `@serialize` magic in the same commit as the renumber.** That is
   the only thing that made the last accidental renumber in this suite
   repairable.
4. Author the migration from the table above — an exact literal map, with a
   count assertion, using `tools/rpp_sliders.py`. Breath Generator is under 64
   sliders both before and after, so the `""` marker at token index 64 does not
   apply; assert that rather than assume it.
5. Verify by decoding a real project line by control NAME against a
   pre-migration snapshot, not against the table the migration used. Range-check
   every migrated value against its new slider's declared min/max.
6. Ask for an ear test. It is not done until it has been heard.
