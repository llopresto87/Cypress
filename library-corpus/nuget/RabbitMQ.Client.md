# RabbitMQ.Client — nuget

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
The official AMQP 0-9-1 client library for .NET, used to connect to a RabbitMQ
broker and publish/consume messages.

## Core API / usage shape
- The modern API is async-first: `IConnectionFactory.CreateConnectionAsync`,
  `IConnection.CreateChannelAsync`, and channel operations such as
  `IChannel.QueueDeclareAsync`, `ExchangeDeclareAsync`, `QueueBindAsync`,
  `BasicQosAsync`, `BasicPublishAsync`, `BasicConsumeAsync`, `BasicAckAsync`,
  `BasicNackAsync`, plus async disposal (`DisposeAsync`).
- Consumers implement `AsyncDefaultBasicConsumer` (or `IAsyncBasicConsumer`) and
  override `HandleBasicDeliverAsync`; delivery properties arrive as
  `IReadOnlyBasicProperties` and the body as `ReadOnlyMemory<byte>`.
- Publish-side metadata is set via `BasicProperties` (Persistent, ContentType,
  DeliveryMode, MessageId, Timestamp), with helper types like `DeliveryModes`
  and `AmqpTimestamp`. `BrokerUnreachableException` (in
  `RabbitMQ.Client.Exceptions`) is thrown when a connection cannot be
  established.

## Idioms & best practices
- Connections and channels are meant to be long-lived; opening a new
  connection/channel per operation is strongly discouraged.
- Prefer one `IChannel` per consumer/queue off a shared `IConnection`. A single
  `IChannel` shared for concurrent publishing interleaves frames incorrectly —
  guard it with mutual exclusion (e.g. `SemaphoreSlim`) if it must be shared.
- Copy or deserialize the delivery body before the handler returns; the
  underlying `ReadOnlyMemory<byte>` buffer is deallocated immediately after
  (e.g. call `body.ToArray()`).

## General pitfalls
- AMQP URIs are parsed strictly: the host part must not be omitted, and virtual
  hosts with empty names are not addressable.

## Upstream docs
- https://www.rabbitmq.com/client-libraries/dotnet
- https://www.rabbitmq.com/client-libraries/dotnet-api-guide
- https://github.com/rabbitmq/rabbitmq-dotnet-client
