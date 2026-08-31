# stomp-sockjs — npm

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
The client-side STOMP-over-WebSocket stack, covering the commonly-paired
packages:

- `@stomp/stompjs` — a STOMP-protocol client for JS/TS: publish/subscribe
  messaging over a message broker.
- `sockjs-client` — a WebSocket-with-HTTP-fallbacks transport, used to reach
  brokers that require SockJS compatibility when a raw WebSocket is not
  available end to end.
- `@stomp/rx-stomp` — wraps the STOMP client as RxJS observables.
- `jwt-decode` — decodes a JWT client-side. It does NOT verify or validate it.

## Core API / usage shape
- Construct a client, e.g. `new Client({ brokerURL, ... })`, then subscribe to
  broker topics/destinations to receive messages and publish to send them.
- An auth token can optionally be attached at connect time (e.g. in the connect
  headers) so the broker authorizes the session.
- When HTTP-fallback compatibility is needed, use the SockJS transport in place
  of the raw WebSocket URL rather than pointing the client at a `ws(s)://` URL.
- `@stomp/rx-stomp` exposes the same broker interactions as observable streams
  for RxJS-based consumers.

## Idioms & best practices
- Prefer a raw WebSocket (`brokerURL`) when the broker and network support it;
  reach for SockJS only when HTTP fallbacks are actually required.
- Treat `jwt-decode` output as untrusted display/context data only — read
  claims from it, never gate security decisions on it (see pitfalls).

## General pitfalls
- Legacy-vs-modern package duplication: an older pre-scoped package (e.g.
  `stompjs`) and its modern scoped successor (`@stomp/stompjs`) can end up
  installed side by side after a rename/rescope, while only one is actually
  imported. Check for superseded-package duplicates after any library rescope.
- Wrapper/adapter service classes over the client can become stale dead code if
  components later call the underlying client directly. Verify a wrapper layer
  is still on the call path before trusting it as the integration point.
- `jwt-decode` DECODES but does not VALIDATE a JWT: it reads the payload without
  checking the signature or expiry. Decoding is not verification — never treat a
  client-side decode as proof the token is authentic or unexpired.
- `jwt-decode`'s export shape has flipped between a default export and a named
  export across major versions — check the installed major before assuming the
  import form.

## Upstream docs
- https://stomp-js.github.io/
- https://github.com/sockjs/sockjs-client
