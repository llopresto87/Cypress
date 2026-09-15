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
# The verifier calls `yaml.safe_load`, and PyYAML is not stdlib. This block used
# to run only `if python3 -c 'import yaml'` and otherwise announce a SKIP and
# print PASS — and the seed's own CI has no `pip install` step, so BOTH legs took
# the skip branch and reported a green gate with a mandatory check unexecuted.
# That is the sentence this release closed for pytest, surviving one file over.
#
# The dependency is not removable (it belongs to the shipped page, which is
# transcribed knowledge and not ours to rewrite for a test's convenience), and
# adding it would make a third-party package a hard requirement of the default
# gate. So the FIXTURE supplies what the fixture needs: a stdlib `safe_load`
# over the two files written immediately below, put on sys.path only when the
# real parser is absent. It parses nested maps of scalars and nothing else,
# which is exactly what these two files are — and if a future fixture outgrows
# it, it raises rather than guessing.
if ! python3 -c 'import yaml' 2>/dev/null; then
  mkdir -p "$TMP/yamlshim"
  cat > "$TMP/yamlshim/yaml.py" <<'SHIM'
"""Enough of `yaml.safe_load` for this suite's own fixtures, in stdlib.

Nested mappings, two-space indentation, `key:` and `key: scalar`. Anything else
raises, because a shim that guesses is worse than no shim: it would let the
verifier under test pass over input it never really parsed.
"""


class YAMLError(Exception):
    pass


def safe_load(text):
    if hasattr(text, "read"):
        text = text.read()
    root = {}
    stack = [(-1, root)]
    for lineno, raw in enumerate(text.splitlines(), 1):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        stripped = raw.lstrip(" ")
        indent = len(raw) - len(stripped)
        if raw[:indent].strip(" "):
            raise YAMLError(f"line {lineno}: tabs are not supported by this shim")
        if stripped.startswith("- "):
            raise YAMLError(f"line {lineno}: sequences are not supported by this shim")
        if ":" not in stripped:
            raise YAMLError(f"line {lineno}: not a key: {raw!r}")
        key, _, value = stripped.partition(":")
        while stack and indent <= stack[-1][0]:
            stack.pop()
        if not stack:
            raise YAMLError(f"line {lineno}: dedent past the document root")
        parent = stack[-1][1]
        value = value.strip()
        if value:
            parent[key.strip()] = value
        else:
            child = {}
            parent[key.strip()] = child
            stack.append((indent, child))
    return root
SHIM
  export PYTHONPATH="$TMP/yamlshim${PYTHONPATH:+:$PYTHONPATH}"
  python3 -c 'import yaml' \
    || { echo "the stdlib YAML shim did not import — the layered-config check would silently skip" >&2; exit 1; }
  echo "  (no PyYAML here; using the suite's own stdlib safe_load for these fixtures)"
fi

if true; then
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
fi

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

printf 'tool-corpus portability: PASS\n'
