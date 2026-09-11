# Spectral Vowel Morpher — fifty-five Drift and Ramp targets, 2026-09-11

No slider moves; the two target lists grow from 24 to 55 and reorder. **Status:
AUTHORED 2026-09-11, before any code.** Snapshot `_pre-morpher-r24-20260911/`
(39 projects, 123 instances); previous build in
`jsfx-backups/effects-folder-baks/pre-morpher-r24-20260911/`.

## What Rozaya decided (quoted), and what is mine

- Morpher next: *"Go for it."*
- "All layers" entries on the Polyrhythm model; Layer harmonics, Capture point and
  Capture average NOT targets: *"Yes, so long as you explain why the two
  non-drifted ones weren't included."* The why is on the controls in the source and
  on the plugin page: Layer harmonics is a CPU cap, so drifting it swings the load;
  Capture point and Capture average re-analyse the captures, heavy, and would click.
- R24 (Star): every sound-shaping control, Play for and Rest for, control order.
- **Mine, unquoted:** the names; the Morph target moves the Morph slider's own
  position, so it acts only while Auto-morph is Off; a layer's overtone drift moves
  only a layer that has its own harmonic (a follower stays a follower, as a level
  drift never un-mutes a layer); clamps to each control's range; Play/Rest still
  switch on only when their sliders are above 0. Side effect, needed for the drift
  and said here: a per-layer overtone harmonic change now rebuilds the overtone
  curve at once; before, it waited for a change to the global overtone.

## The list — 24 become 55, in control order

0 Morph, 1 Auto-morph time, **2 Texture**, 3 Wash grain, **4 Spread**, **5 Pitch**,
**6 Stereo width**, 7 Denoise, **8 Low cut**, **9 High cut**, **10 Overtone
harmonic**, 11 Overtone lift, 12 Overtone width, 13 Layer level (all layers),
**14-29 the sixteen layer levels** (ladder order, as the Layer selector), 30 Layer
pitch (all Custom layers), 31-33 Custom 1-3 pitch, 34 Layer overtone harmonic (all
layers), 35-50 the sixteen layer overtone harmonics, 51 Input level, **52 Output
level**, 53 Play for, 54 Rest for. (Bold: existed.)

Old -> new: `0->2, 1->4, 2->5, 3->6, 4->8, 5->52, 6->10, 7->9, 8+i->14+i`.

The three "all" entries hold nothing of their own (Polyrhythm's shape): reading one
shows its first member, editing it writes every member. Not targets: Capture slot,
Capture now, Capture point, Capture average, Audition, Auto-morph, Rate Mode, Layer,
Layer active, Layer solo, Layer harmonics, Start delay, Rest mode, Output at rest,
Drift restart, and the drift/ramp controls themselves.

## How the values are read

Per block: Auto-morph time, Wash grain, Custom pitches, Play/Rest. Per sample, and
only while driven (so an undriven copy is exactly today's): Morph, Denoise, Overtone
lift and width, layer overtone harmonics, Input level, and the existing eight.
Target selectors switch to Polyrhythm's change-detected capture, adopted in @block.

## Save format and memory

Magic `7700011 -> 7700055`. Every older magic still reads at its own width, runs
its existing layer-order migration, and is then remapped from the 24-target list
with both selectors. Per-target banks respaced from 32 to 64 slots (allocation
only). The drift loop runs the old twenty-four FIRST, in their old order: `rand()`
is one stream. Testing pins the plugin's per-load `time_precise()` scramble in test
copies only -- two runs of the same build otherwise never match.

## Instances

123 in 39 projects, all 51-value lines. Blobs: 7700002 x70, 7700001 x27, 7700008
x20, 7700010 x3, 7700005 x2, 7700011 x1. Selectors other than 0: nine instances.
Every line's two selectors (35, 44) are remapped.

## A bug the 123-instance check could not see

A bulk rename made the new per-layer overtone loop read its own output, so every
layer followed the global harmonic -- while all 123 instances still rendered
identical, because none uses a layer overtone harmonic. The target test failed on a
project whose captures had no usable voice; Rozaya's questions (was the lift raised,
was the harmonic high enough, did the sound have more than one harmonic) led to
testing on `breath-by-breath pt. 2`, a pitched voice, lift 36 dB. There the old build
changed with the harmonic and the new did not. Fixed; the `layers` section now
checks old == new with a layer harmonic set by hand.

Tools: `tools/morpher_r24_migrate_20260911.py`, `tools/morpher_r24_verify_20260911.py`.
