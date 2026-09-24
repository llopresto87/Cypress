#!/usr/bin/env python3
"""status-hook.py — a SessionStart hook that surfaces the plant's lifecycle
status register ONCE per session, and resets the session ledger that its
sibling route-hook.py keeps. The sibling runs on every prompt: this one runs
when a session starts and injects the output of `status-register.py --summary`
— how many items are open / hotfix / deferred and the oldest of them — so
standing debt is in front of the model before it plans, deterministically,
without a line in any brief or a step the model must remember.

Installed to `.claude/status-hook.py` and wired in `.claude/settings.json`
under hooks.SessionStart. The host passes `{"session_id", "hook_event_name",
"source"}` on stdin; whatever `additionalContext` this returns is injected as a
prepended message. Subagents receive nothing: hooks do not cross the spawn
boundary, and a bounded worker reads one node's frontmatter when it needs one
item's status.

The reset runs on every source (startup, resume, clear, compact, fork, and
anything else), because each one can leave the model without context the
ledger says it was shown. The ledger has one owner: `reset_ledger` is loaded
from the sibling route-hook.py, and this file carries no copy of its path
rule or session-id pattern (SPEC-0003).

It never blocks: a missing register, a missing graph, a timeout, or a broken
tool degrades to silence, and a reset that cannot run, or stdin nested past the
JSON parser, costs one stderr line. Exit 0 always. Context injection REQUIRES
JSON on stdout — plain text is not injected by Copilot.
"""

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

CANDIDATES = (Path("docs") / "graph" / "status-register.py", Path("tools") / "status-register.py")


# --- canonical plant-root boundary ---
def _is_plant_root(p) -> bool:
    """True where an upward walk must stop, that directory INCLUDED.

    Unbounded, these walks ascend seven or eight levels from both the cwd and
    the script's own directory and take the first artifact they find. A plant
    checked out inside another checkout therefore used the ANCESTOR's — a file
    the plant does not own, chosen by directory nesting. Reproduced from a git
    repo at `outer/sub/child` with no roster of its own: `agent-lint.py --route`
    returned the ancestor repository's agent at HIGH confidence, score 36, and
    `--lint` printed OK over that foreign roster.

    Callers test their candidate BEFORE calling this, so a plant whose artifact
    sits at its own repo root is still found; only the step BEYOND the root is
    denied.
    """
    return (p / ".git").exists() or (p / ".cypress").is_dir()
# --- end canonical plant-root boundary ---


def find_register():
    starts = [Path.cwd(), Path(__file__).resolve().parent]
    seen = set()
    for start in starts:
        p = start
        for _ in range(7):
            if p in seen:
                break
            seen.add(p)
            for rel in CANDIDATES:
                if (p / rel).exists():
                    return p / rel, p
            if _is_plant_root(p):
                break
            p = p.parent
    return None, Path.cwd()


def emit(text: str, event: str) -> None:
    if not text:
        return
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": event or "SessionStart",
            "additionalContext": text,
        }
    }))


def reset_session_ledger(data: dict) -> None:
    """Reset this session's ledger through the sibling route-hook.py, its one
    owner. Any failure, the sibling missing included, is one stderr line and
    leaves the summary to run. That line carries the sibling's LedgerUnusable
    message, which is safe as it is, and only the type name of anything else,
    whose text can hold a file name and so the raw session id."""
    route_hook = None
    try:
        sibling = Path(__file__).resolve().with_name("route-hook.py")
        spec = importlib.util.spec_from_file_location("cypress_route_hook", sibling)
        if spec is None or spec.loader is None:
            raise ImportError(f"cannot load {sibling.name}")
        route_hook = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(route_hook)
        route_hook.reset_ledger(data.get("session_id"), data.get("source"))
    except Exception as e:                        # noqa: BLE001 — a reset never blocks the session
        safe = route_hook is not None and isinstance(e, getattr(route_hook, "LedgerUnusable", ()))
        why = f"{type(e).__name__}: {e}" if safe else type(e).__name__
        print(f"status-hook: session ledger not reset ({why})", file=sys.stderr)


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except RecursionError:                        # nested past the parser: no session to reset
        print("status-hook: stdin nested past the JSON parser's limit; no reset", file=sys.stderr)
        data = {}
    except Exception:                             # noqa: BLE001 — not JSON, empty stdin included: silent
        data = {}
    if not isinstance(data, dict):
        data = {}
    event = data.get("hook_event_name") or data.get("hookEventName") or "SessionStart"
    reset_session_ledger(data)
    register, root = find_register()
    if register is None:
        return 0
    try:
        out = subprocess.run(
            [sys.executable, str(register), "--summary", "--root", str(root / "docs" / "graph")],
            capture_output=True, text=True, timeout=15, cwd=str(root),
        )
    except Exception:                             # noqa: BLE001 — a broken register is silence,
        return 0                                  # output that does not decode included
    summary = (out.stdout or "").strip()
    if out.returncode not in (0, 1) or not summary:
        return 0
    emit("Status register (lifecycle debt in this plant, from frontmatter — "
         "read it, do not re-infer it): " + summary, event)
    return 0


if __name__ == "__main__":
    sys.exit(main())
