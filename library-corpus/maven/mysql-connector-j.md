# mysql-connector-j — maven

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions: for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
MySQL Connector/J is Oracle's JDBC Type 4 driver for MySQL, published as
`com.mysql:mysql-connector-j` (driver class `com.mysql.cj.jdbc.Driver`). It
also implements the X DevAPI. The current line supports MySQL server 8.0 and
later and Java 8 or later; it implements JDBC 4.2, and a call to a JDBC 4.3 or
later method throws `SQLFeatureNotSupportedException`. The pre-rename
coordinate `mysql:mysql-connector-java` now resolves only to a relocation to
the new one. Upstream home: the Connector/J manual on dev.mysql.com (it
refuses scripted clients; Oracle's documentation mirror carries the same
text) and source on GitHub (`mysql/mysql-connector-j`).

MariaDB ships its own driver, `org.mariadb.jdbc:mariadb-java-client` (LGPL,
driver class `org.mariadb.jdbc.Driver`, URLs `jdbc:mariadb:`), which talks to
both MariaDB and MySQL servers. Its differences from Connector/J are in the
MariaDB section below.

Spring Boot manages both drivers' versions in its dependency BOM under these
current coordinates.

## Install, setup and configuration
- Add `com.mysql:mysql-connector-j` (runtime scope) and let the Boot BOM pick
  the version. `com.google.protobuf:protobuf-java` arrives transitively for the
  X DevAPI and can be excluded when only JDBC is used. The default logger is
  SLF4J-based; OpenTelemetry and OCI IAM support are optional and need their
  libraries added by the application.
- **URL.** `jdbc:mysql://host:port/db?prop=value&...`; host defaults to
  `localhost` and port to 3306 (33060 for the X protocol). Other schemes:
  `jdbc:mysql:loadbalance:`, `jdbc:mysql:replication:`, `mysqlx:`, and `+srv`
  variants for DNS SRV lookup. Per-host properties use
  `address=(host=...)(port=...)`.
- **Spring Boot.** Boot deduces the driver class from `spring.datasource.url`
  (`spring.datasource.driver-class-name` overrides). With no URL set, Boot
  falls back to an embedded database if one is on the class path. HikariCP is
  the preferred pool and comes with the JDBC and JPA starters.
- **TLS (`sslMode`).** DISABLED, PREFERRED (the default), REQUIRED, VERIFY_CA,
  VERIFY_IDENTITY. PREFERRED silently falls back to an unencrypted connection
  when the server offers no TLS, and it does not verify the server. `sslMode` replaces the deprecated `useSSL`,
  `requireSSL` and `verifyServerCertificate`. Trust and client key material go
  in `trustCertificateKeyStoreUrl`/`Type`/`Password` and
  `clientCertificateKeyStoreUrl`/...; `enabledTLSProtocols` and cipher
  properties narrow the handshake.
- **Authentication.** The driver follows the server's default authentication
  plugin and falls back to `caching_sha2_password`
  (`defaultAuthenticationPlugin`). `allowPublicKeyRetrieval` (default false)
  lets the driver fetch the server's RSA public key; `serverRSAPublicKeyFile`
  supplies it from a file instead. Without either, a non-TLS login that needs
  the key fails with "Public Key Retrieval is not allowed".
- **Time zone.** `connectionTimeZone` defaults to LOCAL (the JVM's zone);
  SERVER reads the session's zone, or give an explicit zone id. `serverTimezone`
  is now an alias for it (on early 8.0 releases it overrode the session zone).
  `forceConnectionTimeZoneToSession` (default false) also sets the session
  `time_zone`. `preserveInstants` (default true) converts instant-based values
  between the JVM and connection zones, for TIMESTAMP on write and for
  TIMESTAMP, DATETIME or character columns on read.
- **Character set.** When neither `characterEncoding` nor
  `connectionCollation` is set, current drivers use utf8mb4. For 4-byte UTF-8,
  set `character_set_server=utf8mb4` on the server and leave both properties
  out.
- **Timeouts.** `connectTimeout` and `socketTimeout` default to 0, which means
  no timeout (milliseconds otherwise). `tcpKeepAlive` defaults to true.
- **Catalog or schema.** `databaseTerm` (default CATALOG) decides whether the
  JDBC catalog or the JDBC schema stands for a MySQL database. With the default,
  `setSchema()` and schema filters in metadata calls do not select a database.
- **Type mapping defaults.** `tinyInt1isBit` (default true) maps TINYINT(1) to
  BIT/Boolean; `zeroDateTimeBehavior` (default EXCEPTION) throws on an all-zero
  date; `yearIsDateType` (default true) maps YEAR to a date.

## Core API / usage shape
- Plain JDBC: `DriverManager.getConnection(url, user, password)` finds the
  driver through the service loader. Applications use a pool instead.
- Prepared statements: `cachePrepStmts` (default false) caches statement
  parsing; `useServerPrepStmts` (default false) uses server-side prepared
  statements, which the server caps with `max_prepared_stmt_count`.
- Batching: `rewriteBatchedStatements` (default false) rewrites an
  `executeBatch()` of INSERT or REPLACE statements into multi-value statements
  and uses multi-queries whatever `allowMultiQueries` says. The manual warns
  that it can open SQL injection with plain statements and unsanitized input,
  that `getGeneratedKeys()` works only if the whole batch is INSERT or REPLACE,
  and that `INSERT ... ON DUPLICATE KEY UPDATE` needs care.
- Streaming: `useCursorFetch=true` with a fetch size above zero
  (`defaultFetchSize` or `setFetchSize()`) reads results through a server
  cursor; it turns `useServerPrepStmts` on.
- Generated keys: `Statement.getGeneratedKeys()` returns AUTO_INCREMENT values.
- Multi-host: failover, load-balanced and source/replica URLs are handled in
  the driver.

## Idioms & best practices
- Use a pool (HikariCP under Boot), never `autoReconnect`; validate pooled
  connections and treat SQLState `08S01` as a network failure.
- Set `connectionTimeZone` explicitly to a fixed zone such as UTC, and keep
  the JVM and session zones consistent. The manual recommends a monotonic zone
  to avoid wrong `getTimestamp()` values on daylight-saving switch days.
- Require TLS with certificate checks in production:
  `sslMode=VERIFY_IDENTITY` (or VERIFY_CA), not the default.
- When both the MySQL and MariaDB drivers are on the class path, give the
  MariaDB driver `jdbc:mariadb:` URLs so the right driver claims each URL.
- One codebase can carry the MySQL, MariaDB and embedded (H2) drivers and pick
  one per profile: Boot deduces the driver from the URL. Observed in practice:
  the Hibernate dialect then follows the connection too; Boot's docs do not
  cover that part.

## General pitfalls
- **`allowPublicKeyRetrieval=true` without TLS.** It makes a
  `caching_sha2_password` login work, but the key comes over an unauthenticated
  channel, so a man in the middle can substitute it. Prefer TLS. (The server
  manual states the TLS-or-RSA rule; the man-in-the-middle exposure follows
  from it.)
- **Re-enabling `mysql_native_password` is a dead end.** It is deprecated on
  the 8.0 line, disabled by default on the 8.4 LTS line, and removed on the 9
  line.
- **`autoReconnect`** is deprecated and not recommended: a silent reconnect can
  corrupt connection or transaction state.
- **"Communications link failure"** after idle periods: the protocol does not
  ping, firewalls drop idle connections, and the server closes connections
  idle past `wait_timeout`. Let the pool validate and retire connections.
- `allowMultiQueries` and `rewriteBatchedStatements` change statement parsing
  and widen the SQL-injection surface; leave them off unless needed.
- `elideSetAutoCommits` is ignored (disabled because of a known bug).
  `java.sql.Date` is not proleptic, so dates before the Julian-Gregorian
  cutover differ from what the server stores.
- `tinyInt1isBit` and `zeroDateTimeBehavior` defaults surprise code that
  expects integers or nulls.

## Testing
- Behaviour that depends on driver properties (time-zone conversion, batch
  rewriting, prepared-statement caching) is reproduced only by the real
  engine. Observed in practice: run those tests against MySQL or MariaDB in a
  container; the upstream pages describe the engine-specific behaviour but give
  no testing advice. An embedded H2 is fine for fast tests that do not depend
  on it (see [`h2.md`](./h2.md)).

## Security defaults
- Connector/J defaults: `sslMode=PREFERRED` (encrypted only if the server
  offers TLS, and the server is never verified), `allowPublicKeyRetrieval=false`,
  `allowLoadLocalInfile=false`, `allowMultiQueries=false`,
  `allowUrlInLocalInfile=false`.
- Only VERIFY_CA or VERIFY_IDENTITY protect against an active attacker.
- MariaDB driver defaults differ: `sslMode=disable` and
  `allowLocalInfile=true`. The MariaDB guide calls client-side local infile a
  security concern, so turn it off unless needed.

## Operational behaviour
- Pooling avoids connection set-up cost and the build-up of sockets in
  TIME_WAIT.
- Logging goes through SLF4J (`Slf4JLogger`). From the 8.4 line on, the
  driver can emit OpenTelemetry traces once the application adds the
  OpenTelemetry libraries.
- With `connectTimeout`/`socketTimeout` at their default of 0, a dead server
  can hang a connect or a query indefinitely; set both, or rely on the pool's
  timeouts.

## Interop
- **Spring Boot / HikariCP:** driver deduction from the URL, Hikari as the
  default pool, embedded fallback when no URL is set.
- **Hibernate:** on MySQL a schema is the database; with the default
  `databaseTerm=CATALOG`, a mapped `schema` has no database meaning. Observed in
  practice: this is why a schema-qualified mapping that is inert on MySQL
  breaks on H2 (see [`h2.md`](./h2.md) and
  [`hibernate-orm.md`](./hibernate-orm.md)).
- **Testcontainers:** a real server for tests; see
  [`testcontainers.md`](./testcontainers.md).

## MariaDB Connector/J
- Coordinates `org.mariadb.jdbc:mariadb-java-client`, URLs `jdbc:mariadb:`.
  The 3.x line accepts only `jdbc:mariadb:` unless `permitMysqlScheme` is set.
- URL options and defaults: `sslMode` (disable by default; trust, verify-ca,
  verify-full), `allowPublicKeyRetrieval` false, `connectTimeout` 30000 ms,
  `socketTimeout` 0, `allowLocalInfile` true, `cachePrepStmts` true,
  `useServerPrepStmts` false, `useBulkStmts` false, `autocommit` true.
  `serverTimezone` was removed on 3.x in favour of `connectionTimeZone`
  (LOCAL, SERVER or a zone id).
- `MariaDbDataSource` opens a new connection per call; `MariaDbPoolDataSource`
  is a pool (`maxPoolSize` default 8, `minPoolSize` defaults to
  `maxPoolSize`; also `maxIdleTime`, `poolValidMinDelay`, JMX monitoring).
  With an external pool, configure `org.mariadb.jdbc.Driver`.
- With a non-fixed `connectionTimeZone`, a timestamp can come back shifted by
  an hour across daylight-saving rule changes; store instants in TIMESTAMP
  columns, not DATETIME.

## Major lines
### Coordinates: `mysql:mysql-connector-java` to `com.mysql:mysql-connector-j`
- The old coordinate's last releases are relocation POMs pointing at the new
  one. The Boot 3.0 migration guide requires the new coordinate, and the
  current Boot BOM manages only the new one.

### Connector/J 5.1 to 8.x
- The property set was refactored (the manual has an upgrade chapter) and the
  driver class became `com.mysql.cj.jdbc.Driver`. Within the 8.0 line,
  `sslMode` replaced the boolean TLS flags, `connectionTimeZone` with
  `preserveInstants` replaced the old `serverTimezone` behaviour, and utf8mb4
  became the default encoding. A project moving from an early 8.0 release
  should re-check all three.

### Connector/J 9.x
- `caching_sha2_password` is the default fallback authentication plugin, and
  methods deprecated for insensitive terminology are removed. The 8.4 line
  before it dropped FIDO authentication.

### MariaDB Connector/J 2.x to 3.x
- `jdbc:mysql:` URLs are no longer accepted by default, `serverTimezone` is
  gone, and prepared statements are cached more aggressively: the upgrade
  guide warns the server's `prepared_stmt_count` can rise sharply, so watch it
  after upgrading.

## Upstream docs
- https://dev.mysql.com/doc/connector-j/en/ (mirror: https://docs.oracle.com/cd/E17952_01/connector-j-en/)
- https://github.com/mysql/mysql-connector-j
- https://dev.mysql.com/doc/refman/8.4/en/caching-sha2-pluggable-authentication.html
- https://mariadb.com/docs/connectors/mariadb-connector-j/about-mariadb-connector-j
- https://docs.spring.io/spring-boot/reference/data/sql.html
