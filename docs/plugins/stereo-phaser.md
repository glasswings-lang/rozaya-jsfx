# Stereo Phaser

**Designed by Rozaya — Developed with Claude (Anthropic)**

---

## Overview

A classic swept-allpass phaser with a stereo spread and a very wide stage range. A chain of allpass filters is swept by an LFO; summing the swept signal with the dry input carves moving notches in the spectrum — the phaser "whoosh." Feedback deepens and resonates the notches. The stereo image comes from an LFO phase offset between the two channels, so the sweep swirls across the field rather than moving in lockstep.

At the low end of its stage range it's a normal musical phaser; pushed toward its maximum it turns into a dense, dozens-of-notches "curtain" for sound design.

## Signal Architecture

- **Allpass chain.** Each channel runs a cascade of first-order allpass stages (`y = coef·(y_prev + x) − x_prev`), the Cockos 4-Tap Phaser topology reimplemented and generalised to a selectable number of stages. The coefficient `coef = (1 − d)/(1 + d)`, with `d = 2·fc/srate`, places the phase transition at the audible sweep frequency.
- **LFO sweep.** A sine LFO moves the allpass corner between the Range Min and Range Max endpoints. The notches sweep with it.
- **Stereo spread.** The right channel's LFO is offset from the left by the Stereo Spread angle, so the two channels' sweeps diverge.
- **Feedback.** The last stage's output is fed back into the chain input, resonating the notches (the hollow, vocal character).
- **Mix.** Dry and wet are summed; 50% gives the deepest notches (equal cancellation).

## Parameters

**Rate (Hz, or beats per cycle in Host x)** `0.001–1000, default 0.3` — LFO speed. Slow for long sweeps, faster for vibrato-like motion. In **Host x** this number is **beats per cycle** instead of Hz — see Host tempo sync below.

**Range Min Hz** `40–20000, default 300` — low endpoint of the sweep (where the notches sit at one extreme).

**Range Max Hz** `40–20000, default 1500` — high endpoint. The notches sweep between Min and Max. (Min/Max auto-sort, so order doesn't matter.)

**Feedback** `0–0.95, default 0.6` — resonance around the allpass chain. This is the hollow "whoosh." Push toward 0.9 for the dramatic jet-sweep; 0 for a soft, notches-only phase.

**Stages** `2–64 (even), default 6` — number of allpass stages. Each **2 stages adds one notch**. 4–6 is the classic musical phaser; the teens–20s thicken it; toward 64 it becomes a dense static "curtain" (dozens of notches) for sound design.

**Stereo Spread (degrees)** `0–180, default 90` — LFO phase offset between channels. 0 = mono motion, 90 = wide swirl, 180 = fully counter-rotating.

**Wet/Dry Mix** `0–1, default 0.5` — 0.5 gives the deepest notches; lower for subtler phasing.

## Usage Notes

- **Classic phaser:** Stages 4–6, Feedback 0.5–0.7, Rate ~0.3 Hz, Spread 90°, Range ~300–1500 Hz.
- **Sound-design curtain / "traffic":** Stages up in the 30s–60s, high Feedback — the notches get so dense they merge into a continuous swept resonant wash.
- **Stacking for complex motion (Bi-Phase trick):** two instances in series with *different* Rates drift against each other and beat — richer, evolving motion a single phaser can't make.
- **REAPER auto-mute warning.** One instance is safe at any setting. But **several identical copies on one track at very high Feedback** stay phase-locked (each LFO starts at the same point), so their resonant peaks line up and multiply in series — the level can spike hard enough that REAPER auto-mutes the track to protect your speakers. If that happens: drop Feedback (~0.5 is safe), **vary** the Rate/Range between the copies so they drift apart, or add a limiter after them.

---

*Stereo Phaser is part of the Rozaya JSFX plugin suite.*
*Designed by Rozaya — Developed with Claude (Anthropic).*


### Host tempo sync

**Rate Mode** `BPM / Seconds / Hz / Host x` (**default Hz**) — the suite's
canonical four, in the suite's canonical order, as of 2026-09-05 (R20).

**BPM** is sweeps per minute. **Seconds** is seconds per sweep. **Hz** is the
original free-running behaviour, sweeps per second, project tempo ignored.
**Host x** locks the sweep to the project, and Rate then means **every N beats**:
set it to 4 and one full sweep takes four beats. Tempo changes apply live.

**Why this one defaults to Hz when the rest of the suite defaults to BPM.** All
three saved instances in `strangeness.RPP` store *nothing* for this control, so
they take whatever the declared default is. It used to be `Own Hz` at position
one; putting Hz at the default lands them on exactly the behaviour they had, and
meant this change needed no edit to your project at all. The enum ORDER is
canonical; only which one starts selected differs.

This page used to say "Seconds and BPM would be meaningless here". That was
wrong — seconds per sweep is an ordinary way to say a speed — and consistency
across the suite outranks a per-plugin guess anyway.

**Beats per cycle is a plain number, not a menu.** 4 is every four beats. 3.7 is
every three and seven tenths of a beat — which no note-division grid can express,
and which is exactly the kind of thing this suite exists for. Bigger is slower.

> **Switching modes changes what Rate means, and nothing rescales it.** A rate of
> 0.3 is a slow sweep in Own Hz and just over a third of a beat per cycle — very
> fast — in Host x. Set the mode first, then the value.

**Host ratio (retired)** — hidden, and does nothing.
It used to be a menu of ratios (*every 4 beats*, *2 per beat* …) that wrote a
**multiplier** into Rate. The multiplier is gone, so the menu that translated it has
no job left: "every 4 beats" is now typing 4. The slider itself stays in the file
because slider positions are how REAPER remembers a saved project, so deleting one
would shift every control above it in every project you have.

---

#### Why the multiplier went, and why nothing hides any more

A multiplier is a number you cannot hear without doing arithmetic against the project
tempo — `0.25` is not a speed, it is a sum you have to finish. Because it was
illegible, the rate slider had to be **hidden** in Host x and the menu shown instead;
because it was hidden, entering Host x had to **stamp** a landing value into it so you
were not left on something arbitrary. That stamp is the bug that cost a session
elsewhere in the suite, where a saved project had its hand-set rate overwritten on
every load.

Beats per cycle is legible on its own, so the whole chain unwinds: nothing is hidden,
nothing is stamped, and the rate slider is always visible showing the value it is
actually running at. (Suite rule R13-revised, 2026-09-02.)
