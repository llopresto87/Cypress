#!/usr/bin/env python3
"""brief.py — compose a delegation brief from the plant's canonical templates.

The caller supplies only what is task-specific: the role, the spawn id, the
exact task line, the routing evidence, the effort and the task part. The two
canonical blocks of templates/prompts/graph-session-bootstrap.md and the
HANDBACK block of templates/prompts/handback-payload.md are copied byte for
byte, with their slots filled, so a brief carries them verbatim by
construction and neither the caller nor the worker reads the templates.
`--charter` prepends the role's charter body (frontmatter dropped) for a host
whose spawn has no agent type to carry it (Prime Agent). Step 1 routes with
`--role`, so the worker's route leaves out what its system prompt carries, and
a task line whose route loads no expertise.* or subsystem.* node is named on
stderr. A `security` brief, and
any brief composed with `--security-path` (a RED for a security contract, or for the security
pass's findings), also
carries the SECURITY PATH block of method/security-controls.md byte for byte
(`test-first.security-path`). A `reviewer` brief checks the files changed
(uncommitted, in the plant and in each repository directly under it) and the
files its task part names with `graph-lint.py --trust-claims`; a claimed file
prints `SECURITY PASS REQUIRED after this review: <files>` to the caller and is
logged with the spawn. `--kind KIND[,KIND] [--label LABEL]` derives the spawn's effort
from the role and task kind table of `method/delegation-model-classes.md`
(`delegation.effort`) and prints `effort: <value> (<reason>)` for the caller to
pass as the spawn's effort; of several kinds, `fix`, `mechanical` or `amend`
wins; `--effort` given verbatim is logged as it is. The class table beside it
gives the kind's model class: `model: <class> (<reason>)` and a `Model:` brief
line appear only where it differs from the role's `model:`.

  python3 docs/graph/brief.py --role tester --spawn-id orchestrator.3.tester.1 \
      --task "<exact task line>" --route "<agent-lint line or rationale>" \
      [--kind KIND [--label LABEL] | --effort "<value (reason)>"] [--charter] --part FILE|- [--out PATH]
      [--emulated "<reason>"] [--plan PATH] [--increments N[,N] --unit U [--alone "<reason>"]]
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
`--log` prints the log as the delivery's attribution lines, then the Session
metrics lines the log and the token ledger decide, in the form
session-metrics.py reads: `- Spawns:` (role×count class/effort), `- Serial
waits:` (issue groups: compositions more than ISSUE_GAP seconds apart are two
issues) and `- Tokens:` (the ledger's sums, a count any record lacks `not
recorded`, or `not recorded: <reason>`). It exits 1 with no spawn logged, and
1 with a BLOCK line for each logged review of trust-path files that no later
`security` spawn follows (`test-first.security-path`).

`--increments N[,N] --unit U` names the §9 increments the brief batches; when
they are fewer than the batch table gives their phase and hardest label and
`cycle.py`'s ready increments of that phase would join the batch `pack` makes,
stderr carries one `brief: batch notice — ...` line naming the table's number
and the spawn record gains a `notice` field. It never refuses: a security
brief, `--security-path`, `--alone REASON` (a concurrency GREEN batched alone)
prints no notice; an unknown increment or unreadable plan prints one
`brief: batch notice skipped — <reason>` line and logs nothing. Without the
flags nothing changes.

`--tokens SPAWN_ID --usage FILE|-` appends the spawn's host-reported token
counts to `tokens.jsonl` beside the spawn log, one record per logged spawn_id
(keys: spawn_id, model, input, cache_write, cache_write_5m, cache_write_1h,
cache_read, output, source). A count the usage object does not give is the
literal `not recorded`; nothing is estimated and no price is stored.
`--tokens SPAWN_ID --transcript PATH` reads a Claude Code subagent transcript
instead: each message counts once, from the last record carrying its id.
Exit 0 with one `tokens:` line; exit 2 naming an unlogged or already recorded
spawn_id, a key outside the schema, or a count that is not a whole number.
"""

import argparse
import datetime
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

GRAPH = Path(__file__).resolve().parent
BOOTSTRAP = GRAPH / "templates" / "prompts" / "graph-session-bootstrap.md"
HANDBACK = GRAPH / "templates" / "prompts" / "handback-payload.md"
CONTROLS = GRAPH / "method" / "security-controls.md"
AGENTS = GRAPH / "agents"
MODEL_CLASSES = GRAPH / "method" / "delegation-model-classes.md"
LABELS = {"low": "low", "medium-low": "low", "medium": "medium", "medium-hard": "high", "hard": "high"}
EFFORTS = ["low", "medium", "high"]
PICKED = [""]  # the one kind derive_effort read, for derive_class
LIGHT = ("fix", "mechanical", "amend")  # win over trust and red-trust when several kinds fit


def fenced(path: Path, head: str) -> str:
    m = re.search(r"```\n(" + re.escape(head) + r".*?)```", path.read_text(encoding="utf-8"), re.S)
    if not m:
        raise SystemExit(f"brief: no fenced {head} block in {path}")
    return m.group(1)


def charter_parts(role: str) -> tuple[str, str]:
    for p in sorted(AGENTS.glob("*.md")):
        text = p.read_text(encoding="utf-8")
        if text.startswith("---") and re.search(rf"^name:\s*{re.escape(role)}\s*$", text.split("---", 2)[1], re.M):
            _, head, body = text.split("---", 2)
            return head, body.strip()
    raise SystemExit(f"brief: no agent charter named {role!r} in {AGENTS}")


def charter(role: str) -> str:
    return charter_parts(role)[1]


def charter_head(role: str) -> str:
    return charter_parts(role)[0]


def table_rows(cell: str) -> dict:
    """{(role, kind): value} from a role and task kind table of `delegation.effort`;
    the effort table's kind cell carries `: description`, the class table's does not."""
    text = MODEL_CLASSES.read_text(encoding="utf-8") if MODEL_CLASSES.is_file() else ""
    return {(r, k): e.strip() for r, k, e in
            re.findall(r"^\| ([\w-]+) \| `([\w-]+)`" + cell + r"\| ([^|]+)\|$", text, re.M)}


def effort_rows() -> dict:
    """{(role, kind): effort} from the role and task kind table."""
    return table_rows(":[^|]*")


def class_rows() -> dict:
    """{(role, kind): model class} from the class table beside it."""
    return table_rows(" ")


def derive_class(role: str, kind: str) -> str:
    """`<class> (<role> <kind>, definition default <model>)` for the one kind the
    effort derivation picked, when its class row differs from the role's `model:`; else ""."""
    want = class_rows().get((role, kind))
    head = re.search(r"^model:\s*(\S+)", charter_head(role), re.M)
    default = head.group(1) if head else ""
    if not want or want == default:
        return ""
    return f"{want} ({role} {kind}, definition default {default or 'none'})"


def derive_effort(role: str, kind: str, label: str, security_path: bool, trust: list) -> str:
    """`<value> (<reason>)` by `delegation.effort`'s three rules; exit 2 on an unknown kind or label.
    A tester's RED for the security pass's findings (`findings`) takes its row, not rule 1."""
    if role == "security" or (security_path and kind != "findings"):
        return "high (security path)"
    rows = effort_rows()
    if kind == "first" and trust and (role, "first-trust") in rows:
        kind = "first-trust"
    kinds = [k for k in kind.split(",") if k]
    for k in kinds:
        if (role, k) not in rows:
            known = ", ".join(x for r, x in rows if r == role) or "none"
            raise SystemExit(f"brief: no effort row for {role} --kind {k}; its kinds: {known} "
                             f"(delegation.effort)")
    over = ""
    if len(kinds) > 1:
        light = [k for k in kinds if k in LIGHT]
        if not light:
            raise SystemExit(f"brief: --kind {kind} names several kinds and none of {', '.join(LIGHT)}, "
                             f"which win over the rest; name one (delegation.effort)")
        over = ", over " + ", ".join(k for k in kinds if k != light[0])
        kinds = light[:1]
    kind = kinds[0] if kinds else ""
    PICKED[0] = kind
    if kind:
        value = rows[(role, kind)]
        when = re.fullmatch(r"(\w+); (\w+) when labelled ([\w-]+(?: or [\w-]+)*)", value)
        if when:
            if label and label not in LABELS:
                raise SystemExit(f"brief: {role} --kind {kind} reads --label, one of {', '.join(LABELS)}")
            base, up, hard = when.group(1), when.group(2), when.group(3).split(" or ")
            got = up if label in hard else base
            return f"{got} ({role} {kind}, label {label})" if label else f"{got} ({role} {kind})"
        by_label = re.fullmatch(r"by label(?:, at most (\w+))?", value)
        if by_label:
            if label not in LABELS:
                raise SystemExit(f"brief: {role} --kind {kind} reads --label, one of {', '.join(LABELS)}")
            cap, got = by_label.group(1), LABELS[label]
            if cap and EFFORTS.index(got) > EFFORTS.index(cap):
                return f"{cap} ({role} {kind}, label {label}, capped at {cap})"
            return f"{got} ({role} {kind}, label {label})"
        return f"{value} ({role} {kind}{over})"
    head = re.search(r"^effort:\s*(\w+)", charter_head(role), re.M)
    return f"{head.group(1)} ({role} definition default)" if head else ""


def routes_expertise(task: str, role: str) -> bool:
    """Whether the worker's own route of `task` loads an expertise or subsystem
    node. A route that cannot run counts as routing one: the warning is advice."""
    try:
        r = subprocess.run([sys.executable, str(GRAPH / "graph-lint.py"), f"--plan-json={task}",
                            "--role", role], capture_output=True, text=True, timeout=60)
        load = json.loads(r.stdout)["load"]
    except (OSError, ValueError, KeyError, subprocess.SubprocessError):
        return True
    return any(e["id"].startswith(("expertise.", "subsystem.")) for e in load)


def changed_paths(plant: Path, part: str) -> list[str]:
    """Plant-relative paths a review covers: the uncommitted changes in the
    plant and in each repository directly under it, and the existing files
    the task part names."""
    paths = set()
    repos = [plant] + sorted(d for d in plant.iterdir() if (d / ".git").exists())
    for repo in repos:
        try:
            r = subprocess.run(["git", "-C", str(repo), "status", "--porcelain", "--untracked-files=all"],
                               capture_output=True, text=True, timeout=60)
        except (OSError, subprocess.SubprocessError):
            continue
        prefix = "" if repo == plant else repo.name + "/"
        for line in r.stdout.splitlines() if r.returncode == 0 else []:
            paths.add(prefix + line[3:].split(" -> ")[-1].strip('"'))
    for tok in re.findall(r"[\w.-]+(?:/[\w.-]+)+", part):
        tok = tok.rstrip(".")
        if (plant / tok).is_file():
            paths.add(tok)
    return sorted(paths)


def trust_claims(paths: list[str]) -> list[str]:
    """The paths a `trust: true` crosscut claims (`graph-lint.py --trust-claims`)."""
    if not paths:
        return []
    try:
        r = subprocess.run([sys.executable, str(GRAPH / "graph-lint.py"), "--trust-claims", *paths],
                           capture_output=True, text=True, timeout=60)
        return sorted(json.loads(r.stdout)["claims"])
    except (OSError, ValueError, KeyError, subprocess.SubprocessError):
        return []


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


NR = "not recorded"
COUNTS = ("input", "cache_write", "cache_write_5m", "cache_write_1h", "cache_read", "output")
TOKEN_KEYS = ("spawn_id", "model") + COUNTS + ("source",)


def token_ledger(plan: Path) -> Path:
    return plan.parent / "tokens.jsonl"


def transcript_usage(path: Path) -> dict:
    """Sums of a Claude Code subagent transcript's `assistant` usage, each
    message id counted once from its last record (a streamed message repeats
    its id and only the last record holds the final output count); a
    `<synthetic>` record is the host's, not a model response. No usage gives {}."""
    last = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            r = json.loads(line)
        except ValueError:
            continue
        m = r.get("message") if isinstance(r, dict) else None
        if r.get("type") != "assistant" or not isinstance(m, dict) or not isinstance(m.get("usage"), dict) \
                or m.get("model") == "<synthetic>":
            continue
        last[m.get("id") or f"line{len(last)}"] = m
    if not last:
        return {"source": "claude-code transcript"}
    host = {"input": ("input_tokens",), "cache_write": ("cache_creation_input_tokens",),
            "cache_write_5m": ("cache_creation", "ephemeral_5m_input_tokens"),
            "cache_write_1h": ("cache_creation", "ephemeral_1h_input_tokens"),
            "cache_read": ("cache_read_input_tokens",), "output": ("output_tokens",)}
    out = {"model": ", ".join(sorted({m.get("model") for m in last.values() if m.get("model")})) or NR,
           "source": "claude-code transcript"}
    for key, where in host.items():
        vals = []
        for m in last.values():
            v = m["usage"]
            for w in where:
                v = v.get(w) if isinstance(v, dict) else None
            if isinstance(v, int) and not isinstance(v, bool):
                vals.append(v)
        if vals:
            out[key] = sum(vals)
    return out


def record_tokens(argv: list) -> int:
    tp = argparse.ArgumentParser(prog="brief.py --tokens")
    tp.add_argument("--tokens", required=True, metavar="SPAWN_ID")
    src = tp.add_mutually_exclusive_group(required=True)
    src.add_argument("--usage", help="a JSON usage object, or - for stdin")
    src.add_argument("--transcript", help="a Claude Code subagent transcript")
    tp.add_argument("--plan", default=str(GRAPH / "plans" / "grill.md"))
    a = tp.parse_args(argv)
    sid, plan = a.tokens, Path(a.plan)
    try:
        if a.transcript:
            usage = transcript_usage(Path(a.transcript))
        else:
            usage = json.loads(sys.stdin.read() if a.usage == "-" else Path(a.usage).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        print(f"brief: --tokens could not read the usage: {e}", file=sys.stderr)
        return 2
    if not isinstance(usage, dict):
        print("brief: --tokens takes a JSON object", file=sys.stderr)
        return 2
    extra = sorted(set(usage) - set(TOKEN_KEYS[1:]))
    if extra:
        print(f"brief: --tokens: {', '.join(extra)} is outside the ledger's keys "
              f"({', '.join(TOKEN_KEYS[1:])}); no price is stored", file=sys.stderr)
        return 2
    for k in COUNTS:
        v = usage.get(k, NR)
        if v != NR and (isinstance(v, bool) or not isinstance(v, int) or v < 0):
            print(f"brief: --tokens: {k} is {v!r}, not a whole number or {NR!r}", file=sys.stderr)
            return 2
    if not any(r.get("spawn_id") == sid for r in read_log(plan)):
        print(f"brief: spawn_id {sid} is not in the spawn log {spawn_log(plan)}", file=sys.stderr)
        return 2
    ledger = token_ledger(plan)
    held = ledger.read_text(encoding="utf-8").splitlines() if ledger.is_file() else []
    if any(json.loads(l).get("spawn_id") == sid for l in held if l.strip().startswith("{")):
        print(f"brief: spawn_id {sid} is already recorded in {ledger}; the ledger is append-only", file=sys.stderr)
        return 2
    rec = {k: usage.get(k, NR) for k in TOKEN_KEYS}
    rec["spawn_id"] = sid
    with open(ledger, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"tokens: {sid} — {rec['model']} — input {rec['input']}, cache write {rec['cache_write']} "
          f"(5m {rec['cache_write_5m']}, 1h {rec['cache_write_1h']}), cache read {rec['cache_read']}, "
          f"output {rec['output']} — source: {rec['source']}")
    return 0


CLASSES = {"opus": "authoring", "sonnet": "investigation", "haiku": "investigation", "inherit": "inherit"}
ISSUE_GAP = 60  # seconds between two compositions that make them two issues, not one


def metrics_lines(plan: Path, rows: list[dict]) -> list[str]:
    """The Session metrics lines the spawn log and the token ledger decide
    (protocols/deliver.md): Spawns, Serial waits and Tokens, in the form
    session-metrics.py reads. The lines that need judgment stay the lead's."""
    last = {r["spawn_id"]: r for r in rows if r.get("spawn_id")}
    groups: dict[tuple, int] = {}
    for r in last.values():
        try:
            m = re.search(r"^model:\s*(\S+)", charter_head(r["role"]), re.M)
            cls = CLASSES.get(m.group(1), m.group(1)) if m else "class not recorded"
        except SystemExit:
            cls = "class not recorded"
        eff = (r.get("effort") or "").split(" ")[0] or "effort not recorded"
        groups[(r["role"], cls, eff)] = groups.get((r["role"], cls, eff), 0) + 1
    out = [f"- Spawns: {len(last)} (" + ", ".join(f"{role}×{n} {cls}/{eff}"
                                                  for (role, cls, eff), n in sorted(groups.items())) + ")"]
    issues: list[list[str]] = []
    prev = None
    for r in last.values():
        try:
            at = datetime.datetime.fromisoformat(r["at"])
        except (KeyError, TypeError, ValueError):
            issues = []
            break
        if prev is None or (at - prev).total_seconds() > ISSUE_GAP:
            issues.append([])
        issues[-1].append(r["spawn_id"])
        prev = at
    out.append(f"- Serial waits: {len(issues) - 1} (inferred from composition times, not handback order: "
               f"issue groups, a gap over {ISSUE_GAP} s between "
               f"compositions: " + " → ".join(" ".join(g) for g in issues) + ")" if issues else
               "- Serial waits: not recorded: a spawn log line carries no composition time")
    ledger = token_ledger(plan)
    held, bad = {}, 0
    for i, line in enumerate(ledger.read_text(encoding="utf-8").splitlines() if ledger.is_file() else [], 1):
        try:
            rec = json.loads(line) if line.strip() else {}
        except ValueError:
            rec = None
        if not isinstance(rec, dict):
            bad = bad or i
        elif rec.get("spawn_id") in last:
            held[rec["spawn_id"]] = rec
    if bad:
        out.append(f"- Tokens: not recorded: {ledger.name} line {bad} is not a JSON record")
    elif not held:
        out.append(f"- Tokens: not recorded: no spawn has a record in the token ledger {ledger.name}")
    else:
        def total(k):
            vals = [r.get(k) for r in held.values()]
            ok = all(isinstance(v, int) and not isinstance(v, bool) for v in vals)
            return str(sum(vals)) if ok else NR
        out.append(f"- Tokens: input {total('input')}, cache write {total('cache_write')} "
                   f"(5m {total('cache_write_5m')}, 1h {total('cache_write_1h')}), cache read "
                   f"{total('cache_read')}, output {total('output')} — {len(held)} of {len(last)} "
                   f"spawn{'s' if len(last) != 1 else ''} recorded")
    return out


def batch_notice(plan: Path, unit: str, increments: str) -> str:
    """One notice when the briefed increments are fewer than the batch the
    table gives them while more of the same phase are ready to join
    (`delegation.effort-scale`), else ""; read through cycle.py's own state
    and grill-lint.py's own `pack`. Never a refusal: a problem is a skip line."""
    try:
        sys.dont_write_bytecode = True
        spec = importlib.util.spec_from_file_location("cypress_cycle", GRAPH / "cycle.py")
        cy = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cy)
        c = cy.Cycle(plan, unit)
        nums = [int(x) for x in increments.split(",") if x.strip()]
        unknown = [n for n in nums if n not in c.order]
        if not nums or unknown:
            return f"batch notice skipped — increment {', '.join(map(str, unknown)) or increments!r} is not in §9"
        ph = c.phase[nums[0]]
        if ph not in c.gl.BATCH_SIZE or any(c.label[n] is None for n in nums):
            return ""
        ready = c.state()[5].get(ph, [])
        members = sorted(set(nums) | set(ready), key=c.order.get)
        batch = next(b for b, _d in c.gl.pack(members, ph, c.tokens, c.label, c.order, []) if nums[0] in b)
        join = sorted(set(batch) - set(nums), key=c.order.get)
        hardest = max((c.label[n] for n in nums), key=list(c.gl.BATCH_SIZE["RED"]).index)
        size = c.gl.BATCH_SIZE[ph][hardest]
        if not join or len(nums) >= size:
            return ""
        return (f"batch notice — increment{'s' if len(nums) > 1 else ''} {', '.join(map(str, nums))} "
                f"{'are' if len(nums) > 1 else 'is'} {len(nums)} of the batch table's {size} for {ph} {hardest}; "
                f"ready to join it: {', '.join(map(str, join))} (delegation.effort-scale)")
    except Exception as e:  # a notice never blocks the brief (cycle.py's Refusal included)
        return f"batch notice skipped — {e}"


def main() -> int:
    if "--tokens" in sys.argv[1:]:
        return record_tokens(sys.argv[1:])
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
        print("\n".join(metrics_lines(Path(lp.parse_args().plan), rows)))
        owed = [r for i, r in enumerate(rows) if r.get("role") == "reviewer" and r.get("trust")
                and not any(x.get("role") == "security" for x in rows[i + 1:])]
        for r in owed:
            print(f"BLOCK: {r['spawn_id']} reviewed trust-path files ({', '.join(r['trust'])}) and no "
                  f"security spawn follows it in the spawn log (test-first.security-path)", file=sys.stderr)
        return 1 if owed else 0
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--role", required=True)
    ap.add_argument("--spawn-id", required=True)
    ap.add_argument("--task", required=True, help="the exact task line the worker routes")
    ap.add_argument("--route", required=True, help="the agent-lint --route line, or the override rationale")
    ap.add_argument("--effort", default="", help="the effort verbatim, instead of --kind")
    ap.add_argument("--kind", default="", help="the task kind of the role's effort row (delegation.effort)")
    ap.add_argument("--label", default="", help="the hardest increment effort label, for a `by label` row")
    ap.add_argument("--charter", action="store_true",
                    help="prepend the role's charter body; Prime Agent only, whose spawn has no agent type")
    ap.add_argument("--part", required=True, help="file holding the task part, or - for stdin")
    ap.add_argument("--out", default="", help="write the brief here and print only a pointer prompt")
    ap.add_argument("--plan", default=str(GRAPH / "plans" / "grill.md"))
    ap.add_argument("--security-path", action="store_true",
                    help="embed the SECURITY PATH block (a RED for a security contract or its findings)")
    ap.add_argument("--emulated", default="",
                    help="this spawn runs a generic host type wearing --role; the reason")
    ap.add_argument("--increments", default="", help="the §9 increments of this batch, N[,N]; with --unit")
    ap.add_argument("--unit", default="", help="the unit of work, for the batch-size notice")
    ap.add_argument("--alone", default="", help="a security or concurrency GREEN batched alone: the reason")
    a = ap.parse_args()
    if bool(a.increments) != bool(a.unit):
        print("brief: --increments and --unit go together", file=sys.stderr)
        return 2
    try:
        body = charter(a.role)
        part = sys.stdin.read() if a.part == "-" else Path(a.part).read_text(encoding="utf-8")
        graph = (fenced(BOOTSTRAP, "GRAPH DISCIPLINE").replace("{{exact delegated task}}", a.task)
                 .replace("{{role}}", a.role))
        comp = fenced(BOOTSTRAP, "COMPANION")
        comp = re.sub(r"\{\{the protocol phase.*?\}\}", a.route, comp, flags=re.S)
        payload = fenced(HANDBACK, "HANDBACK")
        security = (fenced(CONTROLS, "SECURITY PATH")
                    if a.role == "security" or a.security_path else "")
    except SystemExit as e:
        print(e, file=sys.stderr)
        return 2
    plant = GRAPH.parent.parent
    if a.charter and not (plant / ".prime" / "agent").is_dir() \
            and any((plant / ".claude" / "agents").glob("*.md")):
        print("brief: --charter is for Prime Agent, whose spawn has no agent type; on Claude Code "
              "the agent type carries the charter in its system prompt", file=sys.stderr)
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
    trust = trust_claims(changed_paths(plant, part)) if a.role == "reviewer" else []
    if trust:
        print(f"brief: SECURITY PASS REQUIRED after this review: {', '.join(trust)}", file=sys.stderr)
    if not a.effort:
        try:
            a.effort = derive_effort(a.role, a.kind, a.label, a.security_path, trust)
        except SystemExit as e:
            print(e, file=sys.stderr)
            return 2
    if a.effort:
        print(f"effort: {a.effort} — pass it as this spawn's effort", file=sys.stderr)
    model = derive_class(a.role, PICKED[0]) if PICKED[0] else ""
    if model:
        print(f"model: {model} — pass it as this spawn's model", file=sys.stderr)
    out = [f"You are `{a.role}`, a CYPRESS specialist. spawn_id: {a.spawn_id}",
           f"Task line (route exactly this): {a.task}"]
    if a.effort:
        out.append(f"Effort: {a.effort}")
    if model:
        out.append(f"Model: {model}")
    if a.charter:
        out += ["", "## Your charter", "", body]
    out += ["", "```", graph.rstrip("\n"), "```", "", "```", comp.rstrip("\n"), "```"]
    if security:
        out += ["", "```", security.rstrip("\n"), "```"]
    out += ["", "## Task", "", part.rstrip("\n"), "",
            "## Handback (fill these fields; the rules are in docs/graph/templates/prompts/handback-payload.md)",
            "", "```", payload.rstrip("\n"), "```"]
    if not routes_expertise(a.task, a.role):
        print("brief: the task line routes no expertise.* or subsystem.* node; name the files it "
              "touches or their stack in --task, so the worker loads that expertise "
              "(graph-session-bootstrap.md, Stack expertise)", file=sys.stderr)
    notice = ""
    if a.increments and not (a.alone or a.security_path or a.role == "security"):
        notice = batch_notice(Path(a.plan), a.unit, a.increments)
        if notice:
            print(f"brief: {notice}", file=sys.stderr)
        if notice.startswith("batch notice skipped"):
            notice = ""
    log = spawn_log(Path(a.plan))
    log.parent.mkdir(parents=True, exist_ok=True)
    rec = {"spawn_id": a.spawn_id, "role": a.role, "task": a.task, "route": a.route,
           "effort": a.effort, "emulated": a.emulated, "trust": trust,
           "brief": a.out, "at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")}
    if notice:
        rec["notice"] = notice
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
