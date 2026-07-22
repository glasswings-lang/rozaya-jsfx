# Dyscalculia-accessibility sweep — design reference

Planning + design reference for making the rozaya-jsfx suite usable by a
**dyscalculic** brain (Rozaya is dyscalculic as well as blind). Companion to the
blind-accessibility work, not a replacement for it — both axes apply at once.

Status: **planned.** Cadence will mirror the Speed Ramp / drift sweeps — audit
every plugin, fix per-plugin, ear-test. This doc is the compass.

---

## The core principle

> **The barrier is ARITHMETIC and CONVERSION — not numbers.** Reading a value,
> setting a value, nudging it up or down by feel are all *fine*. The wall is
> being made to **run an operation** to get from what you want to what the
> control needs. Never hand the user a calculation as a toll gate; the machine
> does any math.

Sharpened 2026-07-09 (Rozaya corrected an earlier overstatement — "never *show* a
number" is condescending; reading and setting values is fine). The canonical
trigger: **`0.0625 ÷ 2` — everything fell apart.** That hits all three weak spots
at once — a decimal with no felt magnitude, the hardest operation (division), and
a working-memory hold — whereas **`480 − 440 = 40` is painless** (round, anchored
numbers; a difference that can be *felt*). It's not the digits, it's the
operation-on-un-anchored-values. Kill the forced operation, keep the honest,
precise control. (Do **not** "fix" this by hiding numbers behind opaque
mood-labels — that's dumbing-down, a separate mistake already made and rejected;
good access keeps full continuous/precise control, the machine just holds the
digits.)

What's *easy* for this brain (use these):
- **Regular, evenly-spaced increment patterns** you continue by feel — counting,
  not computing (the Polyrhythm `0.05, 0.10, 0.15…` voice-drift ladder is the
  template: painless once the pattern is set).
- **Powers of two / note-values** — `1/16, 1/8, 1/4, 1/2` — because they're
  *halving* (a visual/physical bisection) and *felt rhythm* (tap/clap), routed
  through the intact rhythm channel, not arithmetic.
- **Relative nudges** ("longer/shorter") and **tapping** (perform it, machine
  measures it).

What's *hard* (avoid forcing these):
- **Unit conversion** (seconds ↔ steps ↔ beats).
- **Division**, especially by non-round numbers (the `46.5 ÷ 0.375 = 124` trap).
- **Ratios / proportions / decimal fractions** off the power-of-two grid.
- **Absolute targets you must calculate** rather than a pattern you continue.

Backed by dyscalculia research: calculation, division, ratios, multi-step
working-memory tasks are impaired; **rhythm/beat perception is a separate, spared
faculty**, and time perception is normal *until a numeral is introduced*. Pattern
continuation and visual/relational reasoning are documented compensations.

**Blind wrinkle (load-bearing):** Rozaya navigates by the parameter list (OSARA),
not the `@gfx` canvas. So the usual sighted-dyscalculia fix — *show a live
readout of the computed result* — **does not work inside a plugin** (NVDA can't
read `@gfx`). In-plugin, the fix must be **input-side**: the control speaks a
felt unit, or selects from a list, or syncs to REAPER's accessible tempo.

**Carve-out (sharpened 2026-07-21).** "Never display the answer" is true *of the
plugin* and false *outside* it. The blocker is `@gfx`, not display as such — and
a terminal is fully accessible. A companion tool in `tools/` can print both the
answer **and the derivation chain**, and that lands fine: Rozaya can't *hold* a
multi-step chain in working memory, but one can absolutely **audit a result one can
read**. So a displayed chain is not the failed sighted fix; it's a different,
working one. Design rule: the tool does the holding, then shows its work so the
result can be checked rather than trusted. Never a black box that emits a bare
number.

---

## THE NUMBER CHANGE (headline fix) — slider increments are on the wrong grid

**Right now the per-voice timing sliders step on a DECIMAL grid, which can't land
on the values a dyscalculic-musical brain actually holds.**

Confirmed in `melody_phase.jsfx`:

```
slider23:1<0.01,16,0.01> V1 Next voice in (cycles)
slider24:1<0,16,0.01>     V1 Note duration (cycles; 0 = silent)
```

That trailing `0.01` is the increment. Stepping goes `0.01, 0.02 … 0.12, 0.13`.
**`0.125` (an eighth note) is NOT on that grid** — it lives *between* 0.12 and
0.13. So you cannot arrow-step to a note-value; you're forced to *type a decimal*,
which drags you straight back into number-production. The decimal grid makes the
one channel the brain is strong in (note-values, powers of two) **unreachable by
feel.**

### Fix, two options (prefer option 2)

1. **Quick — re-grid the increment to a 16th note.** Set the step (and min) to
   `0.0625`. Then stepping walks `1/16 → 1/8 → 3/16 → 1/4 → …` — every arrow press
   lands on a real note-value. A felt ladder in music's native grid. Cheap, but
   the slider still *reads* as a decimal.

2. **Better — note-value picker.** Replace the raw "cycles (decimal)" slider with
   a selector you step through:
   `{1/16, 1/8, 3/16, 1/4, 1/3, 1/2, 3/4, 1, 1.5, 2, 3, 4}` (cycles), mapped to
   the cycle-fraction internally. No decimals, no typing, no grid math — you
   *pick the rhythm*, the machine stores the number. This is the
   Polyrhythm-clean-ladder idea expressed in note-values, and it's the most
   dyscalculia-native control we can build.

**"The steps across plugins are a mess."** Increments are currently inconsistent
plugin-to-plugin and almost all decimal-based. Part of the sweep is an
**increment audit**: catalog every slider's `<min,max,step>`, and standardize
rhythmic/duration controls onto note-value grids or pickers, and other controls
onto clean, walkable increments. (`melody_phase` timing = `0.01` confirmed; others
TODO — assume they vary until checked.)

---

## Other recurring dyscalculia hells to hunt

- **Welded units.** `Play/Rest` is denominated in **steps = one voice's "Next
  voice in" period** — so the step length is a *hidden product* of two sliders.
  Shortening notes (e.g. to `0.125` cycle for fast flutter) silently shrinks the
  step to `0.375 s`, so a ~46 s rest needs **124** steps, found only by dividing
  by an ugly decimal. **Fix:** denominate Rest in a *stable felt unit* (bars /
  beats / note-values) that does NOT move when note length changes; the plugin
  converts to steps internally. (Note: switching rate mode to BPM does **not**
  fix this — the step coupling is mode-independent. BPM fixes *ratios*, not
  *welded units*.)
- **Hidden ratios.** Layer alignment in Seconds mode hides relationships
  (`3.0 / 1.5` vs the obvious `20 / 40` BPM = 2:1). **Fix:** favor BPM mode for
  rhythmic/ratio work, or express inter-voice timing relative to V1.
- **Rate unit traps.** Hz is the worst (requires inversion, `1/x`). **Fix:**
  tap-to-set / project-tempo-sync (read the `tempo` system var — *read only*, the
  reserved-variable trap), so REAPER's accessible Tap Tempo action drives it.
- **Inverse / derived values** anywhere the user must compute one slider from
  others (e.g. Attack% + Release% summing). Let the plugin clamp/handle it.

---

## Cross-instance — the fixes that CANNOT live in a plugin

Every pattern in the toolkit above is **input-side inside one instance**:
note-value pickers, felt units, nudge-by-ear, relative-to-V1. That's coherent and
it works — but it has a hard edge, and the edge is where the sweep was silently
incomplete.

**Instance 2 has no idea instance 1 exists.** There is no control you can add to
a JSFX that knows what another copy of itself is set to. So any relationship
*between* instances is structurally unreachable from input-side design. Not
un-built: unreachable.

**Worked case (2026-07-21).** Two Polyrhythm-style instances, base 30 BPM, voices
laddering `+0.05` each. Goal: voice 8 of instance 2 should land `0.05` BPM *below*
voice 1 of instance 1. Answer is `29.60`, and getting there means cancelling the
`+0.35` upward stack **and** applying the `−0.05` shift — two subtractions pulling
opposite ways, held simultaneously. Exactly the doc's own failure profile.

Note what this confirms: **within** an instance the `0.05, 0.10, 0.15…` ladder was
painless, precisely as this doc predicts (pattern continuation, spared faculty).
The model held. The wall was *only* at the instance boundary. So this isn't a
correction to the model — it's its missing edge case.

**Fix: `tools/rate_calc.py`.** Takes base, step, which voice you're placing, what
you're placing it against, and the offset you want. Prints the base rate to dial
in, the full derivation chain, the resulting voice table, and a verification line.
See `tools/README.md`.

**Rule of thumb for the sweep — which lane a fix belongs in:**

| The relationship is… | Fix lives… |
|---|---|
| within one instance (voice↔voice, slider↔slider) | **in-plugin, input-side** — picker, felt unit, nudge |
| between instances, or plugin↔project, or plugin↔plugin | **tool-side** — `tools/`, prints answer + chain |

If a fix would require a plugin to know something it cannot see, stop designing
controls and write the tool.

## What JSFX can actually build (control reality — verified 2026-07-09)

Every fix here has to live inside JSFX's real control set. Verified against the
[JSFX spec](https://www.reaper.fm/sdk/js/js.php):

- **No momentary push-button exists.** There is no "press and it springs back"
  control — so an operation like "÷2" / "halve" **cannot** be a button. Don't
  design around one.
- **`@gfx` can draw buttons, but NVDA can't read `@gfx`** — so custom-drawn
  controls are dead for Rozaya regardless. Out.
- **Accessible primitives = stepped sliders + enum/list sliders**
  (`slider1:0<0,N,1>{a,b,c}Name`). OSARA/NVDA read these as list parameters —
  the same family as every dropdown already in the suite.

So the halve/double *action* ships as a **stepped note-value list**, not a
button: `{1/16, 1/8, 1/4, 1/2, 1, 2, 4}`. Down a notch = half, up = double; the
machine stores the real decimal. Strictly better than a button — a button halves
once; the list is the whole ladder to walk by ear. **Every "operation as a
control" idea in this doc must reduce to a stepped/enum slider or a nudge**, because
those are the only accessible controls JSFX has.

### Enum labelling — unit in the NAME, bare values in the list (NVDA verbosity)

When an enum's value labels all repeat the same unit, NVDA re-reads that unit on
every arrow-step — chatty and slow to scan. Put the unit **once** in the parameter
name; make the value labels the bare distinguishing tokens.

```
BAD:   slider5:1<0,3,1>{-12 dB/oct,-24 dB/oct,-36 dB/oct,-48 dB/oct}Slope
GOOD:  slider5:1<0,3,1>{-12,-24,-36,-48}Slope (dB/oct)
```

NVDA then says "Slope dB/oct" once on landing, and just "−12 / −24 / −36 / −48" as
you scroll. (Established 2026-07-09 on `womb_voice.jsfx`.) Applies to **every**
enum in the suite — fold it into the increment audit.

## Fix-pattern toolkit

| Pattern | Use for |
|---|---|
| **Note-value picker** (list of `1/8, 1/4, …`) | any rhythmic/duration control |
| **Note-value increment** (`0.0625` step + min) | rhythmic sliders kept as numbers |
| **Felt unit, machine converts** (bars/beats) | rest, gaps, durations |
| **BPM default** over Seconds | anything where ratios matter |
| **Project-tempo sync** (read `tempo`) | borrow REAPER's accessible tap-tempo |
| **Nudge-by-ear** (clean small step) | "tune it till it sits right" controls |
| **Relative-to-V1** | inter-voice timing relationships |

---

## Snap vs nudge — keeping groove (swing, off-time, humanize)

Making controls dyscalculia-friendly does **not** mean quantizing everything to a
rigid grid and losing the groove. There are two *different* rhythm jobs, and they
want two *different* control types — both feel-based, neither requiring a number:

- **Grid position** — *where a note nominally sits* (1/8, 1/4, …). Discrete,
  snapped, felt → **note-value picker.**
- **Expressive deviation** — *swing, "land it slightly late," humanize.*
  Continuous, found by ear → **nudge-by-ear.** You push it until it grooves; the
  fine fraction lives under the hood and the user **never computes it.**

Swing is the *poster child* for nudge-by-ear, not for typing fractions: nobody
grooving thinks "set the offbeat to 0.667," they think *"more swing… there."*
That's the dyscalculia-friendly mode exactly — relative, felt, machine holds the
number. **The fineness serves the user; the user never produces it.**

So clean grid and expressive timing are *separate knobs* and don't fight:
- the **picker** says *where the note lives*;
- a **Swing / feel** control (continuous nudge; optionally with named presets as a
  felt ladder — *straight / light / triplet / hard*) says *how far off-grid it
  leans*;
- per-voice **"nudge late / early"** micro-offsets handle "land this voice a hair
  off" — relative, by ear, fine under the hood.

Result: **fully off-grid expression with zero off-grid arithmetic.** This is
exactly the jank the hand-typed fractions were *trying* to buy — swing, human
feel, slightly-off landings — delivered through a felt control instead of a
computed one. Fractions stay; they just become the machine's currency, not the
user's.

---

## Open decision — "units match target" vs normalized %

The suite's nested-selector Drift/Speed-Ramp lets one amount slider serve many
targets. When those targets have **different units** (resonance_bank: Hz + dB +
pan; melody_phase: 28 incl. gain dB, durations, %), the shipped convention is a
single slider labelled **"(units match target)"** — the number is read in the
selected target's native unit, so *the same value means a different thing per
selector*. On paper that's the hidden-context trap this doc warns about. In
practice it holds up because **drift is tuned by ear** (nudge the amount until the
wander feels right; the nominal unit barely matters) — and a blind user can't read
an absolute "= 400 Hz" readout anyway.

The alternative: make the amount **normalized (0-100%)** and let each plugin scale
it to the target's own range internally (`cutoff → amount% × 1000 Hz`, `resonance
→ amount% × 0.5`, …). Pro: one consistent meaning everywhere, and the machine does
the unit math (the core principle). Con: the amount becomes **relative, not
absolute** — you lose "Drift up 200 Hz" (a number that means what it says).

**Decision: deferred, suite-wide.** Not worth forking one plugin over — whatever we
pick, apply it to every nested-selector at once. For now new plugins **follow the
"units match target" convention** for consistency (womb_voice does). Revisit as
part of the sweep. (Raised 2026-07-09 while adding resonance targets to womb_voice.)

## Audit checklist (per plugin)

For every slider, flag it if it forces any of:
- [ ] **any operation** to reach the target (halve, double, convert, or split one
      value across channels) — the machine should do it
- [ ] a unit conversion (the goal-unit ≠ the slider-unit)
- [ ] a division, especially by a non-round number
- [ ] a ratio / proportion the user must compute
- [ ] an absolute target derived by calculation (vs a pattern continued)
- [ ] a decimal-grid increment that can't land on note-values
- [ ] a "welded" unit that silently changes when another slider moves
- [ ] a relationship to something **outside this instance** (another instance,
      another plugin, the project) — can't be fixed input-side at all; route it
      to a `tools/` script instead

Then apply the matching fix from the toolkit. Ear-test per plugin. Keep slider
**IDs** stable (add new sliders at the end — the usual rule); changing a slider's
*increment/label/unit* is safe for state as long as the ID and value-range hold.

---

## Pitch was never swept (2026-07-21)

The sweep had only ever covered **rhythm** — rate, drift, timing, duration.
Pitch controls were never audited, and three plugins were handing over raw
semitone counts: `polyrhythm_phase`, `melody_phase`, `bubbler`.

Worse, Polyrhythm was paying the *cost* of a whole-number grid with none of its
benefit. A whole-number grid is the price of putting **names** on the steps —
that is what makes Harmonic Sculptor's picker work at all. Polyrhythm locked
itself to whole semitones and never labelled them, so you could neither detune
by ear nor pick a note. Tax, no service.

**Landed:**

- `polyrhythm_phase` semitone sliders step in tenths, so voices can be detuned
  against each other by ear. One character, no other change; the pitch maths was
  already floating point and had always accepted fractions.
- `src/polyrhythm_notes.jsfx` — the same engine with each voice naming its note
  (`C2`–`C6`) and a separate fine-tune in **cents**. A separate plugin, because
  the layout needed six sliders per voice in a fixed order and renumbering in
  place would have broken every saved project.

**The lesson that cost the most:** the first attempt used *interval* names
("a fifth"), which is music-theory jargon and no more reachable than `7` for
someone who does not read music. Note names are the fix. Written up under
"Two ways to fail this that both look like fixes" in the companion doc.

**Still unswept:** `melody_phase` and `bubbler` both still take raw semitones.

## Morph timing: a percentage was the wrong unit (2026-07-21)

`spectral_vowel_morpher` had one global Auto-morph time for the whole journey
across the captured slots, so capturing another slot made every step *faster*
— the total stayed put and got divided more ways. With exactly two slots that
is indistinguishable from "time per step", which is why it only surprises you
on the third.

The first fix was a per-slot **dwell percentage**, and it was wrong for the
reason this whole document exists: a percentage of a shared total is a ratio.
Replaced with a per-slot **linger in seconds** in `spectral_vowel_morpher_v2`,
and the global removed entirely — a cycle is now its steps added together.
Asymmetry (a breath out longer than a breath in) falls out for free and cannot
be expressed by any single shared number.

Every setting that describes a capture is per-slot in v2 for the same reason:
one global flattening eight captures is a shared quantity nobody asked to share.

## Precedent already shipped

The **multiplier → signed-delta** change across the Speed Ramp sweep ("the
multiplier is a dyscalculia accessibility problem") is the proof-of-concept: same
move, different control. This sweep generalizes it.
