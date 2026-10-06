---
name: drive-azure-pipelines-cli
description: Drive Azure Pipelines from a shell with the az devops extension and the REST API, as the Azure DevOps instance of drive-hosted-cicd-cli. Invoke before queueing a consequential run, when a run built something other than intended, when a pipeline YAML has no pipeline object yet, or when a pull request or a variable-group value is set from the terminal.
id: skill.drive-azure-pipelines-cli
tier: 2
kind: skill
title: drive-azure-pipelines-cli, the Azure DevOps commands for each step of drive-hosted-cicd-cli
owns:
  - drive-azure-pipelines-cli.instantiation
  - drive-azure-pipelines-cli.preview-call
  - drive-azure-pipelines-cli.run-provenance
  - drive-azure-pipelines-cli.registration
requires:
load_when:
  - "az pipelines run, queue an azure pipelines run from the terminal"
  - "which yaml did the run compile, which commit did the azure run build"
  - "dry run an azure pipeline, preview the final yaml"
  - "register a yaml file as an azure pipeline"
stack:
  - library-corpus/platform/azure-pipelines-yaml
  - library-corpus/platform/azure-devops-rest
  - library-corpus/platform/azure-cli
est_tokens: 2506
---

# Suggested skill: drive-azure-pipelines-cli

> Optional procedure, **stack-keyed** on Azure DevOps: the Azure Pipelines
> instance of `skill-corpus/drive-hosted-cicd-cli.md`. That page owns the
> procedure and its reasons (one session login, the two-branch trap, parameter
> surfaces, the free dry run, run identity and provenance, registration, the
> publishing boundary); this page restates none of them and gives, for each
> of its sections, the Azure DevOps inputs, commands and observed behaviour.
> The client and API facts live on `library-corpus/platform/azure-cli.md`,
> `library-corpus/platform/azure-devops-rest.md` and
> `library-corpus/platform/azure-pipelines-yaml.md`; this page links them and
> adds only what the procedure needs.

**The template's parameters, filled:**

| template parameter | Azure DevOps value |
|---|---|
| `<CLI>` | `az` with the `azure-devops` extension (`az pipelines`, `az repos`, `az devops`) |
| `<ORG>`/`<PROJECT>` | `--org https://dev.azure.com/<org> --project <project>` on every command, plus `--detect false` where the working directory may be a clone with an Azure DevOps remote |
| `<CREDENTIAL_ENV_VAR>` | a personal access token in an environment variable of the plant's choosing (`<PAT_VAR>` below), or `AZURE_DEVOPS_EXT_PAT` for the process |
| pipeline id table | `az pipelines list --org … --project … -o table`, recorded in the plant's own copy with each id's environment |
| definition-ref input | `--branch` on `az pipelines run`; `resources.repositories.self.refName` in REST |
| per-target override parameters | the YAML `parameters:` of each pipeline, passed with `--parameters name=value …`, and the `ref:` of each repository resource that those parameters feed |
| unmerged-branch recipe | `--branch <branch>` when the pipeline YAML itself is unmerged; the YAML parameter that feeds a repository resource's `ref:`, passed with `--parameters`, when the built repository's branch is unmerged (§2) |
| preview call | `POST …/_apis/pipelines/{pipelineId}/preview` with `previewRun: true` (§4) |

## When to apply

The triggers of `skill-corpus/drive-hosted-cicd-cli.md`, on an Azure DevOps
Services organization. The client supports only the hosted service; an
on-premises server URL fails (`library-corpus/platform/azure-cli.md`).

## 1. One session login

- `printf '%s' "$<PAT_VAR>" | az devops login --organization https://dev.azure.com/<org>`
  reads the token on stdin, so it never appears as an argument. Exporting
  `AZURE_DEVOPS_EXT_PAT` for the process instead needs no login command.
- Without a credential every command fails with the login-required message
  quoted on `library-corpus/platform/azure-cli.md`. Fix the session once; a
  re-login in the middle of a procedure hides an expired token.
- Keep no stored default (`az devops configure --list` shows none), so an
  omitted `--org` or `--project` is an error and not a switch to the last
  scope used.

## 2. The two branches

- **The definition ref is `--branch`.** It sets the ref of the run's `self`
  repository, the one holding the pipeline YAML, so it decides which YAML
  compiles. Its help text ("branch on which the pipeline run is to be
  queued") reads like the built branch; it is not
  (`library-corpus/platform/azure-cli.md`, General pitfalls). Omitted, it is
  the definition's default branch. Observed in practice: when the YAML file
  exists only on a feature branch, the run never starts and the error names
  the file, the repository and the ref ("File <path> not found in repository
  … branch refs/heads/<default>"). Pass `--branch` on every call.
- **The built refs are set by the YAML.** Each `resources.repositories` entry
  has its own `ref:`, usually fed by a template parameter, and a pipeline may
  re-check out other refs in a later script step. `--parameters` sets them;
  `--branch` does not.
- **Read the record for each question separately:**
  `az pipelines runs show --org … --project … --id <run> --query "{sourceBranch:sourceBranch, sourceVersion:sourceVersion, parameters:templateParameters}"`.
  `sourceBranch` and `sourceVersion` are the definition's ref and commit;
  `templateParameters` is what was asked for. Neither shows what was built
  (§5).

## 3. Per-pipeline parameter surfaces

Read each pipeline's YAML `parameters:` block before composing a call: its
names, types, allowed values and defaults. Observed in practice, measured
against the preview call and real runs:

- A parameter the pipeline does not declare is **rejected** at queue time
  ("Unexpected parameter '<name>'"), and a value outside a `boolean`'s
  spellings is rejected ("… is not a valid Boolean"). A typo is loud, not a
  silent no-op.
- A `boolean` accepts `true` and `false` in several capitalizations and is
  recorded back in `templateParameters` as `"True"` or `"False"`. A template
  that compares the value as a string must lowercase it first, or compare
  against both forms.
- An empty string is not a valid value for a `string` parameter; the
  sentinel-default idiom is on `library-corpus/platform/azure-pipelines-yaml.md`
  (General pitfalls).

## 4. The dry run that costs nothing

`az pipelines run` has no dry run. The REST preview operation compiles the
YAML from the requested definition ref, validates every parameter, and
returns the expanded YAML without creating a run
(`library-corpus/platform/azure-devops-rest.md`, Run vs preview). It checks
both branch questions at once: a ref without the YAML fails here as it would
at queue time. Send the credential through curl's stdin configuration, so the
token stays off the command line:

```bash
body='{"previewRun": true,
       "resources": {"repositories": {"self": {"refName": "refs/heads/<definition-branch>"}}},
       "templateParameters": {"<param>": "<value>"}}'
printf 'header = "Authorization: Basic %s"\n' "$(printf ':%s' "$<PAT_VAR>" | base64 | tr -d '\n')" |
  curl -sS -K - -H 'Content-Type: application/json' -X POST \
    "https://dev.azure.com/<org>/<project>/_apis/pipelines/<id>/preview?api-version=<pinned>" \
    -d "$body"
```

- Success returns `{"finalYaml": …}`; a failure returns a validation error
  whose message names the offending parameter or file. Read `finalYaml` for
  the refs the repository resources will check out.
- A `yamlOverride` field compiles an edited YAML that is not pushed yet.
  Observed in practice: an error from an override compile still names the
  registered YAML path, so the path in the message is not proof of which text
  compiled.
- The preview proves the compile half only: authorization, variable-group
  contents and runtime expressions are known only in a real run
  (`library-corpus/platform/azure-pipelines-yaml.md`, Testing).

## 5. Identifying the run, and proving what it built

- Queue and keep the id in one step:
  `run_id=$(az pipelines run --org … --project … --id <id> --branch <definition-branch> --parameters <name>=<value> … --query id -o tsv)`.
  Every later read uses `az pipelines runs show --id "$run_id"`. The command
  returns on queue, with no wait flag.
- **The checkout display is the compile-time ref.** A `checkout` step's name
  (for example "Checkout <repo>@<ref> to <path>") and its log are generated
  from the repository resource's compile-time `ref:`. Observed in practice: a
  per-target override applied later, in a script step that re-checks out the
  repository, is invisible to both, and the checkout log shows a detached
  HEAD at the compile-time ref's tip. The proof is the log of the step that
  performs the real per-target checkout.
- **Reach that log through the timeline.** Get the project id with
  `az devops project show --org … --project <project> --query id -o tsv`, then
  `GET https://dev.azure.com/<org>/<project-id>/_apis/build/builds/<run_id>/timeline?api-version=<pinned>`
  lists records with `name`, `result` and `log.id`, and
  `GET …/_apis/build/builds/<run_id>/logs/<log id>` returns that step's log
  (`startLine`/`endLine` slice a large one). Use the same stdin credential as
  §4.
- After a consequential run, check the target's own state, not only the run
  result (`skill-corpus/drive-hosted-cicd-cli.md` §5).
- A fix that reached the target only through the unmerged-branch recipe
  (the parameter table) is borrowed, not deployed
  (`core/method/release-posture.md`, §1). On Azure DevOps, list the live
  overrides from the `templateParameters` of each pipeline's recent runs (§2,
  "Read the record") before a run that rebuilds the whole topology.

## 6. Registering a pipeline that exists only as YAML

- Create it with an explicit name. Observed in practice: a definition created
  from a repository without a name takes the repository's name, so a
  production pipeline can sit for weeks under a name that says nothing about
  it; `az pipelines update --id <id> --new-name <name>` repairs that.
- Client: `az pipelines create --org … --project … --name <name> --repository <repo> --repository-type tfsgit --branch <branch> --yml-path <path> --skip-first-run true`.
  REST: `POST …/_apis/pipelines` with
  `{"name": …, "folder": "\\", "configuration": {"type": "yaml", "path": "<path>", "repository": {"id": "<repo id>", "type": "azureReposGit"}}}`.
  Observed in practice: that is the shape a created pipeline reads back with;
  the REST reference documents only `configuration.type`, so confirm the
  result with the gate below.
- **Re-derive the repository id from a live listing in the project that owns
  the repository.** `az repos list` is scoped to the project in effect, so a
  repository hosted in another project of the organization is absent from
  this project's list: `az repos list --org … --project <owning project> -o table`.
- **Gate:** `az pipelines show --id <new id>` names the intended path and
  repository, and a §4 preview of the new id compiles. Record the id in the
  plant's id table.

## 7. Pull requests and variable groups from the same client

- `az repos pr create --org … --project … --repository <repo> --source-branch <b> --target-branch <t> --title <title> --description "$(cat <file>)"`.
  Feed a long description from a file or a heredoc as one value:
  each value given to `--description` becomes a separate line. Before creating, check
  for an existing one with `az repos pr list … --source-branch <b> --target-branch <t> --status all`:
  the default status is `active`, which misses an abandoned or completed one.
  Opening a pull request publishes the branch: `core/method/vcs-posture.md`
  owns the authorization, and the plant's attribution setting covers titles
  and descriptions as it covers commits.
- **Write a variable group one variable at a time**, with
  `az pipelines variable-group variable create` or `update --group-id <id> --name <name>`.
  Keep a secret value off the command line (`core/method/secrets-posture.md`):
  for a secret, `create` without `--value` reads it from the environment
  variable `AZURE_DEVOPS_EXT_PIPELINE_VAR_<name>` or prompts on stdin, and
  `update` does the same with `--prompt-value true`.
- **Never round-trip the whole group** (read it, edit, write it back with the
  REST update). A secret variable reads back as `null`
  (`library-corpus/platform/azure-devops-rest.md`, General pitfalls), and the
  REST reference does not say what writing that `null` back does: a
  conservative rule is never to write the whole group, for fear of blanking
  secrets, while
  a report on a vendor-maintained provider's tracker says the service leaves
  the stored secret unchanged. Neither is documented; one variable at a time
  removes the question.
- A group edit reaches only runs queued after it
  (`library-corpus/platform/azure-pipelines-yaml.md`, General pitfalls).

## Reference files

- `skill-corpus/drive-hosted-cicd-cli.md` (the procedure this instantiates)
- `library-corpus/platform/azure-cli.md` (login, scope, `--branch`, listing
  scope)
- `library-corpus/platform/azure-devops-rest.md` (run versus preview,
  timeline and logs, refs and pull requests, credentials)
- `library-corpus/platform/azure-pipelines-yaml.md` (parameters, variable
  groups, compile-only testing)
- `tool-corpus/ops/chained-pipeline-run-driver.md` (driving a chain of runs
  by run id)
- `core/method/secrets-posture.md`, `core/method/vcs-posture.md`,
  `core/method/release-posture.md`
