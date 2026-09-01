<!--
Template: prompts/growth-author-brief.md
Used: by grow / adopt-existing / from-scratch to dispatch an Opus-class
author that turns a completed growth evidence ledger into a specific
deliverable. This is the GROWTH-DEDICATED author brief: it CONSUMES the
ledger the growth-scout wrote and maps its sections to the deliverable,
so the author builds on collected, cited evidence instead of
re-investigating source or generating structure from scratch. Pair with
templates/prompts/growth-scout-brief.md (the producer).

This brief orchestrates WHICH deliverable an author produces and points
at the per-deliverable contract to obey. For a knowledge-graph node,
that contract is templates/prompts/node-authoring-brief.md (embed its
HARD RULES); for a spec/ADR/agent/library page, the matching template.
Fill the {{PLACEHOLDERS}} and hand the body to the author.
Discipline: protocols/grow.md, agents/growth-orchestrator.md.
-->

# Growth-author brief — {{deliverable}}

**Model class: opus.** Authoring is high-level work — a mechanical
fill-in produces a deliverable that lies. But your **evidence is already
gathered**: you build from the ledger, not from a fresh reading of
source. Confirm a path the ledger cites when it sharpens the point;
do not re-scout.

## Your feedstock — read this first

Read the growth evidence ledger(s) the scouts wrote:

```
.cypress/growth/{{boundary-slug}}.ledger.md   {{+ any reconciled ledgers this deliverable spans}}
```

The ledger schema is `docs/graph/templates/prompts/growth-evidence-ledger.md`;
each section is keyed to the deliverable it feeds. Also load
`docs/graph/_schema.md` and {{an existing exemplar}} for style.

- **Build only on cited claims.** Every fact you write traces to a
  ledger claim with its `path:line` + symbol. A fact the ledger marks
  `not recorded` stays `not recorded` — you do not fill it from memory.
  A section marked `none found` means the deliverable omits it, not that
  you invent content to populate it.
- **Route ledger section → deliverable.** Author {{this deliverable}}
  from these ledger sections:
  - graph node (product/architecture/api/data/prompts/evals) → §1–§6,
    §11;
  - `specs/` → §7 (formalize the candidate behaviors; the observable
    each asserts);
  - `decisions/` (ADR) → §8 (only decisions the source shows; unknown
    rationale is `not recorded`);
  - project-specific specialist agent → §9 (only if a signal genuinely
    warrants one; otherwise report "no custom agent warranted");
  - `runbooks/` + verification → §10, labeled **discovered, not
    executed**;
  - `libraries/` → §5.
- **One home per fact.** A fact the graph already owns is linked, never
  re-stated. Never ask two authors to own overlapping facts or files.
- **Smallest sufficient artifact.** Author only what the evidence
  demands and the graph will consume: no section padded to look
  complete, no node the router cannot reach, no leaf without an
  owning-node edge (`docs/graph/method/engineering-posture.md` §5–§8 — growth
  validation audits over-growth exactly as it audits gaps).

## Rules (state these to the sub-agent verbatim)

- **Execute the graph first.** The route-hook does not fire for you.
  <!-- canonical block from docs/graph/templates/prompts/graph-session-bootstrap.md;
       byte-identity enforced by tests/seed-lint.py — edit it THERE -->

```
GRAPH DISCIPLINE — execute before reading any source:
1. Run: python3 docs/graph/graph-lint.py --plan "{{exact delegated task}}"
   Include the command and its output in your report as graph-route
   evidence (context routing — NOT the `route_evidence` field, which
   carries the agent-routing line from your brief).
2. Load ONLY the reported nodes plus their `requires:` closure.
3. Declare what you loaded, what you deliberately skipped, and any
   later widening (with the reason it became necessary).
4. One home per fact: never duplicate a fact the graph owns — link to
   its owning node. The graph outranks your memory of APIs/versions.
   When a fact is unknown, write "not recorded" — never fabricate a
   version, URL, or identifier.
5. Minimum sufficient work: every read, search, and tool call serves
   your delegated deliverable — smallest sufficient evidence, cheapest
   reliable method; stop when the deliverable is complete and trusted.
   Return findings, not raw dumps; produce nothing your parent does
   not need. Depth: `docs/graph/method/engineering-posture.md` §5–§8.
6. If the graph has no nodes yet (bootstrap pass), report the failed
   probe and stay inside the exact paths named in this brief.
```

- **Obey the per-deliverable contract.** For a knowledge-graph node,
  embed the HARD RULES from `docs/graph/templates/prompts/node-authoring-brief.md`
  verbatim (frontmatter subset, unique `owns`, minimal `requires`, body
  ≤150 lines, no version numbers in body, honest `est_tokens`). For a
  spec/ADR/library/agent, follow the matching template
  (`docs/graph/templates/spec.template.md`, `docs/graph/templates/adr.template.md`,
  `docs/graph/templates/library-page.template.md`, `docs/graph/templates/agent.template.md`).
- **Write only your exclusive scope.** Write exactly: {{list the exact
  file paths}}. Knowledge writes stay under `docs/graph/`; a
  project-specific agent goes where the plant's roster lives. Do not
  touch application code, manifests, CI, or Git state.
- **Never invent.** No fabricated version, URL, CVE, status, date, or
  passing result. `not recorded` / `not audited` / `discovered, not
  executed` instead.
- **Trace this spawn.** Your `spawn_id` is **{{caller-minted dot-chain id,
  e.g. orchestrator.3.architect.1 — see delegation.tracing}}**; echo it
  verbatim in your handback's `spawn_id` field.

- **Cite the router.** Selected by `agent-lint --route`: {{paste the
  ranked line + confidence band}} — echo it back in `route_evidence`.

## Return

The file paths written; for each, the ledger claims it rests on and any
ledger fact you deliberately omitted for length. Confirm the relevant
linter passes (`graph-lint.py`, and `spec-lint.py` for a spec) or report
what it flags. End with the payload from
`docs/graph/templates/prompts/handback-payload.md` (`produced_by: {{you}}`,
`in_domain_work_done` with paths, `route_evidence`); spawn only from your
`delegates_to` allowlist within your depth cap, else STOP and hand back. If
you are a leaf (`can_delegate: false`) you have no allowlist — never spawn;
STOP and hand back instead.
