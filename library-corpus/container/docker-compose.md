# docker-compose — container

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a tool, not a record of one
> project's versions. For exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile / compose-file version.

## What it is
Docker Compose defines and runs multi-container applications from a declarative
YAML file. It brings up a set of services together, wiring them onto a shared
network with named volumes for persistence. The modern form is the **v2 Compose
plugin**, invoked as `docker compose` (a subcommand of the Docker CLI) rather
than the older standalone `docker-compose` binary.

## Install, setup and configuration
- **Packaging.** Docker's apt repository ships the v2 plugin as
  `docker-compose-plugin`; some distributions package it under their own name;
  a distribution package named plain `docker-compose` was historically v1. See
  Major lines before trusting a hyphenated command.
- **File discovery.** Without `-f`, Compose looks for `compose.yaml` and
  `compose.override.yaml` in the working directory and its parents; `-f -`
  reads stdin.
- **Project name**, highest first: `-p`; `COMPOSE_PROJECT_NAME`; top-level
  `name:` (the last one among several `-f` files); the base name of the
  project directory (the first file's directory). Names are lowercase
  letters, digits, dashes and underscores, starting with a letter or digit.
  The project name is the isolation unit: a second name brings up a second
  full stack beside the first.
- **Interpolation sources**, highest first: the shell environment, then
  `--env-file`, then the project's `.env` (read only when `--env-file` is not
  given). That `.env` comes from the project directory (`--project-directory`
  if set, else the directory of the first `-f` file, else the current
  directory), not necessarily where you run the command. A stale shell export
  therefore silently masks the file. `.env` feeds interpolation only: a value reaches a container only
  through `${VAR}` in `environment:` or through `env_file:`.
- **Container environment precedence**, highest first: `docker compose run
  -e`; an `environment:` or `env_file:` entry whose value is interpolated;
  a literal value in `environment:`; `env_file:`; the image's `ENV`. A literal
  in `environment:` is therefore beyond the reach of every env channel short
  of `run -e` or a later `-f` overlay key, which projects use on purpose to
  lock a value.

## Core API / usage shape
- **Services**: each service names an image (or build context), environment,
  ports, volumes, and dependencies; `docker compose up` starts the whole stack.
- **Networking**: services on one Compose project share a default bridge network
  and reach each other by **service name** as a hostname, with no hard-coded IPs.
- **Named volumes**: declared volumes persist data across container restarts and
  recreations, independent of the container filesystem.
- **Interpolation**: `${VAR}` (or unbraced `$VAR`) in the file is substituted
  from the sources listed under Install. Four forms control what happens when
  the value is missing:

  | form | result |
  |---|---|
  | `${VAR:-default}` | `VAR` if set **and non-empty**, else `default` |
  | `${VAR-default}` | `VAR` if set (even empty), else `default` |
  | `${VAR:?error}` | `VAR` if set **and non-empty**, else exit with `error` |
  | `${VAR?error}` | `VAR` if set (even empty), else exit with `error` |

  The alternate-value forms `${VAR:+replacement}` and `${VAR+replacement}`
  substitute only when `VAR` is set; they never guard. Interpolation runs over
  the whole project model at load, so one unset `${VAR:?}` anywhere aborts
  every command, including `up` of an unrelated service, `config` and `down`.

- **`docker compose config`** prints the fully resolved model (includes
  followed, `-f` files merged, variables interpolated) without needing a
  running daemon. `--no-interpolate` prints the merged structure with
  references unresolved (no environment needed), `--environment` shows what
  interpolation used, and `--images`, `--services`, `--volumes`,
  `--profiles` list the parts. It is the native oracle for "what will this stack
  run with"; the
  [`layered-config-merge-verifier`](../../tool-corpus/ops/layered-config-merge-verifier.md)
  tool builds on it.
- **Assembly**: top-level `include:` pulls in other Compose files and is
  resolved by `config`; unlike `-f` it is not an override merge, so a service
  or volume name defined in two included files conflicts. `profiles:` opts a
  service out of the default `up`: it starts only with `--profile` or
  `COMPOSE_PROFILES` (an overlay can switch a base service off by giving it a
  profile). Top-level `x-` keys are extension fields Compose ignores, the
  usual home of YAML anchors.
- **`up -d --wait [--wait-timeout N]`** blocks until services are running or
  healthy.
- **Remote daemon**: setting `DOCKER_HOST=ssh://<host>` targets a remote Docker
  daemon over SSH, so `docker compose` can build/run a stack on another machine
  while driven locally. Because v2 is a Docker CLI plugin, the root flags work
  too: `docker -H …` and `docker --context <ctx> compose …`.

## Merge semantics of multiple -f files
- Mappings merge per key and the later file wins; `environment` and `labels`
  merge per variable name.
- Plain sequences append: `expose`, `dns`, `dns_search`, `tmpfs`, `cap_add`
  in an overlay add to the base.
- Some keys replace instead: `command`, `entrypoint`, `healthcheck.test`.
- Some sequences are keyed so entries stay unique: `volumes`, `secrets` and
  `configs` by container `target`; `ports` by `{ip, target, published,
  protocol}`. An overlay entry with the same key merges; a different key is
  added, so an overlay port with another host port is published **in addition**
  to the base one.
- `!override` replaces an attribute wholesale and `!reset` removes it
  (upstream recommends `!reset null` or `!reset []`). Both need a reasonably
  recent v2, so check the host's Compose version.
- A YAML `<<:` merge is shallow and per file: a local key replaces the
  anchor's whole value, and a list such as `cap_add` cannot be subtracted from,
  so declare the full set (observed in practice; this is YAML behaviour, not a
  Compose rule).
- A docker-less lint needs a YAML loader that resolves `<<` (PyYAML's
  SafeLoader does); it checks structure only and is no substitute for
  `config`.

## Networks
- `internal: true` gives a network no external connectivity, egress
  included; it is the documented way to keep datastores off the host.
- On an `external: true` network Compose creates nothing and ignores
  `internal`, `ipam` and `driver`. Observed in practice: when another file of
  the merged project declared the same network as owned, `external` won and
  the isolation and subnet were dropped silently; a bare `docker network
  create` pre-step does the same.
- Give a shared network one deliberate owner: one project owns it, or it is
  pre-created and declared external everywhere. Otherwise the first project up
  creates it and the result depends on bring-up order. A missing external
  network fails `up`.
- A network `name:` is used verbatim, without the project prefix.
- A container off a network cannot even resolve that network's names, which
  makes per-service private networks a real boundary.
- A datastore needs `expose:` or nothing, never `ports:`; only `ports:`
  touches the host.
- Add `aliases:` when a service name is not a legal URI hostname (an
  underscore breaks strict URI parsers).
- A network alias equal to an external hostname resolves to the aliased
  container for every member of that network, which makes a self-loop through
  embedded DNS when a proxy on that network resolves the name. Map the name on
  the client with `extra_hosts` instead (mechanism on
  [`nginx.md`](nginx.md)).

## Startup order, health and restart
- `depends_on` long form: `condition` is `service_started` (the short form's
  behaviour), `service_healthy` or `service_completed_successfully` (for init
  or migration jobs). `restart: true` restarts the dependent after an explicit
  Compose restart of the dependency (not after an engine auto-restart);
  `required: false` only warns when the dependency is missing. Shutdown runs in
  reverse order.
- Healthcheck fields: `test` (`CMD` exec form or `CMD-SHELL`), `interval`,
  `timeout`, `retries`, `start_period`; `$$VAR` works only in the shell form;
  `test: ["NONE"]` or `disable: true` turns off an image's check.
- Under `service_healthy`, a check that never passes hangs startup (`up --wait`
  waits to its timeout), and one that passes too early is a race. Write the
  healthcheck before the `depends_on`, and run it by hand in the container.
- `restart:` is `no` (the default), `always`, `on-failure[:max-retries]` or
  `unless-stopped`. With no `restart:`, a service stays down after a reboot;
  `always` and `unless-stopped` differ only for a container stopped on
  purpose. A restart policy applies to containers that exist; it is not boot
  automation for a stack that was never brought up.

## Secrets
- Top-level `secrets:` (from a `file:` or an `environment:` variable) are
  granted per service and appear read-only at `/run/secrets/<name>`; the long
  syntax adds `target`, `uid`, `gid`, `mode`. Without Swarm a secret is a
  bind-mounted host file, not encrypted, and works for Linux containers only.
- Upstream names credentials in environment variables as an exposure risk
  (logs, debugging). `*_FILE` variables are an image convention (the official
  database images support them), not a Compose feature; check the image.
- Secret material that must never reach host disk goes on `tmpfs`.

## Idioms & best practices
- Address other services by their service name over the shared network rather
  than by IP or published port, and publish a port only for the stack's actual
  edge. Anything sensitive that host-side tooling must still reach (a database,
  a broker, an admin or metrics surface) binds to loopback
  (`127.0.0.1:<port>:<port>`) instead of `0.0.0.0`, and services are segmented
  onto named bridge networks. Why loopback binding stays mandatory even behind
  a host firewall belongs to
  [`docker-host-hardening.md`](./docker-host-hardening.md).
- Use named volumes for anything that must survive container recreation; keep
  the volume mount path aligned with where the process writes.
- Keep environment-specific values in `.env` / environment interpolation, and
  layer overrides with multiple compose files rather than editing the base: one
  base file plus a per-environment overlay merged with repeated `-f` (dev / qa /
  prod), never a hand-edited base.
- For a value whose absence must stop the deploy, use a `:?` form, or a
  resolver upstream of Compose that fails on an empty value. Give a value that
  is allowed to be blank an explicit `:-` default that matches the
  application's own fallback, so the two cannot disagree.
- Assert effective values against `docker compose config` output. Grepping the
  source files cannot do it, because they cannot see merges, overlays or
  interpolation.
- Leave out the top-level `version:` key. It belongs to the legacy
  schema-versioned file format. The supported mechanism, the Compose
  Specification, keeps it for backward compatibility only: the value is
  ignored, the latest schema validates the file, and Compose warns that the key
  is obsolete.
- Give every long-lived service a `healthcheck`, and make dependents wait on
  readiness with `depends_on: {<svc>: {condition: service_healthy}}`. Startup
  order should follow actual readiness, not just container creation. A service
  with no HTTP surface needs a non-HTTP check (`pg_isready`, `mysqladmin ping`,
  a process or socket test): a service with no healthcheck
  cannot be a `service_healthy` target. Disable only an inherited check that
  cannot pass in that service.
- Docker's "Compose in production" guidance asks for five changes: no
  bind-mounted code, different host ports, a different environment, a
  `restart:` policy, and operational services (logging, monitoring). It asks
  for no registry, orchestrator, secrets manager or multi-host setup, so
  single-host Compose is a legitimate production shape. Apply the changes as an
  overlay.
- Guard a variable at every reference. A lone `:?` covers the other
  references only by accident; a variable that is bare everywhere needs its own
  inventory.
- One shared hardening anchor (`security_opt: [no-new-privileges:true]`,
  `cap_drop: [ALL]`) under an `x-` key, then a minimal `cap_add` per service.
- Set `deploy.resources.limits`; without them nothing caps a container's CPU
  or memory, whatever a runtime's heap flags say.
- Avoid `container_name:`: it pins one name, so the service cannot scale and
  two projects on one host collide.

## General pitfalls
- **Relative bind-mount paths resolve on the REMOTE host's filesystem** when
  using a remote daemon (`DOCKER_HOST=ssh://`). Observed in practice: a
  `./path` bind mount was expanded on the client and then looked up on the
  remote host as an absolute path, so a local-looking path silently mounted a
  non-existent or wrong directory there (upstream says only that relative host
  paths are supported for local runtimes). Prefer named volumes (or absolute, remote-correct paths) for
  remote daemons.
- **An unresolved variable with no default becomes an empty string, with only a
  warning, and the stack deploys.** A bare `${VAR}` that nothing sets does not
  stop Compose, so a blank password, audience or salt reaches the container.
  Only the `?` forms (or a check outside Compose) turn a missing value into a
  failure. Watch too for any tool upstream that pre-blanks unresolved values
  before Compose sees them; each such layer is another place a missing value
  goes quiet.
- **`docker compose restart` may not pick up a changed env file.** It restarts
  the existing container with the configuration it was created with. Recreate
  the affected services (`up -d` on them, or `--force-recreate`) instead, and
  remember that recreation re-runs the entrypoint and everything it does.
- **`$VAR` in a `command:` / healthcheck string is expanded by Compose (the host
  side) at parse time**, not by the container's shell, unless you escape it
  (`$$VAR`) or defer it by invoking a shell inside the container. An unescaped
  variable either resolves to a host value or empties out.
- **A named-volume mount path must match the directory the process actually
  writes to**, or data silently never persists: the process writes to the
  container layer while the volume sits mounted elsewhere, and everything looks
  fine until the container is recreated and data is gone.
- **First-start initialisation reads the environment once.** An image that
  initialises its volume on first start (database init and seed scripts, a
  generated certificate or key) skips that step whenever the volume already
  holds data, so a later change to the variables that drove it does nothing.
  Remove that volume to apply the change, and name the volume to delete next to
  the setting. The database images' own first-start rules are on their pages
  ([`postgres.md`](postgres.md), [`mysql.md`](mysql.md)).
- **`--remove-orphans` is scoped to the whole project, not to the `-f` files you
  passed.** Plain `down` only touches services declared in the files handed to
  the command, but `--remove-orphans` widens removal to every container of the
  resolved project (matched by `COMPOSE_PROJECT_NAME`), regardless of which `-f`
  subset you passed. So if several invocations manage different `-f` subsets
  under one project name, `--remove-orphans` on one deletes containers another
  declared, and exits 0 while doing it. Give the flag only to a run whose files
  cover the whole project, keep it out of any loop over individual files, and
  judge the deploy by the container set the project holds afterwards, not by
  the exit code (the gate step is in
  [`deploy-fleet-on-remote-docker-host`](../../skill-corpus/deploy-fleet-on-remote-docker-host.md)).
  It is off by default; only
  `COMPOSE_REMOVE_ORPHANS=1` makes it implicit. `--no-deps` touches nothing
  outside the named service, and `down` never removes named volumes without
  `--volumes`.
- **An unnamed top-level volume resolves to `<project>_<key>`.** Changing the
  project name (an env var, `-p`, or the working-directory name) computes a
  different volume name, finds none, and silently starts on empty state. The
  old volume is orphaned, not deleted. Give a volume an explicit `name:` before
  any project rename that must keep its data.
- **`config` does not catch host-port conflicts** between merged services;
  they appear only at `up` as "port is already allocated". Check merged ports
  yourself.
- **`:?` does not fire on a placeholder**: `CHANGE_ME` renders with exit 0.
- **A recreated container gets a new IP**, and a proxy that resolved at load
  keeps the stale address (mechanism on [`nginx.md`](nginx.md)).
- **Several projects on one host have no fleet view**: `ps`, `down` and
  `--remove-orphans` each see one project, and duplicate names block
  consolidation.
- **A forwarder started outside the project** (a host-network TCP proxy in
  front of a database, say) survives `compose down` and keeps the exposure open
  until it is removed by hand.
- **Image lists from `image:` lines skip build-only services.**
  `config --images` does print a name for them (`<project>-<service>`), so use
  it rather than reading the file.

## Testing
- `docker compose config -q` (or a full `config` render) in CI for every
  overlay combination that is deployed; assert effective values on the
  rendered output, not on the source files.
- Render once with an empty environment and `--no-interpolate` to check
  structure, and once with the real environment to check values.
- Diff the merged `ports` across services to catch host-port conflicts before
  `up`.
- Run each healthcheck command by hand inside its container before relying on
  `service_healthy`.

## Security defaults
- Services join a project bridge network and are reachable from each other by
  name; nothing is published to the host until `ports:` says so, and then it
  binds on all interfaces unless an address is given.
- Containers run with the engine's security defaults, which
  [docker](docker.md) owns, and with no resource limits.
- Secrets are plain files on the host without Swarm.

## Operational behaviour
- `up` creates or recreates only what changed; `restart` reuses existing
  containers with their old configuration.
- Dependencies start in `depends_on` order and stop in reverse.
- `down` removes containers and networks of the project, never named volumes
  without `--volumes`.

## Interop
- Engine, images and build: [`docker.md`](docker.md); daemon and host
  hardening: [`docker-host-hardening.md`](docker-host-hardening.md).
- Database images and their `*_FILE` and init conventions:
  [`postgres.md`](postgres.md), [`mysql.md`](mysql.md), [`mongo.md`](mongo.md),
  [`redis.md`](redis.md).
- The edge proxy: [`nginx.md`](nginx.md).

## Major lines
### Compose v1 to v2 (and v5)
- v1 was the end-of-life Python `docker-compose`; v2 is written in Go and
  invoked as `docker compose`. v5 is functionally the same as v2 and adds a Go
  SDK (the number skips to avoid confusion with file formats 2 and 3). A
  standalone v2 binary is also named `docker-compose`, so a hyphenated command
  does not prove v1: run `docker-compose version` to see which one answers.
- v1 chose the file schema from `version:`; v2 ignores the key and follows the
  Compose Specification, whose `depends_on` conditions include
  `service_healthy`. Migration is the moment to add health gating.
- Container names changed from `<project>_<service>_<n>` to
  `<project>-<service>-<n>` (underscores are not valid DNS names), which breaks
  scripts that grep names; v2's `--compatibility` flag (or
  `COMPOSE_COMPATIBILITY`) restores underscores.
- `docker-compose scale` and `rm --all` are gone (use `up --scale`).
- v2 applies `deploy.resources` limits outside Swarm, so limits written long
  ago may start to bite. Observed in practice: v1 projects had ignored them;
  upstream does not state the v1 default.
- Remote targets: v1 had its own `-H ssh://`; with v2 use `DOCKER_HOST`,
  `docker -H` or `docker context`.


## Upstream docs
- https://docs.docker.com/compose/
- https://github.com/docker/compose
- Top-level `version` and `name`: https://docs.docker.com/reference/compose-file/version-and-name/
- Merge rules: https://docs.docker.com/reference/compose-file/merge/
- Environment precedence: https://docs.docker.com/compose/how-tos/environment-variables/envvars-precedence/
- Project name: https://docs.docker.com/compose/how-tos/project-name/
- Startup order: https://docs.docker.com/compose/how-tos/startup-order/
- Secrets: https://docs.docker.com/compose/how-tos/use-secrets/
- History (v1, v2, v5): https://docs.docker.com/compose/intro/history/
