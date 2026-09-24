#!/usr/bin/env python3
"""ratchet-lint: the gate's own limits may only tighten.

Every budget, threshold and debt ledger in this repo is a plain literal sitting
in the same file as the check it governs. `tests/test-seed-budgets.sh` proves
each one CAN fire, by overriding it in memory. Nothing proved the SHIPPED value
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

So the shipped values are recorded HERE, in a file whose only job is to hold
them, and each one declares which direction counts as tightening. A limit may
move toward stricter freely. Moving it toward looser fails this check until the
recorded value is changed too — which is a separate, conspicuous edit to a file
that exists for no other purpose, in a diff a reviewer reads.

That is the honest maximum. Nothing here can stop someone editing both files in
one commit; what it stops is loosening a limit SILENTLY, as part of a change
that appears to be about something else. The lock is a tripwire, not a vault.

Usage:
    python3 tools/ratchet-lint.py            # check (default)
    python3 tools/ratchet-lint.py --show     # print current vs recorded
    python3 tools/ratchet-lint.py --bless    # rewrite the lock from current
                                             # values (deliberate, and it says so)

No third-party dependencies.
"""

from __future__ import annotations

import importlib.util
import json
import types
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOCK = ROOT / "tests" / "ratchets.json"

# name -> (source file, attribute, direction)
#   "max" : the value is a CEILING; lowering it is tightening.
#   "min" : the value is a FLOOR;   raising it is tightening.
#   "set" : a debt ledger; removing members is tightening.
#   "map" : name -> ceiling, per key; lowering is tightening, new keys refused.
RATCHETS = {
    "KERNEL_BUDGET":          ("tests/seed-lint.py", "KERNEL_BUDGET", "max"),
    "MACHINERY_BODY_CEILING": ("tests/seed-lint.py", "MACHINERY_BODY_CEILING", "max"),
    "LIFECYCLE_BODY_CEILING": ("tests/seed-lint.py", "LIFECYCLE_BODY_CEILING", "max"),
    "LIFECYCLE_NODES":        ("tests/seed-lint.py", "LIFECYCLE_NODES", "set"),
    "EAGER_BUDGET":           ("tests/seed-lint.py", "EAGER_BUDGET", "max"),
    "EAGER_EXEMPTIONS":       ("tests/seed-lint.py", "EAGER_EXEMPTIONS", "map"),
    "CHARTER_VOCAB_DEBT":     ("tests/seed-lint.py", "CHARTER_VOCAB_DEBT", "max"),
    "SPEC_UNCOVERED_BUDGET":  ("tests/seed-lint.py", "SPEC_UNCOVERED_BUDGET", "max"),
    "SPEC_ROW_UNBOUND_BUDGET": ("tests/seed-lint.py", "SPEC_ROW_UNBOUND_BUDGET", "max"),
    "PREVENTS_OVERLAP_CEILING": ("tests/seed-lint.py", "PREVENTS_OVERLAP_CEILING", "max"),
    "PREVENTS_RESTATEMENT_CEILING": ("tests/seed-lint.py", "PREVENTS_RESTATEMENT_CEILING", "max"),
    "FRONTMATTER_CEILING": ("tests/seed-lint.py", "FRONTMATTER_CEILING", "max"),
    # SPEC-0004, the front door: the first-screen line budgets (each also held
    # under its spec cap by seed-lint), the README catalog ceiling, the limits
    # section's floors, the definition-overlap ceiling, and the pending ledger.
    "FIRST_HEADING_MAX_LINE": ("tests/seed-lint.py", "FIRST_HEADING_MAX_LINE", "max"),
    "FIRST_SCREEN_MAX_LINES": ("tests/seed-lint.py", "FIRST_SCREEN_MAX_LINES", "max"),
    "FIRST_COMMAND_LINE":     ("tests/seed-lint.py", "FIRST_COMMAND_LINE", "max"),
    "README_CATALOG_CEILING": ("tests/seed-lint.py", "README_CATALOG_CEILING", "max"),
    "LIMITS_MIN_REQUESTED":   ("tests/seed-lint.py", "LIMITS_MIN_REQUESTED", "min"),
    "LIMITS_MIN_UNMEASURED":  ("tests/seed-lint.py", "LIMITS_MIN_UNMEASURED", "min"),
    "DEFINITION_OVERLAP_CEILING": ("tests/seed-lint.py", "DEFINITION_OVERLAP_CEILING", "max"),
    "FRONT_DOOR_PENDING":     ("tests/seed-lint.py", "FRONT_DOOR_PENDING", "set"),
    "INLINE_ASSERTION_DEBT": ("tests/check-coverage-binder.py", "INLINE_ASSERTION_DEBT", "max"),
    "EDITION_DEBT":           ("tests/legal-lint.py", "EDITION_DEBT", "set"),
    "PARAPHRASE_MAX_OVERLAP": ("integrations/claude-code/agent-lint.py",
                               "PARAPHRASE_MAX_OVERLAP", "max"),
    "NEAR_DUPLICATE_CEILING": ("integrations/claude-code/agent-lint.py",
                               "NEAR_DUPLICATE_CEILING", "max"),
    "GRANDFATHERED_NEAR_DUPLICATES": ("integrations/claude-code/agent-lint.py",
                                      "GRANDFATHERED_NEAR_DUPLICATES", "set"),
    "CONFIDENT_WRONG_BUDGET": ("integrations/claude-code/agent-lint.py",
                               "CONFIDENT_WRONG_BUDGET", "max"),
    "ADVERSARIAL_CONFIDENT_WRONG_BUDGET": ("integrations/claude-code/agent-lint.py",
                                           "ADVERSARIAL_CONFIDENT_WRONG_BUDGET", "max"),
    "PARAPHRASE_FLOOR":       ("integrations/claude-code/agent-lint.py",
                               "PARAPHRASE_FLOOR", "min"),
    "PARAPHRASE_MIN_ROWS":    ("integrations/claude-code/agent-lint.py",
                               "PARAPHRASE_MIN_ROWS", "min"),
    "ADVERSARIAL_MIN_ROWS":   ("integrations/claude-code/agent-lint.py",
                               "ADVERSARIAL_MIN_ROWS", "min"),
    "EVAL_THRESHOLD":         ("integrations/claude-code/agent-lint.py",
                               "EVAL_THRESHOLD", "min"),
}

_CACHE: dict[str, object] = {}


def load(rel: str):
    """Read a gate module's CURRENT SOURCE and execute it, without running its
    main() and without touching Python's bytecode cache.

    `importlib` validates a cached `.pyc` on (mtime, size). Both can match a
    stale cache: edit a constant from `8_000` to `7_600` — identical length —
    and restore it within the same second, and Python happily replays the old
    bytecode. This tool caught itself doing exactly that, reporting
    `current=7600` while the file on disk plainly read `8_000`.

    For most importers that is a curiosity. For a checker whose entire job is to
    report what the SHIPPED values are, reading a cache is the one thing it must
    never do: it would report a loosened limit as unchanged, which is worse than
    having no check at all. So the source is compiled from text, every time.
    """
    if rel in _CACHE:
        return _CACHE[rel]
    path = ROOT / rel
    name = f"_ratchet_{path.stem.replace('-', '_')}"
    mod = types.ModuleType(name)      # not "__main__", so main() never runs
    mod.__file__ = str(path)
    # Registered BEFORE exec: `agent-lint.py` defines a @dataclass, and
    # dataclasses resolves `sys.modules[cls.__module__]` mid-decoration. An
    # unregistered module makes that lookup return None and the import dies.
    sys.modules[name] = mod
    try:
        exec(compile(path.read_text(encoding="utf-8"), str(path), "exec"), mod.__dict__)
    finally:
        sys.modules.pop(name, None)
    _CACHE[rel] = mod
    return mod


def current() -> dict:
    out = {}
    for name, (rel, attr, kind) in RATCHETS.items():
        mod = load(rel)
        if not hasattr(mod, attr):
            raise SystemExit(
                f"ratchet-lint: {rel} no longer defines {attr}. A recorded limit "
                f"that vanished is a limit nobody is keeping; remove it from "
                f"RATCHETS deliberately, or restore it.")
        val = getattr(mod, attr)
        if kind == "set":
            out[name] = sorted(val)
        elif kind == "map":
            out[name] = {k: v[0] for k, v in val.items()}
        else:
            out[name] = val
    return out


def check() -> int:
    if not LOCK.exists():
        print(f"ratchet-lint: FAIL — {LOCK.relative_to(ROOT)} is missing. The "
              f"recorded limits are the only thing standing between a real "
              f"violation and a two-line edit; run --bless to create it, "
              f"deliberately.", file=sys.stderr)
        return 1
    locked = json.loads(LOCK.read_text(encoding="utf-8"))["ratchets"]
    now = current()
    problems = []
    # A limit in the LOCK but no longer in RATCHETS is the symmetric hole to
    # `current()`'s "the attribute vanished" check, and it was open: deleting
    # one line from RATCHETS stopped guarding that limit entirely, and the tool
    # reported "OK — 14 limits, none loosened" while KERNEL_BUDGET sat at
    # 20 000. The only signal was a count nothing asserted. Loosening a limit
    # SILENTLY, as part of a change that appears to be about something else, is
    # the one thing this tool exists to stop.
    for name in sorted(set(locked) - set(RATCHETS)):
        problems.append(
            f"{name}: recorded in {LOCK.name} but no longer registered in "
            f"RATCHETS. A recorded limit that is no longer registered is a "
            f"limit nobody is keeping — restore the row, or remove it from the "
            f"lock deliberately and say why in CHANGELOG.md.")
    locked_dirs = json.loads(LOCK.read_text(encoding="utf-8")).get("directions", {})
    for name, (_rel, _attr, kind) in RATCHETS.items():
        if kind not in ("max", "min", "set", "map"):
            problems.append(
                f"{name}: direction {kind!r} is not one of max/min/set/map. An "
                f"unrecognised direction matches no branch below, so NO check "
                f"runs on this limit and the tool still reports OK.")
            continue
        was_dir = locked_dirs.get(name)
        if was_dir is None:
            problems.append(
                f"{name}: the lock records no direction for it — re-bless so the "
                f"direction is pinned alongside the value.")
        elif was_dir != kind:
            problems.append(
                f"{name}: direction CHANGED {was_dir!r} -> {kind!r} without the "
                f"lock moving. Flipping a ceiling into a floor inverts what "
                f"'loosened' means, so a raise reads as a tightening. If the "
                f"change is right, record it in {LOCK.name} in the same edit.")
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
    # A lock that is LOOSER than the shipped value is unearned headroom, and it
    # used to be reported as a congratulation. Raising `KERNEL_BUDGET` in
    # ratchets.json alone printed `OK — none loosened; 1 tightened since the
    # lock` — the exact inverse of what happened — and a later, unrelated-looking
    # change raising the source to match was then completely silent. Two steps,
    # each green, and the limit tripled. So drift in either direction is a named
    # condition now: this is `seed-lint`'s own "the debt SHRANK and the record
    # did not" idiom, which exists three checks away for the same reason.
    drifted = [n for n in RATCHETS
               if json.dumps(locked.get(n), sort_keys=True)
               != json.dumps(now[n], sort_keys=True)]
    if drifted:
        for n in drifted:
            print(f"  !! {n}: the lock records {locked.get(n)!r} and the shipped "
                  f"value is {now[n]!r}. If the shipped value is the better one, "
                  f"re-bless so the lock says so; a lock looser than what ships "
                  f"is headroom nobody has to justify, and the next change can "
                  f"spend it silently.", file=sys.stderr)
        print(f"ratchet-lint: FAIL ({len(drifted)} limit(s) out of step with "
              f"{LOCK.name} — run --bless to record them)", file=sys.stderr)
        return 1
    print(f"ratchet-lint: OK — {len(RATCHETS)} limits, none loosened, lock exact")
    return 0


def bless() -> int:
    LOCK.write_text(json.dumps(
        {"_comment": "Recorded limits. A ceiling may fall and a floor may rise "
                     "without touching this file; loosening either requires "
                     "editing it here, on purpose, in a diff someone reads. "
                     "Regenerate with: python3 tools/ratchet-lint.py --bless",
         "ratchets": current(),
         # The direction is recorded too. Without it `check()` read `kind`
         # straight out of RATCHETS and trusted it: flipping one limit's "max"
         # to "min" — a single word, in one file, lock untouched — reported
         # `OK — none loosened; 1 tightened` while the budget tripled. A typo was
         # worse: "mx" matched no branch in the if/elif chain, so NO check ran at
         # all and the same clean OK printed. That is this tool's own worked
         # example of the thing it exists to prevent.
         "directions": {name: kind for name, (_r, _a, kind) in RATCHETS.items()}},
        indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"ratchet-lint: recorded {len(RATCHETS)} limits into {LOCK.relative_to(ROOT)}")
    return 0


def show() -> int:
    locked = json.loads(LOCK.read_text(encoding="utf-8"))["ratchets"] if LOCK.exists() else {}
    now = current()
    for name, (_r, _a, kind) in RATCHETS.items():
        w, i = locked.get(name), now[name]
        if kind in ("set",):
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
