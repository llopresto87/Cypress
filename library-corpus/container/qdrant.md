# qdrant — container

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a tool, NOT a version-pinned page. For
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile / base-image tag. The client library has its own page,
> [`pypi/qdrant-client.md`](../pypi/qdrant-client.md).

## What it is
Qdrant is an open-source vector database: it stores points (a vector plus a
JSON payload) in **collections** and answers similarity search with payload
filtering. Self-hosted, it runs as a server from the official container image,
exposing a REST API and a gRPC API on separate ports, and can run as a single
node or as a cluster.

## Core API / usage shape
- **Collections and points.** Create a collection with a vector size and
  distance metric, upsert points by id, query by vector with an optional payload
  filter, and delete points by id or by filter.
- **Two transports.** REST and gRPC expose the same operations on separate
  ports; which one a consumer should use is a client choice (see the client
  page).
- **API keys.** The server accepts keys of different reach: an **admin** key
  with full access to all operations and collections, a **read-only** key for
  consumers that only query, and **granular** keys scoped per collection. Admin
  and read-only keys can be configured at the same time.
- **Configuration.** Server options come from a config file or from
  environment variables following the `QDRANT__SECTION__KEY` pattern.

## Idioms & best practices
- **Secure it before anything else.** Upstream's recommended order is
  authentication, then audit logging, then binding the network interface, then
  TLS. Configure a key, and do not publish the ports beyond the network its
  consumers sit on.
- **Configure a read-only key alongside the admin key**, and per-collection
  keys where consumers are scoped to collections, so each consumer can be given
  the narrowest key (the consumer-side rule is on the client page). A retrieval
  path that holds the admin key can also delete by filter, which turns a defect
  in that path into a deletion capability.
- **Use TLS whenever the key crosses a network.** Without it the key travels in
  clear to anything that can observe the channel.
- **Pin the image.** API-key kinds and other security controls arrived in
  specific releases; with a floating tag, which controls the running server
  even has is unknowable, a rebuild can cross a breaking change, and a rollback
  has no target.
- **Make a missing key stop the deployment.** An empty key on the client side
  fails open (the client page owns that pitfall), so the server key and every
  consumer key are required values, not optional ones.

## General pitfalls
- **A self-hosted instance is not secure by default.** It listens on all
  interfaces with no authentication configured; upstream calls that state not
  production-ready.
- **Internal cluster channels are not protected by API keys or bearer tokens.**
  Node-to-node traffic has to be protected at the network layer.
- **An admin key shared across every consumer erases the difference between
  reading and writing.** Every service that holds it can delete.
- **A suite that never talks to a real Qdrant API cannot see a server-side
  behaviour change.** The client page owns the local-mode testing idiom that
  closes this without a running server.

## Upstream docs
- https://qdrant.tech/documentation/
- https://qdrant.tech/documentation/security/
- https://github.com/qdrant/qdrant
- https://hub.docker.com/r/qdrant/qdrant
