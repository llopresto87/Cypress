# docker — container

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a tool, not a record of one
> project's versions. For exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile / base-image tags.

## What it is
Docker packages applications and their dependencies into **images** and runs
them as isolated **containers**. The Docker Engine (daemon) builds images from a
`Dockerfile` and runs containers; modern builds use **BuildKit**, a
higher-performance, parallel, cache-aware build backend with features like build
secrets and cache mounts. It is the substrate most container-based deployment
and local-dev workflows sit on. Homes: docs.docker.com (source `docker/docs`),
the Engine `moby/moby`, the CLI `docker/cli` and BuildKit `moby/buildkit`.
Daemon hardening lives on
[`container/docker-host-hardening.md`](docker-host-hardening.md) and
multi-container wiring on [`container/docker-compose.md`](docker-compose.md).

## Install, setup and configuration
- **Client packages.** A container or host that only drives a daemon (a
  mounted socket, a remote context) installs `docker-ce-cli` (plus the Compose
  plugin) from Docker's signed apt repository. Observed in practice: the
  distro `docker.io` package lagged below the daemon's minimum API version and
  failed against it.
- **Default container sysctls.** Since the 20.10 line the daemon sets
  `net.ipv4.ip_unprivileged_port_start=0` (and `net.ipv4.ping_group_range`
  outside a user namespace) for containers with their own network namespace
  only: not with host networking, not when joining another container's
  namespace. That is what lets a non-root process bind ports below 1024 without
  any capability. It can be overridden with `--sysctl`; declare it explicitly
  where a service depends on it.
- **Image store.** On the Engine 29 line, fresh installs use the containerd
  image store; upgraded hosts keep the classic graph-driver store (overlay2)
  until they opt in, and `userns-remap` cannot use the containerd store. Several
  pitfalls below depend on which store a daemon runs.

## Core API / usage shape
- **`Dockerfile`**: declarative build recipe: a base image (`FROM`), copied
  files, `RUN` steps, and the runtime entrypoint/command.
- **Frontend pin**: `# syntax=docker/dockerfile:1` pins the Dockerfile
  frontend, not the Engine, and gives `RUN --mount` its current syntax;
  `--mount` needs BuildKit (the legacy builder cannot build it). BuildKit
  reaches `docker build` through the buildx plugin. Docker's documented
  install includes the `docker-buildx-plugin` package; static binaries and some distribution packaging do not (Debian
  and Ubuntu ship `docker-buildx` as its own package). Without it the CLI falls
  back to the classic builder with a deprecation warning (or fails when
  `DOCKER_BUILDKIT=1` is set), and the classic builder rejects `RUN --mount`. The
  preflight that checks `docker buildx version` is in
  [`deploy-fleet-on-remote-docker-host`](../../skill-corpus/deploy-fleet-on-remote-docker-host.md).
- **Multi-stage builds**: multiple `FROM` stages let a heavy build stage compile
  artifacts while the final stage copies only the results into a lean runtime
  image. A key benefit: the **build host needs only the Docker daemon**; the
  compiler/SDK lives inside the build stage, not on the host.
- **Mounts in `RUN`**:
  - `--mount=type=cache,target=<dir>[,id=…][,sharing=shared|private|locked]`
    keeps package caches out of layers and across builds. The cache `id`
    defaults to the target path, so every build on the host that uses the same
    target shares it. A named `-v` volume is invisible to a build.
  - `--mount=type=bind[,from=<stage|image>]` supplies build inputs that never
    persist, or consumes an artifact another stage published as a layer.
  - `--mount=type=secret,id=…[,required=false]` exposes a secret to a single
    step as a file; it is **not** persisted into any image layer, so
    credentials used at build time never leak into the shipped image.
- **`ADD --checksum=sha256:…`** verifies a remote download; use `ADD` only for
  remote artifacts and `COPY` for everything else.
- **`EXPOSE` publishes nothing**; reachability comes from `-p` or Compose
  `ports:`.
- **Build switches**: `--pull` always tries to pull every referenced base
  image; `--no-cache` ignores the build cache; `--no-cache-filter <stage>`
  rebuilds one stage; `--progress=plain` prints step output (pipe it through
  `tee`, since build logs are not stored).
- **Tags vs digests**: an image is addressed by a mutable tag (e.g.
  `name:label`) or by an immutable content-addressed `@sha256:...` digest. Tags
  can be moved to point at new content; a digest always names exactly one image.
  `docker buildx imagetools inspect <ref>` (or a registry
  `GET /v2/<name>/manifests/<tag>` that accepts both the OCI index and the
  Docker manifest-list media types) reads a tag's digest without pulling;
  `Docker-Content-Digest` is the sha256 of the returned body, and a
  per-platform digest differs from the index digest.

## Idioms & best practices
- Use multi-stage builds to keep runtime images small and free of build tooling.
- Pass build-time credentials via `--secret` mounts, never via `ARG`/`ENV` or a
  copied file, so they cannot be recovered from image history. An `ENV` value
  stays in its layer even if a later layer unsets it; set, use and unset a
  build-only value inside one `RUN`.
- Pin base images by digest (or a specific tag) for reproducible, tamper-evident
  builds, and let update tooling (a dependency bot's docker ecosystem, say)
  raise the re-pin changes. Locally built images that never went through a
  registry have no RepoDigests, so the digest rule applies to pulled bases;
  re-tag the running image (`:rollback`) before rebuilding it, since that tag is
  then the only rollback handle.
- Order layers stable-to-volatile: copy the manifest or lockfile, resolve
  dependencies, then copy the sources. An `ADD . /app` or a pre-built `dist/`
  ahead of the resolve step busts the cache on every commit.
- Run `apt-get update`, the install and `rm -rf /var/lib/apt/lists/*` in one
  `RUN`; a separate update layer is reused from cache with stale lists.
- Prefix piped `RUN` lines with `set -o pipefail &&` (on a dash `/bin/sh`, use
  exec form with `/bin/bash -c`).
- Use exec-form `CMD`/`ENTRYPOINT` and end entrypoint scripts with
  `exec "$@"`, so the application is PID 1 and receives SIGTERM.
- Run as a non-root user and copy only what the runtime needs. Create that user
  with an explicit UID and GID (a "next free" id drifts and breaks volume
  ownership), and drop privileges with `gosu` or `su-exec`, not `sudo`.
- Refresh bases deliberately: periodic security rebuilds need `--pull`;
  `--no-cache` alone rebuilds layers on the old base already on the host.
- Keep a producer and its consumer in one `RUN` when they share a cache mount,
  publish the artifact as a layer and read it with `bind,from=`, or let the
  consumer refill the cache itself: for .NET, drop `--no-restore` from `build`
  and `publish`, so a pruned package cache is restored instead of failing with
  a missing-package error.
- Treat hardening defaults as per-service decisions, each with a recorded
  reason, not a blanket setting. Dropping every capability kills a server whose
  root master process must switch its workers to another user, and a read-only
  root filesystem breaks any image that writes to its own filesystem (a cache, a
  pid file, a generated config). Apply them service by service, and record why
  a service goes without one, so the next person does not "tidy it in" and break
  boot.
- When several Dockerfile variants (one per environment, say) share one
  entrypoint or runtime script set, every variant must copy every file that
  entrypoint invokes. Pin that structurally: a test that, for each variant,
  resolves the scripts the entrypoint calls and asserts each one is copied into
  that variant's image. A gate that inspects only one variant cannot see the
  gap.
- To operate on root-owned host paths without `sudo`, go through a disposable
  container (`docker run --rm`) that runs as root inside, with the narrowest
  bind mount the operation needs, read-only when it only reads. Write outputs to
  a directory the calling user owns, run any ownership fix inside the same
  container, and preserve the original ownership when moving a tree: a tree
  that arrives owned by the login user is a silent change to what you were asked
  to move. Verify from inside a container too, so the check runs with the same
  privilege as the operation. This works because daemon access is
  root-equivalent (see [`docker-host-hardening.md`](./docker-host-hardening.md)),
  so it is audited access, used only when no `sudo` route exists. When the
  root-owned paths are debris a container left behind, the lasting fix is to
  run that container as the caller's uid (`--user uid:gid`).

## General pitfalls
- **Do not assume `curl` (or other conveniences) exists in a minimal base
  image.** A shell, a package manager, `curl` and `wget` are four separate
  facts, and each base lacks a different subset. Distroless has none of the
  four. A Debian `-slim` base has a shell and `apt` but neither `curl` nor
  `wget`. Alpine has a BusyBox shell, `apk` and BusyBox `wget`, but no `curl`.
  An image that adds a runtime on top (a JRE, an interpreter) inherits its OS
  base and may install more, so check the image's own Dockerfile, not its
  kind. A healthcheck or entry script that calls a missing tool fails
  cryptically. With no shell, a `CMD-SHELL` healthcheck fails and only the exec
  form works; on distroless that leaves exec form against a binary in the image.
  With no `curl`, use the `wget` that is present, install the tool explicitly,
  or use a language-native check.
- A mutable tag can silently change what runs between builds; digests pin it.
- Secrets placed in `ARG`/`ENV` or copied into a layer persist in image history
  even if later "deleted" in a subsequent layer.
- Large or poorly ordered layers bust the cache and bloat images.
- **With the containerd image store, `docker system df` measures the wrong
  tree**: the graph-driver directory, not the containerd snapshot/blob store,
  so its usage and prune figures mislead. Size a disk budget from `df` instead,
  and reckon an image at roughly 1.4x its registry size, because the compressed
  blob is kept alongside the unpacked snapshot.
- **A bind-mount whose source path does not exist is created by the daemon as an
  empty directory.** A container that expected a *file* there then fails at
  container creation (a `not a directory` error, exit 127, RestartCount 0), so a
  `restart:` policy never fires and the service stays down with no crash loop to
  notice. Observed in practice, the created directory is owned by root, so on a
  later run it also defeats a reuse check that tests only whether the path
  exists: a directory named like the expected file passes `exists()`. Test each
  expected file for kind (a regular file) and owner. Upstream, Compose's long
  volume syntax with `bind: {create_host_path: false}` stops the creation (it
  defaults to true, and the short syntax always creates), and
  `--mount type=bind` refuses a missing source by default where `-v` creates it. Bake a
  small config file into the image rather than mounting one a cleanup or reboot
  can delete. A workspace cleanup on a host that runs the deployed stack is the
  usual deleter: before removing a directory, read the mounts of every
  container (`docker inspect`), skip any path a container still mounts, and
  delete nothing when that inspection fails.
- **A create-time failure is silent.** No restart churn, no climbing
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
- **A script present in one image variant and missing from another fails only in
  the variant nobody rebuilt.** The shared entrypoint exits 127 (`not found`) at
  start, often as a restart loop, in the environment whose Dockerfile was not
  edited. The structural test in Idioms is the guard.
- **What `docker image inspect --format '{{.Id}}'` returns depends on the
  daemon's image store.** On the classic graph-driver store it is the image's
  config digest; on the containerd store it is the digest the tag points at,
  which for a multi-platform image is the index digest. Both are valid
  content-addressed pins, but an image id declared for comparison depends on the
  store type: the same image reads as a mismatch on a daemon using the other
  store. Record which store the declared value was measured on.
- **A no-cache rebuild peaks well above its final footprint.** With the build
  cache disabled, near-identical images share no layers, and parallel builds
  stack their intermediate state on the same disk, so a build host can fill up
  even when the finished images would fit. Right after a wipe there is no stale
  layer to avoid, so rebuild with the cache on; reach for no-cache only when a
  stale layer is suspected (`--no-cache` rebuilds layers but does not refresh a
  base image already on the host, so pair a deliberate refresh with `--pull`,
  or base-image security fixes are never picked up), lower build parallelism for large
  topologies, and check free space before queueing a large rebuild. A full disk
  on the build host tends to surface as a failure of whatever was being built.
- **A cache mount is not an artifact store.** When a producer and its consumer
  are separate `RUN` steps, the producer can be served from cache while the
  mount has been pruned, and the consumer fails with an unrelated-looking
  error (the fixes are in Idioms). Keying the cache `id` to a lock-file hash
  does not help: a prune with no lock-file change keeps the same id and the same
  layer hit.
- **`--no-cache` and cache mounts.** Observed in practice: a `--no-cache`
  build also started each cache mount empty, and since cache ids are shared
  across the host, an experiment that used `--no-cache` on both legs proved
  nothing about persistence. Upstream describes `--no-cache` only as not using
  the build cache.
- **`read_only: true`, second trap**: a tmpfs laid over a config directory
  masks the config baked into the image. Move the entrypoint's writes
  elsewhere first.
- **macOS AppleDouble sidecars.** `tar` on macOS writes `._<name>` files for
  anything with extended attributes unless `COPYFILE_DISABLE=1` is set. On
  Linux they are ordinary files, so `COPY` takes them into the image, and a
  build step that scans sources (an annotation processor, a code generator, a
  glob compiler) can choke on them yet exit 0 with a broken artifact. Set
  `COPYFILE_DISABLE=1` on the archive and add `**/._*` and `.DS_Store` to
  `.dockerignore`. A direct `docker build` from macOS does not create them;
  only a tar, SMB or FAT hop does (observed in practice).
- **A client older than the daemon's API floor fails**, with "client version X
  is too old". Observed in practice: a caller that read any non-zero
  `docker info` as "Docker not running" then skipped its work silently (a
  secret scan reported a false clean), and a library that pinned an old API
  version instead of negotiating reported "Could not find a valid Docker
  environment", so the tests that assumed Docker skipped themselves. Fix the
  client, not the daemon.

## Testing
- Build every Dockerfile variant in CI, not only the one being edited, and run
  the per-variant script-copy test from Idioms.
- Prove a step re-ran with `--no-cache-filter <stage> --progress=plain | tee`.
- After a create-time failure is suspected, check `docker ps -a` for exited
  containers by name and `RestartCount 0` (see pitfalls).
- Smoke a health check by running its command inside the built image, which
  also proves the tool it calls exists.

## Security defaults
- Build secrets through `--mount=type=secret` never enter a layer; `ARG` and
  `ENV` always do.
- Containers start as root unless the image sets `USER`; the default
  capability set excludes most privileged operations, and the
  unprivileged-port sysctl is on in a private network namespace.
- Daemon access is root-equivalent; the daemon-side controls (socket,
  userns-remap, seccomp, AppArmor, logging) are on
  [`container/docker-host-hardening.md`](docker-host-hardening.md).

## Operational behaviour
- A container's PID 1 receives the stop signal (SIGTERM, then SIGKILL after
  the grace period); a shell-form entrypoint swallows it.
- Build cache and images accumulate until pruned; disk planning is in the
  pitfalls above.
- Restart policies apply only to containers that were created successfully.

## Interop
- Compose: [`container/docker-compose.md`](docker-compose.md).
- Base images: [`container/eclipse-temurin.md`](eclipse-temurin.md) for JVM
  runtimes, [`container/nginx.md`](nginx.md) for static frontends.
- Image scanning: [`cli/trivy.md`](../cli/trivy.md).

## Major lines
### Engine 20.10 line
- Default sysctls for ping sockets and unprivileged low ports arrived.

### Engine 29 line
- The minimum client API version was raised at the start of the line, and a
  later release in the same line lowered it again: read the floor from the
  daemon's error or `docker version`, never assume it.
- The containerd image store is the default on fresh installs (not with
  `userns-remap`; upgraded hosts keep their store).
- Docker Content Trust was removed from the CLI.
- cgroup v1 is deprecated; move hosts to cgroup v2.
- Rootless networking: `pasta` became a fallback when `slirp4netns` is absent,
  and a later release in the line made `gvisor-tap-vsock` the default.

## Upstream docs
- https://docs.docker.com/
- https://docs.docker.com/build/buildkit/
- https://docs.docker.com/reference/dockerfile/ (RUN --mount)
- https://docs.docker.com/build/cache/optimize/
- https://docs.docker.com/build/building/best-practices/
- https://docs.docker.com/reference/cli/docker/buildx/build/
- https://docs.docker.com/engine/release-notes/29/
- https://docs.docker.com/engine/storage/containerd/
- https://docs.docker.com/engine/storage/bind-mounts/
- https://docs.docker.com/engine/deprecated/ (legacy builder fallback)
