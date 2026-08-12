# Full Feature Sweeping Filter

**Designed by Rozaya — Developed with Claude (Anthropic)**

---

## Overview

Full Feature Sweeping Filter is a resonant lowpass filter with a shaped LFO sweep, stereo phase control, wet/dry mixing, and an optional pan modulation system. The filter cutoff is driven by a gated LFO envelope with independently shaped attack and release curves — the same envelope architecture used in the Full Feature Tremolo — giving precise control over how the cutoff moves through the frequency range on each cycle. A wet/dry mix allows the effect to be blended with the dry signal.

The plugin processes incoming stereo audio.

---

## Signal Architecture

The LFO runs as a normalized phase per channel. Each cycle, the LFO output moves through an attack ramp, a hold-high region, a release ramp, and a hold-low region, all with configurable proportions and curve shapes. The LFO output (0-1) is mapped to the frequency range, then scaled by the Depth % parameter around the center frequency, so at less than 100% depth the sweep covers a narrower band centered between Low and High.

The resulting target frequency is converted to a filter coefficient using a linear mapping (`freq * 2 / srate`) and smoothed with a 3 ms lag before being applied to a two-pole resonant lowpass filter on each channel independently. The wet output is then blended with the pre-filter dry signal according to the Wet/Dry Mix.

Left and right channels have independent LFO phase counters. In **Independent L+R** mode both advance freely. In **Offset from L** mode the right channel phase is continuously derived from the left plus the phase offset.

---

## Parameters

### Filter Range

**Frequency Low Hz** `20-20000 Hz, default 500`
The cutoff frequency at the bottom of the sweep — where the filter sits when the LFO is at its minimum. If set higher than Frequency High, the two values are automatically swapped.

**Frequency High Hz** `20-20000 Hz, default 5000`
The cutoff frequency at the top of the sweep — where the filter sits when the LFO is at its peak.

**Resonance** `0.0-1.0, default 0.7`
Resonance of the lowpass filter. Higher values add a pronounced peak at the cutoff frequency, making the sweep more tonally distinctive. Values above 0.9 can produce self-oscillation on some material.

**Wet/Dry Mix** `0.0-1.0, default 1.0`
Blend between the filtered signal (wet) and the original unprocessed signal (dry). At 1.0 the output is fully filtered. At 0.0 the filter has no effect. At 0.5 both are equally present.

---

### LFO Rate

**Rate Value** `0.001-1000, default 2`
The sweep rate in the units set by Rate Mode.

**Rate Mode** `Hz / Seconds / BPM / Host x`

**Host x** makes Rate Value a **multiplier of the project tempo** rather than an
absolute rate — x1 = one sweep per beat, x2 = twice as fast, x0.5 = half. Move
the tempo and it moves with it, in proportion, so instances keep their
relationships instead of scattering. Rate Value stays continuous, so
deliberately unlocked relationships survive a tempo change too. Applies live.

**Host ratio (writes Rate Value)** `Custom / every 8 beats / … / 8 per beat` (default Custom)
Shown only in Host x. Writes the multiplier into Rate Value then gets out of the
way. **Custom** never writes anything, and is deliberately not "Free" — that
means free-running in sync UI, which the other three modes already are.

> **Fixed at the same time:** Start Delay was 60x out in both Hz and BPM modes.
> The conversion was written as if Rate Mode were `{BPM, Seconds, Hz}` (as in
> Melody Phase and Polyrhythm Phase) when here it is `{Hz, Seconds, BPM}`, so Hz
> got the BPM formula and BPM the Hz one. Seconds was always correct.
How Rate Value is interpreted.
- **Hz** — cycles per second.
- **Seconds** — period of one full cycle.
- **BPM** — cycles per minute.

**LFO Start Phase (degrees)** `-180 to +180, default 0`
Sets the initial phase position of the LFO when the plugin is first loaded or when this slider is moved. At 0, the LFO starts at the beginning of the cycle. This is a set-once control — adjusting it repositions both channel phases immediately, after which they run freely from that point. Useful for aligning the filter sweep to a specific position relative to other material or other instances of this plugin.


#### The cycle is positioned from the project, not from when you pressed play

In **Host x**, with the transport rolling, the plugin asks REAPER where it is in the song and puts the cycle there. Drop the playhead into the middle of bar 40 and the sweep is already exactly where it would have been if you'd played from the top — so it lands the same way at the same bar however you got there. That's the behaviour a tempo-synced effect is expected to have, and it's most of the reason to sync at all: a cycle that's the right *length* but starts wherever you pressed play still lands off the grid.

It also can't slowly drift out over a long session, and it follows seeking and looping for free.

Two exceptions, both deliberate:

- **Stopped or paused**, the project position isn't advancing, so it free-runs instead — otherwise it would sit frozen for anyone monitoring live.
- **Drift or Speed Ramp on the rate hands it back to free-running.** Positioning from the project answers "where would this be if it had run at this rate all along," which stops being the right question the moment something is changing the rate. There's no jump at the handover, and it stays free until the next transport start rather than lurching back onto the grid mid-play. Which is what you asked for anyway — putting drift on the rate *is* asking for it off the grid.

Every other rate mode is unchanged and still starts from zero on play.


#### Host x hands you the ratio list, not a multiplier

Switching Rate Mode to **Host x** lands on **1 per beat** and hides the raw rate number. The **Host ratio** list becomes the control you use — *every 8 beats, every 4 beats, 1 per beat, 2 per beat*, and so on — so setting a rate is picking a name, never working out a number.

Set Host ratio to **Custom** and the rate value reappears, with whatever it last held. That's the way in for ratios the list doesn't cover, which is most of the point of a multiplier rather than a note grid.

Two things this fixes. The rate slider's default was chosen for its own unit, so switching mode used to hand you a speed you never asked for — in the effects, a default of 2 meant *double time* the moment you selected Host x. And the picker sits at the far end of the parameter list (slider IDs can never be renumbered without scrambling saved projects), so you met the multiplier first and the cure last.

Landing on 1 per beat only happens when *you* change the mode. Opening a saved project leaves your rate exactly as you set it.

---

### Sweep Shape

**On Duration % of Cycle** `0-100%, default 50`
The proportion of each cycle during which the LFO is in its active (non-minimum) state, including attack and release time. At 50%, the filter sweeps up and back during the first half of the cycle and sits at the low frequency for the second half. At 100%, the sweep never rests at the low frequency.

**Depth %** `0-100%, default 100`
How much of the frequency range the sweep covers. At 100%, the sweep moves fully between Frequency Low and Frequency High. At 50%, it sweeps only the inner half of that range, centered between the two values. At 0%, the filter stays fixed at the center frequency with no movement.

**Attack %** `0-100%, default 0`
Proportion of the on-time spent in the attack ramp, where the cutoff rises from the low to the high frequency. At 0%, the filter opens instantly.

**Release %** `0-100%, default 0`
Proportion of the on-time spent in the release ramp, where the cutoff falls from high to low. At 0%, the filter closes instantly. If Attack % + Release % exceeds 100% of the on-time, both are scaled down proportionally.

**Attack Shape** `Linear / Cosine / Logarithmic / Exponential`
Curve applied to the attack ramp.
- **Linear** — straight ramp.
- **Cosine** — S-curve, gentle at both ends.
- **Logarithmic** — fast initial rise, slow finish.
- **Exponential** — slow initial rise, fast finish.

**Release Shape** `Linear / Cosine / Logarithmic / Exponential`
Curve applied to the release ramp. Same options as Attack Shape.

---

### Stereo

**R Channel Phase Offset degrees** `-180–+180°, default 0`
When Phase Mode is set to Offset from L, this controls the phase difference between the left and right channel LFOs. At 180°, the channels are in opposition — when the left filter is fully open the right is fully closed. At 0° both channels move in unison.

**Phase Mode** `Independent L+R / Offset from L`
- **Independent L+R** — both LFO phases advance freely and in sync.
- **Offset from L** — the right channel phase is continuously derived as the left phase plus the R Channel Phase Offset. Use this mode when a stable stereo phase relationship is needed.

---

### Pan Block

**Pan Enabled** `Off / On`
Enables pan modulation. When on, the post-filter signal is summed to mono and repositioned in the stereo field according to the active pan mode. When off, all pan sliders are hidden.

> **Note:** Enabling pan converts the output to mono before panning. The stereo content of the filtered signal is collapsed. Place this plugin accordingly in your signal chain.

---

#### Per-Cycle Pan Modes

These modes update the pan position once per LFO cycle. **Cycle Steps** controls the sequence length.

**Mono**
No panning. Signal stays centered.

**Alternating**
Alternates hard left and hard right each cycle.

**Alternating (Flipped)**
Same as Alternating but starting from the right.

**Distributed**
Steps evenly from left to right across the cycle count, then wraps back to the left.

**Distributed (Flipped)**
Steps evenly from right to left, then wraps.

**Distributed (Ping-pong)**
Steps left to right then reverses, bouncing between the extremes.

**Converging**
Starts at hard left, then alternates left and right positions stepping progressively toward center with each cycle.

**Converging (Ping-pong)**
Same converging pattern but reverses back outward after reaching center, then converges again.

**Diverging**
Starts at center, then alternates left and right positions stepping progressively outward toward the extremes.

**Diverging (Ping-pong)**
Same diverging pattern but reverses back inward after reaching the extremes.

---

#### Continuous Pan Modes

**Pan Sweep**
Pan position sweeps continuously from left to right at the rate set by Pan Sweep Rate and Pan Sweep Rate Unit, independently of the filter LFO rate.

**Pan Sweep (Flipped)**
Same as Pan Sweep but sweeping right to left.

**Linked Sweep**
Pan sweeps in sync with the filter LFO at a speed multiplied by the Filter Speed Multiplier. At 1×, one full pan sweep per filter cycle. At 2×, two sweeps per cycle.

---

#### Pan Parameters

**Pan Spread** `0.0-1.0, default 1.0`
Scales the pan range. At 1.0 positions reach hard left and right. At 0.0 all modes produce center.

**Pan Glide ms** `0-100 ms, default 5`
Smoothing time for pan position changes. Higher values trade sharpness for click-free transitions.

**Cycle Steps (per-cycle modes)** `2-32, default 8`
Number of steps in the pan sequence for per-cycle modes. Hidden for continuous modes.

**Pan Sweep Rate** `0.001-1000, default 2`
Rate of continuous pan sweep for Pan Sweep and Pan Sweep (Flipped) modes.

**Pan Sweep Rate Unit** `Hz / Seconds / BPM`
Unit for Pan Sweep Rate.

**Filter Speed Multiplier (Linked Sweep)** `0.125-8×, default 1×`
Speed of pan sweep relative to filter LFO rate, for Linked Sweep only.

### Start Delay

**Start Delay** `0–1000, default 0`

Pass-through for N units after playback starts, then applies the filter sweep + pan effect normally. Units match Rate Mode: BPM mode counts cycles of the LFO Rate Value, Seconds is literal seconds, Hz mode counts cycles of Rate Value. The dry signal flows through unchanged during the delay — silencing the output would mute the dry track too, which is rarely what you want for an effect. Filter and LFO state stay frozen during the delay so the sweep begins cleanly at delay-end. Re-arms on every transport stop/start. 0 disables the delay.

### Play / Rest Gating (v2.1)

**Play for (cycles)** `0–1000, default 0`
**Rest for (cycles)** `0–1000, default 0`
**LFO at rest** `Walk through / Freeze in place, default Walk through`
**Output at rest** `Pass-through / Silence, default Pass-through`

A cyclic gate over the filter sweep + pan effect. The effect is applied normally for **Play for** cycles, then enters its rest period for **Rest for** cycles, then resumes — the pattern repeats forever. Useful for rhythmic on/off of the filter: "filter sweep for 4 bars, dry for 4 bars, repeat."

Cycle unit matches Start Delay: Rate Mode units measured against Rate Value.

The feature is **disabled when either of Play for / Rest for is 0** (the default). With both at 0, the plugin behaves as before; the LFO at rest / Output at rest sliders have no effect when the gate is off.

**Click-free transitions.** The effect smoothly fades out on rest entry (and back in on exit) using the same ~3 ms smoother that handles the cutoff sweep. The filter coefficients and resonance state keep running through the rest period so the filter is "warm" and ready to re-engage cleanly — no transient when the effect comes back.

Two independent sliders shape what happens during rest:

**LFO at rest** — what the filter sweep + pan LFOs do during rest:

- **Walk through** (default): LFOs keep cycling during rest. When the effect resumes, the filter cutoff has swept to a different position — you hear the filter come back in at wherever the LFO landed.
- **Freeze in place**: LFO phases pause, frozen at their values at rest entry. When the effect resumes, the cutoff picks up from the same position. The rhythmic sweep pauses and resumes in lockstep with the gate.

**Output at rest** — what the audio output does during rest:

- **Pass-through** (default): dry signal passes through unchanged. Matches Start Delay's behavior on this plugin — silencing the input would mute the upstream track in the FX chain.
- **Silence**: wet+dry mix smooths to 0 over ~3 ms; the audio fades into silence rather than passing dry. Useful when you want the gate to act like a hard mute rather than a filter bypass.

The two sliders are orthogonal — all four combinations work. Walk + Silence keeps the filter sweeping internally while the audio drops out; Freeze + Silence pauses everything; Walk + Pass-through and Freeze + Pass-through are the two "filter bypass" flavors.

**Filter resonance state and cutoff smoother keep running across all four combinations.** Only the LFO phase advancement is frozen in Freeze — the actual filter math continues processing the input throughout rest. This avoids transients on rest exit, at the cost of the filter potentially having settled to a slightly different cutoff position than at rest entry (because the smoother chases the frozen cutoff target). For long rests with a slow smoother this matters little; for short rests the difference is imperceptible.

**Transport behavior**: conventional. Stop passes through dry; play re-initializes everything and starts fresh in its play period from cycle 0.

### Speed Ramp (v2.14 nested-selector)

In-plugin one-time morph over time, without automation envelopes. As of v2.14 Speed Ramp is nested-selector (same shape as Drift) and reaches the **same six targets as Drift** — Sweep Rate, Frequency Low, Frequency High, Pan Sweep Rate, Resonance, Wet/Dry. All six ramp in parallel; the selector only chooses which one the `by` slider is currently editing.

**Speed ramp target (slider 29)** `Sweep Rate / Frequency Low / Frequency High / Pan Sweep Rate / Resonance / Wet/Dry, default Sweep Rate`
Picks which target the `by` amount applies to. Switching the selector saves slider 30 into the old target's memory slot, then loads the new target's stored `by`. Sits at the top of the Speed Ramp block (above the controls it governs) — a v2.14 reorganization; see the migration note below.

**Speed ramp by (slider 30)** `-5000 to +5000, step 0.01, default 0` (units match the selected target)
Signed delta in the selected target's own unit, applied over the duration. **0** = no change. For the rate-type targets (Sweep Rate, Pan Sweep Rate) the delta is in **that rate's currently-displayed unit** (Hz / Seconds / BPM): in BPM/Hz modes negative `by` = slower, in Seconds mode positive `by` = slower (longer period). Frequency Low/High are in Hz (the ±5000 range gives up to ±5 kHz ramps); Resonance and Wet/Dry are 0-1 fractions (use the low end of the range).

**Speed ramp duration (slider 31)** `0–60 minutes, default 0` — **per-target** (v2.14): how long the *selected* target takes to travel from baseline to baseline + `by`; a target with duration 0 doesn't ramp. · **Speed ramp start delay (slider 33)** `0–60 minutes, default 0` — **per-target**: wait this many minutes after engage before *this* target moves (stagger targets by giving them different delays). · **Speed ramp engage (slider 32)** `Off / On, default Off` — **global**: one switch arms every configured target, each riding its own duration after its own delay. (Duration + start delay are saved/loaded per target by the selector, like `by`.)

Engage is a freeze/resume gate (NOT a restart edge): while On, each target's clock advances 0 → 1 over its own duration; while Off, all clocks freeze and resume on re-engage.

A ~100 ms smoother sits between the Rate slider and the audio so manual Rate tweaks don't click. The Linked Sweep pan mode (12) rides the Sweep Rate ramp since it derives from the sweep frequency; the two Pan Sweep modes (10, 11) have their own rate, which you can now ramp directly via the **Pan Sweep Rate** target.

**Transport behavior:** every target's ramp clock resets to 0 on the transport play edge. This is the ONLY thing that resets the ramps — slider changes (engage toggle, selector switch, anything) don't.

**Migration to v2.14 (reorganization + renumber):** Speed Ramp went multi-target and the block was reorganized so the target selector reads *above* the by/duration/engage controls it governs. Because REAPER orders sliders by ID (not file position), this required renumbering the Speed Ramp block (now sliders 29–33) and the Drift block (now sliders 34–38). **Existing Sweeping Filter projects lose their Speed Ramp and Drift settings on upgrade** — both are off-by-default, and the filter sound itself (sliders 1–28) is untouched. Re-add the plugin instance for clean defaults, or re-enter your settings. *(Older history: pre-v2.14 Speed Ramp was single-target Sweep Rate on slider 29; and pre-v2.8 it was a multiplier 0.1–4.0.)*

### Drift (v2.9 nested-selector)

Slow organic wander applied independently to any of six targets: Sweep Rate, Frequency Low, Frequency High, Pan Sweep Rate, Resonance, or Wet/Dry. Each target can have its own drift configuration; all six drift in parallel. The selector chooses which target's drift you're currently editing — the others keep running with their last-saved configuration.

Same pattern as Womb v3's drift and the rest of the sweep (target list now shared with Speed Ramp as of v2.14). Switching the **Drift target** selector saves the current sliders 35-38 into the old target's memory slot, then loads the new target's saved values. All six configurations persist across project save/load.

The two Frequency targets are what make this the most evolving of the filter effects: drift Frequency Low on one period and Frequency High on another, and the sweep band itself wanders and breathes — its edges moving independently, the center and width shifting over time. Layer a slow Resonance drift on top and the filter's character moves too.

**Drift target (slider 34)** `Sweep Rate / Frequency Low / Frequency High / Pan Sweep Rate / Resonance / Wet/Dry, default Sweep Rate`
Picks which target's drift configuration sliders 35-38 reflect. Switching the selector saves and loads automatically — no live edits are lost.

**Drift up amount (slider 35)** `0.0–5000.0, default 0` (units match target)
How far above the target's baseline the drift wanders at its peak. Units: the rate's current unit (BPM / Seconds / Hz) for Sweep Rate, Hz for the two Frequency targets, the Pan Sweep Rate's own unit for Pan Sweep Rate, a 0-1 fraction for Resonance and Wet/Dry. The 0-5000 range spans the frequencies (up to ±5 kHz wander); Resonance and Wet/Dry use the low end (e.g. 0.3), Hz-mode rates use small values. 0 = drift off on the up side.

**Drift down amount (slider 36)** `0.0–5000.0, default 0` (units match target)
How far below the baseline the drift wanders at its trough. Independent from Up — asymmetric wander supported. Either non-zero activates drift for the target; both 0 = drift off.

**Drift period (slider 37, cycles)** `1–1000, default 8`
How many filter LFO cycles one full drift wave takes for this target. All six targets use LFO cycles as their period unit, scaled by Speed Ramp so the wave-per-cycle relationship stays constant under wind-down.

**Drift shape (slider 38)** `Sine / Triangle / Random, default Sine`
Wander waveform. Sine = smooth, Triangle = linear ramps with turnarounds, Random = value-noise interpolating smoothly between fresh random targets at each period boundary.

#### Notes

- **Frequency Low/High drift is clamped to [20, 20000] Hz** and the band edges are re-ordered if drift crosses them — so a Low edge drifting above the High edge just swaps which one leads, rather than producing a negative-width band.
- **Pan Sweep Rate drift only affects pan modes 10 and 11** (Pan Sweep / Pan Sweep Flipped). Linked Sweep follows the filter rate, which Sweep Rate drift already moves.
- **Resonance and Wet/Dry drift are clamped to [0, 1].**

#### Transport behavior (v2.9)

On every transport play press, drift cycle restarts: all six targets' phase counters → 0. The filter LFO restarts from the configured **LFO Start Phase**, the filter state and cutoff smoothers clear, pan state and the Play/Rest gate reset, and the rate smoother re-seeds from the current Rate slider. Drift CONFIG is preserved across stop/play and project save/load. Speed Ramp progress also resets. Renders are deterministic for Sine and Triangle shapes (Random remains non-deterministic per render by design).

#### Migration from v2.8

The old flat-drift block (musical_up/down/period, slow_up/down/period, drift_shape on sliders 33-39) was 7 sliders covering Sweep Rate only. v2.9 is 5 sliders covering 6 independent targets, reusing slider IDs 33-37; sliders 38 and 39 are no longer declared. Old project values get reinterpreted (selector defaults to Sweep Rate; non-zero amounts on sliders 34-35 will produce drift on Sweep Rate). After upgrade, reset drift sliders to defaults if you'd never configured the old flat drift, or reconfigure under the new nested-selector pattern if you had.

---

## Usage Notes

- **Attack and Release are proportions of on-time, not cycle time.** A 50% Attack with 50% On Duration means the attack ramp takes 25% of the total cycle.
- **Depth % scales symmetrically around the center frequency.** At 50% depth with Low=200 Hz and High=2000 Hz, the sweep covers 700-1300 Hz — not 200-1100 Hz.
- **The filter coefficient uses linear frequency mapping** (`freq * 2 / srate`), unlike the sinusoidal mapping in the synthesizer plugins. Displayed Hz values correspond directly to standard filter behavior.
- **Phase Offset only takes effect in Offset from L mode.** In Independent L+R mode the offset slider has no effect on behavior.

---

*Full Feature Sweeping Filter is part of the Rozaya JSFX plugin suite.*
*Designed by Rozaya — Developed with Claude (Anthropic)*


---

