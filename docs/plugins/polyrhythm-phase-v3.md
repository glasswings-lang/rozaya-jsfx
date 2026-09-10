# Polyrhythm Phase v3 (Note-Based)

**Designed by Rozaya — Developed with Claude (Anthropic)**

---

## Overview

Polyrhythm Phase v3 is a binaural oscillator with up to eight simultaneous voices, each tuned to a specific musical pitch. Each voice generates a stereo pair of oscillators with a slight frequency offset between the left and right channels — the binaural beat — producing entrainment tones that shift in perceived frequency as the beat interacts with the listener's auditory system. Each voice carries its own tremolo envelope -- its own waveform, depth, on-duration
and attack/release lengths -- so a shallow near-continuous voice can sit under a
hard short one, with per-voice drift or independent rate options creating
polyrhythmic relationships between them. A pan modulation system adds either
continuous spatial movement (Tremolo / Increment), static spread positions
(Spread / Spread Reversed), or a per-cycle walk through the stereo field.

The plugin generates no audio from an input signal. It is a pure synthesizer.

**The older Polyrhythm is archived (2026-09-10).** It set each voice by counting
semitones from a Base Note and Center Octave; v3 has each voice **name its
note**. Every project that used the older one was converted: each voice now
shows its real note, Transpose and Octave shift start at 0, and all 144
instances render identically. The older plugin and its manual are in
`archive/versions/polyrhythm_phase/`.

**Rebuilt 2026-09-07.** The eight voices moved behind a **Voice** selector,
taking the slider count from 90 down to 56; five controls that used to be one
setting for the whole plugin (Waveform, Tremolo amount, On Duration, Attack % and
Release %) became per-voice; **Solo** and a **Pan rate mode** are new, as are
the six Drift and Ramp controls the rest of the suite already had. Existing
projects were migrated and sound as they did — see the notes on each control
for what was written where.

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
and behaves identically; anything you had saved on it is untouched.)* — Rate Value carries the mode's unit: BPM, seconds, Hz, or beats per cycle.

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

**Host ratio** — *gone.* It was retired in 2026-09-02 and removed outright in the 2026-09-07 rebuild, along with every other slider that no longer had a job. With Rate Value in beats, *every 4 beats* is typing 4.

**Rate Value — all voices** `0.001-1000, default 60`
The shared base tremolo rate, in the units set by Rate Mode. Each voice's own
Drift / Rate is added to it. **Only visible in Drift mode** — in Independent
mode there is no shared rate, because each voice's Drift / Rate *is* its rate.

*The label carries its full unit list and says "all voices" on purpose.* The
2026-09-07 rebuild briefly shortened it to a bare `Rate Value`, and the first
thing that tripped Rozaya up was tabbing onto a rate control that named neither
its unit nor its scope. Restored the same day, to the form four other plugins
in the suite already use.

**Binaural Beat Hz (L/R offset)** `0-100 Hz, default 4`
The frequency difference between each voice's left and right oscillators. At 4 Hz, the left oscillator runs at the voice's base pitch and the right runs 4 Hz higher, creating a 4 Hz binaural beat when heard on headphones. This value is the same for all voices simultaneously.

**Attack Shape** `Linear / Cosine / Logarithmic / Exponential`
Curve shape applied to the attack ramp. **Global**, deliberately: the shape is
refinement, and the LENGTHS (Attack % and Release %, both per-voice) are where
the difference between a pad and a blip lives.

**Release Shape** `Linear / Cosine / Logarithmic / Exponential`
Curve shape applied to the release ramp. Global, same reasoning.

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

### The voices, behind one selector

*Rebuilt 2026-09-07. Until then each voice had its own six sliders and the
plugin declared ninety. The pitch block arrived on 2026-09-10, and it now
declares fifty-nine.*

You pick a voice with the **Voice** selector, and the fifteen controls under it
are that voice's settings. The other
seven keep playing exactly as they were — their values live in the plugin's own
memory, the same way the Drift and Ramp targets already did.

**Voice** `All / Voice 1 … Voice 8, default All`

**All is position 0, and it is the reason the selector is worth having.** Once
each voice is cheap to set individually, setting them all the *same* becomes the
tiring job — arrowing 1 to 8 and picking the same waveform eight times. Park the
selector on **All**, move a control, and every voice takes it. "All sine except
voice five" is two moves rather than eight.

So there are no separate global copies of Waveform, Tremolo amount, On Duration, Attack %
or Release % any more. **All is the global.**

**What All shows when the voices disagree** is voice 1's value. Reading is
approximate; writing is exact and reaches all eight. Nothing writes until you
actually move a control, so parking on All and then adjusting Tone, or opening a
project, changes nothing.

---

**Gain dB** `-60 to +6 dB, default -6 for every voice`
Per-voice output level, applied before the voice is summed. -60 dB is
effectively silent. To cut a voice with no CPU cost, use **Active = Off**
instead.

#### The pitch block *(2026-09-10, Breath Generator's shape)*

Five controls, and each voice has all five. Set them on **All** to change every
voice at once. The left oscillator runs at the voice's pitch; the right runs at
that pitch plus the Binaural Beat Hz offset.

**Pitch mode** `Hz / Semitones / Cents, default Semitones`
What this voice's Pitch value means. It comes first because it decides whether
the note name below means anything. Switching it does not convert the number:
60 in Semitones is middle C, and 60 in Hz is a low hum.

**Note name** `C-1 to G9, default C4`
This voice's pitch, said as a note. It works both ways: pick `A4` here, or type
`69` into Pitch value, and the other follows. Only shown in Semitones, where the
names and the numbers are the same thing. *Until 2026-09-10 the list ran C2 to
C6; every saved voice kept its note.*

**Pitch value (Hz / semitones / cents)** `0 to 20000, default 60`
The pitch itself, not an offset from anything. In **Hz** it is the frequency. In
**Semitones** it is the MIDI note number, so 60 is middle C and 69 is A4. In
**Cents** it is that number times 100, so 6950 is a quarter tone above A4.
**Transpose** and **Octave shift** move every voice on top of this, in any mode.

**Fine tune** `-1000 to +1000, default 0`
The one fine tune, in the unit below. Two voices on the same note with one a few
cents off will beat slowly against each other.

**Fine tune unit** `Hz / Semitones / Cents, default Cents`
What Fine tune counts in, for this voice. In Cents, `+100` is exactly one note
step. Saved voices were in cents, and still are.

**Drift / Rate — offset in Drift mode, this voice's own rate in Independent** `-1000 to +1000, default 0`

*The label spells both meanings out because the control genuinely has two, and
a control whose meaning is gated by a switch has to say so on itself.*

**In Drift mode** this is an *offset* added to Rate Value, never a value on its
own. 0 means this voice runs at exactly the base — not stopped. Whether a
positive offset speeds the voice up or slows it down depends on the unit: faster
in BPM and Hz, **slower in Seconds and *Every N beats***, where a bigger number
means a longer gap.

**In Independent mode** this *is* the voice's rate, directly, in whatever unit
Rate Mode selects — Rate Value is ignored entirely. Here 0 does mean effectively
stopped, in every mode.

**Phase Offset** `-1000 to +1000, default 0`
When this voice becomes audible within its tremolo cycle, in the units set by
Rate Mode (BPM = beats, Seconds = seconds, Hz = cycles). Offset 0 fires the
voice immediately at playback start. Values wrap freely.

**Waveform** *(per-voice since 2026-09-07)*
This voice's waveform, from the fourteen-slot palette described below. It used
to be one setting for the whole plugin. Set it on **All** to change every voice
at once.

**Tremolo amount (dB, 0 = strongest)** `-60 to 0 dB, default -6`
How strongly this voice pulses. **0 dB is the strongest pulse:** the voice dips
to silence at the bottom of each cycle. **-60 dB is no pulse at all:** it holds
steady. The default of -6 is a gentle swell that never goes quiet. This is the
same control, with the same range and behaviour, as REAPER's own stock Tremolo,
where it is called `Amount (dB)`.

*Renamed 2026-09-10 from `Depth dB`. The sound did not change. Until then this
manual described it backwards, which is what the old name invited.*

**On Duration % of Cycle** `0-100%, default 100`
The proportion of this voice's tremolo cycle during which it is in its active
state (including attack and release). At 100% the tremolo never fully closes; at
50% the voice is present for half its cycle.

**This is the big one.** Until this build every voice shared one envelope, so
the plugin made one kind of sound played in a pattern. A voice on for 90% of its
cycle is a **pad**; one on for 10% is a **rhythm** — and now you can have both
at once, a shallow near-continuous bed with a hard short blip ticking over it.

**Attack % of Cycle** `0-100%, default 0`
Proportion of the on-time spent fading up from silence.

**Release % of Cycle** `0-100%, default 100`
Proportion of the on-time spent fading back down. The default of 100% with 0%
attack gives a ramp-down envelope: the voice fades out across its whole on-time
with no hold.

> If Attack % + Release % exceeds 100% of the on-time, both are scaled down
> proportionally so their sum fits.

**Active** `Off / On, default On for V1 only`
Enables or disables the voice. Off bypasses its oscillator entirely — no CPU
cost — and excludes it from the level normalisation count.

**Solo this voice** `Off / On, default Off` *(new 2026-09-07)*
When **any** voice is soloed, only soloed voices sound. Step the Voice selector
through with this switched on and the voice that is wrong announces itself;
before this, hearing one voice alone meant switching seven others off and back
on again.

**Soloing does not change the level of what is left.** The normaliser counts the
voices that will actually sound, so soloing one of eight keeps it at the volume
it had rather than dropping it by 18 dB. Soloing an inactive voice gives
silence — Active still wins.

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
Base rate for pan movement in Increment mode, in the units set by **Pan rate
mode** below.

**Pan rate mode** `BPM / Seconds / Hz / Every N beats / N per beat, default BPM` *(new 2026-09-07)*
The pan's **own** rate mode. It used to borrow the tremolo's, which meant you
could not have the tremolo free-running in Hz while the pan landed on the
project's beats — and that pairing is most of what bilateral panning is for.
Every rate in this suite carries its own mode beside its own value; this is the
pan's.

Only Increment mode uses it. **Tremolo** pan mode pans at each voice's own
tremolo rate, so it follows the main rate pair, which is what that mode means.

*Existing projects keep the mode they were already running:* the migration wrote
each instance's tremolo Rate Mode into this control rather than letting it take
the default, so nothing changed speed.

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

**The release of the final cycle reaches actual silence.** Normally the Tremolo amount slider sets an always-on floor under the tremolo — at the default -6 dB, the LFO modulates between roughly 50% and 75% gain and never goes quiet. That floor would make the gate's rest entry sound like a soft thud (50% → 0% in ~15 ms). The gate's final cycle drops that floor during the release portion of the LFO, so the release tail decays all the way to 0 and the rest freeze lands on actual silence. Cycles 1 through (Play for − 1) keep the normal Depth-floored shape; only the last release changes.

**Use a non-zero Release setting** for the clean rest entry this feature is designed for. Release = 0% has zero release-zone width, so the depth-floor override never fires and you get a sharp cutoff at the rest boundary instead of a glide to silence.

**Wake from rest is handled by the same 3 ms gain smoother** that prevents Attack = 0% from clicking at normal cycle starts. When a voice's rest counter expires, target gain jumps from 0 back to whatever the LFO says, and the smoother ramps gain_l/gain_r over ~3 ms — perceptually a clean attack, not a click. No special wake-side logic needed.

**Transport behavior** is conventional: pressing stop silences the plugin, pressing play re-initializes everything (voice phases, Start Delay counter, per-voice cycle counters, resting flags). Every play press starts a fresh play period from voice cycle 0. Same behavior as without the gate engaged.

### Ramp

A one-time ride of a chosen parameter over a duration, then it holds — the in-plugin stand-in for drawing an automation envelope. It is **multi-target**: the same 88-target list as Drift. Pick a target, set a signed `by`, engage, and that target rides from its baseline to baseline + `by` over the duration. Each target keeps its own `by`; all engaged targets ride in parallel. Drift and Ramp **compose** — a parameter = baseline + drift wander + speed-ramp ride.

This is the complement to Drift: Drift is a *repeating* wander that always returns; Ramp is a *one-time* move that stays. Between them you can replace most automation-envelope use without leaving the plugin.

**Ramp target** `88 options, default Base Rate`
Picks which target the `by` amount edits. The same list as Drift, described
under **Drift target** below, including the "(all voices)" entries. Switching
the selector loads that target's saved values; an edit is written the moment you
make it. Running ramps on other targets keep going.

**Ramp by** `-1000 to +1000, step 0.001, default 0`
Signed amount for the selected target, in that target's natural unit (rate unit for the rate targets, Hz for Binaural, dB for Gain/Depth, % for On Duration / Attack / Release). **0** = no ride.

- **Base Rate** rides as a multiplicative ratio: at 60 BPM, `by -30` scales every voice by 0.5, so V2's 60.5 → 30.25 — the slow beat between voices is preserved.
- **The other 87 targets** ride as additive offsets on their own value.
- In BPM/Hz modes a negative `by` = slower; in Seconds mode a positive `by` = slower (longer period).

**Independent mode note:** Rate Value is still the reference for the Base Rate target's `by` interpretation even though it's not used for audio in Independent mode. Per-voice Rate targets ride each voice's own rate directly.

**Ramp time unit** `Cycles / Seconds / Minutes / Beats, default Minutes` *(new 2026-09-07)*
What Ramp duration and Ramp start delay are counted in. **Minutes is the
default and that is not a free choice** — every saved instance had no such
control, so Minutes is the unit they were all already running on, and putting
Cycles at the top of the list would have quietly rewritten a thirty-minute ramp
into a two-second one. *Cycles* counts this plugin's own tremolo cycles;
*Beats* follows the live project tempo.

**Ramp duration** `0–1000, default 0` — **per-target**: how long the *selected*
target takes to travel from baseline to baseline + `by`, in Ramp time units. A
target with duration 0 doesn't ramp. · **Ramp start delay** `0–1000, default 0`
— **per-target**: wait this long after engage before *this* target moves. ·
**Ramp engage** `Off / On, default Off` — **global**: one switch arms every
configured target.

**Ramp play for** / **Ramp rest for** `0–1000, default 0 each` *(new 2026-09-07)*
Per-target. The ramp advances for `play`, holds for `rest`, and repeats — so it
climbs as a **staircase** rather than a smooth glide. The holds come *out* of
the duration rather than extending it, so Ramp duration goes on meaning "you
arrive in about this long". Both at 0 is the smooth ramp, which is what every
existing project has.

Engage is a freeze/resume gate (NOT a restart edge): while On, each target's clock advances 0 → 1 over its own duration; while Off all freeze and resume on re-engage. Each target has its **own** duration and start delay, so different targets can wind down over different timelines from a single engage.

**Pitch rides too, since 2026-09-10.** Each voice's Pitch and Fine tune,
Transpose and Tuning reference are all targets, so a ramp can glide the tuning.
Octave shift is not a target.

**Transport behavior:** every play press resets ramp_t (and the rest of the play-session state). This is the ONLY thing that resets ramp_t — slider changes, including switching the target selector, don't.

### Drift

Slow organic wander applied independently to any of **88 targets** — by far the widest drift surface in the suite. Each target can have its own drift configuration; all 88 drift in parallel. The selector chooses which target's drift you're currently editing — the others keep running with their last-saved configuration.

The per-voice Rate targets are the rhythmic heart: drift each voice's rate independently and the voices wander against each other, which is the essence of polyrhythmic feel — the pattern is never quite the same twice. The expressive targets (per-voice Gain, Depth, Attack/Release) add the *dynamic* dimension — the pattern can breathe in level and character too, not just timing.

Same pattern as the rest of the suite. Switching the **Drift target** selector loads that target's saved values; an edit is written the moment you make it. All 88 configurations persist across project save/load.

**Drift target** `88 options, default Base Rate` *(24 until 2026-09-10)*

The list runs in the same order as the controls themselves:

- **Base Rate, Tuning reference, Transpose, Binaural Beat, Pulse width, Tone, Edge, Movement, Body** — one each.
- **Eight groups, one for each control a voice has:** Pitch, Fine tune, Rate, Tremolo amount, On duration, Attack, Release, Gain. Each group is an "(all voices)" entry followed by V1 to V8.
- **Pan spread, Pan base rate, Pan increment, Pan glide, Reverse drift offset, Play for, Rest for.**

**An "(all voices)" entry holds nothing of its own.** Pick one and you see voice 1's setup; move a control and it is written into all eight voices' targets, the same way the Voice selector's All works. Afterwards each voice has its own copy, so with Sine or Triangle they move in step, and with Random each wanders its own way. Parking on one and moving some other control writes nothing.

What some of them do:

- **Base Rate** — uniform Hz delta to every voice; preserves inter-voice rate relationships (the whole pattern breathes together).
- **V1–V8 Rate** — wanders each voice's own rate independently. Voices drift against each other. In Both modes the reverse-layer slot 8+k follows V(k+1)'s drift.
- **V1–V8 Pitch** and **Fine tune** — wander that voice's pitch, in that voice's own Pitch mode and Fine tune unit.
- **Pan Base Rate** / **Pan Increment** — wander the Increment-mode pan controls. Only affect Increment pan mode.
- **Binaural Beat** — wanders the L/R frequency offset (the beat frequency itself drifts), applied uniformly to all voices' R channel.
- **V1–V8 Gain** — wanders each voice's level (dB) per-sample, so voices swell and recede independently.
- **Tremolo amount** — wanders how strongly a voice pulses. 0 dB is the strongest, so drifting up makes the pulse stronger.
- **On duration**, **Attack** and **Release** — wander the shape of a voice's pulse.
- **Play for** / **Rest for** — wander the gate's counts. The gate still only switches on when both sliders are above zero.

**Drift up amount** `0.0–100.0, default 0` (units match target)
How far above the target's baseline the drift wanders at its peak. Units: the rate's current unit (BPM / Seconds / Hz) for the rate targets; the voice's own Pitch mode unit for Pitch and its Fine tune unit for Fine tune; semitones for Transpose; Hz for Tuning reference and Binaural Beat; dB for Gain and Tremolo amount; percent for On duration, Attack, Release, Pulse width and Pan spread; ms for Pan glide; cycles for Play for and Rest for. Rate targets in Hz mode use the low end; Gain/Tremolo amount use modest values (a few dB is a strong swell). 0 = drift off on the up side.

**Drift down amount** `0.0–100.0, default 0` (units match target)
How far below the baseline the drift wanders at its trough. Independent from Up — asymmetric wander supported. Either non-zero activates drift for the target; both 0 = drift off.

**Drift period** `0–1000, default 8, 0 = off`
How long one full drift wave takes for this target, counted in the unit below.

**Drift period unit** `Cycles / Seconds / Beats, default Cycles` *(new 2026-09-07)*
What the period counts. **Cycles** is this plugin's native count and the default
— a period of 8 means eight tremolo cycles, and because it rides the same scale
as everything else it follows the rate and the project tempo for free.
**Seconds** is wall clock. **Beats** converts at the live project tempo, so the
wander follows the host rather than the rhythm.

**Drift play for** / **Drift rest for** `0–1000, default 0 each` *(new 2026-09-07)*
Per-target, counted in **periods**. Both must be above zero for the gate to
engage. While resting the drift phase does not advance at all, so the offset
**freezes where it stopped** rather than sliding back to centre.

**The fraction of the play value chooses where it parks.** `x.25` parks at the
crest, `x.75` at the trough, `x.0` and `x.5` at no-change. So a whole number
parks at neutral every time and is nearly inaudible — the awkward fraction is
the interesting one, because each freeze lands further round the wave than the
last.

**Drift shape** `Sine / Triangle / Random, default Sine`
Wander waveform. Sine = smooth, Triangle = linear ramps with turnarounds, Random = value-noise interpolating smoothly between fresh random targets at each period boundary.

#### Notes

- **Per-voice Rate drift vs. the per-voice Drift/Rate slider.** Each voice already has a static Drift/Rate value (its rate offset in Drift mode, or its rate in Independent mode). The new V1–V8 Rate drift targets add *time-varying wander* on top of that static value — the voice's rate now moves around its set point on a slow schedule.
- **Pan Base Rate / Pan Increment drift only affect Increment pan mode.** In Tremolo pan mode the pan follows each voice's tremolo rate (already moved by Base Rate / per-voice Rate drift); Spread modes are static positions.
- **Mode-direction asymmetry on the rate targets:** in BPM and Hz modes a positive drift amount speeds up; in Seconds mode (period) a positive amount slows down.
- **Per-voice Gain drift is continuous (per-sample), so it's a smooth volume swell.** Tremolo amount, On duration, Attack and Release drift are per voice since 2026-09-10; use the "(all voices)" entry to set all eight at once. Together with per-voice Rate and Gain drift, the same notes can wander in timing AND dynamics on independent schedules — the closest the plugin gets to "an unforced live ensemble."

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

