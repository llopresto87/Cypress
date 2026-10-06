# docling-serve — pypi

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions: for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
`docling-serve` is the remote-HTTP **service** sibling of the in-process
`docling` document-conversion package (see the `docling` page). It wraps
Docling's parsing/conversion capability behind a web API so documents are
converted by a running server over the network, rather than by importing the
library into the calling process. From a client's perspective it is a network
service to call, not a Python library whose functions you invoke in-process.

## Install, setup and configuration
- `pip install docling-serve`, then `docling-serve run` (add `--enable-ui` for
  the playground at `/ui`); or the container image
  `quay.io/docling-project/docling-serve`. The server listens on port 5001.
- Configuration is by `DOCLING_SERVE_*` environment variables (each with a CLI
  flag for some). Notable defaults: `DOCLING_SERVE_API_KEY` unset (no
  authentication); `DOCLING_SERVE_MAX_SYNC_WAIT=120` seconds for the
  synchronous endpoints; `DOCLING_SERVE_LOAD_MODELS_AT_BOOT=True`;
  `DOCLING_SERVE_ENG_LOC_NUM_WORKERS=2` task workers in the local engine;
  `DOCLING_SERVE_SINGLE_USE_RESULTS=true` with a 300-second
  `DOCLING_SERVE_RESULT_REMOVAL_DELAY`; `DOCLING_SERVE_ENABLE_UI=false`;
  `DOCLING_SERVE_ENABLE_API_DOCS=true`; `DOCLING_SERVE_MAX_NUM_PAGES` and
  `DOCLING_SERVE_MAX_FILE_SIZE` unset (no limit);
  `DOCLING_SERVE_ARTIFACTS_PATH` points model loading at a local directory.

## Core API / usage shape
- **Remote conversion lifecycle**: the typical interaction is asynchronous:
  submit a document (or a source reference) as a conversion request, receive a
  task/job handle, poll the task's status until it completes (or fails), then
  fetch the converted result.
- **HTTP surface**: endpoints exist to submit a conversion, query task status,
  and retrieve the produced output (e.g. structured document / Markdown /
  JSON), plus health/readiness endpoints for the service.
- **Client shape**: callers use an HTTP client (any language) against the
  service's base URL; the heavy parsing dependencies and models live on the
  server side, keeping the client thin.
- Endpoints (`v1` API): `POST /v1/convert/source` and `POST /v1/convert/file`
  convert synchronously; `POST /v1/convert/source/async` and
  `POST /v1/convert/file/async` return a task; `GET /v1/status/poll/{task_id}`
  reports its state; `GET /v1/result/{task_id}` fetches the output. Inputs go in
  `sources: [...]`, each with a `kind` (`http` with a `url`, `file` with a
  `base64_string` and `filename`).
- Request options include the output formats (Markdown by default; JSON, HTML,
  text, DocTags and others), `do_ocr`, and `image_export_mode`
  (`placeholder` by default, `embedded`, `referenced`).

## Idioms & best practices
- Treat conversion as async: submit, then poll status with backoff, then fetch;
  do not assume a single synchronous request returns the final document,
  especially for large inputs.
- Keep the client decoupled from server internals: depend on the documented
  HTTP contract, not on `docling` library types.
- Because conversion is a network round-trip, apply timeouts, retries on the
  submit/poll calls, and handle the failed-task terminal state distinctly from
  transport errors.
- Observed in practice: keep two timeouts, one per request (each submit or poll
  call) and one total deadline for the whole polling loop.
- Observed in practice: a task can report success with empty output, for
  example on an unreadable scan. Upstream does not document this case, so
  treat such a task as a failure, not a success.
- Keep `image_export_mode` at `placeholder` or `referenced` for text pipelines.
  Observed in practice: strip `data:` image payloads on the client anyway
  before chunking or embedding, because embedded base64 images bloat every
  chunk.
- Observed in practice: treat a missing service URL as a hard configuration
  error at startup; never fall back silently to in-process conversion or to
  skipping documents.
- Moving from the in-process `DocumentConverter` to the service changes what
  comes back: an exported format over HTTP, not a live `DoclingDocument`. Logic
  that reads structure (titles, section headers, `.texts`) must be rewritten for
  the export, or the caller must request JSON output.

## General pitfalls
- Confusing it with the in-process `docling` package: importing behaviors,
  types, or synchronous call patterns from the library do not apply. This is a
  service boundary with its own latency, availability, and versioning
  independent of the caller.
- Polling too aggressively or without an upper bound wastes resources and can
  overload the service; large documents take real time to convert.
- The server's model/dependency footprint is heavy; a client should not assume
  instant startup or unlimited concurrency on the service.
- A host with no route to the model hub cannot fetch a model the server
  lacks. The official image ships the default models under
  `DOCLING_SERVE_ARTIFACTS_PATH` and raises a runtime error for a missing one
  instead of downloading it; a pip install with the variable unset downloads
  on first use, which needs the egress that network segmentation removes.
  Stage every extra model on a host that has egress
  (`docling-tools models download`, as on the `docling` page) into a directory
  the deployment owns and mounts at `DOCLING_SERVE_ARTIFACTS_PATH` (set as an
  environment variable, not the CLI flag, when the server runs several
  workers), or bake it into a derived image. Treat that staging as a named
  provisioning step of the deployment: the runtime, with no egress, cannot do
  it.
- Results are single-use by default: a second `GET /v1/result/{task_id}`
  fails, and results are removed after the removal delay. Fetch once and keep
  the output.
- The synchronous endpoints wait at most `DOCLING_SERVE_MAX_SYNC_WAIT` seconds;
  a larger document needs the async endpoints.

## Testing
- Upstream documents no test harness for clients. Unit tests fake the HTTP
  contract (submit, poll, result, failure); an integration test against the
  container image proves the real formats and timings.

## Security defaults
- Authentication is off unless `DOCLING_SERVE_API_KEY` is set; then every
  request must carry the `X-Api-Key` header. The API reference routes
  (`/openapi.json`, `/docs` and the other docs UIs) need no key even then;
  set `DOCLING_SERVE_ENABLE_API_DOCS=false` where the schema must not be
  readable by anonymous clients.
- CORS defaults allow every origin, method and header (`["*"]`); narrow them
  for a browser-facing deployment.
- `DOCLING_SERVE_ENABLE_REMOTE_SERVICES`, `DOCLING_SERVE_ALLOW_EXTERNAL_PLUGINS`
  and `DOCLING_SERVE_ALLOW_CUSTOM_VLM_CONFIG` default to false; leave them off
  unless a pipeline needs remote calls or plugins.
- `http` sources make the server fetch URLs on the caller's behalf; restrict
  them (`DOCLING_SERVE_ALLOWED_SOURCE_TYPES`) where callers are not trusted. The
  untrusted-document cautions on `library-corpus/pypi/docling.md` apply to the
  server too.

## Operational behaviour
- Startup loads the default models (`LOAD_MODELS_AT_BOOT`), so the service is
  slow to become ready; gate traffic on its health endpoint.
- Throughput is bounded by the local engine's worker count; queued tasks wait.
- Per-document processing is bounded by `DOCLING_SERVE_MAX_DOCUMENT_TIMEOUT`,
  which defaults to 604800 seconds (seven days).

## Interop
- The library side and its `DoclingDocument` model are on
  `library-corpus/pypi/docling.md`.
- Any HTTP client works; the API is a FastAPI app with its OpenAPI docs served
  by default.

## Major lines

### v1alpha API
- The prototype API under `/v1alpha/`, with inputs split into `file_sources`
  and `http_sources`.

### v1 API
- Endpoints renamed to `/v1/`; inputs unified into `sources: [...]` with a
  `kind`; a stable schema that leaves room for new source and target kinds and
  for callbacks. Upstream keeps a migration page.

## Upstream docs
- Docs: https://docling-project.github.io/docling/
- Repo: https://github.com/docling-project/docling-serve
