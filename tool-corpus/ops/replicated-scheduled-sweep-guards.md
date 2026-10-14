---
stack:
  - library-corpus/container/postgres
---
# Tool: replicated-scheduled-sweep-guards

> Project-agnostic capability notes, kept in the seed's tool corpus
> (`tool-corpus/README.md`). Orientation for a reusable pattern, a blueprint:
> the two guards and their failure modes are stack-neutral; the lock primitive
> shown is the database's that the `stack:` entry names, and the start signal
> is the application host's.

## 0. Identity

- **Category:** ops
- **Name:** replicated-scheduled-sweep-guards
- **Language / runtime:** any service runtime with a scheduled background job
  and a relational database; the lock primitive here is a database advisory
  lock.
- **Stability:** **blueprint**: proven in practice by a first-boot failure on
  an upgraded installation that the second guard closed; adapt both guards to
  the project's host and database

## 1. What it does

A recurring background job (a retention sweep, an expiry pass, a cleanup) that
must run **once per cycle across every replica** of a horizontally scaled
service needs **two independent guards**:

1. **A distributed lock**, so only one replica's timer does the work in a
   cycle. Without it every replica selects the same batch: one commit lands and
   the others report a failure about a mechanism that worked.
2. **A start-order gate on the host's own "fully started" signal**, so the
   first run cannot race ahead of a schema or data migration the same
   deployment is still applying. Without it, the first boot of an **upgraded**
   installation fails on a column or table that does not exist yet, and the
   cycle's work is lost.

Dropping either guard reproduces a different failure; neither covers the
other. A fresh installation hides the second one entirely, because there the
schema is created before anything runs.

## 2. Interface & invocation

The pattern lives inside the service, not as a separate command:

```
on host fully started:                  # guard 2: never on raw process start
    every <interval>:
        if try_lock(SWEEP_LOCK_KEY):    # guard 1: non-blocking
            try:     run_sweep()        # report per category
            finally: unlock(SWEEP_LOCK_KEY)
        else:
            log at informational level: "another replica holds the sweep"
```

- **Lock key:** a fixed literal constant per sweep, distinct for each sweep that
  shares the database.
- **Losing the race is normal:** log it at informational level, not as an
  error, and never count it as a failed run.
- **Report:** the sweep reports what it did per category, so a category that
  failed is visible apart from one that had nothing to do.

## 3. Approach / algorithm

**Guard 1, the lock.** With the database the `stack:` entry names, use the
non-blocking advisory-lock functions on a single connection held for the whole
sweep: try to take the lock, run, release on the same connection. A
transaction-scoped variant releases itself at transaction end and suits a sweep
that fits in one transaction; a session-scoped lock is held until released or
until the connection closes.

- **Keep the key a literal, not a hash of a name computed at run time.** A
  derived key is one refactor away from becoming a different lock, after which
  two replicas each hold "the" lock and the guarantee is gone with nothing to
  show for it. Distinct literals per sweep also make each lock recognisable in
  the database's lock view while an operator is looking.
- **One connection for take and release.** A session lock belongs to the
  physical connection: an unlock on a different pooled connection releases
  nothing (it reports the lock was not held), and returning the connection to
  the pool unreleased hands the lock to whoever borrows it next. A pooler that multiplexes sessions per transaction cannot
  carry a session lock at all; take the sweep's connection outside such a
  pooler or use the transaction-scoped lock.

**Guard 2, the start gate.** Wait on the host's lifecycle event that fires
after **every** startup component has started (for example the generic host's
"application started" notification, or an application-ready event), not on
the job's own start and not on the order components were registered in.
Registration order is an implementation detail a later change reorders
silently; the "all started" event holds whatever the order becomes. Where
migrations run outside the process (a separate job), gate instead on a check
that the schema version the sweep needs is present.

## 4. Portable vs blueprint

- **Portable (carry over):** two guards, both required; non-blocking try-lock
  with release in `finally`; a fixed literal key per sweep; losing the race
  logged as information; gate the first run on the host's "all started"
  signal; per-category reporting.
- **Fill in per project:** the lock primitive (the database's, or a lease in a
  shared store when there is no relational database); the host's lifecycle
  event; the interval; the categories; the key constants.

## 5. Pitfalls and sharp edges

- **A lock abstraction that "grants" on an in-memory test provider is never
  exercised by unit tests.** A data-access layer can report a database lock as
  granted, doing nothing, on a non-relational test double. Prove the lock with an integration
  test against the real database engine.
- **The start-order bug only shows on an upgrade.** Test the second guard on
  an installation upgraded from the previous release, not on a fresh one: the
  fresh path creates the schema first and passes for the wrong reason.
- **Registration order "worked" until it did not.** Treat any guard that
  depends on the order components are registered in as no guard.
- **A held session lock survives a hung sweep, and a cancelled statement.** A
  statement timeout aborts the statement but leaves the session, and so the
  session lock, in place: a rollback does not release it. If the sweep can hang,
  bound it so the connection itself is closed (a session-terminating timeout, or
  the application closing the connection), or release the lock in the
  cancellation path.

## 6. Tests that cover it

Cover, against the real database: two concurrent sweeps with the same key,
exactly one does the work and the other logs the lost race at informational
level with no failure reported; release happens on an exception path; two
different sweeps with distinct keys run concurrently; on a database upgraded
from the previous schema, the first sweep runs only after the migration is
applied (no missing-column error in the log); a unit test that relies on a
no-op lock is labelled as not covering the lock.

- **How to run the tests:** `<the plant's integration test command>`

## 7. References & neighbours

- **Library:** `library-corpus/container/postgres.md` (the database whose
  advisory locks the lock guard uses).
- **Sources:** distilled from practice. The lock semantics are
  PostgreSQL's: "Advisory Locks" (a session-level lock is held until
  explicitly released or the session ends; a transaction-level one is
  released at transaction end) and "Advisory Lock Functions"
  (`pg_try_advisory_lock`, `pg_try_advisory_xact_lock`, and
  `pg_advisory_unlock` returning false when the lock was not held)
  (<https://www.postgresql.org/docs/current/explicit-locking.html>,
  <https://www.postgresql.org/docs/current/functions-admin.html>). The
  pooler limit is PgBouncer's feature table, which lists session-level
  advisory locks as unsupported in transaction pooling
  (<https://www.pgbouncer.org/features.html>).

## 8. Changelog

- 2026-10-14: created as a blueprint from a scheduled sweep whose
  start-order guard was added after a measured first-boot failure on an
  upgraded installation; lock keys and table names stay with the project.
