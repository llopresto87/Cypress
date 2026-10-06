# mongo — container

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a server image, not a record of
> one project's versions. For exact pins, advisories and per-release behavior,
> run `ingest-library` against the project's own image tag. The page is named
> for the official image, `mongo`; the server is MongoDB.

## What it is
MongoDB is a document database; `mongod` is its server. The official `mongo`
image (docker-library, Ubuntu base) packages the community server with
`mongosh` and the database tools (`mongodump`, `mongorestore`); a build
argument can select the enterprise package instead. Deployment shapes are a
standalone, a replica set and a sharded cluster; upstream advises a standalone
for test and development only. Users live in an authentication database and
hold roles per database. Homes: the vendor manual at mongodb.com/docs and the
`docker-library/mongo` repository. Server versions after the licence change
are under SSPLv1.

## Install, setup and configuration
- **Image layout.** Port 27017; command `mongod`; data in `/data/db` and
  config-server data in `/data/configdb`, both declared volumes. A `mongodb`
  user (uid 999) owns them: started as root, the entrypoint fixes ownership
  and re-executes as `mongodb` through `gosu`. `mongod` reads no config file
  unless `--config <path>` follows the image name; any other `mongod` flag can
  follow it too.
- **Environment, first start only** (ignored once the data directory holds a
  database):
  - `MONGO_INITDB_ROOT_USERNAME` and `MONGO_INITDB_ROOT_PASSWORD` together
    create a `root`-role user in the `admin` database and start `mongod` with
    `--auth`; both accept a `_FILE` form;
  - `MONGO_INITDB_DATABASE` is the database the `*.js` init scripts run
    against (`test` when unset). MongoDB creates a database only when data is
    written to it.
- **Initialization.** The entrypoint runs a temporary `mongod` on
  `127.0.0.1` without auth, replica set or key file, runs
  `/docker-entrypoint-initdb.d/*.sh` (sourced) and `*.js` (through the shell)
  in alphabetical order, ignores other files, shuts the temporary server down
  and starts the real one. It unsets every `MONGO_INITDB_*` variable before
  that start.
- **Bind address.** `mongod` itself binds to `localhost` by default. The image
  adds `--bind_ip_all` unless `--bind_ip`, `--bind_ip_all` or `net.bindIp` is
  given, so the container listens on every interface.
- **Authorization** is off in the server by default; the image turns it on
  only through the two root variables.
- **Authentication mechanisms** (community): SCRAM (default) and X.509. Replica
  set and shard members authenticate to each other with a key file
  (`security.keyFile`) or X.509; a key file also switches on access control.
  LDAP proxy and Kerberos are enterprise.
- On Windows and macOS hosts, bind-mounting the data directory into a Linux
  image does not work (memory-mapped files); use a named volume.

## Core API / usage shape
```
mongosh --host <name> -u <user> -p <pw> --authenticationDatabase admin <db>
docker exec <ctr> sh -c 'exec mongodump --archive -u "$U" -p "$P" --authenticationDatabase admin' > db.archive
db.adminCommand({ getParameter: 1, featureCompatibilityVersion: 1 })
db.adminCommand({ setFeatureCompatibilityVersion: "<major>", confirm: true })
db.adminCommand('ping')
```
- **Shell.** Current images ship `mongosh`; the legacy `mongo` shell belongs to
  old (4.x) tags, and init `.js` files run with `mongo` only below major 6.
  `mongosh` deprecates several legacy collection methods (`insert`, `remove`,
  `save`, `update`, `count`); a `mongocompat` snippet restores some.
- **Feature compatibility version (FCV)** gates features that change the
  on-disk format. Upgrade procedure for a standalone, one major at a time
  (from the series immediately before the target):
  1. read the FCV; it must equal the running major;
  2. shut down cleanly (`shutdown: 1`);
  3. replace the binaries (change the image tag);
  4. check `mongod --version`;
  5. set the new FCV with `confirm: true` (required since the 7 line).
  Upgrading the FCV over forward-incompatible data fails with `CannotUpgrade`;
  an unfinished FCV change blocks the opposite change until it completes.
- **Users**: create a user administrator first
  (`userAdminAnyDatabase` in `admin`), then one least-privilege user per
  application with `roles` on its own database and, where useful,
  `authenticationRestrictions` (client source and server address).

## Idioms & best practices
- **Follow the vendor security checklist** in order: access control and
  authentication; role-based access control; TLS for every connection; data
  encryption and file protection; limited network exposure (`net.bindIp`,
  firewall, `clusterIpSourceAllowlist`, `authenticationRestrictions`); audit;
  a dedicated OS user; secure configuration options; a STIG where applicable;
  compliance. Then keep checking: advisories, end-of-life dates, network rules,
  user review and rotation.
- **Access control and RBAC are two separate checks.** Every client connecting
  as root passes the first and fails the second.
- **Turn off server-side JavaScript** (`--noscripting`) when `mapReduce`,
  `$where`, `$accumulator` and `$function` are unused.
- **Encryption and audit on the community image.** The encrypted storage
  engine and auditing are enterprise-only: record them as "not available in
  this edition" and use disk encryption plus file permissions instead.
- **Collect logs centrally**: they hold authentication attempts with source
  addresses. Keep antivirus and EDR off the data and log paths; scanning them
  can quarantine files and corrupt the database.
- **Prefer a replica set even for one server** in anything beyond a quick
  test: it unlocks change streams and transactions, and upstream suggests
  converting a standalone before upgrading.
- **Move to the current patch of the running major first.** Observed in
  practice: it needs no FCV decision and shortens the major upgrade.
- **Snapshot before an FCV change.** Observed in practice; upstream advises
  testing in staging and a burn-in period before enabling
  backward-incompatible features, which keeps a downgrade simple.

## General pitfalls
- **Without the root variables, the image listens on every interface with no
  authentication.** The server's safe localhost default is overridden by the
  entrypoint.
- **Wrong mount, empty database.** A volume mounted anywhere but `/data/db`
  persists nothing; every recreate starts empty.
- **Changing `MONGO_INITDB_*` later changes nothing** on an existing data
  directory.
- **The localhost exception** applies only while no users or roles exist: it
  lets a local connection create the first user (which ends it), initiate a
  replica set and read its status. Create the first user in `admin` with a
  role that can create users. On a sharded cluster it applies to each shard and
  each `mongos`; `enableLocalhostAuthBypass=0` turns it off.
- **A standalone has no transactions and no change streams.** The manual says
  transactions need a "multiple node replica set". Observed in practice: a
  single-node replica set (as test containers bootstrap) runs transactions for
  testing; the manual does not discuss that shape.
- **FCV and binaries must stay within one major.** Check the FCV before
  changing the tag. Observed in practice: binaries more than one major ahead
  of the FCV refused to start; the pages read do not state this.
- **Setting the FCV back mid-change does not restore the old state.**
- **Drivers and server move together**: drivers released more than three years
  after a server version's end of life are not compatible with it.
- **Re-check a cited blocker.** Observed in practice: a carried-forward
  upstream ticket was already resolved; re-read its status and re-test on the
  real host before acting on it.

## Testing
- A ping-only test (`db.adminCommand('ping')` through `mongosh`) proves
  connectivity, nothing more. The image defines no health check; supply one.
- Code that uses transactions or change streams must be tested against a
  replica set; a standalone container fails those calls.
- Seed data through `/docker-entrypoint-initdb.d`, which runs only against an
  empty data directory, so give each run a fresh volume.
- Testcontainers' MongoDB module details live on the Java testing page.

## Security defaults
- Server: authorization off, bind to localhost.
- Image: authorization on only with both root variables; bind to all
  interfaces.
- No TLS is enabled by the image; the checklist asks for TLS on every
  connection.
- The `root` role created by the image can do everything; never hand it to an
  application.

## Operational behaviour
- First start runs init through a temporary server; later starts skip it.
- Upgrades go one major at a time and need an FCV step after each. Later
  releases of the 8 line document a one-step FCV downgrade to the previous
  version; check the `setFeatureCompatibilityVersion` page of the release in
  use.
- **Lifecycle**: each server major has its own end of life in the vendor's
  lifecycle table; recent majors get about four to five years from release.
  Read the table for the major in use. The image tags carry no support window
  of their own. Rapid releases between majors have short windows.

## Interop
- `mongodump`/`mongorestore` ship in the image.
- `mongo-express` is the image README's own Compose partner; it connects with
  a credential-bearing URL, so keep it off public networks.
- Compose wiring and secrets:
  [`container/docker-compose.md`](docker-compose.md).
- Driver and server versions are coupled (see pitfalls); the Spring Data side
  has its own page.

## Major lines
- **Shell**: 4.x tags use `mongo`; later tags use `mongosh`; init scripts use
  `mongo` below 6 and `mongosh` from 6.
- **7 line**: `setFeatureCompatibilityVersion` requires `confirm: true`.
- **8 line**: later releases document a one-step FCV downgrade to the
  previous version (check the `setFeatureCompatibilityVersion` page of the
  release in use); an FCV below 8.0 on a cluster first needs
  `transitionToDedicatedConfigServer`.
- Image-level differences of the 9 line beyond tag names were not found in
  the pages read.

## Upstream docs
- https://hub.docker.com/_/mongo (source: https://github.com/docker-library/docs/tree/master/mongo)
- https://github.com/docker-library/mongo
- https://www.mongodb.com/docs/manual/administration/security-checklist/
- https://www.mongodb.com/docs/manual/core/localhost-exception/
- https://www.mongodb.com/docs/manual/tutorial/enable-authentication/
- https://www.mongodb.com/docs/manual/reference/command/setFeatureCompatibilityVersion/
- https://www.mongodb.com/docs/manual/release-notes/8.0-upgrade-standalone/
- https://www.mongodb.com/docs/manual/core/transactions-production-consideration/
- https://www.mongodb.com/docs/mongodb-shell/reference/compatibility/
- https://www.mongodb.com/legal/support-policy/lifecycles
