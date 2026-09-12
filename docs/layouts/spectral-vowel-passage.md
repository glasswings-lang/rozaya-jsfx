# Spectral Vowel Passage — authored layout

Written by hand 2026-08-31, not generated. **Status: order drafted, awaiting review.**
10 projects. Sibling to the Morpher; shared controls must read the same in both.

## The finding that shaped this layout

**Passage is a per-slot editor, and seventeen of its controls are per slot — but only
eight of them say so.**

Verified by reading the selector-change block (`last_cap_slot != cap_slot`), not by
trusting the labels. Per slot: Capture point, Capture average, the four slot timings,
crossfade, mute, Output level, **Texture, Spread, Pitch, Stereo width, Low cut, Denoise**,
Overtone harmonic, Overtone lift.

The last six carry no `(per slot)` in their names at all. That is a trap: set Pitch,
switch slots to check something, come back, and the pitch you set is gone — working
exactly as designed, and looking exactly like a bug.

So the plugin is not "some per-slot timings plus a global tone section". **Each slot is a
complete voice preset** — its own texture, pitch, width, filtering, overtone and level,
plus its place in the route. The layout should say that, and the names should too.

Rozaya spotted this from the reading order alone: *"it feels like the routing for the
slots should be... not there. Something feels off."*

## All slots, and what Passage is FOR -- 2026-09-11

Rozaya, on why Passage should exist beside the Morpher: *"I think the solution is to
have an all slots thing, meaning you can capture to all of them, effect all of them,
etc. then modify each as you see fit. That way it's not just a clunker morfer"*.
And: *"Yes, capture should grab into all 8 slots. tbqh, morfer needs it too"*.

**Mine, unquoted:** `Capture slot` becomes `{All, Slot 1, ..., Slot 8}`, All first as
on Polyrhythm's Voice. The planned 1-based renumber already adds one to every saved
value, so All at 0 costs nothing extra. On All: Capture now grabs the same moment into
all eight; every per-slot control shows Slot 1 and writes all eight, change-detected
so parking on All flattens nothing. The Morpher got the same on 2026-09-11 with no
migration (`spectral-vowel-morpher-all-slots-20260911.md`).

**The slot timings' unit, 2026-09-11.** Rozaya: *"Each slot should have its own:
beats, hz, seconds. :)"* -- one unit picker per slot for its four timings, replacing
the tempo section's `Sync to host` (retired by R20). Order `{Seconds, Hz, Beats}`, the
rate list's relative order -- proposed by me, Rozaya: *"that's fine 🙂"*. **Mine,
unquoted:** in Hz a timing lasts one cycle of that rate (bigger is shorter).

**Pitch, 2026-09-11: Bubbler's Source note block, per slot -- and the Morpher's main
Pitch takes it too.** Rozaya, describing its own design: *"a slider where you could
set it with pitch on 0, to basically tell it, hey, this is where 0 is, that way
adjusting by note name could actually work ... It itself wouldn't change anything"*.
No "As captured" entry: *"As captured is basically what 0 would be there, anyway? ...
you have to build it from there anyway."* **New:** *"you also gotta finetune the
source note in case of some weird microtonal fuckery"* -- a fine tune ON the source
note, which Bubbler and Sustain Looper do not have either, so it goes to all four.
Its shape, proposed by me: a value then a unit `{Hz, Semitones, Cents}`, default
Cents, directly after Source note, as Fine tune is -- Rozaya: *"Yes."* Source note
still starts on None and the new fine tune at 0, so nothing sounds different until
chosen -- Rozaya: *"Yeah, and I like it"*.

**The whole layout is now authored below; its remaining questions are listed at its
end.** What this paragraph used to list as unsettled, kept for the record:
the rest of R22's pitch block for Passage (*"their own discussion"*), R24's full target
list with Start delay / Play for / Rest for, and the two OPEN items further down.

## BUILD PROGRESS -- read this first if you are picking Passage up

Projects migrate ONCE, at the end. Until then `src/` is ahead of every saved
instance: **do not install it.** Tools: `tools/passage_migrate_20260911.py` (the one
slider-line migration, grown stage by stage; `inventory` is a dry run) and
`tools/passage_verify_20260911.py` (`current` = all 49 live instances, pre-layout
build `d5adcaf` on the project vs new build on a temp conversion, bit-identical).
Inventory 2026-09-11: 49 instances in 11 projects; 5 in `nightfall.RPP` are 35-value
lines (pre-Overtone), filled with the defaults REAPER has always supplied.

- **Stage 1, renumber: DONE** (`096ad27`), `jsfx_renumber verify` passed all three.
- **Stage 2, the 24 new controls declared, inert, seeded: DONE**, 49 of 49 bit-identical.
- **Stage 3, All slots on Capture slot: DONE.** Migration adds 1 to each saved slot.
  `current`: 49 of 49 bit-identical. `allslots`: a capture on All == an ordinary capture
  (heard in Slot 8); Texture on All changes Slot 8 and == by hand; passing through All
  keeps Slot 8's own Texture; a Drift set on All moves Slot 8 and == by hand. Change
  detection via `ps_last` (adopted in @block and @serialize). Not yet tested: save and
  reopen on All (bridge test, at the end).
- **Stage 4, the pitch block: DONE.** `current` 49 of 49 bit-identical; `pitch`: 1200
  cents, 440 Hz from 440, 880 Hz from 880, and 11 semitones + 100 cents fine tune all ==
  Transpose 12; Source C4 + Target E4 == Transpose 4; Source C4 50 cents flat + Target
  E4 == Transpose 4.5; Transpose on All == by hand on Slot 8; Transpose 12 != none. Seven per-slot banks (`slot_tunit`, `slot_fine`, `slot_funit`, `slot_srcnote`,
  `slot_srcfine`, `slot_srcfunit`, `slot_tgtnote`) banked on slot switch, stamped live,
  All via `ps_last` 32-38, stamped on capture; `tuning_ref` from slider 30; the Target
  note mirror in @slider before the slot block. **SETTLED:** moving Source note or its
  fine tune re-reads the Target note and never changes the sound. Rozaya: *"The source
  note is just to tell the targget what 0 semitones is though"*. **The new
  banks are NOT yet in @serialize** (the save-format stage adds them all at once).
- **Stage 5, per-slot Wash grain and High cut: DONE.** `current` 49 of 49 bit-identical;
  `grainhc`: High cut 200 Hz takes a 220 Hz tone's wash and voice to rms 0; High cut and
  Wash grain on All == by hand on Slot 8; 40 ms grain on Slot 8 changes Slot 8 and
  leaves Slot 1 bit-identical. Banks `slot_grain`, `slot_hicut`, banked like the others (All via
  `ps_last` 39-40). High cut is the Morpher's shape (`hc_g`, `hc_bound`, fade over the
  top fifth) in all six voice partial lines and in `build_spectrum` after the per-slot
  transposition. Grain follows the heard slots in @block (one slot's exact value when
  they agree). **SAVE-FORMAT STAGE MUST FIX:** `grain_seed` copies Wash grain into all
  eight slots on EVERY load for now; once `slot_grain` is serialized, gate it on the
  older magics only, or per-slot grain is flattened on every reopen.
- **Stage 6, the slot timing unit: DONE.** `current` 49 of 49 bit-identical; `timing`
  (Auto-morph Sweep, crossfade OFF): gap 1.5 s != 1 s; Beats 1, 2, 1, 2 at 120 BPM and Hz
  2, 1, 2, 1 == Seconds 0.5, 1, 0.5, 1; a gap of 0 in Hz == 0 s. **Test trap:** with
  crossfade into next ON (default) a leg ignores its gap, and identical captures blend
  inaudibly -- the first run's can-fail check caught it. Bank
  `slot_tmunit` (All via `ps_last` 41), read once per leg start through `tm_sec`, with
  Drift added in the timing's own unit. **Mine, unquoted, to tell Rozaya:** in Hz a
  value of 0 still means none (not an endless leg); in Beats a leg follows the live
  tempo at the moment it starts.
- **Stage 7, transport: DONE.** `current` 49 of 49 bit-identical; `transport`: Start
  delay 17 s != 16 s; 32 beats at 120 BPM and 0.0625 Hz == 16 s; Play for / Rest for 1 s
  changes the sound and == 2 beats; Silence at rest != Pass-through. Ported from
  the Morpher (`src/spectral_vowel_morpher.jsfx` ~1667-1694 and its output ~2323): the
  Start delay holds Drift, Ramp and the walk; a rest holds the walk only on Freeze in
  place; rest applies to the output SUM (Pass-through keeps dry, Silence mutes all).
  Lengths via `tm_sec(slider41, ...)` per block. **Mine, unquoted:** the counters
  restart on every play edge (Passage sets `ext_noinit`, so @init cannot do it).
- **Stage 8, Drift period unit + Drift play/rest, Ramp time unit + Ramp play/rest:
  DONE.** `current` 49 of 49 bit-identical; `driftramp`: drift period 3 s != 2 s, 4
  beats at 120 BPM == 2 s, Drift play/rest changes the sound; ramp 0.5 min != 0.25 min,
  15 s and 30 beats == 0.25 min, Ramp play/rest changes the sound; `cycles`: 0.0625
  cycles (a 48 s walk) == 3 s, 0.125 cycles != 3 s -- all after the fix below. Ported from the Morpher
  (`pr_frozen`; rests come out of a ramp's duration). Units global, play/rest per
  (slot, target), banked in both selectors and on All (`ps_last` 27-30). **Cycles is
  OPEN:** built as one walk through the active slots' legs (`pv_cyc`, mine). Rozaya:
  *"Passage's whole plan was very delayed, and by the time we got to it we'd settled on
  the full thing for drift. cycles doesn't really make sense here. I can kind of see it
  sort of? though. the way you describe it."* Asked: keep Cycles (same list everywhere)
  or drop it from Passage. **SETTLED:** *"Keep it in. might be interesting"* -- a Cycle
  is one walk through the active slots' legs. **A real fault the Cycles check found:**
  the walk was summed before `rebuild_active_slots()`, so for one block after a capture
  or a mute it read the old slot list; a drift in Cycles ran that block at the 0.05 s
  floor and kept the phase it gained. Measured with a debug copy that wrote
  `drift_unit_sec` and `n_active` out as audio (0.05 in the first block, then 48).
  Moved after the rebuild; `cycles`, `current` and `driftramp` all pass after it.
- **Stage 4 design notes (mine, from reading 2026-09-11):** Bubbler resolves a shift
  to semitones in `bb_semis_from(unit, v)` -- Semitones as is, Cents /100, Hz from the
  Tuning reference `12*log2((ref+v)/ref)` -- and mirrors Target note <-> Transpose value
  only while Source note > 0 AND Transpose unit is Semitones (`src/bubbler.jsfx` ~230-360).
  Passage's heard pitch is set in ONE place: `eff_semi_A/B = slot_pitch[sb_i/j] +
  pitch_mod_A/B` (~line 1600), so each slot's semitones become `semis_from(Transpose
  unit, value + drift) + semis_from(Fine tune unit, fine)`. New per-slot banks go at the
  END of the allocations (after `ps_last`, which grows to 64 for their All indices);
  all of them need `@serialize` fields behind a magic bump, gated on the magic that
  WROTE them. Source fine tune enters the mirror as `transpose = target - (source - 1) -
  source_fine_semis`; **mine, unquoted:** a source fine tune in Hz is measured from the
  source note's own frequency, not from the Tuning reference.
- **Still to build, in this order:** the pitch block (Source note, Source fine tune,
  Target note mirror, Transpose unit, Fine tune, Tuning reference); per-slot Wash grain;
  High cut; slot timing unit; transport (start delay, play/rest, unit, rest mode,
  output at rest); Drift period unit and play/rest; Ramp time unit and play/rest; the
  22-target list with Drift amount unit / Ramp by unit (blob magic bump, DSTRIDE 16 ->
  32, target remap); renames of existing labels to the table below; the manual;
  then the live migration, install, bridge test.

## THE LAYOUT, authored whole 2026-09-11 -- shown to Rozaya and settled the same day; nothing built

38 sliders become 60. Order follows Part 2 of the plan: the per-slot group whole and
contiguous, then what covers all slots, then transport, Drift, Ramp. Quoted decisions
are in the sections above; everything else here is mine and unquoted.

**Per slot -- pick a slot, then everything that slot is**

| # | control | from, and what the migration does |
|---|---|---|
| 1 | Capture slot `{All, Slot 1 ... Slot 8}` | 1; value +1 |
| 2 | Capture now | 2, renamed from `Capture spectrum` |
| 3 | Capture point (%, per slot) | 3 |
| 4 | Capture average (frames, per slot) | 4 |
| 5 | Source note (where zero is, per slot) `{None, C-1 ... G9}` | new, None |
| 6 | Source fine tune (per slot) | new, 0 |
| 7 | Source fine tune unit `{Hz, Semitones, Cents}` | new, Cents |
| 8 | Target note (per slot) | new |
| 9 | Transpose value (Hz / semitones / cents, per slot) | 18 `Pitch (semitones)`, same number |
| 10 | Transpose unit `{Hz, Semitones, Cents}` | new, Semitones |
| 11 | Fine tune (per slot) | new, 0 |
| 12 | Fine tune unit `{Hz, Semitones, Cents}` | new, Cents |
| 13 | Texture (% wash, per slot) | 15 |
| 14 | Wash grain (ms, per slot) | 16; the one global value copied into all eight slots |
| 15 | Spread (Hz, per slot) | 17 |
| 16 | Denoise (%, wash only, per slot) | 21; traced 2026-09-11: subtracts (value% of a tenth of the loudest bin) from every wash bin, floored at 0 -- the voice engine never reads it. The Morpher's is the same formula (`thr`, line ~1011) and takes the same name |
| 17 | Low cut (Hz, per slot) | 20 |
| 18 | High cut (Hz, 20000 = off, per slot) | new, 20000 -- no sound change |
| 19 | Overtone harmonic (per slot) | 36 |
| 20 | Overtone lift (dB, per slot) | 37 |
| 21 | Slot fade in (seconds / Hz / beats, per slot) | 5 |
| 22 | Slot hold (seconds / Hz / beats, per slot) | 6 |
| 23 | Slot fade out (seconds / Hz / beats, per slot) | 7 |
| 24 | Slot gap after (seconds / Hz / beats, per slot) | 8 |
| 25 | Slot timing unit `{Seconds, Hz, Beats}` (per slot) | new, Seconds -- same meaning |
| 26 | Slot crossfade into next (per slot) | 9 |
| 27 | Slot mute (per slot) | 10 |
| 28 | Stereo width (%, per slot) | 19 |
| 29 | Output level (dB, per slot) | 14 |

**All slots**

| 30 | Tuning reference (Hz) | new, 440 -- R22: one per plugin |
| 31 | Fade in shape (all slots) | 11 |
| 32 | Fade out shape (all slots) | 12 |
| 33 | Overtone width (harmonics, all slots) | 38 |
| 34 | Morph (% across captured slots) | 23 |
| 35 | Auto-morph | 24 |
| 36 | Audition | 22 |
| 37 | Input level (dry, dB) | 13 |

**Transport** -- new, as the Morpher has: 38 Start delay, 39 Play for, 40 Rest for,
41 Transport unit `{Seconds, Hz, Beats}`, default Seconds (proposed; Rozaya: *"Yes, I
forgot about that too."*), 42 Rest mode `{Walk through, Freeze in place}`, 43 Output
at rest `{Pass-through, Silence}`. All default off, so no sound change.

**Drift** 44-53: target, up, down, **Drift amount unit** (new, per target, `Target
default` -- today's meaning), period, period unit `{Cycles, Seconds, Beats}` (new,
Seconds -- what `Drift period (seconds)` meant), shape, play for (new), rest for (new),
restart. **Ramp** 54-62: target, by, **Ramp by unit** (new, per target, `Target
default`), time unit `{Cycles, Seconds, Minutes, Beats}` (new, Minutes -- what `Ramp
duration (minutes)` meant), duration, play for (new), rest for (new), engage, start
delay. **62 controls.**

**The amount units, 2026-09-11.** The per-target `Drift amount unit` / `Ramp by unit`
agreed in the Morpher's layout on 2026-09-08 (after *"No unit locks. ever."*) and never
built anywhere. Offered: fold it into Passage's and the Morpher's migrations now, then
sweep the other seventeen straight after, or all nineteen later at a second migration
each. Rozaya: *"Yes, do it your way. I'd prefer that while we have room"*. **The
sweep is owed** (`docs/backlog.md`). **The option list, one for all nineteen plugins,** built from a scan of every slider
name in `src/` (units in use: Hz, dB, %, semitones, cents, ms, sec, minutes, BPM, beats,
cycles, degrees, plus counts): `{Target default, Hz, Semitones, Cents, Milliseconds,
Seconds, Minutes, BPM, Beats, Cycles, dB, Percent, Degrees}`. Proposed by me, grouped
pitch / time / level / angle with pitch in the pitch pickers' order; Rozaya: *"Yes"*.
Counts (harmonics, beats per bar) stay on Target default. It replaces the Morpher
doc's 2026-09-08 list, which lacked five units the suite uses.

**Drift and Ramp targets, in control order:** Transpose, Fine tune, Texture, Wash
grain, Spread, Denoise, Low cut, High cut, Overtone harmonic, Overtone lift, Slot fade
in, Slot hold, Slot fade out, Slot gap after, Stereo width, Output level (sixteen per
slot, reached through Capture slot, so All sets all eight); then Tuning reference,
Overtone width, Morph, Input level, Play for, Rest for (whole plugin, held in Slot 1's
row as Morph and Input level already are). 22 targets, from 14: the per-slot bank
stride grows from 16 to 32, and every saved target remaps -- a blob migration with a
magic bump.

**Not targets:** Capture slot, Capture now, Capture point and Capture average
(re-analysis, as on the Morpher), Source note and Target note (note pickers, as on
Bubbler), every unit and shape picker, Crossfade into next, Mute, Auto-morph,
Audition, Start delay, Rest mode, Output at rest, Drift restart, Ramp engage.

**Questions still open, to ask Rozaya one at a time:**
- SETTLED: Source fine tune is NOT a Drift target -- Rozaya: *"Yes."* And its NAME
  must say when it acts: *"that slider bit, whether it's 1 or 1000, needs to be
  honest about what it is relative to everything else so people aren't confusedly
  trying to change it and wondering wtf it's not doing anything"*. Read in Bubbler
  (`src/bubbler.jsfx` ~341-360): Source note and Target note mirror Transpose value
  ONLY while Source note is not None AND Transpose unit is Semitones; Target note is
  hidden otherwise. Source fine tune joins that mirror, so it acts under exactly the
  same condition. **Names:** `Source fine tune (only with a Source note, in Semitones)`
  and `Target note (only with a Source note, in Semitones)` -- the shorter of two
  offered; Rozaya: *"I think we should go with the shorter one"*. Passage, the
  Morpher, Bubbler and Sustain Looper all take them; a rename moves nothing.

## The order of 2026-08-31 -- SUPERSEDED by the layout above

**Per slot — pick a slot, then everything that slot is**

| new | control | from |
|---|---|---|
| 1 | Capture slot (All, Slot 1-8) | 1, now 1-based with All at 0 |
| 2 | Capture now | 2, renamed from `Capture spectrum` |
| 3 | Capture point (%, per slot) | 3 |
| 4 | Capture average (frames, per slot) | 4 |
| 5 | Slot fade in (sec, per slot) | 5 |
| 6 | Slot hold (sec, per slot) | 6 |
| 7 | Slot fade out (sec, per slot) | 7 |
| 8 | Slot gap after (sec, per slot) | 8 |
| 9 | Slot crossfade into next (per slot) | 9 |
| 10 | Slot mute (per slot) | 10 |
| 11 | Texture (% wash, per slot) | 15 |
| 12 | Spread (Hz, per slot) | 17 |
| 13 | Pitch (semitones, per slot) | 18 |
| 14 | Stereo width (%, per slot) | 19 |
| 15 | Low cut (Hz, per slot) | 20 |
| 16 | Denoise (%, per slot) | 21 |
| 17 | Overtone harmonic (per slot) | 36 |
| 18 | Overtone lift (dB, per slot) | 37 |
| 19 | Output level (dB, per slot) | 14 |

**All slots**

| 20 | Wash grain (ms) | 16 |
| 21 | Fade in shape (all slots) | 11 |
| 22 | Fade out shape (all slots) | 12 |
| 23 | Overtone width (harmonics, all slots) | 38 |
| 24 | Morph (% across captured slots) | 23 |
| 25 | Auto-morph | 24 |
| 26 | Audition | 22 |
| 27 | Input level (dry, dB) | 13 |

**Drift** 28-33 (target, up, down, period, shape, restart) — from 25-30
**Ramp** 34-38 (target, by, duration, engage, start delay) — from 31-35, engage and
start delay swapped into canonical order

38 sliders, unchanged in count.

## Naming

- **Every per-slot control says `(per slot)`.** Nine currently do not. This is the single
  most valuable naming change in the plugin.
- **`Capture spectrum` becomes `Capture now`.** It is a momentary trigger
  (`{Off, Capture now}`) that grabs audio into the selected slot and auto-releases — not
  a setting. The old name reads like a mode.
- The long explanatory labels shorten: `Slot fade in (sec) (per slot: how long this slot
  takes to rise)` becomes `Slot fade in (sec, per slot)`. NVDA reads the whole sentence on
  every arrow-step.
- Shared controls match the Morpher exactly: `Texture (% wash)`, `Stereo width (%)`,
  `Morph (% across captured slots)`, `Capture average (frames)`.

## Two things Wash grain is not

Recorded because I got both wrong out loud and Rozaya corrected them.

**It is not the other half of Texture.** Texture is the only voice-versus-wash control.
Wash grain sets `W`, the resynthesis window length, with `HOP = W/4` — so it is **how long
each grain of the wash is**, four overlapping at any moment. Short is fluttery and
textural; long is smooth and smeared. It is the wash's character, not its amount.

**Its being global is NOT an established constraint.** I asserted that per-slot grain
would cause clicks and that the global scope was therefore deliberate. That is a plausible
mechanism repeated as a finding, which is the exact failure mode CLAUDE.md records for the
`filt_stages` straight-wire theory. **Nobody has tested it.**

## SETTLED 2026-09-11: Wash grain is per slot

Asked with a recommendation of yes; Rozaya: *"I like that idea yeah. especially now
that we're not dealing with cpu shit with that"*. **Mine, unquoted, to MEASURE not
assume:** whether a morph between two slots of different grain lengths costs more
CPU, and the loudness wobble predicted below. Read so far: there is ONE synthesis
window at a time (`build_synwin`: W, HOP, GFFT), rebuilt in @block whenever the grain
length changes -- exactly what dragging Wash grain already does. So a per-slot grain
is born at its slot's (or the blend's) length, and a morph costs about what dragging
Wash grain costs. The crackle Rozaya refers to was heard GONE 2026-08-12 (`724f635`).

## (was OPEN) should Wash grain be per slot?

Rozaya, 2026-08-31: *"letting old grains go at their old length is just... the right thing
to do? My mental image is: grains of rice. You wouldn't chop them, so why do that to
audio."*

That is the standard granular model and it is correct: **a grain is an event, scheduled
with its parameters fixed at birth.** You do not reach into a grain that is already
sounding. A grain-size change applies to the grains scheduled after it.

Reasoning the actual risk through, rather than assuming it:

- Overlap-add does not require every grain to be the same length. Each is windowed before
  being summed, and the read pointer just walks the accumulator.
- What breaks transiently is **normalisation**. Four overlapping Hann windows sum to a
  constant; grains are scheduled every `W/4`, so if new grains are shorter they arrive more
  often, and for about one grain's duration the overlap count is between the two values.
- Predicted symptom is therefore an **amplitude wobble lasting roughly one grain**, not a
  click. Fixable by normalising against the running window sum, or by ramping the grain
  size across one grain length.

**To decide:** whether per-slot grain is musically wanted at all. If it is, the
implementation is "new grains take the new length, in-flight grains finish at the old one"
and the only work is the normalisation. If it is not wanted, keep it global — but document
it as a choice, not as a click hazard.

## Also open

- **Passage has no `High cut`; the Morpher does.** Same voice engine. On the Morpher it
  does double duty, shaping the top end and acting as a CPU dial, because partials above
  the cut stop being computed. Worth adding while the plugin is open.
- **`Denoise` name is provisional** — marked `(%)` without tracing what it scales, same
  as the Morpher's. Trace before committing to it.

## Migration

- **Positions:** the authored permutation above. Generalise
  `tools/passage_migrate_sliders.py` from inserts to permutations — it already knows every
  hop this plugin's layout has taken, and this becomes the next hop in that chain.
- **Values:** `Capture slot` gains 1 (0-7 becomes 1-8). Nothing else changes value.
- **The blob is untouched by a renumber.** Verify with `tools/passage_captures.py`, which
  can list and extract the captures inside it.


## Tempo sync — added 2026-09-01, Rozaya's request. SUPERSEDED 2026-09-11

**Its `Sync to host` switch is replaced by each slot's own `Slot timing unit
{Seconds, Hz, Beats}`** (quoted at the top). R20 retired the switch shape on
2026-09-04. Kept for the reasoning about durations, not as the design.

Rozaya, 2026-09-01: *"[it] absolutely could do with ... a rate mode ... right now it just
uses seconds ... I know hertz isn't in time, for instance, but beats is and seconds are."*

Correct on both counts, including the doubt. **Hz and BPM do not apply to either of these
plugins**, because neither has a *rate* — both have **durations**. A duration's two honest
units are seconds and beats, and that is the whole choice.

### The control

Per **R13**, sync is not a unit, so it is not an entry in a unit picker:

```
Sync to host      {Off, On}
```

One switch, and **no `Rate mode` enum** — a unit picker with one entry (Seconds) would be
a control that cannot be set. This is R13 applied exactly, and it comes out smaller here
than in Womb because there is only ever one unit to leave.

**No `Host sync target` selector either, and this is the part worth reading.** R11 pairs
the selector with `Every N beats` for plugins whose rates are expressed *as rates* — Womb's
heart is a BPM, so it needs somewhere to say how many beats one beat-of-the-heart takes.
**Passage's four slot timings are** durations already. Under sync they are simply **read as beats**, exactly as
Womb's four breath sliders are, and their sum is the cycle by the same rule. There is
nothing left for a selector to select.

Womb's built shape confirms this rather than contradicting it: its `Host sync target` has
**one** option, `{Heart rate}` — the only thing in the plugin expressed as a rate.

### What changes unit, and what deliberately does not

| control | when Sync to host is On |
|---|---|
| Slot fade in, Slot hold, Slot fade out, Slot gap after | read as **beats**; their sum is the slot's cycle |
| Drift period | unchanged — already in its own musical unit |
| Ramp duration, Ramp start delay | unchanged — a wall-clock wind-down, suite-wide |

Ramp is the wind-down you set in minutes because you are going to sleep. Tying it to the
project tempo would be answering a question nobody asked.

### Naming, and the rule it obeys

Every affected slider says so in its own name — `Slot fade in (sec / beats when synced, per slot)` — per the standing
rule that a control may never change what it means without saying so on the control
itself. The switch is named in the label so the two read as a pair.

The labels get longer, which the layout above otherwise works to avoid. That is the cost
of the rule and it is worth paying: a silent unit change is the failure this suite has
already been bitten by.

### Entering and leaving are both silent

On the switch, the affected values **convert** at the current tempo, so the sound does not
change at the moment you flip it — the same behaviour Womb's Host x has. Only the unit
you are typing in changes.

### Migration

**None.** `Sync to host` is a new slider defaulting to Off, and every existing project
keeps reading in seconds. It is the append case, and it costs nothing.
