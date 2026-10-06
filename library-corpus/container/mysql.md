# mysql — container

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a server image, not a record of
> one project's versions. For exact pins, advisories and per-release behavior,
> run `ingest-library` against the project's own image tag. The Java driver is a
> separate page, `library-corpus/maven/mysql-connector-j`.

## What it is
MySQL is a relational database server. One `mysqld` process holds many
schemas; accounts are `user@host` pairs with global, schema and table
privileges. The official `mysql` image (docker-library, Oracle-built server
on an Oracle Linux base) ships the server with the `mysql` client,
`mysqldump` and MySQL Shell. Homes: the vendor reference manual at
dev.mysql.com (one manual per release series) and the `docker-library/mysql`
repository for the image.

Two release tracks: **LTS** series (fixes only; features are added or removed
only in a series' first release) and **Innovation** releases (may change
behaviour, remove deprecated features and add reserved words; each is
supported only until the next). Both are production quality. Image tags follow
the tracks: `lts`, `innovation` (also `latest`), and series tags such as `8.4`
with `8` as the major alias.

## Install, setup and configuration
- **Ports, paths, user.** 3306 (classic protocol) and 33060 (X protocol); data
  in `/var/lib/mysql`; command `mysqld`. Oracle-based images read
  `/etc/my.cnf`, which includes `/etc/mysql/conf.d/`; drop `.cnf` overrides
  there. Server options can also follow the image name as arguments
  (`--character-set-server=...`); `mysqld --verbose --help` lists them.
  `--user <uid>:<gid>` (anything but root) runs `mysqld` as that identity
  against a directory it can write.
- **Environment, first start only.** Every `MYSQL_*` variable is ignored once
  the data directory holds a database:
  - `MYSQL_ROOT_PASSWORD` is required unless `MYSQL_ALLOW_EMPTY_PASSWORD` or
    `MYSQL_RANDOM_ROOT_PASSWORD` (printed once to stdout as
    `GENERATED ROOT PASSWORD`) is set;
  - `MYSQL_DATABASE` creates a schema; `MYSQL_USER` plus `MYSQL_PASSWORD`
    (both needed, or no user is created and only a warning appears) gets
    `GRANT ALL` on that schema only; `MYSQL_USER=root` is refused;
  - `MYSQL_ROOT_HOST` defaults to `%`, so the entrypoint creates
    `root@'%'` with all privileges and grant option;
  - `MYSQL_ONETIME_PASSWORD` expires root's password after init;
    `MYSQL_INITDB_SKIP_TZINFO` skips the time-zone tables;
  - the `_FILE` suffix reads a value from a file, for `MYSQL_ROOT_PASSWORD`,
    `MYSQL_ROOT_HOST`, `MYSQL_DATABASE`, `MYSQL_USER` and `MYSQL_PASSWORD`
    only;
  - setting the client variable `MYSQL_HOST` in this image is known to cause
    trouble.
- **Initialization.** On first start the entrypoint runs a temporary server
  with networking off, sets root, drops the `test` schema, loads time zones,
  then runs `/docker-entrypoint-initdb.d/*.sh`, `*.sql` and compressed
  `*.sql.gz|bz2|xz|zst` in alphabetical order (SQL goes into
  `MYSQL_DATABASE`; a `.sh` without the execute bit is sourced), stops the
  temporary server and starts the real one. Nothing can connect until this
  ends. The scripts never run again once a `mysql` directory exists in the
  data directory.
- **No health check is built into the image**; the operator supplies one (see
  pitfalls on `mysqladmin ping`).
- **Authentication default.** New accounts use the plugin named by
  `authentication_policy`, `caching_sha2_password` by default;
  `IDENTIFIED WITH <plugin>` picks another per account.

## Core API / usage shape
```
docker exec <ctr> sh -c 'exec mysqldump --all-databases -uroot -p"$MYSQL_ROOT_PASSWORD"' > dump.sql
docker exec -i <ctr> sh -c 'exec mysql -uroot -p"$MYSQL_ROOT_PASSWORD"' < dump.sql
docker run --rm -it mysql mysql -h <host> -u <user> -p      # the image as a client
mysqladmin -h 127.0.0.1 -u <user> -p<pw> ping               # liveness, not auth
```
- **Logical backup**: `mysqldump`; for InnoDB, `--single-transaction` takes an
  online, consistent dump without table locks.
- **Physical backup**: copying files needs a stopped server (or locked and
  flushed MyISAM tables); InnoDB hot backup is the commercial product's
  feature.
- **Point-in-time recovery**: restore a full backup, then replay the binary
  log to the chosen point. Binary logging is on by default in the 8.4 line.
- **Accounts**: `CREATE USER 'app'@'%' IDENTIFIED BY ...;`
  `GRANT SELECT, INSERT, UPDATE, DELETE ON appdb.* TO 'app'@'%';`

## Idioms & best practices
- **The vendor security guidelines**: only root accounts may read
  `mysql.user`; grant no more than needed with `GRANT`/`REVOKE`; never grant
  to all hosts; check that `mysql -u root` without a password fails; store
  password hashes, never cleartext; firewall the server so 3306 is unreachable
  from untrusted hosts.
- **Read the transport guideline as written.** It says not to send
  unencrypted data "over the Internet" (use TLS or an SSH tunnel). It sets no
  rule for a private container network; citing it as a TLS mandate there is a
  misreading.
- **One account per consuming service**, scoped to its own schema (or tables,
  if schemas are shared). Observed in practice: root used by every service
  switched the privilege system off and let one leaked config expose every
  schema. The image's own `MYSQL_USER` already follows this shape.
- **Lock root down.** Set `MYSQL_ROOT_HOST` to `localhost` (or a narrow host)
  unless remote root is truly needed; the default `%` accepts it from
  anywhere.
- **Keep 3306 unpublished** or bound to loopback; Compose `expose:` or nothing.
  Observed in practice: reviving an old compose file brought a published port
  back.
- **Migrate accounts rather than re-enable a legacy plugin**:
  `ALTER USER ... IDENTIFIED WITH caching_sha2_password BY ...`. The legacy
  plugin is removed at the next major.
- **Review changed defaults at every LTS jump** and run MySQL Shell's upgrade
  checker before upgrading.
- **A volume is not a backup.** Schedule `mysqldump` (or binlog-based)
  copies off the host.
- Secrets through `_FILE` variables and Compose secrets, not literal
  environment values.

## General pitfalls
- **`mysqladmin ping` exits 0 even on `Access denied`**: the server answered.
  A ping health check proves the process is up, not that the credentials or
  schema work; add a real query for that.
- **Connections during init fail.** A dependent service started at the same
  time needs a retry loop or a Compose `service_healthy` gate.
- **Changing `MYSQL_*` later changes nothing.** On an existing data directory
  the variables are ignored; alter accounts with SQL.
- **Disabled legacy plugin, two symptoms.** `CREATE USER ... IDENTIFIED WITH
  'mysql_native_password'` fails with `ERROR 1524 ... is not loaded`
  (documented). Observed in practice: existing accounts that still use it
  fail to log in with `ERROR 1045 Access denied`, which looks like a wrong
  password; the manual pages read do not describe this symptom.
- **Restored dumps keep old plugins.** Observed in practice: a dump from an
  older major carried each account's plugin, so logins failed even with a new
  client. Check `SELECT user, host, plugin FROM mysql.user` before blaming the
  driver.
- **ORM dialect mismatch.** Observed in practice: a dialect written for an
  older major on a newer server ran with silent differences; prefer the ORM's
  auto-detection.
- **Patch-pinned tags never move.** A tag pinned to a full patch version gets
  no fixes; several servers on one host then lag together unnoticed. Series
  tags (`8.4`, `8`) move within the series.
- **Lowered memory limits.** `temptable_max_ram` on 8.4 is a share of total
  memory as the server sees it; inside a memory-limited container, set it
  explicitly.

## Testing
Upstream gives no test-container guidance. What the documented behaviour
implies, and what was observed in practice:
- wait for initialization to finish (a retry loop or a real-query health
  check), not only for the port;
- run the test container on the same series as production; a different
  series changes defaults and authentication;
- seed test data through `/docker-entrypoint-initdb.d`, which runs only
  against an empty data directory, so use a fresh (tmpfs or anonymous)
  volume per run;
- Testcontainers details live on the Java testing page, not here.

## Security defaults
- Root needs a password unless an opt-in variable says otherwise (upstream:
  an empty password "leaves your MySQL instance completely unprotected").
- Root is reachable from any host by default (`MYSQL_ROOT_HOST=%`).
- `caching_sha2_password` is the default authentication on the 8.4 line, for
  server and clients.
- The image only exposes ports in metadata; publishing them is the operator's
  choice.
- The image's `MYSQL_USER` gets all privileges on its schema, which is more
  than most applications need.

## Operational behaviour
- First start is slow (init, time-zone load, init scripts); later starts skip
  all of it.
- **Upgrade paths**: within an LTS series by in-place upgrade, dump and load,
  replication or clone; to the next LTS series by in-place upgrade, dump and
  load, or replication. An LTS series cannot be skipped (5.7 to 8.0 to 8.4).
  Downgrade rules were not confirmed for this page; read the downgrade chapter
  of the manual for the series in use.
- **Support**: an LTS series gets 5 years of premier and 3 years of extended
  support; an Innovation release only until the next one. Read the vendor's
  lifecycle table for dates.
- Clone between point releases of the same series is supported.

## Interop
- Clients authenticate with the plugin the account names; old drivers that
  lack `caching_sha2_password` support fail against new defaults.
- 33060 serves the X protocol for MySQL Shell and document-style clients.
- Compose wiring, health gating and secrets:
  [`container/docker-compose.md`](docker-compose.md).
- The JDBC driver and its connection-string flags:
  `library-corpus/maven/mysql-connector-j`.

## Major lines
### 8.0 to 8.4 LTS
- `mysql_native_password` is deprecated in 8.0, **disabled by default** in
  8.4 and removed in 9.0. On 8.4 it can be re-enabled with
  `--mysql-native-password=ON` (or `mysql_native_password=ON` under
  `[mysqld]`), and a client opts in with
  `--default-auth=mysql_native_password`. It is a bridge only: it blocks the
  next major.
- Changed defaults (8.0 → 8.4): `innodb_adaptive_hash_index` ON → OFF;
  `innodb_change_buffering` all → none; `innodb_flush_method` fsync →
  O_DIRECT where supported; `innodb_io_capacity` 200 → 10000;
  `innodb_log_buffer_size` 16 → 64 MiB; `innodb_numa_interleave` OFF → ON;
  `innodb_use_fdatasync` OFF → ON; `temptable_max_ram` 1 GiB → 3% of total
  memory within 1–4 GiB; `temptable_use_mmap` ON → OFF;
  `group_replication_consistency` EVENTUAL → BEFORE_ON_PRIMARY_FAILOVER.
- A server option set to `NULL` on the command line is now an error, except
  the TLS option family and path-like variables (`basedir`, `plugin_dir`,
  `socket`, ...).
- `WAIT_UNTIL_SQL_THREAD_AFTER_GTIDS()` is gone (a syntax error);
  `WAIT_FOR_EXECUTED_GTID_SET()` is the remaining GTID wait function.

### 8.4 to 9.x
- `mysql_native_password` no longer exists: migrate every account before the
  jump. The next LTS series after 8.4 lives in the 9 line; Innovation releases
  in between are not LTS.

## Upstream docs
- https://hub.docker.com/_/mysql (source: https://github.com/docker-library/docs/tree/master/mysql)
- https://github.com/docker-library/mysql
- https://dev.mysql.com/doc/refman/8.4/en/mysql-releases.html
- https://dev.mysql.com/doc/refman/8.4/en/security-guidelines.html
- https://dev.mysql.com/doc/refman/8.4/en/upgrade-paths.html
- https://dev.mysql.com/doc/refman/8.4/en/native-pluggable-authentication.html
- https://dev.mysql.com/doc/refman/8.4/en/caching-sha2-pluggable-authentication.html
- https://dev.mysql.com/doc/refman/8.4/en/backup-methods.html
- https://dev.mysql.com/doc/refman/8.4/en/point-in-time-recovery.html
- https://dev.mysql.com/doc/refman/8.4/en/mysqladmin.html
- https://dev.mysql.com/doc/refman/8.4/en/mysql-nutshell.html
