# keycloak-js — npm

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
Client-side OIDC/token adapter for Keycloak. The `Keycloak` default export reads and refreshes tokens, logs out, and loads the user profile. Commonly consumed indirectly via a framework wrapper (e.g. `keycloak-angular`) for route guards, bearer-token interception, and role-based UI gating.

## Core API / usage shape
- Access tokens are short-lived: call `updateToken(minValidity)` and await it before using `keycloak.token` for an authenticated call; handle rejection (typically by forcing logout).
- Register event/callback listeners (e.g. `onTokenExpired`, `onAuthRefreshError`) before calling `init()`.

## Idioms & best practices
- Keep tokens in-memory only; never persist them, to prevent hijacking attacks (upstream security guidance).
- Always `await updateToken(...)` before an authenticated call and handle the rejection path.

## General pitfalls
- **Short-lived tokens:** calling APIs without first `updateToken`-ing risks requests with expired tokens.
- **Listener registration order:** listeners registered after `init()` miss early events; register them first.
- **`checkLoginIframe` can be disabled by the browser:** modern browsers' third-party-cookie / tracking protection can disable the session-status iframe, degrading cross-tab login/logout detection to redirect-based `check-sso`.

## Upstream docs
- Official docs (JavaScript adapter): https://www.keycloak.org/securing-apps/javascript-adapter
- Repo: https://github.com/keycloak/keycloak-js
- npm: https://www.npmjs.com/package/keycloak-js
