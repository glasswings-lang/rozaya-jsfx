# Spectral Vowel Passage — authored layout

Written by hand 2026-08-31, not generated. **Status: order drafted, awaiting review.**
10 projects. Sibling to the Morpher; shared controls must read the same in both.

## The finding that shaped this layout

**Passage is a per-slot editor, and seventeen of its controls are per slot — but only
eight of them say so.**

Verified by reading the selector-change block (`last_cap_slot != cap_slot`), not by
trusting the labels. Per slot: Capture point, Capture average, the four slot timings,
crossfade, mute, Output level, **Texture, Spread, Pitch, Stereo width, Low cut, Denoise**,
Overtone harmonic, Overtone lift.

The last six carry no `(per slot)` in their names at all. That is a trap: set Pitch,
switch slots to check something, come back, and the pitch you set is gone — working
exactly as designed, and looking exactly like a bug.

So the plugin is not "some per-slot timings plus a global tone section". **Each slot is a
complete voice preset** — its own texture, pitch, width, filtering, overtone and level,
plus its place in the route. The layout should say that, and the names should too.

Rozaya spotted this from the reading order alone: *"it feels like the routing for the
slots should be... not there. Something feels off."*

## The order

**Per slot — pick a slot, then everything that slot is**

| new | control | from |
|---|---|---|
| 1 | Capture slot (1-8) | 1, now 1-based |
| 2 | Capture now | 2, renamed from `Capture spectrum` |
| 3 | Capture point (%, per slot) | 3 |
| 4 | Capture average (frames, per slot) | 4 |
| 5 | Slot fade in (sec, per slot) | 5 |
| 6 | Slot hold (sec, per slot) | 6 |
| 7 | Slot fade out (sec, per slot) | 7 |
| 8 | Slot gap after (sec, per slot) | 8 |
| 9 | Slot crossfade into next (per slot) | 9 |
| 10 | Slot mute (per slot) | 10 |
| 11 | Texture (% wash, per slot) | 15 |
| 12 | Spread (Hz, per slot) | 17 |
| 13 | Pitch (semitones, per slot) | 18 |
| 14 | Stereo width (%, per slot) | 19 |
| 15 | Low cut (Hz, per slot) | 20 |
| 16 | Denoise (%, per slot) | 21 |
| 17 | Overtone harmonic (per slot) | 36 |
| 18 | Overtone lift (dB, per slot) | 37 |
| 19 | Output level (dB, per slot) | 14 |

**All slots**

| 20 | Wash grain (ms) | 16 |
| 21 | Fade in shape (all slots) | 11 |
| 22 | Fade out shape (all slots) | 12 |
| 23 | Overtone width (harmonics, all slots) | 38 |
| 24 | Morph (% across captured slots) | 23 |
| 25 | Auto-morph | 24 |
| 26 | Audition | 22 |
| 27 | Input level (dry, dB) | 13 |

**Drift** 28-33 (target, up, down, period, shape, restart) — from 25-30
**Ramp** 34-38 (target, by, duration, engage, start delay) — from 31-35, engage and
start delay swapped into canonical order

38 sliders, unchanged in count.

## Naming

- **Every per-slot control says `(per slot)`.** Nine currently do not. This is the single
  most valuable naming change in the plugin.
- **`Capture spectrum` becomes `Capture now`.** It is a momentary trigger
  (`{Off, Capture now}`) that grabs audio into the selected slot and auto-releases — not
  a setting. The old name reads like a mode.
- The long explanatory labels shorten: `Slot fade in (sec) (per slot: how long this slot
  takes to rise)` becomes `Slot fade in (sec, per slot)`. NVDA reads the whole sentence on
  every arrow-step.
- Shared controls match the Morpher exactly: `Texture (% wash)`, `Stereo width (%)`,
  `Morph (% across captured slots)`, `Capture average (frames)`.

## Two things Wash grain is not

Recorded because I got both wrong out loud and Rozaya corrected them.

**It is not the other half of Texture.** Texture is the only voice-versus-wash control.
Wash grain sets `W`, the resynthesis window length, with `HOP = W/4` — so it is **how long
each grain of the wash is**, four overlapping at any moment. Short is fluttery and
textural; long is smooth and smeared. It is the wash's character, not its amount.

**Its being global is NOT an established constraint.** I asserted that per-slot grain
would cause clicks and that the global scope was therefore deliberate. That is a plausible
mechanism repeated as a finding, which is the exact failure mode CLAUDE.md records for the
`filt_stages` straight-wire theory. **Nobody has tested it.**

## OPEN: should Wash grain be per slot?

Rozaya, 2026-08-31: *"letting old grains go at their old length is just... the right thing
to do? My mental image is: grains of rice. You wouldn't chop them, so why do that to
audio."*

That is the standard granular model and it is correct: **a grain is an event, scheduled
with its parameters fixed at birth.** You do not reach into a grain that is already
sounding. A grain-size change applies to the grains scheduled after it.

Reasoning the actual risk through, rather than assuming it:

- Overlap-add does not require every grain to be the same length. Each is windowed before
  being summed, and the read pointer just walks the accumulator.
- What breaks transiently is **normalisation**. Four overlapping Hann windows sum to a
  constant; grains are scheduled every `W/4`, so if new grains are shorter they arrive more
  often, and for about one grain's duration the overlap count is between the two values.
- Predicted symptom is therefore an **amplitude wobble lasting roughly one grain**, not a
  click. Fixable by normalising against the running window sum, or by ramping the grain
  size across one grain length.

**To decide:** whether per-slot grain is musically wanted at all. If it is, the
implementation is "new grains take the new length, in-flight grains finish at the old one"
and the only work is the normalisation. If it is not wanted, keep it global — but document
it as a choice, not as a click hazard.

## Also open

- **Passage has no `High cut`; the Morpher does.** Same voice engine. On the Morpher it
  does double duty, shaping the top end and acting as a CPU dial, because partials above
  the cut stop being computed. Worth adding while the plugin is open.
- **`Denoise` name is provisional** — marked `(%)` without tracing what it scales, same
  as the Morpher's. Trace before committing to it.

## Migration

- **Positions:** the authored permutation above. Generalise
  `tools/passage_migrate_sliders.py` from inserts to permutations — it already knows every
  hop this plugin's layout has taken, and this becomes the next hop in that chain.
- **Values:** `Capture slot` gains 1 (0-7 becomes 1-8). Nothing else changes value.
- **The blob is untouched by a renumber.** Verify with `tools/passage_captures.py`, which
  can list and extract the captures inside it.
