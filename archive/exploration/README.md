# Exploration archive

Files here are research / diagnostic / iterative work from the
breath-vowel-synthesis exploration that ultimately landed as
[Resonance Bank](../../src/resonance_bank.jsfx) in the main suite.
They do not ship as user-facing plugins. They are preserved here
because the diagnostic insights they captured remain useful if
this territory is ever revisited.

## What's here

### Waveguide tract experiments

- `tract_tube_v5.jsfx` — a Pink-Trombone-style Kelly-Lochbaum
  digital waveguide tract synthesizer (generator form). The
  starting point handed off from a prior session that needed
  diagnostic work.
- `tract_diag_v1.jsfx` — uniform-tube diagnostic build that
  proved the scatter and boundary equations work. The tube
  provably rings at expected closed-open-tube formant
  frequencies (F1 ~500, F2 ~1500, F3 ~2500 Hz).
- `tract_diag_effect_v1.jsfx` ... `_v6.jsfx` — effect-form
  iterations that took audio input (e.g., Breath Generator) and
  shaped it through the waveguide. Successive versions added
  Pink Trombone's three-zone rest tract shape, corrected tongue
  position mapping, ported the cosine tongue formula, and
  constrained the tongue span away from the pharyngeal walls.
  The "vowels emerging but not landing cleanly" pattern at v5
  / v6 was the wall that motivated the pivot away from
  waveguide synthesis.

### Formant-filter vowel shaper experiments

- `vowel_shaper_v1.jsfx` ... `_v8.jsfx` — Klatt-style parallel
  formant synthesis applied to breath input. v1 used linear
  Height/Backness/Rounding-to-formant-frequency mappings; v2
  switched to triangle interpolation through `/i/`, `/a/`, `/u/`
  corners; v3 added a four-corner quadrilateral with `/æ/` and
  `/ɑ/` as separate corners; v4 rebalanced formant strengths for
  noise input (real voice has natural source tilt, whispered does
  not); v5 added Voice Size; v6 made lip rounding GATE the entire
  formant character (per Rozaya's observation that open-mouth
  breath has no vowel and rounded-lip breath does); v7 added
  input-derived constriction noise (extracting 5 kHz band of the
  input rather than synthesizing noise inside the plugin); v8
  restructured so the breath is always the base signal that lip
  rounding shapes, rather than three parallel paths that get
  perceived as "layered."

### Handoff / design notes

- `HANDOFF_vocal_synth.md` — the original handoff document from
  the prior session that started this exploration.

## Why this didn't ship

Both architectures reached real progress points and revealed
real acoustic insights, but neither produced sufficiently natural
breath-driven vowel sounds via pure parametric synthesis. The
journey converged on a clearer architectural realization: what
was actually wanted was a configurable resonance bank with
multi-band parallel filtering and per-band drift modulation. That
plugin (Resonance Bank) does not specifically synthesize vowels
but does provide the general-purpose tool for shaped breath,
windscapes, evolving noise textures, and many other use cases —
including formant emphasis when the user wants it.

The exploration files are kept because the diagnostic builds
demonstrate that the underlying DSP (waveguide ringing, formant
filtering, constriction noise via input bandpass) is sound. If
naturalness becomes a priority again, the next attempt would
likely be sample-based (record real breath samples and manipulate
playback) rather than further parametric refinement.
