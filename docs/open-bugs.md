# Open bugs

**Entries 1 and 2 are CLOSED. Entry 3 is FIXED and waits only on Rozaya meeting
the new name in REAPER.** A closed entry stays here for its reasoning and its
burned theories, so they are not re-derived — read them before touching the
plugin they name, then leave them alone.

Things that are known-broken and NOT fixed. Newest first. A bug leaves this file
only when it has been fixed *and* heard.

---

## 3. Polyrhythm v1, v3 and Full Feature Tremolo — `Depth dB` worked the opposite way to its manual — FIXED 2026-09-10

Found 2026-09-10 while measuring per-voice envelopes. **Resolved the same day,
Rozaya's call, after it asked whether the design or the manual broke convention.**
The code is REAPER's stock `guitar/tremolo` line for line (`Amount (dB)`,
-60..0, default -6), so the MANUAL was wrong, in all three plugins, since the
first release. Manuals corrected; the control is now `Tremolo amount (dB, 0 = strongest)`.
No sound changed. Full Feature Tremolo measured the same way at 60 BPM.

**The code:** `amount = pow(2, depth / 6)`, then gain = `lfo * 0.5 * amount +
(1 - amount)`. So **0 dB pulses fully** (trough silent, peak 0.5), the -6 dB
default swings between 0.5 and 0.75, and **-60 dB does not pulse at all**.

**The manual** (`docs/plugins/polyrhythm-phase-v3.md`, `Depth dB`) says the
reverse: 0 dB is no depth, -60 dB silences the trough.

**Measured with `jsfx_run`, fresh instance, 100 ms RMS:** depth -60 holds level
0.354 flat; depth 0 falls from 0.177 to 0.002 across every cycle.

**v1 has the same formula** (`src/polyrhythm_phase.jsfx`, `amount = pow(2,
depth_db / 6)`), so every saved project was set by ear against the code, not the
manual. Changing the code would change their sound; the manual or the label is
the cheap side. Also worth knowing: the pulse's loudest point drops as depth
grows (0.75 at -6 dB, 0.5 at 0 dB).

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

**Status: CLOSED 2026-09-05 — ACCEPTED WITH ITS WORKAROUND. Not fixed, and not
to be fixed opportunistically.** Rozaya: *"I'd say the bug's marked done.
alt-tab is acceptable."*

> **Why this is closed rather than left open, and it is a process decision.**
> Rozaya: *"having another instance panic over a supposedly open bug and try to
> fix it while also doing other things as 'I also did x while I was in there' is
> how we wound up with errors."*
>
> **An open entry is an invitation.** A session arriving here mid-task reads
> OPEN as a job, reaches for it while already elbow-deep in something else, and
> ships a fix nobody asked for alongside work that was asked for. That is
> precisely how the forbidden fix below got shipped once already. The cost of
> the bug is one alt-tab. The cost of a session opportunistically fixing it is
> unbounded, and has been paid.
>
> **So: do not fix this. Do not "improve" it while you are in Melody for
> something else.** Everything below is kept because the reasoning and the five
> burned theories are worth having — not because there is work outstanding.
> Rozaya may test it independently as its own thing; that is different from a
> session deciding to.

The cause is known and the workaround is reliable.

**Workaround: after opening the project, press play and stop once.** Alt-tabbing
out of REAPER and back does the same thing. Both re-run `@init` on every instance
at the same sample, so they all restart together and stay together. Renders were
never affected. Ear-confirmed repeatedly by Rozaya on 2026-09-02.

### What is left of it

The loud half of the original report was the 2026-07-02 slider-insert bug — drift
switching itself on in projects that never used it — which is fixed and
ear-confirmed (see *Recently closed* below). What remains is the report against
**`simple-sequence`** specifically: 12 instances, all synced, arriving at
slightly different times on project open, with a play/stop curing it.

> **THE PROJECT HAS CHANGED UNDER THIS REPORT. Re-measured 2026-09-05.** This
> paragraph used to say *"every Start delay 0, tempo 205"*. Both were true when
> written and neither is now:
>
> - **The project tempo is 120, not 205.** It was still 205 in the
>   `_pre-phase1-20260831` snapshot, so it was changed some time after that.
> - **Start delays are no longer all zero** — the twelve instances now hold a mix
>   of `0` and `8`.
>
> **This weakens the entry's own explanation for why the fault is audible here.**
> The argument below is that a small absolute offset is a large fraction of a
> 0.585 s step. At 120 BPM the step is **1.000 s**, so the same offset is now a
> smaller fraction of it, and the fault may well be quieter or absent. Anyone
> re-testing should expect that rather than reading a null result as a fix.

`simple-sequence` was **never** affected by the slider shift (its blob magic is
2100028, the current format), so this is a separate, quieter fault.

**The `upswing` half of the original report is now believed to have been the
drift bug and should be treated as withdrawn** unless it is heard again.

### What is known

- A play/stop cures it; renders were always fine. Both follow from `@init`
  re-running on every instance on the same sample at the transport edge, which is
  currently the **only** shared time origin the sequencer has.
- Melody's `@sample` has no `play_state` test anywhere, so each instance's
  sequence starts at *its own* instantiation moment. **This is true of the WHOLE
  SUITE** — re-measured 2026-09-05: of the 17 plugins that can sync, **not one**
  tests `play_state` in `@sample`.

  > **Corrected 2026-09-05.** This bullet used to say *"Only `polyrhythm_phase`
  > and `_v3` have such a test; fourteen other plugins with sync do not."* Both
  > halves were wrong. The Polyrhythms' only mentions of `play_state` are
  > COMMENTS — one of which records that the transport-edge handler was REMOVED
  > in v2.10 Path A — and there are 17 synced plugins now, not 15. The original
  > claim came from a grep that did not exclude comment lines, which is a mistake
  > this repo has now made more than once.
  >
  > **The correction strengthens the diagnosis rather than weakening it.** Melody
  > is not the exception; `@init` re-running at the transport edge is the only
  > shared time origin ANY of these plugins has. Melody is simply where it
  > becomes audible, because of the 0.585 s step below.
- `simple-sequence`'s step was **0.585 s** at the tempo it had when this was
  diagnosed — `(1/0.5) ÷ (205/60)` — so a small absolute offset was a large
  fraction of a step, which is why it was audible there and not in a project with
  4-second steps. **At today's tempo of 120 the same step is 1.000 s**, so the
  mechanism still holds but the margin is nearly double what it was.

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

### Melody Phase — a delayed instance came in early — FIXED 2026-09-06

**This is NOT the alignment bug in entry 1, and conflating them would be a
mistake.** That one scatters many instances and a play/stop cures it. This one
hit exactly one instance, was constant, and play/stop did nothing — which is what
told them apart.

**Symptom.** In `simple-sequence`, track 10 sat a fraction of a beat out against
the melody. From the first note. Not cured by play/stop or by alt-tabbing.

**How it was found, and the method is the point.** Rozaya localised it by ear to
one track, then narrowed it themselves across three exchanges: first that the
offset did not move when the project tempo changed, then that the affected pair
"work with one another", then the correction that it was track 10 and not 9. The
decisive step was a one-slider test — **Start delay to 0 removed the symptom,
restoring 8 brought it back exactly.** Track 10 is the only instance in that
project carrying a Start delay.

**Two false starts on my side, both worth recording.** I first suspected the
Start delay, dropped it on a misreading of "the delays work with one another",
spent a round on the Play/Rest gate instead, and had to be corrected back. And I
twice reported the arithmetic as "consistent on paper" — which it was, for the
quantity I was checking. **The paper was right and the question was wrong:** both
clocks measured beats correctly, and the defect was that they started at
different moments.

**Cause.** The sequencer's first note waits for the config to settle
(`cfg_ready && slider_ran && cfg_stable >= CFG_HOLD_BLOCKS`). The Start delay
counter waited for nothing and began accumulating on the first sample after
`@init`. So a delayed instance spent part of its delay inside a pause the
undelayed instances had not left yet, and entered early by the length of that
pause — **two audio blocks, ~21 ms at 512/48 kHz, 0.043 beats at 120 BPM.**
Deterministic, and it reappears on every transport play because the pause does.

**Fix.** Gate the accumulation on the same condition the sequencer uses, so both
clocks share a starting line. One line. `Start delay = 0` is unaffected — the
counter is never entered.

**Status: FIXED and HEARD, 2026-09-06.** Rozaya, on the installed fix: *"it's
now done, and out of there."* The mechanism above is therefore confirmed rather
than predicted.

**The suite was then audited, because Rozaya asked whether anything else had
it.** The bug needs TWO clocks — a start-delay counter AND a separate gate the
engine waits for. Nineteen plugins have a Start delay; **only Melody and
Full Feature Tremolo have such a gate** (`cfg_stable`/`CFG_HOLD_BLOCKS`), so only
those two could have it. **Tremolo did, with the identical structure**, and was
fixed the same way — its LFO phase advance waits for `cfg_stable` while its delay
counter did not. Tremolo's fix changes no saved project: 11 instances in the
library and **not one has a Start delay set**, so it is purely preventive.

**Checked and cleared while there, so it is not re-derived:** the OTHER start-delay
hazard — counting wall-clock seconds against a delay expressed in cycles — is
correct everywhere. The suite splits into two architectures and both are
self-consistent. Plugins whose rate variable already has the tempo folded in
(bubbler, dapple, heartbeat, rhythm-track, shepard-scale, womb, breath_gen,
sweep-dwell) derive `start_delay_sec` in REAL seconds and rightly accumulate
`1/srate`. Plugins holding a NOMINAL rate with the tempo applied separately
(Melody, Tremolo, the Sweeping Filter, both Polyrhythms, shepard-tone) accumulate
`host_scale/srate`. No plugin mixes them.

**It moves existing projects.** Any saved project using a Start delay now starts
that instance a few milliseconds later than before. That is the correction, not a
side effect, and it is on the plugin page too.



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
