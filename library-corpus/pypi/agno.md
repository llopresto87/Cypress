# agno — pypi

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions: for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
`agno` is a Python agent-orchestration framework (Apache-2.0) for building
LLM agents with pluggable models, tools/toolkits, and storage backends.

## Install, setup and configuration
- `pip install agno`, plus the client package of each model provider and
  storage backend you use (`openai`, `redis`, ...).
- Configuration is per `Agent` constructor argument; the defaults that matter
  are listed under the core API below (history off, no tool-call limit,
  generated session id).

## Core API / usage shape
- `Agent` composes a model, tools, and (optionally) session state; `agent.run(...)`
  executes it. `agent.run(input=..., stream=True)` returns a **lazy synchronous
  generator** whose inference happens during iteration.
- `OpenAIChat` targets OpenAI or any OpenAI-compatible backend via
  `base_url`/`api_key`, and accepts `extra_body` (see `openai.md`). A
  `role_map` argument controls how roles (system/user/assistant/tool) are sent.
- `Toolkit` groups callable tools; storage backends (e.g. Redis) persist session
  data.
- Conversation memory: `Agent(session_id=..., db=RedisDb(redis_client=...,
  db_prefix="agno", expire=...), add_history_to_context=True,
  num_history_runs=N)`. `expire` gives the stored session data a time to live;
  `add_history_to_context` defaults to False, so history is not sent unless
  asked for. `session_id` is generated when unset.
- `tool_call_limit=` caps the tool calls in one run (unset by default).
- A `Toolkit` exposes functions through `self.register(fn, name=None)`, or by
  passing `tools=[...]` to its constructor; async functions are detected
  automatically. The function's signature and docstring become the tool schema
  the model sees, so write them for the model.
- `system_message` replaces the generated system message; `instructions` (a
  string, a list or a callable) and `description` are added into the generated
  one. They are separate inputs.

## Idioms & best practices
- To feed the streaming generator into an async endpoint, iterate it inside a
  worker thread (e.g. `loop.run_in_executor`) and hand chunks to the async side
  via a queue. This is the async/sync boundary rule in `../language/python.md` applied
  to a lazy generator.
- `OpenAIChat`'s default role mapping can send the `system` role as OpenAI's
  `developer` role, which breaks OpenAI-compatible-but-not-OpenAI backends (e.g.
  vLLM accepting only system/user/assistant/tool). Pass an explicit `role_map`
  to override it.
- Creating a fresh `Agent` per request is reasonable defense-in-depth when an
  agent carries per-request state.

## General pitfalls
- `Agent` session state and `Toolkit` instance state are mutable; sharing an
  agent across concurrent requests risks cross-session state leakage. Isolate
  per-request state carefully.
- Passing untrusted input into tool command handlers (e.g. MCP tooling) or into
  dynamically-evaluated fields is an inherent injection/RCE surface: validate
  and constrain tool inputs.
- Without `tool_call_limit`, a model that keeps calling tools runs until the
  model stops; set a limit on any agent exposed to untrusted input.
- `RedisDb` needs the `redis` package (`library-corpus/pypi/redis.md`);
  importing `agno.db.redis` raises `ImportError` when it is missing, before
  any `RedisDb` is constructed.

## Testing
- Upstream documents no test harness on the pages read for this page. Agents
  call a model on every run, so unit tests replace the model client or point
  `base_url` at a local stub; tool functions are plain Python and test on their
  own.

## Security defaults
- No tool-call limit by default (above).
- Tools run with the process's own rights; a tool that shells out or evaluates
  input is the injection surface named in the pitfalls.
- Session data in Redis lives until `expire` (unset means no expiry).

## Operational behaviour
- `agent.run(..., stream=True)` returns a lazy synchronous generator (the
  source hands back the run's generator function unstarted): the model call
  happens while it is iterated, on the iterating thread. Memory creation, when
  enabled, runs in a background thread that the stream waits for.
- Session state persists in the configured `db` between runs.

## Interop
- Models: `OpenAIChat` against OpenAI or any compatible backend
  (`library-corpus/pypi/openai.md`).
- Storage: `RedisDb` over a `redis` client (`library-corpus/pypi/redis.md`),
  among other backends.

## Major lines
- This page does not record differences between agno's lines. Read the
  release notes for your pin.

## Upstream docs
- Docs: https://docs.agno.com
- Repo: https://github.com/agno-agi/agno
