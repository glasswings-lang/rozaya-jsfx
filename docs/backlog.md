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

## Open — checked against the plugins 2026-09-16

- **`Drift period unit` and `Ramp time unit` are shared across targets, and nobody decided
  that.** Rozaya, 2026-09-15: *"after all the work we did to make things per-target in ramp,
  why?"* There is no reason in the record. `docs/history/session-log.md` stage 8 states it
  flatly -- *"Units global, play/rest per (slot, target)"* -- as a fact of the port from the
  Morpher, never as a choice. **Resonance Bank already disagrees**: its `Drift period mode` is
  per band and target, one plugin in nineteen. And R26 makes `Drift amount unit` per target
  outright (*"No unit locks. ever."*), which leaves the period unit the odd one out.
  **Done in Veil and the Stereo Phaser, 2026-09-16**, and in Sweep Dwell and the Sweeping Filter
  2026-09-17 -- the first two had been built the day before WITHOUT it and were fixed on Rozaya's
  *"Do it pls :)"*. Owed by the other fifteen, in their turns.
  Per target would widen `@serialize` and needs a magic bump, so it belongs IN each plugin's
  R26 turn, not as a sweep. If it lands, the `(all targets)` mark comes off those two and
  only `Ramp engage` keeps it.
- **Seven targets R24 is owed, and Play for / Rest for in two.** R24, closed 2026-09-15
  with nothing built; it lands in each plugin's own amount-unit turn (R26/R27), because
  inserting a target in control order renumbers the picker and rewrites every saved
  selection. Rozaya, on the whole-step controls: *"Yeah, I think they should be in the
  picker for drift, and ramp, for that matter."* Gains a target: Melody `Octave shift`,
  Polyrhythm v3 `Octave shift`, Shepard Scale `Centre octave`, Shepard Tone `Centre
  octave`, the Morpher `Layer harmonics` (per layer, so `(all layers)` + 16 like its
  siblings), and `Source fine tune` on the Morpher and Passage. Gains `Play for` and
  `Rest for` as targets: nobody left -- Sweep Dwell and the Sweeping Filter got them 2026-09-17. STAY OUT, decided 2026-09-15:
  Polyrhythm's `Phase offset` and the Sweeping Filter's `LFO start phase` -- *"There's no
  reason to drift a start-only control"*.
  Structural counts stay out. Re-check with `python tools/r24_target_audit.py`; what was
  measured and what is still open is in `docs/history/R24.md`.
- **`Drift movement mode (per target)` in the seven that lack it, and `Cycles` counting the
  target's own cycles.** R23, closed 2026-09-15 with nothing built; Rozaya: *"Fold it in
  yeah"* -- it lands in each plugin's own amount-unit turn (R26/R27), never as a sweep.
  Owed by: Tremolo, Polyrhythm v3, Shepard Scale, Shepard Tone, the Morpher (grain length).
  Sweep Dwell and the Sweeping Filter got it 2026-09-17: Sweep Dwell's four segment lengths latch
  when their cycle begins, the Sweeping Filter's On duration, Depth, Attack and Release likewise,
  and Play for / Rest for when their stretch does. Each recomputes an envelope or segment value
  from a running phase every sample instead of latching it when the occurrence begins.
  Resonance Bank owes nothing; Sustain Looper is deliberately live. Veil and the Stereo
  Phaser got it 2026-09-16 for Play for / Rest for, which turned out to be targets NOTHING
  READ (bit-identical with a large drift). **In each plugin's turn, measure that its Play
  for / Rest for targets change the sound** -- only Veil, the Phaser and the Morpher have
  been checked (the Morpher reads them, every block, so it owes the switch). Separately, Polyrhythm and Shepard Tone count the MASTER rate's cycles for
  per-voice targets. What was read, and the misreading to avoid: `docs/history/R23.md`.
- **`Drift amount unit` / `Ramp by unit` in the other fifteen.** Committed 2026-09-11,
  Rozaya: *"Yes, do it your way. I'd prefer that while we have room"*. Built in Passage,
  the Morpher, Veil, the Stereo Phaser, Sweep Dwell and the Sweeping Filter; the other thirteen
  have neither (read from every slider list, 2026-09-16).
  How: `docs/history/layouts/spectral-vowel-passage.md`, "The amount units".
- **One Pan mode order in all six plugins that have one. Blocks a release.** Rozaya: *"I'm
  not gonna ship something like that on any plugin"*. The order, each plugin showing the
  choices it has: `Mono, Spread, Spread Reversed, Alternating, Alternating every 2,
  Alternating every 4, Alternating every 8, Accent L / Weak R, Distributed, Distributed
  (Ping-pong), Converging, Converging (Ping-pong), Diverging, Diverging (Ping-pong), Linked
  Sweep, Tremolo, Sway, Increment, Pan Sweep`. **Sweep Dwell and the Sweeping Filter have it,
  2026-09-17** -- read either one's list and migration before doing another. Every plugin gets
  every choice except these:
  Spread, Spread Reversed and Increment are Polyrhythm and Melody only; Tremolo is
  Polyrhythm only; Sway is everywhere but those two. Melody's `Tremolo` goes (a saved one
  becomes Increment with `Pan increment` 0). `Pan direction {Normal, Flipped}` sits right
  after `Pan mode` everywhere and mirrors any choice; the three `(Flipped)` choices go (a
  saved one becomes its partner with the switch on Flipped). The migration moves every
  saved choice. A choice that needs a rate or an "every" its plugin lacks brings that
  control, in the layout. Measure pan positions with `jsfx_run` before and after.
- **`Pan sweep every (cycles)` counts only the slow way** (Linked Sweep, in Tremolo; Sweep Dwell
  and the Sweeping Filter got the `Every N cycles / N per cycle` picker 2026-09-17). A sweep faster than one cycle means typing 0.5 or 0.25. Rozaya: *"the
  multiplier is the off-putter there"*. The rate modes solved the same thing with `Every N
  beats` and `N per beat`.
- **The rate block, where it is not yet whole.** Every speed is a pair named `<name> mode`
  then `<name> value` (`Heart rate mode`, `Bubble rate mode`, plain `Rate mode` where nothing
  is more specific; today's names vary). Heartbeat and Rhythm Track lose
  `Host ratio (retired)` (the Stereo Phaser's went 2026-09-16): hidden and switched off, but in the parameter list. Heartbeat's
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
- **Switching any mode or unit picker keeps the thing the same and converts the number**,
  wherever that conversion is exact; where it is not (Cycles of a speed that may drift), the
  number stays. Rozaya: *"It should cover them all I think"*. Passage converts all of its unit
  switches (2026-09-16); the Morpher its rate and transport times; Polyrhythm overwrites Rate value with 4 or 1 on entering
  a beat unit, and that goes; the other plugins leave the number alone.
- **The pitch block, where it is not yet whole.** Blocks for the frequencies with none: the
  Morpher's and Passage's low and high cuts as two blocks each (the Stereo Phaser's range and
  Veil's cutoffs are built, 2026-09-15/16); Womb's breath high-pass,
  breath post-filter and bloodflow filter in place beside their parts. That pairing is a
  trial, Rozaya: *"We can try it; I won't know until I see it."* Melody's and Polyrhythm's
  `Transpose` get a unit picker, starting on Semitones. Shepard Scale's notes go behind a
  Note picker, `All` first, each note's active, gain, pan, fine tune unit and fine tune under
  it. The note name works in every unit, both ways, in every block; so does `Target note` in
  every Transpose unit once a Source note is set, and Bubbler's and Sustain Looper's names
  say "only with a Source note". The two-way link was found by search in Breath Generator,
  Polyrhythm and Sweep Dwell; check each other plugin when building.
- **Womb's Breath High-pass: a better filter.** Still the Chamberlin SVF, which stops near
  7200 Hz of 20000. Rozaya, 2026-09-13: *"We need a better filter."* (TPT, as the sweeping
  filters have.) Agreed condition: measure every saved Womb copy old against new before
  installing, and say how big any difference is.
- **Womb's page** (`docs/plugins/womb.md`) still says a sigh segment's length multiplies
  by `slider61`, which is Bloodflow Volume now. Owed a rewrite from the plugin.
- **The plugin pages, a pass of their own.** `python tools/page_controls.py`: 141 findings on
  2026-09-17 (Sweep Dwell's and the Sweeping Filter's went with their turns; both pages are at 0);
  168 on 09-16 (206 on 09-14; the breakdown below is from 09-14). 95 are controls a page never mentions, mostly Drift and Ramp;
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
- **`Transport unit` may want a better name.** Rozaya, 2026-09-16, told it sets what Start
  delay, Play for and Rest for count in: *"What the hell is a 'transport' unit."*, then, asked
  what it should say, *"I'm... not actually sure."* Kept for now in Veil, the Phaser, Passage
  and the Morpher's layout. A rename moves nothing; rename all at once when a name lands.
- **Drift period units under host sync** -- periods count heartbeats or breaths; should
  they be beats when synced? Not checked against the source on 2026-09-13.

## Decided 2026-09-16, not built: Passage takes over from the Morpher

- **The Morpher's layers (and what else it has that Passage lacks) move into Passage.** Rozaya,
  after capturing to all slots and finding the Morpher's pitch is one setting for every slot: *"the
  closer morfer gets to where I'd want it to be, the more like passage it is than not"*, then *"They
  absolutely do belong in passage. Hell, the only reason passage existed was to give finer control
  over slots, but I see no reason that can't be done by hand with beats and such, or durations."*
  **Auto-morph's continuous sweep stays**, with the Morpher's rate pair (Rozaya: *"Passage needs it."*).
  **Layers are global, not per slot** (Rozaya, 2026-09-16: *"the per slot layering doesn't really
  make sense to me ... I would just have it be global"*; thickening one slot is done with All slots).
  Order agreed-in-principle: first the shared engine faults (both plugins run the per-partial sine
  voice engine and the grain auto-gain), then this. The Morpher is in 39 projects (135 copies);
  `tools/morpher_to_passage.py` already carries a project across by label.

## Decided 2026-09-13, not built

Rozaya, asked all three: *"Yes, and yes, re: sustain looper, breath generater, and the other
one. Finish it, re: the audit."*

- **Start delay, Play for and Rest for in every plugin.** Missing for the whole plugin in
  Sustain Looper and Resonance Bank (read 2026-09-16; Veil and the Stereo Phaser have them now).
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
  Morpher, Passage (read in each @sample 2026-09-13); Resonance Bank lacks it today (Veil and the Stereo Phaser gained it 2026-09-15/16). The nine that make their own sound have nothing to pass. Rozaya: *"Feels
  like you'd want that as a switch. passthrough or silence."*
  **The walk-or-freeze switch's name.** Today it is `Rest mode` in the Morpher, Passage, Melody
  and both Shepards, `Rest mode (LFO)` in Sweep Dwell and the Sweeping Filter (2026-09-17), and
  `LFO at rest` in Tremolo (read 2026-09-13). Rozaya: *"rest mode (for LFO) seems like it'd be clearer for the ones called the
  other thing."* Those three freeze only their LFOs (`in_frozen_rest` gates LFO phase alone),
  so the name is true of them. A label change, no position moves; goes in each one's layout.
- **Every pitch spread takes a unit picker** `{Hz, Semitones, Cents}`, **and no Percent.**
  Rozaya: *"Yes! Fuck those hidden limits"*. Bubbler's `Pitch spread (semitones)` 0..24 and
  `Rise (semitones)` 0..36 get the picker. Dapple's `Pitch spread (%)` is a share of a hidden
  3 octaves: 50% becomes 18 semitones. Sustain Looper's `Spread (%)` fans its copies from 3
  cents at 0% to 25 at 100% and also sets a wander of up to 6 cents: it becomes the fan in
  cents (50% is 14), wander kept in proportion. The hidden limits go. Both are value migrations.

- **No control counts in fractions of one (R9).** Every control whose range sits inside -1 to 1
  changes unit: volumes become dB from -60 (off) to +24, and everything else becomes percent (pan
  runs -100 to 100). Each one is a value migration. Rozaya, 2026-09-14: *"That'd be fine by
  me"*, and on volumes: *"db, that's the only unit it makes sense in for volumes"*. On
  2026-09-14 that was 45 controls in 12 plugins, before Veil's, the Phaser's and then Sweep
  Dwell's and the Sweeping Filter's three each (Resonance, Pan spread, Wet/dry mix, 2026-09-17);
  find them by reading each plugin's ranges.

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
- **Bubbler and Dapple step live on purpose**, behind `Drift movement mode` (Rozaya: *"The
  stepping was deliberately live"*). The seven that still owe R23 are in Open above -- an
  entry here once called them cleared, and that was wrong (checked 2026-09-16).

