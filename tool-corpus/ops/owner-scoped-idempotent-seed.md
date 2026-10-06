---
stack:
  - library-corpus/container/mysql
  - library-corpus/container/postgres
---
# Tool: owner-scoped-idempotent-seed

> Project-agnostic capability notes, kept in the seed's tool corpus
> (`tool-corpus/README.md`). Two parts. The seed itself is a **BLUEPRINT**: the
> reset-then-insert method and its rules are portable, but every table, column
> and foreign key is the adopting project's, so the page gives the method, a
> worked SQL skeleton and the per-engine idioms. The **seeded-world API
> verifier** that proves the seed through the real API is a complete stdlib
> script with its own fixture self-test.

## 0. Identity

- **Category:** ops
- **Name:** owner-scoped-idempotent-seed
- **Language / runtime:** SQL for the target engine, applied with that
  engine's own client; python3 (stdlib only) for the verifier.
- **Stability:** **portable** for the verifier (§3.3), which ran its
  self-test when it was folded in (§6). The seed (§3.1, §3.2) is a blueprint:
  the skeleton shows the shape, and the engine idioms in §3.2 are taken from
  each client's and server's own documentation.

## 1. What it does

Puts a coherent, synthetic data world into a running database so that people
and tests can use every screen of a deployed system: each role, each value of
each status, at least one broken entity per domain, empty and red paths. It is
safe to re-run: every run removes exactly the rows the previous run added and
puts them back, and never touches a real row. Then it proves the world works
by driving the real API the way each screen does.

It exists because the two easy alternatives fail. Clicking data in by hand
cannot be repeated and leaves no record. A dump restored over the database
destroys real rows. A seed that marks its own rows can be removed, re-applied
and audited.

## 2. Interface & invocation

```sh
# 0. once, before the first apply: a dump of the target database
# 1. apply the seed in one transaction with the engine's own client
mysql --default-character-set=utf8mb4 -u "$DB_USER" -p "$DB_NAME" < seed.sql
psql -v ON_ERROR_STOP=1 --single-transaction -f seed.sql "$DATABASE_URL"
# 2. prove the world through the API
DEMO_PASSWORD=... seeded-world-verifier.py --plan verify-plan.json --base-url <url>
```

- **Seed inputs:** the seed file; the database credentials from the
  environment the deploy already uses. The file itself is self-contained: no
  parameter, no id written by hand.
- **Seed outputs:** the seeded rows; a final count per seeded table compared
  with the counts the seed expects (§3.1, step 6). A non-zero client exit
  means the transaction rolled back and the database is unchanged.
- **Verifier inputs:** a JSON plan (§3.3) and a base URL; any secret the plan
  needs is written `${NAME}` and read from the environment.
- **Verifier outputs and exit codes:** one `PASS` or `FAIL` line per login and
  check, a summary; exit 0 all passed, 1 any failed, 2 a usage error, an
  unreadable plan, a missing environment variable or a plan with no check.
- **Preconditions:** a current dump; the live schema read before writing the
  seed (step 0 below); a way to run the engine client against the target.

## 3. Approach / algorithm

### 3.1 The seed

0. **Read the live schema first.** Tables, columns, foreign keys and their
   delete rules, how enums are stored (ordinal integers or names), how
   passwords are hashed, every login mode, and anything date-keyed: a
   scheduled job that purges rows older than today empties a world seeded with
   fixed past dates by the next morning. Use the schema the database has, not
   the one the code or a document says it should have.
1. **Mark every seeded row with an owner.** Use an audit column the schema
   already has (a created-by or owner column) and give it one fixed marker
   value. With no such column, use a marker in a natural key (a fixed prefix
   on a code or name column) or a side table that records the table and id of
   every row the seed inserts. Without a marker the seed cannot remove only
   its own rows.
2. **Open with a reset block that deletes only marked rows, children first.**
   Join tables first (their foreign keys usually restrict and block a parent
   delete), then each child before its parent, up to the roots. When deleting
   a parent cascades into a table that another restrict key protects (users
   under a tenant, blocked by a user-to-role join), delete the protected rows
   explicitly before the parent.
3. **Unlink real rows from seeded parents, then re-link them.** A real row
   (a pre-existing admin account) that points at a seeded parent would be
   deleted or would block the reset. Set its reference to NULL in the reset
   block, and set it again after the parents are re-inserted.
4. **Insert parent first, chaining generated ids through variables.** Every
   child row takes its parent's id from the variable set right after the
   parent's insert. Never write an id literal: auto-increment never rewinds,
   so ids move on every re-apply.
5. **Run it all in one transaction.** On any error the whole run rolls back
   and the database is as it was. Keep schema changes out of the seed file;
   some engines commit implicitly on a schema statement.
6. **End with a count check.** Count the marked rows per table and compare
   with what the seed inserted. Inside the transaction, a mismatch can abort
   it (§3.2 lists how per engine); outside it, the verifier's first checks
   assert the same counts through the API.

A skeleton in the MySQL dialect (two tables, one join table, one real row
re-linked); the names are examples:

```sql
SET FOREIGN_KEY_CHECKS = 1;  -- a session with checks off would orphan rows silently
START TRANSACTION;
-- reset: marked rows only, join tables first, children before parents
DELETE ur FROM user_role ur JOIN app_user u ON ur.user_id = u.id
  WHERE u.created_by = 'demo-seed';
DELETE FROM app_user WHERE created_by = 'demo-seed';
UPDATE app_user u JOIN site s ON u.site_id = s.id
  SET u.site_id = NULL
  WHERE s.created_by = 'demo-seed' AND u.created_by <> 'demo-seed';
DELETE FROM site WHERE created_by = 'demo-seed';
-- insert: parents first, ids chained through unquoted user variables
INSERT INTO site (created_by, name) VALUES ('demo-seed', 'Site A');
SET @site_a = LAST_INSERT_ID();
INSERT INTO app_user (created_by, username, password_hash, site_id)
  VALUES ('demo-seed', 'demo.operator', '<hash of the demo password>', @site_a);
SET @u_op = LAST_INSERT_ID();
INSERT INTO user_role (user_id, role_id)
  SELECT @u_op, id FROM role WHERE name = 'OPERATOR';
UPDATE app_user SET site_id = @site_a
  WHERE username = 'admin' AND created_by <> 'demo-seed';
COMMIT;
SELECT 'site' t, COUNT(*) n FROM site WHERE created_by = 'demo-seed'
UNION ALL SELECT 'app_user', COUNT(*) FROM app_user WHERE created_by = 'demo-seed'
UNION ALL SELECT 'user_role', COUNT(*) FROM user_role ur
  JOIN app_user u ON ur.user_id = u.id WHERE u.created_by = 'demo-seed';
```

Count the join tables too. The `INSERT ... SELECT` into `user_role` inserts
no row, and raises no error, when the role it looks up is missing.

### 3.2 Engine idioms

| Concern | MySQL | PostgreSQL (psql) | SQLite |
|---|---|---|---|
| Id of the row just inserted | `LAST_INSERT_ID()`, kept per connection, then `SET @v = LAST_INSERT_ID();` | `INSERT ... RETURNING id \gset` stores the column in the psql variable `:id` | `last_insert_rowid()` on the same connection |
| Using the variable | `@v`, **unquoted**: `'@v'` is the string `@v` | `:id` (or `:'name'` for a quoted literal) | a subquery that selects the parent by its natural key |
| Stop at the first error | the client stops by default in batch mode; `--force` makes it continue | **continues by default**; set `-v ON_ERROR_STOP=1` (exit code 3 on a script error) | `.bail on` in the shell |
| All or nothing | `START TRANSACTION ... COMMIT` in the file; a client that stops leaves the transaction uncommitted, and closing the connection rolls it back | `--single-transaction` with `ON_ERROR_STOP` sends `ROLLBACK` on failure; the file must then not contain its own `BEGIN`/`COMMIT` | `BEGIN; ... COMMIT;` in the file |
| Delete through a join | `DELETE alias FROM t alias JOIN ...` | `DELETE FROM t USING other WHERE ...` | a subquery in `WHERE ... IN (...)` |
| Abort on a bad count | no conditional abort outside a stored program (`SIGNAL`); assert the counts in the verifier | a `DO` block with `RAISE EXCEPTION` | no conditional abort in a plain script; assert the counts in the verifier |

An uninitialized MySQL user variable is NULL, so a misspelt variable inserts
NULL into a foreign key, which then fails (or, on a nullable column, silently
orphans the row). Read the counts after every first apply.

### 3.3 The seeded-world API verifier

Row counts prove the rows exist. They do not prove that a screen works. The
verifier drives the real API:

1. **Log in as every seeded user in every login mode** (a user login, a device
   or kiosk login, a second role). A login passes only when the response holds
   a non-empty token at the path the plan names.
2. **Call every endpoint each screen uses**, as the user that screen runs as,
   with the bearer token from step 1.
3. **Resolve ids at runtime.** A check can capture a value from its response
   (by path, or from the first list item whose fields match) into a variable
   that later paths use as `{NAME}`. A path whose variable was never captured
   fails; it never guesses an id.
4. **Exercise the red and empty paths:** the broken entity reports its broken
   state, an entity with no children returns an empty list, an unauthenticated
   call is refused.
5. **Assert, and exit non-zero on any failure.** Status (default 200), list
   size (`items`, `min_items`, `max_items`), field values (`equals` by dotted
   path) and list membership (`has_item`). A login that fails fails every
   check that runs as that user, by name.

The plan's fields (a dotted path follows object keys, and an integer part
indexes a list):

| Where | Field | Meaning |
|---|---|---|
| login | `as` | the user name that checks refer to |
| login | `mode` | a label in the report only (`device`, `kiosk`) |
| login | `path`, `method` | the login endpoint; method default `POST` |
| login | `json` | the request body |
| login | `token` | dotted path of the token in the JSON response; default `token` |
| login | `status` | the status a good login returns; default 200 |
| check | `name` | the report label; default the path |
| check | `as` | the login whose bearer token the call carries; none means unauthenticated |
| check | `path`, `method` | the endpoint, with `{NAME}` for a captured value; method default `GET` |
| check | `json` | a request body |
| check | `status` | the expected status; default 200 |
| check | `at` | dotted path to the part of the response the assertions read |
| check | `items`, `min_items`, `max_items` | list size |
| check | `equals` | an object of dotted path to expected value |
| check | `has_item` | a list of objects; each must match some item's fields |
| check | `capture` | `{NAME: {at, find, field}}`: from the response (or its `at` part), the first list item whose fields match `find`, then its `field` |

A value written `${NAME}` anywhere in the plan is read from the environment.
The verifier reads the token from the login's JSON body only. A login that
returns its token in a header or a cookie needs a different login step.

A plan:

```json
{
  "logins": [
    {"as": "admin", "path": "/api/login",
     "json": {"user": "admin", "password": "${DEMO_PASSWORD}"}},
    {"as": "op", "mode": "device", "path": "/api/device/7/login",
     "json": {"user": "demo.operator", "password": "${DEMO_PASSWORD}"}}
  ],
  "checks": [
    {"name": "sites", "as": "admin", "path": "/api/sites", "min_items": 2,
     "capture": {"S1": {"find": {"name": "Site A"}, "field": "id"}}},
    {"name": "units of S1, one broken", "as": "admin", "path": "/api/sites/{S1}/units",
     "has_item": [{"state": "KO"}], "capture": {"KO": {"find": {"state": "KO"}, "field": "id"}}},
    {"name": "broken unit reports KO", "as": "op", "path": "/api/units/{KO}/status",
     "equals": {"state": "KO"}},
    {"name": "unauthenticated is refused", "path": "/api/sites", "status": 401}
  ]
}
```

```python
#!/usr/bin/env python3
"""seeded-world-verifier: after a data seed, log in as every seeded user in
every login mode and drive every endpoint each screen uses, with ids resolved
at runtime, asserting each answer. Stdlib only.

Usage:
  seeded-world-verifier.py --plan PLAN.json --base-url URL
  seeded-world-verifier.py --self-test

The plan names logins and checks (see the page). Secrets never sit in the
plan: a value written "${NAME}" is read from the environment variable NAME.
Exit 0: every login and check passed. Exit 1: any failed. Exit 2: usage error,
an unreadable plan, a missing environment variable, or a plan with no check.
"""
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request

VAR = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")
REF = re.compile(r"\{([A-Za-z_][A-Za-z0-9_]*)\}")


class PlanError(Exception):
    pass


def env_expand(value):
    if isinstance(value, str):
        def sub(m):
            if m.group(1) not in os.environ:
                raise PlanError(f"environment variable {m.group(1)} is not set")
            return os.environ[m.group(1)]
        return VAR.sub(sub, value)
    if isinstance(value, dict):
        return {k: env_expand(v) for k, v in value.items()}
    if isinstance(value, list):
        return [env_expand(v) for v in value]
    return value


def dig(doc, path):
    """Follow a dotted path; integer parts index lists. '' is the document."""
    node = doc
    for part in [p for p in str(path).split(".") if p != ""]:
        if isinstance(node, list) and part.lstrip("-").isdigit():
            node = node[int(part)]
        elif isinstance(node, dict) and part in node:
            node = node[part]
        else:
            raise KeyError(path)
    return node


def call(base, method, path, token=None, body=None, timeout=15):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(base.rstrip("/") + path, data=data, method=method)
    req.add_header("Accept", "application/json")
    if data is not None:
        req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            status, raw = resp.status, resp.read()
    except urllib.error.HTTPError as exc:
        status, raw = exc.code, exc.read()
    try:
        return status, json.loads(raw.decode() or "null")
    except ValueError:
        return status, None


def assert_check(chk, status, doc):
    """-> list of failure strings (empty when the check holds)."""
    fails = []
    want = chk.get("status", 200)
    if status != want:
        return [f"status {status}, expected {want}"]
    target = doc
    if "at" in chk:
        try:
            target = dig(doc, chk["at"])
        except (KeyError, IndexError, TypeError):
            return [f"path {chk['at']!r} not in the response"]
    if "min_items" in chk or "max_items" in chk or "items" in chk:
        if not isinstance(target, list):
            return ["expected a list"]
        n = len(target)
        if "items" in chk and n != chk["items"]:
            fails.append(f"{n} item(s), expected exactly {chk['items']}")
        if n < chk.get("min_items", 0):
            fails.append(f"{n} item(s), expected at least {chk['min_items']}")
        if "max_items" in chk and n > chk["max_items"]:
            fails.append(f"{n} item(s), expected at most {chk['max_items']}")
    for path, value in (chk.get("equals") or {}).items():
        try:
            got = dig(target, path)
        except (KeyError, IndexError, TypeError):
            fails.append(f"{path} missing")
            continue
        if got != value:
            fails.append(f"{path} = {got!r}, expected {value!r}")
    for match in chk.get("has_item") or []:
        if not isinstance(target, list) or not any(
                isinstance(it, dict) and all(it.get(k) == v for k, v in match.items())
                for it in target):
            fails.append(f"no item matches {match}")
    return fails


def capture(chk, doc, vars_):
    for name, spec in (chk.get("capture") or {}).items():
        node = dig(doc, spec.get("at", ""))
        if "find" in spec:
            node = next(it for it in node if isinstance(it, dict)
                        and all(it.get(k) == v for k, v in spec["find"].items()))
        vars_[name] = dig(node, spec.get("field", ""))


def resolve(path, vars_):
    def sub(m):
        if m.group(1) not in vars_:
            raise KeyError(m.group(1))
        return str(vars_[m.group(1)])
    return REF.sub(sub, path)


def verify(plan, base, out=sys.stdout):
    tokens, vars_, passed, failed = {}, {}, 0, 0
    def report(ok, name, why=""):
        nonlocal passed, failed
        passed, failed = passed + ok, failed + (not ok)
        print(f"{'PASS' if ok else 'FAIL'}  {name}{'  - ' + why if why else ''}", file=out)
    for lg in plan.get("logins", []):
        name = f"login {lg['as']}" + (f" ({lg['mode']})" if lg.get("mode") else "")
        try:
            status, doc = call(base, lg.get("method", "POST"), resolve(lg["path"], vars_),
                               body=lg.get("json"))
            tok = dig(doc, lg.get("token", "token")) if status == lg.get("status", 200) else None
        except (KeyError, IndexError, TypeError, OSError) as exc:
            status, tok = getattr(exc, "reason", exc), None
        if isinstance(tok, str) and tok:
            tokens[lg["as"]] = tok
            report(True, name)
        else:
            report(False, name, f"no token (status {status})")
    for chk in plan["checks"]:
        name = chk.get("name", chk["path"])
        who = chk.get("as")
        if who and who not in tokens:
            report(False, name, f"no token for {who}: its login failed")
            continue
        try:
            path = resolve(chk["path"], vars_)
        except KeyError as exc:
            report(False, name, f"id {exc} was never captured")
            continue
        try:
            status, doc = call(base, chk.get("method", "GET"), path, tokens.get(who),
                               body=chk.get("json"))
        except OSError as exc:
            report(False, name, f"no answer: {exc}")
            continue
        fails = assert_check(chk, status, doc)
        if not fails and chk.get("capture"):
            try:
                capture(chk, doc, vars_)
            except (KeyError, IndexError, TypeError, StopIteration):
                fails = ["a capture found nothing to resolve"]
        report(not fails, name, "; ".join(fails))
    print(f"SUMMARY: {passed} passed, {failed} failed", file=out)
    return 1 if failed else 0


def load_plan(path):
    try:
        with open(path, encoding="utf-8") as fh:
            plan = env_expand(json.load(fh))
    except (OSError, ValueError) as exc:
        raise PlanError(f"cannot read plan {path}: {exc}")
    if not plan.get("checks"):
        raise PlanError("the plan has no check; refusing to report a pass")
    return plan


def self_test():
    import io
    import tempfile
    import threading
    from http.server import BaseHTTPRequestHandler, HTTPServer

    class Fake(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass
        def reply(self, status, doc):
            raw = json.dumps(doc).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)
        def do_POST(self):
            body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            if body.get("password") != "demo-pass":
                return self.reply(401, {"error": "bad credentials"})
            mode = "device" if "/device/" in self.path else "user"
            self.reply(200, {"token": f"{mode}-{body['user']}"})
        def do_GET(self):
            if not self.headers.get("Authorization", "").startswith("Bearer "):
                return self.reply(401, {})
            routes = {"/api/sites": [{"id": 41, "name": "Site A"}, {"id": 42, "name": "Site B"}],
                      "/api/sites/41/units": [{"id": 7, "state": "OK"}, {"id": 8, "state": "KO"}],
                      "/api/sites/42/units": [],
                      "/api/units/8/status": {"state": "KO"},
                      "/api/units/7/instructions": None}
            if self.path not in routes:
                return self.reply(404, {})
            if routes[self.path] is None:
                return self.reply(500, {"error": "NullPointerException"})
            self.reply(200, routes[self.path])

    srv = HTTPServer(("127.0.0.1", 0), Fake)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{srv.server_port}"
    os.environ["SELFTEST_DEMO_PASSWORD"] = "demo-pass"
    plan = {
        "logins": [
            {"as": "admin", "path": "/api/login", "json": {"user": "admin", "password": "${SELFTEST_DEMO_PASSWORD}"}},
            {"as": "op", "mode": "device", "path": "/api/device/7/login",
             "json": {"user": "op", "password": "${SELFTEST_DEMO_PASSWORD}"}}],
        "checks": [
            {"name": "sites", "as": "admin", "path": "/api/sites", "min_items": 2,
             "capture": {"S1": {"find": {"name": "Site A"}, "field": "id"},
                         "S2": {"find": {"name": "Site B"}, "field": "id"}}},
            {"name": "units of S1, one broken", "as": "admin", "path": "/api/sites/{S1}/units",
             "items": 2, "has_item": [{"state": "KO"}],
             "capture": {"KO": {"find": {"state": "KO"}, "field": "id"}}},
            {"name": "empty path: S2 has no unit", "as": "admin", "path": "/api/sites/{S2}/units", "items": 0},
            {"name": "broken unit reports KO", "as": "op", "path": "/api/units/{KO}/status",
             "equals": {"state": "KO"}},
            {"name": "unauthenticated is refused", "path": "/api/sites", "status": 401}]}
    bad = json.loads(json.dumps(plan))
    bad["checks"].append({"name": "instructions", "as": "op", "path": "/api/units/7/instructions"})
    bad["checks"].append({"name": "never captured", "as": "admin", "path": "/api/x/{NOPE}"})
    bad["logins"].append({"as": "ghost", "path": "/api/login", "json": {"user": "g", "password": "wrong"}})
    bad["checks"].append({"name": "ghost check", "as": "ghost", "path": "/api/sites"})
    checks = []
    with tempfile.TemporaryDirectory() as tmp:
        def run_plan(p):
            path = os.path.join(tmp, "plan.json"); json.dump(p, open(path, "w"))
            buf = io.StringIO(); rc = verify(load_plan(path), base, out=buf)
            return rc, buf.getvalue()
        rc, text = run_plan(plan)
        checks += [(rc == 0, "a world that matches its plan passes"),
                   ("SUMMARY: 7 passed, 0 failed" in text, "logins and checks all counted")]
        rc, text = run_plan(bad)
        checks += [(rc == 1, "a failing check exits 1"),
                   ("FAIL  instructions  - status 500" in text, "a server error is a failure"),
                   ("FAIL  login ghost" in text and "its login failed" in text,
                    "a failed login fails its user's checks"),
                   ("demo-pass" not in text, "the password is never printed")]
        lone = json.loads(json.dumps(plan))
        lone["checks"].append({"name": "never captured", "as": "admin", "path": "/api/x/{NOPE}"})
        rc, text = run_plan(lone)
        checks.append((rc == 1 and "FAIL  never captured  - id 'NOPE' was never captured" in text,
                       "an unresolved id fails, never guesses"))
        del os.environ["SELFTEST_DEMO_PASSWORD"]
        path = os.path.join(tmp, "p.json"); json.dump(plan, open(path, "w"))
        try:
            load_plan(path); checks.append((False, "a missing env var is refused"))
        except PlanError:
            checks.append((True, "a missing env var is refused"))
        json.dump({"checks": []}, open(path, "w"))
        try:
            load_plan(path); checks.append((False, "an empty plan is refused"))
        except PlanError:
            checks.append((True, "an empty plan is refused"))
    srv.shutdown()
    failed = [n for ok, n in checks if not ok]
    for n in failed:
        print(f"FAIL {n}\n{text}", file=sys.stderr)
    print("self-test:", "FAIL" if failed else f"PASS ({len(checks)} checks)")
    return 1 if failed else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--plan")
    ap.add_argument("--base-url")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not (a.plan and a.base_url):
        ap.print_usage(sys.stderr)
        return 2
    try:
        plan = load_plan(a.plan)
    except PlanError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return verify(plan, a.base_url)


if __name__ == "__main__":
    sys.exit(main())
```

## 4. Portable vs blueprint

- **Portable (adopt verbatim):** the verifier with its plan format and
  self-test; the seed method: owner marker, children-first reset, unlink and
  re-link of real rows, parent-first inserts chained through variables, one
  transaction, count check, dump before the first apply.
- **Blueprint (write per project):** the seed file itself and the verify
  plan. Both are coupled to one schema and one API, which is why they live in
  the project, next to the schema they depend on, and are re-checked when it
  changes.
- **Adopting note:** a schema managed by an ORM's automatic update (no
  migrations) drifts without notice; re-read it before every re-apply.

## 5. Pitfalls and sharp edges

- **The delete order is load-bearing.** A wrong order fails the reset with a
  foreign-key error and the whole run rolls back. Read every foreign key and
  its delete rule (for example from `information_schema`) and order the reset
  from that, not from memory.
- **A statement cannot modify a table and select from the same table in a
  subquery** (MySQL error 1093). Use the multi-table `DELETE ... JOIN` and
  `UPDATE ... JOIN` forms the skeleton shows, or wrap the subquery in a
  derived table that MySQL materializes, which the MySQL manual's
  "Restrictions on Subqueries" names as the exception.
- **A quoted variable is a string.** In MySQL, `'@site_a'` inserts the text
  `@site_a`, and the foreign key check then fails.
- **Enums stored as ordinals.** A schema that stores an enum as its position
  needs the integer, and a reordered enum in the code silently changes what a
  seeded row means. Look the mapping up in the code for every enum the seed
  sets.
- **Date-keyed data and purge jobs.** Seed dates relative to the day of the
  apply (`CURDATE()`, `CURRENT_DATE`) when a screen shows "today" or a nightly
  job removes old rows.
- **A crash on a missing related row is a bug, not a seed problem.** When an
  endpoint fails because a seeded entity lacks an optional related row (an
  instruction with no attachment, a user with no profile), make the seed
  supply the row so the world is usable, and record the crash as a bug for the
  owner. Do not fix the code quietly inside a data task.
- **Ids move on every re-apply.** Anything that names an id (a verify plan, a
  manual test script, a bug report) resolves it at run time.
- **psql keeps going after an error by default.** Without `ON_ERROR_STOP` a
  failing statement is reported and the rest of the file still runs, so a
  half-applied world commits. Always pass it.
- **The demo password is a credential.** Keep it out of the seed file's
  comments and out of the plan (use `${NAME}`); store only its hash in the
  seed. The verifier never prints a value it read from the environment.
- **Take the dump before the first apply.** The reset block only touches
  marked rows, but the first apply is when a wrong marker or a wrong join
  shows itself.

## 6. Tests that cover it

The verifier carries its own fixture self-test (`--self-test`). It starts a
fake API on a loopback port and checks: a world that matches its plan passes
with every login and check counted; a server error fails its check; a path
whose id was never captured fails instead of guessing; a failed login fails
that user's checks by name; the password never appears in the output; a
missing environment variable and a plan with no check are refused.

Recorded when the page was written:

```
$ python3 seeded-world-verifier.py --self-test
self-test: PASS (9 checks)
```

The seed method has no fixture test here because it is schema-bound. Its gate
in the adopting project is: apply twice in a row against a copy of the
database (the second run must succeed and leave the same counts), then run the
verifier.

## 7. References & neighbours

- **Library pages:** `library-corpus/container/mysql.md`,
  `library-corpus/container/postgres.md` (initialization, clients).
- **Related tools:** `tool-corpus/testing/http-smoke-suite.md` (protocol-level
  post-deploy assertions; the verifier asserts the seeded data through the
  same API); `tool-corpus/ops/disposable-test-identity-provisioner.md`
  (throwaway identities, not a data world).
- **Skills:** `skill-corpus/seed-demo-world-for-manual-ui-review.md` (the
  procedure that calls this tool).
- **Sources:** MySQL, `LAST_INSERT_ID()` ("maintained in the server on a
  per-connection basis"), user-defined variables (an uninitialized variable
  "has a value of NULL"), and the `mysql` client's `--force` ("Continue even
  if an SQL error occurs"), and "Restrictions on Subqueries" (error 1093 and
  its derived-table exception) (<https://dev.mysql.com/doc/refman/8.4/en/>);
  PostgreSQL, `psql` `ON_ERROR_STOP`, `--single-transaction` and `\gset`
  (<https://www.postgresql.org/docs/current/app-psql.html>); SQLite,
  `last_insert_rowid()` (<https://www.sqlite.org/c3ref/last_insert_rowid.html>).

## 8. Changelog

- 2026-10-05: created by tool-smith.
  A verify script that prints a digest of each response and always exits 0
  leaves a reader to judge every run by eye; the verifier here asserts and
  exits non-zero.
- 2026-10-05: review fixes. The plan's fields are listed in one table. The
  skeleton sets foreign-key checks on and counts the join table. Error 1093
  and its derived-table exception are named. An earlier note dropped them as
  unconfirmed; the MySQL manual documents both. The calling skill is linked.
