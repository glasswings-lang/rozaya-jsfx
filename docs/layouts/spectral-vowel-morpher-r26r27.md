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

- **Wash grain leaves the Drift and Ramp target lists.** It stays a plain control. Measured
  below: a fast grain drift makes the wash wobble in loudness whatever the timing. Read
  2026-09-16, first Morpher per project: no project drifts or ramps it (27 on 300, six on
  150, two 400, two 600, one 200). Rozaya: *"if drift is going to fuck shit up, why bother
  having it *on there*?"* Removing it renumbers both pickers, so the migration moves every
  saved selection past it. With it gone, Drift movement has no grain to act on; check Play
  for / Rest for as targets before settling that the Morpher needs no switch.

- **Spread gets a unit and the pitch block.** Told that in Hz the blur is one fixed width
  everywhere (it swallows the gaps between low harmonics and barely touches high ones) and
  that in Semitones it would blur evenly across the range; Rozaya: *"For that reason alone we
  should have a spread unit, and it should encorperate the usual pitch block."* Saved
  projects land on Hz with their numbers, so nothing changes sound. Semitones/Cents mean a
  blur reaching that interval either side of each frequency (a per-bin width -- new code in
  gen_grain's running-total blur). Asked: does a note name belong on a width.

## Still to talk through

- Drift period unit and Ramp time unit per target.
- Layer harmonics and Source fine tune as drift/ramp targets.
- Every mode in front of its value (Transpose, Fine tune, Source fine tune, Layer pitch,
  Layer fine tune, both amount units, Auto-morph time and Rate mode).
- Low cut and High cut as pitch blocks.
- **Drift movement on Wash grain, measured 2026-09-16, not yet decided.** Each grain is
  written whole (`gen_grain`), but the hop moves mid-hop. Probe: test copies summing the
  synthesis window alone into a third accumulator (overlap evenness, independent of the
  audio), `breathing.RPP`, Texture 100. Drift off: 1.9% typical wobble. Gentle sine drift
  (+-50 ms, 10 s): 2.2% now, 2.0% latched -- nothing. Fast random drift (+-250 ms, 0.5 s):
  16.2% now vs 12.1% latched; 10 ms stretches over 30% off, 262 now vs 89 latched, worst
  bump +90% either way. Latching helps, but the wobble under a fast grain drift remains
  in both: grains of different lengths overlapping is uneven whatever the timing.
  jsfx_run note: the Morpher ignores drift edits until @block adopts the mirror -- set the
  selector with `--set-after`, then `--stage`, then the values, or the drift never runs.
