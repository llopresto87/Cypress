# redis — container

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a tool, not a record of one
> project's versions. For exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile / base-image tag. The
> Python client has its own page, [`pypi/redis.md`](../pypi/redis.md).

## What it is
Redis is an in-memory key-value data store used as a cache, a session store, a
message broker and a lightweight database. Its values are typed structures
(strings, hashes, lists, sets, sorted sets, streams), keys can carry a time to
live, and the server can persist its dataset to disk. In a containerized stack
it runs as one service from the official image, with its data directory
(`/data`) usually on a volume.

## Install, setup and configuration
- **Image facts.** Data directory `/data` (a declared volume); a first
  argument ending in `.conf` or starting with `-` gets `redis-server`
  prepended, so `redis-server /usr/local/etc/redis/redis.conf` or plain
  flags both work; upstream's persistence example is `--save 60 1`.
- **User.** The entrypoint fixes ownership of the data and config directories
  in the basic cases, then drops from root to the `redis` user and removes
  unneeded capabilities. `--user`, or (from the 8 line) `SKIP_FIX_PERMS=1` and
  `SKIP_DROP_PRIVS=1`, skip those steps.
- **Protected mode is off in the image.** The server's own default is
  `protected-mode yes` with `bind 127.0.0.1 -::1`, which accepts only loopback
  and Unix sockets while no password is set. The official image patches the
  compiled default to off (published ports are an explicit Docker decision),
  so a password-less container on a published port is open to anyone who
  reaches it. Set a password through a config or ACL file.
- **Memory.** `maxmemory` is unset and `maxmemory-policy` is `noeviction` by
  default: at a configured limit, writes that need memory fail; with no limit,
  the process grows until something outside kills it.

## Core API / usage shape
- **Commands over one protocol.** Clients send commands (`GET`, `SET` with
  `EX`, `HSET`, `EXPIRE`, …) over a single TCP port; a server can hold several
  numbered logical databases.
- **Authentication.** Two mechanisms: **ACL users**, named users each with
  their own password and a rule set limiting which commands and key patterns
  they may use; and the legacy **`requirepass`**, one password shared by every
  client.
- **ACL model.** `requirepass` only sets the password of the built-in
  `default` user; without an ACL file every client is `default` with
  `on nopass ~* &* +@all`. `ACL SETUSER` is incremental and a new user starts
  `off` with nothing granted. Rules: `on`/`off`, `>password`, `#<sha256>`,
  `~<key pattern>`, `&<channel>`, `+@<category>`/`-@<category>`,
  `+<cmd>|<subcommand>`. `ACL GENPASS` makes passwords. Users are declared
  either in `redis.conf` or in an `aclfile` (managed with `ACL LOAD`/`SAVE`),
  never both. Categories such as `@dangerous`, `@keyspace` and `@connection`
  group commands; `+@all` also covers module commands.
- **TLS** is optional and covers clients, replication and the cluster bus.
  Without it, `AUTH` crosses the network in clear text.
- **Persistence.** **RDB** writes point-in-time snapshots (`dump.rdb`) to the
  data directory; **AOF** appends every write to a log. Either, both or neither
  can be enabled.
- **Administrative commands.** `CONFIG GET/SET` changes server configuration at
  runtime, and `FLUSHDB` / `FLUSHALL` delete data.

## Idioms & best practices
- **Put the network control first.** Redis is designed for trusted clients in
  a trusted environment: keep the port off untrusted networks (expose it only
  on an internal network, never publish it to the host's public interfaces).
  Authentication is a second layer behind that, not a replacement for it.
- **Prefer ACL users to a shared password.** Give each consumer its own user,
  restricted to the commands and key patterns it needs, so a consumer that only
  reads one key family cannot read the others or wipe the instance.
- **Restrict dangerous commands with ACL rules.** Deny `CONFIG`, `FLUSHALL`,
  `FLUSHDB` and similar to application users. ACL rules are the supported
  mechanism; `rename-command` in `redis.conf` is the legacy one, which upstream
  marks deprecated and may remove.
- **Choose persistence deliberately.** Upstream presents persistence as a
  durability choice and documents running with none as a supported mode for a
  cache. Either disable it (`--save ""`, no AOF) and accept a cold start, or keep
  it and give the data volume the same retention, erasure and backup treatment
  as any other store.
- **Use TLS where the channel can be observed.**
- **Keep the secret off the command line.** `--requirepass` and
  `redis-cli -a` show up in `ps` and `docker inspect`; use a config or ACL
  file, and `REDISCLI_AUTH` for the CLI.
- **Use a long generated password.** Redis answers a very large number of
  `AUTH` attempts per second, so a short one falls to brute force.
- **For a cache, set `maxmemory` and an LRU or LFU policy**
  (`allkeys-lru`, `allkeys-lfu`, `volatile-*`), sized below the container's
  memory limit.
- **Running without persistence is valid only while every key can be rebuilt
  from a system of record.** Sessions, rate-limit counters, one-time tokens and
  locks cannot. Observed in practice: adding a write path that is not a cache
  needs a volume and a persistence mode in the same change. A cold cache after
  a restart is a miss storm on the system of record, not data loss; bound it.
- **AOF for durability**: `appendonly yes` with `appendfsync everysec` loses at
  most about a second. Switch a live instance with `CONFIG SET appendonly yes`
  first; editing the config and restarting can start from an empty AOF and
  lose the dataset.
- **Back up RDB files off the host.** They are safe to copy while the server
  runs; keep encrypted off-host copies and alert when a transfer stops. An
  unclean stop loses the writes since the last save.
- **Do not fight the entrypoint's user switch.** A `user:` override that
  breaks `/data` ownership stops persistence.
- **Remove an unused Redis completely.** A health-gated `depends_on` on it
  still holds dependents down; remove the edges, the secret and the client
  configuration together.

## General pitfalls
- **RDB snapshots are on by default.** Starting the image without a config file
  still writes snapshots of the dataset to the data directory, so the default,
  not a decision, puts the data on disk.
- **A TTL is not the whole retention story.** A key expiring in memory stops
  appearing in later snapshots, but a snapshot taken before expiry is a file on
  a volume that outlives the container. A cache holding personal data must
  either run without persistence or be treated as a store, including under the
  deletion and retention rules in
  [`contract-posture.md` §7](../../core/method/contract-posture.md).
- **`CONFIG` can relocate the dump file**, which an attacker with a connection
  can turn into writing files where the server user can write, and from there
  into code execution. It is an administrative command, not an application one.
- **One `FLUSHALL` deletes the whole dataset.** Any client that can reach an
  unrestricted connection can do it. Key patterns do not help: they restrict
  only commands that name keys, so `~app:* +@all` can still run `FLUSHALL`.
  Add `-flushall -flushdb -swapdb`, or `-@dangerous`.
- **Database indexes are not an access boundary.** ACLs cannot scope keys per
  logical database; a first-argument rule (`-select +select|0`) can pin a user
  to one index, but upstream marks that feature deprecated, and whole-database
  commands still need command rules.
- **The image is open by default** once a port is published (protected mode
  off, no password).
- **`noeviction` under a container limit** ends in write errors or an
  out-of-memory kill rather than eviction.
- **A floating tag can cross a licence boundary** (see Major lines); record
  `redis-server --version` from the running container.
- **A single shared password gives every consumer the same unrestricted
  reach.** Compromise of any one of them is compromise of every key family.

## Testing
- Assert from outside the container that an unauthenticated connection is
  refused, and that each application user is denied `FLUSHALL`, `CONFIG` and
  keys outside its pattern.
- Restart the container in a test and check the persistence mode does what the
  design says (data back, or a cold start that the application survives).

## Security defaults
- Server: protected mode on, bound to loopback. Image: protected mode off;
  the `default` user has no password and every permission until one is set.
- No TLS unless configured.
- The image drops to the `redis` user and trims capabilities.
- RDB snapshots are written by default (see pitfalls).

## Operational behaviour
- Single-threaded command execution: one slow command (`KEYS *`, a large
  `DEL`) stalls every client.
- Shutdown saves an RDB snapshot when save points are configured; a kill
  loses writes since the last save.
- Memory grows with the dataset until `maxmemory` is reached; then the policy
  decides between eviction and write errors.

## Interop
- The Python client: [`pypi/redis.md`](../pypi/redis.md).
- Compose secrets and health gating: [`docker-compose.md`](docker-compose.md).
- Valkey is the BSD-licensed fork for teams that need an OSI licence.

## Major lines
### 6 to 7
- ACL selectors, read and write key permissions (`%R~`, `%W~`) and
  subcommand rules arrived; the pub/sub default for new users became
  `resetchannels`, so a user needs explicit `&` channel rules.

### Licence boundary and the 8 line
- Releases up to the 7.2 line are BSD-3-Clause. Later releases are
  source-available under RSALv2 or SSPLv1 (not OSI-approved; internal use is
  allowed, the restriction targets competing managed services), and the 8 line
  adds AGPLv3 as a third option for new contributions. The change is not
  retroactive.
- The 8 line ships capabilities that were separate Stack modules (JSON,
  search, time series) as built-ins, and the image adds `SKIP_FIX_PERMS` and
  `SKIP_DROP_PRIVS`.

## Upstream docs
- https://redis.io/docs/latest/
- https://redis.io/docs/latest/operate/oss_and_stack/management/security/
- https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/
- https://hub.docker.com/_/redis
- https://redis.io/docs/latest/operate/oss_and_stack/management/security/acl/
- https://github.com/redis/redis/blob/unstable/redis.conf
- https://github.com/docker-library/redis
