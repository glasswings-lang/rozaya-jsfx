# Morpher v2 — slot timing redesign

Design note, written 2026-07-24. **Built and ear-tested ✓ 2026-07-25**, now in
`src/spectral_vowel_passage.jsfx`. The design below is what shipped, with two
decisions resolved at build time noted inline: **the dip was rejected** (gap is
inert when crossfade is on — see that section) and the plugin was **renamed to
Spectral Vowel Passage** (see Related open items).

This replaces how a slot's time is described. It does not touch capture,
analysis, the voice engine, or the wash engine.

## The problem

Today a slot has **Slot linger** (how long it holds) and **Slot crossfade** (how
long it takes to hand over). Both belong to the slot, and both are edited
through the Capture-slot selector, same as everything else.

The trouble is that the fade *into* a slot isn't owned by that slot — it's
owned by the slot before it. So a single thing you want, "a four-second gap,"
is controlled by settings living on two different slots, and only one of them
is on screen at a time.

That is why silence has been so hard to place. It isn't an arithmetic problem
in the sense of sums being hard; it's that half of the thing being tuned is
somewhere you can't see while you tune the other half. The workaround has been
to over-set linger to allow for fades bleeding in from the neighbour, which
means reverse-engineering a number instead of typing the one you want.

Worth noting what is *not* wrong: the code does what the Slot linger label
promises. Linger is pure hold time and the crossfade is added on top. The
memory-layout comment near the top of the source still says `hold = linger -
xfade`, left over from before the semantics were flipped, and should be deleted
when this work happens — it will mislead the next person to read it.

## The model

Every slot owns its whole leg. Selecting a slot shows everything about it:

- **how long it takes to fade in**
- **how long it stays up**
- **how long it takes to fade out**
- **whether it crossfades into the next slot** (a toggle)
- **how long of nothing before the next slot begins**

Nothing about a slot lives on a different slot. That is the entire point of the
change.

Each number is the thing you hear. Four seconds of quiet means typing four. No
allowance, no subtraction, no working backwards from a total.

## The four combinations

The toggle exists because a gap of zero is otherwise ambiguous — does the next
slot start when this one *begins* fading out, or when it *finishes*? Those are
two different sounds and both are wanted. A number can't express which; a switch
can.

The alternative would be letting the gap go negative to mean overlap. Rejected:
that is exactly the kind of control that makes you do sums in your head.

- **Crossfade on, no gap** — classic morph. The next rises as this one falls.
- **Crossfade off, no gap** — clean handover. One stops, the next starts, no
  overlap.
- **Crossfade off, gap set** — hard silence. That many seconds of nothing,
  with edges.
- **Crossfade on, gap set** — see below.

## The dip (REJECTED at build time)

**Resolved 2026-07-25: not built.** With crossfade on, the gap does nothing —
`leg_len = fade_in + hold + fade_out`, the gap is not read. This is the plain
reading below, chosen over the dip. The consequence for labelling is that the
gap control is a no-op whenever crossfade is on; that condition should live in
the wording a user hears, per the Labelling section. The dip stays here as a
future option if the inert combination ever wants to earn its keep.

The obvious reading of "crossfade on, gap set" is that it's contradictory, and
the gap should simply do nothing there.

The alternative is to make it a **dip** rather than a floor. With crossfade off,
the quiet has hard edges — one stops, nothing, the next starts. With crossfade
on, the two slots' fades stretch *across* the quiet instead of stopping at it:
the outgoing slot is still trailing away as the silence opens, and the incoming
one is already breathing in before it closes. The same amount of nothing in the
middle, arrived at and left through a swell rather than an edge.

One is a cut. The other is a breath.

The practical benefit is that every combination then does something, so no
control is ever inert and nobody has to remember why a slider isn't responding.

This is the part of the design most worth throwing out if it doesn't match what
you actually want to hear.

## Labelling

Names carry their own conditions. If any control only applies in certain states,
that belongs in the name, not in a manual and not in a control that disappears.

Hiding a slider from the plugin window does not reliably remove it from the
host's parameter list, so a control can vanish from one view and persist in
another. For anyone driving this by parameter list rather than by mouse, that is
worse than a clearly-named control that is sometimes a no-op.

## Silence slots stop existing

Today a gap is made by capturing silence into a slot and setting its linger.
Under this model the quiet lives *between* slots, where it actually is. No slot
is spent holding nothing, and Slot mute goes back to meaning only "skip this
one" rather than doubling as gap machinery.

## What this replaces

- **Slot linger** stops being a compound value and becomes simply "how long it
  stays up."
- **Slot crossfade** becomes the fade-out, and gains a matching fade-in.
- Two genuinely new controls: the crossfade toggle and the gap.

Net two more controls per slot, all on the existing nested selector. No new
breadth on screen — the nesting suits this plugin because a slot is a *thing
with properties*, unlike Polyrhythm's voices, which are peers you compare
across. Do not flatten one into the other's shape.

## Implementation notes

Status as built (2026-07-25):

- **Done** — the leg envelope (`leg_env` / `out_env`) rides on the voice output
  in `@sample`, so the fades are amplitude, applied on top of the spectral
  crossfade (`xfade`) rather than sharing its single position. Crossfade-on uses
  `xfade` for the handover with `leg_env` open; crossfade-off keeps `xfade` at 0
  and shapes the whole amplitude with `leg_env`.
- **Done** — controls regrouped: fade-in / hold / fade-out / gap / crossfade
  toggle / mute are sliders 4–9; Drift and Ramp shifted to 22–32. Free because
  v2 is unshipped.
- **Done** — `@serialize` migrates older v2 blobs by appending the three new
  per-slot fields after `slot_mute` and defaulting them on a short read
  (fade-in = old fade-out, gap = 0, crossfade = on) so an old project sounds
  unchanged.
- **Done** — the stale `hold = linger - xfade` comment is gone; the memory-layout
  comment now says `slot_linger` holds "Slot hold" and `slot_xfade` holds "Slot
  fade out" (internal names kept to avoid churning the banks).
- **Done** — `tools/morpher_to_passage.py` (renamed from `morpher_v1_to_v2.py`)
  updated for the new labels (it maps by label, so the relabel would otherwise
  crash it): Morpher's per-pass time becomes each slot's fade-out, hold = 0,
  crossfade on, gap 0 — reproducing the continuous morph.
- **Done** — manual moved in lockstep (`docs/plugins/spectral-vowel-passage.md`).
- **Done (ear-tested ✓ 2026-07-25)** — passed by ear.
- **Done** — **named**: the plugin is now **Spectral Vowel Passage** (see below),
  renamed across source, manual, index, READMEs and the migration tool.
- **Pending** — commit.

## Related open items

- **Naming — RESOLVED 2026-07-25: Spectral Vowel Passage.** It is a sibling, not a
  version: Morpher is a field you sit inside, Passage is a route with stops. An
  earlier session (a since-retired handoff note, 2026-07-22) had picked *Loom*; this
  supersedes it. *Passage* — "a way through" and "a section of music" both apply —
  keeps the shared "Spectral Vowel" prefix so the pair sits adjacent in the plugin
  list. The former file `spectral_vowel_morpher_v2.jsfx` is now
  `spectral_vowel_passage.jsfx`.
- **v1 per-slot backport.** v1 banks only Capture point per slot; the mechanism
  for banking the sound-character values already exists in v2 and could be
  ported. Slot timing stays v2's alone — that is what makes them different
  instruments.
- **Capture averages one frame — FIXED 2026-07-27.** Confirmed cause of the
  wobble when re-spectralising already-processed material: a single analysis
  frame freezes that frame's per-bin scatter and repeats it every grain. Raising
  Spread (with grain around 300) smoothed it away in practice but never removed
  it — a blur over the frozen scatter, not a fix, and it cost definition and a
  Spread setting that should have been free for character.

  The proper fix named here is what shipped: `compute_spectrum` now averages
  MAGNITUDES (not complex bins — summing complex would let frames cancel by
  phase, which is a comb filter) across *Capture average* frames stepped by
  `WA/2` and centred on the capture point. **Per slot**, on slider 4 beside the
  other capture-analysis controls, default 1 = the original single-frame
  analysis, so nothing that already exists changes until the dial is turned.
  The trade is time-smear: a vowel that moves gets blended across the span,
  which is why it is a dial rather than a default.

  **No re-capture or re-render needed.** The blob stores `slotraw` — the raw
  captured audio — and the analysis is re-derived from it on load, so every
  capture in every existing project can be re-read at a higher frame count.

  Voice (harmonic) analysis deliberately left single-frame: it resynthesises
  exact harmonics at the detected f0 with continuous phase and has no per-bin
  scatter to freeze, so it has nothing to gain and would multiply the cost of
  its DFT — the expensive half of a capture — by the frame count. Stereo is
  untouched: width comes entirely from the per-bin phase offsets applied at
  synthesis, and the magnitudes the averaging changes are SHARED by both
  channels, which is why the wobble sat in the centre of the image rather than
  in the width.
