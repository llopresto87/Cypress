# keycloak — container

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a tool, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile / base-image tag.

## What it is
Keycloak is an open-source identity and access management server: an OAuth 2.0 /
OpenID Connect provider and SAML identity provider that owns users, credentials,
login flows, and token issuance for everything in front of it — browser
applications, mobile clients, and machine-to-machine callers. It is distributed
as a container image and configured declaratively, so in a containerized stack it
is normally a service of its own rather than a library linked into an
application.

The unit of isolation is the **realm**: a self-contained tenant holding users,
groups, roles, clients, client scopes, authentication flows, required actions,
themes, and mail settings. Applications register as **clients** — *public*
(a browser or mobile app that cannot keep a secret) or *confidential* (a
server-side app or service account that can).

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
  environment variables, or a configuration file — hostname, proxy and TLS
  behavior, database, health and metrics endpoints, logging.
- **Build-time vs runtime options.** The server distinguishes options baked into
  an optimized image by a build step from options read at start-up. Which
  category a given option falls into has moved between major lines; confirm
  against the pin in use rather than copying a flag list from elsewhere.
- **Vault.** Realm configuration may reference `${vault.<key>}` instead of
  holding a secret literally; a file-based vault resolves the reference from a
  mounted file named by realm and key.
- **SPI providers.** Most subsystems are pluggable behind a service provider
  interface — email sender, authenticators, event listeners, user federation. A
  provider is packaged as a jar, placed in the server's providers directory, and
  selected with `--spi-<spi>-provider=<id>`.
- **Themes.** Login, email, and account templates are overridable per realm.

## Idioms & best practices
- **Build a derived image when you need providers or themes**, rather than
  bolting them onto the stock image at run time. Compile a provider against the
  jars copied out of *the same server image that will run it* (a multi-stage
  build copying the server's own libraries), so there is no package-repository
  dependency and provider/server drift is impossible by construction — an
  incompatibility then surfaces at image-build time instead of as mail that
  silently never sends.
- **Treat realm import as bootstrap-only.** Startup import skips a realm that
  already exists, so editing the seed file alone never reaches an already
  provisioned environment. Carry every subsequent realm change as an explicit,
  idempotent, fail-closed migration step executed at start via the admin CLI or
  REST, and keep the seed and the migration set as one artifact.
- **Give each migration a durable idempotence marker** stored on the object it
  changes (a realm or client attribute, say), rather than re-deriving "has this
  already run?" from the state the migration itself sets — re-derivation breaks
  the moment an operator changes that state by hand.
- **Never update a realm with a whole-document PUT.** Submitting a full realm
  representation replaces it wholesale and silently drops whatever the submitted
  document omits — password policy, brute-force settings, token lifespans. Use
  per-field updates.
- **Keep secrets out of the environment.** Put a vault reference in the realm and
  mount the value; an SMTP or client secret in a plain environment variable is
  visible to anything that can inspect the container.
- **Decide the hostname configuration deliberately**, because the configured
  hostname is what the server stamps as the token issuer even for requests that
  arrive on an internal address. Every validator — browser-facing and internal —
  has to agree on that issuer string.
- **Enable brute-force protection and keep action-token lifespans short.**
  Invitation, verify-email, and reset-credential tokens are bearer credentials
  for an account.

## General pitfalls
- **An invalid mail configuration can stop the server from starting**, and a
  failed start-up migration aborts boot. In a deployment where authentication
  gates everything, a mail typo is an outage of the whole platform, not a
  degraded feature.
- **Issuer mismatch is the classic integration failure.** A token minted with an
  externally-facing issuer URL is presented to a service that resolves the server
  internally; validation fails on one side or the other. Reconcile front-channel
  and back-channel URLs explicitly instead of letting each hop guess.
- **A realm export stamps the version of the server that produced it** inside the
  JSON. That is export metadata, not the running server's version — never read a
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
  written against a different line than the one you are running — confirm against
  the pin in use.

## Upstream docs
- https://www.keycloak.org/documentation
- https://www.keycloak.org/server/containers
- https://quay.io/repository/keycloak/keycloak
