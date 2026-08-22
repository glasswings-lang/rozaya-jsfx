# Sweep Dwell Filter

**Designed by Rozaya — Developed with Claude (Anthropic)**

---

## Overview

Sweep Dwell Filter is a resonant lowpass filter driven by an LFO with four time-based phases: hold at high frequency, sweep down to low, hold at low frequency, and sweep back up. Unlike a rate-based LFO, the cycle duration is determined entirely by the four phase times — each phase has its own duration in seconds, and the total cycle length is their sum. The fade transitions have independently selectable curve shapes. A wet/dry mix and an optional pan modulation system complete the feature set.

The plugin processes incoming stereo audio.

---

## Signal Architecture

The LFO phase advances continuously. At any point in the phase, the plugin calculates the current position within the hold-high, sweep-down, hold-low, and sweep-up sequence, and outputs a value between 0 (low cutoff) and 1 (high cutoff) accordingly. The fade transitions use configurable curve shapes. The LFO output is mapped linearly to the frequency range, smoothed with a 3 ms lag, and fed into a two-pole resonant lowpass filter per channel. The wet output is blended with the dry signal.

Left and right channels have independent LFO phases. In **Independent L+R** mode both advance at the same rate, staying in sync. In **Offset from L** mode the right channel phase is continuously derived from the left plus the stereo offset, keeping a stable phase relationship.

---

## Parameters

### Filter Range

**Slope (dB/oct)** `−12 / −24 / −36 / −48 / −60 / −72, default −12`
How steeply the filter falls away past the cutoff — 1 to 6 cascaded two-pole
sections. −12 is the gentle slope this plugin has always had; −72 is a wall.

Two things hold at every slope, which is not automatic:

- **The cutoff number is the actual corner** — −3 dB at the frequency you set,
  at −12 and at −72 alike. Each section gets its own Butterworth Q; cascading
  identical sections instead would drag the real corner below the number,
  further the steeper you went.
- **Resonance means the same thing at every slope.** It is spread across the
  sections rather than applied to each, so it asks for the same total emphasis
  whether that is one section or six.

> **The filter core changed, and old projects were migrated.** This plugin used
> to use a two-pole Kellett cascade whose cutoff coefficient was `2*fc/srate`.
> Measured, its real −3 dB corner sat at **0.21× to 0.77×** the number on the
> slider — and it *moved with Resonance*, so turning resonance up slid the
> corner nearly two octaves without touching the frequency control. Frequency Hz
> was never Hz. Every project in the library was migrated by
> `tools/sweepfilter_migrate_hz.py`, which rewrote each instance's Frequency
> Low/High to the frequency its old filter was really cornering at, using that
> instance's own Resonance. **The numbers changed a lot; the sound did not.**
> What migration cannot carry across is the exact curve — the old filter had a
> droopier passband and a softer knee — so expect a character shift near the
> corner, not a tuning shift.

**Frequency Low Hz** `20-20000 Hz, default 500`
The cutoff frequency during the low-dwell segment — the resting state of the filter. If set higher than Frequency High, the two values are automatically swapped.

**Frequency High Hz** `20-20000 Hz, default 5000`
The cutoff frequency during the high-dwell segment — the open state of the filter.

**Resonance** `0.0-1.0, default 0.7`
Resonance of the lowpass filter. Higher values add a pronounced peak at the cutoff frequency, accentuating the frequencies at each point in the sweep. Values approaching 1.0 can produce self-oscillation.

**Wet/Dry Mix** `0.0-1.0, default 1.0`
Blend between the filtered signal and the unprocessed input. At 1.0 the output is fully filtered; at 0.0 the filter has no effect.

---

### Dwell and Transition Times

The LFO cycle consists of four phases in sequence: hold high → sweep down → hold low → sweep up → repeat. The total cycle length is the sum of all four phase durations.

**High Dwell sec** `0.001-60 sec, default 4`
Duration of the segment where the filter holds at the high cutoff frequency.

**Low Dwell sec** `0.001-60 sec, default 6`
Duration of the segment where the filter holds at the low cutoff frequency.

**Fade Down sec** `0.001-30 sec, default 1`
Duration of the transition from the high cutoff frequency to the low cutoff frequency.

**Fade Down Shape** `Linear / Cosine / Logarithmic / Exponential`
Curve shape applied to the fade-down transition.
- **Linear** — constant rate of frequency change.
- **Cosine** — S-curve, slow at both ends, faster in the middle.
- **Logarithmic** — fast initial drop, slow finish. The filter closes quickly then lingers near the low frequency.
- **Exponential** — slow initial drop, fast finish. The filter holds near the high frequency before closing sharply.

**Fade Up sec** `0.001-30 sec, default 1`
Duration of the transition from the low cutoff frequency back to the high cutoff frequency.

**Fade Up Shape** `Linear / Cosine / Logarithmic / Exponential`
Curve shape applied to the fade-up transition. Same options as Fade Down Shape. Asymmetric shapes between fade down and fade up create distinct opening and closing characters.

---

### Host tempo sync

**Cycle mode** `Own durations / Host x, default Own durations`
- **Own durations** — the four dwell sliders are literal seconds and the cycle is however long they add up to. This is the original behaviour and the default, so existing projects are unchanged.
- **Host x** — the four sliders keep their *proportions* but the whole cycle is stretched or squeezed to fit **Cycle length (beats)** at the project tempo. The shape you tuned by ear survives; only the speed changes.

**Cycle length mode** `Fit to durations / Set in beats, default Fit to durations` *(hidden unless Cycle mode is Host x)*

- **Fit to durations** — the cycle is however long your four dwell sliders add up to, in beats. Which means **each of the four is simply a beat count**: type `2` into Fade Down and the fade is two beats. Nothing to add up, nothing to convert, and the sum is worked out for you.
- **Set in beats** — the cycle is pinned to **Cycle length (beats)** below, and the four durations act as proportions filling it. Use this when you want a shape you've tuned by ear squeezed into a fixed number of beats.

Fit is the plugin's own way of thinking, just expressed in beats instead of seconds — Sweep Dwell has never had a rate slider; it has four times whose sum *is* the cycle. That's how envelopes work too (attack, decay, release — nobody sets a total). Set in beats is the LFO family's convention, borrowed in for when it's the more useful one.

Either way, Fit uses your four **slider** values, never the drifted ones. Drift and Speed Ramp still only move the shape and can't make the cycle wander in length.

**Cycle length (beats)** `0.25–128, default 12` *(hidden unless Cycle length mode is Set in beats)*
How many beats one full dwell pattern takes. The default 12 matches the default durations (4 + 1 + 6 + 1) so the two modes agree out of the box.

Two more things worth knowing before you reach for Host x:

- **In Set in beats, the dwell sliders become shape controls, not length controls.** Doubling High Dwell doesn't make the cycle longer — it makes the high hold take a bigger share of the same cycle, and everything else shrinks to fit. Same for Drift and Speed Ramp aimed at any of the four. (In Fit to durations they stay length controls, which is the point of it.)
- **Start Delay stays in literal seconds.** It's a "wait before the effect arrives" control rather than musical pacing, so it doesn't follow the tempo. If you're staggering two instances against each other, that's the one to watch.

Switching Cycle mode changes what the dwell numbers *mean*, and nothing rescales them for you. Nothing is lost — flip back and the seconds are still there — but the sound will jump.

#### The cycle is positioned from the project, not from when you pressed play

In Host x, with the transport rolling, the plugin asks REAPER where it is in the song and puts the cycle there. Drop the playhead into the middle of bar 40 and the sweep is already exactly where it would have been if you'd played from the top. The start of the high dwell lands on a bar line, every time.

That's the behaviour tempo-synced effects are expected to have, and it's the reason to sync at all — a cycle that's the right *length* but starts wherever you happened to press play still lands off the grid. It also can't slowly drift out over a long session, and it follows seeking and looping for free.

Two exceptions, both deliberate:

- **Stopped or paused**, the project position doesn't move, so the cycle free-runs instead. Otherwise it would sit frozen for anyone monitoring live.
- **Pan Sweep** (modes 10 and 11) always free-runs, even on the Host x unit, because Drift and Speed Ramp can move its rate — and positioning from the project assumes a rate that isn't being modulated underneath. **Linked Sweep** does lock, since its multiplier is fixed. The rule across the plugin is: lock what's constant, accumulate what's modulated.

Every other rate mode is unchanged and still starts from zero on play.

---

### Stereo

**Stereo Phase Offset degrees** `-180–+180°, default 0`
When Phase Mode is Offset from L, this controls the phase difference between the left and right LFOs. At 180° the channels are in opposition — when the left filter is at its high cutoff the right is at its low cutoff. At 0° both channels move identically.

**Phase Mode** `Independent L+R / Offset from L`
- **Independent L+R** — both LFO phases advance freely at the same rate, staying in sync.
- **Offset from L** — the right channel phase is derived continuously as the left phase plus the Stereo Phase Offset. Use this mode to maintain a stable stereo phase relationship.

---

### Pan Block

**Pan Enabled** `Off / On`
Enables pan modulation. When on, the post-filter signal is summed to mono and repositioned in the stereo field. When off, all pan sliders are hidden.

> **Note:** Enabling pan sums the output to mono before panning. Stereo content of the filtered signal is collapsed.

---

#### Per-Cycle Pan Modes

Pan position updates once per LFO cycle. **Cycle Steps** controls the sequence length.

**Mono** — signal stays centered.

**Alternating** — alternates hard left and hard right each cycle.

**Alternating (Flipped)** — same as Alternating, starting from the right.

**Distributed** — steps evenly from left to right across the cycle count, then wraps.

**Distributed (Flipped)** — steps evenly from right to left, then wraps.

**Distributed (Ping-pong)** — steps left to right then reverses, bouncing between extremes.

**Converging** — starts hard left, alternates left/right positions stepping progressively toward center.

**Converging (Ping-pong)** — converges to center then reverses back outward, bouncing.

**Diverging** — starts center, alternates left/right positions stepping progressively outward.

**Diverging (Ping-pong)** — diverges to extremes then reverses back inward, bouncing.

---

#### Continuous Pan Modes

**Pan Sweep** — continuous left-to-right sweep at the rate set by Pan Sweep Rate.

**Pan Sweep (Flipped)** — continuous right-to-left sweep.

**Linked Sweep** — pan sweeps in proportion to the filter cycle rate, scaled by Filter Speed Multiplier. At 1×, one full pan sweep per filter cycle.

---

#### Pan Parameters

**Pan Spread** `0.0-1.0, default 1.0`
Scales the pan range. At 0.0 all modes produce center.

**Pan Glide ms** `0-100 ms, default 5`
Smoothing time for pan position changes.

**Cycle Steps (per-cycle modes)** `2-32, default 8`
Sequence length for per-cycle modes.

**Pan Sweep Rate** `0.001-1000, default 2`
Rate for Pan Sweep and Pan Sweep (Flipped) modes.

**Pan Sweep Rate Unit** `Hz / Seconds / BPM / Host x`
Unit for Pan Sweep Rate. **Host x** makes the value a multiplier of the project tempo — 1 is one pan sweep per beat, 0.25 is one every four beats, 2 is two per beat. Higher is faster.

**Filter Speed Multiplier (Linked Sweep)** `0.125-8×, default 1×`
Pan sweep speed relative to filter cycle, for Linked Sweep only.

#### What host sync does to pan

Most of the pan modes follow the tempo for free once **Cycle mode** is Host x, because they were never on their own clock:

- **Mono** — no motion, nothing to sync.
- **Alternating, Distributed, Converging, Diverging** and their Flipped / Ping-pong variants (the per-cycle modes) step one position per dwell cycle. Sync the cycle and they step in time automatically.
- **Linked Sweep** runs at the filter's own cycle rate times the multiplier, so it follows too — and at multipliers like 2 or 0.5 it lands on beat divisions.
- **Pan Sweep** and **Pan Sweep (Flipped)** are the only two on an independent clock. Those use Pan Sweep Rate Unit above — set it to Host x if you want them locked as well.

### Start Delay

**Start Delay (seconds)** `0–1000, default 0`

Pass-through for N seconds after playback starts, then applies the sweep-dwell filter + pan effect normally. The dry signal flows through unchanged during the delay — silencing the output would mute the dry track too, which is rarely what you want for an effect. Sweep state and filter buffers stay frozen during the delay so the sweep begins cleanly at delay-end. Re-arms on every transport stop/start. 0 disables the delay.

### Play / Rest Gating (v2.1)

**Play for (cycles)** `0–1000, default 0`
**Rest for (cycles)** `0–1000, default 0`
**LFO at rest** `Walk through / Freeze in place, default Walk through`
**Output at rest** `Pass-through / Silence, default Pass-through`

A cyclic gate over the filter + pan effect. The effect is applied normally for **Play for** cycles, then enters its rest period for **Rest for** cycles, then resumes — the pattern repeats forever.

One "cycle" here is one full dwell pattern: **High Dwell + Fade Down + Low Dwell + Fade Up**. So with the default settings (4 + 1 + 6 + 1 = 12 sec/cycle), `Play for = 4` plays 48 seconds of the sweep before entering rest, and `Rest for = 2` rests for 24 seconds. Cycle counts at this plugin can produce long play / rest periods because the dwell pattern itself is long — adjust the dwell + fade sliders if you want shorter cycles.

The feature is **disabled when either of Play for / Rest for is 0** (the default). With both at 0, the plugin behaves as before; the two "at rest" sliders have no effect when the gate is off.

**Click-free transitions.** The effect smoothly fades out on rest entry (and back in on exit) using the same ~3 ms smoother that handles the cutoff sweep. The filter coefficients and resonance state keep running through the rest period so the filter is "warm" and ready to re-engage cleanly.

Two independent sliders shape what happens during rest:

**LFO at rest** — what the dwell-pattern LFO and pan LFOs do during rest:

- **Walk through** (default): LFOs keep cycling during rest. When the effect resumes, the dwell pattern has advanced to a different position — you might hear it resume mid-fade-down or mid-low-dwell rather than at the start of a fresh high dwell.
- **Freeze in place**: LFO phases pause, frozen at their values at rest entry. When the effect resumes, the dwell pattern picks up from the same position. Useful when you want predictable phase relationships across multiple play/rest cycles.

**Output at rest** — what the audio output does during rest:

- **Pass-through** (default): dry signal passes through unchanged. Matches Start Delay's behavior.
- **Silence**: wet+dry mix smooths to 0 over ~3 ms; the audio fades into silence rather than passing dry. Useful when you want the gate to act like a hard mute rather than a filter bypass.

The two sliders are orthogonal — all four combinations work and produce distinct behavior.

**Filter resonance state and cutoff smoother keep running across all four combinations.** Only the LFO phase advancement is frozen in Freeze — the actual filter math continues processing the input throughout rest. This avoids transients on rest exit, at the cost of the filter potentially having settled to a slightly different cutoff position than at rest entry.

**Transport behavior**: conventional. Stop passes through dry; play re-initializes everything and starts fresh in its play period from cycle 0.

### Speed Ramp

Nested-selector pattern matching Womb v3 / breath_gen. Pick a target and set a signed `by` amount. As of v2.14 Speed Ramp reaches the **same 6 targets as Drift** — the four dwell phases (High dwell / Fade down / Low dwell / Fade up) plus **Pan Sweep Rate** and **Resonance** (previously Speed Ramp had only the four dwells). All 6 ramp in parallel; the selector just changes which one you're editing.

**Speed ramp target (slider 26)** `High dwell / Fade down / Low dwell / Fade up / Pan Sweep Rate / Resonance, default High dwell`
The 6-option selector (matches Drift). Switching saves the current target's `by` + duration + start delay to its memory slot and loads the new target's saved values. All 6 targets ramp regardless of which one is selected. The `by` (slider 29) is in seconds for the dwell targets, the Pan Sweep Rate's own unit for that target, and a 0–1 fraction for Resonance.

**Speed ramp duration (slider 27)** `0–60 minutes, default 0` — **per-target** (v2.14): how long the *selected* dwell target takes to travel from baseline to baseline + `by`; a target with duration 0 doesn't ramp. · **Speed ramp engage (slider 28)** `Off / On, default Off` — **global**: one switch arms every configured target, each riding its own duration after its own start delay.

Engage is a freeze/resume gate (NOT a restart edge): while On, each target's clock advances 0 → 1 over its own duration; while Off all freeze and resume on re-engage. As of v2.14 each target has its own duration + start delay (previously shared) — different dwell phases can ramp on different timelines from one engage.

**Speed ramp by (slider 29)** `-60 to +60 seconds, step 0.001, default 0`
Signed delta in seconds for the selected dwell phase. **0** = no change. **Negative** = shorten that phase (shorter cycle if that's High/Low dwell; quicker fade if that's a fade phase). **Positive** = lengthen. Example: target High dwell with `by +4` stretches high dwell from 4 sec → 8 sec over the duration; combined with target Low dwell with `by +2`, both phases ramp together as a coordinated wind-down.

**Speed ramp start delay (slider 37)** `0–60 minutes, default 0` — **per-target** (v2.14): wait this many minutes after engage before *this* target begins moving (stagger targets by giving them different delays). Saved/loaded per target by the selector, like `by` and duration. Lives at slider 37 (after the drift block) because slider 29 was claimed by the `by` amount.

**Transport behavior:** speed_ramp_t resets to 0 on every transport play edge. The existing ~3 ms cutoff smoother absorbs any per-sample step changes, so manual dwell-slider tweaks remain click-free.

**Migration from v2.7:** slider 26 changed from multiplier (0.1–4.0) to a 4-option selector. Existing projects' multiplier value rounds down to a target index, and slider 29 (the new amount) defaults to 0 — Speed Ramp produces no effect on reload until reconfigured.

### Drift (v2.9 nested-selector)

Slow organic wander applied independently to any of six targets: High dwell, Fade down, Low dwell, Fade up, Pan Sweep Rate, or Resonance. Each target can have its own drift configuration; all six drift in parallel. The selector chooses which target's drift you're currently editing — the others keep running with their last-saved configuration.

Same pattern as Womb v3's drift and the rest of the v2.9 sweep. Switching the **Drift target** selector saves the current sliders 31-34 into the old target's memory slot, then loads the new target's saved values. All six configurations persist across project save/load.

The four dwell-phase targets are the same set as the Speed Ramp targets and use the same selector indices, so you can configure a coordinated drift + ramp on the same dwell phase. Drift on a dwell phase is **additive in seconds** (like the Speed Ramp `by`) — drift each phase independently and the pattern's shape itself wanders, not just its overall pace.

**Drift target** `High dwell / Fade down / Low dwell / Fade up / Pan Sweep Rate / Resonance, default High dwell`
Picks which target's drift configuration sliders 31-34 reflect. Switching the selector saves and loads automatically — no live edits are lost.

**Drift up amount** `0.0–100.0, default 0` (units match target)
How far above the target's baseline the drift wanders at its peak. Units: seconds for the four dwell phases, the Pan Sweep Rate's own unit for Pan Sweep Rate, a 0-1 fraction for Resonance. 0 = drift off on the up side. Resonance uses the low end of the range (e.g. 0.3).

**Drift down amount** `0.0–100.0, default 0` (units match target)
How far below the baseline the drift wanders at its trough. Independent from Up — asymmetric wander supported. Either non-zero activates drift for the target; both 0 = drift off.

**Drift period (cycles)** `1–1000, default 8`
How many dwell patterns one full drift wave takes for this target. All six targets use dwell patterns as their period unit, scaled by Speed Ramp so the wave-per-pattern relationship stays constant under wind-down.

**Drift shape** `Sine / Triangle / Random, default Sine`
Wander waveform. Sine = smooth, Triangle = linear ramps with turnarounds, Random = value-noise interpolating smoothly between fresh random targets at each period boundary.

#### Notes

- **Pan Sweep Rate drift only affects pan modes 10 and 11** (Pan Sweep / Pan Sweep Flipped). Linked Sweep follows the dwell-pattern rate, which the dwell-phase targets already move.
- **Resonance drift is clamped to [0, 1].**

#### Transport behavior (v2.9)

On every transport play press, drift cycle restarts: all six targets' phase counters → 0. Dwell LFO phases, filter state + cutoff smoothers, pan state, and the Play/Rest gate also reset. Drift CONFIG (and the Speed Ramp config bank) is preserved across stop/play and project save/load. Speed Ramp progress also resets. Renders are deterministic for Sine and Triangle shapes (Random remains non-deterministic per render by design).

#### Migration from v2.8

The old flat-drift block (musical_up/down/period, slow_up/down/period, drift_shape on sliders 30-36) was 7 sliders covering the whole dwell period. v2.9 is 5 sliders covering 6 independent targets, reusing slider IDs 30-34; sliders 35 and 36 are no longer declared (slider 37, Speed ramp start delay, is unchanged). Old project values get reinterpreted (selector defaults to High dwell; non-zero amounts on sliders 31-32 will produce drift on the High dwell phase). After upgrade, reset drift sliders to defaults if you'd never configured the old flat drift, or reconfigure under the new nested-selector pattern if you had.

---

## Usage Notes

- **Cycle length is the sum of all four phase durations.** Unlike rate-based LFOs there is no single BPM or Hz value — the tempo of the sweep is a consequence of the four phase times combined.
- **Adjusting any phase duration takes effect immediately.** The LFO phase is a running 0-1 counter; changing phase durations changes how that counter maps to filter positions without resetting it. This means a duration change mid-cycle may cause a jump to a different point in the sweep.
- **The frequency mapping is linear.** Displayed Hz values correspond directly to filter behavior — the same linear mapping used in the other filter plugins in this suite.
- **Phase Offset only takes effect in Offset from L mode.** In Independent L+R mode the offset slider has no audible effect.

---

*Sweep Dwell Filter is part of the Rozaya JSFX plugin suite.*
*Designed by Rozaya — Developed with Claude (Anthropic)*


---

