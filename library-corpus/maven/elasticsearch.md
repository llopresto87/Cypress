# elasticsearch — maven

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions: for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
Elasticsearch is a distributed search and analytics server. The cluster is a
separately run service that the application reaches over HTTP; it indexes JSON
documents and answers search and aggregation queries. JVM access comes in
three forms:
- the Java API client `co.elastic.clients:elasticsearch-java` (typed requests
  and responses, blocking and async, Jackson or JSON-B mapping; Java 17 or
  later);
- the low-level REST client `org.elasticsearch.client:elasticsearch-rest-client`;
- Spring Data Elasticsearch, `org.springframework.data:spring-data-elasticsearch`,
  added with `org.springframework.boot:spring-boot-starter-data-elasticsearch`.

Upstream homes: https://www.elastic.co/docs (server and clients; the 7.x and
8.x guides are frozen and cited for their own lines) and
https://docs.spring.io/spring-data/elasticsearch/reference/. Elastic publishes
end-of-maintenance and end-of-support dates per major on its EOL page; read it
rather than assuming a line is supported.

## Install, setup and configuration
- **Binding.** By default the server binds HTTP and transport to loopback only.
- **Development versus production mode.** A node is in production mode when it
  can form a cluster with another machine: transport bound to a non-loopback
  address and no `discovery.type: single-node`. In production mode a failed
  bootstrap check stops startup; in development mode it is a warning (a few
  checks are always enforced). `http.host` and `transport.host` can be set
  separately, so HTTP can be exposed without entering production mode.
- **Kernel.** `vm.max_map_count` must be at least 262144 on the 7.x line; the
  8.x and current docs say 1048576 when the OS default is lower. Too low a
  value fails startup or causes out-of-memory errors.
- **Heap.** The server sizes its heap from node roles and total memory, and
  upstream recommends that default for most production. To override, put a JVM
  options file under `config/jvm.options.d/` (in Docker, bind-mount it into
  `/usr/share/elasticsearch/config/jvm.options.d/`); `ES_JAVA_OPTS` is for
  testing and not recommended in production.
- **Other production settings:** disable swapping (`bootstrap.memory_lock`), at
  least 4096 threads and 65,535 file descriptors, a JNA temp directory not
  mounted `noexec`, a lower `net.ipv4.tcp_retries2`, synchronized clocks, and a
  dedicated unprivileged user.
- **Boot client:** `spring.elasticsearch.uris` defaults to
  `[http://localhost:9200]`, `connection-timeout` 1 s, `socket-timeout` 30 s;
  `username`/`password`; `restclient.sniffer.enabled` false.

## Core API / usage shape
- Index one JSON document per logical record or event; each lives in an index
  and can be retrieved and searched.
- **Spring Data Elasticsearch:** `ElasticsearchOperations`/`ElasticsearchTemplate`
  and repositories. Configure the client by extending `ElasticsearchConfiguration`
  with a `ClientConfiguration` (`connectedTo("host:9200")`).
- `@Document(createIndex = true)` is the default: at repository bootstrap Spring
  Data checks the index and, if it is missing, creates it with mappings derived
  from the entity's `@Field(type = ...)` annotations.
- **Java client transports:** from client 9 the default is `Rest5Client`
  (Apache HttpClient 5); the legacy `RestClient` (HttpClient 4) became optional
  (`elasticsearch-rest-client`, same version).
- **ILM:** `PUT _ilm/policy/<name>` defines phases (hot rollover, delete after
  `min_age`); an index or index template applies it with
  `index.lifecycle.name`. Data streams suit append-only time series.

## Idioms & best practices
- Treat the cluster as a separately owned service, not part of the
  application process.
- Declare retention as an ILM policy applied through `index.lifecycle.name`,
  versioned as configuration, not as rollover code in the application.
- Map fields explicitly (entity annotations, or a mapping document) instead of
  relying on dynamic inference for fields that need a specific type or
  analysis.
- Observed in practice: applying the ILM policy with an idempotent
  `PUT _ilm/policy` at startup, and creating indices with
  `index.lifecycle.name` plus the mapping derived from the annotated model,
  keeps retention declarative. Each step is documented upstream; the startup
  pattern is the practice.
- Keep the automatic heap sizing unless measurements say otherwise.

## General pitfalls
- **Client compatibility is per major.** The Java client is forward compatible
  within one major (it talks to the same or newer minors of that major); a new
  server feature needs a new client, and across majors there is no guarantee.
  REST compatibility headers (`compatible-with=8`) let 8.x-style requests reach
  a 9.x server, as a bridge, not a long-term strategy. Upgrade client and
  server majors together and verify them together.
- **Spring Data ties the client to Boot.** Spring Data Elasticsearch's client
  major follows the Spring Data train, and so the Boot line: late Boot 2
  releases with Spring Data Elasticsearch 4 on Elasticsearch 7 (earlier Boot 2
  releases shipped 3 on Elasticsearch 5 and 6), Boot 3 with 5 on 8, Boot 4 with 6 on
  9. A server major upgrade is then a joint Boot and server move.
- `ClassNotFoundException: jakarta.json.spi.JsonProvider` means a BOM or plugin
  forced `jakarta.json-api` 1.x (javax namespace); declare
  `jakarta.json:jakarta.json-api` 2.x explicitly.
- A client moved from 8 to 9 that keeps the legacy `RestClient` must add
  `elasticsearch-rest-client`, or it stops compiling.
- **Upgrade path:** reach the last 7.x release before going to 8, and the
  latest 8.x release before going to 9, using the Upgrade Assistant (indices
  created before 8.0 need a reindex).
- `cluster.initial_master_nodes` is for the first cluster formation only; a
  single node uses `discovery.type: single-node`.

## Testing
- Boot with Testcontainers: an `ElasticsearchContainer` with `@ServiceConnection`
  supplies the connection details and detects server-side SSL.
- For local development, Elastic's Docker docs give a single-node recipe
  (`discovery.type=single-node`, ports published on 127.0.0.1).
- Upstream gives no further testing guidance for application code; test the
  index mapping and queries against a container of the production major.

## Security defaults
- **7.x (basic licence):** security is off unless `xpack.security.enabled: true`
  is set; upstream says the minimal setup is not enough for production
  clusters, which also need TLS between nodes.
- **8.x and later:** security is on and configured at first start: TLS
  certificates for transport and HTTP, a generated `elastic` password, and a
  Kibana enrollment token valid for 30 minutes. The auto-setup is skipped when
  the node already belongs to a cluster or security is configured or
  explicitly disabled; RPM and Debian installs do not print the password.
- **9.x** removed TLSv1.1 from the default protocols.

## Operational behaviour
- The server assumes it is the only resource-heavy process on its host;
  automatic heap sizing depends on that.
- On 9.x a timed-out request returns 429 instead of a 5xx, and frozen indices
  can no longer be read.

## Interop
- Spring Boot (client auto-configuration, `Rest5Client` with a
  `Rest5ClientBuilderCustomizer`, optional `Sniffer`), Spring Data
  (repositories, operations), Testcontainers, Kibana (enrollment token).
- The server-side facts above (binding, kernel, heap, security) would belong on
  a container page for the server if the corpus gains one.

## Major lines
### 7.x (later Boot 2)
- Security off by default on the basic licence; `vm.max_map_count` at least
  262144; Spring Data Elasticsearch 4 on the RestHighLevelClient.

### 8.x (Boot 3)
- Security on and configured at first start. Spring Data Elasticsearch 5 makes
  the new Java client the default and deprecates its RestHighLevelClient
  (`erhlc`) package. `vm.max_map_count` guidance rises to 1048576.

### 9.x (Boot 4)
- The Java client defaults to `Rest5Client` with the legacy `RestClient`
  optional; Spring Data Elasticsearch 6 builds on the 9 libraries and uses
  `Rest5Client` by default. The REST compatibility mode accepts 8.x requests.

## Upstream docs
- https://www.elastic.co/docs/reference/elasticsearch/clients/java
- https://www.elastic.co/docs/deploy-manage/deploy/self-managed/important-system-configuration
- https://www.elastic.co/guide/en/elasticsearch/reference/7.17/security-minimal-setup.html
- https://docs.spring.io/spring-data/elasticsearch/reference/
- https://www.elastic.co/support/eol
