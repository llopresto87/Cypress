# azure-pipelines-yaml — platform

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). This is a **hosted-platform surface**: there is
> no installable package and no version to pin, so it is pinned by **retrieval
> date**: the surface below was last confirmed against upstream documentation
> **2026-09-25** for the governance, target, checkout, cache and attempt-counter
> details; the rest was confirmed on earlier dates. Some details were read in
> the agent's source or measured with compile-only preview runs, as marked. For
> a project's own agent pools, service connections, variable groups and
> governance checks, run `ingest-library` against the project itself, and
> re-confirm anything load-bearing against current upstream docs.

## What it is
**Azure Pipelines YAML** is the pipeline-as-code schema of Azure Pipelines, the
CI/CD service in Azure DevOps. A file in the repository describes the whole run:
its triggers, its stages, jobs and steps, which agent pool executes them, which
other repositories are checked out, and which variables and secrets are in
scope. The platform compiles that file into a run. The schema reference lives on
Microsoft Learn (`azure/devops/pipelines/yaml-schema`), and the agent that runs
the jobs is open source (`microsoft/azure-pipelines-agent`).

It is a surface of a hosted service, not a library: there is no package, no
release to pin, and no changelog to diff. What is durable is the shape: a
**schema**, a **template model** (two kinds of reuse), **three expression
contexts evaluated at three different times**, a **variable and secret model**,
a **governance model** of checks and job tokens, and the **agent behaviours**
the whole thing sits on.

The mental model that explains most surprises: **a pipeline is compiled, then
authorized, then executed**. Each phase sees a different world.

## Install, setup and configuration
- Nothing installs. A pipeline is a YAML file in a repository, registered as a
  pipeline definition that points at the file's path and a default branch.
- Some behaviour is set outside the YAML, in pipeline, project or
  organization settings, and the YAML cannot see it: checkout defaults
  ("shallow fetch", "sync tags"), the job authorization scope, "protect access
  to repositories", "limit variables that can be set at queue time", and every
  check on a protected resource. An organization-level setting wins over the
  project.
- **Checkout defaults differ by pipeline age and organization.** Newer
  pipelines may default to a shallow depth of 1 with no tags; older ones fetch
  full history with tags. An explicit `fetchDepth: 0` overrides the UI shallow
  setting and an explicit `fetchTags` overrides "sync tags". `persistCredentials`
  defaults to false and `clean` follows the UI setting.
- **Timeouts.** `timeoutInMinutes` defaults to 60 when unset, and
  `cancelTimeoutInMinutes` bounds how long a canceled job may run its cleanup.
  `0` means no limit only where no hosted cap applies; a hosted agent caps a job
  whatever the YAML says. Treat the numbers as orientation and confirm them.
- **Service versions.** The cloud service and the on-premises server ship
  different feature sets (see Major lines).

## Core API / usage shape
```
pipeline:  trigger | pr | schedules | resources | variables | parameters
           stages: | jobs: | steps: | extends:
resources.repositories: {repository, type, name, endpoint, ref}   # other repos as template sources / checkouts
resources.pipelines:    {pipeline, source, trigger: {branches, stages, tags}}  # run on another pipeline's completion
- template: path.yml[@alias]              # INCLUDE-style reference: splices content in
extends: {template, parameters}           # EXTENDS-style: the template owns the shape
parameters: [{name, type, default, values}]
        # types: string | number | boolean | object | stringList |
        #        step | stepList | job | jobList | deployment |
        #        deploymentList | stage | stageList
${{ each item in parameters.list }}: ...  # compile-time iteration (list or object)
${{ insert }}: ${{ parameters.obj }}      # splice an object's keys into a mapping
${{ if }} / ${{ elseif }} / ${{ else }}   # compile-time conditional insertion
${{ expr }} | $[ expr ] | $( var )        # template / runtime / macro contexts
templateContext: {...}                    # per-item metadata carried on job/stage/step list params
checkout: self | none | <repo alias> | git://Project/Repo@ref
          # keys: path, clean, fetchDepth, fetchTags, persistCredentials, workspaceRepo
uses: {repositories: [...], pools: [...]} # job-level: declare access without a checkout
target: {container, commands: any|restricted, settableVariables: none|[names]}
          # step property on script, task, checkout, download, publish
deployment: {environment, strategy: {runOnce | rolling | canary}}
condition: / dependsOn: [...]             # stage- and job-level gating
timeoutInMinutes: / cancelTimeoutInMinutes:
variables:                                # list syntax combines all three:
  - name: x            value: y           #   literal pairs
  - group: <name>                         #   variable-group reference
  - template: vars.yml[ + parameters:]    #   a variables template (may itself carry groups)
pool: / workspace: {clean: outputs|resources|all}
- task: Cache@2  inputs: {key, restoreKeys, path}
```
- A variables template is **not** values-only: it may contain literal pairs and
  variable-group references, and it accepts its own `parameters:`. Mapping
  syntax and list syntax cannot be mixed in one `variables:` section; anything
  beyond literal pairs needs list syntax.
- The inline checkout form `git://Project/Repo@ref` needs no `resources` entry.
- `resources.pipeline.<alias>.*` variables (run id, source branch and so on)
  exist only at runtime, so a template expression cannot see them.
- **Status functions** for `condition:`: `succeeded()` (the default gate),
  `succeededOrFailed()` (runs after a failure but not after a cancel),
  `always()` (runs even after a cancel), `failed()`.
- **Output variables.** A step sets one with the `task.setvariable` logging
  command and `isOutput=true`. Another job in the same stage reads it as
  `$[ dependencies.<job>.outputs['<step>.<var>'] ]`; a job in a later stage
  reads `$[ stageDependencies.<stage>.<job>.outputs['<step>.<var>'] ]`.
- **Attempt counters.** `System.JobAttempt`, `System.StageAttempt` and
  `System.PhaseAttempt` start at 1 and go up on each retry. None exists at
  template expansion.

## Idioms & best practices
- **`extends` for governed pipelines, `template:` includes for reusable
  fragments.** An include splices content in with no ceiling on what the consumer
  can add. An `extends` template owns the pipeline's shape, and the consumer may
  only supply what its parameters (typically a `stepList` or `jobList`) allow.
  Only `extends` can be paired with a required-template check that makes the
  governed template mandatory. If a template exists to enforce something, it
  must be an `extends` template; otherwise it is a suggestion.
- **An `extends` template can enforce policy at compile time** by rewriting the
  consumer-supplied step or job list with `${{ each }}` and `${{ if }}`: reject
  or replace script-running task types, constrain the pool to an allow-list,
  force steps into a locked-down container with `target:`, and restrict which
  variables a step may set with `settableVariables`.
- **Block variable setting with `settableVariables: none`.** That is the
  documented spelling. Measured: the compiler normalizes it to `[]` in the
  compiled YAML, and a list of names is kept as written.
- **Generate maps instead of hand-maintaining them.** A typed `object` parameter
  plus `${{ each }}` and `${{ insert }}` emits an `env:` or `variables:` mapping
  whose key names the template never has to know:
  ```yaml
  parameters:
  - name: envMap
    type: object
    default: {}
  steps:
  - ${{ each kv in parameters.envMap }}:
    - script: echo using ${{ kv.key }}
      env:
        ${{ kv.key }}: $(${{ kv.value }})
  ```
  This removes boilerplate, not the per-secret mapping requirement below.
- **Declare shared variable groups once in a variables template** and consume
  it from each pipeline, so the group list has a single home. Read the
  compile-order pitfall first: per-pipeline authorization of a group does not
  travel with the template.
- **Settle it before the run as a parameter; let it vary per run as a
  variable.** Before a pipeline runs, templates and their parameters become
  constants. Anything the platform needs as a constant (a checkout ref, a
  template path, a stage list) must be a parameter; a variable cannot stand in
  for it. A parameter with a `values:` list restricts the choice, for a pool or
  an environment, to a fixed set.
- **Queue-time parameter validation makes a typo loud; lean on it.** Runtime
  parameters are checked when the run is queued, before anything executes. A
  parameter the pipeline does not declare is rejected, and a non-boolean value
  for a `boolean` parameter is rejected. Observed in practice: `yes` fails,
  while `true`, `True`, `TRUE`, `false` and `False` pass, and the run records
  the value back as `True` or `False`. A template that compares a boolean
  against string literals should normalize case first.
- **Choose the expression context deliberately.** The three are not
  interchangeable, and they fail differently:

  | Syntax | Evaluated | Sees | Valid where | When unresolved |
  |---|---|---|---|---|
  | `${{ expr }}` | compile time | parameters, literal variables | key *or* value, in stages/jobs/steps/containers | empty string |
  | `$[ expr ]` | runtime, before the step | runtime variables, no parameters | value only, whole right-hand side | empty string |
  | `$( var )` | runtime, immediately before task execution | runtime variables | value only, in task inputs | left as literal `$(var)` |

- **Declare every checkout fully.** Set `fetchDepth`, `fetchTags`,
  `persistCredentials` and `clean` on each `checkout`, because the defaults vary
  by pipeline and live in settings the YAML cannot see.
- **Pin a shared template repository to a tag.** A `resources.repositories`
  entry should anchor to a tag (or branch) rather than track a rolling default
  branch, so a breaking template change does not reach existing pipelines. Refs
  are resolved once at pipeline start and not re-resolved mid-run. A commit id
  is the fully immutable escape hatch, but the recommended shape is a tag
  pointing at that commit.
- **Publish in its own job.** Re-running a job whose publish step already ran
  fails, because the artifact name is taken and a published artifact cannot be
  changed. Upstream's fix is a separate publish job behind `dependsOn`.
  Suffixing `$(System.JobAttempt)` to the name is a community workaround, not
  upstream guidance.
- **Agent hygiene for self-hosted pools:** one agent per machine; run it as a
  service, not an interactive session; a low-privileged service account;
  separate pools per project or sensitivity tier; and an explicit
  `workspace: clean:` if the job needs a clean tree. Without root, the agent's
  service installer, which writes a system unit, is not available: run the
  listener as a user-level systemd unit and enable lingering for the service
  account (`loginctl enable-linger`), or the pool goes offline at logout and
  after a reboot. Name each pipeline after its entry file when you create it
  from a repository: the default name is the repository's, so run links and
  alerts do not say which pipeline failed.
- **Caching, used correctly, is cheap.** `Cache@2` takes `key`, `restoreKeys`
  and `path`. Key segments that are file paths or patterns are hashed, so a
  lockfile makes an ideal key segment. A cache is immutable once written for a
  key, so supply ordered `restoreKeys` prefixes, or a lockfile change leaves a
  zero-hit cache. Cache scope is already isolated per project, pipeline and
  branch (and per fork pull-request ref), so do not fold those identifiers into
  the key. Caches expire after a period of inactivity, and upstream documents no
  per-cache or per-organization size cap.
- **Cache and artifact are not substitutes.** Use a pipeline artifact for output
  a downstream job cannot regenerate; use a cache only where the job can rebuild
  the files on a miss. Caching something a later stage strictly requires, with
  no regeneration path, fails intermittently.

## General pitfalls
- **Templates expand before variable groups are resolved and authorized.** The
  platform first expands templates and evaluates template expressions, then
  evaluates stage dependencies, and only then gathers and authorizes the
  resources a selected stage needs. Consequences, in order of practical
  importance:
  - `- group: ${{ parameters.x }}` is order-legal: parameters are already
    resolved during expansion, so the group name is a literal by the time
    authorization runs.
  - `- group: $(someRuntimeVar)` cannot work: macro substitution happens
    immediately before task execution, long after authorization.
  - A group's contents are unavailable to anything evaluated at compile time,
    so no template expression can branch on a value inside a variable group.
- **`checkout: repo@$(branch)` fails with "ref not found".** A checkout ref does
  not expand macro syntax. Use `${{ parameters.x }}` or set `ref:` on the
  repository resource.
- **Template expressions in `trigger` and repository resources.** The upstream
  note on `variables:` also says template expressions cannot be used in
  `trigger` or in a repository resource, and other upstream pages conflict with
  it. Confirm with a preview compile before parameterizing
  `resources.repositories.ref`.
- **Variable-group order is semantic: the last reference wins.** Any generator
  that emits or rewrites a `variables:` block must emit a deterministic order,
  or it silently changes which value is used. Do not rely on last-wins as a
  feature, though: upstream says to avoid cross-group name collisions.
- **Secret variables need an explicit per-step `env:` mapping; there is no bulk
  inject.** Secrets are never decrypted into a script's environment on their
  own, and a pipeline-level alias does not help; only a step-level `env:` entry
  mapping the secret to a name does. Changing how the secret is sourced (a
  vault-linked group, federated identity) does not change that it still needs
  the mapping. A vault-linked group maps only the secret names into the group;
  the values stay in the vault and are fetched for the run. Map a secret into an
  environment variable; never pass it as a command-line argument, which some
  operating systems log.
- **Masking is best effort, and it never covers substrings.** The platform masks
  a secret's whole value in the log, but a fragment of it (one field of a JSON
  blob, a line of a certificate, a decoded half of a credential pair) prints in
  clear. So a secret should never hold structured data: store each part as its
  own secret. A masked value is no proof that a value exists, so do not use the
  log to check that a secret is set. Setting a secret from a script with
  `task.setvariable` and `issecret=true` is, in upstream's own words, the least
  secure way to create one; define it in the pipeline settings or a variable
  group instead.
- **An empty string is not a valid value for a `string` parameter.** Queueing
  with `''` is rejected, so "unset" cannot be spelled as empty. Omit the
  parameter and let its default apply, or give it a sentinel default (a single
  space, say) that the template trims before use, and document why the default
  looks odd, because it is load-bearing.
- **A variable group is read when the run is queued.** Observed in practice;
  upstream does not state it. A run already in flight never sees a later edit to
  the group, so a failure right after a fix may be reporting the old state.
  Queue a fresh run before concluding the fix did not work.
- **Non-secret variables auto-inject with a name transform that is also a
  trap.** They arrive in the process environment uppercased, with every `.`
  turned into `_`, so two variables differing only by case or by `.` versus `_`
  collide. Variables whose names begin with a reserved prefix (`endpoint`,
  `input`, `secret`, `path`, `securefile`, case-insensitive) are silently not
  injected at all, secret or not, with no error at definition time.
- **Three similar-looking syntaxes fail three different ways.** An undefined
  macro reference is left in place and prints literally: loud, and it leaks
  garbage into a script or a filename. The identical typo behind `${{ }}` or
  `$[ ]` silently becomes an empty string, with no error and no warning. The
  silent one is the dangerous one.
- **A custom `condition:` replaces the implicit success gate.** Stages and jobs
  default to `succeeded()`; writing any condition removes that default, so a
  branch-name condition without `and(succeeded(), ...)` runs the job even after
  its dependency failed or the run was canceled. `always()` is for work that
  must run after a cancel too.
- **A second `checkout` silently moves the first repository's path.** With one
  non-default checkout, that repository takes the primary source location; with
  several checkouts, each lands in a folder named after the repository (not the
  resource alias) beneath the sources root, so adding a second repository moves
  the first. Steps that hard-coded the original path break, and nothing fails at
  the checkout step. Set `path:` explicitly when more than one repository is in
  play.
- **The run's repository versions are not deployment provenance.**
  Observed in practice: the versions a run records are the refs resolved when it was compiled; a branch
  or commit chosen later at runtime (a script checkout, an orchestrator that
  overrides branches) does not appear there. Write the full commit of each
  repository and the image id of each container into a record the deploying
  job already publishes, read provenance from that record, and treat a missing
  record as provenance not established, never as consistent.
- **The branch of a pipeline-completion trigger.** When the triggering pipeline
  lives in the same repository (or is `self`), the triggered run uses the
  triggering branch and commit. When it lives in another repository, the
  triggered run compiles from its own "default branch for manual and scheduled
  builds". `resources.pipeline.<alias>.sourceBranch` reports the triggering
  run's branch, not the branch whose YAML was compiled.
- **`download:` without `artifact:` fails open.** The first path segment of
  each pattern is taken as the artifact name, and no match is not an error. With
  a named artifact, a missing artifact fails. Assert that the files you need
  exist.
- **A clean compile does not prove `target:` is spelled right.** Measured: the
  compiler rejects unknown `target:` keys and unknown `settableVariables`
  scalars, but a misspelt `commands:` value compiles unchanged.
- **A self-hosted workspace is not cleaned between runs by default**; only the
  staging and test-result directories are. Stale sources and build outputs
  otherwise persist. Since there is no guarantee of landing on the same agent
  twice (unless demands narrow the pool to one), "no clean" is not a reliable
  cache either. A full disk on a self-hosted agent cuts the agent's own
  connection: the run fails with a lost-agent or log-upload error beside a
  low-disk warning, and reads like a build failure. A full no-cache rebuild of
  large images with several builds in parallel is the usual cause (cause and
  fix on [`container/docker.md`](../container/docker.md)).
- **Cross-job and cross-stage variable propagation is not automatic.** A
  variable set by a logging command is job-scoped; exposing it elsewhere needs
  `isOutput=true` and the dependency syntax in Core API.
- **Job timeouts have a default, and hosted agents cap regardless.** An unset
  timeout is not unlimited, and zero or a very high value does not raise a hosted
  agent's ceiling.
- **Interpolating an expression into a `template:` path is a community pattern,
  not a documented one.** Selecting between fixed template names with
  `${{ if }}` / `${{ else }}` is documented and safe; building the path string
  from a parameter is widely used but unconfirmed, so prefer branch selection or
  test it first.
- **Whether template expressions expand inside `variables:` is documented
  inconsistently upstream.** One note restricts expansion to stages, jobs, steps
  and containers; the same page's own examples splice an object into a job-level
  `variables:` mapping and pick a `value:` with a conditional inside a
  list-syntax variables item. Working reading: those two demonstrated shapes
  work; do not generalize past them. Generating a whole `- group:` item with
  `${{ each }}` / `${{ if }}` is neither documented nor prohibited, so settle it
  by compiling a preview run and reading the resulting YAML. A successful
  compile proves only the compile half, not that the group exists or is
  authorized.

## Testing
- **Compile without running.** The Pipelines preview REST operation
  (`library-corpus/platform/azure-devops-rest`) with `previewRun: true`
  compiles the pipeline, optionally from a `yamlOverride`, and returns the
  expanded `finalYaml` without creating a run. It is the test for template
  expansion, `${{ }}` logic and parameter validation. It proves nothing about
  runtime: authorization, variable-group contents and `$[ ]` / `$( )` values
  are only known in a real run.
- Assert on the compiled YAML, not on the source: read `finalYaml` for the
  steps, conditions and `target:` values the template was meant to produce.
- Two questions upstream leaves open, so test them before relying on them:
  whether a retry attempt can download an artifact an earlier attempt
  published, and whether `checkout`, `publish` and `download` succeed at runtime
  under `commands: restricted`.

## Security defaults
- **Fork builds.** Never give secrets to fork builds, and run them on hosted
  agents, not self-hosted ones, so external code does not execute on internal
  machines.
- **Service connections.** Keep scope minimal, restrict each to specific
  branches with a branch-control check, and prefer federated workload identity
  to stored client secrets.
- **Variable groups.** Authorize them per pipeline, not for the whole project.
  Naming a group in YAML with open access means anyone who can push code can
  read its secrets.
- **Key Vault-linked groups.** An RBAC vault works only through its public
  endpoint; private-endpoint vaults are unsupported, because Azure DevOps is not
  a Key Vault trusted service. Recheck this, since the gap could close.
- **Restricted steps.** `target: {commands: restricted}` blocks only some
  logging commands. Upstream names artifact upload and log attachment among
  them. Per the agent source, still allowed are `complete`, `logissue`,
  `setvariable`, `logdetail`, `setprogress`, `setsecret`, `debug`,
  `settaskvariable` and `prependpath`; blocked are `artifact.upload`,
  `artifact.associate`, `uploadsummary`, `uploadfile`, `addattachment` and
  `setendpoint`. That list is implementation detail. Because `setvariable`
  stays allowed, a step that echoes external text can still inject variables:
  pair `restricted` with a `settableVariables` allow-list, or `none`.
- Per the agent source, the agent rewrites `##vso` to `**vso` in git subprocess
  output, so a logging command hidden in a commit subject is inert at checkout.
  This is implementation behaviour, not a documented contract.
- **Checks on protected resources.** A repository, environment, service
  connection, agent pool, secure file or variable group can carry checks.
  - Checks run once per stage: every check on every resource the stage uses
    must pass before the stage starts.
  - The order is fixed: static checks (branch control, required template,
    evaluate artifact), then pre-check approvals, then dynamic checks, then
    post-check approvals, then the exclusive lock.
  - Branch control takes an allow-list of full `refs/heads/...` refs and can
    require the branch to be protected.
  - The required-template check applies only when the pipeline `extends` a
    template. A pipeline that only uses `template:` includes passes the check
    green without being controlled.
- **Job token scope.** When the job authorization scope is not limited, the job
  token reaches the whole collection: every repository in every project.
  "Limit job authorization scope to current project" is a separate toggle for
  release and non-release pipelines.
- **Protect access to repositories in YAML pipelines** adds a layer on top: a
  job reaches only the repositories it references through `checkout:` or
  `uses:`. It is on by default in newer organizations, and a project cannot
  override the organization setting.
- **Limit variables that can be set at queue time** (organization wins over
  project): only variables marked settable can be overridden, and the UI add
  button disappears. A REST or CLI queue that sets an unmarked variable fails
  with a validation error naming it.
- `persistCredentials: true` leaves the job token in the checkout's git
  configuration for later steps (`library-corpus/cli/git`, the `extraheader`
  idiom). Keep the default `false` unless a later step pushes.

## Operational behaviour
- A run moves through compile, authorize and execute. Errors in the first phase
  stop the run before any agent is assigned; checks and approvals hold a stage
  in the second; only the third consumes agent time.
- Refs of repository resources are resolved once at run start.
- A variable group's values are read at queue time (observed in practice; see
  General pitfalls).
- Retries: a retried job or stage runs again with the attempt counter
  increased, and the steps run again, including any publish step.
- **Variable groups:** upstream documents no cap on variables per group, value
  size or groups per pipeline.
- Self-hosted agents keep their workspace between runs (General pitfalls).

## Interop
- **Azure DevOps REST** (`library-corpus/platform/azure-devops-rest`): the
  preview and run operations, the build timeline and logs, and the job token
  sent as `Authorization: Bearer $(System.AccessToken)` from a step that maps it
  in `env:`.
- **azure-cli** (`library-corpus/platform/azure-cli`): `az pipelines run
  --parameters` feeds the `parameters:` block, and `--branch` selects the ref
  whose YAML compiles. A step can run `az devops` commands through `AzureCLI@3`
  or with `AZURE_DEVOPS_EXT_PAT`.
- **git** (`library-corpus/cli/git`): `fetchDepth`, `fetchTags` and
  `persistCredentials` map to a shallow clone, tag fetch, and an
  `http.<url>.extraheader` credential in the checkout's config.
- **Containers** (`library-corpus/container/docker`): `target: {container}`
  and container jobs run steps inside an image the job declares.

## Major lines

### Azure DevOps Services (cloud)
- The surface on this page. The `iif()` expression function exists here.

### Azure DevOps Server (on-premises)
- `iif()` is not available there, and other features on this page may be
  missing too. Check the schema reference with the on-premises version
  selected before using a function or key.

## Upstream docs
- YAML schema reference:
  https://learn.microsoft.com/azure/devops/pipelines/yaml-schema/
- Templates, expressions, conditions, runs:
  https://learn.microsoft.com/azure/devops/pipelines/process/
- Approvals and checks:
  https://learn.microsoft.com/azure/devops/pipelines/process/approvals
- Security guidance for pipelines and templates:
  https://learn.microsoft.com/azure/devops/pipelines/security/
- Secret variables (mapping, masking, vault-linked groups):
  https://learn.microsoft.com/azure/devops/pipelines/process/set-secret-variables
- Agents, caching, multi-repo checkout:
  https://learn.microsoft.com/azure/devops/pipelines/agents/agents
- Self-hosted Linux agents (`svc.sh install` needs sudo):
  https://learn.microsoft.com/azure/devops/pipelines/agents/linux-agent
- Agent source: https://github.com/microsoft/azure-pipelines-agent
