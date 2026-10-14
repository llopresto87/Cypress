# msal4j — maven

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions: for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
The Microsoft Authentication Library for Java (MSAL4J): Microsoft's client
library for acquiring OAuth 2.0 and OpenID Connect tokens from the Microsoft
identity platform (Microsoft Entra ID, plus Azure AD B2C, AD FS and generic OIDC
authorities). It wraps the token endpoint, the token cache, credential handling
and authority discovery, so an application asks for a token by scope and never
builds the protocol requests itself. Upstream recommends using an MSAL rather
than programming against the protocol directly.

- `com.microsoft.azure:msal4j`: the library itself, package
  `com.microsoft.aad.msal4j`. Needed by any Java application that acquires
  Entra tokens: a daemon or service calling an API with its own identity (client
  credentials), a web API calling a downstream API for its caller (on-behalf-of),
  or a public client signing a user in.

The repository also hosts `msal4j-persistence-extension` (a persistent token
cache for desktop public clients); this page does not cover it. The coordinate
keeps the old `com.microsoft.azure` group even though the Java package is
`com.microsoft.aad.msal4j`. Upstream homes: the reference on Microsoft Learn
(https://learn.microsoft.com/en-us/entra/msal/java/) and the source repository
https://github.com/AzureAD/microsoft-authentication-library-for-java, whose wiki
carries the scenario pages.

Two application classes split the surface:
- A confidential client, `ConfidentialClientApplication`, holds a credential
  (secret, certificate or assertion). Web apps, web APIs and daemons.
- A public client, `PublicClientApplication`, holds none. Desktop and command-line apps signing a
  user in (interactive, device code, integrated Windows authentication).

## Install, setup and configuration
- **Runtime:** the README states Java 8 or higher. Logging goes through SLF4J,
  so the deployment chooses the backend (Logback, Log4j, java.util.logging).
- **Construction:** `ConfidentialClientApplication.builder(clientId, credential)`
  then `.build()`. The settings that matter, with their documented defaults:
  - `authority(url)`: the token authority. The default is the library's
    `DEFAULT_AUTHORITY` constant, `https://login.microsoftonline.com/common/`,
    a multi-tenant authority; the client
    credentials protocol needs a specific tenant, so set
    `https://login.microsoftonline.com/{tenant}/` explicitly. `b2cAuthority`
    and `oidcAuthority` (MSAL appends `.well-known/openid-configuration`) cover
    the other authority kinds.
  - `validateAuthority`: default true; checks an Entra authority against the
    list of known authorities.
  - `instanceDiscovery`: default true; MSAL contacts the central
    `https://login.microsoftonline.com` endpoint for authority metadata. False
    disables that unconditionally.
  - `sendX5c` (confidential client): default true; sends the certificate's
    public key (`x5c`) to the token service with a certificate credential.
  - `logPii`: default false; MSAL logs no personal or organizational
    identifiable information unless this is turned on.
  - `proxy`, `sslSocketFactory`: for the built-in HTTP client, which uses
    `javax.net.ssl.HttpsURLConnection`; with no proxy set, the JVM's system
    proxy properties apply (a custom `httpClient` changes this: General
    pitfalls).
  - `connectTimeoutForDefaultHttpClient`, `readTimeoutForDefaultHttpClient`
    (milliseconds): for the built-in client only.
  - `httpClient(IHttpClient)`: replaces the built-in client for every request
    MSAL makes.
  - `executorService`: the executor that runs the asynchronous requests; the
    caller owns its lifecycle.
  - `setTokenCacheAccessAspect(...)`: plugs in cache persistence (Core API).
  - `azureRegion`, `autoDetectRegion` (default false): send token requests to
    a regional endpoint instead of the global one.
- **Credentials** come from `ClientCredentialFactory`:
  `createFromSecret(String)`, `createFromCertificate(PrivateKey,
  X509Certificate)`, `create(InputStream pkcs12, String password)`, and client
  assertions (a signed JWT supplied by the caller).
- **App registration side:** a secret is generated in the registration; a
  certificate credential needs its public key uploaded to the registration
  (the `keyCredentials` property is multi-valued, so several certificates can be
  registered at once for rotation). Application permissions must be granted by
  an administrator before a client-credentials token carries them.

## Core API / usage shape
- **Client credentials (app-only):**
  `app.acquireToken(ClientCredentialParameters.builder(scopes).build())`
  returns `CompletableFuture<IAuthenticationResult>`. The scope is the resource
  identifier suffixed with `/.default`, for example
  `https://graph.microsoft.com/.default`: it asks for every application
  permission already granted for that resource. All scopes in one request must
  belong to one resource; mixing resources is an error. No refresh token is
  ever issued in this flow; the next call simply acquires again.
- **Cache first:** `acquireToken(ClientCredentialParameters)` and
  `acquireToken(OnBehalfOfParameters)` look in the token cache first and go to
  the token service only when nothing valid is cached (the client-credentials
  default since 1.10.0). `ClientCredentialParameters.skipCache` defaults to
  false; set it only to force a network call.
- `ClientCredentialParameters` also takes `tenant(...)` (overrides the
  authority's tenant for one request), `clientCredential(...)` (overrides the
  credential for one request), `claims(...)` (a claims request, as used to
  answer a claims challenge), `extraHttpHeaders` and `extraQueryParameters`.
- **Silent acquisition** for user flows: `acquireTokenSilently(SilentParameters)`
  returns a cached token or redeems the cached refresh token;
  `SilentParameters.forceRefresh` skips a still-valid access token. The
  `SilentParameters.builder(scopes)` overload without an account is deprecated:
  it served the client-credentials and on-behalf-of flows, which now use the
  cache by default, and upstream says it will be removed in the next major
  version.
- **Result:** `IAuthenticationResult`, the token and its metadata, delivered
  through the returned `CompletableFuture`.
- **Token cache:** an in-memory cache is provided by default and lasts for the
  life of the application object. Persisting it means implementing
  `ITokenCacheAccessAspect` (`beforeCacheAccess` deserializes into
  `ITokenCache`, `afterCacheAccess` serializes out) and registering it on the
  builder. Upstream marks its own sample as not production-ready and says to
  attend to the cache's security and access requirements.
- **Exceptions:** all extend `MsalException`. `MsalServiceException` is an
  error response from the token service or a network error (`headers()` exposes
  the response headers); `MsalClientException` is local to the library or
  device; `MsalInteractionRequiredException` (user flows) means the user must
  sign in interactively, with a `reason` saying why. Distinguish them by type
  and `errorCode()`.

## Idioms & best practices
- **One application object per credential, kept for the life of the process.**
  The cache belongs to the `ConfidentialClientApplication` instance, so a new
  instance per request starts with an empty cache and sends every request to
  the token service. The class is documented as conditionally thread-safe.
- **Let the cache work.** Call `acquireToken` before each use and leave
  `skipCache` false; there is no need to call `acquireTokenSilently` first in
  the client-credentials or on-behalf-of flows.
- **Choosing the credential.** Upstream: "For a higher level of assurance, the
  Microsoft identity platform also allows the calling service to authenticate
  using a certificate or federated credential instead of a shared secret." A
  secret is simpler to provision but is a shared password that must be
  distributed and rotated; a certificate keeps the private key with the
  service and only the public key in the registration; a federated credential
  (workload identity federation, passed as a client assertion) removes the
  stored credential altogether where the hosting platform issues its own
  tokens. Whichever is chosen, it comes from external configuration or a
  secret store, never the repository.
- **Identify a user by `oid` and `tid`.** For user flows, the ID token's `oid`
  is the immutable object id of the user in that tenant (Microsoft Graph
  returns the same value as the user's `id`), and `tid` is the tenant. Upstream:
  store per-user data under `sub` or `oid`, and use `oid` with `tid` when data
  is shared across services. Never key on `preferred_username`, `email`, `upn`
  or `name`: upstream calls them mutable and says they must not drive
  authorization. `oid`, `preferred_username` and `name` need the `profile`
  scope. The same user in another tenant has a different `oid` and is a
  different account by design.
- **Request the claims you validate.** v2.0 tokens are slimmer than v1.0, and
  several claims are now optional claims that must be requested per
  application in the app registration (next section).
- Handle errors on both sides: when acquiring the token, and when the protected
  API rejects it (for example a Conditional Access claims challenge, answered by
  acquiring again with the challenge's `claims`).
- Configure SLF4J logging for MSAL so token failures are diagnosable, and leave
  `logPii` off unless the application is prepared to protect what it then logs.

## General pitfalls
- **`amr` and `auth_time` are not in a v2.0 ID token by default.** The ID token
  claims reference lists neither among the default claims. The optional-claims
  reference lists `auth_time` ("Time when the user last authenticated") in the
  optional claim set and `amr` ("Identifies how the subject of the token was
  authenticated") among the v2.0-specific optional claims, "not included in
  v2.0 tokens unless requested". A validator that requires `amr` to contain
  `mfa`, or checks `auth_time` freshness, rejects every token until the app
  registration requests those optional claims for the ID token.
- **What `amr` values mean.** For OIDC v2.0 the reference maps methods to values:
  password alone is `pwd`; MFA methods add `mfa` (Authenticator push `rsa`,
  `ngcmfa`, `mfa`; TOTP `totp`, `mfa`; SMS `sms`, `mfa`; FIDO2 and passkeys
  `fido`, `mfa`; Temporary Access Pass `otp`, `mfa`). `x509` alone is not
  phishing-resistant MFA. Whether a sign-in that satisfied MFA through an
  earlier session's claim also yields `mfa` is not stated upstream; test it
  against the tenant before relying on it.
- **`.default` with mixed resources fails.** One request, one resource.
- **A token for an API you do not own is opaque.** Upstream warns not to
  validate or parse access tokens issued for Microsoft APIs (some are not
  validatable JWTs, and some are encrypted); only the API's owner reads them.
- **App-only tokens can arrive without `roles`.** Entra issues app-only tokens
  to any client unless the resource requires assignment, so an API that accepts
  them must check the `roles` claim itself (or turn on assignment-required).
- **Group overage.** Beyond 200 groups in a JWT, the `groups` claim is replaced
  by an overage pointer to Microsoft Graph.
- **Proxy and TLS settings move with a custom `httpClient`.** The builder's
  `proxy` and `sslSocketFactory` documentation says that once `httpClient(...)`
  is set, proxy and SSL configuration belong on that client, not on the
  builder.
- **An application object per call** silently defeats the cache (Idioms) and
  multiplies load on the token service.

## Testing
- Upstream ships no test harness or fake authority. A unit test that needs a
  token can stub the `IHttpClient` the application is built with, since every
  HTTP request MSAL makes goes through it.
- A test against a local stub token endpoint points `authority` (or
  `oidcAuthority`) at the stub and turns `instanceDiscovery` off, because
  discovery otherwise calls the central Microsoft endpoint. Assert the request
  shape the stub receives: `grant_type=client_credentials`, the `.default`
  scope, and either `client_secret` or `client_assertion` with
  `client_assertion_type=urn:ietf:params:oauth:client-assertion-type:jwt-bearer`.
- Test the missing-credential path (an empty secret or unreadable key store)
  as a startup failure, not as a first-request failure.
- Claim validation (`tid`, `amr`, `auth_time`) is tested where the ID token is
  validated (the OIDC client library), with signed tokens that carry and omit
  each optional claim.

## Security defaults
- `logPii` is off, `validateAuthority` is on and `sendX5c` is on by default.
- The credential is the application's identity. Upstream: never publish it in
  source code, embed it in web pages, or ship it in a widely distributed
  native application.
- A certificate assertion is a short-lived JWT: upstream advises `exp` at most
  5-10 minutes after `nbf`, a unique `jti`, `aud` set to the tenant's v2.0
  token endpoint, and `iss` and `sub` set to the client id. MSAL builds it for a
  certificate credential.
- A persisted token cache holds live access tokens: store it with the same care
  as the credential.
- Disabling `validateAuthority` or `instanceDiscovery` widens which authorities
  the application accepts; keep them on outside tests and non-Entra
  authorities.
- Application permissions are tenant-wide; grant the least-privileged
  permission each call needs.

## Operational behaviour
- `acquireToken` is asynchronous; the future completes on the configured
  `executorService` (or the library's default). Blocking on `.get()` from a
  request thread ties that thread to the token service's latency on a cache
  miss.
- Access tokens are short-lived (`expires_in` in the response); the cache
  returns a valid token until it expires and then acquires a new one, so a
  steady caller hits the token service about once per token lifetime.
- The in-memory cache is lost on restart; the first call after start always
  goes to the network.
- For on-behalf-of with a persisted cache, upstream advises one cache per
  incoming access token (keyed by its hash) and an eviction policy, since each
  new incoming token creates a new cache entry.
- Timeouts on the built-in HTTP client are opt-in settings; set them so a
  stalled token service cannot hang the caller.

## Interop
- Microsoft Graph and any Entra-protected API: the `.default` scope of the
  resource (see the Microsoft Graph platform page,
  [`../platform/microsoft-graph.md`](../platform/microsoft-graph.md)).
- `com.azure:azure-identity`: the Azure SDK's credential layer
  (`ClientSecretCredential`, `ClientCertificateCredential`), the alternative
  when a client SDK takes a `TokenCredential` (the Microsoft Graph Java SDK
  does). `appTokenProvider` on the MSAL builder exists for that SDK's own use
  and, upstream says, "isn't useful to applications in general".
- OIDC sign-in in a web framework (Spring Security's OAuth2 client, for one:
  [`spring-security`](./spring-security.md)) uses its own token client against
  the same Entra endpoints, not MSAL4J; the ID-token claim facts above apply to
  it unchanged.

## Major lines
MSAL4J has stayed on its 1 major line; behaviour changes arrive in minor
releases, recorded in the repository's `changelog.txt`.
- 1.10.0 made cache lookup the default for the on-behalf-of and client
  credentials flows.
- 1.23.0 replaced the Nimbus OAuth/OIDC, Lombok and Jackson dependencies with
  in-library implementations. Public APIs stayed the same except that protected
  APIs returning or using Nimbus's `ClientAuthentication` were removed, and JSON
  errors now surface as `MsalClientException` or `MsalServiceException`.
- The deprecated account-less `SilentParameters.builder(scopes)` is announced
  for removal in the next major version.

## Upstream docs
- MSAL for Java on Microsoft Learn: https://learn.microsoft.com/en-us/entra/msal/java/
- Client credentials in MSAL Java: https://learn.microsoft.com/en-us/entra/msal/java/getting-started/client-credentials
- Token cache serialization: https://learn.microsoft.com/en-us/entra/msal/java/advanced/msal-java-token-cache-serialization
- API reference: https://learn.microsoft.com/en-us/java/api/com.microsoft.aad.msal4j
- Source, wiki and changelog: https://github.com/AzureAD/microsoft-authentication-library-for-java
- Client credentials flow (protocol): https://learn.microsoft.com/en-us/entra/identity-platform/v2-oauth2-client-creds-grant-flow
- Certificate credentials: https://learn.microsoft.com/en-us/entra/identity-platform/certificate-credentials
- ID token claims: https://learn.microsoft.com/en-us/entra/identity-platform/id-token-claims-reference
- Optional claims and `amr` values: https://learn.microsoft.com/en-us/entra/identity-platform/optional-claims-reference
