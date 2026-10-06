# rabbitmq — maven

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions: for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
RabbitMQ is an AMQP message broker for asynchronous, decoupled messaging
between services. Producers publish to an exchange, which routes messages to
queues according to bindings, and consumers subscribe to the queues. JVM
services connect through the Java client `com.rabbitmq:amqp-client` (and
`com.rabbitmq:stream-client` for streams), usually through Spring AMQP,
`org.springframework.amqp:spring-rabbit` on top of
`org.springframework.amqp:spring-amqp`, added with the Boot starter
`org.springframework.boot:spring-boot-starter-amqp`. Boot manages all of these
versions. Spring AMQP gives a template for sending and receiving and
message-driven POJOs (`@RabbitListener`); Spring Cloud Stream is a further
layer ([`spring-cloud-stream.md`](./spring-cloud-stream.md)). Upstream homes:
https://www.rabbitmq.com/docs (broker), https://docs.spring.io/spring-amqp/reference/
(Spring AMQP), https://docs.spring.io/spring-boot/reference/messaging/amqp.html
(Boot). The broker's release-information page lists each series with its
community and commercial support windows; community support is short (months),
so read the page rather than assuming.

## Install, setup and configuration
- **Boot connection** (`spring.rabbitmq.*`): `host` `localhost`, `port` 5672
  (5671 with SSL), `username` and `password` `guest`, `virtual-host`;
  `addresses` overrides host and port, and an `amqps://` address turns SSL on.
- Boot auto-configures `AmqpTemplate`, `AmqpAdmin` (`spring.rabbitmq.dynamic`,
  default true) and `RabbitMessagingTemplate`. A `MessageConverter` bean is
  applied to the template and the default listener factory, and every `Queue`
  bean is declared on the broker.
- **Boot defaults:** `template.retry.enabled` false; `listener.type` simple;
  `listener.simple.retry.enabled` false; `listener.simple.missing-queues-fatal`
  true; `publisher-returns` false; `publisher-confirm-type` unset (no
  confirms); `requested-channel-max` 2047; `max-inbound-message-body-size`
  64MB; `connection-timeout` has no Boot default (the client's applies), and
  0 waits forever.
- **Spring AMQP listener container defaults:** `acknowledgeMode` AUTO (the
  container acks after the listener returns and rejects if it throws),
  `defaultRequeueRejected` true, `prefetchCount` 250 (1 restores the pre-2.0
  behaviour), `ConditionalRejectingErrorHandler` as the error handler.
- **Broker users:** a fresh node creates `guest`/`guest` with full permissions
  on `/`, and `loopback_users` lists `guest` by default, so it may log in only
  over loopback.
- **Official Docker image:** it ships `/etc/rabbitmq/conf.d/10-defaults.conf`
  with `loopback_users.guest = false` ("allow access to the guest user from
  anywhere on the network") under a header saying the defaults are not meant
  for production. `RABBITMQ_DEFAULT_USER`/`RABBITMQ_DEFAULT_PASS` replace
  `guest`.
- **Management plugin:** UI and HTTP API on port 15672 (an HTTPS listener can be
  configured); it does not speak AMQP.

## Core API / usage shape
- **Exchanges** route by type: direct (exact routing key), topic (routing-key
  patterns), fanout (all bound queues) and headers (message attributes).
  Bindings connect an exchange to a queue, so routing changes are binding
  changes, not producer code.
- **Send** with `AmqpTemplate`/`RabbitTemplate.convertAndSend(...)`; **receive**
  with `@RabbitListener(queues = "...")` on a bean. Boot supplies a
  `SimpleRabbitListenerContainerFactory`, and its configurer builds more
  factories with the same settings.
- **Acknowledgement:** with manual or container-managed acks a message is
  removed only after the consumer confirms it, so a crash mid-work redelivers
  instead of losing it.
- **Publisher confirms and returns:** `publisherConfirmType` `CORRELATED` and
  `publisherReturns` true on the connection factory (Boot:
  `spring.rabbitmq.publisher-confirm-type=correlated`,
  `publisher-returns=true`); returns also need `mandatory`
  (`spring.rabbitmq.template.mandatory`). The broker confirms an unroutable
  message once it knows no queue matches (with `mandatory`, a `basic.return`
  comes first), and a routable one once every queue has accepted it.
- **Queue types:** classic (single replica on 4.x), quorum (replicated, Raft)
  and streams.
- **Dead-letter exchanges** capture rejected, expired and over-limit messages,
  so poison messages are quarantined instead of blocking a queue.

## Idioms & best practices
- Prefer Spring AMQP or Spring Cloud Stream to the raw client for ordinary
  producers and consumers; drop to the raw client only for what the
  abstraction cannot express.
- Delete `guest` in production and create users with generated credentials
  (CLI, definitions file or HTTP API); use a vhost per tenant or environment.
- Use quorum queues or streams for data that must survive a node failure.
- Configure a dead-letter exchange (by policy) for queues whose consumers can
  fail, and keep consumers idempotent: delivery is at least once, and a
  producer using confirms retransmits unconfirmed messages, which can
  duplicate.
- Monitor with Prometheus and Grafana; the management UI keeps recent data only
  ("hours, not days or months").
- Keep `vm_memory_high_watermark.relative` between 0.4 and 0.7 and leave the OS
  at least 30% of memory.

## General pitfalls
- **Infinite redelivery by default in Spring AMQP.** With retries off, a
  listener exception requeues the message and it is redelivered forever. Stop
  it with `defaultRequeueRejected=false` (Boot
  `listener.simple.default-requeue-rejected`) or by throwing
  `AmqpRejectAndDontRequeueException`. With retries on, exhaustion uses
  `RejectAndDontRequeueRecoverer`: the message is rejected and dropped, or
  dead-lettered if the queue has a DLX.
- `ConditionalRejectingErrorHandler` rejects irrecoverable errors (a
  `MessageConversionException`, say) without requeue, and a message carrying
  an `x-death` header that fails fatally is logged and discarded.
- **Autoack loses messages.** Broker "autoack" (Spring AMQP `NONE`) loses
  in-flight messages when the channel closes and has no prefetch bound, so a
  consumer can be flooded. Spring AMQP's `AUTO` is not autoack.
- **A passive declare fails on a cold broker.** `queueDeclarePassive` closes
  the channel with `404 NOT_FOUND` when the queue does not exist yet, and a
  listener on a missing queue stops start-up while `missing-queues-fatal` is
  true. When the producer declares its topology only on
  first use, the consumer crash-loops until then. Declare the queue, exchange
  and binding on the consumer side as well, as `Queue`, `Exchange` and
  `Binding` beans; declaring them again is idempotent while the arguments
  match.
- **Remote `guest` in containers.** A broker from the official Docker image
  accepts remote `guest` logins unless the image default is overridden.
- **Quorum delivery limit.** On 4.x a quorum queue's default delivery limit is
  20; past it a message is dropped, or dead-lettered if a DLX is configured.
  `-1` disables the limit, which upstream advises against.
- **Mirroring policies do nothing on 4.x.** An `ha-mode`/`ha-params` policy
  mirrors nothing; quorum queues are the replicated type.
- **Ordering.** Prefetch 250 raises the chance of out-of-order processing, and
  ordering across several consumers on one queue is never guaranteed.
- **Unbounded queues** with no dead-letter path let one unprocessable message or
  a slow consumer build a backlog that degrades the broker.

## Testing
- `org.springframework.amqp:spring-rabbit-test`: `@SpringRabbitTest` adds the
  infrastructure beans; `@RabbitListenerTest` with `RabbitListenerTestHarness`
  spies on or captures listener calls; `TestRabbitTemplate` tests listeners
  without a broker.
- Boot with Testcontainers: a `RabbitMQContainer` with `@ServiceConnection`
  supplies the connection details.

## Security defaults
- Broker: `guest` is loopback-only; setting `loopback_users = none` "will
  dramatically reduce the security of the cluster". The official Docker image
  reverses the loopback default. In production, delete `guest`.
- Boot's client defaults to `guest`/`guest`; set credentials explicitly.
- Spring AMQP Java deserialization is closed by default: `SimpleMessageConverter`
  and `SerializerMessageConverter` deserialize
  `application/x-java-serialized-object` only for classes on an allowed list
  that is empty by default (a `SecurityException` otherwise).
  `allowedListPatterns` opens it, and so does the system property
  `spring.amqp.deserialization.trust.all` (or the environment variable
  `SPRING_AMQP_DESERIALIZATION_TRUST_ALL`), which is not a Boot property;
  keep it closed for untrusted producers.
- Management UI access is governed by user tags; HTTPS, HSTS and CSP are
  available, not default.

## Operational behaviour
- **Upgrades:** enable all stable feature flags before upgrading, or the
  upgrade may fail. Only the series-to-series jumps on the upgrade page are
  supported; a 3.x broker reaches 4.x only from the last 3.x series, and some
  later 4.x series can be reached only from the series just before them, so
  check the page for the path. Rolling upgrades one node at a time are the
  recommended strategy. Observed in practice: a broker with no data volume
  survived an unsupported jump, because there was no state to migrate; that
  says nothing about a broker with data.
- **4.0 start failures from config:** `classic_queue.default_version = 1` and
  the removed `cluster_formation.randomized_startup_delay_range.*` keys stop a
  4.0 node from starting.
- Quorum queues cap consumer prefetch at 2,000.
- The Boot template `retry` covers connection loss on send and is off by
  default.

## Interop
- Spring Cloud Stream's Rabbit binder reuses Boot's `ConnectionFactory` and
  defaults to classic queues ([`spring-cloud-stream.md`](./spring-cloud-stream.md)).
- Micrometer and Brave instrumentation for Spring Rabbit is BOM-managed; the
  Prometheus plugin exports broker metrics.

## Major lines
### Broker 3.x to 4.x
- Classic queue mirroring removed (mirroring policy keys have no effect;
  classic queues are single-replica); quorum queues get a default delivery
  limit of 20 (it was unlimited); the broker no longer interprets an
  `x-death` header republished by a client; the CQv1 storage format is gone.
- Later 4.x series replace the two-level quorum priority scheme with strict
  priorities and change what counts as a delivery attempt: only genuine
  failures (channel crash, reject, `delivery-failed`), with `x-acquired-count`
  tracking assignments.

### Spring AMQP with Boot
- Spring AMQP majors follow Boot: 2 with Boot 2, 3 with Boot 3, 4 with Boot 4.
  The 4 line adds a generic AMQP 1.0 client module (`spring-amqp-client`).
- Boot 4 names the listener retry key
  `spring.rabbitmq.listener.simple.retry.max-retries` ("maximum number of retry
  attempts", default 3), where Boot 3 has `...retry.max-attempts` ("maximum
  number of attempts", default 3); upstream does not say whether the total
  attempt count changed. Boot 4 moves the auto-configuration to
  `org.springframework.boot.amqp.autoconfigure`.

## Upstream docs
- https://www.rabbitmq.com/docs
- https://www.rabbitmq.com/docs/upgrade
- https://www.rabbitmq.com/docs/queues
- https://www.rabbitmq.com/release-information
- https://docs.spring.io/spring-amqp/reference/
- https://docs.spring.io/spring-amqp/reference/amqp/containerAttributes.html
- https://docs.spring.io/spring-boot/reference/messaging/amqp.html
