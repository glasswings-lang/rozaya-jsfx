# Polyrhythm Phase v3 (Note-Based)

**Designed by Rozaya — Developed with Claude (Anthropic)**

---

## Overview

Polyrhythm Phase v3 is a binaural oscillator with up to eight simultaneous voices, each tuned to a specific musical pitch. Each voice generates a stereo pair of oscillators with a slight frequency offset between the left and right channels — the binaural beat — producing entrainment tones that shift in perceived frequency as the beat interacts with the listener's auditory system. A shared tremolo envelope modulates the amplitude of all voices, with per-voice drift or independent rate options creating polyrhythmic relationships between them. A pan modulation system adds either continuous spatial movement (Tremolo / Increment) or static spread positions (Spread / Spread Reversed) per voice.

The plugin generates no audio from an input signal. It is a pure synthesizer.

**How v3 differs from v2.** The engine is identical — same oscillators, same
tremolo, same drift, same everything you hear. The difference is entirely in
how you set pitch. In [v2](polyrhythm-phase.md), each voice takes a *semitone
offset* counted from a base note, so placing a voice means working out how far
it sits from an anchor. In v3, each voice simply **names its note** — you pick
`G4` from a list — and a separate **Fine tune** control nudges it off that
note in cents. No counting, no offsets, no theory. A cent is one hundredth of
a note step, so `+100` cents is exactly one note up, and every value you touch
is a whole number.

The two versions do not share project data — slider numbers differ, so a
saved project using one will not open correctly under the other. Both ship
in the suite; pick whichever mental model fits the piece, per project.

---

## Signal Architecture

Each active voice runs two oscillators — one for the left channel at the voice's base frequency, one for the right channel at the base frequency plus the binaural beat offset. Both oscillators use the same waveform. The tremolo LFO modulates their shared amplitude using a gated envelope with configurable attack and release shapes. Per-voice gain is applied before the voice's contribution is summed into the output.

All active voices are summed and normalized by the active voice count, keeping the output level consistent regardless of how many voices are enabled.

When pan is enabled, each voice's left and right oscillator outputs are panned independently using separate amplitude multipliers, preserving the binaural beat relationship between channels. The left channel signal is scaled by the cosine of the pan position and the right by the sine, maintaining constant power across the field.

---

## Parameters

### Global Controls

**Tremolo Mode** `Drift / Independent`
Sets how each voice's tremolo rate is determined.

- **Drift** — all voices share a base value (Rate Value, read in whatever unit Rate Mode selects), and each voice adds its own Drift / Rate on top. **This voice's value = Rate Value + that voice's Drift.** So in Host x with Rate Value 4, a voice at 0 cycles every 4 beats and a voice at +1 cycles every 5.

  **Which direction that moves depends on the mode.** In BPM and Hz a bigger number is faster, so positive drift speeds a voice up. In Seconds and Host x a bigger number is a longer gap, so positive drift **slows it down**. The offset is always added; what adding means changes with the unit.

  **With every voice's Drift at 0 — the default — all eight voices are identical** and cycle in lockstep, which sounds like one voice rather than a polyrhythm. The drift values are what create the polyrhythm; without them there isn't one.

> **Direction reverses in Host x.** Rate Value and Drift are in *beats* there, and more beats means slower — so a **positive** drift makes a voice **slower**, not faster. That is the same way Seconds mode already behaves, where a bigger number is a longer period. BPM and Hz go the other way. Worth knowing before you tune drift by ear in a synced project.
- **Independent** — the global Rate Value is hidden. Each voice's Drift / Rate slider sets that voice's tremolo rate directly in the units selected by Rate Mode. Voices can run at entirely different rates with no shared reference.

**Rate Mode** `BPM / Seconds / Hz / Host x` — Rate Value carries the mode's unit: BPM, seconds, Hz, or beats per cycle.

### Host x — following the project tempo

In the first three modes each instance holds its own absolute rate, and nothing
in the plugin knows another instance exists. That's fine until you want to
change the speed of a whole arrangement: nudging each one by hand changes the
*relationships* between them, not just the pace, and layers that used to nest
start scattering. Restarting the transport can't fix that — restart resets
phase, not ratio.

**Host x** makes Rate Value mean **beats per cycle** — the same way it means BPM
in BPM mode and seconds in Seconds mode. Set it to 4 and you get one cycle every
four beats; set it to 0.5 and you get two cycles per beat. It follows the
project tempo, and tempo changes carry the setting with them.

Fractions are free: *every 3.7 beats* is as reachable as *every 4*, which is the
point.

**Switching into Host x lands Rate Value on 4** — one cycle per bar in 4/4 — because the slider's default of 60 was chosen for BPM mode and means *one cycle every sixty beats* when read as beats, which is half a minute at 120 BPM and too slow to identify by ear. It only does this when you actually change mode, never when a project opens, so a rate you set by hand is never overwritten. This suite is phase music — the value in layers slipping against each
other — so nothing here forces you onto a note grid.

**Host ratio** — *retired 2026-09-02.* It existed to spare you arithmetic on a multiplier; with Rate Value in beats, *every 4 beats* is typing 4. The control is hidden and does nothing. It stays in the parameter list only because slider IDs can never be renumbered.

**Rate Value (Drift only)** `0.001-1000, default 60`
The global base tremolo rate, in the units set by Rate Mode. Only visible in Drift mode. Individual voice drift values are added to this.

**Binaural Beat Hz (L/R offset)** `0-100 Hz, default 4`
The frequency difference between each voice's left and right oscillators. At 4 Hz, the left oscillator runs at the voice's base pitch and the right runs 4 Hz higher, creating a 4 Hz binaural beat when heard on headphones. This value is the same for all voices simultaneously.

**On Duration % of Cycle** `0-100%, default 100`
The proportion of each tremolo cycle during which each voice is in its active state (including attack and release). At 100% the tremolo never fully closes. At 50% each voice is present for half its cycle.

**Attack % of Cycle** `0-100%, default 0`
Proportion of the on-time spent in the attack ramp, fading from silence to full amplitude.

**Release % of Cycle** `0-100%, default 100`
Proportion of the on-time spent in the release ramp, fading from full amplitude back to silence. The default of 100% with 0% attack produces a ramp-down envelope — each voice fades out across its full on-time with no hold. Adjusting both attack and release creates a shaped pulse.

> If Attack % + Release % exceeds 100% of the on-time, both are scaled down proportionally so their sum fits within the on-duration.

**Attack Shape** `Linear / Cosine / Logarithmic / Exponential`
Curve shape applied to the attack ramp.

**Release Shape** `Linear / Cosine / Logarithmic / Exponential`
Curve shape applied to the release ramp.

**Depth dB** `-60-0 dB, default -6`
How far each voice drops in amplitude at the bottom of its tremolo cycle. At 0 dB there is no tremolo depth. At -60 dB voices are effectively silenced at the trough.

**Transpose (half steps)** `-12 to +12, default 0`
Shifts every voice up or down by whole note steps, without touching any voice's
own Note setting. At the default of 0, each voice sounds exactly the note it
names. `+2` moves the whole set up two steps; `-12` drops everything one octave.
Use it to move a finished arrangement into a different key in one control.

**Octave shift** `-4 to +4, default 0`
Shifts every voice by whole octaves. Same purpose as Transpose, in bigger steps.
The two stack: Transpose `+2` with Octave shift `-1` moves everything down an
octave and back up two steps.

**Tuning Reference Hz** `400-480 Hz, default 440`
The reference pitch used to calculate all voice frequencies. At 440 Hz, A4 = 440 Hz and all other pitches follow standard equal temperament from that anchor. Adjusting this shifts all voices simultaneously without changing their relative intervals.



---

### Per-Voice Controls (Voices 1-8)

Each voice has six parameters. By default V1 is audible (Gain -6 dB, Active On), V2 is active but silent (Gain -60 dB, Active On — counted in normalization but contributes nothing audibly until you raise its gain), and V3-V8 are inactive (Active Off — bypassed entirely with no CPU cost).

**Vn Gain dB** `-60 to +6 dB, default -6 for every voice`

Changed 2026-08-31. Every voice used to default to -60 (silence) except V1, so activating a voice handed you nothing and a 54 dB climb to get it back. `Vn Active` is the on/off; the gain never needed to be one too. A fresh instance still sounds identical -- only V1 is Active by default -- but any voice you switch on is now audible straight away, and you trim down rather than build up.
Per-voice output level applied before the voice is summed into the mix. -60 dB is effectively silent. Use this to balance voices relative to one another. To fully cut a voice with no CPU cost, prefer Vn Active = Off rather than gain at -60.

**Vn Note** `C2 to C6, default C4`
The note this voice plays, by name. Step through the list and pick one — there
is nothing to calculate and no anchor to count from. The range spans four
octaves, low enough for drones and high enough for shimmer. The left oscillator
runs at this note's frequency; the right runs at the same frequency plus the
Binaural Beat Hz offset.

Global **Transpose** and **Octave shift** move this voice along with all the
others; at their defaults the voice sounds exactly the note shown.

**Vn Fine tune (cents)** `-100 to +100, default 0`
Nudges the voice off its named note, in cents. **One hundred cents is exactly
one note step**, so `+100` here lands on the next note up and `-100` on the next
one down — which means every pitch is reachable, whichever note you picked.

This is the control for detuning voices against each other. Two voices on the
same Note with one of them a few cents off will beat slowly against each other;
the further apart, the faster the beating. Set it by ear — nudge until it sits
where you want. Whole numbers throughout, no decimal point.

**Vn Drift / Rate** `-1000 to +1000, default 0`

**In Drift mode** this is an *offset* added to Rate Value, never a value on its own. 0 means this voice runs at exactly the base — not stopped. Whether a positive offset speeds the voice up or slows it down depends on the unit: faster in BPM and Hz, **slower in Seconds and Host x**, where a bigger number means a longer gap.

**In Independent mode** this *is* the voice's value, directly, in whatever unit Rate Mode selects — Rate Value is ignored entirely. Here 0 does mean effectively stopped, in every mode. In Host x it is a beat count: 4 is one cycle every four beats.

**Vn Phase Offset** `-1000 to +1000, default 0`
When this voice becomes audible within its tremolo cycle, in the units set by Rate Mode (BPM = beats, Seconds = seconds, Hz = cycles). Offset 0 fires the voice immediately at playback start; offset 8 in Seconds mode means the voice waits 8 seconds before becoming audible. Values wrap freely — there is no clamping.

**Vn Active** `Off / On, default On for V1 and V2, Off for V3-V8`
Enables or disables the voice. Off bypasses oscillator computation entirely (no CPU cost) and excludes the voice from the active-voice normalization count.

---

### Waveform

**Waveform** `Sine / Triangle / Saw / Golden TS / Golden SG / Golden GS / Bell / Wavefold / Half-sine / Phi-cascade / Phi Triangle / Phi Sine / Square / Pulse`
The oscillator waveform used by all voices simultaneously.

> **A note on the Golden / Phi family.** Polyrhythm Phase shipped with three "Golden" waveforms whose audible behavior didn't match the names a strict reading would expect — slot 3 ("Golden TS") was a phi-warped sine, not a phi-warped triangle; slot 4 ("Golden SG") added an extra sine pre-warp before the phi-warp. Those sounds are preserved here as Golden TS / SG for back-compat with existing projects. The two **Phi Triangle / Phi Sine** slots at the end of the list are the strict-reading versions (phi-warp into triangle, and phi-warp into clean sine with no pre-warp) — pick those if you want the cleaner interpretations.

- **Sine** — pure sinusoidal tone. Cleanest binaural beat interaction, no harmonics.
- **Triangle** — bipolar triangle wave with odd harmonics, softer than saw.
- **Saw** — sawtooth wave with a full harmonic series. Rich and bright.
- **Golden TS** — a sine wave whose phase is warped using the golden ratio (φ ≈ 1.618): phase split at the 1/φ point, each segment remapped to half a cycle. Produces an asymmetric sine with a slight kink at the warp point. (For the triangle-output reading of the same warp, see Phi Triangle.)
- **Golden SG** — a sine wave whose phase is first remapped through a cosine-shaped pre-warp, then passed through the same golden-ratio warp as Golden TS, then taken through sine. The double pass adds harmonic content the no-prewarp version doesn't have — brighter and more textured. (For the no-prewarp version, see Phi Sine.)
- **Golden GS** — the oscillator phase is self-modulated: the phase is offset by `(1/φ) · sin(phase) / 2π` before the sine function is applied. Creates a continuously self-warping waveform whose harmonic content shifts subtly with frequency.
- **Bell** — additive partials at integer harmonics (1×, 2×, 3×, 4×, 6×) with bell-leaning amplitude weights. Produces a tonal-rich, slightly metallic voice that shimmers under tremolo. Not a true singing-bowl (those use inharmonic partials, which would create discontinuities at each phase wrap), but bell-flavoured in spirit.
- **Wavefold** — sine-of-sine with index 2: `sin(2 · sin(phase))`. A gentle wavefolder — the sine "warms" without any harsh edges, adding mild harmonic content. Stays in the [-1, +1] range naturally; no clipping artifacts. Good when Sine feels too pure.
- **Half-sine** — full-wave rectified sine remapped to bipolar (`2 · |sin(phase)| − 1`). Even-harmonic-only character, hollow and vaguely reedy. Distinct from any of the other waveforms here. **Sounds an octave higher than the same Note setting would on any other waveform in this list.** This isn't a tuning bug — full-wave rectification produces a spectrum with no fundamental and its lowest partial at 2× the carrier frequency, so the perceived pitch is one octave up by design. To match the pitch you'd hear on Sine / Triangle / etc., set Octave shift to -1 (or drop each voice's Note by one octave). To stack a Half-sine drone an octave above another waveform, run this plugin on a second track with a different Waveform selection — this plugin plays one global waveform per instance, so cross-waveform stacking is a multi-track move, not a per-voice one. Also carries a small DC offset (mean ≈ 0.27) which speakers don't reproduce; tremolo and pan attenuate it further.
- **Phi-cascade** — additive harmonics with golden-ratio-decreasing amplitudes: `fundamental + (1/φ)·2nd + (1/φ²)·3rd`. On theme with the Golden TS/SG/GS family but uses pure additive synthesis rather than phase warping. Gives a brighter, more "stacked" character than the phase-warped Goldens.
- **Phi Triangle** — golden-ratio phase warp (same as Golden TS) fed into a TRIANGLE output instead of a sine. Brighter and harmonically richer than Golden TS — triangles carry odd harmonics that the sine-output version smooths over.
- **Phi Sine** — golden-ratio phase warp (same as Golden TS) fed into a clean sine output, with **no** sine pre-warp. The minimalist version of Golden SG: same warp shape, no added prewarp brightness.
- **Square** — the hard-edged classic: full up for the first half of each cycle, full down for the second. Odd harmonics only, hollow and reedy, and much brighter than anything above it in this list. Band-limited (PolyBLEP) at both edges so it stays clean rather than gritty at high pitches.
- **Pulse** — the same shape, but you choose where the fall happens rather than taking the halfway point. See **Pulse width** below. At 50 it is identical to Square; move away from that and the tone thins toward a nasal, reedy buzz.

**Pulse Width %** `1-99%, step 0.1, default 25`
Duty cycle for the **Pulse** waveform — the fraction of each cycle the wave
spends high before snapping low. 50% is a square wave and sounds identical to
the Square slot. Narrower values get thinner and more nasal; wider values mirror
the same character back the other way, so 25% and 75% sound alike. The default
of 25% is deliberately off-square so Pulse sounds distinct from Square the
moment you select it. The range stops short of 0 and 100, which would be
silence and DC respectively.

Only meaningful when Waveform is set to **Pulse**, and hidden from the parameter
list entirely on every other waveform.

---

### Pan

**Pan Enabled** `Off / On`
Enables per-voice pan modulation. When on, each voice is panned independently using a sine LFO before being summed into the output. When off, all pan controls are hidden and voices sum directly to their L/R oscillator channels.

**Pan Mode** `Tremolo / Increment / Spread / Spread Reversed / Alternating / Alternating (Flipped) / Distributed / Distributed (Flipped) / Distributed (Ping-pong) / Converging / Converging (Ping-pong) / Diverging / Diverging (Ping-pong)`
- **Tremolo** — each voice's pan LFO runs at the same rate as that voice's tremolo LFO. The pan and amplitude modulation are locked in phase.
- **Increment** — all voices use a shared Pan Base Rate as their pan foundation, with each voice's rate offset by Pan Increment × voice index. Voice 1 pans at the base rate, voice 2 at base + 1×increment, voice 3 at base + 2×increment, and so on.
- **Spread** — *static* positions, no LFO motion. Active voices are ranked and placed evenly across the stereo field. With four active voices you get four evenly spaced positions; with two active voices, hard left and hard right (scaled by Pan Spread %); with one active voice, dead center. The lowest-numbered active voice goes leftmost. Pan Base Rate and Pan Increment have no effect.
- **Spread Reversed** — same as Spread but with the order flipped: the lowest-numbered active voice goes rightmost.

**Per-cycle pan modes** (`Alternating` through `Alternating every 8`)

Twelve modes that move the pan **one step per tremolo cycle** rather than on an LFO of their own. This is the same set, under the same names, that Full Feature Tremolo, the Resonant Sweeping Filter and the Sweep Dwell Filter already have — only the tick differs.

- **Alternating** — hard left, hard right, left, right.
- **Alternating (Flipped)** — the same, starting on the other side. Two instances set to opposite flips move against each other.
- **Distributed** — walks evenly across the stereo field over `Cycle Steps` positions, then jumps back.
- **Distributed (Flipped)** — the same walk, right to left.
- **Distributed (Ping-pong)** — walks across and back rather than jumping.
- **Converging** — starts hard left, then closes inward toward centre in alternating steps.
- **Converging (Ping-pong)** — the same, bouncing rather than restarting.
- **Diverging** — starts at centre and opens outward in alternating steps.
- **Diverging (Ping-pong)** — the same, bouncing.
- **Alternating every 2 / every 4 / every 8** — the same flip, but it holds each side for 2, 4 or 8 cycles before crossing. This is the one to reach for when the cycles themselves are fast: at 205 BPM a flip on every cycle is far too quick to feel bilateral, where holding for four gives a slow sway that still lands exactly on the boundaries.

**Why use these instead of a separate tremolo plugin panning alongside?** Because they cannot drift. A second plugin panning in time with this one has its own clock, no shared start, and no way to land exactly on a tremolo boundary — so it slides out of alignment and stays there. These move *because the tremolo wrapped*, so there is nothing to hand-match and nothing to fall out of step with.

**Cycle Steps** `2–32, default 8`
How many positions the Distributed / Converging / Diverging walks step through before the pattern repeats. This is the length of a *temporal* pattern and has nothing to do with how many voices you have running.

It matters more than it sounds: **at 2 positions every one of those modes collapses into Alternating** — a walk across two places is a flip. Eight gives Distributed a genuine sweep across the field and Converging a real closing-in. Alternating and the every-N modes ignore it, being two-sided by definition, and it hides for them.

Use **Pan Spread %** for width — at 100% Alternating is hard left/right, around 30-50% it is a sway rather than a flip, which is usually what you want for long listening. Set **Pan Glide ms** to 0 for a hard switch, or leave it at 10 ms for a short sweep between sides.
**Pan Glide ms** `0-100 ms, default 10`
How long the pan takes to travel between positions. **0 is an instant switch** — the sound cuts from one side to the other with no slide, which is what bilateral alternation is supposed to be. Anything above 0 sweeps instead. The default of 10 ms is what this plugin used to do with no way to change it; Full Feature Tremolo and both sweeping filters have had this control all along.





**Pan Spread %** `0-100%, default 100`
Scales the width of pan movement (or for Spread / Spread Reversed, the maximum distance from center). At 100% panning reaches hard left and hard right. At 0% all voices remain centered regardless of mode.

**Pan Base Rate** `0.001-1000, default 60`
Base rate for pan movement in Increment mode, in the units set by Rate Mode.

**Pan Increment per Voice** `-1000–+1000, default 0`
The per-voice rate offset in Increment mode. Each successive voice's pan rate is offset by this amount from the previous. Setting a positive value spreads voices across different pan speeds; a negative value reverses the direction of the spread.

---

### Character

Four controls that shape whichever waveform is selected. They are applied to the
**summed output of all voices**, after all per-voice processing — so they colour
the overall sound rather than each voice separately. All four default to neutral,
so the plugin sounds untouched until you push one.

**Tone (Warm <-> Bright)** `-100 to +100, step 0.1, default 0`
Tilt EQ across the whole output. Negative values are warmer and darker (lows
boosted, highs pulled back); positive values are brighter and airier (the
reverse). One control covering the entire warmth-to-brightness axis. The pivot
sits around 700 Hz, and the extremes reach roughly 9 dB of boost either way.

**Edge** `0-100, step 0.1, default 0`
Soft-clip drive on the summed signal. At 0 the output is clean; pushing it adds
progressively more harmonic grit. A sine picks up a saw-flavoured character; a
triangle gets more bite. Level stays roughly constant as you push it, so you can
judge the change in character without the loudness confusing the comparison.

**Movement** `0-100, step 0.1, default 0`
Chorus on the output. The signal runs through a modulated delay line read at two
separate points, one per output channel, giving stereo shimmer and motion. At 0
there is no effect; higher values raise the wet mix.

**Body** `0-100, step 0.1, default 0`
Peaking EQ centred on the root pitch, boosting the fundamental region by up to
12 dB. It **tracks the pitch** — move the root and the boost moves with it.
Useful for the Golden and Phi waveforms, which can sound thin in the low end.

---

### Direction & Reverse

**Direction & Reverse** `Forward / Reverse — permute / Reverse — time / Both — permute / Both — time`

Selects how the eight-voice palette is read.

- **Forward** — default. 8 voices play in their natural order, tremolo phase advancing forward.
- **Reverse — permute** — 8 voices with **drift values mirrored** V1↔V8, V2↔V7, V3↔V6, V4↔V5. Notes, gains, phase offsets, and active flags stay where you put them — only the cadences swap. With drift values that increment linearly (e.g. 0.00 → 0.35 ascending), this turns the cadence into 0.35 → 0.00 descending: the low note now fires at the high cadence and the high note fires at the low cadence. Swapping the *entire* voice identity together would be a mathematical no-op (the audio sum doesn't care which slot a voice lives in), which is why this slider mirrors just the drift values — that's what produces an audible reordering.
- **Reverse — time** — 8 voices. Voice settings unchanged; tremolo phase decrements instead of incrementing. For symmetric envelopes (equal attack and release) the audible result is the same as Forward. For asymmetric envelopes the gate "breathes" the opposite way — attack 0% / release 100% becomes a slow fade-in into an abrupt cut-off.
- **Both — permute** — 16 voices. Forward layer (slots 0–7) plays unchanged. A second layer (slots 8–15) plays the same notes/gains/offsets with drift values mirrored. Each note now fires at **two different cadences across the two layers** — at the fast end you get harmonic pairs pulsing together, at the slow end you get single notes spaced apart.
- **Both — time** — 16 voices. Forward layer (slots 0–7) plays unchanged. A second layer (slots 8–15) plays the same V1..V8 settings but with tremolo phase decrementing. With an asymmetric envelope (attack 0 / release 100), the reverse layer fades *in* exactly when the forward layer fades *out* — the pulses cancel into a continuous drone with no silent gaps.

In any Both mode, Pan Mode = Spread or Spread Reversed ranks all 16 active voices across the stereo field rather than 8 + 8 stacked, so you hear a wider distribution. Pan Mode = Increment continues the per-voice pan-rate ramp past slot 7 into slots 8–15.

**Reverse Drift Offset** `-1000–+1000, default 0`

Visible only when Direction & Reverse is set to a Both mode. Adds a constant to every drift value in the reverse layer (slots 8–15) before tremolo rates are computed. With offset = 0 the reverse layer's per-voice cadences match the forward layer's exactly (mirrored in Both — permute, identical in Both — time), so the two layers run roughly in lockstep. Non-zero values shift the reverse layer's drift range away from the forward layer's, breaking the lockstep and giving each layer its own polyrhythmic palette from a single plugin instance.

In single-layer modes the slider hides because adding a constant to every drift value would be mathematically identical to adjusting the global Rate Value — a duplicate control would just confuse.

**Replacing multi-track stacks.** If you previously layered two tracks of this plugin with shared notes but different drift palettes (e.g. one track with drift values 0.00 → 0.35 ascending and a second track with 1.55 → 1.20 descending), one instance with Direction & Reverse = Both — permute and Reverse Drift Offset = 1.20 produces the same audible result from a single track. The mirror brings the descending pattern; the offset brings the rate range. Use Both — time when you want parallel-ascending pairing instead (both layers ascending in drift, one playing forward and one backward in time).

### Start Delay

**Start Delay** `0–1000, default 0`

How long the plugin sits silent at the start of playback before voices begin. Units match Rate Mode: BPM mode counts in tremolo cycles of the global Rate Value (so 4 with Rate Value = 60 BPM = 4 cycles = 4 seconds), Seconds mode is literal seconds, Hz mode counts in cycles of the global Rate Value. 0 disables the delay entirely.

During the delay window the voice loop is skipped — phases stay frozen at their play-start reset positions. When the delay elapses, voices begin from phase 0 (or their per-voice Phase Offsets) rather than from a mid-cycle position. So if you set V1 Phase Offset = 2 seconds and Start Delay = 4 seconds, V1 first fires at t = 6 seconds (4 seconds of silence, then V1's own 2-second wait counted from there).

Re-arms on every transport stop/start, so each playback run begins with a fresh silent window.

### Play / Rest Gating (v2)

**Play for (cycles)** `0–1000, default 0`
**Rest for (cycles)** `0–1000, default 0`

A per-voice cyclic gate. Each voice plays for **Play for** cycles of its own tremolo rate (global rate + per-voice Drift), then goes silent for **Rest for** cycles of the same per-voice rate, then resumes. Because counting is per-voice, voices with different Drift settings enter and leave rest at different real-time moments — V8 at Drift 3.5 reaches its 4-cycle play threshold in less wall-clock time than V1 at Drift 0, and V8 wakes earlier from rest for the same reason. The "loop" lives in each voice's own cadence; the rhythmic identity you hear comes from how the voices' independent play/rest cycles interlock.

The feature is **disabled when either slider is 0** (the default). With both at 0, polyrhythm_phase behaves exactly like v1 — no gating, no behavior change.

**The release of the final cycle reaches actual silence.** Normally the Depth dB slider sets an always-on floor under the tremolo — at the default -6 dB, the LFO modulates between roughly 50% and 75% gain and never goes quiet. That floor would make the gate's rest entry sound like a soft thud (50% → 0% in ~15 ms). The gate's final cycle drops that floor during the release portion of the LFO, so the release tail decays all the way to 0 and the rest freeze lands on actual silence. Cycles 1 through (Play for − 1) keep the normal Depth-floored shape; only the last release changes.

**Use a non-zero Release setting** for the clean rest entry this feature is designed for. Release = 0% has zero release-zone width, so the depth-floor override never fires and you get a sharp cutoff at the rest boundary instead of a glide to silence.

**Wake from rest is handled by the same 3 ms gain smoother** that prevents Attack = 0% from clicking at normal cycle starts. When a voice's rest counter expires, target gain jumps from 0 back to whatever the LFO says, and the smoother ramps gain_l/gain_r over ~3 ms — perceptually a clean attack, not a click. No special wake-side logic needed.

**Transport behavior** is conventional: pressing stop silences the plugin, pressing play re-initializes everything (voice phases, Start Delay counter, per-voice cycle counters, resting flags). Every play press starts a fresh play period from voice cycle 0. Same behavior as without the gate engaged.

### Ramp

A one-time ride of a chosen parameter over a duration, then it holds — the in-plugin stand-in for drawing an automation envelope. It is **multi-target**: the same 24-target list as Drift. Pick a target, set a signed `by`, engage, and that target rides from its baseline to baseline + `by` over the duration. Each target keeps its own `by`; all engaged targets ride in parallel. Drift and Ramp **compose** — a parameter = baseline + drift wander + speed-ramp ride.

This is the complement to Drift: Drift is a *repeating* wander that always returns; Ramp is a *one-time* move that stays. Between them you can replace most automation-envelope use without leaving the plugin.

**Ramp target (slider 83)** `24 options, default Base Rate`
Picks which target the `by` amount edits. Same list as the Drift target selector (Base Rate, V1–V8 Rate, Pan Base Rate, Pan Increment, Binaural Beat, Trem On Duration, V1–V8 Gain, Depth dB, Attack %, Release %). Switching the selector saves the current target's `by`/duration/start-delay to the old target and loads the new target's saved values — running ramps on other targets keep going.

**Ramp by (slider 84)** `-1000 to +1000, step 0.001, default 0`
Signed amount for the selected target, in that target's natural unit (rate unit for the rate targets, Hz for Binaural, dB for Gain/Depth, % for On Duration / Attack / Release). **0** = no ride.

- **Base Rate** rides as a multiplicative ratio: at 60 BPM, `by -30` scales every voice by 0.5, so V2's 60.5 → 30.25 — the slow beat between voices is preserved.
- **The other 23 targets** ride as additive offsets on their own value.
- In BPM/Hz modes a negative `by` = slower; in Seconds mode a positive `by` = slower (longer period).

**Independent mode note:** slider 3 (base rate) is still the reference for the Base Rate target's `by` interpretation even though it's not used for audio in Independent mode. Per-voice Rate targets ride each voice's own rate directly.

**Ramp duration (slider 85)** `0–60 minutes, default 0` — **per-target**: how long the *selected* target takes to travel from baseline to baseline + `by`; a target with duration 0 doesn't ramp. · **Ramp start delay (slider 87)** `0–60 minutes, default 0` — **per-target**: wait this many minutes after engage before *this* target moves. · **Ramp engage (slider 86)** `Off / On, default Off` — **global**: one switch arms every configured target, each riding its own duration after its own start delay. (Duration + start delay are saved/loaded per target by the selector, like `by`.)

Engage is a freeze/resume gate (NOT a restart edge): while On, each target's clock advances 0 → 1 over its own duration; while Off all freeze and resume on re-engage. Each target has its **own** duration and start delay, so different targets can wind down over different timelines from a single engage.

**Tuning is unaffected** — only modulation rates, levels, and envelope shape ride; the audible oscillator pitch stays put (Binaural Beat is rideable because it's a modulation-domain offset, not the carrier pitch).

**Transport behavior:** every play press resets ramp_t (and the rest of the play-session state). This is the ONLY thing that resets ramp_t — slider changes, including switching the target selector, don't.

### Drift

Slow organic wander applied independently to any of **24 targets** — by far the widest drift surface in the suite. Each target can have its own drift configuration; all 24 drift in parallel. The selector chooses which target's drift you're currently editing — the others keep running with their last-saved configuration.

The per-voice Rate targets are the rhythmic heart: drift each voice's rate independently and the voices wander against each other, which is the essence of polyrhythmic feel — the pattern is never quite the same twice. The expressive targets (per-voice Gain, Depth, Attack/Release) add the *dynamic* dimension — the pattern can breathe in level and character too, not just timing.

Same pattern as Womb v3's drift and the rest of the suite. Switching the **Drift target** selector (slider 78) saves the current sliders 79-82 into the old target's memory slot, then loads the new target's saved values. All 24 configurations persist across project save/load.

**Drift target** `24 options, default Base Rate`
- **Base Rate** — uniform Hz delta to every voice; preserves inter-voice rate relationships (the whole pattern breathes together).
- **V1–V8 Rate** — wanders each voice's own rate independently. Voices drift against each other. In Both modes the reverse-layer slot 8+k follows V(k+1)'s drift.
- **Pan Base Rate** / **Pan Increment** — wander the Increment-mode pan controls (pan base rate and per-voice pan spread). Only affect Increment pan mode.
- **Binaural Beat** — wanders the L/R frequency offset (the beat frequency itself drifts), applied uniformly to all voices' R channel.
- **Trem On Duration** — wanders the on-portion of the tremolo cycle (how long each pulse stays open).
- **V1–V8 Gain** — wanders each voice's level (dB) per-sample, so voices swell and recede independently. This is the dynamics dimension — the single biggest contributor to a pattern that feels alive rather than looping.
- **Depth dB** — wanders the tremolo depth (the pulse gets shallower and deeper over time).
- **Attack %** / **Release %** — wander the tremolo envelope shoulders (onsets and tails soften/sharpen).

**Drift up amount** `0.0–100.0, default 0` (units match target)
How far above the target's baseline the drift wanders at its peak. Units: the rate's current unit (BPM / Seconds / Hz) for the rate targets, Hz for Binaural Beat, dB for the Gain targets and Depth dB, percent for Trem On Duration and Attack/Release. Rate targets in Hz mode use the low end; Gain/Depth dB use modest values (a few dB is a strong swell). 0 = drift off on the up side.

**Drift down amount** `0.0–100.0, default 0` (units match target)
How far below the baseline the drift wanders at its trough. Independent from Up — asymmetric wander supported. Either non-zero activates drift for the target; both 0 = drift off.

**Drift period (cycles)** `1–1000, default 8`
How many V1 cycles (the global rate) one full drift wave takes for this target. All 24 targets use V1 cycles as their period unit, scaled by Ramp so the wave-per-cycle relationship stays constant under wind-down.

**Drift shape** `Sine / Triangle / Random, default Sine`
Wander waveform. Sine = smooth, Triangle = linear ramps with turnarounds, Random = value-noise interpolating smoothly between fresh random targets at each period boundary.

#### Notes

- **Per-voice Rate drift vs. the per-voice Drift/Rate slider.** Each voice already has a static Drift/Rate value (its rate offset in Drift mode, or its rate in Independent mode). The new V1–V8 Rate drift targets add *time-varying wander* on top of that static value — the voice's rate now moves around its set point on a slow schedule.
- **Pan Base Rate / Pan Increment drift only affect Increment pan mode.** In Tremolo pan mode the pan follows each voice's tremolo rate (already moved by Base Rate / per-voice Rate drift); Spread modes are static positions.
- **Mode-direction asymmetry on the rate targets:** in BPM and Hz modes a positive drift amount speeds up; in Seconds mode (period) a positive amount slows down.
- **Per-voice Gain drift is continuous (per-sample), so it's a smooth volume swell.** Depth / Attack / Release drift are global (one wander shared across all voices). Together with per-voice Rate and Gain drift, the same notes can wander in timing AND dynamics on independent schedules — the closest the plugin gets to "an unforced live ensemble."

#### Transport behavior

The plugin sets `ext_noinit = 1` so the drift config bank survives transport. A comprehensive transport-edge reset gives a clean restart on every play press: all drift phases → 0, every voice's oscillator / tremolo / pan phases, gains, and Play/Rest counters reset, Start Delay and Ramp reset, and the character chain (Tone / Edge / Movement / Body filter state + the chorus delay buffer) clears. Drift CONFIG is preserved across stop/play and project save/load. Renders are deterministic for Sine and Triangle shapes (Random remains non-deterministic per render by design).

---

## Usage Notes

- **Active voice count determines normalization.** The output is divided by the number of active voices each sample, keeping overall level consistent. Enabling or disabling voices mid-playback will change the level slightly as the normalization adjusts.
- **Binaural Beat Hz applies to all voices uniformly.** All voices have the same L/R frequency offset. There is no per-voice binaural beat amount.
- **Playback start resets all phases.** Oscillator phases, tremolo phases, and pan phases all reset to zero when playback begins from a stopped state. This ensures consistent behavior from the same starting point.
- **Rate Mode applies to both tremolo and pan rates.** Both the voice tremolo rates and the Increment mode pan rates are interpreted in whatever unit Rate Mode specifies.
- **Phase Offset means "when does this voice become audible," not a raw phase shift.** An offset of 8 on a 16-second cycle means the voice fires at second 8. An offset of 0 fires immediately. Offsets wrap freely — an offset of 16 on a 16-second cycle is the same as 0.
- **On Duration % and voice count must be coordinated to avoid overlap.** On Duration sets how much of each cycle a voice is present. With multiple voices spaced across a shared cycle, each voice needs enough room to fit without overlapping its neighbors. The safe maximum On Duration for evenly-spaced voices is `100 ÷ number of active voices` percent. For example: 2 voices = 50% max, 3 voices = 33% max, 4 voices = 25% max. Exceeding this will cause voices to overlap at the boundaries regardless of how offsets are set. To space voices evenly, divide the cycle length by the number of voices and use that as the offset step — e.g. 3 voices on a 12-second cycle: offsets of 0, 4, and 8.
- **Offsets don't have to be perfectly even — spacing voices closer together creates overlap, spacing them further apart creates silence between them. Both are valid creative choices.** In Seconds mode this is especially concrete: with a 16-second cycle, On Duration 50%, and two voices, an offset of 8 produces a clean handoff — V1 plays seconds 0–8, V2 plays seconds 8–16. An offset of 7 causes one second of overlap at the boundary. An offset of 9 leaves a one-second gap of silence between them. The relationship is direct: offset in seconds is exactly when V2 becomes audible.
- **When building sequential voice patterns, set Rate Value to `voice duration × number of voices`.** This ensures the cycle fills exactly with no gaps or overlap. For example: 4 voices each lasting 4 seconds requires a rate of 16 seconds, with offsets at 0, 4, 8, and 12. 4 voices each lasting 6 seconds requires a rate of 24 seconds, with offsets at 0, 6, 12, and 18. On Duration % should be set to `100 ÷ number of voices` to match.
- **Spread and Spread Reversed are static, not modulated.** Voices stay locked to their assigned positions across the stereo field for as long as the active set doesn't change. Toggling a voice's Active state will redistribute the positions of the others (the rank-among-active is recalculated each time). Pan Spread % scales how far from center those positions extend.

---

*Polyrhythm Phase is part of the Rozaya JSFX plugin suite.*
*Designed by Rozaya — Developed with Claude (Anthropic)*


---

