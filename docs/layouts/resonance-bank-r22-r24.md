# Resonance Bank — pitch per band, width units, Tuning reference, 10 targets

Authored 2026-09-11, before building. One migration for everything here.
**Status: BUILT AND MEASURED 2026-09-11. Not heard.** Snapshot
`_pre-rb-r22-20260911/`; previous build in
`jsfx-backups/effects-folder-baks/pre-rb-r22-20260911/`.
`tools/resonance_bank_verify_r22r24_20260911.py`: all pass.

**Found while doing it:** `rand()` is one stream shared with the Random drift
shape. Seeding the new slots from it shifted every later random draw and `wind`
stopped matching; they are now scattered from the old slots' values instead.

## What Rozaya decided (quoted), and what is mine

- On widths staying in Hz: *"Widths can take in semitones and sents as well,
  there's no reason why not."*
- Proposed by Claude, then *"Yep, go for it all"*: each band gets its own pitch
  set behind the Band selector, as Polyrhythm's voices do; one Tuning reference
  near the top, where Polyrhythm keeps its own; Fine tune and the four
  whole-plugin controls become targets in this same migration.
- **Mine, unquoted:** a width's unit sits AFTER its value, as Fine tune unit does
  (a width is an interval, not a place, so it has no note name); a width in
  Semitones or Cents is measured from the band's frequency as it is that moment,
  fine tune and drift included; the target order; the four global targets hold
  one setting whichever band is selected.

## The order — 28 controls become 35

| new | control | from |
|---|---|---|
| 1 | Input gain (dB) | 1 |
| 2 | Mode | 2 |
| 3 | Tuning reference (Hz) 20–2000 | NEW, 440 |
| 4 | Band selector (0-15) | 3 |
| 5 | Pitch mode {Hz, Semitones, Cents} | NEW, per band, Hz |
| 6 | Note name {C-1 … G9}, shown in Semitones | NEW, per band, 69 |
| 7 | Frequency (Hz / semitones / cents) 0–20000 step 0.001 | 4 |
| 8 | Fine tune -1000–1000 | NEW, per band, 0 |
| 9 | Fine tune unit {Hz, Semitones, Cents} | NEW, per band, Cents |
| 10 | Width up (Hz / semitones / cents) 0–20000 step 0.001 | 5 (was 1–5000 step 1) |
| 11 | Width up unit {Hz, Semitones, Cents} | NEW, per band, Hz |
| 12 | Width down (Hz / semitones / cents) | 6 |
| 13 | Width down unit | NEW, per band, Hz |
| 14–17 | Gain, Pan, Order, Band solo | 7–10 |
| 18–19 | Wet/dry mix, Output volume | 11–12 |
| 20–27 | Drift target … Drift rest for | 13–20 |
| 28–35 | Ramp target … Ramp start delay | 21–28 |

A width is still floored at 1 Hz after conversion, as today. Names follow the
Sweeping Filter and Sweep Dwell, so the siblings read the same.

## Drift and Ramp targets — 5 become 10, in control order

| idx | target | kind | amount is in |
|---|---|---|---|
| 0 | Input gain | whole plugin | dB |
| 1 | Tuning reference | whole plugin | Hz, clamped 20–2000 |
| 2 | Frequency | per band | the band's Pitch mode unit |
| 3 | Fine tune | per band | the band's Fine tune unit |
| 4 | Width up | per band | the band's Width up unit |
| 5 | Width down | per band | the band's Width down unit |
| 6 | Gain | per band | dB |
| 7 | Pan | per band | -1–1 |
| 8 | Wet/dry | whole plugin | 0–1 |
| 9 | Output volume | whole plugin | 0–1 |

Old → new: `0→2, 1→4, 2→5, 3→6, 4→7`. A whole-plugin target is stored in band
0's row at its own index, which no per-band target uses; every band reaches the
same slot.

## Engine

Frequency: `value + drift + ramp` in its own unit, then fine tune, then Hz — no
20 Hz floor, because today a band can sweep down through zero. In Hz with a Cents
fine tune of 0 this is the old sum times exactly 1, so migrated bands are
bit-identical. Widths convert after the frequency, from it.

`@init` seeds the per-band targets' random drift phases in the OLD order first
(Frequency, Width up, Width down, Gain, Pan), then the new ones, so `rand()` is
consumed exactly as before and random drifts stay bit-identical.

## Save format

Magic `4016010`. New per-band banks: pitch mode, note, fine tune, fine tune unit,
width up unit, width down unit. Target banks become 160 wide at new addresses;
v1, v2 and v3 blobs are read into the old 80-wide addresses exactly as today, then
copied across through the map above, and each band's remembered drift and ramp
target is remapped the same way.

## Instances, measured 2026-09-11

- `E:/reaper/to-play-with-later/wind.RPP`, 1: blob 1016005 (v1), 18 values on
  the 28 layout. Drift in use: band 4 Frequency 100/50 Hz over 30 s, Random; Gain
  on bands 1, 2, 3, 5; Pan on band 5. Expected bit-identical.
  **MIGRATED 2026-09-11**; the live file re-rendered bit-identical.
- `E:/reaper/finished/test-projects/claude-testing002-bridge.RPP`, 1: the bridge
  test project. Verified in a temp copy, **NOT yet written**: it was open in
  REAPER with unsaved changes. Run the migration on it once REAPER has closed it
  without saving, or `tools/bridge_ui_test.py` reads the wrong controls.

## Verify

Old build on the snapshot against the new on the migrated project, noise in,
bit-identical and non-silent. A crafted v3 save with drift and ramp on all five
old targets, old against new. Each of the 10 targets changes the sound and stays
finite. A width of 12 semitones on a 1000 Hz band matches 1000 Hz typed in Hz.
`tuning_ref_check.py` gains Resonance Bank. Band switching, note mirror and save
and reopen through the bridge.
