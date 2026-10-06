# Suggested skill: deploy-fleet-on-remote-docker-host

> Optional procedure — the single universal method for taking a fresh set of
> repos online on a remote Docker host over SSH, from nothing. Composes existing
> corpus pages and tools. Parameterized by `<host>`, `<ssh-user>` (default
> `root`, which logs in by public key only: `harden-docker-host` step 1),
> `<ssh-key>`, `<remote-dir>`; nothing about a specific host, key, or project
> lives here.

## When to apply

- A fresh set of repos must come online on a remote Docker host over SSH, from
  nothing — no host prep, no images, no compose in place.
- An already-deployed fleet must be redeployed, moved between modes, or rolled
  back to a previously-good tag.
- The local machine has no Docker daemon, or a local toolchain that would drift
  from the host's — so the build has to happen on the target.
- The original infrastructure is gone (a common brownfield case). The method is
  self-contained: build from source (no registry needed), point any config
  service at a local filesystem backend, and let dead external dependencies
  fail at runtime while services still boot.

## The one invariant: every image builds on the remote host

**Every image is built on the target host.** The local machine only
orchestrates — ship source, drive SSH, read results — and is assumed to have
**no Docker daemon**. This is why every service ships a **multi-stage
build-from-source Dockerfile** (`library-corpus/container/docker.md`): the
toolchain lives *inside* the build stage, so the host needs only Docker, and
there is no local-vs-remote toolchain drift to debug. `docker build`,
`compose build` and any registry push run on the host.

## Step 0 — the `deploy/` folder (single source of truth)

One `deploy/` folder at the umbrella (multi-repo) root owns the whole bring-up.
Per-repo compose files are retired in its favor. Canonical tree:

```
deploy/
  deploy.sh                     # the single idempotent entrypoint (this skill)
  lib/*.sh                      # sourced-only helpers
  docker-compose.yml            # BASE umbrella stack — the whole fleet, one unit
  docker-compose.dev.yml        # overlay: local fakes/fixtures, seed data
  docker-compose.qa.yml         # overlay: real deps, debug on, smoke-targeted
  docker-compose.prod.yml       # overlay: pinned, hardened, no debug surface
  docker/                       # Dockerfiles + rendered config (nginx, etc.)
  vendor/                       # vendored dead-registry deps, built first
  tests/e2e-smoke.sh            # black-box smoke against the live bring-up
  known_hosts                   # the host's pinned public key — committed
  .env.example                  # committed placeholders only
  .env                          # real secrets — GITIGNORED
  certs/                        # TLS material — GITIGNORED, generated on host
```

Resolve every path from `${BASH_SOURCE[0]}`, because agent and CI shells reset
the cwd.

## Step 1 — Dockerfiles (see `library-corpus/container/docker.md`)

One multi-stage Dockerfile per service under `deploy/docker/` (or the repo),
built to the corpus page: **multi-stage** (build stage carries the SDK, runtime
stage is lean); **pin the base** by tag/digest; **run non-root**; **no secret in
any layer** — build-time creds only via BuildKit `--mount=type=secret`, never
`ARG`/`ENV`/a copied file; a `HEALTHCHECK` (or a compose one) using a tool that
actually exists in the base image; a `.dockerignore` excluding `.git`, build
output, `node_modules`. A dependency whose registry is gone is built from
source and vendored first (`skill-corpus/vendor-dependency-from-dead-registry.md`).

When installing that vendored dependency and packaging the service share a
BuildKit cache mount (`RUN --mount=type=cache,...`), do both in **one** `RUN`.
The contents of a cache mount are not part of the image layer. With the install
in a `RUN` of its own, BuildKit can report that layer `CACHED` and skip running
it while the mount has since been pruned. The packaging step then cannot
resolve the dependency and falls back to the dead registry. One `RUN` means
packaging always runs in the same step that just filled the mount. Leave a
comment in the Dockerfile, so that nobody splits the step later to "tidy" it.

## Step 2 — compose: one base + dev/qa/prod overlays (see `library-corpus/container/docker-compose.md`)

The base `docker-compose.yml` is the fleet. Each **mode is an overlay merged on
top** of the unchanged base (`-f docker-compose.yml -f
docker-compose.<mode>.yml -p <project>`). What the modes mean:

- **dev** — local fakes/stubs for external deps, seeded fixtures, debug ports,
  throwaway credentials, loud "not production" banner.
- **qa** — real dependencies, verbose logging/debug still on, the smoke suite
  targeted here; the rehearsal of prod.
- **prod** — images pinned, debug/introspection surfaces off, host hardening
  assumed (Step 3), only the edge published.

The base follows the corpus page's conventions: services reach each other by
**service DNS**, never IP; **named volumes** for all stateful data; **`.env`
interpolation** with fail-closed required secrets (`${X:?}`) and safe
non-secret defaults (`${X:-default}`); DRY the fleet with **YAML anchors**;
every long-lived service has a **`healthcheck`** and dependents wait on
`depends_on: {x: {condition: service_healthy}}`; **publish only the edge** —
bind sensitive services (DBs, brokers, admin) to **loopback**
(`127.0.0.1:<port>:<port>`), everything else stays in-network; `restart:
unless-stopped`; opt-in planes (monitoring) behind compose `profiles`.

## Step 3 — host prep & hardening

Before the first bring-up, `reliability` runs the **`harden-docker-host`** skill,
which owns the ordered floor and its per-control gate (and defers in turn to
`library-corpus/container/docker-host-hardening.md` for what each control is and
why). Two of its properties are load-bearing *for this method*: its firewall step
is operator-gated, so the bring-up treats inbound filtering as absent — **the
loopback binding of Step 2 is the containment that is always on**, whatever the
operator decides; and the whole procedure is a no-op-safe re-run, so every
redeploy re-asserts the floor instead of trusting that it was done once.

## Step 4 — secrets

Secrets live only in the gitignored `.env`; rotate them with
`tool-corpus/ops/env-secret-rotation.md`, which owns how a secret is generated,
written and kept out of argv and logs.

## Step 5 — the deploy pipeline (`deploy.sh`, idempotent, one command)

1. **Preflight** — `set -euo pipefail`; resolve `SCRIPT_DIR`; build the
   connection once: `SSH="ssh -i <ssh-key> -o StrictHostKeyChecking=accept-new
   -o UserKnownHostsFile=$SCRIPT_DIR/known_hosts <ssh-user>@<host>"`. The
   connection carries `.env` and `certs/`, so it trusts only the pinned host
   key: on first contact, compare the recorded fingerprint with one obtained
   out of band (the provider console, the host's own `ssh-keygen -lf`) and
   commit `known_hosts`; a rebuilt host fails the check until it is re-pinned
   the same way. (A bare-IP host with no `~/.ssh/config` entry needs `-i`; a
   host that DOES have a config entry is addressed by alias without `-i`.)
   **Know what you may do on the host before the first command.** On a host
   you do not own outright, that is only the acts the owner named for it (a
   scoped standing grant, `core/method/vcs-posture.md`); keep every later step
   inside them.
   **Prove the host is yours before the first `up`.** An address is not an
   identity: one machine can change address, and a reused address can be
   another machine. The identity is the pinned host key above. Then list the
   compose projects already on the host (`docker ps -a --format '{{.Label
   "com.docker.compose.project"}}' | sort -u`, or `docker compose ls -a`). A
   project name that is not `<project>` means another tenant's stack: stop
   and confirm the target with the operator. If a deploy did land on the wrong
   host, reverse it by your own label only (`docker compose -p <project>
   down`, then remove the volumes and images that carry the label, listed by
   `docker volume ls -q --filter label=com.docker.compose.project=<project>`
   and the same filter on `docker image ls -q`), and leave every other
   project's resources untouched. Images that compose pulled, not built,
   do not carry the label: list them from the compose file
   (`docker compose -p <project> config --images`) and remove only those that
   no other project uses. Last, check that the build plugin is present
   (`docker buildx version`) before any Dockerfile uses a BuildKit-only
   feature such as `RUN --mount`. Upstream makes Buildx and BuildKit the
   default for `docker build`. Observed in practice: a distribution's
   packaged engine shipped Buildx as a separate package, so a clean host
   lacked it and a Dockerfile with cache mounts failed. The preflight names
   the package to install and stops; it does not fall back to the legacy
   builder.
2. **Ensure `.env`** — if absent, `cp .env.example .env`, warn the operator to
   fill it, stop. Then load it fail-closed.
3. **Ensure TLS** (idempotent) — generate a self-signed cert on the host only if
   absent (`tool-corpus/ops/self-signed-tls-cert.md` — SAN not just CN), else
   reuse the one there.
4. **Prepare the host** — ensure Docker Engine + Compose v2 and the hardening
   floor are in place (Step 3); idempotent.
5. **Ship the source** — `ssh mkdir -p <remote-dir>`; `rsync -az --delete` a
   curated include list (excludes `.git`, build output, `node_modules`), with a
   `tar -czf - … | ssh 'tar -xzf -'` fallback when rsync is absent. Ship `.env`
   and `certs/` explicitly (they are sync-excluded). The host receives the
   source this step ships, so what builds is exactly what was reviewed.
   Two transfer traps come from a macOS workstation:
   - **AppleDouble sidecars.** macOS `tar` archives extended attributes as
     `._<name>` files next to each source file unless told not to: pass
     `--no-mac-metadata` (the bsdtar option) or set `COPYFILE_DISABLE=1`
     (observed in practice to suppress them; it is not in the tar manual).
     Then purge any that arrived anyway, on the host before the build:
     `find <remote-dir> -name '._*' -type f -delete`. Observed in practice: a
     code generator read the sidecars as source, logged errors, reported
     success and generated nothing, and the service crash-looped at runtime
     on a missing class. When a build runs a generator, assert that its
     output exists; a green build log is not that evidence.
   - **Two rsync implementations.** Recent macOS ships `openrsync` as
     `rsync`. Observed in practice: it and GNU rsync on the host disagreed on
     a transfer with several `--exclude` flags. When the exclude list
     misbehaves, ship committed history as a `git bundle` (`git bundle create
     <file> --all`, then clone it on the host) and overlay only the
     uncommitted working-tree files, passed as rsync's `--files-from` list. A
     deploy that tags images by commit needs that history anyway. Build that
     list without deletions: `git ls-files -m -o --exclude-standard` also
     lists a tracked file deleted in the working tree (`-m` counts an
     unstaged deletion as a modification), and rsync then reports the
     missing file and exits 23. Filter the `git ls-files -d` paths out of the
     list (`grep -vxFf <(git ls-files -d)`), and delete those same paths on
     the host as a separate step.
6. **Build, tag and start on the host** — build each service's image and tag it
   with an immutable ref (a content digest / git-SHA tag), then `$SSH 'cd
   <remote-dir>/deploy && DOCKER_BUILDKIT=1 docker compose -f
   docker-compose.yml -f docker-compose.<mode>.yml -p <project> up -d
   --remove-orphans'` against those tags. A host rebuild happens only when the
   source changed — the built-and-tested image is the one that runs.
   - **Build one service at a time, then start without building.** Run
     `docker compose build <svc>` for each changed service in turn, then `up
     -d --no-build`. Do not run one `up -d --build` over the whole fleet.
     Observed in practice: many parallel BuildKit builds on a modest host
     crashed the daemon, and after it restarted several containers with
     `restart: unless-stopped` stayed down, so the whole stack was down. The
     restart-policy docs say such a container comes back when the daemon
     restarts unless it was stopped before, "manually or otherwise". A crash
     during recreation can leave it in that stopped state, so do not count
     on the policy. Recovery: `docker start` the existing containers first,
     then check `docker compose ps -a`, then resume the serialized build.
   - **Restart an edge that resolved its upstreams at boot.** A reverse proxy
     whose `proxy_pass` names a static upstream host resolves it once at
     start (`library-corpus/container/nginx.md`). `up` recreates a changed
     upstream with a new address, but it leaves the unchanged edge running,
     and the edge keeps proxying to the old address and returns 502. End
     every deploy that recreated an upstream with `docker compose restart
     <edge>`, or with a graceful `nginx -s reload` inside the edge, which
     re-resolves the names too and is the lighter choice on an edge that other
     projects share. The lasting fix is per-request resolution (a `resolver` and a
     variable upstream), which has its own URI-forwarding trap on that page.
   - **Fix a bind-mounted secret's owner at deploy time.** When a container's
     root entrypoint cannot read a bind-mounted key because a different UID
     owns the file, set the owner and mode on the host before `up` (for
     example `chown root:root` and `chmod 600` on the key). Do not add a
     DAC-bypass capability (`DAC_READ_SEARCH`, `DAC_OVERRIDE`) to work around
     it: that grants the bypass over every file in the container to fix one
     file the deploy already controls. Use a capability only when the deploy
     cannot control the file's ownership, and record why. That fix is for a
     file the deploy itself writes.
   - **A bind source that keeps coming back root-owned has a writer to
     remove.** The daemon creates a missing bind source, and observed in
     practice it comes back root-owned (`library-corpus/container/docker.md`,
     General pitfalls). A chown on every run hides whichever writer does it
     next. Detect it in the preflight and fail closed. Remove the writer:
     create the directory as the deploy user before `up`, or run the
     container that writes it as that user. Leave clearing what is already
     there to one operator action, and do not build that repair on an image
     that a disk-recovery step may have pruned.
7. **Gate** — first assert the estate: compare the services running under
   `-p <project>` (`docker compose … ps --services --status running`) with the
   services the files of this run declare (`docker compose … config
   --services`), and fail the deploy on any missing or extra one (a one-shot
   service that exits by design is checked by its exit code in `ps -a`, not by
   `--status running`). A zero exit
   from `up` proves the command ran, not that the fleet is the one meant: when
   runs that pass different `-f` subsets share one project name,
   `--remove-orphans` removes what the other subsets declare and still exits 0
   (`library-corpus/container/docker-compose.md`). When one such run is found,
   check what earlier runs of the same shape left behind before calling them
   harmless.
   Then run `tests/e2e-smoke.sh` (`tool-corpus/testing/http-smoke-suite.md`)
   against the live host; nonzero exit fails the deploy.
8. **Report** — `$SSH 'docker compose … ps'` + print the verification curls.

Redeploy of one unchanged service repoints its pinned tag and `up -d --no-deps
<svc>` with **no rebuild** — the released bits are the tested bits. Rollback
repoints that service to its previous retained tag the same way (the
`release`/`rollback` runbook templates own the retag-don't-rebuild doctrine).
Disk hygiene on the host: prune build cache and dangling images and leave
volumes in place, because `--volumes` deletes the data.

## The invocation

`/deploy-fleet <host> key <ssh-key> [mode=prod]` binds `<host>`/`<ssh-key>`
(and optional `<ssh-user>`/`<remote-dir>`/`mode`) and runs the Step 5 pipeline
end to end: preflight → host prep → ship source → build+up on host in the
chosen mode → smoke → report. Default mode is `prod`. A project instantiating
this skill names the command to match its own host substrate.

## Reference files

- `skill-corpus/harden-docker-host.md` (Step 3, run by `reliability`)
- `library-corpus/container/docker.md`, `docker-compose.md`, `docker-host-hardening.md`
- `tool-corpus/ops/{container-deploy-pipeline,self-signed-tls-cert,env-secret-rotation}.md`,
  `tool-corpus/testing/http-smoke-suite.md`
- `templates/docs/runbooks/{release,rollback}.md`
- `skill-corpus/vendor-dependency-from-dead-registry.md` (Step 1, a
  dependency whose registry is gone)
