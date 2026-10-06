# keycloak-js — npm

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions — for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
`keycloak-js` is the browser-side OpenID Connect adapter for a Keycloak server. The `Keycloak` default export logs the user in and out, holds and refreshes the access, refresh and ID tokens, checks roles, and loads the user profile. It also supports Cordova hybrid apps and accepts a custom adapter for other runtimes. The page covers the npm package `keycloak-js`, including its `keycloak-js/authz` entry point. Apps often consume it through a framework wrapper such as `keycloak-angular` for route guards, bearer-token interception and role-based UI gating.

Upstream home: the JavaScript adapter guide on keycloak.org and the `keycloak/keycloak-js` repository.

## Install, setup and configuration
Install it with `npm install keycloak-js`.

The adapter needs a client registered in the Keycloak admin console. That client must be public (client authentication off), because a browser app has no safe place for a secret. Configure its valid redirect URIs and web origins as narrowly as you can. The server side of that setup belongs to [`../container/keycloak.md`](../container/keycloak.md).

Construct the adapter with `new Keycloak({ url, realm, clientId })`. Passing a URL to a JSON adapter file instead also works, but it costs one more request before `init()`, and upstream advises against it for that reason.

`init(options)` returns a promise that resolves to whether the user is authenticated. The options and their defaults:

- `onLoad`: `'login-required'` sends an unauthenticated user to the login page; `'check-sso'` authenticates only a user who already has a session and otherwise returns to the app unauthenticated. Without `onLoad` the adapter does not authenticate on its own; the app calls `login()`.
- `silentCheckSsoRedirectUri`: runs `check-sso` in a hidden iframe instead of a full redirect, so the app loads once. The URI must be a registered redirect URI, and the app itself must serve a small static page there that posts `location.href` back to the parent with `postMessage`. The adapter does not ship that page.
- `silentCheckSsoFallback`: default `true`. When the browser blocks the silent check, it falls back to a regular `check-sso` redirect. With `false`, `check-sso` is switched off entirely in that browser.
- `checkLoginIframe`: default `true`. It runs the session status iframe that detects single sign-out. `checkLoginIframeInterval` defaults to 5 seconds.
- `flow`: `'standard'` (authorization code, the default), `'implicit'` or `'hybrid'`.
- `responseMode`: `'fragment'` (default) or `'query'`. Upstream calls the fragment mode the safer choice.
- `pkceMethod`: `'S256'` by default; `false` switches PKCE off.
- `useNonce`: default `true`; adds a nonce that ties the authentication response to its request.
- `scope`: extra scopes for the login request. The adapter always adds `openid`, and a `scope` passed to `login()` overrides this one.
- `messageReceiveTimeout`: default 10000 ms; how long the adapter waits for a message from the server, for example during the third-party cookie check.
- `enableLogging`: default `false`.
- `redirectUri`, `locale`, and the `token`, `refreshToken`, `idToken` and `timeSkew` seeds for starting from known tokens.
- `adapter`: `'default'`, `'cordova'`, `'cordova-native'` or a custom object that implements the `KeycloakAdapter` interface.

Initialize the adapter before the client-side router starts. `init()` can rewrite the page URL, and a router that has already read it routes on the wrong address.

## Core API / usage shape
- Properties: `authenticated`, `token` and `tokenParsed`, `idToken` and `idTokenParsed`, `refreshToken` and `refreshTokenParsed`, `subject` (the user id), `realmAccess` and `resourceAccess` (the roles), and `timeSkew`, an estimate of the clock difference to the server.
- Session methods: `login(options)`, `logout({ redirectUri })`, `register()`, `accountManagement()`, and their URL builders `createLoginUrl`, `createLogoutUrl`, `createRegisterUrl` and `createAccountUrl`. `login()` options include `redirectUri`, `prompt`, `maxAge`, `loginHint`, `idpHint`, `scope`, `acr` and `acrValues` for step-up authentication, `action` (registration or an application-initiated required action) and `locale`.
- Token methods: `updateToken(minValidity)` refreshes the access token when it expires within `minValidity` seconds (5 when omitted; `-1` forces a refresh). It resolves to whether a refresh happened and rejects when the refresh fails. With the session iframe on, it also checks the session status. `isTokenExpired(minValidity)` only checks. `clearToken()` drops the authentication state and fires `onAuthLogout`.
- Role checks: `hasRealmRole(role)` and `hasResourceRole(role, resource)`. The resource defaults to the client id.
- `loadUserProfile()` resolves with the user's account profile.
- Callbacks, assigned as properties: `onReady`, `onAuthSuccess`, `onAuthError`, `onAuthRefreshSuccess`, `onAuthRefreshError`, `onAuthLogout` and `onTokenExpired`. Register them before calling `init()`.

The canonical call shape is to refresh first and send second:

```ts
try {
  await keycloak.updateToken(30);
} catch {
  await keycloak.login(); // or logout(), or clearToken(), by app policy
}
await fetch(url, { headers: { authorization: `Bearer ${keycloak.token}` } });
```

## Idioms & best practices
- Keep tokens in memory only. The adapter holds the access and refresh tokens in memory and never persists them, and upstream says an app must not persist them either, to prevent hijacking.
- Always `await updateToken(...)` before an authenticated call and handle the rejection path, typically by forcing a logout.
- When a channel other than plain HTTP needs a token (a WebSocket or real-time hub `accessTokenFactory`, a hand-written `fetch`), call `await updateToken(minValidity)` inside the token callback on every use. A `keycloak.token` captured once goes stale across reconnects. This was observed in practice with a real-time hub client; the hub client's own docs ask for the same thing, see [`microsoft-signalr.md`](microsoft-signalr.md).
- For a single-page app, upstream recommends silent `check-sso`: the app's resources load and parse once, with no full redirect after the check.
- Use the standard flow with PKCE, the default. Implicit and hybrid flows put the access token in the URL.
- In a framework app, construct one instance and share it through the framework's dependency injection. For Angular, `keycloak-angular` provides it; see [`keycloak-angular.md`](keycloak-angular.md).

## General pitfalls
- **Short-lived tokens:** calling APIs without first `updateToken`-ing risks requests with expired tokens.
- **Listener registration order:** listeners registered after `init()` miss early events; register them first.
- **`checkLoginIframe` can be disabled by the browser:** modern browsers' third-party-cookie / tracking protection can disable the session-status iframe, degrading cross-tab login/logout detection to redirect-based `check-sso`.
- When the browser blocks third-party cookies, a logout in another window reaches the app only at its next token refresh. Upstream suggests a short access-token lifespan so the app notices sooner.
- `onAuthLogout` fires only while the session iframe is on, or in Cordova mode. An app that relies on it for single sign-out loses the signal when the iframe is off or blocked.
- Silent `check-sso` and the session iframe also need TLS on both the Keycloak side and the app side in browsers that default cookies to `SameSite=Lax`.
- The implicit flow returns no refresh token. When the access token expires, the app must redirect to Keycloak again.
- Do not read Keycloak's session status cookie directly. Its format can change, and it belongs to the Keycloak server's URL, not the app's.
- A missing or unregistered silent redirect page makes silent `check-sso` fail. That page is app code, not adapter code.

## Testing
Upstream documents no testing guidance for the adapter. Observed in practice: end-to-end suites log in through the real Keycloak login page inside a per-test fixture, and create and delete disposable users through the server's admin REST API. [`playwright-test.md`](playwright-test.md) owns that fixture pattern.

## Security defaults
- The client is public by design. The adapter takes no client secret, so a secret placed in a browser bundle is published, not protected.
- Redirect URIs and web origins that are broader than needed are a security hole. Upstream asks for them to be as specific as possible.
- The defaults are the authorization code flow, PKCE with `S256`, a nonce check and the fragment response mode. Turning off PKCE or the nonce, or switching to `'query'`, removes a protection.
- The implicit and hybrid flows send the access token in the URL fragment, where it can leak through server logs and browser history.
- Tokens live in memory. Copying them into local storage or cookies undoes that protection.
- The `'cordova'` adapter renders the login page in an in-app browser that the app fully controls, so the app can read the user's credentials. Use `'cordova-native'` (the system browser) for apps the user may not trust.
- From the 26 line, the adapter requires a secure context (HTTPS, `localhost` or a `.localhost` domain), because it uses the Web Crypto API.

## Operational behaviour
- Startup: `init()` may redirect to Keycloak or open a hidden iframe before it resolves. In a browser that blocks third-party cookies, a regular `check-sso` adds a redirect at startup when the user is logged out.
- The session status iframe makes no network requests. It reads a status cookie every `checkLoginIframeInterval`.
- `timeSkew` is an estimate of the browser-to-server clock difference. Upstream calls it accurate enough to judge token expiry, and `init()` can seed it.
- Failure: `updateToken` rejects when the refresh fails, and `onAuthRefreshError` fires. `clearToken()` resets the local state when the app decides the session is gone.
- Shutdown: `logout()` redirects to the server's logout endpoint and back to `redirectUri`.

## Interop
- [`keycloak-angular.md`](keycloak-angular.md): Angular providers, a bearer-token interceptor, guards and an event signal built on this adapter.
- [`../container/keycloak.md`](../container/keycloak.md): the server, realm, public client, client scopes and audience.
- [`../nuget/Microsoft.AspNetCore.Authentication.JwtBearer.md`](../nuget/Microsoft.AspNetCore.Authentication.JwtBearer.md): a .NET API that validates the tokens this adapter sends.
- [`microsoft-signalr.md`](microsoft-signalr.md): a real-time hub client that takes its token from this adapter through `accessTokenFactory`.

## Major lines
The package follows Keycloak's release numbering: the 26 server distribution ships a `keycloak-js` archive of the same line. The `keycloak-angular` README relays a recommendation to match the adapter to the server version. The server's upgrading guide says to install the latest adapter from npm, and upstream decoupled the library from the server in the 26 line so it can move on its own.

### 26 line
The library was decoupled from the server:
- The server no longer serves `keycloak.js` under `/js/`. Install the npm package, or host a copy yourself.
- The UMD build is gone. The library is an ES module only, so a page without a bundler must load it with `<script type="module">` or an import map. TypeScript may need `"moduleResolution": "Bundler"`.
- The constructor needs its configuration. The old automatic load of `keycloak.json` from the server is gone.
- `login()`, `createLoginUrl()` and `createRegisterUrl()` always return a promise, and callers must await them.
- A secure context is required.

### 24 line
The package declares an `exports` map. Import `keycloak-js` and `keycloak-js/authz`, not paths under `keycloak-js/dist/`.

### Before the 24 line
Older adapters rely on non-standard claims that newer servers no longer add by default. With a 25-line or later server, an adapter from before the 24 line needs the "Nonce backwards compatible" protocol mapper on its client, and an early 24-line adapter needs the "Session State" mapper.

## Upstream docs
- Official docs (JavaScript adapter): https://www.keycloak.org/securing-apps/javascript-adapter
- Upgrading guide (adapter changes per server line): https://www.keycloak.org/docs/latest/upgrading/index.html
- Repo: https://github.com/keycloak/keycloak-js
- npm: https://www.npmjs.com/package/keycloak-js
