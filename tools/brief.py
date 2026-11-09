#!/usr/bin/env python3
"""brief.py — compose a delegation brief from the plant's canonical templates.

The caller supplies only what is task-specific: the role, the spawn id, the
exact task line, the routing evidence, the effort and the task part. The two
canonical blocks of templates/prompts/graph-session-bootstrap.md and the
HANDBACK block of templates/prompts/handback-payload.md are copied byte for
byte, with their slots filled, so a brief carries them verbatim by
construction and neither the caller nor the worker reads the templates.
`--charter` prepends the role's charter body (frontmatter dropped) for a host
whose spawn has no agent type to carry it (Prime Agent). A `security` brief, and
any brief composed with `--security-path` (a RED for a security contract), also
carries the SECURITY PATH block of method/security-controls.md byte for byte
(`test-first.security-path`).

  python3 docs/graph/brief.py --role tester --spawn-id orchestrator.3.tester.1 \
      --task "<exact task line>" --route "<agent-lint line or rationale>" \
      [--effort "<label (row n: reason)>"] [--charter] --part FILE|- [--out PATH]
      [--emulated "<reason>"] [--plan PATH]
  python3 docs/graph/brief.py --log

Exit 0 and the brief on stdout; exit 2 with one stderr line on an unknown role,
a missing template, or a slot left unfilled. With `--out PATH` the brief is
written to PATH and stdout carries only a three-line spawn prompt that points
at it: where the spawn prompt stays in the caller's context, the brief then
never enters it, and the file is the brief's record beside the handbacks.

Every composed brief appends one JSON line to `spawns.jsonl` beside the plan
(spawn_id, role, task, route, effort, emulated, brief path, time):
the spawn's attribution record, so the worker echoes none of it and the
deliver-time attribution assertion reads the log. A spawn_id already logged
for another role is refused (mint once, `delegation.tracing`).
`--log` prints the log as the delivery's attribution lines and exits.
"""

import argparse
import datetime
import json
import re
import sys
from pathlib import Path

GRAPH = Path(__file__).resolve().parent
BOOTSTRAP = GRAPH / "templates" / "prompts" / "graph-session-bootstrap.md"
HANDBACK = GRAPH / "templates" / "prompts" / "handback-payload.md"
CONTROLS = GRAPH / "method" / "security-controls.md"
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


def spawn_log(plan: Path) -> Path:
    return plan.parent / "spawns.jsonl"


def read_log(plan: Path) -> list[dict]:
    path = spawn_log(plan)
    if not path.is_file():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            rows.append(json.loads(line))
        except ValueError:
            continue
    return rows


def main() -> int:
    if "--log" in sys.argv[1:]:
        lp = argparse.ArgumentParser()
        lp.add_argument("--log", action="store_true")
        lp.add_argument("--plan", default=str(GRAPH / "plans" / "grill.md"))
        rows = read_log(Path(lp.parse_args().plan))
        last = {r["spawn_id"]: r for r in rows if r.get("spawn_id")}
        for r in last.values():
            print(f"- {r['spawn_id']} — produced_by: {r['role']} — route: {r['route']}"
                  + (f" — effort: {r['effort']}" if r.get("effort") else "")
                  + (f" — role-emulated ({r['emulated']})" if r.get("emulated") else ""))
        if not last:
            print(f"brief: no spawns logged at {spawn_log(Path(lp.parse_args().plan))}", file=sys.stderr)
            return 1
        return 0
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--role", required=True)
    ap.add_argument("--spawn-id", required=True)
    ap.add_argument("--task", required=True, help="the exact task line the worker routes")
    ap.add_argument("--route", required=True, help="the agent-lint --route line, or the override rationale")
    ap.add_argument("--effort", default="")
    ap.add_argument("--charter", action="store_true", help="prepend the role's charter body")
    ap.add_argument("--part", required=True, help="file holding the task part, or - for stdin")
    ap.add_argument("--out", default="", help="write the brief here and print only a pointer prompt")
    ap.add_argument("--plan", default=str(GRAPH / "plans" / "grill.md"))
    ap.add_argument("--security-path", action="store_true",
                    help="embed the SECURITY PATH block (a RED for a security contract)")
    ap.add_argument("--emulated", default="",
                    help="this spawn runs a generic host type wearing --role; the reason")
    a = ap.parse_args()
    try:
        body = charter(a.role)
        part = sys.stdin.read() if a.part == "-" else Path(a.part).read_text(encoding="utf-8")
        graph = fenced(BOOTSTRAP, "GRAPH DISCIPLINE").replace("{{exact delegated task}}", a.task)
        comp = fenced(BOOTSTRAP, "COMPANION")
        comp = re.sub(r"\{\{the protocol phase.*?\}\}", a.route, comp, flags=re.S)
        payload = fenced(HANDBACK, "HANDBACK")
        security = (fenced(CONTROLS, "SECURITY PATH")
                    if a.role == "security" or a.security_path else "")
    except SystemExit as e:
        print(e, file=sys.stderr)
        return 2
    if "{{" in graph + comp:
        print("brief: a bootstrap slot this tool does not fill is left in the template", file=sys.stderr)
        return 2
    clash = [r for r in read_log(Path(a.plan))
             if r.get("spawn_id") == a.spawn_id and r.get("role") != a.role]
    if clash:
        print(f"brief: spawn_id {a.spawn_id} is already logged for role {clash[-1]['role']!r}; "
              f"mint a new one (delegation.tracing)", file=sys.stderr)
        return 2
    out = [f"You are `{a.role}`, a CYPRESS specialist. spawn_id: {a.spawn_id}",
           f"Task line (route exactly this): {a.task}"]
    if a.effort:
        out.append(f"Effort: {a.effort}")
    if a.charter:
        out += ["", "## Your charter", "", body]
    out += ["", "```", graph.rstrip("\n"), "```", "", "```", comp.rstrip("\n"), "```"]
    if security:
        out += ["", "```", security.rstrip("\n"), "```"]
    out += ["", "## Task", "", part.rstrip("\n"), "",
            "## Handback (fill these fields; the rules are in docs/graph/templates/prompts/handback-payload.md)",
            "", "```", payload.rstrip("\n"), "```"]
    log = spawn_log(Path(a.plan))
    log.parent.mkdir(parents=True, exist_ok=True)
    rec = {"spawn_id": a.spawn_id, "role": a.role, "task": a.task, "route": a.route,
           "effort": a.effort, "emulated": a.emulated,
           "brief": a.out, "at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")}
    with open(log, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
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
