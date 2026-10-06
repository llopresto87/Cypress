# bitbucket-pipelines — platform

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). This is a **hosted-platform surface**: Bitbucket
> Cloud has no installable package and no major versions, so it is pinned by
> **retrieval date**: the surface below was last confirmed against Atlassian's
> documentation **2026-10-05**. Orientation only: for a project's own workspace,
> runners, variables and deployment environments, run `ingest-library` against
> the project, and re-confirm anything load-bearing against current upstream
> docs.

## What it is
Bitbucket Pipelines is the CI/CD service built into Bitbucket Cloud. A
pipeline is one YAML file, `bitbucket-pipelines.yml`, at the repository root.
Each step runs in a separate Docker container started from an image set at
file level and overridable per step (`atlassian/default-image:latest` when
none is set). Hosted steps run on Atlassian infrastructure; self-hosted
runners (Linux Docker, Linux shell, Windows, macOS) run steps on the team's own
machines. The documentation is Atlassian's support site; it is proprietary, so
this page paraphrases it.

## Install, setup and configuration
- **Top-level keys**: `image`, `options`, `clone`, `definitions`, `pipelines`
  (required, once) and `triggers`.
- **`options`** (global): `docker` (false), `max-time` (1–720 minutes,
  default 120), `size` (`1x` default, up to `32x`), `runtime.cloud`
  (`atlassian-ip-ranges` false; `arch` `x86` or `arm`) and `oidc`.
- **Step sizes** on hosted infrastructure (CPU / memory / disk): 1x 2/4 GB/64
  GB; 2x 4/8 GB/64 GB; 4x 8/16 GB/256 GB; 8x 16/32 GB; 16x 32/64 GB; 24x
  48/96 GB; 32x 64/128 GB (256 GB disk from 4x up). Memory is shared by the
  script and every service. Above 2x needs a paid plan; 4x and up get dedicated
  CPUs; a step of size N uses N times the build minutes. `size` does nothing on
  shell runners.
- **`clone`**: `depth` (default 50 commits, or `full`), `lfs` (false; enable
  per step), `enabled` (true; `false` skips the clone, for pure deploy steps),
  and `skip-ssl-verify` (self-hosted runners only). Global or per step.
- `[skip ci]` or `[ci skip]` in a commit message skips the pipeline.
- **Images.** `image: {name, username, password, run-as-user}` (root by
  default) for private registries, or `aws: {oidc-role}` for ECR (upstream
  recommends OIDC over `access-key`/`secret-key`). Images must be reachable
  from the internet. Digest pins (`name: <image>@sha256:<digest>`) are
  supported. `atlassian/default-image` tags track Ubuntu releases; ARM
  runners need the newer tags.

## Core API / usage shape
### Start conditions
```yaml
pipelines:
  default:            # push to any branch no other section matches (not tags)
    - step: {script: [...]}
  branches:
    'release/*':      # quote a glob that starts with '*'
      - step: {...}
  tags:
    'v*': [...]
  pull-requests:
    '**':             # matched against the PR *source* branch
      - step: {...}
  custom:
    redeploy:         # started by hand or by schedule
      - variables:
          - name: TARGET
            default: staging
            allowed-values: [staging, production]
      - step: {...}
```
- **Pull-request pipelines** run when a PR is created or updated, after the
  destination branch is merged into the source (a failed merge stops the
  pipeline). They run in addition to branch and default pipelines, so one
  push can start two. Pull requests from forks do not trigger pipelines.
- **`custom`** pipelines run only by hand or on a schedule; their `variables`
  are prompted at run time and exist only there.
- **Top-level `triggers`** fire `custom` pipelines from events
  (`repository-push`, `pullrequest-created`/`-updated`/`-fulfilled`/
  `-rejected`/`-push`, `pipeline-completed`, `deployment-completed`, and
  more) with a `condition` expression (`==`, `!=`, `&&`, `||`, `!`,
  `glob(value, "pattern")`, `changesetInclude(...)`, case-sensitive). All
  listed pipelines start in parallel.
- A push that moves more than five branches or tags at once starts nothing.
- **Globs**: `*` does not cross `/`, `**` does; an exact name beats a
  pattern, a longer pattern beats a shorter one; quoted and unquoted names
  are the same key.

### Steps, stages and parallel
- A **step** needs `script`; options include `name`, `image`, `max-time`,
  `size`, `runtime`, `caches`, `services`, `artifacts`, `clone`, `condition`,
  `trigger`, `deployment` or `environment`, `oidc`, `after-script`, `on-fail`,
  `fail-fast`, `output-variables`, `concurrency-group`, `runs-on`, `config`
  and `type` (`pipeline` for a child pipeline). Script commands run in order
  with no cleanup between them. A pipeline holds at most 100 steps.
- **`after-script`** runs whether the script passed or failed, with
  `BITBUCKET_EXIT_CODE` (0 or 1) set; a failure inside it does not change the
  step's result.
- **`final`**: one per pipeline, always last, runs even after a failure and
  again on a re-run; not in a stage or parallel group, not manual, no
  `deployment`.
- **`on-fail.strategy`**: `fail` (default), `retry` (`maxRetryCount` 1–10) or
  `ignore`; not on deployment steps.
- **`parallel`**: `steps:` plus optional `fail-fast`. Parallel steps cannot
  see each other's artifacts; each gets `BITBUCKET_PARALLEL_STEP` (0-based)
  and `BITBUCKET_PARALLEL_STEP_COUNT`; every one counts toward the 100.
- **`stage`**: groups sequential steps under one `deployment`, `trigger`,
  `condition` and `on-fail`. No parallel or manual steps inside, and steps
  cannot override stage properties.
- **`condition`**: `changesets` (`includePaths` runs the step if any changed
  file matches; `excludePaths` skips it if all do) or `state` (a boolean
  expression over variables; secured variables not allowed). In pull-request
  pipelines every commit counts; elsewhere only the last commit does.
- **`trigger: manual`** (step or stage): never first, runs only after the
  previous one succeeded, needs write access. For a whole manual pipeline use
  `custom`.
- **`concurrency-group: <name>`**: one step of the group runs at a time,
  first in, first out.
- **Reuse**: YAML anchors under `definitions.steps` (`&name`, `*name`,
  `<<: *name`; anchor names cannot contain `[ ] { } ,`); step configs in
  `definitions.step-config.<name>` inherited with `config: <name>` (top-level
  merge; a list on the step replaces the inherited list); shared pipeline
  files imported through `definitions.imports` (Premium).

### Definitions, caches, artifacts, services
- **Caches**: predefined `node`, `composer`, `maven`, `gradle`, `pip`,
  `docker`, `dotnetcore`, `ivy2`, or `definitions.caches.<name>` as a path, or
  `{key: {files: [...]}, path: ...}`, which starts a new cache whenever a
  listed file changes. Each cache is capped at 1 GB compressed, expires after 7
  idle days, and "may be cleared at any time"; parallel steps read but do not
  write them.
- **Artifacts**: `paths` (under `BITBUCKET_CLONE_DIR`, no `.` or `..`),
  `ignore-paths`, `capture-on` (`success` default, `failed`, `always`), types
  shared (default), `scoped` (stay with the step) and `test-report` (XML).
  A later step can opt out with `download: false` or a name list. Limit 1 GB,
  kept 14 days, downloaded with mode 644 (re-`chmod +x` scripts).
- **Services**: `definitions.services.<name>` with `image`, `variables` and
  `memory` (MB, default 1024). They share the build container's network and
  listen on `localhost` (use `127.0.0.1` to avoid IPv6 trouble), with no port
  mapping. At most 5 per step, port 29418 is reserved, and there is **no
  readiness wait**. Total memory is 4096 MB at 1x, 8192 at 2x, and doubles per
  size; the build container keeps at least 1024 MB.
- **Docker in a step**: `services: [docker]` (or legacy `options.docker`).
  BuildKit is on; multi-arch builds, `--platform`, Buildx and
  `RUN --mount=type=ssh` need Runtime v3. The predefined `docker` cache does
  not cache BuildKit layers.
- **Pipes**: `- pipe: <vendor>/<name>:<version>` with `variables:`; a pipe is
  a Docker-based action, needs the Docker service (counted toward the limit,
  1 GB by default), and usually accepts `DEBUG: 'true'`. Read the pipe's own
  README for its current version.

### Variables and secrets
- `$NAME` on Linux and macOS, `$env:NAME` on Windows runners.
- **Defaults** include `CI`, `BITBUCKET_BUILD_NUMBER`, `BITBUCKET_CLONE_DIR`,
  `BITBUCKET_COMMIT`, `BITBUCKET_BRANCH` (branch builds only),
  `BITBUCKET_TAG` (tag builds only), `BITBUCKET_PR_ID`,
  `BITBUCKET_PR_DESTINATION_BRANCH`, `BITBUCKET_REPO_SLUG`,
  `BITBUCKET_WORKSPACE`, `BITBUCKET_DEPLOYMENT_ENVIRONMENT`,
  `BITBUCKET_EXIT_CODE` (after-script), `BITBUCKET_STEP_OIDC_TOKEN`,
  `BITBUCKET_SSH_KEY_FILE`, `BITBUCKET_PACKAGES_USERNAME`/`_TOKEN`,
  `DOCKER_HOST` and the `BITBUCKET_TRIGGER_*` family.
- **Precedence**, highest first: Pipeline > Deployment > Repository >
  Workspace. Workspace variables need a workspace admin; repository variables
  are managed by repository admins and usable by anyone with write access;
  deployment variables belong to one environment.
- **Names**: letters, digits and underscore, case-sensitive, no leading
  digit; values up to 120,000 characters. Upstream: avoid `PATH`, which breaks
  pipeline commands.
- **Secured variables** are masked in logs, including URL-encoded forms, and
  can only be replaced or deleted, never edited. Other encodings (base64, say)
  are not documented as masked.
- **Passing values between steps**: append `NAME=value` to
  `$BITBUCKET_PIPELINES_VARIABLES_PATH` and list the name under
  `output-variables`; at most 50 variables and 100 KB per pipeline; only later
  sequential steps see them.
- **`${{NAME}}`** templating in the YAML accepts workspace and repository
  variables and some defaults, but not secured or runtime custom variables.

### Deployments, runners, OIDC
- **Deployments**: default environments Test, Staging and Production. A
  step or stage with `deployment: <env>` gets that environment's variables,
  subject to branch and permission checks (deployment permissions are
  Premium). One deployment per environment runs at a time; later ones pause.
  A redeploy needs a prior success and unexpired artifacts.
- **Runners**: `runs-on:` labels must all match one runner (`self.hosted`
  plus an OS label such as `linux.shell`, `linux.arm64`, `windows`, `macos`;
  no OS label means Linux Docker). No matching online runner fails the step;
  busy runners queue it.
- **OIDC**: `oidc: true` on a step puts a signed ID token in
  `BITBUCKET_STEP_OIDC_TOKEN` for assuming a cloud role. The identity provider
  URL and audience come from the repository's Pipelines OpenID Connect
  settings; custom audiences go under `oidc.audiences` (up to 10).

## Idioms & best practices
- Install once with `caches` and file-keyed cache keys, build once into
  `artifacts`, then fan tests out with `parallel`.
- Keep `clone.depth` small, enable `lfs` only where needed, and set
  `clone.enabled: false` on pure deploy steps.
- Deploy through `deployment:` steps in test, staging, production order, with
  `trigger: manual` as the gate before production.
- Factor repeated steps with anchors or `step-config`; use
  `condition.changesets` in a monorepo, knowing its last-commit rule.
- Mark every secret secured and keep it out of the YAML; shared values at
  workspace scope, per-environment values at deployment scope; rotate them,
  and list the required variable names in the repository README.
- Prefer OIDC to stored cloud keys; self-hosted runners can also pull from an
  external secret manager.
- Pin step images to a full tag or a digest (upstream examples use major
  tags), on the language line the project builds for.
- In Docker builds, pass secrets with `--secret` and `RUN --mount=type=secret`,
  never `--build-arg`, which lands them in the image and the logs.
- Put a wait loop in front of tests that use service containers.
- Do not reuse the registry login to fetch runtime secrets in deploy scripts.
  Observed in practice: it widened one credential's reach, and a file-name
  mismatch failed silently; upstream points to secured variables or a secret
  manager instead.

## General pitfalls
- **Two pipelines per push** when a branch section and a pull-request section
  both match.
- **Skipped is not passed.** Outside pull-request pipelines, `changesets`
  reads only the last commit, so a multi-commit push can skip a step, and
  upstream warns that a failing pipeline can turn green only because the
  failing step was skipped on the next run.
- **Fourteen-day horizon.** Artifacts expire after 14 days, and with them the
  ability to run a pending manual step or redeploy.
- **Services start without a wait** and share the step's memory with the
  build; an out-of-memory service kills the step.
- **Caches are not storage.** They can vanish at any time; never use one for a
  build output.
- **`max-time` defaults to 120 minutes**; a hung step runs to the limit.
- **Fork builds and secrets.** Whether secured variables would reach a fork
  build is undocumented; never assume they do or do not.
- **IPv4 only** on builds.
- **Docs disagree with each other** on a few points; write the safe form:
  - set `oidc: true` explicitly (one page says it defaults to false, another
    to true);
  - plan on 2 CPUs for 1x (the text mentions up to 4 shared);
  - plan service memory within 128–3072 MB (one page allows up to 4096) and
    keep 1024 MB for the build;
  - plan on 5 services per step, though the legacy Docker option page says
    two others;
  - never copy a pipe version from an example.

## Testing
- Validate the YAML with Atlassian's online validator before pushing.
- Run the step's commands locally in the same image, especially the service
  wait and the Docker build.
- The Tests feature (beta; Standard and Premium) reads JUnit and Maven
  Surefire XML from a step and shows failures and flaky tests; `test-report`
  artifacts are XML scoped to one step.
- Collect logs in `after-script`; report in a `final` step that always runs.

## Security defaults
- Secured variables mask values in logs; plain variables do not.
- Fork pull requests do not run pipelines at all.
- **SSH access**:
  - client keys: Ed25519 (256), ECDSA (256), RSA (2048 or more), DSA (1024),
    OpenSSH format;
  - **access keys** (repository or project level) are read-only, take no
    seat, belong to no account and usually carry no passphrase, so the key
    file is the whole secret; a project key reaches every repository in the
    project. Repository, project and personal keys are three different blast
    radii;
  - the Pipelines key is at `BITBUCKET_SSH_KEY_FILE` (use
    `--ssh default=$BITBUCKET_SSH_KEY_FILE` with BuildKit).
- **Host keys rotate.** Record Bitbucket's host key before the first
  connection, from the keys Atlassian publishes at
  `https://bitbucket.org/site/ssh` (`ssh git@bitbucket.org host_key_info`
  shows the key in use). A past rotation added ECDSA and Ed25519 keys,
  replaced the RSA key and removed DSA, and clients with pinned old keys
  failed: populate `known_hosts` from the live source, never from a copied
  fingerprint. Upstream flags `StrictHostKeyChecking no` as not recommended
  (man-in-the-middle). Atlassian maintains the host keys inside Pipelines
  builds itself; self-hosted runners clone over HTTPS with tokens.
- OIDC trust policies on the cloud side can restrict by repository,
  environment, Atlassian IP range and a short step `max-time`.

## Operational behaviour
- Limits: 100 steps per pipeline; 10 concurrent steps on a free workspace,
  600 on paid plans (excess steps fail). Build minutes, storage and larger
  sizes depend on the plan.
- One step is one fresh container; nothing survives between steps except
  artifacts, caches and output variables.
- Hosted steps egress from AWS ranges by default; `atlassian-ip-ranges: true`
  uses Atlassian's published ranges for allow-listing.
- Self-hosted runners: at most 120 minutes per step.

## Interop
- Container registries via `image` credentials or OIDC; Bitbucket's package
  registry via `BITBUCKET_PACKAGES_*`. Docker build practice:
  [`container/docker.md`](../container/docker.md).
- AWS, GCP and Vault via OIDC; pipes for clouds, Kubernetes, npm and chat
  notifications.
- Jira issues link to deployments through issue keys in commit messages.
- A service that clones its configuration from a Bitbucket repository at boot
  puts Bitbucket Cloud and its SSH endpoint in its cold-start path, and the
  access key's scope sets the blast radius; the config-server side lives on its
  own page.
- The Azure DevOps counterpart is
  [`platform/azure-pipelines-yaml.md`](azure-pipelines-yaml.md).

## Major lines
Bitbucket Cloud has no major versions. Feature areas that arrived over time
and that an older pipeline file will not use: step `config`, top-level
`triggers` with expression conditions, `condition.state`, `on-fail`, `final`,
`concurrency-group`, child pipelines with artifact passing, shared pipeline
files, Runtime v3 for Docker, `environment` beside `deployment`, and Tests in
Pipelines. The `email` field of a Docker Hub image login is deprecated and no
longer needed.

## Upstream docs
- https://support.atlassian.com/bitbucket-cloud/docs/bitbucket-pipelines-configuration-reference/
- https://support.atlassian.com/bitbucket-cloud/docs/global-options/
- https://support.atlassian.com/bitbucket-cloud/docs/step-options/
- https://support.atlassian.com/bitbucket-cloud/docs/pipeline-start-conditions/
- https://support.atlassian.com/bitbucket-cloud/docs/variables-and-secrets/
- https://support.atlassian.com/bitbucket-cloud/docs/cache-dependencies/
- https://support.atlassian.com/bitbucket-cloud/docs/use-artifacts-in-steps/
- https://support.atlassian.com/bitbucket-cloud/docs/databases-and-service-containers/
- https://support.atlassian.com/bitbucket-cloud/docs/run-docker-commands-in-bitbucket-pipelines/
- https://support.atlassian.com/bitbucket-cloud/docs/integrate-pipelines-with-resource-servers-using-oidc/
- https://support.atlassian.com/bitbucket-cloud/docs/set-up-repository-access-keys-on-linux/
- https://support.atlassian.com/bitbucket-cloud/kb/bitbucket-cloud-ssh-host-key-rotation-faq/
