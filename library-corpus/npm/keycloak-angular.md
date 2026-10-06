# keycloak-angular — npm

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions — for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
Angular DI integration for Keycloak. Wires the `keycloak-js` adapter into an Angular app: application-wide provider setup, automatic token refresh, an HTTP interceptor that attaches Bearer tokens to outgoing requests based on URL-pattern conditions, a role-based structural directive for conditional rendering, a route `CanActivate` guard factory, and a reactive Keycloak event signal. Peer-depends on `keycloak-js`.

The page covers the npm package `keycloak-angular`. Upstream home: the `mauriciovigolo/keycloak-angular` repository, whose README and `docs/` folder are the documentation. No separate documentation site exists.

## Install, setup and configuration
Install both packages: `npm install keycloak-angular keycloak-js`. `keycloak-js` is a peer dependency, so the app picks the adapter version; the README relays Keycloak's advice to match it to the server version.

Add `provideKeycloak(options)` to the `providers` of the `ApplicationConfig`. It returns `EnvironmentProviders`. The options:

- `config`: the adapter configuration, `{ url, realm, clientId }`.
- `initOptions` (optional): the `keycloak-js` `init()` options, such as `onLoad: 'check-sso'` and `silentCheckSsoRedirectUri`. When present, the library runs `init()` at startup through Angular's `provideAppInitializer`. Leave it out to call `keycloak.init()` yourself at a time you choose.
- `providers` (optional): extra Angular providers, for example the interceptor configuration or the services a feature needs.
- `features` (optional): composable features. The one documented today is `withAutoRefreshToken`.

For a silent `check-sso`, serve a static `silent-check-sso.html` from the app's `public` or `assets` folder; [`keycloak-js.md`](keycloak-js.md) describes the page.

`withAutoRefreshToken(options)` needs `AutoRefreshTokenService` and `UserActivityService` in `providers`. Its options and defaults:

- `sessionTimeout`: 300000 ms. Inactivity longer than this counts as an expired session.
- `onInactivityTimeout`: `'logout'` (default), `'login'` or `'none'`.
- `logoutOptions` and `loginOptions`: passed to `keycloak.logout()` or `keycloak.login()` when the timeout action runs.

Interceptors are configured through injection tokens:

- `INCLUDE_BEARER_TOKEN_INTERCEPTOR_CONFIG` takes an array of `IncludeBearerTokenCondition` (`urlPattern: RegExp`, optional `httpMethods`), usually built with `createInterceptorCondition<IncludeBearerTokenCondition>(...)`.
- `CUSTOM_BEARER_TOKEN_INTERCEPTOR_CONFIG` takes an array of `CustomBearerTokenCondition`, whose `shouldAddToken(req, next, keycloak)` returns `Promise<boolean>`.
- Both condition types accept `bearerPrefix` (default `'Bearer'`), `authorizationHeaderName` (default `'Authorization'`) and `shouldUpdateToken(req)`.

To load the Keycloak settings from a file at runtime, fetch it before `bootstrapApplication` and build the providers from the result. Upstream ships an example project for this.

## Core API / usage shape
- `provideKeycloak` and its companion functional providers configure Keycloak application-wide. The NgModule-era symbols (`KeycloakService`, `KeycloakAngularModule`, `KeycloakBearerInterceptor`, `KeycloakAuthGuard`) are deprecated and kept only for backward compatibility.
- The `keycloak-js` instance is injectable: `inject(Keycloak)` returns the instance `provideKeycloak` created, so components and services call the adapter directly with no wrapper service.
- `includeBearerTokenInterceptor` is a functional interceptor, registered with `provideHttpClient(withInterceptors([includeBearerTokenInterceptor]))`. For a request whose URL and method match a condition, it refreshes the token if needed and sets the header. Other requests pass unchanged. `customBearerTokenInterceptor` does the same, with the decision made by `shouldAddToken`.
- `createInterceptorCondition` / `IncludeBearerTokenCondition` build URL-pattern conditions for the bearer-token interceptor.
- `createAuthGuard` produces a route guard factory that receives `AuthGuardData` (with `grantedRoles` = realmRoles + resourceRoles).
- `createAuthGuard<CanActivateFn>(isAccessAllowed)` (or `<CanActivateChildFn>`) calls `isAccessAllowed(route, state, authData)`. `AuthGuardData` also carries the `keycloak` instance and the `authenticated` flag. The function returns `boolean` or a `UrlTree`, so a denied route can redirect, for example to `router.parseUrl('/forbidden')`.
- `*kaHasRoles="['role-a', 'role-b']"` renders its content when the user holds any of the listed roles. `kaHasRolesResource` names the client whose resource roles to check (default: the app's client id); `kaHasRolesCheckRealm: true` also checks realm roles. Import `HasRolesDirective` in the component.
- `KEYCLOAK_EVENT_SIGNAL` is an Angular signal of adapter events. Read it inside an `effect`, compare `event.type` with `KeycloakEventType` values (`Ready`, `AuthLogout`, `AuthRefreshError`, `TokenExpired` and the other adapter callbacks), and read typed arguments with `typeEventArgs<...>(event.args)`.

## Idioms & best practices
- Use `provideKeycloak` for application-wide setup rather than the legacy NgModule API.
- Derive the bearer-token URL patterns from the runtime configuration's API URL, and the Keycloak URL where needed, so a pattern moves with the deployment. Observed in practice as the way to avoid the over-broad-pattern leak below.
- Wrap `createAuthGuard` around a refresh. Observed in practice: the access function first awaits `keycloak.updateToken(30)` and logs the user out when that rejects, then checks `grantedRoles` against the route's data. Upstream's guard example checks roles only.
- Observed in practice: `sessionTimeout` is derived from the same idle-timeout setting the server session uses, minus a margin, so the client acts before the server ends the session.
- Use the role directive for presentation only. Observed in practice alongside server-side role checks: hiding a button does not stop a direct request, so the API must enforce the same role.
- React to `AuthRefreshError` and `TokenExpired` through the event signal in one place, for example the root component.

## General pitfalls
- **Over-broad interceptor `urlPattern` leaks tokens:** the interceptor attaches the Bearer token to any request matching the regex, so an overly broad pattern leaks the token to unintended hosts. Derive patterns from your specific API/Keycloak host URLs rather than a static broad wildcard.
- **Angular-major coupling:** only the Angular-aligned latest major is actively supported, so pin the keycloak-angular major that matches the app's Angular major; an older or mismatched major risks compilation incompatibilities. Verify that alignment rather than trusting a green install. `../language/angular.md` owns why a drifted `@angular/*`-family install can still resolve.
- The library adds no bearer token by default. An app that registers no interceptor, or provides no conditions, sends its API calls without a token.
- Only the interceptor attaches the token. Requests made outside `HttpClient`, such as a hand-written `fetch` or a WebSocket, need their own `updateToken` call; see [`keycloak-js.md`](keycloak-js.md).
- `withAutoRefreshToken` depends on `AutoRefreshTokenService` and `UserActivityService`. Upstream requires both in the `providers` of the same `provideKeycloak` call.
- Automatic refresh reacts to the adapter's `TokenExpired` event. The token is not renewed unless something asks for it, and that is the gap the feature fills.
- When `initOptions` is omitted, nothing calls `init()` for you, and the adapter stays uninitialized until the app does.
- A polled authenticated endpoint refreshes the token on every match and keeps an idle user signed in. The NgModule-era docs name this case; the `shouldUpdateToken` hook on a condition can exclude such requests from refreshing.

## Testing
Upstream documents no testing guidance for consumers, and none was observed in practice. Its repository ships runnable example projects (standalone, NgModule, runtime config) that show the wiring end to end.

## Security defaults
- No token leaves the app unless a condition says so. The interceptors are opt-in, and the include interceptor matches only the URL patterns and methods you list.
- A broad `urlPattern`, or a `shouldAddToken` that returns `true` too freely, sends the user's access token to every host it matches.
- The NgModule-era interceptor attached the token to every `HttpClient` request and relied on an exclusion list. The 19 line removed that model, because a missed exclusion sent tokens to external services.
- The role directive and route guards run in the browser. They shape the UI and navigation; they do not protect data.
- With `withAutoRefreshToken` on, its defaults log an idle user out after 300000 ms without activity.

## Operational behaviour
- Startup: with `initOptions`, `init()` runs in the app initializer, so bootstrap waits for `init()` to settle. The event signal exists from the start of the application, before the adapter has initialized.
- Activity tracking: `UserActivityService` watches mouse movement, key presses, touch starts and clicks.
- On `TokenExpired`, an active user gets a refreshed token, and a user idle longer than `sessionTimeout` gets the `onInactivityTimeout` action.
- Per request, a matching interceptor condition may refresh the token before it sets the header. `shouldUpdateToken` decides that per request.
- Failure: a failed refresh reaches the app as an `AuthRefreshError` event on the signal.

## Interop
- [`keycloak-js.md`](keycloak-js.md): the adapter this library wraps; init options, token methods and browser limits live there.
- [`../language/angular.md`](../language/angular.md): the framework, standalone providers, `provideAppInitializer`, functional interceptors and guards.
- [`../container/keycloak.md`](../container/keycloak.md): the server, realm, client and role setup that the guards and directive read.
- [`rxjs.md`](rxjs.md): the NgModule-era event stream was an RxJS subject; the current API uses Angular signals.

## Major lines
From the 19 line, the library's major version equals the Angular major it supports. Earlier lines had their own numbering. The README table pairs Angular 18 with the 16 line, Angular 17 with the 15 line, Angular 16 with the 14 line and Angular 15 with the 13 line, and lists `keycloak-js` 18 to 26 as compatible with the current lines. Only the newest Angular line gets new features; the one before it gets bug fixes.

### 19 line
The rewrite to Angular's functional style:
- `provideKeycloak` replaces `KeycloakAngularModule` plus an `APP_INITIALIZER` factory.
- `inject(Keycloak)` replaces the `KeycloakService` wrapper.
- Interceptors are opt-in and configured by injection tokens. The old exclude-URL configuration is removed.
- `createAuthGuard` replaces the `KeycloakAuthGuard` class.
- Events moved from the `keycloakEvents$` RxJS subject to `KEYCLOAK_EVENT_SIGNAL`. The old types were renamed `KeycloakEventLegacy` and `KeycloakEventTypeLegacy`.
- `KeycloakAngularModule`, `KeycloakService`, `KeycloakAuthGuard` and `KeycloakBearerInterceptor` are deprecated but still shipped. The migration guide announced their removal for a later line.

### 20 line
A security fix: the custom bearer-token interceptor evaluates asynchronous conditions correctly. Upstream's release notes name the custom interceptor.

### Before the 19 line
NgModule only: `KeycloakService.init({ config, initOptions, ... })` in an `APP_INITIALIZER`, a `KeycloakAuthGuard` subclass, and an interceptor that added the token to every `HttpClient` request unless `shouldAddToken` or `bearerExcludedUrls` excluded it.

## Upstream docs
- Repo: https://github.com/mauriciovigolo/keycloak-angular
- README: https://github.com/mauriciovigolo/keycloak-angular/blob/main/README.md
- Provider docs: https://github.com/mauriciovigolo/keycloak-angular/blob/main/docs/provide.md
- Interceptor docs: https://github.com/mauriciovigolo/keycloak-angular/blob/main/docs/interceptors.md
- Features (`withAutoRefreshToken`): https://github.com/mauriciovigolo/keycloak-angular/blob/main/docs/features.md
- Directives: https://github.com/mauriciovigolo/keycloak-angular/blob/main/docs/directives.md
- NgModule (deprecated) setup: https://github.com/mauriciovigolo/keycloak-angular/blob/main/docs/ngmodule.md
- Migration guide to the 19 line: https://github.com/mauriciovigolo/keycloak-angular/blob/main/docs/migration-guides/v19.md
