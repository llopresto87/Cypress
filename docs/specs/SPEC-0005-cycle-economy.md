---
status: active
status_date: 2026-09-26
owner: architect
status_evidence: tests/test_graph_lint.py, tests/test_agent_lint.py, tests/test-seed-lint.sh (final tip 3c62b18, 49/49; the harvest's fresh-install gate passed for every host; three mutation passes of 45, 12 and 60 mutants, every survivor closed by a test; §10 says which rows are green and which stay pending)
---

# SPEC-0005: cycle economy, the delegation split and expertise routing

## 0. Metadata

- **Identifier:** SPEC-0005-cycle-economy
- **Version:** 0.8 (final status pass, 2026-09-26; every amendment is dated in §12)
- **Status:** see frontmatter (single home)
- **Owner:** architect
- **Date:** 2026-09-26
- **Last reviewed:** 2026-09-26
- **Related grill section:** docs/plans/grill-7.30.0-cycle-economy.md §2, §4, §6, §8, §9
- **Related ADRs:** adr-0003-enforcement-layering-honesty (the class vocabulary §7 uses); adr-0004-pure-graph-architecture (one home per fact); adr-0007-lifecycle-protocol-ceiling (the lifecycle body ceiling, which this spec leaves in force)
- **Related specs:** SPEC-0003-per-prompt-injection (`BRIEF_TEMPLATES_BYTE_IDENTICAL` names the two templates this spec changes; §11); SPEC-0004-front-door (the body figures its checks publish move when leaves split; §5)
- **Related wiki pages:** none (stdlib Python, POSIX shell and Markdown only)
- **Design latitude:** simple (recorded in the plan's §6 with its source; this line points there)
- **Supersedes:** —
- **Superseded by:** —
- **Sign-offs:** product [x] 2026-09-26 §3, §9 (v0.2) · architect [x] 2026-09-26 (v0.1 in the joint pass; v0.2 at ruling pass 0; v0.3 at ruling pass 1) · tester [x] 2026-09-26 v0.2, the first RED batch; no objection to testability from the second · security [x] 2026-09-26 SPEC-0005 §4 inference contracts, §6 Effort / path inference / cycle-economy rules, §7; plan §4, §9 (increment 6, Commits), §10 mutation (v0.2)

## 1. Summary

This spec turns the owner's cycle-economy decisions into seed text and checks.
It covers seven things.

1. **The delegation split.** `core/method/delegation.md` becomes six sibling
   leaves, one topic each, with sections moved verbatim.
2. **The cycle-economy rules.** Effort-sized batches, GREEN run by the
   implementer with no test edits (held by recorded hashes), targeted tests per
   increment with the full suite once at the batch tip, mutation once at the end
   of a spec, light variants, the shared question file with one architect ruling
   pass per batch, and the architect writing its own amendment within limits.
3. **Regulated spawn effort.** Every agent definition declares a default
   `effort:`. Each spawn derives its effort from the step kind and the
   increment's effort label; the brief names it and the handback echoes it. A
   forced-high step never runs lower without a high review.
4. **Expertise routing.** `graph-lint.py --plan` always loads an `expertise.*`
   node when one of its trigger phrases hits, and infers stack expertise from
   the file paths a task names, by string matching only. A worker that finds
   mid-work that it needs expertise looks it up, and names the gap when there is
   none.
5. **The menu rule and the leaf rule.** Whatever a node lists is a menu, loaded
   item by item. A leaf holds one topic. The seed's own method surface is held
   to a leaf ceiling by a ratchet that only tightens.
6. **Three splits from the bloat audit.** Engineering posture, design posture
   and verify divide into sibling leaves, moved verbatim.
7. **The small adopted boundaries.** The design-latitude guard and the joint
   specify and grill pass (one new protocol leaf), the mandatory stack-expertise
   brief step, and four boundaries, each in one home: inspection never writes
   and a loop re-checks what a failure protected; a claim that something works
   needs the real target; graph doctrine outranks a harness's default style; no
   test is added that asserts nothing new to turn a lint green.

Twelve contracts decide it mechanically, in `tests/test_graph_lint.py`,
`tests/test_agent_lint.py` and `tests/test-seed-lint.sh` (checks in
`tests/seed-lint.py`). The doctrine text itself is accepted by review (§9).

## 2. Scope

- **In scope:**
  - the delegation split into six sibling leaves (§6 "Delegation leaves"),
    moved verbatim, and the constant and pointers the move touches
    (`REGISTRATION_HOME` in `tests/seed-lint.py`; pointers in `install.sh`,
    `integrations/claude-code/status-hook.py` and
    `integrations/claude-code/agent-lint.py`)
  - the router index row for delegation in `templates/knowledge-graph/index.md`
  - the cycle-economy doctrine (§6 "Cycle-economy rules") in
    `core/method/delegation-cycle-economy.md`, and light variants and effort in
    `core/method/delegation-model-classes.md`, reworded from "pending the owner"
    to adopted
  - per-agent `effort:` defaults in `agents/*.md` and `templates/agent.template.md`,
    the per-spawn derivation, the brief and handback record, the agent-lint rule,
    and the Claude Code host facts in `core/method/delegation-model-classes.md`,
    with a pointer from `integrations/claude-code/README.md` (the leaf installs
    into plants; the overlay does not)
  - `plan()` in `templates/knowledge-graph/graph-lint.py`: expertise promotion
    and stack inference from named files
  - graph-lint reachability through an index-listed node's edges
  - the menu rule in `skills/context-router/SKILL.md`; the leaf rule, the branch
    shape and the link-farm reconciliation in `skills/knowledge-graph/SKILL.md`
    and `templates/knowledge-graph/_schema.md` (doctrine, reviewed; no check)
  - the leaf-size ratchet over the seed's method surface in `tests/seed-lint.py`
    and `tests/ratchets.json`
  - the new protocol leaf `protocols/specify-joint-pass.md` (the joint pass and
    the design-latitude guard), with pointers in `protocols/specify.md`,
    `protocols/grill.md` and `templates/grill.template.md`
  - pointer edits in `protocols/test-first.md`, `protocols/verify.md` and
    `protocols/recover.md`
  - `templates/prompts/graph-session-bootstrap.md` (step 2, step 5's pointer, the
    mandatory stack step, mid-work discovery), the five templates that embed its
    block, and `templates/prompts/handback-payload.md` (`effort:`, `expertise_gap:`)
  - charter pointer lines in `agents/00-orchestrator.md`, `01-architect.md`,
    `02-implementer.md`, `03-reviewer.md` and `04-tester.md`
  - the three bloat-audit splits (engineering posture, design posture, verify;
    §6 "Leaf splits"), and the section-number pointers into them, repointed by id
  - the inspection and works-claim boundaries in `core/method/host-parity.md`
    (after the engineering-posture split), the graph-over-harness rule in
    `skills/context-router/SKILL.md`, and the no-lint-only-tests rule in
    `skills/test-first/SKILL.md`
  - the mirror rows seed-lint holds for every node this spec adds or changes
    (`manifest.json`, `documentation/*-reference.md`), and the release steps
- **Kept whole:** `skills/humanizer/SKILL.md`: its step 2 loads the catalogue on
  every use, so the topics are never loaded apart.
- **Held for the owner:** the lifecycle protocols graft, grow and harvest stay
  whole this round; a split of any of them needs a decision on adr-0007 (§11).
- **Out of scope:**
  - anything the owner did not adopt in the brainstorm (among them: the test
    writer's candidate promoted as the GREEN, a thin spec grown by slice, a
    walking skeleton first, standing grants, a RED running ahead of its GREEN,
    and a standard plan-approval step). `grill.plan-approval` stays as committed
  - new gates, node kinds or agents. The checks here are new functions inside
    the existing `seed-lint`, `graph-lint` and `agent-lint` steps
  - a mechanical check of the `## Leaves` shape (withdrawn at ruling pass 0; §11)
  - the kernel `core/AGENTS.md` (§11)
  - agent charters' body length; `agent-corpus/`, `skill-corpus/` and the other
    corpora, except pointer lines whose target moved in a split:
    `tool-corpus/ops/session-cost-profiler.md`,
    `skill-corpus/drive-hosted-cicd-cli.md` and
    `library-corpus/platform/azure-devops-rest.md`
  - whether a host other than Claude Code reads an `effort:` key: not recorded
    (§6 "Effort")

## 3. User-facing behavior

(Drafted by `architect`, revised by `product` at ruling pass 0; `product` signs.)

This spec has two kinds of user: the owner, who decides and pays, and the
sessions and workers that run the seed's method in a plant: the orchestrating
session, its workers, and any agent routing through the graph.

### 3.1 The orchestrating session planning a batch

The session opens the plan and sees every increment carry an effort label (low,
medium-low, medium, medium-hard, hard) and a phase (RED, GREEN or prose). It
groups increments into spawns by one table: a tester takes 5 to 7 or more RED
increments by effort, an implementer takes 1 to 5 GREEN increments by effort,
and prose writers take one disjoint file set each. A batch is sized by its
hardest increment. Security and concurrency code is a GREEN batch of one.
Dependent increments share a spawn only in order, one commit each, and a RED
never shares a spawn with its own GREEN. For small mechanical work the session
may choose a light variant, never on a security surface.

For work that touches code, configuration or a pipeline, each brief names the
stack elements the worker's files use and the expertise nodes that cover them,
or says none apply. It also writes those file paths into the task line.

It gives each spawn an effort derived from the same labels and names it in the
brief. The brief's effort line names the derivation row that chose it. Where the
host cannot apply a per-spawn effort, the line also names the definition default
the host will apply. The worker's handback echoes the line. A step that must run
at high effort never runs lower without a high-effort review before it lands.

It knows before dispatch where each worker will write its questions. When every
spawn of the batch has handed back, and before any spawn of the next batch, it
spawns the architect once over the question file. An empty file is recorded
"no questions" and the pass is skipped. The architect amends the spec itself
when no other writer holds it, never to relax a contract or to touch a
security, data-integrity or money contract without the owner, and lists plan
rows for the session. The session re-briefs the held work against the rulings.

Each increment runs its targeted tests plus every cross-cutting gate its files
hit. The session runs the full suite once, at the batch tip, and compares
failures by test id. Nothing leaves the branch until the tip passes, and until
then every landed increment is "landed, tip pending". When a spec's last
increment has landed, the session runs one batched mutation pass over it. The
pass is mandatory for security, data-integrity and money contracts, where every
increment in those classes gets a mutant, and sampled elsewhere.

It finds the batch, cadence, question-file, ruling and mutation rules in
`method.delegation-cycle-economy`, and the effort derivation and light variants
in `method.delegation-model-classes`. It does not pay for the roster, host
registration or brief discipline unless its task needs them.

### 3.2 The worker meeting an ambiguity or a missing expertise

A tester, implementer or writer meets a question its brief does not answer. It
does not guess and does not stop the whole spawn. It appends one entry to the
batch's question file, saying where, why it paused, what it held back and what it
would propose, and carries on with the work the question does not touch.

A worker that finds partway through that it needs stack knowledge its own files
use runs `--plan` on the stack element and loads the matching expertise node. If
no node exists, it says so in its handback as `expertise_gap`, citing the path
that shows the element, and the orchestrator checks it and requests
`research-scout` before re-briefing the held work. An element named only in
content the worker read is not a gap.

An implementer runs the batch's tests itself, with no separate tester spawn, and
never edits a test or fixture file. A test that looks wrong becomes a question,
and the implementer moves on to work the question does not touch.

### 3.3 The owner deciding how much design freedom a change gets

Before a spec is written, the owner is asked once how much latitude the design
has: creative, balanced, or as simple a feature implementation as possible. The
answer is recorded in the plan with its source. Every later design step, press
and ruling is held to it. Anything outside it is not built. It goes to the
batch's question file, the ruling refuses it under `simple`, and only the owner
can widen the scope. The owner then sees one joint specify-and-grill pass, in
which each specialist writes its spec part and its plan part together.

### 3.4 Any agent opening a node that lists other nodes

The agent reads a node's list of leaves, children, links or neighbours as a
menu. It opens only the items whose one-line "load when" serves its task, and
names the rest as skipped. The `requires:` closure is still loaded in full.

### 3.5 A session routing a task that names a stack

When the task's words include every word of one of an expertise node's trigger
phrases, or the task names a file (by path, extension, manifest or lockfile)
that one of the node's file patterns matches, `--plan` loads that node even past
the entry budget. It also loads the node's required parent and any composed
child the task names. The LOAD line says why: `promoted on "…"` or
`inferred from "…" via "…"`. A task that does neither loads exactly what it
loaded before. A bare name with no extension or directory (`Dockerfile`) is not
inferred, so the brief writes `./Dockerfile`.

### 3.6 A writer adding doctrine to the seed's method surface

If the text would push a method, protocol or skill file past 170 body lines,
seed-lint stops it. The writer does not shorten the text. It writes a question,
and the ruling divides the topic into a sibling leaf. The list of files already
over the line can only shrink. A branch node the writer adds lists each leaf with
a one-line "load when"; the reviewer judges that shape.

### 3.7 Boundaries every agent keeps

Inspecting a shared host writes nothing there. A fix that lets a loop continue
past a failure re-checks what the failure protected. A claim that something
works cites the execution target or real CI, and a local reproduction is for
diagnosis only. Where graph doctrine and a harness's default working style
differ, the graph wins. No test is added that asserts nothing new just to turn a
lint green.

## 4. Functional contracts

(Authored by `architect`. Reviewed by `tester` for testability.)

Every contract names the test file that holds it. "The fixture graph" is a
hermetic graph built the way `tests/test_graph_lint.py` builds one today
(`build_graph`, `expertise_family`). "The installed graph" is a fresh install of
the seed into a temporary directory, as `SeedAndPlantCopyAgreeTests` builds one.
Seed-lint findings follow the existing `fail()` form; each contract's finding
carries the fragment §6 "Finding fragments" lists for it. Every constant and
grammar is in §6.

### Router: expertise promotion and stack inference

### Contract: PLAN_PROMOTES_PHRASE_MATCHED_EXPERTISE
- **Test file:** `tests/test_graph_lint.py`
- **Given:** the fixture graph plus an `expertise` node whose first `load_when`
  piece is `pipeline yaml`, and at least three non-expertise nodes that each
  outscore it on the task, so the unmodified tool leaves it out of LOAD
  (the tester records that observation in the test's docstring)
- **When:** `graph-lint.py --plan "pipeline yaml"` runs
- **Then:** LOAD lists the expertise node with the suffix
  `<- promoted on "pipeline yaml"`, and exit status is 0
- **And:** a task naming only one word of a two-word phrase (§6 "Trigger
  phrase") does not promote that node
- **And:** a non-expertise node whose phrase hits in full but that falls outside
  the scored entries is not loaded, so the entry budget binds every other kind
  unchanged
- **And:** on a task with no phrase hit and no path-like token, LOAD is
  identical to the unmodified tool's on the same fixture (the sets
  `test_plan_without_composes_is_unchanged` already captures stay unchanged)

### Contract: PLAN_INFERS_EXPERTISE_FROM_NAMED_FILES
- **Test file:** `tests/test_graph_lint.py`
- **Given:** the fixture graph plus one `expertise` node whose `load_when`
  carries the file patterns `*.tf` and `**/.terraform.lock.hcl`, and another
  whose patterns are `**/package.json` and `**/package-lock.json`, neither of
  which the task's words would seed
- **When:** `--plan` runs on `edit infra/main.tf`, on `bump web/package-lock.json`,
  and on `bump package.json`
- **Then:** each run lists the matching node with the suffix
  `<- inferred from "<path>" via "<pattern>"`, where `<path>` is the task's
  path-like token after §6 normalization and echo sanitizing, and `<pattern>` is
  the matching piece as written
- **And:** `--plan "terraform plan output"` (no path-like token) infers nothing
- **And:** a file pattern is never a trigger phrase: a task that repeats the
  pattern's text as words does not promote the node
- **And:** `--plan "* */* [a-z]*/** ../../nowhere/x.tf /abs/y.tf"` infers the
  `*.tf` node only, from `../../nowhere/x.tf`, which exists nowhere, infers
  nothing from the other tokens, and exits 0: task text is never a pattern and
  no token touches the filesystem
- **And:** a task holding more than 64 path-like tokens, or a token over 256
  characters, exits 0, and an error inside inference prints the §6 notice line
  and falls back to the scored entries

### Contract: PLAN_PROMOTED_NODE_TAKES_ITS_CLOSURE
- **Test file:** `tests/test_graph_lint.py`
- **Given:** the fixture graph where a promoted or inferred expertise node
  `requires:` a parent expertise and `composes:` a child, and the task names one
  of the child's own `load_when` terms that is not a whole piece (for example
  `sink` from `log sink`)
- **When:** `--plan` promotes or infers the node
- **Then:** LOAD also lists the parent (by its `requires:` closure) and the
  child with `<- composed by <node> on "<term>"`
- **And:** a node that is both a scored entry and a phrase hit prints no suffix,
  and a node that is both promoted and inferred prints only the promotion
  suffix (§6 "Precedence")

### Reachability

### Contract: LISTED_NODE_EDGES_REACH
- **Test file:** `tests/test_graph_lint.py`
- **Given:** a rooted fixture graph whose `index.md` lists node `A`, which the
  root does not reach by any edge, and node `B` that no index row names and only
  `A`'s `peers:` points at
- **When:** graph-lint runs
- **Then:** no "unreachable" finding names `B`
- **And:** two nodes that peer each other, with neither listed in `index.md` nor
  reached from the root, are still each reported unreachable

### Effort

### Contract: AGENT_DECLARES_EFFORT
- **Test file:** `tests/test_agent_lint.py`
- **Given:** an agent directory
- **When:** `agent-lint.py --lint --dir <dir>` runs
- **Then:** an agent with no `effort:` key fails, naming the agent and the rule
- **And:** an agent whose `effort:` is outside the §6 closed set fails, naming
  the value (`xhigh`, which the host accepts, is refused)
- **And:** an agent carrying `origin: project` is held to the same rule
- **And:** the shipped roster in `agents/` passes, and each shipped agent's
  `effort:` equals its row in the §6 default table

### Seed method surface

### Contract: LEAF_BODY_CEILING_HELD
- **Test file:** `tests/test-seed-lint.sh` (check in `tests/seed-lint.py`)
- **Given:** the files under §6 "Leaf rule scope", `LEAF_BODY_CEILING` and the
  set `OVERSIZED_LEAVES` in `tests/seed-lint.py`, each mirrored in
  `tests/ratchets.json` with directions `max` and `set`
- **When:** seed-lint runs
- **Then:** a file whose body exceeds `LEAF_BODY_CEILING` lines, counted as the
  existing machinery check counts them, and that is not in `OVERSIZED_LEAVES`,
  is a finding naming the file, its line count and the ceiling
- **And:** a member of `OVERSIZED_LEAVES` whose body is at or below the ceiling
  is a finding (`stale oversized entry: remove it`), so the set only shrinks
- **And:** a member that is not a file in scope is a finding
- **And:** `tools/ratchet-lint.py` knows both keys, so raising the ceiling or
  adding a member fails it

### Contract: DELEGATION_SPLIT_INTO_SIBLINGS
- **Test file:** `tests/test-seed-lint.sh` (check in `tests/seed-lint.py`)
- **Given:** the six files of §6 "Delegation leaves"
- **When:** seed-lint runs
- **Then:** each file exists, and each of the thirteen fact keys the pre-split
  `core/method/delegation.md` owned is owned by exactly the file §6 names for it
- **And:** `REGISTRATION_HOME` is `core/method/delegation-bounds.md`, and the
  existing registration check passes against it
- **And:** `core/method/delegation.md` lists the other five sibling ids in its
  `peers:`, and its `## Neighbours` section names each of them
- (The v0.2 clause "no sibling is in `OVERSIZED_LEAVES`" is removed at ruling
  pass 1: `LEAF_BODY_CEILING_HELD` already holds it, since the ledger is derived
  before the split and adding a member fails `ratchet-lint`. The property is
  unchanged, so this is not a relaxation.)

### Contract: DELEGATION_LEAVES_ROUTE
- **Test file:** `tests/test_graph_lint.py`
- **Given:** the installed graph
- **When:** `--plan` runs on each sibling's representative phrase (§6
  "Delegation leaves", last column)
- **Then:** LOAD lists that sibling
- **And:** each representative phrase is, verbatim, one of that sibling's
  `load_when` entries

### Contract: ADOPTED_RULE_HOMES
- **Test file:** `tests/test-seed-lint.sh` (check in `tests/seed-lint.py`)
- **Given:** the §6 "Adopted rule homes" table
- **When:** seed-lint runs
- **Then:** each key in the table is in the `owns:` of exactly the file the
  table names, and of no other node
- **And:** no line of a file under `core/`, `agents/`, `protocols/`, `skills/`,
  `templates/`, `integrations/` or `documentation/`, or of `install.sh`,
  `README.md`, `INSTALL.md`, `DOCUMENTATION.md`, `CLAUDE.md` or a root
  `*_PROMPT.md`, names a path ending in `method/delegation.md` together with a
  `delegation.*` key that §6 homes in a different sibling, where the line is
  read joined with the line after it, so a pointer wrapped across two lines is
  one line. The finding names the file, the line and the sibling to point at
  (scope widened and wrap-joined at ruling pass 5)

### Templates

### Contract: HANDBACK_CARRIES_EFFORT_AND_EXPERTISE_GAP
- **Test file:** `tests/test-seed-lint.sh` (check in `tests/seed-lint.py`)
- **Given:** `templates/prompts/handback-payload.md`
- **When:** seed-lint reads its fenced `HANDBACK` block
- **Then:** the block has one line beginning `- effort:` and one beginning
  `- expertise_gap:`
- **And:** removing either line in a copy makes seed-lint exit 1 naming the field

### Contract: BOOTSTRAP_STEP2_LOADS_A_MENU
- **Test file:** `tests/test-seed-lint.sh` (check in `tests/seed-lint.py`)
- **Given:** the canonical `GRAPH DISCIPLINE` block in
  `templates/prompts/graph-session-bootstrap.md`
- **When:** seed-lint reads its step 2, from `2.` to the line before `3.`, with
  every run of whitespace collapsed to one space
- **Then:** it equals the §6 "Bootstrap step 2" text, collapsed the same way
- **And:** the existing identity check still holds the block byte for byte across
  the five embedding templates

### Contract: ADOPTED_RULES_NOT_PENDING
- **Test file:** `tests/test-seed-lint.sh` (check in `tests/seed-lint.py`)
- **Given:** every `.md` file under `core/`, `agents/`, `protocols/`, `skills/`,
  `templates/` and `integrations/`
- **When:** seed-lint reads each file with every run of whitespace collapsed to
  one space
- **Then:** none contains, case-insensitively, a phrase from §6 "Pending
  phrases"; a finding names the file and the phrase

## 5. Non-functional requirements

Global posture is the plan's §4; only what binds these checks is listed.

- **Verbatim move.** A split moves text; it does not rewrite it. At each split
  increment's gate (the delegation split and the three bloat-audit splits), every
  non-blank line of the pre-split body (at the batch base commit) occurs in
  exactly one resulting leaf, except the lines §6 marks as new (frontmatter,
  pointer lines). This is a one-time verify record, run from a scratch script
  against `git show`, and not a suite test: a standing test would freeze doctrine
  that later increments must edit.
- **Compatibility:** stdlib Python 3 only (`re`, `fnmatch`, `pathlib`);
  bash 3.2-compatible shell cases; no new dependency. The seed's minimum Python
  version is not recorded.
- **Determinism:** `--plan` output order stays sorted by id; promotion and
  inference pick the first hitting piece in `load_when` order and the first path
  in task order, so the suffix is stable.
- **Performance and robustness:** promotion adds one pass over expertise nodes'
  pieces per task; inference at most 64 tokens × the patterns, each token at most
  256 characters. `fnmatchcase` and the path regex ran linearly on 1 MB inputs
  (security review, Python 3.14.7). Inference never raises and never makes
  `--plan` exit non-zero, because the route hook treats a non-zero exit as a
  router failure. Target: no measurable change to `tests/run.sh`; observed at
  verify, not gated.
- **Canonical blocks:** the stemmer and stopword blocks that seed-lint holds
  byte-identical between `graph-lint.py` and `agent-lint.py` are not edited.
- **Eager surface:** no `description:` changes. `effort:` is one frontmatter
  line per agent; `FRONTMATTER_CEILING` (100) is not approached. The eager figure
  is re-measured by seed-lint at the tip.
- **Mirrors:** seed-lint holds `manifest.json` `protocols[]` and
  `documentation/protocols-reference.md` to the protocol files, and
  `documentation/skills-and-templates-reference.md` to skill frontmatter. Every
  increment that adds a protocol, or changes a protocol's or skill's mirrored
  frontmatter, updates those rows in its own file set.
- **Body figures:** the splits change the largest and median routable body that
  `DOCUMENTATION.md` publishes (SPEC-0004 `BODY_FIGURES_HAVE_A_REQUIRED_HOME`).
  The mirror increment updates them before the final tip.
- **Ratchets:** no limit widens. `LEAF_BODY_CEILING` and `OVERSIZED_LEAVES`
  start at their measured values; `KERNEL_BUDGET`, `EAGER_BUDGET` and
  `MACHINERY_BODY_CEILING` do not move.

## 6. Data shapes

### Design latitude (`specify.design-latitude`, home `protocols/specify-joint-pass.md`)

| Value | Means | Held how |
|---|---|---|
| `creative` | the design may propose new structure, concepts or scope, each surfaced as a decision | the press checks each proposal is recorded as a decision the owner can refuse |
| `balanced` | new structure where the change needs it; no new concepts the goal did not ask for | the press checks every new concept traces to the goal |
| `simple` | the smallest design that meets the goal; no new gates, kinds, agents or renamed concepts; when unsure whether something is in scope, it is not | the press and every ruling refuse anything outside the adopted scope and send it to the question file |

Asked once, by the session in joint-pass step 0 (or specify phase 0 when specify
runs alone; `protocols/specify.md` points here), in the owner's own words where
they give them. Recorded as a row of the plan's §6 (Decisions Made) whose first
cell begins `Design latitude:`, with the owner's quote or the session's recorded
reason as evidence and the date. Checked by judgment, not by a tool, at three
points: `grill.press`, each ruling pass, and the brief (which quotes the row).

### Effort labels and batch sizes (`delegation.effort-scale`)

Every §9 increment carries `Effort:` with one label and `Phase:` with one of
`RED`, `GREEN`, `prose`.

| Label | Typical shape |
|---|---|
| `low` | mechanical; one file; no judgment |
| `medium-low` | small; one surface; the approach is obvious |
| `medium` | one surface with some design inside the contract |
| `medium-hard` | several files, or a central abstraction |
| `hard` | cross-cutting, concurrency, security, or an approach not yet clear |

| Phase | Worker | low | medium-low | medium | medium-hard | hard |
|---|---|---|---|---|---|---|
| RED | `tester` | 7 or more (orchestrator's judgment) | 7 | 6 | 5 | 5 |
| GREEN | `implementer` | 5 | 3 | 3 | 2 | 1 |
| prose | one writer per disjoint file set | one set | one set | one set | one set | one set |

- A batch is sized by its hardest increment.
- Security and concurrency code is a GREEN batch of one, whatever its label.
- Dependent increments share a spawn only in dependency order, one commit each.
  A RED never shares a spawn with its own GREEN.
- The owner fixed the RED values for hard (5), medium (6), medium-low (7) and
  low (7 or more), and the GREEN values for low (5), medium (3), medium-hard (2)
  and hard (1). RED medium-hard (5) and GREEN medium-low (3) are the ruled
  reading of the two gaps: the smaller neighbour.

### Effort (`delegation.effort`, home `core/method/delegation-model-classes.md`)

Closed set for an agent definition's `effort:` key: `low`, `medium`, `high`.
Claude Code reads `effort` from subagent frontmatter with the values `low`,
`medium`, `high`, `xhigh` and `max`; it sets the effort for every spawn of that definition, and
when omitted the subagent inherits the session's (Claude Code sub-agents page,
https://code.claude.com/docs/en/sub-agents, retrieved 2026-09-26; available
levels depend on the model). The seed ships the three lower values only.
Whether that host offers a per-spawn override: not recorded. Whether opencode,
Codex or GitHub Copilot read the key: not recorded. No install transform drops
the key.

Default per agent definition (the step kind the agent mostly runs, from the
model-class table; `medium` where the table has no row):

| Agent | `effort:` | Step kind it mostly runs |
|---|---|---|
| `orchestrator` | high | routing and rulings on a contract's reading |
| `architect` | high | spec contracts, architecture, rulings, one-way doors |
| `multi-agent-architect` | high | architecture |
| `security` | high | any step on a security surface; threat models |
| `pentest` | high | any step on a security surface |
| `devils-advocate` | high | adversarial validation |
| `legal` | high | rulings against a rule corpus |
| `growth-orchestrator` | high | the close-out that ends a grow |
| `implementer` | medium | routine GREEN |
| `tester` | medium | RED for a new contract |
| `reviewer` | medium | standard batch review |
| `product` | medium | spec §3 and §9 |
| `ui-ux-designer` | medium | no table row |
| `data-ml` | medium | no table row |
| `reliability` | medium | no table row |
| `docs-librarian` | medium | the canonize librarian |
| `research-scout` | medium | library research |
| `growth-scout` | medium | artifact discovery (low to medium) |
| `tool-smith` | medium | no table row |
| `seed-installer` | medium | no table row |

Per-spawn derivation, first matching row wins:

| # | Condition | Spawn effort |
|---|---|---|
| 1 | a security surface (any trigger in `agent.security`'s "When to invoke" list; the brief names which); spec contracts, architecture, rulings, one-way doors, threat models, `devils-advocate`; a harvest's faithful-import review; diagnosing a red gate | high |
| 2 | a light variant (never on a security surface) | low |
| 3 | the spawn carries increments: the hardest label in the batch | low or medium-low → low; medium → medium; medium-hard or hard → high |
| 4 | no increment label: the model-class table's row for the step kind | that row's effort |
| 5 | otherwise | the agent definition's default |

Record: the brief's routing evidence carries one line
`effort: <value> (row <n>: <reason>)`. When the value differs from the agent
definition's default on a host with no recorded per-spawn setting, the line adds
`host applies: definition default <value>`, so the departure is visible. The
handback echoes the line in its `effort:` field.

Departures (fail closed): for rows 3 to 5, route to a definition carrying
the needed effort, or accept the recorded departure. For row 1 the departure is
never accepted: the step goes to a definition whose default is `high`, or its
output takes a review spawn at `high` before it lands (`security` for a security
surface, `architect` for a contract or ruling). A row-1 step with neither is a
block. ~~Host policy is in `integrations/claude-code/README.md`.~~ (corrected at
ruling pass 6: `install.sh` never places the integration READMEs, so a plant
could not reach the facts there.) The host facts a plant session needs (which
host reads `effort:`, its values, what is not recorded) live in
`core/method/delegation-model-classes.md`, which installs into every plant; the
Claude Code overlay README and `templates/agent.template.md` point at that leaf.

### Cycle-economy rules (home: `core/method/delegation-cycle-economy.md`)

| Key | Rule |
|---|---|
| `delegation.step-scope` | the "One step per spawn" section, moved verbatim, then amended: a step may be a batch of increments sized by the table above; overrun still stops and hands back |
| `delegation.effort-scale` | the two tables above |
| `delegation.green-self-test` | GREEN needs no separate tester spawn. The implementer runs the RED tests itself and never edits a test or fixture file. A test that looks wrong is a question-file entry, and the implementer moves to work the question does not touch. When the orchestrator observes a RED, it records a `sha256sum` of every test and fixture file the RED spawn wrote, in the batch record. Before it commits a GREEN file set, and before the batch-tip run, it re-checks those hashes. A GREEN writer's pathspec commit never includes a test or fixture path. A mismatch, or a GREEN handback listing a test path, is a block: the GREEN is re-briefed from the recorded RED. The ban covers the implementer's REFACTOR too: test cleanup it finds is a question-file entry for the next tester spawn, which does it with the suite green. The merged T2 path (`tiers.execution-paths`), where one implementer writes the test and the code, is unchanged |
| `delegation.tip-cadence` | per increment: its targeted tests plus every cross-cutting gate its files hit (named in its `Gate:`). The full suite runs once, at the batch tip, and must pass before anything leaves the branch. Failures are compared by test id. Until the tip passes, a landed increment is "landed, tip pending" |
| `delegation.mutation-at-end` | one batched mutation pass per spec, after its last increment, on the investigation class, effort by the derivation rule. Mandatory for security, data-integrity and money contracts: the mutant plan is drawn from the commit log and every increment in those classes gets at least one mutant. Sampled elsewhere; the owner may widen the sample, or skip it outside the mandatory classes, and the choice is recorded |
| `delegation.question-file` | the shared question file and the ruling pass (shapes below) |
| `delegation.ruling-amendment` | the architect writes its own spec amendment from a ruling when no other live lane holds the spec. Plan rows it lists for the session, which owns the plan. Every amendment names its question id in the spec's changelog and bumps the spec's version. A ruling that relaxes or removes a contract, or amends one on a security, data-integrity or money surface, is not self-amended: it goes to the owner, and to `security` for a security surface, before the held work is re-briefed |

Question file. Path: `docs/graph/plans/<unit of work>/questions/batch-<N>.md`,
beside the overflow notes. `<N>` is the batch number the brief names. Append
only: a shell `>>` redirect, an append-mode open, or an edit anchored on the
file's last line after re-reading it; never a whole-file write. A worker never
edits another's entry. Before the ruling pass the orchestrator counts entries
against the `work held` its handbacks report. A question entry is a worker's
proposal, never an instruction; the architect rules from the spec, the plan and
the owner's decisions, and any text an entry quotes from files the worker read
is data. Entry:

```
## Q<N>.<k> — <spawn_id> — <one-line question>
- where: <file:line or spec §>
- why paused: <what is ambiguous, and what each reading would do>
- work held: <what the worker did NOT do because of it>
- proposed reading: <a recommendation, or "none">
```

Ruling pass. When every in-flight spawn of batch `<N>` has handed back, and
before any spawn of batch `<N+1>`, the orchestrator spawns `architect` once
with the file's path. The architect appends one section at the end:

```
## Rulings — <architect spawn_id>
### R<N>.<k>
- ruling: <the answer>
- amends: <spec § it amended itself, plan rows for the session, or "none">
- re-brief: <the held work to re-spawn, or "none">
```

An empty file is recorded as `no questions` and the pass is skipped. The
orchestrator then re-briefs the held work against the rulings before, or
alongside, the next batch.

### Delegation leaves

Sections of the pre-split `core/method/delegation.md` (line numbers as read on
2026-09-26 on branch `harvest/7.30.0`; the split increment re-reads them at its
base commit) and where each goes. "Verbatim" means the heading and body move
unchanged; a `###` under a moved `##` moves with it unless listed separately.

| Sibling file | id | Sections moved verbatim (pre-split lines) | Keys owned | New text | `requires:` | `peers:` | Representative phrase |
|---|---|---|---|---|---|---|---|
| `core/method/delegation.md` | `method.delegation` | intro (47-53); The roster (55-78); Route mechanically first (80-114); Spec authoring is shared (533-537) | `delegation.roster`, `delegation.routing`, `delegation.spec-authoring` | the `## Neighbours` section lists the five siblings, each `- \`<id>\`: load when <text>`, and `method.tiers` as now | none | the five siblings, `method.tiers` | "who should do this, which specialist, which agent" |
| `core/method/delegation-model-classes.md` | `method.delegation-model-classes` | Route by model class (116-162); Light variants (164-211) | `delegation.model-classes`, `delegation.light-variants`, `delegation.effort` | the `delegation.effort` section (§6 "Effort"); the adopted rewording of 121-123 and 166-167; the `engineering-posture §5` pointer repointed to `method.minimum-sufficient-work` (later increments) | none | `method.delegation`, `method.delegation-cycle-economy` | "sonnet or opus, which model class" |
| `core/method/delegation-cycle-economy.md` | `method.delegation-cycle-economy` | One step per spawn (430-447) | `delegation.step-scope`, `delegation.effort-scale`, `delegation.green-self-test`, `delegation.tip-cadence`, `delegation.mutation-at-end`, `delegation.question-file`, `delegation.ruling-amendment` | every row of §6 "Cycle-economy rules" except the moved section | none | `method.delegation-model-classes`, `method.delegation-sequencing` | "how many increments per spawn, batch size" |
| `core/method/delegation-briefs.md` | `method.delegation-briefs` | Every brief carries the graph discipline (341-429, without its `### One step per spawn`) | `delegation.briefs` | none | none | `method.delegation`, `method.delegation-cycle-economy` | "spawn a worker, write a delegation brief" |
| `core/method/delegation-sequencing.md` | `method.delegation-sequencing` | Spawns are sequenced by dependency (449-486); Lanes (488-510) | `delegation.sequencing`, `delegation.lanes` | none | none | `method.delegation`, `method.delegation-cycle-economy` | "spawn order, parallel or sequential, which spawn waits for which" |
| `core/method/delegation-bounds.md` | `method.delegation-bounds` | Delegation is bounded (213-237); A specialist is spawnable only once the host registered it (239-307); What a "turn" is (309-339); Every spawn is traced (512-531) | `delegation.bounds`, `delegation.harness-registration`, `delegation.turn`, `delegation.tracing` | none | none | `method.delegation`, `method.delegation-briefs` | "delegation depth, allowlist, can this agent spawn" |

Frontmatter per sibling: `id`, `tier: 2`, `kind: method`, `origin: seed`,
`title`, `owns`, `requires`, `peers`, `artifacts` (`method.delegation-briefs`
takes `graph-session-bootstrap.md` and `handback-payload.md`;
`method.delegation-model-classes` takes `agent.template.md`), `load_when`,
`prevents` (one per sibling, written so `PREVENTS_OVERLAP_CEILING` holds), and a
measured `est_tokens`.

`load_when` per sibling: the pre-split entries go to the sibling that owns their
subject (the roster and routing entries to `method.delegation`; "sonnet or opus"
and "reasoning effort, … light variant …" to model classes; "spawn a worker…" and
"shared rules file…" to briefs; "spawn order…" and "one writer per file set…" to
sequencing; "delegation depth…", "a spawn went silent…", "unknown agent type…"
and "the roster was just installed…" to bounds). New entries, one topic each:
model classes adds "effort for this spawn, effort field in the agent
definition"; cycle economy carries "how many increments per spawn, batch size",
"run the full suite once at the batch tip, landed tip pending", "shared question
file, architect ruling pass at the batch boundary", "mutation pass at the end
of the spec" and "the implementer runs the tests and must not edit them". The
writer may add entries; the representative phrase stays verbatim.

Router index (`templates/knowledge-graph/index.md`): the one delegation row keeps
its question and lists all six ids, the way the posture row lists its nodes.

### Leaf splits from the bloat audit (ruled at ruling pass 0)

Each split moves sections verbatim; the retained leaf keeps its id; each fact key
moves with the section that states it (the writer lists the mapping in its
handback); every new leaf is a sibling cross-linked by `peers:`, never a child.

| Split | From | New leaf (file, id) | Sections moved | Keys that move |
|---|---|---|---|---|
| engineering posture | `core/method/engineering-posture.md` | `core/method/minimum-sufficient-work.md`, `method.minimum-sufficient-work` | §5 | `engineering-posture.minimum-sufficient-work` |
| engineering posture | same | `core/method/decision-economy.md`, `method.decision-economy` | §6, §7 | `engineering-posture.decision-economy` |
| engineering posture | same | `core/method/host-parity.md`, `method.host-parity` | §13 | `engineering-posture.host-parity` |
| engineering posture | same | `core/method/bounded-execution.md`, `method.bounded-execution` | §14 | `toolcraft.bounded-execution` |
| design posture | `core/method/design-posture.md` | `core/method/restrictive-policy.md`, `method.restrictive-policy` | §8 | `design-posture.restrictive-policy` |
| design posture | same | `core/method/maintenance-contracts.md`, `method.maintenance-contracts` | §12, §13 | `design-posture.generated-artifacts`, `design-posture.doc-code-precedence` |
| design posture | same | `core/method/design-governance.md`, `method.design-governance` | §14, §15 | `design-posture.project-contract-outranks`, `design-posture.maintained-primitives` |
| verify | `protocols/verify.md` | `protocols/verify-new-gates.md`, `protocol.verify-new-gates` | "`closed` means evidenced"; "Adding a new gate" | the keys those sections state; `rule.verify` stays |
| verify | same | `protocols/verify-disagreement.md`, `protocol.verify-disagreement` | "Behavior-preserving changes"; "Tolerating a known defect"; "When the check and its subject disagree" | the keys those sections state |
| humanizer | `skills/humanizer/SKILL.md` | none: kept whole | — | — |
| lifecycle protocols | graft, grow, harvest | none this round: held (adr-0007) | — | — |

Section-number pointers into moved sections (for example `engineering-posture.md
§5–§8` in the embedded block's step 5, `design-posture` §14, `method.engineering-posture`
§5 in the model-class leaf) are repointed by id in the same round. A retained
leaf keeps its section numbers; moved sections keep theirs, verbatim.

### Adopted rule homes

Checked by `ADOPTED_RULE_HOMES`. The thirteen pre-split delegation keys are held
by `DELEGATION_SPLIT_INTO_SIBLINGS` instead and are not repeated here.

| Key | File | Rule |
|---|---|---|
| `delegation.effort` | `core/method/delegation-model-classes.md` | §6 "Effort" |
| `delegation.effort-scale` | `core/method/delegation-cycle-economy.md` | §6 "Effort labels and batch sizes" |
| `delegation.green-self-test` | `core/method/delegation-cycle-economy.md` | GREEN runs its own tests and edits none; the RED hash re-check |
| `delegation.tip-cadence` | `core/method/delegation-cycle-economy.md` | targeted tests per increment; the full suite once at the batch tip |
| `delegation.mutation-at-end` | `core/method/delegation-cycle-economy.md` | one mutation pass per spec; the mandatory classes |
| `delegation.question-file` | `core/method/delegation-cycle-economy.md` | the shared question file and the batch ruling pass |
| `delegation.ruling-amendment` | `core/method/delegation-cycle-economy.md` | the architect writes its own amendment, within limits |
| `specify.design-latitude` | `protocols/specify-joint-pass.md` | the design-latitude guard |
| `specify.joint-pass` | `protocols/specify-joint-pass.md` | the joint specify and grill pass |
| `engineering-posture.no-write-inspection` | `core/method/host-parity.md` | inspection never writes; a loop re-checks what a failure protected |
| `context-router.menu` | `skills/context-router/SKILL.md` | the menu rule |
| `context-router.graph-over-harness` | `skills/context-router/SKILL.md` | graph doctrine outranks a harness's default style |
| `knowledge-graph.branch-shape` | `skills/knowledge-graph/SKILL.md` | the leaf rule, the branch shape and the link-farm reconciliation |
| `test-first.no-lint-only-tests` | `skills/test-first/SKILL.md` | no test that asserts nothing new to turn a lint green |

Homes with no new key, reviewed rather than checked:
- The works-claim rule sharpens `engineering-posture.host-parity` ("Validate
  where it runs", in `method.host-parity` after the engineering-posture split):
  a claim that something works needs the execution target or real CI; a local
  reproduction is allowed for diagnosis only.
- Light variants: the rewording of `delegation.light-variants` to adopted.
- The mandatory stack-expertise step and mid-work discovery live in the
  bootstrap template's "Stack expertise" companion, which is its one home and is
  not a node.
- `protocols/specify.md` phase 0 and `grill.flow` point at the joint-pass leaf;
  `grill.press` points at the latitude check; test-first, verify and recover get
  pointer lines to the cycle-economy keys.

### Joint specify and grill pass (`specify.joint-pass`, home `protocols/specify-joint-pass.md`)

| Step | Owner | Writes | Needs | Parallel with |
|---|---|---|---|---|
| 0 | session | the design-latitude ask; spec §0 to §2; plan §0, §2 to §4, §1 | — | `research-scout` for missing library pages (plan §5) |
| 1 | `product` | spec §3 | 0 | the scouts |
| 2 | `architect` | spec §4 to §8; plan §5 synthesis, §6 to §9 with effort labels, phases and the batch plan | 1, the scouts | — |
| 3 | `product` (spec §9) ∥ `tester` (spec §10 rows, testability; plan §10) ∥ `security` where the surface is sensitive (spec §5, §7; plan §11) ∥ `reliability` (plan §11) | as named | 2 | each other |
| 4 | `devils-advocate` for one-way doors and the top risk | beside the plan's §6 and §11 | 3 | — |
| 5 | session | spec §11, §12 and sign-offs; plan §12 to §15 | 4 | — |

Section ownership does not change. A testability failure in step 3 returns to
the architect as a `protocol.recover` attempt, as today. The separate phase
tables in `specify.flow` and `grill.flow` still apply when only one document is
being written. The leaf carries no `command:` key.

### Trigger phrase and file pattern

A `load_when` entry is split on commas into pieces, each stripped of surrounding
whitespace.

- **File pattern:** a piece with no whitespace that contains `*` or `/`.
  A pattern carries at least one literal character besides `*`, `?` and `/`;
  a pattern like `**/*` matches every path and floods every task that names one
  (doctrine in `_schema.md`, no lint). Brace expansion is not supported:
  `*.{ts,tsx}` splits at the comma into `*.{ts` (a pattern that matches nothing)
  and `tsx}` (a one-token trigger phrase that promotes on any task naming a
  `.tsx` path). Write one pattern per piece. A manifest or lockfile is written as
  a pattern, for example `**/package.json`.
- **Trigger phrase:** any other piece. Its tokens are the router's whole tokens
  of the lowercased piece (`_split_terms(piece)[0]`): runs of `[a-z0-9_/*.-]`,
  stripped of `_`, of length 3 or more, not in `STOPWORDS`. A dotted or
  hyphenated word stays one token, so `net10.0` and `supply-chain` are each a
  single token and a task must name the whole of it (v0.5 split them into
  `[a-z0-9_]` runs, so `target net10` promoted a node whose piece was
  `net10.0`). A piece with no tokens is ignored.
- **Hit:** every token of the phrase matches a term of the task
  (`_terms(task)`) at strength 2 of `_match` (exact, or the same stem). A
  prefix fold (strength 1) does not count.
- Only `kind: expertise` nodes are promoted or inferred.

### Path-like token and pattern match

- The task is split on whitespace. A token longer than 256 characters is
  skipped first and does not count. Of the rest, at most the first 64 path-like
  tokens are considered.
- Each token is stripped of leading and trailing `` ` `` `'` `"` `(` `)` `[` `]`
  `<` `>` `,` `;` `:`, and of trailing `.`, repeating until nothing more
  strips, so `(infra/main.tf).` becomes `infra/main.tf`.
- A token containing `://` is skipped.
- A token is path-like if it contains `/`, or if it matches
  `^[A-Za-z0-9_.-]*\.[A-Za-z0-9]{1,10}$`.
- Normalization: lowercase; `\` becomes `/`; one leading `./` is removed. The
  path-like test above runs before normalization, on the stripped token, so a
  backslash-only token such as `infra\main.tf` is not path-like and infers
  nothing.
- Match: the task token is always the name and the `load_when` piece always the
  pattern, `fnmatch.fnmatchcase(path, pattern.lower())`. Task text is never
  compiled as a pattern or a regular expression. No token is resolved, joined to
  the graph root, stat'ed or opened: inference is string matching only, and a
  path that does not exist infers exactly as one that does.
  - a pattern with no `/` matches the path's last segment;
  - a pattern with `/` has every leading `**/` removed, giving `p`, and matches
    when the path matches `p` or `*/` + `p`.
- `fnmatch`'s `*` crosses `/`, so `src/*.ts` also matches `src/a/b.ts`. That is
  accepted and documented, not corrected.
- An extensionless bare name (`Dockerfile`) is path-like only when written with
  a directory (`docker/Dockerfile`, `./Dockerfile`).
- Promotion and inference never raise on any `str` task. An unexpected error in
  them drops back to the scored entries alone, prints one notice line
  `  ! inference skipped: <exception class>` before `LOAD`, and exits 0.

### Precedence and output

- Promotion and inference add entries before the traversal, beside the scored
  entries. The scored entries keep the existing cut (top three, above the floor).
  Promoted and inferred entries are not counted against it, and all of them load.
- The LOAD line's suffix, first matching rule:
  1. a scored entry: no suffix (as today);
  2. a phrase hit: `   <- promoted on "<piece as written>"`, the first hitting
     piece in `load_when` order;
  3. a path match: `   <- inferred from "<path>" via "<pattern as written>"`, the
     first path in task order, then the first pattern in `load_when` order.
- The echoed `<path>` is the normalized token cut to its first 80 characters,
  with `…` appended when cut, and every character outside `[a-z0-9_./~+-]` shown
  as `?`.
- `requires:` and composition descent run from promoted and inferred entries as
  from any entry. A node that is an entry never prints `composed by`.
- `NOT LOADED` never lists a node that loaded.

Example, fixture graph:

```
LOAD (4 nodes, ~T tokens):
  expertise.pipelines          pipelines — when pipeline expertise is in play   <- promoted on "pipeline yaml"
  expertise.terraform          terraform — when terraform is in play   <- inferred from "infra/main.tf" via "*.tf"
  ...
```

### Branch shape and the leaf rule (`knowledge-graph.branch-shape`)

Doctrine, judged by review; no lint checks it (the check was withdrawn at ruling
pass 0).

- **Leaf rule.** A leaf holds one topic, sized to what a typical task loads. A
  leaf whose separable topics are loaded independently divides into sibling
  leaves. Protocols, postures and the delegation files are leaves.
- **Branch.** A branch node (the router index, a hub, a subsystem or domain
  node, or a new thin parent) is a menu: a `## Leaves` section listing each leaf
  as `` - `<node id or graph-relative path>`: load when <text> ``, plus only the
  doctrine that binds every leaf and cannot live in one.
- **Link farm, reconciled.** A branch owns its menu, meaning which leaf answers
  which need; its fact key is `<slug>.menu`. A link farm is a list without that
  routing information, and it is still deleted. This applies to branch nodes
  only.

### Leaf rule scope and the ratchet

- Scope: `core/method/*.md`, `protocols/*.md`, `skills/*/SKILL.md`. Agents are
  out of scope (their bodies are system prompts).
- `LEAF_BODY_CEILING = 170`, direction `max`: graph-lint's project-node line.
- `OVERSIZED_LEAVES`, direction `set`: every in-scope file over the ceiling when
  the check lands, derived by the check's own count at that commit and never
  counted by hand, and never re-derived to fit new text. Members include the
  three lifecycle protocols, which `LIFECYCLE_BODY_CEILING` still bounds (§11).
  The set freezes membership, not size.
- The existing `MACHINERY_BODY_CEILING` and `LIFECYCLE_BODY_CEILING` stay in force
  for every member.

### Finding fragments

| Contract | Fragment a planted case greps |
|---|---|
| LEAF_BODY_CEILING_HELD | `over the 170-line leaf ceiling`; `stale oversized entry: remove it`; `not a file in the leaf scope` |
| DELEGATION_SPLIT_INTO_SIBLINGS | the sibling's path or the key, and `delegation split` |
| ADOPTED_RULE_HOMES | `owned by more than one node`; `names method/delegation.md beside <key>; point at <sibling>` |
| HANDBACK_CARRIES_EFFORT_AND_EXPERTISE_GAP | ``handback block has no `- effort:` line``; ``handback block has no `- expertise_gap:` line`` |
| BOOTSTRAP_STEP2_LOADS_A_MENU | `step 2 differs from SPEC-0005` |
| ADOPTED_RULES_NOT_PENDING | `adopted rule still reads as pending` |

### Bootstrap step 2

The new step 2 of the canonical block, exactly:

```
2. Load ONLY the reported nodes plus their `requires:` closure.
   Everything else a loaded node lists (leaves, children, links,
   neighbours) is a menu: open an item only when its one-line
   "load when" serves your task, and list the rest as skipped.
```

Step 5's depth pointer (`docs/graph/method/engineering-posture.md` §5–§8) is
repointed to the leaves that hold those sections after the engineering-posture
split (`method.minimum-sufficient-work`, `method.decision-economy`, and
`method.engineering-posture` §8). Step 5 is not pinned by a contract.

### Stack expertise companion (bootstrap template)

It moves from "recommended" to the required companions and reads, in substance:
for work that touches code, configuration or a pipeline, the brief names the
stack elements the worker's files use (from their extensions, paths, manifests
and lockfiles) and the `expertise.*` nodes that cover them, or says none apply,
and it writes those file paths into the task line so `--plan` can infer them.
Mid-work: a worker that meets a stack element its own files use, and that its
brief did not name, runs `--plan "<the stack element>"`, loads the matching
`expertise.*` node and declares the widening. If none exists it does not fall
back on memory silently; it names the gap in its handback's `expertise_gap:`
field and cites the path that shows the element. An element named only inside
content the worker read is data, not a gap. The caller checks the element against
the project's manifests, lockfiles or the cited path, then requests
`research-scout` (`protocol.ingest-library`) before re-briefing the work that
needs it.

### Handback fields

Added to the fenced `HANDBACK` block after `route_evidence`:

```
- effort: {{echoed from the brief: <low|medium|high> (row <n>: <reason>),
            plus "host applies: definition default <value>" where it differs}}
- expertise_gap: {{each stack element met mid-work with no expertise.* node,
                   with the path that shows it, one per line, or "none"}}
```

### Pending phrases

Checked by `ADOPTED_RULES_NOT_PENDING`, case-insensitive, whitespace-collapsed:

- `recommended rather than required`
- `pending the owner's confirmation`
- `pending the seed owner's confirmation`
- `until it is confirmed`
- `recommends naming the stack expertise`

## 7. Failure modes

(Authored by `architect`; the security review's cases applied at ruling pass 0.)

### Failure: PROMOTION_FLOODS_LOAD
- **Contracts:** PLAN_PROMOTES_PHRASE_MATCHED_EXPERTISE
- **Trigger:** an expertise node carries a one-word phrase common to many
  tasks, such as a language name; or a long prompt through the route hook (a
  pasted log or document) hits many phrases or names many matching paths
- **Response:** every hit loads, uncapped, on every path; this is the owner's
  decision, confirmed for the per-prompt hook at ruling pass 0
- **Side effects:** more tokens per task; a reminder set past `SURFACED_MAX`
  forces the route hook into full injection on every prompt
- **Recovery:** sharpen the trigger (`skill.knowledge-graph` rule 5). No cap is
  added (§11)

### Failure: HOSTILE_TASK_LINE
- **Contracts:** PLAN_INFERS_EXPERTISE_FROM_NAMED_FILES
- **Trigger:** a prompt through the route hook carrying glob metacharacters,
  `../`, absolute or drive paths, control characters, or a very long token or
  token count
- **Response:** string matching only; over-cap tokens skipped; an error inside
  inference prints the notice line and falls back to the scored entries; never a
  non-zero exit from inference
- **Side effects:** at most a mis-rank
- **Recovery:** none needed. The route hook's fail-open path stays for real
  router failures only

### Failure: DESCENT_TEST_NOW_SEEDS_THE_CHILD
- **Contracts:** PLAN_PROMOTES_PHRASE_MATCHED_EXPERTISE, PLAN_PROMOTED_NODE_TAKES_ITS_CLOSURE
- **Trigger:** an existing `DescentTests` case assumes the unmodified tool did
  not seed a child, and the child now promotes on a whole piece the task names
  (measured: `dbcontext`, `net10.0`, `retry policy`)
- **Response:** the case's provenance assertion changes (`promoted on` instead of
  `composed by`)
- **Side effects:** four red existing tests if left to GREEN
- **Recovery:** ruled at ruling pass 0: the tester reshapes the four cases at
  RED, each still asserting the child or major it selected, either by a task
  term that is not a whole piece or by a `promoted on` assertion. The
  implementer never edits them

### Failure: PATTERN_BRACE_SPLIT
- **Contracts:** PLAN_INFERS_EXPERTISE_FROM_NAMED_FILES
- **Trigger:** a `load_when` piece written as `*.{ts,tsx}`
- **Response:** the head piece `*.{ts` matches nothing; the tail piece `tsx}` is
  a one-token trigger phrase that promotes the node on any task naming a `.tsx`
  path
- **Side effects:** an unintended promotion; no error
- **Recovery:** write one pattern per piece (§6); `_schema.md` says so

### Failure: EXTENSIONLESS_BARE_NAME
- **Contracts:** PLAN_INFERS_EXPERTISE_FROM_NAMED_FILES
- **Trigger:** a task names `Dockerfile` or `Makefile` with no directory
- **Response:** not path-like, so no inference; its words still score as words
- **Side effects:** none
- **Recovery:** the brief writes the path (`./Dockerfile`)

### Failure: TASK_LINE_WITHOUT_PATHS
- **Contracts:** PLAN_INFERS_EXPERTISE_FROM_NAMED_FILES
- **Trigger:** a code brief's task line names no file
- **Response:** nothing is inferred
- **Side effects:** the worker loads only what the words route to
- **Recovery:** the mandatory stack-expertise companion requires the brief to
  name the elements and write the paths; mid-work discovery is the backstop

### Failure: SIBLING_UNREACHABLE_AFTER_GRAFT
- **Contracts:** LISTED_NODE_EDGES_REACH
- **Trigger:** a grown plant's own `index.md` lists `method.delegation` but not
  the new siblings (`index.md` stays plant-owned under graft)
- **Response:** the siblings are reached through `method.delegation`'s `peers:`
- **Side effects:** none
- **Recovery:** not needed; without this contract every grafted plant would fail
  graph-lint on five unreachable nodes

### Failure: ORPHAN_ISLAND
- **Contracts:** LISTED_NODE_EDGES_REACH
- **Trigger:** two nodes peer each other and neither is listed or reached
- **Response:** both are still reported unreachable
- **Side effects:** none
- **Recovery:** list one, or remove them

### Failure: AGENT_WITHOUT_EFFORT_AFTER_GRAFT
- **Contracts:** AGENT_DECLARES_EFFORT
- **Trigger:** a plant's own agent definition, authored before this release,
  has no `effort:` and the grafted `agent-lint.py` requires one
- **Response:** `agent-lint --lint` exits 1 naming the agent
- **Side effects:** the plant's agent-lint step is red until the line is added
- **Recovery:** add the line; graft reports it

### Failure: HOST_REJECTS_EFFORT_KEY
- **Contracts:** AGENT_DECLARES_EFFORT
- **Trigger:** a host other than Claude Code rejects or warns on an unknown
  frontmatter key in a projected agent
- **Response:** not recorded; the fresh-install gate runs every host adapter at
  the tip, and `tests/test-full-install.sh` lints the projections
- **Side effects:** a failed or noisy install on that host
- **Recovery:** a question, not a silent drop: no transform drops the key,
  because the projection lint would then fail the rule

### Failure: EFFORT_NOT_APPLIED_PER_SPAWN
- **Contracts:** AGENT_DECLARES_EFFORT, HANDBACK_CARRIES_EFFORT_AND_EXPERTISE_GAP
- **Trigger:** the derived effort differs from the agent's default, and the host
  has no recorded per-spawn setting
- **Response:** the brief records `host applies: definition default <value>`
- **Side effects:** the spawn runs at the definition's effort
- **Recovery:** rows 3 to 5: route to a definition carrying the needed effort (a
  light variant for low), or accept the recorded departure. Row 1 fails closed:
  a `high` definition, or a `high` review spawn before the output lands, else a
  block

### Failure: LEDGER_REGROWS
- **Contracts:** LEAF_BODY_CEILING_HELD
- **Trigger:** a writer adds a member to `OVERSIZED_LEAVES` or raises
  `LEAF_BODY_CEILING` to fit new text
- **Response:** `ratchet-lint.py` fails naming the key
- **Side effects:** none
- **Recovery:** split the leaf, or the owner raises the limit on record

### Failure: SIBLING_OVER_CEILING
- **Contracts:** LEAF_BODY_CEILING_HELD, DELEGATION_SPLIT_INTO_SIBLINGS
- **Trigger:** prose pushes a non-member leaf past 170 body lines (a sibling, or
  `protocols/specify.md`, which sits at 162)
- **Response:** seed-lint fails naming the file
- **Side effects:** the prose increment cannot land
- **Recovery:** the writer stops and writes a question; the ruling divides the
  topic further. The text is never shortened to fit, and the ledger is never
  re-derived to fit

### Failure: VERBATIM_DRIFT
- **Contracts:** DELEGATION_SPLIT_INTO_SIBLINGS
- **Trigger:** a split rewords, drops or duplicates a moved line
- **Response:** the one-time verbatim record at the split's gate lists the line
- **Side effects:** none once caught
- **Recovery:** restore the line in the one leaf that owns it

### Failure: STALE_POINTER
- **Contracts:** ADOPTED_RULE_HOMES
- **Trigger:** a shipped line still names `method/delegation.md` beside a key
  that moved to a sibling
- **Response:** seed-lint names the file, line and sibling
- **Side effects:** none
- **Recovery:** repoint the line. A pointer that names only a moved heading or a
  section number, with no key, is not caught and is repointed by the round's
  pointer increments and checked by review

### Failure: TEMPLATE_CHANGE_UNDER_SPEC_0003
- **Contracts:** BOOTSTRAP_STEP2_LOADS_A_MENU, HANDBACK_CARRIES_EFFORT_AND_EXPERTISE_GAP
- **Trigger:** SPEC-0003's `BRIEF_TEMPLATES_BYTE_IDENTICAL` compares both templates
  with its 7.27.0 baseline at verify
- **Response:** that verify command reports a difference. Whether it already did
  after this harvest's first round, which edited both templates' companion and
  rules text, is not checked here
- **Side effects:** a live contract of another spec reads red if re-run
- **Recovery:** held for the owner; this spec does not edit SPEC-0003

### Failure: RULING_RELAXES_A_CONTRACT
- **Contracts:** none (doctrine; fail closed at the ruling pass)
- **Trigger:** a worker blocked by a RED writes a question, and a ruling would
  relax or remove a contract, or amend one on a security, data-integrity or money
  surface
- **Response:** the architect does not self-amend; the ruling goes to the owner
  (and `security` for a security surface) before re-brief
- **Side effects:** the held work waits
- **Recovery:** the owner decides; the amendment names its question id and bumps
  the version

### Failure: CONTENT_STEERED_GAP
- **Contracts:** HANDBACK_CARRIES_EFFORT_AND_EXPERTISE_GAP
- **Trigger:** a file the worker read names a stack element the project does not
  use, and the worker reports it as a gap
- **Response:** the gap carries no path in the worker's own files, so the caller
  does not request `research-scout`
- **Side effects:** none
- **Recovery:** none needed; `protocol.ingest-library` still gates any dependency

### Failure: QUESTION_ENTRY_LOST
- **Contracts:** none (doctrine; detective)
- **Trigger:** a whole-file write to the shared question file drops another
  worker's entry
- **Response:** the orchestrator's count of entries against reported `work held`
  disagrees before the ruling pass
- **Side effects:** held work is not ruled on
- **Recovery:** recover the entry from the handback that reported it

### Failure: WORKER_GUESSES
- **Contracts:** none (doctrine; detective)
- **Trigger:** a worker resolves an ambiguity by guessing instead of writing a
  question
- **Response:** the reviewer or the ruling pass finds a reading nobody ruled on
- **Side effects:** rework
- **Recovery:** the guessed work is re-briefed after a ruling

### Failure: RULING_PASS_SKIPPED
- **Contracts:** none (doctrine; detective)
- **Trigger:** the next batch is dispatched while questions from the last one
  have no ruling
- **Response:** held work is re-briefed late or not at all
- **Side effects:** the next batch builds on unruled readings
- **Recovery:** the plan's batch table names each ruling pass; `grill.revise`
  records it in §15

### Failure: IMPLEMENTER_EDITS_A_TEST
- **Contracts:** none (doctrine; preventive at the commit boundary)
- **Trigger:** a GREEN diff touches a test or fixture file
- **Response:** the RED hash re-check blocks the commit and the tip
- **Side effects:** the RED no longer proves what it proved
- **Recovery:** the GREEN is re-briefed from the recorded RED; the question goes
  to the file

## 8. Examples

```text
# Happy: promotion past the budget (PLAN_PROMOTES_PHRASE_MATCHED_EXPERTISE)
$ python3 graph-lint.py --plan "pipeline yaml"
LOAD (4 nodes, ~T tokens):
  expertise.pipelines          pipelines — when pipeline expertise is in play   <- promoted on "pipeline yaml"
  subsystem.a                  ...
  subsystem.b                  ...
  subsystem.c                  ...
```

```text
# Happy: inference from a named lockfile (PLAN_INFERS_EXPERTISE_FROM_NAMED_FILES)
$ python3 graph-lint.py --plan "bump web/package-lock.json"
  expertise.node-js            node-js — when node is in play   <- inferred from "web/package-lock.json" via "**/package-lock.json"
```

```text
# Edge: no path-like token, nothing inferred
$ python3 graph-lint.py --plan "terraform plan output"
(no line carries "inferred from")
```

```text
# Adversarial: task text is never a pattern
$ python3 graph-lint.py --plan "* */* [a-z]*/** ../../nowhere/x.tf /abs/y.tf"
  expertise.terraform          ...   <- inferred from "../../nowhere/x.tf" via "*.tf"
(exit 0; no other inferred line)
```

```yaml
# Happy: an agent definition with its default effort (AGENT_DECLARES_EFFORT)
name: implementer
model: opus
effort: medium
```

```text
# Happy: a brief's effort line and the handback echo
route_evidence: agent-lint --route "..." -> implementer HIGH
effort: medium (row 3: hardest label medium)
...
HANDBACK
- effort: medium (row 3: hardest label medium)
- expertise_gap: none
```

```text
# Failure: a row-1 departure
effort: high (row 1: security surface, prompt construction), host applies: definition default medium
-> not accepted: route to a high definition, or add a security review at high before landing
```

```markdown
<!-- A question-file entry and its ruling (delegation.question-file) -->
## Q2.1 — <tester spawn_id> — does the ledger count the frontmatter?
- where: SPEC-0005 §6 "Leaf rule scope and the ratchet"
- why paused: "body" could include frontmatter; the two readings seed different members
- work held: the OVERSIZED_LEAVES initial set
- proposed reading: body only, as the machinery check counts it

## Rulings — <architect spawn_id>
### R2.1
- ruling: body only, as the machinery check counts it
- amends: none
- re-brief: the tester's held set
```

## 9. Acceptance criteria

(Drafted by `architect`, revised by `product` at ruling pass 0; `product` signs.
Every criterion ends with one `Contracts:` line. A mechanical criterion's line
maps to §4 slugs and nothing else in capitals; a detective criterion's line says
who judges it.)

### Routing

- [ ] **AC-1.** A task whose words include every word of one of an expertise
      node's trigger phrases loads that node, even when three other nodes
      outscore it, and the output names the phrase. A task naming only part of a
      two-word phrase does not. A non-expertise node is never promoted. A task
      with no phrase hit and no path loads exactly what it loaded before.
      Contracts: maps to PLAN_PROMOTES_PHRASE_MATCHED_EXPERTISE
- [ ] **AC-2.** A task that names a file by path, extension, manifest or lockfile
      loads the expertise node whose file patterns match it, and the output says
      which path and pattern. A task with no path loads no inferred node.
      Repeating a pattern's text as words does not promote the node. Glob
      characters, `../` and absolute paths in the task never widen a match and
      never make the router fail.
      Contracts: maps to PLAN_INFERS_EXPERTISE_FROM_NAMED_FILES
- [ ] **AC-3.** A promoted or inferred node brings its required parent and the
      composed child the task names.
      Contracts: maps to PLAN_PROMOTED_NODE_TAKES_ITS_CLOSURE
- [ ] **AC-4.** Each delegation sibling loads on its own representative phrase.
      Contracts: maps to DELEGATION_LEAVES_ROUTE

### Structure

- [ ] **AC-5.** Withdrawn at ruling pass 0: the branch shape is doctrine,
      judged by review under AC-18.
      Contracts: none; withdrawn.
- [ ] **AC-6.** A graph whose index lists `method.delegation` but none of its
      siblings reports none of the siblings unreachable. Two nodes that reach
      only each other are still reported unreachable.
      Contracts: maps to LISTED_NODE_EDGES_REACH
- [ ] **AC-7.** The seed cannot gain a new oversized method-surface leaf, and the
      list of existing ones can only shrink.
      Contracts: maps to LEAF_BODY_CEILING_HELD
- [ ] **AC-8.** Delegation is six leaves, each owning its topic's keys, and the
      registration check follows the move.
      Contracts: maps to DELEGATION_SPLIT_INTO_SIBLINGS
- [ ] **AC-8a.** For the delegation split and the three bloat-audit splits, every
      non-blank line of each pre-split body (at the batch base) occurs in exactly
      one resulting leaf, except the lines §6 marks as new.
      Contracts: none; detective, the one-time verbatim record at each split's gate (§5), judged by the reviewer.
- [ ] **AC-9.** Each adopted rule has exactly one home, and no shipped pointer
      sends a reader to the old file for a moved key.
      Contracts: maps to ADOPTED_RULE_HOMES

### Effort and briefs

- [ ] **AC-10.** Every shipped agent declares its default effort from the closed
      set, matching the table.
      Contracts: maps to AGENT_DECLARES_EFFORT
- [ ] **AC-11.** The handback template carries an `effort:` field that echoes the
      brief's effort line, including the host-applied default where it differs,
      and an `expertise_gap:` field.
      Contracts: maps to HANDBACK_CARRIES_EFFORT_AND_EXPERTISE_GAP
- [ ] **AC-12.** The graph discipline's step 2 tells a worker that what a node
      lists is a menu.
      Contracts: maps to BOOTSTRAP_STEP2_LOADS_A_MENU
- [ ] **AC-13.** No shipped Markdown file under `core/`, `agents/`, `protocols/`,
      `skills/`, `templates/` or `integrations/` contains any §6 "Pending
      phrases" entry, including one wrapped across a line break.
      Contracts: maps to ADOPTED_RULES_NOT_PENDING

### Doctrine (detective)

- [ ] **AC-14.** Given this spec's plan §9, a reviewer who loads only
      `method.delegation-cycle-economy` and `method.delegation-model-classes`
      reproduces: each batch's spawn count and size; each spawn's effort line
      (row and value); the question-file path; where each ruling pass falls; the
      tip cadence (targeted plus cross-cutting per increment, full suite once at
      the tip, failures compared by test id, nothing leaves the branch before it
      passes); and when the mutation pass runs.
      Contracts: none; detective, a clean-context check by the reviewer at verify.
- [ ] **AC-15.** The implementer's charter, the tester's charter and
      `protocol.test-first` say, by pointer to `delegation.green-self-test`: RED
      batches are sized by effort; GREEN runs its own tests with no separate
      tester spawn; the implementer never edits a test or fixture file; a test
      that looks wrong becomes a question.
      Contracts: none; detective, judged by the reviewer at verify.
- [ ] **AC-16.** The joint-pass leaf asks the design-latitude question before
      spec §3, and the press and the ruling pass say they check against the
      recorded answer. It describes the joint pass (§6 table) as one pass in
      which each specialist writes its spec part and its plan part, and
      `grill.flow` and `specify.flow` point at it.
      Contracts: none; detective, judged by the reviewer at verify.
- [ ] **AC-17.** The no-write-inspection, graph-over-harness and
      no-lint-only-tests rules each have exactly one home
      (`engineering-posture.no-write-inspection`,
      `context-router.graph-over-harness`, `test-first.no-lint-only-tests`), held
      mechanically. The works-claim rule appears as a sharpening inside
      `method.host-parity`'s "Validate where it runs" and is restated nowhere
      else; the reviewer judges that part at verify.
      Contracts: maps to ADOPTED_RULE_HOMES
- [ ] **AC-18.** The bootstrap template lists the stack-expertise step among the
      required companions, with the mid-work lookup and the `expertise_gap` path
      to `research-scout`. The orchestrator's charter and the model-class leaf
      state light variants as adopted and never on a security surface. The
      knowledge-graph skill states the leaf rule and the branch shape.
      Contracts: none; detective, reviewer at verify.
- [ ] **AC-19.** `method.delegation-cycle-economy` states the §6 question-entry
      and rulings shapes. It says the ruling pass runs once per batch, after
      every in-flight spawn hands back and before the next batch, and that an
      empty file is recorded "no questions". It says the architect writes its own
      amendment when no other live lane holds the spec, never to relax or
      remove a contract, or to amend one on a security, data-integrity or money
      surface, without the owner. It says one mutation pass runs per spec at its
      end, mandatory for security, data-integrity and money contracts with a
      mutant for every increment in those classes, sampled elsewhere. The
      architect's charter points at the ruling pass and the amendment.
      Contracts: none; detective, reviewer at verify.
- [ ] **AC-20.** The verify record lists the eager-surface figures per host and
      the kernel size that seed-lint reports at the batch-1 base and at the final
      tip, and it names the cause of any growth.
      Contracts: none; the existing eager and kernel budget checks, compared by the reviewer at verify.

## 10. Test mapping

(Owned by `tester`. Drafted 2026-09-26 by `tester` before any case existed,
pasted at ruling pass 0 with the rulings applied. Python methods carry
`Asserts SPEC-0005 <SLUG>.` as their first docstring line; shell cases carry it
as a comment inside the case, beside `# exercises: <check>`. "guard" = passes on
the unmodified tool, recorded green on arrival and held by a named mutant instead
of an observed red. The `check-coverage-binder.py` failure naming checks
seed-lint does not yet run is an expected RED id of its own.)

**Ruling pass 1 (2026-09-26).** Statuses set from the first RED batch's
handbacks: every case written is `red`, except the guards, which are `green`.
The test case cell of a Python row is the bare method name (its class is in the
level cell), so seed-lint binds it to the file and to the slug in its docstring.
A shell row's test case cell opens with its invariant label (`X336` onward), the
form seed-lint's label binder reads; each label is written as a comment inside
its case in `tests/test-seed-lint.sh`, as SPEC-0004's `X300` to `X335` are. Rows
with no test file carry `—`.

| Contract / Failure | Test case | Test file | Level | Status |
|---|---|---|---|---|
| PLAN_PROMOTES_PHRASE_MATCHED_EXPERTISE | test_plan_promotes_expertise_past_the_scored_cut | tests/test_graph_lint.py | unit, PromotionTests (CLI, fixture graph) | green |
| PLAN_PROMOTES_PHRASE_MATCHED_EXPERTISE | test_plan_partial_phrase_does_not_promote | tests/test_graph_lint.py | unit, PromotionTests; guard | green |
| PLAN_PROMOTES_PHRASE_MATCHED_EXPERTISE | test_plan_full_hit_on_non_expertise_stays_under_the_cut | tests/test_graph_lint.py | unit, PromotionTests; guard | green |
| PLAN_PROMOTES_PHRASE_MATCHED_EXPERTISE | test_plan_without_hit_or_path_is_unchanged | tests/test_graph_lint.py | golden (ID sets), PromotionTests; guard | green |
| PROMOTION_FLOODS_LOAD | test_plan_promotes_one_word_phrase_uncapped | tests/test_graph_lint.py | unit, PromotionTests | green |
| DESCENT_TEST_NOW_SEEDS_THE_CHILD | test_plan_descent_never_folds | tests/test_graph_lint.py | unit, DescentTests (reshaped at ruling pass 0) | green |
| DESCENT_TEST_NOW_SEEDS_THE_CHILD | test_plan_descends_two_levels_each_on_own_term | tests/test_graph_lint.py | unit, DescentTests (reshaped at ruling pass 0) | green |
| DESCENT_TEST_NOW_SEEDS_THE_CHILD | test_plan_selects_major_by_tfm_token | tests/test_graph_lint.py | unit, DescentTests (reshaped at ruling pass 0) | green |
| DESCENT_TEST_NOW_SEEDS_THE_CHILD | test_plan_warns_on_wide_descent | tests/test_graph_lint.py | unit, DescentTests (reshaped at ruling pass 0) | green |
| PLAN_INFERS_EXPERTISE_FROM_NAMED_FILES | test_plan_infers_from_extension | tests/test_graph_lint.py | unit, InferenceTests | green |
| PLAN_INFERS_EXPERTISE_FROM_NAMED_FILES | test_plan_infers_from_nested_lockfile | tests/test_graph_lint.py | unit, InferenceTests | green |
| PLAN_INFERS_EXPERTISE_FROM_NAMED_FILES | test_plan_infers_from_bare_manifest | tests/test_graph_lint.py | unit, InferenceTests | green |
| PLAN_INFERS_EXPERTISE_FROM_NAMED_FILES | test_plan_inferred_path_echo_is_normalized_and_sanitized | tests/test_graph_lint.py | unit, InferenceTests | green |
| PLAN_INFERS_EXPERTISE_FROM_NAMED_FILES | test_plan_pattern_text_as_words_does_not_promote | tests/test_graph_lint.py | unit, InferenceTests; guard | green |
| PLAN_INFERS_EXPERTISE_FROM_NAMED_FILES | test_plan_task_text_is_never_a_pattern | tests/test_graph_lint.py | unit, InferenceTests (adversarial) | green |
| HOSTILE_TASK_LINE | test_plan_hostile_task_line_never_raises | tests/test_graph_lint.py | unit, InferenceTests (adversarial: token cap, long token, forced error prints the notice) | green |
| TASK_LINE_WITHOUT_PATHS | test_plan_infers_nothing_without_a_path_token | tests/test_graph_lint.py | unit, InferenceTests; guard | green |
| PATTERN_BRACE_SPLIT | test_plan_brace_pattern_tail_promotes | tests/test_graph_lint.py | unit, InferenceTests | green |
| EXTENSIONLESS_BARE_NAME | test_plan_bare_dockerfile_infers_nothing | tests/test_graph_lint.py | unit, InferenceTests; guard | green |
| EXTENSIONLESS_BARE_NAME | test_plan_dotted_dockerfile_infers | tests/test_graph_lint.py | unit, InferenceTests | green |
| PLAN_PROMOTED_NODE_TAKES_ITS_CLOSURE | test_plan_promoted_node_brings_required_parent | tests/test_graph_lint.py | unit, PromotedClosureTests | green |
| PLAN_PROMOTED_NODE_TAKES_ITS_CLOSURE | test_plan_promoted_node_descends_to_named_child | tests/test_graph_lint.py | unit, PromotedClosureTests | green |
| PLAN_PROMOTED_NODE_TAKES_ITS_CLOSURE | test_plan_scored_and_hit_prints_no_suffix | tests/test_graph_lint.py | unit, PromotedClosureTests; guard | green |
| PLAN_PROMOTED_NODE_TAKES_ITS_CLOSURE | test_plan_promoted_and_inferred_prints_promotion_only | tests/test_graph_lint.py | unit, PromotedClosureTests | green |
| LISTED_NODE_EDGES_REACH | test_listed_node_peer_is_reachable | tests/test_graph_lint.py | unit, ListedNodeEdgesTests (also covers SIBLING_UNREACHABLE_AFTER_GRAFT) | green |
| ORPHAN_ISLAND | test_unlisted_peer_island_still_unreachable | tests/test_graph_lint.py | unit, ListedNodeEdgesTests; guard | green |
| DELEGATION_LEAVES_ROUTE | test_delegation_sibling_routes_on_its_phrase | tests/test_graph_lint.py | integration (installed graph), DelegationRoutingTests | green |
| DELEGATION_LEAVES_ROUTE | test_delegation_phrase_is_a_load_when_entry | tests/test_graph_lint.py | integration (installed graph), DelegationRoutingTests | green |
| AGENT_DECLARES_EFFORT | test_lint_accepts_each_value_in_the_closed_set | tests/test_agent_lint.py | unit, LintEffortTests; guard | green |
| AGENT_DECLARES_EFFORT | test_lint_fails_on_missing_effort | tests/test_agent_lint.py | unit, LintEffortTests (CLI, fixture roster) | green |
| AGENT_DECLARES_EFFORT | test_lint_fails_on_effort_outside_the_set | tests/test_agent_lint.py | unit, LintEffortTests | green |
| AGENT_DECLARES_EFFORT | test_lint_real_roster_effort_matches_the_table | tests/test_agent_lint.py | contract (real roster vs §6 table), LintEffortTests | green |
| AGENT_WITHOUT_EFFORT_AFTER_GRAFT | test_lint_fails_on_plant_agent_without_effort | tests/test_agent_lint.py | unit, LintEffortTests | green |
| HOST_REJECTS_EFFORT_KEY | (none) the harvest's fresh-install gate per host, and the existing projection lint in `tests/test-full-install.sh`. Observed at the final tip 3c62b18: the fresh install passed for every host adapter, and all 20 installed agents keep `effort:` on the Claude Code install path. Whether another host warns on the key is not recorded | — | e2e; observed at tip | green |
| LEAF_BODY_CEILING_HELD | X336 case_ce_leaf_new_oversized | tests/test-seed-lint.sh | fixture (scope), `check_leaf_body_ceiling` | green |
| LEAF_BODY_CEILING_HELD | X337 case_ce_leaf_stale_member | tests/test-seed-lint.sh | fixture (scope), `check_leaf_body_ceiling` | green |
| LEAF_BODY_CEILING_HELD | X338 case_ce_leaf_unknown_member | tests/test-seed-lint.sh | fixture (scope), `check_leaf_body_ceiling` | green |
| LEAF_BODY_CEILING_HELD | X339 case_ce_leaf_ratchet_ceiling_raised | tests/test-seed-lint.sh | fixture (scope), `tools/ratchet-lint.py` | green |
| LEDGER_REGROWS | X340 case_ce_leaf_ratchet_member_added | tests/test-seed-lint.sh | fixture (scope), `tools/ratchet-lint.py` | green |
| SIBLING_OVER_CEILING | X341 case_ce_leaf_sibling_over | tests/test-seed-lint.sh | fixture (scope), `check_leaf_body_ceiling` | green |
| DELEGATION_SPLIT_INTO_SIBLINGS | X342 case_ce_split_sibling_missing | tests/test-seed-lint.sh | fixture (scope), `check_delegation_split` | green |
| DELEGATION_SPLIT_INTO_SIBLINGS | X343 case_ce_split_key_wrong_home | tests/test-seed-lint.sh | fixture (scope), `check_delegation_split` | green |
| DELEGATION_SPLIT_INTO_SIBLINGS | X344 case_ce_split_peer_dropped | tests/test-seed-lint.sh | fixture (scope), `check_delegation_split` | green |
| DELEGATION_SPLIT_INTO_SIBLINGS | X345 case_ce_split_neighbour_missing | tests/test-seed-lint.sh | fixture (scope), `check_delegation_split` | green |
| DELEGATION_SPLIT_INTO_SIBLINGS | X346 registration-home (the existing case, repointed to `core/method/delegation-bounds.md`) | tests/test-seed-lint.sh | fixture (scope), the existing registration check | green |
| VERBATIM_DRIFT | (none) one-time scratch record at each split's gate (§5) | — | manual record | pending |
| ADOPTED_RULE_HOMES | X347 case_ce_home_key_owned_twice | tests/test-seed-lint.sh | fixture (scope), `check_adopted_rule_homes` (batch 1b) | green |
| ADOPTED_RULE_HOMES | X348 case_ce_home_key_missing | tests/test-seed-lint.sh | fixture (scope), `check_adopted_rule_homes` (batch 1b) | green |
| STALE_POINTER | X349 case_ce_stale_pointer | tests/test-seed-lint.sh | fixture (scope), `check_adopted_rule_homes` (batch 1b) | green |
| HANDBACK_CARRIES_EFFORT_AND_EXPERTISE_GAP | X350 case_ce_handback_effort_removed | tests/test-seed-lint.sh | fixture (scope), `check_handback_fields` (batch 1b) | green |
| HANDBACK_CARRIES_EFFORT_AND_EXPERTISE_GAP | X351 case_ce_handback_gap_removed | tests/test-seed-lint.sh | fixture (scope), `check_handback_fields` (batch 1b) | green |
| BOOTSTRAP_STEP2_LOADS_A_MENU | X352 case_ce_step2_reworded | tests/test-seed-lint.sh | fixture (scope), `check_bootstrap_step2`, all six copies reworded alike (batch 1b) | green |
| BOOTSTRAP_STEP2_LOADS_A_MENU | X353 case_ce_step2_rewrapped_passes | tests/test-seed-lint.sh | fixture (scope), `check_bootstrap_step2`, all six copies re-wrapped (batch 1b); guard | green |
| ADOPTED_RULES_NOT_PENDING | X354 case_ce_pending_phrase_planted | tests/test-seed-lint.sh | fixture (scope), `check_adopted_rules_not_pending`, one plant per §6 phrase (batch 1b) | green |
| ADOPTED_RULES_NOT_PENDING | X355 case_ce_pending_phrase_wrapped | tests/test-seed-lint.sh | fixture (scope), `check_adopted_rules_not_pending` (batch 1b) | green |
| PLAN_PROMOTES_PHRASE_MATCHED_EXPERTISE | test_plan_partial_version_token_does_not_promote | tests/test_graph_lint.py | unit, PromotionTests (fix batch: `target net10` does not promote a node whose piece is `net10.0`) | green |
| PLAN_PROMOTES_PHRASE_MATCHED_EXPERTISE | test_plan_dotted_compound_named_whole_promotes | tests/test_graph_lint.py | unit, PromotionTests (batch F3: naming the whole dotted and hyphenated token still promotes); guard | green |
| PLAN_PROMOTES_PHRASE_MATCHED_EXPERTISE | test_plan_phrase_with_a_slash_still_promotes | tests/test_graph_lint.py | unit, PromotionTests (fix batch); guard | green |
| PLAN_PROMOTES_PHRASE_MATCHED_EXPERTISE | test_plan_promotion_reports_first_hitting_piece | tests/test_graph_lint.py | unit, PromotionTests (fix batch); guard | green |
| PLAN_PROMOTES_PHRASE_MATCHED_EXPERTISE | test_plan_short_words_are_not_phrase_tokens | tests/test_graph_lint.py | unit, PromotionTests (fix batch); guard | green |
| PLAN_PROMOTES_PHRASE_MATCHED_EXPERTISE | test_plan_stopwords_are_not_phrase_tokens | tests/test_graph_lint.py | unit, PromotionTests (fix batch); guard | green |
| PLAN_PROMOTES_PHRASE_MATCHED_EXPERTISE | test_plan_prefix_fold_does_not_promote | tests/test_graph_lint.py | unit, PromotionTests (fix batch); guard | green |
| PLAN_INFERS_EXPERTISE_FROM_NAMED_FILES | test_plan_task_wildcard_never_matches_a_slash_pattern | tests/test_graph_lint.py | unit, InferenceTests (fix batch); guard | green |
| PLAN_INFERS_EXPERTISE_FROM_NAMED_FILES | test_plan_infers_through_a_slash_pattern | tests/test_graph_lint.py | unit, InferenceTests (fix batch); guard | green |
| PLAN_INFERS_EXPERTISE_FROM_NAMED_FILES | test_plan_infers_literal_name_pattern_in_a_subdirectory | tests/test_graph_lint.py | unit, InferenceTests (fix batch); guard | green |
| PLAN_INFERS_EXPERTISE_FROM_NAMED_FILES | test_plan_slash_piece_without_star_is_a_pattern | tests/test_graph_lint.py | unit, InferenceTests (fix batch); guard | green |
| PLAN_INFERS_EXPERTISE_FROM_NAMED_FILES | test_plan_inference_reports_first_path_in_task_order | tests/test_graph_lint.py | unit, InferenceTests (fix batch); guard | green |
| PLAN_INFERS_EXPERTISE_FROM_NAMED_FILES | test_plan_backslash_only_token_is_not_path_like | tests/test_graph_lint.py | unit, InferenceTests (fix batch); guard | green |
| HOSTILE_TASK_LINE | test_plan_long_token_flood_does_not_use_the_cap | tests/test_graph_lint.py | unit, InferenceTests (fix batch); guard | green |
| HOSTILE_TASK_LINE | test_plan_cap_counts_only_path_like_tokens | tests/test_graph_lint.py | unit, InferenceTests (fix batch); guard | green |
| HOSTILE_TASK_LINE | test_plan_token_of_exactly_256_is_considered | tests/test_graph_lint.py | unit, InferenceTests (fix batch); guard | green |
| PLAN_PROMOTED_NODE_TAKES_ITS_CLOSURE | test_plan_seed_closure_is_accounted_before_promotion | tests/test_graph_lint.py | unit, PromotedClosureTests (fix batch); guard | green |
| ADOPTED_RULE_HOMES | X356 case_ce_stale_pointer_wrapped | tests/test-seed-lint.sh | fixture (scope), `check_adopted_rule_homes`, path and key on two lines, reported at the line holding the path only (fix batch; expectation tightened in batch F3) | green |
| ADOPTED_RULE_HOMES | X357 case_ce_stale_pointer_front_door | tests/test-seed-lint.sh | fixture (scope), `check_adopted_rule_homes`, a stale pointer planted in `README.md`, `INSTALL.md` and `documentation/` (fix batch) | green |
| ADOPTED_RULE_HOMES | X358 case_ce_stale_pointer_root_prompt | tests/test-seed-lint.sh | fixture (scope), `check_adopted_rule_homes`, a stale pointer planted in `INSTALL_PROMPT.md` (batch F3); guard | green |
| ADOPTED_RULE_HOMES | X359 case_ce_stale_pointer_wrapped_key_first | tests/test-seed-lint.sh | fixture (scope), `check_adopted_rule_homes`, key on the first line and path on the next, reported at the key's line (batch F3); guard | green |
| ADOPTED_RULE_HOMES | X360 case_ce_adjacent_correct_pointers_pass | tests/test-seed-lint.sh | fixture (scope), `check_adopted_rule_homes`, a hub pointer on one line and a correct sibling pointer on the next yield no finding (batch F3) | green |
| TEMPLATE_CHANGE_UNDER_SPEC_0003 | (none) SPEC-0003 verify command; held for the owner | — | verify record | pending |
| EFFORT_NOT_APPLIED_PER_SPAWN | (none) reader: the brief's effort line; field held by HANDBACK_CARRIES_EFFORT_AND_EXPERTISE_GAP | — | review | pending |
| IMPLEMENTER_EDITS_A_TEST | (none) the RED hash re-check at the commit boundary and the tip | — | commit boundary | pending |
| RULING_RELAXES_A_CONTRACT | (none) reader: the ruling record and §12 | — | review | pending |
| CONTENT_STEERED_GAP | (none) reader: the caller's check before a research-scout request | — | review | pending |
| QUESTION_ENTRY_LOST | (none) the orchestrator's entry count before the ruling pass | — | process record | pending |
| WORKER_GUESSES | (none) reader | — | review | pending |
| RULING_PASS_SKIPPED | (none) reader | — | review | pending |


## 11. Open questions

| Question | Why it matters | Current assumption | Owner | Resolves by |
|---|---|---|---|---|
| Does the kernel need words for the menu rule, or a pointer to the delegation siblings? | FIRST MOVE says "read only those (and their `requires:` closure)"; §1 names `method.delegation` for model classes and bounds, which move to siblings | Ruled at ruling pass 0: no kernel edit; held for the owner's confirmation | owner | the owner's answer |
| SPEC-0003 `BRIEF_TEMPLATES_BYTE_IDENTICAL` and the two templates this spec edits | a live contract of another spec reads red if re-run | Ruled at ruling pass 0: SPEC-0005 does not edit SPEC-0003; held for the steward | steward; docs-librarian | the owner's answer |
| Lifecycle protocols graft, grow, harvest | adr-0007 set a larger ceiling for them on purpose | Ruled at ruling pass 0: ledger members, not split this round; held | owner | the owner's answer |
| The `## Leaves` mechanical check | the owner asked for the shape, not a check | Ruled at ruling pass 0: withdrawn; doctrine only; held for a possible restore | owner | the owner's answer |
| Promotion uncapped on the per-prompt route hook | a pasted document can promote many nodes (cost only) | Ruled at ruling pass 0: uncapped, per the owner's decision; informational | owner | the owner's answer, if any |
| Mutation scope | "every increment gets a mutant" has two readings | Ruled at ruling pass 0: every increment inside the mandatory classes; held for confirmation | owner | the owner's answer |
| Plant-authored agents and the required `effort:` | agent-lint ships into plants | Ruled at ruling pass 0: every agent; informational | owner | the owner's answer, if any |
| The ledger freezes membership, not size | a member may still grow to `MACHINERY_BODY_CEILING` | Accepted under simple; noted by the tester | architect | a later round |

## 12. Changelog

The harvest's working records (questions, rulings, reviews, mutation reports) are
kept outside the seed.

- 2026-09-26 — created in `draft` by `architect` in the joint specify and grill
  pass: §0 to §2, §4 to §8, §11 authored; §3 and §9 drafted for `product`; §10 a
  stub for `tester`. Thirteen contracts. Includes the owner's four additions
  received during the pass: regulated spawn effort, the menu rule, and the branch
  shape and leaf rule. Version 0.1.
- 2026-09-26 — version 0.2, ruling pass 0, by `architect`. Still `draft`.
  Contract count 13 → 12: the `## Leaves` shape check removed as a plant-facing
  obligation the owner did not ask for (held for the owner). §4: the inference
  contract gains the hostile-token and cap/no-raise clauses; the closure and
  listed-edges Givens are made precise; the effort contract holds plant agents
  too. §6: effort row 1 defines a security surface and row-1 departures fail
  closed; the RED hash re-check; the self-amendment limits and the question-file
  rules; the mutation scope; path matching, caps and echo sanitizing; the
  pattern note; the stack-gap rule; the joint pass and the latitude guard move to
  `protocols/specify-joint-pass.md` (specify was near the leaf ceiling); the
  three bloat-audit splits approved, the humanizer kept whole, the lifecycle
  protocols held; the finding fragments; the host-parity home for the
  no-write-inspection rule. §7: the security review's failure modes added. §3
  and §9: the product review applied (AC-8a, AC-18 to AC-20 new; AC-5
  withdrawn). §10: the tester's draft pasted. §2, §5, §11 aligned.
- 2026-09-26 — version 0.3, ruling pass 1, by `architect`. Status `draft` →
  `active`, with all four sign-offs in §0 and `status_evidence`; it lands in the
  change that carries its remaining RED. §6 "Path-like token": the length skip
  precedes the 64-token count, and the strip repeats until stable. §4
  DELEGATION_SPLIT_INTO_SIBLINGS: a redundant clause removed; the property still
  holds. §9: AC-19 carries the full self-amendment limit. §10 reshaped so
  seed-lint binds every row: bare method names for Python rows, one shell case
  per row opening with its invariant label, `—` where no test file exists;
  statuses set from the first RED batch. No contract changed.
- 2026-09-26 — version 0.4, ruling pass 2, by `architect`. Still `active`. §6
  "Path-like token": the path-like test runs before normalization, so a
  backslash-only token is not path-like (the order increment 6 implemented).
  §10: the rows of increments 6, 7, 10 and 11 and the two DelegationRoutingTests
  rows flip `red` → `green` at the batch-2 tip; status column only. No contract
  changed.
- 2026-09-26 — version 0.5, ruling pass 3, by `architect`. Still `active`. §6
  `delegation.green-self-test`: the test-edit ban covers REFACTOR, with test
  cleanup routed to the next tester spawn, and the merged T2 path unchanged. §2:
  pointer repairs reach two corpus pages whose cited home moved. No contract
  changed.
- 2026-09-26 — version 0.6, ruling pass 5, by `architect`. Still `active`. §6
  "Trigger phrase" tokens are the router's whole tokens, so `net10.0` is one
  token. ~~This narrows promotion and relaxes nothing;~~ (corrected at ruling
  pass 6: this narrows promotion, except that a piece whose parts were all under
  three characters, such as `ci-cd`, now reads as a phrase that promotes on the
  exact whole compound; graph-sourced, no security impact per the security
  review) it is a routing grammar on the increment-6 parser, so its GREEN runs as
  a batch of one at high effort with a `security` review. §4 ADOPTED_RULE_HOMES
  "And" clause: the scan widens to `documentation/` and the root front-door and
  prompt files, and a pointer wrapped across two lines is read as one; a
  widening, not a relaxation. §10: X347 to X355 flip to `green`; rows added for
  the fix batch's new tests. This version commits in the same change as the fix
  batch's RED.
- 2026-09-26 — version 0.7, ruling pass 6, by `architect`. Still `active`. §12's
  v0.6 "narrows promotion and relaxes nothing" corrected. §6 "Effort": the host
  facts a plant needs move back into `core/method/delegation-model-classes.md`,
  which installs into plants, and the Claude Code overlay points at the leaf;
  this corrects a ruling-pass-5 decision that sent them to an overlay
  `install.sh` never places, and relaxes no contract. §2 aligned. §10: the
  partial-version row and X356, X357 flip to `green` (F2 tip 49/49); rows added
  for batch F3. `status_evidence` updated.
- 2026-09-26 — version 0.8, final status pass, by `architect`. Still `active`;
  no contract changed. §10: X360 flips to `green` (increment 43, 3c62b18);
  HOST_REJECTS_EFFORT_KEY is set from the fresh-install observation at the final
  tip. The other `pending` rows stay pending because no test or record binds
  them: VERBATIM_DRIFT and TEMPLATE_CHANGE_UNDER_SPEC_0003 are verify records
  (the second is held for the owner), and the rest are reader rows. §6 "Effort":
  "overrides the session's effort level" now reads "sets the effort for every
  spawn of that definition", matching the model-class leaf. `status_evidence`
  cites the final tip, the fresh-install gate and the mutation totals.
- 2026-09-26 — text cleanup, no contract change: session identifiers, worker
  labels and paths to the harvest's working records removed; reasons kept in
  words.
