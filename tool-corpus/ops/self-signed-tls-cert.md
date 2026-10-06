# Tool: self-signed-tls-cert

> Project-agnostic capability notes, kept in the seed's tool corpus
> (`tool-corpus/README.md`). Orientation for a reusable tool, small enough to
> adopt whole. For **internal/throwaway** use only, never a public-facing
> endpoint.

## 0. Identity

- **Category:** ops
- **Name:** self-signed-tls-cert
- **Language / runtime:** bash + `openssl` 1.1.1 or later (the first line
  whose `req` documents `-addext` and whose `x509` documents `-ext`)
- **Stability:** **portable**: a self-contained generator

## 1. What it does

Idempotently generates a self-signed TLS key/cert pair for internal, local, or
throwaway use (dev TLS, an internal service-to-service link, a test endpoint). It
exists to stop the recurring "why does the client reject my cert?" cycle by
encoding the one detail people forget, and to be safely re-runnable: it does not
regenerate an existing cert unless forced.

## 2. Interface & invocation

```sh
gen-cert.sh <host-identity> [--force]
#   host-identity: the name or address the cert is issued for; an address
#                  becomes an IP: SAN, a name a DNS: SAN
#   --force:       regenerate even if a cert already exists; it must be the
#                  second argument, the script reads no other position
#   EXTRA_SAN:     more SAN entries, e.g. "DNS:localhost,IP:127.0.0.1"
#   OUT_DIR:       where tls.crt and tls.key go (default: .)
```

- **Inputs:** the target host identity; optional `EXTRA_SAN`; optional
  `--force`; the output directory.
- **Outputs:** a private key (mode `600`) and a self-signed certificate; a skip
  message when a cert with the same name set already exists.
- **Exit codes:** 0 generated, or skipped because the existing cert already
  carries exactly the requested names; 1 a cert exists with a **different**
  name set and `--force` was not given; any other non-zero is an `openssl`
  failure.
- **Preconditions:** `openssl` 1.1.1 or later on PATH; write access to the
  output directory.

## 3. Approach / algorithm

- **Put the host identity in BOTH the CN and the `subjectAltName`.** This is the
  durable, load-bearing detail: **modern TLS clients ignore a CN-only certificate**
  and validate the name against the SAN. A cert with the name only in the CN will
  be rejected by current browsers and many libraries even though it "looks right".
  Set the SAN (`DNS:<host>`, or `IP:<addr>` for a bare address).
- **Idempotent by default, against the same inputs only:** if the target
  cert already exists, read its SAN set (`openssl x509 -noout -ext
  subjectAltName`) and compare it with the requested set. Equal: skip and say
  so. Different: **refuse with exit 1** and print both sets. Only `--force`
  overwrites. Re-running the deploy must not silently mint a new cert (which
  breaks peers that already trust the old one), and it must not report
  "exists, skipping" as success when the operator asked for a different name.

Portable skeleton (stack-neutral):

```bash
#!/usr/bin/env bash
set -euo pipefail
HOST="${1:?host identity required}"; FORCE="${2:-}"
CRT="${OUT_DIR:-.}/tls.crt"; KEY="${OUT_DIR:-.}/tls.key"
# SAN set: the host (IP: for an address, DNS: for a name) plus EXTRA_SAN,
# e.g. EXTRA_SAN="DNS:localhost,IP:127.0.0.1"
if [[ "$HOST" =~ ^[0-9.]+$ || "$HOST" == *:* ]]; then SAN="IP:${HOST}"; else SAN="DNS:${HOST}"; fi
[ -n "${EXTRA_SAN:-}" ] && SAN="${SAN},${EXTRA_SAN}"

norm() {  # a SAN list as sorted "TYPE:value" lines; openssl prints "IP Address:"
  tr ',' '\n' | sed -e 's/^ *//' -e 's/^IP Address:/IP:/' | grep -v '^$' | sort -u
}
printed_san() {  # the requested SAN as openssl prints it (IPv6 in its own notation),
  local t; t="$(mktemp -d)"   # read back from a throwaway cert
  openssl req -x509 -newkey ec -pkeyopt ec_paramgen_curve:prime256v1 -nodes \
    -keyout "$t/k" -out "$t/c" -days 1 -subj "/CN=probe" \
    -addext "subjectAltName=${SAN}" 2>/dev/null \
    && openssl x509 -in "$t/c" -noout -ext subjectAltName | tail -n +2
  rm -rf "$t"
}

if [ -f "$CRT" ] && [ "$FORCE" != "--force" ]; then
  have="$(openssl x509 -in "$CRT" -noout -ext subjectAltName 2>/dev/null \
          | tail -n +2 | norm)"
  want="$(printed_san | norm)"
  if [ "$have" = "$want" ]; then
    echo "cert exists at $CRT with the requested names: skipping"; exit 0
  fi
  echo "refusing: $CRT exists with a different name set" >&2
  echo "  existing: $(echo $have)" >&2
  echo "  wanted:   $(echo $want)" >&2
  echo "  pass --force to regenerate (peers that trust the old cert must re-trust)" >&2
  exit 1
fi

openssl req -x509 -newkey rsa:2048 -nodes -sha256 \
  -keyout "$KEY" -out "$CRT" -days 365 \
  -subj "/CN=${HOST}" \
  -addext "subjectAltName=${SAN}" \
  -addext "extendedKeyUsage=serverAuth"
# the SAN carries the name: CN alone is ignored by modern clients.
# Apple platforms also require the serverAuth EKU on a TLS server cert.
chmod 600 "$KEY"
echo "generated self-signed cert for ${SAN}"
```

## 4. Portable vs blueprint

- **Portable (use as-is):** the entire generator: the CN+SAN rule, the
  `serverAuth` extended key usage, the SAN-set comparison before a skip, the
  `--force` behavior, key perms. It is pure `openssl`.
- **Fill in:** output paths, key type/size and validity period per policy
  (at most 825 days when Apple clients must trust the cert; the skeleton uses
  365), and the extra names (`EXTRA_SAN`) each deployment mode needs.
- **Adopting note:** `openssl` prints an IPv6 address in its own notation
  (upper case, expanded). The skeleton therefore compares the existing SAN
  set with the requested set as `openssl` prints it, read back from a
  throwaway certificate, so an identical re-run for an IPv6 host skips.

## 5. Pitfalls and sharp edges

- **Generate-if-absent ignores a changed identity input.** A generator that
  only checks whether the file exists keeps the old cert when the operator adds
  a name (a LAN address, a new DNS name), and reports success. Observed in
  practice with a generator that runs in a container's first-start hook and
  keeps the pair in a named volume: a new extra-SAN setting took effect only
  after the volume was removed by hand. The comparison in §3 turns that into a
  refusal that names both sets.
- **A browser's exception for a self-signed cert has a scope, and the engines
  differ:** Firefox keys it by host and port, Chromium by host alone. A page
  that calls an API on a second origin of the same host can then fail in one
  engine only, so serve the API on the same origin as the page. The diagnosis,
  its sources and the same-origin fix are on
  `skill-corpus/same-origin-web-edge.md`.
- **CN-only certs are silently rejected** by modern clients, the single most
  common self-signed-cert failure. The name MUST be in the SAN.
- **Self-signed is for internal/throwaway only.** It is not a substitute for a
  CA-issued cert on anything public-facing; the client must explicitly trust it.
  On a closed network where no public authority can complete a challenge, the
  stronger shape is a certificate the operator supplies (issued by an internal
  authority the clients trust), with the edge failing closed when the
  certificate or key is absent. Put an internal DNS name in the
  SAN in preference to a raw IP: a name survives an address change without a
  reissue, and links already sent keep working. A raw IP with a self-signed
  certificate is a stopgap, recorded as one with the condition that ends it.
- **Non-idempotent regeneration breaks trust.** Overwriting a cert that peers
  already trust on every deploy causes intermittent handshake failures; skip
  unless `--force`.
- **Loose key permissions.** The private key must be owner-only (`600`).

## 6. Tests that cover it

Cover: the generated cert carries the host in **both** CN and SAN
(`openssl x509 -text` shows the SAN); an address becomes an `IP:` SAN, an IPv6
one included; a second run with the same inputs **skips** with exit 0; a run with a different name set
**refuses** with exit 1 and names both sets; `--force` regenerates; the key file
is mode `600`.

Recorded when the comparison was added (OpenSSL 3, a scratch directory): first
run generated `DNS:app.example.test` (exit 0); the same run again skipped
(exit 0); the same host with `EXTRA_SAN=IP:192.0.2.10` refused and printed
both sets (exit 1); with `--force` it regenerated (exit 0); the next identical
run skipped (exit 0); an address as the host produced `IP Address:192.0.2.20`
and the key was mode `600`. Re-run after the IPv6 and EKU fixes (OpenSSL 3):
the same sequence gave the same exit codes; `::1` and `2001:db8::1` generated
and then skipped on an identical re-run (exit 0); `2001:db8::2` over the
`2001:db8::1` cert refused (exit 1); the cert carries
`TLS Web Server Authentication` as its extended key usage.

- **How to run the tests:** `<the plant's test command for shell tooling>`

## 7. References & neighbours

- **Related tools:** `tool-corpus/testing/http-smoke-suite.md` (its TLS
  assertions check this cert binds); `tool-corpus/ops/env-secret-rotation.md`
  (companion local-credential-material handling).
- **Sources:** distilled from practice; OpenSSL 1.1.1
  manual pages for `req -addext` and `x509 -ext`
  (<https://www.openssl.org/docs/man1.1.1/man1/req.html>,
  <https://www.openssl.org/docs/man1.1.1/man1/x509.html>); Apple,
  "Requirements for trusted certificates in iOS 13 and macOS 10.15" (EKU
  `id-kp-serverAuth`, validity of at most 825 days)
  (<https://support.apple.com/en-us/103769>).
- **Skills:** `skill-corpus/same-origin-web-edge.md` (the browser trust scope
  and the same-origin fix).

## 8. Changelog

- 2026-07-16: created by docs-librarian.
- 2026-10-05: enriched by tool-smith. The skip on
  an existing cert now compares the SAN set and refuses on a change; an address
  becomes an `IP:` SAN; `EXTRA_SAN` added. New pitfalls: a changed identity
  input ignored by generate-if-absent, and the browser exception scope that
  breaks a two-origin self-signed deploy.
- 2026-10-05: review fixes. The browser exception-scope pitfall is cut to one
  sentence and a pointer to the skill that owns it. The SAN comparison reads
  the requested set back through `openssl`, so an identical re-run for an IPv6
  host now skips instead of refusing. The skeleton sets `extendedKeyUsage=serverAuth`, as
  the source plant's generator did, and "Fill in" names the 825-day ceiling
  for Apple clients. The usage line says `--force` must be the second
  argument.
- 2026-10-05: the internal-only pitfall now names the closed-network
  alternative (an operator-supplied certificate, a DNS name in the SAN) and
  marks a raw-IP self-signed certificate as a recorded stopgap, by
  docs-librarian.
