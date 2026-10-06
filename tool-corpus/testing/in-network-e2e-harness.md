# Tool: in-network-e2e-harness

> Project-agnostic capability notes, kept in the seed's tool corpus
> (`tool-corpus/README.md`). A portable driver: the module below runs as-is
> against any compose stack whose containers carry a busybox-style `wget`; the
> test cases are the plant's.

## 0. Identity

- **Category:** testing
- **Name:** in-network-e2e-harness
- **Language / runtime:** python3, **stdlib only**, driving the `docker` CLI
  (`docker compose ps`, `docker exec`); the probes run with the `wget` that
  is already inside a service container
- **Stability:** **portable**. The driver, its idioms and its runner are
  complete; the plant writes the cases and sets five environment variables.

## 1. What it does

A reusable driver for live end-to-end tests of a containerized stack. The
probes run **inside a service container** on the stack's own network, not on
the host. That gives three things:

- The test reaches services by their in-network names (`edge:8080`), through
  the same edge a client uses, with no published port added for testing.
- The host needs no HTTP client. A minimal host image without `curl` is
  enough, because the service images already carry busybox `wget`.
- What the test sees is what the services see: the same DNS, the same
  network policy.

On top of that transport it gives tests a small set of idioms that each
close a known way for an end-to-end test to lie or leak: request bodies off
the command line, credentials read at call time and never printed, one-time
codes read only from a mail-capture server's API, infrastructure errors that
fail loudly, and a route precondition that tells an outage apart from the
regression a case guards.

## 2. Interface & invocation

```sh
# from the compose project root on the stack's host
PROBE_SVC=<service> EDGE=<host:port> python3 harness.py   # self-check; exit 2 if unreachable
python3 harness.py --self-test                            # offline self-test
PROBE_SVC=<service> EDGE=<host:port> python3 test_<flow>.py
```

A case file imports the module and hands `(name, function)` pairs to `run`:

```python
import sys
import harness as H

try:
    h = H.Harness()                                 # PROBE_SVC and EDGE are required
except H.HarnessError as e:
    print(e)
    sys.exit(2)                                     # a configuration error: no case ran

def login_roundtrip():
    h.require_alive("/auth/health")                 # outage is ERROR, not FAIL
    before = h.snapshot_mail()                      # before the flow sends mail
    pw = h.credential("SEED_PASSWORD", "auth")      # container env, then host file
    status, _ = h.post_json("/auth/register", {"email": "u1@example.test", "password": pw})
    assert status == 201, status
    mail = h.wait_for_new_mail("u1@example.test", before)
    code = H.extract_single(r"Your code is (\d{6})", H.visible_text(h.mail_html(mail["id"])), "code")
    status, _ = h.post_json("/auth/verify", {"email": "u1@example.test", "code": code})
    assert status == 200, status

sys.exit(H.run([("login round-trip", login_roundtrip)]))
```

- **Environment:** `PROBE_SVC` (required: the service whose container runs
  the probes), `EDGE` (required: the in-network `host:port` of the edge
  under test), `COMPOSE_DIR` (default: the working directory), `MAIL_API`
  (the in-network base URL of the mail-capture server; needed only by the
  mail helpers), `HOST_ENV_FILE` (the host-side env file for the credential
  fallback). Two limits are built in: each `wget` call times out after 20 s
  (`-T 20`), and the mail helpers read only the newest 200 messages
  (`pageSize=200`; smtp4dev's own default is 5), so clear a shared inbox that
  receives more than 200 messages during one flow.
- **API:** `get(path, bearer=None)` and `post_json(path, payload,
  bearer=None)` return `(status, body)`; `wget(args)` is the raw call;
  `require_alive(path)`; `credential(var, service)`; `container_env(service,
  var)`; `snapshot_mail()`, `wait_for_new_mail(recipient, before)`,
  `mail_html(id)`; `visible_text(html)`, `extract_single(pattern, text,
  what)`; `run(cases)`; and `probe(method, url, headers, body)`, a transport
  with the signature `tool-corpus/testing/behavior-baseline-oracle.md`
  accepts. The oracle expects its own `ProbeError` on no answer and maps only
  that error to exit `2`, while `probe` raises `HarnessError`, so the plant
  runs the oracle through the wrapper the oracle page owns (its §4,
  `baseline_in_network.py`), which maps one error to the other.
- **Exit codes:** a case file exits `0` when every case passed, `1` when any
  case failed or errored, `2` when no case ran (the example above also exits
  `2` when `PROBE_SVC` or `EDGE` is unset; without that `try` the error is a
  traceback with exit `1`). The self-check exits `2` when
  the edge or the mail API gives no answer.
- **Preconditions:** Docker with Compose v2 on the host; the stack is up; the
  probe container has a `wget` that supports `-S`, `-T`, `--header` and
  `--post-file` (busybox builds it with long options by default; check with
  `docker exec <c> wget --help`), plus `sh` and `mktemp`.

## 3. Approach / algorithm

**Status from wget's stderr, in both of its forms.** Busybox `wget` exits `1`
for every failure, so the exit code cannot tell a 404 from a refused
connection. The status comes from the `HTTP/x.y NNN` token on stderr. With
`-S` a success prints the status line indented (`  HTTP/1.1 200 OK`) before
the headers; a non-2xx answer prints the same indented line and then dies with
`wget: server returned error: HTTP/1.1 404 Not Found`. Without `-S` only the
second form appears. The harness takes the last match of `HTTP/[0-9.]+
([0-9]{3})`, which reads both forms. No match at all means no HTTP answer
(refused, timed out, name not resolved), which raises `HarnessError`: an
environment fault is never turned into a status. These behaviours are in
busybox's `networking/wget.c` and were reproduced on a current busybox
release. A probe container with no `wget` at all makes `docker exec` exit
`126` or `127`; the harness reports that as "no usable wget", not as a
missing HTTP answer.

**Request bodies travel on stdin, never in argv.** `post_json` pipes the
JSON into a file created by `mktemp` under `umask 077` inside the probe
container, passes it with `--post-file`, and removes it in a `finally`, also
when the request fails. A password in a body therefore never appears in the
host's or the container's process list, and no shell quoting touches it.

**Credentials are read at call time, from two places, and never printed.**
`credential(var, service)` reads the variable from the running service
container's environment. When it is unset or empty there, it reads the
host-side env file named by `HOST_ENV_FILE`. This is the fallback that keeps authenticated
gates working after a cutover to a production profile that deliberately
withholds a seed password from container environments, while the seeded
account persists in the database. When neither source has the value, the
call raises and names both sources, never the value.

**One-time codes and reset mail come only from the capture server's API.**
Never from the source, the logs or the database. `snapshot_mail()` records
the ids already in the inbox before the flow runs; `wait_for_new_mail` polls
for a message to the recipient whose id is new, and raises on timeout. It
compares ids, not received-dates, so a clock difference between the capture
container and the host cannot match an old message or miss a new one. The
list shape assumed is smtp4dev's (`GET /api/Messages` returns `results`, each
with `id`, `to`, `deliveredTo`; `GET /api/Messages/{id}/html` returns the
body; see `library-corpus/container/smtp4dev.md`). For another capture
server, change `mail_ids` and `mail_html` only. `extract_single` returns the
one distinct match of a pattern anchored on the mail template and fails on
zero or several, so a footer year is never mistaken for a code.

**Infrastructure errors fail loudly.** A missing container, an unreadable
variable, a body that could not be staged, a mail that never came: each
raises `HarnessError`, and `run` reports it as `ERROR`, which fails the run.
Nothing in the harness returns an empty default where a value was needed.

**Check the route is alive before asserting a regression.** A case that
guards a specific bug first calls `require_alive(path)` on a cheap route of
the same service (an API-docs or health path). A status outside 2xx there,
or no answer, raises `RouteDown`, which `run` prints as an ERROR marked
"precondition, not the regression". A 500 counts as down too: a service that
answers 500 everywhere (its database is down, its start failed) must not pass
the precondition and then report the regression as FAIL. For a precondition
route that answers 401 or 403 to an unauthenticated call, pass `ok=`, for
example `ok=lambda s: s in (200, 401)`. A routing outage then never reads as the
bug coming back, and the bug's own assertion is reached only when the route
is up.

## 4. Portable vs blueprint

- **Portable (use as-is):** the module below: the container lookup, the
  status parse, the stdin body path, the credential fallback, the id-based
  mail wait, the single-match extractor, the route precondition, the runner,
  the transport adapter, the self-test.
- **Project-specific (fill in):** the cases; the five environment variables;
  the precondition path per service; the mail-template pattern; for another
  mail-capture server, `mail_ids` and `mail_html`. A database assertion is a
  plant addition: pipe the SQL on stdin to the client inside the database
  container, with the database password read by that container's own shell
  from its own environment, and raise on a non-zero exit. Never interpolate
  SQL into a shell string.

```python
#!/usr/bin/env python3
"""in-network-e2e-harness: drive end-to-end probes from INSIDE a service
container on a compose network, so the test sees the network the services
see and the host needs no HTTP client of its own.

  harness.py            # self-check: edge and mail capture reachable (exit 2 if not)
  harness.py --self-test
  import harness as h   # in a test file; see the page for a case example

Stdlib only; drives the `docker` CLI. Configuration comes from the environment:
  COMPOSE_DIR   compose project root (default: current directory)
  PROBE_SVC     service whose container runs the probes (required)
  EDGE          in-network host:port of the edge under test (required)
  MAIL_API      in-network base URL of the mail-capture API (optional)
  HOST_ENV_FILE host-side env file for the credential fallback (optional)
"""
import json, os, re, subprocess, sys, time

STATUS_RE = re.compile(r"HTTP/[0-9.]+ ([0-9]{3})")
VAR_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


class HarnessError(RuntimeError):
    """The environment, not the system under test, failed. Never a pass."""


class RouteDown(HarnessError):
    """The precondition route is not alive: an outage, not the regression."""


def docker_exec(argv, input_bytes=None):
    p = subprocess.run(argv, input=input_bytes, capture_output=True)
    return p.returncode, p.stdout, p.stderr


class Harness:
    def __init__(self, exec_fn=docker_exec, env=None):
        env = os.environ if env is None else env
        self.x = exec_fn
        self.compose_dir = env.get("COMPOSE_DIR", os.getcwd())
        self.probe_svc = env.get("PROBE_SVC") or _need("PROBE_SVC")
        self.edge = env.get("EDGE") or _need("EDGE")
        self.mail_api = env.get("MAIL_API")
        self.env_file = env.get("HOST_ENV_FILE")
        self._ids = {}

    # -- containers ---------------------------------------------------------
    def container_id(self, service):
        if service not in self._ids:
            rc, out, err = self.x(["docker", "compose", "--project-directory",
                                   self.compose_dir, "ps", "-q", service])
            ids = out.decode().split()
            if rc != 0 or not ids:
                raise HarnessError(f"no running container for service '{service}' "
                                   f"(is the stack up?) {err.decode()[:200]}")
            if len(ids) > 1:
                raise HarnessError(f"service '{service}' has {len(ids)} running containers; "
                                   "probe through a service that runs one")
            self._ids[service] = ids[0]
        return self._ids[service]

    def container_env(self, service, var):
        """The value of `var` inside the container, or None when it is unset."""
        if not VAR_NAME.match(var):
            raise HarnessError(f"not a variable name: {var!r}")
        script = f'if [ -n "${{{var}+x}}" ]; then printf %s "${var}"; else exit 3; fi'
        rc, out, err = self.x(["docker", "exec", self.container_id(service),
                               "sh", "-c", script])
        if rc == 3:
            return None
        if rc != 0:
            raise HarnessError(f"reading {var} in '{service}' failed: {err.decode()[:200]}")
        return out.decode()

    def credential(self, var, service):
        """Container env first, then the host env file. Never printed."""
        value = self.container_env(service, var)
        if value:
            return value
        if self.env_file and os.path.exists(self.env_file):
            value = read_env_file(self.env_file).get(var)
            if value:
                return value
        raise HarnessError(f"{var} is set neither in the '{service}' container nor in "
                           f"HOST_ENV_FILE ({self.env_file or 'unset'})")

    # -- HTTP through the probe container -----------------------------------
    def wget(self, args, input_bytes=None, service=None):
        """Run busybox-style wget in the probe container. Returns (status, body).
        The body is empty on a non-2xx answer: busybox wget does not save it."""
        cid = self.container_id(service or self.probe_svc)
        rc, out, err = self.x(["docker", "exec", cid, "wget", "-S", "-T", "20",
                               "-q", "-O-", *args], input_bytes)
        if rc in (126, 127):          # docker exec found no runnable wget
            msg = (out + err).decode(errors="replace").strip()
            raise HarnessError(f"probe container has no usable wget (exit {rc}): {msg[:200]}")
        codes = STATUS_RE.findall(err.decode(errors="replace"))
        if not codes:
            first = (err.decode(errors="replace").strip().splitlines() or ["?"])[0]
            raise HarnessError(f"no HTTP answer (wget exit {rc}): {first[:200]}")
        return int(codes[-1]), out.decode(errors="replace")

    def get(self, path, bearer=None, host=None):
        hdr = ["--header", f"Authorization: Bearer {bearer}"] if bearer else []
        return self.wget([*hdr, f"http://{host or self.edge}{path}"])

    def post_json(self, path, payload, bearer=None, host=None):
        """POST JSON. The body travels on stdin into a mktemp file inside the
        container, so a password in it never appears in any argv."""
        hdr = ["--header", f"Authorization: Bearer {bearer}"] if bearer else []
        return self._post(path, json.dumps(payload).encode(), hdr, host)

    def _post(self, path, body, hdr, host=None, ctype="application/json"):
        cid = self.container_id(self.probe_svc)
        rc, out, err = self.x(["docker", "exec", "-i", cid, "sh", "-c",
                               'umask 077; f=$(mktemp) && cat > "$f" && echo "$f"'], body)
        tmp = out.decode().strip()
        if rc != 0 or not tmp.startswith("/"):
            raise HarnessError(f"could not stage the request body: {err.decode()[:200]}")
        try:
            return self.wget(["--post-file", tmp, "--header", f"Content-Type: {ctype}",
                              *hdr, f"http://{host or self.edge}{path}"])
        finally:
            self.x(["docker", "exec", cid, "rm", "-f", tmp])

    def require_alive(self, path, ok=lambda s: 200 <= s < 300):
        """Precondition: the route answers 2xx (or what `ok` accepts).
        Run it before asserting a regression."""
        try:
            status, _ = self.get(path)
        except HarnessError as e:
            raise RouteDown(f"precondition {path}: {e}") from None
        if not ok(status):
            raise RouteDown(f"precondition {path} answered {status}: route not alive")

    def probe(self, method, url, headers, body):
        """Transport adapter: probe(method, url, headers, body_bytes) -> (status, text).
        The URL's scheme and host are replaced by EDGE. A POST with no body is
        sent as a POST with an empty body; the caller's Content-Type is kept
        (default application/json). Raises HarnessError on no answer."""
        if method not in ("GET", "POST"):
            raise HarnessError(f"busybox wget cannot send {method}")
        ctype = next((v for k, v in headers.items() if k.lower() == "content-type"),
                     "application/json")
        hdr = [a for k, v in headers.items() if k.lower() != "content-type"
               for a in ("--header", f"{k}: {v}")]
        path = re.sub(r"^https?://[^/]+", "", url)
        if method == "GET":
            return self.wget([*hdr, f"http://{self.edge}{path}"])
        return self._post(path, b"" if body is None else body, hdr, ctype=ctype)

    # -- mail capture --------------------------------------------------------
    def _mail_api(self):
        if not self.mail_api:
            raise HarnessError("MAIL_API is not set")
        return self.mail_api

    def mail_ids(self):
        status, body = self.wget([f"{self._mail_api()}/api/Messages?pageSize=200"])
        if status != 200:
            raise HarnessError(f"mail capture list answered {status}")
        data = json.loads(body)
        return data.get("results", data) if isinstance(data, dict) else data

    def snapshot_mail(self):
        """Call BEFORE triggering the flow that sends mail."""
        return {m["id"] for m in self.mail_ids()}

    def wait_for_new_mail(self, recipient, before, timeout_s=45, poll_s=3):
        """The first message to `recipient` whose id was not in `before`.
        Compares ids, not timestamps, so container and host clocks never matter."""
        want = recipient.lower()
        deadline = time.monotonic() + timeout_s
        while time.monotonic() < deadline:
            for m in self.mail_ids():
                to = [t.lower() for t in (m.get("to") or [])]
                if m["id"] not in before and (want in to or
                                              want == (m.get("deliveredTo") or "").lower()):
                    return m
            time.sleep(poll_s)
        raise HarnessError(f"no new mail for {recipient} within {timeout_s}s: "
                           "the flow did not send it, or the capture server lost it")

    def mail_html(self, message_id):
        status, body = self.wget([f"{self._mail_api()}/api/Messages/{message_id}/html"])
        if status != 200:
            raise HarnessError(f"mail body {message_id} answered {status}")
        return body


# -- helpers ----------------------------------------------------------------
def _need(var):
    raise HarnessError(f"{var} must be set")


def read_env_file(path):
    out = {}
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.strip()
        if k.startswith("export "):
            k = k[7:].strip()
        v = v.strip()
        if len(v) >= 2 and v[0] == v[-1] and v[0] in "'\"":
            v = v[1:-1]
        out[k] = v
    return out


def visible_text(html):
    html = re.sub(r"(?is)<(style|script).*?</\1>", " ", html)
    return re.sub(r"\s+", " ", re.sub(r"(?s)<[^>]+>", " ", html).replace("&nbsp;", " ")).strip()


def extract_single(pattern, text, what):
    """Exactly one distinct match, or a loud failure naming the candidates."""
    found = list(dict.fromkeys(re.findall(pattern, text)))
    if len(found) != 1:
        raise HarnessError(f"expected exactly one {what}, found {len(found)}; "
                           "anchor the pattern on the mail template")
    return found[0]


def run(cases):
    """Run (name, fn) cases. Exit 0 all PASS; 1 any FAIL or ERROR; 2 no cases."""
    if not cases:
        print("no cases ran: not a pass")
        return 2
    bad = 0
    for name, fn in cases:
        try:
            fn()
            print(f"  PASS  {name}")
        except RouteDown as e:
            bad += 1
            print(f"  ERROR {name} (precondition, not the regression)\n        {e}")
        except AssertionError as e:
            bad += 1
            print(f"  FAIL  {name}\n        {e}")
        except Exception as e:  # infrastructure: loud, never a silent pass
            bad += 1
            print(f"  ERROR {name}\n        {type(e).__name__}: {e}")
    return 1 if bad else 0


def self_test():
    import tempfile
    calls = []
    mailbox = [{"id": "m1", "to": ["new@example.test"]}]
    files = {}

    def fake(argv, input_bytes=None):
        calls.append((argv, input_bytes))
        if argv[:3] == ["docker", "compose", "--project-directory"]:
            return {"probe": (0, b"cid-probe\n", b""), "bare": (0, b"cid-bare\n", b""),
                    "scaled": (0, b"cid-1\ncid-2\n", b"")}.get(argv[-1], (0, b"", b""))
        if argv[:2] == ["docker", "exec"] and "sh" in argv:
            script = argv[-1]
            if "mktemp" in script:
                files["/tmp/tmp.abc"] = input_bytes
                return 0, b"/tmp/tmp.abc\n", b""
            if "${SET_VAR+x}" in script:
                return 0, b"from-container", b""
            return 3, b"", b""
        if argv[:2] == ["docker", "exec"] and argv[3] == "rm":
            files.pop(argv[-1], None)
            return 0, b"", b""
        if argv[:2] == ["docker", "exec"] and argv[3] == "wget":
            if argv[2] == "cid-bare":
                return 127, b'exec: "wget": executable file not found in $PATH', b""
            url = argv[-1]
            if url.endswith("/ok"):
                return 0, b'{"ok":true}', b"  HTTP/1.1 200 OK\n  Content-Length: 11\n"
            if url.endswith("/missing"):
                return 1, b"", (b"  HTTP/1.1 404 Not Found\n"
                                b"wget: server returned error: HTTP/1.1 404 Not Found\n")
            if url.endswith("/plain-error"):
                return 1, b"", b"wget: server returned error: HTTP/1.1 500 Internal\n"
            if "/api/Messages?" in url:
                return 0, json.dumps({"results": mailbox}).encode(), b"  HTTP/1.1 200 OK\n"
            return 1, b"", b"wget: can't connect to remote host: Connection refused\n"
        return 1, b"", b"unexpected argv"

    h = Harness(exec_fn=fake, env={"PROBE_SVC": "probe", "EDGE": "edge:8080",
                                   "MAIL_API": "http://mail"})
    assert h.get("/ok") == (200, '{"ok":true}')
    assert h.get("/missing") == (404, "")                     # -S form
    assert h.get("/plain-error")[0] == 500                    # error-line form
    try:
        h.get("/down")
    except HarnessError as e:
        assert "no HTTP answer" in str(e)
    else:
        raise AssertionError("a refused connection read as an HTTP status")
    st, _ = h.post_json("/ok", {"password": "pw-123"})
    assert st == 200 and not any("pw-123" in " ".join(a) for a, _ in calls), "secret in argv"
    assert files == {}, "request body file left behind"
    try:
        h.post_json("/down", {"password": "pw-123"})
    except HarnessError:
        pass
    assert files == {}, "body file left behind after a failed request"
    assert h.credential("SET_VAR", "probe") == "from-container"
    envf = tempfile.NamedTemporaryFile("w", suffix=".env", delete=False)
    envf.write("# comment\nexport OTHER='from-file'\n"); envf.close()
    h.env_file = envf.name
    assert h.credential("OTHER", "probe") == "from-file"
    try:
        h.credential("ABSENT", "probe")
    except HarnessError as e:
        assert "neither" in str(e)
    else:
        raise AssertionError("a missing credential did not fail loudly")
    os.unlink(envf.name)
    before = h.snapshot_mail()
    mailbox.append({"id": "m2", "to": ["New@Example.test"]})
    assert h.wait_for_new_mail("new@example.test", before, timeout_s=1, poll_s=0)["id"] == "m2"
    try:
        h.wait_for_new_mail("other@example.test", before, timeout_s=0.2, poll_s=0.1)
    except HarnessError:
        pass
    else:
        raise AssertionError("a mail that never came did not fail")
    assert extract_single(r"code: (\d{6})", "your code: 123456", "code") == "123456"
    try:
        extract_single(r"(?<!\d)(\d{4})(?!\d)", "code 1234, footer 1999", "code")
    except HarnessError:
        pass
    else:
        raise AssertionError("an ambiguous extraction picked a value")
    try:
        h.require_alive("/missing")
    except RouteDown:
        pass
    else:
        raise AssertionError("a 404 precondition passed")
    try:
        h.require_alive("/plain-error")
    except RouteDown:
        pass
    else:
        raise AssertionError("a 500 precondition passed")
    calls.clear()
    st, _ = h.probe("POST", "http://any/ok", {"Content-Type": "text/plain"}, None)
    staged = [b for a, b in calls if "mktemp" in a[-1]]
    sent = [a for a, _ in calls if "wget" in a]
    assert st == 200 and staged == [b""], "a POST with no body was not sent as a POST"
    assert "Content-Type: text/plain" in sent[-1], "the caller's Content-Type was dropped"
    for svc, what in (("bare", "no usable wget"), ("scaled", "2 running containers")):
        try:
            Harness(exec_fn=fake, env={"PROBE_SVC": svc, "EDGE": "edge:8080"}).get("/ok")
        except HarnessError as e:
            assert what in str(e), str(e)
        else:
            raise AssertionError(f"probe service '{svc}' did not fail loudly")
    try:
        Harness(exec_fn=fake, env={"PROBE_SVC": "probe", "EDGE": "e:1"}).mail_html("m1")
    except HarnessError as e:
        assert "MAIL_API is not set" in str(e)
    else:
        raise AssertionError("mail_html ran without MAIL_API")
    import contextlib, io
    with contextlib.redirect_stdout(io.StringIO()) as buf:
        assert run([]) == 2
        assert run([("p", lambda: None)]) == 0
        assert run([("f", lambda: h.require_alive("/missing"))]) == 1
    assert "precondition" in buf.getvalue()
    print("self-test: PASS (status in both wget forms, no-answer error, body off argv,"
          " body file cleaned, credential fallback, mail by new id, single extraction,"
          " route precondition incl. 500, empty POST, caller Content-Type, no-wget and"
          " scaled probe errors, MAIL_API check, runner exits)")
    return 0


if __name__ == "__main__":
    if sys.argv[1:] == ["--self-test"]:
        sys.exit(self_test())
    try:
        h = Harness()
        status, _ = h.get("/")
        print(f"edge {h.edge} answered {status}")
        if h.mail_api:
            print(f"mail capture reachable: {len(h.mail_ids())} message(s)")
    except HarnessError as e:
        print(f"harness self-check FAILED: {e}")
        sys.exit(2)
```

Recorded runs. The self-test, offline:

```text
$ python3 harness.py --self-test
self-test: PASS (status in both wget forms, no-answer error, body off argv, body file cleaned, credential fallback, mail by new id, single extraction, route precondition incl. 500, empty POST, caller Content-Type, no-wget and scaled probe errors, MAIL_API check, runner exits)
```

A synthetic compose fixture: an `edge` service running busybox `httpd` on
port 8080 with a file at `/api/health` and three CGI scripts (one answers
500 with a body, one answers 302, one echoes the method, Content-Type,
Authorization and body it received); a `probe` service (busybox,
`SEED_PASSWORD=synthetic-only` and an empty `EMPTY_PW` in its environment); a
`nowget` service from a slim Python image with no `wget`; and a real smtp4dev
container as `mail`. The case file ran from another directory with
`COMPOSE_DIR` set. The `ERROR` lines are the expected loud failures (container
address elided):

```text
$ COMPOSE_DIR=<fixture> PROBE_SVC=probe EDGE=edge:8080 MAIL_API=http://mail:80 python3 case.py   # exit 1
  PASS  health
  PASS  unrouted 404
        500 -> 500 ''
  PASS  500 body
        302 -> 200 'ok\n'
  PASS  redirect
        echo -> 200 method=POST ctype=application/json len=28 auth=Bearer tok-1 | body={"password": "p@ss w\"rd$x"} |
  PASS  post body arrives
  PASS  post leaves no file
  PASS  cred container
        EMPTY_PW -> '' credential -> from-host-file
  PASS  cred empty->file
  ERROR cred absent
        HarnessError: NOPE_VAR is set neither in the 'probe' container nor in HOST_ENV_FILE (<path>/host.env)
        probe POST, body None -> method=POST ctype=application/json len= auth= | body= |
  PASS  probe POST no body
        probe POST text/plain -> method=POST ctype=text/plain len=3 auth= | body=a=1 |
  PASS  probe POST keeps ctype
        RouteDown: precondition /cgi-bin/err answered 500: route not alive
  PASS  precondition on 500
  ERROR no wget in probe
        HarnessError: probe container has no usable wget (exit 127): OCI runtime exec failed: exec failed: unable to start container process: exec: "wget": executable file not found in $PATH
  PASS  mail roundtrip
  ERROR mail old not matched
        HarnessError: no new mail for u1@example.test within 4s: the flow did not send it, or the capture server lost it
  ERROR renamed service
        HarnessError: no running container for service 'renamed' (is the stack up?)
$ PROBE_SVC=probe EDGE=edge:8080 MAIL_API=http://mail:80 python3 harness.py   # exit 0
edge edge:8080 answered 404
mail capture reachable: 1 message(s)
$ PROBE_SVC=probe EDGE=edge:9999 python3 harness.py                            # exit 2
harness self-check FAILED: no HTTP answer (wget exit 1): wget: can't connect to remote host (<address>): Connection refused
$ EDGE=edge:8080 python3 example_case.py                                       # exit 2
PROBE_SVC must be set
# after `docker compose up --scale probe=2`, any case                         (exit 1)
  ERROR health
        HarnessError: service 'probe' has 2 running containers; probe through a service that runs one
```

The same mapping as the oracle's wrapper (oracle page §4) was run against a
refused connection and raised the oracle's `ProbeError`, not `HarnessError`.

## 5. Pitfalls and sharp edges

- **Busybox `wget` does not save the body of an error answer.** On a non-2xx
  status it stops before reading the body, so `get` and `post_json` return an
  empty body for a 4xx or 5xx. Assert the status; to assert an error body,
  run a full HTTP client inside a container that has one.
- **Busybox `wget` follows redirects.** A 301, 302, 303, 307 or 308 is
  followed and the status returned is the final one, so a redirect cannot be
  asserted through it.
- **Busybox `wget` sends only GET and POST.** It has no method option. A
  PUT, PATCH or DELETE case needs a container with a full client; the
  transport adapter raises rather than send the wrong method.
- **A `--post-data` or `--post-file` body is sent up to its first NUL
  byte.** Busybox reads the file into the same buffer as `--post-data` and
  sends it with `strlen`. JSON from `json.dumps` never holds a raw NUL, but
  `probe` passes arbitrary bytes, so a binary body is cut short. Without a
  `Content-Type` header the body goes out as
  `application/x-www-form-urlencoded`; the harness sends `application/json`
  unless the `probe` caller names another type.
- **Busybox applets depend on the build.** `--header` and `--post-file`
  exist only when busybox is built with wget's long options. Check the probe
  image once with `wget --help`.
- **A bearer token on the command line is visible.** Busybox `wget` has no
  header-file option, so `--header "Authorization: Bearer …"` is in the
  argv of `docker exec` and of `wget` for the life of the call. Use
  short-lived tokens of synthetic accounts, and run the harness only where the
  process list is not shared with untrusted users.
- **Do not "simplify" to a host-side `curl`.** The host may have none, a
  published port may not exist, and a host-side probe tests a different
  network path from the one the services use.
- **A wait on mail by timestamp is a clock bug.** The capture server's
  received-date comes from its container's clock, and the trigger time from
  the host's. Snapshot the ids before the flow runs and wait for a new id.
- **A one-time code read from the database or the logs proves nothing about
  delivery.** The flow is "the user receives a mail"; only the capture
  server's API observes that.
- **A missing mail must fail.** A wait that times out and returns nothing
  turns a broken mail path into a pass. `wait_for_new_mail` raises. The
  application's side of the same failure needs its own case. A send failure
  that is caught and only logged makes a broken mail path look like success:
  the flow answers 201 and no mail ever leaves. Stop the capture server and
  assert that the flow that sends mail reports an error. If that case cannot
  be written yet, record it as absent; a delivery assertion alone does not
  cover it.
- **Never run a state-destroying flow on a shared account.** The rule and
  the case behind it live in `tool-corpus/testing/http-smoke-suite.md` §5.
  Log the cases in with a synthetic account per run
  (`tool-corpus/ops/disposable-test-identity-provisioner.md`), with
  recipients on a reserved test domain (`.test`, RFC 2606), so no real
  mailbox or personal data is involved.
- **A case that writes must survive its own re-run.** A case that creates a
  record with a fixed value in a unique column passes once and then fails on
  every later run, and the failure looks like a validation error (400), not a
  collision. Draw each such value at random within the column's constraint,
  retry on a collision, and accept the case only after it has gone green
  twice back to back against the same stack.
- **Match the generator's full alphabet.** A value drawn from a character
  set with symbols (a temporary password from letters, digits and `! @ $`)
  and captured by a class without them is truncated. The next step then fails
  as a wrong password (401), not as an extraction error. Anchor the pattern on
  the mail template and build the class from the generator's own character
  set.
- **Container and service names are defaults, not facts.** Every name comes
  from the environment; a renamed service fails at `container_id` with a
  message, not later with a confusing status. A scaled probe service (more
  than one running container) fails there too.

## 6. Tests that cover it

`harness.py --self-test` runs offline with a fake `docker` that records
every argv and asserts: the status is read from the `-S` form and from the
bare error-line form; a refused connection raises instead of returning a
status; a password in a POST body appears in no argv; the body file is
removed after a successful and after a failed request; a credential comes
from the container, then from the host env file (with `export` and quotes),
and a missing one raises naming both sources; the mail wait ignores a message
that was already there and raises when none comes; an ambiguous extraction
raises; a 404 and a 500 precondition raise `RouteDown`; `probe` sends a POST
with no body as a POST and keeps the caller's Content-Type; a probe container
with no `wget` and a scaled probe service raise with their own message;
`mail_html` without `MAIL_API` raises; `run` exits `2` for no cases, `0` for
a pass and `1` for a precondition error.

`tests/test-tool-corpus.sh` runs `--self-test` on the module extracted from
this page, then on a copy whose 404/500 precondition check is mutated out, and
fails if that copy still passes.

- **How to run the tests:** `python3 harness.py --self-test`; then the
  self-check (`python3 harness.py`) against the live stack.

## 7. References & neighbours

- **Related tools:** `tool-corpus/testing/http-smoke-suite.md` (the shell
  smoke suite, with the same in-container `wget` idiom for reachability and
  routing); `tool-corpus/testing/behavior-baseline-oracle.md` (uses `probe`
  as its transport when the edge is reachable only in-network);
  `tool-corpus/testing/live-contract-check-harness.md` (the black-box harness
  for a stack reached from outside, with RED and GREEN contract groups);
  `tool-corpus/ops/disposable-test-identity-provisioner.md` (the synthetic
  accounts the cases log in with).
- **Library pages:** `library-corpus/container/smtp4dev.md` (the capture
  server's API), `library-corpus/container/docker-compose.md`.
- **Sources:** distilled from practice (a driver behind a
  suite of live regression cases); busybox `networking/wget.c`
  (https://git.busybox.net/busybox/tree/networking/wget.c) for the status
  line, error line, redirect and option behaviour.

## 8. Changelog

- 2026-10-05 — created from a compose end-to-end driver and a
  credential-fallback idiom: the mail wait compares message ids instead of
  timestamps (falling back to "now" on an unparseable date hides a miss),
  reading a container variable distinguishes unset from a failed
  `docker exec` (one empty string for both hides the failure),
  the body file is created with `mktemp` under `umask 077`, a run with no
  cases exits `2`, and the route precondition got its own error class; by
  tool-smith.
- 2026-10-05 — review fixes: the route precondition accepts only 2xx by
  default (a 500 passed before); `probe` sends a POST with no body as a POST
  and keeps the caller's Content-Type; a probe container with no `wget`, a
  scaled probe service and `mail_html` without `MAIL_API` each raise with a
  plain message; the case example exits `2` on a configuration error; §2 names
  the oracle wrapper, the 20 s timeout and the 200-message window; §5 gained
  the generator-alphabet pitfall and points to the smoke suite for the
  shared-account rule; the live fixture run was redone; by tool-smith.
- 2026-10-05: §5 gained the swallowed-send-error case beside the
  missing-mail rule and the re-run rule for a case that writes; by
  docs-librarian.
