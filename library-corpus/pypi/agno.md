# agno — pypi

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
`agno` is a Python agent-orchestration framework (Apache-2.0) for building
LLM agents with pluggable models, tools/toolkits, and storage backends.

## Core API / usage shape
- `Agent` composes a model, tools, and (optionally) session state; `agent.run(...)`
  executes it. `agent.run(input=..., stream=True)` returns a **lazy synchronous
  generator** whose inference happens during iteration.
- `OpenAIChat` targets OpenAI or any OpenAI-compatible backend via
  `base_url`/`api_key`, and accepts `extra_body` (see `openai.md`). A
  `role_map` argument controls how roles (system/user/assistant/tool) are sent.
- `Toolkit` groups callable tools; storage backends (e.g. Redis) persist session
  data.

## Idioms & best practices
- To feed the streaming generator into an async endpoint, iterate it inside a
  worker thread (e.g. `loop.run_in_executor`) and hand chunks to the async side
  via a queue — the async/sync boundary rule in `../language/python.md` applied
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
  dynamically-evaluated fields is an inherent injection/RCE surface — validate
  and constrain tool inputs.

## Upstream docs
- Docs: https://docs.agno.com
- Repo: https://github.com/agno-agi/agno
