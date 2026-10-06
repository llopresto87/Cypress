# nginx — container

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a tool, not a record of one
> project's versions. For exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile / base-image tag.

## What it is
nginx is a high-performance web server, reverse proxy, and TLS terminator. In
containerized frontends it is commonly the **runtime stage** of a multi-stage
build: a build stage compiles a single-page-application (SPA) into static
assets, and a lean nginx stage serves them and proxies API calls to backend
services. It is configured declaratively via `nginx.conf` / server blocks. It ships as
two images:

- `nginx`: the official image (docker-library docs, `nginx/docker-nginx` for
  the entrypoint).
- `nginxinc/nginx-unprivileged`: the separate non-root image
  (`nginx/docker-nginx-unprivileged`).

Upstream home: nginx.org (docs and CHANGES).

## Install, setup and configuration
- **Official image.** Runs in the foreground (`daemon off`) as its command;
  workers drop to uid/gid 101 (`nginx`) on Debian and Alpine variants.
  Custom config arrives by `COPY` or bind mount over `/etc/nginx/nginx.conf`
  or into `/etc/nginx/conf.d/`, which the stock `http {}` includes wholesale
  (`conf.d/*.conf`). `nginx-debug` ships in the image and runs by replacing
  the command. `gzip` is commented out in the stock `nginx.conf`.
- **Entrypoint hooks.** `/docker-entrypoint.d/` is scanned and sorted with
  version sort (`sort -V`, so unequal-width numeric prefixes order by number):
  executable `*.sh` files run, executable `*.envsh` files are sourced,
  non-executable ones are skipped with a log line, other files are ignored.
  Hooks run **only when the first argument is `nginx` or `nginx-debug`**; a
  container started with any other command (a shell, a test command) skips all
  of them. `NGINX_ENTRYPOINT_QUIET_LOGS` silences the hook log.
- **envsubst templates.** A stock hook renders
  `/etc/nginx/templates/*.template` through `envsubst` into
  `/etc/nginx/conf.d/` with the suffix removed. Controls:
  `NGINX_ENVSUBST_TEMPLATE_DIR`, `NGINX_ENVSUBST_TEMPLATE_SUFFIX`
  (`.template`), `NGINX_ENVSUBST_OUTPUT_DIR`, and `NGINX_ENVSUBST_FILTER`, a
  regular expression on variable **names** (empty by default, meaning every
  defined variable). The hook passes `envsubst` an explicit list of the
  matching names, so nginx's own `$host` or `$uri` survive unless an
  environment variable of that name is listed. A template variable outside the
  filter, or not set, stays literal `${X}` and then fails `nginx -t` or
  misroutes. `*.stream-template` files render into `/etc/nginx/stream-conf.d`,
  and the hook appends a `stream {}` include to `nginx.conf` only when that file
  is writable. The output directory must be writable; when it is not, the hook
  logs an error, skips rendering and the container still starts.
- **Read-only root filesystem.** Upstream's recipe is `--read-only` plus
  writable mounts at `/var/cache/nginx` and `/var/run`. Every other boot-time
  write (template output, generated includes, a runtime `config.json` in the
  web root) needs its own tmpfs or volume.
- **Non-root.** The stock image as an arbitrary non-root user needs a custom
  `nginx.conf` with `pid /tmp/nginx.pid;` and every `*_temp_path`
  (`client_body`, `proxy`, `fastcgi`, `uwsgi`, `scgi`) under a writable
  directory. `nginx-unprivileged` does this already: it listens on 8080, has no
  `user` directive, keeps its pid in `/tmp/nginx.pid` and its temp paths under
  `/tmp`. Replacing its `nginx.conf` means restoring those lines, and switching
  to it moves every port reference (upstream, health check, published port).
  It is published on Docker Hub, Quay, GHCR and an AWS public registry.
- **Capabilities.** Observed in practice: stock nginx under
  `cap_drop: [ALL]` needs SETUID and SETGID back (the master drops workers to
  uid 101), NET_BIND_SERVICE for ports below 1024 and CHOWN for its cache; a
  non-root container with no capabilities must listen above 1024. Upstream
  lists no capability set. The low-port rule depends on the container sysctl
  described on [`container/docker.md`](docker.md).

## Core API / usage shape
- **Config structure**: `http`, then `server`, then `location` blocks;
  `stream {}` (L4) is a top-level sibling of `http {}`.
- **Location selection**: an exact `=` match wins; otherwise the longest
  prefix is remembered, and a `^~` prefix stops there; otherwise the first
  matching regex in file order beats the longest prefix. Which block a request
  lands in decides which headers and proxy settings it gets.
- **`root` versus `alias`**: `root` appends the full URI, location prefix
  included; `alias` replaces the matched prefix. Mixing them up gives 404s that
  look like a missing volume.
- **Static SPA serving**: `try_files $uri $uri/ /index.html;` makes unknown
  client routes fall back to the SPA entry point. It is an internal redirect,
  so if a `location = /index.html` block exists, its headers apply to every SPA
  route.
- **Reverse proxy**: `proxy_pass` forwards matched paths to an upstream;
  `proxy_set_header` sets request headers. By default the proxied request
  carries `Host: $proxy_host` (the upstream name, not the client's host).
  Forward `$host`, not `$http_host`, which is empty when the client sent no
  Host header. `proxy_set_header` follows the same replace-not-merge
  inheritance as `add_header` (see pitfalls), and it acts on the request only:
  response and CORS headers need `add_header … always`.
- **`proxy_pass` with variables**: a variable plus a URI part sends that URI
  verbatim and drops the client's sub-path; use `$request_uri` or no URI part.
  With a variable host, strip a prefix with `rewrite ^/p/(.*)$ /$1 break;` and
  a `proxy_pass` without URI. A variable host is looked up among `upstream {}`
  groups, then through `resolver`; with neither, requests fail with 502 at
  runtime, not at `nginx -t`.
- **WebSocket**: `Upgrade` and `Connection` are hop-by-hop and not forwarded;
  set both explicitly, and nginx tunnels only after the upstream answers 101.
  Use `map $http_upgrade $connection_upgrade { default upgrade; '' close; }`
  and `proxy_set_header Connection $connection_upgrade;`.
- **Timeouts**: `proxy_read_timeout` (60s) counts between two successive
  reads, so an idle socket closes after 60s; raise it per location or ping.
  `proxy_send_timeout` is the write-side twin; `proxy_connect_timeout` cannot
  usefully exceed about 75s.
- **Buffering**: `proxy_buffering on` (the default) stalls server-sent events
  and streamed responses; turn it off per location, or have the upstream send
  `X-Accel-Buffering: no`.
- **TLS termination**: a `server` listening on 443 with certificate and key.
  `ssl_session_cache shared:SSL:10m` (about 4000 sessions per MB) avoids a
  full handshake per connection; `ssl_session_timeout` defaults to 5m.
- **Upstream TLS**: `proxy_ssl_verify` is off, so upstream certificates go
  unchecked until it is on with `proxy_ssl_trusted_certificate`
  (`proxy_ssl_verify_depth` defaults to 1). `proxy_ssl_server_name` is off, so
  no SNI is sent and a virtual-hosted upstream answers with its default host;
  `proxy_ssl_name` defaults to `$proxy_host`.
- **`stream {}` with `ssl_preread on`** reads the SNI without terminating
  TLS, so the proxy holds no certificate. `map $ssl_preread_server_name $dest
  { <name> <name>:<port>; }` with no default pins egress to one name; any other
  maps to empty and is refused. Stream proxying is L4 with no queue, so an
  upstream outage is an immediate client error. The `mail {}` module, by
  contrast, terminates the protocol and needs TLS material and an `auth_http`
  backend; it is not a pass-through.

## Idioms & best practices
- Serve the SPA with the `try_files … /index.html` fallback in `location /`
  only, and end every other location (API prefixes, asset prefixes) with
  `try_files $uri $uri/ =404`. When the SPA shares its origin with API
  proxies, a blanket fallback answers mistyped or unproxied API paths with
  `200 text/html`, the client fails far away on a JSON decode, and a 2xx-only
  check passes. Cover every prefix the bundle can call, or assert status and
  Content-Type per prefix. (The nginx docs only say the last parameter is the
  fallback; the scoping is observed practice.)
- Use nginx as the small final stage of a multi-stage build so the shipped image
  contains only static assets and the server, not the build toolchain.
- Set appropriate cache headers (long-lived for fingerprinted assets, no-cache
  for the entry HTML) so clients pick up new deployments.
- Terminate TLS at nginx and keep upstream hops internal; turn on
  `proxy_ssl_verify` and `proxy_ssl_server_name` when an upstream hop is TLS.
- Add security headers with `always`, and keep the shared header set in one
  included fragment that every location declaring its own `add_header`
  re-includes (see the inheritance pitfall below). Keep fragments outside
  `conf.d/` (for example `snippets/`), because `conf.d/*.conf` is loaded whole.
- Give each security header one owner. When the edge and the upstream both
  emit it, the client gets duplicates: `proxy_hide_header` the upstream copy
  and `add_header … always` at the edge.
- To drop one header (say a CSP) on one route, include only the shared
  fragment without that policy in that location; decide by whether the page's
  markup uses inline scripts.
- At the outermost edge, decide `X-Forwarded-For` deliberately and record the
  choice. **Overwriting** it with `$remote_addr` stops a client from spoofing
  its address and means nothing downstream needs a trust list, but the
  original client chain is lost past the edge (every client may then share one
  rate-limit bucket downstream). **Appending** with
  `$proxy_add_x_forwarded_for` keeps the chain, but every consumer downstream
  must then trust only the hops it knows. An identity provider behind the edge
  usually asks for the overwrite.
- Treat the access-log format as a decision. Any route that carries a
  credential in the URL (a token in a websocket handshake query string, a
  signed-link parameter) needs a format that omits or redacts the query string
  there. Mask with one `log_format` over a `map` chain at http scope, used by
  one `access_log` per server (the map is evaluated lazily, after location
  selection); per-location `access_log` lines drift.
- Classify requests on `$uri` (normalized, decoded, no query string), never on
  `$request_uri`, which a request such as `GET /x?/hub` can spoof.
- Scope security-header sets per application. A single content security policy
  written for one app and applied to every location can break another app
  behind the same edge, an identity provider's login page with inline scripts
  being the classic case. The set of routes that must not carry a given policy
  is part of the contract, not an oversight. Write every CSP source so a
  browser can parse it: in a host-source the `*` wildcard may only be a lone
  `*` or the whole leftmost label (`https://*.example.org`), so a form such as
  `https://*.idp.*` is outside the grammar. Such a source never matches
  anything, so the written policy and the policy in force differ with no error
  (observed in practice: at most a console warning). Check each source token,
  not only the header's presence.
- Put an HTTP→HTTPS redirect inside `location /`, not as a server-scope
  `return`, which runs before location selection and makes a `/health`
  location in that server unreachable (a health check that gets 301 never
  turns healthy).
- `client_max_body_size` defaults to 1m (413 above it); raise it only on the
  upload location. Enable `gzip on` with `gzip_types` for JS, CSS and JSON.
- Prefer a catch-all `default_server` that returns 444 to `if ($host …)`.
- Build an SPA with the right base href for a sub-path instead of rewriting it
  with `sub_filter`, which is unreliable.
- `autoindex on` on an upload location makes it listable at the edge; record
  it as a decision if it is ever on.
- Namespace the envsubst filter (for example `^APP_`) and widen it whenever a
  template gains a variable.

## General pitfalls
- Missing the `try_files` fallback makes client-side routes 404 on direct
  navigation or refresh, even though in-app navigation works. The opposite
  error is the blanket fallback described above: a missing asset or API path
  returns the HTML shell with status 200.
- `proxy_pass` trailing-slash semantics change how the upstream path is
  rewritten; a subtle slash difference sends requests to the wrong upstream path.
  Observed in practice: with a variable in `proxy_pass`, authenticated calls
  returned a backend 404 and a whitelisted path got 401 through the proxy but
  200 direct; send each proxied prefix both ways and compare.
- Serving from the wrong document root (assets landed elsewhere in the multi-stage
  copy) yields blank pages or 404s that look like a build failure.
- `localhost` in a containerized nginx's `proxy_pass` is nginx's own loopback.
- Forwarded/host headers must be set for upstreams that generate absolute URLs
  or enforce host checks, or proxied apps misbehave. Change any header with
  `proxy_set_header`; setting one to an empty string suppresses it.
- **`proxy_set_header` and `add_header` inheritance is replacement, not
  merge.** A block that declares any one of its own inherits *none* of the
  parent scope's: not just the same-named one, all of them, Host and
  `X-Forwarded-*` included for `proxy_set_header`. Re-declare the shared set
  in any location that adds one of its own, or a security header silently
  disappears on exactly the paths that set something else.
  `add_header_inherit` (`on`, `off` or `merge`) changes the rule for
  `add_header`; check the headers-module page for the line you run before
  relying on it (see Major lines).
- **Without `always`, `add_header` applies only to a fixed list of codes:**
  200, 201, 204, 206, 301, 302, 303, 304, 307 and 308. Every other response,
  each 4xx and 5xx included, goes out without the header, so a security header
  is missing exactly on the error pages an attacker probes. Check the emitted
  headers on an error response, not only on a 200. A measuring harness with
  dead upstreams sees only 502 and 401, so only `always` headers show up there:
  absent means "not measured".
- **The default access-log format writes the full request line, query string
  included.** A route that carries a token in the URL leaks that token into the
  log store.
- **`nginx -t` performs the socket binds.** A `listen` on an address the host
  does not hold fails the *entire* configuration test, every server block and not
  only the offending one. A generator that may emit an optional `listen` must
  check the address exists and emit nothing when it does not, so the whole
  edge does not fail closed.
- **Duplicate `server_name` on one listen** gives a "conflicting server name …
  ignored" warning and the first block wins; config generators must
  deduplicate.
- **Scope of an include decides what it may hold.** `stream {}` is a sibling of
  `http {}`, so a `stream` block dropped into a `conf.d` fragment is parsed
  inside `http` and is a syntax error; a file included inside `server {}`
  cannot declare `upstream`, `map` or `limit_req_zone`, which are http scope.
- **A hostname literal in `proxy_pass` is resolved once, at config-load time**,
  in `http` and `stream` alike, so a DNS failure at load refuses the whole
  config and stops the server: a full outage over one unreachable name.
  Declare an explicit `resolver` and put the target in a variable to resolve at
  runtime, so a transient failure degrades that one upstream. Never point that
  `resolver` at the container-embedded DNS when the upstream name is also a
  network alias of this server: it resolves back to itself and the proxy hangs
  on its own address. Map the name on the client with Compose `extra_hosts`
  instead of aliasing the proxy, which keeps the embedded DNS usable
  ([`container/docker-compose.md`](docker-compose.md), Networks). Observed in
  practice: a literal name also keeps the IP it had at load, so after the
  upstream container is recreated with a new address the proxy returns 502 or
  hits the stale IP until a reload.
- **WebSocket over a shared location.** A literal `Connection "Upgrade"` on a
  shared `/api/` location forces Upgrade onto every REST call; use the `map`.
  With the upgrade headers missing, the realtime channel breaks while REST
  works, which looks like an application bug.
- **Dropping `X-Accel-Buffering: no`** still passes a status-code test while
  streaming stalls.
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
  on the stock image is not enough. Either use the unprivileged image or
  replicate its work (pid and temp paths under a writable directory).
- **Replacing the entrypoint, or starting with another command, loses every
  hook**, envsubst rendering included; the container then serves unrendered or
  stale config.
- **A hand-rolled `envsubst < tpl`** with no variable list blanks `$host`,
  `$uri` and `$remote_addr` (observed in practice; upstream's hook avoids it by
  passing a list).
- **`read_only: true` on stock nginx** fails on boot-time writes under
  `/etc/nginx` or the web root; move them to tmpfs first.
- **SIGKILL to the master** orphans workers that keep the port bound; stop with
  SIGQUIT (graceful) or SIGTERM.
- **TLS defaults are already modern** on current lines (see Major lines);
  restating them in config is documentation, not hardening.

## Testing
- `nginx -t` inside the shipped image, after the entrypoint hooks have rendered
  templates (run it through the normal entrypoint, since hooks run only for an
  `nginx` command), is the syntax and bind gate.
- `nginx -V` lists the compiled-in modules (`stream`, `ssl_preread`, mail);
  check it on the image you actually ship.
- Probe emitted headers per route on 200 **and** on an error response, and
  per proxied prefix through the proxy **and** direct to the upstream.
- For SPA fallbacks, assert status and Content-Type per prefix (API returns
  JSON or 404, never `text/html` 200).
- For WebSocket routes, assert the 101 handshake through the proxy.

## Security defaults
- Workers run as uid 101; the master starts as root in the stock image, as a
  non-root user in `nginx-unprivileged`.
- Upstream TLS verification and SNI are off by default (see Core API).
- `add_header` without `always` skips error responses; the default access log
  records query strings.
- `autoindex` is off by default; `client_max_body_size` is 1m.
- The stock `nginx.conf` has no security headers, no CSP and no rate limits;
  all are the operator's job.

## Operational behaviour
- Config is loaded and hostnames in `proxy_pass` resolved at start and on
  reload (`nginx -s reload` or SIGHUP), not per request unless a variable and
  `resolver` are used.
- SIGQUIT is a graceful shutdown; SIGTERM a fast one; SIGKILL leaves workers
  behind.
- `proxy_buffering` holds responses in memory and temp files; with a
  read-only root, the temp paths need a writable mount.
- An unreachable upstream gives 502 per request; a load-time DNS failure stops
  the whole server.

## Interop
- Compose networking, `extra_hosts` and health checks:
  [`container/docker-compose.md`](docker-compose.md).
- Low ports without root and the `ip_unprivileged_port_start` sysctl:
  [`container/docker.md`](docker.md).
- Identity providers behind the edge (forwarded headers, login page CSP):
  [`container/keycloak.md`](keycloak.md).
- Proxy basic-auth in front of login-less UIs (metrics and trace UIs, mail
  catchers); Grafana has its own login:
  [`container/grafana.md`](grafana.md).

## Major lines
nginx numbers its stable lines by even minor (1.26, 1.28, 1.30), and each
stable line inherits the mainline changes before it.
- **1.30 stable line and later**: `proxy_http_version` defaults to 1.1 and no
  `Connection` header is sent by default. Earlier lines defaulted to HTTP/1.0
  with `Connection: close`, so keepalive and WebSocket needed
  `proxy_http_version 1.1` set explicitly. The proxy module page still lists
  `proxy_set_header Connection close` as a default, so the changelog and the
  directive page disagree; check the emitted header on the line you run.
- **1.30 stable line and later**: `add_header_inherit` exists; older lines have
  only replacement inheritance.
- **Current stable lines** default `ssl_protocols` to TLSv1.2 and TLSv1.3 and
  `ssl_ciphers` to `HIGH:!aNULL:!MD5`.
- **Official image**: the template hook exists from the 1.20 stable line; the
  pid file moved from `/var/run/nginx.pid` to `/run/nginx.pid` from the 1.28
  stable line, and the unprivileged image uses `/tmp/nginx.pid`.

## Upstream docs
- https://nginx.org/en/docs/
- `add_header` (the code list, `always`, inheritance): https://nginx.org/en/docs/http/ngx_http_headers_module.html
- https://nginx.org/en/docs/http/ngx_http_proxy_module.html
- https://nginx.org/en/docs/http/websocket.html
- https://nginx.org/en/docs/http/configuring_https_servers.html
- https://nginx.org/en/docs/stream/ngx_stream_ssl_preread_module.html
- https://nginx.org/en/CHANGES
- CSP host-source grammar: https://www.w3.org/TR/CSP3/#grammardef-host-source
- https://hub.docker.com/_/nginx (source: https://github.com/docker-library/docs/tree/master/nginx)
- https://github.com/nginx/docker-nginx
- https://github.com/nginx/docker-nginx-unprivileged
