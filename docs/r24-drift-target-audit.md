# R24 audit — Drift and Ramp targets, 2026-09-10

Every plugin in `src/` read in full against R24. Polyrhythm v1 excluded (frozen).
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
- **womb** — 11 of 16. Missing 31: S1/S2 pitch, fine tune, decay, volume;
  Brightness; HB stereo width; HB master volume; Inhale/Exhale fine tune; four
  fades; Breath high-pass, post-filter Hz, post-filter Q; Sigh extra length;
  Breath stereo width, volume; Bloodflow attack, decay, dicrotic level, filter Hz,
  resonance, stereo width, volume; Tuning reference. Several target names do not
  match their sliders (RSA depth, S1-S2 gap, Inhale/Exhale Freq, Breaths/min).
- **breath_gen** — 7 of 16. Missing 9: Inhale/Exhale fine tune, Tuning reference,
  four fades, Stereo width, Output.
- **heartbeat gen** — 4 of 16. Missing 12: S1/S2 volume, Brightness, S1/S2 decay,
  S1/S2 pitch, S1/S2 fine tune, Tuning reference, Stereo width, Breath cycle
  seconds.
- **rhythm-track** — 2 of 16. Missing 10: Strong/Weak pitch and fine tune, Tuning
  reference, Tone resonance, Strong/Weak volume, Strong/Weak decay, Pan spread.
  The tick is pre-rendered in `@slider`, so these need a re-render path.
- **veil** — 4 of 16. Missing: Output.
- **polyrhythm_phase_v3** — 24 of 32. Missing 9 global: Tuning reference, Pulse
  width, Tone, Edge, Movement, Body, Pan spread, Pan glide, Reverse drift offset.
  Missing 40 per voice: Fine tune, Depth, On duration, Attack, Release, each ×8;
  the last four currently share one target each.
- **shepard-tone** — 28 on room 16. Missing: Tuning reference, Pulse width.
- **shepard-scale** — 29 on room 16. Missing: Tuning reference, Pulse width, the
  twelve per-note fine tunes. Fine tune only reaches the oscillators on rebuild.
- **harmonic_sculptor** — ARCHIVED 2026-09-10, not owed anything.
- **spectral_vowel_morpher** — 24 of 32. Missing 26: Morph, Auto-morph time, Wash
  grain, Denoise, Overtone lift, Overtone width, Input level, three Custom layer
  pitches, sixteen layer overtone harmonics. Save format keyed to `N_TARGETS`.
- **spectral_vowel_passage** — 14 of 16 per slot. Missing: Wash grain, Overtone
  lift, Overtone width (17 total, one over).
- **sustain_looper** — DONE 2026-09-10: 8 targets, including the new pitch block.
- **bubbler** — 9 of 16. Missing: Fine tune, Tuning reference.
- **dapple** — 11 of 16. Missing: Fine tune, Tuning reference.
- **full-feature-sweeping-filter** — 6 of 16. Missing: On duration, Depth, Attack,
  Release, R channel phase offset, Pan spread, Pan glide, Pan sweep every.
- **sweep-dwell-filter** — 6 of 16. Missing: Low/High frequency, Low/High fine
  tune, Tuning reference, Wet/dry, Stereo phase offset, Pan spread, Pan glide,
  Filter speed multiplier.
- **stereo-phaser** — 6 of 16. Missing: none.
- **Full_Feature_Tremolo** — 6 of 16. Missing: Stereo phase offset, Pan spread,
  Pan glide, Pan sweep every.
- **resonance_bank** — 5 per band, banks exactly full. Missing: Input gain,
  Wet/dry, Output. These are global, and the layout has no global slot.

## Borderline, for Rozaya to decide

Start delay, Play for and Rest for (transport). Whole-step pitch controls:
Transpose, Octave shift, Center octave, note pickers. Phaser Stages (clicks when
changed). Morpher and Passage Capture point and Capture average (re-analysis).
