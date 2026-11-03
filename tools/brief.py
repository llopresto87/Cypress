#!/usr/bin/env python3
"""brief.py — compose a delegation brief from the plant's canonical templates.

The caller supplies only what is task-specific: the role, the spawn id, the
exact task line, the routing evidence, the effort and the task part. The two
canonical blocks of templates/prompts/graph-session-bootstrap.md and the
HANDBACK block of templates/prompts/handback-payload.md are copied byte for
byte, with their slots filled, so a brief carries them verbatim by
construction and neither the caller nor the worker reads the templates.
`--charter` prepends the role's charter body (frontmatter dropped) for a host
whose spawn has no agent type to carry it (Prime Agent).

  python3 docs/graph/brief.py --role tester --spawn-id orchestrator.3.tester.1 \
      --task "<exact task line>" --route "<agent-lint line or rationale>" \
      [--effort "<label (row n: reason)>"] [--charter] --part FILE|- [--out PATH]

Exit 0 and the brief on stdout; exit 2 with one stderr line on an unknown role,
a missing template, or a slot left unfilled. With `--out PATH` the brief is
written to PATH and stdout carries only a three-line spawn prompt that points
at it: where the spawn prompt stays in the caller's context, the brief then
never enters it, and the file is the brief's record beside the handbacks.
"""

import argparse
import re
import sys
from pathlib import Path

GRAPH = Path(__file__).resolve().parent
BOOTSTRAP = GRAPH / "templates" / "prompts" / "graph-session-bootstrap.md"
HANDBACK = GRAPH / "templates" / "prompts" / "handback-payload.md"
AGENTS = GRAPH / "agents"


def fenced(path: Path, head: str) -> str:
    m = re.search(r"```\n(" + re.escape(head) + r".*?)```", path.read_text(encoding="utf-8"), re.S)
    if not m:
        raise SystemExit(f"brief: no fenced {head} block in {path}")
    return m.group(1)


def charter(role: str) -> str:
    for p in sorted(AGENTS.glob("*.md")):
        text = p.read_text(encoding="utf-8")
        if text.startswith("---") and re.search(rf"^name:\s*{re.escape(role)}\s*$", text.split("---", 2)[1], re.M):
            return text.split("---", 2)[2].strip()
    raise SystemExit(f"brief: no agent charter named {role!r} in {AGENTS}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--role", required=True)
    ap.add_argument("--spawn-id", required=True)
    ap.add_argument("--task", required=True, help="the exact task line the worker routes")
    ap.add_argument("--route", required=True, help="the agent-lint --route line, or the override rationale")
    ap.add_argument("--effort", default="")
    ap.add_argument("--charter", action="store_true", help="prepend the role's charter body")
    ap.add_argument("--part", required=True, help="file holding the task part, or - for stdin")
    ap.add_argument("--out", default="", help="write the brief here and print only a pointer prompt")
    a = ap.parse_args()
    try:
        body = charter(a.role)
        part = sys.stdin.read() if a.part == "-" else Path(a.part).read_text(encoding="utf-8")
        graph = fenced(BOOTSTRAP, "GRAPH DISCIPLINE").replace("{{exact delegated task}}", a.task)
        comp = fenced(BOOTSTRAP, "COMPANION")
        comp = re.sub(r"\{\{caller-minted.*?\}\}", a.spawn_id, comp, flags=re.S)
        comp = re.sub(r"\{\{paste the line.*?\}\}", a.route, comp, flags=re.S).replace("{{you}}", a.role)
        payload = fenced(HANDBACK, "HANDBACK")
    except SystemExit as e:
        print(e, file=sys.stderr)
        return 2
    if "{{" in graph + comp:
        print("brief: a bootstrap slot this tool does not fill is left in the template", file=sys.stderr)
        return 2
    out = [f"You are `{a.role}`, a CYPRESS specialist. spawn_id: {a.spawn_id}",
           f"Task line (route exactly this): {a.task}"]
    if a.effort:
        out.append(f"Effort: {a.effort}")
    if a.charter:
        out += ["", "## Your charter", "", body]
    out += ["", "```", graph.rstrip("\n"), "```", "", "```", comp.rstrip("\n"), "```",
            "", "## Task", "", part.rstrip("\n"), "",
            "## Handback (fill these fields; the rules are in docs/graph/templates/prompts/handback-payload.md)",
            "", "```", payload.rstrip("\n"), "```"]
    if a.out:
        dest = Path(a.out)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text("\n".join(out) + "\n", encoding="utf-8")
        print(f"You are `{a.role}`, a CYPRESS specialist. spawn_id: {a.spawn_id}\n"
              f"Read your brief at {dest} whole before anything else and follow it: it holds\n"
              f"your task line, the graph discipline and the handback contract.")
        return 0
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
