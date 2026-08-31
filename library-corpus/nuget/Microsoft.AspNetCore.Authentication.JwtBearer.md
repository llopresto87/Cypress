# Microsoft.AspNetCore.Authentication.JwtBearer — nuget

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
ASP.NET Core's **bearer-token authentication handler**. It validates JWTs issued
by an external identity provider (OIDC / OAuth2) on incoming requests and turns a
valid token into a `ClaimsPrincipal` for the rest of the pipeline. It is a
*consumer* of tokens, not an issuer — the identity provider owns issuance, keys,
and lifetimes.

## Core API / usage shape
- Scheme registration:
  `services.AddAuthentication().AddJwtBearer(options => { options.Authority = ...; options.Audience = ...; })`
  — the authority identifies the trusted issuer, the audience identifies this API
  as the intended recipient.
- Validation is driven by the issuer's signing-key and algorithm configuration,
  commonly auto-discovered from the issuer's metadata endpoint rather than
  hard-configured, so key rotation at the provider does not require a redeploy.
- `TokenValidationParameters` is the explicit knob set (issuer, audience,
  lifetime, signing key) when metadata discovery is not used or must be
  overridden.
- The `OnTokenValidated` event, or a claims-transformation step, is the idiomatic
  place to **reshape claims after validation** — for example flattening a
  provider-specific nested role claim into the role claim type the app's
  authorization policies expect.
- Authorization is a separate concern layered on top: the handler establishes
  *who*, policies and `[Authorize]` decide *what*.

## Idioms & best practices
- Do claims reshaping once, at the validation hook, so every downstream policy
  and handler sees one canonical claim shape.
- Express access rules as named authorization policies rather than scattered role
  string comparisons, so the token's claim shape has exactly one consumer.

## General pitfalls
- **Authentication is opt-in, and opting out looks like success:** schemes are
  registered per service and enforcement is per endpoint. A service that never
  registers the JWT bearer scheme, or an endpoint group that never has
  `[Authorize]`/a fallback policy applied, serves **every route unauthenticated**
  — with no warning, no startup error, and passing tests. The failure mode of
  misconfigured authentication here is an open API, not a broken one, so absence
  of auth must be tested for positively (assert that an unauthenticated request
  is rejected) rather than assumed from the presence of the registration code.

## Upstream docs
- https://learn.microsoft.com/en-us/aspnet/core/security/authentication/configure-jwt-bearer-authentication
- https://github.com/dotnet/aspnetcore
- https://www.nuget.org/packages/Microsoft.AspNetCore.Authentication.JwtBearer
