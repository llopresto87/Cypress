# Tool: self-signed-tls-cert

> Project-agnostic, durable capability notes, folded into the seed by the
> harvest protocol. Orientation for a reusable tool — small enough to adopt
> whole. For **internal/throwaway** use only, never a public-facing endpoint.

## 0. Identity

- **Category:** ops
- **Name:** self-signed-tls-cert
- **Language / runtime:** bash + `openssl`
- **Stability:** **portable** — a self-contained generator

## 1. What it does

Idempotently generates a self-signed TLS key/cert pair for internal, local, or
throwaway use (dev TLS, an internal service-to-service link, a test endpoint). It
exists to stop the recurring "why does the client reject my cert?" cycle by
encoding the one detail people forget, and to be safely re-runnable: it does not
regenerate an existing cert unless forced.

## 2. Interface & invocation

```sh
gen-cert.sh <host-identity> [--force]
#   host-identity: the CN/SAN name the cert is issued for (hostname/DNS name)
#   --force:       regenerate even if a cert already exists (default: skip)
```

- **Inputs:** the target host identity; optional `--force`; output paths from
  config.
- **Outputs:** a private key and a self-signed certificate; a skip message when a
  cert already exists and `--force` was not given.
- **Preconditions:** `openssl` on PATH; write access to the output directory.

## 3. Approach / algorithm

- **Put the host identity in BOTH the CN and the `subjectAltName`.** This is the
  durable, load-bearing detail: **modern TLS clients ignore a CN-only certificate**
  and validate the name against the SAN. A cert with the name only in the CN will
  be rejected by current browsers and many libraries even though it "looks right".
  Set the SAN (`DNS:<host>`, or `IP:<addr>` for a bare address).
- **Idempotent by default:** if the target cert already exists, **skip
  regeneration** and report it; only `--force` overwrites. Re-running the deploy
  must not silently mint a new cert (which would break already-trusted peers).

Portable skeleton (stack-neutral):

```bash
#!/usr/bin/env bash
set -euo pipefail
HOST="${1:?host identity required}"; FORCE="${2:-}"
CRT="${OUT_DIR:-.}/tls.crt"; KEY="${OUT_DIR:-.}/tls.key"

if [ -f "$CRT" ] && [ "$FORCE" != "--force" ]; then
  echo "cert exists at $CRT — skipping (pass --force to regenerate)"; exit 0
fi

openssl req -x509 -newkey rsa:2048 -nodes \
  -keyout "$KEY" -out "$CRT" -days 365 \
  -subj "/CN=${HOST}" \
  -addext "subjectAltName=DNS:${HOST}"     # <-- CN alone is ignored by modern clients
chmod 600 "$KEY"
echo "generated self-signed cert for ${HOST}"
```

## 4. Portable vs blueprint

- **Portable (use as-is):** the entire generator — the CN+SAN rule, the
  idempotent skip/`--force` behavior, key perms. It is pure `openssl`.
- **Fill in:** output paths, key type/size and validity period per policy, and
  whether the name is a DNS name or an IP (`IP:` SAN).

## 5. Pitfalls and sharp edges

- **CN-only certs are silently rejected** by modern clients — the single most
  common self-signed-cert failure. The name MUST be in the SAN.
- **Self-signed is for internal/throwaway only.** It is not a substitute for a
  CA-issued cert on anything public-facing; the client must explicitly trust it.
- **Non-idempotent regeneration breaks trust.** Overwriting a cert that peers
  already trust on every deploy causes intermittent handshake failures; skip
  unless `--force`.
- **Loose key permissions.** The private key must be owner-only (`600`).

## 6. Tests that cover it

Cover: the generated cert carries the host in **both** CN and SAN
(`openssl x509 -text` shows the SAN); a second run without `--force` **skips**;
`--force` regenerates; the key file is mode `600`.

- **How to run the tests:** `<the plant's test command for shell tooling>`

## 7. References & neighbours

- **Related tools:** `tool-corpus/testing/http-smoke-suite.md` (its TLS
  assertions check this cert binds); `tool-corpus/ops/env-secret-rotation.md`
  (companion local-credential-material handling).
- **Sources:** distilled from harvested plant experience; no external URL.

## 8. Changelog

- 2026-07-16 — created from harvested, generalized capability, by docs-librarian.
