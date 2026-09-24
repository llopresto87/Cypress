---
status: active
status_date: 2026-09-24
owner: architect
status_evidence: tests/test-seed-lint.sh, tests/fixtures/front-door/, tests/seed-lint.py, tests/test_gate_registry.py (RED landed with this promotion; §10 says which rows are red)
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
- **Sign-offs:** product [x] 2026-09-24 (§3, §9 re-mapped to the 22 contracts after the fold of three into FIRST_SCREEN_ORDER, COST_FIGURES_SCOPED and ENFORCEMENT_ROW_COMPLETE, steward decision D1: AC-1, AC-13, AC-27 and the coverage table re-mapped; AC-2 names the §6 caps; AC-28 and §3.6 carry the 7.29.0 release clause; §3.2 and §3.5 say links target the entry anchor, host rendering unrecorded; earlier alignment kept: strong-claim list and weakest-class rule, traced surfaces, row-specific residuals, `RAISED` and the implemented-empty ledger, repo-relative prose steps; host tiers and "Try it" resolved in §3.1; G3, G8, G11 accepted residuals per §11) · architect [x] · tester [x] 2026-09-24 (§10 matches the increment 1 RED as written: 54 `case_fd_*` in `tests/test-seed-lint.sh` over the fixture in `tests/fixtures/front-door/`, labels X300 to X335 with X325 unassigned; three `test_prose_lint_*` in `tests/test_gate_registry.py`, `expectedFailure` until increment 7; every case except the X300 guard observed failing for the missing behaviour; the row files are bare) · security [ ] required (2026-09-24, press P6): the Class column of the §17 enforcement table, signed row by row against ADR-0003 at verify of increment 3 (§7 `CLASS_CELL_UNTRUE`); the rest of the spec is documentation and lint code with no auth, secret, upload, external call or model action

## 1. Summary

This spec covers the seed's front door: `README.md`, the glossary and a new
enforcement section in `DOCUMENTATION.md`, the openers of the three
references in `documentation/`, and the `tests/seed-lint.py` checks that hold
them. It turns the reader-order rewrite into mechanical contracts, so that a
first reader learns what the seed is, who it is for, what an install writes
into their repository, what it costs and how to try it before meeting a coined
word; every borrowed or coined term links to one glossary entry that states
its field meaning, where the seed departs from it, and the files that
implement it; and every enforcement claim links a row that states its
ADR-0003 class and what it can miss, and a strong claim ("cannot",
"prevents", "blocks") links only rows whose weakest class is hard. It also
moves every README-coupled check to the fact's new home at the same strength
or stricter, and splits the prose-floor gate step so one file's excess cannot
hide in another's slack.
Every contract is decided by `tests/seed-lint.py`,
`tests/test-seed-lint.sh` or `tests/test_gate_registry.py`, never by a reader.

## 2. Scope

- **In scope:**
  - README section order, headings, first-screen boundary and line budgets
  - the install section's named target paths
  - the glossary entry grammar, required headwords, anchors and field value sets
  - the enforcement section's row grammar, required rows and class cells
  - term linking on first use in README, and project-term linking inside
    glossary definitions
  - mechanism-verb tracing in the traced surfaces (§6: README, `INSTALL.md`,
    `integrations/*/README.md`, the glossary's Here and Enforcement fields),
    and overclaim refusal wherever a front-door unit links an enforcement row
  - row-specific residuals the enforcement table must name (§6)
  - the limits section
  - catalog and ADR-range limits in README and the front-door files
  - cost-figure scope, provenance and evidence agreement in README
  - near-duplicate definitions across the front-door files
    (`DEFINITION_HAS_ONE_HOME`)
  - the reference openers, and the level of four part headings in two
    references (`#` to `##`; no heading text, table row or roles block moves)
  - anchor resolution, heading hierarchy, link text and table headers
  - the C5 moves: the README-coupled checks re-pointed to the fact's new home
    (§6, "README-coupled checks after the move")
  - the pending ledger that lets the RED checks land before the prose, and
    its refusal once the spec is `implemented` or the release version is set
  - the spec caps on the first-screen line ceilings
  - the per-file prose-lint gate step
- **Out of scope:**
  - any change to mechanism: hooks, `install.sh`, the shipped plant linters,
    `prose-lint.py`'s own rules
  - host-release facts that contradict seed method nodes (hooks reaching
    subagents, the spawn tool's name, spawn-depth limits, agent-directory
    registration). They are routed to a separate change. On these subjects
    README, the glossary's Here and Enforcement fields, the enforcement rows
    and the ADR-0003 amendment say only that behaviour is host-dependent and
    link the matrix. No check here holds that; it is judged at verify
    (§7 `HOST_FACT_RESTATED`)
  - machinery nodes that ship to installed projects (`core/`, `protocols/`,
    `skills/`, `agents/`, `templates/`). Where one owns a definition, the
    glossary glosses and links it, and `DEFINITION_HAS_ONE_HOME` does not scan
    it, because `install.sh` places no front-door file into a project (§5)
  - the reader test (product's detective AC-18): recorded evidence, never a
    gate
  - whether any sentence is true. Every check here holds shape, presence,
    linkage and agreement with a derived value; truth stays with the reviewer
  - the removal of plant-identifying tokens left by earlier harvests, and the
    version bump. Both are plan increments with no behavior contract
    (grill §9)
  - whether the publishing host resolves an explicit `<a id>` fragment in
    rendered Markdown. It is not recorded. Every anchor contract here assumes
    it, so it is a do-not-guess prerequisite of the glossary increment,
    observed once by the steward on the publishing host (grill §6, §9
    increment 2), never a check (§7 `ANCHOR_NOT_RENDERED_BY_HOST`)
- **Front-door files** (a term used throughout): `README.md`,
  `DOCUMENTATION.md`, `documentation/*.md`, `INSTALL.md` and
  `integrations/*/README.md`.

## 3. User-facing behavior

(Authored by `product`.)

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

The seed's maintainer lands the checks before the prose conforms. While the
rewrite is in progress, the gate still reports each unfinished check by name,
with its count of findings on every run. A check that has started passing
cannot stay excused, so the excused list only shrinks. A check that crashes
is reported as crashed, with the error's type, never as findings, and it
fails the run even while excused. Once the spec is marked implemented, the
excused list must be empty and cannot be refilled without first reopening the
spec. The same holds for the release: once the seed's manifest version is
7.29.0 or later, the excused list must be empty whatever the spec's status,
so a release cannot be stamped while checks are still excused. The prose floor is measured per file, and each file's step is named by
its path from the repository root, so one file's excess cannot hide behind
another file's slack and two files with the same name cannot merge into one
step. The maintainer can decide from one gate run what is left to rewrite.

---

## 4. Functional contracts

(Authored by `architect`. Reviewed by `tester` for testability.)

Every contract below is a check in `tests/seed-lint.py` unless it names
another file. Each seed-lint contract is one function `check_fd_<name>`,
called by name on its own line by the front-door dispatcher
(`with fd_guard("<SLUG>"): check_fd_<name>()`). No table of functions
dispatches them, so the live-check parse of `tests/check-coverage-binder.py`
(`^\s+(check_[a-z0-9_]+)\(`, `:93`) sees every one.

A finding is one line of the form
`front-door: <SLUG>: <file>:<line>: <message>`, with line `0` when the
finding is about a whole file or a missing input. It makes seed-lint exit 1,
except while its slug is in `FRONT_DOOR_PENDING`
(`PENDING_LEDGER_HOLDS_ONLY_FAILING_CONTRACTS`). A check that raises prints
`front-door: <SLUG>: RAISED <ExceptionType>: <message>` and makes seed-lint
exit 1 whether or not its slug is pending (§7 `CHECK_RAISED`). "Body text",
"unit", "inline link", "linked", "path-like" and every constant are defined
in §6.

**Absence is a finding; an empty match is not.** Each seed-lint contract
reads the inputs §6 "Required inputs" lists for it. When one is missing (a
file, a section, a region, a table, or a parse that yields fewer items than
the table's minimum), the check emits one finding per missing input, naming
it, and still checks the inputs that are present. When every required input
is present and parsed, a check whose pattern matches nothing passes: a README
with no mechanism verb has nothing to trace. So a check whose subject arrives
in a later increment (the glossary entries, the enforcement rows) fails on
the tree from the RED increment on, and cannot pass by accident and then turn
red when its subject lands. This rule is part of every contract below and is
not repeated in each.

**Planted cases.** Every planted case runs on a hermetic copy (the
`fresh`/`expect_fail` pattern of `tests/test-seed-lint.sh`) whose
`FRONT_DOOR_PENDING` is rewritten to the empty set, with the conforming
fixture laid in by §6 "Fixture". A case's expected line is
`front-door: <SLUG>: <file>:` of its plant, with the plant's line where the
plant has one, plus a message fragment unique to the plant. A case fails if
the copy's output holds any `: RAISED ` line. The fixture's clean run
produces no `front-door: ` line.

### README shape

### Contract: FIRST_SCREEN_ORDER
- **Given:** `README.md`
- **When:** seed-lint reads its `##` headings outside fenced blocks
- **Then:** the first five `##` headings are, byte for byte and in this order,
  the first five rows of the §6 README heading table, with no other `##`
  heading before or between them
- **And:** the first `##` heading sits on a line no greater than
  `FIRST_HEADING_MAX_LINE`
- **And:** exactly one line equal to `FIRST_SCREEN_MARKER` exists; it lies
  after the fifth heading and before the next `##` heading, on a line no
  greater than `FIRST_SCREEN_MAX_LINES`
- **And:** the first fenced block in README whose info string is `sh` opens
  under `## Try it`, and its first line containing `install.sh` sits on a line
  no greater than `FIRST_COMMAND_LINE`
- **And:** no `##` heading anywhere in README equals `## What you get`
- **And:** among the `##` headings after `FIRST_SCREEN_MARKER`, rows six to
  nine of the §6 README heading table appear as an ordered subsequence, each
  exactly once, byte for byte; other `##` headings may sit between or after
  them (absorbed 2026-09-24 from the former `README_LATER_SECTIONS_ORDER`,
  steward decision D1)
- **And:** the recorded values of `FIRST_HEADING_MAX_LINE`,
  `FIRST_SCREEN_MAX_LINES` and `FIRST_COMMAND_LINE` in `tests/seed-lint.py`
  are no greater than `FIRST_HEADING_CAP`, `FIRST_SCREEN_CAP` and
  `FIRST_COMMAND_CAP`, which seed-lint reads from this spec's §6 constants
  table. The finding names `tests/seed-lint.py`, the constant, its value and
  its cap. A ratchet raised by editing `tests/ratchets.json` in the same diff,
  which `ratchet-lint.py` alone would accept, is refused unless this spec
  changes first

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

### Contract: WHERE_NEXT_LINKS_THE_REFERENCES
- **Given:** the README section headed `## Where to go next`
- **When:** seed-lint reads its inline links
- **Then:** it holds one inline link to each target in the §6 where-next list,
  each target resolving under the seed root (and its fragment, where it has
  one, resolving under `FRONT_DOOR_ANCHORS_RESOLVE`)

### Glossary

### Contract: GLOSSARY_ENTRY_COMPLETE
- **Given:** the glossary region of `DOCUMENTATION.md` (§6)
- **When:** seed-lint parses it into entries by the §6 entry grammar
- **Then:** every entry has its `term-` anchor on the line after its `###`
  headword and exactly the seven labelled fields Forms, Here, Field,
  Implemented at, Enforcement, Divergence, Why, once each, in that order,
  each non-empty after its label
- **And:** Forms includes the headword itself, case-insensitively
- **And:** Enforcement carries at least one bolded class value, and every
  bolded token in it is in the §6 class set
- **And:** Divergence carries at least one bolded divergence value, and every
  bolded token in it is in the §6 divergence set
- **And:** Field satisfies the §6 Field rule and Why the §6 Why rule
- **And:** every headword in the §6 required-headword list has an entry

### Contract: GLOSSARY_PATHS_EXIST
- **Given:** every entry's Implemented at field
- **When:** seed-lint reads its backticked tokens
- **Then:** every path-like token outside an "An install produces" clause
  resolves under the seed root by the §6 seed-path rule, including any `:N` or
  `:N-M` suffix
- **And:** every path-like token inside such a clause passes the §6
  install-literal rule, and every backticked bare identifier inside such a
  clause names a function defined in `install.sh`
- **And:** a field with no path-like token begins with `n/a`

### Contract: NO_UNLINKED_PROJECT_TERM_IN_DEFINITION
- **Given:** the glossary entries, and the project terms among them (§6)
- **When:** seed-lint scans each entry's Here field as body text
- **Then:** the first occurrence in that field of any form of another project
  term lies inside an inline link whose target is `#term-<that entry's id>`
  (or `DOCUMENTATION.md#term-<id>`)
- **And:** the entry's own forms are exempt

### Contract: TERM_LINKED_ON_FIRST_USE
- **Given:** `README.md`, and every glossary entry whose Divergence is not
  exactly `**same**`
- **When:** seed-lint finds, for each such entry, the first occurrence in
  README body text of any of its forms (§6 matching rules)
- **Then:** that occurrence lies inside the text of an inline link whose
  target is `DOCUMENTATION.md#term-<the entry's id>`
- **And:** an entry none of whose forms occurs in README body text passes

### Contract: DEFINITION_HAS_ONE_HOME
- **Given:** every sentence of every entry's Here field, and every unit of the
  front-door files outside the glossary region that contains a form of that
  entry
- **When:** seed-lint compares them by the §6 overlap metric
- **Then:** no pair reaches `DEFINITION_OVERLAP_CEILING`
- **And:** the finding names both the entry and the unit's `file:line`, and
  the overlap to two decimals

### Contract: REFERENCE_OPENS_WITH_ITS_DEFINITION
- **Given:** `documentation/agents-reference.md`,
  `documentation/skills-and-templates-reference.md` and
  `documentation/protocols-reference.md`
- **When:** seed-lint reads the first paragraph after each file's `#` title
- **Then:** its first sentence matches that file's opener pattern in §6
- **And:** the paragraph holds an inline link to that file's required
  glossary anchor in §6

### Enforcement

### Contract: ENFORCEMENT_ROW_COMPLETE
- **Given:** the enforcement region of `DOCUMENTATION.md` (§6)
- **When:** seed-lint parses its table by the §6 row grammar
- **Then:** every body row has five non-empty cells, its first cell begins
  with an `enf-` anchor, its Class cell carries at least one bolded class value
  with every bolded token in the §6 class set, and its Artifact cell holds at
  least one path-like backticked token resolving by the §6 seed-path rule
- **And:** every id in the §6 required-row list is present
- **And:** every row named in the §6 row-specific table carries, in its What
  it can miss cell, a match for each pattern that table lists for it, and
  meets that table's class rule; this includes `enf-route-hook` and
  `enf-status-hook`, whose Class cells contain `**not a control**`
- **And:** in the class table of `documentation/host-capability-matrix.md`,
  the row whose first cell is `**mechanically enforced**` has a Meaning cell
  containing `injects` and an ADR-0003 cell containing `not a control`, so the
  matrix cannot map a hook that only injects text to `hard` while the rows
  class it as no control (absorbed 2026-09-24 from the former
  `HOOK_FIRING_IS_NOT_HOLDING`, steward decision D1; the ADR-0003-cell
  half is new, press P9)

### Contract: MECHANISM_CLAIMS_TRACED
- **Given:** the §6 traced surfaces, and every other front-door file outside
  the enforcement region
- **When:** seed-lint splits their body text into units and matches the §6
  mechanism-verb and strong-claim patterns, with code spans and link targets
  masked
- **Then:** every unit of a traced surface that matches the mechanism-verb
  pattern holds an inline link to `DOCUMENTATION.md#enf-<id>` (`#enf-<id>`
  inside `DOCUMENTATION.md`) for an existing row
- **And:** in every front-door file outside the enforcement region, a unit
  that matches the strong-claim pattern, is not negated (§6), and links at
  least one `enf-` row, links only rows whose weakest class (§6 class order)
  is `hard`; otherwise the finding reads as an overclaim and names each linked
  row with its weakest class
- **And:** a glossary Enforcement field carrying any bolded class other than
  `not a control` links at least one `enf-` row; every bolded class in
  the field occurs in the Class cell of a row it links; and `**hard**` in the
  field requires a linked row whose weakest class is `hard`
- **And:** no unit that links `enf-pre-bash-guard` matches the §6
  `guard_misnomer` pattern

### Contract: LIMITS_SECTION_PRESENT
- **Given:** the README section headed `## What it does not do`
- **When:** seed-lint reads it
- **Then:** it holds exactly the two subsections `### Requested, not enforced`
  and `### Not yet measured`, in that order
- **And:** the first holds at least `LIMITS_MIN_REQUESTED` list items, each
  with an inline link to an `enf-` row whose Class cell carries at least one
  bolded value other than `**hard**`, and those items together link
  `enf-tier-classification`, `enf-spec-before-code` and
  `enf-test-before-code`
- **And:** the second holds at least `LIMITS_MIN_UNMEASURED` list items, each
  containing `not recorded`, `not measured` or `measured once`

### Catalogs and figures

### Contract: CATALOGS_OUT_OF_README
- **Given:** `README.md`, and the name sets derived from disk (§6 catalog
  counting)
- **When:** seed-lint counts, per category, the distinct names README's body
  text names by the §6 counting rule
- **Then:** no category exceeds `README_CATALOG_CEILING`
- **And:** no front-door file matches the §6 ADR-range pattern

### Contract: COST_FIGURES_SCOPED
- **Given:** `README.md`, and the derived set of §6
- **When:** seed-lint finds every figure (§6 figure pattern) in README body
  text, a range contributing both endpoints
- **Then:** the figure's unit contains a scope marker from §6
- **And:** the figure is either derived (its value is in the derived set and
  its unit contains `computed`, or the value is a limit constant and the unit
  contains `budget`, `ceiling` or `limit`) or measured (its unit contains
  `measured once` or `measured <YYYY-MM-DD>` and an inline link to an evidence
  record under `docs/` that resolves, and the figure, number and unit
  together, occurs in that record's text once both are normalized by the §6
  figure normalization, a range contributing each endpoint). The measured
  branch absorbed the former `MEASURED_FIGURE_MATCHES_ITS_EVIDENCE` on
  2026-09-24 (steward decision D1)
- **And:** a unit holding a derived figure contains no §6 `measur_word`
- **And:** within the section headed `## What it costs`, a unit containing a
  §6 `measur_word` holds an inline link to an evidence record under `docs/`
- **And:** that section holds at least one derived figure. README need not
  hold a measured figure: a figure with no clean evidence record (§6
  "Evidence record") is written `not measured` instead

### Contract: EAGER_FIGURES_CHECKED_WHEREVER_PUBLISHED
- **Given:** every front-door file
- **When:** `check_published_eager_figures`' figure and historical-marker rule
  runs over it
- **Then:** every always-loaded byte figure it finds equals a value that
  `check_eager_surface` computes, or `EAGER_BUDGET`
- **And:** the existing pair (`README.md`,
  `documentation/host-capability-matrix.md`) is never subject to
  `FRONT_DOOR_PENDING`

### Contract: BODY_FIGURES_HAVE_A_REQUIRED_HOME
- **Given:** `BODY_FIGURE_HOME` (§6)
- **When:** `check_published_body_figures` runs
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

### Integrity and accessibility

### Contract: FRONT_DOOR_ANCHORS_RESOLVE
- **Given:** every front-door file
- **When:** seed-lint reads every inline link whose fragment begins `term-`
  or `enf-`, or equals `glossary` or `enforcement`
- **Then:** the fragment names exactly one explicit anchor (§6) in the file
  the link targets
- **And:** every explicit anchor id in `DOCUMENTATION.md` is unique
- **And:** every inline link in README whose target is a relative path
  resolves to an existing file under the seed root

### Contract: FRONT_DOOR_HEADINGS_WELL_FORMED
- **Given:** `README.md`, `DOCUMENTATION.md` and the three references
- **When:** seed-lint reads their ATX headings outside fenced blocks
- **Then:** each file has exactly one level-1 heading, it is the first
  heading, and no heading's level exceeds the previous heading's level by more
  than one

### Contract: LINK_TEXT_STANDS_ALONE
- **Given:** `README.md`, the glossary region and the enforcement region
- **When:** seed-lint reads every inline link's text, markup stripped
- **Then:** no link text is empty, equals a §6 generic link text
  case-insensitively, or begins with `http://`, `https://` or `www.`

### Contract: TABLES_HAVE_HEADER_ROWS
- **Given:** `README.md`, the glossary region and the enforcement region
- **When:** seed-lint finds every table (§6)
- **Then:** every header cell is non-empty after markup and whitespace are
  stripped

### Gate mechanics

### Contract: PENDING_LEDGER_HOLDS_ONLY_FAILING_CONTRACTS
- **Given:** `FRONT_DOOR_PENDING` in `tests/seed-lint.py`, mirrored in
  `tests/ratchets.json` with direction `set`
- **When:** seed-lint runs over the tree
- **Then:** a slug in the set whose check produces findings prints one
  `front-door: PENDING <SLUG>: <n> finding(s); first: <finding>` line and does
  not change the exit status
- **And:** a slug in the set whose check produces zero findings is itself a
  finding (`stale pending entry: remove it`), so the set holds only contracts
  observed failing
- **And:** a member that is not a `### Contract:` slug of this spec checked by
  seed-lint, or that is this contract's own slug, is a finding; so neither
  this contract nor `PROSE_FLOOR_HELD_PER_FILE` can be made pending
- **And:** when the frontmatter `status:` of
  `docs/specs/SPEC-0004-front-door.md` is `implemented`, any member of
  `FRONT_DOOR_PENDING` is a finding (`ledger must be empty once SPEC-0004 is
  implemented`). Re-adding a slug after the harvest is then refused even when
  `tests/ratchets.json` is edited in the same diff, which `ratchet-lint.py`
  alone would accept
- **And:** when the `version` of `manifest.json`, compared as a tuple of
  integers, is at least `FRONT_DOOR_RELEASE`, any member of
  `FRONT_DOOR_PENDING` is a finding (`ledger must be empty from
  <FRONT_DOOR_RELEASE>`), whatever this spec's status. A stalled branch
  whose spec never reached `implemented` therefore cannot be stamped with
  the front-door release (press P4, 2026-09-24)

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
  `--lint` exit 1 naming both lines. Today the second merges silently into
  the first (`tools/gate-registry.py:473`). The refusal covers prose-lint
  names only; whether any other tool legitimately appears twice in
  `tests/run.sh` is not recorded
- **Test file:** `tests/test_gate_registry.py`, not seed-lint

## 5. Non-functional requirements

Global posture is grill §4; only what binds these checks is listed.

- **Boundary:** every artifact here is seed-side. `install.sh` places none of
  the front-door files: its `place_tree` calls name `protocols`,
  `core/method`, `agents` and `templates` (`install.sh:815-827`), the corpora
  go through `place_legal_corpus`, and `README.md` appears only in skip
  patterns (`:758`, `:1393`, `:1498`). A definition an installed project needs
  therefore keeps its home in the machinery node that ships.
- **Performance:** text scans over the front-door files, `install.sh` and the
  name sets; the overlap comparison is bounded by entries × units that contain
  a form. Target well under one second on the gate host. Not gated; observed
  at verify.
- **Compatibility:** stdlib Python 3 only (`re`, `pathlib`, `json`); planted
  cases in bash 3.2-compatible shell; no new dependency.
- **Reliability:** deterministic: no network, no clock, no randomness, no
  dependence on file order beyond sorted globs. An unreadable or undecodable
  input is a finding naming the path, never a skip. An exception inside a
  front-door check is caught by `fd_guard` and reported as a `RAISED` line
  under that check's slug (§4), never swallowed and never counted as a
  finding the check observed.
- **Accessibility:** the Markdown floor is held by
  `FRONT_DOOR_HEADINGS_WELL_FORMED`, `LINK_TEXT_STANDS_ALONE`,
  `TABLES_HAVE_HEADER_ROWS` and the explicit anchors of §6. Meaning carried
  only by emphasis is judged at verify (§11).
- **Honesty of the gate:** every new constant is recorded in
  `tests/ratchets.json` at its strict value (§6). The seed-lint entry in
  `tools/gate-registry.py` names the residual false greens of §7.

## 6. Data shapes

### Constants

| Name | Value | Ratchet direction |
|---|---|---|
| `FIRST_SCREEN_MARKER` | the line `<!-- first-screen-end -->`, exactly | not a ratchet |
| `FIRST_HEADING_MAX_LINE` | 6; never above `FIRST_HEADING_CAP` | `max` |
| `FIRST_SCREEN_MAX_LINES` | at most `FIRST_SCREEN_CAP`; recorded at the marker's measured line when the README increment lands | `max` |
| `FIRST_COMMAND_LINE` | at most `FIRST_COMMAND_CAP`; recorded at the measured line of the first `install.sh` command when the README increment lands | `max` |
| `FIRST_HEADING_CAP` | 6 | not a ratchet; home is this row, read by seed-lint (`FIRST_SCREEN_ORDER`) |
| `FIRST_SCREEN_CAP` | 100 | not a ratchet; home is this row, read by seed-lint (`FIRST_SCREEN_ORDER`) |
| `FIRST_COMMAND_CAP` | 80 | not a ratchet; home is this row, read by seed-lint (`FIRST_SCREEN_ORDER`) |
| `FRONT_DOOR_RELEASE` | `7.29.0` | not a ratchet; the release from which `FRONT_DOOR_PENDING` must be empty (`PENDING_LEDGER_HOLDS_ONLY_FAILING_CONTRACTS`) |
| `README_CATALOG_CEILING` | 3 per category | `max` |
| `LIMITS_MIN_REQUESTED` | 3 | `min` |
| `LIMITS_MIN_UNMEASURED` | 2 | `min` |
| `DEFINITION_OVERLAP_CEILING` | 0.50 | `max` |
| `DEFINITION_SHINGLE` | 3 content tokens | not a ratchet |
| `DEFINITION_MIN_TOKENS` | 5 content tokens | not a ratchet |
| `BODY_FIGURE_HOME` | `DOCUMENTATION.md` | not a ratchet |
| `PROJECT_NODE_LINE_FIGURES` | {150, 170}: the project-node body ceiling of `templates/knowledge-graph/graph-lint.py:860-861`, a different fact from the seed's body figures | not a ratchet; each value must occur in that file (§4) |
| `FRONT_DOOR_PENDING` | the §4 slugs observed failing on the tree when the RED increment lands | `set` (members only leave); empty once SPEC-0004 is `implemented` |

~~"At most" values bound the ratchet; the ratchet may fall below them and never
rises above them without a spec change.~~ (superseded 2026-09-24 by the next
paragraph: nothing held the bound)

**Caps (2026-09-24, press P7).** A cap bounds its ratchet, and
`FIRST_SCREEN_ORDER` refuses a recorded value above it. The caps' only home
is the table above: seed-lint reads each `*_CAP` row from this file, so
raising a cap is a spec change that a lock edit cannot make. The three
ratchets are still recorded at the measured line, with zero headroom. Headroom
was weighed and not chosen. It would widen a budget (harvest G11), and slack
nothing uses bounds no drift. The brittleness it would buy off is already
handled: the finding names the line, the ceiling and trimming as the fix
(grill §11). Once the caps hold, "the caps bound how far repeated lock edits
can drift" is a fact the gate checks, not a hope.

### README heading table

| # | Heading line, exact | Part of the first screen |
|---|---|---|
| 1 | `## What CYPRESS is` | yes |
| 2 | `## Who it is for and not for` | yes |
| 3 | `## What installing does to your repository` | yes |
| 4 | `## What it costs` | yes |
| 5 | `## Try it` | yes |
| 6 | `## How it works` | no |
| 7 | `## Why it is built this way` | no |
| 8 | `## What it does not do` | no |
| 9 | `## Where to go next` | no |

A section runs from its heading to the line before the next `##` heading or
the end of the file. Line numbers are 1-based physical lines of the file.

### Body text and units

```yaml
body_text:
  excludes:
    - fenced blocks: from a line opening ``` or ~~~ to its closing fence
    - ATX heading lines: ^#{1,6}\s
    - HTML comments, and explicit anchor tags
  masks_for_matching:                # replaced by spaces, so positions hold
    - inline code spans: a backtick run to the next equal run
    - inline link targets: the "(...)" part of [text](target)
  keeps: link text, table cells, list items, block quotes
unit:
  paragraph: lines separated by blank lines; a list item or a table row starts its own
  table_row: one unit per body row
  sentence_split: at [.!?] followed by whitespace and then [A-Z], "[", "`", "*" or "("
  no_split_after: ["e.g.", "i.e.", "etc.", "vs."]
inline_link:
  form: "[text](target)"          # reference-style links are not resolved and never count as linked
  linked_occurrence: the occurrence lies inside the link's text span
path_like: a backticked token containing "/" or ending in .md .py .sh .json .ts .tsv .yml .toml
```

### Term matching

```yaml
forms: the comma-separated values of an entry's Forms field, trimmed
match:
  case: insensitive
  left_boundary:  not preceded by [A-Za-z0-9_-]
  right_boundary: not followed by [A-Za-z0-9_-]
  overlap: at one position the longest form wins; a form nested inside a longer matched form is not an occurrence
  inflection: none inferred; every inflection the prose uses is a listed form
project_term: an entry whose Divergence contains **no standard meaning**
```

### Explicit anchors

```yaml
anchor_tag: '<a id="ID"></a>'      # on its own line, or at the start of a table cell
ids:
  glossary_region: "glossary"      # on the line after the glossary's ## heading
  enforcement_region: "enforcement"
  entry: '^term-[a-z0-9]+(-[a-z0-9]+)*$'
  row:   '^enf-[a-z0-9]+(-[a-z0-9]+)*$'
uniqueness: every id occurs once in DOCUMENTATION.md
premise:    the publishing host resolves "#ID" to this tag in rendered Markdown. Not recorded;
            observed once before the glossary increment (§2, grill §9 increment 2). The
            checks here hold that the id exists and is unique, never that a browser lands on it
```

### Glossary region and entry grammar

The region runs from the heading `## 15. Glossary` (next non-blank line
`<a id="glossary"></a>`) to the next `##` heading. The section keeps its
number.

```markdown
### <headword>
<a id="term-<slug>"></a>

- **Forms:** <form>, <form>, …
- **Here:** <plain meaning; other project terms linked>
- **Field:** <paraphrased standard meaning> (<source>, <https URL>, retrieved <YYYY-MM-DD>; status: verified)
- **Implemented at:** `<seed path>`, … An install produces `<target path>` (`<install.sh function>`).
- **Enforcement:** **<class>** …
- **Divergence:** **<value>** …
- **Why:** <ADR-NNNN | SPEC-NNNN | docs/plans/… | `<commit>` | path:line | not recorded>
```

A field continues on indented lines until the next label.

```yaml
class_set:      ["hard", "soft", "detective", "judgment", "not a control"]
class_order:    hard > soft > detective > judgment > not a control     # strongest first
weakest_class:  the lowest class in class_order among the bolded class values of one cell or field;
                a row carrying several classes (per host, per case) is judged by its weakest
divergence_set: ["same", "narrower", "broader", "different", "no standard meaning"]
field_rule:
  either: the field contains "no standard meaning"
  or:     the field contains at least one "status: verified", "status: secondhand" or "status: not recorded"
  and:    every "status: verified" has an https:// URL and a YYYY-MM-DD date in the same field
why_rule:
  matches_any: ['\bADR-\d{4}\b', '\bSPEC-\d{4}\b', 'docs/plans/\S+', '`[0-9a-f]{7,40}`', '\S+\.[a-z]{1,4}:\d+', 'kernel §\d+(\.\d+)?', '^not recorded$']
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

**Required headwords and ids.** agent `term-agent`; subagent `term-subagent`;
orchestrator `term-orchestrator`; workflow `term-workflow`; skill
`term-skill`; tool `term-tool`; hook `term-hook`; kernel `term-kernel`;
context window `term-context-window`; progressive disclosure
`term-progressive-disclosure`; knowledge graph `term-knowledge-graph`; node
`term-node`; router `term-router`; routing `term-routing`; specification
`term-specification`; test-first development `term-test-first`; gate
`term-gate`; linter `term-linter`; harness `term-harness`; seed `term-seed`;
plant `term-plant`; growth `term-growth`; graft `term-graft`; harvest
`term-harvest`; canonize `term-canonize`; tier `term-tier`; protocol
`term-protocol`; corpus `term-corpus`; handback `term-handback`; coordinator
`term-coordinator`; leaf `term-leaf`; specialist `term-specialist`; expert
`term-expert`; steward `term-steward`; one home per fact
`term-one-home-per-fact`; turn `term-turn`; toolcraft `term-toolcraft`;
machinery `term-machinery`; brief `term-brief`; reverse loop
`term-reverse-loop`. More entries may be added; none of these may go.

A multi-sense word (leaf, corpus, tier, tool, harness, gate) has one entry
that names every sense and the sense README uses. A term whose definition an
installed project needs keeps its home in the machinery node; its Here field
is a one-line gloss plus a link to that node.

### Enforcement region and row grammar

The region runs from the heading `## 17. What is enforced, and how` (next
non-blank line `<a id="enforcement"></a>`) to the next `##` heading or the
end of the file. It is appended after §16, so no existing section number
moves. It holds one table:

```markdown
| Mechanism | Artifact | Class | What it can miss | Detail |
|---|---|---|---|---|
| <a id="enf-<slug>"></a><mechanism> | `<seed path>` … | **<class>** … | <residual> | <link to the owning detail, or `none`> |
```

Host variance is never a cell; the Detail cell links the matrix.

**Required row ids.** `enf-kernel-load`, `enf-kernel-budget`,
`enf-tool-allowlist`, `enf-leaf-cannot-spawn`, `enf-delegation-frontmatter`,
`enf-route-hook`, `enf-status-hook`, `enf-pre-bash-guard`,
`enf-injection-dedup`, `enf-backup-before-replace`, `enf-plant-files-kept`,
`enf-install-preflight`, `enf-install-stamp`, `enf-registration-notice`,
`enf-graph-lint`, `enf-spec-lint`, `enf-grill-lint`, `enf-agent-lint`,
`enf-prose-lint`, `enf-agnosticism-lint`, `enf-status-register`,
`enf-growth-audit`, `enf-graft-audit`, `enf-tier-classification`,
`enf-protocol-order`, `enf-spec-before-code`, `enf-test-before-code`,
`enf-verify-gates`, `enf-canonize`, `enf-attribution`, `enf-brief-block`,
`enf-charter-duties`, `enf-lifecycle-gate-rows`, `enf-steward-only`,
`enf-seed-gate`, `enf-ratchets`.

**Row-specific requirements.** Security's review named residuals four rows
must state. The patterns hold that each residual is named, not that the row is
true; the Class column is signed row by row by `security` against ADR-0003
(judgment, §7 `CLASS_CELL_UNTRUE`).

| Row | What it can miss matches each of (case-insensitive) | Class rule |
|---|---|---|
| `enf-tool-allowlist` | `\bBash\b`; `role emulation`; `` `?tools:`? `` (an omitted `tools:` line) | weakest class is not `hard` |
| `enf-leaf-cannot-spawn` | `spawn[- ]tool` (another name for the spawn tool); `role emulation`; `` `?tools:`? `` | weakest class is not `hard` |
| `enf-pre-bash-guard` | `fails? open`; `(indirection\|evasion\|evade)`; `\bhosts?\b` | weakest class is not `hard`; `**hard**` may appear only for "a matched command on a host that fires the hook" |
| `enf-backup-before-replace` | `` `?\.cypress/seed\.json`? `` | none |
| `enf-route-hook` | none | Class cell contains `**not a control**` |
| `enf-status-hook` | none | Class cell contains `**not a control**` |

The last two rows came from the former `HOOK_FIRING_IS_NOT_HOLDING`
(2026-09-24, D1). A hook that only injects text fires and holds nothing, and
the matching matrix clause is part of `ENFORCEMENT_ROW_COMPLETE` (§4).

### Traced surfaces

```yaml
traced_surfaces:          # every mechanism-verb unit here links a row
  - README.md
  - INSTALL.md
  - integrations/*/README.md           # at least one must exist
  - the glossary region's Here and Enforcement fields
overclaim_scope:          # a strong claim that links a row is held to weakest-class hard
  - every front-door file, enforcement region excluded (a row is its own trace)
not_traced:               # the manual prose and the references are the detail homes rows link to
  - DOCUMENTATION.md outside the glossary fields above
  - documentation/*.md
  residual: STRONG_CLAIM_IN_MANUAL_PROSE (§7)
```

### Mechanism verbs

```yaml
mechanism_verb: '(?i)\b(enforc\w*|ensur\w*|prevent\w*|requir\w*|block\w*|guarantee\w*|gates?|gated|gating|refus\w*|reject\w*|forbid\w*|guard\w*|stops?|cannot|can''t|never|hard|prove[ns]?|proven)\b'
strong_claim:   '(?i)\b(hard|cannot|can''t|guarantee\w*|ensur\w*|prevent\w*|block\w*|refus\w*|stops?)\b'
strong_claim_negated: a strong-claim word with not, no, nothing, none, never, without or a word ending in n't among the three words before it is not a strong claim ("nothing here is hard", "no tool blocks it")
not_strong:     "never" and "only" stay out of strong_claim. "never" states an absence as often as a hold, and the limits section is built from such sentences; "only" is mostly a quantifier ("installing only places files"), and scoping a sentence is the recovery §7 OVERCLAIM prescribes. "never" is still a mechanism verb, so on a traced surface it links a row
guard_misnomer: '(?i)\b(secur\w*|sandbox\w*|protect\w*)\b'
matched_on: unit body text with code spans and link targets masked
```

### Catalog counting

```yaml
name_sets:
  agents:    the name: frontmatter value of each agents/*.md
  protocols: the stem of each protocols/*.md
  skills:    the directory name of each skills/*/SKILL.md
  templates: the file name of each templates/*.template.md
  adrs:      the four digits of each ADR-NNNN / adr-NNNN
counted_when:                    # bare prose words are not counted
  - an inline code span equals the name
  - a dotted id agent.<name>, protocol.<name>, skill.<name>
  - a path agents/<file>.md, protocols/<name>.md, skills/<name>/ not preceded by [\w/.-]
  - templates: the file name anywhere in body text or code spans
  - adrs: every ADR-NNNN or adr-NNNN, case-insensitive
adr_range: '(?i)\badr-?\d{4}\s*(?:\.\.|–|—|to|through)\s*(?:adr-?)?\d{4}\b'
```

### Cost figures

```yaml
figure: '(?<![\w.])(\d{1,3}(?:[    ,]\d{3})+|\d+(?:\.\d+)?)(?:\s*(?:to|–|-)\s*(\d{1,3}(?:[    ,]\d{3})+|\d+(?:\.\d+)?))?\s*-?\s*(bytes?\b|B\b|KB\b|KiB\b|tokens?\b|%)'
                 # "8 000-byte" is a figure; a range gives both endpoints the range's unit
line_figure: '(?<![\w.])\d[\d    ,]*\s*-?\s*lines?\b'
measur_word: '(?i)(?<!\bnot )(?<!\bnot yet )(?<!\bnever )\bmeasur(?:ed|es|ing|ement|ements|e)?\b'
                 # "not measured", "not yet measured" and "unmeasured" are not claims of measurement
scope_markers: ["per session", "per task", "per prompt", "per spawn", "one-time",
                "Claude Code", "Prime Agent", "opencode", "Codex", "GitHub Copilot",
                "budget", "ceiling"]
derived_set:   # the values the gate computes; a figure not in it is not derived
  - every value check_eager_surface computes per host
  - EAGER_BUDGET, KERNEL_BUDGET
  - the kernel's byte count as measured by seed-lint's main()
  - the largest and median routable body, MACHINERY_BODY_CEILING, LIFECYCLE_BODY_CEILING
limit_constants: [EAGER_BUDGET, KERNEL_BUDGET, MACHINERY_BODY_CEILING, LIFECYCLE_BODY_CEILING]
evidence_record: an inline link whose target resolves to a file under docs/, fragment ignored
normalization:
  numbers: remove [    ,] between digits
  units:   "%" | " bytes" (B and byte read as bytes) | " tokens"
  compare: "<number><unit>" or "<number> <unit>" as a substring of the normalized record
```

Token figures are never derived: no seed-lint computation produces one. A
token figure in README must be measured, with evidence, or not printed.

### Evidence record

```yaml
evidence_record_content:
  carries: [the figure, the method, the date, the seed revision]
  never:   [a session id, a path outside the seed, a host name, a user name, a raw ledger]
  otherwise: the figure is written "not measured" and listed under "### Not yet measured"
held_by: G1 over each record README links, and the reviewer (§7 EVIDENCE_RECORD_CARRIES_ENVIRONMENT); no seed-lint check
```

### Required inputs

What each seed-lint contract reads. A missing input, or a parse under the
minimum, is a finding (§4). The last column is what passes because nothing
matched once the inputs are present.

| Contract | Required inputs | Passes on an empty match |
|---|---|---|
| FIRST_SCREEN_ORDER | `README.md`; at least one `##` heading; the three `*_CAP` rows of this spec's §6 constants table (the later-sections clause reads the `FIRST_SCREEN_MARKER` line, whose absence the marker clause already reports) | — |
| INSTALL_SECTION_NAMES_TARGET_PATHS | the install section; `install.sh` | — |
| WHERE_NEXT_LINKS_THE_REFERENCES | the where-next section | — |
| GLOSSARY_ENTRY_COMPLETE | the glossary region; at least one parsed entry | — |
| GLOSSARY_PATHS_EXIST | at least one parsed entry; `install.sh` | an entry with no install clause |
| NO_UNLINKED_PROJECT_TERM_IN_DEFINITION | at least one parsed entry; at least one project term | a Here field that names no other project term |
| TERM_LINKED_ON_FIRST_USE | `README.md`; at least one parsed entry whose Divergence is not `**same**` | an entry none of whose forms occurs in README |
| DEFINITION_HAS_ONE_HOME | at least one parsed entry with a Here sentence | a unit that names no form |
| REFERENCE_OPENS_WITH_ITS_DEFINITION | each of the three references; a paragraph after its `#` title | — |
| ENFORCEMENT_ROW_COMPLETE | the enforcement region; its table; at least one body row; the matrix class-table row whose first cell is `**mechanically enforced**` | — |
| MECHANISM_CLAIMS_TRACED | `README.md`; `INSTALL.md`; at least one `integrations/*/README.md`; at least one parsed glossary entry; at least one enforcement row | a unit with no mechanism verb or strong claim |
| LIMITS_SECTION_PRESENT | the section; both subsections | — |
| CATALOGS_OUT_OF_README | `README.md`; each §6 name set with at least one name on disk | a category README names nothing from; a file with no ADR range |
| COST_FIGURES_SCOPED | `README.md`; the cost section; at least one derived figure in it; the evidence record each measured figure links | README units outside the cost section that hold no figure; a README with no measured figure (the measured branch then has nothing to compare) |
| EAGER_FIGURES_CHECKED_WHEREVER_PUBLISHED | every front-door file; the values `check_eager_surface` computes | a file with no always-loaded figure |
| BODY_FIGURES_HAVE_A_REQUIRED_HOME | `BODY_FIGURE_HOME` with the four figures; `templates/knowledge-graph/graph-lint.py` | a file with no body line figure |
| FRONT_DOOR_ANCHORS_RESOLVE | every front-door file; the `glossary` and `enforcement` anchors in `DOCUMENTATION.md` | a file with no `term-`, `enf-`, `glossary` or `enforcement` link |
| FRONT_DOOR_HEADINGS_WELL_FORMED | the five files; at least one ATX heading in each | — |
| LINK_TEXT_STANDS_ALONE | `README.md`; the glossary region; the enforcement region | a region with no link |
| TABLES_HAVE_HEADER_ROWS | `README.md`; the glossary region; the enforcement region | a region with no table |
| PENDING_LEDGER_HOLDS_ONLY_FAILING_CONTRACTS | `FRONT_DOOR_PENDING`; this spec's frontmatter status and `### Contract:` headings; the `version` of `manifest.json` | — |

### Fixture

```yaml
fixture_root: tests/fixtures/front-door/
whole_file:              # files the harvest rewrites whole, or whose shipped text every contract would flag
  - README.md
  - INSTALL.md
  - integrations/<host>/README.md, one per host directory
  rule: each stub keeps what non-front-door checks read in it, such as the
        `delegation.harness-registration` pointer that REGISTRATION_REFERRERS
        requires (tests/seed-lint.py:242-272, :3037-3045)
patched_in_place:        # files other checks read; a whole-file swap would trip them
  - DOCUMENTATION.md: the §15 region replaced, §17 appended, the body-figure paragraph inserted, the two ADR ranges replaced
  - the three references: openers inserted, the four part headings demoted
  - documentation/host-capability-matrix.md: the class-table sentence added, and the `**mechanically enforced**` row's ADR-0003 cell given its `not a control` half (2026-09-24)
  rule: every patch is a fixed-string substitution that asserts exactly one match in the copy, so a drifted base fails the case instead of leaving the patch unapplied
computed_values: '"{{NAME}}" placeholders, filled at copy time from the copy''s tests/seed-lint.py loaded as a module (the exec pattern seed-lint itself uses at tests/seed-lint.py:1024-1029); never literals'
evidence: tests/fixtures/front-door/evidence.md, copied under docs/ in the copy; synthetic; holds only what "Evidence record" allows
ledger: FRONT_DOOR_PENDING rewritten to the empty set in the copy, asserting exactly one substitution
binding_values: a case that plants a ledger member runs with the copy's spec status below `implemented` and its manifest version below FRONT_DOOR_RELEASE, unless the case plants those too; otherwise the two emptiness clauses add findings the case did not plant (2026-09-24)
clean_case:
  always: no "front-door: " line and no ": RAISED " line
  until_increment_5: the only other findings allowed are check_published_body_figures' README lines, which that increment re-points
  from_increment_5: seed-lint exits 0 on the clean copy
content: synthetic only; placeholders such as /path/to/your/project and example.com; no credential-shaped string; no text copied from a donor environment
```

### Overlap metric (`DEFINITION_HAS_ONE_HOME`)

```yaml
normalize: link -> its text; code span -> its content; drop * _ ` markup; lowercase; tokens = runs of [a-z0-9]
stopwords: [a, an, the, and, or, of, to, in, on, for, by, with, as, at, from, is, are, was, were,
            be, been, it, its, this, that, these, those, which, who, whose, not, no, but, if,
            then, so, than, into, per, each, every, any, one]
content_tokens: tokens minus stopwords
definition_set: word DEFINITION_SHINGLE-shingles of one Here sentence's content tokens
candidate_set:  the same, over one unit
overlap: |definition_set ∩ candidate_set| / |definition_set|     # containment of the definition
short_definition: fewer than DEFINITION_MIN_TOKENS content tokens -> overlap is 1.0 when the whole content-token sequence occurs contiguously in the unit, else 0.0
scope: front-door files, glossary region excluded
fail_when: overlap >= DEFINITION_OVERLAP_CEILING
```

### Reference openers

| File | First sentence pattern | Required link |
|---|---|---|
| `documentation/agents-reference.md` | `^An agent is\b` | `../DOCUMENTATION.md#term-skill` |
| `documentation/skills-and-templates-reference.md` | `^A skill is\b` | `../DOCUMENTATION.md#term-skill` |
| `documentation/protocols-reference.md` | `^A protocol( node)? is\b` | `../DOCUMENTATION.md#term-protocol` |

The agent-and-skill contrast lives once, in the `skill` entry; both
references link it and neither restates it.

### Where-next list, generic link texts, tables, seed-source prefixes

```yaml
where_next_targets: [DOCUMENTATION.md, "DOCUMENTATION.md#glossary", "DOCUMENTATION.md#enforcement",
                     documentation/agents-reference.md, documentation/protocols-reference.md,
                     documentation/skills-and-templates-reference.md,
                     documentation/host-capability-matrix.md, docs/decisions/index.md, INSTALL.md]
generic_link_texts: [here, this, link, "click here", "this link", "read more", more]
table: consecutive lines beginning "|", whose second line matches '^\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?\s*$'; the first line is the header row
seed_source_prefixes: [core/, agents/, skills/, integrations/, protocols/, templates/, tools/, tests/]
```

### README-coupled checks after the move (C5)

| Check | Fact it holds | Home today | Home after the move | How strength is kept or raised | One RED case in the new home |
|---|---|---|---|---|---|
| `check_published_body_figures` | largest and median body, two ceilings; the `EAGER_EXEMPTIONS` phrases | `README.md`, returns silently when absent | `BODY_FIGURE_HOME`, required; phrases over every front-door file | absent home becomes a finding; phrase rules widen from one file to all | `BODY_FIGURES_HAVE_A_REQUIRED_HOME` |
| `check_published_eager_figures` | always-loaded byte figures | `published` = README and the matrix; absent figures pass | README and the matrix unchanged, plus every other front-door file | a figure moved anywhere in the front door stays checked | `EAGER_FIGURES_CHECKED_WHEREVER_PUBLISHED` |
| numeric-claims scan in `check()` | agent, specialist, coordinator and skill counts; documented version | front-door files plus the kernel and manifest | unchanged file set | unchanged; README catalogs leave, so README counts fall under `CATALOGS_OUT_OF_README` | `CATALOGS_OUT_OF_README` |
| `check_ci_workflow` | the seed's own gate runs in CI on two platforms | message text names README | message names the `enf-seed-gate` row | unchanged assertion; message re-pointed | none: no assertion moves |
| agnosticism scan in `check()` | no IP, CVE or home path | README a named file | unchanged | unchanged | none: no assertion moves |
| reference-table checks (`check_protocol_reference`, `check_reference_second_views`, `check_skills_reference`, `check_agents_reference`) | reference tables mirror frontmatter | the references | unchanged; openers add prose above the tables; four part headings go from `#` to `##` (`skills-and-templates-reference.md:29`, `:868`, `:1387`; `protocols-reference.md:113`) | unchanged, provided no table row, heading text or roles block moves. The one section regex that ends at `^## ` (`tests/seed-lint.py:974`) then stops A.15 at `## Part B` instead of the next summary table, which removes only Part B's intro text from A.15's section. Three of the four checks are in the coverage binder's `UNPROTECTED`, so their green after the edit is weak evidence; increment 4 records a mutation probe for each | `REFERENCE_OPENS_WITH_ITS_DEFINITION`; `FRONT_DOOR_HEADINGS_WELL_FORMED` |
| registration-referrer check in `check()` (`tests/seed-lint.py:3037-3045`) | README points at `delegation.harness-registration` | `README.md` among `REGISTRATION_REFERRERS` | unchanged: the new README keeps the pointer, as a code span, where it names the next session | unchanged; the pointer is a link to the home, not a restatement of host fact M8 | none: no assertion moves |
| prose-lint gate step | the front-door prose floor | one step over README and DOCUMENTATION together | one step per file | a rate is measured per file, so one file cannot hide in another's slack | `PROSE_FLOOR_HELD_PER_FILE` |

## 7. Failure modes

(Authored by `architect`. Security adds adversarial cases.)

Field values below are fragments and carry no closing period.

### Failure: VACUOUS_PASS_ON_ABSENT_TEXT
- **Contracts:** every §4 contract
- **Trigger:** a §6 required input is missing, or its parse yields fewer
  items than §6 "Required inputs" demands, as when the glossary is still in
  its old flat-bullet form and parses to no entries
- **Response:** a finding naming the missing input, at line `0`; exit 1
  unless the slug is pending. An input that is present with nothing matching
  passes (§4)
- **Side effects:** none
- **Recovery:** restore the text, or change this spec first if the text was
  meant to go

### Failure: FIXTURE_ONLY_COVERAGE
- **Contracts:** every seed-lint contract; `PENDING_LEDGER_HOLDS_ONLY_FAILING_CONTRACTS`
- **Trigger:** the planted cases pass on `tests/fixtures/front-door/` while the
  check never binds the shipped files, because its slug stays pending or its
  file list does not name them
- **Response:** each pending slug prints its real-tree finding count on every
  run; a pending slug with zero findings is a finding; the seed-lint
  real-tree run is the partner of the fixture cases, and the gate registry
  records `test-seed-lint.sh` under false-green class `scope`
- **Side effects:** none
- **Recovery:** the increment that makes the prose conform removes the slug in
  the same commit; the plan's done criterion is an empty ledger

### Failure: PENDING_LEDGER_MASKS_A_REGRESSION
- **Contracts:** `PENDING_LEDGER_HOLDS_ONLY_FAILING_CONTRACTS`
- **Trigger:** a slug is pending because part of its input still fails, and a
  new defect lands in the part that already conformed
- **Response:** reported in the PENDING line's count, not enforced
- **Side effects:** the count rises in the log, and nothing turns red
- **Recovery:** bounded to the harvest: every slug leaves the ledger by the
  plan's dependent-cleanup increment; the set cannot grow without an edit to
  `tests/ratchets.json`, and once SPEC-0004 is `implemented` any member is a
  finding (`PENDING_LEDGER_HOLDS_ONLY_FAILING_CONTRACTS`). Each increment's
  handback records every slug's PENDING count, and a count for a slug the
  increment does not target must not rise (grill §9). The one exception
  (2026-09-24, press P4) is a slug the increment's Gate declares by name
  because that increment adds one of the slug's §6 required inputs; any other
  rise stops the increment. From `FRONT_DOOR_RELEASE` on, any member is a
  finding whatever the spec's status
- **Fold note (2026-09-24):** the evidence-agreement clause now sits under
  `COST_FIGURES_SCOPED`, pending until the README increment, where it was
  predicted to be enforced from increment 1. README is not edited before that
  increment, so no text it held at `ee4cd95` goes unchecked for longer
- **Residual:** accepted. A per-slug count ceiling (a `map` ratchet) was
  weighed and rejected: a slug whose input lands in a later increment goes
  from one absence finding to its real count, so the ceiling would have to be
  raised mid-harvest, which is the loosening the ratchet exists to refuse
  (grill §7)

### Failure: ANCHOR_DRIFT
- **Contracts:** `FRONT_DOOR_ANCHORS_RESOLVE`, `TERM_LINKED_ON_FIRST_USE`,
  `MECHANISM_CLAIMS_TRACED`, `WHERE_NEXT_LINKS_THE_REFERENCES`
- **Trigger:** an entry or row anchor is renamed or removed, or two share an
  id, while a front-door link still names the old id
- **Response:** a finding naming the linking `file:line` and the id that does
  not resolve, or the duplicated id
- **Side effects:** none
- **Recovery:** restore the id or re-point every link; once released, ids are
  treated as a public interface (grill §6)

### Failure: ANCHOR_NOT_RENDERED_BY_HOST
- **Contracts:** `FRONT_DOOR_ANCHORS_RESOLVE`, `WHERE_NEXT_LINKS_THE_REFERENCES`,
  `TERM_LINKED_ON_FIRST_USE`, `MECHANISM_CLAIMS_TRACED`
- **Trigger:** the publishing host does not turn an explicit `<a id>` tag into
  a fragment target in rendered Markdown, so a link that resolves by the §6
  rule lands at the top of the page
- **Response:** none; every check passes, because each reads the file, not the
  rendered page
- **Side effects:** a reader following a term or row link lands on no entry
- **Recovery:** prevented, not detected. Before the glossary increment, the
  steward observes one rendered fragment on the publishing host, for example
  on the pushed branch (grill §9 increment 2). If it does not resolve, the
  anchor design is reopened before any entry lands. The choice between
  explicit and legacy anchors hangs on the same one observation (grill §6)

### Failure: FIGURE_MOVED_WITHOUT_ITS_CHECK
- **Contracts:** `EAGER_FIGURES_CHECKED_WHEREVER_PUBLISHED`,
  `BODY_FIGURES_HAVE_A_REQUIRED_HOME`, `COST_FIGURES_SCOPED`
- **Trigger:** a derived figure is moved out of README into another file
- **Response:** within the front-door files, the widened checks still hold
  it, and a body figure outside its home is a finding. Outside the front-door
  files (`CHANGELOG.md`, `docs/plans/`, `CLAUDE.md`) nothing holds it; that is
  the residual, and those files are historical or contributor records by
  design
- **Side effects:** none
- **Recovery:** keep reader-facing figures in the front-door files

### Failure: OVERCLAIM
- **Contracts:** `MECHANISM_CLAIMS_TRACED`
- **Trigger:** a unit in any front-door file matches the §6 strong-claim
  pattern, is not negated, and links a row whose weakest class is not hard:
  "a hard 8 000-byte budget" linked to `enf-kernel-budget`; "the harness
  prevents X" in `INSTALL.md` linked to a soft row; a strong claim linking a
  row whose Class cell holds both `**hard**` and `**judgment**`. Also a glossary
  Enforcement field that says `**hard**` while every row it links is weaker
- **Response:** a finding worded as an overclaim, naming each linked row and
  its weakest class
- **Side effects:** none
- **Recovery:** scope the sentence ("the seed's own gate refuses …") or link
  the hard row that holds it

### Failure: MEASURED_WORD_ON_A_DERIVED_FIGURE
- **Contracts:** `COST_FIGURES_SCOPED`
- **Trigger:** "measured" in a unit holding a derived figure, or in a unit of
  the cost section with no evidence link, such as a lead-in "measured rather
  than estimated"
- **Response:** a finding naming the unit
- **Side effects:** none
- **Recovery:** say "computed from the installed files" for derived figures;
  keep "measured" for figures with an evidence record

### Failure: EVIDENCE_DISAGREES
- **Contracts:** `COST_FIGURES_SCOPED` (its measured branch; before the
  2026-09-24 fold, the former `MEASURED_FIGURE_MATCHES_ITS_EVIDENCE`)
- **Trigger:** a measured figure (a range endpoint included) does not occur in
  its linked record, as with "10 to 20%" linked to a record holding 11%
- **Response:** a finding naming the figure and the record
- **Side effects:** none
- **Recovery:** print the recorded value
- **Residual:** the number may occur in the record in another context and pass

### Failure: CLAIM_WITHOUT_A_LISTED_VERB
- **Contracts:** `MECHANISM_CLAIMS_TRACED`
- **Trigger:** an enforcement claim phrased without any §6 mechanism verb
  ("every task is classified before acting")
- **Response:** none; it passes
- **Side effects:** none
- **Recovery:** the reviewer at verify; registered as a semantic false green

### Failure: PARAPHRASE_BELOW_CEILING
- **Contracts:** `DEFINITION_HAS_ONE_HOME`
- **Trigger:** a second definition reworded below `DEFINITION_OVERLAP_CEILING`,
  or one that never names the headword
- **Response:** none; it passes
- **Side effects:** none
- **Recovery:** the reviewer at verify; registered as a semantic false green

### Failure: UNLISTED_SURFACE_FORM
- **Contracts:** `TERM_LINKED_ON_FIRST_USE`, `NO_UNLINKED_PROJECT_TERM_IN_DEFINITION`,
  `DEFINITION_HAS_ONE_HOME`
- **Trigger:** a term used in an inflection or hyphenated compound its Forms
  field does not list ("multi-agent")
- **Response:** none; it passes
- **Side effects:** none
- **Recovery:** add the form; registered as a semantic false green

### Failure: INSTALL_LITERAL_IS_NOT_A_WRITE
- **Contracts:** `GLOSSARY_PATHS_EXIST`, `INSTALL_SECTION_NAMES_TARGET_PATHS`
- **Trigger:** a target path occurs in `install.sh` only in a comment or a
  message, not on a path that writes it
- **Response:** none; it passes
- **Side effects:** none
- **Recovery:** SPEC-0001's placement tests hold what is written; this check
  holds only that the name is the installer's

### Failure: CATALOG_IN_BARE_WORDS
- **Contracts:** `CATALOGS_OUT_OF_README`
- **Trigger:** a catalog written as plain words, not code spans, ids or paths
- **Response:** none; it passes
- **Side effects:** none
- **Recovery:** the reviewer at verify; bare words are not counted because
  roster names such as `security`, `product` and `legal` are ordinary words

### Failure: BLENDED_PROSE_STEP
- **Contracts:** `PROSE_FLOOR_HELD_PER_FILE`
- **Trigger:** a `tests/run.sh` line passes several `--file` arguments to
  `prose-lint.py`
- **Response:** `gate-registry.py --lint` exits 1 naming the line
- **Side effects:** none
- **Recovery:** one invocation per file, each registered

### Failure: UNREADABLE_INPUT
- **Contracts:** every seed-lint contract
- **Trigger:** a front-door file, `install.sh` or an evidence record cannot be
  read or decoded as UTF-8
- **Response:** a finding at line `0` naming the path, under the slug of
  each check that reads it
- **Side effects:** none
- **Recovery:** fix the file

### Failure: CHECK_RAISED
- **Contracts:** every seed-lint contract
- **Trigger:** a front-door check raises
- **Response:** `front-door: <SLUG>: RAISED <ExceptionType>: <message>`; exit
  1 even when the slug is pending, because a check that cannot run has
  observed nothing. The `RAISED` token keeps the line apart from a finding, so
  a planted case cannot pass on a crash: every `case_fd_*` except the one that
  plants the raise fails when its output holds `: RAISED `. A raised slug
  counts as neither findings nor zero findings for the stale-entry rule
- **Side effects:** none
- **Recovery:** fix the check

### Failure: LEDGER_REGROWS_AFTER_IMPLEMENTED
- **Contracts:** `PENDING_LEDGER_HOLDS_ONLY_FAILING_CONTRACTS`
- **Trigger:** after SPEC-0004 goes `implemented`, a regression is "fixed" by
  adding its slug back to `FRONT_DOOR_PENDING` and to `tests/ratchets.json`
  in one diff
- **Response:** a finding (`ledger must be empty once SPEC-0004 is
  implemented`); exit 1
- **Side effects:** none
- **Recovery:** fix the prose; to reopen the ledger, move the spec out of
  `implemented` by a spec revision

### Failure: RELEASE_WITH_PENDING_LEDGER
- **Contracts:** `PENDING_LEDGER_HOLDS_ONLY_FAILING_CONTRACTS`
- **Trigger:** the branch stalls with slugs pending and the spec short of
  `implemented`, and `manifest.json` is bumped to `FRONT_DOOR_RELEASE` or
  later for a release
- **Response:** a finding (`ledger must be empty from <FRONT_DOOR_RELEASE>`);
  exit 1
- **Side effects:** none
- **Recovery:** finish or revert the pending increments before the bump
- **Residual:** a release numbered below `FRONT_DOOR_RELEASE` from a partly
  merged tree is not refused. The branch is merged once, after its last
  increment, and merging stays the steward's (grill §9)

### Failure: LINE_CEILING_RAISED_PAST_CAP
- **Contracts:** `FIRST_SCREEN_ORDER`
- **Trigger:** `FIRST_HEADING_MAX_LINE`, `FIRST_SCREEN_MAX_LINES` or
  `FIRST_COMMAND_LINE` is raised above its §6 cap by editing
  `tests/seed-lint.py` and `tests/ratchets.json` in one diff
- **Response:** a finding at `tests/seed-lint.py` naming the constant, its
  value and its cap; exit 1
- **Side effects:** none
- **Recovery:** trim README above the marker, or change this spec's cap first

### Failure: PROSE_STEP_NAME_COLLISION
- **Contracts:** `PROSE_FLOOR_HELD_PER_FILE`
- **Trigger:** two prose-lint lines in `tests/run.sh` resolve to the same step
  name, as a basename rule would give `README.md` and
  `integrations/<host>/README.md`
- **Response:** `gate-registry.py --lint` exits 1 naming both lines
- **Side effects:** none
- **Recovery:** name steps by repository-relative path (§4)

### Failure: STRONG_CLAIM_IN_MANUAL_PROSE
- **Contracts:** `MECHANISM_CLAIMS_TRACED`
- **Trigger:** a strong claim in `DOCUMENTATION.md` outside the glossary
  fields, or in `documentation/*.md`, that links no enforcement row
- **Response:** none; it passes. Only a strong claim that links a row is held
  there
- **Side effects:** none
- **Recovery:** the reviewer at verify. Tracing every mechanism verb in the
  manual and the references was weighed and not chosen: they are the detail
  homes the rows link to, and they describe method steps the model is asked
  to follow; the number of units it would touch was not counted

### Failure: CLASS_CELL_UNTRUE
- **Contracts:** `ENFORCEMENT_ROW_COMPLETE`, `MECHANISM_CLAIMS_TRACED`
- **Trigger:** a row's Class cell names a class its artifact does not hold,
  such as `**hard**` for a mechanism that binds only on some hosts
- **Response:** none mechanical; the checks hold that the class is from the
  closed set, that four rows name their residuals, and that strong claims
  match the class as written
- **Side effects:** none
- **Recovery:** `security` signs the Class column row by row against ADR-0003
  (judgment, recorded at verify)
- **Also (2026-09-24, press P9):** the host capability matrix classes the same
  mechanisms in prose. Its class table is held mechanically
  (`ENFORCEMENT_ROW_COMPLETE`'s matrix clause). Its footnote ¹
  (`documentation/host-capability-matrix.md:96-97`) and its delegation note
  (`:199-200`) call the leaf's spawn bar hard with no scope, while
  `enf-leaf-cannot-spawn` must carry a weakest class that is not hard. Grill
  §9 increment 3 reconciles both, changing class wording only and no host
  fact. The reviewer reads them at verify of that increment. They are not
  checked

### Failure: HOST_FACT_RESTATED
- **Contracts:** none; §2 scope
- **Trigger:** README, a glossary Here or Enforcement field, an enforcement
  row, the ADR-0003 amendment, or a unit of `INSTALL.md` or an
  `integrations/*/README.md` that the dependent-cleanup increment edits
  (added 2026-09-24), states a host-release fact (hooks in
  subagents, agent registration, the spawn tool's name, spawn depth) instead
  of saying it is host-dependent and linking the matrix
- **Response:** none; it passes
- **Side effects:** none
- **Recovery:** the reviewer at verify of increments 2, 3, 5 and 6, over
  every hit of `subagent|worker|spawn|depth|restart|Task\b` in those files; a
  phrase check is follow-up work for the host-facts change

### Failure: EVIDENCE_RECORD_CARRIES_ENVIRONMENT
- **Contracts:** `COST_FIGURES_SCOPED` (its measured branch)
- **Trigger:** a committed evidence record carries more than §6 "Evidence
  record" allows: a session id, a scratch path, a host or user name
- **Response:** none from seed-lint
- **Side effects:** an identifying token in a committed file
- **Recovery:** G1 over every record README links, before commit; a figure
  with no clean record is written `not measured`

### Failure: PROJECT_NODE_FIGURE_COLLISION
- **Contracts:** `BODY_FIGURES_HAVE_A_REQUIRED_HOME`
- **Trigger:** a seed body figure outside `BODY_FIGURE_HOME` whose value
  happens to be 150 or 170
- **Response:** none; it passes as the project-node ceiling
- **Side effects:** none
- **Recovery:** the reviewer at verify; the exemption set is bound to the
  literals in `graph-lint.py` and cannot outlive them

## 8. Examples

```markdown
# Happy: a conforming glossary entry (fixture form)
### plant
<a id="term-plant"></a>

- **Forms:** plant, plants
- **Here:** a repository after the [seed](#term-seed) was installed into it and [grown](#term-growth).
- **Field:** no standard meaning.
- **Implemented at:** `install.sh`, `protocols/grow.md`. An install produces `.cypress/seed.json` (`write_seed_stamp`).
- **Enforcement:** **not a control**
- **Divergence:** **no standard meaning**
- **Why:** not recorded
```

```markdown
# Happy: a conforming cost row and its README link
| Figure | Scope and source |
|---|---|
| <always-loaded bytes> bytes | per session on Claude Code; computed from the installed files by the seed's gate |
| 11% more tokens | per task, on one small, well-specified task; measured once ([record](docs/plans/<record>.md)) |
```

```text
# Edge: the first use sits in a code span, the second is linked
README: "Run `plant` checks …" then "… inside your [plant](DOCUMENTATION.md#term-plant) …"
Result: pass. The code span is masked, so the linked occurrence is the first one.

# Edge: a derived figure beside a limit
README: "The kernel is <kernel bytes> bytes, computed, under the seed gate's 8 000-byte budget (per session)."
Result: pass. <kernel bytes> is derived and the unit says "computed"; 8 000 equals KERNEL_BUDGET and the unit says "budget".
```

```text
# Failure: an overclaim (§7 OVERCLAIM)
README: "The kernel sits under a hard 8 000-byte [budget](DOCUMENTATION.md#enf-kernel-budget)."
Output: front-door: MECHANISM_CLAIMS_TRACED: README.md:<n>: overclaim: says 'hard' and links enf-kernel-budget (weakest class: soft)

# Failure: a strong claim outside README linking a mixed row (§7 OVERCLAIM)
INSTALL.md: "The harness blocks the tool for a leaf ([allowlist](DOCUMENTATION.md#enf-tool-allowlist))."
Row Class cell: "**hard** on hosts that honour per-agent tools; **judgment** under role emulation"
Output: front-door: MECHANISM_CLAIMS_TRACED: INSTALL.md:<n>: overclaim: says 'blocks' and links enf-tool-allowlist (weakest class: judgment)

# Pass: a negated strong word in the limits section
README: "- No tool blocks code written before its spec ([spec before code](DOCUMENTATION.md#enf-spec-before-code))."
Result: pass. "No" sits within three words before "blocks"; the unit is traced (it links a row) and is not a strong claim.

# Failure: a check that crashed (§7 CHECK_RAISED)
Output: front-door: TABLES_HAVE_HEADER_ROWS: RAISED RuntimeError: <message>
Result: exit 1 while the slug is pending, and no planted case may pass on this line.

# Failure: a derived figure called measured (§7 MEASURED_WORD_ON_A_DERIVED_FIGURE)
README: "The running cost, measured rather than estimated:"
Output: front-door: COST_FIGURES_SCOPED: README.md:<n>: 'measured' with no evidence record in this unit

# Failure: a linked range whose value is stale (§7 EVIDENCE_DISAGREES)
README: "10 to 20% more tokens per task, measured once ([record](docs/plans/<record>.md))"
Output: front-door: COST_FIGURES_SCOPED: README.md:<n>: '10%' does not occur in docs/plans/<record>.md

# Failure: a line ceiling raised past its cap (§7 LINE_CEILING_RAISED_PAST_CAP)
Copy: FIRST_SCREEN_MAX_LINES = 101 in tests/seed-lint.py and in tests/ratchets.json
Output: front-door: FIRST_SCREEN_ORDER: tests/seed-lint.py:<n>: FIRST_SCREEN_MAX_LINES 101 exceeds FIRST_SCREEN_CAP 100

# Failure: a stalled branch stamped with the release (§7 RELEASE_WITH_PENDING_LEDGER)
Copy: manifest.json version 7.29.0; spec status active; one genuinely failing slug pending
Output: front-door: PENDING_LEDGER_HOLDS_ONLY_FAILING_CONTRACTS: tests/seed-lint.py:<n>: ledger must be empty from 7.29.0

# Pending (RED increment, before the glossary is rewritten)
Output: front-door: PENDING GLOSSARY_ENTRY_COMPLETE: 40 finding(s); first: DOCUMENTATION.md:<n>: no entry for required headword 'agent'
```

## 9. Acceptance criteria

(Authored by `product`. Every criterion ends with one `Contracts:` line naming
the §4 contracts it accepts; `spec-lint.py` checks each name on that line
against the declared contract headings, so the line holds contract names and
nothing else in capitals. AC-1 to AC-17, AC-19 to AC-21 and AC-23 to AC-29 are
mechanical: the named contracts decide them, each with a planted RED case.
AC-18 is the reader test. It is detective: it is never a gate and never wired
into `tests/run.sh`. AC-22 is an accepted residual recorded in §11 and names
no contract; so do G8, G11, G12 and G13 (see "Accepted residuals" below).
The coverage table at the end of this section lists, for every §4 contract,
the criteria that accept it. Re-mapped to the final §4 on 2026-09-24; gaps
G1, G2, G4, G5, G6 and G9 are closed by the contracts they now name.
Re-aligned the same day to the architect's revision of §4, §6 and §7: AC-9,
AC-10, AC-16, AC-26, AC-28 and AC-29 changed. Re-mapped again the same day
after the architect folded three contracts into others (steward decision
D1): the later-sections order into FIRST_SCREEN_ORDER (AC-1), the
evidence match into the measured branch of COST_FIGURES_SCOPED (AC-13), and
the hook-is-not-a-control check into ENFORCEMENT_ROW_COMPLETE (AC-27). AC-2
now names the §6 caps, and AC-28 the release clause. The contract count is
22.)

### Reading order and first screen

- [ ] **AC-1.** README carries the nine sections of §3.1 as `##` headings
      spelled byte for byte as in the §6 README heading table. The first five
      (what it is; who it is for and not for; what installing does to your
      repository; what it costs; try it) come first, in that order, with no
      other `##` heading before or between them, and the first sits on or
      before line `FIRST_HEADING_MAX_LINE`. Exactly one first-screen marker
      follows the fifth, before any other `##` heading, on or before line
      `FIRST_SCREEN_MAX_LINES`. The last four (how it works; why it is built
      this way; what it does not do; where to go next) follow the marker in
      that order, each exactly once; other `##` headings may sit between them.
      A planted README that swaps "what it costs" and "try it", puts any `##`
      heading before "what it is", or drops "where to go next" fails. The
      later four are one contract with the first five: the former separate
      later-sections check was folded into it on 2026-09-24.
      Contracts: maps to FIRST_SCREEN_ORDER.
- [ ] **AC-2.** The first fenced block in README whose info string is `sh`
      opens under "try it", and its first line containing `install.sh` sits on
      or before line `FIRST_COMMAND_LINE`. That ratchet is recorded at the
      measured line and never rises past its cap: seed-lint reads
      `FIRST_HEADING_CAP` (6), `FIRST_SCREEN_CAP` (100) and
      `FIRST_COMMAND_CAP` (80) from the §6 constants table, and a recorded
      `FIRST_HEADING_MAX_LINE`, `FIRST_SCREEN_MAX_LINES` or
      `FIRST_COMMAND_LINE` above its cap is a finding naming
      `tests/seed-lint.py`, the constant, its value and its cap, even when
      `tests/ratchets.json` was raised in the same diff. Raising a cap means
      changing this spec first. A planted README whose first `sh` block opens
      under "how it works" fails, and so does a copy whose
      `FIRST_COMMAND_LINE` is 81 in both `tests/seed-lint.py` and
      `tests/ratchets.json`.
      Contracts: maps to FIRST_SCREEN_ORDER.
- [ ] **AC-3.** README has no `##` heading equal to `## What you get`, the
      heading that presented the seed's source tree as what the reader
      receives and caused before-error 4. A planted README with that heading
      anywhere fails. The path-level half of error 4 is AC-15.
      Contracts: maps to FIRST_SCREEN_ORDER.

### Terms and glossary

- [ ] **AC-4.** For every glossary entry whose Divergence is not exactly
      `**same**`, the first occurrence in README body text of any of its
      listed forms lies inside the text of an inline link to
      `DOCUMENTATION.md#term-<the entry's id>`. Fenced blocks, headings and
      HTML comments are not body text; code spans and link targets are masked.
      An entry none of whose forms occurs in README passes. A planted README
      that uses "plant" unlinked before its first linked use fails; one whose
      first "plant" is in a code span and whose second is linked passes (§8).
      Contracts: maps to TERM_LINKED_ON_FIRST_USE.
- [ ] **AC-5.** Every entry in the glossary region has its `term-` anchor on
      the line after its `###` headword and exactly seven labelled fields,
      once each, non-empty, in the order Forms, Here, Field, Implemented at,
      Enforcement, Divergence, Why:
      - Forms includes the headword itself, case-insensitively.
      - Enforcement carries at least one bolded class, and every bolded token
        in it is one of hard, soft, detective, judgment, not a control.
      - Divergence carries at least one bolded value, and every bolded token
        in it is one of same, narrower, broader, different, no standard
        meaning.
      - Field says "no standard meaning", or carries at least one status of
        verified, secondhand or not recorded; every "verified" has an https
        URL and a retrieval date in the same field.
      - Why cites a decision record, a spec, a plan path, a commit hash, a
        `path:line` or a kernel section, or is the literal `not recorded`.

      Every headword in the §6 required-headword list has an entry. A planted
      entry missing a field, with fields out of order, with a value outside
      its closed set, or with "verified" and no URL, fails; so does removing
      a required headword.
      Contracts: maps to GLOSSARY_ENTRY_COMPLETE.
- [ ] **AC-6.** Every path-like token in an entry's Implemented at field,
      outside an "An install produces" clause, resolves under the seed root
      (placeholders and one level of `{a,b}` expanded), and a `:N` or `:N-M`
      suffix lies within the file's line count. Inside that clause, each
      path's literal prefix occurs in `install.sh`, and each backticked bare
      name is a function `install.sh` defines. A field with no path begins
      `n/a`. A planted nonexistent path, an out-of-range line, an install path
      `install.sh` does not contain, or a function it does not define fails.
      Contracts: maps to GLOSSARY_PATHS_EXIST.
- [ ] **AC-7.** In every entry's Here field, the first occurrence of any form
      of another project term (an entry whose Divergence contains "no standard
      meaning") lies inside a link to that entry's `term-` anchor. The entry's
      own forms are exempt. A planted Here field that says "plant" unlinked
      fails.
      Contracts: maps to NO_UNLINKED_PROJECT_TERM_IN_DEFINITION.
- [ ] **AC-8.** No unit of a front-door file outside the glossary region that
      contains a form of an entry reaches `DEFINITION_OVERLAP_CEILING` of
      overlap with any sentence of that entry's Here field, by the §6 metric.
      This covers the agent-and-skill contrast, which lives only in the
      `skill` entry, and the old §1.1 and §6.7 restatements. The finding names
      the entry, the unit's `file:line` and the overlap. A planted near-copy of
      the `skill` entry's Here sentence in `agents-reference.md` fails. Method
      nodes that ship to installed projects are out of scope, and the
      glossary links them. A reworded copy below the ceiling passes; that is
      the §7 PARAPHRASE_BELOW_CEILING residual, judged at verify.
      Contracts: maps to DEFINITION_HAS_ONE_HOME.

### Enforcement claims

- [ ] **AC-9.** Every unit of a §6 traced surface that matches the §6
      mechanism-verb pattern (code spans and link targets masked) holds an
      inline link to `DOCUMENTATION.md#enf-<id>` (`#enf-<id>` inside
      `DOCUMENTATION.md`) for a row that exists. The traced surfaces are
      `README.md`, `INSTALL.md`, every `integrations/*/README.md` (at least
      one must exist) and the glossary's Here and Enforcement fields. A
      planted unlinked "the gate enforces X" fails in README, in `INSTALL.md`,
      in an integration README and in a glossary Here field, and so does one
      linking an `enf-` id no row carries. This rules out before-error 5
      (graph invariants read as a control in the reader's repository). The
      rest of `DOCUMENTATION.md` and `documentation/*.md` are not traced; a
      mechanism verb there passes unlinked. Two residuals are judged at
      verify: a claim phrased with no listed verb (§7
      CLAIM_WITHOUT_A_LISTED_VERB) and a strong claim in the manual prose or
      references that links no row (§7 STRONG_CLAIM_IN_MANUAL_PROSE).
      Contracts: maps to MECHANISM_CLAIMS_TRACED.
- [ ] **AC-10.** In every front-door file outside the enforcement region, a
      unit that says `hard`, `cannot`, `can't`, a `guarantee-`, `ensur-`,
      `prevent-`, `block-` or `refus-` word, `stop` or `stops`, is not
      negated (not, no, nothing, none, never, without or an `n't` word among
      the three words before it) and links at least one `enf-` row, links
      only rows whose weakest class is `hard`. The weakest class is the
      lowest bolded class in the row's Class cell, by the order hard, soft,
      detective, judgment, not a control. Otherwise it fails as an
      overclaim naming each linked row with its weakest class. "Never" and
      "only" are not strong claims (§6 `not_strong`). A glossary Enforcement
      field that carries any bolded class other than "not a control"
      links at least one `enf-` row, every class it names occurs in the Class
      cell of a row it links, and a field saying `**hard**` links a row whose
      weakest class is hard. Planted cases that fail: README "a hard 8
      000-byte budget" linked only to the kernel-budget row (soft, the seed's
      own gate), which rules out before-error 3; `INSTALL.md` "the harness
      blocks the tool for a leaf" linked to a row classed both hard and
      judgment; a README "refuses" linked to a soft row; a glossary
      Enforcement field saying `**hard**` whose linked rows are all weaker.
      Planted cases that pass: "No tool blocks code written before its spec"
      linked to a judgment row (negated), and "nothing here is hard".
      Contracts: maps to MECHANISM_CLAIMS_TRACED.
- [ ] **AC-11.** README's "what it does not do" section holds exactly two
      subsections, `### Requested, not enforced` then `### Not yet measured`.
      The first holds at least `LIMITS_MIN_REQUESTED` list items, each with an
      inline link to an `enf-` row whose class carries a bolded value other
      than hard; together they link the tier-classification,
      spec-before-code and test-before-code rows. The second holds at least
      `LIMITS_MIN_UNMEASURED` list items, each saying "not recorded", "not
      measured" or "measured once". Limits items link `enf-` rows only, never
      a matrix anchor directly; the row links the matrix (the stricter
      reading recorded in §11). A planted limits item that links only a hard
      row, or no row, or an unmeasured item without one of those phrases,
      fails; so does dropping the test-before-code link.
      Contracts: maps to LIMITS_SECTION_PRESENT.

### Catalogs out of the README

- [ ] **AC-12.** README body text names at most `README_CATALOG_CEILING`
      distinct names in each of five categories, counted separately with the
      names taken from disk: agents, protocols, skills, templates and decision
      record numbers. A name counts when it is a code span, a dotted id or a
      path, by the §6 counting rule. No front-door file holds a range of
      decision records (`adr-0001..0010`, `ADR-0001 to ADR-0010` and the
      like). A planted README listing every agent in code spans, or a planted
      range in any front-door file, fails. A catalog in bare words passes;
      that is the §7 CATALOG_IN_BARE_WORDS residual, judged at verify.
      Contracts: maps to CATALOGS_OUT_OF_README.

### Cost figures

- [ ] **AC-13.** Every README figure in bytes, tokens or percent (both
      endpoints of a range) sits in a unit that holds a §6 scope marker (such
      as "per session", "per task", a harness name, "budget" or "ceiling")
      and is one of two kinds:
      - derived: its value is one the gate computes and the unit says
        "computed", or it equals a limit constant and the unit says "budget",
        "ceiling" or "limit"; or
      - measured: the unit says "measured once" or "measured <date>" and
        links an evidence record under `docs/` that resolves, and the figure,
        number and unit together, occurs in that record.

      Token figures are never derived. A planted "7 742 bytes" kernel figure
      that nothing derives fails, which rules out before-error 2. A planted
      "10 to 20%" with no evidence link fails, and so does one linked to a
      record that holds 11%; together they rule out before-error 6. The
      evidence match is the measured branch of the one cost contract (the
      former separate evidence-match check was folded into it on
      2026-09-24).
      Contracts: maps to COST_FIGURES_SCOPED.
- [ ] **AC-14.** A unit holding a derived figure never says "measured", and in
      "what it costs" a unit that says "measured" links an evidence record.
      "Not measured", "not yet measured" and "unmeasured" are not claims of
      measurement. A derived figure is described as computed. A planted
      "measured rather than estimated" lead-in above the derived always-loaded
      row fails, which rules out before-error 1.
      Contracts: maps to COST_FIGURES_SCOPED.

### Install section

- [ ] **AC-15.** The "what installing does to your repository" section names,
      each as a whole backticked token, the root kernel files `CLAUDE.md` and
      `AGENTS.md`, the harness directory `.claude/`, `docs/graph/` and
      `.cypress/seed.json`. Every path-like token in the section other than
      `install.sh` passes the §6 install-literal rule. No token in the section
      begins with a seed-source prefix (`core/`, `agents/`, `skills/`,
      `integrations/`, `protocols/`, `templates/`, `tools/`, `tests/`). This
      rules out before-error 4. A planted section that lists `core/`, or omits
      `.cypress/seed.json`, fails. A name that occurs in `install.sh` only in a
      comment passes; that is the §7 INSTALL_LITERAL_IS_NOT_A_WRITE residual,
      and SPEC-0001's placement tests hold what is written.
      Contracts: maps to INSTALL_SECTION_NAMES_TARGET_PATHS.
- [ ] **AC-16.** One unit of the install section names `.cypress/seed.json`
      (the one path replaced without a copy) and links
      `DOCUMENTATION.md#enf-backup-before-replace`; any mechanism verb in the
      section links its row. The install guide and each integration README
      are traced surfaces too (AC-9), so the same install facts told there
      carry their row links as well. A planted "every file it replaces is
      left beside itself" in the install section that neither names the stamp
      nor links the row fails, and so does an unlinked "the installer never
      merges a file" in the install section or in `INSTALL.md`.
      Contracts: maps to INSTALL_SECTION_NAMES_TARGET_PATHS, MECHANISM_CLAIMS_TRACED.
- [ ] **AC-17.** Every figure that moves out of README stays held at the same
      strength or stricter, per the §6 table "README-coupled checks after the
      move". Always-loaded byte figures in any front-door file equal a
      computed value or the eager budget, and the README and matrix pair is
      never pending. `DOCUMENTATION.md`, the required home for body figures,
      exists and states the largest and median routable body and both body
      ceilings. The exemption phrase rules run over every front-door file. No
      other front-door file holds a body line figure. Each re-pointed check
      has one planted RED case in its new home: an eager figure that nothing
      computes in `documentation/agents-reference.md`, a body figure copied
      into `INSTALL.md`, and a `DOCUMENTATION.md` missing the median each
      fail. A figure moved outside the front-door files is not held; that is
      the §7 FIGURE_MOVED_WITHOUT_ITS_CHECK residual.
      Contracts: maps to EAGER_FIGURES_CHECKED_WHEREVER_PUBLISHED, BODY_FIGURES_HAVE_A_REQUIRED_HOME, COST_FIGURES_SCOPED.

### Reader test (detective, never a gate)

- [ ] **AC-18.** After the rewrite lands, three fresh model sessions each answer
      the seven reader questions from the rewritten README alone, with no
      linked file opened, using the same model mix as the "before" run.
      Before the run, the answer key is re-checked against the implementation
      at the post-rewrite revision. A reviewer who did not write the README
      grades them against the key with its scoring rules unchanged. **Pass:**
      the median session, by count of fully correct answers, is correct on all
      seven. No README-caused error is recorded in the grades. The result
      (grid, per-cell reasons, inherited-error list) is recorded as verify
      evidence in the plan-of-record. This is **detective** evidence. It is not
      a §10 test, is not wired into `tests/run.sh` or any gate, and a failure
      reopens the README increment rather than turning a gate red. It also
      holds the accepted residual G8 (§11): the reader questions cover what
      the always-loaded figure leaves out and that no money figure exists.
      The contracts below are the ones whose purpose the reader test checks.
      Baseline: median 1 of 7 fully correct; six README-caused errors.
      Contracts: maps to FIRST_SCREEN_ORDER, TERM_LINKED_ON_FIRST_USE, MECHANISM_CLAIMS_TRACED, LIMITS_SECTION_PRESENT, COST_FIGURES_SCOPED, DEFINITION_HAS_ONE_HOME.

### Accessibility floor

- [ ] **AC-19.** README, DOCUMENTATION and the three references each have
      exactly one level-1 heading, it is the first heading, and no heading's
      level exceeds the previous one's by more than one. Headings inside
      fenced blocks do not count. A planted `####` directly under a `##`
      fails, and so does a second `#` heading. This closes G1 across all five
      files, not only README.
      Contracts: maps to FRONT_DOOR_HEADINGS_WELL_FORMED.
- [ ] **AC-20.** No link text in README, the glossary or the enforcement
      section, with markup stripped, is empty, is a generic text from §6
      (here, this, link, click here, this link, read more, more; any case),
      or begins with `http://`, `https://` or `www.`. A planted `[here](...)`
      or `[https://example.org](...)` fails.
      Contracts: maps to LINK_TEXT_STANDS_ALONE.
- [ ] **AC-21.** Every table in README, the glossary and the enforcement
      section has a header row whose every cell is non-empty after markup and
      whitespace are stripped. A planted `| | |` header, or one whose cell
      holds only `**`, fails.
      Contracts: maps to TABLES_HAVE_HEADER_ROWS.
- [ ] **AC-22.** No enforcement class, deprecation or warning in README is
      conveyed only by emphasis. Each is stated in words. This is not
      mechanical and names no contract. It is an accepted residual (G3),
      recorded in §11, judged by the reviewer during verify against the
      README, glossary and enforcement section, and it has no §10 row.

### Navigation and references

- [ ] **AC-23.** README's "where to go next" section holds one inline link to
      each of the nine §6 where-next targets: the manual, the glossary, the
      enforcement section, the three references, the host capability matrix,
      the decision index and the install guide. Each target resolves under
      the seed root, and each fragment resolves to its explicit anchor. This
      is the recovery path for a returning user (§3.4) and for a stale
      bookmark (G11). A planted section missing the decision index link, or
      linking a reference that does not exist, fails.
      Contracts: maps to WHERE_NEXT_LINKS_THE_REFERENCES, FRONT_DOOR_ANCHORS_RESOLVE.
- [ ] **AC-24.** The first paragraph after the title of each reference opens
      with its own definition: "An agent is …" in the agents reference, "A
      skill is …" in the skills-and-templates reference, "A protocol is …" or
      "A protocol node is …" in the protocols reference. That paragraph links
      the glossary: the agents and skills references link the `skill` entry,
      which holds the agent-and-skill contrast, and the protocols reference
      links the `protocol` entry. A planted agents reference that opens with
      its table, or whose opener links no glossary entry, fails.
      Contracts: maps to REFERENCE_OPENS_WITH_ITS_DEFINITION.
- [ ] **AC-25.** Every link in a front-door file to a `term-` or `enf-`
      fragment, or to `glossary` or `enforcement`, lands on exactly one
      explicit anchor in the target file; every explicit anchor id in
      `DOCUMENTATION.md` is unique; every relative link in README resolves to
      an existing file. A planted link to `#term-plnat`, two entries sharing
      `term-plant`, or a README link to a missing file each fail.
      Contracts: maps to FRONT_DOOR_ANCHORS_RESOLVE.

### Enforcement section

- [ ] **AC-26.** Every body row of the enforcement table has five non-empty
      cells (mechanism, artifact, class, what it can miss, detail). The first
      cell begins with an `enf-` anchor. The class cell carries at least one
      bolded class, and every bolded token in it is in the §6 class set. The
      artifact cell holds at least one path that resolves under the seed
      root. Every id in the §6 required-row list is present. A planted row
      with an empty "what it can miss" cell, a class of "strong", or an
      artifact path that does not exist fails; so does removing a required
      row such as `enf-spec-before-code`. Four rows also name their residual
      and meet their class rule, per the §6 row-specific table (patterns
      case-insensitive, in the "what it can miss" cell):
      - `enf-tool-allowlist`: names `Bash`, "role emulation" and an omitted
        `tools:` line; its weakest class is not hard.
      - `enf-leaf-cannot-spawn`: names the spawn tool ("spawn tool" or
        "spawn-tool"), "role emulation" and `tools:`; its weakest class is
        not hard.
      - `enf-pre-bash-guard`: says it fails open, names indirection, evasion
        or evade, and names the host or hosts; its weakest class is not hard,
        and a `**hard**` in its class cell is scoped to "a matched command on
        a host that fires the hook".
      - `enf-backup-before-replace`: names `.cypress/seed.json`; no class
        rule.

      No unit anywhere in the front door that links `enf-pre-bash-guard`
      calls the guard a security, sandbox or protection measure (the §6
      `guard_misnomer` pattern: any `secur-`, `sandbox-` or `protect-`
      word). Planted cases that fail: an allow-list row whose miss cell drops
      "role emulation"; a leaf-spawn row whose only class is `**hard**`; a
      pre-bash-guard row that does not say it fails open; a backup row that
      does not name the stamp; a README "the security guard" sentence linked
      to `enf-pre-bash-guard`. Whether a row's class is true is not
      mechanical: `security` signs the class column row by row at verify
      (§7 CLASS_CELL_UNTRUE).
      Contracts: maps to ENFORCEMENT_ROW_COMPLETE, MECHANISM_CLAIMS_TRACED.
- [ ] **AC-27.** The route-hook and status-hook rows are classed "not a
      control" (their Class cells contain `**not a control**`). In
      the class table of `documentation/host-capability-matrix.md`, the row
      whose first cell is `**mechanically enforced**` has a Meaning cell
      that says `injects` and an ADR-0003 cell that says `not a control`, so
      the matrix cannot map a hook that only injects text to hard while the
      enforcement rows class it as no control. A planted route-hook row
      classed hard fails; so does a matrix row whose Meaning cell drops
      "injects", and one whose ADR-0003 cell drops "not a control". This is
      part of the enforcement-row contract (the former separate hook check
      was folded into it on 2026-09-24).
      Contracts: maps to ENFORCEMENT_ROW_COMPLETE.

### Gate honesty (the maintainer, §3.6)

- [ ] **AC-28.** While a contract's slug is in the pending ledger, each run
      prints one `PENDING` line for it with its finding count and its first
      finding, and the exit status is unchanged. A pending slug with zero
      findings is itself a finding ("stale pending entry: remove it"). A
      member that is not a seed-lint contract of this spec, or that is the
      ledger's own contract or the per-file prose contract, is a finding. A
      check that raises prints `front-door: <SLUG>: RAISED <ExceptionType>:
      <message>` and makes seed-lint exit 1 even while its slug is pending; a
      raised slug counts as neither findings nor zero findings, so it is not
      reported as a stale entry, and no planted case passes on output holding
      `: RAISED `. When this spec's frontmatter `status:` is `implemented`,
      any member of the ledger is a finding ("ledger must be empty once
      SPEC-0004 is implemented"), even when `tests/ratchets.json` was edited
      in the same diff to admit it. When the `version` in `manifest.json`,
      compared as integers, is at least `FRONT_DOOR_RELEASE` (7.29.0), any
      member of the ledger is a finding ("ledger must be empty from 7.29.0"),
      whatever this spec's status, so a release cannot ship with checks still
      excused. Planted cases that fail the run: a ledger holding a passing
      slug, an unknown slug or the ledger's own slug; a check forced to raise
      while its slug is pending (exit 1, a `RAISED` line with the exception
      type, no stale-entry line); a copy whose spec status is `implemented`
      with one slug in the ledger and in `tests/ratchets.json`; and a copy
      whose spec is still `active`, whose manifest version is 7.29.0 and whose
      ledger holds one slug. The same draft copy at manifest version 7.28.0
      passes the release clause.
      Contracts: maps to PENDING_LEDGER_HOLDS_ONLY_FAILING_CONTRACTS.
- [ ] **AC-29.** Each prose-lint invocation in `tests/run.sh` names exactly
      one `--file` and is registered as its own step named
      `prose-lint.py --file <path>`, with `<path>` relative to the repository
      root; README and DOCUMENTATION each have one. A planted `tests/run.sh`
      line passing two `--file` arguments makes `tools/gate-registry.py
      --lint` exit 1 naming the line. Two planted prose-lint lines that
      resolve to the same step name (both naming `README.md`) make `--lint`
      exit 1 naming both lines, where today the second merges silently into
      the first. Lines for `README.md` and `integrations/<host>/README.md`
      register as two distinct steps and pass. The refusal covers prose-lint
      step names only. The check lives in `tests/test_gate_registry.py`.
      Contracts: maps to PROSE_FLOOR_HELD_PER_FILE.

### Accepted residuals (recorded in §11)

Each is a product decision to accept a gap no stdlib check can close. None is
a gate, and none has a §10 row.

- **G3, meaning carried only by emphasis:** AC-22; §11 row 1. The reviewer
  judges it at verify.
- **G8, what the cost section leaves out and "no money figure":** held by the
  detective AC-18; §11 row 2. A phrase check would pin wording, not meaning.
- **G11, old README anchors stop resolving:** §11 row 3. The release's
  changelog names the removed anchors; AC-23 holds the recovery path.
- **G12, README prints no host tier (§3.1 item 2):** §11 row "README names
  hosts with their support tier", resolved by product as the first of its
  two options: README names the hosts, says in words that support differs
  and some are deprecated, and links the matrix's support-tier section and
  ADR-0009 without printing a tier. No contract holds it; the reviewer
  judges it at verify of the README increment. If it is ever to be gated,
  the route is `check_host_tiers` gaining README as a published copy, which
  is an architect change.
- **G13, "Try it" says it tracks the default branch (§3.1 item 5):** §11 row
  "'Try it' and the default branch"; tag pin rejected. The reviewer judges
  the sentence at verify of the README increment.

### Coverage: every §4 contract and the criteria that accept it

| Contract | Accepted by |
|---|---|
| FIRST_SCREEN_ORDER | AC-1, AC-2, AC-3, AC-18 |
| INSTALL_SECTION_NAMES_TARGET_PATHS | AC-15, AC-16 |
| WHERE_NEXT_LINKS_THE_REFERENCES | AC-23 |
| GLOSSARY_ENTRY_COMPLETE | AC-5 |
| GLOSSARY_PATHS_EXIST | AC-6 |
| NO_UNLINKED_PROJECT_TERM_IN_DEFINITION | AC-7 |
| TERM_LINKED_ON_FIRST_USE | AC-4, AC-18 |
| DEFINITION_HAS_ONE_HOME | AC-8, AC-18 |
| REFERENCE_OPENS_WITH_ITS_DEFINITION | AC-24 |
| ENFORCEMENT_ROW_COMPLETE | AC-26, AC-27 |
| MECHANISM_CLAIMS_TRACED | AC-9, AC-10, AC-16, AC-18, AC-26 |
| LIMITS_SECTION_PRESENT | AC-11, AC-18 |
| CATALOGS_OUT_OF_README | AC-12 |
| COST_FIGURES_SCOPED | AC-13, AC-14, AC-17, AC-18 |
| EAGER_FIGURES_CHECKED_WHEREVER_PUBLISHED | AC-17 |
| BODY_FIGURES_HAVE_A_REQUIRED_HOME | AC-17 |
| FRONT_DOOR_ANCHORS_RESOLVE | AC-23, AC-25 |
| FRONT_DOOR_HEADINGS_WELL_FORMED | AC-19 |
| LINK_TEXT_STANDS_ALONE | AC-20 |
| TABLES_HAVE_HEADER_ROWS | AC-21 |
| PENDING_LEDGER_HOLDS_ONLY_FAILING_CONTRACTS | AC-28 |
| PROSE_FLOOR_HELD_PER_FILE | AC-29 |

Twenty-two contracts, each accepted by at least one criterion. Every name on
a `Contracts:` line above is a `### Contract:` of §4.

---

## 10. Test mapping

(Owned by `tester`. Written 2026-09-24 against `ee4cd95`, before any case
exists, and revised the same day after the architect's revision of §4, §6,
§7 and §11 and product's §9 alignment; ~~every row is `red` until increment 1
lands its case and observes it failing for the missing behaviour~~ (struck
2026-09-24; the status line at the end of this preamble replaces it).)

**Re-keyed 2026-09-24 after the G9 fold (steward D1, architect revision).**
Three rows changed key, not case: X302 `README_LATER_SECTIONS_ORDER` →
`FIRST_SCREEN_ORDER`, X313 `HOOK_FIRING_IS_NOT_HOLDING` →
`ENFORCEMENT_ROW_COMPLETE`, X317 `MEASURED_FIGURE_MATCHES_ITS_EVIDENCE` →
`COST_FIGURES_SCOPED`. Their cases keep their names, plants and labels; only
the slug in the expected line and the `check_fd_*` they exercise moved to the
absorbing contract. case_fd_hook_firing (b) now plants in the matrix row's
ADR-0003 cell. Two cases were added for the press: X334
case_fd_first_screen_caps (P7) and X335 case_fd_pending_release (P4). ~~Every
row is still `red`.~~ (struck 2026-09-24 by the next paragraph)

**Status as increment 1 lands (2026-09-24).** Eight rows are `green` because
increment 1 enforces them from its own commit: EAGER_FIGURES_CHECKED_WHEREVER_PUBLISHED
(X318, passing on the real tree and never pending), the three
PENDING_LEDGER_HOLDS_ONLY_FAILING_CONTRACTS rows (X324, X333, X335),
FIXTURE_ONLY_COVERAGE (X324), CHECK_RAISED (X328), LEDGER_REGROWS_AFTER_IMPLEMENTED
(X333) and RELEASE_WITH_PENDING_LEDGER (X335). Every other row is `red`: its
case exists and fires on the fixture, but its slug is still held in
`FRONT_DOOR_PENDING` on the real tree. UNREADABLE_INPUT stays `red` while
CHECK_RAISED is `green` because an unreadable input is reported through
`fd_fail` under the slug of each check that reads the file, so it is held as a
PENDING line while that slug is in the ledger, whereas a raise is reported by
`fd_guard` outside the ledger and fails the run whether or not its slug is
pending.

**Status as increment 2 lands (2026-09-24).** Four more rows are `green`:
GLOSSARY_ENTRY_COMPLETE (X305), GLOSSARY_PATHS_EXIST (X306),
NO_UNLINKED_PROJECT_TERM_IN_DEFINITION (X307) and DEFINITION_HAS_ONE_HOME
(X309). Increment 2's glossary clears them on the real tree, so their slugs
have left `FRONT_DOOR_PENDING`. The rule above is unchanged: every row whose
slug is still in the ledger stays `red`.

**Binding.** Each row citing `tests/test-seed-lint.sh` opens its Test case
cell with one fixed-width label, `X300` to `X335` (`X325` is unassigned).
SPEC-0003 holds `X101` to `X203`. `check_spec_test_mapping` binds only the
label that opens the cell, so a case added to a contract after its first row
gets its own row and label, never a second label inside a cell. Every case
carries its row's label and slug in the comment or OK line that sits beside
the plant. Until a case was written its row cited the file with a
`(to write)` suffix, and the Python rows cited the test name with it.
Increment 1 made both bare (2026-09-24), when the cases were written. Only this table is keyed by contract slug; where a slug has several
rows they carry the same status. The case table below it is keyed by case
name, so it cannot overwrite a row's status in spec-lint's `mapping_rows`.
Each `check_fd_*` is named as grill §8 "Interfaces" lists it. The binding
that counts is the `# exercises:` marker, which
`tests/check-coverage-binder.py` holds equal to `COVERED`. Every planted
case a §9 criterion names has a sub-plant below, in that criterion's words.

**Levels and false-green classes** (`tools/gate-registry.py`):

- **fixture**: a hermetic copy with the conforming fixture laid in by §6
  "Fixture": whole-file stubs for `README.md`, `INSTALL.md` and each
  `integrations/<host>/README.md`; fixed-string patches to `DOCUMENTATION.md`,
  the three references and the matrix, each asserting exactly one match, so a
  drifted base fails the case instead of leaving a patch unapplied; `{{NAME}}`
  placeholders filled from the copy's own `tests/seed-lint.py` loaded as a
  module; `FRONT_DOOR_PENDING` rewritten to the empty set, asserting exactly
  one substitution. Step `test-seed-lint.sh`, registered `real-tree`, class
  `scope`: it proves that the check fires and says nothing about the shipped
  tree.
- **real-tree (copy)**: the same copy without the fixture, ledger intact.
  Same step and class.
- **real-tree**: the `seed-lint.py` step over `$ROOT`, class `semantic`. It
  is the partner of every fixture row (§7 `FIXTURE_ONLY_COVERAGE`).
- **unit**: `tests/test_gate_registry.py` against a synthetic `run.sh`.
  Registered `real-tree`, class `scope`.

**Case discipline.**

- Every `expect_fail` pattern is anchored: `front-door: <SLUG>: <file>:`,
  then the plant's line where it has one (`0` for an absence or whole-file
  finding), then a message fragment unique to the plant. The case table
  gives the file and the fragment per sub-plant; `<line>` there means the
  line computed from the copy, never a literal.
- Every `case_fd_*` except case_fd_check_raised fails when its output holds
  `: RAISED `, so a crash cannot satisfy a planted case (§7 `CHECK_RAISED`).
- A sub-plant marked "passes" asserts that no line matching its anchored
  pattern appears; it pins a boundary §4 or §6 draws, not a finding.
- Until increment 5 the exit code of a fixture copy is not evidence: the
  README stub trips `check_published_body_figures`, so rc is 1 anyway. The
  anchored pattern is the evidence.
- A bare `front-door` pattern also matches this spec's file name in
  unrelated findings, which was observed at `ee4cd95`.
- A bare slug would also match a `CHECK_RAISED` line; the anchored form
  cannot, because `RAISED` stands where the file would.
- Planted line positions are computed from the copy's constants
  (`FIRST_HEADING_MAX_LINE`, `FIRST_SCREEN_MAX_LINES`, `FIRST_COMMAND_LINE`),
  never hard-coded, because increment 5 tightens them. The caps
  (`FIRST_HEADING_CAP`, `FIRST_SCREEN_CAP`, `FIRST_COMMAND_CAP`) are read from
  the copy's SPEC-0004 §6 constants table, never written as literals.
- **Binding values (§6 "Fixture" `binding_values`).** Every copy in which a
  case plants a ledger member (case_fd_eager_published (c),
  case_fd_pending_stale, case_fd_pending_unknown_slug,
  case_fd_pending_holds_exit, case_fd_pending_implemented,
  case_fd_pending_release, case_fd_check_raised) first sets the copy's
  SPEC-0004 frontmatter `status:` to `active` and the copy's `manifest.json`
  `version` to `7.28.0`, each by a substitution asserting exactly one match,
  unless the case plants that value itself (case_fd_pending_implemented plants
  the status, case_fd_pending_release the version). Both values sit below
  their binding values (`implemented`, `FRONT_DOOR_RELEASE`), so neither
  emptiness clause adds a finding the case did not plant, and the cases stay
  valid after the release bump lands on the real tree.

| Contract / Failure | Test case | Test file | Level | Status |
|---|---|---|---|---|
| (fixture guard, no slug) | X300 case_fd_fixture_clean: the conforming fixture produces no `front-door: ` line and no `: RAISED ` line; from increment 5 seed-lint also exits 0 on it (case table) | tests/test-seed-lint.sh | fixture (scope); guard, cannot go red before the checks exist | pending |
| FIRST_SCREEN_ORDER | X301 case_fd_first_screen_order, case_fd_first_screen_budget, case_fd_first_command_line, case_fd_what_you_get_heading · `check_fd_first_screen_order` | tests/test-seed-lint.sh | fixture (scope) | red |
| FIRST_SCREEN_ORDER | X302 case_fd_later_sections_order · `check_fd_first_screen_order` | tests/test-seed-lint.sh | fixture (scope); the later-sections clause (AC-1), re-keyed from the folded `README_LATER_SECTIONS_ORDER` | red |
| FIRST_SCREEN_ORDER | X334 case_fd_first_screen_caps · `check_fd_first_screen_order` | tests/test-seed-lint.sh | fixture (scope); the line-cap clause (§6 "Caps", press P7); `tools/ratchet-lint.py` alone accepts the raise when `tests/ratchets.json` changes in the same diff, so this case is the refusal | red |
| INSTALL_SECTION_NAMES_TARGET_PATHS | X303 case_fd_install_target_paths, case_fd_install_seed_path · `check_fd_install_section_names_target_paths` | tests/test-seed-lint.sh | fixture (scope) | red |
| WHERE_NEXT_LINKS_THE_REFERENCES | X304 case_fd_where_next · `check_fd_where_next_links_the_references` | tests/test-seed-lint.sh | fixture (scope) | red |
| GLOSSARY_ENTRY_COMPLETE | X305 case_fd_glossary_absent, case_fd_glossary_fields, case_fd_glossary_closed_values, case_fd_glossary_required_term · `check_fd_glossary_entry_complete` | tests/test-seed-lint.sh | fixture (scope) | green |
| GLOSSARY_PATHS_EXIST | X306 case_fd_glossary_paths, case_fd_glossary_install_literal · `check_fd_glossary_paths_exist` | tests/test-seed-lint.sh | fixture (scope) | green |
| NO_UNLINKED_PROJECT_TERM_IN_DEFINITION | X307 case_fd_definition_links · `check_fd_no_unlinked_project_term_in_definition` | tests/test-seed-lint.sh | fixture (scope) | green |
| TERM_LINKED_ON_FIRST_USE | X308 case_fd_term_linked · `check_fd_term_linked_on_first_use` | tests/test-seed-lint.sh | fixture (scope) | red |
| DEFINITION_HAS_ONE_HOME | X309 case_fd_one_home · `check_fd_definition_has_one_home` | tests/test-seed-lint.sh | fixture (scope) | green |
| REFERENCE_OPENS_WITH_ITS_DEFINITION | X310 case_fd_reference_opener · `check_fd_reference_opens_with_its_definition` | tests/test-seed-lint.sh | fixture (scope); C5 RED for the four reference-table checks, with X321 (§6 C5 table). Three of them are UNPROTECTED in the coverage binder, so their green after increment 4's heading demotion also rests on that increment's recorded mutation probe | red |
| ENFORCEMENT_ROW_COMPLETE | X311 case_fd_enforcement_row, case_fd_enforcement_required_row · `check_fd_enforcement_row_complete` | tests/test-seed-lint.sh | fixture (scope) | red |
| ENFORCEMENT_ROW_COMPLETE | X329 case_fd_enforcement_row_residuals · `check_fd_enforcement_row_complete` | tests/test-seed-lint.sh | fixture (scope); the §6 row-specific table (AC-26) | red |
| MECHANISM_CLAIMS_TRACED | X312 case_fd_mechanism_traced, case_fd_mechanism_overclaim · `check_fd_mechanism_claims_traced` | tests/test-seed-lint.sh | fixture (scope) | red |
| MECHANISM_CLAIMS_TRACED | X330 case_fd_mechanism_surfaces · `check_fd_mechanism_claims_traced` | tests/test-seed-lint.sh | fixture (scope); traced surfaces beyond README, overclaim scope, glossary Enforcement fields, `guard_misnomer` (AC-9, AC-10, AC-26) | red |
| ENFORCEMENT_ROW_COMPLETE | X313 case_fd_hook_firing · `check_fd_enforcement_row_complete` | tests/test-seed-lint.sh | fixture (scope); the `enf-route-hook` and `enf-status-hook` lines of the §6 row-specific table and the matrix clause (AC-27), re-keyed from the folded `HOOK_FIRING_IS_NOT_HOLDING` | red |
| LIMITS_SECTION_PRESENT | X314 case_fd_limits_hard_row, case_fd_limits_required_rows, case_fd_limits_unmeasured · `check_fd_limits_section_present` | tests/test-seed-lint.sh | fixture (scope) | red |
| CATALOGS_OUT_OF_README | X315 case_fd_catalogs, case_fd_adr_range · `check_fd_catalogs_out_of_readme` | tests/test-seed-lint.sh | fixture (scope); C5 RED for the numeric-claims scan; case_05 and case_06 unchanged | red |
| COST_FIGURES_SCOPED | X316 case_fd_cost_scope, case_fd_cost_provenance, case_fd_cost_measured_derived · `check_fd_cost_figures_scoped` | tests/test-seed-lint.sh | fixture (scope) | red |
| COST_FIGURES_SCOPED | X331 case_fd_cost_no_derived · `check_fd_cost_figures_scoped` | tests/test-seed-lint.sh | fixture (scope); the one-derived-figure required input | red |
| COST_FIGURES_SCOPED | X317 case_fd_measured_evidence · `check_fd_cost_figures_scoped` | tests/test-seed-lint.sh | fixture (scope); the measured branch (AC-13), re-keyed from the folded `MEASURED_FIGURE_MATCHES_ITS_EVIDENCE` | red |
| EAGER_FIGURES_CHECKED_WHEREVER_PUBLISHED | X318 case_fd_eager_published · `check_fd_eager_figures_checked_wherever_published` (grill §8; `check_published_eager_figures` is re-pointed in increment 5, not duplicated) | tests/test-seed-lint.sh | fixture (scope); C5 RED for `check_published_eager_figures`. Predicted to pass on the real tree at `ee4cd95`, so enforced from increment 1 and never pending | green |
| BODY_FIGURES_HAVE_A_REQUIRED_HOME | X319 case_fd_body_home, case_fd_body_figure_elsewhere · `check_fd_body_figures_have_a_required_home` (grill §8; `check_published_body_figures` is re-pointed in increment 5, not duplicated) | tests/test-seed-lint.sh | fixture (scope); C5 RED for `check_published_body_figures`; case_21 unchanged | red |
| BODY_FIGURES_HAVE_A_REQUIRED_HOME | X332 case_fd_body_project_node · `check_fd_body_figures_have_a_required_home` | tests/test-seed-lint.sh | fixture (scope); the `PROJECT_NODE_LINE_FIGURES` exemption and its binding to `graph-lint.py` | red |
| FRONT_DOOR_ANCHORS_RESOLVE | X320 case_fd_anchor_resolves, case_fd_anchor_duplicate · `check_fd_front_door_anchors_resolve` | tests/test-seed-lint.sh | fixture (scope) | red |
| FRONT_DOOR_HEADINGS_WELL_FORMED | X321 case_fd_headings · `check_fd_front_door_headings_well_formed` | tests/test-seed-lint.sh | fixture (scope) | red |
| LINK_TEXT_STANDS_ALONE | X322 case_fd_link_text · `check_fd_link_text_stands_alone` | tests/test-seed-lint.sh | fixture (scope) | red |
| TABLES_HAVE_HEADER_ROWS | X323 case_fd_table_header · `check_fd_tables_have_header_rows` | tests/test-seed-lint.sh | fixture (scope) | red |
| PENDING_LEDGER_HOLDS_ONLY_FAILING_CONTRACTS | X324 case_fd_pending_stale, case_fd_pending_unknown_slug, case_fd_pending_holds_exit · `check_fd_pending_ledger_holds_only_failing_contracts` | tests/test-seed-lint.sh | fixture (scope) and real-tree (copy) (scope); ledger growth is also held by `tools/ratchet-lint.py` (`set`) | green |
| PENDING_LEDGER_HOLDS_ONLY_FAILING_CONTRACTS | X333 case_fd_pending_implemented · `check_fd_pending_ledger_holds_only_failing_contracts` | tests/test-seed-lint.sh | fixture (scope); the empty-when-`implemented` clause (AC-28) | green |
| PENDING_LEDGER_HOLDS_ONLY_FAILING_CONTRACTS | X335 case_fd_pending_release · `check_fd_pending_ledger_holds_only_failing_contracts` | tests/test-seed-lint.sh | fixture (scope); the empty-from-`FRONT_DOOR_RELEASE` clause (AC-28, press P4) | green |
| PROSE_FLOOR_HELD_PER_FILE | test_prose_lint_one_step_per_file | tests/test_gate_registry.py | unit (scope), `expectedFailure` until increment 7; C5 RED for the prose-lint step split | red |
| PROSE_FLOOR_HELD_PER_FILE | test_prose_lint_multi_file_refused | tests/test_gate_registry.py | unit (scope), `expectedFailure` until increment 7 | red |
| PROSE_FLOOR_HELD_PER_FILE | test_prose_lint_same_name_refused | tests/test_gate_registry.py | unit (scope), `expectedFailure` until increment 7 (AC-29) | red |
| VACUOUS_PASS_ON_ABSENT_TEXT | X326 case_fd_absent_inputs; also X305 case_fd_glossary_absent, X319 case_fd_body_home, X331 case_fd_cost_no_derived | tests/test-seed-lint.sh | fixture (scope) | red |
| FIXTURE_ONLY_COVERAGE | X324 case_fd_pending_holds_exit | tests/test-seed-lint.sh | real-tree (copy) (scope), partnered by the real-tree `seed-lint.py` step (semantic) | green |
| PENDING_LEDGER_MASKS_A_REGRESSION | none: counted in the PENDING line, never enforced | none | residual, bounded by the empty-ledger done criterion, by X333 (`implemented`) and by X335 (`FRONT_DOOR_RELEASE`); each increment's handback records every slug's PENDING count (grill §9) | residual |
| ANCHOR_NOT_RENDERED_BY_HOST | none: every check reads the file, not the rendered page; no honest test exists and none is faked | none | residual, prevented not detected; judge: the steward observes one rendered `<a id>` fragment on the publishing host before increment 2 (grill §9 increment 2), recorded in that increment's handback; a fragment that does not resolve reopens the anchor design | residual |
| ANCHOR_DRIFT | X320 case_fd_anchor_resolves, case_fd_anchor_duplicate; X308 case_fd_term_linked (b); X304 case_fd_where_next (b) | tests/test-seed-lint.sh | fixture (scope) | red |
| FIGURE_MOVED_WITHOUT_ITS_CHECK | X318 case_fd_eager_published; X319 case_fd_body_figure_elsewhere | tests/test-seed-lint.sh | fixture (scope); outside the front-door files it is a residual | red |
| OVERCLAIM | X312 case_fd_mechanism_overclaim; also X330 case_fd_mechanism_surfaces (a) to (d) | tests/test-seed-lint.sh | fixture (scope) | red |
| MEASURED_WORD_ON_A_DERIVED_FIGURE | X316 case_fd_cost_measured_derived | tests/test-seed-lint.sh | fixture (scope) | red |
| EVIDENCE_DISAGREES | X317 case_fd_measured_evidence | tests/test-seed-lint.sh | fixture (scope); the other-context match is a residual | red |
| CLAIM_WITHOUT_A_LISTED_VERB | none: passes by design | none | residual, semantic; reviewer at verify | residual |
| PARAPHRASE_BELOW_CEILING | none: passes by design | none | residual, semantic; reviewer at verify | residual |
| UNLISTED_SURFACE_FORM | none: passes by design | none | residual, semantic; reviewer at verify | residual |
| INSTALL_LITERAL_IS_NOT_A_WRITE | none: passes by design; SPEC-0001 placement tests hold writes | none | residual | residual |
| CATALOG_IN_BARE_WORDS | none: passes by design | none | residual, semantic; reviewer at verify | residual |
| BLENDED_PROSE_STEP | test_prose_lint_multi_file_refused | tests/test_gate_registry.py | unit (scope) | red |
| UNREADABLE_INPUT | X327 case_fd_unreadable_input | tests/test-seed-lint.sh | fixture (scope) | red |
| CHECK_RAISED | X328 case_fd_check_raised | tests/test-seed-lint.sh | fixture (scope) | green |
| LEDGER_REGROWS_AFTER_IMPLEMENTED | X333 case_fd_pending_implemented | tests/test-seed-lint.sh | fixture (scope); `tools/ratchet-lint.py` alone accepts the regrowth when `tests/ratchets.json` changes in the same diff, so this case is the refusal | green |
| RELEASE_WITH_PENDING_LEDGER | X335 case_fd_pending_release | tests/test-seed-lint.sh | fixture (scope); a release numbered below `FRONT_DOOR_RELEASE` from a partly merged tree is the §7 residual, held by the steward's single merge | green |
| LINE_CEILING_RAISED_PAST_CAP | X334 case_fd_first_screen_caps | tests/test-seed-lint.sh | fixture (scope) | red |
| PROSE_STEP_NAME_COLLISION | test_prose_lint_same_name_refused | tests/test_gate_registry.py | unit (scope), `expectedFailure` until increment 7 | red |
| STRONG_CLAIM_IN_MANUAL_PROSE | none: passes by design. The held half, a manual strong claim that links a row, is X330 case_fd_mechanism_surfaces (e); the boundary is pinned by its "passes" sub-plant (h) | none | residual, semantic; judge: `reviewer` at verify | residual |
| CLASS_CELL_UNTRUE | none mechanical. The closed class set, the row-specific patterns and class rules, the matrix class-table clause, and strong claims against the class as written are X311, X329, X313, X312 and X330 | none | residual, judgment; judge: `security` signs the Class column row by row against ADR-0003 at verify of increment 3, recorded in that increment's handback; the `reviewer` reads the matrix's footnote ¹ and delegation note at verify of the same increment (§7, P9) | residual |
| HOST_FACT_RESTATED | none: no contract (§2 scope) | none | residual, judgment; judge: `reviewer` at verify of increments 2, 3, 5 and 6, over every hit of the §7 pattern in those files | residual |
| EVIDENCE_RECORD_CARRIES_ENVIRONMENT | none from seed-lint; the fixture's `evidence.md` is synthetic and holds only what §6 "Evidence record" allows | none | residual; judge: the steward's local G1 `--file` over every record README links, before commit (grill §9 increment 5), then the `reviewer` | residual |
| PROJECT_NODE_FIGURE_COLLISION | none: passes by design. X332 case_fd_body_project_node pins that the exemption holds only while `graph-lint.py` carries the literals | none | residual, semantic; judge: `reviewer` at verify | residual |
| DONOR_TOKEN_IN_ADR_BODY | none: a plan residual (grill §6 D2, §9 increment 8), not a §7 mode; an ADR body is never edited, so no case can plant a fix | none | residual, judgment; judge: the steward's local whole-tree G1 (the one excepted path, recorded by path and token class in the increment 8 handback) and G2 | residual |

**What each case plants** (in the copy; one defect per sub-plant, with a
restore between sub-plants, as `caseHOST_TIERS_AGREE` does):

| Case | Plants | Expected line (anchored; fragment after `+`) |
|---|---|---|
| case_fd_fixture_clean | nothing | always: no line matching `front-door: ` and none matching `: RAISED `. Until increment 5 every other finding line is one of `check_published_body_figures`' README lines (§6 "Fixture"); from increment 5 seed-lint exits 0, and increment 5's commit strengthens the case to assert it |
| case_fd_first_screen_order | (a) headings 2 and 3 swapped; (b) an extra `##` between headings 1 and 2; (c) the first `##` pushed below `FIRST_HEADING_MAX_LINE` | `front-door: FIRST_SCREEN_ORDER: README.md:<line>:` + (a) `order`; (b) the extra heading's text; (c) `FIRST_HEADING_MAX_LINE` |
| case_fd_first_screen_budget | (a) marker moved below `FIRST_SCREEN_MAX_LINES`; (b) marker duplicated; (c) marker removed | `front-door: FIRST_SCREEN_ORDER: README.md:` + (a) `<marker line>:` and `FIRST_SCREEN_MAX_LINES`; (b) `<second marker line>:` and `first-screen-end`; (c) `0:` and `first-screen-end` |
| case_fd_first_command_line | (a) first `install.sh` line pushed below `FIRST_COMMAND_LINE`; (b) first `sh` fence moved under `## How it works` (AC-2) | `front-door: FIRST_SCREEN_ORDER: README.md:<line>:` + (a) `FIRST_COMMAND_LINE`; (b) `Try it` |
| case_fd_what_you_get_heading | `## What you get` appended (AC-3) | `front-door: FIRST_SCREEN_ORDER: README.md:<line>:` + `What you get` |
| case_fd_first_screen_caps | in the copy's `tests/seed-lint.py` and `tests/ratchets.json` in one edit: (a) `FIRST_SCREEN_MAX_LINES` set to `FIRST_SCREEN_CAP` + 1; (b) `FIRST_HEADING_MAX_LINE` set to `FIRST_HEADING_CAP` + 1; (c) `FIRST_COMMAND_LINE` set to `FIRST_COMMAND_CAP` + 1; (d) passes: (a) again with the copy's SPEC-0004 §6 `FIRST_SCREEN_CAP` row raised to the same value (the spec changed first); (e) the `FIRST_SCREEN_CAP` row removed from the copy's §6 constants table (§6 "Required inputs") | `front-door: FIRST_SCREEN_ORDER: tests/seed-lint.py:` + (a) `<line of the constant>:` and `FIRST_SCREEN_MAX_LINES` and `FIRST_SCREEN_CAP`; (b) `<line>:` and `FIRST_HEADING_MAX_LINE` and `FIRST_HEADING_CAP`; (c) `<line>:` and `FIRST_COMMAND_LINE` and `FIRST_COMMAND_CAP`; (d) no FIRST_SCREEN_ORDER line naming `tests/seed-lint.py`; (e) `front-door: FIRST_SCREEN_ORDER: docs/specs/SPEC-0004-front-door.md:0:` + `FIRST_SCREEN_CAP`. For (a) to (c) `python3 tools/ratchet-lint.py` on the same copy exits 0, recorded so the refusal is shown to be seed-lint's |
| case_fd_later_sections_order | (a) headings 7 and 8 swapped; (b) `## Where to go next` duplicated; (c) `## How it works` removed | `front-door: FIRST_SCREEN_ORDER: README.md:` + (a) `<line>:` and `order`; (b) `<second line>:` and `Where to go next`; (c) `0:` and `How it works` |
| case_fd_install_target_paths | (a) `` `.cypress/seed.json` `` token removed (AC-15); (b) `` `.cursor/rules/` `` added (not in `install.sh`); (c) the backup unit replaced by "every file it replaces is left beside itself", naming no stamp and linking no row (AC-16) | `front-door: INSTALL_SECTION_NAMES_TARGET_PATHS: README.md:` + (a) `.cypress/seed.json`; (b) `.cursor/rules/`; (c) `enf-backup-before-replace` |
| case_fd_install_seed_path | `` `core/method/` `` added to the install section (AC-15) | `front-door: INSTALL_SECTION_NAMES_TARGET_PATHS: README.md:<line>:` + `core/` |
| case_fd_where_next | (a) the `docs/decisions/index.md` link removed (AC-23); (b) `DOCUMENTATION.md#glossery` in place of `#glossary`; (c) a link to `documentation/no-such-reference.md` (AC-23) | `front-door: WHERE_NEXT_LINKS_THE_REFERENCES: README.md:` + (a) `docs/decisions/index.md`; (b) `glossery`; (c) `no-such-reference.md` |
| case_fd_glossary_absent | glossary region replaced by the `ee4cd95` flat-bullet form | `front-door: GLOSSARY_ENTRY_COMPLETE: DOCUMENTATION.md:0:` + `no entries` |
| case_fd_glossary_fields | (a) `plant` loses Why; (b) Here and Field swapped; (c) a blank line between headword and anchor; (d) Forms without the headword | `front-door: GLOSSARY_ENTRY_COMPLETE: DOCUMENTATION.md:<entry line>:` + (a) `Why`; (b) `order`; (c) `term-plant`; (d) `Forms` |
| case_fd_glossary_closed_values | (a) Enforcement `**mandatory**`; (b) Divergence `**similar**`; (c) `status: verified` with no URL; (d) Why `because` | `front-door: GLOSSARY_ENTRY_COMPLETE: DOCUMENTATION.md:<line>:` + (a) `mandatory`; (b) `similar`; (c) `status: verified`; (d) `Why` |
| case_fd_glossary_required_term | the `tier` entry deleted | `front-door: GLOSSARY_ENTRY_COMPLETE: DOCUMENTATION.md:0:` + `tier` |
| case_fd_glossary_paths | (a) `` `tools/no-such-tool.py` ``; (b) `` `install.sh:999999` ``; (c) a field with no path and no leading `n/a` | `front-door: GLOSSARY_PATHS_EXIST: DOCUMENTATION.md:<line>:` + (a) `tools/no-such-tool.py`; (b) `install.sh:999999`; (c) `n/a` |
| case_fd_glossary_install_literal | (a) An install produces `` `.cypress/no-such.json` ``; (b) `` (`write_nothing`) `` | `front-door: GLOSSARY_PATHS_EXIST: DOCUMENTATION.md:<line>:` + (a) `.cypress/no-such.json`; (b) `write_nothing` |
| case_fd_definition_links | (a) `seed` unlinked in the `plant` Here field; (b) linked to `#term-growth` | `front-door: NO_UNLINKED_PROJECT_TERM_IN_DEFINITION: DOCUMENTATION.md:<line>:` + (a) `seed`; (b) `term-growth` |
| case_fd_term_linked | (a) unlinked `plant` before its first linked use; (b) the first use links `#term-graft`; (c) passes: first `plant` in a code span, the second linked (§8) | `front-door: TERM_LINKED_ON_FIRST_USE: README.md:<line>:` + (a) `plant`; (b) `term-graft`; (c) no such line |
| case_fd_one_home | (a) a near-copy of the `skill` Here sentence appended to `documentation/agents-reference.md`; (b) the same for a short (under five-token) definition | `front-door: DEFINITION_HAS_ONE_HOME: documentation/agents-reference.md:<line>:` + the headword and an overlap matching `[01]\.[0-9]{2}` |
| case_fd_reference_opener | (a) `agents-reference.md` opens with its table (AC-24); (b) opener kept, `term-skill` link removed | `front-door: REFERENCE_OPENS_WITH_ITS_DEFINITION: documentation/agents-reference.md:<line>:` + (a) `An agent is`; (b) `term-skill` |
| case_fd_enforcement_row | (a) a row whose What it can miss cell is empty (AC-26); (b) a row with no `enf-` anchor; (c) Class `**strong**` (AC-26); (d) Artifact `` `tools/no-such.py` ``; (e) a four-cell row | `front-door: ENFORCEMENT_ROW_COMPLETE: DOCUMENTATION.md:<row line>:` + (a) `What it can miss`; (b) `enf-`; (c) `strong`; (d) `tools/no-such.py`; (e) `cells` |
| case_fd_enforcement_required_row | the `enf-spec-before-code` row deleted (AC-26) | `front-door: ENFORCEMENT_ROW_COMPLETE: DOCUMENTATION.md:0:` + `enf-spec-before-code` |
| case_fd_enforcement_row_residuals | (a) `role emulation` dropped from `enf-tool-allowlist`'s miss cell; (b) `enf-leaf-cannot-spawn`'s Class cell reduced to `**hard**`; (c) `fails open` dropped from `enf-pre-bash-guard`; (d) `.cypress/seed.json` dropped from `enf-backup-before-replace`; (e) `Bash` dropped from `enf-tool-allowlist`; (f) `enf-pre-bash-guard` carrying a `**hard**` not scoped to a matched command on a host that fires the hook (all AC-26) | `front-door: ENFORCEMENT_ROW_COMPLETE: DOCUMENTATION.md:<row line>:` + the row id and (a) `role emulation`; (b) `weakest class`; (c) `fail`; (d) `.cypress/seed.json`; (e) `Bash`; (f) `hard` |
| case_fd_mechanism_traced | unlinked "The gate enforces every spec before code." in (a) README; (b) `INSTALL.md`; (c) an `integrations/<host>/README.md` stub; (d) the `plant` Here field; (e) README, linked to `DOCUMENTATION.md#enf-no-such-row`; (f) unlinked "the installer never merges a file" in `INSTALL.md` (AC-9, AC-16) | `front-door: MECHANISM_CLAIMS_TRACED: <file>:<line>:` with file (a) `README.md`, (b) `INSTALL.md`, (c) the stub's path, (d) `DOCUMENTATION.md`, (e) `README.md`, (f) `INSTALL.md` + (a)–(d) `enforces`; (e) `enf-no-such-row`; (f) `never` |
| case_fd_mechanism_overclaim | the §8 overclaim sentence, "a hard 8 000-byte budget", linked only to `enf-kernel-budget` (soft) (AC-10) | `front-door: MECHANISM_CLAIMS_TRACED: README.md:<line>:` + `overclaim` and `enf-kernel-budget` |
| case_fd_mechanism_surfaces | (a) `INSTALL.md` "the harness blocks the tool for a leaf" linked to a row classed both `**hard**` and `**judgment**`; (b) README "refuses" linked to a soft row; (c) a glossary Enforcement field saying `**hard**` whose linked rows are all weaker; (d) a glossary Enforcement field naming `**detective**` that no linked row's Class cell holds, and one naming `**soft**` with no `enf-` link; (e) a strong claim in `DOCUMENTATION.md` outside the glossary linking a soft row; (f) README "the security guard" linked to `enf-pre-bash-guard` (AC-26); (g) `sandbox` in an `INSTALL.md` unit linking `enf-pre-bash-guard`; (h) passes: "No tool blocks code written before its spec" linked to a judgment row, "nothing here is hard", and an unlinked strong claim in `documentation/agents-reference.md` (AC-10, §7 `STRONG_CLAIM_IN_MANUAL_PROSE`) | `front-door: MECHANISM_CLAIMS_TRACED: <file>:<line>:` + (a) `INSTALL.md`, `overclaim`, `judgment`; (b) `README.md`, `overclaim`; (c) `DOCUMENTATION.md`, `hard`; (d) `DOCUMENTATION.md`, `detective`, then `enf-`; (e) `DOCUMENTATION.md`, `overclaim`; (f) `README.md`, `enf-pre-bash-guard` and `secur`; (g) `INSTALL.md`, `sandbox`; (h) no MECHANISM_CLAIMS_TRACED line naming those units |
| case_fd_hook_firing | (a) `enf-route-hook` Class `**hard**` (AC-27); (b) `not a control` removed from the ADR-0003 cell of the matrix class-table row whose first cell is `**mechanically enforced**` (AC-27, P9); (c) `injects` removed from that row's Meaning cell; (d) `enf-status-hook` Class `**soft**` | `front-door: ENFORCEMENT_ROW_COMPLETE:` + (a) `DOCUMENTATION.md:<row line>:` and `enf-route-hook` and `not a control`; (b) `documentation/host-capability-matrix.md:<line>:` and `not a control`; (c) the same file and `injects`; (d) `DOCUMENTATION.md:<row line>:` and `enf-status-hook` and `not a control` |
| case_fd_limits_hard_row | a Requested item that links (a) only a row whose only class is `**hard**`; (b) no row (AC-11) | `front-door: LIMITS_SECTION_PRESENT: README.md:<line>:` + (a) `hard`; (b) `enf-` |
| case_fd_limits_required_rows | (a) the `enf-test-before-code` link dropped (AC-11); (b) the two subsections swapped | `front-door: LIMITS_SECTION_PRESENT: README.md:` + (a) `enf-test-before-code`; (b) `Requested, not enforced` |
| case_fd_limits_unmeasured | a Not-yet-measured item with none of the three phrases | `front-door: LIMITS_SECTION_PRESENT: README.md:<line>:` + `not measured` |
| case_fd_catalogs | every agent name in code spans in README (AC-12) | `front-door: CATALOGS_OUT_OF_README: README.md:` + `agents` |
| case_fd_adr_range | `ADR-0001 to ADR-0010` in `INSTALL.md` | `front-door: CATALOGS_OUT_OF_README: INSTALL.md:<line>:` + `ADR-0001 to ADR-0010` |
| case_fd_cost_scope | a figure with no scope marker | `front-door: COST_FIGURES_SCOPED: README.md:<line>:` + `scope` |
| case_fd_cost_provenance | (a) a "7 742 bytes" kernel figure per session that nothing derives (AC-13); (b) "10 to 20%" with no evidence link (AC-13) | `front-door: COST_FIGURES_SCOPED: README.md:<line>:` + (a) `7 742`; (b) `20%` |
| case_fd_cost_measured_derived | (a) `the 8 000-byte budget per session, measured`; (b) the `ee4cd95` lead-in `measured rather than estimated` above the derived always-loaded row (AC-14) | `front-door: COST_FIGURES_SCOPED: README.md:<line>:` + `measured` |
| case_fd_cost_no_derived | the cost section's only derived figure replaced by `not measured` | `front-door: COST_FIGURES_SCOPED: README.md:0:` + `derived` |
| case_fd_measured_evidence | `10 to 20%` measured once and linked to the fixture record that holds 11% | `front-door: COST_FIGURES_SCOPED: README.md:<line>:` + `10%` and the record's path |
| case_fd_eager_published | (a) an always-loaded figure nothing computes in `documentation/agents-reference.md` (AC-17); (b) the same in `INSTALL.md`; (c) slug forced into the ledger and a stale figure put in README: exit 1 still | `front-door: EAGER_FIGURES_CHECKED_WHEREVER_PUBLISHED:` + (a) `documentation/agents-reference.md:<line>:`; (b) `INSTALL.md:<line>:`; (c) `README.md:<line>:`, and no `front-door: PENDING EAGER_FIGURES_CHECKED_WHEREVER_PUBLISHED` line |
| case_fd_body_home | (a) the median dropped from DOCUMENTATION's body-figure paragraph (AC-17); (b) the whole paragraph removed; (c) `consequently **empty**` in `INSTALL.md` with an `EAGER_EXEMPTIONS` entry injected into the copy's seed-lint | `front-door: BODY_FIGURES_HAVE_A_REQUIRED_HOME:` + (a) `DOCUMENTATION.md:0:` and `median`; (b) `DOCUMENTATION.md:0:` and `largest`; (c) `INSTALL.md:<line>:` and `consequently` |
| case_fd_body_figure_elsewhere | `the largest body is 1 384 lines` in `INSTALL.md` (AC-17) | `front-door: BODY_FIGURES_HAVE_A_REQUIRED_HOME: INSTALL.md:<line>:` + `1 384` |
| case_fd_body_project_node | (a) passes: `the project-node body ceiling is ~150 lines` in `documentation/skills-and-templates-reference.md`; (b) the same unit with `~151 lines`; (c) the `150` literal removed from the copy's `templates/knowledge-graph/graph-lint.py` | (a) no BODY_FIGURES_HAVE_A_REQUIRED_HOME line naming that unit; (b) `front-door: BODY_FIGURES_HAVE_A_REQUIRED_HOME: documentation/skills-and-templates-reference.md:<line>:` + `151`; (c) `front-door: BODY_FIGURES_HAVE_A_REQUIRED_HOME: templates/knowledge-graph/graph-lint.py:0:` + `150` |
| case_fd_anchor_resolves | (a) README links `DOCUMENTATION.md#term-plnat` (AC-25); (b) README links `docs/no-such.md` | `front-door: FRONT_DOOR_ANCHORS_RESOLVE: README.md:<line>:` + (a) `term-plnat`; (b) `docs/no-such.md` |
| case_fd_anchor_duplicate | a second `<a id="term-plant"></a>` | `front-door: FRONT_DOOR_ANCHORS_RESOLVE: DOCUMENTATION.md:<second line>:` + `term-plant` |
| case_fd_headings | (a) `####` directly under `##` in README; (b) a second `#` in DOCUMENTATION; (c) a reference whose first heading is `##` | `front-door: FRONT_DOOR_HEADINGS_WELL_FORMED:` + (a) `README.md:<line>:` and `level`; (b) `DOCUMENTATION.md:<line>:` and `level-1`; (c) the reference's path, `:<line>:` and `level-1` |
| case_fd_link_text | (a) `[here](INSTALL.md)`; (b) `[https://example.org](...)` in the enforcement region (AC-20); (c) `[](INSTALL.md)` | `front-door: LINK_TEXT_STANDS_ALONE:` + (a) `README.md:<line>:` and `here`; (b) `DOCUMENTATION.md:<line>:` and `https://`; (c) `README.md:<line>:` and `empty` |
| case_fd_table_header | (a) a README table whose header cells are all blank (AC-21's two-blank-cell header); (b) a header cell holding only `**` (AC-21) | `front-door: TABLES_HAVE_HEADER_ROWS: README.md:<line>:` + `header` |
| case_fd_pending_stale | ledger `{LINK_TEXT_STANDS_ALONE}` over the conforming fixture | `front-door: PENDING_LEDGER_HOLDS_ONLY_FAILING_CONTRACTS: tests/seed-lint.py:` + `stale pending entry: remove it` and `LINK_TEXT_STANDS_ALONE` |
| case_fd_pending_unknown_slug | ledger holds (a) `NOT_A_CONTRACT`; (b) this contract's own slug; (c) `PROSE_FLOOR_HELD_PER_FILE`; (d) a member that `tests/ratchets.json` does not mirror | `front-door: PENDING_LEDGER_HOLDS_ONLY_FAILING_CONTRACTS: tests/seed-lint.py:` + (a) `NOT_A_CONTRACT`; (b) `PENDING_LEDGER_HOLDS_ONLY_FAILING_CONTRACTS`; (c) `PROSE_FLOOR_HELD_PER_FILE`; (d) `tests/ratchets.json` |
| case_fd_pending_holds_exit | real-tree copy: (a) ledger intact; (b) ledger emptied | (a) exit 0, exactly one `front-door: PENDING <SLUG>: <n> finding(s); first: ` line per member, no `stale pending entry`; (b) exit 1 and a `front-door: <SLUG>: <file>:` line for every former member |
| case_fd_pending_implemented | the copy's SPEC-0004 frontmatter set to `status: implemented`; `LINK_TEXT_STANDS_ALONE` added to `FRONT_DOOR_PENDING` and to the copy's `tests/ratchets.json` in the same edit, with `[here](INSTALL.md)` planted so the slug genuinely fails (AC-28) | exit 1 and `front-door: PENDING_LEDGER_HOLDS_ONLY_FAILING_CONTRACTS: tests/seed-lint.py:` + `ledger must be empty once SPEC-0004 is implemented`; `python3 tools/ratchet-lint.py` on the same copy exits 0, recorded so the refusal is shown to be seed-lint's |
| case_fd_pending_release | binding status only (spec `active`); `LINK_TEXT_STANDS_ALONE` added to `FRONT_DOOR_PENDING` and to the copy's `tests/ratchets.json`, with `[here](INSTALL.md)` planted so the slug genuinely fails; the copy's `manifest.json` `version` set to (a) `7.29.0` (AC-28); (b) `7.100.0`; (c) passes: `7.28.0` (AC-28's control); (d) passes: `7.9.0`. (b) and (d) pin the integer-tuple comparison, which a string comparison inverts | (a), (b) exit 1 and `front-door: PENDING_LEDGER_HOLDS_ONLY_FAILING_CONTRACTS: tests/seed-lint.py:` + `ledger must be empty from 7.29.0`, with no `ledger must be empty once` line; (c), (d) no `ledger must be empty from` line and exactly one `front-door: PENDING LINK_TEXT_STANDS_ALONE: ` line; their exit code is evidence only from increment 5 (case discipline above) |
| case_fd_absent_inputs | README cut to its `#` title, and DOCUMENTATION without regions 15 and 17 | for every slug §6 "Required inputs" lists against those inputs, looped: `front-door: <SLUG>: <file>:0:` + the missing input's name |
| case_fd_unreadable_input | invalid UTF-8 bytes appended to `INSTALL.md` | for every slug whose check reads `INSTALL.md`, looped: `front-door: <SLUG>: INSTALL.md:0:` + `UTF-8` |
| case_fd_check_raised | `raise RuntimeError("planted")` injected at the top of `check_fd_tables_have_header_rows` in the copy, ledger `{TABLES_HAVE_HEADER_ROWS}` (AC-28) | exit 1 and `front-door: TABLES_HAVE_HEADER_ROWS: RAISED RuntimeError: planted`; no `stale pending entry` line and no `front-door: PENDING TABLES_HAVE_HEADER_ROWS` line. The one case exempt from the `: RAISED ` refusal |
| test_prose_lint_one_step_per_file | a synthetic `run.sh` with one `--file` per line; also asserts that the real `run.sh` has one step each for README.md and DOCUMENTATION.md | steps `prose-lint.py --file README.md` and `prose-lint.py --file DOCUMENTATION.md`. At `ee4cd95` both lines collapse into the one blended name (probed) |
| test_prose_lint_multi_file_refused | one line passing two `--file` arguments | `--lint` rc 1, and stderr names the line. At `ee4cd95` rc is 0 (probed) |
| test_prose_lint_same_name_refused | (a) a synthetic `run.sh` with two prose-lint lines both naming `README.md`; (b) control: lines for `README.md` and `integrations/example/README.md` (AC-29) | (a) `--lint` rc 1, and stderr names both lines; (b) two distinct steps, `prose-lint.py --file README.md` and `prose-lint.py --file integrations/example/README.md`, and rc 0. Behaviour at `ee4cd95`: the second line merges into the first (`tools/gate-registry.py:473`, per grill §6); not probed in this pass |

Grill §9 increment 1 names every case in this table; the two lists must stay
equal.

**Written and observed red (2026-09-24, increment 1, `tester`).** The 54
`case_fd_*` are in `tests/test-seed-lint.sh`, over one shared helper
(`fd_py`, `fd_fresh`) and the fixture in `tests/fixtures/front-door/`; the
three `test_prose_lint_*` are in `tests/test_gate_registry.py` under
`expectedFailure`. Observed on a copy of the tree with this spec `active` and
no `check_fd_*`: X300 passes, as a guard must; the other 53 fail, 47 because
their first anchored line is absent and 6 (the five `case_fd_pending_*` and
case_fd_check_raised) at setup, because `tests/seed-lint.py` defines no
`FRONT_DOOR_PENDING` and no `check_fd_tables_have_header_rows`. The three
Python tests fail on their assertions. The cases fix these conventions where
the tables above leave them open:

- A finding about an entry sits on its `###` headword line. A finding about
  one field sits on that field's line or on the headword line. A finding about
  a row sits on the row's line, and a finding about order sits on either
  swapped line.
- case_fd_absent_inputs expects each line-0 finding to name its input:
  `heading` for FIRST_SCREEN_ORDER, the missing section's heading text for the
  four README section contracts, and `glossary` or `enforcement` for a
  missing region.
- A message fragment matches case-insensitively on the anchored line.
- `FRONT_DOOR_PENDING` is one top-level assignment, mirrored under the same
  key in `tests/ratchets.json`. The three first-screen ceilings are top-level
  integer assignments named as their `tests/ratchets.json` keys.
- The version binding moves `manifest.json`, the top `CHANGELOG.md` heading
  and the two documented-version pins together, so the copy stays
  self-consistent.
- case_fd_unreadable_input needs the front-door checks to run even when an
  earlier seed-lint check raised on the same file.

## 11. Open questions

| Question | Why it matters | Current assumption | Owner | Resolves by |
|---|---|---|---|---|
| Is meaning carried only by emphasis (product AC-22) acceptable to leave to judgment? | No stdlib check can tell whether bold carries meaning the words do not | Accepted residual: the reviewer judges it at verify against the README, glossary and enforcement section | product | reviewer's verify pass on the README increment |
| Must the cost section list what the always-loaded figure leaves out and say no money figure exists (product G8)? | Readers missed both in the baseline reader test | Accepted residual: a phrase check would pin wording, not meaning; product's detective reader test holds it | product | the after reader test |
| Old README anchors (`#what-you-get`, `#try-it-and-what-it-costs`) stop resolving (product G11) | External bookmarks break; Markdown cannot redirect | Accepted residual: the release's CHANGELOG entry names the removed anchors, and "Where to go next" is the recovery | orchestrator | the provenance increment |
| Limits items may link a matrix anchor (product AC-11) | Matrix anchors are generated from headings; the gate cannot resolve them without reimplementing the host's slug rules | Stricter: limits items link `enf-` rows only, and each row links the matrix | product | product's re-map of AC-11 |
| ~~Product AC mappings for the contracts added after §9 was drafted~~ | resolved 2026-09-24: product re-mapped §9 to all 25 contracts (coverage table at the end of §9) and signed off in §0 | — | product | closed |
| Is 0.50 containment the right `DEFINITION_OVERLAP_CEILING`? | Too low flags legitimate elaboration; too high lets a copy through | 0.50 is a design threshold, not a measured quantity; if the dependent-cleanup increment finds a legitimate unit at or above it, the unit is reworded to link rather than restate, and the ceiling does not rise | architect | the dependent-cleanup increment |
| ~~Strong claims widened from `hard/cannot/can't/guarantee` to add `ensur-`, `prevent-`, `block-`, `refus-`, `stops` (security S1); `never` and `only` left out~~ | resolved 2026-09-24: product aligned §3.3 and AC-10 (strong-claim list incl. "refuses", weakest-class-hard rule) | — | product | closed |
| ~~Tracing widened from README to the §6 traced surfaces; overclaim refusal to every front-door unit that links a row (security S1)~~ | resolved 2026-09-24: product aligned AC-9 and AC-16 to the §6 traced surfaces; manual prose stays a named residual | — | product | closed |
| Accepted residual: `HOST_FACT_RESTATED` (security S2) | Nothing mechanical keeps M7 to M9 out of glossary fields, rows and the ADR-0003 amendment | Judged at verify by the reviewer; a phrase check belongs to the separate host-facts change, which has its own spec | security; reviewer | verify of increments 2, 3, 5 and 6 (6 added 2026-09-24: it edits `INSTALL.md` and the integration READMEs) |
| Accepted residual: `CLASS_CELL_UNTRUE` | The checks hold class vocabulary and the named residuals, never that a class is true | `security` signs the Class column row by row against ADR-0003 at verify of increment 3 | security | verify of increment 3 |
| Accepted residual: `PENDING_LEDGER_MASKS_A_REGRESSION` (reliability R8) | A regression in already-conforming text of a pending slug only raises a logged count | A per-slug count ratchet was rejected (§7); the count is captured in every increment's handback and the ledger is empty after increment 6 | architect | increment 6 |
| Old README anchors (reliability R7): keep empty `<a id="what-you-get"></a>`-style anchors on the successor sections? | They would let a bookmark land on the successor section | Not kept. Whether the host resolves an `<a id>` tag in a rendered README fragment is not recorded, so the anchor would be an unverified promise. The CHANGELOG names the removed anchors either way (G11 above). Reversible: add them in a later release once the host behaviour is recorded. (2026-09-24: now conditional on the one anchor-render observation in the row above, the same premise the `term-`/`enf-` anchors rest on. If it resolves, product may keep them in increment 5) | orchestrator, product | the anchor-render observation, then increment 5 |
| ~~"Try it" and the default branch (security S5)~~ | resolved 2026-09-24: product aligned §3.1 item 5 (README states the command tracks the default branch); residual G13 | — | product | closed |
| ~~README names hosts with their support tier (§3.1 item 2)~~ | resolved 2026-09-24: product chose link-not-print (§3.1 item 2): README names hosts, prints no tier, links the matrix support-tier section and ADR-0009; residual G12, judged by the reviewer at verify | — | product | closed |
| ~~Would minimum sufficient (G9) return any contract?~~ | resolved 2026-09-24 by steward decision D1: three contracts folded (`HOOK_FIRING_IS_NOT_HOLDING` into `ENFORCEMENT_ROW_COMPLETE` and the §6 row-specific table; `README_LATER_SECTIONS_ORDER` into `FIRST_SCREEN_ORDER`; `MEASURED_FIGURE_MATCHES_ITS_EVIDENCE` into `COST_FIGURES_SCOPED`'s measured branch). Twenty-two contracts; every RED case keeps its plant under the absorbing slug. Product re-maps AC-1, AC-13, AC-27 and the coverage table; tester re-keys §10 | — | steward | closed |
| Does the publishing host resolve an explicit `<a id>` fragment in rendered Markdown? | Every `term-`/`enf-` link, and the legacy-anchor option, assumes it; no check can see a rendered page (§7 `ANCHOR_NOT_RENDERED_BY_HOST`) | Not recorded. Do not guess: before increment 2 the steward observes one rendered fragment on the publishing host (for example on the pushed branch). If it resolves, the explicit-anchor design stands and legacy anchors become product's option. If it does not, the anchor design is reopened before any entry lands (grill §6) | steward (observation); architect (reopen if negative) | before increment 2 |
| Which convention governs a ratified seed ADR: supersede only, or supersede or amend? | `skills/adr-writer/SKILL.md:85-86` says the supersede flip is "the only edit a ratified ADR ever receives"; `docs/decisions/index.md:45` says "supersede or amend, never rewrite", and ADR-0002 (2026-07-23) and ADR-0003 (2026-09-14) already carry appended amendments | Not resolved here. Increment 3's ADR-0003 amendment follows `docs/decisions/index.md:45` and its two precedents. The skill's paths are `docs/graph/decisions/` in an installed project, while `docs/decisions/index.md:3-6` places the seed's own ADRs outside `docs/graph/` on purpose. The amendment corrects a count and leaves the decision alone, so it needs no new ADR. Whether the skill's rule should also bind the seed's self-docs, or the index should narrow, is the docs-librarian's call | docs-librarian | canonize of this harvest |
| The matrix classes a hook that only injects text as `hard` (`documentation/host-capability-matrix.md:36`, applied at `:89-90`) and the leaf's spawn bar as `hard` with no scope (`:96-97`, `:199-200`), against this spec's rows (press P9) | The front door's rows link the matrix as their detail, so the two would contradict each other one click apart | Reconcile, don't record a residual: increment 3 changes class wording only, adding no host fact. The ADR-0003 cell of `:36` gains `not a control` for a hook that only injects (held by `ENFORCEMENT_ROW_COMPLETE`); `:96-97` and `:199-200` scope "hard" and link `enf-leaf-cannot-spawn` with no strong-claim word (reviewer at verify). A residual would leave the reader's detail page contradicting the row that sends them there | architect (design); implementer (edit); reviewer | verify of increment 3 |

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
