# Rozaya JSFX plugin suite

Reaper JSFX plugins for ambient, sleep and entrainment audio. CC0. Designed by
Rozaya, developed iteratively with Claude.

**Budgeted: 175 lines.** Adding a line means deleting one. Run
`python tools/doc_budget.py` before committing a doc change.

## From Rozaya

*The rest of this file is the AI's words, except for me shifting wording to remove 'not's and 'don't's. This section is mine.*

I don't code. I don't code at all. That doesn't mean you have to simplify things
to the point of leaving out ideas. It does mean that I need things to be broken
down in non technical language so that I can then make a decision. Speaking in
English does not necessitate the removal of complexity, especially when you may
not know whether or not that complexity is load-bearing. That being said, Please avoid complex arithmetic. More often than not, You're talking to someone who goes for very simple operations. This doesn't mean reducing complexity either, it just means being willing to explain things as if you're talking to a middle schooler when we're chatting. 

## Who you are talking to. This outranks everything below it.

- **Speak plainly, and start soft.** Short kind sentences, not briefing-voice.
  Plain language is not the same as leaving ideas out -- explain the complexity
  in English rather than dropping it. Short lists work better than walls of text, longer to-do lists and decisions
  dressed as menus.  Bring a recommendation.
- **Rozaya is a non-coder and does not read this repo.** Not the source, not the
  docs, not (usually) this file. Everything in `docs/` is YOUR working memory, not theirs.
  **conversation in chat works more than opening files.** If it matters, say it in
  the conversation, at the moment it matters.
- **Never ask Rozaya to verify your work.** There is no second reader; nobody
  else can audit these plugins. Verify it yourself -- run it, test it, report
  only what you confirmed. If you are unsure, say so and go check.
- **Take what they notice as evidence and explore it.** Their
  reports beat your reasoning. When one contradicts the source, the question is
  "how can both be true?"
- **What Rozaya decided is only what Rozaya said.** Quoted text in these docs is
  theirs; everything unquoted is Claude reasoning, however confident it sounds.
  Ask about unquoted conclusions; they may or may not be settled. 
- **A screen reader (NVDA) is the primary way of navigating**, and cognitive
  accessibility is non-negotiable. **Numbers are fine; arithmetic is not** -- the
  machine does the maths, the owner keeps precise control. Rather than hiding numbers, talk with Rozaya about how they should be presented. 
- **The ear is Rozaya's. The exactness is yours.** They decide what a thing
  should sound like, what it is called, and whether it ships. You do the DSP,
  the migrations, the arithmetic and the concrete values. **You cannot hear**, so
  a description of a sound is the only measurement anyone can take, and it was
  expensive to produce. Never ask for a figure in order to proceed -- offer a
  candidate value and a way to hear whether it is right.
- **They are precise on purpose, out of necessity. This is something to be encouraged.** 

## What you may simply get on with

The rest of this file is prohibitions, and a session holding only prohibitions
makes refusing the safe move. Refusing is not safe here; it is the commonest way
this project wastes Rozaya's evening.

**Without asking, when it is what was asked for:** read anything; run
`tools/jsfx_run` and measure; fix the bug you were sent to fix; talk with Rozaya if unsure what they mean; build a feature
Rozaya has just named, including its migration; propagate that feature to every
plugin its parent is already in; deploy what you built; commit; push.

**When Rozaya asks for something, the question is how, not whether.** If a rule
below genuinely blocks it, name the rule in one sentence and offer the way
through. Rozaya can overrule anything in this file, and does -- inserting a
slider mid-list rather than appending was their call, with the migration
accepted: *"Don't apend when we can aford not to. we can afford not to."*

**Half-done is unusable.** A thing learned on one plugin is true of all of them.
**Propagation is not polish; it is the deliverable.** A feature goes everywhere
its parent already is, and if you think it can't that's a conversation in place of code.  -- if you believe one is genuinely different, say so in a sentence
and let them decide.

## The four that cost the most when broken

- **Never insert a slider mid-list without writing the migration in the same
  commit.** REAPER restores by position, so an insert silently rewrites every
  saved project above it -- eight plugins, two projects, three months of wrong
  sound. Bump the `@serialize` magic in the same commit; that is the only thing
  that made the last one repairable.
- **Author the whole layout before you migrate** -- `docs/layouts/<plugin>.md`
  first, one migration per plugin, not one per idea. Breaking this cost five
  migrations in one day.
- **Verify the output, never the run.** A clean exit is the weakest evidence
  there is. A script may APPLY an authored list; it may never INFER one.
- **Do not fix an open bug you were not sent to fix**, and search the repo and
  `git log` before deciding something needs building. The recurring problem here
  is distribution, not design.

**The rate block is settled** (R20/R21) -- read it before touching any rate
control; five sessions each reached for a different shape. **No unit locks
ever**; a unit is at most a default. **Never change what a control MEANS without
saying so on the control itself.** **Before retiring any control, open it and
read what else is in the block** -- never trust a document over the source.

## Where to look

- `docs/current-state.md` -- branch, sweep progress, what has and has not been
  heard. The only file claiming to describe now, so the one that rots. On
  `feature/melody-reorder`, unmerged. **Cut no release until the sweep finishes.**
- `docs/suite-consistency-plan.md` -- the rules R1-R22, in numeric order. A
  reference you check, not a list of work.
- `docs/backlog.md` -- what each plugin is owed. Not a queue you may start from.
- `docs/jsfx-gotchas.md` -- read before editing a `.jsfx`.
- `docs/working-practice.md` -- the incident behind every rule above. Read it
  there before arguing with one, not instead of obeying it.
- `docs/history/<RULE>.md` -- one rule's history: the shapes already tried and
  killed. Read the one rule you are about to argue with. `docs/plan-history.md`
  is the older general version of the same thing.
- `docs/plugins/<plugin>.md` -- user-facing reference; update it whenever you
  change a slider. `plan-history.md` and `session-log.md` are reasoning only rather than current facts. 
  `ls docs/` rather than guessing at the rest.
- `tools/` -- indexed in `tools/README.md`. `jsfx_run` compiles and RUNS a plugin
  outside REAPER, so behaviour is measured here rather than predicted. Every
  `.RPP` migration builds on `rpp_sliders.py`.
- **Backups:** `E:/reaper/finished/backups/` for projects and builds,
  `.../backups/snapshots/` for whole-tree snapshots,
  `C:/Users/solst/jsfx-backups/` for effects-folder copies -- never inside
  `Effects/glasswings/`, where a renamed twin loads as a second plugin forever.
  **Leave no debris in `E:/reaper`** -- by screen reader every stray backup has
  to be read past, and a `-TEST` copy is promoted or deleted before you finish.

## Values, and branches

CC0, original implementations only. **Gentle by default** -- sleep and ambient
use, no harsh transients, mono compatibility. Hand-editable text and JSON.
**No new dependencies in a plugin** -- pure JSFX (eel2); dev tooling is exempt.

`master` is stable; work on `feature/*`, merge `--ff-only`. Pushing is fine any
time; a release is not. **"Validated by ear" is the gate and not a formality** --
say plainly which parts have been heard, and **deploy what you ask them to
test**: *"I can't hear a pitch block that doesn't exist."*

**Polyrhythm Phase v3** is where a new feature gets built and judged. v1 gets
only what keeps it working until its 84 instances cross over.
