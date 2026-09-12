"""Slider names with their R25 kind taken off, so a tool matches a control by name before
and after the 2026-09-12 rename.

R25 (docs/suite-consistency-plan.md): a control behind a selector ends its name with
which kind it is -- "(per target)", "(all targets)", "(per slot and target)", or joined to
a unit already in parentheses: "Ramp start delay (per target, in ramp time units)".
Found before renaming: bridge_ui_test.py looked up "Drift movement" by exact name and
would have SKIPPED its checks silently afterwards.

    base("Ramp start delay (per target, in ramp time units)") -> "Ramp start delay (in ramp time units)"
    base("Drift movement (per target)")                       -> "Drift movement"
    base("Ramp engage (all targets)")                         -> "Ramp engage"
"""
import re

_KIND = r"(?:per [a-z]+(?: and [a-z]+)?|all [a-z]+)"


def base(name):
    name = re.sub(rf"\s*\({_KIND}\)", "", name)
    name = re.sub(rf"\({_KIND}, ", "(", name)
    return name.strip()


if __name__ == "__main__":
    cases = {
        "Ramp start delay (per target, in ramp time units)": "Ramp start delay (in ramp time units)",
        "Drift movement (per target)": "Drift movement",
        "Ramp engage (all targets)": "Ramp engage",
        "Drift up amount (per target, units match target)": "Drift up amount (units match target)",
        "Slot fade in (per slot and target)": "Slot fade in",
        "Drift target": "Drift target",
        "Pitch value (Hz / semitones / cents)": "Pitch value (Hz / semitones / cents)",
    }
    bad = [(k, base(k), v) for k, v in cases.items() if base(k) != v]
    print("ok" if not bad else f"FAIL {bad}")
