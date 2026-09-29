---
status: implemented
status_date: 2026-09-29
owner: architect
status_evidence: tests/test-seed-lint.sh, tests/fixtures/front-door/, tests/seed-lint.py, tests/test_gate_registry.py (every §10 row green or a named residual; all wired into tests/run.sh)
---

# SPEC-0004: the front door

## 0. Metadata

- **Identifier:** SPEC-0004-front-door
- **Status:** see frontmatter (single home)
- **Owner:** architect
- **Date:** 2026-09-24
- **Last reviewed:** 2026-09-24
- **Related grill section:** docs/plans/grill-7.29.0-front-door.md §2, §3, §6, §8, §9
- **Related ADRs:** adr-0003-enforcement-layering-honesty (the class vocabulary every enforcement claim and glossary entry uses); adr-0004-pure-graph-architecture (one home per fact); adr-0010-context-residency (the always-loaded figures)
- **Related wiki pages:** none (stdlib Python and POSIX shell only)
- **Supersedes:** —
- **Superseded by:** —
- **Sign-offs:** product [x] 2026-09-24 (§3, §9 re-mapped to the 22 contracts after the fold of three into FIRST_SCREEN_ORDER, COST_FIGURES_SCOPED and ENFORCEMENT_ROW_COMPLETE, steward decision D1: AC-1, AC-13, AC-27 and the coverage table re-mapped; AC-2 names the §6 caps; AC-28 and §3.6 carry the 7.29.0 release clause; §3.2 and §3.5 say links target the entry anchor, host rendering unrecorded; earlier alignment kept: strong-claim list and weakest-class rule, traced surfaces, row-specific residuals, `RAISED` and the implemented-empty ledger, repo-relative prose steps; host tiers and "Try it" resolved in §3.1; G3, G8, G11 accepted residuals per §11) · architect [x] · tester [x] 2026-09-24 (§10 matches the increment 1 RED as written: 54 `case_fd_*` in `tests/test-seed-lint.sh` over the fixture in `tests/fixtures/front-door/`, labels X300 to X335 with X325 unassigned; three `test_prose_lint_*` in `tests/test_gate_registry.py`, `expectedFailure` until increment 7; every case except the X300 guard observed failing for the missing behaviour; the row files are bare) · security [x] 2026-09-24 (Class column signed row by row against ADR-0003 as amended, all 36 `enf-` rows, each checked against its artifact in the hook scripts, `install.sh`, the linters, the `agents/*.md` tool grants and the protocol gate tables, and each carrying its weakest class across the hosts `install.sh all` installs; two rows corrected in place: `enf-tool-allowlist` Class scoped to a host that withholds an unlisted tool, `enf-leaf-cannot-spawn` miss cell names a new model session started from a leaf's shell; the 40 glossary Enforcement fields agree with the rows they link; matrix overclaims in Recursion bound, Tool allowlists and Pre-tool guard reworded to per-host class wording; the rest of the spec is documentation and lint code with no auth, secret, upload, external call or model action)
- **Amended:** 2026-09-29 by the architect (test consolidation, §12): fifteen contracts retired, one narrowed, seven kept. The sign-offs above predate it and were not re-taken.

## 1. Summary

This spec covers the checks that hold the seed's front door: `README.md`,
`DOCUMENTATION.md` with its glossary and enforcement section, the references
in `documentation/`, `INSTALL.md` and the integration READMEs. Seven contracts
remain. Links to a glossary entry or an enforcement row land on one anchor;
every seed path the glossary and the enforcement rows name exists; the README
install section names what an install writes and nothing from the seed's own
tree; published always-loaded and body figures equal what the gate computes and
sit in their home; and the prose floor is measured per file. The reader order,
the glossary's fields, first-use links and the other shape rules of the
2026-09-24 rewrite are judged by the reviewer (§3, §12). Every contract is
decided by `tests/seed-lint.py` or `tests/test_gate_registry.py`, never by a
reader.

## 2. Scope

- **In scope:**
  - anchor resolution for `term-`, `enf-`, `glossary` and `enforcement` links,
    and README's relative links
  - the seed paths named in the glossary's Implemented at fields and in the
    enforcement rows' Artifact cells
  - the README install section's named target paths
  - always-loaded and body figures wherever the front door publishes them
  - the per-file prose-lint gate step
- **Out of scope:**
  - any change to mechanism: hooks, `install.sh`, the shipped plant linters,
    `prose-lint.py`'s own rules
  - reading order, glossary grammar, first-use linking, enforcement-row shape,
    overclaim wording, catalogs, cost scoping, heading levels, link text and
    table headers. They are judged at review since 2026-09-24's rewrite landed
    and the checks were retired (§12)
  - host-release facts that contradict seed method nodes (§7
    `HOST_FACT_RESTATED`)
  - machinery nodes that ship to installed projects (`core/`, `protocols/`,
    `skills/`, `agents/`, `templates/`); `install.sh` places no front-door file
    into a project (§5)
  - whether any sentence is true
  - whether the publishing host resolves an explicit `<a id>` fragment in
    rendered Markdown (§7 `ANCHOR_NOT_RENDERED_BY_HOST`)
- **Front-door files** (a term used throughout): `README.md`,
  `DOCUMENTATION.md`, `documentation/*.md`, `INSTALL.md` and
  `integrations/*/README.md`.

## 3. User-facing behavior

(Authored by `product`.)

Since 2026-09-29 (§12) only the seven contracts of §4 gate this section. The
rest of what it describes (reading order, the glossary's fields, first-use
links, the enforcement table's shape, cost scoping, the accessibility floor) is
judged by the reviewer, not by a check.

This spec has one user: a developer who has never seen the seed, who uses or is
considering an AI coding agent, and who is deciding from the README whether to
install. They should be able to decide without learning the project's vocabulary
first. There are four ways into the front door, described below. Each one ends in
a decision the reader can make from what they have read, without asking anyone.

### 3.1 The first reader, reading top to bottom

The reader opens the README and sees these nine sections in this order. Each
answers one question, and none depends on a later one:

1. **What it is.** A few sentences in ordinary words. It is an installer that
   copies instruction files, a Markdown method and small stdlib linters into
   the reader's repository, for the AI coding agent they already use. It is not
   a library their code imports, not a service, and not a model. Installing
   only places files. A separate agent session, started by pasting one prompt,
   reads the repository and builds its knowledge graph. The reader meets no
   coined word here that they need in order to understand the sentence. Where
   a project word appears at all, it is a link.
2. **Who it is for, and who it is not for.** Developers working in a code
   repository through a supported agent harness. The harnesses are named, and
   the reader is told in words that support differs by harness and that some
   are deprecated. Which harness sits in which tier is not printed here: the
   sentence links the support-tier section of the host capability matrix and
   the decision that sets the tiers
   (`docs/decisions/adr-0009-host-support-tiers.md`). The tier
   assignment has one home (`install.sh`'s tier arrays, published in the
   matrix and held there by `check_host_tiers`), and a tier printed in README
   would be a copy nothing compares. ADR-0009 is still `proposed`; README
   links it either way, so its status does not block this section. No
   contract holds "no tier printed"; the reviewer judges it at verify. It
   is not tied to a language or stack, and the one skew (the shipped reference
   corpora) is stated plainly. It is not for someone who does not use an
   agent-capable coding tool, because nothing in the install acts without an
   agent session.
3. **What installing does to your repository.** The files and directories an
   install writes into *the reader's* repository, named by the paths the
   reader will see there after installing: the kernel instruction file at the
   project root, the harness directory, `docs/graph/`, the install stamp and
   the local copy of the entry prompt. Other harnesses write elsewhere, and
   the section links to where that is recorded. The reader learns that a
   differing file already in place is kept beside itself as a timestamped copy
   and then replaced, not merged. The section names the one path that is
   replaced without a copy (the derived install stamp). It also says what the
   install leaves alone: application source, `.gitignore`, git history, CI.
   The seed's own source tree (`core/`, `agents/`, `skills/`, `integrations/`)
   is not presented as what the reader receives.
4. **What it costs.** A table. Each row gives one figure, and the same row says
   what the figure covers and how it was obtained. The always-loaded
   per-session figure is marked as computed from the installed files. It is a
   lower bound, not a live measurement. The section then lists what that
   figure leaves out: on-demand graph nodes, each specialist spawn, the hook
   injections and the one-time growth pass. The method-overhead figure gives
   the value its evidence records, marked as measured once on one small task,
   with a link to the record. The section says that no money figure exists.
5. **Try it.** The two commands (clone, install with a harness name and a
   project path), then the next step: paste the entry prompt into an agent
   session rooted at the project. The section says that running these needs no
   project vocabulary. It also says, in words, that the clone command takes
   whatever the default branch holds when it runs, not a tagged release.
   Pinning a tag was rejected: it is one more version pin every release must
   move, and nothing holds a README pin. No contract holds this sentence; the
   reviewer judges it at verify.
6. **How it works.** One paragraph built on the triage's workflow sentence: the
   seed is a written workflow, not a program. The agent reads which steps a
   task needs and in what order, and does them itself. It hands steps that need
   a clean context to subagents. A few hooks and linters check parts of the
   work, and the rest depends on the model and on the reader. Each project or
   borrowed term is a link to its glossary entry the first time it appears.
7. **Why it is built this way.** A short account of the reasons, linking the
   decision index, never a hand-counted range of decision records.
8. **What it does not do.** A list. Each item names a rule the method *asks*
   the model to follow and no tool holds (task tier, spec before code, test
   before code, routing before reading, and others). Each item links its row in
   the enforcement section. It also names what has not been measured yet, so
   the reader sees the limits before deciding. This section is not softened to
   make the project look simpler than it is.
9. **Where to go next.** Links, each with text that says where it goes: the
   manual, the glossary, the enforcement section, the three references, the
   host capability matrix, the decision index and the install guide.

At the end of section 5 the reader can decide whether to try it. At the end of
section 8 they can decide whether to adopt it, knowing what they are agreeing
to. The README no longer carries release-history narration, the full catalogs,
or a figure that no check pins.

### 3.2 The reader who meets a term and follows it

The reader meets a coined word ("plant", "graft", "canonize") or a borrowed word
used in a narrower sense ("agent", "skill", "hook", "tier") in the README. The
first time it appears, it is a link whose text is the word itself. The link
points at that word's own glossary entry anchor, not at the top of the
glossary (whether the publishing host lands the reader there is the
unrecorded prerequisite named in §3.5). The entry first lists the forms of the word it covers (for example
"plant, plants"), then shows six labelled fields in a fixed order:

- **Here.** What the word means in this project, in plain words. Any other
  project term inside this field is itself a link.
- **Field.** What the word usually means elsewhere, paraphrased, with the
  source, retrieval date and verification status. For a coined word it says
  "no standard meaning".
- **Implemented at.** Seed paths that exist. Where relevant, it also gives
  "an install produces …" lines naming paths in the reader's repository.
- **Enforcement.** One of the enforcement classes, or "not a control".
- **Divergence.** Same, narrower, broader, different, or no standard meaning.
- **Why.** A decision record, plan, commit or code location, or the literal
  words "not recorded".

The reader can decide whether their existing understanding of the word carries
over (Divergence), and where to look to check (Implemented at). Where the seed
does not know something, the entry says "not recorded" instead of guessing.

The agent-and-skill case works the same way. The reader follows "agent" or
"skill" and finds the contrast stated once, in the `skill` entry. An agent is
spawned as a separate worker with its own context, tool list and model class.
A skill is read into the context of whichever session is working and grants
nothing. Both references open with a one-sentence definition of their own term
and link to that entry. Neither restates the contrast.

A term whose definition must reach installed projects (it lives in a method
node that ships to the reader's repository) is glossed in one line and linked
to that node, which stays its only home.

### 3.3 The reader asking "what is actually enforced?"

The reader sees a claim that sounds like enforcement ("enforces", "requires",
"refuses", "blocks", "cannot", "never") in the README, in the install guide, in
a harness's integration README, or in a glossary entry's Here or Enforcement
field. The claim is a link to its row in the enforcement section. Each row
there gives four things: the mechanism, the file that implements it, its class
(the harness refuses; a tool refuses when it is run; caught after the fact; a
named judge decides), and what it can miss. Host differences are not repeated
in the row. The row links the host capability matrix. A hook that only adds
text to the agent's context is listed as not a control, in those words: it
fires, but it holds nothing.

A sentence never states a stronger class than its row holds. A strong claim
is a sentence that says "hard", "cannot", "can't", "guarantees", "ensures",
"prevents", "blocks", "refuses" or "stops", and is not negated ("no tool
blocks it" is not a strong claim). Anywhere in the front door, a strong claim
that links a row links only rows whose *weakest* class is hard. A row that
holds on some harnesses and depends on the model elsewhere counts as its
weaker class, so "the harness blocks it" cannot point at it. "Never" and
"only" are not strong claims: the limits section is written with "never",
and "only" usually scopes a sentence. A glossary entry that calls its term
hard links a row that is hard in the same sense. A limit that applies only in
the seed's own test gate, such as the kernel byte budget, is described as the
seed's gate and never as a control in the reader's repository.

Four rows name the gap the reader most needs to know. The tool allow-list and
the leaf's inability to spawn workers each name role emulation and an omitted
tool list, and neither is classed hard. The command guard says it fails open,
can be evaded by indirection and depends on the harness firing it. It is
never called a security measure, a sandbox or a protection anywhere that
links it. The backup row names the install stamp as the one file replaced
without a copy.

The manual's own prose and the three references are the detail pages the rows
link to, and they are not traced. A strong claim there that links no row is
left to the reviewer (§7 `STRONG_CLAIM_IN_MANUAL_PROSE`).

The reader can then decide which parts of the method they would have to hold
themselves, for example by wiring the linters into their own CI, and which
parts the harness holds for them.

### 3.4 The returning user looking for the catalog

A returning user wants the list of agents, protocols, skills or templates, or the
list of decision records. Earlier README versions held these. The README now
links them from section 9 ("Where to go next") and names only a few items as
examples. The user follows the link to the matching reference. That reference
opens with a one-sentence definition of its term, then the full table, which
the seed's existing checks keep in step with the files. The decision records are
reached through the decision index, never through a numbered range that can go
stale.

Known state: a bookmark to an old README section anchor (for example the old
"What you get" heading) no longer resolves, because Markdown has no redirects.
The user recovers through section 9. This is an accepted residual, recorded
in §11: the release's changelog names the removed anchors.

### 3.5 Accessibility floor for the Markdown front door

These rules apply to the README, the glossary, the enforcement section and the
reference openers:

- One `#` title. Headings never skip a level. The nine sections are `##`.
- Link text makes sense read on its own: the term, the document name or the
  destination, never "here", "this" or "link".
- Every table has a header row, and every column header is non-empty. The
  current cost table has an empty header row, and that does not meet this
  floor.
- No meaning is carried only by bold, italics or letter case. A class, a
  warning or a deprecation is stated in words.
- Glossary entries and enforcement rows have stable explicit anchors, and
  every link to one links to the entry's anchor, not to the top of the
  page. Whether the publishing host then lands the reader (and a
  screen-reader user) on the entry itself depends on that host rendering
  explicit anchors. That is not recorded: it is a do-not-guess prerequisite
  of the glossary increment, observed once on the publishing host, never
  assumed (§2, §7 `ANCHOR_NOT_RENDERED_BY_HOST`).
- No images are needed to understand any of it. If an image is added, it has
  alt text that states what it shows.

### 3.6 The maintainer running the seed's gate

The prose floor is measured per file, and each file's step is named by its
path from the repository root, so one file's excess cannot hide behind another
file's slack and two files with the same name cannot merge into one step.

## 4. Functional contracts

(Authored by `architect`. Reviewed by `tester` for testability.)

Every contract below is a check in `tests/seed-lint.py` unless it names
another file. A finding is one line of the form
`front-door: <SLUG>: <file>:<line>: <message>`, with line `0` when the finding
is about a whole file or a missing input, and it makes seed-lint exit 1. "Body
text", "unit", "inline link", "path-like" and every constant are defined in
§6. Each planted case runs on a hermetic copy with the minimal fixture of §6;
the real-tree seed-lint step is the partner of every planted case.

### Contract: INSTALL_SECTION_NAMES_TARGET_PATHS
- **Given:** the README section headed `## What installing does to your repository`
- **When:** seed-lint reads its backticked tokens
- **Then:** each of `CLAUDE.md`, `AGENTS.md`, `.claude/`, `docs/graph/` and
  `.cypress/seed.json` appears as a whole backticked token
- **And:** every path-like backticked token in the section, `install.sh`
  excepted, passes the §6 install-literal rule against `install.sh`
- **And:** no backticked token in the section begins with a seed-source
  prefix from §6 (`core/`, `agents/`, `skills/`, `integrations/`,
  `protocols/`, `templates/`, `tools/`, `tests/`)
- **And:** one unit in the section contains both `.cypress/seed.json` and an
  inline link to `DOCUMENTATION.md#enf-backup-before-replace`

### Contract: GLOSSARY_PATHS_EXIST
- **Given:** every glossary entry's Implemented at field
- **When:** seed-lint reads its backticked tokens (a row of the
  `FRONT_DOOR_ANCHORS_RESOLVE` check)
- **Then:** every path-like token outside an "An install produces" clause
  resolves under the seed root by the §6 seed-path rule, including any `:N` or
  `:N-M` suffix
- **And:** every path-like token inside such a clause passes the §6
  install-literal rule, and every backticked bare identifier inside such a
  clause names a function defined in `install.sh`
- **And:** a field with no path-like token begins with `n/a`

### Contract: MECHANISM_CLAIMS_TRACED
- **Given:** every body row of the enforcement table in `DOCUMENTATION.md`
- **When:** seed-lint reads the row's Artifact cell (a row of the
  `FRONT_DOOR_ANCHORS_RESOLVE` check)
- **Then:** every path-like backticked token in it, the mechanism the row
  names, resolves under the seed root by the §6 seed-path rule
- **Note:** narrowed on 2026-09-29 (§12). A claim that links an `enf-` row
  is held to an existing row by `FRONT_DOOR_ANCHORS_RESOLVE`. Which units must
  link a row, and whether a strong claim links only hard rows, are judged at
  review

### Contract: EAGER_FIGURES_CHECKED_WHEREVER_PUBLISHED
- **Given:** every front-door file
- **When:** seed-lint's published-figures check reads it for always-loaded byte
  figures, by its figure and historical-marker rule
- **Then:** every always-loaded byte figure it finds equals a value that
  `check_eager_surface` computes, or `EAGER_BUDGET`

### Contract: BODY_FIGURES_HAVE_A_REQUIRED_HOME
- **Given:** `BODY_FIGURE_HOME` (§6)
- **When:** seed-lint's published-figures check reads the body figures
- **Then:** the file exists, and it states the largest and median routable
  body and `MACHINERY_BODY_CEILING` and `LIFECYCLE_BODY_CEILING`, each in one of
  the check's grouped spellings
- **And:** the `EAGER_EXEMPTIONS` "consequently empty" and "no slack" phrase
  rules run over every front-door file, not over README alone
- **And:** no front-door file other than `BODY_FIGURE_HOME` holds a unit that
  contains both the word `body` or `bodies` and a §6 `line_figure` whose value
  is not in `PROJECT_NODE_LINE_FIGURES`
- **And:** every value in `PROJECT_NODE_LINE_FIGURES` occurs as a literal in
  `templates/knowledge-graph/graph-lint.py`, so the exemption cannot outlive
  the ceiling it names

### Contract: FRONT_DOOR_ANCHORS_RESOLVE
- **Given:** every front-door file
- **When:** seed-lint reads every inline link whose fragment begins `term-`
  or `enf-`, or equals `glossary` or `enforcement`
- **Then:** the fragment names exactly one explicit anchor (§6) in the file
  the link targets
- **And:** every explicit anchor id in `DOCUMENTATION.md` is unique
- **And:** every inline link in README whose target is a relative path
  resolves to an existing file under the seed root

### Contract: PROSE_FLOOR_HELD_PER_FILE
- **Given:** `tests/run.sh` and `tools/gate-registry.py`
- **When:** `python3 tools/gate-registry.py --lint` parses the prose-lint
  invocations
- **Then:** each invocation names exactly one `--file`, each is registered as
  its own step named `prose-lint.py --file <path>`, where `<path>` is the
  argument relative to the repository root, and `README.md` and
  `DOCUMENTATION.md` each have one
- **And:** a `tests/run.sh` line passing two `--file` arguments to
  `prose-lint.py` makes `--lint` exit 1 naming the line
- **And:** two prose-lint lines that resolve to the same step name make
  `--lint` exit 1 naming both lines. The refusal covers prose-lint names only
- **Test file:** `tests/test_gate_registry.py`, not seed-lint

## 5. Non-functional requirements

- **Boundary:** every artifact here is seed-side. `install.sh` places none of
  the front-door files, so a definition an installed project needs keeps its
  home in the machinery node that ships.
- **Compatibility:** stdlib Python 3 only; planted cases in bash
  3.2-compatible shell; no new dependency.
- **Reliability:** deterministic: no network, no clock, no randomness, no
  dependence on file order beyond sorted globs.

## 6. Data shapes

### Constants

| Name | Value | Ratchet direction |
|---|---|---|
| `BODY_FIGURE_HOME` | `DOCUMENTATION.md` | not a ratchet |
| `PROJECT_NODE_LINE_FIGURES` | {150, 170}: the project-node body ceiling of `templates/knowledge-graph/graph-lint.py`, a different fact from the seed's body figures | not a ratchet; each value must occur in that file (§4) |

### Body text and units

```yaml
body_text:
  excludes: [fenced blocks, ATX heading lines, HTML comments and explicit anchor tags]
  masks_for_matching: [inline code spans, inline link targets]
unit: a paragraph, a list item or one table body row
inline_link: "[text](target)"      # reference-style links are not resolved
path_like: a backticked token containing "/" or ending in .md .py .sh .json .ts .tsv .yml .toml
line_figure: '(?<![\w.])\d[\d    ,]*\s*-?\s*lines?\b'
seed_source_prefixes: [core/, agents/, skills/, integrations/, protocols/, templates/, tools/, tests/]
```

### Explicit anchors

```yaml
anchor_tag: '<a id="ID"></a>'      # on its own line, or at the start of a table cell
ids:
  glossary_region: "glossary"
  enforcement_region: "enforcement"
  entry: '^term-[a-z0-9]+(-[a-z0-9]+)*$'
  row:   '^enf-[a-z0-9]+(-[a-z0-9]+)*$'
uniqueness: every id occurs once in DOCUMENTATION.md
premise:    the publishing host resolves "#ID" to this tag in rendered Markdown. Not recorded;
            the checks hold that the id exists and is unique, never that a browser lands on it
```

### Glossary fields and enforcement rows

The glossary region runs from `## 15. Glossary` to the next `##` heading; an
entry is a `###` headword, and its Implemented at field is the line labelled
`- **Implemented at:**`, continued on indented lines. The enforcement region
runs from `## 17. What is enforced, and how` to the next `##` heading or the
end of the file; its table's second column is the Artifact cell.

```yaml
seed_path_rule:
  placeholders: "<...>" is read as "*"; one level of {a,b} is expanded
  resolves: every expansion matches at least one file or directory under the seed root
  line_suffix: ":N" or ":N-M" requires N <= M <= the file's line count
install_clause: from the literal "An install produces" to the end of its sentence
install_literal_rule:
  prefix: the token up to its first "<", "*" or "{", with a leading "./" removed
  requires: the prefix is at least 4 characters and occurs literally in install.sh
  bare_identifier: '^[a-z_][a-z0-9_]*$' must match a line '^<name>\(\)' in install.sh
```

### Fixture

`tests/fixtures/front-door/` holds a minimal README, `INSTALL.md` and glossary,
laid into a hermetic copy. Synthetic only: placeholders such as
`/path/to/your/project` and `example.com`, no credential-shaped string, and no
text copied from a donor environment.

## 7. Failure modes

(Authored by `architect`. Security adds adversarial cases.)

Field values below are fragments and carry no closing period.

### Failure: ANCHOR_DRIFT
- **Contracts:** `FRONT_DOOR_ANCHORS_RESOLVE`
- **Trigger:** an entry or row anchor is renamed or removed, or two share an
  id, while a front-door link still names the old id
- **Response:** a finding naming the linking `file:line` and the id that does
  not resolve, or the duplicated id
- **Side effects:** none
- **Recovery:** restore the id or re-point every link; once released, ids are
  treated as a public interface

### Failure: ANCHOR_NOT_RENDERED_BY_HOST
- **Contracts:** `FRONT_DOOR_ANCHORS_RESOLVE`
- **Trigger:** the publishing host does not turn an explicit `<a id>` tag into
  a fragment target in rendered Markdown, so a link that resolves by the §6
  rule lands at the top of the page
- **Response:** none; every check passes, because each reads the file, not the
  rendered page
- **Side effects:** a reader following a term or row link lands on no entry
- **Recovery:** prevented, not detected: one rendered fragment observed on the
  publishing host before the glossary landed

### Failure: FIGURE_MOVED_WITHOUT_ITS_CHECK
- **Contracts:** `EAGER_FIGURES_CHECKED_WHEREVER_PUBLISHED`,
  `BODY_FIGURES_HAVE_A_REQUIRED_HOME`
- **Trigger:** a derived figure is moved out of README into another file
- **Response:** within the front-door files, the checks still hold it, and a
  body figure outside its home is a finding. Outside the front-door files
  (`CHANGELOG.md`, `docs/plans/`, `CLAUDE.md`) nothing holds it; that is the
  residual
- **Side effects:** none
- **Recovery:** keep reader-facing figures in the front-door files

### Failure: INSTALL_LITERAL_IS_NOT_A_WRITE
- **Contracts:** `GLOSSARY_PATHS_EXIST`, `INSTALL_SECTION_NAMES_TARGET_PATHS`
- **Trigger:** a target path occurs in `install.sh` only in a comment or a
  message, not on a path that writes it
- **Response:** none; it passes
- **Side effects:** none
- **Recovery:** SPEC-0001's placement tests hold what is written; this check
  holds only that the name is the installer's

### Failure: BLENDED_PROSE_STEP
- **Contracts:** `PROSE_FLOOR_HELD_PER_FILE`
- **Trigger:** a `tests/run.sh` line passes several `--file` arguments to
  `prose-lint.py`
- **Response:** `gate-registry.py --lint` exits 1 naming the line
- **Side effects:** none
- **Recovery:** one invocation per file, each registered

### Failure: PROSE_STEP_NAME_COLLISION
- **Contracts:** `PROSE_FLOOR_HELD_PER_FILE`
- **Trigger:** two prose-lint lines in `tests/run.sh` resolve to the same step
  name, as a basename rule would give `README.md` and
  `integrations/<host>/README.md`
- **Response:** `gate-registry.py --lint` exits 1 naming both lines
- **Side effects:** none
- **Recovery:** name steps by repository-relative path (§4)

### Failure: HOST_FACT_RESTATED
- **Contracts:** none; §2 scope
- **Trigger:** a front-door file states a host-release fact (hooks in
  subagents, agent registration, the spawn tool's name, spawn depth) instead
  of saying it is host-dependent and linking the matrix
- **Response:** none; it passes
- **Side effects:** none
- **Recovery:** the reviewer at verify

### Failure: PROJECT_NODE_FIGURE_COLLISION
- **Contracts:** `BODY_FIGURES_HAVE_A_REQUIRED_HOME`
- **Trigger:** a seed body figure outside `BODY_FIGURE_HOME` whose value
  happens to be 150 or 170
- **Response:** none; it passes as the project-node ceiling
- **Side effects:** none
- **Recovery:** the reviewer at verify; the exemption set is bound to the
  literals in `graph-lint.py` and cannot outlive them

## 8. Examples

```text
# Failure: a link to an anchor that does not exist (§7 ANCHOR_DRIFT)
README: "a [plant](DOCUMENTATION.md#term-plnat) is ..."
Output: front-door: FRONT_DOOR_ANCHORS_RESOLVE: README.md:<n>: term-plnat

# Failure: a seed path that does not exist
DOCUMENTATION.md, Implemented at: "`tools/no-such-tool.py`"
Output: front-door: GLOSSARY_PATHS_EXIST: DOCUMENTATION.md:<n>: tools/no-such-tool.py
```

## 9. Acceptance criteria

(Authored by `product`; cut to the seven contracts of §4 on 2026-09-29, §12.
The criteria of the retired contracts, and the detective reader test AC-18,
are in the history of this file; their numbers are not reused.)

- [ ] **AC-6.** Every path-like token in an entry's Implemented at field,
      outside an "An install produces" clause, resolves under the seed root
      (placeholders and one level of `{a,b}` expanded), and a `:N` or `:N-M`
      suffix lies within the file's line count. Inside that clause, each
      path's literal prefix occurs in `install.sh`, and each backticked bare
      name is a function `install.sh` defines. A field with no path begins
      `n/a`. A planted nonexistent path fails.
      Contracts: maps to GLOSSARY_PATHS_EXIST.
- [ ] **AC-15.** The "what installing does to your repository" section names,
      each as a whole backticked token, `CLAUDE.md`, `AGENTS.md`, `.claude/`,
      `docs/graph/` and `.cypress/seed.json`. Every path-like token in the
      section other than `install.sh` passes the §6 install-literal rule. No
      token in the section begins with a seed-source prefix. A planted section
      that lists `core/`, or omits `.cypress/seed.json`, fails.
      Contracts: maps to INSTALL_SECTION_NAMES_TARGET_PATHS.
- [ ] **AC-16.** One unit of the install section names `.cypress/seed.json`
      (the one path replaced without a copy) and links
      `DOCUMENTATION.md#enf-backup-before-replace`. A planted "every file it
      replaces is left beside itself" that neither names the stamp nor links
      the row fails.
      Contracts: maps to INSTALL_SECTION_NAMES_TARGET_PATHS.
- [ ] **AC-17.** Always-loaded byte figures in any front-door file equal a
      computed value or the eager budget. `DOCUMENTATION.md`, the required
      home for body figures, exists and states the largest and median
      routable body and both body ceilings. No other front-door file holds a
      body line figure. An eager figure that nothing computes in
      `documentation/agents-reference.md`, a body figure copied into
      `INSTALL.md`, and a `DOCUMENTATION.md` missing the median each fail.
      Contracts: maps to EAGER_FIGURES_CHECKED_WHEREVER_PUBLISHED, BODY_FIGURES_HAVE_A_REQUIRED_HOME.
- [ ] **AC-25.** Every link in a front-door file to a `term-` or `enf-`
      fragment, or to `glossary` or `enforcement`, lands on exactly one
      explicit anchor in the target file; every explicit anchor id in
      `DOCUMENTATION.md` is unique; every relative link in README resolves to
      an existing file. Every seed path an enforcement row's Artifact cell
      names exists. A planted link to `#term-plnat`, two entries sharing
      `term-plant`, a README link to a missing file, or an Artifact path that
      does not exist each fail.
      Contracts: maps to FRONT_DOOR_ANCHORS_RESOLVE, MECHANISM_CLAIMS_TRACED.
- [ ] **AC-29.** Each prose-lint invocation in `tests/run.sh` names exactly
      one `--file` and is registered as its own step named
      `prose-lint.py --file <path>`, with `<path>` relative to the repository
      root; README and DOCUMENTATION each have one. A planted line passing two
      `--file` arguments, or two lines resolving to one step name, make
      `tools/gate-registry.py --lint` exit 1 naming the lines. The check lives
      in `tests/test_gate_registry.py`.
      Contracts: maps to PROSE_FLOOR_HELD_PER_FILE.

| Contract | Accepted by |
|---|---|
| INSTALL_SECTION_NAMES_TARGET_PATHS | AC-15, AC-16 |
| GLOSSARY_PATHS_EXIST | AC-6 |
| MECHANISM_CLAIMS_TRACED | AC-25 |
| EAGER_FIGURES_CHECKED_WHEREVER_PUBLISHED | AC-17 |
| BODY_FIGURES_HAVE_A_REQUIRED_HOME | AC-17 |
| FRONT_DOOR_ANCHORS_RESOLVE | AC-25 |
| PROSE_FLOOR_HELD_PER_FILE | AC-29 |

## 10. Test mapping

(Owned by `tester`.) Each row citing `tests/test-seed-lint.sh` opens its Test
case cell with a fixed-width label that the file carries beside the case.
SPEC-0003 holds `X101` to `X203`. The labels of the retired contracts' cases
are not reused.

| Contract / Failure | Test case | Test file | Level | Status |
|---|---|---|---|---|
| INSTALL_SECTION_NAMES_TARGET_PATHS | X303 case_fd_install_target_paths, case_fd_install_seed_path · `check_fd_install_section_names_target_paths` | tests/test-seed-lint.sh | fixture (scope) | green |
| GLOSSARY_PATHS_EXIST | X306, a row of the anchors check: a glossary path that does not exist, an install literal `install.sh` does not hold | tests/test-seed-lint.sh | fixture (scope) | green |
| MECHANISM_CLAIMS_TRACED | X312, a row of the anchors check: an enforcement row's Artifact path that does not exist | tests/test-seed-lint.sh | fixture (scope) | green |
| EAGER_FIGURES_CHECKED_WHEREVER_PUBLISHED | X318, a scope row of the published-figures check: an always-loaded figure nothing computes, in `documentation/agents-reference.md` and in `INSTALL.md` | tests/test-seed-lint.sh | fixture (scope) | green |
| BODY_FIGURES_HAVE_A_REQUIRED_HOME | X319, a scope row of the published-figures check: the median dropped from the home; a body figure in `INSTALL.md` | tests/test-seed-lint.sh | fixture (scope) | green |
| BODY_FIGURES_HAVE_A_REQUIRED_HOME | X332, a scope row of the published-figures check: the `PROJECT_NODE_LINE_FIGURES` exemption and its binding to `graph-lint.py` | tests/test-seed-lint.sh | fixture (scope) | green |
| FRONT_DOOR_ANCHORS_RESOLVE | X320 case_fd_anchor_resolves, case_fd_anchor_duplicate · `check_fd_front_door_anchors_resolve` | tests/test-seed-lint.sh | fixture (scope) | green |
| PROSE_FLOOR_HELD_PER_FILE | test_prose_lint_one_step_per_file | tests/test_gate_registry.py | unit (scope) | green |
| PROSE_FLOOR_HELD_PER_FILE | test_prose_lint_multi_file_refused | tests/test_gate_registry.py | unit (scope) | green |
| PROSE_FLOOR_HELD_PER_FILE | test_prose_lint_same_name_refused | tests/test_gate_registry.py | unit (scope) | green |
| PROSE_FLOOR_HELD_PER_FILE | test_prose_lint_other_argument_forms_refused | tests/test_gate_registry.py | unit (scope): `--file=`, `--root` and `--glob` refused | green |
| ANCHOR_DRIFT | X320 case_fd_anchor_resolves, case_fd_anchor_duplicate | tests/test-seed-lint.sh | fixture (scope) | green |
| ANCHOR_NOT_RENDERED_BY_HOST | none: every check reads the file, not the rendered page | none | residual, prevented not detected | residual |
| FIGURE_MOVED_WITHOUT_ITS_CHECK | X318 and X319 | tests/test-seed-lint.sh | fixture (scope); outside the front-door files it is a residual | green |
| INSTALL_LITERAL_IS_NOT_A_WRITE | none: passes by design; SPEC-0001 placement tests hold writes | none | residual | residual |
| BLENDED_PROSE_STEP | test_prose_lint_multi_file_refused | tests/test_gate_registry.py | unit (scope) | green |
| PROSE_STEP_NAME_COLLISION | test_prose_lint_same_name_refused | tests/test_gate_registry.py | unit (scope) | green |
| HOST_FACT_RESTATED | none: no contract (§2 scope) | none | residual, judgment; judge: `reviewer` at verify | residual |
| PROJECT_NODE_FIGURE_COLLISION | none: passes by design. X332 pins that the exemption holds only while `graph-lint.py` carries the literals | none | residual, semantic; judge: `reviewer` at verify | residual |

## 11. Open questions

Rows about the contracts retired on 2026-09-29 left with them (§12).

| Question | Why it matters | Current assumption | Owner | Resolves by |
|---|---|---|---|---|
| Is meaning carried only by emphasis (product AC-22) acceptable to leave to judgment? | No stdlib check can tell whether bold carries meaning the words do not | Accepted residual: the reviewer judges it at verify against the README, glossary and enforcement section | product | reviewer's verify pass on the README increment |
| Must the cost section list what the always-loaded figure leaves out and say no money figure exists (product G8)? | Readers missed both in the baseline reader test | Accepted residual: a phrase check would pin wording, not meaning; product's detective reader test holds it | product | the after reader test |
| Old README anchors (`#what-you-get`, `#try-it-and-what-it-costs`) stop resolving (product G11) | External bookmarks break; Markdown cannot redirect | Accepted residual: the release's CHANGELOG entry names the removed anchors, and "Where to go next" is the recovery | orchestrator | the provenance increment |
| Accepted residual: `HOST_FACT_RESTATED` (security S2) | Nothing mechanical keeps M7 to M9 out of glossary fields, rows and the ADR-0003 amendment | Judged at verify by the reviewer; a phrase check belongs to the separate host-facts change, which has its own spec | security; reviewer | verify of increments 2, 3, 5 and 6 (6 added 2026-09-24: it edits `INSTALL.md` and the integration READMEs) |
| Old README anchors (reliability R7): keep empty `<a id="what-you-get"></a>`-style anchors on the successor sections? | They would let a bookmark land on the successor section | Not kept. Whether the host resolves an `<a id>` tag in a rendered README fragment is not recorded, so the anchor would be an unverified promise. The CHANGELOG names the removed anchors either way (G11 above). Reversible: add them in a later release once the host behaviour is recorded. (2026-09-24: now conditional on the one anchor-render observation in the row above, the same premise the `term-`/`enf-` anchors rest on. If it resolves, product may keep them in increment 5) | orchestrator, product | the anchor-render observation, then increment 5 |
| Does the publishing host resolve an explicit `<a id>` fragment in rendered Markdown? | Every `term-`/`enf-` link, and the legacy-anchor option, assumes it; no check can see a rendered page (§7 `ANCHOR_NOT_RENDERED_BY_HOST`) | Not recorded. Do not guess: before increment 2 the steward observes one rendered fragment on the publishing host (for example on the pushed branch). If it resolves, the explicit-anchor design stands and legacy anchors become product's option. If it does not, the anchor design is reopened before any entry lands (grill §6) | steward (observation); architect (reopen if negative) | before increment 2 |
| Which convention governs a ratified seed ADR: supersede only, or supersede or amend? | `skills/adr-writer/SKILL.md:85-86` says the supersede flip is "the only edit a ratified ADR ever receives"; `docs/decisions/index.md:45` says "supersede or amend, never rewrite", and ADR-0002 (2026-07-23) and ADR-0003 (2026-09-14) already carry appended amendments | Not resolved here. Increment 3's ADR-0003 amendment follows `docs/decisions/index.md:45` and its two precedents. The skill's paths are `docs/graph/decisions/` in an installed project, while `docs/decisions/index.md:3-6` places the seed's own ADRs outside `docs/graph/` on purpose. The amendment corrects a count and leaves the decision alone, so it needs no new ADR. Whether the skill's rule should also bind the seed's self-docs, or the index should narrow, is the docs-librarian's call | docs-librarian | canonize of this harvest |

## 12. Changelog

- 2026-09-24 — created in `draft`: §0–§2, §4–§8, §11 by `architect`; §3 and §9
  from `product`, §10 from `tester`, spliced by the session.
- 2026-09-24 — revised by `architect` after the testability, security and
  reliability reviews. Still `draft`; the contract count is unchanged at 25.
  §4: absence now means a missing §6 required input, and an empty match
  passes; checks are called by name through `fd_guard`, and a raised check
  prints `RAISED`. `MECHANISM_CLAIMS_TRACED` traces the §6 traced surfaces,
  holds every row-linking strong claim to weakest-class hard, and covers
  glossary Enforcement fields and `enf-pre-bash-guard` wording.
  `ENFORCEMENT_ROW_COMPLETE` requires the row-specific residuals.
  `COST_FIGURES_SCOPED` requires one derived figure in the cost section.
  `BODY_FIGURES_HAVE_A_REQUIRED_HOME` exempts the project-node ceiling. The
  pending ledger must be empty once the spec is `implemented`. Prose steps
  are named by repository-relative path, and duplicate names are refused.
  §6: class order, row-specific table, traced surfaces, widened strong
  claims, evidence record, required inputs, fixture, and two C5 rows
  (reference heading levels, registration referrer). §7: seven new failure
  modes. §8: one example revised, three added. §11: nine rows.
- 2026-09-24 — `product` aligned §3 and §9 to the revision (AC-9, 10, 16, 26,
  28, 29; residuals G12, G13) and re-signed; `tester` aligned §10 (seven new
  failure rows, labels X329–X333, anchored case patterns, the `RAISED` case).
  The session closed four §11 rows that product's alignment resolved. Still
  `draft`: the tester's sign-off is taken at increment 1, when the RED cases
  exist.
- 2026-09-24 — revised by `architect` after the devils-advocate press and
  the steward's decisions D1 to D3. Still `draft`. **Contract count 25 → 22**
  (D1): `README_LATER_SECTIONS_ORDER` is a clause of `FIRST_SCREEN_ORDER`;
  `HOOK_FIRING_IS_NOT_HOLDING` is two lines of the §6 row-specific table plus
  a matrix clause of `ENFORCEMENT_ROW_COMPLETE`, and that clause now also
  requires the matrix row's ADR-0003 cell to say `not a control` (P9);
  `MEASURED_FIGURE_MATCHES_ITS_EVIDENCE` is the measured branch of
  `COST_FIGURES_SCOPED`. No RED case is dropped; each is re-homed under its
  absorbing slug. §4: `FIRST_SCREEN_ORDER` refuses a line ratchet above its
  spec cap (P7); `PENDING_LEDGER_HOLDS_ONLY_FAILING_CONTRACTS` refuses any
  member once `manifest.json` reaches `FRONT_DOOR_RELEASE` (P4). §6: four
  constants (`FIRST_HEADING_CAP`, `FIRST_SCREEN_CAP`, `FIRST_COMMAND_CAP`,
  `FRONT_DOOR_RELEASE`), the anchor premise, two row-specific lines, required
  inputs, fixture binding values. §7: `ANCHOR_NOT_RENDERED_BY_HOST`,
  `RELEASE_WITH_PENDING_LEDGER`, `LINE_CEILING_RAISED_PAST_CAP`; two modes
  re-pointed; `CLASS_CELL_UNTRUE` and `HOST_FACT_RESTATED` widened. §8: one
  output re-slugged, two examples added. §11: G9 closed; three rows added
  (anchor render, ADR amendment convention, matrix reconciliation). §0:
  security sign-off required for the Class column (P6). Owed by others:
  product (§3.5 wording, §3.6, AC-1, AC-2, AC-13, AC-27, AC-28 and the
  coverage table), tester (§10 re-keying and two new cases).
- 2026-09-24 — G9 fold to 22 contracts (steward decision): `architect`
  revised §0, §2, §4, §6–§8, §11; `product` re-mapped §3/§9 and re-signed;
  `tester` re-keyed §10 (X302, X313, X317) and added X334 and X335. The
  session aligned AC-28's release copy to `active`, matching §8 (both are
  below `implemented`).
- 2026-09-24 — `tester` wrote the increment 1 RED: 54 `case_fd_*`, the
  fixture and three `test_prose_lint_*`. §10's row files are now bare, and
  §10 records the red observation and the conventions the cases fix.
  Tester signed §0. Still `draft` until the session commits increment 1.
- 2026-09-24 — `implementer` landed the increment 1 GREEN: the 21
  `check_fd_*` in `tests/seed-lint.py`, `FRONT_DOOR_PENDING` holding the 19
  contracts observed failing on the shipped tree, and the new limits in
  `tests/ratchets.json`. Status `active`. The rows for
  EAGER_FIGURES_CHECKED_WHEREVER_PUBLISHED and the ledger's mechanics
  (PENDING_LEDGER_HOLDS_ONLY_FAILING_CONTRACTS, FIXTURE_ONLY_COVERAGE,
  CHECK_RAISED, LEDGER_REGROWS_AFTER_IMPLEMENTED, RELEASE_WITH_PENDING_LEDGER)
  are `green`: they are enforced on the shipped tree from this commit. The
  other rows stay `red` until their slug leaves the ledger.
- 2026-09-24 — class value renamed `n/a — not a control` → `not a control`
  (dash-free, so the required value does not trip the prose floor; no
  semantic change). The session's ruling, applied by `implementer` (spawn
  orchestrator.30) in §4, §6, §7, §8, §9 and §10; the class set is now
  {hard, soft, detective, judgment, not a control}. The Divergence set
  carries no dash and is unchanged.
- 2026-09-24 — increment 2: §10 rows GLOSSARY_ENTRY_COMPLETE (X305),
  GLOSSARY_PATHS_EXIST (X306), NO_UNLINKED_PROJECT_TERM_IN_DEFINITION (X307)
  and DEFINITION_HAS_ONE_HOME (X309) flipped `red` → `green`, because their
  slugs left `FRONT_DOOR_PENDING` when the glossary landed. Status column
  only; no contract changed. Applied by `docs-librarian` (spawn
  orchestrator.32) after reviewer orchestrator.31.
- 2026-09-24 — increment 7: status goes from `active` to `implemented`. §10's
  remaining 36 `red` rows and the X300 guard's `pending` flipped to `green`
  (status column only; the §10 increment-7 paragraph says which increment
  cleared each). `tests/run.sh` runs prose-lint once per file, and
  `tools/gate-registry.py --lint` refuses a prose-lint line with two `--file`
  arguments and two lines resolving to one step name. No contract changed.
  Applied by `implementer` (spawn orchestrator.38).
- 2026-09-29 — test consolidation (`docs/plans/grill-test-consolidation.md`,
  S4), by `architect`, on the owner's confirmation of that plan's §4 lines
  14-21 and 23-29. **Contract count 22 → 7.** Retired, with their §7 failure
  modes, §6 shapes and caps, §9 criteria and §10 rows: FIRST_SCREEN_ORDER,
  WHERE_NEXT_LINKS_THE_REFERENCES, GLOSSARY_ENTRY_COMPLETE,
  NO_UNLINKED_PROJECT_TERM_IN_DEFINITION, TERM_LINKED_ON_FIRST_USE,
  DEFINITION_HAS_ONE_HOME, REFERENCE_OPENS_WITH_ITS_DEFINITION,
  ENFORCEMENT_ROW_COMPLETE, LIMITS_SECTION_PRESENT, CATALOGS_OUT_OF_README,
  COST_FIGURES_SCOPED, FRONT_DOOR_HEADINGS_WELL_FORMED, LINK_TEXT_STANDS_ALONE,
  TABLES_HAVE_HEADER_ROWS and PENDING_LEDGER_HOLDS_ONLY_FAILING_CONTRACTS.
  The pending ledger (`FRONT_DOOR_PENDING`), the per-check guard and its
  `RAISED` line, the absence-is-a-finding rule, the coverage binder and the
  fixture-robustness failures (VACUOUS_PASS_ON_ABSENT_TEXT,
  FIXTURE_ONLY_COVERAGE, UNREADABLE_INPUT, CHECK_RAISED) leave the text.
  MECHANISM_CLAIMS_TRACED is narrowed to "each named mechanism path exists"
  (the paths in the enforcement rows' Artifact cells), and it and
  GLOSSARY_PATHS_EXIST are rows of the anchors check. The two figure contracts
  are scope rows of one published-figures check. What the retired contracts
  held is judged by the reviewer (§3 note). §1, §2, §5, §8 and §11 are cut to
  match; §3 keeps product's text with a note, and §3.6 keeps the prose-floor
  paragraph only. The status stays `implemented`.

