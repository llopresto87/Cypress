---
stack:
  - library-corpus/cli/maven
  - library-corpus/language/nodejs
  - library-corpus/language/python
---
# Tool: resolved-dependency-gate

> Project-agnostic capability notes, kept in the seed's tool corpus
> (`tool-corpus/README.md`). The rule checker below is a complete stdlib script
> with its own fixture self-test. The capture step that feeds it (running the
> package manager's own resolver, ideally in a throwaway build container) is
> written per ecosystem in §3.1; the Maven form is the worked example, with the
> npm and pip forms beside it.

## 0. Identity

- **Category:** ops
- **Name:** resolved-dependency-gate
- **Language / runtime:** python3, stdlib only, for the checker; the
  ecosystem's own resolver (Maven, npm, pip) for the capture.
- **Stability:** **portable** for the checker (§3.2), which ran its self-test
  and a synthetic two-consumer fixture when it was folded in (§6). The capture
  commands in §3.1 are documented resolver invocations; the container they run
  in is the adopting project's.

## 1. What it does

Asserts facts about the dependency tree that a build **actually resolves**,
for every consumer that matters, and fails the build when one stops holding:

- **require:** a coordinate must be on the tree (a migration's target library,
  a security bridge, an aspect weaver whose absence silently disables a
  feature);
- **forbid:** a coordinate, or a version range of it, must not be on the tree
  (a retired framework line, a library family removed for an advisory, a
  legacy API package);
- **floor:** every resolved version of a coordinate must be at or above a
  version (a transitive dependency with a known fixed release).

It reads the resolved tree, never the declared versions. A declared version
can lose to a managed version set (a BOM, a parent, a resolution override),
and an undeclared transitive can arrive from anywhere. A gate that reads
resolution gives the same verdict whether the fix came from a version-set bump
or an explicit override, so nobody "simplifies" it into a grep of the build
file that passes while the old version still ships.

The in-build alternative for Maven is the enforcer plugin's
`bannedDependencies` rule. It needs the plugin in every consumer's POM. An
external gate fits better when those POMs are frozen (mid migration, or owned
by someone else) and when one set of rules covers several consumers in one
place.

## 2. Interface & invocation

```sh
# 1. capture each consumer's resolved tree (§3.1), one file per consumer
# 2. check the rules over all of them
resolved-dependency-gate.py --format maven-text \
  --tree service-a=trees/service-a.txt --tree service-b=trees/service-b.txt \
  --require 'org.example:target-lib' \
  --forbid  'org.example.legacy:*' --forbid 'com.example.codec:*@1.4.*' \
  --floor   'com.example.codec:codec-core=3.2.0'
resolved-dependency-gate.py --self-test
```

- **Inputs:** `--format` (`maven-text`, `npm-json` or `pip-inspect`); one
  `--tree NAME=FILE` per consumer; at least one rule. A coordinate is
  `group:artifact` for Maven and a package name for npm and pip; Maven and npm
  coordinates take shell-style globs. `--forbid COORD@GLOB` limits the ban to
  matching versions; an npm scoped name (`@scope/name`, or
  `@scope/name@1.*`) works, because the separator is the first `@` after the
  name's own. `--floor COORD=VERSION`.
- **Outputs:** per consumer, the node count and one `ok` or `FAIL` line per
  rule naming what resolved; then `GATE: PASS` or `GATE: FAIL`.
- **Exit codes:** 0 every rule holds for every consumer; 1 a rule failed;
  2 usage error, an unreadable capture, a capture that records a failed build,
  or a capture with no resolved node. A capture problem is never reported as a
  rule result.
- **Preconditions:** the captures exist. Producing them needs the ecosystem's
  resolver and its repositories (§3.1); checking them needs nothing.

## 3. Approach / algorithm

### 3.1 Capture: let the resolver resolve

Capture per consumer, in an environment that does not leak the host's state
into the result:

- **Maven.** In each consumer module (not the reactor root, whose output holds
  every module's tree in one stream):

  ```sh
  mvn -B -ntp org.apache.maven.plugins:maven-dependency-plugin:<version>:tree \
    > trees/<consumer>.txt
  ```

  Name the plugin with its version, as above, so the tree's output format does
  not change with the Maven install that runs it (`library-corpus/cli/maven.md`
  pins every plugin version); the shorter `dependency:tree` below stands for
  this form. A module whose parent POM is the reactor root (`relativePath`)
  does not resolve when only its own directory is present: run from the
  reactor root with `mvn -pl <module> ... :tree`, so the parent resolves and
  the stream still holds that one module's tree. Without `-am`, a sibling
  module it depends on must already be in the local repository; with `-am`,
  the siblings' trees join the same stream.

  Run it in a throwaway build container that mounts the module and a
  persistent local-repository volume, so repeated runs are fast and the host
  needs no JDK:

  ```sh
  docker run --rm -v "$PWD/<module>":/src -w /src -v m2-cache:/root/.m2 \
    <maven image pinned by digest> mvn -B -ntp dependency:tree > trees/<consumer>.txt
  ```

  Two upstream facts shape this. `outputFile`, when set, writes the tree "to
  the path specified, instead of writing to the console", so grepping the
  console after `-DoutputFile` reads only the build log; capture standard
  output, or read the file you named. `verbose` includes "omitted nodes", the
  versions that lost a conflict; the checker ignores those parenthesized lines,
  but do not use verbose output as the gate's input by habit.
- **An internal artifact that cannot be built yet.** When a consumer depends
  on an in-house artifact that does not build at this stage (it is mid
  migration), install a stub so the consumer's tree still resolves:
  `mvn install:install-file -Dfile=<empty jar> -DpomFile=<the artifact's real
  pom.xml>`. Passing the real POM keeps the artifact's own dependencies on the
  tree; a generated POM would drop them and the gate would check the wrong
  tree. The stub proves resolution only, and the record says so.
- **npm.** `npm ls --all --json > trees/<consumer>.json`. Without `--all`,
  `npm ls` shows only top-level dependencies. `--package-lock-only` reads the
  tree from `package-lock.json` instead of `node_modules`, which is what you
  want in CI before an install. Observed in practice, and not stated on the
  `npm ls` page: `npm ls` exits non-zero when the tree has problems (missing or
  invalid packages) and still prints the JSON. Keep the file and let the
  checker decide.
- **pip.** Inside the built environment or image:
  `python -m pip inspect > trees/<consumer>.json`. It reports what is
  installed in that environment, which is the resolved set; run it in the
  image that ships, not in a developer's virtual environment.

Record the resolver version next to the captures when the result is evidence.

### 3.2 Check: rules over resolved nodes

1. **Parse each capture to a map of coordinate to resolved versions.** Maven
   text lines are `group:artifact:type:version:scope`, or
   `group:artifact:type:classifier:version:scope` when the artifact has a
   classifier; the parser reads both, strips the `[INFO]` prefix and tree
   glyphs, skips the root project line, and skips parenthesized omitted nodes.
   npm JSON is walked through every nested `dependencies` object, skipping
   entries marked `missing`. pip names are normalized (case folded, runs of
   `-`, `_` and `.` made one `-`).
2. **Refuse a capture that proves nothing.** A capture that records
   `BUILD FAILURE` or unresolved dependencies, or that yields no node, exits 2
   and names the consumer. An empty tree is never green by omission.
3. **Apply each rule to each consumer.** require: at least one matching node.
   forbid: no matching node (with `@GLOB`, no matching node at a matching
   version). floor: every matching node at or above the floor, and a floor on
   a coordinate that resolves nowhere fails, because nothing was checked.
4. **Compare versions numerically.** Numeric segments compare as numbers
   (`1.10` is above `1.9`; `3.2.0.1000` is above `3.2.0`; trailing zeros are
   ignored). The qualifiers `final`, `ga` and `release`, in any case, equal the
   plain release, as Maven's version order trims them ("1.final -> 1"), so a
   floor holds for a `.Final` artifact. Any other qualifier after the numbers
   (`-RC1`, `rc1`, `-SNAPSHOT`) sorts below the plain release. This is close
   to, not identical with, each ecosystem's own ordering; a floor that depends
   on qualifier order needs the ecosystem's comparator.
5. **Report every rule for every consumer**, then one verdict.

```python
#!/usr/bin/env python3
"""resolved-dependency-gate: assert rules over the EFFECTIVE RESOLVED
dependency tree of every consumer, never the declared one.

Usage:
  resolved-dependency-gate.py --format maven-text|npm-json|pip-inspect
      --tree NAME=FILE [--tree NAME=FILE ...]
      [--require COORD ...] [--forbid COORD[@VERSION-GLOB] ...]
      [--floor COORD=VERSION ...]
  resolved-dependency-gate.py --self-test

COORD is group:artifact for Maven (fnmatch globs allowed), the package name for
npm and pip. FILE is a captured resolver output (see the page for the capture
commands). Exit 0: every rule holds for every consumer. Exit 1: a rule failed.
Exit 2: usage error, an unreadable or failed capture, or a tree with no node.
"""
import argparse
import fnmatch
import json
import re
import sys
import tempfile
import os

GLYPHS = re.compile(r"^(?:\[[A-Z]+\]\s?)?[\s|+\\`\-]*")


class CaptureError(Exception):
    pass


def parse_maven_text(text):
    """dependency:tree text -> {group:artifact: {versions}}. Lines in
    parentheses are omitted nodes (verbose mode): they did not resolve."""
    if "BUILD FAILURE" in text or "Could not resolve dependencies" in text:
        raise CaptureError("the capture records a failed build")
    nodes = {}
    for raw in text.splitlines():
        line = GLYPHS.sub("", raw).strip()
        if not line or line.startswith("("):
            continue
        parts = line.split()[0].split(":")
        if len(parts) == 5:        # g:a:type:version:scope
            g, a, _t, v, _s = parts
        elif len(parts) == 6:      # g:a:type:classifier:version:scope
            g, a, _t, _c, v, _s = parts
        elif len(parts) == 4 and not nodes:   # the root project g:a:packaging:version
            continue
        else:
            continue
        if not re.match(r"^[\w.\-]+$", g) or not re.match(r"^[\w.\-]+$", a):
            continue
        nodes.setdefault(f"{g}:{a}", set()).add(v)
    return nodes


def parse_npm_json(text):
    data = json.loads(text)
    nodes = {}

    def walk(deps):
        for name, info in (deps or {}).items():
            if info.get("missing") or "version" not in info:
                continue
            nodes.setdefault(name, set()).add(info["version"])
            walk(info.get("dependencies"))
    walk(data.get("dependencies"))
    return nodes


def parse_pip_inspect(text):
    data = json.loads(text)
    nodes = {}
    for item in data.get("installed", []):
        md = item.get("metadata", {})
        name = re.sub(r"[-_.]+", "-", md.get("name", "")).lower()
        if name:
            nodes.setdefault(name, set()).add(md.get("version", ""))
    return nodes


PARSERS = {"maven-text": parse_maven_text, "npm-json": parse_npm_json,
           "pip-inspect": parse_pip_inspect}


def vkey(v):
    """Numeric segments compare as numbers; final, ga and release equal the
    plain release (Maven's order); any other qualifier after the numbers
    (alpha, RC, SNAPSHOT, ...) sorts below the plain release."""
    nums, qual = [], False
    for tok in re.split(r"[.\-+]", v):
        if tok.lower() in ("final", "ga", "release", ""):
            continue
        if tok.isdigit() and not qual:
            nums.append(int(tok))
        else:
            qual = True
    while nums and nums[-1] == 0:
        nums.pop()
    return (nums, 0 if qual else 1)


def split_forbid(rule):
    """COORD[@VERSION-GLOB]. An npm scoped name starts with '@', so the
    version separator is the first '@' after index 0."""
    i = rule.find("@", 1)
    return (rule, "") if i < 0 else (rule[:i], rule[i + 1:])


def matching(nodes, coord, fmt):
    if fmt == "pip-inspect":
        coord = re.sub(r"[-_.]+", "-", coord).lower()
    return {k: vs for k, vs in nodes.items() if fnmatch.fnmatchcase(k, coord)}


def check(name, nodes, fmt, require, forbid, floor, out):
    fails = 0
    def say(ok, msg):
        nonlocal fails
        fails += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'}  {msg}", file=out)
    print(f"[{name}] {sum(len(v) for v in nodes.values())} resolved node(s)", file=out)
    for coord in require:
        hit = matching(nodes, coord, fmt)
        say(bool(hit), f"require {coord}: " + (", ".join(
            f"{k} {'/'.join(sorted(v))}" for k, v in sorted(hit.items())) or "absent"))
    for rule in forbid:
        coord, vglob = split_forbid(rule)
        hit = {k: {v for v in vs if not vglob or fnmatch.fnmatchcase(v, vglob)}
               for k, vs in matching(nodes, coord, fmt).items()}
        hit = {k: v for k, v in hit.items() if v}
        say(not hit, f"forbid {rule}: " + (", ".join(
            f"{k} {'/'.join(sorted(v))}" for k, v in sorted(hit.items())) or "absent"))
    for rule in floor:
        coord, _, minimum = rule.partition("=")
        hit = matching(nodes, coord, fmt)
        if not hit:
            say(False, f"floor {coord}>={minimum}: absent, so nothing was checked")
            continue
        low = sorted(f"{k} {v}" for k, vs in hit.items() for v in vs if vkey(v) < vkey(minimum))
        say(not low, f"floor {coord}>={minimum}: " + (", ".join(low) or "every resolved version meets it"))
    return fails


def run(a, out=sys.stdout):
    if not a.tree or not (a.require or a.forbid or a.floor):
        print("error: give at least one --tree and one rule", file=sys.stderr)
        return 2
    total = 0
    for spec in a.tree:
        name, _, path = spec.partition("=")
        try:
            with open(path, encoding="utf-8") as fh:
                nodes = PARSERS[a.format](fh.read())
        except (OSError, ValueError, CaptureError) as exc:
            print(f"error: [{name}] {path}: {exc}", file=sys.stderr)
            return 2
        if not nodes:
            print(f"error: [{name}] {path}: no resolved node; refusing to report a pass",
                  file=sys.stderr)
            return 2
        total += check(name, nodes, a.format, a.require, a.forbid, a.floor, out)
    print(f"GATE: {'FAIL' if total else 'PASS'} ({total} failed rule check(s))", file=out)
    return 1 if total else 0


MAVEN_GOOD = """[INFO] com.example:svc:jar:1.0.0
[INFO] +- org.example:web:jar:3.1.0:compile
[INFO] |  \\- com.example.codec:codec-core:jar:3.2.0.1000:compile
[INFO] +- org.example:native:jar:linux-x86_64:4.1.0:runtime
[INFO] \\- com.example.legacy:log:jar:0.1.0:compile
[INFO]    \\- com.example.codec:codec-time:jar:3.2.0:compile
[INFO] BUILD SUCCESS
"""
MAVEN_BAD = MAVEN_GOOD.replace("codec-core:jar:3.2.0.1000", "codec-core:jar:1.4.2").replace(
    "[INFO] BUILD SUCCESS", "[INFO] +- (com.example.codec:codec-core:jar:3.2.0.1000:compile - omitted for conflict)\n[INFO] BUILD SUCCESS")
NPM = json.dumps({"name": "app", "version": "1.0.0", "dependencies": {
    "web": {"version": "2.0.0", "dependencies": {"parser": {"version": "1.4.0"}}},
    "gone": {"missing": True}, "@scope/bad": {"version": "1.0.0"}}})
PIP = json.dumps({"version": "1", "installed": [
    {"metadata": {"name": "Example_Lib", "version": "2.1.0rc1"}},
    {"metadata": {"name": "other", "version": "1.0"}}]})


def self_test():
    import io
    checks = []
    with tempfile.TemporaryDirectory() as tmp:
        def f(name, text):
            p = os.path.join(tmp, name); open(p, "w").write(text); return p
        good, bad = f("good.txt", MAVEN_GOOD), f("bad.txt", MAVEN_BAD)
        failed = f("failed.txt", "[INFO] BUILD FAILURE\n")
        empty = f("empty.txt", "[INFO] Scanning for projects...\n")
        npm, pip = f("npm.json", NPM), f("pip.json", PIP)
        def go(*argv):
            a = parser().parse_args(list(argv)); buf = io.StringIO()
            return run(a, out=buf), buf.getvalue()
        rules = ["--require", "com.example.codec:codec-core", "--forbid", "com.example.codec:*@1.4.*",
                 "--floor", "com.example.codec:codec-core=3.2.0", "--require", "org.example:native"]
        rc, text = go("--format", "maven-text", "--tree", f"a={good}", *rules)
        checks += [(rc == 0, "a patched tree passes"),
                   ("org.example:native 4.1.0" in text, "a classifier node parses")]
        rc, text = go("--format", "maven-text", "--tree", f"a={good}", "--tree", f"b={bad}", *rules)
        checks += [(rc == 1, "one regressed consumer fails the gate"),
                   ("codec-core 1.4.2" in text, "the banned version is named"),
                   ("codec-core 3.2.0.1000" not in text.split("[b]")[1], "an omitted node is not resolved")]
        rc, text = go("--format", "maven-text", "--tree", f"a={good}", "--floor", "org.absent:x=1.0")
        checks.append((rc == 1 and "absent" in text, "a floor on an absent artifact fails"))
        checks.append((go("--format", "maven-text", "--tree", f"a={failed}", *rules)[0] == 2,
                       "a failed build capture exits 2"))
        checks.append((go("--format", "maven-text", "--tree", f"a={empty}", *rules)[0] == 2,
                       "a capture with no node exits 2"))
        rc, text = go("--format", "npm-json", "--tree", f"web={npm}", "--floor", "parser=1.5.0",
                      "--forbid", "gone")
        checks.append((rc == 1 and "parser 1.4.0" in text and "forbid gone: absent" in text,
                       "npm: nested node read, missing entry ignored"))
        rc, text = go("--format", "npm-json", "--tree", f"web={npm}", "--forbid", "@scope/bad")
        rc2, text2 = go("--format", "npm-json", "--tree", f"web={npm}", "--forbid", "@scope/bad@2.*")
        checks.append((rc == 1 and "@scope/bad 1.0.0" in text and rc2 == 0,
                       "npm: a scoped name is a name, not a version separator"))
        rc, text = go("--format", "pip-inspect", "--tree", f"env={pip}", "--floor", "example-lib=2.1.0")
        checks.append((rc == 1, "pip: names normalized, a release candidate sorts below the release"))
        checks.append((vkey("3.2.0.1000") > vkey("3.2.0") and vkey("1.10") > vkey("1.9")
                       and vkey("2.0") == vkey("2"), "version order is numeric"))
        checks.append((vkey("1.2.3.Final") == vkey("1.2.3") == vkey("1.2.3-GA")
                       and vkey("1.2.3.RC1") < vkey("1.2.3"),
                       "final and ga equal the release; other qualifiers sort below"))
    failed = [n for ok, n in checks if not ok]
    for n in failed:
        print(f"FAIL {n}", file=sys.stderr)
    print("self-test:", "FAIL" if failed else f"PASS ({len(checks)} checks)")
    return 1 if failed else 0


def parser():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--format", choices=sorted(PARSERS), default="maven-text")
    ap.add_argument("--tree", action="append", default=[])
    ap.add_argument("--require", action="append", default=[])
    ap.add_argument("--forbid", action="append", default=[])
    ap.add_argument("--floor", action="append", default=[])
    ap.add_argument("--self-test", action="store_true")
    return ap


def main():
    a = parser().parse_args()
    return self_test() if a.self_test else run(a)


if __name__ == "__main__":
    sys.exit(main())
```

### 3.3 A sibling check: declared against used (Maven)

`mvn dependency:analyze` reports dependencies that are "used and undeclared"
and "unused and declared". It runs `test-compile` first and works at bytecode
level, so it needs a compiling module; `dependency:analyze-only` is the form
for a lifecycle binding. Use it next to this gate, not instead of it: it says
what the code needs, this gate says what resolved.

## 4. Portable vs blueprint

- **Portable (adopt verbatim):** the checker with its parsers, rules, version
  order, exit codes and self-test; the per-consumer capture rule; the
  stub-with-real-POM rule.
- **Write per project:** the consumer list, the rules (they are the contract a
  migration or an advisory decision sets), and the capture wrapper with its
  pinned build image. Keep the rules next to the decision that motivated them,
  and name that decision in the gate's own output when it fails.
- **Adopting note:** another ecosystem joins by adding a parser that returns
  the same map. A lockfile with exact resolved versions (for example a Gradle
  dependency report or a `uv.lock`) is a fine source, as long as it is the
  resolver's output and not the declared ranges.

## 5. Pitfalls and sharp edges

- **Resolution, not compilation.** A PASS says the tree is right. The code may
  still not compile or start (a migration's later increments, a stubbed
  internal artifact). Do not read PASS as "it builds".
- **A reactor-root capture merges modules.** Run the capture per consumer
  module, or the rules apply to the union of every module's tree.
- **Use the effective tree for review ranking too.** An advisory against a
  transitive version that a managed version set out-resolves is
  defense-in-depth, not a live exposure: the vulnerable version is not on the
  resolved tree. Measure the tree before ranking the finding, and rank it on
  what resolves (`tool-corpus/ops/container-vuln-scan-and-aggregate.md` shows
  what the image holds).
- **A dead repository makes the capture hang or fail.** Neutralize it with a
  settings-level mirror rather than by editing a POM you must not change
  (`library-corpus/cli/maven.md`, "Idioms"), and run the capture offline once
  the cache is warm.
- **Absence of a coordinate the rule names is a failure for require and
  floor.** Write forbid rules for what must be gone, and require or floor rules
  for what must be there; a floor alone on a library that a refactor removed
  fails loudly, which is the point.
- **This is not lock closure.** Whether a hash-pinned lock covers every
  transitive dependency for the target platform is a different question,
  answered by `tool-corpus/ops/hashed-lock-closure-check.md`.

## 6. Tests that cover it

The script carries its own fixture self-test (`--self-test`) over synthetic
captures (example coordinates only). It checks: a patched tree passes; a
classifier node parses; one regressed consumer fails the gate and the banned
version is named; an omitted (parenthesized) node is not treated as resolved;
a floor on an absent artifact fails; a failed-build capture and a capture with
no node exit 2; npm nested nodes are read and a missing entry is ignored; an
npm scoped name is matched as a name, with and without a version glob; pip
names are normalized and a release candidate sorts below its release; the
numeric version order holds; `final` and `ga` equal the release.

Recorded when the page was written:

```
$ python3 resolved-dependency-gate.py --self-test
self-test: PASS (13 checks)
$ python3 resolved-dependency-gate.py --format maven-text \
    --tree service-a=trees/a.txt --tree service-b=trees/b.txt \
    --require org.example:target-lib --forbid 'com.example.codec:*@1.4.*' \
    --floor com.example.codec:codec-core=3.2.0
[service-a] 2 resolved node(s)
  ok    require org.example:target-lib: org.example:target-lib 4.0.1
  ok    forbid com.example.codec:*@1.4.*: absent
  ok    floor com.example.codec:codec-core>=3.2.0: every resolved version meets it
[service-b] 2 resolved node(s)
  FAIL  require org.example:target-lib: absent
  FAIL  forbid com.example.codec:*@1.4.*: com.example.codec:codec-core 1.4.2
  FAIL  floor com.example.codec:codec-core>=3.2.0: com.example.codec:codec-core 1.4.2
GATE: FAIL (3 failed rule check(s))
(exit 1)
```

The capture and the checker were also run once end to end: a synthetic
two-dependency POM (one dependency with a classifier), `mvn -B -ntp
dependency:tree` in a throwaway Maven container with a cache volume, and the
checker over the captured console output. It parsed all 10 resolved nodes,
including the classifier node, and the require, forbid and floor rules passed
(exit 0).

- **How to run the tests:** `python3 resolved-dependency-gate.py --self-test`;
  then the capture plus the checker as the CI step.

## 7. References & neighbours

- **Library pages:** `library-corpus/cli/maven.md` (`dependency:tree`, the
  enforcer, settings mirrors); `library-corpus/language/nodejs.md`;
  `library-corpus/language/python.md`.
- **Related tools:** `tool-corpus/ops/hashed-lock-closure-check.md` (closure
  of a hash-pinned lock, a different property);
  `tool-corpus/ops/renamed-config-key-auditor.md` (the configuration side of
  the same major-version move); `tool-corpus/ops/container-vuln-scan-and-aggregate.md`.
- **Sources:** Maven Dependency Plugin, `dependency:tree` parameters
  (`outputFile`, `outputType`, `verbose`, `includes`)
  (<https://maven.apache.org/plugins/maven-dependency-plugin/tree-mojo.html>)
  and `dependency:analyze`
  (<https://maven.apache.org/plugins/maven-dependency-plugin/analyze-mojo.html>);
  Maven POM reference, "Version Order Specification" (`final`, `ga` and
  `release` equal the release) (<https://maven.apache.org/pom.html>);
  Maven Install Plugin, `install:install-file` with `pomFile`
  (<https://maven.apache.org/plugins/maven-install-plugin/install-file-mojo.html>);
  npm, `npm ls`, `--all` and `--package-lock-only`
  (<https://docs.npmjs.com/cli/v10/commands/npm-ls>);
  pip, `pip inspect` (<https://pip.pypa.io/en/stable/cli/pip_inspect/>).

## 8. Changelog

- 2026-10-05: created by tool-smith.
  Combines two gates: a resolution contract gate (required and
  retired coordinates, a version floor, a stub for an unbuildable internal
  artifact, run in a throwaway build container) and a version gate over the
  resolved tree of several consumers with a fixture mode. Corrected on the way
  in: the version gate's parser mis-read a node with a classifier and ignored
  the resolver's exit state in live mode; both gates hard-coded their
  consumers and rules; the contract gate's floor compared versions with a
  `sort -V` call that is not the ecosystem's order.
- 2026-10-05: review fixes. `--forbid` split an npm scoped name at its
  leading `@` and always passed; it now splits at the first `@` after the
  name's own. `final`, `ga` and `release` equal the release in the version
  order. Fixture versions made neutral. Plugin pin, reactor-root `-pl`
  capture, the enforcer alternative and the `stack:` field added.
