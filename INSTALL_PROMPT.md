# Install and grow CYPRESS — the single entry point

This one prompt is the **primary, tool-neutral entry point** for putting CYPRESS
into a project, and it is the whole flow: it installs **all** the seed's files into your target and then drives a
**complete, full-depth growth** of the target's `docs/graph/` knowledge system.
`install.sh` is only the placement mechanism this prompt invokes; `grow` is the
growth doctrine it executes; `/initialize` is the entry fork that chooses between `grow` and
`from-scratch`; on a target with source to scout it delegates here, and on an
empty one it does not. Paste this whole file into an agent-capable chat and follow it.

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
  governs claims *about the project*, and the web pass belongs to every growth.
- **Why full depth is mandatory.** A half-grown plant — a root node, a router,
  and a few leaves — is the most common way this is mis-run: a failed growth
  reported as a success. The growth here is bound by `grow`'s
  **completeness contract** (`grow.completeness-contract`): every knowledge
  collection is either covered to the depth its evidence supports, or explicitly
  absent because the source has no such evidence. "Enough", "ran out of context",
  and "the templates are present" are not completion. This binds every
  orchestrating model equally, whatever its size or the operator's hurry.

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
`docs/graph/method/delegation-bounds.md` (`delegation.harness-registration`) is the
single home for both the remedy and the fallback. Restart or the recorded
fallback are the two responses; a generic worker silently standing in for a
named specialist is not one.

**Phase 2 — GROW IN FULL.** From the target-rooted session, **execute the
complete `grow` protocol — `docs/graph/protocols/grow.md` — in full**: read it,
then drive every phase it defines, in order (detect scope → scout internal
evidence → retrieve external upstream evidence via `research-scout` → model and
author → grow source-backed leaves → the `docs-librarian` rebalance pass
(connect and fertilize) → independent validation → canonize → delivery and
maturity). Honor its
**completeness contract in full**. That contract is mechanical, not a promise
you make about your own work: reconcile the scouts' findings into the stack
inventory, run
`python3 <seed>/tools/growth-audit.py <plant> <seed> --plan` to turn each item
into the artifacts growth owes it, author them, then run
`python3 <seed>/tools/growth-audit.py <plant> <seed>` and route every finding
back to an author. Repeat until it exits 0: every row is covered to evidence,
absent with a reason and the paths you searched, or a named blocker
(`docs/graph/templates/prompts/growth-coverage-record.md` defines each). Phase 6
validation then passes against the graph rather than the file tree. Work from
the node itself, not a summary. If the target has no executable evidence,
`grow` is the wrong protocol for it:
`protocol.initialize` owns the entry fork and hands an empty repository to
`from-scratch`, a nine-phase workflow that authors the project and its graph
and ends at `deliver`. It does not return here.

Orchestrators optimizing for the checklist instead of depth most often skip
these three steps; each skip is a defect, not a judgment call:

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

This chat is the orchestration and planning plane: it routes, plans and talks
with me, and every investigation, authoring task and code edit goes to a
clean-context worker. Each worker gets a bounded purpose, the exact paths it
may inspect/change, required graph context, evidence rules, deliverables, and
verification. Use purpose-made existing agents/skills/prompts;
if none fits, create the missing project-agnostic expert definition first — and
hold it to that word: `python3 docs/graph/agnosticism-lint.py --file <the new
definition> --forbid <project name> --forbid <domain noun>` catches the
objective leaks before the definition calcifies. A definition that names this
project is not an expert definition, it is a note.

Model policy (the classes are `delegation.model-classes`; the plant's model
map names the model on each host):

- **Investigation-class workers** ONLY scout, inventory, extract and report
  facts, read-only, plus `research-scout`'s mechanical normalization of
  retrieved upstream text into `docs/graph/sources/`, whose drafts the
  authoring-class `docs-librarian` finalizes.
- **Authoring-class workers** do all writing/authoring, code changes,
  synthesis, architecture, deep analysis, review, and adversarial validation.

Every worker brief embeds the graph-session bootstrap blocks
(`templates/prompts/graph-session-bootstrap.md`, placed in the target as
`docs/graph/templates/prompts/graph-session-bootstrap.md`) verbatim.

Hard boundaries bind every worker from the first spawn (`grow`'s § Boundaries is
the full statement): workers leave the application as they find it. They
change none of its code, run none of its builds or test suites, and leave its
Git state alone (no fetch, pull, switch, commit or push), recording that state
only as provenance. Every spec, ADR, rationale, command, source and status they
report is evidenced, never fabricated, and existing docs never outrank current
executable source.

## The plant facts are an explicit choice

Before the installer runs, ask the owner for the four plant facts the router's `plant:`
block carries (`environment_class`, `commit_attribution`, `deliverable_language`,
`comment_language`) as one numbered question, propose each from evidence, and pass the
confirmed values to `install.sh` with `--environment-class`, `--commit-attribution`,
`--deliverable-language`, `--comment-language`. The installer refuses an unknown environment
class, never overwrites a declared value, and names any fact still unset as a NEXT STEP.
Growth asks the same four once more only if they are still placeholders (`grow.plant-facts`).

## Finish

Finish in this chat with the delivery `grow` defines — detected scope/revisions,
workers and briefs used (growth-scouts AND research-scouts), graph artifacts
grown, the librarian rebalance report, the **coverage record**
(`.cypress/coverage.json`, and the `growth-audit.py` run that passed over it),
checks and results, excluded/untrusted evidence, honest unknowns, and one
highest-leverage next action with its task tier (kernel §0), so the next session
starts classified. Run the `canonize` close-out before delivering. Call the
plant mature when the graph proves it and the coverage gate is green; template
files alone prove nothing. Commit the coverage record with the graph —
it is how the next session, and the next graft, can tell what this growth
covered from what it never looked at.
