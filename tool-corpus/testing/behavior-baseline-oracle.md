# Tool: behavior-baseline-oracle

> Project-agnostic capability notes, kept in the seed's tool corpus
> (`tool-corpus/README.md`). A portable tool: the script below runs as-is
> against any HTTP surface, and a plant fills in only the surface list.

## 0. Identity

- **Category:** testing
- **Name:** behavior-baseline-oracle
- **Language / runtime:** Python 3.7 or later (the self-test's
  `ThreadingHTTPServer` arrived in 3.7), **stdlib only** (`urllib`, `json`,
  `http.server` for the self-test)
- **Stability:** **portable**. The capture, normalization, golden record and
  diff are complete; the plant supplies a surface list, and may swap the HTTP
  transport for its own (see §3, "Transport").

## 1. What it does

It is the "how" behind the first step of
`skill-corpus/framework-version-migration.md`: characterize the system before
the change, then prove the change kept its behavior. The method it
implements is `protocols/verify-disagreement.md`'s: characterize first,
capture read-only, and let through only an enumerated list of intended
deltas. The plan keeps that list; `check --allow` reads it (§3).

It sends one representative request to each user-facing surface of a running
system. Each response is normalized so that values that change on every run
(tokens, timestamps, live magnitudes) do not count as drift. It writes one
golden JSON per surface and a manifest. Later, `check` sends the same requests
to the changed system and diffs each normalized response and status against
the golden record. A difference on a stable field is a behavior change the
work introduced, reported with the JSON path where it sits.

Use it when a change must preserve behavior: a framework major-line upgrade,
a runtime swap, a refactor, a rebuild of a lost system. It asserts sameness
across a change. It does not assert that one flow is correct; the
functional tests do that.

## 2. Interface & invocation

```sh
baseline.py capture --spec surfaces.json --dir baseline/                 # first capture
baseline.py capture --spec surfaces.json --dir baseline/ --rebaseline "<why>"
baseline.py check   --spec surfaces.json --dir baseline/                 # the gate
baseline.py check   --spec surfaces.json --dir baseline/ --allow deltas.json
baseline.py --self-test
```

- **Inputs:** a surface list (`--spec`) and the golden-record directory
  (`--dir`). The spec is JSON:

  ```json
  {"base_url": "http://<edge-host>:<port>",
   "surfaces": [
     {"name": "login", "method": "POST", "path": "/auth/login",
      "body": {"user": "<synthetic user>", "password": "${SEED_PASSWORD}"},
      "bind": {"API_TOKEN": "token"}},
     {"name": "catalogue", "path": "/catalogue", "expect_status": 200,
      "headers": {"Authorization": "Bearer ${API_TOKEN}"},
      "volatile_keys": ["requestId"], "note": "seeded catalogue, content is the oracle"},
     {"name": "field-reading", "path": "/items/${SEEDED_ITEM_ID}/reading",
      "headers": {"Authorization": "Bearer ${API_TOKEN}"}, "mode": "shape"}]}
  ```

  `method` defaults to `GET` and `mode` to `stable`. A `${VAR}` anywhere in
  `base_url`, `path`, `headers` or `body` is resolved at probe time: first
  from a value an earlier surface bound in this run, then from the
  environment. A name found in neither stops the run.
- **Authenticated surfaces and run-time values:** a surface's optional
  `"bind": {"VAR": "field"}` copies a field of its raw answer (before
  normalization; a dotted path such as `data.token` reaches into objects) into
  `VAR` for the surfaces after it. That is how a login's token reaches every
  later request, and how an id read at run time reaches a later `path`. A
  bound field that is absent or `null` stops the run (exit `2`). Surfaces run
  in spec order, so a binding surface comes before its users. A value that no
  surface returns (an id the seed put in a database, say) is exported into
  the environment before the run. Either way the golden keeps the template.
- **Request bodies are JSON only.** `body` is sent with `json.dumps`; a form
  or raw body needs a custom transport (§3, "Transport").
- **`note`** (optional) is copied into the surface's golden file for the
  next reader.
- **Outputs:** `<dir>/<name>.json` per surface (method, the path and the
  request body **templates**, status, mode, note, normalized response) and
  `<dir>/manifest.json` (surface table, the transport that captured, and the
  list of re-baseline reasons). `check` prints `MATCH`, one `ALLOWED` line per
  difference the allowlist covers, and one `DRIFT` line per other difference.
  The tool owns `--dir`: a re-baseline replaces the whole directory, so keep
  notes and a README elsewhere. A missing parent of `--dir` is created.
- **Exit codes:** `0` written or MATCH; `1` drift, a stale allowance, or a
  capture where a surface missed its `expect_status`; `2` usage error, an
  unreadable spec or allowlist, an unresolved `${VAR}` or binding, a capture
  over an existing record without `--rebaseline`, a check through a transport
  other than the one that captured, or a probe that got no HTTP answer at
  all.
- **Preconditions:** the system is up, seeded with deterministic synthetic
  data, and **already verified working** (§5, first pitfall).

## 3. Approach / algorithm

**Two normalization modes, chosen per surface.** The mode is an assertion
strength, not a convenience:

- **`stable`** keeps the content verbatim. It masks only values that change
  on every call: a JWT-shaped string (the three-part signed form or the
  five-part encrypted form) or a value under a token key becomes `<JWT>`, an
  ISO-8601 timestamp becomes `<TIMESTAMP>`, and the whole value of each key
  the surface lists in `volatile_keys` becomes `<VOLATILE>`, an object or a
  list included (a request id, a per-run id, a per-run metadata block). Use it for deterministic reads of seeded data, where the
  content is the oracle: names, prices, claims.
- **`shape`** replaces each leaf with its type (`<str>`, `<int>`,
  `<float>`, `<bool>`, `<null>`) and each list with the shape of its first
  element. Use it for surfaces whose content varies legitimately (a live
  reading, a profile the run itself mutates, a list that grows). It catches a
  dropped field, a changed type, a list turned into an object. It does not pin
  magnitudes.

A non-JSON body is stored as `{"_raw": "<text>"}`, so it is compared verbatim
in `stable` mode and as `<str>` in `shape` mode. The default transport does
not follow a redirect: a 3xx is recorded as its status and
`{"_location": "<Location header>"}`, so a moved route or a new login
redirect is drift, not a silent hop to whatever answers at the target.

**The golden record is all-or-nothing.** `capture` writes into a temporary
directory and swaps it in only when every surface answered, so a failed
capture never leaves a mix of old and new goldens. A probe with no HTTP
answer (refused, timeout, DNS, a reply that is not HTTP) raises and exits
`2`: an outage is an environment fault, never a value to record. A status that misses a surface's
`expect_status` exits `1` and writes nothing, because a golden record of
broken behavior turns the gate into a guard for the bug. A surface with a
4xx or 5xx status and no `expect_status` is written, with a `WARNING` line,
because the tool cannot tell an intended error answer from a typo in a path.

**Re-baselining is explicit.** `capture` refuses to overwrite an existing
record unless `--rebaseline "<why>"` is given, and the reason is appended to
the manifest's `rebaselines` list. An intended behavior change therefore
leaves a reason in the record. A hand-edited fixture leaves none.

**`check` diffs in both directions.** A stored surface that is no longer
probed is drift, as is a probed surface with no golden, a changed request
(method, path template or body template), a changed mode, a changed status,
and each differing JSON path (the first 20 per surface). A list that changes
length reports each index added or removed. Checking only the surfaces
present today would let a removed endpoint pass, and checking only the
answers would let a spec edit re-point a surface at another route.

**Intended deltas pass only by name.** `check --allow deltas.json` reads a
list of `{"surface", "path", "why"}` entries, the plan's intended-delta list
in machine form. A difference whose surface matches and whose JSON path
equals the entry's path, or lies under it, prints as `ALLOWED <why>` and does
not fail. Every other difference still fails, and so does an entry that
matched nothing (a stale allowance). `path` may also name `status`, `mode`,
`request` or `surface`. The golden stays the pre-change record while the allowlist is
in force.

**Secrets stay off disk.** The golden keeps the request template
(`"${SEED_PASSWORD}"`), never the expanded value, and tokens in responses are
masked. Use synthetic accounts and synthetic data only, so no personal data
reaches the record either.

**Transport.** The default probe is `urllib` from wherever the script runs.
When the surfaces are reachable only from inside a container network, call
`main(argv, probe=fn, transport="<name>")` with a function of the signature
`probe(method, url, headers, body_bytes) -> (status, text)` that raises
`ProbeError` on no answer. `tool-corpus/testing/in-network-e2e-harness.md`
has such a function, `Harness.probe`; the wrapper in §4 maps its
`HarnessError` to `ProbeError`, so an outage still exits `2`. That transport
is not interchangeable with `urllib`: it sends only GET and POST, and its
`wget` follows redirects and keeps no body of a non-2xx answer (that page
holds the details). The manifest records the transport name, and `check`
refuses (exit `2`) a golden that another transport captured.

## 4. Portable vs blueprint

- **Portable (use as-is):** the script below: both modes, the all-or-nothing
  write, the `--rebaseline` record, the two-way diff with JSON paths, the
  exit codes, the self-test.
- **Project-specific (fill in):** the surface list; which mode each surface
  gets; `volatile_keys`; `expect_status`; `bind` for a login token or a
  run-time id; the synthetic seed the system runs on; the intended-delta
  allowlist of a migration; a transport function when the edge is not
  reachable from the runner.

```python
#!/usr/bin/env python3
"""behavior-baseline-oracle: capture a golden record of user-facing behavior,
then prove a later build still matches it.

  baseline.py capture --spec surfaces.json --dir baseline/ [--rebaseline WHY]
  baseline.py check   --spec surfaces.json --dir baseline/ [--allow deltas.json]
  baseline.py --self-test

Exit: 0 written / MATCH; 1 drift (check), a stale allowance, or a surface that
failed its expected status (capture); 2 usage, unreadable spec, a transport
other than the one that captured, or a probe that got no HTTP answer.
Python 3.7 or later, stdlib only. Request values written as "${VAR}" come from
an earlier surface's "bind" or from the environment, at probe time, and are
never written to disk: the golden keeps the template.
"""
import http.client, json, os, pathlib, re, shutil, sys, tempfile
import urllib.error, urllib.request

JWT_RE = re.compile(r"^[A-Za-z0-9_-]{10,}(\.[A-Za-z0-9_-]{10,}){2}$"     # JWS: 3 parts
                    r"|^[A-Za-z0-9_-]{10,}(\.[A-Za-z0-9_-]*){4}$")       # JWE: 5 parts
ISO_RE = re.compile(r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}")
TOKEN_KEYS = {"token", "jwt", "accesstoken", "refreshtoken", "access_token",
              "refresh_token", "id_token"}
VAR_RE = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")
REQUEST_FIELDS = ("method", "path", "request_body")


class ProbeError(Exception):
    """No HTTP answer at all: an environment fault, never a golden value."""


def expand(value, bound):
    """Resolve ${VAR}: a value bound earlier in this run first, then the
    environment. A name found in neither stops the run."""
    if isinstance(value, str):
        def sub(m):
            name = m.group(1)
            if name in bound:
                return bound[name]
            if name not in os.environ:
                raise ProbeError(f"{name} is neither bound by an earlier surface "
                                 "nor set in the environment")
            return os.environ[name]
        return VAR_RE.sub(sub, value)
    if isinstance(value, dict):
        return {k: expand(v, bound) for k, v in value.items()}
    if isinstance(value, list):
        return [expand(v, bound) for v in value]
    return value


def dig(obj, dotted):
    for k in dotted.split("."):
        obj = obj.get(k) if isinstance(obj, dict) else None
    return obj


def normalize_stable(obj, volatile=frozenset(), key=None):
    """Keep content verbatim; mask tokens, timestamps and declared volatile keys."""
    if key is not None and key in volatile:
        return "<VOLATILE>"                  # whole value, object or list included
    if isinstance(obj, dict):
        return {k: normalize_stable(v, volatile, k) for k, v in obj.items()}
    if isinstance(obj, list):
        return [normalize_stable(v, volatile) for v in obj]
    if isinstance(obj, str):
        if (key or "").lower() in TOKEN_KEYS or JWT_RE.match(obj):
            return "<JWT>"
        if ISO_RE.match(obj):
            return "<TIMESTAMP>"
    return obj


def normalize_shape(obj):
    """Keep structure only: each leaf becomes its type, a list its first element."""
    if isinstance(obj, dict):
        return {k: normalize_shape(v) for k, v in sorted(obj.items())}
    if isinstance(obj, list):
        return [normalize_shape(obj[0])] if obj else []
    if isinstance(obj, bool):
        return "<bool>"
    if isinstance(obj, int):
        return "<int>"
    if isinstance(obj, float):
        return "<float>"
    if obj is None:
        return "<null>"
    return "<str>"


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None                          # a 3xx is a value, not a hop


_OPENER = urllib.request.build_opener(_NoRedirect)


def http_probe(method, url, headers, body):
    """Default transport. Returns (status, text); raises ProbeError on no answer.
    A redirect is not followed: it is recorded as its status and Location."""
    req = urllib.request.Request(url, data=body, method=method, headers=headers)
    try:
        with _OPENER.open(req, timeout=20) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:          # an HTTP answer: a real value
        if 300 <= e.code < 400:
            return e.code, json.dumps({"_location": e.headers.get("Location")})
        return e.code, e.read().decode("utf-8", "replace")
    except (urllib.error.URLError, OSError, http.client.HTTPException) as e:
        raise ProbeError(f"{method} {url}: no HTTP answer ({e!r})") from None


def load_spec(path):
    spec = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    names = [s["name"] for s in spec["surfaces"]]
    if not names or len(names) != len(set(names)):
        raise ValueError("spec needs at least one surface and unique names")
    for s in spec["surfaces"]:
        if s.get("mode", "stable") not in ("stable", "shape"):
            raise ValueError(f"{s['name']}: mode must be stable or shape")
    return spec


def capture(spec, probe=http_probe):
    out, bound = {}, {}
    for s in spec["surfaces"]:
        method = s.get("method", "GET")
        url = expand(spec["base_url"], bound) + expand(s["path"], bound)
        headers = expand(s.get("headers", {}), bound)
        body = None
        if s.get("body") is not None:
            body = json.dumps(expand(s["body"], bound)).encode()
            headers.setdefault("Content-Type", "application/json")
        status, text = probe(method, url, headers, body)
        try:
            parsed = json.loads(text)
        except ValueError:
            parsed = {"_raw": text}
        for var, field in s.get("bind", {}).items():      # from the raw answer
            value = dig(parsed, field)
            if value in (None, ""):
                raise ProbeError(f"{s['name']}: bind {var} <- {field}: absent in "
                                 f"the answer (status {status})")
            bound[var] = value if isinstance(value, str) else json.dumps(value)
        mode = s.get("mode", "stable")
        resp = (normalize_stable(parsed, frozenset(s.get("volatile_keys", [])))
                if mode == "stable" else normalize_shape(parsed))
        out[s["name"]] = {"method": method, "path": s["path"],   # templates, not values
                          "request_body": s.get("body"),
                          "status": status, "mode": mode, "response": resp,
                          "expect_status": s.get("expect_status"),
                          "note": s.get("note")}
    return out


def diff(a, b, path="$", acc=None):
    """Every differing JSON path, as (path, text) pairs."""
    acc = [] if acc is None else acc
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k not in b:
                acc.append((f"{path}.{k}", "removed"))
            elif k not in a:
                acc.append((f"{path}.{k}", "added"))
            else:
                diff(a[k], b[k], f"{path}.{k}", acc)
    elif isinstance(a, list) and isinstance(b, list):
        for i, (x, y) in enumerate(zip(a, b)):
            diff(x, y, f"{path}[{i}]", acc)
        for i in range(len(b), len(a)):
            acc.append((f"{path}[{i}]", "removed"))
        for i in range(len(a), len(b)):
            acc.append((f"{path}[{i}]", "added"))
    elif a != b:
        acc.append((path, f"{json.dumps(a)[:60]} -> {json.dumps(b)[:60]}"))
    return acc


def cmd_capture(spec, outdir, rebaseline=None, probe=http_probe, transport="urllib"):
    outdir = pathlib.Path(outdir)
    old = outdir / "manifest.json"
    if old.exists() and not rebaseline:
        print(f"refusing to overwrite {outdir}: pass --rebaseline '<why>'")
        return 2
    surfaces = capture(spec, probe)
    bad = [f"{n}: status {r['status']}, expected {r['expect_status']}"
           for n, r in surfaces.items()
           if r["expect_status"] is not None and r["status"] != r["expect_status"]]
    if bad:
        print("not writing a golden record of broken behavior:")
        print("\n".join("  " + b for b in bad))
        return 1
    history = json.loads(old.read_text())["rebaselines"] if old.exists() else []
    if rebaseline:
        history.append(rebaseline)
    outdir.parent.mkdir(parents=True, exist_ok=True)
    tmp = pathlib.Path(tempfile.mkdtemp(prefix=".baseline-", dir=outdir.parent))
    mask = os.umask(0); os.umask(mask)
    os.chmod(tmp, 0o777 & ~mask)          # mkdtemp makes 0700; follow the umask
    for name, rec in surfaces.items():
        (tmp / f"{name}.json").write_text(
            json.dumps(rec, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    manifest = {"surfaces": {n: {k: r[k] for k in ("method", "path", "status", "mode")}
                             for n, r in sorted(surfaces.items())},
                "transport": transport, "rebaselines": history}
    (tmp / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    if outdir.exists():
        shutil.rmtree(outdir)              # the tool owns --dir: keep notes elsewhere
    tmp.rename(outdir)                     # all surfaces or none, never a mix
    for n, r in sorted(surfaces.items()):
        print(f"  captured  {n:28s} status={r['status']} mode={r['mode']}")
        if r["status"] >= 400 and r["expect_status"] is None:
            print(f"  WARNING {n}: status {r['status']} and no expect_status; "
                  "is this the behavior to keep?")
    print(f"wrote {len(surfaces)} surface(s) + manifest.json to {outdir} "
          f"(transport {transport})")
    return 0


def allowed(allow, name, path):
    for a in allow:
        p = a["path"]
        if a["surface"] == name and (path == p or path.startswith((p + ".", p + "["))):
            return a
    return None


def cmd_check(spec, outdir, probe=http_probe, transport="urllib", allow=()):
    outdir = pathlib.Path(outdir)
    if not (outdir / "manifest.json").exists():
        print(f"no golden record in {outdir}: capture one first")
        return 2
    manifest = json.loads((outdir / "manifest.json").read_text())
    if manifest.get("transport", "urllib") != transport:
        print(f"golden captured through transport {manifest.get('transport', 'urllib')}, "
              f"check runs through {transport}: capture and check must use the same one")
        return 2
    stored_names = set(manifest["surfaces"])
    current = capture(spec, probe)
    found = [(n, "surface", "in the golden record but no longer probed")
             for n in sorted(stored_names - set(current))]
    for name, rec in sorted(current.items()):
        if name not in stored_names:
            found.append((name, "surface", "probed but has no golden (capture with --rebaseline)"))
            continue
        old = json.loads((outdir / f"{name}.json").read_text(encoding="utf-8"))
        for f in REQUEST_FIELDS:
            if old.get(f) != rec[f]:
                found.append((name, "request", f"request changed ({f}): re-baseline"))
        if old["mode"] != rec["mode"]:
            found.append((name, "mode", f"mode {old['mode']} -> {rec['mode']} (re-baseline)"))
        if old["status"] != rec["status"]:
            found.append((name, "status", f"status {old['status']} -> {rec['status']}"))
        found += [(name, p, f"{p}: {t}") for p, t in diff(old["response"], rec["response"])]
    used, drift, shown = set(), [], {}
    for name, path, text in found:
        a = allowed(allow, name, path)
        if a is not None:
            used.add(id(a))
            print(f"  ALLOWED {name}: {text} ({a['why']})")
        elif shown.get(name, 0) < 20:          # the first 20 per surface
            shown[name] = shown.get(name, 0) + 1
            drift.append(f"{name}: {text}")
    stale = [a for a in allow if id(a) not in used]
    for a in stale:
        drift.append(f"{a['surface']}: stale allowance {a['path']} matched nothing ({a['why']})")
    if drift:
        print("DRIFT (behavior differs from the golden record):")
        print("\n".join("  " + d for d in drift))
        return 1
    print(f"MATCH: {len(current)} surface(s) equal the golden record"
          + (f", {len(used)} allowance(s) used" if used else ""))
    return 0


def main(argv, probe=http_probe, transport="urllib"):
    if argv[:1] == ["--self-test"]:
        return self_test()
    if len(argv) < 1 or argv[0] not in ("capture", "check"):
        print(__doc__)
        return 2
    args = dict(zip(argv[1::2], argv[2::2]))
    if "--spec" not in args or "--dir" not in args:
        print("--spec and --dir are required")
        return 2
    try:
        spec = load_spec(args["--spec"])
        if argv[0] == "capture":
            return cmd_capture(spec, args["--dir"], args.get("--rebaseline"), probe, transport)
        allow = []
        if "--allow" in args:
            allow = json.loads(pathlib.Path(args["--allow"]).read_text(encoding="utf-8"))
            for a in allow:
                if not all(isinstance(a.get(k), str) and a[k] for k in ("surface", "path", "why")):
                    raise ValueError(f"allowance {a!r}: needs surface, path and why")
        return cmd_check(spec, args["--dir"], probe, transport, allow)
    except (ProbeError, ValueError, KeyError, OSError) as e:
        print(f"ERROR: {e}")
        return 2


def self_test():
    import contextlib, io, threading
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
    state = {"price": 3, "calls": 0, "drop_field": False, "tok": ""}

    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_GET(self):
            state["calls"] += 1
            if self.path == "/catalogue":
                body = {"items": [{"name": "a", "price": state["price"]}], "featured": "a",
                        "meta": {"rid": state["calls"], "host": "h1"},
                        "generatedAt": f"2026-01-01T00:00:{state['calls'] % 60:02d}Z"}
            elif self.path == "/live":
                body = {"temp": state["calls"] * 1.5, "unit": "C"}
                if not state["drop_field"]:
                    body["icon"] = f"i{state['calls']}"
            elif self.path == "/old":
                self.send_response(302); self.send_header("Location", "/catalogue")
                self.end_headers(); return
            elif self.path == "/item/a":
                if self.headers.get("Authorization") != f"Bearer {state['tok']}":
                    self.send_response(401); self.end_headers(); return
                body = {"name": "a", "price": state["price"]}
            else:
                self.send_response(404); self.end_headers(); return
            self._send(body)

        def do_POST(self):
            n = int(self.headers.get("Content-Length", 0))
            sent = json.loads(self.rfile.read(n))
            ok = sent.get("password") == "s3cret-value"
            state["tok"] = f"eyJhbGciOiJIUzI1.eyJzdWIiOiJ{state['calls']:05d}.c2lnbmF0dXJlLXZhbHVl"
            self._send({"user": "demo", "token": state["tok"]} if ok else {"error": "bad"})

        def _send(self, body):
            raw = json.dumps(body).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

    srv = ThreadingHTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    work = pathlib.Path(tempfile.mkdtemp())
    os.environ["BASELINE_SELFTEST_PW"] = "s3cret-value"
    spec = {"base_url": f"http://127.0.0.1:{srv.server_port}", "surfaces": [
        {"name": "login", "method": "POST", "path": "/login", "bind": {"TOK": "token"},
         "body": {"user": "demo", "password": "${BASELINE_SELFTEST_PW}"}},
        {"name": "catalogue", "path": "/catalogue", "expect_status": 200,
         "volatile_keys": ["meta"], "bind": {"FEATURED": "featured"}},
        {"name": "item", "path": "/item/${FEATURED}", "expect_status": 200,
         "headers": {"Authorization": "Bearer ${TOK}"}},
        {"name": "old", "path": "/old"},
        {"name": "live", "path": "/live", "mode": "shape"}]}
    gold = work / "new" / "baseline"

    def run(fn, *a, **kw):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = fn(*a, **kw)
        return rc, buf.getvalue()

    rc, out = run(cmd_capture, spec, gold)
    assert rc == 0, out
    disk = "".join(p.read_text() for p in gold.iterdir())
    assert "s3cret-value" not in disk and "${BASELINE_SELFTEST_PW}" in disk, "secret on disk"
    assert state["tok"] not in disk and "/item/${FEATURED}" in disk, "bound value on disk"
    assert '"<JWT>"' in disk and '"<TIMESTAMP>"' in disk, "volatile values not masked"
    assert '"meta": "<VOLATILE>"' in disk, "an object-valued volatile key was not masked"
    assert '"_location": "/catalogue"' in disk and '"status": 302' in disk, "redirect followed"
    rc, out = run(cmd_check, spec, gold)
    assert rc == 0 and "MATCH" in out, f"token/time/magnitude churn read as drift: {out}"
    rc, out = run(cmd_capture, spec, gold)
    assert rc == 2 and "refusing" in out, "silent overwrite of the golden record"
    rc, out = run(cmd_check, spec, gold, transport="in-network")
    assert rc == 2 and "same one" in out, "a check through another transport ran"
    state["price"] = 4
    rc, out = run(cmd_check, spec, gold)
    assert rc == 1 and "catalogue: $.items[0].price: 3 -> 4" in out, out
    allow = [{"surface": "catalogue", "path": "$.items[0].price", "why": "planned"}]
    rc, out = run(cmd_check, spec, gold, allow=allow)
    assert rc == 1 and "ALLOWED catalogue" in out and "item: $.price" in out, out
    allow.append({"surface": "item", "path": "$", "why": "planned"})
    rc, out = run(cmd_check, spec, gold, allow=allow)
    assert rc == 0 and "2 allowance(s) used" in out, f"allowed deltas still failed: {out}"
    state["price"] = 3
    rc, out = run(cmd_check, spec, gold, allow=allow)
    assert rc == 1 and "stale allowance" in out, f"a stale allowance passed: {out}"
    state["drop_field"] = True
    rc, out = run(cmd_check, spec, gold)
    assert rc == 1 and "live: $.icon: removed" in out, out
    state["drop_field"] = False
    fewer = dict(spec, surfaces=spec["surfaces"][:4])
    rc, out = run(cmd_check, fewer, gold)
    assert rc == 1 and "no longer probed" in out, f"a dropped surface passed: {out}"
    moved = dict(spec, surfaces=[dict(s, path="/catalogue") if s["name"] == "old" else s
                                 for s in spec["surfaces"]])
    rc, out = run(cmd_check, moved, gold)
    assert rc == 1 and "old: request changed (path)" in out, f"a re-pointed surface passed: {out}"
    noauth = dict(spec, surfaces=[dict(spec["surfaces"][2], path="/item/a", headers={})])
    rc, out = run(cmd_capture, noauth, work / "other")
    assert rc == 1 and not (work / "other").exists(), "golden written for a 401"
    unbound = dict(spec, surfaces=spec["surfaces"][2:3])
    try:
        run(cmd_capture, unbound, work / "other")
    except ProbeError:
        pass
    else:
        raise AssertionError("an unbound ${VAR} in a path did not stop the run")
    srv.shutdown(); srv.server_close()
    try:
        run(cmd_check, spec, gold)
    except ProbeError:
        pass
    else:
        raise AssertionError("a dead endpoint did not raise ProbeError (exit 2)")
    shutil.rmtree(work)
    del os.environ["BASELINE_SELFTEST_PW"]
    print("self-test: PASS (mask, bind, match, refuse-overwrite, transport, stable drift,"
          " allowlist, shape drift, dropped surface, request change, broken-capture refusal,"
          " unbound variable, dead endpoint)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
```

The in-network wrapper. It sits beside `baseline.py` and the in-network
page's `harness.py`, takes the same arguments as `baseline.py` and the same
environment as the harness:

```python
#!/usr/bin/env python3
"""baseline_in_network.py: baseline.py through the in-network transport.
Same arguments as baseline.py; same environment as harness.py."""
import sys
import baseline as B
import harness as H

h = H.Harness()


def probe(method, url, headers, body):
    try:
        return h.probe(method, url, headers, body)
    except H.HarnessError as e:            # no answer, or a method wget cannot send
        raise B.ProbeError(str(e)) from None


sys.exit(B.main(sys.argv[1:], probe=probe, transport="in-network"))
```

Recorded run of the self-test and of the script on a synthetic fixture (a
static JSON file served by `python3 -m http.server`; the `price` value edited
between the capture and the second check, then the server stopped, then a
listener that answers with a line that is not HTTP), on Python 3.14:

```text
$ python3 baseline.py --self-test
self-test: PASS (mask, bind, match, refuse-overwrite, transport, stable drift, allowlist, shape drift, dropped surface, request change, broken-capture refusal, unbound variable, dead endpoint)
$ python3 baseline.py capture --spec spec.json --dir gold          # exit 0
  captured  items                        status=200 mode=stable
  captured  items_shape                  status=200 mode=shape
wrote 2 surface(s) + manifest.json to gold (transport urllib)
$ python3 baseline.py check --spec spec.json --dir gold            # exit 0
MATCH: 2 surface(s) equal the golden record
$ python3 baseline.py check --spec spec.json --dir gold            # exit 1, after the edit
DRIFT (behavior differs from the golden record):
  items: $.items[0].price: 3 -> 5
$ python3 baseline.py check --spec spec.json --dir gold --allow allow.json   # exit 0
  ALLOWED items: $.items[0].price: 3 -> 5 (price rule changed by the plan)
MATCH: 2 surface(s) equal the golden record, 1 allowance(s) used
$ python3 baseline.py check --spec spec.json --dir gold            # exit 2, server stopped
ERROR: GET http://127.0.0.1:18766/items.json: no HTTP answer (URLError(ConnectionRefusedError(111, 'Connection refused')))
$ python3 baseline.py check --spec g.json --dir gold               # exit 2, not HTTP
ERROR: GET http://127.0.0.1:18767/items.json: no HTTP answer (BadStatusLine('NOT HTTP AT ALL\r\n'))
```

The `items_shape` surface did not drift on the price edit. That is the
`shape` mode working as designed. The wrapper was run with a stand-in
`harness` module (no container stack): a check of the `urllib` golden was
refused with exit `2`, a capture and check through it gave `MATCH`, and a
stand-in `HarnessError` exited `2` as `ERROR: no HTTP answer`. It has not
been run against a live compose stack.

## 5. Pitfalls and sharp edges

- **A baseline captured on a broken system protects the breakage.** The
  rule that a system is seen working before it is migrated belongs to
  `skill-corpus/framework-version-migration.md` (its prerequisite).
  `expect_status` and the capture `WARNING` are this tool's mechanical part
  of it; give every surface whose status you know an `expect_status`.
- **Moving a surface to `shape` weakens the oracle silently.** A seeded,
  deterministic read belongs in `stable`. Put a surface in `shape` only when
  its content varies between two back-to-back captures, and only for that
  reason. A mode change on an existing surface is reported as drift, so it
  needs `--rebaseline` and a reason.
- **A volatile field left unmasked makes the gate flaky, and a flaky gate gets
  ignored.** Run `check` right after the first `capture`, before the change.
  Any drift then is volatility, not behavior: add the key to
  `volatile_keys` or move the surface to `shape`.
- **Fixed-point masks hide changes inside the mask.** A field masked as
  `<TIMESTAMP>` or `<VOLATILE>` can change format or meaning and still match.
  When a timestamp format is part of the contract (a client parses it), cover
  it with a functional test, not with this oracle.
- **`shape` reads only the first list element.** A list whose elements differ
  in structure is compared on its first element only, and a list that is empty
  at capture records no element shape, so it drifts when it fills. Seed the
  data so that each list probed in `shape` mode is non-empty and uniform.
- **Probes are replayed on every check, so each must be safe to repeat.** See
  `tool-corpus/testing/http-smoke-suite.md` §5 for state-destroying flows on
  shared accounts.
- **A bound token must outlive one run.** Every surface after the login
  reuses the token it bound. A token that expires within a run turns the
  later surfaces into 401 drift; capture and check on a token lifetime longer
  than the run.
- **A fire-and-forget surface has no answer to record.** When a request's
  effect shows up elsewhere (a queued command, a sent message), one request
  per surface sees only the acknowledgement. Write a custom `probe` that sends
  the command and returns the observed message, using
  `tool-corpus/testing/fire-and-forget-command-observer.md` as the observer.
- **Capture and check through the same transport.** A golden captured from
  inside the container network and checked from the runner (or the reverse)
  differs on every redirect and every non-2xx body for reasons that are not
  behavior. `check` refuses the mix.
- **A hand-edited golden is a test edited to pass.** Change the record only
  through `capture --rebaseline "<why>"`. During a migration, list the
  intended deltas of the plan (`skill-corpus/framework-version-migration.md`,
  step 5) in the `--allow` file and keep the golden as it is. Re-baseline
  only from a `check` whose every difference printed `ALLOWED`, and name the
  allowlist in the reason. A plain re-baseline re-captures every surface,
  unintended drift included. When differences that no allowlist entry explains
  remain, do not re-capture, skip or mark them expected to reach green.
  Record the failing set by name and count, and ship red with it. A later run
  that reports fewer failures than recorded has absorbed something until the
  change that fixed each one is named. A re-capture that also moves a golden
  already stale for another cause fuses the two, so neither can be
  attributed afterwards.

## 6. Tests that cover it

The self-test in the script above (`baseline.py --self-test`) serves a
synthetic system from `http.server` on a free local port and asserts, in
order: the secret, the token and the bound values never reach disk while the
templates do; an object under a volatile key is masked whole; a redirect is
recorded as its status and target, not followed; token, timestamp and
magnitude churn reads as `MATCH`; a second capture without `--rebaseline` is
refused; a check through another transport is refused; a changed seeded value
is drift with its JSON path; an allowance passes only the difference it names,
and a stale one fails; a field dropped from a `shape` surface is drift; a
surface dropped from the spec is drift; a spec edit that re-points a surface
is drift; a capture where a surface misses `expect_status` (a 401 without the
bound token) writes nothing; a `${VAR}` that nothing bound stops the run; a
stopped server raises `ProbeError` instead of reporting drift or a match.
Each of the five newest properties (the object-valued volatile key, the
redirect, the request comparison, the stale allowance, the transport check)
was mutated out of a scratch copy once, and the self-test failed each time.

- **How to run the tests:** `python3 baseline.py --self-test` (exit 0 on
  pass; an `AssertionError` names the property that failed).

## 7. References & neighbours

- **Related tools:** `tool-corpus/testing/in-network-e2e-harness.md` (the
  transport when the edge is reachable only from inside a container network);
  `tool-corpus/testing/http-smoke-suite.md` (whether the system serves, rather
  than whether it serves the same thing);
  `tool-corpus/testing/cross-implementation-parity-verifier.md` (sameness
  between two implementations running side by side, where this tool compares
  one system before and after a change).
- **Related procedure:** `skill-corpus/framework-version-migration.md`
  (step 1 captures with this tool; step 5's intended-delta list is the
  `--allow` file).
- **Method:** `protocols/verify-disagreement.md` (characterize first, capture
  read-only, an enumerated intended-delta list).
- **Sources:** distilled from practice (a migration gate
  used across a framework major-line upgrade). Standard-library behavior
  checked against the Python docs (`urllib.request` `HTTPRedirectHandler`,
  `http.client` exceptions, `tempfile.mkdtemp`):
  https://docs.python.org/3/library/urllib.request.html,
  https://docs.python.org/3/library/http.client.html,
  https://docs.python.org/3/library/tempfile.html. Token forms:
  RFC 7519 §1 and RFC 7516 §3.1 (https://www.rfc-editor.org/rfc/rfc7516).

## 8. Changelog

- 2026-10-05 — created from a capture-and-check driver, generalized:
  the surface list moved into a spec file with `${VAR}` templates, the
  diff became two-way (a surface dropped from the probe list is drift) with
  JSON paths, and the all-or-nothing write, the `--rebaseline` reason record,
  `expect_status` and the no-answer exit `2` were added; by tool-smith.
- 2026-10-05 (review fix pass): bindings carry a login token or a run-time
  id into later surfaces, and `${VAR}` now expands in `path`; `check` compares
  each surface's request with the golden and reads an intended-delta
  allowlist (`--allow`, stale entries fail); the manifest records the
  transport and `check` refuses a mix; the in-network wrapper is shown; a
  volatile key masks an object whole, a redirect is recorded, not
  followed, a non-HTTP reply exits `2`, an error status without
  `expect_status` warns, and a list length change names each index; the
  shared-account rule now points to the smoke-suite page; by tool-smith.
- 2026-10-05: the hand-edited-golden pitfall now says what to do with
  unexplained residue: record it by name and count, ship red, and never fuse
  it into a re-capture (§5); by docs-librarian.
