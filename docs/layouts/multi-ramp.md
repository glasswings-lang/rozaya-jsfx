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

- **A Ramp selector above the target selector.** Rozaya: *"its own target list, ramp
  selecter, then the ramp stuff"*. In Passage the nesting is slot > ramp > target (Passage
  already nests slot > target, measured).
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
- **Ramp time unit: once per ramp.** Asked in the same question as engage and taken to
  follow it -- confirm if it ever matters.
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
  walk through a rest while another freezes. The switch was first decided on Veil (two, for
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

- **The first option's NAME, not settled.** "Start of the song" is wrong: it counts from
  pressing play. Offered renaming (nothing saved changes) against changing the behaviour;
  Rozaya: *"From play start maybe? IDK"*. Leading candidate, mine: the switch `Ramp start
  delay counts from` with options `Play start` / `End of the ramp before`. To be heard in
  REAPER's parameter list once built, before it is final.
- A saved project's one ramp becomes Ramp 1, unchanged in sound; Ramps 2-8 start empty.

## Still to decide

- **A ramp PAUSED partway: does the ramp after it wait, or start on time?** Found 2026-09-13
  after the "keeps its place" answer: `Ramp engage` is a pause, not an off switch (Veil's page
  and code, Passage's code: Off holds the ride where it stands, On resumes, only Play
  restarts). Claude asked about "switched off" as a mute, so that answer covers a ramp never
  engaged; a ramp paused mid-ride was not asked. The same question comes from `Rest mode (for
  Ramp)` on Freeze, which also makes a ride finish later.

- The above four.
- Where each new control sits in each plugin's list, per plugin layout doc.

## Traps known before building

- Nested selectors zero the selected target on track duplicate unless `@serialize`
  re-asserts the visible values (`docs/jsfx-gotchas.md`); build that in from the start.
- Set a selector one stage before its values in `jsfx_run` tests.
- A tempo change must land at once in any Beats count (Rozaya, 2026-09-11); rescale counts.
