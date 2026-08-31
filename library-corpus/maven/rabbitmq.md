# rabbitmq — maven

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
An AMQP message broker used for asynchronous, decoupled messaging between
services. Producers publish messages to an exchange, which routes them to queues
according to bindings, and consumers subscribe to those queues. The broker
itself is the RabbitMQ server; JVM services connect through the Java client
(`com.rabbitmq:amqp-client`), most often via a higher-level abstraction such as
Spring AMQP (`org.springframework.boot:spring-boot-starter-amqp`) or Spring
Cloud Stream rather than the raw client directly.

## Core API / usage shape
- Exchanges route by type: a direct exchange matches an exact routing key, a
  topic exchange matches routing-key patterns, a fanout exchange broadcasts to
  all bound queues, and a headers exchange matches on message attributes.
- Bindings connect an exchange to a queue (with a routing key or pattern);
  changing routing is a matter of bindings, not producer code.
- Consumers acknowledge messages: with manual acknowledgement a message is only
  removed once the consumer confirms successful processing, so a crash mid-work
  redelivers rather than loses the message.
- A dead-letter exchange/queue captures messages that are rejected, expire, or
  exceed retry limits, so poison messages are quarantined instead of blocking a
  queue.

## Idioms & best practices
- Prefer a messaging abstraction (Spring AMQP, Spring Cloud Stream) over the raw
  AMQP client for ordinary producers and consumers; it handles connection
  management, serialization, and listener wiring. Drop to the raw client only
  for the exceptional case the abstraction cannot express.
- Make consumers idempotent: at-least-once delivery means a message can be
  redelivered, so processing the same message twice must be safe.
- Configure dead-lettering for queues that carry work that can fail, so failures
  are observable and recoverable rather than silently retried forever.

## General pitfalls
- Auto-acknowledging on receipt (rather than after successful processing) means a
  consumer crash loses in-flight messages; use manual acknowledgement when
  delivery must be reliable.
- Unbounded queues with no dead-letter path let a single unprocessable message
  or a slow consumer accumulate a backlog that degrades the broker.
- Message ordering is not guaranteed across multiple consumers on a queue; do not
  rely on strict ordering unless the topology is designed for it.

## Upstream docs
- https://www.rabbitmq.com/documentation.html
- https://www.rabbitmq.com/tutorials
- https://docs.spring.io/spring-amqp/reference/
