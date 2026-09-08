# Working practice, and the incidents behind it

**Budget: 550 lines. Over it? Cut or archive before you add.**

`CLAUDE.md` carries these rules in one line each. This file carries *why* —
the day each one was earned, the quote, the number that proved it. Read it
when a rule in `CLAUDE.md` points here, or when you are about to argue with
one.

Moved out of `CLAUDE.md` 2026-09-08, verbatim. Nothing was cut in the move.

---

## Read this first. It outranks everything below it.

These come from what the person who owns this suite has asked for, and from
sessions where ignoring them did real harm. They are requirements, not
preferences. (Written generically on purpose: this repo is public, and a
person's access needs are theirs to disclose, not a maintenance note's. What a
future session needs is the requirement; whose it is, is not.)

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
- **Numbers are fine; arithmetic is not.** Reading, setting and nudging a value by
  ear is fine. `0.0625 ÷ 2` breaks; `480 − 440 = 40` does not. The machine does
  the maths and the owner keeps precise control. Do not hide numbers behind mood
  labels — that is a different mistake and it has already been rejected.
- **HALF-DONE IS UNUSABLE, AND "ask Claude when you hit it" IS NOT A PLAN.**
  Rozaya will not build with a plugin that cannot do the thing they reach for,
  and reaching for it mid-project is exactly when they cannot stop to have it
  built -- because a feature added on demand lands in ONE plugin and not in the
  others they will want it in next. Under that sits the real constraint, and it
  is not a mood: **they cannot code, and I may not exist in five years.**
  Rozaya, 2026-09-04: *"in five years, I'm gonna open this up and get an error
  in Claude Code or whatever saying the service is not available. I have to be
  ready for that."* So the target is a suite that is **self-sufficient without
  me** -- feature-complete and CONSISTENT, so that a thing learned on one
  plugin is true of all of them.
  **What this changes about my judgement:** "ship it now, fold the rest in
  later" is the wrong recommendation here, and I made it on 2026-09-04 and it
  landed as blaming Rozaya's own plan for the delay. When they say *it is not
  ready yet*, that is a design judgement about fitness for use from the only
  person who uses it -- take it as given, the same way an ear-test report is
  taken as given. **Propagation is not polish. It is the deliverable.**
- **Leave no debris in the folders they open.** `E:/reaper` and
  `E:/reaper/finished` are working areas. A `.pre-something-bak` beside a
  project is a monument to a migration that went wrong, and by screen reader
  every one of them has to be read past to reach the file actually wanted.
  Rozaya, 2026-09-04, having just swept ~44 of them out by hand: *"This is the
  working area. I can't want to do anything if it's cluttered with reminders of
  all the shit that I'm not happy about with these plugins... I'm starting to
  dread opening any of this."* **This is not tidiness. It is whether the
  project gets opened at all.** Backups go to the homes listed under *Layout*;
  a `-TEST` or `-MIGRATED` copy is promoted or deleted before the end of the
  exchange that made it, never left "for now".
- **BEFORE RETIRING OR DELETING ANY CONTROL, OPEN IT AND ASK WHAT ELSE IS
  INSIDE.** A control that looks like a leftover is sometimes half of a working
  pair, and the half you can see is not always the half doing the work.

  **The near-miss, 2026-09-04.** `docs/suite-consistency-plan.md` described Womb
  as "half converted -- `Every N beats (Host x)` AND Host x still in the enum",
  and said to retire the extra slider "the same way the picker does". I was
  about to. Rozaya stopped it: *"host x is the rate mode. every N beats is
  getting the multiplier out of there. neither of them work alone."*

  Exactly right. Womb's Rate Mode, Host sync target and `Every N beats` are ONE
  mechanism -- the mode says follow the project, the beats value says how fast,
  and the beats value is the thing that REPLACED the multiplier. Retiring it
  would have deleted the working half of a working pair, in a plugin with 8
  saved instances, on the authority of a document that was simply out of date.
  Womb was not behind; it got there first and the plan never caught up.

  **The check, and it is cheap.** Open the block and read what is in it. A
  control that is genuinely retired does exactly one thing and that thing is now
  pointless -- every `Host ratio` picker in this suite writes a rate slider and
  calls `slider_automate` on it, and nothing else, which is why all seven were
  safe to retire. A control that is half of a pair does something the other half
  depends on. Those look identical from the slider list and completely different
  from inside.

  **Same rule for code you have decided is dead.** Both Polyrhythms compute
  `entered_host_mode` and never read it. It is provably inert -- one mention per
  file, no readers even case-insensitively, no slider or memory touched -- and it
  is still left in, annotated, because deleting it buys nothing in a plugin with
  92 saved instances. Prove it, annotate it, and leave it alone unless removing
  it actually gains something.

  **And do not trust a document over the source.** The plan's Womb line had been
  wrong since R13-revised overturned the shape it assumed, and it read as
  authoritative the whole time.

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
- **SIMULATE A NEW MODE'S OUTPUT IN EVERY PLUGIN YOU ADD IT TO.** Reading
  confirms the wiring; only numbers confirm the behaviour. R21's `N per beat`
  shipped switched on in twelve plugins and **inverted in two** — 8 per beat gave
  one cycle every 8 beats — because their rate chain ended with the other host
  mode as its fallback. I had checked every gate and got every gate right, and
  never once asked what the new mode actually DID. **"Nothing broke" is not
  evidence a latent feature works**; nothing broke because nothing was stored on
  it yet.
- **CHECK THE @serialize STREAM, NOT JUST THE MAGIC.** A version bump proves you
  meant to change the format, not that you did. Heartbeat's magic was bumped
  while its four new banks were never written to the stream, so its settings
  would have vanished on save. Nothing caught it but grepping all five finished
  plugins for the same line and finding one zero. **After adding a bank, assert
  it appears in BOTH the file_mem list and the duplicate-fix block, in every
  plugin.**
- **A RANGE VIOLATION IS ONLY EVIDENCE IF THE MIGRATION CAUSED IT.** A value that
  was already out of range is a pre-existing oddity, and reporting it as a fault
  buries the real signal. Separate "was already out of range" from "is out of
  range now"; only the second is a failure.
- **PIN A VERIFIER TO A COMMIT HASH, NEVER `HEAD~n`.** A relative revision goes
  stale the moment anything else is committed, and the check then compares a new
  layout against ITSELF and reports catastrophic-looking shifts that are pure
  fiction. Happened twice in one afternoon. **A verifier that cries wolf is worse
  than none** — the whole point is that when it says FAIL, you stop.
- **A SAFETY CHECK THAT QUIETLY COVERS LESS THAN IT CLAIMS IS WORSE THAN NONE.**
  `scan_slider_ranges.py` matched the plugin path as `(\S+)`, so it stopped at
  the space in `heartbeat gen.jsfx` and **silently skipped every Heartbeat
  instance in the library** — reporting it only as a footnote nobody read. One
  plugin here has a space in its filename; REAPER quotes the path when it does.
  Word-splitting on it has now bitten three separate tools.

### Diagnosis

- **A plausible mechanism is not a finding. Mark it proved / predicted /
  untested.** An unmarked mechanism gets read as proved by the next person,
  including a later you; two have hardened into false constraints here that way.
  The test: *if this theory were wrong, what would I hear?* No answer means it is
  a hypothesis.
- **"What else produces exactly this symptom?" is the cheaper question.** Both
  times a wrong theory survived here, a second candidate was the real cause.
- **Rozaya's reports have a track record, and it is better than mine.** Start
  from the assumption that what is described is really happening, where it is
  said to be happening.
  **2026-09-08, and this one is the cleanest example yet: she said "sometimes I
  turn drift period off quickly to disable it" and I told her it did not
  work** — on the strength of a declared minimum of 1, which I read as proof the
  value was unreachable. She tested it; it stopped, as it always had. The
  mechanism I had missed was that two plugins reach "off" by arithmetic rather
  than by a gate. **A slider declaration is not evidence about behaviour, and a
  report from the only person who can hear outranks my reading of one.** The
  question to ask when a report contradicts the source is "how can BOTH be
  true?", never "you must be mistaken". *"it's not in the start delay, it's in the passage from
  one note to the next"* localised a bug a full day of my reasoning had not;
  *"wiggling the slider brought them both back"* names one bug and almost no
  other; *"I bet that 300 was the old wash grain value"* was right about a value
  I had just written a paragraph justifying. Asking what a control does at 0
  caught a bug on its way out the door.
- **Hold the MECHANISM loosely, never the report — and especially my own
  mechanism.** When a report arrives as observation-plus-theory, the observation
  is evidence and the theory is a lead. Ask **what it SOUNDS like**: one question,
  and it gets you the observation underneath. In the 2026-07-27 Passage case the
  report was right on all three counts and I spent the session optimising CPU
  instead of asking.
- **Ask for the observation AND the read on it, never one instead of the other.**
  "Just tell me what it did" sounds like it protects their time and throws away
  the best input the project has.
- **A NEGATIVE TEST RESULT IS A RESULT.** A prediction that does not appear is
  evidence against the prediction, not a puzzle to explain until it survives.
  **The rescuing explanation is the tell** — convincing by construction, because
  it was built to fit. Shipped once on exactly that, and reverted.
- **WHEN REPEATED CHECKS OF A SUSPECT COME BACK CLEAN AND THE SYMPTOM IS STILL
  REAL, STOP RE-CHECKING THE MAGNITUDE AND CHECK THE ORIGIN.** 2026-09-06: twice
  I verified a Start delay's arithmetic and correctly reported it consistent —
  every quantity really did count beats properly. The defect was not *how much*
  was counted but *when counting began*. The paper was right and the question was
  wrong.
- **A ONE-SLIDER TEST BEATS THREE ROUNDS OF SOURCE READING.** Same day: setting
  Start delay to 0 isolated the fault in seconds, after I had read the delay and
  placement code twice without convicting either. Reach for the discriminating
  test earlier — and when a report contradicts a lead, re-read the report before
  abandoning the lead.
- **A COMPENSATING ERROR IS NOT A SPARE PART.** When you remove one half of an
  accidental cancellation, go looking for what the other half was quietly paying
  for. A stale cached value was silently performing a subtraction; making it live
  removed both.
- **When a fix lands near an open bug, re-test the open bug.** One sat on the
  books for two weeks after being silently fixed.

### Scope

- **DO NOT FIX AN OPEN BUG YOU ARE NOT THERE TO FIX. "I also did X while I was in
  there" is a named failure mode here.** Rozaya, 2026-09-05, on why the Melody
  alignment entry was closed rather than left open: *"having another instance
  panic over a supposedly open bug and try to fix it while also doing other
  things as 'I also did x while I was in there' is how we wound up with
  errors."* An OPEN status reads as a job to a session arriving mid-task, and
  the forbidden transport-gate fix was shipped exactly that way once already.
  **A known bug with an accepted workaround is DONE.** Both entries in
  `docs/open-bugs.md` are now closed; read them for their reasoning before
  touching the plugin they name, then leave them alone.


- **Search the repo and `git log` before estimating that something needs
  building or deciding.** The suite's recurring problem is not design, it is
  DISTRIBUTION: nearly every question hit has already been answered correctly
  somewhere in it. One evening turned up five decisions that had been made and
  never propagated, plus a migration tool being rewritten from scratch that
  already existed.
- **AUTHOR THE WHOLE LAYOUT BEFORE YOU MIGRATE ANYTHING. One migration per
  plugin, not one per idea.** Write `docs/layouts/<plugin>.md` first — every
  slider in its final position, every enum in its final order, every control the
  plan still owes it. Then build and migrate, once.

  **Why it is a rule.** A migration costs the same whether one thing changes or
  forty, and every one is a fresh chance to corrupt every project using that
  plugin. Paying that risk repeatedly buys nothing. **Breaking it cost FIVE
  migrations in one day (2026-09-04)** — the Morpher's 38 projects rewritten
  three separate times, Tremolo and the Sweeping Filter twice each. Nothing was
  lost; the risk was just spent five times for one pass of work. Rozaya: *"so
  fuck not having to migrate only once. got it."*

  **Why it happened, which is the reusable part:** I worked reactively — one
  instruction, one change, one migration — instead of reading the plan first and
  collecting everything that plugin was already owed. Every one of those changes
  was implied by something already written down.

  **The check, before writing any migration:** does the layout doc exist, is it
  current against the file, and does it cover everything the plan still owes this
  plugin? If not, stop and author it. **A migration written before its layout is
  a migration you will write again.**
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
- **A WRAPPED control has no values past one wrap, and its RANGE will lie about
  that.** Anything expressed as a position inside a repeating cycle — an offset, a
  phase, a start point — folds back: 125% of a beat IS 25%. So most of a wide
  range is duplicates, and a person typing a round number can land on a no-op
  forever. **Say the wrap on the control itself** (`Bloodflow offset (wraps at one
  heartbeat)`); the range can stay wide when one slider serves several units,
  because that is a real cost and narrowing it just moves the lie.
- **NEVER call a within-cycle position `Cycles`. It is `% of <the thing>`.**
  Cycles COUNTS whole cycles everywhere in this suite — a drift period of 8. A
  position inside ONE cycle is always a fraction, so in cycles every whole number
  is a no-op and the control reads as broken. **This shipped twice in one day**
  (2026-09-06, Womb's Systole and its Bloodflow offset); the second time it
  survived a source comment I wrote arguing the two cases were different. They
  were not. Rozaya caught both: *"cycles in fractions? I thought cycles were
  cycles lol"*, and then found the second by using it and hearing nothing.
- **A PERCENTAGE OF A MOVING BASE IS THE FORBIDDEN SHAPE, AND IT ALWAYS ARRIVES
  LOOKING LIKE THE ACCESSIBLE OPTION.** `docs/designing-for-dyscalculia.md`
  line 120 names it: *"A percentage of a global is a ratio wearing a friendly
  hat."* A `Slot dwell %` was built here on exactly that reasoning and had to be
  undone; the fix was a per-item ABSOLUTE in seconds. **Percent is only ever
  allowed as percentage points of a NAMED, FIXED thing** (`% of inhale`,
  `% of cycle`), which is R17's rule already.
  **Proposed again on 2026-09-08** — a drift amount as "±20% of the current
  rate" — and rejected on sight: *"absolutely fucking not... go read the
  dyscalculia doc."* It was worse than the version already undone, because the
  base moves (rate + ramp + live tempo), so the proportion cannot be held in
  mind even in principle. **The tell is that it feels like it removes a unit
  problem.** It removes the unit and leaves the arithmetic.
- **`Drift period` = 0 MEANS OFF, in all 19 plugins. Made EXPLICIT 2026-09-08.
  It already worked in 15 of them, and Rozaya said so and I did not believe
  her.** She told me plainly: *"Sometimes I turn drift period off quickly to
  disable it."* I read the declared minimum of 1, concluded 0 was unreachable,
  and told her her own practice was impossible. **She then tested it and it
  stopped, "the way it always has, with every build."** Her report was right and
  my reading of a slider declaration was not evidence against it.
  **How it already worked, which is worth knowing:** thirteen plugins gate on
  `per > 0` explicitly (since 2026-06-09/11). The Morpher and Passage got there
  BY ACCIDENT — their advance is `1.0 / max(dper * srate, 1)`, so a period of 0
  makes the increment exactly 1.0, the phase lands on 0.0 every sample, and
  `sin(0)` is zero: the offset is permanently zero and the drift is silent.
  Simulated, not assumed. **Only Melody and the two Polyrhythms behaved badly**
  (`max(per,1)` → a full wander every rate cycle) — and those three have drift
  configured in ZERO saved instances, which is why she never met it.
  So the change made an accident into an intention in two plugins and fixed
  three nobody uses drift in. **It did not repair anything anyone was hearing.**
  The earlier claim in this file that "it never worked" was mine and it was
  wrong. The declared minimum was **1** in
  18 of 19 plugins, so 0 was unreachable; and in Melody and both Polyrhythms the
  code did `per = max(per, 1)`, which turns a 0 into the FASTEST drift the
  control can produce — one full wander per rate cycle. Exactly backwards from
  what the control reads as.
  **The gate is THREE MONTHS old, not two days — I got this wrong twice and
  Rozaya asked the question that caught it.** Walked properly, `&& per > 0`
  first appears in `976dc70` (Womb, 2026-06-09), then eight plugins on
  **2026-06-11** (`854952d` Tremolo, `e9db305` Breath, `bf846e5` the sweeping
  filter, `b285560` Heartbeat, `a06ff95` rhythm-track, `d711c52`/`6e7edb1` the
  Shepards, `d4178a7` Sweep Dwell), Veil in July, and Bubbler / Dapple /
  stereo-phaser on 2026-09-05. **And the slider was already declared
  `<1,1000,1>` in the same commit that added the gate**, so it was unreachable
  from the moment it was written. Dead code from birth, for three months. **A
  gate on a value the slider cannot produce is not a feature, it is a
  note-to-self.**
  **THERE IS NO WINDOW IN WHICH IT WORKED AND THEN BROKE.** That matters,
  because "it regressed recently" is the comfortable story and it is false —
  nothing to hear was ever lost. My first attribution said commit `7e63784`,
  2026-09-06, eleven plugins; that came from a history walk whose `uniq -f2`
  collapsed the transition and reported the wrong side of it. **Walking a
  history to find when something appeared: print EVERY commit and read the
  flip, never summarise inside the pipeline.**
  The fix: range `0..1000` and `0 = off` in the name everywhere, the three
  clamps replaced by the gate, and the Morpher and Passage gated on their
  `td_active` (they had neither, and would have advanced a whole drift cycle per
  SAMPLE at 0). **No migration was needed and none was written** — because the
  minimum had always been 1, no saved project can hold a period below it, which
  is a one-grep argument and beat three failed library scans.
- **NO UNIT LOCKS. EVER. A unit is a CHOICE, and the most it may ever be is a
  DEFAULT.** Rozaya, 2026-09-08, on my deciding that a pitch drift amount would
  always be in cents: *"The minute that kind of collapse is happening it's a
  sign to stare at it harder... Still, the same principles apply. No unit locks.
  ever."*
  **Why it happened is the reusable part.** A JSFX enum cannot change its
  options depending on what a selector points at, so "the unit list depends on
  the target" has no direct expression — and instead of SAYING that, I picked
  one unit and wrote it up as a principle. **A workaround presented as a rule is
  the tell.** The fix was one per-target `Drift amount unit` slider with
  `Target default` at position 0, which keeps every saved value honest and makes
  the old fixed unit a default rather than a cage.
  **The one standing exception is the rate's "amounts are in BPM in every
  mode"**, which was settled by ear twice and which Rozaya explicitly granted as
  *"an unusual exception"*. Do not extend it to anything else, and do not
  re-derive it as a general principle — it is a default that predates the
  control that would have expressed it properly.
- **A LIMIT MAY COME FROM PHYSICS, A STANDARD, OR WHAT THE CODE HONOURS. IT MAY
  NEVER COME FROM WHAT ONE PERSON HAS HAPPENED TO USE.** Measuring the library
  tells you a control is too SMALL. It has no authority over where the top goes.
  Rozaya, 2026-09-08: *"setting things to 'what makes sense' or 'what's already
  there' is an artificial limit based on one user's usage patterns to a
  public-facing suite."*
  **This corrected me twice in one sitting and the second time I had already
  been told.** Sizing R22's note list, I wrote C1-C7 (covers the 88 stored pitch
  values plus headroom), was told to widen rather than reduce, wrote C0-C8 — and
  that was still her projects setting a stranger's ceiling. The answer was the
  full MIDI range, because a standard is principled and a measurement is not.
  **The tell: if the justification contains "which covers everything we
  actually use", it is this mistake.** 20 Hz to 20 kHz is fine — that is the
  audible range, a fact about ears. `0..1500` because nobody went higher is not.
- **The dyscalculia rule is about arithmetic, not numbers.** Move the maths to
  the machine; keep the precise control. **Do not hide numbers behind mood
  labels — that was built once, delivered, and was insulting.** See *Whose job
  is whose* at the top for the story, which is the part that stops it recurring.


---

### Settled — do not re-derive these

Each cost a session or more. The reasoning lives in the plan and the session log;
what matters here is that they are **decided**.

- **The rate block.** Full rule under *Terminology* below. Five separate sessions
  each reached for a different shape here.
- **A FEATURE GOES EVERYWHERE ITS PARENT ALREADY IS. No triage.** Rozaya,
  2026-09-04: *"Anything that has Ramp should have all the controls that go with
  Ramp. End of fucking story."* Do not decide on my own hearing — which I do not
  have — that some plugin will not benefit and skip it. **A bug is a feature's
  twin: propagate a fix the same way, and say which plugins were checked and
  cleared, not just which were fixed.**
- **Ramp time unit** is `{Cycles, Seconds, Minutes, Beats}`, **default Minutes
  (index 2, not 0)**. **Drift period unit** is `{Cycles, Seconds, Beats}`,
  **default Cycles**, everywhere the plugin has a rate to count cycles of (Veil
  is the one principled exception — no rate, no cycles).
- **A DECLARED DEFAULT IS A LIVE VALUE** for every instance that never touched
  the control. Putting a new meaning at index 0 silently reinterprets all of
  them. Move the declared default to wherever the old meaning landed.
- **The canonical reading order:** what the plugin IS → its rate (value, then
  mode) → the shape of its movement → stereo and pan → output level → transport
  → drift → ramp. A modifier is numbered immediately after what it modifies; a
  second rate carries its own complete pair.
- **`docs/open-bugs.md`: BOTH entries are CLOSED.** Neither is a job. Read them
  for their burned theories before touching the plugin they name, then leave them
  alone. An OPEN status reads as a job to a session arriving mid-task, and that
  is how the forbidden fix got shipped once already.

### Terminology that changed, and where the old words survive

`docs/session-log.md` is **append-only and is not rewritten**, so it uses the
names that were current when each entry was written. Plugin pages can lag too.
Three renames matter when reading any of them:

- **`Speed ramp` is now `Ramp`** everywhere the user can see. Internal variables
  are still `speed_ramp_*`, which is fine.
- **`Host x` is retired as a name.** It is `Every N beats`, and the rate value
  there means beats per cycle. The history calls it a *multiplier* of the project
  tempo, which is what it was until 2026-09-02. **No plugin multiplies any more.**
- **`Host ratio` pickers are gone**, all of them.

**THE RATE BLOCK IS SETTLED — R20/R21 in `docs/suite-consistency-plan.md`. READ
THAT BEFORE TOUCHING ANY RATE CONTROL.** Five separate sessions each reached for
a different shape here, and Rozaya — who cannot read the source to check us — had
to catch it every time.

**Forbidden, and every one of them was built here at some point:** a
`Sync to host` switch, a `Host sync target` selector, a free-standing
`Every N beats` slider, a `Host ratio` picker, any control whose job is to write
into another control, and any multiplier in any mode.

**The argument that keeps resurrecting the dead shape, and the number that kills
it.** It is said that a plugin syncing two things independently needs a target
selector, because one rate value cannot express two beat counts. True and
irrelevant — the second rate has its own value. The real gap was that Melody's
pan had no mode of its own, so there was nowhere to put the host mode for it. One
slider fixed that; three were spent instead. And across 73 Melody instances, all
27 synced ones targeted the sequencer and **not one** targeted the pan.

**`Every N beats` and `N per beat` are RECIPROCALS and both are needed.**
Retiring the old pickers kept only the slow half, so eight cycles per beat had to
be typed as `0.125` — arithmetic, which is the barrier this suite exists to
remove.

**Two gates, and the difference matters.** A test meaning *am I host-synced*
covers both host modes and is written `>= 3`. A *conversion* asking *which mode
am I* stays exact, because the two modes are reciprocals and using one formula
for both runs the plugin at the wrong speed, silently. Getting this backwards is
how `N per beat` shipped inverted in two plugins on 2026-09-05.

