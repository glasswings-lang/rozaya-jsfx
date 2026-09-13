# Backlog — what the suite is still owed

**Budget: 650 lines.** Run `python tools/doc_budget.py` before committing.

**NOTHING IN THIS FILE IS A JOB YOU MAY START UNASKED.**

That sentence is the whole reason this file exists separately. This material used
to sit inside `docs/suite-consistency-plan.md`, so a session that opened the plan
to check one rule was handed seven hundred lines of owed work — and read it as a
to-do list. Rozaya, 2026-09-08, on what that felt like from the other side:
*"it was doing the thing of, I'm gonna fix bugs even though you've said you
haven't heard them. It was like we were having two different conversations."*

**A backlog is not permission.** Read this to answer "what is this plugin owed?"
when you are already working on that plugin and have been asked to. Do not read
it to decide what to do next. That decision is Rozaya's.

**And check it against `docs/current-state.md` before believing any line here.**
Anything on the not-heard list there is BLOCKED, not pending: it cannot be built
on, extended, or "finished" until it has been heard. The correct action on
unheard work is to ask for an ear test, never to add to it.

Moved out of the plan 2026-09-08, verbatim. The R24 drift-target audit is in `docs/r24-drift-target-audit.md`.
**OWED, COMMITTED 2026-09-11: per-target `Drift amount unit` / `Ramp by unit` in all nineteen** -- Passage and the Morpher inside their coming migrations, the other seventeen as one sweep straight after. Rozaya: *"Yes, do it your way. I'd prefer that while we have room"*. Why and how: `docs/layouts/spectral-vowel-passage.md`, "The amount units". **Stale slider numbers on plugin pages** (seen 2026-09-12, not fixed): entries such as `Ramp engage (all targets, slider 28)` in sweep-dwell-filter.md, heartbeat-generator.md's `(slider 31)`, `Ramp target (slider 47)` and `(slider 23)` in sweeping-filter.md and rhythm-track.md name positions that have since moved.
---

## Hidden limits: controls whose code stops short of what they say (2026-09-13)

**Found by listening, not reading.** Spread said 1000 and stopped at 150 -- a limit left
when the 2026-09-06 range sweep widened the slider; its clamp scan followed a value one
hop and missed it. Rozaya: *"What I don't understand is why a hard-coded limit of anything
was let in at all. especially when people manually type in weird values because it's jsfx
all the fucking time."* An audit then rendered each of the sweep's 176 widened controls at
half its old ceiling, the old ceiling, halfway up and the new top, in up to three of
Rozaya's saved copies: 41 reach, 104 COULD NOT BE JUDGED (not heard in the copies tried --
most are drift, ramp and per-voice values that nothing in those copies was using), 10 in
archived plugins, 12 replaced since. Caught, and what each is (read in the code, measured):
- **Spread** (Passage, Morpher) stopped at 150 -- a leftover. Lifted: Morpher committed
  `fa8c650`; Passage inside its migration.
- **Low cut** (Passage, Morpher) stopped at 500 -- a leftover. Being lifted, same way.
- **Wash grain** (Passage, Morpher) stopped at one capture buffer, 743 ms at 44.1 kHz, 680 at
  48 kHz, of 1000 -- REAL: JSFX's fft() stops at 32768. Rozaya chose the full 1000
  (*"sounds good"*): a longer grain is built from half-overlapping FFTSIZE pieces. Morpher
  committed; Passage inside its migration.
- **Capture average** (Morpher) stops at 6 frames of 1000 -- REAL, only six fit in a
  capture; Passage's control already stops at 6. Not yet asked: the control back to 1-6
  (no saved copy above 6).
- **Breath High-pass** (Womb) stops between 7200 and 7300 Hz of 20000 (7188 worked out) --
  REAL for that filter type (Chamberlin). Not yet asked: a TPT filter, as the sweeping
  filters have, or an honest range.
- Rhythm Track's Drift up/down amount was flagged and is NOT a limit: the drift in the copy
  heard was on Swing amount, which is -1 to 1 itself.
**Still owed:** the 104 unjudged need a setup that makes each audible. The audit is
`tools/hidden_limit_audit_20260913.py`; its control list holds 2026-09-13's slider ids.

## R23 — drift steps on the target's own turn (2026-09-09)

**From a problem Rozaya found, and approved by it plugin by plugin. The wording
below is Claude's; do not cite it back as its own.**

> A drift target that is READ ONCE PER OCCURRENCE steps once per occurrence, and
> its period counts those occurrences. A target read CONTINUOUSLY drifts
> continuously, and its period is time.

**In its words:** *"you don't get to say drift this thing every two cycles and
drift this thing every four. it's being fucked."*

**THE SWEEP IS DONE, 2026-09-09.** Every plugin with drift was READ, not
name-matched. The earlier table here named three plugins that never needed it.

| plugin | targets that step, and on what |
|---|---|
| `breath_gen` | breath rate + four segments, on their own segment |
| `womb` | Heart rate + Systole per beat; segments + Breath rate per breath (names since 2026-09-11) |
| `heartbeat gen` | heart rate + S1-S2 gap, per beat |
| `melody_phase` | V1-V8 Note duration on that voice's note; Attack/Release on any note |
| `rhythm-track` | none by default (since 2026-09-11); any target per beat, Beats per bar per bar |

**BUBBLER AND DAPPLE: this entry was STALE, corrected 2026-09-09.** It said they
were built, reverted, and must not be rebuilt. The revert did happen — the tell
was an invented "the left stream counts" tie-break — but stepping then came BACK
deliberately, counting every birth on either channel (`272a438`), and nobody
updated this. Rozaya: *"The stepping was deliberately live, that shit's stale in
the doc."* Both now carry `Drift movement`, so neither the plugin nor this file
decides it: the three targets read once at a bubble's birth default to `With the
target`, everything continuous to `On a clock`.

**PASSAGE WAS WRONGLY CLEARED, corrected 2026-09-12.** Its four slot timings are read
once, when a slot's leg begins (`lgo_*`), and were drifting on a clock. Rozaya: *"Um.
yes? Wow, when they said it was excluded they meant it."* It gets `Drift movement` in
its layout migration (`docs/layouts/spectral-vowel-passage.md`). **The Morpher is NOT
re-checked** -- it has no slot timings as targets, but read it rather than trust this.

**Checked and CLEARED — do not "fix" these.** Tremolo, Shepard Scale, Shepard
Tone, Sweep Dwell, Sweeping Filter, Polyrhythm v3, Veil, Stereo Phaser, Morpher,
Resonance Bank. (Rhythm Track left this list 2026-09-11: its clicks now
read their targets as they fire, so it has the switch.) Their
controls feed a shape or a threshold recomputed every sample, so the wander is
expressed rather than sampled. The first three were on the old list
wrongly; Polyrhythm v1 is out by the standing decision to leave it.

**Seconds and Beats on a stepped target — DECIDED AND BUILT 2026-09-10**, all six
plugins. They were silently behaving as the first unit. Rozaya: *"stop mid-cycle,
freeze the clock mid-whatever unit, then pick up on the next cycle from wherever
the clock was last."* The clock runs in that unit only while the target's own
thing happens; a bubble is an instant, so each birth adds its Bubble length.

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

### What is still unplanned, in the order things block each other

**Blocking:**

1. ~~**Part 2's canonical layout is stale.**~~ **CLOSED 2026-09-05** — rewritten
   and approved. Read Part 2; Drift and Ramp stay shared and last.
2. ~~**The version forks.**~~ **CLOSED 2026-08-31.** Melody: archive v2, its note
   picker moves to v1. Polyrhythm: migrate v1's projects up to v3, archive v1.
   Both forks end.
3. **Scope.** Harmonic Sculptor is under an overhaul-or-drop question and Rozaya would not
   reach for it — still open. **Sustain Looper is IN**, corrected 2026-08-31: excluding it
   was Claude's judgement call, not Rozaya's, on the reasoning that it is a "sound-design
   tool". It is not — it runs in a project and plays for the length of a piece, which is
   exactly the profile drift and ramp exist for. Targets below.
4. ~~**Validation — the real hole.**~~ **CLOSED.** Reload and track-duplicate ARE
   testable — ask for one. And since 2026-09-09 `tools/jsfx_run` compiles and
   RUNS a plugin outside REAPER, so behaviour can be measured before it ever
   hears it. Read its README for what it cannot see; the list is real.
   Ear-testing happens over weeks of ordinary use, so the sweep does not block on
   a testing phase. What I owe in return is that everything checkable without
   ears IS checked before it ships.

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

### Three more unpropagated decisions, found by grepping for the pattern

Once R17 named the failure mode — good decisions made in one plugin and never carried
across — it became something searchable. Found 2026-08-31:

**1. The waveform palette drifted, against an explicit written rule.** CLAUDE.md states:
*"any new waveform added to Polyrhythm Phase or Melody Phase should land in all four
plugins at the same slot index."* Measured:

| | waveforms |
|---|---|
| Polyrhythm v1, Polyrhythm v3, Harmonic Sculptor | **14** |
| Melody Phase v1, Melody Phase v2, Shepard Scale, Shepard Tone | **12** |

**Square** and **Pulse** (slots 12–13) never propagated. Cheap to fix and completely safe:
waveforms append to the end of the enum, so slots 0–11 keep their meaning and no project
changes. Note this also explains a stale-docs finding already in the plan — both
Polyrhythm pages document 12 against a source with 14.

**2. Solo exists in two plugins out of six that need it.** **DONE 2026-09-10** in all
six — `docs/layouts/solo-propagation-20260910.md`. Solo overrides Active everywhere.

| plugin | things to audition | Solo |
|---|---|---|
| Spectral Vowel Morpher | 16 layers | **yes** |
| Womb | 3 layers | **yes** |
| Polyrhythm v1 / v3 | 8 voices | no |
| Melody Phase | 8 voices | no |
| Shepard Tone | per-voice | no |
| Resonance Bank | **16 bands** | no |

Solo is not a luxury control, it is *how you hear what you are editing* — Rozaya on the
Morpher's: *"you solo to hear a thing."* Without one, auditioning a single band in
Resonance Bank means turning the other **fifteen** down to −60 dB and back afterwards.
Every plugin with per-voice / per-band / per-layer anything should have Solo, and the
Morpher's semantics are the reference: **Solo overrides Inactive**, because you solo in
order to hear something.

**3. `src/heartbeat gen.jsfx` is the only filename in the suite with a space in it.**
Every other file is hyphenated or underscored. It broke two of my own scripts tonight.
**Renaming is NOT free** — `.RPP` files reference the plugin by filename, so it needs a
project rewrite like any migration. Fold it into Heartbeat's own batch rather than doing
it loose.

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

## What each plugin owes

- **The thirteen already on R13-revised** owe only the enum ORDER, plus a rate
  mode of their own for any rate that lacks one. Measured 2026-09-04: the main
  Rate Mode is canonical in six plugins; `{Own BPM, Host x}` in four (Womb,
  Heartbeat, Rhythm Track, Shepard Scale); `{Own Hz, Host x}` in Stereo Phaser;
  and **every pan unit in the suite runs BACKWARDS** — `{Hz, Seconds, BPM}` on
  Tremolo and the Sweeping Filter, `{Hz, Seconds, BPM, Host x}` on Sweep Dwell.
  Resonance Bank's drift period mode is a third order again,
  `{BPM, Hz, Seconds, Host x}`.
- **Melody Phase** converts: its 27 synced instances get Rate mode `Host x` and
  their beats number moved into `Rate value`; sliders 3, 4 and 5 are deleted;
  the pan gains a rate mode. **Net two fewer controls than it has today.**
- **Womb** converts the same way. Its 1 Host x instance moves its `Every N
  beats` into the heart rate slider. **The beats value MOVES; it is not
  deleted** — see the near-miss note below, which stays true as process even
  though its conclusion about Womb has been overturned by this rule.

## The dependency that makes this three jobs, not one

**Melody Phase and Shepard Tone cannot take this block as they stand.** Both
have eight voices with one flat note slider each. Four controls times eight
voices is thirty-two sliders replacing eight, on plugins already declaring 86
and 75.

So the order is:

1. **This rule.** Done, here.
2. **The voices behind a selector on Melody and Shepard Tone**, the way
   Polyrhythm v3 got on 2026-09-07. That build is the worked example, including
   the `All` position, the change-detected writes, and the blob rewrite.
3. **The pitch migration across eleven plugins**, including the C2→C1 note
   re-index.

Doing 3 before 2 would put a 32-slider pitch block into two plugins that then
need re-migrating when the selector lands. That is the "one migration per
plugin, not one per idea" rule, and breaking it cost five migrations in one day
on 2026-09-04.

## What each pitch-stating plugin owes

**CORRECTED 2026-09-08.** This table said "two blocks" for `breath_gen` and
`heartbeat gen`, which contradicts the rule it belongs to. Rozaya settled it the
same day the table was surveyed and the table was never updated — *"target, then
select from 2, that way you're able to extend it later if needed, also less
sliders."* **Every plugin gets exactly ONE pitch block, behind a `Pitch target`
selector with `All` at position 0, however many pitches it has.** Building from
the old wording would have put ten sliders into each of those two plugins where
five belong.

Surveyed from source 2026-09-08. `Vn` collapses the per-voice banks.

| plugin | states pitch as | owes |
|---|---|---|
| `breath_gen` | Inhale / Exhale Frequency Hz | **one block behind a `Pitch target` selector** |
| `bubbler` | Transpose / Pitch spread / Rise, all semitones | one block, detune to cents |
| `dapple` | Pitch (Hz), Pitch spread (%) | one block, detune to cents |
| `harmonic_sculptor` | Fundamental Hz | one block |
| `heartbeat gen` | S1 / S2 Frequency Hz | **one block behind a `Pitch target` selector** |
| `melody_phase` | Vn Note, Transpose, Octave shift, tuning ref | selector first, then re-index |
| `polyrhythm_phase` | Base Note, Vn Semitones (**range ±1000**), Center Octave | frozen; inherits at the v1→v3 crossing |
| `polyrhythm_phase_v3` | Pitch mode, Note name, Pitch value, Fine tune + unit, per voice | **DONE 2026-09-10**, Breath Gen's block behind the Voice selector |
| `resonance_bank` | Frequency (Hz), per band | one block per band, behind its existing selector |
| `shepard-scale` | Center Octave, Octave Count, tuning ref | one block |
| `shepard-tone` | Root Note, Vn Note, Center Octave, Octave Count | selector first, then re-index |
| `spectral_vowel_morpher` | Pitch (semitones), Layer pitch (semitones), Spread (Hz) | mode pair; **122 instances**, migrate with care |
| `spectral_vowel_passage` | Pitch (semitones), Spread (Hz) | mode pair, rides its owed reorder |
| `sustain_looper` | Pitch (semitones), Spread (detune amount) | mode pair, detune to cents |

**`polyrhythm_phase`'s `Vn Semitones` range of −1000..1000 is eighty-three
octaves in each direction and cannot be meant.** It is left alone — v1 is frozen
until it crosses — but it is noted here so the crossing does not carry it over.

**AND `Center Octave` DOES NOT RETIRE. The first draft of this rule said it
should, and that was a near-miss of exactly the kind this repo has a standing
rule about.** The reasoning was "once `Note` names its own octave, a separate
octave-position control says the same thing twice." Opening the block says
otherwise: in `shepard-tone` it is the centre of the PITCH WINDOW the octave
stack spans — `center_freq = tuning_ref * pow(2, center_oct - 4)`, with the
window `Octave Count` octaves wide around it. It is half of a working pair with
`Octave Count`, not a duplicate of anything. Retiring it would have deleted the
Shepard's stack.

The rule that catches this is already written down: **before retiring any
control, open it and ask what else is inside.** A control that is genuinely
retired does exactly one thing and that thing is now pointless. This one does
something `Octave Count` depends on, and it looks identical from the slider
list.

## Open, and needing Rozaya rather than me

**Nothing.** The rule above is buildable once the two selectors land. The range
question an earlier draft raised was already answered by R12.
## Decision, 2026-09-02: all of it waits for Phase 2

An earlier draft of this section said to reorder positions 4+ immediately, while
it cost one control, and leave 0-3 for later. **Rozaya overruled that and was
right:** *"I say we bloody save it until phase 2. I don't plan to use these
until this is done. I can't be fucked to keep scraping my figurative skin on
sharp edges."*

The "do it now while it's free" argument only holds if the new modes are about
to be used. They are not going to be, so nothing gets saved onto positions 4+
and **the free window stays open indefinitely** rather than closing. Doing half
of it now would buy nothing and leave a list that is tidy from 4 up and
arbitrary below it -- a state someone has to hold in their head, for no gain.

So: **one reorder, in Phase 2, across every plugin that has a Pan Mode**, with
the value remap for 0-3 written at the same time. The new modes ship in their
final order or they do not ship.

**Before starting it,** re-run the stored-value count in the table above --
including the effect plugins, which have never been measured -- because the
"nothing is saved on 4+" fact expires the moment anyone uses one.

---

---

## Part 6 (revised 2026-08-31) — ordered for durability first, then use

Two constraints replace the old family-based batching:

- **Rozaya's testing energy is the only real time constraint.** Not authoring, not
  building. So the work is ordered to spend as little of it as possible per unit of
  benefit, and batched so one listening session covers many changes.
- **This may not have a year.** Rozaya, 2026-08-31, on the possible collapse of frontier
  models: *"we may not have the year I hope for."* Treat AI availability as a resource
  that could end abruptly. **The plan must therefore be ordered so that stopping at any
  point leaves something whole**, and so that whatever is left undone is the kind of work
  a person — or a future model with no memory of this — can pick up from the documents.

### Phase 0 — make what already exists durable. Do this first.

Nothing new; purely protective, and currently the weakest link.

- **Merge `feature/morpher-layers` to master, push, tag, release.** 98 commits ahead of
  master; last tag v2.20 is 102 commits back; master is 4 ahead of origin. Everything in
  use was hand-copied from an unmerged branch. **If work stopped tonight, there would be
  no release containing any of it.**
- Commit the outstanding Morpher `Layer harmonics` work, or drop it deliberately.
- Confirm `docs/plugins/*` matches what actually shipped for the plugins already changed.

**Test cost: none.** It is all already in use.

### Phase 1 — everything that needs no migration, across every plugin at once

This is where most of the value is, and it is nearly test-free because **nothing moves and
no saved value changes**. Ship it as one batch, not per plugin.

- **All naming** — R1–R6, R16 (`Ramp`), R17 (units), target strings, `Loop sequence`.
- **All step sizes** (R8) — always the finer of whatever is in use.
- **Defaults** — Polyrhythm's V2–V8 gain to −6 dB. Free: defaults only affect unsaved
  instances.
- ~~**Enum options only** — `Square` and `Pulse` waveforms in Melody, Shepard Scale and
  Shepard Tone.~~ **DONE and ear-tested ✓ 2026-09-01** (commit `4f7eb14`). All three pass,
  Shepard Tone included — which was the one worth testing, since its oscillators sweep
  continuously and would show aliasing first. Each plugin also gained a **PolyBLEP** helper
  and a **Pulse width** slider (hidden unless Waveform is Pulse), so the "enum options only,
  costs nothing" estimate was very slightly wrong: Pulse needs a duty control, which is a
  new slider. Appended, harmless, and it moves into place in each plugin's Phase 2 reorder.
  The two Shepards share one `wave_sample(ph)`, which gained a second argument for the
  per-sample phase increment that PolyBLEP needs. Both Polyrhythm pages were also corrected
  — they had documented 12 waveforms against a 14-waveform source. **Not** applied to
  `melody_phase_v2`, which is being archived.
- **NOT new sliders.** Solo, Breath Generator's sigh, and the missing drift/ramp blocks
  move to each plugin's Phase 2 reorder, where they land in their proper positions rather
  than being bolted onto the end. See R18.
- **A version stamp in every `@serialize`** — free, silent, and the prerequisite for every
  self-migration in Phase 2. It must be in the field *before* the renumbers.

**Test cost: low.** One pass through the plugins actually in use, listening for anything
that changed audibly — which nothing should.

### Phase 2 ORDER REVISED 2026-09-05 — readiness first, and drift/ramp jumps the queue

**Agreed with Rozaya 2026-09-05.** The table below orders by project count. That
was right when it was written and is not right now, for two reasons found by
working the list rather than reading it:

1. **The top of the list is not startable.** Polyrhythm v1 -> v3 is 17 projects
   and has no authored layout — only a document arguing the decision. The
   author-the-layout-first rule (added 2026-09-04, after five migrations in one
   day) means it cannot begin. **Ordering by use assumes every item is ready;
   readiness gates it in practice.**
2. **Four plugins have no Drift and/or no Ramp AT ALL.** Measured 2026-09-05:
   `bubbler`, `dapple` and `stereo-phaser` have neither; `resonance_bank` has
   drift and no ramp. They were built after the drift sweep and never added to
   it. Part 3 folds missing features into each plugin's own reorder, which puts
   these LAST because those plugins have two or three projects each.

   **That is backwards, and it is the "half-done is unusable" rule.** A plugin
   that cannot drift is a plugin you do not reach for — which is plausibly WHY
   it has three projects. Project count is being read as a preference when it
   is at least partly a consequence. So **Drift and Ramp go into those four
   BEFORE their reorders, not inside them.**

**The revised order:**

| | what | why here |
|---|---|---|
| 1 | **full-feature-sweeping-filter** (11 projects) | the only large one that is READY: layout authored, R20-compliant, no open question. Folds in its own backwards pan unit, so it gets ONE migration |
| 2 | **Drift + Ramp for `bubbler` and `dapple`** (`stereo-phaser` DONE 2026-09-05) | the ONLY three where appending is also the LOGICAL position — see the correction below |
| 3 | **Full Feature Tremolo** (7) | layout authored and R20-compliant; same pan-unit fix as the filter |
| 4 | **polyrhythm_phase v1 -> v3** (17+5) | biggest, and blocked until its layout is AUTHORED |
| 5 | **womb_sound_generator_v3** (8) | converts off the dead sync-block shape (R20) |
| 6 | **spectral_vowel_passage** (10) | blocked on a design conversation, not on work — see below |
| 7 | the singles | `resonance_bank`'s enum needs a version-gated BLOB migration; `sweep-dwell-filter`'s `Cycle mode` needs Passage's answer |

### CORRECTION, same day: "appended, no migration" is true for exactly three plugins

Rozaya, 2026-09-05, on being told the drift/ramp completion would be appended:
*"Why would that be apending. we just reordered to fix the acumulation of
apends making a goddamn mess."* Correct, and it contradicts R18 and Part 3,
both of which this document already contains.

**Measured after the question was asked, and the gap is far bigger than
"three plugins have no drift":**

| control | plugins that HAVE it | plugins MISSING it |
|---|---|---|
| Drift play for / rest for | 4 | **13** |
| Ramp play for / rest for | 4 | **13** |
| Ramp time unit (beats) | 3 | **14** |
| Drift period unit (beats) | 3 | **14** |

Only **Veil**, the **Morpher** and (since 2026-09-05) the **Stereo Phaser** carry
a complete set. Every other plugin can drift and cannot do the staircase or
count in beats. This is the rule *"Anything that has Ramp should have all the
controls that go with Ramp"* having been true on paper and false in the files
since it was written.

**But the fix is NOT an append, except in three plugins.** The test is whether
the plugin already HAS a drift block:

- **No drift block and few sliders** — `bubbler` (11), `dapple` (13),
  `stereo-phaser` (9, done). Drift and Ramp belong LAST in Part 2's order, so
  appending them lands them exactly where the canonical layout wants them.
  Append is correct here by accident of arithmetic, and it is worth saying that
  it is an accident.
- **An existing drift block** — everything else. The missing controls belong
  INSIDE that block. `resonance_bank` is the clearest case: drift sits at 9-14
  and **Mode / Wet-dry / Output Volume sit at 15-17**, so an appended
  `Drift play for` would land at 18, nine places from `Drift shape`, with the
  output controls wedged between. That is the disease this whole document
  exists to cure.

**So the drift/ramp completion is not a shortcut past Phase 2. It IS Phase 2**,
folded into each plugin's single reorder, which is what Part 3 said all along.
Only the three above can be done ahead of it.

---

**Passage is blocked on a question, not a queue position.** Rozaya, 2026-09-05:
*"the whole reason I kinda hate using passage is because there's, you know,
there's no real reason to right now."* It was born to supersede the Morpher and
in practice does not. **Reordering a plugin nobody wants to open buys nothing,
and spends a migration across ten projects to buy it.** What it needs first is a
decision about what it is FOR — the live candidates being durations that follow
the rate mode's unit (the `(in rate mode units)` control the Sweeping Filter
already has), and Play for / Rest for gaining their own target lists.

---

### Phase 2 — the migrations, ordered by USE, not by family

Measured across 91 projects, 2026-08-31:

| order | plugin | projects | note |
|---|---|---|---|
| 1 | ~~**spectral_vowel_morpher**~~ **DONE + EAR-TESTED 2026-09-01** | **38** | 122 instances migrated, 0 problems; 848 captures byte-identical; an existing project reopened correctly. Sync to host and the Pitch+Overtone fix still unheard. |
| 2 | polyrhythm_phase v1 → v3 | 17 (+5) | fork closes; migrate templates too |
| 3 | full-feature-sweeping-filter | 11 | |
| 4 | spectral_vowel_passage | 10 | |
| 5 | womb_sound_generator_v3 | 8 | partly done already |
| 6 | Full_Feature_Tremolo | 7 | |
| 7 | ~~melody_phase~~ **DONE 2026-09-02** | 5 | 58 instances migrated, 0 problems, verified. v2 archived. Awaiting ears. |
| 8 | breath_gen, bubbler, dapple | 3, 3, 2 | |
| 9 | heartbeat, resonance_bank, stereo-phaser, sustain_looper, sweep-dwell | 1 each | heartbeat also gets its filename despaced |

**Zero-project plugins go last, or not at all:** harmonic_sculptor, rhythm-track,
shepard-scale, shepard-tone, veil (melody_phase_v2 is being archived). Veil is the
interesting one — it shipped in July, was ear-tested and liked, and has still never been
used in a project. That is a discoverability signal, not a quality one, and it is worth
asking about before spending a migration on it.

### If it stops

Ordered this way, an abrupt end leaves: a tagged release (Phase 0), a suite that is
consistently *named* and has its missing controls (Phase 1), and migrations completed for
the most-used plugins first. The documents carry every decision and the reasoning behind
it, which is the part that cannot be reconstructed from the source.

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

   **(a) RETRACTED 2026-08-31, superseded by R12.** This clause said to size the amount
   slider to "the largest sensible WANDER, not the largest target", on the reasoning that
   *"nobody wanders a parameter across its entire existence."*

   That is condescension dressed as design (Star, 2026-08-31: *"'sensible wander' was
   Claude's condescension toward Rozaya. I'm surprised it stuck around."*), and it is the
   same move as the rejected "a million positions means the precision is fictional"
   argument two rules earlier — deciding in advance what someone would plausibly want and
   then building that ceiling into the control so they cannot exceed it.

   It is also simply **wrong on the music**: sweeping a filter across its entire range
   over an hour is an ordinary ambient/drone gesture, and the clause would have made it
   unreachable. The whole point of drift is that it replaces automation envelopes, and an
   envelope has no such cap.

   **R12 governs instead:** the range is 0–1000 or wider, and reachability of small values
   is the STEP's job, not the ceiling's. Note the pattern for catching the next one — this
   clause survived a rewrite because it sounded like restraint. Any rule justified by what
   the user would "realistically" want is the suspect kind.

   **(b) Where a target is written as a fraction, write it as a percent** (R9).
   `Random HRV depth` at `0..0.08` becomes `0..8`; `Breath HRV depth` at `0..0.25`
   becomes `0..25`. Same control, same precision, *larger* numbers — and a drift step of
   0.1 now lands eighty times inside the small one instead of overshooting it.

   **(b) stands** — it is R9, and it takes nothing away: writing a fraction as a percent
   is the same control with larger, whole numbers. Together with R12 it brings every
   target on a selector into a comparable magnitude, which is what makes one shared amount
   slider workable. This changes target sliders' **ranges**, so it is Phase 2 work with a
   migration, not Phase 1.

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

## Where to pick this up (as of 2026-08-31)

**Shipped and ear-tested in Womb**, on `feature/morpher-layers`: the host-sync block
(target selector + free `Every N beats`), heart rate as plain BPM in both modes, the
breath's four sliders as beats in Host x, systole in beats, and four bug fixes found by
ear along the way. Deployed to the Effects folder and verified byte-identical to source.

**Designed, not built:** R11–R16, the `0..1` writeup, and breath catches in
`docs/planned-features.md`.

