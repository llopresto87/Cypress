# postgres — container

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a tool, not a record of one
> project's versions. For exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile / base-image tag.

## What it is
PostgreSQL is an open-source relational database server. In a containerized
stack it usually runs from the official image as one service holding a
**cluster**: a single server process managing several **databases**, each with
its own schemas, and one shared set of **roles** (users and groups) that span
all of them. Clients connect over the network with a role, a password or other
authentication method, and a target database.

## Install, setup and configuration
- **Environment, first start only** (ignored, and unset by the entrypoint,
  once a database exists): `POSTGRES_PASSWORD` (required: the entrypoint
  refuses to start without it unless `POSTGRES_HOST_AUTH_METHOD=trust`),
  `POSTGRES_USER` (default `postgres`), `POSTGRES_DB` (default: the user name),
  `POSTGRES_INITDB_ARGS`, `POSTGRES_INITDB_WALDIR`,
  `POSTGRES_HOST_AUTH_METHOD`. Each takes a `_FILE` form that reads the value
  from a file (an image convention, used with Compose secrets).
- **Init phase.** On an empty data directory the entrypoint runs `initdb`,
  starts a temporary server that listens on the Unix socket only
  (`listen_addresses=''`), creates the user and database, runs
  `/docker-entrypoint-initdb.d/*` in sorted name order (by the current
  locale), stops the temporary server, logs `PostgreSQL init process
  complete; ready for start up.` and execs the real server. `*.sql` and
  compressed SQL run as `POSTGRES_USER`; an executable `*.sh` is run, a
  non-executable one is sourced into the entrypoint shell.
- **Data path.** From the 18 line, `PGDATA` is
  `/var/lib/postgresql/<major>/docker` and the declared volume is the parent
  `/var/lib/postgresql`, so one mount can hold two majors for a fast
  `pg_upgrade --link`. On 17 and older, `PGDATA` and the volume are
  `/var/lib/postgresql/data`; a volume mounted at the parent there persists
  nothing (an anonymous volume takes the declared path).
- **`pg_hba.conf`** of the image: local socket connections use `trust`, and
  the entrypoint appends `host all all all <POSTGRES_HOST_AUTH_METHOD>` on an
  empty data directory, `scram-sha-256` by default (see Major lines).
- **Variants and locale.** Debian images set `LANG=en_US.utf8`; Alpine
  images use musl and support ICU locales only from the 15 line, with an
  upstream `POSTGRES_INITDB_ARGS` recipe for the locale.
- **Stop signal** is SIGINT (fast shutdown), and upstream recommends a stop
  timeout longer than the runtime's 10 s default.

## Core API / usage shape
- **Official image bootstrap.** On first start against an empty data directory
  the image initializes the cluster, creates a bootstrap superuser and an
  initial database from environment variables, then runs any scripts placed in
  its init directory (`/docker-entrypoint-initdb.d/`). Those scripts run
  **once**, only when the data directory is empty; changing them later does
  nothing to an existing volume.
- **Roles and privileges.** `CREATE ROLE` with attributes (`LOGIN`,
  `SUPERUSER`, `CREATEDB`, …), `GRANT`/`REVOKE` on databases, schemas, tables
  and sequences, and object ownership. The owner of an object has full rights
  over it.
- **Client authentication.** `pg_hba.conf` decides which roles may connect to
  which databases from which addresses, and with which method.
- **More databases and roles.** `POSTGRES_DB` creates one database; others
  come from init scripts. `CREATE DATABASE` has no `IF NOT EXISTS`, so
  scripts use `SELECT 'CREATE DATABASE x' WHERE NOT EXISTS (…) \gexec` in
  `psql`.
- **Versioning.** A **major** release changes the on-disk format, and moving
  between majors needs a dump and restore or `pg_upgrade`. A **minor** release
  is a drop-in bug and security fix within a major, applied by replacing the
  binaries (in a container, the image) with the same data directory.

## Idioms & best practices
- **Track the current minor of your major.** Upstream supports each major for
  five years after its first release and ships minor releases at least once a
  quarter, and it recommends always running the current minor, because a minor
  upgrade is less risky than staying on an old one. Whichever way the image is
  tagged, make the running minor answerable from somewhere you control (a
  recorded digest, a startup log line, a `SELECT version()` probe in a
  deployment check); "are we current?" should never be unanswerable.
- **Application roles are not superusers.** Use the bootstrap superuser only to
  create databases and roles. Give each consuming service its own login role
  that owns, or is granted on, only its own database. A superuser connection
  gives no blast-radius boundary: one injection or compromised container reaches
  every database in the cluster, including neighbours that were deliberately
  scoped.
- **Keep test and deployment on the same version line.** A test container
  pinned to an exact minor while deployment floats (or the other way round)
  means the suite witnesses a version that is not the one deployed, and any
  minor-specific defect is invisible to the gates. Move both together, or pin
  both.
- **One schema, one owner of its migrations.** When several components write
  the same tables, one of them owns the migrations and the others consume the
  result. A schema dump that another component's tests load, generated from the
  owner's migrations, has to be regenerated by a gate, not by memory.
- **Treat a schema change on a table another writer depends on as a change to
  both writers.** Before narrowing, retyping or constraining a column, check how
  every writer handles the new error (a value-too-long error is often outside a
  consumer's transient-retry set and leaves work silently parked).
- **Free text written by another system is `text`.** In PostgreSQL
  `varchar(n)` has no performance advantage over `text`; a guessed width only
  turns the first longer value into error `22001`, which aborts the whole
  transaction. Give externally authored free text `text` (with a `CHECK` only
  where a real limit exists), widen every column of that kind together, not
  only the one that failed, and refuse an oversized value instead of
  truncating it. A down-migration back to `varchar(n)` stops being clean once
  one longer row exists.

- **Least privilege starts in the init scripts**: one login role per
  consumer (identity servers included), owning its own database, with grants
  on `public` inside it.
- **Probe readiness over TCP or with a real query.** `pg_isready` proves only
  that connections are accepted.

## General pitfalls
- **`pg_isready` without `-h` passes during init.** It probes the Unix
  socket, which the temporary init server also answers, so dependents can start
  before the init scripts finish. A TCP probe (`-h 127.0.0.1`) cannot succeed
  until the real server runs.
- **"ready to accept connections" is logged twice**, once by the temporary
  server and once by the real one; a log-based wait strategy must match the
  second (follows from the entrypoint code; the image docs do not mention it).
- **A failing init script stops the entrypoint**, and on the orchestrator's
  restart the data directory exists, so the scripts are skipped and the half
  initialized database is served.
- **Wrong volume path on a major change.** Moving to the 18 line with the old
  `/var/lib/postgresql/data` mount, or mounting the parent on an older line,
  leaves data in an anonymous volume.
- **Anyone who can `exec` into the container is superuser without a
  password** through the socket `trust` rule.
- **Collation differs by variant**: glibc (Debian) and musl (Alpine) sort
  non-ASCII text differently, so test on the variant you deploy (observed in
  practice; upstream links musl's differences page). The same holds within one
  variant over time: a new base image whose C library changed under an existing
  data directory changes collation rules (C and POSIX locales excepted). The
  server warns of a collation version mismatch (per database from the 15 line
  on), and indexes on text columns may now be wrong. Rebuild them (`REINDEX`),
  then record the new version with `ALTER DATABASE ... REFRESH COLLATION
  VERSION`, or dump and restore. Treat the image refresh as a data change, not
  a routine patch.
- **No TLS, no backups.** Observed in practice: the image answered TLS
  requests with `N` (cleartext unless `ssl=on` and a certificate are
  configured) and configured no backup, retention or point-in-time recovery;
  the absence is silent. The image docs describe neither.
- **Raw-SQL migrations written as `IF NOT EXISTS` with no history table**
  cannot express alter or drop safely and cannot report what ran.
- **A superuser bypasses every permission check except the right to log in.**
  So no `GRANT` or `REVOKE` is evidence of any restriction for a superuser
  connection, and a trigger-based guarantee (an append-only ledger, an audit
  table) is advisory against one, because a superuser can disable or drop the
  trigger.
- **Init scripts do not re-run.** A role, grant or extension added to an init
  script after the volume exists never reaches that environment. Carry later
  changes as migrations.
- **Moving an existing service off a superuser is a migration, not an edit to a
  connection string.** Ownership of the objects it created has to move to the
  new role first, or the service loses access to its own tables.
- **A schema dump generated from another component's migrations drifts
  silently.** Nothing fails when it falls behind, so the consuming suite stays
  green against a schema that no longer exists.
- **Server errors can carry the parameter values that caused them** when a
  client asks for error detail, and from there they reach exception messages
  and logs. The switch is client-side; the .NET driver's is on
  [`nuget/Npgsql.md`](../nuget/Npgsql.md). Keep it out of deployed
  configuration.
- **Migrations applied automatically at application start have no review gate
  between merge and execution.** A destructive migration runs on the first boot
  after deploy.

## Testing
- Run test containers on the same major **and variant** as deployment.
- Wait on a TCP connection or a real query, or on the second
  "ready to accept connections", never on the socket.
- Seed through `/docker-entrypoint-initdb.d` with a fresh volume per run, and
  keep schema evolution in migrations the tests also run.

## Security defaults
- Host connections need a password (`scram-sha-256` on current lines);
  socket connections inside the container are `trust`.
- `POSTGRES_HOST_AUTH_METHOD=trust` opens every host connection without a
  password; upstream warns against it.
- The bootstrap user is a superuser.
- No TLS is configured by the image.

## Operational behaviour
- First start initializes and runs the init scripts; later starts go straight
  to the server.
- SIGINT on stop means a fast shutdown (active transactions roll back); give
  it a stop timeout longer than 10 s.
- Major upgrades need `pg_upgrade` (or dump and restore); the 18-line layout
  exists to make `pg_upgrade --link` work within one volume.

## Interop
- Compose health gating, secrets and `*_FILE`:
  [`docker-compose.md`](docker-compose.md).
- The .NET driver: [`nuget/Npgsql.md`](../nuget/Npgsql.md).

## Major lines
- **14 line**: the default host auth method became `scram-sha-256`; older
  lines used `md5`.
- **15 line**: Alpine images gained ICU locale support.
- **18 line**: version-specific `PGDATA` under a `/var/lib/postgresql`
  volume; 17 and older use `/var/lib/postgresql/data`.

## Upstream docs
- https://www.postgresql.org/docs/current/
- https://www.postgresql.org/support/versioning/
- https://www.postgresql.org/docs/current/role-attributes.html
- https://www.postgresql.org/docs/current/datatype-character.html
- https://www.postgresql.org/docs/current/sql-alterdatabase.html (`REFRESH
  COLLATION VERSION`); https://wiki.postgresql.org/wiki/Locale_data_changes
- https://hub.docker.com/_/postgres
- https://github.com/docker-library/docs/tree/master/postgres
- https://github.com/docker-library/postgres
