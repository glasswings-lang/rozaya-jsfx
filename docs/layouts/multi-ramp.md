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

## Mine, unquoted -- ask before building on them

- Overlapping ramps on one target add together.
- Ramps 2-8 default "counts from" to the end of the ramp before it.
- A saved project's one ramp becomes Ramp 1, unchanged in sound; Ramps 2-8 start empty.
- Whether "counts from" is per ramp or per ramp and target (Start delay itself is per
  target today).

## Still to decide

- The above four.
- What "the ramp before it" means when that ramp is disengaged or empty.
- Where each new control sits in each plugin's list, per plugin layout doc.

## Traps known before building

- Nested selectors zero the selected target on track duplicate unless `@serialize`
  re-asserts the visible values (`docs/jsfx-gotchas.md`); build that in from the start.
- Set a selector one stage before its values in `jsfx_run` tests.
- A tempo change must land at once in any Beats count (Rozaya, 2026-09-11); rescale counts.
