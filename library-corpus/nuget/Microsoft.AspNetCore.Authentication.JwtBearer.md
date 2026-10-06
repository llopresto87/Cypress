# Microsoft.AspNetCore.Authentication.JwtBearer — nuget

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions — for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
`Microsoft.AspNetCore.Authentication.JwtBearer` is ASP.NET Core's
**bearer-token authentication handler**. It validates JWTs issued by an
external identity provider (OIDC / OAuth2) on incoming requests and turns a
valid token into a `ClaimsPrincipal` for the rest of the pipeline. It is a
*consumer* of tokens, not an issuer: the identity provider owns issuance, keys,
and lifetimes. Licence: MIT; it ships from the `dotnet/aspnetcore` repository,
and token parsing and validation come from the Microsoft.IdentityModel
libraries it depends on.

## Install, setup and configuration
- `dotnet add package Microsoft.AspNetCore.Authentication.JwtBearer`, on the
  same major line as the ASP.NET Core runtime.
- Register the scheme and turn on the middleware:
  `builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
  .AddJwtBearer(o => { o.Authority = ...; o.Audience = ...; })`, then
  `app.UseAuthentication()` and `app.UseAuthorization()`. The default scheme
  name is `"Bearer"`; `AddJwtBearer("name", ...)` registers a named scheme.
- `JwtBearerOptions` is a named options type, keyed by the scheme name. What
  each setting means and what its default does:
  - `Authority`: the issuer's base URL. When `MetadataAddress` is empty, the
    handler derives it as `Authority` + `/.well-known/openid-configuration`.
  - `Audience`: copied into `TokenValidationParameters.ValidAudience` when
    that is empty.
  - `RequireHttpsMetadata` (default `true`): a metadata address that is not
    HTTPS makes the options fail with `InvalidOperationException` the first
    time the handler builds them. Turn it off only in development or test.
  - `TokenValidationParameters`: issuer, audience, lifetime and signing-key
    checks, with IdentityModel's defaults: `ValidateIssuer`,
    `ValidateAudience`, `ValidateLifetime`, `RequireSignedTokens` and
    `RequireExpirationTime` are `true`, `ValidateIssuerSigningKey` is `false`,
    and `ClockSkew` is five minutes. Issuers and keys from the metadata
    document are added to them per request.
  - `MapInboundClaims` (default `true`): renames short JWT claim types
    (`sub`, `role`) to the long `ClaimTypes` URIs. Set it to `false` to keep
    the names the token carries.
  - `SaveToken` (default `true`): stores the raw access token in the
    authentication properties after validation.
  - `IncludeErrorDetails` (default `true`): writes `error` and
    `error_description` into the `WWW-Authenticate` header of a `401`.
  - `RefreshOnIssuerKeyNotFound` (default `true`): a token signed with an
    unknown key triggers a metadata refresh, so a key rollover at the
    provider recovers without a restart.
  - `BackchannelTimeout` (default one minute), `AutomaticRefreshInterval` and
    `RefreshInterval`: how metadata is fetched and how often it is
    refreshed; the refresh defaults come from IdentityModel's
    `ConfigurationManager`.
  - `Configuration`: a static OpenID Connect configuration that replaces
    metadata discovery entirely.

## Core API / usage shape
- Scheme registration:
  `services.AddAuthentication().AddJwtBearer(options => { options.Authority = ...; options.Audience = ...; })`
  The authority identifies the trusted issuer; the audience identifies this API
  as the intended recipient.
- Validation is driven by the issuer's signing-key and algorithm configuration,
  commonly auto-discovered from the issuer's metadata endpoint rather than
  hard-configured, so key rotation at the provider does not require a redeploy.
- `TokenValidationParameters` is the explicit knob set (issuer, audience,
  lifetime, signing key, `ValidIssuers` and `ValidAudiences` for more than
  one) when metadata discovery is not used or must be overridden.
- The `OnTokenValidated` event, or a claims-transformation step
  (`IClaimsTransformation`), is the idiomatic place to **reshape claims after
  validation**, for example flattening a provider-specific nested role claim
  into the role claim type the app's authorization policies expect. A claims
  transformation may run more than once per request, so it must only add a
  claim that is not already there.
- Authorization is a separate concern layered on top: the handler establishes
  *who*, policies and `[Authorize]` decide *what*.
- The `OnMessageReceived` event decides where the token comes from. By default
  the handler reads the `Authorization: Bearer` header; an app can set
  `context.Token` from another surface, most commonly the `access_token` query
  parameter on a real-time hub path, because browsers cannot set headers on
  WebSocket or Server-Sent Events requests.
- The other events are `OnAuthenticationFailed`, `OnChallenge` (shape or
  suppress the `401`) and `OnForbidden` (the `403`).
- Several issuers in one API: either one scheme per issuer combined with
  `AddPolicyScheme` to pick the scheme per request, or separate APIs.

## Idioms & best practices
- Do claims reshaping once, at the validation hook, so every downstream policy
  and handler sees one canonical claim shape.
- Express access rules as named authorization policies rather than scattered role
  string comparisons, so the token's claim shape has exactly one consumer.
- Require authentication everywhere by default with a fallback policy
  (`AddAuthorizationBuilder().SetFallbackPolicy(new
  AuthorizationPolicyBuilder().RequireAuthenticatedUser().Build())`), then
  open public endpoints explicitly with `[AllowAnonymous]`.
- Validate signature, issuer, audience and expiry; the docs list these as
  the minimum for an API, and the defaults already check them. Prefer the
  defaults over explicit parameters.
- An API answers `401` or `403`. It never redirects to the identity provider;
  getting a token is the client's job.
- Use access tokens only. An ID token is for the client that signed the user
  in, never for calling an API.

## General pitfalls
- **Authentication is opt-in, and opting out looks like success:** schemes are
  registered per service and enforcement is per endpoint. A service that never
  registers the JWT bearer scheme, or an endpoint group that never has
  `[Authorize]`/a fallback policy applied, serves **every route unauthenticated**
  with no warning, no startup error, and passing tests. The failure mode of
  misconfigured authentication here is an open API, not a broken one, so absence
  of auth must be tested for positively (assert that an unauthenticated request
  is rejected) rather than assumed from the presence of the registration code.
- **Relaxing the options in a test needs `Configure`, not `PostConfigure`.**
  The framework's own `JwtBearerPostConfigureOptions` builds the metadata
  configuration manager, and checks `RequireHttpsMetadata`, in its
  post-configure step. The options factory runs every `Configure` before any
  `PostConfigure`, and post-configure steps run in registration order, so a
  test's `PostConfigure` that sets `RequireHttpsMetadata = false` or a new
  `Authority` runs after the manager already exists, or after the HTTPS check
  has already thrown. Use the named form,
  `services.Configure<JwtBearerOptions>(JwtBearerDefaults.AuthenticationScheme,
  o => { o.RequireHttpsMetadata = false; o.Authority = ...; })`; an unnamed
  `Configure<JwtBearerOptions>` targets the default options name, not the
  `"Bearer"` scheme, and changes nothing the handler reads.
- **A long-lived connection outlives its token.** The token is validated when a
  WebSocket or hub connection is established; by default the connection keeps
  working after the token expires, and after it is revoked. Where expiry must
  end access, have the server close connections on authentication expiry (the
  real-time hub's `CloseOnAuthenticationExpiration` option) and design for the
  client reconnecting with a fresh token.
- **A token in the query string lands in logs.** Servers and proxies commonly
  log request URLs. Limit the query-string fallback to the hub path that needs
  it, and keep access logs on that path from recording the query.
- The default `ClockSkew` of five minutes accepts a token for up to five
  minutes after its `exp`. A test that expects an expired token to fail must
  set `ClockSkew` lower or use a token expired by more than that.
- Claim names differ from the token. With `MapInboundClaims` left on, `sub`
  arrives as `ClaimTypes.NameIdentifier` and `role` as `ClaimTypes.Role`, so a
  policy that looks for `"role"` finds nothing.

## Testing
- Assert the negative path: an unauthenticated request to every protected
  route group gets `401`, and a token without the required claim gets `403`.
- For integration tests, either replace the scheme with a test-only handler
  (`Microsoft.AspNetCore.Mvc.Testing.md` owns that pattern), or keep the real
  handler and point it at a test issuer through named `Configure` (see the
  pitfall above). The `dotnet user-jwts` tool creates local development
  tokens.
- To learn what the handler accepts, drive the real handler offline as
  an oracle (`../../tool-corpus/testing/auth-parity-oracle.md` owns the
  technique). Build it bare: options with no `Authority` and no
  `MetadataAddress` create no configuration manager, so there is no metadata
  discovery and no network. Leave `JwtBearerEvents` off unless the question is
  about the surface an event adds, since an `OnMessageReceived` that reads the
  query string answers a different question from the header parse.
- In that oracle, the handler's answer to "accepted?" is
  `AuthenticateResult.Succeeded`. Whether the handler passed a string on to its
  token validator is only "extracted", and it passes on some strings that can
  never validate. The tool page owns why the difference matters and the
  loaded-version pin that goes with it.

## Security defaults
- On by default: HTTPS-only metadata, signature, issuer, audience and
  lifetime validation, and a metadata refresh when an unknown signing key
  appears.
- Every relaxation is a hole outside a test environment: `RequireHttpsMetadata
  = false` lets a network attacker serve signing keys;
  `RequireSignedTokens`, `ValidateIssuer`, `ValidateAudience` or
  `ValidateLifetime` set to `false` accept unsigned, foreign or expired
  tokens.
  The docs require such changes to stay in a dedicated, isolated test
  environment.
- `IncludeErrorDetails` (on by default) tells a caller why its token failed
  (expired, bad audience, unknown key). Turn it off where that detail should
  not reach clients.
- The handler does not create tokens. The docs advise against self-issued
  tokens outside tests, and for issuing they require asymmetric keys and a
  standard OpenID Connect or OAuth flow, never a username/password exchange.

## Operational behaviour
- Metadata (issuer and signing keys) is fetched over the backchannel on the
  first request that needs it, then cached and refreshed on the configured
  interval. The handler clones the validation parameters per request.
- The default token handler since the 8.x line keeps a "last known good"
  metadata, which protects the API when the provider publishes broken
  metadata.
- Startup does no network call. A wrong or unreachable `Authority` shows up
  on the first request that carries a token, not at boot, so a health check
  that sends no token cannot see it.
- The handler adds no state between requests apart from the metadata cache;
  scale-out needs nothing shared.

## Interop
- Authorization policies and `[Authorize]` consume the principal; the
  fallback-policy idiom above is the usual pairing.
- Real-time hubs: the `OnMessageReceived` query-string fallback and
  `CloseOnAuthenticationExpiration` (pitfalls above).
- Integration tests: `Microsoft.AspNetCore.Mvc.Testing.md`.
- Any OpenID Connect provider works through its metadata document; providers
  that put roles in nested claims need the reshaping step in Core API.

## Major lines

### 7.x line
- When only one authentication scheme is registered, it becomes the default
  scheme automatically.
- `dotnet user-jwts` arrives for creating local development tokens.

### 8.x line
- The default validator changes from `JwtSecurityTokenHandler` to
  `JsonWebTokenHandler` (listed under `TokenHandlers`), which is faster,
  async and keeps last-known-good metadata.
- `TokenValidatedContext.SecurityToken` is now a `JsonWebToken`. Code that
  casts it to `JwtSecurityToken` gets `null`; cast to `JsonWebToken`, or set
  `UseSecurityTokenValidators = true` to keep the old validators.
- `SecurityTokenValidators` is obsolete, and the default inbound claim map
  comes from `JsonWebTokenHandler.DefaultInboundClaimTypeMap`.

## Upstream docs
- https://learn.microsoft.com/en-us/aspnet/core/security/authentication/configure-jwt-bearer-authentication
- https://learn.microsoft.com/en-us/aspnet/core/signalr/authn-and-authz
- https://learn.microsoft.com/en-us/aspnet/core/fundamentals/configuration/options
- https://learn.microsoft.com/en-us/dotnet/core/compatibility/aspnet-core/8.0/securitytoken-events
- https://github.com/dotnet/aspnetcore
- https://www.nuget.org/packages/Microsoft.AspNetCore.Authentication.JwtBearer
