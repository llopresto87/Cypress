# docker-compose — container

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a tool, NOT a version-pinned page. For
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile / compose-file version.

## What it is
Docker Compose defines and runs multi-container applications from a declarative
YAML file. It brings up a set of services together, wiring them onto a shared
network with named volumes for persistence. The modern form is the **v2 Compose
plugin**, invoked as `docker compose` (a subcommand of the Docker CLI) rather
than the older standalone `docker-compose` binary.

## Core API / usage shape
- **Services**: each service names an image (or build context), environment,
  ports, volumes, and dependencies; `docker compose up` starts the whole stack.
- **Networking**: services on one Compose project share a default bridge network
  and reach each other by **service name** as a hostname, with no hard-coded IPs.
- **Named volumes**: declared volumes persist data across container restarts and
  recreations, independent of the container filesystem.
- **Interpolation**: `${VAR}` in the file is substituted from the shell
  environment and the project `.env` file. Four forms control what happens when
  the value is missing:

  | form | result |
  |---|---|
  | `${VAR:-default}` | `VAR` if set **and non-empty**, else `default` |
  | `${VAR-default}` | `VAR` if set (even empty), else `default` |
  | `${VAR:?error}` | `VAR` if set **and non-empty**, else exit with `error` |
  | `${VAR?error}` | `VAR` if set (even empty), else exit with `error` |

- **`docker compose config`** prints the fully resolved model (includes
  followed, `-f` files merged, variables interpolated) without needing a
  running daemon. It is the native oracle for "what will this stack
  run with"; the
  [`layered-config-merge-verifier`](../../tool-corpus/ops/layered-config-merge-verifier.md)
  tool builds on it.
- **Remote daemon**: setting `DOCKER_HOST=ssh://<host>` targets a remote Docker
  daemon over SSH, so `docker compose` can build/run a stack on another machine
  while driven locally.

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
  with no HTTP surface disables the check explicitly instead of false-failing.

## General pitfalls
- **Relative bind-mount paths resolve on the REMOTE host's filesystem** when
  using a remote daemon (`DOCKER_HOST=ssh://`). A `./path` bind mount is
  interpreted where the daemon runs, not where you typed the command, so a
  local-looking path silently mounts a non-existent or wrong directory on the
  remote host. Prefer named volumes (or absolute, remote-correct paths) for
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
- The v2 plugin (`docker compose`) and the legacy binary (`docker-compose`)
  differ in invocation and some behavior; confirm which is in use.
- **`--remove-orphans` is scoped to the whole project, not to the `-f` files you
  passed.** Plain `down` only touches services declared in the files handed to
  the command, but `--remove-orphans` widens removal to every container of the
  resolved project (matched by `COMPOSE_PROJECT_NAME`), regardless of which `-f`
  subset you passed. So if several invocations manage different `-f` subsets
  under one project name, `--remove-orphans` on one deletes containers another
  declared, and exits 0 while doing it. It is off by default; only
  `COMPOSE_REMOVE_ORPHANS=1` makes it implicit. `--no-deps` touches nothing
  outside the named service, and `down` never removes named volumes without
  `--volumes`.
- **An unnamed top-level volume resolves to `<project>_<key>`.** Changing the
  project name (an env var, `-p`, or the working-directory name) computes a
  different volume name, finds none, and silently starts on empty state. The
  old volume is orphaned, not deleted. Give a volume an explicit `name:` before
  any project rename that must keep its data.

## Upstream docs
- https://docs.docker.com/compose/
- https://github.com/docker/compose
- Top-level `version` and `name`: https://docs.docker.com/reference/compose-file/version-and-name/
