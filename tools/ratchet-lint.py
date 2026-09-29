#!/usr/bin/env python3
"""ratchet-lint: the gate's own limits may only tighten.

Every budget, threshold and debt ledger in this repo is a plain literal sitting
in the same file as the check it governs. `tests/test-seed-lint.sh` proves
the budgets CAN fire, by planting a violation. Nothing proved the SHIPPED value
had not been loosened to let a real violation through — and it is a two-line
edit:

  - bloat `core/AGENTS.md` past 8 000 bytes, raise `KERNEL_BUDGET` to 20 000,
    and the gate goes green. The kernel budget exists because "additions there
    need to earn ~2k-token-per-session rent" (CLAUDE.md); a literal in the
    linter is not a rent collector.
  - break the edition markers on a legal page, then add the 25 newly-failing
    entry IDs to `EDITION_DEBT`, and `legal lint: PASS — 70 carrying recorded
    edition debt`. That ledger's own comment says "a NEW entry may not join this
    list"; nothing enforced the sentence.

So the shipped values are recorded in tests/ratchets.json, the one home of the
registry: each limit's `registry` line names its source file and the direction
that counts as tightening, and `ratchets` holds its recorded value. A limit may
move toward stricter freely. Moving it toward looser fails this check until the
recorded value is changed too — which is a separate, conspicuous edit to a file
that exists for no other purpose, in a diff a reviewer reads.

That is the honest maximum. Nothing here can stop someone editing both files in
one commit; what it stops is loosening a limit SILENTLY, as part of a change
that appears to be about something else. The lock is a tripwire, not a vault.

Usage:
    python3 tools/ratchet-lint.py            # check (default)
    python3 tools/ratchet-lint.py --show     # print current vs recorded
    python3 tools/ratchet-lint.py --bless    # rewrite the recorded values from
                                             # current ones (deliberate, and it says so)

Adding a limit: add its `registry` line, then --bless. Retiring one: delete the
constant and its `registry` line, then --bless.

No third-party dependencies.
"""

from __future__ import annotations

import json
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOCK = ROOT / "tests" / "ratchets.json"

# Directions, as written in a `registry` line ("<direction> <source file>"):
#   "max" : the value is a CEILING; lowering it is tightening.
#   "min" : the value is a FLOOR;   raising it is tightening.
#   "set" : a debt ledger; removing members is tightening.
#   "map" : name -> ceiling, per key; lowering is tightening, new keys refused.
DIRECTIONS = ("max", "min", "set", "map")

_CACHE: dict[str, object] = {}


def load(rel: str):
    """Read a gate module's CURRENT SOURCE and execute it, without running its
    main() and without touching Python's bytecode cache.

    `importlib` validates a cached `.pyc` on (mtime, size). Both can match a
    stale cache: edit a constant from `8_000` to `7_600` (identical length) and
    restore it within the same second, and Python replays the old bytecode. A
    checker whose job is to report the SHIPPED values must never read a cache,
    so the source is compiled from text, every time.
    """
    if rel in _CACHE:
        return _CACHE[rel]
    path = ROOT / rel
    name = f"_ratchet_{path.stem.replace('-', '_')}"
    mod = types.ModuleType(name)      # not "__main__", so main() never runs
    mod.__file__ = str(path)
    # Registered BEFORE exec: `agent-lint.py` defines a @dataclass, and
    # dataclasses resolves `sys.modules[cls.__module__]` mid-decoration.
    sys.modules[name] = mod
    try:
        exec(compile(path.read_text(encoding="utf-8"), str(path), "exec"), mod.__dict__)
    finally:
        sys.modules.pop(name, None)
    _CACHE[rel] = mod
    return mod


def read_lock() -> dict:
    if not LOCK.exists():
        raise SystemExit(f"ratchet-lint: FAIL — {LOCK.relative_to(ROOT)} is missing; "
                         f"it is the only home of the recorded limits")
    return json.loads(LOCK.read_text(encoding="utf-8"))


def registry(lock: dict) -> dict:
    """name -> (source, direction), from the lock's `registry` lines."""
    out = {}
    for name, line in lock.get("registry", {}).items():
        kind, _, rel = line.partition(" ")
        if kind not in DIRECTIONS or not rel:
            raise SystemExit(
                f"ratchet-lint: {name}: registry line {line!r} is not "
                f"'<max|min|set|map> <source file>'. An unknown direction "
                f"matches no check, so the limit would pass unchecked.")
        out[name] = (rel, kind)
    return out


def current(reg: dict) -> dict:
    out = {}
    for name, (rel, kind) in reg.items():
        mod = load(rel)
        if not hasattr(mod, name):
            raise SystemExit(
                f"ratchet-lint: {rel} no longer defines {name}. A recorded limit "
                f"that vanished is a limit nobody is keeping; remove its registry "
                f"line deliberately, or restore it.")
        val = getattr(mod, name)
        if kind == "set":
            out[name] = sorted(val)
        elif kind == "map":
            out[name] = {k: v[0] for k, v in val.items()}
        else:
            out[name] = val
    return out


def check() -> int:
    lock = read_lock()
    reg = registry(lock)
    locked = lock.get("ratchets", {})
    now = current(reg)
    problems = [f"{n}: a recorded value with no registry line, so nobody keeps it; "
                f"add the line, or remove the value deliberately"
                for n in sorted(set(locked) - set(reg))]
    for name, (_rel, kind) in reg.items():
        if name not in locked:
            problems.append(f"{name}: not recorded in the lock — add it with --bless")
            continue
        was, is_ = locked[name], now[name]
        if kind == "max" and is_ > was:
            problems.append(
                f"{name} was LOOSENED: {was} -> {is_}. A ceiling may fall freely; "
                f"raising it is how a real violation gets waved through. If the "
                f"new value is right, record it in {LOCK.name} in the same "
                f"change, and say why in CHANGELOG.md.")
        elif kind == "min" and is_ < was:
            problems.append(
                f"{name} was LOOSENED: {was} -> {is_}. A floor may rise freely; "
                f"lowering it means the thing it measures got worse.")
        elif kind == "set":
            joined = sorted(set(is_) - set(was))
            if joined:
                problems.append(
                    f"{name} GREW by {len(joined)} entr(y/ies): {joined[:6]}"
                    f"{' ...' if len(joined) > 6 else ''}. This ledger records "
                    f"debt that predates its check; a NEW entry joining it means "
                    f"a fresh violation was filed as history instead of fixed.")
        elif kind == "map":
            for k, v in is_.items():
                if k not in was:
                    problems.append(f"{name}: new exemption {k!r} ({v}) — an "
                                    f"exemption is a debt, and a new one is a "
                                    f"decision, not a lint fix")
                elif v > was[k]:
                    problems.append(f"{name}[{k}] was LOOSENED: {was[k]} -> {v}")
    if problems:
        for p in problems:
            print(f"  !! {p}", file=sys.stderr)
        print(f"ratchet-lint: FAIL ({len(problems)} loosened limit(s))", file=sys.stderr)
        return 1
    # A lock LOOSER than the shipped value is unearned headroom: a later change
    # could spend it silently. So drift in either direction is a failure.
    drifted = [n for n in reg
               if json.dumps(locked.get(n), sort_keys=True)
               != json.dumps(now[n], sort_keys=True)]
    if drifted:
        for n in drifted:
            print(f"  !! {n}: the lock records {locked.get(n)!r} and the shipped "
                  f"value is {now[n]!r}. If the shipped value is the better one, "
                  f"re-bless so the lock says so; a lock looser than what ships "
                  f"is headroom nobody has to justify.", file=sys.stderr)
        print(f"ratchet-lint: FAIL ({len(drifted)} limit(s) out of step with "
              f"{LOCK.name} — run --bless to record them)", file=sys.stderr)
        return 1
    print(f"ratchet-lint: OK — {len(reg)} limits, none loosened, lock exact")
    return 0


def bless() -> int:
    lock = read_lock()
    reg = registry(lock)
    lock["ratchets"] = current(reg)
    LOCK.write_text(json.dumps(lock, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"ratchet-lint: recorded {len(reg)} limits into {LOCK.relative_to(ROOT)}")
    return 0


def show() -> int:
    lock = read_lock()
    reg = registry(lock)
    locked = lock.get("ratchets", {})
    now = current(reg)
    for name, (_r, kind) in reg.items():
        w, i = locked.get(name), now[name]
        if kind == "set":
            print(f"  {name:<24} recorded={len(w or [])} current={len(i)}")
        elif kind == "map":
            print(f"  {name:<24} recorded={w} current={i}")
        else:
            print(f"  {name:<24} recorded={w} current={i} ({kind})")
    return 0


def main() -> int:
    arg = sys.argv[1] if len(sys.argv) > 1 else "--check"
    if arg in ("-h", "--help"):
        print(__doc__); return 0
    if arg == "--bless":
        return bless()
    if arg == "--show":
        return show()
    if arg == "--check":
        return check()
    print(f"unknown option {arg} (try --help)", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
