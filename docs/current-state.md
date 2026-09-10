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
- **Drift/Ramp: 16 of 19 complete.** Passage is owed it; Polyrhythm v1 inherits
  at v3. **Resonance Bank is not missing one** — its period is a rate by design.
- **Polyrhythm v1 is left alone**, Rozaya 2026-09-06. Its **84 instances across
  17 projects** cross to v3 once, then v1 retires. Do not migrate those 84 twice.
- **Reorders owed:** Passage (blocked on what it is FOR), Sweep Dwell (blocked on its `Cycle mode` question).
- **Polyrhythm v3 is done** — built and migrated 2026-09-07, 90 sliders to 56,
  the eight voices behind a **Voice** selector with an `All` position. The
  largest reorder in the suite so far.
- **The range sweep: passes 1 and 2 done** — 176 sliders widened, 0 narrowed,
  verified against all 641. dB and semitone ranges held for Rozaya's decision.
- **R22:** Breath Gen's block was rebuilt twice in the hearing, so the plan's rule
  is BEHIND the built one — `docs/layouts/breath-gen.md` ships. R22 opens with an
  attribution warning: parts of it were mine, cited back as settled.

## What has been heard, and what has not

Only "it has been heard" counts as done.

**Unheard is not blocked, and asking for an ear test is not free.** Rozaya,
2026-09-09: *"It's OK that I haven't heard them, I'll test them when all the
features are there to test ... doing that repeatedly just makes me want to throw
shit."* This list records what is owed a hearing and it may grow. **One
listening session with everything in place beats five partial ones** — every
promotion costs a full REAPER restart, and the restarts are the cost.

**What is still forbidden is starting work nobody asked for.** Rozaya: *"it was
doing the thing of, I'm gonna fix bugs even though you've said you haven't heard
them. It was like we were having two different conversations."* Build what was
asked, propagate, measure, add it here — never hunt this list for jobs.

**Heard and good:** Melody's R20/R21 rate block and Start delay fix; `N per
beat`; both big reorders on finished work; Dapple's immediate rate change;
per-cycle pan on Polyrhythm; Veil's layout and ramp; the Morpher's 2026-09-06
migration (122 instances); the 2026-09-06 Womb rebuild (70 sliders, 9 projects);
the 2026-09-07 Polyrhythm v3 migration (8 instances, 5 projects); Breath
Generator's 40-slider layout, 2026-09-09 — *"it works end-to-end"*. The quotes
and the how are in `docs/session-log.md`.

**After any promotion the plugin must be re-read from disk.** Rozaya: *"You
don't need to quit reaper, you just need to open a new project and then reopen
one, or load the plugin onto a new track in that new one."* Cheaper than the
full quit this used to demand, and it matters — see the 2026-09-08 breath build
heard, reverted and never explained (`_broken-breathgen-20260908-forensics/`).

**Not heard:**

- **Shepard Tone and Scale: drift and ramp reach everything** — per-voice/note
  Gain and Pan and the binaural beat, Tone 11 targets -> 28, Scale 4 -> 29,
  appended so nothing stored moves. Scale also gained twelve per-note detunes.
  Their banks overlapped until 2026-09-10; now 64 apart, and a ramp surviving a
  drift on another target is measured on both. Ears owed.

- **THE R22 ROLLOUT — running. Done: Breath Gen (heard), Dapple, Bubbler,
  Heartbeat, Womb, Rhythm Track, Melody, Sweep Dwell, Shepard Scale. Owed: the
  two sweeping filters, Resonance Bank, Polyrhythm.** Rozaya: doing some and not
  others is *"shipping a pool ... and only having water that fills half the
  fucking pool"*. Four shapes: Dapple took Breath Gen's block unchanged;
  **Bubbler took the SHIFT form Rozaya designed** — `Source note` says where zero
  is, defaults to `None`, and the semitone value is never gated; Heartbeat's two
  went behind an {All, S1, S2} target, its migration CREATING the blob it never
  had; **Womb and Sweep Dwell replicate the block IN PLACE**, keeping their
  migrations line-only. **Melody and Shepard needed no selector**: a voice already
  has its note, so it gains one fine tune — nine controls, not thirty-two.

- **`Drift movement` — the whole sweep, 2026-09-09.** Per-target switch in all six
  plugins that had stepping: Breath Gen, Bubbler, Dapple, Womb, Heartbeat, Melody.
  Rozaya: it *"should have been a switch from the very beginning"*. Inserted, never
  appended. **110 instances over 24 projects migrated, every project
  bit-identical**; measured changing the sound in five of six. Defaults are what
  `drift_is_stepped()` hardcoded. Backups: `_pre-driftmoves-*-20260909/`. Bubbler's
  could NOT be shown — drift on Bubbler ignores the runner, before as much as
  after; pre-existing. Owed: an open-and-play, and a Breath Gen pitch target on
  `With the target`, which is ears-only.

- **Sustain Looper, 2026-09-10:** Bubbler's pitch block, Drift and Ramp on eight
  targets, and loop moves crossfade instead of cutting. 4 instances migrated,
  bit-identical with the sample loaded. `docs/layouts/sustain-looper.md`.

- **Melody Phase, 2026-09-10:** pitch mode and a pitch per voice, 55 drift
  targets in control order. 73 instances bit-identical. `docs/layouts/melody-phase-r22-r24.md`.

- **The Breath Generator 40-slider build is PROMOTED.** Four instances migrated,
  bit-identical over 40 s on all three; the migrated PROJECTS have not been
  opened since. Backups: `_pre-breathgen-promote-20260909/`.

- The Womb usability fix of 2026-09-06 and its 2026-09-09 drift stepping. Eight
  of nine projects bit-identical; `to-sleep-within` differs for pre-existing
  reasons (`docs/history/R22.md`).
- **R23 is SWEPT** — fourteen plugins cleared and not to be "fixed"
  (`docs/backlog.md` has the table).
- The 2026-09-06 drift/ramp sweep, `N per beat`, Tremolo's Start delay, the ranges.
- **Every new capability on Polyrhythm v3.** Never played: per-voice On Duration /
  Depth / Attack / Release, per-voice Waveform, `Solo this voice`, `Pan rate mode`
  in a new mode, all six drift/ramp controls. **`Voice = All` first** — the
  most-used path, and the only one that changes eight things at once.
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
