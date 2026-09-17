# Where the suite stands

**Budget: 150 lines. Over it? This file describes NOW — delete what stopped
being now.** Narrative belongs in `docs/history/session-log.md`, not here.

**What a plugin HAS is never written here: `python tools/suite_status.py` reads it from the
plugin files** (`--installed` for REAPER's copies; `controls NAME` for one plugin's every
control). This file used to copy that, and the copy rotted -- on 2026-09-13 built work was
passed to Rozaya as owed. Write here only what the plugins cannot say: the branch, what
has been heard, and what Rozaya has said is next.

## The branch

- On `feature/melody-reorder`, pushed, unmerged. **Re-run
  `git rev-list --count master..HEAD` rather than believing any number written
  here** — a count in this file has gone stale twice.
- **Do not propose merging or tagging, and cut no release.** Rozaya,
  2026-09-05: *"I am not tagging that. This is not done."* Pushing is welcome; a
  tag is a distribution artefact and the sweep is mid-flight.

## What is next

- **The rules pass is finished at R25.** R19 to R25 are off the list. R26 and R27 are the
  two that remain and they are BUILD work, taken per plugin below -- not another reading pass.
- **Before each plugin's R26/R27 turn, read ALL of `docs/backlog.md`'s section "Decided
  2026-09-13, not built"** (it ends: *"All of this rides the amount-unit sweep: one layout
  and one migration per plugin"*) **and every Open item naming "each plugin" -- never a
  summary of them, this line included.** `suite_status.py`'s `lacks:` knows none of it. On
  2026-09-16 Veil and the Phaser were built from `lacks:` and missed first the per-target
  period units, then R9 (fractions of one become percent or dB), and a four-item summary
  written here after the first miss did not include R9 either.
- **The amount units (R26) with R27's same things, ONE PLUGIN AT A TIME** -- each planned
  with Rozaya, built, moved, measured and installed before the next. Rozaya: *"I'm wondering
  if we should take this per-plugin rather than a giant sweep."* What each plugin gains:
  `docs/backlog.md`, "Decided 2026-09-13". `tools/jsfx_map.py impact` after every edit.
- **Next plugin for R26/R27:** Rozaya's call which. `docs/backlog.md` says what each gains.
- **Held for Rozaya's decision:** semitone ranges. dB volumes were decided 2026-09-14: -60 to
  +24 everywhere.

## Open at the end of 2026-09-16 (read first)

- **Passage took over from the Morpher, built, migrated and installed (evening 2026-09-16).** Voice
  engine now one wavetable per voice (fixed in Passage only; the Morpher still has the old engine and
  its auto-gain). Grain auto-gain removed from Passage, saved levels kept via Output level. Layers
  global, -6 dB Inactive. Record: `docs/layouts/spectral-vowel-passage-takeover.md`. Every Morpher
  project carried into Passage 2026-09-16 (breathing copy 1 by hand onto slot wait time; layout doc).
- **Sweep Dwell's whole turn, 2026-09-17** (Rozaya checked every backlog item against the plugin in
  REAPER first: *"just go for it"*). 45 -> 52 controls: per-target drift/ramp units, amount units,
  movement mode, both rest modes, Play for / Rest for as targets, one Transport unit, unit switches
  that convert, the note name in every unit, three percents (R9), the shared pan order with
  `Pan direction` + Accent L / Weak R + Sway, and `Pan sweep every` mode. Installed; both saved
  copies render bit-identical (snapshot `sweep-dwell-r26r27-20260917`). Page at 0 findings.
  Record: `docs/history/layouts/sweep-dwell-filter-r26r27-20260917.md`. **Not heard.**
- **The Sweeping Filter's whole turn, 2026-09-17**, straight after Sweep Dwell's and built the
  same way (Rozaya read its list against the plugin in REAPER first). 54 -> 62 controls, blob
  2400019: the per-target units, amount units, movement mode, both rest modes, Play for / Rest for
  as targets, one Transport unit, converting unit switches, the note names in every unit, three
  percents, the shared pan order with `Pan direction` + Accent L / Weak R + Sway, `Pan sweep every`
  mode, and `Depth (% of the Low-to-High range)` -- Rozaya, told what Depth was a percent of:
  *"Yes, yes I do. because I had no idea before this that that's what it was for."* Installed; all
  21 saved copies render bit-identical (snapshot `sweeping-filter-r26r27-20260917`). Page at 0.
  **Also:** `Ramp time unit` moved under `Ramp duration` in BOTH filters (Rozaya: *"in a weird
  spot"*, then *"That sounds right yeah"*), so Sweep Dwell's blob is 2610018 and its two copies
  were migrated again from the snapshot. Record:
  `docs/history/layouts/sweeping-filter-r26r27-20260917.md`. **Not heard.**
- Installed tonight and not heard: the Morpher's grain split (heard as A/B renders: *"I can't hear
  a difference"*) and the work-list change. Still queued from before: Sweep Dwell's R26/R27 turn.



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
and the how are in `docs/history/session-log.md`.

**After any promotion the plugin must be re-read from disk.** Rozaya: *"You
don't need to quit reaper, you just need to open a new project and then reopen
one, or load the plugin onto a new track in that new one."* Cheaper than the
full quit this used to demand, and it matters — see the 2026-09-08 breath build
heard, reverted and never explained (`_broken-breathgen-20260908-forensics/`).

**Not heard** -- all built and installed; how each was built is in git and the layouts:

- **The Morpher's pitch layout, 2026-09-13:** Source/Target note, Transpose and Fine tune
  units, sixteen pitched layers, 87 targets, the amount units, Transpose value and Layer
  pitch value to -20000..20000. Also its new drift/ramp units off their defaults, All slots
  (09-11), sounding on a stopped load (09-12), Spread past 150, Low cut past 500 and Wash
  grain past 680 ms (09-13).
- **Passage's whole 2026-09-11 layout**, installed 09-13, with its 22 targets, the Morph
  drift fix and Transpose value to -20000..20000.
- **The R22 pitch blocks, 2026-09-11:** Dapple, Bubbler, Heartbeat, Womb, Rhythm Track,
  Melody, Sweep Dwell, Shepard Scale, Polyrhythm v3, the Sweeping Filter, Resonance Bank
  (Breath Generator's is heard). Resonance Bank's width units per band with it.
- **Shepard Tone and Scale, 2026-09-10:** Tone's voice split into Rate and Fine tune,
  Scale's fine tunes with their notes, pitch acting live, full targets.
- **`Drift movement mode`, 2026-09-09:** Breath Gen, Bubbler, Dapple, Womb, Heartbeat, Melody.
  Owed: an open-and-play (Bubbler's could not be shown by the runner), and a Breath Gen
  pitch target on `With the target`. Seconds/Beats on such a drift (09-10) too.
- **R24, targets in control order, 2026-09-11:** Veil, Bubbler, Dapple, Tremolo, Breath Gen,
  Heartbeat, Rhythm Track, Womb, the Morpher. Sweep Dwell's Segment selector, 09-10.
- **Sustain Looper's pitch block, Drift and Ramp, 2026-09-10**; Source note re-reading
  Target note in it and Bubbler, 09-11.
- **Melody's pitch per voice and targets (09-10)** and its song placement fix (09-11).
- **Breath Generator's 18 targets (09-11)**; its projects not opened since 09-09.
- **Womb's usability fix (09-06) and drift stepping (09-09)**; `to-sleep-within` differs for
  pre-existing reasons (`docs/history/R22.md`).
- **Solo** in Melody, Shepard Tone and Resonance Bank, overriding Active everywhere (09-10).
- **Polyrhythm v3:** the pitch block, 88 targets, per-voice On Duration, Tremolo amount,
  Waveform, Solo, Pan rate mode, `Voice = All`. Per-voice Attack/Release: Rozaya,
  *"ear-tested by somebody in here and passing, per-voice"*, no written record.
- The 2026-09-06 drift/ramp sweep, Tremolo's Start delay, the ranges; R25 names (09-12).
- Measured, not heard: Tuning reference works in all 14; Heartbeat and Womb no longer blow up
  above ~5 kHz.
- **Veil and the Stereo Phaser, afternoon of 2026-09-16:** per-target period and time units;
  R9 (Veil's resonance, the Phaser's feedback and mix now in percent); and the DRIFT amount
  unit wired in, which had been saved and shown but never applied in either. Measured, not
  heard: all three live instances bit-identical to before the day's changes, and a drift of
  12 semitones on Veil's cutoff reaches the same octave level the ramp measured (0.482
  against 0.479) where 12 in the default unit barely moves it.
- **Passage's takeover build, evening 2026-09-16:** 63 -> 89 controls, 16 layers, Auto-morph Rate,
  111 targets, wavetable voice, no wash auto-gain. Measured, not heard: 49 copies in 11 projects, wash
  within 0.1 dB of their old loudness, voice -117 dB, every control in place. Snapshot:
  `E:/reaper/finished/backups/snapshots/passage-takeover-20260916`.
- **The Morpher's whole R26/R27 layout, night of 2026-09-16:** 64 -> 79 controls, 107 targets,
  Transport unit, the rest switches, per-target units, Drift movement mode, Spread and both cuts
  as pitch blocks, blob 7700107. `docs/history/layouts/spectral-vowel-morpher-r26r27.md`.
  Measured, not heard: all 135 live copies bit-identical old vs new, every control in place.
- **Veil and the Stereo Phaser, evening of 2026-09-16:** the effect now waits out Start
  delay (it only held drift and ramp); `Drift rest mode` / `Ramp rest mode` renamed; and
  `Drift movement mode`, with Play for / Rest for as targets that finally do something. Measured,
  not heard: every stretch holds the length it began with (28 of 28), all five live copies
  bit-identical and every control in place after `tools/drift_movement_migrate_veil_phaser_20260916.py`.
- **The Stereo Phaser's (09-16) and Veil's (09-15) whole R26/R27 layouts.** Measured, not heard:
  bit-identical old vs new on defaults and on every live copy. `docs/history/layouts/`.
- **2026-09-15, measured:** Polyrhythm voices start silent, so no thump on play (Rozaya heard
  the thump); Tremolo's and the Sweeping Filter's Start delay on Every N beats; Tensor's
  `shepard.RPP` carried from the first release (open bug 4).

`docs/host-sync-ear-test.md` is the highest-value thing waiting: five tests,
fifteen minutes, three never heard on any plugin.

## The tool that closes the gap

`~/AppData/Roaming/REAPER/Scripts/kin_bridge.lua` (F4, Load ReaScript, Run, leave
running) drives and reads every control in the **real** plugin. `tools/bridge_ui_test.py`,
2026-09-11 evening, all 18 live: every target name, Drift movement, "all" entry,
selector and mirror passed, and 112 of 112 values survived save and reopen. **REAPER must
be the front window** or its audio is closed and no plugin runs `@block`.
