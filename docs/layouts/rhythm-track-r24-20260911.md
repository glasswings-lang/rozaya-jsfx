# Rhythm Track — sixteen Drift and Ramp targets, and Drift movement, 2026-09-11

One slider inserted (`Drift movement` at 36); the two target lists grow from 2 to
16 and reorder. **Status: BUILT, MEASURED, INSTALLED 2026-09-11. Not heard. Not
yet driven in real REAPER (`bridge_ui_test.py`).** Authored before any code. Snapshot
`_pre-rhythm-r24-20260911/`; previous build in
`jsfx-backups/effects-folder-baks/pre-rhythm-r24-20260911/`.

## What Rozaya decided (quoted), and what is mine

- Rhythm Track next: *"I say we do rhythm"*.
- Beats per bar is a target: *"Beats per bar belongs on there too."* This
  overrules R24's "structural counts are not targets" for this control.
- Each click built fresh as it plays, and the switch: *"Yes, and yes, it should get
  the switch. that makes sense re: the bar"* -- said of: a drifted bar length is
  rounded to whole beats, waits for the next downbeat, and on `With the target`
  steps once per bar.
- Start delay stays off the list: *"I'd understand not putting start delay on
  there"* (it may revisit).
- Carrying over copies never migrated: *"Yes, sync all the broken things"*.
- **Mine, unquoted:** the names; no "both" entries for the per-beat pitch
  targets (Heartbeat's shape); every target defaults to `On a clock`, which is
  what the two old targets always did; the click-sound targets and Play/Rest step
  once per beat, heard or silent (the grid marches through rest, as Heartbeat's
  cycle does); Tone resonance clamps to its control's 0.5-8, volumes and Pan spread
  to 0-1, decays to at least 0.001 s, Tuning reference to 20-2000; a slider edit to
  Beats per bar ALSO waits for the downbeat, since the latch cannot tell a hand
  from a drift; a Host x seek places the grid with the bar length drift has now.

## The list — 2 become 16, in control order

0 Tempo, **1 Beats per bar**, 2 Swing amount, **3 Strong pitch, 4 Weak pitch,
5 Strong fine tune, 6 Weak fine tune, 7 Tuning reference, 8 Tone resonance,
9 Strong volume, 10 Weak volume, 11 Strong decay, 12 Weak decay, 13 Pan spread,
14 Play for, 15 Rest for.** Old -> new: `0->0, 1->2`.

Units: a pitch in that beat's Pitch mode, a fine tune in its Fine tune unit, the
reference in Hz, decay in seconds, Beats per bar / Play for / Rest for in beats.

## When each value is read

- Tempo and Swing: every sample, as now.
- Targets 3-13: when a click fires. The click is rendered then, from the drifted
  values, and only if they differ from the last render of that click, so a copy
  with no drift renders exactly what `@slider` used to. `@slider` no longer renders.
- Beats per bar: latched on each downbeat, `max(1, floor(value + 0.5))`.
- Play for / Rest for: every sample; the gate still switches on only when both
  sliders are above zero.

## Sliders — 39 become 40

1-35 unchanged. **36 Drift movement `{With the target, On a clock}`, default On a
clock.** Old 36 Drift shape -> 37, 37 Drift play for -> 38, 38 Drift rest for ->
39, 39 Host ratio (retired) -> 40. Slider 23 and 31 values remapped `1 -> 2`.

## Save format and memory

Magic `2400002 -> 2500016`. 2400002, 2300002, 2200002, 2100002 are read at width
two, each field only where that format held it, then remapped through `0->0, 1->2`
with both remembered selectors. Order unchanged, `target_drift_moves[16]` appended
last. Sixteen fits the existing 16-slot stride from 131520; new banks above the
pitch banks (which end at 131941): `target_drift_moves` 131952, `drift_step_mem`
131968, `rt_scratch` 131984. No `rand()` added.

## Instances

- Bridge copy: 39-control line, a 2400002 blob, Ramp and Drift both on target 1
  (Swing) at 600. Line migrated; the plugin remaps the blob.
- **Tensor's two, first release (13 values, no blob), never carried over:**
  `tensor-two-track-drift-fixed` (plays) and `tensor-two-track` (typed values,
  volumes 0, silent in every build). By name to the 40-control line, plus a 2500016
  blob holding each line's two frequencies as pitches in Hz. Compared against
  e09eec7, the last build with the first release's positions 1-13.

Tools: `tools/rhythm_r24_migrate_20260911.py`, `tools/rhythm_r24_verify_20260911.py`.
