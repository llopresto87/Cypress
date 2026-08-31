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

## Upstream docs
- https://docs.docker.com/
- https://docs.docker.com/build/buildkit/
