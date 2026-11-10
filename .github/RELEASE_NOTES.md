## 8.3.0 — experimental: one implementer per increment, a security pass on trust paths, and fixes from a trajectory audit (2026-11-10)

This version is experimental. The owner decided on 2026-11-10 to close the
round on a branch of its own instead of the main line, so it carries no tag
and no published release. The round started from an audit of two grown
plants' trajectories and went on to change how work is split across workers,
how much reasoning each spawn gets, and how a change to a trust surface is
checked.

### Measured status

Measured on live builds against the previous release, an increment costs
about the same as it did on 8.2.0, and the security results are stronger:
more evasion paths are caught before a change lands. The round set out to
lower the cost per increment, and that target was not reached. Treat this
version as an experiment to learn from, not as the recommended seed.

### The round in brief

- **One implementer per increment.** The default shape gives one implementer
  the whole increment in one warm cache, and a test judged wrong goes
  straight back to the tester.
- **A security pass on trust paths.** A crosscut node can mark itself
  `trust: true` and claim paths. A change under such a path gets one
  `security` pass after the review; its findings go to a tester for RED and
  then to one implementer for GREEN. Graft and grow ask the owner to settle
  any node whose trust marker is left open.
- **Adversarial controls.** For each security contract, RED writes one
  negative control per evasion class and one test per path to a gated
  action, from the `method.security-controls` checklist.
- **Always-loaded method nodes.** Each role names its core method nodes in
  `always_loads:`, and on Claude Code `install.sh` composes them into the
  role's agent file, so the prompt is the same on every spawn and its cache
  holds.
- **Effort per task.** `brief.py` derives each spawn's reasoning effort from
  its role and task kind. Implementing runs at low effort, and at medium only
  for an increment labelled hard; the review, the security pass and the
  findings tester carry the quality.
- **Graft and grow fixes.** A graft keeps the files the plant edited, stops
  calling new seed nodes re-created, rows a new hook file, and offers a fix
  for a stale composed agent that keeps the node.
- **The orchestrator as output style.** On Claude Code the main session gets
  the orchestrator's charter and always-loaded nodes through a project output
  style, because the main session is no subagent.
- **A project-agnostic sweep.** Seed nodes state their evidence without
  naming the plants or hosts it came from.

### What changed, in the order it landed

The trajectories of two plants grown from scratch were audited: one on
Claude Code (seed 8.1.1, 971 worker spawns) and one on Prime Agent (seed
8.2.0, 59 child sessions). This release fixes what both showed.

- **Route hook: subagent hand-backs are no longer routed.** Claude Code
  hands the `UserPromptSubmit` hook a hand-back as the bare
  `<agent-message …>` frame, not under the "Another Claude session sent a
  message:" header the transcript shows. 966 of the Claude Code plant's
  1,210 route injections fell on hand-backs, 940 of them the "task too
  long to route" notice. `NON_HUMAN_MARKERS` gains `<agent-message `
  (SPEC-0003 §6, X171).
- **Specs, ADRs and plans are graph text.** Their readers are agents, so
  they are written in compact instruction language and get no humanizer
  pass and no prose-lint gate. The humanizer keeps the text people read:
  README and documentation, runbooks, delivery summaries, pull-request
  text, commit messages and what the owner is asked to decide. Owner text
  stays verbatim. The owner of the Claude Code plant ruled this on
  2026-10-31 and paid for a rewrite of about 450 files; the seed now
  starts there. `skill.spec-author` and `skill.adr-writer` drop their
  humanizer step and peer edge; `humanizer.scope` and
  `method.prose-posture` state the rule by consumer.
  The close-out librarian's prose-lint step is scoped the same way: in a
  live A/B run on the Prime Agent plant, 8.3.0 still ran prose-lint 21 times
  on graph text because `canonize` and the librarian charter said "every
  prose file" (76 runs on 8.2.0).
- **New work goes to a fresh worker.** Both owners had to correct a
  session that sent new tasks to old, uncached workers. The rule already
  lived in `delegation.continuation`, a node nothing routes at the moment a
  follow-up is sent, and the Prime Agent plant on 8.2.0 still broke it (307
  messages to children against 43 spawns). The kernel §1 now points at it in
  one line, and the Prime Agent overlay states it beside "collect handbacks
  by message". The overlay no longer tells the session to delete finished
  children: their sessions are the trajectory record an audit like this one
  is built from (the owner, 2026-11-02), and no orchestrator followed it (no
  deletion in 43 spawns on the Prime Agent plant).
- **A worker the host cut off is resumed; a finished one is not woken.** On
  Claude Code a new guard, `.claude/resume-hook.py` (PreToolUse on
  `SendMessage`), reads the target worker's transcript when it has been idle
  longer than a subagent's prompt cache lives (five minutes). A last record
  that is the host's API error (usage or rate limit, network or server
  error) means the worker was cut off mid-turn: the resume passes. Any other
  idle worker, one that handed back above all, is refused, because the
  message rewrites its whole context uncached: new work for an old context,
  or a nudge with nothing to resume. A caller with a real small follow-up,
  or a worker stopped with no error record, starts the message
  `continuation: <reason>`. Cache writes were the largest cost line in both
  plants (49% of the Prime Agent plant's spend), and calls after more than
  five idle minutes were most of them: in the Claude Code plant 531 worker
  calls after such a gap rewrote 135M tokens (44% of its cache writes), 94%
  of them on a worker that had finished its turn and was then messaged.
  Replayed over that plant's 405 messages to workers: 194 warm and 10
  host-cut sends pass, 201 are refused, and the refused sends' first calls
  alone rewrote 63M cache tokens.
- **The Prime Agent README names the cache-lifetime setting.** In the Prime
  Agent plant, the 213 calls that followed an idle gap of more than five
  minutes rewrote the whole context each (290K to 400K tokens) and cost about
  $359 of a $900 run. The README now describes `PI_CACHE_RETENTION=long`,
  which should request the one-hour cache, and how to confirm it on a given
  build, since its value is taken from the upstream library and not verified
  here.
- **Workers read a spec by contract.** `spec-lint.py --slice --refs SLUG`
  has existed since 7.30.0, yet the two plants used it 32 and 2 times. Workers
  instead paged through specs of 84K to 961K characters: about 3,200
  grep/sed/offset-read turns by testers, implementers, reviewers and security
  in one plant, whole-spec dumps in the other. The bootstrap block (step 5)
  now names the slicer, and `delegation.step-scope` has briefs name contract
  slugs instead of copying spec text. Over every contract of both plants (524
  on the Prime Agent plant, 427 in the Claude Code plant's three largest
  specs) the slice is a median of 950 to 1,920 characters, against specs of
  84K to 961K characters. In a controlled pair of workers given the same
  two-contract task on a copy of the Prime Agent plant, the 8.3.0 worker
  read 44% fewer cache tokens (84,576 against 149,804) with the same
  answer; one run per arm.
- **Handbacks carry the route as ids.** The graph-session bootstrap asked
  each worker to paste the router's command and output into its report,
  about 1,100 of a hand-back's 9,000 characters, re-read by the caller on
  every later turn. The route now goes in one `graph_route:` handback
  field: task line, loaded ids, skipped ids, widenings with their reason.
  The five brief templates carry the change byte-identical.
- **A hard-to-undo decision cannot skip its devil's advocate.** On a T3
  plan, grill sent every one-way door to `devils-advocate`, but nothing
  checked that it happened, and the Claude Code plant graded most
  hard-to-undo decisions `expensive`, which the press did not cover: four of
  its seven T3 passes ran none. On the Prime Agent plant the press never
  ran, though a decision there is one-way once real data exists. The owner
  decided on 2026-11-03 that `expensive` decisions are pressed too.
  `grill-lint.py` now fails a §6 row graded `one-way` or `expensive` (now or
  after a milestone) that carries no
  verdict: `could-not-refute`, `refuted`, or `waived by owner <date>`, in
  the row or on a plan line naming an ADR the row cites. The grill
  template's §6 gains a `Refutation` column for it. Of the seven plans on
  hand, the check flags the one missed press and passes the six that ran it.
- **Rulings, fix-ups and next steps go to a fresh worker.** On both plants,
  over 90% of what follow-up messages cost went to workers that had already
  handed back, and each such message replayed the worker's whole context to
  carry what was already a full brief. The two paths were a ruling pass sent
  to the spec's author and a fix-up sent to the worker that wrote the code.
  The ruling pass is now a fresh `architect` briefed by path (spec, question
  files, plan §6). A finished worker is continued only for a small change
  while its prompt cache is still warm (5 minutes on both hosts). Replayed
  over the recorded follow-ups, with a fresh worker's measured start-up cost
  in their place, this saves an estimated 17% of the Claude Code plant's
  cache writes and 22% of the Prime Agent plant's cost. One recorded ruling
  pass was replayed live on a clone of the Prime Agent plant at the commit
  before it: a fresh architect briefed by path gave the same verdict on all
  six parts and wrote 70K tokens to the cache where the idle author had
  rewritten 930K, $0.71 against $4.89 at the same token prices (one run, on
  a different host).
- **The plan linter prints the batches.** `grill-lint.py --batches` groups
  each wave's increments into spawns by the batch table, so batch size is
  read, not judged; on the 8.1.1 plant 54 of 85 RED spawns carried a single
  increment. Increments that write one file run one batch after another,
  each a fresh spawn. The test-first protocol no longer pulls the cycle
  rules into every tester's route; the session still loads them, and a
  tester's route is 15% smaller.
- **The orchestrator stops carrying the review and the brief.** A review
  finding goes to a fresh implementer and a fresh light reviewer of the fix
  diff; a testability return goes to a fresh architect. The kernel no longer
  lists `orchestrator` among the workers, and its description says the
  session plays it and never spawns it. `brief.py --out PATH` writes the
  brief to disk and prints a three-line pointer to send as the prompt: on
  Claude Code the composer's output otherwise reached the orchestrator twice
  per spawn, once as output and once as the prompt. The grill-lint press
  check also fails a §11 risk table with no verdict: the Claude Code
  plant pressed the top risk in none of its seven T3 passes. The
  mutation cadence, the gate-failure count and the close-out count each now
  have one home.
- **Handbacks state paths and gate numbers once.** Callers acted on three
  handback parts: `recommended_next`, `gates` and the paths of the work
  done. On the Claude Code plant the report body repeated the gate numbers
  (about 1,000 characters a handback) and the paths. The body now holds the
  verdict, the blockers and the findings to act on, and repeats a gate only
  when it failed. `next_route_evidence` is gone: 99% of its values were
  "not run", and the caller routes the next hop itself.
- **Workers stop echoing what their caller knows; `brief.py` logs the spawn.**
  The owner decided on 2026-11-03 that a handback carries nothing its caller
  already holds. Every composed brief appends one line to
  `docs/graph/plans/spawns.jsonl` (spawn_id, role, task, route, effort,
  emulation), and `brief.py --log` prints the delivery's
  attribution lines. A spawn_id already logged for another role is refused,
  and `--emulated "<reason>"` records a role emulation. The HANDBACK payload now
  starts at `status:`: `produced_by`, `spawn_id`, `route_evidence`, `effort` and
  `harness_override` are gone, and the deliver-time attribution assertion reads
  the log, so a hand-composed brief now shows up as a missing record. Prime
  Agent spawns each child with `name=<spawn_id>` so a reply pairs with its
  spawn the same way a Task result does on Claude Code. SPEC-0005 retires
  HANDBACK_CARRIES_EFFORT_AND_EXPERTISE_GAP and adds HANDBACK_STARTS_AT_STATUS
  and SPAWN_LOG_RECORDS_THE_ATTRIBUTION.
- **Smaller brief blocks.** The owner decided on 2026-11-03 to rewrite the
  blocks every brief carries compactly. The GRAPH DISCIPLINE, COMPANION and
  HANDBACK blocks went from 6,014 to 3,354 bytes per brief with the same seven
  steps and the same fields minus the echoes; SPEC-0003 moves its
  byte-identity baseline to this commit. Each charter's handback section is now
  a two-line pointer in the instruction voice (7,476 to 4,820 bytes across the
  roster).
- **Each close-out fact has one home (ADR-0032).** The owner decided on
  2026-11-03 to keep the session record and stop writing the same account in
  several places. The delivery is written once, as the plant `changelog.md`
  entry, with a pointer line in `grill.md` §15 and in the chat. The record's
  "Open threads" becomes "Paused state", for a live operation stopped
  mid-flight; progress and the next action stay in `grill.md` §15/§14, which a
  session now reads first when it resumes. Owner rules, corrected assumptions,
  harness migration and canonize status stay in the record, which every T2/T3
  unit still opens.
- **The seed's gate costs a third less CPU.** A profile of every step
  found the gate CPU-bound throughout: 5,748 Python runs and hundreds of
  installs, with shell tools costing next to nothing. The runner now gives
  CPU-bound work one token per core. It measures each step's CPU against its
  wall time into a cache outside the seed, and it starts the longest steps
  first. The install-heavy suites build each base install once and copy it.
  Cases that share a setup are folded together, and three suites stopped
  copying git-ignored files into their seed copies. Every changed case was
  first seen failing against a planted bug. `install.sh` starts its Python
  with `-S` and places files without a `dirname` subshell. All of a run's
  temporary files sit under one `*.noindex` directory, which Spotlight skips.
  On an M2 the full gate went from about 230 s of wall time and 1,280 CPU-s
  to 157 s and 855 CPU-s.
- **A graft catches the plan defects it introduces (`graft.gate.plans`).**
  `tools/graft-run.py` now runs the plant's `grill-lint.py` and
  `spec-lint.py` before the upgrade and again after it, and blocks on each
  defect that only the upgrade raised. In a live implementation run, this
  release's own press rule failed the grafted plant's existing plan: three
  unpressed `expensive` decisions and the top risk. The first work session met
  that failure at its gate and ran a planning press partway through
  implementation. On the same plant the graft now names those four items, so
  they go to the owner as numbered decisions before work starts.
- **Every session loads less.** An audit of each recurring instruction
  surface against both plants' trajectories cut what no agent acted on or what
  a tool now enforces. The kernel is 7,049 bytes (was 8,062): the role
  paragraph, the manual block-embedding instruction `brief.py` replaced and a
  map the FIRST MOVE already gives are gone; §4, the fresh-worker and
  no-orchestrator clauses and every lint-pinned anchor stay. The Prime Agent
  overlay is 3,332 bytes (was 5,182): its restatement of the kernel, a
  close-out section `skill.toolcraft` and `method.stewardship-posture` own,
  and the unused `goal`/heartbeat lines are gone. Every-session load is now
  24,207 bytes on Claude Code (8.2.0: 25,791) and 18,466 on Prime Agent
  (21,799).
- **`grill-planner` folds into `protocol.grill`.** Every rule the skill
  stated already had a home: append-only (kernel §3.3), stable section
  numbers and `[verify]` (grill-lint), increment shape and the press
  (`grill.increment-shape`, `grill.press`), the row discipline (the
  template). Only its consistency audit was its own, and that is now
  `grill.audit` in the protocol. Planning loads one node where it loaded two,
  and every session's always-loaded skill list is 454 bytes shorter. On the
  next graft, `install.sh --check` names a plant's copy RETIRED and graft
  migration (d) deletes it.
- **The release sweep for donor tokens fails closed.** A devil's-advocate
  press of the 8.2.0 plan's top risk, a project-identifying token reaching a
  seed file, returned `refuted`. Without the steward's local forbid list the
  gate step printed SKIPPED, exited 0 and was reported as PASS, so a
  checkout without the list checked nothing; file names were never scanned;
  and the release's "git status is empty" step invited committing local
  archives. `prepare-release.py` now refuses without the list and sweeps
  tracked and untracked-not-ignored files and their path names before it
  stages anything. The gate runner reports a skipped step as SKIP and counts
  it apart. The release procedure stages paths by name and keeps local
  evidence in `.git/info/exclude`.
- **A change to a trust surface takes one security pass
  (`test-first.security-path`).** A `crosscut` node may carry `trust: true`
  and claim paths, by its `repo:` or a file pattern in `load_when`, as the
  router's path tier reads them; `graph-lint.py --trust-claims PATH...` names
  the claims. When an increment writes under such a path, or §9 labels one of
  its contracts `security`, the session spawns `security` once after the
  reviewer, whatever the reviewer rated. The brief `brief.py --role security`
  composes carries the SECURITY PATH block byte for byte: a second path around
  a disabled action, a static rule evaded by alias, helper, factory,
  string-built name or comment, an unpinned value where one value is allowed,
  and line terminators other than `\n`. Every reviewer finding on the covered
  files goes with it. Its findings go to one fixer and one light re-check by
  `security`: one round, no loop. SPEC-0005 adds
  TRUST_PATH_TAKES_THE_SECURITY_PASS.
- **Graft and grow settle the trust marker.** `graph-lint.py
  --trust-unsettled` lists each crosscut node with no `trust:` field and each
  `trust: true` crosscut that claims no path, and the plain lint warns on the
  second. `tools/graft-run.py` prints them as judgment items before the gate
  table; the graft's Phase 8 entry and grow's delivery name each one left open
  and put it to the owner as a numbered decision. SPEC-0005 adds
  TRUST_MARKER_IS_SETTLED.
- **A repository nested in the plant claims its directory.** A subsystem
  whose `repo:` names a git directory inside the plant was never entered by a
  path: in a live run the app's one subsystem node, which owned its change
  flow, loaded only by lexical luck. `source_paths.repo_claim` now reads a
  nested repository as a folder, in the router and in `anchors` alike; the
  plant root still claims nothing. SPEC-0007's X459 arm and SPEC-0002
  GRAPH_ROUTE_NAMED_PATH_LOADS_ITS_OWNER follow. The other two routing defects
  that run found, a long-task notice a composed brief dropped and a library
  pin read as a path, live in brief machinery this release does not carry.
- **A test judged wrong goes straight to the tester.** A failing test judged
  wrong now goes to a fresh `tester` with the failure and the reason, ahead of
  any implementer fix round, because only a fix to the test makes it right
  (`delegation.green-self-test`).
- **One implementer builds the whole increment.** The cheapest measured run
  had one implementer build a whole increment in one warm cache.
  `protocol.test-first`'s GREEN now says the implementer keeps its context
  warm for the whole increment: a fresh worker taking over mid-increment re-reads
  the same code and writes it to the cache again, and a cache write costs about
  40 cache reads.
- **Security contracts carry adversarial RED controls.** In an A/B of four
  implementer runs on a static-rule contract, all four passed the spec's four
  planted controls, and all four rules were evadable by an import alias, a
  helper or factory call, a string-built class name, and the allowed shape
  inside a comment. In earlier runs a disabled action stayed reachable by
  paths no test covered. The SECURITY PATH block is now its own node,
  `method.security-controls`, the one checklist: for each security contract,
  RED writes one negative control per evasion class (or "n/a: <why>") and one
  test per path to a gated action's effect, found from the effect's callers. `brief.py --role tester
  --security-path` carries it to RED, and the security pass confirms the
  controls. The tester charter and `skill.spec-author` point to it. SPEC-0005
  adds SECURITY_CONTRACTS_CARRY_ADVERSARIAL_RED_CONTROLS.
- **Each role always loads its core method nodes.** In the cheapest measured
  run no worker loaded a single `method.*` node: the router's path tier
  returned only the code's owner, and no charter required one. Each charter
  now names its core nodes in `always_loads:`, a key apart from `requires:`
  so no route changes (the implementer: engineering,
  design and contract posture, minimum-sufficient work, holistic editing and
  the security controls; every role's list is in the agents reference). On
  Claude Code `install.sh` composes `.claude/agents/<role>.md` as the charter
  followed by each node's body under `## Always loaded: <id>`, frontmatter
  stripped, in a fixed order, so the role's system prompt is the same on every
  spawn and its cache holds. The nodes stay the only home: the composed file is
  generated: growth-audit and graft-run accept a composed file that begins
  with its charter, and `install.sh claude-code --check` names one whose
  composition drifted. Other
  hosts place the charter as before. SPEC-0005 adds
  ROLE_AGENT_COMPOSES_ITS_ALWAYS_LOADED_NODES.
- **A graft no longer calls a new seed node re-created.** Grafting a plant on
  8.2.0 onto this release, `graft.gate.recreated-nodes` named three nodes the
  seed added since the base as re-created deletions and blocked the gate.
  `tools/graft-run.py` now leaves out each node the ledger classes SEED-NEW.
  SPEC-0001 adds GRAFT_RUN_RECREATED_LEAVES_OUT_SEED_NEW.
- **A graft keeps the files the plant edited.** The same graft replaced
  `method/tiers.md`, which both the plant and the seed had changed, and the
  plant's legal corpus index, losing 16 plant rows, while the customization
  and rootstock rows passed. `install.sh --keep-diverged` now leaves as the
  plant's each file `tools/graft-ledger.py` classes KEEP-PLANT or MERGE;
  `graft-run.py` installs that way, and its `graft.gate.kept-deltas` row
  blocks on a replaced file, naming its backup, and on a MERGE that lacks a
  line the seed added. SPEC-0001 adds INSTALL_KEEPS_DIVERGED_MACHINERY.
- **A STALE composed agent has a remedy that keeps the node.** When a
  steward restored a kept or merged always-loaded node, `--check` called the
  composed agent STALE and told them to re-run the install, which
  fast-forwarded the node again. `install.sh claude-code --recompose-agents`
  rewrites `.claude/agents/` from the nodes on disk and nothing else; the
  STALE line and graft Phase 7 name it. SPEC-0005 adds
  AGENTS_RECOMPOSE_FROM_THE_NODES_ON_DISK.
- **The graft ledger rows a new hook file.** `.claude/resume-hook.py`, new in
  this release, got no ledger row in a plant that runs Claude Code, so the
  steward's table missed it. `tools/graft-ledger.py` now rows an adapter file
  the plant lacks as SEED-NEW when the plant carries the directory it goes
  into.
- **Growth puts an unsettled trust marker to the owner.** A crosscut a
  grower authored with no `trust:` stayed silent: plain graph-lint and
  growth-audit do not name it. `grow.gate.disclosure` now runs
  `graph-lint.py --trust-unsettled` as graft-run already does.
- **Graft and grow point at the new Claude Code machinery.** graft.md's
  projection-drift check said to `diff` each agent against its charter, which
  reports all 13 composed agents as drift; it now runs
  `install.sh claude-code --check`. graft.md, grow.md, INSTALL.md and the
  Claude Code README each point, in a line, at the `always_loads:`
  composition, the spawn log (`docs/graph/plans/spawns.jsonl`) and the resume
  hook where a steward or grower acts on them; seed-lint holds the pointers.
- **The reviewer names an overclaim.** A comment, label, doc string or test
  name that claims more than the code enforces is a finding on the
  reviewer's checklist (`reviewer.checklist`, Maintainability).
- **A handback files its evidence by kind.** `gates:` in the handback
  payload splits into compiled, executed (command and pass/fail counts),
  statically inspected, device-tested and deferred, so a green gate reads
  as what it ran. `brief.py` carries the block; test-brief holds the kinds.
- **A gated action's paths include every channel and state change.** The
  SECURITY PATH block counts every input channel (pointer, keyboard,
  assistive technology) and every state change between enabling and effect
  (resize, recreation) as a path that needs its own test.
- **The Claude Code main session plays the orchestrator.** The main session
  is no subagent, so `.claude/agents/00-orchestrator.md` and its
  `always_loads:` never reached it: in a live A/B run the session spawned five
  ruling passes where the charter's nodes allow one (about $4.10 of $31.94).
  `install.sh claude-code` now places the orchestrator's composition as the
  project output style `.claude/output-styles/orchestrator.md`, and
  `settings.json` selects it. An output style with `keep-coding-instructions:
  true` adds to Claude Code's own prompt and CLAUDE.md still loads, where the
  `agent` setting or `--agent` would replace the default prompt. `--check`
  names a drifted style and `--recompose-agents` rewrites it. A `claude -p`
  probe in a fresh plant quoted the charter's second sentence and an
  always-loaded heading, and quoted neither with the setting removed. Every
  Claude Code session now loads 69,117 bytes, recorded in `EAGER_EXEMPTIONS`.
  SPEC-0005 adds MAIN_SESSION_PLAYS_THE_ORCHESTRATOR.
- **Review findings on a trust path are fixed in the security pass.** In
  the same run a reviewer's trust-path findings went to their own RED and
  GREEN round while the security pass over those files was still owed:
  about $4.40, of which an estimated $2.50 bought a second round on the same
  surface. `protocol.test-first` now holds those findings for the security
  pass, whose one implementer fixes them with its own; when the RED predates
  the security path, the security spawn writes the missing controls.
- **A worker's route leaves out its own prompt and names missing
  expertise.** In the same run the implementer's task line, "make the
  increment tests pass (GREEN)", routed its own charter and holistic editing,
  both already in its system prompt, and no expertise node; it loaded its
  stack's expertise at call 143, after the code was written.
  `graph-lint.py --plan TASK --role R` now leaves out R's charter and its
  `always_loads:`, the bootstrap block's step 1 passes `--role` (the six brief
  templates carry it byte-identical), and `brief.py` tells the caller when the
  task line routes no `expertise.*` or `subsystem.*` node. SPEC-0005 adds
  PLAN_ROLE_LEAVES_OUT_THE_ROLES_OWN_PROMPT and
  BRIEF_WARNS_ON_A_ROUTE_WITHOUT_EXPERTISE.
- **The reviewer runs no build.** In the same run the reviewer built a
  simulation project and ran the full build itself; a ten-minute build
  let its prompt cache expire, and the rewrite cost $0.91 of the review's
  $4.13. The reviewer charter now reviews the diff and the gate evidence the
  builder reports, names a doubted gate as a finding with the run to make, and
  probes a bypass by its callers or in a scratch script. SPEC-0005 adds
  REVIEWER_RUNS_NO_BUILD.
- **`brief.py --charter` is for Prime Agent.** In the same run every brief
  repeated the charter the Claude Code agent type already loads, about 2,300
  tokens a worker. `brief.py` now refuses `--charter` in a plant whose
  `.claude/agents/` carries the roles and that has no `.prime/agent/`.
  SPEC-0005 adds CHARTER_FLAG_ONLY_FOR_PRIME_AGENT.
- **The bound hook reads a heredoc body as data.** In the same run
  `.claude/bound-hook.py` refused a command that wrote a brief through a
  heredoc, because a line of the brief began with "make". The hook now blanks
  each heredoc body before it looks for commands, and still checks the
  command line that opens the heredoc and every command after it
  (`tests/test-bound-hook.sh`, three cases, seen red first).
- **Each role composes only what it needs.** A composed agent carried
  whole nodes, so the implementer's system prompt cost about 16K tokens on
  each of about 180 calls an increment (about $1.60 an increment across the
  roles). The composition now drops each node's Neighbours section and any
  section marked `<!-- reference-only -->` (holistic editing's reference
  list), and an `always_loads:` entry `<id>#<n>,<n>` composes only those
  numbered sections. The implementer keeps engineering posture §1, 2, 4, 9
  and 12 (specs, tests, minimum context, integration, side effects) and design
  posture §2, 5, 6, 7, 10 and 11, and drops engineering §3, 8, 10 and 11
  (choosing late, structure's rent, the next maintainer, boring production
  path) and design §1, 3, 4 and 9 (smallest structure, cohesion, stable
  contracts, seams). The tester keeps the same engineering sections. Contract
  posture, minimum-sufficient work, holistic editing and the security
  controls stay whole, and every other role keeps whole nodes without their
  Neighbours. The implementer goes from 65,798 to 54,891 bytes (about 16.4K to
  13.7K tokens), the tester from 47,378 to 41,299, and the others shrink by
  2 to 5%. The Claude Code every-session load is 67,148 bytes. SPEC-0005 adds
  ALWAYS_LOADS_COMPOSES_ONLY_WHAT_THE_ROLE_NEEDS.
- **A trust-path review names the security pass.** In a live run an
  increment's diff touched eight files its trust crosscut claims, and the
  session never spawned `security`: nothing mechanical said the pass was owed.
  `brief.py --role reviewer` now checks the changed files (uncommitted, in the
  plant and each repository under it) and the files the task part names with
  `graph-lint.py --trust-claims`, prints `SECURITY PASS REQUIRED after this
  review: <files>`, and logs them; `brief.py --log` exits 1 with a BLOCK line
  until a `security` spawn follows that review. SPEC-0005 adds
  REVIEW_BRIEF_NAMES_THE_SECURITY_PASS (X503).
- **Each spawn's effort follows its role and task kind.** The owner decided
  on 2026-11-09 that effort varies within a role by the kind and size of the
  task, pending measurement in the next A/B arm. `delegation.effort` holds a
  role and task kind table (an implementer's increment by its label, a fix
  set medium, a mechanical edit low; a tester's RED by label, a security or
  stateful RED high, one amended test low; a reviewer's first review medium,
  high on a trust surface, a re-check low; an architect's contract high, a
  ruling medium, wording low; the close-out librarian low; a product ruling
  low). `brief.py --kind KIND [--label LABEL]` derives the spawn's effort from
  it, prints `effort: <value> (<reason>)` and logs it, and the orchestrator
  passes it on every spawn: Claude Code takes it as the Agent tool's `effort`
  (v2.1.292+), Prime Agent as `thinking=`, which it already read from the
  brief. Agent frontmatter keeps its `effort:` as the role's default. The
  Claude Code every-session load is 67,131 bytes. SPEC-0005 adds
  BRIEF_DERIVES_THE_SPAWN_EFFORT (X502).
- **The implementer's effort is capped at medium, and a review-fix set runs
  at low.** The owner allowed the cap on 2026-11-09 if medium proved good
  enough. Replays measured a new flow's GREEN at 3/5 on low, 4/5 on medium and
  5/5 on high for 50% more cost, and a review-fix set at 4/5 on low ($1.19),
  4/5 on medium ($2.14) and 5/5 on high ($2.99). The implementer rows of
  `delegation.effort` become: an increment by its label but at most medium, a
  new flow and a trust-surface change medium, a fix set and a mechanical edit
  low. `brief.py` prints `capped at medium` when the cap applies; the other
  roles are unchanged.
- **A whole-increment GREEN defaults to low implementer effort; a hard
  increment runs at medium.** A delta replay of a whole increment with the
  implementer at low effort cost $8.17 against $12.68 at medium and graded
  17/24 against 14/24 by the same blind grader, while a single feature built
  alone dropped at low (3/5 against 4/5). The implementer's `increment` row
  of `delegation.effort` becomes low by default and medium when the hardest
  label is medium-hard or hard, still never above medium; flow and trust stay
  medium, fix and mechanical low (SPEC-0005, X502).
- **The implementer composes design posture whole again.** With design
  §1, 3, 4 and 9 (smallest structure, cohesion and coupling, stable contracts,
  variation at a seam) left out, the next run's implementer put every draft
  and send call into one shell-wide state holder and was graded down on
  architecture. The owner approved restoring them on 2026-11-09; the other
  section trims stand. The composed implementer is 58,769 bytes, and 59,273
  with the design note below.
- **The implementer writes a design note before coding a new flow.** For a
  new flow or a stateful contract it first names which component owns each
  piece of state (domain or authority, coordination or flow, presentation)
  and every transition (inputs and external events, rejection or failure,
  restart of the state holder, environment change) with its observable
  result, then codes to it; the reviewer checks the code against the note.
  Owner-approved on 2026-11-09 after a live run's architecture was graded
  down. SPEC-0005 adds IMPLEMENTER_WRITES_A_DESIGN_NOTE.
- **A test holds its evidence.** `skill.test-first`'s Test shape gains one
  rule: each path to an effect is tested, not one entry point; an assertion
  fails when its evidence is missing; assertions target the component under
  test; stateful behaviour is tested again after rebuilding the component
  that holds the state. Owner-approved on 2026-11-09. SPEC-0005 adds
  RED_TEST_HOLDS_ITS_EVIDENCE.
- **The reviewer checks domain and state, and platform correctness.** Its
  checklist gains Domain & state (one owner per piece of state, checked
  against the implementer's design note; every input, rejection and restart
  of the state holder with a defined result; stale or replayed actions
  rejected; the same behaviour for a fresh observer) and Platform correctness
  (lifecycle, concurrency and accessibility as the plant's expertise nodes
  define them). Its security section points at `method.security-controls` and
  the security pass that follows the review, and `security` leaves the
  reviewer's `delegates_to`. Owner-approved on 2026-11-09. SPEC-0005 adds
  REVIEWER_CHECKS_STATE_AND_PLATFORM.
- **A fix on a trust surface runs at low.** A measured run gave its
  follow-up and fix-round implementers medium effort because they touched a
  trust surface. Where several task kinds fit, `fix`, `mechanical` and
  `amend` now win over `trust` and `red-trust`, and `brief.py --kind
  trust,fix` reads low; a trust-surface GREEN stays medium (SPEC-0005, X502).
- **RED for a security pass's findings runs at medium.** A measured run's
  tester for those findings ran at high, since `--security-path` forced it.
  The tester gains a `findings` kind at medium that starts from the probe and
  control files the security pass wrote; `security` and a tester's RED of a
  security contract before GREEN stay high (SPEC-0005, X502).
- **A security pass's findings go to a tester, then an implementer.**
  `test-first.security-path` sent them to one implementer, which
  `delegation.green-self-test` keeps off test files. The route is now one
  tester writing their RED from the pass's probe and control files (medium),
  one implementer greening them (low), and the light `security` re-check.
  The security charter leaves its probe files in the tree and the tester
  charter starts from them (SPEC-0005, TRUST_PATH_TAKES_THE_SECURITY_PASS).
- **One low tester spawn after a ruling pass.** A measured run spent two
  tester spawns and medium effort around one ruling pass. A test change that
  follows a ruling is a tester `amend` (low); after the pass, one tester spawn
  carries all of its test amendments and the test questions held while it
  ran, and the implementer's follow-up is a `fix` (low)
  (`delegation.ruling-amendment`, SPEC-0005).
- **Implementing runs at low effort.** The owner decided on 2026-11-10 that
  every implementer kind (`flow`, `trust`, `fix`, `mechanical`) runs at low,
  and an `increment` at low unless its hardest label is hard, which runs at
  medium; the cap stays medium. The review, the high-effort security pass and
  the findings tester are the quality net for low-effort implementation
  (SPEC-0005, X502).
