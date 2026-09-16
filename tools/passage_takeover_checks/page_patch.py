"""docs/plugins/spectral-vowel-passage.md for the takeover build (2026-09-16)."""
p = r'C:/git-src/rozaya-jsfx/docs/plugins/spectral-vowel-passage.md'
s = open(p, encoding='utf-8').read()


def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:120])
    s = s.replace(a, b)


def cut(a_start, b_start, new):
    """Replace from the line starting a_start up to (not including) the line starting b_start."""
    global s
    i = s.find(a_start); j = s.find(b_start, i)
    assert i >= 0 and j > i, (a_start[:60], b_start[:60])
    s = s[:i] + new + s[j:]


# --- the intro: Passage now has everything the Morpher had
rep("""> Controls are also grouped by what they belong to rather than by when they were""",
""">
> **4. Since 2026-09-16 Passage has everything the Morpher has.** Sixteen layers, the
> Morpher's continuous Auto-morph at a rate, Spread and both cuts as pitch blocks, and 111
> Drift and Ramp targets. Rozaya: *"the closer morfer gets to where I'd want it to be, the
> more like passage it is than not."* The voice is also much lighter to run (one prepared
> wave per voice instead of 64 tones), and **the wash no longer boosts itself**: see
> **Output level**.
>
> Controls are also grouped by what they belong to rather than by when they were""")

# --- the pitch block
cut("### The pitch block — *per slot*", "Drift and Ramp are applied ON TOP of Transpose value", """### The pitch block — *per slot*

Eight controls set a slot's pitch, built the way Bubbler's are. Every slot has its own, and nothing sounds different until you change one. Every name starts with **Pitch** (since 2026-09-16), and each unit picker sits before the value it sets.

**Pitch source note (where zero is)** `None, C-1 … G9, default None`
Which note the capture already is. It changes nothing on its own: it tells **Pitch target note** where zero is, so you can then transpose by note name. Moving it later re-reads the target note and leaves the sound alone.

**Pitch source fine tune unit** `Hz / Semitones / Cents, default Cents`, then **Pitch source fine tune (only with a Pitch source note, in Semitones)** `-1000 to 1000, default 0`
For a capture that sits between two notes. It acts only while a Pitch source note is set and **Pitch transpose mode** is Semitones, which is what its name says. In Hz it counts from the source note's own frequency. It is a Drift and Ramp target: a drift on it moves what the target note lands on, so the sound moves the opposite way to the drift.

**Pitch target note (only with a Pitch source note, in Semitones)** `C-1 … G9`
The note you want to hear. Picking one sets **Pitch transpose value** to the distance from the source note; moving the value shows the nearest note here.

**Pitch transpose mode** `Hz / Semitones / Cents, default Semitones`, then **Pitch transpose value (Hz / semitones / cents)** `-20000 to +20000, default 0`
How far to shift the slot. In Semitones and Cents it is an interval. In Hz it counts from the **Tuning reference**, so with the reference at 440, a value of 440 is one octave up.

**Pitch fine tune unit** `Hz / Semitones / Cents, default Cents`, then **Pitch fine tune** `-1000 to 1000, default 0`
Added on top of the transpose value.

""")

# --- Spread, Low cut, High cut
cut("**Spread (Hz, per slot)** `0 to 1000, default 0`", "**Denoise (%, wash only, per slot)**", """**Spread pitch mode** `Hz / Semitones / Cents, default Hz`, **Spread value (Hz / semitones / cents)** `0 to 1000, default 0`, **Spread fine tune unit** `Hz / Semitones / Cents, default Cents` and **Spread fine tune** `-1000 to 1000, default 0` — *per slot*
Blurs the spectrum across frequency — diffuses a narrow capture into a wider noise bed. In **Hz** the blur is one fixed width everywhere, so it swallows the gaps between low harmonics and barely touches high ones; that is what every saved project uses, and with no fine tune it is exactly the blur it always was. In **Semitones** or **Cents** each frequency blurs by that interval either side, evenly across the range. A fine tune in Hz then widens both sides by that many Hz. No note name: it is a width, not a note. Spread and Spread fine tune are both Drift and Ramp targets.

*Per slot.* Belongs to whichever **Capture slot** is selected; the morph crossfades it between slots along with the sound itself.

""")
cut("**Low cut (Hz, per slot)** `0 to 20000, default 0`", "### Overtone — one voice, two notes", """**Low cut pitch mode** `Hz / Semitones / Cents, default Hz`, **Low cut note name** `Off, C-1 … G9`, **Low cut value (0 = off)** `0 to 20000`, **Low cut fine tune unit** `default Cents` and **Low cut fine tune** `-1000 to 1000, default 0` — *per slot*
Removes low rumble from the wash. **0 is off in every unit**, and the note list starts on a dedicated **Off**. In Semitones the value is a note number (69 is A4 at the Tuning reference), in Cents that times 100. The note name and the value follow each other, and switching the mode converts the value so the cut stays where it was. A drift or ramp on a cut that is on stops at the lowest real frequency instead of switching it off, and moves nothing while it is off. The cut and its fine tune are both Drift and Ramp targets.

**High cut pitch mode**, **High cut note name**, **High cut value (0 = off)**, **High cut fine tune unit** and **High cut fine tune** — the same block as Low cut, default off — *per slot*
Removes the top of both engines. Its off was 20000 until 2026-09-16; every saved project's 20000 became 0, so it is still off. A drift on a cut that is on stops at 200 Hz or the cut's own frequency, whichever is lower.

*Per slot.* Both cuts belong to whichever **Capture slot** is selected; the morph crossfades them between slots.

""")

# --- slot timing names
for a, b in (("**Slot fade in (seconds / Hz / beats, per slot)**", "**Slot fade in (in slot timing units)**"),
             ("**Slot hold (seconds / Hz / beats, per slot)**", "**Slot hold (in slot timing units)**"),
             ("**Slot fade out (seconds / Hz / beats, per slot)**", "**Slot fade out (in slot timing units)**"),
             ("**Slot gap after (seconds / Hz / beats, per slot)**", "**Slot gap after (in slot timing units)**")):
    rep(a, b)
rep("**Slot timing unit (per slot)** `Seconds / Hz / Beats, default Seconds`",
    "**Slot timing unit (per slot)** `Seconds / Hz / Beats, default Seconds` — sits above the four timings it sets (since 2026-09-16)")

# --- Output level: the wash's hidden boost is gone
cut("**Output level (dB, per slot)** `-60 to +24, default 0`", "**Tuning reference (Hz)**", """**Output level (dB, the wash is no longer auto-boosted)** `-60 to +24, default 0` — *per slot*
The level of everything this slot *makes* — both the voice and the wash, after the voice/wash crossfade. The dry input is the one thing it doesn't touch; that has its own **Input level**.

**Since 2026-09-16 the number is the whole story.** Until then the wash ran through a hidden auto-gain that pulled every grain to one loudness: on the saved projects it added between about 38 and 65 dB, steadily, whatever you set. In the Morpher it also undid Layer 1's level and pushed the other layers up to match. Rozaya: *"-24 db is -24db, it shouldn't be moved up by some overeager hardcoded thing."* Now the wash has one fixed gain, and a capture's wash is as loud as its sound is full. **Saved projects were moved to sound as loud as they did**: each captured slot's Output level was raised or lowered by what the auto-gain had been giving it, measured slot by slot (Rozaya: *"I say you can try to make them sound the same."*).

*Per slot.* Belongs to whichever **Capture slot** is selected; the morph crossfades it between slots along with the sound itself.

""")

# --- Layers, after Overtone width
rep("""**Morph (% across captured slots)** `0 to 100, default 0`""", """### Layers — *whole plugin*

Extra copies of the whole morph — voice and wash both — at their own pitch, locked to the same morph position, so an octave stack stays consonant however the slots move. Each layer's pitch is an offset from **each slot's own pitch**, so the stack moves with every slot. The layers are one set for the whole plugin, not per slot. Rozaya: *"the per slot layering doesn't really make sense to me ... I would just have it be global."* To thicken one thin slot, use a layer and that slot's own settings.

**Layer** `All, Layer 1 to Layer 16, default Layer 1`
Which layer the controls below show. **Layer 1 is the original sound**, and moves like any layer. **All** shows Layer 1 and sends any control you move to all sixteen; only the control you actually move goes across.

**Where each layer starts.** Layer 1 is Active at 0 dB, pitch 0 — so a saved project sounds as it did. Layers 2–16 start **Inactive at −6 dB** (Rozaya: *"If they're not active they don't need to be that low, they're just... off."*), on the Morpher's pitches: Layers 2–7 at −48, −36, −24, −12, −7 and −5 semitones, Layers 8–13 at +5, +7, +12, +24, +36 and +48, Layers 14–16 at −12, +12 and −24.

**Layer active** `Inactive / Active` — switches a layer on or off and keeps its level for when you switch it back.

**Layer pitch mode** `Hz / Semitones / Cents, default Semitones`, then **Layer pitch value (Hz / semitones / cents)** `-20000 to +20000`, then **Layer fine tune unit** `default Cents` and **Layer fine tune** `-1000 to 1000, default 0`
The layer's distance from each slot's pitch. In Hz it counts from the Tuning reference, as Pitch transpose does.

**Layer level (dB, -60 = off)** `-60 to +24` — a real level: −24 dB is 24 dB down, in the voice and the wash (see **Output level**).

**Layer solo** `Off / Solo` — any layer soloed silences every layer that isn't, the original included. Solo overrides Active.

**Layer harmonics (0 = full)** `0 to 64, default 0` — keeps only the layer's first partials: thinner, and lighter to run.

**Layer overtone harmonic (-1 = follow the global)** `-1 to 64, default -1` — gives this layer its own overtone harmonic, with the slots' Overtone lift and the plugin's Overtone width. It acts while the slots' overtone is on.

Every layer's pitch, fine tune, level, harmonics and overtone harmonic is a Drift and Ramp target, each with an **(all layers)** entry that reaches all sixteen.

**Cost.** Each audible layer is two more voices (and a second read of the wash spectrum). A layer that is Inactive or at −60 costs nothing. Measured in the test runner on nightfall, all voice: one voice about 5 ms per 11.6 ms block, all sixteen layers about 12 ms.

### The morph

**Morph (% across captured slots)** `0 to 100, default 0`""")

# --- Auto-morph timing and rate
rep("""**Fixed: a click at slot changes.** Up to and including the build shipped""",
"""**Auto-morph timing** `Slot timings / Rate, default Slot timings`
**Slot timings** is the walk described above: each step lasts the leg of the slot it is leaving. **Rate** is the Morpher's continuous motion: **Sweep** and **Glide once** move smoothly along your unmuted slots in one pass of the rate's time, and **Shuffle** crossfades between shuffled slots, each taking an equal share. Rate has no fades or gaps of its own. In Rate, a **Cycle** (in the drift and ramp units) is one pass. Rozaya, on bringing it back: *"Passage needs it."* Every saved project is on Slot timings.

**Auto-morph rate mode** `BPM / Seconds / Hz / Every N beats / N per beat, default Seconds`, then **Auto-morph rate value** `0.01 to 1000, default 20`
How long one pass takes in Rate, counted in the unit chosen: passes per minute, seconds per pass, passes per second, beats per pass, or passes per beat. Auto-morph rate is a Drift and Ramp target.

**Fixed: a click at slot changes.** Up to and including the build shipped""")

# --- transport names and rest mode
rep("**Start delay (seconds / Hz / beats)** `0 to 1000, default 0`", "**Transport unit** `Seconds / Hz / Beats, default Seconds` — sits above the three it sets (since 2026-09-16)\n\n**Start delay (in transport units)** `0 to 1000, default 0`")
rep("**Play for** / **Rest for (seconds / Hz / beats, 0 = always)** `0 to 1000, default 0`", "**Play for** / **Rest for (in transport units, 0 = always)** `0 to 1000, default 0`")
cut("**Transport unit** `Seconds / Hz / Beats, default Seconds`\nWhat the three above", "**Rest mode** `Walk through", "")
rep("**Rest mode** `Walk through / Freeze in place, default Walk through`\nDuring a rest, whether the walk through the slots carries on unheard or waits where it is.",
    "**Auto-morph rest mode** `Walk through / Freeze in place, default Walk through`\nDuring a rest, whether the walk through the slots carries on unheard or waits where it is. (Named *Rest mode* until 2026-09-16.) Drift and Ramp have their own: **Drift rest mode** and **Ramp rest mode**, both Walk through by default.")
rep("Both are Drift and Ramp targets, so the rhythm of play and rest can itself wander or slowly change.",
    "Both are Drift and Ramp targets, so the rhythm of play and rest can itself wander or slowly change. On **With the target** (their default) a stretch keeps the length it began with; **On a clock** reads it live.")

# --- Drift target list and the six globals
cut("**Drift target** `Transpose / Fine tune", "**Drift is per slot, like everything else here.**", """**Drift target** — a hundred and eleven, in the order of the controls they reach (2026-09-16; it was twenty-two): `Morph / Auto-morph rate / Slot fade in / Slot hold / Slot fade out / Slot gap after / Texture / Pitch source fine tune / Pitch transpose / Pitch fine tune / Tuning reference / Spread / Spread fine tune / Stereo width / Denoise / Low cut / Low cut fine tune / High cut / High cut fine tune / Overtone harmonic / Overtone lift / Overtone width / Layer pitch (all layers) / Layer 1-16 pitch / Layer fine tune (all layers) / Layer 1-16 fine tune / Layer level (all layers) / Layer 1-16 level / Layer harmonics (all layers) / Layer 1-16 harmonics / Layer overtone harmonic (all layers) / Layer 1-16 overtone harmonic / Input level / Output level / Play for / Rest for`, default Morph
Which parameter the Drift controls below are editing. A saved project's drifts moved with their targets. **Wash grain is no longer a target** (a fast drift on it made the wash wobble in loudness whatever the timing; no saved project drifted it). An **(all layers)** entry shows Layer 1's settings and a setting you move reaches all sixteen.

""")
rep("**Six targets belong to the whole plugin and ignore the slot selector: Tuning reference, Overtone width, Morph, Input level, Play for and Rest for.**",
    "**The whole-plugin targets ignore the slot selector: Morph, Auto-morph rate, Tuning reference, Overtone width, every layer target, Input level, Play for and Rest for.**")
rep("**Drift period** `0 to 1000, default 30, 0 = off` — *per slot and target*, in the **Drift period unit** `Cycles / Seconds / Beats, default Seconds` — *all targets*",
    "**Drift period unit** `Cycles / Seconds / Beats, default Seconds` — *per slot and target since 2026-09-16* (a saved project's one unit started every target), then **Drift period** `0 to 1000, default 30, 0 = off` — *per slot and target*")
rep("Only the four slot timings tell these apart.", "Only the four slot timings, and Play for and Rest for, tell these apart.")
rep("**Drift restart (all targets)** `Restart on play / Free-running, default Restart on play`",
    "**Drift rest mode** `Walk through / Freeze in place, default Walk through` — whether a transport rest holds the drifts.\n\n**Drift restart (all targets)** `Restart on play / Free-running, default Restart on play`")
rep("**Ramp target** — the same 22 targets as Drift, default Transpose", "**Ramp target** — the same 111 targets as Drift, default Morph")
rep("the six whole-plugin targets ignore the slot", "the whole-plugin targets ignore the slot")
rep("**Ramp time unit** `Cycles / Seconds / Minutes / Beats, default Minutes` — *all targets*", "**Ramp time unit** `Cycles / Seconds / Minutes / Beats, default Minutes` — *per slot and target since 2026-09-16*")
rep("**Ramp engage** `Off / On, default Off` — *all targets*", "**Ramp rest mode** `Walk through / Freeze in place, default Walk through` — whether a transport rest holds the rides.\n\n**Ramp engage** `Off / On, default Off` — *all targets*")

# --- the auto-gain gotcha section no longer applies
cut("### The auto-gain needs extra time coming out of silence", "## The per-slot rule", """### Coming out of silence

Until 2026-09-16 the wash's auto-gain could bloom as a slot faded in out of a gap, because it froze at its old boost through the silence. That auto-gain is gone (see **Output level**), so there is nothing to catch up.

""")

# --- the global / per-slot lists
rep("- The pitch block: Source note, Source fine tune and its unit, Target note, Transpose value and its unit, Fine tune and its unit\n- Texture, Wash grain, Spread, Denoise, Low cut, High cut, Overtone harmonic, Overtone lift, Stereo width, Output level",
    "- The pitch block: Pitch source note, Pitch source fine tune and its unit, Pitch target note, Pitch transpose mode and value, Pitch fine tune and its unit\n- Texture, Wash grain, the Spread block, Denoise, the Low cut and High cut blocks, Overtone harmonic, Overtone lift, Stereo width, Output level")
rep("- Tuning reference, Fade in shape, Fade out shape, Overtone width, Morph, Auto-morph, Audition, Input level\n- The transport: Start delay, Play for, Rest for, Transport unit, Rest mode, Output at rest\n- Drift period unit, Drift restart, Ramp time unit, Ramp engage\n- The Drift and Ramp settings of the six whole-plugin targets",
    "- Tuning reference, Fade in shape, Fade out shape, Overtone width, Morph, Auto-morph and its timing and rate, Audition, Input level\n- The layers: all ten layer controls\n- The transport: Transport unit, Start delay, Play for, Rest for, Auto-morph rest mode, Output at rest\n- Drift rest mode, Drift restart, Ramp rest mode, Ramp engage\n- The Drift and Ramp settings of the whole-plugin targets")

open(p, 'w', encoding='utf-8').write(s)
print('ok')
