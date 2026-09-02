# Open bugs

Things that are known-broken and NOT fixed. Newest first. A bug leaves this file
only when it has been fixed *and* heard.

---

## 1. Melody Phase durations were wrong in `upswing` and `outcoming`

**Status: CAUSE FOUND, REPAIRED, NOT YET HEARD.** (2026-09-02)

### What it actually was

**A slider was inserted in the MIDDLE of the list.** Commit `ac7f125`
(2026-07-02, "Speed Ramp reaches all 28 targets") added `Ramp target` at
position **67**, taking the count 75 → 76 and pushing every control above it up
one place:

A value sits at a fixed POSITION in the saved line. The old plugin wrote position
P meaning its slider P; the new plugin reads position P as its slider P — and
every new slider from 68 up means what the old slider *below* it meant. So each
saved value is now read as the control one place down the list:

| position | the value there means (old) | the plugin now reads it as (new) |
|---|---|---|
| 67 | Speed ramp by | Ramp target |
| 68 | Speed ramp duration | Ramp by |
| 69 | Speed ramp engage | Ramp duration |
| 70 | Speed ramp start delay | Ramp engage |
| 71 | Drift target | Ramp start delay |
| 72 | Drift up | Drift target |
| 73 | Drift down | Drift up |
| **74** | **Drift period (default 8)** | **Drift down** |
| **75** | **Drift shape (0)** | **Drift period** |

REAPER restores by POSITION, so any project saved before that date fed the
**default Drift period of 8 into `Drift down`**, and Drift shape's 0 into
`Drift period`. In `@sample` the drift gate is `(up > 0 || down > 0)` — which
went **TRUE on a plugin drift was never configured on** — and the period is
`max(per, 1)`, so it became **one cycle**. Result: the rate swung downward by up
to 8 units **every single cycle**. At `upswing`'s 15 BPM that is the rate
lurching between 15 and 7 BPM, note by note.

Rozaya's localisation was exact: *"it's in the passage from one note to the
next"* — that is precisely where `cur_step` is sampled.

### Which projects, and how it was told apart

The same commit bumped the `@serialize` magic `1000000+N` → `2100000+N`, so the
blob's leading float32 is an **exact** gate needing no guesswork:

| project | blob magic | layout | affected |
|---|---|---|---|
| `upswing` | 1000028 | old (75) | **yes — 17 instances** |
| `outcoming` | 1000028 | old (75) | **yes — 19 instances** |
| `melodic` | 2100028 | current | no |
| `simple-sequence` | 2100028 | current | no |
| `slow-summer` | *(no blob)* | stores nothing ≥ 67 | no |

Every blob's drift bank reads `up=0, down=0, per=8, shape=0` — the pristine
`@init` default. **Drift was never configured by hand anywhere.** The `8` in the
slider line was always the default Drift period, sitting one slot too low.

Because the magic mismatched, `@serialize`'s restore branch was skipped
entirely — including the `slider73..76 ← bank` correction at its end — so the
shifted slider line won and `@slider` captured `Drift down = 8` into the bank.

### The repair

`tools/melody_migrate_drift_shift.py` — shifts old sliders 67–75 → 68–76 and
seeds the new slider 67 (`Ramp target`) to **0 = Rate Value**, which is what the
old single-target Speed Ramp always acted on, so the project still sounds like
itself. The blob is **not** touched (its banks are all defaults; REAPER rewrites
it in the current format on the next save).

Applied to 36 instances across the two projects. Snapshot first:
`E:\reaper\_pre-drift-shift-20260902`.

Verified by `tools/melody_verify_drift_shift.py`: **5643 checks, 0 failures** —
sliders 1–66 byte-identical, each old N landing at N+1, the seed present, every
value inside its declared range, the drift block agreeing with the instance's own
untouched blob, and no non-melody line altered. Hand-read afterwards: `upswing`
tracks 3 and 4 now show **drift active `True → False`**, with Start delay (0 and
8) and all eight step lengths unchanged; the migrated tail
`8 0 0 0 0 0 0 0 0 0 8 0` is now the same shape as `melodic`'s known-good line.

### Two process failures worth keeping

1. **"byte-identical to the backup" proved nothing.** Rozaya rejected it
   correctly: if the snapshot were taken *after* damage, both would agree and
   both be wrong. What actually settled it was cracking the files open and
   **range-checking the contents** — `Drift period = 0` against a declared
   minimum of 1 is the whole finding, and it took one look.
2. **The first run of the migration silently ate a line per instance.**
   `rpp_sliders._split` only preserved a trailing `\r`, so a caller using
   `splitlines(keepends=True)` got a rendered line with no ending, which welded
   itself onto the block's closing `>`. The verifier caught it (`line count
   changed: 919 -> 902`); the projects were restored from the snapshot and the
   run redone. **A clean script exit is not evidence.** Both the caller and
   `_split` are fixed, and the migration now refuses to write if the line or
   instance count would change.

### It was SIX plugins, not one

I wrote "Melody Phase is the only plugin this happened to" here and in CLAUDE.md
before running the audit. That was false and the audit took two minutes. The same
2026-07-02 pass inserted `Speed ramp target` mid-list in **six** plugins:

| plugin | commit | sliders | insert at |
|---|---|---|---|
| `melody_phase` | `ac7f125` | 75 → 76 | 67 |
| `Full_Feature_Tremolo` | `d062bc6` | 32 → 33 | 24 |
| `full-feature-sweeping-filter` | `d062bc6` | 37 → 38 | 29 |
| `rhythm-track` | `03470b5` | 25 → 26 | 18 |
| `shepard-scale` | `9c04c4a` | 60 → 61 | 53 |
| `shepard-tone` | `0e57cae` | 72 → 73 | 65 |

Measured against the real library, the damage beyond Melody was **one instance**:
the **Full Feature Tremolo in `upswing`**, carrying the identical `Drift down = 8,
Drift period = 0`. Migrated by `tools/migrate_speedramp_insert.py` (the general
form, with a per-plugin table and the same gate). The Tremolo in `playing-around`
and the three Sweeping Filters in `organic-movement` store nothing at or above
their insert points, so there was nothing to move. `rhythm-track`,
`shepard-scale` and `shepard-tone` appear in **zero** projects.

`tools/scan_slider_ranges.py` now range-checks every stored value in every
project against the INSTALLED plugin. Across the library that is **18063 values**;
after these repairs, **5** remain out of range and none of them is a Speed Ramp
shift. Absence of a range hit is not proof of absence — a shift hides completely
when every value happens to fit — so the blob magic stays the primary gate.

### Still to do

1. **Ear-test `upswing` and `outcoming`.**
2. The five surviving range hits, all pre-existing and none investigated:
   - `nothing to fear.RPP` — Morpher `Stereo width (%) = 300` in a 0–100 control
     (×2). 300 does not fit slider 14 under *either* Morpher layout, so this is
     not simply an un-run reorder migration.
   - `half-music-half-wind.RPP` — Morpher `Ramp duration = 120` in a 0–60 control
     (×2).
   - `womb-and-baby-heartbeats-with-bloodflow.RPP` — Womb v3 `Host sync target = 8`
     against a single-option enum declared `<0,0,1{Heart rate}>`. Clamps to the
     only option, so low impact.
   Both Morpher projects are in `to-play-with-later`, not `finished`.

---

## 2. Melody Phase instances come in out of alignment on project open

**Status: OPEN, but much smaller than it looked.** Cause unknown.

### What is left of it

Bug 1 above was the loud half and is gone. What remains is the report against
**`simple-sequence`** specifically: 12 instances, all synced, every Start delay
0, tempo 205 — arriving at slightly different times on project open, with a
play/stop curing it. `simple-sequence` was **never** affected by the slider
shift (blob magic 2100028), so this is a separate, quieter fault.

The `upswing` half of the original report — *"drifting as if the clocks are
slightly off"* — is now believed to have been Bug 1, and should be re-listened
to before any more work is done here.

### What is known

- A play/stop cures it; renders were always fine. Both are explained by `@init`
  re-running on every instance on the same sample at the transport edge, which
  is currently the **only** shared time origin the sequencer has.
- Melody's `@sample` has no `play_state` test anywhere, so each instance's
  sequence starts at *its own* instantiation moment. Only `polyrhythm_phase` and
  `_v3` have such a test; fourteen other plugins with sync do not.
- `simple-sequence`'s real step is `(1/0.5) ÷ (205/60)` = **0.585 s**, so a small
  absolute offset is a large fraction of a step — which is why it is audible
  there and was not elsewhere.

### Theories already burned — do not resubmit

1. **"The sequence-placement feature is not firing."** Rejected: placement only
   ran under Host x, and it did not explain `upswing`.
2. **"`@init` zeroes the placement gate on every play."** Real, but introduced
   2026-09-02 and fixed in `3b42f07`; it postdates the report.
3. **"Hold the sequencer until the transport moves."** Shipped and **reverted**
   (`dcfeead`). **A fix of this shape is forbidden** — Rozaya must be able to
   hear the plugin with the transport stopped: *"now you take that away for
   what? To force me to play the project if I wanna hear something happening.
   No."*

### A real defect found while looking, not yet shown to be this bug

In the installed pre-reorder build, `@block` line 1166 reads

```
host_scale = rate_mode == 3 ? host_bpm / 60 : 1;
```

`rate_mode` is a **`@slider`-derived variable** (line 797), not a raw slider
read. The post-reorder build reads raw sliders in `@block` instead
(`seq_synced = (slider3 > 0.5) && slider4 < 0.5`), deliberately. So in the
installed build, during any window where `@slider` has only run with defaults
(Rate Mode default is **1, Seconds**), `host_scale` is 1 rather than 3.417 and a
synced sequencer runs 1.7× too slow until the real value lands.
`start_delay_elapsed += host_scale / srate` (line 1316) is wrong in the same
window. **Already fixed by construction in the new build.** Status: PREDICTED,
not proved to be this symptom's cause.

### The next honest step

Re-listen to `simple-sequence` now that Bug 1 is out of the way, and confirm the
symptom still exists at all. If it does, the discriminator is **track order**: if
the cause is instantiation order, the first melody track has been running longest
and should LEAD, monotonically through to the last. If the order is scattered, it
is something else.

### Discipline note

Three wrong mechanisms were stated as findings on this bug in one day, and a
fourth nearly was. The rule the project already carries — *a plausible mechanism
is not a finding; ask what else produces exactly this symptom* — is the one that
was not followed. Rozaya's framings are the tests to apply: **"read and compare,
don't script"**, and **"verify the output, not the run."** Both of them caught a
real error here that reasoning did not.
