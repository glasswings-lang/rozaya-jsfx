#!/usr/bin/env python3
"""Read and write the slider-value line of a REAPER `<JS>` block.

WHY THIS EXISTS
---------------
Because getting it wrong is silent, and it happened. On 2026-09-02 a Melody
Phase migration treated the line as a plain list of numbers, which shifted every
slider from 65 upward by one position and wrote twelve instances of nonsense
into five projects. Nothing errored. The projects were restored from backup, and
this module exists so the knowledge lives in ONE place instead of being
re-derived, differently, by every migration script.

WHAT THE LINE ACTUALLY LOOKS LIKE
---------------------------------
Measured across the whole project library, not inferred:

  1. **A plugin with 64 sliders or fewer** writes exactly 64 tokens, padding with
     `-` for slots it has nothing to say about.

  2. **A plugin with more than 64 sliders** writes the first 64 values, then a
     quoted token `""` at index 64, then the values for slider 65 onward. The
     marker is ALWAYS at index 64 -- 76 instances in the library, no exceptions.
     So the token index of slider N is `N-1` up to 64, and `N` beyond it.

  3. **A file-selector slider's value is a quoted string**, not a number
     (Sustain Looper's slider 1 is a filename). Quoted tokens are carried
     through untouched; never parse one as a float.

  4. `-` means "no value stored", and can sit between real values as well as
     trailing. Filtering dashes out before indexing shifts everything after the
     gap -- the trap CLAUDE.md already warned about, of which the `""` marker
     turned out to be a second flavour.

USE
---
    slots = parse_line(line)              # {slider_id: token or None}
    slots[9] = "3"
    new_line = render_line(line, slots, n_sliders=80)

`render_line` keeps the original indentation and line ending, re-inserts the
marker in the right place, and refuses to produce a line it cannot parse back
into the values it was given -- so a caller cannot silently write a shifted line.
"""

MARKER_INDEX = 64          # the `""` token sits immediately after slider 64
PAD_TO = 64                # plugins with <= 64 sliders are padded to this


class SliderLineError(ValueError):
    pass


def _split(line):
    # Handle every ending, including a real '\n'. This used to notice only a
    # trailing '\r', on the assumption that callers passed lines already
    # stripped of their ending -- so a caller using splitlines(keepends=True)
    # got a rendered line with NO ending at all, which welded itself onto the
    # next line of the .RPP and silently dropped a line per instance. Caught on
    # 2026-09-02 by verifying the output; the caller was fixed too, but the
    # trap belonged here.
    for cand in ("\r\n", "\n", "\r"):
        if line.endswith(cand):
            eol = cand
            break
    else:
        eol = ""
    body = line[: len(line) - len(eol)]
    indent = body[: len(body) - len(body.lstrip())]
    return indent, body.strip().split(), eol


def is_marker(tok):
    """The separator REAPER writes after slider 64 (an empty quoted string)."""
    return tok == '""'


def is_quoted(tok):
    return len(tok) >= 2 and tok.startswith('"') and tok.endswith('"')


def parse_line(line):
    """Map slider id (1-based) -> its token, or None where nothing is stored.

    Raises SliderLineError if the line does not match the documented shape,
    rather than guessing -- a migration should stop, not improvise.
    """
    _, tokens, _ = _split(line)
    if not tokens:
        raise SliderLineError("empty value line")
    if len(tokens) > MARKER_INDEX and not is_marker(tokens[MARKER_INDEX]):
        raise SliderLineError(
            "expected the '\"\"' marker at token index %d, found %r -- the line "
            "does not have the shape this module knows about"
            % (MARKER_INDEX, tokens[MARKER_INDEX]))
    slots = {}
    for k, tok in enumerate(tokens):
        if k == MARKER_INDEX and len(tokens) > MARKER_INDEX:
            continue                      # the marker is not a slider
        sid = k + 1 if k < MARKER_INDEX else k
        slots[sid] = None if tok == "-" else tok
    return slots


def render_line(original, slots, n_sliders):
    """Rebuild the line from `slots`, preserving indentation and line ending.

    Verifies by parsing its own output back and comparing, so a shift cannot
    escape unnoticed.
    """
    indent, _, eol = _split(original)
    vals = [slots.get(i) for i in range(1, n_sliders + 1)]
    toks = ["-" if v is None else str(v) for v in vals]
    if n_sliders <= PAD_TO:
        toks += ["-"] * (PAD_TO - len(toks))
    else:
        toks = toks[:MARKER_INDEX] + ['""'] + toks[MARKER_INDEX:]
    out = indent + " ".join(toks) + eol

    back = parse_line(out)
    for i in range(1, n_sliders + 1):
        if back.get(i) != (None if slots.get(i) is None else str(slots.get(i))):
            raise SliderLineError(
                "round-trip check failed at slider %d: wrote %r, read back %r"
                % (i, slots.get(i), back.get(i)))
    return out


def as_float(tok, what="value"):
    if tok is None:
        return None
    if is_quoted(tok):
        raise SliderLineError("%s is a quoted string (%r), not a number" % (what, tok))
    try:
        return float(tok)
    except ValueError:
        raise SliderLineError("%s is not numeric: %r" % (what, tok))


def fmt(x):
    """REAPER's own style: integers without a trailing .0."""
    return str(int(x)) if float(x) == int(float(x)) else repr(round(float(x), 6))
