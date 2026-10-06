# Tool: http-smoke-suite

> Project-agnostic capability notes, kept in the seed's tool corpus
> (`tool-corpus/README.md`). Orientation for a reusable tool: the assertion set
> is project-specific, but the harness and its idioms are portable and re-usable
> as-is.

## 0. Identity

- **Category:** testing
- **Name:** http-smoke-suite
- **Language / runtime:** bash, using only **`curl` and `openssl`** (no test
  framework, no language runtime) so it runs anywhere the deploy target does,
  or busybox `wget` inside a service container when the host has no HTTP
  client (§3)
- **Stability:** **portable**. The harness skeleton is stack-neutral; only the
  concrete assertions are filled per project

## 1. What it does

A dependency-light post-deploy smoke suite that makes **N boolean,
protocol-level assertions** against a just-deployed endpoint and exits non-zero
if any fail. It answers "is the thing actually serving, correctly, right now?"
without pulling in a test framework: it needs only tools already present on any
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
  config via env (`SMOKE_UNROUTED_PREFIX` places the unrouted-path probe, §3).
- **Outputs:** by default one colored `PASS`/`FAIL` line per assertion plus a
  summary count; under `--json`, one `{section, check, pass, detail}` record per
  check, which is what lets CI attribute a failure to an area. Either mode — and
  a selective run as much as a full one — ends in a **single non-zero exit** on
  any failure, so narrowing the run never weakens the gate.
- **Base path:** an optional path prefix (`SMOKE_BASE_PATH`, empty by
  default) that is put in front of every probed path. Write it with a leading
  slash and no trailing one (`/app`): it is concatenated, so `/app/` probes
  `//health`, which only an edge that merges slashes forgives. When the service is
  published under a sub-path of a shared edge proxy, set it to that prefix, so
  the suite probes the public path users reach and not only the direct
  origin. A suite that probes only the origin stays green while the prefixed
  route, its rewrite or its upgrade headers are broken.
- **Preconditions:** `curl` and `openssl` on PATH; the target reachable. For
  the in-network mode instead: `docker` on the host, and a running container
  whose `wget` supports `-S` and `-T` (`docker exec <c> wget --help`). Pass
  the container's real name: a compose project prefix and a replica suffix
  are part of it.

## 3. Approach / algorithm

Each assertion is a small function returning success/failure; a runner wraps each
in PASS/FAIL bookkeeping with counters. Assertions probe **protocol-level truths**
rather than page contents, e.g.:

- TLS actually binds and negotiates on the secure port (`openssl s_client`).
- A plaintext request **redirects** to the TLS endpoint (not served in the
  clear).
- The health/liveness path returns healthy; the app root serves.
- An endpoint that must require auth **rejects** an unauthenticated request
  (assert the 401/403, and verify the guard is *enforced*, not merely that authed
  requests work). The same assertion doubles as a **route-existence proof**: a
  rejection can only come from a route the edge actually has, whereas a
  not-found is ambiguous between a route that is missing and a route that is
  hidden and reads as the good news either way, so asserting the rejection makes
  a silently-dropped route fail the suite instead of passing it.
- A realtime/upgrade handshake (e.g. a WebSocket upgrade) reaches its backend and
  gets the expected switching-protocols response.
- A surface that must be **closed** serves nothing at all — the negative
  assertion, whose only passing signal is a **connection reset or EOF at the
  transport level**. Assert the transport outcome (a connection-failure exit
  from `curl`, a failed `openssl s_client` connect), never a status code and
  never the body: any HTTP reply proves the endpoint is alive, which is exactly
  what the assertion denies. Pin a short `--max-time`, and decide deliberately
  whether a *timeout* counts as passing: a dropped or filtered packet is a
  weaker signal than a reset.
- **One unrouted path must return 404.** Probe a path that no route serves
  (`/no-such-route-<random>`) and assert 404. This negative control proves
  that the route table decides what is served. Without it, a catch-all route
  that answers every path with 200 makes every "this route serves" assertion
  pass whether the route exists or not. Probe where no fallback applies. An
  origin that serves a single-page app with history-mode fallback answers
  every unknown non-API path with 200 and the HTML shell, and that is correct
  behaviour, so a probe at its root stays red for good. There, set
  `SMOKE_UNROUTED_PREFIX` to the API prefix (`/api`) so the probe lands
  under it; at a gateway with no fallback, leave it empty. If the API prefix
  has a fallback too, assert instead that the unknown API-shaped path is not
  the HTML shell (a 404, or a JSON media type).
- **Each expected service is registered in the discovery registry**, when the
  stack routes through one. List the registered names from the registry's
  own API and match each expected name exactly (`grep -x`), not as a
  substring. A route to a service that never registered fails only at the
  first real request, and a substring match passes `ORDERS` when only
  `ORDERS-ARCHIVE` registered.

**Probing from inside the network, without curl.** When the host has no
HTTP client, or the edge publishes no port to the host, run each probe with
the busybox `wget` inside a service container (`docker exec <container> wget
…`). Busybox `wget` exits 1 on any failure and reports the status only on
stderr, in two forms; take the last `HTTP/x.y NNN` token, and treat none as
no answer, never as a status:

```bash
code() {   # code <container> <url>: the HTTP status, or ERR when nothing answered
           # (ERR also when the probe container itself is missing)
  local c
  c="$(docker exec "$1" wget -S -T 10 -q -O /dev/null "$2" 2>&1 \
       | grep -oE 'HTTP/[0-9.]+ [0-9]{3}' | tail -1 | grep -oE '[0-9]{3}$')"
  printf '%s\n' "${c:-ERR}"
}
```

The two status-line forms, the redirect and error-body limits that follow
from them, and a Python driver with the same idiom live in
`tool-corpus/testing/in-network-e2e-harness.md` (§3 and §5).

**A failing assertion that uncovers a bug stays as it is.** Every assertion
states correct behavior; the suite carries no assertion of broken behavior.
When an assertion uncovers a confirmed bug:

- The assertion that uncovered it is the acceptance check for the fix, so it
  stays unchanged, and the suite stays red on it. To re-run it alone, select
  its section.
- Recording the bug, telling the owner, the fix and the re-run follow
  `protocols/test-first.md` (`test-first.known-bug`).

## 4. Portable vs blueprint

- **Portable (use as-is):** the PASS/FAIL counter harness, colored output, single
  aggregate exit code, and the `assert` wrapper with its section selector and
  `{section, check, pass, detail}` JSON record; the in-network `code()` helper
  (§3).
- **Project-specific (fill in):** the concrete URLs, ports, expected status
  codes, auth scheme, section names, and which protocol facts matter for the
  given service.

Portable skeleton (harness is complete; assertions are examples to replace):

```bash
#!/usr/bin/env bash
set -uo pipefail                       # NOT -e: we want every assertion to run
BASE="${SMOKE_BASE_URL:?set base url}${SMOKE_BASE_PATH:-}"  # origin + optional public prefix
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
unrouted_404()   { [ "$(curl -s -o /dev/null -w '%{http_code}' "$BASE${SMOKE_UNROUTED_PREFIX:-}/no-such-route-$RANDOM")" = 404 ]; }  # SPA origin: set the API prefix

assert tls  "tls binds"                         tls_binds
assert tls  "plaintext redirects to tls"        plain_redirects
assert app  "health endpoint serves"            health_ok
assert auth "protected route rejects anon"      auth_enforced
assert edge "closed port serves nothing at all" port_closed   # ANY HTTP reply FAILS
assert edge "an unrouted path is 404"           unrouted_404  # the route table governs

[ -n "$JSON" ] || printf '\n%d passed, %d failed\n' "$pass" "$fail"
[ "$fail" -eq 0 ]
```

## 5. Pitfalls and sharp edges

- **`set -e` short-circuits the suite.** With `-e` the first failing assertion
  aborts the run and you never see the rest. Use `set -uo pipefail` and let the
  `assert` wrapper own pass/fail.
- **Testing page content instead of protocol facts** is brittle; assert status
  codes, redirects, TLS negotiation, and auth enforcement.
- **A bug hidden by editing its assertion.** Loosening, inverting or deleting
  the assertion that uncovered a bug turns the suite green over a live defect
  and discards the fix's acceptance check; the assertion stays as it is (§3).
- **Asserting only the happy path for auth** proves nothing; assert that the
  unauthenticated request is *rejected*.
- **Reading a not-found as "the route is protected."** It is equally consistent
  with the route having disappeared from the edge configuration, and only a
  rejection tells the two apart.
- **Accepting an error status as proof that a surface is closed.** A 500 or 403
  from a supposedly-removed route is a *failing* assertion, not a passing one —
  see the negative assertion in §3.
- **A probe that changes state on a shared account.** A smoke suite runs
  after every deploy, so each check must be safe to repeat on the target.
  Never call a state-destroying flow (a password reset, an account lockout,
  a delete, a payment) against an account other people use. A verification
  probe made while building a smoke suite triggered a real password reset;
  it overwrote a shared test administrator's password and marked its
  credentials expired, and nobody could log in with it until the row was
  restored by hand. The finished suite left that flow out for this reason. Prove such a flow
  with a disposable identity
  (`tool-corpus/ops/disposable-test-identity-provisioner.md`), or prove only
  that its route exists (the rejection assertion in §3).
- **An artifact-identity expectation list goes stale in a migration.** A
  check that asserts which artifact version each unit runs fails a correct
  rollback, and it also fails a correct migration deploy when the change that
  moved a unit did not extend the list in the same change. One such run
  scored every check but one green, and the one FAIL was the script's list,
  not the deploy. Extend the list in the same change as the migration or the
  rollback, and treat a FAIL there as a claim about the script until you have
  read the artifact inside the running unit yourself. What shipped is
  `release-posture.artifact-identity` (`core/method/release-posture.md`);
  the list only restates it per unit.
- **Probing only the direct origin.** Behind a shared edge proxy the public
  path is the prefixed one; set the base path (§2). The same holds without a
  prefix: a suite that calls the backend directly never crosses the edge a
  browser crosses, and never sends the `Origin` header a browser sends, so a
  cross-origin defect every user sees leaves it green. Probe the browser's
  path through the edge with the page's own `Origin` and with an unlisted
  one, and expect the second to be refused; the with-and-without-`Origin`
  pair on every routed prefix is `skill-corpus/same-origin-web-edge.md`,
  step 7.
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
closed-surface assertion **failing** when the stub answers with an error status
instead of refusing the connection; selecting one section runs only that
section's checks and keeps the same aggregate exit behavior; the base path
prefixes every `$BASE` probe; and the unrouted-path assertion fails against a
stub that answers every path with 200.

- **How to run the tests:** `<the plant's test command for shell tooling>`

## 7. References & neighbours

- **Related tools:** `tool-corpus/ops/container-deploy-pipeline.md` (runs this as
  its post-deploy gate); `tool-corpus/ops/self-signed-tls-cert.md` (supplies the
  cert the TLS assertions check);
  `tool-corpus/ops/disposable-test-identity-provisioner.md` (mints the throwaway
  identities an auth-enforcement assertion authenticates with);
  `tool-corpus/testing/failure-signature-triage.md` (the same
  assert-the-mechanical-fact posture applied to a test run's failures);
  `tool-corpus/testing/in-network-e2e-harness.md` (end-to-end flows driven
  from inside the container network, with the same `wget` idiom);
  `tool-corpus/testing/live-contract-check-harness.md` (contract checks with
  RED and GREEN modes, where this suite only says whether the service
  serves).
- **Sources:** distilled from practice; BusyBox
  `networking/wget.c` (status-line output and error exit, behind `code()`).

## 8. Changelog

- 2026-07-16 — created by docs-librarian.
- 2026-08-06 — folded in three additions, each integrated into the
  section that owns it: the closed-surface negative assertion (§3, with its
  error-status pitfall in §5 and the `port_closed` example in §4's skeleton),
  the section-selectable + JSON-emitting harness (§2's interface and the
  skeleton's `assert` wrapper), and the self-evidencing-instrument pitfall with
  its prove-it-can-go-RED meta-test (§5–§6), by docs-librarian.
- 2026-09-22 — folded in the auth-sweep's second reading: the same rejection
  assertion is also a route-existence proof (§3), with the read-a-not-found-as-
  protected pitfall it closes (§5), by docs-librarian.
- 2026-09-30 — replaced the assert-today's-broken-behavior idiom with the
  owner's known-bug rule:
  the assertion that uncovered a bug stays unchanged as the fix's acceptance
  check, the bug is recorded and the user told, and the same assertion re-runs
  after the fix (§3, §4 skeleton, §5, §6), by implementer.
- 2026-10-05 — folded in idioms from practice, each in the
  section that owns it: the base-path parameter for a service behind a
  shared edge (§2, and the skeleton's `BASE`); the unrouted-path 404 control,
  the discovery-registry assertion and in-network probing with busybox `wget`
  in both of its status-line forms (§3, with `unrouted_404` in the skeleton);
  the state-destroying-probe, stale artifact-identity list and origin-only
  pitfalls (§5); by tool-smith.
- 2026-10-05 (review fix pass): the unrouted-path probe moved under the API
  prefix on a single-page-app origin (`SMOKE_UNROUTED_PREFIX`), the base-path
  format and the in-network preconditions are stated, the password-reset
  pitfall says it was a verification probe, and the busybox `wget` details
  now live on the in-network harness page with a pointer here; by tool-smith.
- 2026-10-05: the origin-only pitfall now covers a suite that skips the edge
  without a prefix, and the `Origin` probe pair (§5); by docs-librarian.
