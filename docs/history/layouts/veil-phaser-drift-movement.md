# Veil and the Stereo Phaser: Drift movement, 2026-09-16

Found 2026-09-16: `Play for` and `Rest for` were drift and ramp targets in both, and
nothing read them (drifting Play for rendered bit-identical to not drifting it; drifting
Output / Wet-dry set up the same way did change the sound). Wiring them in makes them
per-occurrence targets, so the fix brings `Drift movement {With the target, On a clock}`.
Rozaya: *"1 sounds like a bug, the other sounds like a gap"*, then *"Yes pls"*.

## What the switch means here

- **With the target** (default): a play or rest stretch takes its length when it BEGINS,
  drift and ramp included, and keeps it to the end. The next stretch reads again.
- **On a clock**: the length is re-read every sample, so a drift can end the stretch
  being heard early or late (what the Morpher does today).
- Neither plugin has any other per-occurrence target, so the switch is shown only while
  the Drift target is Play for or Rest for.
- The gate still switches on only when BOTH sliders are above zero, as in Heartbeat and
  the Morpher.

## The one move, each plugin

One new control, right after `Drift period`. Everything after it moves down one.

Veil (35 -> 36):   new 22 `Drift movement`;  old 22-35 -> 23-36.
Stereo Phaser (38 -> 39): new 25 `Drift movement`;  old 25-38 -> 26-39.

Renumber map for `tools/jsfx_renumber.py`: Veil `"22-35:+1"`, Phaser `"25-38:+1"`.

## Saved state

`@serialize` magic 3700013 in both: the 3600013 format plus one bank, `drift_moves_mem`,
13 wide, appended last. An older blob leaves every target on With the target (0).
The .RPP migration inserts `0` at the new slider and transcodes the blob to 3700013 by
appending 13 zeros, so its idempotency check is the blob's magic.
