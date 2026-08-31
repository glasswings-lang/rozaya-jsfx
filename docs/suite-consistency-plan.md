# Suite consistency plan

Started 2026-08-28. Planning document — nothing here has been built yet.

## Why

The suite has been swept four times — Speed Ramp (2026-05-30), per-plugin Drift
(2026-06-01), the nested-selector Drift conversion (2026-06-12), and Host x sync
(2026-08-11 onward). Each sweep landed slightly differently, and the plugins written
between sweeps missed the earlier ones. Nothing is broken in the DSP. What has drifted
is the **interface**, which for a screen-reader user is the entire plugin.

An audit on 2026-08-27/28 found the damage falls into four kinds:

1. **Target lists name sliders that do not exist.** Womb's drift/ramp selector has ten
   options and all ten name something other than the slider they modulate — `Heart rate`
   points at a slider called `BPM`, `RSA depth` points at `Heart with breath (BPM
   peak-to-peak)`. Sweeping Filter offers `Sweep Rate` and `Pan Sweep Rate` as apparent
   siblings; only the second is a real slider. Breath Generator offers `Breaths/min` for
   a control it does not have at all.
2. **Ordering reflects when a feature was added, not what it belongs with.** `Slope` is
   slider 41 in Sweeping Filter and slider 5 in Veil. Morpher's `Capture average` is
   slider 28 while the rest of its Capture group is 1–3. Sweep Dwell's Speed Ramp block
   is the only block in the suite that cannot be walked contiguously.
3. **The same concept is worded and cased differently** in different plugins, and
   sometimes within one file — every plugin that has both carries `Start Delay` and
   `Speed ramp start delay`.
4. **Docs are stale in a traceable pattern**: a change landed in source and in at most
   one doc page. Bubbler and Dapple's entire Host x feature is undocumented. Both
   Polyrhythm pages list 12 waveforms against a source with 14.

### The structural finding

Every plugin with host sync gets **two of the three rate controls adjacent and strands
the third.** Which two depends only on which sweep added them.

| | rate slider | Rate Mode | Host ratio |
|---|---|---|---|
| Tremolo | 1 | 2 | **34** |
| Sweeping Filter | 3 | 4 | **39** |
| Shepard Tone | 3 | 2 | **74** |
| Melody Phase (v1, v2) | 2 | 1 | **77** |
| Polyrhythm Phase | 3 | 2 | **84** |
| Womb | **1** | 62 | 63 |
| Heartbeat | **1** | 34 | 35 |
| Shepard Scale | **1** | 62 | 63 |
| Rhythm Track | **1** | 27 | 28 |

`Rate Value` reads as a meaningless name ("value of what rate?") only when it is
orphaned from the Rate Mode that says what mode it is in. The fix is adjacency, not a
rename. This is the clearest single argument for a canonical layout: no amount of
renaming fixes a control that is sixty sliders from its partner.

## The governing constraint

**A migration costs the same whether one thing changes or forty.** Writing the script
that walks a project's slider line from the old layout to the new is a fixed cost per
plugin. Therefore: **everything we want changed in a plugin changes in the same version
bump.** Splitting naming from ordering means paying the migration twice and putting the
project library through two rewrites.

The corollary is that this plan has to decide everything up front, which is what the
rest of this document is for.

---

## Part 1 — Naming rules

### R1. The descriptive name wins, and propagates to both ends

Where a slider and a target list name the same thing differently, keep whichever tells a
stranger what the thing **is**, and push it to both. The winner is sometimes the target
list and sometimes the slider:

| Plugin | Slider today | Target today | Winner | Becomes |
|---|---|---|---|---|
| Womb | `BPM` | `Heart rate` | target — "BPM of what?" in a plugin with a heart, a breath and bloodflow | slider → `Heart rate (BPM)` |
| Womb | `Heart with breath (BPM peak-to-peak)` | `RSA depth` | **neither** — one is jargon, the other is vague | both → `Heart rate swing per breath (BPM)` |
| Sweeping Filter | `Rate Value` | `Sweep Rate` | target — and it makes `Sweep Rate` / `Pan Sweep Rate` genuine siblings | slider → `Sweep rate` |
| Shepard Scale | `BPM (or multiplier in Host x)` | `Tempo` | target; Rhythm Track already writes `Tempo (BPM…)` | slider → `Tempo (BPM…)` |
| Breath Gen | `Inhale Duration (sec)` | `Inhale` | slider — the plugin also has Inhale Frequency and two Inhale fades | target → `Inhale duration` |
| Tremolo, Shepard Scale, Sweeping Filter | `Attack %` | `Attack %` | Polyrhythm's and Melody's longer forms — "percent of what?" | → `Attack % of cycle` / `Attack % of note duration` |

`Rate Value` is **kept** where the rate triple is contiguous (see R7). It is only
illegible when orphaned.

### R2. Target strings are derived from slider labels, mechanically

> A target option string is the slider's label with its trailing parenthetical removed.

`Heart rate (BPM)` → target `Heart rate`. `Sweep rate` → target `Sweep rate`.

This is the rule that makes the whole thing **enforceable**: a linter can strip the
parenthetical from every slider label and assert that every target option matches one.
Without a mechanical rule this drifts again within two sweeps.

### R3. Every target must have a slider

A target list may not offer something the user cannot see or set. Two consequences:

- **Breath Generator gains `Breaths per minute`.** It is the dedicated breathing plugin
  and it currently lets you drift and ramp a rate it gives you no way to set. Womb has
  had this slider since v2.
- Where a target names one entry of a **selector-backed group** (Melody v2's `Voice`
  selector, Morpher's `Layer` selector), the target string is `<selector option> <slider
  label minus parenthetical>` and the plugin page must say it is reached via the
  selector. This is the one legitimate case of a target with no dedicated slider. See
  Open Question 1.

### R4. Units go in parentheses at the end of the name

`Frequency low (Hz)`, not `Frequency Low Hz`. Currently the suite runs both forms, plus
a mixed form (`Inhale Duration sec (shape only in Host x)` -- since fixed, see the
2026-08-30 addendum). Four different spellings
exist for a cutoff frequency in Hz across four plugins.

Additional qualifiers go inside the same parenthetical after the unit:
`High cut (Hz, 20000 = off)`.

For **enum** sliders the unit belongs in the name and the options stay bare —
`{-12,-24,-36}Slope (dB/oct)` — so NVDA does not re-read the unit on every arrow step.
This is already the convention (2026-07-09); it stays.

### R5. Sentence case throughout

`Start delay`, not `Start Delay`. `Drift mode`, not `Drift Mode`.

The suite currently uses Title Case for the transport block and sentence case for the
drift/ramp blocks, which is why `Start Delay` and `Speed ramp start delay` sit in the
same file. Sentence case is the newer convention and the larger block.

**Note honestly: this is a source-consistency fix, not an accessibility one.** NVDA does
not announce capitalisation. It matters for whoever reads the code, including us.

### R6. One phrasing for mode dependence, and only where meaning actually changes

Six phrasings are in use today (`(or multiplier in Host x)`, `(shape only in Host x)`,
`(Host x only)`, `(Host x; writes …)`, `(Own BPM only; …)`, `(in Rate Mode units)`).

New rule: annotate a slider **only where Rate Mode changes what it means**, not merely
what it scales — and use one form, `(… in Host x)`. Womb's four breath durations
genuinely become shape-only, so they keep an annotation. A rate slider that merely
becomes a multiplier does not need one, because under R7 the Rate Mode slider is sitting
right next to it saying so.

### R7. The rate triple is contiguous, always

`<rate slider>` → `Rate mode` → `Host ratio`, in that order, adjacent, no exceptions.
This is what makes `Rate Value` legible and it is what dissolves the `Sweep Rate` /
`Pan Sweep Rate` confusion.

Applies to the secondary rates too: `Pan sweep rate` → `Pan sweep rate mode`. Note the
current suite calls this one `Unit` where the primary is called `Mode`; standardise on
**`mode`**. Sweep Dwell's pan unit offers `Host x` and the other two filters' do not —
they should all offer it.

### R8. Step size is chosen from the range, not typed

Step sizes across the suite do not correlate with range, concept, or precision. They are
authorial accident. The proof is `Start delay`: the same concept with the same range
`0..1000` in all thirteen plugins that have it, at step **0.001** in nine and **0.01** in
four. Nothing else about those sliders differs.

The same range appears at different steps for the same control elsewhere — `Drift up
amount` over `0..100` at step 0.01 (Tremolo, Polyrhythm, Shepard Tone) and at step 0.1
(Shepard Scale); `Speed ramp by` over `-1000..1000` at step 0.001 (Tremolo, Melody,
Polyrhythm, Shepard Tone) and at step 0.1 (Veil).

**Rule: the step is set by the finest adjustment you would ever want to make. The range
is set by the widest value you would ever want to reach. How many positions that produces
is not a problem to be solved.** Where two plugins disagree on the step for the same
control, **take the finer one.**

An earlier draft of this rule said the opposite — that a slider should land in roughly
100–1000 positions, and that a million positions meant the precision was fictional. That
was wrong, and the reason it was wrong matters:

**CORRECTED 2026-08-31 (Star).** An earlier version of this paragraph claimed you can
only arrow in the parameter list, never type. That is wrong: focus a parameter, Tab, and
there is an editable value field — and in the FX dialog you can type into the box beside
the slider. **Typing is available in both places.**

The rule survives the correction, but for a different and better reason. What a step
controls is not how far you have to travel — you can always type — it is **which values
exist at all**. A step of 0.1 where 0.05 is needed means 0.05 cannot be set by any means,
typed or arrowed, because the control quantises to the step. So a coarse step does not
make a value awkward to reach; it deletes it.

And the position count stops mattering entirely. A slider spanning 0.01 to 1000 at step
0.01 is 100,000 positions and is perfectly usable: you type the number you want, then
nudge by ear from there. This is what makes **one slider serve two units** viable —
Systole as milliseconds in Own BPM and beats in Host x on a single 0.01–1000 range —
where an arrow-only reading of the constraint said it needed two sliders.
(Star, 2026-08-31: *"you don't need extra sliders or anything. You can just trust the
ears."*)
(Rozaya, 2026-08-28: *"I want the full range of stuff, and I want it to have the fine
grain control, not the hundredfold bullshit."*)

Standardising downward — always to the finer step — can only ever add reachable values.
It cannot remove a setting from any existing project, so it stays Phase 1 work.

There are two distinct causes and they need different fixes.

**Accident** — `Start delay`, `Drift period` (four conventions for one slider),
`Output (dB)` at 0.5 in Veil and 0.1 everywhere else. Pick one, apply it, done.

**Structural** — dual-purpose sliders whose range must span the union of everything they
can mean: `Speed ramp by`, `Drift up/down amount`, and `Vn Drift / Rate` (drift in Drift
mode, rate in Independent mode). The range goes wide to reach the largest meaning and the
step goes fine to reach the smallest, and the result serves neither. The cure is in Open
Question 2: size the slider to the largest sensible *change*, not the largest target, and
bring the targets into a comparable magnitude. **Not** by normalising the units away.

### R9. Where a natural unit forces a bad range, change the unit

The suite already contains both halves of this lesson. `Stereo width` is `0..1` step
`0.01` in Breath Generator and `0..100` step `1` in the spectral pair. Identical
precision, a hundred positions either way — but one speaks in **0.35** and the other in
**35**, and `docs/dyscalculia-accessibility-sweep.md` names decimals-without-magnitude as
the actual barrier.

Prefer whichever unit makes ordinary values whole numbers: percent over fraction, dB over
linear gain, cents or semitones over frequency ratios. JSFX sliders are linear only, so
the unit is the only lever available for making a wide span navigable.

**This rule never removes range or precision, and must not be read as doing so.**
`0..1` step `0.01` and `0..100` step `1` are the same control with the same hundred
positions; only the notation differs. A change under R9 that costs resolution, or that
replaces a real quantity with a proxy scale, is out of scope — see Open Question 2, where
exactly that was proposed and rejected.

---

## Part 2 — Canonical layout

Sliders are read in **numeric order** regardless of declaration order in the file, so
this is reading order. Every plugin follows the same relative shape, so what is learned
in one transfers to all of them.

```
A. Plugin-specific controls
     A1. primary sound / identity
     A2. the rate triple (rate, rate mode, host ratio) — contiguous
     A3. per-voice / per-band / per-slot groups
     A4. global output (level, wet/dry, output mode) — last in A
B. Transport
     Start delay → Play for → Rest for → Rest mode
     (or, for effects: → LFO at rest → Output at rest)
C. Drift
     target → up amount → down amount → period → period unit → shape → restart
D. Speed ramp
     target → by → duration → engage → start delay
```

### Rules inside section A

- **A modifier is numbered immediately after the thing it modifies.** Unit selectors,
  shape selectors, mode selectors, "…and its partner" pairs. This is the rule that moves
  Veil's `Drift period unit` from 17 to directly after `Drift period`, and moves
  `Pan speed (Linked Sweep)` next to `Filter speed multiplier (Linked Sweep)` in all
  three filters (currently declared adjacent, numbered 30-odd sliders apart — a real
  conflict between source order and reading order, and reading order wins).
- **Groups stay whole.** Morpher's `Capture average` rejoins `Capture point`. Sweep
  Dwell's cycle-length group rejoins its dwell/fade timings. Polyrhythm v1's five tone
  sliders rejoin the waveform group, as v3 already does.
- **Global output goes last in A**, so Resonance Bank's `Mode` / `Wet/dry mix` /
  `Output volume` stop being numbered after the per-band drift block.

### What this fixes on its own

Womb's `Breaths per minute` stops being wedged between the ramp and drift blocks and
rejoins the breath group. `Heart rate swing per breath` rejoins the heart group.
`Direction` stops splitting Melody's transport trio. `Slope` stops being slider 41.
Sweep Dwell's ramp block becomes walkable. Every stranded Host ratio comes home.

That the layout resolves nearly every ordering finding independently is the evidence
that it is the right abstraction.

---

## Part 3 — Missing features, added in the same bump

Free once we are migrating anyway; expensive as separate version bumps later.

| Plugin | Gains | Note |
|---|---|---|
| Breath Generator | `Breaths per minute` | R3; it already offers the target |
| Resonance Bank | full Speed Ramp block | the only plugin with Drift and no ramp |
| Veil | Start delay, Play/Rest | has drift + ramp, no transport |
| Morpher, Passage | Start delay, Play/Rest | same |
| Bubbler, Dapple, Stereo Phaser | Drift + Speed Ramp | got Host x, never in the drift sweep |
| Tremolo, Sweeping Filter | `Host x` on the pan rate mode | Sweep Dwell already has it |

Confirm each against use before building — Harmonic Sculptor and Sustain Looper are
sound-design tools and are deliberately left out.

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

**Therefore: target enum order is frozen. Only the strings change.** New targets
**append** to the end of the enum, never insert — the same rule as sliders, for the same
reason.

Where a target list's order disagrees with its sliders' order (Sweep Dwell lists High
dwell, Fade down, Low dwell, Fade up against sliders 3, 5, 4, 7), **the slider numbering
bends to match the enum**, not the reverse. Since we are renumbering anyway this is free,
and it keeps the blob untouched.

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

## Part 5 — Tooling, built first

The tool is what makes a 22-plugin renumber survivable, and it is also what stops this
rotting a fifth time. Build before touching any plugin — subject to the boundary in the
next section, which is not optional: tools apply authored decisions and report findings.
They never make the decisions, and they never certify the result.

### What tooling is allowed to be, and what it must never be

Star, 2026-08-31: *"scripts are notoriously awful at introducing glitches that nobody
thinks to check for, because the script seems like it works. So everybody assumes it
worked and never double checks the output. As a noncoder, I need you to double check the
output."*

This repo already has the evidence — three bugs in two days from loose pattern matching:
a `grep "^slider"` that also matched `slider_show`, a `.count()` that matched a longer
line containing the target, and a `startswith("slider")` that dropped a declaration inside
`@sample`. All three scripts ran clean and wrote a wrong file.

**The line is between a script that DECIDES and a script that APPLIES.**

- **Never let a script infer from source.** A regex over `.jsfx` that works out which
  sliders to move, or what a name should become, is a script exercising judgment — and
  when its pattern is subtly wrong it does not fail, it silently does the wrong thing to
  the right-looking file.
- **A script may apply an explicitly authored list.** The permutation table for each
  plugin is written out by hand, slider by slider, and the script only carries it out
  over the `.RPP` files. The plan already relies on this: the old→new mapping is
  *authored*, not inferred. Eight project files at sixty-odd tokens each is precisely
  the work a machine should do and a human should not.
- **The safe form of an edit is an exact literal match with a count assertion.** Match the
  full text, assert it occurred exactly once, fail loudly otherwise. That cannot silently
  hit the wrong line — which is the entire failure mode above.

**And the report is about the OUTPUT, never the run.** "The script completed" and "the
linter says zero problems" are not results. What counts is: diff the before and after,
assert only the intended tokens moved, read a sample by hand, and say what was actually
looked at. A clean exit is the weakest possible evidence, and a lint that reports nothing
is the easiest thing in the world to trust wrongly.

**Which downgrades Part 5's linter from a safety net to a lead generator.** Its checks are
worth having because a false report costs a glance while a missed one costs a session —
but nothing may be declared correct because a tool did not object.

### `docs/layouts/<plugin>.md` — one authored layout per plugin

**Where the per-plugin work lives.** Each plugin gets a file holding, together:

- **what changes and why**, one numbered reason per problem being fixed
- **the new reading order** as a table, new number against old
- **the migration** — both halves, positions and any values whose meaning changes
- **status**: draft / order approved / built / ear-tested

Written **by hand**, per the boundary above. This is the artefact that gets reviewed
before anything is touched, and reviewing a reading order is something Rozaya can do
directly — it needs no code reading, which is exactly why it is the review gate.

Done: `melody-phase.md` (order approved 2026-08-31, not built).

### `tools/suite_layout.py`

Holds the canonical layout and, per plugin, the section assignment for each slider.
Emits:

- the new numbering
- the old→new permutation table, ready to hand to the migrator
- a human-readable before/after reading-order diff, for checking by ear-of-the-mind
  before anything is written

### `tools/migrate_layout.py`

Consumes a permutation table and rewrites `.RPP` slider lines. Token-position indexed,
CRLF preserved, idempotent, gated so it is safe to re-run over a folder, backs up first.
One tool plus 22 tables, instead of 22 hand-written migrations.

### `tools/jsfx_lint.py` — new checks

The existing linter catches everything that bites at **load** time (paren balance, empty
`()`, case-folded names, scientific notation, reserved-variable writes, misplaced slider
declarations). Every check below catches something that bites **months later, by ear,
alone**:

1. **Target ↔ slider** (R2): every target option matches a slider label with its
   trailing parenthetical stripped. Catches all of Womb's ten, Sweeping Filter's
   `Sweep Rate`, Breath Gen's phantom `Breaths/min`.
2. **Doc coverage**: every `sliderN:` in source appears on that plugin's page. Catches
   Bubbler and Dapple's undocumented Host x, and `Pan speed (Linked Sweep)` in all three
   filters.
3. **Doc accuracy**: documented default and range match source. Catches Morpher's
   `Layer level` (page says -60, source says 0, and the same page contradicts itself
   forty lines earlier), Heartbeat's two wrong defaults, and the four pages still
   documenting the old narrow rate ranges.
4. **Doc counts**: "N options" / "N targets" / "N parameters" against the real count.
   Catches both Polyrhythm pages claiming 12 waveforms against 14.
5. **Layout**: blocks B/C/D present, contiguous, in canonical internal order.
6. **Casing** (R5) and **unit placement** (R4).

Lockstep is currently a rule in CLAUDE.md with nothing enforcing it. Checks 2–4 are what
turn it into a rule with teeth.

---

## Part 6 — Order of work

**Phase 0 — tooling and this document.** No plugin changes.

**Phase 1 — naming and steps. Costs no migration.** Slider labels, target strings, and
step sizes all sit in the top rows of the cost ladder above. Ship it on its own and get
the largest legibility win immediately, before committing to the expensive part. This is
the exception to the governing constraint, and the only one.

Included:

- **R1–R6** — every naming fix, slider labels and target strings alike.
- **R8** — one step per concept, always the *finer* of whatever is already in use
  (`Start delay` to 0.001, `Output (dB)` to 0.1, drift amounts to 0.01 or below), plus
  the amount sliders that are currently coarser than the controls they modulate.
- **A version stamp in every plugin's `@serialize`.** Free, changes nothing audible, and
  it is what the self-migration above depends on — a plugin cannot tell an old project
  from a new one without it, and it has to be in the field *before* the renumber, not
  alongside it. Where a plugin already serialises without a magic, add it using the
  read-in-one-go technique so legacy blobs are still recognisable rather than scrambled.

Excluded: anything that moves a **range**, which clamps saved values permanently. That
belongs in Phase 2 with its migration.

The sequencing is the point: the cheap, safe phase is also what makes the expensive phase
safe.

**Phase 2 — layout renumber plus migrations.** The expensive half. Batched by family, one
merged branch per batch, ear-tested before the next batch starts:

1. Filters — Veil, Sweeping Filter, Sweep Dwell, Resonance Bank
2. Body — Breath Generator, Heartbeat, Womb
3. Sequencers — Melody v1/v2, Polyrhythm v1/v3, Shepard Scale, Shepard Tone, Rhythm Track
4. Spectral — Morpher, Passage
5. Texture — Bubbler, Dapple, Stereo Phaser, Tremolo

**Phase 3 — missing features** (Part 3), folded into each batch's version bump rather
than run as its own pass.

Re-run the project-count grep at the start of each batch. The counts in CLAUDE.md are
from 2026-08-22 and the note there is explicit that the assumption expires silently.

---

## Open questions

1. **Selector-backed targets.** Melody v2's 24 `Vn …` target options name sliders that
   do not exist, because v2 collapsed forty per-voice sliders behind a `Voice` selector.
   The *target names are good* — `V3 Gain` says exactly what it is. R3's second clause
   proposes allowing this with a doc requirement. Needs a decision on the exact string
   form before the linter can check it.

2. **Drift amount ranges — SETTLED 2026-08-28, and the obvious answer is the wrong one.**

   JSFX cannot change a slider's label, units or range at runtime (confirmed against the
   REAPER SDK docs, 2026-08-28), so one range must serve every target on a selector
   forever. Today that range is sized to the widest target, which makes the narrow ones
   unreachable: Heartbeat's `Drift up amount` has step 0.1 while its `Random HRV depth`
   target spans 0 to 0.08, so the smallest available nudge is larger than the whole
   parameter. That target cannot be drifted at all.

   **Rejected: normalising the amount to "% of the target's own range."** It solves the
   arithmetic on paper and creates it in practice — wanting the heart to wander by 4 BPM
   would mean working out that 4 of 180 is 2.2%. `docs/dyscalculia-accessibility-sweep.md`
   already settled this: the barrier is **conversion, not numbers**, and hiding values
   behind a normalised scale is the same rejected move as hiding them behind mood-labels.
   Rozaya, 2026-08-28: *"I don't want to lose range. I don't want to have to abstract away
   things because you've decided I can't count."* Native units stay. Both features keep
   real numbers in the target's own terms.

   **The actual fix is two changes, and neither takes anything away.**

   **(a) Size the amount slider to the largest sensible WANDER, not the largest target.**
   Womb's `Drift up amount` reaches 2000 because breath frequency reaches 2000 Hz — but
   drift is a wander around a baseline and nobody wanders a parameter across its entire
   existence. A realistic ceiling is a fraction of the range. Womb drops from 0–2000 to
   roughly 0–200, and the step gets ten times finer at the same navigability. This is the
   assumption that produced every oversized amount slider in the suite, and it was never
   examined.

   **(b) Where a target is written as a fraction, write it as a percent** (R9).
   `Random HRV depth` at `0..0.08` becomes `0..8`; `Breath HRV depth` at `0..0.25`
   becomes `0..25`. Same control, same precision, *larger* numbers — and a drift step of
   0.1 now lands eighty times inside the small one instead of overshooting it.

   Together these bring every target on a given selector into a comparable magnitude,
   which is what makes one shared amount slider workable at all. Note this changes target
   sliders' **ranges**, so it is Phase 2 work with a migration, not Phase 1.

3. **`Capture slot` display base.** Both spectral pages document 1–8; source is 0–7
   since the 2026-07-09 change, with no display remapping. The docs are stale rather
   than conventional. Worth deciding whether the suite's selectors are 0-based (matching
   Resonance Bank and the rest) or 1-based (matching how a person counts slots) before
   fixing the pages to agree with whichever wins.

4. **Format longevity — settled, recorded here so it is not relitigated.** JSFX is the
   right home for this suite on a decades horizon, and the reasoning is worth keeping:
   `.jsfx` files are *source that runs* — no build step, no toolchain, no ABI, no code
   signing, no certificate, no vendor. VST2 is the cautionary tale (SDK licence
   withdrawn 2018); VST3's GPL3-or-commercial licensing fights this suite's CC0; native
   binaries need re-making every few years as operating systems move underneath them.
   And the flat numbered slider list — the thing causing every ordering problem in this
   document — is *also* precisely what makes these plugins reachable through OSARA. A
   custom plugin GUI would trade a naming problem for a blindness problem.

   Where the suite genuinely is at the edge is **tooling, not sound**: there is no
   compiler that can be run outside REAPER, so every mistake is found by ear, later.
   Part 5 is the answer to that, and it is why the tooling comes first.

   Worth a look at some point: **YSFX**, a third-party host that loads `.jsfx` files as
   VST3/LV2 outside REAPER. Current maintenance state unverified. Its existence is
   itself the argument — someone was able to write a second host for this format because
   it is small, documented and plain text. Nobody can do that for a compiled binary.

---

## Addendum — 2026-08-30

### Where the work actually sits

- **This document is the plan and nothing has been built from it.** It is still
  untracked; commit it first so it stops being a file that only exists on one machine.
- **`feature/morpher-layers` is the live branch**, 77 commits ahead of master and
  unmerged. It contains the whole Host x sweep (`feature/host-tempo-sync` is an ancestor
  of it, so that branch is finished business).
- **Uncommitted in the tree:** a `Layer harmonics (0 = full)` slider (38) for the
  Morpher — a per-layer CPU dial answering the "~4 layers is the ceiling" note in
  CLAUDE.md. Appended at the end, defaults to no change in sound. Finish or park it
  before starting a sweep; do not carry it through one.
- **Ear-tested since the last note:** Womb's Host x heart controls work.
- Two stale side branches (`feature/gut-sounds`, `feature/vowel-morph`) are old
  exploration, unmerged and not blocking anything.

### R10. A picker never hides the value it writes

The suite's convenience pickers (`Host ratio`, `Breath rate`, the pan-speed pickers)
were designed to *write a value and get out of the way*. In practice they do the
opposite: **13 plugins hide the rate slider whenever the picker is on anything but
`Custom`** — `slider_show(slider1, rate_mode != 1 || sliderN == 0)`.

That turns a shortcut into a grid. The picker's table is a list of ratios against the
beat, so while it is visible the only reachable speeds are the ones on that list. A cycle
every **5** beats of a 4/4 track — an ordinary thing to want in phase music, and the
whole reason this suite prefers a multiplier to a note-division grid — cannot be set at
all without first finding the entry called `Custom`. The value that would express it is
sitting right there and is invisible.

**Rule: the value slider is always visible. The picker is a jump-to, never a gate.**

- The picker writes the value and is done. It never controls whether the value can be
  seen or reached.
- **When the value no longer matches what the picker names, the picker snaps back to
  `Custom`.** This is the other half, and without it the picker becomes a label that
  lies — the failure mode CLAUDE.md already records from the `infantile.RPP` hunt, where
  a hidden picker stamped `0.5` over a hand-set rate. A picker that cannot lie also
  cannot need mode-gating for safety.
- Reconcile by **comparing the value against the picker's own table**, not by tracking
  edits. It is stateless, so it needs no adopt flag and cannot fire early on a restore —
  a fresh instance's default value and default picker agree by construction, so nothing
  is written.

**Cost: free.** `slider_show` and label text only. No renumber, no range change, no
migration. This is Phase 1 work and it is the largest usability change in the phase.

Applies to: Tremolo, Sweeping Filter, Sweep Dwell, Heartbeat, Rhythm Track, Melody v1/v2,
Polyrhythm v1/v3, Shepard Scale, Shepard Tone, Stereo Phaser, Bubbler, Dapple, Womb
(both its heart picker and its breath picker).

### Womb's breath in Host x — the units are right, the labels are not

Verified in source (`breath_host_scale`, `breath_state_advance`): in **Host x** the breath
cycle is **`Beats per breath` beats long, full stop**. The four second-sliders
(`Inhale/Top/Exhale/Bottom Duration sec`) are divided out and used **only as
proportions** — a 4/0.3/4/0.3 setting means the same shape whether it reads as seconds or
not. So the plugin is doing the right thing and saying the wrong thing: it is showing four
numbers in seconds that are not seconds.

Under the suite's own rule (*no silent value or unit changes*) an annotation is not
enough when the **unit itself** stops applying. Two candidate fixes, to be decided:

1. **Rename to the thing they always are.** `Inhale (shape)`, `Top pause (shape)` … with
   the seconds parenthetical dropped. Cheap, but it costs the Own-BPM user a real unit.
2. **Add four `... share` sliders** that are the shape, and let the seconds sliders be
   seconds only in Own BPM — hiding the pair that does not apply, the way `Breaths per
   minute` already hides in Host x. Honest in both modes, four more sliders.

Note the same question exists in reverse for `Beats per breath`, which is visible only in
Host x and is the *correct* control there — R10 makes it always-visible within Host x
rather than gated behind the picker.

### R11. One tempo-sync block, shaped like Drift and Ramp — replacing every Host ratio picker

Decided 2026-08-30 with Rozaya. This **supersedes R10's scope**: R10's "the picker must
not hide the value" is correct but it is a patch on a control that should not exist.

**What is wrong today.** Host sync is spread across three controls per rate — the rate
slider, `Rate mode`, and a `Host ratio` menu — and a plugin has one such set per rate,
plus bespoke extras where a rate did not reduce to one number (Womb grew `Breath rate`
and `Beats per breath` for exactly that reason). The suite navigates by REAPER's
**parameter list**, arrowing one control at a time, so every added control is real cost.
And the `Host ratio` menu is a **grid**: its entries are a fixed list of ratios against
the beat, so an ordinary want — one cycle every **5** beats of a 4/4 bar, which is the
kind of thing this suite exists for — is not on it.

**The replacement.** Set `Rate mode` to Host x, and directly beneath it, two controls
and no others:

```
Rate mode            (…, Host x)
  Host sync target   selector — the same list Drift and Ramp already use
  Every N beats      free value, continuous, no menu
```

Pick a target, set its beats, move on. Pick a second target to sync a second thing. Two
controls cover every rate the plugin has, however many that is.

**Why this is the right shape and not just a smaller one:**

- **It is a pattern already learned.** Drift and Ramp are nested selectors over a target
  list. This is the third instance of the same idiom, pointed at tempo instead of wander.
  Nothing new to learn, and the target lists are shared — which R2's linter can enforce
  across all three.
- **It deletes controls.** Every `Host ratio` menu in the suite goes, and Womb's two
  bespoke breath-rate controls go with them: the breath becomes an ordinary entry in the
  target list. Net fewer things in the parameter list, in every plugin.
- **It is not a grid.** `Every N beats` is a plain continuous number. 5 beats is exactly
  as reachable as 4.
- **It syncs more than one thing.** Today `Host ratio` speaks only to the primary rate;
  pan, secondary sweeps and Womb's breath each needed their own arrangement or went
  without. One selector covers all of them by construction.

**Decided details:**

- **The target's own rate slider stays visible** (Rozaya, 2026-08-30). It is not hidden
  and not disabled — it stays in the list showing the value it is running at. Hiding a
  control because a mode changed is the move that produced every problem in this section.
- **`Every N beats` is per target**, stored in a bank exactly like Drift's per-target
  amounts — so a synced heart and a synced breath hold different beat counts at once,
  and switching the selector edits one without stopping the other. Same mechanics as
  Drift, including `@serialize` and the derive-in-`@block` rule.
- Womb's `Breaths per minute` (a one-way rescale that writes the four duration sliders)
  is the same family of control and is **safe to keep**: the class of failure it used to
  have — a control writing to another control being stamped over during project load —
  was diagnosed and fixed suite-wide on 2026-08-23.

**Cost.** Real per-plugin code, not labels: a selector, a per-target bank, `@serialize`,
and the beats value folded in where each rate is consumed. But every rate in a plugin is
served by one block, and the block is a copy of one that already exists and is trusted.
Sliders are **appended**, and the controls it replaces are removed only once the
replacement is in — so it does not force the Phase 2 renumber to happen first.

**Build order:** Womb first — it has the most rates, it is the one that exposed the
problem, and it has just been ear-tested, so a regression there is legible. Then the rest
by family, following the Phase 2 batches.

### Womb's breath sliders stay in SECONDS -- decided 2026-08-30

The addendum above offered two ways to stop the four breath duration sliders
reading as seconds when Host x makes them proportional. A third was proposed in
conversation and is the one worth recording, because it is attractive and wrong:
make them **shares** (or percentages), identical in both modes, with the cycle
length coming from `Breaths per minute` in Own BPM and `Every N beats` in Host x.
It unifies the two modes, untangles speed from shape, and needs no annotation.

**Rejected, by Rozaya, on entry cost.** A 4-0.5-8-1 breath is four numbers you can
feel and type. The same breath in shares is 29.6 / 3.7 / 59.3 / 7.4, reachable
only by dividing each one by 13.5 -- the conversion barrier
`docs/dyscalculia-accessibility-sweep.md` exists to refuse. Shares would have
scaled with the project tempo perfectly well; they simply could not be entered.

**What shipped instead is only a rename**, because the behaviour was already
right: `Inhale (sec, ratio in Host x)` and its three siblings. Seconds when
free-running, ratio when synced, and a tempo change stretches the whole shape in
proportion. Two things fell out for free -- the four target strings in the Drift
and Ramp lists now match their slider labels minus the parenthetical, satisfying
R2 for those four, and R6's mixed phrasing is gone from this plugin.

**The general lesson for the rest of the sweep:** a unit that changes meaning
between modes is a naming problem first. Reach for a redesign only after checking
that the redesign can still be *entered* in the numbers the user actually thinks
in -- scaling behaviour is easy to verify and entry cost is easy to forget.

### R12. Ranges are 0–1000, or −1000–1000 where the sign means something

Decided 2026-08-31 with Star. Unconventional and deliberate: **stop hand-picking a
range per control.** Today's ranges are authorial accident in exactly the way R8's step
sizes are — `0..30`, `1..3`, `0..5`, `50..400` — each one somebody's guess at what would
ever be wanted, and each one a ceiling nobody agreed to.

**The rule:** a numeric slider spans **0 to 1000**, or **−1000 to 1000** where a negative
value does something real. Pick the step from the finest adjustment ever wanted (R8), and
let the position count be whatever it is.

**Why the position count stopped mattering** — this is what makes the rule possible, and
it is a correction, not a preference. Typing works: the FX dialog has a box beside the
slider, and in the parameter list you focus a parameter, press Tab, and there is an
editable field. So you type the value and nudge by ear from there. An earlier draft of R8
argued the opposite from an arrow-only premise that was simply wrong.

**Three carve-outs, and the first one has teeth:**

1. **"1000 or wider" — never a ceiling.** Narrowing a range **permanently clamps saved
   values**. Several controls are already past 1000 and must stay: breath frequencies
   (`50..2000`), the post-filter (`50..4000`), `Drift up/down` (`0..2000`), `Speed ramp by`
   (`-2000..2000`). The rule raises floors and ceilings; it never lowers them.
2. **Enums are exempt.** Rate Mode, Fade Mode, drift shapes, target selectors.
3. **dB is exempt: its range comes from audibility.** A level slider wants roughly
   `-60..+12`, not a house number — `-60` is already inaudible and `+1000 dB` is not a
   quantity. Where a control is in dB, the range is set by what can be heard, and the
   suite's existing convention holds: **`-60 = off`** (`Layer level (dB, -60 = off)`,
   `V1 Gain dB` at `-60..6`). This matters because R12 and the level conversion in the
   note below would otherwise collide the moment Womb's volumes convert.
4. **The `0..1` controls need a UNIT change, not just a range change.** Volumes, fades and
   the bloodflow proportions all live in `0..1`. Making them `0..1000` means deciding what
   1000 *is*. The honest answer is percent with 100 = unity, which also buys up to 10×
   boost where today nothing can exceed 1.0 — and it satisfies R9 (whole numbers over
   decimals). But it changes what every one of those sliders MEANS, so it is called out
   here rather than sliding in under a range sweep.

**Negatives are added only where they do something.** Not as symmetry.

| Control | Verdict |
|---|---|
| `Heart with breath (BPM peak-to-peak)`, Womb | **Yes** — negative is *inverted RSA*, the heart slowing on the inhale. Normal RSA is a coherence signature and its inversion is a dysregulation one, which is the exact axis the nervous-system-states work runs on. Today you can depict "no RSA" and not "backwards RSA". |
| `HB Stereo Width ms`, Womb | Already signed, and correctly — the sign picks which side the heart sits on. |
| `Sigh depth multiplier`, Womb | Not a negative: it wants a **floor below 1**. `1..3` cannot express a breath *shorter* than normal — a catch, a gasp, a held-in flinch. |
| Any volume / level | **No.** Negative means polarity inversion, which reads as nothing alone and cancels when layers sum — against the suite's mono-compatibility rule. A trap, not a feature. |

**Automation risk: measured, and it is zero.** Changing a range rescales any existing
envelope, because REAPER stores envelope points normalised. Grepped the whole library on
2026-08-31: **`PARMENV` appears in no `.RPP` at all**, so no parameter on any plugin
carries an envelope. Re-run before the sweep, but the finding also stands as evidence that
Drift and Speed Ramp replaced envelopes outright rather than supplementing them.

**Sequencing.** A range change is the one thing R8's cost ladder puts in the *risky* row,
so this is **Phase 2 work, folded into each plugin's reorder** — one migration per plugin,
never two. Womb's own list (RSA to signed, sigh depth floor, systole already done at
`0.01..1000`, the `0..1` group pending the percent decision) rides its reorder.

### The `0..1` group — three families, not one

Written up 2026-08-31 after Star asked what the deal with them was. Sixteen sliders in
Womb alone once the on/off enums are stripped, and they look uniform while being three
different kinds of quantity.

**Family 1 — LEVELS.** Womb: HB Master / S1 / S2 / Breath / Bloodflow Volume. These are
**linear gain**, which is perceptually skewed: the top *half* of the control buys 6 dB,
while everything from quiet to silent is crammed into the bottom tenth (0.1 is −20 dB,
0.01 is −40). They also cannot exceed unity, so making one layer louder means turning
every other layer down.

**The suite already decided this** — Morpher's `Input level (dry, dB)` and `Output level
(dB)`, Polyrhythm's `V1 Gain dB` at `-60..6`, the Morpher layers' `-60 = off`. Womb's
volumes are linear only because Womb predates the decision. → **dB, `-60 = off`.**

**Family 2 — REAL PROPORTIONS.** The four breath fades, plus Bloodflow Attack and Decay
(two of which already say *"proportion of cycle"* in their names). → **percent.** `30`
rather than `0.3`; same control, same precision, no decimals. Pure R9.

**Family 3 — ABSTRACT AMOUNTS.** Brightness, both Stereo Widths, Dicrotic Level,
Resonance. Not a fraction of anything nameable; `0..1` is where somebody landed.
→ **percent**, for the same reason.

**The incoherent caps are the evidence.** Three neighbouring bloodflow sliders:
Resonance `0..0.95`, Attack `0.005..0.5` step `0.005`, Decay `0.05..0.95` step `0.01`.
Three ceilings, two steps, no principle. That is what R8 and R12 exist to end.

**Migration.** Percent is `x100` — exact, sound identical, nothing to decide. dB is
`20*log10(v)`, also exact, with one wrinkle: 0 has no dB value, so it maps to the floor
and the floor becomes "off" — which is what `-60 = off` already means everywhere else.

Both are **Phase 2**, folded into each plugin's reorder, because they move ranges.

### R13. No multipliers. Anywhere. (Host x is not a unit.)

Decided 2026-08-31 with Star: *"That multiplier is gonna be the death of us."* It is
already the direct cause of most of what went wrong in the Womb work, and it is still
live in eight plugins.

**The suite already made this decision once.** The Speed Ramp sweep (2026-05-30) removed
every multiplier in favour of a **signed delta in the target's natural unit**, on Rozaya's
objection that *"the multiplier is a dyscalculia accessibility problem."* Host sync was
built afterwards and reintroduced exactly what that sweep removed.

**What the tempo multiplier costs, itemised — every one of these was paid for in 2026-08:**

- **The number means nothing alone.** `0.25` is not a rate. Knowing what it sounds like
  requires holding the project tempo and multiplying — the one operation this suite
  exists to never require.
- **It reads backwards from everything else.** `x0.5` is slower; *"every 2 beats"* is also
  slower. Two mental models for one idea, with a picker in between translating.
- **It forces hiding, and hiding forces stamping.** `70` as a multiplier is seventy times
  the tempo, so the rate slider had to disappear on entering Host x, which forced a
  landing value, which forced a write on mode entry — and that write is the
  `infantile.RPP` bug that cost a session.
- **One slider means two incompatible things**, against the standing no-silent-unit-change
  rule.

**The replacement — and the key move is that sync stops being a unit.**

Today `Rate Mode` is `{BPM, Seconds, Hz, Host x}`, so "synced" competes for the same slot
as "what unit". Womb escaped this only because BPM was its sole unit. Instead:

```
Rate mode        {BPM, Seconds, Hz}   -- what UNIT the rate slider is in
Sync to host     {Off, On}            -- whether the tempo drives it
Host sync target selector             -- which rate (R11)
Every N beats    free value           -- one cycle of it takes this many beats
```

With sync on, the rate slider keeps reading in the unit you chose, as a live honest
number that follows the tempo — and stays settable, converting back into beats. Nothing
hides, nothing is stamped, nothing multiplies. This is what Womb runs now, generalised.

**Migration:** old `Rate Mode == 3 (Host x)` becomes `Sync to host = On` with the unit
taken from what the value last meant, and the multiplier converted to beats
(`beats = 1 / multiplier`). Exact, and the plugin can do it itself from the blob magic.

**Affected:** Tremolo, Sweeping Filter, Sweep Dwell, Shepard Tone, Shepard Scale, Melody
Phase v1/v2, Polyrhythm Phase v1/v3, Heartbeat, Rhythm Track, Bubbler, Dapple, Stereo
Phaser. Womb is done.

### R13a. The sigh multiplier is the same bug, wearing a different hat

`Sigh depth multiplier` (Womb slider 61, `1.0..3.0`, step `0.05`) survived the 2026-05-30
sweep because it was not a rate. It has three faults, and Star flagged it as its own
problem on 2026-08-31:

- **It is a multiplier.** `1.5` requires multiplying by the breath length to know what you
  get, and the breath length is itself a sum of four sliders.
- **Its range cannot express a short sigh.** Floored at `1.0`, so a breath *shorter* than
  normal — a catch, a gasp, a held-in flinch — is unreachable. (Also noted under R12.)
- **The name is wrong.** It does not touch depth. It scales DURATION, uniformly across all
  four segments. A physiological sigh is deeper *and* longer; this one is only longer, and
  the slider says the opposite of what it does.

**Replacement, following the Speed Ramp precedent exactly:** a **signed delta in the
breath's own unit** — `Sigh by (sec / beats in Host x)`, `0` = no change, negative =
shorter. Same word, same shape and same semantics as `Speed ramp by`, so it is one idiom
rather than a second thing to learn. Internally it still distributes proportionally across
the four segments, preserving the I:E ratio as today; only the control changes.

**Left open, deliberately:** there is no amplitude component at all, despite the current
name promising one. A real sigh is a bigger breath, not merely a slower one. A separate
`Sigh louder by (dB)` would make the feature honest — worth doing, not part of this.

### R14. Speed Ramp states a DESTINATION, not a delta

Decided 2026-08-31 with Star. `Speed ramp by -35` requires knowing where the parameter
is and adding. `Speed ramp to 35 BPM` is the end goal stated outright, with no arithmetic
in it at all. For a control whose whole purpose is *"wind down over the next hour while I
fall asleep"*, the destination **is** the thing already in mind; the delta is a conversion
forced on the user to express it. Star, on why this matters more than it looks: *"it's
more fucking adding than we can deal with sometimes because our cognitive lag is so bad."*

**This reverses a 2026-06-09 decision, and the reason it was reversed the first time is
the reason it can be reversed back.** Womb v3 originally had destination semantics and
Rozaya rejected them — because the amount defaulted to 0, so engaging the ramp meant
"take the heart to 0 BPM" and the sound died. That was a **default problem misdiagnosed as
a semantics problem**, and we threw out the semantics to fix the default.

**The fix for the actual problem:** on first selecting a target, its destination **seeds
to where that parameter already is**. "Ramp to where I am" is no change, safely, and any
move from there states a goal. Identical continuity trick to the one that makes entering
Host x silent, which the suite has now implemented twice and trusts.

Consequences:
- The slider becomes `Speed ramp to`, in the **target's own unit** — which R12's
  `-1000..1000` already accommodates for every target in the suite.
- Seeding is per target and belongs in `@block` (it reads a bank), per the standing rule.
- `Speed ramp engage` still gates whether the ramp advances; nothing about the
  freeze/resume behaviour changes.

**Naming note that generalises:** `by` only reads as a sentence *because a selector sits
next to it finishing it* — "speed ramp by −35, target Heart rate." Anywhere there is no
selector to complete the phrase, `by` dangles. This is why `Sigh by` was proposed and
immediately failed the read-aloud test (*"sigh by... what. what?"*). **Test a slider name
by saying it aloud with its value and nothing else.**

### R15. The sigh gets its own four segments, and the multiplier goes

Star, 2026-08-31: *"we're trying to apply a very coarse control to a very dynamic thing.
Because we have the four sections of the normal breath, we don't have the four sections of
the sigh. And if you look at actual sighing, there is four sections. It's very distinct.
It's not just a computery shift in the normal breath."*

That is the correct diagnosis and it supersedes R13a's replacement. Scaling all four
segments by one number preserves the proportions exactly and only stretches time — so what
comes out is the same breath, slower. A sigh differs in **shape**, not size: a bigger
inhale against a longer, more passive exhale and a longer settle after it. Different
ratios, not a different tempo. No single multiplier or delta can express that, which is
why every naming attempt for one felt wrong.

**Replacement:** `Sigh depth multiplier` is deleted, and the sigh gets **Sigh inhale / Sigh
top pause / Sigh exhale / Sigh bottom pause**, in the same units as the normal four
(`sec / beats in Host x`), sitting immediately after `Sigh interval` in the breath group.
Four plain numbers in a unit already learned. Net +3 sliders in that group.

**Migration is exact and free.** Today's sigh is `normal x multiplier`, so seed the four
sigh segments at the saved multiplier times the normal four. Every existing project sounds
identical on load, and from then on the exhale can be pulled long without touching the
inhale.

**Still open, and it may SIMPLIFY this rather than extend it:** the classic augmented
sigh is *biphasic* — an inhale, a brief catch, then a second inhale stacked on the first,
before the long release. Four sections cannot express the stacked second inhale. But a
catch is arguably an **inhale** feature rather than a sigh one, in which case a sigh is
just its own four segments plus one deep inhale catch, and no fifth phase is needed. The
same mechanism also produces the shuddering post-crying breath, which is the distress cue
Womb currently has no way to make. Written up in `docs/planned-features.md` under
**Breath catches**. Build the four segments, hear them, then try a catch — in that
order. Also still true from R13a: there is **no amplitude component** — a
real sigh is a bigger breath, not only a longer one, and `Sigh louder by (dB)` would make
the feature honest.

### R16. It is `Ramp`, not `Speed ramp`

Star, 2026-08-31: *"It's not really speed anymore, is it."* Correct, and it has not been
for a long time. The feature was born scaling a rate; it now rides **every** target on the
drift list. Womb's ten include S1-S2 gap, RSA depth, the two breath filter frequencies and
four segment durations. Sweep Dwell's include Resonance. Polyrhythm's include per-voice
**Gain dB**. Calling all of that "speed" is a fossil of what it did in May.

**And the decision is already made — it just never propagated.** `spectral_vowel_morpher`
ships `Ramp target` / `Ramp by` / `Ramp duration` / `Ramp engage` / `Ramp start delay`
today, renamed on exactly this reasoning ("honestly named for a value"). Every other
plugin still says `Speed ramp`. This is the same failure mode as the multiplier: a good
call made in one place, not carried across.

**The block becomes**, combining with R14:

```
Ramp target      selector
Ramp to          destination, in the target's own unit, seeded from where it is
Ramp duration    minutes
Ramp engage      Off / On
Ramp start delay minutes
```

Renaming a slider is **free** (R-cost ladder, top row: REAPER restores by ID, never by
name), so this is Phase 1 work and can ship ahead of any renumber. `Ramp to` needs R14's
seeding and is Phase 2.

### Breath features propagate to every plugin with a breath

Star, 2026-08-31: *"any other plugin that uses breath should also get these."*

Only **two** plugins have one — `womb_sound_generator_v3` and `breath_gen` — so the blast
radius is small and there is no reason for them to diverge.

| | Womb | Breath Generator |
|---|---|---|
| Four breath segments | yes | yes |
| Fades + fade mode | yes | yes |
| **Sigh** (interval + four sigh segments, R15) | has interval + the old multiplier | **has none at all** |
| **Catches** (inhale + exhale, planned-features) | to add | to add |

**The Breath Generator cannot sigh.** The dedicated breathing plugin has no sigh mechanism
of any kind, while the womb — where breathing is one layer of three — does. That is
backwards, and it is the kind of gap this sweep exists to find. It gains `Sigh interval`
plus the four sigh segments, matching Womb exactly.

**Both gain catches** on the inhale and the exhale once that design settles.

**And both gain the new drift / ramp targets that follow from it** — the four sigh
segments and the catch controls. Per the standing rule these **append** to the target
enums and never insert, because per-target banks are indexed by target number. Breath
Generator's list is only five entries today (`Inhale, Top pause, Exhale, Bottom pause,
Breaths/min`), so it has the most to gain.

**Catches as a ramp target is the strong one**, and worth stating plainly because it is
the whole reason this matters: ramping inhale catches from four down to zero over twenty
minutes **is** the dysregulated-to-coherent journey, expressed as one control instead of
an envelope nobody can draw.

---

## Where to pick this up (as of 2026-08-31)

**Shipped and ear-tested in Womb**, on `feature/morpher-layers`: the host-sync block
(target selector + free `Every N beats`), heart rate as plain BPM in both modes, the
breath's four sliders as beats in Host x, systole in beats, and four bug fixes found by
ear along the way. Deployed to the Effects folder and verified byte-identical to source.

**Designed, not built:** R11–R16, the `0..1` writeup, and breath catches in
`docs/planned-features.md`.

### What is still unplanned, in the order things block each other

**Blocking:**

1. **Part 2's canonical layout is stale.** It still describes the A/B/C/D block structure;
   2026-08-31 replaced that with *everything belonging to a layer lives with that layer*
   (Star: the blocks "were arbitrary as shit"). Every per-plugin layout is measured
   against Part 2, so it is rewritten first. Drift and Ramp stay shared — their selectors
   span targets across layers, so splitting them costs fifteen sliders where five do.
2. ~~**The version forks.**~~ **CLOSED 2026-08-31.** Melody: archive v2, its note picker
   moves to v1 (`docs/layouts/melody-phase.md`). Polyrhythm: migrate v1's projects up to
   v3, archive v1 — evidenced in `docs/layouts/polyrhythm-phase.md`, and cheaper than
   assumed on all three counts (the project count is a backlog not a preference, v3 is a
   strict superset of what the projects use, and the `@serialize` blobs are identical so
   drift and ramp configs cross untouched). **Both forks end.**
3. **Scope.** Harmonic Sculptor is under an overhaul-or-drop question and Rozaya would not
   reach for it — still open. **Sustain Looper is IN**, corrected 2026-08-31: excluding it
   was Claude's judgement call, not Rozaya's, on the reasoning that it is a "sound-design
   tool". It is not — it runs in a project and plays for the length of a piece, which is
   exactly the profile drift and ramp exist for. Targets below.
4. ~~**Validation — the real hole.**~~ **MOSTLY CLOSED 2026-08-31**, and the hole was
   partly invented. Rozaya: *"I can reload a project if I need to. It's how these things
   get checked easier anyway. I just couldn't be fucked to do it last night because
   brain."* So reload and track-duplicate ARE testable — **ask for one** when a fix
   depends on it rather than assuming the path is dark. What remains true: JSFX cannot be
   compiled outside REAPER, and a clean script run proves nothing.

   **The agreed approach:** ear-testing happens **over weeks of ordinary use**, with the
   option of one set-aside day at the end for a deliberate pass. So the sweep does not
   block on a testing phase; it ships in batches and gets confirmed as the plugins get
   used. What I owe in return is that everything checkable *without* ears is checked
   before it ships — arithmetic by simulation (as the breath and systole numbers were),
   migrations by diffing actual output, and the standing lint checks.

**Needed, not blocking:**

5. **Drift period units under host sync.** Periods count heartbeats or breath cycles —
   should they be beats when synced? Same question already answered twice elsewhere.
6. **R12 vs Open Question 2.** OQ2 said size drift amounts to the largest sensible
   *wander*; R12 says everything is 0–1000. R12 probably wins now that fine steps make
   small values reachable, but two rules currently point different ways.
7. **The `0..1` inventory.** 176 sliders suite-wide top out at 1.0 or less. Minus enums,
   they split into dB and percent, and nobody has listed which is which.
8. **Open Questions 1 and 3** — selector-backed target names, and 0- vs 1-based selectors.
9. **Per-plugin layouts** — 22 hand-authored orders. The bulk of the work, done per batch.

10. **Nothing is merged or released.** `feature/morpher-layers` is **98 commits ahead of
    master**, master is 4 ahead of `origin/master`, and the last tag is **v2.20
    (2026-07-29) — 102 commits ago.** Every plugin Rozaya is currently using was
    hand-copied into the Effects folder from an unmerged branch, so there is no clean
    release to fall back to if something turns out wrong. This is not a consistency
    problem and it is not in the plan, which is exactly why it kept not getting noticed.
    Merging and tagging is cheap and it is the only thing on this list that reduces risk
    rather than adding scope.

**Suggested next:** 10 first because it is cheap and protective, then 1 and 4, which
shape everything else.

### Sustain Looper — drift and ramp targets

Added 2026-08-31 after Rozaya corrected the exclusion. Eight sliders; six are worth
modulating, and one of them is the most valuable target in the plugin.

| Target | Why |
|---|---|
| **Loop position (%)** | **The standout.** Drifting it wanders the loop slowly through the sample, so the timbre evolves instead of repeating. This is the direct answer to the note in CLAUDE.md that *"aliveness comes mostly from the SOURCE, not the plugin"* — it lets the plugin contribute aliveness by travelling through the source rather than sitting on one spot of it. |
| **Pitch (semitones)** | Slow drift is tape-wobble / organic detune; as a ramp it is a long descent over a night. |
| **Loop length (ms)** | Changes both the character and how often the repeat comes round. |
| **Spread (detune amount)** | The ensemble opening and closing over time. |
| **Output (dB)** | Ramp target: the hour-long fade for sleep use. |
| Crossfade (% of loop) | Marginal but harmless. |
| Voices (ensemble) | **No** — integer voice count; changing it mid-play adds and removes oscillators, which clicks. |
| Sample | No — file selector. |

**It should also gain the transport block** (Start delay, Play for, Rest for): a looper
that plays for eight cycles and rests for four is an obvious and currently impossible
thing to ask for.
