# The Morpher's R26/R27 layout -- being talked through, NOT built

Started 2026-09-16. Decisions land here as Rozaya makes them, quoted. The full slider
order is authored here before any migration (CLAUDE.md). 39 projects load the Morpher.

## Decided

- **Transport unit** `{Seconds, Hz, Beats}`, the same three as Passage, sitting above Start
  delay, Play for and Rest for, whose names drop "(sec, or beats in Host x)" for "(in
  transport units)". Each saved project lands on what it counts today (Beats where Rate mode
  is Every N beats or N per beat, else Seconds), so nothing changes sound. Rozaya: *"That
  idea sounds like a good one yeah"*.

- **The existing `Rest mode` becomes `Auto-morph rest mode`**, in place. It still freezes
  only the morph walk. Offered `Rest mode (for Auto-morph)`; Rozaya: *"auto-morf rest mode"*.
  Plus `Drift rest mode` and `Ramp rest mode` inside their blocks, both
  defaulting to Walk through (today's behaviour). Named after Rozaya's pattern, and renamed to match in Veil and the Stereo Phaser the same
  day. Rozaya: *"Yes"*.

- **Wash grain leaves the Drift and Ramp target lists.** It stays a plain control. Measured
  below: a fast grain drift makes the wash wobble in loudness whatever the timing. Read
  2026-09-16, first Morpher per project: no project drifts or ramps it (27 on 300, six on
  150, two 400, two 600, one 200). Rozaya: *"if drift is going to fuck shit up, why bother
  having it *on there*?"* Removing it renumbers both pickers, so the migration moves every
  saved selection past it. Checked 2026-09-16: Play for and Rest for ARE per-occurrence
  targets -- @block recomputes pr_play_sec/pr_rest_sec (lines ~1697) against a running
  pr_accum, so a drift cuts the stretch being heard. So the Morpher DOES get `Drift movement
  {With the target, On a clock}` per target, for those two. Rozaya: *"the other sounds like
  a gap"*.

- **Spread gets a unit and the pitch block.** Told that in Hz the blur is one fixed width
  everywhere (it swallows the gaps between low harmonics and barely touches high ones) and
  that in Semitones it would blur evenly across the range; Rozaya: *"For that reason alone we
  should have a spread unit, and it should encorperate the usual pitch block."* Saved
  projects land on Hz with their numbers, so nothing changes sound. Semitones/Cents mean a
  blur reaching that interval either side of each frequency (a per-bin width -- new code in
  gen_grain's running-total blur). No note name: *"We don't need note names in there cause we're not setting them by that,
  it's just semitones worth of width."* So: Spread unit, Spread value, fine tune unit, fine tune.

## The full order, DRAFT 2026-09-16 -- being walked through with Rozaya

64 -> 79 controls. Rate pair renamed on Rozaya's *"we can try it, it can't hurt. renames are
free if it turns out I hate it."* `was` is today's slider id. Nothing here is built.

```
Capture
 1  Capture slot                                   was 1
 2  Capture now                                    was 2
 3  Capture point (%, earliest .. at press)        was 3
 4  Capture average (frames, all slots, ...)       was 4
The morph
 5  Audition                                       was 5
 6  Morph (% across captured slots)                was 6
 7  Auto-morph                                     was 7
 8  Auto-morph rate mode                           was 9   mode before value, renamed
 9  Auto-morph rate value                          was 8   renamed
The sound
10  Texture (% wash)                               was 10
11  Wash grain (ms)                                was 11  no longer a target
Pitch -- every name starts with `Pitch` (Rozaya: "it needs a pitch prefix anyway")
12  Pitch source note                              was 13  renamed
13  Pitch source fine tune unit                    was 15  mode before value, renamed
14  Pitch source fine tune                         was 14  becomes a target, renamed
15  Pitch target note                              was 16  renamed
16  Pitch transpose unit                           was 18  mode before value, renamed
17  Pitch transpose value                          was 17  renamed
18  Pitch fine tune unit                           was 20  mode before value, renamed
19  Pitch fine tune                                was 19  renamed
20  Tuning reference (Hz)                          was 21  stays plain, as suite-wide (Rozaya)
Spread -- AFTER pitch. Rozaya: "spread is what you do after you've set a pitch"
21  Spread unit {Hz, Semitones, Cents}             NEW     saved copies: Hz
22  Spread value                                   was 12
23  Spread fine tune unit                          NEW
24  Spread fine tune                               NEW     0
25  Stereo width (%)                               was 22
26  Denoise (%, wash only)                         was 23
27  Low cut pitch mode {Hz, Semitones, Cents}      NEW     saved copies: Hz
28  Low cut note name                              NEW
29  Low cut value                                  was 24  (off: ASK)
30  Low cut fine tune unit                         NEW
31  Low cut fine tune                              NEW
32  High cut pitch mode                            NEW     saved copies: Hz
33  High cut note name                             NEW
34  High cut value                                 was 25  (off: ASK)
35  High cut fine tune unit                        NEW
36  High cut fine tune                             NEW
37  Overtone harmonic                              was 26
38  Overtone lift                                  was 27
39  Overtone width                                 was 28
Layers
40  Layer                                          was 29
41  Layer active                                   was 30
42  Layer pitch unit                               was 32  mode before value
43  Layer pitch value                              was 31
44  Layer fine tune unit                           was 34  mode before value
45  Layer fine tune                                was 33
46  Layer level                                    was 35
47  Layer solo                                     was 36
48  Layer harmonics                                was 37  becomes a target (All + 16)
49  Layer overtone harmonic                        was 38
Levels
50  Input level (dry, dB)                          was 39
51  Output level (dB, ...)                         was 40
Transport
52  Transport unit {Seconds, Hz, Beats}            NEW     from Rate mode
53  Start delay (in transport units)               was 41
54  Play for (in transport units, 0 = always)      was 42
55  Rest for (in transport units, 0 = always)      was 43
56  Auto-morph rest mode                           was 44  renamed
57  Output at rest                                 was 45
Drift
58  Drift target                                   was 46
59  Drift amount unit                              was 49  mode before value
60  Drift up amount                                was 47
61  Drift down amount                              was 48
62  Drift period unit (per target)                 was 51  mode before value, loses (all targets)
63  Drift period                                   was 50
64  Drift movement                                 NEW     With the target
65  Drift shape                                    was 52
66  Drift play for                                 was 53
67  Drift rest for                                 was 54
68  Drift rest mode                                NEW     Walk through
69  Drift restart (all targets)                    was 55
Ramp
70  Ramp target                                    was 56
71  Ramp by unit                                   was 58  mode before value
72  Ramp by                                        was 57
73  Ramp time unit (per target)                    was 59  loses (all targets)
74  Ramp duration                                  was 60
75  Ramp play for                                  was 61
76  Ramp rest for                                  was 62
77  Ramp rest mode                                 NEW     Walk through
78  Ramp engage (all targets)                      was 63
79  Ramp start delay                               was 64
```

Targets (Drift and Ramp share one list, control order): today's 87, minus Wash grain, plus
Source fine tune, Spread fine tune, Low cut fine tune, High cut fine tune, and Layer
harmonics (all layers) + 16 -- 107. Confirm the four fine tunes with Rozaya.

## Still to talk through

- Drift period unit and Ramp time unit per target.
- Layer harmonics and Source fine tune as drift/ramp targets.
- Every mode in front of its value (Transpose, Fine tune, Source fine tune, Layer pitch,
  Layer fine tune, both amount units, Auto-morph time and Rate mode).
- Low cut and High cut as pitch blocks.
- **Drift movement on Wash grain, measured 2026-09-16, not yet decided.** Each grain is
  written whole (`gen_grain`), but the hop moves mid-hop. Probe: test copies summing the
  synthesis window alone into a third accumulator (overlap evenness, independent of the
  audio), `breathing.RPP`, Texture 100. Drift off: 1.9% typical wobble. Gentle sine drift
  (+-50 ms, 10 s): 2.2% now, 2.0% latched -- nothing. Fast random drift (+-250 ms, 0.5 s):
  16.2% now vs 12.1% latched; 10 ms stretches over 30% off, 262 now vs 89 latched, worst
  bump +90% either way. Latching helps, but the wobble under a fast grain drift remains
  in both: grains of different lengths overlapping is uneven whatever the timing.
  jsfx_run note: the Morpher ignores drift edits until @block adopts the mirror -- set the
  selector with `--set-after`, then `--stage`, then the values, or the drift never runs.
