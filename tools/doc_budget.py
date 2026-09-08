#!/usr/bin/env python3
"""Check the docs that get read every session against their line budgets.

Why this exists: CLAUDE.md was cut from 824 to 451 lines on 2026-09-03, from
1298 to 784 on 2026-09-06, and was back at 1043 on 2026-09-08 -- growing about
fifteen lines per commit and never once shrinking in between. Three separate
sessions tidied it and it grew back every time.

Tidying is not the fix. A ceiling is, and a ceiling only holds if something
checks it. The rules that have held in this repo are the ones a script
enforces; the ones written as prose have not.

Run it before committing any change under docs/ or to CLAUDE.md:

    python tools/doc_budget.py

Exits 1 if any file is over budget. That is not a nag -- it means stop and
delete something, or move it to the file where it belongs and leave a pointer.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# path -> (budget, what this file is for)
#
# The numbers were set at the 2026-09-08 split, from what each file actually
# contains plus modest headroom. Raising one to fit new text is the failure this
# script exists to stop.
#
# Only files a session is expected to READ are budgeted. docs/session-log.md is
# deliberately absent: it is append-only history and capping it would mean
# rewriting what happened. It gets rotation instead -- see the note at the
# bottom of this file.
BUDGETS = {
    "CLAUDE.md": (175, "loaded into every session; must stay skimmable"),
    "docs/current-state.md": (150, "describes NOW; delete what stopped being now"),
    "docs/working-practice.md": (550, "the incidents behind the rules"),
    "docs/jsfx-gotchas.md": (250, "read before editing any src/*.jsfx"),
    "docs/suite-consistency-plan.md": (1600, "the rules R1-R22, and nothing else"),
    "docs/backlog.md": (650, "what is owed; NOT a list of work to start"),
    "docs/plan-history.md": (700, "why the rules are what they are"),
    "docs/planned-features.md": (2500, "in-flight and deferred design work"),
}


def main() -> int:
    rows = []
    worst = 0
    for rel, (budget, purpose) in sorted(BUDGETS.items()):
        path = ROOT / rel
        if not path.exists():
            rows.append((rel, None, budget, purpose))
            worst = max(worst, 2)
            continue
        n = len(path.read_text(encoding="utf-8").splitlines())
        rows.append((rel, n, budget, purpose))
        if n > budget:
            worst = max(worst, 1)

    width = max(len(r[0]) for r in rows)
    for rel, n, budget, purpose in rows:
        if n is None:
            print(f"MISSING  {rel:<{width}}  (expected, budget {budget})")
            continue
        state = "OVER" if n > budget else "ok"
        slack = budget - n
        print(
            f"{state:<7}  {rel:<{width}}  {n:>5} / {budget:<5}"
            f"  {slack:+d}   {purpose}"
        )

    print()
    if worst == 0:
        print("All budgeted docs are within budget.")
        return 0
    if worst == 2:
        print("A budgeted doc is missing. Fix the path in tools/doc_budget.py.")
        return 1

    print("Over budget. Do NOT just raise the number -- that is how it grew last")
    print("time. Delete something, or move it to the file where it belongs and")
    print("leave a one-line pointer behind. One home per fact.")
    return 1


# On docs/session-log.md, which has no budget here:
#
# Append-only is correct for it -- you should not rewrite what happened. But
# append-only with no rotation is unbounded growth, and it went from 475 lines
# to 1998 in four days. When it gets unwieldy, move whole dated entries older
# than about two months into docs/log-archive/<year>-<month>.md and leave the
# topic index at the top of the live file pointing into the archives. That
# preserves the history exactly while keeping the file a session actually opens
# small enough to open.

if __name__ == "__main__":
    sys.exit(main())
