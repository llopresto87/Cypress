---
stack:
  - library-corpus/platform/azure-devops-rest
  - library-corpus/platform/azure-pipelines-yaml
---
# Tool: chained-pipeline-run-driver-azure-devops

> Project-agnostic capability notes, kept in the seed's tool corpus
> (`tool-corpus/README.md`). The Azure DevOps arm of
> `tool-corpus/ops/chained-pipeline-run-driver.md`: that page owns the
> stack-neutral design (allow-list, production refusal, retry split, visible
> wait, worst-case figure) and this page restates none of it. This page ships a
> portable implementation of that design against the Azure DevOps REST API.

## 0. Identity

- **Category:** ops
- **Name:** chained-pipeline-run-driver-azure-devops
- **Language / runtime:** python3, **stdlib only** (`urllib`, `json`,
  `zipfile`)
- **Stability:** **portable** for a project whose pipelines run on Azure
  DevOps Services. The allow-list, the production patterns, the pipeline
  resource alias and the organization are parameters; nothing is hard-coded.
  A plant supplies them, plus a status-only summary of its own artifacts if
  it wants one (§4).

## 1. What it does

Runs the two-stage chain of the neutral page on Azure DevOps:

1. optionally **preview** both pipelines (compile only, nothing created);
2. **queue** pipeline A on a ref with template parameters, or attach to an
   existing run of A;
3. **wait** for A by its run id, with a visible, bounded wait;
4. only if A succeeded, **queue** pipeline B with A's run bound as B's
   pipeline resource;
5. **wait** for B, list the failed timeline records of each run, and
   **download** B's artifacts;
6. exit 0 only when every run it waited for succeeded.

The whole interface, the exit codes and the reasons behind them are on the
neutral page. This page covers what is specific to Azure DevOps and the code.

## 2. Interface & invocation

```sh
AZURE_DEVOPS_EXT_PAT=... python3 chained-run-ado.py \
  --org-url https://dev.azure.com/<organization> --project <project> \
  --allow <name>=<pipeline id> --allow <name>=<pipeline id> \
  --refuse-pattern '<regex for production names>' \
  --pipeline-a <name> --self-ref refs/heads/<branch> [--params-json '<json>'] \
  --pipeline-b <name> --bind-alias <alias> [--b-self-ref <ref>] [--b-params-json '<json>'] \
  [--attach-run-id <id>] [--first-only] [--preview] [--out <dir>] \
  [--poll-interval 10] [--max-polls 180] [--net-retries 3] \
  [--net-retry-sleep 10] [--request-timeout 60] \
  [--token-env AZURE_DEVOPS_EXT_PAT] [--auth basic|bearer] [--api-version 7.1] [--dry-run]
python3 chained-run-ado.py --self-test
```

What differs from the neutral interface, and why:

- **`--allow NAME=ID`** is the allow-list, given per run or from a wrapper
  script the project commits. The pipeline id is the number in the
  pipeline's URL. There is still no option that takes a bare id for a run.
- **`--refuse-pattern`** is **required**, at least once. Each is a regular
  expression; every resolved string (organization, project, refs, every key
  and value at any depth of both parameter sets, the alias) is scanned before
  a client exists. A run without a production guard is a usage error, not a
  default.
- **`--bind-alias`** is the name B's YAML gives to A under
  `resources.pipelines`. Required unless `--first-only`.
- **`--token-env`** names the environment variable that holds the
  credential. The default is the one the CLI's DevOps extension reads
  (`library-corpus/platform/azure-cli.md`). `--auth basic` sends a personal
  access token as Basic with an empty user name; `--auth bearer` sends an
  Entra or pipeline job token (`library-corpus/platform/azure-devops-rest.md`,
  credentials). The credential needs the scope upstream lists for the run
  call, `vso.build_execute` (Build: read and execute). Without it the first
  real queue fails on permissions.
- **`--api-version`** is the REST `api-version` sent on every API call. The
  default is `7.1`, the version the calls below were checked against. Which
  version a project sends is the project's pin
  (`library-corpus/platform/azure-devops-rest.md`), so the wrapper of §4
  fixes it.
- **A ref for B is required** unless `--first-only`: `--b-self-ref`, or
  `--self-ref`, which B then shares. Without one, B compiles and runs the
  YAML of its default branch, the two-branch trap of §5. The tool refuses
  with exit 2 before any call, and in a dry run too.
- **`--attach-run-id`** must name a run of pipeline A. The tool reads the
  run's `definition.id` first and refuses with exit 2, before B is queued,
  when it is not A's allow-listed id. Otherwise B could be bound to any run,
  a production run included, past both guards.
- **`--preview`** calls the compile-only preview for A and B before anything
  is queued. B is previewed without the binding, because A's run does not
  exist yet.
- **Exit codes:** 0 every run waited for succeeded; 1 a run did not succeed,
  or the platform could not be read (an authentication failure, a lost queue
  response, an exhausted read retry, a wait past its bound); 2 a refusal or a
  usage error, always before any network call.

## 3. Approach / algorithm

### The calls

All under `<org-url>/<project>`, each with the one `api-version` the run
was given:

| Step | Call | Retried? |
|---|---|---|
| preview | `POST _apis/pipelines/{id}/preview`, run body plus `previewRun: true` | yes (creates nothing) |
| queue | `POST _apis/pipelines/{id}/runs`, run body; answer carries `id` | **never** |
| attach check | `GET _apis/build/builds/{runId}`; `definition.id` | yes |
| wait | `GET _apis/build/builds/{runId}`; `status`, `result`, `sourceVersion` | yes |
| failed records | `GET _apis/build/builds/{runId}/timeline`; Stage, Job and Task records whose `result` is not `succeeded` or `skipped` | yes |
| artifacts | `GET _apis/build/builds/{runId}/artifacts`, then each `resource.downloadUrl` (a zip) | yes |

The run body is `{"resources": {"repositories": {"self": {"refName":
<ref>}}}, "templateParameters": {...}}`. For B the tool adds
`"pipelines": {<alias>: {"runId": <A's run id>}}` under `resources`.

- **Waiting on the build resource.** The id the run call returns is used as
  the build id. Observed in practice, over many runs of one organization:
  the two ids are the same, and the build's `status` reaches `completed` with
  `result` `succeeded`, `partiallySucceeded`, `failed` or `canceled`. The tool
  treats only `succeeded` as success. The same observation covers the attach
  check: a pipeline's id is the `definition.id` of its runs. When A
  completes, the tool prints the first seven characters of its
  `sourceVersion`, the commit A built, which is the cheapest proof of the
  ref it ran.
- **Binding B to A by `runId`. Observed in practice, upstream silent.**
  Upstream's reference for the run body lists one field for a pipeline
  resource, `version` (a string). The `runId` field above was used for every
  chained run in the source project, and B's run read A's run through the
  predefined `resources.pipeline.<alias>.runID` variable. On adoption, prove
  it once: print that variable in B's first step and compare it with A's id.
  If the platform ever stops honouring `runId`, B silently uses the latest
  run of A, which is exactly the run this tool exists not to guess.

### Authentication failures are loud

Every API call refuses redirects. A `3xx`, or any answer whose content type
does not start with `application/json`, is reported as an authentication
failure (exit 1), never parsed as an empty result. The platform answers a bad
Basic personal access token (the default `--auth basic`) with `401` and an
empty body, and a bad Bearer token with a `302` to a sign-in page on another
host (`library-corpus/platform/azure-devops-rest.md`, general pitfalls). Both
end here. An artifact download that is not a zip (a sign-in page after a
followed redirect) is a failure too, never a traceback. The media
type is compared by prefix, because the platform adds parameters to it.

### The credential stays in the process

The token is read from the environment once and placed in an
**unredirected** header (`Request.add_unredirected_header`). It is never on
argv, in a URL or in output. The artifact download is the one call allowed
to follow a redirect, because the download URL may point at another host;
the unredirected header means a followed redirect never carries the
credential. Whether the download URL redirects is not recorded.

### Waiting and retries

As on the neutral page. Here `--net-retries` counts retries after the first
attempt, so one read makes at most `--net-retries` + 1 attempts, each bounded
by `--request-timeout`. The worst-case wait per run is printed at start from
the neutral page's formula. The defaults (3 retries, 10 s sleep, 60 s
timeout, 180 polls every 10 s) give 180 x (10 + 4 x 60 + 3 x 10) seconds, a
bound of 14 hours that only a dead network reaches. A normal run returns
after a few polls. Lower `--max-polls` when that bound is too loose.

```python
#!/usr/bin/env python3
"""chained-run-ado: queue pipeline A on Azure DevOps, wait for it, and only if
it succeeded queue pipeline B bound to A's run id, wait, and download B's
artifacts. Status-only summary.

  chained-run-ado.py --org-url URL --project NAME \
      --allow NAME=ID [--allow NAME=ID]... --refuse-pattern REGEX [...] \
      --pipeline-a NAME [--self-ref REF] [--params-json JSON] \
      [--pipeline-b NAME --bind-alias ALIAS [--b-self-ref REF] [--b-params-json JSON]] \
      [--attach-run-id ID] [--first-only] [--preview] [--out DIR] \
      [--poll-interval S] [--max-polls N] [--net-retries N] \
      [--net-retry-sleep S] [--request-timeout S] \
      [--token-env NAME] [--auth basic|bearer] [--dry-run]
  chained-run-ado.py --self-test

Exit 0 every run succeeded; 1 a run did not succeed; 2 refusal or usage error.
The credential is read from the environment variable --token-env, in process
only: never on argv, never in a URL, never printed. Stdlib only.
"""
from __future__ import annotations

import argparse
import base64
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

TRANSIENT = (urllib.error.URLError, ConnectionError, TimeoutError, OSError)
OK_RECORD = ("succeeded", "skipped", None)


class Refused(SystemExit):
    def __init__(self, msg):
        super().__init__(f"refused: {msg}")


class Failed(SystemExit):
    """A loud stop that is not a refusal (exit 1 semantics are set by main)."""


# --------------------------------------------------------------------- refusals
def parse_allow(items):
    table = {}
    for item in items or []:
        name, sep, pid = item.partition("=")
        if not sep or not name or not pid.isdigit():
            raise Refused(f"--allow wants NAME=ID with a numeric id, got {item!r}")
        table[name] = int(pid)
    if not table:
        raise Refused("no --allow entry: the tool queues only named, allow-listed pipelines")
    return table


def pipeline_id(table, name):
    if name not in table:
        raise Refused(f"pipeline {name!r} is not on the allow-list ({', '.join(sorted(table))})")
    return table[name]


def walk_strings(value):
    if isinstance(value, dict):
        for k, v in value.items():
            yield str(k)
            yield from walk_strings(v)
    elif isinstance(value, (list, tuple)):
        for v in value:
            yield from walk_strings(v)
    elif value is not None:
        yield str(value)


def refuse_production(patterns, *values):
    """Scan every resolved string, anywhere in the input, before any client exists."""
    for s in walk_strings(list(values)):
        for p in patterns:
            if p.search(s):
                raise Refused(f"value {s!r} matches production pattern {p.pattern!r}")


# ----------------------------------------------------------------------- client
class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise urllib.error.HTTPError(req.full_url, code,
                                     f"redirect refused (to {headers.get('Location', '?')}): "
                                     "treat as an authentication failure", headers, fp)


class AdoClient:
    """transport(method, url, body, binary) -> (status, content_type, bytes).
    Injectable, so tests never touch the network."""

    def __init__(self, org_url, project, token=None, auth="basic", transport=None,
                 retries=3, retry_sleep=10, timeout=60, out=sys.stdout, api_version="7.1"):
        self.base = f"{org_url.rstrip('/')}/{project}"
        # the plant's pin (--api-version), one value sent on every API call
        self.api = f"api-version={api_version}"
        self._token, self._auth = token, auth
        self.transport = transport or self._urllib
        self.retries, self.retry_sleep, self.timeout, self.out = retries, retry_sleep, timeout, out

    def _urllib(self, method, url, body=None, binary=False):
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(url, data=data, method=method)
        cred = (f"Basic {base64.b64encode((':' + self._token).encode()).decode()}"
                if self._auth == "basic" else f"Bearer {self._token}")
        # unredirected: a redirect followed for a download never carries the credential
        req.add_unredirected_header("Authorization", cred)
        req.add_header("Content-Type", "application/json")
        opener = (urllib.request.build_opener() if binary
                  else urllib.request.build_opener(_NoRedirect))
        try:
            with opener.open(req, timeout=self.timeout) as r:
                return r.status, r.headers.get("Content-Type", ""), r.read()
        except urllib.error.HTTPError as e:
            return e.code, e.headers.get("Content-Type", "") if e.headers else "", e.read() or b""

    def _url(self, path):
        return path if path.startswith("http") else f"{self.base}{path}"

    def _read(self, method, url, body=None, binary=False):
        """Idempotent call: retried on transient errors, at most retries+1 attempts."""
        for attempt in range(self.retries + 1):
            try:
                return self.transport(method, url, body, binary)
            except TRANSIENT as e:
                if attempt == self.retries:
                    raise Failed(f"unreachable after {attempt + 1} attempt(s): {type(e).__name__}")
                print(f"retry {type(e).__name__} (attempt {attempt + 1}/{self.retries}, "
                      f"sleeping {self.retry_sleep}s): {method} {url.split('?')[0]}",
                      file=self.out, flush=True)
                time.sleep(self.retry_sleep)

    @staticmethod
    def _json(status, ctype, payload, what):
        if status in (301, 302, 303, 307, 308) or not ctype.startswith("application/json"):
            raise Failed(f"{what}: HTTP {status}, {ctype or 'no content type'}: not JSON; "
                         "read as an authentication failure")
        data = json.loads(payload or b"{}")
        if status >= 400:
            raise Failed(f"{what}: HTTP {status}: {data.get('message', '')}")
        return data

    def get(self, path):
        return self._json(*self._read("GET", self._url(path)), f"GET {path.split('?')[0]}")

    def preview(self, pid, body):
        # compile only, creates nothing, so it may be retried like a read
        body = dict(body, previewRun=True)
        return self._json(*self._read("POST", self._url(f"/_apis/pipelines/{pid}/preview?{self.api}"), body),
                          f"preview {pid}")

    def queue(self, pid, body):
        # never retried: a lost response may hide a run that was created
        url = self._url(f"/_apis/pipelines/{pid}/runs?{self.api}")
        try:
            resp = self.transport("POST", url, body, False)
        except TRANSIENT as e:
            raise Failed(f"network error while queuing pipeline {pid}: {type(e).__name__}. "
                         "The run may or may not exist: check the pipeline's runs by hand "
                         "before retrying.")
        return self._json(*resp, f"queue {pid}")["id"]

    def wait(self, run_id, label, poll_interval, max_polls):
        last = None
        for i in range(max_polls):
            b = self.get(f"/_apis/build/builds/{run_id}?{self.api}")
            state = (b.get("status"), b.get("result"))
            if state != last:
                print(f"{label} {run_id} poll {i + 1}/{max_polls}: status={state[0]} "
                      f"result={state[1]}", file=self.out, flush=True)
                last = state
            if b.get("status") == "completed":
                return b
            time.sleep(poll_interval)
        raise Failed(f"{label} {run_id}: not completed after {max_polls} polls")

    def definition_of(self, run_id):
        """The pipeline (build definition) id a run belongs to."""
        b = self.get(f"/_apis/build/builds/{run_id}?{self.api}")
        return (b.get("definition") or {}).get("id")

    def failed_records(self, run_id):
        t = self.get(f"/_apis/build/builds/{run_id}/timeline?{self.api}")
        return [(r.get("type"), r.get("name"), r.get("result"))
                for r in (t.get("records") or [])
                if r.get("type") in ("Stage", "Job", "Task") and r.get("result") not in OK_RECORD]

    def download_artifacts(self, run_id, dest: Path):
        dest.mkdir(parents=True, exist_ok=True)
        got = []
        for a in self.get(f"/_apis/build/builds/{run_id}/artifacts?{self.api}").get("value", []):
            status, _, payload = self._read("GET", a["resource"]["downloadUrl"], binary=True)
            if status >= 400:
                raise Failed(f"artifact {a.get('name')}: HTTP {status}")
            try:
                with zipfile.ZipFile(io.BytesIO(payload)) as z:
                    z.extractall(dest)      # extractall drops absolute and '..' parts
                    got.append((a.get("name"), len(z.namelist())))
            except zipfile.BadZipFile:
                raise Failed(f"artifact {a.get('name')}: the download is not a zip "
                             "(a sign-in page after a redirect, for example)") from None
        return got


# -------------------------------------------------------------------------- cli
def build_parser():
    ap = argparse.ArgumentParser(prog="chained-run-ado.py")
    ap.add_argument("--org-url")
    ap.add_argument("--project")
    ap.add_argument("--allow", action="append", default=[], metavar="NAME=ID")
    ap.add_argument("--refuse-pattern", action="append", default=[], metavar="REGEX")
    ap.add_argument("--pipeline-a")
    ap.add_argument("--self-ref")
    ap.add_argument("--params-json", default="{}")
    ap.add_argument("--pipeline-b")
    ap.add_argument("--bind-alias", help="the pipeline resource alias B's YAML declares for A")
    ap.add_argument("--b-self-ref")
    ap.add_argument("--b-params-json", default="{}")
    ap.add_argument("--attach-run-id", type=int)
    ap.add_argument("--first-only", action="store_true")
    ap.add_argument("--preview", action="store_true")
    ap.add_argument("--out", type=Path, default=Path("chained-run-artifacts"))
    ap.add_argument("--poll-interval", type=int, default=10)
    ap.add_argument("--max-polls", type=int, default=180)
    ap.add_argument("--net-retries", type=int, default=3)
    ap.add_argument("--net-retry-sleep", type=int, default=10)
    ap.add_argument("--request-timeout", type=int, default=60)
    ap.add_argument("--token-env", default="AZURE_DEVOPS_EXT_PAT")
    ap.add_argument("--auth", choices=("basic", "bearer"), default="basic")
    ap.add_argument("--api-version", default="7.1",
                    help="the REST api-version the plant pins, sent on every API call")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    return ap


def run_body(self_ref, params, bind=None):
    body = {"resources": {"repositories": {"self": {"refName": self_ref}}} if self_ref else {},
            "templateParameters": params}
    if bind:
        alias, run_id = bind
        body["resources"]["pipelines"] = {alias: {"runId": run_id}}
    return body


def worst_case_seconds(a):
    return a.max_polls * (a.poll_interval + (a.net_retries + 1) * a.request_timeout
                          + a.net_retries * a.net_retry_sleep)


def main(argv=None, client=None, out=sys.stdout):
    a = build_parser().parse_args(argv)
    if a.self_test:
        self_test()
        return 0
    try:
        if not (a.org_url and a.project and a.pipeline_a):
            raise Refused("--org-url, --project and --pipeline-a are required")
        if not a.refuse_pattern:
            raise Refused("at least one --refuse-pattern is required: the production "
                          "guard is not optional")
        table = parse_allow(a.allow)
        patterns = [re.compile(p) for p in a.refuse_pattern]
        pa = pipeline_id(table, a.pipeline_a)
        pb = None
        if not a.first_only:
            if not (a.pipeline_b and a.bind_alias):
                raise Refused("--pipeline-b and --bind-alias are required unless --first-only")
            pb = pipeline_id(table, a.pipeline_b)
        if not a.attach_run_id and not a.self_ref:
            raise Refused("--self-ref is required unless --attach-run-id is given")
        if not a.first_only and not (a.b_self_ref or a.self_ref):
            raise Refused("a ref for B is required unless --first-only (--b-self-ref or "
                          "--self-ref): without one B runs its default branch's YAML")
        params_a, params_b = json.loads(a.params_json), json.loads(a.b_params_json)
        b_ref = a.b_self_ref or a.self_ref
        refuse_production(patterns, a.org_url, a.project, a.self_ref, b_ref,
                          params_a, params_b, a.bind_alias)
    except Refused as r:
        print(r.code, file=sys.stderr)
        return 2
    except (json.JSONDecodeError, re.error) as e:
        print(f"refused: malformed input: {e}", file=sys.stderr)
        return 2

    print(f"worst-case wait per run: {worst_case_seconds(a)}s "
          f"(max_polls x (poll + (retries+1) x timeout + retries x retry_sleep))",
          file=out, flush=True)
    if a.dry_run:
        if a.attach_run_id:
            print(f"dry-run: would attach {a.pipeline_a} run {a.attach_run_id}", file=out)
        else:
            print(f"dry-run: would queue {a.pipeline_a} ({pa}): "
                  + json.dumps(run_body(a.self_ref, params_a), sort_keys=True), file=out)
        if pb:
            print(f"dry-run: would then queue {a.pipeline_b} ({pb}) bound to that run as "
                  f"resources.pipelines.{a.bind_alias}", file=out)
        return 0

    try:
        if client is None:
            token = os.environ.get(a.token_env)
            if not token:
                print(f"refused: {a.token_env} is not set in the environment", file=sys.stderr)
                return 2
            client = AdoClient(a.org_url, a.project, token, a.auth, retries=a.net_retries,
                               retry_sleep=a.net_retry_sleep, timeout=a.request_timeout, out=out,
                               api_version=a.api_version)
        if a.preview:
            if not a.attach_run_id:
                client.preview(pa, run_body(a.self_ref, params_a))
                print(f"{a.pipeline_a} preview: compiled", file=out, flush=True)
            if pb:
                client.preview(pb, run_body(b_ref, params_b))
                print(f"{a.pipeline_b} preview: compiled", file=out, flush=True)
        if a.attach_run_id:
            run_a = a.attach_run_id
            owner = client.definition_of(run_a)
            if owner != pa:
                print(f"refused: run {run_a} belongs to pipeline {owner}, not to "
                      f"{a.pipeline_a} ({pa}): B is never bound to a run outside the "
                      "allow-list", file=sys.stderr)
                return 2
            print(f"{a.pipeline_a} attach {run_a}", file=out, flush=True)
        else:
            run_a = client.queue(pa, run_body(a.self_ref, params_a))
            print(f"{a.pipeline_a} queued {run_a}", file=out, flush=True)
        ba = client.wait(run_a, a.pipeline_a, a.poll_interval, a.max_polls)
        # the short commit A built: the cheapest proof of which ref it ran
        print(f"{a.pipeline_a} {run_a} {ba.get('result')} {str(ba.get('sourceVersion') or '?')[:7]}",
              file=out, flush=True)
        for rec in client.failed_records(run_a):
            print(" | ".join(map(str, rec)), file=out)
        if ba.get("result") != "succeeded":
            print(f"{a.pipeline_a} {run_a} did not succeed: {ba.get('result')}", file=sys.stderr)
            return 1
        if a.first_only:
            return 0
        run_b = client.queue(pb, run_body(b_ref, params_b, bind=(a.bind_alias, run_a)))
        print(f"{a.pipeline_b} queued {run_b} bound to {a.pipeline_a} {run_a}", file=out, flush=True)
        bb = client.wait(run_b, a.pipeline_b, a.poll_interval, a.max_polls)
        print(f"{a.pipeline_b} {run_b} {bb.get('result')}", file=out, flush=True)
        for rec in client.failed_records(run_b):
            print(" | ".join(map(str, rec)), file=out)
        for name, n in client.download_artifacts(run_b, a.out):
            print(f"artifact {name}: {n} file(s)", file=out)
        return 0 if bb.get("result") == "succeeded" else 1
    except Failed as f:
        print(f.code, file=sys.stderr)
        return 1


# -------------------------------------------------------------------- self-test
class FakeTransport:
    """Scripted platform: per-run status sequences, recorded calls, injectable faults."""

    def __init__(self, results=None, fail_queue=False, flaky_get=0, html=False,
                 empty401=False, not_zip=False, defs=None):
        self.calls, self.next_id = [], 100
        self.results = results or {}
        self.polls = {}
        self.defs = dict(defs or {77: 11})       # run id -> pipeline id
        self.fail_queue, self.flaky_get, self.html = fail_queue, flaky_get, html
        self.empty401, self.not_zip = empty401, not_zip

    def __call__(self, method, url, body=None, binary=False):
        self.calls.append((method, url, body))
        J = "application/json; charset=utf-8; api-version=7.1"
        if self.html:                 # a bad Bearer token: redirect to a sign-in page
            return 302, "text/html", b"<html>sign in</html>"
        if self.empty401:             # a bad Basic PAT: 401 with an empty body
            return 401, "", b""
        if method == "GET" and self.flaky_get:
            self.flaky_get -= 1
            raise OSError("transient")
        if method == "POST" and "/preview" in url:
            return 200, J, json.dumps({"finalYaml": "steps: []"}).encode()
        if method == "POST":
            if self.fail_queue:
                raise OSError("lost response")
            self.next_id += 1
            self.defs[self.next_id] = int(re.search(r"/pipelines/(\d+)/runs", url).group(1))
            return 200, J, json.dumps({"id": self.next_id, "state": "inProgress"}).encode()
        m = re.search(r"/builds/(\d+)(/\w+)?", url)
        if m and m.group(2) is None:
            rid = int(m.group(1))
            n = self.polls[rid] = self.polls.get(rid, 0) + 1
            res = self.results.get(rid, "succeeded")
            done = n >= 2
            return 200, J, json.dumps({"id": rid, "status": "completed" if done else "inProgress",
                                       "result": res if done else None,
                                       "definition": {"id": self.defs.get(rid)},
                                       "sourceVersion": "0123456789abcdef"}).encode()
        if m and m.group(2) == "/timeline":
            return 200, J, json.dumps({"records": [{"type": "Task", "name": "scan", "result": "failed"}]
                                       if self.results.get(int(m.group(1))) == "failed" else []}).encode()
        if m and m.group(2) == "/artifacts":
            return 200, J, json.dumps({"value": [{"name": "report", "resource":
                                       {"downloadUrl": "https://example.invalid/a.zip"}}]}).encode()
        if url.endswith("a.zip") and self.not_zip:
            return 200, "text/html", b"<html>sign in</html>"
        if url.endswith("a.zip"):
            buf = io.BytesIO()
            with zipfile.ZipFile(buf, "w") as z:
                z.writestr("report/summary.json", '{"secretish": "never printed"}')
            return 200, "application/zip", buf.getvalue()
        return 404, J, b'{"message": "not found"}'


def self_test():
    import contextlib
    import tempfile
    tmp = Path(tempfile.mkdtemp())
    base = ["--org-url", "https://dev.azure.com/example-org", "--project", "example",
            "--allow", "build=11", "--allow", "verify=12", "--refuse-pattern", r"(?i)\bprod",
            "--pipeline-a", "build", "--pipeline-b", "verify", "--bind-alias", "upstream",
            "--self-ref", "refs/heads/topic", "--poll-interval", "0", "--max-polls", "5",
            "--out", str(tmp / "art")]

    def go(args, fake=None):
        out, err = io.StringIO(), io.StringIO()
        client = None
        if fake is not None:
            client = AdoClient("https://dev.azure.com/example-org", "example", "t",
                               transport=fake, retries=2, retry_sleep=0, out=out)
        with contextlib.redirect_stderr(err):
            rc = main(args, client=client, out=out)
        return rc, out.getvalue(), err.getvalue()

    # the parser never grows a bare-id option
    opts = {o for act in build_parser()._actions for o in act.option_strings}
    assert not any(re.search(r"(?:pipeline|definition)-?id\b", o) for o in opts), opts
    # allow-list and production refusals fire before any transport call
    for args in (base + ["--pipeline-a", "other"],
                 base + ["--params-json", '{"pool": "Prod-agents"}'],
                 base + ["--b-params-json", '{"deep": {"list": ["x", "prod-group"]}}'],
                 [a if a != "refs/heads/topic" else "refs/heads/prod-hotfix" for a in base],
                 [a for a in base if a not in ("--refuse-pattern", r"(?i)\bprod")],
                 base + ["--allow", "bad=notanumber"]):
        fake = FakeTransport()
        rc, _, err = go(args, fake)
        assert rc == 2 and "refused" in err and fake.calls == [], (args, rc, err, fake.calls)
    # dry run: no client, no credential
    os.environ.pop("CHAINED_RUN_SELFTEST_TOKEN", None)
    rc, out, _ = go(base + ["--dry-run", "--token-env", "CHAINED_RUN_SELFTEST_TOKEN"])
    assert rc == 0 and "would queue build (11)" in out and "upstream" in out, out
    # full chain: A queued, waited, B queued bound to A's id, waited, artifacts downloaded
    fake = FakeTransport()
    rc, out, _ = go(base + ["--preview"], fake)
    assert rc == 0, out
    posts = [c for c in fake.calls if c[0] == "POST"]
    assert [("/preview" in u) for _, u, _ in posts] == [True, True, False, False], posts
    assert posts[3][2]["resources"]["pipelines"] == {"upstream": {"runId": 101}}, posts[3]
    assert "/_apis/pipelines/12/runs" in posts[3][1]
    assert all("api-version=" in u for _, u, _ in fake.calls if "a.zip" not in u)
    assert "artifact report: 1 file(s)" in out and "never printed" not in out, out
    assert (tmp / "art" / "report" / "summary.json").is_file()
    # progress: first poll visible, repeats suppressed, worst case printed with the formula
    assert out.count("build 101 poll 1/5") == 1 and "build 101 poll 2/5: status=completed" in out, out
    assert "worst-case wait per run: 1350s" in out, out   # 5 x (0 + (3+1) x 60 + 3 x 10)
    # first-only never queues B; a failed A stops the chain before B
    fake = FakeTransport()
    rc, _, _ = go(base + ["--first-only"], fake)
    assert rc == 0 and sum(1 for c in fake.calls if c[0] == "POST") == 1
    fake = FakeTransport(results={101: "failed"})
    rc, out, _ = go(base, fake)
    assert rc == 1 and sum(1 for c in fake.calls if c[0] == "POST") == 1 and "Task | scan | failed" in out
    # attach mode: no queue for A
    fake = FakeTransport()
    rc, out, _ = go(base + ["--attach-run-id", "77"], fake)
    assert rc == 0 and "build attach 77" in out
    assert [c[2]["resources"]["pipelines"] for c in fake.calls if c[0] == "POST"] == [{"upstream": {"runId": 77}}]
    # attach to a run of another pipeline: refused before B is queued
    fake = FakeTransport(defs={77: 99})
    rc, _, err = go(base + ["--attach-run-id", "77"], fake)
    assert rc == 2 and "belongs to pipeline 99" in err and not [c for c in fake.calls if c[0] == "POST"], err
    # attach with no ref for B: refused before any call (B would run its default branch)
    no_ref = [x for x in base if x not in ("--self-ref", "refs/heads/topic")]
    fake = FakeTransport()
    rc, _, err = go(no_ref + ["--attach-run-id", "77"], fake)
    assert rc == 2 and "a ref for B is required" in err and fake.calls == [], err
    rc, _, err = go(no_ref + ["--attach-run-id", "77", "--dry-run"])
    assert rc == 2 and "a ref for B is required" in err, err
    # A's short commit is printed once A completes
    fake = FakeTransport()
    rc, out, _ = go(base + ["--first-only"], fake)
    assert "build 101 succeeded 0123456" in out, out
    # reads retry with attempt/budget named; the queue call is never retried
    fake = FakeTransport(flaky_get=2)
    rc, out, _ = go(base + ["--first-only"], fake)
    assert rc == 0 and "retry OSError (attempt 1/2" in out and "attempt 2/2" in out, out
    fake = FakeTransport(fail_queue=True)
    rc, _, err = go(base, fake)
    assert rc == 1 and "may or may not exist" in err
    assert sum(1 for c in fake.calls if c[0] == "POST") == 1
    # a redirect or an HTML body is an authentication failure, never an empty result:
    # a bad Bearer token is redirected, a bad Basic PAT gets 401 with an empty body
    rc, _, err = go(base + ["--first-only"], FakeTransport(html=True))
    assert rc == 1 and "authentication failure" in err, err
    rc, _, err = go(base + ["--first-only"], FakeTransport(empty401=True))
    assert rc == 1 and "HTTP 401" in err and "authentication failure" in err, err
    # an artifact that is not a zip is a loud failure, not a traceback
    rc, _, err = go(base, FakeTransport(not_zip=True))
    assert rc == 1 and "not a zip" in err, err
    # the api-version pin is a parameter, sent on every API call
    seen = []
    c = AdoClient("u", "p", "t", api_version="7.2", out=io.StringIO(), transport=lambda m, u, b, bi: (
        seen.append(u) or (200, "application/json", b'{"status": "completed", "result": "succeeded"}')))
    c.wait(5, "x", 0, 1)
    assert seen and all("api-version=7.2" in u for u in seen), seen
    # the real terminal shape completes on the first poll
    c = AdoClient("u", "p", "t", transport=lambda m, u, b, bi: (
        200, "application/json", b'{"id": 5, "status": "completed", "result": "succeeded"}'),
        out=io.StringIO())
    assert c.wait(5, "x", 0, 1)["result"] == "succeeded"
    print("self-test: PASS (no bare-id option, refusals before transport, dry run offline, "
          "full chain bound by run id, first-only, failed A stops, attach, attach to another "
          "pipeline refused, no ref for B refused, A's commit printed, read retry, no queue "
          "retry, redirect and 401 = auth failure, not-a-zip artifact, api-version parameter, "
          "terminal shape)")


if __name__ == "__main__":
    sys.exit(main())
```

Recorded run of the self-test, then of the script against a synthetic local
server that answers the calls above like the platform (JSON with a
parameterized content type, a run's `definition.id` and `sourceVersion`, a
`401` with an empty body for a wrong Basic token, a `302` to another host for
a wrong Bearer token, a zip artifact behind a redirect):

```text
$ python3 chained-run-ado.py --self-test
self-test: PASS (no bare-id option, refusals before transport, dry run offline, full chain bound by run id, first-only, failed A stops, attach, attach to another pipeline refused, no ref for B refused, A's commit printed, read retry, no queue retry, redirect and 401 = auth failure, not-a-zip artifact, api-version parameter, terminal shape)
$ ARGS="--org-url http://127.0.0.1:18766/example-org --project example --allow build=11 --allow verify=12 --refuse-pattern '(?i)\bprod' --pipeline-a build --pipeline-b verify --bind-alias upstream --self-ref refs/heads/topic --poll-interval 1 --max-polls 10 --net-retries 1 --net-retry-sleep 1 --request-timeout 5 --out art"
$ python3 chained-run-ado.py $ARGS --params-json '{"pool": "prod-agents"}'
refused: value 'prod-agents' matches production pattern '(?i)\\bprod'
exit 2
$ python3 chained-run-ado.py $ARGS --dry-run
worst-case wait per run: 120s (max_polls x (poll + (retries+1) x timeout + retries x retry_sleep))
dry-run: would queue build (11): {"resources": {"repositories": {"self": {"refName": "refs/heads/topic"}}}, "templateParameters": {}}
dry-run: would then queue verify (12) bound to that run as resources.pipelines.upstream
exit 0
$ AZURE_DEVOPS_EXT_PAT=synthetic-token python3 chained-run-ado.py $ARGS --preview
worst-case wait per run: 120s (max_polls x (poll + (retries+1) x timeout + retries x retry_sleep))
build preview: compiled
verify preview: compiled
build queued 201
build 201 poll 1/10: status=inProgress result=None
build 201 poll 2/10: status=completed result=succeeded
build 201 succeeded 9f8e7d6
verify queued 202 bound to build 201
verify 202 poll 1/10: status=inProgress result=None
verify 202 poll 2/10: status=completed result=succeeded
verify 202 succeeded
artifact report: 1 file(s)
exit 0
$ AZURE_DEVOPS_EXT_PAT=wrong-token python3 chained-run-ado.py $ARGS --first-only
worst-case wait per run: 120s (max_polls x (poll + (retries+1) x timeout + retries x retry_sleep))
queue 11: HTTP 401, no content type: not JSON; read as an authentication failure
exit 1
$ AZURE_DEVOPS_EXT_PAT=wrong-token python3 chained-run-ado.py $ARGS --first-only --auth bearer
worst-case wait per run: 120s (max_polls x (poll + (retries+1) x timeout + retries x retry_sleep))
queue 11: HTTP 302, text/html: not JSON; read as an authentication failure
exit 1
$ AZURE_DEVOPS_EXT_PAT=synthetic-token python3 chained-run-ado.py $ARGS --attach-run-id 202
worst-case wait per run: 120s (max_polls x (poll + (retries+1) x timeout + retries x retry_sleep))
refused: run 202 belongs to pipeline 12, not to build (11): B is never bound to a run outside the allow-list
exit 2
$ find art -type f
art/report/status.json
```

The wrong-token runs went to two server instances, one per answer. With
`--self-ref` removed from `$ARGS`, `--attach-run-id 77` exits 2 with "a ref
for B is required unless --first-only". The server logged the four POSTs of
the successful run. The last one is B's queue call with the binding. The
artifact URL redirected once; the server saw the credential on the first hop
and none on the followed one.

```text
POST /example-org/example/_apis/pipelines/11/preview {"repositories": {"self": {"refName": "refs/heads/topic"}}}
POST /example-org/example/_apis/pipelines/12/preview {"repositories": {"self": {"refName": "refs/heads/topic"}}}
POST /example-org/example/_apis/pipelines/11/runs {"repositories": {"self": {"refName": "refs/heads/topic"}}}
POST /example-org/example/_apis/pipelines/12/runs {"pipelines": {"upstream": {"runId": 201}}, "repositories": {"self": {"refName": "refs/heads/topic"}}}
```

## 4. Portable vs blueprint

- **Portable (use as-is):** the whole script: allow-list and production
  refusal by parameter, dry run with no client, preview, queue without retry,
  bounded and visible wait, failed-record listing, artifact download with the
  credential kept off redirects, redirect and non-JSON as authentication
  failure, status-only output.
- **Write per project:** a short wrapper or task-runner entry that fixes the
  project's `--allow`, `--refuse-pattern`, `--bind-alias`, `--api-version`,
  organization and project, so nobody types them per run; and, if the project's artifacts
  include a result record, a summary that prints only ids, statuses and
  reasons from it, never report content.
- **Adopting notes:**
  - The production patterns are the project's names for production agent
    pools, queues, variable groups, environments and hosts. Write them to
    match anywhere in a string, and test them against the real names once.
  - A plant whose operators also need read-only checks on a host after a run
    keeps those in a separate tool. One tool, one operation.

## 5. Pitfalls and sharp edges

- **The neutral page's pitfalls all apply** (silent waits, the injected
  transport that makes retry flags no-ops, lost queue responses, `tail`,
  completion by shape). Read them there.
- **The binding field is observed, not documented** (§3). Prove it once per
  project, and again when the platform's REST version pin moves.
- **A parameter the YAML does not declare is rejected at queue time**, with a
  `400` and a message. The tool reports it and exits 1; nothing was queued.
  Use `--preview` to see the same error without a queue attempt.
- **The self ref selects the YAML that runs.** The `refName` decides which
  version of the pipeline definition is compiled, as well as which code is
  checked out (`skill-corpus/drive-hosted-cicd-cli.md`, the two-branch
  trap). Preview against the same ref you queue. That is why the tool
  refuses to queue B without a ref, and prints the commit A built.
- **A token in the shell history is a leaked token.** Export it from a secret
  store into the environment of the one command, never type it inline in a
  shared shell.

## 6. Tests that cover it

The self-test in the script above (`chained-run-ado.py --self-test`) runs
against a scripted fake transport (no network) and asserts: the parser has
no option that takes a bare pipeline or definition id; an unknown pipeline
name, a production name in a parameter, in a nested list of B's parameters
and in the ref, a missing `--refuse-pattern`, and a malformed `--allow` each
exit 2 with zero transport calls; `--dry-run` with no credential set exits 0
and names both pipelines; the full chain with `--preview` makes preview,
preview, queue A, queue B in that order, binds B with
`{"<alias>": {"runId": <A's id>}}`, sends `api-version` on every API call,
downloads and extracts the artifact, and prints no artifact content; the
first poll is printed once and the completed state once; the worst-case line
matches the formula for the given bounds; `--first-only` queues once; a
failed A queues once, lists its failed task, and exits 1; attach mode queues
only B, bound to the attached id; attaching to a run of another pipeline
exits 2 before B is queued; a missing ref for B exits 2 with zero calls, in
a dry run too; A's short commit is printed when A completes; two transient
read errors are retried with
the attempt and the budget named; a lost queue response is not retried and
says the run may or may not exist; a `302` with an HTML body (the Bearer
case) and a `401` with an empty body (the Basic case) each exit 1 as an
authentication failure; an artifact that is not a zip exits 1 with a
message; `--api-version` reaches every API call; the platform's terminal
shape completes on the first poll.

- **How to run the tests:** `python3 chained-run-ado.py --self-test` (exit 0
  on pass; an `AssertionError` names the case that failed).

## 7. References & neighbours

- **Related tools:** `tool-corpus/ops/chained-pipeline-run-driver.md` (the
  design this implements); `skill-corpus/drive-hosted-cicd-cli.md` (session
  login, the two-branch trap, proving which ref a run built).
- **Library notes:** `library-corpus/platform/azure-devops-rest.md` (calls,
  credentials, redirects, throttling); `library-corpus/platform/azure-cli.md`
  (the credential variable); `library-corpus/platform/azure-pipelines-yaml.md`
  (pipeline resources and their predefined variables).
- **Sources:** distilled from practice. The run and
  preview body fields were checked against the upstream reference
  (https://learn.microsoft.com/rest/api/azure/devops/pipelines/runs/run-pipeline,
  version 7.1, retrieved 2026-10-05), which documents `version`, not
  `runId`, for a pipeline resource.

## 8. Changelog

- 2026-10-05: created. The allow-list, production patterns, alias,
  organization, project and credential variable are parameters; the production guard became
  required; the read retry counts retries after the first attempt; redirects
  are refused on API calls and the credential is kept off followed
  redirects; the project-specific summary and host-probe mode were left out.
- 2026-10-05: review fixes. `stack:` also names the pipelines YAML page, so
  a project with a pipeline file is offered this page. The driver refuses to
  queue B without a ref; an attached run must belong to A;
  `api-version` is a parameter; the Basic `401` case is tested, and the
  `302` case is labelled as the Bearer case; the token scope is named; A's
  commit is printed; an artifact that is not a zip fails with a message.
