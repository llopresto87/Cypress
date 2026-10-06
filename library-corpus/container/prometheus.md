# prometheus — container

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a server image, not a record of
> one project's versions. For exact pins, advisories and per-release behavior,
> run `ingest-library` against the project's own image tag. Dashboards over it:
> [`container/grafana.md`](grafana.md).

## What it is
Prometheus is a metrics server (Apache-2.0, repository
`prometheus/prometheus`, docs at prometheus.io). It **pulls** metrics over HTTP
from targets found by static config or service discovery, stores them as time
series (a metric name plus labels) in a local TSDB, evaluates recording and
alerting rules, and answers PromQL over an HTTP API. Pushing is possible only
through an intermediary gateway. It never notifies anyone: it sends firing
alerts to **Alertmanager**, which deduplicates, groups, routes, silences and
delivers them. The image is `prom/prometheus` (Docker Hub, also on Quay.io).

## Install, setup and configuration
- **Image facts.** BusyBox base; runs as `nobody`, which owns
  `/etc/prometheus` and `/prometheus`; port 9090; declared volume
  `/prometheus`; entrypoint `/bin/prometheus`; `promtool` included. Default
  arguments: `--config.file=/etc/prometheus/prometheus.yml
  --storage.tsdb.path=/prometheus`. The bundled sample config scrapes
  Prometheus itself every 15s.
- **Arguments replace, not extend.** Any `command:` (or extra `docker run`
  arguments) replaces the whole default argument list, so restate
  `--config.file` and `--storage.tsdb.path` every time.
- **Config delivery.** Bind-mount the file over
  `/etc/prometheus/prometheus.yml`, mount a directory over `/etc/prometheus`,
  or bake a derived image. Keep `/prometheus` on a named volume, or every
  recreate loses the history.
- **`global`**: `scrape_interval` 1m, `scrape_timeout` 10s (not above the
  interval), `evaluation_interval` 1m, `external_labels` (attached when data
  leaves: federation, remote write, Alertmanager; `$var`/`${var}` read from
  the environment, `$$` escapes).
- **Top-level keys**: `global`, `alerting` (`alertmanagers`,
  `alert_relabel_configs`), `rule_files` and `scrape_config_files` (globs),
  `scrape_configs`, `storage` (`tsdb`, `exemplars`), `tracing`,
  `remote_write`, `remote_read`.
- **`scrape_configs`**: `job_name` (required, unique); per-job interval and
  timeout default to the global ones; `metrics_path` `/metrics`; `scheme`
  `http`; `params`; `honor_labels` false; `honor_timestamps` true; targets
  from `static_configs` or a discovery block (`file_sd_configs`,
  `eureka_sd_configs`, cloud and Kubernetes ones), with `relabel_configs`
  able to rewrite `__address__` and `__metrics_path__`.
- **Per-job HTTP auth**: `basic_auth` (`username` or `username_file`,
  `password` or `password_file`), `authorization` (`type` Bearer;
  `credentials` or `credentials_file`), `oauth2`, plus a separate
  `tls_config`; `follow_redirects` and `enable_http2` default true. Each
  value/`_file` pair is mutually exclusive, and `oauth2` cannot be combined
  with `basic_auth` or `authorization`.
- **Retention.** `--storage.tsdb.retention.time` defaults to 15d when no
  retention is set; `--storage.tsdb.retention.size` is off by default. When
  both are set, whichever triggers first wins. Current docs mark both flags
  deprecated in favour of `storage.tsdb.retention` (`time`, `size`) in the
  config file, which takes precedence and can change at runtime.
- **Web flags.** `--web.listen-address` `0.0.0.0:9090`; `--web.external-url`
  (needed behind a proxy path; it prefixes every endpoint);
  `--web.enable-lifecycle`, `--web.enable-admin-api` and
  `--web.enable-remote-write-receiver` all false; `--web.config.file`
  (experimental) for TLS and basic auth; `--config.auto-reload` false;
  `--query.timeout` 2m; `--query.max-concurrency` 20. On the 3 line
  `--auto-gomaxprocs` and `--auto-gomemlimit` default on, following the
  container's CPU quota and memory limit.

## Core API / usage shape
```
GET  /-/healthy                 # always 200 while the process runs
GET  /-/ready                   # 200 once queries can be served
POST /-/reload                  # needs --web.enable-lifecycle (or send SIGHUP)
GET  /api/v1/targets            # active and dropped targets, health per target
GET  /api/v1/query?query=up
GET  /api/v1/status/config      # the loaded config as YAML
POST /api/v1/admin/tsdb/snapshot   # needs --web.enable-admin-api
promtool check config /etc/prometheus/prometheus.yml
promtool check rules rules/*.yml
```
`/api/v1/targets` shows `labels` after relabelling and `discoveredLabels`
before it, which is how a dropped or mis-labelled target is diagnosed.

## Idioms & best practices
- **Validate before reload**: `promtool check config` and `check rules` in CI
  and before every `/-/reload`.
- **Assert targets, not the server.** `/-/healthy` proves only that the
  process runs. Compare the `up` targets in `/api/v1/targets` with the
  targets the config declares (observed in practice; the endpoint reports
  health per target).
- **Pin a release line.** Upstream marks selected releases LTS and fixes
  high-severity issues in them for a year; ordinary minors get about six
  weeks. Pin an LTS or an explicit release. Observed in practice: a floating
  `:latest` crossed into a new major unannounced; upstream makes no statement
  on `latest`.
- **Credentials from files.** Use `password_file`, `credentials_file` and
  mounted secrets. Observed in practice: an inline password in a committed
  config leaked through the repository whatever the API redacts; upstream
  redacts credentials only in some endpoints (the scrape-pool config one, for
  instance).
- **Do not template the config with `sed` at startup.** Observed in practice:
  it forced the container to run as root to write the file; the image runs as
  `nobody`, and environment expansion exists only for `external_labels`.
  Render the file before the container starts.
- **Bounded labels.** Use labels for bounded dimensions only, never IDs,
  tokens, emails or other personal data; log redaction does not reach metric
  labels (observed in practice). Fewer series cut cost more than a longer
  scrape interval.
- **Back up with snapshots** (admin API) rather than copying the live
  directory, which can miss data newer than the last two-hour block.
- **Local POSIX storage only**; NFS is not supported for the TSDB.
- **Size the disk**: retention seconds × samples per second × about 1–2 bytes
  per sample.

## General pitfalls
- **Lost flags.** A `command:` without `--config.file` and
  `--storage.tsdb.path` loses the image's paths; the binary's own storage
  default is `data/`, outside the `/prometheus` volume.
- **Absent is not zero.** Observed in practice: an empty panel can mean a
  target is down, dropped by relabelling or renamed, not that nothing happened.
  Validate metric names after a rename.
- **Discovery couples monitoring to the registry.** Observed in practice:
  with service discovery, unregistered services were never scraped, a service
  missing its relabelling metadata vanished silently, and a registry outage
  blinded monitoring; keep a static fallback for critical targets.
- **Retention is the investigation horizon.** Data older than the retention
  window is gone; expired blocks can take up to two hours to delete, and
  compaction can briefly exceed the size limit. WAL and head chunks count
  towards the size but are never deleted by retention.
- **Exporter failure is not operation failure.** Observed in practice: a
  failing exporter or scrape says nothing about the operation it measures;
  alert on `up == 0` separately.
- **Strict content types on 3.x.** A scrape with a missing or unknown
  `Content-Type` fails unless `fallback_scrape_protocol` is set.
- **Observability is never a startup dependency.** Observed in practice: an
  application gated on its metrics backend failed to start when the backend
  was down; make it optional.

## Testing
Upstream gives no test recipe; its hooks make one easy:
- `promtool check config` and `promtool check rules` as a CI gate;
- after start, wait for `/-/ready`, then assert every declared target is `up`
  in `/api/v1/targets`;
- after a metric rename, query the new name and assert it returns series.

## Security defaults
- Upstream's security model: only trusted users may change flags, config and
  rules; anyone who reaches the HTTP endpoint can read every series and
  operational detail. Never expose 9090, the API or profiling endpoints
  publicly.
- Admin API, lifecycle endpoints and remote-write receiver are off.
- TLS and basic auth are off and come only through `--web.config.file`:
  `tls_server_config` (`cert_file`, `key_file`, `client_auth_type`
  `NoClientCert`, `min_version` TLS12, `max_version` TLS13),
  `http_server_config` (HTTP/2, security headers) and `basic_auth_users`
  (bcrypt hashes). The file is re-read on every request. Basic auth without
  TLS sends the credentials in clear text, so enable both together.
- Whoever controls a discovery source or relabelling can steer scrapes, and
  with `honor_labels: true` a target can impersonate another.
- Remote read lets an HTTP client query the backing store.
- Alertmanager's API answers any origin (`Access-Control-Allow-Origin: *`);
  without authentication, any web page a browser on its network visits can use
  it.
- The image runs as `nobody`. Security fixes are best effort by volunteers.

## Operational behaviour
- Single node: the local TSDB is neither clustered nor replicated.
- Recent data sits in a two-hour in-memory head block protected by a
  write-ahead log replayed on restart (segments of 128 MB, at least three
  kept). Blocks compact up to a tenth of retention or 31
  days.
- Reload with `SIGHUP` or `/-/reload` (the HTTP form needs
  `--web.enable-lifecycle`); validate first with `promtool`.
- Release cadence: a minor about every six weeks; LTS releases get a year of
  high-severity fixes, with at least a month of overlap between two LTS
  periods. Experimental features are outside LTS support.

## Interop
- **Alertmanager**: listed under `alerting.alertmanagers` (static or
  discovered); Prometheus sends alert states, Alertmanager notifies.
- **Grafana** queries it as a data source over the HTTP API:
  [`container/grafana.md`](grafana.md).
- **Trace servers** expose metrics for it, for example Zipkin on
  `/prometheus`: [`container/zipkin.md`](zipkin.md).
- Remote write receiver (`--web.enable-remote-write-receiver`), agent mode
  (`--agent`) and feature flags (`--enable-feature`).
- A reverse proxy for TLS or auth in front: [`container/nginx.md`](nginx.md).

## Major lines
### 2.x to 3.x
- Flags whose behaviour became the default were removed (they only warn
  now); `agent` and `remote-write-receiver` became `--agent` and
  `--web.enable-remote-write-receiver`.
- No default port is added from the scheme any more (`https://host/metrics`
  stays without `:443`).
- `scrape_classic_histograms` became `always_scrape_classic_histograms`;
  remote-write `enable_http2` now defaults to false; native histograms are
  opt-in.
- PromQL: `.` in regexes matches newlines; range selectors are left-open, so
  some subqueries return one point and `rate` over them yields nothing;
  `holt_winters` became `double_exponential_smoothing` behind a flag.
- Stricter `Content-Type` handling on scrapes (see pitfalls).
- `le` and `quantile` label values are normalized to floats (`le="1"` becomes
  `le="1.0"`); queries matching whole numbers must change.
- UTF-8 metric and label names are allowed
  (`metric_name_validation_scheme: legacy` keeps the old rules); logs are
  structured.
- The TSDB written by 3.x can be read only by the last 2.x minor, so upgrade
  to that first; going lower loses data. The 2.x LTS line is out of support.
- Retention moved into the config file (the flags are deprecated).

## Upstream docs
- https://prometheus.io/docs/prometheus/latest/installation/
- https://prometheus.io/docs/prometheus/latest/configuration/configuration/
- https://prometheus.io/docs/prometheus/latest/command-line/prometheus/
- https://prometheus.io/docs/prometheus/latest/storage/
- https://prometheus.io/docs/operating/security/
- https://prometheus.io/docs/prometheus/latest/configuration/https/
- https://prometheus.io/docs/prometheus/latest/management_api/
- https://prometheus.io/docs/prometheus/latest/querying/api/
- https://prometheus.io/docs/introduction/release-cycle/
- https://prometheus.io/docs/prometheus/latest/migration/
- https://github.com/prometheus/prometheus
