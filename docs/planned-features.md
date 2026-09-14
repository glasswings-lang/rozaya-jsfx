# Planned features

Designs not yet built, and ideas kept for later. What a plugin already HAS is never
written here: `python tools/suite_status.py`. Built work was removed on 2026-09-13;
git history holds it, and the decisions it carried moved to `docs/backlog.md` (Settled)
and `docs/history/`.

## Transport and ramps, suite-wide (not built)



### Pause is not stop, and the song position is the clock -- suite-wide (Rozaya, 2026-09-11, not built; REAPER's side measured)

*"There's play, there's stop, and then there's pause. I say all plugins should respect a
pause. play/stop is play/stop, you'd expect that particular combonation to work exactly
that way."* So play after STOP restarts counters, drift, ramp; play after PAUSE resumes.
Read, not measured: Passage treats pause -> play as a play edge (`play_state == 1 || 5`
against the last state, ~1303 and ~1349), so it restarts. `jsfx_run` cannot pause yet
(playing or `--stopped` only). And its wider worry, all plugins: *"how it deals with
movement forward in time."* Asked what that covers: *"If I've moved forward in a project
by any means, or back by any means, manually, not by the progression of transport. I.E if
I've moved even a beat in, or maybe I've bumped the right arrow by accident or whatever. So
looping counts, rendering a section counts, anything."* Offered: land where it would have
been had it played from the start (delay over, drift and walk where they would be), or
start fresh from there. Rozaya: *"Yes, that."* -- read as the first, which was recommended.
**The rule, in positive words Rozaya accepted:** *"Wherever you are in the project, the
plugin sounds like that moment of the song, playing or stopped"* / *"The song position is
the plugin's clock."* Shape offered: an always-running own clock, re-landed on every
position jump, so moving the cursor while stopped is heard at once. It must NOT need play
pressed -- the reverted Melody attempt (`dcfeead`) did, and Rozaya: *"At that point it
becomes about as difficult to work with as any audio item."* It supersedes "play after
stop restarts". Evidence: Rozaya heard Melody respond to cursor movement.
**MEASURED in REAPER, 2026-09-12** (`tools/probes/position_probe.jsfx` through the bridge,
claude test, track monitoring on, "run FX when stopped" on): REAPER re-runs @init on play,
on a jump while playing, and on RESUME FROM PAUSE -- not on a loop wrapping. While paused a
plugin gets no blocks at all (it never sees play_state 2). After a stop the plugin keeps
running, and a cursor move while stopped reaches it at once (play_position = cursor, beat
follows) with NO @init. So the rule is buildable: keep memory through @init (ext_noinit),
and re-land on any position jump, stopped or playing. Bypass then enable also re-runs @init;
monitoring and mute toggles do not. The Morpher's and Passage's silent load (a real cause,
FIXED 2026-09-12) is in `docs/history/session-log.md`, 2026-09-11/12. **Still unexplained:** a probe
freshly added while stopped got no blocks until the first play, in a just-made tab and a
just-reopened project; after one play everything ran. Guess, untested: a freshly opened
project runs nothing while stopped until the first play. Test by probing claude test right
after Rozaya opens it (Rozaya does not press play there). **A loop wrap is a jump with no @init** (measured 51.74 -> 50.62 s), and
Rozaya: looping counts. So re-landing must come from WATCHING THE POSITION (Melody's
predicted-versus-actual check), never from @init or a play edge alone.
`tools/lock_test.py` covers only tempo-synced plugins starting mid-song.

### More than one Ramp -- suite-wide (Rozaya, 2026-09-12, being designed, nothing built)

Rozaya: *"I noticed we only have one ramp. That's great for sleep. That's not so great for
waking."* Eight ramps behind a Ramp selector, each with its own shape, engage and time
unit. Everything settled and still open: `docs/layouts/multi-ramp.md`.

### A bar-shape change lands on the next click (Rozaya, 2026-09-11, not built)

Rozaya noticed drift on the bar length seeming to wait for the end of the bar, and:
*"if you've got 20 beats per bar and it drifts down to 4, where are you? ... I'd think
it should start reaching for the current bar shape on the next click, treating the
previous one, before drift said hey your bar's 4 now as like... the last beat on the
one of 20. even if it wasn't."* So: the click just heard closes the old bar, and the
next click is the one of the new shape. Rozaya: *"You can't have half-beats ... but
that doesn't mean you can't have it readjust in the silences between beats."* **Unasked:** does a bar that GROWS (4 to 20)
also restart, or carry on counting? **Unchecked:** whether what it heard is `Drift
movement` on `With the target` (steps once per bar by design) or the bar edit that
waits for the downbeat (`rhythm_r24_verify_20260911.py`). Pairs with Tempo changes
landing at once, 2026-09-11: *"a tempo change is meant to be a tempo change, not a
delayed tempo change."*



---



## Deferred for separate planning



Mentioned in the design session but explicitly deferred to keep current scope manageable:



- **A deploy/sync script for the REAPER effects folder, with pruning (captured 2026-07-28).** Plugins are hand-copied from `src/` into `<REAPER resource>/Effects/glasswings/`. Copying never *removes* anything, so a renamed plugin leaves its old filename behind as a working-but-frozen twin — and it keeps showing up in the FX browser under a name that reads as a real, distinct plugin. This actually bit: `spectral_vowel_morpher_v2.jsfx` sat there for three days after the Passage rename, identical to Passage bar its `desc:` line and one comment, and got loaded and played in preference to the plugin that was actually being updated. A script that copies every `src/*.jsfx` and then *deletes* anything in the target folder that `git ls-files` doesn't know about would have caught it at the next deploy. **The obvious rule is wrong and would destroy projects — do not write this from "not in `src/` means dead".** An audit on 2026-07-28 found two orphans in the effects folder that are indistinguishable from outside (installed, absent from `src/`, mtime lagging their siblings) and want opposite treatment: `spectral_vowel_morpher_v2.jsfx` was a rename artifact with zero users, while `melody_phase.jsfx` is Melody Phase **v1** — byte-identical to `archive/versions/melody_phase/v1.jsfx` and still loaded by five projects, because v2 shipped as a separate plugin rather than replacing it. A first draft of this note proposed gating deletion on "has the repo ever owned this file" (`git log --all --diff-filter=A`); that check passes for melody_phase and would have deleted it. So the gate has to be, in order: (1) skip anything matching a file under `archive/versions/`, (2) scan the project folders for references and skip anything still used, (3) `--dry-run` by default and require confirmation. Rozaya's summary of the near-miss — *"and this is why I don't trust scripts"* — is the right instinct: the hazard is not automation, it is automation encoding an assumption nobody tested. Detection tell in the meantime: an orphan's mtime lags its siblings'.



- **"Rest between voices" macro for Melody Phase** — a pan-mode-style global mode + per-voice increment for automatic rest distribution across voices. The existing per-voice "Note duration" + "Next voice in" sliders already cover the underlying mechanism (set Note duration < Next voice in to get silence between voices); the macro would be a shortcut for setting up uniform rest patterns without going voice-by-voice. Needs its own design pass — what modes, override semantics, etc.



---



## Spectral Vowel Morpher -- slot patterns via a TEXT FILE (not built)

**Caveat added 2026-07-05:** same chord/clash limit as 2b applies — stepping a pattern between captures at *different pitches* stacks/juxtaposes different chords. Fine as *sequential* motion (like Drift/Glide, one capture at a time), NOT as simultaneous blend. The accessible-pattern mechanism itself is still sound; just frame it as sequencing the morph *target*, not layering slots.

**The accessibility wall (confirmed):** JSFX sliders are numeric / enum only — there is no text-string slider — and an `@gfx` text box has NO accessibility tree, so NVDA can't see it and it never appears in the parameter list. Typing a pattern *into the plugin* is off the table for a screen-reader user.

**The sideways fix — read the pattern from a `.txt` file.** JSFX can read text files (`file_open` + `file_string`), and a file-picker slider (`sliderN:/folder:default:Name`, the Sustain Looper idiom) IS NVDA-navigable.

- Pattern lives in a `.txt` (e.g. `1 3 2 4 1 1 3`) the user types in **Notepad** (fully accessible) and drops in a patterns folder.

- Plugin file-picks it; on change, read + parse the slot indices into an array; step through them on the clock (`0` = rest/hold).

- The user "types into a box" — just Notepad's, not the plugin's — sidestepping the string-slider wall entirely. Bonus: the kin_bridge can also inject a pattern live.



Same family as Polyrhythm Phase's per-voice sequencing. All three compose into a capture "sampler/sequencer," dyscalculia-clean: Random needs no numbers; the file-pattern is typed in an accessible editor, never dialed on a slider.



---



## Loop-slot player — "sustain looper × morpher slots" (feasibility, captured 2026-07-10)



**Rozaya's question:** a plugin that plays LOOPS the way the morpher handles capture slots — slot-style randomness, multiple loops at once — borrowing from both Sustain Looper (WAV loading, crossfade-loop, ensemble) and Spectral Vowel Morpher (multi-slot store, shuffle-bag, auto-morph/drift between slots).



**Feasibility: high.** Every building block already ships in the suite; this is a *recombination*, not new DSP.



- **Multi-loop storage** — the morpher's per-slot memory pattern (`slotraw[NSLOTS*LEN]`, running-allocator memory map) but filled from WAVs via Sustain Looper's file-selector idiom (`sliderN:/glasswings_samples/…`, `file_open`/`file_riff`/`file_mem`, reload only when `sliderN|0` changes). N file-selector slots, each pre-loaded at init.

- **Slot randomness** — lift the morpher's `shuffle_bag` + auto-morph modes **verbatim in spirit**: Off / Sweep / Glide once / Shuffle (random-order, even coverage, no immediate repeat). That's "handle loops the way slots are handled."

- **Seamless switching** — pre-load ALL slots at init, then randomize among *already-loaded* buffers so switching is a click-free equal-power crossfade (morpher's direct A→B crossfade, or Sustain Looper's crossfade-loop machinery). Only changing which *file* occupies a slot has a load hitch — so keep the slot set fixed during play, randomize selection/pitch/timing freely.

- **Extra randomness dimensions** (the "randomness, basically") — random pitch/detune per pick (Dapple's Pitch spread), random start offset into the loop, random dwell before the next switch. All cheap per-event RNG (Park-Miller, per the LCG gotcha).

- **Ensemble + Drift/Ramp** fall in for free — Sustain Looper's true-detune voices per slot; the suite Drift/Ramp system on switch-rate / pitch / level / crossfade-time.



**Two shapes to pick between:**

1. **Multi-slot loop player** (recommended) — N fixed file-selector slots, shuffle/morph/drift/crossfade between them. Cleanest; a direct "Sustain Looper that holds several loops and wanders between them."

2. **Folder-shuffle player** — point at a folder, randomly pull files each cycle. More generative but needs double-buffered background loading to switch files without a hitch (JSFX loads are load-time, not real-time) — meaningfully harder; option 1 gets ~90% of the feel with none of the loading risk.



**Constraints:** memory budget (~80 s stereo default, 32 M = ~5.5 min via `options:maxmem`) means *short* loops — fine for the intended use. WAV/OGG only (FLAC/MP3 unreliable — see CLAUDE.md sample-loading gotcha). Loop STEADY material or the loop seam telegraphs (Sustain Looper's lesson).



**Verdict:** a genuinely new, coherent plugin that's mostly assembly of proven parts. Good candidate for a focused build session. Open question for Rozaya: option 1 vs 2, and how many slots (morpher settled on 8).



## Getting captures out of (and into) REAPER project files (captured 2026-07-27)



**Where this came from.** A slider renumber broke five saved projects, and the

repair turned out to be a plain-text edit of one line per plugin instance —

because a JSFX `@serialize` blob is a raw memory dump with no notion of slider

numbering, so it survives anything done to the slider list. Decoding one to prove

that also proved the format is *fully* understood: the layout consumed exactly

every float in the blob, none left over. Rozaya, on realising what that implies:

*"I have a weird feeling that suddenly I'll be wanting blobs for a lot more than

just featuring in soundscapes."*



**What is actually in there.** A Passage blob holds, per instance, eight slots ×

32768 samples of **raw captured audio** (mono float32 at project rate — about 5.5

seconds each), plus every per-slot bank. One 21-track project already carries

twenty instances: roughly 20 MB of recorded voice, existing nowhere else.



Ideas, roughly in order of value:



Built: listing and extracting slots (`tools/passage_captures.py`), and writing them back (`tools/passage_inject.py`). Still open:

4. **Generalise to the whole suite.** Nothing here is Passage-specific; every

   plugin serialises memory the same way. A generic dumper plus a per-plugin

   memory map would turn future migrations into text edits instead of

   redo-by-ear, and would make `@serialize` bugs inspectable rather than

   deducible.

5. **The weight problem.** Each Passage instance carries ~1 MB of audio, ~1.4 MB

   once base64'd into the RPP, and REAPER re-serialises all of it into *every

   undo point*. That is why a twenty-instance project is 30 MB and why editing it

   feels like wading. Captures-as-external-files would fix it, at the cost of

   projects no longer being self-contained — a real trade, not an obvious win.



**Constraint to respect:** reading is safe, writing much less so, and the blob

layout is version-gated on a magic number that has already moved four times

(7700001 → 7700004). Any tool must check it exactly as the plugin does and refuse

rather than guess.



---



## Random drift barely moves — three defects and one missing control (captured 2026-08-12)

Rozaya, playing Resonance Bank: Random drift on Pan *"start[s] from its current
position in the stereo field and mov[es] from there to something tinier-ly
different."* Correct, and it is not bad luck — it's the design. Four separate
things, in rising order of how much they matter.

### 1. Missing control: you can bound the territory but not ask for a journey

**This is the real one.** Drift up / Drift down set *where the value is allowed
to go*. Nothing sets *how far it travels each period*. Each period draws a new
ABSOLUTE target with `rand(2) - 1`, independent of where the value currently
sits — so the step size is whatever chance hands you.

The gap between two independent uniform draws has a **triangular distribution
peaking at zero**. The single most likely step is *no step*. Small moves aren't
an occasional failure, they're the default; large moves are the exception.
Roughly one period in five moves less than a tenth of the range, better than a
third move less than a fifth of it — and each of those costs a whole period,
which is minutes.

Two things compound it perceptually. Because targets are absolute rather than
steps, consecutive periods frequently double back (high, low, middling), so it
jiggles around the base value instead of exploring. And the interpolation is
linear across the whole period, so even a large draw is spread over minutes and
reads as slow creep rather than travel.

**Cheap fix (a couple of lines, no new slider):** force each new target into the
opposite half from the current one, with a minimum magnitude. Every period then
crosses centre and covers real ground. For Pan that means actually traversing
the stereo field instead of loitering on one side. Site:
`src/resonance_bank.jsfx:347`, and the equivalent in every ported plugin.

**Fuller fix (better, costs a slider in ~11 plugins):** a separate *travel*
amount — how far it moves per period — with Up/Down staying as bounds it
reflects off. Decide this one alongside the dyscalculia sweep; it's the same
question about what the numbers on a drift control should *mean*.

### 2. Cold start — Random gives one full period of NOTHING, every play (REGRESSION)

*(2026-09-13: v1 is archived. `src/polyrhythm_phase_v3.jsfx` still zeroes both at its
runtime reset, lines 588-589; whether the cold start remains is NOT measured.)*

`src/polyrhythm_phase.jsfx:557` zeroes `target_drift_prev[i]` and
`target_drift_curr[i]` in the RUNTIME reset. New targets are only drawn when the
phase WRAPS (`:1157`), so the first full period interpolates `0 + (0-0)*phase` =
flat. With a 4-minute drift period that's 4 minutes of no drift **after every
transport play** (`@init` re-runs per play). Random-only — Sine and Triangle
start moving immediately, which is exactly why it reads as "sometimes."

**Resonance Bank does NOT have this** — `src/resonance_bank.jsfx:173-175` seeds
`band_drift_phase` (via `rand(1)`), `band_rand_old` and `band_rand_new` on every
init. It was the reference implementation and it got this right; **the
2026-06-12 nested-selector sweep dropped the seeding on the way out.** So this is
a port regression, and it probably affects most sweep-era plugins — NOT audited
beyond these two yet (~10 quick greps to know).

### 3. A zero on one side kills a quarter of periods outright

`d_offset = d_mod >= 0 ? d_mod * d_up : d_mod * d_down`
(`src/resonance_bank.jsfx:358`, `src/polyrhythm_phase.jsfx:1176`). With
`down = 0`, any period whose old AND new targets both landed negative outputs
exactly zero for its entire length — 25% of periods, dead flat. Same for
`up = 0`. Fix: map the random value across the full Down-to-Up span so neither
half can be dead. Random only — changing it for Sine/Triangle would alter
existing projects.

### 4. Polyrhythm's targets all crest together

Polyrhythm zeroes drift phase for all 24 targets, so anything sharing a period
moves in lockstep. Resonance Bank scatters it per slot deliberately —
`src/resonance_bank.jsfx:166`: *"so the bands don't all crest together (matches
the original load-time seeding)."* That reasoning didn't survive the port
either, and it's part of why Resonance Bank's drift feels more alive.

**Ordering note:** 2 and 3 are bug fixes and are cheap. 1 is a design decision
and shouldn't be rushed. Do the fixes in ONE plugin and ear-test before porting
— that's what went wrong the first time.

## Custom drift shapes — breakpoint lists as a fourth Shape option (captured 2026-08-12)

Wanted: arbitrary drift/LFO shapes, e.g. for a sweep filter — *"sweeps up fully,
down fully, up halfway then holds, then the rest of the way."* Currently only
reachable by drawing an automation envelope, which is the thing the whole suite
exists to avoid (see "Why this exists" above).

**Data model:** a breakpoint list. Each segment has a target level, a duration,
and a curve. "Hold" is just a segment whose target equals where it already is.
That's all of it.

**The slider problem dissolves — this is the nested-selector pattern again.**
Segment selector + target level + duration + curve = **4 sliders for N
segments**, plus a fifth for how many segments are active so the loop knows
where to wrap. Slider count is decoupled from segment count exactly as it is for
drift targets, so there is **no hard segment limit** — the cap is however many
slots the bank allocates. 64 costs the same 4 sliders as 8.

**Where it plugs in:** Drift's Shape slider already reads Sine / Triangle /
Random. **Custom becomes the fourth option.** Nothing else in the architecture
changes — same per-target phase counter, same period slider setting how long one
pass takes, same offset consumed at the same site. One plugin working means every
drift target in it gains arbitrary shapes, and the port is mechanical. Unlike an
envelope it runs indefinitely, survives a tempo change, and travels with the
plugin instance.

**Unsolved half — sharing shapes.** A segment bank lives inside one instance. A
library ("twelve breathing curves") needs files. The file-selector slider from
`src/sustain_looper.jsfx` gives an NVDA-navigable dropdown of a Data folder,
which is the right interface. Whether JSFX reads TEXT files reliably needs
verifying (`file_string` exists; behavior unconfirmed). Bulletproof fallback:
ship shapes as tiny WAVs — one cycle of the curve, read via the exact mechanism
Sustain Looper already uses, indexed by drift phase — with a `tools/` script
compiling plain-text shape descriptions into them, so text stays the source of
truth and modders stay first-class.

**Cost, honestly:** new memory bank, `@serialize` version bump with the
count-encoded magic, the segment-selector save/restore dance, and the
track-duplicate fix in `@serialize`'s read branch. All have reference
implementations; it's four of them at once. Not an afternoon.

## Breath catches — the hitch on the way in, and on the way out

Captured 2026-08-31 with Star, out of the sigh discussion. **Not built. Decide after the
sigh's four segments are audible**, because it may absorb them.

### The observation

A sigh is not a big breath, it is **two breaths stacked**: an inhale, a tiny catch, then a
second inhale on top taking you past normal fullness, then a long passive exhale and a
longer settle. Physiologically this is the *augmented breath*, generated by its own neural
mechanism and literally described as a second breath begun at the peak of the first.

**The catch is the perceptual signature, not the size.** A single long smooth inhale is a
deep breath; the ear separates the two instantly. This is exactly why a duration
multiplier can never produce a sigh at any setting — it can only make the same smooth
inhale take longer, which is what "computery" meant (Star, 2026-08-31).

### The generalisation, which is the actually interesting part

A catch is not a sigh feature. It is a **breath** feature, and it belongs to both halves:

| where | how many | what it is |
|---|---|---|
| inhale | one, deep | a **sigh** |
| inhale | several, small | the **shuddering breath** after crying; fright; coming down from panic |
| exhale | several, small | the **stuttering sob** — the broken release |
| either | none | the breath as it is today |

One mechanism, four expressions, and three of them are currently impossible.

**Why this matters beyond realism.** Womb can depict calm, and it can depict fast. It
cannot depict **distressed** in any way a body recognises. A hitching inhale is probably
the single most legible cue for that — more than rate, more than depth — and dysregulation
is the axis the nervous-system-states work runs on
(see the Womb-for-nervous-system-states thread: dysregulated -> activated-coherent ->
resting-coherent).

### Implementation sketch — no new states needed

The tempting design is extra segments in the state machine (inhale, catch, inhale-2, ...).
That is the expensive route and probably the wrong one. A catch is a **momentary stall in
the segment's own progress**, not a new phase: hold the envelope briefly, N times, on the
way through an existing segment. The breath already has shaped fades, so this is a
modulation of the existing ramp rather than new machinery.

Controls, per half, in the units already learned:

- `Inhale catches` / `Exhale catches` — how many, 0 = off (today's behaviour)
- `Catch depth` — how hard each one stalls
- possibly placement (evenly spread vs weighted early/late)

### Why it may SIMPLIFY R15 rather than add to it

If a catch is an inhale feature, the sigh does not need a fifth segment for its stacked
second inhale — **a sigh becomes its own four segments plus one deep inhale catch.** That
would close R15's open question without new sections. Worth resolving in that order:
build the four sigh segments, hear them, then try a catch on the inhale, and only then
decide whether anything needs a fifth phase.

### Open

- Should catches be a **Drift / Speed Ramp target**? If so, ramping catches from four to
  zero over twenty minutes *is* the dysregulated-to-coherent journey, stated as one
  control. That is a strong argument for yes.
- Does the exhale catch want a different character from the inhale one? A sob is not a
  mirrored hitch — it tends to be more abrupt.
- No **amplitude** component exists anywhere in the sigh yet (carried over from R13a): a
  real sigh is a bigger breath, not only a longer one.

---

## A techniques page -- deferred, but the material is already arriving (captured 2026-09-04)

Not a plugin feature. A page (or a section of `docs/plugins/`) for **things you
can DO with these**, as distinct from what each control means. Rozaya: *"we need
a techniques page, but that can come way later."* Deferred on purpose -- it is
written down here so the entries stop evaporating in the meantime.

**Why it exists at all:** the first entry came out of an ear-test, and only
because Rozaya volunteered it after the fact. I had taken *"the ramp worked"* as
a pass/fail and moved on. Rozaya: *"the thing I was hearing was actually pretty
fucking cool... but I wasn't asked about that. I was just kinda taken as a
fucking briefing."* **An ear-test report is the only measurement anyone on this
project can take. Harvesting a yes/no out of it and discarding the rest throws
away the best input the suite has.** Ask what it SOUNDED like, every time.

### Entry 1 -- "ramp on one side, stairs on the other"

Rozaya's name for it, 2026-09-04, and it is exact: a ramp and a staircase in a
building rise the same height to the same landing and differ only in how they
cover the ground between. Same rise, same landing. That IS the invariant below.

Heard on Veil, 2026-09-04. Two filter cutoffs, both ramping 100 Hz -> 500 Hz over
the same span. One set to glide continuously; the other given **Ramp play 2 /
rest 2**, so it climbs in two-and-two steps to the same destination.
Rozaya: *"That was a cool fucking noise."*

**It requires the controls to be EVERYWHERE**, which is the general argument for
the propagation work: the trick only exists if two separate things can each do
both the smooth and the stepped version. A feature present in two plugins out of
fifteen cannot be played this way.

**Resolved 2026-09-04, and the mechanism is confirmed in the code, not guessed.**
Rozaya: *"I imagine it did its ramp in the bursts that it could. It didn't feel
like it was pulling apart. It would, then it'd catch up, then it would, then it'd
catch up."* That is exactly what `src/veil.jsfx` does. In `@block`:

```
sr_step = 1.0 / (srate * speed_ramp_dur_mem[i] * ramp_time_scale);
sr_pr_on ? sr_step *= (sr_pl + sr_rs) / sr_pl;
```

**The ramp keeps its total duration; play/rest changes its SHAPE, not its arrival
time.** During a rest the progress freezes; during a play burst it advances by
`(play+rest)/play` times the smooth rate -- at play 2 / rest 2, double speed. So
the stepped ramp falls behind, sprints, falls behind, sprints, and lands on its
destination at the same moment a smooth twin does.

**This invariant is why the technique works and it MUST survive propagation.** If
a plugin's play/rest merely paused the ramp without the speed compensation, the
stepped one would arrive late and keep drifting -- which is the 'pulling apart'
reading Rozaya explicitly did not hear. Two ramps arriving together, one smooth
and one in bursts, is the whole effect.

## Ranges left standing by the 2026-09-06 range sweep

* **Percentages that are genuinely proportions** — Attack %, Release %, Denoise,
  Depth %, Dry/wet, Tone vs noise, Timing randomness, Crossfade, Loop position,
  Capture point, Note length %, On duration %. 0..100 IS the range.
* **Pans at +/-100 and phase offsets at +/-180** — already the full span.
* **Volumes and resonances normalised to 0..1.**
* **Tone resonance Q (0.5..8)** — high Q self-oscillates. A real limit, and one to
  widen only with an ear on it.
* **Capture average (1..6)** — check it against the capture buffer's size first;
  it may be an array bound rather than a preference.
* **dB and semitones** — still held for a decision.

## Womb got repurposed as a noise source ONCE, and that is still a signal (2026-09-06)

Rozaya, on why it had `scattered.rpp` open at all: *"I was half-assed using
scattered for crashes, womb was the only place I could get different frequencies
of noise coming in like that."*

**Scope it honestly: this is ONE project, not how it uses Womb.** Asked about
the rest: *"At least with scatter. The rest... well. I try to use it like it was
meant for lol."* So Womb is not secretly a noise instrument and must not be
redesigned as one.

**What makes it worth recording anyway** is that it reached for it — a use found
rather than asked for is a real signal about what is MISSING elsewhere, even when
it happened once. Womb has three independent
filtered-noise layers with their own envelopes, frequencies and stereo:

- Bloodflow — noise through a resonant lowpass, swelling once per heartbeat.
- Breath — noise through separate inhale/exhale filters plus a high-pass and a
  post-filter, on a four-segment envelope.
- Both with their own play/rest gating, drift and ramp.

Nothing else in the suite offers that. Veil, Dapple and Bubbler are each one
character; breath_gen is one breath. **The gap is a noise instrument with several
independently-tuned bands swelling on their own clocks.**

**What this changes about the bloodflow offset**, which landed the same day: it is
not primarily an anatomical control. It is a way to stop two noise swells landing
on top of each other. Framing it as pulse transit time is true and beside the
point for how it is actually used.

**Not a job yet, and deliberately not scoped here.** Recorded so the next session
does not "simplify" Womb's three-layer noise engine toward the womb-sound brief in
its name, and so that if a noise instrument ever gets built, this is the
requirement it starts from. Ask Rozaya what it is reaching for before designing
one — the useful question is what the crashes need to DO, not which filters to
offer.

## Polyrhythm with a SAMPLE as its voice source — the reason it was abandoned no longer applies (2026-09-07)

Rozaya: *"sustain looper only loops samples. It doesn't do the tremolo with pitch
that polyrhythm does, and I think we tried to build it, failed, then I gave up."*

**We did try, and the reason it failed is recorded.** `archive/exploration/
polyrhythm_tremolo.jsfx`, archived `289e611` (2026-06-08):

> polyrhythm_tremolo decomposed the polyrhythm modulation from its bundled
> oscillator cleanly enough — basic plugin works on external input — but lost the
> per-voice semitones that make polyrhythm_phase musical, and getting that back
> requires a quality real-time pitch shifter on arbitrary input audio (its own
> non-trivial project).

**That reasoning is correct and it is about the wrong architecture.** It was built
as an EFFECT: audio streams in from outside, and pitching a live stream into eight
independent voices really does need a real-time pitch shifter.

**A sample LOADED INTO the plugin is not a stream.** It sits in memory, and eight
voices reading it at eight rates is eight interpolated read pointers — a sampler,
not a pitch shifter. `src/sustain_looper.jsfx` already does the hard halves: it
loads a WAV through a file-selector slider (`sliderN:/foldername:default:Name`,
then `file_open` / `file_riff` / `file_mem`) AND runs a true-detune multi-voice
ensemble off one buffer.

So the pieces exist in this suite and nobody has put them together. Polyrhythm's
polyrhythmic tremolo, its 16 pan modes, its per-voice drift and ramp are all
already per-voice; only the SOURCE would change.

**Status: PREDICTED, not proved.** Reasoned from the parts, not built. The known
constraints, none of them fatal:

- **Memory.** ~8 M slots per instance by default, about 80 s of 48 kHz stereo
  interleaved; 32 M with `options:maxmem=33554432`. Wants a short sample.
- **Loop points.** Sustain Looper's crossfade loop already solves this BY EAR,
  which is the accessibility win — no visual waveform matching.
- **Pitch moves like tape.** Faster is higher AND shorter. Fine for a sustained,
  loopable source; wrong for anything with an articulated attack.
- **Formats.** WAV and OGG are reliable; FLAC/MP3 are not guaranteed.

**Related and much cheaper: PER-VOICE WAVEFORMS.** Checked in the source — the
waveform chain is already INSIDE the per-voice loop and already indexes that
voice's own phase and gain (`osc_phase_l[i]`, `gain_l[i]`). Only the waveform
NUMBER is global. Per-voice waveform is one substitution plus storage; the engine
was built for it and nobody wired the control. A single-cycle wavetable read from
a WAV would drop into the same chain as one more branch.

**And per-cycle waveform CHANGES are nearly free of the usual problem.** The
tremolo already silences each voice for part of every cycle, so a switch made
during that silence cannot click.

**Note for whoever picks this up:** per-voice waveform makes it SEVEN controls a
voice, 56 flat parameters. Every per-voice feature makes the flat layout worse and
the nested-selector question more urgent. They are the same question.
