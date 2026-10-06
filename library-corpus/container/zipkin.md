# zipkin — container

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a tool, not a record of one
> project's versions. For exact pins, advisories and per-release behavior, run
> `ingest-library` against the project's own image tag. This page covers the
> server; the tracers that send to it (Brave, Micrometer Tracing, Spring Cloud
> Sleuth) are client libraries with their own pages.

## What it is
Zipkin is a distributed tracing system: it collects span timing data, lets an
operator look traces up by trace ID or by service, span name, tag and duration,
and draws a service dependency diagram. Home: the `openzipkin/zipkin`
repository (Apache-2.0) and zipkin.io; the repository READMEs are the manual,
with no versioned docs site. The server ships as two images, both also on
`ghcr.io/openzipkin/`:

- `openzipkin/zipkin`: UI, API and every collector.
- `openzipkin/zipkin-slim`: the smaller image, with UI and API, memory or
  Elasticsearch storage, and HTTP and gRPC collectors only.

It listens on 9411 and serves the UI at `/zipkin`.

Model: tracers inside the applications propagate IDs in request headers (IDs
only, never the operation name) and report finished spans out of band and
asynchronously to a collector; the collector writes to storage; the query API
serves the UI. Upstream supports only the released packaged server, not a
server embedded in or repackaged into another application. It is a volunteer
project with no SLA and no published support window.

## Install, setup and configuration
- **Quick start.** `docker run -d -p 9411:9411 openzipkin/zipkin`, or the
  executable jar (Java 17 or later) with `java -jar zipkin.jar`. One server
  README section still says Java 8; the module intro and the 3.0 release notes
  say 17.
- **Image runtime.** Alpine base with few utilities, a no-login user `zipkin`
  with home `/zipkin`. `JAVA_OPTS` sets heap and trust store; the default
  maximum heap is 64m in `zipkin` and 32m in `zipkin-slim`. Upstream's compose
  example raises it with `-Xms128m -Xmx128m -XX:+ExitOnOutOfMemoryError`. Extra
  server flags go in the container `command:` (for example
  `--logging.level.zipkin2=DEBUG`).
- **Configuration is environment variables**, mapped to Spring properties by
  the server's shared YAML (property names upper-cased with underscores, such
  as `ZIPKIN_UI_QUERY_LIMIT`). A properties file or system properties work but
  are self-supported.
- **Server settings and defaults.** `QUERY_PORT` 9411; `QUERY_ENABLED` true
  (false also disables the UI); `SEARCH_ENABLED` true (false leaves only
  lookup by trace ID); `UI_ENABLED` true; `QUERY_TIMEOUT` 11s; `QUERY_LOOKBACK`
  24h (for the service and span name lists); `QUERY_NAMES_MAX_AGE` 300s;
  `COLLECTOR_SAMPLE_RATE` 1.0 (keep everything); `AUTOCOMPLETE_KEYS` and
  `AUTOCOMPLETE_TTL`.
- **Storage** (`STORAGE_TYPE`):
  - `mem` (the default when unset): spans purged oldest first above
    `MEM_MAX_SPANS` (500000); meant for tests and quick starts.
  - `elasticsearch` (Elasticsearch and OpenSearch): `ES_HOSTS`
    (`http://localhost:9200`), `ES_INDEX` prefix `zipkin` with daily indices,
    `ES_INDEX_SHARDS` 5, `ES_INDEX_REPLICAS` 1, `ES_ENSURE_TEMPLATES` true,
    `ES_USERNAME`/`ES_PASSWORD` or a reloaded `ES_CREDENTIALS_FILE`.
  - `cassandra3`: `CASSANDRA_CONTACT_POINTS`, `CASSANDRA_LOCAL_DC`,
    `CASSANDRA_KEYSPACE` (`zipkin2`), `CASSANDRA_ENSURE_SCHEMA` true,
    credentials and SSL options.
  - `mysql`: legacy, not recommended for production, schema applied by hand.
- **Collectors.** HTTP is on (`COLLECTOR_HTTP_ENABLED`), gRPC
  (`zipkin.proto3.SpanService/Report`) on the same port
  (`COLLECTOR_GRPC_ENABLED`). Setting one variable turns on a message
  collector: `KAFKA_BOOTSTRAP_SERVERS` (topic and group `zipkin`),
  `RABBIT_ADDRESSES`, `ACTIVEMQ_URL`, `PULSAR_SERVICE_URL`.
- **UI settings** (`ZIPKIN_UI_*`): `BASEPATH` (default `/zipkin`; set it
  behind a reverse proxy that serves another prefix), `DEFAULT_LOOKBACK` (15
  minutes), `QUERY_LIMIT` (10), `LOGS_URL` (link out to a log system),
  `ENVIRONMENT`, archive URLs and the dependency-graph options.
- **CORS.** Every `/api/v2` endpoint allows any origin by default;
  `ZIPKIN_QUERY_ALLOWED_ORIGINS` narrows it.
- **Optional Eureka registration** when `EUREKA_SERVICE_URL` is set (set
  `EUREKA_HOSTNAME` to the container's name under Compose). The registration
  carries host and port only, so tracers that discover it must append
  `/api/v2/spans`.

## Core API / usage shape
```
POST /api/v2/spans                              # JSON or protobuf; 202 Accepted
GET  /api/v2/services                           # services that have reported
GET  /api/v2/spans?serviceName=S
GET  /api/v2/traces?serviceName=S&limit=1       # filters: spanName, remoteServiceName,
                                                #   annotationQuery, minDuration/maxDuration (µs),
                                                #   endTs/lookback (ms), limit (10)
GET  /api/v2/trace/{traceId}                    # 16 or 32 lowercase hex
GET  /api/v2/dependencies?endTs=...&lookback=...
GET  /health   /info   /metrics   /prometheus   /config.json
```
The v1 ingest path is still accepted. `annotationQuery` reads like
`http.uri=/foo and retried`.

## Idioms & best practices
- **Pick storage before you rely on traces.** Memory is for tests; a trace
  store someone will read during an incident needs Elasticsearch, OpenSearch
  or Cassandra, sized for the retention you want.
- **Size the heap whenever memory storage is used.** Set `JAVA_OPTS` and keep
  `MEM_MAX_SPANS` inside it; add `-XX:+ExitOnOutOfMemoryError` so an
  exhausted server restarts instead of hanging.
- **Prove export with an external witness.** Observed in practice: send a
  deliberate request through the service, then read
  `GET /api/v2/services` and `GET /api/v2/traces?serviceName=<id>&limit=1`, and
  compare the newest trace timestamp with the container's start time. Idle
  services emit nothing, so absence before a request proves nothing.
- **Sample deliberately.** Most tracers sample at the client;
  `COLLECTOR_SAMPLE_RATE` samples again at the server. Self-tracing
  (`SELF_TRACING_ENABLED=true`) is for diagnosing the server, at a low rate
  in production.
- **Decide how operators reach the UI.** Observed in practice: an unpublished
  9411 with no proxy route meant nobody ever read the traces.
- Use `SEARCH_ENABLED=false` when trace IDs always come from logs; it removes
  the search load and keeps lookup by ID.

## General pitfalls
- **Memory storage forgets.** Every restart erases all traces. Observed in
  practice: under a container memory limit, growth with traffic ended in an
  out-of-memory restart loop that lost the evidence; upstream bounds memory by
  `MEM_MAX_SPANS` and the heap and says to lower one or raise the other.
  Capture readings at measurement time.
- **Names age out of the dropdown.** Service and span lists look back only
  `QUERY_LOOKBACK` (24h), so a quiet service vanishes from the list while its
  traces remain.
- **Collector outages are silent to the application.** Reporting is
  asynchronous and out of band, so the client keeps working while spans are
  dropped (observed in practice; consistent with the architecture page).
  Watch the collector's `/metrics` counters (`spans_dropped`,
  `messages_dropped`).
- **The slim image refuses** Cassandra, MySQL and the message collectors.
- **Index auto-creation off breaks Elasticsearch storage.** Zipkin creates its
  daily indices itself; a cluster with `action.auto_create_index: false`
  blocks it. `ES_INDEX_REPLICAS=0` is discouraged.
- **The dependency graph stays empty** on Cassandra and Elasticsearch until a
  separate dependency-aggregation job runs.
- **Mixed trace-ID widths.** `STRICT_TRACE_ID=false` matches only the
  right-most 16 hex characters; use it only during a 64-to-128-bit migration.
- Legacy container-link environment variables are unsupported.

## Testing
Upstream gives no consumer test guide; it ships demo compose files (memory,
Cassandra, Elasticsearch, Kafka, ActiveMQ) and per-backend test images for
client authors. Usable checks:
- `GET /health` returns 200 and `/info` the version;
- after a deliberate request, `/api/v2/services` lists the service and
  `/api/v2/traces?serviceName=<id>&limit=1` returns a trace newer than the
  container start (observed in practice as the export proof);
- collector counters in `/metrics` show spans accepted per transport.

## Security defaults
- **No authentication** on ingest or query: the server docs describe
  credentials only for storage and broker connections. Access control comes
  from the network or a proxy in front.
- CORS on `/api/v2` is open by default; narrow it.
- TLS is off; it can be enabled through the server's Armeria properties
  (`--armeria.ssl.*`) with a key store.
- `/metrics` and `/prometheus` are on the same unauthenticated port.
- Spans can carry tags with request data; what a tracer records is the
  tracer's configuration, so check it before treating traces as non-sensitive.
- The images run as a non-login user. Upstream has no dedicated security team
  and gives no warranty.

## Operational behaviour
- Health at `/health`, version at `/info`, Prometheus scrape at `/prometheus`.
- Memory use follows the storage type: in-memory storage holds every span up
  to the cap inside the JVM heap.
- Logs go to the console at INFO.
- Releases are irregular; image updates also move the bundled JRE, so re-test
  after a tag change.
- A trace archive is a second server on longer-retention storage, linked from
  the UI through the archive URL settings.

## Interop
- Tracers: Brave (Java), Micrometer Tracing (Spring Boot 3 and later, B3 and
  W3C propagation), Spring Cloud Sleuth (older Spring lines), zipkin-go,
  zipkin-js and others. Observed in practice: OpenTelemetry exporters also
  report to it; the fetched upstream pages do not list them.
- Prometheus scrapes `/prometheus` on 9411:
  [`container/prometheus.md`](prometheus.md).
- `ZIPKIN_UI_LOGS_URL` links a trace to a log system.
- Eureka registration and Kafka, RabbitMQ, ActiveMQ and Pulsar collectors as
  configured above.

## Major lines
### 2.x to 3.x
The server moved to Spring Boot 3 and a Java 17 floor, and the core library
target moved from Java 6 to Java 8; Java 6 users stay on 2.x or use the
reporter library.

### Within 3.x
Images moved to newer LTS JREs over the line, and Elasticsearch 7 left the
tested set even though one server README section still lists it: treat
Elasticsearch 8 and 9 and OpenSearch 2 as the tested backends.

## Upstream docs
- https://github.com/openzipkin/zipkin (README)
- https://github.com/openzipkin/zipkin/blob/master/zipkin-server/README.md
- https://github.com/openzipkin/zipkin/blob/master/docker/README.md
- https://github.com/openzipkin/zipkin-api/blob/master/zipkin2-api.yaml
- https://zipkin.io/pages/architecture.html
- https://zipkin.io/pages/tracers_instrumentation.html
