# Backlog — what the suite is still owed

**Budget: 650 lines.** Run `python tools/doc_budget.py` before committing.

**NOTHING IN THIS FILE IS A JOB YOU MAY START UNASKED.**

That sentence is the whole reason this file exists separately. This material used
to sit inside `docs/suite-consistency-plan.md`, so a session that opened the plan
to check one rule was handed seven hundred lines of owed work — and read it as a
to-do list. Rozaya, 2026-09-08, on what that felt like from the other side:
*"it was doing the thing of, I'm gonna fix bugs even though you've said you
haven't heard them. It was like we were having two different conversations."*

**A backlog is not permission.** Read this to answer "what is this plugin owed?"
when you are already working on that plugin and have been asked to. Do not read
it to decide what to do next. That decision is Rozaya's.

**And check it against `docs/current-state.md` AND THE PLUGIN before believing any
line here.** On 2026-09-13 most of this file described work already built, and a
session passed it to Rozaya as open. Every item below was checked against `src/`
that day; an item you cannot find in the source the way it is described is stale.
Anything on the not-heard list in current-state is BLOCKED, not pending.

---

## Open — checked against the plugins 2026-09-13

- **`Drift amount unit` / `Ramp by unit` in the other seventeen.** Committed 2026-09-11,
  Rozaya: *"Yes, do it your way. I'd prefer that while we have room"*. Built in Passage
  and the Morpher only; the other seventeen have neither (read from every slider list).
  How: `docs/layouts/spectral-vowel-passage.md`, "The amount units".
- **R19, the pan mode order. Blocks a release.** Rozaya: *"I'm not gonna ship something
  like that on any plugin"*. Still in arrival order: Melody and Polyrhythm lead with
  Tremolo / Increment / Spread / Spread Reversed; Tremolo has no `Alternating (Flipped)`,
  the filters and Sweep Dwell do; Rhythm Track has six modes including `Accent L / Weak R`.
  Decided 2026-09-02 (Rozaya: *"I say we bloody save it until phase 2"*): ONE reorder
  across every plugin with a Pan Mode, with the value remap for 0-3 in the same commit.
  Re-count stored values first -- "nothing is saved on 4+" expires the moment one is used.
  The proposed order is R19 in `docs/suite-consistency-plan.md`.
- **Womb's Breath High-pass: a better filter.** Still the Chamberlin SVF, which stops near
  7200 Hz of 20000. Rozaya, 2026-09-13: *"We need a better filter."* (TPT, as the sweeping
  filters have.) Agreed condition: measure every saved Womb copy old against new before
  installing, and say how big any difference is.
- **Womb's page** (`docs/plugins/womb.md`) still says a sigh segment's length multiplies
  by `slider61`, which is Bloodflow Volume now. Owed a rewrite from the plugin.
- **Heartbeat's batch**, when it comes:
  - the filename: `src/heartbeat gen.jsfx` is the only one with a space. Rozaya,
    2026-09-13: *"We can wait for heartbeat's thing"*. Projects that load it (backups
    aside): `finished/transformation.RPP`, Tensor's `transformation.RPP` and
    `tensor-heartbeat-pulse` (never loaded -- its path broke on the space), the bridge
    test project. Suggested `heartbeat_gen`, not chosen.
  - R9, a fraction written as a percent: `Breath HRV Depth` is still 0..0.25 and
    `Random HRV Depth` 0..0.08, so a drift step of 0.1 overshoots the whole control. As
    percents they become 0..25 and 0..8. Changes a range, so it needs a migration.
- **Breath catches** (Womb and Breath Generator): designed in `docs/planned-features.md`,
  "Breath catches", not built in either. Star, 2026-08-31: *"any other plugin that uses
  breath should also get these."*
- **Hidden limits, still owed:** the 2026-09-13 audit could not judge 104 widened controls
  (nothing in the copies tried was using them). `tools/hidden_limit_audit_20260913.py`.
  **Asked 2026-09-13 whether this is still wanted.**
- **jsfx_run does not clamp to a slider's declared range; REAPER does.** 700 set into a
  -96..96 control stored 700 (measured 2026-09-13), so an offline test passed what REAPER
  caps. Owed: clamp like REAPER, or check every set value against the declared range.
- **The Morpher's R23 check.** The drift-stepping sweep (done 2026-09-09) lists the Morpher
  as cleared, and a later note says it was never re-checked. Read it before relying on either.
- **The `0..1` inventory.** Sliders topping out at 1.0 or less split into dB and percent,
  and nobody has listed which is which. current-state holds dB and semitone ranges for
  Rozaya's decision.
- **Drift period units under host sync** -- periods count heartbeats or breaths; should
  they be beats when synced? Not checked against the source on 2026-09-13.

## Decided 2026-09-13, not built

Rozaya, asked all three: *"Yes, and yes, re: sustain looper, breath generater, and the other
one. Finish it, re: the audit."*

- **Start delay, Play for and Rest for in every plugin.** Missing for the whole plugin in
  Sustain Looper, Veil, Stereo Phaser and Resonance Bank (read ignoring capitals, 2026-09-13).
  What they DO have is `Drift play for / rest for`, `Ramp play for / rest for` and `Ramp start
  delay` -- per target, a different thing. Rozaya, on whether every plugin should have the same
  things: *"They should all have the same things"*, then *"Yes both"* (the spreads below, and
  the suite).
- **Every pitch spread takes a value and a unit picker** `{Hz, Semitones, Cents}`, as Fine tune
  does -- not locked to cents (no unit locks). Bubbler's `Pitch spread (semitones)` 0..24 and
  `Rise (semitones)` 0..36; Dapple's `Pitch spread (%)`; Sustain Looper's `Spread (%)`. Read
  what each percent is a percent OF before authoring: converting one is a value migration.

**All of this rides the amount-unit sweep: one layout and one migration per plugin**, holding
everything that plugin gains, never a second pass (CLAUDE.md, "Author the whole layout").
- **A sigh for Breath Generator**, matching Womb's (`Sigh interval`, `Sigh extra length`),
  plus its drift and ramp targets. Its layout's "No sigh" was a Claude scope note, not a no.
- **Finish the hidden-limit audit**: the 104 controls it could not judge each need a setup
  that makes them audible.

## Settled -- do not propose again

- **Melody Phase has no voice selector, deliberately.** Each of its eight voices has its own
  Note, Pitch (Hz / semitones / cents) and Fine tune. Rozaya, 2026-09-13: *"melody phase
  deliberately lacks a voice selecter, and the pitch work was described to me as done"*.
- **The Shepards have no Hz / semitones / cents mode.** Star, 2026-09-10: *"a Shepard voice
  is its note in every octave at once."* (`docs/layouts/shepards-r22-r24.md`.) And
  `Center Octave` does not retire: it centres the octave window `Octave Count` spans.
- **The Morpher's layers carry no Source or Target note.** Rozaya: *"Nah, keep it as-is."*
  (`docs/layouts/spectral-vowel-morpher.md`.)
- **No unit locks, ever.** A unit is at most a default.
- **Drift amounts stay in the target's own units, never "% of its range."** Rozaya,
  2026-08-28: *"I don't want to lose range. I don't want to have to abstract away things
  because you've decided I can't count."* R12 governs ranges (0-1000 or wider; small values
  are the step's job). Sizing an amount to a "sensible wander" was retracted as condescension.
- **Scatter (random slot per wash grain) is ruled out** for Rozaya's chordal captures.
  `docs/planned-features.md`.
- **Harmonic Sculptor is archived** (`4d0339f`).
- **JSFX stays the format.** Plain source that runs, no toolchain, CC0-compatible, and the
  flat slider list is what makes the plugins reachable through OSARA.
- **Drift steps on the target's own turn (R23): swept 2026-09-09.** Bubbler and Dapple step
  deliberately, behind `Drift movement` (Rozaya: *"The stepping was deliberately live"*).
  Cleared, do not "fix": Tremolo, both Shepards, Sweep Dwell, Sweeping Filter, Polyrhythm
  v3, Veil, Stereo Phaser, Resonance Bank. Seconds and Beats on a stepped target were
  decided and built 2026-09-10.

## Removed 2026-09-13 because it is built

Checked in `src/` before removal: every Rate Mode and pan rate mode reads `BPM, Seconds, Hz,
Every N beats, N per beat`; every plugin has Drift and Ramp play for / rest for, a Drift
period unit or mode and a Ramp time unit; Breath Generator's `Breath rate`; Sustain
Looper's Drift and Ramp targets; pitch blocks in Breath Generator, Bubbler, Dapple,
Heartbeat, Melody (per voice), Polyrhythm v3, Resonance Bank (per band), Sustain Looper,
Passage and the Morpher; Transpose value and Layer pitch value at -20000..20000; the capture
slot selector `{All, Slot 1-8}`; a version stamp in every `@serialize`; Polyrhythm v3's voice
gain at -6 dB; Sweep Dwell's segments behind a selector; the Spread, Low cut, Wash grain and
Capture average limits. With them went the Phase 0/1/2 plans and migration tables, all
worked through (Polyrhythm v1 crossed, the Sweeping Filter, Tremolo, Womb, Melody, Passage,
the Morpher). The full earlier text is in git, in this file before the commit that says so.
