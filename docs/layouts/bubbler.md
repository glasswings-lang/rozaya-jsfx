# Bubbler — authored transpose layout (R22 for a SHIFT)

**Status: BUILT 2026-09-09. NOT HEARD.**

**Written alongside the build, not before it, and that is a departure from the
standing rule.** The design arrived from Rozaya mid-session and was built as it
was described. The rule exists so a migration is not written twice; this one was
written once, so nothing was lost — but the order was wrong and is recorded here
rather than tidied away.

## Why Bubbler is not Dapple

Dapple's `Pitch (Hz)` is a real frequency, so Breath Generator's block drops on
unchanged. Bubbler's `Transpose (semitones)` is a SHIFT applied to incoming
audio. It has no frequency of its own.

**A first attempt made the note name an interval measured from the tuning
reference. Rozaya stopped it:** *"you're doing the thing prior claudes started to
with pitch."* She was right — that is the shape she already rejected once, where
the note stops being a note and becomes an offset, which is what turned the pitch
value into a second fine tune. It was reverted whole.

## Rozaya's design — you tell it where zero is

> *"I feel like I should be able to enter, like, a center note to tell the plugin
> this is where this audio is ... it can't auto detect, so you gotta tell it.
> just leave it alone if there's no center note there ... if you're thinking in
> music theory anyway, you already have a center note in your head, and then you
> have to go out of that brain and calculate, okay, how many semitones down is
> this? When you know what fucking key it's in, you know what you wanna hear."*

And the hard constraint, stated in the same breath:

> *"I think you can get rid of the note names, but I don't think you should get
> rid of the semitones because at that point, you leave people dead in the water,
> and that's a feature I use fairly frequently."*

**So the semitone value is the control of record and nothing may gate it.**

## What replaces what

`Transpose (semitones)` (slider 4) becomes seven controls in the same position.
Everything from old slider 5 up moves up by six: **31 sliders → 37**.

| # | control | note |
|---|---|---|
| 4 | `Source note (where zero is)` `{None, C-1 … G9}` | **Defaults to None**, which is what every saved project gets and what makes this migration silent. At None the rest behaves exactly like the old slider. |
| 5 | `Target note` | Comes alive only once Source note is set — hidden otherwise, because it would have nothing to measure from. Pick what you want to hear; the shift is worked out. |
| 6 | `Transpose value (Hz / semitones / cents)` | **THE shift**, always. Was slider 4. Range widened per R12 carve-out 1. |
| 7 | `Transpose unit` `{Hz, Semitones, Cents}` | Defaults to Semitones, which is what the old slider was. |
| 8 | `Fine tune` | The only fine tune. |
| 9 | `Fine tune unit` `{Hz, Semitones, Cents}` | Cents. |
| 10 | `Tuning reference (Hz)` | 440. **This is what lets a shift be spoken in Hz at all** — `ref → ref + v` is one specific interval; without an anchor "shift by 30 Hz" means nothing. |

Everything resolves to semitones, because that is what the grain ratio wants:
`ratio = 2^(semitones/12)`.

## Measured

A fresh instance is bit-identical to the old plugin. Picking Source note `C4` and
Target note `G4` produces a stream bit-identical to typing `7` semitones, so the
note path and the number path agree exactly.

## Migration — 10 instances, 3 finished projects

`birdsong-2` (3), `birdsong` (2), `the-sound-of-a-drain` (5). The stored semitone
number moves into `Transpose value`, unit written as Semitones, Source note None.
Idempotence gates on slider 7, which is `Bubble length (ms)` (min 5) before and
`Transpose unit` (max 2) after.

## Blob

Untouched. These are ordinary sliders; there is no per-target bank and no magic.
