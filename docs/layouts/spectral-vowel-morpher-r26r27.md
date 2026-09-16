# The Morpher's R26/R27 layout -- being talked through, NOT built

Started 2026-09-16. Decisions land here as Rozaya makes them, quoted. The full slider
order is authored here before any migration (CLAUDE.md). 39 projects load the Morpher.

## Decided

- **Transport unit** `{Seconds, Hz, Beats}`, the same three as Passage, sitting above Start
  delay, Play for and Rest for, whose names drop "(sec, or beats in Host x)" for "(in
  transport units)". Each saved project lands on what it counts today (Beats where Rate mode
  is Every N beats or N per beat, else Seconds), so nothing changes sound. Rozaya: *"That
  idea sounds like a good one yeah"*.

- **The existing `Rest mode` becomes `Auto-morph rest mode`**, in place. It still freezes
  only the morph walk. Offered `Rest mode (for Auto-morph)`; Rozaya: *"auto-morf rest mode"*.
  Plus `Drift rest mode` and `Ramp rest mode` inside their blocks, both
  defaulting to Walk through (today's behaviour). Named after Rozaya's pattern, and renamed to match in Veil and the Stereo Phaser the same
  day. Rozaya: *"Yes"*.

## Still to talk through

- Drift period unit and Ramp time unit per target.
- Layer harmonics and Source fine tune as drift/ramp targets.
- Every mode in front of its value (Transpose, Fine tune, Source fine tune, Layer pitch,
  Layer fine tune, both amount units, Auto-morph time and Rate mode).
- Low cut and High cut as pitch blocks.
- Open questions: whether Drift movement is owed at all (each wash grain is written whole
  when it starts, `gen_grain`, so a drift cannot reshape a grain being heard; only HOP moves
  mid-hop), and whether `Spread` (a spectral blur in Hz) counts as a pitch spread under R27.
