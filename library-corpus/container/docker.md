# docker — container

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a tool, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile / base-image tags.

## What it is
Docker packages applications and their dependencies into **images** and runs
them as isolated **containers**. The Docker Engine (daemon) builds images from a
`Dockerfile` and runs containers; modern builds use **BuildKit**, a
higher-performance, parallel, cache-aware build backend with features like build
secrets and cache mounts. It is the substrate most container-based deployment
and local-dev workflows sit on.

## Core API / usage shape
- **`Dockerfile`**: declarative build recipe — a base image (`FROM`), copied
  files, `RUN` steps, and the runtime entrypoint/command.
- **Multi-stage builds**: multiple `FROM` stages let a heavy build stage compile
  artifacts while the final stage copies only the results into a lean runtime
  image. A key benefit: the **build host needs only the Docker daemon** — the
  compiler/SDK lives inside the build stage, not on the host.
- **BuildKit `--secret` mounts**: `RUN --mount=type=secret,...` exposes a secret
  to a single build step as a mounted file; it is **not** persisted into any
  image layer, so credentials used at build time never leak into the shipped
  image.
- **Tags vs digests**: an image is addressed by a mutable tag (e.g.
  `name:label`) or by an immutable content-addressed `@sha256:...` digest. Tags
  can be moved to point at new content; a digest always names exactly one image.

## Idioms & best practices
- Use multi-stage builds to keep runtime images small and free of build tooling.
- Pass build-time credentials via `--secret` mounts, never via `ARG`/`ENV` or a
  copied file, so they cannot be recovered from image history.
- Pin base images by digest (or a specific tag) for reproducible, tamper-evident
  builds; order `Dockerfile` layers stable-to-volatile to maximize cache reuse.
- Run as a non-root user and copy only what the runtime needs.

## General pitfalls
- **Do not assume `curl` (or other conveniences) exists in a minimal base
  image.** Slim, distroless, alpine, and JRE-only bases often ship without
  `curl`, `wget`, a shell, or a package manager — a healthcheck or entry script
  that calls `curl` fails cryptically. Install the tool explicitly, use a tool
  that is present, or use a language-native check.
- A mutable tag can silently change what runs between builds; digests pin it.
- Secrets placed in `ARG`/`ENV` or copied into a layer persist in image history
  even if later "deleted" in a subsequent layer.
- Large or poorly ordered layers bust the cache and bloat images.
- **With the containerd image store, `docker system df` measures the wrong
  tree** — the graph-driver directory, not the containerd snapshot/blob store —
  so its usage and prune figures mislead. Size a disk budget from `df` instead,
  and reckon an image at roughly 1.4x its registry size, because the compressed
  blob is kept alongside the unpacked snapshot.
- **A bind-mount whose source path does not exist is created by the daemon as an
  empty directory.** A container that expected a *file* there then fails at
  container creation (a `not a directory` error, exit 127, RestartCount 0), so a
  `restart:` policy never fires and the service stays down with no crash loop to
  notice. Bake a small config file into the image rather than mounting one a
  cleanup or reboot can delete.
- **A create-time failure is silent** — no restart churn, no climbing
  RestartCount, no repeating log line, the service is simply absent. A quiet
  `docker ps` is therefore not evidence the stack is up; check for exited
  containers by name and for `RestartCount 0`, the tell that separates a
  creation failure from an application crash loop.
- **`cap_add: NET_BIND_SERVICE` does not let a non-root user bind a privileged
  (<1024) port.** The container gets the bounding/permitted/effective capability
  sets but not the *ambient* set, and a non-root `execve` without file
  capabilities drops permitted/effective to nothing. The mechanism that works is
  the sysctl `net.ipv4.ip_unprivileged_port_start=0`; `setcap` file capabilities
  are not an alternative under `no-new-privileges: true`, which is mutually
  exclusive with them.
- **A container's IP is assigned dynamically and is not stable across restart or
  recreate**, and a freed address can be reassigned to a different container on
  the same network. Reference peers by name; a component that resolves a peer's
  address and then *trusts* it (a proxy IP fed to a forwarded-headers allow-list)
  can silently trust the wrong container after a restart. Trust a declared
  subnet, which is fixed at network creation, not a resolved address.

## Upstream docs
- https://docs.docker.com/
- https://docs.docker.com/build/buildkit/
