# Changelog

## 6.10.0 — termination bounds made real; every spawn traced (2026-09-01)

Closes the debt recorded in 6.9.2: multi-agent-architect's pre-ship checklist
demanded caps the seed itself lacked. Steward decision: token/time caps are
NOT wanted — the seed's real bounding mechanisms are the depth cap, the
three-attempt boundary, the single-step spawn scope, and the graph's context
budgets, and those four now bound execution without holes. Correlation-id
tracing IS wanted, and now exists.

### Changed — the four bounds close their gaps

- **`protocols/recover.md`** (three-attempt boundary): an attempt that ends
  without advancing its deliverable — no new artifact, evidence, or narrowed
  hypothesis — now **counts as a failed attempt** even though nothing errored.
  A loop that keeps "succeeding" at making no progress previously evaded
  every error-shaped gate; the boundary is the seed's iteration cap, so it
  trips on futility too.
- **`core/method/delegation.md`** (`delegation.step-scope`): the spawn-scope
  overrun now has ONE defined outcome — finish the briefed step (or its
  coherent finishable part), STOP, and hand back naming the remainder for the
  caller to re-slice; absorbing overflow in-place is named as the
  unbounded-spawn anti-pattern.
- `max_spawn_depth` and the graph load-tier/est_tokens budgets were audited
  and left as-is (already lint-enforced end to end).

### Added — spawn tracing (`delegation.tracing`)

- Every delegation carries a caller-minted, dot-chained **`spawn_id`**
  (`orchestrator.3.architect.1`): stated in the brief, echoed verbatim in the
  handback, cited wherever the spawn's work is referenced. The chain
  reconstructs the full delegation path with zero infrastructure, and an id
  deeper than the caller's `max_spawn_depth` is a bound violation on its
  face. Leaves mint nothing. Wired into
  `templates/prompts/handback-payload.md` (new `spawn_id` field), all five
  delegation briefs, and the growth evidence-ledger's handback list.
  `tests/seed-lint.py` now fails any brief/handback template that drops the
  field (planted regression: case 5d in `tests/test-seed-lint.sh`).

### Changed — multi-agent-architect checklist matches the doctrine

- **Termination bounds** no longer demands "hard iteration/token/time caps"
  (scrubbed by steward decision): it now names the real mechanisms — depth
  cap, no-progress-counting retry boundary, single-step spawn scope with
  stop-and-hand-back overrun — each with defined at-boundary behavior. The
  agent-contract workflow step says the same.
- **Cost ceiling** drops the per-task token/latency budget demand; it keeps
  model-tier-per-role and adds the graph's load-tier context budgets.
- **Observability** (correlation-id tracing) is unchanged — and the seed now
  satisfies it via `delegation.tracing`.

## 6.9.2 — the doctrine audit: 18 scoped reviews of the method surface itself (2026-09-01)

6.9.1 proved the gates honest; this release audits what the gates cannot see —
the MEANING of the kernel, protocols, agents, skills, templates, and corpora.
Eighteen scoped read-only doctrine audits (one per surface) fed two
implementation passes. Every fix repairs a verified contradiction, broken
handoff, unexecutable instruction, restatement drift, or plant-breaking
assumption; regression tests were added where a gate could carry the invariant.

### Fixed — the kernel's mandatory routing step now exists on every harness

- `python3 .claude/agent-lint.py --route` was mandated by the kernel,
  delegation.md, the orchestrator, and grow.md on ALL five tools — but
  install.sh placed agent-lint.py only for claude-code: 4/5 single-tool plants
  had an unexecutable mandatory first delegation step. The router now installs
  at **`docs/graph/agent-lint.py`** on every adapter (claude-code keeps its
  `.claude/` projection) and — unlike the config-carrying graph engines —
  FAST-FORWARDS on re-install (identical untouched, changed backed up for
  graft-audit, which now maps it and the golden corpus as seed machinery).
  `agents/_routes.golden.tsv` rides with the roster into every plant so
  `--eval` (a graft exit gate) runs everywhere; roster discovery prefers
  the graph home `docs/graph/agents/` (where a commissioned expert is
  authored) over the `.claude/` projection; every normative reference uses
  the universal path. Regressions in `tests/test-full-install.sh`: all five
  adapters run `--lint`, `--route` (the kernel-mandated step) and `--eval`
  in-plant, and a stale router is proven fast-forwarded with backup.
- Kernel §2's default T3 sequence named a phantom `implement` protocol (no such
  node; implementation lives inside test-first's GREEN phase) — dropped, and
  the three documentation mirrors aligned. Kernel §0's T1 hard edge restored
  tiers.md's fifth condition: "or anything a spec covers".

### Fixed — contradictions an executing agent could not obey

- T2 RED→GREEN merging existed in three conflicting versions (tiers.md vs
  tester charter vs orchestrator): tiers.md now owns the canonical criterion
  (single contract + mechanical RED), the others cite it.
- growth-scout was mandated to write its evidence ledger by three documents
  while its own tools lacked Write and its last line claimed "strictly
  read-only" — Write granted, the read-only bound rewritten to its true scope.
- Implementer/reviewer instructed inline wiki edits the librarian-ownership
  doctrine forbids — now handback-mediated. Tester's bug-fix loop names the
  actor split. Pentest loads the actual threat-model artifact, binds
  protocol.test-first, and the AI red-team gate bar has one owner (security).
- Project-skill cataloging had two irreconcilable homes (`.claude/skills/`
  direct vs graph node + projection): harvest.md's graph-home doctrine now
  rules everywhere (toolcraft, canonize, docs-librarian, skill template,
  skill-corpus entries), stated strictly: the plant creates its own harness
  projection; install.sh projects only seed skills.
- graft.md contradicted itself on `_schema.md`/`index.md` ownership: they are
  project-instantiated, plant-owned — the machinery list, graft-audit's
  exemption set (`SCAFFOLD_FILES`), and a new regression case all agree an
  overwrite of them is a knowledge overwrite.
- verify.md names its handoff (canonize → deliver) and peers; canonize's
  runbook actor matches verify/tester; deliver uses verify's owned three-state
  gate vocabulary (executed/discovered/absent); grill's workflow now fills
  §0–§15 — its own exit bar — and exits through §15.
- Entry-protocol repairs: brainstorm hands off to from-scratch Phase 2 (not 4);
  from-scratch defers to brainstorm-socratic's nine-question budget;
  ingest-library's seed-corpus check is plant-safe and its "fill every
  section" no longer contradicts the template's demand-grown discipline.

### Fixed — tools and their contracts

- graph-lint.py: the pre-growth reachability branch got the 6.9.1 boundary fix
  (the root branch alone had it — a machinery orphan could ride a prefix);
  duplicate node ids are now detected (_schema.md claimed it, nothing enforced
  it); the body-ceiling message states the real rule (170 hard, ~150 aim).
  Regressions in `tests/test_graph_lint.py` (17 tests).
- graft-audit.py: space-form options (`--tokens acme`) were silently dropped —
  the audit ran with default tokens and could print "clean" over a buried
  customization; both flag forms now parse, stray positionals exit 2.
  graft.md's documented invocation includes `--engine=` so the engine-currency
  check it cites actually runs. Regressions in `tests/test-graft-tools.sh`.
- install.sh's Copilot agent projection granted ONE fixed tool superset
  (editFiles/runCommands for everyone, `model:` never emitted as claimed):
  tools now derive from each agent's own allowlist — `editFiles` only with
  Write/Edit, `runTasks` only with Bash, `fetch`/`githubRepo` only with web
  tools; `runCommands` stays a baseline for ALL agents because the GRAPH
  DISCIPLINE bootstrap mandates running the graph router in every session.
  Neither `model:` (Copilot ids churn) nor `Task` (no subagent spawning on
  Copilot — coordinator flows degrade to the single session there, and the
  README says so) is projected. Regression in `tests/test-full-install.sh`.
- claude-code settings.json shipped four schema-invalid dead keys
  (agents/skills/commands/memory) — removed; discovery is by convention.
- _schema.md now documents KIND_PREFIX, the agent-node routing_triggers
  substitution, and the version-check code exemptions; the knowledge-graph and
  context-router skills point at the adopted `docs/graph/_schema.md` rather
  than the pristine seed template; spec-author's contract example uses the
  `### Contract:` form the linter actually counts.

### Fixed — legal corpus grade honesty (129 entries)

- Four cra.md sites claimed `text_form: verbatim` over unquoted paraphrase,
  invisible to legal-lint through multi-id folding — regraded per-id
  ("per id, not uniform"); the mis-formed "Open source:" heading became a real
  canonical entry (128 → 129). Seven dangling GDPR sub-ids repointed to their
  real undivided entries. nis2.md flags the three un-extracted decree articles
  as open ingest work. The table-only id sets carry ISO-style id-formation
  notes. No content, quotation, or grade was invented or upgraded.
- The independent review of this release then caught that the new compound
  grade line DISABLED legal-lint's start-anchored honesty check: the gate now
  captures the full (multi-line) grade value and fires on a `verbatim` grade
  token anywhere in it — which immediately exposed and fixed a fifth stale
  claim in cra.md's penalties block. The same review pass regraded the
  remaining structure-as-verbatim entries per span (`gdpr-art-13`,
  `gdpr-art-15`, `nis2-dir-art-21`, `nis2-dir-art-23`) and converted
  cra-art-14's three minted sub-ids to provision labels citable through
  the parent entry. Regression: the compound-grade fixture in
  `tests/test-legal-lint.sh`.

### Fixed — smaller drifts

Root README symlink-default and "Seven templates" claims; codex README's
phantom `.codex/protocols/`; opencode/prime-agent symlink wording; copilot
hook-path claim; prime-agent CI-parity wiring documented; posture nodes cite
their owning protocols instead of restating them; grow/graft cite the
graph-session-bootstrap home; brief/handback path typos (`.agents/`);
growth-scout-brief's handback field list matches the ledger schema;
prompt-contract template wired to data-ml; golden-corpus comment count;
delegation model-class rule covers adversarial validation (opus) and
mechanical retrieval (sonnet); research-scout's legal-ingest handoff;
LOW/NONE commissioning checks agent-corpus; canonize/docs-librarian check
tool-corpus in the tool half.

### Recorded debt (not fixed)

multi-agent-architect's pre-ship checklist demands hard iteration/token/time
caps with defined at-cap behavior and correlation-id tracing; the seed's own
coordinator system has only depth caps (`max_spawn_depth`) and recover.md's
3-attempt boundary. Known gap, recorded here rather than papered over.

## 6.9.1 — the gates stop lying: false-pass fixes across every linter, idempotent installs (2026-09-01)

A holistic bug hunt (four parallel read-only investigators + orchestrator
verification) found no failure in what the gates test — and eleven ways the
gates and tools could report green without testing anything. Every fix below
repairs a "vacuous pass" or a silent misbehavior; each carries a regression
case that fails on the pre-fix code.

### Fixed — linter false-passes

- **`tests/legal-lint.py`**: `has_field()` matched `**text_form:**` when asked
  for `text` (the `[^:]*` gap swallowed `_form`), so an entry carrying only
  the grade — not the law's words — passed as citable. A `\b` after the field
  name closes it. The stricter check exposed four shipped corpus entries with
  no conforming `text` field (`cra-art-13-1-3`, `cra-art-28-30` in
  `legal-corpus/eu/cra.md`; `it-dlgs-138-2024`, `acn-registration-pages` in
  `legal-corpus/eu/nis2.md`); each now carries a `text` bullet built strictly
  from facts already recorded in the entry. Regression: case 6 in
  `tests/test-legal-lint.sh`.
- **`templates/knowledge-graph/spec-lint.py`**: the contract-slug scan was a
  bare substring match — a prefix slug (`PARSE_JSON`) stole coverage credit
  from `PARSE_JSON_STRICT` (the longer, actually-covered slug was reported
  uncovered), and an UNREGISTERED extension (`PARSE_JSON_V2` in a test)
  credited `PARSE_JSON`. Now boundary-guarded (`(?<![A-Z0-9_])…(?![A-Z0-9_])`)
  and longest-first. Regressions: cases 5 and 5b in
  `tests/test-spec-lint.sh`.
- **`templates/knowledge-graph/graph-lint.py`**: (a) `VERSION_RE`'s lookbehind
  excluded the leading `v` of `vX.Y.Z` — the most common semver spelling
  evaded the version-leak check entirely; the optional `v` is now part of the
  match. (b) reachability used a plain substring test against `index.md`, so
  an unreachable node passed whenever its id merely prefixed an unrelated
  longer string — including a dotted child (`x.orphan` vs `x.orphan.child`,
  the graph's normal id shape); now a boundary match that rejects both
  continuations while still accepting a trailing sentence period.
  Regressions: `VersionLeakageTests` and `ReachabilityBoundaryTests` in
  `tests/test_graph_lint.py`.
- **`integrations/claude-code/agent-lint.py`** (the single home; installers
  copy it into plants): `--eval` on a golden corpus with zero labeled rows
  reported "top-1 accuracy 100.0% (0/0) — OK" at exit 0; the fail-closed gate
  now fails on a vacuous 0/0. Regression:
  `test_eval_fails_on_zero_labeled_rows` in `tests/test_agent_lint.py`.
- **`tools/graft-audit.py`**: a wrong plant root (or wrong `--date`) found
  zero backups and printed the same "clean — no customization buried" exit-0
  line a real audit earns. A root without `docs/graph/` is now refused
  (exit 1); zero backups for the requested date while backups exist under
  other date stamps is refused as a wrong `--date` (exit 1); zero backups
  anywhere stays a legitimate no-op graft (the idempotent installer makes
  that the normal case) and says so explicitly. Regressions: the
  non-plant-root and wrong-date cases in `tests/test-graft-tools.sh`.

### Fixed — test suites that could not fail

- **`tests/test-spec-lint.sh`**: `! grep -q OLD_RETIRED_THING` — bash exempts
  `!`-negated commands from `set -e`, so the retired-contract leak this line
  exists to catch could never stop the suite. Now an explicit `if grep; then
  fail` with a message.
- **`tests/test-knowledge-paths.sh`**, **`tests/test-orchestration-entry.sh`**:
  both hard-depended on undocumented `rg`; on a machine without ripgrep the
  `|| true` / bare-`if` idioms turned exit 127 into "no match" and the suites
  passed while checking nothing. Converted to POSIX `grep -rE` with explicit
  rc discrimination (rc>1 fails the suite loudly).

### Fixed — installer

- **`install.sh`**: (a) re-running any installer backed up and rewrote every
  byte-identical file — measured pre-fix: 103–134 no-op `.bak`s per
  single-tool re-run and 608 for `install.sh all`, burying graft-audit's
  real signal; identical placements are now skipped. (b) the
  opencode/codex/copilot installers placed `AGENTS.md` via raw `place_file`
  while prime-agent used `place_kernel`; on `install.sh all` the two
  ping-ponged the kernel between a copy and the CLAUDE.md-shared symlink,
  creating fresh backups on every run — all four now route through
  `place_kernel`, and `place_kernel` converges a pristine (byte-identical)
  kernel copy without a backup: to the shared symlink where the platform
  allows, kept as an identical copy where `ln -s` fails (symlink-less
  platforms churned 5 kernel `.bak`s per re-run even after the reroute).
  (c) the unquoted `${f#$src/}` prefix-strip treated the seed
  path as a glob pattern: a checkout under a path containing `[`/`]`/`*`
  silently nested every machinery file under the full absolute source path
  and reported success; both strips are now quoted. Regressions: the
  idempotent-re-run, glob-metachar-path, and symlink-less-platform cases in
  `tests/test-full-install.sh`.

### Fixed — docs that contradicted the code, and a brief outside the lint

- **`INSTALL.md`** no longer claims the installer "never touches your existing
  files in docs/graph/": the seed-owned machinery subtrees are fast-forwarded
  with backups for graft-audit (as `GRAFT_PROMPT.md` always said);
  plant-authored graph content is add-only. `install.sh`'s
  `place_docs_skeleton` docstring says the same.
- **`integrations/claude-code/README.md`** claimed symlinks-by-default and
  "the installer prompts before touching it… never silently overwritten" —
  the installer copies by default and has no prompts; the README now
  describes the real backup/`--force` behavior.
- **`templates/prompts/clean-context-validation-brief.md`** is a live
  delegation brief but never embedded the canonical GRAPH DISCIPLINE block
  ("brief templates embed it byte-identical; lint enforces sync" — the lint's
  hardcoded list simply didn't know this brief). Block embedded; the brief
  joined `tests/seed-lint.py`'s byte-identity list.
- **`README.md`** repository-layout block said "17 specialist agents" while
  line 40 of the same file said 18; `tests/seed-lint.py` now also polices the
  "N specialist agents" phrasing.
- **`DOCUMENTATION.md`** and **`documentation/`** were pinned at 6.8.0 with a
  17-agent roster omitting `ui-ux-designer` — the 6.9.0 roster commit updated
  every governed surface but this tree, which no gate read. Roster, counts,
  and version updated; the whole tree now sits in `tests/seed-lint.py`'s
  numeric-claims prose scan, the "N specialist agents" pattern tolerates
  qualifier words ("18 *named* specialist agents"), and the tree's
  documented-version pins are checked against `manifest.json`
  (regressions: cases 5b/5c in `tests/test-seed-lint.sh`). The in-sample
  honesty note now reads 42-of-49 labeled rows (recomputed against the
  current golden corpus). An adversarial review of this release's own
  diff caught and removed a mis-attribution it had introduced in
  `legal-corpus/eu/nis2.md` (`it-dlgs-138-2024`): the amend/repeal
  clauses in the decree's title describe Directive (EU) 2022/2555, not
  acts of the decree itself.

No kernel, protocol, agent-charter, or routing behavior changed; the eight
rule homes, the roster, and the golden corpus are untouched.

## 6.9.0 — lean funnel spawns; legal in the architecture path; ui-ux-designer joins the roster (2026-09-01)

The grill funnel's worker agents are re-scoped to spend tokens on the work
instead of on rediscovering context; architectural work gains a named legal
checkpoint; and the roster gains a definitive interface-design expert with
matching growth facilities. Plan-of-record:
`docs/plans/grill-lean-funnel-design-legal.md`. Quality over size governed the
rewrite: no normative rule was dropped — duplicated depth was replaced by a
pointer to its owning node, verified by an independent review pass.

### Changed — one step per spawn (`tester`, `implementer`, `reviewer`, `method.delegation`)

- **`agents/04-tester.md`**, **`agents/02-implementer.md`**,
  **`agents/03-reviewer.md`** each gain a **"Scope of one spawn"** section
  (new owned facts `tester.spawn-scope`, `implementer.spawn-scope`,
  `reviewer.spawn-scope`): one spawn = the RED phase for ONE increment's named
  contracts / ONE RED→GREEN→REFACTOR cycle / ONE diff for ONE increment. The
  brief carries the inputs (contract text, test paths, diff); oversized or
  under-specified work is handed back for re-slicing, never absorbed. Depth
  duplicated from owning nodes became pointers (test-first, toolcraft,
  design/engineering posture, holistic-editing); the token economy comes from
  the per-spawn scope and brief-carried inputs, not from shrinking the
  charters. Every check of the reviewer checklist survives with unchanged
  output format and severity semantics.
- **`core/method/delegation.md`** gains the orchestrator side of the same
  contract (`delegation.step-scope`): a funnel-worker brief names ONE
  well-defined step and embeds its inputs; oversized steps are re-sliced
  before spawning, per `protocols/grill.md` §9 increment shape.

### Added — legal checkpoint in architectural work (`architect.legal-checkpoint`, `grill.legal-checkpoint`)

- **`agents/01-architect.md`**: when a boundary, contract, dependency, or ADR
  implicates externally-authored rules (licenses, regulation, data protection,
  standards, third-party terms), the question routes to `legal` before the ADR
  is accepted — instantiated from `agent-corpus/legal.md` via the corpus
  withdraw contract when the plant roster lacks it; a legal-corpus gap becomes
  an explicit grill.md §12 open question ("not recorded — needs ingest"),
  never a recalled rule.
- **`protocols/grill.md`** §11 hands externally-authored-rule exposure to
  `legal` alongside `security`/`reliability` (minimal touch; the protocol was
  deliberately not compressed). `agent-corpus/legal.md` gains one
  architecture-review routing exemplar. `legal` remains a corpus role — the
  per-session roster economy stands.

### Added — `ui-ux-designer` (18th roster agent) and the design surface in growth

- **`agents/13-ui-ux-designer.md`**: definitive interface/interaction design
  authority — information architecture, screen flows, interaction states,
  design tokens and component system, visual hierarchy, usability-heuristics
  audits, and how the accessibility floor is met in the interface. Authors
  design specs under `docs/graph/design/` mapping to spec §3/§9. Boundaries:
  `product` keeps outcome, acceptance criteria, and the accessibility floor
  itself; `implementer` writes all production code. Leaf agent with its own
  "Scope of one spawn" (one flow, one heuristics audit, or one
  component/token spec per spawn).
- Growth facilities: `templates/prompts/growth-scout-brief.md` and
  `agents/growth-scout.md` now inventory the **design surface** (screens,
  components, tokens/styles, interaction states, a11y state) read-only;
  `agents/growth-orchestrator.md` may delegate design-surface node authoring
  to `ui-ux-designer` (added to its `delegates_to`).
- Roster wiring: kernel §1, `method.delegation` roster table, `manifest.json`,
  README (18-agent team), graph-template `index.md`, and three
  `_routes.golden.tsv` rows (eval gate stays at 100% top-1; no existing row
  changed hands).

## 6.8.0 — one labeled entry point; growth bound by an explicit completeness contract (2026-08-31)

The install/grow surface is refactored into **one clearly-labeled flow** and the
growth is made **complete-or-not-done** by an explicit doctrine that binds
whatever model orchestrates it. This closes the two long-standing gaps: the
entry was split across a shell script and a paste-in prompt with a buried
"root at the target, not the seed" gotcha, and nothing forced a growth to reach
full depth — a skeleton graph could be delivered as a grown plant.

### Added — the completeness contract (`grow.completeness-contract`)

- **`protocols/grow.md`** gains a new owned fact, the **completeness contract**:
  the rule of evidence-bounded totality (every knowledge collection is either
  *covered to the depth its evidence supports* or *absent with a named reason* —
  never a silent third state), a required **growth completeness ledger** the
  orchestration chat fills before declaring growth done, an explicit **no-early-stop**
  rule, and the statement that template files existing is never coverage. Phase 6
  validation gains item 10 (audit the ledger; under-growth is a defect on equal
  footing with over-growth) and the delivery block now carries the ledger.
  `est_tokens` bumped 2800 → 3600 for the added body.
- **`templates/prompts/growth-completeness-ledger.md`** — the canonical
  schema of the completeness ledger, filled by the orchestration chat and
  written to the plant's gitignored `.cypress/growth/completeness-ledger.md`.
  It makes the contract mechanical: one row per `docs/graph/` collection,
  each COVERED / ABSENT / named-UNKNOWN, so full-depth coverage is proven,
  not asserted.

### Changed — one entry point, three named phases

- **`INSTALL_PROMPT.md`** rewritten as the unmistakable single entry point. It
  opens with what/how/why, then runs one flow in three named phases — **PLACE**
  (may run from a seed-rooted chat), **HAND OFF** (restart rooted at the target
  for the registration boundary, no longer a buried gotcha), and **GROW IN FULL**
  (execute `grow` end to end under its completeness contract). Strict model policy
  and the graph-router mandate are retained verbatim (still gated).
- **`INSTALL.md`** reframed: `INSTALL_PROMPT.md` is named as the one entry; the
  shell installer is documented as the PLACE-phase mechanism you rarely call
  directly; the three-phase flow and the completeness contract are stated up top.
- **`install.sh`** final NEXT STEP output now says files are PLACED but the
  project is NOT grown yet, names the HAND OFF phase, and points at the GROW IN
  FULL phase under `grow.completeness-contract`.
- **`manifest.json`** → 6.8.0; `entry_points.primary` rewritten to describe the
  single three-phase flow and a new `entry_points.completeness` key documents the
  contract.
- **`tests/test-orchestration-entry.sh`** gains assertions that pin the single
  three-phase entry and the completeness contract in prose, so the doctrine
  cannot silently regress.


## 6.7.0 — Prime Agent becomes a first-class citizen, interchangeable with Claude Code (2026-08-31)

Prime Agent (PrimeIntellect-ai/prime-agent, v0.8.1) joins Claude Code as a
**first-class** integration at full parity — not the lighter
opencode/codex/copilot tier — and one plant can now run Claude Code and Prime
Agent **interchangeably** off a single shared kernel. Every claim below was
verified against the installed `dist/` source (eight parallel scouts) and
cross-checked online; evidence lives in `docs/plans/scout-0*.md` and the
plan-of-record `docs/plans/prime-agent-integration.md`.

### Added — `integrations/prime-agent/`

- **`README.md`** — the seed→Prime Agent map, the runtime-`rlm()` delegation
  model, the interchangeable-with-Claude-Code setup, and the recursion-depth
  dial. A `delegation.harness-registration` referrer (seed-lint enforced).
- **`route-extension.ts`** — progressive-discovery enforcement via the
  `before_agent_start` event (inject the route-first mandate + `graph-lint
  --plan` suggestion). The Prime Agent parity of `route-hook.py`; loaded from
  `.prime/agent/extensions/` with no build step (jiti); fail-open.
- **`settings.json`** — minimal, bare-relative resource paths (resolve against
  `.prime/agent/`); no `instructions` (kernel auto-loads, no double-load) and
  no `rlmMaxDepth` (a global/session/env dial, silently ignored in project
  settings).
- **`APPEND_SYSTEM.md`** — an RLM-native execution overlay Prime Agent appends
  to the system prompt every session (Claude Code never reads it). It maps the
  kernel's discipline onto Prime Agent's unique primitives — recursive/parallel
  `rlm()` subagents from brief sources, the continual harness (`refine`,
  memories) for cross-session close-out, `agent_message`/`agent_observe`
  handbacks, in-kernel gates, goals/heartbeats for long-running work — so Prime
  Agent exploits its edge over Claude Code instead of emulating a file harness.

### Added — installer + gates

- **`install.sh prime-agent`** (and in `all`): kernel → repo-root `AGENTS.md`;
  `agents/*.md` → `.prime/agent/agents/` as brief sources (+ the golden routing
  corpus); skills → `.prime/agent/skills/`; `command:true` protocols →
  `.prime/agent/prompts/` (generated); the route extension and settings copied.
  Prime Agent has no session-start roster enumeration, so there is **no
  registration lag** — briefs are usable by the next `rlm()` call.
- **CI PARITY GATE.** `tests/test-full-install.sh` now runs the SAME
  `agent-lint.py --lint`/`--eval` claude-code runs, pointed at
  `.prime/agent/agents/` (`--dir` bypasses the `.claude/agents/` assumption —
  zero linter changes), plus `assert_cmd_roster` on the prompt roster and a
  golden-corpus byte check. Prime Agent is CI-validated, not doc-only.

### Added — interchangeable Claude Code + Prime Agent in one plant

- **Shared kernel, no drift.** New `place_kernel` helper collapses `CLAUDE.md`
  and `AGENTS.md` to one source of truth — the first placed is the real file,
  the second a project-local symlink to it — so editing the kernel updates both
  harnesses. Copy-mode isolation from the seed is preserved (the link is
  project-local). `test-full-install.sh` gates the coexistence in both install
  orders.

### Changed

- `manifest.json` → 6.7.0; `integrations` gains the `prime-agent` entry
  (`first_class: true`). `tests/seed-lint.py` adds the prime-agent README to the
  registration-referrer set. `README.md`, `INSTALL.md`, and the Claude Code
  README updated four→five. `.gitignore` ignores `.prime/`.
- Cross-organ enumeration parity: the kernel, `core/method/delegation.md`
  (with Prime Agent's no-registration-lag note), `agents/seed-installer.md`,
  and the `initialize`/`from-scratch`/`graft` protocols plus the
  `from-scratch-bootstrap` skill now list Prime Agent alongside the other
  harnesses, so the seed's own organs treat it as first-class.

### Fixed

- `skills/test-first/SKILL.md` — quoted the `title:` value. Its unquoted `test:`
  substring is rejected by strict YAML (`npm yaml`, which Prime Agent uses),
  which would have **silently dropped the skill** on Prime Agent. Harmless to
  the seed's own regex frontmatter parser and every other harness.


## 6.6.0 — `devils-advocate` joins the roster; three new gates; a defined "turn" (2026-08-08)

### Added — `agents/12-devils-advocate.md` (roster 16 → 17)

A hostile pass over a **finished**, claim-bearing deliverable that tries to
**refute** each load-bearing claim from **primary sources only** — never the
drafts that produced it, since reading those is a second vote from the same
voter. Closed verdict vocabulary whose permanent ceiling is `could-not-refute`;
"verified" and "confirmed" are never available. Read-only by construction (no
`Write`/`Edit`): attacking and repairing stay structurally separate. Bounded
against `reviewer` (audits a *changing diff*, no opinion on a finished claim's
truth) and `pentest` (proves a defect against a *running* system).

### Added — three `seed-lint` gates, each with a planted violation

The seed shipped rules it never checked against itself. `tests/seed-lint.py`
(+135 lines) and `tests/test-seed-lint.sh` now gate:

- **`delegation.harness-registration`** — the fact keeps one home, *and* every
  dispatch/install surface keeps pointing at it. The second half is the real rot
  mode: the rule stays written while the surface that needed it quietly stops
  citing it.
- **`est_tokens` within 2× of the measured body** — mirroring the
  `graph-lint.py` the seed ships, which would otherwise reject seed-authored
  nodes the moment they installed into a plant.
- **The opencode config contract** — a stale `$schema`, a key
  `additionalProperties:false` makes fatal, a re-declared `AGENTS.md` that
  double-loads the kernel, and a `subagent_depth` that silently caps delegation.

`tests/run.sh` also gained a `pytest` fallback: Homebrew and pipx expose only the
executable, so probing `python3 -m pytest` alone skipped a gate that *was*
installed.

### Added — `delegation.turn`, because the term was load-bearing and undefined

"Turn" appeared 43 times across the seed, defined nowhere, in **three
incompatible senses** — two of them 54 lines apart in the same file: the
handback contract said "at the END of every specialist turn" while also calling
the payload something "the caller re-reads every turn". A worker could
reasonably have emitted the payload after every tool call. `method.delegation`
now owns the definition (one spawn → return cycle; hand back **once**, on all
three endings), the contract points at it, and the conversational sense in
`from-scratch.md` says "per exchange" instead.

### Changed — promotion to the roster is now a defined, steward-only move

`protocols/harvest.md` said a harvested role lands in the catalog **"never the
always-loaded roster"** — categorical, which made this promotion a silent
contradiction of the seed's own protocol. The catalog is now the **default**,
with a named bar for promotion: the mandate must be **universal** and no
base-roster agent may already cover it. Harvest may *propose* a promotion; it
never performs one. The catalog role `corpus-bound-obligation-analyst` is
renamed `agent-corpus/legal.md` — same domain-general mandate, a name a steward
can recall.

### Fixed

- **`install.sh` copied a file the seed no longer ships.** An earlier release
  deleted `integrations/opencode/opencode.jsonc`; the installer still `cp`'d it,
  so `install.sh opencode` — and `all` — aborted for every user. A
  `tests/test-full-install.sh` guard now pins that it stays absent.
- **A bracketed `## [X.Y.Z]` CHANGELOG heading defeated `seed-lint`'s own
  version check**, which read past the top entry and reported a false drift
  against a much older release.
- **`agents/11-pentest.md`** carried a frontmatter line appended into its prose
  body — a one-way peer edge and a nonsense bullet that would have installed
  into every plant. `graph-lint.py` checks that declared peers *resolve*, never
  that they are reciprocal, so nothing caught it.
- **`agents/12-devils-advocate.md`** was missing the Handback section every
  other roster member carries, which would have made each of its turns a
  deliver-time BLOCK.

### Previously undocumented — recorded here rather than by editing a released entry

The 6.5.3 entry as shipped recorded only two `engineering-posture` rules. The
same release also introduced the **legal corpus** (`legal-corpus/`, the fifth
corpus: the citation of an externally-authored rule, graded **per entry, never
per page**, with the amendment trap mandatory), further **corpus pages**, and
**two optional expert roles** in `agent-corpus/`. That entry is left exactly as
released; this is the supersession, per the append-only rule.

### Gates

- `bash tests/run.sh`: **PASS** — 8 shell suites, `test_graph_lint.py`,
  `agent-lint --lint`, `agent-lint --eval`, `pytest test_agent_lint.py`
  (43 passed, 1 skipped), and `seed-lint.py`. Thirteen invocations; eleven print
  a PASS/OK line.
- **Known weakness in that eval, stated rather than hidden:** 42 of its 46
  golden rows are byte-identical to the expected agent's own
  `routing_triggers`, so the score is substantially in-sample and reads far
  stronger than it is. The four `devils-advocate` rows added here are in-sample
  too.
- **Not gated:** `legal-corpus/` entry structure (scanned only for host-IPs,
  CVEs and dangling refs) and the agnosticism claim — `seed-lint.py` says so
  itself: subtler fingerprints "remain human judgment".

## 6.5.3 — 2026-08-07

### Harvested
- `core/method/engineering-posture.md` §12 — sharpened the durable-state
  discipline: crash-atomic writes (complete old or complete new, never partial)
  and quarantine-on-corrupt (preserve bad artifact, recover to safe state,
  surface the fault).
- `core/method/engineering-posture.md` §5 — added the optional-side-effect
  rule: a failing optional effect (notification, telemetry, non-critical
  integration) degrades to a logged warning and never fails the required path.

## 6.2.0 — doctrine pass: test coverage, structural + vocabulary integrity (2026-07-23)

A third holistic-rebalancing pass, run straight from the reconstruction doctrine
(not the pure-graph lens), over the integrity dimensions the prior passes had not
deeply examined — test, contract, structural/dependency, and conceptual. The
sharpest finding was self-inflicted: the 6.1.0 behavior shipped essentially
untested.

### Test + contract integrity — the new behavior is now tested

- `tests/test-full-install.sh` now asserts every harness emits **exactly** the
  `command: true` roster and **not** the sovereign meta-loop
  (graft/grow/harvest/toolcraft) — guarding the Copilot-leak regression 6.1.0
  fixed, and pinning install.sh's awk parser to the frontmatter source of truth.
- New `tests/test-seed-lint.sh` (wired into `run.sh`): a plant-a-violation
  regression asserting seed-lint EXITS 1 with the right message on each class it
  guards — sovereign-command, `command:`-on-non-protocol, unresolved edge,
  requires-cycle, miscounted prose, kernel budget, version drift — converting the
  linter from self-asserting to behaviorally tested.
- `seed-lint.py` gains a **version single-source** check: the top CHANGELOG
  `## X.Y.Z` must equal `manifest.json` version, so a behavior bump can no longer
  update one and forget the other.

### Structural integrity — one substantive one-home violation closed

- `from-scratch`'s protocol and skill both owned a `*.phases` fact and walked the
  identical nine-phase sequence. Re-carved to the grill/grill-planner pattern: the
  **protocol** owns the phase sequence + orchestration (`from-scratch.phases`);
  the **skill** owns only the honesty discipline (`from-scratch-bootstrap.method`)
  — dropped `from-scratch-bootstrap.phases` and the duplicated walkthrough, and the
  protocol's failure list now points to the skill's catalog (one home per fact).
- `skill.adopt-existing` `requires:` repointed from the thin `protocol.initialize`
  adapter to its real fact-owner `protocol.grow`; `initialize` kept as a peer (the
  command framing).

### Conceptual integrity — three overloads signposted

- "tier" carries three axes (task risk T0–T3, graph load-tier, model class).
  `core/method/delegation.md` no longer says "the tier lives in `model:`" (→ "model
  class"), and it and `_schema.md` now signpost the three axes. The node `tier:`
  frontmatter field was deliberately **not** renamed — that would break the
  installed graph contract for a naming nicety; signposting is the proportional fix.
- "specialist" vs "expert" glossed once in `delegation.md` (specialist = shipped
  roster; expert = commissioned for the project); "steward" glossed at first use in
  graft/harvest (the user acting as owner).

Dimensions audited and recorded as already coherent (unchanged): peer asymmetry
(intentional directional semantics), corpus/tombstone placement, spec §-numbering,
the plant/project and wiki/corpus distinctions, the `initialize` thin adapter, and
the test-first owns-namespace (facts are distinct).

## 6.1.0 — holistic rebalancing: pure-graph projections end to end (2026-07-23)

A holistic-rebalancing pass (in two sweeps) that extends the seed's own one-home
+ pure-graph discipline (6.0.0, ADR-0004) to every surface that still drifted
from it — the lifecycle prompts, the harness command trees, and the declarative
rim (READMEs, manifest) — makes `graft` carry that discipline outward to every
existing plant, and makes the seed **validate its own machinery as a graph
in-source**. The always-loaded kernel and plant-facing knowledge are untouched;
the pure-graph *spec* stays 6.0.0, and this release makes more of the seed
actually obey it — and lint-enforces that it keeps obeying.

### Lifecycle prompts defer to their nodes (no more drift copies)

- `INSTALL_PROMPT.md`, `GRAFT_PROMPT.md`, and `HARVEST_PROMPT.md` no longer
  re-list a protocol's phases inline. That copy had drifted behind its node:
  `GRAFT_PROMPT` was missing graft's grow-onto-the-plant phase and three Phase-6
  gates (customization audit, minimum-sufficient, cross-author rebalance);
  `HARVEST_PROMPT` advertised two triage gates against harvest's three. Each
  prompt now keeps only its paste-orientation + pre-node bootstrap contract and
  drives the phases from the authoritative `protocols/<name>.md` node — the
  omissions are structurally impossible with no second copy to drift.
- Fixed an internal inconsistency in `protocols/harvest.md`: Phase 2 said "apply
  both gates" while the protocol defines three (agnosticism, durability,
  non-redundancy) — now "all three".

### Slash commands are generated projections of the protocol nodes

- A protocol declares its own command-surface membership with `command: true`
  in frontmatter (the 11 session-entry protocols carry it; the user-sovereign
  meta-loop graft/grow/harvest and the canonize-folded toolcraft do not). Every
  harness's command file is now GENERATED from that field by `install.sh` — one
  home, projected — replacing the two hand-maintained, already-drifted command
  trees under `integrations/{claude-code,opencode}/commands/` (8 of 11 files had
  diverged; both trees deleted). `github-copilot` prompt generation is filtered
  to the same roster, so the command surface is identical on every harness —
  previously Copilot silently exposed graft/grow/harvest/toolcraft as prompts.
- `seed-lint.py` gains a command-roster guard: the user-sovereign/canonize-folded
  protocols may never declare `command: true`, and `command:` is protocol-only.

### graft rebalances existing plants toward pure graph, end to end

- New `graft.pure-graph-mandate` (`protocols/graft.md`): every graft — not only a
  legacy-layout migration — audits the plant against the pure-graph spec and
  reconstructs it toward maximal purity (machinery re-homed into nodes, duplicate
  homes collapsed, drifted projections regenerated from their nodes, obsolete
  residue listed), following the holistic-reconstruction doctrine and bounded by
  the rootstock line (facts are re-homed, never lost). Added as **Phase 6**
  (renumbering apply/verify → 7, deliver → 8), with a fail-closed pure-graph
  integrity gate, an output section, and quality-bar entries.

### Self-documentation caught up to the framework

- `docs/decisions/adr-0002` amended (append-only): the roster grew to 16 agents
  and delegators from five to six (growth-orchestrator); the bounded-delegation
  depth invariant is unchanged.
- New `docs/decisions/adr-0004` records the 6.0.0 pure-graph architecture — the
  current governing decision, previously recorded only in CHANGELOG + plans.
- `docs/plans/integrate-design-doctrine.md` marked EXECUTED-then-SUPERSEDED;
  `pure-graph-refactor.md` agent count corrected (17 → 16); the decisions index
  notes that ADRs 0001–0003 describe pre-6.0 mechanics.

### Fitness functions closed the drift gaps

- `tests/run.sh` now runs the two previously-orphaned regression suites
  (`test_graph_lint.py` always; `test_agent_lint.py` when pytest is present, with
  a loud skip otherwise); `CLAUDE.md`'s stale "5 shell suites" gate description
  corrected.
- `seed-lint.py` numeric-claim scan extended to the skills count and to
  `INSTALL.md`; the golden-corpus "13 agent defs" comment corrected to 16;
  manifest agents array reordered into file-number sequence.

### Second pure-graph pass — the seed validates its own graph, and the rim can't drift

- **The seed is now a validated graph in-source.** `seed-lint.py` previously
  checked each machinery node's *local* frontmatter but never the graph-level
  edges; it now resolves every `requires:`/`peers:` target against the machinery
  node set and proves the `requires:` relation acyclic — so a dangling edge or a
  cycle in a seed node fails fast, named at the seed file, instead of surfacing
  only after an install reconstitutes `docs/graph/` for `graph-lint.py`.
- **The declarative rim is guarded.** `seed-lint.py`'s prose scan now covers the
  integration READMEs and `manifest.json`, not just the three root docs — the
  gap that had let two facts drift silently: `integrations/codex/README.md` said
  "eight skills" (there are 13), and the claude-code/opencode READMEs pointed at
  a since-deleted `integrations/commands/` directory. Both corrected; the
  integration READMEs now describe slash commands as generated from each
  protocol node's `command: true` field (the real home) rather than restating a
  roster or a phantom source.
- `README.md`'s "What you get" is framed as a human overview of a canonical
  source (`manifest.json` + node frontmatter + the router), not a competing home.

## 6.0.0 — the seed becomes a pure graph (2026-07-22)

Everything that can activate progressively now lives in the graph; nothing
about *how to work* is always-loaded except a small bootstrap. Plan-of-record:
`docs/plans/pure-graph-refactor.md`. Breaking for 5.x plants (graft carries a
layout-migration path).

### The machinery is graph content

- Every protocol (15), skill (13, flattened to `<name>.md`), agent charter
  (16), and the new `method/` nodes install INTO the plant's `docs/graph/`
  as seed-owned routable Tier-2 nodes — kinds `protocol`/`skill`/`agent`/
  `method`, marked `origin: seed` — routed by the one router with
  `load_when:` triggers (agents reuse `routing_triggers`), costed by
  `est_tokens`, linted by the one `graph-lint.py`. Templates ship as Tier-3
  artifacts under `docs/graph/templates/`.
- The kernel (`core/AGENTS.md`) shrank 20,940 → ~7,100 bytes: identity, the
  first move, the tier table, the eight rules as one-line anchors
  (`### 3.1`–`### 3.8` preserved; each names its owning node and `rule.*`
  fact-key), the §4 boundaries, and pointers. Full rule statements moved to
  their owning nodes: 3.1→`protocol.specify`, 3.2→`skill.context-router`,
  3.3→`protocol.grill`, 3.4→`protocol.test-first`, 3.5→`protocol.verify`,
  3.6→`protocol.deliver`, 3.7→`protocol.canonize`, 3.8→`protocol.toolcraft`.
  Kernel §0/§1 depth moved to `method.tiers` and `method.delegation`; the §2
  protocol table became the router's pre-filled **Method** section.
- `core/operating-principles.md` (27 principles, 24 KB) split at its
  thematic joints into three routable posture nodes:
  `method.engineering-posture` (§1–§12), `method.design-posture` (§13–§19),
  `method.stewardship-posture` (§20–§27); the old file is a tombstone.
- Tool directories keep only **harness projections** — surfaces the host
  tool loads from fixed locations: `.claude/agents/`, `.claude/skills/`
  (same for opencode/codex; Copilot keeps its transformed views). Gone from
  plants: `.claude/protocols/`, `.claude/templates/`, `.claude/core/` and
  their opencode/codex/.github equivalents.

### Enforcement moved with the facts

- `graph-lint.py`: machinery kinds + dirs, per-kind filename rule
  (`NN-` prefixes stripped), `origin:` key, pre-growth grace (root node
  required only once project nodes exist), doctrine exemptions (no
  version-pin/line-ceiling checks on machinery), router treats
  `routing_triggers` as agent `load_when`. A fresh install lints clean:
  49 machinery nodes, ~75 K tokens if fully loaded — which is the point:
  no task loads more than its resolved closure (typically 3 nodes).
- `tests/seed-lint.py`: kernel budget 21 000 → 8 000 bytes; new machinery
  checks — node frontmatter on every protocol/skill/agent/method file,
  global owns-uniqueness, and the eight `rule.*` keys owned by exactly
  their mapped homes. Session budget 24 000 → 10 000.
- Install suites assert the new layout, including the negative space (no
  tool-dir machinery) and that the machinery-only graph lints clean.

### Graft-migration hardening (fed back from the first live 5.x→6.0.0 graft)

The first real graft onto this layout surfaced six ways the migration made
the operator hand-correct what the protocol should self-enforce; each is now
closed at its home so the next graft does not need the operator to force it.
The first three were caught by re-running the tool/engine gate; the last
three took the operator **four separate rounds of prompting** on the live
graft to surface, because each looks done right up until someone checks
whether it actually was — that gap is exactly why they are now protocol text
instead of tribal knowledge:

- **`tools/graft-graph-engine.py` now UNIONS a set-valued config knob the seed
  extended, instead of re-injecting the plant's wholesale.** The load-bearing
  case is `KINDS`: 6.0.0 added `protocol`/`skill`/`agent`/`method`, and keeping
  the plant's older set verbatim dropped them, so every newly-installed
  machinery node failed lint (`kind not in KINDS`). The engine now keeps the
  plant's own kinds *and* adds the seed's new members; scalar/list identity
  knobs (`ROOT_ID`, `TEST_GLOBS`) stay wholesale. `tests/test-graft-tools.sh`
  updated to assert the union (the old test encoded the wholesale-keep bug).
- **`graft` Phase 4 — one home per dependency.** When the plant already has a
  library/tool page, the corpus refresh now merges the orientation *into* that
  page and explicitly does **not** mirror the corpus's internal sub-namespace
  (e.g. `library-corpus/container/docker.md`) into the plant as a second,
  parallel page — the duplication the minimum-sufficiency gate already BLOCKs,
  now prevented at the source rather than caught after the fact.
- **`graft` layout-migration — the plant's OWN agents/skills relocate in the
  same pass.** A 5.x plant's plant-authored (`origin: project`) experts and
  project skills are promoted into `docs/graph/{agents,skills}/` (with harness
  projections regenerated) as part of the migration, not deferred to a
  follow-up "absorption" pass — a plant left with its own agents/skills in the
  old harness-only spot is half-migrated (the router can't route them).
- **Round 2 — relocating is not reconciling.** The first pass at the bullet
  above tagged the plant's relocated experts with node frontmatter and copied
  their bodies verbatim; the operator had to point out that copying byte-for-
  byte and calling it integration misses the point — the content still
  restated facts the graph's crosscut/platform/subsystem nodes already owned.
  Phase 3(c) now states plainly: relocating a pre-graph expert or skill still
  needs the same holistic reconciliation a MERGE gets, trimming every
  restated fact to a cross-reference, or the move is cosmetic.
- **Round 3 — a migration owes a fact-sweep, not just a machinery swap.**
  Finishing the machinery migration left the graph structurally current but
  substantively thin: a plant old enough to predate the graph was never run
  through `adopt-existing`/`ingest-library`, so its real knowledge (deploy
  docs, per-repo READMEs, comment-only sharp edges) had nowhere to land and
  stayed outside the graph entirely. New migration step (f) makes sweeping
  that knowledge — scouts across the plant's real source, Opus authors to
  weave findings into the owning node — part of the migration for any
  plant this old, not a follow-on the steward has to separately ask for.
- **Round 4 — parallel absorption needs a rebalance no single author owns.**
  Sweeping (f) at any real scale means multiple Opus authors on disjoint file
  sets, which is necessary for tractability but leaves nobody responsible for
  cross-file consistency: a shared summary file (an `index.md` node table)
  none of them owned went stale the moment any of them changed a node's
  `est_tokens`, and a fact ended up restated across two files two different
  authors touched. Phase 6 gained a **cross-author rebalance** gate — one
  final docs-librarian spawn seeing the whole graph at once, followed by a
  structural topology audit (node `kind` correctness, `requires`/`peers` edge
  sense, topology-map completeness) — for exactly the class of drift a
  passing `graph-lint.py` cannot see, because it validates that edges
  resolve, not that a parallel absorption reconciled correctly.

### Superseded

- 5.x "three symmetric surfaces" layout (kernel + tool-dir machinery +
  graph): superseded by the single graph surface + bootstrap + projections.
- `.core/operating-principles.md` shipping convention (5.6.0): superseded
  by the `method.*` posture nodes.

## 5.7.0 — the design-for-responsibility doctrine, woven and planted (2026-07-22)

Executes the SOLID / separation-of-responsibilities integration that had sat
as an unexecuted plan (`docs/plans/integrate-design-doctrine.md`) — the one
doctrine found injected-but-never-woven by the 5.6.0 audit — rebased onto the
post-5.6.0 seed (the plan's section anchors had moved +4, its version slot
was taken, and the `.core/` shipping convention postdates it). Same method as
5.6.0: integrated into existing homes, shipped to plants, and wired into the
surfaces that act on it — with the plan-time weave the original plan lacked.

### Canonical home: `core/operating-principles.md` (new §13–§19; 20 → 27 principles)

- **§13 Design for the smallest structure that fits** — separation is a
  tool, not a quota; correct separation, never maximum; project idioms and
  ADRs win on conflict.
- **§14 Responsibilities are reasons to change** — one coherent obligation
  per component; split by reason-to-change, owner, and failure/security
  semantics, never by size; do not split when it scatters an invariant.
- **§15 Cohesion and coupling are the real metrics** — direction and
  stability over count; hidden coupling worse than explicit; no cycles.
- **§16 Depend on stable contracts, not volatile detail** — inversion via
  the smallest mechanism; DI is not dependency inversion.
- **§17 Honor contracts at type boundaries** — interfaces sized to the
  consumer; substitutability or composition.
- **§18 Own state; separate deciding from sequencing** — policy apart from
  orchestration; validation and error handling live where the decision does.
- **§19 Abstract only where variation is real** — over-abstraction is a
  defect exactly as under-abstraction is (§8: structure earns its rent);
  closes with the applying-to-a-change questions and the anti-pattern list,
  and names one-home-per-fact as the graph's single-responsibility rule.
- Overlaps folded, not duplicated: §9 (Integrate) gains the
  duplicated-*policy* nuance linked to §14; §12 (side effects) names itself
  dependency inversion made concrete, linked to §16. Tail renumbered
  §20–§27; internal references updated.

### Durable in planning (the plan-time weave)

Structure is now decided where it is cheapest to reject — the plan:

- `templates/grill.template.md` §9 — an increment that adds structure (a
  module, layer, interface, service) names the single responsibility that
  structure owns and the present variation justifying any abstraction.
- `skills/grill-planner/SKILL.md` — new "Structure earns its place at plan
  time" rule: the plan's default is the smallest structure that fits; a
  speculative seam is cheapest to delete before it is built.
- `agents/01-architect.md` — the non-negotiable boundary rule is named as
  dependency inversion applied, with the one-responsibility and
  real-variation-only rules beside it.
- `agents/02-implementer.md` — an abstraction the spec's variation does not
  demand is the same violation as bolting on (§19).
- `agents/03-reviewer.md` — "Architecture adherence" becomes "Architecture
  & responsibilities": responsibility cohesion and dependency direction are
  audited per diff; over-abstraction stays with the Minimum-sufficient-work
  block (one home — it is a design and an economy defect at once).

### Self-application: the seed audited against its own design cluster

Asking "does the seed obey §13–§19?" found four structural defects, all
in one family — structure without a clearly-owned seam — and fixed them:

- **brainstorm protocol ↔ brainstorm-socratic skill** — duplicated policy
  across layers (the §14 anti-pattern by name): questioning mode, cap,
  convergence checklist, output map, and anti-patterns all stated twice.
  Re-split on the protocol=workflow / skill=technique seam: the protocol
  keeps entry, the grill.md output map, and the explicit-confirmation
  exit; the skill is the one home for the Socratic method and the
  eight-point checklist. 9.0 KB of doubled policy → 6.3 KB, zero overlap.
- **test-first protocol ↔ test-first skill** — same policy stated twice
  in *different words* (the worst drift shape), and the drift had already
  happened: the protocol's COMMIT still told the session to edit the wiki
  inline, contradicting the §3.7 close-out rule the skill carried. Same
  seam applied: the protocol is the workflow home (gaining the skill's
  corrections — spec-§10 status rows, prove-RED-by-mutation for inherited
  suites, the intentionally-failing known-bug variant, the migration
  safety gate, the CI-parity anti-pattern, and the canonize-consistent
  COMMIT); the skill is the test-shaping technique (level selection,
  contract naming, one outcome per test). 17.5 KB → 12.8 KB; the
  contradiction resolved in favor of §3.7. Four references repointed to
  the content's new home.
- **threat-model.template.md orphaned** — the security agent inlined its
  own copy of the template's section list (the same second-home defect
  data-ml had), which is why nothing referenced the template. Inline copy
  replaced by the reference.
- **investigation-brief.md unrouted** — the orchestrator now names it as
  the brief for generic read-only investigations (growth has its own
  scout/author pair).

Both pairs' descriptions now state *different responsibilities*, so the
consumer choosing what to load can tell them apart (§17 — the interface
sized to its consumer).

### A rework lens for the seed's own growth

- `protocols/grow.md` Phase 6 check 9 extends to **well-composed**: a node
  owning unrelated facts is weak cohesion to split; a node that only
  forwards is a pass-through to delete — mis-composition routes back to an
  author exactly as over-growth and gaps do. (Graft and harvest inherit the
  lens through their existing §5–§8 audit gates, which §19 now cross-links.)
- `protocols/graft.md` Phase 5 gains the **own-kernel plants still receive
  the substance** rule, found by grafting a plant that deliberately carries
  no seed machinery: its machinery is KEEP-PLANT, but the seed's substantive
  delta is re-WOVEN into the plant's equivalent surfaces — each seed surface
  the delta changed mapped to the plant surface where that rule acts (verify
  discipline → validation playbook, reviewer checks → change guide, kernel
  posture → instruction file), in the plant's idiom. Collapsing the delta
  into one summary section is a photocopy, not a graft. A stamp advance with
  the substance undelivered is bookkeeping, not an upgrade; the quality bar
  now fails both explicitly.

### Installer fix (found by the first full absorption of an own-kernel plant)

- `install.sh` github-copilot adapter: the repo-root kernel drop used a raw
  `cp`, which on a plant whose `copilot-instructions.md` was a symlink wrote
  THROUGH the link and clobbered its target file (the plant's own instruction
  system — recovered from backup). Now `place_file`, whose backup `mv` takes
  the symlink itself.

### Shipping

Rides the 5.6.0 machinery unchanged: the file installs to
`<tool dir>/core/operating-principles.md` in all four adapters, is
referenced as `.core/operating-principles.md`, and grafts with `core/`
audit coverage. Zero kernel bytes. Manifest gains the 12th principle
("Design for responsibility…"); version → 5.7.0. The executed plan file
`docs/plans/integrate-design-doctrine.md` is superseded by this entry.

## 5.6.0 — the minimum-sufficient-work doctrine, integrated holistically (2026-07-22)

The seed enforced *what* must be done (specs, tests, gates, canonize) but had
no single posture for *how much* — so effort scaled with capability and habit
instead of uncertainty and consequence, and nothing reviewed growth, graft, or
harvest for over-delivery. This release ingrains the minimum-sufficient-work
doctrine into the seed's existing homes — no new file, no parallel doctrine
document, zero kernel bytes (the kernel's tiers and load-minimally rules
already carry its per-session essence; the depth lands at reference tier) —
and ships that reference tier to every plant: `operating-principles.md` is now
installed machinery (`<tool dir>/core/`, referenced seed-wide as
`.core/operating-principles.md`), carried by graft, and woven into the
canonical delegation block so the doctrine governs every worker of every
plant, including the scouts and authors that grow it.

### Canonical home: `core/operating-principles.md` (new §5–§8; 16 → 20 principles)

- **§5 Do the minimum sufficient work** — governing objective (smallest body
  of work that reliably delivers the required result), the precedence order
  when goals conflict (safety → contracts → correctness → completion →
  validation → efficiency → polish), what efficiency may never justify
  (invented information, skipped required checks, concealed failures), the
  execution shape, and the scaling rule: effort follows uncertainty and
  consequence, with the kernel §0 tiers as the instrument — the tier
  authorizes the maximum process; this principle selects the minimum within it.
- **§6 Every operation serves a decision** — decision-relevance test for
  every read/search/tool call/spawn, the marginal-value continuation rule,
  progressive retrieval and the query-precision ladder, single-authoritative-
  source default, direct-execution bias, batching, and no unchanged retries
  (deferring to `recover` for classification).
- **§7 Stop when the result is sufficiently trusted** — termination and
  escalation conditions (escalation only for a named unresolved decision;
  never completeness theater), the one bounded pre-finalization audit, and
  the assumption-vs-clarification discipline.
- **§8 Structure, artifacts, and delegation earn their rent** — lifecycle-cost
  test for every abstraction/layer/agent/artifact, minimal-worker-set
  delegation economy, intermediate-artifact criteria (the growth ledger as
  the model), alternatives only when material, prompt/instruction economy
  (one home per rule, generalize before appending — the kernel byte budget
  named as this rule enforced), cheapest-competent-method, and future-cost
  awareness.
- §4 (Load the minimum context) extended with its general form: context as
  working memory (admission test, smallest sufficient representation, exact
  retention only where fidelity matters, eviction), and delta discipline for
  long sessions (one compact canonical state; the transcript is history).
- Tail renumbered §9–§20; internal §-references updated.

### Enforcement wiring (each concept folded into the home that acts on it)

- `skills/context-router/SKILL.md` — cost discipline gains the progressive
  retrieval ladder and query-precision order within the loaded closure.
- `protocols/verify.md` — gate selection is risk-first (test the assumption
  most capable of invalidating the increment first), prefers one
  high-information gate over overlapping ones, and stops when mandatory gates
  pass and residual uncertainty is immaterial.
- `protocols/deliver.md` — quality bar gains the smallest-sufficient-summary
  pass line and a fail line for narration that taxes future turns.
- `agents/03-reviewer.md` — new "Minimum sufficient work" checklist block:
  over-work is a finding exactly as a gap is (speculative structure,
  unconsumed artifacts, duplicated validation, more machinery than the spec
  required).
- `agents/00-orchestrator.md` — new invariant: every spawn, gate, and
  artifact serves a named unresolved decision; minimal worker set within the
  tier's authorized maximum.

### The growth reviewer (grow / graft / harvest audit their own additions)

- `protocols/grow.md` — Phase 6 validation gains check 9: the growth is
  minimum-sufficient (every node/leaf/specialist serves a real need, no
  artifact without a consumer, no second fact home, compact router);
  over-growth findings route back to authors exactly as gaps do.
- `agents/growth-orchestrator.md` — step 5 gates the *size* of the growth,
  not only its correctness.
- `protocols/graft.md` — Phase 6 gains the **minimum-sufficient upgrade**
  gate (the graft reviewer): fast-forwarding machinery is the contract;
  everything beyond it must cite the plant evidence that demanded it, merges
  must be the smallest re-integration preserving both intents, and an
  unconsumed or thinly-evidenced addition BLOCKS that item. Added to the
  integrity-gate output block and the quality bar (over-delivery is a
  failing graft).
- `protocols/harvest.md` — Phase 4 gains the **minimum-sufficient fold-back**
  gate: generalize an existing rule before appending a sibling; land lessons
  in the cheapest surface that reaches their audience (kernel bytes cost
  every session of every plant); a fold-back that could be a one-line
  sharpening is returned in that form.

### Shipped to plants, and woven into growth itself

The depth is not seed-internal: it installs, grows into new organs, and
grafts forward.

- `install.sh` — all four adapters place `core/operating-principles.md` at
  `<tool dir>/core/operating-principles.md` (claude-code, opencode, codex,
  github-copilot); every seed-wide reference uses the in-plant
  `.core/operating-principles.md` notation (graft/harvest keep the
  seed-relative path — those two protocols hold the seed itself in hand,
  like their `tools/graft-*.py` references).
- `templates/prompts/graph-session-bootstrap.md` — the canonical GRAPH
  DISCIPLINE block gains rule 5 (minimum sufficient work: every operation
  serves the delegated deliverable; smallest sufficient evidence; stop when
  trusted; return findings, not dumps), so every delegation brief of every
  plant carries the doctrine across the clean-context boundary — the same
  vehicle the graph discipline rides. Synced byte-identically into all four
  embedding briefs (seed-lint enforces).
- `templates/agent.template.md` — every expert a plant commissions inherits
  the posture in its "Context you load first" contract.
- `templates/prompts/growth-author-brief.md` — growth authors carry the
  smallest-sufficient-artifact rule, closing the loop with grow's Phase 6
  over-growth check.
- `tools/graft-audit.py` — the customization audit maps `core/` backups to
  their seed source, so a plant's local divergence in the posture file is
  preserved and flagged exactly like any other machinery divergence.
- `INSTALL.md` step 1 documents the placement.

### Seed-wide weave: the doctrine applied to the seed's own prose

A full review of every agent, protocol, skill, template, and entry prompt,
with the doctrine as the lens and plant-session token cost as the metric.
Almost every finding was a deletion or consolidation — the doctrine's own
prediction: the cheapest instruction is the one you stop paying for.

- **Duplicated rules re-homed** (one home per rule; the copy becomes a
  reference): implementer's tail bullets restating its body; architect's
  third restatement of its spawn allowlist; the no-fabrication rule stated
  beside the GRAPH DISCIPLINE fence that already carries it (investigation,
  node-authoring, growth-scout briefs); knowledge-graph skill's key-semantics
  gloss and anti-pattern list (home: `_schema.md`); the source-conflict
  ladder stated by both research-scout and docs-librarian (home: the scout);
  canonize's re-teaching of the toolcraft doctrine; grill's duplicate
  toolcraft anti-pattern; from-scratch re-listing ingest-library's checks and
  its sub-protocols' failure modes; initialize re-listing grow's policy;
  specify's second hand-to-section mapping; ingest-library's prose copy of
  the library-page template's section list; data-ml's inline copy of the
  data-contract template; multi-agent-architect's anti-patterns restating its
  own pre-ship checklist, and its thrice-stated model tiers (IDs now pinned
  via `claude-api`, never memory); adopt-existing's duplicated handoff
  sentence; GRAFT/HARVEST prompts' repetition-for-emphasis.
- **Inlined structure moved to point of use**: product's two document
  skeletons now live in the installed `docs/graph/product/README.md`;
  docs-librarian's 55-line directory tree compressed to the shape the docs
  skeleton and `_schema.md` already own.
- **Templates stopped breeding boilerplate**: spec §5 gains the bind-only
  NFR rule; grill §10 defaults to the verification-runbook pointer (expand
  only on divergence — grill.md is read every session); grill §12 compressed
  to point-of-use cues; the library page is demand-grown (§0–§3 on creation,
  never "none" rows to look complete), matching the library-wiki skill.
- **Discipline inserted where it was missing** (the few additions): the
  handback payload — re-read by the caller every turn — gains
  shortest-sufficient-form; security findings gain a reachable-path,
  no-scanner-dumps output cap.
- **Deliberately declined**: trimming security's and reliability's
  rationale tails — those are harvested operational tells, and the
  precedence order puts safety above efficiency.

### Manifest

- 11th principle ("Minimum sufficient work…") added; the
  `operating-principles.md` kernel entry records its install path and graft
  coverage; version → 5.6.0.

## 5.5.0 — growth gets a producer/consumer contract: scouts collect, authors apply (2026-07-21)

Growth had a seam it papered over. Scouts ran on the *generic*
`investigation-brief.md` and authors on the *generic* `node-authoring-brief.md`;
the `growth-scout` agent promised an "evidence ledger" that had **no schema
anywhere**, and authors received facts pasted ad hoc. So every grow/adopt run
re-improvised both what to collect and how to generate from it — the
implementation phase effectively regenerated structure from scratch each time.
This gives growth its own matched pair of briefs joined by a defined
intermediate artifact, so scouts collect exactly the feedstock the deliverables
need and authors build on it instead of re-investigating.

### New (three growth-dedicated prompt templates)

- **`templates/prompts/growth-evidence-ledger.md`.** The canonical schema of the
  one artifact that passes between scout and author. Its sections are keyed 1:1
  to every growth deliverable — graph nodes/wiki (product, architecture, api,
  data, libraries, prompts, evaluations), `specs/` candidates, `decisions/` (ADR)
  candidates, **project-specific specialist agents**, and `runbooks/`+verification
  (discovered, not executed) — so the scout knows *why* it collects each fact and
  the author knows *where* each fact goes. Every claim carries `path:line` +
  symbol; empty sections are `none found`, unestablished facts `not recorded`.
- **`templates/prompts/growth-scout-brief.md`.** The growth-dedicated read-only
  scout brief. Unlike the generic investigation brief, its collection target IS
  the ledger schema; it embeds the canonical GRAPH DISCIPLINE block verbatim and
  directs the scout to write one ledger per boundary.
- **`templates/prompts/growth-author-brief.md`.** The growth-dedicated author
  brief. It CONSUMES the ledger and routes each section to its deliverable,
  building only on cited claims (a `not recorded` stays unrecorded; a `none
  found` is omitted, never invented). It embeds `node-authoring-brief.md`'s HARD
  RULES for the node case and points at the spec/ADR/agent/library templates for
  the others.

### The ledger is a seed organ, not a plant organ

Ledgers are growth-time feedstock, transient to a grow/adopt run. They are
persisted to the plant's **gitignored** seed-adjacent scratch,
`.cypress/growth/<slug>.ledger.md` — never under `docs/graph/`, which is
permanent plant knowledge. The plant-owned `.cypress/seed.json` stamp stays
tracked; the growth scratch does not. After delivery the plant keeps its graph
and may discard the scratch — the grow/graft/harvest machinery is a seed organ
the living plant does not carry.

### Wiring

- `protocols/grow.md`: the mandatory worker topology and Phases 1–4 now dispatch
  the growth-dedicated briefs, gitignore `.cypress/growth/` before scouting,
  treat the persisted per-boundary ledgers as the evidence set, and formalize a
  spec/ADR/specialist-agent only from the ledger section that grounds it.
- `agents/growth-scout.md`: output section now references the canonical ledger
  schema and the persisted seed-organ location instead of paraphrasing a format.
- `agents/growth-orchestrator.md`: steps 3–4 dispatch the dedicated briefs,
  ensure the scratch is gitignored, and map ledger sections to deliverables.
- `manifest.json`: the three templates registered; version → 5.5.0.
- `tests/seed-lint.py`: the two new runtime briefs join the GRAPH DISCIPLINE
  byte-identity check.

## 5.4.0 — graft becomes a true, audited, growing upgrade (2026-07-21)

Distilled from a multi-plant graft that exposed three gaps between what
`graft` *promised* and what its tooling *did*. The protocol leaned on the
installer's blind fast-forward, and the installer neither upgrades the graph
engine nor checks what it overwrites — so a "true upgrade" could leave a plant
on a stale linter, silently bury a plant's local customization, and deliver new
capabilities as inert machinery that never actualized. This closes all three,
holistically across `graft`, `grow`, and `harvest`, with two tested support tools.

### New (support tooling — a new `tools/` home for seed-operator scripts)

- **`tools/graft-graph-engine.py`.** The installer drops the knowledge-graph
  scaffold (`graph-lint.py`, `spec-lint.py`, …) only if absent, so a graft left
  plants on their old engine. This performs a **config-preserving fast-forward**:
  adopt the seed's current engine body, re-inject the plant's own PROJECT CONFIG
  (`ROOT_ID`/`KINDS`/`KIND_PREFIX`; `TEST_GLOBS` via `--preserve`), and adopt the
  seed default for a knob the plant predates. Detects a plant engine that is a
  strict **superset** of the seed's (KEEP-PLANT, unchanged, a harvest candidate).
  Quote-aware inline-comment normalization so cosmetic drift is not mistaken for
  a real engine difference.
- **`tools/graft-audit.py`.** The reconcile-before-overwrite gate. Maps every
  fresh backup to the seed source that replaced it and classifies IDENTICAL /
  DELTA (normal version advance) / **CUSTOMIZED** (differs *and* carries
  plant-signal content — a divergence the blind FF buried, exit 1 until
  re-integrated or ratified). Flags knowledge overwrites under `docs/graph/`;
  optional engine-currency check. "Plant-signal" catches generic self-reference
  ("this project's", "this program"), not just the plant name.
- **`tests/test-graft-tools.sh`** wired into `tests/run.sh` — proves both tools
  non-vacuously on synthetic fixtures (config preserved, superset detected,
  customization flagged with a gate exit, clean FF passes).

### Changed — `graft.md`

- **The graph engine is machinery too** (Phase 3): reconcile it explicitly and
  config-preservingly — a graft that leaves a plant on a stale engine is not a
  true upgrade; `_schema.md`/`index.md` stay the plant's (project-instantiated).
- **The blind fast-forward is only real if audited** (Phase 3 → gate in Phase 6):
  the installer overwrites with a backup but never checks for a customization
  first, so a mandatory post-FF audit is the only thing that keeps the
  reconcile-before-overwrite promise. An un-reintegrated customization BLOCKS.
- **New Phase 5 — grow the new capabilities onto the living plant.** Grafted is
  not grown: a carried capability is inert until actualized. Grow what the plant
  evidently needs, grounded in its own facts; never fabricate a skill/ADR/runbook
  to fill a surface (those sprout from real use, owned by `canonize` →
  `docs-librarian`); and **surface every capability grafted-but-not-grown** so
  copy-but-not-actualized never reads as delivered. Phases renumbered 5→6, 6→7.
- Integrity gate + output format gain: engine upgraded (or superset kept),
  customization audit clean, capabilities grown-or-surfaced. Quality bar updated.

### Changed — `grow.md`, `harvest.md`

- `grow`: the anti-fabrication rule now names **project skills** explicitly — an
  empty procedure/decision/runbook surface is left to sprout from real use at
  close-out, never fabricated to look populated.
- `harvest`: a prior graft's customization-audit ledger + KEEP-PLANT list is a
  ready-made **divergence inventory** that feeds harvest candidates directly. New
  donor surface: a **capability the seed ships that stays inert across plants** is
  a design signal (a missing withdraw contract or grow step) — harvest the fix to
  the seed's own machinery, never any plant's would-be content.

## 5.3.0 — harvest: decision/verification discipline + harvest's own donor surfaces (2026-07-20)

A multi-plant harvest gathering generalizable discipline from several mature
grown plants. The dominant finding is itself folded back: a plant grown from
the seed reflects the seed's own doctrine back through its ADRs, plan-of-record,
best-practices, and runbooks, so most candidates a plant-only survey turns up
are the seed's existing rules filled in with local facts. Only the genuinely
net-new residue landed; everything already owned by a seed agent/skill/protocol/
template was rejected as redundant. (Plant-identifying provenance stays in the
ratification record, per harvest's agnosticism gate.)

### New / changed

- **`protocols/harvest.md` — new donor surfaces + a third gate.** Phase 1 now
  names the plant's plan-of-record (`grill.md` §6/§7/§11/§12), best-practices
  pages, and runbooks as donor surfaces, each mined for *discipline*, not
  content. A new **non-redundancy gate** (alongside agnosticism and durability)
  requires every candidate be checked against its would-be seed home before
  proposal; a rule the seed already owns is rejected, not re-harvested — an echo
  of the seed's own doctrine is not a lesson, and a second home splits a fact
  the one-home-per-fact rule keeps single.
- **`protocols/verify.md` — behavior-preservation gate + self-expiring
  known-defect exception.** A new gate class for behavior-preserving changes
  (characterize first; diff against a baseline oracle; allow only an enumerated
  intended-delta list — observable-behavior preservation is the contract, not
  byte-identical output). A `KNOWN_BUG_<id>` assertion pattern that asserts a
  known-broken behavior on purpose and flips to FAIL when it is fixed, so
  tolerated debt is mechanically visible and self-retiring rather than a silent
  green.
- **`agents/05-security.md` — token/crypto defaults + scan-coverage.** Verify
  the expected signature algorithm structurally (reject `alg:none`/family
  confusion); revocation keys on a stable id and a revocation path is required
  by design; authentication failures are response-indistinguishable (no
  user-enumeration oracle). And confirm what a dependency scan actually examined
  — an unconfirmed-coverage scan is a green lie about what it inspected.
- **`agents/00-orchestrator.md` — planning/decision discipline in the brief
  contract.** A delegation brief that produces a plan or records a decision must
  carry the `grill-planner`/`adr-writer` discipline verbatim; a clean-context
  worker has only what the brief carries, so an omitted discipline is silently
  lost by the plan and the decision record.
- **`skills/adr-writer` — don't fabricate a decision.** An as-built observation
  reconstructed from source is not an ADR; "do nothing now" is a recordable
  decision (destination separated from its timing trigger); record the
  asymmetric cost of being wrong in each direction.
- **`skills/grill-planner` + `templates/grill.template.md` — cite-or-mark
  discipline.** Unconfirmed claims carry a `[verify]` tag; §12 rows needing
  human input are marked do-not-guess and left for sign-off; resolve rows in
  place, never by deletion.
- **New runbook templates — `release`, `rollback`, `incident-response`,
  `operations`** (under the seed's runbook-template dir). The base roster's
  operations agent already references these runbooks; the templates now exist,
  each with its discipline baked in: a
  release-readiness gate (shipped ≠ hardened; a tested rollback path is
  required) and released-bits-are-tested-bits; a rollback that is
  fix-forward-first, non-autonomous, and reversible-before-destructive; an
  incident loop that contains without destroying evidence and closes by adding
  a gate + regression.
- **`agent-corpus/` — new suggested-expert catalog** (the roster mirror of
  `library-corpus`/`tool-corpus`). A stable, agnostic surface for **optional**
  specialist roles a project selects on demand — held outside the always-loaded
  16-agent roster and the kernel §1 table, so it never touches the per-session
  kernel budget. Seeded with four generalized roles (legacy-runtime
  reconstruction, inter-service topology, config/secret-contract
  reconciliation, client/frontend) that are genuine roster gaps corroborated
  across independent plant lineages but do not earn always-on per-session
  rent. `harvest` (new corpus section + Phase 3 target) now has a
  home to fold generic foreign roles into; `grow`/`graft`/commission withdraw
  from it via `templates/agent.template.md`.
- **Skills become a per-project surface — `skill-corpus/` + `skill.template.md`
  + a `toolcraft` authoring path.** Closes an asymmetry: agents (roles) and
  tools (artifacts) each had a per-project authoring path and a harvest corpus,
  but skills (procedures) had neither — the core `skills/` were the only skills
  a plant ever saw. `toolcraft` now names the durable **skill** (a procedure)
  as the sibling of the durable **tool** (code): when a repeatable procedure
  recurs and no core skill covers it, author it as a project skill in
  `.claude/skills/` from the new `templates/skill.template.md`; `harvest` folds
  the agnostic ones into `skill-corpus/`. Seeded with one corroborated
  inaugural procedure (a behavior-preserving framework/dependency migration,
  composing the `verify`/`grill`/`adr-writer`/`security` disciplines) —
  observed across independent lineages, skill-shaped, previously homeless.
- **The plant now sprouts skills over its life.** The authoring path is wired
  into the operating lifecycle exactly as tools are: `toolcraft` design-time
  names a recurring *procedure* as a unit of work; workers flag it in the
  handback's new `skills_built` field; and the single `canonize` close-out has
  the **docs-librarian** crystallize it into `.claude/skills/` from
  `skill.template.md` (checking `skill-corpus/` first, deduping against skills
  present). The same fail-closed rule applies — a procedure worn in by
  repetition but left uncaptured is a silent capability leak, the sibling of an
  uncatalogued tool. The librarian's mandate, audits, and routing now cover the
  project-skill catalog.
- **First real harvested skill + its supporting corpus — remote-Docker
  deployment.** `skill-corpus/deploy-fleet-on-remote-docker-host.md` is one
  universal method for taking a fresh multi-repo fleet online on a remote
  Docker host over SSH, averaged from several independent lineages and reduced
  to a single path by one invariant: **always build on the remote host, never
  locally** (the multi-stage build-from-source Dockerfile puts the toolchain in
  the build stage, so the host needs only Docker). It prescribes the `deploy/`
  folder, the Dockerfile rules, one base compose + dev/qa/prod overlays,
  loopback-only sensitive ports, the ship-source-then-build-on-host pipeline,
  stdin-only secret rotation, and a live smoke gate — composing existing
  `tool-corpus`/runbook artifacts by reference, parameterized by host+key (the
  `/deploy-fleet` invocation, which a project aliases to taste). Host hardening
  is a **standalone skill**,
  `skill-corpus/harden-docker-host.md` — run by `reliability`, called from the
  deploy method's host-prep step or on demand — that applies and **verifies
  active** the floor in its knowledge base, the new
  `library-corpus/container/docker-host-hardening.md` (recent-Ubuntu-LTS +
  Docker: SSH, an operator-gated firewall — never automatic, since it can lock
  out access or collide with an upstream firewall — the root-equivalent
  daemon/socket, the ufw-vs-Docker-iptables trap, with loopback binding as the
  always-on containment). `docker-compose.md` gained readiness-ordered
  startup, loopback binding, and base+overlay dev/qa/prod modes; the
  `reliability` agent points at the hardening procedure in its bring-up.

- **`seed-lint` now guards the corpora.** Extended `tests/seed-lint.py` with an
  agnosticism / cross-reference floor over `core`/`agents`/`protocols`/`skills`/
  `templates` and all four corpora: a leaked host-IP literal, a pinned CVE, or a
  dangling corpus/template reference now FAILS the gate. Objective leaks only —
  project names and stack fingerprints stay human judgment (the seed cannot
  blocklist plant names without itself naming them). Closes the gap where the
  new corpus surfaces had zero lint coverage and "agnosticism scan PASS" was a
  hand-assertion (found by an adversarial review of this harvest).

### Seed integrity gate

- Agnosticism scan: PASS — no plant name, host/IP, key, path, stack fingerprint,
  or identifying count in the diff or this entry; the only version tokens are
  illustrative OS-line examples (orientation, not pins). The objective-leak
  class (host IPs, pinned CVEs, dangling corpus refs) is now **mechanically
  gated** by `seed-lint` over the corpora, not hand-asserted.
- Seed lint/tests (`bash tests/run.sh`): PASS — 6 install/consistency suites,
  agent-lint (16 agents), routing eval 100% (42/42), seed-lint PASS.
- Kernel budget: unchanged — 20940/21000 bytes; no kernel edits, no roster change.
- Version bump: 5.2.0 → 5.3.0; CHANGELOG updated.

## 5.2.0 — harvest: `graph-lint.py` gains `KIND_PREFIX` (2026-07-17)

Harvested from a mature plant during its 4.9.0 → 5.1.0 graft: the plant's
steward had advanced its own `docs/graph/graph-lint.py` engine with a
generalizable feature the seed template lacked, so graft kept the plant's copy
(KEEP-PLANT) and raised it as a harvest candidate. This folds that capability
back into the seed for every future plant. (Plant-identifying provenance
stays in the ratification record, per harvest's agnosticism gate.)

### New

- **`graph-lint.py` — `KIND_PREFIX` mapping.** A node's `kind` no longer has to
  equal its id-prefix. `KIND_PREFIX` maps a kind → the id-prefix its nodes must
  carry, so a verbose kind name (e.g. a `devops` subsystem family) can live in a
  terse or shared id namespace while still linting. Absent from the map, a kind
  keeps the identity rule (ids must start with `<kind>.`), and the default `{}`
  means every existing graph lints exactly as before — additive, backward-
  compatible. Ported into `templates/knowledge-graph/graph-lint.py` holistically
  (new `kind_prefix()` helper + `check_schema` using it); the seed's generic
  `KINDS` default is unchanged — only the engine gained the capability, no
  project-specific kinds entered the seed (harvest's agnosticism gate).

## 5.1.0 — the seed gates itself: routing eval in CI, four-tool install contract, integration drift fixed (2026-07-16)

Eight audit passes over the surfaces v5.0.0 hadn't reached: the seed's
own CI, the integration adapters, the corpus contract, and the last
unswept protocol/agent prose.

### New

- **The routing gates run in the seed's own CI.** `agent-lint.py` gained
  `--dir`, so `tests/run.sh` now runs `--lint` (frontmatter + delegation
  graph) and `--eval` (golden routing corpus: 100% top-1, 42/42,
  novel-stack phrases correctly LOW/NONE) against `agents/` on every
  test run. Until now these fail-closed gates existed only inside
  plants; the seed could not check its own router.
- **`tests/test-full-install.sh` — the four-tool install contract.**
  Installs every adapter into a scratch plant and asserts the v5 runtime
  machinery lands: templates/briefs/bootstrap, recover protocol and
  commands, spec-lint, in-plant `agent-lint --lint`, opencode's
  single-instruction config, codex's full skill registration. Guards the
  never-installed-templates defect class permanently. The suite is now
  **10 gates**.

### Fixed

- **Codex plants were missing the knowledge-system core.**
  `config.toml.example` registered only 9 of 13 skills — absent were
  `context-router`, `knowledge-graph`, `holistic-editing`, and
  `validate-knowledge`, the four most doctrine-critical. All 13 now
  registered; INSTALL.md's stale "eight skills" corrected, its installer
  step now mentions template placement, and the Copilot uninstall list
  gained `.github/templates` + `.github/hooks`.
- **Corpus contract disagreement.** `ingest-library` described the
  seed corpus as version-keyed (`<library>@<version>.md`) while
  `harvest` and the actual corpus files are version-unkeyed. One
  contract now: the corpus holds the version-durable layer, keyed by
  library; the pin check always runs against the plant's real lockfile
  and never trusts the corpus for version-specific facts.
- **Route hook now fires the tier spine.** The per-prompt injected
  mandate adds the tier-classification step (T0–T3), so kernel §0 runs
  deterministically on every prompt, not only when the model recalls it.
- Path-convention residue in protocols (`initialize`, `grow`,
  `canonize`, `toolcraft`, `test-first`) normalized to plant-facing
  dot-names; `multi-agent-architect` no longer restates the bootstrap
  block (references + embeds the canonical one).
- Protocol and agent-body audits (partly inline after two subagent
  attempts died on server 529s — classified transient, retried twice,
  then strategy changed per `recover`'s own discipline): agent bodies
  clean on every violation class; protocols clean beyond the path fixes
  above.

## 5.0.0 — the efficiency overhaul: risk-proportional tiers, one close-out, one home per rule (2026-07-16)

The seed preached minimum-sufficient context to every plant while paying
maximum-uniform process itself: a 27 KB kernel restating each rule two to
four times, two librarian spawns closing every task, the full delegation
funnel for a typo, and its own meta-facts duplicated across README /
kernel / manifest until they drifted (the README claimed 5 coordinators,
a 12-agent team, and a ~9 KB kernel; frontmatter said six, sixteen, and
27 KB — the exact asymmetric rot `one home per fact` predicts). 5.0.0
turns the knowledge rule on the seed itself.

### Changed — breaking (doctrine)

- **Risk-proportional task tiers (kernel §0).** Every task is classified
  before acting: **T0** question (read + cite, no spawn), **T1** trivial
  non-behavioral edit (the one in-session authoring exception; one
  focused gate; compact delivery), **T2** spec-covered change (minimal
  worker set), **T3** spec-bearing work (full delegated funnel). The
  former "no authoring exception for a small edit" rule is superseded:
  its cost was four model contexts per typo. The tier edges are hard —
  T1 cannot touch behavior/contract/spec surface, T2 requires existing
  authorization — and misclassifying down is the violation.
- **One close-out spawn (§3.7 + §3.8).** `canonize` now owns the single
  end-of-task docs-librarian spawn that persists knowledge AND catalogs
  durable tools in one brief and one graph-lint pass; `toolcraft` keeps
  the durable-tool doctrine but never spawns separately. Both fail-closed
  guarantees are unchanged; the second spawn (same bootstrap, same lint)
  was pure coordination waste. T0/T1 satisfy close-out with a one-line
  self-record in the compact delivery.
- **Risk-proportional verification (`verify.md`).** A change-class →
  gate-depth table: one focused check for a T1 edit up to the broad
  battery for contract/security/persistence/concurrency changes;
  uncertainty buys breadth, never a discount.

### Changed — structure

- **Kernel rewritten, 27 KB → ~20 KB with tiers added.** Every rule now
  has one home (§3 owns the eight rules; §2 and §5 are pointers);
  harvest/graft explained once instead of three times; delegation bounds
  once instead of three. Stable §3.1–§3.8 anchors preserved — every
  cross-reference in the seed still resolves.
- **`templates/prompts/graph-session-bootstrap.md` — the canonical
  graph-discipline block.** Runtime briefs embed it verbatim (hooks do
  not reach subagents — that stays); static seed files reference it
  instead of paraphrasing. The brief templates now carry a fill-time
  paste placeholder rather than their own wording of the same rule.
- **Orchestrator rewritten** around the tier decision tree; delegation
  brief contract unchanged in force, now referencing the canonical block.

### Changed — per-spawn and per-tool costs (second pass)

- **opencode no longer double-loads the posture.** Its `instructions`
  list carried `core/operating-principles.md` (9.2 KB, self-described as
  the "deep version" of what AGENTS.md already states) on every session.
  The kernel is now the only always-loaded instruction file for every
  tool; operating-principles is the on-demand deep reference. seed-lint
  budgets the sum of always-loaded instruction files (24 000 bytes) so
  this regression class cannot return.
- **Handback sections deduplicated across the roster.** Every agent
  carried a ~9-line restatement of the handback contract — a third home
  after `templates/prompts/handback-payload.md` (canonical) and the
  delegation brief (runtime carrier). All 15 non-orchestrator agents now
  carry a 3-sentence pointer preserving the leaf/delegator distinction
  and the fail-closed `produced_by` rule.
- **T2 may run RED→GREEN in one worker.** On a T2 increment the
  authorizing spec contract already pins the behavior, so the test
  cannot drift to fit the code; one test-first worker owns RED→GREEN in
  a single context and the independent `reviewer` audit stays. The
  tester/implementer split remains for increments spanning contracts or
  judgment-heavy RED phases. Halves the typical T2 spawn count.
- **`CLAUDE.md` added to the seed repo itself** — gates, the canonical-
  homes map, and maintenance conventions, so sessions working *on* the
  seed no longer start blind and re-derive them.

Deliberately untouched: `harvest.md`/`graft.md` mirroring (cold-path,
user-sovereign, loaded only on explicit invocation — dedup risk exceeds
the token rent) and `grow.md` (loaded once per growth).

### New — the missing organs (third pass)

- **`protocols/recover.md` — the failure discipline.** The seed
  specified how to work but not how to fail: nothing bounded retries,
  classified failures, or stopped a fallback chain. Now every failure is
  classified first (transient / deterministic / capability / ambiguity /
  systemic), each class allows exactly one recovery move (retry-as-is
  max 2 / change the input / re-route or commission / fix the owning
  upstream artifact / stop the line), three attempts total before
  escalating with evidence, a gate red twice reopens `grill`, and
  partial work always survives in the handback (`status: failed` +
  `failure_class`, new payload fields).
- **`templates/knowledge-graph/spec-lint.py` — "specs are executable,"
  proven mechanically.** Installed at `docs/graph/spec-lint.py` beside
  graph-lint by `install.sh`. Parses live specs for
  `### Contract: SLUG` headings, requires every slug to appear in at
  least one test file, warns on slugs tested but no longer specified,
  and treats "contracts exist but zero test files matched" as a loud
  green-lie FAIL rather than a vacuous pass. New row in `verify.md`'s
  gate table. Verified against a three-path fixture
  (fail-for-the-right-reason / pass / green-lie).
- **Session metrics — the system can now measure itself.** The full
  delivery gains a five-line telemetry block (tier + reclassifications,
  spawns by agent, route bands + overrides, retries by class, gate
  outcomes), and `harvest` Phase 1 gains its first *quantitative* donor
  surface: recurring overrides → sharpen `routing_triggers`; one-way
  tier reclassifications → tune the §0 edges; repeated retries of one
  class → a protocol is missing a step. The improvement loop now runs
  on evidence instead of anecdote.
- **Parallel delegation by independence.** The orchestrator's blanket
  "sequence specialists, don't parallelize" rule is replaced with an
  independence test: disjoint files/contracts and no output feeding →
  spawn in parallel; otherwise sequence in the plan. Genuine
  parallelism is wall-clock kept; false parallelism is a scheduled
  merge conflict.

### New

- **`tests/seed-lint.py` — one-home-per-fact for the seed's own
  meta-facts,** wired into `tests/run.sh`: roster consistency across
  agents/ frontmatter ↔ manifest ↔ kernel table, the delegator invariant
  (can_delegate ⇔ Task-in-tools, resolvable allowlists), numeric claims
  ("N-agent team", "N coordinators") checked against frontmatter ground
  truth, a hard kernel size budget (21 000 bytes), stable §3.n anchor
  presence, and manifest-path existence. The drift class this release
  fixed can no longer land silently.

### Fixed — the wiring pass (fourth)

- **Templates now actually reach plants.** `install.sh` never installed
  `templates/` — every plant-facing instruction to use the delegation
  briefs, the handback payload, the bootstrap block, or the
  spec/grill/ADR/agent templates was a dangling path in every grown
  plant on all four tools, since the beginning. All four installers now
  place the tree (`.claude/templates`, `.opencode/templates`,
  `.codex/templates`, `.github/templates`), all plant-facing prose uses
  the `.templates/` logical dot-name matching the existing
  `.protocols/`/`.agents/`/`.skills/` convention, and graft's seed-owned
  machinery inventory carries the templates and `spec-lint.py` (with the
  plant's `TEST_GLOBS` preserved) to existing plants. Verified by a real
  install into a scratch plant.
- `/recover` and `/canonize` slash commands added (claude-code,
  opencode) — the two protocols had no command adapters.

### Changed — growth path (sixth pass)

- `grow.md` Phase 6 and `INSTALL_PROMPT.md` validation loops are now
  **bounded** (two fix-and-revalidate rounds per finding, then record as
  honest unknown and hand to the user — the recover discipline); both
  previously said "repeat until clean".
- Growth configures `spec-lint.py`'s `TEST_GLOBS` while stack evidence
  is fresh, so the plant's first spec lands with a live §3.1 gate.
- The growth delivery reports birth telemetry (scouts/authors spawned,
  contradictions resolved, findings fixed, gaps left) and hands off the
  next action **with its tier**, so the next session starts classified.

### Fixed — audit passes (fifth and seventh): two subagent sweeps of all
13 skills plus an adversarial clean-context walkthrough of the kernel
hot path, findings verified then applied

- **BLOCKER:** "the session never edits the graph" contradicted the
  mandatory session writes to grill.md / changelog.md / verification.md
  (which live under `docs/graph/`) on every single delivery. Ownership
  is now scoped precisely: the librarian owns the fact-bearing surfaces
  (nodes, wiki, tool catalog); the session owns its operational
  artifacts (plan, changelog, runbook) as a stated exception
  (kernel §3.7, canonize, verify — which also gained an explicit actor).
- **T2 edge decided both ways:** kernel demanded a pre-existing plan
  line (making every fresh bug fix T3) while the orchestrator said add
  the line and proceed. Resolved: spec coverage is the authorization;
  the grill line is bookkeeping added on entry.
- **T1 self-contradiction:** "a config value with documented bounds"
  was a T1 example, but a config change alters behavior by definition —
  removed, and the edge now says so explicitly.
- **`route_evidence` had three meanings** (the line that selected this
  worker / the line for the next hop / graph-lint output). Now one:
  it always justifies `produced_by`, a new `next_route_evidence` carries
  the recommendation's routing, and the bootstrap block explicitly
  separates graph-route evidence from the field. Dead
  `needs-precondition` status removed; "none — session ends here"
  defined for final turns; seed-development references purged from
  plant-facing files.
- **Skills aligned:** adopt-existing's unbounded validation rerun
  bounded (two rounds → escalate) and given a real stopping condition +
  canonical handback; context-router's worker-session section now
  defers to the canonical bootstrap block (it keeps the traversal
  algorithm it legitimately owns); test-first's COMMIT step routes wiki
  idioms through the close-out instead of inline edits, and notes the
  T2 single-worker option; spec-author's sign-off gained the mechanical
  spec-lint tie-in (an uncovered new contract is the spec working, not
  a defect); knowledge-graph gained an explicit DONE condition;
  from-scratch states it is inherently T3; kernel tier table gained a
  catch-all row and the commissioning rule an unambiguous antecedent;
  path conventions normalized across all skills.

### Fixed

- README: 5 → six coordinators (twice), 12 → 16 agents, false "~9 KB"
  kernel claim removed; `multi-agent-architect` added to the kernel §1
  roster and `manifest.json` (it was in neither, despite being the
  largest agent and named in the delegation tiering).
## 4.9.0 — Multi-plant harvest: deploy/security corpus + the first tool-corpus (2026-07-16)

A `harvest` gathering generalizable lessons from several mature grown plants at
once. Read-only scouts surveyed each plant; every candidate then had to clear
**both gates** — agnosticism ("true for an arbitrary next project?") and
durability ("about the library, or one pinned release?") — before an author
folded its **generalized** form into the seed. Cross-plant convergence was the
strongest keep-signal: the same deploy discipline, secret-rotation ordering,
smoke-suite shape, and upgrade sequencing surfaced independently in more than one
plant, which is precisely the evidence that a lesson is not one project's flesh.
No plant name, domain noun, stack fingerprint, identifying count, path,
credential, host, port, or version pin survived into the fold-back content — the corpus, tooling,
and doctrine changes themselves scan clean.

**Provenance.** This entry generalizes lessons from several mature grown plants.
Plant identities are deliberately withheld, per the standing rule that keeps
project identity out of committed seed files; only the generalized, agnostic
form of each lesson survived into the fold-back content.

### New (library-corpus)

- **`container/` — a new ecosystem** (`docker`, `docker-compose`, `nginx`):
  build-stage/runtime-stage separation so a build host needs only the daemon;
  build-secret mounts that never become an image layer; tags vs digests; and the
  container gotchas that fail silently (remote-resolved relative bind mounts,
  host-side `$VAR` expansion in a healthcheck string, a mount path that must match
  the process's write dir, and never assuming `curl` ships in a minimal base).
- **`maven/`** — `spring-security` (filter-chain auth; allow-list must match the
  *computed* class-prefix+method-path mapping), `spring-cloud-openfeign`
  (declarative client + fallback + error-decoder + breaker), `guava`
  (`-jre`/`-android` flavour split), `hibernate-orm` (ORM under Spring Data JPA;
  lazy/N+1), `jakarta-mail` (the enduring `javax`→`jakarta` namespace split).
- **`pypi/`** — `numpy`, `scipy` (the load-bearing scalar-last vs scalar-first
  quaternion convention mismatch), `docling-serve` (the HTTP-service sibling of an
  in-process parsing library).
- **`npm/`** — `angular-material` (+CDK). **`language/`** — `flutter` (with the
  scaffolded-but-unused-app recognition heuristic, generalized to any scaffolder).
- **`library-corpus/README.md`:** documents the new `container` ecosystem and a
  convention — a hosted platform's declarative DSL (CI/deploy YAML) may earn a
  page under a platform bucket, pinned by retrieval-date rather than a version.

### New (tool-corpus — the first pages in a previously-empty corpus)

- **`ops/container-deploy-pipeline.md`:** staged remote container deploy with
  immutable-tag+digest discipline (release re-tags an already-built artifact,
  never rebuilds), polling the container's *own* healthcheck rather than a host
  probe, gated by a smoke suite. **`testing/http-smoke-suite.md`:** a
  dependency-light PASS/FAIL protocol-level smoke suite with the `KNOWN_BUG_*`
  idiom that asserts today's confirmed-broken behavior on purpose so debt is
  mechanically visible. **`ops/env-secret-rotation.md`:** safe `.env` secret
  rotation (STDIN-only supplied values, atomic rewrite, 600 floor, refuse a
  git-tracked file, name-only `--check`). **`ops/self-signed-tls-cert.md`:**
  identity in both CN and SAN. **`testing/ci-runner-local-simulator.md`:** a
  stack-neutral blueprint for reconstructing a CI agent's environment locally,
  fail-loud on target ambiguity.

### New (tooling)

- **`templates/knowledge-graph/graph-lint.py`:** an optional `KIND_PREFIX` map lets
  a verbose node `kind` use a terse id namespace; default `{}` preserves the
  identity rule byte-for-byte, so every existing project lints unchanged. Landed
  with its own stdlib regression test (`tests/test_graph_lint.py`).

### Changed (doctrine, skills, templates)

- **`agents/05-security.md`:** a secrets-hygiene vocabulary (a per-service-embedded
  secret is a fleet-wide compromise primitive; cross-boundary reuse; frontend-
  bundle exposure regardless of expiry; VC-history = permanent-compromise → rotate,
  don't scrub; rotate by blast radius and verify the rotation's *actual* effect);
  client-side token decode never gates authz; a routing-only gateway is not an auth
  boundary; two-axis severity; verify a CVE's range before flagging; network
  position is not a compensating control; cloned-archetype security-code divergence
  audit; a minimum gate-bar checklist; trust-boundary input validation (domain
  bounds, anchored prefix-strip, guarded-parse → deliberate denial not a crash).
- **`agents/06-reliability.md`:** immutable-tag+digest release discipline; poll the
  container's own healthcheck; disable non-critical health indicators that can block
  a gate; remote-boot-config-without-fallback is a total-outage SPOF; a fallback
  value must be distinguishable from a real answer; the silent container gotchas;
  config-over-source workarounds; internal-TLS fail-closed addressed by a
  SAN-matching DNS name, not a raw address.
- **`skills/holistic-editing/SKILL.md`:** a rename is never trivial when the
  identifier crosses a serialization/wire/process boundary (an unversioned
  contract). **`skills/knowledge-graph/SKILL.md`:** dated Correction notes over
  silent rewrites; separate observed-from-audited; never inline a secret's value.
  **`skills/context-router/SKILL.md`:** a naming-divergence note when names alias
  across layers. **`skills/test-first/SKILL.md`:** prove-RED-by-mutation for
  inherited suites; known-bug-as-failing-test; a no-migrations+no-tests migration
  gate; CI-environment parity for browser tests. **`skills/adopt-existing/SKILL.md`:**
  excluded legacy docs get a routable exclusion node, not silence.
  **`skills/research-and-ingest/SKILL.md`** (+ `validate-knowledge` cross-link): a
  lightweight source-reconciliation drift pass between full ingests.
- **`protocols/verify.md`:** gate reporting sharpened to an explicit tri-state —
  *executed* / *discovered* / *absent* — so silence can never imply a pass.
- **`templates/adr.template.md`:** reversibility may be graduated/time-conditioned
  (reversible now → expensive after a named milestone). **`templates/grill.template.md`:**
  an optional open-backlog table and an append-don't-fork convention for follow-up
  investigations.

### Rejected (stayed in the plants)

- Internal/proprietary library pages with no agnostic public surface.
- A plant's own in-flight seed-development WIP (reaches the seed by direct commit,
  not by harvest — folding it back would be circular).
- Common-knowledge rules the kernel or an agent already teaches, and a handful of
  narrow single-plant candidates (niche UI components, a niche sensor-fusion lib,
  thin single-driver pages) deferred to keep the seed lean.

### Harvest log

```
# Harvest — from grown plants — 2026-07-16
Harvested:   13 library-corpus pages (new `container` ecosystem; maven/pypi/npm/
             language surfaces); the first 5 tool-corpus pages into a previously
             empty corpus; 1 graph-lint tooling enhancement (+regression test);
             ~13 doctrine/skill/template fold-backs across 2 agents, 7 skills, 1
             protocol, and 2 templates.
Generalized: every plant name/domain/path/credential/host/port, every stack
             fingerprint and identifying count, and every version pin stripped;
             before→after held per candidate in the phase-2 triage.
Rejected:    internal/proprietary pages; a plant's own seed-dev WIP (circular);
             kernel/agent duplicates; narrow single-plant candidates deferred.
Integrity:   agnosticism scan PASS (no plant/domain/org/path/IP token in any
             changed file); durability scan PASS (no version pin, no CVE);
             agent-lint --lint PASS (23 agents); seed tests PASS (4/4);
             graph-lint regression PASS (5/5); clean dry-run --copy install into a
             scratch target PASS (additive, pristine copy). Version: 4.8.0 → 4.9.0.
```

## 4.8.0 — Copy-by-default install; total project-agnosticism (2026-07-16)

A post-harvest integrity pass over the 4.x line with two aims: stop plant edits
from writing back into the seed, and enforce that the seed carries **no reference
to any specific project whatsoever**.

Two contamination vectors were found and closed. First, an install default that
**symlinked** a plant's `.claude/` files and kernel into the seed, so any plant
edit to a shared agent/protocol/command mutated the seed. Second — and more
serious — a full sweep found project-identifying content that had reached the
seed from the projects it was authored and grown inside: a host application's
name and absolute install path, an authoring fleet's internal
component/file/config names narrated as "this project's X", stack fingerprints
and an identifying count in the harvest logs, and one concrete dependency version
pin. All of it is now purged and generalized; the lessons are kept, the project
identities are gone.

### Changed (install)

- **`install.sh` now defaults to `--copy` on every platform** (was: symlink on
  macOS/Linux, copy on Windows). A plant gets its own independent files and can
  customize placed agents/protocols/commands without mutating the shared seed;
  `--symlink` is retained as an explicit opt-in for developers who *want* live
  seed links. Removed the now-dead `is_windows`/`resolve_link_mode` auto-mode
  machinery (copy is the universal default). `--copy` still accepted explicitly.
- **`INSTALL.md`:** rewrote the mode table and the prerequisites/upgrading notes
  around copy-as-default; symlink is documented as the opt-in with its
  write-back caveat.

### Purged (project-agnosticism)

- **`agents/multi-agent-architect.md`:** recast ~16 catalog exemplars and
  anti-patterns that narrated a specific authoring fleet's internals (named
  source files, plugins, config keys, and a dependency version pin) into generic
  patterns. The design wisdom is unchanged; the project identity is gone.
- **`docs/plans/agent-routing-and-delegation.md`:** replaced a host
  application's name and the absolute `/root/…` install path with generic
  "host application" / relative references; the seed's own agent-router design
  record is otherwise intact.
- **`tests/test_agent_lint.py`:** replaced the hardcoded absolute repo path with
  paths derived from the test file's own location — portable and project-agnostic.
- **`CHANGELOG.md`:** generalized every source-plant descriptor in the 4.5.0 /
  4.7.0 harvest logs (stack fingerprints, an identifying page count, and
  internal-component / secret descriptions) to "a grown plant" and generic
  categories.

### Doctrine (harvest protocol)

- **`protocols/harvest.md` + `HARVEST_PROMPT.md`:** the agnosticism gate now
  explicitly binds **every committed byte, including the CHANGELOG entry, the
  harvest-log, and provenance notes**; it defines a "project reference" broadly
  (a name, a stack fingerprint, an identifying count, an internal-component name,
  a path, or an illustrative example framed as "this project's X"); and it splits
  harvest output into a plant-identifying **proposal** shown to the steward (never
  committed) versus an **agnostic seed-committed log**. This fixes the root cause:
  the old output-format template prescribed recording "from `<plant lineage id>`"
  and "generalized-from: `<plant surface>`" straight into the seed's CHANGELOG.

### Fixed

- **`CHANGELOG.md`:** restored the dropped `## 4.4.0 — The toolcraft rule` header.
  The entire 4.4.0 toolcraft release entry (including its own "version bump to
  4.4.0") had been orphaned under the 4.5.0 maven-harvest section — a body with
  no header. History now descends 4.7.0 → 4.0.0 with no gaps.

### Verified

- Seed test suite 4/4 PASS (`tests/run.sh`); `agent-lint --lint` and `--eval`
  (100%) PASS; `manifest.json` valid. Clean-scratch installs confirmed:
  `--copy` (now default) places 0 symlinks / all real files; `--symlink` opt-in
  still links correctly. Final agnosticism sweep across the whole seed: no
  specific-project name, stack fingerprint, internal-component name, absolute
  path, or dependency version pin remains.

## 4.7.0 — Second harvest: corpus completion + first doctrine fold-backs (2026-07-15)

A follow-up `harvest` on the same grown plant whose public library pages seeded
`library-corpus/` at 4.5.0. That first pass was
**corpus-only**; this one finishes the corpus sweep — folding in the `maven` pages
the first pass missed and refining two existing pages — and, for the first time,
lifts **doctrine and templates** out of a plant and back into the seed's agents,
skills, protocols, and templates. Every fold-back cleared both gates
(agnosticism + durability); no plant name, domain noun, path, credential, host,
port, or version pin survived, and no rule that the kernel or an agent already
teaches was duplicated.

### New (library-corpus, maven)

- **`library-corpus/maven/querydsl.md`:** type-safe JVM-persistence query
  framework; a build-time `Q`-class metamodel generated by an annotation
  processor. Durable pitfalls — looks unused but is load-bearing through a generic
  predicate repository; codegen-before-compile ordering and processor conflicts;
  BOM-governed version drift that forces metamodel regeneration.
- **`library-corpus/maven/mapstruct.md`:** compile-time bean mapper; `@Mapper`
  interfaces with a one-mapper-per-entity DTO boundary. Durable pitfall —
  annotation-processor **order** is load-bearing when paired with an
  accessor-generating processor; without the binding the mapper silently emits
  null output.
- **`library-corpus/maven/springfox.md`:** the legacy Swagger-2-era API-doc
  generator for a JVM web framework, superseded by an OpenAPI-3 generator
  (cross-links `springdoc-openapi.md`). Recognize the legacy tool on sight and
  verify the real migration state — half-staged migrations are common.

### Changed (corpus refinements)

- **`library-corpus/language/angular.md`:** new pitfall — a web-framework package
  family's peer-dependency misalignment can be masked by an installer's
  legacy-peer-deps escape hatch; verify family alignment explicitly rather than
  trusting a clean install.
- **`library-corpus/npm/stomp-sockjs.md`:** new pitfall — a JWT-decode library's
  export shape can flip (default vs named) across majors; check the installed
  major before importing.

### New (doctrine & authoring guidance — the first non-corpus harvest)

- **`agents/05-security.md` — "Secure defaults you enforce":** the base/default
  config fails closed (debug/attach interfaces are opt-in, never present in the
  default artifact); the layer terminating a public handshake owns origin and auth
  and never assumes an upstream layer did it; the presence of a security control
  is not its enforcement — verify the wiring.
- **`agents/06-reliability.md`:** dev/local configuration defaults to a
  local/sandboxed backend; reaching shared or live infrastructure is an explicit
  opt-in, never the default.
- **`skills/holistic-editing/SKILL.md`:** detection cue — a dangling import to a
  deleted or commented-out definition is a half-removed-feature signature to
  finish, not to preserve.
- **`skills/adopt-existing/SKILL.md`:** record a codebase's non-English identifier
  language as a graph fact during adoption; the librarian pass must emit explicit
  `absent (date) — reason` gate rows when zero test infrastructure is found.
- **`protocols/verify.md`:** a blank verification runbook is not an acceptable
  resting state; adoption records each gate explicitly as absent rather than
  leaving it unstated.
- **`templates/agent.template.md`:** a recommended body order for code-owning
  experts that mirrors the node schema (including a distinct "Where the code is"
  section); a named "Neighbours & scope boundary" section for expert
  constellations; and restate-and-cite (never fork) to preserve one-home-per-fact.

### Rejected (stayed in the plant)

- The plant's internal/proprietary library pages (no agnostic public surface) and
  a standalone jwt-decode page (too thin to stand alone — its one durable lesson
  was folded into `stomp-sockjs.md` instead).
- Prevention-rule candidates the kernel or an agent already teaches:
  secrets-in-config, module-self-description drift, long-lived V1/V2 duplication,
  and generic scope hygiene.
- Two borderline rules dropped to keep the seed lean: per-profile external
  reachability, and CI-image-vs-manifest drift.
- The plant's plan/verify/tools side: no delivered increment existed, so there was
  nothing mature to harvest there.

### Harvest log

```
# Harvest — from a grown plant — 2026-07-15
Harvested:   3 maven corpus pages (first-pass gap); 2 corpus refinements
             (angular, stomp-sockjs); 6 doctrine/template fold-backs
             (security, reliability, holistic-editing, adopt-existing, verify,
             agent.template) — the first non-corpus harvest into the seed.
Generalized: every plant name/domain/path/credential/host/port and every version
             pin stripped; before→after held per candidate in the phase-2 triage.
Rejected:    internal/proprietary pages; a too-thin jwt-decode page; kernel/agent
             duplicates; 2 lean-cut borderline rules; the immature plan/verify side.
Integrity:   agnosticism scan PASS (no plant/domain/org token in any changed file);
             agent-lint --lint PASS (23 agents); seed tests PASS (4/4);
             clean dry-run --copy install into a scratch target PASS (additive);
             version scan PASS (no pins). Version: 4.6.0 → 4.7.0.
```

## 4.6.0 — `graft`: distributing the harvest to existing plants (2026-07-14)

Harvest gave the seed a way to draw one plant's generalizable lessons *up into*
itself. It had no way to push those lessons *back out* to the plants that were
grown before the seed learned them — so a harvest enriched the seed and every
*future* plant, while the siblings that already existed silently fell behind.
`graft` closes that gap. It is the **distribution arm** of the cross-project
loop and the outward complement of harvest: harvest collects (plant → seed),
graft distributes (seed → existing plant). Together they let one plant's
harvested fruit reach all the others.

The metaphor is exact: you do not uproot an established, fruiting plant to give
it a better cultivar — you graft the new scion onto the living rootstock. The
rootstock here is the plant's own life (its source and the `docs/graph/` facts it
authored) and it is inviolate; the scion is the seed's evolved machinery and its
enriched library/tool corpus.

### New

- **`protocols/graft.md` — the protocol.** Mirrors `harvest.md` in shape and
  rigour. Its heart is the **rootstock line** (the mirror of harvest's
  agnosticism gate): graft writes only seed-owned machinery and the deliberately
  refreshed library/tool *surface*, and leaves everything the plant authored
  about itself exactly as the plant left it. Machinery is upgraded by a
  **three-way reconciliation** (base = the seed the plant grew from; theirs = the
  seed today; ours = the plant now): FAST-FORWARD adopts what advanced on a
  pristine artifact, KEEP-PLANT preserves the plant's own divergence and raises it
  as a *harvest candidate*, MERGE re-integrates a true conflict holistically for
  the steward. Six phases (locate & establish base → survey drift → reconcile
  machinery → refresh knowledge from the corpus → apply/verify/stamp → deliver),
  strict Sonnet-survey / Opus-author model policy, a fail-closed integrity gate,
  an output format, a quality bar, and an out-of-scope section.
- **`GRAFT_PROMPT.md` — the tool-neutral standalone entry**, mirroring
  `HARVEST_PROMPT.md`: paste it into an agent-capable chat with an existing plant
  as scope to run a graft end to end.
- **A plant-owned seed stamp** (`.cypress/seed.json` or equivalent) that records
  which seed version a plant carries, so every future graft has a real *base* for
  its three-way merge. The first graft of a pre-stamp plant reconstructs the base
  from install backups / content lineage and establishes the stamp going forward.

### Changed

- **`manifest.json`:** registered the `graft` protocol; version bump 4.5.0 →
  4.6.0.
- **`core/AGENTS.md`:** protocol-table row for `graft`, and a meta-loop paragraph
  placing graft as harvest's outward complement (harvest fills the corpus, graft
  withdraws from it into an existing plant); §5 reference pointer added.
- **`README.md`:** listed `graft` among the protocols, extended the "reverse
  loop" section to "canonize + harvest + graft", and pointed "Updating the seed"
  at graft for a principled, reconciled upgrade of an existing plant.

### Notes

- `graft` is **user-decided, never automatic** — the same sovereignty harvest
  carries, for the same reason: it changes an established, possibly production
  plant. The most the system does unprompted is *propose* a graft, most naturally
  as the tail of a harvest, and stop. Every upgrade is additive, backed up, and
  reversible, and the steward ratifies the reconciled result before it lands.
- `install.sh` places `protocols/*.md` wholesale, so `graft.md` reaches every
  newly installed and re-installed plant with no installer change;
  `GRAFT_PROMPT.md` stays seed-side as the standalone entry, exactly as
  `HARVEST_PROMPT.md` does.

## 4.5.0 — First library-corpus harvest: the `maven` ecosystem (2026-07-14)

The first `harvest` run to fold a grown plant's `ingest-library` output back into
the seed's `library-corpus/`. A grown plant had authored a set of library wiki
pages during its growth; harvest lifted the
**version-durable, project-agnostic surface** of the public ones into the seed so
the next plant's `ingest-library` starts from an orientation instead of a blank
page, then fetches only the pinned delta fresh. Every fold-back passed both
gates (agnosticism + durability): no plant name, domain noun, path, credential,
host, port, or version pin survived.

### New

- **`library-corpus/maven/` — a brand-new ecosystem (13 pages):** `spring-boot`,
  `spring-cloud`, `spring-cloud-stream`, `spring-data-jpa`, `spring-data-mongodb`,
  `springdoc-openapi`, `sleuth-zipkin`, `resilience4j`, `rabbitmq`, `jjwt`,
  `freemarker`, `elasticsearch`, `stripe-java`. Each carries the enduring surface
  — capability, canonical Maven coordinates, stable API shape, cross-release
  idioms, and conceptual pitfalls (e.g. Spring Cloud release-train BOM alignment,
  Spring Data `Persistable` insert/update detection, `ddl-auto`/schemaless
  "no versioned schema history" risk, resilience "declared but dormant",
  prefer-abstraction-over-raw-AMQP-client, jjwt api/impl/jackson artifact-split
  lineage, FreeMarker render-time-only template errors, Elasticsearch
  client/server major lockstep, Stripe `Webhook.constructEvent` over hand-rolled
  verification).
- **`library-corpus/npm/bootstrap.md`, `library-corpus/npm/stomp-sockjs.md`:**
  Bootstrap (CDN-delivery + missing-SRI supply-chain pitfall); a combined
  client-side realtime stack page for `@stomp/stompjs` + `sockjs-client` +
  `@stomp/rx-stomp` + `jwt-decode` (legacy/scoped package duplication, stale
  wrapper dead code, decode≠verify).

### Changed

- **`library-corpus/language/angular.md`:** standalone bootstrap
  (`bootstrapApplication`, no root `NgModule`, `standalone: true`, Router-optional
  composition) woven into the existing functional-interceptor / SSR surface.
- **`protocols/ingest-library.md`:** the one lesson salvaged from a **rejected**
  internal library — resolving a private/internal dependency needs private-registry
  credentials in the build environment; a credential-less fresh checkout or CI job
  looks like a broken build, not a missing secret. Generalized tool-neutrally
  across Maven/npm/PyPI/NuGet.

### Rejected (stayed in the plant)

- A plant's internal/proprietary library (private, not on any public
  registry): no agnostic public surface exists — a corpus page would be empty or
  leak org-internal facts. Only its generalized prevention rule was kept (above).
- All version pins, resolved versions, CVEs, per-release deprecations, migration
  diffs, ports, hosts, image tags, and any checked-in secrets found on the plant
  pages: pinned/ephemeral or secret — rediscovered per project by
  `ingest-library`, never seeded.

### Harvest log

```
# Harvest — from a grown plant — 2026-07-14
Harvested:   13 maven + 2 npm corpus pages; 1 angular merge; 1 ingest-library rule.
Generalized: every plant name/domain/path/credential/host/port and every version
             pin stripped; before→after held per candidate in the phase-2 triage.
Rejected:    1 internal library (non-agnostic); all pinned/secret specifics.
Integrity:   agnosticism scan PASS (grep for plant/domain/org tokens = 0);
             durability scan PASS (no version-like token in any new page);
             seed tests PASS (4/4 via tests/run.sh); clean dry-run install PASS
             (additive; seed unmodified).
Version:     4.4.0 → 4.5.0.
```

## 4.4.0 — The toolcraft rule: durable tools compound (2026-07-14)

A new operating doctrine: when an operation will recur across independent
sessions, agents build a **durable, tested, reusable tool** rather than an
ad-hoc script they discard and the next session reinvents. At task end the tool
is handed to the librarian and catalogued, so capabilities compound the way
knowledge and specs already do. It is the tool-analog of `canonize`.

### New

- **Operating principle §16 — "Build tools to last, not to discard"**
  (`core/operating-principles.md`): the why. Recurrence across sessions, not
  size, is the trigger; reconciles with the throwaway-prototype carve-out (§3.4).
- **Kernel rule §3.8 — the toolcraft rule** (`core/AGENTS.md`): "The seven rules"
  becomes **"The eight rules"**. Fail-closed: a task is not complete until any
  durable tool it produced is catalogued in `docs/graph/tools/`, or the librarian
  recorded there was none. Adds a §4 boundary, a §5 pointer, the §2 lifecycle
  (`verify → canonize → toolcraft → deliver`), and a protocol-table row.
- **`protocols/toolcraft.md`**: the capture protocol, mirroring `canonize.md`
  (when to invoke, what counts as a durable tool vs. a throwaway, the librarian
  handoff, fail-closed doctrine, relationships to canonize/deliver/harvest).
- **`docs/graph/tools/` leaf**: `templates/tool-page.template.md` (one card per
  tool: interface, invocation, code location, tests) and a `tools/index.md`
  registry in the docs skeleton. Reached via the generic `artifacts:` edge — no
  `graph-lint.py` change needed; `tools` added to the Tier-3 list in `_schema.md`.
- **Seed-level `tool-corpus/`** mirroring `library-corpus/`: project-agnostic,
  durable tools promoted via `harvest` under the existing agnosticism + durability
  gates, with a withdraw contract for the next plant.

### Updated

- `templates/prompts/handback-payload.md` gains a `tools_built:` line feeding
  `toolcraft`.
- `agents/09-docs-librarian.md` owns `docs/graph/tools/`, gains a routing trigger
  ("catalog a reusable tool the work produced") and a tool-catalog audit.
- Echoes in `agents/02-implementer.md` (reuse before rebuild; catalog durable
  tools), `agents/06-reliability.md` (scripted bring-up steps that recur are
  tools), and the design-time decision gate in `protocols/grill.md`.
- `protocols/harvest.md` surveys and promotes the plant's `docs/graph/tools/`
  into `tool-corpus/`.
- `manifest.json`: registered the protocol, the template, a new principle line,
  the librarian and harvest role lines; version bump to 4.4.0.
- Golden routing rows added to `agents/_routes.golden.tsv` and
  `tests/agent_router/routes.golden.tsv`.
- Fixed a pre-existing drift: `agents/00-orchestrator.md` said it enforced "the
  six rules" and omitted canonize; it now names all eight in dependency order.

## 4.3.0 — Renamed to CYPRESS (2026-07-14)

The project is renamed to **CYPRESS — the Contextual Yield Protocol for Routed
Expert Seed Systems**. The name is a backronym: the seed still grows and routes
expert teams over a project's knowledge graph exactly as before; only the
branding changes. No behavior, protocol, or contract is affected.

- Prose branding "Expert Seed System" → "CYPRESS" across the kernel, install
  prompts, integration configs, skills, and agent descriptions.
- The seed directory and its path slug `expert-seed-system/` → `cypress/`,
  updated in the `manifest.json` name, integration READMEs, `agent-lint.py`
  banners, the routing/delegation plan, and the agent-lint test paths.
- `manifest.json` gains a `fullName` field and a version bump to 4.3.0.
- Historical changelog entries below are left intact — they record the names
  releases carried at the time.
- The `seed-installer` routing trigger keyword "install the expert seed system
  …" is retained: the backronym still contains "Expert Seed Systems," so the
  phrase remains a valid, test-golden matcher.

## 4.2.0 — The reverse loop: canonize + harvest (2026-07-14)

Closes the lifecycle so the seed compounds. Two new protocols plus a seventh
kernel rule turn a one-way seed→plant flow into a loop where every task feeds
the plant's graph and every mature plant feeds the seed.

### New: the `canonize` rule (kernel §3.7) and protocol

- `protocols/canonize.md` — doctrine that a task is **not complete** until the
  librarian has persisted its knowledge of interest (new/changed facts, sharp
  edges, corrected assumptions, provenance, failed `load_when:` triggers) into
  `docs/graph/`, or explicitly recorded there was none. Runs before `deliver`.
  Added as kernel rule §3.7 ("The seven rules") with a matching §4 boundary, so
  it is doctrine in the seed and in every plant grown from it.

### New: the `harvest` protocol — the inverse of `grow`

- `protocols/harvest.md` — once a plant is mature, fold its **project-agnostic**
  lessons (tooling fixes with generalized tests, sharpened skill rules, protocol
  gaps, new experts, template improvements, generalized prevention rules) back
  into the seed, gated by a hard **agnosticism** test: a lesson lands only if it
  helps an arbitrary next project, generalized until no plant name/domain/stack
  remains. Harvest is **user-triggered only — never automatic** (no schedule, no
  hook, no tail-end step); the system may at most *propose* a harvest and stop.
  It **proposes for human ratification** and never silently mutates the seed —
  nothing lands until the user is satisfied with the growth.
- **Library & language documentation corpus.** Harvest also folds the plant's
  version-pinned library/language wiki pages into a seed-side corpus
  (`library-corpus/<ecosystem>/<library>@<version>.md`). `ingest-library`
  withdraws from it first — reusing/refreshing a current page instead of
  re-downloading and re-authoring — so the next plant pays only for the delta.
- Standalone portable entry `HARVEST_PROMPT.md` runs the harvest against any
  project grown from the seed and emits a reviewable seed-improvement proposal.

### New: growth-specialized agents (the seed's growth DNA)

Growth used to spawn generic scouts. Three purpose-built experts now guide it,
authored from `templates/agent.template.md` and validated by `agent-lint`
(delegation graph valid; each routes HIGH from its triggers):

- `agents/growth-orchestrator.md` — Opus delegator (depth 2) that conducts
  grow/adopt/from-scratch: detect project shape, dispatch scouts by real
  boundary, sequence authoring from the evidence ledgers, gate on knowledge
  validation. Added to the orchestrator's `delegates_to`.
- `agents/growth-scout.md` — Sonnet read-only leaf; the per-boundary
  executable-evidence gatherer (internal-source analog of `research-scout`) that
  returns claims tied to paths/symbols for the authors.
- `agents/seed-installer.md` — Opus leaf; additive seed/adapter install that
  preserves target-owned files and verifies the host tool loads the kernel.

Registered in `manifest.json` and the kernel §1 roster; golden routing rows added
to `agents/_routes.golden.tsv`.

## 4.1.0 — Mechanical agent-router and bounded delegation (2026-07-13)

Mechanizes the *expensive* routing decision (which expert does the work) the way
the knowledge router already mechanized the cheap one (which docs to read), and
replaces the flat-by-tool-grant topology with a small, depth-capped set of
delegators. Decisions recorded as `docs/decisions/adr-0001..0003`; plan-of-record
at `docs/plans/agent-routing-and-delegation.md`. Reviewer verdict SHIP-WITH-MINORS
(1 Major + Minors, all fixed).

### New: the mechanical agent-router (`agent-lint.py`)

- `integrations/claude-code/agent-lint.py` (installed to `.claude/agent-lint.py`)
  — the specialist-selection analog of `graph-lint.py --plan`. `--route "<task>"`
  ranks specialists by an IDF-weighted match against each agent's new
  `routing_triggers` frontmatter and prints a confidence band
  (HIGH/MEDIUM/LOW/NONE) to cite in the delegation brief. `--lint` validates the
  routing/delegation frontmatter (the P0/P1 gate); `--eval` runs the golden
  routing set and asserts top-1 accuracy + novel-stack LOW/NONE.
- `agents/_routes.golden.tsv` (installed to `.claude/agents/`) — the golden
  routing set backing `--eval` (100% top-1, 33/33 at ship).
- `install.sh` now copies both the router and its golden set into a claude-code
  install (fixing a Major where the installer shipped the router dead).

### New: routing + delegation frontmatter on all 13 agents

- Added `routing_triggers` (the agent analog of a node's `load_when:`) and
  `can_delegate` to every agent. `agent-lint.py --lint` enforces
  `can_delegate == (Task ∈ tools)` so a config field can never imply a capability
  the harness doesn't grant.
- **Bounded delegation:** 5 coordinators carry a depth-capped `Task`
  (orchestrator 3; multi-agent-architect 2; architect/reviewer/docs-librarian 1)
  with `delegates_to` allowlists under a strictly-decreasing-depth invariant; the
  8 leaf workers stay Task-less (the one hard recursion cap). Reconciled the prose
  that said "delegate to peer X" without a tool to back it.

### New: handback payload + deliver-time attribution

- `templates/prompts/handback-payload.md` — the standard HANDBACK block every
  specialist ends its turn with; the reliable carrier across the subagent
  boundary (where hooks do not reach).
- `.protocols/deliver.md` gains a fail-closed `produced_by` routing-attribution
  assertion (missing attribution → BLOCK). The optional top-session `Stop` hook
  is deliberately left unwired (green-lie discipline) — a deferred warn→block
  follow-up.
- The three delegation brief templates now require `--route` evidence and a
  handback payload.

## 4.0.0 — Tool-neutral growth and one unified knowledge graph (2026-07-12)

- Adds `INSTALL_PROMPT.md` as the primary install-and-grow interface and
  installs it into targets as `EXPERT_SEED_INSTALL_PROMPT.md`.
- Adds canonical `grow`; reduces `/initialize` to a coding-tool adapter.
- Makes user chat a strict orchestration/planning plane: it always spawns
  clean-context workers, routes read-only scouting to Sonnet-class models,
  and routes all authoring, code, deep analysis, review, and validation to
  Opus-class models. Persona simulation is no longer an accepted fallback.
- Applies the executable graph router inside every spawned session. Worker
  returns must include the exact `--plan` command/output, loaded closure,
  deliberate skips, and widening; pre-node bootstrap probes fail visibly.
- Unifies progressive discovery, fact-owning graph nodes, provenance, and
  LLM-wiki depth beneath `docs/graph/`; all detailed leaves connect through
  `artifacts:` or `libraries:` edges.
- Refactors installation to add missing unified-graph scaffold/leaves without
  overwriting target-owned graph files. No legacy knowledge trees are created.
- Refactors existing-project growth into source-first Scout/Librarian passes;
  centralized prose is evidence only, never a trust root.
- Adds regression coverage for installed graph shape, legacy paths,
  orchestration/model policy, additive preservation, artifact edge resolution,
  every supported adapter, frontmatter, and generated-view drift.

## 3.1.0 — Delegation doctrine: the session orchestrates, experts do the work

Codifies a single operating rule the deployment kept re-learning: the
host chat session never does the work with its own hands. It plans,
routes, verifies, and talks to the user; every piece of doing —
investigating a subsystem, authoring a spec, test, code, or doc — is
delegated to a clean-context expert subagent. Investigation routes to
sonnet-class experts; authoring and judgment-heavy design route to
opus-class experts. If no expert matches, the session builds one first
— the library of experts compounds.

### New: the delegation doctrine in the kernel

- Kernel §0 (Operating identity): the host session **is** the
  orchestrator and only the orchestrator; its "unit of work" is now a
  *delegated, verified* change, not one it authored itself. Carve-outs:
  FIRST-MOVE routing, one-line/trivial edits, answering from
  already-loaded context.
- Kernel §1 (The team): adds the **model-class routing rule** (sonnet →
  read-only investigation; opus → authoring and judgment-heavy design)
  and generalizes the stack-expert-on-demand pattern to **all** missing
  experts — author one from the new template first, then delegate.
- Kernel §4 (Boundaries): adds "You do not do the work in the main
  session" and "You do not delegate without the graph discipline in the
  brief" (the route-hook does not reach subagents, so the brief is the
  only enforcement).
- Kernel §5 points at `templates/agent.template.md`.

### New: agent-authoring template

- `templates/agent.template.md` — authors a new specialist/expert: the
  exact four-key frontmatter (`name`, `description`, `tools`, `model`),
  per-key guidance (model: sonnet for investigation-only, opus for
  anything that authors), and the house body shape (identity paragraph,
  when-to-invoke, graph-discipline load-first block, discipline
  sections, what-you-do-not-do). Referenced from kernel §5 and the
  orchestrator.

### Updated: orchestrator delegation mechanics

- `agents/00-orchestrator.md` — "Specialist routing" now delegates in a
  **clean context**, routes by **model class**, and codifies
  **create-missing-expert-first**. The delegation-brief section replaces
  the vague "match the model to the work" line with the sonnet/opus tier
  rule and makes the brief **mandatory**: it must carry the model class,
  the deliverable, the **graph discipline stated verbatim** (because no
  hook reaches subagents), the contract, and the gates + where to record.
  "What you do not do" tightened accordingly; a routing example for the
  no-expert-fits case added.

### Changed: model tiers aligned to the doctrine

- Agents that author flip to `model: opus`: `agents/02-implementer.md`,
  `agents/04-tester.md`, `agents/09-docs-librarian.md`. Investigation-only
  `agents/10-research-scout.md` stays `sonnet`; `agents/03-reviewer.md`
  stays `opus` (judgment). (Stack experts are domain-generated under the
  host tool's agent dir, not in `expert-seed-system/agents/`; align them
  the same way when regenerated — opus for the authoring ones.)

### Updated: delegation-brief templates

- `templates/prompts/investigation-brief.md` (sonnet),
  `node-authoring-brief.md` (opus), and
  `clean-context-validation-brief.md` (opus) each now state their target
  model class and embed the progressive-discovery / graph instruction
  verbatim, since the route-hook does not fire for subagents.

## 3.0.0 — Progressive-discovery knowledge graph + holistic editing

Backport of lessons from a large multi-repo deployment, generalized.
The seed now scales from a single repo to a program of several without
privileging either, and treats the project's knowledge as a routed,
deduplicated graph rather than a flat docs tree.

### New: the knowledge graph (source of truth for structure & capability)

- `skills/knowledge-graph/SKILL.md` — build/maintain tiered nodes under
  `docs/graph/`; **one home per fact**; honest per-node budgets;
  cite-don't-fabricate. The library wiki becomes the graph's **leaf
  tier**, not a separate system.
- `skills/context-router/SKILL.md` — resolve the *minimal* node set a
  task needs (entry nodes + required closure), **declare what you loaded
  and deliberately skipped**, and never bulk-read a subsystem to
  orient. Includes the "`--plan` is a heuristic, not an oracle" caveat.
- `templates/knowledge-graph/` — `_schema.md` (node contract),
  `graph-lint.py` (a dependency-free enforcer: unique fact-keys,
  resolvable/acyclic edges, reachability, no version-pin leakage, token
  budgets; with an IDF-weighted `--plan` router dry-run), `index.md`
  (router), `node.template.md`. The installer scaffolds these into
  `docs/graph/`.
- Kernel §3.2 (was the "wiki rule") generalized to the **knowledge
  rule**: load minimally and declare it; one home per fact; read the
  graph ahead of memory.

### New: holistic editing (integrate, don't bolt on)

- `skills/holistic-editing/SKILL.md` — the unit of work is the whole
  file; no appended functions, `_v2` wrappers, or special-case branches
  around logic that should itself change; delete and consolidate;
  additive-only diffs are a red flag. Explicitly **exempts append-only
  artifacts** (grill.md history, ADRs, changelogs).
- Reconciled the "smallest change" framing in `core/operating-principles.md`,
  `protocols/test-first.md`, and `agents/02-implementer.md`: "minimum"
  governs *new behavior*, integrated — REFACTOR is mandatory when you
  touched existing code. `agents/03-reviewer.md` gains an
  integration-coherence checklist.

### New: characterization-first, honest gates, knowledge validation

- `protocols/test-first.md` — on untested existing code, the first move
  is a **characterization test** that pins current behavior before any
  change.
- `protocols/verify.md` — a gate that runs but asserts nothing is a
  **green lie**; don't add a CI gate in the same increment as the first
  thing it checks. Adds a graph-lint gate.
- `skills/validate-knowledge/SKILL.md` — prove the graph works with
  clean-context test agents (known-answer + adversarial false-premise
  questions) and enforcement tests (plant a violation, confirm the catch).

### New: roster and delegation

- `agents/11-pentest.md` — hands-on authorized penetration testing with
  an explicit scope gate and a reproduce → fix → re-verify loop.
- `agents/07-data-ml.md` broadened to own **synthetic/example data**,
  with a hard **no-production-data** rule (also kernel §4, a genuine
  gap before).
- `agents/06-reliability.md` sharpened to own **bring-up from scratch**,
  not only documenting an existing pipeline.
- `agents/00-orchestrator.md` gains a delegation-brief method
  (deliverable, context to load, contract, "facts only / cite paths /
  say not-found", capable-model authoring) and the
  **stack-expert-from-detected-stack** pattern; `templates/prompts/`
  ships parameterized delegation briefs.
- `agents/09-docs-librarian.md` now owns the graph and enforces the
  dedup rule + graph lint.

### New: enforced progressive discovery via cross-tool Agent Hooks

- **`route-hook.py`** + a `UserPromptSubmit` hook — on every prompt,
  runs the graph router and *injects* the route-first mandate plus the
  suggested node set as `hookSpecificOutput.additionalContext`.
  Deterministic enforcement, independent of how well the model follows
  prose. **It works in both Claude Code and VS Code Copilot (Agent
  Hooks, Preview):** both read `.claude/settings.json` hooks and both
  accept the JSON `additionalContext` output. The hook emits JSON
  (plain text is not injected by Copilot) and uses a relative command
  path (not the Claude-only `$CLAUDE_PROJECT_DIR`) so it resolves in
  both. The linter is located by walking up, so one script works at any
  install depth.
- The claude-code install drops it to `.claude/`; a Copilot-only install
  drops `.github/hooks/route.json` + `route-hook.py` (VS Code's native
  location), guarded so it never coexists with the `.claude/` hook and
  fire twice.
- Both kernels open with a blunt, tool-free **"FIRST MOVE"** banner
  (open the router, load 2–3 nodes, declare skips) so even with hooks
  off, the route-first instruction is the first thing the model reads.
- `integrations/github-copilot/README.md` documents enabling Agent
  Hooks and the weak-model reality (the hook guarantees the context is
  present; a capable model and a fresh, un-stuffed chat still help).

### New: multi-tool drift gate & scale-agnostic adoption

- `install.sh --check` verifies the generated Copilot `.github/` views
  are in sync (CI drift gate); generated files carry a "do not edit"
  banner.
- `initialize`/`from-scratch`/`adopt-existing` reworded to handle **one
  repo or a program of several**, with the graph as the central
  adoption artifact — validated before finishing.

## 2.1.0 — `initialize` universal entry protocol

### New: `initialize` protocol

`protocols/initialize.md` is the new universal entry point. It
detects whether a project is new (empty repo) or existing (code
already present) and dispatches accordingly:

- New → `from-scratch` protocol (existing, unchanged).
- Existing → new `adopt-existing` skill.

Initialize is the only protocol that can be safely run blind in any
repo: it is read-only during detection and asks for explicit user
confirmation before any write. The orchestrator's decision tree
puts initialize at the top, so it runs first in any project where
no `docs/graph/plans/grill.md` exists yet.

### New: `adopt-existing` skill

`skills/adopt-existing/SKILL.md` adopts an existing codebase
additively and safely:

- Reads the project (ecosystem detection, test/lint/CI signals,
  dependency inventory, docs state, competing AI configs).
- Writes ONLY the additive seed artifacts that are missing:
  `docs/graph/plans/grill.md` (§1 populated from discovery, §9 seeded
  with the adoption backfill plan), `docs/graph/runbooks/verification.md`
  (gate commands lifted from CI / manifests), `docs/graph/libraries/index.md`
  (every direct dependency listed with status `pending wikification`),
  `docs/graph/sources/index.md`.
- Optionally drafts `docs/graph/product/requirements.md` from README
  clues, clearly marked DRAFT.
- Never overwrites existing files.
- Never fabricates specs for code it doesn't understand.
- Wikifies lazily — dependencies are listed but only wikified
  when the next change touches them.
- Never modifies code, tests, CI, or competing AI configs.
- Documents pre-existing test failures in grill.md §12 without
  fixing them in the adoption session.

### New: slash command

Both `/initialize` slash commands ship for Claude Code and
opencode (`integrations/{claude-code,opencode}/commands/initialize.md`).
The installer auto-generates the Copilot prompt-file equivalent
(`.github/prompts/initialize.prompt.md`).

### New: Codex skill registration

`integrations/codex/config.toml.example` now registers the
`adopt-existing` skill alongside the eight existing ones.

### Updated: orchestrator routing

`agents/00-orchestrator.md` decision tree now has `initialize`
as the first node — "Has this project been initialized?" — before
the "is the project new?" branch.

### Updated: kernel pointers

`core/AGENTS.md` §2 (protocols table) and §5 (entry points) both
point at `initialize` as the universal first step.

### Updated: installer post-install message

`install.sh` now prints a clear "next step: run /initialize"
message after a successful install.

### Files added (4)

- `protocols/initialize.md`
- `skills/adopt-existing/SKILL.md`
- `integrations/claude-code/commands/initialize.md`
- `integrations/opencode/commands/initialize.md`

## 2.0.0 — Expert Seed System

Full redesign of the upstream `general_expert_prompts` archive into a
multi-agent seed system with turnkey integrations.

### New: spec-driven and test-driven foundations

- `protocols/specify.md` + `skills/spec-author/SKILL.md` — executable
  specs under `docs/graph/specs/SPEC-NNNN-*.md` with stable section
  numbers, three-way sign-off (product, architect, tester), and a
  testability review gate.
- `protocols/test-first.md` + `skills/test-first/SKILL.md` —
  RED-GREEN-REFACTOR-COMMIT discipline. Bug fixes start with a
  regression test. Tests name spec contracts.
- `templates/spec.template.md` — the executable-spec template.
- `agents/01-architect.md`, `agents/04-tester.md`, `agents/08-product.md`
  rewritten to be co-authors of every spec (sections §4/§6/§7, §10,
  §3/§9 respectively).

### New: multi-agent team

11 specialist agents, each with universal frontmatter:
- `orchestrator`, `architect`, `implementer`, `reviewer`, `tester`
- `security`, `reliability`, `data-ml`, `product`
- `docs-librarian`, `research-scout`

The orchestrator owns the decision tree (from-scratch / brainstorm /
specify / grill / test-first / question / trivial-shortcut).

### New: LLM-wiki for libraries

- `protocols/ingest-library.md` + `skills/library-wiki/SKILL.md` +
  `skills/research-and-ingest/SKILL.md` — `docs/graph/libraries/<name>.md`
  is the project-local source of truth for every dependency,
  version-pinned, with smoke-test validation.
- `templates/library-page.template.md` — wiki page structure.
- Native support for documentation MCP servers (Context7, DeepWiki)
  for fetching upstream content.

### New: named protocols

8 protocols, each with YAML frontmatter so they trigger as skills /
commands in host tools:
- `from-scratch` (9-phase project bootstrap)
- `brainstorm`, `specify`, `grill`, `test-first`,
  `ingest-library`, `verify`, `deliver`.

### New: per-tool integrations

- `integrations/claude-code/` — `.claude/` overlay, `settings.json`,
  slash commands.
- `integrations/opencode/` — `.opencode/` overlay, `opencode.json`,
  slash commands.
- `integrations/codex/` — `.codex/` overlay, `config.toml.example`
  with all skills registered.
- `integrations/github-copilot/` — `.github/` overlay with
  transformed frontmatter (Copilot conventions differ from the
  universal ones).
- `install.sh` — universal installer; symlinks by default, transforms
  for Copilot, prints Codex config snippet with resolved paths.

### New: populated docs skeleton

`templates/docs/` ships a complete starter docs tree (README,
specs/, libraries/, sources/, plans/, decisions/, runbooks/,
product/, etc.) that the installer drops into projects without an
existing `docs/`.

### Progressive disclosure applied throughout

Following Anthropic's SKILL.md format:
- Every agent, protocol, and skill has tight `name` + pushy
  `description` frontmatter (~100 words).
- Bodies are under 500 lines; longer reference material is
  bundled.
- Templates carry self-describing HTML-comment headers.

### Supersedes

- `general_expert_prompts/prompts/00-master-general-expert-programmer.md`
  → distributed across `core/AGENTS.md`, `agents/00-orchestrator.md`,
  `protocols/from-scratch.md`, `protocols/grill.md`.
- `general_expert_prompts/prompts/01-llm-vlm-systems-architect.md`
  → `agents/07-data-ml.md` (eval), `agents/01-architect.md` (AI
  boundary), `templates/prompt-contract.template.md`.
- `general_expert_prompts/prompts/02-security-privacy-...md`
  → `agents/05-security.md` + `templates/threat-model.template.md`.
- `general_expert_prompts/prompts/03-reliability-...md`
  → `agents/06-reliability.md`.
- `general_expert_prompts/prompts/04-data-ml-...md`
  → `agents/07-data-ml.md` + `templates/data-contract.template.md`.
- `general_expert_prompts/prompts/05-product-...md`
  → `agents/08-product.md`.
- `general_expert_prompts/prompts/06-documentation-...md`
  → `agents/09-docs-librarian.md` + `agents/10-research-scout.md`.
- `general_expert_prompts/templates/grill.template.md`
  → `templates/grill.template.md` (kept stable; section numbers
  match for tooling compatibility).
- `general_expert_prompts/docs-blueprints/docs-folder-blueprint.md`
  → `templates/docs/` (now populated, not just described).
- `general_expert_prompts/skill-synthesis/generalized-skill-patterns.md`
  → absorbed into `core/operating-principles.md` and the eight
  SKILL.md files.

## 1.0.0 — general_expert_prompts

Original archive: language-agnostic expert prompts as seed prompts.
