# grill — bounded execution and estate standards (7.2.0)

Plan-of-record for one new mechanism and six doctrine sharpenings. The mechanism
is a guard hook that refuses an unbounded foreground command; the sharpenings are
estate standards mined from grown plants and from an operator's session history,
each folded into the node that **already owns** the fact it sharpens. No new node,
no kernel edit, no second home for anything the graph already reasons about.

Ratified items, executed in this order: **I0** portable in-place edit in the
graft-tools suite, **I1** bounded execution (hook + test + doctrine), **I2**
no-write / no-restart default, **I3** source of record then installer, **I4**
spec promotion gated on passing assertions, **I5** decision gate written before
the measurement, **I6** an inert setting announces itself. This file is I7.

Release shape: T2 against the seed itself — every increment is authorized by an
item above, and each is one node or one file.

## §1 Artifact discovery (all read, paths cited)

**Kernel and budget**

- `core/AGENTS.md` — 7 180 B of the 8 000-byte budget. Untouched this release; its
  §3.8 anchor is the only kernel handle on the toolcraft rule, and it already
  reaches the new doctrine through that pointer.
- `tests/seed-lint.py` — `KERNEL_BUDGET = 8_000` (L35, checked L208); globally
  unique `owns:` keys; `est_tokens` within 2x of the measured body (L295–L308);
  machinery-node frontmatter required on every protocol/skill/agent/method file.

**Nodes that receive the change**

- `protocols/toolcraft.md` (121 L, `est_tokens: 1000`) — owns `rule.toolcraft`
  and `toolcraft.durability-criteria`; §"Fail-closed doctrine" (L108) is where a
  delivered mechanism gets its one-line pointer. Home of the six bounded-execution
  clauses under one new key, `toolcraft.bounded-execution`; the clauses are
  summarised in one line everywhere else and restated nowhere.
- `protocols/verify.md` (475 L) — owns `rule.verify` plus ten keys. Two receive a
  sentence: §"A gate that found nothing has not yet said anything" (L115, key
  `verify.null-result`) and §"`closed` means evidenced" (L326, key
  `verify.status-evidence`).
- `core/method/release-posture.md` (179 L) — §5 "Land the reversible parts first;
  gate the one-way step on their evidence" (L135, key `release-posture.ordering`).
- `core/method/vcs-posture.md` (123 L) — §2 "Publishing is a separate
  authorization — MANDATE" (L49, key `vcs-posture.publish-authorization`); the
  bullet list of separately-authorized acts is extended, in the list's own voice.
- `core/method/engineering-posture.md` (374 L) — §1 "Specs are the contract; code
  is the implementation" (L36, key `engineering-posture.sources-of-truth`).
- `core/method/design-posture.md` (397 L) — key `design-posture.anti-patterns`;
  the anti-pattern paragraph at L226 (under §8, "A rule that restricts must not
  deny the default") is the nearest existing neighbour for the inert-setting rule.
  The concrete instance already documented in the seed is an adapter setting
  accepted in one scope and silently ignored in another (`integrations/*/README.md`).
- `core/method/tiers.md` (L30–L48) — the T0–T3 table and the two hard edges; the
  release is classified against it above.

**Mechanism surface**

- `integrations/claude-code/settings.json` — today two hooks, both fail-open by
  design: `UserPromptSubmit` → `route-hook.py`, `SessionStart` → `status-hook.py`,
  each suffixed `|| true` because they inject context and must never break a
  session. The new `PreToolUse` entry carries no `|| true`.
- `integrations/claude-code/route-hook.py`, `status-hook.py` — the stdin-JSON,
  exit-code shape the new hook copies.
- `integrations/claude-code/README.md` (80 L) — hook inventory and the
  per-session instruction budget; documents the fail-open/fail-closed asymmetry.
- `install.sh` L339–L343 — the hook copy block with its backup behaviour; the new
  file joins that block and nothing else changes in the installer.
- `integrations/codex/README.md` (94 L), `integrations/opencode/README.md`
  (127 L) — no hook surface exists in either, so the clauses are the agent's own
  discipline there: one paragraph each, pointing at `protocols/toolcraft.md`.

**Gates and harness**

- `tests/run.sh` — thirteen shell suites, then the graph-lint and agent-lint
  regressions, then `seed-lint.py` and `legal-lint.py`. Registration point for the
  new suite is immediately after `tests/test-full-install.sh` (L10–L11).
- `tests/test-full-install.sh` L59 — `need "$T/.claude/status-hook.py" claude-code`
  is the delivery-assertion pattern the new hook file follows.
- `tests/test-graft-tools.sh` L374 and L377 — BSD-only `sed -i ''`; on a GNU
  toolchain the empty string is read as the script and the file as a missing one.
  This is the standing RED in the baseline suite run.
- `templates/knowledge-graph/graph-lint.py` — the graph contract; `--plan "TASK"`
  dry-runs the context router and is the seed-side resolver used for routing diffs.
- `tools/agnosticism-lint.py` — `--root` / `--file` / `--forbid` (repeatable) /
  `--glob`; three objective classes (forbidden term, host-IP literal, pinned
  advisory). Its own docstring states the constraint that shapes §10.5: *a
  component cannot enumerate the names it must not contain without containing them*.
- `tools/prose-lint.py` — `--file` / `--against REV` / `--strict`; the mechanical
  floor under the prose doctrine, run on every edited node.
- `CLAUDE.md` — behavior change ⇒ `manifest.json` bump + `CHANGELOG.md` entry;
  `CHANGELOG.md` and `docs/decisions/` are append-only; everything else integrates.
- `manifest.json` L5 — `"version": "7.1.1"`, moving to 7.2.0 at close-out, which is
  a later wave and a different writer.

**Format precedent**

- `docs/plans/grill-operator-distilled-refinements.md` — the seed-side plan-of-record
  shape this file follows (stable section numbers, append-only §15).
- `skills/grill-planner/SKILL.md` — owns `grill-planner.method` and
  `grill-planner.audit`: append don't rewrite, section numbers are stable, one
  action in §14, every §9 row named with files and a gate.

## §6 Decisions

**D1 — The in-place edit in the graft-tools suite becomes toolchain-portable. (I0)**
Both call sites move to `sed -i.bak '<script>' "$file" && rm -f "$file.bak"`.
*Evidence:* the suite fails at that line on a GNU toolchain in the captured
baseline; the form is a proven fix, not a guess. *Reversible.*

**D2 — Bounded execution ships as a mechanism, not as doctrine alone. (I1)**
A `PreToolUse` hook on the shell tool reads the hook JSON on stdin, and exits 2 —
blocking the call — when a blocking-prone command carries neither a bound nor a
detached launch. *Evidence:* the class of fault the six clauses describe is a
runtime fault; doctrine that only an attentive reader applies does not reach it.
*Reversible: delete the settings entry and the file.*

**D3 — This is the one fail-closed hook; the existing hooks stay fail-open. (I1)**
The two shipped hooks inject context and carry `|| true`; a guard that cannot
block is documentation. The new entry omits `|| true`, and the asymmetry is stated
where a reader meets it, in the integration README. *Reversible.*

**D4 — The guard never crashes. (I1)** Any internal exception exits 0 with a
one-line note on stderr; only a positive match exits 2. *Evidence:* a fail-closed
hook is the one component whose own defect can end a session — see R2.
*Reversible.*

**D5 — The blocking-prone list is a commented constant, not a config surface. (I1)**
One entry per line with a comment saying why it hangs; extending it is a one-line
change. *Evidence:* a config surface for a list this small would be a dial nobody
turns, and a setting nobody sets is exactly the defect I6 legislates against.
*Reversible.*

**D6 — Exactly two accepted forms. (I1)** A bound (`timeout` preceding the first
matched token, after any leading directory change, environment assignments or
`nice`), or a detached launch that redirects output to a durable path and records
its pid. The stderr on a block shows both forms filled in for the offending
command, so the fix is copy-paste rather than recall. *Evidence:* clauses 1 and 2
name these two shapes and no third. *Reversible.*

**D7 — The six clauses have one home. (I1)** `protocols/toolcraft.md` gains the
new `owns:` key `toolcraft.bounded-execution` and one new section carrying them.
The fail-closed section gains one line naming the hook as the delivered mechanism;
the two adapters without a hook surface get one paragraph each that *points* at
the key. No copy of a clause exists anywhere else in the seed, including in this
plan. *Evidence:* `seed-lint.py` enforces globally unique `owns:`, and three
prose copies of one fact is the drift `owns:` exists to prevent. *Reversible.*

**D8 — No new node, and no kernel edit. (I0–I6)** A bounded-execution node would
compete for routing weight with the rule that already owns tool discipline; the
kernel is anchors and prohibitions, and the mechanism enforces this one at the
tool boundary, so kernel rent buys nothing. *Irreversible-ish: moving either
decision later costs a kernel edit and a routing re-measure.*

**D9 — Generation and recovery stage; they do not apply, and they never restart. (I2)**
One paragraph under `release-posture.ordering` (no-write default, candidate written
as a separate full copy, source untouched, applying/promoting/activating as
distinct steps each with its own authorization and gate), and the
`vcs-posture.publish-authorization` list extended with restarting, reloading or
stopping a running service, killing a process the agent did not start, and
touching a workload serving live traffic. *Reversible: two contained reverts.*

**D10 — The source of record is edited; the target is reached through the
installer. (I3)** One paragraph under `engineering-posture.sources-of-truth`: an
installed, generated or deployed file is never edited in place, and an edit made
only on the target is lost on the next rebuild and a second source of truth until
then. *Evidence:* the node already owns "which artifact is authoritative"; this is
that fact applied to a target that is downstream of a build. *Reversible.*

**D11 — A live status over an empty assertion set is a false green. (I4)** One
sentence under `verify.status-evidence`: promotion waits on executable assertions
that exist and pass, and lands in the same change that adds them. *Reversible.*

**D12 — The criterion is written before the measurement runs. (I5)** One sentence
under `verify.null-result`: a result that fails the pre-written criterion is a
recorded negative and the change is reverted, never rationalised into a partial
success. *Evidence:* the section already owns what a gate's silence means; this
fixes *when* the meaning is fixed. *Reversible.*

**D13 — An inert setting announces itself. (I6)** One sentence beside the
best-fitting existing anti-pattern under `design-posture.anti-patterns`: an
accepted-but-inert setting, parameter or code path announces itself where it is
accepted, or is documented as dead — otherwise it is indistinguishable from a
working one. *Reversible.*

**D14 — Every sentence sharpens a fact its node already owns; it points, it does
not restate. (I2–I6)** No `load_when:` phrase and no title is touched, so the
router sees no new weight from these five edits; `est_tokens` is re-measured, not
guessed, on every edited node. *Evidence:* `load_when:` and titles are the router's
inputs, and the routing gate in §10.7 is only interpretable if they hold still.
*Reversible.*

**D15 — Version 7.2.0, a minor bump. (release)** One new fact key, one new
mechanism with its own suite, five sharpenings, one portability fix: additive
capability, not a fix release. Version strings and the changelog entry belong to
the close-out wave, not to wave 1. *Reversible.*

**D16 — The new suite is committed RED, against the absent hook, before the hook
exists. (I1)** *Evidence:* a gate that never went red has not been shown to test
anything — the seed's own `verify` doctrine, applied to the seed. *Reversible.*

## §7 Options considered and discarded

- **A new `protocols/bounded-execution.md` node.** Discarded per D8: a command is
  a tool use, so the clauses are the toolcraft rule's own subject; a sibling node
  would duplicate its reasoning and compete with it in routing.
- **A kernel prohibition for the bound.** Discarded: the kernel's boundary section
  is a short list of hard prohibitions loaded on every session of every plant, and
  the hook enforces this one at the tool boundary, which is where it is violated.
  Kernel rent with no added enforcement is the accumulation the budget prevents.
- **A fail-open guard (`|| true`, or exit 0 with a warning).** Discarded per D3: a
  guard that only warns is a comment with a process cost.
- **Rewriting the command — injecting a bound automatically.** Discarded: a hook
  that edits what runs makes the agent's belief about the command and the command
  itself two different things. Blocking with both accepted forms on stderr keeps
  one source of truth and leaves the author in control of the bound.
- **An allowlist of safe commands instead of a blocking-prone list.** Discarded: a
  default-deny rule with no audited allow set is an anti-pattern
  `design-posture.anti-patterns` already names, and the failure mode — every
  ordinary command blocked on day one — is R1 at maximum severity.
- **A configurable pattern list.** Discarded per D5.
- **Restating the six clauses in each adapter README.** Discarded per D7: three
  copies, three drift paths, one `owns:` violation in spirit if not in lint.
- **A new estate-standards document collecting I2–I6.** Discarded: each of the five
  is a sharpening of a fact an existing node owns, and a collection document would
  be a second home for all five at once — the precise defect these five sentences
  are being written to prevent.
- **Bundling the portability fix into the mechanism increment.** Discarded: I0 has
  its own RED in the baseline and its own one-line revert; folding it in would
  make one increment's failure ambiguous between two causes.

## §9 Implementation waves

### Single-writer file ownership, wave 1

Nobody writes a file another worker owns. A worker that needs one hands back.
Model class is set by the brief (`delegation.model-classes`); it is not a seed
fact and is not recorded here.

| worker | owns (nobody else writes these) |
|---|---|
| `planner` | `docs/plans/grill-7.2.0-bounded-execution-and-estate-standards.md` |
| `hook-worker` | `tests/test-graft-tools.sh`, `integrations/claude-code/bound-hook.py`, `integrations/claude-code/settings.json`, `integrations/claude-code/README.md`, `tests/test-bound-hook.sh`, `tests/run.sh`, `tests/test-full-install.sh`, `install.sh`, `protocols/toolcraft.md`, `integrations/codex/README.md`, `integrations/opencode/README.md` |
| `doctrine-worker` | `protocols/verify.md`, `core/method/release-posture.md`, `core/method/vcs-posture.md`, `core/method/design-posture.md`, `core/method/engineering-posture.md` |

Locked in wave 1, reserved for the close-out worker in wave 2: `core/AGENTS.md`,
`manifest.json`, `CHANGELOG.md`, `DOCUMENTATION.md`, `documentation/`, `README.md`.

### Wave 1 — increments

| # | Increment | Files touched | Fact | Gate |
|---|---|---|---|---|
| I0 | Toolchain-portable in-place edit | `tests/test-graft-tools.sh` (L374, L377) | none | the suite, RED in baseline → GREEN |
| I1a | Suite first, proven RED | `tests/test-bound-hook.sh` (new), `tests/run.sh` | none | new suite fails with no hook present |
| I1b | The guard | `integrations/claude-code/bound-hook.py` (new), `.../settings.json` | none | new suite GREEN; every case's exit code asserted |
| I1c | Delivery | `install.sh`, `tests/test-full-install.sh` | none | `test-full-install.sh`, RED against the un-wired installer first |
| I1d | Doctrine | `protocols/toolcraft.md` | `toolcraft.bounded-execution` (new) | seed-lint (unique `owns:`, `est_tokens` 2x), graph-lint, prose-lint |
| I1e | No-hook-surface adapters | `integrations/{claude-code,codex,opencode}/README.md` | none (pointer prose) | seed-lint per-session instruction budget |
| I2 | Stage, don't apply; don't restart | `core/method/release-posture.md`, `core/method/vcs-posture.md` | extends `release-posture.ordering`, `vcs-posture.publish-authorization` | seed-lint, graph-lint, prose-lint |
| I3 | Source of record, then installer | `core/method/engineering-posture.md` | extends `engineering-posture.sources-of-truth` | seed-lint, graph-lint, prose-lint |
| I4 | Promotion needs passing assertions | `protocols/verify.md` | extends `verify.status-evidence` | seed-lint, graph-lint, prose-lint |
| I5 | Criterion before measurement | `protocols/verify.md` | extends `verify.null-result` | seed-lint, graph-lint, prose-lint |
| I6 | An inert setting announces itself | `core/method/design-posture.md` | extends `design-posture.anti-patterns` | seed-lint, graph-lint, prose-lint |
| I7 | This plan | this file | none | agnosticism-lint, prose-lint |

I4 and I5 land in one file under one writer; they are separate rows because they
sharpen two different keys and revert independently.

**Rollback.** I0 and I2–I6 are each a contained edit to one node — restore the
file. I1 rolls back as a set: delete the hook file, the suite, the two
registration lines, the installer lines and the `settings.json` entry, and
restore `protocols/toolcraft.md`; nothing else in the seed depends on any of them.

### Wave 2 — close-out and adversarial review

Gates in §10 run in full before the close-out worker starts. That worker then
owns the changelog entry, the version strings, and the integration README where
the hook set is listed, under the seed's append-only convention. A read-only
adversarial pass reviews the diff against this plan: every sentence lands under
the named key, nothing restates a fact owned elsewhere, no pattern fires on a
command the seed's own suites run, and the suite covers every accepted form.
Findings return to the author, who fixes or hands back.

### Wave 3 — pilot graft and independent review

The seed installs into one already-grown plant chosen for one property: it is a
version-controlled tree with the graph already installed, so the revert path
exists and `git diff --stat` is the verification instrument. Verification is item
by item: every listed file present, lint green, a sample of `load_when:` phrases
resolving to the intended nodes, and no runtime file touched. Nothing is
committed. A separate review, by an agent that has not read this session, tests
the release's headline claim against the seed diff; the author does not open it.

## §10 Verification plan

1. `bash tests/run.sh` — green, end to end, with any SKIP named explicitly rather
   than absorbed. The baseline for this release is the suite failing at the
   graft-tools in-place edit, so a green run is also I0's evidence.
2. **RED before GREEN, `tests/test-bound-hook.sh`.** The suite is written and
   registered first and run with no hook file present; that failure is recorded.
   Only then does the hook appear, and the same suite is re-run green. Every case
   asserts an exit code against JSON fed on stdin: a bare service-control command
   blocks; the same command with a bound passes; a bare installer blocks; the same
   installer behind a directory change and a bound passes; a pattern-matching kill
   blocks while a kill by recorded pid or by literal pid passes; a detached launch
   that redirects to a log and records its pid passes; an ordinary listing passes;
   a non-shell tool name carrying a matching command string passes; garbage on
   stdin exits 0; and a block's stderr names **both** accepted forms.
3. `python3 tests/seed-lint.py` — the new `owns:` key globally unique; `est_tokens`
   within 2x of the measured body on every node touched, re-measured rather than
   carried forward; machinery-node frontmatter intact; the per-session instruction
   budget of the integrations still met after the adapter paragraphs.
4. `python3 templates/knowledge-graph/graph-lint.py` on a fresh install — no
   duplicate facts, no broken `requires:` edges, the new key resolvable.
5. `python3 tools/agnosticism-lint.py` over the diff, with `--forbid` repeated for
   every plant and host token the adopting tree supplies. Those tokens are passed
   on the command line and are never written into the seed or into this plan: a
   component that enumerated the names it must not contain would contain them, and
   the file you are reading would fail the lint it is prescribing.
6. `python3 tools/prose-lint.py --file` on every edited node, and on this plan.
7. **Routing diff.** The unchanged baseline installs into one scratch tree and the
   candidate into another; every trigger of both graphs is resolved
   (`graph-lint.py --plan` is the seed-side resolver) and the two result sets are
   compared. Baseline: 231 triggers. Accept only additive loads on the apt route.
   Any displaced route is either reworded until it stops displacing, or recorded
   in §15 as a deliberate sharpening with the route it replaced. The differ itself
   is release-harness machinery and is not shipped in the seed.
8. **Kernel byte budget.** `core/AGENTS.md` stays at **7 180 bytes of the 8 000**
   budget — unchanged, because no item in this release edits it. Enforced by §10.3;
   asserted here so a silent kernel edit cannot pass as incidental.
9. **False-positive sweep.** The hook is run against the shell command lines the
   seed's own suites and installer issue, and against a sample of ordinary
   read-only commands. Any block on one of them is a defect in the pattern list,
   not a finding about the command.

## §11 Risks

**R1 — The hook blocks ordinary commands.** *Medium / high.* A word-anchored
pattern that fires on a substring, or a bound the matcher fails to see because it
sits behind an environment assignment, turns the guard into an obstacle and the
first response will be to remove it. *Mitigation:* the accepted-form matcher
tolerates a leading directory change, environment assignments and a niceness
prefix before the bound; §10.9 sweeps the seed's own command surface; the suite
pins the passing cases, not only the blocking ones, so a later pattern addition
that over-fires goes red. *If a real command cannot be expressed in either
accepted form, the pattern is narrowed — the clause is not weakened.*

**R2 — The guard crashes and takes the session with it.** *Low / critical.* It is
the one hook without `|| true`, so an unhandled exception is a non-zero exit and a
blocked tool call on every command. *Mitigation:* D4 — the whole body is wrapped;
any internal exception exits 0 with a single stderr line, and only a positive
match exits 2. The suite's garbage-stdin case and its non-shell-tool case exercise
that path directly.

**R3 — A doctrine sentence restates a fact owned elsewhere.** *Medium / medium.*
Five sentences across four nodes, each near a neighbour that already says
something adjacent; `seed-lint.py` catches a key *collision*, never a semantic
*overlap*. *Mitigation:* each sentence is placed under a named key by this plan,
not chosen at writing time; the drafting rule is point, don't restate; the
adversarial pass in wave 2 reads for exactly this and can hand back a sentence.

**R4 — New phrases drift the router.** *Medium / medium.* New prose changes term
frequencies even when no `load_when:` phrase is added, and a common word gaining
weight can pull an unrelated node into an existing route. *Mitigation:* D14 holds
`load_when:` and titles still; §10.7 compares all 231 baseline triggers against the
candidate; a displacement is reworded, and only a displacement judged a genuine
improvement survives, recorded in §15 with the route it replaced.

**R5 — `est_tokens` drift.** *High / low.* Every edited node grows, and the
frontmatter number is the router's cost input; a stale one is a quiet lie that
compounds across releases. *Mitigation:* re-measured on every touched node, never
adjusted by eye; `seed-lint.py` enforces the 2x band, and the largest growth this
release — the new toolcraft section — is the one most likely to leave it.

## §13 Done criteria

- I0 and I1–I6 present in their mapped owners, each reading as though it had
  always been there: no appended block, no duplicated fact, no orphan section.
- Exactly one new `owns:` key, `toolcraft.bounded-execution`, owned in one file;
  the six clauses stated once in the seed and pointed at from everywhere else.
- `tests/test-bound-hook.sh` proven RED against the absent hook, then GREEN,
  with both results recorded.
- `bash tests/run.sh` green, every SKIP named.
- seed-lint, graph-lint, prose-lint clean; agnosticism-lint clean with the full
  forbidden-token set supplied by the adopting tree.
- Routing diff recorded: additive loads only, or a residual explained in §15.
- Kernel unchanged at 7 180 bytes of 8 000.
- `est_tokens` re-measured on every edited node.
- Nothing plant-, host- or operator-identifying anywhere in the diff, and no
  count that fingerprints one.
- Version and changelog handled in wave 2 by their own writer, append-only.

## §14 Recommended next step

Execute I0 and I1a — the portable in-place edit, then commit `tests/test-bound-hook.sh`
and record it failing against the absent hook — before any other line of this
release is written.

## §15 Changelog

- 2026-09-07 — plan created. Seven items scoped (I0–I6 ratified, this file I7);
  one new fact key decided (`toolcraft.bounded-execution`, D7), no new node and no
  kernel edit (D8), the guard alone made fail-closed while every other hook stays
  fail-open (D3), the pattern list kept a commented constant rather than a config
  surface (D5), and the suite ordered RED-before-GREEN against the absent hook
  (D16). Single-writer ownership fixed for wave 1: three workers, no shared file.
- 2026-09-07 — I2's owning key corrected from `release-posture.rollout` to `release-posture.ordering`: the paragraph lands in §5 (reversible parts first), which the node maps to `ordering`; §6 (`rollout`) is per-target order and was never the intent. Wave 1 landed I0–I6; the guard test was proven RED then GREEN.
- 2026-09-07 — close-out gates: `tests/run.sh` green; seed-lint PASS; agnosticism lint PASS over the 17 changed files with nine forbidden terms (one pre-existing host path in `documentation/` found and replaced); routing diff against a baseline install of the previous version: 231 triggers, 0 routes changed; the one new `load_when` phrase on `protocol.toolcraft` (the stuck-command case) is additive and deliberate; kernel 7 180 B unchanged; `prose-lint` on `protocols/toolcraft.md` reports the seed's house dash rate, which fell from 34.3 to 25.3 per 1 000 words with this change and is not gated for protocols. Version 7.2.0 in manifest and documentation.
- 2026-09-07 — adversarial review: a bare `make` (no target) passed the guard because its pattern required a trailing space; fixed to a word boundary, with bare/bound test pairs added for every pattern in the table and for the `nohup`-only and `setsid`-only detached forms; `apt` no longer fires on `apt-cache`/`apt-mark`. The no-write paragraph in release posture now points at the design posture's report-only default as its neighbour. `prose-lint` reports the same house dash rate on all six edited nodes as at the previous version; it is not a gate for doctrine nodes.
- 2026-09-07 — I3 (source of record, then installer) reverted from `core/method/engineering-posture.md` pending re-ratification: the plant-artifact evidence cited for it counted one plant three times; the rule rests on two plants plus the operator's session history. The independent review also found six host paths in `docs/plans/scout-0*.md`; replaced with placeholders.
- 2026-09-07 — independent review of the guard: `bash -c` / `sh -c` / `eval` payloads and a pipe into a shell walked through; read-only `systemctl` queries, `make -n` and a quoted `;` were refused. Fixed with tests first: wrappers are unwrapped and their payload inspected in place (a bound on the wrapper still counts), quoted strings are masked before separators and patterns are read, and status/show/is-active/dry-run forms are exempt.
- 2026-09-07 — I2: the clause "defaults to a no-write mode" restated the design posture's report-only default (one home per fact); removed, the paragraph now points at that owner and keeps only the release-side steps.
- 2026-09-08 — 7.2.1 follow-up, owner's rulings: (1) I3 re-ratified on its corrected evidence (two plants plus the operator's session history, the seed owner already existing) and re-applied under `engineering-posture.sources-of-truth`. (2) The exclusive-lock theme is rejected for the seed as project-specific; it stays in the operator layer. (3) `graph-lint.py`'s version-pin rule read a specification revision (`SPEC-0002 v0.2.0`) as a dependency pin; a project-artifact identifier directly before the token now exempts it, test first. (4) The four plant facts become an explicit owner choice at install, growth and graft time: `install.sh` gains `--environment-class`, `--commit-attribution`, `--deliverable-language`, `--comment-language`, fills placeholders only, refuses an unknown class, and names unset facts as a NEXT STEP; the install and graft prompts ask for them before running; growth already did (`grow.plant-facts`). Tests: `test_graph_lint.py` spec-revision case, `test-full-install.sh` plant-facts block, both red first.

