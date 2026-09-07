# Womb Sound Generator v3 — authored layout

Written by hand 2026-09-06, not generated. **Authored BEFORE anything is built or
migrated**, per the standing rule: one migration per plugin, not one per idea.

**Status: BUILT, MIGRATED and HEARD 2026-09-06.** 9 instances across 9 projects,
64 sliders to 70, verified by behaviour and then confirmed by ear -- Rozaya:
*"Everything else, though, passes. :)"* The one thing that did NOT pass is the
breath, and it has its own section at the end of this document.

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
- **`Systole` silently changes unit** — milliseconds normally, BEATS under sync,
  with nothing on the control saying so. Nothing has been broken by it, but it is
  one load-time migration away from breaking, and that migration is being removed
  by this very job. See the section below.
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

## Systole, and a claim I got wrong

**First, the correction, because a wrong finding is worse than none.** This
document said `womb-and-baby-heartbeats-with-bloodflow.RPP` was broken — that its
Systole of 180, meant as milliseconds, was being read as 180 BEATS, giving a
heartbeat with no second sound. **That is wrong.** The stored value and the read
path were both read correctly; the LOAD path was not read at all.

That project carries an old-format blob (magic 2100010), which sets
`host_beats_seed_pending`, and the seeding block in `@block` — gated on
`slider2 == 1`, so it fires for that instance and no other — converts on open:
`slider4 * (tempo/60) * 0.001` turns 180 into 0.21 beats, which at its tempo of 70
is 0.18 s. **180 ms, exactly as intended. S2 fires. The project is fine.**

The rule that should have caught this is already written down: *a plausible
mechanism is not a finding — mark it proved / predicted / untested*, and *what else
produces exactly this symptom?* The arithmetic was right and the question was
wrong, which is the same shape as the 2026-09-06 Start delay case.

**What is still true, and is still worth fixing.** `Systole (ms / beats in Host x)`
is read at line 665 as `srate * slider4 * (rate_mode == 1 ? 60/tempo : 0.001)`: the
same number means milliseconds in one mode and beats in the other, with nothing on
the control saying so. The by-hand conversion only runs in the
`last_rate_mode != rate_mode` branch, so any other route into host mode leaves the
value in the old unit. Today that hole is plugged for exactly one instance by a
blob-version migration that this job removes — so the danger is real and this build
is what would create it.

**The fix, unchanged.** `Systole` gains `Systole unit`, declared Milliseconds, at
position 5 directly after it, and the flip-conversion goes. **Rozaya asked for the
full list rather than a cut-down one** — a stunted option list is the exact thing
this job is fixing in `Rate Mode`, so the gap does not get one either. The fourth
option is `% of heartbeat` and is deliberately NOT called `Cycles`: everywhere else
in the suite Cycles COUNTS whole cycles, and systole is always a fraction of one,
so the same word would mean two different things inside one plugin. (Rozaya caught
this: *"cycles in fractions? I thought cycles were cycles lol"* — right, and it was
named wrong for an hour.) The name it takes instead is the idiom already next door
here, where Bloodflow Attack and Decay are proportions of a cycle. It earns its
place: systole shortens as the heart speeds up, so a percentage is the
physiologically right reading and the only unit here that tracks the rate instead
of fighting it.

**A clamp goes in regardless of units.** `systole_samples` is never held below
`cycle_len`, and S2 fires on an exact equality with `hb_phase`, which wraps at
`cycle_len`. So a systole longer than the beat silences S2 completely rather than
sounding wrong. Nothing reaches that state today; the clamp is what makes sure
nothing can.

## The blob reality, measured — and it changes the migration

Read from the nine projects rather than assumed. Every value line has exactly 64
tokens; the `@serialize` blobs are three different vintages:

| blob | instances | what it means |
|---|---|---|
| **2100010** | **6** | The OLDEST versioned format. Drift and ramp banks restore; sets `host_beats_seed_pending` and `host_bpm_migration_pending`. |
| unversioned (leading float 5, 148 bytes) | 2 | Matches no magic, so the whole block is skipped — drift and ramp fall through to `@init` defaults, and no seeding runs. |
| **2300010** | **1** | Current. `scattered.rpp`. |

**Six of nine are on the oldest format, and that path is load-bearing.** Three
things follow, none of which the first draft of this document accounted for:

1. **The old-blob seeding path cannot simply be deleted.** It is gated on host
   mode, so today it fires only for `womb-and-baby...`, and it is what makes that
   instance correct. It must be REWRITTEN to write the new controls, not removed.
   Deleting it is precisely how this job would create the breakage it was written
   to prevent.
2. **`N_TARGETS` goes 10 → 11** (appending `Bloodflow offset` to the drift and ramp
   target lists), which changes every bank's width in the stream. Old blobs must be
   read at the OLD width or the stream desyncs and every later bank is garbage. The
   Morpher's `n_ser_targets` pattern is the precedent:
   `n_ser = magic == NEW ? N_TARGETS : 10`.
3. **The two unversioned instances have no drift or ramp state to preserve** —
   they already fall through to defaults on every load, so nothing is lost by the
   change. Worth asserting rather than assuming when the migration runs.

**The migration must therefore reproduce what a LOAD produces, not what the file
stores.** For the one host-mode instance with an old blob, the stored breath
segments are seconds and become beats on open; the stored Systole is milliseconds
and becomes beats on open; the stored Heart rate is a multiplier and becomes BPM on
open. Migrating the stored numbers as if they were the live ones would be wrong on
all three. This is the single most dangerous part of the job and it is worth its
own verifier.
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
| `Bloodflow offset unit` | `{Milliseconds, Seconds, Beats, % of heartbeat}` | **% of heartbeat (3)** | Same list as Systole. `Cycles` was tried and was WRONG -- see below |
| `Systole unit` | `{Milliseconds, Seconds, Beats, % of heartbeat}` | **Milliseconds (0)** | What every non-host instance means today, and what the broken host one MEANT |
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

- **% of heartbeat** — 25 puts the flow a quarter of a beat behind the thump, and
  it scales automatically as the heart rate changes.
- **Milliseconds** — the physiologically real one; pulse transit is roughly
  100–250 ms from heart to periphery.
- **Seconds**, **Beats** — fixed wall clock, and the project tempo.

**This said `Cycles` for one hour and it made the whole control look broken.** The
offset WRAPS into a single heartbeat, so in cycles every whole number — 1, 2, 5,
10 — is bit-identical to 0, and only fractions do anything. Rozaya turned the
control on, moved it to a round number and correctly heard nothing.

It is the identical error she had already caught on Systole the same day, and the
rule is now stated once for both: **Cycles COUNTS whole cycles everywhere in this
suite, so anything that is really a position inside one beat must not borrow the
word.** Both controls say `% of heartbeat`, and every whole number a person can
reach for now does something.

No migration was needed for the change: measured, no instance stores a value for
either slider, so all nine take the new default.

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
| 5 | Systole unit | NEW |
| 6 | S1 Frequency Hz | 11 |
| 7 | S1 Decay ms | 9 |
| 8 | S1 Volume | 6 |
| 9 | S2 Frequency Hz | 12 |
| 10 | S2 Decay ms | 10 |
| 11 | S2 Volume | 7 |
| 12 | Brightness | 8 |
| 13 | HB Stereo width ms | 13 |
| 14 | HB Master volume | 3 |
| 15 | Heartbeat solo | 4 |

S1 and S2 are interleaved by SOUND rather than by parameter: frequency, decay and
volume for the first beat, then the same three for the second. Today the six are
split across three separated pairs (6/7, 9/10, 11/12), so tuning one beat means
visiting three places.

### Breath

| new | control | from |
|---|---|---|
| 16 | Breaths per minute | 53, no longer rewriting anything |
| 17 | Breath rate mode | NEW |
| 18 | Inhale | 16 |
| 19 | Top pause | 17 |
| 20 | Exhale | 18 |
| 21 | Bottom pause | 19 |
| 22 | Inhale Frequency Hz | 20 |
| 23 | Exhale Frequency Hz | 21 |
| 24 | Inhale Fade In | 23 |
| 25 | Inhale Fade Out | 24 |
| 26 | Exhale Fade In | 25 |
| 27 | Exhale Fade Out | 26 |
| 28 | Fade Mode | 27 |
| 29 | Breath High-pass Hz | 22 |
| 30 | Breath Post-filter Hz | 39 |
| 31 | Breath Post-filter Q | 40 |
| 32 | Sigh interval | 60 |
| 33 | Sigh depth multiplier | 61 |
| 34 | Breath Stereo width | 28 |
| 35 | Breath Volume | 14 |
| 36 | Breath Solo | 15 |

### Bloodflow

| new | control | from |
|---|---|---|
| 37 | Bloodflow offset | NEW |
| 38 | Bloodflow offset unit | NEW |
| 39 | Bloodflow Attack (proportion of cycle) | 34 |
| 40 | Bloodflow Decay (proportion of cycle) | 35 |
| 41 | Bloodflow Dicrotic Level | 32 |
| 42 | Bloodflow Filter Hz | 31 |
| 43 | Bloodflow Resonance | 33 |
| 44 | Bloodflow Stereo width | 36 |
| 45 | Bloodflow Volume | 29 |
| 46 | Bloodflow Solo | 30 |

Bloodflow has no rate of its own, so the offset takes the rate's place at the head
of the group: it is the control that says how this layer sits in time.

### Master and transport

| new | control | from |
|---|---|---|
| 47 | Master stereo flip | 2 |
| 48 | Start delay | 41 |
| 49 | HB: Play for | 42 |
| 50 | HB: Rest for | 43 |
| 51 | Breath: Play for | 44 |
| 52 | Breath: Rest for | 45 |
| 53 | Bloodflow: Play for | 46 |
| 54 | Bloodflow: Rest for | 47 |

### Drift

| new | control | from |
|---|---|---|
| 55 | Drift target | 54 |
| 56 | Drift up amount | 55 |
| 57 | Drift down amount | 56 |
| 58 | Drift period | 57 |
| 59 | Drift period unit | NEW |
| 60 | Drift shape | 58 |
| 61 | Drift play for | NEW |
| 62 | Drift rest for | NEW |

### Ramp

| new | control | from |
|---|---|---|
| 63 | Ramp target | 48 |
| 64 | Ramp by | 49 |
| 65 | Ramp time unit | NEW |
| 66 | Ramp duration | 50 |
| 67 | Ramp play for | NEW |
| 68 | Ramp rest for | NEW |
| 69 | Ramp engage | 51 |
| 70 | Ramp start delay | 52 |

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

**`Systole unit`, per instance.** `scattered.rpp` gets **Beats** — its 0.14 is
genuinely beats and that preserves it exactly. Every other instance gets the
declared default of **Milliseconds**, which is already what its number means.
`womb-and-baby...` included: its 180 is milliseconds, and 180 ms is what the
load-time seeding already turns it into today. **No instance changes what it
sounds like.**

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
- **Assert `systole_samples < cycle_len`** in the simulation, across every mode
  and both units, so the S2-never-fires case cannot come back.
- **Fix `CLAUDE.md`'s "R20/R21 built everywhere" claim** in the same commit.

## Open, and needing Rozaya rather than me

1. **Does `Heart rate` want `Seconds` and `Hz` at all?** The canonical five are the
   suite standard and consistency is the whole point, but "a heartbeat every 0.857
   seconds" is a stranger thing to reach for than the same idea in BPM. The
   recommendation is to ship all five anyway — an unused option costs nothing, and
   a missing one makes this plugin the odd one out again, which is what we are
   fixing.
2. **Nothing in this migration changes a sound, after all.** An earlier draft said
   `womb-and-baby-heartbeats-with-bloodflow.RPP` needed repairing and asked for a
   yes on it. That was based on a wrong finding (see *Systole, and a claim I got
   wrong*): the project self-corrects on load and is fine. Every instance keeps
   `Systole` at its stored value, with the unit that reproduces what it does today
   — Milliseconds for the eight that mean milliseconds, Beats for `scattered.rpp`,
   whose 0.14 really is beats. **The permission asked for is withdrawn because the
   problem it was for does not exist.**

---

# Follow-up, 2026-09-06 (evening) — the breath, after hearing it

**The rebuild above was HEARD AND GOOD** — *"Everything else, though, passes. :)"*
This section is the one thing that did not pass, and it is a regression I
introduced the same day.

**Status: BUILT AND MIGRATED 2026-09-06.** 9 instances, values only -- no slider
moved and the count stayed at 70. Verified by BEHAVIOUR: every project's breath
cycle length and sigh-breath length are identical before and after. The migration
REFUSES rather than flattening if it ever meets a stored breath rate that would
actually have rescaled something. **NOT HEARD.**

## What went wrong, and it was written down before I did it

Rozaya, using it: *"The every n beats vs. n per beat distinction is confusing in
practice when it comes to breath segments and breaths per minute."* Then, asked
whether it was the name fighting the mode or the two competing beat-counts:
*"It's both. And both interacting with other, which is a third thing that fell out
and clattered, loudly, on the ground."*

The third thing is the root. I made the four breath segments **proportions of a
length set elsewhere**. That exact model had already been built, reported broken by
Rozaya three separate times in August, and deliberately replaced — and the comment
saying so was in the block I was editing:

> *What this replaced: the four sliders were a RATIO and a separate value set the
> total. It fitted the shape correctly and was still wrong, because 4-0.5-8-1
> stopped meaning anything you could count, halving the in and out did not shorten
> the breath (it only gave the pauses a bigger share), and the total was seeded
> from the tempo you happened to switch modes at. (Rozaya, three separate reports,
> 2026-08-30/31.)*

**I quoted the paragraph above it in my own new comment and rebuilt the thing it
rejected.** Reading a warning is not the same as heeding it. The test that would
have caught it: *what did this replace, and why?*

## What is NOT the fix

**Removing the control.** That was proposed and Rozaya caught the hole in it:
*"I think there are times you'd want to be able to adjust all 4 ratoes at once."*
Correct — and checked: with it gone, the only way to rescale a breath is to
multiply four numbers by hand, which is precisely the barrier this suite exists to
remove. (The Drift/Ramp `Breaths/min` target survives either way, but that is
modulation over time, not setting.)

**Removing the slider rewrite.** Also proposed, also wrong. Rozaya: *"I'm not happy
with the death of the slider changes; that was a deliberate bend toward honesty
when rescaling."* Right — after a rescale the four numbers ARE the real durations
rather than a ratio to decode. R20's "no control writes into another" is against
SILENT coupling; a one-shot you press, that shows you its result, is the opposite
of silent. **The rewrite is the honest half and it stays.**

## The three changes

### 1. The breath setup control speaks the breath's own unit

Rozaya: *"Breaths per minute needs to not make up that seconds are slower... 4
seconds isn't *that*, if set in like 70 bpm or something."* The failure mode: type
5 breaths a minute while the segments are in beats and they come back as 14 and
28, which reads as nothing you asked for.

**So what you type and what appears must be the same family:**

| breath unit | the setup control | type 12 and you get |
|---|---|---|
| Seconds | **Breaths per minute** | a 12-per-minute breath, segments summing to 5 s |
| Beats | **Beats per breath** | segments summing to 12 beats |

One-shot in both cases: it scales the four segments once, in their own unit, then
reads 0 again. Afterwards every number on screen is a real duration, and halving
the inhale genuinely shortens the breath.

**The trade, chosen deliberately:** per-minute is not reachable while the breath is
in beats. That is the point — in beats you are thinking in beats, which is why you
are there. Coherence-rate breathing is a seconds-mode activity.

### 2. The segments get a plain unit

`Breath rate mode` (the five-option R20 picker) goes. The breath has no rate
control, so it needs no rate mode — it needs to know what its four numbers are in.
**`Breath unit {Seconds, Beats}`**, declared Seconds.

This is a **principled exception to R20**, like Veil's. The breath's rate is
EMERGENT from its segments; there is no rate value for a mode to qualify. Forcing
the five-option picker on it is what produced the `N per beat` nonsense Rozaya hit
— "eight breaths per beat" is not a thing anyone wants.

### 3. Sigh depth stops being a multiplier

Rozaya: *"that sigh multiplier is the exact same type of problem."* Correct.
`Sigh depth multiplier` at 1.5 means doing multiplication in your head to set it
and division to hit a target. It becomes **how much LONGER the sigh breath is**, in
the breath's own unit — additive, direct, and it composes with everything else.

## What this costs the library

Nothing audible, and that is measured rather than assumed. Every instance holding
a non-zero `Breaths per minute` has segments that ALREADY sum to exactly the cycle
it asks for, so the scale is 1 and removing the live scaling changes no sound:

| project | Breaths/min | segments | sum | 60/rate |
|---|---|---|---|---|
| back-to-life | 5 | 4/0/8/0 | 12 | 12 |
| deep-night | 6 | 4/0/6/0 | 10 | 10 |
| womb-bubbles-proto | 5 | 4.8/0/7.2/0 | 12 | 12 |

The other six hold 0. One more migration of 9 instances, and it should be the
last — everything Womb is owed is now in this document.
