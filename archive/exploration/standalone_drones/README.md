# Experimental Drone Synths (archived)

These plugins were experimental drone synthesizers exploring a single
question from several directions: how to shape a sound's character by
ear, without relying on a visual waveform display. Each was a
different approach to that problem; none was presented as a finished
answer.

They were moved here from `src/standalone/` in 2026-06 after the
broader architectural goal (experimental oscillator paradigms feeding
back into the main suite) hit blockers: the plugins shipped mono in a
stereo suite, and JSFX's read-only file I/O ruled out the
"capture-a-wave-and-use-it-everywhere" workflow that would have
justified them.

They are preserved here as a record of the exploration and because
they may be useful to others. They are not maintained.

Like the rest of the suite, they are released into the public domain
under CC0 and are free to use, study, and modify.

## The plugins

### Additive Drone

Sixteen sliders, each setting the loudness of one harmonic. A tone is
built up from a pure sine by raising individual harmonics. Tested and
working as described.

### Harmonic Drone

The same engine as Additive Drone, but pre-loaded to a sawtooth —
every harmonic present, each quieter than the last. Harmonics are
removed from a rich tone rather than added to a bare one. Tested and
working as described.

### Shape Drone

A single Shape slider morphs continuously through sine, triangle, saw,
and square. A Symmetry slider tilts the wave; a Brightness slider
softens the high end. The saw and square discontinuities are
anti-aliased using PolyBLEP. Tested and working as described.

Known limitation: the Shape slider uses linear amplitude crossfading
between adjacent reference waveforms — intermediate Shape values
produce a SUM of two waves at reduced amplitude, not a clean
intermediate shape. A proper morph would require geometric
interpolation, phase distortion, or wavetable-grid lookup; none of
those landed.

### Point Drone

Eight sliders, each setting the wave's height at one point along the
cycle, with the wave drawn as the line segments connecting them.
Intended for drawing a waveform by ear, one point at a time. Tested
and working as described.

### Feature Drone

A Peak and a Trough are each placed on the wave with a position and a
height, and the wave is drawn through them. Suited to triangle-family
shapes. Two known quirks: setting both the Peak and Trough heights to
the same sign can produce an audible click at the cycle boundary, and
the Peak and Trough labels exchange roles if their positions are
crossed.

### Feel Drone

Six controls described in perceptual rather than technical terms —
Warmth, Brightness, Edge, Hollowness, Body, and Movement — each
driving a harmonic recipe internally. One known quirk: Hollowness
works by removing even harmonics, so it has no audible effect on its
own; another control (Warmth, Body, or Edge) must first place energy
in those harmonics. On the default patch this is not an issue.

### Mode Drone

All four approaches above — Feel, Shape, Points, and Additive —
combined in one plugin and selected with a Mode control. The inactive
modes' sliders are hidden from the REAPER UI but remain available in
OSARA's parameter list. It inherits Feel mode's Hollowness behavior
and is the most complex plugin of the set.

### Harmonic Sculptor

The most experimental and least tested plugin in the set. A base wave
is chosen, the plugin analyses it into 64 harmonics and loads them,
and any harmonic can then be adjusted by ear. Selection uses a
two-slider editor (described below), and the selector carries
musical-interval labels. Output loudness is normalized automatically.
This plugin was unfinished and unverified at archive time. A companion
feature to announce the full harmonic state on a key press was planned
but not built. The interval labels become approximate above roughly
the 32nd harmonic.

## The Two-Slider Harmonic Editor (Harmonic Sculptor)

To avoid presenting 64 separate sliders, Harmonic Sculptor uses a
selector-and-editor pair: one slider selects which harmonic is being
edited, and a second sets its level. Moving the Harmonic Select slider
loads the selected harmonic's stored level into the Harmonic Level
slider so that it displays correctly.

There is an accessibility limitation that screen-reader users should
be aware of. The Harmonic Level slider always announces as "Harmonic
Level"; it does not announce which harmonic is being edited, because
JSFX cannot change a slider's spoken name at runtime. The Harmonic
Select slider does carry interval labels (for example, "H5 +maj3rd
(flat)") and announces the musical interval as it moves, but the
selected harmonic must be kept in mind when switching to the Level
slider. This division was the central unresolved usability problem
with the plugin and is the reason it is marked most experimental.

## Stereo limitation across the set

7 of the 8 plugins ship as dual-mono — the same signal on both
channels, with no per-channel processing. Only `additive_drone.jsfx`
produces true stereo. This is one of the things that prevented the
set from being promoted to first-class status alongside the rest of
the suite.

---

*Designed by Rozaya — Developed with Claude (Anthropic). Released
into the public domain under CC0.*
