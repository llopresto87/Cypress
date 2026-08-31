#!/usr/bin/env python3
"""agent-lint.py — the mechanical agent-router, roster linter, and eval gate.

The knowledge router (`docs/graph/graph-lint.py --plan`) mechanizes the cheap
decision — which docs to read. This tool mechanizes the expensive one — which
specialist does the work — with the same executable floor, IDF-weighted scoring,
and honesty about being a keyword heuristic rather than an oracle.

It is the agent analog of `graph-lint.py`: it parses the roster's frontmatter,
scores each agent's `routing_triggers` / `name` / `description` against a task,
and returns a ranked list with a confidence band. It also lints the delegation
frontmatter and scores a golden routing corpus as a fail-closed gate.

Install target : .claude/agent-lint.py
Seed source    : cypress/integrations/claude-code/agent-lint.py
(kept byte-identical). Design of record:
  docs/plans/agent-routing-and-delegation.md  (§4 router, §4.1 schema, §4.3 eval)

Usage:
    python3 agent-lint.py --route "TASK"   # rank specialists + confidence band
    python3 agent-lint.py --lint           # validate roster frontmatter (default)
    python3 agent-lint.py --eval           # score the golden corpus; fail-closed

No third-party dependencies: it must run on a bare python3.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

# ----------------------------- CONFIG -------------------------------------
# The router walks up for this directory the way route-hook.py walks up for
# docs/graph/graph-lint.py.
AGENTS_REL = Path(".claude") / "agents"
GOLDEN_NAME = "_routes.golden.tsv"

# Delegation-depth bounds (plan ADR-B): 1 <= max_spawn_depth <= 3.
MIN_DEPTH, MAX_DEPTH = 1, 3

# Confidence-band calibration (plan §4.2 — tunable, calibrated to the golden
# corpus). A single distinctive trigger double-hit scores weight(3)*2*2 = 12; a
# genuine multi-term route scores far higher, while a novel task that only grazes
# one stray trigger word tops out near 12. FLOOR sits in that gap so novel-stack
# tasks fall to LOW (the commission path) and real routes clear it.
FLOOR = 13
HIGH_RATIO = 1.5

# Eval gate (plan §4.3): top-1 accuracy over the labeled rows must clear this,
# and every novel-stack ("LOW") row must return LOW or NONE.
EVAL_THRESHOLD = 0.90

STEM = 6  # prefix length for the singular/plural fold (test/tests, node/nodes)

# Filler words that carry no routing signal (mirrors graph-lint's stopword set).
STOPWORDS = frozenset(
    "the and for add new from that this with why how are was not you its "
    "change what where when does did into out about a an of to in on it "
    "over via using use onto off around per which while would could should "
    "want need make made get got run see tell show give take find "
    "there any some someone goes going tells told anyone something "
    "stack whole".split()
)

# Task is the one tool whose presence is harness-enforced delegation capability
# (plan ADR-C): can_delegate MUST equal (Task in tools).
DELEGATE_TOOL = "Task"


class LintError(Exception):
    pass


# --- frontmatter parsing --------------------------------------------------


@dataclass
class Agent:
    path: Path
    meta: dict
    body: str

    @property
    def name(self) -> str:
        return str(self.meta.get("name", "") or self.path.stem)

    @property
    def model(self) -> str:
        return str(self.meta.get("model", ""))

    @property
    def ident(self) -> str:
        """Human-facing identity for lint messages (stem + declared name)."""
        stem = self.path.stem
        name = str(self.meta.get("name", ""))
        return f"{stem}" if name in ("", stem) else f"{stem} ({name})"

    def get_list(self, key: str) -> list:
        v = self.meta.get(key, [])
        return v if isinstance(v, list) else [v]

    @property
    def tools(self) -> list:
        return [str(t) for t in self.get_list("tools")]

    @property
    def triggers(self) -> list:
        return [str(t) for t in self.get_list("routing_triggers")]

    @property
    def description(self) -> str:
        return str(self.meta.get("description", ""))

    @property
    def can_delegate(self) -> bool:
        return str(self.meta.get("can_delegate", "")).strip().lower() == "true"

    @property
    def has_task(self) -> bool:
        return DELEGATE_TOOL in self.tools

    @property
    def max_spawn_depth(self):
        return self.meta.get("max_spawn_depth")

    @property
    def delegates_to(self) -> list:
        return [str(d) for d in self.get_list("delegates_to")]

    @property
    def effective_depth(self) -> int:
        """Leaves (can_delegate:false) sit at depth 0 (plan ADR-B)."""
        if not self.can_delegate:
            return 0
        d = self.max_spawn_depth
        return d if isinstance(d, int) else 0


def _scalar(v: str):
    """Parse the small YAML value subset the agent frontmatter permits.

    Extends graph-lint's `_scalar` with inline-list parsing (`[a, b, c]`), the
    form the agent `tools:` (and any inline `routing_triggers`) line uses — the
    parser gap the router must close so the Task⟺can_delegate rule can be checked.
    """
    v = v.strip()
    # Strip a trailing `  # comment` on unquoted, non-list values only.
    if v[:1] not in "\"'[" and "  #" in v:
        v = v.split("  #", 1)[0].strip()
    if v.startswith("[") and v.endswith("]"):
        inner = v[1:-1].strip()
        if not inner:
            return []
        return [x.strip().strip("\"'") for x in inner.split(",") if x.strip()]
    if v and v[0] in "\"'" and v[-1] == v[0] and len(v) > 1:
        return v[1:-1]
    if re.fullmatch(r"-?\d+", v):
        return int(v)
    return v


def parse_frontmatter(text: str, path: Path):
    """Parse the YAML subset the agent contract permits (mirrors graph-lint)."""
    if not text.startswith("---\n"):
        raise LintError(f"{path.name}: missing YAML frontmatter")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise LintError(f"{path.name}: unterminated frontmatter")
    raw, body = text[4:end], text[end + 5:]

    meta: dict = {}
    current = None
    for lineno, line in enumerate(raw.split("\n"), start=2):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith((" ", "\t")):
            item = line.strip()
            if not item.startswith("- "):
                raise LintError(f"{path.name}:{lineno}: expected '- item', got {line!r}")
            if current is None:
                raise LintError(f"{path.name}:{lineno}: list item before any key")
            meta.setdefault(current, []).append(_scalar(item[2:]))
            continue
        if ":" not in line:
            raise LintError(f"{path.name}:{lineno}: expected 'key: value', got {line!r}")
        key, _, value = line.partition(":")
        key, value = key.strip(), value.strip()
        if value:
            meta[key] = _scalar(value)
            current = None
        else:
            meta[key] = []
            current = key
    return meta, body


def find_agents_dir() -> Path | None:
    """Walk up from cwd and the script's own location for `.claude/agents/`."""
    starts = [Path.cwd(), Path(__file__).resolve().parent]
    seen = set()
    for start in starts:
        p = start.resolve()
        for _ in range(8):
            if p in seen:
                break
            seen.add(p)
            cand = p / AGENTS_REL
            if cand.is_dir():
                return cand
            if p.name == ".claude" and (p / "agents").is_dir():
                return p / "agents"
            p = p.parent
    return None


def load_agents(adir: Path) -> list:
    agents = []
    for p in sorted(adir.glob("*.md")):
        if p.name.startswith("_"):
            continue
        meta, body = parse_frontmatter(p.read_text(encoding="utf-8"), p)
        agents.append(Agent(p, meta, body))
    if not agents:
        raise LintError(f"no agent defs found in {adir}")
    return agents


# --- scoring (mirror graph-lint.resolve) ----------------------------------


def _tokens(text: str) -> set:
    return set(re.findall(r"[a-z0-9_]+", text.lower()))


def _match(term: str, toks: set) -> int:
    """Token-match strength: 2 exact, 1 prefix-fold, 0 none. Never substring."""
    if term in toks:
        return 2
    if len(term) >= STEM and any(k.startswith(term[:STEM]) for k in toks):
        return 1
    return 0


def _terms(task: str) -> set:
    """Extract match terms, keeping paths whole and split (`/api/x` → `x`)."""
    out = set()
    for w in re.findall(r"[a-z0-9_/*.-]+", task.lower()):
        for part in [w, *re.split(r"[/*.-]+", w)]:
            part = part.strip("_")
            if len(part) >= 3 and part not in STOPWORDS:
                out.add(part)
    return out


def _token_sets(agent: Agent):
    name_toks = _tokens(agent.name)
    trig_toks = _tokens(" ".join(agent.triggers))
    desc_toks = _tokens(agent.description)
    return name_toks, trig_toks, desc_toks


def score(agents: list, task: str):
    """Rank agents for a task. IDF-weighted: a term matching many agents is
    generic (low weight); one matching one or two is distinctive (dominates).

    score(agent) = Σ_t weight(t) · max(2·match(name), 2·match(trigger),
    1·match(desc)) — triggers and name are first-class, description is the
    fallback (plan §4.2).
    """
    terms = _terms(task)
    buckets = {a.name: _token_sets(a) for a in agents}

    df = {t: 0 for t in terms}
    for name_toks, trig_toks, desc_toks in buckets.values():
        allt = name_toks | trig_toks | desc_toks
        for t in terms:
            if _match(t, allt):
                df[t] += 1

    def weight(t: str) -> int:
        d = df.get(t, 0)
        return 3 if d <= 1 else 2 if d <= 3 else 1

    entries = []
    for a in agents:
        name_toks, trig_toks, desc_toks = buckets[a.name]
        s = 0
        for t in terms:
            w = weight(t)
            s += w * max(
                2 * _match(t, name_toks),
                2 * _match(t, trig_toks),
                1 * _match(t, desc_toks),
            )
        if s:
            entries.append((s, a))
    entries.sort(key=lambda x: (-x[0], x[1].name))
    return entries


def confidence(entries: list) -> str:
    best = entries[0][0] if entries else 0
    second = entries[1][0] if len(entries) > 1 else 0
    if best == 0:
        return "NONE"
    if best < FLOOR:
        return "LOW"
    if best >= HIGH_RATIO * second:
        return "HIGH"
    return "MEDIUM"


# --- commands -------------------------------------------------------------

BANNER = "Router suggestion is a keyword heuristic — reason over it, not an oracle."


def cmd_route(agents: list, task: str) -> int:
    entries = score(agents, task)
    band = confidence(entries)
    top = entries[0][1].name if entries else None

    print(BANNER)
    print()
    print(f"task: {task}")
    print()
    print(f"ROUTE (ranked, confidence: {band}):")
    for s, a in entries[:5]:
        print(f"  {a.name:<18} {a.model:<6} can_delegate={str(a.can_delegate).lower():<5} score={s}")
    if band in ("HIGH", "MEDIUM"):
        print(f"HINT: cite this in the delegation brief. {band} → top candidate `{top}`"
              f"{'.' if band == 'HIGH' else '; confirm before routing.'}")
        print("      If you override to a different/generic agent, record why "
              "(deliver assertion checks this).")
    else:
        print("HINT: no clear specialist — commission an expert from "
              "templates/agent.template.md, then delegate (RC4 path).")
    # This ranks files ON DISK. It cannot see the host's session registry, so
    # it will name a specialist a just-installed session is unable to spawn.
    print("NOTE: fit only, not registration — this reads .claude/agents/ off "
          "disk, not the host's session registry. Preflight the type before "
          "dispatch (docs/graph/method/delegation.md, "
          "delegation.harness-registration).")
    return 0


def _distinctiveness_warnings(agents: list) -> list:
    """Rule 4 (plan §4.1): warn when a trigger token is shared across too many
    agents — a non-distinctive trigger carries no routing signal (the IDF
    analog). Warnings never fail the lint."""
    limit = max(3, len(agents) // 2)
    token_owners: dict = {}
    for a in agents:
        for tok in _tokens(" ".join(a.triggers)):
            if len(tok) < 3 or tok in STOPWORDS:
                continue
            token_owners.setdefault(tok, set()).add(a.name)
    warns = []
    for tok, owners in sorted(token_owners.items()):
        if len(owners) > limit:
            warns.append(f"trigger token {tok!r} shared across {len(owners)} agents "
                         f"(low routing signal): {', '.join(sorted(owners))}")
    return warns


def cmd_lint(agents: list) -> int:
    names = {a.name for a in agents}
    depth_by_name = {a.name: a.effective_depth for a in agents}
    errs = []

    for a in agents:
        # Rule 1: routing_triggers present and non-empty.
        if not a.triggers:
            errs.append(f"{a.ident}: routing_triggers missing or empty (§4.1 rule 1)")

        # Rule 2: can_delegate == (Task in tools). No dormant-but-enabled drift.
        if a.can_delegate != a.has_task:
            errs.append(
                f"{a.ident}: can_delegate={str(a.can_delegate).lower()} but "
                f"{'Task is' if a.has_task else 'Task is not'} in tools — "
                f"can_delegate must equal (Task ∈ tools) (§4.1 rule 2)"
            )

        # Rule 3: delegation caps present and coherent iff can_delegate.
        if a.can_delegate:
            d = a.max_spawn_depth
            if not isinstance(d, int) or not (MIN_DEPTH <= d <= MAX_DEPTH):
                errs.append(f"{a.ident}: max_spawn_depth must be an int in "
                            f"[{MIN_DEPTH},{MAX_DEPTH}] (got {d!r}) (§4.1 rule 3)")
            if not a.delegates_to:
                errs.append(f"{a.ident}: can_delegate:true requires a non-empty "
                            f"delegates_to allowlist (§4.1 rule 3)")
            for target in a.delegates_to:
                if target not in names:
                    errs.append(f"{a.ident}: delegates_to → unknown agent {target!r}")
                    continue
                if isinstance(d, int) and depth_by_name[target] >= d:
                    errs.append(
                        f"{a.ident}: delegates_to → {target!r} has depth "
                        f"{depth_by_name[target]} ≥ this agent's {d}; the allowlist "
                        f"must name strictly-shallower agents (leaves = 0) (ADR-B)"
                    )
        else:
            if a.max_spawn_depth is not None:
                errs.append(f"{a.ident}: max_spawn_depth is set but can_delegate is "
                            f"false — leaves carry no caps (§4.1 rule 3)")
            if a.delegates_to:
                errs.append(f"{a.ident}: delegates_to is set but can_delegate is "
                            f"false — leaves carry no allowlist (§4.1 rule 3)")

    for w in _distinctiveness_warnings(agents):
        print(f"agent-lint: warning: {w}", file=sys.stderr)

    if errs:
        print(f"agent-lint: {len(errs)} error(s) across {len(agents)} agent(s)\n",
              file=sys.stderr)
        for e in errs:
            print(f"  ✗ {e}", file=sys.stderr)
        return 1

    print(f"agent-lint: OK — {len(agents)} agents, frontmatter and delegation graph valid")
    return 0


def load_golden(adir: Path):
    path = adir / GOLDEN_NAME
    if not path.exists():
        raise LintError(f"missing golden corpus: {path}")
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "\t" not in line:
            continue
        task, expected = line.split("\t", 1)
        rows.append((task.strip(), expected.strip()))
    if not rows:
        raise LintError(f"golden corpus is empty: {path}")
    return rows


def cmd_eval(agents: list, adir: Path) -> int:
    rows = load_golden(adir)
    labeled = [(t, e) for t, e in rows if e != "LOW"]
    novel = [(t, e) for t, e in rows if e == "LOW"]

    misroutes = []
    correct = 0
    for task, expected in labeled:
        entries = score(agents, task)
        top = entries[0][1].name if entries else None
        if top == expected:
            correct += 1
        else:
            misroutes.append((task, expected, top))

    novel_leaks = []
    for task, _ in novel:
        entries = score(agents, task)
        band = confidence(entries)
        if band not in ("LOW", "NONE"):
            top = entries[0][1].name if entries else None
            novel_leaks.append((task, band, top))

    total = len(labeled)
    acc = correct / total if total else 1.0
    print(f"agent-lint --eval: top-1 accuracy {acc*100:.1f}% ({correct}/{total}); "
          f"novel-stack rows checked: {len(novel)}")
    for task, expected, top in misroutes:
        print(f"  ✗ misroute: {task!r} → got {top!r}, expected {expected!r}", file=sys.stderr)
    for task, band, top in novel_leaks:
        print(f"  ✗ novel-stack leak: {task!r} → {band} (top {top!r}); "
              f"must be LOW/NONE (commission path)", file=sys.stderr)

    ok = acc >= EVAL_THRESHOLD and not novel_leaks
    if not ok:
        print(f"agent-lint --eval: FAIL — accuracy {acc*100:.1f}% "
              f"(threshold {EVAL_THRESHOLD*100:.0f}%) / {len(novel_leaks)} novel leak(s)",
              file=sys.stderr)
        return 1
    print(f"agent-lint --eval: OK — accuracy {acc*100:.1f}% ≥ {EVAL_THRESHOLD*100:.0f}%, "
          f"all novel-stack rows LOW/NONE")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--route", metavar="TASK", help="rank specialists for TASK")
    ap.add_argument("--lint", action="store_true", help="validate roster frontmatter")
    ap.add_argument("--eval", action="store_true", help="score the golden corpus (fail-closed)")
    ap.add_argument("--dir", metavar="PATH",
                    help="explicit agents directory (e.g. the seed repo's bare "
                         "agents/); default: walk up for .claude/agents/")
    args = ap.parse_args()

    if args.dir:
        adir = Path(args.dir)
        if not adir.is_dir():
            print(f"FATAL: --dir is not a directory: {adir}", file=sys.stderr)
            return 2
    else:
        adir = find_agents_dir()
    if adir is None:
        print("FATAL: no .claude/agents/ directory found by walking up from cwd "
              "or the script location (pass --dir to point at one).\n"
              "  If you are rooted in the SEED repo rather than a plant, that is "
              "expected — the seed ships no roster projection of its own, and a "
              "seed-rooted session can spawn no plant specialist. Re-enter rooted "
              "at the plant (delegation.harness-registration).", file=sys.stderr)
        return 2
    try:
        agents = load_agents(adir)
    except LintError as e:
        print(f"FATAL: {e}", file=sys.stderr)
        return 2

    if args.route is not None:
        return cmd_route(agents, args.route)
    if args.eval:
        try:
            return cmd_eval(agents, adir)
        except LintError as e:
            print(f"FATAL: {e}", file=sys.stderr)
            return 2
    return cmd_lint(agents)


if __name__ == "__main__":
    sys.exit(main())
