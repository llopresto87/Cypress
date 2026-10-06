# jjwt — maven

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions: for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
JJWT is a pure-Java library that creates and verifies JSON Web Tokens and JSON
Web Keys on the JVM and Android, implementing the JOSE RFCs (JWT 7519, JWS
7515, JWE 7516, JWK 7517, JWA 7518). Apache 2.0. Since the 0.10 line it is a
module set: `io.jsonwebtoken:jjwt-api` (compile scope),
`io.jsonwebtoken:jjwt-impl` (runtime scope) and a JSON module,
`io.jsonwebtoken:jjwt-jackson` or `io.jsonwebtoken:jjwt-gson` (runtime scope).
The 0.9 line shipped one jar, `io.jsonwebtoken:jjwt`, with API and
implementation together; from the 0.12 line `jjwt` is back only as an empty
aggregator that pulls in the three modules, and upstream still recommends
declaring the modules. The Spring Boot BOM manages no `io.jsonwebtoken`
artifact, so the project pins the version; a JJWT BOM exists from the late
0.12 line. Upstream home: https://github.com/jwtk/jjwt (the
README is the reference manual), Javadoc at
https://javadoc.io/doc/io.jsonwebtoken/jjwt-api.

JJWT is pre-1.0, and each 0.x minor line has carried breaking changes, so this
page treats each as a major line.

## Install, setup and configuration
- Declare `jjwt-impl` and the JSON module with `runtime` scope. JJWT promises
  semantic versioning for every artifact except `jjwt-impl`, whose internals can
  change at any time, so it must never be a `compile` dependency.
- BouncyCastle (`org.bouncycastle:bcprov-jdk18on`, runtime) is needed only for
  some algorithms on old JDKs (PS* on JDK 10 or earlier, EdDSA on JDK 14 or
  earlier).
- **Parser builder (0.12 line), with defaults:**
  - `verifyWith(SecretKey|PublicKey)` sets one constant verification key;
    `keyLocator(Locator<Key>)` looks the key up per token.
  - `clockSkewSeconds(long)` tolerates clock skew on `exp` and `nbf` (none
    unless set; upstream calls two or three minutes enough); `clock(Clock)`
    replaces the default clock.
  - `require*` / `require(name, value)` assert claims.
  - `sig()`, `enc()`, `key()` and `zip()` are nested algorithm collections; all
    JWA-standard algorithms are accepted by default, and entries can be
    removed.
  - `unsecured()` enables `alg: none` tokens (off by default); `critical()`
    lists accepted `crit` header names (unknown ones are rejected).
- `build()` returns an immutable, thread-safe `JwtParser`: build it once and
  reuse it.

## Core API / usage shape
- **Issue (0.12 line):**
  `Jwts.builder().subject(..).issuer(..).expiration(..).claim(name, value).signWith(key).compact()`.
  `signWith(key)` picks the strongest algorithm the key allows and sets `alg`
  (a 32-byte `SecretKey` gives HS256; a 2048-bit RSA key RS256, 3072 RS384,
  4096 RS512); `signWith(key, Jwts.SIG.RS512)` overrides within what the key
  permits. Signing with a `PublicKey` throws `InvalidKeyException`.
- **Verify (0.12 line):**
  `Jwts.parser().verifyWith(key).build().parseSignedClaims(jws).getPayload()`.
  A bad signature throws `SignatureException`; every failure extends
  `JwtException`; calling the wrong type-safe `parse*` method for the token
  kind throws `UnsupportedJwtException`.
- **Keys:** generate with `Jwts.SIG.HS256.key().build()` or the RSA/EC key-pair
  builders; turn a stored secret into a key with
  `Keys.hmacShaKeyFor(Decoders.BASE64.decode(secret))`; a password-like string
  becomes `Keys.password(chars)` and belongs in key derivation. The README warns
  that any form of `secretString.getBytes()` in a cryptographic context is
  almost always wrong.
- **Key types:** an HMAC algorithm verifies with a `SecretKey`; an asymmetric
  one with the `PublicKey`, never the `PrivateKey`. A `Locator` must return the
  type that matches the token's algorithm. With symmetric algorithms one secret
  signs and verifies; with asymmetric ones only the issuer holds the private
  key.
- **Claim assertions:** `requireSubject`, `requireIssuer`, `requireAudience`
  and `require(name, value)` throw `MissingClaimException` or
  `IncorrectClaimException`. JJWT checks `iss` and `aud` only when asked.
- `claim(name, value)` with a null or empty value removes the claim, as do the
  standard setters (`issuer(null)`) and `claims(Map)`: a claim is present with
  a value or absent.

## Idioms & best practices
- Pin the algorithm family through the key given to the parser: with
  `verifyWith(publicKey)` a token whose header says HS256 cannot verify,
  because HMAC needs a `SecretKey`. That is the library's structural defence
  against key and algorithm confusion (the key-type rule is upstream; that the
  parser then rejects HS256 was read from the source in practice).
- Narrow accepted algorithms further by removing entries from the `sig()`
  collection; from the late 0.12 line an empty `sig()` rejects every JWS.
- Use the `require*` methods for `iss` and `aud` instead of extracting and
  comparing claims by hand (observed in practice: the hand comparison is where
  bugs hide).
- Distribute verification keys by `kid` through a `keyLocator` (or the JWK set
  support of the 0.12 line) instead of copying one public key into every
  service. Observed in practice: with a copied key, rotation is a coordinated
  redeploy of every validator. A locator must key on `kid` and the algorithm
  family, or the key-type defence weakens to whatever it returns.
- Wrap issue and verify in one internal service so key handling and claim
  conventions live in one place (seed advice; upstream is silent).

## General pitfalls
- **Runtime-scope gaps.** A missing `jjwt-impl` or JSON module compiles and
  boots; the failure appears when JJWT first builds a builder or parser.
  Observed in practice: the service passes health checks and fails on the first
  token.
- **Weak keys throw from the 0.10 line** (`WeakKeyException`): HS256 needs at
  least 32 bytes, HS384 48, HS512 64; RSA needs at least 2048 bits. The 0.9
  line had no strength check, so a secret that worked there can fail after an
  upgrade.
- **JAXB on the 0.9 line.** Its `Base64Codec` calls
  `javax.xml.bind.DatatypeConverter`, which left the JDK with JAXB at Java 11,
  so signing or parsing with a Base64 secret throws `NoClassDefFoundError`
  unless a JAXB API jar is present. The 0.10 line has its own Base64.
- **Expiry is enforced while parsing:** a past `exp` throws
  `ExpiredJwtException` (within any skew allowance). A hand-written expiry check
  after a successful parse is redundant but still runs; never let a caller
  swallow `ExpiredJwtException`.
- **No revocation.** A valid token stays valid until `exp`, and disabling a
  user does not invalidate it. OWASP describes a deny list keyed on `jti` and
  `iss` (not a token hash), and first suggests a Token Status List or short
  expiry; either costs statelessness.
- From the 0.12 line, header or claims serialization errors throw
  `io.jsonwebtoken.io.SerializationException`.
- **Every line crossing is a code migration** in every copy of the token code,
  not a coordinate bump (see Major lines).

## Testing
- Pass a fixed `Clock` through `clock(...)` for deterministic `exp` and `nbf`
  tests; the README names determinism as its purpose.
- Generate test keys with the algorithm key builders
  (`Jwts.SIG.HS256.key().build()`, `Jwts.SIG.RS256.keyPair().build()`), so the
  strength checks pass.
- Test the negative paths: a token signed by another key, an expired token, an
  `alg: none` token, an HS256 token presented to a public-key parser, and a
  missing required claim (observed in practice as the set that catches
  regressions).

## Security defaults
- **0.12 line and later:** unsecured tokens (`alg: none`, or no `alg`) are
  rejected by default, as RFC 7518 requires; only `JwtParserBuilder.unsecured()`
  accepts them (the changelog calls it `enableUnsecured()`). Never call it on an
  authentication path. A `PrivateKey` is refused for verification; `Claims`,
  `Header` and `JwtParser` are immutable; the builder always sets `alg` from the
  key.
- **0.9 line:** `parse(..)` and `parseClaimsJwt(..)` accept unsigned tokens
  (they exist for them); only `parseClaimsJws` and `parsePlaintextJws` demand a
  signature. Use `parseClaimsJws` on every authentication path. Observed in
  practice as defence in depth: also check the header's algorithm after
  parsing.
- JWK `toString()` redacts secret material from the 0.12 line, so printing a
  key does not leak it.
- Base64 is not encryption: an encoded secret in configuration is still a
  secret.

## Operational behaviour
- The built parser is thread-safe and immutable; share one per configuration.
- Key strength is checked at sign and verify time, so a short configured secret
  fails on the first token, not at startup, unless the application builds its
  key at startup.
- From the late 0.12 line `jjwt-api` finds implementation factories by
  reflection once at class load; GraalVM native images must register the
  factory class names.

## Interop
- **JSON:** `jjwt-jackson` uses Jackson (a custom `ObjectMapper` and claim-type
  map can be passed to `JacksonDeserializer`); `jjwt-gson` uses Gson.
- **Spring Security:** JJWT is not part of Spring, so an application using it
  writes its own filter; Spring Security's resource server uses a different JOSE
  library.
- Decoding a JWT in a browser without verifying it is a separate concern,
  covered by the npm token-decoding pages.

## Major lines
### 0.9
- One jar, `io.jsonwebtoken:jjwt`; `Jwts.parser()` is a mutable parser;
  `setSigningKey`, `parseClaimsJws`; no key-strength checks; JAXB Base64.

### 0.10
- Modular jars (`jjwt-api` compile; `jjwt-impl`, `jjwt-jackson` runtime); every
  internal class moves to `jjwt-impl`; the algorithm is chosen from the key;
  key-strength assertions; `Keys.hmacShaKeyFor` and `Keys.secretKeyFor`; own
  Base64.

### 0.11
- `Jwts.parserBuilder()...build()` is added and recommended (immutable,
  thread-safe), and the mutators on `JwtParser` are deprecated: for example
  `Jwts.parserBuilder().setSigningKey(key).build().parseClaimsJws(jws)`. Gson
  support. The Jackson and org.json serializer classes move package
  (`io.jsonwebtoken.io.JacksonSerializer` to
  `io.jsonwebtoken.jackson.io.JacksonSerializer`).

### 0.12
- The large break: `Jwts.parser()` returns a `JwtParserBuilder` and
  `parserBuilder()` is removed; `setSigningKey` becomes `verifyWith`,
  `parseClaimsJws` becomes `parseSignedClaims`, `parseClaimsJwt` becomes
  `parseUnsecuredClaims`, `getBody()` becomes `getPayload()`,
  `SignatureAlgorithm.X` becomes `Jwts.SIG.X`, and `setSubject` becomes
  `subject` (old setters deprecated). `Claims` and `Header` are immutable, built
  with `ClaimsBuilder`/`HeaderBuilder`; non-claims payloads are `byte[]`;
  `PrivateKey` verification is gone; unsecured JWTs are off by default; JWE and
  JWK support arrive. The maintainers suggested waiting for 1.0 to take the
  breaks once.

### 0.13 and after
- The 0.13 line adds a public `JacksonDeserializer` constructor taking an
  `ObjectMapper` and is the last to support Java 7. The next line requires
  Java 8 and renames `io.jsonwebtoken.lang.Supplier` to
  `io.jsonwebtoken.security.ConfidentialValue`.

## Upstream docs
- https://github.com/jwtk/jjwt
- https://github.com/jwtk/jjwt/blob/master/CHANGELOG.md
- https://javadoc.io/doc/io.jsonwebtoken/jjwt-api
- https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_Cheat_Sheet.html
