# Sweep Dwell Filter — its whole turn, authored 2026-09-17

Rozaya opened it in REAPER, checked every item on its backlog against the plugin, and said
*"I think, because I just had it open and can verify that every single one of those is accurate,
I'm gonna say, just go for it."* So this is the WHOLE list in one layout and one migration.

Saved copies: 2 (`E:/reaper/to-play-with-later/surges.RPP`, `E:/reaper/finished/test-projects/
claude-testing001.RPP`). Both have pan off, Start delay 0, Play/Rest 0, Resonance 0.000.

## What it gains

1. **Per target:** `Drift period unit`, `Ramp time unit` (the `(all targets)` mark comes off both),
   plus `Drift amount unit` / `Ramp by unit` (the 13-entry list Veil and Passage have).
2. **`Drift movement mode`** {With the target, On a clock}, per target (R23), and **`Drift rest mode`
   / `Ramp rest mode`** {Walk through, Freeze in place} — it had freeze-in-place behaviour with no switch.
3. **`Play for` and `Rest for` as drift and ramp targets** (R24). They sit after `Wet/dry mix` in
   control order, so they APPEND as targets 16 and 17: no saved target selection renumbers.
4. **One `Transport unit`** {Cycles, Seconds, Beats} for Start delay, Play for and Rest for, replacing
   `Start delay mode`. Default Cycles, which is what Play for and Rest for have always counted.
5. **Every unit switch keeps the thing and converts the number** (as Passage got 2026-09-16):
   Segment length mode, Segment pitch mode and fine tune unit, Pan sweep rate mode, Transport unit,
   Drift period unit, Ramp time unit. Cycles is not a fixed length, so to or from Cycles the number stays.
6. **The note name works in every pitch unit, both ways.** Today `Segment note name` only appears on
   Semitones.
7. **No control counts in fractions (R9):** `Resonance`, `Pan spread` and `Wet/dry mix` become percents,
   0..100. Drift and ramp amounts aimed at those three scale by 100 in the migration.
8. **The pan block:** one shared order, `(Flipped)` choices retired into a `Pan direction` switch,
   and the two choices this plugin is owed — `Accent L / Weak R` (Rhythm Track's) and `Sway`.
9. **`Pan sweep every (cycles)` gains a mode**, {Every N cycles, N per cycle}, so a pan pass faster than
   one dwell cycle is a whole number instead of 0.25.
10. **`LFO at rest` becomes `Rest mode (LFO)`.** Rozaya: *"rest mode (for LFO) seems like it'd be
    clearer for the ones called the other thing."* It freezes the LFOs only, so the name stays true.
11. The page is rewritten from the plugin (10 findings today).

Nothing else moves. Rozaya, 2026-09-16: *"it can stay. stay as it is, ffs I didn't mean everything to
be shuffled around in everything I ever use"* — so units stay under the numbers they set, the pan
rate keeps value-then-mode, and no control moves except where this list says.

## The order, in full (new or changed marked)

```
 1 Segment
 2 Segment length mode
 3 Segment length
 4 Segment fade shape
 5 Segment pitch mode
 6 Segment note name                     CHANGED: shown in every pitch unit
 7 Segment frequency (Hz / semitones / cents)
 8 Segment fine tune
 9 Segment fine tune unit
10 Tuning reference (Hz)
11 Resonance (%)                         CHANGED: 0..100, was 0..1
12 Slope (dB/oct)
13 Stereo phase offset (degrees)
14 Phase mode
15 Pan enabled
16 Pan mode                              CHANGED: the shared order, below
17 Pan direction {Normal, Flipped}       NEW
18 Pan spread (%)                        CHANGED: 0..100, was 0..1
19 Pan glide (ms, 0 = instant)
20 Cycle steps (per-cycle modes)
21 Pan sweep rate
22 Pan sweep rate mode
23 Pan sweep every mode {Every N cycles, N per cycle}   NEW
24 Pan sweep every (in its own mode)     CHANGED name
25 Wet/dry mix (%)                       CHANGED: 0..100, was 0..1
26 Transport unit {Cycles, Seconds, Beats}   NEW (replaces Start delay mode)
27 Start delay (in transport units)
28 Play for (in transport units, 0 = always)
29 Rest for (in transport units, 0 = always)
30 Rest mode (LFO)                       RENAMED from LFO at rest
31 Output at rest
32 Drift target                          CHANGED: 18 targets (Play for, Rest for appended)
33 Drift up amount (in the Drift amount unit)
34 Drift down amount (in the Drift amount unit)
35 Drift amount unit                     NEW, per target
36 Drift period (0 = off)
37 Drift period unit                     CHANGED: per target
38 Drift movement mode                   NEW, per target
39 Drift shape
40 Drift play for (periods, 0 = always)
41 Drift rest for (periods, 0 = always)
42 Drift rest mode                       NEW, per target
43 Ramp target                           CHANGED: 18 targets
44 Ramp by (in the Ramp by unit)
45 Ramp by unit                          NEW, per target
46 Ramp time unit                        CHANGED: per target
47 Ramp duration (in ramp time units)
48 Ramp play for (0 = smooth)
49 Ramp rest for (0 = smooth)
50 Ramp rest mode                        NEW, per target
51 Ramp engage (all targets)
52 Ramp start delay (in ramp time units)
```

## Pan mode: the list and the map

New: `Mono, Alternating, Alternating every 2, Alternating every 4, Alternating every 8,
Accent L / Weak R, Distributed, Distributed (Ping-pong), Converging, Converging (Ping-pong),
Diverging, Diverging (Ping-pong), Linked Sweep, Sway, Pan Sweep`.

Old -> new (`+F` means Pan direction becomes Flipped):

```
0 Mono                  -> 0        8  Diverging            -> 10
1 Alternating           -> 1        9  Diverging (Ping-pong)-> 11
2 Alternating (Flipped) -> 1 +F     10 Pan Sweep            -> 14
3 Distributed           -> 6        11 Pan Sweep (Flipped)  -> 14 +F
4 Distributed (Flipped) -> 6 +F     12 Linked Sweep         -> 12
5 Distributed (Ping-pong)-> 7       13 Alternating every 2  -> 2
6 Converging            -> 8        14 Alternating every 4  -> 3
7 Converging (Ping-pong)-> 9        15 Alternating every 8  -> 4
```

`Accent L / Weak R`: Rhythm Track's — one side full, the other at `Pan spread` of it, alternating
per cycle. `Sway`: a smooth (sine) swing at `Pan sweep rate`, where `Pan Sweep` is a ramp; R19 keeps
Sway for the plugins with no Increment.

## The migration (`tools/sdf_migrate_r26r27_20260917.py`)

Blob magic 2500016 -> 2600018. Every saved copy is rewritten: nothing reads an old blob.

- **Slider line:** old 1..45 -> new per the order above (16 -> 16 remapped, 17 new, old 17..23 -> 18..25,
  old 24 `Start delay mode` -> new 26 `Transport unit` converted, old 25..29 -> 27..31, old 30..37 ->
  32..42 with the new pickers filled, old 38..45 -> 43..52).
- **Values:** Resonance, Pan spread and Wet/dry x100. Drift up/down and Ramp by for targets 9, 11 and
  15 x100. Pan mode and direction per the map.
- **Transport unit:** Start delay 0 and Play/Rest 0 -> Cycles, everything 0 (both saved copies).
  Start delay > 0 with Play/Rest 0 -> Seconds, Start delay converted from its old rate mode. Both
  non-zero -> Seconds, Play/Rest converted from cycles using the SAVED cycle length (the four segment
  lengths in seconds); the cycle is what they counted, so this keeps the time they meant.
- **Banks:** the new per-target banks are seeded from the one shared value each project holds
  (period unit, ramp time unit), the amount units to `Target default`, movement mode to each target's
  default, and both rest modes to Freeze in place — which is what the plugin does today.

## Checks before installing

- `tools/sweep_dwell_checks/unit_switches.py` — every unit switch converts, every selector switch does not.
- `tools/sweep_dwell_checks/verify_live.py` — both saved copies, old build against new: with nothing
  drifting and pan off, bit-identical; each new control measured to do something.
- `tools/page_controls.py` — 0 findings for this plugin afterwards.
