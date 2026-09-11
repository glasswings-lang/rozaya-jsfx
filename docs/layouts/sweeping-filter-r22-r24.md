# Sweeping Filter — the pitch blocks, Tuning reference and 17 targets

Authored 2026-09-10, before building. One migration for everything here.

## What Rozaya decided (quoted), and what is mine

- Two full pitch blocks, Low and High, the shape Sweep Dwell already has. Asked
  "Does two full sets, Low and High, sound right to you?" — *"Yes, and please
  make sure the tuning refference code works, that's a problem. and it needs to
  work across all of the plugins of course"*.
- Tuning reference straight after both pitch blocks, in BOTH filters; Tensor's
  unmigrated filters folded into this migration; Heartbeat's blow-up fixed.
  Asked all three together — *"ewww, yeah, fix all of that."*
- **Mine, not settled by Rozaya:** the target list and its order (control order,
  as Polyrhythm v3 and Melody did), respacing the banks, the names of the new
  targets, and treating a pitch target's amount in the pitch value's own unit.
  R22's unquoted "more than one pitch goes behind a Pitch target selector" is
  NOT followed here; Rozaya chose two full sets.

## The order — 54 controls (was 45)

| new | control | from |
|---|---|---|
| 1 | Low pitch mode {Hz, Semitones, Cents} | NEW, default Hz |
| 2 | Low note name | NEW, default 71 (B4), shown in Semitones only |
| 3 | Low frequency (Hz / semitones / cents) | 1 (`Frequency Low Hz`), range widened to 0–20000 step 0.001 |
| 4 | Low fine tune | NEW, default 0 |
| 5 | Low fine tune unit {Hz, Semitones, Cents} | NEW, default Cents |
| 6 | High pitch mode | NEW, default Hz |
| 7 | High note name | NEW, default 111 |
| 8 | High frequency (Hz / semitones / cents) | 2 (`Frequency High Hz`) |
| 9 | High fine tune | NEW |
| 10 | High fine tune unit | NEW, default Cents |
| 11 | Tuning reference (Hz) | NEW, 440, 20–2000 |
| 12–38 | Resonance … Output at rest | 3–29, each +9, unchanged |
| 39–46 | Drift target … Drift rest for | 30–37, each +9 |
| 47–54 | Ramp target … Ramp start delay | 38–45, each +9 |

Declarations and every code reference move with `tools/jsfx_renumber.py apply`
using the map `1:3, 2:8, 3-45:+9`; the nine new controls are then added by hand.

Names are Sweep Dwell's, word for word, so the siblings read the same.

## Drift and Ramp targets — 17, in control order (was 6)

| new idx | target | old idx | amount is in |
|---|---|---|---|
| 0 | Low frequency | 1 | the Low pitch mode's unit |
| 1 | Low fine tune | — | the Low fine tune unit |
| 2 | High frequency | 2 | the High pitch mode's unit |
| 3 | High fine tune | — | the High fine tune unit |
| 4 | Tuning reference | — | Hz, clamped 20–2000 |
| 5 | Resonance | 4 | 0–1 |
| 6 | Rate value | 0 (`Sweep Rate`) | unchanged: the rate mode's unit |
| 7 | On duration | — | % of cycle, 0–100 |
| 8 | Depth | — | %, 0–100 |
| 9 | Attack | — | % of cycle, 0–100 |
| 10 | Release | — | % of cycle, 0–100 |
| 11 | R channel phase offset | — | degrees, wraps round the circle |
| 12 | Pan spread | — | 0–1 |
| 13 | Pan glide | — | ms, 0–1000 |
| 14 | Pan sweep rate | 3 | unchanged |
| 15 | Pan sweep every | — | cycles, min 0.001 |
| 16 | Wet/dry | 5 | 0–1 |

Old index → new: `0→6, 1→0, 2→2, 3→14, 4→5, 5→16`. Applied to the Drift target
and Ramp target slider values by the migration, and to the saved blob by the
PLUGIN on reading an old magic, so a blob and its selector always agree.

A frequency target's amount is added to the pitch VALUE before conversion, so in
Hz mode it is Hz exactly as before and the sum happens in the same order
(`value + drift + ramp`), which is what keeps migrated projects bit-identical.
Each end now drifts on its own; before, drift applied after sorting low/high.
Those differ only when Low is set above High, and no saved instance does.

## Save format

`N_TARGETS` 6 → 17. Banks respaced from 16 to 32 slots so they do not overlap.
Magic `2200006` → `2300017`. The plugin still READS `2200006` and `2100006`:
it reads six into each bank, resets all 17 to defaults, then places the six at
their new indices, and remaps `last_target_select` / `last_sr_target`.

## Which instances, measured 2026-09-10

- **E:/reaper, 20 instances in 11 files**, all on the 45-control layout. 17 have a
  blob; organic-movement's 3 (to-play-with-later) have none.
- **E:/tensor's-rpp-projects, 5 instances, never migrated before.**
  - `organic-movement.RPP`, 3: 23 values = the layout of `ae4a655` (2026-04-18).
  - `shepard.RPP`, `singing-bowl.RPP`, 1 each: 22 values = the first release
    `d19873f`, which had no LFO start phase. REAPER header dates: 2026-04-09 and
    2026-03-30. Decoded by that layout every value is in range; decoded by the
    later one, Release shape reads 0.7 and Resonance -180, so the layout is not
    in doubt.
  - All three predate the honest-Hz change (`ce3f391`), the rate-mode reorder and
    the September 5 reorder, so they take every step: the old corner correction
    from `sweepfilter_migrate_hz.py`, rate and pan units `{Hz, Seconds, BPM}` →
    canonical (0→2, 1→1, 2→0), the Linked Sweep multiplier inverted into
    `Pan sweep every`, then this layout. Decoded by control NAME.
- **Sweep Dwell** is renumbered in `src/` only (Tuning reference 55 → 11). Its
  projects still wait on its Cycle mode question; its migration will be written
  against the 55-control layout with the reference at 11.

## Verification, before it is called done

- `tools/jsfx_renumber.py verify` on the pure renumber step.
- Old build on each snapshot project against new build on the migrated project,
  noise in, bit-identical, every E:/reaper instance, non-silent.
- `tools/tuning_ref_check.py` gains the Sweeping Filter.
- Each new target: a drift on it changes the output; each remapped old target:
  covered by the projects whose blobs have drift or ramp set.
- Tensor's five: decoded by name against the old layout, and the organic-movement
  three against Rozaya's already-migrated copy of the same project.
