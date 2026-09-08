# Plan history — why the rules are what they are

**Budget: 700 lines.** Run `python tools/doc_budget.py` before committing.

Read this when you want to argue with a rule in
`docs/suite-consistency-plan.md`, or when you are about to propose something and
want to know whether it has already been tried and killed. **Do not read it for
current facts** — every status note in here is dated and most of them are stale.
`docs/current-state.md` is the file that describes now.

Moved out of the plan 2026-09-08, verbatim.

**The warning the old plan carried about itself, kept because it is the same
failure this split is fixing:**

> Started 2026-08-28. **Much of this HAS been built.** The line that used to sit here
> said nothing had been, which was true for three days and has been wrong ever since —
> and it cost real time, because every session opened this file, believed it, and
> re-derived the state from the source. Status is now recorded here. **Keep it recorded.**

That is now structural rather than a reminder: status lives in
`docs/current-state.md` and nowhere else, and this file is explicitly not
read for current facts.


---

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


---

## Dated status, all of it stale

## STATUS — verified against the source 2026-09-04 — STALE, DO NOT USE

`docs/current-state.md` is the file that describes now.

### Shipped

| what | where it stands |
|---|---|
| **R16** `Speed ramp` → `Ramp` | done, 70 labels across 14 plugins |
| **R8** step sizes standardised down | done for dB (0.01) and `Start delay` (0.001) |
| ~~**R11** one sync block~~ | **SUPERSEDED BY R20, 2026-09-04. Do not build this shape.** Its `Sync to host` / `Host sync target` / `Every N beats` block is what Womb and Melody carry, and both now convert away from it. Measured: across 73 Melody instances, the target selector has NEVER been pointed at anything but `Rate value` — the multi-target capability it exists for has never been used |
| **R13-revised** Host x means beats, not a multiplier | **COMPLETE 2026-09-04, EAR-TESTED ✓, and now folded into R20.** All thirteen plugins converted; every Host ratio picker retired; every landing block deleted; the rate slider never hides. Ten stored instances migrated by reciprocal. **R20 keeps all of this and adds the two things it left undone: a canonical enum ORDER, and a rate mode of its own for every rate** |
| **Polyrhythm per-voice gain default** −60 → −6 | done |
| **Morpher — the entire authored layout** | **LANDED** (`340fd4e`). `Capture average` 28 → 4, `High cut` beside `Low cut`, Drift and Ramp moved to the end, Input/Output relocated, `Layer overtone harmonic` added. `docs/layouts/spectral-vowel-morpher.md` describes a finished job, not a pending one — and it is itself stale: it says 39 sliders, the file has 44 |
| **Stereo Phaser — rate triple made contiguous** | **LANDED** 2026-09-04, plugin installed and `strangeness.RPP` migrated. First reorder to use a project-file migration rather than runtime repair |
| **Drift and Ramp play/rest** | **Veil, Tremolo, Morpher** |
| **Ramp counted in beats** (`Ramp time unit`) | **Veil, Tremolo** only |

### Still true, re-measured 2026-09-04 — this is the remaining work

- **The rate triple — mostly fixed 2026-09-04.** Every Host ratio picker is now
  retired and hidden, so the third member of each triple no longer occupies
  reading order at all. Rate Mode was then brought home to slider 2 in **Rhythm
  Track** (from 27) and **Shepard Scale** (from 62), both free because neither has
  any projects. **Two remain stranded: Heartbeat (rate 1, mode 34) and Womb
  (rate 1, mode 62)**, needing a migration for 1 and 8 projects respectively.
  Everything else was already adjacent. The original measurement follows.
- ~~The rate triple is still split in seven plugins.~~ Seven of the nine rows in the
  table below are unchanged: Tremolo 1/2/**34**, Sweeping Filter 3/4/**39**, Shepard
  Tone 3/2/**74**, Polyrhythm 3/2/**84**, Heartbeat 1/**34**/35, Shepard Scale
  1/**62**/63, Rhythm Track 1/**27**/28. The Melody Phase and Womb rows are superseded
  by R11 and should be read as done.
- **`Slope` is still 41 in Sweeping Filter, 42 in Sweep Dwell, 5 in Veil.** Veil's is
  the correct position; the filters move to match it, not the other way round.
- **Target lists still name sliders that do not exist.** Measured: Womb 4 of 10 wrong,
  Sweeping Filter 4 of 6 (`Sweep Rate` still does not exist), Breath Gen 3 of 5 —
  still offering `Breaths/min` for a control it does not have. Some are near-misses on
  a trailing parenthetical, which is exactly what R2 exists to make mechanical.
- **Womb's `RSA depth` / `Heart with breath (BPM peak-to-peak)` pair** is untouched.
  R1 says both become `Heart rate swing per breath (BPM)`.
- **Phase 2 has otherwise not started.** Remaining reorders, by measured use: Polyrhythm
  v1 (17 projects), Sweeping Filter (11), Passage (10), Womb (8), Tremolo (8), Melody (7).

### No longer true — do not act on these

- The Morpher audit items in *Why* below. All fixed.
- Both doc-staleness claims in *Why* below: Bubbler and Dapple document Host x, and
  neither Polyrhythm page claims 12 waveforms. Verified 2026-09-04.
- Womb's slider is `Heart rate (BPM)` now, not `BPM`.
- `Speed ramp start delay` is `Ramp start delay`. R16 shipped.

---


## Addendum — 2026-08-30 — STALE STATUS, LIVE REASONING

Its opening claim that nothing has been built from the plan stopped being true
weeks ago. The reasoning below it is still worth reading.

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

### Polyrhythm's per-voice gain default — free to fix, and its sibling already did

Rozaya, 2026-08-31: *"we need a better default for polyrhythm. Bumping gain down is easier
than raising it every time from 60."*

| | per-voice gain defaults |
|---|---|
| Melody Phase | all **−6 dB**; `Active` decides who plays |
| Shepard Tone | all **0 dB** |
| **Polyrhythm v1 and v3** | V1 = −6, **V2–V8 = −60** |

**Two faults.** Activating a voice hands you silence and a 54 dB climb, when the plugin
already has a dedicated on/off (`Active`) so gain never needed to double as one. And
**V2 ships Active = On with its gain at −60** — a voice paying CPU and counting in the
active-voice normalizer while being inaudible.

It is also the bug the Morpher already hit and fixed (2026-08-19, in CLAUDE.md):
`Layer level` defaulted to −60 and every fresh instance muted its own Original before the
first sample. Same shape, same cause — **−60 used as a default on a control that has a
separate on/off** — and Melody Phase already carries the corrected form.

**Fix:** V2–V8 default to **−6 dB**, matching Melody. `Active` stays the on/off.

**Cost: nothing.** A default only applies to instances that have never been saved, so no
existing project changes in any way. **Phase 1, no migration**, and it improves the
most-used plugin in the suite immediately.

**General rule this yields:** where a control has a dedicated on/off beside it, its value
must default to a *usable* setting, never to the off sentinel. The sentinel is for the
user to reach deliberately, not somewhere to be stranded on arrival.

---

### Decisions approved 2026-08-31

Rozaya approved all of the following leans in one pass. Recorded here so none of them has
to be re-decided.

| # | Decision | Status |
|---|---|---|
| 1 | Heartbeat's `Breath HRV Depth` and `Random HRV Depth` become **BPM peak-to-peak**, matching Womb's `Heart with breath` | approved — Phase 2 (changes range) |
| 2 | `Bloodflow Resonance` becomes **dB of peak**, as the filters already did | approved — Phase 2 |
| 3 | Both `Stereo Width` controls become **% of full width** | approved — Phase 2 |
| 4 | `Brightness` — unit unknown until the code is traced | **not yet a decision**; read first |
| 5 | `Bloodflow Dicrotic Level` — same | **not yet a decision**; read first |
| 6 | **Harmonic Sculptor drops out of the sweep.** Zero projects and Rozaya would not reach for it; its overhaul-or-drop question is settled separately | approved |
| 7 | **Veil is swept anyway.** Zero projects but cheap, and worth learning why it never got used | approved |
| 8 | **Drift periods stay in cycles**, not beats, under host sync — a cycle is the musically meaningful unit for a wander, and beats would make it drift against itself | approved |
| 9 | The sigh gains a **loudness** component eventually, not now — a real sigh is a bigger breath, not only a longer one | approved, deferred |
| 10 | **Capture slots display 1-based.** Disagrees with every other selector in the suite, which is why it was open; people count slots from one | approved — closes Open Question 3 |

Rozaya, on 4 and 5: *"the ones I need to make decisions about I'll do when I can actually
think."* Those two are mine to research before they become questions at all.

Note 8 closes a question that had been asked and answered twice already in other forms —
and note 10 deliberately accepts an inconsistency, because matching how a person counts
beats matching the rest of the suite.

### Items 4 and 5, traced — they are answerable now

Both were held back on 2026-08-31 as "not yet a decision" because I could not say what the
control scaled. Traced in source; both now have a real answer, and neither needs Rozaya to
work anything out.

**4. `Brightness` (Womb slider 8, `0..1`) is a lowpass cutoff in Hz.**

```
lp_cutoff_near = 200.0 + slider8 * 250.0;    ->  200..450 Hz
lp_cutoff_far  = 175.0 + slider8 * 220.0;    ->  175..395 Hz
```

It sets the heartbeat's near and far channel cutoffs together. So the honest unit is
**Hz** — and the useful discovery is that the two curves are **the same ratio the whole way
along**: `far/near` runs 0.8750 to 0.8778, constant to within 0.002. One Hz control can
drive both as `far = near * 0.877`, and the difference is inaudible.

→ **Proposal: `Heart lowpass (Hz)`, `175..1000`, replacing `Brightness`.** The user sets a
frequency, which is a real quantity they can reason about and drift in its own units,
instead of a 0-to-1 abstraction over two hidden numbers. Migration is exact:
`Hz = 200 + old * 250`.

**5. `Bloodflow Dicrotic Level` (Womb slider 32, `0..1`) is a proportion of the pulse.**

```
bf_env_dicrotic = bf_dicrotic_level * (0.5 + 0.5*cos(...));
bf_env_pulse    = bf_env_main + bf_env_dicrotic;
```

`bf_env_main` peaks at exactly 1.0, so the dicrotic level is literally the height of the
secondary bump **as a fraction of the main pulse's peak**. That is a genuine proportion of
a nameable thing, which R17 allows.

→ **Proposal: `Dicrotic notch (% of pulse height)`, `0..100`.** Migration is `x100`.

Note the asymmetry, which is R17 working as intended: one turned out to be a real
measurement wearing a normalised disguise, and the other turned out to be an honest
proportion that simply never said what it was a proportion of. The test told them apart.

### CORRECTION to Part 5 — most of the tooling already exists

Rozaya, 2026-08-31: *"didn't we have a script for exactly this?"* Yes, and more of it than
Part 5 assumed. It says to **build** `tools/migrate_layout.py`; that would have rebuilt
working code badly. Read `tools/README.md` before writing anything new.

**`tools/passage_migrate_sliders.py` is the layout migrator already.** It solves every
fiddly part: token-position indexing (never "values with `-` stripped"), CRLF preserved,
backups first, gating so it is safe to re-run over a folder, and a `HOPS` table walked
oldest-first so a project several layouts behind migrates through in a single pass. Its
docstring carries the reasoning too, including why the blob is untouched by a renumber.

**The one thing it cannot do:** its hops are **inserts** — `(count, keep, inserted)`,
meaning "keep N values, splice these in, shift the rest up." A reorder is an arbitrary
**permutation**. So the work is to generalise it to accept an authored old→new mapping
alongside the existing insert hops, not to write a new tool.

**Two others that matter more than I had credited:**

- **`tools/passage_captures.py`** — lists and extracts the captures stored inside a
  Morpher/Passage `@serialize` blob. This makes the riskiest migration in the suite
  *checkable*: inventory the captures in all 38 Morpher projects before touching them,
  and verify afterwards that every one came through. Checking rather than hoping.
- **`tools/morpher_to_passage.py`** — copies a project from one plugin to a different
  one. That is exactly the shape the Polyrhythm v1 → v3 migration needs, which was being
  treated as unbuilt.

**Revised Part 5:**

| need | status |
|---|---|
| `.RPP` slider-line rewriting, safely | **exists** — `passage_migrate_sliders.py` |
| arbitrary permutation (not just inserts) | **generalise the above** |
| cross-plugin project conversion | **exists in shape** — `morpher_to_passage.py` |
| blob inspection / verification | **exists** — `passage_captures.py` |
| enum-index migration | **exists** — `morpher_migrate_layer_order.py` |
| per-plugin authored layouts | `docs/layouts/*.md`, hand-written |
| linter | exists; corrected 2026-08-31; a lead generator, not a safety net |

**The general lesson, and it is the same one as the unpropagated decisions:** this repo
keeps containing the answer already. Check `tools/README.md` and `git log` before
estimating that something needs building.

---


---

## Superseded shapes — do not re-derive these

### ~~R11. One tempo-sync block, shaped like Drift and Ramp~~ — SUPERSEDED BY R20, 2026-09-04

**Do not build this. Everything below is kept for its reasoning about the Host
ratio pickers, which was right, and those pickers are all retired. Its
replacement — `Sync to host` + `Host sync target` + `Every N beats` — is dead:
see R20 for what replaced it and for the measurement that killed it.**


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

## Part 6 — Order of work — SUPERSEDED

**Do not follow this ordering.** It was replaced by the revised Part 6 of
2026-08-31, which now lives in `docs/backlog.md`. Both sat in the same document
unmarked for weeks, and a session reading top-down hit this one first.

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

## OPEN, AND DELIBERATELY NOT STARTED: pitch needs its own rule (raised 2026-09-05)

Rozaya: *"pitch needs its own whole thing, doesn't it."* It does. Measured the
same day, before anyone designed anything — **this suite states a pitch seven
different ways:**

| how | where |
|---|---|
| note name WITH octave (48-entry picker, C2..C6) | melody_phase, polyrhythm_phase_v3 |
| note name WITHOUT one (12-entry) + separate Centre Octave | polyrhythm_phase, shepard-tone |
| semitones, raw | spectral_vowel_morpher, spectral_vowel_passage, sustain_looper, polyrhythm_phase's per-voice pitch |
| hertz, directly | dapple, resonance_bank, rhythm-track, womb, heartbeat gen, breath_gen, both sweeping filters |
| cents | polyrhythm_phase_v3 fine tune, shepard-tone drift |
| percent | dapple's Pitch spread |
| semitones, for a spread | bubbler's Pitch spread |

**The three worst, and two are siblings disagreeing with each other:**

1. **Bubbler and Dapple state the same control two ways.** Bubbler: Transpose
   (semitones) + Pitch spread (semitones). Dapple: Pitch (Hz) + Pitch spread
   (**percent**). Same family, same job.
2. **Semitone ranges are unrelated to each other** — sustain_looper ±24,
   the Morpher ±96, and **polyrhythm_phase's per-voice Semitones ±1000**, which
   is eighty-three octaves.
3. **Tuning reference exists in five plugins and is absent from every other one
   that makes a pitch** — bubbler, dapple, the Morpher, Passage and
   sustain_looper all produce pitched sound with no way to say what A is.

### Why this is NOT the rate block, and must not be done the same way

**There is no free window.** The rate-mode sweep was cheap because nothing was
stored on those controls — 47 instances all sitting on a declared default. Every
pitch value in this table is stored in real projects **and is the sound**.
Changing a pitch unit changes what you hear, in work that is finished.

**So: write the rule, argue it out, and touch no code until the shape is
settled.** That is what finally worked for R20 after five sessions each reached
for a different answer, and pitch is a bigger surface than rates were.

**Deferred deliberately on 2026-09-05**, with the reasoning recorded rather than
the work half-started. Rozaya: *"It's a thing that needs exploration... I don't
think we should start that tonight."*

---

## Part 5 — Tooling, built first — SUPERSEDED

**Most of this tooling already exists.** See the CORRECTION above.

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


---

## Cost measurements, taken before each decision

## Cost, measured 2026-09-02 — and it is asymmetric

The stored value is the POSITION, so reordering moves every saved project's pan
mode to a different mode. Measured across the whole library:

| plugin | stored values | reorder cost |
|---|---|---|
| `melody_phase` | 64 at Pan Mode 2, 8 at 3, **1 at 4** | 0-3 must not move; 4+ costs one control in `simple-sequence` |
| `polyrhythm_phase` | 35 at 0, 16 at 1, 18 at 2, 15 at 3 | 0-3 must not move |
| `polyrhythm_phase_v3` | 6 at 0, 2 at 2 | 0-3 must not move |

So **the new modes (4 and up) are effectively free to reorder right now** — one
instance to re-set, and that window closes as soon as anyone saves a project
using them. The old 0-3 need a value remap per plugin, which is a small `.RPP`
script of the same shape as the existing migrations.

The effect plugins (`Full_Feature_Tremolo`, both filters, `rhythm-track`) have
not been measured yet — run the same count before touching them.

## What it costs, measured 2026-09-05 before deciding

**Nothing.** Renaming index 3 and appending index 4 move no stored value.

**What was rejected on cost:** sorting the list by DIRECTION, so everything where
bigger-means-faster sits together. That is arguably the more logical order, and it
would mean reordering the settled three — **256 stored rate-mode values across 12
plugins**, including the Morpher's 122 on Seconds alone. The grouping we get for
free (three ways to say your own speed, then two ways to say it against the
project) is logical at the level that matters. Rozaya: *"in logical positions
though"* — this is that, without re-opening R20.

## The enum-order migration, measured 2026-09-04

Reordering an enum changes what a stored index MEANS, so this needs a migration
even though it is "only naming". Every affected instance in the library:

| what | instances | change |
|---|---|---|
| Pan unit, Tremolo / Sweeping Filter / Sweep Dwell | **32** | all stored `Hz`; index 0 → 2 |
| Stereo Phaser rate mode | **3** | all on the DEFAULT, and its default is `Own Hz` — needs `2` written EXPLICITLY or they silently become BPM |
| Womb rate mode | **1** | `Host x` index 1 → 3. The other 7 are on BPM and do not move |
| Melody, Heartbeat, Rhythm Track, Shepard Scale | 0 | Melody's `{BPM, Seconds, Hz}` gains Host x on the END, so its indices are stable |

**36 instances, every one uniform.** Nothing anybody has saved changes how it
sounds.

## Cost, and why it is much smaller than R13's

Nothing moves position, so **most instances need no migration at all** -- a
relabel and a changed interpretation. Only instances actually **on Host x** need
their Rate Value converted, and the conversion is a reciprocal: a stored
multiplier of 0.5 (half tempo) becomes 2 beats per cycle.

**Counted 2026-09-02, across every project in the library:**

| plugin | instances | on Host x |
|---|---|---|
| `full-feature-sweeping-filter` | 20 | **6** — `as-things-are`, `bilateral-with-binaurals`, `noisescape-august-18-2026`, `womb-and-baby-heartbeats-with-bloodflow` |
| `Full_Feature_Tremolo` | 11 | **4** — `simple-sequence`, `simple-sequence-check` |
| `womb_sound_generator_v3` | 8 | **1** — `womb-and-baby-heartbeats-with-bloodflow` |
| `polyrhythm_phase` | 84 | 0 |
| `dapple` / `bubbler` / `polyrhythm_phase_v3` / `stereo-phaser` / `resonance_bank` / `sweep-dwell-filter` | 37 | 0 |
| `heartbeat gen` / `rhythm-track` / `shepard-scale` / `shepard-tone` | none in any project | 0 |

**So it is three plugins and eleven instances, not twelve plugins.** Everything
else is a relabel with nothing stored to convert. Worth noting that
`polyrhythm_phase` is the suite's most-used plugin by a wide margin — 84
instances — and not one of them uses host sync.

Do the free ones first: they need no migration, no snapshot, and no ear test
beyond confirming the label reads right.

## The four shapes this is cleaning up (audited 2026-09-02)

- `melody_phase` -- sync switch + target + Every N beats. Keeps it.
- `womb_sound_generator_v3` -- **NOT half converted. This was wrong and acting
  on it would have broken the plugin.** Rozaya, 2026-09-04: *"host x is the
  rate mode. every N beats is getting the multiplier out of there. neither of
  them work alone."* Rate Mode `{Own BPM, Host x}` at 62, `Host sync target` at
  63 and `Every N beats` at 64 are ONE mechanism: the mode says follow the
  project, the beats value says how fast, and it is the thing that replaced the
  multiplier. Retiring the beats slider "the same way the picker does", as this
  document used to say, would delete the working half of a working pair.
  It reads as a leftover only if you assume R11's separate sync switch is the
  target -- and R13-REVISED ALREADY OVERTURNED THAT. Womb is the plugin that
  got there first; the plan never caught up. What it actually needs is its Rate
  Mode moved next to the rate it governs (62 against a rate at 1), which is a
  position change, not a redesign.
- `spectral_vowel_morpher` -- a sync switch and no Every N beats. Half converted
  the other way.
- Twelve others -- Host x in the enum plus a Host ratio multiplier picker:
  both Polyrhythms, both Shepards, Full Feature Tremolo, both sweeping filters,
  `sweep-dwell-filter`, `heartbeat gen`, `rhythm-track`, `dapple`, `bubbler`,
  `stereo-phaser`, `resonance_bank`.

