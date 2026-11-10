<!-- The owner decisions T1 to T11 of `docs/plans/grill-8.3.1-token-efficiency.md`; its §12 row 7 points here. Kept beside the plan, outside its increment directory, which holds only §9 increments. -->

# Owner decisions T1 to T11: levers that need a trial

The owner's brief of 2026-11-10 asks for each of these to be prepared, not landed: each changes what the method asks of a model, or a default the owner set. Each note gives the proposal, the mechanism it relies on today (path and line at this round's tip), the quality risk against the safeguards the brief's section 9 names, the trial that would decide it, how its cost is read, and a recommendation. No note claims a saving.

**What every trial shares.** Each follows `skill.lever-trial` (`docs/skills/lever-trial.md`): arm A is today's setting and arm B the proposal; the fixed task set of `lever-trial.design` step 2; the run count, interleaving, rubric and blind grader of steps 3 to 5; the measures of `lever-trial.measures` (review and security findings per increment, red full-suite runs, mutation score where a pass runs, escaped findings, rubric score); a margin agreed before the first run; and the fail-closed verdict of `lever-trial.verdict`. Each note names only what differs.

**How the cost is read.** For each spawn of a run, after it hands back, the owner runs `python3 docs/graph/brief.py --tokens <spawn_id> --transcript PATH` (or `--usage FILE`); `brief.py --log` then prints the Spawns and Tokens lines. The ledger is keyed by `spawn_id`, so the lead's own turns are outside it: for a lever on the lead (T3, T6, T7, T8), the owner also records the session's host-reported usage per run (`claude -p ... --output-format json` returns a `usage` object; an OpenTelemetry export reports tokens per session) beside the run's evidence.

## T1. A contained T2 fix closes without a docs-librarian spawn unless a graph node must change

- **Proposal.** When a contained-lane fix changes no graph node (no fact, deviation, status move or tool), the session writes the why-record line in `changelog.md` itself and records "canonize: no graph node changes, because ..." in the delivery; any node change still spawns the librarian.
- **Relies on.** One librarian spawn per T2/T3 task (`protocols/canonize.md:52-62`); the T0/T1 self-record (`canonize.md:79-83`); `changelog.md` is already the session's own artifact (`canonize.md:64-70`); the why-record duty (`canonize.md:202-212`).
- **Quality risk.** No section 9 safeguard sits on this path. The nearest is the independent first review: the librarian is the one reader besides the author who walks the session record and the status register and asks why (`canonize.md:163-174`, `186-189`). If the session misjudges "no node changes", a corrected assumption or a status move stays in the transcript, and a fix that needed a spec loses its reclassification check (`canonize.md:209-211`).
- **Trial.** Lever: the close-out spawn on contained fixes. Tasks: the contained fix, plus a second contained fix built to surface one graph fact. Added measure: facts the grader finds in the transcript that the arm's graph lacks.
- **Cost.** The docs-librarian `close-out` records in arm A against the lead's added turns in arm B.
- **Recommendation.** Adopt only if the trial shows arm B places the planted fact in every run; otherwise keep the spawn.

## T2. A review finding that came with a failing test closes by the tip run, without a re-check spawn

- **Proposal.** When a separate tester wrote the failing test that pins a review finding, and its hash is in the batch record, the fix closes when the batch-tip run turns that test green with the hash unchanged; the light reviewer re-check is left out. Security findings keep their light security re-check.
- **Relies on.** The REVIEW row and COMMIT step 1, which spawn a fresh light reviewer on the fix diff (`protocols/test-first.md:111`, `235-238`); the security row's re-check (`test-first.md:112`); RED hashes and the expected-red list held by `tools/cycle.py` (`core/method/delegation-cycle-economy.md:102-106`); the reviewer `recheck` row (`core/method/delegation-model-classes.md:136`).
- **Quality risk.** Closest to the independent first review. A green test proves the finding's behaviour, not that the fix stayed inside its hunks or left no stitch (`agents/03-reviewer.md:97-115`). What escapes: scope creep in the fix, a second defect it introduced, a test green for the wrong reason.
- **Trial.** Lever: the re-check after a test-pinned fix. Tasks: the covered-lane change and the new flow, where findings arise; the trust-path change as a control on which both arms keep the security re-check. Added measure: defects in fix diffs that a later review or the grader traces back.
- **Cost.** The reviewer `recheck` records.
- **Recommendation.** Adopt after a trial, scoped to non-security findings with a tester-written RED, and keep the re-check whenever the fix diff touches lines outside the finding's hunks, a condition `cycle.py` could check from git.

## T3. A declarative edit proved by a recorded run stays in-session when it is one file, reversible, off every trust path and under no spec

- **Proposal.** Such an edit (a selector, a pipeline stage, a flag) is written by the session, as a T1 edit is, in place of an implementer spawn; the recorded run, the why-record and the independent review stay.
- **Relies on.** T1, the one in-session authoring exception (`core/method/tiers.md:42`; `agents/00-orchestrator.md:119-121`); proof by a recorded run (`tiers.md:54-56`; `protocols/test-first.md:45-47`); the contained lane's entry conditions and its review (`tiers.md:58-71`, `80`).
- **Quality risk.** Closest to worker preconditions and the duty to refuse, which bind a worker and not the lead, and to the independent first review, which must then come from a reviewer spawn rather than the lead's reading of its own edit. The author also judges "off every trust path". What escapes: a declarative edit that crosses a trust path (a flag gating authentication), or a run recorded against the wrong environment.
- **Trial.** Lever: who authors a declarative contained edit. Tasks: a declarative contained fix, plus a flag that gates an authentication surface as a control that arm B must route out. Added measure: misrouted controls per run.
- **Cost.** The implementer `mechanical` records in arm A against the lead's session usage in arm B, read over the whole session, since the lead pays its added context on every later turn.
- **Recommendation.** Adopt only if arm B routes the control out in every run and review findings stay inside the margin.

## T4. The first review scales to the increment's effort label

- **Proposal.** A first review of a `low` or `medium-low` increment runs at low effort, `medium` and above at medium; a trust-surface first review stays `first-trust` at high.
- **Relies on.** The reviewer rows and the by-label rule (`core/method/delegation-model-classes.md:113-121`, `134-136`), read by `brief.py --role reviewer --kind first --label L`; the labels of `delegation.effort-scale` (`core/method/delegation-cycle-economy.md:57-68`); the checklist (`agents/03-reviewer.md:93-95`).
- **Quality risk.** The independent first review itself: its independence holds, its depth falls. The planner sets the label at grill time, so a mislabelled increment gets the lighter review. Every implementer kind already runs at low because the review is the net for low-effort implementation (`delegation-model-classes.md:121`), so two cheaper steps would meet on one increment.
- **Trial.** Lever: the reviewer's effort on low-labelled increments, with the checklist unchanged (a reduced checklist would be a second lever and a second trial). Tasks: the contained fix and the covered-lane change; the new flow as a medium control. Measures as shared, findings read by severity.
- **Cost.** The reviewer `first` records, grouped by label.
- **Recommendation.** Adopt only after a trial on effort alone; keep the checklist whole while implementation runs at low.

## T5. A third model class for mechanical work, and the building class for implementer, tester and reviewer

- **Proposal.** Add a mechanical class (the host's smallest model) for gate runs, extraction and mechanical edits, and run implementer, tester and reviewer on a building class below authoring, keeping authoring for contracts, rulings, security and adversarial work.
- **Relies on.** Two classes and four aliases (`core/method/delegation-model-classes.md:42-50`); the plant's model map (`delegation-model-classes.md:51-64`); the per-role-and-kind class table, every row today the role's `model:`, with `brief.py` printing a `Model:` line only where a row differs (`delegation-model-classes.md:145-167`); light variants, which already put small mechanical work on the investigation class with mechanical escalation (`core/method/delegation-light-variants.md:22-51`).
- **Quality risk.** Closest to RED before GREEN (a weaker tester writes tests that survive mutants) and the independent first review (a weaker reviewer misses findings); the security pass stays on authoring by the security-surface rule (`delegation-model-classes.md:87`). A third class also adds a column to every plant's model map.
- **Trial.** One row per trial, moved in a copy of the plant for arm B only (`lever-trial.md:29`): reviewer `first`, then tester `red`, then implementer `increment`. All five task kinds; the trust-path task stays on authoring in both arms as a control. Mutation score is the deciding measure for the tester row.
- **Cost.** The moved role's records, read with each record's `model` field.
- **Recommendation.** Adopt row by row, each after its own trial; hold the third class until row trials show the class table is the lever that pays, since it changes a file every plant fills.

## T6. A lower default effort for the lead's routing turns

- **Proposal.** The lead runs routine turns (reading a handback, briefing the next ready batch, logging) at medium and keeps high for tier classification, rulings, one-way decisions and acceptance.
- **Relies on.** The charter's `effort: high` and its table row (`agents/00-orchestrator.md:6`; `core/method/delegation-model-classes.md:110`). The charter is never spawned, so on Claude Code the lead's effort is the session's own setting, which the installer leaves to the host (no effort option among `install.sh:2679-2718`; inferred). `tools/cycle.py` now computes the routing turn's bookkeeping (`core/method/delegation-cycle-economy.md:50-55`).
- **Quality risk.** The lead decides tier, `--security-path` and whether a decision is one-way, so this sits closest to the security pass and the devil's-advocate check: a misclassifying turn routes work around both. A host may expose effort only per session, and a session-wide setting reaches the classification turns too.
- **Trial.** Lever: lead effort, at the finest grain the host exposes, verified before the trial. All five task kinds, the trust-path change and the new flow weighted. Added measure: missed security paths and misclassified tiers, graded from the delivery.
- **Cost.** The lead's session usage per run.
- **Recommendation.** Adopt only if the host can set effort per turn and the trial shows no missed security path; otherwise keep high.

## T7. A short orchestrator digest always loaded, the full charter loaded on entering T2 or T3 work

- **Proposal.** The Claude Code output style carries a short digest (classify the tier, route, the kernel anchors); the full charter and its `always_loads:` nodes load when the session classifies work as T2 or T3.
- **Relies on.** The main session plays the orchestrator through the output style `install.sh` composes from the charter and its `always_loads:` (`tests/seed-lint.py:1228-1232`; SPEC-0005 `MAIN_SESSION_PLAYS_THE_ORCHESTRATOR`); the list (`agents/00-orchestrator.md:45-50`); the claude-code always-loaded exemption, an owner decision of 2026-11-09, held by `tools/ratchet-lint.py` (`tests/seed-lint.py:87-90`).
- **Quality risk.** Classification would run on the digest alone. A T2 or T3 task classified T1 never loads the charter and is edited in-session, which bypasses RED before GREEN, the independent first review and the security pass together. A digest written by hand is also a second home for charter facts.
- **Trial.** Lever: the always-loaded orchestrator surface. The five task kinds, plus a T0 question, a T1 edit and a deliberately ambiguous request (which the kernel sends to T3). Added measure: tier correctness per task.
- **Cost.** The lead's session usage per run; `eager_surfaces` in `tests/seed-lint.py` prints the byte figure as structure, not as a token count.
- **Recommendation.** Adopt only if the digest is generated from the charter and the trial shows no downward misclassification; the exemption would then be lowered and stay ratcheted.

## T8. An install option for a minimal roster

- **Proposal.** An opt-in installer option places a core roster the owner names and leaves every other agent in the graph, placeable by a later install; the default install places the whole roster as today.
- **Relies on.** Each placed agent's description is in every host's always-loaded figure (`tests/seed-lint.py:1209-1223`); the installer projects the graph's whole roster per host (`install.sh:1061-1073`); `--expertise <ids>` is the precedent for placing exactly an owner-confirmed list (`install.sh:67-72`); roster ground truth is `agents/*.md` frontmatter.
- **Quality risk.** Several section 9 safeguards are carried by a roster member: the tester for RED, the reviewer, `security`, `devils-advocate`. A session that needs an absent specialist skips the step or does it itself, and a specialist placed mid-session is spawnable only after the host registers it (`delegation.harness-registration`).
- **Trial.** Lever: roster size. Arm B keeps every role a section 9 safeguard names. All five task kinds. Added measure: steps where a needed role was absent.
- **Cost.** The lead's session usage per run.
- **Recommendation.** Adopt only with a minimal set that always includes every safeguard role, and an `install.sh --check` line naming the agents left out; the trial then shows whether host usage moves.

## T9. Staged growth as an owner choice

- **Proposal.** The owner may grow a plant in stages: the first stage covers the collections the owner names to full depth, and each other collection is recorded as deferred by the owner, with the date and a reopen condition, for a later session.
- **Relies on.** The completeness contract: growth is complete or not done, every collection is covered or absent with a reason, and "ran out of context" is the forbidden third outcome (`protocols/grow.md:214-240`); each phase already opens and closes on a commit (`grow.md:457-475`); `UNKNOWN` rows reach the owner as numbered decisions (`grow.md:1205-1210`; `tools/growth-audit.py`).
- **Quality risk.** No section 9 safeguard names growth; the nearest is the duty to refuse, and staging makes the forbidden third outcome a permitted one. What escapes: sessions after a staged growth re-derive the facts the graph lacks, and a deferral nobody reopens becomes permanent. It amends `grow.completeness-contract`, so it needs an ADR.
- **Trial.** Lever: growth completeness. Arm A grows fully; arm B grows stage one, then both run the five task kinds on their grown plant. Added measure: facts a task re-derived that full growth would hold.
- **Cost.** The growth spawns' records plus every task run after them, summed per arm.
- **Recommendation.** Adopt only as an explicit, dated owner choice per collection, counted by `growth-audit.py` as `UNKNOWN` and named in the plant's `changelog.md`; full growth stays the default.

## T10. A byte budget for every node, and grow, graft and harvest split by phase

- **Proposal.** (a) Each routable node carries a byte ceiling, ratcheted like the line ceilings. (b) `grow`, `graft` and `harvest` become a shared core plus one node per phase, so a session or worker loads only the phase it runs.
- **Relies on.** The node ceilings count lines: `MACHINERY_BODY_CEILING`, `LIFECYCLE_BODY_CEILING`, `LEAF_BODY_CEILING` and the frozen `OVERSIZED_LEAVES` (`tests/seed-lint.py:32-63`); only the kernel and the always-loaded surface are measured in bytes (`seed-lint.py:30`, `83-90`); every limit is ratcheted by `tools/ratchet-lint.py:129-188`. [ADR-0007](../decisions/adr-0007-lifecycle-protocol-ceiling.md) keeps the three whole: only the session running one loads it, and procedural completeness there is load-bearing for safety. Their phases: `grow.md:477-1186`, `graft.md:519-1394`, `harvest.md:278-864`; SPEC-0005 §6 records the split as held.
- **Quality risk.** (a) touches no safeguard, but a ceiling a later edit hits invites trimming procedure text, the risk ADR-0007 names. (b) is closest to worker preconditions and graft's integrity gates (`graft.md:1221`): a phase node missing a cross-phase rule (Reversibility, write scope) lets a destructive step run without it, and a plant customization is overwritten.
- **Trial.** (a) changes no model behaviour and needs no trial. (b) Lever: the lifecycle loading pattern; tasks are a grow of a fixture plant, a graft across one seed version over a plant customization, and a harvest with a non-agnostic candidate. Added measures: integrity-gate verdicts, customizations preserved.
- **Cost.** The records of every spawn that loads these nodes, plus the lead's usage for the phases it runs.
- **Recommendation.** (a) Adopt, recorded from the tree as it stands. (b) Adopt only after a trial and an ADR that supersedes ADR-0007's whole-node decision in part, with the cross-phase rules in the core every phase node requires.

## T11. A context-size trigger for handing a worker's batch to a fresh worker

- **Proposal.** When a RED or GREEN worker's context passes a threshold the owner sets, it hands back at the next increment boundary and the rest of its batch goes to a fresh worker briefed from the batch record and the committed tip.
- **Relies on.** One worker per batch, fixed at spawn, which stops at a boundary and names the remainder (`core/method/delegation-cycle-economy.md:41-55`); a fresh worker by default, since a continued one replays its whole context (`core/method/delegation-continuation.md:27-51`); `cycle.py` for readiness and RED hashes; per-response counts from a transcript (`brief.py --tokens --transcript`). An earlier measured run showed a mid-increment handoff costing more than it saved for a single warm implementer; this proposal hands off only between increments of a batch.
- **Quality risk.** Closest to RED before GREEN with hashes, which the fresh worker re-checks through `cycle.py`, and worker preconditions. What escapes: the design context the first worker built, so the second contradicts it, a stitch the reviewer rates major. The trigger needs a context reading inside the worker's own turn; whether a host exposes one is unknown.
- **Trial.** Lever: a handoff threshold for batches. Tasks: the new flow and the covered-lane change, briefed as batches at the table's size. Added measure: integration-coherence findings at the handoff seam.
- **Cost.** The sum over every worker of a batch, per arm, by token kind: a fresh worker writes cache the warm one reads.
- **Recommendation.** Keep one worker per batch. Run this trial only once a context signal the worker can read is verified on the host; the earlier measured run puts the burden of proof on arm B.
