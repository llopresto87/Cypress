# Plan-of-record — CYPRESS 6.0.0: the seed becomes a pure graph

**Directive (user, verbatim intent):** everything that CAN be folded into
the graph so that knowledge activates progressively MUST be moved into the
graph — methods, how-to, why. No large always-loaded files; a dynamic
system that selects what is needed at any moment.

**Status:** EXECUTED (2026-07-22, shipped as 6.0.0 — see CHANGELOG.md).
All gates green: `bash tests/run.sh` + `pytest tests/` (54) + four-tool
scratch install lints clean (49 machinery nodes). Deviations from plan:
operating-principles had 27 principles (not 23), split at 12/7/8
(`method.engineering-posture` §1–§12, `design-posture` §13–§19,
`stewardship-posture` §20–§27); `core/operating-principles.md` kept as a
tombstone rather than deleted (deletion needs explicit user confirmation).

---

## Target architecture

### In a grown plant

- `docs/graph/` is the ONLY knowledge system. It now contains, besides
  project knowledge, the seed machinery as first-class routable nodes:
  - `docs/graph/protocols/<name>.md` — kind `protocol` (15 nodes)
  - `docs/graph/skills/<name>.md` — kind `skill` (13 nodes; flattened
    from the seed's `skills/<name>/SKILL.md`)
  - `docs/graph/agents/<file>.md` — kind `agent` (16 nodes; id from
    frontmatter `name:`)
  - `docs/graph/method/<name>.md` — kind `method`: relocated kernel
    depth (`method.tiers`, `method.delegation`) and the split
    `operating-principles` posture nodes
  - `docs/graph/templates/**` — Tier-3 **artifacts**, not nodes (blank
    forms have no routable knowledge; machinery nodes point at them via
    `artifacts:`)
- All machinery nodes carry full node frontmatter **plus** `origin: seed`
  (graft's ownership marker) and are routed from `docs/graph/index.md`
  like any other node.
- The kernel (`CLAUDE.md`/`AGENTS.md`) shrinks to a **bootstrap**
  (budget: 8 000 bytes): identity ¶, FIRST MOVE (open the router),
  compressed tier table, the eight rules as one-line anchors
  (`### 3.1`–`### 3.8` headings preserved — plants cite them) each
  pointing to the node that now owns its full statement, §4 boundaries
  (safety cannot depend on routing), delegation ¶ referencing
  `graph-session-bootstrap.md`, and a compact roster line naming every
  agent in backticks (lint invariant). Nothing else.
- Harness-mandated locations become **projections** (generated copies
  with a banner, or symlinks in `--symlink` mode):
  - `.claude/agents/*.md` ← `docs/graph/agents/` (spawnability)
  - `.claude/skills/<name>/SKILL.md` ← `docs/graph/skills/<name>.md`
  - same pattern for opencode/codex; Copilot keeps its transform.
  - `.claude/protocols/`, `.claude/templates/`, `.claude/core/` are
    **gone** — protocols/templates/method are graph-only.
- Executable tools stay Tier-3 leaves: `graph-lint.py`, `spec-lint.py`
  in `docs/graph/`; `agent-lint.py`, hooks in `.claude/` (harness-side).

### Rule relocation map (one home per fact)

| Kernel anchor | Full statement moves to (owns `rule.<x>`) |
|---|---|
| §3.1 spec | `protocol.specify` |
| §3.2 knowledge | `skill.context-router` (loading) — authoring sentence links `skill.knowledge-graph` |
| §3.3 grill | `protocol.grill` |
| §3.4 test-first | `protocol.test-first` |
| §3.5 verify | `protocol.verify` |
| §3.6 deliver | `protocol.deliver` |
| §3.7 canonize | `protocol.canonize` |
| §3.8 toolcraft | `protocol.toolcraft` |
| §0 tier depth/edges | `method.tiers` |
| §1 roster/routing/delegation depth | `method.delegation` |
| §2 protocol table | router `index.md` "Method" section |
| `core/operating-principles.md` (24 KB) | split into 2–4 `method.*` nodes |

### Frontmatter contract for machinery nodes

```yaml
---
id: protocol.test-first        # <kind>.<basename> (agents: <kind>.<name:>)
tier: 2
kind: protocol                 # protocol | skill | agent | method
origin: seed                   # graft ownership marker
title: one line
owns:
  - rule.test-first            # where applicable per the map above
  - test-first.<fact>
requires:                      # other node ids; minimal, acyclic
peers:
artifacts:                     # e.g. templates/grill.template.md
load_when:                     # agents: keep routing_triggers too (harness)
est_tokens: <honest>
---
```

Agents keep their existing harness keys (`name`, `description`, `tools`,
`model`, `routing_triggers`, `can_delegate`, …) and add the node keys.
Projections may strip node-only keys.

## Seed-repo layout: unchanged

`protocols/ skills/ agents/ templates/ core/` stay where they are in the
seed repo; `install.sh` maps them into `docs/graph/` on the plant.
`core/operating-principles.md` is deleted after its content moves to
`core/method/` (seed-side home of `method.*` nodes, installed to
`docs/graph/method/`). All prose references use **plant-relative** paths
(`docs/graph/protocols/x.md`), replacing `.protocols/x.md`,
`.skills/x/SKILL.md`, `.templates/…`, `.core/operating-principles.md §N`,
`.agents/…`.

## Phases

1. **Schema + lint.** `_schema.md` + `graph-lint.py`: machinery kinds,
   `origin:` key, scan `docs/graph/{protocols,skills,agents,method}/`,
   per-kind required-key profiles, machinery routable via `--plan`.
   Extend `tests/test_graph_lint.py`. Router `index.md` template gains a
   pre-filled **Method** section (the reborn §2 table + tier row hints).
2. **Frontmatter sweep** (parallel workers): protocols (15), skills
   (13), agents (16) per the contract above; path rewrites inside each
   file in the same pass.
3. **Kernel + method nodes.** Rewrite `core/AGENTS.md` (≤ 8 000 B).
   Author `core/method/tiers.md`, `core/method/delegation.md`; split
   `core/operating-principles.md` into `core/method/*.md` posture nodes;
   relocate the eight rule statements into their owning nodes; rewrite
   all `.core/operating-principles.md §N` citations.
4. **Installer + seed tests.** `install.sh`: machinery → `docs/graph/`,
   agent/skill projections, drop `.claude/{protocols,templates,core}`.
   `tests/seed-lint.py`: budget 8 000, machinery-frontmatter check,
   keep roster/anchor/canonical-block/agnosticism checks. Update the 5
   shell suites' expected paths.
5. **Meta-protocols + release.** `grow`/`graft`/`harvest` path + model
   updates; graft gains a 5.x→6.0 layout-migration section (old tool-dir
   machinery folds into the graph; deletions steward-confirmed).
   Re-sync `graph-session-bootstrap.md` canonical block (byte-identical
   in 4 brief templates). `manifest.json` → 6.0.0; README; CHANGELOG.
6. **Gates.** `bash tests/run.sh` green; a scratch full install
   inspected; deliver.

## Invariants held throughout

- One home per fact — every relocation is a move, never a copy.
- Kernel keeps: `### 3.1`–`### 3.8` headings, every agent name in
  backticks, the string `graph-session-bootstrap.md`.
- Append-only: CHANGELOG, docs/decisions.
- No production/plant identifiers enter the seed (agnosticism lint).
- `harvest`/`graft` stay user-sovereign.
