# More than one Ramp -- suite-wide design (2026-09-12, being designed, nothing built)

Every plugin with a Ramp. The design is authored here first; each plugin then gets its
own layout doc and ONE migration (CLAUDE.md). Quoted text is Rozaya's; everything
unquoted is Claude's and is not settled until asked.

## Why

Rozaya: *"I noticed we only have one ramp. That's great for sleep. That's not so great for
waking."* Today each plugin has one linear ramp per target, run once, then held; Ramp
engage and Ramp time unit are one each for the whole plugin (e.g. Passage sliders 57 and
61; Sustain Looper 25 and 29).

## Settled

- **WRONG WAY ROUND, corrected 2026-09-14: this said "a Ramp selector above the target
  selector".** Rozaya's words, 2026-09-12, in full: *"that could go under its own target
  list, ramp selecter, then the ramp stuff for the... wait, can we have nested stuff within
  nested stuff?"* -- target list FIRST, then the ramp selector, then the ramp settings. The
  2026-09-12 note inverted it and Veil's plan was drafted on the inversion. Rozaya, on catching
  it: *"ramps and all that shit is replacement for automation"* -- a target is a lane, its
  ramps are pieces of that lane. Re-asked 2026-09-14.
- **Eight ramps.** Rozaya: *"Yes. I think that's a good one"*.
- **Start delay "counts from" {start of the song, end of the ramp before it}.** Offered
  dropping the song-start choice for later ramps as rarely needed; Rozaya: *"Rarely is not
  the same as never."* Ramp 1 has nothing before it.
- **A shape per ramp and target**, the suite's fade names {Linear, Cosine, Logarithmic,
  Exponential}, default Linear so every saved ramp stays even. Rozaya: *"Yes, actually."*
  `apply_curve` is identical in all six plugins that have it (checked 2026-09-12):
  Logarithmic fast then slow, Exponential slow then fast, Cosine gentle at both ends.
- **Ramp engage: once per ramp**, covering all of that ramp's targets. Rozaya first:
  *"Ramp engage is just like any other ramp control. needs to be per-ramp"*; then, asked
  whether per ramp or per ramp and target: *"Once per ramp"*.
- **Ramp time unit: NOT settled.** Written as "once per ramp, taken to follow engage"; the
  transcript shows it was never asked on its own. Part 2's rule puts a unit immediately after
  what it modifies, so it belongs beside the durations whatever its scope.
- **Engage, the exact exchange:** offered once per ramp against per ramp AND per control, with
  per control recommended; Rozaya: *"Once per ramp"*. Asked under the inverted nesting above.
- **NOTHING in a ramp is shared, 2026-09-14.** Rozaya: *"Engage is a per ramp thing. That's
  all there is to it. So why is it sitting above everything else ... Why is any of that
  globally affecting all the ramps?"* With the target list first, a ramp is a piece of one
  target's lane, so "once per ramp" never meant "across every target": Claude's framing did.
  Every ramp setting -- engage, time unit, Rest mode (for Ramp), by, its unit, shape,
  duration, play/rest, start delay, counts from -- belongs to one ramp on one target, and
  sits below both pickers. Today's `(all targets)` Ramp time unit and Ramp engage end.
- **Overlapping ramps on one target add together**, so each ramp always moves by its own
  amount. Offered against "the later ramp takes over from where the earlier one got to",
  with adding recommended; Rozaya, 2026-09-13: *"I'd go with adding as well"*.
- **Ramps 2-8 start on "the end of the ramp before it"**, so fresh ramps follow one another
  with no sums; any ramp can be switched to the other. Rozaya, asked which is less maths and
  told each avoids a different sum: *"As long as it's clearly described. And as long as it's
  an optout lol"*. So the switch's name and options must say plainly what each counts from.
- **"Counts from" is per ramp and target**, like Start delay itself. Offered once per ramp,
  recommended; Rozaya: *"To maximize automation-replacability, I'd lean per-targget"* -- each
  target behaves like its own automation lane.
- **"End of the ramp before" means the SAME TARGET's ride in the ramp before** -- the next
  point on that target's own lane. Offered with, and accepted as, this detail (mine): a ramp
  that does not move the target is skipped back to the last one that did, and play start
  if none did. Against "when the whole ramp before finishes"; Rozaya: *"The same target,
  yeah."*

- **A ramp switched off keeps its place in the chain.** Its targets do not move, but the ramps
  after it start exactly when they would have, so switching one off to compare changes nothing
  else. Offered against "later ramps slide earlier", keeping recommended as muting one piece of
  automation does; Rozaya, 2026-09-13: *"Keep it like you suggested, yeah."* A ramp that never
  moved the target is still skipped back past, as settled above.
- **`Rest mode (for Ramp)` once per ramp**, `{Walk through, Freeze in place}`, so one ramp can
  walk through a rest while another freezes. **Caveat, 2026-09-14:** Claude offered only "per
  ramp or one for all eight", never per target, and under the inverted nesting. The switch was first decided on Veil (two, for
  Drift and for Ramp: `veil-r26-r27.md`). Offered per ramp against one for all eight; Rozaya,
  2026-09-13: *"Yeah, I was going to ask for that actually"*. Every plugin with Drift and Ramp
  gets both switches; Rozaya: *"Yes, all of them should get both"* (R27).

## Measured facts about today's Ramp start delay (read in code, 2026-09-12)

- **Per target in every plugin with a Ramp** (all 17; Resonance Bank per band): the value
  swaps with the Ramp target selector (`speed_ramp_delay_mem[target]`, the Morpher's and
  Passage's `ramp_delay_mem`). Plugin pages say so ("per-target ... stagger targets").
- **It counts from pressing play, only while the ramp is engaged** (Sustain Looper:
  elapsed advances under `slider29 ?`, reset by `reset_runtime()` on the play edge). I
  told Rozaya it counted from the start of the song -- wrong, unchecked. The "counts from"
  choice settled above was offered in those words; its first option is really "from play".
- Separate from the transport **Start delay**, which is one per plugin and holds drift and
  ramps together. Rozaya: *"I was under the impression that start delay was global
  affecting all ramp controls"* -- the single visible slider reads as global.

## Mine, unquoted -- ask before building on them

- The switch's own name, mine: `Ramp start delay counts from`. To be heard in REAPER.
- A saved project's one ramp becomes Ramp 1, unchanged in sound; Ramps 2-8 start empty.
- **Reading of the two "ramp end" options, mine, told to Rozaya and not corrected:** `From
  ramp end` = when the ramp before was DUE to end, ignoring anything that made it late; `From
  ramp end incl. play/rest for` = when it REALLY ends, after rests and pauses. Note `Ramp play for / rest for` (the staircase)
  never makes a ramp late -- its holds come out of the duration -- so the name could be read
  as that staircase; hear it in REAPER.

## Decided, 2026-09-13

- **After a paused or late ramp, the next one waits or keeps its time: a choice, on the
  "counts from" switch as three options.** Found after the "keeps its place" answer:
  `Ramp engage` is a pause, not an off switch (Veil's page and code, Passage's code: Off holds
  the ride where it stands, On resumes, only Play restarts), so that answer covers a ramp never
  engaged. Offered wait against start on time; Rozaya: *"It should be controlable"*. Offered a
  third option against a switch of its own; Rozaya named all three: *"From play start, from
  ramp end, from ramp incl. play/rest for"*, then *"ramp end incl. play/rest for"*. So:
  `{From play start, From ramp end, From ramp end incl. play/rest for}`.

- **A manual Engage pause counts like a rest** in `From ramp end incl. play/rest for`: the
  next ramp waits for the real end either way. Recommended; Rozaya: *"Count it yeah"*. The
  option's name mentions only play/rest, so hear it in REAPER with this in mind.

## Still to decide

- Where each new control sits in each plugin's list, per plugin layout doc.

## Traps known before building

- Nested selectors zero the selected target on track duplicate unless `@serialize`
  re-asserts the visible values (`docs/jsfx-gotchas.md`); build that in from the start.
- Set a selector one stage before its values in `jsfx_run` tests.
- A tempo change must land at once in any Beats count (Rozaya, 2026-09-11); rescale counts.
