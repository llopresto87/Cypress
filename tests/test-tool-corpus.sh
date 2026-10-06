#!/usr/bin/env bash
# tool-corpus portability contract.
#
# A page in tool-corpus/ may declare `Stability: portable`, which the corpus
# README defines as "a self-contained script with no third-party or project
# dependencies" that an adopting project can use as-is. Nothing checked that.
# A portable implementation nobody has executed is a claim, not a tool — the
# same green lie protocols/verify.md forbids in a gate — and it fails at the
# worst moment, inside a plant that trusted the corpus instead of writing its
# own.
#
# So: every embedded implementation on a page that claims portability must at
# least PARSE, and the two whose behaviour is the reason the page exists must
# actually demonstrate it.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# 1. Every fenced implementation on a page claiming portability compiles —
# in EITHER of the seed's two required languages. Checking only one of them is
# how five of the eight pages claiming portability shipped their shell
# implementations with nothing looking at them at all, while this file's own
# prose and the corpus README both claimed every implementation was compiled.
python3 - "$ROOT" <<'PY'
import re, sys, ast, pathlib, subprocess, tempfile
root = pathlib.Path(sys.argv[1])
checked = 0
for page in sorted((root / "tool-corpus").rglob("*.md")):
    text = page.read_text(encoding="utf-8")
    if not re.search(r"\*\*Stability:\*\*\s*\*\*portable", text):
        continue
    for block in re.findall(r"```python\n(.*?)```", text, re.S):
        # A block is an IMPLEMENTATION only if it defines or imports
        # something. Pages also show bare interface sketches — a signature with
        # its keyword-only marker and no body — which are documentation, not
        # code, and are not Python that could be expected to parse.
        if not re.search(r"(?m)^(def |class |import |from |@)", block):
            continue
        try:
            ast.parse(block)
        except SyntaxError as exc:
            sys.exit(f"{page.relative_to(root)}: a page claiming portability "
                     f"embeds Python that does not parse: {exc}")
        checked += 1
    for block in re.findall(r"```(?:bash|sh)\n(.*?)```", text, re.S):
        # Same discriminator, in shell's vocabulary: a shebang, a shell option
        # line, or a function definition means this is meant to RUN. An
        # invocation example ("tool.sh <results-file>") is documentation and is
        # not shell that could be expected to parse.
        if not re.search(r"(?m)^(#!|set -|[A-Za-z_][A-Za-z0-9_]*\(\) *\{)", block):
            continue
        script = pathlib.Path(tempfile.mkstemp(suffix=".sh")[1])
        script.write_text(block)
        proc = subprocess.run(["bash", "-n", str(script)],
                              capture_output=True, text=True)
        script.unlink()
        if proc.returncode != 0:
            sys.exit(f"{page.relative_to(root)}: a page claiming portability "
                     f"embeds shell that does not parse: "
                     f"{proc.stderr.strip().splitlines()[-1] if proc.stderr.strip() else ''}")
        checked += 1

# A count with no floor is the vacuous pass this whole suite exists to refuse:
# rename the Stability marker and the selector matches nothing, the loop runs
# zero times, and the gate prints OK.
if checked < 8:
    sys.exit(f"only {checked} implementation(s) were compiled across the "
             f"portable pages — the selector matched almost nothing, which is "
             f"a vacuous pass, not a clean one")
print(f"  {checked} embedded implementation(s) on portable pages compile — OK")
PY

# 2. working-tree-snapshot: the property the page exists for is that an
# UNTRACKED-but-not-ignored file is in the listing. A tracked-only copier is
# the bug, and it is invisible until a gate fails for an unrelated reason.
python3 - "$ROOT/tool-corpus/testing/working-tree-snapshot.md" "$TMP/wts.py" <<'PY'
import re, sys, pathlib
blocks = re.findall(r"```python\n(.*?)```",
                    pathlib.Path(sys.argv[1]).read_text(), re.S)
pathlib.Path(sys.argv[2]).write_text(max(blocks, key=len))
PY
mkdir -p "$TMP/wt/sub"
( cd "$TMP/wt"
  git init -q .
  printf 'tracked\n'  > a.txt
  printf 'nested\n'   > sub/b.txt
  printf '*.log\n'    > .gitignore
  git add . && git -c user.email=t@t -c user.name=t commit -qm init
  printf 'untracked\n' > c.txt
  printf 'ignored\n'   > d.log )
python3 - "$TMP/wts.py" "$TMP/wt" <<'PY'
import importlib.util, pathlib, sys, tempfile
spec = importlib.util.spec_from_file_location("wts", sys.argv[1])
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
root = pathlib.Path(sys.argv[2]).resolve()
tree = sorted(m.list_repo_files(repo_root=root))
assert "a.txt" in tree and "sub/b.txt" in tree, f"tracked files missing: {tree}"
assert "c.txt" in tree, f"UNTRACKED file missing — the page's whole point: {tree}"
assert "d.log" not in tree, f"ignored file leaked into the listing: {tree}"
idx = sorted(m.list_repo_files(include_untracked=False, repo_root=root))
assert "c.txt" not in idx, f"the committed-state opt-out did not narrow: {idx}"
dest = pathlib.Path(tempfile.mkdtemp()) / "copy"
m.copy_repo_tree(dest, repo_root=root)
got = sorted(str(p.relative_to(dest)) for p in dest.rglob("*") if p.is_file())
assert "c.txt" in got and "sub/b.txt" in got and "d.log" not in got, got
print("  working-tree-snapshot: untracked in, ignored out, layout preserved — OK")
PY

# 3. layered-config-merge-verifier: the two properties that make it worth
# shipping — drift is keyed on the VARIABLE REFERENCE (the defect the page
# records is that keying on the config KEY produced mostly false positives),
# and analysing zero variables REFUSES rather than reporting a pass.
python3 - "$ROOT/tool-corpus/ops/layered-config-merge-verifier.md" "$TMP/lcmv.py" <<'PY'
import re, sys, pathlib
blocks = re.findall(r"```python\n(.*?)```",
                    pathlib.Path(sys.argv[1]).read_text(), re.S)
pathlib.Path(sys.argv[2]).write_text(max(blocks, key=len))
PY
# The verifier scans the layer files as text; it imports yaml only to parse a
# --resolver's output, which this check does not use, so no YAML parser is needed.
mkdir -p "$TMP/cfg"
cat > "$TMP/cfg/base.yml" <<'EOF'
services:
  api:
    environment:
      TOKEN: ${API_TOKEN:?set API_TOKEN}
EOF
cat > "$TMP/cfg/over.yml" <<'EOF'
services:
  api:
    environment:
      TOKEN: ${API_TOKEN}
EOF
out="$(python3 "$TMP/lcmv.py" --layer base="$TMP/cfg/base.yml" \
                              --layer over="$TMP/cfg/over.yml" 2>&1)" && rc=0 || rc=$?
[[ $rc -eq 1 ]] || { echo "a weakened guard did not fail the verifier" >&2; echo "$out" >&2; exit 1; }
grep -q "API_TOKEN" <<<"$out" || { echo "the weakened variable was not named" >&2; echo "$out" >&2; exit 1; }

printf 'services:\n  api:\n    image: x\n' > "$TMP/cfg/novars.yml"
cp "$TMP/cfg/novars.yml" "$TMP/cfg/novars2.yml"
out="$(python3 "$TMP/lcmv.py" --layer a="$TMP/cfg/novars.yml" \
                              --layer b="$TMP/cfg/novars2.yml" 2>&1)" && rc=0 || rc=$?
[[ $rc -eq 1 ]] || { echo "zero variables analysed was reported as a PASS" >&2; exit 1; }
grep -qi "refusing to report a pass" <<<"$out" \
  || { echo "the false-green guard did not say why it refused" >&2; echo "$out" >&2; exit 1; }
echo "  layered-config-merge-verifier: drift caught, zero-variable run refused — OK"

# 4. structured-secret-field-detector: the two properties that make it worth
# shipping — an EXACT key-name match (a substring match would flag a legitimate
# same-named-but-different field), and a missing subtree that RAISES rather than
# reporting clean, because a subtree that was not there was never searched.
python3 - "$ROOT/tool-corpus/ops/structured-secret-field-detector.md" "$TMP/ssfd.py" <<'PY'
import re, sys, pathlib
blocks = re.findall(r"```python\n(.*?)```",
                    pathlib.Path(sys.argv[1]).read_text(), re.S)
pathlib.Path(sys.argv[2]).write_text(max(blocks, key=len))
PY
python3 - "$TMP/ssfd.py" <<'PY'
import importlib.util, sys
spec = importlib.util.spec_from_file_location("ssfd", sys.argv[1])
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

doc = {"realm": {"users": [{"name": "a",
                            "credentials": [{"secretData": "x", "salt": "y"}]},
                           {"name": "b", "notSecretDataAtAll": "harmless"}]}}
hits = m.find_forbidden(doc, "realm.users", {"secretData", "salt"})
assert any("secretData" in h for h in hits), hits
assert any("salt" in h for h in hits), hits
assert not any("notSecretDataAtAll" in h for h in hits), \
    f"substring match flagged a legitimate field: {hits}"

try:
    m.find_forbidden(doc, "realm.absent", {"salt"})
except Exception:
    pass
else:
    sys.exit("a missing subtree reported clean instead of raising — "
             "an unsearched subtree must never pass")
print("  structured-secret-field-detector: exact-name only, missing subtree raises — OK")
PY

# 5. parallel-suite-runner: a parallel run reports the same failures a serial
# run would, and every way it can go wrong fails CLOSED: failures are judged
# against a baseline BY TEST ID; a hung shard fails the run after one re-run and
# is never a failing test id; a crashed shard, an abnormal exit, a lost id, a
# run where no test ran, and an unreadable baseline all fail. The fixture is a
# synthetic stdlib-unittest package; the implementation is the largest
# ```python block on the page, driven only through its command line.
PSR_PAGE="$ROOT/tool-corpus/testing/parallel-suite-runner.md"
[[ -f "$PSR_PAGE" ]] || { echo "parallel-suite-runner: page not found: $PSR_PAGE" >&2; exit 1; }
python3 - "$PSR_PAGE" "$TMP/psr.py" <<'PY'
import re, sys, pathlib
text = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")
if not re.search(r"\*\*Stability:\*\*\s*\*\*portable", text):
    sys.exit("parallel-suite-runner: the page does not claim portable stability, "
             "so section 1 never compiles its implementation")
blocks = re.findall(r"```python\n(.*?)```", text, re.S)
if not blocks:
    sys.exit("parallel-suite-runner: the page embeds no ```python implementation")
pathlib.Path(sys.argv[2]).write_text(max(blocks, key=len))
PY
python3 - "$TMP/psr.py" "$TMP/psr" <<'PY'
import re, subprocess, sys, textwrap, pathlib

TOOL, WORK = sys.argv[1], pathlib.Path(sys.argv[2])
SEP = "=" * 70
ID = re.compile(r"^(FAIL|ERROR): .+$")

BASE = {
    # Importable only if the start dir is on sys.path, as `discover -s` puts it.
    "helper.py": "VALUE = 42\n",
    "test_pass.py": """
        import os, unittest, helper
        class P(unittest.TestCase):
            def test_one(self): self.assertEqual(helper.VALUE, 42)
            def test_cwd_is_repo(self): self.assertTrue(os.path.isfile("MARKER"))
    """,
    "test_known.py": """
        import unittest
        class K(unittest.TestCase):
            def test_known_fail(self): self.fail("known")
            def test_error(self): raise RuntimeError("boom")
    """,
}
n = 0
def repo(extra=None, base=True):
    global n
    n += 1
    r = WORK / f"r{n}"
    (r / "tests").mkdir(parents=True)
    (r / "MARKER").write_text("")
    for name, body in {**(BASE if base else {}), **(extra or {})}.items():
        (r / "tests" / name).write_text(textwrap.dedent(body))
    return r

def serial_ids(r):
    p = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests",
                        "-p", "test_*.py"], cwd=r, capture_output=True, text=True)
    lines = p.stderr.splitlines()
    return {l for i, l in enumerate(lines) if i and lines[i - 1] == SEP and ID.match(l)}

def run(r, *args):
    logs = r.parent / (r.name + "-logs")
    p = subprocess.run([sys.executable, TOOL, "--repo", str(r), "-s", "tests",
                        "--logs", str(logs), *args],
                       capture_output=True, text=True, timeout=120)
    out = p.stdout + p.stderr
    ids_file = logs / "failing-ids.txt"
    ids = set(filter(None, ids_file.read_text().splitlines())) if ids_file.exists() else None
    return p.returncode, out, ids

def check(cond, msg, out=""):
    if not cond:
        sys.exit(f"parallel-suite-runner: {msg}\n--- tool output ---\n{out}")

# The failing ids a parallel run reports are exactly the ids a serial run reports.
r = repo()
known = serial_ids(r)
assert len(known) == 2, f"fixture drifted: {known}"
rc, out, ids = run(r, "-j", "2")
check(ids == known, f"failing ids {ids} differ from a serial discover run {known}", out)
check(rc == 1, f"no baseline given, so every failure is new, yet exit {rc}", out)

# Baseline BY ID: carried ids pass, a new id fails and is named.
r = repo()
base = WORK / "base-all.txt"; base.write_text("\n".join(sorted(known)) + "\n")
rc, out, _ = run(r, "--baseline", str(base))
check(rc == 0, f"every failing id is in the baseline, yet exit {rc}", out)
check("new failing ids: 0" in out, "a fully baselined run did not report zero new ids", out)
base = WORK / "base-part.txt"
base.write_text("".join(i + "\n" for i in sorted(known) if "test_error" not in i))
rc, out, _ = run(r, "--baseline", str(base))
check(rc == 1, f"an id outside the baseline did not fail the run (exit {rc})", out)
new_block = out.split("new failing ids: 1\n", 1)
check(len(new_block) == 2 and "test_error" in new_block[1].split("\n", 1)[0],
      "the one new id was not listed under 'new failing ids'", out)
# The same number of failures with a DIFFERENT id is still a new failure.
r = repo({"test_known.py": """
    import unittest
    class K(unittest.TestCase):
        def test_known_fail(self): self.fail("known")
        def test_error_renamed(self): raise RuntimeError("boom")
"""})
rc, out, _ = run(r, "--baseline", str(WORK / "base-all.txt"))
check(rc == 1, "an equal failure COUNT with a new id passed: ids were not compared", out)

# Unreadable shards fail closed, even with every failing id baselined.
hang = """
    import time, unittest
    class H(unittest.TestCase):
        def test_hang(self):
            with open("attempts-hang.txt", "a") as f: f.write("x")
            time.sleep(60)
"""
r = repo({"test_hang.py": hang})
rc, out, ids = run(r, "--timeout", "3", "--baseline", str(WORK / "base-all.txt"))
attempts = len((r / "attempts-hang.txt").read_text())
check(attempts == 2, f"a persistently hung shard ran {attempts} time(s); expected exactly 2", out)
check(rc == 1, f"a shard that timed out twice did not fail the run (exit {rc})", out)
check("test_hang: timed out" in out, "the hung shard was not named as timed out", out)
check(ids is not None and not any("test_hang" in i for i in ids),
      f"a timeout was counted as a failing test id: {ids}", out)

r = repo({"test_crash.py": "import os\nos._exit(3)\n"})
rc, out, _ = run(r, "--baseline", str(WORK / "base-all.txt"))
check(rc == 1, f"a shard that crashed before its run line did not fail closed (exit {rc})", out)
check("test_crash:" in out, "the crashed shard was not named", out)

r = repo({"test_late_exit.py": """
    import atexit, os, unittest
    atexit.register(lambda: os._exit(3))
    class L(unittest.TestCase):
        def test_ok(self): pass
"""})
rc, out, _ = run(r, "--baseline", str(WORK / "base-all.txt"))
check(rc == 1, f"an abnormal exit after a complete run did not fail closed (exit {rc})", out)
check("test_late_exit: exit 3" in out, "the abnormal exit was not named with its code", out)

# A shard whose parsed ids do not account for its failures+errors count has
# lost an id: fail closed, even though the one id it did print is baselined.
# The fixture rewrites its own ERROR header so that no id follows the separator,
# which is how a mangled or interleaved log loses an id.
r = repo({"test_lostid.py": """
    import unittest
    _desc = unittest.TextTestResult.getDescription
    def _lose(self, test):
        d = _desc(self, test)
        return "\\n" + d if "test_lost_error" in test.id() else d
    unittest.TextTestResult.getDescription = _lose
    class L(unittest.TestCase):
        def test_visible_fail(self): self.fail("visible")
        def test_lost_error(self): raise RuntimeError("lost")
"""})
lostbase = WORK / "base-lost.txt"
lostbase.write_text("\n".join(sorted(known)) + "\nFAIL: test_visible_fail (test_lostid.L.test_visible_fail)\n")
rc, out, ids = run(r, "--baseline", str(lostbase))
check(ids is not None and "FAIL: test_visible_fail (test_lostid.L.test_visible_fail)" in ids
      and not any("test_lost_error" in i for i in ids),
      f"fixture drifted: the lost-id shard parsed {ids}", out)
check(rc == 1, f"a shard with 2 failures+errors but 1 parsed id passed (exit {rc})", out)
check("test_lostid:" in out, "the shard that lost an id was not named", out)

# A run in which no test ran at all is not a pass.
r = repo({"test_empty.py": "import unittest\n"}, base=False)
rc, out, _ = run(r)
check(rc == 1, f"a suite where zero tests ran exited {rc}, not 1", out)
check("no tests ran" in out, "a zero-test run did not say 'no tests ran'", out)

# A baseline that cannot be read is a usage error, never an empty baseline.
r = repo()
rc, out, _ = run(r, "--baseline", str(WORK / "no-such-baseline.txt"))
check(rc == 2, f"a missing baseline file exited {rc}, not the usage error 2", out)
bad = WORK / "base-bad.txt"; bad.write_text("test_foo (x.Y.test_foo)\n")
rc, out, _ = run(r, "--baseline", str(bad))
check(rc == 2, f"a malformed baseline line exited {rc}, not the usage error 2", out)

print("  parallel-suite-runner: id-baselined, hung shard re-run once, "
      "unreadable shards fail closed — OK")
PY

# 6. Every portable page that ships a runnable offline self-test has that
# self-test RUN here, from the blocks extracted off the page, not only parsed by
# section 1. A self-test PASS printed on a page is the author's recorded run;
# without this step nothing re-runs it after the page is edited. Each row also
# re-runs the self-test on a MUTATED COPY of one extracted block (the page is
# never touched) with the property the page exists for broken, and requires a
# nonzero exit with no pass line: a self-test that still passes there checks
# nothing. A fake `docker` on PATH fails loudly, so a self-test that claims to be
# offline but reaches the container engine is caught, not silently served. The
# table is data, and a portable page that names a self-test (`--self-test` or a
# `selftest.sh`) with no row here fails the step: the gap this step closes must
# not reopen with the next page.
mkdir -p "$TMP/fakebin"
cat > "$TMP/fakebin/docker" <<EOF
#!/usr/bin/env bash
echo "\$*" >> "$TMP/fakebin/docker-called"
echo "fake docker: an offline self-test reached the container engine" >&2
exit 97
EOF
chmod +x "$TMP/fakebin/docker"
python3 - "$ROOT" "$TMP/selftests" "$TMP/fakebin" <<'PY'
import os, re, shutil, subprocess, sys, pathlib

root, work, fakebin = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]), sys.argv[3]
work.mkdir()
env = dict(os.environ, PATH=fakebin + os.pathsep + os.environ.get("PATH", ""))

# page -> files to extract (name, the marker that picks its block), the
# command the page's "How to run the tests" line names, the pass line it
# prints, and one mutation (file, exact text, replacement) that breaks a
# property the page's section 6 says the self-test asserts.
ROWS = [
    ("testing/behavior-baseline-oracle",
     [("baseline.py", '"""behavior-baseline-oracle:')],
     ["python3", "baseline.py", "--self-test"], r"^self-test: PASS",
     ("baseline.py", "if old.exists() and not rebaseline:", "if False:"),
     "a second capture without --rebaseline is refused"),
    ("testing/in-network-e2e-harness",
     [("harness.py", '"""in-network-e2e-harness:')],
     ["python3", "harness.py", "--self-test"], r"^self-test: PASS",
     ("harness.py",
      'raise RouteDown(f"precondition {path} answered {status}: route not alive")',
      "pass"),
     "a 404 or 500 precondition raises RouteDown"),
    ("testing/live-contract-check-harness",
     [("contract-checks.sh", "# contract-checks.sh:"),
      ("lint-harness.sh", "# lint-harness.sh FILE:"),
      ("selftest.sh", "# selftest.sh:")],
     ["bash", "selftest.sh"], r"^selftest: PASS",
     ("lint-harness.sh", '&& fail "set -x"', "&& true"),
     "the lint fails a planted set -x"),
    ("testing/touched-file-lint-hook",
     [("touched_lint.py", '"""touched-file-lint-hook:')],
     ["python3", "touched_lint.py", "--self-test"], r"^self-test: PASS",
     ("touched_lint.py", '("ls-files", "-z", "--others", "--exclude-standard")',
      '("ls-files", "-z", "--exclude-standard")'),
     "an untracked new file is linted"),
    ("ops/resolved-dependency-gate",
     [("resolved-dependency-gate.py", '"""resolved-dependency-gate:')],
     ["python3", "resolved-dependency-gate.py", "--self-test"], r"^self-test: PASS \(\d+ checks\)",
     ("resolved-dependency-gate.py",
      'say(False, f"floor {coord}>={minimum}: absent, so nothing was checked")',
      'say(True, f"floor {coord}>={minimum}: absent, so nothing was checked")'),
     "a floor on an absent artifact fails"),
    ("ops/image-reference-pin-lint",
     [("image-pin-lint.py", '"""image-reference-pin-lint:')],
     ["python3", "image-pin-lint.py", "--self-test"], r"^self-test: PASS \(\d+ checks\)",
     ("image-pin-lint.py", "sha512:[0-9a-f]{128}", "sha512:[0-9a-f]{64}"),
     "a sha512 digest is pinned"),
    ("ops/source-default-credential-gate",
     [("source-default-credential-gate.py", '"""source-default-credential-gate:')],
     ["python3", "source-default-credential-gate.py", "--self-test"], r"^self-test: PASS \(\d+ checks\)",
     ("source-default-credential-gate.py",
      "if QUERY_PW.search(literal_part(default)):", "if False:"),
     "a query-parameter password in a default is a finding"),
    ("ops/owner-scoped-idempotent-seed",
     [("seeded-world-verifier.py", '"""seeded-world-verifier:')],
     ["python3", "seeded-world-verifier.py", "--self-test"], r"^self-test: PASS \(\d+ checks\)",
     ("seeded-world-verifier.py", 'report(False, name, f"id {exc} was never captured")',
      'report(True, name, f"id {exc} was never captured")'),
     "a path whose id was never captured fails instead of guessing"),
    ("ops/lenient-json-response-parser",
     [("lenient-json.py", '"""lenient-json:')],
     ["python3", "lenient-json.py", "--self-test"], r"^self-test: PASS",
     ("lenient-json.py", "parse_constant=_refuse_constant,", ""),
     "NaN, Infinity and -Infinity raise"),
    ("ops/destructive-command-guard-hook",
     [("destructive-guard.py", '"""destructive-guard:')],
     ["python3", "destructive-guard.py", "--self-test"], r"^self-test: PASS",
     ("destructive-guard.py",
      'if sub == "reset" and re.search(r"(?:^|\\s)--hard\\b", rest):', "if False:"),
     "git reset --hard is denied"),
    ("ops/orphaned-scoped-config-auditor",
     [("orphaned-scope-config.py", '"""orphaned-scope-config:')],
     ["python3", "orphaned-scope-config.py", "--self-test"], r"^self-test: PASS",
     ("orphaned-scope-config.py",
      'scopes.update(c for c in val.get("children", []) or [] if isinstance(c, str))',
      "pass"),
     "every children name is a scope (an empty group counts)"),
    ("ops/chained-pipeline-run-driver-azure-devops",
     [("chained-run-ado.py", '"""chained-run-ado:')],
     ["python3", "chained-run-ado.py", "--self-test"], r"^self-test: PASS",
     ("chained-run-ado.py", '{alias: {"runId": run_id}}', '{alias: {"runId": None}}'),
     "B is bound to A's run id"),
    ("ops/container-vuln-scan-and-aggregate",
     [("vuln-scan-aggregate.py", '"""vuln-scan-aggregate:')],
     ["python3", "vuln-scan-aggregate.py", "--self-test"], r"^self-test: PASS \(\d+ checks\)",
     ("vuln-scan-aggregate.py", '("V40Score", "V3Score", "V2Score")',
      '("V40Score", "V31Score", "V30Score")'),
     "a V3Score is read"),
]

def fail(msg, out=""):
    sys.exit(f"self-test step: {msg}" + (f"\n--- output ---\n{out[-3000:]}" if out else ""))

# Coverage: every portable page that names a self-test has a row.
covered = {r[0] for r in ROWS}
for page in sorted((root / "tool-corpus").rglob("*.md")):
    text = page.read_text(encoding="utf-8")
    if not re.search(r"\*\*Stability:\*\*\s*\*\*portable", text):
        continue
    rel = str(page.relative_to(root / "tool-corpus"))[:-3]
    if re.search(r"--self-test|\bselftest\.sh\b", text) and rel not in covered:
        fail(f"tool-corpus/{rel}.md is portable and names a self-test, but no "
             f"row here runs it: the page's PASS is a recorded claim, not a gate")

def run(d, cmd):
    marker = pathlib.Path(fakebin) / "docker-called"
    if marker.exists():
        marker.unlink()
    try:
        p = subprocess.run(cmd, cwd=d, env=env, capture_output=True, text=True, timeout=300)
    except subprocess.TimeoutExpired as exc:
        return 124, f"timed out after 300s: {exc}", False
    return p.returncode, p.stdout + p.stderr, marker.exists()

def row(page, files, cmd, passline, mfile, old, new, prop):
    name = page.split("/")[-1]
    path = root / "tool-corpus" / f"{page}.md"
    if not path.is_file():
        return note(f"{name}: page not found: {path}")
    text = path.read_text(encoding="utf-8")
    if not re.search(r"\*\*Stability:\*\*\s*\*\*portable", text):
        return note(f"{name}: the page no longer claims portable stability")
    code = re.findall(r"(?ms)^```(?:python|bash|sh)\n(.*?)^```", text)
    d = work / name
    d.mkdir()
    for fname, mark in files:
        hit = [b for b in code if mark in b]
        if len(hit) != 1:
            return note(f"{name}: expected exactly one code block carrying {mark!r} "
                 f"(the block the page calls {fname}), found {len(hit)}")
        (d / fname).write_text(hit[0])
    # The extracted self-test, as the page says to run it.
    rc, out, docker = run(d, cmd)
    if docker:
        return note(f"{name}: the offline self-test called docker", out)
    if rc != 0 or not re.search(passline, out, re.M):
        return note(f"{name}: `{' '.join(cmd)}` on the blocks extracted from the page "
             f"exited {rc} without the pass line /{passline}/", out)
    # The same self-test on a copy with one property broken must fail.
    m = work / f"{name}.mutant"
    shutil.copytree(d, m)
    src = (m / mfile).read_text()
    if src.count(old) != 1:
        return note(f"{name}: the mutation target {old!r} occurs {src.count(old)} time(s) "
             f"in {mfile}, not once; re-aim the mutation at the code as it now reads")
    (m / mfile).write_text(src.replace(old, new))
    rc, out, docker = run(m, cmd)
    if rc == 0 or re.search(passline, out, re.M):
        return note(f"{name}: with '{prop}' mutated out of {mfile}, the self-test still "
             f"passed (exit {rc}); it does not check what its page says it checks", out)
    print(f"  {name}: extracted self-test passes; fails with '{prop}' mutated out — OK")

# Every row runs, so one red row does not hide the state of the others.
failures = []
def note(msg, out=""):
    failures.append(msg + (f"\n--- output ---\n{out[-2000:]}" if out else ""))

for page, files, cmd, passline, (mfile, old, new), prop in ROWS:
    row(page, files, cmd, passline, mfile, old, new, prop)
if failures:
    sys.exit("self-test step: %d of %d row(s) RED\n" % (len(failures), len(ROWS))
             + "\n".join("  " + f for f in failures))
PY

printf 'tool-corpus portability: PASS\n'
