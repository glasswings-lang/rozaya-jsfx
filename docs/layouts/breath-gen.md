# Breath Generator — authored target layout

**Status: BUILT AND MIGRATED 2026-09-08. NOT HEARD.**

The plugin is at 40 sliders, installed, and all 4 instances across the 3 live
projects are migrated and verified (238 checks by control name against the
pre-migration snapshot, 0 failures). **Nothing here has been played.**

Written before touching the file, per the standing rule: author the whole layout
first, then build and migrate once. Breath Generator has never had a session of
its own — every change it carries arrived as part of a suite-wide pass — so this
is the first time its order has been decided rather than accumulated.

**Cost: 32 sliders → 40, and every one of them moves.** **4 instances across 3
live projects** need a slider-line migration: `templates/breathscapes.RPP`,
`to-play-with-later/micle.RPP`, and `to-play-with-later/organic-movement.RPP`
(two instances). **Nothing in `finished/` uses this plugin at all.**

**An earlier count in this file said 27 instances across 20 projects. That was
wrong** — the grep swept `E:/reaper/finished/backups/` and counted seventeen old
snapshots of the same three files as live projects. Scope a project grep to
exclude the backups folder, or it will inflate every number you take from it.
This is the cheapest migration in the suite, which is part of why R22 should be
prototyped here. Rozaya, 2026-09-08, on accepting that:
*"I'd reach for the controls being in places that make fucking sence, migration
again be damned."*

**The reference is Womb, not a blank page.** Womb v3 carries the same breath —
four segments whose sum is the cycle, a rate that is emergent from them, the two
filter frequencies, four fades — and its layout has been heard and approved
(2026-09-06, *"Everything else, though, passes. :)"*). Where Womb has already
answered a question, this copies the answer rather than re-deriving it. That is
the whole point of the suite being consistent: a thing learned on one plugin
should be true of its twin.

## The output control — ANSWERED, it goes in

**Breath Generator has no output level control of any kind.** Not Output dB, not
Volume, nothing — verified against all 32 sliders. Womb has `Breath Volume`.
Every other plugin in the suite has an output. Rozaya, 2026-09-08: *"We do need
it I think, yeah."* So slider 21 is decided, not proposed.

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
| 1 | `Breath rate (per minute, or beats per breath)` | **NEW, and REBUILT 2026-09-09 as a LIVE TWO-WAY control, not the one-shot originally authored here.** It always shows the rate the segments imply, and typing into it rescales them, ratio kept. Rozaya: *"it either has to write to the 4 segments or the 4 segments have to write to it, or both. but it 0s out and reaper reads it and clamps."* Womb's `Set breath rate` is still the one-shot; this one is not. |
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

R22, one block behind a target. **The rule was rebuilt on 2026-09-09 after the
first version was heard and rejected.**

**What was wrong with the first version.** It had a `Note` picker as the coarse
control and a `Pitch value` that was an OFFSET from it, plus a `Fine tune` pair.
Rozaya: *"you're doing one job twice... note is not master here. it's one way of
expressing pitch, period."* Making the value an offset turned it into a second
fine tune sitting above the real one, with the wrong half labelled as coarse.
Remove the master relationship and the duplication disappears.

**And `Note is not a mode` was a workaround dressed as a rule.** R22 stated it as
a principle. The actual reason is that a JSFX slider can be a list of note names
or a continuous number, never both. That is the failure this repo already has a
name for, and it got caught again.

| # | control | note |
|---|---|---|
| 7 | `Pitch target` `{All, Inhale, Exhale}` | `All` at position 0. |
| 8 | `Pitch mode` `{Hz, Semitones, Cents}` | **Mode first**, deliberately — it decides whether the readout below means anything. Inverts R20's value-then-mode order on purpose. |
| 9 | `Note name` | **A real control, both ways.** Pick C4 or type 60 — move either and the other follows. `slider_show` hides it outside Semitones mode, where it would be lying. |
| 10 | `Pitch value (Hz / semitones / cents)` | **THE pitch.** Hz is the frequency; Semitones is the MIDI note number (60 = middle C); Cents is the same axis ×100. |
| 11 | `Fine tune` | The only fine tune. There is exactly one. |
| 12 | `Fine tune unit` `{Hz, Semitones, Cents}` | |
| 13 | `Tuning reference (Hz)` | One per plugin. |

**The note binding is TWO-WAY, and safe because of the mirror.** Rozaya, on the
readout-only first version: *"So does the note name do anything? cause it needs
to."* Right — a note list you cannot pick from is half a control, and picking a
name instead of knowing that 60 is middle C is the entire point of having names.

Two-way binding is the shape that broke **Womb** in August — its `Every N beats`
value and the heart's BPM readout each held the same fact, either could be moved,
and the code had to guess which. (Not to be confused with the *other* August
fault, the Sweeping Filter's, which was about a tracker being adopted in
`@slider` and capturing a default. Different bug.) It is safe here for one
specific reason: the **mirror** (`pui_last`) says which end the user
actually moved this pass, so nothing has to guess. REAPER fires `@slider` per
parameter change, so only one end moves at a time, and the mirror is adopted in
`@block` where it cannot capture a default. **The reconciliation runs BEFORE the
banks are captured** — the other order banks the stale half, and the sound lags
the display by one edit.

**Migration note:** the two frequencies now migrate as themselves — `Pitch mode`
= Hz, `Pitch value` = 300. The earlier note-plus-remainder encoding produced
values like `6.335232` on screen and is gone.

**Verified by running it** (`tools/jsfx_run`), not by reading: a fresh instance
is sample-identical to the pre-change plugin, and Hz 300, Semitones 62.3486 and
Cents 6234.86 all produce bit-identical output.

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
| 21 | `Output (dB)` | **NEW, and approved 2026-09-08.** Default 0 dB (no change to any existing instance), range −60…+12. |

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
| 29 | `Drift period unit` `{Breaths, Seconds, Beats}` | **`Breaths`, not the suite's `Cycles`**, from 2026-09-09. A cycle here is one WHOLE breath — all four segments — whichever target is drifted, and the plugin already counts in breaths on Play for / Rest for. Same index, nothing reinterpreted. |
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
| 35 | `Ramp time unit` `{Breaths, Seconds, Minutes, Beats}` |
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
- ~~**No new drift or ramp targets.**~~ **WRONG, and undone 2026-09-09.** I
  wrote that as a scope boundary; it was triage. Rozaya: *"breath gen doesn't
  have pitch as a drift target set at all"* — and **Womb, the same breath with
  the same two filter centres, has had `Inhale Freq` and `Exhale Freq` as drift
  targets all along.** `Inhale pitch` and `Exhale pitch` are now appended to
  both the drift and ramp target lists, taking both to seven.

  **And then REORDERED, 2026-09-09**, because Rozaya established that drift is
  configured in zero instances — verified against all four before touching it —
  so no stored index could be repointed. Both lists now mirror the plugin's own
  controls top to bottom: **Breath rate, Inhale, Top pause, Exhale, Bottom pause,
  Inhale pitch, Exhale pitch.** `Breaths/min` was renamed `Breath rate` to match
  the control it targets. Reordering an enum is normally forbidden; it is safe
  here only because nothing stores an index.

  **The pitch drift is wired but UNPROVEN, and cannot be proven by the runner.**
  Moving a filter centre from 300 Hz to 1200 Hz changes its output by 2.4e-07 —
  the degenerate noise rails the filter to DC, so cutoff is invisible. Drift on
  the two pitch targets measures the same magnitude as setting the pitch by
  hand, which is consistent with it working and is not evidence that it does.
  **This one is an ear test.**

## Build order

1. ~~Rozaya answers the output-level question.~~ **DONE — it goes in.**
2. **Back up first. DONE 2026-09-08**, at Rozaya's request: the three live
   projects to
   `E:/reaper/finished/backups/snapshots/_pre-breathgen-layout-20260908/`, and
   the installed plugin to
   `C:/Users/solst/jsfx-backups/breath_gen.pre-20260908-layout.jsfx`. All four
   copies verified byte-identical to their sources.
3. ~~Build the file at 40 sliders~~ **DONE.**  Was: build at 40 sliders, every new control defaulting to off or to what
   the plugin already means: `Breath unit` Seconds, `Pitch mode` Hz,
   `Fine tune` 0.
4. **Bump the `@serialize` magic in the same commit as the renumber.** That is
   the only thing that made the last accidental renumber in this suite
   repairable.
5. Author the migration from the table above — an exact literal map, with a
   count assertion, using `tools/rpp_sliders.py`. Breath Generator is under 64
   sliders both before and after, so the `""` marker at token index 64 does not
   apply; assert that rather than assume it.
6. Verify by decoding a real project line by control NAME against a
   pre-migration snapshot, not against the table the migration used. Range-check
   every migrated value against its new slider's declared min/max.
7. Ask for an ear test. It is not done until it has been heard.


## What the build turned up that the layout did not predict

Three things only showed up once the code existed, and all three would have been
silent failures.

**The `All` position needed change-detected writes.** The first implementation
wrote the visible controls into both targets on every `@slider` pass, so an
instance parked on `All` would stamp the inhale frequency over the exhale one on
every single load -- and then save the damage. Polyrhythm v3 already solves this
with a per-control mirror that writes only when a value actually moved, plus a
flag adopted in `@block`; that is now copied here. Simulated in both restore
orders before applying.

**`tuning_ref` was unseeded.** `pitch_to_hz()` reads it and is called from
`@block`, which can run before `@slider` ever has. Unseeded it is 0, which puts
every note at 0 Hz and parks both filters on the low clamp.

**The migration's idempotence gate was wrong, and in the dangerous direction.**
It asked "does this line store a slider above 32?", which never trips for
`organic-movement.RPP` because that project stores nothing above slider 24. A
second run would have read the already-migrated slider 5 -- Exhale, a duration
of 10 -- as a frequency. The gate is now the blob magic, which is exact.

**And two of the four instances had no `<JS_SER>` blob at all**, being old enough
to predate serialization here. The migration creates one, or the two frequencies
would have had nowhere to land and both would have reverted to 800/600.

## What to listen for

Nothing should have changed. Every migrated instance keeps its exact
frequencies, durations, fades and stereo settings, and the new controls all
default to off or to what the plugin already meant.

The new capabilities have never been played:

- **`Breath rate`** -- type 10 with Breath unit on Seconds and watch the four
  segments rescale, keeping their ratio; then move one segment and watch the rate
  follow it back.
- **`Breath unit = Beats`** -- the breath should then ride the project tempo.
- **The pitch block** -- this is R22's first outing anywhere. `Pitch target` on
  `All` moving both filter centres together is the path most likely to be used
  and the only one that can change two things at once.
- **`Output (dB)`**.
