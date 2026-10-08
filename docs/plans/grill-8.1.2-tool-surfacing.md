# grill.md: Plan of Record: round 8.1.2, tool surfacing (install, graft, grow)

## 0. Metadata
- Project: CYPRESS seed
- Feature or goal: make the placed source index found by topic and built in every plant once install, grow or graft has run, and make what a plant must set before trusting it visible, with the exact fix, after each of them; patch 8.1.2 over 8.1.1
- Date: 2026-10-07
- Owner: the steward; the orchestrating session plans, briefs and commits
- Tier: T3. Protocol: `protocol.specify` (SPEC-0007 grows by an 8.1.2 slice), then `protocol.grill`
- Current phase: specified by `architect-8.1.2`, rewritten on the owner's rulings of questions 2 and 3 by `architect-8.1.2b`; the owner ruled §12 questions 1, 8 and 9 on 2026-10-07 ("1 ok 2 ok 3 go"), and `architect-8.1.2c` wrote the SPEC-0001 amendment (increment 2); product signed §3 and §9; `architect-8.1.2d` applied the `security-8.1.2` lines S1 to S4 and arms A1 to A4 (security signed) and the `devils-advocate-8.1.2` changes that need no owner ruling; three owner questions pending (§12 questions 12 to 14); next the owner's rulings, product's re-read of §3 and §9, tester §10, then RED
- Related files: `skills/source-index/SKILL.md` (new), `manifest.json`, `tools/source-index.py`, `tools/growth-audit.py`, `install.sh`, `tools/graft-run.py` (docstring only), `protocols/graft.md`, `protocols/grow.md`, `protocols/canonize.md`, `skills/toolcraft/SKILL.md`, the catalog template `tools/index.md` under `templates/docs/`, `documentation/source-index.md`, `docs/specs/SPEC-0001-install-placement.md`, `tests/test-source-index.sh`, `tests/test-full-install.sh`, `tests/test-growth-audit.sh`, `tests/run.sh`
- Related documentation: `docs/plans/grill-8.1.0-source-index.md` (the round that built the tool; its §10 measurements); the steward plant's card `docs/graph/tools/source-index.md` (plant-written, read as evidence only)
- Related ADRs: [ADR-0030](../decisions/adr-0030-a-seed-tool-is-surfaced-by-a-seed-skill.md) (accepted 2026-10-07: a placed seed tool is surfaced by a seed skill node); [ADR-0029](../decisions/adr-0029-source-index-is-derived-scratch.md) (accepted; its "Amendment, 8.1.2", ratified 2026-10-07, records that the installer runs the build); [ADR-0021](../decisions/adr-0021-seed-only-procedures-stay-home.md) (the manifest names what the installer places)
- Related specs: [SPEC-0007](../specs/SPEC-0007-source-index.md) §4 "Surfacing (8.1.2)" (every contract of this plan); [SPEC-0001](../specs/SPEC-0001-install-placement.md) (`BACKUP_BEFORE_REPLACE` and the seed-skill placement the new skill rides on, unchanged; increment 2 added §2's line for the build, an And clause in `SINGLE_WRITER` and an Except clause in `IDENTICAL_RERUN_IS_INERT`)
- Related libraries: none (stdlib Python and Git)
- Baseline: seed `main` at `e3b22be` (v8.1.1)

## 1. Artifact Discovery
- Existing files inspected: `install.sh` (`place_file` 389, `place_generated` 478, `place_graph_machinery` 1065 to 1087, which places every `skills/*/SKILL.md` as `docs/graph/skills/<name>.md`, `place_graph_scaffold` 1522 to 1586, `fill_plant_facts` 1588 onwards, the NEXT STEP banners 3226 to 3275); `manifest.json` (`tools`, `skills`, `templates`, `docs_skeleton`); `tools/graft-audit.py` (MODE 1 classes, the knowledge-overwrite flag, MODE 2 byte-identity); `tools/growth-audit.py` (`required_collections` 367, `collection_leaves` 573, `lint_collections` 1058, `VERDICTS`); `tools/graft-run.py` (steps 1 to 8); `templates/tool-page.template.md`; the catalog template `tools/index.md` under `templates/docs/`; `templates/knowledge-graph/_schema.md` ("Tiers": `tools/**` is Tier 3); `templates/knowledge-graph/graph-lint.py` (`KINDS`, `MACHINERY_DIRS`, `check_artifacts`)
- Existing docs inspected: `skills/toolcraft/SKILL.md`; `skills/context-router/SKILL.md` (frontmatter); `protocols/graft.md` (headings, Phase 7 gate table, output format); `protocols/grow.md` 630 to 660 (the Phase 2 `build --json` step); `templates/grill.template.md`; `templates/adr.template.md`
- Existing tests inspected: `tests/run.sh` (`ACTIVE_PLAN`, the spec-lint and grill-lint steps); `tests/graph-route-eval.sh` and `tests/graph-routes.golden.tsv` (the node-route corpus over a fresh install); `tests/test-source-index.sh` X430 (asserts the re-install leaves the cache and the next query rebuilds it); `tests/test-full-install.sh` E15 (asserts no `.cypress/source-index/` after an install); `tests/test-install-placement.sh` (M7's `is_installer_state`, `case_recover` over a fresh non-Git target, `tree_sig` checks); `tests/helpers/plant.sh` `plant_base` (installs into a non-Git directory); `tests/seed-lint.py` `install_write_sites` (a command that runs a tool is no write site)
- Existing specs inspected: `docs/specs/SPEC-0007-source-index.md` (§2, §4 `SOURCE_INDEX_IS_PLACED`, `REPO_CLAIM_READ_ALIKE_BY_ROUTER_AND_ANCHORS`, §6 "Incomplete", "Query answer", "CLI", §7, §10); `docs/specs/SPEC-0001-install-placement.md` (§2, §4 `SINGLE_WRITER`, `BACKUP_BEFORE_REPLACE`, the 8.0.0 expertise contracts, §6 "Selective placement")
- Existing architecture signals: the router routes Tier-2 nodes only; seed skills are placed and refreshed on every install by `place_file`; `tools/` is a growth-audit collection, so a seed page there is a substantive leaf of every plant; the steward plant routes the tool through its own `subsystem.source-index`, and `graph-lint.py --plan "find where a function is defined"` loads no node there
- Libraries already wikified: none, no library is involved
- External sources downloaded: none
- Constraints discovered: until this round the installer wrote no source-index cache (SPEC-0007 `SOURCE_INDEX_IS_PLACED`, ADR-0029 Consequences, the `manifest.json` description of `tools/source-index.py`, `documentation/source-index.md` "The installer never writes it"), each of which changes; `install.sh` writes `.cypress/seed.json` (so `.cypress/` exists) as its last write, then prints the `NEXT STEP` notices and the closing banner; `--check` and `--expertise propose` exit before any placement; macOS has no `timeout` command and `install.sh` is bash 3.2; the tool takes the plant root from its working directory; in a non-Git directory `build` exits 0 and writes nothing (`NO_GOVERNED_REPOSITORY`); `graft-run.py` runs `install.sh` on its stage (step 3, `install.log`) and growth-audit's lint (step 6, `coverage.txt`), and graft's Phase 7 applies with `install.sh` in the plant; `docs/graph/tools/index.md` and its cards are plant-owned (`skill.toolcraft`); a backup over plant-authored graph content is flagged by `graft-audit.py`; `SINGLE_WRITER` counts every in-place rewrite of a plant file; plants are read-only evidence for this round

## 2. Shared Understanding
The owner's words (2026-10-07), verbatim: "when doing graft do we create/add/update all the things the new tools need to be used and shine?", then, after the session's answer, "go do it. update graft and install/growth".

The session's answer named four gaps: no routable page for the tool in a plant, the seed-only user guides, `repo:` values that name nothing (turboquant holds six comma lists), and no prompt to write `docs/graph/source-index.json`. The owner approved (A) a seed tool card and catalog row in every plant, and (B) a checklist after install and graft, also reported by grow or growth-audit.

Success means: in any plant, a session that asks what depends on a file, which tests a change reaches, which pages cite a file or where a name is defined is routed to the tool; after an install, a grow or a graft the plant sees the build's time and counts, every `repo:` value that names nothing and the test-class hints, from one command, `source-index.py build`.

Design change from (A), put to the owner (§12 question 1, ADR-0030): a seed skill node, not a card, carries the tool, because a Tier-3 card is not routed and a seed card in `tools/` breaks growth-audit's `ABSENT` rows for that collection.

The owner's rulings on questions 2 and 3 (2026-10-07), verbatim: "2 ACTUALLY BUILD IT. a user cannot be expected to know that it needs to do things if it executes a graft/install/growth. the plant needs to be ready to go from te get-go after executing the protocols. 3 yes". Question 1 is taken as yes on the same ground (a tool no route finds is not ready), until the owner rules on ADR-0030.

Success therefore also means: after an install, a graft or a grow, the plant's cache is built (where the plant has a governed repository) and the report has been printed; every setup gap the build can detect is named in that report with the exact fix. The build does not judge whether `TEST_GLOBS` is right, only whether it matches, and a config pattern that matches no file is not reported (§12 question 14, pending owner). The routing claim holds for path-free phrasings; a task that names a path a node owns loads that node, and the skill then reaches the session through the host's skill listing (§12 question 12, option (b), pending owner).

Out of scope (SPEC-0007 §2): seed cards or rows in a plant's `docs/graph/tools/`; a growth-audit verdict; an install or graft that fails or stops on the build; a flag to skip it; any tool writing a plant's config, `TEST_GLOBS` or `repo:` values; skills for the other placed tools; the seed-only user guides; editing any plant.

## 3. User Goal
- Primary user: a session in any plant; the steward after an install or graft
- Primary outcome: the tool is used when its question comes up, and its answers are trusted only once the plant's `repo:` values and test class are right
- Job to be done: find the tool by topic; have it built by the protocol that installed or grafted the plant; see the setup items and their fixes after each install, grow and graft
- Acceptance criteria (link to spec §9): SPEC-0007 §9, the 8.1.2 rows `product` adds
- Non-goals: fixing a plant's `repo:` values or test config by tool; gating a graft on a hint

## 4. Operating Constraints
- Runtime constraints: stdlib Python 3.12 or newer and Git; bash 3.2 syntax in `install.sh`; no new dependency
- Security constraints: the installer and `growth-audit.py` run the tool as `python3 -I -B`, so no plant file is imported in place of a standard module, and print its stdout only on exit 0, never its stderr (`security-8.1.2` S1, S2); `growth-audit.py` runs the seed's own `tools/source-index.py`, never plant code; the build stays read-only over repositories and writes only `.cypress/source-index/` (SPEC-0007 §5)
- Privacy constraints: synthetic fixtures only; no plant name in seed files or tests
- Data constraints: the cache stays derived scratch (ADR-0029); the plant config stays plant-owned and never placed
- Cost constraints: the batch sizes of `delegation.effort-scale`; batch per wave, no micro-loops (owner)
  - Plan approval (`grill.plan-approval`), 2026-10-07: the owner approved (A) and (B) in the session and ruled §12 questions 2 and 3; question 1 is taken as yes pending ADR-0030. Levers this plan uses: none defined beyond the batch sizes (default)
  - Owner-only prerequisites: the ratification of ADR-0030 (question 1) and of the ADR-0029 amendment (question 8), and the go for the SPEC-0001 amendment (question 9), before RED (increment 3)
  - Scoped standing grant: none asked
- Latency constraints: `build` within SPEC-0007 §5; the install's build bounded by `INSTALL_BUILD_TIMEOUT` and growth-audit's by `GROWTH_REPORT_TIMEOUT` (120 s each); every install now spends the build's time (0.06 s on an empty plant to 3.7 s on a 4,320-file llama.cpp clone, measured cold at 3.64 s by `devils-advocate-8.1.2`); a graft spends about four builds (stage install, stage lint, apply, coverage gate)
- Compliance constraints: none
- Maintenance constraints: one home per rule (the build report and its fixes in `tools/source-index.py`; the installer and growth-audit print it, never restate it); the seed reads as if the feature always existed; tests only for real contracts; doctrine edits carry no tests of their own, the lints are their proof (`crosscut.operator-seed-rounds` in the steward plant)

## 5. Research Summary
no external dependency — every increment uses stdlib Python and Git, which the seed's tools already use; no §9 row depends on a `docs/graph/libraries/` page. The evidence is the seed's own source (§1):
- The router's tiers: `templates/knowledge-graph/_schema.md` "Tiers" puts `docs/graph/tools/**` in Tier 3, loaded only when a Tier-2 node names it.
- Growth-audit: `required_collections` makes `tools/` a collection row; `lint_collections` turns an `ABSENT` row with an authored leaf into `CONTRADICTED`.
- Placement: `place_graph_machinery` places every `skills/<name>/SKILL.md` on every run; the skill projection writes `.claude/skills/<name>/SKILL.md` with no new code.
- Precedent for a tool's usage living in a skill: `skill.humanizer` with `prose-lint.py` as its floor.

## 6. Decisions Made
| Decision | Rationale | Evidence | Reversibility | ADR | Date |
|---|---|---|---|---|---|
| Design latitude: balanced | new structure only where the change needs it: one seed skill node, one report in an existing command, one step at the end of the installer | the owner, 2026-10-07: "go do it. update graft and install/growth" | reversible | — | 2026-10-07 |
| Tier T3 | a new seed skill, a changed CLI output, the installer and growth-audit | kernel §0 | not applicable | — | 2026-10-07 |
| Owning spec: SPEC-0007, an 8.1.2 slice; SPEC-0001 gains only a pointer and an Except clause | every new behaviour is about the source index; the installer's run of it is a SPEC-0007 contract (`INSTALL_RUNS_THE_BUILD`), and SPEC-0001 keeps the placement rules it already owns | SPEC-0007 §4 "Surfacing (8.1.2)"; SPEC-0001 §2, `IDENTICAL_RERUN_IS_INERT` | reversible | — | 2026-10-07 |
| The tool's seed-owned page in a plant is a seed skill node `skill.source-index`, not a card in `docs/graph/tools/` (question 1, taken as yes) | a card is Tier 3 and not routed; a seed card breaks growth-audit's `tools/` rows; the skill is placed, refreshed, retired and projected by machinery that exists, on every install and graft | §5; ADR-0030 | reversible | [ADR-0030](../decisions/adr-0030-a-seed-tool-is-surfaced-by-a-seed-skill.md) | 2026-10-07 |
| The report has one home, `source-index.py build`: time, counts, `repo-unresolved`, the test-declaration records, one `BUILD_FIX` line under each record, two hints | the rules it reports (`repo_kind`, `TEST_GLOBS`, the config) live in the tool and its helper; a second reader would be a second home; a fix beside each record is what makes "ready to go" checkable by a reader who knows nothing | SPEC-0007 §6 "Build report", `BUILD_RECORDS_NAME_THEIR_FIX` | reversible | — | 2026-10-07 |
| The installer runs the placed `build` as its last step and prints the report (question 2, the owner: "ACTUALLY BUILD IT") | a plant must be ready after the protocol runs; graft applies with the installer, so graft gets it without a step of its own | SPEC-0007 `INSTALL_RUNS_THE_BUILD` | reversible | [ADR-0029](../decisions/adr-0029-source-index-is-derived-scratch.md) (amendment) | 2026-10-07 |
| Where: after the stamp (the last write) and before the `NEXT STEP` notices and the closing banner | every file is placed, so a build failure leaves nothing unplaced, and the report is read where the install ends; `--check`, `--expertise propose` and refusals exit earlier and run none | `install.sh` main flow, `write_seed_stamp` then the notices | reversible | — | 2026-10-07 |
| Every install that places files runs it, not only the first | a re-install or a graft can move the key (the tool, HEAD, the config), and "has a cache" is no sign the report was read; the cost is one build per install | SPEC-0007 `GRAFT_REBUILDS_THE_CACHE` as amended | reversible | — | 2026-10-07 |
| Fail-open: a failed, slow or missing build never changes the install's exit code; it prints `INSTALL_BUILD_FAILED` with the rerun command | the build is advice about a derived cache; an install that fails on it would block a graft on scratch | SPEC-0007 §7 `INSTALL_BUILD_FAILED` | reversible | — | 2026-10-07 |
| Bound and interpreter: `INSTALL_BUILD_TIMEOUT` 120 s through Python's subprocess timeout, the same `python3` the installer runs, in isolated mode (`-I -B`), stdin closed, working directory the plant root | macOS has no `timeout` command and `install.sh` stays bash 3.2; the interpreter is in the cache key, so the session's `python3` reuses the cache; `-I` stops a plant file such as `docs/graph/fnmatch.py` from shadowing a standard module the tool imports (`security-8.1.2` C1, shown on a synthetic plant) | SPEC-0007 §5 Security, §6 "Build report"; ADR-0029 key | reversible | — | 2026-10-07 |
| The installer and growth-audit print the build's stdout only on exit 0, never its stderr; the run is guarded under `set -euo pipefail` and decoded with `errors="replace"` | a traceback carries raw strings the `?` replacement never saw; a crash or an undecodable byte must not stop an install (`security-8.1.2` S2, S3) | SPEC-0007 §6 "Build report", §7 `INSTALL_BUILD_FAILED`, `SOURCE_INDEX_REPORT_UNAVAILABLE` | reversible | — | 2026-10-07 |
| `build` names each nested Git work tree inside a governed repository that no `repo:` names (`repository-unnamed`, build only), with its fix | its code is in no answer, silently, at every first install before grow writes `repo:` nodes; the root's listing already holds it (`devils-advocate-8.1.2` 1a) | SPEC-0007 §6 "Build report", §7 `REPOSITORY_UNNAMED` | reversible | — | 2026-10-07 |
| The readiness claim is "every setup gap the build can detect is named with its fix", not "no finding means ready"; the `build` `ACTION_LINE` names the setup items | an unconfirmed `TEST_GLOBS` default and a config pattern that matches nothing are not detected (`devils-advocate-8.1.2` 1b, 11) | SPEC-0007 §3, §6 "Build report"; ADR-0030 | reversible | — | 2026-10-07 |
| The installer runs the placed copy; growth-audit runs the seed's copy | after an install the two are byte-identical; growth-audit can be run against a plant whose placed copy is older (before an apply), and the seed copy runs no plant code | SPEC-0007 §6 "Build report" | reversible | — | 2026-10-07 |
| No plant, no Git, no code: the build still runs and its report names `no-repository`, `git-unavailable` or `no-test-files` with the fix; it writes nothing where there is no repository | one rule for every target; the fix is the step a person would otherwise have to know | SPEC-0007 `BUILD_RECORDS_NAME_THEIR_FIX`, §7 `NO_GOVERNED_REPOSITORY` | reversible | — | 2026-10-07 |
| Growth-audit prints the build report after its verdicts, never a verdict, running the seed's copy (question 3, the owner: "yes") | the owner named growth-audit; a report keeps the coverage gate's meaning | SPEC-0007 `GROWTH_AUDIT_PRINTS_THE_BUILD_REPORT` | reversible | — | 2026-10-07 |
| The owner's rulings of §12 questions 1, 8 and 9: ADR-0030 accepted, the ADR-0029 amendment ratified, go for the SPEC-0001 amendment | the owner, 2026-10-07: "1 ok 2 ok 3 go"; the SPEC-0001 amendment keeps its contracts true about the build's cache without a test change (increment 2) | ADR-0030 and ADR-0029 Ratification sections; SPEC-0001 §12 entry of 2026-10-07 | reversible | [ADR-0030](../decisions/adr-0030-a-seed-tool-is-surfaced-by-a-seed-skill.md), [ADR-0029](../decisions/adr-0029-source-index-is-derived-scratch.md) | 2026-10-07 |
| `graft-run.py` gets no code change | its step 3 runs the installer (so the build, kept in `install.log`) and its step 6 runs growth-audit's lint (the report, kept in `coverage.txt`); graft's Phase 7 apply prints the report in the plant itself; graft.md tells the steward where to read it | `tools/graft-run.py` docstring steps 3 and 6; `protocols/graft.md` Phase 7 | reversible | — | 2026-10-07 |
| Test-name hints read a closed list of name patterns and never gate | a name is a guess about a project's habits; the owner rules on each hint | SPEC-0007 §6 `TEST_NAME_PATTERNS` | reversible | — | 2026-10-07 |
| A plant's `repo:` values, `TEST_GLOBS` and config are corrected by people (graft Phase 6, grow's plant facts, canonize), never by a tool; the report names each with its fix | each needs a choice only the owner or an author with understanding can make | SPEC-0007 §6 `BUILD_FIX`, §7 `REPO_VALUE_UNRESOLVED` recovery | reversible | — | 2026-10-07 |

## 7. Options Considered
| Option | Benefits | Costs | Risks | Outcome |
|---|---|---|---|---|
| (A) seed card in `docs/graph/tools/` plus a seed block in `tools/index.md` | the owner's approved shape; a catalog row | still needs a Tier-2 node to be routed; a provenance rule, a growth-audit exclusion, a `--unfilled` block reader, a second SINGLE_WRITER exception, a backup class | every plant with an `ABSENT` `tools/` row fails its next graft gate until the exclusion lands | rejected for ADR-0030, put to the owner (§12 question 1) |
| (S) seed skill `skill.source-index` | routed by `load_when`; native host skill; no new mechanism; plant cards untouched | a sixteenth seed skill; the figures in README and the reference pages move at release | a plant skill of the same name is backed up (none known) | chosen (question 1 taken as yes) |
| Phrases on `skill.context-router` | no new node | a second subject in a node most tasks load | dilutes the knowledge rule's routing | rejected |
| A new subcommand `check` for the checklist | `build` output unchanged | a sixth verb for what `build` already computes | two commands to name | rejected: `build` is the command the owner named |
| Growth-audit verdict on report lines | forces a fix | a hint is a guess; a verdict blocks a graft on it | false blocks | rejected: report only |
| The installer only names the build (the first draft) | no install time; no cache written by an install | relies on someone reading a line and acting | the plant is not ready after the protocol | rejected by the owner (question 2) |
| The installer runs the build only when no cache exists | no time on re-installs | a re-install or graft that moved the key prints nothing, and the report is never seen again | stale advice | rejected: every install |
| The installer runs it through growth-audit, or runs the seed's copy | one runner | growth-audit is a seed-only tool that needs a coverage record; the seed's copy is not the command the report tells a person to rerun | a report whose rerun line names another file | rejected: the placed copy |
| GNU `timeout` around the build | one word in bash | absent on macOS, the CI's mac leg | the install dies on macOS | rejected: Python's subprocess timeout |
| A `--no-source-index` flag | faster test installs | a second path through every install; the owner wants the plant ready without choices | plants installed without it | rejected; test fixtures are non-Git and the build there costs milliseconds |
| `graft-run.py` prints the report after its gate table | one screen | a second reader of growth-audit's output, in a tool whose output is the gate table | an advice line read as a gate | rejected: Phase 7's apply prints it in the plant, and graft.md names the log |

## 8. Architecture Plan
- System boundary: the seed's `tools/source-index.py` (domain: the build report and its fixes), `install.sh` and `tools/growth-audit.py` (adapters that run it and print it), and one seed skill node (knowledge); no plant file is written by any of them beyond the cache a build writes
- Main components: `skills/source-index/SKILL.md` (routing and usage); `build`'s report (§6 "Build report", `BUILD_FIX`); the installer's last step (`INSTALL_BUILD_HEAD`, `INSTALL_BUILD_FAILED`, `INSTALL_BUILD_TIMEOUT`); `growth-audit.py`'s report block
- Interfaces: `build` text view (fix lines under records) and `--json` keys `seconds` and `hints` (`ANSWER_SCHEMA` `/1`, keys added); growth-audit `--json` key `source_index_report`; the installer's output lines
- Data flow:

```mermaid
flowchart LR
  I[install.sh: last step] -->|places| S[docs/graph/skills/source-index.md]
  I -->|runs placed copy, cwd = plant, 120 s| B[source-index.py build]
  T[graft Phase 7 apply / graft-run step 3] --> I
  R[graph-lint --plan] -->|load_when| S
  S -->|tells the session to run| Q[impact / affected-tests / anchors / symbols]
  G[growth-audit.py lint] -->|runs seed copy, cwd = plant| B
  B --> C[(.cypress/source-index/)]
  B -->|time, counts, records + fix, hints| I
  B -->|same report| G
  G -->|report after verdicts| P[grow delivery / graft record]
```
- Error handling: a failed or slow build prints `INSTALL_BUILD_FAILED` in the installer and `GROWTH_REPORT_FAILED` in growth-audit, and changes nothing else (SPEC-0007 §7)
- Observability: the report lines in the install output and the growth-audit output; `graft-run.py` keeps both under `<stage>/graft-run-logs/` (`install.log`, `coverage.txt`)
- Security posture: the installer runs a file it has just placed from the seed, in isolated mode (`python3 -I -B`), so it imports no plant code; growth-audit runs the seed's copy the same way; both print the build's stdout only on exit 0 and never its stderr; the build's existing guarantees hold (read-only over repositories, writes only `.cypress/source-index/`)
- Deployment model: seed release 8.1.2; plants receive it by install or graft. A fresh install places the skill, builds and prints the report; an existing plant's graft does the same at its apply, its Phase 7 growth-audit run prints the report again, and Phase 6 corrects the `repo:` values it names
- Environment parity: not applicable, no deploy chain

## 9. Implementation Plan

Increments are inline; numbers are dependency order. Increment 1 carries the slice-1 and slice-2 contracts this plan leaves as they are. The owner ruled §12 questions 1, 8 and 9 on 2026-10-07; increment 2 is written, and RED (increment 3) waits for the reviews §14 names.

| Spawn | Increments | Worker | Batch rule (`delegation.effort-scale`) |
|---|---|---|---|
| — | 1 | none | carried from the 8.1.0 plan, no spawn |
| A1 | 2 | `architect` | spec text, one file |
| R1 | 3 | `tester` | RED medium: one spawn, eight cases and two amended ones |
| G1 | 4 | `implementer` | GREEN medium: one |
| G2 | 5, 6 | `implementer` | GREEN medium-low: two |
| P1 | 7 | one writer | prose, one file set |
| V1 | 8 | session | verify and one measurement |

G1 and G2 may run side by side after R1: their files are disjoint. Increment 6's installer cases pass only with increment 4's fix lines; G2's gate runs after G1 lands.

### Increment 1 — Carried: the slice-1 and slice-2 contracts
- Spec contracts: SPEC-0007/BUILD_INVENTORIES_THE_CODE_OF_EVERY_GOVERNED_REPOSITORY, SPEC-0007/BUILD_IS_DETERMINISTIC, SPEC-0007/CACHE_WRITTEN_SELF_IGNORED, SPEC-0007/CACHE_REUSED_WHILE_THE_KEY_HOLDS, SPEC-0007/CACHE_REBUILT_WHEN_THE_KEY_CHANGES, SPEC-0007/LINK_PYTHON_IMPORT_CERTAIN, SPEC-0007/LINK_SHELL_INVOCATION_CERTAIN, SPEC-0007/LINK_PATH_LITERAL_AND_DIRECTORY_ARE_MAYBE, SPEC-0007/LINK_TS_SPECIFIER_CERTAIN, SPEC-0007/UNPINNED_REFERENCE_RECORDED_WITH_ITS_REASON, SPEC-0007/TESTS_ARE_THE_PLANTS_TEST_GLOBS, SPEC-0007/PLANT_CONFIG_REPLACES_EACH_DEFAULT_KEY, SPEC-0007/WALK_NEAREST_FIRST_ONCE, SPEC-0007/WALK_CHAIN_IS_ITS_WEAKEST_LINK, SPEC-0007/WALK_FLOOR_LISTED_APART_AFTER_THE_INPUT_ROWS, SPEC-0007/WALK_DELETED_INPUT_REACHES_ITS_NAMERS, SPEC-0007/INPUT_FORMS_RESOLVED, SPEC-0007/WALK_INCOMPLETE_NAMES_REASON_AND_ACTION, SPEC-0007/AFFECTED_TESTS_ARE_THE_WALK_FILTERED, SPEC-0007/AFFECTED_ALWAYS_RUN_LISTED_APART, SPEC-0007/ANCHORS_NAME_CITING_PAGES_OR_UNCITED, SPEC-0007/ANCHORS_BASENAME_IS_MAYBE_AMBIGUOUS_IS_INCOMPLETE, SPEC-0007/OUTPUT_CARRIES_NO_RAW_CONTROL, SPEC-0007/SYMBOLS_PYTHON_DEFINITIONS_CERTAIN, SPEC-0007/SYMBOLS_LINE_READ_DECLARATIONS_ARE_MAYBE, SPEC-0007/SYMBOLS_LIST_EVERY_DEFINITION, SPEC-0007/SYMBOLS_UNREADABLE_FILE_MAKES_IT_INCOMPLETE, SPEC-0007/HISTORY_ROWS_ARE_MAYBE_WITH_THEIR_COUNT, SPEC-0007/HISTORY_ONLY_ADDS, SPEC-0007/HISTORY_SHALLOW_OR_MISSING_IS_INCOMPLETE, SPEC-0007/ANCHORS_MOVED_EQUALS_THE_NAMED_PATHS, SPEC-0007/ANCHORS_MOVED_WITHOUT_A_LIST_IS_INCOMPLETE, SPEC-0007/REPO_CLAIM_READ_ALIKE_BY_ROUTER_AND_ANCHORS
- Files touched: none
- Tests to write (RED): none — implemented and green at `68c970e` under `docs/plans/grill-8.1.0-source-index.md` increments 3 to 20; this plan changes none of them except `SOURCE_INDEX_IS_PLACED` and `GRAFT_REBUILDS_THE_CACHE`, amended for the installer's build and carried by increment 3, and `build`'s added report keeps their outputs (the count line and `ANSWER_SCHEMA` `/1`)
- Behavior added: none
- Gate: their §10 rows stay green in increment 7's full gate
- Rollback path: none needed
- Effort: low
- Phase: GREEN, done in 8.1.0
- Depends on: none

### Increment 2 — SPEC-0001 amendment for the installer's build
- Spec contracts: none — spec text only: SPEC-0001's `IDENTICAL_RERUN_IS_INERT` gains an Except clause and its `SINGLE_WRITER` an And clause (census unchanged); their tests stay as they are
- Files touched: `docs/specs/SPEC-0001-install-placement.md`: §2 in scope, one line: the source-index build the installer runs as its last step, owned by SPEC-0007 `INSTALL_RUNS_THE_BUILD`; `SINGLE_WRITER`: the cache under `.cypress/source-index/` is the placed tool's own atomic write, outside the census of the installer's writes, which is unchanged; `IDENTICAL_RERUN_IS_INERT`: Except the cache, which the build replaces with equal bytes when nothing moved (SPEC-0007 `BUILD_IS_DETERMINISTIC`); changelog line
- Tests to write (RED): none — no test changes: `seed-lint`'s write-site census sees no new site (a command that runs a tool is none), and the placement suites install into non-Git targets, where the build writes nothing; increment 8's full gate proves both
- Behavior added: none
- Gate: `tests/run.sh` spec-lint and seed-lint steps green
- Rollback path: revert the commit
- Effort: low
- Phase: prose, written 2026-10-07 by `architect-8.1.2c`
- Depends on: none (§12 question 9, ruled 2026-10-07)

### Increment 3 — RED for the 8.1.2 contracts
- Spec contracts: SPEC-0007/SOURCE_INDEX_SKILL_ROUTES_ITS_FOUR_QUESTIONS, SPEC-0007/BUILD_REPORTS_ITS_TIME_AND_COUNTS, SPEC-0007/BUILD_NAMES_REPO_VALUES_THAT_NAME_NOTHING, SPEC-0007/BUILD_NAMES_TESTS_OUTSIDE_THE_TEST_CLASS, SPEC-0007/BUILD_HINTS_EXCLUDE_FOR_NON_TEST_FILES, SPEC-0007/BUILD_RECORDS_NAME_THEIR_FIX, SPEC-0007/INSTALL_RUNS_THE_BUILD, SPEC-0007/GROWTH_AUDIT_PRINTS_THE_BUILD_REPORT, SPEC-0007/GRAFT_REBUILDS_THE_CACHE (amended), SPEC-0007/SOURCE_INDEX_IS_PLACED (amended)
- Files touched: `tests/test-source-index.sh` (the build, fix, skill and installer cases; X430's last two checks rewritten: the re-install's output holds `Cache: rebuilt (build forced)` and the next query reports `reused`), `tests/test-full-install.sh` (E15: the `.cypress/source-index` absence check struck, the config check kept), `tests/test-growth-audit.sh` (the report case and its `SOURCE_INDEX_REPORT_UNAVAILABLE` arm), `tests/run.sh` (`ACTIVE_PLAN` to this plan), SPEC-0007 §10 file cells and labels
- Tests to write (RED): 8 cases, one per new contract above, the tester names them; failure arms inside them as §10 says (`INSTALL_BUILD_FAILED` in the installer case, `REPOSITORY_UNNAMED` in the `repo:` case, the owned-path arm in the skill case, the security arms A1 to A4); X430 rewritten, E15 trimmed; the case file's `ACTION` prefix for `build` follows the new `ACTION_LINE`; X459's case checks guarded by the case-sensitivity probe of SPEC-0007 §10
- Behavior added: none; every new case and X430 fail for the missing behaviour, not for a fixture error
- Gate: the eight cases and X430 fail; E15 and the rest of `tests/run.sh` stay green
- Rollback path: revert the RED commit
- Effort: medium
- Phase: RED
- Depends on: increment 2

### Increment 4 — The build report
- Spec contracts: SPEC-0007/BUILD_REPORTS_ITS_TIME_AND_COUNTS, SPEC-0007/BUILD_NAMES_REPO_VALUES_THAT_NAME_NOTHING, SPEC-0007/BUILD_NAMES_TESTS_OUTSIDE_THE_TEST_CLASS, SPEC-0007/BUILD_HINTS_EXCLUDE_FOR_NON_TEST_FILES, SPEC-0007/BUILD_RECORDS_NAME_THEIR_FIX
- Files touched: `tools/source-index.py`
- Tests to write (RED): none here; increment 3 holds them
- Behavior added: `build` prints `BUILD_TIME_LINE`, adds `repo-unresolved`, `repository-unnamed`, `no-test-declaration` and `no-test-files` to its `incomplete`, closes with the new `build` `ACTION_LINE`, prints a `BUILD_FIX` line under each record, and adds `hints` (§6 "Build report"); the answer gains `seconds` and `hints`; the cache is unchanged
- Gate: the five cases green; `tests/test-source-index.sh` whole green but for the increment-6 cases
- Rollback path: revert the commit
- Effort: medium
- Phase: GREEN
- Depends on: increment 3

### Increment 5 — The seed skill
- Spec contracts: SPEC-0007/SOURCE_INDEX_SKILL_ROUTES_ITS_FOUR_QUESTIONS
- Files touched: `skills/source-index/SKILL.md` (new: node frontmatter with `id: skill.source-index`, `origin: seed`, `load_when` phrases that route `SKILL_ROUTE_TASKS` and their everyday wording, a `description` for host skills; a body in the sections of `templates/tool-page.template.md` written for any plant: invocation, outputs, when to use and when not, that install, graft and growth-audit run `build` and print its report, the one-line limit of SPEC-0007 §5 (a recommendation over cooperative code; a file's absence from `dependents` or `tests` is never proof), that a session reruns it after changing `TEST_GLOBS`, the config or a `repo:` value, `docs/graph/source-index.json`, pitfalls, and the protocols that call it), `manifest.json` (`skills` entry)
- Tests to write (RED): none here; increment 3 holds it
- Behavior added: the tool is routed by topic in every plant and projected into each harness's skills, at every install and graft
- Gate: the skill case green; `graph-lint.py` and `agent-lint.py --lint` clean on a fresh install; `tests/graph-route-eval.sh` ratchets hold
- Rollback path: revert the commit
- Effort: medium-low
- Phase: GREEN
- Depends on: increment 3
- Structure added: one seed skill node; its one responsibility is how a session uses the placed source index; the variation that justifies it is real now (four questions no seed node routes)

### Increment 6 — The installer's build and growth-audit's report
- Spec contracts: SPEC-0007/INSTALL_RUNS_THE_BUILD, SPEC-0007/GRAFT_REBUILDS_THE_CACHE, SPEC-0007/SOURCE_INDEX_IS_PLACED, SPEC-0007/GROWTH_AUDIT_PRINTS_THE_BUILD_REPORT
- Files touched: `install.sh` (after `write_seed_stamp` and before the `NEXT STEP` notices: `INSTALL_BUILD_HEAD`, the placed `build` run from `$PROJECT_DIR` by `python3 -I -B` with `INSTALL_BUILD_TIMEOUT` through Python's subprocess timeout, guarded under `set -euo pipefail`, stdout decoded with `errors="replace"`, its stdout lines indented in the `log` form only on exit 0 and its stderr never printed, `INSTALL_BUILD_FAILED` on any other outcome, the exit code untouched; the usage header names the step in one line), `manifest.json` (the `tools/source-index.py` description: "the installer runs its build as its last step and prints the report" in place of "the installer writes no cache"), `tools/growth-audit.py` (the report after the verdicts, run as `python3 -I -B`, stdout only on exit 0, never stderr, `source_index_report` empty on a failure; `GROWTH_REPORT_HEAD`, `GROWTH_REPORT_FAILED`, `GROWTH_REPORT_TIMEOUT`; `--json` `source_index_report`; nothing in `--plan` or `--agents`)
- Tests to write (RED): none here; increment 3 holds them
- Behavior added: every install that places files builds the index and prints the report; the report again at every grow and graft lint
- Gate: the installer, growth-audit, X430 and E15 cases green; `tests/test-full-install.sh`, `tests/test-install-placement.sh`, `tests/test-growth-audit.sh`, `tests/test-graft-tools.sh` and `seed-lint` (no new write site) green
- Rollback path: revert the commit
- Effort: medium-low
- Phase: GREEN
- Depends on: increment 3; its installer cases also need increment 4

### Increment 7 — Protocol, template and guide wiring
- Spec contracts: none; doctrine text, proved by the lints that already run
- Files touched: `protocols/graft.md` ("The installer is the hand that applies it": the install ends with the source-index build, which writes only the self-ignored cache; Phase 6: correct each `repo:` value the report names, one plant-relative path that exists or none; Phase 7 and the output format: a "Source index after the graft" section recording the apply install's report and what was done with each line, hints and fixes put to the owner as next steps, read on the stage from `graft-run-logs/install.log` and `coverage.txt`); `protocols/grow.md` (Phase 2's `build --json` stays; the delivery records the report of its last growth-audit run); `protocols/canonize.md` (a `repo-unresolved` record from `anchors --moved` is corrected in the same close-out); `tools/graft-run.py` (docstring steps 3 and 6 name the report in `install.log` and `coverage.txt`; no code); `skills/toolcraft/SKILL.md` and the catalog template `tools/index.md` under `templates/docs/` (one sentence each: the seed's placed tools are described by seed skills and need no catalog row; a plant may still write its own card); `documentation/source-index.md` ("The installer never writes it" becomes: the installer runs `build` as its last step and prints the report; deleting the directory stays safe)
- Tests to write (RED): none — doctrine text; proved by `seed-lint`, `graph-lint` on a fresh install and the route corpus
- Behavior added: graft, grow and canonize act on the report
- Gate: `tests/run.sh` green
- Rollback path: revert the commit
- Effort: low
- Phase: prose
- Depends on: increments 4, 5, 6

### Increment 8 — Verify and one measurement
- Spec contracts: every 8.1.2 contract
- Files touched: SPEC-0007 §10 statuses and status `implemented`; this plan's §10
- Tests to write (RED): none — verification
- Behavior added: none; the full gate, then an install into scratch copies of two plants (never the plants), the build time it prints and its findings recorded in §10, and the gate's wall time before and after the round
- Gate: `tests/run.sh` whole green; the measurement recorded
- Rollback path: none needed
- Effort: low
- Phase: prose
- Depends on: increment 7

No consolidation increment: the round adds eight cases to three existing suites, one per contract, and amends two.

## 10. Verification Plan
Covered by the seed's standard gate, `tests/run.sh`. One addition: increment 8 runs `install.sh` into scratch copies of two plants, a TypeScript plant and the plant with comma-list `repo:` values, and records the build time the install prints, its counts and findings, and the gate's wall time before and after the round here; it is a measurement, not a gate.

## 11. Risks and Mitigations
| Risk | Probability | Impact | Mitigation | Owner | Verification |
|---:|---:|---:|---|---|---|
| The skill's `load_when` also catches unrelated tasks and shifts the route corpus | 0.3 | 2 | the phrases name the four questions; `tests/graph-route-eval.sh` ratchets gate it | implementer | increment 5 gate |
| The test-name hints fire on a whole fixture tree and read as noise | 0.5 | 1 | counts and five paths only; one `exclude` key, even `[]`, ends the hint | architect | increment 8 measurement |
| Every install spends the build's time; a large monorepo install waits up to the bound | 0.5 | 1 | measured 0.06 s (empty) to 3.7 s (llama.cpp, 4,320 files); a graft spends about four builds; `INSTALL_BUILD_TIMEOUT` 120 s and fail-open; above the bound or `CACHE_MAX_BYTES` each query rebuilds and no setting narrows the inventory (§12 question 13) | implementer | increment 8 measurement |
| A test that installs into a Git fixture and compares the tree, the backups or the output now meets the cache or the report | 0.4 | 2 | the placement suites install into non-Git targets (`plant_base`, `case_recover`); the cache is self-ignored and outside `placed_files`' backups; X430 and E15 are amended at RED; G2's gate runs the suites that install into Git fixtures (`test-graft-tools.sh`, `test-prompt-hooks.sh`, `test-tool-corpus.sh`) | tester | increment 6 gate |
| An old `python3` on a plant host fails the build | 0.2 | 1 | `INSTALL_BUILD_FAILED` names the exit; the install completes | implementer | the failure arm |
| The owner vetoes the skill (question 1) | 0.2 | 3 | ADR-0030 lists the card design's extra contracts; the build report, installer and growth-audit increments stand either way | architect | the ruling |

## 12. Open Questions
| # | Question | Why it matters | Current assumption | How to resolve | Owner | Pinned by |
|---:|---|---|---|---|---|---|
| 1 | Resolved 2026-10-07: surface the tool through a seed skill; ADR-0030 accepted. The owner: "1 ok 2 ok 3 go" (item 1) | — | — | resolved | owner | SPEC-0007 SOURCE_INDEX_SKILL_ROUTES_ITS_FOUR_QUESTIONS |
| 2 | Resolved 2026-10-07: the installer runs the build. The owner: "ACTUALLY BUILD IT. a user cannot be expected to know that it needs to do things if it executes a graft/install/growth. the plant needs to be ready to go from te get-go after executing the protocols" | — | — | resolved | owner | SPEC-0007 INSTALL_RUNS_THE_BUILD |
| 3 | Resolved 2026-10-07: growth-audit runs the seed's `build` on the plant and prints the report as advice, never a verdict. The owner: "yes" | — | — | resolved | owner | SPEC-0007 GROWTH_AUDIT_PRINTS_THE_BUILD_REPORT |
| 4 | Settled, owner may veto: only the source index gets a seed skill now; `code-anchor.py`, `status-register.py`, `prose-lint.py` and the linters wait | scope | none now | veto | owner | — |
| 5 | Settled, owner may veto: a test-file name list (`test_*.py`, `*.spec.*` and the rest of `TEST_NAME_PATTERNS`) is used only for hints | a name is a guess | hints only | veto | owner | SPEC-0007 BUILD_NAMES_TESTS_OUTSIDE_THE_TEST_CLASS |
| 6 | Settled, owner may veto: the round ships as 8.1.2, as the owner set, though it adds a seed skill and changes what an install does | version label only | 8.1.2 | veto | owner | — |
| 7 | Settled, owner may veto: the seed-only user guides stay seed-only; the skill carries what a plant session needs | the guides describe the seed for its steward | unchanged | veto | owner | — |
| 8 | Resolved 2026-10-07: the ADR-0029 "Amendment, 8.1.2" is ratified, in place. The owner: "1 ok 2 ok 3 go" (item 2) | — | — | resolved | owner | SPEC-0007 INSTALL_RUNS_THE_BUILD |
| 9 | Resolved 2026-10-07: SPEC-0001 gains §2's line for the build, an And clause in `SINGLE_WRITER` and an Except clause in `IDENTICAL_RERUN_IS_INERT`, written as increment 2. The owner: "1 ok 2 ok 3 go" (item 3) | — | — | resolved | owner | SPEC-0001 IDENTICAL_RERUN_IS_INERT |
| 10 | Settled, owner may veto: every install that places files runs the build, not only the first; there is no flag to skip it | a re-install or graft can move the key; a skip flag is a second path | every install, no flag | veto | owner | SPEC-0007 INSTALL_RUNS_THE_BUILD |
| 11 | Settled, owner may veto: `graft-run.py` gets no code change; the report is in its `install.log` and `coverage.txt`, Phase 7's apply prints it in the plant, and graft.md says where to read it | a second reader of growth-audit's output in a tool whose output is the gate table | docstring only | veto | owner | — |
| 12 | Pending owner: when a task names a path a node owns, (a) the router adds phrase-tier hits of `origin: seed` skill nodes beside the `named_path` entries (a SPEC-0002 / ADR-0026 change, outside this slice), or (b) the claim narrows to path-free phrasings, the skill reaching the session through the host's native skill listing (`devils-advocate-8.1.2` 2) | the first tier that hits wins, so in a grown plant three of the four `SKILL_ROUTE_TASKS` load the owning node and not the skill | flagged assumption: (b), stated provisionally in SPEC-0007 §3, ADR-0030 and the owned-path arm of SOURCE_INDEX_SKILL_ROUTES_ITS_FOUR_QUESTIONS | owner rules (a) or (b) before RED | owner | SPEC-0007 SOURCE_INDEX_SKILL_ROUTES_ITS_FOUR_QUESTIONS |
| 13 | Pending owner: does an inventory-narrowing config key (for example `inventory_exclude`) belong in slice 3? (`devils-advocate-8.1.2` 6) | a plant above `CACHE_MAX_BYTES` (about 65k files, inferred) or past the 120 s bound rebuilds on each query, and `exclude` only narrows the test class | flagged assumption: no such key in this slice; SPEC-0007 §7 says so | owner rules before slice 3 | owner | SPEC-0007 §7 INSTALL_BUILD_FAILED, CACHE_WRITE_FAILED |
| 14 | Pending owner: should a config pattern (`exclude`, `always_run`, `global_inputs`) that matches no inventory file become a build hint? (`devils-advocate-8.1.2` 1c) | a typo in `always_run` makes the always-run set wrong with no record and no hint; the hint is cheap, in the same pass | flagged assumption: not reported; SPEC-0007 §3 and §6 "Build report" say so | owner rules before RED | owner | SPEC-0007 BUILD_NAMES_TESTS_OUTSIDE_THE_TEST_CLASS |

## 13. Done Criteria
- Every 8.1.2 row of SPEC-0007 §10 is green and `tests/run.sh` is green whole.
- In a fresh install, the four `SKILL_ROUTE_TASKS` load `skill.source-index`.
- A fresh install into a Git work tree ends with the build's report and a cache a following query reuses; one into a directory with no governed repository ends with the `no-repository` fix; both exit 0.
- The owner has ruled §12 questions 12 and 14 (before RED) and 13 (before slice 3), and the provisional text follows the rulings.
- The increment 8 measurement is recorded in §10.
- The release procedure's one documentation pass has run (`CHANGELOG.md`, the skill count in `README.md` and the reference pages, `documentation/source-index.md`).

## 14. Recommended Next Step
Updated 2026-10-07 by `architect-8.1.2d`: put §12 questions 12 to 14 to the owner; then product re-reads SPEC-0007 §3 and §9 (AC-23 under option (b), AC-26 for `repository-unnamed`, the readiness line before AC-23) and SPEC-0001 §3 and AC-3 (the governed-repository scope); tester signs §10 (the new arms, the `REPOSITORY_UNNAMED` row, the X459 probe); then RED (increment 3). The earlier step below is done.

Brief product (SPEC-0007 §3 and §9, and SPEC-0001 §3 and AC-3, whose "does nothing and says nothing" and "zero churn" now meet the build's report and cache), tester (SPEC-0007 §10; SPEC-0001's 2026-10-07 text, which changes no row), security and devils-advocate on SPEC-0007 "Surfacing (8.1.2)"; then RED (increment 3).

## 15. Changelog
- 2026-10-07: created by `architect-8.1.2` from the owner's request ("go do it. update graft and install/growth"); SPEC-0007 8.1.2 slice and ADR-0030 written; RED waits for §12 questions 1 to 3.
- 2026-10-07: rewritten by `architect-8.1.2b` on the owner's rulings of questions 2 ("ACTUALLY BUILD IT") and 3 ("yes"): the installer runs the placed `build` as its last step on every install and graft apply, fail-open and bounded; `build` prints a fix under each record; question 1 taken as yes pending ADR-0030; questions 8 (ADR-0029 amendment) and 9 (SPEC-0001 amendment) added; increments renumbered 1 to 8, with the SPEC-0001 amendment as increment 2.
- 2026-10-07: the owner ruled §12 questions 1, 8 and 9 ("1 ok 2 ok 3 go"): ADR-0030 accepted, the ADR-0029 amendment ratified, go for SPEC-0001; `architect-8.1.2c` wrote increment 2 (SPEC-0001 §2, `SINGLE_WRITER` And, `IDENTICAL_RERUN_IS_INERT` Except, §12 entry; no §10 row changed), set both ADRs' records and the index, and added the §6 row.
- 2026-10-07: `architect-8.1.2d` applied the `security-8.1.2` review (S1 the isolated run `python3 -I -B`, S2 stdout only on exit 0 and never stderr, S3 the guarded run, S4 the skill's limit line; arms A1 to A4; security signed in SPEC-0007 §0) and the `devils-advocate-8.1.2` changes that need no owner ruling (1a `repository-unnamed`, 1b the narrowed readiness claim, 3 the governed-repository scope in SPEC-0001 and SPEC-0007, 4 the measured cost and four builds per graft, 5 the reordered `no-repository` fix, 6 the recovery line, 7 the case-sensitivity probe, 11 the `build` `ACTION_LINE`); ADR-0029 and ADR-0030 revised in place with a dated note; §0, §2, §4, §6 (three rows added, one widened), §8, §9 increments 3 to 6, §11, §13 and §14 follow; §12 questions 12 to 14 added, pending owner.
