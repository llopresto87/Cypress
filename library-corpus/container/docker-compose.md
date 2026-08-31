# docker-compose — container

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a tool, NOT a version-pinned page — for
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
  and reach each other by **service name** as a hostname — no hard-coded IPs.
- **Named volumes**: declared volumes persist data across container restarts and
  recreations, independent of the container filesystem.
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
  layer overrides with multiple compose files rather than editing the base — one
  base file plus a per-environment overlay merged with repeated `-f` (dev / qa /
  prod), never a hand-edited base.
- Give every long-lived service a `healthcheck`, and make dependents wait on
  readiness with `depends_on: {<svc>: {condition: service_healthy}}` — startup
  order should follow actual readiness, not just container creation. A service
  with no HTTP surface disables the check explicitly rather than false-failing.

## General pitfalls
- **Relative bind-mount paths resolve on the REMOTE host's filesystem** when
  using a remote daemon (`DOCKER_HOST=ssh://`). A `./path` bind mount is
  interpreted where the daemon runs, not where you typed the command — so a
  local-looking path silently mounts a non-existent or wrong directory on the
  remote host. Prefer named volumes (or absolute, remote-correct paths) for
  remote daemons.
- **`$VAR` in a `command:` / healthcheck string is expanded by Compose (the host
  side) at parse time**, not by the container's shell, unless you escape it
  (`$$VAR`) or defer it by invoking a shell inside the container. An unescaped
  variable either resolves to a host value or empties out.
- **A named-volume mount path must match the directory the process actually
  writes to**, or data silently never persists — the process writes to the
  container layer while the volume sits mounted elsewhere, and everything looks
  fine until the container is recreated and data is gone.
- The v2 plugin (`docker compose`) and the legacy binary (`docker-compose`)
  differ in invocation and some behavior; confirm which is in use.

## Upstream docs
- https://docs.docker.com/compose/
- https://github.com/docker/compose
