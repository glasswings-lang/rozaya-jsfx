# R24 audit — Drift and Ramp targets, 2026-09-10

Every plugin in `src/` read in full against R24. Polyrhythm v1 excluded (archived 2026-09-10).
"Room" is how many targets the per-target banks hold before one overlaps the next.
Nothing here is a job to start unasked.

## Live memory and save bugs, present before any R24 work

Each confirmed by reading the offsets and code directly. **All fixed in `src/` on
2026-09-10** except Harmonic Sculptor and Sustain Looper. All installed except
Sweep Dwell, whose `src/` waits on migrating `surges.RPP`.

Not fixed, harmless as used today: in both Shepards `NUM_OSC` and `num_osc` are
one variable, because eel2 folds case.

- **shepard-tone:** `N_TARGETS = 28` on banks 16 apart (576–911). Drift, ramp and
  play/rest banks overlap: drift offsets overwrite ramp `by` every sample, and
  `@init` zeroes drift play-for on targets 0–11. Introduced in `3d23306`. Zero
  live projects.
- **shepard-scale:** the same, `N_TARGETS = 29`, banks 640–975. Introduced in
  `3d23306`. Zero live projects. A likely cause of the runner's "non-default
  Shepard runs are not reproducible" trap, not yet proven.
- **sweep-dwell-filter:** filter state `svf_l = 4400` sits on `sr_pr_accum_mem`
  (4400) and `sr_pr_resting_mem` (4416). Also in the installed copy.
- **resonance_bank:** `band_svf_L/R` (768–1279) and `band_bq_*` (1280–1407) sit on
  the drift play/rest and ramp banks (752–1807), and `@init` zeroes them on every
  transport play.
- **rhythm-track:** `@serialize` reads and writes drift and ramp play/rest only when
  the magic `== 2200000 + N_TARGETS`. Current saves are 2300000, so play/rest is
  never saved.
- **womb:** the Breaths/min aggregate sums the four segments without the breath
  unit conversion Breath Generator applies, so it is wrong in Beats.
- **sweep-dwell-filter (src, not installed):** slider55 `Tuning reference` is never
  read; `tuning_ref = 440` is hardcoded.
- **harmonic_sculptor, sustain_looper:** no `@serialize`, no Drift, no Ramp.

## Per plugin: room, and what is missing

Missing lists are from the audit reads, not individually re-checked.

- **melody_phase** — DONE 2026-09-10: 55 targets, including Play for and Rest for.
- **womb** — DONE 2026-09-11: 49 targets in control order, named for their
  controls, Sigh interval and the six Play/Rest included; Breath rate counts like
  Set breath rate; `scattered` carried over (`docs/layouts/womb-r24-20260911.md`).
- **breath_gen** — DONE 2026-09-11: 18 targets, Play/Rest included; Tensor's seven
  carried over from April (`docs/layouts/breath-gen-r24-20260911.md`).
- **heartbeat gen** — DONE 2026-09-11: 18 targets in control order, Play/Rest
  included (`docs/layouts/heartbeat-r24-20260911.md`).
- **rhythm-track** — DONE 2026-09-11: 16 targets, Beats per bar and Play/Rest
  included; clicks built as they fire; Drift movement added
  (`docs/layouts/rhythm-track-r24-20260911.md`).
- **veil** — DONE 2026-09-11: Output, 5 targets (`docs/layouts/r24-small-batch-20260911.md`).
- **polyrhythm_phase_v3** — DONE 2026-09-10: 88 targets, each per-voice control
  with an "(all voices)" entry that copies into eight. Phase Offset is not one.
- **shepard-tone** — DONE 2026-09-10: 40 targets.
- **shepard-scale** — DONE 2026-09-10: 45 targets.
- **harmonic_sculptor** — ARCHIVED 2026-09-10, not owed anything.
- **spectral_vowel_morpher** — DONE 2026-09-11: 55 targets in control order, with
  "all layers" entries; Layer harmonics, Capture point and Capture average left off
  on purpose, reasons on the controls (`docs/layouts/spectral-vowel-morpher-r24-20260911.md`).
- **spectral_vowel_passage** — 14 of 16 per slot. Missing: Wash grain, Overtone
  lift, Overtone width (17 total, one over).
- **sustain_looper** — DONE 2026-09-10: 8 targets, including the new pitch block.
- **bubbler** — DONE 2026-09-11: 13 targets in control order, Play/Rest included.
- **dapple** — DONE 2026-09-11: 15 targets in control order, Play/Rest included.
- **full-feature-sweeping-filter** — DONE 2026-09-10: 17 targets in control order.
- **sweep-dwell-filter** — DONE 2026-09-10: 16 targets, behind Rozaya's Segment
  selector (`docs/layouts/sweep-dwell.md`).
- **stereo-phaser** — 6 of 16. Missing: none.
- **Full_Feature_Tremolo** — DONE 2026-09-11: 12 targets in control order, Play/Rest
  included; Tensor's six and the track template carried over from April.
- **resonance_bank** — DONE 2026-09-11: 10 targets, the four whole-plugin ones
  held in band 0's row (`docs/layouts/resonance-bank-r22-r24.md`).

## Borderline, for Rozaya to decide

Start delay, Play for and Rest for (transport). Whole-step pitch controls:
Transpose, Octave shift, Center octave, note pickers. Phaser Stages (clicks when
changed). Morpher and Passage Capture point and Capture average (re-analysis).
