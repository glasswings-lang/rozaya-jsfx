# Full Feature Sweeping Filter — authored layout

Written by hand 2026-09-04. **Status: READING ORDER APPROVED BY ROZAYA
2026-09-05. BUILD IN PROGRESS -- renumber and retirements DONE in `src/`,
NOT installed, NO project migrated.**

**What is done:** the 41 sliders are renumbered into the approved order, both
retired controls are DELETED (Host ratio, and the Linked Sweep picker), and
`Filter speed multiplier` has become **`Pan sweep every (cycles)`** with the
reciprocal applied at both read sites. 39 sliders.

**What remains:** the six new drift/ramp controls (drift period unit, drift
play/rest, ramp time unit, ramp play/rest) and their engine wiring; the pan
sweep rate mode gaining Host x in canonical order; then the migration of 20
instances across 11 projects, and installing.** *"Reading order seems OK to me."* Building against it.

**Recorded here on purpose rather than left in a conversation.** Rozaya had in
fact engaged with this order earlier the same day; the thread went sideways into
R20 before anyone said yes, and they later said *"I thought I nodded at it. I
don't remember."* **A decision that only exists in a chat log is a decision
someone has to remember. Write it into the artefact it governs, at the moment it
is made.**

**R20 (2026-09-04) applies to this layout and the rate block below already
satisfies it** — a rate value with its own rate mode, and a pan rate with its
own rate mode, each pair self-contained. Two things it adds:

- **The pan's mode enum must be the canonical `{BPM, Seconds, Hz, Host x}`.**
  Today the pan unit is `{Hz, Seconds, BPM}` — BACKWARDS relative to the Rate
  Mode sitting a few positions above it in this same plugin. All 20 stored
  instances are on `Hz`, so it is a uniform index 0 → 2.
- **No sync switch, no target selector, no separate beats slider.** If a future
  draft of this document grows one, it is wrong; see R20.

**Read `CLAUDE.md`'s one-migration rule before building this.** Everything this
plugin is owed goes in ONE version bump. It has already been migrated twice on
2026-09-04 — Host x values, then the rate-mode enum order — which is the mistake
this document exists to stop repeating. Eleven projects, twenty instances.

---

## Why it needs one

**`Slope` is slider 41, at the very end.** It is one of the four things that
define what this filter *is*, sitting after the drift block. Veil has it at 5,
next to the cutoffs, and Veil's position is the correct one — the plan says the
filters move to match Veil, not the other way round.

**`Pan speed (Linked Sweep)` is at 40, seventeen places from its partner** at 23,
`Filter Speed Multiplier (Linked Sweep)`. They are declared on adjacent lines in
the source; REAPER orders by number, so they read apart. Same fault as the
Tremolo.

**`Resonance` is at 12**, wedged between `Depth %` and a phase offset, away from
the frequencies it shapes.

**Attack and Release are separated from their own shape selectors** — 8, 9, 10,
11 runs Attack %, Release %, Attack Shape, Release Shape.

**`Wet/Dry Mix` is at 15, mid-list.** Global output belongs last in the
plugin's own section, so it stops interrupting the pan group.

**Drift and Ramp are missing six controls Veil has.** No drift period unit, no
drift play/rest, no ramp time unit, no ramp play/rest. The Tremolo already has
drift play/rest and this one does not — the same unpropagated-good-decision
pattern the whole sweep keeps finding.

**The pan rate has no Host x**, which Part 3 lists as owed; Sweep Dwell has it.

**Naming.** Title Case throughout, units outside their parentheses,
`Attack %` not saying percent of what.

---

## What changes, and why each one

1. **`Slope` comes home to 4**, beside the frequencies and resonance, matching
   Veil.
2. **`Resonance` joins the frequency group** at 3.
3. **`Pan speed (Linked Sweep)` is absorbed, not moved.** It is a picker that
   WRITES into the multiplier beside it, not a partner control. Both collapse
   into one honest number — see the section below.
4. **`Wet/dry mix` moves last in the plugin's own section**, at 25.
5. **Attack and Release pair with their shapes.**
6. **Drift and Ramp match Veil exactly** — the built, ear-tested reference —
   which means six new controls: drift period unit, drift play/rest, ramp time
   unit, ramp play/rest.
7. **`Pan sweep rate unit` becomes `Pan sweep rate mode`** and gains **Host x**
   in the canonical `{BPM, Seconds, Hz, Host x}` order.
8. **Sentence case, units in parentheses.**
9. **The retired `Host ratio` is deleted.** Deleting a slider is safe;
   RENUMBERING one is not. See the section below — I had this wrong.

---

## The order

45 controls, all of them live. Six net new; two deleted (the retired `Host
ratio`, and the `Pan speed` picker whose job folds into the control it used to
write into).

| new | control | from |
|---|---|---|
| 1 | Frequency low (Hz) | 1 |
| 2 | Frequency high (Hz) | 2 |
| 3 | Resonance | **12** |
| 4 | Slope (dB/oct) | **41** — comes home, matching Veil |
| 5 | Rate value (BPM / sec / Hz / beats per cycle) | 3 |
| 6 | Rate mode | 4 |
| 7 | LFO start phase (degrees) | 5 |
| 8 | On duration (% of cycle) | 6 |
| 9 | Depth (%) | 7 |
| 10 | Attack (% of cycle) | 8 |
| 11 | Attack shape | 10 |
| 12 | Release (% of cycle) | 9 |
| 13 | Release shape | 11 |
| 14 | Right channel phase offset (degrees) | 13 |
| 15 | Phase mode | 14 |
| 16 | Pan enabled | 16 |
| 17 | Pan mode | 17 |
| 18 | Pan spread (0 = mono, 1 = full) | 18 |
| 19 | Pan glide (ms, 0 = instant) | 19 |
| 20 | Cycle steps (per-cycle modes) | 20 |
| 21 | Pan sweep rate | 21 |
| 22 | Pan sweep rate mode | 22, **gains Host x**, canonical order |
| 23 | **Pan sweep every (cycles)** | **23 + 40 merged** — the multiplier inverts, the picker goes |
| 24 | Wet/dry mix | **15** — global output, last in this section |
| 25 | Start delay (in rate mode units) | 24 |
| 26 | Play for (cycles) | 25 |
| 27 | Rest for (cycles) | 26 |
| 28 | LFO at rest | 27 |
| 29 | Output at rest | 28 |
| 30 | Drift target | 34 |
| 31 | Drift up amount (units match target) | 35 |
| 32 | Drift down amount (units match target) | 36 |
| 33 | Drift period | 37 |
| 34 | Drift period unit (Seconds / Beats) | **NEW** |
| 35 | Drift shape | 38 |
| 36 | Drift play for (periods, 0 = always) | **NEW** |
| 37 | Drift rest for (periods, 0 = always) | **NEW** |
| 38 | Ramp target | 29 |
| 39 | Ramp by (units match target) | 30 |
| 40 | Ramp time unit | **NEW** |
| 41 | Ramp duration | 31 |
| 42 | Ramp play for (0 = smooth) | **NEW** |
| 43 | Ramp rest for (0 = smooth) | **NEW** |
| 44 | Ramp engage | 32 |
| 45 | Ramp start delay | 33 |

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

**One `.RPP` pass.** Twenty instances across eleven projects — the second-most
used plugin in the suite after Polyrhythm, so this is the one to be slowest and
most careful about.

- Authored permutation, exact table, line and instance counts asserted before
  any write.
- **All six new controls seed to 0**, which is off in every case: no period
  unit change (0 = Seconds), gates disabled, ramp in minutes. A migrated project
  sounds exactly as it did.
- **`Pan sweep rate mode` needs a value remap as well as a move**, `{Hz,
  Seconds, BPM}` → `{BPM, Seconds, Hz, Host x}`: Hz 0 → 2, BPM 2 → 0. All twenty
  instances measured on Hz as of 2026-09-04, but the table covers all three,
  because "they are all on the default" expires the moment someone changes one.
- Verify by decoding before and after **by control name**, with an authored
  rename table for the labels that change in the same pass. Never against the
  table the migration used.

## Still owed after this, and deliberately not folded in

- **R12 ranges and R17 units** — `Resonance`, `Depth %`, `Pan spread` and
  `Wet/dry mix` all want the suite-wide range and unit decisions, which need the
  `0..1` inventory authored first.
- **The Pan Mode reorder (R19)**, frozen until the whole suite does it at once.
- **`Slope`'s twin in Sweep Dwell** (slider 42) moves in that plugin's own pass,
  not this one.
