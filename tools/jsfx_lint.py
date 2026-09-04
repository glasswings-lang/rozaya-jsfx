import io, re, sys, collections
p = sys.argv[1] if len(sys.argv) > 1 else r"C:\git-src\rozaya-jsfx\src\spectral_vowel_morpher.jsfx"
raw = io.open(p, encoding="utf-8", newline="").read()

# strip comments the way the JSFX compiler does, then check paren balance
lines = raw.split("\n")
code = []
for ln in lines:
    code.append(re.sub(r"//.*$", "", ln))
code = "\n".join(code)
code = re.sub(r"/\*.*?\*/", "", code, flags=re.S)

# paren balance, per @section
sections = re.split(r"^(@\w+)", code, flags=re.M)
bal_total = 0
i = 1
while i < len(sections):
    name, body = sections[i], sections[i+1]
    b = body.count("(") - body.count(")")
    print("%-12s parens %+d" % (name, b))
    bal_total += abs(b)
    i += 2

# empty () BLOCKS -- the comment-only-branch trap.
#
# Only a BLOCK counts. `function foo()` and `foo()` are zero-argument
# declarations and calls: legal, ubiquitous, and flagging them made this check
# fire 22 times across four shipped, working plugins -- which teaches everyone
# to ignore the whole linter. An empty block is a "()" NOT preceded by an
# identifier; it follows ? : = ( , or ; instead. (Fixed 2026-08-31.)
for m in re.finditer(r"\(\s*\)", code):
    before = code[:m.start()].rstrip()
    if before and (before[-1].isalnum() or before[-1] == "_"):
        continue          # foo() / function foo() -- a call, not an empty block
    ln = code[:m.start()].count("\n") + 1
    print("EMPTY PARENS at line", ln, "->", lines[ln-1].strip()[:80])
    bal_total += 1

# case-variant identifier collisions (EEL2 folds case)
#
# Scan CODE ONLY. A slider declaration's label and enum options are TEXT,
# not identifiers. Scanning them fired this check on all 21 plugins, 3 to 24
# times each -- {Minutes,Beats} beside a parameter named `play`, and so on.
# Never once actionable, which is the tell: a check nobody can act on is a
# check everybody learns to skip, exactly as happened with the empty-parens
# check above. (Fixed 2026-09-04.)
code_ids = re.sub(r"(?m)^\s*slider\d+:.*$", "", code)
ids = re.findall(r"\b[A-Za-z_][A-Za-z0-9_]*\b", code_ids)
byfold = collections.defaultdict(set)
for t in ids:
    byfold[t.lower()].add(t)
for k, v in sorted(byfold.items()):
    if len(v) > 1:
        print("CASE COLLISION:", sorted(v))
        bal_total += 1

# slider DECLARATIONS must precede the first @section. A line like
# "slider41:0<0,5,1{...}>Name" sitting in @sample is a syntax error, and it is an
# easy one to cause: "the last line starting with 'slider'" also matches
# slider_show() and sliderN = ... down in the code.
_first_sec = None
for _i, _l in enumerate(code.split(chr(10))):
    if re.match(r"^@\w+", _l) and _first_sec is None:
        _first_sec = _i
    if _first_sec is not None and re.match(r"^slider\d+:", _l):
        print("SLIDER DECL AFTER @SECTION at line", _i + 1, "->", _l[:60])
        bal_total += 1

# scientific notation: EEL2 has none, 1e9 is a syntax error
for m in re.finditer(r"(?<![A-Za-z0-9_])[0-9]+(\.[0-9]+)?[eE][+-]?[0-9]+", code):
    print("SCI NOTATION:", m.group(0), "line", code[:m.start()].count(chr(10))+1)
    bal_total += 1

# reserved read-only system vars must never be assigned
for m in re.finditer(r"^\s*(tempo|play_state|play_position|beat_position|ts_num|ts_denom|samplesblock|num_ch|srate)\s*=", code, flags=re.M):
    print("ASSIGN TO RESERVED:", m.group(1), "line", code[:m.start()].count("\n")+1)
    bal_total += 1

print("PROBLEMS:", bal_total)
