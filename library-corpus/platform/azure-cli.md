# azure-cli — platform

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). This is a **hosted-platform client surface**:
> the client is installed from a package manager, but what is durable here is
> the shape of the platform it drives, which has no version to pin. It is pinned
> by **retrieval date** instead: last confirmed against the upstream reference
> documentation and the DevOps extension's source **2026-10-05**. Re-read a
> command's own `--help` before depending on a flag.

## What it is
`az` (Azure CLI) is the command-line client for Microsoft's cloud and for Azure
DevOps. It is a Python program, installed from a package manager or installer,
that runs on Windows, Linux and macOS, in a container, or in a cloud shell. It
wraps the platform's REST APIs in one command tree, adds a sign-in and session
model, and renders every response through a shared output and query layer.

**Extensions** are Python wheels that add command groups to the same tree and
update apart from the core client. The `azure-devops` extension adds the groups
`devops`, `pipelines`, `boards`, `repos` and `artifacts`. Its upstream home is
the `Azure/azure-devops-cli-extension` repository (MIT licence). It replaced the
older VSTS CLI. It works only with Azure DevOps Services, the cloud offering:
the source refuses an on-premises Azure DevOps Server URL. The extension is a
thin layer over the Azure DevOps REST API (`library-corpus/platform/azure-devops-rest`),
and `az devops invoke` reaches any REST area directly.

The durable surface is four things, and none of them is a particular command:
the command-group model, the sign-in and session model, the output and query
projection, and the pitfalls of driving a hosted platform from a shell.

## Install, setup and configuration
- Install the core client with the platform installer (WinGet or MSI on
  Windows, the distribution package on Linux, Homebrew on macOS, or the Docker
  image). `az version` prints the client and extension versions.
- `az extension add --name azure-devops` installs the extension;
  `az extension update --name azure-devops` updates it; `az extension list` or
  `az extension show --name azure-devops` confirms it. Extension files live
  under `$AZURE_EXTENSION_DIR`, by default `~/.azure/cliextensions`.
- **Dynamic install.** When a script runs a command from a missing extension,
  the client can install the extension on the spot. This is on by default.
  `az config set extension.use_dynamic_install=yes_prompt|yes_without_prompt|no`
  controls it, and `extension.run_after_dynamic_install=no` stops the rerun
  after the install. `extension.index_url` points the client at a private
  extension index.
- Extensions cannot depend on each other. An extension may replace a core
  command, and the client warns before running a replaced command.
- **Configuration precedence**, highest first: command-line parameters, then
  environment variables, then the config file written by `az config` or
  `az init`. Once an argument has a stored default, it is no longer required.
- The config file is `$AZURE_CONFIG_DIR/config` (INI; default directory
  `~/.azure`). Section names are case-sensitive and key names are not; `#` and
  `;` start a comment, and inline comments are not allowed. Booleans accept
  `1/yes/true/on` and `0/no/false/off`. Every file option has an environment
  variable `AZURE_<SECTION>_<NAME>`, for example `AZURE_CORE_OUTPUT`.
- Core keys that change behaviour: `core.output` (default `json`),
  `core.only_show_errors` (only errors on stderr; hides preview, deprecated and
  experimental warnings), `core.disable_confirm_prompt`,
  `core.collect_telemetry`, and the `defaults.*` keys (`defaults.group`,
  `defaults.location` and a few per-service ones).
- Cloud subscription scope: after sign-in, commands run against the default
  subscription. `az account set --subscription <id-or-name>` changes it, and the
  global `--subscription` flag overrides it for one command.
- **DevOps extension defaults.** `az devops configure --defaults
  organization=<url> project=<name>` stores defaults, `--defaults project=''`
  clears one, and `--list` shows them. `--use-git-aliases true` adds git
  aliases such as `git pr list`. The extension keeps its own config file in
  `azuredevops/config` under the core config directory;
  `AZURE_DEVOPS_EXT_CONFIG_DIR` moves it, and its environment variables use the
  prefix `AZURE_DEVOPS_EXT_` (source-read; the Learn pages do not state this).
- **Scope detection.** `--detect` is on by default. When the organization flag
  is omitted, the extension first reads the organization, project and repository
  from the current git repository's Azure DevOps remote, then falls back to the
  stored default. A missing project is taken from the remote only when the
  organization also came from it. If scope is still unresolved, the command
  stops with an error naming the missing argument. An explicit organization
  flag skips detection.
- `az devops configure` and `az devops --help` need no sign-in and do not
  contact the service.

## Core API / usage shape
```
az <group> [<subgroup> ...] <verb> [--flags]
az <group> --help                       # the authoritative surface, at every level
-o json|jsonc|yaml|yamlc|table|tsv|none # global on every command
--query "<JMESPath>"  --subscription  --only-show-errors  --debug  --verbose
```
- **Verbs are conventional**: `list`, `show`, `create`, `update`, `delete`,
  `set`, and for long-running work a `wait` companion.
- **Sign-in, core client.** Four shapes: cloud shell (automatic); interactive
  `az login` (browser, or device code with `--use-device-code` or when no
  browser exists); a service principal (`az login --service-principal
  --username <app-id> --password <secret> --tenant <tenant>`, or
  `--certificate <pem>` with the certificate appended to the private key in one
  file; write `--password=<secret>` when the secret starts with `-`); and a
  managed identity (`az login --identity`, plus `--client-id`, `--object-id` or
  `--resource-id` for a user-assigned one). Upstream recommends a service
  principal for scripts. `az account get-access-token` returns an access token.
- **Sign-in, DevOps extension.** Two shapes: the Entra session from `az login`,
  or a personal access token (PAT). A PAT is supplied by `az devops login`
  (prompt, or piped on stdin in a non-interactive shell), or by setting
  `AZURE_DEVOPS_EXT_PAT` for the process, in which case no login command is
  needed. `az devops logout` clears one organization's credential, or all. The
  extension does not accept a service principal or managed identity directly.
  In source the lookup order is: `az login` tokens, then
  `AZURE_DEVOPS_EXT_PAT`, then the stored `az devops login` credential. With
  none, the command fails with a message beginning "Before you can run Azure
  DevOps commands, you need to run the login command" that names both login
  commands.
- An Entra token for Azure DevOps REST comes from `az account get-access-token
  --resource 499b84ac-1321-427f-aa17-267ca6975798 --query accessToken -o tsv`.
  Entra tokens last one hour.
- **Identifiers for raw REST calls.** `az devops project show --project <name>`
  returns the project id, and `az repos list` returns the repositories (their
  fields are on [azure-devops-rest](azure-devops-rest.md), under Identifiers).
  Together they are the cheap lookup for the ids a REST call needs. `repos list` is scoped to the
  project in effect.
- **Pipelines.** `az pipelines create|list|show|update|delete|run`, with the
  groups `runs`, `runs artifact`, `runs tag`, `build`, `variable`,
  `variable-group`, plus folder, agent, pool, queue and release commands.
  `az pipelines create` makes a YAML pipeline from a repository, branch and YAML
  path (`--skip-first-run` skips the first run).
- `az pipelines run --id <id> | --name <name>` (the name is ignored when an id
  is given) takes `--branch`, `--commit-id`, `--folder-path`, `--parameters`,
  `--variables` and `--open`. `--parameters` and `--variables` each take
  space-separated `name=value` pairs.
- What `run` sends, per the extension source: with `--parameters`, it calls the
  Pipelines run API, setting the `self` repository's `refName` from `--branch`
  and `version` from `--commit-id`, `templateParameters` from `--parameters` and
  `variables` from `--variables`. Without `--parameters`, it queues a classic
  build instead, with the branch normalized to `refs/heads/...` and
  `--variables` sent as build parameters.
- `az pipelines runs list` filters on `--pipeline-ids`, `--branch`,
  `--status`, `--result`, `--reason`, `--tags`, `--requested-for`,
  `--query-order` and `--top`; `az pipelines runs show --id <run>` reads one
  run.
- The older `az pipelines build` family (`list`, `queue`, `show`, `cancel`,
  `definition`, `tag`) stays beside `az pipelines runs` in the same extension,
  and both read builds through the same client. They are two views of the same
  runs.
- **Pull requests.** `az repos pr create` takes `--source-branch`,
  `--target-branch`, `--title`, `--description`, `--repository`, reviewer flags
  (`--reviewers`, `--required-reviewers`), `--auto-complete` (default false),
  `--delete-source-branch`, `--squash`, `--merge-commit-message`, `--draft`,
  `--labels`, `--work-items` and the policy-bypass flags. `list`, `show`,
  `update`, `set-vote`, `reviewer`, `work-item` and `policy` complete the
  family.
- **Raw REST.** `az devops invoke --area <a> --resource <r> --route-parameters
  k=v --query-parameters k=v --http-method <verb> --api-version <v>
  [--in-file <f>]` calls any resource with the session's credential. Its default
  api-version is 5.0 and its response shape is not fixed, so use JSON output.
  The credential shapes of a direct HTTPS call are on
  [azure-devops-rest](azure-devops-rest.md), under Credentials.

## Idioms & best practices
- **Pass scope explicitly in scripts.** Give `--org` and `--project` (or
  `--subscription`) on every consequential command, and add `--detect false`
  where the working directory may be a clone with an Azure DevOps remote. Upstream
  documents stored defaults and remote detection as features. Observed in
  practice: a script that relies on either can act against whichever scope was
  configured last or whichever clone it ran in, and the transcript looks correct
  afterwards. An omitted flag is a reliable error only when no default is stored
  and detection is off.
- **Script against `--query` projections, not rendered output.** The query runs
  on the JSON result before formatting. `--query ... -o tsv` feeds one value to
  the next command; `-o json` into a real parser handles anything structured.
  Table and default JSON layouts are presentation. A projection that names its
  fields survives a response-shape change that positional parsing does not.
- **Feed secrets on stdin or through an environment variable**, never as an
  argument, which lands in shell history and process listings. Upstream shows
  `az devops login` reading a PAT on stdin and `read -s` for an interactive
  service principal secret.
- **Pick one of `pipelines runs` and `pipelines build` per script.** They read
  the same runs. Observed in practice: mixing the two in one script makes field
  names and filters disagree for no gain.
- **Use the pipelines preview operation as the dry run.** The client's `run`
  has no preview flag. The request body and the response are on
  [azure-devops-rest](azure-devops-rest.md), under "Run vs preview".
- **Read a run's step logs through REST**, with the timeline and log routes on
  [azure-devops-rest](azure-devops-rest.md).
- **Turn dynamic install off on build machines**
  (`extension.use_dynamic_install=no`) and install the extension explicitly,
  so a missing extension fails the job instead of installing whatever is current.
- **Treat an extension's flags as their own surface.** Re-read the relevant
  `--help` after updating one.
- **Feed long free-text arguments from a file or heredoc**, not an inline
  string: multi-paragraph descriptions otherwise collide with shell quoting.
- **Prefer a scripted command to a web form for anything consequential.** A
  command is reviewable before it is sent and reproducible after.

## General pitfalls
- **Read the help of any flag whose consequence is a deployment**, and confirm
  its meaning once. The `--branch` flag below shows why.
- **`--branch` on `az pipelines run` selects the definition, not just the
  code.** Per the source it sets the ref of the run's `self` repository, the one
  that holds the pipeline YAML, so it decides which YAML compiles. The help text
  ("branch on which the pipeline run is to be queued") does not say this. Code
  from other repository resources is set by the YAML, not by this flag.
- **"Variables" and "parameters" are different systems.** `--variables` feeds
  the runtime variable namespace and `--parameters` the declared template
  parameters. Without `--parameters` the extension takes the classic build
  route. Upstream does not document what happens when a value goes through the
  wrong flag. Observed in practice, on YAML pipelines with a declared
  `parameters:` block: an undeclared key in `--parameters` is rejected loudly
  with a validation error. A declared parameter passed through `--variables`
  was not seen to fail loudly, so the older claim that the wrong flag "fails
  quietly, by using the defaults" may hold for that direction; it is not
  confirmed upstream.
- **`name=value` parsing.** A pair is split at the first `=` only, so a value
  may contain `=`; a pair with no `=` is an error.
- **A mutating command returns when the work is accepted, not complete.**
  `run` returns the queued run, and no wait flag exists; read the outcome with
  `runs show`. Treating the first response as success is how a failed deploy
  gets reported as a good one.
- **Not everything has a dry run.** Where neither the client nor REST offers a
  preview, a low-stakes rehearsal target is the only honest mitigation.
- **Listing is scoped.** A `list` covers the project, subscription or resource
  group in effect; something absent is often elsewhere, not missing.
- **`az devops invoke` defaults to api-version 5.0**, older than the current
  REST docs. Set `--api-version` for newer resources.
- **JMESPath quoting.** Query strings are case-sensitive. Use single quotes or
  backticks for string literals; double quotes inside a filter predicate give
  empty output. Quoting rules belong to the shell, and syntax copied between
  shells often breaks; most upstream examples are tested in Bash.
- **`tsv` and `table` drop nested objects.** Project the field you need first.
- `runs list --query-order` accepts only its listed values; an unknown value
  logs a warning and the list comes back unordered.
- **An unauthenticated command fails with a message naming the fix.** That makes
  an expired session easy to paper over with a re-login mid-procedure instead of
  noticing it.
- **Only Azure DevOps Services is supported.** An on-premises server URL fails.
- **A client version is not a platform version.** Observed in practice: new
  platform capability reaches REST before the client, and the extension lags
  further; upstream states no cadence. A command on one workstation may be
  missing on another, so an operator procedure belongs in a checked-in script.
- **It is an operator tool, so it appears in no manifest.** Observed in
  practice: no dependency tooling reports its drift and no test fails when it
  moves.

## Testing
- Upstream documents no test harness for scripts that drive the client. What
  it offers: `--debug` and `--verbose` print the underlying REST calls; the
  pipelines preview resource checks a definition and its parameters with no side
  effect; `az devops configure --list`, `az version` and `az extension list`
  show local state without contacting the service.
- A script's scope handling can be tested offline: run it with no stored
  defaults, `--detect false` and no credential, and assert that it stops on the
  missing-argument or login error instead of acting. This procedure is derived
  from the extension source's resolution order; it is not an upstream procedure.

## Security defaults
- The token is a bearer credential with the full rights of the identity behind
  it. It never goes into a file, log, prompt, commit or document.
- Upstream prefers Entra tokens to PATs and calls a PAT the higher-risk
  credential. In a pipeline, upstream prefers a service connection with workload
  identity federation and the `AzureCLI@3` task with
  `connectionType: azureDevOps`; mapping `System.AccessToken` into
  `AZURE_DEVOPS_EXT_PAT` in each step's `env` also works.
- Multi-factor authentication is required for user identities on command-line
  tools. It does not affect service principals or managed identities, so
  scripted user-name and password sign-in must move to a workload identity.
- Command output can carry secrets into CI logs. Use `-o none` or capture the
  output in a variable.
- `core.collect_telemetry` controls anonymous usage data.
- Security reports for the extension go through its repository's security
  policy. No dependency-advisory feed covers an operator client; check the
  client release notes at adoption.

## Operational behaviour
- Session state and the user sign-in refresh token are cached under the config
  directory (`~/.azure` by default) and persist across shells. The extension
  stores the `az devops login` credential itself; the Learn pages do not record
  where.
- `az account get-access-token` returns `expires_on` (POSIX, UTC) beside
  `expiresOn` (local time). Use `expires_on`.
- Azure DevOps rate limits apply to the client's calls as to any REST call
  (`azure-devops-rest`).
- Upstream names the error classes a script meets: unrecognized argument,
  missing required argument, mutually exclusive arguments, invalid value (often
  quoting or spacing), HTTP 400, resource not found, and authentication.

## Interop
- **Azure DevOps REST** (`library-corpus/platform/azure-devops-rest`): the
  extension sits on it, `az devops invoke` reaches the rest, and the Entra token
  from `az account get-access-token --resource 499b84ac-...` works there.
- **Azure Pipelines YAML** (`library-corpus/platform/azure-pipelines-yaml`):
  `--parameters` is the YAML `parameters:` block (`templateParameters` in REST).
  A pipeline step can run `az devops` commands with `AZURE_DEVOPS_EXT_PAT` or
  through `AzureCLI@3`.
- **git** (`library-corpus/cli/git`): `--detect` reads git remotes, and
  `--use-git-aliases` adds `git pr ...` aliases.
- `az account` subscription commands belong to the cloud side and do not scope
  Azure DevOps organizations.

## Major lines

### Core client 2.x line
- The current line. Dynamic extension install, private extension indexes, the
  `expires_on` token field, and a subscription selector at interactive sign-in
  (with the Web Account Manager on Windows) all arrived within 2.x. Check
  `az version` before relying on any of them on an old build agent.

### azure-devops extension 1.x line
- The current line; it requires a 2.x core client new enough for it, and older
  0.x releases ran on much older cores. It moves slowly. `az pipelines runs` and
  `az pipelines build` coexist in it. No 2.x extension line existed at retrieval.

### Azure DevOps Server (on-premises)
- A different line that the extension does not support. Drive it with its own
  REST API.

## Upstream docs
- Command reference: https://learn.microsoft.com/cli/azure/reference-index
- Install, sign-in and configuration: https://learn.microsoft.com/cli/azure/
- Output formats and JMESPath queries:
  https://learn.microsoft.com/cli/azure/query-azure-cli
- Azure DevOps CLI: https://learn.microsoft.com/azure/devops/cli/
- Extension source: https://github.com/Azure/azure-devops-cli-extension
