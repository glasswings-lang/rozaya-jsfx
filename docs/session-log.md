# Session log

History, newest first. **Append-only, and NOT kept current** — each entry
describes what was true on its own date.

## What this file is for, and what it is not for

It is here for the **reasoning**: why a decision went the way it did, what was
tried and rejected, what a bug's symptom actually sounded like from the
listening chair. None of that goes stale.

**The facts in it do.** Branch names, slider counts, project counts, "still
open" lists and ear-test status were all true once and mostly are not now. For
what is true today, read *Where things stand* at the top of `CLAUDE.md`,
`docs/suite-consistency-plan.md`, and the tree itself.

Anything from this log that is still a live RULE has been lifted out into
`CLAUDE.md` — into *How to work here* (practice) or *JSFX gotchas* (mechanics).
**Those are the versions to follow.** What remains here is the story around them.

Three habits keep this honest, and all three have failed here before:

- **When you add an entry, update *Where things stand* in `CLAUDE.md` in the same
  commit.** Status lives in exactly one place.
- **When a lesson in an entry is still a live rule, lift it out.** A rule buried
  in a dated entry is a rule nobody reads.
- **Never quote an entry back as evidence without re-checking it.** Two claims
  here hardened into false constraints purely by being restated — the
  `filt_stages` straight-wire theory, and "~4 layers is the CPU ceiling", which
  was arithmetic about oscillators later cited as a measurement about the wash.
  Mark a mechanism **proved / predicted / untested** when you write it down.

## Index by topic

Newest entries are the most likely to still be accurate.

| If you are working on | Read |
|---|---|
| The Morpher's unit controls, appending vs reordering, the N-per-beat reciprocal | 2026-09-06 |
| Polyrhythm Phase, pan modes, Host x as beats-per-cycle | 2026-09-02 |
| The consistency sweep's origin, Womb's tempo sync, the R-rules | 2026-08-30/31 |
| Morpher Layers, filter rolloff and the stock-filter Hz error, restore order | 2026-08-19..22 |
| Host x generally, why it is a multiplier and not a note grid | 2026-08-11 |
| Overtone lift, and why the first version ducked instead of lifting | 2026-07-28 (ear-test results) |
| Capture average, the stale twin in the effects folder | 2026-07-28 (global capture) |
| Passage's slot-handoff click, harmonic phase runaway | 2026-07-27 |
| The muted-layer CPU crackle | 2026-07-10 |
| Veil, and why it is not the Sweeping Filter | 2026-07-09 |
| Stereo Phaser, Dapple, Bubbler — the bubble pair | 2026-07-08/09 |
| Sustain Looper, Harmonic Sculptor, the sample-based pivot | v2.11, 2026-06-26 |
| The render / alt-tab stale-state regression, Park-Miller | 2026-06-15 |
| Expressive drift, and why drift replaces automation envelopes | Polyrhythm v2.10 |
| The Speed Ramp sweep (now called Ramp) | 2026-05-30 |
| Womb v3 — nested drift, the sigh, signed-delta ramp | Womb v3 |
| Whether bloodflow should decouple from the heart | Design point: bloodflow |
| The drift nested-selector sweep across the suite | 2026-06-12 |
| Resonance Bank, and the vowel-synth dead ends before it | Resonance Bank |
| Womb v2 — RSA, bidirectional HRV | Womb v2 |
| Why per-plugin drift replaced the Wobble Modulator | Per-plugin Drift sweep |
| Play/Rest gating across the suite | v2.1 sweep |

---

## 2026-09-06 — the Morpher's two unit controls, and a reciprocal that was still inverted

**What this closes.** The drift/ramp sweep owed the Morpher exactly two controls:
`Drift period unit` and `Ramp time unit`. It is now 14 of 19 plugins complete. The
four still owed the full six — both Polyrhythms, Passage, Womb — are the same four
still owed a reorder, so their six ride along with that one migration.

**Rozaya stopped an append, for the second time.** The first instinct was to add
the two sliders at the end of the list, where adding is mechanically free. That
would have put `Drift period unit` two blocks below the period it measures, which
is the scatter the reorder existed to fix. The same objection is already recorded
in the consistency plan from 2026-09-05: *"Why would that be apending. we just
reordered to fix the acumulation of apends making a goddamn mess."* Making it
twice means the pull toward appending is structural, not a slip — **appending is
always the cheap option at the moment you are choosing, and always the expensive
one afterwards.** The thirteen finished plugins all have their units in the right
place, with migrations; the precedent was already correct and nearly got ignored.

**The decision that needed evidence, not taste.** `Drift period unit` declares
SECONDS, where the rest of the suite declares Cycles. Two independent reasons and
they agree. All 122 instances mean seconds today — measured, not assumed — and a
declared default is a live value, so Cycles at index 0 would have silently
reinterpreted every one of them. And this is the only plugin whose cycle is
OPTIONAL: Cycles counts one Auto-morph pass, Auto-morph defaults to Off, and the
morph rate control is hidden entirely while it is. A fresh instance defaulting to
Cycles would have had a drift that never advanced the first time it was switched
on. The option LIST stays identical to the suite, which is the consistency that
matters; only the default moved, the way Veil's already had.

**A note the units resolved rather than replaced.** The ramp times had been left
in minutes on purpose, with a comment saying so: tying them to Rate Mode meant a
mode change would have to CONVERT the number into beats, and the range could not
hold the answer — a 20-minute ramp at 120 BPM is 2400 beats — so a long ramp would
have been silently clamped. An explicit unit control does not convert anything.
The number stays put and its unit is the one you picked. **The blocker was never
the beats; it was the conversion.**

**Drift period stopped following Rate Mode.** It used to read as seconds, or beats
under sync, with the value rewritten on the flip. That is one control silently
rewriting another that now names its own unit on itself, so it went. Safe on real
data, and checked rather than assumed: every one of the 122 instances is on Rate
Mode = Seconds, so the conversion had never once fired.

### The bug next door, and why it was in scope

`auto_time` handled Rate Modes 0, 1 and 2 explicitly and let **both** host modes
fall into the `Every N beats` formula. Mode 4 is `N per beat`, its reciprocal: at
120 BPM "8 per beat" ran as one morph every 8 beats — 64x too slow — while the
display said the right thing throughout. Identical to the defect fixed in Tremolo
and the Sweeping Filter (`c4c9b31`) and Resonance Bank (`47da263`) the day before.
**This plugin was missed by that sweep, and nothing noticed for a day.**

It is latent — no instance is in either host mode — so by the standing rule it
would have been someone else's job. It was not, because `Cycles` in both new unit
controls counts that period and would have inherited the wrong number. **A latent
bug becomes load-bearing the moment you build on top of it.** Fixed in its own
commit, landing first, so it stays separately hearable.

**Shepard Tone looked like the second case and is correct.** It also has no
`mode == 4` branch. Its chain returns a nominal rate against 60 BPM, where one
beat is one second, so `N per beat` and `Hz` genuinely coincide and the fallback
lands exactly right. **The count said two plugins; reading said one.** A grep for
the shape of a fix finds plugins that do not need it as readily as ones that do.

### What was actually checked

- **Simulation, not reading, for both.** 120 combinations of mode, rate value and
  tempo for `auto_time` — 20 wrong before, 0 after, modes 0-3 bit-identical. Then
  every drift and ramp unit against what its own words say a period should last:
  0 mismatches, and both declared defaults reproduce the old behaviour exactly.
- **The migration verified by NAME, not by its own table** — 122 instances, 38
  projects, 12,200 checks, 0 failures, 0 newly out of range, with values that were
  already out of range counted separately so they could not mask a real one.
- **The verifier was wrong first, and said so.** Matching by name reported three
  controls as vanished; they had been renamed in the same change. An authored
  rename table fixed the checker. Worth recording because the tempting move is to
  loosen the check until it passes, and the failure was real information about
  what the change actually did.
- **Pinned to a commit hash**, not `HEAD~n`, for the reason already in `CLAUDE.md`.

**Nothing here has been heard.** The claim that 122 instances still sound like
themselves rests on the verifier. Opening one finished project and hearing it be
itself is the whole test.

---

## Archived 2026-09-06 — CLAUDE.md's status section, verbatim

**Why this is here.** `CLAUDE.md`'s *Where things stand* had grown to 566 lines,
44%% of the whole file, and its top three bullets were marked *(superseded)*. A
section whose only job is to describe NOW had become a diary. Rozaya, on what
that costs: *"Claude.md being bloated was what literally had me breaking down
crying out of pure frustration"* — and the cost is not the reading, it is that a
session cannot hold a 1,300-line brief and so contradicts itself, which is the
thing Rozaya then has to catch.

Moved here rather than deleted, so nothing is lost and nothing has to be
re-derived. **Some of it duplicates entries already below**, because it was
written to both places on the same day; where they disagree, the dated entry
below is the one written closer to the event. **None of it is current** — read
`CLAUDE.md`'s replacement section for that.

## Where things stand

**Everything under this heading goes stale. Update it at the end of a session,
in the same commit as any entry you add to `docs/session-log.md`** — that log is
append-only history; this is the only part of the repo that claims to describe
*now*.

*Checked against the tree 2026-09-06.*

- **DRIFT/RAMP SWEEP: THIRTEEN OF NINETEEN COMPLETE. Breath Gen landed
  2026-09-06** — 4 instances across 3 projects (one of them a TEMPLATE, in
  `E:/reaper/templates`, which earlier scans of `E:/reaper` did pick up but which
  is easy to forget exists). Verified with the others: 6 instances, 293 checks,
  126 name-decoded comparisons, PASS.

  **STILL OWED: Polyrhythm v3 (8 instances), Womb (9), Passage (48), Polyrhythm
  v1 (84), and the Morpher's two unit controls (122).**

  **A RANGE VIOLATION IS ONLY EVIDENCE IF THE MIGRATION CAUSED IT.**
  `breathscapes.RPP` stores Top pause and Bottom pause at 8 against a 0-5
  control, and REAPER silently clamps them to 5. That is PRE-EXISTING — sliders
  1-16 are byte-identical before and after, proven — and reporting it as a
  migration fault buries the real signal. The verifier now separates "was already
  out of range" from "is out of range now", and only the second is a failure.

  **PIN A VERIFIER TO A COMMIT HASH, NEVER TO `HEAD~n`.** A relative revision
  goes stale the moment anything else is committed, and the check then compares a
  new layout against ITSELF and reports catastrophic-looking shifts that are pure
  fiction. It happened twice in one afternoon. There is a slider-count guard for
  it now, but the guard is the backstop, not the fix.

- **(superseded) DRIFT/RAMP SWEEP: TWELVE OF NINETEEN PLUGINS NOW COMPLETE.** Added
  2026-09-06: Rhythm Track, Shepard Scale, Shepard Tone (no migration -- zero
  saved instances), then **Heartbeat and Sweep Dwell** (one instance each,
  migrated and verified). **Resonance Bank's `Drift period mode` also got the
  R20/R21 rename** -- `Host x` -> `Every N beats`, plus `N per beat` -- which cost
  no migration at all.

  **STILL OWED THE FULL FOUR, and this list is CORRECTED:** Breath Gen (4
  instances), Polyrhythm v3 (8), Womb (9), Passage (48), Polyrhythm v1 (84).
  **The Morpher owes its two UNIT controls only** -- it already has both
  play/rest pairs. That is six plugins, not the nine an earlier count claimed.

  **RESONANCE BANK IS NOT MISSING A CONTROL, AND A NAME-MATCHING SWEEP WILL SAY
  IT IS.** Everywhere else a drift period is a COUNT of cycles with a unit beside
  it; there it is a RATE (`Drift period mode`), because each band drifts
  independently and there is no single cycle to count. That is a real difference
  in meaning, it is now stated in the source, and converting it would move stored
  values in a live project. **Leave it.**

  **A held-back job turned out to be free, so re-check the reason before
  believing it.** The plan recorded Resonance Bank's mode as needing a
  version-gated blob migration because its value lives in a serialized per-band
  bank. True of REORDERING the enum; false of renaming one entry and appending
  another, which moves no index at all.

  **AND CHECK THE @serialize STREAM, NOT JUST THE MAGIC.** Heartbeat's blob magic
  was bumped while the four new banks were never actually written to or read from
  the stream, so its play/rest settings would not have survived a save. Caught
  only by grepping all five finished plugins for the same line and finding one
  with a zero. **After adding a bank, assert it appears in BOTH the file_mem list
  and the duplicate-fix block, in every plugin, not just the one in front of you.**

- **(superseded, kept for the reasoning) Rhythm Track, Shepard Scale and Shepard
  Tone completed 2026-09-06, with NO migration.** All three had **zero saved
  instances** -- measured, not assumed -- so the six missing controls went into
  their canonical positions instead of being appended, and no project was
  touched. 28 -> 34, 64 -> 70, 75 -> 81 sliders. Defaults reproduce the old
  behaviour exactly by construction. Installed, **not heard**.

  **Ten plugins now complete** (Veil, Tremolo, Morpher*, Phaser, Bubbler, Dapple,
  Resonance Bank*, Sweeping Filter, Melody, + these three = twelve, with * owing
  a unit each). **Still owed the full six: both Polyrhythms, Passage, Womb,
  Heartbeat, Breath Gen, Sweep Dwell.**

  **The order to do the rest in, by risk:** Heartbeat, Sweep Dwell and Resonance
  Bank have ONE saved instance each; Breath Gen has 4, Polyrhythm v3 has 8, Womb
  has 9; then Passage (48 across 10 projects), Polyrhythm v1 (84 across 17) and
  the Morpher (122 across 38). **Re-measure before each -- the counts move.**

  **Read a period's LABEL against its code before choosing the default unit.**
  Rhythm Track's period said "beats" and meant the METRONOME's beats, which are
  its own cycles -- so `Cycles` was both canonical and behaviour-preserving, and
  `Beats` (the host) was genuinely new. Trusting the label would have inverted it.

- **`N per beat` WAS BROKEN IN TREMOLO AND THE SWEEPING FILTER -- IT RAN AT THE
  RECIPROCAL. Fixed 2026-09-06, no project affected, NOT HEARD.** `N per beat` = 8
  gave 0.125 cycles per beat instead of 8. Their rate chain ends
  `rate_mode == 2 ? (x) : (1/x)`, so mode 4 fell into the `Every N beats` default
  branch. Both Polyrhythms end `rmode == 3 ? (1/x) : (x)` and were right --
  **that difference in chain ORDER is the whole bug**, and it is invisible unless
  you ask what mode 4 lands on. Three further leaks in the same two plugins, all
  fixed: `rate_pos_lock` gated `== 3` (mode 4 followed the tempo without locking
  to the grid), the Speed Ramp rate conversion likewise, and the Morpher's `tr_k`
  treating durations as beats only in mode 3. `rate_drift_hz` was checked and is
  correct as-is.

  **THE LESSON IS ABOUT VERIFICATION, NOT GATES.** I checked R21 by reading every
  gate and asking whether it should widen, and got every gate I looked at right.
  **I never asked what mode 4 actually DID.** **When you add a mode, option or
  branch to N plugins, SIMULATE ITS OUTPUT IN EACH ONE** -- the same check that
  caught seven pan modes all returning `[-1,1,-1,1]`. Reading confirms the
  wiring; only numbers confirm the behaviour. And **"nothing broke" is not
  evidence that a latent feature works** -- nothing broke here only because
  nothing was stored on the new mode yet.

- **A REAL BUG WAS FOUND BY EAR IN THE START DELAY, 2026-09-06, and fixed. Not
  yet heard.** Melody's sequencer waits for its config to settle before the first
  note; the Start delay counter did not, so a delayed instance burned part of its
  delay during that pause and came in early by ~21 ms — a fraction of a beat,
  from the first note, surviving play/stop because the pause recurs. Both clocks
  now start on the same line. **Any saved project with a Start delay now starts
  that instance a few milliseconds later.**

  **The lesson is about the QUESTION, not the listening.** Twice I checked the
  suspected path's arithmetic and correctly reported it consistent — every
  quantity really did count beats properly. The defect was not *how much* was
  counted but *when counting began*. **When repeated checks of a suspect come
  back clean and the symptom is still real, stop re-checking the magnitude and
  check the ORIGIN.** Also: I had the right suspect early, dropped it on a
  misreading of Rozaya's words, and spent a round elsewhere — when a report
  contradicts a lead, re-read the report before abandoning the lead.

  **And the one-slider test beat three rounds of source reading.** Start delay to
  0 removed the symptom; 8 restored it exactly. Reach for a discriminating test
  sooner than I did.

  **EAR-TESTED ✓ 2026-09-06** — *"it's now done, and out of there."*

  **THE SAME BUG WAS IN FULL FEATURE TREMOLO, and Rozaya found it by asking, not
  me by checking.** *"does tremolo, or any other plugin, have that?"* It did.
  Fixed identically, installed, and it changes no saved project — 11 Tremolo
  instances in the library and none has a Start delay set.

  **AUDIT RESULT, so it is not re-run blindly: only those two plugins can have
  it.** The bug needs TWO clocks — a delay counter AND a gate the engine waits
  for. Nineteen plugins have a Start delay; **only Melody and Tremolo have a
  settling gate** (`cfg_stable` / `CFG_HOLD_BLOCKS`). The other seventeen have
  nothing for the delay to get out of step with.

  **A BUG IS A FEATURE'S TWIN. PROPAGATE THE FIX THE WAY A FEATURE IS
  PROPAGATED.** *"A feature goes everywhere its parent already is"* applies to
  defects too: a mechanism that is wrong in one plugin is wrong in every plugin
  built from the same parts. **After fixing anything, grep the suite for the
  same shape before saying it is done** -- and say plainly which plugins were
  checked and cleared, not just which were fixed.

- **MELODY IS CONVERTED, AND THE SUITE NO LONGER HAS A PLUGIN WITH ITS OWN SYNC
  MECHANISM. Built, migrated, installed 2026-09-06. NOT HEARD.**
  Melody was the last plugin on the R11 shape — a `Sync to host` switch, a
  `Host sync target` selector and a free `Every N beats` slider. All three
  retired; the rate block is now the suite's two controls, and the pan has its
  own rate mode for the first time. **82 sliders → 86**, 73 instances across 7
  projects migrated, **11,865 checks / 5,706 name-decoded comparisons, PASS.**

  **It also closed Melody's drift/ramp gap in the SAME pass**, which is the part
  worth carrying forward. The authored plan covered the rate block only; Melody
  was also missing all six Drift and Ramp controls. Building just the plan would
  have migrated the same 73 instances twice. **Before writing any migration, ask
  whether the layout doc covers everything the plan still owes that plugin** —
  here it did not, and the check took two minutes.

  **Drift and Ramp are now COMPLETE in nine plugins** — Veil, Tremolo, Morpher,
  Phaser, Bubbler, Dapple, Resonance Bank, Sweeping Filter, Melody. The Morpher
  still owes its two unit controls. Nine plugins owe the full six.

  **A latent direction bug was found and fixed on the way**, the same one the
  Polyrhythms had on 09-04: `rate_mode == 1` decided whether a positive drift
  speeds up or slows down, which is wrong once `Every N beats` exists, because
  more beats is a longer cycle. Widened to `== 1 || == 3` in both the drift and
  ramp paths and simulated. No project was affected — nothing in the library
  drifts. **This is an EXACT gate, not a `>= 3` one: the two host modes fall on
  opposite sides of it.**

  **Still owed a reorder:** Polyrhythm v1 → v3, Passage, Womb, and the
  zero-project plugins. Melody owes nothing further.

- **Branch `feature/melody-reorder`, 107 commits ahead of `master`, PUSHED
  through 2026-09-05, unmerged.** `master` is in sync with `origin/master`. The
  branch is on GitHub, so nothing lives only on the one drive. **This number goes
  stale every session — re-run `git rev-list --count master..HEAD` rather than
  believing it.** It said 65 while the truth was 107.

  **DO NOT PROPOSE MERGING OR TAGGING.** Rozaya, 2026-09-05, asked directly:
  *"I am not tagging that. This is not done. And with the plan in flight, the
  branch isn't done either. we can put it on the remote, but I ain't calling
  this a release."* Pushing is right and welcome; a tag is a distribution
  artefact and the sweep is mid-flight. This is the plan's own *No releases
  until the sweep is finished* rule, and I offered a tag anyway — which is how a
  written rule gets broken, by someone reaching for the reassuring cheap win.

- **The Phaser reorder is LANDED, and it is the suite's first Phase 2 change.**
  `src/stereo-phaser.jsfx` and the effects folder now MATCH — that half-landed
  state is closed. Its rate triple (Rate / Rate Mode / Host ratio) is contiguous
  at 1, 2, 3. `E:/reaper/finished/strangeness.RPP` **is the migrated file**; the
  pre-reorder original and the old plugin build are both in
  **`E:/reaper/finished/backups/`** — `strangeness.PRE-PHASER-REORDER.RPP` and
  `stereo-phaser.PRE-REORDER-20260904.jsfx`. **That folder is where backups go**
  (Rozaya, 2026-09-04); it already held 44 of them, so it is an existing
  convention, not a new one. Note the plugin build lives there too rather than
  anywhere under the REAPER resource folder — a renamed twin left in
  `Effects/glasswings/` is the stale-twin trap and would show as a second
  Phaser forever. **Verified by decoding, NOT ear-tested**: 27 controls by
  name old-vs-new across 3 instances, 0 mismatches; 21 stored values in range
  after promotion; 192 lines unchanged. Nobody has played it since the swap.
  If it is ever wrong, put both backups back.
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
  snapshot at `backups/snapshots/_pre-melody-layout-20260902-1503` — and never played. Now both.
- **EAR-TESTED 2026-09-04 ✓ — Veil's rebuilt layout and the Ramp in beats.**
  *"Slider layout? Excellent. Ramp stuff? Works."* So the 22-slider reorder
  reads correctly, and `Ramp time unit` / the beat-counted staircase do what
  they say. **The steeper slopes are confirmed too** — *"rolloff works"* —
  which closes the last item outstanding from the August rolloff overhaul.
- **A FEATURE GOES EVERYWHERE ITS PARENT ALREADY IS. No triage.** Rozaya,
  2026-09-04, overruling exactly the kind of note this file is full of:
  *"Anything that has Ramp should have all the controls that go with Ramp. End
  of fucking story."* If a plugin has Ramp it gets every Ramp control; if it
  has Drift it gets every Drift control. **Do not decide on my own hearing --
  which I do not have -- that some plugin will not benefit and skip it.**
  Consistency is the point: a thing learned on one plugin has to be true of all
  of them, because Rozaya may not have me around to explain the exceptions.
  What this replaced, and why it is worth naming: a bullet that took Rozaya's
  real observation (*"filters are hard to hear a semi-beat pause on"* -- still
  true, still theirs) and grew a Claude-authored conclusion onto it, that
  propagation should be *aimed* at parameters with an attack. Then I quoted
  that conclusion back to Rozaya as though it were their guidance.
  **Everything in these docs that is not inside quote marks is Claude-to-Claude
  and may simply be wrong. Never hand it back to Rozaya as their own view.**
- **EAR-TESTED 2026-09-04 ✓ — Drift play/rest on Full Feature Tremolo.**
  *"It's definitely doing something... it goes real slow, then speeds up...
  it's really hard to tell exactly what it'll do next, which is the point."*
  Rozaya's causal read was right: with `play 1.75` it freezes at the trough,
  which with `Drift down 1.5` on a 2 Hz rate parks it at 0.5 Hz.
- **And the park point ROTATES — that is the feature, not an accident.** Each
  freeze lands further round the wave than the last, so `play 1.75` cycles
  through four positions before repeating and only ONE is dramatic; `1.2`
  gives five with two partial parks at different depths. Simulated, not
  reasoned. **So an awkward fraction beats a tidy one**, a whole number parks
  at neutral every time and is nearly inaudible, and setting only `down`
  wastes half the holds (every park on the positive half lands at no-change).
  Written up on both plugin pages.
- **EAR-TESTED 2026-09-04 ✓ — the Host x beats-per-cycle conversion, on the
  migrated Sweeping Filter instances.** Rozaya played them and the sweeps run at
  the speed they remember. **This closes what was the largest untested block in
  the suite** — the R13-revised conversion across thirteen plugins, where a
  stored multiplier was flipped to its reciprocal.

  **Which instances that actually covers, decoded from the project files rather
  than from this note.** Ten instances were on Host x. **Four of them — every
  Tremolo, in `simple-sequence` and `simple-sequence-check` — were stored at 1,
  and one is its own reciprocal**, so nothing about them changed and they were
  never evidence either way. The six that genuinely moved are all Sweeping
  Filter, in four projects: `bilateral-with-binaurals` (2, at 0.125),
  `as-things-are` (1, at 8), `noisescape-august-18-2026` (2, at 4 and 8) and
  `womb-and-baby-heartbeats-with-bloodflow` (1, at 0.5). Those six are the ones
  the ear-test speaks for.

  The check that needs no ears was already done: at 205 BPM a Rate Value of 4
  must give one cycle every 1.171 s, and it does.

  **Still unheard within Host x, and it is a narrower list than it used to be:**
  Drift and Ramp running *while* in Host x (tests 3 and 4 of
  `docs/host-sync-ear-test.md`), and pan following the project tempo. The mode
  itself is proved — Melody on 2026-08-11, Womb on 08-30/31, and now the
  conversion.
- **A latent bug in the 09-02 conversion, found and fixed 2026-09-04, unheard.**
  Both Polyrhythms added Drift and Ramp amounts to the raw Rate Value. That was
  right while Host x's Rate Value WAS the rate, and wrong the moment it became
  beats per cycle — more beats is slower, so a positive drift ran BACKWARDS.
  Simulated at 120 BPM with a cycle every 2 beats: +10 BPM of drift gave 57.6
  cycles/min instead of 70. Now added in the Hz domain instead. Shepard Tone was
  converted with the correction already in. **No project was affected**: not one
  Polyrhythm instance in the library is on Host x.
- **Heartbeat's rate slider was widened** from `20..200` step 1 to
  `0.001..1000` step 0.001, because beats-per-cycle needs values that range
  could not express. Widening never clamps a stored value; only narrowing does.
- **Still unheard:** the per-cycle pan tick in Melody (note trigger) and the
  filters (LFO wrap) — Polyrhythm's tremolo-wrap tick passed on 09-04 but the
  others advance on a different clock. Plus tests 3-5 of
  `docs/host-sync-ear-test.md`, which are Drift and Ramp under Host x, and pan
  following the tempo. **The beats-per-cycle conversion itself is no longer on
  this list** — it was heard on 09-04, see above.
- **THE DRIFT/RAMP GAP IS THE SUITE'S BIGGEST REMAINING INCONSISTENCY, and four
  plugins were fixed 2026-09-05: Stereo Phaser, Bubbler, Dapple, Resonance
  Bank.** All built, migrated (25 instances / 6 projects, verified by 266
  name-decoded comparisons, PASS) and INSTALLED. **Not heard.**

  **The measurement, and it is worse than it sounds:** 13 plugins still lack
  drift play/rest, 13 lack ramp play/rest, 14 lack each of the two beat-counting
  unit controls. **Only Veil, the Morpher and the Phaser have a complete set.**
  The remaining eleven are Phase 2 work — their missing controls belong INSIDE
  existing blocks, so they need a renumber, not an append.

  **The unlock worth reusing**, Rozaya 2026-09-05: *"I'm not using these until
  they're done, therefore no projects should be saved with our changes, therefore
  we can aford to be aggressive."* Restructure freely, install nothing, migrate
  once at the end. That is the one-migration rule achieved by NOT INSTALLING, and
  it is much cheaper than migrating at every step. **It holds only while the
  projects stay closed** — a reordered build plus an opened project equals a
  scrambled save.

- **EAR-TESTED 2026-09-05 ✓✓✓ — R21, and by the strongest test there is: it got
  USED.** Rozaya: *"it worked. it worked so well I made and saved another project
  despite myself."* `N per beat` was not merely confirmed correct, it was reached
  for and built with. **That is the actual goal of this suite** — not that the
  plugins are right, but that they get opened.

  **AND IT CLOSES THE AGGRESSIVE-RESTRUCTURING WINDOW.** This morning's unlock
  was Rozaya's own condition: *"I'm not using these until they're done, therefore
  no projects should be saved with our changes, therefore we can aford to be
  aggressive."* A project has now been saved on today's builds, so that premise
  is spent. **Assume saved work exists from here, and migrate accordingly.**
  Re-run the file scan before any layout change rather than trusting a list from
  earlier in the session.

- **R21 — THE RATE MODE NOW HAS FIVE ENTRIES, BUILT AND INSTALLED IN ALL TWELVE
  PLUGINS 2026-09-05.** `BPM / Seconds / Hz / Every N beats / N per beat`.
  `Host x` was RENAMED to `Every N beats` — index 3 did not move, so the 10
  instances stored on it are untouched — and `N per beat` appends at index 4.
  **No migration. Not heard.**

  **Why:** the retired pickers offered both directions in words (*"every 8 beats
  … 8 per beat"*), and retiring them kept the slow half only, so eight cycles per
  beat became `0.125`. Rozaya hit it: *"Rate value should not have to be set to
  0.5 to get 8 bubbles every beat."* The two directions are reciprocals, so
  neither is right alone — the mode picks which end of your music is
  arithmetic-free.

  **The trick that made it free, and it generalises:** `N per beat` computes
  EXACTLY like Hz — a nominal cycles-per-second against 60 BPM — and only differs
  in being multiplied by `host_scale`. So in the three plugins with a shared
  `rate_to_hz()` the function needed NO change at all; mode 4 falls through to
  the Hz branch and the only edit was widening `host_scale = rate_mode == 3` to
  `>= 3`.

  **The gates that must NOT be widened**, and they were checked one at a time:
  the conversion chains themselves (which mode am I) stay exact, while every gate
  meaning "am I host-synced" becomes `>= 3`. Both Polyrhythms keep one exact
  `== 3` — the landing block, which stamps Rate Value to 4 on entering beats mode
  and now stamps 1 on entering per-beat mode, because the two units are
  reciprocal and carrying the number across would change the speed sixteenfold.

  **The Morpher was the odd one out:** it CONVERTS its value on a mode switch
  rather than branching, so it needed both directions of its conversion table
  extended, and its transport durations read as beats in EITHER host mode
  (a start delay of "per beat" is not a length).

- **EAR-TESTED 2026-09-05 ✓✓ — THE TWO BIG REORDERS, ON FINISHED WORK.** Rozaya
  played every project on the safety-check list and they came back correct:
  **`the-sound-of-a-drain`** (five Sweeping Filters AND five Bubblers, both
  migrated), **`bilateral-with-binaurals`** (two filters, including the live
  30-minute ramp), and **`melodic` / `upswing`** (Tremolo). *"we listened to
  those ones... I did listen to all of the ones you pointed at."*

  **What that clears, and it is the largest block in the sweep:**
  - The **Sweeping Filter** reorder — 20 instances, 11 projects, 45 sliders
    renumbered, two controls deleted, Linked Sweep collapsed to one number.
  - The **Tremolo** reorder — 11 instances, 8 projects, same shape.
  - **Bubbler's** reorder, its deleted Host ratio, and its transport block not
    disturbing anything at rest defaults.
  - **The Ramp time unit's moved default.** `bilateral-with-binaurals`' two
    ramps are on the default and still run 30 MINUTES. That is the near-miss
    proving itself: had the default stayed at index 0 with Cycles there, this
    project would have come back audibly wrong.

  **What it does NOT clear.** Those projects were played, not reconfigured, and
  every new control defaults to off — so **Drift and Ramp actually doing
  something is still unheard** on all four plugins that gained them, as are the
  transport gates, the drift period units, and Resonance Bank and Stereo Phaser
  entirely (`wind` and `strangeness` were not on the list).

- **EAR-TESTED 2026-09-05 ✓ — Dapple's rate change landing immediately, and its
  Seconds rate mode.** *"There we go, works perfectly."* Set to Seconds with a
  value of 6, Rozaya heard one drip every six seconds — which confirms the R20
  canonical rate modes are right on a converted plugin — then changed the value
  to 1 mid-play and heard it respond at once rather than finishing the old
  six-second gap.

  **That clears the count-up scheduling change** in Bubbler and Dapple: the
  jitter is rolled as a proportion of a gap re-read every sample, instead of an
  absolute length frozen when the previous bubble was born. **It does NOT clear**
  the rest of today's work — the two reorders, the drift/ramp blocks, the
  transport gates and the unit changes are all still unheard.

  **How it was found is the reusable part.** The observation located the symptom
  (*"you of course have to wait for 6 seconds to elaps"*) and the QUESTION
  located the cause (*"Why does womb and friends not do the same thing?"*).
  Heartbeat and Womb count UP to a target recomputed every sample; these two
  counted DOWN from a committed length. Asking why a sibling behaves differently
  is a cheap and unusually direct way into a structural difference.

- **PHASE 2 REORDERS LANDED AND INSTALLED: Morpher, Melody, Stereo Phaser,
  Bubbler, Dapple, Resonance Bank, SWEEPING FILTER and TREMOLO.** The last two on
  2026-09-05 — 31 instances across 19 projects between them, verified by 725 and
  348 name-decoded comparisons, both PASS, eleven finished projects touched.
  **None of it heard.**

  **Still owed a reorder:** Polyrhythm v1 → v3 (its layout is NOT authored, which
  is what blocks it), Passage (blocked on what it is FOR), Womb, ~~Melody's second
  pass for its drift/ramp controls~~ (DONE 2026-09-06), and the zero-project
  plugins.

  ~~**Drift and Ramp are now COMPLETE in eight plugins**~~ — **NINE as of
  2026-09-06**; see the Melody entry at the top of this section, which is the
  current count. Struck rather than edited because a number in a dated bullet
  goes stale by design, and the top of the section is where status lives.

- **PITCH IS THE NEXT BIG INCONSISTENCY AND IT IS DELIBERATELY NOT STARTED.**
  Raised and measured 2026-09-05: the suite states a pitch **seven different
  ways** — note-with-octave, note-without, raw semitones, hertz, cents, percent,
  and semitones-as-a-spread. Bubbler and Dapple disagree with each other on the
  same control. Full table and the three worst cases are in
  `docs/suite-consistency-plan.md` under *pitch needs its own rule*.

  **Do not start it opportunistically.** Unlike the rate sweep there is NO free
  window: every pitch value is stored in real projects and IS the sound. Write
  the rule, settle it with Rozaya, then build — the R20 way, which is what
  finally worked after five sessions each guessed differently.

- **THE RAMP TIME UNIT IS `{Cycles, Seconds, Minutes, Beats}` — AND ITS DECLARED
  DEFAULT IS MINUTES, NOT INDEX 0.** Settled 2026-09-05. It was `{Minutes, Beats}`
  everywhere, so a thirty-second ramp had to be entered as *0.5 minutes* — a
  conversion, which is the exact barrier this suite exists to remove — and a ramp
  counted in cycles was unreachable though Drift could do it. Veil and Resonance
  Bank get `{Seconds, Minutes, Beats}`: no rate, so no cycles to count.

  **The near-miss, and it is the reusable part.** I checked that the unit was
  unset on all 59 instances and reported "nothing stored", which sounded like
  "nobody uses Ramp". Rozaya: *"Which plugin has it? because we do have projects
  that use ramp lol what."* They were right — `bilateral-with-binaurals` has TWO
  Sweeping Filters ramping by −1 over **30 minutes**, engaged. Putting Cycles at
  index 0 while those instances sit on the default would have turned a
  thirty-minute fade into a two-second one. **A control being unset is not the
  same as a feature being unused, and the default is a live value for every
  instance that never touched it.** The fix is to move the declared default to
  wherever the old meaning landed — the same trick the Phaser's rate mode uses.

  **Caveat that remains:** per-target ramp settings live in the `@serialize`
  blob, so the slider line only shows whichever target was selected at save.
  There may be more configured ramps than can be counted from outside REAPER.

- **THE DRIFT PERIOD UNIT IS `{Cycles, Seconds, Beats}`, and Cycles is the
  default — everywhere the plugin HAS a rate to count cycles of.** Veil is the
  one exception and it is a principled one: it has no rate, so there are no
  cycles to offer. Settled 2026-09-05 after Rozaya caught the inconsistency:
  *"I'd imagine both bubbler and daple have cycles, sort of, in the form of
  bubbles. Don't they?"* They do — their own transport block already counted in
  cycles, meaning one mean bubble interval, while the drift period I had just
  given them counted in seconds. Same plugin, two time bases, no reason.

  **It was free because nothing was stored:** all 47 instances across the four
  plugins had NOTHING saved for that control, so every one took the declared
  default. Checked before changing it, not assumed. **The period is referenced
  against the PRE-drift rate**, so drifting the rate cannot modulate its own
  drift period.

- **PART 2 — THE CANONICAL READING ORDER — WAS APPROVED BY ROZAYA 2026-09-05 AND
  IS NOW WRITTEN DOWN.** Every per-plugin layout is measured against it, and for
  five days it described a block structure that had been thrown out on 08-31
  with no replacement written. That single gap is what made the sweep feel
  unnavigable to Rozaya — *"I'm very lost, and I don't think I planned this out
  well at all"* — and it was five days of nobody writing a paragraph, not a hard
  problem. The order, so it is in this file too:

  **what the plugin IS → its rate (value, then mode) → the shape of its movement
  → stereo and pan → output level → transport → drift → ramp.**

  Inside that: everything belonging to a layer lives with that layer; a modifier
  is numbered immediately after the thing it modifies; a second rate carries its
  own complete R20 pair; global output sits last before transport. Drift and
  Ramp are last because their target lists reach across every other group.

  It was not designed top-down — it is what the Sweeping Filter and Tremolo
  layouts independently came out as when authored by hand, then described and
  approved. **The three drafted layouts can now be reviewed against something
  real.**

- **R20 — THE RATE BLOCK. SETTLED 2026-09-04, and the enum order is BUILT AND
  INSTALLED in SEVEN plugins as of 2026-09-05: Rhythm Track, Shepard Scale,
  Heartbeat, Stereo Phaser, Sweep Dwell, Bubbler, Dapple.**

  **The measurement that found them had a blind spot, so re-run it properly.**
  A grep for enums containing `BPM`, `Hz` or `Seconds` misses every list that
  names its unit its own way — `{Own rate, Host x}`, `{Own durations, Host x}`.
  The correct scan is
  `grep -nHE "^slider[0-9]+:.*\{[^}]*Host x[^}]*\}" src/*.jsfx | grep -v "{BPM,Seconds,Hz,Host x}"`,
  which lists exactly what is left. **But that scan is not the whole remainder
  either**, because a list with no `Host x` in it at all does not match: the
  **Tremolo and Sweeping Filter pan units are `{Hz, Seconds, BPM}`, backwards
  AND missing Host x**, and Melody's Rate mode is `{BPM, Seconds, Hz}`. Those
  three are held for their own reorder passes.

  **What the scan does show, all three deliberately held:** Resonance Bank's
  `Drift period mode` (its value lives in a SERIALIZED per-band bank, so it
  needs a version-gated blob migration, not a token edit), Sweep Dwell's
  `Cycle mode` (`{Own durations, Host x}` — not a unit list at all; "own
  durations" means the four dwell sliders SUM to the cycle, so giving it
  BPM/Seconds/Hz turns them into proportions. Same design question as Passage,
  and it waits for that conversation), and Womb's Rate Mode (converting off the
  dead sync-block shape, its own pass). Verified by simulation, lint clean, **not heard.** Only
  `surges.RPP` needed a project edit (one token, backed up, verified by decoding
  against the new enum). **Resonance Bank is deliberately NOT done** — its drift
  period mode lives in a serialized bank and needs a version-gated blob
  migration, not a token edit. **Melody, Womb, Tremolo and the Sweeping Filter
  are held for their own reorder passes so each gets ONE migration.** The rule
  itself is in `docs/suite-consistency-plan.md`; the rule is written down in
  `docs/suite-consistency-plan.md` and summarised under *Terminology* below.
  **It goes before the Sweeping Filter reorder**, because the reorder moves
  controls and this decides what they say — doing the layout first means
  touching that plugin twice.

  **Measured 2026-09-04, so the size is known:** the mode enum has FIVE different
  shapes across the suite, and **every pan unit runs backwards** relative to the
  Rate Mode sitting above it in the same plugin. Canonicalising costs **36
  stored instances**, all uniform: 32 pan units (all on `Hz`, index 0 → 2), 3
  Stereo Phasers (on the DEFAULT, whose index 0 is `Own Hz` — they need `2`
  written explicitly or they silently become BPM), and 1 Womb on Host x
  (1 → 3). Melody, Heartbeat, Rhythm Track and Shepard Scale need nothing.
  Then Melody and Womb convert off the dead sync-block shape — Melody's 27
  synced instances move their beats number into `Rate value`, and it comes out
  **two controls shorter**.

  **Rozaya, 2026-09-04, on why this keeps going wrong:** *"I've had five
  different Claude sessions try and fuck this aspect up, and I don't know enough
  JSFX or syntax or anything like that to try and fix it."* The plan's own text
  was the tripping hazard — it read as authoritative and said the opposite. Both
  offending paragraphs are now struck through in place rather than deleted, so a
  session that half-remembers them finds the correction instead of the claim.

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

---


**This section is append-only and is NOT kept current.** Each entry describes
what was true on its own date. It is here for the *reasoning* — why a decision
went the way it did, what was tried and rejected, what a bug's symptom actually
sounded like — none of which goes stale. **The facts in it do.** For what is
true now, read *Where things stand* at the top of this file, the consistency
plan, and the tree itself.

Two habits keep this honest, and both have failed here before:

- **When you add an entry, update *Where things stand* in the same commit.** The
  status heading exists so that status lives in exactly one place.
- **Never quote an entry back as evidence without re-checking it.** Two claims
  in this log hardened into constraints purely by being restated — the
  `filt_stages` straight-wire theory, and the "~4 layers is the CPU ceiling"
  figure, which was arithmetic about oscillators that was later cited as a
  measurement about the wash. Mark a mechanism **proved / predicted / untested**
  when you write it down, because an unmarked one gets read as proved by the
  next person, including by a later you.

- **2026-09-06 — Drift/Ramp sweep continues: Heartbeat and Sweep Dwell completed, Resonance Bank renamed, and two of my own faults caught by cross-checking.**

  Heartbeat and Sweep Dwell each had ONE saved instance, so both got a real
  migration: 2 instances, 110 checks, 48 name-decoded comparisons against the
  snapshot, PASS. Both also had their ramp blocks put in order -- Heartbeat's
  Rate Mode was thirty-three sliders from its rate value, and Sweep Dwell's ramp
  block was scattered with its start delay stranded eight places away.

  **The miss worth recording: Heartbeat's blob magic was bumped while the four
  new banks were never written to the stream.** Its play/rest settings would have
  vanished on save. Nothing detected this except grepping all five finished
  plugins for the same line and noticing one returned zero. **After adding a bank,
  assert it appears in BOTH the file_mem list and the duplicate-fix block, in
  every plugin -- a magic bump proves intent, not format.**

  **Two tooling faults, both found by using the tools rather than reading them:**
  the migration re-read the snapshot once per plugin and wrote the live file each
  time, so a project holding two migrated plugins would have silently lost the
  first's edits; and the verifier was pointed one commit short and compared a new
  layout against ITSELF, reporting twelve catastrophic-looking shifts that were
  nothing of the kind. It now refuses when old and new have the same slider count.

  **A measurement I got wrong, and the shape of the error is the lesson.** My gap
  table matched the exact string "Drift period unit", so it reported Resonance
  Bank as missing one. It is not: it has "Drift period mode", which is a
  genuinely different control -- a RATE rather than a count, because each band
  drifts independently and there is no single cycle to count. **A name-matching
  sweep cannot tell a missing control from a differently-shaped one.**

  **And a job held back for a reason that did not survive checking.** Resonance
  Bank's mode was recorded as needing a version-gated blob migration because its
  value lives in a serialized per-band bank. That is true of REORDERING the enum
  and false of renaming one entry and appending another: indices 0-3 keep their
  meanings, nothing moves, and the R20/R21 rename was free.

- **2026-09-06 — the Drift/Ramp sweep starts: Rhythm Track, Shepard Scale and Shepard Tone completed, no migration needed.**

  Ten plugins were missing all six of the Drift and Ramp controls the other
  seven have. **These three have ZERO saved instances in the whole library** --
  measured before touching anything -- so the sliders went into their canonical
  positions rather than being appended, and no `.RPP` was touched at all.

  Each gained `Drift period unit`, `Drift play for`, `Drift rest for`,
  `Ramp time unit`, `Ramp play for`, `Ramp rest for`, plus the shared `pr_frozen`
  gate and four per-target banks. Slider counts 28 -> 34, 64 -> 70, 75 -> 81.

  **Defaults reproduce the old behaviour exactly**, and that was designed rather
  than hoped: the drift period unit's default branch IS the old expression
  verbatim, and the ramp time unit's default of Minutes gives the `* 60` the code
  had hardcoded. So the only way to change the sound is to move a new control.

  **Rhythm Track needed a judgement the others did not.** Its drift period was
  labelled "beats", but they are the METRONOME's beats, not the project's -- and
  one metronome beat is one of its cycles. So `Cycles` is both the canonical
  default and the existing behaviour, and `Beats` is genuinely new: it counts the
  host, which is a different clock whenever the two disagree. Reading the label
  alone would have got this backwards.

  **Shepard Scale crossed 64 sliders (64 -> 70).** Its `.RPP` value lines will now
  carry the `""` marker at index 64, so any future migration must go through
  `tools/rpp_sliders.py`. Nothing to do today -- it has no projects -- but it is
  the kind of thing that is invisible until it bites.

  Each blob magic bumped, with the READ accepting both old and new, gated on
  "this blob HAS the field". Lint clean, installed. **Not heard** -- though with
  every new control defaulting to off, nothing can regress.

  Still owed the same six: both Polyrhythms, Passage, Womb, Heartbeat, Breath Gen,
  Sweep Dwell. Resonance Bank owes one, the Morpher two.

- **2026-09-06 — `N per beat` WAS NEVER ACTUALLY BUILT in Tremolo and the Sweeping Filter. It ran at the reciprocal.**

  Rozaya asked to close the one R21 gate left unwidened yesterday. It was not one
  gate.

  **What R21 claimed:** mode 4 computes exactly like Hz -- a nominal rate against
  60 BPM -- differing only by a multiply by `host_scale`, so a shared
  `rate_to_hz()` needed no change because mode 4 falls through to the Hz branch.
  **True for both Polyrhythms:** their chain ends `rmode == 3 ? (1/x) : (x)`.

  **Tremolo and the Sweeping Filter end the other way round** --
  `rate_mode == 2 ? (x) : (1/x)`, with `Every N beats` as the DEFAULT branch -- so
  mode 4 fell into it and ran at the RECIPROCAL. Measured: `N per beat` = 8 gave
  **0.125 cycles per beat instead of 8**, a 64x error, and exactly the arithmetic
  R21 exists to abolish, performed backwards.

  **Three further leaks in the same two plugins**, all the same omission:
  `rate_pos_lock` gated `== 3` (mode 4 followed the tempo without locking to the
  grid); the Speed Ramp rate conversion likewise; and the Morpher's `tr_k`
  treating durations as beats only in mode 3. Where the gate widened, the
  *formula* under it was branched EXACTLY -- widening a sync test is right,
  widening a conversion is not, and the two host modes are reciprocals.
  `rate_drift_hz` was checked and correctly left alone.

  **No project affected: zero saved instances anywhere are on mode 4.**

  **The lesson is about verification, not gates.** I checked R21 by reading every
  gate and asking whether it should widen, and every gate I looked at I got right.
  **I never asked what mode 4 actually DID in each plugin**, and in two of them
  the answer was "the opposite of what it says". A feature switched on everywhere
  is not a feature that WORKS everywhere. **When you add a mode to N plugins,
  simulate its OUTPUT in each one** -- the check that caught seven pan modes
  returning identical arrays. Reading confirms the wiring; only numbers confirm
  the behaviour. And nothing broke on release only because nothing was stored on
  the new mode yet: **"nothing broke" is not evidence that a latent feature
  works.**

- **2026-09-06 — a real bug, found by ear, in the Start delay: two clocks with different starting lines.**

  Rozaya, testing `simple-sequence`: track 10 sat a fraction of a beat out
  against the melody, from the first note, and neither play/stop nor alt-tab
  fixed it. Track 10 is the only instance in that project with a Start delay.

  **Cause.** Melody's sequencer waits for the config to settle before its first
  note (`cfg_ready && slider_ran && cfg_stable >= CFG_HOLD_BLOCKS`). The Start
  delay counter waited for nothing. So a delayed instance burned part of its
  delay inside a pause the undelayed ones were still in, and came in early by the
  length of that pause — two audio blocks, ~21 ms at 512/48 kHz, 0.043 beats at
  120 BPM. Deterministic, and it reappears on every play press because the pause
  does. Fixed by gating the accumulation on the same condition. One line.

  **The diagnosis was Rozaya's, and mine was wrong twice.** They localised it to
  one track, established the offset did not move with tempo, and then settled it
  with a one-slider test: delay 0 removed it, delay 8 restored it exactly. I had
  suspected the Start delay, DROPPED it on a misreading of "the delays work with
  one another", chased the Play/Rest gate instead, and had to be corrected back.

  **The reusable lesson is sharper than "listen to the report".** Twice I checked
  the arithmetic and reported it "consistent on paper", and twice it really was —
  every quantity I checked measured beats correctly. **The paper was right and
  the question was wrong.** I kept asking *is this counting the right amount?*
  when the defect was *when does it start counting?* When repeated checks of a
  suspected path come back clean but the symptom is real, the next move is to
  stop re-checking the magnitude and start checking the ORIGIN.

  **And a one-slider test beat three rounds of reading.** Setting the delay to 0
  isolated the path in seconds, after I had read the delay and placement code
  twice without convicting either. Reach for the discriminating test earlier.

  **EAR-TESTED ✓ the same day** — *"it's now done, and out of there."* So the
  mechanism is confirmed, not predicted.

  **Then Rozaya asked the propagation question — "does tremolo, or any other
  plugin, have that?" — and the answer was yes, one.** The bug needs TWO clocks,
  and only Melody and Tremolo carry a settling gate for an engine to wait on.
  Nineteen plugins have a Start delay; seventeen of them have nothing for the
  delay to get out of step WITH. Tremolo had the identical structure and is fixed
  the same way. It changes no saved project — 11 instances in the library, none
  with a Start delay set.

  **This is the shape of question that should have been asked without prompting.**
  A bug is a feature's twin: if a mechanism is wrong in one plugin it is wrong in
  every plugin built from the same parts, and *"anything that has Ramp should have
  all the controls that go with Ramp"* applies to defects as much as to controls.

- **2026-09-06 — Melody Phase converted to R20/R21, and the last non-standard sync mechanism in the suite is gone. Built, migrated, installed, UNHEARD.**

  Melody was the only plugin still carrying the R11 shape: a `Sync to host`
  switch, a `Host sync target` selector and a free-standing `Every N beats`
  slider. All three are retired. The rate block is now the suite's two controls —
  a value, then a mode of `{BPM, Seconds, Hz, Every N beats, N per beat}` — and
  the pan has its own mode for the first time. **82 sliders → 86.**

  **The scope was widened before anything was built, and that is the reusable
  part.** The authored plan covered the rate block only. Melody was ALSO missing
  all six Drift and Ramp controls the other eight plugins have — period unit,
  ramp time unit, and both play/rest pairs. Building only the rate block would
  have migrated 73 instances and then migrated the same 73 again, which is
  precisely the *five migrations in one day* failure. So the layout document was
  extended first and everything landed in one pass. **The check that catches
  this is cheap: before writing a migration, ask whether the layout doc includes
  everything the plan still owes that plugin.** Here it did not.

  It was also free. All 73 instances had **nothing** stored on Drift or Ramp —
  zero drift amounts, zero engaged ramps, checked rather than assumed — so the
  seven new controls moved no stored value and only needed the renumber that was
  happening anyway.

  **A latent bug found on the way, same shape as the Polyrhythm one from
  2026-09-04.** Both the drift and the ramp rate paths asked `rate_mode == 1` to
  decide whether a positive offset speeds up or slows down. That was right while
  Seconds was the only "time per cycle" unit, and wrong the moment `Every N
  beats` joined it — more beats is a longer cycle, so a positive drift would have
  run BACKWARDS in the new mode. Both gates widened to `== 1 || == 3`, and
  simulated: value 4 with a +1 offset now gives x0.8 in Every N beats and x1.25
  in N per beat. **No project was affected** — nothing in the library drifts.

  **The `>= 3` / `== 3` distinction is the whole of R21 and it was applied one
  gate at a time.** Gates meaning *am I host-synced* widened; conversion chains
  asking *which mode am I* stayed exact. The direction gate above is the sharp
  case: it is exact, and the two host modes fall on OPPOSITE sides of it, so the
  widened form would have been actively wrong there.

  **The blob got a magic bump, 2200000 → 2300000, and it needed one.** The four
  new per-target banks were going to be appended without a bump, the way the sync
  bank had been. That would have landed the retired sync bank's three leftover
  floats in `drift_play_mem[0..2]` on any older blob — a drift play/rest config
  nobody set, restored out of retired data. It happens to be inert, because the
  rest bank stays 0 and the gate needs both above zero. **Inert by luck is not a
  design**, and the luck expires the first time the bank order changes. The read
  accepts all three magics, so no existing Drift or Ramp config resets.

  **Two lines of dead code removed rather than annotated**, which is the opposite
  of the standing rule and deliberate: `last_rate_mode` had one write and zero
  readers (checked case-insensitively, because eel2 folds case), and *this change
  is what orphaned it*. The comment above it described a picker that no longer
  exists. The Polyrhythm precedent leaves inert code alone because deleting it
  buys nothing there; here, leaving it would have left a monument to a retired
  mechanism.

  **Verification, none of it with ears.** Lint clean. The five rate modes
  simulated and their numbers read: `Every N beats` = 4 at 205 BPM gives one
  cycle every 1.1707 s, which is 4 beats exactly; modes 3 and 4 are reciprocals
  at every tempo tested. Migration equivalence proved from first principles —
  every synced instance's old cycle length recomputed against its new one, all
  identical. 73 instances across 7 projects migrated and checked by **11,865
  checks, 5,706 of them name-decoded value comparisons** against the snapshot,
  PASS.

  **The verifier deliberately does not import the migration's table**, because a
  Melody migration passed its own verification on 2026-09-02 while writing twelve
  instances of nonsense. It reads old names from `git show` and new names from
  the tree. Its first run reported 166 failures, all of them its own
  double-counting: four RENAMED controls were being counted as new ones by one
  check while another check already aliased them. Worth recording because the
  fix was to the question, not the data — and because a verifier that declares
  renames explicitly is what stops a rename reading as a deletion plus an
  addition, which is the fingerprint of a mid-list insert.

  **The one judgement call.** Of the 27 synced instances, 26 held tidy beat
  counts and one held `0.333333`. It was rewritten as `3` in `N per beat` — the
  same speed, said so it can be read. The new value is in fact 1 ppm closer to a
  true third of a beat than the stored one was.

  Backups: `E:/reaper/finished/backups/snapshots/_pre-melody-r20-20260906/` and
  `E:/reaper/finished/backups/melody_phase.PRE-R20-20260906.jsfx`.

- **2026-09-05 — EAR-TESTED ✓✓: both big reorders played back correctly on finished work.**

  `the-sound-of-a-drain`, `bilateral-with-binaurals`, `melodic` and `upswing` all
  played and were correct. Between them that is the Sweeping Filter's 20-instance
  reorder, the Tremolo's 11-instance one, Bubbler's, and the Ramp time unit's
  moved default — 31 migrated instances across 19 projects, heard rather than
  only decoded.

  **The migrations were already verified by 725 + 348 name-decoded comparisons.
  This is the half that decoding cannot do**, and the repo's own rule is that
  only "it has been heard" counts as done.

  **The moved default earned its keep here.** `bilateral-with-binaurals`' two
  ramps sit on the Ramp time unit's default and still run 30 minutes. Had the
  default stayed at index 0 when Cycles was put there, this project would have
  come back audibly wrong — a thirty-minute fade in two seconds — and it was
  Rozaya's question that stopped it.

  **Scope, stated because it is easy to over-claim:** the projects were PLAYED,
  not reconfigured, and every newly added control defaults to off. So the
  reorders and migrations are cleared; Drift and Ramp actually moving something,
  the transport gates, the period units, and Resonance Bank and Stereo Phaser as
  wholes are all still unheard.

- **2026-09-05 — EAR-TESTED ✓: Dapple responds to a rate change immediately, and its Seconds mode is right.**

  *"There we go, works perfectly."* Rate mode Seconds, value 6, heard as one drip
  every six seconds; then changed to 1 mid-play and heard it respond at once.

  Clears the count-up scheduling change in Bubbler and Dapple. Does NOT clear the
  two reorders, the drift and ramp blocks, the transport gates or the unit
  changes — all still unheard.

  **The chain is worth keeping.** Rozaya hit the symptom while testing something
  else, described it exactly (*"you of course have to wait for 6 seconds to elaps
  before hearing, in this case, it beginning to do 1 a second"*), and then asked
  the question that found the cause: *"Why does womb and friends not do the same
  thing?"* It turned out to be a structural difference — count up to a live
  target versus count down from a committed one — and once that was named the fix
  was obvious and small. **Asking why a SIBLING behaves differently is a cheap
  route into a structural difference, and it beat my own guess**, which was a
  clamp that would have papered over the symptom without fixing drift and ramp.

- **2026-09-05 (morning) — the Sweeping Filter and the Tremolo both reordered, migrated and installed; Ramp and Drift gain the units they were missing. Nothing heard.**

  **Both filters' siblings done in one window**, the Tremolo second and cheaply
  because the Filter's shape was still loaded. Between them: 31 instances across
  19 projects migrated, verified by 725 and 348 name-decoded comparisons, both
  PASS. Eleven finished projects touched.

  Each lost TWO controls rather than hiding them — the retired `Host ratio`, and
  the Linked Sweep picker. **Linked Sweep collapsed to `Pan sweep every
  (cycles)`**, which is R13's shape applied to the last place a
  multiplier-plus-picker survived. Rozaya on the old one, 2026-09-04: *"I've
  never used it and I've never liked it being the current way BECAUSE of that
  exact thing."* Both pan rate lists were also running BACKWARDS against the Rate
  Mode fifteen and eighteen places above them in the same plugin.

  **The DEADSLIDER trick, worth keeping.** Before deleting a retired control,
  rename every reference to it `DEADSLIDER<n>` in the same pass as the renumber.
  Eight references surfaced in each plugin — two `slider_show` calls, a writer
  block, a tracker — instead of some quietly surviving a grep.

  **Two rules settled by Rozaya's questions, and both were catches:**

  1. *"I'd imagine both bubbler and daple have cycles, sort of, in the form of
     bubbles. Don't they?"* They do — their own transport block already counted
     in cycles while the drift period I had given them the day before counted in
     seconds. Same plugin, two time bases. **The drift period unit is now
     `{Cycles, Seconds, Beats}` wherever the plugin has a rate to count cycles
     of**, Veil excepted because it has none. Free: all 47 instances had that
     control unset.

  2. *"Which plugin has it? because we do have projects that use ramp lol what."*
     **This one prevented a real break.** I had reported "nothing stored" having
     checked only the unit selector, which sounded like nobody used Ramp.
     `bilateral-with-binaurals` has two Sweeping Filters ramping by −1 over
     **30 minutes**, engaged, in finished work. The Ramp time unit gains Seconds
     and Cycles — a thirty-second ramp used to mean typing *0.5 minutes*, which
     is the exact conversion this suite exists to remove — but **the declared
     default had to move to Minutes**, because those two instances sit on the
     default and putting Cycles at index 0 would have turned a thirty-minute fade
     into two seconds.

     **The general rule, now in CLAUDE.md: a control being UNSET is not the same
     as a feature being UNUSED.** The default is a live value for every instance
     that never touched it, so moving what index 0 means rewrites them all.

  **And pitch was raised, measured, and deliberately NOT started.** Seven
  different ways of stating a pitch across the suite; Bubbler and Dapple state
  the same control two ways. Written up as an open question with the reasoning
  for deferring, because unlike the rate sweep there is no free window: every
  pitch value is stored in real projects and IS the sound. Rozaya: *"It's a thing
  that needs exploration... I don't think we should start that tonight."*

- **2026-09-05 (later) — the four plugins that could not drift now can, and the suite's biggest capability gap is closed. Built, migrated, installed, UNHEARD.**

  **Stereo Phaser, Bubbler, Dapple and Resonance Bank** had no Drift and/or no
  Ramp. They were written after the 2026-06 drift sweep and never joined it. All
  four now carry the complete Veil block.

  **The audit that found the real size, and it came from Rozaya's question**
  (*"doesn't resonance bank need the drift play and rest stuff?"*). Yes — and so
  did nearly everything else. Measured across the suite: **13 plugins lack drift
  play/rest, 13 lack ramp play/rest, 14 lack each of the two beat-counting unit
  controls.** Only Veil, the Morpher and now the Phaser have a complete set. The
  rule *"anything that has Ramp should have all the controls that go with Ramp"*
  had been true on paper and false in the files since it was written. **The
  remaining eleven are Phase 2 work**, because their missing controls belong
  INSIDE existing blocks and so need a renumber.

  **"Append it" was wrong and Rozaya caught it.** *"Why would that be apending.
  we just reordered to fix the acumulation of apends making a goddamn mess."*
  Appending is correct only where a plugin has no drift block and few sliders --
  the Phaser, Bubbler and Dapple -- because drift and ramp belong last in the
  canonical order anyway, so append and logical position coincide. That is an
  accident of arithmetic. Resonance Bank is the counter-example: its drift sits
  at 9-14 with Mode/Wet-dry/Output at 15-17, so an appended `Drift play for`
  would have landed at 18, nine places from `Drift shape`.

  **What unlocked doing it properly**, Rozaya: *"I'm not using these until
  they're done, therefore no projects should be saved with our changes,
  therefore we can aford to be aggressive."* So layouts were restructured freely
  and everything moved in ONE migration at the end, rather than a migration per
  step. **That is the one-migration rule achieved by not installing**, and it is
  worth reaching for again.

  **The migration: 25 instances across 6 projects, verified PASS.** 266 value
  comparisons decoded by control NAME, before against after, using the OLD
  plugin sources kept out of the Effects folder and the new ones from `src/`.
  Zero mismatches, zero values outside their declared ranges.
  `tools/drift_ramp_migrate_20260905.py` reads the SNAPSHOT and writes the live
  file, which makes it idempotent by construction -- these plugins' old and new
  layouts overlap in range, so a "has this already been done?" test on the line
  itself would have been guesswork, and guesswork is what ate a line per
  instance on 2026-09-02.

  **Three things the count assertions refused rather than half-doing:** `inp`
  appears five times across three lines in Dapple, not three; `width` appears in
  a COMMENT, which inflated its count until the rewrite was made to skip comment
  text; and the first idempotence gate matched nothing at all because REAPER pads
  every value line to 64 tokens, so `max(slider_id)` is always 64. Each one was a
  wrong assumption that stopped instead of spreading.

  **Two things found by reading rather than reasoning.** The Phaser's own comment
  said its host position-lock needed no guard *because nothing in this plugin can
  modulate the rate* -- adding Drift made that false, so it now hands over to
  free-running exactly as the filters do. And a `cd src` inside a compound command
  failed because the shell was already there, so an edit never ran AND the lint
  that followed reported clean, on the unchanged file. Caught by grepping the
  actual slider line rather than trusting an exit code.

  **Resonance Bank was the hard one.** Its Drift is a TWO-dimensional nested
  selector, 16 bands x 5 targets, so Ramp had to match that shape: nine more
  80-slot banks, its own target selector, and clocks advanced once per sample
  outside the serial/parallel branch because only one of those runs. Its
  `Drift period mode` also lives in a SERIALIZED bank, so the blob bumped to v2
  and a v1 blob is read and then migrated -- gated on the blob HAVING the field,
  never on "the blob is old". Simulated: all four period modes drift at
  identical speeds before and after the remap.

- **2026-09-05 — R20's enum order BUILT in five plugins, and four of the five cost no project edit at all.**

  The sweep the rule was written for. `{Own BPM, Host x}` and `{Own Hz, Host x}`
  become the canonical `{BPM, Seconds, Hz, Host x}`, which moves Host x from
  index 1 to 3 and adds two real modes rather than merely renaming.

  **Rhythm Track, Shepard Scale, Heartbeat, Stereo Phaser, Sweep Dwell.** All
  lint clean, all verified by simulating the branch at project tempo 90 and
  reading the output: Seconds 2 gives a cycle every 2.000 s, Hz 2 gives 0.500 s,
  Host x 1 gives exactly one cycle per project beat, Host x 2 gives 1.333 s.

  **The trick worth keeping: a DEFAULT change can stand in for a migration.**
  Stereo Phaser's three instances in `strangeness.RPP` and Heartbeat's one in
  `transformation.RPP` all store `-` for their rate mode — nothing at all — so
  they take whatever the DECLARED default is. Moving the Phaser's default to Hz
  (index 2, not the suite's usual BPM) lands them on exactly the behaviour they
  had, with no edit to a finished project. Checked by reading one real line
  rather than trusting the decoder, which is the standing rule and which is what
  distinguished "stored 0" from "stored nothing" — the two look identical in a
  summary and are completely different to migrate.

  **Sweep Dwell's pan list was BACKWARDS and nobody had noticed.**
  `{Hz, Seconds, BPM, Host x}` against `{BPM, Seconds, Hz, Host x}` on the Rate
  Mode a few positions above it in the same plugin. Position one meant Hz on one
  control and BPM on the next, in a suite navigated by arrowing the parameter
  list one control at a time. The Tremolo and the Sweeping Filter have the same
  fault and get it fixed in their own reorders.

  **One project migrated: `surges.RPP`**, slider 19 from `0` to `2` — the same
  Hz, in its new position. Backed up to
  `E:/reaper/finished/backups/surges.RPP.pre-panmode-order-20260905-bak`.
  Assertions before writing: exactly one instance, the line has an ending, the
  token is what was expected, only that token differs, line count unchanged,
  byte length unchanged. Verified after by re-reading from disk and decoding
  against the NEW enum, plus a range check — 64 stored values, 0 out of range.

  **Ordering hazard, and it was worth saying out loud rather than assuming:**
  installing the new Sweep Dwell BEFORE migrating `surges.RPP` would have read
  that project's pan as BPM instead of Hz and run it sixty times slower. The
  plugin and the project have to move together.

  **HELD BACK on purpose: Resonance Bank.** Its `Drift period mode` is out of
  order too (`{BPM, Hz, Seconds, Host x}`), but it is stored in a SERIALIZED
  per-band bank — `file_mem(0, band_drift_mode, N_BANDS * N_TARGETS)` — so
  reordering it needs a version-magic-gated blob migration and an `@init`
  default change, not a token edit. That is the "migrate what was RESTORED,
  never what was DEFAULTED" trap sitting in the middle of it. It gets its own
  pass. Squeezing it in at the end of a long session is exactly the pattern this
  repo keeps paying for.

- **2026-09-04 (last) — R20: the rate block is SETTLED. The sixth session's worth of redesign, stopped by Rozaya, and written down so there is not a seventh.**

  Nothing was built. The whole session on this point was me proposing three
  different shapes in a row and being corrected each time, which is worth
  recording exactly because the correction came from the person who cannot read
  the source.

  **The shape.** Every rate carries two adjacent controls: a rate value, then a
  rate mode of `{BPM, Seconds, Hz, Host x}` — always those four, always that
  order, everywhere. In Host x the rate value means every N beats. A plugin with
  two rates has two complete pairs, and the pan gets its OWN mode rather than
  borrowing the main one. Forbidden: a sync switch, a target selector, a
  separate `Every N beats` slider, a `Host ratio` picker, any control that
  writes into another control, any multiplier.

  **What I got wrong, in order, because the sequence is the lesson.** I showed a
  Sweeping Filter layout whose rate value read `(BPM / sec / Hz / beats per
  cycle)`. Rozaya: *"beats per cycle makes me raze my eyebrows... Don't do to
  filter what nearly happened to womb."* I read that as "adopt Womb's separate
  beats slider", went and read R11, found the plan's paragraph saying a
  two-rate plugin needs a target selector, and proposed exactly that. Rozaya:
  *"The thing here was to remove the fucking multiplier, not to have it do the
  thing of, oh, well, this is host x, so I guess we can just add more sliders."*
  I then swung the other way and proposed reversing all thirteen plugins to
  Womb's shape. Rozaya pulled it back again: *"rate value means every n beats in
  host x, just like it does with anything else. We don't need a separate
  slider."*

  **The thing I should have led with, and did not, is that the suite navigates
  by ARROWING the parameter list.** Rozaya: *"Keep in mind, I have to arrow
  through the p list to get to things I don't tab. So this is what... this is
  why I'm so picky about it."* Every proposal above should have been costed in
  positions-to-arrow-past first. Melody's way is 7 controls for the filter's two
  rates; the settled way is 4.

  **The measurement that ended it, and it is the reusable kind.** The plan
  justified R11's three extra sliders on Melody needing to sync its sequencer
  and its pan independently. Decoded across all 73 Melody Phase instances in the
  library: 27 have `Sync to host` ON and **all 27 target `Rate value`. Zero
  point at the pan.** The capability has never been used once, and it has cost
  three positions in the parameter list on every instance since it shipped. One
  instance is set to every `0.333333` beats, which does confirm the other half
  of the original argument — the beats number must be free, never a menu.

  **And the real constraint underneath, which was a missing control rather than
  a limitation.** Melody's `Pan base rate` has no mode of its own: it is handed
  the SEQUENCER's `rate_mode` (`melody_phase.jsfx:1116`, `:1492`). So there was
  nowhere to put Host x for the pan, and three sliders were added to reach
  around the outside instead of one to fill the hole. Rozaya had been given this
  as a justification at the time and could not evaluate it — *"I just nodded and
  smiled... They're Claude. You're not breaking it down at all."* It was true as
  far as it went, and the cheaper fix was sitting next to it unmentioned.

  **The enum order was the part nobody had noticed at all.** Measured: five
  different shapes for the rate mode, and **every pan unit in the suite runs
  backwards** — `{Hz, Seconds, BPM}` on Tremolo and the Sweeping Filter against
  `{BPM, Seconds, Hz, Host x}` on the Rate Mode a few positions above it in the
  same plugin. For someone arrowing, position one means BPM on one control and
  Hz on the next. Canonicalising costs 36 stored instances, all uniform, none of
  them changing how anything sounds.

  **What was actually done this session: documentation, and deliberately in
  place rather than by deletion.** R20 written into
  `docs/suite-consistency-plan.md`; R11's heading and the "where the heavier R13
  shape still earns its keep" paragraph both struck through WITH their original
  text preserved, so a session that half-remembers the claim finds the
  correction attached to it rather than a silent absence. Rozaya on why that
  matters: *"make sure you're updating said plan because that's another tripping
  hazard that all the clods have just been stumbling and falling on their asses
  about."*

  **Migration honesty.** Melody was already migrated on 2026-09-02 and this will
  migrate it again, breaking the one-migration-per-plugin rule. Flagged before
  proceeding rather than after. Rozaya: *"that's already been broken. It's
  already been broken five times today because we've been busy dealing with
  fucking bugs and glitches and getting distracted and not sticking to the
  goddamn plan."*

- **2026-09-04 (latest) — EAR-TESTED ✓: the Host x beats-per-cycle conversion. The suite's largest untested block is closed.**

  R13-revised flipped `Rate Value` in Host x from a tempo MULTIPLIER to BEATS
  PER CYCLE across thirteen plugins, finishing earlier the same day. In eleven
  of them nothing saved was touched, so the risk was confined to the mode. In
  the Tremolo and the Sweeping Filter, real stored values in real projects were
  rewritten to their reciprocals. **Rozaya played them: the sweeps run at the
  speed they remember.**

  **The sharpening, and it is the reusable part of this entry.** The status note
  had been saying "ten instances worth playing, across six projects". Decoding
  the live project files rather than re-reading the note cut that in half.
  **Four of the ten were Tremolos stored at `1`, and one is its own
  reciprocal** — their number did not move and neither did their meaning, so
  they were never evidence about the conversion in either direction. The six
  that genuinely changed are all Sweeping Filter, in four projects:
  `bilateral-with-binaurals` (2, now 0.125), `as-things-are` (1, now 8),
  `noisescape-august-18-2026` (2, now 4 and 8) and
  `womb-and-baby-heartbeats-with-bloodflow` (1, now 0.5). Only the first is
  finished work; the rest are in `to-play-with-later`.

  So the general form: **an identity value under the transform is not a test
  of the transform.** When a migration is asked to be ear-tested, decode which
  stored values actually moved before naming the projects to play — otherwise
  half the ask is confirmation that cannot confirm anything, and the listener
  spends their attention on it.

  **What this does NOT cover.** Drift and Ramp running *while* in Host x, and
  pan following the project tempo — tests 3, 4 and 5 of
  `docs/host-sync-ear-test.md`, still never heard on any plugin. The mode itself
  was already proved by ear twice before today (Melody, 2026-08-11; Womb,
  2026-08-30/31); what closed today is the conversion sitting on top of it.

  **And a note on how it nearly stayed open.** Rozaya had already done this test
  and had simply not said so — *"They do, I just forgot to say so."* The suite's
  documented failure mode is a settled thing being re-derived by a later
  session, and this is that failure mode with the polarity reversed: work that
  is done, recorded as outstanding, and queued up to be asked for again. Ask
  what has already been heard before recommending an ear-test.

- **2026-09-04 (later) — the Phaser reorder LANDED: plugin installed, project migrated and promoted. Verified by decoding; NOT ear-tested.**

  The rate triple (Rate / Rate Mode / Host ratio) had been reordered in `src/`
  on 2026-09-04 and deliberately left uninstalled, because installing it alone
  would have made `strangeness.RPP` read its numbers off the wrong controls.
  Both halves are now in place: `src/stereo-phaser.jsfx` is copied into the
  effects folder, and the migrated project has been promoted to
  `E:/reaper/finished/strangeness.RPP` with the pre-reorder original kept beside
  it as `strangeness.PRE-PHASER-REORDER.RPP`. The old plugin build is backed up
  OUTSIDE the effects folder, at
  `<REAPER resource>/_plugin-backups/stereo-phaser.PRE-REORDER-20260904.jsfx` —
  outside on purpose, because a renamed twin left inside that folder is its own
  documented trap here and would have shown up as a second Phaser forever.

  **Evidence, and its limit.** Decoded control-by-control by NAME, old layout
  against new, across all three instances: 27 comparisons, 0 mismatches. After
  promotion, re-checked in place: 21 stored values, 0 outside their declared
  ranges, 192 lines unchanged. **It has not been heard.** Rozaya listened to
  `leaning into strange.opus` (an August render that is probably this project)
  and called it close enough — but the new build was not installed at that
  moment, so nothing was A/B'd. Recorded as decoded, not eared, because that is
  what happened.

  **Two process notes, both mine to own.** I asked for a two-render before/after
  comparison for a change already verified by decoding, which was ceremony on
  top of sufficient evidence and cost the session its patience. And when asked
  whether a reference render existed, I searched `E:/reaper` only, found nothing,
  and reported "there isn't one" as though I had looked everywhere — there are
  426 renders on that drive, under `E:/renders/finished projects/` and
  `E:/renders-opus/`. The conclusion happened to hold; the method did not. **A
  negative from a search is only worth its scope, so state the scope or widen
  it.**

  Also fixed: the reorder's header comment still promised that old projects
  "repair themselves on load, see @block", pointing at a runtime repair that had
  been deleted the day before *on purpose* (a migrated project has no blob
  either, so it would have permuted a correct file a second time). A comment
  pointing at absent code is how a future session re-adds it.

- **2026-09-04 — five ear-tests passed, drift and ramp learned to rest, and I spent the day overriding the person who could see. On `feature/melody-reorder`, 65 commits, PUSHED, unmerged.**

  **Heard and passing, all by Rozaya:** the Melody layout migration on all four *finished* projects (`melodic`, `outcoming`, `slow-summer`, `upswing` — 73 instances that had been verified by decoding and never played); per-cycle pan on Polyrhythm, each voice stepping on its own tremolo wrap; Veil's 22-slider rebuild and the beat-counted Ramp; the -12..-72 dB/oct rolloff, closing the last item from the August overhaul; and Tremolo's drift play/rest.

  **Built:** Drift play/rest and a Ramp staircase, in Veil then Tremolo. `Ramp time unit {Minutes,Beats}` — REAPER counts in beats and the Ramp was hardwired to wall clock, the same decision Drift got in the Host x sweep and the Ramp did not. **Beats, never bars**, decided by Rozaya asking *"what is a thousand beats in bars? do we know?"* — 250 in 4/4, 333 in 3/4, so bars need `ts_num`/`ts_denom`, which NOTHING in this suite reads. One shared `pr_frozen()` rather than two copies, because two becomes 28 across the remaining plugins.

  **The park point rotates, and that is the feature.** Each freeze lands further round the wave, so `play 1.75` cycles four positions before repeating and only one is dramatic. An awkward fraction beats a tidy one; a whole number parks at neutral every time and is nearly inaudible. Rozaya heard it as *"really hard to tell exactly what it'll do next, which is the point"* before it was measured.

  **The linter had been crying wolf on all 21 plugins** — 3 to 24 false hits each, because the case-collision check scanned slider LABELS as code. Never once actionable, which is how a check gets ignored. Fixed; the suite drops to two real hits, both neutralised by `local()`.

  **Four errors in one day, all the same error.** Every one was me trusting my own construction over what Rozaya had directly said.
  - Wrote *"a listener's report is a symptom, not a diagnosis"* into CLAUDE.md, aimed at the person whose diagnoses have repeatedly beaten mine. Deleted.
  - Invented an example of how they talk (*"make it breathe slower"*) and got it backwards — they are precise **on purpose**, because a session once read vagueness as licence and shipped a plugin with no numeric entry at all.
  - Wrote *"don't diagnose, just say what it did"*, which throws away the best input the project has. Their correction of a Depth dB value I had specified caught a **false fail** before it happened.
  - **The bad one.** Predicted a case-fold bug in both Shepards. Rozaya tested them and said plainly they were fine, BEFORE I touched anything. I produced an exact-cancellation argument that made that compatible with the bug still existing, and shipped the change anyway while they were busy testing something else. The argument fitted one plugin and contradicted the other. Reverted; the prediction is refuted by two direct tests. The collision is real and inert. **A fact about the source is not a fact about the sound.**

  **And the judgment call that closes it.** For Phase 2 I built a runtime self-repair — the plugin permuting its own sliders on load. Rozaya refused to open the result: *"reaper only reads the numbers. It doesn't know what sliders they correspond to."* Right, and the repair belongs in the project FILE where it can be checked before anything opens. Worse, once the file migration existed the runtime version became a way to scramble a correct project, because a migrated file has no blob either and the plugin could not tell "old layout" from "already fixed". Deleted. `tools/phaser_migrate_rate_triple.py` does it in the file: 27 controls decoded by name old-vs-new, 0 mismatches, 0 out of range, 3 changed lines out of 192.

  **Carry forward, and it is one line: when Rozaya says something plainly, that IS the answer, not an input to reconcile with a model.** Every check that worked today was theirs.

- **2026-09-02 — the long repair day. Melody's layout migration finally ran; per-cycle pan modes reached the oscillator plugins; Host x started becoming a real unit. On `feature/melody-reorder`, ~40 commits, UNPUSHED, unmerged.**

  **Melody layout migration: DONE and verified.** 73 instances across 7 projects. The script existed and had run once in August, but the projects were restored from backup afterwards for the line-eating defect and nobody re-ran it. Its gate was the problem: it asked "does this store more than OLD_COUNT values", and a count cannot answer that — it was already wrong for two projects storing 84, and adding `Pan Glide ms` that morning pushed a third un-migrated project to 79 and made it look done. **It now range-checks every value against BOTH layouts' declared ranges, read from git and the working tree rather than from a table authored beside the permutation map.** Verification decodes each instance by CONTROL NAME on both sides against a pre-migration snapshot: 4632 comparisons, plus line counts, instance counts, and a range check. Snapshot at `E:
eaper\_pre-melody-layout-20260902-1503`.

  **Per-cycle pan modes** (`Alternating`, `Distributed`, `Converging`, `Diverging`, ping-pong variants, plus new `Alternating every 2/4/8`) now exist in all six plugins that have pan modes. `percycle_pan()` is byte-identical across the oscillator sources. **The tick differs and that is the whole point:** filters advance on their LFO wrap, Polyrhythm on the voice's TREMOLO wrap, Melody on the NOTE TRIGGER — so the pan moves because the sound did and there is no second clock to drift. In Polyrhythm the cycle index is **per voice**; a single shared index panned everything at the base rate and Rozaya heard it instantly: *"it was using the base rate, and ignoring the rest."*

  **`Pan Glide ms` propagated** to the oscillator plugins (was hardcoded at 10 ms while three effect plugins exposed it). **0 = instant is not a nicety** — bilateral alternation is a cut, not a sweep, and that difference is why a Tremolo instance could not be swapped for Melody's own pan: *"you're asking me to replace apples with cake."*

  **R13 REVISED — Host x stays a rate mode.** The original R13 said "sync is not a unit" and split it into a switch. Rozaya inverted the diagnosis: Host x IS a rate mode; what was dishonest was Rate Value silently becoming a multiplier there. So leave it in the enum and make **Rate Value mean beats per cycle**, with the label saying so. No new sliders, and irrational ratios survive. Done in both Polyrhythms, Dapple and Bubbler. **The counts that rank the rest: only `full-feature-sweeping-filter` (6), `Full_Feature_Tremolo` (4) and `womb_sound_generator_v3` (1) have any instance on Host x — 11 instances, not twelve plugins.** Full recipe, per-plugin shapes and the guard below are in `docs/suite-consistency-plan.md`.

  **Two bugs I introduced and Rozaya caught by asking, both worth generalising:**
  - **Inverting a unit inverts its edge cases.** `1 / max(raw, 0.001)` clamps the DENOMINATOR, so 0 became 1000 Hz where it used to mean "stopped". `Vn Drift / Rate` spans −1000..1000 and defaults to 0, so every fresh voice would have screamed. Write `raw > 0.001 ? 1/raw : 0.001`. **Whenever a control's unit inverts, re-check zero and negative.**
  - **Two numbers that look alike can answer different questions.** I removed `Cycle Steps` and derived it from the active-voice count, because Spread uses that count. But Spread ranks VOICES across the field; a per-cycle walk is a TEMPORAL pattern length. At 2 steps every walk mode returns `[-1,1,-1,1]` — seven modes silently collapsed into Alternating. **And `Cycle Steps` is not a parameter of the shape function, it is the wrap length of the INDEX feeding it**, which is why it affects Alternating too (an odd value makes it limp). Reading `percycle_pan` alone cannot show that; you have to read the advance and the function together.

  **The process lesson, and Rozaya put it hardest: "THIS IS WHY SCRIPTS WILL END A PROJECT."** A scripted edit applies one wrong assumption to every file instantly, and every structural check still passes — paren balance, lint, slider counts — because nothing is malformed. It is semantically gutted and syntactically perfect. **The check that catches it is simulating the function and looking at the output numbers.** Seven modes returning `[-1,1,-1,1]` is visible in one line.

  **Still open:** R19 (pan mode lists are in arrival order across four different inventories — blocks a RELEASE, not a push); `rhythm-track` has six pan modes, no per-cycle machinery and no Pan Glide; Tremolo lacks `Alternating (Flipped)` both filters have; nine plugins still on the Host x multiplier. **Nothing in this session has been ear-tested except Pan Glide 0** (*"no click, no weird shit"*).

- **2026-08-30/31 — Womb's tempo sync rebuilt and ear-tested, the whole consistency sweep DESIGNED, and Phase 0 + most of Phase 1 shipped. Everything merged to master and pushed. `docs/suite-consistency-plan.md` is the authoritative document; read it before doing anything here.**

  **Womb (built, ear-tested ✓).** Host x carried two named-ratio pickers, each writing into a number that hid behind it. Replaced by the shape Drift and Ramp already use: a **`Host sync target`** selector and one free **`Every N beats`** value, sitting directly under Rate Mode. A ratio menu is a **grid** — "every 5 beats of a 4/4 bar" was not on it, in a suite whose whole subject is layers slipping against each other. **Heart rate is plain BPM in both modes now**, not a tempo multiplier, which is what had forced it to hide (70 as a multiplier is seventy times the tempo). **The breath's four sliders ARE beats in Host x**, and their sum is the cycle — the same rule Own BPM uses with seconds. **Systole is in beats too**, so both halves of the heartbeat land where you put them: `0.25` is a quarter-beat after the lub at any tempo. Entering and leaving Host x are both silent; the four breath sliders and systole convert at the switch.

  **Four bugs, all found by ear, all mine, and two are new gotcha entries above.** The beats bank was seeded outside the `drift_cfg_inited` guard, so every transport play reset it (Womb has no `ext_noinit`). The sync block was gated on a tracker adopted only in `@block`, so it was **dead while the transport was stopped** — which is how this suite gets configured. A slider written without `sliderchange()` reverted, because REAPER keeps its own copy. And `@serialize`'s read branch didn't restore the visible slider from the bank like every other bank in the file does.

  **The design is complete.** R11 (one sync block, not per-rate pickers) · R12 (ranges 0–1000 or signed, dB exempt) · R13 (**no multipliers anywhere; sync is not a unit** — split `Rate mode` from a `Sync to host` switch) · R14 (`Ramp to`, a destination, not `by`) · R15 (the sigh gets its own four segments; a multiplier can only stretch time, and a sigh differs in *shape*) · R16 (`Ramp`, not `Speed ramp`) · R17 (**no unitless sliders** — "depth of what?" must have an answer) · R18 (**new sliders go where they belong; only enum OPTIONS append**). Plus ten decisions approved in one pass, four authored layouts in `docs/layouts/`, and `docs/planned-features.md` gained **breath catches** — one control giving a sigh, the post-crying shudder and the sobbing exhale, and the most legible distress cue Womb could have.

  **Shipped, no migration needed:** `Speed ramp` → `Ramp` (70 labels, 14 plugins) · one step per concept (43 sliders; `Start delay` now 0.001 everywhere) · **every dB slider at 0.01** · Polyrhythm's per-voice gain defaults −60 → −6 (activating a voice gave silence and a 54 dB climb; Melody had it right all along).

  **The finding that reframes the whole sweep: the suite does not have a design problem, it has a DISTRIBUTION problem.** Nearly every question hit was already answered correctly *somewhere in it* — the multiplier had been removed once, `Ramp` was already renamed in the Morpher, Melody already defaulted gains right, Womb already named RSA in BPM, the migration tool I was about to write already exists as `tools/passage_migrate_sliders.py`. Five unpropagated decisions in one evening. **Search the repo and `git log` before estimating that something needs building or deciding.**

  **Three process rules, all Rozaya's, all binding.** (1) **Verify the OUTPUT, never the run** — a clean script exit is the weakest available evidence, and scripts may *apply* an authored list but never *infer* one; the safe edit form is an exact literal match plus a count assertion. (2) **No releases until the sweep is done** — pushing is fine, a release is a distribution artefact and shipping one mid-sweep hands a stranger a half-renamed suite. v2.21 was made this session and is now marked **pre-release**; v2.20 is "Latest" again. (3) Rozaya **can** reload projects to test — ask for one rather than assuming that path is dark.

  **Where it stands.** Phase 0 done. Phase 1 mostly done. Phase 2 (reorders + migrations) not started, ordered **by measured use**: Morpher 38 projects, Polyrhythm v1 17, Sweeping Filter 11, Passage 10, Womb 8, Tremolo 7, Melody 5. Six plugins have **zero** projects. Both version forks are resolved: **Melody v2 archives** (its note picker moves to v1), **Polyrhythm v1 migrates up to v3** — the blobs are byte-identical, so drift and ramp configs cross untouched, and no project uses a semitone value v3 cannot hold. 91 projects snapshotted to `E:\reaper\_pre-phase1-20260831`.

- **2026-08-19..22 — the long one: Morpher Layers + Solo, a filter-rolloff overhaul that turned into a calibration bug hunt, Womb's breath following Host x, and a suite-wide restore-order sweep. All on `feature/morpher-layers`, UNMERGED. Partly ear-tested — see the status list at the end.**

  **Spectral Vowel Morpher — Layers.** Sixteen copies of the whole morph (voice
  *and* wash) at fixed intervals, behind one nested selector: a PITCH LADDER —
  4/3/2/1 octaves down, a fifth down, a fourth down, **Original (unison)**, a
  fourth up, a fifth up, 1/2/3/4 octaves up, then three free-interval Custom
  slots. Five sliders total (Layer, Active, Level, Solo, Pitch). The point is the
  LOCK: two instances on Shuffle land on different slots and clash, where a layer
  is the same capture an octave away, so octaves stack consonantly. Also shipped:
  **High cut** (absolute frequency, applied AFTER the pitch shift so a layer
  transposes underneath it; also thins the voice's partials, making it cheaper),
  **Solo** (overrides Inactive — you solo to hear a thing), and **Voice level →
  Output level** in both Morpher and Passage, because it was never the voice's
  level: it sits after the voice/wash crossfade and scales everything but the dry
  input. Slider IDs 33-37; targets 24; blob magic **7700008**.

  **The Original is a layer.** It has a bank slot (index 6) like everything else,
  so it takes Active/Level/Solo and `base_gain = layer_gain[LAY_ORIG]` gates both
  the voice engine and the wash's base term. That one line caused two silences —
  see the bugs below.

  **Filter rolloff — and REAPER's stock filters are miscalibrated.** Star noticed
  the *filter* plugins had almost no slope control. Veil and both sweeping
  filters now do **-12 through -72 dB/oct** (1-6 cascaded 2-pole TPT sections).
  Three things had to be right and only the first is obvious: per-section
  **Butterworth Q** (cascading identical sections drags the composite -3 dB point
  down by `sqrt(2^(1/N)-1)` — at six stages a 480 Hz cutoff really corners near
  168); **resonance spread across sections** (peaks add in dB, so per-section
  resonance multiplies); and **TPT rather than Chamberlin** (a six-stage
  Butterworth puts Q 3.83 on its last section before Resonance is touched).
  Verified by simulating the exact arithmetic: -3.01 dB at the cutoff at every
  slope, 2 through 12 poles.

  **...and the sweeping filters' "Frequency Hz" was never Hz.** They shared
  REAPER's stock `filters/resonantlowpass` core verbatim — Paul Kellett's
  musicdsp #29 with `cut = 2*fc/srate`. Measured, the real -3 dB corner sat at
  **0.21x to 0.77x** the number on the slider, *varying with Resonance* (so
  Resonance was quietly a second frequency control, moving the corner nearly two
  octaves). The error decomposes exactly: musicdsp documents `f = 2*sin(pi*fc/sr)`
  ≈ `2*pi*fc/sr`, and REAPER's is that **with the pi dropped** (measured ratio
  0.3184 vs 1/pi = 0.3183), compounded with the 0.644x from cascading two poles.
  0.318 × 0.644 = 0.205, against 0.206 measured. **REAPER's stock Resonant
  Lowpass and Sweeping Lowpass have this too** — if you ever use them, their Hz
  reads 2-5x high. Nothing was copied from Liteon's GPL Apple 12-Pole (which is
  where the 72 dB/oct idea came from, and whose cutoff is a MIDI note number
  squashed onto 0-100); Butterworth is 1930s textbook and the pole angles are
  computed, not tabled.

  **Womb — the breath follows Host x now.** It didn't: the heart went through
  `slider1 * tempo` while `breath_state_advance` was a bare `1`. The breath has
  its own rate control (sliders 64/65: a picker + beats-per-breath), because the
  heart had ONE number to multiply and the breath's rate was an emergent sum of
  four sliders. Entering Host x is silent — beats-per-breath is seeded from the
  cycle the four sliders already describe. Every slider whose meaning depends on
  Rate Mode now says so in its own name, and Breaths-per-minute HIDES in Host x
  rather than sitting there inert (Star: a silent unit change is "the same
  problem wearing different clothes" whether a mode gates it or not).

  **Migrations run against the real library** (all with backups; snapshot of the
  9 filter projects in `E:\reaper\_pre-hz-migration`):
  - `tools/morpher_migrate_layer_order.py` — layer/target indices, 2 projects.
  - `tools/sweepfilter_migrate_hz.py` — 9 projects, 16 instances. Matches the old
    filter's **PEAK**, not its corner: above ~0.4 Resonance that filter peaks at
    0.32x the set frequency, well below its corner, and corner-matching put the
    drain half an octave high and 8 dB quiet. Rewrites Resonance too (the old
    curve is flat to 0.4 then vertical: +5 dB at 0.7, +28 at 0.98, +53 at 1.0).
    Peak height within 0.10 dB across the library. RES_DB_MAX is 34 nominal
    (~+31 dB actual) in all three filters so the drain was representable.
  - `tools/morpher_repair_muted_original.py` — 9 instances the muted-Original bug
    had baked in.
  - `tools/jsfx_lint.py` — paren balance per section, empty `()`, case-folded
    names, scientific notation, reserved-variable writes, and slider declarations
    after an `@section`. Run it; REAPER tells you none of this until load.

  **Four bugs worth remembering, all of them mine, all found by ear or by
  measurement rather than by reading:**
  - **Bank-derived values computed in `@slider`** — swept the suite; own gotcha
    entry above. Symptom: touching any control fixes it, transport does not.
  - **A version gate that migrated DEFAULTS.** The layer permutation was gated on
    "blob is old" (`< 7700008`) rather than "blob HAS layer banks" (`>= 7700004`).
    Pre-layers blobs never wrote those banks, so the `@init` defaults — already in
    the current order — got permuted, moving the Original's unity gain off its
    slot. **Migrate what was RESTORED, never what was DEFAULTED.**
  - **A selector default and a value default are a PAIR.** `slider33` (Layer)
    defaulted to the Original; `slider35` (Layer level) defaulted to -60; `@slider`
    stamps the visible level into the selected layer, so every fresh instance
    muted its own Original before the first sample. The value slider's default is
    not a free choice — it is whatever the default-selected target holds.
  - **Loose pattern matching, three times in two days**: `grep "^slider"` matching
    `slider_show`, a `.count()` matching a deeper-indented superset line, and
    `startswith("slider")` putting a slider declaration inside `@sample`. The
    declaration form is `^slider<digits>:` and nothing else is. Now linted.

  **EAR-TEST STATUS.** Confirmed working: the restore-order picker fix (2026-08-23, on `infantile` — Rate Value holds at 180 on load and on track duplicate); Morpher Solo; the filter Hz migration
  (`the-sound-of-a-drain`, five instances at Resonance 0.98, the extreme case);
  Morpher defaults. NOT YET HEARD: **Veil**, **Sweep Dwell Filter** (1 project),
  **Womb's Host x breath controls**, and the steeper slopes generally.

  **RESOLVED 2026-08-23 — the "fresh/duplicated Sweeping Filter had no LFO
  effect" report was the picker bug, not `filt_stages`.** The straight-wire
  theory is now RULED OUT rather than merely unproved: the picker diagnosis
  proved `@slider` DOES run on a fresh or duplicated instance, just early, with
  the DEFAULT slider values still in place. With defaults, `filt_stages =
  min(FILT_MAXSTAGES, slider41 + 1)` is `min(6, 1)` = **1**, never 0 — so the
  cascade was never a straight wire and the loop count was never the fault.
  What actually happened is that the Host ratio picker stamped Rate Value to
  **0.5** on every fresh instance. In BPM mode that is one sweep every two
  minutes, which is exactly what "the LFO does nothing" sounds like from the
  listening chair, and it went away the moment you touched a slider because
  touching one made the tracker match. Ear-confirmed by Rozaya after the
  restore-order fix landed.
  The `filt_stages` move to `@block` STAYS — it is correct under any ordering
  and costs nothing — but it fixed a bug that was not there. **The seven other
  plugins with the same shape** (`polyrhythm_phase` and `_v3` `n_voices`,
  `shepard-scale` / `shepard-tone` `num_osc`, `stereo-phaser` `stages`,
  `sustain_looper` `nv`, `veil` `n_stages`) **need no change, and the reasoning
  that spared them was right**: "nobody has ever reported silent-until-you-
  touch-a-slider" was correctly read as evidence that `@slider` does run on
  instantiation. It does. Not sweeping seven working plugins on an unconfirmed
  diagnosis was the right call, and is the general lesson worth keeping —
  a symptom that matches your theory is not the same as your theory being true,
  and "what else produces exactly this symptom?" is the cheaper question.

  **Open, and not a bug: ~4 layers is the CPU ceiling -- PREDICTED, never
  measured, and about the VOICE only** (flagged 2026-09-01) even with Auto-morph off —
  five sources x 64 partials x 4 banks is ~1280 oscillators/sample. That is arithmetic over OSCILLATORS, so it says
  nothing about the WASH -- where layers are extra reads inside a grain that was
  already being built, not extra transforms (`build_spectrum`'s own comment: "this
  is why layers are nearly free here"), and where the voice engine is skipped
  entirely via its `hlevel` guard. It got quoted back on 2026-09-01 as a measured
  ceiling, to justify not building the wash half of the per-layer overtone. It is
  not evidence for that or anything else about the wash. Two existing
  controls are also CPU dials and it is not obvious that they are: **High cut**
  stops partials being computed (6 kHz on a 200 Hz capture caps you at harmonic
  30 instead of 64, ~half), and **Stereo width 0** runs a mono bank instead of a
  detuned pair (half again) — together ~4x. If that is not enough, the honest
  next step is a **Layer detail** control (layers synthesise fewer partials than
  the Original, since they are support rather than focus). Not built.

- **2026-08-11 Melody Phase v1 came BACK OUT of the archive, and Host x rate mode landed in both Melody Phases. On `feature/host-tempo-sync`, NOT ear-tested yet, NOT compiled — see the caveat at the end.**
  - **v1 was archived on a false premise.** The archive convention says a superseded version moves to `archive/versions/` and is frozen. But `grep -rl melody_phase.jsfx --include=*.RPP` over `E:/reaper` returns **five projects on v1 (`melodic`, `outcoming`, `slow-summer`, `upswing`, `simple-sequence`) and ZERO on v2.** Four of those are in `finished/`. v1 wasn't superseded in practice; it's the only Melody Phase actually in use, so it now lives at `src/melody_phase.jsfx` with its page restored to `docs/plugins/melody-phase.md`. **This is exactly the trap the slider-renumber note warns about** ("the assumption that lets you renumber freely expires silently") — run that grep before declaring anything superseded.
  - **v1 → v2 is NOT a filename swap, and nothing should ever suggest it is.** v2 collapsed the forty flat per-voice sliders (22–61) into six behind a Voice selector (22–27), so everything from 22 up shifts. Worse than the Passage case: v2's per-voice data lives in a `@serialize` bank rather than the slider line, so `tools/passage_migrate_sliders.py`'s "shift the slider line" approach does not transfer. A migration would have to synthesise a serialize blob. Not attempted.
  - **`Host x` is rate mode 3 on slider1, added at the END of the existing enum** (`{BPM,Seconds,Hz,Host x}`, range `0,3`), which is the waveform-slot pattern — saved values 0/1/2 are untouched. Rate Value becomes a **multiplier of the project tempo**; higher = faster, so only Seconds mode still inverts and the `rate_mode == 1 ?` branches in the Speed Ramp / Drift ratio code needed no change.
  - **Deliberately a multiplier, not a note-division grid.** Rozaya: *"I'm not just designing for locks."* The whole suite is phase music — the point is layers slipping against each other. A multiplier preserves ANY ratio through a tempo change, including irrational ones, which is precisely what a grid would take away. `slider77 Host ratio` is a convenience picker that WRITES Rate Value on change and then gets out of the way (`Custom` default, hidden unless mode 3, includes both phi ratios). That's the dyscalculia doc's actual rule — move the arithmetic, keep the precise control — rather than its rejected first draft.
  - **Tempo-follow is done through `combined_scale`, not by recomputing `@slider`.** `@slider` doesn't re-run on a tempo change, so everything derived from `cycle_seconds` would go stale. Rather than lift ~60 lines into a function, a new `@block` computes `host_scale` and folds it into `combined_scale` alongside Speed Ramp and Drift — the mechanism that already exists to stretch the whole timeline while keeping envelope proportions. `host_scale` is 1 in every other mode, so BPM/Seconds/Hz projects are bit-identical.
  - **`host_scale` MUST be absolute (`tempo / 60`), never a ratio against a remembered reference tempo — and this one shipped broken for an hour.** The first version stored "the tempo this `@slider` derivation was computed against" and used `host_bpm / host_bpm_ref`. That reads fine and it works right up until you press play: **`@init` re-runs on every transport play and wipes globals**, so the reference was reset to the *current* tempo while `v_step_seconds` / `v_note_seconds` still described the OLD one — ratio back to 1, tempo change silently discarded. Rozaya found it immediately ("transport doesn't flush the old thing either"). The fix is to have nothing to remember: `rate_to_cycle_seconds` computes mode 3 against a **nominal 60 BPM** so it's tempo-independent, and `@block` applies the live tempo as `host_scale = tempo / 60`. The two multiply out to the same `60/(tempo*value)`. **General rule for this codebase: with `@init` re-running per play, any design that needs to remember a value across transport is wrong unless it's explicitly guarded like `drift_cfg_inited`.**
  - **…and to the Start Delay counter, which is where it actually bit.** `start_delay_elapsed += 1 / srate` counts WALL-CLOCK seconds, but `start_delay_sec` is `units * cycle_seconds` — and in Host x `cycle_seconds` is NOMINAL. So the delay came out wrong by exactly the tempo ratio while every other timing on the same track was right. The symptom is nasty precisely because it's small and partial: two instances meant to hand off to each other sit *slightly* apart, which reads as drift or sloppiness rather than as a units bug. Rozaya diagnosed the shape of it before the code did — *"I suspect the problem is in the 'rate mode units' stuff."* Now `+= host_scale / srate`. **Lesson: when you introduce a second time base, audit every accumulator, not just the obvious one.** It still doesn't track Speed Ramp / Drift — pre-existing, left alone so existing projects don't shift.
  - **`host_scale` has to be applied to pan and drift EXPLICITLY — they don't ride `dt`.** `combined_scale` reaches the sequencer and envelopes through `dt`, but `pan_phase[i] += v_pan_freq[i] * pan_rate_mult / srate` and the drift phase advance (`speed_scale_current / (per * samples_per_primary_cycle)`) both accumulate on their own. Without the factor they simply ignore the project tempo. Anything else added later that advances outside `dt` needs the same treatment.
  - **Two naming traps, both found by Rozaya on first use, both worth internalising for any future sync UI.**
    - **`1/8` meant the OPPOSITE of what it says.** The picker's original labels were bare ratios (`1/8, 1/4, 1/2, ...`) meaning multipliers. But `1/8` in every other plugin on earth means an eighth NOTE — *faster* than a beat — whereas here it meant one cycle every eight beats, the far slow end. Now labelled by what you hear: `every 8 beats` … `1 per beat` … `8 per beat`, with `phi slow` / `phi fast` for the two irrational ones. **Never label a multiplier with note-value notation.**
    - **The null entry must not be called `Free`.** In LFO / tempo-sync UI everywhere, "Free" means FREE-RUNNING, i.e. not synced. Rozaya read it exactly that way — *"I thought it would just free it up and set it to wander at the tempo the plugin had set?"* — which is a completely reasonable thing to want and is a real feature, it's just Rate Mode (BPM / Seconds / Hz are the free-running cases; Host x is the synced one). Calling the do-nothing entry "Free" made the picker look like a second, competing sync switch. Renamed to **`Custom`** ("Rate Value is whatever you typed").
  - **Switching Rate Mode changes what Rate Value MEANS, and nothing rescales it.** 20 is 20 BPM in BPM mode and twenty times the project tempo in Host x. Toggling a running instance therefore jumps hard. Documented on both plugin pages; a future "convert my rate to the new mode" helper would be a genuine kindness but isn't built.
  - **Both files gained their first `@block` section.** Neither had one; the tempo read belongs there (same reasoning as the existing "transport-edge detection belongs in `@block`" note).
  - **`start_delay_sec` was simplified while passing.** The three-way per-mode arithmetic collapses to `units * cycle_seconds` for every non-Seconds mode — algebraically identical for BPM and Hz, and it picks up Host x for free instead of silently falling through the Hz branch and ignoring the tempo.
  - **The picker adopts on load rather than firing.** Without the `host_ratio_inited` guard, a project that saved `slider77 = 1/2` would have had its hand-tuned Rate Value overwritten the instant it opened, via `slider_automate`. Change-triggered one-shots that write another slider need this guard.
  - **EAR-TESTED 2026-08-11 (Rozaya): Host x works.** Two `harmoney-walk` instances on Host x, staggered by Start Delay, handing off to each other correctly once the time-base fix landed — *"Yes, that worked!"* So the mode compiles, loads, follows the tempo, and Start Delay is right. **Not yet heard:** Speed Ramp / Drift under Host x, pan following the tempo, and v2 specifically (all four tested instances were v1).
  - **Rozaya has now poked at it in REAPER**, which is how the transport bug and both naming traps surfaced — so it at least COMPILES and loads. Still not ear-tested for sound.
  - **CAVEAT: not compiled by us, not ear-tested.** JSFX can't be built outside REAPER, so this is syntax-checked only (paren balance, no empty `()` branches, reserved-name audit clean). Installed copies are backed up as `*.pre-hostsync.bak` in the Effects folder. Merge `--ff-only` once it's been heard.

- **2026-07-28 EAR-TEST RESULTS from Rozaya, clearing most of the outstanding queue — and one REJECTION.**
  - **Melody Phase v2 — PASSED** (tested some time ago; the "untested" note below was stale).
  - **Passage Capture average — VERIFIED WORKING**, heard while adjusting projects.
  - **Morpher/Passage click fix — VERIFIED on BOTH.** Passage first, Morpher confirmed on a fresh project later the same day. This was the bug that started the whole run.
  - **Morpher Capture average (global) — VERIFIED.**
  - **Overtone — REJECTED, and the design is wrong at the concept, not the implementation.** Rozaya: *"I can hear that real overtones don't dip everything else and that's what this is doing."* Correct. The gain curve floors every partial at `otfl` and returns the chosen one to **1.0** — the maximum gain in the curve is 1, so nothing is ever lifted; the overtone only ever emerges by everything else falling away. That is a duck, and it sounds like one. **The error was mine and it was in the reasoning, not the code:** I argued a tract resonance "redistributes rather than adds," which is true of a filter's ENERGY but not of its SHAPE — a resonance is a PEAK, so the chosen harmonic goes ABOVE its normal level while the others stay roughly put. Normalizing to the peak is mathematically identical to attenuating everything else, which is exactly what shipped.
    - **Fix: normalize by total POWER, not by peak.** Boost the target partial, then scale the whole bank so summed RMS is unchanged. Ear-safety survives (output never gets louder) and the percept inverts. For 64 partials with a 20 dB boost: chosen partial **+16 dB**, everything else **−4 dB**, versus today's 0 dB / −24 dB. A 4 dB dip reads as "a note emerged"; a 24 dB dip reads as "the voice ducked." Real spectra roll off steeply, so boosting a quiet upper partial (8-10, the usable range) costs even less broadband reduction than that.
    - Consequence: **Overtone depth stops meaning "dB the others drop by"** and becomes how hard the resonance lifts the chosen partial — the honest description of what a throat does. Same change needed in both plugins (Passage per slot, Morpher global).
    - **General lesson: an ear-safety constraint ("it can only ever get quieter") silently dictated the DSP shape.** The constraint was right; expressing it as per-partial peak normalization was not. Power normalization satisfies the same safety requirement without inverting the effect.
    - **FIXED same day and EAR-TESTED ✓ by Rozaya, both plugins.** Curve is now `1` everywhere with a raised-cosine LIFT to `10^(dB/20)` on the window, then the whole bank scaled by `sqrt(NHARM / Σgain²)` — folded into `ot_gain[]` so the voice loop is unchanged. Wash mirrors it (`(1 + (ot_boost-1)*ow) * ot_norm`, with sub-f0 bins taking `ot_norm` alone so the bed recedes with the band rather than the band rising out of an untouched bed). `ot_floor` is gone; `ot_boost` / `ot_norm` replace it. Slider relabelled **Overtone lift**, same ID (Passage 37, Morpher 30).
      - Measured: 6 dB → **+5.8 / −0.2**; 12 → +11.1 / −0.9; 18 → +15.1 / −2.9; 24 → +17.1 / −6.9; 36 → +18.0 / −18.0. **Sweet spot moved DOWN to 12–20 dB** (was documented as 20–30). Past ~30 dB the lift plateaus near +18 and you only lose drone — so high settings degenerate back toward the old ducking, which is inherent to a fixed power budget, not a bug.
      - Normalization is computed against a FLAT spectrum (cheap, no per-sample pass over live magnitudes). Verified it errs in the safe direction on real material: at 24 dB lift the overall level lands **−1.6 dB on a 1/n spectrum and −5.4 dB on 1/n^1.5** — never louder. Exact only on flat, and that is fine.
      - **Old projects change character**: the number now means the opposite thing, so a saved 24 was a 24 dB duck and is now a 17 dB lift. Documented in both plugin pages; no migration, because the right value is an ear decision.

- **2026-07-28 (ear-tested ✓) — Morpher's Capture average goes global; a dead "Morpher v2" plugin file found in the effects folder.** Two things, both housekeeping that mattered.
  - **A stale `spectral_vowel_morpher_v2.jsfx` was sitting in `<REAPER resource>/Effects/glasswings/`, and Rozaya had been loading it.** It is the pre-rename snapshot of Passage — 1448 lines, **8 lines different** from `spectral_vowel_passage.jsfx` at the rename commit `6d192ab` (the `desc:` line plus one comment paragraph), deployed about an hour before that commit landed. So it worked, felt like a real third plugin, and silently missed everything after 25 July. No project on C: or E: referenced it (100 `.RPP` files checked); deleted. **General lesson: plugins are hand-copied into the effects folder and copying never REMOVES anything, so a rename leaves a working-but-frozen twin behind.** A `--prune`-style sync script would close this; noted in `docs/planned-features.md`. Diagnostic tell for next time: the orphan's mtime is older than its siblings' and it is absent from `git ls-files`.
  - **Capture average is now GLOBAL in Morpher** (per slot in Passage still). It landed per slot only because `f7dfbc0` ported it wholesale from Passage; Overtone was ported in the *same commit* and correctly made global ("a field you sit inside, not a route whose stops each have a character"), and the same reasoning simply never got applied to the second control. The justification it carried — "pairs with the per-slot Capture point" — does not hold: **Capture POINT must be per slot because it INDEXES into that slot's own grab; Capture average is a smoothness dial, and nothing about it is local.** Rozaya's report was "the only thing I've done with it is set all 8 slots, painfully, by hand, to 6." **Design tell worth keeping: when a control needs an external tool to be usable in bulk, its granularity is wrong** — `tools/passage_set_capture_average.py` existed precisely because of this.
    - Implementation: slider 28 keeps its ID and its meaning changes. `@slider` stamps the slider onto all 8 bank entries every call (so the per-slot bank and the `@serialize` byte format are untouched, and a project from the per-slot build flattens to whatever the slider shows). The bank stamp also runs in `@serialize`'s read branch, so it converges whichever of REAPER's two restore paths runs first. New `capavg_dirty` flag splits the re-derive SCOPE: a Capture-point change still re-derives only the focused slot, a Capture-average change re-derives every captured slot.
    - **The tool KEPT its Morpher entry** — my first call to drop it was wrong. The global change fixed "set 8 slots inside the plugin"; it did nothing about "set it across 18 projects without opening each in REAPER," which is what the tool is actually for. It also got *more* reliable for Morpher: the slider now always wins, where before per-slot values in already-saved projects silently beat it. Docstring + `tools/README.md` rewritten to split Morpher (global, slider is truth) from Passage (per slot, slider only seeds projects predating the control).
    - Also filled a lockstep gap `f7dfbc0` left: **neither Capture average nor Overtone was documented in `docs/plugins/spectral-vowel-morpher.md` at all**, and both target lists still said six targets when the plugin has seven.

- **2026-07-27 (click fix ear-tested ✓ by Rozaya; the other three UNTESTED) — Spectral Vowel Passage: the click at slot changes, plus Capture average and Overtone.** Rozaya reported "a CPU-related bug in the engine that controls harmonics... it seems to happen at random," in a 5-instance project. It was not CPU. **Every slot handoff clicked, and had since the plugin's birth** — the two-oscillator-bank handover dropped the phases (full writeup in the "crossfade hands a source from one bank to another" gotcha above). Its loudness varies run to run because the step is the difference between two unrelated phase sets, which is precisely what made a once-per-handoff bug read as random dropouts. **Diagnostic lesson, and note where it points: the report was RIGHT** — a real bug, in the harmonics engine, varying run to run, all three confirmed. The one loose word was "CPU", and the failure was mine: I acted on the attached mechanism instead of asking what it SOUNDS like, which is one question and would have got there. **Ask for the observation; never discount the report.** (This entry was once summarised as "a listener's report is a symptom, not a diagnosis", which inverts it — it reads as doubt aimed at the person who was right. Removed 2026-09-03. The live rule is in `CLAUDE.md` under *How to work here*, and it is the same rule as *a plausible mechanism is not a finding*, which is aimed at me.) Three fixes and two features shipped (commits `0d66546`, `836c4c0`, `660b4a3`):
  - **Voice phase handover** (the click). Ear-tested ✓.
  - **`flush_accum_pending`** replaces `clear_accum` at the sequential-handoff flush — the anti-bleed fix from `811709f` is unchanged, but it now clears only the one grain-length window that can still be read instead of 131072 slots from inside a SINGLE sample. Generalisable: **an accumulator flush only has to cover [readpos, readpos+W); everything else is already-read zeros** — and do NOT reset the read pointer while doing a partial clear.
  - **Harmonic phase runaway.** Above `srate` the per-sample step exceeds TWOPI, the single-subtract wrap can't keep up, and `wtsin` indexes the sine table straight off that accumulator — so it read past the end of the table. Fixed by moving the phase advance *inside* the existing audibility guard, which also makes the loop cheaper. **Audit pattern: any `ph += inc; ph >= TWOPI ? ph -= TWOPI;` is only correct if `inc < TWOPI` is guaranteed — check what happens when a rate slider or drift target can push it past that.**
  - **Capture average** (slider 4, per slot, default 1 = unchanged) — closes the long-open wobble item in `docs/morpher-v2-slot-timing-design.md`. Single-frame capture froze that frame's per-bin scatter and the wash replayed it on every grain; Spread only ever blurred it. Now averages MAGNITUDES (not complex bins — that would be a comb filter) over K frames stepped by `WA/2`. **Because the blob stores `slotraw` and the analysis is re-derived on load, this reached every existing capture with no re-capture and no re-render.** Voice analysis deliberately left single-frame (exact harmonics, continuous phase, no scatter to freeze); stereo untouched (width is phase-side, and the magnitudes this changes are shared L/R — which is why the wobble sat centre-image).
  - **Overtone** (sliders 36-38, appended) — overtone / throat singing, from Rozaya wanting "a voice that *sounds* like it's singing 2 notes at once." They had stacked **20 Passage instances** chasing it; stacking structurally can't get there, because the cue is that the overtone shares every fluctuation of the fundamental. Passage's voice engine is already 64 partials at exact multiples of the detected f0, so it was three controls away. **Modelled as ATTENUATION of the other partials, never a boost of the chosen one** — that is what a tract resonance physically does, and it means the control can only make the voice quieter, which is an ear-safety requirement for a headphones user who can't see a meter. Harmonic 1 is exempt at any depth (it's the drone half of "two notes"). Overtone harmonic is a Drift/Ramp target — that's the melody, mouse-free — and fractional values are deliberate (at 7.5 the emphasis hands over between partials 7 and 8, as a real sweep does).
  - **The 20-instance experiment was carrying both bugs at 20x the dose**, in a project built specifically to sum things — worth re-listening to before concluding what it can't do.
  - **`tools/passage_migrate_sliders.py`** (was `passage_shift_fade_shapes.py`): a HOPS table walked in order, so a project two layouts behind migrates straight through in one run. All 29 Passage instances across 5 projects migrated 32→34→35. Slider IDs 36-38 were APPENDED, so Overtone cost no migration.
  - **Harmonic Sculptor is under an overhaul-or-drop question** — Rozaya wouldn't reach for it. See the banner in `docs/planned-features.md`; don't propose it as a prototyping surface.
  - **Open:** getting captures out of `@serialize` blobs as WAVs (and back in), plus a slot-contents text report for NVDA — written up in `docs/planned-features.md`. Also unmerged: this work sits on `feature/passage-and-melody-v2` (renamed from `feature/melody-phase-v2`, which had been carrying three Passage commits since before Melody v2 was added — the name was the inaccurate part, not the contents). The branch is a clean fast-forward from master, so `git merge --ff-only` lands it whenever the outstanding ear-tests pass: Capture average, Overtone, the Morpher click fix, and Melody Phase v2 itself. **Note master is ~37 commits ahead of origin/master** — the whole 2026-07 run is unpushed.

- **2026-07-10 (shipped **v2.18**) — Spectral Vowel Morpher crackle fix (point release, no other changes).** At Texture 0 the wash engine ran heavy per-grain FFTs on muted (×0) audio, tipping busy projects into real-time dropouts = non-clipping crackle on ~every slot. Gated grain synth on `wlevel > 0.0001`. Full writeup + the general pattern is in the "**muted/inaudible layers still cost CPU**" JSFX gotcha above (commit `1affa90`). Lesson kept because it generalizes to any plugin with a layer whose gain can hit 0.

- **2026-07-09 (ear-tested ✓, shipped **v2.17**) — Veil (`src/veil.jsfx`): mono→stereo "womb-heard" voice muffle; plus a morpher slot fix and a dyscalculia-principle sharpen.** Veil muffles a MONO voice like prenatal hearing (steep lowpass ~500 Hz, "speech from behind a veil"; newborns actually prefer a ~400 Hz-filtered mother's voice). **Two fully INDEPENDENT filter chains (L/R)**, each with its own cutoff + resonance, so it MANUFACTURES stereo width from a mono source: **width = the difference between the two cutoffs** (spectral decorrelation only, no phase/delay → mono-safe; a mono sum just averages the two rolloffs, no comb cancellation). Chamberlin SVF; **Slope** cascades 1–4 stages = −12/−24/−36/−48 dB/oct. Per-channel **Drift + Speed Ramp**, 4 targets (L/R cutoff, L/R resonance), suite "units match target" convention, drift period in seconds; positive cutoff ramp = the muffle "clearing" (gestational open). Path A `@init` (no `ext_noinit`; cfg-guarded banks), versioned `@serialize` (magic 3100000+N) + track-duplicate fix; cutoff/res coeffs recomputed per-sample. Manual: `docs/plugins/veil.md`.
  - **Why Veil is NOT the Resonant Sweeping Filter (don't re-litigate — this was worked through at length).** Sweep Filter = ONE moving band SHARED across the stereo field: its width is a *byproduct of the sweep* (stop the motion → width collapses), it's fixed at −12 dB/oct, and its L/R are phase-locked. Veil = a STILL, deep, wide muffle: width AT REST from fixed independent cutoffs, steeper slope, and — because its two channels are independent — their drifts wander apart so the **width itself breathes** (Sweep structurally can't do that). They also **stack** (Veil for character → Sweep for motion). General lesson: overlap between tools isn't the problem; a *shared center of gravity* is — fix it with distinct identities + a name, not by deleting the overlap. Hence the name **Veil** (a character name — "a thin thing you hear through"), replacing the placeholder "Womb Voice" (which read as "just another filter" beside the Sweep Filter).
  - **Also shipped this session:** (a) **spectral_vowel_morpher Capture slot 0-indexed** — was `1<1,8,1>` with `cap_slot = slider1−1`; the engine already ran 0-based, so dropped the −1 → `0<0,7,1>`, matching resonance_bank/suite selectors. Captures RELOAD INTACT (serialize is internally-indexed by slot; byte-format untouched); the only migration effect on old projects is the capture-slot CURSOR sitting one slot higher (cosmetic, self-correcting; a saved slot-8 lands on the same internal slot). (b) **Dyscalculia principle SHARPENED** (`docs/dyscalculia-accessibility-sweep.md` + memory): the barrier is **ARITHMETIC/CONVERSION, not numbers** — reading/setting/nudging a value is fine; the machine does any math. "Never make the user produce a number" was too broad and condescending. Canonical trigger from Rozaya: **`0.0625 ÷ 2` broke; `480 − 440 = 40` is fine** (decimal-with-no-magnitude + division + working-memory hold vs a round anchored subtraction). Do NOT "fix" access by hiding numbers behind mood-labels (a separate, already-rejected mistake). (c) **NVDA enum-labeling pattern:** unit in the param NAME, bare values in the list (`{-12,-24,…}Slope (dB/oct)`) so NVDA doesn't re-read the unit on every arrow-step. (d) **Deferred suite-wide decision:** whether to move all nested-selector Drift/Ramp from "units match target" (one amount slider whose number reinterprets per selector — the shipped convention across resonance_bank/melody/etc.) to normalized-% (machine scales per target). "Units match target" holds up because drift is tuned by ear; decide once, suite-wide, as part of the dyscalculia sweep.

- **2026-07-08/09 (ear-tested ✓, shipped **v2.16**) — three new plugins: `src/stereo-phaser.jsfx`, `src/dapple.jsfx`, `src/bubbler.jsfx`.** Born in one session. (Released as v2.16, not v2.15 — v2.15 was already the Spectral Vowel Morpher; the local clone's tags were stale so `git describe` mis-reported v2.14 as latest. **Lesson: `git fetch --tags` before assuming the next version number.**) Dapple + Bubbler are a **bubble pair, tuned for opposite material**: Dapple (generator, noise engine) for noise/broadband texture, Bubbler (effect, granular) for tonal sources — crossing them is janky (documented in both pages). Both carry a `//tags: bubble bubbles water …` line so a REAPER FX-browser search for "bubble" finds them despite the non-literal name "Dapple".
  - **Stereo Phaser** — swept-allpass phaser, 2–64 stages, stereo spread (per-channel LFO offset), feedback. **Lesson worth keeping:** the first attempt used a `(a + z⁻¹)/(1 + a·z⁻¹)` allpass with a positive coefficient — that parks the phase transition up near Nyquist, so it produced *no audible notches* (sounded like gentle stereo movement, not a phaser). Fix was to adopt the stock Cockos "4-Tap Phaser" form `(coef − z⁻¹)/(1 − coef·z⁻¹)` with `coef = (1−d)/(1+d), d = 2·fc/srate`, which puts the sweep in the audible band. **When building a filter, verify the frequency RESPONSE (notches form + move), not just that it's stable** — a "stable" check passed a silent-phaser bug through to the user's ears. Doc carries a REAPER auto-mute note: stacked identical high-feedback copies phase-lock and multiply resonant peaks until REAPER's runaway protection mutes the track.
  - **Dapple** — scattered-droplet texture *generator* (makes its own noise; Park-Miller per channel). Started as a water-synth attempt, became its own pointillist thing. Each event = a random low pitch that chirps upward as it decays, blended between a resonant-lowpass NOISE voice and a rising-sine TONE voice (the Farnell/Minnaert "plink"). **32-voice polyphony per channel** was the load-bearing fix: monophonic (one filter/channel) truncated overlapping bubbles — new events steal the *quietest* voice so nothing audible is cut. Adds to the track (layers). Real water needs the tonal chirp, not noise — noise-through-resonance only ever gives fizz/steam. **Later add — `Excite from input` (slider11):** blends the noise voice's excitation from internal noise → the track's audio, so Dapple doubles as an EFFECT on a noisescape/broadband source (safety soft-clip gated to `inp>0` so generator mode stays byte-identical). It's the noise-input counterpart to Bubbler's tonal-input — Dapple for broadband, Bubbler for pitched.
  - **Bubbler** — granular "bubble" *effect* (input-excited sibling to Dapple). Scatters a tonal input into rising pitched droplets *made of the source*: each event captures a ~300 ms grain, resamples it to a random transposition, and chirps the pitch up over the bubble's life. **Design arc worth keeping** (each step was an ear-test failure that taught the next): (1) resonant filter *on the input* can't impose a rising pitch — the source's own spectrum dominates, so it only "bubbled" at max resonance; the rise has to be *created*, not filtered. (2) A short impulsive kick into the filter bubbled across the res range but still couldn't rise in pitch (filters colour, they don't transpose). (3) Granular resample *does* transpose — but play-once grains get consumed fast at high pitch, cutting bubbles short (and clicking). (4) **Two-tap triangular-crossfade seamless loop** is the fix: the grain loops under the read pointer so a bubble sustains the full envelope and completes the full rise at any transposition. Negative Transpose (−24 to −36 st) on a sustained tone = the "underwater" sound Rozaya loved. Soft-clip (`x/sqrt(1+x²)`) bounds the wet, `(1−res)`-style level worries gone with the filter. 16 voices, quietest-steal. **Process lesson reinforced: validate the CHARACTER on a cheap/limited version before building the heavy engine** — the overlap-add loop only got built after the play-once version confirmed the vibe was right.

- **SHIPPED v2.11 (2026-06-26, ear-tested ✓) — sample-based render-and-loop pipeline; new Sustain Looper + graduated Harmonic Sculptor.** The original breathed-vowel goal (synthesize vowels from scratch) was re-confirmed a dead end in real-time JSFX — both the Klatt-style formant filter and the Pink-Trombone waveguide ceiling out on naturalness (see `archive/exploration/`). The win was pivoting to **sample-based**: design or record a sound → render a short WAV → loop it. Two plugins shipped:
  - **`src/sustain_looper.jsfx`** (NEW — "the sampler") — loads a WAV via file-selector slider (drop WAVs in `<REAPER resource>/Data/glasswings_samples/`), **crossfade-loops** a steady region so loop points need NO visual matching (set by ear, raise Crossfade till seamless — the accessibility win over a normal sampler sustain loop). Plus a true-detune multi-voice **ensemble** (Voices 0-12 + Spread) for lush choir-like width. Loop STEADY material — baked-in vibrato/swell telegraphs the loop; broadband/breath sources loop near-invisibly, pure tones are hardest. Outputs the loop only; needs the transport rolling (or track armed+monitored) to sound.
  - **`src/harmonic_sculptor.jsfx`** (GRADUATED from `archive/.../standalone_drones`) — additive synth, the sound-design front end: sculpt a timbre/vowel by ear from 64 harmonics → render → loop. Bug-swept; made **stereo** (bounded decorrelated per-harmonic phase = diffuse width, mono-safe, switchable via Output mode Mono/Stereo); added **Square + Pulse** (with Pulse-width re-stamp) to match Polyrhythm's 14-wave palette; base-wave changes now use a ~30 ms click-free crossfade (instant) instead of the slow Attack/Release morph, onset swell preserved.
  - **Archived (functional/known, not released):** `breath_granulator` (granular texture — works, but granular = wash, not clean pads; revivable), `smear_stretch` (Paulstretch-style spectral stretch — works, original CC0 reimpl of the public-domain algorithm, but redundant with PaulXStretch which Rozaya can drive), `breathed_vowels` + `tract_vowels` (parametric vowel-synth dead ends).
  - **Workflow facts worth keeping:** pitch-shifting one vowel sample slides it through neighbouring vowels (formants ride with pitch, tape-style) — a few base samples cover a continuum. Aliveness comes mostly from the SOURCE, not the plugin. Claude can generate CC0 source samples on demand (Python additive + FFT-shaped noise); a CC0 sample pack to ship with the looper is an open idea. Two new JSFX gotchas surfaced (sample loading; `fft_permute`) — see the gotchas section above.

- **DONE 2026-06-15 (ear-tested suite-wide ✓) — v2.9 render/alt-tab stale-state regression + two bugs found alongside it. Fixed across every active plugin on branch `fix/v2.9-render-and-serialize` (one+ commit per plugin; NOT yet merged/tagged).** Full writeup in [`docs/v2.9-render-state-bug.md`](docs/v2.9-render-state-bug.md) (read the ✅ STATUS block at top). **Three distinct fixes shipped this sweep:** (1) **Render — Path A** (drop `ext_noinit`; guard the per-target drift/Speed-Ramp CONFIG bank(s) behind a one-time `*_cfg_inited` flag; move runtime to the unguarded `@init` path; delete the `@sample` transport-edge handler). REAPER **does** re-run `@init` on offline-render transport start, so this restores v2.8 render behavior AND fixes alt-tab resume, with release tails intact (nothing resets on STOP). Applied to all 12 active rate-bearing plugins. (2) **Serialize version guard** — only where a serialized count changed: melody (10→28, dev-only) and polyrhythm (13→24, pre-v2.10); resonance-bank got a brand-new versioned `@serialize` (it had none — closes a pre-existing band-persistence gap). Pattern: lead the stream with a count-encoded magic so mismatched/legacy blobs fall through to defaults instead of mis-reading. Plugins whose format never changed were left alone (a guard would needlessly reset existing drift configs). (3) **Park-Miller PRNG** — separate latent bug surfaced during ear-testing: breath/heartbeat/womb-v3's decorrelated R-channel noise used LCG multiplier 22695477, which overflowed EEL2's float64 2^53 limit → periodic tone + DC offset on R only (audible "swung" wobble). Replaced with Park-Miller/MINSTD (see the LCG gotcha above). **Path B** (stop-edge reset) stays known-bad — it cut release tails. **Womb v1/v2 archived** (legacy, frozen-as-shipped with the PRNG bug). **Remaining:** merge `fix/v2.9-render-and-serialize` to master + tag/release (this also finally releases the un-tagged polyrhythm v2.10 expressive-drift `7955e85` and melody expressive-drift `57671a3` work, now ear-tested by virtue of this sweep).

  - **JSFX gotcha surfaced here — version your `@serialize` stream.** `file_mem`/`file_var` on handle 0 share ONE sequential read cursor across all calls in `@serialize`. If you ever change how many values you serialize (more targets, more fields, an added array), an old project's blob mis-aligns: reads run off the end of one array into the next, silently fabricating garbage state (here: phantom drift that wrecked timing, with NO error and NO visible slider change — the scrambled values live only in the memory bank, not in sliders, so the user correctly says "I never configured this"). REAPER serializes as float32, leaves dest unchanged past EOF, and pops no error on a short read. **Always lead a multi-value `@serialize` with a version/count marker** (`magic = 1000000 + count; file_var(0, magic); magic == expected ? ( ...read arrays... );`) so format changes degrade to defaults instead of scrambling. Pick a marker > the max plausible first-field value and ≤ 2^24 (float32-exact); encoding the count makes every format version mutually exclusive and forward-safe. Symptom signature: audible state the user never configured, appearing right after a plugin update, with the relevant sliders all at default.

- **Polyrhythm Phase v2.10 — expressive drift + multi-target Speed Ramp** (committed `7955e85`, NOT ear-tested, NOT released). Motivated by REAPER automation envelopes being *reachable but overwhelming* under OSARA — drift (repeating wander) + Speed Ramp (one-time ride) are the in-plugin automation substitute, so both now cover the same unified 24-target list. **Get this rationale right, it keeps getting mis-stated:** OSARA has full envelope support (alt+L / alt+shift+L select envelope, alt+K / alt+J step between points, shift+E insert, ctrl+alt+J cycle point shape, plus automation items and context menus). Nothing here is inaccessible. The problem is that every one of those commands is **serial and single-point** — you traverse a curve one point at a time with no way to perceive it whole, so building a 40-minute wander means inserting and shaping dozens of points while holding the entire intended shape in working memory. Same family as the dyscalculia rule (`docs/dyscalculia-accessibility-sweep.md`): the barrier is the holding-and-assembling, not the reaching. Drift/Speed Ramp invert it — you state the *behavior* (up amount, down amount, period, shape) and the machine generates the curve. Two functional wins that follow, and they'd hold even for a mouse user: an envelope has a length whereas drift runs indefinitely (an 8-hour sleep render is not a drawable envelope, and Random shape never repeats), and drift travels with the plugin instance between projects instead of living in one track's parameter lane. Rozaya designed around the overwhelm deliberately, on the assumption others would hit it too — it was a usability call, not a workaround for an access failure. Drift grew 13→24 (added per-voice Gain dB 13-20 / Depth dB 21 / Attack% 22 / Release% 23; bank re-spaced 16→32 slots/field like melody). Speed Ramp went single-target→nested-selector (new slider79 target selector; per-target `by` bank `speed_ramp_by_mem` at 8768; Base Rate stays the proportional ratio via `combined_scale`, the other 23 ride as additive offsets FOLDED into `target_drift_offset[1..23]` right after the drift loop so consumption sites need no change). Migration: v2.9→v2.10 drift configs reset (re-spacing); Speed Ramp Base-Rate survives (selector defaults to Base Rate, slider65 captures into the bank). **Next: ear-test (per-voice Gain swells, multi-target Speed Ramp ride, v2.9-project Base-Rate-ramp-survives-on-load), fix the render bug above, THEN tag v2.10.** Melody got the same expressive drift earlier (`57671a3`, 28 targets) — it has no Depth (no tremolo).

- **Suite-wide Speed Ramp sweep — every plugin to signed-delta + freeze-gate engage + transport-only restart** (2026-06-10, shipped same session). Ports the Speed Ramp design Womb v3 worked out (multi-target nested selector, signed `by` amount, engage as freeze/resume gate, transport-only ramp_t reset) to every other plugin in the suite. Three ear-test confirmations along the way (breath_gen multi-target additive ✓, shepard-scale single-target additive ✓, and a final batch of 3 including polyrhythm_phase ✓) validated the pattern category by category.
  - **No multipliers anywhere in the suite anymore.** Earlier in the session I tried to keep multiplier-factor form for plugins with wide-range rates (Shepard Tone, Full Feature Tremolo, Sweep Dwell — Rate Value spanning 0.001-1000 across Hz/Sec/BPM modes). Rozaya pushed back: "The multiplier is a dyscalculia accessibility problem." Reversed that call — every Speed Ramp in the suite now uses signed delta. Internal representation varies (some plugins compute a multiplicative ratio behind the scenes — see "Diverges" group below), but the UI is uniform: `Speed ramp by N` in the rate's natural unit.
  - **Three implementation shapes across the suite, varying in internal audio-path math:**
    - **Multi-target additive (closest to Womb v3 pattern):** breath_gen (4 segments), heartbeat gen (Heart BPM / S1-S2 gap / Breath HRV depth / Random HRV depth), sweep-dwell-filter (4 dwells). Per-target memory bank, parallel ramping, selector-saves-and-loads. Womb v3's code was the reference implementation; these match its shape.
    - **Single-target additive (simpler):** rhythm-track (Tempo BPM), shepard-scale (BPM). No selector, no memory bank — `slider17`/`slider52` is the `by` directly. Speed Ramp offset added at consumption site (effective_bpm = baseline + drift + speed_ramp_offset).
    - **Single-target ratio-based (diverges from Womb v3):** shepard-tone, Full Feature Tremolo, full-feature-sweeping-filter, polyrhythm_phase, melody_phase. Audio path uses rate-as-multiplier at multiple use sites, so the additive `by` is converted to a multiplicative ratio internally (`speed_scale_current = effective_rate_hz / base_rate_hz`). User experience stays signed-delta; the audio-path translation is new per-plugin code that isn't in Womb v3. Polyrhythm Phase additionally uses this ratio to scale ALL 8 voices proportionally (preserving rate relationships between voices — V1 at 60 and V2 at 60.5 both halve to 30 and 30.25, keeping the slow beat between them coherent). Melody Phase additionally has mode-aware inversion for Seconds mode (period unit flips the ratio direction).
  - **Engage semantics fix is universal.** Every plugin: `slider_engage` is a freeze/resume gate, NOT an edge trigger. While On, `ramp_t` advances 0 → 1 over the duration; while Off, it freezes wherever it is and resumes from there on re-engage. The OLD `slider_engage && !engaged_last` edge-detection pattern (which silently re-fired on every slider change after a transport play) is gone from every plugin. Only the transport play edge (`play_state > 0 && last_play_state == 0`) resets `ramp_t` and `speed_ramp_delay_elapsed`. This was discovered via Womb v3's third ear-test ("on every change, the ramp restarts. It should only be restarting on transport"). All `speed_ramp_engaged_last` and `speed_scale_start` variables removed from every plugin.
  - **`Speed ramp by` is the slider label**, not "Speed ramp amount." Reads as a complete sentence with the selector (*"Speed ramp by -35, target Heart BPM"*); the preposition carries the signed-delta semantic without needing an explanatory hint. The word "target" is reserved for the selector slider where applicable.
  - **Start delay added everywhere.** Every plugin's Speed Ramp now has a `Speed ramp start delay (minutes)` slider — `0–60 min, default 0`. Waits N minutes after engage before `ramp_t` starts advancing. Useful for "let me fall asleep first, then begin the wind-down." Slider position varies per plugin (placed wherever a gap existed near the existing Speed Ramp block, or at the next free slot after drift if no nearby gap).
  - **Mode-direction asymmetry to be aware of for users.** For plugins with multi-mode Rate Value sliders (Shepard Tone, Full Feature Tremolo, Sweeping Filter, Polyrhythm Phase, Melody Phase): in **BPM and Hz modes**, negative `by` = slower (intuitive). In **Seconds mode** (where Rate Value is a period in seconds), positive `by` = longer period = slower (flipped). The user has to know which mode they're in. Documented per-plugin in the manual.
  - **Migration story for v2.7 → v2.8 users.** Old plugins had `Speed ramp target (multiplier) 0.1–4.0` at the first Speed Ramp slot. In the new plugins that slot is either a selector index (0-N integer) or a signed delta (-X to +X range). Old projects' multiplier value gets interpreted as either a low selector index (typically target 0 = first target) or as a tiny delta — either way, Speed Ramp produces no effect on reload until the user reconfigures. No catastrophic breakage; just "Speed Ramp is effectively off" semantics.
  - **Inconsistency surfaced (not fixed):** Womb v3 uses the nested-selector drift pattern (7 targets, per-target memory bank, all run in parallel) — the new design. Every OTHER plugin still uses the older flat 2-source drift pattern (musical drift up/down/period + slow drift up/down/period + one shape selector, affecting only the plugin's primary rate). The suite-wide drift sweep is now the planned next undertaking — see "Planned: Drift nested-selector sweep across the suite" below.
  - **Per-plugin commit list** (in order): `feat(breath)`, `feat(rhythm-track)`, `feat(shepard)` (both tone and scale, bundled), `feat(tremolo,sweep-dwell)` (first pass — multiplier kept), `feat(heartbeat)`, `feat(shepard-tone,tremolo,sweep-dwell)` (second pass — multiplier removed after dyscalculia feedback), `feat(sweeping-filter,polyrhythm,melody)`. Each commit message names the slider IDs it added and the implementation shape (additive vs ratio-based).
  - **CLAUDE.md gotchas + slider-rule additions surfaced.** Slider ID renumbering safety (didn't move existing IDs — only added new sliders at gaps or after drift block). Layout-vs-tab-order constraint (REAPER UI displays sliders in numeric order regardless of declaration order in the file). Per-plugin Speed Ramp slider layouts in the manual — each plugin has its own slider IDs documented because they vary based on what gap was available.

- **Womb Sound Generator v3 — nested-selector drift + sigh mechanism + signed-delta Speed Ramp** (2026-06-09). New ship: `src/womb_sound_generator_v3.jsfx`. Sibling-file pattern alongside v2 (v2 stays in place for projects already built on it). Three substantive changes vs v2:
  - **Drift system rebuilt around the resonance-bank nested-selector pattern.** v2's flat Heart+Breath drift block (6 sliders + shape covering 2 targets) collapsed to a single target selector + up + down + period + shape (5 sliders covering 7 targets: Heart BPM, S1-S2 gap, Inhale Duration, Top Pause, Exhale Duration, Bottom Pause, RSA depth). All 7 targets run in parallel; only one's settings visible at a time per the selector. Memory banks at 8192+ store per-target up/down/period/shape/phase/prev/curr/offset, 16-slot aligned for future growth. `@serialize` persists configurations across project save/load (without it, only the most-recently-edited target's slider values survive). `ext_noinit = 1` preserves drift state across transport play.
  - **Periodic sigh mechanism (sliders 60-61: interval minutes, depth multiplier).** Pure wall-clock timer. On 3→0 transition, if timer crossed threshold, sigh_active flips to 1 for the full duration of the next breath. Multiplier applies to ALL FOUR segments uniformly (not just inhale) so the entire sigh breath stretches in lockstep, preserving I:E ratios. Multiplier applies at each state-entry on top of the currently-drifted segment length — sigh inherits live drift, doesn't lock to a snapshot.
  - **Speed Ramp — nested-selector + signed delta + all five sliders grouped together** (refined late in the session after first-pass ear-test feedback). 7-option target selector matching the drift target set (Heart BPM, S1-S2 gap, Inhale, Top pause, Exhale, Bottom pause, RSA depth). The amount slider is a **signed delta in the selected target's natural unit** — 0 = no change (safe default; engaging at 0 does nothing), negative = decrease the parameter (slower heart, shorter inhale), positive = increase. Range `-300 to +300, step 0.1` covers every target's range needs. Formula: `offset = ramp_t * slider49` (no baseline subtraction — the slider IS the delta). All five Speed Ramp sliders live in one place at the top of the variable block: `slider48` "Speed ramp target" (selector), `slider49` "Speed ramp by" (signed delta), `slider50` "Speed ramp duration", `slider51` "Speed ramp engage", `slider52` "Speed ramp start delay". Slider 49's visible label is "Speed ramp by" rather than "amount" because "Speed ramp target" already uses the word "target" — `by` reads as a complete sentence with the selector (*"Speed ramp by -35, target Heart BPM"*) and the preposition implicitly carries the signed-delta semantic. The early-session iteration had them split (selector + duration + engage + start delay at 48-51, target value way down at slider 61 with thirteen unrelated sliders between) AND used destination-value semantics (with default 0 meaning "ramp heart to 0 BPM" = silence on engage). Both were fixed in the same pass — Rozaya's reaction was *"can we put the speed ramp sliders in one place? And add numbers below 0? Otherwise it just gets faster lol"*. Renumbering was safe because v3 had never shipped — sliders 49→50 (duration), 50→51 (engage), 51→52 (start delay), 52→53 (BPM rescale), 53-57→54-58 (drift block), 58→59 (RSA), 59-60→60-61 (sigh); old slider 61 (target value) became the new slider 49 (amount with delta semantics). Per-target stored amounts via `speed_ramp_target_value_mem[7]`; `@serialize` persists across save/load. **All targets are additive** — selecting Heart BPM with amount -35 ramps just the heart down 35 BPM; the breath cycle stays at its base rate. **All 7 ramps run in parallel like drift** — the @sample block reads each target's offset directly from the memory bank (`speed_ramp_target_value_mem[i] * speed_ramp_t`) rather than from slider49, so switching the selector doesn't stop any running ramp; it just changes which target's amount you're editing. The first implementation had this wrong — it zeroed all 6 non-selected offsets each sample, which meant flipping the selector silenced the previously-engaged ramp (Rozaya caught it on ear-test: "I set a heartbeat ramp. As soon as I switched the selecter, the ramp stopped. Switched back to the heartbeat ramp and it picked up as if it hadn't stopped"). The fix is the right design: this enables the "configure Heart BPM by -35 AND Inhale by +4, engage, get a coordinated multi-parameter wind-down over the same duration" workflow that's the natural fit for sleep use. Speed Ramp + Drift + Sighs compose at consumption sites: `effective_inhale_sec = baseline + drift_offset + speed_ramp_offset`, sigh multiplier applied on top. v3 also **removed the `combined_scale` variable entirely** — drift phases and sigh timer no longer scale with Speed Ramp (drift periods are now in true heartbeats/breath cycles always; sighs are pure wall-clock minutes). Transport play (`play_state > 0 && last_play_state == 0`) resets `speed_ramp_t` and `speed_ramp_delay_elapsed`. **Engage is a freeze/resume gate, NOT a restart trigger** — there's no engage-edge detection at all. The only thing that resets `speed_ramp_t` is the transport play edge. This came out of a third ear-test where Rozaya found the ramp was restarting on every slider change after transport had played once (*"On every change, the ramp restarts. It should only be restarting on transport"*). Root cause: the earlier design zeroed `speed_ramp_engaged_last` on transport reset to "fake an edge for the next @slider," but that meant the NEXT @slider invocation (for any reason — selector change, anything) would detect `slider51 && !engaged_last` as an Off→On edge and re-reset the ramp. Fix: removed the engage-edge logic entirely. Engage now just gates whether ramp_t advances in @sample; it doesn't trigger restarts. Drift phases and sigh timer deliberately NOT reset on transport; they're "lived" state we want continuous across play presses.

- **Design point: bloodflow as an independent layer** (flagged 2026-06-09, no work planned). Bloodflow is currently phase-locked to heart in Womb (all versions): `bf_cycle_pos = hb_phase / cycle_len`, no separate phase counter, no bloodflow rate slider, no bloodflow drift target, no bloodflow Speed Ramp target. This is biologically correct for the womb context (normal physiology: cardiac output IS the pulse wave). The design tradeoff captured here is whether bloodflow should EVER be exposed as an independently-modulatable layer — would need its own phase counter, its own rate slider, its own drift target, its own Speed Ramp target. **Use cases that might want this:**
  - **Plugin-internal:** bloodflow drift on a slightly different cycle than the heart (modeling vasomotor tone wandering at a different rate than cardiac rhythm — real physiology, ~0.1Hz Mayer waves are different from heart rate).
  - **Cross-suite generalization:** if another suite plugin grows a "pulse-style" amplitude envelope layered on top of a rhythm source, it'd inherit the same locked-vs-independent question Womb has now.
  - **Pathology modeling:** LVAD (continuous pump, no pulse), AV dissociation (pulse rate ≠ heart electrical rate), pacemaker pacing patterns. Probably not within scope for a "womb" plugin, but the architecture decision applies anywhere pulse-flow is modeled.
  
  **Current answer:** locked. **Open if:** someone wants pulse-vs-heart decoupling for a real perceptual reason, OR if the bloodflow modeling extends to plugins beyond Womb where the heart isn't necessarily the master. The slider+memory cost is non-trivial (one selector option + storage in every target list across drift and Speed Ramp); only worth doing if a real use case justifies it. Flagged here so future sessions know the question exists and can evaluate it against whatever concrete need surfaces.
  - **As of 2026-06-09, Womb v3 has not yet been tested by ear.** All the v3 changes (nested-selector drift, sigh mechanism, nested-selector Speed Ramp) landed in code in a single session and need validation. The drift system and sigh mechanism are conceptually proven (drift mirrors resonance bank, sighs are mechanical), but the Speed Ramp redesign in particular is a fresh pattern that hasn't been run through real audio yet. Suite-wide propagation (see below) should NOT happen until Womb v3 has been ear-tested and any issues fixed there first.

- **SHIPPED 2026-06-12: Drift nested-selector sweep across the suite — DONE.** All 10 rate-bearing plugins converted from the flat 2-source drift to Womb v3's nested-selector pattern. One commit per plugin (manual section bundled): breath-gen (4 targets) `e9db305`, heartbeat (4) `b285560`, rhythm-track (2) `a06ff95`, shepard-scale (4) `d711c52`, shepard-tone (11) `6e7edb1`, tremolo (6) `854952d`, sweeping-filter (6) `bf846e5`, sweep-dwell (6) `d4178a7`, melody-phase (10, then +18 expressive targets → 28) `56e6702`+`57671a3`, polyrhythm-phase (13) `c762dc8`. Each ear-tested by Rozaya before/at commit. The planning detail below is preserved as reference; deltas from the plan and lessons learned are captured in this banner.
  - **Universal pattern (matches Womb v3 exactly):** 5 sliders per plugin (target selector + up + down + period + shape), per-target memory bank (8 fields × N targets, 16-slot-spaced — EXCEPT melody at 32-slot spacing because its 28 targets exceed 16 and would overflow), `@serialize` of the config bank, `ext_noinit = 1` so the bank survives transport, all targets drift in parallel, selector only chooses which target's config is on the visible sliders. Sliders reuse the old flat-drift IDs (net −2 per plugin); old projects reinterpret garbage into the new selector/amounts → "drift effectively off until reconfigured" (Rozaya accepted this; "I never used them and doubt others have").
  - **Transport reset is now uniform suite-wide and it's a REAL behavior change for some plugins.** Every converted plugin resets drift CYCLE state (phases/prev/curr/offset → 0) on the transport play edge while preserving drift CONFIG. Plugins that previously had NO `ext_noinit` (rhythm-track, shepard-scale, shepard-tone, tremolo, sweeping-filter, sweep-dwell, melody, polyrhythm) gained it here — which means the "clean restart on play" they used to get free from `@init` re-running is now done by an explicit comprehensive transport-edge reset (state machines, filter banks, gates, smoothers, noise seeds, chorus buffers, etc.). This was the riskiest part of each conversion. Drift restarts at phase 0 on play, continues across stop, starts fresh on render — "like any other synth would" (Rozaya's spec). Sine/Triangle renders are deterministic; Random is not (uses `rand()`, accepted).
  - **Two latent bugs flushed out by the ear-testing** (both fixed as standalone commits, independent of the sweep): `tempo` is a reserved JSFX system variable — rhythm-track's master Tempo slider had been a silent no-op since initial release (`ea8f201`, see the reserved-name gotcha above). And shepard-tone Independent-mode rate of 0 clamped to a creep/1000Hz-sweep instead of "no sweep" (`4da88e2`). Pushing sliders to their edges during drift ear-tests is what surfaced both.
  - **Per-plugin target counts diverge from the bolded "minimum viable" plan below** — every plugin got its full meaningful target set, not just the minimum. Notable: melody-phase grew beyond its drift targets into an EXPRESSIVE set (per-voice Gain + per-voice Note duration + Attack%/Release%, 28 targets total) after Rozaya asked "what would make a sequence feel like a breathing piece of music" — dynamics (gain) were the missing ingredient. Gain drifts per-sample (continuous swell); Note duration / Attack / Release are sampled once per note at trigger (articulation, not mid-note movement). That granularity split is the model for any future "expressive drift" on a sequencer plugin.
  - **Ratio-vs-additive audio-path split** (same as the Speed Ramp sweep): rate-type targets in plugins whose audio path uses rate-as-multiplier (shepard-tone, tremolo, sweeping-filter, melody, polyrhythm) convert the additive `by` offset to a multiplicative ratio internally, which also handles the BPM/Hz-vs-Seconds mode-direction asymmetry for free. Additive-on-segment targets (breath segments, sweep-dwell dwell phases, heartbeat) just add in their native unit at the consumption site.
  - **Open follow-ups:** none blocking. Not yet tagged/released — Rozaya to decide the version (the notes elsewhere reference v2.9 as the target). Womb v1/v2 deliberately untouched (legacy). Resonance Bank already nested. Womb v3 got the transport-reset fix retrofitted (`4ca7e56`) so its drift now restarts on play like the rest of the suite (it previously persisted drift across transport — the old "lived" behavior Rozaya rejected as "really weird on play/stop").

  **Original planning detail (2026-06-10) — preserved as reference:** Womb v3 introduced a nested-selector drift pattern: one target selector (slider 54 in v3) + per-target up/down/period/shape (sliders 55-58), covering 7 wander targets in parallel. Same shape Resonance Bank uses. Every OTHER plugin in the suite still uses the older flat 2-source drift design: musical drift up/down/period + slow drift up/down/period + one shape selector, all affecting the plugin's single primary rate. This sweep ports the suite to Womb v3's pattern.

  **Motivation.** Three reasons surfaced in conversation:
  1. **Consistency.** Womb v3 is the odd one out right now — its drift looks totally different from every other plugin in the suite. Surfaced during the Speed Ramp sweep when Rozaya asked "why did musical and slow drift survive here? How do they even tie into the work we just did, I'm lost." The architectural inconsistency is real and worth resolving.
  2. **Cogacc/discalculia win.** The nested-selector pattern matches the Speed Ramp design that just shipped: one selector + a small set of value sliders that adapt to whichever target you're editing. Less stuff on screen at once, value-IS-the-thing semantics throughout.
  3. **Polyrhythm Phase specifically would benefit.** Rozaya flagged this directly: "Polyrhythm feels like it could do with a selector and drift thing like womb has." Polyrhythm's drift currently only modulates the base rate; a multi-target drift selector would let it wander pan, tremolo rate, voice rates, etc. independently — which fits its multi-voice character.

  **Per-plugin design — what each plugin's Drift selector should look like.** Match the Speed Ramp selector targets where possible (and add other meaningful targets the plugin has). Items in bold are the "minimum viable target list" for that plugin; items not bolded are optional adds:

  | Plugin | Drift targets |
  |---|---|
  | Womb v3 | **already done** ✓ (7 targets) |
  | Womb v1/v2 | (legacy, not changed — they have v2's flat 2-source drift, leave it alone) |
  | Heartbeat Generator | **Heart BPM, S1-S2 gap, Breath HRV depth, Random HRV depth** |
  | Breath Generator | **Inhale, Top pause, Exhale, Bottom pause** |
  | Polyrhythm Phase | **Base Rate, per-voice rates, Pan Base Rate**, Pan Increment per Voice, Binaural Beat, Tremolo on-duration |
  | Melody Phase | **Rate Value, per-voice timings, Pan rate** |
  | Rhythm Track | **Tempo BPM**, Swing amount |
  | Shepard Scale Generator | **BPM**, Note Length %, Attack %, Release % |
  | Shepard Tone Generator | **Rate Value**, per-voice rates, Fade In %, Fade Out % |
  | Full Feature Tremolo | **Rate Value, Depth dB, Pan Sweep Rate**, On Duration %, Attack %, Release % |
  | Resonant Sweeping Filter | **Sweep Rate, Frequency Low, Frequency High, Pan Sweep Rate**, Resonance, Wet/Dry |
  | Sweep Dwell Filter | **High dwell, Fade down, Low dwell, Fade up, Pan Sweep Rate**, Resonance |

  Some plugins legitimately have a lot of meaningful targets (Polyrhythm Phase, FFT, Sweeping Filter, Sweep Dwell). The pattern handles arbitrarily many targets — slider count stays at 5 (selector + 4 drift sliders) regardless of how many targets there are.

  **Implementation pattern** (based on Womb v3's drift code as the reference implementation, which itself mirrored Resonance Bank's pattern):
  - **Slider layout: 5 drift sliders grouped together in tab order** (target selector + up + down + period + shape). For each existing plugin: repurpose the current flat-drift sliders. Current shape is 7 sliders (musical_up, musical_down, musical_period, slow_up, slow_down, slow_period, drift_shape); new shape is 5 sliders (target_selector, drift_up, drift_down, drift_period, drift_shape) — net 2 fewer drift sliders per plugin. The OLD musical-vs-slow distinction goes away (the nested-selector pattern doesn't have it); if both musical-feel and wall-clock-feel drifts are wanted, the user configures two different targets with very different periods (one in cycles, one in minutes — see period units below).
  - **Period units auto-match the target.** In Womb v3: heartbeats for Heart BPM and S1-S2 gap; breath cycles for the four breath segments and RSA depth. For other plugins: use the natural cycle unit of each target (BPM-driven → beats; rate-driven → cycles of the plugin's primary rate; "wall-clock-style" targets → minutes — though this last case may not exist for most plugins). Document per-plugin in the manual.
  - **Memory bank for per-target drift configs.** Up amount + down amount + period + shape + phase + (random-shape state: prev_target + curr_target) + offset = 8 fields per target. Each field array is 16-slot-aligned for future growth. Total memory needs: N_TARGETS × 8 slots = up to 16 × 8 = 128 slots, comfortably within free memory above 8192.
  - **@slider target-selector save/restore.** Same pattern as Speed Ramp: when the selector changes, save current slider values into the OLD target's bank slot, then load NEW target's bank values into the visible sliders. When selector hasn't changed, capture live edits to the current target's bank. This is the well-tested pattern from Womb v3 (which itself fixed an earlier bug Rozaya caught — selector switching shouldn't STOP any running drift).
  - **@sample loops over all targets every sample**, advancing each target's phase counter and computing its current offset. Each target's offset is then consumed at its specific audio path use site (effective_X = baseline + drift_offset[t] + speed_ramp_offset). All targets drift in parallel; selector is never referenced in @sample.
  - **Shape options match Womb v3.** Sine (smooth wander), Triangle (linear ramps with turnarounds), Random (value noise that interpolates smoothly between random targets at each period boundary, with per-target random state). Each target picks ONE shape.
  - **@serialize the memory bank** so per-target configs survive project save/load.

  **Polyrhythm Phase specifically — Rozaya's flagged interest.** Pol' currently has a flat drift that affects only the base rate. A nested-selector drift would unlock:
  - **Base Rate drift** (today's behavior — keep as one target).
  - **Per-voice rate drift** — each of the 8 voices could have its own drift configured independently. Each voice already has a "Drift / Rate" slider (slider22 for V1 in Drift mode, etc.); the drift selector would let you wander each voice's rate around its base. This is the heart of polyrhythmic feel — voices drifting against each other at slightly different rates.
  - **Pan drift** — wander pan position across the stereo field.
  - **Binaural Beat drift** — wander the L/R offset slowly. Subtle but musical.
  - Polyrhythm Phase would probably want 8-12+ drift targets after this sweep. Larger target list than Womb v3 but the pattern handles it.

  **Migration story for v2.8 → v2.9 users.** Existing flat-drift settings (musical_up, musical_down, musical_period, slow_up, slow_down, slow_period, drift_shape values) need a re-interpretation. Cleanest is to migrate musical → first drift target (period in cycles), slow → second drift target (period in minutes) — automatic on project load. But this requires migration code per-plugin; alternative is just resetting drift to defaults on plugin update and asking users to reconfigure. Decision deferred until implementation.

  **Timing.** Plan in this file. No external dependency — the Speed Ramp sweep validated the broader engage-as-gate / transport-only-restart pattern, and the nested-selector drift pattern is already shipping in Womb v3 and Resonance Bank. Pick this up as a focused session when Rozaya has the bandwidth — probably a half-day to a full day across ~10 plugins. Per-plugin commits + ear-test cadence (similar to the Speed Ramp sweep).

- **Resonance Bank — 16-band configurable filter with multi-target drift** (2026-06-05). New ship: `src/resonance_bank.jsfx`. Documented in the manual under Effects. Goes alongside Sweeping Filter / Dwell Filter / Tremolo as the suite's fourth Effect. Major plugin, 17 sliders, nested selector pattern. Long session arc — most of the work was exploration that didn't ship.
  - **Architecture:** 16 parallel bandpass filters (or 16 serial peaking EQ biquads — Mode slider switches) with stereo processing, asymmetric per-band widths (Width up + Width down in Hz), cascade-order rolloff (1/2/4/8 stages giving -6/-12/-24/-48 dB/oct slopes in parallel mode), per-band drift modulation on any combination of 5 target parameters (Frequency, Width up, Width down, Gain, Pan), and proper dB gain (-60 to +24 dB, -60 = off). On load every band is at -60 dB so output equals input × Wet/Dry; user activates bands one at a time.
  - **Selector pattern is nested.** Outer selector picks band (0-15); inner Drift target selector picks which of that band's parameters the drift sliders are configuring. Each (band, target) has its own up/down/period/mode/shape stored independently. Up to 5 simultaneous drifts per band. Slider count stays at 17 regardless of band count or drift target count — that's the accessibility win over ReaEQ-style "every band's parameters always visible." Memory banks hold all the configurations.
  - **Why both filter topologies in one plugin.** Parallel bandpass selects frequency slices and sums — the "voice" model, good for windscapes, vocoder-like work, breath-shaping. Serial peaking EQ boosts/cuts on the running signal — the "shape" model, good for tonal correction. Same selector pattern and drift system serve both; only the inner DSP differs.
  - **The cascade order fix was the perceptual turning point.** Single-stage SVF bandpass has -6 dB/oct skirts. At narrow widths and high gain, broadband noise still bled through the skirts and dominated perception over the band's ring. Rozaya described this as "a band under a bunch of other noise even with the width set to something that should exclude it." Cascade N stages → -N×6 dB/oct skirts. At Order 8 the band is genuinely isolated. Each band has its own Order setting; SVF state allocated for max order = 8 stages.
  - **Multi-target drift on a single band is the windscape engine.** One band with simultaneous drifts on Frequency (period 47s), Gain (period 13s), and Pan (period 23s) at independent rates produces a single voice that wanders in pitch, brightens and dims, and sweeps in stereo space — all uncorrelated. A few such bands at different center frequencies make dense evolving texture without any global rhythm. This is what the plugin is FOR; the formant/vowel use case is one configuration among many.
  - **dB gain replaced linear-multiplier "Strength."** The earlier Strength slider had different meaning in each mode (linear multiplier in parallel, dB-multiplied-by-6 in serial). Confusing. Replaced with proper dB throughout: range -60 to +24, -60 treated as "off" (filter computation skipped for CPU). Parallel mode converts dB to linear via `10^(dB/20)` before multiplying with cascade output. Serial mode uses dB directly as the peaking EQ gain (A = `10^(dB/40)` for the biquad coefficient math). Phase inversion via negative gain dropped — it was a vestigial weirdness, not a useful feature.
  - **Width sliders own resonance.** No separate "sharpness" / Q knob. Width up + Width down (in Hz) determine bandwidth; bandwidth × center determines damp; damp determines Q. Narrow widths = peaky resonant character. Wide widths = broad non-resonant emphasis. Resonance is implicit in narrowness. Asymmetric widths shift the actual filter center while keeping the user's Frequency value as a reference point.
  - **`ext_noinit = 1` is load-bearing.** Without it, REAPER re-runs @init on every transport play, which zeros all per-band memory banks. Rozaya hit this during testing ("transport stops it entirely") — the band configurations were silently wiped each play. The flag at the top of @init prevents this.
  - **Stereo image preserved through wet path.** Each band runs L and R SVFs independently with shared parameters. Input's stereo image survives; per-band Pan then shifts each band's balance from the preserved-image starting point. Earlier mono-summed version (input → mono → bandpass → panned) lost the input's stereo image in the wet path; user flagged this.
  - **Pre-history (didn't ship, archived in `archive/exploration/`).** Hours of exploration before this design crystallized. Tract waveguide diagnostic builds (`tract_diag_v1.jsfx` and `tract_diag_effect_v1-v6.jsfx`) proved a Pink-Trombone-style Kelly-Lochbaum tract rings correctly with proper three-zone rest shape and cosine tongue formula but produced "vowels emerging but not landing cleanly" character that hit a wall. Klatt-style parallel formant filter (`vowel_shaper_v1.jsfx` through `_v8.jsfx`) went through eight iterations chasing natural shaped-breath: triangle → quadrilateral vowel-space interpolation, formant strength rebalance for noise input, Voice Size, lip rounding as the entire vowel-character gate, input-derived constriction noise (no synthesis inside the plugin), and finally architectural restructure so breath is the base signal that lip rounding shapes rather than three parallel paths the brain perceives as layered. Pure parametric synthesis hit a naturalness ceiling. The conceptual pivot to "the right tool isn't a vowel-specific plugin, it's a configurable resonance bank with multi-target drift" landed the win.
  - **Lessons preserved in archive's README.** If natural shaped breath becomes a priority again, the conclusion is that the next attempt would be sample-based (real breath recordings the plugin manipulates) rather than further parametric refinement. The diagnostic builds documented that the underlying DSP is sound; the limit is perceptual, not technical.

- **Womb v2 — RSA + drift redesign** (2026-06-03, on `feature/womb-v2`, merged to master in same session). Womb v2 ships as a sibling file to v1 (`src/womb_sound_generator_v2.jsfx` alongside `src/womb_sound_generator.jsfx`) because the slider IDs in the drift block (52+) have different semantics between v1 and v2 — re-using one file would scramble user state on update. Three substantive changes vs v1 (and vs the selector+value v2 attempt at commit `4628210`):
  - **HRV / RSA is bidirectional now.** v1 and the 4628210 attempt both had `heart_with_breath_offset` modulating from 0 → +bpm only (HR climbed during inhale, returned to baseline at bottom pause, never went below). Real RSA modulates around baseline — heart rate descends past baseline during exhale and dwells at the trough through bottom pause for 1-2 beats before the next inhale climbs again. Rozaya reported observing this in real bodies and pushed back on the one-directional shape. New wiring: `-bpm/2` trough at bottom pause, `+bpm/2` peak at top pause, linear ramps in between. Slider expresses peak-to-peak BPM (value of 6 = swing between -3 and +3 around baseline). The natural top-pause / bottom-pause durations of the breath cycle give the peak and trough their dwell time automatically.
  - **Breaths per minute is a one-way rescale tool, not bidirectional sync.** v2 at 4628210 had bidirectional BPM ↔ duration sync (tweak either, the other updates). Rozaya's pushback: "BPM needs to be at 0, letting you set the durations to be scaled and then, as you adjust it, reflecting the modified durations in those 4 sliders." Implementation: default 0 = inert (durations control rate); nonzero triggers a one-time rescale of the four duration sliders to fit `60/BPM` seconds total. Subsequent duration edits don't update BPM back. Each new BPM value triggers a new rescale. Matches Reaper's per-track Timebase semantics and every consumer breathing-app idiom (research surveyed apps from Awesome Breathing, Breathing Zone, iBreathe, The Breathing App).
  - **Heart drift and Breath drift are independent (deliberate divergence from suite-wide canonical drift).** The 2026-06-01 per-plugin drift sweep gave every rate-bearing plugin a single drift wave with Musical + Slow timescales (7 sliders total). Womb v2 diverges: separate Heart drift Up/Down/Period and Breath drift Up/Down/Period sliders, single timescale each. Reason: real physiology HRV and respiratory-rate-variability are independent — coupling them collapses what makes Womb feel alive. Other plugins don't have this physiological constraint so the canonical pattern fits them. The Womb v2 manual section calls out the divergence explicitly so users coming from other plugins know the slider structure is different on purpose.
  - **Process arc worth knowing.** Two prior v2 attempts in tree at older commits — `53b5163` (scaler-based, scrapped) and `4628210` (selector+value pattern using a memory bank, scrapped). The selector+value pattern works for homogeneous items (Harmonic Sculptor's 64 harmonics) but adds cognitive overhead for heterogeneous drift parameters where each one has a different conceptual role (Heart Up vs Heart Down vs HRV). Rozaya pushed back specifically — "Heart drift up and drift down should probably be their own sliders" — and the third iteration landed on 9 individual sliders, accepting more surface in exchange for unambiguous naming. Full research synthesis + design rationale in `docs/womb-v2-design.md` ("Research synthesis + finalized design (2026-06-03)" section).
  - **Open work**: ear-tested end-to-end by Rozaya, merged to master. Next steps in this session: tag + `gh release create` bundling Womb v2 with the prior unreleased Speed Ramp sweep + per-plugin drift sweep work (the previous `v2.3` tag was created and deleted; the actual next formal release tag would be `v2.2` or `v2.4` depending on numbering preference — see git tag list for current state).

- **Speed Ramp sweep across the suite** (2026-05-30, on `feature/rate-morph`, unmerged at time of writing). Every plugin gained an in-plugin slowdown/speedup feature designed for sleep wind-down — the user reported difficulty using REAPER automation envelopes via OSARA, and that manual rate-slider adjustments clicked on several plugins. Three new sliders per plugin (always at the end of the existing range): **Speed ramp target (multiplier)**, **Speed ramp duration (minutes)**, **Speed ramp engage (Off/On)**. Off → On captures the current `speed_scale_current` and ramps fresh toward target over duration; On → Off freezes at the in-flight position (does not reset to 1.0). Resets on transport play, like Start Delay + Play/Rest. Per-plugin implementation strategies vary because the rate semantics do:
  - **Frequency-like rate** (Heartbeat, Womb, Tremolo, Sweeping Filter, Sweep Dwell, Rhythm Track): multiply the effective frequency by `speed_scale_current` at the per-sample use site (`freq * speed_scale_current` or `samples_per_beat / speed_scale_current` etc.). Heartbeat, Tremolo, Sweeping Filter, and Womb additionally got a ~100 ms one-pole smoother between the rate slider and the audio to kill clicks on manual adjustment (`rate_smoother_coeff` + `freq_smoothed` / `bpm_smoothed`). Smoothed values are seeded from current slider values in @init so the first sample after transport-start uses the saved rate, not a default — important because @init re-runs on play.
  - **Period-like rate / state-machine plugins** (Breath, Womb's breath layer, Melody Phase, Shepard Scale): scale the state-pos increment by `speed_scale_current` (was `state_pos += 1`, now `state_pos += speed_scale_current`). For Melody Phase, `dt = speed_scale_current / srate` scales every per-sample time accumulation — sequencer + voice envelopes + pan modulation all stretch together so Attack %, Release %, Note duration proportions stay intact. For plugins with a Freeze-mode rest timer (Shepard Scale, Melody Phase, Womb breath), `pr_rest_elapsed += speed_scale_current` too so rest duration tracks effective tempo.
  - **Multi-voice / polyrhythmic** (Polyrhythm Phase, Shepard Tone): multiply each voice's per-sample phase advance and cycle counter by `speed_scale_current` at the use site. Single multiplier preserves the rate RELATIONSHIPS between voices — V1 at 60 BPM and V2 at 60.5 BPM both halve at scale=0.5, so the slow beat between them halves too.
  - **Womb scales ALL THREE LAYERS** (HB BPM, breath state, bloodflow which is locked to HB) from one Speed Ramp control — keeps the physiological coherence the plugin is built around.
  - **Audible pitch / tuning is never scaled.** Only modulation / sequencer / envelope rates. Oscillator frequencies, filter resonance centers, binaural beat, tuning reference all stay where the user set them.
  - **One commit per plugin.** Each commit message names the slider IDs it added and the implementation strategy in shorthand. Manual updated alongside the code (every plugin's section in `docs/rozaya_jsfx_manual.md` got a `### Speed Ramp (new)` subsection).
  - **Open work**: merged to master but not tagged/released. User to test by ear across all 11 plugins before tag + `gh release create` as v2.2 (same note style as v2.0/v2.1). Per-plugin tweaks possible (different smoother time constants, different multiplier ranges if 0.1–4.0 isn't right, etc.).
  - **Pattern to reuse**: the universal Speed Ramp UI (3 sliders, identical names + semantics + behavior across the suite) is now a convention. New plugins added to the suite should include it.

- **Per-plugin Drift sweep — Wobble removed, drift built in** (2026-06-01). Replaces the Wobble Modulator + suite-wide Wobble slot pattern (next entry, marked superseded). Two motivations: any third-party JSFX could write into the same gmem slot and collide; the cognitive-load distinction (workflow plugin vs sliders on the synth itself) made the cross-plugin pattern more taxing than per-plugin sliders. So drift moved INTO each rate-bearing plugin as built-in sliders, and got richer in the process — two stacked drift sources at different timescales, asymmetric up/down amplitudes, three shape options.
  - **7 sliders per plugin**, always at the end of the existing range. **Musical drift** (scales with Speed Ramp, like the rest of the plugin's rate behavior): *Drift up by* / *Drift down by* (separate amplitudes for biological-feel asymmetry) / *Drift period (cycles)*. **Slow drift** (wall-clock, independent of Speed Ramp): *Slow drift up by* / *Slow drift down by* / *Slow drift period (minutes)*. **Drift shape**: Sine / Triangle / Random.
  - **Two stacked drift sources at different timescales.** Musical drift sits at the cycle level — it's musical because it tracks the plugin's own clock and slows when Speed Ramp slows. Slow drift sits at the wall-clock level — minutes-long wander that keeps drifting at the same rate even if the user ramps the whole plugin down. Both multiply into the rate together; either can be zero to disable that layer.
  - **Asymmetric Up by / Down by amplitudes.** Biological signals don't drift symmetrically around their center (heart rate variability is famously asymmetric, breath cycles too). Separate up and down amplitudes let the drift sit slightly off-center in a way that feels alive rather than mechanical. Down by = Up by recovers symmetric drift.
  - **Three shapes.** Sine = smooth continuous wander. Triangle = linear ramps with turnaround points. Random = value-noise that interpolates smoothly between random targets at each period boundary (not white noise — still smooth, just unpredictable in direction).
  - **Multi-voice / multi-layer plugins share ONE drift across all voices/layers** (matches the Speed Ramp / Wobble convention before it). Polyrhythm Phase: one drift across all 8 voices, preserving the rate relationships between voices. Shepard Tone: one drift across all layers. Womb: one drift across HB / breath / bloodflow, keeping the physiological coherence the plugin is built around. Per-voice / per-layer drift would be 7N sliders instead of 7; cost not worth it.
  - **Wobble Modulator plugin removed entirely.** `src/wobble_modulator.jsfx` is gone. The per-plugin Wobble slot slider (one per rate-bearing plugin) is gone. The WOBBLE_BASE = 100000 gmem convention no longer applies — drift is now strictly local per-plugin state, no gmem reads/writes for drift purposes anywhere in the suite.
  - **v2.3 tag was created and deleted.** Releases were premature; this is the actual content of the next release once user-tested. No `gh release create` until the per-plugin drift sweep is validated by ear across the suite.

- **Wobble Modulator + suite-wide Wobble slot** (2026-05-30, `feature/wobble`, branched off `1585dc7` (v2.2 final), unmerged at time of writing). New modulator-plugin pattern for adding organic wander to any rate-bearing plugin in the suite. **History worth knowing:** before this approach landed, the same session had built a built-in LFO layer onto Speed Ramp directly (the v2.3 work on `feature/rate-morph`) — four extra sliders per plugin, target-relative LFO with freeze-phase logic, ramp/LFO interaction. The user reported they couldn't follow what it was doing, even after a manual rewrite. The conceptual confusion was real: "Speed Ramp's LFO" conflates two unrelated features (slow wind-down ramp vs always-on organic wander) that should be independent. The modulator-plugin approach is the cleaner architecture and the one the user actually wanted.
  - **New plugin: `wobble_modulator.jsfx`.** Four sliders (Slot 1-16 / Depth 0-1.0 / Period 0.1-60 min per cycle / Shape Sine|Triangle). Audio passes through unchanged. Per sample, writes `1.0 + depth * shape(phase)` into `gmem[100000 + slot]`.
  - **Each rate-bearing plugin gets one new slider: Wobble slot** (0-16, default 0 = off). At the rate-use site, reads `gmem[100000 + slider_value]` with a defensive `> 0` check (defaults to 1.0 if the mailbox is empty), multiplies the rate by it. Combined with the existing speed_scale via `combined_scale = speed_scale_current * wobble_mult` and used wherever speed_scale was used before.
  - **WOBBLE_BASE = 100000** is hardcoded in `wobble_modulator.jsfx` AND each rate-bearing plugin's `@init`. Twelve files in sync — if this constant ever needs to change, ALL twelve must change together. Chosen high to avoid collision with other JSFX plugins the user might install (gmem is global across the Reaper session, shared with every JSFX in any project).
  - **Why per-sample gmem reads work fine here.** Each rate-use site does ONE read per sample (`gmem[WOBBLE_BASE + slot]`), which is cheap. No locking concerns — gmem is single-threaded per Reaper instance. The wobble values are sample-accurate because the modulator writes per sample too. No interpolation or smoothing needed since the modulator's wobble itself moves at sub-Hz rates (period > 0.1 min = 6 sec = << audio rate).
  - **Womb uses ONE wobble slot for all three layers** (HB BPM, breath state_pos, breath rest timer). Same scope as Speed Ramp — the whole womb wobbles together as one organism. Per-layer wobble would be 2-3 sliders instead of 1; chose simpler. Polyrhythm similarly uses ONE wobble for all eight voices (preserves rate relationships).
  - **Defensive gmem read** in every synth: `slot > 0 ? raw_wobble = gmem[BASE + slot]; raw_wobble > 0 ? wobble_mult = raw_wobble;` else default to 1.0. Catches: slot unassigned (0), mailbox never written (gmem starts zeroed at Reaper boot), or a removed modulator that left a 0 or negative value behind. Multiplying rate by 0 would silence the synth — this avoids that. Documented in the manual that a stale value can linger when a Modulator is removed mid-session (set Wobble slot back to 0 to fully disengage).
  - **Manual: conversational mailbox metaphor.** User's feedback on the v2.3 docs was that they couldn't follow them despite a rewrite — too much version-spec / internal-variable / cross-plugin-reference language. The Wobble Modulator section explains gmem with "numbered mailboxes that every JSFX plugin in your Reaper session can see at once," walks through the patching workflow step by step, and only then gets to slider descriptions. Each per-plugin Wobble slot subsection cross-links to Wobble Modulator instead of duplicating the explanation.
  - **Open work after the wobble sweep.** Superseded by the per-plugin drift sweep. No remaining Wobble work — the Modulator plugin and per-plugin Wobble slot sliders are gone.
  - **The pattern itself is reusable.** Future modulator plugins (e.g. "Random Drift Modulator" for unpredictable wander, "Envelope Follower Modulator" for audio-reactive control) can use the same WOBBLE_BASE offset with different slot ranges, or pick their own offset. The receiving synth side is already in place — any plugin in the suite that has a Wobble slot is automatically compatible with any future modulator that writes to its slot in the same multiplier convention (multiplier centered on 1.0).

  **Superseded 2026-06-01.** Replaced by per-plugin built-in drift (next entry). The gmem-routing approach raised reliability concerns (any third-party JSFX could collide on the same slot) and the cognitive-load distinction (workflow vs sliders) made the cross-plugin pattern more taxing than per-plugin sliders. Cross-plugin coupling went; richer per-plugin drift came in its place.


- **Pan modes feature** added Spread + Spread Reversed (commit `b60e635`) — static pan positions ranking active voices across the stereo field. Bonus discovery: running two tracks of the synth, one with Spread + one with Spread Reversed at slightly different Tuning Reference Hz, produces a surprisingly rich stereo width effect via composition rather than DSP. Documented in the Pan section of the manual.
- **Per-voice docs fix** (commit `fb6199a`) — the manual previously listed Vn Note and Vn Octave as per-voice sliders; the actual sliders are Gain dB / Semitones / Drift-Rate / Phase Offset / Active. Also default Gain dB is -6 for V1 and -60 for V2-V8 (manual previously claimed default 0 for all). **Superseded 2026-08-31: every voice now defaults to -6.** -60 is the off sentinel and `Vn Active` is already the on/off, so defaulting a voice's gain there stranded it -- activating a voice gave silence and a 54 dB climb. Melody Phase already defaulted all eight to -6; this was another unpropagated fix. V2's Active also went 1 -> 0, since it had been shipping On at -60 (paying CPU, inaudible, and counting in the active-voice normalizer); a fresh instance therefore sounds exactly as before. **Rule: where a control has a dedicated on/off beside it, its value defaults to something usable, never to the off sentinel.**
- **Polyrhythm Phase v2 — Play/Rest gating** (2026-05-25, merged on `feature/polyrhythm-loops`). v2 adds sliders 63 (Play for) and 64 (Rest for), per-voice cycle counting (V8 paces ahead of V1), and a depth-floor cancel on the final cycle's release so the voice glides to actual silence before the rest freeze regardless of Depth dB setting. Iteration went through three approaches before landing: in-place edits to polyrhythm_phase (parked on `feature/play-rest-gating`, abandoned), a sibling plugin `polyrhythm_phase_loops.jsfx` while the cutoff thud was being worked out, then consolidated back into polyrhythm_phase.jsfx once the depth-floor-cancel approach proved solid in user testing. v1 project files open unchanged in v2 — the new sliders default to 0 which keeps the gate off, and slider IDs 1-62 are bit-identical. Also folded in: the `total_active` normalizer fix (latent bug in v1, exposed by the gate but correct for the engine generally).
- **v2.1 sweep — Play/Rest gating across the rest of the suite** (2026-05-26, on `feature/play-rest-everywhere`, unmerged at time of writing). Every plugin in the suite that has Start Delay now also has Play/Rest gating. Per-plugin commits in the branch log; consistent slider IDs / labels per family. Three different gate semantics by plugin type:
  - **Event-triggered synths** (Heartbeat, Breath, Rhythm Track): just `Play for` / `Rest for`. Gate at the event trigger site (don't fire new beats / ticks / breath-cycles while resting). Existing envelopes finish naturally.
  - **Sequencer synths** (Melody Phase, Shepard Scale): `Play for` / `Rest for` + `Rest mode` (Walk through / Freeze in place). Walk mode lets the sequencer walk through voices silently during rest; Freeze pauses the sequencer entirely and resumes from the frozen voice. Melody Phase Freeze uses a `simulate_rest_duration_seconds()` function to match Walk mode's wall-clock duration when voices have varied "Next voice in" timings (so the slider value means the same wall-clock time in both modes). Shepard Tone uses the same pattern but the unit naturally matches (single global rate).
  - **Effects** (Full Feature Tremolo, Resonant Sweeping Filter, Sweep Dwell Filter): `Play for` / `Rest for` + two orthogonal mode sliders — `LFO at rest` (Walk through / Freeze in place) and `Output at rest` (Pass-through / Silence). Four combinations of rest behavior. "Rest" doesn't silence the input by default (matches Start Delay's pass-through-during-delay convention for effects) but Silence mode is available when you want a hard mute. effect_mix smoother (3 ms) blends play-mode output with the rest target.
  - **Womb Sound Generator**: per-layer gates (six sliders, two per layer: Heartbeat / Breath / Bloodflow). Each layer's gate mirrors the design of its standalone sibling plugin. Bloodflow's gate uses `hb_phase` wraps as its tick (since BF is locked to HB), even when HB itself is gating beats out — so BF's counter advances on the underlying heartbeat clock, not the audible-beats clock. **Resolved 2026-06-01** (was an open question after v2.1): the BF tick stays on `hb_phase` wraps — there's no realistic context where bloodflow decouples from heartrate (medical decouplings are all "the heart isn't pumping anymore" — LVAD, bypass, CPR — which is the opposite of what Womb evokes). And per-layer Rest mode (Walk/Freeze) isn't added because none of Womb's three layers are sequencers — there's no sequence position to walk silently through. The existing per-layer rest IS freeze-style for breath (state machine pauses on bottom pause) and event-gate for HB/BF, matching each layer's standalone sibling which also doesn't expose Walk/Freeze.
- **JSFX gotcha — empty `()` from comment-only conditional branches** (commit `a546fce`, lessons-learned). Discovered while adding Play/Rest to Breath Generator: a `cond ? (...) : (...)` where one branch contains only comments resolves to an empty `( )` after comment stripping, which eel2 rejects. Symptom is "the plugin loads but produces no sound" — Reaper doesn't always pop a visible error. Workaround: invert to a one-armed conditional so the parser never sees an empty block. Also documented in the JSFX gotchas section above.
- **Shipped as v2.1** (2026-05-27) — branch merged, tag pushed, `gh release create` done. The `feature/play-rest-gating` and `feature/polyrhythm-loops` branches have been deleted. The Womb open question is resolved above (BF tick stays on `hb_phase`; no per-layer Walk/Freeze). The only remaining future-work pointer from this sweep: per-cycle fade shoulders on Polyrhythm Phase (commit `080f505` on `feature/polyrhythm-loops`, reverted) — if you ever want to revisit the "fade in / fade out around rest" idea for the polyrhythm plugin specifically (different from the depth-cancel approach that landed), the design is in `docs/planned-features.md` under "Polyrhythm Phase Loops" → "Rejected alternatives."
