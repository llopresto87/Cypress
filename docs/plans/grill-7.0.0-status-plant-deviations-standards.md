# grill — 7.0.0: lifecycle status, plant facts, deviations, scaffold pruning, estate standards

Plan-of-record. Ratified decisions D1–D8 are recorded here as contract, not re-argued.

## §1 Artifact discovery (all read, paths cited)
- `templates/knowledge-graph/_schema.md` — frontmatter contract, node kinds, 11 linter rules.
- `templates/knowledge-graph/graph-lint.py` — PROJECT CONFIG (`KINDS`, `KIND_PREFIX`, `MACHINERY_DIRS`), `REQUIRED_KEYS`, `check_schema`, `check_budget`, `resolve()`.
- Seven status vocabularies in `templates/{adr,spec,threat-model,data-contract,prompt-contract}.template.md`, the specs-index template and the decisions README template under `templates/docs/` — all body prose, none machine-readable, none compatible.
- `legal-corpus/_schema.md` + `tests/legal-lint.py` — the one linted status; domain fact, not lifecycle; **left untouched**.
- `integrations/claude-code/{route-hook.py,settings.json}`, `integrations/github-copilot/hooks/route.json`, `integrations/prime-agent/{route-extension.ts,settings.json}` — the hook surfaces; `install.sh` places them (lines ~318–332, ~528–540, ~574–592).
- `tools/graft-audit.py` — `SCAFFOLD_FILES`, `seed_source_for`; `tools/agnosticism-lint.py` — the delivered-tool precedent (6.14.0).
- `protocols/{canonize,deliver,grow,graft,verify}.md`, `skills/{adr-writer,context-router,knowledge-graph,holistic-editing}/SKILL.md`, `core/method/{design,engineering}-posture.md` — doctrine homes touched in wave 2.
- `core/AGENTS.md` 7 180 / 8 000 B — **not touched**.

## §6 Decisions (contract)

**D-STATUS.** Lifecycle status lives in frontmatter only. Base vocabulary
`open | deferred | hotfix | rejected | superseded | closed`. Kind extensions: ADR `proposed | accepted`;
spec `draft | active | implemented | back-written`; deviation `standing`. Required companions:
`closed → status_evidence`; `superseded → superseded_by`; `deferred → reopen_when`;
`open|hotfix|deferred → owner`; `standing → ends_when`. `status_date` always. A body `## Status`
section may exist only as a pointer ("see frontmatter"); a body value that differs is a lint failure.
`legal_status` is a separate, unchanged vocabulary.

**D-TOOL.** `tools/status-register.py`, delivered as `docs/graph/status-register.py`, config-free
fast-forward machinery (agent-lint class). Roles: lint (exit 1) and query
(`--open --hotfix --deferred --by-kind K --since D --summary`). Cadence: CI lint; a `SessionStart`
hook per harness injecting `--summary` once; canonize close-out runs `--open --hotfix` and asks.
Nothing in any brief. Subagents receive nothing.

**D-PLANT.** `docs/graph/index.md` frontmatter gains a `plant:` block — the owner-declared facts:
`environment_class: ephemeral-test|staging|real-production|mixed`, `commit_attribution: none|<trailer>`,
`deliverable_language`, `comment_language`. Asked once in grow Phase 1 and adopt-existing.
`graph-lint`: missing block **fails** on a grown plant, **warns** on an adopted one (detected by the
presence of `.cypress/growth/completeness-ledger.md` or a `grown: true` marker in `index.md`).

**D-DEVIATION.** New node kind `deviation` (dir `docs/graph/nodes/`, id prefix `deviation.`), frontmatter
`status: standing`, `departs_from`, `reason`, `scope`, `ends_when`, `recorded_in`. Canonize gains
`canonize.deviation-capture`: at close-out, any decision departing from a known standard is asked *why*
and written to both the ADR (history) and a deviation node (standing truth).

**D-SCAFFOLD.** A template scaffold byte-identical to `templates/docs/**` at grow Phase 6 or graft Phase 7
is renamed `<name>.unfilled.md` (default) or removed (`--prune`), and reported. `verification.md` exempt
only when it carries at least one `executed` gate. Detection: `graft-audit.py --unfilled`.

**D-STANDARDS.** 39 new-home themes land as 4 new method nodes + extensions to `verify.md` and
`design-posture.md` + a new `vcs-posture.md`; 27 sharpenings as single clauses in their owners.
Fact keys per node are fixed in §9 wave 2. Kernel untouched. Routing displacement must be 0.

**D-VERSION.** 7.0.0. CHANGELOG states what changed.

## §9 Implementation — waves, with single-writer file ownership

### Wave 1 (parallel; disjoint files)
| owner | files | delivers |
|---|---|---|
| coordinator | `templates/knowledge-graph/_schema.md`, `templates/knowledge-graph/graph-lint.py`, the 7 templates, `tests/test_graph_lint.py`, `install.sh`, `integrations/claude-code/{status-hook.py,settings.json}`, `integrations/github-copilot/hooks/{status.json}`, `integrations/prime-agent/{status-extension.ts,settings.json}` | D-STATUS schema + lint rules, D-PLANT block + severity, `deviation` kind, template migration, delivery + hooks |
| worker B | `tools/status-register.py` (new), `tests/fixtures/status/**` (new), `tests/test-status-register.sh` (new), `tests/run.sh` (one line) | D-TOOL lint + query roles |
| worker C | `tools/graft-audit.py`, `tests/test-graft-tools.sh`, `tests/fixtures/graft/**` | D-SCAFFOLD `--unfilled`/`--prune`; registers `status-register.py` in `SCAFFOLD_FILES`/`seed_source_for` |
| worker A | plant-side files only (outside this repo) and the distillation workspace | credential-value stripping in two plants; distillation-method guard. Tracked in the owner's masterplan, not here. |

### Wave 2 (after wave 1 gates green; disjoint files)
| owner | files | fact keys |
|---|---|---|
| worker D | new `core/method/secrets-posture.md`, `release-posture.md`, `incident-posture.md`, `contract-posture.md` | `secrets-posture.{channel,recording,compromise,lifetime}` · `release-posture.{artifact-identity,readiness,dependency-graph,advisories,ordering,rollout}` · `incident-posture.{containment,closure,evidence,sequencing,residuals,register-closure}` · `contract-posture.{required-input,domain,unversioned,ordering,errors,authorization,read-surfaces,logging}` |
| worker E | `protocols/verify.md` only | `verify.status-evidence` + `verify.{measure-integrity,composition,characterize,tool-faults,silent-substitutes,test-first}` + sharpenings T16 T02 T12 T05 T04 T82 T28 T03 T11 T14 |
| worker F | `core/method/design-posture.md`, `core/method/engineering-posture.md`, `skills/holistic-editing/SKILL.md` | `design-posture.{seam-variation,structural-invariants,converge-on-drift,generated-artifacts,doc-code-precedence,project-contract-outranks,maintained-primitives}` + sharpenings T52 T60 T80 T46 T58 (design) · T32 T59 T36 T23 (engineering) · T48 (holistic) |
| worker G | `protocols/{canonize,deliver,grow,graft}.md`, `skills/adr-writer/SKILL.md` | `canonize.deviation-capture`, `canonize.status-review`; `deliver.numbered-decisions`; grow Phase 1 plant-facts ask + Phase 6 unfilled gate; graft Phase 7 unfilled report; adr-writer vocabulary |
| worker H | new `core/method/vcs-posture.md`; `skills/context-router/SKILL.md`; `skills/knowledge-graph/SKILL.md`; `templates/docs/nodes/_deviation.template.md` (new); `templates/knowledge-graph/index.md` (plant block) | `vcs-posture.{local-resting-state,publish-authorization,no-worktrees,plant-settings}`; sharpenings T25 T89 T49 T94 T29 (context-router / knowledge-graph); deviation template |
| coordinator | routing diff, est_tokens, seed-lint, `CHANGELOG.md`, `manifest.json`, `DOCUMENTATION.md`, `documentation/README.md`, `documentation/protocols-reference.md` | gates + canonize |

### Wave 3 (plant side — tracked per plant in the owner's masterplan, never named here)
For each plant: status-frontmatter migration script (old vocabularies → D-STATUS), `plant:` block
declared, standing deviations written as `deviation.*` nodes with `ends_when`, and any plant-local
inconsistency the estate review surfaced (a restated status deleted; a containment marked `hotfix`
with an owner; a back-written spec labelled as such). One plant per increment; gates per plant:
`status-register.py` lint clean, `graph-lint` clean, `agnosticism-lint` unchanged. Revert per plant.

## §10 Verification
Per wave: `python3 tests/seed-lint.py`; `bash tests/run.sh`; fresh install → `graph-lint.py` clean;
~~routing diff over all baseline `load_when` triggers = 0;~~ routing diff: no baseline route loses an owning node; residual changes are recorded sharpenings (§15, 2026-09-06); `agnosticism-lint.py` over the diff with all
12 plant names as `--forbid`; kernel byte count unchanged; every new test verified RED against the
defect it guards before GREEN.

## §11 Risks
R1 two writers on one file → the ownership matrix above is binding; a worker that needs a file it
does not own hands back naming it. R2 `hotfix` abused as closed-lite → lint requires `owner`.
R3 routing degradation from 5 new nodes → sharp `load_when`; the diff gate. R4 plant migration
breaks a plant's own gates → one plant per increment, revert per plant. R5 `SessionStart` hook
semantics differ per harness → each hook fails open, mirrors route-hook exactly.

## §13 Done
`7.0.0` in manifest; gates green; ~~routing diff 0~~ routing: zero displacement of owning nodes, three recorded sharpenings; kernel unchanged; `status-register.py --open`
runs on a fresh install and on at least one grown plant; every standing deviation is a node with `ends_when`;
contradictions #2 #3 #6 #8 each have a recorded resolution; #1 #4 #5 #7 #9 recorded as dissolved.

## §15 Changelog
- 2026-09-06 — plan created from the ratified masterplan; wave 1 dispatched.
- 2026-09-06 — **Waves 1 and 2 executed.** Contract (schema rules 12–14, `deviation` kind,
  `plant:` block), three delivered tools (`status-register`, `status-migrate`,
  `graft-audit --unfilled`), installer delivery + `.unfilled.md` marker, session-start hooks
  for three harnesses, five posture nodes, verify/design/engineering/holistic sharpenings,
  canonize/deliver/grow/graft/adr-writer/context-router/knowledge-graph updates, 7.0.0
  CHANGELOG and version strings. Full suite exit 0; kernel 7 180 B; agnosticism clean over
  the diff.
- 2026-09-06 — **Fact-key convention normalised.** Posture facts use `<node>.<fact>`
  (`design-posture.*`, `vcs-posture.*`, `secrets-posture.*`, `release-posture.*`,
  `incident-posture.*`, `contract-posture.*`), matching `engineering-posture.*`; the plan's
  earlier short prefixes are superseded.
- 2026-09-06 — **Routing ruling.** Five new nodes and new `load_when` phrases shifted 11 of
  161 baseline routes at first measurement. Titles score double in `resolve()`, so titles
  and phrases were reworded against the baseline trigger vocabulary (637 tokens) until no
  baseline route lost an owning node. Three residual changes are accepted as sharpenings,
  not regressions: *record an architecture decision* now loads stewardship + grill +
  adr-writer (engineering-posture dropped; grill §6 is where decisions land);
  *supersede an existing decision record* resolves to adr-writer alone (it now owns
  supersession mechanics); *upgrade this plant to the newer seed* resolves to graft alone
  (harvest is the fold-back direction). Method for future authors: check a new node's title
  and phrases against the baseline trigger vocabulary before installing.
- 2026-09-06 — **Flag, not fixed:** `protocols/verify.md` grew to ~5 200 tokens (seven
  facts, ten sharpenings) and is loaded at every close-out; splitting it is a 7.1 question.
- 2026-09-06 — **Wave 3 narrowed by the steward:** one plant is grafted to 7.0.0 (the pilot, which also receives the owner's operator nodes); no other plant is grafted or migrated in this cycle. Remaining plants upgrade only when their steward starts a graft (`graft.user-sovereignty`).
- 2026-09-07 — **Pilot graft completed and audited.** Two seed follow-ups surfaced, not fixed here:
  (a) `install.sh github-copilot --check` diffs the whole `.github/` tree against a fresh regeneration,
  so a plant's own expert agents (legitimately projected there) and a plant-merged kernel copy read as
  STALE — the gate needs to exclude plant-authored projections and compare only seed-generated views;
  (b) `graft-audit` reports KERNEL STALE on byte-identity, so a plant that deliberately carries an extra
  §4 boundary in its kernel is flagged on every audit — the honest state is a `deviation` node, and the
  audit should recognise one. Both are 7.1 items.

