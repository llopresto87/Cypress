## 7.32.0 — settled facts, a code anchor read once per session, and graft's mechanical steps as tools (2026-09-28)

A plant was grafted to 7.31.0, and what that graft had to work out by hand
comes back here as tools and recorded facts. The owner set the rule for the
round: everything the seed ships is for the plants it grows, and where a model
would otherwise work something out, the seed hands it the answer. The design
latitude was simple: each ratified item got the smallest design that met it,
and anything outside the items went to the question file.

**A fact the graph states is settled (ADR-0018).** A session uses it and does
not re-derive or re-check it. Only a fact about the plant's own code can go
stale, and only when that code moved. The kernel's §3.2 says so in two
sentences, `rule.knowledge` in `skill.context-router` holds the full rule, and
step 4 of the worker bootstrap block carries a worker's form of it, because a
worker starts clean. Grow's completeness contract now names its purpose: it
establishes the plant's facts so that no later session has to. The seed's
`manifest.json` records the rule as a principle.

**The code anchor says which code facts to check.** Canonize's last step runs
`docs/graph/code-anchor.py --record`, which writes `.cypress/anchor.json`: the
branch, the commit and the uncommitted code paths of each repository the plant
governs. At the start of the next session, Claude Code's `status-hook.py`
(SessionStart) and Prime Agent's `status-extension.ts` (first prompt) run
`--compare` once and add one line after the status summary. The line says
that no code changed, names the paths that did, says no anchor is recorded
yet, or, when the comparison does not finish within 5 s, says the code was not
checked. The last two lines tell the session to check the code facts it relies
on. No per-prompt hook and no per-tool hook runs the anchor. opencode has no
hook and reads the line from the newest session record, where canonize writes
it. SPEC-0003 carries the tool's and the hooks' contracts.

**The kernel sheds its pre-growth lines (ADR-0017).** The pointer to the
install prompt, which only an ungrown plant needs, moves into a pre-growth
block of the placeholder `docs/graph/index.md`, and grow removes that block
when it marks the plant grown. With the §3.2 sentences added, the kernel went
from 7,931 to 7,797 bytes.

**Always-loaded text is cut to what every session needs.** The descriptions of
`growth-orchestrator`, `growth-scout` and `seed-installer` now say only what
each role does and that it runs inside grow, graft or adopt, 921 bytes fewer
across the three. The Prime Agent overlay drops both Opus version tables
(ADR-0019): Opus-class work runs on Opus 5.5, and on Opus 4.6 only for
extremely light authoring that Sonnet should not be trusted with. The Sonnet
floor stays at 4.6, and the protocols stay the one home of each phase's model
class. `multi-agent-architect` follows the same rule.

**The router prints where each node lives.** Each `graph-lint.py --plan` entry
now reads `<id>  <path>  <reason>`, and both route hooks keep the path, so a
session no longer searches for the file a node names. The path costs bytes on
every routed prompt. Measured on a grown plant before and after this release,
the route hook's output grew by 935, 742 and 1,367 bytes on three of four
fixed prompts and shrank by 750 on the fourth. The total cost still fell: the
prompt about editing the installer went from 3 turns and 69,192 input tokens
to 2 turns and 47,474, the prompt asking where the route hook is installed from
went from 6 turns to 5, and twelve runs cost $3.6140 against $3.7063 before.
No median got worse beyond the spread of its own three runs, and
`agent-lint --eval` returned identical results on both copies.

**Graft's mechanical steps are tools, run from the seed.** None of these is
placed into a plant.
- `tools/graft-ledger.py` prints one row per seed-owned file with its
  three-way class (CURRENT, FAST-FORWARD, KEEP-PLANT, SEED-NEW, HARVESTED or
  MERGE) and, with `--base`, the graft's base: the stamped version's tag, or
  else the seed commit the plant's machinery matches best.
- `tools/graft-run.py` copies the plant to a stage outside it, runs the
  ledger, the install with its log, the engine reconciliation, the audits and
  the lints there, and prints the Phase 7 gate table with each judgment row
  `not run`. It refuses a stage inside the plant and ratifies nothing.
- `tools/graft-audit.py` stops raising four false alarms: it takes `--base`,
  no longer reports an engine's preserved config as a customization, maps the projections
  of a plant's own agents and skills (the Copilot view included), and skips
  nested plant copies. It walks the plant through the new shared
  `tools/plant_walk.py`, and `tools/growth-audit.py` uses the same walk.

Graft points at these tools where its steps used to describe them. It also
reads the plant's operator node before calling a migration optional, keeps a
plant fact it corrects as one dated line of history, and, like harvest's G5,
says why its untouched check uses the narrow `git status --porcelain` form.

**The installer (SPEC-0001).** A replaced kernel identical to any earlier seed
kernel files no migration row. Every run that writes the stamp also writes
`.cypress/recreated-nodes.txt`, the whole list of seed nodes it re-created;
the console notice still stops at ten, and graft's re-created-nodes gate reads
the file. The stamp keeps every key the installer does not own (ADR-0016). A
stamp that is valid JSON but not an object is backed up and replaced with one
warning, and a stamp that is not UTF-8 is refused by the preflight with its
normal message instead of a Python traceback. The installer places
`docs/graph/code-anchor.py` and writes no anchor.

**The seed's own plans are ledgers (ADR-0020).** This round's plan was a
ledger from its first increment, and the 7.30.0 and 7.31.0 plans were
converted: `tools/verify-ledger.py` rebuilt each one byte for byte from its
index and leaves. `grill-lint.py` reads a seed-side ledger plan, takes its
spec and decision homes from flags, and reports a decision cited as
`<name>:ADR-NNNN` as another repository's (ADR-0015). The seed's gate now runs
it over the active round's plan. `spec-lint.py` refuses a table row whose cell
count differs from its header.

**Roles and rules.** A tester's RED spawn writes the test, confirms it fails
for the right reason and hands back; the owner's words are in the tester
charter, and any implementation, even a throwaway one, is the implementer's
GREEN. The design latitude is classified the way a tier is, from the request,
and the owner is asked only in doubt (SPEC-0005, version 0.13). `tool-smith`
gains its handback and "what you do not do" sections. ADR-0002 states its
invariant and points at the roster's one home.

**The seed's gate.** `tests/seed-lint.py` fails when `tests/run.sh` loses any
part of `set -euo pipefail` above its first step. A mutation pass over the
round's code ran 24 mutants and killed 15. Of the nine survivors, new guards
kill four, a suite the pass had not run already killed one, two are
equivalent, and two have no small test yet. The same pass
found the not-UTF-8 stamp defect above.

**Reach.**
- A new plant receives everything at install.
- An existing plant receives it at its next graft. The graph engines arrive
  through `tools/graft-graph-engine.py`, since a plain re-install never
  overwrites a placed engine; the hooks, the kernel, the agents and the
  protocols fast-forward.
- The code anchor starts at each plant's next canonize. Until then, the
  session-start line says no anchor is recorded, and the session checks the
  code facts it relies on.
- Copilot and Codex, the frozen hosts, receive the updated agents, the shared
  kernel and, where Copilot's projected hooks run, the new status-hook
  behaviour, and nothing beyond that.
