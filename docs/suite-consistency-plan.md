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

## R26 — No unit locks: every Drift and Ramp amount names its unit (2026-09-11)

Rozaya: *"No unit locks. ever."* On doing it in every plugin: *"Yes, do it your way. I'd
prefer that while we have room"*.

- Every Drift block has `Drift amount unit` beside the amounts; every Ramp block has
  `Ramp by unit` beside `Ramp by`. Both switch with the target and therefore carry NO
  scope mark -- R25 was flipped on 2026-09-15 and only the shared ones say so. One option list for every plugin:
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

### The rules inside the order

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
- **Every pitch is a block:** its unit `{Hz, Semitones, Cents}`, a note name, the
  value, then a fine tune unit and fine tune, with one `Tuning reference (Hz)` per
  plugin. The note name works in every unit, both ways. Every frequency that shapes
  the sound has a block, filters included. A range's two ends are two blocks; two
  sides of one thing are one block behind a target picker, `All` first. Sound the
  plugin did not make takes `Source note`, `Target note` (every unit, once a source is
  set), transpose and fine tune. Spreads are `{Hz, Semitones, Cents}`, never a
  percent of a hidden limit. A Shepard voice is its note in every octave at once, so
  the Shepards take notes and fine tunes only.
- **A control behind a selector says which kind it is -- and only the SHARED ones say so.**
  Rozaya, 2026-09-15: *"instead of cluttering up the majority of controls, we can just mark
  the ones that effect a whole of a plugin's output ... non-global things can safely be
  assumed to be non-global because we've not put that mark there. Less to read."* So a
  control that is one value for every option of its selector ends its name with what the
  "all" is -- `(all targets)`, `(all voices)`, `(all bands)`, `(all slots)` -- and a control
  that switches with the selector says nothing. Never `(global)`: it lies about a drift
  control that is shared across targets but touches nothing else.
  **Where the shared controls outnumber the switching ones, put the group's word at the
  FRONT instead** (`Voice gain`, `Segment length`, `Pitch note name`, `Layer level`) --
  Rozaya: *"you can first-letter nav through the p list"* -- which also ends the block, so
  nothing after it needs a mark. **Measure which kind it is; never read it off a label or a
  comment** (`tools/selector_scope_probe.py`, or a declaration the code makes in more than
  one place and agrees with itself). Do not stack redundant scopes: *"once you're drifting
  or ramping something, you don't need that kind of redundency."* **A rename moves no value,
  so it needs no migration** -- but the plugin's page in `docs/plugins/` changes with it, and
  a new control in such a block is named this way in the same change. History:
  `docs/history/R25.md`.
- **Every control that shapes the sound is a Drift and Ramp target.** Star, 2026-09-10:
  *"all the targets ... that directly affect your sound should absolutely be drift
  candidates."* A target is any control that changes what you hear -- pitch, fine tune,
  tuning reference, gain, output, pan spread and glide, binaural beat, glide time, pulse
  width, filter frequencies, resonance, mix -- **including one that moves in whole steps**
  (an octave shift, a centre octave, a harmonic count). Rozaya, 2026-09-15: *"Yeah, I think
  they should be in the picker for drift, and ramp, for that matter."* Not a target: modes,
  unit selectors, shape pickers, on/off switches, and structural counts such as sequence
  length, octave count, phaser stages or ensemble voices -- **except Rhythm Track's Beats
  per bar**, Rozaya 2026-09-11: *"Beats per bar belongs on there too."* **Play for and Rest
  for ARE targets; Start delay is not** -- Star: *"play for and rest for though I absolutely
  can. that's the featheriest timing trick I can think of"*. Drift and Ramp share ONE list,
  and **target options go in the order of the controls they reach**, never appended to save
  a migration. A new sound-shaping control gets its target in the same change that adds it.
  Check a plugin with `python tools/r24_target_audit.py`; history in `docs/history/R24.md`.
- **A drift steps on its target's own turn.** Rozaya: *"you don't get to say drift this
  thing every two cycles and drift this thing every four. it's being fucked."* A target read
  ONCE PER OCCURRENCE (a breath's length, a note's duration, a segment's length, a pulse's
  on-duration) steps once per occurrence and its period counts occurrences; a target read
  continuously drifts continuously, on a clock. Where a plugin has both kinds,
  `Drift movement {With the target, On a clock}` decides, per target -- on Bubbler and
  Dapple, Rozaya: *"The stepping was deliberately live"*. Seconds and Beats on a stepped
  target run only while the target's own thing happens: *"stop mid-cycle, freeze the clock
  mid-whatever unit, then pick up on the next cycle from wherever the clock was last."*
  Where a plugin has several speeds, `Cycles` counts THAT target's cycles, never the master
  rate's. **Classify a target by READING where the plugin reads it, never by its name** --
  a value recomputed every sample is not thereby continuous; see `docs/history/R23.md`.
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

