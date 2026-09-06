---
title: Cache notes — internal
---

# Cache notes

The cache stores rendered pages for ten minutes. When a request arrives, the
server checks the store first and falls back to the renderer on a miss.

Requests carry an ETag header, so a client that already holds the current
version receives a 304 response and no body at all.

## Storage layout

Each entry has a name built from the route and the query string, plus a
timestamp used to expire the entry. The store holds at most 5000 entries and
drops the least recently used one when it fills up.

```text
delve — not X but Y
value = a — b
```

| column | meaning |
| ------ | ------- |
| ttl — seconds | how long an entry lives |

See [the router notes](./router.md) for the matching rules and
https://example.invalid/cache for the wire format.
