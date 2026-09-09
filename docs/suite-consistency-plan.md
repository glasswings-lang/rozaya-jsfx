# Suite consistency plan — THE RULES

**Budget: 1600 lines.** Run `python tools/doc_budget.py` before committing.

**This file is a reference you check, not a list of work.** It holds the rules
R1–R22 and nothing else. Look up the rule you need, obey it, and close the file.

**Where the other two thirds went, 2026-09-08.** This document used to be 2742
lines of three different things stacked together: the rules, a backlog of what
each plugin is owed, and the history of how each decision was reached. Sessions
opened it to check one rule and came back with a to-do list, then started work
Rozaya had not asked for on plugins she had not yet heard. The rules are the
smallest part of what was here and they were the hardest to find — they are
numbered R1 to R22 and they were scattered across five parent sections in
non-numeric order, with R17 buried inside "Where to pick this up" and R18 inside
"Part 6 revised".

- **`docs/backlog.md`** — what each plugin is owed, the phase ordering, the open
  questions. **Nothing in it is a job you may start unasked.**
- **`docs/plan-history.md`** — why each rule is what it is, the shapes that were
  killed, the cost measurements, and the dated status notes.

Every line of the old document is in one of these three files, verbatim. Nothing
was rewritten in the split.

**The rules are in numeric order here for the first time.** R11 is superseded and
lives in the history; its slot below says so.

---

## The rules, in order

- **R1** — The descriptive name wins, and propagates to both ends
- **R2** — Target strings are derived from slider labels, mechanically
- **R3** — Every target must have a slider
- **R4** — Units go in parentheses at the end of the name
- **R5** — Sentence case throughout
- **R6** — One phrasing for mode dependence, and only where meaning actually changes
- **R7** — The rate triple is contiguous, always
- **R8** — Step size is chosen from the range, not typed
- **R9** — Where a natural unit forces a bad range, change the unit
- **R10** — A picker never hides the value it writes
- **R11** — One tempo-sync block — SUPERSEDED BY R20, 2026-09-04
- **R12** — Ranges are 0–1000, or −1000–1000 where the sign means something
- **R13** — No multipliers. Anywhere. (Host x is not a unit.)
- **R13a** — The sigh multiplier is the same bug, wearing a different hat
- **R13-revised** — Host x stays a rate mode; Rate Value means BEATS there
- **R14** — Speed Ramp states a DESTINATION, not a delta
- **R15** — The sigh gets its own four segments, and the multiplier goes
- **R16** — It is `Ramp`, not `Speed ramp`
- **R17** — There are no unitless sliders. "Depth in what?" must have an answer
- **R18** — New sliders go where they belong. Only enum OPTIONS append.
- **R19** — Pan modes need one canonical order
- **R20** — THE RATE BLOCK. This is settled. Do not redesign it.
- **R21** — the host modes name their DIRECTION, and there are two
- **R22** — THE PITCH BLOCK. Settled with Rozaya 2026-09-08. Not built.

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

## R1. The descriptive name wins, and propagates to both ends

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

## R2. Target strings are derived from slider labels, mechanically

> A target option string is the slider's label with its trailing parenthetical removed.

`Heart rate (BPM)` → target `Heart rate`. `Sweep rate` → target `Sweep rate`.

This is the rule that makes the whole thing **enforceable**: a linter can strip the
parenthetical from every slider label and assert that every target option matches one.
Without a mechanical rule this drifts again within two sweeps.

## R3. Every target must have a slider

A target list may not offer something the user cannot see or set. Two consequences:

- **Breath Generator gains `Breaths per minute`.** It is the dedicated breathing plugin
  and it currently lets you drift and ramp a rate it gives you no way to set. Womb has
  had this slider since v2.
- Where a target names one entry of a **selector-backed group** (Melody v2's `Voice`
  selector, Morpher's `Layer` selector), the target string is `<selector option> <slider
  label minus parenthetical>` and the plugin page must say it is reached via the
  selector. This is the one legitimate case of a target with no dedicated slider. See
  Open Question 1.

## R4. Units go in parentheses at the end of the name

`Frequency low (Hz)`, not `Frequency Low Hz`. Currently the suite runs both forms, plus
a mixed form (`Inhale Duration sec (shape only in Host x)` -- since fixed, see the
2026-08-30 addendum). Four different spellings
exist for a cutoff frequency in Hz across four plugins.

Additional qualifiers go inside the same parenthetical after the unit:
`High cut (Hz, 20000 = off)`.

For **enum** sliders the unit belongs in the name and the options stay bare —
`{-12,-24,-36}Slope (dB/oct)` — so NVDA does not re-read the unit on every arrow step.
This is already the convention (2026-07-09); it stays.

## R5. Sentence case throughout

`Start delay`, not `Start Delay`. `Drift mode`, not `Drift Mode`.

The suite currently uses Title Case for the transport block and sentence case for the
drift/ramp blocks, which is why `Start Delay` and `Speed ramp start delay` sit in the
same file. Sentence case is the newer convention and the larger block.

**Note honestly: this is a source-consistency fix, not an accessibility one.** NVDA does
not announce capitalisation. It matters for whoever reads the code, including us.

## R6. One phrasing for mode dependence, and only where meaning actually changes

Six phrasings are in use today (`(or multiplier in Host x)`, `(shape only in Host x)`,
`(Host x only)`, `(Host x; writes …)`, `(Own BPM only; …)`, `(in Rate Mode units)`).

New rule: annotate a slider **only where Rate Mode changes what it means**, not merely
what it scales — and use one form, `(… in Host x)`. Womb's four breath durations
genuinely become shape-only, so they keep an annotation. A rate slider that merely
becomes a multiplier does not need one, because under R7 the Rate Mode slider is sitting
right next to it saying so.

## R7. The rate triple is contiguous, always

`<rate slider>` → `Rate mode` → `Host ratio`, in that order, adjacent, no exceptions.
This is what makes `Rate Value` legible and it is what dissolves the `Sweep Rate` /
`Pan Sweep Rate` confusion.

Applies to the secondary rates too: `Pan sweep rate` → `Pan sweep rate mode`. Note the
current suite calls this one `Unit` where the primary is called `Mode`; standardise on
**`mode`**. Sweep Dwell's pan unit offers `Host x` and the other two filters' do not —
they should all offer it.

## R8. Step size is chosen from the range, not typed

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

## R9. Where a natural unit forces a bad range, change the unit

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

## R10. A picker never hides the value it writes

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


## ~~R11. One tempo-sync block~~ — SUPERSEDED BY R20, 2026-09-04

**Do not build this shape.** Its `Sync to host` / `Host sync target` /
`Every N beats` block is what Womb and Melody used to carry, and both have
converted away from it. The full text, and the measurement that killed it,
are in `docs/plan-history.md`. R20 below is the rule that replaced it.

## R12. Ranges are 0–1000, or −1000–1000 where the sign means something

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

## R13. No multipliers. Anywhere. (Host x is not a unit.)

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

## R13a. The sigh multiplier is the same bug, wearing a different hat

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

## R13 REVISED — Host x stays a rate mode; Rate Value means BEATS there (2026-09-02)

**SUPERSEDED IN PART BY R20 (2026-09-04).** Everything here about Host x being
a rate mode and Rate Value meaning beats is CORRECT and still in force. What R20
overturns is the paragraph below headed *Where the heavier R13 shape still earns
its keep* — it does not earn its keep anywhere, and that paragraph is what sent
multiple sessions to build a sync block that the measurements say nobody uses.

**This supersedes R13's "split Rate mode from a Sync to host switch" for every
plugin with a single sync target.** Rozaya raised it and the reasoning is
better than the original.

## What R13 got right and what it got wrong

Right: the **multiplier** was dishonest. In Host x, Rate Value silently became a
factor on the project tempo and nothing on the control said so.

Wrong: the diagnosis. R13 blamed Host x's *position* -- "sync is not a unit" --
and moved it out of the rate mode list into its own switch. But **Host x is a
rate mode.** It is one of the ways you say what the rate is. Rozaya:

> "specify that rate value doesn't apply to host x, and/or make it mean every n
> beats in host x and specify that, while leaving host x where it is, as what it
> is -- a rate mode"

## The revision

Leave `Host x` in the Rate Mode enum. In that mode, **Rate Value means beats per
cycle**, and the label says so.

This is not a new pattern, it is the existing one continued. Rate Value already
changes unit with the mode: BPM, then seconds, then Hz. Beats is the fourth. It
also satisfies the standing rule that a control must never change meaning
without saying so on the control itself.

**It keeps what the multiplier was for.** Rate Value is a free float, so *every
3.7 beats* stays reachable. The original argument for a multiplier was that a
note-division grid would take the irrational ratios away and this suite is phase
music -- "I'm not just designing for locks." A free beat count loses nothing.

**And it costs no new sliders.** No `Sync to host`, no `Host sync target`, no
`Every N beats`. The `Host ratio` multiplier picker becomes redundant.

## ~~Where the heavier R13 shape still earns its keep~~ — WRONG. KILLED BY R20, 2026-09-04.

**This paragraph is the single most expensive sentence in this document. Do not
act on it.** It said the sync block earns its keep where a plugin syncs more
than one thing independently, and named Melody Phase. It is wrong twice over:

- **A second rate does not need a selector. It needs its own rate mode.** One
  Rate Value cannot express two beat counts — true, and irrelevant, because the
  second rate has its own value. Melody's pan lacked a MODE, not a selector.
- **Nobody has ever used the capability.** 73 Melody instances, 27 synced, all
  27 targeting `Rate value`. Zero pointing at the pan.

The original text is preserved here because it was quoted back at Rozaya as a
justification and they could not evaluate it: *"Only where a plugin has more
than one thing to sync independently. Melody Phase syncs the sequencer and the
pan separately, which needs a target selector and a per-target beat count; one
Rate Value cannot express two. Melody keeps what it has."* Read R20 instead.

## The recipe — how R13-revised is applied to one plugin

Proven on `polyrhythm_phase` and `polyrhythm_phase_v3` (commit `9302c01`).
Five edits, none of which move a slider id.

**1. The label carries the unit.** The Rate Value declaration gains
`: BPM / sec / Hz / beats per cycle`. This is the standing rule that a control
never changes meaning without saying so on itself.

**2. The conversion, one line.** In the plugin's rate function:

    rmode == 3 ? max(raw_rate, 0.001) :        ->   rmode == 3 ? 1 / max(raw_rate, 0.001) :

At the nominal 60 BPM one beat is one second, so N beats per cycle is 1/N
cycles per second; `host_scale = tempo/60` in `@block` then makes it
`tempo/(60*N)`. **Check the plugin actually uses the nominal-60 pattern before
assuming this line is right** — grep for `host_scale` and confirm the tempo is
applied in `@block` rather than inside the rate function.

**3. Retire the Host ratio picker.** Change its guard to `0 ? (` with a comment
saying why, and its `slider_show(...)` to `slider_show(sliderN, 0)`. **Do not
delete the slider** — ids can never be renumbered. It existed only to spare you
arithmetic on a multiplier, and "every 4 beats" is now typing 4.

**4. Drop the landing block.** The `rate_mode_inited && last_rate_mode !=
rate_mode ? (...)` block stamped the picker to "1 per beat" and the rate to its
multiplier, because meeting a bare multiplier first was the trap. There is no
trap now. Replace the whole block with `rate_mode_inited ? last_rate_mode =
rate_mode;`, and delete the `slider_show(rate slider, ...)` line that hid the
rate — it is always visible now.

**5. The plugin page.** Replace the "multiplier of the project tempo"
explanation, retire the Host ratio entry, and delete any section teaching the
old ratio-list workflow.

**Step 2a — guard the zero end, and this one nearly shipped.** Beats-per-cycle
INVERTS, so a naive `1 / max(raw, 0.001)` clamps the DENOMINATOR and turns 0
into 1000 Hz. Under the old multiplier 0 clamped to 0.001 and meant "effectively
stopped"; it must keep meaning that, not the exact opposite. This bites wherever
the rate can arrive from a SIGNED slider: in Polyrhythm, `Vn Drift / Rate` spans
-1000..1000, defaults to 0, and in Independent mode IS the voice's rate -- so a
fresh voice would have screamed at audio rate. Write it as
`raw > 0.001 ? 1 / raw : 0.001`. Dapple and Bubbler are exempt only because
their rate slider's declared minimum is 0.001 and it can never reach zero.
Caught by Rozaya asking "is that every 4 beats per voice?".

**Verify each one:** slider count unchanged, all five sections paren-balanced,
lint problem count unchanged from before the edit, and the arithmetic sanity
check — at 205 BPM a value of 4 must give one cycle every 1.171 s.

### The recipe's line-level anchors DO NOT generalise — checked 2026-09-02

Do not batch this. Measured across the nine free plugins:

| plugin | uses the nominal-60 `host_scale` pattern | has the `rmode == 3 ? max(raw_rate,...)` line |
|---|---|---|
| `rhythm-track`, `shepard-scale`, `shepard-tone` | yes | only `shepard-tone` |
| `dapple`, `bubbler`, `stereo-phaser`, `resonance_bank`, `sweep-dwell-filter`, `heartbeat gen` | **no** | no |

`dapple` and `heartbeat gen` have no `== 3` branch at all, so **Host x is not at
index 3 in their enums** — their rate mode lists are shaped differently. Six of
the nine apply the tempo somewhere other than a `host_scale` in `@block`, which
means step 2's one-line conversion is wrong for them and would need working out
against whatever they actually do.

So the five edits are the right SHAPE for every plugin, but only the two
Polyrhythms and possibly `shepard-tone` share the exact anchors. For each of the
others: find its Host x enum index, find where the tempo is applied, and derive
the beats conversion from that before touching anything. The arithmetic check is
the same everywhere and does not care how it is implemented — **at 205 BPM a
value of 4 must give one cycle every 1.171 s.**

The caveat in step 2 caught this on the first batch attempt. Keep it.

**Order.** Do the nine free plugins first (`dapple`, `bubbler`, `stereo-phaser`,
`resonance_bank`, `sweep-dwell-filter`, `heartbeat gen`, `rhythm-track`,
`shepard-scale`, `shepard-tone`) — nothing stored is on Host x, so no migration
and no snapshot. Commit each. Then the three with real instances
(`full-feature-sweeping-filter` 6, `Full_Feature_Tremolo` 4,
`womb_sound_generator_v3` 1), which need a snapshot and a **reciprocal** value
conversion: a stored multiplier of 0.5 becomes 2 beats per cycle. Do not start
those without room to snapshot, migrate, verify independently and ear-test.

**Womb is a special case:** it already has `Every N beats (Host x)` as a
separate slider, gated on its rate mode. Converting it means Rate Value takes
that job and the extra slider retires the same way the picker does — check
which of the two the project instances actually rely on before touching it.

## R14. Speed Ramp states a DESTINATION, not a delta

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

## R15. The sigh gets its own four segments, and the multiplier goes

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

## R16. It is `Ramp`, not `Speed ramp`

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

## R17. There are no unitless sliders. "Depth in what?" must have an answer

Star, 2026-08-31: *"we've always gone — depth in what? x in what? what's the unit?"*

This is sharper than R9 and it supersedes how R9 was being applied. Rewriting `0.25` as
`25` makes the number easier to read and leaves it **just as unitless**. The reader's
question was never "how many decimal places", it was **"twenty-five of WHAT?"**

**The test:** ask "x of what?" out loud.

- If the answer is a real quantity — BPM, Hz, dB, seconds, beats, semitones — **use that
  quantity.** It is not a proportion, it is a measurement that somebody normalised.
- If the answer is genuinely a proportion of a nameable thing, **name the thing in the
  slider**: `Inhale fade in (% of inhale)`, `Bloodflow attack (% of cycle)`.
- If the answer is *"of itself"* or *"of the maximum"* — the control is an abstraction
  with nothing behind it, and that is the bug. Find the underlying quantity.

**The worked example, and it is another propagation failure.** Heartbeat Generator has
`Breath HRV Depth` at `0.0..0.25` and `Random HRV Depth` at `0.0..0.08`. Traced to its
consumption:

```
cycle_len = cycle_len_base * (1.0 - breath_mod + rand_hrv)
```

They are fractions of the beat interval. **Womb already names this quantity properly** —
`Heart with breath (BPM peak-to-peak)` — so the same measurement is honest in one plugin
and an unlabelled decimal in its sibling. Heartbeat's two become **BPM peak-to-peak**,
matching Womb. The fraction-to-BPM relation is not linear across tempo, but Womb has
worked in BPM and converted internally since v2, so the precedent is built and tested.

**Others failing the test today:** `Brightness` (0..1 — of what? it scales a filter, so it
has an underlying Hz or a mix), `Bloodflow Dicrotic Level`, `Bloodflow Resonance` (the
filter sweep already learned this one — resonance is honestly expressed in dB of peak, see
the 2026-08 filter recalibration), and both `Stereo Width` controls (a proportion of full
decorrelation, so at minimum `% of full width`).

**Note the pattern, since this is the fourth tonight**: the multiplier, the `Ramp` rename,
the missing sigh, and now this — each is a good decision made in ONE plugin and never
carried to its siblings. The suite's real failure mode is not bad decisions, it is
**unpropagated good ones**.

## R18. New sliders go where they belong. Only enum OPTIONS append.

Decided 2026-08-31 with Rozaya, correcting a rule I was about to apply past its purpose:
*"the rule for appending to the end is if it's a new feature, not if it's an extension of
a thing that should have been there all along... we're doing a big reorder of all the
things. We shouldn't be pushing them one by one. That's kind of an embarrassment."*

**Is append-at-the-end a real convention outside this repo?** Yes — and the reason it
exists is the whole point. VST, AU and CLAP identify parameters by index or ID, and hosts
save automation and preset state against those. Insert a parameter mid-list and every
saved preset and automation lane silently points at the wrong control. VST3's stable
parameter IDs exist specifically to escape this; CLAP has its own scheme for the same
reason.

**So the convention is a workaround for not being able to migrate saved state.** Where
the state CAN be migrated — and this suite migrates it, deliberately, as the entire
purpose of this document — the reason evaporates. Applying it during a reorder would bake
the ordering problem into the release meant to fix it.

**What protects a third party is the self-migration, not the append rule.** The plugin
detects an old project on load from the blob's version magic and repairs the values in
memory, on any machine, with nothing for anyone to run (Part 4). Someone with no old
projects simply gets the clean layout. **That mechanism must be built and verified before
any renumber ships** — it is the gate, and Rozaya's concern is exactly right: *"the last
thing I want is for some motherfucker to be shipped a bullshit plugin and think it doesn't
work and think the rest of them are like that."*

**The one genuine exception, for a different reason.** An enum **option** is stored as an
index *inside* a slider's value. Insert `Square` into the middle of the waveform list and
every saved project's waveform changes character; insert a drift target and every
per-target bank points at the wrong parameter. No slider-line migration fixes that
cheaply, so **enum options always append** — waveforms at the end of the list, drift and
ramp targets at the end of theirs.

**The rule, then:**

| thing | where it goes |
|---|---|
| a new slider | **its logical position** in the layout |
| a new enum option (waveform, drift target, mode) | **the end of the list** |
| an existing slider | wherever the authored layout puts it |

## R19 — Pan modes need one canonical order (raised 2026-09-02)

**Rozaya:** *"the types of panning are just kinda pell mell put in there, and
that's confusing as shit. I'm not gonna ship something like that on any plugin
... I don't wanna make a release like that. That's kind of embarrassing."*

**Blocks a release. Does not block pushing to master.**

## What the mess actually is

Every plugin's Pan Mode list grew by appending, so each one is in the order its
features happened to arrive rather than any order a person could reason about.

- **Polyrhythm** now reads: Tremolo, Increment, Spread, Spread Reversed,
  Alternating, Alternating (Flipped), Distributed, Distributed (Flipped),
  Distributed (Ping-pong), Converging, Converging (Ping-pong), Diverging,
  Diverging (Ping-pong), **Alternating every 2, every 4, every 8**. The three
  extra Alternating variants are at 13-15, with the whole Distributed /
  Converging / Diverging family sitting between them and the Alternating they
  belong to. That was done on 2026-09-02 and it is the clearest example.
- **Full Feature Tremolo** has no `Alternating (Flipped)`; both sweeping filters
  do.
- **rhythm-track** has a shorter list in a different order, plus `Accent L /
  Weak R` which exists nowhere else.
- The oscillator plugins lead with four modes (Tremolo / Increment / Spread /
  Spread Reversed) that no effect plugin has.

## Proposed order — group by WHAT THE PAN DOES

Three groups, in this order, each plugin including only the members it has:

1. **Still** — the pan does not move on its own.
   `Mono` · `Spread` · `Spread Reversed` · `Accent L / Weak R`
2. **Stepped** — the pan moves one position per cycle / note. Two-position
   members first, then multi-position.
   `Alternating` · `Alternating (Flipped)` · `Alternating every 2` ·
   `Alternating every 4` · `Alternating every 8` · `Distributed` ·
   `Distributed (Flipped)` · `Distributed (Ping-pong)` · `Converging` ·
   `Converging (Ping-pong)` · `Diverging` · `Diverging (Ping-pong)`
3. **Continuous** — the pan travels on a clock of its own.
   `Tremolo` · `Increment` · `Pan Sweep` · `Pan Sweep (Flipped)` ·
   `Linked Sweep`

The grouping is the useful part: **still / stepped / continuous** is the
distinction a listener actually hears, and it tells you immediately whether a
mode can drift against the material (only group 3 can).

## R20 — THE RATE BLOCK. This is settled. Do not redesign it. (2026-09-04)

**Supersedes R11 entirely and completes R13-revised.** Decided with Rozaya on
2026-09-04 after five separate sessions had each reached for a different shape.
If you are reading the suite for "how does tempo sync work here", stop at this
section — everything below it is history and two of the shapes it describes are
dead.

## The rule, in full

**Every rate in a plugin carries exactly two controls, adjacent, in this order:**

```
<Name> rate value        free number
<Name> rate mode         {BPM, Seconds, Hz, Host x}   -- ALWAYS these four, ALWAYS this order
```

- **In Host x, the rate value means EVERY N BEATS.** One cycle takes N beats of
  the project. Bigger is slower. It is a free number, so `0.333333` — every
  three beats — is as reachable as `4`.
- **The mode list is identical everywhere.** Same four entries, same order, in
  every plugin, for every rate. This is the whole point: the suite is navigated
  by arrowing the parameter list one control at a time, so position 3 must not
  mean Hz on one control and BPM on the one under it.
- **A plugin with two rates has two of these pairs**, each complete and
  self-contained. The pan gets its own rate value and its own rate mode. It does
  not borrow the main rate's mode, and nothing points across at it.

**What is forbidden, and each of these has been built at least once:**

- No `Sync to host` switch. Host x is a rate mode; a second switch is a second
  way to say the same thing.
- No `Host sync target` selector. Each rate carries its own sync.
- No separate `Every N beats` slider. The rate value IS that number in Host x.
- No `Host ratio` picker, or any control whose job is to write a value into
  another control. All seven were retired 2026-09-04 and they stay retired.
- No multiplier, anywhere, in any mode.

## Why the two dead shapes existed, so nobody re-derives them

**R11's sync block (Melody, Womb).** Its stated justification was that a plugin
syncing more than one thing independently cannot express two beat counts in one
rate value. **That is true and it is the wrong conclusion**, because you do not
use one rate value for two rates — you give the second rate its own pair.

The real constraint was narrower and is worth stating exactly, because it is a
missing control rather than a limitation: **Melody's `Pan base rate` (slider 21)
has no mode of its own.** Read `rate_to_cycle_seconds(pan_base_rate, rate_mode)`
at melody_phase.jsfx:1116 and :1492 — the pan is handed the SEQUENCER's
`rate_mode`. So there was nowhere to put Host x for the pan, and three sliders
were added to reach around the outside. One slider — a pan rate mode — does it
better, and untangles the pan from the sequencer's units as a side effect.

**Measured, and this is the number that ended the argument.** Across all 73
Melody Phase instances in the library, 27 have `Sync to host` ON, and **all 27
have the target set to `Rate value`. Not one points at the pan.** The capability
those three controls exist to provide has never been used, and it cost three
positions in the parameter list on every instance since it shipped.

**R13's "sync is not a unit" split.** Overturned by R13-revised on 2026-09-02 and
still dead. Host x IS a rate mode — it is one of the ways of saying what the
rate is.

## The near-miss this rule must not repeat

**BEFORE DELETING ANY CONTROL THIS RULE RETIRES, OPEN THE BLOCK AND READ IT.**
On 2026-09-04 a plan document described Womb's `Every N beats` as a leftover and
it is not — it is half of a working pair. Rozaya: *"host x is the rate mode.
every N beats is getting the multiplier out of there. neither of them work
alone."* R20 does retire it, but **by moving its number into the rate value,
with a migration**, which is a different operation from deleting it. A retired
`Host ratio` picker writes one slider and does nothing else; a working half of a
pair does something the other half depends on. Those look identical from the
slider list and completely different from inside.

---

## R21 — the host modes name their DIRECTION, and there are two (2026-09-05)

**Extends R20; does not overturn it.** One rate value, one rate mode, same
adjacency. What changes is that the mode enum gains a fifth entry and the fourth
is renamed to say what it does.

```
BPM / Seconds / Hz / Every N beats / N per beat
```

- **`Every N beats`** is what `Host x` already was: one cycle takes N beats.
  Renamed only — **index 3 does not move**, so the 10 instances stored on it are
  untouched.
- **`N per beat`** is new at index 4, appended, so nothing shifts. N cycles fit
  in one beat.

## Why, and it is a gap the retired pickers used to cover

The pickers deleted on 2026-09-04 offered **both directions in words** — their
list ran *"every 8 beats … 1 per beat … 8 per beat"*. Retiring them kept the slow
half and silently dropped the fast one, so *eight cycles per beat* became
`0.125`: three decimal places, and a reciprocal to work out. That is the exact
arithmetic this suite exists to remove, and Rozaya found it by hitting it:
*"Rate value should not have to be set to 0.5 to get 8 bubbles every beat."*

**Neither direction is right on its own, because they are reciprocals.** Whichever
way the number runs, one end is whole and the other is fractional. Polyrhythm
lives at the slow end — *every 3 beats* against *every 5 beats* is how voices walk
past each other — and Bubbler and Dapple live at the fast end. So the mode picks
which end of your own music is arithmetic-free.

**The sound is identical either way.** Both reach the same rates; only the typing
differs. That is worth stating because it means this can never be judged by ear,
only by use.

## The conversion, per shape

At 60 BPM one beat is one second, which is the nominal both host modes are
computed against (never remember a tempo — `@init` wipes it on play).

| mode | nominal cycles/sec | then |
|---|---|---|
| `Every N beats` (3) | `1 / N` | × `host_scale` (= tempo/60) |
| `N per beat` (4) | `N` | × `host_scale` |

So `N per beat` computes exactly like **Hz** does, and only the host_scale gate
differs. Every `rate_mode == 3` gate that means "are we host-synced" becomes
`>= 3`; the ones that mean "which conversion" stay exact.

**Three shapes to apply it to:** a shared `rate_to_hz()` (both Polyrhythms,
Shepard Tone), inline branch chains (most of the rest), and the Morpher, which
CONVERTS the value on a mode switch and so needs its conversion table extended
rather than a branch added.

---

## R22 — THE PITCH BLOCK. Settled with Rozaya 2026-09-08. Not built.

> **ATTRIBUTION WARNING, added 2026-09-09.** Rozaya, on being told that parts of
> this rule were "already settled": *"No, you settled that on your own. I had
> nothing to do with those decisions. That's a problem."*
>
> **She is right, and this section is the worst offender in the repo.** Quoted
> text below is hers. Everything unquoted is Claude reasoning written in the same
> confident voice, and at least three pieces of it were then cited back to her as
> settled decisions:
>
> - **The deferred list.** She said *"Morpher and Passage are their own
>   discussion there."* — two plugins. Sustain Looper and Bubbler are mine.
> - **The build order** — Melody and Shepard Tone's voice selectors before the
>   migration — is my slider-count analysis, not her decision.
> - **"`Note` is NOT one of the modes"** was a JSFX limitation promoted to a
>   principle, and she overturned it on 2026-09-09.
>
> **Before citing anything here as settled, check whether it is in quotation
> marks.** If it is not, it is a proposal that has been sitting still long enough
> to look like a decision.

**Status: RULE AGREED, NOTHING BUILT.** This is deliberately the R20 order of
operations — write the rule, settle it, *then* build — because that is what
finally worked for the rate after five sessions each guessed differently. The
pitch has more at stake than the rate did: **there is no free window.** Every
pitch value in this suite is in a real project and IS the sound. There is no
equivalent of the nine plugins that had nothing stored on Host x.

## The rule

> **Every pitch carries a value and a mode, adjacent, in that order:
> `Pitch value (Hz / semitones / cents)`, then `Pitch mode`. The mode is always
> `{Hz, Semitones, Cents}` — always those three, always that order. A plugin
> with two pitches has two complete pairs.**
>
> **A plugin that GENERATES ITS OWN SOUND also carries a `Note` picker,
> immediately before the pair, and the pair then reads as an offset from that
> note. One note list everywhere: the FULL MIDI RANGE, C-1 to G9 (128
> notes, 8.18 Hz to 12543 Hz).**
>
> **All four names are R4/R5 compliant** — sentence case, unit in parentheses at
> the end. The value slider lists its three units the way `Rate Value (BPM / sec
> / Hz / beats per cycle / per beat)` already does in four plugins, which is
> also the fix Rozaya asked for on 2026-09-07 after a bare `Rate Value` named
> neither its unit nor its scope.
>
> **`Fine tune` is a SECOND pair, always present, always after the first:
> `Fine tune value`, then `Fine tune mode`, the same `{Hz, Semitones, Cents}`.**
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

## ~~Why `Note` is not one of the modes~~ — OVERTURNED 2026-09-09

**This section argued at length that `Note` could not be one of the pitch modes,
because a plugin that did not make the audio does not know its pitch. Rozaya
overturned it the first time she navigated the built block:** *"note is not
master here. it's one way of expressing pitch, period. Don't have two
finetunes."*

She was right, and the argument was a workaround wearing a rule's clothes. The
real constraint is that a JSFX slider can be a list of note names or a
continuous number, never both — which I could not express, so I promoted it to a
principle instead of saying it out loud. `docs/designing-for-dyscalculia.md` and
`CLAUDE.md` both already name that exact failure.

**Making `Note` the master also created a second fine tune.** Once the pitch
value is an OFFSET from a note, it stops being the pitch and becomes a fine
adjustment — so the block carried two of those, with the wrong half labelled as
coarse.

**The replacement** — mode first, a note name that is a real control in
Semitones mode and hidden elsewhere, the pitch value, then exactly one fine
tune — is in `docs/layouts/breath-gen.md`. Old text at commit `11b58ac`.

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

## `Fine tune` SURVIVES, and gets its own mode — the fourth reduction, caught

An earlier draft of this rule deleted `Fine tune (cents)`, on the reasoning that
the pitch value-and-mode pair "does its job and more, and keeping both would be
two ways to say one thing". I even flagged it as the one reduction here that
came from correctness rather than tidying. It did not.

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

## The superseded reasoning, kept so it is not re-derived

The first draft of this rule offered `{Note, Hz}` only, on the reasoning that a
heartbeat thump is a frequency and a drone voice is a note. **Rozaya killed
that, and was right to:** *"the minute I'm making decisions like this is the
minute I say include all of them."*

That draft was TRIAGE, which this suite's own rule forbids — a feature goes
everywhere its parent already is, and deciding per plugin which controls a
person may reach for is the same mistake in a different coat. It also had a
concrete cost I had not noticed: **`Pitch (semitones)` is how the Morpher,
Passage, Sustain Looper and Bubbler already state pitch.** A `{Note, Hz}` list
gives those four nowhere to land, so the "tidy" rule would have forced a unit
change on 122 Morpher instances plus Passage's, for nothing. Rozaya named the
three missing units in five words and the gap closed.

**Semitones and Cents are both offsets, and both are needed, for exactly the
reason `Every N beats` and `N per beat` are both needed.** They are the same
quantity at two scales. Keeping only semitones means seven cents is typed as
`0.07` — arithmetic, which is the barrier this suite exists to remove.

**What the offset modes are an offset FROM** is the plugin's own natural
reference: the captured sample's pitch in the Morpher and Passage, the loaded
loop in Sustain Looper, the base note elsewhere. That is what those controls
already mean; the mode only names it.

## Why the FULL MIDI range, and why measurement did not decide it

**The note list is C-1 to G9 — MIDI notes 0 to 127, 8.18 Hz to 12543 Hz.** It is
that because that is the standard every other piece of music software uses, and
a standard is a principled boundary. It is NOT sized to anything in this
library.

**Three drafts of this line got smaller and smaller for the same bad reason, and
the correction is a rule, not a preference.** I wrote C1–C7 first (sized to just
cover the stored values), then C0–C8 after Rozaya said *"let's use that to widen
ranges, not reduce them"*. Both were still derived from her projects. She named
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
shifts every saved note by twelve semitones. This is the R18 append-never-insert
rule at enum scale, and it is the one genuinely risky part of this job.

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

> **`Spread value` then `Spread mode`, always `{Cents, Semitones, Hz, %}`,
> always that order.**

Only one thing is genuinely fixed here: Sustain Looper's `Spread (detune
amount)` is 0-100 with **no unit at all**, so it has to be told which of the
four it means. It is a percentage of its existing internal range, so it becomes
`%` and no stored value moves.

## How this sits with the rules that already exist

**Checked 2026-09-08, after Rozaya said "you need to look at existing rules,
please" — and she was right, two of these I was re-deriving from scratch.**

- **R4 / R5 — names.** Sentence case, unit in parentheses at the end. This
  sweeps up a pile of existing violations in the pitch surface on the way past:
  `Tuning Reference Hz` → `Tuning reference (Hz)`, `S1 Frequency Hz` →
  `S1 frequency (Hz)`, `Inhale Frequency Hz`, `Exhale Frequency Hz`,
  `Fundamental Hz`, `Root Note`, `Center Octave`, `Octave Count`, `Base Note`.
  All free — names are not stored in projects.
- **R6 — mode dependence is annotated once, where meaning changes.** The value
  slider does not need a `(in Pitch mode units)` tag, because under the
  contiguity rule the mode slider is sitting next to it saying so.
- **R7 — contiguity.** R22 is R7 applied to pitch: value then mode, adjacent, no
  exceptions, and a second pitch gets its own complete pair. (R7's own text
  still names `Host ratio` as the third member; that was retired by R20 and R7
  is stale there, not R22.)
- **R9 — ALREADY SAYS MOST OF THIS, and I did not check before writing it out
  again.** R9: *"Prefer whichever unit makes ordinary values whole numbers:
  percent over fraction, dB over linear gain, **cents or semitones over
  frequency ratios**."* That is the pitch mode list, written down on 2026-08-31.
  R9 also already carries Rozaya's widening principle in its own words: *"This
  rule never removes range or precision, and must not be read as doing so."*
- **R12 — the range, and it is DECIDED, not open.** An earlier draft of R22 left
  the `Pitch value` range as an open question for Rozaya. It is not one. R12
  says a numeric slider spans 0–1000 or −1000–1000, and carve-out 1 says
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

An earlier draft of this rule gave Heartbeat TWO complete pitch blocks, one for
each thump, and would have given Womb four. That is ten and twenty sliders where
there are two and four, and the number grows every time a plugin gains a sound.

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

What is settled is the GENERAL rule: `Note` cannot be one of the modes, because
a plugin that did not make the audio does not know its pitch. That reasoning is
why the mode list is three units and it stands.

What is NOT settled is what those two actually end up carrying. An earlier draft
of this rule wrote "they carry the pair alone" into the rule statement as though
it were decided. It is not. They are the suite's two spectral plugins, they
share a capture mechanism, Passage has an owed reorder blocked on what it is
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

## The one place R22 CONTRADICTS an existing rule, and the argument for it

**R18 says enum OPTIONS always append. Widening the note list from C2–C6 to
C0–C8 PREPENDS two octaves, which is an insert at the front.** An enum option is
an index stored inside a slider's value, so every saved note would shift by 24
semitones. This is the one part of R22 that is not merely new.

**R18's own reasoning is why the exception is arguable here.** It says the
append rule is *"a workaround for not being able to migrate saved state"*, and
that the enum carve-out exists because *"no slider-line migration fixes that
cheaply."* For the note list it does: adding 24 to one integer per voice is
exact, provable and verifiable by name against a snapshot — it is arithmetic,
not inference, which is the line `tools/` scripts already have to stay on.

**But the gate R18 names is real and is NOT built.** What protects a third party
is the plugin's own self-migration from the blob's version magic (Part 4), so it
repairs an old project on any machine with nothing for anyone to run. That does
not exist yet. Today the only projects are Rozaya's and a script reaches all of
them — **and no release has shipped, by standing decision, precisely so that
stays true.**

**So: the note-list widening is allowed, and it is allowed for a reason that
expires.** If a release ships before this lands, it stops being allowed and the
self-migration has to be built first.


---

## Part 2 — Canonical layout

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
2. Its rate                    rate value, then rate mode          (the R20 pair)
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
- **A modifier is numbered immediately after the thing it modifies.** Unit
  selectors, shape selectors, mode selectors. This is the rule that puts
  `Drift period unit` directly after `Drift period`, and `Attack shape` directly
  after `Attack` rather than after both amounts.
- **A second rate carries its own complete pair** (R20). The pan gets its own
  rate value and its own rate mode, inside the pan group. It never borrows the
  main rate's mode and nothing points across at it.
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

