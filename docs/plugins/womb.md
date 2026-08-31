# Womb Sound Generator v3

**Designed by Rozaya — Developed with Claude (Anthropic)**

*v3 is the current and only shipped Womb (`src/womb_sound_generator_v3.jsfx`). The earlier v1 and v2 were archived on 2026-06-15; their manuals live beside the frozen source in [`archive/versions/womb_sound_generator/`](../../archive/versions/womb_sound_generator/).*

---

## Overview

Womb Sound Generator v3 is a Womb variant with the same three-layer architecture as v2 (heartbeat / breath / bloodflow) and most of the same controls. The headline change is the **drift system**: v2 had separate Heart drift and Breath drift slider blocks covering 2 wander targets. v3 collapses to a single target-selector pattern (same shape Resonance Bank uses) that covers **10 wander targets** with **fewer total sliders**: Heart rate, S1-S2 gap, Inhale Duration, Top Pause, Exhale Duration, Bottom Pause, RSA depth, Breaths/min (the aggregate breath-rate target), and Inhale Freq + Exhale Freq (the breath-noise filter cutoffs — the breath's brightness; all three added v2.14). All ten wanders run in parallel; you configure them one at a time via the selector.

v3 also adds a **periodic sigh** mechanism — every ~N minutes a single breath's inhale stretches by a configurable depth multiplier, modeling the real sleep-breathing pattern of occasional deep breaths between regular cycles.

v3 ships **alongside** v1 and v2 (all three files live in the same plugin folder). v2 stays available unchanged for projects already built on it. v3 is the recommended version going forward for new projects.

The audio architecture (heartbeat sound generation, breath filters, bloodflow envelope, post-filter, Solo logic, Speed Ramp, Start Delay, Play/Rest gates per layer, BPM rescale, Heart-with-breath RSA) is identical to v2 — those parts of the design are mature and didn't need changes.

---

## What's different from v2

| Concern | v2 | v3 |
|---|---|---|
| Drift targets | Heart rate + Breath rate (2 total) | Heart rate + S1-S2 gap + Inhale + Top pause + Exhale + Bottom pause + RSA depth + Breaths/min + Inhale Freq + Exhale Freq (10 total, v2.14) |
| Drift sliders | 6 (Heart up/down/period + Breath up/down/period) + 1 shape = 7 | 5 (target + up + down + period + shape) |
| Sighs | none | Yes (interval + depth multiplier, multiplier scales ALL four segments) |
| Heart-with-breath baseline | slider 56 | slider 59 (moved to make room for the new drift block) |
| Drift configs persist across save/load | n/a (per-slider) | Yes (via `@serialize`; all 10 targets' configs preserved) |
| Speed ramp shape | one scope (scales all 3 layers together via a multiplier) | **nested-selector pattern: pick which target to ramp, set a signed amount.** Every target is additive — each ramp affects only its own parameter. |
| Speed ramp amount semantics | multiplier 0.1-4.0 (destination scaling) | signed delta in target's natural units (0 = no change, negative = decrease, positive = increase) |
| Speed ramp behavior on transport play | resets implicitly via @init re-run | resets explicitly via play-edge detection (so drift state stays continuous while ramp restarts cleanly) |
| Audio sliders (1-47) | unchanged | unchanged |
| Speed ramp sliders | 48-51 (multiplier / duration / engage / start delay) | 48-52 (target / amount / duration / engage / start delay — note: amount is NEW) |

Migration from v2: the audio-shaping sliders 1-47 keep their meaning, so the heart sound, breath sound, bloodflow, and per-layer gates all carry over unchanged. Everything from slider 48 onward needs to be re-entered — v3 changed the layout substantially (Speed Ramp added an amount slider and switched to signed-delta semantics; BPM rescale shifted from slider 52 to slider 53; the drift block is now nested-selector at sliders 54-58; RSA moved to slider 59; sighs are new at sliders 60-61).

---

## Signal Architecture

Identical to v2 for the three audio layers (see [Womb Sound Generator v2 → Signal Architecture](#womb-sound-generator-v2) for the full description). The change is in **how the drift modulations are computed and applied**:

Each of the 10 drift targets has its own phase counter advancing per sample. The phase advance scales with Speed Ramp so all drifts slow together when Speed Ramp engages. Per-target up amount, down amount, period, and shape are stored in a per-instance memory bank — the slider 55-57 values you see at any moment reflect whichever target is currently selected.

Target indices and units:

| Target | Index | Up/Down units | Period units |
|---|---|---|---|
| Heart rate | 0 | BPM | heartbeats |
| S1-S2 gap | 1 | ms | heartbeats |
| Inhale | 2 | seconds | breath cycles |
| Top pause | 3 | seconds | breath cycles |
| Exhale | 4 | seconds | breath cycles |
| Bottom pause | 5 | seconds | breath cycles |
| RSA depth | 6 | BPM peak-to-peak | breath cycles |
| Breaths/min | 7 | breaths/min (scales all 4 segments in lockstep, I:E preserved) | breath cycles |
| Inhale Freq | 8 | Hz (inhale breath-noise filter cutoff — brightness) | breath cycles |
| Exhale Freq | 9 | Hz (exhale breath-noise filter cutoff — brightness) | breath cycles |

Each drift offset is added to the target's baseline slider value per sample. For example: with Heart rate target's up/down at 5/5 and a period of 8 heartbeats with Sine shape, the effective BPM each beat wanders within ±5 of the baseline slider 1 value, completing one full sine over 8 beats.

---

## Parameters

### Global Controls

Sliders 1-47: identical to [Womb Sound Generator v2](#womb-sound-generator-v2). See that section for full descriptions of BPM, the three layer Volume / Solo sliders, heartbeat sound parameters (Systole ms, S1/S2 Frequency Hz, Decay ms, Brightness, Stereo Width ms), breath sound parameters (Inhale/Top Pause/Exhale/Bottom Pause durations, Frequencies, Fade In/Out, Stereo Width, Post-filter), bloodflow parameters (Filter Hz, Dicrotic Level, Resonance, Attack, Decay, Stereo Width), Start Delay, and per-layer Play/Rest gates.

Sliders 48-52 are the Speed Ramp block, sliders 54-58 are the Drift block, slider 53 is BPM rescale, slider 59 is Heart-with-breath / RSA depth, sliders 60-61 are the Sigh mechanism — all described below.

### Drift target selector (slider 54)

`Drift target` — pick which parameter the drift sliders 55-58 are currently configuring. Options: **Heart rate**, **S1-S2 gap**, **Inhale**, **Top pause**, **Exhale**, **Bottom pause**, **RSA depth**, **Breaths/min**, **Inhale Freq**, **Exhale Freq** (last three v2.14).

Switching the selector saves the current values of sliders 55-58 to the previously-selected target's memory slot, then loads the newly-selected target's saved values into the sliders. So you never lose any target's configuration — it just gets hidden when you switch to another target. **All ten configured drifts run in parallel** regardless of which one you're currently editing.

**Inhale Freq / Exhale Freq (breath brightness).** These wander (or ramp) the breath-noise filter cutoff for the inhale and exhale — the breath's *brightness*. Low = dark/muffled, high = bright/airy. Units are Hz (base 250 inhale / 170 exhale, range 50–2000). A big up/down or a Speed Ramp on these lets the breath brighten and darken over time — the "breath timbre" journey natively, no external automation. Because the shared drift up/down and Speed Ramp `by` sliders must also serve the Hz-scale frequency targets, their ranges are wide (drift 0–2000, `by` ±2000); that makes them coarser for the small-value targets (a −35 BPM ramp is a small nudge on the ±2000 slider) — the one-slider-serves-all tradeoff.

**Breaths/min (aggregate target).** Unlike the four individual segment targets, this one scales **all four breath segments in lockstep**, preserving the inhale:exhale ratio — it wanders (Drift) or winds (Speed Ramp) the *whole breath rate* as one felt control, in breaths per minute (signed: negative = slower). It composes with the per-segment targets, so you can, e.g., slow the overall breath rate while independently drifting just the top pause. It's the live-modulation cousin of the one-way "Breaths per minute" setup slider (53), which rewrites the four duration sliders once and then reads 0 again — use slider 53 to dial a starting rate, use this target to move it over time.

### Drift up amount (slider 55)

`Drift up amount (units match target)` — peak amplitude the current target wanders ABOVE its baseline. Range 0-2000 step 0.1 (widened in v2.14 to reach the Hz-scale frequency targets); the unit depends on the target (BPM for Heart rate and RSA depth, ms for S1-S2 gap, seconds for breath segments, breaths/min for Breaths/min, Hz for Inhale/Exhale Freq). 0 disables the upward swing.

### Drift down amount (slider 56)

`Drift down amount (units match target)` — peak amplitude the current target wanders BELOW its baseline. Same range and unit-by-target as Up. Setting Up and Down to different values gives biological-feel asymmetry around the baseline. Setting both to 0 disables drift for this target entirely.

### Drift period (slider 57)

`Drift period (heartbeats or breath cycles)` — how many parent-rhythm cycles one full drift wave takes. Range 1-1000 step 1. The unit auto-matches the target: heartbeats for Heart rate and S1-S2 gap, breath cycles for the four breath segments and RSA depth.

Period 1 with Random shape gives beat-to-beat (or breath-to-breath) jitter — each cycle gets a fresh random value within the up/down range.

### Drift shape (slider 58)

`Drift shape` — wave shape for the drift modulation. Options:

- **Sine** — smooth continuous wander, equal time on either side of baseline.
- **Triangle** — linear ramps with turnaround points at the peaks.
- **Random** — value noise that interpolates smoothly between random targets at each period boundary. Random targets are independent per-target (each of the 10 wander-targets has its own random state).

### Heart with breath (slider 59)

`Heart with breath (BPM peak-to-peak)` — baseline RSA coupling depth. Identical semantics to v2's slider 56 (moved to slider 59 in v3 because the drift block needed those slots). 0 = no RSA. A value of 6 means HR climbs ~3 above baseline at the peak (top of inhale) and descends ~3 below at the trough (bottom of exhale).

When drift target 6 (RSA depth) has nonzero up/down values, this baseline depth wanders too — the up/down amplitudes are in the same BPM peak-to-peak units.

### Speed Ramp (sliders 48-52)

Speed Ramp in v3 uses the nested-selector pattern (same shape as Drift) and all five Speed Ramp sliders live in one place. Pick a target on slider 48, set the amount on slider 49, set the duration and engage. The targets and their natural units:

| Selector | Target | Amount unit |
|---|---|---|
| 0 | Heart rate | BPM |
| 1 | S1-S2 gap | ms |
| 2 | Inhale Duration | seconds |
| 3 | Top Pause | seconds |
| 4 | Exhale Duration | seconds |
| 5 | Bottom Pause | seconds |
| 6 | RSA depth | BPM peak-to-peak |
| 7 | Breaths/min | breaths/min (scales all 4 segments together, I:E preserved) |
| 8 | Inhale Freq | Hz (inhale breath-noise brightness) |
| 9 | Exhale Freq | Hz (exhale breath-noise brightness) |

**Amount is a signed delta, not a destination.** 0 means no ramp (safe default — engaging while at 0 does nothing). Negative means decrease this parameter — slower heart, shorter inhale, less RSA swing. Positive means increase — faster heart, longer inhale, more swing. Whatever you type is how far the parameter moves from its current value over the duration. To slow heart from 70 to 35, set Heart rate target and an amount of -35. To stretch inhale from 4 sec to 8 sec, set Inhale target and +4.

**All targets are additive — they ramp only their specific parameter.** Speed Ramp is for independent fine-tuning, not organism-wide scaling. Selecting Heart rate with amount -35 ramps just the heart down by 35 BPM; the breath cycle stays at its base rate, top/bottom pauses stay at their base, RSA depth stays where you left it. Bloodflow follows the heart automatically (it's phase-locked by design), so a Heart rate ramp does also slow bloodflow — but breath does NOT auto-slow.

If you want the v2-style "whole womb winds down together" feel where everything slows in coordinated lockstep: configure a `by` amount on each target you want to ramp (Heart rate and the breath segments most likely), then engage. All 10 targets' ramps run in parallel over the same duration, so configuring multiple targets gives you a coordinated multi-parameter wind-down. The selector is just for editing — switching it does NOT stop ramps already running on other targets (same model as drift).

#### Sliders

- **slider 48 — Speed ramp target** — the 10-option selector (v2.14 adds **Breaths/min**, **Inhale Freq**, **Exhale Freq**). Changing it saves the current slider 49 amount to the previous target's memory slot, then loads the new target's saved amount into slider 49. So you can configure multiple targets in sequence and switch between them without losing settings.

  **All 10 ramps run in parallel** (same model as drift). The selector is just for editing — switching it does NOT stop a ramp already running on another target. If you set Heart rate `by` -35 and Inhale `by` +4 and engage, both ramp together over the same duration. Targets you haven't configured stay at amount 0, which is a no-op. The **Breaths/min** target rides the whole breath rate (all four segments in lockstep, I:E preserved) in breaths per minute — e.g. `by` -4 winds the breath from 8/min down to 4/min over the duration; the wind-down move for a dysregulated→resting descent. The **Inhale Freq / Exhale Freq** targets ride the breath's *brightness* (breath-noise filter cutoff, Hz) — e.g. Inhale Freq `by` -200 darkens the in-breath from 250 Hz airy down to ~50 Hz muffled over the duration; the breath-timbre journey natively.

- **slider 49 — Speed ramp by** — signed delta in the selected target's natural units. Range -2000 to +2000, step 0.1 (widened in v2.14 to reach the Hz-scale Inhale/Exhale Freq targets; coarser for the small-value targets as a result). **0 = no change, negative = decrease, positive = increase.** Reads as a sentence with the selector: *"Speed ramp by -35, target Heart rate."* Examples:
    - Heart rate target, amount -35: heart ramps DOWN 35 BPM from wherever it started (70 → 35).
    - In **Host x** this is still BPM — the amount never becomes a multiplier, so `-35` stays `-35 BPM` whatever the project tempo does. HRV figures are real quantities you'd read off a page, and ±5 BPM of variability should stay ±5 BPM rather than growing because the project sped up. (Same reasoning as RSA depth, which is a BPM swing in every mode.)
    - Inhale target, amount +4: inhale ramps from 4 sec → 8 sec.
    - Bottom Pause target, amount +2: bottom pause stretches by 2 seconds.
    - RSA depth target, amount +6: RSA swing grows by 6 BPM peak-to-peak.

  Each target stores its own amount, so configuring an amount for Heart rate, switching to Inhale, configuring there, and switching back to Heart rate brings back the original Heart rate amount.

- **slider 50 — Speed ramp duration (minutes)** — **per-target** (v2.14): how long the *selected* target takes to travel from baseline to baseline + `by`. Range 0-60 minutes; 0 = that target doesn't ramp. Each target has its own duration (saved/loaded by the selector, like `by`).

- **slider 51 — Speed ramp engage** — Off/On, **global**: one switch arms every configured target, each riding its own duration after its own start delay. Freeze/resume gate: when On, each target's clock advances; when Off, all freeze and resume on re-engage. Engage does NOT reset the ramps — only transport play does (each play press starts fresh from 0). You can switch the selector mid-ramp without affecting any running ramp.

- **slider 52 — Speed ramp start delay (minutes)** — **per-target** (v2.14): wait this many minutes after engage before *this* target begins moving. Range 0-60. Stagger targets by giving them different start delays (e.g. Heart rate starts at 0, breath brightness at minute 10). Useful for "let me fall asleep first, then begin the wind-down."

As of v2.14 the ramp is **fully per-target**: `by`, duration, and start delay are all per-target, so different targets can wind down over different timelines from a single engage — the coordinated multi-parameter wind-down that makes the nervous-system journey renderable natively.

#### How ramp_t works

While engaged and past the start delay, `ramp_t` advances from 0 to 1 over the configured duration. At any moment, the offset applied to the selected target is `ramp_t × amount`. So:

- ramp_t = 0 → offset = 0 → no change to the target's value
- ramp_t = 1 → offset = amount → target's effective value = baseline + amount
- in between → linear interpolation

When disengaged, ramp_t freezes at its current value — the system holds the partial ramp. Re-engaging resumes from the frozen value (engage is a gate, not a restart). The only thing that resets ramp_t to 0 is a transport play edge.

#### Speed Ramp + Drift + Sighs

Speed Ramp, Drift, and Sighs all compose at the parameter consumption sites:

```
effective_inhale_sec = baseline_slider16 + drift_offset[2] + speed_ramp_inhale_offset
```

Drift wanders the segment cycle-to-cycle. Speed Ramp adds a one-way movement (the amount, scaled by ramp_t) on top. Sigh multiplies the resulting (drifted + ramped) length by the sigh multiplier when a sigh is in progress. All three layers stack independently — drift continues during a ramp, sigh continues during a ramp, the underlying physiology stays alive.

For Heart rate specifically: drift, RSA, and Speed Ramp heart offsets all add to the smoothed BPM in raw BPM units. So a Heart rate ramp of -35 BPM still has drift wandering ±5 BPM around the trajectory, and RSA still modulates ±3 BPM around that, all the way through the ramp. Organic at every moment — the drift's absolute size doesn't change as the ramp progresses (whereas in a multiplicative design, drift would scale with the ramped rate, making it feel different at the endpoint vs the start).

#### Migration from v2's Speed Ramp

v2 had one Speed Ramp scope that scaled all 3 layers proportionally (target = multiplier 0.1-4.0). v3 splits that into 7 explicit additive targets — there is no longer a "scale everything together" mode. The closest equivalent of v2's "ramp everything to 50% over 10 minutes" is to configure Speed Ramp on Heart rate AND independently set breath drift / Speed Ramp on the breath segments to slow them too. The slow-down isn't automatically propagated because Speed Ramp's intent in v3 is independent fine-tuning, not organism-wide scaling.

This is a deliberate departure from v2. If the v2 "whole organism wind-down" feel is what you actually want, the workflow is: ramp Heart rate via Speed Ramp, AND set drift on each breath segment so they wander into longer values over time. Or — simpler — for a coherent wind-down, leave breath drift off and just ramp Heart rate; the heart slows while breath stays at its natural rate. Real physiology actually does this: breath and heart DON'T always slow together; they're separate rhythms with their own variability.

---

### Sigh interval (slider 60)

`Sigh interval (minutes, 0=off)` — average minutes between sighs. Range 0-30 step 0.1. 0 disables sighs entirely (no event ever fires).

When the timer reaches the configured interval, the NEXT breath transition (state 3 → state 0, end of bottom pause → start of new inhale) flags that breath as a sigh. The flag stays set through the entire sigh breath — inhale, top pause, exhale, bottom pause — and clears at the next 3→0 transition (where a new sigh may fire immediately if the timer crossed threshold again).

The timer scales with Speed Ramp — so when Speed Ramp slows the whole womb down, sigh interval slows along with it. (Specifically: every sample, `sigh_time_since_last += (1/srate) * speed_scale_current`.)

### Sigh depth multiplier (slider 61)

`Sigh depth multiplier` — how much longer each segment of the sigh breath is, compared to a normal breath. Range 1.0-3.0 step 0.05. 1.0 = no stretch (effectively disables sighs even with a nonzero interval); 1.5 = sigh breath is 1.5× longer in every segment; 3.0 = 3× longer. Default 1.5.

**All four segments stretch uniformly** — inhale, top pause, exhale, and bottom pause all get multiplied by the same value. The whole sigh breath is "more breath" — same shape as a normal breath, just longer and consequently deeper (the inhale envelope rises higher under the same fade curves applied over a longer span). I:E and pause ratios are preserved during the sigh, which matches the observed shape of real sighs (the entire breath cycle elongates, not just one phase).

**Drift continues to apply through the sigh.** Each segment's length at state entry is `(current drifted length) × slider61` — so a sigh that fires during a "longer inhale" portion of the breath-drift wander is even longer, while a sigh during a "shorter inhale" portion is correspondingly shorter. The sigh inherits the live drift state; it doesn't lock to a snapshot.

---

## Workflow tips

### Configuring drift across multiple targets

1. Set slider 54 to the target you want to drift first (e.g. Heart rate).
2. Set sliders 55-58 (up amount, down amount, period, shape) for THAT target.
3. Change slider 54 to the next target. Sliders 55-58 will snap to fresh values (defaults for an unconfigured target, or whatever you set previously if you've already touched that target).
4. Set 55-58 for the new target. The previous target's values are saved automatically.
5. Repeat for as many targets as you want. They all run in parallel.

If you ever want to **disable** a target's drift without losing its configuration: select it, set Up amount AND Down amount to 0. The target is now effectively muted but its period and shape are still remembered for later.

### Sigh + drift together

Sighs and drift compose multiplicatively. The drift system wanders each segment's length per sample; when a sigh starts (state 3 → 0 transition), each subsequent state's length is set as `(current drifted length) × slider61`. So a sigh that fires when breath drift has the inhale at its peak makes for a particularly long inhale; a sigh that fires when drift has the inhale at its trough is correspondingly shorter. The sigh isn't a frozen island — it inherits whatever organic wander is current.

Heart drifts (Heart rate, S1-S2 gap, RSA depth) are independent of sigh state and continue running normally through the sigh breath. The heart wanders even while a sigh is in progress.

### Period 1 + Random for beat-to-beat jitter

Want each heartbeat to be ±5ms off from a metronome? Configure: Heart rate target, Up 0, Down 0, Period 1, Random shape — except that wouldn't do anything with up=0 down=0. Pick: Heart rate target, Up 5, Down 5, Period 1, Random. Each heartbeat gets a fresh random value in the ±5 range, interpolated within that single beat's duration.

Same trick works for S1-S2 gap (beat-to-beat systole length jitter), or for any of the breath segments (cycle-to-cycle pause-length jitter etc.).

### RSA depth wander

To make the RSA coupling itself feel alive rather than mechanically constant, set slider 54 to RSA depth (target 6), give it a small up amount (e.g. 2 BPM) and a long period (e.g. 20 breath cycles). The RSA depth slowly wanders over the course of ~20 breaths, deepening and shallowing — matches real physiology where RSA strength rises with relaxation and decreases with tension.

---

## Notes worth knowing

- **Drift configurations persist across project save/load** via `@serialize`. All 10 targets' configs are written into the project file (about 40 numeric values total — negligible storage). Reopening a project restores every target's drift settings, not just the last-edited one.
- **`ext_noinit = 1`** at the top of `@init` keeps the drift memory banks alive across transport play, so configured drifts don't reset every time you press the play button.
- **Drift phases have small random offsets at @init** so the 10 drift waves don't all start at zero crossings in sync — first-listen feel is more organic.
- **The selector counts as a slider edit** in REAPER's automation sense. If you change target via slider 54, sliders 55-58 will fire `slider_automate` callbacks as their values change. This is intended — it lets the slider state stay accurate for save/restore.
- **Heart rate drift modulates effective BPM**, which means it interacts with Speed Ramp (multiplied together for the heart's final rate) and with RSA (added together). The display BPM remains your slider 1 value; the drift offset is applied at the audio path layer.
- **Solo and Volume affect drift output the same way they affect normal output** — drift doesn't bypass any layer mixing.

---

## Limitations and known behavior

- **A single Shape per target.** Each target's shape (Sine / Triangle / Random) is stored independently, but within a target you pick ONE shape. There's no "Sine on Up, Triangle on Down" combo — the same shape governs the full wave.
- **Drift up/down range is 0-2000** (widened from 0-50 in v2.14 to reach the Hz-scale Inhale/Exhale Freq targets). One range serves every target, so the unit changes per target (BPM, ms, seconds, breaths/min, Hz) while the range stays the same. The wide cap makes the slider coarser for the small-value targets (a 5 BPM drift is a small move on a 0-2000 slider), the one-slider-serves-all tradeoff — you navigate by value, not by slider feel.
- **Sigh and drift compose multiplicatively, not as separate visible layers.** Drift wanders the segment lengths; sigh multiplies the current drifted lengths by slider61 at state entry. There's no separate "sigh wave" you can examine independently — sigh is just "this breath gets bigger." If you want to test sigh shape in isolation, set all drift up/down to 0 first so only the baseline segment values are scaled by the sigh.
- **First-load defaults.** Targets that haven't been configured yet hold zeros (no drift). This means the first time you open v3, all ten targets show 0 up / 0 down / period 8 / shape Sine — nothing wanders until you start configuring.

---

*Womb Sound Generator v3 is part of the Rozaya JSFX plugin suite.*
*Designed by Rozaya — Developed with Claude (Anthropic)*


---


### Host tempo sync

**Rate Mode** `Own BPM / Host x` (default Own BPM)
**Own BPM** is the original behaviour — free-running, project tempo ignored.
**Host x** hands the timing to the project tempo. Tempo changes apply live.

Only two entries rather than the four in Melody Phase / Polyrhythm, because this
plugin only ever had one unit — "Seconds" and "Hz" would be meaningless here.

**The whole body follows the tempo**, not just the heart: the heart scales,
bloodflow is locked to the heart, and the breath cycle is set in beats. One body,
and the heart and lungs of one body don't disagree about how fast time is passing.

**Host sync target** `Heart rate` (default Heart rate)
**Every N beats (Host x)** `0.25 to 64, step 0.01, default 1`

The numbers live in the plugin's own memory and are saved with your project,
the same way Drift stores a setting for each of its ten targets behind four
sliders. One target today; the list grows by adding targets, not controls.

**The breath is not on this list, and does not need to be** — see below.

Two controls, sitting directly under Rate Mode, and they cover both rates. Pick
the target, set how many project beats one cycle of it takes, move on. Pick the
other target to set that one — the first keeps running exactly as you left it,
the same way switching Drift's target doesn't stop the other drifts.

**The breath works differently, and more simply: its four sliders ARE beats in
Host x.** Inhale 4, top pause 0.5, exhale 8, bottom pause 1 is a breath of 13.5
beats — four beats in, eight beats out, exactly as written. Nothing to set the
total with, because the total is the sum, which is the same rule Own BPM has
always used with seconds.

That is the whole unit change: **seconds when free-running, beats when synced**,
and the slider names say so. Slow the project from 120 to 30 and that breath
stretches from 6.75 seconds to 27 — same 4-and-8, more real time each.

**Switching modes converts them for you**, so entering or leaving Host x sounds
identical: a 4-second inhale at 120 BPM becomes an 8-beat inhale, which is the
same 4 seconds. The numbers move because their unit moved; the breath does not.

**Systole works the same way.** `Systole (ms / beats in Host x)` is the gap
between the lub and the dub. In Host x it is in beats, so both halves of the
heartbeat land where you put them: `0.25` puts the dub a quarter-beat after the
lub, `0.5` exactly halfway to the next beat — and that stays true at any tempo,
which is the thing a millisecond value can never do. The default 120 ms converts
to 0.24 beats at 120 BPM, so switching modes changes nothing you can hear.

| in beats | what you hear | at 60 BPM | at 120 | at 180 |
|---|---|---|---|---|
| 0.125 | an eighth of a beat after the lub | 125 ms | 62 ms | 42 ms |
| 0.25 | a quarter-beat after | 250 ms | 125 ms | 83 ms |
| 0.5 | halfway to the next beat | 500 ms | 250 ms | 167 ms |

Note the physiological caveat: a real systole stays roughly constant as heart
rate changes rather than scaling with it, so a beats value is the *musical*
choice, not the anatomical one. Own BPM keeps milliseconds for when you want the
body to be right. A heartbeat every 1 beat at 70 BPM is 70 BPM.

**It is not a grid.** The beats value is a plain continuous number, so one cycle
every **5** beats of a 4/4 track is exactly as reachable as 4 — and so is 5.3,
which is how you set two instances slipping slowly against each other. The step
is 0.01 because in REAPER's parameter list you can only arrow, never type, so a
value the step can't land on is a value that doesn't exist.

**Heart rate stays visible and stays live.** It reads in BPM in Host x just as it
does in Own BPM — it is never a multiplier of anything now — so it shows what the
sync is actually running at, and it follows the project tempo as that moves.
Moving it by hand converts back into beats rather than being ignored: the two are
two views of one number and whichever you moved is the one that wins.

**Switching into Host x does not change what you hear.** Both layers land on
continuity: the heart converts the BPM it already had into the beats that
reproduce it at this tempo, and the breath takes the cycle its four duration
sliders already describe. The tempo simply takes over from there.

### Which controls are true, and when

**Rate Mode is the only thing that decides this**, for both layers.

| | **Own BPM** | **Host x** |
|---|---|---|
| Heart rate | BPM you set | BPM, derived from beats × tempo — still shown, still settable |
| Breath rate | the four durations add up to it | set in beats by *Every N beats* |
| Inhale / Top pause / Exhale / Bottom pause | **literal seconds** | the **ratio** fitted into the cycle |
| Breaths per minute | rewrites the four durations | **hidden** — does not apply |

The four breath sliders say it on the tin: **`Inhale (sec, ratio in Host x)`**.
Free-running, they're literal seconds. Synced, the cycle is however many beats you
asked for and those four numbers set the **ratio** of it — inhale to top pause to
exhale to bottom pause. What matters is 4:0.5:8:1, not that it adds to 13.5.

**This is why a tempo change stretches your breath instead of breaking it.**
Slow the project down and the cycle gets longer, so every part of the shape grows
in proportion — a 4-0.5-8-1 breath stays a 4-0.5-8-1 breath, just slower. The
inhale passes 4 seconds, the exhale passes 8, and the pauses stretch with them.
Nothing about the feel of it changes; only the clock does.

They stay in **seconds** rather than becoming percentages for a reason worth
recording: 4, 0.5, 8 and 1 are numbers you can feel and enter directly. The same
breath written as shares is 29.6 / 3.7 / 59.3 / 7.4, and the only way to reach
those is to divide each one by 13.5. The seconds are the interface; converting
them away to make the internals tidier would be paying in arithmetic for nothing.
(Decided 2026-08-30, after exactly that change was proposed and rejected.)

Drift and Speed Ramp keep working on every breath parameter in both modes, and
breath drift periods are counted in the breath cycles you can actually hear. The
sigh timer is the one deliberate exception: a 5-minute sigh interval is five real
minutes at any tempo.

---

#### What replaced the ratio menus (2026-08-30)

Host x used to carry two named-ratio pickers — *Host ratio* for the heart and
*Breath rate* for the breath — each writing into a number that hid behind it.
Three problems, and the replacement above fixes all three:

- **A menu of ratios is a grid.** Its entries were fixed fractions of the beat, so
  *every 5 beats* was not on the list at all — in a suite whose whole subject is
  layers slipping against each other.
- **A picker that hides its value is a gate, not a shortcut.** The free number was
  reachable only by first finding the entry called *Custom*.
- **One picker could only ever point at one rate.** The breath needed a second
  pair of controls purely because the heart's picker couldn't point at it.

**Existing projects migrate themselves.** In Host x the heart rate used to be a
*multiplier* of the tempo; it is plain BPM now. A project saved under the old
build is detected on load and converted — the heart keeps the rate it had, and
the beats it implies are filled in for you. Nothing to run, and it works on any
machine. Save the project once and the conversion stops happening.

Two things do need re-setting by hand in a project saved under the old build:
the **Host sync target** may land somewhere arbitrary (it inherited the old
*Host ratio* slider's slot), and if you had set a **breath** rate, check it.
The heart's rate carries over untouched.
