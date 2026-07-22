# Designing audio controls for a dyscalculic brain

Most accessibility work for audio software is about **blindness** — screen-reader
labels, keyboard navigation, not relying on mouse-only gestures. This is about a
different, far less discussed axis: **dyscalculia.** I'm dyscalculic as well as
blind, and the two together rule out the usual fix for each. These are the design
principles the Rozaya JSFX suite is moving toward — written down in case they're
useful to anyone else building instruments that people like me actually have to
*use*.

> **Working doc:** the implementation detail lives in
> [dyscalculia-accessibility-sweep.md](dyscalculia-accessibility-sweep.md) —
> per-plugin audit checklist, JSFX control reality, cross-instance rule. This
> page is the general write-up.

## The one principle

> **The barrier is ARITHMETIC, not numbers.** Reading a value, setting a value,
> comparing two values, nudging by feel — all fine. The wall is being made to
> **run an operation** to get from what you want to what the control needs.
> Never hand the user a calculation as a toll gate; the machine does any math.

Everything below is a consequence of that.

**An earlier draft of this page said "never make the user produce a number,"**
which reads as *keep numbers away from the user* — and that's the wrong fix, made
here once already and rejected. Precision is the job. A dyscalculic engineer
still needs `29.600`, not "a bit slower," and swapping honest values for opaque
mood-labels takes away a working tool to solve a problem it doesn't touch. The
digits were never the barrier. The **operation on un-anchored values** is:
`0.0625 ÷ 2` collapses; `480 − 440 = 40` is painless. Keep the precise control,
move the arithmetic.

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
result." **Inside a plugin, that's unavailable here:** navigating by the
screen-reader parameter list (not a visual canvas) means there's nothing to read
the computed answer *off of*. So in-plugin the fix has to be **input-side:** the
control itself speaks a felt unit, or offers a list to pick from, or borrows an
already-accessible value from elsewhere (the host's tap-tempo). Don't display the
answer — *change the question.*

**But that's a limit of the plugin canvas, not of display.** A terminal is
perfectly accessible. A companion script can print the answer *and the working
that produced it*, and that lands fine — because the deficit is in **holding** a
multi-step chain, not in reading one. A chain you can re-read as many times as you
like is auditable; the same chain in working memory is not. So the rule outside
the plugin inverts: **show everything, including the intermediate steps.** A bare
answer you have to trust is worse than a derivation you can check.

## What a plugin structurally cannot fix

Input-side design only reaches relationships *inside* one instance. A second
instance of the same plugin has no idea the first one exists — so "make voice 8
of this one land just under voice 1 of that one" is not a control that can be
built, at any level of design effort. Same for anything spanning two different
plugins.

Those relationships are exactly where the arithmetic is worst (you're crossing a
boundary, so nothing is anchored), and they're unreachable from inside. **That
work belongs in a small external tool** that takes the felt intent, does the
math, and shows its working. Not a fallback — the correct home.

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
