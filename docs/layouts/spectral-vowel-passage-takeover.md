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
