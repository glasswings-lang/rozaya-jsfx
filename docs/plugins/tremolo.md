# Full Feature Tremolo

**Designed by Rozaya — Developed with Claude (Anthropic)**

---

## Overview

Full Feature Tremolo is an amplitude modulation effect with a fully configurable LFO envelope and an optional pan modulation system. The tremolo LFO is not a simple sine wave — it is a gated envelope with independently shaped attack and release curves, a configurable on-time within each cycle, and a hold-high region between them. This allows the plugin to produce anything from a smooth, sine-like tremolo to a hard gate with slow attack, fast release, or any combination in between.

The pan block, when enabled, moves the signal through the stereo field in sync with or independently of the tremolo cycle, with twelve pan modes ranging from simple alternation to continuous sweeps.

The plugin processes incoming stereo audio.

---

## Signal Architecture

### Tremolo

The LFO runs as a normalized phase (0-1 per cycle). Each sample, the phase advances by `freq / srate`. The LFO envelope is computed from the phase position relative to the on-time, attack, and release durations. The resulting gain value (between the depth floor and 1.0) is smoothed with a 3 ms lag to prevent zipper noise on abrupt transitions, then applied as a multiplier to each channel.

Left and right channels have independent phase counters. In **Independent L+R** mode they both advance freely at the same rate. In **Offset from L** mode the right channel phase is derived as the left channel phase plus the stereo offset, keeping them locked in relative position.

### Pan

When the pan block is enabled, the post-tremolo signal is summed to mono, then redistributed to L and R using constant-power panning. The pan position is smoothed by the glide coefficient before being applied, preventing clicks on sudden position changes.

---

## Parameters

### Tremolo

**Rate Value** `0.001-1000, default 2`
The tremolo rate in the units set by Rate Mode.

**Rate Mode** `Hz / Seconds / BPM / Host x`

**Host x** makes Rate Value a **multiplier of the project tempo** instead of an
absolute rate — x1 = one tremolo cycle per beat, x2 = twice as fast, x0.5 =
half. Move the project tempo and it moves with it, in proportion, so several
instances keep their relationships to each other instead of scattering when you
change the speed of an arrangement.

Not quantising: Rate Value stays continuous, so deliberately unlocked
relationships survive a tempo change just as locked ones do. Tempo changes
apply live, including mid-playback.

**Host ratio (writes Rate Value)** `Custom / every 8 beats / … / 8 per beat` (default Custom)
Shown only in Host x mode. Writes the multiplier into Rate Value and then gets
out of the way, so you can still type or automate anything. **Custom** never
writes anything, and is deliberately not called "Free" — in sync UI that means
free-running, which is what the other three modes already are. Entries are
named for what you hear, never as note values.

> **Fixed at the same time:** Start Delay was 60x out in both Hz and BPM modes.
> The conversion had been written as if Rate Mode were ordered
> `{BPM, Seconds, Hz}` (as it is in Melody Phase and Polyrhythm Phase), but here
> it is `{Hz, Seconds, BPM}` — so Hz was getting the BPM formula and BPM the Hz
> one. Seconds mode was always correct. If you had dialled a Start Delay by ear
> to compensate, it will now be 60x off in the other direction.
How Rate Value is interpreted.
- **Hz** — cycles per second.
- **Seconds** — period of one full cycle.
- **BPM** — cycles per minute.

**On Duration % of Cycle** `0-100%, default 50`
The proportion of each cycle during which the tremolo is in its active (non-silent) state — including attack and release time. At 50%, the signal is present for half the cycle and absent for the other half. At 100%, the tremolo never fully closes. At 0%, the output is silence.

**Depth dB** `-60-0 dB, default -6`
How far the signal drops at the bottom of the tremolo cycle. At 0 dB there is no depth and the output is unaffected. At -60 dB the signal is effectively silenced at the trough. The depth is converted internally to a linear gain multiplier.

**Attack %** `0-100%, default 0`
Proportion of the on-time spent fading in from silence to full level. At 0%, the tremolo opens instantly at the start of each on-period. Attack and Release proportions are expressed relative to the on-time, not the full cycle — so an Attack of 50% means the first half of the on-duration is the attack ramp. If Attack % + Release % exceeds 100% of the on-time, both are scaled down proportionally.

**Release %** `0-100%, default 0`
Proportion of the on-time spent fading from full level back to silence. At 0%, the tremolo closes instantly at the end of each on-period.

**Attack Shape** `Linear / Cosine / Logarithmic / Exponential`
Curve applied to the attack ramp.
- **Linear** — straight ramp.
- **Cosine** — S-curve, gentle at both ends.
- **Logarithmic** — fast initial rise, slow finish. Perceived loudness increases quickly.
- **Exponential** — slow initial rise, fast finish. Builds tension before arrival.

**Release Shape** `Linear / Cosine / Logarithmic / Exponential`
Curve applied to the release ramp. Same options as Attack Shape. Mixing attack and release shapes — e.g., Logarithmic attack with Exponential release — can produce organic, asymmetric tremolo characters.

**Stereo Phase Offset (degrees)** `-180–+180°, default 0`
When Phase Mode is set to Offset from L, this controls how far ahead or behind the right channel's LFO is relative to the left. At 180° or -180°, the channels are in perfect opposition — when left is at its peak, right is at its trough. At 0°, the offset is zero and both channels move in unison regardless of mode (equivalent to Independent L+R for most purposes).

**Phase Mode** `Independent L+R / Offset from L`
- **Independent L+R** — left and right LFO phases advance independently. Both start at zero and run freely. In practice they stay in sync unless rates diverge, which they don't in this plugin — so this mode produces synchronized stereo tremolo.
- **Offset from L** — the right channel phase is continuously derived as the left phase plus the Stereo Phase Offset. This keeps the offset locked regardless of where in the cycle each channel is, and is the correct mode to use when you want a stable stereo phase relationship.


#### The cycle is positioned from the project, not from when you pressed play

In **Host x**, with the transport rolling, the plugin asks REAPER where it is in the song and puts the cycle there. Drop the playhead into the middle of bar 40 and the tremolo is already exactly where it would have been if you'd played from the top — so it lands the same way at the same bar however you got there. That's the behaviour a tempo-synced effect is expected to have, and it's most of the reason to sync at all: a cycle that's the right *length* but starts wherever you pressed play still lands off the grid.

It also can't slowly drift out over a long session, and it follows seeking and looping for free.

Two exceptions, both deliberate:

- **Stopped or paused**, the project position isn't advancing, so it free-runs instead — otherwise it would sit frozen for anyone monitoring live.
- **Drift or Speed Ramp on the rate hands it back to free-running.** Positioning from the project answers "where would this be if it had run at this rate all along," which stops being the right question the moment something is changing the rate. There's no jump at the handover, and it stays free until the next transport start rather than lurching back onto the grid mid-play. Which is what you asked for anyway — putting drift on the rate *is* asking for it off the grid.

Every other rate mode is unchanged and still starts from zero on play.

---

### Pan Block

**Pan Enabled** `Off / On`
Enables the pan modulation system. When off, all pan-related sliders are hidden and the signal passes through the tremolo section unaffected by panning. When on, the post-tremolo signal is summed to mono and panned according to the active pan mode.

> **Note:** Enabling pan converts the output to mono before panning. If your source is stereo and you want to preserve its stereo image, use Pan Enabled only when the mono sum is acceptable, or place the tremolo before stereo-sensitive processing.

---

#### Per-Cycle Pan Modes

These modes update the pan position once per tremolo cycle, at the moment the LFO phase resets. The **Cycle Steps** parameter controls how many steps the sequence runs before repeating (where applicable).

**Mono**
No panning. Signal stays centered regardless of Cycle Steps.

**Alternating**
Jumps between hard left and hard right on each cycle. Step count does not affect this mode.

**Distributed**
Steps evenly from left to right across the cycle count, then repeats from the left. At 8 steps: hard left, then incrementally right, reaching hard right on step 8, then back to hard left.

**Distributed (Flipped)**
Same as Distributed but starting from the right and stepping left.

**Distributed (Ping-pong)**
Steps left to right then reverses back right to left, bouncing between the extremes.

**Converging**
Starts at hard left, then alternates left and right positions that step progressively toward center. Each pair of positions is closer to center than the last.

**Converging (Ping-pong)**
Same pattern as Converging but bounces back outward after reaching center, then converges again.

**Diverging**
Starts at center, then alternates left and right positions stepping progressively outward toward the extremes.

**Diverging (Ping-pong)**
Same as Diverging but bounces back inward after reaching the extremes.

---

#### Continuous Pan Modes

**Pan Sweep**
Pan position sweeps continuously from left to right using a linear ramp at the rate set by Pan Sweep Rate and Pan Sweep Rate Unit, independently of the tremolo rate. When the pan reaches the right extreme it wraps back to the left.

**Pan Sweep (Flipped)**
Same as Pan Sweep but sweeping from right to left.

**Linked Sweep**
Pan position sweeps in sync with the tremolo LFO, but at a speed multiplied by the Filter Speed Multiplier. At 1×, the pan completes one full sweep per tremolo cycle. At 2×, it sweeps twice per cycle. At 0.5×, it sweeps once every two cycles.

---

#### Pan Parameters

**Pan Spread** `0.0-1.0, default 1.0`
Scales the pan range. At 1.0, pan positions reach hard left and hard right. At 0.5, the maximum excursion is halfway to each side. At 0.0, all pan modes produce center regardless of their position calculations.

**Pan Glide ms** `0-100 ms, default 5`
Smoothing time applied to pan position changes. At 0 ms, pan position jumps immediately to each new value — appropriate for hard-cut effects but can produce clicks on per-cycle modes at slow tempos. Higher values smooth the transition, trading sharpness for click-free movement.

**Cycle Steps (per-cycle modes)** `2-32 steps, default 8`
Number of steps in the pan sequence for per-cycle modes (Alternating through Diverging Ping-pong). Hidden when a continuous pan mode is active.

**Pan Sweep Rate** `0.001-1000, default 2`
Rate of the continuous pan sweep for Pan Sweep and Pan Sweep (Flipped) modes. Hidden for other modes.

**Pan Sweep Rate Unit** `Hz / Seconds / BPM`
Unit for Pan Sweep Rate. Hidden for modes that don't use it.

**Filter Speed Multiplier (Linked Sweep)** `0.125-8×, default 2×`
Speed of the pan sweep relative to the tremolo rate, for Linked Sweep mode only. Hidden for other modes.

### Start Delay

**Start Delay** `0–1000, default 0`

Pass-through for N units after playback starts, then applies the tremolo + pan effect normally. Units match Rate Mode: BPM mode counts cycles of the tremolo Rate Value, Seconds is literal seconds, Hz mode counts cycles of Rate Value. The dry signal flows through unchanged during the delay — silencing the output would mute the dry track too, which is rarely what you want for an effect. Phase counters and gain smoothing stay frozen during the delay so the tremolo begins cleanly at delay-end. Re-arms on every transport stop/start. 0 disables the delay.

### Play / Rest Gating (v2.1)

**Play for (cycles)** `0–1000, default 0`
**Rest for (cycles)** `0–1000, default 0`
**LFO at rest** `Walk through / Freeze in place, default Walk through`
**Output at rest** `Pass-through / Silence, default Pass-through`

A cyclic gate over the tremolo + pan effect. The effect is applied normally for **Play for** cycles, then enters its rest period for **Rest for** cycles, then resumes — the pattern repeats forever. Useful for rhythmic on/off of the modulation: "tremolo for 4 bars, no tremolo for 4 bars, repeat."

Cycle unit is the same as Start Delay: Rate Mode units measured against Rate Value. At the default Rate Value = 2 in Hz mode, "4 cycles" = 2 seconds.

The feature is **disabled when either of Play for / Rest for is 0** (the default). With both at 0, the plugin behaves as before; the LFO at rest / Output at rest sliders have no effect when the gate is off.

**Click-free transitions.** When entering rest, the relevant target (dry pass-through or silence, depending on Output at rest) is smoothly faded toward over ~3 ms. On rest exit, the same fade brings the effect back in. The gate sounds like a soft swell rather than an abrupt switch.

Two independent sliders shape what happens during rest:

**LFO at rest** — what the tremolo + pan LFOs do during rest:

- **Walk through** (default): LFOs keep cycling during rest. When the effect resumes, the LFOs are at new phase positions reflecting wall-clock time passed. The rhythmic cycle keeps running even when you can't hear it.
- **Freeze in place**: LFO phases pause during rest, frozen at their values at rest entry. When the effect resumes, the LFOs pick up from the same phase. The rhythmic cycle pauses and resumes in lockstep with the gate.

**Output at rest** — what the audio output does during rest:

- **Pass-through** (default): dry signal passes through unchanged. Effect plugins normally don't silence their input — silencing would mute whatever's upstream in the FX chain. Matches Start Delay's pass-through-during-delay behavior on this plugin.
- **Silence**: gain target smooths to 0 over ~3 ms; the audio fades into silence rather than passing dry. Useful when you want the gate to act like a hard mute rather than an effect bypass — e.g., for rhythmic drop-outs in an arrangement.

The two sliders are orthogonal — all four combinations work and produce distinct behavior. Walk + Silence keeps the rhythm running internally while the audio drops out; Freeze + Silence pauses everything (audio AND rhythm); Walk + Pass-through and Freeze + Pass-through are the two "effect bypass" flavors.

**Transport behavior**: conventional. Stop passes through dry; play re-initializes everything (LFO phases, rest state, cycle counter) and starts fresh in its play period from cycle 0.

### Speed Ramp (v2.14 nested-selector)

In-plugin one-time morph over time. As of v2.14 Speed Ramp is nested-selector (same shape as Drift) and reaches the **same six targets as Drift** — Rate Value, Depth dB, Pan Sweep Rate, On Duration %, Attack %, Release %. All six ramp in parallel; the selector only chooses which one the `by` slider is currently editing.

**Speed ramp target (slider 24)** `Rate Value / Depth dB / Pan Sweep Rate / On Duration % / Attack % / Release %, default Rate Value`
Picks which target the `by` amount applies to. Switching the selector saves slider 25 into the old target's memory slot, then loads the new target's stored `by`. Sits at the top of the Speed Ramp block (above the controls it governs) — a v2.14 reorganization; see the migration note below.

**Speed ramp by (slider 25)** `-1000 to +1000, step 0.001, default 0` (units match the selected target)
Signed delta in the selected target's own unit, applied over the duration. **0** = no change. For the rate-type targets (Rate Value, Pan Sweep Rate) the delta is in **that rate's currently-displayed unit** (Hz / Seconds / BPM): in BPM/Hz modes negative `by` = slower, in Seconds mode positive `by` = slower (longer period). Depth is dB, the three % targets are percentage points.

**Speed ramp duration (slider 26)** `0–60 minutes, default 0` — **per-target** (v2.14): how long the *selected* target takes to travel from baseline to baseline + `by`; a target with duration 0 doesn't ramp. · **Speed ramp start delay (slider 28)** `0–60 minutes, default 0` — **per-target**: wait this many minutes after engage before *this* target moves (stagger targets by giving them different delays). · **Speed ramp engage (slider 27)** `Off / On, default Off` — **global**: one switch arms every configured target, each riding its own duration after its own delay. (Duration + start delay are saved/loaded per target by the selector, like `by`.)

Engage is a freeze/resume gate (NOT a restart edge): while On, each target's clock advances 0 → 1 over its own duration; while Off, all clocks freeze and resume on re-engage.

A ~100 ms smoother sits between the Rate slider and the effective frequency, so manual Rate tweaks don't click. The linked-sweep pan rate (Pan Mode 11) rides the Rate Value ramp since it derives from the tremolo frequency; Pan Sweep modes 9/10 have their own rate, which you can now ramp directly via the **Pan Sweep Rate** target.

**Transport behavior:** every target's ramp clock resets to 0 on the transport play edge. This is the ONLY thing that resets the ramps — slider changes (engage toggle, selector switch, anything) don't.

**Migration to v2.14 (reorganization + renumber):** Speed Ramp went multi-target and the block was reorganized so the target selector reads *above* the by/duration/engage controls it governs. Because REAPER orders sliders by ID (not file position), this required renumbering the Speed Ramp block (now sliders 24–28) and the Drift block (now sliders 29–33). **Existing Tremolo projects lose their Speed Ramp and Drift settings on upgrade** — both are off-by-default, and the tremolo sound itself (sliders 1–23) is untouched. Re-add the plugin instance for clean defaults, or re-enter your settings. *(Older history: pre-v2.14 Speed Ramp was single-target Rate Value on slider 24; and pre-v2.8 it was a multiplier 0.1–4.0.)*

### Drift (v2.9 nested-selector)

Slow organic wander applied independently to any of six targets: Rate Value, Depth dB, Pan Sweep Rate, On Duration %, Attack %, or Release %. Each target can have its own drift configuration; all six drift in parallel. The selector chooses which target's drift you're currently editing — the others keep running with their last-saved configuration.

Same pattern as Womb v3's drift and the rest of the sweep (target list now shared with Speed Ramp as of v2.14). Switching the **Drift target** selector saves the current sliders 30-33 into the old target's memory slot, then loads the new target's saved values. All six configurations persist across project save/load.

Drift on Depth dB makes the tremolo breathe deeper and shallower over time; drift on On Duration / Attack / Release wanders the *shape* of each pulse rather than its rate. Combine a slow Rate Value drift with a faster Depth drift for a modulation that wanders in both speed and intensity on independent schedules.

**Drift target (slider 29)** `Rate Value / Depth dB / Pan Sweep Rate / On Duration % / Attack % / Release %, default Rate Value`
Picks which target's drift configuration sliders 30-33 reflect. Switching the selector saves and loads automatically — no live edits are lost.

**Drift up amount (slider 30)** `0.0–100.0, default 0` (units match target)
How far above the target's baseline the drift wanders at its peak. Units are the rate's current unit (BPM / Seconds / Hz) for Rate Value, dB for Depth, the Pan Sweep Rate's own unit for Pan Sweep Rate, percent for the three % targets. 0 = drift off on the up side. Rate / Pan-rate targets in Hz mode use the low end of the range.

**Drift down amount (slider 31)** `0.0–100.0, default 0` (units match target)
How far below the baseline the drift wanders at its trough. Independent from Up — asymmetric wander supported. Either non-zero activates drift for the target; both 0 = drift off.

**Drift period (slider 32, cycles)** `1–1000, default 8`
How many tremolo cycles one full drift wave takes for this target. All six targets use tremolo cycles as their period unit, scaled by Speed Ramp so the wave-per-cycle relationship stays constant under wind-down.

**Drift shape (slider 33)** `Sine / Triangle / Random, default Sine`
Wander waveform. Sine = smooth, Triangle = linear ramps with turnarounds, Random = value-noise interpolating smoothly between fresh random targets at each period boundary.

#### Notes

- **Pan Sweep Rate drift only affects pan modes 9 and 10** (Pan Sweep / Pan Sweep Flipped) — the only modes that use the Pan Sweep Rate. In Linked Sweep mode the pan rate follows the tremolo rate, so Rate Value drift already moves it.
- **Mode-direction asymmetry on the rate targets:** in BPM and Hz modes a positive drift amount speeds up; in Seconds mode (where the rate value is a period) a positive amount lengthens the period and so slows down. Handled automatically by the same rate-unit conversion the Speed Ramp uses.

#### Transport behavior (v2.9)

On every transport play press, drift cycle restarts: all six targets' phase counters → 0 (drift offset = 0 at the first sample). Tremolo LFO phases, gains, pan state, and the Play/Rest gate also reset; the rate smoother re-seeds from the current Rate slider. Drift CONFIG (up/down/per/shape values per target) is preserved across stop/play and across project save/load. Speed Ramp progress also resets on transport play. This makes renders deterministic for Sine and Triangle shapes (Random remains non-deterministic per render by design).

#### Migration from v2.8

The old flat-drift block (musical_up/down/period, slow_up/down/period, drift_shape on sliders 28-34) was 7 sliders covering Rate Value only. v2.9 is 5 sliders covering 6 independent targets, reusing slider IDs 28-32; sliders 33 and 34 are no longer declared. Old project values get reinterpreted (selector defaults to Rate Value; non-zero amounts on sliders 29-30 will produce drift on Rate Value). After upgrade, reset drift sliders to defaults if you'd never configured the old flat drift, or reconfigure under the new nested-selector pattern if you had.

---

## Usage Notes

- **Pan block sums to mono before panning.** This is intentional — pan modulation is applied to a unified signal. If the source is stereo, the two channels are averaged before any pan position is applied.
- **Attack and Release are proportions of on-time, not cycle time.** A 50% Attack with a 50% On Duration means the attack ramp takes 25% of the total cycle.
- **Phase Offset only takes effect in Offset from L mode.** In Independent L+R mode the offset slider has no effect.
- **Per-cycle pan modes update at LFO phase reset.** The pan position does not glide to a new value mid-cycle — it jumps (subject to Pan Glide smoothing) at the moment the tremolo cycle wraps.

---

*Full Feature Tremolo is part of the Rozaya JSFX plugin suite.*
*Designed by Rozaya — Developed with Claude (Anthropic)*


---

