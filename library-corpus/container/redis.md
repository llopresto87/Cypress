# redis — container

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a tool, NOT a version-pinned page. For
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile / base-image tag. The Python client has its own page,
> [`pypi/redis.md`](../pypi/redis.md).

## What it is
Redis is an in-memory key-value data store used as a cache, a session store, a
message broker and a lightweight database. Its values are typed structures
(strings, hashes, lists, sets, sorted sets, streams), keys can carry a time to
live, and the server can persist its dataset to disk. In a containerized stack
it runs as one service from the official image, with its data directory
(`/data`) usually on a volume.

## Core API / usage shape
- **Commands over one protocol.** Clients send commands (`GET`, `SET` with
  `EX`, `HSET`, `EXPIRE`, …) over a single TCP port; a server can hold several
  numbered logical databases.
- **Authentication.** Two mechanisms: **ACL users**, named users each with
  their own password and a rule set limiting which commands and key patterns
  they may use; and the legacy **`requirepass`**, one password shared by every
  client.
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
  unrestricted connection can do it.
- **A single shared password gives every consumer the same unrestricted
  reach.** Compromise of any one of them is compromise of every key family.

## Upstream docs
- https://redis.io/docs/latest/
- https://redis.io/docs/latest/operate/oss_and_stack/management/security/
- https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/
- https://hub.docker.com/_/redis
