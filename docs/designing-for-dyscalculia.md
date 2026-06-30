# Designing audio controls for a dyscalculic brain

Most accessibility work for audio software is about **blindness** — screen-reader
labels, keyboard navigation, not relying on mouse-only gestures. This is about a
different, far less discussed axis: **dyscalculia.** I'm dyscalculic as well as
blind, and the two together rule out the usual fix for each. These are the design
principles the Rozaya JSFX suite is moving toward — written down in case they're
useful to anyone else building instruments that people like me actually have to
*use*.

## The one principle

> **Never make the user produce a number. The user supplies the *feel*; the
> machine supplies the *number*.**

Everything below is a consequence of that.

## What a dyscalculic brain finds easy vs hard

It isn't "bad at math" in some flat, uniform way — it's specific. The faculties
split cleanly, and good control design routes *into* the spared ones and *around*
the impaired ones.

**Spared / easy — design into these:**

- **Pattern continuation.** Continuing an even, regular increment by feel
  ("…0.05, 0.10, 0.15…") is *counting*, not *computing* — painless once the
  pattern is set.
- **Powers of two and note-values** (`1/16, 1/8, 1/4, 1/2`) — because halving is a
  physical *bisection*, and note-values are *felt rhythm*, routed through the
  intact beat-perception channel rather than arithmetic.
- **Relative nudges** ("longer / shorter / more / less") and **tapping** — perform
  it; let the machine measure it.

**Impaired / hard — never force these:**

- **Unit conversion** (seconds ↔ steps ↔ beats).
- **Division**, especially by non-round numbers.
- **Ratios, proportions, and decimal fractions** off the power-of-two grid.
- **Absolute targets you must calculate** — versus a pattern you simply continue.

This tracks the research: calculation, division, ratio, and multi-step
working-memory tasks are the impaired functions, while **rhythm and beat
perception are a separate, *spared* faculty** — and time perception is normal
*right up until a numeral is introduced.* That last point is the whole game: the
moment a control forces a number, it drops you out of the channel you're strong
in.

## The blind + dyscalculia wrinkle

The standard sighted fix for dyscalculia is "show a live readout of the computed
result." That fix is unavailable here: navigating by the screen-reader parameter
list (not a visual canvas) means there's nothing to read the computed answer
*off of*. So the fix can't live on the display side. **It has to be input-side:**
the control itself speaks a felt unit, or offers a list to pick from, or borrows
an already-accessible value from elsewhere (the host's tap-tempo). Don't display
the answer — *change the question.*

## The fix-pattern toolkit

| Pattern | Use it for |
|---|---|
| **Note-value picker** — a list of `1/8, 1/4, …` you step through | any rhythmic / duration control |
| **Note-value increment** — step *and* min on a `0.0625` grid | rhythmic sliders kept as raw numbers |
| **Felt unit, machine converts** — bars / beats, not derived steps | rests, gaps, durations |
| **Ratio-friendly modes** — BPM over raw seconds | anything where relationships matter |
| **Host-tempo / tap sync** | borrowing the host's accessible tap-tempo |
| **Nudge-by-ear** — a clean small step, "tune it till it sits" | "get it feeling right" controls |
| **Relative-to-reference** | inter-voice / inter-layer timing |

The decimal grid is the recurring villain. A slider that steps
`0.01, 0.02 … 0.12, 0.13` *cannot land on `0.125`* — an eighth note lives
*between* two steps, so you're forced to type the decimal, straight back into
number-production. Re-grid to note-values, or replace the number with a picker,
and the brain's strongest channel becomes reachable by feel.

## Snap vs. nudge — you don't lose the groove

Making controls dyscalculia-friendly is **not** quantizing everything to a rigid
grid and flattening the feel. There are two *different* rhythm jobs, and they want
two *different* felt controls — neither of which needs a number:

- **Grid position** — *where a note nominally sits.* Discrete, snapped →
  **note-value picker.**
- **Expressive deviation** — *swing, "land it a hair late," humanize.* Continuous,
  found by ear → **nudge-by-ear.**

Nobody grooving thinks "set the offbeat to 0.667." They think *"more swing…
there."* That's the dyscalculia-friendly mode exactly: relative, felt, the machine
holding the fraction. Clean grid and expressive timing are *separate knobs* and
don't fight each other — you get fully off-grid feel with zero off-grid
arithmetic.

## The shape of it

None of this removes precision — it relocates *who has to produce the number.* A
worked precedent from this suite: replacing a "multiplier" control (a ratio you
compute) with a signed "+/− amount" (a delta you feel) kept every capability and
removed the math. Same move, generalized: the number still exists, exactly where
it always did — under the hood, where it belongs. **The fractions stay; they just
become the machine's currency, not the user's.**
