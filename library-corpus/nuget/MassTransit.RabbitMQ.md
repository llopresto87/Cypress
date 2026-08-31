# MassTransit.RabbitMQ — nuget

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
The RabbitMQ transport for MassTransit, a message-bus abstraction for .NET. It
provides typed publish/consume, retry and error-handling middleware, and
convention-based endpoint naming over AMQP, so application code works in terms
of message contracts and consumers instead of hand-rolled channels, exchanges,
and bindings (`RabbitMQ.Client.md` covers that raw AMQP surface).

## Core API / usage shape
- Registration is `AddMassTransit(cfg => cfg.UsingRabbitMq(...))` in the DI
  container; the RabbitMQ host and endpoint topology are configured inside
  that callback.
- Producing is `IPublishEndpoint.Publish<T>()` (or a send endpoint for
  directed messages); the message type drives the published contract.
- Consuming is a class implementing `IConsumer<T>` with
  `Consume(ConsumeContext<T> context)`; the context carries the message plus
  correlation, headers, and reply/publish capabilities.
- Endpoint and queue names are derived by convention from the consumer or
  message type name, kebab-cased — the topology is generated rather than
  spelled out.
- Retry is middleware: `UseMessageRetry(r => r.Interval(...))` configures
  attempts and spacing, and `.Ignore<TException>()` excludes exception types
  from retry entirely.

## Idioms & best practices
- Define message contracts as plain, versionable types shared between producer
  and consumer rather than transport-specific payloads.
- Pair every retry policy with an explicit `.Ignore<T>()` list covering the
  exceptions that are deterministic failures.
- Let the naming conventions stand unless there is a real interop reason to
  override them; overriding one endpoint's name breaks the symmetry that makes
  the rest predictable.

## General pitfalls
- Retry policies assume failures are transient. An exception that can never
  succeed on retry — a permanent validation failure, a malformed payload — must
  be excluded via `.Ignore<T>()`. Without that, a poison message retries
  forever, consuming the consumer's concurrency and stalling the queue behind
  it.

## Upstream docs
- https://masstransit.io/
- https://github.com/MassTransit/MassTransit
- https://www.nuget.org/packages/MassTransit.RabbitMQ
