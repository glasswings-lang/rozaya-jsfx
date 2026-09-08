# Spectral Vowel Morpher — authored layout

Written by hand 2026-08-31, not generated. Reading order **approved by Rozaya**.
**Status: BUILT, MIGRATED and EAR-TESTED 2026-09-01.** 122 instances across 38
projects migrated with 0 problems; the capture inventory is byte-identical before and
after -- 848 slots, every peak, RMS and detected pitch unchanged. Rozaya then opened
an **existing, already-migrated project**: it loaded correctly and the reorder was
right, which is the migration proving itself on real data rather than on a diff.
Overtone confirmed working.

**Still unheard, and worth naming rather than letting the pass cover them:**
`Sync to host`; the per-layer overtone specifically at the WASH end; the Pitch +
Overtone correction below (which changes the sound of any project using both); and
the other 37 projects, which will be confirmed by ordinary use over weeks, as agreed. `Layer overtone harmonic` shipped voice-side only; the wash followed the global
until later the same day, when the wash half landed too -- see the last section.

**This is the most-used plugin in the suite — 38 projects, more than double anything
else — and the riskiest migration in it**, because its `@serialize` blob carries actual
captured spectral analysis rather than just settings. `tools/passage_captures.py` can
list and extract those captures: **inventory them before touching a single project, and
verify every one afterwards.** Checking, not hoping.

## What changes, and why

1. **Drift and Ramp sit in the MIDDLE** (17-27), splitting the sound controls in half.
   They move to the end, where every other plugin keeps them.
2. **`Capture average` is at 28** while the rest of the Capture group is at 1-3.
3. **`High cut` is at 32, twenty-one sliders from `Low cut`** at 11. They are a pair.
4. **`Input`/`Output level` sit at 4-5**, among the capture controls, rather than at the
   end of the sound section where a global output belongs.
5. **`Capture slot` displays 1-8** instead of 0-7 (approved decision 10). The only value
   change in this layout; everything else is pure movement.
6. **New: `Layer overtone harmonic`** — see below.

## The order

| new | control | from |
|---|---|---|
| 1 | Capture slot (1-8) | 1, now 1-based |
| 2 | Capture spectrum | 2 |
| 3 | Capture point (% back from the press) | 3 |
| 4 | Capture average (frames) | **28** |
| 5 | Audition | 13 |
| 6 | Morph (% across captured slots) | 14 |
| 7 | Auto-morph | 15 |
| 8 | Auto-morph time (sec) | 16 |
| 9 | Texture (% wash) | 6 |
| 10 | Wash grain (ms) | 7 |
| 11 | Spread (Hz) | 8 |
| 12 | Pitch (semitones) | 9 |
| 13 | Stereo width (%) | 10 |
| 14 | Denoise (%) | 12 — name provisional, not yet traced |
| 15 | Low cut (Hz) | 11 |
| 16 | High cut (Hz) | **32** |
| 17 | Overtone harmonic | 29 |
| 18 | Overtone lift (dB) | 30 |
| 19 | Overtone width (harmonics) | 31 |
| 20 | Layer | 33 |
| 21 | Layer active | 34 |
| 22 | Layer level (dB) | 35 |
| 23 | Layer solo | 36 |
| 24 | Layer pitch (semitones) | 37 |
| 25 | Layer harmonics | 38 |
| 26 | **Layer overtone harmonic** | **NEW** |
| 27 | Input level (dry, dB) | 4 |
| 28 | Output level (dB) | 5 |
| 29-34 | Drift: target, up, down, period, shape, restart | 17-22 |
| 35-39 | Ramp: target, by, duration, engage, start delay | 23-27, engage and start delay swapped into canonical order |

39 sliders, from 38.

---

## THE FILE HAS MOVED PAST THIS DOCUMENT — amended 2026-09-04

**The order above is what SHIPPED on 2026-09-01 and it is no longer the file.**
The Morpher has 49 sliders, not 39. Everything from 29 onward has moved, and
three separate migrations ran on 2026-09-04 to get there — which is precisely
the failure `CLAUDE.md`'s one-migration rule now exists to prevent, and this
document going stale is part of how it happened.

What landed after this layout was authored:

| new | control | when |
|---|---|---|
| 8 | **Rate Mode** `{BPM, Seconds, Hz, Host x}` | was `Sync to host`, an on/off switch; became the suite's four |
| 9 | Auto-morph time (BPM / sec / Hz / beats per cycle) | relabelled with it |
| 30 | **Start delay** (sec, or beats in Host x) | NEW, transport block |
| 31 | **Play for** (sec, or beats in Host x) | NEW |
| 32 | **Rest for** (sec, or beats in Host x) | NEW |
| 33 | **Rest mode** (Walk through / Freeze in place) | NEW |
| 34 | **Output at rest** (Pass-through / Silence) | NEW |
| 35-42 | Drift, now with play/rest | +2 |
| 43-49 | Ramp, now with play/rest | +2 |

**Do not build from the table above.** It is kept because it records the
reasoning for the 2026-09-01 reorder, which is still sound and still describes
why sliders 1-28 sit where they do. For anything from 29 up, read the source.

**What this plugin is still owed**, and what a re-authored layout has to cover
before it is touched again:

- **`Ramp duration` and `Ramp start delay` are minutes-only** and sit outside
  Rate Mode, because a beat count will not fit their `0..60` range — a
  20-minute ramp at 120 BPM is 2400 beats. Needs a range decision, not a quiet
  clamp.
- **`Drift restart`** (Restart on play / Free-running) has no equivalent
  anywhere else in the suite; either it propagates or it is explained.
- **R12 ranges and R17 units** for the `0..1` and percent controls.
- **The Capture-slot 1-based display decision** (approved, item 10) is not
  reflected here.

## The new control: `Layer overtone harmonic`

**What it does today:** the overtone is folded into the shared magnitude array —
`hmA_arr[vn] = slot_harm[...] * ot_gain[vn]` — and **every layer reads that same array**.
So one setting applies to all layers at once, by harmonic *index*, not by frequency. With
`Overtone harmonic 8` the lift lands at 8·f0 in the Original, 4·f0 an octave down, 2·f0
two octaves down, 16·f0 an octave up. Consonant, because the layers are octaves and
fifths — but not controllable, and there is no way to say *"overtone on the lead, none on
the drone,"* which is what a throat-singing patch actually wants.

**Decided: the HARMONIC goes per layer; `lift` and `width` stay global.** The harmonic is
the melodic choice — it is already a Drift and Ramp target, which is how the overtone
melody gets played — while lift and width are character, and character can reasonably be
uniform across a stack.

**Implementation:** build a per-layer magnitude array once per frame
(`lay_hmA[lyk*NHARM+vn] = base * lay_ot_gain[...]`) rather than multiplying per sample.
About 2000 multiplies per frame, nothing added to the per-sample path, so no CPU change
where it matters.

---

## READ THIS BEFORE IMPLEMENTING THE PER-LAYER VALUE

**Nested selectors are the single trickiest pattern in this suite**, and every plugin that
has one has been broken by it at least once. A selector plus shared value sliders backed
by a per-target memory bank can drop or overwrite the user's values in at least six
distinct ways. Rozaya, 2026-08-31: *"you have to make sure values don't get dropped and/or
overwritten by selection changes, and we've solved that already with, of all things, the
layer implementation itself."*

**The reference implementation is in this very file** — the `last_lay_sel != lay_sel`
block in `@slider`. Copy its shape. Do not invent a new one.

The traps, each tied to the incident that proved it:

1. **Save the OLD target before loading the new one.** On a selector change, write the
   visible sliders into `bank[last_sel]` *first*, then load `bank[new_sel]`. Skip this and
   every edit is lost the moment you look at another layer.
2. **Capture live edits into the current target** when the selector has NOT changed — the
   `else` branch. Without it, an edit only persists if you happen to switch away.
3. **Adopt change-trackers in `@block`, not `@slider`.** On a fresh or duplicated instance
   `@slider` runs while REAPER is still handing over saved values, so a tracker adopted
   there captures a DEFAULT, and the real value arriving later reads as a user edit.
   (Proved 2026-08-23: it stamped 0.5 over a hand-set rate on every load and duplicate.)
4. **...but do not let that make the control dead.** `@block` only runs when audio is
   being processed, so a block gated on "tracker initialised" does nothing while the
   transport is stopped — which is how this suite gets configured. Adopt in both;
   whichever runs first wins. (Found by ear, 2026-08-31.)
5. **Guard the bank's `@init` defaults behind a `*_cfg_inited` flag.** Most of this suite
   has no `ext_noinit`, so `@init` re-runs on every transport play and will re-default the
   bank mid-session. (Found by ear, 2026-08-31: set 5 beats, press play, get 16 back.)
6. **Restore the visible sliders from the bank in `@serialize`'s read branch**, and
   serialise which target was selected. `@slider` and `@serialize` restore by independent
   paths in no guaranteed order, so an `@slider` pass running against a still-empty bank
   can drag the visible slider to a default, and `slider_automate` makes it stick.

Two more that are not selector-specific but bite in the same place:

7. **Writing to a slider needs announcing** — `sliderchange(-1)`, or `slider_automate`
   only where automation is genuinely wanted. REAPER keeps its own copy and hands it back
   otherwise. **A memory bank has no second copy, which is exactly why banks beat hidden
   sliders for storage**: it removes the failure mode rather than guarding against it.
8. **Anything DERIVED from the bank belongs in `@block`**, never `@slider`, or a restore
   leaves the derived value stale while the bank itself is perfect.

## Migration

- **Positions:** the authored permutation above, applied to the `.RPP` slider line by
  token position. Generalise `tools/passage_migrate_sliders.py` from inserts to
  permutations rather than writing a new tool.
- **Values:** `Capture slot` gains 1 (0-7 becomes 1-8). Nothing else changes value.
- **New slider — decide before building.** `Layer overtone harmonic` seeding to 0 (off)
  on every layer does NOT reproduce today's sound, because today the global overtone
  applies to all layers. Either seed each layer to the global value (identical sound, and
  the global control becomes the Original's own), or accept a documented change. The first
  is almost certainly right.
- **The blob is untouched by a renumber.** Verify anyway, with `passage_captures.py`.


## Tempo sync — added 2026-09-01, Rozaya's request

Rozaya, 2026-09-01: *"[it] absolutely could do with ... a rate mode ... right now it just
uses seconds ... I know hertz isn't in time, for instance, but beats is and seconds are."*

Correct on both counts, including the doubt. **Hz and BPM do not apply to either of these
plugins**, because neither has a *rate* — both have **durations**. A duration's two honest
units are seconds and beats, and that is the whole choice.

### The control

Per **R13**, sync is not a unit, so it is not an entry in a unit picker:

```
Sync to host      {Off, On}
```

One switch, and **no `Rate mode` enum** — a unit picker with one entry (Seconds) would be
a control that cannot be set. This is R13 applied exactly, and it comes out smaller here
than in Womb because there is only ever one unit to leave.

**No `Host sync target` selector either, and this is the part worth reading.** R11 pairs
the selector with `Every N beats` for plugins whose rates are expressed *as rates* — Womb's
heart is a BPM, so it needs somewhere to say how many beats one beat-of-the-heart takes.
**`Auto-morph time` is** a duration durations already. Under sync they are simply **read as beats**, exactly as
Womb's four breath sliders are, and their sum is the cycle by the same rule. There is
nothing left for a selector to select.

Womb's built shape confirms this rather than contradicting it: its `Host sync target` has
**one** option, `{Heart rate}` — the only thing in the plugin expressed as a rate.

### What changes unit, and what deliberately does not

| control | when Sync to host is On |
|---|---|
| Auto-morph time | reads as **beats per morph** |
| Drift period | unchanged — already in its own musical unit |
| Ramp duration, Ramp start delay | unchanged — a wall-clock wind-down, suite-wide |

Ramp is the wind-down you set in minutes because you are going to sleep. Tying it to the
project tempo would be answering a question nobody asked.

### Naming, and the rule it obeys

Every affected slider says so in its own name — `Auto-morph time (sec / beats when synced)` — per the standing
rule that a control may never change what it means without saying so on the control
itself. The switch is named in the label so the two read as a pair.

The labels get longer, which the layout above otherwise works to avoid. That is the cost
of the rule and it is worth paying: a silent unit change is the failure this suite has
already been bitten by.

### Entering and leaving are both silent

On the switch, the affected values **convert** at the current tempo, so the sound does not
change at the moment you flip it — the same behaviour Womb's Host x has. Only the unit
you are typing in changes.

### Migration

**None.** `Sync to host` is a new slider defaulting to Off, and every existing project
keeps reading in seconds. It is the append case, and it costs nothing.

## The wash half of `Layer overtone harmonic` is OWED, not declined

Written 2026-09-01, correcting myself the same day I shipped it.

I built the per-layer overtone on the voice only, and justified leaving the wash out
by saying per-layer there would cost an extra spectral pass per layer per grain on a
plugin "already at its CPU ceiling around four layers." Rozaya challenged both halves
and was right about both.

**The `~4 layers` figure is a CALCULATION, not a measurement**, and it is about the
VOICE: CLAUDE.md derives it as *five sources x 64 partials x 4 banks = ~1280
oscillators/sample*. Oscillators are the voice engine. Nobody has ever measured a
layer ceiling on the wash. This is the third time in this repo a mechanism has been
quoted back as a finding, and this one is mine.

**And the wash does not build per-layer FFTs at all.** `build_spectrum` sums every
layer into ONE spectrum -- two inverse FFTs per grain, whatever the layer count. The
function's own comment says so: *"This is why layers are nearly free here -- one extra
interpolated read per bin, inside a grain that was already going to be built, rather
than a second pair of FFTs per layer."* I wrote a cost claim that the function I was
editing contradicts in a comment three lines above the code I changed.

**It also happens to be the half that matters.** Rozaya, 2026-09-01: *"wash is where I
live anyway."* And at the wash end the voice engine is skipped entirely -- it is gated
on `hlevel > 0.0001` -- so the per-layer overtone as shipped does nothing at all where
this plugin actually gets used.

### What building it actually costs

The global overtone is currently baked into `curmag` in `gen_grain`, before
`build_spectrum` reads it. Per layer it has to move INTO the per-bin layer loop that
already runs:

- stop baking the overtone into `curmag`; keep `curmag` clean
- in `build_spectrum`, multiply each layer's contribution by that layer's own overtone
  window, and the base term by the global one
- per-layer power normalisation, as the voice already does
- `ot_wash`'s sub-fundamental rule (bins under f0 take the normalisation but not the
  lift) applies per layer too, against that layer's own shifted fundamental

Cost is a window evaluation per bin per ACTIVE layer, alongside the interpolated read
already happening there -- same order as what the loop does today, and no new
transforms. Worth precomputing each active layer's window across output bins once per
grain rather than re-evaluating it per bin.

**BUILT 2026-09-01, same day.** Applied inline in `build_spectrum`'s bin loop rather
than through a helper -- that loop runs FFTSIZE/2+1 times, times every audible layer,
twice per grain, and is the hottest in the file. Away from the window the factor is
just the layer's power normalisation, so a range test skips the window arithmetic for
nearly every bin: one compare and one multiply. Not ear-tested.

### And it turned up a real bug, by reading

The wash overtone's centre was computed as `f0 x harmonic x pitch_ratio` -- an OUTPUT
bin -- and then used to index `curmag`, which is in SOURCE bins. At Pitch 0 the two
coincide, which is why it has never been noticed. At any other Pitch the wash lifted
harmonic `n x pitch_ratio` instead of harmonic `n`: at +12 semitones, the 2nd harmonic
when you asked for the 1st. Moving the window into source bins -- which the per-layer
work required anyway, since every layer reads that one spectrum at its own scale --
corrects it. **Found by reading, NOT confirmed by ear**, and it changes the sound of
any project using Overtone and Pitch together. Documented on the plugin page.

---

# Second layout change, 2026-09-06 — the two unit controls

Authored before anything was touched, per the standing rule. This is the LAST thing
the drift/ramp sweep owes the Morpher; every other control it was owed is already in
the file. One migration, not the first of several.

## What changes

The Morpher is the only plugin left carrying Drift and Ramp without the two controls
that say what unit their times are counted in. It gains both, in the canonical
positions the rest of the suite uses:

- **`Drift period unit`** `{Cycles, Seconds, Beats}` — directly after `Drift period`.
- **`Ramp time unit`** `{Cycles, Seconds, Minutes, Beats}` — directly after `Ramp by`
  and *before* `Ramp duration`, which is where every finished plugin puts it.

Nothing else moves. Eleven controls shift up to make room.

## Defaults, and why they are not the suite's usual ones

**`Drift period unit` declares SECONDS (index 1), not Cycles.** Two independent
reasons, and they agree:

1. **Every existing instance means seconds.** Measured, not assumed: all **122**
   instances across 38 projects are on Rate Mode = Seconds, and the drift period has
   read as seconds in every one of them since the control existed. A declared default
   is a live value for every instance that never touched the control, so putting
   Cycles at index 0 would silently reinterpret all 122.
2. **A Morpher can have no cycle at all.** Everywhere else in the suite the cycle is
   unconditional — a breath, a heartbeat, a bubble. Here the cycle is one Auto-morph
   traversal, and `Auto-morph` defaults to Off, which also hides `Auto-morph time`
   entirely. Defaulting to a unit that counts something a fresh instance does not have
   would mean drift silently never advancing the first time it is switched on.

This is the same principled-exception shape Veil already has, and the option list
stays identical to the rest of the suite so nothing learned elsewhere goes wrong here.

**`Ramp time unit` declares MINUTES (index 2)**, which is both the suite default and
exactly what `Ramp duration (minutes)` already meant. No instance changes meaning.

## What the unit controls replace

Drift period currently reads as seconds, or as beats when Rate Mode is one of the two
host modes — an implicit unit change with no control of its own, and the number was
rewritten on the mode flip to keep the length of time the same. That coupling goes:
**Drift period now reads whatever its own unit control says, and Rate Mode no longer
touches it.** Safe to remove outright, because no instance in the library has ever
been in a host mode — all 122 are on Seconds, so the conversion has never once fired.

The transport durations (`Start delay`, `Play for`, `Rest for`) keep the old implicit
behaviour. They have not been given explicit units anywhere in the suite yet, and
changing them is not this job.

## The permutation

Old 1–38 keep their places. `Drift period unit` is new at 39; `Ramp time unit` is new
at 46.

| old | new | control |
|---|---|---|
| 1–38 | 1–38 | unchanged |
| — | **39** | **Drift period unit** (new) |
| 39 | 40 | Drift shape |
| 40 | 41 | Drift play for |
| 41 | 42 | Drift rest for |
| 42 | 43 | Drift restart |
| 43 | 44 | Ramp target |
| 44 | 45 | Ramp by |
| — | **46** | **Ramp time unit** (new) |
| 45 | 47 | Ramp duration |
| 46 | 48 | Ramp play for |
| 47 | 49 | Ramp rest for |
| 48 | 50 | Ramp engage |
| 49 | 51 | Ramp start delay |

49 sliders become 51.

## The blob

`@serialize` gains no new bank — both new controls are plain global sliders, not
per-target values. The magic is bumped anyway (`7700010` → `7700011`), because a
slider layout changed and the blob's leading float is the only independent witness of
which layout an instance was saved on. That is what made the Melody Phase insert
repairable without guessing.

## The bug found next door

`auto_time` — the Auto-morph period in seconds — handles Rate Mode 0, 1 and 2
explicitly and lets **both** host modes fall through to the `Every N beats` formula.
Mode 4 is `N per beat`, its reciprocal, so it ran inverted: at 120 BPM, "8 per beat"
gave one morph every 8 beats instead of 8 per beat — 64x too slow.

This is the identical defect fixed in Tremolo and the Sweeping Filter (`c4c9b31`) and
in Resonance Bank (`47da263`); the Morpher was missed by that sweep. It is latent —
no instance is in either host mode — but it is **load-bearing for this job**, because
`Cycles` in both new unit controls means one Auto-morph cycle and would have inherited
the wrong number. Fixed in its own commit, landing first, so it stays separately
hearable.

Shepard Tone also has no `mode == 4` branch and is **correct** — its chain returns a
nominal rate against 60 BPM, where one beat is one second, so `N per beat` and `Hz`
genuinely coincide and the fallback is right. Checked by reading, not by counting.

## The layers get free pitch — authored 2026-09-08, NOT BUILT

**Status: SPEC AGREED, NOTHING BUILT.** Authored before anything is touched,
which is the rule this plugin has already paid for breaking.

### The brief, in Rozaya's words

> *"The layers were there to take away drift. My previous technique was to put
> three instances of Morpher up and scale them up by pitch. But the side effect
> of that, because they were all on shuffle so they wouldn't be boring, was that
> they would clash with each other. The layers were supposed to help with the
> pitch side of it, but I didn't mean for them to stay in lockstep. So we do need
> fine tune per layer, and we do need all the modes that pitch has — which then
> takes out the complexity of the octaves and the fifths and all that shit,
> because you'd be setting it yourself, which opens the door to all kinds of cool
> shit."*

**The layers solved the RIGHT half of the problem and over-solved the other
half.** Locking every layer to the same morph position is what stops three
Shuffled instances clashing, and that lock stays — it is the whole reason layers
exist. Locking every layer to a FIXED INTERVAL from the main pitch was never
asked for, and it is what makes the stack feel rigid.

### What changes

**Every layer gets its own pitch, freely set, with the full R22 treatment: a
pitch pair and a fine tune pair, each `{Hz, Semitones, Cents}`.** The pitch value
is signed — Rozaya: *"that's why you need the negative numbers as well"*.

**The named-interval ladder goes.** The selector stops being `4 octaves down …
a fifth up … Custom 3` and becomes `All, Layer 1 … Layer 16`. The thirteen fixed
intervals and the three Custom slots stop being different kinds of thing; there
are just sixteen layers, each sitting wherever it is put.

**The Original becomes Layer 1.** Rozaya: *"Original is already represented, or
will be, as the first layer, shifting falls out there."* It stops being a
special case — it is the layer whose pitch happens to default to 0, and it can
now be shifted like any other, which it could not before.

**The global `Pitch` stays, and stays global.** Rozaya: *"keep it global, that's
what it's for."* Every layer's pitch is an offset from it, so the whole stack
still transposes in one move; what changed is that the offsets are yours to set
rather than a ladder's to dictate.

### The layer block, exact

Ten sliders where there are seven. **Being honest about that: the SLIDER count
grows.** What shrinks is the sixteen-entry ladder of interval names to read
past, and the two-tier "is this a fixed layer or a Custom one" split — which is
what the complaint was actually about.

| # | control | note |
|---|---|---|
| 1 | `Layer` | `{All, Layer 1 … Layer 16}` |
| 2 | `Layer active` | unchanged; stays directly under the selector because "is this in play" is the first question about a layer |
| 3 | `Layer pitch value` | signed, −20000..20000 per R12 carve-out 1 |
| 4 | `Layer pitch mode` | `{Hz, Semitones, Cents}` |
| 5 | `Layer fine tune value` | signed |
| 6 | `Layer fine tune mode` | `{Hz, Semitones, Cents}` |
| 7 | `Layer level (dB, -60 = off)` | unchanged |
| 8 | `Layer solo` | unchanged |
| 9 | `Layer harmonics (0 = full)` | unchanged, a CPU control |
| 10 | `Layer overtone harmonic` | unchanged |

**Pitch moves ahead of Level, which is a change from today's order.** R19's
canonical reading order is what the thing IS, then its shape, then output level.
A layer's pitch is now its identity; its level is its output. `Active` keeps its
place at the top for the reason already written into the source.

**`All` at position 0**, same as Polyrhythm's `Voice`. Setting every layer's
pitch at once collapses the stack to unison, which is a real thing to want
occasionally and a real thing to do by accident — so the write must be
CHANGE-DETECTED, exactly as Polyrhythm v3's voice block is. Only a control
actually moved gets written. That build is the reference implementation.

### Defaults: a fresh instance must sound as it does today

`@init` seeds the sixteen layer pitches to the ladder they replace, in the new
order: Layer 1 = 0 (the Original), then −48, −36, −24, −12, −7, −5, +5, +7, +12,
+24, +36, +48, then the three Custom slots at their current defaults (−12, +12,
−24). So a new instance is the same instrument; the ladder becomes a starting
position rather than a cage.

### The migration, and how much of it already exists

**Most of it is built.** This plugin already self-migrates its blob across layer
reorderings: a version magic (`7700001`..`7700011`), a `permute_bank()` helper,
and permutation tables. Bumping to **7700012** and adding one permutation is the
same move it has made four times.

**What the blob owes:** the per-layer banks (`lay_db_base`, `lay_active`,
`lay_solo`, `lay_nharm`, `lay_ot_harm`) permute into the new order, and
`lay_semi` grows from 3 entries to 16 and is seeded from the ladder table for
the thirteen that never had one. The drift and ramp target banks permute too, at
offset `LAY_T0` — the existing code already does exactly this.

**What the SLIDER LINE owes:** a script, because the line does not self-migrate.
`tools/morpher_migrate_layer_order.py` is the worked example and does this job
already. **122 instances across 38 projects**, and this plugin's blob carries
real captured spectral analysis — so `tools/passage_captures.py` inventories the
captures before, and every one is verified after. Checking, not hoping.

**The target list's LABELS change** (`4 octaves down level` → `Layer 2 level`)
which is free, and their ORDER changes, which is not — but the permutation
already covers it.

### 7700007 put the Original first and it was reverted. That does not bind us.

The source records it: at `7700007` the Original moved to the FRONT of the Layer
selector, and at `7700008` it moved back to unison, mid-list. The reason is
written down —

> The list is a PITCH LADDER: four octaves down up to four octaves up, with the
> original sitting at unison where it belongs. Putting it at either END of the
> list was the same problem twice: an entry out of musical order.

**That was correct for a ladder and is irrelevant to a free list.** Once every
layer carries its own pitch there is no musical order for an entry to be out of,
so the objection dissolves with the thing it was protecting. Recorded here so a
future session finding `7700007` reverted does not read it as a warning.

### Per-layer pitch IS a Drift and Ramp target — decided 2026-09-08

Rozaya: *"Yes, something to drift and ramp for sure."* So the target list goes
from 24 to 40: eight global, then sixteen layer levels, then sixteen layer
pitches. A long enum to arrow, but typing works (R12), and this is the control
that turns a stack of fixed copies into something that shimmers.

Two follow-on details fall out of that, **and both are MY reading rather than
Rozaya's words — check them before building.**

**1. ~~The drift and ramp amount is in CENTS, always.~~ WRONG, AND WITHDRAWN
THE SAME DAY.** The drift/ramp AMOUNT gets its own unit control.

I had written that a pitch drift amount is always in cents whatever the layer's
pitch mode is, reasoning by analogy to the rate rule (*"Drift and Ramp amounts
are in BPM in EVERY mode"*). Rozaya:

> *"This right here argues for pitch either supporting the rest or being its own
> drift section. The minute that kind of collapse is happening it's a sign to
> stare at it harder. I'll hand you that it's an unusual exception to almost
> everything else in here, if not actually everything else in here. Still, the
> same principles apply. **No unit locks. ever.**"*

**The collapse was a workaround wearing a principle's clothes.** A JSFX enum
cannot change its options depending on what a selector points at, so "the unit
list should depend on the target" has no direct expression — and rather than
saying that, I picked one unit and dressed the constraint up as a rule. That is
the same shape as every other reduction caught this week: tidier in the
document, worse in the hand.

**The fix, and it costs one slider on each block:**

> `Drift amount unit` and `Ramp by unit`, both PER-TARGET (they join the
> existing nested selector alongside up/down/period), both
> `{Target default, Hz, Cents, Semitones, BPM, Seconds, dB, Percent}`.

**`Target default` is position 0 and is the live value for every saved
instance** — it means "whatever this target's natural unit already was", so
nothing moves on migration and the declared default is honest. Every other
position is an override reached for deliberately. That is not a lock: the plugin
still converts and the user still does no arithmetic, but the CHOICE of unit is
theirs.

The list carries units that make no sense for some targets — drifting a dB
target in cents. That is the honest cost of a static enum, and it is cheaper
than the alternative, which was telling somebody which unit they were allowed to
think in.

**NOT re-opened here: the rate's BPM rule.** CLAUDE.md records that as settled
BY EAR, twice, and Rozaya explicitly granted it as *"an unusual exception"*. So
a rate target's `Target default` goes on meaning BPM in every mode, exactly as
today. **But her principle plainly points at it**, and this note says so rather
than letting a future session find the tension and guess: under `Drift amount
unit` the BPM rule stops being a lock and becomes a DEFAULT, which is what it
should have been. Whether to say that out loud in R20 is its own conversation.

**2. The sixteen new targets are GROUPED BY LAYER, not appended in a block.**
So the list reads `Layer 1 level, Layer 1 pitch, Layer 2 level, Layer 2 pitch,
…` rather than all sixteen levels followed by all sixteen pitches. Working on
one layer means both its targets are adjacent, which is how the plugin is
actually used.

**This deliberately does not follow R18's enum-options-append rule, and the
reason it is allowed is specific to this plugin.** R18 forbids inserting enum
options because the option index is stored inside a slider's value and *"no
slider-line migration fixes that cheaply"*. Here both halves are covered: the
blob self-migrates through `permute_bank()` at offset `LAY_T0`, which already
handles an arbitrary permutation of the target banks, and the `Drift target` /
`Ramp target` slider values are remapped by the line migration that this change
needs anyway. **If either of those is not true when this is built, append
instead** — the grouping is a convenience and the correctness is not.
