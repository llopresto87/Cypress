# openai — pypi

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions: for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
`openai` (openai-python) is the official OpenAI Python SDK for calling the
OpenAI API (chat/responses, embeddings, etc.). Being an OpenAI-compatible client,
it can also target other servers implementing the OpenAI API (e.g. self-hosted
inference servers) by setting `base_url`.

## Install, setup and configuration
- `pip install openai`. The client reads `OPENAI_API_KEY` from the
  environment when `api_key` is not passed; upstream recommends keeping the key
  in a `.env` file (loaded with python-dotenv) rather than in source control.
- `base_url` (or `OPENAI_BASE_URL`) points the client at another
  OpenAI-compatible server.
- Defaults per the README: a 10-minute request timeout and 2 automatic retries.
  Retried: connection errors, 408, 409, 429 and 5xx responses, and only when
  the request body can be safely resent.
- `OPENAI_LOG=info` (or `debug`) turns on the SDK's logging through the
  standard `logging` module.

## Core API / usage shape
- Instantiate a client: a sync `OpenAI` client and an async `AsyncOpenAI` client
  are both provided. Call the API surface off the client (chat/responses, etc.).
- `base_url`, `api_key`, and `timeout` are set per client instance.
- `extra_body` (and `extra_query` / `extra_headers`) passes non-standard or
  undocumented request parameters not in the standard OpenAI request signature —
  e.g. vendor-specific fields for an OpenAI-compatible backend.

## Idioms & best practices
- Pick the client that matches the calling context; the general async/sync
  boundary rule lives in `../language/python.md`.
- Set `timeout` explicitly per client (short for quick extraction calls, generous
  for long reasoning calls) rather than relying on the default; timed-out requests
  are retried automatically by default. Per the README, the default timeout is
  10 minutes and failed requests are retried twice with a short exponential
  backoff, so one call can block for about three times its timeout. Set
  `timeout=` and `max_retries=` per client, or override one call with
  `client.with_options(...)`.
- Catch `APIStatusError` (and subclasses) rather than a bare `Exception` to
  access request IDs and error detail useful for debugging.
- Observed in practice: check `choices[0].finish_reason` on chat completions.
  `"length"` means the output was cut at the token limit, and reasoning models
  behind compatible backends can spend the whole budget on reasoning and return
  empty `content`.

## General pitfalls
- Observed in practice: `except (json.JSONDecodeError, Exception)` is the same
  as `except Exception`. Around an LLM call it collapses an outage, a changed
  response shape and a code bug into one silent fallback. Catch the SDK's
  errors and parse errors separately (the general Python half is on
  `library-corpus/language/python.md`).
- Errors: connection failures and timeouts raise `openai.APIConnectionError`
  (timeouts as its `APITimeoutError` subclass); a 4xx or 5xx response raises an
  `openai.APIStatusError` subclass carrying `status_code` and `response`. All
  inherit from `openai.APIError`. While a stream is consumed, a read timeout
  raises `APITimeoutError`; catch the SDK exceptions, not raw HTTP-library ones.

## Testing
- Upstream documents no test harness. Unit tests inject a fake client or mock
  the HTTP transport; set `max_retries=0` in tests so a failure surfaces at
  once instead of after retries.

## Security defaults
- The key travels in a request header to `base_url`; a compatible backend
  reached over plain HTTP sees it in clear.
- Keep the key out of source control (the README's `.env` advice above).

## Operational behaviour
- With the defaults a stalled request can hold its caller for the timeout
  times three (one try plus two retries). Size `timeout` and `max_retries` to
  the caller's own deadline.
- Request IDs on `APIStatusError` (`exc.request_id`) are what upstream support
  asks for.

## Interop
- Any server implementing the OpenAI API can sit behind `base_url`; fields it
  adds go through `extra_body`.
- The async client uses an HTTPX-based transport by default, and the README
  documents an optional `aiohttp` transport for higher concurrency.

## Major lines
- The package "generally follows SemVer", but upstream reserves the right to
  ship some backwards-incompatible changes (for example type-only changes) in
  minor releases. This page does not record the differences between the major
  lines; read the release notes before crossing one.

## Upstream docs
- Repo/docs: https://github.com/openai/openai-python
- API reference: https://platform.openai.com/docs/
