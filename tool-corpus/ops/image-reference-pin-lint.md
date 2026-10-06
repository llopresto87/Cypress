---
stack:
  - library-corpus/container/docker
  - library-corpus/container/docker-compose
---
# Tool: image-reference-pin-lint

> Project-agnostic capability notes, kept in the seed's tool corpus
> (`tool-corpus/README.md`). The lint below is a complete stdlib script with its
> own fixture self-test; adopt it as written and supply only the exempt
> patterns.

## 0. Identity

- **Category:** ops
- **Name:** image-reference-pin-lint
- **Language / runtime:** python3, stdlib only. No container daemon, no
  network, no YAML parser.
- **Stability:** **portable**: the script in §3 ran its self-test and a
  synthetic two-file fixture when it was folded in (§6).

## 1. What it does

Reads Compose files and Dockerfiles and puts every image reference that would
be pulled into one of three classes:

- **pinned:** the reference carries a well-formed content digest,
  `name[:tag]@sha256:<64 lowercase hex>` or `@sha512:<128 lowercase hex>`;
- **violation:** untagged (which resolves to `latest`), `:latest`, a tag with
  no digest, a malformed digest, or a variable the lint cannot resolve;
- **exempt:** an image the project builds itself (matched by a declared glob,
  and in Compose only when its service sets `pull_policy: build` or `never`),
  an earlier build stage named in the same Dockerfile, or `scratch`.

It prints one line per reference, a summary with the three counts, and exits
non-zero on any violation. A mutable tag can change what runs between two
builds with no change in the repository; a digest names exactly one image
(`library-corpus/container/docker.md`, "Tags vs digests"). The library page
says to pin by digest. This tool is the gate that checks that the rule holds
in every file that deploys.

## 2. Interface & invocation

```sh
image-pin-lint.py [--exempt '<glob>' ...] [--allow-todo] <file> [<file> ...]
image-pin-lint.py --self-test
```

- **Inputs:** the Compose files and Dockerfiles that make up the deploy path,
  named explicitly. A file whose name ends in `.yml` or `.yaml` is read as
  Compose; any other file is read as a Dockerfile. `--exempt` takes a glob
  over the full reference (for example `'example/*:local'`) and is
  repeatable. There is no default root and no default exempt pattern: both
  are facts about one project.
- **Outputs:** `PINNED`, `VIOLATION` or `EXEMPT` per reference, with
  `file:line` and the reason; then
  `SUMMARY: <n> pinned, <n> violations, <n> exempt` and a line that says what
  the result does not prove (§5).
- **Exit codes:** 0 no violation; 1 at least one violation; 2 usage error, an
  unreadable file, or no image reference found in any file (a run that read
  nothing refuses to report a pass).
- **Preconditions:** none beyond python3. The lint never contacts a registry.

## 3. Approach / algorithm

1. **Find the references.** In Compose, every `image:` value, including one
   written as a list item, with quotes stripped and a trailing `# comment`
   kept apart. In a Dockerfile, every `FROM` line, with flags such as
   `--platform=...` skipped, so the first remaining word is the image.
2. **Drop what is not a pull.** `FROM scratch` and `FROM <stage>`, where
   `<stage>` was named by an earlier `FROM ... AS <stage>` in the same file,
   pull nothing. Upstream documents that a stage name "can be used in
   subsequent `FROM <name>`" instructions. The stage name is recorded after
   its own line is checked, so `FROM x AS x` still checks the pull of `x`.
3. **Split the reference correctly.** The tag is whatever follows a `:` in
   the **last** path component; a `:` earlier in the string is a registry
   port. `registry.example:5000/edge` is untagged, not tagged `5000/edge`.
4. **Classify.** Exempt globs first; then a `$` anywhere means a variable the
   lint cannot resolve, which is a violation, never a pass; then a digest that
   matches `@sha256:[0-9a-f]{64}` or `@sha512:[0-9a-f]{128}` at the end is
   pinned; then untagged,
   `latest` and tag-without-digest are violations, each with its own reason.
5. **Report and exit.** Counts by class; exit 1 on any violation.

A RED phase is allowed to carry `# TODO` markers on the unpinned lines while
nobody can reach the registry yet. `--allow-todo` annotates those lines and
still counts them as violations, so a TODO never turns the gate green. Writing
a digest you did not resolve is never acceptable: it is a fabricated fact
that looks exactly like a verified one.

```python
#!/usr/bin/env python3
"""image-reference-pin-lint: classify every pulled image reference as
digest-pinned, violation, or exempt. Daemon-free, network-free, stdlib only.

Usage:
  image-pin-lint.py [--exempt GLOB ...] [--allow-todo] FILE [FILE ...]
  image-pin-lint.py --self-test

FILE is a Compose file (any name ending .yml/.yaml) or a Dockerfile (any
other name). Exit 0: no violation. Exit 1: at least one violation.
Exit 2: usage error, an unreadable file, or no reference found at all.
"""
import argparse
import fnmatch
import os
import re
import sys
import tempfile

DIGEST = re.compile(r"@(?:sha256:[0-9a-f]{64}|sha512:[0-9a-f]{128})$")
PULL_LOCAL = re.compile(r"^\s*pull_policy\s*:\s*[\"']?(build|never)[\"']?\s*(?:#.*)?$")
COMPOSE_IMAGE = re.compile(r"^\s*(?:-\s*)?image\s*:\s*(?P<ref>[^#\s]+)(?P<rest>.*)$")
FROM_LINE = re.compile(r"^\s*FROM\s+(?P<args>.+?)\s*$", re.IGNORECASE)


def split_ref(ref):
    """Return (name, tag, digest) of an image reference; the registry port
    is part of the name, never mistaken for a tag."""
    name, _, digest = ref.partition("@")
    last = name.rsplit("/", 1)[-1]
    tag = ""
    if ":" in last:
        tag = last.split(":", 1)[1]
        name = name[: len(name) - len(tag) - 1]
    return name, tag, digest


def classify(ref, exempt):
    """-> (verdict, reason). verdict is pinned, exempt or violation."""
    if any(fnmatch.fnmatchcase(ref, g) for g in exempt):
        return "exempt", "matches a declared exempt pattern"
    if "$" in ref:
        return "violation", "variable reference: not checkable statically"
    name, tag, digest = split_ref(ref)
    if digest:
        if DIGEST.search(ref):
            return "pinned", "digest present"
        return "violation", "malformed digest"
    if not tag:
        return "violation", "untagged (resolves to latest)"
    if tag == "latest":
        return "violation", ":latest"
    return "violation", "tag without digest"


def indent(line):
    return len(line) - len(line.lstrip())


def pulls_first(lines, idx):
    """True unless the service block holding lines[idx] sets pull_policy
    build or never. With build: and image: and no pull_policy, Compose pulls
    the image first and builds only when the registry has none."""
    ind = indent(lines[idx])
    lo = idx
    while lo > 0 and (not lines[lo - 1].strip() or indent(lines[lo - 1]) >= ind):
        lo -= 1
    hi = idx + 1
    while hi < len(lines) and (not lines[hi].strip() or indent(lines[hi]) >= ind):
        hi += 1
    return not any(PULL_LOCAL.match(l) and indent(l) == ind for l in lines[lo:hi])


def compose_refs(path, lines):
    for no, line in enumerate(lines, 1):
        m = COMPOSE_IMAGE.match(line)
        if m:
            yield no, m.group("ref").strip("\"'"), (m.group("rest"), pulls_first(lines, no - 1))


def dockerfile_refs(path, lines):
    stages = set()
    for no, line in enumerate(lines, 1):
        m = FROM_LINE.match(line)
        if not m:
            continue
        words = m.group("args").split("#", 1)[0].split()
        words = [w for w in words if not w.startswith("--")]   # --platform=...
        if not words:
            continue
        ref = words[0]
        local = ref.lower() == "scratch" or ref.lower() in stages
        if len(words) >= 3 and words[1].lower() == "as":
            stages.add(words[2].lower())      # named after the check: FROM x AS x pulls x
        if local:
            yield no, None, ref               # an earlier build stage or scratch: no pull
            continue
        yield no, ref, line


def lint(files, exempt, allow_todo, out=sys.stdout):
    rows, seen = [], 0
    for path in files:
        try:
            with open(path, encoding="utf-8") as fh:
                lines = fh.read().splitlines()
        except OSError as exc:
            print(f"error: cannot read {path}: {exc}", file=sys.stderr)
            return 2
        is_compose = path.endswith((".yml", ".yaml"))
        gen = compose_refs(path, lines) if is_compose else dockerfile_refs(path, lines)
        for no, ref, rest in gen:
            seen += 1
            if ref is None:
                rows.append(("exempt", f"{path}:{no}", rest, "build stage or scratch"))
                continue
            pull = False
            if is_compose:
                rest, pull = rest
            verdict, reason = classify(ref, exempt)
            if verdict == "exempt" and pull:
                verdict, reason = "violation", ("exempt pattern, but the service has no "
                                                "pull_policy: build or never, so Compose "
                                                "pulls this name first")
            if verdict == "violation" and allow_todo and "TODO" in (rest or ""):
                reason += " (TODO marker: accepted in a RED phase only)"
            rows.append((verdict, f"{path}:{no}", ref, reason))
    if seen == 0:
        print("error: no image reference found in the given files; "
              "refusing to report a pass", file=sys.stderr)
        return 2
    counts = {"pinned": 0, "violation": 0, "exempt": 0}
    for verdict, loc, ref, reason in rows:
        counts[verdict] += 1
        print(f"{verdict.upper():9} {loc}  {ref}  ({reason})", file=out)
    print(f"SUMMARY: {counts['pinned']} pinned, {counts['violation']} violations, "
          f"{counts['exempt']} exempt", file=out)
    print("NOTE: this checks the shape of each pin, not that the digest is the "
          "one the tag points at.", file=out)
    return 1 if counts["violation"] else 0


def self_test():
    d = "0123456789abcdef" * 4
    compose = (
        "services:\n"
        f"  db:\n    image: postgres:16@sha256:{d}\n"
        "  cache:\n    image: redis:latest\n"
        "  web:\n    image: example/web:local\n    build: .\n    pull_policy: build\n"
        "  side:\n    build: .\n    image: example/side:local\n"
        f"  long:\n    image: alpine:3@sha512:{d}{d}\n"
        "  proxy:\n    image: \"registry.example:5000/edge\"  # TODO: digest-pin\n"
        "  bad:\n    image: alpine:3@sha256:XYZ\n"
        "  var:\n    image: ${PROXY_IMAGE}\n")
    dockerfile = (
        f"FROM --platform=$BUILDPLATFORM golang:1@sha256:{d} AS build\n"
        "FROM build AS test\n"
        "FROM scratch\n"
        "FROM debian:stable-slim\n")
    with tempfile.TemporaryDirectory() as tmp:
        c = os.path.join(tmp, "compose.yaml"); open(c, "w").write(compose)
        f = os.path.join(tmp, "Dockerfile"); open(f, "w").write(dockerfile)
        e = os.path.join(tmp, "empty.yml"); open(e, "w").write("services: {}\n")
        import io
        buf = io.StringIO()
        rc = lint([c, f], ["example/*:local"], True, out=buf)
        text = buf.getvalue()
        checks = [
            (rc == 1, "a violation exits 1"),
            ("SUMMARY: 3 pinned, 6 violations, 3 exempt" in text, "counts"),
            ("example/side:local  (exempt pattern, but" in text,
             "an exempt name that Compose would pull first is a violation"),
            ("example/web:local  (matches" in text, "pull_policy: build keeps the exemption"),
            ("registry.example:5000/edge  (untagged" in text, "a registry port is not a tag"),
            ("TODO marker" in text, "TODO marker reported"),
            ("malformed digest" in text, "a malformed digest is a violation"),
            ("variable reference" in text, "a variable is not silently passed"),
            ("build stage or scratch" in text, "stage names and scratch are not pulls"),
            (lint([e], [], False, out=io.StringIO()) == 2, "no reference refuses a pass"),
        ]
        buf2 = io.StringIO()
        pinned = os.path.join(tmp, "Dockerfile.ok")
        open(pinned, "w").write(f"FROM alpine:3@sha256:{d}\n")
        checks.append((lint([pinned], [], False, out=buf2) == 0, "all pinned exits 0"))
    failed = [name for ok, name in checks if not ok]
    for name in failed:
        print(f"FAIL {name}\n{text}", file=sys.stderr)
    print("self-test:", "FAIL" if failed else f"PASS ({len(checks)} checks)")
    return 1 if failed else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("files", nargs="*")
    ap.add_argument("--exempt", action="append", default=[],
                    help="glob of a locally built image reference (repeatable)")
    ap.add_argument("--allow-todo", action="store_true",
                    help="annotate violations that carry a TODO marker")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not a.files:
        ap.print_usage(sys.stderr)
        return 2
    return lint(a.files, a.exempt, a.allow_todo)


if __name__ == "__main__":
    sys.exit(main())
```

## 4. Portable vs blueprint

- **Portable (use as-is):** the whole script: reference discovery in both file
  kinds, the stage and `scratch` rule, the registry-port-safe split, the
  variable-is-a-violation rule, the TODO handling, the three exit codes and the
  self-test.
- **Fill in:** the list of files on the deploy path and the exempt globs for
  the images the project builds itself. Keep that list next to the deploy
  definition, so a new file is added to the gate in the same change that adds
  it to the deploy.
- **Adopting note:** a project that deploys through other manifest kinds
  (Kubernetes manifests, Helm values, a CI file that runs containers) adds a
  reader for each one. The classifier does not change.

## 5. Pitfalls and sharp edges

- **Shape, not truth.** The lint proves a digest is present and well formed.
  It does not prove that the digest is the one the tag points at, or that the
  image is current. Resolve and cross-check digests with
  `tool-corpus/ops/registry-digest-resolver.md`; scan what they name with
  `tool-corpus/ops/container-vuln-scan-and-aggregate.md`.
- **A locally built image needs an explicit exemption, and a pull policy.**
  A Compose service with both `build:` and `image:` and no `pull_policy`
  does not simply build: Compose "attempts to pull the image first and then
  builds from source if the image isn't found". So an exempt name can arrive
  from a registry, unpinned. Give every exempt service `pull_policy: build`
  (or `never`), declare its pattern with `--exempt`, and keep that pattern on
  a tag no registry carries (a project namespace plus a local tag). The lint
  reports an exempt Compose image whose service sets neither policy as a
  violation. It finds the policy by indentation inside the service block, so
  a policy set through an anchor or `extends:` is not seen.
- **Variables are violations.** `image: ${REGISTRY}/app:1` and
  `FROM ${BASE}` cannot be checked without the values the deploy supplies.
  Either check the rendered configuration (for example the output of
  `docker compose config`), or accept the violation and pin the default where
  the variable is defined.
- **Only the files you name are checked.** An overlay Compose file or a second
  Dockerfile left out of the argument list is unchecked. A run that finds no
  reference at all exits 2 for that reason.
- **The lint reads lines, not YAML.** It does not expand anchors, merge keys
  or `extends:`. An image set only through those is invisible; check the
  rendered configuration when the project uses them.
- **A digest without a tag is valid and is reported as pinned.** Keeping the
  tag next to the digest (`name:tag@sha256:...`) costs nothing and tells a
  reader which release the digest was taken from.

## 6. Tests that cover it

The script carries its own fixture self-test (`--self-test`). It writes a
synthetic Compose file and Dockerfile to a temporary directory and checks: a
violation exits 1; the counts are exact; a registry port is not read as a tag;
a TODO marker is reported and still counts as a violation; a malformed digest
and a variable reference are violations; a `sha512` digest is pinned; an
exempt Compose image with `pull_policy: build` stays exempt and one without a
policy is a violation; build stages and `scratch` are not pulls; a file set with no reference exits 2; an all-pinned file exits 0.

Recorded when the page was written:

```
$ python3 image-pin-lint.py --self-test
self-test: PASS (11 checks)
$ python3 image-pin-lint.py --exempt 'example/*:local' compose.yml Dockerfile
VIOLATION compose.yml:3  nginx:1.27  (tag without digest)
EXEMPT    compose.yml:5  example/api:local  (matches a declared exempt pattern)
VIOLATION Dockerfile:1  python:3.12-slim  (tag without digest)
EXEMPT    Dockerfile:2  base  (build stage or scratch)
SUMMARY: 0 pinned, 2 violations, 2 exempt
(exit 1)
```

- **How to run the tests:** `python3 image-pin-lint.py --self-test`, plus the
  lint itself over the real deploy files as the gate.

## 7. References & neighbours

- **Library pages:** `library-corpus/container/docker.md` (tags against
  digests, and the rule to pin base images);
  `library-corpus/container/docker-compose.md`.
- **Related tools:** `tool-corpus/ops/registry-digest-resolver.md` (resolves
  the digest this lint asks for); `tool-corpus/ops/container-vuln-scan-and-aggregate.md`
  (scans the images the pins name); `tool-corpus/testing/static-config-contract-gate.md`
  (the general shape of a static check over deploy configuration).
- **Sources:** the Dockerfile reference for `FROM` and named build stages
  (<https://docs.docker.com/reference/dockerfile/>); the OCI image
  specification for the registered `sha256` and `sha512` digest forms
  (<https://github.com/opencontainers/image-spec/blob/main/descriptor.md>);
  the Compose build reference, "Using build and image", for the pull-first
  rule (<https://docs.docker.com/reference/compose-file/build/>).

## 8. Changelog

- 2026-10-05: created by tool-smith.
  Generalized from a plant gate with a fixed deploy root and one hard-coded
  exempt namespace. Corrected on the way in: the plant script read a
  `--platform` flag as the image, flagged every `FROM <stage>` line, read a
  registry port as a tag, and had no fixture test.
- 2026-10-05: review fixes. The `build:` plus `image:` statement was wrong:
  without `pull_policy`, Compose pulls first. An exempt Compose image now
  needs `pull_policy: build` or `never`, or it is a violation. A `sha512`
  digest is accepted as pinned.
