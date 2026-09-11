# Shepard Tone Generator

**Designed by Rozaya — Developed with Claude (Anthropic)**

---

## Overview

Shepard Tone Generator produces the Shepard-Risset glissando — a continuous auditory illusion of pitch that sweeps endlessly upward or downward without ever actually arriving anywhere. Unlike the Shepard Scale, which steps through discrete notes, this plugin sweeps continuously, producing a tone that feels like it is perpetually rising (or falling) through pitch space.

Up to eight simultaneous voices allow complex chord textures, counterpoint (voices moving in opposite directions), or polyrhythmic drift patterns. Each voice is an independent continuous sweep, rooted on a different pitch class.

The plugin generates no audio from an input signal. It is a pure synthesizer.

---

## Signal Architecture

Each voice maintains a stack of oscillators spread across a pitch window exactly as wide as the Octave Count setting. All oscillators in a voice sweep continuously in the same direction — upward or downward — at a rate determined by the Rate parameters. Each oscillator's amplitude is shaped by a fade-in / fade-out window: loud near the center of the pitch range, silent at the edges. When an oscillator sweeps out of the top of the window it wraps silently to the bottom and begins fading in again. Because the window width equals the oscillator spacing (always exactly one octave), wraps are always seamless.

All active voices are summed and normalized by active voice count and oscillator count each sample.

---

## Parameters

### Global Controls

**Drift Mode** `Synced / Independent`
Sets how per-voice sweep rates are determined.
- **Synced** — all voices share the global Rate Value as their sweep speed. Each voice's Drift slider adds a cents offset to its oscillators, creating subtle detuning without changing the underlying rate.
- **Independent** — the global Rate Value is ignored. Each voice's Drift / Rate slider sets that voice's sweep rate directly, in the units set by Rate Mode. Voices can sweep at entirely different speeds.

**Rate Mode** `BPM / Seconds / Hz / Every N beats / N per beat`

**The two host modes are the same idea from opposite ends, and both follow the
project tempo.** *Every N beats* means one cycle takes that many beats — `4` is
one per bar in 4/4. *N per beat* means that many cycles fit in a beat — `8` is
eight per beat.

They are reciprocals, so whichever you pick decides which end of your music is a
whole number and which needs a decimal. Slow, drifting, phase-music settings are
whole in *Every N beats*; dense, fast ones are whole in *N per beat*. They agree
exactly at `1`, which is one cycle per beat either way.

*(Renamed and extended 2026-09-05. `Host x` was the old name for `Every N beats`
and behaves identically; anything you had saved on it is untouched.)*
Unit for interpreting rate values. **Host x** follows the project tempo — see below.

### Host x — following the project tempo

In the first three modes the plugin holds its own absolute rate, and nothing in
it knows that another instance exists. That's fine until you want to change the
speed of a whole arrangement: nudging each instance by hand changes the
*relationships* between them, not just the pace, and layers that used to nest
start scattering. Restarting the transport can't fix that — restart resets
phase, not ratio.

**Host x** locks the sweep to the project tempo, and Rate Value there means
**beats per cycle**: 4 is one full sweep every four beats, 0.5 is two sweeps a
beat. **Bigger is slower** — the one mode where that is true, alongside Seconds.
Move the tempo and everything moves with it, in proportion.

This is **not** quantising — Rate Value stays a continuous number, so `3.7`
beats per cycle is exactly as reachable as `4`. That is the point: deliberately
unlocked relationships survive a tempo change just as locked ones do. 2 and 4
beats nest forever; 2 against 3.236 never resolves, and keeps not resolving in
the same way at any tempo.

Tempo changes apply live, including mid-playback. The sweep rate, the Play/Rest
cycle counter and Start Delay all follow. **Pitch does not** — a tempo change
moves the glissando, it doesn't transpose the tone.

> **Switching Rate Mode changes what Rate Value means, and nothing rescales it
> for you.** 0.5 is 0.5 BPM in BPM mode, and in Host x it is half a beat per
> cycle — two sweeps every beat, which is very fast. Set the mode first, then
> the rate.

**Rate Value (BPM / sec / Hz / beats per cycle)** `0.001-1000, default 0.5 BPM`
The global sweep rate, in the units set by Rate Mode. Only used in Synced mode. At 0.5 BPM, one full sweep cycle takes two minutes — appropriate for slow ambient use.

**Octave Count** `2-16, default 8`
The number of oscillator layers per voice and the width of the pitch window in octaves. Higher values produce a richer, denser texture. Also controls the spacing — oscillators are always exactly one octave apart regardless of count.

**Center Octave** `0-8, default 3`
The octave at the center of the pitch window. All voices sweep through a range centered here. Lower values produce a deeper, more bass-heavy texture.

**Fade In %** `0-100%, default 20`
The fraction of each sweep cycle spent fading in at the bottom of the pitch window. Lower values produce a sharper entry; higher values a longer crossfade.

**Fade Out %** `0-100%, default 20`
The fraction of each sweep cycle spent fading out at the top of the pitch window. Fade In and Fade Out together determine how much of the window is at full volume.

> If Fade In % + Fade Out % exceeds 100%, both are scaled down proportionally.

**Waveform** `Sine / Triangle / Saw / Golden TS / Golden SG / Golden GS / Bell / Wavefold / Half-sine / Phi-cascade / Phi Triangle / Phi Sine / Square / Pulse`
The oscillator waveform used by all voices simultaneously. Sine produces the purest Shepard illusion — fewer harmonics means a cleaner register-wrap. The richer waveforms (Bell, Phi-cascade, etc.) are available if you want the illusion to sit inside a more textured tone. See Polyrhythm Phase for waveform descriptions, including the back-compat note on the Golden / Phi family.

**Pulse width (%, 50 = square)** `1 – 99, step 0.1, default 25`
Duty cycle for the **Pulse** waveform — the fraction of each cycle the wave spends high before snapping low. 50 is a square wave and sounds identical to the Square slot. Narrower values get thinner and more nasal; wider values mirror the same character back the other way, so 25 and 75 sound alike. The default of 25 is deliberately off-square so Pulse sounds distinct from Square the moment you select it. The range stops short of 0 and 100, which would be silence and DC respectively.

Only meaningful when Waveform is set to **Pulse**, and hidden from the parameter list entirely on every other waveform.

**Binaural Beat Hz** `0-100 Hz, default 0`
Offsets the right channel oscillator frequencies by this many Hz, adding a binaural beat across all voices and oscillators simultaneously.

**Root Note** `C / C# / D / D# / E / F / F# / G / G# / A / A# / B, default C`
The global tonic. Per-voice Note sliders are interpreted as offsets from this value. Setting Root Note to D and a voice Note to E produces F# (D + a major second).

**Tuning Reference Hz** `20-2000 Hz, default 440`
The A4 reference frequency used to calculate all oscillator pitches. Changing it while playing retunes every voice at once.

**Fine tune unit (for every voice)** `Hz / Semitones / Cents, default Cents`
What every voice's *Fine tune* is counted in.


#### Why the multiplier went, and why nothing hides any more

A multiplier is a number you cannot hear without doing arithmetic against the
project tempo — `0.25` is not a speed, it is a sum you have to finish. Because it
was illegible, Rate Value had to be **hidden** in Host x and a menu of named ratios
shown instead; because it was hidden, entering Host x had to **stamp** a landing
value into it. That stamp is the bug that cost a session elsewhere in the suite,
where a saved project had its hand-set rate overwritten on every load.

Beats per cycle is legible on its own, so the chain unwinds: nothing hides, nothing
is stamped, and Rate Value is always visible showing the value it is running at.
(Suite rule R13-revised, 2026-09-02; converted here 2026-09-04.)

**Drift and Ramp amounts stay in BPM in Host x**, as they are in every other mode —
you say "wander by 10 BPM" and the plugin does the conversion. That needed care
here: adding a BPM amount to a beats-per-cycle number would move the wrong quantity
in the wrong direction, since more beats per cycle is *slower*. The amount is
converted and added to the resulting speed instead. The same oversight had shipped
in both Polyrhythms and was fixed the same day.

---

### Per-Voice Controls (Voices 1-8)

Each voice has eight controls: Note, Fine tune, Direction, Rate, Gain, Pan, Active, Solo. Voice 1 is active by default; Voices 2-8 are inactive.

**Vn Note** `C / C# / D / D# / E / F / F# / G / G# / A / A# / B`
The pitch class of this voice, relative to Root Note. Changing it while playing moves the voice straight to the new note.

**Vn Fine tune (in fine tune units)** `-1000–+1000, default 0`
A pitch offset on all of this voice's oscillators, in both drift modes, in the unit set by *Fine tune unit*. In cents it reaches ten semitones either way. It moves the pitch without moving where the octaves fade, which is a different sound from changing the note. Small values make voices beat against each other. It acts while playing.

**Vn Direction** `Asc / Desc`
Whether this voice sweeps upward or downward. Setting two voices to opposite directions creates counterpoint — one pitch class continuously rising, another continuously falling.

**Vn Rate (in rate mode units; 0 = holds still)** `-1000–+1000, default 0`
Independent mode only, and hidden in Synced mode. This voice's own sweep speed, in the units set by Rate Mode. At 0 or below the voice does not sweep at all: it holds as a steady chord of its note in every octave.

**Vn Gain dB** `-60–+6 dB, default 0`
Per-voice output level, applied before the voice is summed into the mix.

**Vn Pan** `-100–+100, default 0`
Stereo position of this voice. Negative values place it left, positive values right, 0 is center. Uses constant-power panning. The binaural beat is preserved across the pan field.

**Vn Active** `Off / On`
Enables or disables the voice. Inactive voices contribute nothing to the output and are excluded from normalization.

**Vn Solo (heard even when Active is off)** `Off / On, default Off` *(new 2026-09-10)*
When any voice is soloed, only soloed voices sound; solo more than one to hear
those together. A soloed voice is heard **even if its Active is off**, because you
solo something in order to hear it, and its controls stay visible while it is
soloed. The level count follows what actually sounds, so soloing one voice of
several keeps it at the volume it had.

### Start Delay

**Start Delay** `0–1000, default 0`

Silent for N units after playback starts, then the Shepard tone(s) begin normally. Units match Rate Mode (BPM beats / Seconds / Hz cycles), interpreted against Rate Value. Oscillator phases stay frozen during the delay so the illusion begins cleanly at delay-end rather than mid-sweep. Re-arms on every transport stop/start. 0 disables the delay.

### Play / Rest Gating (v2.1)

**Play for (cycles)** `0–1000, default 0`
**Rest for (cycles)** `0–1000, default 0`
**Rest mode** `Walk through / Freeze in place, default Walk through`

A cyclic gate over the continuous glissando. Voices play normally for **Play for** cycles, sit silent for **Rest for** cycles, then resume — the pattern repeats forever. Useful for breathing-room ambient where the sweep illusion is interrupted by silences.

The cycle unit is the same as Start Delay: Rate Mode units measured against Rate Value. At Rate Value = 0.5 Hz, "4 cycles" = 8 seconds; at 120 BPM, "4 cycles" = 2 seconds; at Rate Value = 2 in Seconds mode, "4 cycles" = 8 seconds.

The feature is **disabled when either of Play for / Rest for is 0** (the default). With both at 0, the plugin behaves as before; Rest mode has no effect when the gate is off.

**Rest mode** picks one of two behaviors for what the oscillators do during rest:

- **Walk through** (default): oscillators keep sweeping during rest, just silently. When rest ends, you hear the tone wherever the sweep happened to be — the position has shifted during the silent stretch. Preserves the "the glissando is always running, the gate just controls output" feel. Each play period starts at a different point in the sweep, so the resumed harmonic content varies cycle-to-cycle.
- **Freeze in place**: oscillators stop sweeping during rest, frozen at their current frequencies and phases. When rest ends, the tone resumes from exactly where it left off. Preserves the "pause and resume continuous motion" feel. Each play period starts where the previous one ended.

For short rests with slow sweep rates the difference between modes is subtle (small position shift). For long rests with fast sweep rates the difference is clearly audible — Walk re-positions the harmonics each cycle, Freeze always resumes at the pre-rest position.

**Anti-click**: the existing 8 ms per-oscillator gain smoother handles all rest entry / exit transitions. When rest starts, `target_gain` is forced to 0 and the smoother decays each oscillator's audio output to silence over ~40 ms. When rest ends, target_gain returns to its window-based value and the smoother ramps gain back up. Same mechanism that prevents clicks during normal sweep wraps.

**Independent drift mode**: the Play/Rest counter uses base_rate_hz (from the Rate Value slider) as its clock, regardless of drift_mode. So in Independent mode where each voice has its own rate, the gate still fires at the global Rate Value cadence — voices all gate on and off together even though their individual sweeps are at different rates. This matches Start Delay's behavior on this plugin.

**Transport behavior**: conventional. Stop silences; play re-initializes everything (oscillator positions, rest state, cycle counter) and starts fresh in its play period from cycle 0.

### Ramp (v2.14 nested-selector)

> **Added 2026-09-06.** These six controls existed in seven other plugins and not
> here, which is exactly the inconsistency the suite sweep exists to remove — a
> thing learned on one plugin should be true of all of them. This plugin had no
> saved projects at the time, so the sliders were placed in their proper
> positions rather than appended, and nothing needed migrating.

**Ramp time unit** `Cycles / Seconds / Minutes / Beats, default Minutes`
What the duration and start delay are counted in — one unit for both, so they
always mean the same thing as each other. **Minutes** is the default and is what
this block always did. **Seconds** is there so a thirty-second ramp can be typed
as `30` rather than as `0.5` minutes. **Cycles** counts this plugin's own cycles,
referenced against the rate *before* drift and ramp touch it, so a ramp cannot
alter its own clock. **Beats** follows the project tempo, live.

**Ramp play for** `0–1000, default 0` · **Ramp rest for** `0–1000, default 0`
Per-target, in ramp time units. Turns the smooth ride into a **staircase**: the
ramp advances for `play`, holds for `rest`, and repeats. Both zero is the smooth
ramp, which is the default.

The holds come **out of** the duration rather than extending it — the advancing
steps are made proportionally faster — so Ramp duration goes on meaning "you
arrive in about this long" however you set the staircase.

In-plugin one-time morph over time, without automation. As of v2.14 Ramp is nested-selector (same shape as Drift) and reaches the **same eleven targets as Drift** — the global Rate Value, each of the 8 voices' sweep rates, Fade In %, and Fade Out %. It is **fully per-target**: each target has its own `by`, its own duration, and its own start delay, so different targets can wind down over different timelines from a single engage. Only **engage** is global.

**Ramp target** `40 options, default Rate value`
The same list as Drift target. Switching it saves the current values into the old target and loads the new one's.

**Ramp by (slider 65)** `-1000 to +1000, step 0.001, default 0` (units match the selected target)
Signed delta in the selected target's own unit, applied over that target's duration. **0** = no change (safe default). For the rate targets (Rate Value + per-voice) the delta is in **the rate's currently-displayed unit**:

- Rate Mode **BPM**, Rate Value 60, `by -30` → ramps 60 BPM → 30 BPM (slower).
- Rate Mode **Hz**, Rate Value 0.5, `by -0.25` → ramps 0.5 Hz → 0.25 Hz (slower).
- Rate Mode **Seconds** (period), Rate Value 2, `by +1` → stretches 2 sec → 3 sec (slower).

So in **BPM and Hz modes, negative = slower**; in **Seconds mode, positive = slower** (longer period) — the same mode-direction rule as Drift, because the offset is added in the native unit before conversion. For **Fade In / Out** targets the delta is in percentage points. The audible pitch of any oscillator is NOT scaled — only the sweep rate. The Play/Rest cycle counter scales with the Rate Value ramp too.

**Ramp duration (slider 66)** `0–60 minutes, default 0` — **per-target.** How long the *selected* target takes to travel from its baseline to baseline + `by`. Each target has its own duration; a target with duration 0 does not ramp (so set a duration for every target you want to move). · **Ramp start delay (slider 68)** `0–60 minutes, default 0` — **per-target.** Wait this many minutes (after engage) before *this* target begins moving. Stagger targets by giving them different start delays. · **Ramp engage (slider 67)** `Off / On, default Off` — **global.** One switch arms the whole wind-down; every configured target then rides its own duration after its own start delay.

Engage is a freeze/resume gate (NOT a restart edge): while On, each target's clock advances 0 → 1 over its duration; while Off, all clocks freeze where they are and resume on re-engage.

Example (one engage): Rate Value `by -40`, duration 30 min, start delay 0; V3 Rate `by -10`, duration 8 min, start delay 12 min → on engage the master rate eases down over half an hour while V3 holds, then peels away 12 minutes in over its own 8-minute glide.

**Transport behavior:** every target's ramp clock resets to 0 on the transport play edge (via `@init`). That is the ONLY thing that resets the ramps — slider changes (engage toggle, selector switch, anything) don't.

**Migration to v2.14 (reorganization + renumber):** Ramp went multi-target and the block was reorganized so the target selector reads *above* the by/duration/engage controls it governs. Because REAPER orders sliders by ID (not file position), this required renumbering the Ramp block (now sliders 64–68) and the Drift block (now sliders 69–73). **Existing Shepard Tone projects lose their Ramp and Drift settings on upgrade** — both are off-by-default, and the tone sound itself (sliders 1–63) is untouched. Re-add the plugin instance for clean defaults, or re-enter your Ramp / Drift settings. *(Older history: pre-v2.14 Ramp was single-target Rate Value on slider 64; and pre-v2.8 it was a multiplier 0.1–4.0.)*

### Drift (v2.9 nested-selector)

> **Added 2026-09-06.** These six controls existed in seven other plugins and not
> here, which is exactly the inconsistency the suite sweep exists to remove — a
> thing learned on one plugin should be true of all of them. This plugin had no
> saved projects at the time, so the sliders were placed in their proper
> positions rather than appended, and nothing needed migrating.

**Drift period unit** `Cycles / Seconds / Beats, default Cycles`
What the period above is counted in. **Cycles** counts this plugin's own cycles —
which is exactly what the control did before this unit existed, and it follows
the rate for free. **Seconds** is wall clock, independent of the rate. **Beats**
counts the project tempo, so the wander follows the host rather than the plugin,
and it follows a live tempo change.

The period is measured against the rate **before** drift touches it, so drifting
a rate cannot modulate its own drift period.

**Drift play for** `0–64 periods, default 0` · **Drift rest for** `0–64 periods, default 0`
Makes the drift come and go instead of wandering forever. It drifts for `play`
periods, then **freezes exactly where it stopped** for `rest` periods, then
carries on. Both must be above zero or the gate is off entirely — which is what
`0` means, and why the default is "always".

It freezes in place rather than returning to centre, and that is the interesting
part: **the fraction of the play value chooses where it parks.** `x.25` parks at
the crest, `x.75` at the trough, and `x.0` or `x.5` at no change at all. So a
whole number parks at neutral every single time and is nearly inaudible, while an
awkward fraction is the one worth using — each freeze lands further round the wave
than the last, so `1.75` cycles through four different park points before
repeating and `1.2` through five. Setting only `Drift down` wastes half of them,
because every park on the positive half lands at no change.

Slow organic wander applied independently to any of eleven targets: the global Rate Value, each of the 8 voices' individual sweep rates, Fade In %, or Fade Out %. Each target can have its own drift configuration; all eleven drift in parallel. The selector chooses which target's drift you're currently editing — the others keep running with their last-saved configuration.

Same pattern as Womb v3's drift and the rest of the sweep, scaled up to the largest target list in the suite (shared with Ramp as of v2.14). Switching the **Drift target** selector saves the current sliders 70-73 into the old target's memory slot, then loads the new target's saved values. All eleven configurations persist across project save/load.

The per-voice targets are what make this plugin's drift special: with **Independent** drift mode and a different drift configuration on each voice, every voice wanders its own sweep rate on its own schedule — the voices breathe against each other, drifting in and out of phase. This is the continuous-glissando analogue of Polyrhythm Phase's per-voice character.

**Drift target** `40 options, default Rate value`
Every control that shapes the sound, in the order the controls appear: Rate value, Fade in, Fade out, Pulse width, Binaural beat, Tuning reference; then for each voice its Fine tune, Rate, Gain and Pan; then Play for and Rest for. A voice's Rate target only acts in Independent mode; its Fine tune target acts in both.
Picks which target's drift configuration sliders 70-73 reflect. Switching the selector saves and loads automatically — no live edits are lost.

**Drift up amount (slider 70)** `0.0–100.0, default 0` (units match target)
How far above the target's baseline the drift wanders at its peak. Units are the rate's current unit (BPM / Seconds / Hz) for Rate Value and per-voice targets, percent for Fade In/Out. The 0-100 range covers Fade fully and BPM-mode rate drift; in **Hz mode** you'll use the low end (e.g. 0.1-0.5), in **Seconds mode** small period offsets. 0 = drift off on the up side.

**Drift down amount (slider 71)** `0.0–100.0, default 0` (units match target)
How far below the baseline the drift wanders at its trough. Independent from Up — asymmetric wander supported. Either non-zero activates drift for the target; both 0 = drift off.

**Drift period (slider 72, cycles)** `0–1000, default 8, 0 = off`
How many glissando cycles one full drift wave takes for this target. All eleven targets use glissando cycles (paced by the global Rate Value clock) as their period unit, scaled by Ramp so the wave-per-cycle relationship stays constant under wind-down.

**Drift shape (slider 73)** `Sine / Triangle / Random, default Sine`
Wander waveform. Sine = smooth, Triangle = linear ramps with turnarounds, Random = value-noise interpolating smoothly between fresh random targets at each period boundary.

#### How rate drift composes (internal note)

Rate Value drift applies a global multiplier to the master sweep rate (affecting all voices proportionally), folded into the same `combined_scale` as Ramp. Per-voice rate drift applies an additional per-voice multiplier on top, relative to that voice's own reference rate (the Rate Value in Synced mode, or the voice's Drift/Rate slider in Independent mode). All rate offsets are converted to multipliers via a rate-unit ratio, so the **mode-direction asymmetry** is handled automatically: in BPM and Hz modes a positive offset speeds up; in Seconds mode (where the rate value is a period) a positive offset lengthens the period and so slows down.

#### Transport behavior (v2.9)

On every transport play press, drift cycle restarts: all eleven targets' phase counters → 0 (drift offset = 0 at the first sample, wanders out from there). Oscillators re-place to the window, Play/Rest gate resets. Drift CONFIG (up/down/per/shape values per target) is preserved across stop/play and across project save/load. Ramp progress also resets on transport play. This makes renders deterministic for Sine and Triangle shapes (Random remains non-deterministic per render by design).

#### Migration from v2.8

The old flat-drift block (musical_up/down/period, slow_up/down/period, drift_shape on sliders 68-74) was 7 sliders covering Rate Value only. v2.9 is 5 sliders covering 11 independent targets, reusing slider IDs 68-72; sliders 73 and 74 are no longer declared. Old project values get reinterpreted (selector defaults to Rate Value; non-zero amounts on sliders 69-70 will produce drift on Rate Value). After upgrade, reset drift sliders to defaults if you'd never configured the old flat drift, or reconfigure under the new nested-selector pattern if you had.

---

## Usage Notes

- **The illusion works because no single octave dominates.** The bell-shaped amplitude window ensures that as one oscillator fades out at the window edge, an identical one is fading in at the other edge. The listener perceives continuous directional motion with no anchor point.
- **Fade In and Fade Out control the crossfade quality.** At 20%/20%, the middle 60% of the window plays at full volume with 20% ramps at each edge. At 50%/50%, the entire window is one continuous crossfade — no hold at full volume, maximum smoothness.
- **Multiple voices create Shepard chords.** Enabling voices on different note intervals (e.g. C, E, G for a major triad) produces a sweeping chord where all voices move in parallel. Each voice can be panned independently for spatial spread.
- **Independent mode with different rates creates polyrhythmic sweep textures.** One voice sweeping at 0.3 BPM and another at 0.5 BPM will periodically converge and diverge in unpredictable ways.
- **Pan and binaural beats are complementary.** Unlike some other plugins in this suite, Shepard Tone's pan implementation preserves the binaural beat when voices are panned — the L/R frequency difference is maintained across the stereo field.
- **Root Note transposes the entire plugin at once.** Changing Root Note shifts all voices simultaneously by the same interval, making it suitable for automation-based key changes.

---

*Shepard Tone Generator is part of the Rozaya JSFX plugin suite.*
*Designed by Rozaya — Developed with Claude (Anthropic)*
*Designed by Rozaya — Developed with Claude (Anthropic)*
