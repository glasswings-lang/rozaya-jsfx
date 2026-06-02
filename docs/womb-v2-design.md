# Womb v2 — design notes (in-progress)

Captured at the end of an iterative design session that left v2 in an
in-between state. Branch `feature/womb-v2`, last commit `4628210`. This
doc is for a future session (or fresh-context redo) to pick up without
having to re-derive what's been tried and where the confusion landed.

The current committed v2 is **not** known-good — it hasn't been tested
by ear in REAPER, and the most recent operator feedback (captured in
"Latest direction" below) wants to change it again.

## Pointers

- **Current v2 source:** `src/womb_sound_generator_v2.jsfx` on branch `feature/womb-v2`, commit `4628210`.
- **Previous v2 commit** (superseded): `53b5163` — kept for history.
- **v1 baseline** (still in tree, untouched): `src/womb_sound_generator.jsfx`.
- **Pattern source for selector+value:** `src/standalone/harmonic_sculptor.jsfx` (its slider2 + slider3 with backing memory bank `harm_amp`).
- **Related deferred work:** Speed Ramp start delay as a suite-wide sweep — see `docs/planned-features.md` under "Deferred for separate planning."

## Current state (commit 4628210)

Inherited from v1, unchanged:
- BPM (slider1), heartbeat (3–13), breath durations (16–19) in seconds,
  other breath controls (14, 15, 20–28), bloodflow (29–36), breath post-filter
  (39, 40), Start Delay (41), Play/Rest (42–47), Speed Ramp target /
  duration / engage (48–50).

Removed from v1:
- Breath HRV Depth (slider37) and Random HRV Depth (slider38) — slot
  IDs left vacant; comment in source notes the removal.
- All `breath_mod`, `rand_hrv`, `hrv_seed` machinery from `@init` and
  `@sample` (the cycle_len computation is now just BPM-derived with
  the existing 200-BPM safety floor).

New in v2:
- **slider51 — Speed Ramp start delay** (0–60 min, default 0). When the
  Speed Ramp engage toggle flips on, this many minutes elapse at base
  rate before the ramp begins. A future suite-wide sweep is documented
  in `docs/planned-features.md`.
- **slider52 — Breaths per minute** (4–30, default 7). Currently
  *bidirectional* with the four phase duration sliders (16–19): tweak
  BPM and the four durations rescale proportionally; tweak any
  duration and BPM updates to reflect the new total. Implemented via
  `slider_automate()` with change-source detection so the two sides
  stay in sync without infinite loop.
- **slider53 — Drift parameter selector** (enum, 5 options):
  `{Heart Up by, Heart Down by, Heart with breath, Breath Up by, Breath Down by}`.
- **slider54 — Drift value** (0–50, step 0.1). Sets the value for
  whichever parameter slider53 is on. A memory bank (`drift_values_bank[0..4]`)
  holds all 5 values. When the selector moves, the value slider snaps
  to the new slot's stored value via `slider_automate()`. When the
  value moves with the selector unchanged, the new value writes back
  to the current slot. Pattern is borrowed from `harmonic_sculptor.jsfx`.
- **slider55 — Heart drift period** (cycles, 1–1000, default 8). How
  many heartbeats per one heart drift cycle.
- **slider56 — Breath drift period** (cycles, 1–1000, default 8). How
  many breath cycles per one breath drift cycle.
- **slider57 — Drift shape** (Sine / Triangle / Random, default Sine).
  Shared by both heart and breath drift.

Wiring inside `@sample`:
- Heart drift wave produces `heart_drift_offset` (BPM), added to
  `effective_bpm`.
- "Heart with breath" produces `heart_with_breath_offset` (BPM)
  modulated by `breath_state` (inhale → ramp up to max, top pause →
  hold at max, exhale → ramp back down, bottom pause → 0). Also added
  to `effective_bpm`. Layers cleanly with heart drift.
- Breath drift wave produces `breath_drift_offset_bpm`. Effective
  breath rate = `slider52 + breath_drift_offset_bpm`. Conversion to a
  state-advance multiplier: `breath_combined_scale = combined_scale * (effective_breath_bpm / slider52)`,
  which replaces `combined_scale` at the two breath state-advance
  sites (`breath_state_pos +=` and `pr_br_rest_elapsed +=`).

## What's been tried (in iteration order)

### Iteration 1: Breath cycle scaler + Link-based breath drift (commit 53b5163, superseded)

- Replaced HRV depth sliders with a "Breath cycle scaler" (0.1–4.0
  multiplier on the four phase durations, computed at `@slider` time).
- Added breath drift as 7 new sliders: a Link toggle (default On) plus
  Musical/Slow Up/Down/Period for breath drift; when linked, breath
  drifted proportionally with the heart's drift; when unlinked, breath
  used its own sliders to drift the scaler.
- Added Speed Ramp start delay (slider67, moved later).

**Tested in REAPER:** scaler worked clearly and intuitively. Breath
drift did **not** produce audible breath rate change in either Link
mode. Multiple suspects, none definitively isolated:
- Slider values typically set were small (e.g., 2 in a 0–2 range with
  step 0.01) and produced only ~2% rate variation — possibly below
  audibility.
- Scaler-delta unit ("Up by 0.5" with no unit label) felt abstract;
  hard to know what value to set.
- REAPER may not always pick up `.jsfx` file changes if a project
  already has the plugin loaded.
- An actual wiring bug was never definitively ruled out.

### Iteration 2: Selector + value pattern + bidirectional BPM (commit 4628210, current)

Born from a conversation where the operator (a) noted that "Breath
HRV Depth" in v1 was abstract and not directly controllable, and (b)
referenced the two-slider selector+value pattern from
`harmonic_sculptor.jsfx` (which they'd built in a prior session). The
goal was to collapse the 14 drift sliders into a much smaller surface
where each parameter could be edited one at a time with backing
memory.

- Replaced Breath cycle scaler with bidirectional BPM <-> phase
  durations sync (slider52).
- Replaced all 14 drift sliders with: Drift parameter selector
  (slider53, 5 enum options) + Drift value (slider54) + memory bank.
- Kept Heart/Breath drift periods as separate sliders (55, 56) and
  Drift shape as its own slider (57). The Musical/Slow two-timescale
  split was dropped — single drift wave per cycle.
- HRV came back as one of the selector entries ("Heart with breath"),
  expressed in concrete BPM.
- Speed Ramp delay moved to slider51.

**Tested in REAPER:** not yet. The doc was written before the operator
ran v2 with these changes. See "Latest direction" below for the
feedback that immediately followed.

## Latest direction (not yet built)

After looking at the current v2's slider surface, the operator pushed
back on the selector+value pattern for this plugin specifically:

> Heart drift up and drift down should probably be their own sliders.
> Breaths per minute needs to be at 0, letting you set the durations
> to be scaled and then, as you adjust it, reflecting the modified
> durations in those 4 sliders. HRV needs to be bpm, independent of
> drift but also a layer on top of it if both are active.

Concretely:

- **BPM behavior** — default 0 (inert; the four duration sliders run
  the breath cycle directly). When set to nonzero, the four durations
  rescale proportionally to match the target BPM, and the slider
  values in REAPER update to show the new numbers. Direction: probably
  one-way (BPM nonzero → rescale durations), not bidirectional —
  duration tweaks after the rescale don't auto-update BPM. **Not
  confirmed.**
- **Heart drift Up / Down** as their own sliders (BPM).
- **HRV** ("Heart with breath") as its own slider (BPM), independent
  of heart drift, additively layered when both are active.
- **Breath drift Up / Down** — operator hasn't explicitly confirmed
  whether breath drift exists in this iteration, what unit it would
  use, or whether it would also have its own sliders. Likely
  breaths-per-minute by analogy with heart drift, but **not confirmed.**

Sketched layout (not built; await operator confirmation before
implementing):

- slider52 — Breaths per minute (default 0 = inert; one-way rescale)
- slider53 — Heart drift: Up by (BPM)
- slider54 — Heart drift: Down by (BPM)
- slider55 — Heart drift: Period (cycles)
- slider56 — HRV / Heart with breath (BPM)
- slider57 — Breath drift: Up by (breaths/min)?
- slider58 — Breath drift: Down by (breaths/min)?
- slider59 — Breath drift: Period (cycles)?
- slider60 — Drift shape (Sine / Triangle / Random)

That's 9 sliders in the breath-rate + drift + HRV block, vs the
current 7. More slider count, but each one is unambiguously labeled
for what it controls.

## Confusion points and lessons learned

- **Sub-1 fractional values in abstract units feel meaningless.** A
  slider value of "0.5" without a clear concrete unit reads as
  arbitrary. The same number in a familiar unit (BPM, seconds) reads
  as meaningful. The v1 HRV "depth" sliders (0–0.25) had this exact
  problem.

- **Selector + value pattern works when items are the same kind of
  thing.** Harmonic Sculptor has 64 harmonics — all the same entity
  type, all with the same unit (dB). v2's drift parameters have
  similar units (BPM-ish) but different conceptual roles (Heart Up
  vs Heart Down vs HRV); collapsing them into one selector adds
  cognitive overhead (which parameter am I editing right now?)
  without saving meaningful slider space.

- **Use case matters for slider density.** Womb is for slow,
  attentive listening — you tweak rarely and want clear naming, not
  fast access. A larger but unambiguous slider surface is probably
  better than a compact selector pattern.

- **"Cycles" as an amplitude unit is confusing.** "Period in cycles"
  is fine (how long a drift wave takes). "Amplitude in cycles"
  overloads the word.

- **Naming asymmetry breeds confusion.** When some drift sliders say
  what they affect ("Breath drift: ...") and others don't ("Musical
  drift: ..."), the un-prefixed ones become ambiguous about whether
  they're for heart or breath.

- **Breath drift in scaler-delta units was inaudible at typical
  settings.** Whether the wiring was correct was never definitively
  confirmed; the operator-felt failure was real and the redesign
  skipped past the diagnosis rather than nailing the cause.

- **BPM behavior needs careful thought about defaults.** If BPM has a
  "real" default (e.g., 7), on first load it might conflict with what
  the durations actually total. If BPM has an "inert" default (0),
  the question becomes "what does the value mean when nonzero" and
  "do durations changing back-update BPM."

- **Iterating in chat is hard for this kind of design.** Many turns
  went into restating the same idea differently, partial proposals
  that then needed walking back, etc. A grounding pass (look at how
  other meditation/biofeedback plugins handle this) before the next
  iteration would likely help.

## Open design questions (for the next session)

1. **BPM default behavior** — one-way "rescale tool" (default 0,
   nonzero rescales durations once, duration changes don't update
   BPM), bidirectional (both stay in sync continuously), or something
   else?

2. **Does breath drift exist** in the next iteration? Heart drift is
   consistent; breath drift has wavered between "yes own sliders,"
   "yes selector entries," and "no, just heart."

3. **Unit for breath drift** if it exists: breaths-per-minute
   (parallels heart in concept) or seconds (concrete time unit, more
   directly matches the duration sliders' unit)?

4. **HRV / heart-with-breath** — confirmed as its own slider in BPM,
   independent of and additively layering with heart drift. Math is
   the same RSA pattern v1 used (modulate HR by breath phase), but
   amplitude in concrete BPM rather than the v1 abstract depth
   multiplier.

5. **Drift period(s) and shape** — keep as separate sliders, or fold
   into other controls?

6. **Slider clutter vs naming clarity** — if every drift parameter
   gets its own slider, the parameter list is longer but every name
   is unambiguous. Is that acceptable, or is some compaction worth
   the cognitive overhead?

## Research that would help before the next iteration

A grounding pass before more design iteration. Specifically:

- How meditation / biofeedback plugins (Muse Calm Mode, Calm /
  Headspace breath features, dedicated REAPER plugins for breathing
  entrainment, granular synths used for sleep) surface breath-rate
  and HRV controls.
- Clinical-vs-consumer language for HRV: how it's expressed in apps
  people actually use vs in clinical literature.
- UI patterns for "master rescale" knobs that affect multiple
  subordinate sliders in audio production (e.g., master tempo with
  per-track tempo overrides, group faders, send levels).
- Whether existing JSFX plugins have solved similar selector+value
  or master+scaled-children problems.

Single-agent research task, not a parallel-agent workflow. ~20–40
minutes of focused web search and synthesis.

## What hasn't been tested by ear

The entire `4628210` commit (the current v2) hasn't been
REAPER-validated. The previous v2 (`53b5163`) was partially tested:
the scaler worked; breath drift didn't seem to. The current v2 changed
both pieces significantly, so neither the known-working nor the
known-broken state from `53b5163` carries forward — everything needs
fresh testing.

## Suggested next-session shape

1. Operator plays with the current v2 in REAPER (commit `4628210`)
   to get an embodied sense of what the selector+value pattern feels
   like and whether the BPM <-> durations sync works as expected.
2. A research pass (the bullet list above) to ground the next design
   in actual patterns from other plugins.
3. Re-converge on a slider layout — likely the "individual sliders
   per parameter" direction in "Latest direction" above, refined by
   what the research surfaces.
4. Build it in chunks small enough to test each piece by ear before
   moving on.
