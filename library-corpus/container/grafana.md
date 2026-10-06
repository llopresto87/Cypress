# grafana — container

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a tool, not a record of one
> project's versions. For exact pins, advisories and per-release behavior, run
> `ingest-library` against the project's own image tag. The metrics server it
> most often reads is [`container/prometheus.md`](prometheus.md).

## What it is
Grafana is an observability UI: dashboards, exploration and alerting over many
data sources (metrics, logs, traces, SQL). The self-managed server comes from
the `grafana/grafana` repository (AGPL-3.0) and ships as container images:

- `grafana/grafana`: the Open Source edition.
- `grafana/grafana-enterprise`: the edition upstream recommends, free with the
  OSS feature set until a licence is added.
- `grafana/grafana-oss`: the older image repository, no longer updated.

Grafana keeps its own state (users, dashboards saved in the UI, alert state)
in an internal database, embedded SQLite by default, on its data volume.
Grafana Cloud is a separate hosted product with no local configuration file
and is out of scope here.

## Install, setup and configuration
- **Image facts.** Port 3000. Runs as uid 472, gid 0. Entrypoint `/run.sh`,
  which starts `grafana server` with console logging. Paths: config
  `/etc/grafana/grafana.ini`, data `/var/lib/grafana`, plugins
  `/var/lib/grafana/plugins`, logs `/var/log/grafana`, provisioning
  `/etc/grafana/provisioning` (`datasources`, `dashboards`, `alerting`,
  `plugins`, `access-control`, `notifiers`).
- **Tags.** `<version>` is Alpine (the recommended base); `-ubuntu` and
  `-distroless` variants exist, each also as `-slim`. Minor-line tags exist. A
  security release carries a `+security-NN` suffix, which Docker tags render as
  `-security-NN`.
- **Persistence.** Mount a volume on `/var/lib/grafana`; without one, every
  container removal loses all state. A bind mount must be writable by the
  container user (upstream shows `--user "$(id -u)"`). SQLite is not
  recommended for production: set `[database] type` to `mysql` or `postgres`.
- **Configuration layers.** `conf/defaults.ini` holds the defaults (never edit
  it); `custom.ini`, the packaged `/etc/grafana/grafana.ini` or `--config`
  overrides it. Any key can be overridden by `GF_<SECTION>_<KEY>` (upper case,
  `.` and `-` become `_`; the default section is `GF_DEFAULT_<KEY>`); use env
  to override existing options, not to invent new ones.
- **Secrets.** Inside the ini, `$__env{NAME}` (or `${NAME}`) and
  `$__file{path}` expand values. In the container, `GF_<SECTION>_<KEY>__FILE`
  points at a file whose content becomes the value. Setting both the plain and
  the `__FILE` variable is an error and the container exits.
- **Plugins.** `GF_PLUGINS_PREINSTALL` (comma list, optional `@version` or
  `id@version@url`) installs in the background while the server starts;
  `GF_PLUGINS_PREINSTALL_SYNC` blocks until installed. `GF_INSTALL_PLUGINS` is
  deprecated.
- **`[server]`.** `protocol` (http, https, h2, socket, socket_h2); `http_port`
  3000; an empty `http_addr` means all interfaces. `root_url` is the full public
  URL (OAuth callbacks need it). `serve_from_sub_path` defaults to false; set it
  true together with a sub-path in `root_url` when a proxy serves Grafana under
  a prefix. `min_tls_version` defaults to TLS1.2.
- **Other defaults that matter.** `[analytics] reporting_enabled` and
  `check_for_updates` are true; `[dashboards] min_refresh_interval` is 5s and
  `versions_to_keep` 20; `[unified_alerting] enabled` is true.

## Core API / usage shape
- **Provisioning is the declarative route.** YAML files with `apiVersion: 1`
  under the provisioning directories, read at startup.
- **Data sources** (`provisioning/datasources/*.yaml`): `datasources:` is a
  list of `name`, `type`, `access` (proxy or direct), `orgId` (1), `uid`, `url`,
  `isDefault` (one per org), `jsonData`, `secureJsonData` (encrypted before
  storage), `version`, `editable`. `deleteDatasources:` runs before the list is
  applied; `prune: true` removes provisioned sources that disappear from the
  files. Custom HTTP headers go in `jsonData.httpHeaderName1` plus
  `secureJsonData.httpHeaderValue1`.
- **Dashboards** (`provisioning/dashboards/*.yaml`): `providers:` each with
  `name`, `orgId`, `folder`, `folderUid`, `type: file`, `disableDeletion`,
  `updateIntervalSeconds` (10), `allowUiUpdates` (false), `options.path` and
  `options.foldersFromFilesStructure` (needs `folder` and `folderUid` unset).
  The files under `path` hold dashboard JSON, or the Kubernetes resource form
  that the newer dynamic dashboards require.
- **Alerting** (`provisioning/alerting/*.yaml` or JSON): rule `groups`,
  `deleteRules`, contact points, notification policies, mute timings and
  templates. Rule `uid` is letters, digits, `-` and `_`, at most 40 characters;
  `noDataState` defaults to NoData and `execErrState` to Alerting.
- **Plugins provisioning** (`provisioning/plugins/`) configures installed apps;
  it does not install them.
- **HTTP API.** `GET /api/health` returns JSON with `commit`, `database` and
  `version`. Automation authenticates with **service accounts** and their
  tokens, which replace API keys.
- **Environment in provisioning files** is allowed in values only (`$NAME` or
  `${NAME}`), not in keys, not in structure and not inside dashboard JSON; a
  literal `$` is `$$`.

## Idioms & best practices
- **Provision everything you care about from version control**: data sources,
  dashboards and alerting. Upstream frames it as GitOps. An unprovisioned
  Grafana starts empty, and its volume then becomes the only copy of every
  dashboard: unreviewable, and gone with the volume.
- **Set `uid` explicitly** on data sources and dashboards so dashboards, alert
  rules and URLs reference something stable; export dashboard JSON with `id`
  removed and `uid` kept.
- **With several instances**, give each provisioned data source a `version`
  and raise it on change; Grafana applies only an equal or higher version.
- **Secrets through `__FILE` or `$__file{}`**, never inline in a committed
  provisioning file.
- **Service accounts for automation**, never a person's login.
- **Back up before upgrading**: config, plugin data and the database (stop
  Grafana and copy `grafana.db` for SQLite; dump MySQL or PostgreSQL). Update
  plugins after the upgrade (`grafana cli plugins update-all`).
- **Its own login is enough.** Grafana authenticates users itself. Observed in
  practice: a proxy basic-auth layer belongs in front of the UIs that have no
  login (the Prometheus UI, trace UIs, mail catchers), not stacked on Grafana.

## General pitfalls
- **No volume, no data.** Container removal loses dashboards, users and alert
  state.
- **Uid 472 cannot write the mount.** The data path must be writable by uid 472
  (gid 0) or by the user the container runs as.
- **Double expansion.** With `${NAME}`, a value that itself contains `$` is
  expanded twice; prefer `$NAME` for passwords.
- **File edits seem ignored.** At `updateIntervalSeconds` of 10 or less Grafana
  waits for filesystem events, which some bind mounts and network filesystems
  never deliver; set a value above 10 to force polling.
- **UI edits to provisioned dashboards are lost.** With `allowUiUpdates: true`
  a save works but the file wins again on the next pass (and the file's
  `version` is ignored); with the default false the UI refuses the save.
  Reusing a `uid` or a title in one folder behaves inconsistently.
- **Removing a dashboard file deletes the dashboard** unless `disableDeletion`
  is set.
- **Provisioned alerting is read-only in the UI**, importing an existing
  resource conflicts, and the notification policy tree is one resource:
  provisioning it replaces the whole tree.
- **Sub-path behind a proxy.** A sub-path in `root_url` alone is not enough;
  `serve_from_sub_path` must be true when the proxy does not strip the prefix.
  Observed in practice: a Grafana address hard-coded into a front-end build
  broke when the serving path changed; reach it through configuration, not a
  build constant.
- **`localhost` in a data source URL** is the Grafana container itself; use
  the other container's service name.
- **A frozen image repository.** A pin on `grafana/grafana-oss` stops receiving
  images; move to `grafana/grafana`.
- **Empty is not zero.** See
  [`container/prometheus.md`](prometheus.md), General pitfalls, "Absent is not
  zero".

## Testing
Upstream gives no test recipe. Derived from the provisioning and API docs:
- smoke: `GET /api/health` returns 200 with `"database": "ok"`;
- provisioning: start the container with the provisioning directories
  mounted, list data sources and dashboards through the HTTP API with a
  service-account token, and compare with the files;
- dashboards: keep the exported JSON (no `id`, stable `uid`) under review, so a
  diff shows every panel change.

## Security defaults
- First run creates `admin` with password `admin` (set once;
  `disable_initial_admin_creation` false). Change it on first boot or provision
  the admin password through a secret.
- `secret_key` encrypts data-source secrets; changing it later means
  re-encoding them.
- Anonymous access is off (`[auth.anonymous] enabled`); upstream calls public
  dashboards the safer way to share.
- `cookie_secure` is false (set true behind HTTPS); `cookie_samesite` is lax
  (strict breaks OAuth and SAML logins); `allow_embedding` is false
  (X-Frame-Options deny); HSTS and a Content-Security-Policy are opt-in;
  brute-force login protection is on; Gravatar is on.
- It listens on all interfaces; publish the port only through the proxy that
  terminates TLS.
- Usage reporting and update checks call out by default; turn them off where
  egress is restricted.
- `[unified_alerting] allowed_integrations` limits which contact-point types
  can send data out.

## Operational behaviour
- Startup runs database migrations; a large upgrade can need extra disk (one
  12-line migration of the annotation table needed two to three times the
  table's size free).
- **Support policy** (self-managed): each minor is supported for nine months,
  the last minor of a major for fifteen; patches fix bugs and security only.
  Upstream publishes a dated support table: read it for the line in use, and
  never assume an old major is still covered. Cadence: a minor about every
  other month, a major once a year.
- **High availability**: two or more active-active servers behind a load
  balancer on one shared MySQL or PostgreSQL database; sessions live in the
  database, so no affinity is needed. Alerting HA runs every rule on every
  server and deduplicates the notification; it does not spread the load.
- Provisioned alerting changes apply on restart or through the admin reload
  API.

## Interop
- **Prometheus data source**: `url` is the server address (the Prometheus
  container's service name), auth basic, forwarded OAuth or none;
  `jsonData.httpMethod` (POST), `timeInterval` (set it to the scrape interval),
  `prometheusType` (Prometheus, Mimir, Cortex, Thanos), `manageAlerts`,
  `alertmanagerUid`. See [`container/prometheus.md`](prometheus.md).
- An Alertmanager data source links external rule management into the
  Alerting UI.
- Image rendering runs as a separate renderer service on current lines.
- A reverse proxy in front: [`container/nginx.md`](nginx.md); compose wiring:
  [`container/docker-compose.md`](docker-compose.md).
- Community config-management modules exist (an Ansible collection among
  them).

## Major lines
### 12 line
- The annotation-table migration needs free disk of two to three times the
  table before upgrading.
- Data-source UID format enforcement tightened; fix non-conforming UIDs.
- The `grafana/grafana-oss` repository stopped receiving images during this
  line; `grafana/grafana` carries the same OSS images.

### 13 line
- Front end on React 19: update plugins first, then Grafana.
- Data-source APIs addressed by numeric id are off by default (the
  `datasourceLegacyIdApi` flag re-enables them), and the legacy `/api` tree is
  deprecated in favour of a Kubernetes-style `/apis` layer (still served).
- The Image Renderer plugin is gone; the renderer runs as a service and
  authenticates with JWTs.
- Dynamic dashboards are on by default and dashboards migrate to the new
  schema when opened; Git Sync is generally available.
- Azure AD and SigV4 auth on the core Prometheus data source moved to
  dedicated plugins, migrated at startup.
- An early build of the line could lose dashboards and folders when Git Sync
  had been adopted early on the 12 line; it was withdrawn, and the fix does not
  restore lost data. Back up before crossing to 13.

Earlier majors are out of support; their differences are not recorded here.

## Upstream docs
- https://grafana.com/docs/grafana/latest/setup-grafana/installation/docker/
- https://grafana.com/docs/grafana/latest/setup-grafana/configure-docker/
- https://grafana.com/docs/grafana/latest/setup-grafana/configure-grafana/
- https://grafana.com/docs/grafana/latest/administration/provisioning/
- https://grafana.com/docs/grafana/latest/alerting/set-up/provision-alerting-resources/file-provisioning/
- https://grafana.com/docs/grafana/latest/setup-grafana/configure-security/configure-security-hardening/
- https://grafana.com/docs/grafana/latest/upgrade-guide/when-to-upgrade/
- https://grafana.com/docs/grafana/latest/datasources/prometheus/configure/
- https://github.com/grafana/grafana
