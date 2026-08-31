#!/usr/bin/env python3
"""graft-graph-engine: adopt the seed's current engine body into a plant script
while preserving the plant's PROJECT CONFIG.

install.sh drops the knowledge-graph scaffold (graph-lint.py, spec-lint.py,
_schema.md, index.md) ONLY IF ABSENT — so a plant that already has them keeps
its OLD engine across a graft, and the upgrade silently misses the linter.
A graft that leaves a plant on a stale graph engine is not a true upgrade.

This tool makes the engine a first-class, config-preserving fast-forward: it
takes the seed's current script as the body of record and re-injects the
plant's own top-level config assignments (ROOT_ID / KINDS / KIND_PREFIX for
graph-lint.py; TEST_GLOBS for spec-lint.py), so the plant gains every engine
improvement while keeping the identity it configured. A config knob the plant
predates (an older engine that never had it) adopts the seed's default.

A config knob is reconciled by shape, not blindly kept wholesale:
  * a SET literal the seed has EXTENDED (e.g. KINDS gaining the machinery kinds
    protocol/skill/agent/method) is UNIONED — the plant's own members AND the
    seed's new members both survive; keeping the plant's set wholesale would
    drop the seed's new kinds and every newly-installed machinery node would
    fail graph-lint with `kind not in KINDS`;
  * every other knob (a scalar identity like ROOT_ID, a dict, a list like
    TEST_GLOBS) is the plant's to keep wholesale — that is its configured
    identity, which the seed must not touch.

If the PLANT engine is a strict superset of the seed's (it already contains
every non-config engine line), the tool reports KEEP-PLANT and changes nothing
— the plant is ahead and its extra capability is a harvest candidate.

Usage:
  graft-graph-engine.py <plant-file> <seed-file> [--preserve VAR1,VAR2,...]
Defaults --preserve to ROOT_ID,KINDS,KIND_PREFIX. Backs the plant file up
(.bak-<ts>) before writing. Dependency-free. Exit 0 on success/no-op, 2 on refuse.
"""
import re
import shutil
import sys
import time
from pathlib import Path

DEFAULT_PRESERVE = ("ROOT_ID", "KINDS", "KIND_PREFIX")


def grab_assignment(text: str, name: str):
    """Return the full source of a top-level `NAME = <value>` assignment,
    consuming continuation lines until brackets balance (handles multi-line
    dict/set/list literals). None if not found."""
    m = re.search(rf"^{name}\s*=.*$", text, re.M)
    if not m:
        return None
    start = m.start()
    lines = text[start:].splitlines(keepends=True)
    buf, depth = "", 0
    for ln in lines:
        buf += ln
        depth += ln.count("{") + ln.count("[") + ln.count("(")
        depth -= ln.count("}") + ln.count("]") + ln.count(")")
        if depth <= 0:
            break
    return buf.rstrip("\n")


def strip_inline_comment(line: str) -> str:
    """Drop a trailing `#` comment not inside a string literal, and rstrip.
    Good enough for engine source comparison (no line-continuation strings)."""
    q = None
    for i, c in enumerate(line):
        if q:
            if c == q:
                q = None
        elif c in "'\"":
            q = c
        elif c == "#":
            return line[:i].rstrip()
    return line.rstrip()


def engine_body(text: str, preserve) -> set:
    """The set of code lines with every preserved assignment, all comments
    (full and inline), and blank lines removed — the comparable 'engine'."""
    t = text
    for name in preserve:
        a = grab_assignment(t, name)
        if a:
            t = t.replace(a, "", 1)
    out = set()
    for l in t.splitlines():
        s = strip_inline_comment(l)
        if s.strip() and not s.lstrip().startswith("#"):
            out.add(s)
    return out


def _rhs(asg: str) -> str:
    """The right-hand side of an assignment source (everything after the first
    '='), whitespace-stripped."""
    return asg.split("=", 1)[1].strip()


def is_set_literal(rhs: str) -> bool:
    """True for a non-empty set literal `{...}` (no top-level ':'). `{}` is an
    empty dict, not a set, so it returns False."""
    if not (rhs.startswith("{") and rhs.endswith("}")):
        return False
    inner = rhs[1:-1]
    if not inner.strip():
        return False
    without_strings = re.sub(r"""(['"]).*?\1""", "", inner)
    return ":" not in without_strings


def set_members(rhs: str) -> list:
    """The quoted string members of a set literal, in source order."""
    return re.findall(r"""['"]([^'"]*)['"]""", rhs[1:-1])


def union_set(plant_rhs: str, seed_rhs: str) -> str:
    """Union of two set literals as a single-line literal: the seed's members
    first (in seed order), then any plant-only members (in plant order)."""
    seen, out = set(), []
    for m in set_members(seed_rhs) + set_members(plant_rhs):
        if m not in seen:
            seen.add(m)
            out.append(m)
    return "{" + ", ".join(f'"{m}"' for m in out) + "}"


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    preserve = DEFAULT_PRESERVE
    for a in sys.argv[1:]:
        if a.startswith("--preserve="):
            preserve = tuple(x for x in a.split("=", 1)[1].split(",") if x)
        elif a == "--preserve" and len(args) >= 3:
            preserve = tuple(x for x in args[2].split(",") if x)
            args = args[:2]
    if len(args) < 2:
        print(__doc__)
        return 2
    plant_p, seed_p = Path(args[0]), Path(args[1])
    plant, seed = plant_p.read_text(), seed_p.read_text()

    # superset check: does the plant already contain every seed engine line?
    seed_lines = engine_body(seed, preserve)
    plant_lines = engine_body(plant, preserve)
    if seed_lines and seed_lines <= plant_lines and len(plant_lines) > len(seed_lines):
        print("  KEEP-PLANT: plant engine is a superset of the seed's "
              "(ahead) — unchanged; raise as a harvest candidate")
        return 0

    merged = seed
    for name in preserve:
        p_asg, s_asg = grab_assignment(plant, name), grab_assignment(seed, name)
        if s_asg is None:
            print(f"  ! REFUSE: seed engine lacks config '{name}'")
            return 2
        if p_asg is None:
            print(f"  adopted seed default {name} (plant predated it)")
            continue
        p_rhs, s_rhs = _rhs(p_asg), _rhs(s_asg)
        if is_set_literal(p_rhs) and is_set_literal(s_rhs):
            # additive-vocabulary knob (e.g. KINDS): union so the seed's new
            # members AND the plant's own members both survive.
            new_asg = f"{name} = {union_set(p_rhs, s_rhs)}"
            merged = merged.replace(s_asg, new_asg, 1)
            seed_new = [m for m in set_members(s_rhs) if m not in set_members(p_rhs)]
            plant_own = [m for m in set_members(p_rhs) if m not in set_members(s_rhs)]
            if seed_new or plant_own:
                print(f"  unioned {name}: added seed {seed_new or '[]'}, kept plant {plant_own or '[]'}")
        else:
            merged = merged.replace(s_asg, p_asg, 1)
            if p_asg.strip() != s_asg.strip():
                print(f"  kept plant {name}")

    if merged == plant:
        print("  = already current (engine + config identical) — no change")
        return 0
    bak = f"{plant_p}.bak-{time.strftime('%Y%m%d-%H%M%S')}"
    shutil.copy2(plant_p, bak)
    plant_p.write_text(merged)
    print(f"  engine adopted from seed, plant config preserved; backup {Path(bak).name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
