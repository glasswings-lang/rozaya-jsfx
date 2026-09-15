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

**What a plugin has comes from `python tools/suite_status.py`, never from this file.** On
2026-09-13 most of this file described built work, and a session passed it to Rozaya as
open. This file holds what Rozaya decided and what is owed; where an item says what a plugin
lacks, check it with the tool first. Built work is not listed here -- git history has it.
Anything on the not-heard list in current-state is BLOCKED, not pending.

---

## Open — checked against the plugins 2026-09-13

- **`Drift amount unit` / `Ramp by unit` in the other seventeen.** Committed 2026-09-11,
  Rozaya: *"Yes, do it your way. I'd prefer that while we have room"*. Built in Passage
  and the Morpher only; the other seventeen have neither (read from every slider list).
  How: `docs/history/layouts/spectral-vowel-passage.md`, "The amount units".
- **One Pan mode order in all six plugins that have one. Blocks a release.** Rozaya: *"I'm
  not gonna ship something like that on any plugin"*. The order, each plugin showing the
  choices it has: `Mono, Spread, Spread Reversed, Alternating, Alternating every 2,
  Alternating every 4, Alternating every 8, Accent L / Weak R, Distributed, Distributed
  (Ping-pong), Converging, Converging (Ping-pong), Diverging, Diverging (Ping-pong), Linked
  Sweep, Tremolo, Sway, Increment, Pan Sweep`. Every plugin gets every choice except these:
  Spread, Spread Reversed and Increment are Polyrhythm and Melody only; Tremolo is
  Polyrhythm only; Sway is everywhere but those two. Melody's `Tremolo` goes (a saved one
  becomes Increment with `Pan increment` 0). `Pan direction {Normal, Flipped}` sits right
  after `Pan mode` everywhere and mirrors any choice; the three `(Flipped)` choices go (a
  saved one becomes its partner with the switch on Flipped). The migration moves every
  saved choice. A choice that needs a rate or an "every" its plugin lacks brings that
  control, in the layout. Measure pan positions with `jsfx_run` before and after.
- **`Pan sweep every (cycles)` counts only the slow way** (Linked Sweep, in Tremolo and both
  filters). A sweep faster than one cycle means typing 0.5 or 0.25. Rozaya: *"the
  multiplier is the off-putter there"*. The rate modes solved the same thing with `Every N
  beats` and `N per beat`.
- **The rate block, where it is not yet whole.** Every speed is a pair named `<name> mode`
  then `<name> value` (`Heart rate mode`, `Bubble rate mode`, plain `Rate mode` where nothing
  is more specific; today's names vary). Heartbeat, Rhythm Track and the Stereo Phaser lose
  `Host ratio (retired)`: hidden and switched off, but in the parameter list. Heartbeat's
  `Breath cycle (seconds)` becomes a Breath rate pair on the rate picker, 0 = no breath
  sway. **Polyrhythm:** the rate mode moves under the Voice selector, per voice; in Drift a
  voice reads `Rate value (all voices)` in its own unit; Permute swaps a voice's unit with
  its speed; `Phase offset` gets a per-voice unit picker `{BPM, Seconds, Hz, Beats, N per
  beat, Milliseconds, Cycles, Percent}` (it counts seconds, or beats on a beat unit, today,
  whatever its name says); `Reverse drift offset` gets one `{Each voice's own unit, BPM,
  Seconds, Hz, Every N beats, N per beat}`; Transport Cycles counts each voice's own pulses,
  Start delay included. **Shepard Tone:** voices go behind a Voice selector, All first, with
  every per-voice control under it, rate unit and fine tune unit included; synced voices
  read the shared Rate value in their own unit; its Transport unit is `{Seconds, Beats}`.
  Saved projects land on what
  they count today. Dapple's Start delay is read, not measured.
- **Put every mode before its value, in every plugin.** Most plugins still have the value
  first. Fix it inside each plugin's own planned migration, not as a separate pass. The
  rule is in the rules file, under "The four rules inside the order".
- **Passage, in its next migration:** each unit picker moves above the timings it sets
  (Slot timing unit above slot fade in, hold, fade out and gap after; Transport unit above
  Start delay, Play for and Rest for), and those names lose their `seconds / Hz / beats`.
  The fade shapes stay under the timings. Rozaya said yes to this.
- **Womb's Breath High-pass: a better filter.** Still the Chamberlin SVF, which stops near
  7200 Hz of 20000. Rozaya, 2026-09-13: *"We need a better filter."* (TPT, as the sweeping
  filters have.) Agreed condition: measure every saved Womb copy old against new before
  installing, and say how big any difference is.
- **Womb's page** (`docs/plugins/womb.md`) still says a sigh segment's length multiplies
  by `slider61`, which is Bloodflow Volume now. Owed a rewrite from the plugin.
- **The plugin pages, a pass of their own.** `python tools/page_controls.py`, 2026-09-14: 206
  findings (215 that morning). 95 are controls a page never mentions, mostly Drift and Ramp;
  77 are pages quoting ranges from before the 2026-09-06 range sweep; 34 are old name styles,
  changed option lists, retired controls and one default. The rules work does not reduce
  these -- it only touches a page where a rule does -- so they need their own pass, ranges
  first, then the missing controls one plugin at a time. Any rule work updates its pages in
  the same commit so this does not grow. The commit gate on this check was proposed
  2026-09-13 and not agreed.
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
  the suite). **The shape, agreed 2026-09-13:** Start delay, Play for and Rest for share ONE
  `Transport unit` picker in every plugin, defaulting to what the plugin counts in today
  (cycles, beats, breaths, steps; Seconds where it has no turn, as Veil), with Seconds and
  Beats offered. Nothing saved changes meaning. Rozaya: *"Yes. should have had that from
  the beginning."*
  **The Morpher's** Start delay, Play for and Rest for still say `(sec, or beats in Host x)`;
  no mode has been called Host x since R21 (beats when Rate mode is Every N beats or N per
  beat). Left for its own Transport unit, which renames them. Rozaya, 2026-09-14: *"It can
  wait for its own unit switch"*.
  **At rest:** anything with movement offers BOTH Walk through and Freeze in place (Rozaya:
  *"Walk *and* freez, those two things are not either/or"*). The `Output at rest` switch
  `{Pass-through, Silence}` goes in every plugin that works on incoming sound -- Tremolo, the
  Sweeping Filter, Sweep Dwell, Veil, Stereo Phaser, Resonance Bank, Bubbler, Dapple, the
  Morpher, Passage (read in each @sample 2026-09-13); Veil, Stereo Phaser and Resonance Bank
  lack it today. The nine that make their own sound have nothing to pass. Rozaya: *"Feels
  like you'd want that as a switch. passthrough or silence."*
  **The walk-or-freeze switch's name.** Today it is `Rest mode` in the Morpher, Passage, Melody
  and both Shepards, and `LFO at rest` in Tremolo, the Sweeping Filter and Sweep Dwell (read
  2026-09-13). Rozaya: *"rest mode (for LFO) seems like it'd be clearer for the ones called the
  other thing."* Those three freeze only their LFOs (`in_frozen_rest` gates LFO phase alone),
  so the name is true of them. A label change, no position moves; goes in each one's layout.
- **Every pitch spread takes a value and a unit picker** `{Hz, Semitones, Cents}`, as Fine tune
  does -- not locked to cents (no unit locks). Bubbler's `Pitch spread (semitones)` 0..24 and
  `Rise (semitones)` 0..36; Dapple's `Pitch spread (%)`; Sustain Looper's `Spread (%)`. Read
  what each percent is a percent OF before authoring: converting one is a value migration.

- **No control counts in fractions of one (R9).** Every control whose range sits inside -1 to 1
  changes unit: volumes become dB from -60 (off) to +24, and everything else becomes percent (pan
  runs -100 to 100). Each one is a value migration. Rozaya, 2026-09-14: *"That'd be fine by
  me"*, and on volumes: *"db, that's the only unit it makes sense in for volumes"*. On
  2026-09-14 that was 45 controls in 12 plugins; find them by reading each plugin's ranges.

**All of this rides the amount-unit sweep: one layout and one migration per plugin**, holding
everything that plugin gains, never a second pass (CLAUDE.md, "Author the whole layout").
- **Breath and sigh, in Womb and Breath Generator.** A `Breath mode` picker, `{Breath, Sigh}`.
  Every breath control below it belongs to whichever is picked: breath unit, set breath rate,
  the four lengths, the inhale and exhale pitches and fine tunes, the four fades and fade
  shape, the high-pass and post-filter with its Q, stereo width and volume. Shared: how often
  a sigh comes, and breath solo. `Sigh extra length` goes; the migration sets each project's
  sigh so it sounds as it does now. How often a sigh comes gets a unit picker,
  `{Seconds, Minutes, Beats}`, default Minutes, in the slot `Sigh extra length` leaves (the
  picker first, then the interval). Drift and ramp get a breath entry, a sigh entry and a both
  entry for each of these. Breath Generator gets all of it, including a sigh. Rozaya:
  *"breath mode (breath or sigh) aught to do it, then let the rest of the breath controls
  touch each of those individually"*; on the unit, *"Just make it per thinggy"*; on the
  targets, *"Yeah, I was going to ask for that anyway"*.
- **Finish the hidden-limit audit**: the 104 controls it could not judge each need a setup
  that makes them audible.

## Settled -- do not propose again

- **Melody Phase has no voice selector, deliberately.** Each of its eight voices has its own
  Note, Pitch (Hz / semitones / cents) and Fine tune. Rozaya, 2026-09-13: *"melody phase
  deliberately lacks a voice selecter, and the pitch work was described to me as done"*.
- **The Shepards have no Hz / semitones / cents mode.** Star, 2026-09-10: *"a Shepard voice
  is its note in every octave at once."* (`docs/history/layouts/shepards-r22-r24.md`.) And
  `Center Octave` does not retire: it centres the octave window `Octave Count` spans.
- **The Morpher's layers carry no Source or Target note.** Rozaya: *"Nah, keep it as-is."*
  (`docs/history/layouts/spectral-vowel-morpher.md`.)
- **No unit locks, ever.** A unit is at most a default.
- **Drift amounts stay in the target's own units, never "% of its range."** Rozaya,
  2026-08-28: *"I don't want to lose range. I don't want to have to abstract away things
  because you've decided I can't count."* R12 governs ranges (0-1000 or wider; small values
  are the step's job). Sizing an amount to a "sensible wander" was retracted as condescension.
- **Scatter (random slot per wash grain) is ruled out** for Rozaya's chordal captures.
  `docs/planned-features.md`.
- **Harmonic Sculptor is archived** (`4d0339f`). Rozaya, 2026-07: *"harmonic sculpter is
  something I feel like needs a serious overhaul, either that, or to be dropped entirely. I
  certainly wouldn't reach for it."*
- **Before adding a slider, check whether the plugin already knows the answer.** The rule
  that killed two invented pan sliders (2026-09-02), Rozaya: *"Add to the slider that reaches
  sideways... you could extend to infinity"* -- the enum is the free axis.
- **Position locking is for plugins that play a sequence of notes** (Shepard Scale, Melody):
  starting mid-song on the wrong note is audibly wrong. The rest keep their own time.
  2026-08-12; `tools/lock_test.py`.
- **JSFX stays the format.** Plain source that runs, no toolchain, CC0-compatible, and the
  flat slider list is what makes the plugins reachable through OSARA.
- **Drift steps on the target's own turn (R23): swept 2026-09-09.** Bubbler and Dapple step
  deliberately, behind `Drift movement` (Rozaya: *"The stepping was deliberately live"*).
  Cleared, do not "fix": Tremolo, both Shepards, Sweep Dwell, Sweeping Filter, Polyrhythm
  v3, Veil, Stereo Phaser, Resonance Bank. Seconds and Beats on a stepped target were
  decided and built 2026-09-10.

