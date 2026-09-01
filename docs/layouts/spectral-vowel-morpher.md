# Spectral Vowel Morpher — authored layout

Written by hand 2026-08-31, not generated. Reading order **approved by Rozaya**.
**Status: BUILT and MIGRATED 2026-09-01** (commit `340fd4e`). 122 instances across
38 projects migrated with 0 problems; the capture inventory is byte-identical before
and after -- 848 slots, every peak, RMS and detected pitch unchanged. **Not yet
ear-tested.** `Layer overtone harmonic` shipped voice-side only; the wash follows the
global, because per-layer there would cost an extra spectral pass per layer per grain.

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
