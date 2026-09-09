# Where the suite stands

**Budget: 150 lines. Over it? This file describes NOW — delete what stopped
being now.** Narrative belongs in `docs/session-log.md`, not here.

*Checked against the tree 2026-09-08.*

## The branch

- On `feature/melody-reorder`, pushed, unmerged. **Re-run
  `git rev-list --count master..HEAD` rather than believing any number written
  here** — a count in this file has gone stale twice.
- **Do not propose merging or tagging.** Rozaya, 2026-09-05: *"I am not tagging
  that. This is not done."* Pushing is right and welcome; a tag is a
  distribution artefact and the sweep is mid-flight.
- **No releases until the sweep finishes** — shipping one now hands a stranger
  a half-renamed suite.

## The consistency sweep

`docs/suite-consistency-plan.md` is authoritative. Read it before touching any
slider's name, order, range or unit.

**Grep before believing any claim in this section.** The line "the rate block
is built everywhere" sat here for weeks while Womb offered two rate options
where the standard is five. Nobody noticed because nothing contradicted the
sentence.

- **The rate block (R20) and both host modes (R21): built everywhere.** True as
  of 2026-09-06 and not before.
- **Drift/Ramp: 16 of 19 plugins complete.** Passage is the only plugin that
  still needs the work done to it. Polyrhythm v1 is owed them only in the sense
  that it will inherit them when it crosses to v3.
  **Resonance Bank is not missing one** — its drift period is a rate by design,
  because each band drifts independently and there is no single cycle to count.
  A name-matching sweep will claim otherwise; it is wrong.
- **Polyrhythm v1 is left alone.** Decided by Rozaya 2026-09-06: *"The
  polyrhythm can just... be left. If we do v3 and then migrate it'll be fine."*
  v1 gets no drift/ramp controls and no reorder. v3 gets its layout and the six,
  then v1's **84 instances across 17 projects** cross to v3 once and v1 retires.
  Do not migrate those 84 twice. Only v3's layout needs authoring, plus the
  v1→v3 conversion after it.
- **Reorders still owed:** Passage (blocked on what it is FOR) and Sweep Dwell
  (blocked on its `Cycle mode` question, not on effort).
- **Polyrhythm v3 is done** — built and migrated 2026-09-07, 90 sliders to 56,
  the eight voices behind a **Voice** selector with an `All` position. The
  largest reorder in the suite so far.
- **The range sweep: passes 1 and 2 are done** — 176 sliders widened, 0
  narrowed, verified against all 641 continuous sliders. dB and semitone ranges
  are held for Rozaya's decision.
- **R22, the pitch block: built once and REVERTED. Nothing ships it.** See the
  Breath Generator entry below before building it again. The rule is in the
  plan; do not re-derive it, and do not re-derive the killed two-mode version.
  The rest is two jobs in order: **Melody and Shepard Tone's voices behind a
  selector**, then the pitch migration.
  **The Morpher, Passage, Sustain Looper and Bubbler are deferred and out of the
  migration list** — they pitch audio they did not make.

## What has been heard, and what has not

Only "it has been heard" counts as done.

**The not-heard list is BLOCKED work, not pending work.** It is not a queue and
it is not a to-do list. Nothing on it may be extended, built on, or "finished",
and no bug in it may be fixed unasked. **The only correct action on unheard work
is to ask for an ear test.**

That is written this plainly because the opposite kept happening. Rozaya,
2026-09-08: *"it was doing the thing of, I'm gonna fix bugs even though you've
said you haven't heard them. It was like we were having two different
conversations."* A session that starts work here is not helping — it is adding
more unheard change on top of unheard change, which makes the listening session
that eventually has to happen bigger and harder to attribute.

**Heard and good:** Melody's R20/R21 rate block and its Start delay fix; `N per
beat`; both big reorders on finished work; Dapple's immediate rate change;
per-cycle pan on Polyrhythm; Veil's layout and ramp; **the Morpher's 2026-09-06
migration** (122 instances, confirmed on real work); **the 2026-09-06 Womb
rebuild** (70 sliders across 9 projects) — *"Everything else, though, passes.
:)"*; **the 2026-09-07 Polyrhythm v3 migration** (8 instances, 5 projects) —
Rozaya opened `shapes` the same day: *"Nothing sounds off which is nice"*.

**Not heard:**

- **BREATH GENERATOR'S 2026-09-08 LAYOUT WAS BUILT, HEARD, AND REVERTED THE
  SAME DAY.** Rozaya: *"This is deeply, deeply broken... whatever the prior
  claude set it to, it only holds on the first inhale, then it falls away to
  those stored values."* Broken in BOTH Seconds and Beats.
  **`src/breath_gen.jsfx` in the repo is the 40-slider version; the INSTALLED
  plugin and all three projects are back on the 32-slider one.** They diverge on
  purpose. Do not reinstall from `src/` until the fault is found.
  The broken plugin and the migrated projects are kept for forensics at
  `E:/reaper/finished/backups/snapshots/_broken-breathgen-20260908-forensics/`.
  **Two bugs are proved and NEITHER explains the symptom**: `@slider` computes
  segment lengths without `breath_unit_sec` (Beats only, so not this), and
  `Pitch target = All` writes only the control you moved while each target holds
  a different Hz remainder, so moving the Note collapses both filters together.
  **The open question is whether the fault is mine at all** — this plugin had
  not been played in months, so it may predate the change.

- The Womb usability fix from the evening of 2026-09-06 — the breath has no rate
  mode at all now (a principled R20 exception, since its rate is emergent from
  its four segments), `Set breath rate` is a one-shot in the breath's own unit,
  and Sigh depth is additive.
- Everything from the 2026-09-06 drift/ramp sweep (six plugins), the `N per
  beat` reciprocal fix in all four plugins it touched, the Tremolo Start delay
  fix, and the range widenings.
- **Every new capability on Polyrhythm v3.** A clean open proves the old work
  survived and nothing more. Never played: per-voice On Duration / Depth /
  Attack / Release, per-voice Waveform, `Solo this voice`, `Pan rate mode` in
  any mode the tremolo was not already in, and all six drift/ramp controls.
  **`Voice = All` writing across eight voices is the one to try first** — the
  path that will be used most, and the only one that can change eight things at
  once.
- The Morpher's two new units doing anything other than their defaults. A drift
  period in Cycles or Beats, and a ramp in anything but Minutes.

Nothing in that list can regress silently — every new control defaults to off or
to what the plugin already meant, and no stored value moved. But none of it has
been played.

`docs/host-sync-ear-test.md` is still the highest-value thing waiting: five
tests, about fifteen minutes, three of them never heard on any plugin.

## The tool that closes the gap

`~/AppData/Roaming/REAPER/Scripts/kin_bridge.lua` (F4, Load ReaScript, Run,
leave running) writes a manifest of every control's live value twice a second
and reads a command mailbox — so a control can be driven and read back in the
**real** plugin rather than in a Python model of it. That is the gap the
2026-09-07 Polyrhythm build could not close. Use it to test a claim instead of
asserting one.

## The v1 → v3 Polyrhythm crossing

**Their `@serialize` blobs are no longer byte-identical.** That was true until
2026-09-07 and was the stated reason the migration was tractable. v3's blob now
carries twelve per-voice banks and four drift/ramp play-rest banks that v1 has
no equivalent of, and its magic is 2200024 against v1's 2100024.

It is still tractable — the stream layout is fully known, `tools/rpp_sliders.py`
handles the value line, and `tools/polyv3_migrate_layout_20260907.py` is a
worked example of writing that exact blob. But it is **its own job, with its own
authored conversion and its own verifier**: v1's forty per-voice values per
instance have to move off the slider line and into the blob, for 84 instances.
Skipping that step is what killed Melody v2.

**v1's slider line is over 64 values**, so the `""` marker at token index 64
applies at the source end even though v3 no longer has it.
