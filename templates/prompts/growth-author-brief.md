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

Read `.cypress/growth/corrections.md` beside them: it outranks the
ledgers and the orchestration plan wherever they conflict
(`protocol.grow`, the corrections record).

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
   Report it in `graph_route:` as ids, never the router's output.
2. Load ONLY the reported nodes plus their `requires:` closure.
   Everything else a loaded node lists (leaves, children, links,
   neighbours) is a menu: open an item only when its one-line
   "load when" serves your task, and list the rest as skipped.
3. Before reading the files you will touch, check that each stack
   element they use (extension, path, manifest, lockfile) and their
   area has an `expertise.*` node, owning node or `libraries/` page in
   the route; for each one missing, run `--plan "<that element>"` and
   load what it reports. Declare in `graph_route:` what you loaded,
   skipped, and widened (with the reason).
4. Link to the node that owns a fact; do not restate it. The graph
   outranks your memory of APIs and versions. A fact the graph states
   is settled: use it as stated; re-deriving or re-checking it spends
   what the graph saves. Facts about code are current only where your
   brief carries a code-anchor line saying no code changed; otherwise
   check the code facts you rely on against the code. An unknown fact
   is "not recorded": never invent a version, URL or identifier.
5. Every read, search and tool call serves the deliverable; stop when
   it is complete and trusted. Read a spec by contract:
   `python3 docs/graph/spec-lint.py --slice --refs SLUG...`, then open
   only the §6/§7 headings it cites. Return only what your parent
   needs (`method.minimum-sufficient-work`).
6. Leave shared git state alone: `git stash`, `checkout`, `restore`,
   `reset` and `clean` move other writers' uncommitted files. Take a
   baseline by copying the file or `git show HEAD:<path>`
   (`delegation.wave-baseline`).
7. No graph nodes yet (bootstrap pass): report the failed probe and
   stay inside the paths this brief names.
```

```
COMPANION:
- Routed by: {{the protocol phase, the agent-lint --route line and band,
  or the override rationale}}. brief.py logged it with your spawn_id, role
  and effort, so your handback starts at `status:`. At a LOW/NONE band,
  name the gap in `out_of_domain_needed`: the fitting specialist, or the
  expertise the graph still needs.
- End your turn with the HANDBACK payload; at an out-of-domain boundary
  name the specialist in `recommended_next`. Past the soft target, write
  the overflow note as you work and name it (handback-payload.md, Rules).
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
  Outside that scope you may only append to `.cypress/growth/corrections.md`:
  a ledger claim the source contradicts, a fact two ledgers home
  differently, a boundary drawn in the wrong place, or an edge or
  ownership question, never an edit to a ledger.
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
