# cryptography — pypi

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions: for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
`cryptography` gives Python developers cryptographic recipes (high-level and
safe by default) and primitives (low-level, under `cryptography.hazmat`). Its
stated aim is to be a "cryptographic standard library" for Python. The
distribution and the import are both `cryptography`. Licence: dual,
Apache-2.0 or BSD. It is the crypto backend for many other packages, among
them the asymmetric algorithms of `library-corpus/pypi/pyjwt.md` and the
Ansible modules on `library-corpus/galaxy/community.crypto.md`.

## Install, setup and configuration
- `pip install cryptography` is normally all it takes. The Linux (manylinux
  and musllinux), macOS and Windows wheels are statically linked and ship
  their own OpenSSL, so the system OpenSSL is not used. Upgrade pip first: an
  old pip may miss the wheel and fall back to a source build.
- A source build (a platform with no wheel) needs a C compiler, a Rust
  compiler, the Python headers, and the OpenSSL and libffi headers. The build
  backend is maturin; the runtime depends on `cffi` (except on PyPy).
- There is no global configuration and no backend selection to make: OpenSSL
  is an internal implementation detail.

## Core API / usage shape
- Keys: `serialization.load_pem_private_key(data, password)`,
  `load_pem_public_key(data)`, `load_der_*` for DER, and
  `load_ssh_private_key` for OpenSSH-format private keys. The loaders return
  typed key objects (RSA, DSA, EC, Ed25519 and others); branch with
  `isinstance` against the `rsa`, `ec`, ... classes.
- Certificates: `x509.load_pem_x509_certificate(data)`, and
  `x509.load_pem_x509_certificates(data)` for a bundle.
- Building: `x509.CertificateBuilder()` and
  `x509.CertificateSigningRequestBuilder()` are immutable. Each method returns
  a new builder; add extensions with `add_extension(ext, critical=...)` and
  finish with `sign(private_key, hashes.SHA256())`.
- Symmetric recipe: `key = Fernet.generate_key()`,
  `token = Fernet(key).encrypt(data)`, `Fernet(key).decrypt(token, ttl=None)`.
  The key is 32 bytes, URL-safe base64. `MultiFernet([new, old])` encrypts
  with the first key and decrypts with any; `rotate(token)` re-encrypts under
  the first.

## Idioms & best practices
- Use a recipe (Fernet, the x509 loaders and builders) before reaching for
  hazmat. The hazmat layer is labelled "Hazardous Materials": use it only when
  you are sure of what you are doing.
- Derive a Fernet key from a password with a KDF; never use the password
  itself as the key.
- Rotate Fernet keys with `MultiFernet`: put the new key first, re-encrypt
  stored tokens with `rotate`, then drop the old key.
- Observed in practice: declare `cryptography` explicitly when your code calls
  it, rather than relying on it arriving through another package's extra.
  Treat a multi-major bump as a change to the dependency tree: run `pip check`
  and an import and round-trip smoke test, because dependents set floors and
  majors drop platforms and Python versions.

## General pitfalls
- Fernet holds the whole message in memory and never exposes unauthenticated
  bytes, which makes it unsuitable for very large files.
- `Fernet.decrypt` raises one exception, `InvalidToken`, for an expired
  token (`ttl`), a malformed token and a bad signature alike; the reason is not
  in the exception.
- A lost Fernet key makes the data unrecoverable, and anyone holding the key
  can both decrypt and forge tokens.
- Recent major lines raise `UnsupportedAlgorithm` instead of `ValueError` when
  a key uses an unsupported algorithm or explicit curve encoding; an `except
  ValueError` around a loader stops catching it.

## Testing
- Application tests normally exercise round trips with generated keys:
  encrypt then decrypt, sign then verify, load then serialize. Upstream
  documents test vectors for its own algorithms, not a testing guide for
  callers.
- Generate keys in the test (`rsa.generate_private_key(...)`,
  `Fernet.generate_key()`); never commit a real private key as a fixture.

## Security defaults
- Recipes are safe by default; hazmat leaves every parameter choice to you.
- Documented API behaviour does not change between releases (the API-stability
  policy). Non-cryptographic parsing such as ASN.1 is rewritten in Rust for
  memory safety.
- Known vulnerabilities are published on osv.dev and scannable with
  `pip-audit` or `osv-scanner`.
- Observed in practice: because the wheels bundle OpenSSL, an OpenSSL advisory
  is fixed by upgrading `cryptography`, not by patching the operating system's
  OpenSSL. The docs state the static linking; the upgrade rule follows from it.

## Operational behaviour
- Wheels are self-contained, so behaviour does not depend on the host's
  OpenSSL; a source build links whatever OpenSSL it finds. Supported OpenSSL
  versions (3.x and later, plus BoringSSL, aws-lc and supported LibreSSL) are
  listed on the installation page.
- The `Fernet` class is thread-safe. Upstream says nothing about the
  thread-safety of other objects.

## Interop
- PyJWT uses it for RS/ES/PS/EdDSA; its `pyjwt[crypto]` extra pulls it in, and
  a `cryptography` key object is a valid PyJWT key
  (`library-corpus/pypi/pyjwt.md`).
- The Ansible `community.crypto` modules need it on the host where the module
  executes (`library-corpus/galaxy/community.crypto.md`).

## Major lines

### From the 35 line on
- The version is `X.0.Z`: X, the major, increments on every feature release;
  the middle number is always 0; Z increments for compatible fixes. Majors
  therefore arrive often.
- Deprecation window: a feature emits `CryptographyDeprecationWarning` in
  majors X+1 and X+2 and is removed or changed in X+3, so code that runs
  without warnings keeps working for two more majors. For a widely used API,
  upstream may grant a longer deprecation period at its discretion.
- A major may still drop platform or Python support without a warning cycle
  (the changelog marks such entries as backwards incompatible). Read the
  changelog entries between your old and new majors before bumping.

### Before the 35 line
- Releases used a custom scheme: X.Y was one decimal number, raised for any
  potentially backwards-incompatible release, and Z counted compatible
  releases. The two-major deprecation window above does not describe these
  releases.

## Upstream docs
- Docs: https://cryptography.io/
- Repo: https://github.com/pyca/cryptography
