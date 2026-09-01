#!/usr/bin/env python3
"""seed-lint: one-home-per-fact enforcement for the seed's OWN meta-facts.

graph-lint.py guards a grown plant's docs/graph/; nothing guarded the
seed's meta-documentation, and its duplicated facts drifted (README said
5 coordinators and a 9 KB kernel while frontmatter said six and 27 KB).
This linter makes that failure class deterministic to catch:

  1. roster: agents/ frontmatter <-> manifest.json <-> kernel §1 table
  2. delegator invariant: can_delegate == (Task in tools); allowlists resolve
  3. numeric claims: "N-agent team" and "N coordinators" match reality
  4. kernel budget: core/AGENTS.md stays under KERNEL_BUDGET bytes
  5. kernel anchors: §3.1–§3.8 headings exist (cited seed-wide)
  6. manifest paths: every cataloged file exists on disk
  7. canonical bootstrap block exists and the kernel references it
  8. harness registration: the "installed but not spawnable" rule has one
     home (method.delegation) and every dispatch/install surface points at it
  9. corpus agnosticism floor: no leaked host-IP literal or pinned CVE, and
     no dangling corpus/template cross-reference, in the shipped prose
     (objective leaks only — project names and stack fingerprints stay human
     judgment, since the seed cannot enumerate plant names without naming them)

Dependency-free; exit 0 clean, 1 with findings.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KERNEL = ROOT / "core" / "AGENTS.md"
KERNEL_BUDGET = 8_000  # bytes; 6.0.0 shrank the kernel to a bootstrap —
                       # depth lives in graph machinery nodes, not here

# 6.0.0: the eight rules' full statements live in (only) these machinery
# nodes; the kernel keeps one-line anchors. Each rule fact-key must be
# owned by exactly this file and no other.
RULE_HOMES = {
    "rule.spec": "protocols/specify.md",
    "rule.knowledge": "skills/context-router/SKILL.md",
    "rule.grill": "protocols/grill.md",
    "rule.test-first": "protocols/test-first.md",
    "rule.verify": "protocols/verify.md",
    "rule.deliver": "protocols/deliver.md",
    "rule.canonize": "protocols/canonize.md",
    "rule.toolcraft": "protocols/toolcraft.md",
}
# 6.4.0: "installed but not spawnable" — a harness registers agent types when a
# SESSION STARTS, so the session that installs a roster cannot spawn it. The rule
# has one home and a fixed set of referrers: every surface that dispatches a
# specialist by name or installs the projection they come from. A referrer that
# drops the pointer silently re-opens the trap, so the fact key IS the
# machine-checkable pointer (the same referenced-never-paraphrased discipline the
# bootstrap-block check enforces).
REGISTRATION_FACT = "delegation.harness-registration"
REGISTRATION_HOME = "core/method/delegation.md"
REGISTRATION_REFERRERS = (
    # protocols that install the projection and/or dispatch by name
    "protocols/grow.md",
    "protocols/graft.md",
    "protocols/from-scratch.md",
    "protocols/initialize.md",
    "protocols/specify.md",
    "protocols/canonize.md",
    "protocols/recover.md",      # the node a failed dispatch actually lands on
    "protocols/deliver.md",      # the gate that must see a declared emulation
    # agents that install it or route to it
    "agents/00-orchestrator.md",
    "agents/growth-orchestrator.md",
    "agents/seed-installer.md",
    # the handback that carries the declaration
    "templates/prompts/handback-payload.md",
    # entry surfaces and installers
    "INSTALL_PROMPT.md",
    "GRAFT_PROMPT.md",
    "INSTALL.md",
    "README.md",
    "install.sh",
    # per-host docs that own the enumeration mechanism, and the router that
    # names specialists off disk rather than out of the session registry
    "integrations/claude-code/README.md",
    "integrations/claude-code/agent-lint.py",
    "integrations/opencode/README.md",
    "integrations/codex/README.md",
    "integrations/github-copilot/README.md",
    "integrations/prime-agent/README.md",
)
WORD_NUMS = {"two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
             "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11,
             "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
             "sixteen": 16, "seventeen": 17}

findings: list[str] = []


def fail(msg: str) -> None:
    findings.append(msg)


def parse_frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    m = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
    if not m:
        fail(f"{path}: no frontmatter block")
        return {}
    fm: dict = {"_body": text[m.end():]}
    current_list = None
    for line in m.group(1).splitlines():
        if re.match(r"^\s+-\s+", line) and current_list is not None:
            fm[current_list].append(line.split("-", 1)[1].strip().strip('"'))
            continue
        kv = re.match(r"^([A-Za-z_]+):\s*(.*)$", line)
        if kv:
            key, val = kv.group(1), kv.group(2).strip()
            if val == "":
                fm[key] = []
                current_list = key
            else:
                fm[key] = val
                current_list = None
    return fm


def check() -> None:
    # -- gather ground truth from agents/ frontmatter -------------------
    agent_files = sorted(p for p in (ROOT / "agents").glob("*.md"))
    agents = {}
    for p in agent_files:
        fm = parse_frontmatter(p)
        name = fm.get("name")
        if not name:
            fail(f"{p}: frontmatter has no name")
            continue
        agents[name] = {"path": p, "fm": fm}

    delegators = set()
    for name, a in agents.items():
        fm = a["fm"]
        tools = fm.get("tools", "")
        has_task = "Task" in tools if isinstance(tools, str) else "Task" in tools
        declares = str(fm.get("can_delegate", "false")).lower() == "true"
        if has_task != declares:
            fail(f"{a['path']}: can_delegate={declares} but Task-in-tools={has_task}")
        if declares:
            delegators.add(name)
            if "max_spawn_depth" not in fm:
                fail(f"{a['path']}: delegator without max_spawn_depth")
            for target in fm.get("delegates_to", []):
                if target not in agents:
                    fail(f"{a['path']}: delegates_to unknown agent '{target}'")

    # -- manifest <-> disk ----------------------------------------------
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    manifest_agents = {a["name"] for a in manifest.get("agents", [])}
    for name in agents:
        if name not in manifest_agents:
            fail(f"manifest.json: agents[] is missing '{name}'")
    for name in manifest_agents:
        if name not in agents:
            fail(f"manifest.json: agents[] lists '{name}' with no file in agents/")
    for section in ("agents", "protocols", "skills"):
        for entry in manifest.get(section, []):
            if not (ROOT / entry["file"]).exists():
                fail(f"manifest.json: {section} file does not exist: {entry['file']}")
    for entry in manifest.get("templates", []):
        if not (ROOT / entry["file"]).exists():
            fail(f"manifest.json: template file does not exist: {entry['file']}")

    # -- version single source: manifest == CHANGELOG top entry ---------
    # The version is the repo's most fundamental state fact; the CLAUDE.md
    # convention "behavior change ⇒ bump manifest + CHANGELOG" is only real
    # if the two cannot silently diverge.
    mver = manifest.get("version", "")
    changelog_text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    cm = re.search(r"^##\s+(\d+\.\d+\.\d+)\b", changelog_text, re.MULTILINE)
    if not cm:
        fail("CHANGELOG.md: no '## X.Y.Z' version heading found")
    elif cm.group(1) != mver:
        fail(f"version drift: manifest.json is {mver!r} but the top CHANGELOG "
             f"entry is {cm.group(1)!r} — bump both together")

    # -- kernel roster table, anchors, budget, canonical reference ------
    kernel_text = KERNEL.read_text(encoding="utf-8")
    for name in agents:
        if f"`{name}`" not in kernel_text:
            fail(f"core/AGENTS.md: §1 roster does not mention `{name}`")
    for n in range(1, 9):
        if not re.search(rf"^### 3\.{n} ", kernel_text, re.MULTILINE):
            fail(f"core/AGENTS.md: stable anchor §3.{n} heading is missing")
    size = KERNEL.stat().st_size
    if size > KERNEL_BUDGET:
        fail(f"core/AGENTS.md: {size} bytes exceeds the {KERNEL_BUDGET}-byte budget "
             f"(every session of every plant pays this file)")
    if "graph-session-bootstrap.md" not in kernel_text:
        fail("core/AGENTS.md: does not reference the canonical "
             "templates/prompts/graph-session-bootstrap.md block")
    canonical = ROOT / "templates/prompts/graph-session-bootstrap.md"
    if not canonical.exists():
        fail("templates/prompts/graph-session-bootstrap.md: canonical block missing")
    else:
        # the fenced block is the one home; embedding templates must carry
        # it byte-identical (the deliberate runtime-brief exception)
        m = re.search(r"```\n(GRAPH DISCIPLINE.*?)```", canonical.read_text(encoding="utf-8"), re.DOTALL)
        if not m:
            fail(f"{canonical}: no fenced GRAPH DISCIPLINE block found")
        else:
            block = m.group(1)
            for rel in ("templates/prompts/investigation-brief.md",
                        "templates/prompts/node-authoring-brief.md",
                        "templates/prompts/growth-scout-brief.md",
                        "templates/prompts/growth-author-brief.md",
                        "templates/prompts/clean-context-validation-brief.md"):
                p = ROOT / rel
                if not p.exists():
                    fail(f"{rel}: embedding template missing")
                elif block not in p.read_text(encoding="utf-8"):
                    fail(f"{rel}: embedded GRAPH DISCIPLINE block has drifted from "
                         f"the canonical copy in {canonical.name} — sync it verbatim")

    # -- spawn tracing contract: every delegation brief carries the
    # caller-minted spawn_id and the handback payload echoes it
    # (delegation.tracing — the correlation chain only works if no
    # template drops the field)
    for rel in ("templates/prompts/handback-payload.md",
                "templates/prompts/investigation-brief.md",
                "templates/prompts/node-authoring-brief.md",
                "templates/prompts/growth-scout-brief.md",
                "templates/prompts/growth-author-brief.md",
                "templates/prompts/clean-context-validation-brief.md"):
        p = ROOT / rel
        if p.exists() and "spawn_id" not in p.read_text(encoding="utf-8"):
            fail(f"{rel}: no spawn_id field — the delegation trace chain "
                 f"(delegation.tracing) breaks at this template")

    # -- machinery nodes: the seed's method surface is graph content ----
    # Every protocol, skill, agent, and method file installs into a
    # plant's docs/graph/ as a routable node; its frontmatter must carry
    # the node contract, owns keys must be globally unique, and the
    # eight rule fact-keys must live in exactly their mapped homes.
    machinery: list[tuple[Path, str, str | None]] = []   # (path, kind, expected-name)
    for p in sorted((ROOT / "protocols").glob("*.md")):
        machinery.append((p, "protocol", p.stem))
    for d in sorted((ROOT / "skills").iterdir()):
        if (d / "SKILL.md").exists():
            machinery.append((d / "SKILL.md", "skill", d.name))
    for p in sorted((ROOT / "agents").glob("*.md")):
        machinery.append((p, "agent", None))      # agents: name from frontmatter
    for p in sorted((ROOT / "core" / "method").glob("*.md")):
        machinery.append((p, "method", p.stem))

    owns_home: dict[str, Path] = {}
    command_protocols: set[str] = set()
    node_ids: set[str] = set()
    requires_adj: dict[str, list[str]] = {}
    edge_refs: list[tuple[Path, str, str, str]] = []   # (rel, src-id, edge-type, target-id)
    for p, kind, expected in machinery:
        fm = parse_frontmatter(p)
        if not fm:
            continue
        rel = p.relative_to(ROOT)
        name = expected if expected is not None else fm.get("name")
        want_id = f"{kind}.{name}"
        if fm.get("id") != want_id:
            fail(f"{rel}: id must be {want_id!r} (got {fm.get('id')!r})")
        if fm.get("kind") != kind:
            fail(f"{rel}: kind must be {kind!r}")
        if str(fm.get("tier")) != "2":
            fail(f"{rel}: tier must be 2")
        if fm.get("origin") != "seed":
            fail(f"{rel}: origin must be 'seed' (graft ownership marker)")
        for key in ("title", "owns", "est_tokens"):
            if not fm.get(key):
                fail(f"{rel}: machinery node missing {key!r}")
        if kind != "agent" and not fm.get("load_when"):
            fail(f"{rel}: machinery node missing 'load_when'")
        if kind == "agent" and not fm.get("routing_triggers"):
            fail(f"{rel}: agent node needs routing_triggers (its load_when source)")
        est = str(fm.get("est_tokens", ""))
        if not est.isdigit():
            fail(f"{rel}: est_tokens must be an integer (got {est!r})")
        else:
            # Every machinery node installs into a plant, where graph-lint.py's
            # check_budget enforces est_tokens within 2x of the measured body
            # (words * BODY_TOKENS_PER_WORD). The seed never checked it, so it
            # could ship a node that fails the very linter it also ships.
            # Mirrored here with the same metric.
            body = p.read_text(encoding="utf-8").split("\n---\n", 1)[-1]
            measured = int(len(body.split()) * 1.35)
            declared = int(est)
            if measured > 2 * declared or declared > 2 * max(measured, 1):
                fail(f"{rel}: est_tokens={declared} but body measures ~{measured} "
                     f"— graph-lint.py would reject this node once installed "
                     f"(must be within 2x)")
        for fact in fm.get("owns", []) or []:
            if fact in owns_home:
                fail(f"{rel}: fact-key {fact!r} already owned by "
                     f"{owns_home[fact].relative_to(ROOT)} — one home per fact")
            owns_home[fact] = p
        # `command: true` marks a protocol as a user-facing slash command;
        # install.sh generates every harness's command file from this field
        # (one home, projected — no authored command tree). It is protocol-only.
        cmd = fm.get("command")
        if kind == "protocol":
            if cmd == "true":
                command_protocols.add(name)
        elif cmd is not None:
            fail(f"{rel}: 'command:' is a protocol-only field (found on a {kind} node)")
        # Collect the graph edges for the in-source graph validation below.
        node_ids.add(want_id)
        req = fm.get("requires") or []
        requires_adj[want_id] = list(req)
        for target in req:
            edge_refs.append((rel, want_id, "requires", target))
        for target in fm.get("peers", []) or []:
            edge_refs.append((rel, want_id, "peers", target))
    for rule, home in RULE_HOMES.items():
        owner = owns_home.get(rule)
        if owner is None:
            fail(f"{home}: does not own {rule!r} — the kernel anchor points at it")
        elif owner != ROOT / home:
            fail(f"{rule}: owned by {owner.relative_to(ROOT)}, expected {home}")

    # -- harness registration: one home, and every referrer still points ----
    reg_owner = owns_home.get(REGISTRATION_FACT)
    if reg_owner is None:
        fail(f"{REGISTRATION_HOME}: does not own {REGISTRATION_FACT!r} — the "
             f"install and dispatch surfaces all point at it")
    elif reg_owner != ROOT / REGISTRATION_HOME:
        fail(f"{REGISTRATION_FACT}: owned by {reg_owner.relative_to(ROOT)}, "
             f"expected {REGISTRATION_HOME}")
    for rel in REGISTRATION_REFERRERS:
        p = ROOT / rel
        if not p.exists():
            fail(f"{rel}: registration referrer is missing from disk")
        elif REGISTRATION_FACT not in p.read_text(encoding="utf-8"):
            fail(f"{rel}: dispatches specialists by name (or installs the "
                 f"projection they come from) but never points at "
                 f"{REGISTRATION_FACT!r} — the 'installed but not spawnable' "
                 f"trap re-opens silently")

    # -- command roster: user-sovereign protocols are never slash commands --
    # Slash commands are generated projections of the protocol nodes that
    # declare `command: true`. The cross-project meta-loop (graft/grow/harvest)
    # is user-sovereign, and the durable-tool doctrine (toolcraft) folds into
    # canonize — none may become a routine slash command on any harness. This
    # guards that invariant; it does not re-declare the roster (the nodes do).
    for sovereign in ("graft", "grow", "harvest", "toolcraft"):
        if sovereign in command_protocols:
            fail(f"protocols/{sovereign}.md: must not declare 'command: true' — "
                 f"{sovereign} is user-sovereign / canonize-folded, a slash command on no harness")
    if not command_protocols:
        fail("no protocol declares 'command: true' — the slash-command surface would be empty")

    # -- machinery graph edges: resolve + acyclic (the seed IS a graph) -----
    # In-source validation of the node graph the seed installs: every
    # requires:/peers: target resolves to a real machinery node, and the
    # requires: relation is acyclic. graph-lint.py enforces this too, but only
    # after an install reconstitutes docs/graph/; asserting it here makes the
    # seed a validated navigable graph at source, and names the failing seed
    # file directly instead of surfacing late as an install-test side effect.
    for rel, src, etype, target in edge_refs:
        if target not in node_ids:
            fail(f"{rel}: {etype} → unknown machinery node {target!r}")
    WHITE, GREY, BLACK = 0, 1, 2
    colour = {n: WHITE for n in requires_adj}

    def _visit(n: str, stack: list[str]) -> None:
        colour[n] = GREY
        for m in requires_adj.get(n, []):
            if m not in colour:          # unresolved target already reported
                continue
            if colour[m] == GREY:
                cyc = " → ".join(stack[stack.index(m):] + [m])
                fail(f"requires cycle in machinery graph: {cyc}")
            elif colour[m] == WHITE:
                _visit(m, stack + [m])
        colour[n] = BLACK

    for n in list(requires_adj):
        if colour[n] == WHITE:
            _visit(n, [n])

    # -- per-session instruction budget (every always-loaded file) ------
    # A tool that loads more than the kernel every session re-creates the
    # tax this lint exists to prevent. Budget covers the SUM of a tool's
    # always-loaded instruction files.
    SESSION_BUDGET = 10_000  # bytes; bootstrap kernel (~7 KB) + small overlay headroom
    oc = ROOT / "integrations/opencode/opencode.json"
    if oc.exists():
        cfg = json.loads(oc.read_text(encoding="utf-8"))
        # opencode auto-loads the project's AGENTS.md (which IS the kernel), so
        # the always-loaded total starts there and grows with anything the
        # config declares on top. Re-declaring AGENTS.md in `instructions`
        # would load the kernel twice per session — the exact tax this budget
        # exists to prevent, so it fails as a duplicate rather than as size.
        instructions = cfg.get("instructions", [])
        total = KERNEL.stat().st_size
        for rel in instructions:
            if rel in ("AGENTS.md", "CLAUDE.md"):
                fail(f"opencode.json: instructions re-declares {rel!r}, which "
                     f"opencode already auto-loads — the kernel would load twice")
                continue
            p = ROOT / rel
            if not p.exists():
                fail(f"opencode.json: instructions file not found: {rel}")
            else:
                total += p.stat().st_size
        if total > SESSION_BUDGET:
            fail(f"opencode.json: always-loaded instructions total {total} bytes "
                 f"> {SESSION_BUDGET} budget (auto-loaded AGENTS.md + {instructions})")

        # -- opencode config validity (upstream contract, verified 2026-08-05) --
        # The live schema at https://opencode.ai/config.json sets
        # additionalProperties: false, so an unknown key is a REJECTED config,
        # not a harmless hint — the seed shipped `agents`/`commands`/`skills`
        # directory keys that no release ever accepted, against a $schema URL
        # that now 404s. Keys are pinned here rather than fetched: a gate that
        # needs the network is a gate that fails offline.
        OC_SCHEMA_URL = "https://opencode.ai/config.json"
        OC_VALID_KEYS = {
            "$schema", "agent", "attachment", "autoupdate", "command",
            "compaction", "default_agent", "disabled_providers",
            "enabled_providers", "enterprise", "experimental", "formatter",
            "instructions", "logLevel", "lsp", "mcp", "model", "permission",
            "plugin", "provider", "references", "server", "share", "shell",
            "skills", "small_model", "snapshot", "subagent_depth",
            "tool_output", "tools", "username", "watcher",
        }
        if cfg.get("$schema") != OC_SCHEMA_URL:
            fail(f"opencode.json: $schema must be {OC_SCHEMA_URL!r} "
                 f"(got {cfg.get('$schema')!r}; the old config-schema.json URL 404s)")
        for key in sorted(set(cfg) - OC_VALID_KEYS):
            fail(f"opencode.json: {key!r} is not a key in opencode's config "
                 f"schema, which sets additionalProperties:false — the whole "
                 f"config is rejected, not just this key")
        # The seed's deepest legal delegation chain must be executable on
        # opencode. Its subagent_depth defaults to 1 ("prevents subagents from
        # launching subagents"), which silently caps every coordinator.
        depths = [int(a["fm"]["max_spawn_depth"]) for a in agents.values()
                  if str(a["fm"].get("max_spawn_depth", "")).isdigit()]
        if depths and cfg.get("subagent_depth") != max(depths):
            fail(f"opencode.json: subagent_depth={cfg.get('subagent_depth')!r} "
                 f"but the roster's deepest max_spawn_depth is {max(depths)} — "
                 f"the seed's delegation topology would be capped on opencode")

    # -- numeric claims in prose ----------------------------------------
    def num(tok: str) -> int:
        return int(tok) if tok.isdigit() else WORD_NUMS[tok.lower()]

    n_skills = sum(1 for _, k, _ in machinery if k == "skill")
    word_alt = "|".join(WORD_NUMS)  # word-number alternates for the count regexes
    manifest_version = json.loads(
        (ROOT / "manifest.json").read_text(encoding="utf-8"))["version"]
    # Every shipped prose surface, including the integration READMEs and the
    # manifest — the declarative rim where roster/skill counts drift (the
    # "eight skills" / phantom-command-home class) if left unscanned.
    prose_files = ["README.md", "core/AGENTS.md", "INSTALL.md", "manifest.json"]
    prose_files += sorted(str(p.relative_to(ROOT))
                          for p in ROOT.glob("integrations/*/README.md"))
    # the companion documentation tree drifted a whole release once
    # (17 agents, no ui-ux-designer) because no gate ever read it
    prose_files += ["DOCUMENTATION.md"]
    prose_files += sorted(str(p.relative_to(ROOT))
                          for p in ROOT.glob("documentation/*.md"))
    prose = {p: (ROOT / p).read_text(encoding="utf-8")
             for p in prose_files if (ROOT / p).exists()}
    for path, text in prose.items():
        for m in re.finditer(rf"\b(\d+|{word_alt})[- ]agent team\b", text, re.I):
            if num(m.group(1)) != len(agents):
                fail(f"{path}: claims a {m.group(1)}-agent team; agents/ has {len(agents)}")
        # same fact, second phrasing — README's layout block said "17
        # specialist agents" and DOCUMENTATION.md "17 named specialist
        # agents" for a release while README line 40 said 18; up to two
        # qualifier words are allowed between the number and the noun
        for m in re.finditer(
                rf"\b(\d+|{word_alt})\s+(?:[a-z-]+\s+){{0,2}}specialist agents\b",
                text, re.I):
            if num(m.group(1)) != len(agents):
                fail(f"{path}: claims {m.group(0)!r}; "
                     f"agents/ has {len(agents)}")
        # the documented-version pins drifted a whole release unnoticed:
        # "Version documented: 6.8.0" / "(version 6.8.0)" vs manifest
        for m in re.finditer(r"[Vv]ersion(?: documented)?[:*\s]+\**(\d+\.\d+\.\d+)",
                             text):
            if path in ("DOCUMENTATION.md", "documentation/README.md") \
                    and m.group(1) != manifest_version:
                fail(f"{path}: documents version {m.group(1)}; "
                     f"manifest.json is {manifest_version}")
        for m in re.finditer(rf"\b(\d+|{word_alt})\s+(?:opus\s+)?coordinator",
                             text, re.I):
            if num(m.group(1)) != len(delegators):
                fail(f"{path}: claims {m.group(1)} coordinators; frontmatter has "
                     f"{len(delegators)}: {sorted(delegators)}")
        for m in re.finditer(rf"\b(\d+|{word_alt})\s+skills\b", text, re.I):
            if num(m.group(1)) != n_skills:
                fail(f"{path}: claims {m.group(1)} skills; skills/ has {n_skills}")

    # -- corpus agnosticism + cross-reference scan (mechanical floor) ----
    # Catches the OBJECTIVE plant-identifier leak class the harvest
    # agnosticism gate promises — a real host IP, a pinned CVE, a dangling
    # corpus/template link — over the seed's shipped prose. Subtler
    # fingerprints (a project name, a stack combo) remain human judgment:
    # the seed cannot hardcode plant names to blocklist without itself
    # leaking them. Loopback / unspecified / documentation IPs are allowed.
    agn_roots = ("core", "agents", "protocols", "skills", "templates",
                 "library-corpus", "legal-corpus", "tool-corpus",
                 "agent-corpus", "skill-corpus")
    ip_ok = {"127.0.0.1", "0.0.0.0", "255.255.255.255"}
    ip_re = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
    cve_re = re.compile(r"\bCVE-\d{4}-\d+\b")
    ref_re = re.compile(r"\b(?:library-corpus|legal-corpus|tool-corpus|"
                        r"agent-corpus|skill-corpus|templates)/[A-Za-z0-9_./-]+\.md\b")
    scan = [p for r in agn_roots for p in (ROOT / r).rglob("*.md")]
    scan += [ROOT / f for f in ("manifest.json", "README.md", "CHANGELOG.md")
             if (ROOT / f).exists()]
    for p in scan:
        text = p.read_text(encoding="utf-8")
        rel = p.relative_to(ROOT)
        for ip in ip_re.findall(text):
            if ip in ip_ok or ip.startswith(("192.0.2.", "198.51.100.", "203.0.113.")):
                continue
            fail(f"{rel}: leaked host-IP literal '{ip}' — agnosticism gate "
                 f"(use a <host> placeholder, not a real address)")
        for cve in cve_re.findall(text):
            fail(f"{rel}: pinned advisory '{cve}' — durability gate "
                 f"(belongs in a plant's docs, never the seed)")
        for ref in ref_re.findall(text):
            if "<" in ref or "*" in ref or "{" in ref:
                continue
            if not (ROOT / ref).exists():
                fail(f"{rel}: dangling corpus/template reference '{ref}'")


def main() -> int:
    check()
    if findings:
        print(f"seed lint: FAIL ({len(findings)} finding(s))")
        for f in findings:
            print(f"  - {f}")
        return 1
    print("seed lint: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
