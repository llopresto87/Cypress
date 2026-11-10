---
name: lever-trial
description: Seed-only. How a steward compares two settings of one lever of the method (a model class, an effort, a rule) on a fixed task set, grades the runs blind, costs them from the token ledger, and lets a cheaper setting become the default only inside an agreed quality margin.
id: skill.lever-trial
kind: skill
origin: seed-only
owns:
  - lever-trial.when
  - lever-trial.design
  - lever-trial.measures
  - lever-trial.verdict
load_when:
  - "compare two settings of one lever, trial a model class, an effort or a rule"
  - "measured trial before changing a default, A/B arm, blind grader"
---

# lever-trial

A lever is one setting the method chooses for a worker: a row of the model-class table, a row of the effort table, or one rule. A default moves only on evidence. This procedure produces that evidence: two arms that differ in the one lever, run on the same tasks, graded blind, costed from the host's own counts. It runs from the seed and is never placed in a plant ([ADR-0021](../decisions/adr-0021-seed-only-procedures-stay-home.md)); the runs themselves happen in a plant the steward governs.

## When to apply (`lever-trial.when`)

- Before any change to a default the owner set: a class or effort row, or a rule that a worker follows.
- When a proposal claims a lever is cheaper at equal quality. The trial decides it; the claim alone moves nothing.
- Start it only on the owner's go-ahead, because every run spends real model work. Hold each arm until the owner says run.

## Design (`lever-trial.design`)

1. **Name the lever and its two settings.** Arm A is today's setting; arm B is the candidate. Everything else stays identical between arms: the seed version, the plant commit each task starts from, the briefs, the tools, the host and its version. A row moved through the model-class table is set in a copy of the plant for arm B only, so the shipped table keeps reproducing today's model.
2. **Fix the task set before the first run.** Choose one task of each kind, written as a brief a worker can start from and stored with the trial:
   - a contained fix: one defect in one module, its test already describing the wanted behaviour;
   - a covered-lane change: a change inside a lane whose tests already cover it;
   - a new flow: a user-facing feature or stateful contract with its spec contracts and RED tests to write;
   - a trust-path change: new code on a trust surface, which takes the security pass;
   - a dependency upgrade: one library moved a major version, with the fixes it forces.
   Describe each task by its shape and stack, never by a project's name. Keep the set fixed across both arms and every run.
3. **Run at least five times per arm per task.** Start each run from the same commit in a fresh worktree. Interleave the arms (A, B, A, B, ...) so a host change during the trial falls on both.
4. **Write the rubric before grading.** For each task, list what a correct result does, what a partial one misses, and what counts as a defect, with a score per item. Commit the rubric before the first run.
5. **Grade blind.** Strip each result of its arm, its model and its effort, give it a random label, and hand it to one grader running a model class at least as strong as the strongest arm, at high effort. The grader scores against the rubric only. Keep the label key out of the grader's reach until every run is scored.

## Measures (`lever-trial.measures`)

Record per run, per increment where the run has several:

- review findings and security findings, counted per increment by severity;
- full-suite runs that came back red before the increment closed;
- the mutation score, where the increment's contracts take a mutation pass;
- findings that escape to a later increment: a defect a later review, test or run traces back to this one;
- the rubric score from the blind grader;
- the cost: the token ledger of each spawn, `docs/graph/brief.py --tokens <spawn_id> --usage FILE` or `--transcript PATH`, which appends host-reported counts to `tokens.jsonl` beside the spawn log. Compare arms on those counts as recorded. A count the host did not report stays `not recorded`; leave it so and say how many runs it affects.

Report counts and their spread per arm. State no price; the owner applies prices outside the record.

## Verdict (`lever-trial.verdict`)

- **Agree the quality margin before the first run**: for each outcome measure, how far arm B may fall from arm A and still count as equal. Write it beside the rubric.
- **Fail closed.** A cheaper arm whose quality falls outside the agreed margin on any outcome measure stays a non-default, whatever its cost. A result the runs cannot decide, too few runs or too wide a spread, also leaves the default where it is.
- An arm inside the margin on every measure and cheaper on the ledger is a proposal for the owner. The owner decides the default and records the decision in words with its date; the trial's record supports it.
- One trial moves one lever. A second lever starts a second trial.

## Where the evidence lives

Commit the trial in the plant where it ran, under `docs/graph/evaluations/<lever>/`, one folder per lever:

- `design.md`: the lever, the two settings, the task briefs, the rubric and the agreed margin, committed before the first run;
- `runs/<arm>-<task>-<n>/`: each run's spawn log, its `tokens.jsonl`, its gate output and the grader's scored sheet under the blind label;
- `key.md`: the label-to-arm key, committed after grading closes;
- `verdict.md`: the measures per arm, the comparison against the margin, and the outcome the fail-closed rule gives.

A seed release that changes a default because of a trial names the trial in its CHANGELOG entry and keeps the plant's evidence out of seed nodes.
