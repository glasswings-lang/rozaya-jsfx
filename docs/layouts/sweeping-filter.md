# Full Feature Sweeping Filter — authored layout

Written by hand 2026-09-04, not generated. **Status: order drafted, awaiting
review. Nothing built.**

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
3. **`Pan speed (Linked Sweep)` comes home** to sit after
   `Filter speed multiplier (Linked Sweep)`.
4. **`Wet/dry mix` moves last in the plugin's own section**, at 25.
5. **Attack and Release pair with their shapes.**
6. **Drift and Ramp match Veil exactly** — the built, ear-tested reference —
   which means six new controls: drift period unit, drift play/rest, ramp time
   unit, ramp play/rest.
7. **`Pan sweep rate unit` becomes `Pan sweep rate mode`** and gains **Host x**
   in the canonical `{BPM, Seconds, Hz, Host x}` order.
8. **Sentence case, units in parentheses.**
9. **The retired `Host ratio` parks at the end**, hidden. Not deleted — ids are
   primary keys.

---

## The order

46 controls, all of them live. Six net new, one deleted (the retired `Host
ratio`).

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
| 23 | Filter speed multiplier (Linked Sweep) | 23 |
| 24 | Pan speed (Linked Sweep) | **40** — comes home to its partner |
| 25 | Wet/dry mix | **15** — global output, last in this section |
| 26 | Start delay (in rate mode units) | 24 |
| 27 | Play for (cycles) | 25 |
| 28 | Rest for (cycles) | 26 |
| 29 | LFO at rest | 27 |
| 30 | Output at rest | 28 |
| 31 | Drift target | 34 |
| 32 | Drift up amount (units match target) | 35 |
| 33 | Drift down amount (units match target) | 36 |
| 34 | Drift period | 37 |
| 35 | Drift period unit (Seconds / Beats) | **NEW** |
| 36 | Drift shape | 38 |
| 37 | Drift play for (periods, 0 = always) | **NEW** |
| 38 | Drift rest for (periods, 0 = always) | **NEW** |
| 39 | Ramp target | 29 |
| 40 | Ramp by (units match target) | 30 |
| 41 | Ramp time unit | **NEW** |
| 42 | Ramp duration | 31 |
| 43 | Ramp play for (0 = smooth) | **NEW** |
| 44 | Ramp rest for (0 = smooth) | **NEW** |
| 45 | Ramp engage | 32 |
| 46 | Ramp start delay | 33 |

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
