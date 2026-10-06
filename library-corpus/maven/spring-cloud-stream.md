# spring-cloud-stream — maven

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions: for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
A framework for message-driven microservices on a message broker, built on
Spring Boot and Spring Integration. Application code produces and consumes
messages through bindings, and a pluggable "binder" maps them onto a concrete
broker: RabbitMQ, Apache Kafka, Kafka Streams and Apache Pulsar upstream, plus
partner binders (Solace, Azure Event Hubs, Google PubSub). Coordinates, all
versioned by the Spring Cloud train BOM
([`spring-cloud.md`](./spring-cloud.md)): the core
`org.springframework.cloud:spring-cloud-stream`, the Rabbit binder
`org.springframework.cloud:spring-cloud-stream-binder-rabbit` or the starter
`org.springframework.cloud:spring-cloud-starter-stream-rabbit` (core plus
binder), and the test binder
`org.springframework.cloud:spring-cloud-stream-test-binder`. This page covers
the core and the Rabbit binder; [`rabbitmq.md`](./rabbitmq.md) covers the
broker and Spring AMQP. Upstream home:
https://docs.spring.io/spring-cloud-stream/reference/, source on GitHub
`spring-cloud/spring-cloud-stream`.

## Install, setup and configuration
- The Rabbit binder uses Spring Boot's `ConnectionFactory`, so every
  `spring.rabbitmq.*` option applies; binder-only keys live under
  `spring.cloud.stream.rabbit.binder.*`.
- **Binding properties:** `spring.cloud.stream.bindings.<bindingName>.*`, with
  `.consumer.*` and `.producer.*` subtrees; defaults for all bindings under
  `spring.cloud.stream.default.consumer|producer.*`; Rabbit-specific ones
  under `spring.cloud.stream.rabbit.bindings.<bindingName>.consumer|producer.*`.
- `destination` defaults to the binding name. `group` (inbound only) defaults
  to null, an anonymous consumer. `contentType` defaults to
  `application/json`.
- **Consumer retry defaults:** `maxAttempts` 3 (the first attempt included; 1
  turns retry off), `backOffInitialInterval` 1000 ms, `backOffMaxInterval`
  10000 ms, `backOffMultiplier` 2.0, `defaultRetryable` true; `concurrency` 1;
  `autoStartup` true.
- **Producer `requiredGroups`:** groups the producer guarantees delivery to even
  if they start later, by pre-creating their durable queues on RabbitMQ.
- **Rabbit consumer defaults:** `acknowledgeMode` AUTO, `autoBindDlq` false,
  `requeueRejected` false, `republishToDlq` true, `durableSubscription` true
  (with a `group`), `exchangeType` topic, `prefetch` 1, `recoveryInterval`
  5000 ms, `missingQueuesFatal` false (the container keeps retrying),
  `quorum.enabled` false, DLQ name `<prefix><destination>.dlq`; producers send
  PERSISTENT messages.
- **Function selection:** `spring.cloud.function.definition` names the
  functional beans to bind. With exactly one `Supplier`, `Function` or
  `Consumer` bean it can be left out (auto-discovery), but the docs call
  setting it best practice, and with several functional beans it must be set.
  `spring.cloud.stream.function.autodetect=false` turns auto-discovery off.

## Core API / usage shape
- **Functional model:** handlers are `java.util.function.Supplier`, `Function`
  or `Consumer` beans. Binding names follow `<functionName>-in-<index>` and
  `<functionName>-out-<index>` (index 0 for a single input or output), for
  example `spring.cloud.stream.bindings.uppercase-in-0.destination=my-topic`.
- **Renaming:** `spring.cloud.stream.function.bindings.<implicit-name>=<explicit-name>`
  renames a binding; the docs advise against it except for function
  composition, because it adds indirection.
- **`StreamBridge.send(bindingName, payload)`** sends from non-stream code (a
  POJO or a `Message`, with output conversion and partitioning applied). An
  unknown binding is created on the first send, destination provisioning
  included, and cached; pre-create bindings at startup with
  `spring.cloud.stream.output-bindings=foo;bar` (the 3.2 docs used
  `spring.cloud.stream.source` for this and also list `output-bindings`). The dynamic-destination cache holds 10 bindings by default.
  Bindings created by `StreamBridge` are not in the application context, so
  binding control cannot manage them unless created explicitly first.
- **Consumer groups:** every group on a destination gets a copy, and one member
  per group handles each message; without a group the application is an
  anonymous single-member group.
- **Rabbit mapping:** each destination is a `TopicExchange`; each consumer
  group a queue bound to it; an anonymous consumer gets an auto-delete queue
  named `anonymous.<base64 UUID>`.
- Payloads are converted to and from the domain type by message converters.

## Idioms & best practices
- Set `spring.cloud.function.definition` even with one handler, so an unrelated
  functional bean is never bound by accident.
- Keep the plain `<fn>-in-0` names in configuration so the link between binding
  and destination stays readable.
- Always set a consumer `group`; pre-create output bindings that must exist at
  startup, and list `requiredGroups` on producers that may publish before
  consumers exist.
- Bind a DLQ (`autoBindDlq=true`) on every consumer that must not lose
  messages.
- Keep application code broker-agnostic: swapping brokers should mean changing
  the binder dependency and configuration, not business logic.
- Observed in practice: consuming `Message<byte[]>` and decoding JSON in the
  handler makes the wire contract bytes plus a JSON shape, independent of each
  end's framework generation (producers on an older train fed consumers on a
  much newer one this way). Converter-bound domain types couple both ends to
  converter behaviour; with bytes, a malformed payload fails inside the handler
  instead. Upstream documents the `Message<byte[]>` path but says nothing about
  cross-generation compatibility.

## General pitfalls
- **No `group` on a Rabbit consumer** means an anonymous auto-delete queue:
  messages published while the consumer is down are lost, and no DLQ can be
  named.
- **`group` on a producer does nothing;** only `producer.requiredGroups`
  pre-creates the group's queue, so messages sent before the consumer's queue
  exists otherwise have nowhere to land.
- **The default failure path drops.** After 3 attempts the default error
  handlers log and drop the message unless a binder DLQ is configured; the docs
  say this is not acceptable in most cases. A consumer that always throws does
  not loop by default; a loop needs the next pitfall.
- **`requeueRejected=true` with `republishToDlq=false`** requeues and redelivers
  a poison message forever.
- **A custom `error-handler-definition`** replaces the framework handlers, so a
  configured DLQ stops receiving failed messages.
- **Reactive functions** (`Flux`) get none of the retry, drop or DLQ behaviour;
  handle errors with Reactor operators.
- `ImmediateAcknowledgeAmqpException` bypasses the DLQ and discards the message.
- **No DLQ replay.** The framework has no standard way to consume dead letters
  or route them back; re-routing a permanent failure to the original queue can
  loop forever, so the documented recipe parks a message in a parking-lot queue
  after a number of attempts. Replay is the service's job.
- **`StreamBridge` takes a string.** A typo creates a new binding and
  destination on first use instead of failing, so the message goes where nobody
  consumes (an inference from the creation rule).
- **Naming is load-bearing.** Observed in practice: a mismatch between the bean
  name (or function definition) and the expected `-in-0`/`-out-0` binding name
  fails to wire the handler without an error. Upstream documents the naming
  convention but not this failure mode.
- With several Rabbit binders, exclude `RabbitAutoConfiguration` so its
  configuration is not applied to both.
- Delivery semantics, ordering, partitioning and acknowledgement are the
  binder's and broker's properties; do not assume exactly-once or ordered
  delivery without configuring for it.

## Testing
- Add `spring-cloud-stream-test-binder` (test scope), annotate the test
  configuration with `@EnableTestBinder`, and inject `InputDestination` and
  `OutputDestination` to send and receive without a broker.
  `TestChannelBinderConfiguration.getCompleteConfiguration(...)` builds an
  explicit context. `send` and `receive` take a destination name when there
  are several bindings.
- The test binder replaced the older `spring-cloud-stream-test-support`
  (`MessageCollector`), deprecated on the 3 line.
- Broker-specific behaviour (DLQ routing, confirms, quorum queues) needs a real
  broker, for example a RabbitMQ container; the test binder does not model it.

## Security defaults
- The `bindings` actuator endpoint lists bindings and, through a POST with a
  `state` of STOPPED, STARTED, PAUSED or RESUMED, changes them. It needs web
  and actuator on the class path and
  `management.endpoints.web.exposure.include=bindings`; Boot exposes only
  `health` by default. Never expose `bindings` publicly.
- **Publisher confirms are off** unless the connection factory sets
  `spring.rabbitmq.publisher-confirm-type=correlated`; then use
  `producer.useConfirmHeader=true` (preferred) or the legacy
  `confirmAckChannel`, whose default `nullChannel` discards acks. Without
  confirms, a send the broker never accepted is not reported to the producer
  (an inference; the binder docs do not state it, and
  [`rabbitmq.md`](./rabbitmq.md) has the broker side).

## Operational behaviour
- The Rabbit binder publishes on a separate connection
  (`usePublisherConnection`), so producers do not block consumers when a broker
  memory alarm blocks connections.
- With `transacted` consumers the DLQ publish joins the transaction; with
  confirms or returns on, the DLQ publish waits for the confirm and a nack
  throws `AmqpRejectAndDontRequeueException`, so the broker dead-letters
  instead.
- `republishToDlq=true` adds headers such as `x-exception-stacktrace`; long
  traces are truncated to fit the frame (`frameMaxHeadroom`).
- Queues are classic unless `quorum.enabled=true` (`dlqQuorum.enabled=true` for
  the DLQ); a quorum queue's delivery limit is the broker's default.

## Interop
- Boot `spring.rabbitmq.*` for the connection, Spring AMQP for the listener
  container and `RabbitTemplate` ([`rabbitmq.md`](./rabbitmq.md)), Spring Cloud
  Function for the functional model and composition with `|`, Boot Actuator
  for `bindings` and the binder health indicator, the Spring Cloud BOM for
  versions.

## Major lines
### Stream 3 (Boot 2 era; train 2021.0)
- The functional model is recommended and the annotation model
  (`@EnableBinding`, `@StreamListener`) is deprecated;
  `spring-cloud-stream-reactive` is discontinued; `BinderAwareChannelResolver`
  is deprecated in favour of `spring.cloud.stream.sendto.destination`; the
  test-support binder is replaced. Its docs pre-create with
  `spring.cloud.stream.source` and already list `output-bindings`.

### Stream 4 (trains 2022.0 to 2025.0, Boot 3)
- Java 17, Boot 3, Framework 6 baseline. The annotation model is removed, so
  code on `@EnableBinding`/`@StreamListener` must be rewritten to functions.
  `BinderAwareChannelResolver` is gone, binding-specific error-channel naming
  changed, and a dedicated reactive Kafka binder appears. The current docs
  pre-create with `spring.cloud.stream.output-bindings`.

### Stream 5 (train 2025.1, Boot 4)
- Breaking changes for Jackson 3, JSpecify nullability, Framework 7 and Boot 4.

## Upstream docs
- https://docs.spring.io/spring-cloud-stream/reference/
- https://docs.spring.io/spring-cloud-stream/reference/rabbit/rabbit_overview.html
- https://github.com/spring-cloud/spring-cloud-stream
- https://github.com/spring-cloud/spring-cloud-stream/wiki
