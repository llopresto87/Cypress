---
status: active
status_date: 2026-10-09
owner: seed-installer
status_evidence: tests/test-install-placement.sh, tests/test-plant-state.sh, tests/test-install-kernel-modes.sh, tests/test-install-adoption.sh, tests/test-full-install.sh, tests/test-seed-lint.sh, tests/test-graft-tools.sh, tests/test_corpus_match.py (every §10 contract row green but the two 8.1.2 graft-finding rows, CHECK_FLAGS_RETIRED_GRAPH_NODE (M13 case_retired_flag, graph-node arm) and GRAFT_RUN_TIES_LINT_ERRORS_TO_RETIRED_NODES (X469), `red` since their RED of 2026-10-09 until GREEN, plan grill-8.1.2 increment 12; HARVEST_CANDIDATE_FORM_IS_PLACED included, held by S14 in case_plan_records and proved by mutation, §12's second entry of 2026-10-05 on the harvest-candidate form; all wired into tests/run.sh)
---

# SPEC-0001: install placement

## 0. Metadata

- **Identifier:** SPEC-0001-install-placement
- **Status:** see frontmatter (single home)
- **Sign-offs:** product [x] · architect [x] · tester [x]
  Each role signed the 8.0.0 contracts (§12) on its own read-only review of
  2026-10-04, held with increment 10's RED over JURISDICTION_RESOLVED_ONCE,
  the RED the promotion to `active` lands with (`verify.status-evidence`).
  No condition blocks. Product asked §3 to state the jurisdiction outcome,
  done with the promotion, and named three gaps in
  RECORDED_EXPERTISE_PAGE_WITHDRAWN for increment 13: the exit code of a
  plain install after its WARNING, its overlap with
  EXPERTISE_SURVIVES_SILENCE (a withdrawn page cannot be placed again), and
  AC-23's silence on it. The architect named two: a listed id whose
  destination a different recorded id already owns is not refused by the
  preflight (increment 13), and CHECK_EXECUTES_EACH_WIRED_HOOK fails a hook
  that prints nothing while SPEC-0003 lets the status hook stay silent when
  its register fails (increment 11). The tester signed with no condition.
  Increment 11 answered the architect's second condition in the contract
  text rather than by an exception: on the check envelope the status hook
  is never silent, because SPEC-0003 STATUS_HOOK_RESETS_WITHOUT_REGISTER and
  STATUS_HOOK_ANCHOR_FAILURE_FAILS_TOWARD_INCLUSION end its output with the
  anchor line or its not-checked line when the register is absent, fails or
  prints nothing. The silence SPEC-0003 allows is the summary's, not the
  hook's, so "prints nothing" can only name a broken script.
  Increment 13 answered the conditions owed to it in the contract text.
  RECORDED_EXPERTISE_PAGE_WITHDRAWN now states that a plain install exits 0
  after its WARNING, that it takes precedence over EXPERTISE_SURVIVES_SILENCE
  (a withdrawn page the plant deleted is not placed again, and its entry is
  kept), and that a listed id the seed withdrew is refused by the preflight;
  AC-22 and AC-23 map to it. UNKNOWN_EXPERTISE_ID_REFUSED_BEFORE_WRITING's
  Given gains the architect's case, a listed id whose destination a different
  recorded id already owns, and the preflight refuses it before the first
  write.
  The contracts and texts that came after those ticks were reviewed at the
  8.0.0 tip (increment 15), each role on its own read-only review of
  2026-10-04: CHECK_FLAGS_RETIRED_HARNESS_ENTRY and
  CHECK_FLAGS_ORPHAN_HARNESS_ENTRY (increment 12), the increment-13 contract
  text above, and the matcher rules §6 gained in increment 13's follow-up.
  Sign-offs for them: product [x] · architect [x] · tester [x].
  Product signed, and asked AC-26 to say that a flag alone does not fail
  `--check`, which it now does. The architect signed with no blocking
  condition and left notes for a later round: graft-audit counts a backup of
  a live ORPHAN entry `ORPHAN` rather than `UNMAPPED`, which §4 does not
  state; an `origin: seed` harness entry with no node whose name the seed
  still ships is flagged neither way; a recorded withdrawn id also warns on
  a list run, where RECORDED_EXPERTISE_PAGE_WITHDRAWN names only the silent
  run; and the matcher also reads `Dockerfile.*` and `*.dockerfile`, while a
  registry-less `dotnet/` image is not read as dotnet. The tester blocked
  first on three gaps, each closed with a case before the tick: M13 gains an
  `origin: seed` harness entry with no graph node, and M13 and M14 assert
  graft-audit's exit code against the clean copy; M17 gains a skill id that
  lands on a seed skill node and a library id that lands on a scaffold leaf;
  and the matcher cases gain a `Containerfile`, a `dotnet/` image and a
  manifest under each agent host's directory.
  The matcher increment of 2026-10-05 came after every tick above. It adds
  LANGUAGE_DECLARATION_PROPOSES_ITS_PAGE, OWN_PACKAGE_LIST_PROPOSES_ITS_PAGE,
  CITED_PACKAGE_PROPOSES_NOTHING and PACKAGELESS_PAGE_PROPOSED_BY_ITS_TRIGGER,
  the failure OWN_PACKAGE_NAMED_ONLY_IN_PROSE, AC-27 and AC-28, and the §6
  rules they rest on (the own-package list among them). The architect wrote
  them and signs that §4, §6 and §7 cohere. The tester wrote the five cases
  from the brief, before these contracts existed, then reviewed them, added
  the two subtests and the contract names the architect asked for, and
  signed. Product reviewed §3 and §9 on 2026-10-05 and held its tick on
  three points, answered in the text: AC-28 claimed that a cited package
  never proposes a page, while CITED_PACKAGE_PROPOSES_NOTHING keeps an
  Except for `maven` pages, and it now states that exception and its
  recovery; AC-27 stated no bound, and it now binds to the §6 rows and holds
  that a build with no Java level does not bring in `language/java`; and §3
  now names the Maven exception and how the owner recovers a page no rule
  reaches. Product re-reads before it ticks.
  Sign-offs for them: product [x] · architect [x] · tester [x].
  HARVEST_CANDIDATE_FORM_IS_PLACED (2026-10-05) came after every tick above.
  The architect wrote it. The tester wrote S14 in case_plan_records against
  it and signed. Product held its tick until §3 named the form and AC-29
  mapped to the contract, then re-read and signed.
  Sign-offs for it: product [x] · architect [x] · tester [x]. Product signed:
  the form is placed byte-identical, never clobbered or backed up, and AC-29
  states the outcome the owner checks, the one S14 asserts.
  The 8.1.2 amendment (2026-10-07) came after every tick above: §2's line for
  the source-index build, SINGLE_WRITER's And clause for it and
  IDENTICAL_RERUN_IS_INERT's Except clause for its cache. The architect wrote
  it on the owner's go ("3 go", 2026-10-07). It changes no test and no §10
  row; product and tester owe their review of the text, and product owns
  whether §3 and AC-3 name the cache.
  Product reviewed the amendment on 2026-10-07 and reworded §3 and AC-3 to
  match it: a re-run over an unchanged project leaves the installer's own
  files untouched and makes no backup, still prints the build report, and
  refreshes the self-ignored cache in a plant with at least one governed
  repository, the one exception.
  Sign-off for it: product [x] · tester [x] (2026-10-09, `tester-R3-8.1.2`:
  the And and Except clauses are observable as written; the cache bytes are
  held by SPEC-0007 X467 and BUILD_IS_DETERMINISTIC, and M3's target has no
  governed repository, so its Then holds there without exception; no test
  changes).
  The 8.1.2 graft-finding contracts (2026-10-09) came after every tick above:
  CHECK_FLAGS_RETIRED_GRAPH_NODE and GRAFT_RUN_TIES_LINT_ERRORS_TO_RETIRED_NODES,
  with §2's line and §6 "Retired graph nodes". The architect wrote them
  (`architect-8.1.2j`) from the test graft of a plant copy, where a retired
  `origin: seed` protocol node failed graph-lint with no flag naming it.
  Product owes §3 and AC-26, which name only agents and skills; the tester
  owes the two §10 rows.
  Sign-offs for them: product [x] · architect [x] · tester [x] (2026-10-09,
  `tester-R3-8.1.2`: both §10 rows written and red, each for the missing
  behaviour: M13 case_retired_flag's graph-node arm, where graft-audit names
  no `RETIRED docs/graph/protocols/toolcraft.md`, and X469
  case_run_ties_lint_errors_to_retired_nodes, where the routes row is BLOCK
  over the stage copy's one duplicate fact-key error naming
  `protocol.toolcraft` but names no RETIRED protocol). Product
  (`product-8.1.2e`, 2026-10-09) signed: §3 now names the retired seed page,
  the graft run's explanation of the graph-lint errors it causes, and the
  steward's deletion by name after the owner's named confirmation; AC-26
  maps both contracts in plain words.
  Before 8.0.0 this spec was `back-written` and carried no sign-off, because
  there was no RED for a promotion to land with. An earlier draft asserted
  signatures dated to a RED that never landed; that was fabricated to satisfy
  a linter and is recorded here so the correction is not silently absorbed.
  `active` was then used with a long argument for why it was honest, which
  was an argument for `back-written` by another name while the right value
  sat in the schema. The ticks above are the first real ones.

- **Owner:** seed-installer
- **Date:** 2026-09-13
- **Last reviewed:** 2026-10-09
- **Related grill section:** docs/plans/grill-7.15.0-remediation.md §3, §5; docs/plans/grill-8.0.0-wave-a.md §9 (the 8.0.0 contracts); the matcher increment of 2026-10-05 is its increment 17; docs/plans/grill-8.1.2-tool-surfacing.md increment 2 (the source-index build) and increments 11 and 12 (the retired seed graph nodes)
- **Related ADRs:** adr-0003-enforcement-layering-honesty, adr-0009-host-support-tiers, adr-0013-harness-memory-is-not-a-home, adr-0014-graft-reconciles-every-graph-engine, adr-0016-stamp-carries-keys-it-does-not-own, adr-0017-pre-growth-pointers-leave-the-kernel, adr-0018-code-fact-freshness-anchor (the last three proposed), adr-0021-seed-only-procedures-stay-home, adr-0022-the-plant-model-map (both proposed), adr-0024-one-hook-core-per-session-residency (proposed), adr-0029-source-index-is-derived-scratch (its 8.1.2 amendment: the install runs the build)
- **Supersedes:** —
- **Superseded by:** —

## 1. Summary

What `install.sh` is allowed to do to a target directory. The seed's kernel
§3.1 says code without a spec is in remediation mode, and the installer — the
one component that writes into somebody else's repository — had no spec at all.
This contracts the properties that make an install safe to run twice, safe to
run over a customized plant, and safe to audit afterwards: every write is
recoverable, no write escapes the target, an identical re-run changes nothing,
and the record the installer keeps cannot contradict the filesystem. It also
contracts the one write the seed's graft tools make into a plant's placed
files, the reconciliation of the graph engines the installer placed
add-if-missing, and the audit that says whether each engine is current.
Since 8.0.0 it also contracts the selective placement of corpus knowledge:
the installer proposes the corpus pages a plant's manifests match, places
only the list the owner confirms, records it, and refreshes it on a later
install without replacing a page the plant edited or owns.

## 2. Scope

- **In scope:**
  - every byte `install.sh` writes into `--project-dir`
  - the backup contract and what `--force` does and does not suppress
  - copy vs symlink placement, including the root kernel
  - `.cypress/seed.json` as the plant's persistent record
  - the legal corpus as a whole-or-nothing artifact
  - preflight refusal before any write
  - which hosts `all` installs, and the deprecation notice a frozen host prints
  - the graph-engine reconciliation `tools/graft-graph-engine.py` performs on a
    plant's placed engines (`graph-lint.py`, `spec-lint.py`, `grill-lint.py`),
    and the engine-currency check of `tools/graft-audit.py --engine`
    (adr-0014)
  - the list of re-created nodes written to `.cypress/recreated-nodes.txt`
  - the keys of `.cypress/seed.json` that the installer does not own
    (adr-0016)
  - the placement of `docs/graph/code-anchor.py` (adr-0018)
  - the plant's model map, `docs/graph/models.md`: its placement, the one
    line of each opencode agent projection the installer writes from it, and
    the `--check` that compares those projections with the map (adr-0022)
  - the seed-only files the installer never places, and the tools it does
    place, held against `manifest.json` (adr-0021)
  - the selective placement of corpus pages (`--expertise`): the proposal
    `tools/corpus-match.py` prints from the plant's manifests, the placement
    of a confirmed list of `library-corpus/`, `skill-corpus/` and
    `tool-corpus/` pages, the stamp's `expertise` key, the refresh on a later
    install, and the `--check` of the recorded pages
  - the one shape of a corpus page the matcher reads, the own-package list
    of a library page's `## What it is` (§6), and the files that propose a
    `language`, `platform` or `cli` page, which no lockfile declares
  - the one resolution of the legal jurisdiction that the national-layer
    report, the stamp and the closing banner share
  - the execution of each wired context hook under `--check`
  - the `RETIRED` and `ORPHAN` flags: the harness entries and the retired
    seed graph nodes `--check` and `tools/graft-audit.py` name, and how
    `tools/graft-run.py`'s `graft.gate.routes` row reports them and the
    graph-lint errors a retired node causes
  - the one write of an install that is not the installer's: the cache under
    `.cypress/source-index/` that the placed
    `docs/graph/source-index.py build` writes when the install runs it as its
    last step. This spec owns only where that write stands against its own
    rules: outside SINGLE_WRITER's census, and the one exception to
    IDENTICAL_RERUN_IS_INERT (adr-0029, amendment 8.1.2)
- **Out of scope:**
  - the anchor file `docs/graph/code-anchor.py` writes: SPEC-0003 owns it,
    because the session-start hooks read it and canonize writes it; the
    installer never writes it
  - the source-index build itself: when the install runs it, its report, its
    bound and its failure, and the cache document it writes. SPEC-0007 owns
    them (`INSTALL_RUNS_THE_BUILD`, `INSTALL_BUILD_FAILED`, §6 "Cache
    document")
  - what the placed files MEAN (the graph schema, the kernel's content)
  - `grow`, `graft` and `harvest`, which are user-sovereign flows over an
    already-installed plant, apart from the engine reconciliation above
  - the seed's own repository layout
  - how Prime Agent reads the model map (overlay prose, brief-enforced), and
    whether a host's model catalog carries a selector the map names
  - what a corpus page says (each corpus's `README.md` owns its admission
    bar), and the merge of a plant-edited or plant-owned page with the
    corpus's newer layer, which graft Phase 4 performs with understanding
  - removing an id from the `expertise` record (§11)

## 3. User-facing behavior

An owner points the installer at a project and names one or more harnesses. The
installer either completes, or refuses before writing anything and says which
path is in the way. Running it again over an unchanged project rewrites none of the
installer's own files, makes no backup and names none as replaced. It still
ends with the source-index build report, on every run. In a project with at
least one Git repository the build reads, that build also refreshes its
cache under `.cypress/source-index/`, a scratch
folder that ignores itself in Git; when nothing in the project moved, the
new cache holds the same bytes as the old one. That cache is the only thing a
re-run writes, and in a project with no such repository the build writes nothing. Running it over a project someone has edited replaces the seed's
own files, leaves a timestamped copy of every body it replaced, and names them.
Nothing outside the named project directory is ever modified.
A fresh plant also gets a blank harvest-candidate form under
`docs/graph/plans/`. Canonize starts the plant's own record from it. No
install creates that record. After the plant writes the record or edits the
form, a re-install leaves both as they are and keeps no copy of either.
`all` installs the maintained hosts: claude-code, opencode and prime-agent. A
frozen host (codex, github-copilot) still installs when it is named, and says
that it is deprecated. `all --check` still checks the Copilot views of a plant
whose record carries github-copilot, because checking writes nothing, and it
checks the opencode agent projections of a plant whose record carries opencode,
because those carry a `model:` line written from the plant's model map.

An owner who wants the seed's knowledge of a stack runs the installer with
`--expertise propose` and reads the corpus pages the project's manifests
match; nothing is written. Running it again with `--expertise` and the ids
the owner keeps places those pages in the plant's graph, each marked with the
seed version it came from, and records them. The proposal reaches a language,
a platform or a tool page through the file in the project that declares or
drives it, and a library page through each package the page lists as its
own. A package a page only mentions, such as its runtime dependency, does
not bring that page into the proposal, with one exception for now: a Maven
page is still brought in by a coordinate its opening section names, even one
it only mentions, and the owner leaves that page out of the list (§11). A
page that no rule reaches, such as a tool the project only calls from a
script or Java whose level a parent build outside the project sets, is
placed when the owner lists its id. Every later install refreshes
the pages nobody edited and names each page it left alone. `--check` also
runs each wired context hook once, so a hook whose script is gone is found by
the check and not by a session. It also names each agent or skill in a harness
directory that has no home in the plant's graph: `RETIRED` for one the seed
does not ship, `ORPHAN` for one the plant authored there. It names in the same way, as
`RETIRED`, a seed page in the plant's `docs/graph/protocols/` or
`docs/graph/method/` that the seed no longer ships, such as a protocol the
seed folded into a skill. It deletes none of them, and a flag alone fails
nothing. A graft run names those outdated seed pages in its routes row. When
graph-lint fails because such a page repeats a fact a page the seed ships
owns, the row also says how many of the errors that page causes, names it, and
says that each error clears when the steward deletes the page by name. The
graft still blocks on those errors and deletes nothing; removing the page is
the steward's act, after the owner confirms that page by name.
A plant whose record names its national jurisdiction keeps it on a re-install
that passes no flag, and the run names that code instead of calling the
jurisdiction undecided.

## 4. Functional contracts

### Contract: SINGLE_WRITER
- **Given:** any destination inside the target
- **When:** the installer places content there
- **Then:** the write passes through one of four named operations —
  `place_file`, `place_generated`, `place_if_missing`, `place_state`
- **And:** no adapter has a private placement path
- **Except:** 11 writes into the target are authored rather than placed, and are
  recorded here because a contract with unnamed exceptions is a contract that is
  simply false. `record_instruction_migration` (4) moves a symlink off the note
  path, moves a HARD LINK off it for the same reason — `cat >` and `>>` write
  the inode, so a note hardlinked to a file outside the target had the ledger
  appended into that outside file, and `-L` is false for a hardlink — writes the
  note's header, and appends one ledger row per replaced kernel
  — there is no seed-side source file to place, because the body is generated
  from the kernel that was replaced, and none of the four operations expresses
  an append. `place_kernel` (4) backs up the sibling kernel, removes it, lays a
  relative project-local link by hand — `place_file` cannot express a link that
  points inside the target rather than into the seed — and falls back to `cp`
  where the filesystem refused the link. `fill_plant_facts` (1) rewrites
  `docs/graph/index.md` in place through an embedded python heredoc, because the
  plant's facts are merged into a file the plant owns rather than copied over it.
  `ensure_dir` (1) creates a destination directory before a placer writes into
  it — the one write every placer depends on, and a directory rather than
  content, but a write into the target all the same. It was invisible twice
  over: `mkdir` was not a verb the derivation looked for, and `ensure_dir` was
  exempted from the sweep wholesale. `retire_copilot_hook_duplicates` (1) moves
  a `.github/hooks/` file that `.claude/settings.json` now supersedes to a
  timestamped backup beside itself: a removal, which none of the four operations
  expresses, and there is no seed source to place. The Copilot installer already
  skipped those hooks when `settings.json` was present, but that guard ran in
  one direction only — adopting Copilot first and Claude Code second left both
  sets wired, and VS Code reads both, so every hook fired twice.
- **And:** that list is DERIVED from `install.sh` on every run rather than read
  from this page: `seed-lint`'s `check_install_write_sites()` attributes every
  raw write to the function that holds it and compares the set outside the four
  operations against `INSTALL_WRITE_EXCEPTIONS`, **by count as well as by
  shape** — and the four placers are counted too, in `PLACER_WRITES`, rather
  than exempted wholesale. They were exempted wholesale until a reviewer put one
  `case "$dest" in */.github/hooks/*) cat "$src" > "$dest"; return ;; esac`
  inside `place_file` and watched the full gate exit 0 while an install
  destroyed a file outside `--project-dir`. The count above is likewise summed
  from the rows that declare themselves target-side, not written down beside
  them: a row that declares neither side is refused, because "undeclared" used
  to mean "temp, therefore harmless".
- **And:** a new bypass fails because it is absent from that table; a second
  write of an already-excepted shape fails because the count moved; a retired
  one fails because the table is then stale; and the number quoted in the
  sentence above fails if it stops matching the table.
- **And:** the derivation reads shell with regexes, so it is bounded and says
  so. It sees a write behind `if`/`&&`/`;`, a one-line function body, a
  `function name {` definition, and a write performed by an embedded python
  heredoc — the last of which is how `fill_plant_facts` writes, and was
  invisible for as long as the check existed without it. It does NOT see a
  write under a non-python inline interpreter, or under `eval`. Two shapes this
  list used to name — a write inside a command substitution, and a write on the
  right of a pipe — were re-tested during the conformance review and are in fact
  CAUGHT (`_o=$(cp a b)` and `printf x | tee "$dest"` are both found by segment
  splitting), so the list was overstated as well as mislocated: it said these
  residuals were recorded in `tools/gate-registry.py`, and they were not there at
  all. They are recorded in the registry's `seed-lint.py` row now.
- **And:** the source-index build that ends an install (SPEC-0007
  `INSTALL_RUNS_THE_BUILD`) is a tool run of a placed file, not an installer
  write: `install.sh` runs `python3 -I -B docs/graph/source-index.py build`
  from the target (SPEC-0007 §6 "Build report"), and the cache that run writes under `.cypress/source-index/` is the
  tool's own atomic write under adr-0029. The run adds no raw write to
  `install.sh`, so it is neither a placer write nor a row of
  `INSTALL_WRITE_EXCEPTIONS`, and the count of 11 above is unchanged.

### Contract: BACKUP_BEFORE_REPLACE
- **Given:** a destination that exists and differs from what is being placed
- **When:** the installer replaces it
- **Then:** the previous body is recoverable at `<path>.bak-<timestamp>`
- **And:** the two exceptions are `.cypress/seed.json` and
  `.cypress/recreated-nodes.txt`, both written by `place_state`: installer-owned
  derived state, never authored by hand, that would otherwise accrue one backup
  per run

### Contract: FORCE_SUPPRESSES_WARNING_NOT_BACKUP
- **Given:** `--force`
- **When:** a differing destination is replaced
- **Then:** the per-file warning is suppressed and the backup is still made
- **And:** no flag exists that replaces a file without a recovery copy

### Contract: SYMLINK_IS_REPLACED_NOT_FOLLOWED
- **Given:** a destination that is a symlink to a file outside the target
- **When:** the installer places content at that destination
- **Then:** the link object is moved aside or replaced
- **And:** the referent outside the target is unchanged

### Contract: IDENTICAL_RERUN_IS_INERT
- **Given:** a plant nobody has modified since the last install
- **When:** the same install command runs again
- **Then:** no file is rewritten and no `.bak-*` is created
- **Except:** the derived cache under `.cypress/source-index/`, which the
  install's build (SPEC-0007 `INSTALL_RUNS_THE_BUILD`) replaces through the
  tool's own atomic write on every install into a plant with at least one
  governed repository (the plant root when it is a Git work tree, or a
  nested work tree a node's `repo:` names). When nothing
  moved, the new cache holds the same bytes as the old one (SPEC-0007
  `BUILD_IS_DETERMINISTIC`), and no `.bak-*` is made for it, because the
  installer neither places nor backs up a cache file. Over a target with no
  governed repository the build writes nothing, so the Then holds there
  without exception

### Contract: EVERY_BACKUP_IS_CLASSIFIABLE
- **Given:** any backup the installer produced
- **When:** `tools/graft-audit.py` runs over the plant
- **Then:** the backup classifies as identical, delta, customized, generated, or
  a named exclusion — never `UNMAPPED`
- **And:** an unclassifiable backup makes the audit exit non-zero rather than
  report "clean"

### Contract: SYMLINK_MODE_IS_UNIFORM
- **Given:** `--symlink`
- **When:** the install completes
- **Then:** every placed file is a symlink, except generated content and
  add-if-missing plant-owned files, which have no seed original to point at
- **And:** the root kernel is a link, so a seed kernel change reaches the plant
  without reinstalling

### Contract: COPY_MODE_ISOLATES
- **Given:** `--copy` (the default)
- **When:** the seed's kernel changes afterwards
- **Then:** the installed plant is unaffected until it is reinstalled

### Contract: ONE_KERNEL_BODY
- **Given:** a plant running more than one harness
- **When:** the install completes, in any adapter order
- **Then:** exactly one of `CLAUDE.md` / `AGENTS.md` is a real file and the other
  is a project-local relative symlink to it
- **And:** both resolve to byte-identical content

### Contract: DECISIONS_SURVIVE_SILENCE
- **Given:** a recorded owner decision in `.cypress/seed.json`
- **When:** a later install passes no flag for it
- **Then:** the recorded value is preserved
- **And:** only `undecided` is ever overwritten by silence

### Contract: ADAPTERS_ACCUMULATE
- **Given:** a plant already carrying one or more adapters
- **When:** another adapter is installed
- **Then:** the recorded adapter set is the union, and `agent_projections` is
  derived from it rather than maintained separately

### Contract: RECORD_AGREES_WITH_DISK
- **Note (corrected):** the inheritance re-check covered only the `yes`
  direction, so the record could say `legal_corpus: no` over statutes on disk —
  two ordinary commands, exit 0, no warning — while `agent.legal` answers from
  the corpus rather than from the stamp. The `no` direction now refuses the same
  way the explicit flag always did. Separately, the closing banner gated on flag
  SILENCE rather than on the resolved value, so a plant recording `no` was told
  its own file said `undecided`.
- **Given:** an installed legal corpus
- **When:** an install would record `legal_corpus: no`
- **Then:** the install is refused, naming both ways out
- **And:** neither the corpus nor the record is changed by the refusal

### Contract: CORPUS_IS_WHOLE_OR_ABSENT
- **Given:** `--legal-corpus yes`
- **When:** placement completes
- **Then:** the plant carries **no fewer than** every page the seed ships,
  counting pages and not backups. A shortfall is refused; a surplus is the
  plant's own ingest, is named in the log, and is not a reason to refuse.
- **Note (corrected):** this `Then` read "the number of corpus pages in the
  plant EQUALS the number in the seed", and equality is the wrong test. A plant
  that did what the installer's own notice tells it to do — run a
  research-scout ingest and land its national statute under
  `docs/graph/legal/corpus/` — got `legal corpus placed partially (17 of 16
  pages)` and could never install again. The code was corrected to `-lt` first
  and this sentence was left asserting the falsified version, four lines below
  the note recording the correction; the cited test asserted `-eq` as well.

### Contract: PREFLIGHT_REFUSES_BEFORE_WRITING
- **Given:** a target where a directory the preflight ENUMERATES already exists
  as a regular file, is not writable, or is a symlink leaving the target
- **When:** the installer runs
- **Then:** it exits non-zero naming the offending path, and the target is
  unchanged
- **And:** the failure is the tool's own message, not a raw shell error
- **Except:** a directory the preflight does not enumerate. The `Given` above
  read "a needed directory" with no qualifier, and that was false by 239 paths:
  a regular file at `.claude/skills/library-wiki` — a per-skill leaf the
  preflight does not reach — refuses only when `ensure_dir` meets it, after 239
  paths are already written, and a variant of the same case replaces the
  project's own `CLAUDE.md` and THEN refuses. `install.sh`'s `ensure_dir` header comment documents this
  honestly as "the preflight is the early warning, and this is the floor
  underneath it"; the contract asserted the opposite. What the preflight DOES
  enumerate is: `adapter_dirs()` for every selected tool, every directory that
  already exists beneath the trees the installer writes
  (`PREFLIGHT_SCOPED_TO_WRITTEN_TREES`), and every existing symlink beneath those
  trees. The last two are walked rather than listed, so they do not depend on
  anyone remembering to add a path.

### Contract: PREFLIGHT_SCOPED_TO_WRITTEN_TREES
- **Given:** a target that holds unwritable directories, or a directory symlink
  leaving the target, in a tree the installer never writes: `node_modules/`,
  `.next/`, a database volume, a nested checkout, `test-results/`. Docker builds
  and test runs leave such trees, often owned by root.
- **When:** the installer runs
- **Then:** it installs, and it does not open, change or refuse over those trees
- **And:** the deep walks for an unwritable directory and for an escaping
  symlink cover only the trees a run writes: `docs/graph`, `.cypress`, each
  selected adapter's own top directory, and the four `.github` subdirectories
  the Copilot adapter writes. The roots come from `adapter_dirs()`, so a new
  adapter is covered by its own entry.
- **Except:** none inside a written tree. A read-only directory or an escaping
  symlink under `docs/graph`, `.cypress` or an adapter directory still refuses
  before the first byte (`PREFLIGHT_REFUSES_BEFORE_WRITING`,
  `SYMLINK_IS_REPLACED_NOT_FOLLOWED`).

### Contract: ALL_EXCLUDES_LEGACY_HOSTS
- **Given:** an empty target
- **When:** `install.sh all` runs
- **Then:** `.claude/`, `.opencode/` and `.prime/agent/` exist, and `.codex/` and
  `.github/` do not
- **And:** the stamp's `tools` is exactly `claude-code opencode prime-agent`

### Contract: LEGACY_INSTALL_PRINTS_DEPRECATED
- **Given:** an empty target
- **When:** `install.sh codex` or `install.sh github-copilot` runs
- **Then:** stderr carries exactly one `DEPRECATED` line, naming that tool and
  ADR-0009
- **And:** `install.sh opencode` prints no such line

### Contract: LEGACY_INSTALL_STILL_SUCCEEDS
- **Given:** an empty target
- **When:** a frozen host is named
- **Then:** the install exits 0 and places that host's destinations as 7.26.0 did
- **And:** `codex --print-config` keeps the notice off stdout, which carries
  config a user pastes, and still prints it on stderr

### Contract: ALL_NAMES_SKIPPED_FROZEN_HOSTS
- **Given:** a plant whose stamp records `codex`
- **When:** `install.sh all` runs
- **Then:** stderr names `codex` as not refreshed, together with the command that
  refreshes it, `install.sh all codex`
- **And:** `.codex/` is byte-identical before and after, and the stamp still
  lists `codex` (ADAPTERS_ACCUMULATE)

### Contract: CHECK_WITHOUT_COPILOT_SAYS_SO
- **Given:** a target whose record carries neither github-copilot nor
  opencode, the two hosts whose views `--check` can compare
- **When:** `install.sh all --check` runs
- **Then:** it exits 0 and prints that no generated views are in scope
- **And:** silence is the failure, because a CI job reading only the exit code
  would take it for "in sync"

### Contract: ALL_CHECK_INCLUDES_RECORDED_COPILOT
- **Given:** a plant whose `.cypress/seed.json` records github-copilot
- **When:** `install.sh all --check` runs
- **Then:** the Copilot views are checked as `install.sh github-copilot --check`
  checks them: in sync, it exits 0 and reports them up to date; drifted, it
  exits non-zero and names them STALE
- **And:** the not-refreshed warning of FROZEN_PROJECTION_LEFT_STALE does not
  fire for github-copilot, which this run checks. The DEPRECATED notice does
  fire, once, because the run acts on a frozen host, the same as a `--check`
  that names it

### Contract: HOST_TIERS_AGREE
- **Given:** the tier arrays in `install.sh` (the one home of the assignment)
- **When:** `seed-lint` runs
- **Then:** it fails, naming `install.sh`, when a host sits in two tiers, or
  when `all` expands to anything but the first-class and supported hosts
- **And:** it fails, naming `install.sh`, when the three arrays together are not
  exactly the labels of the adapter dispatch `case "$tool"` block, whatever
  shape an arm's command takes, or when a label there is not a bare tool name
- **And:** it fails, naming `install.sh`, when the argument parser's
  `case "$1"` arms that append to `TOOLS` accept anything but the three
  arrays' hosts plus `all`
- **And:** it fails, naming the suite, when the `EVERY_HOST` literal in
  `tests/test-full-install.sh`, `tests/test-install-placement.sh` or
  `tests/test-unified-graph-install.sh` names a different set of tools than
  the dispatch installs
- **And:** the unmutated tree passes

### Contract: SESSION_RECORD_FORM_IS_PLACED
- **Given:** a fresh target directory
- **When:** `install.sh claude-code --project-dir <target>` runs
- **Then:** `docs/graph/plans/sessions/_session-record.template.md` exists
  and is byte-identical to the seed's
  `templates/docs/plans/sessions/_session-record.template.md`, placed by
  `place_docs_skeleton`'s existing `templates/docs/**` walk with
  `place_if_missing`, so `SINGLE_WRITER`'s census is unchanged
- **And:** after the plant writes its own record in
  `docs/graph/plans/sessions/` and edits the placed form, `install.sh all
  --project-dir <target>` leaves both files byte-identical and writes no
  backup beside either

### Contract: HARVEST_CANDIDATE_FORM_IS_PLACED
The harvest-candidate form is a seed-shipped blank form, like the
session-record form, and is placed rather than held back. Three readers need
it at its placed path: `canonize.harvest-candidates` creates the plant's
`docs/graph/plans/harvest-candidates.md` from
`docs/graph/plans/_harvest-candidates.template.md` when absent; graft's
Phase 8 hands KEEP-PLANT divergences back as rows of that record; and
`graft.gate.rootstock` names the placed form as an expected new leaf under
`plans/`, not a breach. Its leading underscore keeps it out of
`graft-audit.py --unfilled`, which skips `_`-prefixed and `.template.md`
leaves, so a fresh plant reports no unfilled scaffold for it. The existing
walk places it, so it adds no write site and `SINGLE_WRITER`'s census is
unchanged. Holding it back
would leave canonize pointing at a file no plant has. It is a separate
contract from SESSION_RECORD_FORM_IS_PLACED because it has its own reader and
its own record, and that slug stays as written in §12's history.
- **Given:** a fresh target directory
- **When:** `install.sh claude-code --project-dir <target>` runs
- **Then:** `docs/graph/plans/_harvest-candidates.template.md` exists and is
  byte-identical to the seed's
  `templates/docs/plans/_harvest-candidates.template.md`, placed by
  `place_docs_skeleton`'s existing `templates/docs/**` walk with
  `place_if_missing`
- **And:** no `docs/graph/plans/harvest-candidates.md` record is created; the
  record is the plant's, made from the form by canonize
- **And:** after the plant writes its own
  `docs/graph/plans/harvest-candidates.md` and edits the placed form,
  `install.sh all --project-dir <target>` leaves both files byte-identical
  and writes no backup beside either
- **And:** the seed places nothing else into `docs/graph/plans/` beyond the
  `grill.md` scaffold, the `sessions/` form, this form, and
  `adopted-instructions.md` when adoption writes it

### Contract: ENGINE_RECONCILE_PICKS_CONFIG_BY_ENGINE
- **Given:** a plant engine file and the seed's engine of the same name
- **When:** `tools/graft-graph-engine.py <plant-file> <seed-file>` runs with no
  `--preserve`
- **Then:** it preserves the config that engine carries: `ROOT_ID`, `KINDS`
  and `KIND_PREFIX` for `graph-lint.py`; `TEST_GLOBS` for `spec-lint.py`;
  nothing for `grill-lint.py`; and exits 0, having adopted the seed body with
  a `.bak-<ts>` of the plant file, or reporting it already current or
  KEEP-PLANT
- **And:** a plant file with any other name takes the `graph-lint.py` set
- **And:** an explicit `--preserve` wins over the per-engine set

### Contract: ENGINE_AUDIT_CHECKS_EVERY_PAIR
- **Given:** `tools/graft-audit.py <plant> <seed>` with `--engine
  <plant-file>:<seed-file>` given more than once
- **When:** it runs
- **Then:** it prints one engine-currency line per pair, each naming its plant
  file
- **And:** a malformed or unreadable pair, in any position, makes it exit
  non-zero, because a check that did not run is not reported as run

### Contract: EXISTING_PLANT_RECEIVES_CURRENT_ENGINES
- **Given:** an installed plant whose `docs/graph/grill-lint.py` is an older
  engine body
- **When:** `install.sh` re-runs
- **Then:** `docs/graph/grill-lint.py` is unchanged: the engines stay
  plant-owned
- **And:** when `tools/graft-graph-engine.py` then runs, with no
  `--preserve`, over each of the three engines, every run exits 0,
  `docs/graph/grill-lint.py` is byte-identical to the seed's, one backup holds
  the older body, and `python3 docs/graph/grill-lint.py --waves` prints a line
  starting `waves:`
- **And:** `tools/graft-audit.py` with the three `--engine` pairs reports
  every engine current

### Contract: PRISTINE_PRIOR_KERNEL_IS_NOT_MIGRATION
- **Given:** a target whose `CLAUDE.md` (or `AGENTS.md`) is byte-identical to
  `core/AGENTS.md` at an earlier commit of the seed checkout the installer runs
  from, and differs from the current `core/AGENTS.md`
- **When:** `install.sh claude-code --project-dir <target>` runs
- **Then:** the kernel is replaced with a backup, as `BACKUP_BEFORE_REPLACE`
  requires, and `docs/graph/plans/adopted-instructions.md` gains no row for
  that backup
- **And:** stderr carries no `OVERWRITTEN` line for it; the log names the
  replacement as a fast-forward from an earlier seed kernel
- **And:** a later run's orphan sweep files no row for that backup either
- **And:** a kernel body that matches no seed kernel in that history is filed
  exactly as today

### Contract: RECREATED_LIST_IS_COMPLETE
- **Given:** an installed plant whose `.cypress/seed.json` predates the run and
  from which twelve seed-owned graph nodes were deleted
- **When:** `install.sh claude-code --project-dir <target>` runs again
- **Then:** `.cypress/recreated-nodes.txt` lists all twelve paths, one per line,
  sorted and unique, under the header line §6 gives
- **And:** the console notice still prints at most ten paths, and it names the
  file that holds the whole list
- **And:** a later run that re-creates nothing rewrites the file with the header
  line alone, so the file always describes the run that last wrote the stamp

### Contract: UNKNOWN_STAMP_KEYS_SURVIVE
- **Given:** a `.cypress/seed.json` that holds the installer's own keys plus two
  keys the installer does not own, one a string and one an object
- **When:** `install.sh all --project-dir <target>` runs with no flag
- **Then:** both keys are in the new stamp with JSON-equal values, in their
  original order, after the installer's own keys
- **And:** the installer's own keys follow their existing rules
  (`DECISIONS_SURVIVE_SILENCE`, `ADAPTERS_ACCUMULATE`)

### Contract: PRE_GROWTH_POINTER_LIVES_IN_THE_PLACEHOLDER_INDEX
- **Given:** a fresh target directory
- **When:** `install.sh claude-code --project-dir <target>` runs
- **Then:** `docs/graph/index.md` holds one pre-growth block, delimited as §6
  gives, that names `EXPERT_SEED_INSTALL_PROMPT.md` and `protocol.initialize`
- **And:** the placed kernel, `CLAUDE.md`, names neither
  `EXPERT_SEED_INSTALL_PROMPT.md` nor `protocol.initialize`
- **And:** a re-install over a plant whose `index.md` has no such block leaves
  that `index.md` byte-identical, because the index is plant-owned

### Contract: CODE_ANCHOR_TOOL_IS_PLACED
- **Given:** a fresh target directory
- **When:** `install.sh all --project-dir <target>` runs
- **Then:** `docs/graph/code-anchor.py` exists and is byte-identical to the
  seed's `tools/code-anchor.py`
- **And:** no `.cypress/anchor.json` exists, because only canonize records an
  anchor
- **And:** a re-install over an older copy of the tool replaces it with a
  backup, as it does `docs/graph/status-register.py`

### Contract: MODEL_MAP_TEMPLATE_IS_PLACED
- **Given:** a fresh target directory
- **When:** `install.sh claude-code --project-dir <target>` runs
- **Then:** `docs/graph/models.md` exists and is byte-identical to the seed's
  `templates/docs/models.md`, placed by `place_docs_skeleton`'s existing
  `templates/docs/**` walk with `place_if_missing`, so `SINGLE_WRITER`'s
  census is unchanged
- **And:** after the plant edits the placed map, `install.sh all
  --project-dir <target>` leaves it byte-identical and writes no backup
  beside it

### Contract: OPENCODE_MODEL_FROM_MAP
- **Given:** a plant whose `docs/graph/models.md` fills the opencode cell of
  the `authoring | high` row with `` `provider-a/model-x` `` and of the
  `investigation | medium` row with `` `provider-b/model-y` ``, and whose
  graph holds an agent with `model: opus` and `effort: high` and one with
  `model: sonnet` and `effort: medium`
- **When:** `install.sh opencode --project-dir <target>` runs
- **Then:** each of the two agents' `.opencode/agents/<name>.md` equals its
  graph home `docs/graph/agents/<name>.md` with the `model:` line replaced by
  `model: provider-a/model-x` and `model: provider-b/model-y` respectively,
  and with no other byte changed
- **And:** the projection is written through `place_generated`, so it is a
  real file under `--symlink` as well, and `SINGLE_WRITER`'s exception count
  is unchanged
- **And:** the stamp's `agent_projections` entry for opencode records
  `"verbatim": false`
- **And:** a plant agent with `model: haiku` gets the opencode cell of the
  `investigation | low` row, whatever its `effort:` says (§6)

### Contract: OPENCODE_NO_MAP_ROW_NO_MODEL_LINE
- **Given:** a fresh target, so `docs/graph/models.md` is the unfilled
  template
- **When:** `install.sh opencode --project-dir <target>` runs
- **Then:** it exits 0, and each `.opencode/agents/<name>.md` equals its graph
  home with the `model:` line removed and no other byte changed
- **And:** the same holds, in a map whose other rows are filled, for an agent
  whose class and effort have no row, for one whose row's opencode cell is
  `-`, and for a plant agent with `model: inherit`, whatever the map says
- **And:** stdout carries one line that names `docs/graph/models.md` and the
  number of agents projected with no `model:` line, so an agent that runs on
  its caller's model is never silent

### Contract: OPENCODE_MAP_UNREADABLE_FAILS_CLOSED
- **Given:** an installed opencode plant whose `docs/graph/models.md` breaks
  the §6 map grammar (for example, a row whose class is `premium`)
- **When:** `install.sh opencode --project-dir <target>` runs
- **Then:** it exits non-zero, and stderr names `docs/graph/models.md` and the
  offending line
- **And:** every `.opencode/agents/*.md` is byte-identical to its state
  before the run, and no backup is made beside any of them

### Contract: OPENCODE_CHECK_DETECTS_DRIFT
- **Given:** an opencode plant, its record carrying opencode, installed with a
  map that fills the opencode cell of the `authoring | high` row
- **When:** `install.sh opencode --check --project-dir <target>` runs
- **Then:** after a hand edit to one `.opencode/agents/<name>.md`, it exits
  non-zero and names that projection as stale
- **And:** after an edit of the map's filled cell with no re-run, which
  changes only `model:` lines, it exits non-zero and names each projection
  whose `model:` line the edit changes
- **And:** the expected set is rendered from the plant's `docs/graph/agents/`
  and `docs/graph/models.md` by the §6 projection rule and compared with the
  plant's `.opencode/agents/`, backups excluded, so a projection that is
  missing, or that has no graph home, is stale too
- **And:** in sync, it exits 0 and says the opencode projections are up to
  date
- **And:** every run leaves the plant byte-identical: no projection, backup or
  stamp is written
- **And:** `install.sh all --check` checks the same projections, because
  `all` names opencode and the record carries it

### Contract: PRIME_HOOK_SCRIPTS_ARE_PLACED
- **Given:** a fresh target directory
- **When:** `install.sh prime-agent --project-dir <target>` runs
- **Then:** `.prime/agent/hooks/route-hook.py` and
  `.prime/agent/hooks/status-hook.py` exist and are byte-identical to the
  seed's `integrations/claude-code/route-hook.py` and `status-hook.py`
  (adr-0024), placed by `place_file`, so `SINGLE_WRITER`'s census is unchanged
- **And:** `adapter_dirs prime-agent` names `.prime/agent/hooks`, so the
  preflight covers it
- **And:** a re-install over an older copy of either script replaces it with
  a backup
- **And:** no `.claude/` directory is created by a `prime-agent` run alone

### Contract: REINSTALL_ENGINE_SERVES_THE_HOOKS
- **Given:** an installed plant whose `docs/graph/graph-lint.py` is an engine
  that predates `--plan-json` (the `v7.36.0` file) with a plant PROJECT CONFIG
  (a plant member in `KINDS`, a plant `KIND_PREFIX`), and older hook scripts
- **When:** a plain `install.sh <host>` runs again and places the hook scripts
- **Then:** it leaves `docs/graph/graph-lint.py` byte-unchanged, PROJECT CONFIG
  included: the engine is plant-owned and upgrading it is graft's job (adr-0014)
- **And:** the placed `route-hook.py` names the gap rather than routing to
  nothing: its first-prompt injection is the pointer line and one notice line
  naming `graph-lint.py`, `--plan-json` and graft (SPEC-0003
  `ENGINE_OLDER_THAN_HOOK_IS_NAMED`)
- **And:** after graft's engine step, `tools/graft-graph-engine.py <plant
  engine> <seed engine>` as `tools/graft-run.py` step 4 calls it, the engine
  accepts `--plan-json`, the placed `route-hook.py` injects a route (the
  suggestion header), and the plant's `KINDS` member and `KIND_PREFIX` survive

### Contract: SEED_ONLY_FILES_NEVER_PLACED
- **Given:** `SEED_ONLY` in `tests/seed-lint.py`, which names
  `tools/prepare-release.py` and `docs/skills/seed-release.md` (adr-0021)
- **When:** `seed-lint` runs
- **Then:** it fails, naming the path, when a `SEED_ONLY` path is missing from
  the seed or `manifest.json` names it
- **And:** it fails, naming `install.sh`, when the installer names a
  `SEED_ONLY` path or sources any file under `$SEED_ROOT/docs`
- **And:** it fails, naming `manifest.json`, when the keys of its `tools` map
  differ from the set of `$SEED_ROOT/tools/*` and `$SEED_ROOT/tests/*` files
  `install.sh` places

### Contract: EXPERTISE_PROPOSAL_WRITES_NOTHING
- **Given:** a target whose manifests (§6) declare dependencies, some of which
  have a page in the seed's `library-corpus/`, and a `skill-corpus/` or
  `tool-corpus/` page whose `stack:` names one of those library pages
- **When:** `install.sh <host> --expertise propose --project-dir <target>` runs
- **Then:** stdout carries one line per matching page, in the §6 proposal
  form: the corpus id, then the manifest path and the entry that matched; a
  skill or tool page names the library page id its `stack:` matched through.
  The lines are sorted by id and unique, and the run exits 0
- **And:** the target is byte-identical afterwards: no adapter is installed,
  no stamp or backup is written, and a target with no `.cypress/seed.json`
  still has none
- **And:** a target whose manifests match nothing gets one line saying so,
  so an empty proposal is never silent
- **And:** the matching is `tools/corpus-match.py`'s, run from the seed. The
  tool is not placed in the plant and is not a key of `manifest.json`'s
  `tools` map (SEED_ONLY_FILES_NEVER_PLACED)

### Contract: LANGUAGE_DECLARATION_PROPOSES_ITS_PAGE
- **Given:** a target whose manifest declares the language a `language` page
  covers, in a form the §6 language rows name: a `pom.xml`, `build.gradle` or
  `build.gradle.kts` that sets the Java language level, or a `pubspec.yaml`
  whose `environment:` carries a Dart SDK constraint
- **When:** the matcher runs over it (`--expertise propose`)
- **Then:** the proposal carries `library-corpus/language/java` or
  `library-corpus/language/dart`, and its evidence names that manifest and
  the declaration that matched
- **And:** a Flutter app's `pubspec.yaml` proposes `language/dart` beside
  `language/flutter`, because the Flutter SDK runs a Dart SDK and the dart
  page owns the SDK constraint

### Contract: OWN_PACKAGE_LIST_PROPOSES_ITS_PAGE
- **Given:** a library page whose `## What it is` carries the own-package list
  (§6), one list item per package the page covers, each opening with the
  package's name in backticks and a colon; and a target whose manifest
  declares one of those packages
- **When:** the matcher runs over it
- **Then:** the proposal carries that page, and its evidence names the
  manifest and the entry
- **And:** this holds in the page's own key, whichever it is, and the listed
  name is read the way that key's §6 row reads a manifest entry, so on an
  npm page `@stomp/rx-stomp` and the entry `@stomp/rx-stomp` meet as
  `stomp-rx-stomp`

### Contract: CITED_PACKAGE_PROPOSES_NOTHING
- **Given:** a library page that names a package outside its own-package
  list (in running prose, inside a list item that opens with something else,
  or in a later section), as its runtime dependency, its peer or the library
  it wraps; and a target whose manifest declares that package and none of
  the page's own
- **When:** the matcher runs over it
- **Then:** the proposal does not carry that page
- **Except:** a coordinate that a `maven` page names in its `## What it is`,
  which the transitional own-coordinate form (§6) reads as the page's own
  even when the page only cites it there. That page is proposed, a known
  false positive (§6, §11), and the owner leaves it out of the confirmed
  list. A coordinate a `maven` page cites in a later section proposes
  nothing

### Contract: PACKAGELESS_PAGE_PROPOSED_BY_ITS_TRIGGER
- **Given:** a `platform` or `cli` page, which no lockfile declares, and a
  target that holds one of the triggers the §6 rows list for it: the file
  the platform reads, an entry whose only use is to drive the platform, the
  tool's official image, the GitHub Action the tool's page names, the
  config file the tool reads, or one of its pre-commit hook ids
- **When:** the matcher runs over it
- **Then:** the proposal carries that page, and its evidence names the file
  that holds the trigger and the entry that matched, or `(present)` when the
  file's presence is the trigger

### Contract: EXPERTISE_PLACES_ONLY_THE_CONFIRMED_LIST
- **Given:** a target, and a comma-separated list of corpus ids (§6), each
  naming a page the seed carries under `library-corpus/`, `skill-corpus/` or
  `tool-corpus/`
- **When:** `install.sh <host> --expertise <id>[,<id>...] --project-dir
  <target>` runs
- **Then:** each listed page is placed at the destination §6 gives for its
  corpus, and no other corpus page is placed, whatever the manifests match
- **And:** a listed id no manifest matched is placed all the same, so the
  owner can add a page the matcher missed
- **And:** nothing is written under `docs/graph/legal/` by this arm: the
  legal corpus keeps its own flag and CORPUS_IS_WHOLE_OR_ABSENT
- **And:** every write goes through one of the four placers, so
  SINGLE_WRITER's exception count is unchanged

### Contract: UNKNOWN_EXPERTISE_ID_REFUSED_BEFORE_WRITING
- **Given:** an `--expertise` list holding, in turn, an id that names no page
  under the three corpus roots (misspelt, or under `legal-corpus/` or
  `agent-corpus/`), an id holding `..` or starting with `/`, two ids whose
  pages place at one destination (§6), and an id whose destination a
  different id recorded in the stamp's `expertise` key already owns (for
  example `library-corpus/container/redis` listed over a recorded
  `library-corpus/pypi/redis`)
- **When:** the installer runs
- **Then:** it exits non-zero naming each offending id, and the target is
  byte-identical: the ids are checked by the preflight, before the first
  write
- **And:** the refusal is the tool's own message, not a raw shell or Python
  error, as PREFLIGHT_REFUSES_BEFORE_WRITING requires
- **And:** the same preflight refuses a skill id whose destination is a node
  the seed's own `skills/` places, and an id whose destination is a scaffold
  leaf the seed places from `templates/docs/`, because either page would be
  replaced by the seed's own on the same run

### Contract: PLACED_PAGE_CARRIES_ITS_PROVENANCE
- **Given:** a library or tool page placed by `--expertise`
- **When:** the install completes
- **Then:** the placed file's first line is the provenance line of §6, which
  carries `origin: corpus@<seed version>` and the corpus id, and every later
  byte equals the corpus page
- **And:** a placed skill page carries its provenance in its frontmatter
  instead, as PLACED_SKILL_IS_A_ROUTABLE_NODE gives
- **And:** `<seed version>` is the `version` of the seed's `manifest.json`,
  the same value the run writes to the stamp's `version`
- **And:** `tools/graft-audit.py` reads `origin: corpus@` and classifies the
  page, and a backup of it, as corpus-placed: neither seed-owned nor
  plant-authored, and never `UNMAPPED` (EVERY_BACKUP_IS_CLASSIFIABLE)

### Contract: PLACED_SKILL_IS_A_ROUTABLE_NODE
- **Given:** a `skill-corpus/<key>/<name>.md` page, which carries node
  frontmatter, placed by `--expertise` into a plant installed for claude-code
- **When:** the install completes
- **Then:** `docs/graph/skills/<name>.md` equals the corpus page with its
  `origin:` value set to `corpus@<seed version>` (the key added when the page
  has none) and no other byte changed
- **And:** it is a top-level node of the plant's graph:
  `python3 docs/graph/graph-lint.py --show <its id>` exits 0 and prints it
- **And:** `.claude/skills/<name>/SKILL.md` exists, written by the existing
  skill projection with no new projection code

### Contract: EXPERTISE_IS_RECORDED_IN_THE_STAMP
- **Given:** a run that places one or more pages through `--expertise`
- **When:** the stamp is written
- **Then:** `.cypress/seed.json` holds the `expertise` key of §6: one entry
  per recorded page, with its corpus id, its placed path relative to the
  target and the SHA-256 of the bytes the installer wrote there, sorted by id
- **And:** `expertise` is an installer-owned key, written with the
  installer's own keys, and every key the installer does not own still
  survives (UNKNOWN_STAMP_KEYS_SURVIVE)
- **And:** a later explicit list adds its ids to the record; no run removes a
  recorded id or deletes a placed page (§11)
- **And:** a plant that never used `--expertise` gets no `expertise` key, so
  its stamp is unchanged by this arm

### Contract: EXPERTISE_SURVIVES_SILENCE
- **Given:** a plant whose stamp records `expertise` entries, each page on
  disk equal to its recorded hash
- **When:** a later install runs with no `--expertise` flag
- **Then:** the record keeps every id, and each recorded page is placed again
  from the running seed: a page whose new bytes equal the bytes on disk is
  not rewritten, and a page whose bytes changed (a newer seed version, or a
  newer corpus page) is replaced with a backup (BACKUP_BEFORE_REPLACE) and
  its recorded hash updated
- **And:** an identical re-run from the same seed rewrites no page and makes
  no backup (IDENTICAL_RERUN_IS_INERT)
- **And:** a recorded page the plant deleted is placed again and named in the
  log, as a re-created seed node is, because the record holds the owner's
  decision until the owner changes it (§11)
- **Except:** a recorded id whose page is gone from the running seed.
  RECORDED_EXPERTISE_PAGE_WITHDRAWN governs it, so it is not placed again
  even when the plant deleted the page

### Contract: PLANT_EDITED_PAGE_IS_LEFT_AND_NAMED
- **Given:** a recorded page whose bytes on disk differ from its recorded
  hash
- **When:** a later install runs, with no `--expertise` flag or with a list
  that names its id
- **Then:** the page is byte-identical afterwards and no backup is made
  beside it
- **And:** one log line names its path, says the plant edited it, and names
  graft Phase 4 as the step that merges the corpus's newer layer into it
- **And:** its record entry is unchanged, hash included, so the next run
  still finds it edited

### Contract: PLANT_OWNED_PAGE_IS_NEVER_REPLACED
- **Given:** a target where the destination of a listed id already exists
  and the record holds no entry for that id: the plant's own page, written by
  its `ingest-library` or by hand
- **When:** `install.sh <host> --expertise <that id>` runs
- **Then:** the file is byte-identical afterwards, no backup is made beside
  it, and one log line names its path and graft Phase 4, as
  PLANT_EDITED_PAGE_IS_LEFT_AND_NAMED gives
- **And:** no record entry is written for that id, because the installer
  placed nothing there; the other ids in the list are placed and recorded

### Contract: EXPERTISE_CHECK_NAMES_MISSING_OR_STALE
- **Given:** a plant whose stamp records `expertise` entries
- **When:** `install.sh <host> --check --project-dir <target>` runs
- **Then:** it names each recorded page that is missing, and each that is
  stale: its bytes equal the recorded hash and the running seed would place
  different bytes. With either present it exits non-zero
- **And:** a recorded page whose bytes differ from its recorded hash is named
  as plant-edited and left for graft Phase 4; it does not change the exit
  code on its own
- **And:** with every recorded page present and current, it says the
  expertise pages are up to date
- **And:** the run writes nothing: no page, backup or stamp
- **And:** a plant with no `expertise` key gets no expertise line, so the
  output CHECK_WITHOUT_COPILOT_SAYS_SO holds is unchanged for it

### Contract: JURISDICTION_RESOLVED_ONCE
- **Given:** a plant whose stamp records `legal_corpus: yes` and
  `legal_jurisdiction` as a two-letter code
- **When:** `install.sh <host> --project-dir <target>` runs again, in turn
  with no `--legal-jurisdiction` flag and with the flag naming another code
- **Then:** the installer resolves the jurisdiction once, the flag first and
  then the stamp's recorded value, and the national-layer report, the stamp
  writer and the closing NEXT STEP banner all read that one value
- **And:** with no flag, no line of the run calls the jurisdiction undecided
  or says no `--legal-jurisdiction` was given; the report names the recorded
  code, and the stamp keeps it
- **And:** with the flag, the report names the flag's code and the stamp
  records it (DECISIONS_SURVIVE_SILENCE: only silence keeps a recorded value)
- **And:** a plant with no recorded code and no flag still gets the
  undecided banner

### Contract: CHECK_EXECUTES_EACH_WIRED_HOOK
- **Given:** an installed plant, and the context hooks its recorded hosts
  wire: the `UserPromptSubmit` and `SessionStart` commands of
  `.claude/settings.json`, the commands of the Copilot
  `.github/hooks/route.json` and `status.json` when the plant has them, and
  the `.prime/agent/hooks/` scripts the Prime Agent extensions call
- **When:** `install.sh <host> --check --project-dir <target>` runs
- **Then:** for each wired context hook it resolves the script the command
  names under the target, and fails, exiting non-zero and naming the hook,
  its event and the script, when the script is absent
- **And:** it runs each present script once from the target, without the
  command's `|| true`, on the §6 check envelope of its event, and fails the
  same way when the script exits non-zero or prints nothing on stdout; a
  passing hook gets one line saying it ran
- **And:** the envelope carries no session id, so neither script writes the
  ledger (SPEC-0003 LEDGER_ABSENT_SESSION_ID_FULL,
  STATUS_HOOK_NO_LEDGER_WRITES_NOTHING), and the run leaves the plant
  byte-identical
- **And:** on that envelope a sound hook always prints: `route-hook.py`
  gives the full injection, the pointer line or the no-graph message (the
  prompt is not trivial and the envelope is a top-level human turn), and
  `status-hook.py` ends with the code-anchor line or its not-checked line
  even when the status register is absent, fails or prints nothing (SPEC-0003
  STATUS_HOOK_RESETS_WITHOUT_REGISTER,
  STATUS_HOOK_ANCHOR_FAILURE_FAILS_TOWARD_INCLUSION). A silent register is
  therefore not a failed check
- **And:** a wired command that names no script under the plant is said on
  one line and not run
- **And:** `bound-hook.py`, wired under `PreToolUse` without `|| true`, is a
  guard and not a context hook, and is not run
- **And:** with every hook passing, CHECK_WITHOUT_COPILOT_SAYS_SO's line and
  exit code are unchanged

### Contract: CHECK_FLAGS_RETIRED_HARNESS_ENTRY
- **Given:** a plant carrying an `origin: seed` agent or skill that the
  running seed does not ship (no `agents/<name>.md`, no
  `skills/<name>/SKILL.md` in the seed): its graph node
  `docs/graph/agents/<name>.md` or `docs/graph/skills/<name>.md`, a harness
  entry projected from it (§6 harness entries), or a harness entry with no
  graph node whose own frontmatter says `origin: seed`
- **When:** `install.sh <host> --check --project-dir <target>` runs
- **Then:** it prints one `RETIRED` line (§6) for each such node and each such
  entry, naming its target-relative path
- **And:** the run writes nothing and deletes nothing; the deletion is the
  owner's act (the owner decided on 2026-10-04 that such entries are
  flagged, never deleted)
- **And:** a `RETIRED` line is a flag, not a failure: the exit code is the one
  the rest of the check sets, so CHECK_WITHOUT_COPILOT_SAYS_SO's exit 0 holds
  for a plant whose only finding is a flag
- **And:** `tools/graft-audit.py <plant> <seed>` prints the same lines after
  its backup verdicts, and classifies a backup of such an entry `RETIRED`
  in place of `UNMAPPED` (EVERY_BACKUP_IS_CLASSIFIABLE); neither changes its
  exit code

### Contract: CHECK_FLAGS_ORPHAN_HARNESS_ENTRY
- **Given:** a plant carrying a harness entry (§6) whose graph node is
  absent and which is not an `origin: seed` entry: an agent or skill the
  plant authored straight into a harness directory, which the router and
  every other harness cannot see
- **When:** `install.sh <host> --check --project-dir <target>` runs
- **Then:** it prints one `ORPHAN` line (§6) naming the entry and the graph
  node it lacks
- **And:** the run writes nothing and deletes nothing, and the exit code is
  the one the rest of the check sets, as for a `RETIRED` line
- **And:** `tools/graft-audit.py <plant> <seed>` prints the same line
- **And:** with no `RETIRED` and no `ORPHAN` finding, `--check` says in one
  line that every harness entry has a graph home

### Contract: CHECK_FLAGS_RETIRED_GRAPH_NODE
- **Given:** a plant carrying an `origin: seed` node under
  `docs/graph/protocols/` or `docs/graph/method/` whose seed source (§6
  "Retired graph nodes") the running seed does not ship: a node the seed
  folded into others, such as a protocol whose rules moved into a skill and
  a method node, which no harness projects
- **When:** `install.sh <host> --check --project-dir <target>` runs
- **Then:** it prints one `RETIRED` line (§6) naming the node's
  target-relative path, the line CHECK_FLAGS_RETIRED_HARNESS_ENTRY prints for
  an agent or skill
- **And:** the run writes nothing and deletes nothing, and the exit code is
  the one the rest of the check sets, as for a `RETIRED` harness entry; the
  deletion stays the owner's act, named by graft migration (d)
- **And:** `tools/graft-audit.py <plant> <seed>` prints the same line after
  its backup verdicts, and `--harness` prints it, neither changing its exit
  code; the classification has its one home there, which `--check` runs
- **And:** a node in those folders whose seed source the seed ships, or
  whose frontmatter does not say `origin: seed`, is not named

### Contract: GRAFT_RUN_TIES_LINT_ERRORS_TO_RETIRED_NODES
- **Given:** a plant carrying a node CHECK_FLAGS_RETIRED_GRAPH_NODE names,
  whose `owns:` repeats a fact-key that a node the seed ships owns, so the
  stage copy's `docs/graph/graph-lint.py` fails with a duplicate fact-key
  error naming the retired node's `id` (a graft that leaves a retired
  `protocol.toolcraft` beside `skill.toolcraft`)
- **When:** `tools/graft-run.py <plant> <seed> --stage <dir>` runs
- **Then:** its `graft.gate.routes` row names the node's path among the
  `RETIRED` entries it reads from the `--check` lines, and adds
  `RETIRED_LINT_CLAUSE` (§6) with the count of graph-lint error lines that
  name the `id` of a RETIRED node, and those ids
- **And:** the row's verdict stays the one graph-lint's exit sets (BLOCK
  here), because the error is real until the steward deletes the node by
  name, migration (d); the `RETIRED` flag itself gates nothing, and
  graft-run deletes nothing in the plant or the stage
- **And:** an error line that names no RETIRED node's id is not counted, and
  with no such line the clause is absent

## 5. Non-functional requirements

- **Compatibility:** bash and `python3` only; no third-party imports. The
  binding shell floor is bash, not the POSIX subset: `install.sh:1` declares
  `#!/usr/bin/env bash`, `:69` uses `set -euo pipefail` whose `pipefail` POSIX's
  `set` does not define, and every shell file in this tree declares a bash
  shebang. The in-tree constraint that is recorded is the bash 3.2 floor
  (`install.sh:1824`, `:2192`). The two floors are different and a grown
  plant's graph owns the distinction at `docs/graph/best-practices/bash.md`
  §"Two floors, not one"; it is not restated here. (This line claimed a POSIX
  shell floor until 2026-09-16 — see §12.)
  Placement is exercised on Linux and macOS in CI, because symlink semantics are
  where the platforms differ.
- **Reliability:** generation completes before replacement, so a failed
  generation cannot leave a partial destination.
- **Security:** an install may not modify any path outside `--project-dir`.
  An `--expertise` id resolves only to a page under the seed's
  `library-corpus/`, `skill-corpus/` or `tool-corpus/`, so an id cannot name
  a source outside them (UNKNOWN_EXPERTISE_ID_REFUSED_BEFORE_WRITING).

## 6. Data shapes

```yaml
# .cypress/seed.json — the plant's persistent record
seed:                 { type: string, const: "cypress" }
version:              { type: string }            # seed version now installed
installed_at:         { type: string, format: rfc3339 }
installed_from:       { type: string, optional: true }
tools:                { type: string }            # space-joined adapter list, accumulating
legal_corpus:         { enum: [yes, no, undecided] }
legal_jurisdiction:   { type: string }            # two-letter code, or "undecided"
agent_projections:    { type: array, derived_from: tools }
```

Beyond the keys above, the stamp has one rule: any key the installer does not
own is carried forward unchanged.

```yaml
# .cypress/seed.json, additions to the shape above
additional_keys:      { carried: unchanged, order: kept, after: installer keys }
```

```text
# .cypress/recreated-nodes.txt: written by every run that writes the stamp
# install.sh <version> <UTC rfc3339>: seed-owned graph nodes re-created by this run
docs/graph/protocols/grill.md
docs/graph/skills/humanizer/SKILL.md
```

The pre-growth block in the placeholder `docs/graph/index.md` opens with the
line `<!-- pre-growth: grow removes this block -->` and closes with the line
`<!-- /pre-growth -->`. `protocol.grow` removes it in the phase that sets
`grown: true`.

The stamp's `agent_projections` entry for opencode reads
`{"tool": "opencode", "path": ".opencode/agents/{name}.md", "verbatim": false}`
(adr-0022); the other hosts' entries are unchanged.

The model map, `docs/graph/models.md` (adr-0022), is placed from
`templates/docs/models.md` when missing and is plant-owned from then on. The
opencode projection reads one table from it:

```text
# the first table under the `## Map` heading
header:   | Class | Effort | Prime Agent | opencode |          exact
class:    authoring | investigation                          closed set
effort:   low | medium | high                                closed set
rows:     at most one per (class, effort); a missing pair reads as unfilled
cell:     `<provider>/<model>`   one inline-code span, at least one "/", no
                                 whitespace, no "<" or ">"           filled
          `<...>` or <...>       the template's placeholder          unfilled
          -                      inherit the caller's model          unfilled
token:    model: opus   -> authoring, the agent's effort
          model: sonnet -> investigation, the agent's effort
          model: haiku  -> investigation, low (the agent's effort is not read)
          model: inherit -> no row: the projection carries no model line
```

The opencode projection of a graph agent follows from its frontmatter:

| The agent's `model:` and `effort:` | The projected `model:` line |
|---|---|
| `opus`, `sonnet` or `haiku`, and the map's cell for its (class, effort) is filled | `model: <cell>`, in place of the token |
| `opus`, `sonnet` or `haiku`, and the cell is unfilled, the row is missing, the `effort:` of an `opus` or `sonnet` agent is missing, or the map is absent | none |
| `inherit`, or no `model:` key | none |
| any other `model:` value | copied unchanged |

A map is absent when the plant renamed it by hand to
`docs/graph/models.unfilled.md`, a marker `place_docs_skeleton` honours by
leaving `docs/graph/models.md` unplaced; `graft-audit.py --rename` leaves the
map in place (ADR-0022, S4). The Prime
Agent column is read by the Prime Agent overlay, and the installer does not
read it.

`--check` renders the same rule into a scratch directory under the run's stage
and compares it with `.opencode/agents/`, excluding `*.bak-*`. The opencode
projections are in its scope when the run names opencode, directly or through
`all`, and the stamp's `tools` carries opencode; the Copilot views keep their
own scope rule (ALL_CHECK_INCLUDES_RECORDED_COPILOT). With neither in scope,
the run says that no generated views are in scope and exits 0.

### Selective placement (8.0.0)

A corpus id is the page's path in the seed, relative to the seed root, without
`.md`: `library-corpus/<key>/<name>`, `skill-corpus/<key>/<name>` or
`tool-corpus/<category>/<name>`. `--expertise` takes `propose`, or a
comma-separated list of ids with no spaces.

```yaml
# .cypress/seed.json, the installer-owned key (absent until a page is placed)
expertise:
  type: array
  sorted_by: id
  items:
    id:     { type: string }   # corpus id, as above
    path:   { type: string }   # placed path, relative to the target
    sha256: { type: string }   # hex digest of the bytes the installer wrote
```

| Corpus | Destination in the plant | Provenance |
|---|---|---|
| `library-corpus/<key>/<name>` | `docs/graph/libraries/<name>.md` | the provenance line, prepended |
| `tool-corpus/<category>/<name>` | `docs/graph/tools/<name>.md` | the provenance line, prepended |
| `skill-corpus/<key>/<name>` | `docs/graph/skills/<name>.md`, a top-level node | frontmatter `origin: corpus@<seed version>` |

Two ids with one destination (for example `library-corpus/pypi/redis` and
`library-corpus/container/redis`) are refused before writing
(UNKNOWN_EXPERTISE_ID_REFUSED_BEFORE_WRITING); the owner places one of them,
and graft Phase 4 folds the other into that page by hand.

```text
# the provenance line: the first line of a placed library or tool page
<!-- origin: corpus@<seed version> id: <corpus id> -->

# one proposal line per match, on stdout of --expertise propose
<corpus id>  <manifest path>: <entry>
<corpus id>  stack: <library corpus id>
```

The matcher, `tools/corpus-match.py`, reads the direct dependencies each
manifest declares, normalizes each one to a candidate id, and proposes every
library page whose `<key>/<name>` equals a candidate, compared without regard
to case. One entry proposes every page one of its candidates names, so a
module's own page and its family's umbrella page are proposed together. It
then proposes every skill and tool page whose `stack:` names a library page it
proposed.

The walk reads the project's own manifests. It does not enter a dependency
store, a build output, a virtual environment (`.venv*`), version control, the
plant's `docs/graph/`, a scratch or copy directory (`.tmp/`,
`.graft-backup-*`, `.graft-snapshot-*`, `*.bak-*`), an agent host's own
directory (`.claude/`, `.opencode/`, `.codex/`, `.prime/`), a nested plant
(a directory holding its own `.cypress/seed.json`) or a symlinked directory.
A copy repeats the plant's manifests, and reading it would put a scratch path
in the evidence or propose what the plant has since dropped.

| Manifest | Key | Candidate names from one entry |
|---|---|---|
| `pom.xml` (`<dependency>`, `<plugin>`) | `maven` | every run of consecutive tokens of the `artifactId` (tokens split at `-` and `.`), read three ways: as written, with a `starter` token dropped, and with it and the token before it dropped; the last segment of the `groupId`, and its last two segments joined by `-`; and the `groupId:artifactId`, read the same three ways, against the coordinates a page claims (the own-coordinate form below) |
| `pom.xml`, present | `cli` | `maven` |
| `pom.xml` setting the Java language level: a `java.version`, `maven.compiler.release`, `maven.compiler.source` or `maven.compiler.target` property, or the compiler plugin's `<release>`, `<source>` or `<target>` | `language` | `java` |
| `build.gradle`, `build.gradle.kts` setting the Java language level: a Java toolchain's `languageVersion`, or a `sourceCompatibility` or `targetCompatibility` | `language` | `java` |
| `package.json` (`dependencies`, `devDependencies`) | `npm` | the package name, lowercased, a leading `@` dropped and `/` read as `-` |
| `package.json`, present | `language` | `nodejs`; also `typescript` when `typescript` is a dependency, and `angular` when `@angular/core` is |
| `requirements*.txt`, `pyproject.toml` | `pypi` | the name normalized as PyPI does: lowercased, each run of `-`, `_` and `.` read as `-` |
| `requirements*.txt` or `pyproject.toml`, present | `language` | `python` |
| `*.csproj` (`PackageReference Include`) | `nuget` | the package id as written |
| `*.csproj`, present | `language` | `dotnet` |
| `pubspec.yaml` (`dependencies`, `dev_dependencies`) | `pub` | the package name as published |
| `pubspec.yaml` with an `sdk: flutter` dependency | `language` | `flutter` |
| `pubspec.yaml` whose `environment:` carries an `sdk:` constraint | `language` | `dart` |
| compose files (`image:`), `Dockerfile` and `Containerfile` (every stage's `FROM`), `bitbucket-pipelines.yml` (each `image:` given as a string, at file level or on a step) | `container` | the image's last path segment, tag and digest dropped; nothing for a `FROM` that names an earlier stage, `scratch`, or an image whose last segment is a variable |
| the same images | `language`, `cli` | `nodejs` for a `node` image, `python` for a `python` image, `dotnet` for an image under a `dotnet/` path; `cli/maven` for a `maven` image, `cli/trivy` for a `trivy` image, `cli/gitleaks` for a `gitleaks` image |
| a compose file, present | `container` | `docker-compose` |
| a `Dockerfile` or `Containerfile`, present | `container` | `docker` |
| `dotnet-tools.json` (`tools`) | `nuget` | the tool's package id as written |
| `azure-pipelines*.yml`, present | `platform` | `azure-pipelines-yaml` |
| `bitbucket-pipelines.yml`, present | `platform` | `bitbucket-pipelines` |
| Ansible `requirements.yml` (`collections:`) | `galaxy` | the collection name, dotted as written |
| Ansible `requirements.yml`, the collection `community.proxmox`; `requirements*.txt` or `pyproject.toml`, the requirement `proxmoxer` | `platform` | `proxmox-ve` |
| `.github/workflows/*.yml` and `*.yaml`, a step's `uses:` naming `aquasecurity/trivy-action` or `gitleaks/gitleaks-action` at any ref | `cli` | `trivy`, `gitleaks` |
| `trivy.yaml`, `.trivyignore`, present | `cli` | `trivy` |
| `.gitleaks.toml`, present; `.pre-commit-config.yaml`, a hook `id:` of `gitleaks`, `gitleaks-docker` or `gitleaks-system` | `cli` | `gitleaks` |

A key the seed's `library-corpus/` does not carry yet proposes nothing. A
lockfile's transitive entries are not matched (§11). Any page no row of this
table reaches is placed only when the owner lists it. The evidence of a
declaration names it (`java.version`, `languageVersion`, `sdk`), the evidence
of a `uses:` names the action as written, and the evidence of a hook names
its id.

**Language pages** (LANGUAGE_DECLARATION_PROPOSES_ITS_PAGE). A `language`
page is proposed by the manifest fact that says the project is written in
that language. When a manifest belongs to one language, its presence is that
fact: `package.json`, a Python requirement file, a `*.csproj`. When a
manifest serves several languages, the fact is the declaration the language
page names as the language's own. A Maven or Gradle build also compiles
Kotlin, Scala or Groovy, and an aggregator `pom.xml` compiles nothing, so
`language/java` waits for the Java language level, which the java page
places in the build descriptor. A `pubspec.yaml` serves a Dart package and a
Flutter app alike, and its `environment:` `sdk:` constraint belongs to the
Dart SDK, which the dart page owns; a Flutter app therefore proposes both
pages. The trade-off: presence would also propose `language/java` for a
Kotlin-only build. The declaration rule misses a build that inherits its
level from a parent outside the project, and the owner lists `language/java`
for it by hand (§11). A Gradle build is read for its language level only;
its dependencies match no `maven` page yet (§11).

**The own-package list** (OWN_PACKAGE_LIST_PROPOSES_ITS_PAGE,
CITED_PACKAGE_PROPOSES_NOTHING). This is the one convention a corpus page
author follows to say which packages a library page covers. In the page's
`## What it is` section, write a Markdown list with one item per package the
page covers, each item opening with the package's registry name in
backticks, then a colon:

```markdown
## What it is
<what the family of packages is, in a sentence or two>

- `<package>`: <what this package is>
- `<package>`: <what this package is>
```

Each listed name proposes the page. It is read the way the page's key reads
a manifest entry in the table above, so `@stomp/stompjs` on an npm page
meets the entry `@stomp/stompjs`. The page's own `<name>` proposes it as
before, listed or not. Every other mention of a package is a citation: in
running prose, inside an item that opens with something else, or in a later
section. A citation proposes nothing, so a page can name its runtime
dependency, its peer or the library it wraps, and a project that declares
only that package is not offered the page. Two pages that both list one
package are both proposed by it, as one entry proposes every page one of its
candidates names.

The list lives in the prose, not in a frontmatter field, because the list is
then the fact's one home: the reader and the matcher read the same lines,
and a corpus page needs no new shape (it carries no frontmatter, and a
placed page keeps the corpus page's bytes under its provenance line). A
`packages:` field would repeat what the section says and drift from it. The
cost is that the convention is a shape of prose that only an author can get
right. A page that names its own sibling packages only in running prose is
not proposed by them, which costs recall that the owner recovers by listing
the id. An item that opens with a dependency's name makes it the page's own,
which costs precision (OWN_PACKAGE_NAMED_ONLY_IN_PROSE). The decision is
reversible: changing the convention touches the matcher and the corpus pages,
and no plant's data.

**The own-coordinate form** (`maven` only, transitional). A `maven` page
also claims each `groupId:artifactId` its `## What it is` section names in
backticks, in a list or in prose, read the three ways the table reads an
`artifactId`. A coordinate that a later section cites is not the page's own.
The maven pages were written to this form before the own-package list
existed, and the form cannot tell an owned coordinate from a cited one in
that section: the mysql-connector-j page names MariaDB's driver there as the
alternative, so the entry `org.mariadb.jdbc:mariadb-java-client` proposes
the mysql-connector-j page. A maven page therefore cites a coordinate it does
not own in a later section. That proposal is not always wrong: the
mysql-connector-j page has a MariaDB section, so a project on the MariaDB
driver may want it. Until a page is rewritten, the owner decides whether a
page proposed this way belongs on the list. An own-package list item on
a maven page names the full `groupId:artifactId`, which this form reads as
well. §11 asks when the maven pages move to the list and the form retires.

**Pages without a package** (PACKAGELESS_PAGE_PROPOSED_BY_ITS_TRIGGER). A
`platform` or `cli` page has no lockfile entry, so the rows above name its
triggers, and a trigger is admitted only when it exists to drive that
subject: the file a platform reads (`azure-pipelines*.yml`,
`bitbucket-pipelines.yml`), an entry whose only use is to call the platform
(the `community.proxmox` collection and the `proxmoxer` client both drive the
Proxmox VE API, as the platform page's Interop and the collection's page
say), the official image of a tool that arrives as an image (`maven`,
`trivy`, `gitleaks`), the GitHub Action the tool's page names as its own
channel, the config file the tool reads by default, and the pre-commit hook
ids the tool's page names. A `bitbucket-pipelines.yml` is read for its step
images, and a GitHub workflow for its `uses:` lines, because the CI step is
where a scanner's version is decided, as the trivy and gitleaks pages say. A
`bitbucket-pipelines.yml` image given as a mapping (`name:` beside registry
credentials) is not read; an official tool image needs no credentials. A
trigger is a row of this table, never a word found in a script, so a page
gains a trigger through a row here and a test.

Four pages are unreachable by decision: `platform/azure-cli`,
`platform/azure-devops-rest`, `cli/curl` and `cli/git`. An operator runs them
from a shell, or a script calls them, and no manifest declares them. Git is
the project's version control, which the walk does not enter, and curl ships
in nearly every base image, so a trigger for either would fire on every
project and tell the owner nothing. The Azure CLI and the Azure DevOps REST
API appear in scripts and pipeline steps only as command text, which this
matcher does not read. The image rows do not reach them either: a `git` or
`curl` image proposes only a `container` page of that name, and the corpus
carries none. The owner lists them by id when a plant wants them.

The check envelope (CHECK_EXECUTES_EACH_WIRED_HOOK) is the host's envelope
for the hook's event (SPEC-0003 §6) with no `session_id`. For
`UserPromptSubmit` its prompt is the fixed text
`cypress install check: route this task`, which is not trivial and carries no
non-human marker; for `SessionStart` its `source` is `startup`. The Prime
Agent scripts get the same values through the argv envelope (`--prompt=`,
`--source=`). The check's lines, with `<event>` and `<script>` the hook's event
and its target-relative path:

```text
[seed] --check: hook <event> <script> ran and printed its context.
[seed] WARNING: --check: hook <event> <script> is wired but the script is missing; re-run install.sh to restore it
[seed] WARNING: --check: hook <event> <script> failed (exit <code>)
[seed] WARNING: --check: hook <event> <script> printed nothing on stdout
```

The harness entries (CHECK_FLAGS_RETIRED_HARNESS_ENTRY,
CHECK_FLAGS_ORPHAN_HARNESS_ENTRY) are the files the roster and skill
projections write, read in every harness directory the plant carries, recorded
or not:

| Entry | Graph home |
|---|---|
| `<adapter>/agents/<name>.md`, `<adapter>` one of `.claude`, `.codex`, `.opencode`, `.prime/agent` | `docs/graph/agents/<name>.md` |
| `<adapter>/skills/<name>/SKILL.md`, the same adapters | `docs/graph/skills/<name>.md` |
| `.github/agents/<name>.agent.md` | the `docs/graph/agents/` node whose name, without a leading `<digits>-`, is `<name>` |

A name starting with `_`, `index` and `README`, and an installer backup, are
not entries. The flag lines, with `<entry>` and `<home>` target-relative:

```text
[seed] --check: RETIRED <entry>: an origin: seed node or projection the running seed does not ship; the owner decides its deletion
[seed] --check: ORPHAN <entry>: no graph home (<home>); propose relocating it into the graph, graft migration (c)
[seed] --check: every harness entry has a graph home.
```

`tools/graft-audit.py` prints the same two flag lines without the `[seed]
--check: ` prefix.

### Retired graph nodes

The nodes CHECK_FLAGS_RETIRED_GRAPH_NODE reads are the `*.md` files directly
under `docs/graph/protocols/` and `docs/graph/method/` whose frontmatter says
`origin: seed`; with `agents/` and `skills/` (CHECK_FLAGS_RETIRED_HARNESS_ENTRY)
they are the four machinery folders graph-lint reads as nodes (its
`MACHINERY_DIRS`). A name starting with `_`, `index` and `README` is not a
node. A node's seed source is the file the installer places it from,
`protocols/<name>.md` or `core/method/<name>.md` in the seed; the one home of
that map is `seed_source_for` in `tools/graft-audit.py`, which the backup
audit reads too. The node is `RETIRED` when that file is absent, and its line
is the `RETIRED` line above.

`tools/graft-run.py`'s `graft.gate.routes` row reports the flags it reads
from the `--check` lines of each host, then the clause for the lint errors
they explain:

```text
<n> RETIRED entr{y|ies} (<first three paths>[ ...]; migration (c)/(d), not gated)
<n> ORPHAN harness entr{y|ies} (<first three paths>[ ...]; migration (c)/(d), not gated)
RETIRED_LINT_CLAUSE: "<n> graph-lint error(s) name a RETIRED node (<ids>): each clears when the steward deletes that node by name, migration (d)"
```

A graph-lint error line is an output line that starts with `✗`. It names a
RETIRED node when the `id` in that node's frontmatter, read from the stage
copy, appears in it as a whole word (no letter, digit, `.`, `-` or `_` on
either side). `<ids>` lists each such id once, in path order. A RETIRED path
outside `docs/graph/`, or a node with no `id`, is named in the first line
and counts no error.

## 7. Failure modes

### Failure: DESTINATION_PATH_OCCUPIED
- **Trigger:** a needed directory exists as a regular file
- **Response:** non-zero exit naming every offending path
- **Side effects:** none for an ENUMERATED path — the refusal precedes the
  first write. For a path the preflight does not reach (a per-skill leaf under
  `.claude/skills/`), `ensure_dir` refuses late and the writes already made
  stand; see PREFLIGHT_REFUSES_BEFORE_WRITING's `Except`.
- **Recovery:** move or remove the file and re-run

### Failure: TARGET_NOT_WRITABLE
- **Trigger:** the target directory denies writes
- **Response:** non-zero exit naming the path
- **Side effects:** none
- **Recovery:** fix permissions and re-run

### Failure: CONTRADICTORY_CORPUS_TRANSITION
- **Trigger:** `--legal-corpus no` while corpus pages are installed
- **Response:** non-zero exit naming the page count and both remedies
- **Side effects:** none; the installer never deletes a corpus
- **Recovery:** record `yes`, or remove the corpus deliberately and then `no`

### Failure: PARTIAL_CORPUS
- **Trigger:** placed page count does not equal the seed's
- **Response:** `die` — a subset makes a missing instrument indistinguishable
  from one that does not apply
- **Recovery:** re-run; investigate placement if it recurs

### Failure: FROZEN_PROJECTION_LEFT_STALE
- **Trigger:** the stamp records a frozen host and `install.sh all` runs
  without acting on it (a github-copilot that `all --check` checks is acted on;
  see ALL_CHECK_INCLUDES_RECORDED_COPILOT)
- **Response:** one `WARNING` line per such host on stderr: its files were not
  refreshed, and `install.sh all <host>` refreshes them
- **Side effects:** none; the frozen host's tree is left exactly as it was
- **Recovery:** re-run with the host named

### Failure: ENGINE_LEFT_STALE_BY_GRAFT
- **Trigger:** a graft reconciles fewer than the three engines, or the engine
  tool refuses one and the refusal is not acted on
- **Response:** `graft.gate.engine`, run with the three pairs, prints a `graph
  engine STALE` line naming the stale engine (`detective`: the line does not
  gate the exit code)
- **Side effects:** the plant keeps its older engine; for `grill-lint.py`,
  `--waves` is missing
- **Recovery:** run `tools/graft-graph-engine.py` over the named engine, or
  record a superset as KEEP-PLANT

### Failure: SEED_HISTORY_UNAVAILABLE
- **Contracts:** PRISTINE_PRIOR_KERNEL_IS_NOT_MIGRATION
- **Trigger:** the seed root is not a Git work tree, or `git` is not on `PATH`
- **Response:** the kernel is compared with the current `core/AGENTS.md` only,
  as before 7.32.0, and the log says so in one line
- **Side effects:** a pristine older kernel body is filed for migration: work
  for `docs-librarian` that turns out to be empty, never a lost instruction
- **Recovery:** none needed; the librarian strikes the row

### Failure: STAMP_NOT_AN_OBJECT
- **Contracts:** UNKNOWN_STAMP_KEYS_SURVIVE
- **Trigger:** `.cypress/seed.json` parses as JSON but its top level is not an
  object (an array, a string, a number, `true`, `false` or `null`)
- **Response:** the installer moves it aside to a `.bak-<ts>` sibling, writes a
  stamp from its own keys as before 7.32.0, and prints one warning that names
  the backup and says the keys it does not own could not be carried
- **Side effects:** those keys are in the backup only
- **Recovery:** the owner copies them back by hand

### Failure: MODEL_MAP_UNREADABLE
- **Contracts:** OPENCODE_MAP_UNREADABLE_FAILS_CLOSED, OPENCODE_CHECK_DETECTS_DRIFT
- **Trigger:** `docs/graph/models.md` exists and is not UTF-8, or its
  `## Map` table is missing, has a header other than §6's or no separator row
  under it, holds a row without four cells or a class or an effort outside §6's
  closed sets, repeats a (class, effort) pair, or has an opencode cell that is
  none of §6's cell forms; or `docs/graph/models.md` is a symlink leaving the
  target, which is refused as `docs/graph/index.md`'s is
  (SYMLINK_IS_REPLACED_NOT_FOLLOWED), naming the link
- **Response:** `die` naming the file and the offending line, before the
  first opencode agent is projected; under `--check`, the same exit and message
  before any comparison, so an unreadable map is never reported in sync
- **Side effects:** none under `--check`. Otherwise the writes the run made
  before the opencode adapter stand (the kernel, `docs/graph/`, an earlier
  adapter's tree); the opencode projections are unchanged; the stamp is not
  rewritten, because `write_seed_stamp` runs after every adapter
- **Recovery:** fix the map and re-run

### Failure: OPENCODE_SELECTOR_UNRESOLVED
- **Contracts:** OPENCODE_MODEL_FROM_MAP
- **Trigger:** a filled opencode cell names a `provider/model` the host's
  catalog does not carry
- **Response:** none from the installer, which has no access to the host's
  catalog and writes the cell as given. What opencode does when it spawns that
  agent: not recorded
- **Side effects:** that agent may fail to spawn on opencode
- **Recovery:** fix the row and re-run `install.sh opencode`

### Failure: EXPERTISE_MANIFEST_UNREADABLE
- **Contracts:** EXPERTISE_PROPOSAL_WRITES_NOTHING,
  LANGUAGE_DECLARATION_PROPOSES_ITS_PAGE, OWN_PACKAGE_LIST_PROPOSES_ITS_PAGE,
  PACKAGELESS_PAGE_PROPOSED_BY_ITS_TRIGGER
- **Trigger:** a manifest the matcher reads (§6) does not parse: a `pom.xml`
  that is not XML, a `package.json` that is not JSON, a file that is not UTF-8.
  A file whose presence alone is the trigger (`trivy.yaml`, `.trivyignore`,
  `.gitleaks.toml`) is not read, so it cannot be unreadable
- **Response:** one line names the manifest and why it was skipped, and the
  proposal is made from every other manifest; the run exits 0
- **Side effects:** none; a propose run writes nothing
- **Recovery:** fix the manifest, or add the pages it would have matched to
  the list by hand

### Failure: OWN_PACKAGE_NAMED_ONLY_IN_PROSE
- **Contracts:** OWN_PACKAGE_LIST_PROPOSES_ITS_PAGE,
  CITED_PACKAGE_PROPOSES_NOTHING
- **Trigger:** a page author breaks the own-package list (§6): a package the
  page covers is named only in running prose, or a list item of
  `## What it is` opens with a package the page only cites
- **Response:** the matcher reads the page as written. The first package
  proposes nothing; the second proposes the page. No line says so, because
  the page's text is the only statement of what it owns
- **Side effects:** none; a propose run writes nothing
- **Recovery:** the author rewrites the section to the own-package list.
  Until then the owner adds the missed id to the list by hand, or leaves the
  wrongly proposed one out. Pages that name their own sibling packages only
  in prose (several nuget, npm and pypi pages, written before the list
  existed) are converted by a docs pass; §11 asks how the last one is found

### Failure: RECORDED_EXPERTISE_PAGE_WITHDRAWN
- **Contracts:** EXPERTISE_SURVIVES_SILENCE, EXPERTISE_CHECK_NAMES_MISSING_OR_STALE
- **Trigger:** the stamp records an id whose page is missing from the
  running seed (the corpus renamed or withdrew it)
- **Response:** one `WARNING` line names the id; the placed page and its
  record entry are left as they are, and a plain install still exits 0,
  because the warning reports a seed change and no write failed; `--check`
  names it the same way and exits non-zero
- **Precedence:** over EXPERTISE_SURVIVES_SILENCE. A withdrawn page the plant
  deleted cannot be placed again: the run names the id in the same `WARNING`,
  writes nothing at the path and keeps the entry, so the record still says
  what the owner chose
- **Listed:** an `--expertise` list that names a withdrawn id is refused by
  the preflight like any id that names no page
  (UNKNOWN_EXPERTISE_ID_REFUSED_BEFORE_WRITING); the WARNING is for a
  recorded id the run re-applies in silence
- **Side effects:** none
- **Recovery:** graft Phase 4 decides whether the plant keeps the page as its
  own; the record entry goes with the removal path §11 leaves open

## 8. Examples

```
# inert re-run
$ install.sh all --project-dir /p && install.sh all --project-dir /p
$ find /p -name '*.bak-*' | wc -l
0

# a destination symlinked outside the target
$ ln -s /elsewhere/secret /p/.claude/route-hook.py
$ install.sh claude-code --project-dir /p
$ cat /elsewhere/secret        # unchanged; the LINK was replaced

# refused contradiction
$ install.sh claude-code --legal-corpus no --project-dir /p
ERROR: refusing --legal-corpus no: 16 corpus page(s) are installed at ...
$ echo $?
1

# propose, then place the confirmed list
$ install.sh claude-code --expertise propose --project-dir /p
library-corpus/language/nodejs  package.json: (present)
library-corpus/npm/rxjs  package.json: rxjs
$ install.sh claude-code --expertise library-corpus/npm/rxjs --project-dir /p
$ head -1 /p/docs/graph/libraries/rxjs.md
<!-- origin: corpus@<seed version> id: library-corpus/npm/rxjs -->
```

## 9. Acceptance criteria

- [x] AC-1: every destination is recoverable — maps to BACKUP_BEFORE_REPLACE,
      SINGLE_WRITER
- [x] AC-2: no install modifies a file outside the target — maps to
      SYMLINK_IS_REPLACED_NOT_FOLLOWED
- [x] AC-3: an unchanged plant re-installs with none of the installer's own
      files rewritten and no backup made; the build report still prints, and
      the one write is the self-ignored cache under `.cypress/source-index/`
      in a plant with at least one governed repository, the same bytes when
      nothing moved — maps to
      IDENTICAL_RERUN_IS_INERT (SPEC-0007 INSTALL_RUNS_THE_BUILD holds the
      report and the cache)
- [x] AC-4: every backup is classifiable by the audit — maps to
      EVERY_BACKUP_IS_CLASSIFIABLE
- [x] AC-5: one kernel body regardless of adapter order — maps to
      ONE_KERNEL_BODY, COPY_MODE_ISOLATES, SYMLINK_MODE_IS_UNIFORM
- [x] AC-6: owner decisions survive unrelated installs — maps to
      DECISIONS_SURVIVE_SILENCE, ADAPTERS_ACCUMULATE
- [x] AC-7: the record cannot contradict the disk — maps to
      RECORD_AGREES_WITH_DISK, CORPUS_IS_WHOLE_OR_ABSENT
- [x] AC-8: a bad target is refused before any write — maps to
      PREFLIGHT_REFUSES_BEFORE_WRITING
- [ ] AC-9: an upgrade over a pristine earlier seed kernel files no migration
      work, and a kernel with a plant line is still filed — maps to
      PRISTINE_PRIOR_KERNEL_IS_NOT_MIGRATION
- [ ] AC-10: the graft's re-created-nodes evidence is complete — maps to
      RECREATED_LIST_IS_COMPLETE
- [ ] AC-11: a stamp annotation survives every install — maps to
      UNKNOWN_STAMP_KEYS_SURVIVE
- [ ] AC-12: a grown plant's kernel carries no pre-growth pointer — maps to
      PRE_GROWTH_POINTER_LIVES_IN_THE_PLACEHOLDER_INDEX
- [ ] AC-13: every plant has the anchor tool the hooks call, and no install
      writes an anchor — maps to CODE_ANCHOR_TOOL_IS_PLACED
- [ ] AC-14: every plant receives an unfilled model map, which it then owns;
      maps to MODEL_MAP_TEMPLATE_IS_PLACED
- [ ] AC-15: an opencode agent carries the model the plant's map names, or no
      model line where the map names none; maps to OPENCODE_MODEL_FROM_MAP,
      OPENCODE_NO_MAP_ROW_NO_MODEL_LINE
- [ ] AC-16: a map the installer cannot read stops the opencode projection and
      leaves it as it was; maps to OPENCODE_MAP_UNREADABLE_FAILS_CLOSED
- [ ] AC-17: a seed-only file never reaches a plant; maps to
      SEED_ONLY_FILES_NEVER_PLACED
- [ ] AC-18: a drifted opencode projection, its `model:` line included, is
      reported by `--check`, which writes nothing; maps to
      OPENCODE_CHECK_DETECTS_DRIFT
- [ ] AC-19: a Prime Agent plant carries the same hook scripts as Claude Code,
      beside its extensions; maps to PRIME_HOOK_SCRIPTS_ARE_PLACED
- [ ] AC-20: an owner sees the corpus pages the plant's manifests match before
      anything is written; maps to EXPERTISE_PROPOSAL_WRITES_NOTHING
- [ ] AC-21: exactly the confirmed pages land, each with its provenance, a
      skill page as a routable node, and a bad list writes nothing; maps to
      EXPERTISE_PLACES_ONLY_THE_CONFIRMED_LIST,
      UNKNOWN_EXPERTISE_ID_REFUSED_BEFORE_WRITING,
      PLACED_PAGE_CARRIES_ITS_PROVENANCE, PLACED_SKILL_IS_A_ROUTABLE_NODE
- [ ] AC-22: the placed list is recorded and refreshed by every later install
      without losing a plant edit or replacing a plant page; maps to
      EXPERTISE_IS_RECORDED_IN_THE_STAMP, EXPERTISE_SURVIVES_SILENCE,
      PLANT_EDITED_PAGE_IS_LEFT_AND_NAMED, PLANT_OWNED_PAGE_IS_NEVER_REPLACED,
      and the failure RECORDED_EXPERTISE_PAGE_WITHDRAWN
- [ ] AC-23: `--check` names a recorded page that is missing, stale or
      withdrawn from the seed, and writes nothing; maps to
      EXPERTISE_CHECK_NAMES_MISSING_OR_STALE and the failure
      RECORDED_EXPERTISE_PAGE_WITHDRAWN
- [ ] AC-24: the report, the stamp and the banner agree on the jurisdiction;
      maps to JURISDICTION_RESOLVED_ONCE
- [ ] AC-25: a wired context hook whose script is gone, or that prints
      nothing, fails `--check`; maps to CHECK_EXECUTES_EACH_WIRED_HOOK
- [ ] AC-26: an agent or skill in a harness directory with no graph home is
      named `RETIRED` or `ORPHAN` by `--check` and by the graft audit, and
      an `origin: seed` page under `docs/graph/protocols/` or
      `docs/graph/method/` whose seed source the running seed does not ship
      is named `RETIRED` by its path in the same way; a page the seed still
      ships, or one not marked `origin: seed`, is not named. Nothing is
      deleted, and the flag alone neither fails `--check` nor changes the
      graft audit's exit code. When a retired page repeats a fact-key a
      shipped page owns, the graft run's `graft.gate.routes` row names the
      page, counts the graph-lint error lines that name its `id`, lists that
      `id`, and says each error clears when the steward deletes the page by
      name (`RETIRED_LINT_CLAUSE`); the row still takes graph-lint's verdict
      (BLOCK), an error line that names no retired page is not counted, with
      no such line the clause is absent, and the graft run deletes nothing in
      the plant or its stage; maps to CHECK_FLAGS_RETIRED_HARNESS_ENTRY,
      CHECK_FLAGS_ORPHAN_HARNESS_ENTRY, CHECK_FLAGS_RETIRED_GRAPH_NODE,
      GRAFT_RUN_TIES_LINT_ERRORS_TO_RETIRED_NODES
- [ ] AC-27: a project is offered a `language` page when a manifest declares
      that language in a form a §6 language row names, and a `platform` or
      `cli` page when it holds a trigger a §6 row lists for that page; a
      `pom.xml`, `build.gradle` or `build.gradle.kts` that sets no Java
      language level (an aggregator `pom.xml`) does not bring in
      `language/java`, and only a §6 row is a trigger, so a word in a file
      brings in no page; maps to LANGUAGE_DECLARATION_PROPOSES_ITS_PAGE,
      PACKAGELESS_PAGE_PROPOSED_BY_ITS_TRIGGER
- [ ] AC-28: a project that declares a package a library page lists as its
      own (§6, the own-package list) is offered that page; a project that
      declares only a package the page cites is not, except for a coordinate
      a `maven` page names in its `## What it is` while the own-coordinate
      form stands (§6, §11), and the owner then leaves that page out of the
      list; maps to OWN_PACKAGE_LIST_PROPOSES_ITS_PAGE,
      CITED_PACKAGE_PROPOSES_NOTHING
- [ ] AC-29: a fresh install holds the seed's blank harvest-candidate form
      at `docs/graph/plans/_harvest-candidates.template.md`, byte-identical
      to the seed's, and no `docs/graph/plans/harvest-candidates.md` record;
      after the plant writes its record and edits the form, `install.sh all`
      changes neither and writes no backup beside either; maps to
      HARVEST_CANDIDATE_FORM_IS_PLACED

## 10. Test mapping

| Contract / Failure | Test case | Test file | Level | Status |
|---|---|---|---|---|
| SINGLE_WRITER | M7 sweep over the discovered destination set | tests/test-install-placement.sh | integration | green |
| SINGLE_WRITER | check_install_write_sites — the exception set is exhaustive, by count as well as by shape | tests/seed-lint.py | unit | green |
| BACKUP_BEFORE_REPLACE | M7 sweep | tests/test-install-placement.sh | integration | green |
| SYMLINK_IS_REPLACED_NOT_FOLLOWED | M2 attack over every destination | tests/test-install-placement.sh | integration | green |
| IDENTICAL_RERUN_IS_INERT | M3 churn check (names the churned files) | tests/test-install-placement.sh | integration | green |
| SYMLINK_MODE_IS_UNIFORM | M9 link-uniformity check, inside case_symchurn | tests/test-install-placement.sh | integration | green |
| EVERY_BACKUP_IS_CLASSIFIABLE | M8 audit-totality check: every backup of a real install classifies; the UNMAPPED exit is held by X390's second arm | tests/test-install-placement.sh | integration | green |
| FORCE_SUPPRESSES_WARNING_NOT_BACKUP | M4: --force keeps every backup, and without it the backup is announced | tests/test-install-placement.sh | integration | green |
| ONE_KERNEL_BODY | K1/K4/K5 cases | tests/test-install-kernel-modes.sh | integration | green |
| COPY_MODE_ISOLATES | K2 case | tests/test-install-kernel-modes.sh | integration | green |
| SYMLINK_MODE_IS_UNIFORM | K3 case | tests/test-install-kernel-modes.sh | integration | green |
| DECISIONS_SURVIVE_SILENCE | S1 case | tests/test-plant-state.sh | integration | green |
| ADAPTERS_ACCUMULATE | S2/S5 cases, both orders | tests/test-plant-state.sh | integration | green |
| RECORD_AGREES_WITH_DISK | S6 refusal case | tests/test-plant-state.sh | integration | green |
| CORPUS_IS_WHOLE_OR_ABSENT | S6 whole-corpus case | tests/test-plant-state.sh | integration | green |
| CONTRADICTORY_CORPUS_TRANSITION | S6 refusal leaves disk and record untouched | tests/test-plant-state.sh | integration | green |
| PREFLIGHT_REFUSES_BEFORE_WRITING | D1 inside case_block_declared and case_block_readonly: the preflight refuses before any write (`.claude`-as-a-file, read-only target) | tests/test-install-adoption.sh | integration | green |
| PREFLIGHT_SCOPED_TO_WRITTEN_TREES | D6 case_unrelated_trees: unwritable trees and an escaping directory link outside the written set do not refuse the install, and are unchanged afterwards | tests/test-install-adoption.sh | integration | green |
| SYMLINK_IS_REPLACED_NOT_FOLLOWED | M10 (6) a symlinked DIRECTORY leaving the target is refused, at two paths (an adapter directory and a `docs/graph/` subtree), M10 (7) one staying inside still works — §5's Security NFR and §9 AC-2 rest on this | tests/test-install-placement.sh | integration | green |
| DESTINATION_PATH_OCCUPIED | D1 inside case_block_declared: destination occupied by a non-directory | tests/test-install-adoption.sh | integration | green |
| TARGET_NOT_WRITABLE | D1 inside case_block_readonly: target directory not writable | tests/test-install-adoption.sh | integration | green |
| PARTIAL_CORPUS | (no behavioural test — see §11) | — | — | pending |
| ALL_EXCLUDES_LEGACY_HOSTS | E1 caseALL_EXCLUDES_LEGACY_HOSTS: `all` places three hosts, and the stamp lists exactly those | tests/test-full-install.sh | integration | green |
| LEGACY_INSTALL_PRINTS_DEPRECATED | E2 case_codex, case_github_copilot: one DEPRECATED line naming the tool and ADR-0009; that a maintained host prints none is held by E1 caseALL_EXCLUDES_LEGACY_HOSTS | tests/test-full-install.sh | integration | green |
| LEGACY_INSTALL_STILL_SUCCEEDS | E3 case_codex, case_github_copilot: exit 0, two destinations each, `--print-config` stdout clean | tests/test-full-install.sh | integration | green |
| ALL_NAMES_SKIPPED_FROZEN_HOSTS | S8 caseALL_NAMES_SKIPPED_FROZEN_HOSTS: the skip and its refresh command named, `.codex/` byte-identical, stamp keeps codex | tests/test-plant-state.sh | integration | green |
| FROZEN_PROJECTION_LEFT_STALE | S8 caseALL_NAMES_SKIPPED_FROZEN_HOSTS (the same case holds the warning and the untouched tree) | tests/test-plant-state.sh | integration | green |
| CHECK_WITHOUT_COPILOT_SAYS_SO | D3 caseCHECK_WITHOUT_COPILOT_SAYS_SO: `all --check` exits 0 and says no generated views are in scope, on a target with no record and on a plant whose record carries neither github-copilot nor opencode (`install.sh claude-code codex`) | tests/test-install-adoption.sh | integration | green |
| ALL_CHECK_INCLUDES_RECORDED_COPILOT | D4 caseALL_CHECK_INCLUDES_RECORDED_COPILOT: a Copilot-recording plant is checked by `all --check`, in sync exits 0 with "up to date", drifted exits non-zero with STALE, no not-refreshed warning. The DEPRECATED notice of this run is held by E2 (LEGACY_INSTALL_PRINTS_DEPRECATED) | tests/test-install-adoption.sh | integration | green |
| HOST_TIERS_AGREE | E4 caseHOST_TIERS_AGREE, two rows: the tier arrays and `all` disagree; codex leaves every tier while still dispatched. `check_host_tiers` fails naming `install.sh` | tests/test-seed-lint.sh | unit | green |
| SESSION_RECORD_FORM_IS_PLACED | S9 inside case_plan_records: a fresh `install.sh claude-code` holds `docs/graph/plans/sessions/_session-record.template.md` byte-identical to the seed's form; after a plant record and an edit to the placed form, `install.sh all` leaves both byte-identical, with no backup beside either | tests/test-plant-state.sh | integration | green |
| HARVEST_CANDIDATE_FORM_IS_PLACED | S14 inside case_plan_records: a fresh `install.sh claude-code` holds `docs/graph/plans/_harvest-candidates.template.md` byte-identical to the seed's form and no `harvest-candidates.md`; after a plant `harvest-candidates.md` and an edit to the placed form, `install.sh all` leaves both byte-identical, with no backup beside either; the leak check admits the form by name ; green on the real tree from its first run, because the installer already placed the form, so no RED was seen there; each check was proved instead by mutating a temp copy of the seed (the seed without the form, an installer that does not place it, a placed form one byte off, an install that creates the record, a reinstall that overwrites the edited form, one that backs it up, another seed leaf leaking into `plans/`), and each mutation failed on its own S14 message | tests/test-plant-state.sh | integration | green |
| ENGINE_RECONCILE_PICKS_CONFIG_BY_ENGINE | X383 case_engine_reconcile_stale_grill_lint: a stale `grill-lint.py` (the seed's copy with every line naming `waves` removed), reconciled with no `--preserve`, exits 0, equals the seed's file byte for byte, and leaves one `.bak-*` holding the older body | tests/test-graft-tools.sh | unit | green |
| ENGINE_RECONCILE_PICKS_CONFIG_BY_ENGINE | X384 case_engine_reconcile_spec_lint_keeps_test_globs: a `spec-lint.py` with the plant's own `TEST_GLOBS` and an older body, reconciled with no `--preserve`, exits 0, keeps the plant's `TEST_GLOBS` and adopts the seed's body | tests/test-graft-tools.sh | unit | green |
| ENGINE_RECONCILE_PICKS_CONFIG_BY_ENGINE | X385 case_engine_reconcile_explicit_preserve_wins: `--preserve=ROOT_ID` on a `graph-lint.py` whose plant changed `ROOT_ID` and `KIND_PREFIX` keeps the plant's `ROOT_ID` and takes the seed's `KIND_PREFIX`; guard | tests/test-graft-tools.sh | unit | green |
| ENGINE_RECONCILE_PICKS_CONFIG_BY_ENGINE | X386 case_engine_reconcile_other_name_takes_graph_lint_set: the same plant file named `project-lint.py`, reconciled with no `--preserve`, exits 0 and keeps both `ROOT_ID` and `KIND_PREFIX`; guard | tests/test-graft-tools.sh | unit | green |
| ENGINE_AUDIT_CHECKS_EVERY_PAIR | X387 case_engine_audit_one_line_per_pair: `graft-audit.py` with two `--engine` pairs, a current `graph-lint.py` and a stale `grill-lint.py`, prints two engine-currency lines, the current one naming `graph-lint.py` and the `graph engine STALE` one naming `grill-lint.py` | tests/test-graft-tools.sh | unit | green |
| ENGINE_AUDIT_CHECKS_EVERY_PAIR | X388, a row inside X389: a current pair then a malformed one exits non-zero and says `--engine wants <plant-file>:<seed-file>`, where the current pair alone exits 0; guard | tests/test-graft-tools.sh | unit | green |
| ENGINE_AUDIT_CHECKS_EVERY_PAIR | X389 case_engine_audit_malformed_first_pair_fails: a malformed pair then a current one exits non-zero and says `--engine wants <plant-file>:<seed-file>` | tests/test-graft-tools.sh | unit | green |
| EXISTING_PLANT_RECEIVES_CURRENT_ENGINES | S10 case_engine_upgrade: re-install leaves the older `grill-lint.py`. The reconcile half is held by X383 and the audit half by X387, both in `tests/test-graft-tools.sh` | tests/test-plant-state.sh | integration | green |
| ENGINE_LEFT_STALE_BY_GRAFT | X387 case_engine_audit_one_line_per_pair: the stale pair's `graph engine STALE` line names `grill-lint.py`, beside the current pair's line | tests/test-graft-tools.sh | unit | green |
| PRISTINE_PRIOR_KERNEL_IS_NOT_MIGRATION | K7 case_k7_prior_kernel_fast_forwards: a kernel byte-identical to `core/AGENTS.md` at an earlier commit of a temp `git clone --local` of the seed is replaced with one backup holding it, no adopted-instructions row for that backup, no `OVERWRITTEN` line, a log line naming an earlier seed kernel; a second run files no row | tests/test-install-kernel-modes.sh | integration | green |
| PRISTINE_PRIOR_KERNEL_IS_NOT_MIGRATION | K7 case_k7_sweep_skips_prior_kernel_backup: a `CLAUDE.md.bak-*` holding an earlier seed kernel beside an installed plant gets no row from the next run's orphan sweep | tests/test-install-kernel-modes.sh | integration | green |
| PRISTINE_PRIOR_KERNEL_IS_NOT_MIGRATION | K7 case_k7_plant_line_is_still_filed: an earlier seed kernel with one plant line added is filed and announced `OVERWRITTEN`; guard | tests/test-install-kernel-modes.sh | integration | green |
| SEED_HISTORY_UNAVAILABLE | K7 case_k7_no_history_falls_back: from a seed copy with no `.git`, an earlier seed kernel is filed for migration and exactly one log line names the missing history | tests/test-install-kernel-modes.sh | integration | green |
| RECREATED_LIST_IS_COMPLETE | D5 case_d5_recreated_list: twelve deleted protocol nodes re-created; `.cypress/recreated-nodes.txt` holds the §6 header (checked by its prefix) and all twelve paths, sorted and unique; the console prints ten and names the file | tests/test-install-adoption.sh | integration | green |
| RECREATED_LIST_IS_COMPLETE | D5 case_d5_fresh_list, the first check of case_d5_recreated_list: a first install writes `.cypress/recreated-nodes.txt` with the §6 header alone (checked by its prefix); guard, red under a mutant that records nodes on a first install | tests/test-install-adoption.sh | integration | green |
| RECREATED_LIST_IS_COMPLETE | D5 case_d5_recreated_list, third check: after the run that re-created twelve nodes, a run that re-creates nothing rewrites the file with the header line alone | tests/test-install-adoption.sh | integration | green |
| UNKNOWN_STAMP_KEYS_SURVIVE | S11 case_stamp_keys: a string key and an object key the installer does not own survive `install.sh all` JSON-equal, in their original order, after the installer's keys; `legal_corpus` and `tools` keep their own rules | tests/test-plant-state.sh | integration | green |
| STAMP_NOT_AN_OBJECT | S11 case_stamp_keys, second arm: a stamp that is a JSON array is moved to a `seed.json.bak-*`, a stamp is written from the installer's keys, one line names the backup. The arm runs after the first, so its red is not observed until the first arm is green | tests/test-plant-state.sh | integration | green |
| STAMP_NOT_AN_OBJECT | S12 inside case_s7: a stamp that does not parse (cut off inside a field; bytes that are not UTF-8) is not the trigger: the run exits non-zero with the preflight's refusal line, the stamp is byte-identical, no `seed.json.bak-*` is made, the file listing is unchanged. The truncated arm is a guard; the not-UTF-8 arm is red: the preflight's reader stops on a Python traceback, not its refusal | tests/test-plant-state.sh | integration | green |
| PRE_GROWTH_POINTER_LIVES_IN_THE_PLACEHOLDER_INDEX | E5 case_pre_growth_pointer, first check: a fresh `install.sh claude-code` gives `docs/graph/index.md` one pre-growth block, delimited as §6 gives, naming `EXPERT_SEED_INSTALL_PROMPT.md` and `protocol.initialize` | tests/test-full-install.sh | integration | green |
| PRE_GROWTH_POINTER_LIVES_IN_THE_PLACEHOLDER_INDEX | E5 case_pre_growth_pointer, second check: the placed `CLAUDE.md` names neither `EXPERT_SEED_INSTALL_PROMPT.md` nor `protocol.initialize` | tests/test-full-install.sh | integration | green |
| PRE_GROWTH_POINTER_LIVES_IN_THE_PLACEHOLDER_INDEX | E5 case_pre_growth_pointer, third check: a re-install over an index with no pre-growth block leaves it byte-identical; guard | tests/test-full-install.sh | integration | green |
| CODE_ANCHOR_TOOL_IS_PLACED | E6 case_code_anchor_tool: a fresh `install.sh all` places `docs/graph/code-anchor.py` byte-identical to `tools/code-anchor.py` and writes no `.cypress/anchor.json`. The second check, a re-install over an older copy leaving a backup, is held by the M7 sweep of `tests/test-install-placement.sh`, whose discovered destination set holds the tool | tests/test-full-install.sh | integration | green |
| EVERY_BACKUP_IS_CLASSIFIABLE | X390 case_audit_plant_agent_projection (GA-C3): a `.claude/agents/<name>.md` backup whose plant node `docs/graph/agents/<name>.md` has `origin: project` is not UNMAPPED and the audit exits 0; a projection backup with no seed source and no plant node stays UNMAPPED, exit 1 | tests/test-graft-tools.sh | unit | green |
| EVERY_BACKUP_IS_CLASSIFIABLE | X391, a row of X390: a `.claude/skills/<name>/SKILL.md` backup whose plant node `docs/graph/skills/<name>.md` has `origin: project` is not UNMAPPED and the audit exits 0; a skill projection backup with no plant node stays UNMAPPED, exit 1 | tests/test-graft-tools.sh | unit | green |
| EVERY_BACKUP_IS_CLASSIFIABLE | X392, a row of X390: a `.github/agents/<name>.agent.md` backup whose plant node `docs/graph/agents/<name>.md` has `origin: project` is not UNMAPPED and the audit exits 0; a Copilot agent view backup with no seed agent and no plant node stays UNMAPPED, exit 1 | tests/test-graft-tools.sh | unit | green |
| MODEL_MAP_TEMPLATE_IS_PLACED | E7 case_model_map_placed: a fresh `install.sh claude-code` holds `docs/graph/models.md` byte-identical to `templates/docs/models.md`; after a plant edit to it, `install.sh all` leaves it byte-identical with no backup beside it; guard: the existing scaffold walk places the template, so the case passes on arrival once `templates/docs/models.md` exists, and is held by the mutant that deletes that template | tests/test-full-install.sh | integration | green |
| OPENCODE_MODEL_FROM_MAP | E8 case_opencode_model_from_map: a map filling the opencode cells of the authoring-high and investigation-medium rows, then `install.sh opencode`: an opus/high agent and a sonnet/medium agent each equal their graph home with only the `model:` line replaced by the cell; under `--symlink` the projection is a regular file; the stamp's opencode entry is `"verbatim": false`; a plant agent with `model: haiku` and `effort: high` gets the investigation-low cell | tests/test-full-install.sh | integration | green |
| OPENCODE_NO_MAP_ROW_NO_MODEL_LINE | E9 case_opencode_no_map_row: a fresh `install.sh opencode` exits 0 and every projection equals its graph home with the `model:` line removed; stdout has one line naming `docs/graph/models.md` and the count; with other rows filled, an agent whose row is `-`, one whose row is missing and a plant agent with `model: inherit` carry no `model:` line, a plant agent with `model: provider-q/model-q` keeps that value (copied as is), and stdout has exactly one line `opencode: <n> of <total> agents carry no model: line`, where the two numbers differ | tests/test-full-install.sh | integration | green |
| OPENCODE_MAP_UNREADABLE_FAILS_CLOSED | E10 case_opencode_map_unreadable: over an installed opencode plant whose authoring-high cell is filled and projected, a change to that cell plus a map row with class `premium` makes `install.sh opencode` exit non-zero with stderr naming `docs/graph/models.md`; every `.opencode/agents/*.md` is byte-identical to the snapshot taken before the run and no new `.bak-*` is beside any, so a run that projects before it refuses fails the case | tests/test-full-install.sh | integration | green |
| MODEL_MAP_UNREADABLE | E10 case_opencode_map_unreadable (the same case holds the refusal and the untouched projections) | tests/test-full-install.sh | integration | green |
| OPENCODE_SELECTOR_UNRESOLVED | (no behavioural test: the installer has no host catalog to check a cell against; §7) | — | — | pending |
| OPENCODE_CHECK_DETECTS_DRIFT | E11 case_opencode_check_drift: over an opencode plant with a filled authoring-high cell, `install.sh opencode --check` exits 0 and says up to date; after a hand edit to one projection, and after a cell edit with no re-run, it exits non-zero naming the stale projections; `install.sh all --check` fails the same way; the plant's file digest is unchanged by every run | tests/test-full-install.sh | integration | green |
| MODEL_MAP_UNREADABLE | E11 case_opencode_check_drift, its last arm: a map row with class `premium` makes `install.sh opencode --check` exit non-zero with stderr naming `docs/graph/models.md` | tests/test-full-install.sh | integration | green |
| SEED_ONLY_FILES_NEVER_PLACED | X393 check_seed_only_stays_home: a copied `manifest.json` whose `tools` map gains `tools/prepare-release.py` is a finding naming that path as a seed-only file | tests/test-seed-lint.sh | unit | green |
| SEED_ONLY_FILES_NEVER_PLACED | X394 check_seed_only_stays_home: a copied `install.sh` that places a file from `$SEED_ROOT/docs/` that is not itself seed-only (`docs/decisions/index.md`) is a finding naming `install.sh` that says it sources a file under `$SEED_ROOT/docs` | tests/test-seed-lint.sh | unit | green |
| SEED_ONLY_FILES_NEVER_PLACED | X395 check_seed_only_stays_home: a copied `manifest.json` whose `tools` map drops `tools/code-anchor.py`, which `install.sh` places, is a finding naming `manifest.json` | tests/test-seed-lint.sh | unit | green |
| PRIME_HOOK_SCRIPTS_ARE_PLACED | E12 case_prime_hook_scripts_placed: a fresh `install.sh prime-agent --copy` places `.prime/agent/hooks/route-hook.py` and `status-hook.py` byte-identical to `integrations/claude-code/`; `adapter_dirs prime-agent` names `.prime/agent/hooks`; a re-install over an older copy replaces it with a `.bak-` backup; no `.claude/` is created | tests/test-full-install.sh | integration; red on arrival (nothing placed under `.prime/agent/hooks/`); the no-`.claude/` arm passes today | green |
| REINSTALL_ENGINE_SERVES_THE_HOOKS | E13 case_reinstall_engine_serves_hooks: over a `claude-code --copy` plant whose engine is the `v7.36.0` graph-lint.py with `plantkind` added to `KINDS` and `KIND_PREFIX = {"plantkind": "pk"}`, and older hook scripts, a plain `install.sh claude-code --copy`: (a) the engine is byte-unchanged; (b) the placed route-hook's first-prompt injection is the pointer line and one notice line naming `graph-lint.py`, `--plan-json` and `graft`; then `tools/graft-graph-engine.py` on the engine: (c) it accepts `--plan-json`, the hook injects `Router suggestion`, and `KINDS` holds `plantkind` and `KIND_PREFIX` equals the plant's | tests/test-full-install.sh | integration; red on arrival in (b) only (the hook has no notice path); (a) and (c) pass today, guards: (a) against an installer that touches the engine, (c) against a reconcile that copies the seed engine wholesale | green |
| EXPERTISE_PROPOSAL_WRITES_NOTHING | M15 case_expertise_propose: over the synthetic manifests, `install.sh claude-code --expertise propose` exits 0 and prints the §6 lines for a Maven, an npm and a stack-keyed skill match; the target is byte-identical and carries no `.cypress/`, kernel or adapter; M16 holds that `corpus-match.py` is not placed | tests/test-install-placement.sh | integration; red on arrival (`unknown argument: --expertise`) | green |
| EXPERTISE_PROPOSAL_WRITES_NOTHING | test_proposes_every_ecosystem_and_its_stack_pages | tests/test_corpus_match.py | unit; red on arrival (`tools/corpus-match.py` did not exist) | green |
| EXPERTISE_PROPOSAL_WRITES_NOTHING | test_empty_proposal_is_never_silent | tests/test_corpus_match.py | unit; red on arrival (`tools/corpus-match.py` did not exist) | green |
| EXPERTISE_PROPOSAL_WRITES_NOTHING | test_scratch_copies_and_foreign_dirs_are_not_read; at the tip it also writes a manifest under each agent host's directory (`.opencode`, `.claude`, `.codex`, `.prime`) | tests/test_corpus_match.py | unit; red on arrival (the walk read a `.bak-` copy, a graft backup, a `.tmp/` copy and a nested plant); the host arms added at the tip, proved by a reverted mutation that read `.claude`, `.codex` and `.prime` | green |
| EXPERTISE_PROPOSAL_WRITES_NOTHING | test_manifest_rules_propose_their_pages: one project built in the test holds the maven starter and own-coordinate rule, the Dockerfile and Containerfile rules (a `dotnet/` image included), the azure-pipelines file and the dotnet-tools manifest; consolidated 2026-10-05 from four cases, each red on arrival in its own round | tests/test_corpus_match.py | unit | green |
| LANGUAGE_DECLARATION_PROPOSES_ITS_PAGE | test_seed_pages_are_proposed_by_their_triggers: the eight Java-level forms (five pom.xml, two toolchain builds, source/targetCompatibility), two dart rows and Flutter beside Dart, and AC-27's no-level pom guard; consolidated 2026-10-05 | tests/test_corpus_match.py | unit | green |
| OWN_PACKAGE_LIST_PROPOSES_ITS_PAGE | test_page_matches_the_packages_it_lists_as_its_own_in_any_ecosystem | tests/test_corpus_match.py | unit, the synthetic own-list subtests (`@comet/core`, `comet-rx`, `loom.extras`); the seed pages' rows (`@stomp/stompjs`; `bloc`, `bloc_test`) are in test_seed_pages_are_proposed_by_their_triggers since the 2026-10-05 consolidation, and `@stomp/rx-stomp`, `sockjs-client`, `stompjs` were cut as list data | green |
| CITED_PACKAGE_PROPOSES_NOTHING | test_page_matches_the_packages_it_lists_as_its_own_in_any_ecosystem | tests/test_corpus_match.py | unit, the guard subtest: `tslib`, `nanoid`, `@popperjs/core` and `pdfjs-dist`, each cited in the `## What it is` prose of `npm/rxjs`, `npm/postcss`, `npm/bootstrap` and `npm/ng2-pdf-viewer`, propose none of them; green on arrival, so the GREEN proved it by a reverted mutation that reads every backticked name of the section (the guard and two synthetic citation subtests went red, then green on revert); the row reads the case | green |
| PACKAGELESS_PAGE_PROPOSED_BY_ITS_TRIGGER | test_seed_pages_are_proposed_by_their_triggers: proxmox-ve by `community.proxmox` and `proxmoxer`, bitbucket-pipelines by its file, trivy by a compose image, a CI step image, its action and `trivy.yaml`, gitleaks by a compose image, its action, `.gitleaks.toml` and hook id `gitleaks-docker`; consolidated 2026-10-05, the alternate names cut as list data | tests/test_corpus_match.py | unit | green |
| OWN_PACKAGE_NAMED_ONLY_IN_PROSE | (no behavioural test: the failure is a page author's; the matcher's half of it is CITED_PACKAGE_PROPOSES_NOTHING's guard) | — | — | pending |
| EXPERTISE_PLACES_ONLY_THE_CONFIRMED_LIST | M16 case_expertise_place: a confirmed list of a library, a skill, a tool and an unmatched `platform`-key page places exactly those four and nothing under `docs/graph/legal/corpus/` | tests/test-install-placement.sh | integration; red on arrival (`unknown argument: --expertise`) | green |
| UNKNOWN_EXPERTISE_ID_REFUSED_BEFORE_WRITING | M17 case_expertise_refused: a misspelt id, a `legal-corpus/` and an `agent-corpus/` id, an id holding `..`, an absolute path, a flat skill page, two ids with one destination, a skill id landing on the seed's own `skills/test-first` node and a library id landing on the `libraries/index.md` scaffold leaf (the last two added at the tip) are each refused by name with no Python error and the target byte-identical; over a plant recording `library-corpus/pypi/swift-cache`, listing `library-corpus/container/swift-cache` is refused by name with the plant byte-identical (the architect's condition) | tests/test-install-placement.sh | integration; red on arrival (`unknown argument: --expertise`) | green |
| PLACED_PAGE_CARRIES_ITS_PROVENANCE | M16 case_expertise_place: the placed library and tool pages open with the §6 provenance line carrying the stamp's `version`, and every later byte equals the corpus page; M18 case_expertise_silence: `graft-audit.py` counts the refreshed page's backup `CORPUS-PLACED`, with no `UNMAPPED` backup and no knowledge overwrite | tests/test-install-placement.sh | integration; red on arrival (`unknown argument: --expertise`); the audit arm red until `graft-audit.py` read `origin: corpus@` | green |
| PLACED_SKILL_IS_A_ROUTABLE_NODE | M16 case_expertise_place: `docs/graph/skills/lumen-upgrade.md` equals its stack-keyed corpus page plus the `origin: corpus@<version>` line, `graph-lint.py --show skill.lumen-upgrade` exits 0 and prints it, and `.claude/skills/lumen-upgrade/SKILL.md` exists | tests/test-install-placement.sh | integration; red on arrival (`unknown argument: --expertise`) | green |
| EXPERTISE_IS_RECORDED_IN_THE_STAMP | M16 case_expertise_place: the stamp's `expertise` key holds the four ids sorted, each with its placed path and the SHA-256 of the file on disk; M18 holds that a key the installer does not own survives after it | tests/test-install-placement.sh | integration; red on arrival (`unknown argument: --expertise`) | green |
| EXPERTISE_SURVIVES_SILENCE | M18 case_expertise_silence: a silent re-run makes no backup and keeps the record; a newer corpus page is placed with a backup and its recorded hash updated, an unchanged page is not backed up; a recorded page the plant deleted is placed again and named | tests/test-install-placement.sh | integration; red on arrival (`unknown argument: --expertise`) | green |
| PLANT_EDITED_PAGE_IS_LEFT_AND_NAMED | M19 case_expertise_plant_edits: an edited placed page is byte-identical after a silent run and after a run listing its id, with no backup beside it, one line naming it and graft Phase 4, and its record entry unchanged | tests/test-install-placement.sh | integration; red on arrival (`unknown argument: --expertise`) | green |
| PLANT_OWNED_PAGE_IS_NEVER_REPLACED | M19 case_expertise_plant_edits: the plant's own `docs/graph/libraries/ripple.md` is left byte-identical with no backup and named for graft Phase 4, no entry is recorded for it, and the other listed id is placed and recorded | tests/test-install-placement.sh | integration; red on arrival (`unknown argument: --expertise`) | green |
| EXPERTISE_CHECK_NAMES_MISSING_OR_STALE | M20 case_expertise_check: a plant with no `expertise` key gets no expertise line; a current plant passes with the up-to-date line; a stale and a missing page fail `--check`, each named, with the plant byte-identical; a plant-edited page alone exits 0 and is named for graft Phase 4 | tests/test-install-placement.sh | integration; red on arrival (`unknown argument: --expertise`) | green |
| EXPERTISE_MANIFEST_UNREADABLE | M15 case_expertise_propose: a `package.json` that is not JSON is named with its reason, the other manifests still match, exit 0, target byte-identical | tests/test-install-placement.sh | integration; red on arrival (`unknown argument: --expertise`) | green |
| EXPERTISE_MANIFEST_UNREADABLE | test_unreadable_manifest_is_named_and_skipped | tests/test_corpus_match.py | unit; red on arrival (`tools/corpus-match.py` did not exist) | green |
| RECORDED_EXPERTISE_PAGE_WITHDRAWN | M18 case_expertise_silence: with the seed's page removed, a plain install exits 0 with a `WARNING` naming the id and leaves the page and its entry; after the plant deletes the page the next run does not place it and keeps the entry; `--check` names the id and exits non-zero | tests/test-install-placement.sh | integration; red on arrival (`unknown argument: --expertise`) | green |
| JURISDICTION_RESOLVED_ONCE | S13 case_jurisdiction_resolved_once: over a plant stamped `legal_corpus: yes`, `legal_jurisdiction: it`, a re-install with no flag prints no "jurisdiction undecided" line and no "no --legal-jurisdiction given", the national-layer report names `'it'` and the stamp keeps it; a re-install with `--legal-jurisdiction fr` names `'fr'`, not `'it'`, and the stamp records `fr`; a plant with no recorded code and no flag still prints the undecided banner | tests/test-plant-state.sh | integration; red on arrival (the no-flag re-install printed the undecided banner) | green |
| CHECK_EXECUTES_EACH_WIRED_HOOK | M12 case_hook_check: over a copy of the every-host install, `claude-code --check` exits 0, keeps CHECK_WITHOUT_COPILOT_SAYS_SO's line, prints a ran line for the two Claude Code and the two Prime Agent hooks, and leaves the tree byte-identical; with `.claude/route-hook.py` removed it exits non-zero naming `UserPromptSubmit .claude/route-hook.py`; over a copy of the Copilot-only install with `.github/hooks/status-hook.py` removed, `github-copilot --check` exits non-zero naming `SessionStart .github/hooks/status-hook.py` | tests/test-install-placement.sh | integration; red on arrival (no ran line: `--check` ran no hook) | green |
| CHECK_FLAGS_RETIRED_HARNESS_ENTRY | M13 case_retired_flag: over a copy of the every-host install carrying an `origin: seed` `docs/graph/skills/from-scratch-bootstrap.md` the seed does not ship and its `.claude/skills/` projection, plus an `origin: seed` `.claude/agents/legacy-steward.md` with no graph node (added at the tip), `graft-audit.py` keeps its clean-copy exit code and names the lone agent `RETIRED`, and `claude-code --check` exits 0, names all three `RETIRED` and leaves the tree byte-identical; after the projection gains a line and a re-install backs it up, `graft-audit.py` counts the backup `RETIRED`, reports no `UNMAPPED` backup and names the projection `RETIRED`; both entries are still on disk | tests/test-install-placement.sh | integration; red on arrival (`--check` printed no harness line, not even over the clean copy) | green |
| CHECK_FLAGS_ORPHAN_HARNESS_ENTRY | M14 case_orphan_flag: over a copy of the every-host install, `claude-code --check` says every harness entry has a graph home (inside M13); with a skill in `.claude/skills/deploy-notes/` and an agent in `.prime/agent/agents/` and no graph node, it exits 0, names each `ORPHAN` with the graph home it lacks and leaves the tree byte-identical; `graft-audit.py` names the skill `ORPHAN` with its clean-copy exit code (asserted since the tip) | tests/test-install-placement.sh | integration; red on arrival (`--check` did not name the orphan skill) | green |
| CHECK_FLAGS_RETIRED_GRAPH_NODE | M13 case_retired_flag, graph-node arm (8.1.2, graft finding F1): the every-host install copy also carries an `origin: seed` `docs/graph/protocols/<name>.md` the seed does not ship and an `origin: project` protocol of another name: `claude-code --check` exits 0, names the seed one `RETIRED` and not the project one, and leaves the tree byte-identical; `graft-audit.py` names it `RETIRED` with its clean-copy exit code; the node is still on disk | tests/test-install-placement.sh | integration | red |
| GRAFT_RUN_TIES_LINT_ERRORS_TO_RETIRED_NODES | X469 case_run_ties_lint_errors_to_retired_nodes, a GR case of `tools/graft-run.py` (8.1.2, graft finding F1): a synthetic plant carrying an `origin: seed` `docs/graph/protocols/<name>.md` the seed does not ship, whose `owns:` repeats a fact-key of a seed skill node: the `graft.gate.routes` row is BLOCK, names the path among the `RETIRED` entries and carries `RETIRED_LINT_CLAUSE` with the node's id and a count of 1; arm: the same node with that fact-key dropped from its `owns:` carries no clause; the node is on disk after the run | tests/test-graft-tools.sh | integration (synthetic plant) | red |

Coverage note, so the table is not read as more than it is.

**The engine rows (7.31.0).** Every case of `tests/test-graft-tools.sh`, X383
to X389 among them, runs under one collector, so each label shows its own
result in one run. A row marked guard passes on the unmodified tools and is held
by a named mutant instead of an observed red: X385 by an explicit `--preserve`
ignored, X386 by an unknown engine name given no preserve set, X388 by a later
malformed pair skipped. EXISTING_PLANT_RECEIVES_CURRENT_ENGINES is held in
two halves: S10 `case_engine_upgrade` in `tests/test-plant-state.sh` holds the
re-install, and X383 and X387 hold the reconcile and the audit.

**The 7.32.0 rows.** K7, D5, S11, E5 and E6 are the RED of the five
contracts and two failures promoted from the 7.32.0 pending block. K7's four
cases run in one collecting block at the end of
`tests/test-install-kernel-modes.sh`, so each shows its own result; the other
suites run each case as its own scenario. E5, E6 and D5 are one scenario per
contract, and each check in it reports its own result. A row marked guard passes on the
unmodified installer. K7's seed is a temp clone of the real seed; when the
checkout is shallow and holds no earlier kernel, the clone gains an earlier
body and the current one as two commits, so the case still has a history to
walk.

**The 7.35.0 rows.** E7 to E11 and X393 to X395 were written ahead of their
RED (adr-0021, adr-0022). E7 is a guard, `green` on arrival, because placing
the template needs no installer change. Every other row was `red` until the
tester's case landed and showed its failure on the tree it was written against;
the label is written as a comment inside its case, beside the slug. All of them
turned green in the round's GREEN wave (increments 19 and 21). E8 to E11
run in `tests/test-full-install.sh`, and the M9 exception list of
`tests/test-install-placement.sh` (`is_generated`) gained `.opencode/agents/*`
in the same RED, because `SYMLINK_MODE_IS_UNIFORM` already exempts generated
content and the opencode projections are generated. D3's second arm moved
its setup from `install.sh all codex` to `install.sh claude-code codex` in the
same RED: `all` records opencode, which `--check` checks, so the old setup
would no longer be a plant with no views in scope. The edited arm is green
before and after the installer change. The one `pending` failure row,
OPENCODE_SELECTOR_UNRESOLVED, has no test by design: it needs a host catalog
the installer does not have.

**The 8.0.0 rows.** The twelve contracts and two failures of the 8.0.0
entry in §12 were written ahead of their RED, each row `pending` until the
increment it names landed its case. The selective-placement rows landed with
increment 13: M15 to M20 in `tests/test-install-placement.sh` install from a
copy of the seed whose three corpora are replaced by the synthetic subset
under `tests/fixtures/corpus-placement/seed`, into a copy of the synthetic
manifests beside it, never a real plant's; the matcher's own cases are in
`tests/test_corpus_match.py`. Each case was run and seen failing before the
installer, the matcher or the audit changed.

**The matcher increment rows (2026-10-05).** The five cases of the
increment match against the seed's own `library-corpus/`, while the older
matcher cases use the fixture subset. Each new case holds a trigger or an
own-package list that a named corpus page states, so a renamed page or a
dropped list item fails here, which is the intent: the list is a contract
between the page and the matcher. The projects stay synthetic and are built
in the test. The assertions are by id and by the evidence's manifest prefix,
so the corpus can grow under them. The GitHub Action and the
`bitbucket-pipelines.yml` step-image subtests went past the brief's examples,
and they are in scope by the architect's decision: the trivy and gitleaks
pages name the action and the pipeline as the channels that decide the
version a project runs. The tester added the two arms of §6 the first
cases lacked, the Gradle `sourceCompatibility` and `targetCompatibility`
form and a `pom.xml` that sets no language level, and named the four new
contracts in the five cases' docstrings, which `spec-lint.py` reads for
coverage and `seed-lint` requires before a row turns `green`. The
unreachable pages of §6 have no case, by decision, and neither has the
own-coordinate form's false positive (CITED_PACKAGE_PROPOSES_NOTHING's
Except), which a case would freeze into the corpus.

**M1 shares a label with a different invariant.** `tests/test-install-placement.sh`
carries cases headed `M1 completeness` and exits `M1 VIOLATED`, but what they
assert is that every machinery node the seed owns *arrives* in the plant — not
this spec's M1 (one canonical write mechanism). `seed-lint`'s
`check_spec_test_mapping` only greps for the label, so the divergence passes.
Read the two as separate claims until one is renamed; this spec's M1 is covered
the way M5 is, below.

**M5** (generated and copied files share destination safety) has no test of its
own and needs none: the M7 and M2 sweeps run over the destination set
*discovered* from a real install, which includes every generated file, so a
bypass or an unsafe generated write fails them by construction. This spec's M1
is covered by the same sweeps, for the same reason.

**M6** (generation completes before replacement) has no regression — proving it
needs a fault injected mid-generation, which is the same missing harness §11
records for PARTIAL_CORPUS.

**M10** (no write escapes PROJECT_DIR) is enforced by
`tests/test-install-placement.sh`'s target-containment case and is the
mechanism behind AC-2 and the §5 security NFR, both of which map only to the
narrower M2 above.

## 11. Open questions

| Question | Why it matters | Current assumption | Owner | Resolves by |
|---|---|---|---|---|
| PARTIAL_CORPUS has no regression | The check was corrected from `-ge` over files to `-eq` over pages, but `place_tree` never fails partway, so no public-interface sequence produces the partial corpus the old check waved through | The correction is right and untested; it becomes testable when placement can fail mid-tree (ENOSPC, permission fault) | seed-installer | a fault-injection harness, if one is ever justified |
| How does an owner drop a page from the `expertise` record? | EXPERTISE_IS_RECORDED_IN_THE_STAMP never removes an id, and EXPERTISE_SURVIVES_SILENCE places a deleted page again, so a page the plant has dropped returns on every install | None this round: the record only grows; the owner edits the stamp by hand, which the installer then honours | seed-installer | the first plant that withdraws a placed page |
| When do the `maven` pages move to the own-package list? | The own-coordinate form (§6) reads every backticked coordinate in `## What it is`, so a coordinate a page only cites there proposes it (the mysql-connector-j page and a MariaDB driver entry), the exception CITED_PACKAGE_PROPOSES_NOTHING and AC-28 state | The form stays for `maven` pages; their authors cite a coordinate they do not own in a later section, and the owner leaves a wrongly proposed page out of the list | seed-installer | a docs pass that writes every `maven` page's own coordinates as an own-package list; the matcher then drops the form, with its case |
| When are the pages that name their own sibling packages only in prose converted to the own-package list? | A project that declares only a sibling package is not offered the page (OWN_PACKAGE_NAMED_ONLY_IN_PROSE), so that plant pays for a research-scout run the page exists to save, and no line of the proposal reports the miss | A docs pass converts each such page it reaches; until then the owner lists the missed id by hand | seed-installer | a corpus page-shape check that names each library page whose `## What it is` carries no own-package list, or the last such page converted |
| Should a Gradle build's dependencies match `maven` pages? | A Gradle project gets no library page proposed from its build; only its Java language level is read (§6) | No, this increment reads a Gradle build for its language level only | seed-installer | the first Gradle plant whose proposal misses a library it declares |
| How is `language/java` reached when the language level comes from a parent outside the project? | The declaration rule (§6) proposes nothing for a build that inherits its level, though the project is Java | The owner lists `language/java` by hand; a JDK runtime image rule (`eclipse-temurin`, `openjdk`) is the candidate fix, as the java page puts the runtime build in the base image | seed-installer | the first plant whose proposal misses `language/java` |
| Should the matcher read a lockfile's transitive entries? | A direct dependency names what the plant calls; a transitive one names what it carries, and a page for it is noise in the plant's routing | No: direct dependencies only (§6) | seed-installer | the first proposal that misses a library the plant calls through a transitive entry |

## 12. Changelog

This section did not exist before 2026-09-16. It was added with the entry
below rather than the correction being made silently, because a spec that is
edited to match the code without saying so is the drift kernel §4 forbids.
The file carries no version field; `status_date` in the frontmatter is the
only version surface it has, and it moves with each entry here.

- 2026-09-13 — written as `back-written` over existing installer behaviour.
  Sign-offs recorded as not owed; see §0.
- 2026-09-16 — §5 **Compatibility** corrected. The line read "POSIX shell and
  `python3` only", which was false about the code: `install.sh:1` is
  `#!/usr/bin/env bash` and `:69` uses `set -euo pipefail`, whose `pipefail`
  POSIX's `set` does not define, and all 30 shell files in this tree declare a
  bash shebang. Per the kernel's rule that a spec is never silently changed to
  match code, this is the SPEC being wrong about the code: the claim was
  corrected deliberately, `status_date` moved to this date, and the original
  wording is quoted above so the correction is not silently absorbed. No
  contract in §4, no data shape in §6 and no failure mode in §7 changed. The
  bash-versus-POSIX distinction itself is owned by a grown plant's
  `docs/graph/best-practices/bash.md` §"Two floors, not one" and is linked,
  not restated.
- 2026-09-23: host support tiers,
  [ADR-0009](../decisions/adr-0009-host-support-tiers.md). §2 and §3 name
  which hosts `all` installs; §4 gains six contracts written ahead of the code,
  with their RED at `9ca5900` (ALL_EXCLUDES_LEGACY_HOSTS,
  LEGACY_INSTALL_PRINTS_DEPRECATED, LEGACY_INSTALL_STILL_SUCCEEDS,
  ALL_NAMES_SKIPPED_FROZEN_HOSTS, CHECK_WITHOUT_COPILOT_SAYS_SO,
  HOST_TIERS_AGREE); §7 gains FROZEN_PROJECTION_LEFT_STALE; §10 binds each to
  its case. No existing contract changed. The status stays `back-written`
  for now: `active` needs product, architect and tester sign-offs under
  spec-lint, none is recorded for this increment, and §0 already records what
  a sign-off written to satisfy the linter did to this spec once before.
- 2026-09-23: review fixes, RED at `dd3e65c`. §4 gains
  ALL_CHECK_INCLUDES_RECORDED_COPILOT: `all --check` checks the Copilot views
  of a plant whose record carries github-copilot, so a CI job that ran it
  before 7.27.0 still fails on drift, and the DEPRECATED notice fires for that
  run because it acts on a frozen host. CHECK_WITHOUT_COPILOT_SAYS_SO's Given
  narrows from any target to a target whose record lacks github-copilot; the
  earlier Given blessed an exit 0 that hid a real check. HOST_TIERS_AGREE
  gains the duplicate-row, dispatchable-tool and `EVERY_HOST` clauses. §7
  FROZEN_PROJECTION_LEFT_STALE now says what the code prints, one `WARNING`
  line per host, and excludes a host the run checks. `status_evidence` names
  the two suites that already held contracts here and were missing from it.
  The status stays `back-written`; the owner decision in the entry above is
  still pending.
- 2026-09-23: review minor m1. HOST_TIERS_AGREE's dispatch clause reads every
  label of the `case "$tool"` block rather than lines shaped
  `<tool>) install_<tool> ;;`, which left `cursor) install_cursor || true ;;`
  green, and refuses a label that is not a bare tool name. A new And-clause
  holds the argument parser's accepted tools to the arrays plus `all`.
  Review minor m2: §10's ALL_CHECK_INCLUDES_RECORDED_COPILOT row now names
  the assertion that pins "fires, once". No other contract changed.
- 2026-09-28: 7.31.0 session record,
  [ADR-0013](../decisions/adr-0013-harness-memory-is-not-a-home.md). §4 gains
  SESSION_RECORD_FORM_IS_PLACED: every plant receives the session-record form,
  and so the `docs/graph/plans/sessions/` directory, through the existing
  scaffold walk. It adds no installer code and no write site, and a plant's own
  records are never touched. It is written ahead of its RED
  (`tests/test-plant-state.sh`), and §10 binds it when that RED lands. No
  existing contract changed; the status stays `back-written`.
- 2026-09-28: 7.31.0 plant pickup,
  [ADR-0014](../decisions/adr-0014-graft-reconciles-every-graph-engine.md).
  §1 and §2 take in the graph-engine reconciliation and the audit's engine
  check, the one write graft's tools make into a plant's placed engines; graft
  as a whole stays out of scope. §4 gains ENGINE_RECONCILE_PICKS_CONFIG_BY_ENGINE,
  ENGINE_AUDIT_CHECKS_EVERY_PAIR and EXISTING_PLANT_RECEIVES_CURRENT_ENGINES,
  written ahead of their RED (`tests/test-graft-tools.sh`,
  `tests/test-plant-state.sh`); §7 gains ENGINE_LEFT_STALE_BY_GRAFT. No
  installer behaviour and no existing contract changed; the status stays
  `back-written`.
- 2026-09-28: 7.31.0 §10 rows. S9 (`case_session_records`) flips to `green`.
  X383 to X389 bind the engine contracts in `tests/test-graft-tools.sh`: X383,
  X384, X387 and X389 are `red`, and X385, X386 and X388 are guards that are
  green on arrival. EXISTING_PLANT_RECEIVES_CURRENT_ENGINES carries a `pending`
  row until its RED lands in `tests/test-plant-state.sh`, and
  ENGINE_LEFT_STALE_BY_GRAFT has a row of its own.
- 2026-09-28: 7.31.0 final status pass. The graft-tool increment landed, and
  the final tip ran every step green with nothing carried or left unrun. X383,
  X384, X387 and X389 flip `red` → `green`; the guards X385, X386 and X388 stay
  `green`; EXISTING_PLANT_RECEIVES_CURRENT_ENGINES is bound by S10
  `case_engine_upgrade` in `tests/test-plant-state.sh` and is `green`, and so
  is ENGINE_LEFT_STALE_BY_GRAFT through X387. `status_date` moves to this entry,
  and `status_evidence` gains `tests/test-graft-tools.sh`, which holds three
  of the engine contracts and the failure row. One recorded limit: X386's
  mutant is first killed by an older case of `tests/test-graft-tools.sh` that
  exercises the same fallback and aborts before the collecting block, so the
  suite run does not show X386 killing it on its own (verified by hand). A
  candidate for a later round converts the older cases to the collecting
  pattern. No contract changed; the status stays `back-written`.
- 2026-09-28: 7.32.0 harvest, written ahead of its RED tests. §4 gains a block
  of pending amendments: five contracts (PRISTINE_PRIOR_KERNEL_IS_NOT_MIGRATION,
  RECREATED_LIST_IS_COMPLETE, UNKNOWN_STAMP_KEYS_SURVIVE,
  PRE_GROWTH_POINTER_LIVES_IN_THE_PLACEHOLDER_INDEX,
  CODE_ANCHOR_TOOL_IS_PLACED), two failure modes (SEED_HISTORY_UNAVAILABLE,
  STAMP_NOT_AN_OBJECT) and the §6 shapes they need. They are headed so that
  `spec-lint.py` counts none of them, and each moves to §4 or §7 as a
  `### Contract:` or `### Failure:` heading in the commit that lands its RED
  (`verify.status-evidence`), with its §10 row. This departs from the 7.31.0
  practice, which wrote contracts live ahead of their RED and carried the
  over-budget coverage line as expected-red at each tip. No existing contract
  changed; the status stays `back-written`.
- 2026-09-28: 7.32.0 RED. The pending block of §4 is gone: its five
  contracts are now `### Contract:` headings in §4
  (PRISTINE_PRIOR_KERNEL_IS_NOT_MIGRATION, RECREATED_LIST_IS_COMPLETE,
  UNKNOWN_STAMP_KEYS_SURVIVE, PRE_GROWTH_POINTER_LIVES_IN_THE_PLACEHOLDER_INDEX,
  CODE_ANCHOR_TOOL_IS_PLACED), its two failures are in §7
  (SEED_HISTORY_UNAVAILABLE, STAMP_NOT_AN_OBJECT), its shapes are in §6, and §2
  gains the three scope lines it named. §10 binds each to its RED case: K7,
  D5, S11, E5 and E6, `red` except the two guards. The contract text did not
  change in the move. No installer behaviour changed; the status stays
  `back-written`.
- 2026-09-28: 7.32.0 rulings on the RED, no installer behaviour changed. By
  the owner's decision, STAMP_NOT_AN_OBJECT's trigger narrows to a stamp that
  parses as JSON with a top level that is not an object. An empty stamp, a
  stamp that is not JSON, and one whose owned keys have the wrong type stay
  refused before any write by the installer's preflight (S7 unchanged).
  §9 gains AC-9 to AC-13 for the five contracts that left the pending block.
  The status stays `back-written`.
- 2026-09-28: 7.32.0 plant-owned projections. §10 binds
  EVERY_BACKUP_IS_CLASSIFIABLE to three cases of `tests/test-graft-tools.sh`.
  X390 is the GA-C3 case under a label the seed-lint binder reads, and it is
  `green`. X391 (the skill projection of a plant skill node) and X392 (the
  Copilot view of a plant agent node) are `red`: the audit reports each backup
  UNMAPPED. No contract changed; the status stays `back-written`.
- 2026-09-28: 7.32.0 docs pass, no installer behaviour changed.
  BACKUP_BEFORE_REPLACE's And-clause named `.cypress/seed.json` as the only
  exception, while `place_state` also writes `.cypress/recreated-nodes.txt`
  with no backup (RECREATED_LIST_IS_COMPLETE; ruling Q2.1 of the round's second
  question batch). The clause now names both. The spec was wrong about the code;
  no other contract changed, and the status stays `back-written`.
- 2026-09-29 — new contract `PREFLIGHT_SCOPED_TO_WRITTEN_TREES`, and the
  enumeration sentence under `PREFLIGHT_REFUSES_BEFORE_WRITING` corrected. The
  preflight walked every directory under the project root, so root-owned
  directories left by Docker in `node_modules/`, `.next/` or a data volume
  refused every install of that plant, though the installer never writes there.
  The walks now cover the written trees only. The earlier text said "beneath the
  target at any depth", which described the code and not the promise it exists
  for: a refusal that writes nothing. `status_date` moved to this date.
- 2026-09-29 — test consolidation (`docs/plans/grill-test-consolidation.md`,
  S1). HOST_TIERS_AGREE drops its clauses on the tier table of
  `documentation/host-capability-matrix.md`: the arrays in `install.sh` are the
  one home, and a published copy is no longer held to them. The dispatch,
  argument-parser and `EVERY_HOST` clauses stay. E4 keeps two planted rows (the
  arrays against `all`, and a dispatched tool in no tier); the other clauses
  run on the real tree and are no longer planted. §10 follows the folds of the
  consolidation: M9 in case_symchurn; D1 in case_block_declared and
  case_block_readonly; S9 in case_plan_records; S12 in case_s7; X388 in X389;
  X391 and X392 as rows of X390, which also holds M8's UNMAPPED arm;
  EXISTING_PLANT_RECEIVES_CURRENT_ENGINES's S10 row cites X383 and X387 for the
  reconcile and audit halves; the second check of CODE_ANCHOR_TOOL_IS_PLACED is
  the M7 sweep; the recreated
  list's header is checked by its prefix; the DEPRECATED count of
  ALL_CHECK_INCLUDES_RECORDED_COPILOT is held by E2. No installer behaviour
  changed; the status stays `back-written`.
- 2026-09-29: consolidation close-out, by the docs-librarian (spawn
  `session.10.docs-librarian.1`). §10 text only: the M10 row names the two
  paths the case now covers, the E2 row names E1 as the holder of the
  maintained-host negative, and the E3 row says two destinations each. No
  contract changed.
- 2026-09-30: 7.35.0, written ahead of its RED tests
  ([ADR-0021](../decisions/adr-0021-seed-only-procedures-stay-home.md),
  [ADR-0022](../decisions/adr-0022-the-plant-model-map.md)). §2 takes in the
  plant's model map and the seed-only files. §4 gains five contracts, live
  from this entry: MODEL_MAP_TEMPLATE_IS_PLACED (the map template, placed only
  when missing), OPENCODE_MODEL_FROM_MAP, OPENCODE_NO_MAP_ROW_NO_MODEL_LINE and
  OPENCODE_MAP_UNREADABLE_FAILS_CLOSED (the opencode projection writes its
  `model:` line from the map, or none, and refuses a map it cannot read), and
  SEED_ONLY_FILES_NEVER_PLACED (seed-lint holds the seed-only files and the
  manifest's `tools` map against `install.sh`). §6 gains the map grammar, the
  projection rule and the opencode stamp entry; §7 gains MODEL_MAP_UNREADABLE,
  OPENCODE_SELECTOR_UNRESOLVED and OPENCODE_PROJECTION_DRIFT_UNCHECKED; §9
  gains AC-14 to AC-17; §10 gains E7 (a guard, `green` on arrival) and E8 to
  E10 and X393 to X395, `red` until their RED lands, and two `pending` failure
  rows; §11 gains the opencode
  `--check` question. Until the RED lands, `spec-lint.py` counts these five
  contracts as uncovered and `seed-lint` reports each label as absent from its
  test file; both clear when the tester's cases name them. The contracts are
  written live, as in 7.31.0, because the round's RED batch lands before any
  GREEN and a pending block would need a second spec edit in that batch. No
  existing contract changed; the status stays `back-written`.
- 2026-09-30: 7.35.0, the session's rulings S1 and S3 on the architect's first
  findings (kept with the round's working records outside the seed), applied
  before any test of the entry above was written; the round's plan of record is
  `docs/plans/grill-7.35.0-positive-voice.md`. S1: a graft pickup that reports
  "none drifted" after checking nothing is a green that asserts nothing
  (`rule.verify`), so `install.sh opencode --check` is built. §4 gains
  OPENCODE_CHECK_DETECTS_DRIFT, which replaces the failure
  OPENCODE_PROJECTION_DRIFT_UNCHECKED and its §11 question, both removed.
  CHECK_WITHOUT_COPILOT_SAYS_SO's Given narrows to a record that carries
  neither github-copilot nor opencode, because `all --check` now checks the
  opencode projections of a plant that records opencode; its D3 case moves
  its second arm's setup to `install.sh claude-code codex`. §2, §3 and §6 name
  the check and its scope; MODEL_MAP_UNREADABLE also covers `--check`. S3:
  agent-lint's token set is every alias Claude Code accepts (SPEC-0005), so §6
  reads `haiku` as the `investigation | low` row and writes no model line for
  `inherit`, and OPENCODE_MODEL_FROM_MAP and OPENCODE_NO_MAP_ROW_NO_MODEL_LINE
  each gain that clause. §9 gains AC-18; §10 gains E11's two rows, `red`, and
  keeps one `pending` failure row. `spec-lint.py` counts six new contracts as
  uncovered until the RED lands. The status stays `back-written`.
- 2026-09-30: 7.35.0, the post-review fix pass (text only; no contract added
  or removed). §6: a plant declines the map by renaming it by hand, because
  `graft-audit.py --rename` leaves `models.md` in place since ruling S4.
  §7 MODEL_MAP_UNREADABLE's trigger names the refusals the renderer already
  makes: a map that is not UTF-8, a missing separator row, a row without four
  cells, and a `models.md` symlink leaving the target. §10: the 7.35.0 note is
  in the past tense, and the E9, E10, X393 and X394 rows describe the
  strengthened cases (E9's copy-through and count arms; E10's filled-cell
  setup; the needles X393 and X394 pin). The status stays `back-written`.
- 2026-10-01: 7.37.0, written ahead of its RED
  ([ADR-0024](../decisions/adr-0024-one-hook-core-per-session-residency.md);
  plan `docs/plans/grill-7.37.0-routing-context.md`). The Prime Agent
  extensions call the Claude Code hook scripts, so `install.sh prime-agent`
  places byte-identical copies at `.prime/agent/hooks/`. §4 gains
  PRIME_HOOK_SCRIPTS_ARE_PLACED, live from this entry; §9 gains AC-19; §10
  gains its row, `pending` until the tester names the case. Until then
  `spec-lint.py` counts it as uncovered. No existing contract changed; the
  status stays `back-written`.
- 2026-10-01: 7.37.0 increment 2 review fix, RED by the tester (spawn
  `orchestrator.12.tester.6`), on the orchestrator's ruling for reviewer F1.
  §4 gains REINSTALL_ENGINE_SERVES_THE_HOOKS: a re-install that places the hook
  scripts reconciles `docs/graph/graph-lint.py` through
  `tools/graft-graph-engine.py`, PROJECT CONFIG preserved. §10 gains its E13
  row, `red`. The status stays `back-written`.
- 2026-10-01: 7.37.0, REINSTALL_ENGINE_SERVES_THE_HOOKS rewritten by the
  tester (spawn `orchestrator.13.tester.7`) on the orchestrator's corrected
  ruling: the earlier wording had the installer reconcile the engine, which
  contradicts accepted adr-0014. A plain re-install now leaves the engine and
  its config byte-unchanged and the hook names the gap; graft's engine step
  (`tools/graft-graph-engine.py`) makes the hook route, config preserved. §10
  E13 row rewritten, `red` ((b) only). The status stays `back-written`.
- 2026-10-01: 7.37.0, GREEN by the implementer (spawn
  `orchestrator.14.implementer.4`): the route hook's notice for an engine
  without `--plan-json` (SPEC-0003 ENGINE_OLDER_THAN_HOOK_IS_NAMED) turns arm
  (b) green; install.sh unchanged. §10 E13 row `green`. The status stays
  `back-written`.
- 2026-10-01: 7.37.0 release pass, by `architect` (spawn
  `orchestrator.26.architect.1`). Every contract this round added or rewrote
  (PRIME_HOOK_SCRIPTS_ARE_PLACED, REINSTALL_ENGINE_SERVES_THE_HOOKS) reads
  `green`; the two `pending` rows are the failures PARTIAL_CORPUS and
  OPENCODE_SELECTOR_UNRESOLVED, untested by design (§7, §11). No contract
  changed. The status stays `back-written`.
- 2026-10-04: 8.0.0, written ahead of its RED (plan
  `docs/plans/grill-8.0.0-wave-a.md`, increment 1), on the owner's
  decisions of 2026-10-04: corpus knowledge is placed selectively, and a
  fail-open hook warns on a missing script and is run once by `--check`.
  §1, §2 and §3 take in the selective placement, the one jurisdiction
  resolution and the hook execution under `--check`. §4 gains twelve
  contracts, live from this entry: EXPERTISE_PROPOSAL_WRITES_NOTHING,
  EXPERTISE_PLACES_ONLY_THE_CONFIRMED_LIST,
  UNKNOWN_EXPERTISE_ID_REFUSED_BEFORE_WRITING,
  PLACED_PAGE_CARRIES_ITS_PROVENANCE, PLACED_SKILL_IS_A_ROUTABLE_NODE,
  EXPERTISE_IS_RECORDED_IN_THE_STAMP, EXPERTISE_SURVIVES_SILENCE,
  PLANT_EDITED_PAGE_IS_LEFT_AND_NAMED, PLANT_OWNED_PAGE_IS_NEVER_REPLACED and
  EXPERTISE_CHECK_NAMES_MISSING_OR_STALE (increment 13),
  JURISDICTION_RESOLVED_ONCE (increment 10) and
  CHECK_EXECUTES_EACH_WIRED_HOOK (increment 11). §5 Security bounds an id to
  the three corpus roots. §6 gains the `expertise` stamp key, the corpus id,
  the destinations, the provenance line, the proposal line, the matcher's
  per-ecosystem normalization and the check envelope. §7 gains
  EXPERTISE_MANIFEST_UNREADABLE and RECORDED_EXPERTISE_PAGE_WITHDRAWN; §9
  gains AC-20 to AC-25; §10 gains fourteen rows, `pending` until each
  increment's tester names its case; §11 gains two questions, the removal of
  a recorded id and the lockfile's transitive entries. §0 lists the sign-offs
  these contracts owe, unticked. Until the RED lands, `spec-lint.py` counts
  the twelve contracts as uncovered. No existing contract changed; the status
  stays `back-written` until the first RED over a new contract (plan §12
  question 5).
- 2026-10-04: 8.0.0, increment 10 (lane Serial chain), the first RED over a
  new contract: `case_jurisdiction_resolved_once` in
  `tests/test-plant-state.sh` failed on a re-install with no flag, whose
  banner called the recorded jurisdiction undecided, and passes once
  `install.sh` resolves the jurisdiction once, the flag and then the stamp.
  §10's JURISDICTION_RESOLVED_ONCE row is `green`. The status moves from
  `back-written` to `active` with this RED (plan §12 question 5); product,
  architect and tester signed in §0, where their non-blocking conditions are
  listed. §3 gains the jurisdiction sentence product asked for. No contract
  changed.
- 2026-10-04: 8.0.0, increment 11 (lane Serial chain), the RED over
  CHECK_EXECUTES_EACH_WIRED_HOOK: `case_hook_check` in
  `tests/test-install-placement.sh` failed because `--check` ran no hook,
  and passes once `install.sh --check` runs each wired context hook. §10's
  row is `green`. The contract gains two And clauses: a sound hook always
  prints on the check envelope, which answers the architect's condition that
  SPEC-0003 lets the status hook stay silent (only its summary can be
  silent; the anchor line is not), and a command that names no plant script
  is said and not run. §6 gains the Prime Agent argv values and the check's
  four lines. §0 records the answer. No other contract changed.
- 2026-10-04: 8.0.0, increment 12 (lane Serial chain), written in the
  increment's specify step on the owner's decision of 2026-10-04 (flag harness
  entries with no graph home, never delete them), after the reproduction confirmed both halves (plan
  §12 question 4): over a synthetic plant carrying a retired `origin: seed`
  skill and its `.claude/skills/` projection, and a skill living only in
  `.claude/skills/`, `install.sh claude-code --check` and
  `tools/graft-audit.py` named neither. §4 gains
  CHECK_FLAGS_RETIRED_HARNESS_ENTRY and CHECK_FLAGS_ORPHAN_HARNESS_ENTRY; §3
  gains their sentence; §6 gains the harness entries and the flag lines; §9
  gains AC-26. Their RED: `case_retired_flag` and `case_orphan_flag` in
  `tests/test-install-placement.sh` failed because `--check` printed no harness line,
  and pass once `--check` runs `graft-audit.py --harness`, the one home of the
  classification. §10's two rows are `green`. The sign-offs in §0 predate these
  two contracts, which are owed product, architect and tester reviews. No
  existing contract changed; EVERY_BACKUP_IS_CLASSIFIABLE gains a named
  exclusion, `RETIRED`, in place of an `UNMAPPED` backup.
- 2026-10-04: 8.0.0, increment 13 (lane Serial chain), the RED over the
  selective placement. M15 to M20 in `tests/test-install-placement.sh` failed
  with `unknown argument: --expertise`, and the three cases of the new
  `tests/test_corpus_match.py` because `tools/corpus-match.py` did not exist;
  they pass once the installer carries the `--expertise` arm, the matcher
  exists and `tools/graft-audit.py` counts a corpus-placed backup
  `CORPUS-PLACED`. §10's fourteen rows are `green`. The two conditions §0
  recorded for this increment are answered in the contract text:
  RECORDED_EXPERTISE_PAGE_WITHDRAWN states the exit code of a plain install,
  its precedence over EXPERTISE_SURVIVES_SILENCE (which gains the matching
  Except) and the refusal of a listed withdrawn id, and AC-22 and AC-23 map
  to it; UNKNOWN_EXPERTISE_ID_REFUSED_BEFORE_WRITING's Given gains a listed id
  whose destination a different recorded id owns, and an And clause for a
  destination the seed itself places. No other contract changed.
- 2026-10-04: 8.0.0, a follow-up to increment 13 (lane Serial chain): the
  matcher's recall. Read-only runs of `tools/corpus-match.py` over real projects
  showed four defects that leave out a page a plant needs: the walk read
  scratch and copy directories, so an evidence line could name a `.tmp/`
  copy instead of the manifest; a starter entry proposed its umbrella page and never its
  module's page; a `Dockerfile` was not read; and several pages had no rule a
  manifest could meet. §6 gains the walk's edge, the starter reading of an
  artifactId, the coordinates a maven page names as its own, the `Dockerfile`
  and `Containerfile` rule, the runtime-image rule, the presence rules for a
  compose file, a `Dockerfile` and an `azure-pipelines*.yml`, and the
  `dotnet-tools.json` rule. The five new `tests/test_corpus_match.py` cases
  failed first and pass now; §10 gains their rows. The proposal's line form is
  unchanged, so M15 to M20 are untouched. No contract's text changed.
- 2026-10-04: 8.0.0, increment 15 (the tip). Product, architect and tester
  reviewed CHECK_FLAGS_RETIRED_HARNESS_ENTRY, CHECK_FLAGS_ORPHAN_HARNESS_ENTRY,
  increment 13's contract text and its follow-up's §6 matcher rules, each on
  its own read-only review, and signed (§0, with the architect's notes for a
  later round). The tester's blocking gaps were closed with cases before the
  tick: M13 gains an `origin: seed` harness entry with no graph node, M13 and
  M14 assert graft-audit's exit code against the clean copy, M17 gains the
  two destinations the seed itself places (a skill node, a scaffold leaf),
  and `tests/test_corpus_match.py` gains a `Containerfile`, a `dotnet/` image
  and a manifest under each agent host's directory; each new matcher arm was
  proved by a reverted mutation, since it passed on arrival. AC-26 now says a
  flag alone does not fail `--check`. Every §10 contract row is `green`; the
  two `pending` rows are the failures PARTIAL_CORPUS and
  OPENCODE_SELECTOR_UNRESOLVED, untested by design. The status moves from
  `active` to `implemented` (plan §12 question 5, `verify.status-evidence`).
  No contract was added or changed.
- 2026-10-05: 8.0.0, the matcher increment, written by the architect after
  the tester's RED. Read-only runs of the matcher
  had left `language/java`, `language/dart`, `platform/proxmox-ve`,
  `platform/bitbucket-pipelines`, `cli/trivy` and `cli/gitleaks` with no rule
  a project could meet, and the own coordinates were read on `maven` pages
  only, so the packages an npm or pub page lists as its own proposed nothing.
  §4 gains four contracts: LANGUAGE_DECLARATION_PROPOSES_ITS_PAGE,
  OWN_PACKAGE_LIST_PROPOSES_ITS_PAGE, CITED_PACKAGE_PROPOSES_NOTHING and
  PACKAGELESS_PAGE_PROPOSED_BY_ITS_TRIGGER. §6 gains the language rows (the
  Java language level in a Maven or Gradle build, the Dart SDK constraint in
  a pubspec), the own-package list as the one convention by which a library
  page in any key names its own packages, with its reasons and its cost, the
  `maven` own-coordinate form as transitional, the platform and tool
  triggers (a `bitbucket-pipelines.yml` and its step images, the
  `community.proxmox` collection and the `proxmoxer` requirement, the
  `trivy` and `gitleaks` images, GitHub Actions, config files and pre-commit
  hooks), and the four pages unreachable by decision (`platform/azure-cli`,
  `platform/azure-devops-rest`, `cli/curl`, `cli/git`). The `maven` row's
  sentence on own coordinates moves into the own-coordinate paragraph; its
  meaning is unchanged. §7 gains OWN_PACKAGE_NAMED_ONLY_IN_PROSE, and
  EXPERTISE_MANIFEST_UNREADABLE names the new contracts. §2 and §3 take in
  the own-package list and the triggers; §9 gains AC-27 and AC-28; §10 gains
  six `red` rows over the tester's five cases and one `pending` failure row;
  §11 gains three questions. The status moves from `implemented` back to
  `active`, because the new rows are `red` and `implemented` means every
  contract row is green (`verify.status-evidence`); it returns with the
  GREEN. The architect signs these additions in §0; product and tester owe
  their reviews. None of the tester's cases is dropped. No existing
  contract's text changed.
- 2026-10-05: 8.0.0, the matcher increment's product review, answered by
  the architect. AC-28 said a page is never offered for a package it only
  mentions, which CITED_PACKAGE_PROPOSES_NOTHING's Except for `maven` pages
  contradicted. AC-28 now names that exception and the owner's recovery, and
  the Except says which coordinate it covers: one a `maven` page names in its
  `## What it is`, not one it cites later. Its meaning is unchanged. AC-27
  binds to the §6 rows and gains its precision arm, a build that sets no Java
  level does not bring in `language/java`, which the tester's aggregator
  `pom.xml` subtest holds. §3 names the Maven exception and the owner's
  listing of a page no rule reaches. §6 and §11 replace the jjwt example of
  the false positive with the mysql-connector-j page and the MariaDB driver,
  because the corpus pass of this round moved jjwt's BouncyCastle coordinate
  to a later section; the MariaDB entry still proposes mysql-connector-j,
  seen by running the matcher. §7's recovery points to a new §11 question on
  the pages that name their sibling packages only in prose. §10 records the
  tester's two added subtests. No contract was added.

- 2026-10-05: 8.0.0, the matcher increment's GREEN in `tools/corpus-match.py`.
  The own-package list is read on the pages of every key, with the key's
  normalization, and the own-coordinate form stays for `maven` pages. The
  matcher gains the language rows (a `pom.xml` Java level, a Gradle toolchain
  `languageVersion` or `sourceCompatibility`/`targetCompatibility`, a pubspec
  `environment:` `sdk:`), the `bitbucket-pipelines.yml` presence and string
  images, a GitHub workflow's `uses:`, the pre-commit hook ids, the presence
  of `trivy.yaml`, `.trivyignore` and `.gitleaks.toml`, the `trivy` and
  `gitleaks` images, and the two Proxmox VE rows. §10's six `red` rows are
  `green`. Each guard was proved by a reverted mutation: reading every
  backticked name of `## What it is` turned the citation guard red, and
  proposing `language/java` on a `pom.xml`'s presence turned the no-level
  subtest red. Within one manifest, an entry that names a page is preferred
  as evidence over one the page's list names. The evidence of a list match
  names the declared package without its version specifier. §6's sentence on
  the MariaDB driver no longer calls that proposal wrong, because the
  mysql-connector-j page has a MariaDB section. The status returns to
  `implemented`. No contract changed.

- 2026-10-05: 8.0.0, the harvest-candidate form. This release added
  `templates/docs/plans/_harvest-candidates.template.md`, and the
  `templates/docs/**` walk places it at
  `docs/graph/plans/_harvest-candidates.template.md`. case_plan_records then
  failed, because its leak check allowed only the `grill.md` scaffold and
  the session-record form into `plans/`. The architect decided the form is
  placed, not held back: `canonize.harvest-candidates` creates the plant's
  record from the form at that path, graft's Phase 8 writes KEEP-PLANT
  divergences into that record, `graft.gate.rootstock` already names the
  placed form as an expected leaf, and `graft-audit.py --unfilled` skips
  `_`-prefixed leaves, so the form is never reported as an unfilled
  scaffold. §4 gains HARVEST_CANDIDATE_FORM_IS_PLACED, with the same
  guarantees as SESSION_RECORD_FORM_IS_PLACED: placed byte-identical by the
  existing walk with `place_if_missing`, no new write site, never
  overwritten once the plant edits it, no backup beside it, and the plant's
  record untouched. It is a new slug rather than a widened S9, because the
  form has its own reader and record, and S9's slug is cited in the entries
  above. §10 binds it to a new label, S14 in case_plan_records, as `red` until the tester's
  adjusted case lands, so the status moves from `implemented` back to
  `active`; it returns to `implemented` when that row is `green`. No
  installer behaviour and no existing contract changed. The architect wrote
  the contract; product and tester owe their review of it.

- 2026-10-05: 8.0.0, the harvest-candidate form's GREEN. The tester added
  S14 to case_plan_records in `tests/test-plant-state.sh`. It passed on the
  real tree from its first run, because the installer's `templates/docs/**`
  walk already placed the form; no RED was seen on the real tree. The checks
  were proved by mutation instead: on a temp copy of the seed the unmutated
  case passed, and seven mutations each failed on their own S14 message (the
  seed without the form, an installer that does not place it, a placed form
  one byte off, an install that creates `harvest-candidates.md`, a reinstall
  that overwrites the edited form, a reinstall that backs it up, and another
  seed leaf leaking into `plans/`). §10's row for
  HARVEST_CANDIDATE_FORM_IS_PLACED is `green`, and the status returns to
  `implemented`. The tester signs the contract in §0; product's review is
  still owed. No contract and no installer behaviour changed.

- 2026-10-05: 8.0.0, the harvest-candidate form's product review, answered
  by the architect. Product held its tick because §3 did not name the form
  and no acceptance criterion mapped to HARVEST_CANDIDATE_FORM_IS_PLACED. §3
  now states the owner-visible outcome: a blank form is placed, canonize
  starts the record from it, no install creates the record, and a
  re-install keeps the plant's record and edited form with no copy. §9
  gains AC-29, bound to the path, the `install.sh all` re-run and the
  backup check that S14 asserts. The contract's Then clause on
  `SINGLE_WRITER`'s census, which S14 does not measure, moves into the
  contract's preamble as its rationale; the contract's meaning is unchanged.
  Product re-reads before it ticks.

- 2026-10-07: 8.1.2, the source-index build (grill-8.1.2-tool-surfacing.md
  increment 2, on the owner's go of 2026-10-07: "3 go"). SPEC-0007
  `INSTALL_RUNS_THE_BUILD` makes every install that places files end by
  running the placed `docs/graph/source-index.py build`, so an install into a
  Git work tree now writes, through the tool, the cache under
  `.cypress/source-index/` (adr-0029, its 8.1.2 amendment). Two contracts here
  would otherwise be false about that write, so the text changes and the code
  is to follow it. §2 names the write in scope and the build itself as
  SPEC-0007's. SINGLE_WRITER gains an And clause: the build is a tool run of a
  placed file, not an installer write, and the count of 11 exceptions is
  unchanged. IDENTICAL_RERUN_IS_INERT gains an Except clause: the cache is
  replaced on every install into a Git work tree, with equal bytes when
  nothing moved (SPEC-0007 `BUILD_IS_DETERMINISTIC`) and no backup. No §10 row
  changes: M3, M7 and `check_install_write_sites` install into, or read,
  non-Git targets and `install.sh`, where the build adds no write, and
  SPEC-0007's rows hold the cache. No §6 shape and no §7 failure changed.
  Product and tester owe their review of the text; §3's "does nothing and
  says nothing" and AC-3's "zero churn" are product's to reword. Product
  reworded both the same day: the installer's own files stay untouched, the
  build report always prints, and the derived cache is the one exception.

- 2026-10-07: 8.1.2 scope correction (`architect-8.1.2d`, on
  `devils-advocate-8.1.2` 3 and `security-8.1.2` S1). The build writes its
  cache wherever the plant has a governed repository, which includes a
  non-Git plant root holding a nested work tree a node's `repo:` names; "a
  Git work tree" was too narrow. `IDENTICAL_RERUN_IS_INERT`'s Except, §0's
  product note, §3 and AC-3 now say "a plant with at least one governed
  repository" (§3 in its plain form), which supersedes the "into a Git work
  tree" wording of the 8.1.2 entry above. `SINGLE_WRITER`'s And clause names
  the isolated run, `python3 -I -B`, that SPEC-0007 §6 "Build report" owns.
  No contract added or removed, no §10 row changed; product re-reads §3 and
  AC-3.
- 2026-10-09 — 8.1.2 graft finding F1 (`architect-8.1.2j`, from the test
  graft `tester-verify-8.1.2` on a copy of one plant). The plant kept an
  `origin: seed` `docs/graph/protocols/toolcraft.md` whose rules the seed now
  ships in `skill.toolcraft` and `method.bounded-execution`; graph-lint on the
  stage failed with three duplicate fact-key errors, and nothing named the
  node, because the `RETIRED` classification read only the agents and skills
  folders. CHECK_FLAGS_RETIRED_GRAPH_NODE widens the flag to the other two
  machinery folders graph-lint reads as nodes, `protocols/` and `method/`,
  with the same line, the same one home (`tools/graft-audit.py`, which
  `--check` runs) and the same rule: named, never deleted.
  GRAFT_RUN_TIES_LINT_ERRORS_TO_RETIRED_NODES makes graft-run's routes row
  say which graph-lint errors such a node causes and that migration (d)
  clears them; the row still blocks on the error. §2 gains the line for the
  flags, §6 the section "Retired graph nodes" with `RETIRED_LINT_CLAUSE`;
  no §7 failure. Status `active` from `implemented`, with two `pending` §10
  rows until plan increment 11's RED; `implemented` returns when they are
  green. §3 and AC-26 name agents and skills only: product's to follow.
