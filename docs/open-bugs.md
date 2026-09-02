# Open bugs

Things that are known-broken and NOT fixed. Newest first. A bug leaves this file
only when it has been fixed *and* heard.

---

## 1. Melody Phase instances come in out of alignment on project open

**Status: OPEN, and much smaller than it looked.** Cause unknown.

### What is left of it

The loud half of the original report was the 2026-07-02 slider-insert bug — drift
switching itself on in projects that never used it — which is fixed and
ear-confirmed (see *Recently closed* below). What remains is the report against
**`simple-sequence`** specifically: 12 instances, all synced, every Start delay 0,
tempo 205, arriving at slightly different times on project open, with a play/stop
curing it.

`simple-sequence` was **never** affected by the slider shift (its blob magic is
2100028, the current format), so this is a separate, quieter fault.

**The `upswing` half of the original report is now believed to have been the
drift bug and should be treated as withdrawn** unless it is heard again.

### What is known

- A play/stop cures it; renders were always fine. Both follow from `@init`
  re-running on every instance on the same sample at the transport edge, which is
  currently the **only** shared time origin the sequencer has.
- Melody's `@sample` has no `play_state` test anywhere, so each instance's
  sequence starts at *its own* instantiation moment. Only `polyrhythm_phase` and
  `_v3` have such a test; fourteen other plugins with sync do not.
- `simple-sequence`'s real step is `(1/0.5) ÷ (205/60)` = **0.585 s**, so a small
  absolute offset is a large fraction of a step — which is why it would be
  audible there and not in a project with 4-second steps.

### Theories already burned — do not resubmit

1. **"The sequence-placement feature is not firing."** Rejected: placement only
   ran under Host x, and it did not explain `upswing`.
2. **"`@init` zeroes the placement gate on every play."** Real, but introduced
   2026-09-02 and fixed in `3b42f07`; it postdates the report.
3. **"Hold the sequencer until the transport moves."** Shipped and **reverted**
   (`dcfeead`). **A fix of this shape is forbidden** — Rozaya must be able to
   hear the plugin with the transport stopped: *"now you take that away for what?
   To force me to play the project if I wanna hear something happening. No."*

### A real defect found while looking, not shown to be this bug

In the installed pre-reorder build, `@block` line 1166 reads

```
host_scale = rate_mode == 3 ? host_bpm / 60 : 1;
```

`rate_mode` is a **`@slider`-derived variable** (line 797), not a raw slider read.
The post-reorder build reads raw sliders in `@block` instead
(`seq_synced = (slider3 > 0.5) && slider4 < 0.5`), deliberately. So in the
installed build, during any window where `@slider` has only run with defaults
(Rate Mode default is **1, Seconds**), `host_scale` is 1 rather than 3.417 and a
synced sequencer runs 1.7× too slow until the real value lands.
`start_delay_elapsed += host_scale / srate` (line 1316) is wrong in the same
window. **Already fixed by construction in the new build.** Status: PREDICTED,
not proved to be this symptom's cause.

### The next honest step

Re-listen to `simple-sequence` now the drift bug is out of the way, and confirm
the symptom exists at all. If it does, the cheapest discriminator is **track
order**: if the cause is instantiation order, the first melody track has been
running longest and should LEAD, monotonically through to the last. A scattered
order means it is something else.

---

## Recently closed

### The 2026-07-02 mid-list slider insert — FIXED and HEARD (2026-09-02)

A slider (`Speed ramp target`) was inserted in the MIDDLE of six plugins' lists,
so every project saved before that day read each stored value as the control one
place down. `Drift period`'s default of 8 landed on `Drift down` and `Drift
shape`'s 0 landed on `Drift period`, which made the drift gate
`(up > 0 || down > 0)` go true at a one-cycle period on plugins nobody had ever
configured drift on — the rate swinging down by up to 8 units every cycle.

Repaired in `9a84e87`: 37 instances (36 Melody Phase across `upswing` and
`outcoming`, 1 Full Feature Tremolo in `upswing`). Ear-confirmed by Rozaya the
same day — *"Melody phase sounds back to normal."*

Full writeup, the six affected plugins, the audit command and the process
failures are in **CLAUDE.md** under the JSFX gotchas. Tools:
`scan_slider_ranges.py`, `migrate_speedramp_insert.py`,
`melody_migrate_drift_shift.py`, `melody_verify_drift_shift.py`.

**Still outstanding from that sweep — five pre-existing range hits, none
investigated:**

- `nothing to fear.RPP` — Morpher `Stereo width (%) = 300` in a 0–100 control
  (×2). 300 does not fit slider 14 under *either* Morpher layout, so this is not
  simply an un-run reorder migration.
- `half-music-half-wind.RPP` — Morpher `Ramp duration = 120` in a 0–60 control (×2).
- `womb-and-baby-heartbeats-with-bloodflow.RPP` — Womb v3 `Host sync target = 8`
  against a single-option enum declared `<0,0,1{Heart rate}>`. Clamps to the only
  option, so low impact.

Both Morpher projects are in `to-play-with-later`, not `finished`.
