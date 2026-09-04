# Open bugs

Things that are known-broken and NOT fixed. Newest first. A bug leaves this file
only when it has been fixed *and* heard.

---

## 2. Shepard Tone / Shepard Scale — CLOSED, prediction refuted by ear

**Status: NOT A BUG. Tested 2026-09-04 by Rozaya and closed the same day.**
*"The two plugins that are in there now are fine. Tested scale. Whatever other
versions exist, the ones in the glasswings folder are fine."*

**Do not re-apply the rename.** A change was written, reverted, and is not to
be restored: commit `1cc177d`, left in history deliberately.

### What was true, and is still true

`NUM_OSC` and `num_osc` in both plugins differ only by case, and EEL2 folds
case, so they are one variable. The author intended two — the placement loop's
`o < num_osc` guard has an else-branch that can never execute. That much is a
language fact and is not in dispute.

### What was wrong

The claim that it was AUDIBLE. Predicted from reading: `@init` re-runs on
transport play with no `ext_noinit`, `@slider` does not re-run, `@sample`
re-places oscillators via `needs_init` — therefore Octave Count should silently
jump to the maximum on every play. **It does not.** Tested directly, twice, on
both plugins. One of those premises is false and I have not established which,
and that is the honest state of it — a mechanism that reads convincingly and
does not happen.

### The part worth keeping

Rozaya tested it and said it was fine BEFORE the change was written. I produced
a cancellation theory that made the negative result compatible with the bug
still existing, and shipped on the theory. The theory did not even cover both
plugins: it explains Tone's default 8 against max 16 exactly, and fails for
Scale's 8 against 12, which should have sounded uneven and did not.

**A negative test result is a result.** When a prediction is tested and does not
appear, that is evidence against the prediction — not a puzzle to be explained
until the prediction survives. The rescuing explanation is the tell.

The collision may still be worth removing one day as tidiness. It is not worth
changing what a working plugin sounds like for.

---
## 1. Melody Phase instances come in out of alignment on project open

**Status: OPEN — no fix, but the cause is no longer unknown and the workaround
is reliable.**

**Workaround: after opening the project, press play and stop once.** Alt-tabbing
out of REAPER and back does the same thing. Both re-run `@init` on every instance
at the same sample, so they all restart together and stay together. Renders were
never affected. Ear-confirmed repeatedly by Rozaya on 2026-09-02.

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

### What the 2026-09-02 measurement established

The installed build was temporarily instrumented to record, per instance, what it
could actually see at two moments: the sample it played its first note, and the
moment it stops trusting the remembered tempo. The values were appended to the end
of the `@serialize` blob (magic unchanged, so an ordinary build simply stops
reading before them) and read back out of the saved project. All twelve instances
of `simple-sequence`, project tempo 205:

- **At the first note**, every instance used **205**, not 120. `host_scale` was
  **3.4167** in all twelve, identical to four decimal places. Eleven fired at
  block 3 (16 ms); the twelfth is the one carrying `Start delay = 8` and fired
  later, as intended.
- REAPER itself was still reporting **120** to eleven of them at that moment. The
  remembered-tempo guard did its job and they ignored it.
- **At the handover** — where the settle window lapses and the live reading takes
  over — every instance saw **205** and remembered **205**. No divergence there
  either.

**So the tempo is correct at every measured point and the clock rate is identical
across instances.** The tempo path is ruled out as the cause. That also retires
the PREDICTED `host_scale` defect below: whatever that code can do in principle,
it is not doing it here.

**And the decisive one, by ear:** the scatter is present at a project tempo of
**120** too — where the placeholder and the real tempo are the same number and
there is nothing available to get wrong. **Tempo is not the variable.** The
earlier 120 test appeared to exonerate it only because it checked whether the
instances *started* together; the scatter develops later, and that was missed.

What the measurement CANNOT see: each instance counts blocks in its own lifetime,
so "block 3" for one and "block 3" for another say nothing about whether those
were the same wall-clock moment. An instantiation-order offset is fully
consistent with every number above.

### The standing explanation (Rozaya, 2026-09-02, by ear)

> "two plugins coming in on, in theory, dead-on start delays, that don't quite
> line up because independent clocks ... it reminds me of someone having to adjust
> midi I gave them because my clock ran weirdly compared to theirs. it was a
> daw-side problem."

With the transport stopped there is no shared position to reference —
`play_position` does not advance — so each instance free-runs from its own
instantiation moment. REAPER creates them one after another during project load,
so they are born milliseconds apart and nothing ever pulls them back into line.
Two instances with identical Start delays stay offset by however far apart they
were born. A transport edge is the only event that restarts them all on the same
sample, which is exactly why play/stop cures it.

**A real fix means giving synced instances a shared time origin**, and that is a
design change rather than a patch. It is the same gap already flagged above: only
`polyrhythm_phase` and `_v3` test `play_state`; fourteen plugins with sync do not.

### Theories already burned — do not resubmit

1. **"The sequence-placement feature is not firing."** Rejected: placement only
   ran under Host x, and it did not explain `upswing`.
2. **"`@init` zeroes the placement gate on every play."** Real, but introduced
   2026-09-02 and fixed in `3b42f07`; it postdates the report.
3. **"Hold the sequencer until the transport moves."** Shipped and **reverted**
   (`dcfeead`). **A fix of this shape is forbidden** — Rozaya must be able to
   hear the plugin with the transport stopped: *"now you take that away for what?
   To force me to play the project if I wanna hear something happening. No."*
4. **"The remembered tempo arrives too late, so the first note is played at
   120."** Tested 2026-09-02 by gating the sequencer's start on the blob having
   arrived (installed build only, reverted afterwards). No audible change, and
   the instrumentation then showed the premise was false: the blob had already
   arrived and 205 was already in use at the first note.
5. **"Instances hand over from remembered to live tempo at different moments,
   and some do it while REAPER still says 120."** Measured 2026-09-02: every
   instance saw 205 at its handover. False.

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
