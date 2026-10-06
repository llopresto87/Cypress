# pyjwt — pypi

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions: for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
PyJWT encodes and decodes JSON Web Tokens (RFC 7519) in Python. The
distribution is `PyJWT` (`pip install pyjwt`); the import name is `jwt`.
Licence: MIT. The core is pure Python; the asymmetric algorithms come from the
`cryptography` library. The issuer and verifier roles in a mixed-language
system are described on `library-corpus/maven/jjwt.md`; this page covers the
Python side.

## Install, setup and configuration
- `pip install pyjwt` gives HS256/384/512 (and `none`). RSA, ECDSA, RSA-PSS and
  EdDSA need `cryptography`, installed through the `pyjwt[crypto]` extra.
  Upstream recommends writing the extra form in requirements files, because a
  bare `cryptography` line can later be mistaken for an unused requirement and
  removed.
- There is no global configuration. Options are set per instance
  (`jwt.PyJWT(options={...})`) or per call (`decode(..., options={...})`). The `verify_*` options (`verify_signature`,
  `verify_exp`, `verify_nbf`, `verify_iat`, `verify_aud`, `verify_iss`,
  `verify_sub`, `verify_jti`) default to True. `require` defaults to an empty
  list. `strict_aud` and `enforce_minimum_key_length` default to False; with
  the latter True, a short key raises `InvalidKeyError` instead of only
  warning.

## Core API / usage shape
- `jwt.encode(payload, key, algorithm="HS256", headers=None)` returns a `str`.
- `jwt.decode(token, key, algorithms=[...], audience=, issuer=, leeway=0,
  options={...})` checks the signature and the registered claims and returns
  the claim dict. `jwt.decode_complete` returns header, payload and signature.
- `jwt.get_unverified_header(token)` reads the header (for `kid`) without
  verifying anything.
- `jwt.PyJWKClient(uri, cache_keys=False, max_cached_keys=16,
  cache_jwk_set=True, lifespan=300, headers=None, timeout=30, ssl_context=None,
  cooldown_duration=30)`;
  `client.get_signing_key_from_jwt(token).key` picks the key by `kid`.
- Errors descend from `jwt.PyJWTError`. Validation failures are
  `InvalidTokenError` and its subclasses: `ExpiredSignatureError`,
  `InvalidAudienceError`, `InvalidIssuerError`, `MissingRequiredClaimError`,
  `InvalidSignatureError`, `InvalidAlgorithmError`, `DecodeError`.

## Idioms & best practices
- Verifier shape:
  ```python
  claims = jwt.decode(
      token, public_key, algorithms=["RS256"],
      audience=EXPECTED_AUD, issuer=EXPECTED_ISS, leeway=30,
      options={"require": ["exp", "iat", "aud", "iss"]},
  )
  ```
  Catch `jwt.InvalidTokenError` (or `PyJWTError`) around it and treat every
  failure as a rejection. Mapping that rejection to HTTP 401 is application
  practice, not something PyJWT does.
- Pass a parsed key object (a `cryptography` public key, or the `.key` of a
  PyJWK) for asymmetric verification rather than a PEM string. A
  passphrase-protected private key is passed as a `cryptography` key object.
- With a JWKS endpoint, build one `PyJWKClient` per issuer at startup and reuse
  it, so its cache works.
- Observed in practice: a verifier service holds only the public key, and the
  claim set is a contract with an issuer that may be another language's
  library. Write the required claims down on both sides. Upstream is silent on
  this.

## General pitfalls
- `decode` with signature verification on and no `algorithms` raises
  `DecodeError` ("It is required that you pass in a value for the algorithms
  argument"), except when the key is a PyJWK.
- A token whose header `alg` is outside `algorithms` raises
  `InvalidAlgorithmError`; a header with no `alg` fails too.
- A missing `cryptography` does not fail `import jwt`. It surfaces when an
  RS/ES/PS/EdDSA algorithm is looked up during `encode` or `decode`, as
  `NotImplementedError("Algorithm 'RS256' could not be found. Do you have
  cryptography installed?")`. An import smoke test does not catch it; a
  decode test does.
- `exp` is checked only when the token carries it. A token with no `exp` never
  expires unless `require` lists `exp`. `require` fails on an absent or null
  claim.
- A token carrying `aud` decoded without `audience=` raises
  `InvalidAudienceError`. Passing `audience=` against a token with no `aud`
  raises `MissingRequiredClaimError`.
- Observed in practice: PyJWT often arrives only as a transitive dependency.
  Whether an advisory against it matters depends on whether anything in the
  process calls `jwt.decode`. Upstream does not discuss this.

## Testing
- Encode a token with a test key, then decode it with the same algorithm list
  the production verifier uses. Upstream gives no testing guide beyond the
  examples on its usage page.
- For expiry, encode `exp` as a UTC timestamp or an aware `datetime`; decode
  compares it with the current UTC time, with `leeway` added.
- Cover the rejections, not only the happy path: wrong `alg`, missing `exp`,
  wrong `aud`, wrong `iss`, tampered signature. Each maps to one exception
  class above.

## Security defaults
- The `algorithms=` allow-list blocks `alg: none` and algorithm substitution.
  The `none` algorithm also needs `key=None`, so it cannot verify by accident
  with a real key.
- HMAC key preparation refuses a key that looks like a PEM or DER asymmetric
  key or an X.509 certificate, as a defence against algorithm confusion. Never
  list HS* and asymmetric algorithms together for one verifier; a parsed key
  object narrows the surface further.
- `verify_signature=False` reads claims with no check at all; the docs call
  that generally ill-advised.
- `PyJWKClient` rejects URI schemes other than http and https, so a `file:`
  URI cannot be fetched.
- Observed in practice: take the JWKS URL from trusted configuration, over
  https, never from a token header such as `jku` or `x5u`. The docs do not
  mention `jku`, and the client itself still accepts plain http.

## Operational behaviour
- `PyJWKClient` fetches the key set with urllib (default timeout 30 s), caches
  it for `lifespan` seconds (default 300), and refetches once when a `kid` is
  not in the cached set, subject to a cooldown. A failed fetch keeps the cached
  set. Each fetch is a blocking call on the request path when the cache is cold.
- `encode` and `decode` are CPU-only and hold no state between calls.

## Interop
- `cryptography` is the only crypto backend. Keys from
  `cryptography.hazmat.primitives.serialization.load_pem_public_key` /
  `load_pem_private_key`, and a certificate's
  `x509.load_pem_x509_certificate(...).public_key()`, can be passed directly
  (`library-corpus/pypi/cryptography.md`).
- Tokens interoperate with other JOSE libraries (for example a Java issuer on
  `library-corpus/maven/jjwt.md`) as long as both sides agree on the algorithm,
  the key, and the required claims.

## Major lines

### 1.x line
- `encode` returns `bytes`; `algorithms` on `decode` is optional; PyCrypto and
  ECDSA backends exist alongside `cryptography`; deprecated exception aliases
  such as `ExpiredSignature` still exist.

### 2.x line
- Python 2 support is gone and `cryptography` is the only backend.
  `encode` returns `str`, `algorithms` is required on `decode`, and only the
  `...Error` exception names remain. A signature failure raises
  `InvalidSignatureError`, a subclass of `DecodeError`.
- Later 2.x releases add validation (`iat`, `sub`, `jti`, the `crit` header),
  minimum-key-length warnings, and hardening of `PyJWKClient`. Read the
  changelog before relying on an edge behaviour of your pin.

## Upstream docs
- Docs: https://pyjwt.readthedocs.io/
- Repo: https://github.com/jpadilla/pyjwt
