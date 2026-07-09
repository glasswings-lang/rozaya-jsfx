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

**Rate Hz** `0.01–10, default 0.3` — LFO speed. Slow for long sweeps, faster for vibrato-like motion.

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
