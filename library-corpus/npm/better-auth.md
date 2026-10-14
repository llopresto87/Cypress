# better-auth — npm

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions. For exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
Better Auth is a framework-agnostic authentication and authorization library
for TypeScript. One server instance, built with `betterAuth({...})`, owns
sign-up and sign-in (email and password, social and OAuth providers), password
hashing, cookie-based sessions and the tables that hold them, and grows through
plugins (two-factor, passkey, organization, admin, SSO, OAuth provider, and
more). It stores its data in the application's own database through an
adapter, so the user table belongs to the application. A typed client,
`createAuthClient`, calls the server's endpoints from the browser. Licence:
MIT. Docs: https://www.better-auth.com/docs ; source (a monorepo of the core,
the CLI, adapters and plugins): https://github.com/better-auth/better-auth.

- `better-auth`: the server library, the framework handler helpers
  (`better-auth/node`, `better-auth/next-js`, ...), the clients
  (`better-auth/client`, `better-auth/react`, `better-auth/vue`, ...), the
  built-in plugins, and re-exports of the database adapters.
- `auth`: the CLI (`npx auth@latest <command>`): `generate`, `migrate`,
  `check`, `secret`, `upgrade`, `info`, `init`, `create-admin`.
- `@better-auth/cli`: the CLI's former package, now marked deprecated on npm;
  the same commands run from `auth`.
- `@better-auth/drizzle-adapter`: the Drizzle ORM adapter as its own package
  (the same `drizzleAdapter` is also importable from
  `better-auth/adapters/drizzle`); needed only on Drizzle.

The packages of one release train (`better-auth` and the official
`@better-auth/*` packages) are upgraded together.

## Install, setup and configuration
- `npm install better-auth` in the server, and in the client too when client
  and server are separate projects. The packages are ES modules; upstream says
  CommonJS is not supported for the Node.js handler.
- **`BETTER_AUTH_SECRET`** (or `AUTH_SECRET`, or the `secret` option) signs
  cookies and keys encryption and hashing. Upstream asks for at least 32
  characters of high entropy (`openssl rand -base64 32` or `npx auth secret`).
  Unset, it falls back to a fixed, public default string; in production an
  unset secret throws. Versioned secrets (`secrets: [{ version, value }]` or
  `BETTER_AUTH_SECRETS=2:new,1:old`) rotate it without invalidating data: the
  first entry encrypts, the rest only decrypt, and data is re-encrypted lazily.
- **`BETTER_AUTH_URL`** (or the `baseURL` option) is the public base URL of the
  auth server. Unset, it is inferred from the incoming request, which upstream
  advises against; set it explicitly. The object form
  (`{ allowedHosts, protocol, fallback }`) resolves one base URL per request
  across several allowed hosts, which are also trusted origins.
- **`basePath`** is where the routes are mounted, `/api/auth` by default; a
  path inside `baseURL` overrides it.
- **`database`** takes a driver instance (a `pg` `Pool`, a `mysql2` pool, a
  SQLite database), which the built-in Kysely adapter wraps, or an ORM adapter
  (`drizzleAdapter(db, { provider: "pg" | "mysql" | "sqlite" })`, Prisma,
  MongoDB). Without a database, sessions can run stateless in cookies; most
  plugins need a database.
- **`emailAndPassword`**: `enabled` (off by default), `minPasswordLength` 8,
  `maxPasswordLength` 128, `autoSignIn` true, `requireEmailVerification` false,
  `disableSignUp` false, `revokeSessionsOnPasswordReset` false,
  `resetPasswordTokenExpiresIn` 3600 s, `sendResetPassword` (required for the
  reset flow), and `password: { hash, verify }` to replace the hasher.
- **Schema.** The CLI produces the tables the configuration needs:
  `generate` writes an ORM schema (Drizzle, Prisma) or an SQL file (Kysely);
  `migrate` applies the schema directly and works only with the built-in
  Kysely adapter. With Drizzle or Prisma, the generated schema goes through
  that ORM's own migration tool (for Drizzle, `drizzle-kit generate` then
  `drizzle-kit migrate`). `getMigrations` from `better-auth/db/migration` runs
  Kysely migrations from code where no CLI can run. The CLI finds the config in
  an `auth.ts` under the project root, `lib/` or `utils/` (also under `src/`),
  or takes `--config`.

## Core API / usage shape
- **Server instance.** `export const auth = betterAuth({ database, emailAndPassword, socialProviders, session, plugins, ... })`,
  exported as `auth` or as the default export so the CLI can load it.
- **Mounting.** `auth.handler(request)` takes a standard `Request` and returns
  a `Response`; mount it on a catch-all route for `GET` and `POST` under the
  base path. Helpers adapt it: `toNodeHandler(auth)` for Node.js servers
  (Express, Fastify), `toNextJsHandler(auth)`, `svelteKitHandler`,
  `toSolidStartHandler`, and others.
- **Server-side calls.** `auth.api.<endpoint>({ body, headers, query })` calls
  any endpoint, core or plugin, as a function. `auth.api.getSession({ headers })`
  reads the session from the request's cookie and returns it or `null`.
  Failures throw `APIError` (`isAPIError(err)` from `better-auth/api`).
  `returnHeaders: true` returns the response headers (to forward
  `Set-Cookie`), and `asResponse: true` returns a `Response`.
- **Client.** `createAuthClient({ baseURL })` from the framework's entry
  (`better-auth/react`, `/vue`, `/svelte`, `/solid`, or `better-auth/client`
  for plain or server-side code); `baseURL` may be omitted on the same origin.
  Calls return `{ data, error }` instead of throwing (`signUp.email`,
  `signIn.email`, `signIn.social`, `signOut`, `getSession`,
  `requestPasswordReset`, `revokeSession`, `revokeOtherSessions`).
  `useSession()` is a reactive hook built on nanostores.
- **Core schema** (table names `user`, `session`, `account`, `verification`):
  - `user`: `id`, `name`, `email` (unique), `emailVerified`, `image`
    (optional), `createdAt`, `updatedAt`.
  - `session`: `id`, `userId` (foreign key), `token` (unique), `expiresAt`,
    `ipAddress` and `userAgent` (optional), `createdAt`, `updatedAt`.
  - `account`: `id`, `userId`, `accountId`, `providerId`, then optional
    `accessToken`, `refreshToken`, `accessTokenExpiresAt`,
    `refreshTokenExpiresAt`, `scope`, `idToken`, `password`; `createdAt`,
    `updatedAt`.
  - `verification`: `id`, `identifier`, `value`, `expiresAt`, `createdAt`,
    `updatedAt`.
  Table and column names map through `modelName` and `fields`;
  `user.additionalFields` and `session.additionalFields` extend the schema
  with typed fields (`input: false` keeps a field server-owned).
- **Where the password lives.** An email-and-password credential is an
  `account` row with `providerId` `"credential"`, `accountId` the user's `id`,
  and the hash in `account.password`; the `user` row holds no credential.
- **IDs** are generated by Better Auth unless
  `advanced.database.generateId` says otherwise: `false` (the database
  generates), `"serial"`, `"uuid"`, or a function per model.

## Idioms & best practices
- **One server instance, one config file**, imported by the handler, by
  server-side session reads, and by the CLI. Anything the CLI must load stays
  importable outside the bundler.
- **Regenerate the schema whenever plugins or schema options change.** A plugin
  adds tables or columns; the generated schema and the database only follow
  when `generate` (and the ORM's migration) or `migrate` runs again. Treat the
  CLI output as the canonical shape and change names through `modelName` and
  `fields`, not by hand-editing columns. `npx auth check schema` verifies the
  configured schema (for Drizzle and Prisma it reads the schema object or
  client model, so it cannot see a migration that was never applied).
- **Choose the password hasher before the first user.** The default is
  `scrypt` (upstream: memory-hard, natively supported by Node.js, OWASP's
  choice where argon2id is unavailable). A policy that requires another scheme
  (argon2id, say) sets `emailAndPassword.password: { hash, verify }`; a plain
  `enabled: true` stores scrypt hashes. `verify` receives every stored hash, so
  a switch after users exist needs a `verify` that still accepts the old format.
- **Read sessions on the server with `auth.api.getSession({ headers })`.** The
  client's `getSession` cannot see cookies from a server component or route.
- **Forward cookies when signing in from server code.** A server-side
  `auth.api` call sets no cookie by itself: return its `Response`
  (`asResponse`) or copy its `Set-Cookie` headers; for Next.js server actions
  upstream ships a cookie plugin.
- **Set `baseURL`, `trustedOrigins` and the IP header explicitly** in every
  deployed environment, and validate the secret and URL at startup with the
  rest of the configuration ([`zod`](zod.md)).
- **Use database transactions** for flows that change several records: the
  Drizzle and Prisma adapters use them only with `transaction: true`, and
  password reset with session revocation is all-or-nothing only then.

## General pitfalls
- **The secret has a public default.** Outside production an unset
  `BETTER_AUTH_SECRET` falls back to a well-known string, so a staging or
  preview environment that does not count as production signs cookies with it.
- **`migrate` does nothing for Drizzle or Prisma.** It is Kysely-only; with an
  ORM adapter the tables exist only after the ORM's own migration runs.
- **Schema drift surfaces at runtime.** Better Auth compares the schema with
  what it writes when it initializes and fails requests on a mismatch.
  Upstream's database page says the check is on by default, production
  included; its options reference lists the default as on outside production.
  `advanced.database.validateSchema: false` turns it off.
- **Express body parsing before the handler breaks it.** Mount `toNodeHandler`
  first and `express.json()` after; on Express 5 the catch-all is
  `/api/auth/{*any}`.
- **Duplicate copies of `better-auth` or `@better-auth/core` in the tree**
  produce errors such as "No request state found"; upstream calls it a dual
  module hazard, seen mostly after upgrades. `npm ls better-auth @better-auth/core`
  finds the copies.
- **Cookie cache delays revocation.** With `session.cookieCache` on, a revoked
  session can stay valid on other devices until the cache's `maxAge` passes;
  use a short `maxAge`, or `disableCookieCache: true` on sensitive reads.
- **Default sign-up reveals registered emails.** With `autoSignIn` on and no
  email verification, signing up with an existing email returns an error (422);
  the same-response protection applies only with `requireEmailVerification`
  or `autoSignIn: false`.
- **`name`, `email` and `image` cannot be removed** from the user table.
- **TypeScript inference needs `strict`** (or at least `strictNullChecks`).

## Testing
- The `testUtils()` plugin (`better-auth/plugins`) adds factories
  (`createUser`), database helpers (`saveUser`, `deleteUser`), `login({ userId })`
  returning headers and a session, and OTP capture (`captureOTP: true`) on
  `(await auth.$context).test`. It registers no routes but its helpers are
  privileged: keep it in a test-only auth instance, not in the production
  config. A conditional plugin array weakens type inference.
- Point the test instance at the same database engine as production, migrated
  by the same generated schema, so the schema check and the queries are the
  ones deployed.
- Rate limiting is off outside production by default; a test of it sets
  `rateLimit.enabled: true`.

## Security defaults
- **Cookies**: `session_token` (an opaque, signed identifier), `session_data`
  only when the cookie cache is on, `dont_remember` when "remember me" is off;
  prefix `better-auth`. They are `httpOnly`, `SameSite=Lax`, and `Secure` in
  production (the options reference ties `Secure` to `NODE_ENV=production` or
  an `https` protocol; `advanced.useSecureCookies: true` forces it).
  `crossSubDomainCookies` widens the cookie to a parent domain: every
  subdomain under it then receives the session.
- **CSRF**: state-changing routes prefer non-simple requests (JSON), every
  request's `Origin` is checked against the trusted origins (the base URL plus
  `trustedOrigins`, wildcards allowed), and first-login sign-in and sign-up
  use Fetch Metadata to block cross-site navigations.
  `advanced.disableCSRFCheck` removes all of it; `advanced.disableOriginCheck`
  also allows any redirect or callback URL (an open redirect) and, for
  backward compatibility, disables CSRF protection too. Keep `localhost` out
  of a production `trustedOrigins`.
- **Sessions** expire after 7 days (`expiresIn`); each use after `updateAge`
  (1 day) extends them. `freshAge` (1 day) gates sensitive endpoints on how
  recently the session was created. Sessions can be revoked singly, all but
  the current, or all; a password reset does not revoke other sessions unless
  `revokeSessionsOnPasswordReset` is set.
- **Rate limiting** is on in production and off in development by default:
  100 requests per 10 s per client, with stricter built-in rules (sign-in by
  email: 3 per 10 s). The store is in memory by default, so it is per process
  and lost on restart; `storage: "database"` or `"secondary-storage"` shares
  it. Client-initiated requests are limited, server-side `auth.api` calls are
  not.
- **Client IP** comes from `X-Forwarded-For`, whose leftmost entry a client
  controls. Behind a proxy, name a single trusted header
  (`advanced.ipAddress.ipAddressHeaders`) or list `trustedProxies`, and keep
  the origin reachable only through them; otherwise rate limits can be evaded
  by spoofing. `advanced.trustedProxyHeaders` lets forwarded host and protocol
  headers build the base URL: enable it only when end users cannot set them.
- **Passwords**: scrypt, length 8 to 128 by default; duplicate sign-ups
  simulate hashing time.

## Operational behaviour
- **Startup** validates the schema against the database (Kysely reads live
  metadata, so it needs database access while initializing) and logs
  mismatches with their fixes.
- **Per request**, a session read hits the database (or secondary storage)
  unless the cookie cache answers; `GET /get-session` also writes when it
  extends a session, which `deferSessionRefresh` moves off read-replica GETs.
- **Password hashing** runs on Node's `node:crypto` scrypt on the libuv thread
  pool from 1.6, with a pure-JavaScript fallback on runtimes without it.
- **Secondary storage** (a key-value store such as Redis) can hold sessions,
  verification records and rate-limit counters.
- **Multiple instances** need the same secret, a shared rate-limit store and
  the same base URL resolution, and are upgraded together.

## Interop
- Drizzle ORM: `drizzleAdapter(db, { provider, schema })`; the adapter expects
  Drizzle table names to match the auth models (map them with `schema` or
  `modelName`), and joins (`advanced.database.joins`, from 1.4) need the
  relations defined. See [`drizzle-orm`](drizzle-orm.md).
- PostgreSQL directly: pass a `pg` `Pool` as `database`, and set
  `database.schemaName` for a non-default schema. See [`pg`](pg.md) and
  [`container/postgres.md`](../container/postgres.md).
- Configuration validation: [`zod`](zod.md).
- Redis as secondary storage: [`container/redis.md`](../container/redis.md).

## Major lines
The package is on its 1 line, and upstream ships breaking changes in minor
releases, each with an "Important changes" list; read it before a minor
upgrade. `npx auth upgrade` moves every package of the release train
together.

- **1.4**: `authClient.forgotPassword` became `requestPasswordReset`;
  `advanced.generateId` was removed for `advanced.database.generateId`
  (`useNumberId` became `generateId: "serial"`); the passkey plugin moved to
  `@better-auth/passkey`; plugin callbacks receive `ctx` instead of `request`.
- **1.5**: the CLI moved to the `auth` package (`npx auth`), replacing
  `@better-auth/cli`; adapters were extracted into `@better-auth/*-adapter`
  packages (still re-exported from `better-auth`); the API key plugin moved to
  `@better-auth/api-key`; `better-auth/adapters/test` was removed; secret
  rotation and the `testUtils` plugin arrived.
- **1.6**: `freshAge` counts from session creation, not the last update; the
  cookie cache's `maxAge` follows the session's `expiresIn`; scrypt runs on
  `node:crypto` (existing hashes stay valid); the `oidcProvider` plugin was
  deprecated for `@better-auth/oauth-provider`.
- **1.7**: `oidcProvider` was removed; external accounts use a normalized
  provider identity (provider plus confirmed subject), and existing account
  identities need a reviewed migration; MCP moved to `@better-auth/mcp`.
  Upstream warns that the generated migration is not the whole upgrade.

## Upstream docs
- https://www.better-auth.com/docs (installation, basic usage; concepts: API,
  client, CLI, cookies, database, rate limit, session management;
  authentication: email and password; adapters: Drizzle, PostgreSQL;
  reference: options, security, FAQ; plugins: test utils)
- Release notes: https://www.better-auth.com/blog (1.4, 1.5, 1.6, 1.7)
- https://github.com/better-auth/better-auth (docs sources under
  `docs/content`)
- https://www.npmjs.com/package/better-auth ; https://www.npmjs.com/package/auth
