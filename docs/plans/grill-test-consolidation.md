# grill.md: Plan of Record: seed test consolidation

## 0. Metadata
- Project: CYPRESS seed
- Goal: shrink the seed's own checks to what `test-first.proportionate-checks` allows (skills/test-first/SKILL.md), by one merged plan over the four test reviews
- Date: 2026-09-29
- Owner: the steward; the orchestrating session plans, briefs and commits
- Tier: T3. Protocol: `protocol.grill`
- Current phase: done (2026-09-29). Every increment applied, the review fixes landed, and the F2 close-out is recorded in §15. Uncommitted in the seed; the commit and the release name are the session's call
- Inputs (plant records, `.seed-worktrees/records-unreleased-proportionate-checks/`): test-review-A-seed-lint.md, test-review-B-graph-linters.md, test-review-C-install-and-harness.md, test-review-D-tools.md, owner-steer-test-review.md. Per-case reasoning lives there and is not restated here
- Owner steer (binding): SIMPLIFY > FOLD/MERGE > DEDUPLICATE > DELETE. Reviewers B and C wrote before the steer; this pass re-ran their DELETE verdicts under it
- Related specs: SPEC-0001, SPEC-0002, SPEC-0003, SPEC-0004, SPEC-0005 (amended by S1-S5, §3)
- Code anchor: line numbers and `wc -l` figures read from the seed working tree on 2026-09-29 (HEAD d6ec78c plus the uncommitted proportionate-checks edits). Re-check a cited line before editing it
- Version: not recorded (the release name is the session's call)

### Changes this pass made to the reviewers' verdicts
- DELETE turned into FOLD (assertion kept): PromotionTests negatives x4 and InferenceTests backslash/bare-Dockerfile/first-path x3 (rows in the survivor tables); grill X378 (one assertion inside X377); test_gate_pool bare-command label (one step line in test_run_parallel); nested-checkout CYPRESS_ROSTER_DIR override (one run inside caseROSTER_DEFAULT_RESOLVES_INSIDE_THE_SEED; the knob is documented in DOCUMENTATION.md); Prime overlay X139/X140 (one identifier and one word ban inside X141); X339/X340 ratchet cases (moved to a new tests/test-ratchet-lint.sh, see §1.1); front-door GLOSSARY_PATHS_EXIST and the mechanism-path half of MECHANISM_CLAIMS_TRACED (rows of the kept anchors check); front-door figure checks (scope rows of the merged `check_published_figures`); check_delegation_split key-home arm (rows of the adopted-rule-homes map); test_metadata_equivalence.py (its two tables move into their subjects' files and the file goes); test-knowledge-paths.sh (one forbidden-pattern row of seed-lint's new text-rules table).
- Cuts rejected (the check is cheaper than the spec edit its removal needs, or it pins a live contract): C case_codex ADR-0009 match (SPEC-0001 LEGACY_INSTALL_PRINTS_DEPRECATED names it); C case_k7_no_history "exactly one line" (SEED_HISTORY_UNAVAILABLE says one line); C caseALL_NAMES_SKIPPED_FROZEN_HOSTS skip-names arm (it is the contract; only the exact line formats go); D X109 "loaded" ban (invariant I-6, one line); D test_prose_lint_one_step_per_file real-run.sh half (holds SPEC-0004 PROSE_FLOOR_HELD_PER_FILE, which stays).
- Move rejected: A's move of `check_spec_test_mapping` into spec-lint.py. spec-lint ships into plants, so the move adds a check to every plant's runs ("the seed adds none"). The check is simplified inside seed-lint.py instead; case_23/case_36 stay as table rows.
- DEDUP separated from DELETE: a case removed because a named survivor already asserts the same thing drops nothing, so it is listed in its §3 increment, not in §4.

## 1. Summary

Measured with `wc -l` on 2026-09-29. "After" figures are the reviewers' per-case estimates, adjusted for this pass's changes; each batch records measured figures in its handback. "Check lines" is every line under tests/ in the group (tests, gates, harness, check data). "Subject" is the code those lines exercise: whole-file `wc` where a file is the subject, the reviewer's slice estimate where only part is.

| Group | Check lines now | Subject now | Ratio now | Check lines after | Subject after | Ratio after |
|---|---|---|---|---|---|---|
| A seed-lint, legal-lint, ratchets, floors | 11202 (gates 6211 + tests/data 4991) | 6884 (seed-lint.py 5841, legal-lint.py 370, ~673 code slices, est) | 0.72 (tests/data only) | ~3275 (gates ~2520 + tests/data ~755) | ~3193 | ~0.24 |
| B graph linters | 7918 | 6541 | 1.21 | ~4860 | 6541 | ~0.74 |
| C install suites and gate harness | 5639 (suites 4687 + harness/unit 952) | 3453 (install.sh 2561, harness 662, ~230 slices, est) | 1.63 | ~2770 | ~3141 | ~0.88 |
| D tools | 8001 | 7537 | 1.06 | ~5200 | 7537 | ~0.69 |
| Fixtures (tests/fixtures) | 2282 | - | - | ~1160 | - | - |
| Total, excluding fixtures | 32760 | 23512 distinct | 1.39 | ~16100 | ~19509 distinct | ~0.83 |
| Total, excluding fixtures and the two gates | 26549 | 23512 | 1.13 | ~13580 | ~19509 | ~0.70 |

- Removed: ~16660 check lines (51%) and ~1120 fixture lines.
- Group A's gates are both checks and subjects: seed-lint.py is the subject of test-seed-lint.sh, and its own subject is the seed's prose tree, which has no code ratio. The A ratio counts only the tests and check data.
- Distinct subject total: A's two gates 6211 + B 6541 + install.sh 2561 + harness 662 + D 7537. Slices already inside another group's files are not counted twice. Subject falls after the plan because seed-lint.py (~5841 to ~2150) and the harness (662 to ~350) shrink.
- Owner-confirm lines in §4: 97.

### 1.1 Survivor claims the reviewers left unverified (read in code this pass)
1. C: graph-lint's duplicate fact-key check covers `tiers.contained-lane` single ownership. PARTLY. Two owners fail: templates/knowledge-graph/graph-lint.py:455-465 (message at :462) in a plant, and tests/seed-lint.py:3559-3562 on the seed tree every gate run. seed-lint walks core/method/*.md (:3459-3460), so seed-lint is the stronger survivor. Zero owners, or a move out of core/method/tiers.md, fail nowhere (test-tier-lanes.sh:23-28 held that half, and the same for `canonize.why-record`). The dropped half is §4 line 54.
2. B: test-full-install.sh holds golden-corpus parity. YES. `projection_parity` (test-full-install.sh:62-83) requires `_routes.golden.tsv` in both directories (:65-66) and `cmp`s every shared file (:82). It runs on the claude-code projection at :188 and :840, and the prime-agent corpus is `cmp`ed at :377-379. test_agent_lint.py:1959-1985 is an unconditional SkipTest, so its removal is DEDUP.
3. A: does tools/ratchet-lint.py (310 lines) have its own tests? NO. Its refusal path is exercised only by test-seed-lint.sh X339/X340 (`ce_expect_ratchet`, :2942-2947, cases near :2996 and :3008) and its accept path by `fd_ratchet_accepts` (:1722-1725). test_agent_lint.py:1160-1169 only runs it on the real tree, which duplicates run.sh:299. A's DELETE of X339/X340 would leave the tool's refusal untested, so they FOLD into a new tests/test-ratchet-lint.sh (increment I4).
- Also verified: `unittest` exits 5 with "NO TESTS RAN" when a suite collects nothing (Python 3.14 here; CI pins 3.12 at .github/workflows/gate.yml:38, and 3.12 is where the exit code arrived). That is the survivor for the zero-collection half of collected.json.
- Also verified: CYPRESS_ROSTER_DIR is documented in DOCUMENTATION.md, so its test is simplified, not deleted.

## 2. Patterns and their doctrine cause

| Pattern (reviews) | Doctrine cause | Fix in this plan |
|---|---|---|
| Spec size sets test count: one case per §4 contract and §7 failure, variant loops per boundary (A1, B P1, D P1) | rule.spec plus §10 "one case per contract and failure"; contracts written as test fixtures (SPEC-0003 Given clauses carry 40 ledgers, 300 temp files, hard links) | table-driven survivors; S1-S5 amend contracts to behavior; §5 (a), (e) |
| Prose held by code: wording pins, doc mirrors kept in sync by a lint (A1, B P5, C3, D P3) | "every behavior gets an executable spec" applied to documentation; one home per fact enforced by syncing copies instead of removing them | SPEC-0004 retirements, reference-table and host-matrix mirrors cut, test_tool_authorship.py and test_brainstorm_modes.py deleted; §5 (g) |
| Full rigor everywhere: planted mutant per arm, guards, mutation proofs of helpers (A2, B P2, C4, D P5) | `delegation.mutation-at-end` rigor used as the default test shape | variant cuts, self-test cuts; §5 (h) |
| Every incident becomes a permanent gate, told in the test file (A3, B P3, C1, C2, D P4) | "an escaped bug earns a regression test" with no fold step and no retire path | folds into the contract's existing case; rule R4; §5 (b), (c) |
| Anti-shrink machinery: floors, binder, ratchets restated in three places (A4) | the ratchet doctrine reads a smaller suite as a regression | I4 |
| Costly setup per case: whole-tree tar, a fresh install per case (A5, B P6, C5, D P6) | "run the expensive action once" was not applied | I3 helpers, adopted per batch |
| Test in the wrong file: verify-ledger in grill, install.sh in legal and budgets, four subjects in test-bound-hook.sh (A6, B P7, C6, D) | no rule that a test sits in its subject's file | moves in B3, C1, C3, D1a; §5 (d) |
| Re-implementing the subject: TS tokenizer, ledger validator, YAML shim, vocabulary extraction, a seed-lint constant probed from an install (B, C6, D P2) | "a test is cheaper than its subject" absent when written | D1b, D3, B5, C1 |
| Real-tree duplicates of run.sh steps (B P4, D P7, A: collected-count) | "every deleted test names its survivor" never run in reverse when a test is added | DEDUP lines in each batch; §5 (j) |
| Consumer pins: real roster, real plan, real vocabulary golden (B P5) | test-first "test reusable code over its consumers" not applied | B2, B3, B5 |
| Frozen hosts under full regression (C5) | ADR-0009 tiers not mapped to test depth | C1, C2b; §5 (i) |
| Environment-fragile checks: clock, euid, timing, a tag on this checkout (D P8, C) | none; hermeticity is not stated anywhere | I2, D1b, D3, C2b |

## 3. Increments

### Rules for every batch
- R1 A fold keeps the survivor's existing name or label. The folded case's label (X1NN, M9, D1, S12 ...) stays in the survivor as a comment or row id, so each spec §10 row stays bound (`check_spec_test_mapping` binds a shell row by label).
- R2 A deleted case with no survivor retires its contract in the S increment. SPEC_UNCOVERED_BUDGET is never loosened.
- R3 No whole-tree tar copies. Copy only what the tool reads (`mini_tree`, I3).
- R4 History leaves test files. One "why" line per case at most; the history is in CHANGELOG and the plans.
- R5 No new assertion beyond the rows this plan names.
- R6 A fold that writes a new assertion line (not a moved one) is seen red once by a scratch edit of the subject, then reverted. Moved lines need no re-proof.
- R7 Do not edit tests/run.sh or tools/gate-registry.py (F1 owns both). Run new and renamed files directly in the batch gate.
- R8 Batch gate: run the affected suites once at the end of the batch. A red that pins old wording is listed in the handback; any other red stops the batch. Record `wc -l` before and after for each touched file.
- R9 Only §4 lines the owner confirmed are applied. An unconfirmed line leaves its case as it is.

### Wave 1: bugs and helpers (parallel)

#### I1: test-legal-lint.sh leaks $TMP
- Item: bug. Line 16 sets `trap 'rm -rf "$TMP"' EXIT`; line 250 replaces it with `trap 'rm -rf "$CTMP"' EXIT`, so $TMP (a whole-tree copy) is never removed
- Spec contracts: none
- Files: tests/test-legal-lint.sh
- RED: run the suite and see the $TMP directory left behind
- Change: one trap at the top that removes both (`"$TMP" "${CTMP:-}"`); drop the second trap
- Lines: 322 -> 322
- Gate: `bash tests/test-legal-lint.sh`, then confirm no leftover temp directory
- Effort: low. Phase: GREEN (implementer). Depends on: none

#### I2: GR-h depends on this checkout having no tag
- Item: bug. `gr_fixture` (test-graft-tools.sh:1342) installs a plant stamped with this checkout's version. When `v<version>` exists (v7.32.1 does), graft-ledger finds the tag, and GR-h's "inferred by content lineage" precondition fails
- Spec contracts: none
- Files: tests/test-graft-tools.sh
- RED: GR-h fails on this checkout
- Change: in `gr_fixture`, before the commit, set `.cypress/seed.json` `version` to a value with no tag (for example `0.0.0`). If another GR case reads that version, give GR-h its own copy of the fixture instead
- Lines: 1525 -> ~1527
- Gate: `bash tests/test-graft-tools.sh`
- Effort: low. Phase: GREEN. Depends on: none

#### I3: shared helpers
- Item: shared setup
- Files: tests/helpers/plant.sh (new), tests/helpers/lintcase.sh (new)
- Change: plant.sh has `plant_base <hosts> [flags]`, which installs once per suite into a cache keyed by hosts and flags, and `plant_copy <dst>` (`cp -a`). A case that asserts first-install behavior still installs fresh. lintcase.sh has `expect_rc <rc> <needle> -- <cmd>`, `mini_tree <dst> <paths...>`, and the `collect_case` collector promoted from test-graft-tools.sh, so each label shows its own result in one run. Python suites use `setUpModule` for one install per file and need no shared file
- Lines: 0 -> ~90
- Gate: `bash -n` on both files; source plant.sh and build one claude-code base in a temp directory
- Effort: low. Phase: GREEN. Depends on: none

### Wave 2: machinery and spec amendments (after owner confirmation)

The brief lists machinery after the cuts. It runs here instead: while it stands, each cut pays extra edits (table below). If the owner keeps some machinery (§4 lines 91-97), the cuts pay those edits.

| Machinery | Edits each cut forces while it stands |
|---|---|
| tests/collected.json floors | every Python suite that shrinks lowers its floor: B1 (test_graph_lint 62), B2 (test_agent_lint 69), B5 (test_router_reach 9, test_frontmatter_contract 9, test_metadata_equivalence 18 removed), C4 (test_run_parallel 8, test_gate_pool 11), D4 (test_gate_registry 13; test_tool_authorship 12 and test_brainstorm_modes 8 removed) |
| tests/check-coverage-binder.py | A1a and A1b edit COVERED/UNPROTECTED for each deleted or merged `check_*`, and INLINE_ASSERTION_DEBT as inline assertions in `check()` move |
| ratchet limits (tools/ratchet-lint.py RATCHETS + tests/ratchets.json value and direction) | 4 edits to retire one limit (constant, RATCHETS row, lock value, lock direction) plus the CHANGELOG line the tool demands. A1a retires 8 limits (FIRST_HEADING_MAX_LINE, FIRST_SCREEN_MAX_LINES, FIRST_COMMAND_LINE, README_CATALOG_CEILING, LIMITS_MIN_REQUESTED, LIMITS_MIN_UNMEASURED, DEFINITION_OVERLAP_CEILING, FRONT_DOOR_PENDING); A1b retires 3 (CHARTER_VOCAB_DEBT, PREVENTS_OVERLAP_CEILING, PREVENTS_RESTATEMENT_CEILING); I4 retires INLINE_ASSERTION_DEBT |
| SPEC_UNCOVERED_BUDGET (max 2) | none, under R2 |
| run.sh step + GATES entry per file | 2 edits per deleted or added file; F1 does them all once. Kept: this is what the registry is for |
| spec §10 rows | deliberate by kernel §4; done in S1-S5 and D1a. Kept |

#### I4: anti-shrink machinery
- Item: machinery (§4 lines 91-97)
- Files: tests/check-coverage-binder.py (delete), tests/collected.json (delete), tests/test-collected-count.sh (delete), tools/ratchet-lint.py, tests/ratchets.json, tests/test-ratchet-lint.sh (new), tests/test-seed-lint.sh (remove the binder call and cases X339/X340)
- Change:
  - Delete the binder and its call. Delete INLINE_ASSERTION_DEBT from the lock.
  - Delete the floors file and its runner. Zero collection is caught by unittest's exit 5; a partial drop is the recorded loss (§4 line 93).
  - ratchet-lint gets one home for its registry. Each lock entry holds source, attribute, direction and value; the RATCHETS table in ratchet-lint.py goes, and so do the "recorded but not registered" and "direction changed without the lock" checks, which cannot happen with one list. The "constant vanished" check stays. Retiring a limit then takes 2 edits (constant and lock entry).
  - tests/test-ratchet-lint.sh: X339 (ceiling raised gives exit 1) and X340 (set member added gives exit 1) move here, as two rows on a synthetic lock and source file in a `mini_tree`. Labels are kept.
- RED: none new; X339/X340 are moved assertions (R6)
- Lines: binder 179 -> 0; collected.json 15 -> 0; test-collected-count.sh 54 -> 0; ratchet-lint.py 310 -> ~230; ratchets.json 149 -> ~150; test-ratchet-lint.sh 0 -> ~40; test-seed-lint.sh -~40
- Gate: `python3 tools/ratchet-lint.py`; `bash tests/test-ratchet-lint.sh`; `python3 tests/seed-lint.py`
- Effort: medium. Phase: GREEN. Depends on: I3 (mini_tree)

#### S1-S5: spec amendments
Architect-owned, deliberate (kernel §4). Each lands before the cuts that need it. Each changes §4/§6/§7 text, removes the §10 rows of retired contracts and deleted cases, and points rows of folded cases at the survivor's existing label (R1). Survivor names do not change, so the rows stay bound before and after the cuts. Gate for each: the spec-lint step (`python3 templates/knowledge-graph/spec-lint.py --specs docs/specs --root . --uncovered-budget <SPEC_UNCOVERED_BUDGET>`) and `python3 tests/seed-lint.py`. Effort: medium. Phase: spec (architect). Depends on: owner confirmation; S5 also on I4.

| Inc | Spec | Section | What changes | Version |
|---|---|---|---|---|
| S1 | SPEC-0001 (870 lines) | §4 HOST_TIERS_AGREE | drop the clauses on the host-capability-matrix tier table (§4 line 10) | no version line (not recorded); dated §12 entry, status_date |
| S1 | SPEC-0001 | §10 | SYMLINK_MODE_IS_UNIFORM: M9 inside case_symchurn. PREFLIGHT_REFUSES_BEFORE_WRITING, DESTINATION_PATH_OCCUPIED, TARGET_NOT_WRITABLE: D1 inside case_block_declared and case_block_readonly. ALL_CHECK_INCLUDES_RECORDED_COPILOT: the "one DEPRECATED line in each arm" clause leaves the row (E2 holds it). SESSION_RECORD_FORM_IS_PLACED: S9 inside case_plan_records. STAMP_NOT_AN_OBJECT: S12 inside case_s7. EXISTING_PLANT_RECEIVES_CURRENT_ENGINES: S10 keeps the re-install half; the reconcile and audit half cites X383 and X387. RECREATED_LIST_IS_COMPLETE: header checked by prefix. CODE_ANCHOR_TOOL_IS_PLACED second check: the M7 sweep. ENGINE_AUDIT_CHECKS_EVERY_PAIR: X388 inside X389. EVERY_BACKUP_IS_CLASSIFIABLE: X391 and X392 as rows of X390; M8's UNMAPPED arm held by X390's second arm. HOST_TIERS_AGREE: E4 reduced to two rows | same entry |
| S2 | SPEC-0002 (456) | §4 | retire A_STEM_COLLISION_IS_REVIEWED_BEFORE_IT_SHIPS (§4 line 53) | no version line and no §12; add §12 with a first dated entry, as SPEC-0001 did |
| S2 | SPEC-0002 | §10 | THE_ADVERSARIAL_BUDGET_IS_RATCHETED_NOT_ZERO: test_exceeding_the_budget_fails_the_gate only; the ratchet clause cites the ratchet-lint step. AN_ABSOLUTE_FLOOR_IS_KEYED_TO_ITS_ROSTER: the value-unchanged row goes (§4 line 52). RARITY and COMPOUND_FRAGMENT rows point at the two survivor tables (test_a_rare_word_in_a_real_trigger_still_dominates, test_a_compound_fragment_does_not_earn_a_confident_route). HELD_OUT_SET_MAY_NOT_BE_EMPTIED: test_a_padded_trigger_copy_cannot_pass_as_held_out. NEITHER_HELD_OUT_SET_MAY_BE_THINNED: test_emptying_a_whole_class_is_refused | same entry |
| S3 | SPEC-0003 (1948) | §4 | retire STATUS_HOOK_RESET_OWNS_NO_PATH_RULE and PRIME_OVERLAY_RESTATES_NO_KERNEL_RULE. Rewrite HOOK_TEXT_RESTATES_NO_KERNEL_RULE as a byte budget on the injected hook text. Narrow PRIME_OVERLAY_KEEPS_SURFACED_SET to naming `_cypress_surfaced`. Drop fixture clauses: LEDGER_REFRESH_EVERY_N rewrite-to-3; LEDGER_WRITE_IS_ATOMIC hard-link Then (the failed-replace And stays); LEDGER_SYMLINK_REFUSED 5 shapes to 3; LEDGER_GC_BOUNDED removal order and the 300-file And; LEDGER_WRITE_FAILURE_FAILS_OPEN read-only-directory branch and three-prompt oversize; id, corrupt-shape, source and stub-mode counts in LEDGER_INVALID_SESSION_ID_FULL, LEDGER_CORRUPT_FULL, STATUS_HOOK_RESETS_LEDGER, STATUS_HOOK_NO_LEDGER_WRITES_NOTHING, ROUTER_OUTPUT_WITHOUT_ECHO_PREFIX_POINTER_ONLY, ROUTE_HOOK_UNPASSABLE_PROMPT_FAILS_OPEN; ROUTE_EXTENSION_* to substring level; ROUTE_EXTENSION_HOLDS_NO_LEDGER_STATE to the fs-write ban; STATUS_EXTENSION_INJECTS_THE_ANCHOR_LINE and the X164/X165 clauses; ANCHOR_RECORD_NAMES_EVERY_REPOSITORY key set, mode and ISO format; ANCHOR_RECORD_REFUSES_A_SYMLINK hard-link half; STATUS_HOOK_ANCHOR_FAILURE_FAILS_TOWARD_INCLUSION to 2 causes and 1 register state (§4 lines 7, 31, 69-80) | no version line; dated §12 entry, status_date; §0 sign-off line gets a dated amendment note |
| S3 | SPEC-0003 | §10 | rows follow the folds: X105 in X106; X108 in X109; X112 split over X106, X107, X110, X113, X120, X123; X116 in X107; X121 and X122 in X120; X129's fault half in X133; X147 in X143; X149 in X134; X151 in X110; X166 in X160; X136 and X150 in X135; X139 and X140 in X141; X201 becomes the byte-budget row; X202 and X203 go. Remove the technique bullets for rewrite-to-3 and the hard link, and the binder bullet. The file column change to the split files rides with D1a | same entry |
| S4 | SPEC-0004 (2347) | §4 §6 §7 §10 | retire 15 contracts (§4 lines 14-21, 23-29) with their §7 failures, §6 caps and §10 rows. Keep 7: FRONT_DOOR_ANCHORS_RESOLVE, GLOSSARY_PATHS_EXIST (held as a row of the anchors check), MECHANISM_CLAIMS_TRACED (narrowed to "each named mechanism path exists", also a row of the anchors check), INSTALL_SECTION_NAMES_TARGET_PATHS, EAGER_FIGURES_CHECKED_WHEREVER_PUBLISHED and BODY_FIGURES_HAVE_A_REQUIRED_HOME (scope rows of `check_published_figures`), PROSE_FLOOR_HELD_PER_FILE. Remove FRONT_DOOR_PENDING and the binder from the text; status stays `implemented`; update status_evidence | no version line; dated §12 entry, status_date |
| S5 | SPEC-0005 (2506) | §4 §6 | DELEGATION_SPLIT_INTO_SIBLINGS: key homes held by the ADOPTED_RULE_HOMES map; drop the peers and Neighbours clauses. AGENT_DECLARES_EFFORT: drop "each shipped agent's effort equals its row in the §6 default table", and replace the §6 per-agent effort table with a pointer to the agents' frontmatter (one home). LEAF_BODY_CEILING_HELD: drop the stale and unknown member clauses. ADOPTED_RULE_HOMES: drop the wrapped and scoped stale-pointer clauses. KERNEL_POINTS_AT_THE_SESSION_RECORD: drop the moved and emptied-directory plants. GRILL_WAVES_LEAVES_THE_GATE_UNCHANGED: drop the golden clause | 0.13 -> 0.14; dated §12 entry; §0 Version line |
| S5 | SPEC-0005 | §10 | remove rows: test_plan_warns_on_wide_descent, test_plan_long_token_flood_does_not_use_the_cap, test_plan_cap_counts_only_path_like_tokens, test_plan_token_of_exactly_256_is_considered, test_plan_scored_and_hit_prints_no_suffix, test_plan_promoted_and_inferred_prints_promotion_only, test_delegation_phrase_is_a_load_when_entry, test_lint_real_roster_effort_matches_the_table, X337, X338, X342-X345, X356-X360, X365, X379. Repoint: promotion negatives and folds in test_plan_promotes_expertise_past_the_scored_cut and test_plan_partial_phrase_does_not_promote; inference folds in test_plan_infers_from_extension; descent folds in test_plan_descends_on_specific_term; X339 and X340 to tests/test-ratchet-lint.sh; X341 in X336; X343 in X347; X350-X355 kept as labels of text-rules rows; X362-X364 in X361; X367-X370 in X366; X371-X376 and X380 in X373; X378 in X377. HOSTILE_TASK_LINE note: cap and length boundaries are untested by decision (report-only surface). Remove the binder sentence | same entry |

### Wave 3: consolidation batches (parallel; file sets are disjoint)
Every batch: Phase GREEN (implementer), rules R1-R9, gate = the listed suites once at the end. DEDUP lines name the survivor and are not in §4.

#### A1a: seed-lint front-door block
- Spec contracts: SPEC-0004 (after S4)
- Files: tests/seed-lint.py, tests/test-seed-lint.sh, tests/fixtures/front-door/, tests/ratchets.json
- Change: delete the 15 retired `check_fd_*`, their FD constants, the pending-ledger machinery (`fd_guard`, raised handling), their fd cases and the fd harness robustness cases (X326-X328). Keep `check_fd_front_door_anchors_resolve` with a minimal parser. Keep `check_fd_install_section_names_target_paths`. Leave `check_fd_eager_figures_checked_wherever_published` and `check_fd_body_figures_have_a_required_home` as they are; A1b merges them into `check_published_figures`. Fold `check_fd_glossary_paths_exist` and the path half of `check_fd_mechanism_claims_traced` into the anchors check as rows. Cut `fd_py` to ~40 lines for the kept rows. Shrink the fixtures to a minimal README, INSTALL and glossary. Retire the 8 ratchet limits
- Lines: seed-lint.py 5841 -> ~4550; test-seed-lint.sh ~3380 -> ~2650; fixtures/front-door 643 -> ~100
- Gate: `python3 tests/seed-lint.py`; `bash tests/test-seed-lint.sh`; `python3 tools/ratchet-lint.py`
- Effort: medium. Depends on: I4, S4

#### B1: test_graph_lint.py
- Spec contracts: SPEC-0005 promotion, inference, descent and closure rows (after S5)
- Files: tests/test_graph_lint.py, tests/test-graph-artifacts.sh (delete), tests/fixtures/root.md (delete; only test-graph-artifacts.sh uses it)
- Change: B's §3 verdicts, plus these folds: the promotion negatives (partial version token, short words, stopwords, prefix fold) become rows of test_plan_partial_phrase_does_not_promote; backslash-only token, bare Dockerfile and first-path-in-task-order become rows of test_plan_infers_from_extension. Add one unit case for a missing artifacts path (from test-graph-artifacts.sh). Use one `setUpModule` install for SeedAndPlantCopyAgreeTests and DelegationRoutingTests. Use one shared router fixture graph. DEDUP: test_delegation_phrase_is_a_load_when_entry (survivor test_delegation_sibling_routes_on_its_phrase)
- Lines: 2788 -> ~1510; test-graph-artifacts.sh 29 -> 0; root.md 24 -> 0
- Gate: `python3 tests/test_graph_lint.py`
- Effort: medium. Depends on: S5

#### B2: test_agent_lint.py and test-nested-checkout.sh
- Spec contracts: SPEC-0002 and SPEC-0005 AGENT_DECLARES_EFFORT (after S2, S5)
- Files: tests/test_agent_lint.py, tests/test-nested-checkout.sh
- Change: B's §3 verdicts. Tables keep existing names (R1). DEDUP: test_lint_real_roster_passes (run.sh:253 runs `agent-lint.py --lint --dir agents`); test_eval_real_golden_meets_threshold (run.sh:254 runs `--eval`); test_triggers_parse_from_real_agent_def (run.sh:253); test_the_shipped_corpus_sits_under_the_budget (run.sh:254); test_the_budget_is_ratcheted_shrink_only (run.sh:299); test_golden_corpus_copies_are_byte_identical (§1.1 item 2); test_the_original_misroute_no_longer_routes_confidently_wrong (golden row 178 under `--eval` with CONFIDENT_WRONG_BUDGET 0 [verify: the budget counts the paraphrase class; if not, the case stays]). Nested checkout: C's verdicts, but the CYPRESS_ROSTER_DIR override is kept as one run inside caseROSTER_DEFAULT_RESOLVES_INSIDE_THE_SEED
- Lines: test_agent_lint.py 1989 -> ~1085; test-nested-checkout.sh 379 -> ~180
- Gate: `python3 tests/test_agent_lint.py`; `bash tests/test-nested-checkout.sh`
- Effort: medium. Depends on: S2, S5

#### B3: test-grill-lint.sh and verify-ledger
- Spec contracts: SPEC-0005 GRILL_WAVES_* (after S5)
- Files: tests/test-grill-lint.sh, tests/test-verify-ledger.sh (new), tests/fixtures/grill/fixture-plan.plain.golden (delete)
- Change: B's §3 verdicts; one harness family on lintcase.sh; X378's assertion (no report line in plain output) becomes one check inside X377; the verify-ledger cases move to their own file, with multi_table_changed_byte folded into multi_table. DEDUP: X365 (survivor X361)
- Lines: 1051 -> ~640; test-verify-ledger.sh 0 -> ~75
- Gate: `bash tests/test-grill-lint.sh`; `bash tests/test-verify-ledger.sh`
- Effort: medium. Depends on: I3, S5

#### B4: small lint suites
- Files: tests/test-spec-lint.sh, tests/test-status-register.sh, tests/test-agnosticism-lint.sh, tests/test-lint-audibility.sh
- Change: B's §3 verdicts; `mini_tree` in place of tar. DEDUP: agnosticism case 8 (seed-lint.py:4035 onward calls `scan` and `iter_files` in the gate); the four lint-audibility "clean still passes" halves (each tool's own case 1 or 3); status-register empty-root sub-check (case 6)
- Lines: 466 -> ~360; 373 -> ~300; 140 -> ~115; 186 -> ~120
- Gate: the four suites
- Effort: low. Depends on: I3

#### B5: router and frontmatter tests
- Spec contracts: SPEC-0002 A_STEM_COLLISION (after S2)
- Files: tests/test_router_reach.py, tests/test_frontmatter_contract.py, tests/test_metadata_equivalence.py (delete), tests/fixtures/router/stem-collisions.json (delete)
- Change: StemCollisions and `_bless` go. The metadata-equivalence router tests fold into one `test_routers_score_alike` table in test_router_reach.py (subject: both routers' scoring). The status-register reader tests fold into one table in test_frontmatter_contract.py (subject: the readers agree with frontmatter.py). test_frontmatter_contract runs over the canonical copy only. Add a plain double-quoted title row to its quoting test so test_quoted_scalar keeps full coverage. DEDUP: test_all_five_implementations_import (module-level load errors the file); the four reader-wrapper tests (test_frontmatter_contract survivors named in review A §3c)
- Lines: 321 -> ~180; 149 -> ~155; 611 -> 0; fixture 551 -> 0
- Gate: `python3 tests/test_router_reach.py`; `python3 tests/test_frontmatter_contract.py`
- Effort: medium. Depends on: S2

#### C1: test-full-install.sh and the prose-pin files
- Files: tests/test-full-install.sh, tests/test-entry-paths.sh (delete), tests/test-tier-lanes.sh (delete), tests/test-orchestration-entry.sh (delete), tests/test-seed-budgets.sh (delete)
- Change: C's §3 verdicts except the rejected cuts (§0); plant.sh base installs; the entry-paths routing asserts fold into case_claude_code; the codex hostile-path case from test-seed-budgets.sh becomes one install into one directory name holding all 7 characters, inside case_codex (it keeps helpers/codex-path-roundtrip.py). DEDUP: `_coexist` x2 (K5); case_idempotent_rerun (M3); case_router_fast_forward and case_code_anchor_tool `_fast_forwards` (case_recover sentinel sweep); settings.json backup and --force arms (M4, case_recover); case_opencode negative DEPRECATED arm (caseALL_EXCLUDES_LEGACY_HOSTS); case_prime_agent lint and eval (case_universal_router); case_seed_stamp tool membership (plant-state case_s1_s2_s5); entry-paths kernel budget (seed-lint KERNEL_BUDGET); tier-lanes duplicate-owner half (§1.1 item 1); test-seed-budgets run_budget_probe ceiling and eager arms (A1b rows from case_17 and case_22)
- Lines: 928 -> ~460; 249, 99, 89, 240 -> 0
- Gate: `bash tests/test-full-install.sh`
- Effort: medium. Depends on: I3, S1

#### C2a: placement and kernel modes
- Files: tests/test-install-placement.sh, tests/test-install-kernel-modes.sh
- Change: C's §3 verdicts. case_m9 folds into case_symchurn; K6 into K1/K4; K2 uses tar without .git. DEDUP: case_m8 UNMAPPED arm (X390, §3 S1); the kernel-modes EXIT guard on core/AGENTS.md (run.sh `_seed_digest`)
- Lines: 879 -> ~440; 308 -> ~195
- Gate: both suites
- Effort: medium. Depends on: I3, S1

#### C2b: adoption and unified graph
- Files: tests/test-install-adoption.sh, tests/test-unified-graph-install.sh
- Change: C's §3 verdicts; one copilot install for the three check sub-cases. DEDUP: case_index (case_pre_growth_pointer); case_d1_file (case_block_declared); case_d2 (case_d5_recreated_list, case_freshquiet, case_nostamp); case_idem (M3); ALL_CHECK DEPRECATED-count arms (E2); unified case_seed_stamp (plant-state case_s1_s2_s5, case_stamp_keys); unified case_kernel --force arm (M4)
- Lines: 716 -> ~380; 286 -> ~165
- Gate: both suites
- Effort: medium. Depends on: I3, S1

#### C3: plant state and legal
- Files: tests/test-plant-state.sh, tests/test-legal-lint.sh
- Change: C's plant-state verdicts. The install.sh legal placement and jurisdiction cases move from test-legal-lint.sh into test-plant-state.sh and merge with case_s6 and case_drift; name the survivor for each arm. test-legal-lint.sh keeps review A's lint verdicts, with synthetic pages in a `mini_tree` of legal-corpus/ and legal-lint.py. DEDUP: case_s4 (case_drift); case_edited (case_recover sweep); case_corpus_linkmodes copy arm (case_s6); case_engine_upgrade graft half (test-graft-tools X383-X387); legal final re-lint (baseline 0); legal 8b plain "Italian" (case 8)
- Lines: 662 -> ~390; 322 -> ~135
- Gate: both suites
- Effort: medium. Depends on: I1, I3, S1

#### C4: harness units
- Files: tests/run-parallel.py, tests/gate_pool.py, tests/test_gate_pool.py, tests/test_run_parallel.py
- Change: C's verdicts; the bare-command label becomes one step line in test_run_parallel's folded red case. DEDUP: DispatchTests (test_run_parallel); test_serialized_single_worker_still_aggregates and test_high_concurrency_does_not_drop_a_failure (folded red case)
- Lines: 67 -> 30; 277 -> 200; 169 -> 52; 96 -> 45
- Gate: `python3 tests/test_gate_pool.py`; `python3 tests/test_run_parallel.py`
- Effort: low. Depends on: none

#### D1a: split test-bound-hook.sh by subject
- Spec contracts: SPEC-0003 §10 file column
- Files: tests/test-bound-hook.sh, tests/test-prompt-hooks.sh (new: route-hook, status-hook, Prime extensions), tests/test-code-anchor.sh (new: tools/code-anchor.py), SPEC-0003 §10 (file column only, and the placement paragraph)
- Change: move cases without editing them, then apply D's code-anchor verdicts in test-code-anchor.sh (X166 into X160). The Copilot fail-open block folds into X118 and X124 in test-prompt-hooks.sh
- Lines: 2537 -> bound-hook ~150 + prompt-hooks ~1880 + code-anchor ~400
- Gate: the three suites
- Effort: medium. Depends on: S3

#### D2: test-growth-audit.sh
- Files: tests/test-growth-audit.sh
- Change: D's verdicts: plant.sh bases (24+ installs to ~4), a `patch_record` helper in place of the 95 heredocs, one all-ABSENT fixture, and the listed folds (29, 30 into 28; 47, 48 into 46; 53-57 and 67 into 52; 59, 60 into 58; the three walk scenarios into one)
- Lines: 2550 -> ~1700
- Gate: `bash tests/test-growth-audit.sh`
- Effort: medium. Depends on: I3

#### D3: graft tools and tool corpus
- Files: tests/test-graft-tools.sh, tests/test-tool-corpus.sh
- Change: D's verdicts (GT02 into GT04; GT12, GT13 into GT07; X388 into X389; X391, X392 into X390; GL-b, GL-b2 into GL-a; GT15 CLI half only; tool-corpus §3 JSON fixtures in place of the YAML shim; §5 cut)
- Lines: ~1527 -> ~1275; 508 -> ~330
- Gate: both suites
- Effort: medium. Depends on: I2, S1

#### D4: registry, release and two prose files
- Files: tests/test_gate_registry.py, tests/test_prepare_release.py, tests/test_tool_authorship.py (delete), tests/test_brainstorm_modes.py (delete)
- Change: D's verdicts, except that test_prose_lint_one_step_per_file keeps its real-run.sh half. DEDUP: the three RealTreeTests duplicates (run.sh:301 `gate-registry.py --lint`); test_help_exits_zero (test-tool-help.sh); test_plain_semver_reads_cleanly (fold); test_tool_authorship RULE_HOMES and manifest items and test_brainstorm_modes test_each_mode_is_a_node (seed-lint RULE_HOMES :272, :3581; one home :3561; edges :3633; manifest :3313)
- Lines: 337 -> ~296; 160 -> ~146; 196, 137 -> 0
- Gate: `python3 tests/test_gate_registry.py`; `python3 tests/test_prepare_release.py`
- Effort: low. Depends on: none

### Wave 4: second passes on shared files

#### A1b: seed-lint rest and the table runner
- Spec contracts: SPEC-0001 HOST_TIERS_AGREE, SPEC-0003 HOOK_TEXT_RESTATES_NO_KERNEL_RULE, SPEC-0005 (after S1, S3, S5)
- Files: tests/seed-lint.py, tests/test-seed-lint.sh, tests/frontmatter.py (delete), tests/test-knowledge-paths.sh (delete), tests/ratchets.json
- Change: review A's §3a and §3b verdicts, except that `check_spec_test_mapping` stays in seed-lint, simplified. New `check_text_rules` (required and forbidden text table), with the bare knowledge-path pattern of test-knowledge-paths.sh as one forbidden row. New `check_published_figures` (body and eager figures, with the front-door scope rows from A1a). New `check_reference_tables`. check_delegation_split's key-home pairs become rows of the adopted-rule-homes map. `case_planted_table` calls each kept `check_*` in process on a small tree; rows keep their X labels. seed-lint.py:47 and FRONTMATTER_COPIES point at templates/knowledge-graph/frontmatter.py. Retire 3 ratchet limits. DEDUP: case_ce_leaf_sibling_over (X336 row); check_charter_vocabulary is on §4 as partial
- Lines: seed-lint.py ~4550 -> ~2150; test-seed-lint.sh ~2650 -> ~470; frontmatter.py 133 -> 0; test-knowledge-paths.sh 63 -> 0
- Gate: `python3 tests/seed-lint.py`; `bash tests/test-seed-lint.sh`; `python3 tools/ratchet-lint.py`
- Effort: high. Depends on: A1a, I4, S1, S3, S5

#### D1b: prompt-hook cases
- Spec contracts: SPEC-0003 (after S3)
- Files: tests/test-prompt-hooks.sh
- Change: D's hook-block and Prime-block verdicts. The TS tokenizer and `ledger_problems` go. X139 and X140 become two assertions in X141 (the section names `_cypress_surfaced`; no "loaded"). X109 keeps its "loaded" ban
- Lines: ~1880 -> ~850
- Gate: `bash tests/test-prompt-hooks.sh`
- Effort: medium. Depends on: D1a, S3

### Wave 5: run.sh and the gate registry, then the full gate

#### F1: steps
- Files: tests/run.sh, tools/gate-registry.py
- Change: remove the steps and GATES entries of the 10 deleted suites (test-entry-paths, test-tier-lanes, test-orchestration-entry, test-graph-artifacts, test-knowledge-paths, test-seed-budgets, test-collected-count, test_brainstorm_modes, test_tool_authorship, test_metadata_equivalence). Add steps and entries for test-verify-ledger.sh, test-ratchet-lint.sh, test-prompt-hooks.sh and test-code-anchor.sh. Cut run.sh history comments; `_seed_digest` stays. Update each spec's status_evidence list for moved or deleted files
- Lines: run.sh 318 -> ~120
- Gate: `bash tests/run.sh`, once, from the seed root. Record the §1 figures measured
- Effort: low. Phase: GREEN. Depends on: every increment above

#### F2: close-out
- Files: CHANGELOG.md (humanized), the session record, the §5 follow-ups filed for the owner
- Gate: prose-lint on CHANGELOG.md if run.sh does not cover it
- Effort: low. Phase: canonize (docs-librarian). Depends on: F1

## 4. OWNER-CONFIRM LIST

Only true deletions (nothing kept) and folds or simplifications that drop an assertion. Format: file :: case - what is dropped - survivor. Confirm by number or range. A line left unconfirmed leaves its case as it is (R9). The spec retirements a confirmed line needs are in S1-S5 and follow the line; they are not listed twice.

tests/seed-lint.py
1. check_delegation_split peers and Neighbours arms - a dropped peer or Neighbours entry among the delegation leaves - none (key homes survive as adopted-rule-homes rows)
2. check_prevents_are_distinct - overlapping `prevents:` lines between nodes - none
3. check_charter_vocabulary (+ _charter_vocabulary_holes) - an agent not reachable by its own charter's words - partial: every agent has golden rows and `--eval` gates them, but the rows are authored, not derived from the charter
4. check_plan_ledgers (+ _classification_names) - the seed's plan index disagreeing with its plan files - none
5. check_shell_floor_claim_matches_the_shebang - spec prose claiming POSIX over bash code - none
6. check_file_endings - a missing final newline on a machinery node - none
7. check_hook_text_restates_no_kernel_rule, kernel-token arm - a short paraphrase of a kernel rule in hook text - partial: byte budget on the hook text (growth only) (needs S3)
8. check_gate_single_home class-vocabulary, lifecycle-name and judge arms - a gate row with a bad class, a LIFECYCLE_NODES name that is not a file, a judgment row with no judge - partial: ratchet-lint's LIFECYCLE_NODES set pins the names
9. check_adopted_rule_homes wrapped and scoped stale-pointer handling - stale pointers split over two lines or placed in README, INSTALL, INSTALL_PROMPT or documentation/ - partial: single-line pointer row
10. check_host_tiers published-table mirror - host-capability-matrix tier table disagreeing with install.sh arrays - none (needs S1)
11. check_reference_second_views and the restated reference columns - summary rows, edge tables and "Roles at a glance" disagreeing with frontmatter - partial: one `check_reference_tables` over the primary tables
12. check(): node-contract two views, all arms except template-passes-linter and declared-collections-exist - schema kinds list, verdict vocabularies, staffing-decision homes vs the linter - none
13. check(): growth intake parity, audit-row arms - per-page audit rows vs collections - partial: intake arm kept
14. check_fd_first_screen_order (FIRST_SCREEN_ORDER) - README first-screen order, caps, first command line, later section order - none (needs S4)
15. check_fd_where_next_links_the_references (WHERE_NEXT_LINKS_THE_REFERENCES) - README not linking the reference manuals - partial: FRONT_DOOR_ANCHORS_RESOLVE still fails a broken link
16. check_fd_glossary_entry_complete (GLOSSARY_ENTRY_COMPLETE) - glossary entries missing fields, closed values or required terms - none
17. check_fd_no_unlinked_project_term_in_definition (NO_UNLINKED_PROJECT_TERM_IN_DEFINITION) - unlinked project terms inside definitions - none
18. check_fd_term_linked_on_first_use (TERM_LINKED_ON_FIRST_USE) - first use of a term not linked - none
19. check_fd_definition_has_one_home (DEFINITION_HAS_ONE_HOME) - a definition restated in two documents - none
20. check_fd_reference_opens_with_its_definition (REFERENCE_OPENS_WITH_ITS_DEFINITION) - reference manual opener - none
21. check_fd_enforcement_row_complete (ENFORCEMENT_ROW_COMPLETE) - enforcement table rows, required rows, residuals, hook firing - none
22. check_fd_mechanism_claims_traced overclaim and surfaces arms (MECHANISM_CLAIMS_TRACED narrowed) - a claim stronger than its mechanism; the surfaces list - partial: named mechanism paths must exist
23. check_fd_limits_section_present (LIMITS_SECTION_PRESENT) - the limits section and its requested and unmeasured floors - none
24. check_fd_catalogs_out_of_readme (CATALOGS_OUT_OF_README) - catalogs and ADR ranges in README - none
25. check_fd_cost_figures_scoped (COST_FIGURES_SCOPED) - cost figures without scope, provenance or measured/derived label - none
26. check_fd_front_door_headings_well_formed (FRONT_DOOR_HEADINGS_WELL_FORMED) - heading hygiene - none (prose-lint covers title case only)
27. check_fd_link_text_stands_alone (LINK_TEXT_STANDS_ALONE) - "click here" style link text - none
28. check_fd_tables_have_header_rows (TABLES_HAVE_HEADER_ROWS) - tables without a header row - none
29. check_fd_pending_ledger_holds_only_failing_contracts (PENDING_LEDGER_HOLDS_ONLY_FAILING_CONTRACTS) with FRONT_DOOR_PENDING, fd_guard and the raised-check handling - pending-ledger mechanics and fd input robustness (the ledger is empty) - none

tests/test-seed-lint.sh (cases that go with lines 1-29 are covered by those lines and not repeated)
30. case_spec_row_toplevel_def - a neighbouring top-level def falsely binding a §10 row - none
31. case_x202, case_x203 - kernel-step paraphrase inside the Prime overlay section, and its renamed-heading variant - partial: X141 overlay byte ceiling
32. case_hook_reach_rewordings - reworded variants of the banned hook-reach claim - partial: one forbidden row and one allowed row
33. case_ce_leaf_stale_member, case_ce_leaf_unknown_member - a stale or unknown OVERSIZED_LEAVES member not flagged - partial: ratchet-lint refuses growth of the set
34. case_ce_pending_phrase_planted - planting 4 of the 5 §6 pending phrases (all 5 stay in the table data) - partial: one planted phrase
35. case_ce_kernel_session_record_pointer - the "moved to §5" and "sessions directory emptied" plants - partial: the removed-sentence plant
36. caseHOST_TIERS_AGREE parser mutants (duplicated tier row, `cursor` arm shapes, quoted label, split arm guard) - install.sh dispatch-parser edge shapes - partial: two rows (arrays vs `all`; a tool in no tier)

tests/test_metadata_equivalence.py
37. test_multiline_description_is_refused_the_same_everywhere - the wrapper's "one line" error text - behavior survivor: test_frontmatter_contract.py test_a_multi_line_value_is_refused
38. test_graph_lints_dead_tokenizer_has_no_live_caller - expertise descent reading Node.triggers (a source-slice assert) - partial: the router table row holds the strengths

tests/test-seed-budgets.sh
39. (a) claude-code install into a directory with `&` - claude-code install into a hostile path - none (the codex case keeps the 7-character path)
40. (b) run_budget_probe lifecycle-ceiling arm and one-byte EAGER_EXEMPTIONS arm - those two arms firing - partial: A1b rows from case_17 and case_22

tests/test-legal-lint.sh
41. 8 edition-debt-shrinks - a stale EDITION_DEBT row not flagged - partial: ratchet-lint blocks the set growing
42. jurisdiction carried-confirm install - the "national layer: '<cc>' is carried" message - none

tests/test_graph_lint.py
43. LibraryIndexRowBoundaryTests.test_the_pending_vocabulary_is_stated_in_the_schema - _schema.md omitting a PENDING_HEADINGS word - none
44. DescentTests.test_plan_warns_on_wide_descent - the wide-descent warn line of `--plan` - none
45. InferenceTests.test_plan_long_token_flood_does_not_use_the_cap - cap ordering vs the length skip - none
46. InferenceTests.test_plan_cap_counts_only_path_like_tokens - plain words counting against the 64-token cap - none
47. InferenceTests.test_plan_token_of_exactly_256_is_considered - off-by-one at the 256 length limit - none
48. PromotedClosureTests.test_plan_scored_and_hit_prints_no_suffix, test_plan_promoted_and_inferred_prints_promotion_only - suffix text and precedence on `--plan` lines - none
49. InferenceTests.test_plan_hostile_task_line_never_raises cap and length subtests and the second fault class - those inputs under the guard - partial: one fault class, notice line and exit 0

tests/test_agent_lint.py
50. LintEffortTests.test_lint_real_roster_effort_matches_the_table (+ _spec_effort_table, _roster_efforts) - drift between roster `effort:` and the SPEC-0005 §6 table - none needed: S5 removes the second home
51. AdversarialBudgetTests.test_the_shipped_corpus_sits_under_the_budget - the "N within it (budget M)" report line - behavior survivor: run.sh:254 `--eval`
52. MeasuredRosterTests.test_scoping_the_floor_did_not_move_its_recorded_value - a silent raise of PARAPHRASE_FLOOR - partial: ratchet-lint refuses a lowering (needs S2)

tests/test_router_reach.py
53. StemCollisions.test_agent_roster_collisions_are_reviewed, test_load_when_collisions_are_reviewed, `_bless`, fixtures/router/stem-collisions.json - review of new false stem merges in real vocabulary - none (needs S2)

tests/test-tier-lanes.sh (whole file)
54. one-home greps (test-tier-lanes.sh:23-28) - `tiers.contained-lane` and `canonize.why-record` owned zero times or by another file - partial: two owners fail seed-lint (§1.1 item 1)
55. five conditions, never-waives, why-record, specify exception, surfaces and superseded-edge greps - those phrases in 12 files - none

tests/test-orchestration-entry.sh (whole file)
56. every grep and the persona-simulation grep - phrases in INSTALL_PROMPT, grow, graft, agents, templates - none

tests/test-entry-paths.sh
57. retired from-scratch-bootstrap references - stale mentions of a retired skill - partial: graph-lint catches dangling node ids
58. absorbed discipline phrases, initialize.md fork table rows, adapter-sites co-occurrence sweep, install.sh post-install line, grow hands-off - those phrases - none; routing behavior kept in case_claude_code

tests/test-full-install.sh
59. caseROSTER_PROJECTION_PARITY_KEEPS_A_LIVE_HOME - mutation proof of the projection_parity helper - none; the helper still runs on the real projection
60. case_github_copilot COPILOT_POINTER_OVERHEAD probe - seed-lint's frozen-host byte estimate measured on an install - none

tests/test-install-placement.sh
61. case_m10 (6) - 4 of 6 symlinked-directory depths - partial: 2 paths (one adapter directory, one docs/graph subtree)

tests/test-install-adoption.sh
62. case_migration_date live-date arm - the date on a live (non-orphan) row - partial: orphan row carries the backup date
63. case_d5_recreated_list timestamp header regex - the header's timestamp format - partial: header prefix

tests/test-unified-graph-install.sh
64. case_required initialize.md greps, _schema/graph-lint greps, legacy-directory absences - those texts and absences - partial: required list, target README survival, in-plant graph-lint

tests/test-nested-checkout.sh
65. caseROSTER_TOOL_UNDER_TEST_IS_THE_SEED_COPY - which agent-lint copy the nested suite loads - none
66. caseROSTER_EXPLICIT_DIR_IS_HONOURED_VERBATIM refusal guards - the override's refusal guards - partial: override honoured, kept inside caseROSTER_DEFAULT_RESOLVES_INSIDE_THE_SEED
67. caseROSTER_RESOLVED_SCOPE_IS_STATED_IN_THE_OUTPUT - roster path in test-failure messages - none
68. caseROSTER_PROJECTION_PARITY_SKIPS_EVERYWHERE - skip reason text of a deleted SkipTest - none

tests/test-bound-hook.sh (after D1a: tests/test-prompt-hooks.sh, tests/test-code-anchor.sh)
69. X126 STATUS_HOOK_RESET_OWNS_NO_PATH_RULE - status-hook.py carrying its own session-id or path rule - partial: X127 catches the behavior (needs S3)
70. X139 PRIME_OVERLAY_KEEPS_SURFACED_SET - 3 of 4 phrases and the no-`rlm`/no-`brief` ban - partial: `_cypress_surfaced` named, inside X141
71. X135 + X150 + X136 into one substring case - branch placement, no `.slice(<n>)`, no line split, no stdout reassignment, argv element analysis - partial: three substrings
72. X138 to the fs-write ban - module-scope allowlist, `pi.on` event check, reminder-prefix ban, `globalThis` ban - partial: no fs write call
73. X163, X164, X165 - argv-array parse, `findRegister` early return, source greps in 3 files, the §6 table value - partial: substrings, SessionStart wiring, hook constant equals TS timeout
74. X129 into X133 - hard-link inode (replace, not rewrite) and no stray temp on success - partial: failed replace leaves the ledger intact
75. X113 - refresh at a rewritten REFRESH_EVERY of 3 - partial: N and N-1 with the real constant
76. X134 + X149 - GC removal order and the 300-file GC_SCAN_MAX bound - partial: old ledgers go, foreign files stay, scan fault row
77. X148 - the three-prompt no-flip-flop run - partial: one prompt, not written, full mode
78. X152 - exact key set, 0644 mode and ISO-8601 format of `.cypress/anchor.json` - partial: every repository named
79. X160 - hard-link replace check on a second `--record` - partial: symlink and directory refused
80. X103, X104, X118, X119, X120, X123, X124, X130, X133, X162 variant cuts - the 2,000,000-character prompt; 2 of 3 stub modes; 1 envelope; 4 of 7 ids; 3 of 6 corrupt shapes; 6 of 8 sources; 6 of 9 ids; `.cypress` and `.gitignore` symlink shapes; the read-only directory branch; 6 of 8 mode and register runs - partial: the kept variant of each

tests/test-graft-tools.sh
81. GT15 in-process asserts on SCAFFOLD_FILES and seed_source_for - internal constant pins - partial: CLI identical-backup run

tests/test-tool-corpus.sh
82. §5 parallel-overlap timing, timed-out-once-then-pass re-run, grandchild process-group kill - those three runner behaviors - partial: the seven kept §5 checks

tests/test_tool_authorship.py (whole file)
83. test_the_tool_smith_is_a_routable_agent - `prevents` key on tool-smith - partial: agent-lint rule 1, seed-lint manifest agents
84. test_the_close_out_names_the_producer - canonize and tool-smith edge pair, the producer phrase - none
85. test_the_golden_corpus_routes_to_it - at least 3 golden rows for tool-smith - partial: GoldenCorpusTests roster coverage (at least 1 row)
86. test_the_charter_refuses_seed_machinery, test_canonize_still_forbids_a_second_cataloging_spawn, test_authoring_is_not_a_close_out_step - those clauses' wording - none
87. test_it_is_owned_exactly_once_and_not_by_the_author, test_nothing_points_at_protocol_toolcraft - zero owners, owner in agents/, the retired id in body prose - partial: one-home and edge checks in seed-lint

tests/test_brainstorm_modes.py (whole file)
88. test_the_protocol_reaches_both, test_mode_selection_has_exactly_one_home - protocol.brainstorm's edges to both modes; zero owners - partial: seed-lint one-home
89. test_the_socratic_mode_keeps_the_user, test_the_internal_mode_can_finish_without_a_user, test_the_question_cap_is_a_rule_in_one_mode_and_a_reference_in_the_other, test_it_names_the_strawman_failure - wording in the two brainstorm skills - none
90. test_socratic_declares_the_humanizer - the skill.humanizer edge on brainstorm-socratic - none

Machinery
91. tests/check-coverage-binder.py (whole file) - a new seed-lint check can land with no planted row - none (intended: a RED seen once is the proof)
92. tests/check-coverage-binder.py INLINE_ASSERTION_DEBT - the ratchet on inline assertions in check() - none
93. tests/collected.json + tests/test-collected-count.sh - a Python suite silently collecting fewer tests - partial: unittest exits 5 when it collects none
94. tools/ratchet-lint.py RATCHETS table - the registry moves into tests/ratchets.json (one list); "recorded but not registered" check - none needed: one list cannot disagree with itself
95. tools/ratchet-lint.py direction-flip check - a direction flipped without the lock moving - none needed: the direction lives in the lock entry, so a flip is a lock edit
96. tests/ratchets.json FIRST_HEADING_MAX_LINE, FIRST_SCREEN_MAX_LINES, FIRST_COMMAND_LINE, README_CATALOG_CEILING, LIMITS_MIN_REQUESTED, LIMITS_MIN_UNMEASURED, DEFINITION_OVERLAP_CEILING, FRONT_DOOR_PENDING - go with lines 14-29 - none
97. tests/ratchets.json CHARTER_VOCAB_DEBT, PREVENTS_OVERLAP_CEILING, PREVENTS_RESTATEMENT_CEILING - go with lines 2-3 - none


### Owner confirmation (2026-09-29)

Owner: "accepted" (the session's recommendation). Applied under R9:
- CONFIRMED: §4 lines 1-38, 40-53, 55-92, 94-97.
- NOT CONFIRMED, line 39: the claude-code install into a directory with `&` stays (installer quoting has real blast radius).
- MODIFIED, line 54: test-tier-lanes.sh is reduced to ONE check that `tiers.contained-lane` and `canonize.why-record` each have exactly one owner (zero owners must fail). The rest of the file (line 55) goes. May live in seed-lint instead of its own file if that is smaller.
- MODIFIED, line 93: the collected.json floors, the floor file and its per-suite edits go. Minimal replacement: the run prints each Python suite's collected test count, so a drop is visible in the output; zero collection is caught by unittest exit 5. No floor file, no new gate.

## 5. Doctrine follow-ups (seed nodes; list only, nothing edited)

a. A print-only or report-only surface (`--plan`, `--route`, `--waves`, `--slice`) gets one case per behavior, not one per spec boundary. Home: `test-first.proportionate-checks`.
b. A gate born from an incident carries a retire path: the condition under which it goes, checked at each consolidation. Home: `protocol.verify-new-gates`.
c. No incident narration in test files. The history lives in the plan and CHANGELOG; a test keeps at most one "why" line. Home: skill.test-first (test shape).
d. A test sits in its subject's file. A property checked across many tools (lint audibility) is its own subject. Home: skill.test-first (test level selection).
e. A spec contract states behavior, not the test fixture. Fixture counts in Given clauses (40 ledgers, 300 temp files, a hard link) make spec size set test size. Home: `protocol.specify` / skill.spec-author.
f. A seed-only check never moves into a shipped engine, because that adds a check to every plant's runs. Home: `test-first.proportionate-checks` ("the seed adds none") or subsystem.graph-linters.
g. A fact restated in a second document is fixed by linking, not by a lint that keeps the copies in sync (reference tables, host matrix, the SPEC-0005 effort table). Home: skill.knowledge-graph or method.design-posture.
h. Test helpers get no tests of their own: no mutation proofs of a helper, no self-tests of roster resolution. Home: `test-first.proportionate-checks`.
i. A frozen host (ADR-0009) gets smoke coverage (installs, exits 0, one DEPRECATED line), not full regression. Home: subsystem.installer or the ADR's consequences.
j. A test that runs a tool over the real tree duplicates the gate step that already does it. Unit suites test fixtures; the real tree is the gate's job. Home: `protocol.verify`.
k. Consolidation keeps the survivor's name and label, so spec rows stay bound through a fold. Home: skill.test-first ("shrink on purpose").
l. `tools/gate-registry.py --lint` does not check that a step's file exists (F1 finding). The nine deleted suites were caught only because their GATES entries no longer matched a `run.sh` step; if both had stayed, `--lint` would report OK and only the step's own exit code would fail. Home: subsystem.test-gate (recorded there as a sharp edge); a fix is a tool change for the owner (R5 held it out of this plan).
m. `check_canonical_router_blocks` has no planted row in `tests/test-seed-lint.sh`, now or at HEAD (review m4); the old case_32 "exercises" comment was wrong. Recorded, not closed: R5 forbade a new row and §4 line 91 accepts a check with no row. Home: `test-first.proportionate-checks` (when a check without a row is acceptable) or the seed-lint table.
n. A print-only or report-only surface gets one case per behavior (review B, P1: about 60 router and `--waves` cases were one per spec boundary). This is (a) seen at scale in one group; file it once, under (a)'s home, not as a second rule.

## 12. Open Questions (owner)
1. §4 confirmation by number. Lines 14-29 retire 15 of SPEC-0004's 22 contracts; that is the largest single decision.
2. Machinery (§4 lines 91-97): if any stays, the cut batches carry the forced edits in the §3 wave 2 table.
3. B2's [verify]: does CONFIDENT_WRONG_BUDGET count golden row 178's class? If not, the misroute case stays.

## 13. Done Criteria
- Every confirmed §4 line applied; every unconfirmed line's case unchanged.
- `bash tests/run.sh` green once at the end (F1), with the §1 "after" column replaced by measured figures.
- No spec §10 row cites a missing test; SPEC_UNCOVERED_BUDGET not loosened.

Checked 2026-09-29 at close-out (F2, spawn `session.10.docs-librarian.1`), from the handbacks and the review:
- [x] Confirmed §4 lines applied; line 39 kept (`case_claude_code_ampersand_path`), lines 54 and 93 applied as modified. Review `session.8.reviewer.1` found one unconfirmed weakening (M1, the step-2 word-for-word compare), fixed by `session.9.implementer.1`.
- [x] `bash tests/run.sh` green: 45/45 steps, 26.0 s (`session.9.implementer.1`, after the review fixes). Measured in place of the §1 "after" estimates: tests/ excluding fixtures 32760 -> 16015 lines; fixtures 2282 -> 1098; subject about 15100 lines (install.sh 2561, tools/*.py 8427, templates/knowledge-graph/*.py 2792, integration hook scripts 1320); check:subject about 2.17 -> about 1.06 on that subject. The §1 table keeps its estimates as written.
- [x] No §10 row cites a missing test: `python3 tests/seed-lint.py` PASS (it runs `check_spec_test_mapping`); spec-lint WARN 2/130 at `--uncovered-budget 2`, the same budget as HEAD.
- [ ] Found at close-out, outside the criteria above: The plant's own spec lost its test bindings. `python3 docs/graph/spec-lint.py` (plant) PASSes 39/39 live contracts of `docs/graph/specs/SPEC-0001-gate-assertion-floor.md` against seed HEAD `d6ec78c`'s `tests/`, and FAILs 27/39 against the consolidated tree: 20 `AUDIT_*` slugs left `tests/test-growth-audit.sh` with its history comments (D2; the assertions stayed), `AGNOSTICISM_GATE_SCANS_DOCS_PLANS_TOOLS_INSTALLER` and `AGNOSTICISM_GATE_SCANS_PY_AND_SH` left `tests/test-seed-lint.sh` (A1), and five went with confirmed deletions or folds (`SHELL_FLOOR_CLAIM_MATCHES_THE_SHEBANG`, §4 line 5; `ROSTER_TOOL_UNDER_TEST_IS_THE_SEED_COPY`, `ROSTER_EXPLICIT_DIR_IS_HONOURED_VERBATIM`, `ROSTER_RESOLVED_SCOPE_IS_STATED_IN_THE_OUTPUT`, §4 lines 65-67; `ROSTER_PROJECTION_PARITY_KEEPS_A_LIVE_HOME`, §4 line 59). R1 and R2 covered the seed's specs only. Fix: restore the slug comments where the assertion survived (implementer), and retire the five in the plant spec (plant spec owner).

## 15. Changelog
- 2026-09-29: plan written by the architect (spawn `session.5.architect.1`) from reviews A-D and the owner steer.
- 2026-09-29: owner confirmation recorded under §4 ("accepted": lines 1-38, 40-53, 55-92, 94-97; line 39 not confirmed; lines 54 and 93 modified).
- 2026-09-29: wave 1 and 2. `session.6.implementer.1` applied I1-I4 (the legal-lint temp leak, GR-h on a tagged checkout, `tests/helpers/plant.sh` and `lintcase.sh`, the binder and floors deleted, the ratchet registry moved into `tests/ratchets.json`, `tests/test-ratchet-lint.sh`). `session.6.architect.1` applied S1-S5 (SPEC-0004 2347 -> 760 lines, 22 -> 7 contracts; SPEC-0005 0.13 -> 0.14).
- 2026-09-29: wave 3. Fifteen batches by `session.7.implementer.*` (A1, B1-B5, C1, C2a, C2b, C3, C4, D1, D2, D3, D4); A1 carried A1a with A1b and D1 carried D1a with D1b, so wave 4 needed no separate spawns. Handbacks: `.seed-worktrees/records-unreleased-proportionate-checks/`.
- 2026-09-29: F1 by `session.8.implementer.F1`. 45 steps; nine suites removed, test-tier-lanes.sh kept (§4 line 54 overrides the F1 list), four added. First full run 44/45: the grill-lint step went red on the 7.32.0 harvest plan's increment 53, which cited two SPEC-0003 contracts S3 retired. The session fixed it by a dated amendment to `docs/plans/grill-7.32.0-harvest/increment-53-final-tip.md`.
- 2026-09-29: review by `session.8.reviewer.1`: APPROVE WITH FIXES (M1, m1-m6). `session.9.implementer.1` applied M1 and m1-m3; m5 and m6 were F1's and held; m4 is follow-up (m) in §5. Gate after the fixes: 45/45, 26.0 s.
- 2026-09-29: F2 close-out by `session.10.docs-librarian.1`: CHANGELOG "Unreleased" entry extended; stale prose fixed in DOCUMENTATION.md, documentation/ (host-capability-matrix, protocols-reference), CLAUDE.md, the parallel-suite-runner tool page, and SPEC-0001, SPEC-0003 and SPEC-0005 (dated §12 lines, spec text only); §5 (l)-(n) added; §13 checked; the phase line in §0 updated.
- 2026-09-29: plant spec links repaired after the F2 gate found them broken: labels restored on surviving tests (spawn `session.11.implementer.1`, 22 slugs); 5 plant SPEC-0001-gate-assertion-floor contracts retired for owner-confirmed cuts (`session.11.architect.1`); 13 stale plant graph files refreshed (`session.11.docs-librarian.1`). Plant spec-lint PASS 34/34.
- 2026-09-29: released as 7.33.0 (owner: "commit push tag release").
