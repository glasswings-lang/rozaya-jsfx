# Dapple — authored pitch layout (R22)

**Status: AUTHORED 2026-09-09. Build follows this file, not the other way round.**

Rozaya, 2026-09-09, on the four plugins R22 had deferred: *"a plug in that can't
make its own audio doesn't know its pitch. No. But it can pitch shift ... Morpher
and Passage are their own conversation, but Bubbler and Dapple are pretty much
good to go ... use breath gen as an example. They did it perfectly there."*

**Dapple is the clean case.** Its `Pitch (Hz)` is a real absolute frequency — the
resonant centre of the noise voice and the frequency of the tonal plink, at
`40..1500` — so Breath Generator's shipped block drops straight on. Bubbler is
NOT this case and is not in this file: its pitch control is `Transpose
(semitones)`, a SHIFT applied to incoming audio, with no absolute frequency to
name.

## What replaces what

`Pitch (Hz)` (slider 4) becomes six controls in the same position. Everything
from old slider 5 upward moves up by five: **33 sliders → 38**.

| # | control | note |
|---|---|---|
| 4 | `Pitch mode` `{Hz, Semitones, Cents}` | **Mode first**, exactly as Breath Gen ships it — it decides whether the number below means anything. Defaults to `Hz`, which is what every saved project holds. |
| 5 | `Note name` | A real control both ways: pick `C4` or type `60`, move either and the other follows. Hidden outside Semitones, where it would be lying. |
| 6 | `Pitch value (Hz / semitones / cents)` | **THE pitch.** Hz is the frequency; Semitones is the MIDI note number (60 = middle C); Cents is the same axis ×100. Was slider 4. |
| 7 | `Fine tune` | The only fine tune. There is exactly one. |
| 8 | `Fine tune unit` `{Hz, Semitones, Cents}` | Defaults to Cents, matching Breath Gen. |
| 9 | `Tuning reference (Hz)` | One per plugin. 440. |

**No `Pitch target` selector.** Dapple has one pitch, and a one-entry selector is
a control with nothing to choose.

## The range widens, and it may not narrow

`Pitch value` is `0..20000` step `0.001`, as Breath Gen ships it — not the old
`40..1500`. R12 carve-out 1: a range may be raised, never lowered, because
narrowing permanently clamps saved values. Nothing stored is above 1500, so the
widening costs nothing and buys the whole band.

## Drift and Ramp

`Pitch` stays at index 2 in both target lists — **the enum index must not move**,
because every per-target bank in every saved project points at it. Its units
follow the value's own unit, exactly as Breath Gen does it: drift in Hz while the
mode is Hz, in semitones while it is Semitones.

## Migration — 14 instances, 2 projects

`finished/bubbles.RPP` (11) and `to-play-with-later/womb-bubbles-proto.RPP` (3).

Per instance: shift stored sliders 5-33 up to 10-38, then write the block —
mode `0` (Hz), the old frequency into `Pitch value`, the nearest note at or below
it into `Note name`, fine tune `0`, fine tune unit `2` (Cents), reference `440`.
Mode Hz means the note name is hidden and inert, so seeding it is a convenience
rather than a semantic.

**Nothing stored changes meaning, and the render must prove it**: old plugin on
old project against new plugin on migrated project, bit-identical.

## Blob

Untouched. Dapple's single pitch lives in ordinary sliders, so there is no
per-target bank to serialize and no magic to bump.
