# Suggested skill: same-origin-web-edge

> Optional procedure. It moves a browser client and every API call it makes
> onto one origin, served by the reverse-proxy edge that already serves the
> page, and then proves the move from the browser's side rather than from the
> server's. It composes `protocols/verify.md` (when a gate counts as green, and
> why an absent leg is never green), `protocols/test-first.md` (each gate goes
> red before the change it guards), `skill-corpus/mutation-verify.md` (planting
> the defect a gate claims to catch), `core/method/incident-posture.md`
> (locating a client-reported failure from the access logs before changing the
> server), and the library pages that own the substrate
> facts: `library-corpus/container/nginx.md` for proxy, fallback, WebSocket,
> timeout, template and cache-header mechanics,
> `library-corpus/language/angular.md` and `library-corpus/language/flutter.md`
> for the client side. Those pages keep their one home and are not restated
> here. Parameterized by `<PAGE_ORIGIN>` (the scheme, host and port the page is
> served from), `<DIRECT_API_BASE>` (the API edge reached without the page's
> proxy), `<EDGE_CONFIG>` (the proxy configuration that serves the page),
> `<SERVED_BUNDLE>` (the built client as the running edge serves it),
> `<PROBE_ACCOUNT>` (a synthetic account, never a real user) and, for a shared
> edge, `<PUBLIC_PREFIX>`.

## When to apply

- A browser user reports a failure that leaves no trace on the server, or one
  that happens in one browser and not in another.
- A web client calls its API on a second origin: another host, or the same
  host on another port. A self-signed certificate on either origin makes this
  urgent (step 1).
- The client bundle carries an absolute API or WebSocket URL, and a host,
  domain or address change turned every call into a "CORS error".
- Clients on a network with no outbound internet get a blank page.
- An application is being published under a path prefix of a reverse proxy it
  shares with other tenants (step 8).

## The procedure

### 1. Diagnose before changing anything: count the origins

The move this replaces is widening CORS, reissuing the certificate, or blaming
credentials because the user saw a login error.

- Diagnose first, by `incident-posture.evidence` (`core/method/incident-posture.md`
  §3): read each edge's access log for the failing client. In this setup the
  telling line is a browser that loaded the page from the page origin and made
  no API call to the API edge; the client-side causes to check next are the
  ones this procedure covers (trust scope per origin, mixed content, a cached
  bundle).
- Count the distinct origins the page uses. Browsers scope a user's
  certificate exception differently. Firefox stores an exception per host and
  port (the documented `cert_override.txt` format keys each entry as
  `host:port`). Chromium keys its exception decision by host alone (its
  `SSLHostStateDelegate::AllowCert` takes a host and no port), so one
  acceptance covers every port on that host. Observed in practice: a
  background request (XHR or fetch) to an origin the user has not yet trusted
  shows no warning page in either engine; it is aborted with no HTTP status and
  leaves no line in the server log. Browser documentation describes the warning
  page for page navigations and is silent on this case. So a page and an API on
  two ports under one self-signed certificate work in one engine and fail
  silently in the other, with green CORS and a valid certificate.
- Do not fix it by reissuing or widening the certificate (it is already valid
  for both origins; the user's trust decision is what does not reach the
  second one), by a wildcard CORS rule, or by falling back to plain HTTP. Plain
  HTTP loses the secure context that browser crypto and storage APIs need
  (`window.crypto.subtle` exists only in a secure context, see
  `library-corpus/language/flutter.md`), and an HTTPS page that calls an HTTP
  API is blocked as mixed content (MDN lists `fetch()` and `XMLHttpRequest`
  among the requests a browser blocks rather than upgrades).
- A client whose error handler renders every fault as one message ("wrong
  credentials") turns a transport abort into a password problem. Record that as
  its own diagnosability defect and its own increment; it is not the cause.

Gate: the cause is named from evidence gathered in the failing browser, and the
origin count is written down.

### 2. Inventory every API prefix the bundle can emit

The move this replaces is adding proxy locations for the prefixes someone
remembers.

- Read the prefixes from two places: the client source (every base-URL use,
  every service or repository client, the token-refresh call, upload and
  download paths, WebSocket and SockJS endpoints, rarely used admin calls) and
  `<SERVED_BUNDLE>` itself, searched for absolute URLs and path prefixes. The
  built artifact is the evidence; a source read can miss a value injected at
  build time.
- Write the list once, in `<EDGE_CONFIG>`. The gates in step 9 read the
  proxied prefixes back from that file instead of keeping a second copy.
- Probe each prefix at `<DIRECT_API_BASE>` and confirm the backend router
  resolves it. A client path the router does not resolve is a clean 404 today;
  behind a page fallback it would become `200 text/html` and fail far from its
  cause. Fix such a routing defect before or together with the move, never
  after.
- When the move is forced by a retired host, the API base is one reference to
  it among many. Search every channel that can carry the old name: the served
  configuration of each profile, links the application writes into mail
  (account recovery, attachments, images), the compiled client bundle, the
  proxy configuration and its certificate paths, and dashboard links. A value
  compiled into a bundle is fixed only by a rebuild (step 5). The canonical
  external address that replaces the old one is an owner decision. Do not
  probe whatever the old name or a look-alike now resolves to: that address
  may belong to someone else.

Gate: every prefix in the list resolves at `<DIRECT_API_BASE>`, and every
prefix the bundle contains is in the list.

### 3. One proxy location per prefix, forwarding the original request URI

The move this replaces is a single happy-path call through the new location,
taken as proof that forwarding works.

- On the edge that serves the page, add one location per prefix. It forwards to
  the in-network API (a service name on the internal network), not back out
  through a public name. It forwards the original request URI unchanged:
  every path segment after the prefix and the whole query string. On nginx a
  variable upstream combined with a URI part on `proxy_pass` sends that URI
  verbatim and drops the client's sub-path; the rule and its fix are on
  `library-corpus/container/nginx.md`. The signature is a backend 404 (or a
  401 on a path that is public when called directly) through the page origin,
  where the same call made directly succeeds. Observed in practice: this
  defect recurred on more than one edge of the same deployment until a
  differential probe (step 9, G1) existed.
- Bound a hanging upstream with connect, send and read timeouts on every proxy
  location. Observed in practice on nginx: against an unroutable upstream, a
  location with a short connect timeout answered 504 within that timeout, and
  the same file without the timeout lines was still hanging long after it. A
  working starting point: connect within a few seconds, send and read within
  tens of seconds.
  Long-lived connections (WebSocket, server-sent events) get the upgrade
  headers and their own longer read timeout (`library-corpus/container/nginx.md`,
  WebSocket and Timeouts).
- Prefer an exact alternation of the inventoried prefixes to one broad pattern.
  When a location is wider than the backend router (it forwards a whole
  namespace the router serves only in part), record that, and assert that the
  router answers 404 for the rest; the router is then the guard.

Gate: a static read of `<EDGE_CONFIG>` finds that every proxy directive
forwards the original URI and appends nothing after it. The reader fails
loudly when it finds no proxy location at all, because an empty set would pass
every check. The static read is necessary and not sufficient; G1 proves the
forwarding.

### 4. End every API-shaped miss in a loud 404

The move this replaces is a page fallback that answers every unknown path with
the application shell.

- When the client has no router that needs deep links, remove the fallback:
  every listener ends with a not-found answer, so a mistyped or unproxied API
  path is a 404. When deep links are needed, keep the fallback in the page's own
  location only and end every API-shaped prefix with a terminal 404 (the idiom
  is on `library-corpus/container/nginx.md`). A fallback that answers an
  unproxied API path with `200 text/html` is a fail-open success: the client
  fails later on a JSON decode, the user sees a generic error, and any check
  that asserts only a 2xx passes.
- A structural removal beats a gate over a fail-open surface, but keep a
  regression leg (G2), because the fallback is a one-line change away from
  coming back.

Gate: G2.

### 5. Make the client's API base relative, or supply it at run time

The move this replaces is an absolute API host baked into the bundle at build
time.

- Point the client at a relative base (`/api`, or an empty base so calls
  resolve to `/<prefix>/...`), and make the WebSocket endpoint path-only, with
  the scheme derived from the page, so `ws` or `wss` follows the page and no
  host is baked in. The framework idiom is on
  `library-corpus/language/angular.md`.
- An empty base must be explicitly empty, never absent. Observed in practice:
  a dotenv-style loader returned null for a missing key, and string
  concatenation produced the literal path `null/<prefix>/...`. With step 4 in
  place, such a bug is a loud 404 instead of a silent shell.
- When a deployment really needs an absolute value, supply it without baking it:
  either a runtime `config.json` that the container entrypoint writes (or a
  mount provides) and the client fetches before it boots, refusing to boot
  without it, or a build argument whose default is the relative base. A
  writable web root is the trap on a non-root or read-only image; the mounts it
  needs are on `library-corpus/container/nginx.md`.
- A base URL baked at build time means the fix, and its revert, each cost a
  rebuild of the client image, not a restart. Plan the rollback with that in
  mind.

Gate: `<SERVED_BUNDLE>`, read from the running container and not from the
build directory, contains no absolute API host and no retired host, and its
API and WebSocket bases equal the relative defaults.

### 6. Serve every boot-time asset from the page origin

The move this replaces is trusting the framework's default asset hosts.

- Rendering engines, WebAssembly modules, default fonts and fallback fonts that
  a framework loads from a public CDN by default turn a network with no
  outbound internet into a blank page. Serve them from the page origin. The
  framework-specific facts (which files, which flags, which fetch no flag turns
  off) are on the library pages, for example
  `library-corpus/language/flutter.md`, Web.
- Remove each external fetch at its cause, for example by bundling the font the
  engine would otherwise download. Do not grant a named external origin an
  exception in the gate: an exception written for one host is inherited by the
  next one.
- When a content-dependent path can still reach a public host (a fallback font
  fetched only for characters no bundled font covers), name it, record what
  would trigger it and who owns it, and do not claim the client is provably
  offline.

Gate: G3, run with every public host blocked.

### 7. Keep server-side CORS and transport rules right, not wider

The move this replaces is deleting the CORS configuration because the client
is now same-origin.

- Browsers send an `Origin` header on same-origin requests whose method is not
  `GET` or `HEAD` (Fetch standard, the `Origin` header section). A backend CORS
  layer that rejects an unrecognised `Origin` therefore still sees proxied
  same-origin `POST`, `PUT` and `DELETE` calls. Keep `<PAGE_ORIGIN>` in every
  allowlist. Where the allowlist lives in more than one place (the edge and each
  service), gate that the copies agree, and probe each routed prefix with and
  without `Origin`: the two answers must match. Never fix a mismatch by
  widening.
- A check asserting that the page origin receives a cross-origin
  `Access-Control-Allow-Origin` becomes vacuous after the move. Re-point it or
  retire it; a check that can no longer fail is a green lie
  (`protocols/verify.md`).
- If plain HTTP can reach the HTTPS port, answer it with a method-preserving
  permanent redirect (308: method and body are kept) to the deployment's own
  configured identity, never to the client-supplied `Host`. Reflecting `Host`
  on the login front door is an open redirect. Probe it with a hostile `Host`,
  a hostile `Host` with a port, a look-alike host, and an HTTP/1.0 request
  with no `Host` at all, and confirm a plain-HTTP `POST` keeps its method. An
  internal health-check listener stays free of redirects.
- Keep the old direct API edge if non-browser callers use it (native clients,
  server-to-server probes). Record that a native client has no certificate
  warning page at all and needs its own trust decision; this procedure does not
  fix it.

Gate: the with-and-without-`Origin` pair matches on every routed prefix, and
every redirect probe lands on the configured identity with its method intact.

### 8. Publishing under a path prefix on a shared edge (when it applies)

The move this replaces is editing a proxy that other tenants depend on and
restarting it.

- The shared proxy has an owner and, usually, written instructions on that
  host. Read them before any change, and touch only this application's own
  route file. Another tenant's route that is broken is observed state to
  report, not to fix. Keep this application's route file in its own
  repository, so the route can be rebuilt when the shared proxy loses it to
  another tenant's edit.
- The route strips `<PUBLIC_PREFIX>` before forwarding, forwards the WebSocket
  upgrade headers, raises the read timeout for long-lived connections and
  sets the request body limit the application needs. A request for the bare
  prefix without its trailing slash redirects to the prefix with the slash.
  Record whether the proxy verifies the application's upstream certificate;
  turning verification off is a decision, not a default.
- Build the client prefix-agnostic: a relative base href (or one built for the
  prefix; rewriting HTML in flight is unreliable, see
  `library-corpus/container/nginx.md`) and relative API and WebSocket URLs, so
  the same bundle works directly and under the prefix.
- Test the new configuration in a throwaway container first (on nginx,
  `nginx -t` against the candidate file), then apply it with a graceful reload,
  never a restart. On a reload nginx starts new workers with the new
  configuration and lets the old ones finish serving their current clients
  (nginx documentation, "Controlling nginx"); if the new configuration fails to
  load, the master keeps the old one. A restart drops every tenant's
  connections.
- When the public origin changes (step 2 lists where the old one hides), one
  value that serves two uses (the backend's allowed CORS origin and the base
  of links the application writes into mail, say) breaks one
  of them whichever way it is set, so split it into two settings before the
  move, and set the allowed origin to the public one.
- A smoke suite that probes only the direct origin cannot see the prefixed
  public path. Give it a base-path parameter
  (`tool-corpus/testing/http-smoke-suite.md`).

Gate: through the public prefixed URL, the page and its assets answer 200, the
health endpoint answers healthy, a protected route answers 401, the WebSocket
upgrade answers 101, and any SockJS info endpoint answers 200, each served by
this application.

### 9. The gate set

Write the gates first and watch each one fail against the current deployment
(`protocols/test-first.md`). Then prove each bites by planting the defect it
claims to catch (`skill-corpus/mutation-verify.md`): put a literal URI suffix
back on one proxy location and G1 must go red; restore the shell fallback and
G2 must go red.

How the probes run:

- An HTTP client from the language's standard library, so the gate runs on an
  operator machine and on a deploy host that has no curl and no package
  manager access.
- Decide reachability first, by a TCP connect to each edge before any probe.
  An edge that does not accept the connection makes its live legs ABSENT,
  reported with the reason. Once an edge is reachable, any transport failure
  on a probe (DNS, refused, TLS) is red, never a skip. The gate exits 0 only
  when every leg ran and passed, 1 on any failure, and 2 when nothing failed
  but a leg is ABSENT, so red outranks absent. A
  repo-only mode runs the offline legs (the static reads) and reports every live
  leg ABSENT by construction, so it is safe in CI and is never mistaken for the
  live run.
- The routing legs may turn certificate verification off at the transport,
  because they assert routing and not trust. Browser trust belongs to the
  browser legs, which never bypass it. Keep the two in separate gates.
- Read the bare media type: the `Content-Type` value lowercased, with
  parameters such as the charset dropped. A missing header is a distinct value,
  never an empty string that could match.

The legs:

- **G1, differential probe.** Send the same request through `<PAGE_ORIGIN>` and
  to `<DIRECT_API_BASE>`, with identical headers on both legs, `Origin`
  included, and a token obtained through each edge where the path needs one.
  Use a deep sub-path (at least two segments after the prefix) with a query
  string that carries an encoded slash, for `GET` and for `POST`, on every
  proxied prefix. The verdict is equivalence, not a fixed status: the same status
  and the same media type. A fixed expected status would couple the leg to
  endpoint inventory and seed data, and it would go red for reasons that are not
  this failure. Name the loudest case on its own: HTML through the page origin
  where the direct answer is not HTML. Check the precondition first: each
  probe's prefix is one `<EDGE_CONFIG>` proxies, otherwise the probe measures
  the static file server and the leg is an error, not a pass.
- **G2, a miss is a 404 and not the shell.** Through `<PAGE_ORIGIN>`, a few
  API-shaped paths that no location proxies (an unknown prefix, a near-miss of
  a real prefix, a path ending in `.json`) answer 404, and the body is not the
  application shell. Identify the shell by its loader markers (the bootstrap
  script names the built `index.html` always carries), not by `text/html`,
  because the server's own 404 page is HTML too. In the same leg, one proxied
  path answers the backend's status with a JSON media type, so a proxy that
  answers 404 to everything cannot pass.
- **G3, no second origin.** A real browser with default certificate
  validation, trust granted for `<PAGE_ORIGIN>` only, and every other host
  blocked at the network. Drive page load, login with `<PROBE_ACCOUNT>` and at
  least one authenticated call, and collect the origin of every request. The set
  is exactly `{ <PAGE_ORIGIN> }`; any other origin fails, and no request may end
  aborted without an HTTP status. Run it once per browser engine the users have,
  at least one Chromium-family and one Firefox-family engine, because their
  trust scopes differ (step 1). When the client stores a session token, read it
  right after login and again a few seconds later: both reads find it.
- **G4, convergence for fresh and returning visitors.** First run G3 on a fresh
  profile, or with the site data for `<PAGE_ORIGIN>` cleared, so the first
  measurement is of the new bundle and not of a cached one. Then prove that a
  browser profile that loaded the previous bundle converges on the new one:
  after the deploy it executes the new bundle, whose served main script carries
  none of the retired absolute hosts, and G3 holds for it. The browser
  mechanics behind this leg are documented: a navigation checks the service
  worker script for a byte change, by default bypassing the HTTP cache for that
  script, and an updated worker waits until no page it controls is open, so one
  reload is not enough (web.dev, "The service worker lifecycle"). The
  response-header policy that makes `index.html` revalidate and hashed assets
  long-lived is on the web server's page (`library-corpus/container/nginx.md`);
  the framework's service-worker files are on its page. Observed in practice:
  Chromium refused to register a service worker on an origin with an untrusted
  self-signed certificate, so the stale-bundle risk sat with returning users of
  the other engines; one engine did not clear service-worker state on its own
  while a private window worked. A written "clear site data, then reload" step
  is an acceptable interim control; a remembered one is no control at all.
- **G5, static edge read.** Every proxy directive forwards the original URI
  (step 3), every proxy location carries timeouts, and the last directive on
  every listener is a not-found answer or a page-only fallback (step 4).
- **G6, public prefix smoke** when step 8 applies.

G1, G2 and G5 need no browser. G3 and G4 need a real browser, because the
defect they close leaves no trace a server-side probe can read.

A minimal stdlib sketch of G1, to adapt (cases, token, TLS context):

```python
import sys, urllib.error, urllib.request

def call(method, url, headers, body=None, ctx=None):
    req = urllib.request.Request(url, data=body, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=20, context=ctx) as r:
            st, ct = r.status, r.headers.get("Content-Type")
    except urllib.error.HTTPError as e:
        st, ct = e.code, e.headers.get("Content-Type")
    # any other exception (DNS, refused, TLS) propagates: transport failure is red
    return st, (ct or "<absent>").split(";")[0].strip().lower()

def differential(page_origin, direct_base, cases, ctx=None):
    """cases: (label, method, path_with_query, headers, body)"""
    problems = []
    for label, method, path, headers, body in cases:
        h = {"Origin": page_origin, **headers}  # identical headers on both legs
        via = call(method, page_origin + path, h, body, ctx)
        direct = call(method, direct_base + path, h, body, ctx)
        print(f"{label}: {method} {path} via={via} direct={direct}")
        if via[1] == "text/html" and direct[1] != "text/html":
            problems.append(f"{label}: HTML via the page origin, {direct[1]} direct")
        elif via != direct:
            problems.append(f"{label}: via {via} != direct {direct}")
    return problems

if __name__ == "__main__":
    q = "probe=1&deep=a%2Fb"
    cases = [("deep-get", "GET", f"/svc/items/42/detail?{q}", {}, None),
             ("deep-post", "POST", f"/svc/session/login?{q}",
              {"Content-Type": "application/json"}, b"{}")]
    bad = differential(sys.argv[1], sys.argv[2], cases)
    print("FAIL" if bad else "PASS", *bad, sep="\n  ")
    sys.exit(1 if bad else 0)
```

Against a fixture edge that forwards only the bare prefix, both cases report
`via (404, 'application/json') != direct (200, 'application/json')`; against
one that forwards the full URI, both agree and the sketch passes. The sketch
has no reachability pre-check: an unreachable edge raises and ends it with
exit 1, not the ABSENT exit 2. Add the TCP-connect check before you rely on
that distinction.

### 10. Record the decision and every gap in the open

The move this replaces is calling the deploy green because the server-side
checks pass.

- The decision record (`skills/adr-writer/SKILL.md`) states the one origin,
  what stays (the direct edge for non-browser callers, the CORS allowlists),
  the rebuild cost in both directions, and each residual with its owner.
- Where a contract's text asserts more than its gate leg does, record the leg
  as absent with an owner. An absent leg is never coverage, and the deploy is
  not called green while a leg the decision requires is ABSENT
  (`protocols/verify.md`).

## Reference files

- `protocols/verify.md` (when a gate is trusted, what an absent leg means, and
  the planted-violation clause)
- `protocols/test-first.md` (each gate red before the change it guards)
- `skill-corpus/mutation-verify.md` (planting the dropped sub-path and the
  restored fallback to prove G1 and G2 bite)
- `core/method/incident-posture.md` §3, `incident-posture.evidence` (locate a
  client-reported failure from each edge's access log before changing the
  server; an unreproduced cause is a hypothesis; step 1)
- `skills/adr-writer/SKILL.md` (the decision record of step 10)
- `library-corpus/container/nginx.md` (`proxy_pass` with variables, the SPA
  fallback and terminal 404, WebSocket headers, timeouts, envsubst templates,
  read-only and non-root web roots, base href, cache headers)
- `library-corpus/language/angular.md` (relative API base, path-only
  WebSocket endpoint, base href, stale bundle)
- `library-corpus/language/flutter.md` (engine and font CDN dependencies,
  secure-context APIs, service-worker update behaviour)
- `tool-corpus/ops/self-signed-tls-cert.md` (the certificate an IP-only edge
  serves)
- `tool-corpus/testing/http-smoke-suite.md` (the smoke harness G6 extends with a
  base path)
- `agent-corpus/client-frontend-specialist.md` (the role that owns the
  client-to-edge contract)
- `agents/06-reliability.md` (edge configuration and cache-header policy) and
  `agents/04-tester.md` (the gate legs)
