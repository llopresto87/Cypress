# community.crypto — galaxy

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions: for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
`community.crypto` is the Ansible collection for cryptographic assets: OpenSSL
private keys (`openssl_privatekey`, `openssl_privatekey_pipe`), certificate
signing requests (`openssl_csr`, `openssl_csr_pipe`), X.509 certificates
(`x509_certificate` with the `selfsigned`, `ownca` and `acme` providers,
`x509_certificate_pipe`, `x509_certificate_info`), OpenSSH key pairs
(`openssh_keypair`), ACME (`acme_certificate` and the account and order
modules), PKCS#12 files, CRLs and more. Galaxy namespace `community`, name
`crypto`; licence GPL-3.0-or-later. Its backend is the Python `cryptography`
library (`library-corpus/pypi/cryptography.md`).

## Install, setup and configuration
- The collection ships inside the `ansible` community package. On an
  ansible-core-only control node install it with
  `ansible-galaxy collection install community.crypto`, or list it with a
  pinned `version:` range in `collections/requirements.yml`.
- Requirements are per module and apply to the host that executes the module.
  Most modules need `cryptography` importable by that interpreter; each module
  page states its own floor. The `acme` provider of `x509_certificate` also
  needs `acme-tiny`. `openssh_keypair` needs the OpenSSH client tools with
  `backend: openssh`, or `cryptography` (plus `bcrypt` for a passphrase) with
  `backend: cryptography`. Under `connection: local` the executing interpreter
  is the control node's (the interpreter drift is on
  `library-corpus/pypi/ansible-core.md`).

## Core API / usage shape
- Local CA, adapted from the collection's own guide (`cipher: auto` and
  `regenerate: never` added; see Idioms):
  ```yaml
  - community.crypto.openssl_privatekey:
      path: /etc/pki/ca/ca.key
      passphrase: "{{ vault_ca_passphrase }}"
      cipher: auto
      regenerate: never
  - community.crypto.openssl_csr_pipe:
      privatekey_path: /etc/pki/ca/ca.key
      privatekey_passphrase: "{{ vault_ca_passphrase }}"
      common_name: Example CA
      use_common_name_for_san: false
      basic_constraints: ["CA:TRUE"]
      basic_constraints_critical: true
      key_usage: [keyCertSign]
      key_usage_critical: true
    register: ca_csr
  - community.crypto.x509_certificate:
      path: /etc/pki/ca/ca.crt
      csr_content: "{{ ca_csr.csr }}"
      privatekey_path: /etc/pki/ca/ca.key
      privatekey_passphrase: "{{ vault_ca_passphrase }}"
      provider: selfsigned
  ```
  Then, per leaf: a key, an `openssl_csr_pipe` with the subject alternative
  names, and `x509_certificate` with `provider: ownca` (`ownca_path`,
  `ownca_privatekey_path`, `ownca_privatekey_passphrase`).
- The `_pipe` variants take and return content (`csr_content`, the registered
  `.csr`) instead of files, so key material and intermediate files can stay on
  one host.
- `openssl_privatekey` writes the key with mode 0600 unless `mode` is set;
  `passphrase` with `cipher: auto` encrypts it; `backup: true` keeps a
  timestamped copy before an overwrite; `return_content` returns the key.

## Idioms & best practices
- Set `regenerate` explicitly on any key that must never change, a CA key above
  all. `never` fails when the key cannot be read or the passphrase is wrong and
  never replaces it; `fail` fails when the key does not match the options.
- Use `backup: true` on keys and certificates where an overwrite would hurt.
- Mark tasks `no_log: true` when `return_content` or a pipe result carries key
  material, and keep passphrases in vault.
- Observed in practice: a CA certificate whose `key_usage` also lists `cRLSign`
  can sign revocation lists; the collection's guide lists `keyCertSign` only.
- Observed in practice: install the CA root certificate into the trust store
  of every client before validating TLS against certificates it signed. The
  collection issues certificates; it does not distribute trust. Keep a
  trust-store path per OS family and fail on a family that has none; never
  skip it. Once clients trust the root, treat a CA with only one of its
  key and certificate present as an error, not a reason to regenerate, and
  rotate both only behind an explicit switch: a regenerated root key is a new
  root that no client trusts yet.

## General pitfalls
- `openssl_privatekey` `regenerate` takes `never`, `fail`,
  `partial_idempotence`, `full_idempotence` and `always`. The declared default
  is `full_idempotence`, which also regenerates a key it cannot read or whose
  passphrase does not match ("make sure you have a backup"). The option's prose
  still describes the `partial_idempotence` behaviour, which leaves such a key
  alone. Upstream contradicts itself here: trust the declared default, and
  always set the value. `always` is the same as `force: true`.
- With the default, a mistyped CA passphrase can replace the CA key and
  invalidate every certificate it signed. `regenerate: never` on CA keys
  prevents that.
- `openssl_csr`, `openssl_csr_pipe` and `x509_certificate` regenerate an
  existing CSR or certificate that does not match the options or looks
  corrupt; a changed option reissues on the next run.
- `x509_certificate` `ignore_timestamps` defaults to true, and the docs advise
  keeping it true with relative times such as `+365d`. With
  `ignore_timestamps: false` the relative `not_before` / `not_after` resolve
  differently on each run, so the certificate never matches and is reissued
  every time. `force: true` reissues unconditionally. An unexpected reissue
  traces back to one of these or to a changed option.
- Observed in practice: because the `ansible` package bundles this collection,
  a playbook that never declares it works until its first run on an
  ansible-core-only control node. Declare it in `requirements.yml`.

## Testing
- Idempotence is part of each module's contract: run the play twice, and the
  second run must report `ok` for every key, CSR and certificate task. A
  `changed` on the second run points at a timestamp or option mismatch.
- Each module's attribute table states its check-mode and diff support; use
  `--check --diff` only where the table says it is supported.
- Read the result back with `x509_certificate_info` (validity window, issuer,
  extensions) rather than trusting the task status.

## Security defaults
- Private keys are written with mode 0600 by default.
- `return_content` and the `_pipe` results expose key material in the task
  result; the docs advise `no_log`.
- The default `regenerate` policy can replace an unreadable or mis-passphrased
  key, which for a CA key is a trust-root risk. Use `never` or `fail` there.
- Keep CA keys passphrase-protected and the passphrase in vault.

## Operational behaviour
- The modules work on local files or content on the executing host and call no
  service, except the ACME modules, which talk to the ACME directory you
  configure. Upstream records nothing further on runtime behaviour.

## Interop
- `cryptography` is the backend for nearly every module and must import in the
  executing interpreter (`library-corpus/pypi/cryptography.md`).
- `acme_certificate` obtains certificates from an ACME CA; the `acme` provider
  of `x509_certificate` uses `acme-tiny`.

## Major lines

### 2.x line
- `ignore_timestamps` arrives on `x509_certificate`.

### 3.x line
- All `doc_fragments`, `module_utils` and `plugin_utils` become private to the
  collection: other collections must not import them, and they can change in
  any release.
- All content for the Entrust certificate service is removed, after that
  service was shut down.

## Upstream docs
- Docs: https://docs.ansible.com/ansible/latest/collections/community/crypto/
- Repo: https://github.com/ansible-collections/community.crypto
