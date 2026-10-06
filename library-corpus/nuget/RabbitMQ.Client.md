# RabbitMQ.Client — nuget

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions — for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
The official AMQP 0-9-1 client library for .NET, used to connect to a RabbitMQ
broker and publish/consume messages. The package id is `RabbitMQ.Client`; the
RabbitMQ team maintains it. Licence: dual Apache-2.0 and MPL-2.0, and the user
may pick either. The 7.x and 6.x lines are supported; 5.x and older are end of
life. The API mirrors the AMQP 0-9-1 model (connections, channels, exchanges,
queues, bindings) with some convenience on top.

## Install, setup and configuration
- `dotnet add package RabbitMQ.Client`. The 7.x line needs .NET Framework
  4.6.1+ or a .NET Standard 2.0 implementation. OpenTelemetry tracing support
  is the separate `RabbitMQ.Client.OpenTelemetry` package.
- A `ConnectionFactory` holds the settings. Set `HostName`, `Port`,
  `VirtualHost`, `UserName`, `Password` one by one, or set `Uri`
  (`amqp://user:pass@host:port/vhost`). Defaults when unset:
  - user `guest`, password `guest`, virtual host `/`, host `localhost`;
  - port 5672, or 5671 with TLS;
  - `AutomaticRecoveryEnabled` and `TopologyRecoveryEnabled`: true;
  - `NetworkRecoveryInterval`: 5 seconds;
  - `RequestedHeartbeat`: 60 seconds;
  - `RequestedConnectionTimeout`, `SocketReadTimeout`, `SocketWriteTimeout`:
    30 seconds;
  - `ConsumerDispatchConcurrency`: 1 (deliveries handled one at a time);
  - `MaxInboundMessageBodySize`: 64 MiB.
- `ClientProvidedName` names every connection the factory opens. The name shows
  in broker logs and the management UI. Upstream strongly encourages setting it.
- `CreateConnectionAsync(endpoints)` with a list of `AmqpTcpEndpoint`s
  connects to the first reachable node.
- TLS: `factory.Ssl.Enabled = true`, `Ssl.ServerName` (must match the server
  certificate's SAN or CN), optional `Ssl.CertPath` / `Ssl.CertPassphrase` for
  a PKCS#12 client certificate, `Ssl.Version` for the allowed protocols.
- OAuth 2: `OAuth2ClientCredentialsProvider` set as the factory's
  `CredentialsProvider` sends a token as the password. `CredentialsRefresher`
  renews it before it expires. The broker needs its OAuth 2 plugin.

## Core API / usage shape
- The modern API is async-first: `IConnectionFactory.CreateConnectionAsync`,
  `IConnection.CreateChannelAsync`, and channel operations such as
  `IChannel.QueueDeclareAsync`, `ExchangeDeclareAsync`, `QueueBindAsync`,
  `BasicQosAsync`, `BasicPublishAsync`, `BasicConsumeAsync`, `BasicAckAsync`,
  `BasicNackAsync`, `BasicRejectAsync`, `BasicCancelAsync`, plus
  `CloseAsync` and async disposal (`DisposeAsync`).
- Declaring a queue or exchange creates it if it is missing. The guide's
  short example declares non-durable, non-auto-delete entities; pass
  `durable: true` for entities that must survive a broker restart.
  `QueueDeclarePassiveAsync` only checks existence and closes the channel if
  the queue is missing.
- The default exchange (empty name) routes to the queue whose name equals the
  routing key; every queue is bound to it automatically. Upstream says not to
  add your own bindings to it. A named direct exchange needs `QueueBindAsync`.
  A publish to the default exchange with a named exchange's binding key as the
  routing key reaches no queue, unless a queue has that exact name.
- Consumers implement `AsyncDefaultBasicConsumer` (or `IAsyncBasicConsumer`) and
  override `HandleBasicDeliverAsync`; delivery properties arrive as
  `IReadOnlyBasicProperties` and the body as `ReadOnlyMemory<byte>`.
  `AsyncEventingBasicConsumer` exposes the same as a `ReceivedAsync` event.
- Publish-side metadata is set via `BasicProperties` (Persistent, ContentType,
  DeliveryMode, MessageId, Timestamp, Headers, Expiration), with helper types
  like `DeliveryModes` and `AmqpTimestamp`. `BrokerUnreachableException` (in
  `RabbitMQ.Client.Exceptions`) is thrown when a connection cannot be
  established.
- `BasicPublishAsync(exchange, routingKey, mandatory, props, body)`: with
  `mandatory: true`, an unroutable message comes back through the
  `BasicReturnAsync` event.
- Publisher confirms are off by default. Turn them on per channel with
  `CreateChannelAsync(new CreateChannelOptions(publisherConfirmationsEnabled:
  true, publisherConfirmationTrackingEnabled: true))`. With tracking on,
  awaiting `BasicPublishAsync` returns once the broker confirms, and throws if
  the broker nacks or returns the message.
- `BasicQosAsync(0, prefetchCount, false)` caps unacknowledged deliveries per
  consumer. `BasicGetAsync` polls one message and is upstream's least
  recommended way to consume.

## Idioms & best practices
- Connections and channels are meant to be long-lived; opening a new
  connection/channel per operation is strongly discouraged.
- Prefer one `IChannel` per consumer/queue off a shared `IConnection`. A single
  `IChannel` shared for concurrent publishing interleaves frames incorrectly;
  guard it with mutual exclusion (e.g. `SemaphoreSlim`) if it must be shared.
- Copy or deserialize the delivery body before the handler returns; the
  underlying `ReadOnlyMemory<byte>` buffer is deallocated immediately after
  (e.g. call `body.ToArray()`).
- Retry the first connection yourself. Automatic recovery covers only a
  connection that was once open, so a hosted service that starts before the
  broker is ready must catch `BrokerUnreachableException` and retry a bounded
  number of times with a delay.
- Observed in practice, in a publisher service that is called from concurrent
  requests and opens its connection and channel on first use: the publisher
  guards the creation with a `SemaphoreSlim` and rechecks
  `IChannel.IsOpen` inside the lock, so concurrent first callers do not open
  two channels. Upstream documents the mutual-exclusion rule but not this lazy
  pattern.
- Use manual acknowledgements (`autoAck: false`) and ack after processing.
  Upstream calls automatic acknowledgement unsafe: a delivery is lost if the
  consumer's connection or channel closes first.
- Set a prefetch with `BasicQosAsync`. The protocol default of 0 means no
  limit.
- Use publisher confirms where a lost message matters. Publishing alone gives
  no delivery guarantee.
- With `ConsumerDispatchConcurrency` above 1, acknowledge one delivery at a
  time. A multiple-ack can acknowledge a tag twice, which is a protocol error.
- Set `ClientProvidedName` on every factory.

## General pitfalls
- AMQP URIs are parsed strictly: the host part must not be omitted, and virtual
  hosts with empty names are not addressable.
- A channel-level error (consuming from a missing queue, a failed passive
  declare) closes the channel for good.
  It is not recovered, even when the connection recovers; open a new channel.
- Messages published while the connection is down are lost: the client does
  not buffer them. During recovery, publishes throw. Republishing is the
  application's job, and only confirms tell you what arrived.
- After recovery, deliveries that were not acked are redelivered. Handlers must
  be idempotent or detect redeliveries.
- If no handler is attached to `BasicReturnAsync`, returned mandatory messages
  are dropped without notice.
- Requeueing every failed delivery (`BasicNackAsync(tag, false, requeue:
  true)`) can loop forever. Count redeliveries, and reject for good or requeue
  after a delay once a limit is reached.
- The client cannot encode `ulong` values in headers or arguments; it throws.
  Signed 64-bit integers work.
- Do not re-publish a nacked message from inside a confirm callback; upstream
  says to hand it to a separate publishing loop.

## Testing
- Upstream documents no test doubles. Its own integration tests run against a
  real broker, and the migration guide points to them as usage examples.
- Run integration tests against a real broker, for example in a container.
  `IConnection`, `IChannel` and `IAsyncBasicConsumer` are interfaces, so a unit
  test can substitute them (`NSubstitute.md`) or call
  `HandleBasicDeliverAsync` on a consumer directly; the 7.x changelog records
  work on that method's testability.

## Security defaults
- The `guest` user can connect only from localhost by default. Remote clients
  need their own user. Upstream recommends deleting `guest` or giving it a
  strong generated password.
- TLS is off by default. When it is on, the .NET client verifies the server
  certificate by default, unlike the Java client. Turning verification off
  (`Ssl.AcceptablePolicyErrors`) exposes the connection to impersonation.
- Setting `Uri` to an `amqps://` URI turns TLS on, but also sets
  `Ssl.AcceptablePolicyErrors` to `RemoteCertificateNameMismatch`, so the
  server name is not checked. Reset it to `SslPolicyErrors.None` after you set
  the URI, or configure `Ssl` explicitly.
- Credentials in an `amqp://user:pass@...` URI end up wherever the URI is
  logged or stored. Supply them from a secret store.
- Use an HTTPS token endpoint for OAuth 2.

## Operational behaviour
- Each `IConnection` runs one background task that reads the socket and
  dispatches events. Heartbeats use timers per connection.
- Consumer callbacks run in delivery order per channel, one at a time by
  default. `ConsumerDispatchConcurrency` above 1 keeps dispatch in order but
  lets processing overlap.
- Automatic recovery starts after an I/O error, a socket read timeout or missed
  heartbeats. It reconnects, reopens channels, restores QoS and confirm
  settings, then redeclares exchanges, queues, bindings and consumers. It
  retries every `NetworkRecoveryInterval` until it succeeds. It does not start
  for a connection the application closed, or for the first connection
  attempt.
- Close the channel and the connection with `CloseAsync`, then dispose them.
  Upstream calls an explicit close first the best practice.
- `MaxInboundMessageBodySize` is the largest message body the client accepts
  from the broker (64 MiB by default).

## Interop
- OpenTelemetry: `RabbitMQ.Client.OpenTelemetry` bridges the client's
  activity source into OpenTelemetry tracing; the hosting side is on
  `OpenTelemetry.Extensions.Hosting.md`.
- Other-language consumers: AMQP 0-9-1 is the wire contract, so a .NET
  publisher and, say, a Python consumer interoperate on exchange, routing key,
  properties and body bytes alone. Agree the content type and encoding
  explicitly.

## Major lines

### 6.x line
- The channel type is `IModel`; operations are synchronous
  (`BasicPublish`, `QueueDeclare`), and message properties come from
  `CreateBasicProperties()`.
- Consumers are synchronous (`EventingBasicConsumer`, `DefaultBasicConsumer`)
  unless the factory sets `DispatchConsumersAsync = true`, which is required
  before async consumers work.

### 7.x line
- The public API is async throughout (task-based, `Async` suffix). `IModel` is
  renamed `IChannel`, and the synchronous consumer types are gone: implement
  `IAsyncBasicConsumer` / `AsyncDefaultBasicConsumer` or use
  `AsyncEventingBasicConsumer`.
- Properties are a `new BasicProperties()` passed to `BasicPublishAsync`;
  `CreateBasicProperties` is removed.
- Delivery bodies are `ReadOnlyMemory<byte>` owned by the library and valid
  only inside the handler.
- Publisher confirms are configured through `CreateChannelOptions` at channel
  creation, and awaiting the publish waits for the confirm when tracking is on.
- The migration guide (`v7-MIGRATION.md`) lists the remaining changes.

## Upstream docs
- https://www.rabbitmq.com/client-libraries/dotnet
- https://www.rabbitmq.com/client-libraries/dotnet-api-guide
- https://www.rabbitmq.com/docs/confirms
- https://www.rabbitmq.com/tutorials/tutorial-seven-dotnet (publisher confirms)
- https://github.com/rabbitmq/rabbitmq-dotnet-client
- https://github.com/rabbitmq/rabbitmq-dotnet-client/blob/main/v7-MIGRATION.md
- https://rabbitmq.github.io/rabbitmq-dotnet-client/api/RabbitMQ.Client.html
