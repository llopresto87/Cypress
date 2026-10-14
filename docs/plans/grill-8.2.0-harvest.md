# grill.md: Plan of Record: round 8.2.0, a harvest

## 0. Metadata
- Project: CYPRESS seed
- Feature or goal: fold back into the seed what a harvest found: defects reported against the seed, the friction a graft or a harvest met, the doctrine and procedures worth keeping, and the library, tool, skill and legal knowledge plants had to write for themselves; and recast the identifying tokens a previous release shipped
- Date: 2026-10-14
- Owner: the steward
- Tier: T3. Protocol: `protocol.harvest` (what to fold back, and the owner's decisions), then `protocol.grill` for the increments; this plan is the record of what landed and why
- Current phase: every increment is done, the tip included; the release pass (`docs/skills/seed-release.md`) follows this plan and is not an increment of it
- Related files: `install.sh`, `integrations/claude-code/route-hook.py`, `integrations/claude-code/settings.json`, `integrations/claude-code/agent-lint.py`, `integrations/prime-agent/route-extension.ts`, `integrations/prime-agent/status-extension.ts`, `.github/workflows/gate.yml`, `tools/corpus-match.py`, `tools/graft-audit.py`, `tools/session-metrics.py`, `tools/source-index.py`, `tools/plant_walk.py`, `tools/agnosticism-lint.py`, `tools/gate-registry.py`, `templates/knowledge-graph/spec-lint.py`, `templates/knowledge-graph/graph-lint.py`, `tests/run.sh`, `tests/seed-lint.py`, `protocols/graft.md`, `protocols/harvest.md`, `protocols/grow.md`, `core/method/delegation-wave-integrity.md`, `core/method/delegation-continuation.md`, `agents/*.md`, `library-corpus/`, `skill-corpus/`, `tool-corpus/`, `legal-corpus/`, `agent-corpus/iac-change-author.md`, `manifest.json`
- Related documentation: `docs/plans/grill-8.1.2-tool-surfacing.md` (the previous plan the gate linted, and the shape of its carried increment); `docs/plans/grill-8.0.0-wave-a.md` (the previous harvest round's plan); `docs/skills/seed-release.md` (the release pass that follows this plan)
- Related ADRs: [ADR-0031: a donor-identifying token is recast as a generic reference that keeps every fact, in every record, an ADR body included](../decisions/adr-0031-donor-tokens-recast-generically.md) (new, accepted 2026-10-14; it amends ADR-0011); ADR-0029 (its body recast under ADR-0031, with a dated section saying so); ADR-0023 (a declarative edit is proved by a run)
- Related specs: [SPEC-0001](../specs/SPEC-0001-install-placement.md) (six new contracts, increments 3 and 14); [SPEC-0002](../specs/SPEC-0002-routing-contract.md) (one, increment 4); [SPEC-0006](../specs/SPEC-0006-session-metrics.md) (one, increment 4); [SPEC-0007](../specs/SPEC-0007-source-index.md) (three, increment 4); [SPEC-0003](../specs/SPEC-0003-per-prompt-injection.md) (one new failure, the crashed router, increment 3) and [SPEC-0005](../specs/SPEC-0005-cycle-economy.md) (§5 becomes the Python floor's one home, increment 3), both amended in text with no new contract
- Related libraries: none (stdlib Python and bash; the library-corpus pages are content the seed carries, not dependencies of its code)
- Baseline: seed at `1f7385a` (the v8.1.2 release notes); the round lands as the 8.2.0 commit on top of it

## 1. Artifact Discovery
Every line cites the paths it rests on. Each owner decision is stated in words with its date.
- Existing files inspected: `git diff --stat 1f7385a` (the round's changes, 47 of them library-corpus pages); `install.sh` (`PYTHON_FLOOR`, the stamp writer and its owned keys, the backup report, `--kernel-mode`, `--expertise`); `templates/knowledge-graph/grill-lint.py` (`CONTRACT_DECL_RE`, the rule that every declared contract of a spec §9 names appears in some increment); `tools/graft-audit.py` (`--record`, the graft-entry heading match); `tools/source-index.py`; `tools/session-metrics.py`; `tools/plant_walk.py`; `tools/agnosticism-lint.py`; `integrations/claude-code/agent-lint.py` (`ADVERSARIAL_CONFIDENT_WRONG_BUDGET`, `--record-baseline`)
- Existing docs inspected: `docs/plans/grill-8.0.0-wave-a.md` and `docs/plans/grill-8.1.2-tool-surfacing.md` (shape, carried increment); `templates/grill.template.md`; `protocols/graft.md` (`graft.gate.routes`); `CLAUDE.md` (Conventions, the identifying-token exception as ADR-0031 amends it); `docs/decisions/adr-0031-donor-tokens-recast-generically.md`
- Existing tests inspected: `tests/run.sh` (`ACTIVE_PLAN`); the §10 rows of each new contract: `tests/test-full-install.sh` (E16 to E19), `tests/test-install-kernel-modes.sh` (K8), `tests/test-install-placement.sh` (M16, M21), `tests/test_agent_lint.py`, `tests/test_graph_lint.py`, `tests/test-session-metrics.sh` (X484), `tests/test-source-index.sh` (X481 to X483, X448), `tests/test-tool-help.sh`, `tests/test-prompt-hooks.sh` (X471)
- Existing specs inspected: `docs/specs/SPEC-0001-install-placement.md`, `SPEC-0002-routing-contract.md`, `SPEC-0003-per-prompt-injection.md`, `SPEC-0005-cycle-economy.md`, `SPEC-0006-session-metrics.md`, `SPEC-0007-source-index.md` (each one's `### Contract:` list at `1f7385a` and after the round, its §0 sign-offs, its §10 rows and its 2026-10-14 changelog entries)
- Existing architecture signals: `core/AGENTS.md` is at its budget and the round leaves it untouched; the version, the `CHANGELOG.md` entry and the documentation figures belong to `docs/skills/seed-release.md`
- Libraries already wikified: none, no library is a dependency of the seed's code
- External sources downloaded: upstream documentation and the legal publisher's texts, fetched for the corpus pages; each page cites its sources, and nothing fetched is a seed file except the pages written from it
- Constraints discovered: the kernel is at its budget (`tests/seed-lint.py`, `KERNEL_BUDGET`); a seed file names no project the seed was harvested from, checked by `tools/agnosticism-lint.py` against a forbid list kept outside the seed

## 2. Shared Understanding
A harvest reads plants read-only and proposes what the seed should learn from them; nothing reaches the seed before the owner ratifies it. This round folds back four kinds of finding: seed defects and protocol friction; doctrine and decision rules; corpus pages; and library pages.

The owner's decisions this round rests on, all of 2026-10-14:

| Decision | What it settles | Where it lands |
|---|---|---|
| holistic fold-back | every fold-back is an integration: comprehend the receiving file first, put the lesson where it belongs, sweep the ripple and the class, and leave the file reading as if the lesson had always been there, with no appended harvest section | every increment |
| the library pages | ratified as drafted and reviewed: 27 new pages, 16 rewritten, one correction, plus the back-links the review asked for | increment 2 |
| preview and release-candidate lines | a page for a library whose packages are in preview, or whose next major is a release candidate, lands now with that caveat stated on the page | increment 2 |
| vendor sub-processor citations | dropped | increment 2 |
| the Python floor | stays at 3.14, with one home; the installer finds an interpreter at the floor and writes it into every hook, or refuses with the fix | increment 3 |
| a crashed router | is named in one line in the session | increment 3 |
| the stamp and the baseline commit | the installer prints the `.gitignore` lines that keep the stamp tracked; graft makes the baseline commit itself | increments 3, 5 |
| backups | listed by date for the owner's retention call, with a stage-by-explicit-path line | increments 3, 5 |
| stale stamp keys | keys an earlier seed wrote are reported and kept | increment 3 |
| an existing instruction hub | compose mode is an opt-in installer and graft option; replace stays the default, and the cost is stated | increment 3 |
| generic skill pages | reach a plant by needs-driven placement: grow and graft identify what the plant's work needs, and `--expertise` places a generic page as a routable skill node | increments 3, 5, 6, 13 |
| the Graph SDK packages | trigger the Microsoft Graph platform page in the matcher; the Azure DevOps REST page stays unreachable by manifest | increment 3 |
| a comment-only slug | spec-lint reports it as a WARN, never as coverage | increment 4 |
| every agent's lookup tools | every agent, the shell-less ones included, runs the plant's routing and lookup tools read-only to load its own nodes and expertise; the scope is enforced by charter text | increments 7, 9, 10 |
| two axes | a project's own authorization levels and the seed's process tiers are two axes; the stricter wins and neither is translated; the seed's own `covered` and `contained` names are kept | increment 7 |
| operations-pass bugs | an operations or verification pass lists a bug, root-caused, and fixes it only on the owner's go-ahead; the seed's known-bug default stands | increments 6, 9 |
| owner working preferences | imported as doctrine: all of a spec's failing tests in one wave with mutation testing batched at the end; resume an agent only for a small change that needs its whole context or after a usage limit, otherwise brief fresh; numbered options with a recommendation at every decision point; split a batched call when it stalls or to localize a stall | increments 7, 9 |
| a demo password | lives on disk only, in a file no model reads; never in docs, plans, tests a model reads, or the seed | increment 11 |
| grow's checkpoints | grow commits a checkpoint per phase, and its write-scope gate compares each phase against that phase's own baseline (the owner left the choice open; a baseline per phase was chosen) | increment 6 |
| the throwaway review packet | imported and generalized into a report-producing procedure | increment 12 |
| identifying tokens in published records | a project name a published record carries is rewritten with a generic reference that keeps every fact, never a placeholder, an ADR body included; disclosed in the release CHANGELOG; no history rewrite, no force-push, no tag move | increment 16 |
| commit attribution | the round lands with no AI co-author line, as this repository's history does | the release pass |

Success means: each ratified row is in the seed in its one home, read as if it had always been there; every new contract is declared in its spec and green in its §10 row; `bash tests/run.sh` is green on the floor interpreter; and no seed file names a project the seed was harvested from.

Out of scope: the version bump, the `CHANGELOG.md` entry with the disclosure ADR-0031 requires, and the one documentation pass, which the release procedure writes after this plan; the reported defects the owner has not ruled (§12); the owner's longer list of working preferences, not yet sent.

## 3. User Goal
- Primary user: the owner growing or grafting a plant, and the sessions inside it
- Primary outcome: the reported defects stop recurring, and what one plant learned is available to the next from the seed
- Job to be done: install or graft a plant on a host whose `python3` is old, keep the stamp and the backups under control, keep a team's own instruction hub, place the procedures a plant needs, and route every agent to its own nodes
- Acceptance criteria (link to spec §9): the SPEC-0001, SPEC-0002, SPEC-0006 and SPEC-0007 rows the 2026-10-14 changelog entries add, each signed by product, architect and tester (increment 17)
- Non-goals: rewriting the seed's tools for interpreters below the floor; a reader per language in the source index; editing any plant

## 4. Operating Constraints
- Runtime constraints: bash 3.2 syntax in `install.sh`; stdlib Python at the 3.14 floor, whose one home is SPEC-0005 §5; no new dependency
- Security constraints: security findings land at the level of a defensive rule only; no credential value enters any seed file; the installer writes only under `--project-dir`
- Privacy constraints: no project name or project identity in any seed file, test or fixture; the tree lint runs against a forbid list kept outside the seed, SKIPPED where that list is absent; fixtures are synthetic
- Data constraints: `.cypress/seed.json` gains one installer-owned key, `kernel_mode`; keys an earlier seed wrote are named and kept; unknown keys still survive
- Cost constraints: the batch sizes of `delegation.effort-scale`; no two writers of one file in one wave
  - Plan approval (`grill.plan-approval`), skipped: the plan did not go to the owner before the work ran; the owner ratified each finding row by row and ruled each question on 2026-10-14, and this plan records that work. Levers this plan uses: none defined (default)
  - Owner-only prerequisites: the release and its tag push wait for the owner's explicit go-ahead (`vcs-posture.publish-authorization`)
  - Scoped standing grant: none asked
- Latency constraints: none
- Compliance constraints: legal pages are citations from the publisher's text, never a plant's application of them
- Maintenance constraints: one home per fact; seed text states each owner decision in words with its date; human-facing prose passes prose-lint; the release documentation pass happens once

## 5. Research Summary
no external dependency — the seed's code gains no library; the library, tool, skill and legal pages are corpus content, each researched from upstream sources its own page cites, and no §9 row depends on a `docs/graph/libraries/` page.

## 6. Decisions Made
| Decision | Rationale | Evidence | Reversibility | ADR | Date |
|---|---|---|---|---|---|
| Tier T3 | the installer, four tools, five specs, three protocols, the method leaves and every corpus | kernel §0 | not applicable | none | 2026-10-14 |
| Design latitude: balanced | the owner ruled the shape of each row; where each lesson lives follows the holistic rule | §2 | reversible | none | 2026-10-14 |
| §9 increments are grouped by subject, each with a disjoint write set; a file two subjects write is ordered by `Depends on:` | two writers of one file is a race no gate sees | §9 schedule note | reversible | none | 2026-10-14 |
| A reported defect is reproduced before its RED; one the code read confirms is fixed RED-first | the 8.0.0 rule for reported rows | the 2026-10-14 entries of SPEC-0007 and SPEC-0006 | reversible | none | 2026-10-14 |
| Parse failures of `graph-lint.py`, `grill-lint.py` and `status-register.py` under an interpreter below the floor are out of scope; the floor resolution fixes the cause | the owner kept the floor at 3.14 | SPEC-0005 §5 | reversible | none | 2026-10-14 |
| Two new delegation leaves, wave integrity and continuation, rather than a longer `delegation-bounds.md` | the method leaves' line ceiling forced the split; each leaf owns one concern | `core/method/delegation-wave-integrity.md`, `core/method/delegation-continuation.md` | reversible | none | 2026-10-14 |
| The two-axes rule lands without renaming the seed's `covered` and `contained` names | a rename ripples into the kernel and ADR-0006; the rule keeps a project's own vocabulary on its own axis | `core/method/tiers.md` | reversible | none | 2026-10-14 |
| A plant roster is gated on its own recorded adversarial baseline; the seed roster keeps its budget | the seed's budget was measured over the seed's roster; a plant's extra specialists change the number | SPEC-0002 `A_PLANT_ROSTER_IS_GATED_ON_ITS_OWN_ADVERSARIAL_BASELINE`; `graft.gate.routes` | reversible | none | 2026-10-14 |
| A generic page model-written without a fetch lands only after a fetch confirms each fact, or the fact is dropped | `protocol.harvest`: a model-supplied fact lands only after a fetch | the QoS skill page, fetched and corrected before it landed | reversible | none | 2026-10-14 |
| The upstream vendor name and default ports on the RouterOS collection page are library facts, re-admitted on that page only | a product's documented default port is not a plant port | a per-file allowance in the tree lint's forbid list | reversible | none | 2026-10-14 |

## 7. Options Considered
| Option | Benefits | Costs | Risks | Outcome |
|---|---|---|---|---|
| Lower the Python floor to 3.9 | stock `python3` works | rewrite every tool that uses newer syntax; a second floor in the specs | the class recurs with each new syntax | Rejected by the owner's decision of 2026-10-14 |
| A fixed `[redacted]` placeholder for identifying tokens (ADR-0011 limit (a)) | mechanical, no rewording | sentences lose the fact the token carried | a record a later reader cannot follow | Rejected by the owner's decision of 2026-10-14, superseding the placeholder choice made earlier that day (ADR-0031) |
| Compose mode as the default for an existing instruction hub | a team keeps its hub without a flag | a second kernel body in every plant that has one | two kernel homes | Rejected: opt-in, the owner's decision of 2026-10-14 |
| Rename the seed's `covered` and `contained` names for the two-axes rule | one vocabulary | kernel and ADR-0006 ripple at budget | a broken anchor in every plant | Rejected (§6) |
| One fixed HEAD for grow's write-scope gate across phases | simpler gate | checkpoint commits move HEAD | a false scope failure after the first checkpoint | Rejected: a baseline per phase (§2) |
| A hook that restricts the Bash scope of the read-only agents | mechanical enforcement | a hook cannot reliably know which agent issued a command | false blocks | Rejected: charter text, with the destructive-command guard unchanged |

## 8. Architecture Plan
- System boundary: unchanged; the seed installs into a plant directory and grafts into it, and the corpora reach a plant only by an explicit placement
- Main components: the installer's floor resolution (one responsibility: find an interpreter at the floor and name it in every hook); compose kernel mode; the stamp and backup reports; the agent router's plant baseline file `_eval.baseline.json`; the source index's three new incomplete reasons; the tree lint's local forbid list; graph-lint's reading of a placed corpus page as an entry point
- Interfaces: `install.sh <host> --kernel-mode compose|replace`; `install.sh <host> --expertise skill-corpus/<name>` (the flat id of a generic page); `agent-lint.py --eval --record-baseline`; `agnosticism-lint.py --forbid-file PATH`, `--tracked`, `--terms-only`
- Data flow: unchanged except the stamp key `kernel_mode` and the baseline file beside a plant's routing corpus
- Error handling: `NO_INTERPRETER_AT_THE_FLOOR` refuses before any write with a one-line fix; `HUB_NOT_COMPOSABLE` refuses compose over a hub it cannot keep; the crashed router is one notice line, exit 0
- Observability: the install prints the backups by date, the tracking lines and the retired stamp keys; `session-metrics --all` names a zero-entry answer on stderr
- Security posture: unchanged; no credential value in any seed file
- Deployment model: new plants at install; existing plants at their next graft
- Environment parity: `.github/workflows/gate.yml` runs the gate on Python 3.14, equal to `install.sh`'s `PYTHON_FLOOR` and SPEC-0005 §5; `tests/test-tool-help.sh` holds the three equal

## 9. Implementation Plan

Increments are inline, grouped by subject; numbers are dependency order. Increment 1 carries the contracts of SPEC-0001, SPEC-0002, SPEC-0006 and SPEC-0007 this round left as they were. Rolling back the whole round is reverting the 8.2.0 commit; an increment's own rollback restores its files from `1f7385a`.

| # | Subject | Status |
|---|---|---|
| 1 | carried | done |
| 2 | library corpus | done |
| 3 | installer | done |
| 4 | tools | done |
| 5 | graft and harvest | done |
| 6 | grow and lifecycle | done |
| 7 | delegation | done |
| 8 | postures | done |
| 9 | skills and agents | done |
| 10 | templates | done |
| 11 | tool corpus | done |
| 12 | skill corpus | done |
| 13 | generic skill-page frontmatter | done |
| 14 | placed corpus pages as entry points | done |
| 15 | legal corpus | done |
| 16 | identifying-token recast and ADR-0031 | done |
| 17 | tip: gate, review, sign-offs | done |

### Increment 1: Carried: the contracts this round left as they were
- Spec contracts: SPEC-0001/ADAPTERS_ACCUMULATE, SPEC-0001/ALL_CHECK_INCLUDES_RECORDED_COPILOT, SPEC-0001/ALL_EXCLUDES_LEGACY_HOSTS, SPEC-0001/ALL_NAMES_SKIPPED_FROZEN_HOSTS, SPEC-0001/BACKUP_BEFORE_REPLACE, SPEC-0001/CHECK_EXECUTES_EACH_WIRED_HOOK, SPEC-0001/CHECK_FLAGS_ORPHAN_HARNESS_ENTRY, SPEC-0001/CHECK_FLAGS_RETIRED_GRAPH_NODE, SPEC-0001/CHECK_FLAGS_RETIRED_HARNESS_ENTRY, SPEC-0001/CHECK_WITHOUT_COPILOT_SAYS_SO, SPEC-0001/CITED_PACKAGE_PROPOSES_NOTHING, SPEC-0001/CODE_ANCHOR_TOOL_IS_PLACED, SPEC-0001/COPY_MODE_ISOLATES, SPEC-0001/CORPUS_IS_WHOLE_OR_ABSENT, SPEC-0001/DECISIONS_SURVIVE_SILENCE, SPEC-0001/ENGINE_AUDIT_CHECKS_EVERY_PAIR, SPEC-0001/ENGINE_RECONCILE_PICKS_CONFIG_BY_ENGINE, SPEC-0001/EVERY_BACKUP_IS_CLASSIFIABLE, SPEC-0001/EXISTING_PLANT_RECEIVES_CURRENT_ENGINES, SPEC-0001/EXPERTISE_CHECK_NAMES_MISSING_OR_STALE, SPEC-0001/EXPERTISE_IS_RECORDED_IN_THE_STAMP, SPEC-0001/EXPERTISE_PLACES_ONLY_THE_CONFIRMED_LIST, SPEC-0001/EXPERTISE_PROPOSAL_WRITES_NOTHING, SPEC-0001/EXPERTISE_SURVIVES_SILENCE, SPEC-0001/FORCE_SUPPRESSES_WARNING_NOT_BACKUP, SPEC-0001/GRAFT_RUN_TIES_LINT_ERRORS_TO_RETIRED_NODES, SPEC-0001/HARVEST_CANDIDATE_FORM_IS_PLACED, SPEC-0001/HOST_TIERS_AGREE, SPEC-0001/IDENTICAL_RERUN_IS_INERT, SPEC-0001/JURISDICTION_RESOLVED_ONCE, SPEC-0001/LANGUAGE_DECLARATION_PROPOSES_ITS_PAGE, SPEC-0001/LEGACY_INSTALL_PRINTS_DEPRECATED, SPEC-0001/LEGACY_INSTALL_STILL_SUCCEEDS, SPEC-0001/MODEL_MAP_TEMPLATE_IS_PLACED, SPEC-0001/ONE_KERNEL_BODY, SPEC-0001/OPENCODE_CHECK_DETECTS_DRIFT, SPEC-0001/OPENCODE_MAP_UNREADABLE_FAILS_CLOSED, SPEC-0001/OPENCODE_MODEL_FROM_MAP, SPEC-0001/OPENCODE_NO_MAP_ROW_NO_MODEL_LINE, SPEC-0001/OWN_PACKAGE_LIST_PROPOSES_ITS_PAGE, SPEC-0001/PACKAGELESS_PAGE_PROPOSED_BY_ITS_TRIGGER, SPEC-0001/PLACED_PAGE_CARRIES_ITS_PROVENANCE, SPEC-0001/PLACED_SKILL_IS_A_ROUTABLE_NODE, SPEC-0001/PLANT_EDITED_PAGE_IS_LEFT_AND_NAMED, SPEC-0001/PLANT_OWNED_PAGE_IS_NEVER_REPLACED, SPEC-0001/PRE_GROWTH_POINTER_LIVES_IN_THE_PLACEHOLDER_INDEX, SPEC-0001/PREFLIGHT_REFUSES_BEFORE_WRITING, SPEC-0001/PREFLIGHT_SCOPED_TO_WRITTEN_TREES, SPEC-0001/PRIME_HOOK_SCRIPTS_ARE_PLACED, SPEC-0001/PRISTINE_PRIOR_KERNEL_IS_NOT_MIGRATION, SPEC-0001/RECORD_AGREES_WITH_DISK, SPEC-0001/RECREATED_LIST_IS_COMPLETE, SPEC-0001/REINSTALL_ENGINE_SERVES_THE_HOOKS, SPEC-0001/SEED_ONLY_FILES_NEVER_PLACED, SPEC-0001/SESSION_RECORD_FORM_IS_PLACED, SPEC-0001/SINGLE_WRITER, SPEC-0001/SYMLINK_IS_REPLACED_NOT_FOLLOWED, SPEC-0001/SYMLINK_MODE_IS_UNIFORM, SPEC-0001/UNKNOWN_EXPERTISE_ID_REFUSED_BEFORE_WRITING, SPEC-0001/UNKNOWN_STAMP_KEYS_SURVIVE, SPEC-0002/A_WORD_EVERY_TASK_WRITES_CANNOT_SELECT_AN_AGENT, SPEC-0002/ABSTENTION_IS_A_CORRECT_OUTCOME, SPEC-0002/AN_ABSOLUTE_FLOOR_IS_KEYED_TO_ITS_ROSTER, SPEC-0002/AN_INFLECTION_MATCHES_THE_WORD_IT_INFLECTS, SPEC-0002/COMPOSED_CHILD_NEEDS_ITS_OWN_PHRASE, SPEC-0002/COMPOUND_FRAGMENT_IS_WEAK_EVIDENCE, SPEC-0002/CONFIDENT_WRONG_IS_THE_GATE, SPEC-0002/CONTRACT_ROW_ABSTENTION_IS_A_DEFECT, SPEC-0002/EVERY_NUMBER_NAMES_ITS_CORPUS, SPEC-0002/GRAPH_EVAL_GATES_PER_CLASS, SPEC-0002/GRAPH_RATCHETS_ARE_KEYED_TO_THEIR_GRAPH, SPEC-0002/GRAPH_ROUTE_NAMED_ID_LOADS_IT, SPEC-0002/GRAPH_ROUTE_NAMED_PATH_LOADS_ITS_OWNER, SPEC-0002/GRAPH_ROUTE_PHRASE_LOADS_ITS_NODE, SPEC-0002/HELD_OUT_SET_MAY_NOT_BE_EMPTIED, SPEC-0002/HELD_OUT_STAYS_HELD_OUT, SPEC-0002/IDS_AND_PATHS_ARE_NOT_LEXICAL_TERMS, SPEC-0002/LONG_TASK_ABSTAINS_WITH_NOTICE, SPEC-0002/NEITHER_HELD_OUT_SET_MAY_BE_THINNED, SPEC-0002/NO_SIGNAL_LOADS_NOTHING, SPEC-0002/ONE_TERM_CANNOT_SEED_A_NODE, SPEC-0002/OVERLAP_IS_PUBLISHED_BESIDE_ACCURACY, SPEC-0002/PATH_OR_IDENTIFIER_DOES_NOT_BREAK_A_PHRASE, SPEC-0002/PATH_OR_IDENTIFIER_FILLS_A_SLOT_WORD, SPEC-0002/PATH_ROUTE_ADDS_SEED_SKILL_PHRASES, SPEC-0002/PATH_ROUTE_SKILL_ADDITION_IS_CAPPED, SPEC-0002/PROMOTION_NEEDS_A_CONTIGUOUS_PHRASE, SPEC-0002/PUNCTUATION_DOES_NOT_CHANGE_A_TERM, SPEC-0002/RARITY_AMPLIFIES_ONLY_A_CONFIDENT_MATCH, SPEC-0002/STRONG_TIER_OVER_CAP_FALLS_THROUGH, SPEC-0002/THE_ADVERSARIAL_BUDGET_IS_RATCHETED_NOT_ZERO, SPEC-0002/UNKNOWN_DOMAIN_MUST_ABSTAIN, SPEC-0002/VACUOUS_CORPUS_IS_REFUSED, SPEC-0006/METRICS_ALL_REPORTS_EVERY_ENTRY, SPEC-0006/METRICS_BLOCK_MISSING_FAILS, SPEC-0006/METRICS_COMPACT_ENTRY_EXEMPT, SPEC-0006/METRICS_DATED_HEADING_ENDS_ENTRY, SPEC-0006/METRICS_DELIVER_NODE_UNPARSEABLE_FAILS_LOUD, SPEC-0006/METRICS_ENTRIES_BEFORE_SINCE_NOT_JUDGED, SPEC-0006/METRICS_ENTRY_HEADINGS_RECOGNIZED, SPEC-0006/METRICS_FILLED_ENTRY_PASSES, SPEC-0006/METRICS_LABELS_FROM_DELIVER_NODE, SPEC-0006/METRICS_LEADING_BOM_IGNORED, SPEC-0006/METRICS_LINE_EMPTY_FAILS, SPEC-0006/METRICS_LINE_MISSING_FAILS, SPEC-0006/METRICS_LINES_COUNTED_AS_GREP_DOES, SPEC-0006/METRICS_LOW_TIER_EXEMPT, SPEC-0006/METRICS_MISSING_CHANGELOG_FAILS, SPEC-0006/METRICS_NO_ENTRY_SINCE_FAILS, SPEC-0006/METRICS_NOT_RECORDED_WITH_REASON_IS_FILLED, SPEC-0006/METRICS_NOT_RECORDED_WITHOUT_REASON_FAILS, SPEC-0006/METRICS_OTHER_ENTRY_DEFECT_IS_A_NOTE, SPEC-0006/METRICS_READER_RUNS_IN_A_FRESH_PLANT, SPEC-0006/METRICS_SECTION_HEADINGS_STAY_IN_ENTRY, SPEC-0006/METRICS_SHIPPED_DELIVER_NODE_PARSES, SPEC-0006/METRICS_SINCE_REQUIRED, SPEC-0006/METRICS_UNREADABLE_CHANGELOG_FAILS_LOUD, SPEC-0007/ACTION_LINE_NAMES_AT_MOST_TEXT_MAX_ROWS_RECORDS, SPEC-0007/AFFECTED_ALWAYS_RUN_LISTED_APART, SPEC-0007/AFFECTED_TESTS_ARE_THE_WALK_FILTERED, SPEC-0007/ANCHORS_BASENAME_IS_MAYBE_AMBIGUOUS_IS_INCOMPLETE, SPEC-0007/ANCHORS_MOVED_EQUALS_THE_NAMED_PATHS, SPEC-0007/ANCHORS_MOVED_WITHOUT_A_LIST_IS_INCOMPLETE, SPEC-0007/ANCHORS_NAME_CITING_PAGES_OR_UNCITED, SPEC-0007/BUILD_HINTS_CONFIG_PATTERNS_THAT_MATCH_NOTHING, SPEC-0007/BUILD_HINTS_EXCLUDE_FOR_NON_TEST_FILES, SPEC-0007/BUILD_INVENTORIES_THE_CODE_OF_EVERY_GOVERNED_REPOSITORY, SPEC-0007/BUILD_IS_DETERMINISTIC, SPEC-0007/BUILD_NAMES_REPO_VALUES_THAT_NAME_NOTHING, SPEC-0007/BUILD_NAMES_TESTS_OUTSIDE_THE_TEST_CLASS, SPEC-0007/BUILD_RECORDS_NAME_THEIR_FIX, SPEC-0007/BUILD_REPORTS_ITS_TIME_AND_COUNTS, SPEC-0007/CACHE_REBUILT_WHEN_THE_KEY_CHANGES, SPEC-0007/CACHE_REUSED_WHILE_THE_KEY_HOLDS, SPEC-0007/CACHE_WRITTEN_SELF_IGNORED, SPEC-0007/GRAFT_REBUILDS_THE_CACHE, SPEC-0007/GROWTH_AUDIT_PRINTS_THE_BUILD_REPORT, SPEC-0007/HISTORY_ONLY_ADDS, SPEC-0007/HISTORY_ROWS_ARE_MAYBE_WITH_THEIR_COUNT, SPEC-0007/HISTORY_SHALLOW_OR_MISSING_IS_INCOMPLETE, SPEC-0007/INPUT_FORMS_RESOLVED, SPEC-0007/INSTALL_RUNS_THE_BUILD, SPEC-0007/KERNEL_NAMES_THE_SOURCE_INDEX, SPEC-0007/LINK_PATH_LITERAL_AND_DIRECTORY_ARE_MAYBE, SPEC-0007/LINK_PYTHON_IMPORT_CERTAIN, SPEC-0007/LINK_SHELL_INVOCATION_CERTAIN, SPEC-0007/LINK_TS_SPECIFIER_CERTAIN, SPEC-0007/OUTPUT_CARRIES_NO_RAW_CONTROL, SPEC-0007/PLANT_CONFIG_REPLACES_EACH_DEFAULT_KEY, SPEC-0007/REPO_CLAIM_READ_ALIKE_BY_ROUTER_AND_ANCHORS, SPEC-0007/SOURCE_INDEX_IS_PLACED, SPEC-0007/SOURCE_INDEX_SKILL_ROUTES_ITS_FOUR_QUESTIONS, SPEC-0007/SYMBOLS_LINE_READ_DECLARATIONS_ARE_MAYBE, SPEC-0007/SYMBOLS_LIST_EVERY_DEFINITION, SPEC-0007/SYMBOLS_PYTHON_DEFINITIONS_CERTAIN, SPEC-0007/SYMBOLS_UNREADABLE_FILE_MAKES_IT_INCOMPLETE, SPEC-0007/TESTS_ARE_THE_PLANTS_TEST_GLOBS, SPEC-0007/UNPINNED_REFERENCE_RECORDED_WITH_ITS_REASON, SPEC-0007/WALK_CHAIN_IS_ITS_WEAKEST_LINK, SPEC-0007/WALK_DELETED_INPUT_REACHES_ITS_NAMERS, SPEC-0007/WALK_FLOOR_LISTED_APART_AFTER_THE_INPUT_ROWS, SPEC-0007/WALK_INCOMPLETE_NAMES_REASON_AND_ACTION, SPEC-0007/WALK_NEAREST_FIRST_ONCE
- Files touched: none
- Tests to write (RED): none: implemented and green at `1f7385a` under `docs/plans/grill-8.0.0-wave-a.md`, `docs/plans/grill-8.1.0-source-index.md` and `docs/plans/grill-8.1.2-tool-surfacing.md`; this round amended the text of `ONE_KERNEL_BODY` (an Except for compose mode), `CHECK_EXECUTES_EACH_WIRED_HOOK` (each hook runs on the interpreter it names), `PLACED_SKILL_IS_A_ROUTABLE_NODE` (the flat id of a generic page) and `THE_ADVERSARIAL_BUDGET_IS_RATCHETED_NOT_ZERO` (an And clause pointing at the plant baseline), each held by the cases increments 3 and 4 name
- Behavior added: none
- Gate: their §10 rows stay green in increment 17's full gate
- Rollback path: none needed
- Effort: low
- Phase: GREEN
- Depends on: none

### Increment 2: Library corpus
- Spec contracts: none: corpus content; its contract is `library-corpus/README.md`'s admission bar and seed-lint's page checks
- Files touched: 47 pages under `library-corpus/` (27 new, 16 rewritten whole, one correction, three back-links from existing pages)
- Tests to write (RED): none: corpus pages are transcribed knowledge (the recorded exemption in `CLAUDE.md`); proved by `tests/seed-lint.py`, `tools/agnosticism-lint.py` against the forbid list, and a review of every page against its fetched sources (no page blocked; four seed claims corrected upstream-first)
- Behavior added: the matcher can propose the new pages to a plant whose manifests name their packages
- Gate: seed-lint and the tree lint green; the page review closed
- Rollback path: restore `library-corpus/` from `1f7385a`
- Effort: high
- Phase: prose
- Depends on: none

### Increment 3: Installer: the floor, the crashed router, compose mode, the install reports
- Spec contracts: SPEC-0001/HOOKS_RUN_ON_THE_FLOOR_INTERPRETER, SPEC-0001/STAMP_TRACKING_LINES_PRINTED, SPEC-0001/BACKUPS_LISTED_BY_DATE, SPEC-0001/HUB_KEPT_CANONICAL_IN_COMPOSE_MODE, SPEC-0001/RETIRED_STAMP_KEYS_NAMED_AND_KEPT, SPEC-0001/ONE_KERNEL_BODY, SPEC-0001/CHECK_EXECUTES_EACH_WIRED_HOOK, SPEC-0001/PLACED_SKILL_IS_A_ROUTABLE_NODE, SPEC-0001/PACKAGELESS_PAGE_PROPOSED_BY_ITS_TRIGGER
- Files touched: `install.sh`, `tools/corpus-match.py`, `integrations/claude-code/route-hook.py`, `integrations/claude-code/settings.json`, `integrations/prime-agent/route-extension.ts`, `integrations/prime-agent/status-extension.ts`, `.github/workflows/gate.yml`, `docs/specs/SPEC-0001-install-placement.md` (five contracts, the failures `NO_INTERPRETER_AT_THE_FLOOR` and `HUB_NOT_COMPOSABLE`, the §6 Graph SDK trigger row, the `kernel_mode` key, the flat skill row), `docs/specs/SPEC-0003-per-prompt-injection.md` (the failure `ROUTER_CRASH_IS_NAMED` and its `CRASHED` text), `docs/specs/SPEC-0005-cycle-economy.md` (§5, the floor's one home), `tests/test-full-install.sh`, `tests/test-install-kernel-modes.sh`, `tests/test-install-placement.sh`, `tests/test-prompt-hooks.sh`, `tests/test-tool-help.sh`, `tests/test_corpus_match.py`, `tests/fixtures/corpus-placement/`, `skill-corpus/README.md` (placement text)
- Tests to write (RED): E16 (the floor interpreter in every hook command), E17 (the tracking lines), E18 (backups by date), E19 (the floor sweep: every shipped script compiles and every tool answers `--help` at the floor), K8 (compose keeps the hub), M21 (retired stamp keys), X471 (the crashed router), the matcher's Graph SDK rows; E19 and the matcher rows were seen red first, the others first ran after the change, so their RED is by construction, recorded in SPEC-0001's changelog
- Behavior added: the installer runs on, and writes into each hook, the first interpreter at the floor on PATH, or refuses before writing; a crashed router is one notice line; the install prints the stamp's tracking lines, the backups by date and the retired stamp keys; `--kernel-mode compose` keeps a team's hub; a generic skill page is placed by its flat id; E16 also found and fixed a bash 3.2 defect in `place_state`
- Gate: the named suites green on the floor interpreter; `SINGLE_WRITER`'s count unchanged
- Rollback path: restore the files above from `1f7385a`
- Effort: high
- Phase: GREEN
- Depends on: increment 1

### Increment 4: Tools: source index, session metrics, the plant roster's baseline, the unspecced lints
- Spec contracts: SPEC-0007/INPUT_IN_AN_UNREAD_LANGUAGE_IS_INCOMPLETE, SPEC-0007/TEST_REACHING_CODE_OVER_HTTP_IS_INCOMPLETE, SPEC-0007/ANCHORS_MOVED_SKIPS_A_NESTED_WORK_TREE, SPEC-0006/METRICS_ZERO_ENTRIES_ARE_NAMED, SPEC-0002/A_PLANT_ROSTER_IS_GATED_ON_ITS_OWN_ADVERSARIAL_BASELINE, SPEC-0002/THE_ADVERSARIAL_BUDGET_IS_RATCHETED_NOT_ZERO
- Files touched: `tools/source-index.py`, `tools/session-metrics.py`, `tests/test-source-index.sh`, `tests/test-session-metrics.sh`, `docs/specs/SPEC-0007-source-index.md`, `docs/specs/SPEC-0006-session-metrics.md`; `integrations/claude-code/agent-lint.py`, `tests/test_agent_lint.py`, `docs/specs/SPEC-0002-routing-contract.md`; the unspecced tools, in remediation mode with each rule held by its regression case (§12 question 3): `tools/graft-audit.py` and `tests/test-graft-tools.sh` (`--record` reads any heading that names a graft, in any case or position, and bold-label bullets; an entry that lists no file fails closed), `templates/knowledge-graph/spec-lint.py` and `tests/test-spec-lint.sh` (a slug only a comment carries is a WARN, never coverage; the seed's own suites name their slugs in code), `tools/plant_walk.py` (a seed checkout inside the plant is foreign to the walk), `tools/agnosticism-lint.py`, `tests/test-agnosticism-lint.sh`, `tests/run.sh`, `tools/gate-registry.py` and `docs/skills/seed-release.md` (`--forbid-file` with allow exemptions, `--tracked`, `--terms-only`, and a gate step that lints the shipped tree against the local forbid list, SKIPPED when it is absent), `tests/fixtures/grill/scheduled_plan.py` (the fixture writer refuses a file that is not a plan: handed its own path, it had spliced a plan into its own source)
- Tests to write (RED): each seen red first on a synthetic plant: X481 (a Go input answers `language-not-read`, a Python input does not), X482 (a loopback-URL end-to-end test is `reached-over-http`), X483 (a work tree added under the plant is one `repository-unnamed` record and the rest of the moved list is answered), X484 (a changelog with dated headings in no known form is named on stderr); X448's `NON_UTF8_PATH` arm reports SKIPPED where the filesystem refuses the name; three agent-lint cases, red observed first (the seed roster plus one plant agent under bait rows failed `--eval` on the seed's budget): a plant roster without a baseline is reported, not gated; the recorded baseline gates it; the seed roster ignores a baseline file; one regression case per unspecced rule in the suites named
- Behavior added: an input in a language the index does not read, a test that reaches code only over HTTP, and a nested work tree each get a named record instead of an empty or refused answer; a zero-entry metrics answer says why; `agent-lint.py --eval --record-baseline` writes `_eval.baseline.json` beside a plant's corpus, and the seed roster keeps the constant and refuses the flag; the unspecced rules as listed
- Gate: `tests/test-source-index.sh`, `tests/test-session-metrics.sh`, `tests/test_agent_lint.py` and the named suites green; the agent route eval holds its ratchets; `python3 tools/gate-registry.py --summary` classifies the new step
- Rollback path: restore the files above from `1f7385a`
- Effort: medium
- Phase: GREEN
- Depends on: increment 1

### Increment 5: Graft and harvest
- Spec contracts: none: doctrine text, proved by the lints that already run
- Files touched: `protocols/graft.md`, `protocols/harvest.md`, `GRAFT_PROMPT.md`, `HARVEST_PROMPT.md`
- Tests to write (RED): none: doctrine text; proved by seed-lint, prose-lint and the route corpus
- Behavior added: graft makes the baseline commit itself, per repository shape, with checkpoint commits; graft lists backups by date; graft identifies the plant's needs and places generic skill, tool and library knowledge where it is needed; `graft.gate.routes` records a plant's adversarial baseline with `--eval --record-baseline` at the graft that brings the routing corpus or changes the roster; the harvest's gate on the plants compares content hashes of dirty, untracked and read-ignored files, so a write to an already-dirty file is caught; a fast path for re-reading a plant a harvest has already read; seed prose and plant prose kept apart in what a harvest reads; the harvest's agnosticism check uses `--forbid-file`
- Gate: `tests/run.sh` doctrine steps green
- Rollback path: restore the files above from `1f7385a`
- Effort: medium
- Phase: prose
- Depends on: increment 3 and increment 4 (the interfaces the text names)

### Increment 6: Grow and the lifecycle protocols
- Spec contracts: none: doctrine text
- Files touched: `protocols/grow.md`, `protocols/from-scratch.md`, `protocols/specify.md`, `protocols/ingest-library.md`, `protocols/recover.md`, `protocols/verify.md`, `protocols/deliver.md`, `protocols/test-first.md` (the operations-pass exception)
- Tests to write (RED): none: doctrine text; proved by seed-lint and prose-lint
- Behavior added: grow identifies the plant's needs and places knowledge where needed; grow commits a checkpoint per phase and gates write scope against each phase's baseline; from-scratch says when `grown:` becomes true; a post-freeze corrections record growth authors read and append; owner-stated facts no file witnesses are recorded as such; an operations pass lists a root-caused bug and fixes it only on the owner's go-ahead
- Gate: `tests/run.sh` doctrine steps green; `ingest-library` within its line ceiling
- Rollback path: restore the files above from `1f7385a`
- Effort: medium
- Phase: prose
- Depends on: increment 5 (grow's baseline commit points at graft's)

### Increment 7: Delegation, decision economy, tiers
- Spec contracts: none: doctrine text
- Files touched: `core/method/delegation-wave-integrity.md` (new), `core/method/delegation-continuation.md` (new), `core/method/delegation.md`, `core/method/delegation-briefs.md`, `core/method/delegation-bounds.md`, `core/method/delegation-sequencing.md`, `core/method/delegation-model-classes.md`, `core/method/decision-economy.md`, `core/method/tiers.md`, `core/method/bounded-execution.md`, `manifest.json` (the two new leaves)
- Tests to write (RED): none: doctrine text; proved by seed-lint (machinery-node frontmatter, unique `owns`) and the route corpus
- Behavior added: running a parallel wave as one passage (a table of each worker's write set, a wave baseline, durable output); the continuation rule for resuming an agent; every worker runs its own route, superseding the caller-runs clause for a worker without a shell; numbered options with a recommendation; the conditional one-command rule; the two-axes rule
- Gate: seed-lint green
- Rollback path: restore the files above from `1f7385a`
- Effort: medium
- Phase: prose
- Depends on: none

### Increment 8: The method postures
- Spec contracts: none: doctrine text
- Files touched: `core/method/release-posture.md`, `core/method/secrets-posture.md`, `core/method/contract-posture.md`, `core/method/host-parity.md`, `core/method/vcs-posture.md`, `core/method/design-posture.md`, `core/method/incident-posture.md`, `core/method/stewardship-posture.md`
- Tests to write (RED): none: doctrine text; proved by seed-lint
- Behavior added: the postures absorb the rollback, backup, credential, contract, reconcile and diagnosis rules plants had written for themselves
- Gate: seed-lint green; `incident-posture.md` at its leaf line ceiling
- Rollback path: restore the files above from `1f7385a`
- Effort: medium
- Phase: prose
- Depends on: none

### Increment 9: Skills and agents
- Spec contracts: none: charter and skill text, with regenerated golden routes
- Files touched: `skills/test-first/SKILL.md`, `skills/adopt-existing/SKILL.md`, `skills/knowledge-graph/SKILL.md`, `skills/library-wiki/SKILL.md`, `skills/toolcraft/SKILL.md`, the lead agent's charter `agents/00-orchestrator.md`, `agents/01-architect.md`, `agents/04-tester.md`, `agents/05-security.md`, `agents/08-product.md`, `agents/09-docs-librarian.md`, `agents/12-devils-advocate.md`, `agents/13-ui-ux-designer.md`, `agents/14-legal.md`, `agent-corpus/iac-change-author.md`
- Tests to write (RED): none: charter text; proved by `agent-lint.py --lint`, the agent route eval and seed-lint
- Behavior added: architect, product, devils-advocate, ui-ux-designer and legal get Bash for lookup and measurement only, by charter; the operations-pass mode in the tester's bug-fix loop; test-set design and batched mutation testing in test-first; the docs-librarian charter stops contradicting `canonize.harvest-candidates`; library-wiki gains its trigger for filing a staged draft
- Gate: agent-lint and the agent route eval green
- Rollback path: restore the files above from `1f7385a`
- Effort: medium
- Phase: prose
- Depends on: increment 7 (the lookup rule the charters follow)

### Increment 10: Templates
- Spec contracts: none: template text; the brief templates' byte identity is held by seed-lint
- Files touched: `templates/prompts/graph-session-bootstrap.md` and the brief templates that embed it, `templates/prompts/handback-payload.md`, `templates/prompts/growth-author-brief.md`, `templates/spec.template.md`, `templates/library-page.template.md`, `templates/docs/README.md`, and under `templates/docs/` the libraries and tools index templates, the rollback runbook template and the session record template, `templates/knowledge-graph/index.md`
- Tests to write (RED): none: template text; proved by seed-lint's canonical-block check and prose-lint
- Behavior added: a worker checks its stack route at the start of a task and leaves shared git state alone; spec §10 states setup sharing; rollback per unit; library page travel marks; the libraries index states its completeness; declined tool candidates are recorded; the index routes the two new delegation leaves
- Gate: seed-lint green
- Rollback path: restore the files above from `1f7385a`
- Effort: medium-low
- Phase: prose
- Depends on: increment 7 (the bootstrap points at `delegation.briefs`)

### Increment 11: Tool corpus
- Spec contracts: none: corpus content (the recorded exemption)
- Files touched: `tool-corpus/README.md`, 20 pages under `tool-corpus/ops/` and `tool-corpus/testing/` (11 new, 9 integrated)
- Tests to write (RED): none: corpus content; proved by seed-lint's page checks and the tree lint
- Behavior added: the demo password rule in `owner-scoped-idempotent-seed.md`
- Gate: seed-lint green; the database citations of `replicated-scheduled-sweep-guards.md` checked against fetched sources
- Rollback path: restore the files above from `1f7385a`
- Effort: medium
- Phase: prose
- Depends on: none

### Increment 12: Skill corpus
- Spec contracts: none: corpus content (the recorded exemption)
- Files touched: new `skill-corpus/dead-hostname-audit.md`, `skill-corpus/review-rendered-ui.md`, `skill-corpus/change-review-report.md` (the throwaway review packet generalized), `skill-corpus/galaxy/managed-edge-read-only-triage.md`, `skill-corpus/galaxy/shared-line-qos-design.md`; integrated `skill-corpus/prove-red-after-green.md`, `skill-corpus/adversarial-pentest-passes.md` (defensive level), `skill-corpus/deploy-fleet-on-remote-docker-host.md`, `skill-corpus/vulnerability-reduction-by-version-bumps.md`, `skill-corpus/seed-demo-world-for-manual-ui-review.md`; `.github/workflows/release.yml` (a comment follows the rename)
- Tests to write (RED): none: corpus content; proved by seed-lint and the tree lint; the QoS page's facts fetched and corrected before it landed
- Behavior added: none in code
- Gate: seed-lint green
- Rollback path: restore the files above from `1f7385a`
- Effort: medium
- Phase: prose
- Depends on: increment 11 (the demo password rule the demo-world page follows)

### Increment 13: Node frontmatter on every generic skill-corpus page
- Spec contracts: SPEC-0001/PLACED_SKILL_IS_A_ROUTABLE_NODE
- Files touched: every generic page under `skill-corpus/`, the `prevents:` line on the keyed pages, `skill-corpus/README.md` (the frontmatter contract in its own section), `documentation/corpus-placement.md` (the generic id form and the refusal of a page without frontmatter)
- Tests to write (RED): none: the placement contract is increment 3's; the gap was that no generic page carried frontmatter, so the installer refused every one; proved by seed-lint's frontmatter checks and a scratch install that places a generic page as a routable node
- Behavior added: needs-driven placement reaches every generic page
- Gate: seed-lint green; the scratch install's graph-lint route loads a placed generic page
- Rollback path: restore the files above from `1f7385a`
- Effort: medium-low
- Phase: prose
- Depends on: increment 3 (the flat id it places by) and increment 12 (the pages it gives frontmatter)

### Increment 14: A placed corpus page is an entry point of the plant's graph
- Spec contracts: SPEC-0001/PLACED_CORPUS_PAGE_IS_REACHABLE
- Files touched: `templates/knowledge-graph/graph-lint.py` (the reachability rule reads `origin: corpus@<version>` as an entry point), `templates/knowledge-graph/index.md` (one sentence: a placed page needs no row), `templates/knowledge-graph/_schema.md` rule 7, `tests/test-install-placement.sh` (M16), `tests/test_graph_lint.py` (CorpusPlacedEntryTests), `docs/specs/SPEC-0001-install-placement.md`
- Tests to write (RED): M16 a placed generic and a placed keyed skill page leave the plant's graph-lint green and reachable by `--plan`; CorpusPlacedEntryTests a node carrying `origin: corpus@<version>` is an entry point and one without it stays unreachable
- Behavior added: a page `install.sh --expertise` places is reachable without a row in the plant's `index.md`; the installer and the plant's index stay untouched, removing the page leaves nothing behind, and a plant that drops the `origin:` line takes the page over and lists it itself
- Gate: `bash tests/test-install-placement.sh`, `python3 tests/test_graph_lint.py`; a scratch install that places corpus pages of each kind passes the plant's graph-lint
- Rollback path: restore the files above from `1f7385a`
- Effort: medium-low
- Phase: GREEN
- Depends on: increment 10 (the index template it amends) and increment 13 (the generic pages it makes reachable)

### Increment 15: Legal corpus
- Spec contracts: none: corpus content (the recorded exemption)
- Files touched: `legal-corpus/eu/mdr.md` (new), `legal-corpus/eu/gdpr.md` (Arts. 11, 12, 88 and Recital 26 from the publisher's current text), `legal-corpus/eu/cra.md`, `legal-corpus/index.md`
- Tests to write (RED): none: legal entries are held by `legal-lint.py`
- Behavior added: none in code
- Gate: legal-lint and seed-lint green
- Rollback path: restore the files above from `1f7385a`
- Effort: medium-low
- Phase: prose
- Depends on: none

### Increment 16: Identifying tokens recast generically; ADR-0031
- Spec contracts: none: record text under the owner's decision of 2026-10-14; no figure, rule or decision changed
- Files touched: `docs/decisions/adr-0031-donor-tokens-recast-generically.md` (new), `docs/decisions/index.md`, `docs/decisions/adr-0029-source-index-is-derived-scratch.md` (body recast, with a dated section saying so), `docs/plans/grill-8.1.0-source-index.md`, `docs/plans/grill-8.1.2-tool-surfacing.md`, `docs/specs/SPEC-0007-source-index.md`, `tests/graph-routes.golden.tsv`, `tests/test-install-adoption.sh`, `CHANGELOG.md` (the 8.1.2 entry), `.github/RELEASE_NOTES.md`, `CLAUDE.md` (Conventions follow ADR-0031)
- Tests to write (RED): none: record text; proved by the tree lint against the forbid list over the whole shipped tree, and by the two edited tests staying green
- Behavior added: none
- Gate: `tools/agnosticism-lint.py --tracked` with the forbid list PASS; `tests/graph-route-eval.sh` and `tests/test-install-adoption.sh` green
- Rollback path: restore the files above from `1f7385a`; the disclosure in the release CHANGELOG stays owed either way
- Effort: medium-low
- Phase: prose
- Depends on: increment 4 (both write SPEC-0007, and the tree lint's `--forbid-file` is this increment's proof)

### Increment 17: Tip: the full gate, the review and the sign-offs
- Spec contracts: SPEC-0001/HOOKS_RUN_ON_THE_FLOOR_INTERPRETER, SPEC-0001/STAMP_TRACKING_LINES_PRINTED, SPEC-0001/BACKUPS_LISTED_BY_DATE, SPEC-0001/HUB_KEPT_CANONICAL_IN_COMPOSE_MODE, SPEC-0001/RETIRED_STAMP_KEYS_NAMED_AND_KEPT, SPEC-0002/A_PLANT_ROSTER_IS_GATED_ON_ITS_OWN_ADVERSARIAL_BASELINE, SPEC-0006/METRICS_ZERO_ENTRIES_ARE_NAMED, SPEC-0007/INPUT_IN_AN_UNREAD_LANGUAGE_IS_INCOMPLETE, SPEC-0007/TEST_REACHING_CODE_OVER_HTTP_IS_INCOMPLETE, SPEC-0007/ANCHORS_MOVED_SKIPS_A_NESTED_WORK_TREE, SPEC-0001/PLACED_CORPUS_PAGE_IS_REACHABLE
- Files touched: the §0 sign-off lines of SPEC-0001, SPEC-0006 and SPEC-0007; `tools/graft-audit.py` (compose mode); this plan's §12 and §15; each review fix, in the file it names
- Tests to write (RED): none: verification and review; the round adds one case per contract to existing suites and no new suite; two tester-requested assertions tightened in place
- Behavior added: `graft-audit.py` reads a compose-mode plant; the review checked every increment for bolt-on seams and unfetched facts and its fixes are applied; product, architect and tester each reviewed the new contracts alone and read-only. Product accepted the floor and the stamp lines, accepted backups, retired keys and the crashed router with changes since applied, and accepted compose once `graft-audit.py` learned compose mode; tester accepted every new contract, two after tightened asserts; architect accepted with changes since applied
- Gate: `bash tests/run.sh` passed on the floor interpreter, all 52 steps; every review closed; every sign-off ticked
- Rollback path: none needed
- Effort: medium
- Phase: prose
- Depends on: increment 2, increment 6, increment 8, increment 9, increment 14, increment 15 and increment 16, which close every other increment

**Delegation and parallelism.** The static schedule is `python3 templates/knowledge-graph/grill-lint.py --plan docs/plans/grill-8.2.0-harvest.md --specs docs/specs --decisions docs/decisions --waves`. Each increment owns an exclusive write set; a file two increments write is ordered by a `Depends on:` path. Serialization points: `skill-corpus/README.md` and the skill-corpus pages (3 or 12, then 13); `docs/specs/SPEC-0001-install-placement.md` and `tests/test-install-placement.sh` (3, then 14, then 17); `docs/specs/SPEC-0007-source-index.md` (4, then 16, then 17); `tools/graft-audit.py` (4, then 17); `templates/knowledge-graph/index.md` (10, then 14); `tests/run.sh` (4, then this plan's `ACTIVE_PLAN` line). The schedule puts no two writers of one file in one wave.

## 10. Verification Plan
The standard gate holds (`CLAUDE.md` Gates: `bash tests/run.sh`), on an interpreter at the 3.14 floor. This plan diverges in two places:

- The tree lint step against the local forbid list is SKIPPED on a checkout without that list; the release procedure runs it.
- The RED of E16, E17, E18, K8, M21 and X471 is by construction: they first ran after the change, as SPEC-0001's and SPEC-0003's changelogs record.

## 11. Risks and Mitigations
| Risk | Probability | Impact | Mitigation | Owner | Verification |
|---|---:|---:|---|---|---|
| A fold-back reads as an appended harvest section | medium | medium | the holistic rule; the tip's review checks for seams | architect | increment 17 |
| A corpus page carries a model-supplied fact no fetch confirmed | medium | medium | fetch or drop before landing | docs-librarian | increment 17's review of increments 11 and 12 |
| A project-identifying token reaches a seed file again | medium | high | the gate step with the local forbid list; the release procedure runs it | the steward | increment 4's gate step |
| A plant host has no interpreter at the floor | medium | medium | the installer refuses before writing, with the fix line | implementer | `NO_INTERPRETER_AT_THE_FLOOR` |
| Compose mode leaves two kernel homes | low | medium | opt-in; `--kernel-mode replace` restores one body; the stamp records the mode | architect | K8 |
| A plant's recorded adversarial baseline hides a routing regression | low | medium | the baseline is recorded only at the graft that brings the corpus or changes the roster; the seed roster keeps its budget | tester | `tests/test_agent_lint.py` |

## 12. Open Questions
| # | Question | Why it matters | Current assumption | How to resolve | Owner | Pinned by |
|---:|---|---|---|---|---|---|
| 1 | **do-not-guess** The reported defect that the router misses task lines written in a language other than English has not been reproduced | a plant may route nothing for such a task | open | reproduce on a scratch install, then rule | owner | none |
| 2 | **do-not-guess** `--symlink` writes absolute targets, so a seed copy inside a project breaks when the project moves | relative links change every symlink install | left as is; the owner has not ruled | the owner's decision | owner | none |
| 3 | Do the unspecced rules of increment 4 (graft-audit's record reading, spec-lint's comment rule, the walk's foreign checkout, the tree lint's local list) earn a spec? | they change in remediation mode | no new spec this round; each regression case holds its rule | a later specify pass, if the owner wants one | owner | increment 4 |
| 4 | The owner's longer list of working preferences has not been sent | the preferences row of §2 is partial | nothing written until it arrives | the owner | owner | none |

## 13. Done Criteria
- Every increment in §9 is done; each new contract has a `green` §10 row in its spec, and `spec-lint.py` is within its budget.
- `grill-lint.py` lints this plan from `tests/run.sh` and passes, and `--waves` prints no overlap warning.
- `bash tests/run.sh` is green on the floor interpreter.
- The tree lint against the local forbid list passes over every tracked file.
- Product, architect and tester have signed the new contracts.

## 14. Recommended Next Step
Run the release pass, `docs/skills/seed-release.md`; the tag push waits for the owner's explicit go-ahead.

## 15. Changelog
- 2026-10-14: plan written as the record of round 8.2.0, a harvest: the owner's decisions of 2026-10-14 listed in §2, and the increments of §9 grouped by subject. `tests/run.sh` `ACTIVE_PLAN` moves here from the 8.1.2 plan, so the gate holds the eleven contracts this round added. The tip closed with the full gate green, the review's fixes applied and the product, architect and tester sign-offs given.
