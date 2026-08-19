# -*- coding: utf-8 -*-
"""For each plugin: which values are DERIVED from a @serialize-restored bank
but computed in @slider? Those are the ones a restore leaves stale, because
@slider and @serialize have no guaranteed relative order."""
import io, re, glob, os

for path in sorted(glob.glob(r"C:\git-src\rozaya-jsfx\src\*.jsfx")):
    raw = io.open(path, encoding="utf-8", errors="replace", newline="").read()
    code = re.sub(r"//.*$", "", raw, flags=re.M)
    secs, cur = {}, None
    for ln in code.split("\n"):
        m = re.match(r"^@(\w+)", ln)
        if m:
            cur = m.group(1); secs.setdefault(cur, [])
        elif cur:
            secs[cur].append(ln)
    if "serialize" not in secs:
        continue
    # bank arrays that @serialize restores
    banks = set(re.findall(r"file_mem\(\s*0\s*,\s*([A-Za-z_]\w*)", "\n".join(secs["serialize"])))
    banks |= set(re.findall(r"file_var\(\s*0\s*,\s*([A-Za-z_]\w*)", "\n".join(secs["serialize"])))
    if not banks:
        continue
    hits = []
    for ln in secs.get("slider", []):
        m = re.match(r"\s*([A-Za-z_]\w*)\s*\[?[^=]*\]?\s*=\s*(.+)$", ln)
        if not m:
            continue
        lhs, rhs = m.group(1), m.group(2)
        if lhs in banks or lhs.startswith("slider"):
            continue            # writing INTO a bank, or into a slider: fine
        used = [b for b in banks if re.search(r"\b" + b + r"\s*\[", rhs)]
        if used:
            hits.append((lhs, sorted(set(used))))
    if hits:
        print("%-34s %s" % (os.path.basename(path), "has @block" if "block" in secs else "NO @block"))
        seen = set()
        for lhs, used in hits:
            k = (lhs, tuple(used))
            if k in seen:
                continue
            seen.add(k)
            print("      %-24s <- %s" % (lhs, ", ".join(used)))
