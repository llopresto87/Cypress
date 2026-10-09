---
name: canonize
description: The single end-of-task close-out spawn. At the completion of every non-trivial task, spawn the docs-librarian once with a combined brief that (a) persists into docs/graph any knowledge of interest the work surfaced (b) catalogs in docs/graph/tools any durable tool it produced (the toolcraft doctrine, kernel §3.8, executes inside this same spawn — never a second one), (c) walks the open/hotfix status register item by item and moves — in frontmatter, with evidence — what this session actually moved, (d) records every decision that departs from a standard the graph owns as both an ADR entry and a standing `deviation.*` node, and (e) on a T2 contained-lane task writes the why-record the lane owes — one ADR or one changelog line carrying defect → cause → fix → pinning test. A task is not complete until all five are done or explicitly recorded empty. For Tier 0/1 tasks (kernel §0), the session self-records "nothing of interest / no tool" in the delivery instead of spawning. Runs before deliver signs off.
id: protocol.canonize
tier: 2
kind: protocol
origin: seed
title: canonize — the single close-out spawn that persists knowledge and catalogs tools
owns:
  - rule.canonize
  - canonize.close-out-flow
  - canonize.status-review
  - canonize.deviation-capture
  - canonize.why-record
  - canonize.session-record
  - canonize.harvest-candidates
requires:
  - skill.toolcraft
peers:
  - agent.tool-smith
  - protocol.deliver
  - protocol.harvest
  - skill.adr-writer
  - skill.source-index
artifacts:
  - templates/prompts/graph-session-bootstrap.md
  - templates/tool-page.template.md
  - templates/skill.template.md
  - templates/docs/nodes/_deviation.template.md
  - templates/docs/nodes/_expertise.template.md
load_when:
  - "task is finishing, close out, before deliver"
  - "persist what we learned into the graph"
  - "spawn the docs-librarian, canonize"
  - "catalog a tool or skill the work produced"
  - "status review at close-out: did each register item move this session"
  - "we departed from the standard, record the deviation and why"
  - "small fix with no spec, where does the why get written down"
  - "handback overflow notes, read them at close-out"
  - "file the session record, which harness memory entries can be retired"
  - "a lesson flagged as a harvest candidate: add its row to the plant's record"
prevents: Knowledge that dies with the session that produced it, and durable tools reinvented as throwaway scripts because nothing cataloged the last one.
est_tokens: 4272
command: true
---

# Protocol: canonize — the close-out spawn

This node owns **the canonize rule**: knowledge of interest is captured
before a task is done. Work generates knowledge and capabilities; if
either lives only in the session transcript, it dies with the session and
the next agent rediscovers or rewrites it the hard way. Every T2/T3 task
ends with **one** docs-librarian spawn, the close-out, which persists into
`docs/graph/` the facts, sharp edges, corrected assumptions, provenance,
and missed `load_when:` triggers the work surfaced; catalogs its durable
tools (the toolcraft rule) in the same pass; moves the lifecycle status of
whatever the session closed, parked, or patched; and writes each
deliberate departure from a graph-owned standard as a standing deviation.
Facts land in the graph, tools in the catalog, status in frontmatter,
deviations in `nodes/`. It is one execution for all of it, because a second
spawn with the same bootstrap and the same lint run would be pure
coordination waste.

Only the librarian writes the graph's **fact-bearing surfaces** (nodes,
wiki pages, the tool catalog), and it keeps one home per fact; the session
writes none of them. The session writes its own operational artifacts under
the same root directly:
grill.md (`rule.grill`), changelog.md, and the session records in
`plans/sessions/`, where the librarian's one write is the status lines it
appends. The verification runbook belongs to the tester worker that ran
the gates (`protocol.verify`).

## When to invoke

- At the completion of every **Tier 2/3** task or increment (kernel §0),
  before `deliver`.
- Whenever the work surfaced a fact the graph does not own, contradicted
  one it does, or produced a tool a future session will run again.
- **Tier 0/1 shortcut:** a question answered or a trivial non-behavioral
  edit needs no spawn. The session writes one line in the delivery,
  "canonize: nothing of interest / no tool, because …", however minor the
  task, and that line satisfies the fail-closed doctrine. A T0/T1 task
  that surfaced something durable escalates: spawn the librarian.

## What the one brief carries

**Knowledge candidates** (§3.7), canonize this:
- a new or changed fact about the project's structure or capability;
- a sharp edge that bit (and the tell that would spot it next time);
- a corrected assumption: the graph asserted X, the work proved not-X;
- a page `anchors --moved` named in flow step 1: a page citing moved code,
  whose facts about that code are re-checked against it;
- provenance for a claim (the source/path/symbol that grounds it);
- a `load_when:` trigger that should have matched this task and didn't;
- a new library idiom or pitfall learned while using a dependency.

**Session record** (`canonize.session-record`): what the orchestrating
session itself learned, which no handback carries. The record and its
shape belong to `method.stewardship-posture`
(`stewardship-posture.session-record`). The brief names the path of every
record the task wrote or appended to since the last close-out; it
carries the paths ONLY, and the librarian reads each record itself. The
librarian walks every item that has no line in the record's "Canonize
status" and gives each exactly one outcome. An owner rule about how agents
work with this owner goes to `crosscut.operator`
(`docs/graph/nodes/_operator.template.md`); an owner rule about the
project goes to the node that owns its topic, and a procedure to a project
skill. A corrected assumption is fixed in place, in the node or leaf that
asserted the wrong thing. Resume state is not placed
("resume state; stays in the record"). Anything else is placed where it belongs, or not placed
with the reason. Per item the librarian appends one line to "Canonize
status",
`- <section> <item> → <node id and fact key, or file>` or
`- <section> <item> → not placed: <reason>`, then one line
`- retirable harness entries: <names>, awaiting the owner's confirmation by name`
(or `none`), and last the code-anchor line of flow step 3. The librarian
ONLY appends to a record, and ONLY writes inside the plant: harness memory
sits outside it, and retiring a harness entry stays the owner's decision,
taken by name (kernel §4). The record is a source of knowledge candidates,
so it adds no sixth duty to this close-out. A T2/T3 task that wrote no
record is handed back as the finding "no session record".

**Tool candidates** (§3.8, `docs/graph/skills/toolcraft.md` owns the
doctrine): catalog any durable tool the work produced (recurs across
sessions, stable interface, test-authorized, lives in the repo). The
worker handbacks already name these in `tools_built`; the brief forwards
them, and adds what no handback named: each script, plugin or module the
task's diff added outside the test tree, so durable code nobody reported
still meets the durability test instead of waiting for the librarian to
notice it. The builder is `agent.tool-smith`, spawned mid-task when the
recurrence was noticed; the close-out ONLY catalogs what was built. A tool
candidate that arrives with no tool behind it is a finding for the next
plan, not work for the librarian. The brief names the same way each core
dependency the work leaned on that has no `libraries/` page, and the
librarian runs `protocol.ingest-library` for it in this close-out (a
`research-scout` spawn, its one `delegates_to` entry). A page the pass
cannot build now is recorded as a finding for the next plan, and the
delivery names it under Known limitations.

**Skill candidates** (§3.8, the procedure sibling of a tool; the doctrine
lives in `docs/graph/skills/toolcraft.md`): forward any repeatable
multi-step procedure the work walked that a future session will walk
again, named in `skills_built` on a handback, or the same sequence now
appearing a third time in grill/changelog. The brief forwards the
candidates; the librarian authors them.

**Harvest candidates** (`canonize.harvest-candidates`): a lesson the owner, a
session record, a handback or a retrospective flags as possibly belonging in the
seed. The lesson is placed in its plant home first, like any knowledge
candidate. Then the librarian appends one row to
`docs/graph/plans/harvest-candidates.md`, created from
`docs/graph/plans/_harvest-candidates.template.md` when absent: the candidate in
one line, its home in the plant, its provenance and trigger, and a first guess
at its class. The form's admission test filters first: a lesson that would make
no sense in a repository with none of this project's services or domain is a
project rule, and it gets no row. A lesson bound to a stack still gets a row,
because harvest keys it by stack. A row is struck with a dated note, never
rewritten. The record is the plant's own, so a graft that overwrites a charter
cannot take its lessons with it, and a harvest can start from the rows instead
of re-reading the plant's history. A row decides nothing: harvest stays the
owner's to start, and its agnosticism gate rules on each row.

**Status review** (`canonize.status-review`): the brief instructs the
librarian to run `python3 docs/graph/status-register.py --open --hotfix`
against the tree as the session left it and walk the result item by
item, asking of each: *did this move this session?* What the work
closed gets `status: closed` + `status_evidence` (the gate run, commit,
or path#anchor that proves it); what it patched improperly is `hotfix`
with an `owner`; what it parked is `deferred` with `reopen_when`. Moves
land in frontmatter ONLY, where the register reads them; the vocabulary
and its companions are `docs/graph/_schema.md` §"Lifecycle status". The
librarian ONLY records the moves this session made: an item the work did
not move keeps its status. The brief carries the instruction, and the
librarian runs the register itself.

**Session metrics**: the check is deliver's: the session runs
`docs/graph/session-metrics.py` on its own delivery entry
(`docs/graph/protocols/deliver.md`). When the brief asks for the plant's
metrics, the librarian runs `python3 docs/graph/session-metrics.py --all`
and hands back what it prints, an `incomplete` entry included, and never
reconstructs a number, because reconstructed numbers would be guesses
that `harvest` aggregates as data.

**Deviation candidates** (`canonize.deviation-capture`): every
decision made this session that departs from a standard the graph owns
(a fact key, a posture node, a `best-practices/` leaf, an external norm
the graph records). The brief names the decision and the standard; the
librarian asks **why**, of the session or of the handback that
carries the decision, and writes BOTH homes: the ADR entry (the
history; `docs/graph/skills/adr-writer.md`) and a `deviation.<slug>`
node in `docs/graph/nodes/` (the standing truth: `status: standing`,
`departs_from`, `reason`, `scope`, `ends_when`, `recorded_in` naming the
ADR), in the form of `docs/graph/nodes/_deviation.template.md` (the
seed ships it in its `templates/docs/` mirror; the underscore keeps the
blank form out of the router). A departure with no node is a lapse the next
session will "fix"; one with no ADR is a decision nobody can trace; with
both, the router surfaces it exactly when the topic comes up and it is
never re-litigated or mistaken for a lapse. If nobody can say why, it
is not a standing deviation: record it `status: open` with an owner
and let the next session decide.

**Why-record** (`tiers.contained-lane`): owed by every **T2
contained lane** task, because the lane spent no spec to explain
itself and the close-out is where that debt comes due. The brief names
the defect, its cause, the fix, and the test that pins it (for a
declarative edit, the run that proved it), and the
librarian writes exactly **one** entry: an **ADR** when a real choice was
made among options (`docs/graph/skills/adr-writer.md`), otherwise a
`changelog.md` line naming defect → cause → fix → test or run. A small change
that needs a spec to be explicable was misclassified: the close-out says
so in the delivery and reclassifies it. A covered-lane task owes no
why-record: its spec contract already carries the why.

**Prose pass** (`humanizer.scope`): node bodies and session records are
written for models, so the librarian writes them in compact instruction
language and gives them no humanizer pass. A runbook or README paragraph it
writes or refreshes this spawn is prose a person reads, so the brief
instructs the librarian to apply `docs/graph/skills/humanizer.md` in file
mode to it. On every prose file the spawn changes, the librarian runs
`python3 docs/graph/prose-lint.py --file <path> --against HEAD` before the
graph-lint pass, so no file gains a strong tell or drops a number, heading,
code span, or link target.

**Kept out of every candidate list:** ephemeral scratch, throwaway
prototypes and genuine one-offs (they have no future reader); secrets,
credentials, production or personal data (kernel §4); speculation (write
"not recorded"); project-specific material aimed at the seed (it stays in
its plant home; a lesson that passes the admission test gets a
harvest-candidate row, and `harvest`'s agnosticism gate decides the rest).

## The flow (one spawn)

1. **Assemble candidates** from the finished work, the session's
   records in `docs/graph/plans/sessions/` (named by path), and the
   workers' handback payloads: facts with evidence, tools with path +
   entry point + invocation + covering test, the scripts, plugins and
   modules the diff added that no handback named, every lesson flagged a
   harvest candidate, every decision that
   departed from a graph-owned standard (each with the standard it
   departs from), and, on the T2 contained lane, the why-record's
   defect, cause, fix, and pinning test. Include every overflow note a
   worker wrote when its handback did not fit, at
   `docs/graph/plans/<unit of work>/overflow/<spawn_id>.md`
   (`docs/graph/templates/prompts/handback-payload.md` owns its shape):
   the brief names each one, and the librarian reads each as candidate
   evidence. A handback carries only the decision content, so the
   caveats and dead ends that did not fit live in the note and nowhere
   else. Last, the session runs
   `python3 docs/graph/source-index.py anchors --moved` once: it lists the
   graph pages that cite a code file moved since the last recorded anchor,
   and the brief hands those pages to the librarian as the pages whose
   facts it re-checks. It runs here, before step 3's
   `code-anchor.py --record`, because recording the anchor first empties
   the moved list; nothing runs it per prompt or per file access
   (ADR-0018).
   A `repo-unresolved` record in its answer is a node whose `repo:`
   names nothing on disk; the brief hands that node to the librarian,
   which corrects it in the same close-out: one plant-relative path that
   exists, or no `repo:` line.
2. **Spawn the docs-librarian once** (authoring-class; it owns
   `docs/graph/`) with a brief that embeds the canonical block from
   `docs/graph/templates/prompts/graph-session-bootstrap.md` plus the
   candidate lists. This spawn is fail-closed, and a `grow`/`graft`
   session reaches it in the same session that installed the roster, so
   if the host has no such type, apply `delegation.harness-registration`
   (`docs/graph/method/delegation-bounds.md`): re-enter rooted at the
   plant or role-emulate and record it. The close-out runs either way.
3. **The librarian persists and catalogs in one pass.** Where the step
   says a corpus is checked first, that applies when the corpus is present
   (the seed repo, or a plant that harvested it).
   - *Facts:* each lands in exactly one node's `owns:`; when the graph
     already owns the fact, update that home in place. `load_when:`
     triggers that failed to fire are sharpened.
   - *Tools:* each gets `docs/graph/templates/tool-page.template.md`
     filled into `docs/graph/tools/<name>.md`, an index row, and an
     `artifacts:` edge from its owning node; check `tool-corpus/` first
     for a ready card. A tool the plant built against a page placed
     earlier from `tool-corpus/` re-points that page in place, to the
     real implementation path and test command, and drops its
     `blueprint only, not built here` mark; a second page for the same
     tool would be two homes.
   - *Skills:* each recurring procedure gets
     `docs/graph/templates/skill.template.md` filled into its home node
     `docs/graph/skills/<name>.md`, plus the projection in each harness
     directory the plant actually uses (`.claude/skills/<name>/SKILL.md`
     and kin). Check `skill-corpus/` first for a ready one, dedupe
     against skills already present, and compose existing disciplines by
     reference.
   - *Status:* run the status register (`--open --hotfix`) and walk it
     item by item, moving in frontmatter, with evidence, what this session
     moved.
   - *Claims of state:* each status line, figure, pin and commit reference
     the session wrote into a node, a plan row or a record is re-read
     against its source (the repository, the lockfile, the running system)
     before the record closes. A wrong one in a node is corrected in place
     with the check that proved it; one in a plan row or a record, which
     the session writes, goes back to the session with that check, and a
     scope conflict found on the way is flagged, not resolved. A commit is
     cited by a reference that survives a history rebuild (a tag or a
     merged commit).
   - *Deviations:* write each candidate as ADR entry + `deviation.` node
     once its *why* is on record.
   - *Lint:* one `graph-lint` run plus the register's lint role
     (`python3 docs/graph/status-register.py --root docs/graph`) confirm
     the graph stays clean.
   - *Anchor:* with the graph reconciled, run
     `python3 docs/graph/code-anchor.py --record` once. It writes
     `.cypress/anchor.json`: the branch, the commit and the uncommitted
     code paths of each repository the plant governs. The line it prints
     goes into the newest session record's "Canonize status" as a bullet
     of its own, as printed: it already begins `Code anchor recorded`.
     The next session compares against the anchor once at its start: its
     session-start hook runs `--compare`, and a host with no hook reads
     that line. A refusal (exit 1) leaves the old anchor standing, and its
     stderr line takes the place of the printed line. Nothing runs the
     tool per prompt or per tool call.
4. **Confirm or record-empty.** The librarian hands back nodes/fact-keys
   touched, tool cards written, status items moved (id → new status +
   evidence), deviation nodes written, and harvest-candidate rows added,
   or an explicit "nothing of interest, because …" / "no durable tool,
   because …" / "no status moved" / "no deviation". For each session
   record it hands back the items placed (item → home), the items not
   placed (item → reason), and the harness entries that can be retired;
   with no record, it hands back "no session record". It also hands back
   the code-anchor line or its refusal, the lint results and each overflow
   note it read with whether anything in it was persisted.

## Fail-closed doctrine

A task is **not complete** until its knowledge is canonized, any durable
tool is cataloged, and any recurring procedure is crystallized into a
project skill, or each is explicitly recorded empty with a reason
(this node and `docs/graph/skills/toolcraft.md` own the rule; toolcraft
owns what counts as durable). Each duty left neither done nor recorded
empty is a leak of the same failure class as a green lie (§3.5):
- an uncaptured fact (a knowledge leak), tool or procedure (a capability
  leak);
- a status the work moved while the frontmatter still shows `open` (the
  next session redoes closed work, or trusts a hotfix as a fix);
- an unrecorded deviation (a deliberate departure read as a lapse and
  reverted);
- a contained-lane change delivered with no why-record (a behavior change
  nobody can trace back to a reason, the exact debt the lane borrowed
  against when it skipped the spec).

`deliver` (§3.6) signs off once this close-out has run (or the T0/T1
self-record line is present).

## Relationship to the other protocols

- `deliver` produces the human-facing cold-pickup **summary**; canonize
  persists the machine-facing **graph knowledge and tool catalog**.
- `toolcraft` (`docs/graph/skills/toolcraft.md`) owns the *doctrine* of what
  counts as a durable tool. Three actors act at three moments, and each
  needs its own owner: **`skill.toolcraft` rules**, **`agent.tool-smith`
  builds** (mid-task, when the recurrence is noticed), **canonize
  catalogs** (once, in the close-out spawn, which authors nothing).
- `adr-writer` (`docs/graph/skills/adr-writer.md`) writes the ADR that
  carries a deviation's history, and the short-form ADR a contained
  lane's why-record calls for; canonize owns the moment either is
  captured and the `deviation.*` node that makes a departure standing
  truth.
- `harvest` folds **project-agnostic** lessons and tools into the seed,
  user-triggered only; canonize keeps **project-specific** knowledge and
  tools in the plant, and keeps the harvest-candidate record that tells
  a later harvest where to start. What harvest's agnosticism gate rejects
  still belongs here.
