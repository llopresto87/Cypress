# azure-devops-rest — platform

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). This is a **hosted-platform surface**: there is
> no package to install. The REST API is versioned by an `api-version` query
> parameter on every request, and this page is pinned by **retrieval date**
> instead: the surface below was confirmed against the upstream reference (the
> 7.1 pages) on **2026-10-05**. The items marked observed in practice come from
> a plant's earlier live read-only calls. Which `api-version` a project sends is
> the project's pin, recorded by `ingest-library` in its own wiki page.
> Re-confirm anything load-bearing against current upstream docs.

## What it is
The **Azure DevOps Services REST API** is the HTTP surface behind every Azure
DevOps client: the web UI, the `az devops` extension (see
[azure-cli](azure-cli.md): its "Raw REST" bullet and its "A client version is
not a platform version" pitfall are the reasons to come here) and the pipeline
tasks. Every resource
the platform has (projects, Git repositories, refs, pull requests, pipelines and
their runs, builds, timelines and logs, variable groups) is reachable as JSON
under an organization URL, with the same credential the CLI uses. The reference
lives on Microsoft Learn, with a version selector on each page.

A caller that talks to it directly, from a script or a pipeline step with a
plain HTTP client, owns three things the CLI would otherwise hide: the
authentication scheme, the redirect behavior, and the paging and throttling
contract. Those three are where direct callers go wrong.

## Install, setup and configuration
- Nothing installs. A caller needs an organization URL
  (`https://dev.azure.com/{organization}`), a credential, and an `api-version`.
- **`api-version` belongs on every request** (upstream: "should include an
  api-version to avoid having your app or service break"), in the form
  `{major}.{minor}[-{stage}[.{resource-version}]]`, for example `7.1` or
  `7.2-preview.1`. Several versions of the same operation are served side by
  side, and field shapes differ between them.
- **Credentials.** Outside a pipeline: a personal access token (PAT) in HTTP
  Basic with an empty user name (`curl -u ":$TOKEN"`), or an Entra access token
  as `Authorization: Bearer` (how to get one, and its one-hour life:
  [azure-cli](azure-cli.md), Core API section). Upstream prefers
  Entra tokens to PATs. Inside a pipeline job: the job token as
  `Authorization: Bearer $SYSTEM_ACCESSTOKEN`.
- The job token reaches a script only when the step maps it explicitly:
  `env: SYSTEM_ACCESSTOKEN: $(System.AccessToken)`. In a classic pipeline the
  equivalent is the "Allow scripts to access the OAuth token" option.
- Identifiers: the project resource returns the project `id`; the repository
  list returns each repository's `id`, `name` and `defaultBranch` (a full
  `refs/heads/...` name). Either a name or an id works in most routes.

## Core API / usage shape
```
https://dev.azure.com/{organization}/{project}/_apis/<area>/<resource>?api-version=<pinned>

GET  .../_apis/git/repositories                             # id, name, defaultBranch
GET  .../_apis/git/repositories/{repo}/refs?filter=heads/<prefix>
        [&filterContains=<substring>][&peelTags=true][&$top=<n>][&continuationToken=<t>]
     -> { "count": <int>, "value": [GitRef { name, objectId, peeledObjectId? }] }
GET  .../_apis/git/repositories/{repo}/pullrequests
        ?searchCriteria.sourceRefName=refs/heads/<branch>
        &searchCriteria.targetRefName=refs/heads/<branch>
        &searchCriteria.status=active|abandoned|completed|all
        [&$top=<n>&$skip=<n>]
     -> { "count": <int>, "value": [GitPullRequest, ...] }
POST .../_apis/git/repositories/{repo}/pullrequests
     body: { sourceRefName, targetRefName, title, description }
     -> GitPullRequest { pullRequestId: <int>, ... }      # 200 or 201
PATCH .../_apis/git/repositories/{repo}/pullrequests/{id}  # update
PUT  .../pullrequests/{id}/reviewers/{reviewerId}          # body { vote }
GET  .../_apis/distributedtask/variablegroups              # variable groups
POST .../_apis/pipelines/{pipelineId}/runs                 # queue a run -> { id, state, result, ... }
     body: { resources: { repositories: { self: { refName, version } } },
             templateParameters, variables, previewRun, yamlOverride }
POST .../_apis/pipelines/{pipelineId}/preview              # compile only -> { finalYaml }
GET  .../_apis/pipelines/{pipelineId}/runs/{runId}          # poll that run by its id
GET  .../_apis/build/builds/{buildId}/timeline              # records, each with a log id
GET  .../_apis/build/builds/{buildId}/logs/{logId}[?startLine=&endLine=]
```
- List responses share one envelope, `{count, value}`. `count` is the length of
  `value` in this response (one page), not a total.
- **Refs `filter` is a prefix match.** Upstream says the filter returns refs
  that "start with" it, so `filter=heads/x` also returns `heads/x-y`.
  `filterContains` is the separate substring parameter. `$top` cannot exceed
  1000 and defaults to 100 when only a `continuationToken` is given; further
  pages come through the continuation token. `peeledObjectId` is filled only
  for annotated tags and only with `peelTags=true`. Observed in practice: for a
  branch, `objectId` is the tip commit, equal to `git rev-parse` on the same
  ref; the docs show the field without defining it.
- **Pull-request list.** `searchCriteria.status` defaults to `active` when
  unset; `all` includes every state. `$top` and `$skip` exist, with no
  documented default, maximum or continuation token. Descriptions in the list
  are cut at 400 "symbols".
- **Pull-request update** accepts a description up to 4000 characters. A
  property outside the documented set is either rejected with
  `InvalidArgumentValueException` or silently ignored.
- **Reviewer vote scale:** 10 approved, 5 approved with suggestions, 0 no vote,
  -5 waiting for author, -10 rejected.
- **Run vs preview.** The run body sets the `self` repository's ref and commit,
  `templateParameters` for the YAML `parameters:` block and `variables` for
  runtime variables. The preview operation takes the same body with
  `previewRun: true`, compiles the YAML (or a `yamlOverride` of it), returns
  `finalYaml`, and creates no run.

## Idioms & best practices
- **Pin `api-version` in one constant and send it on every call.** The version
  in the code is the version the project depends on, and it belongs in the
  project's wiki page.
- **Match refs exactly on the client.** Because `filter` is a prefix, look a
  branch up with `filter=heads/<branch>` and then keep only the entry whose
  `name` equals `refs/heads/<branch>`.
- **Refuse redirects in the HTTP client, always.** This platform answers a bad
  Bearer token with a cross-host redirect (the first pitfall). The discipline
  itself, and the test that the credential is never re-sent, are owned by
  `tool-corpus/ops/declared-variable-existence-auditor.md` ("Hard refusal to
  follow redirects", §3, with its test in §6). Why a mocked transport cannot
  test the refusal is on `library-corpus/language/python.md` (the `urlopen`
  pitfall).
- **Treat any non-JSON or 3xx answer as an authentication failure.** Check the
  status and the `Content-Type` before parsing. An HTML body is the sign-in
  page, never an empty result, and must never be read as "no pull requests" or
  "no such group".
- **Test the media type by prefix.** Observed in practice on the Git resources:
  the JSON `Content-Type` carries extra parameters, such as
  `application/json; charset=utf-8; api-version=7.1`. Compare the
  `application/json` prefix, never the whole string. Upstream documents only the
  query-string form of `api-version`.
- **Use full ref names in search criteria.** Upstream's own examples pass
  `refs/heads/<branch>`, and every ref in every response is in that form.
  Whether a bare branch name is accepted is not recorded.
- **Send `searchCriteria.status` explicitly.** A duplicate check that relies
  on the `active` default misses an abandoned or completed pull request from the
  same branch.
- **Create with the minimal body and nothing that acts on its own.** Automation
  that opens a pull request sends source, target, title and description only.
  The fields `completionOptions` (auto-complete, merge strategy, policy bypass),
  `autoCompleteSetBy` and `reviewers` (an entry can carry a vote) all exist and
  act. Observed in practice as a rule for a publisher that only proposes: send
  none of them, and let a human merge.
- **Poll the run the queue call returned, and never re-send a `POST` blind.**
  Queueing a run answers with its `id`. The identity rule is
  `core/method/bounded-execution.md` (`toolcraft.bounded-execution`, clause 4),
  and `skill-corpus/drive-hosted-cicd-cli.md` §5 shows where it bites on a hosted
  pipeline. A `GET` may be retried within a bound, but the `POST`s that queue a
  run or create a pull request are not idempotent. After a lost response, read
  first, because the object may already exist.
- **Preview before you queue.** The preview operation is the only no-side-effect
  check of a pipeline definition and its parameters.
- **Walk a failed run's logs**: read the timeline, pick the failed record's log
  id, fetch that log, and slice it with `startLine`/`endLine` when it is large.
- **List variable groups unfiltered, then look up what seems missing.** A
  server-side name filter lets the server decide what the audit examines. Read
  the whole scope, compare locally, and do a targeted lookup for each name that
  appears absent.

## General pitfalls
- **A bad Bearer token gets a redirect to a sign-in page, not a 401.** Observed
  in practice on one organization, on read calls: an invalid `Basic` personal
  token got `401` with an empty body, but an invalid `Bearer` token, or no
  `Authorization` header at all, got a `302` with an HTML body and a `Location`
  on a *different host* (the sign-in service). That redirect also carried
  `WWW-Authenticate: Bearer authorization_uri=...` and `Basic realm=...`
  headers, so the failure can be detected from headers without parsing HTML.
  Upstream documents no failed-call response. A client that follows redirects by
  default will send the Bearer header to that other host (some standard-library
  clients copy every request header onto the redirected request) and then hand
  the caller an HTML page where JSON was expected. An expired or wrong pipeline
  job token takes exactly this path.
- **A refs `filter` is not a lookup.** Read as an exact match, a prefix filter
  silently returns a sibling branch whose name starts the same way.
- **Variable-group responses carry non-secret values in plaintext.** Observed
  in practice, reading groups through the variable-group REST list: a secret
  variable's value comes back as `null`, but every non-secret value is in the
  response body. A tool meant to report names only must split the response at
  the boundary and never print or log the raw body.
- **A group that exists is not a group the pipeline may use.** Existence and
  authorization are separate grants. Observed in practice: a populated group
  that no pipeline linked delivered its keys empty, not as an error, because
  every step downstream accepted blank values. Upstream does not state this
  empty-value behaviour. A present name in the REST listing proves nothing about
  delivery.
- **Pull-request paging is under-documented; assume one page.** Until a project
  has measured it, treat a listing as one page and bound any loop that walks
  `$skip`.
- **The list truncates descriptions; that is not the storage limit.** The list
  cut (400) says nothing about create or update. Upstream gives 4000 only on
  update; whether create enforces the same ceiling, or truncates rather than
  rejects, is not recorded.
- **Create may answer `200` or `201`.** The create operation's response table
  says one and its own worked example returns the other. Accept both.
- **Update can ignore a field silently.** Read the pull request back after an
  update that matters.
- **Throttling starts before `429`** (see Operational behaviour). A client that
  reads only the status code will not notice it is being slowed.

## Testing
- Upstream offers no sandbox organization or mock server. The preview
  operation is the one documented no-side-effect call for pipelines; read-only
  `GET`s are safe against a real organization.
- Observed in practice: a mocked HTTP transport cannot prove redirect refusal,
  because the redirect handling lives in the real client stack. A loopback
  server pair, one answering `302` to the other, shows whether the credential is
  re-sent. Probe failed-auth behaviour live with a bad Basic token, a bad Bearer
  token and no header, with redirects refused, and record status,
  `Content-Type`, `Location` and `WWW-Authenticate`.

## Security defaults
- Every credential is a bearer credential with the rights of the identity
  behind it. Upstream calls the PAT the higher-risk credential and prefers Entra
  tokens; scope a PAT to the least it needs and give it a short life.
- The job token is not in a script's environment unless the step maps it, so a
  step that needs no API access should not get it. Its reach is set by the
  pipeline's job authorization scope (`library-corpus/platform/azure-pipelines-yaml`,
  governance section).
- A token belongs in a header, never in a URL, a log or a command argument.
- Follow no redirects with a credential attached (General pitfalls).

## Operational behaviour
- **Rate limits.** The budget unit is the throughput unit (TSTU). The global
  limit is 200 TSTU in any sliding five-minute window, and each pipeline has its
  own 200. Over budget, the service first delays requests and answers with a
  normal success status plus `Retry-After` (seconds) and
  `X-RateLimit-{Resource,Delay,Limit,Remaining,Reset,Cost}` headers. `Reset` is
  Unix epoch seconds; `Resource` is for display only and may change without
  notice. A blocked call gets `429` with a message starting `TF400733`. Honor
  `Retry-After` whenever it is present.
- Queue and create calls return when the object is accepted; a run's `state`
  and `result` are later states of that object.
- Responses are paged per resource: refs by continuation token, pull requests
  by `$top`/`$skip`.

## Interop
- **azure-cli** (`library-corpus/platform/azure-cli`): the DevOps extension
  is a thin layer over this API, and `az devops invoke` calls any resource here
  with the CLI's session. Its default api-version (5.0) is older than the
  current reference.
- **Azure Pipelines YAML** (`library-corpus/platform/azure-pipelines-yaml`):
  `templateParameters` is the YAML `parameters:` block; `finalYaml` is the
  compiled template expansion.
- **git** (`library-corpus/cli/git`): ref names and object ids match what
  `git` reports for the same repository.

## Major lines

### api-version 7.x
- 7.x is the current line. Several 7.x minors and older majors (6.x, 5.x) are
  served side by side for the same operations. A caller pins one, and fields
  can differ between them. The surface on this page is the 7.1 reference.

### Azure DevOps Server (on-premises)
- Not covered on this page. Upstream's versioning page has a table that maps
  each on-premises server release to the REST api-version it serves; read it
  there before calling a server.

## Upstream docs
- REST API reference (all areas, version selector per page):
  https://learn.microsoft.com/rest/api/azure/devops/
- Pull requests (list, create, update):
  https://learn.microsoft.com/rest/api/azure/devops/git/pull-requests
- Refs: https://learn.microsoft.com/rest/api/azure/devops/git/refs
- Pipelines runs and preview: https://learn.microsoft.com/rest/api/azure/devops/pipelines
- Authentication guidance for integrations:
  https://learn.microsoft.com/azure/devops/integrate/get-started/authentication/authentication-guidance
- Rate and usage limits:
  https://learn.microsoft.com/azure/devops/integrate/concepts/rate-limits
- Using the pipeline job token from a script:
  https://learn.microsoft.com/azure/devops/pipelines/scripts/powershell
