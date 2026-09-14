# More than one Ramp -- suite-wide design (2026-09-12, being designed, nothing built)

Every plugin with a Ramp. The design is authored here first; each plugin then gets its
own layout doc and ONE migration (CLAUDE.md). Quoted text is Rozaya's; everything
unquoted is Claude's and is not settled until asked.

## Why

Rozaya: *"I noticed we only have one ramp. That's great for sleep. That's not so great for
waking."* Today each plugin has one linear ramp per target, run once, then held; Ramp
engage and Ramp time unit are one each for the whole plugin (e.g. Passage sliders 57 and
61; Sustain Looper 25 and 29).
*these are Rozaya's words. 

ramp layout for all plugins since claude kept making such a mess he couldn't understand his own notes: 
ramp selecter 
ramp targget selecter 
ramp controls (ramp from, then ramp *to*, replacing the current 'ramp by', then ramp shape, then duration units, then ramp duration.)
ramp engage (per targget, to mimic automation) 
play/rest for controls (per-targget)
switch that determines  what happens for play/rest for (per-target; "play mode, rest mode, both are side-branches hosting: freez, walk through.")

start delay (units, then value, then switch,  "begin start delay: from start of project, or from prior ramp's ending, only for ramps 2 and up). 

When a ramp begins before another has ended, it should be allowed to; start delay serves, alone, to let timing be adjusted manually. 

when a ramp is switched off, it shouldn't move other ramps; let the gap exist. 
From claude, pasted by me. "When a ramp runs late, because it was paused or frozen during a rest, the next ramp's start delay switch decides what happens. It has three choices. Count from the start. Count from when the ramp before was supposed to end. Or count from when the ramp before really ended."
That gives your start delay switch three choices instead of two.


This is for all plugins. 



*now back to claude. Talk with Rozaya about what's below here. slowly.

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
