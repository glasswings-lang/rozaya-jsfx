# Melody Phase — the R20/R21 conversion, and everything else it is owed

Written 2026-09-05, **BUILT, MIGRATED and INSTALLED 2026-09-06. NOT HEARD.**

Verification, all of it without ears: lint clean; the five rate modes and the
drift/ramp direction gates simulated and their numbers read; 73 instances across
7 projects migrated and checked by **11,865 checks, 5,706 of them name-decoded
value comparisons against the pre-migration snapshot** — PASS. Nobody has played
it since the swap. Backups: projects at
`E:/reaper/finished/backups/snapshots/_pre-melody-r20-20260906/`, the old plugin
build at `E:/reaper/finished/backups/melody_phase.PRE-R20-20260906.jsfx`.

Rozaya: *"Melody needs what daple just got I think rofl."* It does. This is the
delta from the layout that landed on 2026-09-02 (`melody-phase.md`), not a
re-listing of it.

**This is Melody's SECOND migration**, and that is knowingly spending the risk
twice. It is worth it because the alternative is Melody keeping a sync mechanism
no other plugin has, which is exactly the "a thing learned on one plugin is not
true of the others" problem the whole sweep exists to remove.

**It is the second and it must also be the LAST.** The first draft of this
document covered the rate block only. That would have migrated 73 instances
today and migrated the same 73 again to add the Drift and Ramp controls Melody
is still missing — which is the exact failure `CLAUDE.md` records as *five
migrations in one day*. Everything Melody is owed is therefore in here.

---

## What changes

### 1. The rate block becomes the suite's (R20 + R21)

**Today** Melody carries the older R11 shape — five controls:

```
1  Rate value
2  Rate mode                {BPM, Seconds, Hz}
3  Sync to host             {Off, On}
4  Host sync target         {Rate value, Pan base rate}
5  Every N beats (per sync target)
```

**After** — two controls, the same as everywhere else:

```
1  Rate value
2  Rate mode                {BPM, Seconds, Hz, Every N beats, N per beat}
```

Sliders 3, 4 and 5 are **deleted**.

### 2. The pan gets its own rate mode

`Pan base rate` currently has **no mode of its own** — it is handed the
sequencer's, at `melody_phase.jsfx:1116` and `:1492`. That is the missing control
that caused R11's target selector to be built in the first place, and R20 says
every rate carries its own complete pair.

So a **`Pan rate mode`** is added immediately after `Pan base rate`, with the
same five entries. The pan can then be synced while the sequencer runs free, or
the reverse, with no selector reaching across.

### 3. `Pan glide` and `Cycle steps` come home

They are pan controls sitting at **81 and 82**, appended after the Ramp block
because that was where the free IDs were. They move into the pan block, in the
position the Tremolo already puts them: after `Pan spread`, before the pan rate.
Reading order says everything belonging to a layer lives with that layer.

### 4. Drift gains its three missing controls

Melody has `target / up / down / period / shape`. The canonical block, as built
in the Sweeping Filter, Tremolo, Veil, Morpher, Phaser, Bubbler, Dapple and
Resonance Bank, is:

```
Drift target
Drift up amount
Drift down amount
Drift period
Drift period unit      {Cycles, Seconds, Beats}     <- NEW, default Cycles
Drift shape
Drift play for         (periods, 0 = always)        <- NEW
Drift rest for         (periods, 0 = always)        <- NEW
```

Melody has a rate, so it has cycles to count, so `Cycles` is the default — the
same rule that made Veil the one principled exception.

### 5. Ramp gains its three missing controls

```
Ramp target
Ramp by
Ramp time unit         {Cycles, Seconds, Minutes, Beats}  <- NEW, default Minutes
Ramp duration
Ramp play for          (0 = smooth)                       <- NEW
Ramp rest for          (0 = smooth)                       <- NEW
Ramp engage
Ramp start delay
```

**The default is index 2, `Minutes`, not index 0.** That is the near-miss
recorded in `CLAUDE.md`: the declared default is a live value for every instance
that never touched the control, and putting `Cycles` at index 0 would silently
reinterpret every existing ramp. All 73 Melody instances are on the default, so
this matters here exactly as much as it did there.

**Both new play/rest pairs are per-target**, banked in `@serialize` beside the
existing per-target Drift and Ramp values, which is how the other eight carry
them.

### 6. Net slider count

**82 → 86.** Three deleted, seven added.

---

## The order

Measured against the canonical reading order approved 2026-09-05: *what the
plugin IS → its rate (value, then mode) → the shape of its movement → stereo and
pan → output level → transport → drift → ramp.*

| New | Control | From |
|---|---|---|
| 1 | Rate value | 1 |
| 2 | Rate mode `{BPM,Seconds,Hz,Every N beats,N per beat}` | 2 (enum widened) |
| 3 | Waveform | 6 |
| 4 | Pulse width | 7 |
| 5 | Tuning reference (Hz) | 8 |
| 6 | Transpose (half steps) | 9 |
| 7 | Octave shift | 10 |
| 8 | Binaural beat (Hz, L/R offset) | 11 |
| 9 | Attack (% of note duration) | 12 |
| 10 | Attack shape | 13 |
| 11 | Release (% of note duration) | 14 |
| 12 | Release shape | 15 |
| 13 | Glide time (seconds; 0 = off) | 16 |
| 14 | Legato glide | 17 |
| 15 | Pan enabled | 18 |
| 16 | Pan mode | 19 |
| 17 | Pan spread (%) | 20 |
| 18 | Pan glide ms (0 = instant) | **81** |
| 19 | Cycle steps (per-cycle modes) | **82** |
| 20 | Pan base rate | 21 |
| 21 | Pan rate mode | **NEW** |
| 22 | Pan increment per voice | 22 |
| 23 | Sequence length | 23 |
| 24 | Direction | 24 |
| 25 | Loop sequence | 25 |
| 26–65 | V1–V8 (Note / Next voice in / Note duration / Gain dB / Active) | **26–65, unchanged** |
| 66 | Master gain (dB) | 66 |
| 67 | Start delay (in rate mode units) | 67 |
| 68 | Play for (steps) | 68 |
| 69 | Rest for (steps) | 69 |
| 70 | Rest mode | 70 |
| 71 | Drift target | 71 |
| 72 | Drift up amount | 72 |
| 73 | Drift down amount | 73 |
| 74 | Drift period | 74 |
| 75 | Drift period unit | **NEW** |
| 76 | Drift shape | 75 |
| 77 | Drift play for | **NEW** |
| 78 | Drift rest for | **NEW** |
| 79 | Ramp target | 76 |
| 80 | Ramp by | 77 |
| 81 | Ramp time unit | **NEW** |
| 82 | Ramp duration | 78 |
| 83 | Ramp play for | **NEW** |
| 84 | Ramp rest for | **NEW** |
| 85 | Ramp engage | 79 |
| 86 | Ramp start delay | 80 |

### The property that makes this cheaper than it looks

**Sliders 22 through 70 do not move.** The three deletions at 3–5 are exactly
cancelled by the two controls pulled back from 81/82 plus the one new pan mode,
so the numbering re-converges at 22 and stays put through the whole voice bank,
the output level and the transport block.

That means the migration only touches **1–21 and 71–86** — 37 of 86 positions —
and the 40 per-voice sliders, which are the ones carrying the actual music, are
untouched by construction. It is not a reason to skip verification; it is a
reason the verification should *show* those 40 unchanged, because if it does not,
something is wrong that the table above cannot explain.

---

## The measurement, taken live 2026-09-05

Re-scanned at authoring time rather than trusted from the earlier draft, because
the aggressive-restructuring window is closed.

**73 instances across 7 projects** — `melodic` (4), `outcoming` (19),
`slow-summer` (6), `upswing` (17), `simple-sequence` (12),
`simple-sequence-check` (12), `testing-proof of concept` (3). Four are finished
work, ear-tested 2026-09-04.

**27 are synced, 46 are free-running.** Of the 27:

| Every N beats | instances |
|---|---|
| 2 | 12 |
| 4 | 12 |
| 1 | 1 |
| 0.5 | 1 |
| 0.333333 | 1 |

**Not one of the 27 targets the pan.** Every single one is on `Rate value`, which
is the measurement that killed R11's selector in the first place — the capability
it exists for has never been used.

**Nothing is stored on Drift or Ramp anywhere.** Zero of 73 instances have a
drift up or down amount set; zero have Ramp engaged. So the seven new controls
move no stored value, and the whole cost of adding them is the renumber that is
happening anyway. **This is why they go in now and not later.**

That `0.333333` is worth keeping in view: it is *every third of a beat*, three
cycles per beat, and no ratio menu would have offered it. It is also the instance
that will read most clearly after R21, as **`3` in `N per beat`**.

---

## The migration

**For the 27 synced instances:**

- `Rate mode` → **3** (`Every N beats`)
- `Rate value` → the stored `Every N beats` value

Their existing Rate value and Rate mode are DISCARDED, and that is correct: while
`Sync to host` is On those two are not consulted for the synced target, so they
hold whatever was last set free-running. Overwriting them is what preserves the
sound.

**The one `0.333333` instance** becomes `Rate mode` **4** (`N per beat`) with a
`Rate value` of **3** — the same speed, written so it can be read. Recommended by
Claude 2026-09-05 and taken as agreed by Rozaya in the same exchange; it is a
judgement about how it reads, not about correctness, so it can be reverted to
`0.333333` in `Every N beats` without touching anything else.

**For the 46 free instances:** the rate block is untouched in meaning. Rate mode
indices 0, 1 and 2 keep their exact meanings; only the slider's declared range
widens from 2 to 4.

**For all 73:** the permutation above is applied, and the seven new sliders are
left absent from the value line, so every instance takes their declared defaults
— which are the off/neutral values by design.

---

## What must be checked before building

- **The aggressive-restructuring window is CLOSED** as of 2026-09-05 — a project
  has been saved on current builds. The scan above was re-run at authoring time;
  re-run it again at migration time rather than trusting these counts.
- `docs/open-bugs.md`'s Melody entry is **CLOSED and accepted with its
  workaround** as of 2026-09-05. **Read it for its five burned theories and the
  FORBIDDEN fix, then leave it alone.** Do not attempt the alignment bug while
  doing this conversion — that is the "I also did X while I was in there" failure
  mode, and it is how the forbidden fix got shipped once already.
- Melody has **more than 64 sliders**, so its `.RPP` value lines carry the `""`
  marker at index 64. `tools/rpp_sliders.py` handles it; nothing may re-derive
  the format.
- Bump the `@serialize` magic in the same commit as the renumber. That is the
  only thing that made the 2026-07-02 slider-insert repairable. The magic is
  `2200000 + N_TARGETS`; the two new per-target play/rest pairs for Drift and
  the two for Ramp change the blob's size, so the READ must accept the old magic
  and skip them, exactly as the `host_bpm_saved` field already does.
- **Sequence placement follows the sync switch that is being deleted.** The
  2026-09-02 build note records that transport-start sequence placement was
  gated on `rate_mode == 3` and then moved onto `Sync to host`. Deleting that
  switch means re-pointing it at `rate_mode >= 3`, which is the suite's standard
  "am I host-synced" gate. **Miss this and a well-built feature dies silently.**
- Every gate meaning *am I host-synced* becomes `>= 3`; every conversion chain
  asking *which mode am I* stays exact. That distinction is R21's, and it was
  checked one gate at a time in the other twelve plugins.
