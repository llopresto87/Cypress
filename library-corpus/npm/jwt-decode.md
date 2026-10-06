# jwt-decode — npm

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions — for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
`jwt-decode` is a small helper, published by Auth0, that decodes the payload
or the header of a JSON Web Token in the browser or in Node.js. It splits the
token, base64url-decodes one part and parses it as JSON. It does not validate
anything: not the signature, not the issuer, not the expiry. Upstream says so
at the top of its README and sends validation to server-side code.

Upstream home: https://github.com/auth0/jwt-decode (README, changelog and
source). MIT licensed.

## Install, setup and configuration
- `npm install jwt-decode`. The package bundles its own TypeScript types, so
  no `@types` package is needed.
- There is nothing to configure. The only option is per call:
  `{ header: true }` decodes the header instead of the payload.
- The library relies on the global `atob()`. Modern browsers and supported
  Node.js lines provide it. A runtime without it needs a polyfill installed
  before the first decode: `import "core-js/stable/atob"`, or the `base-64`
  package assigned to `global.atob`. Upstream names React Native before 0.74
  as such a runtime.
- The 4 line supports Node.js 18 and later and targets ES2017.

## Core API / usage shape
```ts
import { jwtDecode, JwtPayload, InvalidTokenError } from 'jwt-decode';

interface AppClaims extends JwtPayload { roles?: string[]; name?: string; }

try {
  const claims = jwtDecode<AppClaims>(token);           // payload
  const header = jwtDecode(token, { header: true });      // { typ, alg, kid }
} catch (e) {
  if (e instanceof InvalidTokenError) { /* treat as signed out */ }
}
```

- `jwtDecode(token)` returns the payload, typed `JwtPayload` by default
  (`iss`, `sub`, `aud`, `exp`, `nbf`, `iat`, `jti`, all optional).
- `jwtDecode(token, { header: true })` returns the header, typed `JwtHeader`
  (`typ`, `alg`, `kid`).
- A type argument (`jwtDecode<T>`) names the expected shape. Extend
  `JwtPayload` or `JwtHeader` for non-standard claims. The type argument is a
  compile-time assertion, not a check of the decoded data.
- It throws `InvalidTokenError` when the token is not a string, lacks the
  requested part, holds invalid base64, or holds invalid JSON. A falsy token
  throws too.

## Idioms & best practices
- Use the decoded claims for presentation only: a display name, which menu
  entries to show, an early redirect to the login page when the token has
  expired. The server enforces every one of those decisions again.
- JWT `exp`, `nbf` and `iat` are NumericDate values: seconds since the epoch
  (RFC 7519). Compare them with `Date.now() / 1000`, never with the raw
  millisecond `Date.now()`.
- Wrap every decode in `try`/`catch`. A malformed or missing token is an
  ordinary input (an empty storage slot, a truncated header), not a crash.
- Type custom claims through an interface that extends `JwtPayload`, and keep
  that interface beside the code that reads the claims.
- When the app already uses a full identity-provider adapter, read the parsed
  token from the adapter instead of adding this package. Observed in
  practice: apps on [keycloak-js](keycloak-js.md) use its parsed token and
  carry no separate decoder, while apps whose backend issues its own JWTs
  carry `jwt-decode`.

## General pitfalls
- Decoding is not verification. A tampered or forged token decodes just as
  well as a genuine one, so an expiry check or a role gate built on decoded
  claims is a user-experience feature. Observed in practice: client guards and
  permission checks built on decoded claims, with the real check on the
  server; the pattern is sound only while that server check exists.
- Comparing `exp` with the millisecond clock makes every token look expired,
  because the seconds value is about a thousand times smaller.
- The import form depends on the major line (see Major lines). An import
  line copied from an example written for another major fails to build.
- A claim present in the decoded object says nothing about whether the
  token is still accepted. A revoked or rotated token decodes exactly as
  before.

## Testing
Upstream gives no testing guidance for consumers. Because the library decodes
any well-formed token without checking a signature, a unit test can build its
fixture token from base64url-encoded JSON parts with any third segment, and
no signing key is needed. Test the malformed-token path too, since
`InvalidTokenError` is part of the contract.

## Security defaults
- There is no validation to switch on: the library never checks the
  signature, `alg`, `iss`, `aud`, `exp` or `nbf`. Upstream's guidance is to
  validate on the server with a JWT library for that platform.
- Treat the decoded object as untrusted input that the user can edit. Never
  gate access to data or actions on it; only the server can.
- Upstream notes the header decode is useful for reading `kid` when a
  separate library verifies the token. Reading it here proves nothing.

## Operational behaviour
A pure, synchronous function with no network access, no state and no
caching (one source file). Decoding again on each use costs nothing that
matters. Failures surface only as a thrown `InvalidTokenError`.

## Interop
- Identity adapters: [keycloak-js](keycloak-js.md) exposes the parsed token
  itself, which makes this package redundant beside it.
- HTTP and realtime clients: the raw token (not the decoded object) is what
  an HTTP interceptor or a STOMP `connectHeaders` entry sends
  ([stomp-sockjs](stomp-sockjs.md)).
- Server side: validation belongs to the server's JWT library (upstream names
  express-jwt, koa-jwt and the ASP.NET Core JWT bearer handler as examples).

## Major lines

### 2 line
Imported as a namespace: `import * as jwt_decode from 'jwt-decode'`.

### 3 line
A default export: `import jwt_decode from 'jwt-decode'` and, from CommonJS,
`const jwt_decode = require('jwt-decode')`. The 3 line added an ES module
build and, later in the line, TypeScript definitions and a generic return
type. It still bundled an `atob` polyfill.

### 4 line
A named export: `import { jwtDecode } from 'jwt-decode'` and
`const { jwtDecode } = require('jwt-decode')`. The package ships both an ES
module and a CommonJS build behind the `exports` field. Upstream warns that
the `exports` field is the change most likely to break a build. The `atob` polyfill is gone, the build
targets ES2017, Node.js 14 and 16 are dropped, and the return type follows
the `header` option. Observed in practice, and contradicted by upstream: a
belief that the 4 line is ES-module-only; the published package carries a
CommonJS build as well.

## Upstream docs
- https://github.com/auth0/jwt-decode: README (usage, errors, polyfilling
  `atob`)
- https://github.com/auth0/jwt-decode/blob/main/CHANGELOG.md: the 4 line's
  migration note
- https://www.npmjs.com/package/jwt-decode
- https://www.rfc-editor.org/rfc/rfc7519: JWT and the NumericDate claims
