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
Ramp (1 to 8)
Ramp target
"Everything below this is for one ramp on one target."
Ramp from
Ramp to
Ramp shape
Ramp duration unit
Ramp duration
Slide unit (Off, or a unit)
Slide time
Ramp engage
Ramp play for
Ramp rest for
Ramp at rest (Play through, or Freeze)
Ramp start delay unit
Ramp start delay
'Start delay counts from': from pressing play, from the start of the project, from when the ramp before was planned to end, or from when the ramp before really ended. Per target. On ramp 1, the last two fall back to the start of the project.
Here are notes on the unbuilt bits: 
When a ramp begins before another has ended, it should be allowed to; start delay serves, alone, to let timing be adjusted manually. When it does take over: (claude's words, my agreement; I pasted this in, not it.) "If a ramp begins while another ramp on the same target is still running, the newer ramp takes over. It glides from wherever the control is to its own starting value, using its slide time, then carries on to its end value."

when a ramp is switched off, it shouldn't move other ramps; let the gap exist. 
From claude, pasted by me. "When a ramp runs late, because it was paused or frozen during a rest, the next ramp's start delay switch decides what happens. It has four choices. From pressing play
From the start of the project
From when the ramp before was planned to end
From when the ramp before really ended

From claude, about more new, as yet unbuilt, controls: "Ramp from and ramp to: the ramp starts at one value and ends at another. Old saved ramps convert on their own and sound the same. While a ramp waits out its start delay, the control stays wherever its knob is. When the ramp begins, a slide time glides the control from the knob's value to the ramp's starting value. Slide time has its own unit picker, and Off means jump."
"When a ramp reaches its 'to' value, it stays there."
"Slide: whenever a ramp takes over a control, it glides there first. That happens when a ramp begins, from the knob's value to the ramp's 'from'. It also happens when a ramp overlaps another, from wherever the control is. Slide unit Off means it jumps."

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

## Decided, 2026-09-14

- **A new ramp starts where the control is.** On a brand new ramp, Ramp from and Ramp to
  both start at the control's current value, so switching the ramp on changes nothing until
  you set where it goes. Recommended; Rozaya: *"Yes."*

## Still to decide

- Where each new control sits in each plugin's list, per plugin layout doc.

## Traps known before building

- Nested selectors zero the selected target on track duplicate unless `@serialize`
  re-asserts the visible values (`docs/jsfx-gotchas.md`); build that in from the start.
- Set a selector one stage before its values in `jsfx_run` tests.
- A tempo change must land at once in any Beats count (Rozaya, 2026-09-11); rescale counts.
