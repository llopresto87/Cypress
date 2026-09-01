# Install and grow CYPRESS — the single entry point

This one prompt is the **primary, tool-neutral entry point** for putting CYPRESS
into a project. There is nothing else to run first and nothing else to run after:
it installs **all** the seed's files into your target and then drives a
**complete, full-depth growth** of the target's `docs/graph/` knowledge system.
`install.sh` is only the placement mechanism this prompt invokes; `grow` is the
growth doctrine it executes; `/initialize` is only a thin coding-tool adapter to
the same flow. Paste this whole file into an agent-capable chat and follow it.

---

## What this does, and why

- **What.** Two things, as one flow: (1) *place* every seed file into the target
  (kernel, the entire method surface as `docs/graph/` nodes, host adapters,
  templates, linters), and (2) *grow* the target into a source-grounded graph —
  a node for every real subsystem, a page for every architecturally significant
  dependency, and a connected leaf for every observed route, entity, migration,
  config, and AI contract the source actually contains. Growth's evidence is
  **two-sided**: internal `growth-scout`s read this project's code, and
  external `research-scout`s retrieve the upstream documentation and community
  standards that code operates against — "executable source is the truth"
  governs claims *about the project*, and is never a license to skip the web.
- **Why full depth is mandatory.** A half-grown plant — a root node, a router,
  and a few leaves — is the most common way this is mis-run: a failed growth
  reported as a success. The growth here is bound by `grow`'s
  **completeness contract** (`grow.completeness-contract`): every knowledge
  collection is either covered to the depth its evidence supports, or explicitly
  absent because the source has no such evidence. "Enough", "ran out of context",
  and "the templates are present" are not completion. This binds whatever model
  is orchestrating; it does not soften with model size or operator impatience.

## How it runs — one flow, three phases

You may **start this chat rooted at the seed** (it is the source you copy from)
or already rooted at the target. Either way the flow is the same.

**Phase 0 — PLACE (may run from the seed).** Install CYPRESS from
`{{seed path; locate this repository if already in scope}}` into
`{{target project or umbrella; default: current working directory}}` by invoking
the placement mechanism — normally `./install.sh <tool> --project-dir <target>`
(or `all`), additive, preserving every target-owned file. Install only the host
adapters actually used. This step places files; it does not grow anything.

**Phase 1 — HAND OFF (the registration boundary).** Growth dispatches specialists
by name, and a host registers its agent roster when a session *starts* — so the
session that just placed the roster (and any session rooted at the seed) cannot
spawn it yet. **Re-enter this prompt in a fresh session rooted at the target**
before growth dispatches anything; this is expected and is not a failure. The
target now carries `EXPERT_SEED_INSTALL_PROMPT.md`, a copy of this prompt, for
exactly this re-entry and for later refreshes. If a restart is truly impossible,
use the recorded role-emulation fallback and report it in the delivery.
`docs/graph/method/delegation.md` (`delegation.harness-registration`) is the
single home for both the remedy and the fallback. Silently substituting a
generic worker for a named specialist is the one response that is not allowed.

**Phase 2 — GROW IN FULL.** From the target-rooted session, **execute the
complete `grow` protocol — `docs/graph/protocols/grow.md` — in full**: read it,
then drive every phase it defines, in order (detect scope → scout internal
evidence → retrieve external upstream evidence via `research-scout` → model and
author → grow source-backed leaves → the `docs-librarian` rebalance pass
(connect and fertilize) → independent validation → canonize → delivery and
maturity). Honor its
**completeness contract in full**: fill the growth completeness ledger with a row
for every collection, and do not declare growth done until every row is
covered-to-evidence or absent-with-reason and Phase 6 validation passes against
the graph — never against the file tree. Do not work from a summary and do not
skip or collapse its phases. If the target has no executable evidence, `grow`
routes through `from-scratch` for intent discovery.

Three steps are historically skipped by orchestrators optimizing for the
checklist instead of depth, and each is a defect, not a judgment call:

1. **The external pass** (grow topology step 3): after the internal ledgers
   reconcile, dispatch `research-scout`s for every architecturally
   significant / cross-cutting / security- or operations-critical dependency
   the ledgers flag, and for the external standards the project is held to —
   version-pinned upstream docs into `docs/graph/sources/`, feeding rich
   `libraries/` pages and a **normative** `best-practices/` (the standard,
   cited, plus the project's stance). Marking `sources/` absent because "no
   external information was consumed" when no research-scout was dispatched
   is circular and fails Phase 6.
2. **The librarian rebalance pass** (grow Phase 5): one whole-graph
   `docs-librarian` dispatch after authoring — connect, merge, split,
   delete, keep the router compact. Authors work in exclusive scopes; only
   this pass sees the seams.
3. **The canonize close-out** (§3.7) before delivery, so the growth's own
   lessons land in the graph instead of evaporating with the session.

## The orchestration rules that bind this chat

This chat is the orchestration and planning plane. **Do not perform investigation,**
authoring, or code edits in the main chat. Maintain the plan here, communicate
with me here, and always spawn clean-context workers with a bounded purpose, the
exact paths they may inspect/change, required graph context, evidence rules,
deliverables, and verification. Use purpose-made existing agents/skills/prompts;
if none fits, create the missing project-agnostic expert definition first.

Model policy is strict:

- **Sonnet-class workers**: read-only scouting, inventory, extraction, and factual
  evidence reports only. They do not author artifacts or make deep design calls.
  (`research-scout`'s snapshot/normalize writes into `docs/graph/sources/` are
  mechanical normalization of retrieved upstream text, not authoring — its
  drafts are finalized by the Opus-class `docs-librarian`.)
- **Opus-class workers**: all writing/authoring, code changes, synthesis,
  architecture, deep analysis, review, and adversarial validation.

**Every spawned session must execute**
`python3 docs/graph/graph-lint.py --plan "<its exact task>"` before reading source
or writing, load the resulting nodes plus their `requires` closure, and return the
command/output, the loaded closure, deliberate skips, and any later widening. A
bootstrap scout facing an empty initial graph still runs the probe, reports that
it is not yet routable, and stays strictly inside the exact paths in its brief.
Once nodes exist there is no fallback to hand-waved routing.

Hard boundaries bind every worker from the first spawn (`grow`'s § Boundaries is
the full statement): do not modify application code; do not run application builds
or test suites; do not fetch/pull/switch/commit/push Git; do not fabricate specs,
ADRs, rationale, commands, sources, or green status. Record Git state only as
provenance; existing docs never outrank current executable source.

## Finish

Finish in this chat with the delivery `grow` defines — detected scope/revisions,
workers and briefs used (growth-scouts AND research-scouts), graph artifacts
grown, the librarian rebalance report, the **growth completeness ledger**,
checks and results, excluded/untrusted evidence, honest unknowns, and one
highest-leverage next action with its task tier (kernel §0), so the next session
starts classified. Run the `canonize` close-out before delivering. Do not call the plant mature merely because template files
exist; maturity is proved by the graph, and by every completeness-ledger row
being closed.

---

The prompt is intentionally project-, language-, vendor-, repository-, and
coding-tool-agnostic. Tool commands such as `/initialize` are convenience
adapters to this workflow, not the workflow's primary interface.
