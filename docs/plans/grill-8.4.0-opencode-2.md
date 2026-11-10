# grill.md: Plan of Record: round 8.4.0, opencode is a first-class host on OpenCode 2

## 0. Metadata
- Project: CYPRESS seed
- Feature or goal: make opencode a first-class host at parity with Claude Code, on OpenCode 2 only (requirements O1 to O12 of the owner's brief of 2026-11-10), and prepare the decisions that are the owner's
- Date: 2026-11-10
- Owner: the steward
- Tier: T3. Protocol: `protocol.grill` for the increments; this plan is the record of what lands and why
- Current phase: increments 1 to 7 are done; the version and changelog are written by the release pass
- Related files: `install.sh`, `integrations/opencode/`, `tools/agent_compose.py`, `tools/graft-audit.py`, `tools/growth-audit.py`, `tools/brief.py`, `tests/seed-lint.py`, `tests/test-full-install.sh`, `tests/test-opencode-plugin.sh`, `tests/test-prompt-hooks.sh`, `tests/test-bound-hook.sh`, `tests/test-brief.sh`, `tests/test-seed-lint.sh`, `tests/run.sh`
- Related documentation: `docs/plans/grill-8.3.2-review-fixes.md` (the previous plan the gate linted); `docs/skills/seed-release.md` (the release pass that follows this plan); `docs/skills/opencode-live-verification.md` (the repeatable live procedure)
- Related ADRs: [ADR-0033](../decisions/adr-0033-opencode-first-class-on-opencode-2.md) (supersedes the opencode row of [ADR-0009](../decisions/adr-0009-host-support-tiers.md)); [ADR-0022](../decisions/adr-0022-the-plant-model-map.md); [ADR-0024](../decisions/adr-0024-one-hook-core-per-session-residency.md)
- Related specs: [SPEC-0001](../specs/SPEC-0001-install-placement.md) (the projections, the placement, `--check`); [SPEC-0003](../specs/SPEC-0003-per-prompt-injection.md) (the plugin envelope); [SPEC-0004](../specs/SPEC-0004-front-door.md); [SPEC-0005](../specs/SPEC-0005-cycle-economy.md); [SPEC-0007](../specs/SPEC-0007-source-index.md)
- Related libraries: none (stdlib Python, bash, and a TypeScript file the host loads with no build step)
- Baseline: 8.3.2, the commit this round builds on

## 1. Artifact Discovery
Every line cites the paths it rests on. Each owner decision is stated in words with its date.
- Existing files inspected: `install.sh` (`render_opencode_agents`, `render_claude_agents`, `install_opencode`, `check_opencode_projections`, `check_wired_hooks`, the tier arrays); `integrations/opencode/` (`README.md`, `opencode.json`); `integrations/prime-agent/route-extension.ts` and `status-extension.ts` (the envelopes the plugin follows); `integrations/claude-code/{route,status,bound,resume}-hook.py`; `tools/brief.py`; `tools/graft-audit.py`; `tests/seed-lint.py`
- Existing docs inspected: `docs/decisions/adr-0009-host-support-tiers.md`; `documentation/host-capability-matrix.md`; `core/method/delegation-model-classes.md`; `docs/plans/owner-decisions-8.3.2-review-fixes.md` (the shape of the decision notes)
- Existing tests inspected: `tests/test-full-install.sh` (E8 to E11); `tests/test-prompt-hooks.sh`; `tests/test-bound-hook.sh`; `tests/test-brief.sh`; `tests/test-seed-lint.sh`
- Existing specs inspected: SPEC-0001, SPEC-0003, SPEC-0005 (each one's `### Contract:` list)
- Existing architecture signals: the always-loaded budget is a ratchet; the shared hook core decides and a host envelope composes nothing (ADR-0024)
- Libraries already wikified: none
- External sources downloaded: none
- Constraints discovered: the installed host at the verified version is OpenCode 2; the file name is the host's agent id; a frontmatter `tools:` list voids the agent file; the top-level `subagent_depth` is an unsupported legacy setting and the key is `experimental.subagent_depth`; a plugin imports the host's bundled package with no install; a hook edits by mutating its argument; a synthetic message starts a model call unless given `resume: false`

## 2. Shared Understanding
The owner decided on 2026-11-10 that opencode becomes a first-class host at parity with Claude Code, and that the seed supports OpenCode 2 only.

| Requirement | What it settles | Where it lands |
|---|---|---|
| O1 | the ADR, the tier arrays, the lint and the documents that state the tiers agree | increment 2 |
| O2, O3, O4 | native agent files with the tool bound and delegation list as host permissions, composed from the always-loaded nodes; the OpenCode 2 config; a re-install over the earlier shape | increment 3 |
| O5, O6 | one plugin over the shared cores: route, status, no routing of a child, bounded execution | increment 4 |
| O10, O11 | `--check` names each opencode surface; the gate covers them | increment 5 |
| O9 | the brief composer refuses `--charter` on an opencode plant | increment 6 |
| O8 | the orchestrator is the default agent; its charter is the main session's system prompt; the exemption is recorded (owner decisions D1 and D2, 2026-11-10) | increment 7 |
| O7 | not landed: recorded as an open defect | the host matrix |

Success means: each requirement that lands has a test seen red first and green, the full gate passes on the floor interpreter without OpenCode 2 or a network, and live verification is recorded with the host version. Out of scope: any change to Claude Code, Prime Agent, Codex or GitHub Copilot; tagging and pushing.

## 3. User Goal
- Primary user: an owner running a plant on OpenCode 2
- Primary outcome: the specialists register with their models, tool bounds and delegation lists held by the host, the session receives the route suggestion and status register, and an unbounded shell command is refused with its reason
- Job to be done: run `install.sh opencode` and `install.sh opencode --check` and know every opencode surface works or is named
- Acceptance criteria (link to spec §9): the SPEC-0001 and SPEC-0003 rows the 2026-11-10 changelog entries add
- Non-goals: OpenCode 1; a redesign of the hook core; Prime Agent (set aside by the owner on 2026-11-10)

## 4. Operating Constraints
- Runtime constraints: bash 3.2 syntax in `install.sh`; stdlib Python at the 3.14 floor; no new dependency; a placed TypeScript file loads with no build step
- Security constraints: a missing or failing guard allows the command and is reported; a refusal carries the core's reason; the read-only roles keep their bound
- Privacy constraints: no project, host-machine or path name from the working environment in any tracked file; fixtures and live prompts are synthetic
- Data constraints: none
- Cost constraints: the batch sizes of `delegation.effort-scale`; no two writers of one file in one wave
  - Plan approval (`grill.plan-approval`), skipped: the owner's brief of 2026-11-10 is the approved scope. Levers this plan uses: none defined (default)
  - Owner-only prerequisites: the release and its tag push wait for the owner's explicit go-ahead (`vcs-posture.publish-authorization`); D1 and D2 were the owner's and are decided; D3 did not arise and D4 is set aside
  - Scoped standing grant: none asked
- Latency constraints: none
- Compliance constraints: none
- Maintenance constraints: one home per fact; the always-loaded surface and `EAGER_BUDGET` do not move

## 5. Research Summary
no external dependency — the seed's code gains no library, and no §9 row depends on a `docs/graph/libraries/` page. The host facts were observed on a running OpenCode 2 and are recorded in `docs/skills/opencode-live-verification.md` and the host matrix, with the version in `integrations/opencode/verified-version`.

## 6. Decisions Made
| Decision | Rationale | Evidence | Reversibility | ADR | Date |
|---|---|---|---|---|---|
| Tier T3 | the installer, a new envelope, three specs | kernel §0 | not applicable | none | 2026-11-10 |
| opencode is first-class and the seed targets OpenCode 2 only | the owner's decision of 2026-11-10 | ADR-0033 | reversible | ADR-0033 | 2026-11-10 |
| An agent is transformed into the host's native file, named by its callable name | the host drops a file with a `tools:` list and reads the file name as the id | SPEC-0001 `OPENCODE_AGENT_IS_NATIVE` | reversible | ADR-0033 | 2026-11-10 |
| The tool map has one home, a JSON table, and an unknown tool stops the render | an unknown name must never read as allowed | SPEC-0001 `OPENCODE_TOOL_BOUND_IS_HOST_PERMISSIONS` | reversible | none | 2026-11-10 |
| One composer serves both hosts, in `tools/agent_compose.py` | the two hosts cannot diverge in which nodes ride along | SPEC-0001 `OPENCODE_AGENT_COMPOSES_ITS_ALWAYS_LOADED_NODES` | reversible | none | 2026-11-10 |
| The route and status text travel as synthetic messages with `resume: false` | the prompt edit has no effect, a keyed entry sits in the system section, a synthetic message is appended history | SPEC-0003 `OPENCODE_PLUGIN_INJECTS_THE_CORES_TEXT_ONCE` | reversible | none | 2026-11-10 |
| The guard refuses through the permission hook's `deny` and message | the reason reaches the model | SPEC-0003 `OPENCODE_SHELL_GUARD_REFUSES_WITH_THE_CORES_REASON` | reversible | none | 2026-11-10 |
| The version is 8.4.0 | a behaviour change for existing opencode plants | `docs/skills/seed-release.md` | reversible | none | 2026-11-10 |

## 7. Options Considered
| Option | Benefits | Costs | Risks | Outcome |
|---|---|---|---|---|
| Edit the user's prompt to carry the route text | one mechanism | rewrites the user's input | the host ignores the edit | Rejected |
| Add a keyed instruction entry per turn | persists in the session | sits in the system section | a changed value breaks the provider's cached prefix | Rejected |
| Make the orchestrator the default agent | the lead plays the charter with no plugin delivery | replaces the host's base prompt and changes the user's default | owner decision D2 | Taken on 2026-11-10 |
| Deliver the charter to the main session while the host's agent stays | the host's base prompt stays | the always-loaded surface rises past `EAGER_BUDGET` all the same, plus a delivery duty in the plugin | owner decision D1 | Not taken |

## 8. Architecture Plan
- System boundary: unchanged
- Main components: `render_opencode_agents` and `tools/agent_compose.py`; `integrations/opencode/tool-permissions.json`; `integrations/opencode/cypress-plugin.ts`; the three cores placed under `.opencode/hooks/`
- Interfaces: `.opencode/agents/<callable name>.md` in the host's own fields; `.opencode/plugins/cypress.ts`; `install.sh opencode --check` and `--recompose-agents`
- Data flow: charter and always-loaded nodes, to the agent file; prompt, to the core, to a synthetic message; shell command, to the core, to the permission verdict
- Error handling: any failure of the plugin or a core injects nothing and refuses nothing; a tool the table lacks stops the render
- Observability: the `--check` lines; the installer's OpenCode 2 line
- Security posture: unchanged for the other hosts; the opencode bound is held by the host
- Deployment model: new plants at install; existing plants at their next install or graft
- Environment parity: the gate runs without OpenCode 2 and without a network; the plugin's fixture half skips with a printed reason without `bun`

## 9. Implementation Plan

Increments are inline; numbers are dependency order. Increment 1 carries the contracts of SPEC-0001, SPEC-0003, SPEC-0004, SPEC-0005 and SPEC-0007 this round leaves as they were. Rolling back the round is reverting its commits on the work branch; an increment's own rollback restores its files from the baseline commit.

| # | Subject | Status |
|---|---|---|
| 1 | carried | done |
| 2 | O1 the ADR and the tier | done |
| 3 | O2, O3, O4 native agents, config, composition, re-install | done |
| 4 | O5, O6 the plugin over the shared cores | done |
| 5 | O10, O11 `--check` and the gate | done |
| 6 | O9 the brief composer | done |
| 7 | O8 the lead plays the orchestrator | done |

### Increment 1: Carried: the contracts this round leaves as they were
- Spec contracts: SPEC-0001/SINGLE_WRITER, SPEC-0001/BACKUP_BEFORE_REPLACE, SPEC-0001/FORCE_SUPPRESSES_WARNING_NOT_BACKUP, SPEC-0001/SYMLINK_IS_REPLACED_NOT_FOLLOWED, SPEC-0001/IDENTICAL_RERUN_IS_INERT, SPEC-0001/EVERY_BACKUP_IS_CLASSIFIABLE, SPEC-0001/SYMLINK_MODE_IS_UNIFORM, SPEC-0001/COPY_MODE_ISOLATES, SPEC-0001/ONE_KERNEL_BODY, SPEC-0001/DECISIONS_SURVIVE_SILENCE, SPEC-0001/ADAPTERS_ACCUMULATE, SPEC-0001/RECORD_AGREES_WITH_DISK, SPEC-0001/CORPUS_IS_WHOLE_OR_ABSENT, SPEC-0001/PREFLIGHT_REFUSES_BEFORE_WRITING, SPEC-0001/PREFLIGHT_SCOPED_TO_WRITTEN_TREES, SPEC-0001/ALL_EXCLUDES_LEGACY_HOSTS, SPEC-0001/LEGACY_INSTALL_PRINTS_DEPRECATED, SPEC-0001/LEGACY_INSTALL_STILL_SUCCEEDS, SPEC-0001/ALL_NAMES_SKIPPED_FROZEN_HOSTS, SPEC-0001/CHECK_WITHOUT_COPILOT_SAYS_SO, SPEC-0001/ALL_CHECK_INCLUDES_RECORDED_COPILOT, SPEC-0001/HOST_TIERS_AGREE, SPEC-0001/SESSION_RECORD_FORM_IS_PLACED, SPEC-0001/HARVEST_CANDIDATE_FORM_IS_PLACED, SPEC-0001/ENGINE_RECONCILE_PICKS_CONFIG_BY_ENGINE, SPEC-0001/ENGINE_AUDIT_CHECKS_EVERY_PAIR, SPEC-0001/EXISTING_PLANT_RECEIVES_CURRENT_ENGINES, SPEC-0001/PRISTINE_PRIOR_KERNEL_IS_NOT_MIGRATION, SPEC-0001/RECREATED_LIST_IS_COMPLETE, SPEC-0001/UNKNOWN_STAMP_KEYS_SURVIVE, SPEC-0001/RETIRED_STAMP_KEYS_NAMED_AND_KEPT, SPEC-0001/LEAD_CACHE_TTL_IS_PLACED_ONLY_ON_OPT_IN, SPEC-0001/HOOKS_RUN_ON_THE_FLOOR_INTERPRETER, SPEC-0001/STAMP_TRACKING_LINES_PRINTED, SPEC-0001/BACKUPS_LISTED_BY_DATE, SPEC-0001/HUB_KEPT_CANONICAL_IN_COMPOSE_MODE, SPEC-0001/PRE_GROWTH_POINTER_LIVES_IN_THE_PLACEHOLDER_INDEX, SPEC-0001/CODE_ANCHOR_TOOL_IS_PLACED, SPEC-0001/MODEL_MAP_TEMPLATE_IS_PLACED, SPEC-0001/OPENCODE_MODEL_FROM_MAP, SPEC-0001/OPENCODE_NO_MAP_ROW_NO_MODEL_LINE, SPEC-0001/OPENCODE_MAP_UNREADABLE_FAILS_CLOSED, SPEC-0001/OPENCODE_CHECK_DETECTS_DRIFT, SPEC-0001/PRIME_HOOK_SCRIPTS_ARE_PLACED, SPEC-0001/REINSTALL_ENGINE_SERVES_THE_HOOKS, SPEC-0001/SEED_ONLY_FILES_NEVER_PLACED, SPEC-0001/EXPERTISE_PROPOSAL_WRITES_NOTHING, SPEC-0001/LANGUAGE_DECLARATION_PROPOSES_ITS_PAGE, SPEC-0001/OWN_PACKAGE_LIST_PROPOSES_ITS_PAGE, SPEC-0001/CITED_PACKAGE_PROPOSES_NOTHING, SPEC-0001/PACKAGELESS_PAGE_PROPOSED_BY_ITS_TRIGGER, SPEC-0001/EXPERTISE_PLACES_ONLY_THE_CONFIRMED_LIST, SPEC-0001/UNKNOWN_EXPERTISE_ID_REFUSED_BEFORE_WRITING, SPEC-0001/PLACED_PAGE_CARRIES_ITS_PROVENANCE, SPEC-0001/PLACED_SKILL_IS_A_ROUTABLE_NODE, SPEC-0001/PLACED_CORPUS_PAGE_IS_REACHABLE, SPEC-0001/EXPERTISE_IS_RECORDED_IN_THE_STAMP, SPEC-0001/EXPERTISE_SURVIVES_SILENCE, SPEC-0001/PLANT_EDITED_PAGE_IS_LEFT_AND_NAMED, SPEC-0001/PLANT_OWNED_PAGE_IS_NEVER_REPLACED, SPEC-0001/EXPERTISE_CHECK_NAMES_MISSING_OR_STALE, SPEC-0001/JURISDICTION_RESOLVED_ONCE, SPEC-0001/CHECK_EXECUTES_EACH_WIRED_HOOK, SPEC-0001/BLOCKING_HOOK_WIRING_FAILS_OPEN_ON_A_MISSING_SCRIPT, SPEC-0001/CHECK_REPORTS_A_MISSING_BLOCKING_HOOK_SCRIPT, SPEC-0001/CHECK_FLAGS_A_DRIFTED_SKILL_PROJECTION, SPEC-0001/CHECK_FLAGS_RETIRED_HARNESS_ENTRY, SPEC-0001/CHECK_FLAGS_ORPHAN_HARNESS_ENTRY, SPEC-0001/CHECK_FLAGS_RETIRED_GRAPH_NODE, SPEC-0001/GRAFT_RUN_NAMES_PLAN_DEFECTS_THE_UPGRADE_RAISES, SPEC-0001/GRAFT_RUN_TIES_LINT_ERRORS_TO_RETIRED_NODES, SPEC-0001/INSTALL_KEEPS_DIVERGED_MACHINERY, SPEC-0001/GRAFT_RUN_RECREATED_LEAVES_OUT_SEED_NEW, SPEC-0003/ROUTE_HOOK_STRIPS_MULTILINE_PROMPT_ECHO, SPEC-0003/ROUTE_HOOK_PASSES_PROMPT_AS_ONE_OPTION_VALUE, SPEC-0003/ROUTE_HOOK_UNPASSABLE_PROMPT_FAILS_OPEN, SPEC-0003/ROUTE_HOOK_POINTS_AT_KERNEL, SPEC-0003/HOOK_TEXT_RESTATES_NO_KERNEL_RULE, SPEC-0003/LEDGER_FIRST_PROMPT_FULL, SPEC-0003/LEDGER_LATER_PROMPT_REMINDER, SPEC-0003/REMINDER_KEEPS_NOTICE_LINES, SPEC-0003/REMINDER_SAYS_SURFACED_NEVER_LOADED, SPEC-0003/LEDGER_NEW_IDS_LISTED, SPEC-0003/REMINDER_DROPS_PEERS_ALREADY_SHOWN, SPEC-0003/LEDGER_EVERY_LOAD_ID_NAMED, SPEC-0003/LEDGER_REFRESH_EVERY_N, SPEC-0003/LEDGER_TRIVIAL_PROMPT_UNTOUCHED, SPEC-0003/LEDGER_UNUSED_WITHOUT_GRAPH, SPEC-0003/LEDGER_NEVER_EMITS_UNROUTED_ID, SPEC-0003/LEDGER_ABSENT_SESSION_ID_FULL, SPEC-0003/LEDGER_INVALID_SESSION_ID_FULL, SPEC-0003/LEDGER_CORRUPT_FULL, SPEC-0003/LEDGER_UNKNOWN_VERSION_FULL, SPEC-0003/LEDGER_EXPIRED_FULL, SPEC-0003/STATUS_HOOK_RESETS_LEDGER, SPEC-0003/STATUS_HOOK_NO_LEDGER_WRITES_NOTHING, SPEC-0003/STATUS_HOOK_RESETS_WITHOUT_REGISTER, SPEC-0003/STATUS_HOOK_WITHOUT_SIBLING_LEAVES_LEDGER, SPEC-0003/LEDGER_GITIGNORED, SPEC-0003/LEDGER_WRITE_IS_ATOMIC, SPEC-0003/LEDGER_SYMLINK_REFUSED, SPEC-0003/LEDGER_FOREIGN_OR_WRITABLE_REFUSED, SPEC-0003/LEDGER_NO_CYPRESS_DIR_NO_WRITE, SPEC-0003/LEDGER_WRITE_FAILURE_FAILS_OPEN, SPEC-0003/LEDGER_GC_BOUNDED, SPEC-0003/BRIEF_TEMPLATES_BYTE_IDENTICAL, SPEC-0003/HOOK_ARGV_ENVELOPE_EQUALS_STDIN_ENVELOPE, SPEC-0003/CHILD_SESSION_GETS_NO_INJECTION, SPEC-0003/NON_HUMAN_TURN_NOT_ROUTED, SPEC-0003/SESSION_INJECTION_WITHIN_BUDGET, SPEC-0003/ROUTE_EXTENSION_PASSES_PROMPT_AS_ONE_OPTION_VALUE, SPEC-0003/PRIME_SESSION_ID_PASSED, SPEC-0003/PRIME_RESET_ON_EVENTS, SPEC-0003/STATUS_ONCE_PER_SESSION, SPEC-0003/EVERY_RESOLVER_PATH_IS_INSTALLED, SPEC-0003/PRIME_EAGER_SURFACE_WITHIN_BUDGET, SPEC-0003/PLAN_ENTRY_NAMES_THE_NODE_FILE, SPEC-0003/PLAN_PRINTS_PLANT_BLOCK, SPEC-0003/PLAN_JSON_SCHEMA, SPEC-0003/PLAN_JSON_CARRIES_NO_PROMPT, SPEC-0003/PLAN_JSON_HASH_BINDS_TASK, SPEC-0003/PLAN_JSON_EQUALS_PLAN, SPEC-0003/ROUTE_HOOK_READS_PLAN_JSON, SPEC-0003/ROUTE_FULL_TEXT_EQUALS_PLAN, SPEC-0003/ROUTE_HOOK_KEEPS_THE_PATH, SPEC-0003/SHOW_KEEPS_EVERY_POINTER, SPEC-0003/SHOW_DROPS_ROUTER_AND_SPAWN_KEYS, SPEC-0003/SHOW_BODY_VERBATIM, SPEC-0003/SHOW_UNKNOWN_ID_FAILS, SPEC-0003/ANCHOR_RECORD_NAMES_EVERY_REPOSITORY, SPEC-0003/ANCHOR_QUIET_WHEN_NOTHING_MOVED, SPEC-0003/ANCHOR_NAMES_PATHS_WHEN_THE_COMMIT_MOVED, SPEC-0003/ANCHOR_NAMES_BOTH_BRANCHES_WHEN_THE_BRANCH_MOVED, SPEC-0003/ANCHOR_NAMES_NEW_UNCOMMITTED_WORK, SPEC-0003/ANCHOR_ABSENT_FAILS_TOWARD_INCLUSION, SPEC-0003/ANCHOR_OUTPUT_WITHIN_BUDGET, SPEC-0003/ANCHOR_COMPARE_WRITES_NOTHING, SPEC-0003/ANCHOR_RECORD_REFUSES_A_SYMLINK, SPEC-0003/ANCHOR_IGNORES_BUILD_AND_BACKUP_NOISE, SPEC-0003/STATUS_HOOK_INJECTS_THE_ANCHOR_LINE, SPEC-0003/STATUS_HOOK_ANCHOR_FAILURE_FAILS_TOWARD_INCLUSION, SPEC-0003/MISSING_HOOK_SCRIPT_WARNS_AND_PASSES, SPEC-0004/INSTALL_SECTION_NAMES_TARGET_PATHS, SPEC-0004/GLOSSARY_PATHS_EXIST, SPEC-0004/MECHANISM_CLAIMS_TRACED, SPEC-0004/EAGER_FIGURES_CHECKED_WHEREVER_PUBLISHED, SPEC-0004/BODY_FIGURES_HAVE_A_REQUIRED_HOME, SPEC-0004/COST_ROW_REPORTS_THE_WHOLE_MEASUREMENT, SPEC-0004/FRONT_DOOR_ANCHORS_RESOLVE, SPEC-0004/PROSE_FLOOR_HELD_PER_FILE, SPEC-0007/BUILD_INVENTORIES_THE_CODE_OF_EVERY_GOVERNED_REPOSITORY, SPEC-0007/SEED_PLACED_FILES_ARE_NOT_THE_PLANTS_CODE, SPEC-0007/BUILD_IS_DETERMINISTIC, SPEC-0007/CACHE_WRITTEN_SELF_IGNORED, SPEC-0007/CACHE_REUSED_WHILE_THE_KEY_HOLDS, SPEC-0007/CACHE_REBUILT_WHEN_THE_KEY_CHANGES, SPEC-0007/GRAFT_REBUILDS_THE_CACHE, SPEC-0007/LINK_PYTHON_IMPORT_CERTAIN, SPEC-0007/LINK_SHELL_INVOCATION_CERTAIN, SPEC-0007/LINK_PATH_LITERAL_AND_DIRECTORY_ARE_MAYBE, SPEC-0007/LINK_TS_SPECIFIER_CERTAIN, SPEC-0007/UNPINNED_REFERENCE_RECORDED_WITH_ITS_REASON, SPEC-0007/TESTS_ARE_THE_PLANTS_TEST_GLOBS, SPEC-0007/PLANT_CONFIG_REPLACES_EACH_DEFAULT_KEY, SPEC-0007/WALK_NEAREST_FIRST_ONCE, SPEC-0007/WALK_CHAIN_IS_ITS_WEAKEST_LINK, SPEC-0007/WALK_FLOOR_LISTED_APART_AFTER_THE_INPUT_ROWS, SPEC-0007/WALK_DELETED_INPUT_REACHES_ITS_NAMERS, SPEC-0007/INPUT_FORMS_RESOLVED, SPEC-0007/WALK_INCOMPLETE_NAMES_REASON_AND_ACTION, SPEC-0007/INPUT_IN_AN_UNREAD_LANGUAGE_IS_INCOMPLETE, SPEC-0007/ACTION_LINE_NAMES_AT_MOST_TEXT_MAX_ROWS_RECORDS, SPEC-0007/AFFECTED_TESTS_ARE_THE_WALK_FILTERED, SPEC-0007/AFFECTED_ALWAYS_RUN_LISTED_APART, SPEC-0007/TEST_REACHING_CODE_OVER_HTTP_IS_INCOMPLETE, SPEC-0007/ANCHORS_NAME_CITING_PAGES_OR_UNCITED, SPEC-0007/ANCHORS_BASENAME_IS_MAYBE_AMBIGUOUS_IS_INCOMPLETE, SPEC-0007/OUTPUT_CARRIES_NO_RAW_CONTROL, SPEC-0007/SOURCE_INDEX_IS_PLACED, SPEC-0007/SYMBOLS_PYTHON_DEFINITIONS_CERTAIN, SPEC-0007/SYMBOLS_LINE_READ_DECLARATIONS_ARE_MAYBE, SPEC-0007/SYMBOLS_LIST_EVERY_DEFINITION, SPEC-0007/SYMBOLS_UNREADABLE_FILE_MAKES_IT_INCOMPLETE, SPEC-0007/HISTORY_ROWS_ARE_MAYBE_WITH_THEIR_COUNT, SPEC-0007/HISTORY_ONLY_ADDS, SPEC-0007/HISTORY_SHALLOW_OR_MISSING_IS_INCOMPLETE, SPEC-0007/ANCHORS_MOVED_EQUALS_THE_NAMED_PATHS, SPEC-0007/ANCHORS_MOVED_WITHOUT_A_LIST_IS_INCOMPLETE, SPEC-0007/ANCHORS_MOVED_SKIPS_A_NESTED_WORK_TREE, SPEC-0007/REPO_CLAIM_READ_ALIKE_BY_ROUTER_AND_ANCHORS, SPEC-0007/SOURCE_INDEX_SKILL_ROUTES_ITS_FOUR_QUESTIONS, SPEC-0007/BUILD_REPORTS_ITS_TIME_AND_COUNTS, SPEC-0007/BUILD_NAMES_REPO_VALUES_THAT_NAME_NOTHING, SPEC-0007/BUILD_NAMES_TESTS_OUTSIDE_THE_TEST_CLASS, SPEC-0007/BUILD_HINTS_EXCLUDE_FOR_NON_TEST_FILES, SPEC-0007/BUILD_RECORDS_NAME_THEIR_FIX, SPEC-0007/BUILD_HINTS_CONFIG_PATTERNS_THAT_MATCH_NOTHING, SPEC-0007/KERNEL_NAMES_THE_SOURCE_INDEX, SPEC-0007/INSTALL_RUNS_THE_BUILD, SPEC-0007/GROWTH_AUDIT_PRINTS_THE_BUILD_REPORT, SPEC-0005/PLAN_INFERS_EXPERTISE_FROM_NAMED_FILES, SPEC-0005/LISTED_NODE_EDGES_REACH, SPEC-0005/AGENT_DECLARES_EFFORT, SPEC-0005/AGENT_DECLARES_MODEL_CLASS, SPEC-0005/LEAF_BODY_CEILING_HELD, SPEC-0005/DELEGATION_SPLIT_INTO_SIBLINGS, SPEC-0005/DELEGATION_LEAVES_ROUTE, SPEC-0005/ADOPTED_RULE_HOMES, SPEC-0005/HANDBACK_STARTS_AT_STATUS, SPEC-0005/SPAWN_LOG_RECORDS_THE_ATTRIBUTION, SPEC-0005/TRUST_PATH_TAKES_THE_SECURITY_PASS, SPEC-0005/BRIEF_DERIVES_THE_SPAWN_EFFORT, SPEC-0005/BRIEF_DERIVES_THE_MODEL_CLASS, SPEC-0005/TOKEN_LEDGER_RECORDS_HOST_USAGE, SPEC-0005/TOKEN_LEDGER_READS_A_CLAUDE_CODE_TRANSCRIPT, SPEC-0005/BRIEF_LOG_PRINTS_THE_DERIVABLE_METRICS, SPEC-0005/BRIEF_NOTICES_AN_UNDERSIZED_BATCH, SPEC-0005/RESUME_GUARD_FOLLOWS_THE_CONFIGURED_CACHE_LIFETIME, SPEC-0005/REVIEW_BRIEF_NAMES_THE_SECURITY_PASS, SPEC-0005/IMPLEMENTER_WRITES_A_DESIGN_NOTE, SPEC-0005/RED_TEST_HOLDS_ITS_EVIDENCE, SPEC-0005/REVIEWER_CHECKS_STATE_AND_PLATFORM, SPEC-0005/SECURITY_CONTRACTS_CARRY_ADVERSARIAL_RED_CONTROLS, SPEC-0005/ROLE_AGENT_COMPOSES_ITS_ALWAYS_LOADED_NODES, SPEC-0005/AGENTS_RECOMPOSE_FROM_THE_NODES_ON_DISK, SPEC-0005/PLAN_ROLE_LEAVES_OUT_THE_ROLES_OWN_PROMPT, SPEC-0005/BRIEF_WARNS_ON_A_ROUTE_WITHOUT_EXPERTISE, SPEC-0005/REVIEWER_RUNS_NO_BUILD, SPEC-0005/SLOW_COMMAND_LEAVES_THE_WORKER_TURN, SPEC-0005/GATE_OUTPUT_KEEPS_STATUS_AND_LOG, SPEC-0005/ALWAYS_LOADS_COMPOSES_ONLY_WHAT_THE_ROLE_NEEDS, SPEC-0005/MAIN_SESSION_PLAYS_THE_ORCHESTRATOR, SPEC-0005/TRUST_MARKER_IS_SETTLED, SPEC-0005/BOOTSTRAP_STEP2_LOADS_A_MENU, SPEC-0005/ADOPTED_RULES_NOT_PENDING, SPEC-0005/KERNEL_POINTS_AT_THE_SESSION_RECORD, SPEC-0005/SESSION_RECORD_FORM_IS_NOT_A_SCAFFOLD, SPEC-0005/GRILL_WAVES_LEVELS_FROM_DEPENDS_ON, SPEC-0005/GRILL_WAVES_OVERLAP_IS_A_WARNING, SPEC-0005/GRILL_WAVES_UNSCHEDULED_WITHOUT_PHASE, SPEC-0005/GRILL_WAVES_NOT_COMPUTED_ON_DEPENDENCY_DEFECT, SPEC-0005/GRILL_WAVES_LEAVES_THE_GATE_UNCHANGED, SPEC-0005/GRILL_BATCHES_FOLLOW_THE_EFFORT_TABLE, SPEC-0005/CYCLE_DRIVER_PRINTS_THE_CYCLE_STATE, SPEC-0005/CYCLE_DRIVER_NAMES_THE_HOLD_CONDITION, SPEC-0005/CYCLE_DRIVER_CHECKS_THE_RED_HASHES, SPEC-0005/CYCLE_DRIVER_REFUSES_MALFORMED_INPUT, SPEC-0005/CYCLE_DRIVER_IS_DETERMINISTIC_AND_READ_ONLY, SPEC-0005/CYCLE_DRIVER_RECORDS_ATOMICALLY, SPEC-0005/CYCLE_DRIVER_RUNS_IN_A_FRESH_PLANT
- Files touched: none
- Tests to write (RED): none: implemented and green at the baseline under earlier plans
- Behavior added: none
- Gate: their §10 rows stay green in the round's full gate
- Rollback path: none needed
- Effort: low
- Phase: GREEN
- Depends on: none

### Increment 2: O1 the ADR and the tier
- Spec contracts: SPEC-0001/OPENCODE_VERSION_HAS_ONE_HOME
- Files touched: `docs/decisions/adr-0033-opencode-first-class-on-opencode-2.md`, `docs/decisions/index.md`, `install.sh`, `tests/test-seed-lint.sh`, `tests/seed-lint.py`, `integrations/opencode/verified-version`, `documentation/host-capability-matrix.md`
- Tests to write (RED): E4 mutates the first-class array; E22 holds the verified version to its citations
- Behavior added: opencode sits in the first-class array; `all` keeps its expansion and order
- Gate: `python3 tests/seed-lint.py`, `bash tests/test-seed-lint.sh`
- Rollback path: revert the increment's commit
- Effort: low
- Phase: GREEN
- Depends on: increment 1

### Increment 3: O2, O3, O4 native agents, config, composition, re-install
- Spec contracts: SPEC-0001/OPENCODE_AGENT_IS_NATIVE, SPEC-0001/OPENCODE_TOOL_BOUND_IS_HOST_PERMISSIONS, SPEC-0001/OPENCODE_AGENT_COMPOSES_ITS_ALWAYS_LOADED_NODES, SPEC-0001/OPENCODE_CONFIG_IS_OPENCODE_2, SPEC-0001/OPENCODE_REINSTALL_RETIRES_OLD_SHAPE
- Files touched: `install.sh`, `tools/agent_compose.py`, `tools/graft-audit.py`, `tools/growth-audit.py`, `integrations/opencode/opencode.json`, `integrations/opencode/tool-permissions.json`, `tests/test-full-install.sh`, `tests/seed-lint.py`, `tests/test-seed-lint.sh`, `tests/test-unified-graph-install.sh`, `docs/specs/SPEC-0001-install-placement.md`
- Tests to write (RED): E19 and E20 in `tests/test-full-install.sh`, seen red on the baseline tree; E21 rows in `tests/test-seed-lint.sh`
- Behavior added: each agent is a native OpenCode 2 file named by its callable name with its permissions and composition; an unknown tool stops the render; the config carries `experimental.subagent_depth`; a re-install retires the earlier shape to backups
- Gate: `bash tests/test-full-install.sh`, `bash tests/test-install-placement.sh`, `bash tests/test-install-adoption.sh`, `bash tests/test-seed-lint.sh`
- Rollback path: revert the increment's commit
- Effort: high
- Phase: GREEN
- Depends on: increment 2

### Increment 4: O5, O6 the plugin over the shared cores
- Spec contracts: SPEC-0003/OPENCODE_PLUGIN_IS_A_THIN_ENVELOPE, SPEC-0003/OPENCODE_PLUGIN_INJECTS_THE_CORES_TEXT_ONCE, SPEC-0003/OPENCODE_SHELL_GUARD_REFUSES_WITH_THE_CORES_REASON, SPEC-0001/OPENCODE_HOOK_CORE_AND_PLUGIN_ARE_PLACED
- Files touched: `integrations/opencode/cypress-plugin.ts`, `install.sh`, `tests/test-opencode-plugin.sh`, `tests/test-prompt-hooks.sh`, `tests/test-bound-hook.sh`, `tests/run.sh`, `tools/gate-registry.py`, `docs/specs/SPEC-0003-per-prompt-injection.md`
- Tests to write (RED): X520 to X522 in `tests/test-opencode-plugin.sh`, each seen red against a deliberately broken copy; OC1 in `tests/test-prompt-hooks.sh`; five `opencode:` cases in `tests/test-bound-hook.sh`
- Behavior added: the plugin injects the cores' text once per the cores' rules, none in a child, and refuses a listed shell command with the core's reason
- Gate: `bash tests/test-opencode-plugin.sh`, `bash tests/test-prompt-hooks.sh`, `bash tests/test-bound-hook.sh`
- Rollback path: revert the increment's commit
- Effort: high
- Phase: GREEN
- Depends on: increment 3

### Increment 5: O10, O11 `--check` and the gate
- Spec contracts: SPEC-0001/OPENCODE_CHECK_NAMES_THE_EARLIER_SHAPE
- Files touched: `install.sh`, `tests/test-full-install.sh`, `docs/specs/SPEC-0001-install-placement.md`
- Tests to write (RED): E20 arms (a) to (g)
- Behavior added: `--check` names an old-shape agent or config, a missing plugin and a missing core, each with a remedy and a non-zero exit, and `--recompose-agents` covers opencode
- Gate: `bash tests/test-full-install.sh`
- Rollback path: revert the increment's commit
- Effort: medium
- Phase: GREEN
- Depends on: increment 4

### Increment 6: O9 the brief composer
- Spec contracts: SPEC-0005/CHARTER_FLAG_ONLY_FOR_PRIME_AGENT
- Files touched: `tools/brief.py`, `tests/test-brief.sh`, `docs/specs/SPEC-0005-cycle-economy.md`
- Tests to write (RED): X502 in `tests/test-brief.sh`, seen red on the baseline tree
- Behavior added: `brief.py --charter` is refused on an opencode plant
- Gate: `bash tests/test-brief.sh`
- Rollback path: revert the increment's commit
- Effort: low
- Phase: GREEN
- Depends on: increment 3

**Delegation and parallelism.** The static schedule is `python3 templates/knowledge-graph/grill-lint.py --plan docs/plans/grill-8.4.0-opencode-2.md --specs docs/specs --decisions docs/decisions --waves`. A file two increments write (`install.sh`, `docs/specs/SPEC-0001-install-placement.md`, `tests/test-full-install.sh`) is ordered by `Depends on:`.

### Increment 7: O8 the lead plays the orchestrator
- Spec contracts: SPEC-0001/OPENCODE_LEAD_PLAYS_THE_ORCHESTRATOR
- Files touched: `integrations/opencode/opencode.json`, `tests/seed-lint.py`, `tests/test-seed-lint.sh`, `tests/test-full-install.sh`, `tools/ratchet-lint.py` lock, `docs/specs/SPEC-0001-install-placement.md`
- Tests to write (RED): E23 in `case_opencode`; the opencode-default-agent row of `tests/test-seed-lint.sh`; the ratchet refusing a new exemption until the owner's decision is blessed
- Behavior added: `default_agent` names the orchestrator; opencode's modelled surface includes its charter; the exemption records 67,131 bytes by owner decision
- Gate: `bash tests/test-full-install.sh`, `bash tests/test-seed-lint.sh`, `python3 tests/seed-lint.py`, `python3 tools/ratchet-lint.py`
- Rollback path: revert the increment's commit
- Effort: medium
- Phase: GREEN
- Depends on: increment 3

## 10. Verification Plan
The standard gate holds (`CLAUDE.md` Gates: `bash tests/run.sh`), on an interpreter at the 3.14 floor, with no OpenCode 2 installed and no network. The live checks of `docs/skills/opencode-live-verification.md` are recorded separately with the host version.

## 11. Risks and Mitigations
| Risk | Probability | Impact | Mitigation | Owner | Verification | Refutation |
|---|---:|---:|---|---|---|---|
| A later OpenCode 2 release changes a plugin hook | medium | medium | every registration is guarded; the live procedure repeats the checks | steward | `docs/skills/opencode-live-verification.md` | not pressed |
| A role keeps a permission its charter does not grant | low | high | the rules deny all first and allow by the table; E19 evaluates every agent's rules | tester | E19 | `could-not-refute`, press note below |
| The shared `brief.py` change reaches Claude Code plants | low | low | the change only widens a refusal on a plant with `.opencode/agents/` | tester | X501, X502 | not pressed |

**Press note (2026-11-10).** The press took row 2, the top risk by probability × impact, and tried to find an agent holding an action its charter does not grant. It read the effective rules of all 20 projected agents from the running host's own listing (OpenCode 2.2.6, `opencode2 debug agents`, no model call), evaluated each action under the host's last-match-wins rule, and compared it with the charter's `tools:` and `delegates_to:`: no discrepancy, including the subagent allowlists. Live, a read-only agent with neither edit nor shell had its write tool removed by the host, a coordinator's launch of an agent outside its list was refused by the host ("Permission denied: subagent") and a launch inside it ran. Verdict `could-not-refute`. Blind spots: the press ran one model for the live runs, and `external_directory` is allowed for every agent that has a tool, as the host's own read-only agent has it.

## 12. Open Questions
| # | Question | Why it matters | Current assumption | How to resolve | Owner | Pinned by |
|---:|---|---|---|---|---|---|
| 1 | D1 to D4 of the decision notes | D1 and D2 are decided on 2026-11-10; D3 did not arise; D4 is set aside | the decisions stand | the notes in [`owner-decisions-8.4.0-opencode-2.md`](owner-decisions-8.4.0-opencode-2.md) | owner | none |

Row 1 is closed for this round.

## 13. Done Criteria
- Every increment in §9 is done; each new contract has a `green` §10 row in its spec.
- `grill-lint.py` lints this plan from `tests/run.sh` and passes.
- `bash tests/run.sh` is green on the floor interpreter.

## 14. Recommended Next Step
Run the release pass, `docs/skills/seed-release.md`; the tag push waits for the owner's explicit go-ahead.

## 15. Changelog
- 2026-11-10: plan opened as the record of round 8.4.0, built on 8.3.2. `tests/run.sh` `ACTIVE_PLAN` moves here from the 8.3.2 plan, so the gate holds the contracts this round adds.
