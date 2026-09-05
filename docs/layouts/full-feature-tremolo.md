# Full Feature Tremolo — authored layout

Written by hand 2026-09-04, not generated. **Status: order drafted, awaiting
review. Nothing built.**

This is the artefact that gets reviewed before anything is touched, and reviewing
a reading order needs no code reading — which is exactly why it exists.

**Read `CLAUDE.md`'s rule on this first if you are about to build it:** everything
this plugin is owed goes in ONE version bump and ONE migration. The Tremolo has
already been migrated twice on 2026-09-04 (Host x values, then the rate-mode
enum order) and that was the mistake this document exists to stop repeating.

---

## Why it needs one

**Six controls are stranded at the end of the list, away from the blocks they
belong to.** They were appended as they were invented, which is the ordering
problem the whole sweep is about:

| stranded at | control | belongs with |
|---|---|---|
| 35 | `Pan speed (Linked Sweep)` | 18, `Filter Speed Multiplier (Linked Sweep)` — its partner |
| 36, 37 | `Drift play for` / `Drift rest for` | the Drift block at 29–33 |
| 38 | `Ramp time unit` | the Ramp block at 24–28 |
| 39, 40 | `Ramp play for` / `Ramp rest for` | the same |

The `Pan speed` one is the sharpest: it and `Filter Speed Multiplier` are
declared on adjacent lines in the source and read **seventeen apart**, because
REAPER orders by slider number and not by file position. The plan names this one
specifically.

**Attack and Release are separated from their own shape selectors.** The order
runs Attack %, Release %, Attack Shape, Release Shape — so setting an attack
means passing the release to reach its shape. A modifier belongs immediately
after the thing it modifies.

**Drift has no period unit.** Veil can count a drift period in beats; the
Tremolo cannot. Same feature, one plugin has it.

**The pan rate has no Host x.** Sweep Dwell's pan rate can follow the tempo and
this one cannot, which Part 3 of the plan already lists as owed.

**Naming.** Title Case throughout (`On Duration % of Cycle`, `Depth dB`) against
the suite's sentence case, and units outside their parentheses. `Attack %` does
not say percent of what.

---

## What changes, and why each one

1. **`Pan speed (Linked Sweep)` is absorbed, not moved.** It was never a
   partner control — it is a picker that WRITES into the multiplier beside it.
   Both collapse into one honest number. See the section below; this was the
   thing I described wrongly in the first draft.
2. **Drift and Ramp become contiguous and match Veil's order**, which is the
   built, ear-tested reference for both blocks: target → up → down → period →
   period unit → shape → play → rest, and target → by → time unit → duration →
   play → rest → engage → start delay.
3. **Attack and Release pair with their shapes.**
4. **Drift gains a period unit** (`Seconds / Beats`), matching Veil.
5. **`Pan sweep rate unit` becomes `Pan sweep rate mode`** and gains **Host x**,
   in the canonical `{BPM, Seconds, Hz, Host x}` order. R7 standardises on
   *mode*, not *unit*, for the secondary rates.
6. **Sentence case, units in parentheses**, `Attack (% of cycle)`.
7. **The retired `Host ratio` is deleted.** It is inert, and keeping it would
   cost a dead control to walk past forever. Deleting a slider is safe;
   RENUMBERING one is not. See the section below — I had this wrong.

---

## The order

39 controls, all of them live. One net new (`Drift period unit`); two deleted
(the retired `Host ratio`, and the `Pan speed` picker whose job folds into the
control it used to write into).

| new | control | from |
|---|---|---|
| 1 | Rate value (BPM / sec / Hz / beats per cycle) | 1 |
| 2 | Rate mode | 2 |
| 3 | On duration (% of cycle) | 3 |
| 4 | Depth (dB) | 4 |
| 5 | Attack (% of cycle) | 5 |
| 6 | Attack shape | 7 |
| 7 | Release (% of cycle) | 6 |
| 8 | Release shape | 8 |
| 9 | Stereo phase offset (degrees) | 9 |
| 10 | Phase mode | 10 |
| 11 | Pan enabled | 11 |
| 12 | Pan mode | 12 |
| 13 | Pan spread (0 = mono, 1 = full) | 13 |
| 14 | Pan glide (ms, 0 = instant) | 14 |
| 15 | Cycle steps (per-cycle modes) | 15 |
| 16 | Pan sweep rate | 16 |
| 17 | Pan sweep rate mode | 17, **gains Host x**, canonical order |
| 18 | **Pan sweep every (cycles)** | **18 + 35 merged** — the multiplier inverts, the picker goes |
| 19 | Start delay (in rate mode units) | 19 |
| 20 | Play for (cycles) | 20 |
| 21 | Rest for (cycles) | 21 |
| 22 | LFO at rest | 22 |
| 23 | Output at rest | 23 |
| 24 | Drift target | 29 |
| 25 | Drift up amount (units match target) | 30 |
| 26 | Drift down amount (units match target) | 31 |
| 27 | Drift period | 32 |
| 28 | Drift period unit (Seconds / Beats) | **NEW** — Veil has it |
| 29 | Drift shape | 33 |
| 30 | Drift play for (periods, 0 = always) | **36** |
| 31 | Drift rest for (periods, 0 = always) | **37** |
| 32 | Ramp target | 24 |
| 33 | Ramp by (units match target) | 25 |
| 34 | Ramp time unit | **38** |
| 35 | Ramp duration | 26 |
| 36 | Ramp play for (0 = smooth) | **39** |
| 37 | Ramp rest for (0 = smooth) | **40** |
| 38 | Ramp engage | 27 |
| 39 | Ramp start delay | 28 |

---

## The retired `Host ratio` is DELETED, not parked

An earlier draft of this document kept it in the list, hidden, on the reasoning
that "ids are primary keys and can never be renumbered". Rozaya: *"host ratio.
can't be deleted? why."*

It can. Two different things were being conflated:

- **Renumbering** a slider is dangerous, because REAPER restores by position and
  everything above it shifts. That rule is real and is why this document exists.
- **Deleting** one is not. The id is written explicitly (`sliderN:`), so removing
  the declaration simply leaves N unused. An old project still has a value at
  that position; REAPER hands it to a slider that is not there and it is ignored.

**The suite already does this.** `heartbeat gen` declares 1-16, then 21-25, then
29-35: ids 17-20 and 26-28 were retired by deletion in the v2.14 reorg and the
gaps have been sitting there ever since, harmlessly.

So the picker goes. Keeping it would have cost a dead control that a screen
reader has to walk past forever, in exchange for nothing -- it is already inert.
And since this layout renumbers everything anyway, deleting it does not even
leave a gap.

**This applies to the other six plugins whose pickers were retired on
2026-09-04** -- Stereo Phaser, Resonance Bank (never had one), Rhythm Track,
Shepard Tone, Shepard Scale, Heartbeat, Sweep Dwell. Each should delete its
picker in its own reorder pass rather than carrying a hidden corpse.

---

## `Linked Sweep` loses its multiplier and its picker — added 2026-09-04

**What it does, since the names do not say.** Linked Sweep is a pan mode where
the pan is locked to this plugin's own cycle. One line does it:
`pan_phase += (freq * pan_sweep_ratio) / srate`. At 1 the pan makes one full
left-to-right pass per cycle; at 2 it makes two; at 0.25 it takes four cycles to
cross once. The lock holds whatever the rate does — drift it, ramp it, sync it to
the host, and the pan follows in proportion.

**The two controls are not a pair. One writes the other.** `Filter speed
multiplier (Linked Sweep)` is the real value, a MULTIPLIER in 0.125 steps.
`Pan speed (Linked Sweep)` is a named picker that writes into it, so you can
choose "every 4 cycles" instead of typing 0.25.

**Which is the exact shape R13-revised deleted everywhere else on 2026-09-04:**
a multiplier you cannot hear without arithmetic, plus a picker that writes into
it to hide the arithmetic. It is a milder case than Host x was — "every 4 cycles"
is at least audible, where "0.25x the tempo" is not — but it is the same fault,
and the picker-writes-a-value shape is what caused the `infantile.RPP` bug.

Rozaya, 2026-09-04: *"I don't actually know what that one does. It seems right,
but I don't know what it does in practice."* Then, on hearing what it was:
*"I've never used it and I've never liked it being the current way BECAUSE of
that exact thing."*

**The replacement, following R13 exactly.** Both controls collapse into one:

    Pan sweep every (cycles)     0.001 - 1000, step 0.001, default 1

Bigger is slower, the same direction as Seconds and beats-per-cycle. Say it
aloud with its value and it finishes the sentence: *"pan sweep every 4 cycles"*,
*"pan sweep every 0.25 cycles"*. No menu, nothing writing into anything else,
and thirds become reachable — the 0.125 grid cannot express "every 3 cycles",
which is why that entry is missing from the picker today.

**MEASURED FREE, 2026-09-04.** Across the whole library, every instance of all
three plugins carrying this pair — 11 Tremolo, 20 Sweeping Filter, 1 Sweep Dwell
— has the multiplier at **1** and the picker untouched. So the reciprocal
conversion is 1 -> 1: not one saved value changes, and the picker can be deleted
with nothing stored on it. That window is open now and closes the moment anyone
uses it.

**Sweep Dwell has the identical pair** (sliders 20 and 41) and gets the same
treatment in its own reorder pass, not this one.

---

## The migration

**One `.RPP` pass, and it is the only one this plugin should need.** Eleven
instances across the library.

- The permutation above is authored, not inferred. Applied by an exact table,
  with line and instance counts asserted before anything is written.
- **`Drift period unit` (new 29) seeds to 0 = Seconds**, which reproduces
  today's behaviour exactly — the period has always been in seconds here.
- **`Pan sweep rate mode` (new 17) needs a value remap as well as a move.** Its
  enum goes `{Hz, Seconds, BPM}` → `{BPM, Seconds, Hz, Host x}`, so a stored
  Hz (0) becomes 2 and a stored BPM (2) becomes 0. Measured 2026-09-04: all
  eleven instances are on Hz, so in practice this is 0 → 2 eleven times — but
  the table handles all three, because "they are all on the default" is a fact
  with an expiry date.
- Verify by decoding before and after **by control name**, never against the
  table the migration used, with an authored rename table for the controls
  whose labels change in the same pass.

## Still owed after this, and deliberately not folded in

- **R12 ranges and R17 units.** `Pan spread` is `0..1`, `Depth dB` is `-60..0`.
  Those are suite-wide decisions with their own migration shape, and pulling
  them in here would mean authoring the `0..1` inventory first.
- **The Pan Mode reorder (R19).** Frozen until the whole suite does it at once,
  by Rozaya's own decision, so it stays out.
