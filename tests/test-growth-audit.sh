#!/usr/bin/env bash
# test-growth-audit.sh — the coverage gate does what protocols/grow.md and
# protocols/graft.md promise: growth is proven against a recorded plan, not
# asserted about itself.
#
# The failures pinned here are the ones that shipped for real. Plants arrived
# carrying a ui-ux-designer with no design/ material, a legal analyst with no
# corpus, and library pages written from model memory rather than retrieved
# documentation — each invisible because no gate ever asked. Every case below
# is one of those made mechanical.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AUDIT="$ROOT/tools/growth-audit.py"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
PLANT="$TMP/plant"

fail() { printf 'test-growth-audit: FAIL — %s\n' "$1" >&2; exit 1; }

# exit code of the audit, without tripping `set -e`
audit() { python3 "$AUDIT" "$PLANT" "$ROOT" "$@" >"$TMP/out" 2>&1 && echo 0 || echo $?; }
# same, for a plant other than the main fixture
audit_at() { local d="$1"; shift; python3 "$AUDIT" "$d" "$ROOT" "$@" >/dev/null 2>&1 && echo 0 || echo $?; }

mkdir -p "$PLANT"
bash "$ROOT/install.sh" claude-code --project-dir "$PLANT" >/dev/null 2>&1

# --- 1. a plant with no record cannot be called grown ----------------------
[[ "$(audit)" == 1 ]] || fail "a plant with no coverage record passed the gate"
grep -q "MISSING" "$TMP/out" || fail "a missing record was not reported as MISSING"

# --- 2. --plan derives its rows from the SEED, not from the record ---------
# This is what makes a forgotten collection impossible: adding a template to
# the seed adds a required row to every plant's next audit.
[[ "$(audit --plan)" == 1 ]] || fail "--plan on an empty inventory should report the empty inventory"
for row in "design/" "tools/" "legal/" "best-practices/" "runbooks/rollback.md"; do
    grep -q "collection $row" "$TMP/out" || fail "--plan omitted the $row row"
done
# The two specialists added late to the roster must each get an agent row.
for a in ui-ux-designer legal; do
    grep -q "agent $a" "$TMP/out" || fail "--plan omitted the $a agent row"
done
grep -q "inventory is empty" "$TMP/out" || fail "an empty inventory was not called out"

# --- 3. an inventory item's planned artifacts are checked, one by one ------
python3 - "$PLANT" <<'PY'
import json, sys, pathlib
p = pathlib.Path(sys.argv[1])/".cypress/coverage.json"
rec = json.loads(p.read_text())
(pathlib.Path(sys.argv[1])/"app.csproj").write_text("<Project/>\n")
rec["inventory"] = [{"kind": "runtime", "name": "dotnet", "version": "9.0",
                     "significance": "core", "evidence": ["app.csproj:1"]}]
p.write_text(json.dumps(rec, indent=2) + "\n")
PY
python3 "$AUDIT" "$PLANT" "$ROOT" --plan >/dev/null
[[ "$(audit)" == 1 ]] || fail "an ungrown inventory item passed the gate"
grep -q "UNGROWN" "$TMP/out" \
    || fail "a missing planned artifact was not reported UNGROWN"
grep -q "libraries/dotnet.md — does not exist" "$TMP/out" \
    || fail "the missing library page was not named"
grep -q "best-practices/dotnet.md — does not exist" "$TMP/out" \
    || fail "the missing best-practices page was not named"
grep -q "UNGROUNDED" "$TMP/out" \
    || fail "a runtime with no retrieved upstream source was not UNGROUNDED"

# --- 4. a scaffold is not coverage ----------------------------------------
# A page that exists but is still the seed's blank form, or still carries a
# {{placeholder}}, shadows the authored page a cold agent needed.
mkdir -p "$PLANT/docs/graph/libraries"
printf '# dotnet\n\n{{what this library is}}\n' > "$PLANT/docs/graph/libraries/dotnet.md"
audit >/dev/null
grep -q "HOLLOW" "$TMP/out" \
    || fail "a page still carrying a template placeholder was not HOLLOW"
grep -q "template placeholder {{what this library is}}" "$TMP/out" \
    || fail "the placeholder that made the page hollow was not named"

# --- 5. an absence must be established, not just asserted ------------------
python3 - "$PLANT" <<'PY'
import json, sys, pathlib
p = pathlib.Path(sys.argv[1])/".cypress/coverage.json"
rec = json.loads(p.read_text())
for c in rec["collections"]:
    if c["name"] == "legal/":
        c["status"] = "ABSENT"          # no reason, no searched paths
p.write_text(json.dumps(rec, indent=2) + "\n")
PY
audit >/dev/null
grep -q "UNJUSTIFIED  collection legal/" "$TMP/out" \
    || fail "an ABSENT row with no reason was accepted"

# --- 6. the plant's own files can contradict a COVERED claim ---------------
python3 - "$PLANT" <<'PY'
import json, sys, pathlib
p = pathlib.Path(sys.argv[1])/".cypress/coverage.json"
rec = json.loads(p.read_text())
for c in rec["collections"]:
    if c["name"] == "design/":
        c.update(status="COVERED", evidence=[])
for a in rec["agents"]:
    if a["name"] == "ui-ux-designer":
        a["status"] = "COVERED"
p.write_text(json.dumps(rec, indent=2) + "\n")
PY
audit >/dev/null
grep -q "CONTRADICTED collection design/" "$TMP/out" \
    || fail "design/ claimed COVERED with only a scaffold was accepted"
grep -q "CONTRADICTED agent ui-ux-designer" "$TMP/out" \
    || fail "ui-ux-designer claimed COVERED with no design material was accepted"

# --- 7. --agents answers the roster question on its own -------------------
audit --agents >/dev/null
grep -q "agent legal" "$TMP/out" || fail "--agents did not report the legal row"
! grep -qE "^  [A-Z]+ +collection " "$TMP/out" \
    || fail "--agents leaked collection rows"

# --- 8. a fully grown plant passes ----------------------------------------
# A gate that can never go green is not a gate.
python3 - "$PLANT" "$ROOT" <<'PY'
import json, sys, pathlib
plant, seed = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
g = plant/"docs/graph"
BODY = "\n## Fact\n\n" + ("A project-specific fact with its source path. " * 14) + "\n"
def leaf(rel):
    f = g/rel; f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(f"# {f.stem}\n{BODY}")
rec = json.loads((plant/".cypress/coverage.json").read_text())
# every collection the seed installs is either filled or honestly absent
for c in rec["collections"]:
    name = c["name"]
    rel = name.rstrip("/") + "/overview.md" if name.endswith("/") else name
    leaf(rel)
    c.update(status="COVERED", evidence=[f"docs/graph/{rel}"], leaves=1,
             reason="", searched=[], blocker="")
for a in rec["agents"]:
    a.update(status="COVERED", artifacts=[], reason="", searched=[], blocker="")
leaf("sources/normalized/dotnet-9-docs.md")
leaf("libraries/dotnet.md"); leaf("best-practices/dotnet.md")
for it in rec["inventory"]:
    it["status"] = "COVERED"
    it["grounding"]["sources"] = ["docs/graph/sources/normalized/dotnet-9-docs.md"]
(plant/".cypress/coverage.json").write_text(json.dumps(rec, indent=2) + "\n")
PY
[[ "$(audit)" == 0 ]] || { cat "$TMP/out" >&2; fail "a fully grown plant did not pass the gate"; }
grep -q "coverage complete" "$TMP/out" || fail "a passing audit did not say so"

# --- 9. a graft to a newer seed re-opens the record ------------------------
# "Grafted is not grown": the record was planned against an older seed, so the
# audit must refuse it rather than report coverage it never checked.
python3 - "$PLANT" <<'PY'
import json, sys, pathlib
p = pathlib.Path(sys.argv[1])/".cypress/coverage.json"
rec = json.loads(p.read_text()); rec["seed_version"] = "0.0.1-old"
p.write_text(json.dumps(rec, indent=2) + "\n")
PY
[[ "$(audit)" == 1 ]] || fail "a record planned against an older seed still passed"
grep -q "STALE" "$TMP/out" || fail "a stale record was not reported STALE"

# --- 10. the false-green regression: every bypass the first cut allowed ----
# A one-byte edit to the seed's own design/README.md and legal/index.md once
# marked those collections COVERED, and their agents with them — the exact
# "a one-word edit passes" failure this tool was written to close. Alongside
# it: an inventory row waved through with a bare UNKNOWN, a planned artifact
# with no path, and grounding "cited" to the sources DIRECTORY. Each of these
# reported green on an ungrown plant.
rm -rf "$TMP/s9"; mkdir -p "$TMP/s9"
bash "$ROOT/install.sh" claude-code --project-dir "$TMP/s9" >/dev/null 2>&1
python3 "$AUDIT" "$TMP/s9" "$ROOT" --plan >/dev/null 2>&1 || true
printf 'x\n' >> "$TMP/s9/docs/graph/legal/index.md"
printf 'x\n' >> "$TMP/s9/docs/graph/design/README.md"
python3 - "$TMP/s9" <<'PY'
import json, pathlib, sys
p = pathlib.Path(sys.argv[1])/".cypress/coverage.json"
r = json.loads(p.read_text())
for c in r["collections"]:
    c.update(status="COVERED", evidence=[], leaves=1)
for a in r["agents"]:
    a["status"] = "COVERED"
r["inventory"] = [
    {"kind": "regulatory-exposure", "name": "gdpr", "status": "UNKNOWN",
     "evidence": ["docs/graph/index.md"]},
    {"kind": "framework", "name": "react", "status": "COVERED",
     "evidence": ["docs/graph/index.md"], "expect": [{}],
     "grounding": {"required": True, "sources": ["docs/graph/sources/"]}},
]
p.write_text(json.dumps(r, indent=2) + "\n")
PY
out9="$(python3 "$AUDIT" "$TMP/s9" "$ROOT" 2>&1)" && fail "the false-green scenario passed the gate"
grep -q "CONTRADICTED collection design/" <<<"$out9" \
    || fail "design/ covered by a one-byte edit to the seed's own README passed"
grep -q "CONTRADICTED collection legal/" <<<"$out9" \
    || fail "legal/ covered by a one-byte edit to the seed's own index passed"
grep -q "CONTRADICTED agent ui-ux-designer" <<<"$out9" \
    || fail "ui-ux-designer passed with no design material"
grep -q "UNJUSTIFIED  regulatory-exposure gdpr" <<<"$out9" \
    || fail "an inventory row closed with a bare UNKNOWN and no blocker"
grep -q "a planned artifact with no path" <<<"$out9" \
    || fail "a planned artifact with no path was skipped silently"
grep -q "UNGROUNDED   framework react" <<<"$out9" \
    || fail "grounding cited to the sources directory was accepted"

# --- 11. agent coverage is all-of, not any-of -----------------------------
# ui-ux-designer reads design/ AND best-practices/; one best-practices page
# written for the implementer must not cover the designer.
python3 - "$TMP/s9" <<'PY'
import json, pathlib, sys
plant = pathlib.Path(sys.argv[1])
body = "\n" + ("A normative standard and this project's stance against it. " * 14)
(plant/"docs/graph/best-practices/react.md").write_text("# react\n" + body)
p = plant/".cypress/coverage.json"; r = json.loads(p.read_text())
for a in r["agents"]:
    a["status"] = "COVERED" if a["name"] == "ui-ux-designer" else ""
p.write_text(json.dumps(r, indent=2) + "\n")
PY
out11="$(python3 "$AUDIT" "$TMP/s9" "$ROOT" --agents 2>&1)" || true
grep -q "CONTRADICTED agent ui-ux-designer" <<<"$out11" \
    || fail "one best-practices page covered an agent whose design/ is empty"
grep -q "design/ holds no filled leaf" <<<"$out11" \
    || fail "the audit did not name WHICH declared collection was empty"

# --- 12. an absolute path is not a claim about this plant ------------------
python3 - "$TMP/s9" <<'PY'
import json, pathlib, sys
p = pathlib.Path(sys.argv[1])/".cypress/coverage.json"; r = json.loads(p.read_text())
r["inventory"] = [{"kind": "framework", "name": "react", "status": "COVERED",
                   "evidence": ["/etc/hostname"],
                   "expect": [{"path": "libraries/react.md"}],
                   "grounding": {"required": False, "sources": []}}]
p.write_text(json.dumps(r, indent=2) + "\n")
PY
out12="$(python3 "$AUDIT" "$TMP/s9" "$ROOT" 2>&1)" || true
grep -q "DANGLING" <<<"$out12" \
    || fail "an absolute path outside the plant was accepted as evidence"

# --- 13. a malformed record is named, not a traceback ---------------------
printf '{"schema": "cypress.coverage/1", "collections": "nope"}\n' \
    > "$TMP/s9/.cypress/coverage.json"
[[ "$(audit_at "$TMP/s9")" == 2 ]] || fail "a malformed record did not exit 2"

# --- 14. an honestly-empty plant passes on ABSENT rows ---------------------
# The green case above goes green by covering everything. A real plant with no
# user interface and no regulatory exposure must be able to pass by ESTABLISHING
# those absences — reason plus the paths searched — and that path has its own
# failure mode: the seed's own scaffold sitting in the empty collection. The
# audit must name it and point at the remedy rather than passing over it.
rm -rf "$TMP/absent"; mkdir -p "$TMP/absent"
bash "$ROOT/install.sh" claude-code --project-dir "$TMP/absent" >/dev/null 2>&1
python3 "$AUDIT" "$TMP/absent" "$ROOT" --plan >/dev/null 2>&1 || true
python3 - "$TMP/absent" <<'PY'
import json, pathlib, sys
p = pathlib.Path(sys.argv[1])/".cypress/coverage.json"; r = json.loads(p.read_text())
for c in r["collections"]:
    c.update(status="ABSENT", reason="the source shows no such evidence",
             searched=["src/"], evidence=[], leaves=0)
for a in r["agents"]:
    a.update(status="ABSENT", reason="its collections are absent-with-reason",
             searched=["src/"])
r["inventory"] = [{"kind": "domain", "name": "batch etl", "status": "ABSENT",
                   "reason": "no artifact of its own; the architecture node owns it",
                   "searched": ["src/"], "evidence": ["docs/graph/index.md"],
                   "expect": [], "grounding": {"required": False, "sources": []}}]
p.write_text(json.dumps(r, indent=2) + "\n")
PY
# The seed's scaffolds are still sitting in those collections: that must fail,
# and the message must name the remedy rather than just contradicting.
out14="$(python3 "$AUDIT" "$TMP/absent" "$ROOT" 2>&1)" || true
grep -q "still carries the seed's unfilled scaffold" <<<"$out14" \
    || fail "an ABSENT row over an untouched scaffold did not name it as one"
grep -q -- "--unfilled --rename" <<<"$out14" \
    || fail "the scaffold contradiction did not name the remedy"
# Apply the remedy the message names, then the honest plant passes.
python3 "$ROOT/tools/graft-audit.py" "$TMP/absent" "$ROOT" --unfilled --rename >/dev/null 2>&1 || true
[[ "$(audit_at "$TMP/absent")" == 0 ]] || {
    python3 "$AUDIT" "$TMP/absent" "$ROOT" >&2
    fail "an honestly-empty plant could not pass by establishing its absences"
}

printf 'growth coverage gate: PASS\n'
