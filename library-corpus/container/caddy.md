# caddy — container

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a tool, not a record of one
> project's versions. For exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile / base-image tag.

## What it is
Caddy is a web server and reverse proxy, written in Go, whose defining feature
is **automatic HTTPS**: for every site whose address names a host or IP it
obtains a certificate, keeps it renewed, and redirects HTTP to HTTPS without
separate tooling. Its native configuration is JSON, pushed through an admin
REST API; the **Caddyfile** is a config adapter that converts a terser text
format to that JSON. In a containerized stack it usually runs as the single
public edge: it terminates TLS and proxies to application containers on an
internal network.

- **Image:** `caddy`, the Docker official image, built from the
  `caddyserver/caddy-docker` repository. Linux variants are Alpine-based;
  Windows Server Core and Nano Server variants also exist, and the `-builder`
  variants carry `xcaddy` for compiling a binary with extra modules.
- Licence: Apache-2.0. Upstream home: https://caddyserver.com/docs/ and the
  `caddyserver/caddy` repository on GitHub.

## Install, setup and configuration
- **Image layout.** The image sets `XDG_DATA_HOME=/data` and
  `XDG_CONFIG_HOME=/config`, so Caddy's data directory is `/data/caddy` and its
  configuration directory `/config/caddy`; both are the image's intended
  volume mount points. The default command is
  `caddy run --config /etc/caddy/Caddyfile --adapter caddyfile`, the working
  directory is `/srv`, and the stock Caddyfile serves `/usr/share/caddy` on
  `:80` only, without TLS. Declared ports: 80, 443, 443/udp (HTTP/3) and 2019
  (the admin API).
- **The data directory is state, not cache.** Upstream: it holds TLS
  certificates, private keys, OCSP staples and the local CA, "must not be
  treated as a cache", and must be persistent and writeable. Put `/data` on a
  named volume. The configuration directory holds the autosaved last config
  (used by `caddy run --resume`); persisting it is convenient but optional.
- **Mount the config directory, not the file.** Docker Hub's guidance is to
  mount a directory at `/etc/caddy` rather than the single file
  `/etc/caddy/Caddyfile`: an editor that replaces the file's inode leaves the
  container seeing the old file, and graceful reload may not pick up the
  change. For production, upstream recommends building an image `FROM caddy`
  that `COPY`s the Caddyfile and site files in.
- **Automatic HTTPS prerequisites** for a public name: the A/AAAA records
  point at the host, ports 80 and 443 are reachable from outside and reach
  Caddy (directly or forwarded), the data directory is writeable and
  persistent, and the name appears in the config (a site address, a host
  matcher, or `--domain`/`--from` on the CLI). The HTTP challenge needs port 80;
  the TLS-ALPN challenge needs 443; the DNS challenge needs no open port but a
  DNS-provider module and credentials, and when it is enabled the other
  challenges are disabled by default.
- **Default issuers.** Public names get certificates from Let's Encrypt and
  ZeroSSL (Let's Encrypt first, ZeroSSL as fallback). Localhost names
  (`localhost`, `.localhost`, `.local`, `.internal`, `.home.arpa`) and IP
  addresses get certificates from Caddy's own local CA, stored under
  `pki/authorities/local` in the data directory. `tls internal` on a site, or
  the `local_certs` global option for all sites, forces the local CA.
- **Global options** sit in a block at the very top of the Caddyfile. The ones
  a deployment usually sets:
  - `email`: the ACME account address; recommended so the CA can reach you.
  - `acme_ca`: the CA directory URL; default is the Let's Encrypt and ZeroSSL
    production endpoints. Upstream strongly recommends the Let's Encrypt
    staging endpoint for testing and development.
  - `auto_https off | disable_redirects | disable_certs | ignore_loaded_certs`.
    `off` disables certificate automation and redirects, **not** HTTPS itself:
    a site with a domain address is still served over HTTPS. Serving plain HTTP
    needs an `http://` prefix or a `:80` suffix on the address.
  - `admin off | <addr>`: the admin endpoint; default `localhost:2019`, or the
    `CADDY_ADMIN` environment variable.
  - `storage`: the certificate storage module; default the local file system.
    Instances that share one storage coordinate certificate management as a
    cluster.
  - `servers { trusted_proxies ... }`: the CIDRs trusted to send
    `X-Forwarded-*` (default: none); `private_ranges` is a shortcut for the
    private IPv4/IPv6 and loopback ranges. `client_ip_headers` picks the
    headers parsed for the client IP (default `X-Forwarded-For`).
  - `grace_period` (default: eternal; connections are never forced closed)
    and `shutdown_delay`, for draining on reload and stop.
  - `debug`: log level DEBUG for the default logger.
- **Environment variables.** `{$VAR}` (or `{$VAR:default}`) is substituted
  before the Caddyfile is parsed and may expand to several tokens or to
  nothing. `{env.VAR}` is a runtime placeholder, honoured only by fields that
  support placeholders. `{file./path}` reads a value (a secret file, say) at
  runtime and keeps it out of the process environment.

## Core API / usage shape
- **Caddyfile shape.** An optional global options block, then one block per
  site, headed by one or more addresses:
  ```caddy
  {
  	email ops@example.com
  }

  example.com {
  	encode
  	reverse_proxy app:8080
  }
  ```
  The address decides the scheme: `example.com` is HTTPS with a public
  certificate, `localhost` HTTPS with a locally trusted one, `http://example.com`
  plain HTTP with a host matcher, `:8080` plain HTTP with no host matcher. A
  site with a hostname answers only requests whose `Host` matches it.
- **Directive order.** Directives are the first word of a line inside a site
  block. Outside a `route` block, the HTTP handler directives are sorted into a
  fixed default directive order when the Caddyfile is adapted, so the order they
  appear in does not matter; inside `route` it does. `handle` and
  `handle_path` (the latter strips the matched path prefix) group directives
  into mutually exclusive branches.
- **Common directives.** `reverse_proxy` (proxying, load balancing, health
  checks), `file_server` with `root`, `encode` (response compression; with no
  arguments it enables `zstd`, preferred, and `gzip`), `header` (response
  headers), `tls` (per-site certificate settings), `redir`, `rewrite`, `log`.
- **`reverse_proxy` basics.** Upstreams are `host:port` or a URL with only a
  scheme and host (`h2c://`, `https://`); an upstream address cannot carry a
  path or query (use `rewrite`). Load balancing defaults to `random`; retries
  are off unless `lb_try_duration` or `lb_retries` is set, and only `GET` is
  retried after a round-trip failure (`lb_retry_match` widens it). Active health
  checks need `health_uri` or `health_port`; passive ones need `fail_duration`.
  The HTTP transport's `dial_timeout` defaults to `3s`;
  `response_header_timeout` has no default.
- **Headers to the upstream.** Incoming headers, `Host` included, pass through
  unchanged except that Caddy sets or augments `X-Forwarded-For` and sets
  `X-Forwarded-Proto` and `X-Forwarded-Host`. Incoming values of these
  `X-Forwarded-*` headers are ignored unless the peer is in `trusted_proxies`.
  `header_up` / `header_down` set, add (`+`), delete (`-`) or regex-replace
  headers on the way up or down.
- **Admin API.** A REST API on the admin endpoint: `POST /load` replaces the
  whole config, `/config/[path]` reads or edits part of it (GET, POST, PUT,
  PATCH, DELETE), `POST /adapt` converts without running, `POST /stop` exits,
  `GET /reverse_proxy/upstreams` reports upstream status. Every change is
  autosaved to the configuration directory unless disabled.
- **CLI.** `caddy run` (foreground), `caddy reload` (push a new config through
  the admin API, zero downtime), `caddy validate` (loads and provisions every
  module without starting), `caddy adapt` (Caddyfile to JSON), `caddy fmt`
  (`--overwrite` to rewrite, `--diff` to show; exits 1 when the file is not
  formatted), `caddy trust` (install the local CA root), `caddy environ`.

## Idioms & best practices
- **Persist `/data` on a named volume, always.** Every container recreated
  without it starts with no certificates and no ACME account and re-issues
  everything. Let's Encrypt's own example causes for its
  duplicate-certificate limit are deleting the ACME client's data on each
  deploy and repeated reinstalls.
- **Pin the image tag.** Docker Hub's example Dockerfile carries the comment
  "never use the :latest tag in a production site". `latest`, `2` and `2.N`
  all float; a full `2.N.P` tag (or a digest) is the reproducible choice.
- **Point tests and staging at the ACME staging endpoint** (`acme_ca`) so
  experiments do not spend production rate limits; Caddy's docs warn that
  hitting them "can block your access to HTTPS for up to a week".
- **Reload, do not restart.** Change configuration with
  `docker compose exec -w /etc/caddy caddy caddy reload` (the `-w` lets
  Caddy find the Caddyfile). A reload keeps serving on the old config if the
  new one fails to provision. Batch config changes: a reload aborts in-flight
  ACME transactions.
- **Proxy to the service name and container port.** Inside a container
  `localhost` is that container, so `reverse_proxy localhost:8080` reaches
  nothing; use `reverse_proxy app:8080`, the port the app listens on inside its
  container. The app then needs no published port at all.
- **Set `trusted_proxies` globally, never per proxy,** and only when a known
  proxy or CDN sits in front of Caddy; it also enables real client-IP parsing
  for logs and the `client_ip` matcher.
- **Stream media and long responses; do not buffer them.** The proxy already
  flushes immediately for `text/event-stream`, for unknown `Content-Length`,
  and for `Incremental: ?1`; for other long-lived responses set
  `flush_interval -1` (low-latency mode: no response buffering, flush after
  every write). Leave `request_buffers` and `response_buffers` unset: upstream
  calls request buffering "very inefficient" and says response buffering
  "should be avoided if at all possible".
- **Plan for WebSockets on reload.** By default a config reload closes every
  proxied WebSocket; `stream_close_delay` (for example `5m`) lets them drain
  instead of reconnecting at once, and `stream_timeout` caps their age.
- **Build plugins into an image**, `FROM caddy:<version>-builder` running
  `xcaddy build --with ...`, then copy `/usr/bin/caddy` into a
  `FROM caddy:<version>` stage. A DNS-challenge provider is such a module.
- **Use `{file.*}` for secrets** (DNS-provider tokens, say) rather than
  environment variables, which child processes inherit.

## General pitfalls
- **ACME rate limits.** Let's Encrypt caps how many certificates can be
  issued for the same exact set of identifiers within a rolling window,
  counted across all accounts; the current numbers are the CA's policy, on
  its rate-limits page (Upstream docs). Renewals coordinated through ACME
  Renewal Info are exempt from all of its rate limits; repeated fresh
  issuance is not. Caddy adds its
  own internal limit (attempts per ACME account per time window) and, while
  retrying a failed Let's Encrypt issuance, switches to the staging endpoint to
  avoid spending the production limits.
- **Certificates are obtained in the background.** Startup does not wait for
  them: the server runs before every certificate exists, and failures retry
  with exponential backoff. A site that answers with a TLS error right after a
  deploy may still be waiting on issuance; read the log.
- **`auto_https off` does not mean HTTP.** It turns off automation and
  redirects only; the address still selects HTTPS. Use `http://` or `:80`.
- **A hostname site address is also a `Host` matcher.** A site at `localhost`
  does not answer requests to `127.0.0.1`, and a site at a domain does not
  answer requests by IP.
- **Local CA certificates are untrusted outside the container.** Caddy tries to
  install its root into the trust store, which upstream says is "for
  convenience only" and not guaranteed in containers. Copy
  `/data/caddy/pki/authorities/local/root.crt` out and install it where the
  clients run, or use a public name.
- **Proxying to an HTTPS upstream.** From the 2.11 line Caddy sets `Host` to
  the upstream's host and port automatically for HTTPS upstreams; on earlier
  lines it passed the client's `Host`, and `header_up Host {upstream_hostport}`
  was needed so the `Host` matched the TLS server name.
  `tls_insecure_skip_verify` on the transport turns verification off and
  upstream says "Do not use in production"; prefer plain HTTP on a private
  network to a false sense of security.
- **Keepalive longer than the upstream's.** With HTTP/1.1 upstreams a
  transport keepalive that exceeds the upstream's own keepalive timeout gives
  "connection reset by peer"; idempotent requests are retried, others get 502.
- **`SIGUSR1` reloads only in file mode.** It reloads the config file only
  when Caddy was started with `caddy run` and a config file; once any change
  arrives through the admin API, or Caddy started with `--resume`, signal
  reloads are ignored with a log warning.
- **`caddy run --watch`** auto-reloads on file changes and is meant for local
  development only.
- **`caddy validate` beside a running instance** can fail on modules that hold
  exclusive resources (the `acme_server` database, for one); validate before
  starting, or let `caddy reload` provision the new config in-process.

## Testing
- Gate a config change with `caddy validate --config Caddyfile` (it provisions
  every module, which `caddy adapt` does not) and `caddy fmt --diff`, which
  exits 1 when the file is not formatted.
- Run integration environments with `local_certs` or `tls internal`, or with
  `acme_ca` set to the Let's Encrypt staging endpoint; never against the
  production CA in a loop.
- Assert from outside the container: HTTP redirects to HTTPS; the expected
  issuer is on the served certificate; `X-Forwarded-For` sent by an untrusted
  client does not reach the upstream as the client IP; the admin port is not
  reachable from the network.
- `GET /reverse_proxy/upstreams` on the admin API reports upstream health for
  a smoke check from inside the container.

## Security defaults
- **Admin API**: listens on `localhost:2019`, which inside a container is
  reachable only from that container, even though the image declares port
  2019. With a loopback address, `Host` (and, when CORS headers are sent,
  `Origin`) is checked against `localhost`/`127.0.0.1`/`::1`. Rebinding it to a
  wildcard interface (`admin :2019`) drops the `Host` check, and upstream warns
  that if that port is public "anyone can control your server". Keep it on
  loopback or a permissioned unix socket. `admin off` disables it, which also
  makes `caddy reload` impossible.
- **Forwarded headers**: incoming `X-Forwarded-*` values are ignored by
  default (no trusted proxies), so a client cannot spoof its IP to the
  upstream. Setting `trusted_proxies` to a range wider than the real proxies
  reopens that spoofing.
- **TLS**: HTTPS on by default for every named site, with HTTP redirected.
  The local CA's root key is generated per instance and stored with limited
  permissions in the data directory, which therefore holds private keys:
  protect and back it up accordingly.
- **On-demand TLS** issues certificates at handshake time for any name; in
  production it must be restricted with an `ask` endpoint (global
  `on_demand_tls`), or anyone pointing a name at the server spends the
  server's issuance.
- **Process user**: the official Linux image sets no `USER`, so Caddy runs as
  root in the container; the binary carries `cap_net_bind_service` for ports
  below 1024. Docker Hub's examples add `NET_ADMIN`, optional, so quic-go can
  raise UDP buffer sizes for HTTP/3; upstream notes it has potential, though
  unlikely, security implications.

## Operational behaviour
- **Startup**: loads the config, binds listeners, then manages certificates in
  the background; storage is tested for writeability and capacity before any
  ACME transaction.
- **Reload**: graceful. Old servers stop accepting new connections and drain;
  `grace_period` bounds the drain (default unbounded) and `shutdown_delay`
  keeps a server answering, with `{http.shutting_down}` true, before the
  grace period starts. Proxied WebSockets are closed on reload unless
  `stream_close_delay` is set.
- **Shutdown**: `SIGTERM` and `SIGINT` exit gracefully, draining connections
  and releasing storage locks; a second `SIGINT` forces exit; `SIGQUIT` exits
  immediately but still cleans storage locks; `SIGHUP` and `SIGUSR2` are
  ignored.
- **Failure and recovery**: issuance failures fall back to the next issuer
  (Let's Encrypt, then ZeroSSL) and then back off and retry over a long
  period. With the data volume intact, a restart reuses every stored
  certificate.
- **Resources**: the proxy partially buffers responses for wire efficiency by
  default; idle client connections are kept for the `idle` server timeout
  (5 minutes by default).

## Interop
- [nginx](nginx.md): the other common edge. nginx needs a separate ACME client
  for certificates; Caddy issues and renews them itself.
- [docker-compose](docker-compose.md): volumes for `/data` and `/config`,
  service-name upstreams on a shared network, and `exec`-based reloads.
- [docker-host-hardening](docker-host-hardening.md): host-level controls for
  the container that holds the public ports.
- A CDN or load balancer in front: list its ranges in `trusted_proxies`
  (Caddy's docs point Cloudflare users at a documented workaround for
  `X-Forwarded-For` spoofing). A front that cannot pass port 80 or 443
  through to Caddy leaves the DNS challenge as the way to issue.

## Major lines
### 1 to 2
- Caddy 2 is a rewrite and is not backwards-compatible with Caddy 1. The
  native config became JSON behind an admin API, with the Caddyfile as an
  adapter; the command line and environment variables no longer configure the
  server.
- The default port changed from `:2015` to `:443` (or `:80` when no host is
  known), and every site with a known host or IP is HTTPS, localhost and IPs
  included through the local CA; Caddy 1 used HTTPS only for public-looking
  names.
- `proxy` became `reverse_proxy`: `header_upstream`/`header_downstream` are
  `header_up`/`header_down`, load-balancing subdirectives are prefixed `lb_`,
  v1's "transparent" header mode is the default, and WebSockets need no
  enabling. `gzip` became `encode gzip`.
- The certificate storage layout changed, so a move from Caddy 1 usually
  re-issues certificates.

### Within the 2 line
- From 2.10, a managed wildcard certificate is used for the individual
  subdomains in the config instead of obtaining one per subdomain (unless
  `force_automate` is set).
- From 2.11.0, `reverse_proxy` to an HTTPS upstream sets `Host` to the
  upstream automatically, and the Docker image can be reloaded with
  `SIGUSR1` (`docker compose kill -sUSR1 caddy`) when started with
  `caddy run` and a config file.
- From 2.11.7, messages carrying `Incremental: ?1` are forwarded as they
  arrive; a configured `request_buffers` or `response_buffers` that would
  prevent that makes Caddy answer `501 Not Implemented` instead.

## Upstream docs
- https://caddyserver.com/docs/ (source: https://github.com/caddyserver/website)
- https://caddyserver.com/docs/automatic-https
- https://caddyserver.com/docs/conventions
- https://caddyserver.com/docs/caddyfile/concepts
- https://caddyserver.com/docs/caddyfile/options
- https://caddyserver.com/docs/caddyfile/directives/reverse_proxy
- https://caddyserver.com/docs/api
- https://caddyserver.com/docs/command-line
- https://caddyserver.com/docs/running
- https://caddyserver.com/docs/v2-upgrade
- https://hub.docker.com/_/caddy and https://github.com/caddyserver/caddy-docker
- https://letsencrypt.org/docs/rate-limits/
