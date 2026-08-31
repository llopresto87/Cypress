# Tool: http-smoke-suite

> Project-agnostic, durable capability notes, folded into the seed by the
> harvest protocol. Orientation for a reusable tool — the assertion set is
> project-specific, but the harness, idioms, and the known-bug discipline are
> portable and re-usable as-is.

## 0. Identity

- **Category:** testing
- **Name:** http-smoke-suite
- **Language / runtime:** bash, using only **`curl` and `openssl`** (no test
  framework, no language runtime) so it runs anywhere the deploy target does
- **Stability:** **portable** — the harness skeleton is stack-neutral; only the
  concrete assertions are filled per project

## 1. What it does

A dependency-light post-deploy smoke suite that makes **N boolean,
protocol-level assertions** against a just-deployed endpoint and exits non-zero
if any fail. It answers "is the thing actually serving, correctly, right now?"
without pulling in a test framework — it needs only tools already present on any
host that can reach the service. It is the gate the deploy pipeline runs after
healthcheck.

## 2. Interface & invocation

```sh
smoke.sh [SECTION] [--json]
#   SECTION: run one named section of checks; omit it to run all of them
#   --json:  machine-readable records instead of the colored PASS/FAIL lines
#   the target base URL/host comes from env/config
#   exit 0 if every assertion passed; non-zero if any failed
```

- **Inputs:** the target base URL/host; an optional **section selector** —
  checks are grouped into independently-selectable named sections, which is what
  keeps the suite from being one monolithic all-or-nothing script and lets an
  operator debugging one surface run just that section; optional per-assertion
  config via env.
- **Outputs:** by default one colored `PASS`/`FAIL` line per assertion plus a
  summary count; under `--json`, one `{section, check, pass, detail}` record per
  check, which is what lets CI attribute a failure to an area. Either mode — and
  a selective run as much as a full one — ends in a **single non-zero exit** on
  any failure, so narrowing the run never weakens the gate.
- **Preconditions:** `curl` and `openssl` on PATH; the target reachable.

## 3. Approach / algorithm

Each assertion is a small function returning success/failure; a runner wraps each
in PASS/FAIL bookkeeping with counters. Assertions probe **protocol-level truths**
rather than page contents, e.g.:

- TLS actually binds and negotiates on the secure port (`openssl s_client`).
- A plaintext request **redirects** to the TLS endpoint (not served in the
  clear).
- The health/liveness path returns healthy; the app root serves.
- An endpoint that must require auth **rejects** an unauthenticated request
  (assert the 401/403 — verify the guard is *enforced*, not merely that authed
  requests work).
- A realtime/upgrade handshake (e.g. a WebSocket upgrade) reaches its backend and
  gets the expected switching-protocols response.
- A surface that must be **closed** serves nothing at all — the negative
  assertion, whose only passing signal is a **connection reset or EOF at the
  transport level**. Assert the transport outcome (a connection-failure exit
  from `curl`, a failed `openssl s_client` connect), never a status code and
  never the body: any HTTP reply proves the endpoint is alive, which is exactly
  what the assertion denies. Pin a short `--max-time`, and decide deliberately
  whether a *timeout* counts as passing — a dropped or filtered packet is a
  weaker signal than a reset.

The distinctive, durable idiom — **`KNOWN_BUG_*` assertions**:

- For each **confirmed-broken** behavior, add an explicitly-named assertion (e.g.
  `KNOWN_BUG_redirect_drops_query`) that asserts **today's broken behavior on
  purpose**, with the root cause documented inline.
- It PASSES while the bug exists and **flips to FAIL once the bug is fixed** —
  turning the suite red exactly when someone fixes the bug without removing its
  known-bug marker. This makes technical debt **mechanically visible** and
  impossible to silently absorb: a known bug is either still asserted (and
  tracked) or the fix forces you to promote it to a real assertion.

## 4. Portable vs blueprint

- **Portable (use as-is):** the PASS/FAIL counter harness, colored output, single
  aggregate exit code, the `assert` wrapper with its section selector and
  `{section, check, pass, detail}` JSON record, and the `KNOWN_BUG_*`
  convention.
- **Project-specific (fill in):** the concrete URLs, ports, expected status
  codes, auth scheme, section names, and which protocol facts matter for the
  given service.

Portable skeleton (harness is complete; assertions are examples to replace):

```bash
#!/usr/bin/env bash
set -uo pipefail                       # NOT -e: we want every assertion to run
BASE="${SMOKE_BASE_URL:?set base url}" # target from env/config
SECTION=all; JSON=                     # smoke.sh [SECTION] [--json]
for a in "$@"; do case "$a" in --json) JSON=1 ;; *) SECTION="$a" ;; esac; done
G=$'\033[32m'; R=$'\033[31m'; Z=$'\033[0m'
pass=0; fail=0

assert() {                             # assert <section> "name" <cmd...>
  local sec="$1" name="$2"; shift 2
  [ "$SECTION" = all ] || [ "$SECTION" = "$sec" ] || return 0
  local detail ok
  if detail="$("$@" 2>&1)"; then ok=true;  pass=$((pass+1))
  else                          ok=false; fail=$((fail+1)); fi
  detail="${detail%%$'\n'*}"; detail="${detail//\"/}"      # one quote-free line
  if [ -n "$JSON" ]; then
    printf '{"section":"%s","check":"%s","pass":%s,"detail":"%s"}\n' \
           "$sec" "$name" "$ok" "$detail"
  elif $ok; then printf '%sPASS%s %s\n' "$G" "$Z" "$name"
  else           printf '%sFAIL%s %s\n' "$R" "$Z" "$name"
  fi
}

# --- protocol-level assertions (replace with the service's real contracts) ---
tls_binds()      { echo | openssl s_client -connect "${HOST:?}:443" -servername "${HOST}" 2>/dev/null | grep -q "BEGIN CERTIFICATE"; }
plain_redirects(){ [ "$(curl -s -o /dev/null -w '%{http_code}' "http://${HOST}/")" -ge 300 ]; }
health_ok()      { curl -fsS "$BASE/health" >/dev/null; }
auth_enforced()  { [ "$(curl -s -o /dev/null -w '%{http_code}' "$BASE/protected")" = 401 ]; }
port_closed()    { ! curl -s -o /dev/null --max-time 5 "http://${HOST}:${CLOSED_PORT:?}/"; }

assert tls  "tls binds"                         tls_binds
assert tls  "plaintext redirects to tls"        plain_redirects
assert app  "health endpoint serves"            health_ok
assert auth "protected route rejects anon"      auth_enforced
assert edge "closed port serves nothing at all" port_closed   # ANY HTTP reply FAILS

# --- KNOWN BUG: asserts TODAY's broken behavior on purpose. ---
# root cause: <one-line cause>. Flips FAIL when fixed -> promote to a real assert.
known_bug_x() { : ; }   # <cmd that succeeds WHILE the bug is present>
assert bugs "KNOWN_BUG_x (expected to flip when fixed)" known_bug_x

[ -n "$JSON" ] || printf '\n%d passed, %d failed\n' "$pass" "$fail"
[ "$fail" -eq 0 ]
```

## 5. Pitfalls and sharp edges

- **`set -e` short-circuits the suite.** With `-e` the first failing assertion
  aborts the run and you never see the rest. Use `set -uo pipefail` and let the
  `assert` wrapper own pass/fail.
- **Testing page content instead of protocol facts** is brittle; assert status
  codes, redirects, TLS negotiation, and auth enforcement.
- **A removed `KNOWN_BUG_*` marker hides regressions.** If someone deletes the
  known-bug assertion instead of promoting it, the debt vanishes from view —
  code review must catch that.
- **Asserting only the happy path for auth** proves nothing; assert that the
  unauthenticated request is *rejected*.
- **Accepting an error status as proof that a surface is closed.** A 500 or 403
  from a supposedly-removed route is a *failing* assertion, not a passing one —
  see the negative assertion in §3.
- **The self-evidencing instrument.** When the harness itself *is* the
  acceptance record — no independent CI gate sitting above it — a bug in the
  harness is a **green lie** with nothing else to catch it. A harness that has
  never been proven to fail is not proven to catch anything, which is why §6's
  meta-test is not optional here.

## 6. Tests that cover it

Self-testing, against a stub that returns known responses. **First prove the
harness can go RED** — run it once against a deliberately-broken target (a
stopped service, a wrong port, a stub returning the wrong status) and assert that
it *fails*. That is the check that makes the self-evidencing-instrument pitfall
in §5 falsifiable, so it comes before the suite is trusted as a gate, not after.
Then cover: the aggregate exit code (pass-all → 0, any-fail → non-zero); a
`KNOWN_BUG_*` case flipping when the stub's behavior is "fixed"; a
closed-surface assertion **failing** when the stub answers with an error status
instead of refusing the connection; and selecting one section running only that
section's checks while keeping the same aggregate exit behavior.

- **How to run the tests:** `<the plant's test command for shell tooling>`

## 7. References & neighbours

- **Related tools:** `tool-corpus/ops/container-deploy-pipeline.md` (runs this as
  its post-deploy gate); `tool-corpus/ops/self-signed-tls-cert.md` (supplies the
  cert the TLS assertions check);
  `tool-corpus/ops/disposable-test-identity-provisioner.md` (mints the throwaway
  identities an auth-enforcement assertion authenticates with);
  `tool-corpus/testing/failure-signature-triage.md` (the same
  assert-the-mechanical-fact posture applied to a test run's failures).
- **Sources:** distilled from harvested plant experience; no external URL.

## 8. Changelog

- 2026-07-16 — created from harvested, generalized capability, by docs-librarian.
- 2026-08-06 — folded in three harvested additions, each integrated into the
  section that owns it: the closed-surface negative assertion (§3, with its
  error-status pitfall in §5 and the `port_closed` example in §4's skeleton),
  the section-selectable + JSON-emitting harness (§2's interface and the
  skeleton's `assert` wrapper), and the self-evidencing-instrument pitfall with
  its prove-it-can-go-RED meta-test (§5–§6), by docs-librarian.
