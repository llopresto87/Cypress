## 8.3.1 — token accounting, a cycle driver and opt-in cache settings (2026-11-10)

This round adds the instruments needed to measure what a build costs, and
the levers a later round can test with them. A plant installed without
opting in behaves as it did on 8.3.0. The kernel, the always-loaded surface
and the brief blocks are no larger than 8.3.0's. No saving was measured in
this round. To measure one, the owner composes briefs with the token ledger
on, then compares two arms under the trial protocol in
`docs/skills/lever-trial.md`.

### The round in brief

- **A token ledger.** `brief.py --tokens <spawn_id>` records each spawn's
  host-reported token counts in `tokens.jsonl` beside the spawn log, or
  `not recorded` with a reason when the host reports none. It reads the
  counts from a usage object or from a Claude Code subagent transcript.
  Deliver gains one optional Tokens line, summed from the ledger, and the
  log reader prints it.
- **The resume guard follows the worker cache lifetime.** `resume-hook.py`
  reads the configured worker lifetime. It counts a configured one-hour
  lifetime only when the worker's own transcript shows a one-hour cache
  write.
- **Cache lifetimes, documented and opt-in.** The Claude Code README and the
  capability matrix record the lead and worker lifetimes and their
  precedence. `install.sh claude-code --prompt-cache-ttl 1h` writes the lead
  setting and records the choice in `.cypress/seed.json`;
  `--prompt-cache-ttl default` removes it. The default install writes no
  cache setting.
- **A cycle driver.** `docs/graph/cycle.py`, placed in every plant, prints
  a build cycle's state in one read: ready batches, held increments with
  their condition, the expected-red list, RED-hash mismatches and whether a
  ruling pass is owed. It reads the plan, the spawn log, the batch record,
  the question files and git. An increment counts as landed when every
  contract slug its plan row names appears in a GREEN `feat`/`fix`
  commit subject on the branch, and the report says this is inferred. `record-red` and `record-tip` write the batch record. It spawns
  nothing and decides nothing.
- **Generated Session metrics lines.** `brief.py --log` prints the
  countable lines of the delivery's Session metrics block, so they are
  copied, not counted by hand. The Serial waits value is inferred from
  composition times and says so.
- **A batch-size notice.** `brief.py --increments N[,N] --unit <unit>`
  prints a notice when a batch is smaller than its effort scale allows;
  `--alone` records a security or concurrency GREEN batched alone on
  purpose.
- **Slow commands and gate output.** The rule for a command that outlasts
  the cache, and the rule for reading gate output, now live in the nodes
  that own them.
- **Model classes and a trial protocol.** `brief.py` derives a model class
  per role and task kind from a table that keeps today's defaults. The
  seed-only `docs/skills/lever-trial.md` says how to test a lever: two arms,
  a quality margin agreed before the first run, and a verdict that fails
  closed.

### Also in this round

- Eleven owner decision notes in
  `docs/plans/owner-decisions-8.3.1-token-efficiency.md`, prepared and not
  adopted.
- The light-variants section moved to its own node,
  `core/method/delegation-light-variants.md`.
- The plan of record is `docs/plans/grill-8.3.1-token-efficiency.md`.
- A placement test no longer depends on one platform's tools.
- `graft-audit.py` maps the placed cycle driver to its seed source.
