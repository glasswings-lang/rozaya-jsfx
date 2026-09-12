# Spectral Vowel Morpher — All slots, 2026-09-11

**Status: AUTHORED 2026-09-11 before any code; BUILT, MEASURED and installed the same
day. Not heard.** `tools/morpher_all_slots_verify_20260911.py`: 123 of 123 saved
instances bit-identical; All fills each slot exactly as an ordinary capture into it;
Capture point on All == by hand on Slots 1 and 8, and moves Slots 4 and 5; passing
through All keeps Slot 8's own point. **Not measured: the capture's CPU inside REAPER.**
It runs the eight analyses a Capture average change already runs in one block. No slider moves. Passage gets the
same feature inside its own single migration (`docs/layouts/spectral-vowel-passage.md`).

## What Rozaya decided (quoted), and what is mine

- The feature, said of Passage: *"have an all slots thing, meaning you can capture
  to all of them, effect all of them, etc. then modify each as you see fit."*
- *"Yes, capture should grab into all 8 slots. tbqh, morfer needs it too"* -- one
  press, the same moment, in all eight.
- **Mine, unquoted:** everything below.

## The control

`Capture slot` becomes `{All, Slot 1, ..., Slot 8}`, range 0-8. It was a plain 1-8
number, so every saved value keeps its meaning: 1 is still Slot 1. **No migration.**
All sits first, as on Polyrhythm's Voice, Heartbeat's and Breath Generator's Pitch
target and Rhythm Track's.

## On All

- **Capture now** grabs the same moment into all eight slots, each stamped with the
  Capture point on screen.
- **Capture point** shows Slot 1's and writes all eight -- change-detected on
  Polyrhythm's model, so parking on All, or a stray @slider pass on load, flattens
  nothing.
- **Capture average** is already global. Nothing else in the Morpher is per slot.
- **Audition, Focused slot** plays Slot 1 while All is selected. Said on the plugin
  page.

## Measure, don't predict

Eight captures in one block run eight spectrum and harmonic analyses. Measure the
block with `tools/jsfx_run`. If it is heavy enough to risk a dropout, grab the raw
audio once, copy it to the other seven, and analyse one slot per block.

## Verify

- Every saved instance's slider line is unchanged, and a copy saved on Slot 3 opens
  on Slot 3 (the load path reads `slider1 - 1`; All must not read as slot -1).
- Captures on All: eight identical raw buffers, eight identical analyses.
- On All, changing Capture point reaches all eight; selecting All alone changes none.
- Bridge test: add All slots to the Morpher's item-selector checks.
