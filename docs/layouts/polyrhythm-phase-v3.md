# Polyrhythm Phase v3 — authored layout

Written by hand 2026-09-06, not generated. **Authored BEFORE anything is built or
migrated.**

**Status: AUTHORED, NOT BUILT.**

**Scale.** v3 has **8 instances across 5 projects** — a small, low-risk migration.
v1 has **84 instances across 17 projects** and is NOT touched by this job.

## Why this, and why now

Rozaya, asked what actually bothers her about the plugin in use: *"I haven't
touched polyrhythm since every n beats and n per beat got introduced and then I
stumbled on them... So in practice, the thing that bugs me most is that the orders
are scattered as shit."*

**So the scattering IS the brief.** There is no hunt for usability bugs here the
way there was on Womb, because she has not been able to use it.

## And v1 is deliberately left alone

Decided 2026-09-06: *"The polyrhythm can just... be left. If we do v3 and then
migrate it'll be fine."* So v1 gets **no** drift/ramp controls and **no** reorder.
v3 gets its layout, and afterwards v1's 84 instances cross to v3 once and v1
retires. **Do not migrate those 84 twice.**

## What is wrong today

- **Two pan controls are stranded sixty places from the pan block.** `Pan Glide ms`
  (89) and `Cycle Steps` (90) are both pan controls — each is `slider_show`n only
  when pan is enabled — and both were appended rather than placed.
- **The pan has a RATE but no MODE.** `Pan Base Rate` (23) sits with nothing saying
  what unit it is in, so it cannot follow the project independently of the main
  rate. R20/R21: *a plugin with two rates has two complete pairs; the pan gets its
  OWN mode and never borrows the main one.* **Melody Phase has one; neither
  Polyrhythm does.** `CLAUDE.md` said R21 landed everywhere. That is the THIRD such
  claim to fail a check today, after Womb's rate block and the Morpher's reciprocal.
- **Slider 88 is a corpse.** The retired `Host ratio (writes Rate Value)` picker:
  its write block is `0 ? (...)`, it is `slider_show`n off, and nothing reads it.
  It is only still declared because ids can never be renumbered — and a reorder is
  exactly the moment that stops being true.
- **The rate value's label is stale.** `Rate Value (Drift only: BPM / sec / Hz /
  beats per cycle)` names four units for a mode that has five, and predates
  `N per beat`.
- **Womb owed the six drift/ramp controls and so does this.** It is the last of the
  three (with Passage) still owing them.
- **The tremolo's shape is interleaved oddly** — On Duration, Attack %, Release %,
  Attack Shape, Release Shape, Depth. Each shape sits two places from the amount it
  shapes.

## New controls

| control | options / range | default | why |
|---|---|---|---|
| `Pan rate mode` | `{BPM, Seconds, Hz, Every N beats, N per beat}` | BPM (0) | The pan's rate needs its own mode; this is the R21 gap |
| `Drift period unit` | `{Cycles, Seconds, Beats}` | **Cycles (0)** | The period already counts CYCLES here, so Cycles is both the suite default and the back-compatible one |
| `Drift play for` / `Drift rest for` | `0..1000, 0.01` | 0 (off) | Off |
| `Ramp time unit` | `{Cycles, Seconds, Minutes, Beats}` | **Minutes (2)** | Ramp duration and start delay already read in minutes |
| `Ramp play for` / `Ramp rest for` | `0..1000, 0.01` | 0 (smooth) | Off |

**No control changes what it MEANS.** Every one of the 89 survivors keeps its units
and its range; this is a move, plus seven additions that default to off or to what
the plugin already did. That is what makes it a low-risk migration despite touching
almost every slider.

## The order

96 sliders, up from 90 declared. Each group reads the same way — what it is, how
fast it goes (value then mode), the shape of its movement, then level, then on/off.

**The eight voice blocks are grouped BY VOICE, not by parameter**, and each reads
in that same order: its note, its detune, its own rate, its phase, its level, its
on/off. You tune one voice at a time, so one voice's six controls belong together.
That is 48 of the 96, and it is the reason the rest has to be tight.

| new | control | from |
|---|---|---|
| 1 | Tremolo Mode | 1 |
| 2 | Rate Value | 3 |
| 3 | Rate Mode | 2 |
| 4 | Depth dB | 10 |
| 5 | On Duration % of Cycle | 5 |
| 6 | Attack % of Cycle | 6 |
| 7 | Attack Shape | 8 |
| 8 | Release % of Cycle | 7 |
| 9 | Release Shape | 9 |
| 10 | Tuning Reference Hz | 11 |
| 11 | Transpose (half steps) | 12 |
| 12 | Octave shift | 13 |
| 13 | Binaural Beat Hz (L/R offset) | 4 |
| 14 | Waveform | 14 |
| 15 | Pulse Width % (50 = square) | 15 |
| 16 | Tone (Warm <-> Bright) | 16 |
| 17 | Edge | 17 |
| 18 | Movement | 18 |
| 19 | Body | 19 |
| 20 | V1 Note | 26 |
| 21 | V1 Fine tune (cents) | 27 |
| 22 | V1 Drift / Rate | 28 |
| 23 | V1 Phase Offset | 29 |
| 24 | V1 Gain dB | 25 |
| 25 | V1 Active (Off = no CPU cost) | 30 |
| 26 | V2 Note | 32 |
| 27 | V2 Fine tune (cents) | 33 |
| 28 | V2 Drift / Rate | 34 |
| 29 | V2 Phase Offset | 35 |
| 30 | V2 Gain dB | 31 |
| 31 | V2 Active (Off = no CPU cost) | 36 |
| 32 | V3 Note | 38 |
| 33 | V3 Fine tune (cents) | 39 |
| 34 | V3 Drift / Rate | 40 |
| 35 | V3 Phase Offset | 41 |
| 36 | V3 Gain dB | 37 |
| 37 | V3 Active (Off = no CPU cost) | 42 |
| 38 | V4 Note | 44 |
| 39 | V4 Fine tune (cents) | 45 |
| 40 | V4 Drift / Rate | 46 |
| 41 | V4 Phase Offset | 47 |
| 42 | V4 Gain dB | 43 |
| 43 | V4 Active (Off = no CPU cost) | 48 |
| 44 | V5 Note | 50 |
| 45 | V5 Fine tune (cents) | 51 |
| 46 | V5 Drift / Rate | 52 |
| 47 | V5 Phase Offset | 53 |
| 48 | V5 Gain dB | 49 |
| 49 | V5 Active (Off = no CPU cost) | 54 |
| 50 | V6 Note | 56 |
| 51 | V6 Fine tune (cents) | 57 |
| 52 | V6 Drift / Rate | 58 |
| 53 | V6 Phase Offset | 59 |
| 54 | V6 Gain dB | 55 |
| 55 | V6 Active (Off = no CPU cost) | 60 |
| 56 | V7 Note | 62 |
| 57 | V7 Fine tune (cents) | 63 |
| 58 | V7 Drift / Rate | 64 |
| 59 | V7 Phase Offset | 65 |
| 60 | V7 Gain dB | 61 |
| 61 | V7 Active (Off = no CPU cost) | 66 |
| 62 | V8 Note | 68 |
| 63 | V8 Fine tune (cents) | 69 |
| 64 | V8 Drift / Rate | 70 |
| 65 | V8 Phase Offset | 71 |
| 66 | V8 Gain dB | 67 |
| 67 | V8 Active (Off = no CPU cost) | 72 |
| 68 | Pan Enabled | 20 |
| 69 | Pan Mode | 21 |
| 70 | Pan Spread % | 22 |
| 71 | Pan Base Rate | 23 |
| 72 | Pan rate mode | NEW |
| 73 | Pan Increment per Voice | 24 |
| 74 | Cycle Steps (per-cycle modes) | 90 |
| 75 | Pan Glide ms (0=instant) | 89 |
| 76 | Direction & Reverse | 73 |
| 77 | Reverse Drift Offset | 74 |
| 78 | Start delay (in rate mode units) | 75 |
| 79 | Play for (cycles) | 76 |
| 80 | Rest for (cycles) | 77 |
| 81 | Drift target | 78 |
| 82 | Drift up amount | 79 |
| 83 | Drift down amount | 80 |
| 84 | Drift period | 81 |
| 85 | Drift period unit | NEW |
| 86 | Drift shape | 82 |
| 87 | Drift play for | NEW |
| 88 | Drift rest for | NEW |
| 89 | Ramp target | 83 |
| 90 | Ramp by | 84 |
| 91 | Ramp time unit | NEW |
| 92 | Ramp duration | 85 |
| 93 | Ramp play for | NEW |
| 94 | Ramp rest for | NEW |
| 95 | Ramp engage | 86 |
| 96 | Ramp start delay | 87 |

Only **slider 88** is dropped, and it is already dead code.

## Migration notes

**Both ends are over 64 sliders**, so every value line carries a quoted `""` marker
at token index 64 and the token index of slider N is `N-1` up to 64 and `N` beyond.
`tools/rpp_sliders.py` handles it and must not be re-derived — this is the trap
that broke five Melody Phase projects on 2026-09-02.

**`@serialize` gains no bank** — all seven new controls are plain global sliders
except the four per-target ones, which DO need banks:

- `Drift play for` / `Drift rest for` and `Ramp play for` / `Ramp rest for` are
  per-target, like every other drift and ramp config here. Four new banks, APPENDED
  to the stream so an older blob simply runs out and leaves them at their `@init`
  zeroes — which is "no staircase", the correct reading for a project that never
  had one. **Assert they appear in BOTH the file_mem list and the duplicate-fix
  block**; a bank added to one and not the other is how Heartbeat nearly shipped
  settings that vanished on save.

**Bump the blob magic** in the same commit. No format change is needed for the
plain sliders, but a slider layout moved, and the blob's leading float is the only
independent witness of which layout an instance was saved on.

**The Drift and Ramp target lists are APPEND-ONLY** and are not touched by this
job: their indices are stored in projects AND are bank positions.

## What to check before believing it shipped

- **Simulate the pan rate in all five modes**, at several tempos, with the two host
  modes asserted RECIPROCAL. This plugin has never had a pan mode before, and the
  R21 reciprocal shipped inverted in two plugins precisely because a new mode was
  wired and never asked what it DID.
- **Verify the migration BY CONTROL NAME** against a pre-migration snapshot, never
  against the table the migration used, with an authored rename table for the one
  label that changes (`Rate Value`).
- **Range-check every migrated value**, separating "was already out of range" from
  "is out of range now".
- **Fix `CLAUDE.md`'s R21 claim** in the same commit, and say plainly that the pan
  modes did NOT land everywhere.

## Open, and needing Rozaya rather than me

1. **Nothing blocking.** The layout above is a pure rearrangement plus seven
   off-by-default additions, so it can be built and heard without any further
   decision. The one judgement call already made is grouping the voices by voice
   rather than by parameter, which is how they are today.
