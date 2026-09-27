# azure-devops-rest — platform

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. This is a **hosted-platform surface**: there is no package to
> install. The REST API is versioned by an `api-version` query parameter on every
> request, and this page is pinned by **retrieval date** instead: the surface
> below was confirmed against upstream documentation and live read-only calls
> on **2026-09-24/25**. Which `api-version` a project
> sends is the project's pin, recorded by `ingest-library` in its own wiki page.
> Orientation only; re-confirm anything load-bearing against current upstream docs.

## What it is
The **Azure DevOps Services REST API** is the HTTP surface behind every Azure
DevOps client: the web UI, the `az devops` extension (see
`library-corpus/platform/azure-cli.md`, whose "where the client stops and REST
begins" idiom is the reason to come here) and the pipeline tasks. Every resource
the platform has (Git repositories, refs, pull requests, pipelines and their
runs, variable groups) is reachable as JSON under an organization URL, with the
same credential the CLI uses.

A caller that talks to it directly, from a script or a pipeline step with a
plain HTTP client, owns three things the CLI would otherwise hide: the
authentication scheme, the redirect behavior, and the paging and throttling
contract. Those three are where direct callers go wrong, and they are what this
page carries.

## Core API / usage shape
```
https://dev.azure.com/{organization}/{project}/_apis/<area>/<resource>?api-version=<pinned>
    # every call names its api-version explicitly; never rely on a default

GET  .../_apis/git/repositories/{repo}/pullrequests
        ?searchCriteria.sourceRefName=refs/heads/<branch>
        &searchCriteria.targetRefName=refs/heads/<branch>
        &searchCriteria.status=active|abandoned|completed|all
        [&$top=<n>&$skip=<n>]
     -> { "count": <int>, "value": [GitPullRequest, ...] }
POST .../_apis/git/repositories/{repo}/pullrequests
     body: { sourceRefName, targetRefName, title, description }
     -> GitPullRequest { pullRequestId: <int>, ... }      # 200 or 201
GET  .../_apis/git/repositories/{repo}/refs?filter=heads/<branch>
     -> { "count": <int>, "value": [GitRef { name, objectId }] }
GET  .../_apis/distributedtask/variablegroups              # variable groups
POST .../_apis/pipelines/{pipelineId}/runs                 # queue a run -> { id, state, result, ... }
GET  .../_apis/pipelines/{pipelineId}/runs/{runId}          # poll that run by its id

Authorization: Bearer <pipeline job token>                 # inside a pipeline job
Authorization: Basic base64(":" + <personal access token>) # outside one: empty user name
```
List responses share one envelope, `{count, value}`, and `count` is the length
of `value` in the response (one page), not a total across pages.

## Idioms & best practices
- **Pin `api-version` in one constant and send it on every call.** The platform
  serves several versions of the same operation side by side, and field shapes
  differ between them. The version in the code is the version the project
  depends on, and it belongs in the project's wiki page, not in anyone's memory.
- **Refuse redirects in the HTTP client, always.** This platform answers a bad
  Bearer token with a cross-host redirect (the first pitfall). The discipline
  itself, and the test that the credential is never re-sent, are owned by
  `tool-corpus/ops/declared-variable-existence-auditor.md` ("Hard refusal to
  follow redirects", §6). Why a mocked transport cannot test the refusal is on
  `library-corpus/language/python.md` (the `urlopen` pitfall).
- **Treat any non-JSON or 3xx answer as an authentication failure.** Check the
  status and the `Content-Type` before parsing. An HTML body is the sign-in
  page, never an empty result, and must never be read as "no pull requests" or
  "no such group".
- **Use full ref names in search criteria.** Upstream's own examples pass
  `refs/heads/<branch>`, and every ref in every response is in that form.
  Whether a bare branch name is accepted is not recorded, so do not rely on it.
- **Send `searchCriteria.status` explicitly.** Unset, the pull-request list
  defaults to active pull requests only; `all` is a documented value that
  includes every state. A duplicate check that forgets this misses an abandoned
  or completed pull request from the same branch.
- **Create with the minimal body and nothing that acts on its own.** Automation
  that opens a pull request sends source, target, title and description only. It
  never sends `completionOptions` (auto-complete, merge strategy, policy bypass),
  never sets `autoCompleteSetBy`, and never includes `reviewers`, because a
  reviewer entry can carry a vote. A human merges; the script proposes.
- **Poll the run the queue call returned, and never re-send a `POST` blind.**
  Queueing a run answers with its `id`. The identity rule is
  `core/method/bounded-execution.md` (`toolcraft.bounded-execution`, clause 4),
  and `skill-corpus/drive-hosted-cicd-cli.md` §5 shows where it bites on a hosted
  pipeline. What this API adds: a `GET` may be retried within a bound, but the
  `POST`s that queue a run or create a pull request are not idempotent. After a
  lost response, read first, because the object may already exist.
- **List variable groups unfiltered, then look up what seems missing.** A
  server-side name filter lets the server decide what the audit examines. Read
  the whole scope, compare locally, and do a targeted lookup for each name that
  appears absent.

## General pitfalls
- **A bad Bearer token gets a redirect to a sign-in page, not a 401.** Observed
  on a read call: an invalid `Basic` personal token got `401` with an empty body,
  but an invalid `Bearer` token, or no `Authorization` header at all, got a `302`
  with an HTML body and a `Location` on a *different host* (the sign-in service).
  Upstream documents no redirect-on-auth-failure behavior. A client that follows
  redirects by default will send the Bearer header to that other host (some
  standard-library clients copy every request header onto the redirected request)
  and then hand the caller an HTML page where JSON was expected. An expired or
  wrong pipeline job token takes exactly this path.
- **Variable-group responses carry non-secret values in plaintext.** A secret
  variable's value comes back as `null`, but every non-secret value is in the
  response body. A tool meant to report names only must split the response at
  the boundary and never print or log the raw body.
- **A group that exists is not a group the pipeline may use.** Existence and
  authorization are separate grants. A pipeline that references a group it is not
  authorized for can receive empty values rather than an error, so a present name
  in the REST listing proves nothing about delivery.
- **Paging is under-documented; assume one page.** The pull-request list accepts
  `$top` and `$skip`, but upstream states no default page size, no maximum and no
  continuation token for it. Until a project has measured the paging behavior,
  treat a listing as one page and bound any loop that walks `$skip`.
- **The list truncates descriptions; that is not the storage limit.** The
  pull-request list returns each description cut short at read time. That limit
  says nothing about how long a description may be on create or update. Upstream
  gives a maximum only on the update operation, and whether create enforces the
  same ceiling, or truncates rather than rejects, is not recorded.
- **Create may answer `200` or `201`.** The create operation's response table
  says one and its own worked example returns the other. Accept both.
- **Throttling starts before `429`.** Requests over the usage budget are first
  delayed and answered with a normal success status plus `Retry-After` and
  `X-RateLimit-*` headers; only later are they blocked with `429`. A client that
  reads only the status code will not notice it is being slowed. Honor
  `Retry-After` whenever it is present.

## Upstream docs
- REST API reference (all areas, version selector per page):
  https://learn.microsoft.com/rest/api/azure/devops/
- Pull requests (list, create, update):
  https://learn.microsoft.com/rest/api/azure/devops/git/pull-requests
- Refs: https://learn.microsoft.com/rest/api/azure/devops/git/refs
- Authentication guidance for integrations:
  https://learn.microsoft.com/azure/devops/integrate/get-started/authentication/authentication-guidance
- Rate and usage limits:
  https://learn.microsoft.com/azure/devops/integrate/concepts/rate-limits
- Using the pipeline job token from a script:
  https://learn.microsoft.com/azure/devops/pipelines/scripts/powershell
