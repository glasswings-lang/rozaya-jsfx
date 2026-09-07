# Womb Sound Generator v3 — authored layout

Written by hand 2026-09-06, not generated. **Authored BEFORE anything is built or
migrated**, per the standing rule: one migration per plugin, not one per idea.

**Status: AUTHORED, NOT BUILT.** Nothing in the source or in any project has been
touched. This document is the thing to argue with; the code comes after.

**Scale.** 9 instances across 9 projects — the smallest migration in the sweep so
far, and the only one where **two instances are actually in host-sync mode**
(`scattered.rpp`, `womb-and-baby-heartbeats-with-bloodflow.RPP`). That path is
live, not theoretical, and it is the part of this that can go wrong quietly.

## Where this came from

Rozaya asked for Womb next, "because I have concerns about it anyway". The
concerns turned out to be the design, and they are load-bearing enough that they
are recorded here in their own words rather than paraphrased into requirements.

**On collapsing controls:** *"My concern is that in collapsing a bunch of shit, we
lose the finer control that made these things stand out... if I set breath values
to four and zero and eight and zero and switch everything to beats, I right now
can trust that it goes in for four beats, out for eight beats."*

That is not hypothetical. `scattered.rpp` is set exactly that way right now —
host mode, inhale 4, exhale 8. **Any layout that costs her that is wrong**, and
this one does not: the four breath sliders survive untouched and gain a rate mode
that is theirs alone.

**On the one-entry sync picker:** *"The thing that only has heartbeat right now,
is because we were going to put in breath and some other things to go alongside
it."* So `Host sync target` is a STUB, not debris — and this is the second time in
this plugin that a control which looked retired turned out to be half of a plan.
See *What retires* below, which does not skip the check a second time.

**On bloodflow:** *"Bloodflow is its own layer, but has no surfaced controls to
regulate its own rhythm relative to heart."* Correct, and see below — this was
flagged and parked in June with an explicit condition for reopening, and the
condition is now met.

**On the unit for that:** *"It would be nice to be able to simulate something like
that by hand, using beats as the user-defined offset, which falls out of,
bloodflow in n beats/every n seconds/ whatever."* Which is the suite's existing
unit vocabulary, reached for unprompted. Taken exactly as offered.

## What is wrong with the layout today

- **The rate block is at the BOTTOM.** `Rate Mode` (62), `Host sync target` (63)
  and `Every N beats` (64) sit sixty places below `Heart rate` (1), the thing they
  govern. R20 says a rate carries its mode adjacent to it.
- **`Rate Mode` offers TWO options** — `{Own BPM, Host x}` — where every other
  plugin with a rate offers the canonical five. **`CLAUDE.md` claims R20/R21 is
  "BUILT EVERYWHERE" and that is false; Womb is the exception and nobody noticed.**
  Fix the claim in the same commit as the build.
- **One mode governs two independent things.** Heart and breath share `Rate Mode`,
  so syncing the breath drags the heart along whether or not that was wanted.
- **Five controls are stranded at the end**, far from their groups: `Breath
  Post-filter Hz`/`Q` (39/40), `Breaths per minute` (53), `Heart with breath` (59),
  `Sigh interval`/`depth` (60/61).
- **Sliders 37 and 38 do not exist** — a hole left by an earlier change.
- **`Breaths per minute` REWRITES four other sliders** and calls
  `slider_automate` on each. See the next section; this is the forbidden pattern.
- **Womb owes the full six drift/ramp controls** — the last plugin group in the
  sweep besides the two Polyrhythms and Passage.

## The decision that matters most: what `Breaths per minute` IS

**Today it is a control whose job is to overwrite other controls.** `@slider`:

```
slider53 != last_bpm && slider53 > 0 ? (
  current_total_sec = slider16 + slider17 + slider18 + slider19;
  target_total_sec  = 60.0 / slider53;
  rescale_ratio     = target_total_sec / current_total_sec;
  slider16 *= rescale_ratio; slider_automate(slider16);   ... and 17, 18, 19
);
```

R20 forbids exactly this ("any control whose job is to write into another
control"), and it writes automation while doing it.

**It has never misfired, and the reason is a coincidence worth writing down.** In
all nine instances the four durations already sum to precisely what the BPM asks
for, so `rescale_ratio` is 1.0 and the multiply is a no-op:

| project | in | top | out | bottom | sum | BPM | 60/BPM |
|---|---|---|---|---|---|---|---|
| back-to-life | 4 | 0 | 8 | 0 | 12 | 5 | 12 |
| deep-night | 4 | 0 | 6 | 0 | 10 | 6 | 10 |
| womb-bubbles-proto | 4.8 | 0 | 7.2 | 0 | 12 | 5 | 12 |
| womb-and-baby | 1.860465 | 0.139535 | 1.860465 | 0.139535 | 4.0 | 15 | 4 |

**A latent hazard on a real project, though.** `slider_show(slider53, rate_mode
!= 1)` hides it in host mode, but the rescale block has **no matching gate** — and
`womb-and-baby-heartbeats-with-bloodflow.RPP` is in host mode holding a hidden
15. A hidden control that can still write is the 2026-08-23 bug shape verbatim.
If anything nudged it, it would rescale the four breath sliders with a SECONDS
formula while they are sitting in BEATS.

**The resolution, agreed with Rozaya 2026-09-06.** `Breaths per minute` becomes
the breath's actual rate, with its own mode beside it. The four sliders stop being
rewritten and are what she already treats them as: **the shape of the breath**,
whose proportions divide the cycle.

- Breath rate **off (0)** — cycle length is the sum of the four, exactly as today.
- Breath rate **set** — the cycle is that long and the four divide it in their
  stored proportions. Applied at DSP time, never written back.
- Mode **`Every N beats` = 12**, segments 4/0/8/0 — four beats in, eight out.
  **Her stated case, preserved to the number.**

Nothing she has typed moves, and no control writes into another.

## What retires, and what was inside it first

**The rule this plugin already taught us once** (the 2026-09-04 near-miss, in
`CLAUDE.md`): open the control and ask what else is in it before retiring it. Done,
by reading and by asking the person who wanted it.

- **`Rate Mode` (62) `{Own BPM, Host x}`** — does not retire. It BECOMES `Heart
  rate mode` and gains the canonical five options.
- **`Every N beats (Host x)` (64)** — retires as a slider, survives as a MEANING.
  Under R20 the rate VALUE carries the beat count when the mode says `Every N
  beats`, so its number moves into `Heart rate`. This is the same conversion
  `tools/melody_migrate_r20.py` already performed; it is not new ground.
- **`Host sync target` (63)** — retires. It declares `<0,0,1{Heart rate}>`: one
  option, nothing selectable. **Rozaya confirmed what was inside it: a plan to add
  breath and others.** The two-pair layout delivers that plan and more — breath can
  now be synced while the heart runs free, which a shared picker could never
  express. It indexes `host_beats_mem`, which has exactly one live slot.

**Nothing else is retired.** `Heart with breath`, the sigh pair and the breath
post-filter all MOVE; none is dropped.

## New controls

| control | options / range | default | why that default |
|---|---|---|---|
| `Heart rate mode` | `{BPM, Seconds, Hz, Every N beats, N per beat}` | BPM (0) | What every non-host instance means today |
| `Breath rate mode` | same five | BPM (0) | Same |
| `Bloodflow offset` | `-1000..1000, 0.001` | **0** | Zero is today's behaviour exactly — bloodflow welded to the heart |
| `Bloodflow offset unit` | `{Cycles, Seconds, Beats}` | Cycles (0) | Rozaya's own framing; and at offset 0 the unit cannot matter, so the default is free |
| `Drift period unit` | `{Cycles, Seconds, Beats}` | **Cycles (0)** | The period already counts heartbeats or breath cycles — Cycles IS the current meaning |
| `Drift play for` / `Drift rest for` | `0..1000, 0.01` | 0 (off) | Off |
| `Ramp time unit` | `{Cycles, Seconds, Minutes, Beats}` | **Minutes (2)** | Ramp duration and start delay already read in minutes |
| `Ramp play for` / `Ramp rest for` | `0..1000, 0.01` | 0 (smooth) | Off |

**Womb's `Drift period unit` DOES default to Cycles**, unlike the Morpher's. The
period is already documented as "heartbeats or breath cycles", so Cycles preserves
the meaning rather than changing it. Same rule, opposite answer, because the
plugin's prior meaning was different — that is the rule working, not an exception
to it.

### Bloodflow offset, in more detail

`bf_cycle_pos = hb_phase / max(cycle_len, 1)` is the whole of bloodflow's timing:
it reads the heart's phase directly and has no counter of its own. The offset adds
to that position and wraps, so it needs **no new phase counter and no new bank** —
which is what makes it cheap enough to do now.

- **Cycles** — a fraction of a heartbeat. 0.25 sits a quarter of the way round, and
  scales automatically as the heart rate changes.
- **Seconds** — fixed wall-clock, which is what real pulse transit time is
  (roughly 0.1–0.25 s from heart to periphery).
- **Beats** — the project tempo.

An offset longer than one cycle wraps into the next, which is meaningful rather
than an error: the flow you hear belongs to the previous beat.

**Deliberately NOT built: bloodflow on its own separate clock.** The June note
priced it (own phase counter, own rate, own drift and ramp entries) and Rozaya
agreed to hear the offset first. Once the flow is unwelded from the thump, the
remaining stiffness — if any — will say whether the problem is *when it arrives*
or *that it never breathes independently*, and those want different fixes.

## The order

69 sliders, up from 64 declared. Grouped by layer, each group in the canonical
reading order — what it is, its rate (value then mode), the shape of its movement,
its filtering, its stereo, its level, its solo.

### Heartbeat

| new | control | from |
|---|---|---|
| 1 | Heart rate | 1 |
| 2 | Heart rate mode | 62, gaining three options |
| 3 | Heart with breath (BPM peak-to-peak) | 59 — a modifier of the rate, so it sits with it |
| 4 | Systole | 5 |
| 5 | S1 Frequency Hz | 11 |
| 6 | S1 Decay ms | 9 |
| 7 | S1 Volume | 6 |
| 8 | S2 Frequency Hz | 12 |
| 9 | S2 Decay ms | 10 |
| 10 | S2 Volume | 7 |
| 11 | Brightness | 8 |
| 12 | HB Stereo width ms | 13 |
| 13 | HB Master volume | 3 |
| 14 | Heartbeat solo | 4 |

S1 and S2 are interleaved by SOUND rather than by parameter: frequency, decay and
volume for the first beat, then the same three for the second. Today the six are
split across three separated pairs (6/7, 9/10, 11/12), so tuning one beat means
visiting three places.

### Breath

| new | control | from |
|---|---|---|
| 15 | Breaths per minute | 53, no longer rewriting anything |
| 16 | Breath rate mode | NEW |
| 17 | Inhale | 16 |
| 18 | Top pause | 17 |
| 19 | Exhale | 18 |
| 20 | Bottom pause | 19 |
| 21 | Inhale Frequency Hz | 20 |
| 22 | Exhale Frequency Hz | 21 |
| 23 | Inhale Fade In | 23 |
| 24 | Inhale Fade Out | 24 |
| 25 | Exhale Fade In | 25 |
| 26 | Exhale Fade Out | 26 |
| 27 | Fade Mode | 27 |
| 28 | Breath High-pass Hz | 22 |
| 29 | Breath Post-filter Hz | 39 |
| 30 | Breath Post-filter Q | 40 |
| 31 | Sigh interval | 60 |
| 32 | Sigh depth multiplier | 61 |
| 33 | Breath Stereo width | 28 |
| 34 | Breath Volume | 14 |
| 35 | Breath Solo | 15 |

### Bloodflow

| new | control | from |
|---|---|---|
| 36 | Bloodflow offset | NEW |
| 37 | Bloodflow offset unit | NEW |
| 38 | Bloodflow Attack (proportion of cycle) | 34 |
| 39 | Bloodflow Decay (proportion of cycle) | 35 |
| 40 | Bloodflow Dicrotic Level | 32 |
| 41 | Bloodflow Filter Hz | 31 |
| 42 | Bloodflow Resonance | 33 |
| 43 | Bloodflow Stereo width | 36 |
| 44 | Bloodflow Volume | 29 |
| 45 | Bloodflow Solo | 30 |

Bloodflow has no rate of its own, so the offset takes the rate's place at the head
of the group: it is the control that says how this layer sits in time.

### Master and transport

| new | control | from |
|---|---|---|
| 46 | Master stereo flip | 2 |
| 47 | Start delay | 41 |
| 48 | HB: Play for | 42 |
| 49 | HB: Rest for | 43 |
| 50 | Breath: Play for | 44 |
| 51 | Breath: Rest for | 45 |
| 52 | Bloodflow: Play for | 46 |
| 53 | Bloodflow: Rest for | 47 |

### Drift

| new | control | from |
|---|---|---|
| 54 | Drift target | 54 |
| 55 | Drift up amount | 55 |
| 56 | Drift down amount | 56 |
| 57 | Drift period | 57 |
| 58 | Drift period unit | NEW |
| 59 | Drift shape | 58 |
| 60 | Drift play for | NEW |
| 61 | Drift rest for | NEW |

### Ramp

| new | control | from |
|---|---|---|
| 62 | Ramp target | 48 |
| 63 | Ramp by | 49 |
| 64 | Ramp time unit | NEW |
| 65 | Ramp duration | 50 |
| 66 | Ramp play for | NEW |
| 67 | Ramp rest for | NEW |
| 68 | Ramp engage | 51 |
| 69 | Ramp start delay | 52 |

**Sliders 37 and 38 were a hole and are not any more** — the numbering is
contiguous 1..69 after this.

## Migration notes

**This plugin crosses the 64-slider boundary**, from 64 declared to 69. A REAPER
value line with more than 64 sliders carries a quoted `""` marker **at token index
64**, so the token index of slider N is `N-1` up to 64 and `N` beyond it. Every
Womb instance today sits at exactly 64 — the boundary — and three carry a real
value at slider 63 or 64. `tools/rpp_sliders.py` handles the marker and
round-trips all 377 value lines in the library byte-identically; **the migration
must use it and must not re-derive the format.** This is the trap that broke five
Melody projects on 2026-09-02.

**The R20 conversion, for the two host-mode instances.** Under R20 the rate VALUE
carries the beat count, so for any instance with `Rate Mode = 1 (Host x)`:

- `Heart rate` ← the stored `Every N beats` (slider 64), or **1** where it is
  absent, since 1 is that slider's declared default and a declared default is a
  live value;
- `Heart rate mode` ← **3** (`Every N beats`);
- `Breath rate mode` ← **3** as well, because one mode used to govern both and the
  breath segments were reading as beats.

| project | mode | heart rate | Every N beats | becomes |
|---|---|---|---|---|
| `scattered.rpp` | 1 | 35 (a readout) | 2 | Heart rate **2**, mode `Every N beats`, breath mode `Every N beats` |
| `womb-and-baby...` | 1 | 1 | absent → 1 | Heart rate **1**, mode `Every N beats`, breath mode `Every N beats` |

The stored `Heart rate` in host mode is a DERIVED READOUT, not a setting — 35 BPM
is what 2 beats per heartbeat comes to at that project's tempo. Carrying it across
as a BPM would be wrong twice over. **This is the single most dangerous step in the
migration and it affects two instances**, both of which should be listened to
specifically.

For the seven instances NOT in host mode, `Heart rate mode` takes its declared
default of BPM (0) and the value is already in BPM. Nothing to convert.

**The `Breaths per minute` change needs no value migration.** Every instance's four
durations already sum to what its BPM asks for (the table above), so the stored
numbers are already consistent with the new reading. This is luck, and it is worth
asserting in the migration rather than trusting.

**Blob magic.** Womb's `@serialize` gains no new bank — every new control is a
plain global slider. Bump the magic anyway, in the same commit, because a slider
layout moved and the blob's leading float is the only independent witness of which
layout an instance was saved on.

**Drift and Ramp target lists are APPEND-ONLY.** The index is stored in the
project AND is the bank position. `Bloodflow offset` may be appended to both; no
existing entry may move.

## What to check before believing any of this shipped

- **Simulate the rate chain in all five modes**, both pairs, at several tempos —
  the R21 reciprocal shipped inverted in two plugins because the chain fell
  through to the wrong host arm, and Womb has never had either host option before.
- **Simulate the breath cycle** with the rate off and set, and assert 4/0/8/0 at
  `Every 12 beats` gives four beats in and eight out. That is Rozaya's stated case
  and it is the acceptance test.
- **Simulate the bloodflow offset** at 0 and confirm the output is bit-identical to
  today. Offset 0 must be exactly the current sound, not approximately.
- **Verify the migration BY CONTROL NAME** against a pre-migration snapshot, never
  against the table the migration used, with an authored rename table for any
  control whose label changed.
- **Range-check every migrated value**, separating "was already out of range" from
  "is out of range now".
- **Fix `CLAUDE.md`'s "R20/R21 built everywhere" claim** in the same commit.

## Open, and needing Rozaya rather than me

1. **Does `Heart rate` want `Seconds` and `Hz` at all?** The canonical five are the
   suite standard and consistency is the whole point, but "a heartbeat every 0.857
   seconds" is a stranger thing to reach for than the same idea in BPM. The
   recommendation is to ship all five anyway — an unused option costs nothing, and
   a missing one makes this plugin the odd one out again, which is what we are
   fixing.
2. **`Systole` reads "ms / beats in Host x".** With the heart owning its own mode
   this still works, but it is the same implicit-unit shape the Morpher just
   replaced with an explicit control. Left alone here on purpose — it is not what
   this job is for, and it should be a suite-wide decision about durations rather
   than a Womb-only one.
