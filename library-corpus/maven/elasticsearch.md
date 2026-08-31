# elasticsearch — maven

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
Elasticsearch is a distributed search and analytics engine, consumed from Java
via an HTTP-based client that indexes JSON documents and issues search and
analytics queries against a cluster. On the JVM this has been offered as a
typed Java API client and, historically, as a high-level REST client; Spring
applications may instead consume it through `spring-data-elasticsearch`. The
cluster itself is a separately-run service the application connects to over the
network.

## Core API / usage shape
- Index one JSON document per logical record or event; each document lives in
  an index and is addressable for retrieval and search.
- Issue search and analytics queries (full-text, filters, aggregations)
  against one or more indices through the client.
- Define Index Lifecycle Management (ILM) policies to control rollover and
  retention declaratively at the cluster, rather than managing index rollover
  in application code.

## Idioms & best practices
- Treat the cluster as a separately-owned service the application connects to,
  not something embedded in the application process.
- Express retention and rollover through an ILM policy document so lifecycle
  rules are managed by the cluster and versioned as configuration.
- Model the document shape deliberately (mappings) rather than relying purely
  on dynamic inference for fields that need specific analysis or types.

## General pitfalls
- The Elasticsearch Java client's major version must match the cluster's major
  version — a mismatched client/server major combination fails to interoperate.
  Client and server majors are therefore upgraded in lockstep and verified
  together, not bumped independently.

## Upstream docs
- https://www.elastic.co/guide/en/elasticsearch/client/java-api-client/current/index.html
- https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html
