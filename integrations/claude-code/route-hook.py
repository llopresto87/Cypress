#!/usr/bin/env python3
"""route-hook.py — a UserPromptSubmit hook that enforces progressive
discovery. Works in BOTH Claude Code and VS Code Copilot (Agent Hooks,
Preview): both read `.claude/settings.json` hooks, and both inject
context via the `hookSpecificOutput.additionalContext` output shape.

Installed to `.claude/route-hook.py` and wired in `.claude/settings.json`
under hooks.UserPromptSubmit, this runs on every prompt. The host passes
`{"prompt": "..."}` (plus `cwd`, `session_id`, `hook_event_name`) on
stdin; whatever `additionalContext` this returns is injected as a
prepended message before the model answers. So the route-first step
happens deterministically, not just when the model follows the kernel.

It locates the graph linter at `docs/graph/graph-lint.py` (the scaffold
the installer drops in) and attaches the router's suggested node set when
present. It never blocks: any error degrades to the mandate or silence,
so a missing/broken graph can't wedge the session. Exit 0 always.

Context injection REQUIRES JSON on stdout — plain text is not injected by
Copilot.
"""

import json
import subprocess
import sys
from pathlib import Path

# The same script may live at .claude/route-hook.py or
# .github/hooks/route-hook.py (different depths), so find the project
# root by walking up for the graph linter rather than assuming a depth.
#
# One candidate, and it is the one the installer writes. A candidate list is a
# claim about where the artifact is written, so a path no writer produces is
# not a fallback: the only file it could ever select is one this project did
# not put there. That is the unbounded reach `_is_plant_root` below bounds,
# arriving through the list instead of through the walk. A path is listed here
# only while something writes it, and is deleted in the change that retires
# the writer.
CANDIDATES = (Path("docs") / "graph" / "graph-lint.py",)


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


def find_lint():
    """Locate the plant's graph linter by walking up — but never out of the
    plant. The walk stops at the first directory that looks like a project
    root (`.git`, or the seed stamp `.cypress/`), that directory included.

    Unbounded, the walk ascended seven levels from BOTH the cwd and the script
    directory and executed the first graph-lint.py it found. A plant checked
    out inside another checkout therefore ran the ANCESTOR's linter on every
    prompt — a script the plant does not own, chosen by directory nesting.
    Reproduced during the 7.15.0 audit: from a git repo at `outer/child`, the
    walk resolved to `outer/docs/graph/graph-lint.py`.
    """
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
            if p.parent == p:
                break
            p = p.parent
    return None, Path.cwd()


LINT, ROOT = find_lint()

TRIVIAL = {"", "yes", "no", "ok", "thanks", "thank you", "go", "continue", "y", "n"}


def emit(text: str, event: str) -> None:
    if not text:
        return
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": event or "UserPromptSubmit",
            "additionalContext": text,
        }
    }))


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0
    prompt = (data.get("prompt") or data.get("initialPrompt") or "").strip()
    event = data.get("hook_event_name") or data.get("hookEventName") or "UserPromptSubmit"

    if prompt.lower() in TRIVIAL or len(prompt) < 8:
        return 0

    if LINT is None:
        emit("No knowledge graph found (docs/graph/). Use the canonical "
             "INSTALL_PROMPT.md; /initialize is the entry fork behind it \u2014 "
             "grow when there is source to scout, from-scratch when the "
             "repository is empty.", event)
        return 0

    mandate = (
        "PROGRESSIVE DISCOVERY IS REQUIRED. Before reading source or writing "
        "anything, open docs/graph/index.md, load only the nodes this task "
        "needs, and state which you loaded and which you deliberately "
        "skipped. Do not bulk-read to orient. Then classify the task tier "
        "out loud (kernel §0: T0 question / T1 trivial non-behavioral edit / "
        "T2 contained change — spec-covered, or small, local and reversible "
        "with a RED test and a recorded why / T3 everything else) — process "
        "follows the tier."
    )
    suggestion = ""
    try:
        out = subprocess.run(
            [sys.executable, str(LINT), "--plan", prompt],
            capture_output=True, text=True, timeout=15, cwd=str(ROOT),
        )
        if out.returncode == 0 and out.stdout.strip():
            body = out.stdout.split("\n", 2)[-1].strip()
            if body:
                suggestion = "\n\nRouter suggestion (a keyword heuristic — reason over it):\n" + body
    except Exception:
        pass

    emit(mandate + suggestion, event)
    return 0


if __name__ == "__main__":
    sys.exit(main())
