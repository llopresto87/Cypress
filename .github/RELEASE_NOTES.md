## 7.37.0 — the first move runs the router, and a session pays for a route once (2026-10-01)

The owner asked for fewer model-facing tokens, not for speed. One `--plan`
run already takes about 70 ms, so latency was never the cost. The cost was
text: Prime Agent injected the full route on every prompt, a route printed
the same facts several ways, and every session opened `docs/graph/index.md`
before it knew what the task needed. This release cuts that text where a
program can derive it, and keeps every pointer a model follows.

### What a plant gets

- **The FIRST MOVE routes the task line.** A session takes the router
  suggestion the host injected, or runs
  `python3 docs/graph/graph-lint.py --plan "<task>"`, reads the LOAD nodes
  through `graph-lint.py --show <id>...`, and acts on any `!` notice.
  `docs/graph/index.md` becomes the fallback map: a session opens it when the
  router fails, when a notice leaves the plan empty or wrong, or when the task
  explores the graph itself. The orchestrator's Turn 0, the
  `knowledge-graph` tier table, `_schema.md` and the docs map say the same.
- **Prime Agent keeps one route per session.** `install.sh prime-agent` now
  places the same `route-hook.py` and `status-hook.py` that Claude Code runs,
  byte for byte, under `.prime/agent/hooks/`. The two extensions pass the
  prompt, the session id and the session depth to that core and compose no
  text of their own. A node this session was already shown is named by id on
  one `seen:` line instead of being injected again. The status register and
  the code-anchor line arrive once after each session start, compaction,
  tree switch or refine. The overlay's `## Surfaced nodes` section, a set the
  model kept by hand, is gone.
- **Children and non-human turns are not routed.** A spawned child session
  (depth above 0) and a turn a person did not type (an agent message, a
  task notification, a harness digest) get no route and no status text, on
  every host that runs the core.
- **Route lines are compact and keep every path.** `--plan` prints one line
  per node with its file beside its id, a skip block, and the owner's
  `plant:` facts when all four are filled. Programs read `--plan-json`, one
  `cypress.plan/1` document bound to the prompt by its SHA-256. The hooks
  read only that document and render the same lines from it.
- **`--show` reads a node without its router keys.** It prints a header with
  every edge and leaf pointer resolved (`requires`, `peers`, `composes`,
  `delegates_to`, `artifacts`, `libraries`, `plant_knowledge`), then the body
  verbatim. It drops only router input, spawn settings and copies of the body.
- **The node router abstains instead of guessing.** It takes the first tier
  that hits: an exact node id in the task, a path the task names, a trigger
  phrase of two or more content words, then the word score with a floor of
  two confident terms. A strong tier that hits more than three nodes falls
  through. A task with no signal, or one too long to be a task line, loads
  nothing and gets a short notice that names the next step. Root is no longer
  forced into every plan.

### Measured

Model-facing tokens are cl100k counts from the round's records; each run
replays real sessions from the steward plant against the uncommitted tree.

- Follow-up prompts: 47 follow-ups across 22 real sessions fell from 36,402
  to 11,131 injected tokens (-69%).
- Five real prompts in one session: 5,885 to 2,306 tokens (-61%).
- First-move window of short sessions: Prime Agent 25,359 to 14,739 tokens
  (-42%, 15 sessions), Claude Code 56,189 to 32,418 (-42%, 9 sessions). This
  assumes a session no longer reads `index.md` first. On Prime Agent the
  saving holds while fewer than about 14% of short sessions still read it;
  before the change, 5 of 15 did.
- `--show` over the plant's 116 nodes saves about 216 tokens per opened node
  and keeps 651 of 651 pointers.
- Routing quality on a 74-row plant corpus: adversarial rows hit a forbidden
  node 2 times, down from 19, and 8 of 9 unknown-domain tasks now abstain,
  up from 1.

### Known limits

- A plain re-install keeps a plant's older `graph-lint.py`
  ([ADR-0014](docs/decisions/adr-0014-graft-reconciles-every-graph-engine.md)). The
  new hook then injects one line saying the engine lacks `--plan-json`, until
  `graft` brings the engine up.
- The FIRST MOVE now needs `python3`. A shell-less GitHub Copilot mode can
  only take the `index.md` fallback; Copilot is a frozen host and gets no
  adapter work.
- The hook waits up to 15 s for the router before it gives up and injects
  the pointer line alone.

### Decisions and checks

- [ADR-0024](docs/decisions/adr-0024-one-hook-core-per-session-residency.md):
  one Python hook core and per-session residency on Prime Agent; children and
  non-human turns are not routed. It supersedes ADR-0010 in part.
- [ADR-0025](docs/decisions/adr-0025-compact-route-lines-json-between-programs.md):
  compact route lines with every path, `--plan-json` between programs,
  `--show` for reading nodes.
- [ADR-0026](docs/decisions/adr-0026-node-router-ladder-and-gated-corpus.md):
  the tier ladder, the abstentions, and `graph-lint.py --eval` over
  `tests/graph-routes.golden.tsv`, gated per class on the `GRAPH_*` ratchets
  by `tests/graph-route-eval.sh` in `tests/run.sh`.
- [ADR-0027](docs/decisions/adr-0027-first-move-runs-the-router.md): the
  FIRST MOVE runs the router and `index.md` is the fallback map. It amends a
  consequence of ADR-0017 in part.
- SPEC-0001, SPEC-0002, SPEC-0003 and SPEC-0005 carry the new contracts.
  `tests/test_graph_lint.py`, `tests/test-prompt-hooks.sh`,
  `tests/test-full-install.sh` and `tests/test-install-placement.sh` hold
  them. `tools/code-anchor.py` no longer counts `__pycache__/`, `*.pyc` or
  installer backup files as code.

### How plants pick this up

- **A new plant** gets all of it from `install.sh`.
- **An existing plant** needs `graft`: it brings the engine, the kernel's
  FIRST MOVE and, on Prime Agent, the hook core under `.prime/agent/hooks/`.
  A plant that re-installs an adapter without `graft` gets the one-line
  engine notice above in place of a route.
