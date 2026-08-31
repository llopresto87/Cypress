# Working on the CYPRESS seed (this repo)

This repository IS the seed — not a grown plant. `core/AGENTS.md` here is
the product shipped to target projects, not this repo's instructions.
There is no `docs/graph/` here; these notes replace it.

## Gates (run before claiming anything works)

```
bash tests/run.sh        # 9 shell suites + agent-lint (lint/eval) + graph/agent-lint regressions + seed-lint.py + legal-lint.py
```

`tests/seed-lint.py` is one-home-per-fact for the seed's own meta-facts:
roster/frontmatter/manifest/README consistency, the delegator invariant,
numeric claims, the kernel size budget (8 000 bytes), stable §3.1–§3.8
anchors, machinery-node frontmatter (every protocol/skill/agent/method
file is a graph node: id, kind, origin: seed, owns, load_when,
est_tokens; owns globally unique; the eight `rule.*` keys in exactly
their mapped homes), canonical-block byte-identity in the brief
templates, and the per-session instruction budget of the integrations.

## Canonical homes (edit the home, never a copy)

- The seed IS a graph (6.0.0): every protocol, skill, agent, and
  `core/method/` file is a routable node installed into a plant's
  `docs/graph/{protocols,skills,agents,method}/`; the kernel is a
  bootstrap of anchors and pointers.
- Each of the eight rules → its owning node's `rule.*` fact
  (3.1 specify, 3.2 context-router, 3.3 grill, 3.4 test-first,
  3.5 verify, 3.6 deliver, 3.7 canonize, 3.8 toolcraft); the kernel
  keeps only the one-line §3.x anchors.
- Tier depth → `core/method/tiers.md`; roster/routing/brief depth →
  `core/method/delegation.md`; engineering/design/stewardship posture →
  `core/method/{engineering,design,stewardship}-posture.md`
  (`core/operating-principles.md` is a tombstone).
- Graph-session discipline → `templates/prompts/graph-session-bootstrap.md`
  (brief templates embed it byte-identical; lint enforces sync).
- Handback contract → `templates/prompts/handback-payload.md`
  (agent files carry a 3-sentence pointer, never the full spec).
- Close-out flow → `protocols/canonize.md` (single librarian spawn;
  `toolcraft.md` owns only the durable-tool doctrine).
- Failure discipline → `protocols/recover.md` (classify, one move per
  class, three attempts, escalate).
- Spec-contract coverage → `templates/knowledge-graph/spec-lint.py`
  (tested by `tests/test-spec-lint.sh`).
- Roster ground truth → `agents/*.md` frontmatter (manifest, kernel
  roster line, and README follow it; lint checks).

## Conventions

- Behavior change ⇒ bump `manifest.json` version + `CHANGELOG.md` entry
  (append-only; supersede, don't rewrite).
- The kernel is loaded on every session of every plant: additions there
  need to earn ~2k-token-per-session rent, and lint fails past budget.
  Depth belongs in a machinery node, never the kernel.
- Append-only artifacts: CHANGELOG.md, docs/decisions/. Everything else:
  integrate, don't bolt on.
- `harvest`/`graft` are user-sovereign; nothing in the seed may trigger
  them automatically.
