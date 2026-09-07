# Polyrhythm Phase v3 - authored layout

Written by hand 2026-09-07, not generated. **Authored BEFORE anything is built.**
Supersedes the first draft of this document (a flat 96-slider reorder), which is
in git history if the reasoning is ever wanted.

**Status: BUILT AND MIGRATED 2026-09-07. THE MIGRATION IS HEARD AND GOOD; THE
NEW CAPABILITIES ARE NOT.**

Rozaya opened `shapes` the same day -- *"Nothing sounds off which is nice"* --
which confirms the 8 instances on real work. It does not touch the new
controls, all of which default to no-change.

Built exactly as authored below -- 56 sliders, the twelve-control voice block,
`All` at position 0, Solo, the pan's own rate mode, and the six drift/ramp
controls. All 8 instances across 5 projects migrated; the verifier ran 1176
name-driven checks with 0 failures. `tools/polyv3_migrate_layout_20260907.py`
and `tools/polyv3_verify_layout_20260907.py`; snapshot at
`E:/reaper/finished/backups/snapshots/_pre-polyv3-layout-20260907/`.

**Two things changed from the table below during the build, both small:**

- The voice block writes on CHANGE rather than capturing wholesale. The
  ordinary nested-selector shape copies the visible sliders into the current
  target on every @slider pass, which with an `All` position would flatten all
  eight voices on any stray pass -- including the ones REAPER fires with default
  values mid-load. Change detection removes that, and removes the need for a
  save-on-switch step as well.
- The migration seeds `Voice` to **1**, not to its declared default of `All`. A
  fresh instance has eight identical voices so `All` is harmless there; a
  migrated one has eight configured voices, and parking on `All` would mean one
  stray nudge writes across all of them.

**What is still owed:** an ear test, and the v1 -> v3 crossing (its own job, as
the migration notes below say).

**Scale.** v3 has **8 instances across 5 projects**. v1 has **84 across 17** and is
NOT touched by this job - it crosses later, once, and then retires.

## The brief, in Rozaya's words

Asked what actually bothers her about the plugin: *"I haven't touched polyrhythm
since every n beats and n per beat got introduced and then I stumbled on them...
So in practice, the thing that bugs me most is that the orders are scattered as
shit."*

And on the voices: *"say I fuck up the fifth voice, but then I don't know which one
I fucked up. that's kinda difficult to determine with the sliders being the way
they are... Is there a better design that would lead to less tabbing and less of me
having to, like, wear out my hand trying to air through the p list?"*

## The answer: the voices go behind a selector

**48 per-voice parameters become 8.** One `Voice` selector, then that voice's own
controls. The other seven voices keep playing; their values live in the plugin's
memory, exactly as Drift and Ramp targets already do here.

**90 sliders become 56**, which is also under the 64-slider boundary where a REAPER
value line grows a quoted marker - so this removes an entire class of file-format
trap from the plugin's future as a side effect.

### We built this once and archived it, and that does not bind us

Rozaya remembered: *"Feels like we did, then ditched it. I don't remember why we
did but it feels important."* She was right. **Melody Phase v2** collapsed forty
flat per-voice sliders behind a Voice selector and is archived.

**Two things killed it and only one is about the design:**

- **It could never gain a user.** Its per-voice data lived in a `@serialize` blob
  with no path across from v1's slider line, so it had **zero projects, ever**. The
  archive note calls it *"the better-looking design"*.
- Rozaya called the selector **overkill for that plugin**: *"that was my fault
  because I got overeager one day."*

So the design judgement was made about a version nobody was ever able to run -
including her. It is not evidence from use. What IS evidence from use is what she
said this week about the plugin she does run.

**The difference here: no fork.** This is built into v3 in place, with a migration,
which is the thing whose absence killed v2.

## Voice = All, and why it is not optional

Once per-voice is cheap, setting things UNIFORMLY becomes the expensive case -
arrowing the selector 1 to 8 and setting the same waveform eight times. That trades
one hand-wearing problem for another, and it is the design tell already written
down: *when a control needs a tool or a ritual to be usable in bulk, its
granularity is wrong.*

So the selector's first position is **All**. Park it there, move a control, every
voice takes it. "All sine except voice five" is two moves, not eight.

## Solo this voice

One slider, and the direct answer to *"I don't know which one I fucked up."* Step
the selector through the voices with Solo on and the broken one announces itself.
Today there is no way to hear one voice alone without switching seven others off
and back on again.

## What this unlocks, which is the real prize

Rozaya: *"At that point, it's trivial to make most controls per-voice."* Correct,
and it is the argument for doing it at all.

**A per-voice control costs 8 parameters today and 1 behind a selector.** So the
things the plugin has wanted and could not afford become affordable:

- **Per-voice waveform** - asked for directly, and nearly free in the engine:
  checked in the source, the waveform chain is already INSIDE the per-voice loop
  and already indexes that voice's own phase and gain. Only the waveform NUMBER is
  global.
- **Per-cycle waveform changes** - the tremolo already silences each voice for part
  of every cycle, so a switch made in that silence cannot click.
- **Per-voice tremolo shape: Depth, On Duration, Attack % and Release %.** Agreed
  with Rozaya 2026-09-07. Today the voices differ in pitch, rate and phase but
  share ONE envelope, so the plugin makes one kind of sound played in a pattern.
  Per voice, a shallow near-continuous voice becomes a bed while a hard short one
  becomes a blip on top of it; a long swell drifts through a fast tick. On Duration
  is the big one -- a voice on for 90% of its cycle is a pad, one on for 10% is a
  rhythm, and right now everything is one or the other together.
- **The two envelope CURVES and the four timbre controls stay global**, also agreed.
  That is where the refinement lives; Depth and On Duration are where the identity
  lives. Four extra per-voice sliders instead of eleven.

### No "follow the global" sentinel, and no global copies either

The first draft gave each per-voice override a `-1 = follow the global` value. That
is unnecessary and was removed: **`Voice = All` IS the global.** Park the selector
there, move Depth, all eight take it -- so the separate global copies of Waveform,
Depth, On Duration, Attack % and Release % simply move INTO the voice block and
stop existing twice.

No sentinel, no hidden follow-state, no control that behaves differently depending
on a value you cannot see. The slider count goes DOWN rather than up.

**What `All` shows when the voices disagree:** voice 1's value. Reading is
approximate; writing is exact and hits all eight. That is the honest version of a
multi-select control, and it matches the rewrite behaviour Rozaya asked to keep in
Womb -- you see the result of what you did.

## The order

56 sliders. Global first, then the voices behind their selector, then pan,
direction, transport, drift, ramp. **The per-voice block is thirteen controls** --
the selector and twelve.

| new | control | from |
|---|---|---|
| 1 | Tremolo Mode | 1 |
| 2 | Rate Value | 3 |
| 3 | Rate Mode | 2 |
| 4 | Attack Shape | 8 |
| 5 | Release Shape | 9 |
| 6 | Tuning Reference Hz | 11 |
| 7 | Transpose (half steps) | 12 |
| 8 | Octave shift | 13 |
| 9 | Binaural Beat Hz (L/R offset) | 4 |
| 10 | Pulse Width % (50 = square) | 15 |
| 11 | Tone (Warm <-> Bright) | 16 |
| 12 | Edge | 17 |
| 13 | Movement | 18 |
| 14 | Body | 19 |
| 15 | **Voice** (All, 1-8) | NEW |
| 16 | Note | 26 |
| 17 | Fine tune (cents) | 27 |
| 18 | Drift / Rate | 28 |
| 19 | Phase Offset | 29 |
| 20 | Waveform | 14 |
| 21 | Depth dB | 10 |
| 22 | On Duration % of Cycle | 5 |
| 23 | Attack % of Cycle | 6 |
| 24 | Release % of Cycle | 7 |
| 25 | Gain dB | 25 |
| 26 | Active | 30 |
| 27 | Solo this voice | NEW |
| 28 | Pan Enabled | 20 |
| 29 | Pan Mode | 21 |
| 30 | Pan Spread % | 22 |
| 31 | Pan Base Rate | 23 |
| 32 | Pan rate mode | NEW |
| 33 | Pan Increment per Voice | 24 |
| 34 | Cycle Steps (per-cycle modes) | 90 |
| 35 | Pan Glide ms (0=instant) | 89 |
| 36 | Direction & Reverse | 73 |
| 37 | Reverse Drift Offset | 74 |
| 38 | Start delay (in rate mode units) | 75 |
| 39 | Play for (cycles) | 76 |
| 40 | Rest for (cycles) | 77 |
| 41 | Drift target | 78 |
| 42 | Drift up amount | 79 |
| 43 | Drift down amount | 80 |
| 44 | Drift period | 81 |
| 45 | Drift period unit | NEW |
| 46 | Drift shape | 82 |
| 47 | Drift play for | NEW |
| 48 | Drift rest for | NEW |
| 49 | Ramp target | 83 |
| 50 | Ramp by | 84 |
| 51 | Ramp time unit | NEW |
| 52 | Ramp duration | 85 |
| 53 | Ramp play for | NEW |
| 54 | Ramp rest for | NEW |
| 55 | Ramp engage | 86 |
| 56 | Ramp start delay | 87 |

**Where the other 42 went:** V2-V8's per-voice sliders (old 31-72) are not sliders
any more - they are bank values reached through the selector. Old **88** is the
already-dead `Host ratio` picker and is simply dropped.

## Migration notes - and the hard part is NOT this migration

**v3's own 8 instances are easy.** Their V1 values stay on the slider line as the
selector's editing slots; V2-V8's values move from the line into the blob. 8
instances, and the blob format is known.

**The hard part is the v1 crossing, later, and it is exactly what killed Melody
v2.** v1's 84 instances hold 40 per-voice values each on the slider line, and they
have to end up in a `@serialize` blob. CLAUDE.md currently says v1 and v3 blobs are
*byte-identical, which is what makes the v1 -> v3 migration tractable* - **that
stops being true the moment this lands, and that line must be updated in the same
commit.**

**Why it is tractable now and was not in June:** the blob is a stream of float32s
whose layout is fully known and has been decoded from real projects twice this
week; `tools/rpp_sliders.py` handles the value line; and the verifier discipline
now in use - decode what was written back and check it against what the plugin
would load - did not exist here in June. Writing the stream is mechanical rather
than clever. **It should still be its own job, with its own authored conversion and
its own verifier.**

**Blob magic bumps** in the same commit as the build. The per-voice banks are new
and must appear in BOTH the `file_mem` list and the duplicate-fix block - a bank in
one and not the other is how Heartbeat nearly shipped settings that vanished on
save.

**The nested-selector gotcha applies in full.** Selector-plus-shared-config-sliders
silently zeroes the selected target on track duplicate unless `@serialize` forces
the visible sliders back from the bank on read. Required here on day one, not
later; the reference implementation is in `src/shepard-tone.jsfx`.

## What to check before believing it shipped

- **Simulate the pan rate in all five modes** with the two host modes asserted
  RECIPROCAL. The pan has never had a mode before, and the R21 reciprocal shipped
  inverted elsewhere precisely because a new mode was wired and never asked what it
  DID.
- **Duplicate the track** and confirm no voice is zeroed. That is the specific
  failure this pattern has.
- **Set Voice = All, move a control, and read back all eight banks** - the bulk path
  is the one nobody tests and the one that will be used most.
- **Verify the migration BY CONTROL NAME** against a pre-migration snapshot, and
  separately decode the written blob and check it against what the plugin loads.
- **Fix CLAUDE.md's R21 claim** (the pan modes did not land everywhere) and the
  byte-identical-blobs line, in the same commit.

## Open, and needing Rozaya rather than me

1. **Nothing.** The per-voice question was the last one open and it is decided:
   Waveform, Depth, On Duration, Attack % and Release % go per-voice; the two
   envelope curves, Pulse Width and the four timbre controls stay global. The
   layout above is buildable as it stands.
