# spring-cloud-stream — maven

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
A framework for building message-driven microservices on top of a message
broker without programming against the broker's client API directly. Application
code produces and consumes messages through binding abstractions; a pluggable
"binder" maps those bindings onto a concrete broker. Canonical coordinates:
`org.springframework.cloud:spring-cloud-stream` plus one binder dependency for
the target broker (e.g. `spring-cloud-stream-binder-rabbit`).

## Core API / usage shape
- **Bindings** are the named connection points between the application and the
  broker; the binder wires each binding to a broker destination based on
  configuration.
- **Producers** send via `StreamBridge` to a named output binding; the framework
  convention names an output binding `<binding-name>-out-0`.
- **Consumers** are plain `java.util.function.Consumer<T>` beans; the binder
  binds a consumer to an input destination by matching the bean name to the
  binding (functional binding, convention `<binding-name>-in-0`). Functions
  (`java.util.function.Function<T,R>`) act as processors, consuming input and
  producing output.
- Message payloads are converted to/from the domain type via configurable
  message converters.

## Idioms & best practices
- Prefer `StreamBridge` for sends, especially dynamic ones where the target
  binding is chosen at runtime.
- Expose consumers and processors as functional beans (`Consumer`/`Function`)
  and let the binder wire them by naming convention; this is the modern
  functional model that replaces the older annotated
  `@StreamListener`/channel-interface style.
- Keep application code broker-agnostic: swapping brokers should be a matter of
  changing the binder dependency and its configuration, not the business logic.
- Configure consumer groups so multiple instances of a service share a
  subscription rather than each receiving every message.

## General pitfalls
- The binding-name convention is load-bearing: a mismatch between the bean name
  (or configured function definition) and the expected `-in-0` / `-out-0`
  binding name silently fails to wire the consumer or producer.
- Delivery semantics, ordering, and retry/dead-letter behavior are properties of
  the underlying broker and binder, not the abstraction; do not assume
  exactly-once or ordered delivery without configuring for it.
- Because the abstraction hides the broker, it is easy to overlook
  broker-specific operational concerns (partitioning, acknowledgements,
  back-pressure) that still apply beneath it.

## Upstream docs
- https://spring.io/projects/spring-cloud-stream
- https://docs.spring.io/spring-cloud-stream/reference/
- https://mvnrepository.com/artifact/org.springframework.cloud/spring-cloud-stream
