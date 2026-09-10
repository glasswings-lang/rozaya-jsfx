# Where the suite stands

**Budget: 150 lines. Over it? This file describes NOW — delete what stopped
being now.** Narrative belongs in `docs/session-log.md`, not here.

*Checked against the tree 2026-09-09.*

## The branch

- On `feature/melody-reorder`, pushed, unmerged. **Re-run
  `git rev-list --count master..HEAD` rather than believing any number written
  here** — a count in this file has gone stale twice.
- **Do not propose merging or tagging, and cut no release.** Rozaya,
  2026-09-05: *"I am not tagging that. This is not done."* Pushing is welcome; a
  tag is a distribution artefact and the sweep is mid-flight.

## The consistency sweep

`docs/suite-consistency-plan.md` is authoritative. Read it before touching any
slider's name, order, range or unit.

**Grep before believing any claim in this section.** The line "the rate block
is built everywhere" sat here for weeks while Womb offered two rate options
where the standard is five. Nobody noticed because nothing contradicted the
sentence.

- **The rate block (R20) and both host modes (R21): built everywhere.** True as
  of 2026-09-06 and not before.
- **Drift/Ramp: 16 of 19 plugins complete.** Passage is the only one still owed
  it; Polyrhythm v1 inherits when it crosses to v3. **Resonance Bank is not
  missing one** — its drift period is a rate by design, whatever a name-matching
  sweep claims.
- **Polyrhythm v1 is left alone.** Rozaya, 2026-09-06: *"The polyrhythm can
  just... be left. If we do v3 and then migrate it'll be fine."* No drift/ramp
  and no reorder; its **84 instances across 17 projects** cross to v3 once, then
  v1 retires. Do not migrate those 84 twice.
- **Reorders still owed:** Passage (blocked on what it is FOR), Sweep Dwell
  (blocked on its `Cycle mode` question, not effort).
- **Polyrhythm v3 is done** — built and migrated 2026-09-07, 90 sliders to 56,
  the eight voices behind a **Voice** selector with an `All` position. The
  largest reorder in the suite so far.
- **The range sweep: passes 1 and 2 done** — 176 sliders widened, 0 narrowed,
  verified against all 641 continuous sliders. dB and semitone ranges held for
  Rozaya's decision.
- **R22, the pitch block: built in Breath Generator ONLY, heard good
  2026-09-09.** Rebuilt twice by Rozaya in the hearing, so the plan's written
  rule is BEHIND the built one — `docs/layouts/breath-gen.md` is what ships.
  **R22 opens with an attribution warning**: parts were mine, cited back as
  settled. Only *"Morpher and Passage are their own discussion"* is hers.

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

**Heard and good:** Melody's R20/R21 rate block and Start delay fix; `N per
beat`; both big reorders on finished work; Dapple's immediate rate change;
per-cycle pan on Polyrhythm; Veil's layout and ramp; the Morpher's 2026-09-06
migration (122 instances); the 2026-09-06 Womb rebuild (70 sliders, 9 projects);
the 2026-09-07 Polyrhythm v3 migration (8 instances, 5 projects); Breath
Generator's 40-slider layout, 2026-09-09 — *"it works end-to-end"*. The quotes
and the how are in `docs/session-log.md`.

**Quit REAPER fully before reopening after any promotion** — from the 2026-09-08
breath build heard, reverted and never explained; pair kept at
`snapshots/_broken-breathgen-20260908-forensics/`.

**Not heard:**

- **`Drift movement` — the whole sweep, 2026-09-09.** Whether a target's drift
  steps with its own thing or runs on a clock is now a per-target switch in all
  six plugins that had stepping: Breath Gen (slider 30), Bubbler (20), Dapple
  (22), Womb (60), Heartbeat (23), Melody (76). Rozaya: it *"should have been a
  switch from the very beginning"*. INSERTED beside the period controls on their
  call, never appended. **110 instances across 24 projects migrated; every
  project renders bit-identical**, and the switch is measured changing the sound
  in five of the six. Defaults are exactly what `drift_is_stepped()` hardcoded.
  Backups: the three `_pre-driftmoves-*-20260909/` snapshots.
  Bubbler's switch could NOT be demonstrated — drift on Bubbler ignores the
  runner entirely, before this change as much as after; pre-existing, unchased.
  Womb/Melody blobs were left alone: seven stored formats between them, all
  still readable, so only slider lines moved. Owed: an open-and-play, and a
  Breath Gen pitch target on `With the target` — a filter centre, so ears-only.



- **The Breath Generator 40-slider build is PROMOTED, 2026-09-09.** It IS the
  live plugin, `_TEST40` deleted, four instances migrated. **The migrated
  PROJECTS have not been opened since**, so an open-and-play of `breathscapes`,
  `micle` and `organic-movement` is the ear test owed. Backups:
  `_pre-breathgen-promote-20260909/`. **Bit-identical over 40 s on all three** —
  envelope and timing only; the runner cannot see filter frequency. The reload
  bug it caught is in `docs/session-log.md`.

- The Womb usability fix of 2026-09-06 (no breath rate mode — a principled R20
  exception; `Set breath rate` a one-shot; Sigh depth additive), **and its
  2026-09-09 drift stepping** — six of eleven targets step on their own turn.
  Eight of nine live projects render bit-identical; **`to-sleep-within` changes**,
  being the only one with a stepped drift running (its drift is also misfiled
  onto Heart rate by an old blob — pre-existing).
- **R23 is SWEPT, 2026-09-09** — Heartbeat and Melody too; Bubbler and Dapple
  built then REVERTED at Rozaya's call, and fourteen plugins are cleared and must
  not be "fixed" (`docs/backlog.md` has the table). Every live project renders
  identical except `to-sleep-within`. Unheard, all of it.
- The 2026-09-06 drift/ramp sweep (six plugins), the `N per beat` reciprocal fix
  in all four plugins it touched, the Tremolo Start delay fix, the range widenings.
- **Every new capability on Polyrhythm v3.** A clean open proves the old work
  survived and nothing more. Never played: per-voice On Duration / Depth /
  Attack / Release, per-voice Waveform, `Solo this voice`, `Pan rate mode` in a
  new mode, and all six drift/ramp controls. **`Voice = All` writing across eight
  voices is the one to try first** — the most-used path, and the only one that
  can change eight things at once.
- The Morpher's two new units off their defaults: a drift period in Cycles or
  Beats, a ramp in anything but Minutes.

`docs/host-sync-ear-test.md` is the highest-value thing waiting: five tests,
fifteen minutes, three never heard on any plugin.

## The tool that closes the gap

`~/AppData/Roaming/REAPER/Scripts/kin_bridge.lua` (F4, Load ReaScript, Run,
leave running) writes every control's live value twice a second and reads a
command mailbox, so a control can be driven and read back in the **real**
plugin. Use it to test a claim instead of asserting one.

## The v1 → v3 Polyrhythm crossing

**Their `@serialize` blobs are no longer byte-identical.** That was true until
2026-09-07 and was the stated reason the migration was tractable. v3's blob now
carries twelve per-voice banks and four drift/ramp play-rest banks that v1 has
no equivalent of, and its magic is 2200024 against v1's 2100024.

Still tractable — `tools/polyv3_migrate_layout_20260907.py` is a worked example
of writing that blob. But it is **its own job, with its own authored conversion
and verifier**: v1's forty per-voice values per instance move off the slider line
into the blob, 84 times. Skipping that is what killed Melody v2.

**v1's slider line is over 64 values**, so the `""` marker at token index 64
applies at the source end even though v3 no longer has it.
