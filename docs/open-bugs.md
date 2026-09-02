# Open bugs

Things that are known-broken and NOT fixed. Newest first. A bug leaves this file
only when it has been fixed *and* heard.

---

## 1. Melody Phase instances come in out of alignment on project open

**Status: OPEN. Cause unknown. Do not attempt a fix without reading "What was
already tried" below — three wrong theories have been shipped or nearly shipped.**

Reported by Rozaya, 2026-09-02.

### The symptom

- Open a project containing several Melody Phase instances. **Do not press play.**
- They do not come in together. In `simple-sequence` (12 instances, all synced,
  every Start Delay 0) they arrive at visibly different times.
- **A play/stop cures it.** After that they are correct.
- **Renders were always fine.**
- Rozaya, on the synced project: *"each thing comes in at a slightly different
  time... a quick play and stop fixes it."*
- On `upswing` (17 instances, **none synced**): *"didn't come in staggered in the
  same way. It just came in stacked up. It came in drifting as if the clocks are
  slightly off. They all came in at the same time, but it does sound like there
  might have been a stagger going on."*

### What is known for certain

- **It predates 2026-09-02.** Rozaya: *"This predates you."* It is NOT caused by
  the layout reorder, the migration, or anything done that day.
- **It appeared when host sync was implemented** (2026-08-11), by Rozaya's
  account: *"The melody phase didn't even do this before host-sync. Melody phase
  would come in fine."*
- **It is not Start Delay staggering.** `simple-sequence` has every Start Delay at
  0 and still staggers. (`upswing`, which is unsynced, is where the hand-computed
  delays live: 0, 5, 8, then four at 4 and four at 8.)
- **It is not Drift or Ramp.** Rozaya has not used them on these; measured across
  all 58 instances, Ramp amount and duration are 0 everywhere.
- **The unsynced project is not clean either**, which is the single most important
  fact here and the one that rules out the obvious theory. Whatever this is, it is
  not purely about sync.

### What was already tried, and why each was wrong

1. **"The sequence-placement feature is not firing."** Placement only ever ran
   under Host x and now under sync. Rejected: it does not explain `upswing`, which
   is unsynced and has no placement to fail.

2. **"`@init` zeroes the placement gate on every play."** This one was REAL but was
   a bug introduced on 2026-09-02 (`seq_synced = 0` in `@init`, which `@slider`
   never re-runs to undo). Fixed in `3b42f07`. It cannot be the reported cause,
   because the report predates it.

3. **"`@sample` has no transport test, so each instance free-runs from the moment
   it is instantiated, and REAPER loads plugins one at a time."** Shipped as a
   hold-until-transport-moves gate, and **reverted** (`dcfeead`) — it was wrong and
   it removed something Rozaya needs, namely hearing the plugin with the transport
   stopped. Rozaya: *"now you take that away for what? To force me to play the
   project if I wanna hear something happening. No."*
   The observation about `@sample` is nonetheless TRUE and worth keeping: there is
   no `play_state` test anywhere in Melody's `@sample`. Only `polyrhythm_phase`
   and `_v3` have one; fourteen other plugins with sync do not. That is a fact
   about the code. It has **not** been shown to be this bug's cause, and the
   arithmetic cuts against it — it also fails to explain why it started with host
   sync, since it was equally true before.

### The next honest step

Not another theory. An **observation that separates causes**, or instrumentation.

Useful discriminators, cheapest first:

- Does the stagger amount **change between two opens of the same project**? If yes,
  it tracks something about load (order, timing). If it is the same every time, it
  is deterministic and lives in the plugin's own state.
- Does **one** instance alone, in a fresh project, come in correctly? If a single
  instance is fine and two are not, it is about them relative to each other.
- Does it depend on **project tempo**? `simple-sequence` is 205 BPM, `upswing` 120.
- **Instrumentation beats guessing:** a temporary build that writes
  `play_position` / `beat_position` / `srate`-elapsed at the first sequencer
  trigger, so the actual start offsets can be read rather than inferred.

### Discipline note

Three wrong mechanisms in one day on this one bug, two of them stated as findings
and one of them shipped. CLAUDE.md already carries the rule — *a plausible
mechanism is not a finding; ask what else produces exactly this symptom* — and it
was not followed. Rozaya's framing is the test to apply: **"read and compare,
don't script"**, and check whether the theory explains ALL the observations,
including the inconvenient one (here: `upswing`).

### State of the work around it

Melody Phase's reorder, note names, tempo-sync block and v2 archival are BUILT and
committed on `feature/melody-reorder`, but **rolled back on disk**: the five
projects are restored byte-identical to `E:\reaper\_pre-melody-reorder-20260902`,
and the installed plugin (and v2) are back to the pre-reorder versions. Nothing is
lost — the migration is reproducible from `tools/melody_migrate_layout.py` — but
none of it should go back in front of Rozaya until this bug is understood, since
it would put the new build on top of an unexplained timing fault.
