# Tool: container-deploy-pipeline

> Project-agnostic, durable capability notes, folded into the seed by the
> harvest protocol. Orientation for a reusable tool, NOT a project runbook — the
> adopting plant re-authors the blueprint sections against its own container tool
> and host layout, test-first.

## 0. Identity

- **Category:** ops
- **Name:** container-deploy-pipeline
- **Language / runtime:** bash (host needs only a container/orchestration CLI —
  **no language toolchains**, since building happens inside the builder)
- **Stability:** portable surface + **blueprint** implementation (the remote/host
  and container-tool steps are filled against the adopting stack)

## 1. What it does

A single staged, verbose driver for the whole lifecycle of a remotely-deployed
container image: **preflight → build → deploy → healthcheck → smoke**, plus
`release` and `rollback` as first-class stages. It exists to stop every project
from re-growing the same brittle "ssh in, docker build, hope it came up" script,
and to encode one hard discipline: **the released bits are the tested bits**.
Every deploy and rollback pins an **immutable tag + digest**, never a floating
ref (`latest`, a branch name), so what runs is exactly what was built and
verified.

## 2. Interface & invocation

The stable contract is a subcommand + flags surface. Names are illustrative; the
shape is the durable part.

```sh
deploy.sh <stage> [flags]
#   stages:  preflight | build | deploy | release | rollback | smoke | up (all)
#   flags:   --no-build     reuse the current image, skip the build stage
#            --partial      rebuild only changed layers (no --no-cache)
#            --no-smoke     deploy without running the smoke gate
#            --down         stop/remove the running container(s)
#            --tag <ref>    operate on a specific immutable tag (deploy/rollback)
```

- **Inputs:** a stage selector; optional flags; deploy target + registry
  coordinates supplied by **config/env**, never baked into the script.
- **Outputs:** per-stage banners to stdout; a non-zero exit on the **first**
  failing stage (fail-fast); the deployed image's resolved tag+digest echoed so
  it can be recorded.
- **Preconditions:** the container CLI is present on the invoking host; the
  registry is reachable and authenticated; the deploy target answers preflight.

Key semantic distinctions that must survive re-authoring:

- **`build`** produces an artifact tagged with an **immutable** id (e.g. a
  content or commit-derived tag) and pushes it.
- **`release`** only **re-tags and re-pushes an already-built artifact** — it
  **never rebuilds**. Promotion moves the exact bytes that passed the gates;
  rebuilding at release time would ship untested bits.
- **`deploy` / `rollback`** always pull a specific **tag + digest**. Rollback is
  just a deploy of a previously-good immutable ref — no rebuild, no guesswork.

## 3. Approach / algorithm

1. **Preflight** — cheap reachability and precondition checks first (target
   answers, registry auth valid, required config present). Fail here before
   spending a build.
2. **Build** — build inside the builder using **BuildKit cache mounts** so
   dependency layers and package caches persist across builds; tag with an
   immutable id and push. `--partial` skips `--no-cache`; the default is a clean
   build for release candidates.
3. **Deploy** — pull the pinned tag+digest on the target and start the
   container(s). Never deploy a floating ref.
4. **Healthcheck** — poll the **container's own healthcheck** (the orchestrator's
   health status / the image's declared `HEALTHCHECK`), **not a host-side port
   probe**. A port probe **false-fails** whenever the service is healthy but its
   port is not published to the host (internal-only networks, reverse-proxy
   fronting, sidecars). Poll with a bounded timeout and a clear timeout message.
5. **Smoke** — run the post-deploy smoke gate (see the http-smoke-suite tool);
   `--no-smoke` opts out explicitly for emergency pushes.
6. **Fail-fast throughout** — any stage's failure aborts the pipeline with a
   non-zero exit and a labelled banner; `up` runs the stages in order and stops
   at the first failure.

## 4. Portable vs blueprint

- **Portable:** the stage decomposition, the immutable-tag discipline, the
  build-once/release-promotes rule, the "poll the container's own health, not a
  host port" rule, the fail-fast + per-stage-banner control flow, the flag
  surface. These are stack-neutral and should be preserved verbatim in intent.
- **Blueprint (fill against your stack):** the actual container/orchestration
  commands (single-container CLI vs a compose/orchestrator up), how you reach the
  remote host (ssh, an agent, a control-plane API), how you read the health
  status, and how the registry is authenticated. Present these as slots the
  adopting project wires to its own tooling.

Blueprint skeleton (stack-neutral scaffolding; container/remote commands are
placeholders to fill):

```bash
#!/usr/bin/env bash
set -euo pipefail

banner() { printf '\n=== %s ===\n' "$1"; }

# --- config comes from env / a config file, never baked in ---
: "${DEPLOY_TARGET:?set deploy target}"
: "${REGISTRY:?set registry}"
IMAGE="$REGISTRY/<name>"

preflight() {
  banner "preflight"
  # reachability + auth + required-config checks; fail here, cheaply
  : # <fill: ping target, verify registry login, assert config present>
}

build() {
  banner "build"
  local tag="$1"                       # immutable id (content/commit-derived)
  # BuildKit cache mounts keep dependency layers warm across builds
  DOCKER_BUILDKIT=1 <build-cmd> \
    ${PARTIAL:+} ${PARTIAL:---no-cache} \
    -t "$IMAGE:$tag" .                  # <fill: your builder>
  <push-cmd> "$IMAGE:$tag"             # <fill>
}

release() {                            # promote ONLY — never rebuild
  banner "release"
  local from="$1" to="$2"
  <pull-cmd> "$IMAGE:$from"            # the already-built, already-tested bytes
  <retag-cmd> "$IMAGE:$from" "$IMAGE:$to"
  <push-cmd> "$IMAGE:$to"
}

deploy() {                             # always pin tag + digest
  banner "deploy"
  local ref="$1"                       # tag@digest
  # <fill: on DEPLOY_TARGET, pull $IMAGE:$ref and (re)start container(s)>
}

healthcheck() {                        # poll the CONTAINER's own health
  banner "healthcheck"
  local deadline=$(( SECONDS + ${HEALTH_TIMEOUT:-120} ))
  until <container-health-is-healthy>; do   # <fill: read orchestrator/HEALTHCHECK status>
    (( SECONDS < deadline )) || { echo "unhealthy after timeout"; return 1; }
    sleep 3
  done
}

rollback() { deploy "$1"; }           # deploy a known-good immutable ref

smoke() { banner "smoke"; [ -n "${NO_SMOKE:-}" ] && return 0; ./smoke.sh; }

case "${1:-up}" in
  preflight) preflight ;;
  build)     build "${TAG:?}";;
  release)   release "${FROM:?}" "${TO:?}";;
  deploy)    deploy "${TAG:?}";;
  rollback)  rollback "${TAG:?}";;
  smoke)     smoke ;;
  up)        preflight; [ -n "${NO_BUILD:-}" ] || build "${TAG:?}"; \
             deploy "${TAG:?}"; healthcheck; smoke ;;
  *) echo "unknown stage: $1" >&2; exit 2 ;;
esac
```

## 5. Pitfalls and sharp edges

- **Host-side port probes false-fail.** The most common bug this tool prevents:
  a healthy container whose port is not published to the host reads as "down" to
  a `curl localhost:PORT` probe. Always poll the container's own health status.
- **Rebuilding at release time ships untested bits.** If `release` rebuilds, the
  promoted image is not the one the gates passed. Promotion must re-tag an
  existing artifact only.
- **Floating tags erase reproducibility.** Deploying/rolling back to `latest` or
  a branch name means "what runs" drifts. Always pin tag + digest.
- **Silent partial builds.** `--partial` reusing a stale cached layer can hide a
  dependency change; use clean builds for release candidates, partial only for
  fast local iteration.

## 6. Tests that cover it

A durable version is authorized by tests before cataloging in a plant. Cover at
minimum: each stage fails fast on an injected precondition failure; `release`
never invokes the build path; deploy/rollback reject a non-immutable ref; the
healthcheck loop times out (not hangs) when health never turns green.

- **How to run the tests:** `<the plant's test command for shell tooling>`

## 7. References & neighbours

- **Related tools:** `tool-corpus/testing/http-smoke-suite.md` (the smoke gate
  this pipeline runs); `tool-corpus/ops/self-signed-tls-cert.md` (cert material a
  deployed TLS endpoint may need).
- **Sources:** distilled from harvested plant experience; no external URL.

## 8. Changelog

- 2026-07-16 — created from harvested, generalized capability, by docs-librarian.
