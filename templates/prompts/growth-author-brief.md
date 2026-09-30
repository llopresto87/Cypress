<!--
Template: prompts/growth-author-brief.md
Used: by grow / adopt-existing / from-scratch to dispatch an
authoring-class author that turns a completed growth evidence ledger
into a specific deliverable. This is the growth-dedicated author brief:
it consumes the ledger the growth-scout wrote and maps its sections to
the deliverable, so the author builds on collected, cited evidence
instead of re-investigating source or generating structure from
scratch. Pair with templates/prompts/growth-scout-brief.md (the
producer).

This brief orchestrates which deliverable an author produces and points
at the per-deliverable contract to obey. For a knowledge-graph node,
that contract is templates/prompts/node-authoring-brief.md (embed its
linted rules); for a spec/ADR/agent/library page, the matching template.
Give each author an exclusive set of facts and files.
Model class: opus (the authoring class): authoring is judgment work,
and a mechanical fill-in produces a deliverable that lies.
Fill the {{PLACEHOLDERS}} and hand the body to the author.
Discipline: protocols/grow.md, agents/growth-orchestrator.md.
-->

# Growth-author brief — {{deliverable}}

Your **evidence is already gathered**: build from the ledger, and open a
path the ledger cites only when it sharpens the point.

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
  `not recorded` stays `not recorded`, and a section marked `none found`
  is left out of the deliverable.
- **Route ledger section → deliverable.** Author {{this deliverable}}
  from these ledger sections:
  - graph node (product/architecture/api/data/prompts/evals) → §1–§6,
    §11;
  - `specs/` → §7 (formalize the candidate behaviors; the observable
    each asserts);
  - `decisions/` (ADR) → §8 (only decisions the source shows; unknown
    rationale is `not recorded`);
  - `nodes/expertise.<slug>.md` → §9's expertise half, which is what §9
    normally produces: one node per core or significant stack element,
    owning only *when* that element is in play, what must not be done
    without it, and which sub-expertises apply under which condition.
    Author `load_when` from the ≥3-character words §9 records (the child's
    own words, never the family's), `composes:` from the sub-expertises §9
    names, and the `libraries:`/`artifacts:` edges to the depth pages
    below; the node is written from the same retrieved sources as those
    leaves, carries no version, and links to what they own
    (`docs/graph/templates/docs/nodes/_expertise.template.md`);
  - project-specific specialist agent → §9's agent half, and only where the
    work needs what a node cannot give it: different `tools`, a different
    `model` class, an adversarial `stance`, or context `isolation`;
    otherwise report "no custom agent warranted". Either way the decision is
    recorded, in the `expert` object of the inventory item it belongs to,
    naming which of those four it `needs`. An authored expert carries
    `origin: project`, a `plant_knowledge:` list (the collections or
    expertise nodes it draws on), and a `motivated_by` citation, and is
    projected into every harness directory the plant carries — unprojected,
    it is on disk and unspawnable;
  - `runbooks/` + verification → §10, labeled **discovered, not
    executed**;
  - `libraries/` → §5 **plus** the research-scout's normalized upstream
    sources under `docs/graph/sources/normalized/` — a rich page for a
    §5-flagged significant dependency is grounded in that retrieved
    material (`docs/graph/protocols/ingest-library.md`). This page is the
    one home of the pin; the slug's expertise node points here for it;
  - `design/` → §12 (screens, flows, components, tokens, interaction
    states, the accessibility affordances present) **plus** the retrieved
    design standards and platform conventions in
    `docs/graph/sources/` — one leaf per interface surface, authored by
    `ui-ux-designer`; `none found` in §12 means the boundary has no user
    interface, not that the leaf is skipped silently;
  - `legal/` → §13 (the regulated data, jurisdictions and compliance
    artifacts the source shows) **plus** the seed's
    `legal-corpus/<scope>/<instrument>.md` as the orientation layer,
    currency re-confirmed against the publisher. The ledger supplies the
    technical facts; `agent.legal` qualifies them against the corpus;
  - `best-practices/` → §14 (which standards apply and where the
    project's stance is visible) **plus** the retrieved standards in
    `docs/graph/sources/`: state the external standard (cited), what it
    says not to do, and where the project observably stands — normative,
    not a description of current habits. This page is the one home of the
    stance; the slug's expertise node points here for it.
- **Smallest sufficient artifact.** Author only what the evidence
  demands and the graph will consume: no section padded to look
  complete, no node the router cannot reach, no leaf without an
  owning-node edge (`method.minimum-sufficient-work`,
  `method.decision-economy`, `method.engineering-posture` §8 — growth
  validation audits over-growth exactly as it audits gaps).

## Rules (state these to the sub-agent verbatim)

- **Execute the graph first; these blocks are your routing.**
<!-- canonical blocks from docs/graph/templates/prompts/graph-session-bootstrap.md;
     tests/seed-lint.py holds them byte-identical, so edit them there -->

```
GRAPH DISCIPLINE — execute before reading any source:
1. Run: python3 docs/graph/graph-lint.py --plan "{{exact delegated task}}"
   Include the command and its output in your report as graph-route
   evidence (this is context routing; the `route_evidence` field
   carries the agent-routing line from your brief).
2. Load ONLY the reported nodes plus their `requires:` closure.
   Everything else a loaded node lists (leaves, children, links,
   neighbours) is a menu: open an item only when its one-line
   "load when" serves your task, and list the rest as skipped.
3. Declare what you loaded, what you deliberately skipped, and any
   later widening (with the reason it became necessary).
4. One home per fact: link to the node that owns a fact instead of
   restating it. The graph outranks your memory of APIs/versions.
   A fact the graph states is settled: use it as stated; re-deriving
   or re-checking it spends what the graph saves. Facts about code are
   current only where your brief carries a code-anchor line saying no
   code changed; otherwise check the code facts you rely on against
   the code.
   When a fact is unknown, write "not recorded" — never fabricate a
   version, URL, or identifier.
5. Minimum sufficient work: every read, search, and tool call serves
   your delegated deliverable — smallest sufficient evidence, cheapest
   reliable method; stop when the deliverable is complete and trusted.
   Return findings, and only what your parent needs. Depth:
   `method.minimum-sufficient-work`, `method.decision-economy`,
   `method.engineering-posture` §8.
6. If the graph has no nodes yet (bootstrap pass), report the failed
   probe and stay inside the exact paths named in this brief.
```

```
COMPANION (echo each item back in your handback):
- Trace this spawn. Your `spawn_id` is {{caller-minted dot-chain id,
  e.g. orchestrator.3.architect.1; see delegation.tracing}}. Echo it
  verbatim in your handback's `spawn_id` field.
- Cite the router. The `agent-lint --route` ranked line and confidence
  band that selected you, or the caller's override rationale:
  {{paste the line + band, or the rationale}}. Echo it back in
  `route_evidence`. At a LOW/NONE band, say so there and name the gap:
  a different specialist, or expertise no node in this graph carries.
- End with a handback. Close your turn with the payload from
  `docs/graph/templates/prompts/handback-payload.md`: `produced_by:
  {{you}}`, `in_domain_work_done` with paths, `route_evidence`,
  `effort`, `expertise_gap`, `gates`, `tools_built`, and, at any
  out-of-domain boundary, `recommended_next` naming the specialist.
  When your report outgrows the soft target, write the overflow note
  as you work and name it (that file's Rules).
```

- **Obey the per-deliverable contract.** For a knowledge-graph node,
  embed the linted rules of
  `docs/graph/templates/prompts/node-authoring-brief.md` verbatim. For a
  spec/ADR/library/agent, follow the matching template
  (`docs/graph/templates/spec.template.md`, `docs/graph/templates/adr.template.md`,
  `docs/graph/templates/library-page.template.md`, `docs/graph/templates/agent.template.md`).
- **Write only your exclusive scope.** Write exactly: {{list the exact
  file paths}}. Knowledge writes stay under `docs/graph/`; a
  project-specific agent goes where the plant's roster lives.
  Application code, manifests, CI and Git state stay as they are.
- **Mark every unknown.** Write `not recorded`, `not audited` or
  `discovered, not executed` wherever a version, URL, CVE, status, date
  or passing result is not in evidence (GRAPH DISCIPLINE 4).
- **Delegate only as your frontmatter allows.** A delegator spawns only
  from its `delegates_to` allowlist within its depth cap; a leaf
  (`can_delegate: false`) ONLY recommends the next specialist and hands
  back.

## Return

The file paths written; for each, the ledger claims it rests on and any
ledger fact you deliberately omitted for length. Confirm the relevant
linter passes (`graph-lint.py`, and `spec-lint.py` for a spec) or report
what it flags.
