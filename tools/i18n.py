"""Translation helper for Hold'em Drill (index.html, `const T={...}`).

    python tools/i18n.py check     list keys each language is missing compared to English (exit 1 if any)
    python tools/i18n.py extract   write i18n/new_en.js and i18n/new_fr.js with the keys missing somewhere
    python tools/i18n.py insert    insert every i18n/new_<code>.js at the end of its language block
                                   (keys placed last override older ones)

Rule: new features ship in English and French only; translations are batched later
(nightly task "holdem-drill-translations").
"""
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HTML = ROOT / "index.html"
OUT = ROOT / "i18n"


def t_bounds(s):
    a = s.index("const T={\n") + len("const T={\n")
    return a, s.index("\n};", a)


def blocks(s):
    """{code: (start, end)} of each language block 'code:{...}' inside T."""
    a, b = t_bounds(s)
    res, i = {}, a
    while i < b:
        m = re.compile(r"([a-z]{2,3}):\{").match(s, i)
        if not m:
            i += 1
            continue
        j = skip(s, m.end() - 1)  # index after the matching }
        res[m.group(1)] = (m.start(), j)
        i = j
    return res


def skip(s, i):
    """i points at an opening bracket; return the index just after its match (strings aware)."""
    depth, n = 0, len(s)
    while i < n:
        c = s[i]
        if c in "\"'":
            i = skip_str(s, i)
            continue
        if c == "`":
            i = skip_tpl(s, i)
            continue
        if c in "{[(":
            depth += 1
        elif c in "}])":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    raise ValueError("unbalanced")


def skip_str(s, i):
    q, i = s[i], i + 1
    while s[i] != q:
        i += 2 if s[i] == "\\" else 1
    return i + 1


def skip_tpl(s, i):
    i += 1
    while s[i] != "`":
        if s[i] == "\\":
            i += 2
            continue
        if s[i] == "$" and s[i + 1] == "{":
            i = skip(s, i + 1)
            continue
        i += 1
    return i + 1


def entries(s, start, end):
    """[(key, value_start, value_end)] of the top-level entries of a block."""
    i = s.index("{", start) + 1
    out = []
    while True:
        m = re.compile(r"[\s,]*([A-Za-z_]\w*)\s*:").match(s, i)
        if not m or m.end() >= end:
            return out
        j = m.end()
        while True:  # value runs to the next top-level comma or the block's closing brace
            c = s[j]
            if c in "\"'":
                j = skip_str(s, j)
            elif c == "`":
                j = skip_tpl(s, j)
            elif c in "{[(":
                j = skip(s, j)
            elif c == "," or j >= end - 1:
                break
            else:
                j += 1
        out.append((m.group(1), m.end(), j))
        i = j


def keys(s, code, bl):
    """Top-level keys, plus 'key.sub' for keys whose value is an object (e.g. prof.omc)."""
    out = set()
    for k, a, b in entries(s, *bl[code]):
        out.add(k)
        if s[a:b].lstrip().startswith("{"):
            out |= {f"{k}.{q}" for q, _, _ in entries(s, a, b)}
    return out


def missing(s):
    """Per language, the top-level keys to (re)translate. A key counts as missing when it is
    absent or when one of its sub-keys is absent; the whole object is then re-translated and
    inserted last, so it overrides the older, incomplete one."""
    bl = blocks(s)
    en = keys(s, "en", bl)
    res = {}
    for c in bl:
        if c == "en":
            continue
        gap = en - keys(s, c, bl)
        res[c] = sorted({k.split(".")[0] for k in gap})
    return bl, res


def cmd_check():
    s = HTML.read_text(encoding="utf-8")
    _, miss = missing(s)
    todo = {c: m for c, m in miss.items() if m}
    if not todo:
        print("All languages complete.")
        return 0
    allk = sorted({k for m in todo.values() for k in m})
    print(f"{len(todo)} languages missing {len(allk)} keys: {', '.join(allk)}")
    for c, m in todo.items():
        print(f"  {c}: {len(m)}")
    return 1


def cmd_extract():
    s = HTML.read_text(encoding="utf-8")
    bl, miss = missing(s)
    want = sorted({k for c, m in miss.items() if c != "fr" for k in m})
    if not want:
        print("Nothing to extract.")
        return 0
    OUT.mkdir(exist_ok=True)
    for code in ("en", "fr"):
        ent = {k: s[a:b] for k, a, b in entries(s, *bl[code])}
        body = ",\n  ".join(f"{k}:{ent[k].strip()}" for k in want if k in ent)
        (OUT / f"new_{code}.js").write_text(f"{code}:{{{body}}}\n", encoding="utf-8")
    print("Extracted:", ", ".join(want))
    print("Languages to translate:", ", ".join(c for c, m in miss.items() if m and c != "fr"))
    return 0


def cmd_insert():
    s = HTML.read_text(encoding="utf-8")
    done = []
    for f in sorted(OUT.glob("new_*.js")):
        code = f.stem[4:]
        if code in ("en", "fr"):
            continue
        bl = blocks(s)
        if code not in bl:
            print("no block for", code)
            continue
        txt = f.read_text(encoding="utf-8").strip().rstrip(",")
        assert txt.startswith(code + ":{") and txt.endswith("}"), code
        inner = txt[len(code) + 2:-1].strip().rstrip(",")
        close = bl[code][1] - 1  # the block's closing brace
        s = s[:close] + ",\n  " + inner + "\n" + s[close:]
        done.append(code)
    HTML.write_text(s, encoding="utf-8")
    print("Inserted:", ", ".join(done) or "nothing")
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    sys.exit({"check": cmd_check, "extract": cmd_extract, "insert": cmd_insert}[cmd]())
