#!/usr/bin/env python3
"""Carry each R25 kind onto the plugin pages, from the AUTHORED list only.

Updates ENTRY lines: a bold control name followed by its range in backticks, e.g.
    **Drift up amount** `0 to 1000, default 0`
becomes
    **Drift up amount (per target)** `0 to 1000, default 0`
and a bold name already holding parentheses takes the kind first inside them, the same
way the labels did: **Drift period (per band and target, BPM / Hz ...)**. Prose mentions
are left alone. The kind comes from docs/layouts/r25-labels-20260912.md for the page's
own plugin; an entry whose name matches no row for that plugin is REFUSED and reported,
never guessed.

    python tools/r25_pages_apply.py            # dry run
    python tools/r25_pages_apply.py --apply    # write, then re-read and verify
"""
import collections, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from r25_names import base  # noqa: E402

LIST = os.path.join(ROOT, "docs", "layouts", "r25-labels-20260912.md")
APPLY = "--apply" in sys.argv
PAGES = {  # page -> plugin file, authored
    "tremolo.md": "Full_Feature_Tremolo.jsfx", "breath-generator.md": "breath_gen.jsfx",
    "bubbler.md": "bubbler.jsfx", "dapple.md": "dapple.jsfx",
    "sweeping-filter.md": "full-feature-sweeping-filter.jsfx", "heartbeat-generator.md": "heartbeat gen.jsfx",
    "melody-phase.md": "melody_phase.jsfx", "polyrhythm-phase-v3.md": "polyrhythm_phase_v3.jsfx",
    "resonance-bank.md": "resonance_bank.jsfx", "rhythm-track.md": "rhythm-track.jsfx",
    "shepard-scale.md": "shepard-scale.jsfx", "shepard-tone.md": "shepard-tone.jsfx",
    "spectral-vowel-morpher.md": "spectral_vowel_morpher.jsfx", "stereo-phaser.md": "stereo-phaser.jsfx",
    "sustain-looper.md": "sustain_looper.jsfx", "veil.md": "veil.jsfx",
    "womb.md": "womb_sound_generator_v3.jsfx", "sweep-dwell-filter.md": "sweep-dwell-filter.jsfx",
}
ROW = re.compile(r"^\|\s*src/([^|]+?\.jsfx)\s*\|\s*\d+\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*$")
KIND = re.compile(r"\((per [a-z]+(?: and [a-z]+)?|all targets)(?:\)|, )")
ENTRY = re.compile(r"\*\*((?:Drift|Ramp) [a-z][^*]*?)\*\*(?= `)")


def short(name):
    """The control's name with no parentheses at all: 'Drift period (0 = off)' -> 'Drift period'."""
    return re.sub(r"\s*\(.*\)\s*$", "", base(name)).strip()


def kinds():
    out = collections.defaultdict(dict)   # plugin file -> {short name: kind}
    for line in open(LIST, encoding="utf-8-sig"):
        m = ROW.match(line)
        if m:
            out[m[1]][short(m[2])] = KIND.search(m[3])[1]
    return out


def with_kind(bold, kind):
    if KIND.search(bold):
        return bold                              # already carries one
    m = re.match(r"^(.*?) \((.*)\)$", bold)
    return f"{m[1]} ({kind}, {m[2]})" if m else f"{bold} ({kind})"


def main():
    table = kinds()
    refusals, changes, plans = [], 0, {}
    for page, plugin in PAGES.items():
        path = os.path.join(ROOT, "docs", "plugins", page)
        if plugin not in table:
            continue                              # not in the list yet (e.g. Sweep Dwell before its rows)
        text = open(path, encoding="utf-8", newline="").read()

        def sub(m):
            nonlocal changes
            name = short(m[1])
            if name in ("Drift target", "Ramp target"):
                return m[0]                       # the selector itself: R25 names what is BEHIND it
            # One entry naming two controls ("Drift up amount / Drift down amount", Veil):
            # every part must have a row, and all must share the kind, or it is refused.
            parts = [short(p) for p in name.split(" / ")]
            missing = [p for p in parts if p not in table[plugin]]
            if missing:
                refusals.append(f"{page}: entry '**{m[1]}**' matches no {plugin} row for {missing}")
                return m[0]
            ks = {table[plugin][p] for p in parts}
            if len(ks) != 1:
                refusals.append(f"{page}: entry '**{m[1]}**' names controls of different kinds {sorted(ks)}")
                return m[0]
            new = with_kind(m[1], ks.pop())
            if new != m[1]:
                changes += 1
                print(f"{page}: **{m[1]}** -> **{new}**")
            return f"**{new}**"
        plans[path] = ENTRY.sub(sub, text)
    if refusals:
        print("\nREFUSED -- nothing written:")
        print("\n".join("  " + r for r in refusals))
        sys.exit(1)
    print(f"\n{changes} entr(ies) on {len(plans)} page(s)" + ("" if APPLY else " -- dry run, nothing written"))
    if not APPLY:
        return
    for p, t in plans.items():
        open(p, "w", encoding="utf-8", newline="").write(t)
    left = []
    for p in plans:
        for m in ENTRY.finditer(open(p, encoding="utf-8").read()):
            # The selectors are skipped on purpose; the first version counted them here and
            # reported a failure after a correct write (2026-09-12).
            if short(m[1]) in ("Drift target", "Ramp target"):
                continue
            if not KIND.search(m[1]):
                left.append(f"{os.path.basename(p)}: **{m[1]}**")
    print("verified: every Drift/Ramp entry on these pages carries its kind" if not left
          else "FAIL, entries still without a kind:\n  " + "\n  ".join(left))
    sys.exit(1 if left else 0)


if __name__ == "__main__":
    main()
