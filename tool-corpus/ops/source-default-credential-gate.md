---
stack:
  - library-corpus/maven/spring-boot
  - library-corpus/container/docker-compose
---
# Tool: source-default-credential-gate

> Project-agnostic capability notes, kept in the seed's tool corpus
> (`tool-corpus/README.md`). The gate below is a complete stdlib script with its
> own fixture self-test; adopt it as written and supply the file list and the
> key names.

## 0. Identity

- **Category:** ops
- **Name:** source-default-credential-gate
- **Language / runtime:** python3, stdlib only. No network, no configuration
  parser: it reads the files as text, line by line.
- **Stability:** **portable**: the script in §3 ran its self-test and a
  synthetic two-file fixture when it was folded in (§6).

## 1. What it does

Configuration is often externalized with placeholders that carry a fallback:
`${DB_URL:jdbc:...}` in Spring property files, `${DB_PASSWORD:-...}` in a
Compose file or a shell script. The fallback is what a run with no environment
gets: a developer's laptop, a container started by hand, an image someone
pulled and ran. A credential written into that fallback is a credential in
source and in every image built from it, even when the deploy always sets the
variable.

The gate reads the **default** part of every placeholder and fails when it
holds a credential in one of the two forms it knows: a password in URL
userinfo (`scheme://user:password@host`) or in URL query parameters
(`?password=...`). It also takes a list of key names whose value must be a
placeholder with an empty default, and fails when one of them holds a literal.
It reports `file:line [REDACTED]` and a reason, and never the value.

It answers one question that a generic secret scanner answers badly: a scanner
looks for strings that look like secrets anywhere, so it either misses
`http://app:example@host` inside a default or flags every runtime form that
only names a variable. This gate looks at the one place a source default lives.

## 2. Interface & invocation

```sh
source-default-credential-gate.py [--key <name> ...] <file> [<file> ...]
source-default-credential-gate.py --self-test
```

- **Inputs:** the configuration files to check, named explicitly (property
  files, YAML, Compose files, `.env` templates, shell scripts). `--key` names
  a key whose value must be a placeholder with no literal default; it matches
  the whole key or its last dotted segment exactly, so `--key password`
  covers `spring.datasource.password` and a YAML `password:` and leaves
  `password-policy` alone. Repeatable. No default file set and no default key
  list: both are facts about one project.
- **Outputs:** one `RED <file>:<line> [REDACTED] <reason>` per finding; a
  `SUMMARY` line; a `NOTE` line that says what GREEN does not mean (§5).
- **Exit codes:** 0 no finding; 1 at least one finding; 2 usage error or an
  unreadable file. A missing file is an error, never a clean result.
- **Preconditions:** python3. The files are read as UTF-8 text.

## 3. Approach / algorithm

1. **Find every placeholder, nested ones included.** Scan for `${`, balance
   the braces, and split the inside into a name, an operator and the rest.
   The operators recognized are the Spring default separator `:` and the
   Compose and shell forms `:-`, `-`, `:+`, `+`, `:?` and `?`. Compose
   documents nesting (`${VARIABLE:-${FOO:-default}}`), so the default of an
   outer placeholder is scanned again for inner ones.
2. **Skip what is not a default.** `${VAR:?message}` and `${VAR?message}`
   stop with an error when the variable is missing; the text after the
   operator is a message, not a value. A placeholder whose default is only
   another placeholder has no literal part.
3. **Check the literal part of each default** for URL userinfo with a
   password, `scheme://user:password@host`, and for a password in URL query
   parameters (`?password=`, `&pwd=` and the like, the form many JDBC drivers
   take). The literal part is the default with every nested placeholder
   removed, so `http://${USER}:${PASS}@host` and `...&password=${DB_PW}` pass,
   and `http://app:example@host` and `...&password=example` fail.
4. **Check the literal part of the whole line** for the same patterns, which
   catches a connection URL written with no placeholder at all.
5. **Check the named keys.** A key on the `--key` list must hold one
   placeholder and nothing else, and that placeholder's default must be empty
   (`${DB_PASSWORD}`, `${DB_PASSWORD:}`, `${DB_PASSWORD:?required}`, or
   Compose's unbraced `$DB_PASSWORD`). A literal, or a placeholder with a
   non-empty literal default, is a finding.
6. **Report by location only**, deduplicated per line and reason, and exit 1
   on any finding.

```python
#!/usr/bin/env python3
"""source-default-credential-gate: fail when a configuration file carries a
credential in source, either in the DEFAULT of a ${VAR...} placeholder or as
a literal value of a key that must be a placeholder. Never prints a value.

Usage:
  source-default-credential-gate.py [--key NAME ...] FILE [FILE ...]
  source-default-credential-gate.py --self-test

Exit 0: no finding. Exit 1: at least one finding. Exit 2: usage error, an
unreadable file, or no file given.
"""
import argparse
import os
import re
import sys
import tempfile

NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_.\-]*")
# URL userinfo with a password part: scheme://user:password@host
USERINFO = re.compile(r"[A-Za-z][A-Za-z0-9+.\-]*://[^/@\s:]+:[^/@\s]+@")
# a password in URL query parameters, the form many JDBC drivers take
QUERY_PW = re.compile(r"[?&;](?:password|passwd|pwd|pass)=[^&;\s#\"'}]+", re.IGNORECASE)
COMPOSE_VAR = re.compile(r"\$[A-Za-z_][A-Za-z0-9_]*")
KEY_LINE = re.compile(
    r"^\s*(?:-\s*)?(?:export\s+)?(?P<key>[A-Za-z_][A-Za-z0-9_.\-]*)\s*(?::|=)\s*(?P<val>.*?)\s*$")


def placeholders(text):
    """Yield (name, operator, default) for every ${...} in text, with nested
    braces balanced, so ${A:${B:x}} yields both levels."""
    i = 0
    while True:
        start = text.find("${", i)
        if start < 0:
            return
        depth, j = 0, start
        while j < len(text):
            if text.startswith("${", j):
                depth += 1
                j += 2
                continue
            if text[j] == "}":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        inner = text[start + 2:j] if depth == 0 else text[start + 2:]
        m = NAME.match(inner)
        name = m.group(0) if m else ""
        rest = inner[len(name):]
        op = ""
        for cand in (":-", ":+", ":?", ":", "-", "+", "?"):
            if rest.startswith(cand):
                op = cand
                break
        default = rest[len(op):] if op else ""
        yield name, op, default
        yield from placeholders(default)
        i = start + 2


def literal_part(default):
    """The source-literal text of a default: nested placeholders removed."""
    out, i = [], 0
    while True:
        s = default.find("${", i)
        if s < 0:
            out.append(default[i:])
            return "".join(out)
        out.append(default[i:s])
        depth, j = 0, s
        while j < len(default):
            if default.startswith("${", j):
                depth += 1
                j += 2
                continue
            if default[j] == "}":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        i = j + 1


def scan(path, keys):
    """Yield (lineno, reason) per finding. Never yields a value."""
    with open(path, encoding="utf-8") as fh:
        for no, line in enumerate(fh, 1):
            for _name, op, default in placeholders(line):
                if op in ("?", ":?"):        # an error message, not a default
                    continue
                if USERINFO.search(literal_part(default)):
                    yield no, "URL userinfo in a placeholder default"
                if QUERY_PW.search(literal_part(default)):
                    yield no, "URL query password in a placeholder default"
            if USERINFO.search(literal_part(line)):
                yield no, "URL userinfo in a literal value"
            if QUERY_PW.search(literal_part(line)):
                yield no, "URL query password in a literal value"
            m = KEY_LINE.match(line)
            if not m or not keys:
                continue
            leaf = re.split(r"[.]", m.group("key"))[-1]
            if leaf not in keys and m.group("key") not in keys:
                continue
            val = m.group("val").split(" #", 1)[0].strip().strip("\"'")
            if val in ("", "|", ">") or COMPOSE_VAR.fullmatch(val):
                continue                     # $NAME: Compose's unbraced form, no default
            phs = list(placeholders(val))
            whole = val.startswith("${") and val.endswith("}") and phs
            if not whole:
                yield no, f"key '{leaf}' holds a literal, a placeholder is required"
                continue
            name, op, default = phs[0]
            if op in ("?", ":?"):
                continue
            if literal_part(default).strip():
                yield no, f"key '{leaf}' placeholder has a non-empty literal default"


def run(files, keys, out=sys.stdout):
    findings = 0
    for path in files:
        try:
            hits = sorted(set(scan(path, keys)))
        except OSError as exc:
            print(f"error: cannot read {path}: {exc}", file=sys.stderr)
            return 2
        for no, reason in hits:
            findings += 1
            print(f"RED  {path}:{no}  [REDACTED]  {reason}", file=out)
    print(f"SUMMARY: {findings} finding(s) in {len(files)} file(s)", file=out)
    print("NOTE: GREEN means no credential is left in these source defaults. "
          "It does not mean a value that was ever committed has been rotated.", file=out)
    return 1 if findings else 0


def self_test():
    import io
    clean = (
        "spring:\n  config:\n"
        "    import: ${CONFIG_IMPORT:configserver:http://localhost:8888/}\n"
        "  datasource:\n    password: ${DB_PASSWORD}\n"
        "    url: ${DB_URL:jdbc:postgresql://db:5432/app}\n"
        "remote:\n  password: ${REMOTE_PASSWORD:}\n"
        "edge:\n  url: ${EDGE_URL:?set EDGE_URL}\n"
        "services:\n  api:\n    environment:\n"
        "      - DB_PASSWORD=${DB_PASSWORD:?required}\n"
        "    db:\n      environment:\n        DB_PASSWORD: $DB_PASSWORD\n"
        "jdbc: ${JDBC_URL:jdbc:mysql://db/app?user=app&password=${DB_PW}}\n")
    leaky = (
        "spring:\n  config:\n"
        "    import: ${CONFIG_IMPORT:configserver:http://cfguser:s3cr3tA@localhost:8888/}\n"
        "  datasource:\n    password: hunter2B\n"
        "remote:\n  password: ${REMOTE_PASSWORD:fallbackC}\n"
        "nested: ${OUTER:${INNER:https://u:s3cr3tD@host/x}}\n"
        "plain: amqp://guest:s3cr3tE@broker:5672/\n"
        "services:\n  api:\n    environment:\n"
        "      - DB_PASSWORD=${DB_PASSWORD:-s3cr3tF}\n"
        "jdbc: ${JDBC_URL:jdbc:mysql://db/app?user=root&password=s3cr3tG}\n")
    secrets = ["s3cr3tA", "hunter2B", "fallbackC", "s3cr3tD", "s3cr3tE", "s3cr3tF", "s3cr3tG"]
    keys = {"password", "DB_PASSWORD"}
    checks = []
    with tempfile.TemporaryDirectory() as tmp:
        c = os.path.join(tmp, "clean.yml"); open(c, "w").write(clean)
        l = os.path.join(tmp, "leaky.yml"); open(l, "w").write(leaky)
        buf = io.StringIO(); rc = run([c], keys, out=buf); text_c = buf.getvalue()
        checks.append((rc == 0, "clean file exits 0"))
        buf = io.StringIO(); rc = run([l], keys, out=buf); text_l = buf.getvalue()
        checks.append((rc == 1, "leaky file exits 1"))
        checks.append(("SUMMARY: 7 finding(s)" in text_l, "seven findings, one per planted leak"))
        for line in (3, 5, 7, 8, 9, 13, 14):
            checks.append((f"leaky.yml:{line}" in text_l, f"line {line} reported"))
        checks.append((not any(s in text_l + text_c for s in secrets), "no value printed"))
        checks.append((run([os.path.join(tmp, "absent.yml")], keys, out=io.StringIO()) == 2,
                       "an unreadable file exits 2"))
    failed = [n for ok, n in checks if not ok]
    for n in failed:
        print(f"FAIL {n}\n{text_l}", file=sys.stderr)
    print("self-test:", "FAIL" if failed else f"PASS ({len(checks)} checks)")
    return 1 if failed else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("files", nargs="*")
    ap.add_argument("--key", action="append", default=[],
                    help="exact key name whose value must be a placeholder "
                         "with an empty default (repeatable)")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not a.files:
        ap.print_usage(sys.stderr)
        return 2
    return run(a.files, set(a.key))


if __name__ == "__main__":
    sys.exit(main())
```

## 4. Portable vs blueprint

- **Portable (use as-is):** the whole script: the balanced placeholder parser
  with both syntax families, the literal-part rule, the userinfo pattern, the
  exact key match, the redacted report, the exit codes and the self-test.
- **Fill in:** the file list and the key names. Keep the file list where the
  deploy definition lives, so a new configuration file joins the gate in the
  same change that adds it.
- **Adopting note:** a configuration syntax with a different placeholder form
  (for example `%(name)s`, or `{{ name | default(...) }}` in a template
  engine) needs its own parser for step 1. Steps 2 to 6 do not change.

## 5. Pitfalls and sharp edges

- **GREEN is not rotation.** The gate proves that no credential is left in
  the files it read. A value that was committed once is compromised
  (`core/method/secrets-posture.md` §3): it is still in the history, in
  every image built from it, and in every clone. Rotate it with
  `tool-corpus/ops/env-secret-rotation.md`, then rebuild the images that
  carried it. The gate stops the leak from coming back; it does not undo it.
- **Keep the scope narrow on purpose.** A gate that also covers a known,
  accepted residue (a credential the owner has scheduled for rotation in a
  later phase) fails on every run until that work lands, and people learn to
  ignore it. Name the files and keys it owns; track the residue elsewhere and
  add it to the gate when it is fixed.
- **Never print the value.** Not in the finding, not in a debug line, not in
  an assertion message of the self-test. The value is the secret.
- **Only the two URL forms are recognized in a default.** A bare password
  as a default (`${DB_PASSWORD:example}`) is caught only when its key is on
  the `--key` list, and a credential in any other shape (a token in a header
  value, a key in a DSN that is not a URL) is not caught at all.
- **Userinfo without a password is not flagged.** A token sent as the user
  part (`https://<token>@host`) is a credential too. The pattern needs a `:`
  in the userinfo, because `ssh://git@host` and similar forms are common and
  harmless. Add a project rule when the project uses token-as-user URLs.
- **Comments are read.** A commented-out connection string with a password is
  still in source, and the gate reports it. Delete it rather than exempting it.
- **An escaped dollar is read as a placeholder.** Compose treats `$${VAR}` as
  a literal `${VAR}`. The gate still parses it; a finding there is a false
  positive, and the fix is to check the rendered file instead.
- **The key match is exact.** A credential under a key you did not name is not
  covered by step 5. The generic secret scanner and
  `tool-corpus/ops/structured-secret-field-detector.md` cover other classes;
  this gate does not replace either.

## 6. Tests that cover it

The script carries its own fixture self-test (`--self-test`). It writes a clean
and a leaky file to a temporary directory and checks: the clean file exits 0
(a credential-less default, a required variable with a `:?` message, an empty
default on a named key, a Compose list entry, an unbraced `$NAME` on a named
key, a query-parameter password that is itself a placeholder); the leaky file
exits 1 with exactly seven findings, one per planted leak (userinfo in a default, a literal on
a named key, a literal default on a named key, userinfo in a nested default,
userinfo in a plain value, a `:-` literal default in a Compose list entry, a
query-parameter password in a default); no
planted value appears in any output; an unreadable file exits 2.

Recorded when the page was written:

```
$ python3 source-default-credential-gate.py --self-test
self-test: PASS (12 checks)
$ python3 source-default-credential-gate.py --key password --key DB_PASSWORD \
    application.properties compose.yaml
RED  application.properties:2  [REDACTED]  key 'password' holds a literal, a placeholder is required
RED  application.properties:3  [REDACTED]  URL userinfo in a placeholder default
SUMMARY: 2 finding(s) in 2 file(s)
(exit 1)
```

- **How to run the tests:** `python3 source-default-credential-gate.py --self-test`,
  then the gate over the real files as the CI step.

## 7. References & neighbours

- **Related tools:** `tool-corpus/ops/structured-secret-field-detector.md`
  (exact key names under one subtree of a parsed document; this gate reads
  placeholder defaults in text); `tool-corpus/ops/env-secret-rotation.md` (the
  rotation a GREEN here does not perform);
  `tool-corpus/ops/layered-config-merge-verifier.md` (whether a guard such as
  `:?` survives the layering of several files).
- **Library pages:** `library-corpus/maven/spring-boot.md` (externalized
  configuration); `library-corpus/container/docker-compose.md`.
- **Sources:** Spring Boot, "Externalized Configuration", property
  placeholders: "a default value using a `:` to separate the default value
  from the property name"
  (<https://docs.spring.io/spring-boot/reference/features/external-config.html>);
  Compose file reference, "Interpolation": the default, required and
  alternative forms, nesting and the `$$` escape
  (<https://docs.docker.com/reference/compose-file/interpolation/>).

## 8. Changelog

- 2026-10-05: created by tool-smith.
  Generalized from a plant gate bound to one framework property and one
  config-server file. Corrected on the way in: the plant gate accepted a
  placeholder with a literal default on a password key (it checked only that
  the value began with `${`), cut a nested default at the first `}`, and read
  only one fixed file path per check.
- 2026-10-05: review fixes. A password in URL query parameters is now
  detected, and Compose's unbraced `$NAME` counts as a placeholder with no
  default. §5 names the credential shapes the gate does not cover. `stack:`
  added.
