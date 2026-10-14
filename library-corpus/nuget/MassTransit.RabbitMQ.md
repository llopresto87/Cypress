# MassTransit.RabbitMQ — nuget

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions — for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
MassTransit is a message-based application framework for .NET: typed message
contracts, consumers, retry, redelivery, an outbox, sagas and a test harness,
over a choice of brokers. Application code works with contracts and consumers;
MassTransit declares the exchanges, queues and bindings. On RabbitMQ it builds
on the official AMQP client, whose raw surface is on `RabbitMQ.Client.md`. The
packages this page covers:

- `MassTransit.RabbitMQ`: the RabbitMQ transport (`UsingRabbitMq`). It depends
  on `MassTransit` and on `RabbitMQ.Client`.
- `MassTransit`: the core (registration, consumers, middleware, the
  in-memory transport). Needed by every MassTransit application; the transport
  package brings it.
- `MassTransit.EntityFrameworkCore`: the transactional outbox and inbox on an
  EF Core `DbContext`, and the EF saga repository. Needed when messages must be
  published if and only if a database transaction commits.

Upstream: the docs at `masstransit.massient.com` (the older `masstransit.io`
addresses redirect there), the source in `MassTransit/MassTransit`. Licence:
the 8 line is Apache-2.0 open source; from the 9 line MassTransit is a
commercial product that needs a licence key (Major lines).

## Install, setup and configuration
- `dotnet add package MassTransit.RabbitMQ`, plus
  `MassTransit.EntityFrameworkCore` for the outbox.
- Register with `services.AddMassTransit(x => { ... x.UsingRabbitMq((context,
  cfg) => { ... }); })`. Methods on `x` configure the bus and the service
  collection; the `UsingRabbitMq` callback runs after the container is built,
  so bus-level registration belongs outside it.
- Host: `cfg.Host("host", "vhost", h => { h.Username(...); h.Password(...);
  })`, or `cfg.Host(new Uri("amqps://..."))`. Credentials are per virtual host.
  `h.UseSsl(...)` turns on TLS. The common settings can instead be bound
  through `RabbitMqTransportOptions` (`Host`, `Port`, `VHost`, `User`, `Pass`,
  `UseSsl`) with the options pattern; an explicit `cfg.Host(...)` wins over
  them.
- Host-wide options: `PublisherConfirmation` (default true: a publish or send
  waits for the broker's confirm), `Heartbeat`, `RequestedChannelMax`,
  `RequestedConnectionTimeout`, `ContinuationTimeout`. `UseCluster` exists, but
  upstream prefers a load balancer in front of a RabbitMQ cluster.
- Receive endpoints: `PrefetchCount` (default max(CPU count × 2, 16)),
  `ConcurrentMessageLimit` (defaults to the prefetch count), `PurgeOnStartup`
  (default false), `AutoDelete` (default false), `Durable` (default true),
  `ConfigureConsumeTopology` (default true), `PublishFaults` (default true).
  `PrefetchCount` and `ConcurrentMessageLimit` set at bus level become each
  endpoint's default, not a limit shared across the bus.
- `SetQuorumQueue(n)` makes an endpoint's queue a quorum queue; apply it to all
  endpoints through `AddConfigureEndpointsCallback` with a pattern match on
  `IRabbitMqReceiveEndpointConfigurator`.
- Bus lifetime: `AddMassTransit` registers a hosted service that starts and
  stops the bus with the host, and health checks per bus tagged `ready` and
  `masstransit`. `MassTransitHostOptions` holds `WaitUntilStarted` (default
  false: the broker connection is made asynchronously and host startup does
  not wait for it), `StartTimeout` (default: wait forever), `StopTimeout`
  (default: wait forever for consumers to finish) and `ConsumerStopTimeout`.
  The Generic Host's own `ShutdownTimeout` must leave the bus time to stop.

## Core API / usage shape
- Consumers implement `IConsumer<T>` with `Consume(ConsumeContext<T>
  context)`; the context carries the message, headers and correlation, and is
  itself a publish and send endpoint. Conventional consumers, a class marked
  `[Consumer]` with public `Consume` methods per message type, exist from
  v9.2.1.
- Register with `x.AddConsumer<T>()` (optionally with a
  `ConsumerDefinition<T>`) or `x.AddConsumers(assembly)`, then call
  `cfg.ConfigureEndpoints(context)` last, after every setting and middleware,
  so it creates one receive endpoint per consumer.
- Endpoint names come from the endpoint name formatter. The default formatter
  uses the PascalCase type name without namespace, trimming suffixes such as
  `Consumer` (`SubmitOrder`); `SetKebabCaseEndpointNameFormatter()` gives
  `submit-order`, `SetSnakeCaseEndpointNameFormatter()` gives `submit_order`.
  A formatter constructed with a prefix (`new KebabCaseEndpointNameFormatter(
  prefix: "dev", ...)`) namespaces every queue, for a broker shared between
  developers. Naming precedence: a name fixed in the definition's constructor,
  then `.Endpoint(e => e.Name = ...)` on the registration, then the formatter.
- Producing: `IPublishEndpoint.Publish<T>()` for events, `ISendEndpointProvider`
  / `ISendEndpoint.Send<T>()` for commands, `IRequestClient<T>` for
  request/response. All are scoped services; inside a consumer, publish
  through the `ConsumeContext`. v9 adds `IScopedBus`, one scoped interface for
  all three.
- RabbitMQ topology: a publish goes to a fanout exchange named after the
  message type; each receive endpoint has a queue and an exchange of the same
  name, and the message-type exchange is bound to the endpoint exchange for
  every consumed type. Exchanges and queues are durable by default. Send
  addresses are `queue:name` or `exchange:name`; an address query string can
  set `durable`, `autodelete`, `temporary`, `bind` and the exchange `type`.
- Middleware is configured per endpoint: `UseMessageRetry(r => ...)` with the
  policies `None`, `Immediate`, `Interval`, `Intervals`, `Exponential`,
  `Incremental`; `r.Handle<T>()` or `r.Ignore<T>()` filter which exceptions
  are retried (use one kind per filter, combining them is unpredictable).
  `UseDelayedRedelivery(...)` returns the message to the broker for a later
  attempt. `UseInMemoryOutbox(context)` and
  `UseEntityFrameworkOutbox<TDbContext>(context)` hold outgoing messages until
  the consumer succeeds.
- Transactional outbox (`MassTransit.EntityFrameworkCore`):
  `x.AddEntityFrameworkOutbox<TDbContext>(o => { o.UsePostgres(); /* or
  UseSqlServer, UseMySql */ o.UseBusOutbox(); })`, plus
  `modelBuilder.AddInboxStateEntity()`, `AddOutboxMessageEntity()` and
  `AddOutboxStateEntity()` in `OnModelCreating` (the `InboxState`,
  `OutboxMessage` and `OutboxState` tables). The consumer outbox is switched on
  per endpoint with `UseEntityFrameworkOutbox<TDbContext>(context)`, usually
  from `AddConfigureEndpointsCallback`. Options: `QueryDelay` (poll delay when
  idle), `DuplicateDetectionWindow` (how long an `InboxState` row is kept),
  `IsolationLevel` (Serializable by default), `QueryMessageLimit`,
  `QueryTimeout`.
- Failure flow: a consumer exception that survives retry moves the message to
  the endpoint's `<queue>_error` queue, with the exception details in headers,
  and produces a `Fault<T>` (published, or sent to the `FaultAddress` /
  `ResponseAddress` header when present). A message with no matching consumer
  goes to `<queue>_skipped`. `DiscardFaultedMessages()` and
  `DiscardSkippedMessages()` change that per endpoint.

## Idioms & best practices
- Define message contracts as plain types (records) shared between producer
  and consumer, not transport payloads. Treat them as the boundary between
  services.
- One consumer per queue is upstream's default and recommendation: each
  consumer gets its own prefetch, concurrency, retry and outbox, and a slow
  consumer does not hold up others. Group consumers on one queue only when they
  share throughput and retry needs; shared definitions can stack duplicate
  middleware.
- Use retry for short transient faults and redelivery for faults that need
  minutes. Upstream calls an hour-long retry interval "bad things": retry runs
  in memory and keeps the message locked, so a consumer with a concurrency
  limit of five and five retrying messages is stalled for the whole interval.
- Pair each retry policy with an explicit `Ignore<T>()` (or `Handle<T>()`)
  list, so a deterministic failure (a validation error, a malformed payload)
  goes straight to the error queue instead of through every attempt.
- Call `UseMessageRetry` at the receive-endpoint level (or in
  `AddConfigureEndpointsCallback`) rather than the bus level, which keeps the
  filter order right when combined with the outbox and redelivery.
- Use an outbox whenever a consumer changes state and publishes. Retry and
  redelivery decide when the work runs again; only an outbox decides when its
  messages become visible. Consumers stay idempotent regardless: delivery is at
  least once.
- In an API or service that writes to the database and publishes outside a
  consumer, use the bus outbox, so the message is written with the data in the
  same `SaveChangesAsync` and delivered by the background delivery service.
- Keep each saga's persistence and its consumer outbox on the same
  `DbContext`.
- Leave the naming conventions alone unless an interop reason forces a
  name; one overridden endpoint breaks the predictability of the rest.

## General pitfalls
- **A retry policy without an ignore list spends its whole schedule on
  failures that cannot succeed.** A permanent exception is retried until the
  limit, holding a concurrency slot for every interval, and only then reaches
  the error queue. With long exponential intervals that stalls the endpoint.
- **Publishing before any consumer has started loses messages.** A publish
  creates the message-type exchange, but until a consumer's bus has started
  once there is no queue bound to it, and RabbitMQ drops the message. After
  the first start the durable queue stays bound, even while the consumer is
  stopped.
- **`AddEntityFrameworkOutbox` alone is neither outbox.** Without
  `UseBusOutbox()`, `IPublishEndpoint` and `ISendEndpointProvider` outside a
  consumer still deliver straight to the broker, not through the database.
  Without `UseEntityFrameworkOutbox` on the receive endpoints there is no
  consumer outbox and no inbox duplicate detection. Two services can therefore
  register the same package with different guarantees; check which side of
  the commit a publish happens on before reasoning about delivery.
- **Outbox tables live in the application's database.** They are mapped into
  the `DbContext` and created by its migrations, so a schema or permission
  change to that database also affects message delivery. When several
  `DbContext` types share one database, map their outbox tables to unique
  names (`AddTransactionalOutboxEntities(x => x.ToTable(...))`) and pass
  `false` to `UsePostgres` / `UseSqlServer` to disable lock-statement caching,
  which is keyed by entity type and would otherwise reuse another context's
  statement. Several bus outboxes on one bus need
  `IScopedBusOutbox<TDbContext>` or `UseDefaultEntityFrameworkBusOutbox<T>()`
  (v9.2), because MassTransit cannot infer which context a scoped publish
  belongs to.
- **The bus-outbox mode is fixed when the scope resolves its first scoped
  MassTransit service.** Changing `IBusOutboxContext.Mode` afterwards has no
  effect.
- **`ConfigureEndpoints` must come last.** Upstream says to call it after all
  settings and middleware, and, when receive endpoints are configured by hand,
  after them or not at all.
- **Delayed redelivery on RabbitMQ needs the delayed-exchange plugin** for
  `UseDelayedRedelivery`. Without plugins, `UseQueueBasedDelayedRedelivery`
  (v9.1) uses TTL queues and dead-letter exchanges instead; it needs an
  interval policy, creates one queue per distinct interval, and all endpoints
  using it must share one queue type (classic or quorum), or startup throws a
  `ConfigurationException`.
- **Select-style test assertions wait for the full test timeout** unless the
  query is limited (for example with `.FirstOrDefault()`), which upstream
  notes means 50 minutes while debugging.

## Testing
- The test harness: `new ServiceCollection().AddMassTransitTestHarness(x =>
  x.AddConsumer<T>()).BuildServiceProvider(true)`, then `await
  provider.StartTestHarness()`. It uses the in-memory transport, a delayed
  message scheduler and `ConfigureEndpoints` by default, and stops when the
  provider is disposed.
- Assert through the harness's asynchronous collections:
  `await harness.Consumed.Any<T>(filter)`, `Published.Any<T>()`,
  `Sent.SelectAsync<T>().FirstOrDefault()`. They are backed by a test timer
  and an inactivity timer, so use one harness per scenario.
- `harness.Act(...)` (v9.1) runs the actions and returns completed results,
  so negative assertions ("not consumed") return at once instead of waiting
  out the timeouts.
- The harness accepts any transport, so an integration test can run the real
  RabbitMQ transport against a broker in a container; the unit-level default
  is in-memory.
- A consumer that publishes is tested the way upstream's consumer guide does
  it: publish the input through `harness.Bus`, then assert
  `Consumed.Any<TInput>()` and `Published.Any<TEvent>()`.

## Security defaults
- The minimal configuration uses `guest:guest` on `localhost`, the broker's
  defaults; the RabbitMQ broker only lets `guest` connect from localhost
  (`RabbitMQ.Client.md`). Give each service its own broker user and supply the
  password from a secret store.
- TLS is opt-in: upstream's minimal configuration is plain AMQP, and its
  hosted-broker examples turn TLS on with `h.UseSsl(...)` or an `amqps://`
  host URI.
- The outbox tables store whole message bodies and headers in the database, so
  whatever a message carries (personal data included) is persisted there and
  in its backups. Keep payloads to identifiers where you can.
- A v9 licence key is a secret: upstream says never to commit it or bake it
  into an image, and to inject it at run time (`MT_LICENSE`,
  `MT_LICENSE_PATH`, or `SetLicense` / `SetLicenseLocation` on the bus
  configurator).
- Queue-based delayed redelivery shares its `mt-delay-*` exchanges and queues
  across applications on one virtual host; `DelayPrefix` (v9.2.2) isolates an
  application's delay topology so its broker permissions can be narrowed.

## Operational behaviour
- Startup: the hosted service starts the bus. With the default
  `WaitUntilStarted = false`, the application reports started while the
  broker connection is still being made, and with no `StartTimeout` it keeps
  trying for ever. On first start MassTransit declares exchanges, queues and
  bindings for every endpoint; `RabbitMqEntityCacheDefaults.
  TopologyConcurrencyLimit` (v9.2.2, process-wide, set before configuring the
  bus) limits concurrent declarations when there are many endpoints.
- Shutdown: the bus waits for in-flight consumers (`StopTimeout`);
  `ConsumerStopTimeout` cancels `ConsumeContext.CancellationToken` after a
  delay so long consumers can observe it.
- Transactional outbox: a hosted service removes delivered `InboxState` rows
  once `DuplicateDetectionWindow` has passed (one instance suffices, and it can
  be disabled where another service runs it). With the bus outbox, a second
  hosted delivery service polls `OutboxMessage`, delivers in order per outbox
  (`ConcurrentDeliveryLimit` defaults to 1 to keep order) and uses
  `OutboxState` to lock so several instances coexist; `DisableDeliveryService()`
  moves delivery elsewhere.
- Durable entities keep routing while a consumer is down: messages queue and
  are consumed when the bus restarts.
- Faulted messages in `_error` queues can be inspected and moved back with the
  RabbitMQ management UI and the shovel plugin.

## Interop
- `RabbitMQ.Client.md`: the AMQP client underneath. From 8.3.2 MassTransit
  uses the 7.x client, and `ConfigureBatchPublish` is deprecated with that move.
- `Microsoft.EntityFrameworkCore.md`: the outbox tables arrive through the
  application's own migrations; the outbox's `IsolationLevel` and lock
  provider must suit the database engine.
- `OpenTelemetry.Extensions.Hosting.md`: traces come from the
  `DiagnosticHeaders.DefaultListenerName` activity source and metrics from
  the `InstrumentationOptions.MeterName` meter; add both to the providers.
- Other platforms: MassTransit wraps each message in an envelope before it
  serializes it, with `System.Text.Json` as the default serializer (Newtonsoft
  was the default before the 8 line). A non-.NET producer or consumer either
  reads and writes that envelope or the shared endpoints use
  `UseRawJsonSerializer`. Exchanges are named after .NET types, so agree the
  names too.

## Major lines

### 8.x line
- Apache-2.0 licensed, published to NuGet under that licence; no licence key.
- 8.3.0 adds the RabbitMQ reply-to request client
  (`SetRabbitMqReplyToRequestClientFactory`) and `AddConfigureEndpointCallback`
  on endpoint configuration; 8.3.2 moves to the 7.x `RabbitMQ.Client`.

### 9.x line
- A commercial licence is required. The key is configured through
  `MT_LICENSE`, `MT_LICENSE_PATH`, `SetLicense` or `SetLicenseLocation`, and
  is validated locally with no call home. A version released while a
  subscription is active keeps running after it expires; MassTransit logs a
  warning and does not stop. Only an upgrade to a later release needs a current
  key.
- 9.0: `IScopedBus` and message routes; `AddSendEndpointConvention` becomes
  `AddMessageRoute` (9.0.1); serializer settings are per bus or endpoint, no
  longer global; `TransactionalBus` is deprecated (removed in 9.2).
- 9.1: transactional outbox for MultiBus and Kafka, `[SkipOutbox]`,
  queue-based delayed redelivery on RabbitMQ, the harness `Act` method. The
  outbox table schema changed in 9.1: apply the migration before rolling out.
- 9.2: bus-outbox control per scope or request (`EnableBusOutbox` /
  `DisableBusOutbox`, `ITransactionalOutbox`), several EF bus outboxes per bus,
  and a behaviour change: inside a MultiBus consumer, `IPublishEndpoint` and
  `ISendEndpointProvider` now follow the consuming bus instead of the default
  one.
- Moving from 8 to 9 is a licensing decision as much as an upgrade; read the
  change log for the release you target.

## Upstream docs
- https://masstransit.massient.com/
- https://masstransit.massient.com/configuration/transports/rabbitmq/
- https://masstransit.massient.com/configuration/
- https://masstransit.massient.com/concepts/exceptions/
- https://masstransit.massient.com/configuration/middleware/retry/
- https://masstransit.massient.com/configuration/middleware/redelivery/
- https://masstransit.massient.com/concepts/outbox/
- https://masstransit.massient.com/configuration/middleware/outbox/
- https://masstransit.massient.com/guides/unit-testing/
- https://masstransit.massient.com/configuration/license/
- https://masstransit.massient.com/reference/change-log/
- https://github.com/MassTransit/MassTransit
- https://www.nuget.org/packages/MassTransit.RabbitMQ
