# grill.md: Plan of Record: round 8.3.1, token efficiency

## 0. Metadata
- Project: CYPRESS seed
- Feature or goal: make the method spend fewer model turns and fewer rewritten tokens on work that needs no judgment, and make token use visible per spawn, with every quality safeguard as strong as before; mechanisms E1 to E8 of the owner's brief of 2026-11-10
- Date: 2026-11-10
- Owner: the steward
- Tier: T3. Protocol: `protocol.grill` for the increments; this plan is the record of what lands and why
- Current phase: increments 1 to 5 are done; the later mechanisms append their own increments
- Related files: `tools/brief.py`, `tools/session-metrics.py`, `protocols/deliver.md`, `integrations/claude-code/resume-hook.py`, `integrations/claude-code/README.md`, `core/method/delegation-continuation.md`, `install.sh`, `tests/test-brief.sh`, `tests/test-session-metrics.sh`, `tests/test-resume-hook.sh`, `tests/run.sh`
- Related documentation: `docs/plans/grill-8.2.0-harvest.md` (the previous plan the gate linted, and the shape of its carried increment); `docs/skills/seed-release.md` (the release pass that follows this plan)
- Related ADRs: none new
- Related specs: [SPEC-0005](../specs/SPEC-0005-cycle-economy.md) (the token ledger and the resume guard); [SPEC-0006](../specs/SPEC-0006-session-metrics.md) (the Tokens line); [SPEC-0001](../specs/SPEC-0001-install-placement.md) (the cache-lifetime opt-in, increment 4)
- Related libraries: none (stdlib Python and bash)
- Baseline: the 8.3.0 experimental line at `ce0d12c` (the 8.3.0 release documentation pass and its staged notes, untagged); this round builds on it

## 1. Artifact Discovery
Every line cites the paths it rests on. Each owner decision is stated in words with its date.
- Existing files inspected: `tools/brief.py` (the spawn log and its one writer); `tools/session-metrics.py`; `integrations/claude-code/resume-hook.py` (`COLD_AFTER`); `integrations/claude-code/settings.json`; `install.sh` (its options and `--check`); `templates/knowledge-graph/grill-lint.py` (the rule that every declared contract of a named spec appears in some increment)
- Existing docs inspected: `docs/plans/grill-8.2.0-harvest.md` (shape, carried increment); `templates/grill.template.md`; `core/method/delegation-continuation.md`; `CLAUDE.md`
- Existing tests inspected: `tests/run.sh` (`ACTIVE_PLAN`); `tests/test-brief.sh` (X505, X506); `tests/test-session-metrics.sh` (X504); `tests/test-resume-hook.sh`
- Existing specs inspected: `docs/specs/SPEC-0001-install-placement.md`, `SPEC-0005-cycle-economy.md`, `SPEC-0006-session-metrics.md` (each one's `### Contract:` list and its 2026-11-10 changelog entries)
- Existing architecture signals: the kernel, the always-loaded surface of each host and the canonical brief blocks are measured before the round and may not grow (`tests/seed-lint.py`)
- Libraries already wikified: none, no library is a dependency of the seed's code
- External sources downloaded: none; the Claude Code documentation pages on prompt caching, settings, subagents and environment variables were read on 2026-11-10 and each fact this round relies on is cited where it lands
- Constraints discovered: the claude-code always-loaded figure has no slack (`EAGER_EXEMPTIONS` in `tests/seed-lint.py`); `install.sh --check` names a missing route or status hook script but not a missing resume or bound hook script

## 2. Shared Understanding
The owner's brief of 2026-11-10 asks for eight mechanisms that reduce token use without changing any safeguard, and for the trials that need measurement to be prepared, not landed. No token or cost saving is measured or claimed by this round; each mechanism makes a saving measurable by the owner.

| Mechanism | What it settles | Where it lands |
|---|---|---|
| E1 token ledger | host-reported tokens per spawn, or `not recorded`; an optional Tokens metrics line | increment 2 |
| E2 resume guard lifetime | the guard follows the worker cache lifetime the host is configured for, 300 seconds when it cannot tell | increment 3 |
| E3 cache-lifetime settings | documented, and placed only on an explicit opt-in | increment 4 |
| E4 to E8 | cycle driver, generated delivery lines, batch-size notice, two execution rules, trial enablement | later increments, appended as each lands |

Success means: each mechanism exists, is correct and tested, and the three byte figures are not above the baseline. Out of scope: the decisions T1 to T11 the brief prepares for the owner; the version bump and the `CHANGELOG.md` entry, which the release pass writes.

## 3. User Goal
- Primary user: the owner running a plant, and the lead session inside it
- Primary outcome: token use is visible per spawn, and the method's machinery spends fewer turns on work that needs no judgment
- Job to be done: read the tokens each spawn used, keep a resume from rewriting a cold cache, place the cache-lifetime setting when it pays
- Acceptance criteria (link to spec §9): the SPEC-0005, SPEC-0006 and SPEC-0001 rows the 2026-11-10 changelog entries add
- Non-goals: measuring a saving; changing any default; any item of the brief's section 8

## 4. Operating Constraints
- Runtime constraints: bash 3.2 syntax in `install.sh`; stdlib Python at the 3.14 floor (SPEC-0005 §5); no new dependency
- Security constraints: hooks keep their failure model, an internal error allows the action
- Privacy constraints: no project name in any seed file, test or fixture; fixtures are synthetic
- Data constraints: the spawn log stays append-only; the token ledger is a sibling record keyed by `spawn_id`
- Cost constraints: the batch sizes of `delegation.effort-scale`; no two writers of one file in one wave
  - Plan approval (`grill.plan-approval`), skipped: the owner's brief of 2026-11-10 is the approved scope. Levers this plan uses: none defined (default)
  - Owner-only prerequisites: the release and its tag push wait for the owner's explicit go-ahead (`vcs-posture.publish-authorization`)
  - Scoped standing grant: none asked
- Latency constraints: none
- Compliance constraints: none
- Maintenance constraints: one home per fact; no growth of the kernel, the always-loaded surface or the canonical brief blocks

## 5. Research Summary
no external dependency — the seed's code gains no library, and no §9 row depends on a `docs/graph/libraries/` page. Host facts were checked against the Claude Code documentation on 2026-11-10 and are classed as verified, documented or inferred where they land.

## 6. Decisions Made
| Decision | Rationale | Evidence | Reversibility | ADR | Date |
|---|---|---|---|---|---|
| Tier T3 | the installer, a hook, a tool and three specs | kernel §0 | not applicable | none | 2026-11-10 |
| The token ledger is a mode of `brief.py`, the spawn log's one writer | no new script placed in a plant | SPEC-0005 `TOKEN_LEDGER_RECORDS_HOST_USAGE` | reversible | none | 2026-11-10 |
| The resume guard's contract lives in SPEC-0005 | the resume hook had no contract; SPEC-0005 owns the cycle economy and `delegation.continuation` | SPEC-0005 changelog of 2026-11-09 | reversible | none | 2026-11-10 |
| Where the guard cannot tell the lifetime, it assumes five minutes | refusing a warm resume costs a fresh brief; allowing a cold one rewrites the whole context | the brief's section 7, E2 | reversible | none | 2026-11-10 |

## 7. Options Considered
| Option | Benefits | Costs | Risks | Outcome |
|---|---|---|---|---|
| A separate ledger script placed in a plant | one tool per job | a new placed script, manifest row and write site | two writers beside the spawn log | Rejected: a mode of `brief.py` |
| A resume guard that assumes one hour when unset | fewer refusals | a cold resume rewrites the whole context | the brief names it an anti-pattern | Rejected |

## 8. Architecture Plan
- System boundary: unchanged
- Main components: the token ledger beside the spawn log; the resume guard's lifetime resolution; the installer's cache-lifetime opt-in
- Interfaces: `brief.py --tokens SPAWN_ID --usage FILE|-` or `--transcript PATH`; the resume hook's stdin contract is unchanged
- Data flow: `docs/graph/plans/tokens.jsonl` beside `spawns.jsonl`
- Error handling: the hooks fail open; the ledger refuses an unlogged or repeated spawn id with exit 2
- Observability: the delivery's optional Tokens line
- Security posture: unchanged
- Deployment model: new plants at install; existing plants at their next graft
- Environment parity: unchanged

## 9. Implementation Plan

Increments are inline; numbers are dependency order. Increment 1 carries the contracts of SPEC-0001, SPEC-0005 and SPEC-0006 this round leaves as they were. Rolling back the round is reverting its commits on the work branch; an increment's own rollback restores its files from `ce0d12c`.

| # | Subject | Status |
|---|---|---|
| 1 | carried | done |
| 2 | E1 token ledger | done |
| 3 | E2 resume guard follows the configured cache lifetime | done |
| 4 | E3 cache-lifetime settings documented and placed on opt-in | done |
| 5 | E4 cycle driver | done |

### Increment 1: Carried: the contracts this round leaves as they were
- Spec contracts: SPEC-0001/ADAPTERS_ACCUMULATE, SPEC-0001/ALL_CHECK_INCLUDES_RECORDED_COPILOT, SPEC-0001/ALL_EXCLUDES_LEGACY_HOSTS, SPEC-0001/ALL_NAMES_SKIPPED_FROZEN_HOSTS, SPEC-0001/BACKUPS_LISTED_BY_DATE, SPEC-0001/BACKUP_BEFORE_REPLACE, SPEC-0001/CHECK_EXECUTES_EACH_WIRED_HOOK, SPEC-0001/CHECK_FLAGS_ORPHAN_HARNESS_ENTRY, SPEC-0001/CHECK_FLAGS_RETIRED_GRAPH_NODE, SPEC-0001/CHECK_FLAGS_RETIRED_HARNESS_ENTRY, SPEC-0001/CHECK_WITHOUT_COPILOT_SAYS_SO, SPEC-0001/CITED_PACKAGE_PROPOSES_NOTHING, SPEC-0001/CODE_ANCHOR_TOOL_IS_PLACED, SPEC-0001/COPY_MODE_ISOLATES, SPEC-0001/CORPUS_IS_WHOLE_OR_ABSENT, SPEC-0001/DECISIONS_SURVIVE_SILENCE, SPEC-0001/ENGINE_AUDIT_CHECKS_EVERY_PAIR, SPEC-0001/ENGINE_RECONCILE_PICKS_CONFIG_BY_ENGINE, SPEC-0001/EVERY_BACKUP_IS_CLASSIFIABLE, SPEC-0001/EXISTING_PLANT_RECEIVES_CURRENT_ENGINES, SPEC-0001/EXPERTISE_CHECK_NAMES_MISSING_OR_STALE, SPEC-0001/EXPERTISE_IS_RECORDED_IN_THE_STAMP, SPEC-0001/EXPERTISE_PLACES_ONLY_THE_CONFIRMED_LIST, SPEC-0001/EXPERTISE_PROPOSAL_WRITES_NOTHING, SPEC-0001/EXPERTISE_SURVIVES_SILENCE, SPEC-0001/FORCE_SUPPRESSES_WARNING_NOT_BACKUP, SPEC-0001/GRAFT_RUN_NAMES_PLAN_DEFECTS_THE_UPGRADE_RAISES, SPEC-0001/GRAFT_RUN_RECREATED_LEAVES_OUT_SEED_NEW, SPEC-0001/GRAFT_RUN_TIES_LINT_ERRORS_TO_RETIRED_NODES, SPEC-0001/HARVEST_CANDIDATE_FORM_IS_PLACED, SPEC-0001/HOOKS_RUN_ON_THE_FLOOR_INTERPRETER, SPEC-0001/HOST_TIERS_AGREE, SPEC-0001/HUB_KEPT_CANONICAL_IN_COMPOSE_MODE, SPEC-0001/IDENTICAL_RERUN_IS_INERT, SPEC-0001/INSTALL_KEEPS_DIVERGED_MACHINERY, SPEC-0001/JURISDICTION_RESOLVED_ONCE, SPEC-0001/LANGUAGE_DECLARATION_PROPOSES_ITS_PAGE, SPEC-0001/LEGACY_INSTALL_PRINTS_DEPRECATED, SPEC-0001/LEGACY_INSTALL_STILL_SUCCEEDS, SPEC-0001/MODEL_MAP_TEMPLATE_IS_PLACED, SPEC-0001/ONE_KERNEL_BODY, SPEC-0001/OPENCODE_CHECK_DETECTS_DRIFT, SPEC-0001/OPENCODE_MAP_UNREADABLE_FAILS_CLOSED, SPEC-0001/OPENCODE_MODEL_FROM_MAP, SPEC-0001/OPENCODE_NO_MAP_ROW_NO_MODEL_LINE, SPEC-0001/OWN_PACKAGE_LIST_PROPOSES_ITS_PAGE, SPEC-0001/PACKAGELESS_PAGE_PROPOSED_BY_ITS_TRIGGER, SPEC-0001/PLACED_CORPUS_PAGE_IS_REACHABLE, SPEC-0001/PLACED_PAGE_CARRIES_ITS_PROVENANCE, SPEC-0001/PLACED_SKILL_IS_A_ROUTABLE_NODE, SPEC-0001/PLANT_EDITED_PAGE_IS_LEFT_AND_NAMED, SPEC-0001/PLANT_OWNED_PAGE_IS_NEVER_REPLACED, SPEC-0001/PREFLIGHT_REFUSES_BEFORE_WRITING, SPEC-0001/PREFLIGHT_SCOPED_TO_WRITTEN_TREES, SPEC-0001/PRE_GROWTH_POINTER_LIVES_IN_THE_PLACEHOLDER_INDEX, SPEC-0001/PRIME_HOOK_SCRIPTS_ARE_PLACED, SPEC-0001/PRISTINE_PRIOR_KERNEL_IS_NOT_MIGRATION, SPEC-0001/RECORD_AGREES_WITH_DISK, SPEC-0001/RECREATED_LIST_IS_COMPLETE, SPEC-0001/REINSTALL_ENGINE_SERVES_THE_HOOKS, SPEC-0001/RETIRED_STAMP_KEYS_NAMED_AND_KEPT, SPEC-0001/SEED_ONLY_FILES_NEVER_PLACED, SPEC-0001/SESSION_RECORD_FORM_IS_PLACED, SPEC-0001/SINGLE_WRITER, SPEC-0001/STAMP_TRACKING_LINES_PRINTED, SPEC-0001/SYMLINK_IS_REPLACED_NOT_FOLLOWED, SPEC-0001/SYMLINK_MODE_IS_UNIFORM, SPEC-0001/UNKNOWN_EXPERTISE_ID_REFUSED_BEFORE_WRITING, SPEC-0001/UNKNOWN_STAMP_KEYS_SURVIVE, SPEC-0005/ADOPTED_RULES_NOT_PENDING, SPEC-0005/ADOPTED_RULE_HOMES, SPEC-0005/AGENTS_RECOMPOSE_FROM_THE_NODES_ON_DISK, SPEC-0005/AGENT_DECLARES_EFFORT, SPEC-0005/AGENT_DECLARES_MODEL_CLASS, SPEC-0005/ALWAYS_LOADS_COMPOSES_ONLY_WHAT_THE_ROLE_NEEDS, SPEC-0005/BOOTSTRAP_STEP2_LOADS_A_MENU, SPEC-0005/BRIEF_DERIVES_THE_SPAWN_EFFORT, SPEC-0005/BRIEF_WARNS_ON_A_ROUTE_WITHOUT_EXPERTISE, SPEC-0005/CHARTER_FLAG_ONLY_FOR_PRIME_AGENT, SPEC-0005/DELEGATION_LEAVES_ROUTE, SPEC-0005/DELEGATION_SPLIT_INTO_SIBLINGS, SPEC-0005/GRILL_BATCHES_FOLLOW_THE_EFFORT_TABLE, SPEC-0005/GRILL_WAVES_LEAVES_THE_GATE_UNCHANGED, SPEC-0005/GRILL_WAVES_LEVELS_FROM_DEPENDS_ON, SPEC-0005/GRILL_WAVES_NOT_COMPUTED_ON_DEPENDENCY_DEFECT, SPEC-0005/GRILL_WAVES_OVERLAP_IS_A_WARNING, SPEC-0005/GRILL_WAVES_UNSCHEDULED_WITHOUT_PHASE, SPEC-0005/HANDBACK_STARTS_AT_STATUS, SPEC-0005/IMPLEMENTER_WRITES_A_DESIGN_NOTE, SPEC-0005/KERNEL_POINTS_AT_THE_SESSION_RECORD, SPEC-0005/LEAF_BODY_CEILING_HELD, SPEC-0005/LISTED_NODE_EDGES_REACH, SPEC-0005/MAIN_SESSION_PLAYS_THE_ORCHESTRATOR, SPEC-0005/PLAN_INFERS_EXPERTISE_FROM_NAMED_FILES, SPEC-0005/PLAN_ROLE_LEAVES_OUT_THE_ROLES_OWN_PROMPT, SPEC-0005/RED_TEST_HOLDS_ITS_EVIDENCE, SPEC-0005/REVIEWER_CHECKS_STATE_AND_PLATFORM, SPEC-0005/REVIEWER_RUNS_NO_BUILD, SPEC-0005/REVIEW_BRIEF_NAMES_THE_SECURITY_PASS, SPEC-0005/ROLE_AGENT_COMPOSES_ITS_ALWAYS_LOADED_NODES, SPEC-0005/SECURITY_CONTRACTS_CARRY_ADVERSARIAL_RED_CONTROLS, SPEC-0005/SESSION_RECORD_FORM_IS_NOT_A_SCAFFOLD, SPEC-0005/SPAWN_LOG_RECORDS_THE_ATTRIBUTION, SPEC-0005/TRUST_MARKER_IS_SETTLED, SPEC-0005/TRUST_PATH_TAKES_THE_SECURITY_PASS, SPEC-0006/METRICS_ALL_REPORTS_EVERY_ENTRY, SPEC-0006/METRICS_BLOCK_MISSING_FAILS, SPEC-0006/METRICS_COMPACT_ENTRY_EXEMPT, SPEC-0006/METRICS_DATED_HEADING_ENDS_ENTRY, SPEC-0006/METRICS_DELIVER_NODE_UNPARSEABLE_FAILS_LOUD, SPEC-0006/METRICS_ENTRIES_BEFORE_SINCE_NOT_JUDGED, SPEC-0006/METRICS_ENTRY_HEADINGS_RECOGNIZED, SPEC-0006/METRICS_FILLED_ENTRY_PASSES, SPEC-0006/METRICS_LABELS_FROM_DELIVER_NODE, SPEC-0006/METRICS_LEADING_BOM_IGNORED, SPEC-0006/METRICS_LINES_COUNTED_AS_GREP_DOES, SPEC-0006/METRICS_LINE_EMPTY_FAILS, SPEC-0006/METRICS_LINE_MISSING_FAILS, SPEC-0006/METRICS_LOW_TIER_EXEMPT, SPEC-0006/METRICS_MISSING_CHANGELOG_FAILS, SPEC-0006/METRICS_NOT_RECORDED_WITHOUT_REASON_FAILS, SPEC-0006/METRICS_NOT_RECORDED_WITH_REASON_IS_FILLED, SPEC-0006/METRICS_NO_ENTRY_SINCE_FAILS, SPEC-0006/METRICS_OTHER_ENTRY_DEFECT_IS_A_NOTE, SPEC-0006/METRICS_READER_RUNS_IN_A_FRESH_PLANT, SPEC-0006/METRICS_SECTION_HEADINGS_STAY_IN_ENTRY, SPEC-0006/METRICS_SHIPPED_DELIVER_NODE_PARSES, SPEC-0006/METRICS_SINCE_REQUIRED, SPEC-0006/METRICS_UNREADABLE_CHANGELOG_FAILS_LOUD, SPEC-0006/METRICS_ZERO_ENTRIES_ARE_NAMED
- Files touched: none
- Tests to write (RED): none: implemented and green at `ce0d12c` under earlier plans
- Behavior added: none
- Gate: their §10 rows stay green in the round's full gate
- Rollback path: none needed
- Effort: low
- Phase: GREEN
- Depends on: none

### Increment 2: E1 token ledger
- Spec contracts: SPEC-0005/TOKEN_LEDGER_RECORDS_HOST_USAGE, SPEC-0005/TOKEN_LEDGER_READS_A_CLAUDE_CODE_TRANSCRIPT, SPEC-0006/METRICS_OPTIONAL_LINE_MAY_BE_ABSENT, SPEC-0006/METRICS_TOKENS_LINE_READ
- Files touched: `tools/brief.py`, `tools/session-metrics.py`, `protocols/deliver.md`, `tests/test-brief.sh`, `tests/test-session-metrics.sh`, `docs/specs/SPEC-0005-cycle-economy.md`, `docs/specs/SPEC-0006-session-metrics.md`
- Tests to write (RED): X505, X506 in `tests/test-brief.sh`; X504 in `tests/test-session-metrics.sh`; each seen red first
- Behavior added: `brief.py --tokens` records host-reported tokens per spawn, or `not recorded`; the delivery may carry a Tokens line
- Gate: `bash tests/test-brief.sh`, `bash tests/test-session-metrics.sh`
- Rollback path: restore the files touched from `ce0d12c`
- Effort: medium
- Phase: GREEN
- Depends on: increment 1

### Increment 3: E2 resume guard follows the configured cache lifetime
- Spec contracts: SPEC-0005/RESUME_GUARD_FOLLOWS_THE_CONFIGURED_CACHE_LIFETIME
- Files touched: `integrations/claude-code/resume-hook.py`, `integrations/claude-code/settings.json` (the hook's comment only; the wiring is unchanged), `core/method/delegation-continuation.md`, `tests/test-resume-hook.sh`, `docs/specs/SPEC-0005-cycle-economy.md`
- Tests to write (RED): X507 in `tests/test-resume-hook.sh`: fixture transcripts idle 4, 30 and 90 minutes against a lifetime of 5m, 1h, an invalid value and none, through each source and each precedence step; seen red first (seven cases refused a 30-minute worker under a one-hour lifetime)
- Behavior added: the guard refuses a resume past the configured worker lifetime, 300 seconds when it cannot tell
- Gate: `bash tests/test-resume-hook.sh`
- Rollback path: restore the files touched from `ce0d12c`
- Effort: low
- Phase: GREEN
- Depends on: increment 2

### Increment 4: E3 cache-lifetime settings documented and placed on opt-in
- Spec contracts: SPEC-0001/LEAD_CACHE_TTL_IS_PLACED_ONLY_ON_OPT_IN
- Files touched: `install.sh` (`--prompt-cache-ttl 1h|default`, the stamp key `prompt_cache_ttl`), `integrations/claude-code/README.md`, `documentation/host-capability-matrix.md`, `tests/test-install-placement.sh`, `docs/specs/SPEC-0001-install-placement.md`
- Tests to write (RED): M26 in `tests/test-install-placement.sh`: install with and without the opt-in, a silent re-run, `default`, an invalid value, `--check` in each state; seen red first (the installer refused the unknown option)
- Behavior added: the lead's one-hour prompt-cache setting is written only on the owner's opt-in; the default install writes nothing new; the Claude Code README states the defaults, controls, precedence, version requirements and rule of thumb
- Gate: `bash tests/test-install-placement.sh`
- Rollback path: restore the files touched from `ce0d12c`
- Effort: low
- Phase: GREEN
- Depends on: increment 3

### Increment 5: E4 cycle driver
- Spec contracts: SPEC-0005/CYCLE_DRIVER_PRINTS_THE_CYCLE_STATE, SPEC-0005/CYCLE_DRIVER_NAMES_THE_HOLD_CONDITION, SPEC-0005/CYCLE_DRIVER_CHECKS_THE_RED_HASHES, SPEC-0005/CYCLE_DRIVER_REFUSES_MALFORMED_INPUT, SPEC-0005/CYCLE_DRIVER_IS_DETERMINISTIC_AND_READ_ONLY, SPEC-0005/CYCLE_DRIVER_RECORDS_ATOMICALLY, SPEC-0005/CYCLE_DRIVER_RUNS_IN_A_FRESH_PLANT
- Files touched: `tools/cycle.py`, `templates/knowledge-graph/grill-lint.py` (`plan_graph` and `pack` taken out of `main` and `batch_report`, output unchanged), `install.sh`, `manifest.json`, `tests/test-cycle.sh`, `tests/fixtures/cycle/`, `tests/run.sh`, `tools/gate-registry.py`, `core/method/delegation-cycle-economy.md`, `core/method/delegation-sequencing.md`, `protocols/test-first.md`, `docs/specs/SPEC-0005-cycle-economy.md`
- Tests to write (RED): X508 to X514 in `tests/test-cycle.sh`: an empty cycle, a RED wave ready, a held increment under each of the three conditions, a hash mismatch, a malformed record, byte-identical output on two runs, the record writer, the placed tool in a fresh plant; seen red first
- Behavior added: one read prints the ready batches, what is in flight or waits on a live lane, the held increments with their condition, the expected-red list, the `not run` ids, RED-hash mismatches and whether a ruling pass is owed; two explicit subcommands write the batch record
- Gate: `bash tests/test-cycle.sh`, `bash tests/test-grill-lint.sh`, `bash tests/test-tool-help.sh`, `python3 tests/seed-lint.py`
- Rollback path: restore the files touched from `77bbf6c` and delete `tools/cycle.py`, `tests/test-cycle.sh` and `tests/fixtures/cycle/`
- Effort: medium
- Phase: GREEN
- Depends on: increment 4

### Increment 6: E5 generated delivery lines
- Spec contracts: SPEC-0005/BRIEF_LOG_PRINTS_THE_DERIVABLE_METRICS
- Files touched: `tools/brief.py`, `tests/test-brief.sh`, `tests/fixtures/brief-log/`, `protocols/deliver.md`, `docs/specs/SPEC-0005-cycle-economy.md`
- Tests to write (RED): X515 in `tests/test-brief.sh`: a hand spawn log and ledger print `tests/fixtures/brief-log/log.out`; the three lines pass `session-metrics.py`; no ledger, a broken ledger line and an empty log; seen red first
- Behavior added: `brief.py --log` also prints the Spawns, Serial waits and Tokens lines of the Session metrics block
- Gate: `bash tests/test-brief.sh`, `bash tests/test-session-metrics.sh`, `python3 tests/seed-lint.py`
- Rollback path: revert the increment's commit
- Effort: medium-low
- Phase: GREEN
- Depends on: increment 5

### Increment 7: E6 batch-size notice at brief time
- Spec contracts: SPEC-0005/BRIEF_NOTICES_AN_UNDERSIZED_BATCH
- Files touched: `tools/brief.py`, `tests/test-brief.sh`, `core/method/delegation-cycle-economy.md`, `docs/specs/SPEC-0005-cycle-economy.md`
- Tests to write (RED): X516 in `tests/test-brief.sh`: an undersized batch with more ready, an exact batch, a security and a concurrency batch of one, a wave with nothing else ready, an unknown increment; seen red first
- Behavior added: `brief.py --increments N[,N] --unit U` prints one notice and logs it when the batch is smaller than the table gives while more of its phase is ready; never a refusal
- Gate: `bash tests/test-brief.sh`, `bash tests/test-cycle.sh`, `python3 tests/seed-lint.py`
- Rollback path: revert the increment's commit
- Effort: medium-low
- Phase: GREEN
- Depends on: increment 6

### Increment 8: E7 slow-command and gate-output rules in their homes
- Spec contracts: SPEC-0005/SLOW_COMMAND_LEAVES_THE_WORKER_TURN, SPEC-0005/GATE_OUTPUT_KEEPS_STATUS_AND_LOG
- Files touched: `core/method/bounded-execution.md`, `agents/03-reviewer.md`, `protocols/verify.md`, `tests/seed-lint.py`, `docs/specs/SPEC-0005-cycle-economy.md`
- Tests to write (RED): two `TEXT_RULES` rows in `tests/seed-lint.py` that require each sentence in its home and the reviewer's pointer, and two that forbid the rule in the kernel, the orchestrator's always-loaded nodes and the canonical brief blocks; seen red first
- Behavior added: a command expected to outlast the worker's cache lifetime leaves the worker's turn; a gate returns failing ids and a summary, keeps its exit status and leaves the full log on disk
- Gate: `python3 tests/seed-lint.py`
- Rollback path: revert the increment's commit
- Effort: low
- Phase: GREEN
- Depends on: increment 7

### Increment 9: E8 model class per role and task kind
- Spec contracts: SPEC-0005/BRIEF_DERIVES_THE_MODEL_CLASS
- Files touched: `tools/brief.py`, `tests/test-brief.sh`, `tests/fixtures/brief-class/before.sha256`, `core/method/delegation-model-classes.md`, `core/method/delegation-light-variants.md`, `core/method/delegation.md`, `templates/agent.template.md`, `manifest.json`, `tests/seed-lint.py`, `DOCUMENTATION.md`, `docs/specs/SPEC-0005-cycle-economy.md`
- Tests to write (RED): X517 in `tests/test-brief.sh`: every role and kind of the effort table composes the brief and stderr whose hashes were captured from the prior tip, and a class row changed to another class adds one `Model:` line; seen red first
- Behavior added: a class table beside the effort table, read by the same loader, gives each role and kind the role's `model:`; `brief.py` prints a class only where a row differs. The table pushed `delegation-model-classes.md` past the 170-line leaf ceiling, so its light-variants section moved verbatim to the sibling leaf `delegation-light-variants.md`
- Gate: `bash tests/test-brief.sh`, `python3 tests/seed-lint.py`, `python3 tests/test_graph_lint.py`
- Rollback path: revert the increment's commit
- Effort: medium-low
- Phase: GREEN
- Depends on: increment 8

**Delegation and parallelism.** The static schedule is `python3 templates/knowledge-graph/grill-lint.py --plan docs/plans/grill-8.3.1-token-efficiency.md --specs docs/specs --decisions docs/decisions --waves`. A file two increments write (`docs/specs/SPEC-0005-cycle-economy.md`) is ordered by `Depends on:`.

## 10. Verification Plan
The standard gate holds (`CLAUDE.md` Gates: `bash tests/run.sh`), on an interpreter at the 3.14 floor. Each mechanism also re-measures the three byte figures against the baseline taken before the round.

## 11. Risks and Mitigations
| Risk | Probability | Impact | Mitigation | Owner | Verification | Refutation |
|---|---:|---:|---|---|---|---|
| A mechanism grows what every session pays for | medium | high | measure the kernel, always-loaded and brief-block bytes before and after each slice | the steward | `tests/seed-lint.py` and the per-slice figures | `could-not-refute`, the top risk, devils-advocate press of 2026-11-10 (press note below) |
| A recorded token count is estimated, not host-reported | low | high | the ledger stores `not recorded` for anything the host did not report | tester | X505, X506 | not pressed |
| The resume guard assumes a lifetime longer than the host's | low | medium | an unreadable or invalid control resolves to 300 seconds | tester | `tests/test-resume-hook.sh` | `refuted` as mitigated, devils-advocate press of 2026-11-10 (press note below; §12 rows 3 and 4) |

**Press note (devils-advocate, 2026-11-10).** The press took the top risk by probability × impact (row 1) and row 3, which holds the strongest defeater it found. It read primary sources only: the round's diff against `ce0d12c`, `eager_surfaces` from `tests/seed-lint.py` run on both trees, the round's code, and the Claude Code prompt-caching page read on 2026-11-10.
- Row 1, `could-not-refute`. The kernel measures 7049 bytes and the always-loaded figures (claude-code 67131, opencode 24207, codex 24207, prime-agent 18466, github-copilot 29851) are equal at `ce0d12c` and at the round's head. No file under `agents/`, `skills/`, `templates/` or `core/AGENTS.md` changed; `core/method/delegation-continuation.md`, the one always-loaded node the round edits, is 4088 bytes before and after; `tools/brief.py` only gains lines. What the three figures leave out is cost paid per use: `protocols/deliver.md` grows from 13517 to 13831 bytes, read at each delivery, and the ledger costs the lead one `brief.py --tokens` call per spawn. Neither is paid by every session, and neither is a default.
- Row 3, `refuted` as mitigated. The mitigation covers an unreadable or invalid control. A readable, valid `1h` that the host does not honour is left out, and there the guard now lets through a resume idle for up to 60 minutes into a cache the host let expire at five, which it refused before the round. The page documents four such cases: a host older than v2.1.242, the floor it names for both settings and both variables; a `subagentPromptCacheTtl` in managed settings, which the page says can set the lifetime and the hook does not read; a provider or gateway where the one-hour lifetime is unavailable or its header is dropped; and `ENABLE_PROMPT_CACHING_1H`, documented as `=1`, which the hook takes as on for any value other than empty, `0`, `false`, `no` or `off`. A default install sets no worker control, so a default plant behaves as before; only a plant whose owner set a worker `1h` is exposed. The hook docstring's sentence that the guard never assumes a warm cache it cannot prove is overstated for the same cases.
- Outside the table, `stale`: the Claude Code README and this plan's increment-3 changelog line say the pages read did not document `FORCE_PROMPT_CACHING_5M` and `ENABLE_PROMPT_CACHING_1H`; the prompt-caching page documents both, as steps 1 and 5 of the precedence. The README's Defaults bullet and the capability-matrix row leave out the lead's default lifetime (one hour on a subscription within plan usage; five minutes on usage credits, an API key or a cloud provider), which E3's acceptance asks them to state (§12 row 5).
- `could-not-refute`: no default changes (without `--prompt-cache-ttl` the installer takes the unchanged `place_hook` path and writes no stamp key), and no price or multiplier is stored.
- Blind spot: the press did not run the full gate, did not read the settings-reference, managed-settings or pricing pages, did not test the transcript reader on a real record, and covers increments 1 to 4 only; E4 to E8 take their own press when they land.

## 12. Open Questions
| # | Question | Why it matters | Current assumption | How to resolve | Owner | Pinned by |
|---:|---|---|---|---|---|---|
| 1 | Is the round's version 8.3.1 or another? | the plan's name and the release notes | 8.3.1 | the release pass | owner | none |
| 2 | `install.sh --check` does not name a missing resume or bound hook script | a plant can lose its guard silently | left as is this round; the hook wiring is not changed | a later round | owner | none |
| 3 | Should the resume guard count a worker `1h` only where it can confirm the host honours it, and take 300 seconds otherwise? | the devils-advocate press of 2026-11-10 refuted §11 row 3's mitigation: a valid `1h` the host ignores lets a cold resume through for up to an hour | resolved 2026-11-10 by the round brief's anti-pattern "a resume guard that assumes a long cache lifetime when it cannot tell", not by the owner: a resolved `1h` counts only when the worker's transcript shows the host's latest cache write was a one-hour one, else 300 seconds | X507 cases: a 5m-only last write, a one-hour last write, no creation tokens | brief | `tests/test-resume-hook.sh` |
| 4 | Should the guard read managed settings, or take 300 seconds for a project or user `subagentPromptCacheTtl: 1h` whenever a managed settings file exists? | managed settings outrank the files the hook reads, and the prompt-caching page says they can set the lifetime | managed settings are not read | the owner's decision, then a RED case in `tests/test-resume-hook.sh` | owner | none |
| 5 | Should the Claude Code README and the capability matrix state the lead's default lifetime and record the force and enable variables as documented, with a new §15 line correcting increment 3's classification? | the prompt-caching page read on 2026-11-10 documents both variables, and E3's acceptance asks the docs to state the lead default | resolved 2026-11-10 by the round brief's E3 acceptance: both documents state the lead default and the two variables as documented, "Set to `1`" | the env-vars and prompt-caching pages, read 2026-11-10 | brief | `tests/test-resume-hook.sh` |
| 6 | Should the token ledger record every logged spawn of a delivery in one call, so the lead spends one call per delivery instead of one per spawn? | `brief.py --tokens` takes one spawn per call, a lead tool call each | one call per spawn | E5's interface step | owner | none |

Row 4 stays open for the owner.

Row 6 stays open for the owner.

## 13. Done Criteria
- Every increment in §9 is done; each new contract has a `green` §10 row in its spec.
- `grill-lint.py` lints this plan from `tests/run.sh` and passes.
- `bash tests/run.sh` is green on the floor interpreter.
- The three byte figures are not above the baseline.

## 14. Recommended Next Step
Land the next mechanism's increment, then run the release pass, `docs/skills/seed-release.md`; the tag push waits for the owner's explicit go-ahead.

## 15. Changelog
- 2026-11-10: plan opened as the record of round 8.3.1, built on the 8.3.0 experimental line. `tests/run.sh` `ACTIVE_PLAN` moves here from the 8.2.0 plan, so the gate holds the contracts this round adds. Increments 1 to 3 written; E3 to E8 append their own.
- 2026-11-10: increment 3 (E2) landed: the resume guard resolves the configured worker cache lifetime, 300 seconds when it cannot tell. A frontmatter `1h` resolves to 300 seconds, because the host ignores it on usage credits and a hook cannot see the billing state; the two force and enable variables are honoured on the owner's account, which the documentation pages read did not confirm.
- 2026-11-10: increment 4 (E3) landed: `--prompt-cache-ttl 1h` places the lead setting and the stamp keeps it; the documentation carries no cost multiplier, since the pages read state none.
- 2026-11-10: devils-advocate press (`grill.press`) on the top risk and on §11 row 3: row 1 `could-not-refute`, row 3 `refuted` as mitigated; the changes it calls for are §12 rows 3 to 6, held for the owner and not made.
- 2026-11-10: §12 row 3 resolved by the round brief's anti-pattern against a resume guard that assumes a long cache lifetime when it cannot tell, not by the owner: the guard counts a resolved `1h` only when the worker's transcript shows the host's latest cache write was a one-hour one (X507, new cases seen red first). §11 row 3's refutation is answered for the four cases the press named, since each leaves a 5m-only write or none.
- 2026-11-10: §12 row 5 resolved by E3's acceptance: the Claude Code environment-variables and prompt-caching pages, read 2026-11-10, document `FORCE_PROMPT_CACHING_5M` and `ENABLE_PROMPT_CACHING_1H`, each set to `1`; increment 3's line that the pages read did not document them is superseded. The README and the capability matrix state the lead default; the hook counts the enable variable only at `1` (X507 case seen red first).
- 2026-11-10: increment 5 (E4) landed: `cycle.py` prints the state of a build cycle from the plan, the spawn log, the batch record, the question files and git, and writes only through `record-red` and `record-tip`. The batch record's location and line format now live in `delegation.green-self-test`. A commit counts an increment as committed when its message names it, so `test-first.cycle`'s commit message names the increment.
- 2026-11-10: increments 6 (E5) and 7 (E6) landed: `brief.py --log` prints the Spawns, Serial waits and Tokens lines from the spawn log and the ledger, and `brief.py --increments N --unit U` notices an undersized batch and logs the notice. The spawn log holds composition time only, so a serial wait is read as a gap of more than 60 seconds between two compositions.
- 2026-11-10: increment 8 (E7) landed: the slow-command rule joins clause 2 of `toolcraft.bounded-execution`, which now also holds that a reviewer runs no build, and the reviewer charter points there; the gate-output rule joins `protocols/verify.md` beside the line-cap sentence. The kernel, the always-loaded figures and the brief blocks are unchanged.
- 2026-11-10: increment 9 (E8) landed: a model-class table beside the effort table reproduces each role's `model:`, and `brief.py` prints a class only where a row differs; every brief composes byte for byte as before. The light-variants section moved verbatim to its own leaf to keep `delegation-model-classes.md` under the leaf ceiling.
