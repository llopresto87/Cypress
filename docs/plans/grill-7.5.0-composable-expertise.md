# grill — composable expertise as graph nodes (7.5.0)

Plan-of-record for one new node kind, one new lazy edge, and the intake,
audit, and doctrine changes that make them load-bearing. Nothing here is
implemented; this file is the masterplan and, per item, the implementation
plan the executing session follows. It absorbs the uncommitted 7.4.0 increment
(17 modified files, gate-green, HEAD `713d32a`) into one 7.5.0 release (Q4).

Every item is written as an **integration, not a patch**
(`skills/holistic-editing/SKILL.md`; §8 binds it): each names the file's
responsibility, where the change belongs architecturally, what the change
makes obsolete, and the class sweep it belongs to. An item whose diff would be
purely additive says why nothing needed to change or die.

**The objective, in the user's terms.** Project-specific expertise in a plant
composes through the knowledge graph's own edges and is resolved by the
context router, never by agents spawning agents. The shipped roster stays flat
and few. An expertise unit is reusable and can be shared by more than one
parent. Expertise is not a property of an agent row: it is **called by the
agents that use it**, each pulling what fits its identity. The user chose the
hybrid (option C): `expertise` is a node **kind**, and a spawnable expert agent
becomes the rare case reserved for work that needs different tools, a
different model class, an adversarial stance, or context isolation.

**The load-bearing mechanism.** `requires:` is eager and always-loaded
(`_schema.md` §"Key semantics"; the "requires everything" anti-pattern is named
there). Composing libraries through it would drag every library page into
every stack task. 7.5.0 adds a second edge, `composes:`, that is lazy and
task-conditioned: the router descends from a loaded expertise node into only
those composed children that the task names **specifically**, beyond what the
parent already covers. A task about EF mapping loads `expertise.dotnet` +
`expertise.ef-core` and never touches `expertise.serilog`.

Release shape: **T3 against the seed** (new behaviour, a schema change, a new
kind). Version `7.5.0`, absorbing the unreleased 7.4.0 entry; ADR-0005.

---

## §0.0 Handoff to the implementing session — read this first

You are implementing 7.5.0 on the CYPRESS seed at `/home/okik/Cypress`. This
plan was authored and verified against the worktree on 2026-09-09; §E lists
every fact that was checked and how. Treat the plan as transferred context
and the worktree as truth: if they disagree, the worktree wins and you record
the discrepancy in §15 before proceeding.

**State you should find.** Branch `7.3.0-growth-coverage-gate`, HEAD `713d32a`,
17 modified files (the uncommitted 7.4.0 increment) and this plan untracked,
`manifest.json` at `7.4.0`, `bash tests/run.sh` exit 0.

**Hazards (from the original handoff; all still true).**
- The 17 modified files are gate-green work. Never `git checkout`, `stash`,
  `reset`, or revert them. Mutation-test by copying a file aside and restoring
  from the copy.
- Local git history was rewritten and not pushed; `origin` holds older SHAs.
  Do not push. If the user asks, the safe form is a `--force-with-lease`
  against the old SHA over the SSH URL (`git@github.com:llopresto87/Cypress.git`);
  the HTTPS remote has no credential helper.
- Commit attribution follows the user's standing rule in
  `~/.claude/projects/-home-okik-Cypress/memory/git-attribution-lopresto.md`.
- The handoff document lives outside the repo at
  `/home/okik/cypress-handoff-7.5.0-composable-expertise.md`; do not move it in.
- The kernel `core/AGENTS.md` is not edited in this release; seed-lint fails
  past 8 000 bytes.
- The canonical bootstrap block in `templates/prompts/graph-session-bootstrap.md`
  is embedded byte-identical in several briefs; do not edit it.

**Read order before writing anything.** `CLAUDE.md`;
`skills/holistic-editing/SKILL.md`; this plan's §0–§8; then per wave, the files
that wave names, whole. `_schema.md` and `graph-lint.py` in full before M2.

**Gate commands.**

```sh
bash tests/run.sh                                   # the gate; exit 0
python3 tests/test_graph_lint.py                    # 27 cases today
bash tests/test-growth-audit.sh                     # 27 cases today
python3 tests/seed-lint.py
mkdir -p <dir> && bash install.sh claude-code --project-dir <dir>
python3 tools/growth-audit.py <plant> <seed> [--plan|--agents|--json]
python3 <plant>/docs/graph/graph-lint.py --plan "<task>"
```

**Scratch.** The session scratchpad (system prompt) for the M1 fixture and
every mutation copy; never `/tmp` inside the repo.

**Sequence.** Waves are sequential; items inside a wave may run in parallel
where file sets are disjoint (single-writer per file per wave). M1's stop rule
gates everything after it. §15 is append-only: record the M1 observations, the
provenance decision, and the mutation matrix there as you go.

**When done.** §13 is the checklist. Then the reviewer spawn in M12, fixes, the
gate again, one commit. Report per `protocols/deliver.md`.

---

## §0 Decisions — ratified 2026-09-09

| # | Question | Decision |
|---|---|---|
| **Q1** | Edge name and direction | `composes:` on the parent, downward; the child keeps `requires:` upward; a reciprocity lint (a child that `requires` an expertise node must appear in its `composes:`) makes a missed parent update a lint error naming the line to add. |
| **Q2** | Does the slug carry the version? | **No — with a condition:** the dotnet expertise must distinguish dotnet versions. §0.1 Q2: the pin has one home (`libraries/<slug>.md`), every expertise node carries at least one depth edge, the body has a mandatory "Version in play" pointer, and when a plant runs two majors at once the unversioned parent composes one version-qualified child per major, derived from the inventory and retired with `status: superseded`. The only place a version enters a slug. |
| **Q3** | May the node hold stance? | Routing only. The node owns `<slug>.applicability` and `<slug>.composition`; stance stays in `best-practices/`, facts in `libraries/`; the body's "Depth" section tells each reader which leaf serves which purpose. |
| **Q4** | Fold or on top? | **Fold.** 7.4.0 is not committed separately. Its unreleased CHANGELOG entry is superseded in place by one 7.5.0 entry; the manifest goes 7.4.0 → 7.5.0 in the same commit; the `expert` object is reshaped where the fold makes it coherent (M7). |
| **D5** | `stack.*` vs `expertise.*` | Both live; `stack.x` owns this project's conventions; `expertise.x` owns applicability and composition over external depth; `stack.x requires expertise.x`; graft moves routing prose rather than copying it. |
| **D6** | Where expertise nodes live | `nodes/expertise.<slug>.md`, following the `deviation` precedent (`nodes/deviation.<slug>.md` + `nodes/_deviation.template.md`). One graph, one directory. No linter loading change. |
| **D7** | Seed agents and `plant_knowledge:` | Expertise is **not part of the agent row set**. No seed agent declares expertise. Agents reach it through the router: every brief runs `--plan` on the exact delegated task; identity selects the leaf via the node's Depth map. Coverage is derived per inventory item. `plant_knowledge:` accepts a node id only for a plant-authored expert. |
| **D8** | Who may carry `composes:` | Only `kind: expertise` nodes, toward `kind: expertise` targets. |
| **D9** | Descent rule | **Delta-exact descent** (§0.1 D9). |

### §0.1 Context per decision

**Q1.** The graph has two edges: `requires:` (always load with me, cycle-checked)
and `peers:` (do not load unless the task crosses). Neither can say "these are
my specialisations; load one only if the task is about it". Downward on the
parent, `expertise.dotnet` lists its children and both the router and a human
read the family in one place; upward on the child, a new library is a local
edit that cannot forget its parent, but the router needs a reverse index and
the parent no longer shows what it composes. Downward plus the reciprocity
lint gives both. The child's upward `requires:` already exists and is right.

**Q2.** *Why unversioned:* a node id is repeated in every `requires:`,
`composes:`, `plant_knowledge:`, `index.md` row, and `owns` prefix; a
versioned id makes a major upgrade a new node and every referrer an edit, and
spreads a pin into every referrer, which rule 10 exists to prevent. The
inventory row has its own `version` field, `slugify()` already yields `dotnet`,
and `library-corpus/` is keyed by library, so the corpus seam only works
unversioned.

*How the expertise still distinguishes versions* — four mechanisms, one home
each:

1. **The pin has one home.** `libraries/<slug>.md` §0 records the exact version,
   §6 the deprecations in that version, §8 the upgrade path. §0 is reworked so
   "Versions in play" is its shape (one row per major the plant runs; one row
   is the common case).
2. **Every expertise node routes to that home.** Lint: ≥1 `libraries:` or
   `artifacts:` edge. Audit: an expertise node owed by a `language`/`runtime`/
   `framework`/`dependency` item has `<slug>` in its `libraries:` list.
3. **The body says where the version lives, never what it is.** The template's
   "Version in play" section is fixed pointer text (§C.1).
4. **Two majors at once compose two children.** One slug with two majors in
   the inventory → the unversioned parent `composes:` one child per major,
   `load_when` carrying the target-framework tokens (`net8.0`, `net10.0`),
   body owning applicability for that major only. `--plan` derives them;
   reciprocity keeps the parent's menu honest; the retired child gets
   `status: superseded` + `superseded_by`. A `-<digits>` slug suffix is legal
   only in that shape. The router keeps `net8`/`net10.0` as terms (§E).

**Q3.** Facts live in `libraries/`, stance in `best-practices/`, routing has no
home yet. Stance in the node is a second home that drifts and names versions
the leakage lint rejects. Routing-only is still worth a file because Tier-3
leaves are never routed directly, so the node is the only handle `--plan` can
return, and because the child's `load_when` is the descent condition itself.
The **Depth** section maps purpose to leaf, which is how an agent of a given
identity knows which leaf to open. Body order: *In play for* · *Do not
without* · *Composition* · *Version in play* · *Depth*.

**Q4.** One release: the 7.4.0 entry is unreleased and may be rewritten in
place. The staffing decision is reshaped where the new default makes the old
shape incoherent (M7). No plant has been planned against 7.4.0, so there is no
record migration. The 7.4.0 review findings and mutation results stay valid
because the checks they pinned are extended in place.

**D5.** The schema defines `stack` as "a language or framework's shared
conventions" and grown plants carry `stack.dotnet`. Without a declared seam
authors write the same sentence in both nodes. No lint can tell convention
from applicability, so this stays a reviewer item.

**D6.** `docs/graph/` is one graph however many directories it spans. The
machinery directories exist only for graft's `origin: seed` boundary, which
expertise nodes do not need, and with coverage derived per item a directory's
coverage-row advantage disappears. `graft-audit --unfilled` already skips
`_*` and `*.template.md` files (§E), so the new template never reads as an
unfilled scaffold.

**D7.** *Expertise is called by the agents that will use the knowledge, fitting
their identity.* The agent row set is untouched; the call is the router; the
orchestrator writes the task line in the domain's words; identity selects the
leaf; a plant-authored expert may declare `plant_knowledge: [expertise.dotnet]`.
The `empty_reads()` all-of wrinkle is real but not this release's (§12).

**D8.** Only expertise nodes could sensibly compose. Both ends `kind: expertise`
keeps reciprocity and pass-through simple; loosening later is additive.

**D9 — delta-exact descent, derived.**

*Requirement.* Given a loaded expertise parent P with children C₁…Cₙ and a
task T, load exactly the children T is specifically about: deterministic,
dependency-free, no drift with graph size, no descent on a generic trigger,
visible per child, recursive without a depth knob.

*What the router gives us.* `_terms(T)` yields the task's tokens (≥3
characters, stopwords removed). Seed scoring already builds each node's
tokens into `buckets` (name tokens from id/title/repo; trigger tokens from
`load_when`), scores them with `_match` (2 exact, 1 six-character prefix
fold) times an IDF weight over the whole graph, and **cuts**: the top three
entries at or above `floor = max(3, (best + 1) // 2)` become seeds (L603–L606).
Every seed's `requires:` closure loads.

*What descent decides — stated honestly.* A child whose triggers the task
names loudly is seeded by that cut and needs no descent; `requires:` then
pulls its parent. Descent decides the rest: a child the task names **exactly
but not loudly enough** — one specific term against a task dominated by a
subsystem, or a child pushed out of the top three by stronger subjects — is
composed in because its parent is loaded, without competing in the cut. That
is the regime every spike task and every descent test must sit in (M1, M3):
a task on which the unmodified router does **not** load the child. A test
whose task seeds the child directly proves nothing about descent.

*The vocabulary.* For descent, `V(n)` = the tokens of the node's `load_when`
plus its **slug as one whole token** (the id after the first dot: `ef-core`,
`dotnet-10`) — the trigger vocabulary an author controls. Title and repo
words stay out (they belong to seed scoring: a title like "ef-core — entity
framework applicability" would put `applicability` in every sibling's
vocabulary), and the id is **not** split into fragments: `_tokens` would turn
`ef-core` into `ef` and `core`, and "fix the core service" must not compose
EF. A task that types the slug whole still hits, because `_terms` keeps
`ef-core` as a term alongside its parts. The same `V` serves the
distinctiveness warnings below, so one definition governs both.

*Why a score threshold is wrong.* IDF changes as the graph grows, so a fixed
threshold descends on a small plant and not on a large one; and a score
cannot tell "the task names EF Core" from "the task names dotnet loudly".

*The rule.* Let `Δ(C) = V(C) \ V(P)`. Descend into C iff some task term t has
`_match(t, Δ(C)) == 2`. C's `requires:` closure loads; C becomes P for its own
children. A child with no such term is reported as not loaded with the reason
`no task term specific to it`. No weights, no threshold, no depth cap.

*Why it fits.* "Match" means *specific evidence*, not *loud evidence*. Family
vocabulary sits on the parent by construction and cannot descend anyone.
IDF-free, so plant size does not change routing. Descent never prefix-folds:
`migrat` in a task cannot *compose* `expertise.ef-migrations`. (Seeding still
folds — that is today's router and unchanged; a fold that beats the cut loads
the child the way it always has. The exact-only rule bounds what descent
adds, not what seeding does.) Explainable per child in one line.

*Distinctiveness, integrated.* `integrations/claude-code/agent-lint.py`
already has `_distinctiveness_warnings()` (L363) for `routing_triggers`;
`graph-lint` gets the same rule over `V` for composed children in two forms,
both ignoring terms the parent already carries (a term on the parent is
family vocabulary by design, not a defect) and both ignoring tokens under
three characters (mirroring `_terms`; `net8.0` yields `0` and `8`, which no
task can ever match, so they must not warn either): a term shared by two or
more siblings and absent from the parent ("move `<term>` to the parent"); a
term present in more than three nodes graph-wide ("sharpen `<term>`"). Both
warn.

*Explosion notice.* If one parent would descend into more than half its
children on one task, `--plan` prints a one-line notice and still loads them.

*Tokenizer fact.* `_terms` drops tokens under three characters, so "change the
EF mapping" yields only `mapping` (§E). Authoring rule: spell every trigger in
its ≥3-character forms. The spike evaluates keeping two-letter tokens that
are upper-case in the original text, adopted only with a golden test and no
change to existing expectations.

**Not being re-decided:** option A (expert agents spawning expert agents) is
rejected by the user and unsound against ADR-0001/0002. The narrow escape
hatch to a real agent remains and is exactly what the hybrid keeps.

---

## §1 Artifact discovery (all read, paths cited; line numbers verified 2026-09-09)

**Doctrine and contract**

- `CLAUDE.md` — gates, canonical homes, the 8 000-byte kernel budget, append-only
  artifacts, user-sovereign harvest/graft, "integrate, don't bolt on".
- `skills/holistic-editing/SKILL.md` — comprehend, locate, assess ripple,
  integrate, output the whole unit; forbidden moves; the class sweep; the
  append-only exception.
- `templates/knowledge-graph/_schema.md` (265 L) — intro edge list L21–L31;
  tiers table L43–L48; frontmatter subset L65–L98 (no nested maps, no inline
  lists — `libraries: [x]` must be written as indented `  - x` lines); node
  kinds L128–L163 (`deviation` L145–L152); key semantics L184–L211; body
  order L213–L219; rules 1–14 L221–L245 (rules 2, 12, 13, 14 are cited by
  number in `graph-lint.py` docstrings, so numbering is stable); anti-patterns
  L253–L265.
- `templates/knowledge-graph/graph-lint.py` (691 L) — PROJECT CONFIG L30–L54
  (`KINDS` L36–L37); `REQUIRED_KEYS` L62, `LIST_KEYS` L63; `Node` L113–L138;
  `load_nodes()` L192–L207 (skips `_*`, `index.md`); `check_schema` L219–L259;
  `check_status` L266–L291; `check_deviation` L293–L301; `check_edges`
  L387–L395; `check_acyclic` L398–L417 (hard-wired to `requires`, arrow `→`);
  `check_reachability` L420–L468 (traversals at L443 and L455 each hand-list
  `requires + peers`); `check_version_leakage` L496–L518; `check_budget`
  L521–L531; `_tokens` L537, `_match` L541–L552, `_terms` L555–L563,
  `resolve()` L566–L625 (`buckets` L576–L580; seed scoring L581–L606; closure
  loop L608–L617; peers L619–L624; returns `(loaded, skipped)`); `main()`
  L628–L687 (`--plan` L640–L651; `--graph` L653–L657; check list L661–L674).
  `resolve()` has exactly one caller, `main()` L641 (§E).
- `templates/knowledge-graph/node.template.md`, `index.md` (task-shape table;
  node table grouped "Roots / Stacks-Platform-Data-Cross-cutting-Domain /
  Subsystems").
- `templates/docs/nodes/_deviation.template.md` — the kind-template precedent:
  frontmatter with `<placeholders>`, a header comment explaining "Lives at",
  "Used", "Contract", and why the underscore keeps it out of the linter; body
  sections; a fenced YAML example. The expertise template mirrors this shape.
- `templates/library-page.template.md` — §0 Pin L15–L18 (`- **Version:**
  <exact>`), §6 deprecations, §8 upgrade path, §12 changelog.
- `skills/context-router/SKILL.md` — §2 "Resolve entry nodes", §3 "Take the
  required closure" (L129–L134 — descent belongs here), §4 "Do not take
  peers", §5 "Declare before you work" (the LOAD / NOT LOADED block L147–L165
  — reasons belong here), §6 "Widen honestly".
- `integrations/claude-code/agent-lint.py` — `_distinctiveness_warnings()`
  L363, the routing-trigger analogue of the `load_when` warnings M3 adds.
- `skills/knowledge-graph/SKILL.md` — L63 edge keys, L196–L212 rules and CLI.
- `templates/prompts/node-authoring-brief.md` — HARD RULES L61–L85.
- `templates/prompts/graph-session-bootstrap.md` — canonical block; **not edited**.
- `core/method/delegation.md` (250 L) — `## Route mechanically first` L70–L88;
  `## Every brief carries the graph discipline` L190–L226 (the task-line
  sentence lands here); owns `delegation.harness-registration`.
- `core/AGENTS.md` — no roster-gap wording; **no kernel edit**.
- ADR-0001, ADR-0002, ADR-0004, `docs/decisions/index.md`, `templates/adr.template.md`.

**Coverage machinery (7.3.0/7.4.0, uncommitted, folded into this release)**

- `tools/growth-audit.py` (1135 L) — `VERDICTS` L142; `KIND_PLAN` L169–L181;
  `SIGNIFICANCE` L184; `STAFFED_KINDS` L192; `slugify` L227; `required_collections`
  L233–L257 (skips `nodes/`); `parse_frontmatter` L260–L277; `is_substantive`
  L339–L369 (`template_text` parameter); `collection_leaves` L372–L384;
  `resolves` L387–L405; `plant_experts` L469–L499; `agent_scaffolds` L502–L516;
  `needs_staffing` L519–L522; `do_plan` L532–L626 (incidental `if` L578–L579
  — it flips paths **and** grounding, for `dependency` only; hint loop
  L607–L622); `check_row_shape` L629–L656; `empty_reads` L717–L731;
  `lint_agents` L734–L764; `lint_experts` L767–L907 (`agent_scaffolds()`
  called L785; byte-identity branch L828–L836; `is_substantive(...,
  agent_template)` L837); `lint_inventory` L908–L1035 (no `seed` parameter;
  staffing branch L971–L1000: `warranted is False` / else with `name` and
  `why`; comments L186–L191 and L971–L976 carry the 7.4.0 "the usual one"
  wording — S4 members); `template_bytes()` L308 (the byte index, built at
  L1089 in `do_lint`); `do_lint` L1051.
- `templates/prompts/growth-coverage-record.md` (220 L) — row sets L54–L79,
  staffing L98–L135, kind table L145–L157, JSON L166–L209.
- `templates/prompts/growth-evidence-ledger.md` (189 L) — §9 L101–L119.
- `templates/prompts/growth-author-brief.md` — ledger map L45–L85 (§9 line L52).
- `templates/agent.template.md` — `plant_knowledge:` L67–L69.
- `protocols/grow.md` (669 L) — shape L141–L159; Phase 4 L408–L529
  (`libraries/` bullet L417–L426; "Staff the project" L466–L500); Phase 5
  L531–L551; Phase 6 L553–L639.
- `protocols/graft.md` (916 L) — step (c) L290–L320; Phase 5 L465–L548; Phase 7
  L591–L716.
- `tools/graft-graph-engine.py` — unions `KINDS` on graft L160–L168.
- `tools/graft-audit.py` — `--unfilled` skips `_*` and `*.template.md` L273.
- `install.sh` — `place_docs_skeleton` L200–L218; `agent_projection_for` L792–L800.
- `manifest.json` — `templates[]` entries are `{"file", "produces"}` objects;
  the list carries **no** entry for `_deviation.template.md` (verified), so
  the new entry is appended, not placed beside one.

**Gates**

- `tests/run.sh`; baseline **exit 0** (2026-09-08 and 2026-09-09).
- `tests/seed-lint.py` (731 L) — machinery-node contract L265–L352; version
  pins and numeric claims L476–L527; intake parity L528–L677 (`KIND_PLAN` arm
  L594–L604, verdict arm L606–L616, template-key arm L643–L657, staffing token
  arm L659–L668, `plant_knowledge` validity L670–L677).
- `tests/test_graph_lint.py` — 27 `def test_` cases; `node_md()` helper
  L60–L100; `build_graph()` L108–L112 writes an `index.md` that **lists every
  node id**, so reachability is satisfied by listing alone unless a test
  leaves a node unlisted; config injection by rewriting `KIND_PREFIX = {}`.
- `tests/test-growth-audit.sh` — cases `# --- 1.` … `# --- 27.`; case 21 "a
  form is not an expert" is the brace-stripped template case.
- `tests/test-unified-graph-install.sh` L25–L50 required list;
  `tests/test-orchestration-entry.sh` L36–L60 grep pins;
  `tests/test-graft-tools.sh`.

---

## §6 Decisions (contract)

- **C1 — Kind.** `expertise` joins `KINDS`. Ids `expertise.<slug>`, tier 2,
  `nodes/expertise.<slug>.md`, `origin: project`. Rules 10 and 11 apply. A
  `-<digits>` slug suffix is legal only on a child composed by the unversioned
  prefix node.
- **C2 — Edges.** `requires:` unchanged. `composes:` lazy, downward,
  expertise→expertise only, acyclic on its own; the union with `requires` is
  legitimately cyclic. Reciprocity.
- **C3 — Descent.** Delta-exact, recursive, visible, with distinctiveness
  warnings and the wide-descent notice.
- **C4 — Ownership.** An expertise node owns `<slug>.applicability` and
  `<slug>.composition`, never a version; ≥1 `libraries:`/`artifacts:` edge;
  body order In play for · Do not without · Composition · Version in play ·
  Depth.
- **C5 — Derivation.** An inventory item of kind `language`/`runtime`/
  `framework`/`dependency`/`infrastructure`/`datastore` with `significance`
  other than `incidental` owes `nodes/expertise.<slug>.md`; the first four
  kinds also owe `<slug>` in that node's `libraries:` list. Two majors of one slug owe the
  parent plus one child per major. Incidental items owe nothing new.
- **C6 — Seam.** `plant_knowledge:` entries are a collection, a row, or a node
  id. Seed agents use collections only. Plant experts may name a node id.
- **C7 — Staffing.** `warranted: true` requires `name`, `why`, and `needs` ∈
  {`tools`, `model`, `stance`, `isolation`}; anything else is `UNSTAFFED`.
- **C8 — Budget.** No kernel edit; every touched machinery node's `est_tokens`
  re-measured (`int(len(body.split()) * 1.35)`, body = text after the closing
  `---`): `protocols/grow.md`, `protocols/graft.md`, `protocols/recover.md`,
  `protocols/harvest.md`, `skills/context-router/SKILL.md`,
  `skills/knowledge-graph/SKILL.md`, `skills/adopt-existing/SKILL.md`,
  `core/method/delegation.md`, `agents/00-orchestrator.md`,
  `agents/growth-scout.md`, `agents/growth-orchestrator.md`. seed-lint's 2×
  arm is the backstop, not the measure.
- **C9 — One home.** Adapter mapping only in `install.sh`; collection set only
  in `required_collections()`; verdicts only in `VERDICTS`; canonical block
  untouched; the pin only in `libraries/`.

---

## §7 Options considered and discarded

- Compose through `requires:` — closure explosion by construction.
- Upward-only edge — reverse index, no menu.
- Versioned slugs everywhere — a pin in every referrer.
- `stack` replaced by `expertise` — breaks grown plants.
- Own `docs/graph/expertise/` directory — reads as a second graph.
- `expertise/` in seed agents' `plant_knowledge:` — not an agent row fact.
- Absolute score threshold — drifts with IDF.
- A depth cap — a second knob.
- A separate descent pass beside the closure loop — integrated instead (M3).
- A second cycle-check function — generalised instead (M3).
- A second scaffold helper beside `agent_scaffolds` — one resolver (M5).
- A new ledger §16 — §9 reworked instead (M4).

---

## §8 Integration discipline (binds every item in §9)

The unit of work is the whole file. For each file an item names, the executing
session, before editing: states the file's responsibilities and conventions;
locates where the change conceptually belongs; lists the ripple — helpers to
merge, branches that go dead, names and comments that go stale, tests the
change implies; rewrites the affected region as a whole; outputs the whole
revised unit. Deletion and consolidation are outcomes to report.

**Forbidden in this release, by name.** A second function beside one that
should generalise (`check_acyclic`, `agent_scaffolds`); a second traversal
beside the closure loop; an `if` for expertise beside the general rule
(`do_plan()`'s incidental `if` is folded into the plan function, not joined by
a sibling); a "7.5.0 says…" passage inserted into a protocol whose paragraph
should be rewritten; a `needs` check appended after the `warranted` branch
instead of inside it; a new section where an existing one owns the topic
(ledger §9); a parallel `NOT COMPOSED` section beside `NOT LOADED`.

**Class sweeps** (find every member, land once, report):

- **S1 — edge-key enumerations:** `_schema.md` (intro list L23–L28,
  frontmatter block, key semantics, rule 5 L227), `node.template.md`,
  `skills/knowledge-graph/SKILL.md` L63, `skills/adopt-existing/SKILL.md` L97,
  `node-authoring-brief.md` rules 2/5, `templates/knowledge-graph/index.md`
  L22, `agents/growth-orchestrator.md` L100, `DOCUMENTATION.md` and
  `documentation/skills-and-templates-reference.md` where they describe edges
  — including L1234–L1238, which describes `check_edges`/`check_acyclic`
  internals M3 changes.
- **S2 — kind enumerations:** `_schema.md` kinds list, `graph-lint.py` `KINDS`,
  the `index.md` node table, the documentation's kind list. The new seed-lint
  arm makes S2 mechanical thereafter.
- **S3 — what an inventory kind owes:** `KIND_PLAN`, the record doc's kind
  table, grow Phase 4's collection list, `protocols-reference.md`,
  `skills-and-templates-reference.md`.
- **S4 — the staffing decision and the "commission first" spine:** grow
  Phase 4, the record doc, the author brief §9 line, `delegation.md` L70–L88,
  `agent.template.md` header, `DOCUMENTATION.md` L285–L286 and §7 item 6,
  `protocols-reference.md` L823 and L1598–L1625, `agents/00-orchestrator.md`
  L134 ("On LOW/NONE, commission first"), `documentation/agents-reference.md`
  L21, `protocols/recover.md` L46, `protocols/harvest.md` L494,
  `templates/prompts/investigation-brief.md` L51, and the audit's own
  comments `tools/growth-audit.py` L186–L191 and L971–L976 ("the usual
  one"). Each member is rewritten in its own voice to the 7.5.0 shape:
  knowledge → an expertise node; judgment needing its own context → an agent.
- **S5 — template-less substance measurement:** `is_substantive()` callers
  that supply `template_text` (agents today, expertise now). One resolver.
- **S6 — the two hand-listed traversals** in `check_reachability` (L443, L455).
- **S7 — the folded 7.4.0 prose:** CHANGELOG entry (superseded in place),
  `DOCUMENTATION.md` L410–L420, `protocols-reference.md` L1598–L1625,
  `skills-and-templates-reference.md` L1488–L1510.
- **S8 — the ledger's §9 references** (verified: nine, in six files):
  `growth-author-brief.md` L52; `agents/growth-orchestrator.md` L106;
  `growth-coverage-record.md` L72, L101, L118; `protocols/grow.md` L478, L483;
  `documentation/skills-and-templates-reference.md` L1429, L1468. Every other
  `§9` in the repo is a spec §9 or a grill §9 and is untouched.

**Append-only exception.** Released `CHANGELOG.md` entries and every ADR are
never rewritten; the unreleased 7.4.0 entry is the one legitimate in-place
supersession. This plan's §15 is append-only.

**Self-check per item, recorded in the handback.** Whole file read? Diff
purely additive — if so, why? Anything now in two places? Sibling defect
elsewhere — did I look? Names, comments, docs still true? Could a reader tell
where the patch was stitched in?

---

## §9 Implementation — waves, single-writer file ownership

### Wave 0 — Freeze the base

#### M0 — Confirm the base; no separate 7.4.0 commit (Q4)

`git status --porcelain` shows the 17 modified files and this plan;
`bash tests/run.sh` → 0. No commit, no push, no `git checkout`. Copy any file
you will mutation-test into the scratchpad first.

### Wave 1 — The load-bearing spike

#### M1 — Prove delta-exact descent fits the closure loop (D9)

- **Files.** A scratch copy of `graph-lint.py` and the fixture in §B, in the
  scratchpad. Nothing in the repo changes.
- **RED first, or the spike proves nothing.** The independent review ran the
  §B fixture on the **unmodified** tool and found every child of the first
  draft's tasks loaded by seeding alone (their triggers beat the top-3/floor
  cut), so a descent mechanism was never exercised. The spike therefore runs
  in two passes. *Pass A (unmodified copy):* run each task below and record
  LOAD. A task qualifies for the descent battery only if its target child is
  **absent** from LOAD on the unmodified tool. Reword a task (make the
  subsystem the loud subject; name the child by one exact term) until it
  qualifies, and record the final wording in §15. *Pass B (§A.1 applied):*
  the same tasks; the child must now appear with the provenance line
  `composed by <parent> on "<term>"`, and every un-composed sibling under
  NOT LOADED with its reason.
- **Fixture discipline.** Every added node changes document frequencies and
  therefore the seed floor, so pass-A wording is **fixture-specific**. Tasks
  1–7 run on §B exactly as written (eight nodes). Task 8 runs on a separate
  copy with `subsystem.checkout` and `subsystem.billing` added. Each
  `test_plan_*` in M3 builds exactly the node set its docstring records.
- **Tasks (wordings verified RED on the unmodified tool by the independent
  review, 2026-09-09; re-verify in pass A, since any fixture edit moves the
  floor).**
  1. `"in the orders service, fix the mapping"` → unmodified LOAD `dotnet,
     orders`. Pass B: `ef-core` composed by `expertise.dotnet` on `mapping`,
     reached through the **required** parent; `serilog`, `dotnet-8`,
     `dotnet-10` under NOT LOADED with their reason.
  2. `"in the orders service, add a sink"` → unmodified LOAD `dotnet, orders`
     (with "log sink" the child seeds itself: `log`+`sink` = 12 ≥ floor).
     Pass B: `serilog` on `sink`; `ef-core` listed with its reason.
  3. `"rename the orders service"` → no child composed; four siblings listed.
  4. `"in the orders service, editing the dbcontext, write the migration"` →
     unmodified LOAD `dotnet, orders` (`editing` lifts `orders` to 30, floor
     15; `ef-migrations` 12 and `ef-core` 6 are cut). Pass B: `ef-core` on
     `dbcontext`, then `ef-migrations` on `migration`: two levels, each on
     its own term. (The shorter "write the migration script" seeds
     `ef-migrations` through its title and is not a descent case; do not use
     it.)
  5. `"in the orders service, target net10.0"` → unmodified LOAD `dotnet,
     orders` on §B as written (with the task-8 nodes present the floor drops
     and `dotnet-10` seeds — hence the fixture discipline above). Pass B:
     `dotnet-10` on `net10`; `dotnet-8` listed as not loaded.
  6. Give `serilog` the extra trigger `"dotnet logging"` and run `"in the
     orders service, fix the dotnet mapping"` → unmodified LOAD `dotnet,
     orders` (serilog's `dotnet` scores 4 < floor 12). Pass B: `ef-core` on
     `mapping`; `serilog` under NOT LOADED with `no task term specific to it`,
     because `dotnet` ∈ V(parent). This is `test_plan_ignores_family_vocabulary`'s
     task.
  7. `"in the orders service, fix the EF mapping"` → composes `ef-core` on
     `mapping` only; record that `EF` is dropped; evaluate the upper-case
     two-letter option (§A.1 note) with a golden test.
  8. Top-3 cut, on the copy with `checkout` and `billing`: `"orders service,
     checkout service, billing service: change the entity mapping"` →
     unmodified LOAD `dotnet, billing, checkout, orders` (`ef-core` cut from
     the top three). Pass B composes it on `entity` or `mapping`.
  9. `python3 tests/test_graph_lint.py` pointed at the scratch copy (set
     `GRAPH_LINT` by editing a scratch copy of the test): 27 pass.
- **Provenance decision (pinned now, so the golden in M3 is capturable):**
  LOAD lines keep today's shape `  {id:<28} {title}` for seeded and required
  nodes; **only composed nodes** carry a trailing `  ← composed by <parent>
  on "<term>"`. NOT LOADED becomes one section whose heading is
  `NOT LOADED (with the reason; cross only if the task requires it)` and
  whose lines are `  {id:<28} {reason}`.
- **Stop rule.** If task 1 or task 4's second form cannot go RED on pass A
  and GREEN with provenance on pass B without restructuring the loop, stop
  and report before M2.

### Wave 2 — Contract and engine

#### M2 — `_schema.md`: the contract reads as if expertise had always existed (Q1–Q3, D5, D8; S1, S2)

- **File.** `templates/knowledge-graph/_schema.md`.
- **Integration.** The intro list (L21–L31) gains `composes:` as its third edge
  in the same voice, so "a traversal with a stopping rule" describes all three
  from the start. The frontmatter block carries `composes:` between `peers:`
  and `libraries:` (comment: "lazy, downward; expertise nodes only; the router
  descends only into children the task names specifically"). The kinds list:
  the `stack` bullet is rewritten to state the D5 seam from its side
  ("project conventions; requires the matching `expertise.*`"), and the
  `expertise` bullet follows it (§C.2). Key semantics: a `composes` paragraph
  after `peers` (§C.3); the `requires` paragraph's "Must be acyclic" becomes
  "Must be acyclic on its own (see `composes`)". Body order: the expertise
  variant stated where body order is stated. Rules 15–19 appended (§C.4).
  Anti-patterns: three new ones woven beside their kin. CLI block: `--graph`
  prints `composes` as `~>`.
- **What dies.** The intro's two-bullet edge list (L23–L28) as a pair; the
  bare "Must be acyclic" at L192–L194; rule 5's "`requires`/`peers`" pair
  (L227). Grep found no literal "two edges" phrase; these three are the
  places that *imply* two.

#### M3 — Engine: kind, edge, checks, router, output (M1, M2; S2, S6)

- **Files.** `templates/knowledge-graph/graph-lint.py`, `tests/test_graph_lint.py`.
- **Integration, by region** (code in §A.1–§A.3).
  - `KINDS` includes `"expertise"`. `LIST_KEYS` includes `"composes"`.
  - `TRAVERSAL_EDGES = ("requires", "peers", "composes")` beside `LIST_KEYS`,
    and `Node.out_edges()` returns their union; both traversals in
    `check_reachability` call it (S6).
  - `check_edges` iterates `("requires", "peers", "composes")`; for
    `composes` it also errors unless both ends are `kind: expertise`.
  - `check_acyclic(nodes, errs, key="requires", arrow="→")`; `main()` calls
    it for `requires` and for `composes` (`arrow="~>"`). Docstring says why the
    union is not checked.
  - `check_expertise(n, errs, by_id)` beside `check_deviation`: ≥1 depth edge;
    reciprocity; the `-\d+$` slug rule (§A.2).
  - `check_trigger_distinctiveness(nodes, warns)`: shared-sibling and
    graph-wide forms, composed children only.
  - `resolve()`: descent inside the closure loop; **one return contract,
    stated here and in §A.1:** `loaded: list[tuple[Node, str]]` (node, how —
    `entry`, `requires of <id>`, or `composed by <id> on "<term>"`),
    `not_loaded: list[tuple[Node, str]]` (node, reason), `notices: list[str]`
    (the wide-descent lines). The peers block dissolves into `not_loaded`.
    `main()` is the only caller (§E) and is rewritten for that shape with the
    M1 provenance decision; `--graph` prints `~>` edges in the same loop.
    Module docstring's usage lines updated.
- **What dies.** The hand-listed `requires + peers` at L443/L455; the
  `skipped` dict; the peers-only NOT LOADED heading text; the two-value
  unpack at L641.
- **Tests.** `node_md()` gains `peers=()`, `composes=()`, `libraries=()`,
  `artifacts=()` kwargs (it has none of them today — the golden fixture and
  the not-loaded-reason test need peers); `build_graph()` gains `listed=None`
  (default: every id, as today)
  so a test can leave a node **unlisted** in `index.md`; expertise fixtures
  write a `libraries/<x>.md` file. **Every `test_plan_*` asserts the
  provenance line or the not-loaded reason, never bare membership**, and
  every descent case uses a task on which the child is not seeded (the M1
  pass-A wording; the test's docstring records the pre-change LOAD it was
  verified against). Cases: `test_expertise_kind_in_nodes_dir`,
  `test_composes_target_must_resolve`, `test_composes_self_edge_fails`,
  `test_composes_only_between_expertise_nodes`, `test_composes_cycle_fails`,
  `test_requires_composes_pair_is_not_a_cycle`,
  `test_child_requires_parent_needs_reciprocal_composes`,
  `test_expertise_without_depth_edge_fails`,
  `test_versioned_slug_only_as_composed_child`,
  `test_reachable_only_through_composes_passes` (the child **unlisted** in
  `index.md`; reachable only via `~>`), `test_shared_sibling_trigger_warns`,
  `test_generic_child_trigger_warns`, `test_parent_terms_do_not_warn`
  (a term on the parent and both children warns nothing; a `0` token from
  `net8.0` on two siblings warns nothing),
  `test_plan_descends_on_specific_term`, `test_plan_ignores_family_vocabulary`
  (the child's only hit is a parent word → not composed, reason printed),
  `test_plan_descent_never_folds` (the child's own nine-character trigger,
  the task's eight-character prefix of it, task otherwise dominated by a
  subsystem so seeding's fold stays under the floor → not composed),
  `test_plan_descends_from_required_node`,
  `test_plan_descends_two_levels_each_on_own_term`,
  `test_plan_selects_major_by_tfm_token`,
  `test_plan_reports_not_loaded_with_reason`,
  `test_plan_without_composes_is_unchanged` — **golden over id sets, not
  stdout:** on a composes-free fixture with peers, the set of LOAD ids and
  the set of NOT LOADED ids (first column of each line) equal what the
  unmodified tool printed, captured into the test as literals **before** M3
  edits the tool.
- **Mutation checks** (§D rows 1–10 and 23).

### Wave 3 — The kind exists in the seed's intake

#### M4 — Templates, router index, protocol prose, ledger, parity (M2, M3, D6; S1–S3, S8)

- **Files (one writer each), each treated as a whole.**
  - `templates/docs/nodes/_expertise.template.md` (new; §C.5 gives the
    frontmatter and header comment verbatim, mirroring the deviation template).
  - `templates/library-page.template.md` — §0 Pin reworked to the "Versions in
    play" shape (§C.6).
  - `templates/knowledge-graph/index.md` — task-shape row "Working against
    {{framework or library}}" → `expertise.{{slug}}` after the stack row; the
    existing second node table is retitled "Stacks / Expertise / Platform /
    Data / Cross-cutting / Domain" and gains the row
    `| \`expertise.{{lib}}\` | applicability, composition | {{n}} |`.
  - `manifest.json` `templates[]` — append `{"file":
    "templates/docs/nodes/_expertise.template.md", "produces":
    "docs/graph/nodes/expertise.<slug>.md (one per core or significant stack
    element; applicability and composition only)"}`; the list has no
    deviation-template entry to sit beside (§E).
  - `protocols/grow.md` — shape diagram's `nodes/` line →
    `nodes/            (project facts · expertise.* · deviation.*)`; Phase 4's
    `libraries/` bullet (L417–L426) rewritten so it, `best-practices/`, and
    `expertise.*` are described as three artifacts authored from the same
    §5/§9/§14 evidence and the same retrieved sources, the node owning
    applicability and composition only and routing to the other two; "Staff
    the project" (L466–L500) rewritten per M7 (§C.7); Phase 5 librarian bullet
    on pass-throughs cites the new warnings; Phase 6 item 5 rewritten to
    include descent. **Verdict-arm trap:** seed-lint L609–L616 fails any
    backticked all-caps word of four or more letters in grow/graft that is
    not a verdict or status — write "the LOAD list" or `--plan`'s load list,
    never `` `LOAD` ``. `est_tokens` re-measured.
  - `templates/prompts/growth-evidence-ledger.md` — §9 reworked (§C.8).
  - `templates/prompts/growth-author-brief.md` — §9 line L52 rewritten for
    both deliverables; `libraries/` and `best-practices/` lines say the
    expertise node is authored from the same sources and restates neither.
  - `templates/prompts/growth-coverage-record.md` — kind table rewritten with
    an "expertise node" column (§C.9); two-majors rule in its note; JSON
    example's `expect` shows the path; staffing section per M7.
  - `agents/growth-scout.md` L92–L100 (it says "project-specific specialist
    agents" without citing §9) and `agents/growth-orchestrator.md` L106 (cites
    §9) — each sentence rewritten to the new scope (expertise nodes first,
    agents by trigger); `est_tokens`.
  - `tests/seed-lint.py` — in the intake-parity block: `LIST_KEYS` ⊆
    backticked keys in `_schema.md`; schema kinds == `KINDS` (parse
    `^- \`([a-z]+)\`` bullets under "### Node kinds"); the template-key arm
    generalised to a table `{template: [required line regexes]}` covering
    `agent.template.md` and `_expertise.template.md` (`^kind: expertise`,
    `^composes:`, `^libraries:`, `^id: expertise\.`).
  - `tests/test-unified-graph-install.sh` — `docs/graph/nodes/_expertise.template.md`
    in the required list. `tests/test-orchestration-entry.sh` — pins:
    `composes:` in `protocols/grow.md` and `_schema.md`; `Version in play` in
    the template; the reworked §9 heading in the ledger.
- **What dies.** The old §9 heading and agent-only framing; the `libraries/`
  bullet's stand-alone description; the scalar `Version:` line; the
  single-template shape of the seed-lint template-key arm.
- **Mutation checks** (§D rows 11–14).

### Wave 4 — The audit holds plants to it

#### M5 — Derivation in the audit (M4, C5; S3, S5)

- **Files.** `tools/growth-audit.py`, `tests/test-growth-audit.sh`.
- **Integration** (code in §A.4–§A.5).
  - `KIND_PLAN` values become `(paths, grounded, expertise)`; a
    `planned_artifacts(item, majors)` function beside it owns every rule
    (base paths; the incidental exception **exactly as today** — a
    `dependency` marked incidental owes an index line and no grounding, and
    an incidental item of any other kind keeps its kind's paths and
    grounding; no expertise node for any incidental item; expertise for
    non-incidental of the six kinds; per-major children). The incidental
    `if` at L578–L579 dies; `do_plan()` calls the function. The seed-lint
    `KIND_PLAN` arm still reads the same keys.
  - `majors_in_play(rec, slug)` beside `slugify()`.
  - `agent_scaffolds()` generalised to `scaffold_for(seed, rel)` (S5):
    `agents/*.md` → (agent template text, seed roster blobs);
    `nodes/expertise.*.md` → (expertise template text, ∅); else `(None, ∅)`.
    `is_substantive()` consults it when `templates.get(rel)` is `None`. It
    needs the seed path, and `lint_inventory()` has none (L908): make
    `template_bytes()` (L308, built once at L1089) return a small
    `Templates` object carrying the byte index **and** `seed`, so every
    existing `templates` argument keeps flowing unchanged and no caller gains
    a parameter. `lint_experts()` stops passing `agent_template`, and its
    byte-identity branch reads the blobs from the resolver.
  - `lint_inventory()`: in the `expect` loop, an expertise path on an
    incidental item is `BLANK`; after substance, for `PINNED_KINDS` the
    node's `libraries:` must name the slug, else `HOLLOW` ("routes to no pin
    home"). `NEEDS COMPOSITION` joins the existing hint loop.
  - Module docstring's PLAN paragraph rewritten to include expertise.
- **What dies.** The incidental `if`; `agent_scaffolds` as a name; explicit
  `template_text` arguments at call sites.
- **Tests (cases 28–34, same helpers).** 28 core runtime plans
  `nodes/expertise.dotnet.md` and reports `UNGROWN`; 29 significant dependency
  plans; 30 incidental dependency does not (and an incidental `runtime` keeps
  its `libraries/` and `best-practices/` paths and its grounding — today's
  behaviour, pinned); 31 a copy of the expertise template with every
  `{{ }}` placeholder replaced by a short word and nothing else written is
  `HOLLOW` — the template uses `{{ }}` placeholders (§C.5) precisely so the
  existing `PLACEHOLDER` regex and `_norm()` brace-stripping (L155–L161,
  L321–L336) measure it the way they measure an agent file; 32 a node whose
  `libraries:` list does not name `dotnet` is `HOLLOW`; 33 two `dotnet` rows
  at 8.0 and 10.0 plan three paths and print `NEEDS COMPOSITION`; 34 a plant
  whose only item is incidental is **green** with no expertise rows. Cases
  15–27 unchanged (the S5 uniformity check).
- **Mutation checks** (§D rows 15–20).

#### M6 — `plant_knowledge:` node ids for plant experts (D7; C6)

- **Files.** `tools/growth-audit.py`, `tests/test-growth-audit.sh`,
  `templates/agent.template.md`, `protocols/graft.md` step (c).
- **Integration** (§A.6). `empty_reads()` is rewritten around one
  `read_target(plant, entry)` that yields the files behind a collection, a
  row, or a **project** node id (`nodes/<id>.md`); substance is measured
  through `scaffold_for`. Machinery ids are not accepted: a plant expert
  reads project knowledge, and machinery files carry `NN-` prefixed natural
  names the id does not encode (`graph-lint.py` L248–L255). `lint_experts()`
  reports an unresolvable node id as `DANGLING` beside the dangling-citation
  check. `agent.template.md` L67–L69: one collection example, one node
  example. **seed-lint is unchanged:** its validity arm (L670–L677) already
  rejects any entry that is not a collection, a row, or a template leaf, so
  "the seed cannot name a plant node" is today's behaviour; the executing
  session verifies it on a scratch copy of an agent file and records the
  message in §15.
- **What dies.** The collection-only assumption in `empty_reads()`.
- **Tests.** 35 plant expert naming a substantive `expertise.dotnet` passes;
  36 missing → `DANGLING`; 37 scaffold → `CONTRADICTED`.
- **Mutation checks** (§D row 21).

### Wave 5 — Doctrine follows the mechanism

#### M7 — Staffing: the node is owed, an agent needs a trigger (Q4, D7, C7; S4)

- **Files.** `tools/growth-audit.py` (staffing branch L971–L1000 and the
  comments at L186–L191), `protocols/grow.md`,
  `templates/prompts/growth-coverage-record.md`,
  `templates/prompts/growth-author-brief.md`, `core/method/delegation.md`
  (L70–L88, L190–L226), `templates/agent.template.md` header,
  `agents/00-orchestrator.md` L134, `protocols/recover.md` L46,
  `protocols/harvest.md` L494, `templates/prompts/investigation-brief.md`
  L51 (the S4 members that carry the "commission first" spine),
  `tests/test-growth-audit.sh`, `tests/seed-lint.py` (token arm L659–L668).
  The three documentation members of S4 (`agents-reference.md` L21,
  `DOCUMENTATION.md` L285–L286, `protocols-reference.md` L823) land in M11,
  which names them.
- **Integration.** `SPAWN_TRIGGERS = ("tools", "model", "stance", "isolation")`
  beside `STAFFED_KINDS`; inside the `warranted is True` branch, after `name`
  and `why`, `needs` must be in it (§A.7). `NEEDS EXPERT` hint rewritten. grow
  "Staff the project" rewritten as §C.7. Record doc staffing section rewritten
  to the same shape with `needs` in both JSON examples. `delegation.md` "Route
  mechanically first" restructured (§C.10); the brief-discipline section says
  the task line is written in the domain's words because it is what routes the
  worker's expertise closure. `agent.template.md` header's "when to commission"
  sentence points at the four triggers. seed-lint token arm includes `needs`.
- **What dies.** "Declining is the usual answer" and its echoes (S4); the
  "LOW/NONE → corpus → commission" spine.
- **Tests.** 38: `warranted: true` with `name` and `why` but no `needs` →
  `UNSTAFFED`; with `needs: isolation` → passes. Grep pins for the four
  triggers in grow.md and the record doc.
- **Mutation** (§D row 22).

#### M8 — Router-facing skills and briefs (M3; S1)

- **Files.** `skills/context-router/SKILL.md`, `skills/knowledge-graph/SKILL.md`,
  `templates/prompts/node-authoring-brief.md`.
- **Integration.** context-router §3 "Take the required closure" (L129–L134)
  is rewritten as "Take the closure": requires transitively, and from any
  loaded expertise node the composed children the task names specifically —
  the one sentence of the rule, and that a child you needed but that was not
  composed is a trigger to sharpen in the same commit. §5's declaration block
  (L147–L165) gains the not-loaded reason forms (`peer — owns X` and
  `composed by X; no task term specific to it`) and a line under "Tier-3 to
  open on demand" that identity picks the leaf via the node's Depth map. §4
  unchanged. knowledge-graph SKILL: the edge list (L63) names three edges;
  the rules summary (L196–L212) is a nine-item list with its own numbering
  that cites "schema rules 12–14" — its item 3 is extended to `composes`
  and one item is added pointing at schema rules 15–19 (do **not** renumber
  it to nineteen); the `load_when` authoring paragraph gains the
  "≥3-character, the child's own words" rule. `skills/adopt-existing/SKILL.md`
  L97 (S1) names the third edge. node-authoring-brief rules 2 and 5 name
  `composes` in the same breath as `requires`/`peers`. `route-hook.py`
  unchanged. `est_tokens` re-measured.
- **Tests.** `test-orchestration-entry.sh`: the reason phrase `no task term
  specific to it` in context-router; seed-lint `est_tokens` and canonical-block
  arms.

#### M9 — Graft carries it to living plants (M4–M6; D5)

- **Files.** `protocols/graft.md`, `tests/test-graft-tools.sh`.
- **Integration.** Phase 5's paragraph on rows an older plant gains names
  expertise among them, with the D5 move rule in the sentence that already
  says how a new row is grown from the plant's own facts. Phase 7's
  machinery-healthy bullet names the `composes` rules among what the upgraded
  engine enforces. Step (c)'s `plant_knowledge:` clause reads "the collections
  or expertise nodes it must be able to read". No new bullets. `est_tokens`.
- **Tests.** None new: `tests/test-graft-tools.sh` L22–L47 already proves the
  `KINDS` union with a stub engine, and the seed-lint kinds arm (M4) proves
  the seed's shipped `KINDS` carries `expertise`; together they cover the
  claim. A new case would earn its place only by running the real
  `graph-lint.py` through the engine graft, which the M12 scratch-plant run
  does end to end.

### Wave 6 — Record, version, verify

#### M10 — ADR-0005

`docs/decisions/adr-0005-composable-expertise-as-graph-nodes.md` from
`templates/adr.template.md` (frontmatter `status: accepted`, `status_date`);
a row in `docs/decisions/index.md`. Sections: Context; Decision (kind + lazy
edge + delta-exact descent + hybrid escape hatch; D5 seam; unversioned slugs
with the two-majors exception; expertise called by agents, not carried by
rows); Consequences; Alternatives (§7); Reversibility (additive; fold back
into `stack.*` by graft); References (this plan, CHANGELOG 7.5.0, ADR-0001/2/4).

#### M11 — Version, CHANGELOG, documentation, `est_tokens` (S7)

`manifest.json` `7.5.0`. `CHANGELOG.md`: the unreleased 7.4.0 entry is
superseded in place by one `## 7.5.0` entry (§C.11 skeleton) in one voice.
`DOCUMENTATION.md` L10 and `documentation/README.md` L3 → 7.5.0; growth items
5–6 rewritten as one description; the graph section's edges cover three.
`documentation/protocols-reference.md` L1598–L1625 and
`skills-and-templates-reference.md` L1429, L1468, L1488–L1510 likewise;
`README.md` where it enumerates edges or templates. The S4 documentation
members land here: `documentation/agents-reference.md` L21,
`DOCUMENTATION.md` L285–L286, `documentation/protocols-reference.md` L823.
`est_tokens` re-measured on every file in the C8 list. Self-check: no
sentence left that describes the 7.4.0 default or the "commission first"
spine.

#### M12 — Gate, mutation matrix, review, commit

`bash tests/run.sh` → 0. End-to-end on a scratch plant: install → `--plan`
with a two-major dotnet inventory → author the §B nodes by hand into the plant
→ lint green; `--plan "upgrade orders to net10.0"` composes `dotnet-10` only.
Fill §D with results. Reviewer spawn on `agents/03-reviewer.md`, scoped to the
diff, briefed with §8 as its coherence bar, attacking for false greens and
mutation-testing the gates, restoring from copies. Fix criticals and majors;
gate again. One commit, single-line version style, the user's attribution
rule; no push.

### Optional follow-on (not in done criteria)

#### M13 — Corpus payoff

`library-corpus/` pages gain `## In play for` and `## Composes` sections;
`harvest.md` admits them; `ingest-library.md` step 0 and grow Phase 4 seed an
expertise node's `load_when` and `composes` candidates from them. Deferred
until a harvested plant proves the round trip.

---

## §10 Verification plan

| Claim | Proof |
|---|---|
| Delta-exact descent fits the closure loop, and decides something | M1 pass A RED on the unmodified tool, pass B GREEN with provenance, tasks 1–9 |
| Parent + only the task-specific children | `test_plan_descends_on_specific_term`, `..._ignores_family_vocabulary`, `..._descends_from_required_node`, `..._descent_never_folds` — each asserting provenance or reason on a task the unmodified tool does not seed |
| No explosion, no depth knob | `..._descends_two_levels_each_on_own_term`; the wide-descent notice never fires on §B's tasks |
| Version distinction | `..._selects_major_by_tfm_token`; cases 32–33; `test_expertise_without_depth_edge_fails`; `test_versioned_slug_only_as_composed_child` |
| Cycles | `test_composes_cycle_fails`, `test_requires_composes_pair_is_not_a_cycle` |
| Missed parent update is a lint error | reciprocity test |
| Expertise owed per item, never per agent | cases 28–34; `git diff agents/` touches no `plant_knowledge:` line (growth-scout, growth-orchestrator, and 00-orchestrator change prose only) |
| A plant owing none is green | case 34 |
| Staffing default | case 38 |
| Collapses kept old behaviour (S5, S6) | cases 15–27 unchanged; `test_plan_without_composes_is_unchanged`; the 27 pre-existing graph-lint cases |
| One home | rule 10 on expertise nodes; pin only in `libraries/`; adapter mapping only in `install.sh`; canonical block byte-identical |
| Kernel untouched | `git diff --stat core/AGENTS.md` empty |
| Every new check load-bearing | §D complete, every row red |
| Coherence | reviewer's §8 pass: no additive-only file without a stated reason |

---

## §11 Risks

- **Planner cannot express descent inside the loop** — M1 gates everything.
- **Over-growth per significant dependency** — `significance` is the valve;
  incidental over-growth is `BLANK`; narrow `planned_artifacts` to core-only
  for `dependency` if a pilot shows the grain is too fine.
- **`stack`/`expertise` two-home rot** — D5 seam + graft's move rule; reviewer.
- **Two-letter acronyms never route** — authoring rule; spike evaluates.
- **Family vocabulary left on children** — shared-sibling warning; NOT LOADED
  reasons.
- **Collapsing `agent_scaffolds` and the two traversals regresses 7.4.0** —
  cases 15–27 and the 27 graph-lint cases run before and after.
- **`est_tokens` drift** — every machinery body in the C8 list changes;
  re-measure each.
- **Dirty worktree** — copy aside; never `git checkout`.
- **§9 rework** — the nine S8 references, each rewritten in its own voice.
- **Frontmatter subset** — `libraries: [dotnet]` inline lists are illegal;
  every fixture and template writes indented `  - dotnet` lines.
- **`test_plan_without_composes_is_unchanged`** — capture the shipped tool's
  LOAD and NOT LOADED **id sets** on the fixture *before* M3 edits it and
  write them into the test as literals; stdout equality is impossible because
  M3 changes the NOT LOADED heading and adds a provenance suffix on composed
  lines.
- **Seeding masks descent** — a descent test whose task seeds the child
  proves nothing (the review's critical finding). Every descent case records
  in its docstring the unmodified tool's LOAD for its task, and the M1 pass A
  discipline is how those tasks are found.

---

## §12 Open questions and follow-ups

- Practical grain and whether any real plant has a sub-expertise that must
  *act*: pilot findings, not blockers.
- **Follow-up, not 7.5.0:** `empty_reads()` is all-of; an agent whose declared
  collection is legitimately absent can only be marked `ABSENT`. Fix at
  `read_target`: a collection row `ABSENT` with reason and searched paths
  counts as answered. Own increment, own test, own mutation.

---

## §13 Done criteria

- `bash tests/run.sh` exits 0 and the M12 scratch-plant run is green.
- `kind: expertise` lints in `nodes/`; `--plan` on §B returns the parent plus
  only the task-specific children, lists the rest with reasons, and the
  two-majors task composes the right major — by tests.
- §D is complete and every row is red.
- `--plan` derives `nodes/expertise.<slug>.md` for core/significant items and
  version-qualified children for two majors; a plant owing none is green with
  no expertise rows.
- No seed agent's `plant_knowledge:` changed.
- No fact has two homes; no function has a sibling copy; S1–S8 reported with
  members.
- `manifest.json` 7.5.0, one CHANGELOG entry superseding the unreleased 7.4.0
  entry, ADR-0005, `est_tokens` refreshed, documentation surfaces agree
  (seed-lint's version-pin arm is the check).
- The reviewer's §8 pass finds no file where a reader can tell where the
  change was stitched in.

---

## §14 Recommended next step

M0 then M1 in one session; record the observed `--plan` output, the
provenance-column decision, and the two-letter token finding in §15 before any
prose is written.

---

## §A Code sketches (shape, not verbatim; integrate into the file's conventions)

### A.1 `resolve()` with descent inside the closure loop

```python
def resolve(nodes: list, task: str):
    """Mirror the traversal in skills/context-router/SKILL.md.

    Seeds score IDF-weighted; the closure follows `requires` eagerly and
    `composes` lazily — a composed child loads only when the task names,
    exactly, a term in the child's OWN vocabulary (its tokens minus its
    parent's). Returns (loaded, not_loaded, notices): loaded pairs each
    node with how it got there, not_loaded pairs each node with the reason
    it stayed out (a peer, or an un-composed child), notices are the
    wide-descent lines.
    """
    by_id = {n.id: n for n in nodes}
    terms = _terms(task)
    ...                                          # unchanged bucket build, df, weight, seeds
    # descent vocabulary (D9): load_when tokens plus the slug kept WHOLE —
    # never id fragments ("core" must not compose ef-core); seed scoring
    # keeps using the fuller buckets, which also carry title/repo words
    trig = {n.id: _tokens(" ".join(n.get_list("load_when"))) | {n.id.split(".", 1)[-1]}
            for n in nodes}

    loaded: list = []                            # [(Node, how)] in load order
    seen: set = set()
    reasons: dict = {}                           # id -> reason (not loaded)
    notices: list = []
    stack = [(n, "entry") for n in seeds]
    while stack:
        n, how = stack.pop()
        if n.id in seen:
            continue
        seen.add(n.id)
        loaded.append((n, how))
        for r in n.get_list("requires"):
            if r in by_id:
                stack.append((by_id[r], f"requires of {n.id}"))
        if n.meta.get("kind") != "expertise":
            continue
        kids = [by_id[c] for c in n.get_list("composes") if c in by_id]
        hits = 0
        for c in kids:
            own = trig[c.id] - trig[n.id]
            term = next((t for t in sorted(terms) if _match(t, own) == 2), None)
            if term:
                hits += 1
                stack.append((c, f'composed by {n.id} on "{term}"'))
            else:
                reasons.setdefault(c.id, f"composed by {n.id}; no task term specific to it")
        if kids and hits * 2 > len(kids):
            notices.append(f"wide descent from {n.id}: {hits} of {len(kids)} children — the task or the triggers are too generic")
    for n, _ in loaded:
        for p in n.get_list("peers"):
            if p in by_id:
                reasons.setdefault(p, f"peer of {n.id} — cross only if the task requires it")
    not_loaded = [(by_id[i], r) for i, r in reasons.items() if i not in seen]
    return loaded, not_loaded, notices
```

Notes: `sorted(terms)` makes the reported term deterministic. A child
recorded as not loaded and later loaded through another path drops out in
the final comprehension (`seen` is the authority). `main()` prints
`notices` once, before the lists. The `loaded` list preserves load order;
`main()` sorts by id as today. Two-letter option: in `_terms`, keep a part
when `len(part) == 2 and part.upper() in task` — evaluate in M1 only.

### A.2 Per-kind check for expertise (beside `check_deviation`)

```python
VERSIONED_SLUG_RE = re.compile(r"^(?P<base>expertise\.[a-z0-9-]+?)-(?P<major>\d+)$")

def check_expertise(n: Node, errs: list, by_id: dict) -> None:
    """Rules 18–19 and 17: an expertise node routes somewhere, a child's
    upward `requires` is mirrored by the parent's `composes`, and a version
    suffix exists only under an unversioned parent that composes it."""
    if n.meta.get("kind") != "expertise":
        return
    if not (n.get_list("libraries") or n.get_list("artifacts")):
        errs.append(f"{n.id}: expertise node with no libraries/artifacts edge — routes to nothing")
    for r in n.get_list("requires"):
        p = by_id.get(r)
        if p and p.meta.get("kind") == "expertise" and n.id not in p.get_list("composes"):
            errs.append(f"{n.id}: requires {r} but {r} does not compose it — add `  - {n.id}` under composes: in {p.path.name}")
    m = VERSIONED_SLUG_RE.match(n.id)
    if m:
        base = by_id.get(m.group("base"))
        if base is None or n.id not in base.get_list("composes"):
            errs.append(f"{n.id}: a versioned expertise slug is legal only as a child composed by {m.group('base')}")
```

### A.3 `check_acyclic` generalised; traversal edges owned once

```python
TRAVERSAL_EDGES = ("requires", "peers", "composes")

class Node:
    ...
    def out_edges(self) -> list:
        return [t for k in TRAVERSAL_EDGES for t in self.get_list(k)]

def check_acyclic(nodes: list, errs: list, key: str = "requires", arrow: str = "→") -> None:
    """`requires` and `composes` are each acyclic on their own. Their union is
    NOT checked: `parent composes child` + `child requires parent` is the
    intended shape (the eager edge points up, the lazy one down), and the
    router's loaded-set makes termination trivial."""
    graph = {n.id: list(n.get_list(key)) for n in nodes}
    ...                                          # same DFS; message f"{key} cycle: {arrow.join(...)}"
```

`main()`: `check_acyclic(nodes, errs)` and `check_acyclic(nodes, errs, "composes", " ~> ")`;
`check_reachability` uses `by_id[cur].out_edges()` in both traversals.

### A.4 `planned_artifacts` owns what a kind owes

```python
KIND_PLAN = {                    # kind -> (paths, grounded, expertise)
    "language":            (["libraries/{slug}.md", "best-practices/{slug}.md"], True,  True),
    "runtime":             (["libraries/{slug}.md", "best-practices/{slug}.md"], True,  True),
    "framework":           (["libraries/{slug}.md", "best-practices/{slug}.md"], True,  True),
    "dependency":          (["libraries/{slug}.md"],                              True,  True),
    "infrastructure":      (["architecture/{slug}.md", "best-practices/{slug}.md"], True, True),
    "datastore":           (["data/{slug}.md", "best-practices/{slug}.md"],       True,  True),
    "external-service":    (["architecture/{slug}.md"],                           True,  False),
    "ai-provider":         (["prompts/{slug}.md", "evaluations/{slug}.md"],       True,  False),
    "design-surface":      (["design/{slug}.md"],                                 True,  False),
    "regulatory-exposure": (["legal/{slug}.md"],                                  True,  False),
    "domain":              ([],                                                   False, False),
}
PINNED_KINDS = ("language", "runtime", "framework", "dependency")
EXPERTISE_PATH = "nodes/expertise.{slug}.md"

def planned_artifacts(item, majors):
    """Every rule about what an inventory item owes, in one place: the base
    paths per kind, the incidental exception (an index line, nothing
    retrieved, no node), the expertise node for a core or significant stack
    element, and one version-qualified child per major when a plant runs
    more than one. Returns (expect rows, grounding required)."""
    kind, slug = item.get("kind", ""), item["slug"]
    paths, ground, expertise = KIND_PLAN.get(kind, ([], False, False))
    incidental = item.get("significance") == "incidental"
    if incidental and kind == "dependency":
        # today's rule (do_plan L578–L579), unchanged: an index line, nothing retrieved
        return [{"path": "libraries/index.md", "why": f"{kind} {slug} — incidental"}], False
    rows = [{"path": p.format(slug=slug), "why": f"{kind} {slug}"} for p in paths]
    if incidental:
        # an incidental item of any other kind keeps its paths AND its
        # grounding exactly as today; it only never owes an expertise node
        return rows, ground
    if expertise:
        rows.append({"path": EXPERTISE_PATH.format(slug=slug),
                     "why": f"{kind} {slug} — applicability and composition"})
        for major in majors:
            rows.append({"path": EXPERTISE_PATH.format(slug=f"{slug}-{major}"),
                         "why": f"{kind} {slug} major {major} — applicability for this major"})
    return rows, ground
```

Check before landing: today only `dependency` + incidental is special-cased
(L578–L579), and it flips both paths and grounding; every other incidental
item keeps paths and grounding. The sketch preserves both facts; case 30
pins them.

### A.5 One scaffold resolver

```python
def scaffold_for(seed, rel):
    """What a plant file at `rel` must not still be, when no seed template
    sits at the same path: the form it was authored from, plus any seed file
    a copy would be byte-identical to. Agents (7.4.0) and expertise nodes
    are the two such shapes. Returns (template text or None, set of blobs)."""
    if rel.startswith("agents/"):
        tmpl = seed / "templates" / "agent.template.md"
        blobs = {p.read_bytes() for p in (seed / "agents").glob("*.md")}
    elif re.match(r"^nodes/expertise\.[a-z0-9.-]+\.md$", rel):
        tmpl = seed / "templates" / "docs" / "nodes" / "_expertise.template.md"
        blobs = set()
    else:
        return None, set()
    text = tmpl.read_text(encoding="utf-8", errors="replace") if tmpl.is_file() else ""
    if text:
        blobs.add(text.encode("utf-8"))
    return text, blobs
```

`is_substantive()` gains: `if template is None: text_t, blobs =
scaffold_for(templates.seed, rel); ...`. The seed path rides on the
`templates` argument: `template_bytes(seed)` (L308) returns a `Templates`
object (a dict subclass or a tiny class with `.seed`), built once in
`do_lint` (L1089) and already threaded to every caller — so no signature
changes and `lint_inventory()` needs no new parameter.

### A.6 One read resolver for `plant_knowledge`

```python
NODE_REF_RE = re.compile(r"^[a-z][a-z0-9-]*\.[a-z0-9.-]+$")

def read_target(plant, entry):
    """The files a plant_knowledge entry stands for: a collection's leaves, a
    single row, or a PROJECT node id's file (docs/graph/nodes/<id>.md —
    filename equals id there; machinery nodes carry NN- prefixed natural
    names and are not project knowledge, so they are not accepted)."""
    if entry.endswith("/") or entry.endswith(".md"):
        return collection_leaves(plant, entry)[0]
    if NODE_REF_RE.match(entry):
        f = plant / GRAPH_HOME / "nodes" / f"{entry}.md"
        return [f] if f.is_file() else []
    return []
```

### A.7 Staffing branch, `needs` inside it

```python
SPAWN_TRIGGERS = ("tools", "model", "stance", "isolation")
...
            else:                                   # warranted is True
                for key, msg in (("name", "warrants a project-specific expert and names none"),
                                 ("why",  "... gives no reason — the why is what the charter is written from")):
                    if not str(ex.get(key) or "").strip():
                        findings.append(Finding("UNSTAFFED", label, msg))
                if ex.get("needs") not in SPAWN_TRIGGERS:
                    findings.append(Finding("UNSTAFFED", label,
                        f"`needs` is {ex.get('needs')!r} — say which of "
                        f"{', '.join(SPAWN_TRIGGERS)} the expertise node cannot serve"))
```

---

## §B The M1 fixture (verbatim; frontmatter uses indented lists only)

`index.md` lists every id below in a table **except where a test needs a
node unlisted** (`test_reachable_only_through_composes_passes`; the M12
scratch-plant reachability check likewise leaves one child unlisted, or the
claim is vacuous — listing alone satisfies rule 7). `libraries/dotnet.md`
exists with a few hundred bytes of body. Bodies are **at least twelve
words** each (`check_budget` requires measured ≥ `est_tokens`/2, and
`est_tokens: 30` needs ~15 measured tokens); `est_tokens` derived from the
word count. Files are `nodes/<id>.md`. Titles carry ordinary words; descent
and the warnings read `load_when` plus the whole slug only, so titles and id
fragments cannot trip them, and sub-three-character tokens (`0`, `8` from
`net8.0`) never warn. **Slugs are triggers:** a slug typed whole in a task
composes its node, so choose slugs that are the library's own name. For the
top-3 task (M1 task 8) add `subsystem.checkout` and `subsystem.billing`
shaped like `subsystem.orders` **on a separate copy** — tasks 1–7 run on the
eight-node fixture, because every added node moves the seed floor.

```yaml
# nodes/root.md
---
id: root
tier: 2
kind: root
title: root — fixture
owns:
  - root.map
requires:
  - subsystem.orders
load_when:
  - "what is this project"
est_tokens: 30
---
```

```yaml
# nodes/subsystem.orders.md
---
id: subsystem.orders
tier: 2
kind: subsystem
title: orders — the orders service
owns:
  - orders.responsibility
requires:
  - expertise.dotnet
load_when:
  - "orders service"
  - "editing src/Orders/**"
est_tokens: 30
---
```

```yaml
# nodes/expertise.dotnet.md
---
id: expertise.dotnet
tier: 2
kind: expertise
origin: project
title: dotnet — when .NET expertise is in play, and what it composes
owns:
  - dotnet.applicability
  - dotnet.composition
requires:
composes:
  - expertise.ef-core
  - expertise.serilog
  - expertise.dotnet-8
  - expertise.dotnet-10
libraries:
  - dotnet
load_when:
  - "dotnet, .NET, csharp"
  - "target framework, runtime"
est_tokens: 30
---
```

```yaml
# nodes/expertise.ef-core.md
---
id: expertise.ef-core
tier: 2
kind: expertise
origin: project
title: ef-core — entity framework applicability
owns:
  - ef-core.applicability
  - ef-core.composition
requires:
  - expertise.dotnet
composes:
  - expertise.ef-migrations
libraries:
  - dotnet
load_when:
  - "entity framework, dbcontext"
  - "entity mapping, linq query"
est_tokens: 30
---
```

```yaml
# nodes/expertise.ef-migrations.md
---
id: expertise.ef-migrations
tier: 2
kind: expertise
origin: project
title: ef-migrations — schema migration applicability
owns:
  - ef-migrations.applicability
  - ef-migrations.composition
requires:
  - expertise.ef-core
libraries:
  - dotnet
load_when:
  - "add a migration, migration script"
  - "schema change"
est_tokens: 30
---
```

```yaml
# nodes/expertise.serilog.md
---
id: expertise.serilog
tier: 2
kind: expertise
origin: project
title: serilog — structured logging applicability
owns:
  - serilog.applicability
  - serilog.composition
requires:
  - expertise.dotnet
libraries:
  - dotnet
load_when:
  - "structured logging, log sink"
  - "enrichers"
est_tokens: 30
---
```

```yaml
# nodes/expertise.dotnet-8.md   (dotnet-10 identical with 10 / net10.0)
---
id: expertise.dotnet-8
tier: 2
kind: expertise
origin: project
title: dotnet-8 — applicability for the .NET 8 major
owns:
  - dotnet-8.applicability
  - dotnet-8.composition
requires:
  - expertise.dotnet
libraries:
  - dotnet
load_when:
  - "net8.0, .NET 8 target"
est_tokens: 30
---
```

Every `expertise.*` node's `composition` fact key is unique by slug, so rule
4 holds. `ef-migrations` and `serilog` compose nothing (their `composes:` is
absent), which is legal; the pass-through warning does not fire because each
is composed by a parent.

---

## §C Fixed text blocks

### C.1 "Version in play" (the template's section body, fixed)

> The pinned major(s) live in `libraries/<slug>.md` §0 — read the pin before
> writing anything against this stack. The pins are often old on purpose; the
> wiki is authoritative over memory. Behaviour that differs between majors is
> recorded there (§5 sharp edges, §6 deprecations), never here. Where this
> plant runs more than one major, the composition above lists one child per
> major; load the one whose target the task names.

### C.2 The `expertise` kind bullet (schema "Node kinds"), after `stack`

> - `stack` — a language/framework's shared conventions **in this project**:
>   layout, build, house rules, which projects target what. Requires the
>   matching `expertise.*` node; never restates its applicability.
> - `expertise` — **when** a language, runtime, framework, library, or
>   platform is in play for a task, what must not be done without it, and
>   which sub-expertises apply under which condition. Lives in `nodes/` as
>   `expertise.<slug>.md` (unversioned slug; see `composes`). Owns exactly
>   `<slug>.applicability` and `<slug>.composition`; every fact, pin, and
>   standard stays in `libraries/` and `best-practices/`, reached by
>   `libraries:`/`artifacts:` — an expertise node with no depth edge routes
>   to nothing and fails lint. When a plant runs two majors of one stack at
>   once, the unversioned node composes one child per major
>   (`expertise.dotnet-8`), the only place a version enters a slug; the
>   retired child is `superseded`.

### C.3 The `composes` paragraph (schema "Key semantics"), after `peers`

> **`composes`** — lazy, downward, and task-conditioned; expertise nodes
> only, toward expertise nodes only. Where `requires` is a closure the router
> always takes, `composes` is a menu it reads: a composed child loads only
> when the task names, exactly, a term in the child's own vocabulary — its
> `load_when` tokens and its whole slug, minus the parent's. Family words on the parent
> therefore never descend a child; a child's triggers must be its own.
> `composes` is acyclic on its own. Its union with `requires` is deliberately
> not: `parent composes child` and `child requires parent` is the intended
> shape (the eager edge points up, the lazy one down), and a child that
> `requires` an expertise node must appear in that node's `composes` — lint
> names the line to add. The router prints un-composed children as "not
> loaded" with the reason, so the choice is visible.

### C.4 Rules 15–19 (schema "The rules the linter enforces")

> 15. Every id in `composes` resolves, and both ends are `kind: expertise`.
> 16. `composes` is acyclic (its union with `requires` is not checked; see
>     `composes`).
> 17. An expertise node that `requires` an expertise node is listed in that
>     node's `composes`.
> 18. An expertise node has at least one `libraries` or `artifacts` edge.
> 19. An expertise id ending in `-<digits>` is composed by the id without the
>     suffix.

### C.5 `_expertise.template.md` frontmatter and header comment

Placeholders are `{{ }}`, not the deviation template's `<…>`: an expertise
node is measured by `growth-audit.py`, whose `PLACEHOLDER` regex and
`_norm()` brace-stripping (L155–L161, L321–L336) only know `{{ }}` — the
same reason `agent.template.md` uses them. (Bringing `<…>` under the same
measure is a class sweep that would touch deviation nodes; filed, not done.)

```yaml
---
id: expertise.{{slug}}
tier: 2
kind: expertise
origin: project
title: {{slug}} — when this expertise is in play, and what it composes
owns:
  - {{slug}}.applicability
  - {{slug}}.composition
requires:
  - {{the parent expertise, if this is a sub-expertise; else leave the key empty}}
composes:
  - {{a sub-expertise that applies under a condition of its own; else leave the key empty}}
libraries:
  - {{slug}}                        # the pin home; required for a pinned stack element
artifacts:
  - best-practices/{{slug}}.md      # the standard and this project's stance
load_when:
  - "{{the ≥3-character phrases a developer types when THIS is in play — never the family's words}}"
  - "{{another; a version-qualified child carries the target tokens, e.g. net8.0}}"
est_tokens: {{honest estimate of the body}}
---
```

```html
<!--
Template: docs/nodes/_expertise.template.md
Lives at: docs/graph/nodes/expertise.<slug>.md   (filename MUST equal the id)
Used: one file per core or significant language, runtime, framework,
dependency, infrastructure component, or datastore the stack inventory
carries (growth-audit plans the path; grow Phase 4 authors it from ledger
§5, §9, §14 and the same retrieved sources as its libraries/ and
best-practices/ leaves). The node owns applicability and composition and
nothing else — it routes to the pin and the standard, it never restates
them. Agents reach it through the router: the brief's task line is what
composes it in, and the Depth section tells each reader which leaf to open.
Contract: docs/graph/_schema.md — "Node kinds" (expertise), "Key semantics"
(composes), rules 15–19. The leading underscore keeps this blank form out of
the linter; the node you copy it to must not carry one.
-->
```

Body headings, in order: `## In play for` · `## Do not without` ·
`## Composition` (one line per child: `` `expertise.<child>` — when <condition> ``)
· `## Version in play` (C.1 verbatim) · `## Depth` (`API and pins →
libraries/<slug>.md · standard and stance → best-practices/<slug>.md ·
project conventions → stack.<slug>`).

### C.6 Library template §0 reworked

> ## 0. Pin
>
> | Major | Exact version | Projects / paths | Notes |
> |---|---|---|---|
> | <major> | <exact> | <where it is used> | <one row per major the plant runs; one row is the common case> |
>
> - **Registry / source:** <url>
> - **Lockfile / manifest line:** <path:line>

### C.7 grow Phase 4 "Staff the project" (rewritten as one paragraph)

> **Staff the project, and record the decision either way.** A plant is not
> only knowledge; it is also the expertise that knowledge is for. Every core
> or significant stack element owes an `expertise.*` node (the coverage plan
> derives it), and that node is the default answer to "who knows this here":
> the router composes it into any worker whose task names it. An **agent** is
> warranted only for what a node cannot serve — work that needs different
> `tools`, a different `model` class, an adversarial `stance`, or context
> `isolation` — and every inventory item of kind `domain` or marked
> `significance: core` closes its `expert` decision in the coverage record
> with `warranted`, a `why`, and, when true, the `needs` it names. A decision
> nobody recorded reads exactly like a §9 nobody opened. Where an agent is
> warranted, check the seed's `agent-corpus/` first, author from
> `docs/graph/templates/agent.template.md` and the cited evidence, mark it
> `origin: project`, declare its `plant_knowledge:` (collections or the
> expertise nodes it draws on), cite what motivated it, and project it to
> every path this plant's `.cypress/seed.json` records — unprojected it is on
> disk and unspawnable (`delegation.harness-registration`), and on most
> harnesses spawnable only in the next session; say so in the delivery.

### C.8 Ledger §9 reworked

> ## 9 — Expertise and specialist signals  → expertise.* nodes + project-specific expert agents
>
> - **Expertise (the usual outcome).** For each core or significant stack
>   element in §5/§0: the libraries and platform pieces it is used *with*
>   (call sites, `path:line`); the task shapes each is in play for, in the
>   ≥3-character words a developer would type (these become `load_when`);
>   what goes wrong without it (the applicability fact); and, from the
>   manifests, whether more than one major is in play. This is what an
>   `expertise.*` node is authored from; the node routes to the pin and the
>   standard and restates neither.
> - **Agents (the rare outcome).** Evidence that some sub-work needs its own
>   context: different tools, a different model class, an adversarial stance,
>   or context isolation. Each signal cites the source, names the recurring
>   task shape, the collections or expertise nodes it would read, and the
>   `needs` it satisfies. The author decides; the scout only supplies
>   grounded evidence.
> - `none found` is a real answer for either half and a common one for the
>   second; say it explicitly, because an unrecorded decision reads exactly
>   like a section nobody opened.

### C.9 Coverage-record kind table (rewritten)

> | kind | planned artifacts | expertise node | grounded |
> |---|---|---|---|
> | `language`, `runtime`, `framework` | `libraries/<slug>.md`, `best-practices/<slug>.md` | yes (its `libraries:` names `<slug>`) | yes |
> | `dependency` (core / significant) | `libraries/<slug>.md` | yes (its `libraries:` names `<slug>`) | yes |
> | `dependency` (incidental) | a line in `libraries/index.md` | no | no |
> | `infrastructure` | `architecture/<slug>.md`, `best-practices/<slug>.md` | yes | yes |
> | `datastore` | `data/<slug>.md`, `best-practices/<slug>.md` | yes | yes |
> | `external-service` | `architecture/<slug>.md` | no | yes |
> | `ai-provider` | `prompts/<slug>.md`, `evaluations/<slug>.md` | no | yes |
> | `design-surface` | `design/<slug>.md` | no | yes |
> | `regulatory-exposure` | `legal/<slug>.md` | no | yes |
> | `domain` | whatever the evidence names | no | no |
>
> An expertise node is `nodes/expertise.<slug>.md`. When the inventory
> carries one slug at two majors, the node composes one child per major
> (`nodes/expertise.<slug>-<major>.md`), and `--plan` says so.

### C.10 `delegation.md` "Route mechanically first" (restructured)

> Before spawning, run `python3 docs/graph/agent-lint.py --route "<task>"`
> and cite the ranked line + confidence band in the brief. It is a keyword
> heuristic, not an oracle — reason over it, and record why if you override a
> HIGH-band pick. On **LOW/NONE** ask first what the gap *is*. If it is
> **knowledge** — a stack, library, or platform nobody on the roster is
> written for — the answer is an `expertise.*` node, authored or extended
> (`docs/graph/nodes/_expertise.template.md`), which the router
> composes into any worker whose task names it; no agent is commissioned.
> If it is **judgment that needs its own context** — different tools, a
> different model class, an adversarial stance, or isolation — check the
> seed's `agent-corpus/` for the role first, then spawn an Opus-class
> agent-definition author to create the missing expert from
> `docs/graph/templates/agent.template.md`, grounded in the project's
> version-pinned facts (the `stack.*` node, the expertise node, the library
> wiki). A definition authored mid-session is not yet a spawnable type — see
> `delegation.harness-registration` below. (A *specialist* is a member of the
> shipped roster; an *expert* is one commissioned for this project. The
> words are otherwise interchangeable.) The expert's `model:` is sonnet if it
> only investigates, opus if it authors; the definition author is always
> opus.

### C.11 CHANGELOG 7.5.0 entry skeleton (supersedes the unreleased 7.4.0 entry in place)

> ## 7.5.0 — expertise composes through the graph: the staffing decision is recorded and spawnable, its default answer is a node, and the router descends (date)
>
> Opening: the two halves — 7.4.0's (staffing recorded where it survives;
> an expert spawnable) and 7.5.0's (expertise as a node kind called by agents
> through the router; the lazy edge; delta-exact descent; the version
> distinction; the fold).
>
> ### Added — `expertise` kind, `composes:` edge, delta-exact descent
> ### Added — `templates/docs/nodes/_expertise.template.md`
> ### Added — the expert row set and the staffing decision (7.4.0's text, in one voice)
> ### Added — `install.sh` records where a roster is spawnable from (7.4.0)
> ### Changed — `graph-lint.py` (checks 15–19; `--plan` prints provenance and reasons; `--graph` prints `~>`)
> ### Changed — `tools/growth-audit.py` (what a kind owes, in one place; expertise derivation; two majors; one scaffold resolver; `needs`; node ids in `plant_knowledge`)
> ### Changed — `_schema.md`, `library-page.template.md`, `index.md`
> ### Changed — `protocols/grow.md`, `protocols/graft.md`
> ### Changed — `growth-evidence-ledger.md` §9, `growth-coverage-record.md`, `growth-author-brief.md`, `agent.template.md`
> ### Changed — `skills/context-router`, `skills/knowledge-graph`, `method.delegation`
> ### Changed — tests (`test_graph_lint.py` +19; `test-growth-audit.sh` 28–38; seed-lint arms)

---

## §D Mutation matrix (fill during M3–M7; every row must be red)

| # | Check | Mutation (on a copy) | Test that goes red | Result |
|---|---|---|---|---|
| 1 | composes target resolves | drop `composes` from `check_edges` | `test_composes_target_must_resolve` | red |
| 2 | expertise-only ends | drop the kind test | `test_composes_only_between_expertise_nodes` | red |
| 3 | composes acyclic | call `check_acyclic` once | `test_composes_cycle_fails` | red |
| 4 | reciprocity | drop the loop in `check_expertise` | `test_child_requires_parent_needs_reciprocal_composes` | red |
| 5 | depth edge | drop the edge test | `test_expertise_without_depth_edge_fails` | red |
| 6 | versioned slug | drop the regex branch | `test_versioned_slug_only_as_composed_child` | red |
| 7 | reachability via composes | remove `composes` from `TRAVERSAL_EDGES` | `test_reachable_only_through_composes_passes` (child **unlisted** in `index.md`, else listing masks it) | red |
| 8 | exact-only descent | `== 2` → `>= 1` | `test_plan_descent_never_folds` | red |
| 9 | delta vocabulary | `own = trig[child]` | `test_plan_ignores_family_vocabulary` | red |
| 10 | not-loaded reasons | drop the reason string | `test_plan_reports_not_loaded_with_reason` | red |
| 11 | schema documents `composes` | remove the backticked key | seed-lint LIST_KEYS arm | red |
| 12 | schema kinds == KINDS | remove `expertise` from `KINDS` | seed-lint kinds arm | red |
| 13 | ledger §9 reworked | restore the old heading | `test-orchestration-entry.sh` pin | red |
| 14 | template keys | remove `libraries:` from the template | seed-lint template-key arm | red |
| 15 | expertise owed | `expertise=False` for `runtime` | case 28 | red |
| 16 | incidental exempt | remove the incidental early return | case 30 | red |
| 17 | scaffold resolver (expertise) | return `None` for `nodes/expertise.` | case 31 | red |
| 18 | scaffold resolver (agents) | return `None` for `agents/` | case 21 | red |
| 19 | pin home | drop the `libraries:` check | case 32 | red |
| 20 | two majors | `majors_in_play` returns `[]` | case 33 | red |
| 21 | node-ref reads | drop the node branch of `read_target` | case 36 | red |
| 22 | `needs` required | drop the `needs` test | case 38 | red |
| 23 | parent terms exempt from warnings | drop the `- trig[parent]` in the sibling check | `test_parent_terms_do_not_warn` | red |

---

## §E Verified facts (2026-09-09; how each was checked)

- Worktree: 17 modified files, no staged, one untracked (this plan); HEAD
  `713d32a`; branch `7.3.0-growth-coverage-gate`; manifest `7.4.0` —
  `git status --porcelain`, `git log`, `python3 -c 'json…'`.
- `bash tests/run.sh` exit 0 on 2026-09-08 (full run; 44 pytest passed, 1
  skipped; seed lint PASS; legal lint PASS 129 entries). seed-lint and
  test-knowledge-paths re-run PASS after each plan write on 2026-09-09.
- `_terms("change the EF mapping") == {"mapping"}`;
  `_terms("upgrade orders to net10.0") ⊇ {"net10", "net10.0"}`;
  `_terms("add a migration for the orders dbcontext") == {"dbcontext",
  "migration", "orders"}` — reproduced with the tool's regexes and stopwords.
- `resolve()` is called only from `main()` (`grep -rn "resolve("`); the
  route hook consumes `--plan` stdout.
- `graft-audit.py --unfilled` skips files whose name starts with `_` or ends
  with `.template.md` (L273).
- `required_collections()` skips `nodes/` (L250–L251), so an expertise node
  never creates a collection row; `is_substantive()` takes `template_text`
  (L339) and `agent_scaffolds()` is its only such caller (L502–L516, used at
  L785 and L837).
- `test_graph_lint.py` has 27 `def test_` cases; `test-growth-audit.sh` cases
  are numbered 1–27 and case 21 is "a form is not an expert".
- `agent-lint.py` has `_distinctiveness_warnings()` at L363.
- `delegation.md` sections: `## Route mechanically first` L70, `## Every brief
  carries the graph discipline` L190.
- `context-router/SKILL.md`: §3 "Take the required closure" L129–L134; §5
  declaration block L147–L165.
- Ledger-§9 references: nine, in six files (S8 list); every other `§9` is a
  spec or grill section.
- `manifest.json` `templates[]` entries are `{"file", "produces"}`;
  seed-lint checks existence of each `file`.
- `graft-graph-engine.py` unions set-literal config, `KINDS` included
  (L160–L168).
- Rule numbers cited in code: 2, 12, 13, 14 (graph-lint docstrings); the
  schema's numbering is therefore stable and 15–19 are appended.
- `_deviation.template.md` shape: frontmatter with `<placeholders>`, header
  comment, body sections, fenced YAML example — mirrored by C.5 except that
  C.5 uses `{{ }}` placeholders (audit-measurable).
- `library-page.template.md` §0 Pin is L15–L18 with a scalar `Version:` line.
- Independent review (Fable, 2026-09-09, read-only): built §B verbatim in
  scratch and ran the **unmodified** `graph-lint.py --plan` — every child of
  the first-draft tasks was seeded directly, and `"migrating the CI runner"`
  loaded `ef-migrations` by prefix fold. Also ran it on a copy of a real
  plant graph (39 project + 113 machinery nodes) with §B added: same result.
  This is why M1 is RED-first and every descent test asserts provenance on a
  task the unmodified tool does not seed. The review's line-number
  corrections (incidental `if` L578–L579; staffing branch L971; scaffold
  call L785; context-router §3 L129–L134; graft-audit L273) are applied.
- `manifest.json` `templates[]` carries no `_deviation.template.md` entry.
- `tests/seed-lint.py` L671–L677 already rejects a `plant_knowledge` entry
  that is not a collection, row, or template leaf — no seed-lint change is
  needed for C6.
- `tests/test_graph_lint.py` `build_graph()` L108–L112 lists every node id in
  `index.md`; reachability tests must leave the node under test unlisted.
- `tests/test-graft-tools.sh` L22–L47 already proves the `KINDS` union.

---

## §15 Changelog

- 2026-09-08 — plan authored against HEAD `713d32a` + the uncommitted 7.4.0
  increment; baseline gate exit 0. Nothing implemented.
- 2026-09-09 — §0 ratified by the user: Q1 as recommended; Q2 unversioned
  with the version-distinction mechanism; Q3 routing-only; Q4 fold; D5 as
  recommended; D6 revised to `nodes/`; D7 revised: expertise is called by
  agents through the router, not carried by agent rows; D8 stands; D9
  redesigned as delta-exact descent. Tokenizer fact recorded.
- 2026-09-09 — plan rewritten under the holistic-editing discipline at the
  user's instruction: §8 added and binding; descent moved inside the closure
  loop; `check_acyclic` generalised instead of copied; `agent_scaffolds`
  generalised into one scaffold resolver; ledger §9 reworked instead of a new
  §16; NOT COMPOSED folded into NOT LOADED with reasons; every item names
  what dies; class sweeps enumerated.
- 2026-09-09 — prepared for handoff to an implementing session: §0.0 resume
  block; line numbers re-verified; §A code sketches; §B verbatim fixture; §C
  fixed text blocks; §D mutation matrix; §E verified-facts ledger; S8 sweep
  (the nine ledger-§9 references) added; context-router target corrected from
  §2 to §3/§5; frontmatter-subset and golden-capture risks added.
- 2026-09-09 — independent Fable review (2 critical, 6 major, 11 minor, 3
  nit) integrated. Critical: the first-draft spike and descent tests were
  not load-bearing because seeding already loaded every child (M1 is now
  RED-first with pass A on the unmodified tool; every `test_plan_*` asserts
  provenance or reason; the "migrat" claim is qualified to descent only);
  the stdout golden was uncapturable (now a golden over id sets, and the
  provenance format is pinned in M1). Major: reachability test and fixture
  must leave a node unlisted; §D row 8 gets its own fold test; A.4 preserves
  grounding for incidental non-dependency items; S4 gains the seven
  "commission first" members and the audit's own comments, and the C8
  `est_tokens` list grows accordingly; one `resolve()` return contract;
  descent and warning vocabulary unified as id + `load_when`, parent terms
  exempt. Minor and nit: line numbers; no deviation entry in the manifest;
  M2's "what dies" named; M6 drops the seed-lint change and machinery ids;
  case 31 defined and the template moved to `{{ }}` placeholders;
  knowledge-graph SKILL rules list not renumbered; S1 members added;
  verdict-arm trap noted; `template_bytes()` named as the seed carrier; M9's
  redundant test dropped; inline-list notation removed from the kind table;
  §B word-count and unlisted-node notes; growth-scout wording.
- 2026-09-09 — **M1 spike executed; GREEN, stop rule not triggered.** Pass A
  on the unmodified tool reproduced the reviewer's measurements exactly:
  tasks 1–8 all RED with the plan's wordings, and both trap phrasings
  confirmed ("add a log sink" seeds serilog; "write the migration script"
  seeds ef-migrations through its title; `net10.0` seeds dotnet-10 once the
  two extra subsystems are present). Pass B with §A.1 applied: every task
  loads its target child with the provenance line and lists the rest with
  reasons, including the two-level case (`dbcontext` → ef-core, `migration`
  → ef-migrations). Task 6 is the family-vocabulary proof — serilog carrying
  the trigger "dotnet logging" still stays out, because `dotnet` belongs to
  the parent. Exact-only proven: a task saying "migrating the runner" does
  **not** compose `expertise.ef-migrations` while `dbcontext` composes
  `ef-core` in the same run. All 27 `test_graph_lint.py` cases pass against
  the patched tool. **Two spike corrections to §A.1:** the wide-descent
  notice needs `len(kids) > 1` (a single-child parent tripped it on every
  legitimate descent), and the slug-whole vocabulary behaves as designed —
  an id fragment (`core`) never composes, though seeding may still load a
  node by its title, which correctly shows no composed-by marker. Provenance
  format confirmed as pinned: `  <id:<28> <title>   <- composed by <parent>
  on "<term>"` on composed lines only.
- 2026-09-09 — **7.5.0 implemented; `bash tests/run.sh` exits 0.** Waves 0–6
  executed. Deviations from the plan as written, all recorded here rather than
  in the items they change:
  - **Descent vocabulary refined during M1.** `V(n)` is the node's `load_when`
    tokens plus its slug kept WHOLE (`Node.triggers`). The plan's first form
    ran the id through `_tokens`, which splits `ef-core` into `ef` and `core`
    and would let "fix the core module" compose the persistence expertise.
  - **The wide-descent notice needs `len(kids) > 1`.** A parent with a single
    child tripped it on every legitimate descent, which is not evidence of a
    generic task. Found by running the fixture, not by reading.
  - **Test wordings are fixture-specific, and one had to be re-measured.**
    `test_plan_selects_major_by_tfm_token` seeds its child on the small
    hermetic fixture with the plan's task; it names the subsystem's path glob
    instead, verified RED against the pre-change tool. Its docstring records
    why.
  - **Case 31 was not load-bearing as first written** — it grepped for
    `HOLLOW` anywhere in the audit output, which another row satisfied.
    Tightened to the node's own path and the inherited-content phrase; the
    mutation then turns it red. This is the same defect class the independent
    review caught in the plan, found here by running the matrix.
  - **`empty_reads` message changed** from "holds no filled leaf" to "holds
    nothing this plant wrote", because a declared read can now be a node and
    "leaf" is collection language. `test-growth-audit.sh` case 25's pin
    followed.
  - **Two collapses beyond the named sweeps**, both duplications the work
    exposed: `seed-lint.py` had two identical module loaders (`load_tool` and
    `load_agnosticism_lint`), now one; `load_tool` also registers the module
    in `sys.modules` before executing it, which a module defining a
    `@dataclass` requires.
  - **Case 8's "fully grown plant" fixture now authors an expertise node.**
    That is what fully grown means in 7.5.0; the alternative was weakening the
    gate.
  - **M9 added no test**, as the plan directed: `test-graft-tools.sh` already
    proves the `KINDS` union and seed-lint now proves the seed's own `KINDS`
    carries the kind.
  - **§D is complete: all 23 mutations turn their named case red**, and each
    tool was restored byte-identical afterwards.
  - **M12 end-to-end**, on a throwaway install (no plant on this host was
    touched): a two-major dotnet inventory plans the parent and one child per
    major and prints `NEEDS COMPOSITION`; the authored plant lints clean at 64
    nodes; `--plan` on a task naming `net10.0` composes `dotnet-10` and lists
    `dotnet-8` with its reason, `net8.0` composes the other, and a task naming
    neither composes neither.
- 2026-09-09 — second review pass (19 of 22 closed, 3 partial; 2 new major,
  5 new minor) integrated. M1's task table now carries wordings the reviewer
  measured RED on the unmodified tool (tasks 2, 4, 6 reworded; task 4's
  unreachable first form dropped) and the rule that tasks 1–7 run on the
  eight-node fixture while task 8 runs on a copy with two extra subsystems,
  because added nodes move the seed floor. §C.10's template path corrected
  to `docs/graph/nodes/_expertise.template.md`. Descent vocabulary refined
  to `load_when` plus the whole slug (id fragments such as `core` are not
  triggers); the warnings ignore sub-three-character tokens. §C.3 aligned.
  `est_tokens` counts point at C8. `node_md()` gains `peers`. M11 names the
  three documentation members of S4.
