# grill.md: Plan of Record: round 8.3.2, fixes from the independent review

## 0. Metadata
- Project: CYPRESS seed
- Feature or goal: land the defects an independent review confirmed in the installer, the hooks, the source index, the test suite and the front door, requirements R1 to R8 of the owner's brief of 2026-11-10, and prepare the seven decisions D1 to D7 for the owner
- Date: 2026-11-10
- Owner: the steward
- Tier: T3. Protocol: `protocol.grill` for the increments; this plan is the record of what lands and why
- Current phase: increments 1 to 7 are done; the version and changelog are written by the release pass
- Related files: `integrations/claude-code/settings.json`, `integrations/claude-code/bound-hook.py`, `integrations/claude-code/resume-hook.py`, `integrations/claude-code/README.md`, `install.sh`, `tools/source_paths.py`, `templates/knowledge-graph/source_paths.py`, `tests/seed-lint.py`, `tests/test-install-placement.sh`, `tests/test-source-index.sh`, `tests/test-bound-hook.sh`, `tests/test-lint-audibility.sh`, `tests/test-install-adoption.sh`, `tests/test-seed-lint.sh`, `tests/test-prompt-hooks.sh`, `README.md`, `tests/run.sh`
- Related documentation: `docs/plans/grill-8.3.1-token-efficiency.md` (the previous plan the gate linted); `docs/skills/seed-release.md` (the release pass that follows this plan)
- Related ADRs: [ADR-0009](../decisions/adr-0009-host-support-tiers.md) (the frozen hosts, which this round leaves unchanged)
- Related specs: [SPEC-0001](../specs/SPEC-0001-install-placement.md) (the guard wiring, `--check`, projection drift); [SPEC-0007](../specs/SPEC-0007-source-index.md) (the plant's code only); [SPEC-0004](../specs/SPEC-0004-front-door.md) (the cost row)
- Related libraries: none (stdlib Python and bash)
- Baseline: v8.3.1, the tagged release this round builds on

## 1. Artifact Discovery
Every line cites the paths it rests on. Each owner decision is stated in words with its date.
- Existing files inspected: `integrations/claude-code/settings.json` (the `PreToolUse` commands ran `python3 <script>` with no existence test); `install.sh` (`check_wired_hooks` ran only the `UserPromptSubmit` and `SessionStart` hooks; `check_claude_projections` compared agents and left skills unchecked; `project_skills`); `tools/source_paths.py` (`NOT_CODE`, `is_code`); `integrations/claude-code/bound-hook.py` (`BLOCKING_PRONE`); `README.md` (the cost table)
- Existing docs inspected: `docs/plans/grill-7.29.0-front-door/method-overhead-evidence.md` and the slice it cites; `docs/decisions/adr-0009-host-support-tiers.md`; `docs/skills/seed-release.md`; `docs/plans/owner-decisions-8.3.1-token-efficiency.md` (the shape of the decision notes)
- Existing tests inspected: `tests/test-install-placement.sh` (M12 `case_hook_check`); `tests/test-source-index.sh`; `tests/test-bound-hook.sh`; `tests/test-lint-audibility.sh`; `tests/test-install-adoption.sh` (`case_block_readonly`); `tests/test-seed-lint.sh`; `tests/test-prompt-hooks.sh` (X179)
- Existing specs inspected: `docs/specs/SPEC-0001-install-placement.md`, `SPEC-0004-front-door.md`, `SPEC-0007-source-index.md` (each one's `### Contract:` list)
- Existing architecture signals: the kernel, the always-loaded surface of each host and the canonical brief blocks may not grow (`tests/seed-lint.py`)
- Libraries already wikified: none, no library is a dependency of the seed's code
- External sources downloaded: none
- Constraints discovered: the installer's stamp `.cypress/seed.json` records the hosts, not the files placed, so the list of placed files cannot be derived from it; only the Claude Code adapter wires a `PreToolUse` guard (Codex and Copilot are frozen, Prime Agent and opencode wire none)

## 2. Shared Understanding
The owner's brief of 2026-11-10 asks for the confirmed defects of an independent review to be reproduced, fixed and tested, and for seven decisions that change a default to be prepared and not landed.

| Requirement | What it settles | Where it lands |
|---|---|---|
| R1, R2, R3 | a missing blocking-hook script no longer blocks the tool it guards; `--check` names it; the docstrings state the failure model | increment 2 |
| R4 | the source index inventories the plant's code only | increment 3 |
| R5 | `--check` flags a skill projection that differs from its node, with a remedy that keeps the node | increment 4 |
| R6 | two cases skip with a printed reason under uid 0 | increment 5 |
| R7 | the bound hook treats equivalent spellings of a blocked command alike | increment 6 |
| R8 | the README cost row states the whole measurement | increment 7 |

Success means: each requirement has a test seen red first and green, the full gate passes on the floor interpreter, and the three byte figures are not above the baseline. Out of scope: the decisions D1 to D7; tagging and pushing.

## 3. User Goal
- Primary user: the owner running a plant, and the steward releasing the seed
- Primary outcome: a hook script that goes missing degrades to a stated, detectable condition instead of blocking every tool call; the index and the front door describe what they claim to
- Job to be done: run `install.sh <host> --check` and learn every way the plant's wiring and projections have drifted
- Acceptance criteria (link to spec §9): the SPEC-0001, SPEC-0004 and SPEC-0007 rows the 2026-11-10 changelog entries add
- Non-goals: any redesign of the installer, the routers or the method; any default the owner set; the items of D1 to D7

## 4. Operating Constraints
- Runtime constraints: bash 3.2 syntax in `install.sh`; stdlib Python at the 3.14 floor; no new dependency
- Security constraints: a guard whose script is present blocks exactly what it blocked before, except the R7 additions; the context hooks stay fail-open
- Privacy constraints: no project, host-machine or path name from the working environment in any tracked file; fixtures are synthetic
- Data constraints: none
- Cost constraints: the batch sizes of `delegation.effort-scale`; no two writers of one file in one wave
  - Plan approval (`grill.plan-approval`), skipped: the owner's brief of 2026-11-10 is the approved scope. Levers this plan uses: none defined (default)
  - Owner-only prerequisites: the release and its tag push wait for the owner's explicit go-ahead (`vcs-posture.publish-authorization`)
  - Scoped standing grant: none asked
- Latency constraints: none
- Compliance constraints: none
- Maintenance constraints: one home per fact; no growth of the kernel, the always-loaded surface or the canonical brief blocks

## 5. Research Summary
no external dependency — the seed's code gains no library, and no §9 row depends on a `docs/graph/libraries/` page. Each defect was reproduced on this tree before its fix; the reproduction is in the increment's commit message.

## 6. Decisions Made
| Decision | Rationale | Evidence | Reversibility | ADR | Date |
|---|---|---|---|---|---|
| Tier T3 | the installer, hooks, the index and three specs | kernel §0 | not applicable | none | 2026-11-10 |
| The guard wiring tests the script's existence and passes its exit code through | `|| true` would turn the guard into a no-op; an absent script must not exit 2 | SPEC-0001 `BLOCKING_HOOK_WIRING_FAILS_OPEN_ON_A_MISSING_SCRIPT` | reversible | none | 2026-11-10 |
| The index excludes placed files by a list of exact paths | the stamp does not enumerate placed paths, and a directory prefix would hide a file the plant authored beside them | SPEC-0007 `SEED_PLACED_FILES_ARE_NOT_THE_PLANTS_CODE` | reversible | none | 2026-11-10 |
| Skill drift is reported, and `--recompose-agents` re-projects it | the pattern already used for composed agents; links in place of copies change a placement contract | SPEC-0001 `CHECK_FLAGS_A_DRIFTED_SKILL_PROJECTION` | reversible | none | 2026-11-10 |
| The release is a patch version, 8.3.2 | the base is the tagged v8.3.1 | `docs/skills/seed-release.md` | reversible | none | 2026-11-10 |

## 7. Options Considered
| Option | Benefits | Costs | Risks | Outcome |
|---|---|---|---|---|
| Append `|| true` to the guard commands | a missing script cannot block | exit 2 no longer blocks | the guard becomes a no-op | Rejected |
| Exclude `.claude/` and the other host directories from the index | one line | a file the plant authored there vanishes from the index | the index misses plant code | Rejected |
| Derive placed paths from the installer's record | no list to keep | the record does not list them | none available | Rejected: not enumerable |
| Replace projection copies with links | no drift possible | a placement contract changes on every host | breaks `--copy` mode | Rejected: drift is reported instead |

## 8. Architecture Plan
- System boundary: unchanged
- Main components: the `PreToolUse` commands in the Claude Code settings; `check_wired_hooks` and `check_claude_projections` in `install.sh`; `SEED_PLACED` beside `NOT_CODE` in the path-rule module
- Interfaces: `install.sh <host> --check` prints a `[seed] WARNING:` line per missing guard script and per drifted skill; `install.sh claude-code --recompose-agents` also re-projects skills
- Data flow: unchanged
- Error handling: a guard with its script absent exits 0 and prints one stderr line; a hook that raises inside allows
- Observability: the `--check` lines
- Security posture: unchanged; the guards block exactly what they blocked
- Deployment model: new plants at install; existing plants at their next graft
- Environment parity: the two root-sensitive cases skip with a printed reason where `chmod` denies nothing

## 9. Implementation Plan

Increments are inline; numbers are dependency order. Increment 1 carries the contracts of SPEC-0001, SPEC-0004 and SPEC-0007 this round leaves as they were. Rolling back the round is reverting its commits on the work branch; an increment's own rollback restores its files from `v8.3.1`.

| # | Subject | Status |
|---|---|---|
| 1 | carried | done |
| 2 | R1, R2, R3 guard wiring, check and docstrings | done |
| 3 | R4 the index inventories the plant's code only | done |
| 4 | R5 skill projection drift | done |
| 5 | R6 root-safe cases | done |
| 6 | R7 equivalent spellings in the bound hook | done |
| 7 | R8 the cost row | done |

### Increment 1: Carried: the contracts this round leaves as they were
- Spec contracts: SPEC-0001/SINGLE_WRITER, SPEC-0001/BACKUP_BEFORE_REPLACE, SPEC-0001/FORCE_SUPPRESSES_WARNING_NOT_BACKUP, SPEC-0001/SYMLINK_IS_REPLACED_NOT_FOLLOWED, SPEC-0001/IDENTICAL_RERUN_IS_INERT, SPEC-0001/EVERY_BACKUP_IS_CLASSIFIABLE, SPEC-0001/SYMLINK_MODE_IS_UNIFORM, SPEC-0001/COPY_MODE_ISOLATES, SPEC-0001/ONE_KERNEL_BODY, SPEC-0001/DECISIONS_SURVIVE_SILENCE, SPEC-0001/ADAPTERS_ACCUMULATE, SPEC-0001/RECORD_AGREES_WITH_DISK, SPEC-0001/CORPUS_IS_WHOLE_OR_ABSENT, SPEC-0001/PREFLIGHT_REFUSES_BEFORE_WRITING, SPEC-0001/PREFLIGHT_SCOPED_TO_WRITTEN_TREES, SPEC-0001/ALL_EXCLUDES_LEGACY_HOSTS, SPEC-0001/LEGACY_INSTALL_PRINTS_DEPRECATED, SPEC-0001/LEGACY_INSTALL_STILL_SUCCEEDS, SPEC-0001/ALL_NAMES_SKIPPED_FROZEN_HOSTS, SPEC-0001/CHECK_WITHOUT_COPILOT_SAYS_SO, SPEC-0001/ALL_CHECK_INCLUDES_RECORDED_COPILOT, SPEC-0001/HOST_TIERS_AGREE, SPEC-0001/SESSION_RECORD_FORM_IS_PLACED, SPEC-0001/HARVEST_CANDIDATE_FORM_IS_PLACED, SPEC-0001/ENGINE_RECONCILE_PICKS_CONFIG_BY_ENGINE, SPEC-0001/ENGINE_AUDIT_CHECKS_EVERY_PAIR, SPEC-0001/EXISTING_PLANT_RECEIVES_CURRENT_ENGINES, SPEC-0001/PRISTINE_PRIOR_KERNEL_IS_NOT_MIGRATION, SPEC-0001/RECREATED_LIST_IS_COMPLETE, SPEC-0001/UNKNOWN_STAMP_KEYS_SURVIVE, SPEC-0001/RETIRED_STAMP_KEYS_NAMED_AND_KEPT, SPEC-0001/LEAD_CACHE_TTL_IS_PLACED_ONLY_ON_OPT_IN, SPEC-0001/HOOKS_RUN_ON_THE_FLOOR_INTERPRETER, SPEC-0001/STAMP_TRACKING_LINES_PRINTED, SPEC-0001/BACKUPS_LISTED_BY_DATE, SPEC-0001/HUB_KEPT_CANONICAL_IN_COMPOSE_MODE, SPEC-0001/PRE_GROWTH_POINTER_LIVES_IN_THE_PLACEHOLDER_INDEX, SPEC-0001/CODE_ANCHOR_TOOL_IS_PLACED, SPEC-0001/MODEL_MAP_TEMPLATE_IS_PLACED, SPEC-0001/OPENCODE_MODEL_FROM_MAP, SPEC-0001/OPENCODE_NO_MAP_ROW_NO_MODEL_LINE, SPEC-0001/OPENCODE_MAP_UNREADABLE_FAILS_CLOSED, SPEC-0001/OPENCODE_CHECK_DETECTS_DRIFT, SPEC-0001/PRIME_HOOK_SCRIPTS_ARE_PLACED, SPEC-0001/REINSTALL_ENGINE_SERVES_THE_HOOKS, SPEC-0001/SEED_ONLY_FILES_NEVER_PLACED, SPEC-0001/EXPERTISE_PROPOSAL_WRITES_NOTHING, SPEC-0001/LANGUAGE_DECLARATION_PROPOSES_ITS_PAGE, SPEC-0001/OWN_PACKAGE_LIST_PROPOSES_ITS_PAGE, SPEC-0001/CITED_PACKAGE_PROPOSES_NOTHING, SPEC-0001/PACKAGELESS_PAGE_PROPOSED_BY_ITS_TRIGGER, SPEC-0001/EXPERTISE_PLACES_ONLY_THE_CONFIRMED_LIST, SPEC-0001/UNKNOWN_EXPERTISE_ID_REFUSED_BEFORE_WRITING, SPEC-0001/PLACED_PAGE_CARRIES_ITS_PROVENANCE, SPEC-0001/PLACED_SKILL_IS_A_ROUTABLE_NODE, SPEC-0001/PLACED_CORPUS_PAGE_IS_REACHABLE, SPEC-0001/EXPERTISE_IS_RECORDED_IN_THE_STAMP, SPEC-0001/EXPERTISE_SURVIVES_SILENCE, SPEC-0001/PLANT_EDITED_PAGE_IS_LEFT_AND_NAMED, SPEC-0001/PLANT_OWNED_PAGE_IS_NEVER_REPLACED, SPEC-0001/EXPERTISE_CHECK_NAMES_MISSING_OR_STALE, SPEC-0001/JURISDICTION_RESOLVED_ONCE, SPEC-0001/CHECK_EXECUTES_EACH_WIRED_HOOK, SPEC-0001/CHECK_FLAGS_RETIRED_HARNESS_ENTRY, SPEC-0001/CHECK_FLAGS_ORPHAN_HARNESS_ENTRY, SPEC-0001/CHECK_FLAGS_RETIRED_GRAPH_NODE, SPEC-0001/GRAFT_RUN_NAMES_PLAN_DEFECTS_THE_UPGRADE_RAISES, SPEC-0001/GRAFT_RUN_TIES_LINT_ERRORS_TO_RETIRED_NODES, SPEC-0001/INSTALL_KEEPS_DIVERGED_MACHINERY, SPEC-0001/GRAFT_RUN_RECREATED_LEAVES_OUT_SEED_NEW, SPEC-0004/INSTALL_SECTION_NAMES_TARGET_PATHS, SPEC-0004/GLOSSARY_PATHS_EXIST, SPEC-0004/MECHANISM_CLAIMS_TRACED, SPEC-0004/EAGER_FIGURES_CHECKED_WHEREVER_PUBLISHED, SPEC-0004/BODY_FIGURES_HAVE_A_REQUIRED_HOME, SPEC-0004/FRONT_DOOR_ANCHORS_RESOLVE, SPEC-0004/PROSE_FLOOR_HELD_PER_FILE, SPEC-0007/BUILD_INVENTORIES_THE_CODE_OF_EVERY_GOVERNED_REPOSITORY, SPEC-0007/BUILD_IS_DETERMINISTIC, SPEC-0007/CACHE_WRITTEN_SELF_IGNORED, SPEC-0007/CACHE_REUSED_WHILE_THE_KEY_HOLDS, SPEC-0007/CACHE_REBUILT_WHEN_THE_KEY_CHANGES, SPEC-0007/GRAFT_REBUILDS_THE_CACHE, SPEC-0007/LINK_PYTHON_IMPORT_CERTAIN, SPEC-0007/LINK_SHELL_INVOCATION_CERTAIN, SPEC-0007/LINK_PATH_LITERAL_AND_DIRECTORY_ARE_MAYBE, SPEC-0007/LINK_TS_SPECIFIER_CERTAIN, SPEC-0007/UNPINNED_REFERENCE_RECORDED_WITH_ITS_REASON, SPEC-0007/TESTS_ARE_THE_PLANTS_TEST_GLOBS, SPEC-0007/PLANT_CONFIG_REPLACES_EACH_DEFAULT_KEY, SPEC-0007/WALK_NEAREST_FIRST_ONCE, SPEC-0007/WALK_CHAIN_IS_ITS_WEAKEST_LINK, SPEC-0007/WALK_FLOOR_LISTED_APART_AFTER_THE_INPUT_ROWS, SPEC-0007/WALK_DELETED_INPUT_REACHES_ITS_NAMERS, SPEC-0007/INPUT_FORMS_RESOLVED, SPEC-0007/WALK_INCOMPLETE_NAMES_REASON_AND_ACTION, SPEC-0007/INPUT_IN_AN_UNREAD_LANGUAGE_IS_INCOMPLETE, SPEC-0007/ACTION_LINE_NAMES_AT_MOST_TEXT_MAX_ROWS_RECORDS, SPEC-0007/AFFECTED_TESTS_ARE_THE_WALK_FILTERED, SPEC-0007/AFFECTED_ALWAYS_RUN_LISTED_APART, SPEC-0007/TEST_REACHING_CODE_OVER_HTTP_IS_INCOMPLETE, SPEC-0007/ANCHORS_NAME_CITING_PAGES_OR_UNCITED, SPEC-0007/ANCHORS_BASENAME_IS_MAYBE_AMBIGUOUS_IS_INCOMPLETE, SPEC-0007/OUTPUT_CARRIES_NO_RAW_CONTROL, SPEC-0007/SOURCE_INDEX_IS_PLACED, SPEC-0007/SYMBOLS_PYTHON_DEFINITIONS_CERTAIN, SPEC-0007/SYMBOLS_LINE_READ_DECLARATIONS_ARE_MAYBE, SPEC-0007/SYMBOLS_LIST_EVERY_DEFINITION, SPEC-0007/SYMBOLS_UNREADABLE_FILE_MAKES_IT_INCOMPLETE, SPEC-0007/HISTORY_ROWS_ARE_MAYBE_WITH_THEIR_COUNT, SPEC-0007/HISTORY_ONLY_ADDS, SPEC-0007/HISTORY_SHALLOW_OR_MISSING_IS_INCOMPLETE, SPEC-0007/ANCHORS_MOVED_EQUALS_THE_NAMED_PATHS, SPEC-0007/ANCHORS_MOVED_WITHOUT_A_LIST_IS_INCOMPLETE, SPEC-0007/ANCHORS_MOVED_SKIPS_A_NESTED_WORK_TREE, SPEC-0007/REPO_CLAIM_READ_ALIKE_BY_ROUTER_AND_ANCHORS, SPEC-0007/SOURCE_INDEX_SKILL_ROUTES_ITS_FOUR_QUESTIONS, SPEC-0007/BUILD_REPORTS_ITS_TIME_AND_COUNTS, SPEC-0007/BUILD_NAMES_REPO_VALUES_THAT_NAME_NOTHING, SPEC-0007/BUILD_NAMES_TESTS_OUTSIDE_THE_TEST_CLASS, SPEC-0007/BUILD_HINTS_EXCLUDE_FOR_NON_TEST_FILES, SPEC-0007/BUILD_RECORDS_NAME_THEIR_FIX, SPEC-0007/BUILD_HINTS_CONFIG_PATTERNS_THAT_MATCH_NOTHING, SPEC-0007/KERNEL_NAMES_THE_SOURCE_INDEX, SPEC-0007/INSTALL_RUNS_THE_BUILD, SPEC-0007/GROWTH_AUDIT_PRINTS_THE_BUILD_REPORT
- Files touched: none
- Tests to write (RED): none: implemented and green at `v8.3.1` under earlier plans
- Behavior added: none
- Gate: their §10 rows stay green in the round's full gate
- Rollback path: none needed
- Effort: low
- Phase: GREEN
- Depends on: none

### Increment 2: R1, R2, R3 guard wiring, check and docstrings
- Spec contracts: SPEC-0001/BLOCKING_HOOK_WIRING_FAILS_OPEN_ON_A_MISSING_SCRIPT, SPEC-0001/CHECK_REPORTS_A_MISSING_BLOCKING_HOOK_SCRIPT
- Files touched: `integrations/claude-code/settings.json`, `integrations/claude-code/bound-hook.py`, `integrations/claude-code/resume-hook.py`, `integrations/claude-code/README.md`, `install.sh`, `tests/test-install-placement.sh`, `tests/test-prompt-hooks.sh`, `docs/specs/SPEC-0001-install-placement.md`
- Tests to write (RED): M27 `case_guard_wiring` in `tests/test-install-placement.sh`; seen red first (the wired Bash command exited 2 with the script absent)
- Behavior added: a guard command whose script is absent, dangling or a directory exits 0 with one stderr line naming the path; `--check` names the event, matcher and path and does not run the guard
- Gate: `bash tests/test-install-placement.sh`, `bash tests/test-prompt-hooks.sh`, `bash tests/test-bound-hook.sh`
- Rollback path: revert the increment's commit
- Effort: medium
- Phase: GREEN
- Depends on: increment 1

### Increment 3: R4 the index inventories the plant's code only
- Spec contracts: SPEC-0007/SEED_PLACED_FILES_ARE_NOT_THE_PLANTS_CODE
- Files touched: `tools/source_paths.py`, `templates/knowledge-graph/source_paths.py`, `tests/test-source-index.sh`, `docs/specs/SPEC-0007-source-index.md`
- Tests to write (RED): X519 in `tests/test-source-index.sh`; seen red first (the build listed 243 placed files beyond the plant's own)
- Behavior added: files the installer places as seed machinery are not inventoried; a plant-authored file in the same directories is
- Gate: `bash tests/test-source-index.sh`, `bash tests/test-code-anchor.sh`
- Rollback path: revert the increment's commit
- Effort: medium
- Phase: GREEN
- Depends on: increment 2

### Increment 4: R5 skill projection drift
- Spec contracts: SPEC-0001/CHECK_FLAGS_A_DRIFTED_SKILL_PROJECTION
- Files touched: `install.sh`, `tests/test-install-placement.sh`, `docs/specs/SPEC-0001-install-placement.md`
- Tests to write (RED): M28 `case_skill_projection_drift` in `tests/test-install-placement.sh`; seen red first (`--check` exited 0 on an edited graph-home skill)
- Behavior added: `--check` names every skill projection that differs from its node; `--recompose-agents` re-projects skills and writes no node
- Gate: `bash tests/test-install-placement.sh`
- Rollback path: revert the increment's commit
- Effort: medium
- Phase: GREEN
- Depends on: increment 2

### Increment 5: R6 root-safe cases
- Spec contracts: none (two test-suite cases; no behavior of the seed changes)
- Files touched: `tests/test-lint-audibility.sh`, `tests/test-install-adoption.sh`
- Tests to write (RED): the two cases failed under uid 0 in a container before the change; each now prints one SKIPPED line there and runs unchanged for other users
- Behavior added: none
- Gate: `bash tests/test-lint-audibility.sh`, `bash tests/test-install-adoption.sh`, each as uid 0 and as another user
- Rollback path: revert the increment's commit
- Effort: low
- Phase: GREEN
- Depends on: increment 1

### Increment 6: R7 equivalent spellings in the bound hook
- Spec contracts: none (the hook has no spec; `tests/test-bound-hook.sh` holds it)
- Files touched: `integrations/claude-code/bound-hook.py`, `tests/test-bound-hook.sh`
- Tests to write (RED): blocked and bounded rows for each added spelling, and allowed rows for quoted text, a heredoc body and non-equivalent commands; seen red first (`npm i` exited 0)
- Behavior added: `npm i`, `pnpm`, `yarn`, `bun`, `python -m pip`, `uv pip`, `podman` and `nerdctl` run and exec, `docker exec -ti`, `cargo b`, `gmake`, `tail -F` and the `--follow` spellings are treated as the commands they spell
- Gate: `bash tests/test-bound-hook.sh`
- Rollback path: revert the increment's commit
- Effort: low
- Phase: GREEN
- Depends on: increment 2

### Increment 7: R8 the cost row
- Spec contracts: SPEC-0004/COST_ROW_REPORTS_THE_WHOLE_MEASUREMENT
- Files touched: `README.md`, `docs/plans/grill-7.29.0-front-door/method-overhead-evidence.md`, `tests/seed-lint.py`, `tests/test-seed-lint.sh`, `tests/fixtures/front-door/README.md`, `docs/specs/SPEC-0004-front-door.md`
- Tests to write (RED): X518 in `tests/test-seed-lint.sh`: a row that drops the tool-call figure, drops the missed defect, adds a number the record lacks, or links no record; seen red first
- Behavior added: the README row states the token, tool-call and wall-clock figures, the defect the run with the method missed and that it was measured once; seed-lint holds each number to the record or the slice it cites
- Gate: `python3 tests/seed-lint.py`, `bash tests/test-seed-lint.sh`
- Rollback path: revert the increment's commit
- Effort: low
- Phase: GREEN
- Depends on: increment 1

**Delegation and parallelism.** The static schedule is `python3 templates/knowledge-graph/grill-lint.py --plan docs/plans/grill-8.3.2-review-fixes.md --specs docs/specs --decisions docs/decisions --waves`. A file two increments write (`install.sh`, `docs/specs/SPEC-0001-install-placement.md`, `tests/test-install-placement.sh`) is ordered by `Depends on:`.

## 10. Verification Plan
The standard gate holds (`CLAUDE.md` Gates: `bash tests/run.sh`), on an interpreter at the 3.14 floor. The three byte figures are measured against the baseline taken before the round.

## 11. Risks and Mitigations
| Risk | Probability | Impact | Mitigation | Owner | Verification | Refutation |
|---|---:|---:|---|---|---|---|
| The guard wiring changes what a present guard blocks | low | high | the command passes the script's exit code through and carries no `|| true` | tester | M27 runs the Bash guard on a blocked input and expects exit 2 | `could-not-refute`, devils-advocate press of 2026-11-10 (press note below) |
| The list of placed files misses a path the installer later gains | medium | low | the source-index case installs every host and fails on an uncovered file | tester | X519 | not pressed |
| An added spelling blocks a command that is not equivalent | low | medium | allowed rows for each neighbouring non-equivalent command | tester | `tests/test-bound-hook.sh` | not pressed |

**Press note (devils-advocate, 2026-11-10).** The press took row 1, the top risk by probability × impact, and tried five claims against primary sources by running the shipped commands under `/bin/sh` and `dash`, with a project path holding a space, a quote and a dollar sign. A present guard returned its script's exit code (2 for a refusal), with stdin, `-S` and the `$PWD` fallback intact; the interpreter rewrite reached each command once; `--check` captured the right paths and ran nothing. Verdict `could-not-refute` for what a present guard blocks. It refuted one wording: the missing-script line was not always one line, because `echo` expands backslash escapes in `sh` and `dash` and a project path holding `\n` printed two. The command now prints it with `printf '%s\n'`, and M27 runs a path holding a backslash. Blind spots it named: no live host, no Windows Git Bash, and a guard wired to an interpreter that is no longer on PATH exits 127 and nothing reports it, which was true before this round.

## 12. Open Questions
| # | Question | Why it matters | Current assumption | How to resolve | Owner | Pinned by |
|---:|---|---|---|---|---|---|
| 1 | Which of D1 to D7 should the owner adopt, trial or leave? | each changes a default the owner set, or needs evidence this round could not produce | nothing lands; each stays as today | the decision notes in [`owner-decisions-8.3.2-review-fixes.md`](owner-decisions-8.3.2-review-fixes.md) | owner | none |
| 2 | `--check` does not yet compare skill projections for hosts other than Claude Code, and the opencode remedy (a re-run of the installer) replaces a graph node with the seed's | a drifted `.opencode/skills/`, `.codex/skills/` or `.prime/agent/skills/` projection passes `--check` | left as is this round; the review's confirmed case was Claude Code | a later round, with a remedy that keeps the node | owner | none |
| 3 | 8.3.1's open question 2 (`--check` did not name a missing resume or bound hook script) | a plant lost its guard silently | resolved by increment 2 | none | steward | SPEC-0001 `CHECK_REPORTS_A_MISSING_BLOCKING_HOOK_SCRIPT` |

Row 1 stays open for the owner. Its notes live in a sibling file because each runs to a paragraph, which this table's one-line rows cannot hold readably, and the plan's own directory holds only §9 increments.

Row 2 stays open for the owner.

## 13. Done Criteria
- Every increment in §9 is done; each new contract has a `green` §10 row in its spec.
- `grill-lint.py` lints this plan from `tests/run.sh` and passes.
- `bash tests/run.sh` is green on the floor interpreter.
- The three byte figures are not above the baseline.

## 14. Recommended Next Step
Run the release pass, `docs/skills/seed-release.md`; the tag push waits for the owner's explicit go-ahead.

## 15. Changelog
- 2026-11-10: plan opened as the record of round 8.3.2, built on v8.3.1. `tests/run.sh` `ACTIVE_PLAN` moves here from the 8.3.1 plan, so the gate holds the contracts this round adds.
- 2026-11-10: increments 2 to 7 landed (R1 to R8 of the brief). R1 and R2: the `PreToolUse` guards test that their script exists and pass its exit code through, and `--check` names a missing guard script without running it. R4: the index leaves out a list of the exact files the installer places. R5: `--check` flags a drifted Claude Code skill projection and `--recompose-agents` re-projects it. R6: two cases skip with a reason under uid 0. R7: the bound hook blocks the equivalent spellings listed in increment 6. R8: the README row states the whole measurement. The decision notes D1 to D7 are written for the owner and nothing in them is implemented.
