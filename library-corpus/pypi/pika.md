# pika — pypi

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions: for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
`pika` is a synchronous AMQP 0-9-1 client for Python, used to talk to RabbitMQ.

## Install, setup and configuration
- `pip install pika`. Connection settings live in
  `pika.ConnectionParameters(host, port, virtual_host, credentials,
  heartbeat=..., connection_attempts=..., retry_delay=...)` (or
  `pika.URLParameters("amqp://...")`).
- Defaults, from the source: host `localhost`, port 5672, credentials
  `PlainCredentials("guest", "guest")`, `connection_attempts=1`,
  `retry_delay=2.0`, and `heartbeat=None`, which accepts the broker's proposed
  heartbeat during connection tuning.
- Pass credentials as `pika.PlainCredentials(user, password)`.

## Core API / usage shape
- `pika.BlockingConnection` opens a connection; `connection.channel()` creates a
  channel for declaring queues, publishing, and consuming.
- Declare queues with `channel.queue_declare(queue=..., durable=True)`; consume
  with `channel.start_consuming()`; publish with `channel.basic_publish(...)`.
- Durable delivery: pair a durable queue with
  `pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent)` on publish so
  messages are written to disk and survive a broker restart.
- `channel.basic_qos(prefetch_count=N)` caps how many unacknowledged messages
  the broker pushes to this consumer (`prefetch_size` and `global_qos` are the
  other knobs; all default to 0 / False, meaning no limit).

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
- Set `basic_qos(prefetch_count=...)` before consuming on long-running job
  workers, so one busy worker does not hoard the queue while others idle.
- Observed in practice: containers often start before the broker is ready.
  Wrap the first `BlockingConnection(...)` in a retry with exponential backoff
  on `AMQPConnectionError` and a maximum number of attempts, or raise
  `connection_attempts` / `retry_delay` on the parameters (the default is one
  attempt).
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

- An unset `credentials` silently falls back to `guest` / `guest`, and an unset
  host to `localhost`; a missing configuration value shows up as an
  authentication or connection failure, not as a configuration error.

## Testing
- Upstream documents no test harness. Unit tests stub the channel; behaviour
  that depends on the broker (acks, redelivery, prefetch, heartbeats) is proved
  only against a real RabbitMQ.

## Security defaults
- The default credentials are RabbitMQ's `guest` account; never rely on them
  outside a local broker.
- Plain AMQP is unencrypted. TLS goes through `ssl_options` on the connection
  parameters.

## Operational behaviour
- Startup: one connection attempt by default; with `connection_attempts` and
  `retry_delay` set, pika retries the socket connection itself.
- Steady state: heartbeats and deliveries are processed only inside pika's
  I/O methods (pitfall above), so the connection's thread must call them
  regularly.
- Shutdown: close the connection explicitly. Unacknowledged messages of a
  closed consumer return to the queue, per AMQP semantics (the broker side is on
  the RabbitMQ page).

## Interop
- The broker and its exchange, queue and acknowledgement model are on
  `library-corpus/maven/rabbitmq.md`.
- For asyncio code, `aio-pika` is the commonly cited alternative.

## Major lines
- Upstream's major-line differences were not fetched for this page; read the
  changelog before crossing a major.

## Upstream docs
- Docs: https://pika.readthedocs.io/
- Repo: https://github.com/pika/pika
