# pika — pypi

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
`pika` is a synchronous AMQP 0-9-1 client for Python, used to talk to RabbitMQ.

## Core API / usage shape
- `pika.BlockingConnection` opens a connection; `connection.channel()` creates a
  channel for declaring queues, publishing, and consuming.
- Declare queues with `channel.queue_declare(queue=..., durable=True)`; consume
  with `channel.start_consuming()`; publish with `channel.basic_publish(...)`.
- Durable delivery: pair a durable queue with
  `pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent)` on publish so
  messages are written to disk and survive a broker restart.

## Idioms & best practices
- `BlockingConnection` is synchronous-only and has no notion of threading — for
  multi-threaded use, create one connection per thread, in that thread.
- Only `add_callback_threadsafe()` is thread-safe; all other connection/channel
  operations (publish, `process_data_events`, `channel()`, etc.) must run on the
  connection's own thread.
- To keep heartbeats alive while a long synchronous task runs, run the task on
  another thread (e.g. a `ThreadPoolExecutor`) and poll
  `connection.process_data_events(time_limit=...)` on the connection's own thread
  until it completes.
- Prefer a persistent per-worker connection over opening a new connection per
  publish for high-throughput scenarios.
- For async contexts, `aio-pika` is the commonly-cited alternative.

## General pitfalls
- Heartbeats and data events are dispatched only inside designated methods
  (`process_data_events()`, `start_consuming()`, etc.); if the calling thread
  blocks doing other work without invoking one of these, the broker may consider
  the connection dead and drop it.
- Setting the root logging level affects all loggers including pika's — verbose
  pika/AMQP frame logging can leak into application logs unless pika's logger is
  scoped separately.

## Upstream docs
- Docs: https://pika.readthedocs.io/
- Repo: https://github.com/pika/pika
