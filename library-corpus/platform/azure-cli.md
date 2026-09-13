# azure-cli — platform

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. This is a **hosted-platform client surface**: the client is
> installed from a package manager, but what is durable here is the *shape of the
> platform it drives*, which has no version to pin — so it is pinned by
> **retrieval date**: last confirmed against the installed client and upstream
> reference documentation **2026-09-11**. Orientation only; re-read a command's
> own `--help` before depending on a flag.

## What it is
`az` (Azure CLI) is the command-line client for a hosted cloud and DevOps
platform. It is a Python program that wraps the platform's REST APIs behind a
uniform command tree, adds an authentication/session model, and renders every
response through a shared output and query layer. Optional **extensions** graft
additional command groups onto the same tree — the DevOps extension, for
instance, adds pipeline, repository, and pull-request commands.

Its durable surface is four things, and none of them is a particular command
line:

1. **The command-group model** — a predictable `az <group> <subgroup> <verb>`
   tree with `--help` at every level.
2. **The authentication and session model** — how identity is established and how
   long it lasts.
3. **The output and query projection** — how a response becomes text a script can
   consume.
4. **The conceptual pitfalls of driving a hosted platform from a shell** — which
   are the same pitfalls for any such client.

## Core API / usage shape
```
az <group> [<subgroup> ...] <verb> [--flags]
az <group> --help                # the authoritative surface, at every level
az extension add|list|update|remove --name <ext>
```
- **Verbs are conventional**: `list`, `show`, `create`, `update`, `delete`,
  `set`, and (for long-running work) a `wait` companion. Learning the convention
  is worth more than memorizing commands.
- **Authentication** comes in several shapes, and which one is in play decides
  everything about reproducibility: an interactive browser or device-code login;
  a non-interactive service principal or federated workload identity; a managed
  identity when running on platform-hosted compute; and, for some extensions, a
  personal access token supplied to a dedicated login command. Session state is
  cached under the user's CLI configuration directory and persists across shells.
  Feed a token on **stdin** or from an environment variable — never as a
  command-line argument, which lands in shell history and process listings.
- **Scope flags.** Organization, project, subscription, and resource-group scope
  can each be passed per command or stored as a configured default.
- **Output and projection**:
  ```
  -o json | table | tsv | yaml | none
  --query "<JMESPath>"        # project/filter server responses client-side
  --only-show-errors          # suppress warnings in scripted use
  --debug / --verbose         # show the underlying REST calls
  ```
  `--query` with `-o tsv` is the composable form for shell pipelines; `-o table`
  is for human eyes; `-o json` piped into a real parser is for anything
  structured.
- **Where the client stops and REST begins.** An extension's command surface is
  typically *thin over the platform REST API*, and new platform capability appears
  in REST first. Anything unexposed is reachable by calling the REST endpoint
  directly with the same credential — for token-based platforms, HTTP basic with
  an empty username (`curl -u ":$TOKEN"`) keeps the secret out of the URL and
  therefore out of shell history and server access logs.

## Idioms & best practices
- **Pass scope explicitly on every command; configure no defaults.** An omitted
  organization, project, or subscription flag should be an *error*, not a silent
  switch to whichever scope was configured last. This is the single highest-value
  habit with this class of tool: a stored default turns a copy-pasted command into
  an action against the wrong environment, and the command looks correct in the
  transcript afterwards.
- **Script against `--query` projections, not against rendered output.** Table
  and default JSON layouts are presentation, not an interface; a projection that
  names the fields it needs survives a response-shape change that positional
  parsing does not.
- **Prefer a scripted command over a web form for anything consequential.** A
  command with a long parameter set is reviewable *before* it is sent and
  reproducible *after*; a dropdown set by hand on a deploy is neither, and a
  mis-set one is expensive. Read runs in the UI, queue them from a shell.
- **Parse structured output with a real parser.** Piping JSON into a language
  runtime is more robust than stringing together text utilities, and it fails
  loudly when the shape changes.
- **Know how the tool encodes key/value parameter lists.** Where a flag takes
  space-separated `name=value` pairs, only the *first* `=` separates, so a value
  may itself contain `=` — useful, and a trap for anyone who quotes defensively
  in the wrong place.
- **Treat an extension's flags as their own surface.** An extension moves
  independently of the core client, so re-read the relevant `--help` after
  updating one, especially where a script depends on flag names.
- **Feed long free-text arguments from a heredoc or a file**, not from an inline
  string — multi-paragraph descriptions and bodies otherwise collide with shell
  quoting.
- **Prove a change before making it, where a dry run exists.** Some platforms
  expose a preview/what-if endpoint that compiles or plans without creating
  anything; it is often reachable only via REST, and it is worth the extra call.

## General pitfalls
- **Flag names describe the client's model, not your mental model.** The most
  expensive traps in this class of tool are flags that read as one thing and mean
  another — a ref flag on a "run" command that selects which ref supplies the
  *pipeline definition* rather than which code is built is the canonical example.
  Read the help text for any flag whose consequence is a deployment, and confirm
  the semantics once, deliberately.
- **"Variables" and "parameters" are different systems** on the same platform:
  one sets the runtime variable namespace, the other supplies the declared inputs
  of the definition. Passing the right values through the wrong flag fails
  quietly, by using the defaults.
- **Listing commands are scoped.** A `list` is scoped to the project,
  subscription, or resource group in effect — something absent from the output is
  frequently present somewhere else, not missing.
- **A mutating command usually returns when the operation is *accepted*, not when
  it is complete.** Queuing a run or starting a deployment returns immediately;
  the outcome needs a follow-up `show` or `wait`, and treating the first response
  as success is how a failed deploy gets reported as a successful one.
- **Not everything has a dry run.** Where the client offers none, either the
  platform's preview REST endpoint is the substitute or there is no substitute —
  in which case a low-stakes rehearsal target is the only honest mitigation.
- **An unauthenticated command usually fails with a message naming the fix** —
  which is convenient, but it also means an expired session is an easy thing to
  paper over with a re-login instead of noticing that a session expired
  mid-procedure, halfway through a multi-step change.
- **The token is a bearer credential with the full rights of the identity behind
  it**, up to and including production deployments. It must never be written into
  a file, a log, a prompt, a commit, or documentation; prefer short-lived or
  federated credentials over long-lived personal tokens wherever the platform
  offers them.
- **A client version is not a platform version.** The client lags the REST API,
  and an extension lags further; a capability missing from the client may exist on
  the platform. Conversely, a command that works on one workstation may not exist
  on another — which is why an operator procedure built on this client belongs in
  a checked-in script or runbook rather than in someone's shell history.
- **It is an operator tool, so it appears in no manifest.** Nothing builds or runs
  against it, so nothing in dependency tooling will tell you it drifted, and no
  test will fail when it does.

## Upstream docs
- Command reference: https://learn.microsoft.com/cli/azure/reference-index
- Install and authentication: https://learn.microsoft.com/cli/azure/
- Output formats and JMESPath queries:
  https://learn.microsoft.com/cli/azure/query-azure-cli
