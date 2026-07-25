# Polyrhythm Phase v3 — binaural channel-swap slider

Design note, 2026-07-25. **Not built this session — deferred by choice** (context
budget). Pick up when ready; the design decision is settled, the slider-budget
question is the one open item.

## The feature

Add one control to **polyrhythm_phase v3**, placed **under the existing binaural
controls**: a **channel swap** — swap which output channel (L/R) carries the
binaural frequency offset.

Cheap, functional, no redesign of the beat itself. It gives the user a choice of
*which ear* the offset lands on, rather than changing what the offset does.

## Why this, and not a "balanced" redesign

This came out of a listening + analysis session on the brainwave-entrainment
catalogue. The finding (measured, not guessed):

- polyrhythm_phase builds its binaural beats **one-sided**. The **left** channel
  is a pure octave grid (base 82.4 Hz -> 82.4, 164.8, 329.6, 659.2, exact 1:2:4:8
  octaves that fuse into one clean tone). The **right** channel is that grid with
  the beat frequency **added to each octave** (e.g. +40 for the 40 Hz file ->
  122.4, 204.8, 369.6, 699.2).
- Adding a constant to an octave stack **breaks the octaves** (octaves multiply,
  the offset adds), so the offset ear goes **inharmonic** — four tones that don't
  fuse, heard as roughness/buzz. The reference ear stays pure. The result is an
  audible **left/right asymmetry**: clean on one side, rough on the other. The
  user's ear caught it on `4oct-40hz-binaural-beats.flac`.
- **Severity scales with the beat.** At 1-8 Hz (delta/theta) the offset is tiny
  and the right ear is *almost* harmonic — inaudible. At ~20-40 Hz (high
  beta/gamma) it's stark. All 40 binaural files in the set share the exact same
  one-sided construction (verified: L always 82.4 Hz, R always 82.4 + the
  filename's beat, every beat dead-on). The 36 isochronic files are L=R identical
  and correct — this does not touch them.

Alternatives were auditioned this session (short pure-tone examples were rendered
to a scratch folder — `40hz_A_one-sided`, `40hz_B_symmetric`,
`40hz_C_single-carrier`):

- **Symmetric split** (left -beat/2, right +beat/2): both ears equally, mildly
  inharmonic; the asymmetry vanishes but *both* ears lose a little purity. Same
  beat, same entrainment.
- **Single carrier per ear** (drop the octave stack): both ears perfectly pure,
  zero roughness — but thin; loses the lush octave-stacked body.

**The decision:** binaural beats are treated as *medicine* — functional over
pretty. The one-sided design is fine to keep; the roughness is not a defect so
much as a property. So rather than rebuild the beat (symmetric / single-carrier),
just add a **channel swap** so the user controls which ear carries it. Right-sized
for the use, and v3 holds it perfectly.

## Slider spec

- **Control:** a 2-option slider — `Binaural channel [Normal | Swapped]` (or
  `Offset on Right | Offset on Left`, whichever reads clearer in the binaural
  section). Default = Normal (current behaviour, offset on right — matches every
  file already rendered, so nothing shifts unless the user opts in).
- **Placement:** immediately under the existing binaural controls, so it reads as
  part of that group when tabbing the parameter list (NVDA).
- **Effect:** swap the L and R output channels of the binaural-beat generation
  (equivalently, apply the offset to the left grid instead of the right). A plain
  output-channel swap is the simplest correct implementation; confirm it only
  swaps the *binaural* pair and doesn't disturb any non-binaural output the plugin
  also produces.

## The one open question: slider budget

`docs/planned-features.md` records polyrhythm_phase at **slider64 — the project's
soft ceiling (0 remaining)**. A new swap slider is **slider65**. JSFX supports up
to slider256, so it's allowed, but it breaks the "stay <= 64" habit. Options for
the future session:

1. **Accept slider65.** Simplest. The ceiling is a habit, not a hard limit.
2. **Fold the swap into an existing binaural control** if one has spare enum room
   (e.g. an existing 2-option binaural toggle could become a 4-option that encodes
   on/off x normal/swapped) — keeps the count at 64 but is less discoverable.

Recommendation: option 1 unless a clean fold presents itself. One slider past a
soft habit is not worth an awkward combined control on an accessibility-first
plugin.

## Locating the code

Source: the polyrhythm_phase v3 JSFX under `src/` (see `docs/plugins/
polyrhythm-phase-v3.md` for the control map). Find the binaural-beat generation
block — where the beat frequency is added to one channel's carrier(s) — and the
existing binaural slider group. The swap is a small change right there.

## Also worth doing when this lands

- The manual (`docs/plugins/polyrhythm-phase-v3.md`) moves in lockstep — document
  the new control.
- No re-render of the existing 40-file catalogue is needed: default = Normal
  reproduces exactly what's already there. The swap is purely additive choice for
  future renders.
