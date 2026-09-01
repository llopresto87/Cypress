# Suggested skill: deploy-fleet-on-remote-docker-host

> Optional procedure — the single universal method for taking a fresh set of
> repos online on a remote Docker host over SSH, from nothing. Not a core
> skill; instantiate into `docs/graph/skills/<name>.md` (its home, projected
> into the harness dirs the plant uses) from `templates/skill.template.md`
> if selected. Composes existing corpus pages and tools — it does not restate
> them. Parameterized by `<host>`, `<ssh-user>` (default `root`), `<ssh-key>`,
> `<remote-dir>`; nothing about a specific host, key, or project lives here.

## When to apply

- A fresh set of repos must come online on a remote Docker host over SSH, from
  nothing — no host prep, no images, no compose in place.
- An already-deployed fleet must be redeployed, moved between modes, or rolled
  back to a previously-good tag.
- The local machine has no Docker daemon, or a local toolchain that would drift
  from the host's — so the build has to happen on the target.

## The one invariant: build on the remote host, never locally

**Every image is built on the target host.** The local machine only
orchestrates — ship source, drive SSH, read results — and is assumed to have
**no Docker daemon**. This is why every service ships a **multi-stage
build-from-source Dockerfile** (`library-corpus/container/docker.md`): the
toolchain lives *inside* the build stage, so the host needs only Docker, and
there is no local-vs-remote toolchain drift to debug. No `docker build`, no
`compose build`, no registry push runs on the local machine. Ever.

## Step 0 — the `deploy/` folder (single source of truth)

One `deploy/` folder at the umbrella (multi-repo) root owns the whole bring-up.
Per-repo compose files are retired in its favor. Canonical tree:

```
deploy/
  deploy.sh                     # the single idempotent entrypoint (this skill)
  lib/*.sh                      # sourced-only helpers (never executed directly)
  docker-compose.yml            # BASE umbrella stack — the whole fleet, one unit
  docker-compose.dev.yml        # overlay: local fakes/fixtures, seed data
  docker-compose.qa.yml         # overlay: real deps, debug on, smoke-targeted
  docker-compose.prod.yml       # overlay: pinned, hardened, no debug surface
  docker/                       # Dockerfiles + rendered config (nginx, etc.)
  vendor/                       # vendored dead-registry deps, built first
  tests/e2e-smoke.sh            # black-box smoke against the live bring-up
  .env.example                  # committed placeholders only
  .env                          # real secrets — GITIGNORED
  certs/                        # TLS material — GITIGNORED, generated on host
```

Resolve every path from `${BASH_SOURCE[0]}`, never the caller's cwd (agent/CI
shells reset cwd). `lib/*.sh` are sourced, never run.

## Step 1 — Dockerfiles (see `library-corpus/container/docker.md`)

One multi-stage Dockerfile per service under `deploy/docker/` (or the repo).
Non-negotiables, all from the corpus page: **multi-stage** (build stage carries
the SDK, runtime stage is lean); **pin the base** by tag/digest; **run
non-root**; **no secret in any layer** — build-time creds only via BuildKit
`--mount=type=secret`, never `ARG`/`ENV`/a copied file; a `HEALTHCHECK` (or a
compose one) using a tool that actually exists in the base image; a
`.dockerignore` excluding `.git`, build output, `node_modules`. Vendored
dead-registry dependencies are built first into the local build cache.

## Step 2 — compose: one base + dev/qa/prod overlays (see `library-corpus/container/docker-compose.md`)

The base `docker-compose.yml` is the fleet. Each **mode is an overlay merged on
top** (`-f docker-compose.yml -f docker-compose.<mode>.yml -p <project>`), never
an edited base. What the modes mean:

- **dev** — local fakes/stubs for external deps, seeded fixtures, debug ports,
  throwaway credentials, loud "not production" banner.
- **qa** — real dependencies, verbose logging/debug still on, the smoke suite
  targeted here; the rehearsal of prod.
- **prod** — images pinned, debug/introspection surfaces off, host hardening
  assumed (Step 5), only the edge published.

Base conventions (all from the corpus page, do not restate): services reach
each other by **service DNS**, never IP; **named volumes** for all stateful
data; **`.env` interpolation** with fail-closed required secrets (`${X:?}`) and
safe non-secret defaults (`${X:-default}`); DRY the fleet with **YAML anchors**;
every long-lived service has a **`healthcheck`** and dependents wait on
`depends_on: {x: {condition: service_healthy}}`; **publish only the edge** —
bind sensitive services (DBs, brokers, admin) to **loopback**
(`127.0.0.1:<port>:<port>`), everything else stays in-network; `restart:
unless-stopped`; opt-in planes (monitoring) behind compose `profiles`.

## Step 3 — the deploy pipeline (`deploy.sh`, idempotent, one command)

1. **Preflight** — `set -euo pipefail`; resolve `SCRIPT_DIR`; build the
   connection once: `SSH="ssh -i <ssh-key> -o StrictHostKeyChecking=no
   <ssh-user>@<host>"`. (A bare-IP host with no `~/.ssh/config` entry needs
   `-i`; a host that DOES have a config entry is addressed by alias without
   `-i`.)
2. **Ensure `.env`** — if absent, `cp .env.example .env`, warn the operator to
   fill it, stop. Then load it fail-closed.
3. **Ensure TLS** (idempotent) — generate a self-signed cert on the host only if
   absent (`tool-corpus/ops/self-signed-tls-cert.md` — SAN not just CN), else
   reuse; never regenerate a trusted cert on redeploy.
4. **Prepare the host** — ensure Docker Engine + Compose v2 and the hardening
   floor are in place (Step 5); idempotent.
5. **Ship the source** — `ssh mkdir -p <remote-dir>`; `rsync -az --delete` a
   curated include list (excludes `.git`, build output, `node_modules`), with a
   `tar -czf - … | ssh 'tar -xzf -'` fallback when rsync is absent. Ship `.env`
   and `certs/` explicitly (they are sync-excluded). **Source is shipped — never
   `git`-pulled on the host, never built locally.**
6. **Build + tag + up ON THE HOST** — build each service's image **on the
   host** and tag it with an immutable ref (a content digest / git-SHA tag),
   then `$SSH 'cd <remote-dir>/deploy && DOCKER_BUILDKIT=1 docker compose -f
   docker-compose.yml -f docker-compose.<mode>.yml -p <project> up -d
   --remove-orphans'` against those tags. A host rebuild happens only when the
   source changed — the built-and-tested image is the one that runs.
7. **Gate** — run `tests/e2e-smoke.sh` against the live host (Step 4 of the
   smoke tool); nonzero exit fails the deploy.
8. **Report** — `$SSH 'docker compose … ps'` + print the verification curls.

Redeploy of one unchanged service repoints its pinned tag and `up -d --no-deps
<svc>` with **no rebuild** — the released bits are the tested bits. Rollback
repoints that service to its previous retained tag the same way; only a source
change triggers a host rebuild (see the `release`/`rollback` runbook templates,
which own the retag-don't-rebuild doctrine). Disk hygiene on the host: prune
build cache and dangling images, **never `--volumes`** (that is the data).

## Step 4 — secrets & TLS

Secrets live only in the gitignored `.env` (rotate via
`tool-corpus/ops/env-secret-rotation.md`: CSPRNG-generated or **stdin-only**,
never argv/log/`set -x`, atomic in-place rewrite, refuse a git-tracked target).
When the original infrastructure is gone (a common brownfield case) the method
is self-contained: build from source (no registry needed), point any config
service at a local filesystem backend, and let dead external dependencies fail
at runtime while services still boot.

## Step 5 — host prep & hardening

Before the first bring-up, `reliability` runs the **`harden-docker-host`** skill,
which owns the ordered floor and its per-control gate (and defers in turn to
`library-corpus/container/docker-host-hardening.md` for what each control is and
why). Two of its properties are load-bearing *for this method*: its firewall step
is **operator-gated**, never automatic, so the bring-up may not assume inbound
filtering exists — **the loopback binding of Step 2 is the containment that is
always on**, whatever the operator decides; and the whole procedure is a
no-op-safe re-run, so every redeploy re-asserts the floor instead of trusting
that it was done once.

## The invocation

`/deploy-fleet <host> key <ssh-key> [mode=prod]` binds `<host>`/`<ssh-key>`
(and optional `<ssh-user>`/`<remote-dir>`/`mode`) and runs Steps 0–3 end to
end: preflight → host prep → ship source → build+up on host in the chosen mode
→ smoke → report. Default mode is `prod`. A project instantiating this skill
names the command to match its own host substrate.

## Anti-patterns

- Building (or running a Docker daemon) locally — everything builds on the host.
- Editing the base compose per environment instead of overlaying.
- A secret in an image layer, an `ARG`, argv, a log, or a git-tracked file.
- A datastore on `0.0.0.0` instead of loopback + in-network DNS.
- `git pull` on the host instead of shipping the reviewed source.
- Pruning `--volumes` to reclaim disk.

## Reference files

- `skill-corpus/harden-docker-host.md` (Step 5, run by `reliability`)
- `library-corpus/container/docker.md`, `docker-compose.md`, `docker-host-hardening.md`
- `tool-corpus/ops/{container-deploy-pipeline,self-signed-tls-cert,env-secret-rotation}.md`,
  `tool-corpus/testing/http-smoke-suite.md`
- `templates/docs/runbooks/{release,rollback}.md`
