# keycloak — container

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a tool, not a record of one
> project's versions. For exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile / base-image tag.

## What it is
Keycloak is an open-source identity and access management server: an OAuth 2.0 /
OpenID Connect provider and SAML identity provider that owns users, credentials,
login flows, and token issuance for everything in front of it: browser
applications, mobile clients, and machine-to-machine callers. It is distributed
as a container image and configured declaratively, so in a containerized stack it
is normally a service of its own rather than a library linked into an
application.

The unit of isolation is the **realm**: a self-contained tenant holding users,
groups, roles, clients, client scopes, authentication flows, required actions,
themes, and mail settings. Applications register as **clients**, either *public*
(a browser or mobile app that cannot keep a secret) or *confidential* (a
server-side app or service account that can).

## Install, setup and configuration
- **First admin.** `KC_BOOTSTRAP_ADMIN_USERNAME` and
  `KC_BOOTSTRAP_ADMIN_PASSWORD` create a **temporary** admin in the master
  realm on the first start only, while the master realm does not yet exist.
  Upstream says to replace and remove it by hand. Changing the variables later
  does nothing, and the account is no application realm's admin. Lost admin
  access is recovered with the separate `bootstrap-admin` command, with every
  node stopped.
- **Development mode.** The quick start (`start-dev`, `admin`/`admin`) is for
  development only.
- **Management interface.** With health or metrics enabled, their endpoints
  (`/health/started`, `/health/live`, `/health/ready`, `/metrics`) are served on
  a separate management port, 9000 by default, so they can stay off the public
  listener. With `http-management-health-enabled=false` they move to the main
  port and must be blocked at the proxy.
- **Vault.** Realm configuration may reference `${vault.<key>}` instead of
  holding a secret literally. `--vault=file` resolves the reference from a
  mounted file named by realm and key, in a directory (mounted secrets suit
  it); a keystore vault also exists. Observed in practice: on the 26 line
  `--vault` and `--spi-*-provider` behaved as runtime options; upstream's
  vault page does not state the category.
- **Event logging.** The logging event listener writes to the
  `org.keycloak.events` category; successful events log at `debug` by default,
  which the default root level does not show.
  `--spi-events-listener--jboss-logging--success-level` and `--error-level`
  (`debug`, `info`, `warn`, `error`, `fatal`) change that.
- **Tracing.** `tracing-enabled` is a build-time option; the default exporter
  endpoint is gRPC on port 4317 and the service name `keycloak`; the operator
  sets `KC_TRACING_*` variables.

## Core API / usage shape
- **OIDC surface.** Everything hangs off the realm's discovery document at
  `/realms/<realm>/.well-known/openid-configuration`: authorization, token,
  userinfo, JWKS, and logout endpoints. Resource servers validate bearer JWTs
  against the published JWKS and check `iss`, `aud`, and expiry.
- **Grants in practice.** Authorization code + PKCE for browser and mobile
  clients; `client_credentials` for service-to-service calls with a confidential
  client; refresh tokens for session continuity.
- **Realm import/export.** A realm can be exported to, and seeded from, a single
  JSON representation; the server can import it at startup from an import
  directory (`--import-realm`).
- **Admin CLI and admin REST.** `kcadm.sh` authenticates once and then performs
  `get` / `create` / `update` / `delete` against admin resource paths; `-s
  field=value` applies partial updates, `-f <file>` submits a whole
  representation. The admin REST API exposes the same resources for scripting.
- **Configuration.** Options are supplied interchangeably as CLI flags, `KC_*`
  environment variables, or a configuration file: hostname, proxy and TLS
  behavior, database, health and metrics endpoints, logging.
- **Build-time vs runtime options.** The server distinguishes options baked into
  an optimized image by a build step from options read at start-up. Which
  category a given option falls into has moved between major lines; confirm
  against the pin in use rather than copying a flag list from elsewhere.
- **SPI providers.** Most subsystems are pluggable behind a service provider
  interface: email sender, authenticators, event listeners, user federation. A
  provider is packaged as a jar, placed in the server's providers directory, and
  selected with `--spi-<spi>-provider=<id>`.
- **Themes.** Login, email, and account templates are overridable per realm.
- **Context path.** The current distribution serves from `/`, not the old
  `/auth`. `http-relative-path` restores a prefix, and then the prefix is part
  of every URL, the issuer included, so proxies and validators must use it
  (observed in practice).
- **Client scopes and protocol mappers.** What goes into a token is decided per
  client by protocol mappers, and a client scope bundles mappers and role scope
  so clients can share them. A realm's **default** client scopes apply to every
  token automatically; **optional** ones apply only when the request's `scope`
  parameter asks for them.

## Idioms & best practices
- **Build a derived image when you need providers or themes**, rather than
  bolting them onto the stock image at run time. Compile a provider against the
  jars copied out of *the same server image that will run it* (a multi-stage
  build copying the server's own libraries), so there is no package-repository
  dependency and provider/server drift is impossible by construction. An
  incompatibility then surfaces at image-build time instead of as mail that
  silently never sends.
- **Treat realm import as bootstrap-only.** Startup import skips a realm that
  already exists, so editing the seed file alone never reaches an already
  provisioned environment. Carry every subsequent realm change as an explicit,
  idempotent, fail-closed migration step executed at start via the admin CLI or
  REST, and keep the seed and the migration set as one artifact.
- **Give each migration a durable idempotence marker** stored on the object it
  changes (a realm or client attribute, say), rather than re-deriving "has this
  already run?" from the state the migration itself sets. Re-derivation breaks
  the moment an operator changes that state by hand. Not every place that looks
  like it can hold a marker does: a **user attribute** is silently dropped when
  the realm's declarative user profile does not admit unmanaged attributes, and
  a **required action** clears when the user completes it, so it cannot tell
  "never applied" from "applied and done". A realm attribute survives both.
- **Put a reverse proxy in front and expose only the public surface.** Expose
  the realm, well-known and static-resource paths (`/realms/`, `/.well-known/`,
  `/resources/`) publicly; keep `/admin/` and the master realm
  (`/realms/master/`) internal; block health and metrics at the proxy. Better
  still, serve the admin console and admin REST API on a separate hostname or
  context path from the public frontend URLs, so the proxy rule becomes a
  hostname split instead of a path list.
- **Forwarded headers are opt-in and must be overwritten, not appended.** The
  server trusts `X-Forwarded-*` / `Forwarded` only when its proxy-headers option
  is set explicitly. The proxy in front must **overwrite** those headers with its
  own values, so a client cannot inject a false address, and the server's
  trusted-proxy-addresses option (a list of addresses or CIDRs) then narrows
  whose headers it believes. Trust a declared subnet, not a resolved container
  address (see [`docker.md`](./docker.md)).
- **Plan production for more than one instance.** Run two or more instances,
  wire a readiness check to the readiness health endpoint, and set a limit on
  queued HTTP requests explicitly; left unset, the queue is unbounded, so
  overload shows up as latency growing without limit instead of fast rejection. If a single instance is the declared shape, say so
  where the deployment is described, so the gap reads as a decision.
- **Never update a realm with a whole-document PUT.** Submitting a full realm
  representation replaces it wholesale and silently drops whatever the submitted
  document omits: password policy, brute-force settings, token lifespans. Use
  per-field updates.
- **Keep secrets out of the environment.** Put a vault reference in the realm and
  mount the value; an SMTP or client secret in a plain environment variable is
  visible to anything that can inspect the container.
- **Decide the hostname configuration deliberately**, because the configured
  hostname is what the server stamps as the token issuer even for requests that
  arrive on an internal address. Every validator, browser-facing and internal,
  has to agree on that issuer string.
- **Reconcile realm settings that live in the realm.** Realm SMTP
  (`smtpServer`) and `loginTheme` are realm data, so environment or image
  changes never reach an existing realm; reconcile each with an idempotent
  `kcadm.sh update … -s` step.
- **Rotate a leaked realm secret inside the realm.** For the same reason, a
  changed environment variable or a re-run of an idempotent seed leaves an
  imported realm on the old keys and client secrets. Rotate through the admin
  console or REST API (a client secret has its own regenerate action) in
  dependency order: realm keys first (add a new key provider at a higher
  priority, or at the same priority with the old one made passive, and remove
  the old one once tokens have moved; tokens signed by a removed key stop
  validating and inactive users re-authenticate), then any client that can
  administer the realm, then the rest. Verify the rotation in the realm itself,
  not in the environment or the seed file.
- **Run boot-time `kcadm` migrations defensively**: start the server in the
  background, wait for readiness, re-authenticate before each step (master
  tokens are short-lived), and stop the server if a step fails.
- **Back up the database before every upgrade.** A version bump migrates the
  schema one way; reverting the image tag is not a rollback. Observed in
  practice: the community edition patches only the current minor, so a
  security fix can force a cross-minor upgrade with its migration.
- **Set the expected audience on every resource server.** Many validators skip
  `aud` when it is left empty, which reopens "any token from this realm"
  access. A bearer-only client can exist purely as an audience target.
- **Pin the event log level when logs ship to a shared aggregator.** Events
  carry the user, client and source address; raising the success level logs
  every successful login.
- **Expose `/lb-check`** with the public paths; upstream lists it for external
  load-balancer checks.
- **Enable brute-force protection and keep action-token lifespans short.**
  Invitation, verify-email, and reset-credential tokens are bearer credentials
  for an account.

## General pitfalls
- **A project that gates boot on mail-configuration validation, or on start-up
  migrations, turns a mail typo into an authentication outage.** Keycloak keeps
  SMTP settings per realm and does not itself document refusing to start on
  them; the failure comes from a pre-flight step in the project's own
  entrypoint (validate, then exit non-zero) or from fail-closed migrations.
  Where authentication gates everything, decide deliberately whether a mail
  typo should be able to stop the platform.
- **Issuer mismatch is the classic integration failure.** A token minted with an
  externally-facing issuer URL is presented to a service that resolves the server
  internally; validation fails on one side or the other. Reconcile front-channel
  and back-channel URLs explicitly instead of letting each hop guess.
- **A realm export stamps the version of the server that produced it** inside the
  JSON. That is export metadata, not the running server's version. Never read a
  pin from it.
- **Recreating the container re-runs the entrypoint**, including any realm
  reconciliation it performs. Everything the entrypoint does must be idempotent,
  or an ordinary restart corrupts realm state.
- **Audience is not automatic.** A token issued to a front-end client is not
  valid at a downstream service just because both live in the same realm; the
  audience has to be arranged through a client scope or audience mapper, or the
  resource server rejects a token that otherwise looks perfect.
- **A public client has no secret.** Embedding a confidential client's secret in
  a browser bundle does not make the client confidential; it publishes the
  secret.
- **The development start mode is not a deployment mode.** It relaxes transport
  and hostname strictness for convenience; carrying it into a real environment
  ships those relaxations with it.
- **Older major lines exposed configuration, hostname handling, and the
  build/runtime split differently.** Recipes found in the wild are frequently
  written against a different line than the one you are running. Confirm against
  the pin in use.
- **Readiness is not "accepting connections".** Observed in practice: on the
  26 line the server accepted connections before it was ready (an asynchronous
  bootstrap); gate dependents on `/health/ready` on the management port, not on
  the TCP port.
- **Egress the server lacks fails late.** SMTP, external identity-provider
  metadata and JWKS lookups fail on first use with `UnknownHostException`, not
  at start. Plan the egress path (an L4 forwarder that keeps TLS end to end is
  one shape). A mail check that reads only settings and files never opens a
  socket, so it reports valid while no route exists; prove the path with one
  real send from inside the container. Attaching the server to a general
  outbound network cures the symptom by granting unrestricted egress; a
  one-destination forwarder does not.
- **A strict edge CSP breaks login themes.** A no-nonce application CSP
  applied to the login paths, or hiding the server's own CSP, breaks
  inline-script themes; exclude the identity paths from the edge policy.
- **The temporary bootstrap admin stays** until someone removes it.
- **`OTEL_*` variables do not govern it.** Observed in practice: a global
  `OTEL_SDK_DISABLED` did not silence its tracing, which retried an absent
  collector indefinitely; use the server's own tracing options.

## Testing
- Without a configured hostname the issuer follows the request URL and port,
  so a test harness with a random mapped port changes `iss` on every run; set
  the hostname, or derive the expected issuer from the mapped port.
- Wait on `/health/ready` (management port) before seeding or calling the
  server.
- Run realm migrations twice in a test to prove idempotence.
- Assert a token from one client is rejected by a resource server that
  expects another audience.

## Security defaults
- The production start mode requires a hostname and TLS (or an explicit proxy
  configuration); development mode relaxes both.
- Forwarded headers are ignored unless the proxy-headers option is set.
- Health and metrics live on the management port, off the public listener.
- Brute-force detection is a realm setting to enable deliberately.
- The bootstrap admin is temporary by design.

## Operational behaviour
- Start-up runs database migrations after a version bump; they are one-way.
- Realm import at start skips realms that exist.
- Recreating the container re-runs the entrypoint and any reconciliation in
  it.
- Readiness comes from `/health/ready`; plan two or more instances for
  availability.

## Interop
- The edge proxy and its header rules: [`nginx.md`](nginx.md).
- A development mail catcher for realm email: [`smtp4dev.md`](smtp4dev.md).
- Its database: [`postgres.md`](postgres.md).

## Major lines
- **WildFly to Quarkus distribution**: the context path changed from `/auth`
  to `/`, configuration moved to `KC_*` options and the build-time versus
  runtime split appeared.
- **25 line and later**: health and metrics are served on the management
  interface, no longer on the main server port (the 25 release notes).
- **26 line**: the bootstrap admin variables are `KC_BOOTSTRAP_ADMIN_*`
  (earlier lines used `KEYCLOAK_ADMIN*`, observed in practice). Observed in
  practice: provider compile-time jars sit under
  `/opt/keycloak/lib/lib/{main,boot}/` in the image.

## Upstream docs
- https://www.keycloak.org/documentation
- https://www.keycloak.org/server/containers
- https://quay.io/repository/keycloak/keycloak
- https://www.keycloak.org/server/reverseproxy
- https://www.keycloak.org/server/management-interface
- https://www.keycloak.org/observability/health
- https://www.keycloak.org/server/bootstrap-admin-recovery
- https://www.keycloak.org/server/vault
- Server administration (rotating keys, client secret rotation):
  https://www.keycloak.org/docs/latest/server_admin/
- Release notes: https://www.keycloak.org/docs/latest/release_notes/index.html
