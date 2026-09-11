# Sweep Dwell — segments behind a selector

Authored 2026-09-10, before building. **Status: PROPOSED, not built.** One
migration for everything here, including the pitch blocks and Tuning reference
already in `src/` (which were never installed).

## What Rozaya decided (quoted), and what is mine

- On a cycle rate with durations as shares: *"Share of cycle is a very vague,
  confusing lable. I propose a selecter and then the modes, then the value. stick
  the frequencies in there too while we're at it. If we ever do decide to add
  other segments later, that's the extensable option and doesn't mean rewriting
  the entire plugin :)"*
- *"The sweeping filter because of what it is, should stay as it is. the
  sweep/dwell filter *wants* to be more"* — read by Claude as: the frequency sits
  on the two dwells, and the Sweeping Filter keeps its two full sets.
- On the five rate options for a length: *"I think it's doable re: the 5 controls"*.
- **Mine, not settled by Rozaya:** `All segments` at position 0; the meaning of
  each of the five modes as a LENGTH; Start delay gaining a mode; drift before
  ramp to match the Sweeping Filter; the target list; retiring the three cycle
  controls and the Pan speed picker (R20 retires both shapes); Tensor's handling.

## The segment block

A segment is one stretch of the cycle. The cycle is the segments added up, in
order: High dwell, Fade down, Low dwell, Fade up. Adding a segment later is one
more entry in the selector and one more slot in each bank.

| # | control | shown for |
|---|---|---|
| 1 | Segment {All segments, High dwell, Fade down, Low dwell, Fade up} | always |
| 2 | Length mode {BPM, Seconds, Hz, Every N beats, N per beat} | always |
| 3 | Length (BPM / sec / Hz / beats / per beat) | always |
| 4 | Fade shape {Linear, Cosine, Logarithmic, Exponential} | the fades, and All |
| 5 | Pitch mode {Hz, Semitones, Cents} | the dwells, and All |
| 6 | Note name | the dwells in Semitones |
| 7 | Frequency (Hz / semitones / cents) | the dwells, and All |
| 8 | Fine tune | the dwells, and All |
| 9 | Fine tune unit {Hz, Semitones, Cents} | the dwells, and All |

**A length in each mode**, computed by the plugin: Seconds — that many seconds.
Every N beats — that many beats. N per beat — that many fit in one beat. BPM — as
long as one beat at that tempo. Hz — as long as one cycle at that speed. The two
beat modes follow the live project tempo.

**All segments** writes a moved control into every segment it applies to (a pitch
into both dwells, a shape into both fades). Migrated instances land on High dwell,
never on All, as Polyrhythm's do.

## The order — 45 controls (src has 55)

| new | control | from src (55) | from installed (46) |
|---|---|---|---|
| 1–9 | the segment block above | 1–10, 12–17 into banks | 1–8 into banks |
| 10 | Tuning reference (Hz) | 11 | NEW, 440 |
| 11 | Resonance | 18 | 9 |
| 12 | Slope (dB/oct) | 55 | 46 |
| 13 | Stereo phase offset (degrees) | 20 | 11 |
| 14 | Phase mode | 21 | 12 |
| 15–19 | Pan enabled, Pan mode, Pan spread, Pan glide, Cycle steps | 22–26 | 13–17 |
| 20 | Pan sweep rate | 27 | 18 |
| 21 | Pan sweep rate mode | 28 | 19 |
| 22 | Pan sweep every (cycles) | 29 inverted | 20 inverted |
| 23 | Wet/dry mix | 19 | 10 |
| 24 | Start delay mode {BPM, Seconds, Hz, Every N beats, N per beat} | NEW, Seconds | NEW |
| 25 | Start delay | 30 | 21 |
| 26–29 | Play for, Rest for, LFO at rest, Output at rest | 31–34 | 22–25 |
| 30–37 | Drift block (target … rest for) | 43–50 | 34–41 |
| 38–45 | Ramp block (target … start delay) | 35–42 | 26–33 |

**Retired:** Cycle mode, Cycle length (beats), Cycle length mode — every length
now says its own unit; and Pan speed (Linked Sweep), a picker that writes a value
(R20). Before deleting, their jobs are carried: Host x + Fit puts every segment in
`Every N beats` at its own number; Host x + Set in beats puts every segment in
`Every N beats` at its number times (cycle length / sum). No saved instance uses
Host x, measured 2026-09-10.

## Drift and Ramp targets — 16

0 High dwell length, 1 Fade down length, 2 Low dwell length, 3 Fade up length,
4 High dwell frequency, 5 High dwell fine tune, 6 Low dwell frequency, 7 Low
dwell fine tune, 8 Tuning reference, 9 Resonance, 10 Stereo phase offset, 11 Pan
spread, 12 Pan glide, 13 Pan sweep rate, 14 Pan sweep every, 15 Wet/dry.

A length amount is in that segment's own length unit; a frequency or fine tune in
its own unit. Old index → new: `0→0, 1→1, 2→2, 3→3, 4→13, 5→9`.

## Save format

Segment banks (length mode, length, fade shape, pitch mode, note, frequency, fine
tune, fine tune unit) live in the blob. The migration WRITES a blob for instances
without one, as Heartbeat's did. New magic; old 2200006 read and remapped.

## Instances, measured 2026-09-10

- `E:/reaper/to-play-with-later/surges.RPP`, 1: installed 46 layout, blob 2200006
  with no drift or ramp set. Expected bit-identical.
- `E:/tensor's-rpp-projects/tensor-two-track-*.RPP`, 2: hand-written, 6 values
  then explicit zeros, on the April layout (`ae4a655`). Wet/dry is 0, so the filter
  has never been audible in them, and `Fade Down Shape = 50` suggests a value
  shifted by one slot. **Carried over exactly as REAPER loads them, clamps
  included; not guessed at.**
