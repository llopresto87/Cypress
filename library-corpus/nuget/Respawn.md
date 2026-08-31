# Respawn — nuget

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
A test-database reset library for .NET integration tests. It resets a database's
**data** between test runs — deleting rows — rather than dropping and recreating
the schema. That keeps each test isolated against a real database while avoiding
the cost of a full schema rebuild per test, which is what makes database-backed
integration suites fast enough to run routinely.

## Core API / usage shape
- Build a respawner once against a live connection:
  `Respawner.CreateAsync(connection, new RespawnerOptions { SchemasToInclude = [...], TablesToIgnore = [...] })`.
  Creation inspects the database to work out the delete order, so it is the
  expensive step; `ResetAsync` is the cheap one.
- Call `ResetAsync(connection)` per test to return the database to its
  post-migration baseline.
- The reset truncates/deletes respecting foreign-key order, so tables do not have
  to be listed in dependency order by hand.
- `SchemasToInclude` (or its exclude counterpart) scopes the blast radius to the
  application's own schemas, keeping migration-history and infrastructure schemas
  out of the reset.
- `TablesToIgnore` is the escape hatch for tables that must survive a reset —
  migration history, seed/reference/lookup data.

## Idioms & best practices
- Own the respawner in a shared test fixture so creation happens once and every
  test pays only the reset (`xunit.md` owns the collection-fixture mechanism).
- Treat the ignore list as part of the schema contract: whoever adds a
  seed/reference table also adds it to the ignore list in the same change.

## General pitfalls
- **A newly added seed table silently gets wiped:** reference/seed data that is
  not in `TablesToIgnore` survives only until the first reset. The test that runs
  before that reset passes, so the failure surfaces later and elsewhere — every
  subsequent test that depends on the seed data breaks, with nothing pointing back
  at the reset as the cause. Adding a seed table without updating the ignore list
  is the classic way to poison a whole suite.

## Upstream docs
- https://github.com/jbogard/Respawn
- https://www.nuget.org/packages/Respawn
