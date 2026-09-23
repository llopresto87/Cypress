# grill — host support tiers (7.27.0)

**Status:** planned, nothing implemented. ADR-0009 is `proposed`.
**Baseline commit:** `5a1ca2c` (7.26.0)
**Tier:** T3. It changes what `install.sh all` writes into a target, adds
installer output, and adds contracts to SPEC-0001.
**Decision record:** [ADR-0009](../decisions/adr-0009-host-support-tiers.md)

This file is the plan-of-record for one increment. It lists every file that
changes with its line, the new failing tests by contract name, and every
existing test that has to move so it keeps covering what it covers today. The
tester writes the RED tests from §3, the implementer makes them green from §2,
and §4 is done in the same increment so that no suite silently narrows.

Line numbers were read at `5a1ca2c` and will drift as the edits land. Where a
line is quoted as a range, the range is the edit's anchor.

## §0 Baseline record

| Fact | Value at `5a1ca2c` | Where |
|---|---|---|
| `all` expansion | `claude-code opencode codex github-copilot prime-agent` | `install.sh:1717-1724` |
| Positional parser | accepts several tools in one run, so `all codex` is already legal | `install.sh:1622` |
| `log` / `warn` / `die` | stdout / stderr / stderr | `install.sh:91-93` |
| `--check` scope | only `github-copilot` in the expanded list is checked | `install.sh:2019-2022` |
| Adapter dispatch | one `case` per tool | `install.sh:2095-2104` |
| Harnesses held to `EAGER_BUDGET` | all five, no exemptions | `tests/seed-lint.py:182`, `:211`, `:2299-2312` |
| Suites that call `install.sh all` | 4 suites, 17 call sites | §4 |
| Kernel size budget | 8 000 B, and this plan leaves `core/AGENTS.md` alone | `tests/seed-lint.py` |

Gate result at baseline: not recorded by this plan. The implementing session
runs `bash tests/run.sh` before its first edit and records the result here.

## §1 Owner decision and the ledger it opens

The owner decided on 2026-09-23, in chat, and the decision is authoritative.
It is transcribed here and not re-opened.

1. Full support with feature parity as the target: `claude-code` and
   `prime-agent`.
2. `opencode` is supported and keeps its current install surfaces unchanged.
   The seed does not strive for parity where the host cannot natively carry a
   feature; such features are recorded as gaps, with no workarounds.
3. `codex` and `github-copilot` are legacy and deprecated: frozen, still
   installable. `install.sh codex|github-copilot` still works and prints a
   DEPRECATED notice. `install.sh all` no longer includes them. Their adapter
   files stay byte-unchanged except for deprecation notices in their READMEs.
   Their existing tests keep running as regression. They get no new features.
   Removing them is a future, separate owner decision.

The ADR names the tiers `first-class`, `supported` and `frozen`.

One research finding is recorded and deliberately not acted on: upstream Codex
CLI documents stable hooks, which contradicts the matrix's "no hook surface"
evidence line. The host is frozen, so no Codex hook is wired. See ADR-0009,
"Host matrix".

| # | Entry | Disposition |
|---|---|---|
| H-1 | `all` installs two hosts the seed no longer develops | fixed by S-1 |
| H-2 | nothing tells a user that codex and github-copilot are deprecated | fixed by S-1 |
| H-3 | a plant carrying a frozen host, re-run with `all`, keeps stale frozen projections with no word said | fixed by S-1 |
| H-4 | `all --check` loses its only subject and would exit 0 having checked nothing | fixed by S-1 |
| H-5 | the Claude Code hooks reach Copilot and nothing pins that they fail open there | fixed by S-2 |
| H-6 | the tier table would have two homes, the installer and the matrix | fixed by S-3 |
| H-7 | docs describe `all` as five hosts | fixed by S-4 |
| H-8 | the matrix's Codex hooks evidence contradicts upstream | recorded, not acted on (ADR-0009) |

## §2 Change inventory

### `install.sh`

| Line | Change |
|---|---|
| `:12-21` | Usage header. Mark `codex` (`:17`) and `github-copilot` (`:18`) as `DEPRECATED (frozen, ADR-0009)`. `:21` becomes "Run claude-code, opencode and prime-agent. Name codex or github-copilot as well to install a frozen host." `usage()` at `:1615-1618` extracts this block with `sed`, so help and header cannot disagree and need no second edit. |
| `:91-93` | Beside `log`/`warn`, one helper that prints the deprecation line to stderr: `[seed] DEPRECATED: <tool> is a frozen host (docs/decisions/adr-0009-host-support-tiers.md). It still installs and gets no new features.` Stderr keeps `codex --print-config` stdout clean. |
| new, before `:1717` | The one home of the tier assignment: `FIRST_CLASS_TOOLS=(claude-code prime-agent)`, `SUPPORTED_TOOLS=(opencode)`, `FROZEN_TOOLS=(codex github-copilot)`, with a comment pointing at ADR-0009. |
| `:1721` | `all) expanded+=(claude-code opencode prime-agent) ;;`. The order is today's with the frozen pair removed. Write it as an explicit list in the same comment block as the arrays; deriving it by concatenation would reorder `prime-agent` before `opencode` and change install order for no reason. |
| after `:1724` | For each tool in `expanded` that is in `FROZEN_TOOLS`, call the helper once. Placing it here, ahead of the `--check` branch at `:2019`, makes the notice fire for both installs and `--check`, and leaves the bodies of `install_codex` (`:1286`) and `install_github_copilot` (`:1348`) byte-unchanged. |
| after `:1724` | When `all` was given and the stamp's `tools` (read through `stamp_field`, never a regex) names a frozen host absent from `expanded`, `warn` once per host: its projections were not refreshed, and `install.sh all <host>` refreshes them. |
| `:2019-2022` | When `--check` runs and `expanded` contains no `github-copilot`, `log` that no generated views are in scope and exit 0. |

`install.sh:1622`, the dispatch at `:2095-2104`, and `agent_projection_for`
are unchanged.

### Specs and decisions

| File:line | Change |
|---|---|
| `docs/specs/SPEC-0001-install-placement.md:3` | `status_date` moves to the landing date. |
| `SPEC-0001:43-49` | §2 in-scope gains "which hosts `all` installs, and the deprecation notice". |
| `SPEC-0001:56-63` | §3 gains two sentences: `all` installs the maintained hosts, and a frozen host installs when named and says it is deprecated. |
| `SPEC-0001`, §4 after `:221` | The six contracts in §3 below, in the spec's Given/When/Then shape. |
| `SPEC-0001`, §7 after `:295` | `Failure: FROZEN_PROJECTION_LEFT_STALE`. Trigger: the stamp records a frozen host and `all` runs. Response: the warning from §2. Side effects: none; the frozen tree is left exactly as it was. Recovery: re-run with the host named. |
| `SPEC-0001:344-364` | One §10 row per new contract, suite and case named, status `red` until green. |
| `SPEC-0001:397` onward | §12 entry dated at landing, naming ADR-0009. |
| `docs/decisions/adr-0009-host-support-tiers.md` | Flips to `accepted` with the landing version once §3 is green. |
| `docs/decisions/index.md:19` | Its status cell follows the ADR. |

### Documentation

| File:line | Change |
|---|---|
| `documentation/host-capability-matrix.md`, before `:54` | New section "Support tiers (ADR-0009)": the three-row tier table, and the opencode statement, "a feature reaches opencode only where the host carries it natively; where it cannot, the gap is recorded in this matrix and no workaround is built". The matrix cells are untouched, since a tier is a maintenance commitment and the six classes describe what the harness holds. |
| `documentation/host-capability-matrix.md:11`, `:25` | "all five" stays true of method parity and enforcement coverage; add "(two of them frozen, see Support tiers)" at `:11` only. |
| `documentation/host-capability-matrix.md:276-277` | Codex hooks evidence keeps `unsupported` and gains one sentence: upstream Codex documents `SessionStart`, `UserPromptSubmit` and `PreCompact` hooks, the seed wires none, and ADR-0009 is why. |
| `README.md:6` | Host list reordered by tier, with Codex and Copilot marked deprecated. |
| `README.md:51` | No change. The figures are derived by `check_published_eager_figures` and all five harnesses stay measured. |
| `README.md:156-172` | `:165` "all five adapters" gets "(two of them frozen)"; `:170-172` "one tool or all five" becomes "one tool, or `all` for the three maintained ones". |
| `INSTALL.md:57-63` | `codex` and `github-copilot` bullets marked deprecated with the ADR link; `:63` becomes "`all` runs claude-code, opencode and prime-agent". |
| `INSTALL.md:71-72` | Example comment becomes "The three maintained tools, explicit target". |
| `INSTALL.md:275-285` | "Recommended order if installing all five" keeps the five-line listing, marks the two frozen lines, and `:285` says `all` covers the maintained three. |
| `DOCUMENTATION.md:727-728` | Tool list marks the frozen pair and says what `all` covers. |
| `documentation/corpora-and-integrations-reference.md:427`, `:444` | Same correction as README `:171`. |
| `integrations/claude-code/README.md:113` | "all five supported tools" becomes "every host the seed installs". |
| `integrations/codex/README.md:1` | A deprecation notice under the title: frozen, still installable, no new features, link to ADR-0009. Nothing else in the file changes. |
| `integrations/github-copilot/README.md:1` | The same notice, plus one line: Copilot reads `.claude/settings.json`, so the Claude Code hooks keep failing open for it. |
| `integrations/opencode/README.md:1` | One paragraph under the title stating the `supported` tier and the native-only rule. |
| `core/AGENTS.md:20-21` | No edit. It names the five hosts as the files each reads, which stays true of every installable host, and the kernel budget argues against touching it. |
| `INSTALL_PROMPT.md:44` | No edit. "`<tool>` (or `all`)" stays accurate. |
| `protocols/harvest.md` | No edit in this increment; see §6 question 2. |

The seed-lint arms that read the integration READMEs, `REGISTRATION_REFERRERS`
(`tests/seed-lint.py:242-272`) and the numeric-claims scan (`:2815-2857`),
keep passing as long as the new notices add prose and remove no pointer.

### Release

| File:line | Change |
|---|---|
| `manifest.json:5` | `"version": "7.27.0"`. |
| `manifest.json:18` | The tagline stays true; mark the two frozen hosts only if the release writer wants to. |
| `CHANGELOG.md:3` | New `## 7.27.0` entry above the 7.26.0 one: what `all` installs now, the notice, how to keep a frozen host, the Codex hooks finding and why it was left alone, ADR-0009. |

### Gate machinery

| File:line | Change |
|---|---|
| `tests/seed-lint.py`, new function | `check_host_tiers`: parses the three arrays and the `all` line out of `install.sh`, and the tier table out of the matrix, and fails when they disagree or when a tool appears in two tiers. |
| `tests/seed-lint.py:2299-2312` | Comment only: all five stay in `surfaces` on purpose, and a frozen host alone over budget is a removal trigger under ADR-0009, never an exemption. |
| `tests/check-coverage-binder.py:36-50` | `check_host_tiers` joins `COVERED` once the planted case exists. |

## §3 New failing tests (RED first)

No new test file and no new gate. Every contract fits a suite already wired
into `tests/run.sh`.

| Contract | Given / When / Then | Suite |
|---|---|---|
| `ALL_EXCLUDES_LEGACY_HOSTS` | Given an empty target, when `install.sh all` runs, then `.claude/`, `.opencode/` and `.prime/agent/` exist, `.codex/` and `.github/` do not, and the stamp's `tools` is exactly `claude-code opencode prime-agent`. | `tests/test-full-install.sh`, new case beside `case_seed_stamp` |
| `LEGACY_INSTALL_PRINTS_DEPRECATED` | Given an empty target, when `install.sh codex` or `install.sh github-copilot` runs, then stderr carries exactly one `DEPRECATED` line naming that tool and ADR-0009, and `install.sh opencode` prints none. | `tests/test-full-install.sh`, extending `case_codex` (`:229`) and `case_github_copilot` (`:240`) |
| `LEGACY_INSTALL_STILL_SUCCEEDS` | Given an empty target, when a frozen host is named, then the exit is 0, its destinations are placed as at 7.26.0, and `codex --print-config` stdout carries no `DEPRECATED` text. | `tests/test-full-install.sh`, same two cases |
| `ALL_NAMES_SKIPPED_FROZEN_HOSTS` | Given a plant whose stamp records `codex`, when `install.sh all` runs, then stderr names `codex` as not refreshed and names the command that refreshes it, `.codex/` is byte-identical before and after, and the stamp still lists `codex`. | `tests/test-plant-state.sh`, next to the S2/S5 `ADAPTERS_ACCUMULATE` cases |
| `CHECK_WITHOUT_COPILOT_SAYS_SO` | Given any target, when `install.sh all --check` runs, then it exits 0 and prints that no generated views are in scope. Silence fails the case. | `tests/test-install-adoption.sh`, beside `case_check_backups` (`:360`) |
| `CLAUDE_HOOKS_FAIL_OPEN_ON_COPILOT_ENVELOPE` | Given the shipped `route-hook.py` and `status-hook.py`, when each is fed a Copilot-shaped stdin (no `session_id`, `source: "new"`, an unknown extra field) and also an empty stdin, then each exits 0 and writes nothing to stderr that a host would read as a block. | `tests/test-bound-hook.sh`, which already builds hook stdin envelopes (`:31`, `:110`); its scope widens from the guard to every Claude Code hook |
| `HOST_TIERS_AGREE` | Given a copy of the seed whose matrix tier table moves `opencode` to `frozen`, when `seed-lint` runs, then it fails naming both files. The unmutated tree passes. | `tests/test-seed-lint.sh`, planted-violation case, `# exercises: check_host_tiers` |

The first five and `HOST_TIERS_AGREE` also get SPEC-0001 §4 contracts and §10
rows. `CLAUDE_HOOKS_FAIL_OPEN_ON_COPILOT_ENVELOPE` belongs to no spec, since
SPEC-0001 covers placement only; its authority is ADR-0009's "Claude Code
hooks and Copilot" consequence.

## §4 Existing tests that must change

The rule: a call that exists to cover the complete destination set, or that
asserts a frozen host's files, names all five hosts explicitly, so the frozen
adapters stay under regression. Each suite gets one variable,
`EVERY_HOST="claude-code opencode codex github-copilot prime-agent"`, and the
call becomes `install.sh $EVERY_HOST ...`. A call whose assertion holds for any
adapter set keeps `all`, so that `all` itself stays exercised.

| File:line | Today | Why it breaks or narrows | Change |
|---|---|---|---|
| `tests/test-install-placement.sh:703` | `BASE` built with `all` | `:766` asserts `.github/copilot-instructions.md` and `:770` asserts `.codex/codex-config-snippet.toml` in `BASE`; both fail. `COND_FILES` (`:713-725`) is the difference against `BASE`, so every `.github/` file would turn "conditional" | `$EVERY_HOST` |
| `tests/test-install-placement.sh:98`, `:103`, `:143` | `case_recover` with `all` | M7/M3 claim the complete destination set; frozen destinations would drop out of the sentinel sweep | `$EVERY_HOST` at all three |
| `tests/test-install-placement.sh:211` | `case_symchurn` with `all` | the defect it pins was five adapters flipping the kernel pair (comment `:205-206`); three adapters narrow it | `$EVERY_HOST` |
| `tests/test-install-placement.sh:257` | `case_m2` loop with `all` | M2 runs over `FILES` from `BASE`; with `BASE` on five hosts and this loop on three, frozen destinations would keep the attacker's link and read as never written | `$EVERY_HOST` |
| `tests/test-install-placement.sh:334` | `case_m9` with `all` | M9 link uniformity over every placed file; frozen destinations drop out | `$EVERY_HOST` |
| `tests/test-install-placement.sh:428`, `:436` | `case_m8` with `all` | M8 audit totality; Copilot's generated files are the main source of classification cases | `$EVERY_HOST` at both |
| `tests/test-install-placement.sh:615` | M10 (6) with `all` | every refused path (`:608-609`) is shared or Claude Code's, so the refusal holds for three hosts | keep `all` |
| `tests/test-full-install.sh:396-397` | `case_idempotent_rerun` with `all` | the regression it pins is the codex/copilot `place_kernel` ping-pong (comment `:392-394`) | `$EVERY_HOST` at both; comment unchanged |
| `tests/test-full-install.sh:429-430` | `case_no_symlink_churn` with `all` | "5 .bak per `all` re-run" (`:424`) needs the five kernel writers | `$EVERY_HOST` at both; comment `:424` says five hosts |
| `tests/test-full-install.sh:445` | `case_universal_router` loops over the five by name | unaffected | no change |
| `tests/test-full-install.sh:714` | banner "full five-tool install contract" | still true | no change |
| `tests/test-unified-graph-install.sh:253` | `all --force` then negative asserts on `.codex` and `.github` (`:254`, `:258`) | without the frozen hosts those asserts pass vacuously, since nothing re-projects there | `$EVERY_HOST` |
| `tests/test-plant-state.sh:156-157` | re-install with `all` over a plant's plan records | asserts plan records survive; holds for any adapter set | keep `all` |
| `tests/test-install-adoption.sh:291`, `:313`, `:378`, `:395`, `:405` | capture `github-copilot` stderr and grep it | each greps for text it needs; one more `DEPRECATED` line does not disturb a positive or negative match | no change; the tester confirms at RED |
| `tests/test-seed-budgets.sh:44` | `codex` install log | read only on failure | no change |
| `tests/test-plant-state.sh:215-218` | `codex` install log grepped for "beyond the" | positive match, unaffected | no change |
| `tests/check-coverage-binder.py:36-50` | `COVERED` set | new check needs its planted case | add `check_host_tiers` |

Nothing else in `tests/` calls `install.sh all`. The search that established
this covered `tests/*.sh` and `tests/*.py`.

## §5 Slice sequence

| # | Slice | Contracts | Depends on |
|---|---|---|---|
| S-0 | Move the §4 call sites to `$EVERY_HOST` against unchanged `install.sh`; the gate stays green | none; characterization | — |
| S-1 | Installer: tier arrays, `all`, notice, skipped-host warning, `--check` notice, SPEC-0001 rows | first five in §3 | S-0 |
| S-2 | Hook fail-open regression; expected green on arrival, so RED is shown by a mutation (make `status-hook.py` raise past its `except`) | `CLAUDE_HOOKS_FAIL_OPEN_ON_COPILOT_ENVELOPE` | — |
| S-3 | `check_host_tiers` and the matrix tier section | `HOST_TIERS_AGREE` | S-1 |
| S-4 | README, INSTALL, DOCUMENTATION, reference page, integration READMEs, CHANGELOG, manifest | none; prose, run through `tools/prose-lint.py` | S-1, S-3 |

S-0 lands first so that no suite is narrowed by S-1 even for one commit.

## §6 Open questions for the owner

1. **SPEC-0001 status.** The spec is `back-written`, and these contracts are
   forward-written with a RED. Either the spec moves to `active` with the new
   rows (and the sign-off questions §0 raises), or the contracts go into a new
   SPEC-0003. Recommendation: keep one spec for one surface and move it to
   `active`. This is the architect's call to confirm with the tester at RED,
   since `spec-lint` decides what each status demands.
2. **Harvest targeting in the protocol.** ADR-0009 says harvests target the
   first-class hosts. `protocols/harvest.md` does not say so. Adding a line
   there changes a machinery node every plant installs. Recommendation: leave
   the protocol alone until a harvest meets the question, and let the matrix's
   tier section carry it.
3. **Notice wording in the frozen READMEs.** The owner allowed "deprecation
   notices" only. The Copilot README line about `.claude/settings.json` hooks
   is a fact, not a notice; confirm it may go in.

## §7 Slice records

Empty until S-0 lands.

## §8 Review rounds

Empty.
