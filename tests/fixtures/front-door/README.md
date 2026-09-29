# Example seed

A synthetic front door for tests/test-seed-lint.sh (SPEC-0004 §6 "Fixture").
Read the [glossary](DOCUMENTATION.md#glossary) and the [install guide](INSTALL.md).

## What installing does to your repository

The installer writes `CLAUDE.md`, `AGENTS.md`, the `.claude/` directory and the graph under `docs/graph/`.

A differing file is kept beside itself as a timestamped copy. The one file replaced without a copy is the install stamp `.cypress/seed.json` ([backup before replace](DOCUMENTATION.md#enf-backup-before-replace)).

## Where next

A [plant](DOCUMENTATION.md#term-plant) is a repository at `/path/to/your/project` after an install.
