# Aspire.Hosting.Keycloak — nuget

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions — for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
Aspire's Keycloak integration: an AppHost resource that runs Keycloak (the
`quay.io/keycloak/keycloak` image) as part of the application model, and a
client library that points ASP.NET Core authentication at it by service name.
Both packages are published as previews only (no stable release on NuGet);
upstream marks the integration "Preview". MIT licensed, source in the
Aspire repository on GitHub (`microsoft/aspire`, as its READMEs link it),
docs at `aspire.dev`. The packages this page covers:

- `Aspire.Hosting.Keycloak`: the hosting integration (`AddKeycloak` and its
  builder methods). Needed in the AppHost project.
- `Aspire.Keycloak.Authentication`: the client integration
  (`AddKeycloakJwtBearer`, `AddKeycloakOpenIdConnect`). Needed in an API or web
  project that validates Keycloak tokens or signs users in.

The Keycloak server's own configuration (hostname, proxy, TLS, realms) is the
image's concern; [`keycloak.md`](../container/keycloak.md) covers it.

## Install, setup and configuration
- AppHost: `aspire add Aspire.Hosting.Keycloak`, or `dotnet add package
  Aspire.Hosting.Keycloak --prerelease`. Service projects: `dotnet add package
  Aspire.Keycloak.Authentication --prerelease`.
- `builder.AddKeycloak(name, port?, adminUsername?, adminPassword?)` adds the
  resource. What it sets up, from the source:
  - an HTTP endpoint on container port 8080 (host port `port`, or a random
    one), and a separate `management` endpoint on 9000 that references
    exclude;
  - an HTTP health check on the management endpoint's `/health/ready`, with
    `KC_HEALTH_ENABLED=true`;
  - `KC_BOOTSTRAP_ADMIN_USERNAME` and `KC_BOOTSTRAP_ADMIN_PASSWORD` from the
    parameters. With no username parameter the admin user is `admin`; with no
    password parameter Aspire creates a generated secret parameter
    `<name>-password`, kept in the AppHost's user secrets under
    `Parameters:<name>-password`. (The docs page names the variables
    `KEYCLOAK_ADMIN` / `KEYCLOAK_ADMIN_PASSWORD`; the source sets the
    `KC_BOOTSTRAP_*` names.)
  - the arguments `start-dev` in run mode and `start` when publishing, both
    followed by `--import-realm`;
  - an OTLP exporter (`WithOtlpExporter`, which also enables Keycloak's
    `opentelemetry` feature);
  - in run mode, when a TLS certificate is configured for the resource, the
    primary endpoint switches to HTTPS on container port 8443, with the
    certificate passed through `KC_HTTPS_*` variables.
- Builder methods: `WithDataVolume(name?)` and `WithDataBindMount(path)` mount
  `/opt/keycloak/data`; `WithRealmImport(path)` copies realm JSON files into
  `/opt/keycloak/data/import`; `WithEnabledFeatures(...)` /
  `WithDisabledFeatures(...)` set `KC_FEATURES` / `KC_FEATURES_DISABLED`;
  `WithDockerfile(dir)` builds a custom image while keeping `AddKeycloak`'s
  defaults (no extra `WithArgs("start", "--import-realm")` needed).
- `WithReference(keycloak)` on a project gives it the service-discovery
  connection named after the resource, which the client integration resolves.
- Use a stable host port in development. Browser cookies hold OIDC tokens whose
  authority URL includes the port, and they outlive the AppHost run.
- A database: the Community Toolkit's
  `CommunityToolkit.Aspire.Hosting.Keycloak.Extensions` adds `WithPostgres(db)`,
  which passes the JDBC URL and credentials and makes Keycloak wait for the
  database.
- An existing Keycloak instead of a container: `AddConnectionString("keycloak",
  ...)` in the AppHost, referenced the same way.

## Core API / usage shape
- AppHost:
  ```csharp
  var keycloak = builder.AddKeycloak("keycloak", 8080)
      .WithDataVolume()
      .WithRealmImport("./Realms");
  builder.AddProject<Projects.Api>("api").WithReference(keycloak).WaitFor(keycloak);
  ```
- API (resource server): `builder.Services.AddAuthentication()
  .AddKeycloakJwtBearer(serviceName: "keycloak", realm: "<realm>", options =>
  { options.Audience = "<api-client>"; })`. It registers the JwtBearer
  handler, sets `Authority` to `https+http://<serviceName>/realms/<realm>`, and
  uses a named `HttpClient` (`KeycloakBackchannel`) from `IHttpClientFactory`
  as the metadata backchannel, so service discovery resolves the host.
- Web app (interactive sign-in):
  `AddKeycloakOpenIdConnect(serviceName, realm, options => { options.ClientId =
  ...; options.ResponseType = OpenIdConnectResponseType.Code; })`, same
  authority and backchannel.
- Each has overloads taking an authentication scheme name, for apps with more
  than one handler.

## Idioms & best practices
- Keep realms as code: export the realm JSON and import it at startup, rather
  than configuring through the admin console. Use `WithRealmImport` in
  development; for a published app, bake the files into a custom image with
  `WithDockerfile` (`COPY realms/*.json /opt/keycloak/data/import/`), seed
  through the Admin REST API from an init job, or manage realms with
  infrastructure as code. `WithRealmImport` is development-only and not
  supported by `aspire publish` / `aspire deploy`.
- Realm JSON can use `${ENV_VAR}` placeholders, which Keycloak resolves from
  environment variables at import. Pass per-environment values (redirect URIs,
  web origins, client secrets) through `WithEnvironment` instead of editing the
  JSON per environment.
- Pass admin credentials as parameters with `secret: true`, never as literal
  defaults in the AppHost.
- Set the API's `Audience` to a dedicated client for that API, so a token
  issued for another client of the realm is not accepted.
- Make `RequireHttpsMetadata` depend on the environment explicitly (true
  outside development), and decide in production how the HTTPS authority is
  reached (see the pitfalls).

## General pitfalls
- **The service-discovery authority fails JwtBearer's HTTPS check.** With
  `RequireHttpsMetadata = true` (ASP.NET Core's default), the JwtBearer
  post-configuration throws unless the metadata address starts with the
  literal `https://`, and the integration's `https+http://` pseudo-scheme does
  not. Upstream's docs show turning `RequireHttpsMetadata` off in development
  and setting an explicit `https://` `Authority` in production. Observed in
  practice, a third way: rewrite the authority's scheme from `https+http://`
  to `https://` while keeping the service name as the host. Service discovery
  still resolves the name, but now only to an HTTPS endpoint (`https://name`
  means "HTTPS only" in Aspire's scheme table), so the guard passes and a
  deployment that publishes only a plain-HTTP Keycloak endpoint fails loudly
  instead of downgrading. Upstream documents the scheme table and the guard,
  not this combination.
- **A host address handed to a container is the container's view, not the
  browser's.** When a container resource (Keycloak) gets an endpoint
  reference to a host-based project, Aspire resolves it to an address
  reachable from the container network (its container tunnel, or
  `host.docker.internal` where the tunnel is disabled). A realm-import
  placeholder for a browser-facing value (a redirect URI, a web origin) must
  not take that reference. Observed in practice: placeholders fed from
  endpoint references produced redirect URIs on the container-side host, and
  Keycloak rejected the browser's real callback; passing the browser-facing
  origin (for example `https://localhost:<port>`) fixed it. Also observed: a
  placeholder whose variable was not set was imported as the literal text
  `${...}`, registering it as a redirect URI. Keycloak's import docs describe
  the placeholders but not the unset case.
- **A data volume shadows a baked import directory.** The data volume and the
  data bind mount are mounted at `/opt/keycloak/data`, and the import
  directory is `/opt/keycloak/data/import`. On a custom image that copies
  realms into the import directory, also mounting the data volume hides those
  files, and `--import-realm` finds nothing, with no error. Observed in
  practice on a published app; it follows from the two paths upstream
  documents. When identity state lives in a database, a published Keycloak
  needs no data volume.
- **Realm import skips realms that already exist.** Keycloak imports a file
  only if the realm is not present, to preserve state across restarts. With a
  persistent data volume (or database), editing the realm JSON changes
  nothing after the first import; delete the volume, or run Keycloak's
  `import` command, to re-create it.
- **Changed admin credentials do not apply to an existing volume.** Upstream:
  the admin credentials are stored in the data volume, so after changing them
  Keycloak will not accept the new ones until the volume is deleted.
- **Publish mode starts Keycloak in its production profile** (`start`), which
  requires either `--hostname` or `--hostname-strict false`, and HTTPS or an
  explicit `--http-enabled true`. Behind a TLS-terminating proxy the published
  resource therefore needs the hostname and proxy-header settings
  ([`keycloak.md`](../container/keycloak.md)), or redirect URIs and token issuers come out wrong.
  Run mode uses `start-dev`, where `hostname-strict` is false by default, so a
  configuration that works locally can fail only when published.

## Testing
- An AppHost-based integration test (`Aspire.Hosting.Testing`) starts the real
  Keycloak container with the realm import, which tests the realm JSON and the
  token validation together; it needs a container runtime and the image's
  startup time.
- Wait on the resource (`WaitFor(keycloak)`) before running anything that
  fetches the discovery document; the health check on `/health/ready` gates
  it.

## Security defaults
- The admin password is a generated secret unless a parameter is supplied; a
  parameter whose default value is a fixed literal (`admin`, say) reopens the
  well-known-credential hole in every environment that does not override it.
- `start-dev` (run mode) is Keycloak's development profile: HTTP and relaxed
  hostname checking. It is for the local loop only.
- `RequireHttpsMetadata = false` lets the API fetch keys over plain HTTP, so
  anyone on the path can substitute signing keys. Keep it to development.
- `--hostname-strict false` makes Keycloak build URLs from the request's
  `Host` / `X-Forwarded-Host` headers; upstream warns that untrusted clients
  able to set them can inject hosts into generated URLs. Use it only behind a
  proxy that overwrites those headers.
- Realm-file placeholders can reference any environment variable; upstream
  warns to make sure they do not expose sensitive values.
- The management endpoint (health, metrics) is excluded from references and
  should stay off public ingress; Keycloak's production guide also recommends
  exposing the admin console on a separate hostname.

## Operational behaviour
- Startup: the container runs `--import-realm`; Keycloak does not finish
  starting until the import is done, and with health enabled the readiness
  probe stays down during long initialization (database migrations), which is
  what `WaitFor` observes.
- With `WithLifetime(ContainerLifetime.Persistent)` and a data volume, the
  container and its state survive AppHost restarts, which avoids a re-import on
  every run (and is why realm edits stop applying; see the pitfalls).
- Shutdown and restart follow the AppHost; without a volume or database,
  every run starts again from the imported realm, and anything created at run
  time is gone.
- Telemetry flows to the AppHost's OTLP endpoint (the dashboard) through the
  `opentelemetry` feature `AddKeycloak` enables.

## Interop
- `Microsoft.AspNetCore.Authentication.JwtBearer.md`: the handler the client
  integration configures; audience, issuer and HTTPS-metadata semantics are
  its own.
- Aspire service discovery (`Microsoft.Extensions.ServiceDiscovery`) resolves
  the `https+http://` authority through the backchannel `HttpClient`, from the
  configuration `WithReference(keycloak)` injects; a project without that
  reference cannot resolve the name.
- Code running in the browser (a WebAssembly front end, a single-page app)
  cannot use service discovery; it signs in against a Keycloak URL the
  browser can reach, which is one more reason the browser-facing origin and
  the container-side address must be kept apart.
- `Aspire.Hosting.AppHost.md`: the AppHost model, parameters, `WaitFor` and
  container lifetimes.
- [`keycloak.md`](../container/keycloak.md) (container): the server this
  resource runs, with its hostname, proxy, realm-import, admin-email and
  health-endpoint behaviour.

## Major lines
- **Preview only.** Every published version of both packages is a
  prerelease that follows the Aspire release train, from the 8.x ".NET
  Aspire" line to the 13.x "Aspire" line. Preview APIs can change between
  releases; read the release notes of the Aspire version you move to.
- `WithRealmImport(path, isReadOnly)` is obsolete: it bind-mounted the folder.
  `WithRealmImport(path)` copies the files into the container instead, which
  is why it works with any container runtime in run mode and is unsupported in
  publish.

## Upstream docs
- https://aspire.dev/integrations/security/keycloak/
- https://github.com/microsoft/aspire/tree/main/src/Aspire.Hosting.Keycloak
- https://github.com/microsoft/aspire/tree/main/src/Components/Aspire.Keycloak.Authentication
- https://aspire.dev/fundamentals/service-discovery/
- https://aspire.dev/fundamentals/container-networking/
- https://www.keycloak.org/server/importExport
- https://www.keycloak.org/server/hostname
- https://www.keycloak.org/server/reverseproxy
- https://www.nuget.org/packages/Aspire.Hosting.Keycloak
- https://www.nuget.org/packages/Aspire.Keycloak.Authentication
