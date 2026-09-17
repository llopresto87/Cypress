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
- **`add_header` inheritance is replacement, not merge.** A block that declares
  any `add_header` of its own inherits *none* of the parent scope's headers —
  not just the same-named one, all of them. Re-declare the shared header set in
  any location that adds a header of its own, or a security header silently
  disappears on exactly the paths that set something else.
- **`nginx -t` performs the socket binds.** A `listen` on an address the host
  does not hold fails the *entire* configuration test — every server block, not
  only the offending one. A generator that may emit an optional `listen` must
  check the address exists and emit nothing when it does not, rather than fail
  the whole edge closed.
- **`stream {}` (L4 proxying) is a top-level block, a sibling of `http {}`.**
  Because `http {}` includes `conf.d/*.conf`, a `stream` block dropped into a
  `conf.d` fragment is parsed inside `http` and is a syntax error. Where an
  include fragment lands decides its scope.
- **A hostname literal in `proxy_pass` is resolved once, at config-load time**,
  so a DNS failure at load refuses the whole config and stops the server — a
  full outage over one unreachable name. Declare an explicit `resolver` and put
  the target in a variable to resolve at runtime, so a transient failure
  degrades that one upstream. Never point that `resolver` at the
  container-embedded DNS when the upstream name is also a network alias of this
  server: it resolves back to itself and the proxy hangs on its own address.
- **A `map`-produced log variable is always "set".** nginx's log module renders
  a not-found variable as `-` and a found-but-empty one as `""`; routing a log
  field through a `map` turns every `-` into `""`. A field whose contract is
  byte-identical output must read its source variable directly, and the probe
  that catches the difference sends the header absent.
- **A `log_format` declared but never referenced by an `access_log` is a silent
  no-op**: `nginx -t` passes, the server starts, and the compiled-in default
  keeps writing. A gate that greps for the format *name* passes on a broken
  config; assert the directive's effect and that it is scoped once, not the
  presence of its definition.
- **`proxy_hide_header X` suppresses only the upstream's `X`, never this
  server's own `add_header X`.** Keeping both is correct: the hide strips
  whatever an upstream might send, the set adds yours.
- **The stock `nginx:*-alpine` image does not make `/var/cache/nginx`, `/var/run`,
  or the default pid path writable by the built-in uid 101.** Running `USER 101`
  on the stock image is not enough — either use nginx's own unprivileged image
  or replicate its work (make the cache dir group-writable and redirect the pid
  file to a writable path).

## Upstream docs
- https://nginx.org/en/docs/
- https://hub.docker.com/_/nginx
