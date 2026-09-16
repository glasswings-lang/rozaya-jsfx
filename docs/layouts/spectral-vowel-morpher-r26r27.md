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
  pr_accum, so a drift cuts the stretch being heard. So the Morpher DOES get `Drift movement mode
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

## The full order, AGREED 2026-09-16

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
16  Pitch transpose mode                           was 18  mode before value, renamed
17  Pitch transpose value                          was 17  renamed
18  Pitch fine tune unit                           was 20  mode before value, renamed
19  Pitch fine tune                                was 19  renamed
20  Tuning reference (Hz)                          was 21  stays plain, as suite-wide (Rozaya)
Spread -- AFTER pitch. Rozaya: "spread is what you do after you've set a pitch"
21  Spread pitch mode {Hz, Semitones, Cents}       NEW     saved copies: Hz (Rozaya: "Go for that too")
22  Spread value                                   was 12
23  Spread fine tune unit                          NEW
24  Spread fine tune                               NEW     0
25  Stereo width (%)                               was 22
26  Denoise (%, wash only)                         was 23
27  Low cut pitch mode {Hz, Semitones, Cents}      NEW     saved copies: Hz
28  Low cut note name {Off, C-1 .. G9}             NEW
29  Low cut value (0 = off, in any unit)          was 24
30  Low cut fine tune unit                         NEW
31  Low cut fine tune                              NEW
32  High cut pitch mode                            NEW     saved copies: Hz
33  High cut note name {Off, C-1 .. G9}            NEW
34  High cut value (0 = off, in any unit)         was 25  saved 20000 (today's off) -> 0; range 0..20000
35  High cut fine tune unit                        NEW
36  High cut fine tune                             NEW
37  Overtone harmonic                              was 26
38  Overtone lift                                  was 27
39  Overtone width                                 was 28
Layers
40  Layer                                          was 29
41  Layer active                                   was 30
42  Layer pitch mode                               was 32  mode before value, renamed
43  Layer pitch value                              was 31
44  Layer fine tune unit                           was 34  mode before value
45  Layer fine tune                                was 33
46  Layer level                                    was 35
47  Layer solo                                     was 36
48  Layer harmonics                                was 37  becomes a target (All + 16)
49  Layer overtone harmonic                        was 38
Levels
50  Input level (dry, dB)                          was 39  global, measured 2026-09-16
51  Output level (dB, ...)                         was 40  global, measured 2026-09-16
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
64  Drift movement mode                            NEW     With the target (renamed suite-wide, Rozaya)
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

Both cuts: 0 means off in every unit, and each note name list starts on a dedicated Off.
Rozaya: *"Feels like 0 could just be 0, then the first thing everything lands on is a
dedicated off position"*. (Asked because the note names stop at G9, ~12.5 kHz, so High
cut's old off at 20000 Hz could not be reached by note.) A drift or ramp cannot carry a cut
across 0 into off by accident: clamp the effective value at the lowest real frequency when
the base value is on. CHECK THAT CLAMP WHEN BUILDING.

A value's Hz/semitones/cents picker is a `pitch mode`, as Veil's and the Phaser's are (fine
tune pickers stay `fine tune unit`). Rozaya: *"yeah. I think it should."* The drift clamp
on the cuts: *"I like that re: the drift move."*

Targets (Drift and Ramp share one list, control order): today's 87, minus Wash grain, plus
Source fine tune, Spread fine tune, Low cut fine tune, High cut fine tune, and Layer
harmonics (all layers) + 16 -- 107. Rozaya, on the new fine tunes as targets: *"Yeah it is"*.

**The whole order was walked through with Rozaya on 2026-09-16 and is agreed.**

## Still to talk through

- Drift period unit and Ramp time unit per target.
- Layer harmonics and Source fine tune as drift/ramp targets.
- Every mode in front of its value (Transpose, Fine tune, Source fine tune, Layer pitch,
  Layer fine tune, both amount units, Auto-morph time and Rate mode).
- Low cut and High cut as pitch blocks.
- **Drift movement mode on Wash grain, measured 2026-09-16, not yet decided.** Each grain is
  written whole (`gen_grain`), but the hop moves mid-hop. Probe: test copies summing the
  synthesis window alone into a third accumulator (overlap evenness, independent of the
  audio), `breathing.RPP`, Texture 100. Drift off: 1.9% typical wobble. Gentle sine drift
  (+-50 ms, 10 s): 2.2% now, 2.0% latched -- nothing. Fast random drift (+-250 ms, 0.5 s):
  16.2% now vs 12.1% latched; 10 ms stretches over 30% off, 262 now vs 89 latched, worst
  bump +90% either way. Latching helps, but the wobble under a fast grain drift remains
  in both: grains of different lengths overlapping is uneven whatever the timing.
  jsfx_run note: the Morpher ignores drift edits until @block adopts the mirror -- set the
  selector with `--set-after`, then `--stage`, then the values, or the drift never runs.

## Build progress (a handoff: read this first if picking the build up)

Plan: stages in src, measured each time; the 39 live projects (123 instances, plus
`C:/Users/solst/Dropbox/quick one.RPP`) are migrated ONCE at the end; nothing installed until then.

**Found 2026-09-16:** 122 of 123 live instances hold OLD blobs (7700001 x27, 7700002 x70,
7700005 x2, 7700008 x20, 7700010 x3); only the bridge test project has 7700087. The plugin
converts them on load. So the migration first RESEALS each instance through the pre-build
Morpher (jsfx_run --save-rpp, render-compared with `_tp = time_precise();` pinned to 0.25,
silence in, as tools/morpher_verify_20260913.py does), then transcodes 7700087 -> the new
magic in Python, keyed on the magic. Survey helpers were in the session scratchpad
(morpher_blob.py: parse87); rebuild them into the tool.

- **Stage 1, renumber, DONE:** `tools/jsfx_renumber.py` map (old:new)
  `1-7:+0, 9:8, 8:9, 10:10, 11:11, 13:12, 15:13, 14:14, 16:15, 18:16, 17:17, 20:18, 19:19,
  21:20, 12:22, 22:25, 23:26, 24:29, 25:34, 26:37, 27:38, 28:39, 29:40, 30:41, 32:42, 31:43,
  34:44, 33:45, 35:46, 36:47, 37:48, 38:49, 39:50, 40:51, 41:53, 42:54, 43:55, 44:56, 45:57,
  46:58, 49:59, 47:60, 48:61, 51:62, 50:63, 52:65, 53:66, 54:67, 55:69, 56:70, 58:71, 57:72,
  59:73, 60:74, 61:75, 62:76, 63:78, 64:79`. Verify PASS on pinned copies (text, declarations,
  28 continuous and 36 selectors bit-identical).
- **Stage 2, names, DONE** (labels only).
- **Stage 3, Transport unit, DONE:** slider52 {Seconds, Hz, Beats}; Rate mode no longer touches
  the three times; switching the unit converts them (checked: 2 s -> 4 beats at 120, -> 0.5 Hz,
  0 stays 0). Migration seed: 2 where old slider9 >= 3, else 0. Old pinned build on
  breathing.RPP vs new pinned build on `convert_line`: bit-identical as saved, with play/rest
  in seconds, and under Every N beats at 97 BPM. Checks: tools/morpher_r26r27_checks/
  (stage_check.py needs a scratch dir holding pin/old and pin/new copies, `_tp` pinned).
- **Stage 4, Drift rest mode (68) and Ramp rest mode (77), DONE:** global, Walk through by
  default. Unset slots read as Walk through, so no seed. Bit-identical on breathing.RPP as
  saved and with play/rest; a probe showed drift and ramp offsets frozen through every rest on
  Freeze in place and moving on Walk through.
- **Stage 5, DONE:** 107 targets (t107_o2n; Wash grain dropped, a picker on it lands on Morph),
  drift loop order carried so rand() draws as before; per-target Drift period unit, Ramp time
  unit, Drift movement mode (latches Play for / Rest for per stretch); Layer harmonics (LH_T0)
  and Pitch source fine tune wired; blob 7700107 appends the three banks, an older blob remaps
  87 -> 107 and seeds units from sliders 62/73. convert_line remaps pickers 58/70. Measured:
  breathing (blob 7700001) and the bridge test project (7700087, 24 drifts incl. Random)
  bit-identical as saved and with play/rest; a 7700107 save reopens bit-identical with every
  control equal; per-target units stay per target; movement mode 11/11 held; harmonics drift
  0..10; source fine tune +-50 cents moves pitch only with a source note. NOT YET READ BY
  ANYTHING: targets 8, 12, 14 (Spread / cut fine tunes) -- stages 6 and 7 wire them.
- **Stage 6, Spread block, DONE:** 21 mode, 22 value, 23 fine unit, 24 fine; targets 7 and 8
  wired (sp_q). Hz with fine 0 runs the old expression. Semitones/Cents: per-bin window
  f/r..f*r via running sums (spc), an Hz fine tune widens both sides. Measured: breathing (as
  saved, and at Spread 150) and the bridge project bit-identical old vs new; a snapshot probe
  of curmag straight after the blur matched an independent numpy blur to ~4e-8 for 2 semitones,
  2 semitones + 40 Hz, breathing's own 100 Hz, and 100 Hz + 12 semitone fine tune (= 200 Hz).
- **Stage 7, cut blocks, DONE:** 27-31 Low cut, 32-36 High cut; 0 = off in every unit, note list
  {Off, C-1..G9}; note <-> value linked and a mode switch converts (trackers adopted in @block).
  On: Hz with no fine tune is the old expression; a drift stops at one FFT bin (low) / 200 Hz
  (high, as before) instead of switching off; High cut reaching 20000 is off, as before. Off: a
  drift moves nothing (undoes 2026-09-13's "a cutoff at 0 still moves" -- CHECK the reseal
  survey for any project drifting a cut from 0). Migration: Hz as saved, note from cut_note,
  High cut 20000 -> 0. Measured: breathing and bridge bit-identical as saved, with cuts 150/3000
  and 90/5000 + play/rest; 150 Hz <-> 50.37 st <-> 150; note A4 -> 440; 0 -> Off; drift limits.
- Still to build:
  9 migration (reseal old blobs, transcode 7700087 -> 7700107 keyed on magic), verify, install.
