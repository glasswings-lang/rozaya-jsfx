# Rozaya JSFX plugin suite

A small collection of Reaper JSFX plugins for ambient, sleep, and entrainment audio. Public domain (CC0). Designed by Rozaya, developed iteratively with Claude.

## From Rozaya

*The rest of this file is the AI's words. This section is mine.*

I don't code. I don't code at all. That doesn't mean you have to simplify things
to the point of leaving out ideas. It does mean that I need things to be broken
down in non technical language so that I can then make a decision. Speaking in
English does not necessitate the removal of complexity, especially when you may
not know whether or not that complexity is load-bearing.

## Read this first. It outranks everything below it.

These come from what the person who owns this suite has asked for, and from
sessions where ignoring them did real harm. They are requirements, not
preferences. (Written generically on purpose: this repo is public, and a
person's access needs are theirs to disclose, not a maintenance note's. What a
future session needs is the requirement; whose it is, is not.)

- **Speak plainly, and start soft.** Short kind sentences, not briefing-voice.
  Dense or clipped delivery lands badly. Plain language is not the same as
  leaving ideas out — explain the complexity in English rather than dropping it,
  because you often cannot tell which part is load-bearing.
- **The owner is a non-coder and does not read this repo.** Not the source, not
  the docs, not this file. That is correct and expected. Everything in `docs/`
  and everything here is YOUR working memory, not theirs. **Never point at a
  file and expect it to be opened.** If something matters, say it in the
  conversation, at the moment it matters, in words.
- **There is no second reader.** Every established practice for working safely at
  this scale assumes a human reviews the diff. That step does not exist here, and
  no one else can audit or edit these plugins. Whatever substitutes for it — a
  plain-English account of what you did, a check you can describe, a thing that
  can be heard — is load-bearing in a way it would not be elsewhere.
- **A screen reader (NVDA) is the primary way of navigating**, and cognitive
  accessibility is non-negotiable. Both apply to every slider you name or move.
- **Numbers are fine; arithmetic is not.** Reading, setting and nudging a value by
  ear is fine. `0.0625 ÷ 2` breaks; `480 − 440 = 40` does not. The machine does
  the maths and the owner keeps precise control. Do not hide numbers behind mood
  labels — that is a different mistake and it has already been rejected.
- **Walls of text and to-do lists are a cost, not a service.** So is handing over
  a decision dressed as a menu. Bring a recommendation.

### Whose job is whose

**The ear is the owner's. The exactness is yours.** They decide what a thing
should sound like, what it is called, whether it is good, and whether it ships.
You do the DSP, the migrations, the slider arithmetic, and the concrete values.

**The owner is precise on purpose. Do not mistake that for a burden to relieve
them of.** They can be sharply analytical in short bursts, and they aim for
precision deliberately — because the one time a session read vagueness as an
invitation, it built and delivered a plugin with **no numeric entry at all**,
only mood labels. That was condescending, it was said so at length, and it is
where "never make the user produce a number" got corrected to *stop the
arithmetic*. The tidy version of that rule is easy to rationalise past, so keep
the story attached: **the failure mode is condescension, and on the way out the
door it looks like helpfulness.**

What is actually expensive, and none of it is precision:

- **Arithmetic and unit conversion.** Never ask for it. The machine does it.
- **Sustained analytical load.** Short bursts are fine; a long chain of steps
  held in the head is not. One decision at a time, and carry the context
  between them yourself.
- **Turning a sound into text at all.** There is no channel for making a noise
  at you — *"I wish they had the tech for me to make noises at you instead of
  just talk"* — so every description of a sound has already been paid for in
  translation before it reaches you. Treat it as expensive data, not as a rough
  first pass to be interrogated.

**And you cannot hear.** That is the fact under everything else on this page.
The owner is the only ear on the project: a description of how something sounds
is not an opinion about the work, it is the only measurement anyone can take.
That is the real reason reports here are believed, and why "it has been heard"
is the only status that counts as done.

So the useful move is never to ask for a figure so you can proceed. It is to
**offer a candidate value and a way to hear whether it is right**, so the loop is
listen-and-react rather than specify-from-scratch. Precision comes back to you
either way, and it costs them less.

The stated goal is soundscapes, and a suite good enough to put a name to in
public. Everything here serves that. When something in this file starts serving
the file instead, cut it.
## Where things stand

**Everything under this heading goes stale. Update it at the end of a session,
in the same commit as any entry you add to `docs/session-log.md`** — that log is
append-only history; this is the only part of the repo that claims to describe
*now*.

*Checked against the tree 2026-09-03.*

- **Branch `feature/melody-reorder`, 42 commits ahead of `master`, unpushed and
  unmerged.** `master` itself is in sync with `origin/master` — the session log
  still says the 2026-07 run is unpushed, and that is no longer true.
- **`v2.21` is the newest tag and sits 23 commits back on `master`**, so
  everything on `master` since it, plus all 42 branch commits, is unreleased.
  Per the session log, v2.21 is marked *pre-release* on GitHub and v2.20 is
  "Latest" — that is release metadata this file cannot verify, so check with
  `gh release list` rather than trusting the line. And **`git fetch --tags`
  before assuming the next version number**; stale local tags have already
  caused one misnumbered release.
- **EAR-TESTED 2026-09-04 ✓ — per-cycle pan on Polyrhythm Phase.** Independent
  tremolo mode, two voices at 60 and 24 BPM, Depth dB 0, Pan mode `Alternating`:
  each voice steps its pan on **its own** tremolo wrap, at its own rate.
  *"It works perfectly."* That clears the per-cycle shape functions, the
  per-voice cycle index (the regression Rozaya caught by ear on 09-02, where a
  single shared index panned everything at the base rate), and `Pan Glide`.
  **It does NOT clear the other ticks:** `percycle_pan()` is byte-identical
  across the oscillator plugins, but what ADVANCES it differs on purpose —
  Melody steps on the note trigger, the filters on their LFO wrap. Those are
  still unheard.
- **EAR-TESTED 2026-09-04 ✓ — the Melody layout migration, on the finished work.**
  All four finished projects (`melodic`, `outcoming`, `slow-summer`, `upswing`)
  played and correct. *"They came out perfectly."* **This was the highest-stakes
  unverified thing in the repo**: 73 instances across 7 projects, rewritten by a
  script whose earlier run had a wrong gate and had once eaten a line per
  instance. It had been verified by DECODING — 4632 comparisons against the
  snapshot at `_pre-melody-layout-20260902-1503` — and never played. Now both.
- **EAR-TESTED 2026-09-04 ✓ — Veil's rebuilt layout and the Ramp in beats.**
  *"Slider layout? Excellent. Ramp stuff? Works."* So the 22-slider reorder
  reads correctly, and `Ramp time unit` / the beat-counted staircase do what
  they say. **The steeper slopes are confirmed too** — *"rolloff works"* —
  which closes the last item outstanding from the August rolloff overhaul.
- **Where Drift play/rest earns its keep, and where it does not.** Rozaya, on
  hearing it in Veil: *"filters are hard to hear a semi-beat pause on."* A
  pause inside a slow cutoff wander is barely perceptible, because a filter
  has no articulation of its own to interrupt. **So when this propagates,
  aim it at parameters with an attack**: tremolo depth and rate, note timing,
  breath and heart segments. On the filters it is correct and nearly
  inaudible, which is not a reason to remove it but is a reason not to lead
  with it.
- **Still unheard:** the Host x beats-per-cycle conversion in four plugins, and
  the per-cycle pan tick in Melody (note trigger) and the filters (LFO wrap) —
  Polyrhythm's tremolo-wrap tick passed on 09-04 but the others advance on a
  different clock. Plus tests 3-5 of `docs/host-sync-ear-test.md`.
- **The suite consistency sweep is mid-flight.** `docs/suite-consistency-plan.md`
  is the authoritative document for it — read it before touching interface
  naming, ordering, ranges or units anywhere in the suite. Phase 0 and most of
  Phase 1 are done; **Phase 2 (reorders + migrations) has not started.**
- **No releases until the sweep finishes.** Pushing is fine; a release is a
  distribution artefact and shipping one mid-sweep hands a stranger a
  half-renamed suite.
- **`docs/open-bugs.md` has one open entry** (Melody Phase instances arriving out
  of alignment in `simple-sequence`). Read it before touching Melody.
- **`docs/host-sync-ear-test.md` is the highest-value thing waiting.** Five tests,
  about fifteen minutes, and **three of them have never been heard on any
  plugin.** It is written to be handed over: preconditions, failure shapes and
  what each one means, design questions marked as separate from correctness ones,
  and an explicit *don't diagnose, just say which number did what*.

### Terminology that changed, and where the old words survive

`docs/session-log.md` is **append-only history and is not rewritten**, so it uses
the names that were current when each entry was written. The plugin pages and
older docs can lag too. Two renames matter when reading any of them:

- **`Speed ramp` is now `Ramp`** everywhere the user can see (2026-08-31, 70
  labels across 14 plugins). The internal variables are still `speed_ramp_*` and
  that is fine. Every "Speed Ramp" in the history means today's `Ramp`.
- **`Host x` is a rate mode, and `Rate Value` there means BEATS PER CYCLE.** The
  history describes it as a *multiplier* of the project tempo, which is
  what it was from 2026-08-11 until R13-revised on 2026-09-02. **Sixteen plugins
  have a Host x mode. Four are converted** — both Polyrhythms, Dapple, Bubbler —
  **and twelve still read Rate Value as a multiplier there** (counted
  2026-09-03; the 2026-09-02 log entry says "nine", which was already wrong when
  written). Womb is in the twelve but is a special case: its Host x was rebuilt
  on the R11 shape (a sync-target selector plus a free `Every N beats`) rather
  than left as a bare multiplier, so the raw count overstates the remaining
  work by one. So both descriptions are true of different files right now —
  check the file before trusting either. Recount with:
  `cd src && for f in *.jsfx; do grep -q "Host x" "$f" && { grep -qiE "beats per (cycle|bubble|beat|breath)" "$f" && echo "CONVERTED $f" || echo "multiplier $f"; }; done`

## Layout

- `src/*.jsfx` — plugin source files (one per plugin), 21 of them. A plugin can ship parallel versions when they have genuinely different design tradeoffs, but a superseded version moves to `archive/versions/`. **Only one parallel pair is left: Polyrhythm Phase v1 (`polyrhythm_phase.jsfx`) and v3 (`polyrhythm_phase_v3.jsfx`)**, and that pair is a migration backlog rather than a decision — see the versioning section. Womb v1/v2 were archived 2026-06-15 (legacy, frozen, and still carrying the pre-Park-Miller right-channel PRNG artifact, left unfixed as frozen-as-shipped); **Melody Phase v2 was archived 2026-09-02** after zero projects ever reached it, its note-name picker having moved into v1.
- `docs/plugins/` — user-facing reference, **one page per plugin** (`docs/plugins/<plugin>.md`), indexed by `docs/plugins/README.md`. Split from the old single-file `docs/rozaya_jsfx_manual.md` on 2026-07-08 (verbatim carve; nothing lost) so a player who installs one `.jsfx` reads only that plugin's page. Each page is self-contained — it documents that plugin's own controls (including how shared features like Drift and Speed Ramp apply to it), so no companion file is needed; the earlier `shared-systems.md` was removed for reintroducing exactly the "docs for stuff you don't have" coupling the split fixes. `docs/rozaya_jsfx_manual.md` is now a stub redirect. **Update the relevant plugin page whenever you change a slider or add a feature** — modders and players read it instead of the source. **Lockstep still applies** (see the manual-audit discipline): update the touched plugin's page and re-verify counts/defaults, but the audit surface is now scoped to one file per plugin.
- `docs/suite-consistency-plan.md` — **the authoritative document for the interface sweep currently in flight.** Naming rules (R1–R19), the canonical layout, the migration strategy, and the phase ordering all live here. Read it before changing any slider's name, order, range or unit. It is long because it had to decide everything up front: a migration costs the same whether one thing changes or forty, so everything a plugin needs changes in one version bump.
- `docs/layouts/<plugin>.md` — the authored target layout for a plugin whose reorder hasn't landed yet. Four exist so far.
- `docs/open-bugs.md` — known-broken and not fixed. **Read it before touching the plugin it names.** It also records theories already burned, so they aren't tried again.
- `docs/session-log.md` — dated history, newest first, with a topic index. Read it for the *reasoning* behind a decision or a bug, never for current facts. **Anything in it that is still a live rule belongs in this file instead** — if you find one down there that isn't up here, lift it.
- `docs/versioning.md` — the full standard for forking, archiving and migrating a plugin. This file carries the short form.
- `docs/planned-features.md` — design-session capture of in-flight feature work and deferred items. Less authoritative than the plugin pages.
- `docs/womb-v2-design.md` — Womb v2 architectural rationale.
- `docs/dyscalculia-accessibility-sweep.md` and `docs/designing-for-dyscalculia.md` — Rozaya is dyscalculic as well as blind; both axes apply. **The core rule was sharpened and the old wording is wrong: the barrier is ARITHMETIC AND CONVERSION, not numbers.** Reading, setting and nudging a value by ear is fine. `0.0625 ÷ 2` breaks; `480 − 440 = 40` does not. So the machine does any maths, and the user keeps precise control — do NOT "fix" access by hiding numbers behind mood labels, which is a separate and already-rejected mistake.
- `tools/` — Python utilities, all run from outside REAPER. Two families worth knowing: **`jsfx_lint.py`** (paren balance per section, empty `()` branches, case-folded names, scientific notation, reserved-variable writes, slider declarations after an `@section` — REAPER tells you none of this until load, so run it), and the **`.RPP` migration scripts**, which all build on `rpp_sliders.py` for parsing a project's slider line. `tools/README.md` indexes them. See also the standing rule that a script may *apply* an authored list but must never *infer* one.
- `archive/exploration/` — work that never shipped. Experiments, abandoned approaches, discarded design directions (tract waveguide diagnostics, vowel shapers, the polyrhythm_tremolo decomposition experiment, the standalone drone synths). Preserved as reference, not maintained.
- `archive/versions/<plugin>/v<N>.jsfx` — prior shipped versions that have since been replaced. Distinct from `exploration/` (which holds never-shipped work). See `archive/versions/README.md` for the convention.
- `LICENSE` — CC0.
- `README.md` — top-level overview.

## Active plugin under heaviest development

**Polyrhythm Phase — and `src/polyrhythm_phase_v3.jsfx` is where a new feature
gets built and judged.** `src/polyrhythm_phase.jsfx` (v2 of the v1 line) gets
only what keeps it working until its projects cross over. Defaulting to v1
because it has more instances is backwards — that count is the migration
backlog, not a vote. (Confirmed by Rozaya 2026-09-02; see the versioning section.)

A drone synth, not a playable instrument. Up to 8 simultaneous voices,
polyrhythmic tremolo with attack/release envelope, optional binaural beat,
**16 pan modes** (Tremolo / Increment / Spread / Spread Reversed, plus the
per-cycle family added 2026-09-02), **14 waveforms**, Direction & Reverse
(5 modes), Start Delay, Play/Rest gating (per-voice cycle counts, depth-floor
cancel on final release for clean rest entry), nested-selector Drift and Ramp,
and a Host x rate mode where **Rate Value means beats per cycle**.

The two differ in how a voice is pitched: v1 takes semitones against a tuning
reference, v3 is note-based. Slider counts as of 2026-09-03: v1 declares 82
sliders with a highest ID of 86; v3 declares 90. Their `@serialize` blobs are
byte-identical, which is what makes the v1 → v3 migration tractable.

## Project values to preserve

- **Public domain (CC0)** — no proprietary code, no copying from licensed sources. Original implementations only.
- **Gentle by default** — these plugins target sleep / ambient / entrainment use. Avoid harsh transients, aggressive transients, or designs that produce mono-cancellation artifacts on speakers. Mono compatibility matters because users play these on HomePods, phone speakers, etc.
- **Hand-editable text and JSON** — every slider has a sensible default in the spec; every text pool is plain-text with one entry per line. Modders are first-class users.
- **No new dependencies** — pure JSFX (eel2 syntax). No external libraries, no Reaper extensions.

## How to work here

Practice rules, each one earned by something going wrong. They were scattered
through the session log as single sentences inside dated entries; they are here
because they apply every session, not on the day they were learned.

### Evidence

- **Verify the OUTPUT, never the run.** A clean script exit is the weakest
  available evidence. Report what you actually inspected, not that a thing ran.
- **A script may APPLY an authored list. It may never INFER one.** The safe edit
  form is an exact literal match plus a count assertion, so a wrong assumption
  refuses instead of spreading. Rozaya, after a near-miss: *"THIS IS WHY SCRIPTS
  WILL END A PROJECT"* — a scripted edit applies one wrong assumption to every
  file instantly, and every structural check still passes, because nothing is
  malformed. **Semantically gutted and syntactically perfect is the failure mode
  a linter cannot see.**
- **The check that catches that is simulating the function and reading the
  output numbers.** Seven pan modes all returning `[-1,1,-1,1]` is invisible in a
  paren-balance check and obvious in one line of output.
- **Range-check every migrated value against its slider's declared min/max.** A
  value that cannot fit its control (`Drift period = 0` where the minimum is 1)
  is the fastest possible proof that a mapping shifted, and it needs no ears.
- **Do not verify a migration against the same table the migration used** — it
  will agree with itself perfectly. Decode by control NAME against a
  pre-migration snapshot, and assert line counts and instance counts before
  writing anything.
- **"Read and compare, don't script"** — Rozaya. Reading ONE real line beside the
  control names has twice found in seconds what a day of reasoning did not.

### Diagnosis

- **A plausible mechanism is not a finding. Say which one you have.** Mark it
  **proved / predicted / untested** when you write it down — an unmarked
  mechanism gets read as proved by the next person, including by a later you.
  Two have hardened into false constraints here that way. The test: *if this
  theory were wrong, what would I hear?* No answer means it is a hypothesis.
- **"What else produces exactly this symptom?" is the cheaper question.** Both
  times a wrong theory survived here, a second candidate was the real cause.
- **Rozaya's reports have a track record, and it is better than mine. Start from
  the assumption that what is described is really happening, where it is said to
  be happening.** The measured history in `docs/session-log.md`:
  *"it's not in the start delay, it's in the passage from one note to the next"*
  localised the slider-insert bug after a full day of my reasoning had not;
  *"it was using the base rate, and ignoring the rest"* was the shared pan index,
  heard instantly; *"I suspect the problem is in the rate mode units stuff"* was
  the Host x accumulator; *"wiggling the slider brought them both back"* is so
  diagnostic it names one bug and almost no other; *"I can hear that real
  overtones don't dip everything else"* was correct at the level of the CONCEPT,
  against a design I had argued for from physics and got wrong. Asking what a
  control does at 0 caught a bug on its way out the door.
- **What to hold loosely is any MECHANISM attached to a report — including, and
  especially, my own.** When a report arrives as observation-plus-theory
  ("it crackles, I think it's CPU"), the observation is evidence and the theory
  is a hypothesis — and that is not a fact about who is speaking: my mechanisms
  are the ones that have actually hardened into false constraints here. So the
  move is never to discount the report. It is to ask **what it SOUNDS like**,
  which costs one question and gets you the observation underneath. The
  2026-07-27 Passage case is the whole lesson: the report said a real bug, in the
  harmonics engine, varying run to run — all three true — and I spent the session
  optimising CPU instead of asking.
- **Ask for the observation AND the read on it. Never for one instead of the
  other.** "Just tell me what it did, don't diagnose" sounds like it protects
  their time and actually throws away the best input the project has. The
  diagnoses here have repeatedly been right and faster than mine, and on
  2026-09-04 a correction to a test's own settings caught a **false fail** before
  it happened. What went wrong in the case that produced the rule was not that a
  theory was offered — it was that I acted on the theory and never asked what it
  sounded like. Hold the two apart: observation as evidence, mechanism as the
  lead worth checking first.
- **When a fix lands near an open bug, re-test the open bug.** One sat on the
  books for two weeks after being silently fixed, and a diagnostic plan was
  written for a problem that no longer existed.

### Scope

- **Search the repo and `git log` before estimating that something needs
  building or deciding.** The suite's recurring problem is not design, it is
  DISTRIBUTION: nearly every question hit has already been answered correctly
  somewhere in it. One evening turned up five decisions that had been made and
  never propagated, plus a migration tool being rewritten from scratch that
  already existed.
- **Validate the CHARACTER on a cheap or limited version before building the
  heavy engine.** Bubbler's granular loop was only built after a play-once
  version proved the sound was right.
- **Ask for an ear-test rather than assuming that path is dark.** Rozaya can
  reload projects and test.

### Design tells

- **When a control needs an external tool to be usable in bulk, its granularity
  is wrong.** A script existed purely to set one slider across eight slots by
  hand; the real fix was that the control should never have been per-slot.
- **Where a control has a dedicated on/off beside it, its VALUE defaults to
  something usable — never to the off sentinel.** Defaulting a voice's gain to
  −60 next to its own Active toggle means activating it gives silence and a 54 dB
  climb.
- **A selector default and a value default are a PAIR.** If `@slider` stamps the
  visible value into whatever the selector points at, the value slider's default
  is not a free choice: it is whatever the default-selected target should hold.
  Getting this wrong muted every fresh instance before its first sample.
- **Never label a multiplier with note-value notation.** `1/8` means an eighth
  NOTE everywhere else — faster than a beat — and here it meant one cycle every
  eight beats, the opposite end of the range. Label by what you hear: `every 8
  beats`, `1 per beat`, `8 per beat`.
- **The null entry in a sync picker must not be called `Free`.** In LFO UI
  everywhere, "Free" means free-running, i.e. NOT synced, so it reads as a second
  competing sync switch. `Custom` is the word.
- **Never change what a control MEANS without saying so on the control itself.**
  A silent unit change is "the same problem wearing different clothes" whether or
  not a mode gates it. Gate on one visible switch AND name it in every affected
  slider.
- **The dyscalculia rule is about arithmetic, not numbers.** Move the maths to
  the machine; keep the precise control. **Do not hide numbers behind mood
  labels — that was built once, delivered, and was insulting.** See *Whose job
  is whose* at the top for the story, which is the part that stops it recurring.

## JSFX gotchas baked in from past sessions

- **Slider IDs are primary keys.** Reaper preserves slider VALUES by ID across file edits. Renumbering existing sliders scrambles user state — V1 Active ends up holding V2 Gain dB's value, which clamps to a different range and silently breaks things. **Always add new sliders at the END of the slider range, never in the middle.** If a player reports "everything is wrong after the update," the fix is usually `git status` + re-add the plugin instance for clean defaults.
- **JSFX has reserved system variable names — `tempo` is one of them.** Several read-only variables expose REAPER state to the script: `tempo` (project tempo BPM), `play_state` (transport state), `play_position` (project position seconds), `beat_position` (project position beats), `ts_num` / `ts_denom` (time signature), `samplesblock` (block size), `num_ch` (channels), `srate` (sample rate), plus the `pdc_*` and `ext_*` config flags. **Assignments to read-only system variables are silently ignored** — `tempo = slider1` does nothing, and the variable keeps returning the project tempo (default 120). This caused a latent bug in rhythm-track from initial release through 2026-06-11: the master Tempo slider didn't change the metronome rate at all because `effective_tempo = max(10, tempo + ...)` was always computing against the project tempo. **Symptom signature:** a slider has no audible effect AND seems to "lock" at a value matching some REAPER state. **Fix:** rename your variable (we used `track_bpm` for rhythm-track). Full list of reserved names: [reaper.fm/sdk/js/var.php](https://www.reaper.fm/sdk/js/var.php). Audit pattern to catch this early: `grep -nHE '^\s*(tempo|play_state|play_position|beat_position|ts_num|ts_denom|samplesblock|num_ch)\s*=' src/*.jsfx` — should return no hits across the suite. Commit `ea8f201` was the fix.
- **EEL2 is CASE-INSENSITIVE for variable and function names — a global `W` and a parameter `w` are the SAME variable.** This is the nastiest naming trap because it produces total silence with no error. In `spectral_vowel_probe.jsfx`, `function set_window(w) ... ( W = w; ... )` looked like "assign the parameter to the global W" but `W` *is* `w` (case folded), so `W = w` was a self-assign of the local parameter — the global `W` that every `loop(W, ...)` in the analysis/synth read was never written, stayed 0, and every windowed loop ran zero times → the whole spectral voice was silent (dry passed fine). Diagnostics that gate tones on "did the FFT produce energy" all stayed dark, which *looks* like an FFT/transport problem and sent a whole session chasing the wrong thing (including a bogus "functions can't be called from @block" theory — they absolutely can). **Symptom signature:** a code path that by every trace *should* produce output produces exactly zero, and a variable you "set" inside a function reads back as its old/zero value outside. **Fix:** never name a function parameter or local the case-variant of a global it assigns to — here `set_window(wlen) ( W = wlen; )`. Audit: skim each `function f(args) local(...)` for any arg/local that case-folds onto a global the function writes. (Diagnosed 2026-06-28.)
- **Slider count limit is 256, not 64.** Modern Reaper JSFX supports `slider1` through `slider256`. An older "soft 64 cap" idea is captured in `docs/planned-features.md` from a 2026-05-25 design session, when polyrhythm_phase was at 59 and the conversation discussed staying at or under 64 as a project habit. That habit is no longer in force — use whatever slider count a feature actually needs. The plugin's slider count is a UX consideration (256 sliders in one plugin would be unusable), not a technical one. Don't collapse two sliders into one combined slider just to stay under 64 — that pattern (e.g. the "Direction & Reverse" 5-option slider in polyrhythm_phase) was a workaround for the soft cap and shouldn't be the default approach going forward.
- **Phase wrap discontinuity.** Any modulator computed as `sin(2π · k · phase)` where `k` is a non-integer (golden ratio, 2.4, 4.5, etc.) creates a discontinuity each time the carrier phase wraps. This shows up as a click at the fundamental rate. To use non-integer harmonics cleanly, you'd need a separate phase counter for the modulator (extra memory bank slot). For new waveforms, prefer integer harmonic multipliers (1, 2, 3, ...) unless you're willing to add the extra state.
  **Separate audit on the same accumulator: `ph += inc; ph >= TWOPI ? ph -= TWOPI;` is only correct while `inc < TWOPI` is GUARANTEED.** A single subtract cannot catch up once the per-sample step exceeds a full cycle, and anything indexing a sine table off that accumulator then reads past the end of the table. Check what a rate slider at its maximum, or a drift/ramp target, can push `inc` to. (Above `srate` in Passage's harmonic engine; fixed by moving the advance inside the audibility guard, which was also cheaper.)
- **When a crossfade hands a source from one oscillator bank to another, hand the PHASE over too — otherwise every handoff clicks, and it will look intermittent.** Any A/B crossfade engine (two voices, two banks, ping-pong grains) eventually reaches "the thing B was fading *to* is now A's job." If A resumes from its own phase accumulators, the waveform steps: same magnitudes, same frequency, but every partial restarts mid-cycle. **Symptom signature:** a click at transitions whose LOUDNESS varies wildly run to run — sometimes inaudible, sometimes a pop — because the step size is the difference between two unrelated phase sets. That randomness is what disguises a once-per-transition bug as a CPU dropout, and it sends you hunting for load problems instead. **Second tell, and a sharper one: the click lives in ONE engine, so it vanishes as that engine's own level goes to zero.** In Passage/Morpher the voice is scaled by `hlevel = cos(texture*PI/2)`, so the click is full at Texture 0 and *mathematically absent* at Texture 100 (Rozaya, 2026-07-28: "with 100 percent it was a non-issue"). A fault that tracks a crossfade slider is a fault in one side of the crossfade -- which localises it instantly, and is worth asking about before touching anything. **Fix:** on the swap, copy B's phase accumulators into A's (`hph[i] = hphB[i]` across all partials). A then resumes the exact waveform B was mid-way through; B's own phases don't matter afterwards because it re-enters at zero level and fades up. Mirror the copy for a backwards step, and make the two cases mutually exclusive — a two-slot bounce satisfies both tests at once and running both copies feeds each bank the other's already-overwritten values. Cost is one copy on the transition sample only. Reference implementation: the "voice phase handover" block in `@sample` of `src/spectral_vowel_passage.jsfx` (ear-tested by Rozaya 2026-07-27; the same plugin's slot changes clicked from birth until this landed). Applies to Passage's morph legs, any future two-bank morph engine, and manual crossfade sliders that cross a source boundary.
- **A slider renumber breaks shipped projects, but `@serialize` blobs survive it — so the repair is a text migration of the project's slider line, not another renumber.** REAPER restores plugin values by slider POSITION, so inserting a control mid-list shifts every value above it (Passage's Fade in/out shape at 10-11 pushed Wash grain's 150 onto Voice level dB, Auto-morph onto Audition, etc.). The `<JS_SER>` blob is a raw memory dump with no notion of slider numbering, so captures/banks come through untouched — which means the whole break lives in one plain-text line per instance and can be shifted in place. `tools/passage_migrate_sliders.py` is the worked example: a HOPS table of `(slider count this applies to, how many keep their place, values to insert)`, walked in order so a project two layouts behind migrates straight through in one run. Seed each new slider to whatever reproduces the OLD behavior (Linear fades, a one-frame capture average) rather than to the plugin's default — the project should still sound like itself. Keep the line's token width, preserve CRLF, and gate on the value count so it is idempotent and safe to re-run over a folder. **Still add new sliders at the END** — this is the repair, not a licence. And the assumption that lets you renumber freely ("no shipped projects yet") expires silently: Passage had real projects before the comment claiming otherwise was written. Check with `grep -rl <plugin>.jsfx --include=*.RPP` over the project folders before renumbering anything.
- **LCG random/noise generators overflow EEL2's 2^53 integer limit — use Park-Miller.** EEL2 does ALL arithmetic in float64, where integers are exact only up to 2^53 (9.0e15). A power-of-2-modulus LCG step `(seed * a + c) & 0xFFFFFFFF` only stays exact if `a * seed_max < 2^53`; with a 32-bit seed (`seed_max ≈ 2^32`) that means `a` must be under ~2^21. The glibc multiplier **22695477** violates this (`22695477 * 2^32 = 9.7e16 > 2^53`): the multiply silently ROUNDS before the bitmask, degenerating the "random" stream into a faint **periodic tone + DC offset**. This shipped in breath_gen / heartbeat / all three wombs on the right (decorrelated) channel only — audible as a subtle "swung" wobble on R that scales with volume (because it's baked into the signal). The left channels used 1664525 (`1664525 * 2^32 = 7.1e15`, just under the limit) so they were fine, which is why it was R-only. **Fix: Park-Miller / MINSTD** (`x = (x * a) % 2147483647`, a ∈ {16807, 48271, 69621}) — a prime modulus generator whose `a * modulus ≈ 1e14` sits ~60-90x under 2^53 by design, with full period and no low-bit patterning. Give the two channels DIFFERENT multipliers (e.g. 48271 / 69621) so they're genuinely independent, not phase-shifted copies; seed each nonzero in [1, 2^31-2]. EEL2's built-in `rand()` is fine for a single stream but is one shared sequence — you can't pull two independent deterministic channels from it, which is why these plugins roll their own. Reference implementation: the noise block in `src/breath_gen.jsfx`. Symptom signature: a faint periodic/tonal artifact on one channel that follows volume and survives into rendered files. (Diagnosed 2026-06-15; the two archived wombs keep the bug frozen-as-shipped.)
- **The Golden TS / SG slots are NOT what the names suggest** — and this is deliberate now. Polyrhythm Phase originally shipped with slot 3 ("Golden TS") as a phi-warped *sine* (not triangle, despite the name), and slot 4 ("Golden SG") with an extra sine pre-warp before the phi-warp. Melody Phase initially implemented them strictly per their names (warp → triangle, clean warp → sine), which made the two plugins SOUND DIFFERENT for the same slot. Reconciled 2026-05-24: all four oscillator plugins (Polyrhythm Phase, Melody Phase, Shepard Scale Generator, Shepard Tone Generator) now offer the same waveform palette at the same slot indices — **14 slots as of 2026-09-03** (Square and Pulse were appended at 12/13 by the 2026-06-26 Harmonic Sculptor work, which shares the same palette; that is five plugins carrying it, not four). Slots 3 / 4 / 5 match Polyrhythm Phase's original behavior (preserves existing project files); slots 10 ("Phi Triangle") and 11 ("Phi Sine") are the strict / manual-correct versions. Don't "fix" slot 3 to output a triangle — there are projects built on the sine sound. Shepard Scale + Tone gained the new slots 6–11 (Bell, Wavefold, Half-sine, Phi-cascade, Phi Triangle, Phi Sine) in this same change — they previously stopped at slot 5. **Convention going forward: any new waveform added to Polyrhythm Phase or Melody Phase should land in all four plugins at the same slot index.** Diverging waveform palettes between sibling oscillator plugins is exactly the inconsistency this sweep cleaned up.
- **Stop-sequence-style behaviors** don't apply here (no language model). What does apply: stay below 90° static L/R phase offset to avoid mono-cancellation on speakers; static phase offsets read as **lateralization** to the listener (ITD cue), not as width. True width without binaural beating requires either a) multi-voice unison with detune, b) chorus/ensemble effects with modulated delay lines, or c) all-pass filter networks. There's a session log of attempting (b) inside the plugin and reverting to "use Reaper's stock chorus AFTER the synth" — see git log around the pan-modes merge for context.
- **`@init` re-runs on every transport start by default.** This silently re-zeros all plugin memory (variables, arrays, oscillator phases, smoother states) on every press of the Reaper play button. Usually you WANT that (conventional Reaper "fresh start on play"), but if you ever need state to persist across stop/play (drift relationships, gate progression, accumulated phase positions), set `ext_noinit = 1;` at the top of `@init`. With that flag, `@init` only runs on actual plugin load and Reaper leaves memory intact at transport boundaries. Polyrhythm Phase v2 deliberately does NOT set this flag — the gate begins a fresh play period on every play press, matching v1 behavior. Documented at [reaper.fm vars.php](https://www.reaper.fm/sdk/js/vars.php).
  **The general rule that follows: with `@init` re-running per play, any design that needs to REMEMBER a value across transport is wrong unless it is explicitly guarded** (the `drift_cfg_inited` pattern). This shipped broken for an hour in Melody's Host x: `host_scale` was computed as a ratio against "the tempo this derivation was made at", the reference got wiped on the next play while the derived values still described the old tempo, and the tempo change silently vanished. The fix was to have nothing to remember — derive against a nominal constant and apply the live value per block. **A seeded bank is the same trap**: Womb's beats bank was seeded OUTSIDE its config guard, so every transport play reset it.
- **`play_state` enumeration** (verbatim from official docs): `0 = stopped, <0 = error, 1 = playing, 2 = paused, 5 = recording, 6 = record paused`. There's no `3` or `4`. Common pitfall: `play_state == 0` alone misses the pause case — use `play_state == 0 || play_state == 2` if you want to gate "transport is not advancing." For "transport is actively moving" (regardless of mode) use `play_state == 1 || play_state == 5`. Transport-edge detection via `play_state != last_play_state` is more robust than the `play_state > 0 && last_play_state == 0` pattern (which only catches stop→play, not pause→play or play→pause).
- **Transport-edge detection belongs in `@block`, not `@sample`.** `play_state` updates per block, never mid-block, so polling in `@sample` is wasted work. Audio behavior is the same; it's a code-quality / performance note. (Polyrhythm Phase v2 doesn't currently poll play_state at all — `@init` running per-play covers the reset case without explicit edge detection. Noted here for future plugins that might.)
- **The active-voice normalizer is per-sample, and it bites you when voices drop out.** Polyrhythm Phase divides its summed output by the count of currently-audible voices each sample. When voices come and go (Play/Rest gate, future per-voice mutes, anything that silences some voices but not others) the divisor shrinks and the surviving voices get LOUDER — up to +18 dB when only one voice is still audible. Fix: divide by `total_active` (precomputed in `@slider` from `v_active` toggles), so the divisor is stable across runtime voice silencing. Polyrhythm Phase v2 has the fix; the Play/Rest gate exposes it, but the fix is correct for the engine generally and should be the pattern for any future plugin that can silence voices at runtime.
- **Empty `()` from a comment-only conditional branch breaks compilation silently.** JSFX strips comments at compile time, so this:

  ```
  pr_resting ? (
    // stay where we are
  ) : (
    breath_state = 0;
    state_len = inhale_len;
  );
  ```

  ...becomes `pr_resting ? ( ) : (...)` to the eel2 parser. Empty paren block is a syntax error. The plugin fails to compile, but Reaper doesn't always pop a visible error — symptom is just "no sound." Discovered 2026-05-26 while adding Play/Rest to Breath Generator (commit `a546fce` is the fix). **Workarounds:** either invert the conditional to a one-armed form (`!pr_resting ? (...);` — only the populated case runs), or put a no-op like `0;` inside the empty branch. Whenever you write a `cond ? (...) : (...)` where one branch is "do nothing," prefer the one-armed inverted form so the parser never sees an empty block.
- **Anything DERIVED from a `@serialize` bank must be computed in `@block`, never in `@slider` — otherwise a restore leaves the derived value stale while the bank itself is perfect.** (Diagnosed 2026-08-19 in spectral_vowel_morpher; swept the suite the same night.) The nested-selector gotcha below covers the bank being *zeroed*; this is the sibling failure where the bank is **fine** and the values computed *from* it are not. **Mechanism:** `@slider` and `@serialize` restore by two independent paths with no guaranteed relative order. If `@slider` runs first it derives from banks still holding `@init` defaults — every gain 0, every ratio 1, every gating flag off — and then `@serialize` fills the banks in underneath and *nothing recomputes*, because the derivation only lives in `@slider`. The audio engine reads the derived arrays, so the plugin goes silent (or drift/ramp silently never runs) while every saved value is sitting right there intact. **Symptom signature, and it is an unusually clean one: touching ANY control fixes it completely** (that runs `@slider`), **and transport play/stop does not** — which is the tell that separates it from an `@init`/`ext_noinit` problem, since transport never calls `@slider`. Rozaya's report was "wiggling the slider brought them both back", which is this bug and almost nothing else. **Fix:** move the derivation into `@block`. It runs every block forever, so by the first sample of audio the values are correct regardless of what ran when; the cost is a handful of `pow()` per block against whatever the DSP is already doing. **Rule:** a value derived from a serialized BANK belongs in `@block`; only values derived from a SLIDER may live in `@slider`, because those arrive with the slider itself. **Audit:** `tools/scan_bank_derived.py` reports, per plugin, every `@slider` assignment whose right-hand side reads a bank that `@serialize` restores. Known-benign hits it will still print: debounce trackers (`last_cappoint`, `last_capavg`) and selector-load temps (`saved_target` in resonance_bank) — those are re-read fresh each time rather than cached for the engine. **Found in three plugins:** spectral_vowel_passage (`td_active`/`mod_active` — drift and ramp did not run on first load), womb_sound_generator_v3 (`breath_freq_active`), and melody_phase_v2, which was the worst: the entire per-voice configuration (note, step, duration, gain, active for all 8 voices) was derived in `@slider`. Every other plugin runs drift unconditionally and has no such flag, so the suite is clean as of the sweep.

- **A REAPER `.RPP` slider line is NOT a plain list of numbers. There is a `""` marker after slider 64, and a file-selector slider's value is a quoted string.** (Broke five Melody Phase projects on 2026-09-02; restored from backup.) The line under a `<JS>` block looks like a row of numbers and it is tempting to `split()` it and index by position. **Measured across all 377 JS value lines in the library**, the real shape is:
  - **64 sliders or fewer:** exactly 64 tokens, padded with `-` for slots with nothing stored.
  - **More than 64 sliders:** the first 64 values, then a quoted `""` token **at index 64**, then slider 65 onward. Always index 64; 76 instances, no exceptions. So the token index of slider N is `N-1` up to 64 and **`N` beyond it**.
  - **A file-selector slider stores a quoted filename**, not a number (`sustain_looper`'s slider 1). Never `float()` a quoted token.
  - `-` means "nothing stored" and can sit BETWEEN real values, not only trailing — the trap already recorded under the versioning rules. The `""` marker turned out to be a second flavour of the same thing.

  **Symptom signature, and it is a good one: values that cannot fit their control.** The Melody break showed `Rest mode = 8` on a 0-1 enum and `Drift shape = 8` on a 0-2 enum. Shift them back one and every value lands in range. **Range-check every migrated value against its slider's declared min/max** — it catches a shifted map in seconds and needs no ears.

  **Why it slipped through:** the verification compared the output against the same authored table the migration used, so it agreed with itself perfectly. Rozaya: *"read and compare, don't script."* Reading ONE real line beside the control names would have shown it immediately — and did, once asked.

  **Which plugins are exposed:** any with more than 64 sliders. Today that is `melody_phase` (82), `polyrhythm_phase` (82 declared, highest ID 86), `polyrhythm_phase_v3` (90), `shepard-tone` (75) and `shepard-scale` (64, i.e. exactly at the boundary and one slider away from crossing it). **Re-count rather than trusting these figures — they moved twice in one day on 2026-09-02.** **Polyrhythm v1 -> v3 is next in Phase 2 and both ends are over 64**, so it is squarely in this.

  **Fix: `tools/rpp_sliders.py`.** One module that parses a value line into `{slider_id: token}` and renders it back, marker and padding handled, with a round-trip check inside `render_line` so a shifted line cannot be written silently. It round-trips all 377 lines in the library byte-identically. **Every migration script uses it; none re-derives the format.** `morpher_migrate_layout.py` predates it, is correct because the Morpher has 40 sliders, and now refuses outright if it ever meets a quoted token.

  **`render_line`'s round-trip check does NOT cover the line ENDING, and that ate a line per instance on 2026-09-02.** `_split` originally noticed only a trailing `\r`, on the assumption callers passed lines already stripped of their ending. A caller using `splitlines(keepends=True)` therefore got back a line with **no ending at all**, which welded itself onto the `>` that closes the `<JS>` block — 17 lines silently lost in `upswing`, 19 in `outcoming`. The round-trip check passed the whole time, because the tokens were perfect. `_split` now handles `\r\n` / `\n` / `\r`, but the general lesson is the one that matters: **assert the line count and the instance count before writing.** Both Melody migration scripts do now, and it is a two-line check that turns a silent corruption into a refusal.

- **NEVER insert a slider in the middle of the list — and Melody Phase already had it done to it, which cost two projects three months of wrong sound.** (Diagnosed 2026-09-02; full writeup in `docs/open-bugs.md`.) The rule is stated twice above and it was still broken: commit `ac7f125` (2026-07-02, "Speed Ramp reaches all 28 targets") added **`Ramp target` at position 67**, count 75 → 76, pushing every control above it up one place. REAPER restores by POSITION, so every project saved before that date fed the **default Drift period of 8 into `Drift down`** and Drift shape's 0 into `Drift period`. Because the drift gate is `(up > 0 || down > 0)` and the period is `max(per, 1)`, drift went **ON, at a one-cycle period, on a plugin nobody had ever configured drift on** — the rate swinging down by up to 8 units every single cycle. At `upswing`'s 15 BPM that is 15 → 7 BPM, note by note.
  **Symptom signature, and it is a good one: the durations are wrong and the fault lands at the passage from one note to the next** (that is exactly where `cur_step` is sampled), plus **a value that cannot fit its control** — here `Drift period = 0` against a declared minimum of 1. Range-checking the decoded values found it in one look, after a day of reasoning had not. Rozaya localised it by ear before the code did: *"it's not in the start delay, it's in the passage from one note to the next."*
  **What made it survivable:** the same commit bumped the `@serialize` magic (`1000000+N` → `2100000+N`), so the blob's leading float32 is an EXACT gate for which layout an instance was saved on — and the blob itself, which a renumber cannot touch, is an independent witness for what the values should have been (every drift bank read `up=0, down=0, per=8, shape=0`, i.e. off). **If you ever do change a slider layout, bump the blob magic in the same commit.** It is the only thing that made this repairable without guessing.
  **Repair:** `tools/melody_migrate_drift_shift.py` (shift 67-75 → 68-76, seed the new 67 to 0 = Rate Value, which is what the old single-target Speed Ramp always acted on) and `tools/melody_verify_drift_shift.py` (5643 checks against the snapshot AND the untouched blob).
  **Audit — run it before believing any plugin is safe:** `for c in $(git log --format=%h -- src/<plugin>.jsfx); do echo "$c $(git show $c:src/<plugin>.jsfx | grep -cE '^slider[0-9]+:')"; done` — a count that goes UP is fine only if the new IDs are all at the END; check the boundary with `git show <c>:src/<plugin>.jsfx | grep -E '^slider(6[5-9]|7[0-9]):'` across the step.
  **It happened to EIGHT plugins, not one. I asserted "Melody Phase was the only plugin" in this file before running the audit; that was false, and the audit took two minutes.** The 2026-05-30 Speed Ramp sweep inserted `Speed ramp target` mid-list in **six** plugins in one pass — `melody_phase` (`ac7f125`), `Full_Feature_Tremolo` + `full-feature-sweeping-filter` (`d062bc6`), `rhythm-track` (`03470b5`), `shepard-scale` (`9c04c4a`), `shepard-tone` (`0e57cae`) — each shifting 8 sliders, all with the identical `Speed ramp duration -> Speed ramp by` signature. Separately: `full-feature-sweeping-filter` `d19873f -> ae4a655` (18 sliders, `LFO Start Phase` inserted), `shepard-tone` `d19873f -> 9cb8ecf` (**49 sliders**, `Root Note` inserted), `spectral_vowel_morpher` `62c1a47 -> bde91ba` (4, `Layer active`), `spectral_vowel_passage` `7abb9cd -> 0800774` (31, `Capture average`). The last two already have migrations (`morpher_migrate_layout.py`, `passage_migrate_sliders.py`); **the six-plugin Speed Ramp insert does not, and no project has ever been checked against it.**
  **The audit that found this is worth keeping as a standing check** — it walks every commit of every `src/*.jsfx` and flags any slider whose name became its neighbour's: that is the fingerprint of an insert, as distinct from an honest rename. Run it after any slider-layout change.

- **A slider you write from code needs `sliderchange()` or REAPER reverts it — it keeps its own copy.** Setting the variable is not setting the slider. Use `sliderchange(-1)` to refresh REAPER's display and parameter without touching automation; `slider_automate()` also makes the value stick but WRITES AUTOMATION, so it is right in a picker the user just moved and wrong inside `@serialize`'s restore branch. (Cost an evening in Womb: a slider written on mode entry silently reverted.)

- **Inverting a unit inverts its EDGE CASES — re-check zero and negative every time.** `1 / max(raw, 0.001)` looks like a safe clamp and is not: it clamps the DENOMINATOR, so an input of 0 comes out as 1000 rather than as "stopped". On a control spanning −1000..1000 that defaults to 0, every fresh voice would have screamed. Write `raw > 0.001 ? 1/raw : 0.001`. Caught before shipping only because Rozaya asked what 0 did. The same applies to any control whose meaning flips (period ↔ frequency, beats-per-cycle ↔ cycles-per-beat): **the value the user leaves alone is the one you must check first.**

- **When you introduce a SECOND TIME BASE, audit every accumulator — not just the obvious one.** Adding Host x to Melody scaled the sequencer and the envelopes correctly, and missed `start_delay_elapsed += 1 / srate`, which counts wall-clock seconds against a delay expressed in nominal cycles. **The symptom is nasty precisely because it is small and partial:** two instances meant to hand off sat *slightly* apart, which reads as sloppiness rather than as a units bug. Anything that accumulates outside the shared `dt` — pan phase, drift phase, rest timers — needs the factor applied explicitly, and anything added later does too.

- **Cascading N identical filter sections does NOT give you N times the slope at the same corner — and REAPER's own stock filters get their Hz wrong.** Two separate facts that bit together during the rolloff overhaul:
  - Cascading drags the composite −3 dB point DOWN by `sqrt(2^(1/N)-1)`; at six stages a 480 Hz cutoff really corners near 168. A correct cascade needs per-section **Butterworth Q** (computed pole angles, 1930s textbook, nothing to copy), resonance spread across sections (peaks add in dB, so per-section resonance multiplies), and **TPT rather than Chamberlin** — a six-stage Butterworth puts Q 3.83 on its last section before Resonance is touched at all.
  - **REAPER's stock `filters/resonantlowpass` — and its Resonant Lowpass and Sweeping Lowpass — read 2–5x high in Hz.** Its `cut = 2*fc/srate` is musicdsp #29's `f = 2*sin(pi*fc/sr)` **with the pi dropped** (measured 0.3184 against 1/pi = 0.3183). Our sweeping filters inherited this verbatim, so their "Frequency Hz" was never Hz — the real corner sat at 0.21x–0.77x the number, *varying with Resonance*, which made Resonance quietly a second frequency control worth nearly two octaves. If you ever reach for a stock REAPER filter, measure it.
  - **Verify a filter's frequency RESPONSE, not just that it is stable.** A "stable" check once passed a phaser whose allpass coefficient parked the phase transition up near Nyquist — perfectly stable, and it produced no audible notches at all.

- **Migrate what was RESTORED, never what was DEFAULTED.** Gate a blob migration on "this blob HAS the field" (`>= the magic that introduced it`), not on "this blob is old" (`< the current magic`). A pre-feature blob never wrote those banks, so an old-blob gate permutes the `@init` DEFAULTS — which were already in the current order — and moves them out of it. Silent, and it mutes things.

- **Plugins are hand-copied into `<REAPER resource>/Effects/glasswings/`, and copying never REMOVES anything — so a RENAME leaves a working, frozen twin behind.** A `spectral_vowel_morpher_v2.jsfx` sat there for a month, eight lines different from the file it was renamed from, loading fine and silently missing every change since. **Diagnostic tell: the orphan's mtime is older than its siblings' and it is absent from `git ls-files`.** Check the effects folder against the repo after any rename.

- **Host sync, four rules that were settled by ear and should not be re-derived.**
  (From the 2026-08 tempo-sync sweep.)
  - **Drift and Ramp amounts are in BPM in every mode, Host x included.** The
    plugin converts (`D BPM` = `D/tempo` in multiplier terms); the user never
    does. The multiplier form was tried twice and fails both times: at 0.1 slider
    steps the value you want is not reachable, and where the step is fine it
    still forces arithmetic to hit a musical destination.
  - **Lock what is constant; accumulate what is modulated.** Position-locking
    answers *"where would this be if it had run at this rate all along"*, which
    stops being the right question the moment drift or a ramp moves the rate.
  - **Effects lock per sample; sequencers place once.** A sequencer that
    recomputed its position continuously would jump mid-note.
  - **Before changing what a control's number MEANS, ask what the user holds in
    their head when setting it** — a figure they know (5 BPM of HRV) or a feel
    they are dialling for. Neither the code nor the label can tell you, and
    getting it wrong is the silent-unit-change failure.

- **EEL2 has NO scientific notation — `1e9` is a syntax error, not a big number.** Every other C-family language accepts it, so it gets typed on autopilot when you want "effectively infinity" as a sentinel (here: a High-cut fade threshold that no frequency can reach, so the fade multiplier is always exactly 1 when the control is off). REAPER reports it clearly — `@init:360: syntax error: 'hc_lo = 1 <!> e9;'` — but only when the plugin is loaded, so it survives every desk check. **Fix:** write the digits out, `1000000000`. **Audit:** `grep -nE '(?<![A-Za-z0-9_])[0-9]+(\.[0-9]+)?[eE][+-]?[0-9]+' src/*.jsfx` (ripgrep needs `-P` for the lookbehind) — should return nothing across the suite. Worth running alongside the paren-balance and empty-`()` checks, since none of those catch it. (Hit 2026-08-19 adding High cut to spectral_vowel_morpher; the whole suite was scanned and this was the only instance.)

- **Polyrhythm Phase voice memory layout** (16 slots each):
  - 0  osc_phase_l
  - 16 osc_phase_r
  - 32 trem_phase
  - 48 gain_l
  - 64 gain_r
  - 80 v_freq_l
  - 96 v_freq_r
  - 112 v_trem_freq
  - 128 v_active
  - 144 v_semitones
  - 160 v_dr (drift in Drift mode / rate in Independent mode)
  - 176 pan_phase
  - 192 pan_smooth
  - 208 v_pan_freq
  - 224 v_gain
  - 240 v_phase_off (last-known per-voice offset slider value)
  - 256 v_phase_off_last
  - 272 v_pan_static (target pan position for Spread / Spread Reversed modes)
  - 288 v_resting (per-voice Play/Rest flag: 1 = silent during rest, 0 = playing)
  - 304 v_pr_cycle (per-voice Play/Rest cycle counter, advances at the voice's own v_trem_freq)
  - 320 **is NOT free** — `chorus_buf` owns 320..8511, the drift / Ramp banks run
    8512..8927, and the per-cycle pan banks added 2026-09-02 took the next two:
    8928 `pan_cycle_index`, 8944 `pan_cycle_dir`. **The first free slot is now
    8960**, in both v1 and v3.
    This line used to say "320 onward: free for new arrays", which would have
    written a new bank straight through the chorus delay buffer, silently — and
    then it said 8928 was free for one day, until the pan work took it. **Do not
    trust the number written here; re-derive it.** `grep -nE '^[a-z_]+ *= *[0-9]{3,};'
    src/<plugin>.jsfx` lists every allocation in the file, and the last one plus
    its width is the answer.
- **JSFX can LOAD audio samples — it's not just live DSP.** Idiom (from stock `guitar/amp-model-dual`, used in `src/sustain_looper.jsfx`): a file-selector slider `sliderN:/foldername:default:Name` presents a dropdown of files in `<REAPER resource>/Data/foldername/` (NVDA-navigable as a list-parameter, same family as enum dropdowns). Then `fh = file_open(sliderN); file_riff(fh, nch, sr); n = file_avail(fh)/nch; file_mem(fh, buf, n*nch); file_close(fh);` reads interleaved samples. Reload only when `sliderN|0` changes. **Formats:** WAV and OGG are reliable; FLAC/MP3 are NOT guaranteed — export loop sources as WAV. **Memory:** ~8 million slots/instance by default (≈80 s of 48 kHz stereo, interleaved), max 32M via `options:maxmem=33554432` (≈5.5 min) — keep loaded samples short. `file_riff` with nch `'rqsr'` + a target SR auto-resamples (REAPER 6.29+).
- **JSFX `fft()`/`ifft()` operate on PERMUTED bin order.** To read or edit frequency bins by index you MUST call `fft_permute(buf,size)` after `fft()`, do the work in natural order, then `fft_ipermute(buf,size)` before `ifft()`. Skipping it corrupts the spectrum — a magnitude-preserving op (e.g. phase randomization) will *grow harmonics on a pure sine*, which is impossible if implemented right and is the diagnostic tell. (Surfaced building the Paulstretch-style `smear_stretch`, now archived.)
- **Muted/inaudible layers still cost full CPU — gate expensive per-grain / per-block DSP (FFTs especially) on the layer's LEVEL, or a busy project crackles.** JSFX runs the code whether or not its output is audible. In `spectral_vowel_morpher` at Texture 0 (pure voice, wash muted), the wash engine still ran two `FFTSIZE` inverse FFTs *per grain* on audio being multiplied by zero — a real per-grain load that tipped busy projects into occasional real-time-deadline misses: **non-clipping crackle on ~every slot.** That's the diagnostic tell — the crackle scales with project CPU load, NOT with signal level, and it eases when you free CPU / mute other tracks (a clip-driven crackle would do the opposite). **Fix:** gate the heavy work on the layer being audible — `have > 0 && wlevel > 0.0001 ? gen_grain();` — mirroring whatever guard the sibling/parallel layer already has (here the voice engine's `hlevel` guard). Keep the accumulator draining (read-and-clear) so the layer fades back cleanly over ~one grain when its level rises off 0; output is bit-identical while muted. Applies to ANY plugin computing a voice/band/layer whose gain can reach 0 — skip its expensive DSP when silent, not merely its output. (Fixed 2026-07-10, shipped **v2.18**, commit `1affa90`.)
- **The nested-selector pattern (selector slider + shared config sliders backed by a per-target memory bank) silently ZEROES the selected target on track duplicate — fix it in `@serialize`, not `@init`/`@slider`.** (Diagnosed 2026-07-02 during the automation-replacement sweep; researched against the Cockos docs/forums.) **Mechanism:** on load, slider *values* and `@serialize` memory are restored by two INDEPENDENT paths with no guaranteed relative order, and on a **track duplicate `@init` may not re-run at all** (memory is copied). If `@slider`'s "selector changed → load `bank[selected]` into the visible slider" branch runs while the bank is momentarily empty, it writes `slider = 0`, and `slider_automate()` in that branch propagates the 0 to REAPER's parameter so it sticks and then gets captured back into the bank. Only the *selected* target dies (it's the one backed by a live slider); non-selected targets survive straight from `@serialize` — that asymmetry is the diagnostic tell. **Why `@init`/`@slider` fixes fail:** an `@init` flag never runs on duplicate; an "adopt on first `@slider`" flag gets consumed by an early `@slider` firing with default (pre-restore) slider values. **The fix:** `@serialize` is the ONE section guaranteed to run on both load and duplicate. Inside it, `file_avail(0) >= 0` means READ (load/duplicate), `< 0` means WRITE (save/undo) — a reliable read/write discriminator. So after restoring the banks, on read, force the visible config sliders back to `bank[selected]` for each nested selector and call `sliderchange(-1)` to refresh REAPER's display/param (do NOT use `slider_automate` here — it would write automation). This re-establishes the "visible slider == `bank[selected]`" invariant authoritatively, regardless of what order `@slider` ran in. Reference implementation: the `file_avail(0) >= 0 ? (...)` block at the end of `@serialize` in `src/shepard-tone.jsfx` (ear/duplicate-tested by Rozaya). **Applies to every nested-selector block in the suite** — both Speed Ramp and Drift selectors — so any plugin with this pattern needs the fix (the pre-existing Drift selectors shipped with the latent bug since the v2.9 drift sweep).

- **An "adopt on first `@slider`" flag is NOT a load guard — it is the bug. Any tracker that answers "did the user just move this control?" must be adopted in `@block`.** (Proved 2026-08-23, and this is the *confirmed* mechanism the nested-selector entry above only predicted in passing: "an adopt-on-first-`@slider` flag gets consumed by an early `@slider` firing with default (pre-restore) slider values.") **Mechanism:** on a fresh or duplicated instance, `@slider` runs while REAPER is still handing over the saved parameter values. A tracker adopted there captures a **default**; the real value arriving a moment later then reads as a user edit, the change-detecting branch fires, and `slider_automate()` makes the write stick — so the damage is saved back into the project. **Worked example, with the number that proves it:** `infantile.RPP` held a Sweeping Filter in **BPM** mode, Rate Value **180**, and — invisibly — Host ratio on *"every 2 beats"*. That picker's table maps "every 2 beats" to the multiplier **0.5**, so every load and every track duplicate stamped Rate Value to exactly 0.5. Fixing it by hand held for the session (the tracker finally matched) and died on the next duplicate. **Two faults, and they are separable:** (a) the picker wrote its ratio **without checking Rate Mode**, while `slider_show` hid it outside Host x — so the control doing the damage was invisible and firing in a mode where it has no meaning; (b) the tracker was adopted in `@slider`. **The fix, both halves:** gate every picker's write on the same condition its `slider_show` uses (if it is hidden it must not write), and move the `!flag ? ( tracker = sliderN; flag = 1; )` adopt into `@block`, reading the **raw slider** rather than a `@slider`-local variable. `@block` cannot run before the instance is configured, so it adopts settled values whatever order the restore paths ran in; and while the flag is still 0, `@slider` fires nothing at all, which is the safe direction. **Consequence to handle:** once a picker is mode-gated it no longer self-corrects on reload, so entering the host-sync mode with a stale picker would name one speed on screen and run another (the raw multiplier hides behind the picker). Add a one-pass entry edge — `entered_host_mode = rate_mode_inited && sliderM == H && last_rate_mode != sliderM;` at the very top of `@slider` — and OR it into the picker's condition. **Applied across 15 plugins / 30 trackers** (every `host_ratio` and `pan_speed` picker, every "landing in Host x" block, and Womb's breath picker). Reference implementation: the `@block` head and `@slider` head of `src/full-feature-sweeping-filter.jsfx`. **Audit:** `grep -n '^!.*_inited ? (' src/*.jsfx` — any hit inside `@slider` is this bug. **Does NOT explain the `filt_stages` mystery** below: this proves `@slider` runs *early with defaults*, which gives a stage count of 1, not 0.

- **A plausible mechanism is not a finding, and this codebase has been bitten by the confusion twice. Say which one you have.** Both times the shape was identical: a mechanism that would explain the symptom got written down — and then quoted back later — as though it were the established cause.
  - **`filt_stages` (2026-08-19).** "A fresh Sweeping Filter has `filt_stages = 0`, so the cascade is a straight wire" explained the reported symptom perfectly. It was false: `@slider` *does* run on instantiation, just early with defaults, which gives 1 and never 0. The actual cause was the Host ratio picker stamping Rate Value to 0.5. The theory survived because it matched.
  - **Per-slot wash grain (2026-08-31).** "Changing `W` per slot would click, which is why Wash grain is global" was asserted as the reason for a design decision. Nobody has ever tested it. Reasoned through afterwards, the predicted symptom isn't even a click — it's an amplitude wobble over about one grain, from the overlap count sitting between two values, and it normalises out.
  - **The tell:** you can state the mechanism but not the observation that would separate it from the alternatives. If asked *"what would I hear if this theory were wrong?"* and there's no answer, it is a hypothesis.
  - **The cheaper question, every time: "what else produces exactly this symptom?"** Both cases had a second candidate that was the real one.
  - **Discipline when writing it down:** mark the status. This file already distinguishes *ear-tested ✓* from *NOT TESTED*, and the same applies to mechanisms — **proved / predicted / untested**. An unmarked mechanism gets read as proved by the next person, including by a later you. That is exactly how both of these hardened into constraints.



## Adding a new waveform to Polyrhythm Phase

1. Update `slider14`'s option list at the top of the file. Range becomes `0,N,1` where N+1 is the new option count.
2. Add a new `: waveform == K ? (...)` branch in the `@sample` voice loop's waveform chain. Compute `osc_l` from `osc_phase_l[i]` and `osc_r` from `osc_phase_r[i]`. Multiply by `gain_l[i] * v_gain[i]` (and `gain_r[i]` for R).
3. Update the Waveform section of `docs/plugins/polyrhythm-phase.md` **and
   `polyrhythm-phase-v3.md`** with a one-line description. (`docs/rozaya_jsfx_manual.md`
   is a stub redirect since the 2026-07-08 split — don't write to it.)
4. **A new waveform lands in all five plugins that share the palette** at the same
   slot index: both Polyrhythms, Melody Phase, Shepard Scale, Shepard Tone, and
   Harmonic Sculptor. Diverging palettes between siblings is the exact
   inconsistency the 2026-05-24 sweep cleaned up.
5. **Append it — never insert.** An enum option is an index stored inside a
   slider's value, so inserting one silently changes the waveform of every saved
   project. This is the one case where append survives the consistency sweep
   (R18); it is not a stylistic preference.

## Adding a new slider to Polyrhythm Phase (or any plugin)

- **Today: pick the next free slider ID at the end of the range, and do not
  insert mid-list.** See the two gotchas above on what a mid-list insert costs —
  it has happened to eight plugins in this suite and cost two projects three
  months of wrong sound.
- **This rule is scheduled to change, and hasn't yet.** R18 in
  `docs/suite-consistency-plan.md` says a new slider should go in its *logical*
  position once the plugin can migrate its own saved state on load from the
  blob's version magic. **That mechanism is the gate and it is not built** —
  Phase 2 hasn't started. Until it is, append.
- Read it in `@slider` after the existing reads — **unless it derives from a
  `@serialize` bank, or answers "did the user just move this?", in which case it
  belongs in `@block`.** Both have their own gotcha above; both produced real bugs.
- Use `slider_show(sliderN, condition)` to hide it conditionally. **If it is
  hidden, it must not write** — gate any write on the same condition the
  `slider_show` uses.
- If it persists state, decide whether it's a runtime tunable (don't persist) or
  saved per-instance.
- Give it a unit, sentence case, and a step size chosen from its range — the
  naming rules are R1–R19 in the consistency plan, not free choices.
- Document it on that plugin's page in `docs/plugins/`.
- Run `python tools/jsfx_lint.py src/<plugin>.jsfx` before you believe it
  compiles. It takes one file per run and defaults to the Morpher if you forget
  the argument — so a clean result on the wrong file is a real way to fool
  yourself here.

## Branches

- `master` — stable. Releases tag from here.
- `feature/*` — work in progress. Merge with `--ff-only` when ready (see git log for past examples).
- Don't work directly on master — use a branch and merge when validated by ear.
- **"Validated by ear" is the actual gate and it is not a formality.** JSFX
  cannot be compiled outside REAPER, so nothing here is verified by writing it.
  Rozaya can reload projects and test — **ask for an ear-test rather than
  assuming that path is dark.** Say plainly which parts of a change have been
  heard and which have not; this file marks that distinction everywhere and it
  is worth keeping.
- **Pushing is fine at any time. Cutting a release is not** — see *No releases
  until the sweep is finished* in the consistency plan. A release is a
  distribution artefact, and shipping one mid-sweep hands a stranger a
  half-renamed suite.

## Versioning: when to fork a plugin, when to archive it

**Full standard: `docs/versioning.md`.** Read it before forking, archiving, or
writing a migration — it carries the migration mechanics and a list of details
that each came from a migration nearly going wrong.

The short form:

1. **Default to editing in place.** Append sliders at the end, default them to
   the old behaviour, ship one file. This covers almost everything, including
   large changes — the Morpher grew fifteen layers, Solo, High cut and an octave
   ladder this way without ever forking.
2. **A new version must ship with a migration, or it does not ship.** A version
   nobody can cross to is not a successor; it is a second thing to maintain
   forever. Where the migration lives depends on where the state lives: a
   `@serialize` blob can migrate itself via a version magic, while slider values
   need a script in `tools/`.
3. **Archive only when the grep is zero** — never on the assumption that a
   successor superseded something:

   ```bash
   grep -rl <plugin>.jsfx --include=*.RPP /e/reaper
   ```

   Melody Phase v1 was archived because v2 existed, while five projects were on
   v1 and zero on v2. It had to be brought back out.
4. **Public is not the same as local.** A file with local users but no public
   future belongs in `archive/versions/`, frozen and annotated — out of `src/`,
   out of the release, out of `docs/plugins/README.md`.

**One fork is still open: Polyrhythm Phase v1 and v3.** v1 has 18 projects, v3
has 5, and the direction is that **v1 migrates UP to v3, then retires** — so v3
is where features get built, and v1 gets only what keeps it working. That
18 is the migration backlog, not a vote. Everything else in the suite is
single-version.

## Open bugs

`docs/open-bugs.md` — known-broken, not fixed. **Read it before touching the
plugin it names.** One entry: **Melody Phase instances come in out of alignment
on project open** — now only against `simple-sequence`, since the loud half of
that report turned out to be the 2026-07-02 slider-insert bug (fixed and heard,
`9a84e87`). **The cause is no longer unknown and there is a reliable workaround:
open the project, then press play and stop once** (alt-tabbing out of REAPER and
back does the same). Both re-run `@init` on every instance at the same sample, so
they all restart together. Renders were never affected. **Three wrong theories
are already burned** and the doc lists them so they are not tried again. One was
shipped and reverted, and a fix of that shape (holding the sequencer until the
transport moves) is **forbidden** — the plugin must keep sounding with the
transport stopped.

## Session log

**Moved to `docs/session-log.md`** — 414 lines of dated history, with a
topic index at the top saying which entry to read for which area of the suite.

It is worth opening when you want the *reasoning* behind something: why a
decision went the way it did, what was tried and rejected, what a bug actually
sounded like. It is not worth opening for facts — branch names, counts and
"still open" lists in it are mostly out of date, which is why it moved.

**Everything in it that is still a live rule has been lifted into this file** —
*How to work here* for practice, *JSFX gotchas* for mechanics. Follow those
versions. If you find a rule down there that isn't up here, that is a bug in
this file: lift it.
