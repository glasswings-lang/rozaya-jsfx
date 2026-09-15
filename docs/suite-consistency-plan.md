# Suite consistency plan — THE RULES

**Budget: 1600 lines.** Run `python tools/doc_budget.py` before committing.

**This file is a reference you check, not a list of work.** It holds the rules
still open (a rule that is done moves to `docs/history/<RULE>.md`), then the canonical layout (Part 2) and the migration strategy (Part 4). Look up
the rule you need, obey it, and close the file. **A rule here does not mean the plugins
obey it** -- R12 said 20000 while two plugins stopped at 96. Read the plugin.

**Where the other two thirds went, 2026-09-08.** This document used to be 2742
lines of three different things stacked together: the rules, a backlog of what
each plugin is owed, and the history of how each decision was reached. Sessions
opened it to check one rule and came back with a to-do list, then started work
Rozaya had not asked for on plugins it had not yet heard. The rules are the
smallest part of what was here and they were the hardest to find — they are
numbered R1 to R22 and they were scattered across five parent sections in
non-numeric order, with R17 buried inside "Where to pick this up" and R18 inside
"Part 6 revised".

- **`docs/backlog.md`** — what each plugin is owed, the phase ordering, the open
  questions. **Nothing in it is a job you may start unasked.**
- **`docs/history/<RULE>.md`** — one rule's history, capped at 200 lines each:
  the shapes tried and killed for THAT rule. Started 2026-09-09 when Rozaya
  asked why there was one history file rather than one per rule.
- **`docs/history/plan-history.md`** — the older general version of the same thing: cost
  measurements, dated status notes, and superseded shapes not yet filed per rule.

Every line of the old document is in one of these three files, verbatim. Nothing
was rewritten in the split.

**The rules are in numeric order.**

---

## The rules, in order

- **R22** — THE PITCH BLOCK, settled with Rozaya 2026-09-08: a pitch value and a pitch mode, adjacent. Built.
- **R23** — A drift steps on its target's own turn
- **R24** — Every control that shapes the sound is a Drift and Ramp target
- **R25** — A control behind a selector says which kind it is
- **R26** — No unit locks: every Drift and Ramp amount names its unit
- **R27** — Every plugin has the same things

---

## The governing constraint

**A migration costs the same whether one thing changes or forty.** Writing the script
that walks a project's slider line from the old layout to the new is a fixed cost per
plugin. Therefore: **everything we want changed in a plugin changes in the same version
bump.** Splitting naming from ordering means paying the migration twice and putting the
project library through two rewrites.

The corollary is that this plan has to decide everything up front, which is what the
rest of this document is for.

**This constraint was broken five times on 2026-09-04** -- the Morpher's 38 projects
migrated three times in one day, Tremolo and the Sweeping Filter twice -- by working
one instruction at a time instead of reading this document first. The operational
form of the rule now lives in `CLAUDE.md` under *How to work here*: **author
`docs/layouts/<plugin>.md` in full before writing any migration for that plugin.**
A migration written before its layout is a migration you will write again.

---


---

## Part 1 — Naming rules

---

## R22 — THE PITCH BLOCK, settled with Rozaya 2026-09-08: a pitch value and a pitch mode, adjacent. Not built yet.

> **ATTRIBUTION WARNING, added 2026-09-09.** Rozaya, on being told that parts of
> this rule were "already settled": *"No, you settled that on your own. I had
> nothing to do with those decisions. That's a problem."*
>
> **It is right, and this section is the worst offender in the repo.** Quoted
> text below is its own. Everything unquoted is Claude reasoning written in the same
> confident voice, and at least three pieces of it were then cited back to it as
> settled decisions:
>
> - **The deferred list.** It said *"Morpher and Passage are their own
>   discussion there."* — two plugins. Sustain Looper and Bubbler are mine.
> - **The build order** — Melody and Shepard Tone's voice selectors before the
>   migration — is my slider-count analysis, not its decision.
> - **"`Note` is NOT one of the modes"** was a JSFX limitation promoted to a
>   principle, and it overturned it on 2026-09-09.
>
> **Before citing anything here as settled, check for quotation marks.** Without
> them it is a proposal that sat still long enough to look like a decision.

**Status: RULE AGREED, NOTHING BUILT.** This is deliberately the R20 order of
operations — write the rule, settle it, *then* build — because that is what
finally worked for the rate after five sessions each guessed differently. The
pitch has more at stake than the rate did: **there is no free window.** Every
pitch value in this suite is in a real project and IS the sound. There is no
equivalent of the nine plugins that had nothing stored on Host x.

## The rule

> **Every pitch carries a mode and a value, adjacent, mode first:
> `Pitch mode`, then `Pitch value`. The mode is always
> `{Hz, Semitones, Cents}` — always those three, always that order. A plugin
> with two pitches has two complete pairs.**
>
> **A plugin that GENERATES ITS OWN SOUND also carries a `Note` picker,
> immediately before the pair, and the pair then reads as an offset from that
> note. One note list everywhere: the FULL MIDI RANGE, C-1 to G9 (128
> notes, 8.18 Hz to 12543 Hz).**
>
> **All four names are R4/R5 compliant** — sentence case, unit in parentheses at
> the end.
>
> The mode says the unit, so the value's name lists none.
>
> **`Fine tune` is a SECOND pair, always present, always after the first:
> `Fine tune mode`, then `Fine tune value`, the same `{Hz, Semitones, Cents}`.**
> It is a finer offset that coexists with the coarse one; it is not the same
> control at a different scale.
>
> **A plugin that pitches audio it did not make — the Morpher, Passage, Sustain
> Looper — has no note to offer. What those three carry is DEFERRED to their own
> discussion (see below); do not settle it from here.**
>
> **A plugin with MORE THAN ONE pitch puts them behind a `Pitch target`
> selector — one block, not N blocks — with `All` as position 0. A plugin with
> one pitch has no selector, because a one-entry selector is a control with
> nothing to choose. Where a selector ALREADY exists over the things that carry
> pitches (Polyrhythm's `Voice`, Resonance Bank's `Band`), the block joins that
> one rather than adding a second.**
>
> **One `Tuning reference (Hz)` per plugin**, with the other global pitch
> controls, not repeated per voice.

This is R20's shape applied to pitch: a value, then a mode saying what the value
means, same options in the same order wherever you meet it.

**`Note` was once argued out of the mode list, and Rozaya overturned it** on
2026-09-09: *"note is not master here. it's one way of expressing pitch,
period."* The argument is in `docs/history/R22.md`.

## Flat notes, and what this buys that nothing in the suite has

The pair is an OFFSET from the note on a self-generating plugin, so `Cents` mode
reaches the pitches BETWEEN the names. Rozaya, 2026-09-08: *"flat notes,
anyone?"*

Nothing in the suite can do that today except Polyrhythm v3, whose `Fine tune
(cents)` was built for exactly this and exists nowhere else. Under this rule
every self-generating plugin gets it, and gets it in three units rather than
one — so a voice can sit a true third above another rather than an equal-
tempered approximation of one, and a drone can be detuned in Hz against a
measured reference rather than by ear alone.

## `Fine tune` is its own pair, always present

**Keep it.** It was once proposed for deletion, on the reasoning that the pitch
value-and-mode pair "does its job and more" — see `docs/history/R22.md`. It does
not, and here is why.

Rozaya, 2026-09-08:

> *"At this specific stage, plugins getting pitch modes doesn't have to mean
> things get lost. It does mean that fine-tuning should have been a feature from
> the start, and that was my oversight. But that's a long way from saying, we
> don't need this control because this other one, requiring more fiddling, looks
> tidier on paper."*

**They are not two ways to say one thing, and the proof is in the fiddling.**
Folding fine tune into the pitch pair means that nudging a voice seven cents
requires switching `Pitch mode` to Cents — which changes what the MAIN pitch
value means — nudging, and switching back. You cannot hold a coarse offset and a
fine one at the same time, because there is only one value. A second pair costs
two sliders and removes a mode-switch from an operation you do by ear, over and
over, while listening.

**"Tidier on paper" is the exact failure mode**, and this is the fourth time in
one sitting the same instinct produced a wrong answer here: the `{Note, Hz}`
mode list, collapsing detune into cents, retiring `Center Octave`, and now this.
It is recorded in CLAUDE.md as a standing correction, not as four incidents.

**Fine tune gets the full mode list too**, and that is not symmetry for its own
sake. Rozaya: *"Rate mode features everything you could possibly want. so should
pitch. so should fine-tune."* A fine tune in **Hz** is how you set a beat
against another voice — plus three Hz IS the beat frequency, and asking for that
in cents means knowing the pitch first. That is arithmetic, which is the barrier.

**And the honest history: fine tune was missing suite-wide, not over-served.**
It exists in exactly one plugin today (Polyrhythm v3), which is why the pitches
between the note names have been unreachable everywhere else. R22 adds it
everywhere; it does not tidy it away.

## Why Hz must stay wide

`Hz` is the mode that has to reach whatever a person is actually working with,
and the suite already spans **20 Hz to 20000 Hz** — Resonance Bank's band
frequency alone goes to 20000. So the Hz end of this control is wide by
necessity, not by generosity.

**20 Hz to 20000 Hz is a PHYSICAL boundary — the audible range — not a usage
one, which is why it is allowed to set this ceiling when the library's stored
values are not.** That is the distinction to apply everywhere: a limit may come
from physics, from a standard, or from what the code can actually honour. It may
not come from what one person has happened to use.

**The reasoning this replaced**, kept so it is not re-derived, is in
`docs/history/R22.md`.

## Why the FULL MIDI range, and why measurement did not decide it

**The note list is C-1 to G9 — MIDI notes 0 to 127, 8.18 Hz to 12543 Hz.** It is
that because that is the standard every other piece of music software uses, and
a standard is a principled boundary. It is NOT sized to anything in this
library.

**Three drafts of this line got smaller and smaller for the same bad reason, and
the correction is a rule, not a preference.** I wrote C1–C7 first (sized to just
cover the stored values), then C0–C8 after Rozaya said *"let's use that to widen
ranges, not reduce them"*. Both were still derived from its projects. It named
what was actually wrong with that:

> *"We've also established, through repeated trial and error, that no, in fact,
> setting things to 'what makes sense' or 'what's already there' is an
> artificial limit based on one user's usage patterns to a public-facing
> suite."*

**So: MEASUREMENT IS A FLOOR, NEVER A CEILING.** The 2026-09-08 scan of all 153
project files found 88 stored Hz-pitch values spanning **40 Hz to 2000 Hz**.
That number's only job is to prove the CURRENT lists are too small — C2–C6 is
65–1046 Hz and reaches neither Dapple's 40 Hz nor the 45 Hz heartbeat. It has no
authority over where the top is. A stranger who installs one of these plugins
has never opened a project in this library.

**A long list is not the cost it looks like.** REAPER's parameter list takes a
typed value (focus, then Tab, gives an editable field), so reaching G9 is not
128 presses of the arrow key. That is R12's own reasoning for abandoning
hand-picked ranges, and it applies unchanged to enum length. A person switching those to Note mode would find the pitch they
already had was not in the list.

**Widening the list is a MIGRATION, not a rename.** An enum option is an index
stored inside a slider's value, so moving the bottom of the list from C2 to C1
shifts every saved note by twelve semitones. Like any move of a picker choice, it
needs its migration in the same commit (CLAUDE.md).

## What falls out for free

Naming changes cost nothing — names are not stored in projects — so these ride
along with whichever plugin is being touched:

- **`Transpose` gets one name.** It is `(half steps)` in Melody and Polyrhythm
  v3 and `(semitones)` in Bubbler. Pick `semitones`: four plugins already use
  that word for the same quantity, and it pairs with the new Semitones mode.
  This is a rename, not a reduction — nothing becomes unreachable.

**Detune gets its own value-and-mode pair, for the same reason pitch does.**
The first draft said "detune becomes cents everywhere", collapsing the four
units in use into one. That is the same reducing instinct that produced the
two-mode pitch list, and it fails the same test: `Pitch spread (%)` in Dapple
and `Spread (Hz)` in the Morpher are not clumsy spellings of cents, they are
different questions with different right answers.

> **`Spread mode` then `Spread value`, always `{Cents, Semitones, Hz, %}`,
> always that order.**

Only one thing is genuinely fixed here: Sustain Looper's `Spread (detune
amount)` is 0-100 with **no unit at all**, so it has to be told which of the
four it means. It is a percentage of its existing internal range, so it becomes
`%` and no stored value moves.

## How this sits with the rules that already exist

**Checked 2026-09-08, after Rozaya said "you need to look at existing rules,
please" — and it was right, two of these I was re-deriving from scratch.**

- **R4 / R5 — names.** Sentence case, unit in parentheses at the end. This
  sweeps up a pile of existing violations in the pitch surface on the way past:
  `Tuning Reference Hz` → `Tuning reference (Hz)`, `S1 Frequency Hz` →
  `S1 frequency (Hz)`, `Inhale Frequency Hz`, `Exhale Frequency Hz`,
  `Fundamental Hz`, `Root Note`, `Center Octave`, `Octave Count`, `Base Note`.
  All free — names are not stored in projects.
- **R6 — mode dependence is annotated once, where meaning changes.** The value
  slider does not need a `(in Pitch mode units)` tag, because under the
  contiguity rule the mode slider is sitting next to it saying so.
- **R7 — contiguity** (done, `docs/history/R7.md`). R22 is R7 applied to pitch:
  mode then value, adjacent, no exceptions, and a second pitch gets its own
  complete pair.
- **R9 — ALREADY SAYS MOST OF THIS, and I did not check before writing it out
  again.** R9: *"Prefer whichever unit makes ordinary values whole numbers:
  percent over fraction, dB over linear gain, **cents or semitones over
  frequency ratios**."* That is the pitch mode list, written down on 2026-08-31.
  R9 also already carries Rozaya's widening principle in its own words: *"This
  rule never removes range or precision, and must not be read as doing so."*
- **R12 — the range, and R12 already decided it.** A numeric slider spans
  0–1000 or −1000–1000, and carve-out 1 says
  *"'1000 or wider' — never a ceiling"* because narrowing permanently clamps
  saved values. Resonance Bank's band frequency already reaches 20000, so the
  Hz end must reach 20000 and **the range is −20000..20000**. R12 decided that
  in August.
- **R17 — no unitless sliders.** Sustain Looper's `Spread (detune amount)`,
  0-100 with no unit, is already condemned by R17's *"x of what?"* test. R22
  does not discover it; it inherits it.

## One pitch block per plugin, behind a target — Rozaya, 2026-09-08

> *"Heartbeat: target, then select from 2, that way you're able to extend it
> later if needed, also less sliders."*

One block per plugin, not one per sound. Heartbeat with a block per thump would
be ten sliders where there are two, and Womb four blocks would be twenty where
there are four — and the count grows every time a plugin gains a sound.

**The selector is the suite's own answer and it was already sitting there.**
`Drift target` and `Ramp target` are one selector over 24 targets; Polyrhythm's
`Voice` is one over eight; Resonance Bank's `Band` is one over its bands. A
`Pitch target` is the same pattern, and it makes the block a FIXED cost: every
plugin has exactly one pitch block no matter how many pitches it has.

**And it is extensible in the way N blocks are not.** A new sound in Heartbeat
adds one enum option, not five sliders — which is the difference between a
feature being affordable later and not.

`All` sits at position 0 for the same reason it does on Polyrhythm's `Voice`:
once per-target is cheap, setting them together becomes the expensive case.

## Filters get notes too — musicality, not classification

> Rozaya, 2026-09-08: *"Filters: yes, they should. Musicality integration, not
> exclusivity, is the idea here."*

I had asked whether a filter CENTRE should get a pitch block, having found that
three of the frequencies I listed as pitches are not tones at all: Resonance
Bank's band centres are peaking-EQ points on incoming audio, and Breath's and
Womb's inhale/exhale frequencies tune a state-variable filter over noise
(`in_f = 2*sin(pi * slider5 / srate)` — a coefficient, not an oscillator).

**The question was the wrong shape.** It asked what a control IS, in order to
decide what a person is allowed to reach for — which is the triage this rule has
already been corrected for twice. The answer is that tuning a resonant band to a
note is a real musical act: a bank tuned to a chord, a breath band sitting under
a drone. The plugin not GENERATING that pitch does not stop it being a pitch you
want to place.

**So every frequency in the suite that shapes what you hear gets the block**,
whether it is generated or resonated. The one thing that stays out is the
source-pitching case (below), and that is not a taste judgement — those plugins
genuinely do not have the information.

## The Morpher and Passage are their own discussion — NOT settled here

Rozaya, 2026-09-08: *"Morpher and Passage are their own discussion there."*

**This paragraph used to say the opposite and was wrong until 2026-09-09.** It
claimed as settled that `Note` cannot be one of the modes, because a plugin that
did not make the audio does not know its pitch. Rozaya overturned exactly that:
*"note is not master here. it's one way of expressing pitch, period."* The
argument is in `docs/history/R22.md` and must not be cited from here again.

What is settled is only the quoted line above: these two are their own
discussion. What they end up carrying is NOT settled, and one draft of this rule
wrote "they carry the pair alone" into the rule statement as though it were.
They are the suite's two spectral plugins, they share a capture mechanism, Passage has an owed reorder blocked on what it is
FOR, and Rozaya has just said its fine-tune surface is part of the answer to
that — *"passage earns a place by having room for a fine-tune control tapping
into those pitch modes (flat notes, anyone)?"*

**Sustain Looper and Bubbler are probably in the same conversation** — Sustain
Looper pitches a file loaded through a file-selector slider, and Bubbler grains
incoming audio (`dryL = spl0`), so neither knows its source pitch either. Rozaya
named two; the other two are noted, not assumed.

**Bubbler was in the buildable list until 2026-09-08 and should not have been.**
I had it down as "one block, detune to cents" without checking whether it makes
its own sound. It does not.

Take those four out of the migration list until that discussion happens.

## R23 — A drift steps on its target's own turn (2026-09-09)

Rozaya, on drift sampled from a free-running clock: *"you don't get to say drift this thing
every two cycles and drift this thing every four. it's being fucked."*

- A target read ONCE PER OCCURRENCE (a breath's length, a note's duration, a bubble's birth)
  steps once per occurrence, and its period counts occurrences. A target read continuously
  drifts continuously, on a clock. *(This wording is Claude's.)*
- Where a plugin has both kinds, `Drift movement {With the target, On a clock}` decides, per
  target. On Bubbler and Dapple, Rozaya: *"The stepping was deliberately live"*.
- Seconds and Beats on a stepped target run only while the target's own thing happens.
  Rozaya: *"stop mid-cycle, freeze the clock mid-whatever unit, then pick up on the next
  cycle from wherever the clock was last."*
- Classify a target by READING where the plugin reads it, never by its name.

---

## R24 — Every control that shapes the sound is a Drift and Ramp target

Star, 2026-09-10: *"all the targets ... that directly affect your sound should
absolutely be drift candidates."* Drift and Ramp exist to replace automation.

- **A target:** any continuous control that changes what you hear — pitch, fine
  tune, tuning reference, gain, output, pan spread and glide, binaural beat,
  glide time, pulse width, filter frequencies, resonance, mix.
- **Not a target:** modes, unit selectors, shape pickers, on/off switches, and
  structural counts such as sequence length -- **except Rhythm Track's Beats per
  bar**, Rozaya 2026-09-11: *"Beats per bar belongs on there too."*
- **Play for and Rest for ARE targets; Start delay is not.** Star, 2026-09-10:
  *"play for and rest for though I absolutely can. that's the featheriest timing
  trick I can think of"*.
- **Target options go in the order of the controls they reach**, never appended
  to save a migration. Star, 2026-09-10.
- **A new sound-shaping control gets its target in the same change that adds it.**
- Drift and Ramp share one target list. A new target goes where it belongs in it, with its migration.

## R25 — A control behind a selector says which kind it is (2026-09-12)

Rozaya, finding Ramp start delay switched with the Ramp target: *"if it's gonna do that,
can't it at least say that's what it's doing?"* Then: *"anything would do at this point,
just don't forget to put this snag in the damn thing in case names come up as another
problem"*. History: `docs/history/R25.md`.

- **Every control in a block with a selector ends its name with which kind it is:**
  `(per target)` when its value switches with the selector, `(all targets)` when one value
  serves every option. A slot, band, layer, voice or segment selector says so the same way
  (`(per slot)`, `(per slot and target)`), and a unit already in parentheses joins it:
  `Ramp start delay (per target, in ramp time units)`.
- **Measure which kind it is; never read it off a label or a comment.** Set it on one
  option, switch, read it back: `tools/selector_scope_probe.py`, live in REAPER.
- **A rename moves no value** (REAPER restores by position), so it needs no migration --
  but the plugin's page in `docs/plugins/` changes with it.
- **A new control added to such a block is named this way in the same change.**

---

## R26 — No unit locks: every Drift and Ramp amount names its unit (2026-09-11)

Rozaya: *"No unit locks. ever."* On doing it in every plugin: *"Yes, do it your way. I'd
prefer that while we have room"*.

- Every Drift block has `Drift amount unit (per target)` beside the amounts; every Ramp
  block has `Ramp by unit (per target)` beside `Ramp by`. One option list for every plugin:
  `{Target default, Hz, Semitones, Cents, Milliseconds, Seconds, Minutes, BPM, Beats,
  Cycles, dB, Percent, Degrees}` (Rozaya: *"Yes"*).
- `Target default` is what the amount meant before, so a migrated copy sounds the same. A
  unit that cannot fit its target acts as Target default (Rozaya: *"It should fall back to
  the target's native unit, if one's not already been set"*).
- A unit is at most a default, never a lock, in any control.
- Built in Passage and the Morpher, 2026-09-13; their `au_*` functions are the conversion.

---

## R27 — Every plugin has the same things (2026-09-13)

Rozaya: *"They should all have the same things"*.

- **Transport:** Start delay, Play for and Rest for, sharing ONE `Transport unit` that
  defaults to what the plugin counts in today (cycles, beats, breaths, steps; Seconds where
  it has no turn) and offers Seconds and Beats. Rozaya: *"Yes. should have had that from the
  beginning."*
- **At rest:** where something moves, Walk through and Freeze in place are both offered
  (*"those two things are not either/or"*). Where the plugin works on incoming sound,
  `Output at rest {Pass-through, Silence}` (*"Feels like you'd want that as a switch"*). A
  plugin that only makes its own sound has nothing to pass: read its `@sample` to tell.
- **`Rest mode (for Drift)` and `Rest mode (for Ramp)`, two switches, in every plugin with
  both** (19): *"Drift is its own thing. ramp is its own thing"*; *"all of them should get
  both"*. A plugin's own-motion switch (LFO, walk) stays too. Ramp's is per ramp. Each sits
  IN the block it freezes (Rozaya: *"Otherwise we get slider scatter stuff"*), not in transport.
- **Every pitch spread takes a value and a unit picker** `{Hz, Semitones, Cents}`.
- It lands inside each plugin's one amount-unit migration (R26), never as a second pass.

---

## Part 2 — Canonical layout

**REWRITTEN AND APPROVED BY ROZAYA 2026-09-05.** The A/B/C/D block structure this
section used to describe was thrown out on 2026-08-31 (Star: the blocks "were
arbitrary as shit") and the replacement was never written down — so for five
days every per-plugin layout was being measured against a ruler nobody believed
in any more. That is the single thing that made the sweep feel unnavigable.

Sliders are read in **numeric order** regardless of declaration order in the
file, so this is reading order, and reading order is the whole interface. Rozaya
arrows the parameter list one control at a time.

### The order

This was not designed top-down. It is what the Sweeping Filter and Tremolo
layouts independently came out as when authored by hand, described afterwards
and then approved:

```
1. What the plugin IS          its identity — the sound, the frequencies, the voices
2. Its rate                    rate mode, then rate value          (the rate pair)
3. The shape of its movement   depth, on-duration, attack + its shape, release + its shape
4. Stereo and pan
5. Output level                wet/dry mix, output volume
6. Transport                   start delay, play for, rest for, what happens at rest
7. Drift                       target, up, down, period, period unit, shape, play/rest
8. Ramp                        target, by, time unit, duration, play/rest, engage, start delay
```

**Why Drift and Ramp are last, and it is not because they matter least.** Their
selectors reach across every other group — a drift target list names controls
from sections 1, 3 and 4 — so they cannot sit *inside* any one of them without
lying about their scope. Transport goes above them because it is also
plugin-wide but simpler, and you set it once and leave it.

### The four rules inside the order

- **Everything belonging to a layer lives with that layer.** A per-voice,
  per-band or per-slot group is whole and contiguous, and its own rate, gain,
  timing and toggles sit inside it. This is what replaced the old block
  structure: the grouping follows the *thing*, not an abstract category.
- **A mode or unit comes immediately BEFORE the value it qualifies.** Rozaya,
  2026-09-14: *"every thing with a mode gets the mode before the value.
  everything. I don't care what it is."* So `Drift period unit` goes directly
  before `Drift period`. A shape
  selector (`Attack shape`) is not a mode and goes AFTER its value. Rozaya,
  2026-09-14: *"They'd universally go afterward. except where there's durations
  and other stuff in the way. then they go under all that"*. **Switching a mode or
  unit keeps the thing the same and converts the number**, wherever that is exact;
  where it is not (Cycles of a speed that may drift), the number stays.
- **Every speed is a pair, `<name> mode` then `<name> value`,** and its mode is
  always `{BPM, Seconds, Hz, Every N beats, N per beat}`, in that order, in every
  plugin: `Every N beats` is one cycle per N beats, `N per beat` is N cycles in one
  beat, so whole numbers work at both ends. A second speed -- the
  pan's, a voice's -- carries its own complete pair, inside its own group: never the
  main rate's mode, and nothing points across at it. No sync switch, no host-sync
  target, no multiplier, and no control that writes a value into another. Retiring
  one of those: open the block first, and move a working half's number, not delete it.
- **Global output goes last before transport**, so it stops interrupting the pan
  group — which is exactly where the Sweeping Filter's `Wet/dry mix` sits today,
  at slider 15.

### What this fixes on its own

`Slope` stops being slider 41 and rejoins the frequencies. Womb's `Breaths per
minute` stops being wedged between the ramp and drift blocks and rejoins the
breath group. `Heart rate swing per breath` rejoins the heart group. `Direction`
stops splitting Melody's transport trio. Sweep Dwell's ramp block becomes
walkable. Every stranded rate mode comes home to sit under its own rate.

That the order resolves nearly every ordering finding in this document without
being aimed at any of them is the evidence that it is the right shape.

---


---

## Part 4 — Migration strategy

### What each kind of change actually costs

Not every fix in this document is expensive. The escalation, cheapest first:

| Change | Cost | Why |
|---|---|---|
| **Slider label** | free | REAPER restores by ID, never by name |
| **Target option string** | free | same — the enum's *index* is what is stored |
| **Step size** | near-free | affects the increment, not the stored value; verify one project for snapping |
| **Adding a slider at the END** | near-free | absent from old projects, so it takes its default — seed that default to reproduce the old behaviour |
| **Range** | risky | saved values outside the new range are clamped, silently and permanently |
| **Renumbering** | needs an `.RPP` migration | values are restored by position |
| **Target enum order or count** | needs a blob migration | per-target banks are indexed by target number |

This ladder is why Phase 1 exists: rules R1–R6, R8's "accident" half, and R9 sit entirely
in the top three rows. They can ship without touching a single project.

### Two things break independently, and they need different treatment.

### The slider line — an `.RPP` text migration

REAPER restores plugin values by slider **position**, so renumbering rewrites every
project. This is the expensive half, and it is also the **easy** kind of migration to
generate, because the old→new mapping is *authored* rather than inferred: we decide the
layout, so we know the permutation exactly.

Worked shapes already exist: `tools/passage_migrate_sliders.py` (HOPS table walked in
order, so a project several layouts behind migrates through in one run) and
`tools/sweepfilter_migrate_hz.py`.

Hard-won details that carry over unchanged (see CLAUDE.md):

- Index the slider line by **token position**, never by "values with the `-` padding
  stripped" — REAPER writes `-` between real values, not only as trailing padding.
- Gate on something that distinguishes migrated from un-migrated. Slider **count**
  usually does not change; the blob's version magic can.
- Do not require sliders that only exist on newer layouts.
- Seed any new slider to whatever **reproduces the old behaviour**, not to the plugin's
  default. The project should still sound like itself.
- Snapshot whole projects into their own folder first; per-file `.bak` is the second
  line, not the first.
- Verify afterwards that **only the intended tokens moved**.

### The `@serialize` blob — mostly untouched, with one trap

The blob is a raw memory dump with no notion of slider numbering, so **renumbering
sliders does not touch it**. Captures, banks and per-target drift configs all survive a
layout change for free.

The trap: per-target drift and ramp configs are stored in memory banks **indexed by
target number**. So changing a target enum's *order* silently repoints every saved
config at the wrong target.

**So reordering a target list, or putting a new target where it belongs, needs a migration
that moves each saved config with its target** (CLAUDE.md).

### The plugin migrates itself — the script is a convenience, not the safety net

**A migration script only protects projects you actually run it over.** Anything on
another drive, an old backup, a project reopened in 2029 — loads with every value in the
wrong slot, silently, with nothing to signal it. That is worse than the mess we are
fixing, and it is the reason the script cannot be the correctness mechanism.

`@serialize` is the one section guaranteed to run on both **load** and **track
duplicate**, and inside it `file_avail(0) >= 0` means read while `< 0` means write. So on
read, a plugin can detect that the values it has just been handed belong to the *old*
layout, permute them into the new positions itself, and push them back with
`sliderchange(-1)`.

It cannot rewrite the project file's slider line — but it does not need to. It fixes the
values in memory every time the project opens, on any machine, forever, with nothing for
anyone to run. The bulk script stays useful for repairing the library in one pass so the
files on disk are correct too, but nothing depends on remembering to run it.

**Mechanics, and the traps:**

- **Gate on the blob's version magic**, and migrate only what was *restored*, never what
  was *defaulted*. This is the exact bug that hit the Morpher layer permutation on
  2026-08-19 — the gate asked "is this blob old?" instead of "does this blob actually
  contain the thing I am about to permute?", so `@init` defaults got permuted.
- **Use `sliderchange(-1)`, never `slider_automate`** — the latter writes automation.
- **Read the blob in one go rather than sequentially.** `n = file_avail(0);
  file_mem(0, scratch, n);` then inspect `scratch[0]` for the magic. Sequential `file_var`
  reads advance a cursor that cannot be rewound, so a plugin that guesses wrong about the
  format has already destroyed its own ability to fall back.
- **Idempotence falls out for free.** If the project is loaded and not saved, the file on
  disk still holds the old layout and the old magic, so the next load permutes again —
  correctly. Save once and both the slider line and the magic are current.
- **CORRECTION 2026-09-04 — the permute must happen in `@block`, NOT in
  `@serialize`, and this section as written would have shipped the bug it warns
  about two bullets earlier.** `@serialize` and REAPER's restore of the slider
  LINE are two independent paths with no guaranteed relative order (the
  nested-selector gotcha in CLAUDE.md, and the adopt-on-first-`@slider` gotcha
  that followed it). A permute running inside `@serialize` can therefore read
  slider values that have not been restored yet, permute the `@init` DEFAULTS,
  and push them back with `sliderchange(-1)` — which is exactly "migrate what
  was DEFAULTED", the failure this document already tells you to avoid.

  **The shape that works, and it is the one already proven here for the picker
  bug:** `@serialize` only READS the blob and RAISES A FLAG. It touches no
  sliders. Then the first `@block` after that does the permute and the
  `sliderchange(-1)`. `@block` cannot run before the instance is configured, so
  whatever order the restore paths ran in, the values it sees are the real ones.

  ```
  @serialize
    n = file_avail(0);
    n > 0 ? (
      file_mem(0, scratch, n);          // whole blob, one read, cursor-safe
      scratch[0] == OLD_MAGIC ? pending_layout_migration = 1;
    );
    // ... normal restore ...

  @block
    pending_layout_migration ? (
      // permute the visible sliders old -> new, THEN:
      sliderchange(-1);                 // never slider_automate
      pending_layout_migration = 0;
    );
  ```

  **`pending_layout_migration` must be set in `@serialize` and cleared in
  `@block`, and must NOT be initialised in `@init`** — `@init` re-runs on every
  transport play in most of this suite, and clearing the flag there would let a
  play press eat a migration that had not happened yet.

- **Projects with no blob at all** cannot be identified this way. Those need the bulk
  script. Worth measuring how many exist before assuming it is nobody.

### Versioning

Per the standing rule in CLAUDE.md: **a new version must ship with a migration, or it
does not ship.** Melody Phase v2 is the proof — better design, zero projects, no path
across.

Old versions move to `archive/versions/<plugin>/`, out of `src/`, out of
`docs/plugins/README.md`. Not alongside. Two live versions is a permanent maintenance
cost.

**Before archiving anything, run the grep** — a successor existing is not evidence that
anyone crossed over. Melody Phase v1 was archived while five projects were on it and
zero on v2, and had to be brought back out.

```bash
grep -rl <plugin>.jsfx --include=*.RPP /e/reaper
```

---

### No releases until the sweep is finished

Rozaya, 2026-08-31: *"We're not tagging releases until this is done. It's bad enough that
the previous release is what I'd consider half-done. We can absolutely push stuff to
remote. Just not make a release out of it. That's what people grab when they don't want to
deal with source code."*

**Pushing to `origin` is fine and should continue** — it is what makes the work survive a
dead disk, and it is addressed to us. **Tagging and publishing a release is a different
act**: it is a distribution artefact aimed at someone who will never read the source, and
shipping one mid-sweep hands a stranger a suite that is half-renamed, half-reordered and
inconsistent with its own documentation.

This corrects Phase 0 as I originally wrote it. Phase 0's value was the **push** — the
tag and the release added nothing to "if this stops, is the work safe." I bundled three
different actions under one heading and only one of them was protective.

**Standing rule for the rest of this work:**

| action | during the sweep |
|---|---|
| commit | freely |
| push to `origin` | freely |
| annotated tag | no |
| GitHub release | **no** |

The next release is the one that ships the finished sweep, and it should be the first
thing a stranger could download and find self-consistent.

