#!/usr/bin/env python3
"""status-hook.py — a SessionStart hook that surfaces the plant's lifecycle
status register ONCE per session. The sibling of route-hook.py (which runs on
every prompt): this one runs when a session starts and injects the output of
`status-register.py --summary` — how many items are open / hotfix / deferred
and the oldest of them — so standing debt is in front of the model before it
plans, deterministically, without a line in any brief or a step the model must
remember.

Installed to `.claude/status-hook.py` and wired in `.claude/settings.json`
under hooks.SessionStart. The host passes `{"session_id", "hook_event_name",
"source"}` on stdin; whatever `additionalContext` this returns is injected as a
prepended message. Subagents receive nothing: hooks do not cross the spawn
boundary, and a bounded worker reads one node's frontmatter when it needs one
item's status.

It never blocks: a missing register, a missing graph, a timeout, or a broken
tool degrades to silence. Exit 0 always. Context injection REQUIRES JSON on
stdout — plain text is not injected by Copilot.
"""

import json
import subprocess
import sys
from pathlib import Path

CANDIDATES = (Path("docs") / "graph" / "status-register.py", Path("tools") / "status-register.py")


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


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        data = {}
    event = data.get("hook_event_name") or data.get("hookEventName") or "SessionStart"
    register, root = find_register()
    if register is None:
        return 0
    try:
        out = subprocess.run(
            [sys.executable, str(register), "--summary", "--root", str(root / "docs" / "graph")],
            capture_output=True, text=True, timeout=15, cwd=str(root),
        )
    except Exception:
        return 0
    summary = (out.stdout or "").strip()
    if out.returncode not in (0, 1) or not summary:
        return 0
    emit("Status register (lifecycle debt in this plant, from frontmatter — "
         "read it, do not re-infer it): " + summary, event)
    return 0


if __name__ == "__main__":
    sys.exit(main())
