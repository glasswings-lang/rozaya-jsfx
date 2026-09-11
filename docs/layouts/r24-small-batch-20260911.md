# The small R24 batch — Bubbler, Dapple, Veil, Tremolo, 2026-09-11

Authored alongside the build, not before it, because no slider moves in any of
the four: only the Drift and Ramp target lists change. One migration per plugin.
**Status: BUILT, MIGRATED, MEASURED 2026-09-11. Not heard.**
Snapshot `_pre-r24-batch-20260911/`; previous builds in
`jsfx-backups/effects-folder-baks/pre-r24-batch-20260911/`.

## What Rozaya decided (quoted), and what is mine

- The batch and its order: *"I say we go for it"*, on the handoff's recommendation.
- Carrying over the copies that were never migrated: *"Yes, sync all the broken
  things"*.
- R24 (Star, quoted in the rules): every sound-shaping control is a target, Play
  for and Rest for are, and targets go in control order.
- **Mine, unquoted:** the target names; Fine tune and Tuning reference defaulting
  to `With the target` in Bubbler and Dapple, because both are read when a bubble
  is born, as Transpose and Pitch are; Cycle steps is not a target (a count).

## The lists

| plugin | targets, in control order | old -> new |
|---|---|---|
| Veil (5) | Left cutoff, Right cutoff, Left resonance, Right resonance, **Output** | unchanged; Output appends because it is last |
| Bubbler (13) | Bubble rate, Timing randomness, Transpose, **Fine tune**, **Tuning reference**, Pitch spread, Rise, Bubble length, Stereo width, Dry/wet, Output, **Play for**, **Rest for** | 0-2 stay, 3-8 +2 |
| Dapple (15) | Bubble rate, Timing randomness, Pitch, **Fine tune**, **Tuning reference**, Pitch spread, Resonance, Bubble length, Rise, Tone vs noise, Excite from input, Stereo width, Output, **Play for**, **Rest for** | 0-2 stay, 3-10 +2 |
| Tremolo (12) | Rate value, On duration, Tremolo amount, Attack, Release, **Stereo phase offset**, **Pan spread**, **Pan glide**, Pan sweep rate, **Pan sweep every**, **Play for**, **Rest for** | 0->0, 1->2, 2->8, 3->1, 4->3, 5->4 |

Amounts are in each target's own unit. Stereo phase offset wraps round the circle.
Play for and Rest for move how long each lasts; the gate still switches on only
when both sliders are above zero.

## Save formats

Veil `3200004 -> 3300005`, Bubbler `3500009/3400009 -> 3600013`, Dapple
`3600011/3500011 -> 3700015`, Tremolo `2200006/2100006 -> 2300012`. Each plugin
reads its old formats at their own width and remaps them itself, selectors
included, remapping only what the save held. `@init` draws `rand()` exactly as
before, in the old order; new slots are scattered from those values (the
Resonance Bank lesson of the same day).

## Instances, measured 2026-09-11

- **Current layout, no file change needed:** Bubbler 10, Dapple 14, Tremolo 11,
  Veil 1 (the bridge project). All rendered old against new, bit-identical.
- **knocking.RPP** (Tremolo, Drift target on Tremolo amount): selector 1 -> 2 and
  the blob rewritten as 2300012.
- **Never carried over, now migrated:** Tensor's six Tremolos and the
  `custom-polyrhythm` track template, on the first release's 18 controls
  (`d19873f`): rate mode and pan unit `{Hz, Seconds, BPM}` -> canonical, Release %
  and Attack shape swap, the Linked Sweep multiplier inverted. `scattered.rpp`'s two
  Dapples on the 32-control layout of 2026-09-06: Drift movement inserted, the
  pitch block, selectors remapped.
- **The bridge test project** holds one of each; it was open in REAPER, so it is
  migrated only after closing (`--bridge`). The plugins read it correctly anyway.

Tools: `tools/r24_batch_migrate_20260911.py`, `tools/r24_batch_verify_20260911.py`.
