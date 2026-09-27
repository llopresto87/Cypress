# azure-pipelines-yaml — platform

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. This is a **hosted-platform surface**: there is no installable
> package and no version to pin, so it is pinned by **retrieval date** — the
> surface below was last confirmed against upstream documentation **2026-07-27**
> (the secret-variable and parameter-validation notes **2026-09-13**).
> Orientation only: for a project's own agent pools, service connections,
> variable groups, and governance checks, run `ingest-library` against the
> project itself, and re-confirm anything load-bearing against current upstream
> docs.

## What it is
**Azure Pipelines YAML** is the pipeline-as-code schema of Azure Pipelines, the
hosted CI/CD service in Azure DevOps. A file in the repository describes the
whole run — its triggers, its stages, jobs and steps, which agent pool executes
them, which other repositories are checked out, which variables and secrets are
in scope — and the platform compiles that file into a run.

It is a *surface of a hosted service*, not a library: there is no package, no
release to pin, and no changelog to diff. What is durable about it is the shape:
a **schema**, a **template model** (two distinct kinds of reuse), **three
expression contexts evaluated at three different times**, a **variable and secret
model**, and the **agent behaviors** the whole thing sits on. Those are what a
new pipeline author has to understand before touching a template, and they are
what this page carries.

The mental model that explains most surprises: **a pipeline is compiled, then
authorized, then executed** — three phases, each seeing a different world.

## Core API / usage shape
```
pipeline:  trigger | pr | schedules | resources | variables | parameters
           stages: | jobs: | steps: | extends:
resources.repositories: {repository, type, name, endpoint, ref}   # other repos as template sources / checkouts
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
checkout: self | none | <repo alias>      # with path:, clean:, fetchDepth:
deployment: {environment, strategy: {runOnce | rolling | canary}}
condition: / dependsOn: [...]             # stage- and job-level gating
variables:                                # list syntax combines all three:
  - name: x            value: y           #   literal pairs
  - group: <name>                         #   variable-group reference
  - template: vars.yml[ + parameters:]    #   a variables template (may itself carry groups)
pool: / workspace: {clean: outputs|resources|all}
```
A variables template is **not** values-only: it may contain literal pairs *and*
variable-group references, and it accepts its own `parameters:`. Mapping syntax
and list syntax cannot be mixed in one `variables:` section; anything beyond
literal pairs requires list syntax.

## Idioms & best practices
- **`extends` for governed pipelines, `template:` includes for reusable
  fragments.** An include splices content in with no ceiling on what the consumer
  can add. An `extends` template owns the pipeline's shape and the consumer may
  only supply what its parameters (typically a `stepList`/`jobList`) allow — and
  only `extends` can be paired with a *required-template* approval check that
  makes the governed template mandatory. If a template exists to enforce
  something, it must be an `extends` template; otherwise it is a suggestion.
- **An `extends` template can enforce policy at compile time** by rewriting the
  consumer-supplied step or job list with `${{ each }}` + `${{ if }}`: reject or
  replace arbitrary script-running task types, constrain pool choice to an
  allow-list, force steps into a locked-down container, and restrict which
  variables a task's logging commands may set (an empty settable-variables list
  disallows all of them).
- **Generate maps instead of hand-maintaining them.** A typed `object` parameter
  plus `${{ each }}` / `${{ insert }}` emits an `env:` or `variables:` mapping
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
- **Declare shared variable groups once in a variables template** and consume it
  from each pipeline, so the group list has a single home. Read the compile-order
  pitfall first: per-pipeline authorization of a group does **not** travel with
  the template.
- **Settle it before the run as a parameter; let it vary per run as a
  variable.** Before a pipeline runs, templates and their parameters become
  constants. Anything the platform needs as a constant (a checkout ref, a
  template path, a stage list) must therefore be a parameter, and a variable
  cannot stand in for it. A parameter with a `values:` enumeration restricts the
  choice, for a pool or an environment, to a fixed list.
- **Queue-time parameter validation makes a typo loud; lean on it.** Runtime
  parameters are checked when the run is queued, before anything executes. A
  parameter the pipeline does not declare is rejected, a non-boolean value for a
  `boolean` parameter is rejected (observed: `yes` fails, while `true`, `True`,
  `TRUE`, `false` and `False` pass, and the run records the value back as `True`
  or `False`). A mistyped flag
  is therefore an error at queue time, not a silent no-op. A template that
  compares a boolean against string literals should normalize case first rather
  than trust the recorded spelling.
- **Choose the expression context deliberately** — the three are not
  interchangeable and they fail differently:

  | Syntax | Evaluated | Sees | Valid where | When unresolved |
  |---|---|---|---|---|
  | `${{ expr }}` | compile time | parameters, literal variables | key *or* value, in stages/jobs/steps/containers | empty string |
  | `$[ expr ]` | runtime, before the step | runtime variables, no parameters | value only, whole right-hand side | empty string |
  | `$( var )` | runtime, immediately before task execution | runtime variables | value only, in task inputs | left as literal `$(var)` |

- **Pin a shared template repository to a tag.** A `resources.repositories` entry
  should anchor to a tag (or branch) rather than tracking a rolling default
  branch, so a breaking template change does not reach existing pipelines. Refs
  are resolved **once at pipeline start** and not re-resolved mid-run. A commit
  identifier is the fully immutable escape hatch, but the recommended shape is a
  tag pointing at that commit.
- **Agent hygiene for self-hosted pools:** one agent per machine; run it as a
  service rather than an interactive session; a low-privileged service account;
  separate pools per project or sensitivity tier; and set `workspace: clean:`
  explicitly if the job needs a clean tree.
- **Caching, used correctly, is cheap.** Cache key segments that are file paths or
  patterns are *hashed*, so a lockfile makes an ideal key segment; caches are
  immutable once written for a key, so supply ordered `restoreKeys` prefixes or a
  lockfile change leaves a zero-hit cache. Cache scope is already isolated per
  project, pipeline, and branch — do not fold those identifiers into the key
  yourself. Caches expire after a period of inactivity.
- **Cache and artifact are not substitutes.** Use a pipeline artifact for output a
  downstream job *cannot regenerate*; use a cache only where the job can rebuild
  the files itself on a miss. Caching something a later stage strictly requires,
  with no regeneration path, is a category error that fails intermittently.
- **Security posture that belongs in every pipeline:** never provide secrets to
  fork builds, and run fork builds on hosted rather than self-hosted agents so
  external code does not execute on internal machines; keep service-connection
  scope minimal and restrict connections to specific branches with a
  branch-control check; prefer federated workload identity over stored client
  secrets; authorize variable groups per pipeline rather than opening them to the
  whole project — naming a group in YAML with open access means anyone who can
  push code can exfiltrate its secrets.

## General pitfalls
- **Templates expand *before* variable groups are resolved and authorized.** The
  platform first expands templates and evaluates template expressions, then
  evaluates stage dependencies, and only then gathers and authorizes the
  resources a selected stage needs. Consequences, in order of practical
  importance:
  - `- group: ${{ parameters.x }}` is order-legal — parameters are already
    resolved during expansion, so the group *name* is a literal by the time
    authorization runs.
  - `- group: $(someRuntimeVar)` **cannot work**: macro substitution happens
    immediately before task execution, long after authorization.
  - A group's *contents* are unavailable to anything evaluated at compile time,
    so no template expression can branch on a value that lives inside a variable
    group.
- **Variable-group order is semantic: the last reference wins.** Any generator
  that emits or rewrites a `variables:` block must emit a deterministic order, or
  it silently changes which value is used. Do not *rely* on last-wins as a
  feature, though — deliberate cross-group name collisions are documented as
  something to avoid.
- **Secret variables require explicit per-step `env:` mapping; there is no bulk
  inject.** Secrets are never auto-decrypted into a script's environment, and a
  pipeline-level alias does not help — only a step-level `env:` entry mapping the
  secret to a name does. Changing *how* the secret is sourced (a vault-linked
  group, federated identity) does not change *that* it still needs the mapping.
  A vault-linked group maps only the secret *names* into the group; the values
  stay in the vault and are fetched for the run. Map a secret into an
  environment variable; never pass it as a command-line argument, which some
  operating systems log.
- **Masking is best effort, and it never covers substrings.** The platform masks
  a secret's whole value in the log, but a fragment of it (one field of a JSON
  blob, a line of a certificate, a decoded half of a credential pair) prints in
  clear. So a secret should never hold structured data: store each part as its
  own secret. A masked value is also no proof that a value exists, so do not use
  the log to check that a secret is set. Setting a secret from a script with the
  `task.setvariable` logging command and `issecret=true` is, in upstream's own
  words, the least secure way to create one; prefer defining it in the pipeline
  settings or a variable group.
- **An empty string is not a valid value for a `string` parameter.** Queueing
  with `''` is rejected, so "unset" cannot be spelled as empty. Either omit the
  parameter and let its default apply, or give it a sentinel default (a single
  space, say) that the template trims before use, and document why the default
  looks odd, because it is load-bearing.
- **A variable group is read when the run is queued** (observed behavior; an
  upstream citation is not recorded). A run already in flight never sees a later
  edit to the group, so a failure right after a fix may be reporting the old
  state. Queue a fresh run before concluding the fix did not work.
- **Non-secret variables auto-inject with a name transform that is also a
  footgun.** They arrive in the process environment uppercased with every `.`
  turned into `_`, so two variables differing only by case or by `.` versus `_`
  collide. Variables whose names begin with certain reserved prefixes are
  **silently not injected at all**, whether or not they are secret — no error at
  definition time.
- **Three similar-looking syntaxes fail three different ways.** An undefined
  macro reference is left in place and prints literally — loud, and it leaks
  garbage into a script or a filename. The identical typo behind `${{ }}` or
  `$[ ]` silently becomes an empty string: no error, no warning, nothing that
  looks wrong. The silent one is the dangerous one.
- **A custom `condition:` replaces the implicit success gate, it does not layer
  on top of it.** Stages and jobs default to running only on success; writing any
  condition removes that default, so a branch-name condition without
  `and(succeeded(), …)` runs the job even after its dependency failed or the run
  was canceled.
- **A second `checkout` silently moves the first repository's path.** With one
  non-default checkout, that repository takes the primary source location; with
  multiple checkouts, each lands in a folder named after the *repository* (not the
  resource alias) beneath the sources root — so adding a second repository moves
  the first. Steps that hard-coded the original path break, and nothing fails at
  the checkout step itself. Set `path:` explicitly when more than one repository
  is in play.
- **A self-hosted workspace is not cleaned between runs by default** — only the
  staging and test-result directories are. Stale sources and build outputs
  otherwise persist. And since there is no guarantee of landing on the same agent
  twice (unless demands narrow the pool to one), "no clean" is not a reliable
  cache: the files may persist, or may not, depending on which agent picks the
  job up.
- **Cross-job and cross-stage variable propagation is not automatic.** A variable
  set by a logging command is job-scoped; exposing it elsewhere requires marking
  it as an output variable and reading it explicitly through the job or stage
  dependency object.
- **Job timeouts have a default, and hosted agents hard-cap regardless.** An
  unset timeout is not unlimited, and a job-level setting of zero or a very high
  value does not raise a hosted agent's ceiling.
- **Interpolating an expression into a `template:` *path* is a community pattern,
  not a documented one.** Selecting between fixed template names with
  `${{ if }}` / `${{ else }}` is documented and safe; building the path string
  from a parameter is widely used but unconfirmed — prefer branch selection, or
  test it before relying on it.
- **Whether template expressions expand inside `variables:` is documented
  inconsistently upstream.** One note restricts expansion to stages, jobs, steps
  and containers; the same page's own examples splice an object into a job-level
  `variables:` mapping and pick a `value:` with a conditional inside a list-syntax
  variables item. Working reading: those two demonstrated shapes work; do not
  generalize past them. The specific case of generating a whole `- group:`
  sequence item with `${{ each }}` / `${{ if }}` is neither documented nor
  prohibited — the only evidence is old community writing, so settle it by
  compiling a preview run and reading the resulting YAML rather than by argument.
  Note that a successful compile proves only the *compile* half; it does not
  prove the group exists or is authorized.

## Upstream docs
- YAML schema reference:
  https://learn.microsoft.com/azure/devops/pipelines/yaml-schema/
- Templates, expressions, conditions, runs:
  https://learn.microsoft.com/azure/devops/pipelines/process/
- Security guidance for pipelines and templates:
  https://learn.microsoft.com/azure/devops/pipelines/security/
- Secret variables (mapping, masking, vault-linked groups):
  https://learn.microsoft.com/azure/devops/pipelines/process/set-secret-variables
- Agents, caching, multi-repo checkout:
  https://learn.microsoft.com/azure/devops/pipelines/agents/agents
