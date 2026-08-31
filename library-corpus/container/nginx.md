# nginx — container

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a tool, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile / base-image tag.

## What it is
nginx is a high-performance web server, reverse proxy, and TLS terminator. In
containerized frontends it is commonly the **runtime stage** of a multi-stage
build: a build stage compiles a single-page-application (SPA) into static
assets, and a lean nginx stage serves them and proxies API calls to backend
services. It is configured declaratively via `nginx.conf` / server blocks.

## Core API / usage shape
- **Static SPA serving**: a `location` block uses
  `try_files $uri $uri/ /index.html;` so unknown client-side routes fall back to
  the SPA entry point instead of returning 404 — essential for HTML5 push-state
  routing.
- **Reverse proxy**: `proxy_pass` forwards matched request paths to an upstream
  service, with `proxy_set_header` propagating host and forwarded headers.
- **TLS termination**: nginx terminates HTTPS (certificate + key in a `server`
  block listening on 443), then talks plaintext to internal upstreams.
- **Config structure**: `http` → `server` → `location` blocks; the container
  image serves from a document root populated by the build stage.

## Idioms & best practices
- Serve the SPA with a `try_files … /index.html` fallback so deep links and
  refreshes on client routes work.
- Use nginx as the small final stage of a multi-stage build so the shipped image
  contains only static assets and the server, not the build toolchain.
- Set appropriate cache headers (long-lived for fingerprinted assets, no-cache
  for the entry HTML) so clients pick up new deployments.
- Terminate TLS at nginx and keep upstream hops internal.

## General pitfalls
- Missing the `try_files` fallback makes client-side routes 404 on direct
  navigation or refresh, even though in-app navigation works.
- `proxy_pass` trailing-slash semantics change how the upstream path is
  rewritten; a subtle slash difference sends requests to the wrong upstream path.
- Serving from the wrong document root (assets landed elsewhere in the multi-stage
  copy) yields blank pages or 404s that look like a build failure.
- Forwarded/host headers must be set for upstreams that generate absolute URLs
  or enforce host checks, or proxied apps misbehave.

## Upstream docs
- https://nginx.org/en/docs/
- https://hub.docker.com/_/nginx
