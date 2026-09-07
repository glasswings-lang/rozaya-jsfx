# Polyrhythm Phase v3 - authored layout

Written by hand 2026-09-07, not generated. **Authored BEFORE anything is built.**
Supersedes the first draft of this document (a flat 96-slider reorder), which is
in git history if the reasoning is ever wanted.

**Status: AUTHORED, NOT BUILT.**

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

**90 sliders become 57**, which is also under the 64-slider boundary where a REAPER
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
  global. **In this layout at 28**, with `-1 = follow the global` so nothing changes
  until it is used (the Morpher's per-layer-overtone pattern).
- **Per-cycle waveform changes** - the tremolo already silences each voice for part
  of every cycle, so a switch made in that silence cannot click.
- **Per-voice tremolo shape** (Depth, On Duration, Attack, Release and their
  curves) and **per-voice timbre** (Tone, Edge, Movement, Body) are the obvious next
  ones. See *Open* - they are NOT in this build, and that is a decision rather than
  an oversight.

## The order

57 sliders. Global first, then the voices behind their selector, then pan,
direction, transport, drift, ramp.

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
| 20 | **Voice** (All, 1-8) | NEW |
| 21 | Note | 26 |
| 22 | Fine tune (cents) | 27 |
| 23 | Drift / Rate | 28 |
| 24 | Phase Offset | 29 |
| 25 | Gain dB | 25 |
| 26 | Active | 30 |
| 27 | Solo this voice | NEW |
| 28 | Waveform (-1 = follow the global) | NEW |
| 29 | Pan Enabled | 20 |
| 30 | Pan Mode | 21 |
| 31 | Pan Spread % | 22 |
| 32 | Pan Base Rate | 23 |
| 33 | Pan rate mode | NEW |
| 34 | Pan Increment per Voice | 24 |
| 35 | Cycle Steps (per-cycle modes) | 90 |
| 36 | Pan Glide ms (0=instant) | 89 |
| 37 | Direction & Reverse | 73 |
| 38 | Reverse Drift Offset | 74 |
| 39 | Start delay (in rate mode units) | 75 |
| 40 | Play for (cycles) | 76 |
| 41 | Rest for (cycles) | 77 |
| 42 | Drift target | 78 |
| 43 | Drift up amount | 79 |
| 44 | Drift down amount | 80 |
| 45 | Drift period | 81 |
| 46 | Drift period unit | NEW |
| 47 | Drift shape | 82 |
| 48 | Drift play for | NEW |
| 49 | Drift rest for | NEW |
| 50 | Ramp target | 83 |
| 51 | Ramp by | 84 |
| 52 | Ramp time unit | NEW |
| 53 | Ramp duration | 85 |
| 54 | Ramp play for | NEW |
| 55 | Ramp rest for | NEW |
| 56 | Ramp engage | 86 |
| 57 | Ramp start delay | 87 |

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

1. **How many per-voice overrides to fold in NOW.** This build has one: waveform.
   The candidates are per-voice Depth, On Duration, Attack %, Attack Shape,
   Release %, Release Shape, Tone, Edge, Movement, Body and Pulse Width - eleven
   more sliders, all "follow the global" by default, so none of them changes an
   existing project. **Each one added later costs another migration**, which is the
   argument for deciding now rather than discovering the want in three weeks. The
   argument against is that per-voice envelopes change what the plugin IS, and that
   is a musical judgement rather than a layout one.
2. **Nothing else blocks.** The layout above is buildable as it stands.
