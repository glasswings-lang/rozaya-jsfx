# Passage takes over from the Morpher -- AGREED, NOT built

Started 2026-09-16. Decisions land here as Rozaya makes them, quoted; everything unquoted is
Claude's proposal. The whole order is authored here before any migration (CLAUDE.md).
Passage today: 63 controls, magic 7700008, 10 projects (49 copies at the 09-13 install).

## Decided

- **Passage takes over; the Morpher's layers and everything else it has move in.** Rozaya:
  *"They absolutely do belong in passage."* (`docs/backlog.md`, "Decided 2026-09-16".)
- **Layers are global, not per slot.** Rozaya: *"the per slot layering doesn't really make
  sense to me ... I would just have it be global"*. Thickening one slot: All slots, then nudge.
- **Auto-morph's continuous sweep comes back.** Rozaya: *"Passage needs it."*
- **Unit pickers above the timings they set, names lose `seconds / Hz / beats`**; fade shapes
  stay under the timings. Rozaya said yes (backlog).
- **Grain auto-gain removed; layers default -6 dB and Inactive** (current-state, both quoted).
- **The voice engine cost is fixed inside this build**, not left for later: 16 layers on the
  per-partial sine engine would drop out as the Morpher's do.

## Agreed 2026-09-16 with the whole order below

Rozaya, on the full draft with these two points: *"It seems OK to me, tbh. I liked what I saw
in morfer so..."*


- **`Auto-morph timing {Slot timings, Rate}`** under Auto-morph. Slot timings = today's
  slot-to-slot walk (saved copies land here, nothing changes). Rate = the Morpher's glide
  along the slot line at `Auto-morph rate mode` / `value`, for Sweep, Glide once and Shuffle.
  (The continuous glide was replaced by the slot walk when Passage was born, `4fe51a1`; no
  record of Rozaya asking for that.)
- **Layer 1 is the original voice**, as in the Morpher: Active at 0 dB. Layers 2-16 start
  Inactive at -6 dB. A saved Passage lands on Layer 1 alone, sounding as today.
- Everything else below is the Morpher's agreed shape copied, with Passage's per-slot
  sections kept.

## The wash's hidden boost goes, and saved projects keep their loudness (decided 2026-09-16)

Measured first: Passage's grain auto-gain adds a steady, per-capture boost of +37.6 to +65.3 dB
across the 23 wash copies (median +47.2). In the Morpher it also normalised the wash to Layer 1:
breathing.RPP, Layer 1 at -24 dB changed the level by -0.1 dB, and Layer 1 -24 with Layer 10 -12
came out +16 dB (Layer 10 heard 12 dB ABOVE Layer 1). The voice end was never affected.
Rozaya, on keeping saved work as it sounds: *"I say you can try to make them sound the same.
they're finished and won't be re-rendered, or are at least very unlikely to be re-rendered."* And on
the Morpher: *"the morfer's do [have layers], and in morfer I used it. so if we do migrate these, we
have to account for it anyway."*
So: one fixed wash gain replaces the auto-gain; the migration sets each slot's Output level to hold
each saved copy's measured loudness; the Morpher -> Passage carry-over must turn its wash layer
levels into what was heard (each layer relative to Layer 1) and account for the boost too.

## The Morpher carry-over (started 2026-09-16)

Measured: 136 Morpher copies in 41 projects; 135 all wash, 111 Shuffle, 19 with layers on (9 of those
with Layer 1 silent), 7 drifting, 1 Random drift on a target that becomes per slot (revery).
Rozaya, on replacing the Morpher inside the projects rather than writing copies: *"replace them."*
How the layer levels should read afterwards: asked again, in plainer words.

## The full order, AGREED 2026-09-16

`was` is today's Passage slider id. P = per slot, G = global.

```
Capture
 1  Capture slot {All, Slot 1-8}                   was 1
 2  Capture now                                    was 2
 3  Capture point                                  was 3   P
 4  Capture average                                was 4   P
The morph
 5  Audition                                       was 36  G
 6  Morph                                          was 34  G
 7  Auto-morph                                     was 35  G
 8  Auto-morph timing {Slot timings, Rate}         NEW     G  saved: Slot timings
 9  Auto-morph rate mode                           NEW     G  BPM..N per beat, default Seconds
10  Auto-morph rate value                          NEW     G  20
Slot timing
11  Slot timing unit                               was 25  P  moved above
12  Slot fade in (in slot timing units)            was 21  P
13  Slot hold                                      was 22  P
14  Slot fade out                                  was 23  P
15  Slot gap after                                 was 24  P
16  Fade in shape                                  was 31  G
17  Fade out shape                                 was 32  G
18  Slot crossfade into next                       was 26  P
19  Slot mute                                      was 27  P
The sound
20  Texture                                        was 13  P
21  Wash grain                                     was 14  P  no longer a target
Pitch
22  Pitch source note                              was 5   P
23  Pitch source fine tune unit                    was 7   P
24  Pitch source fine tune                         was 6   P  becomes a target
25  Pitch target note                              was 8   P
26  Pitch transpose mode                           was 10  P
27  Pitch transpose value                          was 9   P
28  Pitch fine tune unit                           was 12  P
29  Pitch fine tune                                was 11  P
30  Tuning reference                               was 30  G
Spread and tone
31  Spread pitch mode                              NEW     P  saved: Hz
32  Spread value                                   was 15  P
33  Spread fine tune unit                          NEW     P
34  Spread fine tune                               NEW     P
35  Stereo width                                   was 28  P
36  Denoise                                        was 16  P
37  Low cut pitch mode                             NEW     P  saved: Hz
38  Low cut note name {Off, C-1..G9}               NEW     P
39  Low cut value (0 = off)                        was 17  P
40  Low cut fine tune unit                         NEW     P
41  Low cut fine tune                              NEW     P
42  High cut pitch mode                            NEW     P  saved: Hz
43  High cut note name {Off, C-1..G9}              NEW     P
44  High cut value (0 = off)                       was 18  P  saved 20000 -> 0
45  High cut fine tune unit                        NEW     P
46  High cut fine tune                             NEW     P
47  Overtone harmonic                              was 19  P
48  Overtone lift                                  was 20  P
49  Overtone width                                 was 33  G
Layers (all global)
50  Layer {All, Layer 1-16}                        NEW
51  Layer active                                   NEW     L1 Active, others Inactive
52  Layer pitch mode                               NEW
53  Layer pitch value                              NEW
54  Layer fine tune unit                           NEW
55  Layer fine tune                                NEW
56  Layer level                                    NEW     L1 0 dB, others -6
57  Layer solo                                     NEW
58  Layer harmonics                                NEW
59  Layer overtone harmonic (-1 = follow)          NEW
Levels
60  Input level (dry, dB)                          was 37  G
61  Output level (dB)                              was 29  P
Transport
62  Transport unit                                 was 41  G  moved above
63  Start delay (in transport units)               was 38  G
64  Play for                                       was 39  G
65  Rest for                                       was 40  G
66  Auto-morph rest mode                           was 42  G  renamed
67  Output at rest                                 was 43  G
Drift
68  Drift target                                   was 44
69  Drift amount unit                              was 47  mode before value
70  Drift up amount                                was 45
71  Drift down amount                              was 46
72  Drift period unit (per target)                 was 49
73  Drift period                                   was 48
74  Drift movement mode                            was 50
75  Drift shape                                    was 51
76  Drift play for                                 was 52
77  Drift rest for                                 was 53
78  Drift rest mode                                NEW     Walk through
79  Drift restart (all targets)                    was 54
Ramp
80  Ramp target                                    was 55
81  Ramp by unit                                   was 57  mode before value
82  Ramp by                                        was 56
83  Ramp time unit (per target)                    was 58
84  Ramp duration                                  was 59
85  Ramp play for                                  was 60
86  Ramp rest for                                  was 61
87  Ramp rest mode                                 NEW     Walk through
88  Ramp engage (all targets)                       was 62
89  Ramp start delay                               was 63
```

63 -> 89. Targets, control order, 111: Morph, Auto-morph rate, Slot fade in, Slot hold, Slot
fade out, Slot gap after, Texture, Pitch source fine tune, Pitch transpose, Pitch fine tune,
Tuning reference, Spread, Spread fine tune, Stereo width, Denoise, Low cut, Low cut fine tune,
High cut, High cut fine tune, Overtone harmonic, Overtone lift, Overtone width, Layer pitch /
fine tune / level / harmonics / overtone harmonic (All + 16 each), Input level, Output level,
Play for, Rest for. Wash grain leaves (the Morpher's measured reason applies to the same engine).

## To check when building

- How a global target (layers, Auto-morph rate) drifts under Passage's per-slot drift keying.
- The cut clamp (a drift must not carry an on cut into off), as in the Morpher.
- `tools/morpher_to_passage.py` must carry layers once they exist.

## Build progress (a handoff: read this first if picking the build up)

Same method as the Morpher (`docs/history/layouts/spectral-vowel-morpher-r26r27.md`): stages
in src, each measured; live projects migrated ONCE at the end; nothing installed until then.
Pre-build copy for comparisons: keep one pinned outside the repo (`git show 48e3771:src/...`).

- **Stage 1, renumber, DONE:** map `1-4:+0, 36:5, 34:6, 35:7, 25:11, 21:12, 22:13, 23:14,
  24:15, 31:16, 32:17, 26:18, 27:19, 13:20, 14:21, 5:22, 7:23, 6:24, 8:25, 10:26, 9:27, 12:28,
  11:29, 30:30, 15:32, 28:35, 16:36, 17:39, 18:44, 19:47, 20:48, 33:49, 37:60, 29:61, 41:62,
  38:63, 39:64, 40:65, 42:66, 43:67, 44:68, 47:69, 45:70, 46:71, 49:72, 48:73, 50:74, 51:75,
  52:76, 53:77, 54:79, 55:80, 57:81, 56:82, 58:83, 59:84, 60:85, 61:86, 62:88, 63:89`.
  Verify PASS (text, declarations, 28 continuous + 35 selectors bit-identical).
- **Stage 2, names, DONE** (labels only).
- **Stage 3, DONE:** Drift rest mode (78), Ramp rest mode (87), Walk through by default.
- **Stage 4, DONE:** Spread (31-34), Low cut (37-41), High cut (42-46) as per-slot pitch blocks,
  the Morpher's functions; blob 7700009 appends nine per-slot banks; an older blob's High cut 20000
  becomes 0 in the plugin, and `convert_line` does the same on the slider line and sets the note
  names. Checks: `tools/passage_takeover_checks/stage4.py` (every live instance, old vs new).
- **Stage 5, DONE:** the voice is one wavetable per voice position (wt_build / wt_check / wt_read /
  wt_take). `engine_compare.py`: nightfall, all voice, widths 50 and 0, -117 dB from the sine
  engine; block time roughly halved.
- **Stage 5b, DONE:** drift/ramp work lists; bit-identical with drifts and a ramp set after load.
- **Stage 6, DONE:** sixteen global layers (voice: own wavetable pair each; wash: the grain spectrum
  read again at each ratio; per-layer overtone via curmag_pre). Layer 1 = original.
- **Stage 5 FIX:** WT_XF and wt_xf are ONE EEL variable (case-insensitive): tables never rebuilt.
  Renamed WT_FADELEN/WT_TICKLEN; `engine_stress.py` exercises rebuilds (focus steps, overtone
  drift, high cut with pitch drift). CHECK EVERY NEW NAME FOR A CASE-ONLY TWIN.
- **Stage 7, DONE** (landed inside 4cb1a07): Auto-morph timing {Slot timings, Rate} + rate pair.
- **Stage 8, DONE:** 111 targets, stride 128, t111_remap for 7700008 saves, per-target units
  (units_seed), tg_glob, (all layers) entries with their own change memory (lay_dr_last -- ps_last
  is re-adopted by the slot block every pass). Every live copy through stages 1-8: wash
  bit-identical, voice -117 dB.
- **Stage 9, DONE:** auto-gain removed, WASH_GAIN +47 dB. `wash_gain_survey.py` measured every
  captured slot (scratchpad wash_gain.json; echoing infinity slot 3 needs +36 and is capped at +24,
  but that copy auditions Slot 2).
- **Stage 10:** `verify_live.py --out DIR --survey JSON` builds migrated copies (reseal through a
  throwaway plugin that adds the Output level offsets) and measures them; then
  `passage_migrate_takeover_20260916.py apply DIR`. Page updated (page_controls: 1 finding, the
  Auto-morph option spelling the Morpher's page shares).
- **Owed after install:** the Morpher -> Passage carry-over (`tools/morpher_to_passage.py`) must turn
  wash layer levels into what was heard (relative to Layer 1) and add the boost offsets.
