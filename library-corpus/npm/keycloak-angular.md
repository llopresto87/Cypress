# keycloak-angular — npm

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
Angular DI integration for Keycloak. Wires the `keycloak-js` adapter into an Angular app: application-wide provider setup, automatic token refresh, an HTTP interceptor that attaches Bearer tokens to outgoing requests based on URL-pattern conditions, a role-based structural directive for conditional rendering, a route `CanActivate` guard factory, and a reactive Keycloak event signal. Peer-depends on `keycloak-js`.

## Core API / usage shape
- `provideKeycloak` and its companion functional providers configure Keycloak application-wide. The NgModule-era symbols (`KeycloakService`, `KeycloakAngularModule`, `KeycloakBearerInterceptor`, `KeycloakAuthGuard`) are deprecated and kept only for backward compatibility.
- `createInterceptorCondition` / `IncludeBearerTokenCondition` build URL-pattern conditions for the bearer-token interceptor.
- `createAuthGuard` produces a route guard factory that receives `AuthGuardData` (with `grantedRoles` = realmRoles + resourceRoles).

## Idioms & best practices
- Use `provideKeycloak` for application-wide setup rather than the legacy NgModule API.

## General pitfalls
- **Over-broad interceptor `urlPattern` leaks tokens:** the interceptor attaches the Bearer token to any request matching the regex, so an overly broad pattern leaks the token to unintended hosts. Derive patterns from your specific API/Keycloak host URLs rather than a static broad wildcard.
- **Angular-major coupling:** only the Angular-aligned latest major is actively supported, so pin the keycloak-angular major that matches the app's Angular major; an older or mismatched major risks compilation incompatibilities. Verify that alignment rather than trusting a green install — `../language/angular.md` owns why a drifted `@angular/*`-family install can still resolve.

## Upstream docs
- Repo: https://github.com/mauriciovigolo/keycloak-angular
- README: https://github.com/mauriciovigolo/keycloak-angular/blob/main/README.md
- Provider docs: https://github.com/mauriciovigolo/keycloak-angular/blob/main/docs/provide.md
- Interceptor docs: https://github.com/mauriciovigolo/keycloak-angular/blob/main/docs/interceptors.md
