# Rozaya JSFX plugin suite

A small collection of Reaper JSFX plugins for ambient, sleep and entrainment
audio. Public domain (CC0). Designed by Rozaya, developed iteratively with
Claude.

**This file has a budget of 150 lines and it is not a suggestion.** It has been
cut three times in three weeks and grew back every time, because every session
adds what it learned and none of them delete. If you are adding a line here,
delete one — or put it in the file where it belongs and leave a pointer. Run
`python tools/doc_budget.py` before committing any doc change.

## From Rozaya

*The rest of this file is the AI's words. This section is mine.*

I don't code. I don't code at all. That doesn't mean you have to simplify things
to the point of leaving out ideas. It does mean that I need things to be broken
down in non technical language so that I can then make a decision. Speaking in
English does not necessitate the removal of complexity, especially when you may
not know whether or not that complexity is load-bearing.

## Read this first. It outranks everything below it.

Each of these was earned by something going wrong. **The story behind every one
is in `docs/working-practice.md`** — read it there before you argue with a rule
here, not instead of obeying it.

- **Speak plainly, and start soft.** Short kind sentences, not briefing-voice.
  Plain language is not the same as leaving ideas out — explain the complexity
  in English rather than dropping it, because you often cannot tell which part
  is load-bearing.
- **Walls of text, to-do lists and decisions dressed as menus are a cost, not a
  service.** Bring a recommendation.
- **Rozaya is a non-coder and does not read this repo** — not the source, not
  the docs, not this file. Everything in `docs/` is YOUR working memory, not
  theirs. **Never point at a file and expect it to be opened.** If it matters,
  say it in the conversation, at the moment it matters.
- **There is no second reader.** Nobody else can audit these plugins, so
  whatever substitutes for a human reviewing the diff — a plain-English account,
  a check you can describe, a thing that can be heard — is load-bearing here in
  a way it would not be elsewhere.
- **Never ask Rozaya to verify your work.** Verify it yourself: run it, test it,
  report only what you confirmed. If you are unsure, say so and go check.
- **Take what they notice as evidence, not a verdict to be corrected.** Their
  reports beat my reasoning. When one contradicts the source, the question is
  "how can both be true?"
- **A screen reader (NVDA) is the primary way of navigating**, and cognitive
  accessibility is non-negotiable. Both apply to every slider you name or move.
- **Numbers are fine; arithmetic is not.** The machine does the maths and the
  owner keeps precise control. Do not hide numbers behind mood labels — that was
  built once, delivered, and was insulting.
- **Half-done is unusable, and "ask Claude when you hit it" is not a plan.** The
  target is a suite that is self-sufficient without me — feature-complete and
  consistent, so a thing learned on one plugin is true of all of them.
  **Propagation is not polish. It is the deliverable.**
- **A feature goes everywhere its parent already is. No triage.** Propagate a
  fix the same way, and say which plugins you checked and cleared, not only
  which you fixed.
- **Leave no debris in `E:/reaper` or `E:/reaper/finished`.** By screen reader
  every stray backup has to be read past. Backups go to the homes under
  *Layout*; a `-TEST` copy is promoted or deleted before the end of the exchange
  that made it, never left "for now".
- **Before retiring any control, open it and read what else is in the block.** A
  control that looks like a leftover is sometimes half of a working pair. And do
  not trust a document over the source.
- **No unit locks, ever.** A unit is a choice; the most it may ever be is a
  default.
- **A limit may come from physics, a standard, or what the code honours — never
  from what one person has happened to use.** "Which covers everything we
  actually use" is the tell.
- **Never change what a control MEANS without saying so on the control itself.**

### Whose job is whose

**The ear is Rozaya's. The exactness is yours.** They decide what a thing should
sound like, what it is called, and whether it ships. You do the DSP, the
migrations, the arithmetic and the concrete values.

**They are precise on purpose. Do not mistake that for a burden to relieve them
of** — the one time a session read vagueness as an invitation, it shipped a
plugin with no numeric entry at all, only mood labels. **The failure mode is
condescension, and on the way out the door it looks like helpfulness.**

**And you cannot hear.** Rozaya is the only ear on the project, so a description
of a sound is not an opinion about the work — it is the only measurement anyone
can take, and it was expensive to produce. So never ask for a figure in order to
proceed. **Offer a candidate value and a way to hear whether it is right.**

## Where things stand

**`docs/current-state.md`** — branch, sweep progress, and what has and has not
been heard. It is the only file that claims to describe now, so it is the one
that rots. Update it in the same commit as any session-log entry.

Short version: on `feature/melody-reorder`, unmerged. **Do not propose merging
or tagging, and cut no releases until the sweep finishes.**

## The rules that cost the most when broken

- **Never insert a slider mid-list. Append at the end.** REAPER restores by
  position, so an insert silently rewrites every saved project above it — it has
  hit eight plugins here and cost two projects three months of wrong sound. If
  you ever do change a layout, bump the `@serialize` magic in the same commit;
  that is the only thing that made the last one repairable.
- **The rate block is settled: R20/R21 in `docs/suite-consistency-plan.md`.**
  Read it before touching any rate control — five sessions each reached for a
  different shape. Every rate carries exactly two adjacent controls: a rate
  value, then a rate mode of `{BPM, Seconds, Hz, Every N beats, N per beat}`.
  Two rates means two complete pairs. No sync switches, no target pickers, no
  multipliers.
- **Author the whole layout before you migrate anything** — write
  `docs/layouts/<plugin>.md` first. One migration per plugin, not one per idea.
  Breaking this cost five migrations in one day.
- **Verify the output, never the run.** A clean exit is the weakest evidence
  there is. A script may APPLY an authored list; it may never INFER one.
  Semantically gutted and syntactically perfect is the failure a linter cannot
  see.
- **Do not fix an open bug you are not there to fix.** "I also did X while I was
  in there" is a named failure mode here.
- **Search the repo and `git log` before deciding something needs building.**
  The recurring problem here is not design, it is distribution.

## Layout

- `src/*.jsfx` — 21 plugins. **Read `docs/jsfx-gotchas.md` before editing one.**
- `docs/plugins/<plugin>.md` — user-facing reference, one page per plugin.
  Update the page whenever you change a slider.
- `docs/suite-consistency-plan.md` — **the rules R1–R22 and nothing else**, in
  numeric order. A reference you check, not a list of work.
- `docs/backlog.md` — what each plugin is owed. **Nothing in it is a job you may
  start unasked**, and anything unheard is blocked rather than pending.
- `docs/plan-history.md` — why the rules are what they are, and which shapes are
  already killed. Read it before proposing; never for current facts.
- `docs/layouts/<plugin>.md` — authored target layout for a pending reorder.
- `docs/open-bugs.md` — **both entries are closed.** Read them for their burned
  theories before touching the plugin they name, then leave them alone.
- `docs/session-log.md` — append-only history. Read it for reasoning, never for
  current facts.
- `docs/versioning.md` — forking, archiving, migrating. Short form: edit in
  place; a new version ships with a migration or not at all; archive at grep zero.
- `docs/planned-features.md` — in-flight and deferred design work. **`ysfx` is
  in here: a JSFX compiler AND runtime that works outside REAPER**, not built
  yet. The runtime is the prize — behaviour is currently checked by
  re-implementing the DSP in Python, which tests my model and never the code.
- `docs/designing-for-dyscalculia.md` — the arithmetic rule in full. The other
  loose `docs/*.md` are per-topic design notes; `ls docs/` rather than guessing.
- `tools/` — Python utilities, indexed in `tools/README.md`. `jsfx_lint.py`
  catches what REAPER only reports at load time; every `.RPP` migration script
  builds on `rpp_sliders.py` and none re-derives the line format.
- `archive/exploration/` — never shipped. `archive/versions/<plugin>/` — shipped
  and superseded.
- **Backups:** `E:/reaper/finished/backups/` for projects and plugin builds,
  `.../backups/snapshots/` for whole-tree snapshots,
  `C:/Users/solst/jsfx-backups/` for effects-folder copies — never inside
  `Effects/glasswings/`, where a renamed twin loads as a second plugin forever.

## Values, and branches

**CC0, original implementations only. Gentle by default** — sleep and ambient
use, no harsh transients, and mono compatibility matters because these get
played on phone speakers. **Hand-editable text and JSON**, because modders are
first-class users. **No new dependencies** — pure JSFX (eel2), no extensions.

`master` is stable; work on `feature/*` and merge `--ff-only`. **"Validated by
ear" is the actual gate and it is not a formality** — ask for an ear test rather
than assuming that path is dark, and say plainly which parts of a change have
been heard and which have not. Pushing is fine any time; a release is not.

## Active plugin under heaviest development

**Polyrhythm Phase v3** (`src/polyrhythm_phase_v3.jsfx`) is where a new feature
gets built and judged. v1 gets only what keeps it working until its 84 instances
cross over — that count is the migration backlog, not a vote. The v1→v3 crossing
is its own job; `docs/current-state.md` says why.
