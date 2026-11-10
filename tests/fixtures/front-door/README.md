# Example seed

A synthetic front door for tests/test-seed-lint.sh (SPEC-0004 §6 "Fixture").
Read the [glossary](DOCUMENTATION.md#glossary) and the [install guide](INSTALL.md).

## What installing does to your repository

The installer writes `CLAUDE.md`, `AGENTS.md`, the `.claude/` directory and the graph under `docs/graph/`.

A differing file is kept beside itself as a timestamped copy. The one file replaced without a copy is the install stamp `.cypress/seed.json` ([backup before replace](DOCUMENTATION.md#enf-backup-before-replace)).

## What it costs

| Figure | What it covers, and how it was obtained |
|---|---|
| 11% more tokens | per task, against a session with no method: 131 583 tokens against 118 973. The same run took 20% more tool calls (72 against 60) and 20% more wall-clock time (12 min 40 s against 10 min 32 s), and the run without the method found a defect that the run with the method missed. Measured once, on one small, well-specified task ([evidence record](docs/plans/grill-7.29.0-front-door/method-overhead-evidence.md)) |

## Where next

A [plant](DOCUMENTATION.md#term-plant) is a repository at `/path/to/your/project` after an install.
