# py-eureka-client — pypi

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions: for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
`py-eureka-client` is a Eureka client for Python services. It registers an
instance with a Netflix Eureka server, keeps it alive with heartbeats, can pull
the registry and call other registered applications through it, and supports
several servers with failover, per-zone server maps, DNS-based server discovery
and a replaceable HTTP client. It has sync and async interfaces. The
distribution is `py-eureka-client` (`pip install py_eureka_client` also
resolves); the import is `py_eureka_client`. Licence: MIT. It is how a Python
service becomes reachable through a Spring Cloud gateway route that names an
application id (`lb://<app-id>`); the Eureka model itself is on
`library-corpus/maven/spring-cloud.md`.

## Install, setup and configuration
- `pip install py_eureka_client`. The 0.13 line depends on `ifaddr`,
  `dnspython` and `httpx`.
- `eureka_client.init(eureka_server=..., app_name=..., instance_port=...)`
  registers and starts a cached module-level client
  (`eureka_client.get_client()` returns it). `app_name` is mandatory when
  `should_register` is true.
- Defaults, from the source:
  - server `http://127.0.0.1:8761/eureka/` (`eureka_protocol="http"`,
    `eureka_context="/eureka"`);
  - `should_register=True`, `should_discover=True`;
  - `instance_port=9090`, secure port 9443 (disabled);
  - `renewal_interval_in_secs=30` (heartbeat), `duration_in_secs=90` (lease);
  - request timeout 5 s, HA strategy random, data centre `"MyOwn"`;
  - `status_page_url`, `health_check_url` and `home_page_url` empty;
  - `strict_service_error_policy=True`.
- Servers: a comma-separated list, a per-zone map (`eureka_availability_zones`,
  `zone`, `prefer_same_zone`), or DNS TXT discovery (`eureka_domain`,
  `region`, `zone`). Protocol, basic-auth user and password, and context path
  can be given as separate parameters instead of inside the URL.
- Instance address: in the Amazon data centre the client reads the local IP
  and host name from the metadata service; otherwise it takes the first
  non-loopback interface. Override with `instance_ip` / `instance_host`, or
  pick an interface with `instance_ip_network` (a container on several
  networks needs this).

## Core API / usage shape
- Facade: `init(...)`, `stop()`, and the async forms `init_async(...)`,
  `stop_async()`.
- Raw client: `client = EurekaClient(...)`, then `await client.start()` and
  `await client.stop()` explicitly.
- Calling another application: `eureka_client.do_service(app_name,
  service_path, return_type="string" | "json", prefer_ip=False,
  prefer_https=False, method="GET", headers=None, data=None, timeout=5)`, and
  `do_service_async`. HA strategies: `HA_STRATEGY_RANDOM` (default),
  `HA_STRATEGY_STICK`, `HA_STRATEGY_OTHER`.
- Errors: an `on_error(err_type, exception)` callback fires with
  `ERROR_REGISTER`, `ERROR_DISCOVER` or `ERROR_STATUS_UPDATE`, only after every
  configured server URL has failed.

## Idioms & best practices
- Set `should_discover=False` on a service that only needs to be found; the
  default pulls the registry at start and a delta on every heartbeat cycle.
- Point `status_page_url` and `health_check_url` at paths the service really
  serves.
- Pass credentials through `eureka_basic_auth_user` and
  `eureka_basic_auth_password`, not inside the server URL.
- For self-signed certificates or another async HTTP library, subclass
  `http_client.HttpClient` and install it; on the 0.11 line and later its
  methods are async.
- Observed in practice: register from the process launch path, gated on the
  server-URL setting being present, and import the client lazily there. Tests
  and local runs then stay offline. Upstream shows only an unconditional
  `init` call.
- Call `stop()` from the shutdown path (an application `atexit` hook or a
  SIGTERM handler), so the instance deregisters before the process exits.

## General pitfalls
- Registration fails soft: `register()` catches every exception, logs the
  warning "Register error! Will try in next heartbeat", marks the client not
  alive and calls `on_error` (none by default). The process runs on
  unregistered. Alert on that warning or set `on_error`.
- An unset server URL quietly targets localhost:8761.
- The status and health URLs default to empty, so the registry points at
  nothing useful. Observed in practice: a consumer that probes Spring's default
  actuator paths gets 404 from a Python service. Upstream is silent on this.
- The library installs no `atexit` or signal handler; deregistration happens
  only when the application calls `stop()`. After a hard kill (SIGKILL) the
  instance stays in the registry until its lease expires (90 s by default), and
  callers keep being routed to it. Give the container a SIGTERM grace period.
- Observed in practice: a service that failed to register shows up at a
  gateway that routes by application id as a missing route or a 503, while the
  container behind it is healthy. Check the registry first.
- The heartbeat runs on a daemon `Timer` thread (`HeartbeatThread`) that
  creates its own event loop, beside whatever loop the application runs.
  Upstream says nothing about its interaction with an async server.
- `walk_nodes`, which some notes cite, is not in the current README or client
  module; do not rely on it.

## Testing
- Upstream documents no test harness. Observed in practice: keep
  `should_register` off, or leave the server URL unset under the gate above,
  so unit tests need no registry. Test the gate itself: with the setting
  absent, nothing imports or calls the client.
- Upstream offers no fake server, so registration, heartbeat and
  deregistration are proved only against a real Eureka server.

## Security defaults
- The default protocol is plain http, and basic-auth credentials travel with
  every call. Set `eureka_protocol="https"` when the registry crosses a network
  you do not trust.
- The URL parser accepts `user:pass@host`, so credentials written into the URL
  can end up in logs; use the separate basic-auth parameters.

## Operational behaviour
- Startup: `init` registers immediately and starts the heartbeat thread; a
  failed registration is retried on each heartbeat.
- Steady state: a heartbeat every 30 s against a 90 s lease, and with
  `should_discover` a registry delta fetch in the same cycle (a full pull
  only when the local registry is empty or the delta hash does not match);
  requests time out after 5 s.
- Shutdown: `stop()` (or `stop_async()`) deregisters and stops the thread.
  Without it the instance lingers until the lease expires.

## Interop
- Speaks the Netflix Eureka server's wire format, so Spring Cloud services and
  gateways (`library-corpus/maven/spring-cloud.md`) reach the Python instance
  by its registered application name, and the Python side can call them with
  `do_service`.

## Major lines
All releases are 0.x, so a minor line is the breaking boundary.

### 0.9 line
- Python 2 support is dropped.

### 0.11 line
- `EurekaClient` and `HttpClient` methods are async; `init_async`,
  `do_service_async` and `stop_async` arrive. The transport is stdlib
  `urllib`, and the only runtime dependencies are `ifaddr` and `dnspython`.

### 0.13 line
- `httpx` becomes a runtime dependency. Parts of the README still describe the
  older built-in `urlopen` transport.

## Upstream docs
- Repo and docs (README): https://github.com/keijack/python-eureka-client
