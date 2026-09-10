#!/usr/bin/env bash
# test-growth-audit.sh — the coverage gate does what protocols/grow.md and
# protocols/graft.md promise: growth is proven against a recorded plan, not
# asserted about itself.
#
# The failures pinned here are the ones that shipped for real. Plants arrived
# carrying a ui-ux-designer with no design/ material, a legal analyst with no
# corpus, and library pages written from model memory rather than retrieved
# documentation — each invisible because no gate ever asked. Every case below
# is one of those made mechanical. Cases 42-45 came from one real graft the
# audit passed: an index line never written, a retrieval with no artifact
# behind it, an absence that had found the material, and an owner's decision
# filed in the record and never put to the owner.
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
# 7.11.0: agent.legal declares legal/corpus/, so a grown plant is one whose
# owner answered the corpus question. `yes` is that plant; case 14 covers the
# owner who answered `no` and establishes the absence instead.
bash "$ROOT/install.sh" claude-code --project-dir "$PLANT" --legal-corpus yes >/dev/null 2>&1
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
# 7.10.0: a normalized snapshot keeps its raw sibling, or says why not.
src = g/"sources/normalized/dotnet-9-docs.md"
src.write_text("---\nraw: withheld — the upstream license forbids redistribution; "
               "URL and date are in the index row\n---\n" + src.read_text())
leaf("libraries/dotnet.md"); leaf("best-practices/dotnet.md")
# 7.5.0: a core stack element also owes the expertise node that says when it is
# in play and routes to the two leaves above. It carries the `libraries:` edge
# to its own pin home, because that is where the version distinction lives.
(g/"nodes").mkdir(parents=True, exist_ok=True)
(g/"nodes/expertise.dotnet.md").write_text(
    "---\nid: expertise.dotnet\ntier: 2\nkind: expertise\norigin: project\n"
    "title: dotnet — when this expertise is in play\nowns:\n"
    "  - dotnet.applicability\n  - dotnet.composition\nrequires:\n"
    "libraries:\n  - dotnet\nload_when:\n  - \"dotnet, csharp\"\n"
    "est_tokens: 120\n---\n" + BODY)
for it in rec["inventory"]:
    it["status"] = "COVERED"
    it["grounding"]["sources"] = ["docs/graph/sources/normalized/dotnet-9-docs.md"]
    # a core item answers the staffing question. The expertise node above is
    # owed either way; declining an AGENT on top of it is the usual answer.
    it["expert"] = {"warranted": False, "why": "the expertise node and its "
                    "composition cover it; nothing here needs a different "
                    "tool, model, stance, or isolation"}
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

# --- 15. an expert that was never projected is not a specialist -----------
# The second half of growth's promise: it is supposed to leave behind experts
# this project needs and the base roster lacks. Through 7.3.x nothing checked
# that it happened, and nothing checked that it TOOK — an expert authored into
# docs/graph/agents/ and never projected sits on disk unspawnable, because the
# host reads its roster from the projection directory when a session starts.
rm -rf "$TMP/staff"; mkdir -p "$TMP/staff"
bash "$ROOT/install.sh" claude-code --project-dir "$TMP/staff" >/dev/null 2>&1
STAFF="$TMP/staff"
python3 - "$STAFF" <<'PY'
import pathlib, sys
p = pathlib.Path(sys.argv[1])
charter = "\n\n## Charter\n\n" + ("It owns claims adjudication in this project. " * 12) + "\n"
(p/"docs/graph/agents/claims-expert.md").write_text(
    "---\nname: claims-expert\norigin: project\nplant_knowledge:\n  - architecture/\n"
    "---\n# Claims expert" + charter)
(p/"src").mkdir(exist_ok=True)
(p/"src/Adjudicator.cs").write_text("class Adjudicator {}\n")
(p/"docs/graph/architecture/claims.md").write_text(
    "# claims\n\n" + ("The adjudication pipeline and its rule sources. " * 14))
PY
# the expert row is derived from the PLANT's own graph, so planning finds it
python3 "$AUDIT" "$STAFF" "$ROOT" --plan >/dev/null 2>&1 || true
grep -q "claims-expert" "$STAFF/.cypress/coverage.json" \
    || fail "--plan did not open an expert row for the plant's own expert"
python3 - "$STAFF" <<'PY'
import json, pathlib, sys
f = pathlib.Path(sys.argv[1])/".cypress/coverage.json"; rec = json.loads(f.read_text())
for e in rec["experts"]:
    e.update(status="COVERED", motivated_by=["src/Adjudicator.cs:1"])
rec["inventory"] = [{"kind": "domain", "name": "claims adjudication",
                     "status": "COVERED", "evidence": ["src/Adjudicator.cs:1"],
                     "expect": [{"path": "architecture/claims.md", "why": "domain"}],
                     "grounding": {"required": False, "sources": []},
                     "expert": {"warranted": True, "name": "claims-expert",
                                "why": "every rule change touches three layers"}}]
f.write_text(json.dumps(rec, indent=2) + "\n")
PY
out15="$(python3 "$AUDIT" "$STAFF" "$ROOT" --agents 2>&1)" || true
grep -q "UNGROWN      expert claims-expert" <<<"$out15" \
    || fail "an expert that reached the graph but no harness passed the gate"
grep -q ".claude/agents/claims-expert.md" <<<"$out15" \
    || fail "the audit did not name the projection the expert is missing"
grep -q "no claude-code session can spawn it" <<<"$out15" \
    || fail "the audit did not say why an unprojected expert is not a specialist"

# --- 16. a projection is a copy, not a second home ------------------------
cp "$STAFF/docs/graph/agents/claims-expert.md" "$STAFF/.claude/agents/claims-expert.md"
out16a="$(python3 "$AUDIT" "$STAFF" "$ROOT" --agents 2>&1)" || true
! grep -q "expert claims-expert" <<<"$out16a" \
    || { printf '%s\n' "$out16a" >&2; fail "a projected expert still drew a finding"; }
printf 'edited only in the projection\n' >> "$STAFF/.claude/agents/claims-expert.md"
out16="$(python3 "$AUDIT" "$STAFF" "$ROOT" --agents 2>&1)" || true
grep -q "CONTRADICTED expert claims-expert" <<<"$out16" \
    || fail "a projection edited away from its graph home was accepted"
cp "$STAFF/docs/graph/agents/claims-expert.md" "$STAFF/.claude/agents/claims-expert.md"

# --- 17. an expert the plant does not carry is staffing on paper ----------
python3 - "$STAFF" <<'PY'
import json, pathlib, sys
f = pathlib.Path(sys.argv[1])/".cypress/coverage.json"; rec = json.loads(f.read_text())
rec["inventory"][0]["expert"]["name"] = "fraud-expert"
rec["experts"].append({"name": "fraud-expert", "status": "COVERED",
                       "motivated_by": ["src/Adjudicator.cs:1"], "evidence": [],
                       "reason": "", "searched": [], "blocker": ""})
f.write_text(json.dumps(rec, indent=2) + "\n")
PY
out17="$(python3 "$AUDIT" "$STAFF" "$ROOT" --agents 2>&1)" || true
grep -q "UNSTAFFED    expert fraud-expert" <<<"$out17" \
    || fail "an item staffed with an expert the plant does not carry passed"
grep -q "staffed on paper only" <<<"$out17" \
    || fail "the paper-staffing finding did not say what was wrong"

# --- 18. the expert's own frontmatter is what makes it a node -------------
# No `origin: project` and a graft cannot tell the plant's work from the seed's;
# no `plant_knowledge:` and the one agent authored FOR this project's surface is
# the only one exempt from the check that asks if it has anything to read.
python3 - "$STAFF" <<'PY'
import json, pathlib, sys
p = pathlib.Path(sys.argv[1])
a = p/"docs/graph/agents/claims-expert.md"
a.write_text(a.read_text().replace("origin: project\n", "")
                          .replace("plant_knowledge:\n  - architecture/\n", ""))
(p/".claude/agents/claims-expert.md").write_text(a.read_text())
f = p/".cypress/coverage.json"; rec = json.loads(f.read_text())
rec["inventory"][0]["expert"]["name"] = "claims-expert"
rec["experts"] = [e for e in rec["experts"] if e["name"] == "claims-expert"]
for e in rec["experts"]:
    e["motivated_by"] = []
f.write_text(json.dumps(rec, indent=2) + "\n")
PY
out18="$(python3 "$AUDIT" "$STAFF" "$ROOT" --agents 2>&1)" || true
grep -q "no \`origin: project\`" <<<"$out18" \
    || fail "an expert indistinguishable from seed machinery was accepted"
grep -q "declares no \`plant_knowledge:\`" <<<"$out18" \
    || fail "an expert that declares nothing to read was accepted"
grep -q "UNJUSTIFIED  expert claims-expert" <<<"$out18" \
    || fail "an expert citing nothing that motivated it was accepted"

# --- 19. declining to staff is a complete answer, silence is not ----------
# A roster padded with experts nobody needed is its own failure, so the gate
# must go green on an honest `warranted: false` — and only when it carries why.
rm -rf "$TMP/nostaff"; mkdir -p "$TMP/nostaff"
bash "$ROOT/install.sh" claude-code --project-dir "$TMP/nostaff" >/dev/null 2>&1
python3 "$AUDIT" "$TMP/nostaff" "$ROOT" --plan >/dev/null 2>&1 || true
python3 - "$TMP/nostaff" <<'PY'
import json, pathlib, sys
p = pathlib.Path(sys.argv[1]); f = p/".cypress/coverage.json"
rec = json.loads(f.read_text())
for c in rec["collections"]:
    c.update(status="ABSENT", reason="the source shows no such evidence",
             searched=["src/"], evidence=[], leaves=0)
for a in rec["agents"]:
    a.update(status="ABSENT", reason="its collections are absent-with-reason",
             searched=["src/"])
(p/"src").mkdir(exist_ok=True); (p/"src/main.py").write_text("print(1)\n")
rec["inventory"] = [{"kind": "domain", "name": "batch etl", "status": "COVERED",
                     "evidence": ["src/main.py:1"], "expect": [],
                     "grounding": {"required": False, "sources": []},
                     "expert": {"warranted": False}}]
f.write_text(json.dumps(rec, indent=2) + "\n")
PY
out19="$(python3 "$AUDIT" "$TMP/nostaff" "$ROOT" 2>&1)" || true
grep -q "UNSTAFFED    domain batch etl" <<<"$out19" \
    || fail "\`warranted: false\` with no reason was accepted as a decision"
grep -q "is a decision, and a decision carries" <<<"$out19" \
    || fail "the unreasoned decline did not say what was missing"
python3 - "$TMP/nostaff" <<'PY'
import json, pathlib, sys
f = pathlib.Path(sys.argv[1])/".cypress/coverage.json"; rec = json.loads(f.read_text())
rec["inventory"][0]["expert"]["why"] = "ordinary etl; the base roster covers it"
rec["inventory"][0]["expect"] = [{"path": "architecture/etl.md", "why": "domain"}]
f.write_text(json.dumps(rec, indent=2) + "\n")
PY
python3 - "$TMP/nostaff" <<'PY'
import pathlib, sys
p = pathlib.Path(sys.argv[1])/"docs/graph/architecture/etl.md"
p.write_text("# etl\n\n" + ("The batch pipeline and where its stages live. " * 14))
PY
python3 "$ROOT/tools/graft-audit.py" "$TMP/nostaff" "$ROOT" --unfilled --rename >/dev/null 2>&1 || true
python3 - "$TMP/nostaff" <<'PY'
import json, pathlib, sys
f = pathlib.Path(sys.argv[1])/".cypress/coverage.json"; rec = json.loads(f.read_text())
for c in rec["collections"]:
    if c["name"] == "architecture/":
        c.update(status="COVERED", evidence=["docs/graph/architecture/etl.md"],
                 reason="", searched=[], leaves=1)
f.write_text(json.dumps(rec, indent=2) + "\n")
PY
[[ "$(audit_at "$TMP/nostaff")" == 0 ]] || {
    python3 "$AUDIT" "$TMP/nostaff" "$ROOT" >&2
    fail "a plant that honestly declined to staff its domain could not pass"
}

# --- 20. the arm runs in the gate grow and graft actually invoke -----------
# Cases 15-18 all pass --agents. Grow Phase 6 and graft Phase 7 run the DEFAULT
# mode, so the expert arm could have been dead on the only path a real plant
# takes and every test above would still have passed. This case runs the gate
# the way the protocols run it, and it also pins the headline defect: an item
# with no `expert` object AT ALL, which is the state every pre-7.4 plant is in.
rm -rf "$TMP/dflt"; mkdir -p "$TMP/dflt"
bash "$ROOT/install.sh" claude-code --project-dir "$TMP/dflt" >/dev/null 2>&1
python3 - "$TMP/dflt" <<'PY'
import pathlib, sys
p = pathlib.Path(sys.argv[1])
charter = "\n\n## Charter\n\n" + ("It owns claims adjudication in this project. " * 12) + "\n"
(p/"docs/graph/agents/claims-expert.md").write_text(
    "---\nname: claims-expert\norigin: project\nplant_knowledge:\n  - architecture/\n"
    "---\n# Claims expert" + charter)
(p/"src").mkdir(exist_ok=True); (p/"src/A.cs").write_text("class A {}\n")
(p/"docs/graph/architecture/claims.md").write_text(
    "# claims\n\n" + ("The adjudication pipeline and where its stages live. " * 14))
PY
python3 "$AUDIT" "$TMP/dflt" "$ROOT" --plan >/dev/null 2>&1 || true
python3 - "$TMP/dflt" <<'PY'
import json, pathlib, sys
f = pathlib.Path(sys.argv[1])/".cypress/coverage.json"; r = json.loads(f.read_text())
for e in r["experts"]:
    e.update(status="COVERED", motivated_by=["src/A.cs:1"])
r["inventory"] = [
    # no `expert` key at all: a core item that never answered the question
    {"kind": "runtime", "name": "dotnet", "significance": "core",
     "status": "COVERED", "evidence": ["src/A.cs:1"],
     "expect": [{"path": "architecture/claims.md"}],
     "grounding": {"required": False, "sources": []}},
]
f.write_text(json.dumps(r, indent=2) + "\n")
PY
out20="$(python3 "$AUDIT" "$TMP/dflt" "$ROOT" 2>&1)" || true
grep -q "UNGROWN      expert claims-expert" <<<"$out20" \
    || fail "the expert arm does not run in the DEFAULT mode grow and graft use"
grep -q "UNSTAFFED    runtime dotnet" <<<"$out20" \
    || fail "a core item with no staffing decision at all passed"
grep -q "records no staffing decision" <<<"$out20" \
    || fail "the unasked staffing question was not named as such"

# --- 21. a form is not an expert ------------------------------------------
# A filled-in copy of agent.template.md once passed as a real expert: the
# scaffold comparison only indexed templates/docs/**, so the template's own
# instructional prose counted as this plant's authored content. Rubbing the
# {{ }} braces off was enough to make every line look written.
python3 - "$TMP/dflt" "$ROOT" <<'PY'
import pathlib, re, sys
p, seed = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
t = (seed/"templates/agent.template.md").read_text().split("-->\n", 1)[1]
t = re.sub(r"\{\{|\}\}", "", t)
(p/"docs/graph/agents/form-expert.md").write_text(t)
(p/".claude/agents/form-expert.md").write_text(t)
PY
python3 "$AUDIT" "$TMP/dflt" "$ROOT" --plan >/dev/null 2>&1 || true
python3 - "$TMP/dflt" <<'PY'
import json, pathlib, sys
f = pathlib.Path(sys.argv[1])/".cypress/coverage.json"; r = json.loads(f.read_text())
for e in r["experts"]:
    e.update(status="COVERED", motivated_by=["src/A.cs:1"])
f.write_text(json.dumps(r, indent=2) + "\n")
PY
out21="$(python3 "$AUDIT" "$TMP/dflt" "$ROOT" --agents 2>&1)" || true
grep -q "HOLLOW       expert form-expert" <<<"$out21" \
    || fail "a filled-in copy of the agent template passed as an expert"
grep -q "inherited from its seed template" <<<"$out21" \
    || fail "the template copy was not named as inherited content"
rm -f "$TMP/dflt/docs/graph/agents/form-expert.md" "$TMP/dflt/.claude/agents/form-expert.md"

# --- 22. seed-ness is derived, never self-declared -------------------------
# The plant's own expert is whatever the SEED did not put in docs/graph/agents/.
# Reading the file's own `origin:` inverted the check it was paired with: an
# expert copied from a seed agent keeps `origin: seed`, and the one wrong value
# the `origin: project` finding exists to catch was the value that hid the file.
python3 - "$TMP/dflt" <<'PY'
import pathlib, sys
p = pathlib.Path(sys.argv[1])
body = "\n\n## Charter\n\n" + ("It owns fraud scoring in this project. " * 14) + "\n"
(p/"docs/graph/agents/fraud-expert.md").write_text(
    "---\nname: fraud-expert\norigin: seed\nplant_knowledge:\n  - architecture/\n"
    "---\n# Fraud" + body)
PY
out22="$(python3 "$AUDIT" "$TMP/dflt" "$ROOT" --agents 2>&1)" || true
grep -q "expert fraud-expert" <<<"$out22" \
    || fail "an expert declaring origin: seed made itself invisible to the gate"
rm -f "$TMP/dflt/docs/graph/agents/fraud-expert.md"

# --- 23. the filename is what the harness spawns --------------------------
python3 - "$TMP/dflt" <<'PY'
import pathlib, sys
p = pathlib.Path(sys.argv[1])
a = p/"docs/graph/agents/claims-expert.md"
a.write_text(a.read_text().replace("name: claims-expert", "name: claims-adjudicator"))
(p/".claude/agents/claims-expert.md").write_text(a.read_text())
PY
out23="$(python3 "$AUDIT" "$TMP/dflt" "$ROOT" --agents 2>&1)" || true
grep -q "spawns by filename" <<<"$out23" \
    || fail "a frontmatter name disagreeing with the filename was accepted"

# --- 24. a plant whose stamp cannot say where a roster is spawnable from ---
# The projection paths live in the stamp install.sh writes. A stamp that
# records none must not pass every registration check by default.
python3 - "$TMP/dflt" <<'PY'
import json, pathlib, sys
f = pathlib.Path(sys.argv[1])/".cypress/seed.json"
d = json.loads(f.read_text()); d.pop("agent_projections", None)
f.write_text(json.dumps(d, indent=2) + "\n")
PY
out24="$(python3 "$AUDIT" "$TMP/dflt" "$ROOT" --agents 2>&1)" || true
grep -q "STALE        .cypress/seed.json" <<<"$out24" \
    || fail "a stamp recording no projection paths silently passed every expert"

# --- 25. the rest of the expert row's promises ----------------------------
rm -rf "$TMP/rows"; mkdir -p "$TMP/rows"
bash "$ROOT/install.sh" claude-code --project-dir "$TMP/rows" >/dev/null 2>&1
python3 - "$TMP/rows" <<'PY'
import pathlib, sys
p = pathlib.Path(sys.argv[1])
body = "\n\n## Charter\n\n" + ("It owns settlement netting in this project. " * 14) + "\n"
(p/"docs/graph/agents/netting-expert.md").write_text(
    "---\nname: netting-expert\norigin: project\nplant_knowledge:\n  - design/\n"
    "---\n# Netting" + body)
(p/".claude/agents/netting-expert.md").write_text(
    (p/"docs/graph/agents/netting-expert.md").read_text())
PY
# no expert row at all -> MISSING, derived from the plant's own graph
python3 "$AUDIT" "$TMP/rows" "$ROOT" --plan >/dev/null 2>&1 || true
python3 - "$TMP/rows" <<'PY'
import json, pathlib, sys
f = pathlib.Path(sys.argv[1])/".cypress/coverage.json"; r = json.loads(f.read_text())
r["experts"] = []
f.write_text(json.dumps(r, indent=2) + "\n")
PY
out25="$(python3 "$AUDIT" "$TMP/rows" "$ROOT" --agents 2>&1)" || true
grep -q "MISSING      expert netting-expert" <<<"$out25" \
    || fail "an expert the plant carries with no row in the record passed"
python3 - "$TMP/rows" <<'PY'
import json, pathlib, sys
f = pathlib.Path(sys.argv[1])/".cypress/coverage.json"; r = json.loads(f.read_text())
r["experts"] = [{"name": "netting-expert", "status": "ABSENT",
                 "reason": "not needed", "searched": ["src/"],
                 "motivated_by": [], "evidence": []}]
f.write_text(json.dumps(r, indent=2) + "\n")
PY
out25b="$(python3 "$AUDIT" "$TMP/rows" "$ROOT" --agents 2>&1)" || true
grep -q "CONTRADICTED expert netting-expert" <<<"$out25b" \
    || fail "an expert claimed ABSENT while its file exists was accepted"
python3 - "$TMP/rows" <<'PY'
import json, pathlib, sys
f = pathlib.Path(sys.argv[1])/".cypress/coverage.json"; r = json.loads(f.read_text())
r["experts"] = [{"name": "netting-expert", "status": "COVERED",
                 "motivated_by": ["src/nowhere.cs:1"], "evidence": [],
                 "reason": "", "searched": [], "blocker": ""}]
f.write_text(json.dumps(r, indent=2) + "\n")
PY
out25c="$(python3 "$AUDIT" "$TMP/rows" "$ROOT" --agents 2>&1)" || true
grep -q "DANGLING     expert netting-expert" <<<"$out25c" \
    || fail "an expert motivated by a path that does not exist was accepted"
# a roster cannot be its own evidence
python3 - "$TMP/rows" <<'PY'
import json, pathlib, sys
f = pathlib.Path(sys.argv[1])/".cypress/coverage.json"; r = json.loads(f.read_text())
r["experts"][0]["motivated_by"] = ["docs/graph/agents/netting-expert.md"]
f.write_text(json.dumps(r, indent=2) + "\n")
PY
out25d="$(python3 "$AUDIT" "$TMP/rows" "$ROOT" --agents 2>&1)" || true
grep -q "cannot be its own evidence" <<<"$out25d" \
    || fail "an expert citing its own agent file as what motivated it passed"
grep -q "design/ holds nothing this plant wrote" <<<"$out25c" \
    || fail "an expert declaring a collection with nothing in it was accepted"

# --- 26. a staffing decision is a boolean, not a remark -------------------
python3 - "$TMP/rows" <<'PY'
import json, pathlib, sys
p = pathlib.Path(sys.argv[1]); f = p/".cypress/coverage.json"
r = json.loads(f.read_text())
(p/"src").mkdir(exist_ok=True); (p/"src/N.cs").write_text("class N {}\n")
r["inventory"] = [{"kind": "domain", "name": "netting", "status": "COVERED",
                   "evidence": ["src/N.cs:1"], "expect": [{"path": "design/x.md"}],
                   "grounding": {"required": False, "sources": []},
                   "expert": {"warranted": "no", "why": "looks fine"}}]
f.write_text(json.dumps(r, indent=2) + "\n")
PY
out26="$(python3 "$AUDIT" "$TMP/rows" "$ROOT" 2>&1)" || true
grep -q "not true or false" <<<"$out26" \
    || fail "a staffing decision of \"no\" was read as a decision"
python3 - "$TMP/rows" <<'PY'
import json, pathlib, sys
f = pathlib.Path(sys.argv[1])/".cypress/coverage.json"; r = json.loads(f.read_text())
r["inventory"][0]["expert"] = {"warranted": True, "name": "netting-expert"}
f.write_text(json.dumps(r, indent=2) + "\n")
PY
out26b="$(python3 "$AUDIT" "$TMP/rows" "$ROOT" 2>&1)" || true
grep -q "gives no reason" <<<"$out26b" \
    || fail "an expert warranted with no reason was accepted"
python3 - "$TMP/rows" <<'PY'
import json, pathlib, sys
f = pathlib.Path(sys.argv[1])/".cypress/coverage.json"; r = json.loads(f.read_text())
r["inventory"][0]["expert"] = {"warranted": True, "why": "a recurring shape"}
f.write_text(json.dumps(r, indent=2) + "\n")
PY
out26c="$(python3 "$AUDIT" "$TMP/rows" "$ROOT" 2>&1)" || true
grep -q "warrants a project-specific expert and names none" <<<"$out26c" \
    || fail "a surface warranted an expert, named none, and passed"

# --- 27. an untouched copy of a seed agent is a form, not an expert -------
rm -rf "$TMP/copy"; mkdir -p "$TMP/copy"
bash "$ROOT/install.sh" claude-code --project-dir "$TMP/copy" >/dev/null 2>&1
cp "$ROOT/agents/05-security.md" "$TMP/copy/docs/graph/agents/payments-expert.md"
cp "$ROOT/agents/05-security.md" "$TMP/copy/.claude/agents/payments-expert.md"
python3 "$AUDIT" "$TMP/copy" "$ROOT" --plan >/dev/null 2>&1 || true
python3 - "$TMP/copy" <<'PY'
import json, pathlib, sys
f = pathlib.Path(sys.argv[1])/".cypress/coverage.json"; r = json.loads(f.read_text())
for e in r["experts"]:
    e.update(status="COVERED", motivated_by=["docs/graph/index.md"])
f.write_text(json.dumps(r, indent=2) + "\n")
PY
out27="$(python3 "$AUDIT" "$TMP/copy" "$ROOT" --agents 2>&1)" || true
grep -q "byte-identical to " <<<"$out27" \
    || fail "a seed agent copied under a new name passed as a project expert"

# ==========================================================================
# 7.5.0 — expertise composes through the graph.
#
# A core or significant stack element owes an `expertise.*` node: the Tier-2
# handle that says when it is in play and routes to its pin page and its
# standards page without restating either. These cases pin the derivation
# (who owes one, who does not), the substance (a form is not a node, and a
# node routing to no pin home is not one either), the two-majors shape, and
# the staffing default the node changes.
# ==========================================================================

# a planned plant carrying one dotnet item. $1 = dir, $2 = significance,
# $3 = kind (default runtime). Leaves the --plan output in $TMP/plan-out.
expertise_plant() {
    local d="$1" sig="$2" kind="${3:-runtime}"
    rm -rf "$d"; mkdir -p "$d"
    bash "$ROOT/install.sh" claude-code --project-dir "$d" >/dev/null 2>&1
    python3 "$AUDIT" "$d" "$ROOT" --plan >/dev/null 2>&1 || true
    printf '<Project/>\n' > "$d/app.csproj"
    python3 - "$d" "$sig" "$kind" <<'PY'
import json, pathlib, sys
f = pathlib.Path(sys.argv[1])/".cypress/coverage.json"; r = json.loads(f.read_text())
r["inventory"] = [{"kind": sys.argv[3], "name": "dotnet", "version": "9.0",
                   "significance": sys.argv[2], "evidence": ["app.csproj:1"]}]
f.write_text(json.dumps(r, indent=2) + "\n")
PY
    python3 "$AUDIT" "$d" "$ROOT" --plan >"$TMP/plan-out" 2>&1 || true
}

# --- 28. a core stack element owes an expertise node ----------------------
# Derived from the inventory like every other planned artifact, so a plant
# cannot arrive without one by nobody having decided.
expertise_plant "$TMP/x28" core
planned_paths() {   # the paths --plan wrote into the record for its inventory
    python3 - "$1" <<'PY'
import json, pathlib, sys
r = json.loads((pathlib.Path(sys.argv[1])/".cypress/coverage.json").read_text())
print("\n".join(e["path"] for i in r["inventory"] for e in i.get("expect", [])))
PY
}
planned_paths "$TMP/x28" | grep -q "nodes/expertise.dotnet.md" \
    || fail "--plan did not derive an expertise node for a core runtime"
out28="$(python3 "$AUDIT" "$TMP/x28" "$ROOT" 2>&1)" || true
grep -q "UNGROWN" <<<"$out28" || fail "an unwritten expertise node did not fail the gate"
grep -q "nodes/expertise.dotnet.md — does not exist" <<<"$out28" \
    || fail "the missing expertise node was not named"

# --- 29. a significant dependency owes one too ----------------------------
expertise_plant "$TMP/x29" significant dependency
planned_paths "$TMP/x29" | grep -q "nodes/expertise.dotnet.md" \
    || fail "a significant dependency was not planned an expertise node"

# --- 30. an incidental item owes none, and keeps everything else ----------
# The valve. An incidental DEPENDENCY still earns only its index line and no
# grounding (the pre-7.5.0 rule, unchanged); an incidental item of any other
# kind still keeps its kind's pages AND its grounding. Neither owes a node:
# the graph gains a routing handle for the stack a worker writes against, not
# for every name in the lockfile.
expertise_plant "$TMP/x30" incidental dependency
planned_paths "$TMP/x30" | grep -q "libraries/index.md" \
    || fail "an incidental dependency lost its index line"
! planned_paths "$TMP/x30" | grep -q "expertise" \
    || fail "an incidental dependency was planned an expertise node"
expertise_plant "$TMP/x30b" incidental
python3 - "$TMP/x30b" <<'PY' || exit 1
import json, pathlib, sys
r = json.loads((pathlib.Path(sys.argv[1])/".cypress/coverage.json").read_text())
it = r["inventory"][0]
paths = [e["path"] for e in it["expect"]]
assert paths == ["libraries/dotnet.md", "best-practices/dotnet.md"], paths
assert it["grounding"]["required"] is True, "incidental non-dependency lost grounding"
assert not any("expertise" in p for p in paths), paths
PY

# --- 31. a filled-in form is not an expertise node ------------------------
# The node's form is nodes/_expertise.template.md — a leading underscore, so
# the same-path lookup that measures every other leaf never finds it. Without
# the resolver the form's own prose counts as this plant's content, and a
# scaffold with the braces rubbed off reads as knowledge.
expertise_plant "$TMP/x31" core
python3 - "$TMP/x31" "$ROOT" <<'PY'
import pathlib, re, sys
seed = pathlib.Path(sys.argv[2])/"templates/docs/nodes/_expertise.template.md"
out = pathlib.Path(sys.argv[1])/"docs/graph/nodes/expertise.dotnet.md"
text = re.sub(r"\{\{([^}]*)\}\}", lambda m: m.group(1).split(",")[0][:24],
              seed.read_text(), flags=re.S)
out.write_text(text)
PY
out31="$(python3 "$AUDIT" "$TMP/x31" "$ROOT" 2>&1)" || true
grep -q "nodes/expertise.dotnet.md — holds .* bytes this plant wrote" <<<"$out31" \
    || fail "a brace-stripped copy of the expertise form passed as a node"
grep -q "inherited from its seed template" <<<"$out31" \
    || fail "the expertise form's own prose was not named as inherited content"

# --- 32. a node that routes to no pin home is not a node ------------------
# It owns applicability, never the version. Without its own library page
# named, the version distinction has nowhere to live and the node is the
# second home it was designed not to be.
expertise_plant "$TMP/x32" core
python3 - "$TMP/x32" <<'PY'
import pathlib, sys
body = "A project-specific applicability fact with its source path. " * 12
(pathlib.Path(sys.argv[1])/"docs/graph/nodes/expertise.dotnet.md").write_text(
    "---\nid: expertise.dotnet\ntier: 2\nkind: expertise\norigin: project\n"
    "title: dotnet applicability\nowns:\n  - dotnet.applicability\n"
    "  - dotnet.composition\nrequires:\nartifacts:\n"
    "  - best-practices/dotnet.md\nload_when:\n  - dotnet, csharp\n"
    "est_tokens: 120\n---\n\n" + body + "\n")
PY
out32="$(python3 "$AUDIT" "$TMP/x32" "$ROOT" 2>&1)" || true
grep -q "names no .libraries: dotnet." <<<"$out32" \
    || fail "an expertise node routing to no pin home passed"

# --- 33. two majors at once compose one child per major -------------------
# The single place a version enters a node id, and derived from the inventory
# rather than decided: applicability really does differ by major.
rm -rf "$TMP/x33"; mkdir -p "$TMP/x33"
bash "$ROOT/install.sh" claude-code --project-dir "$TMP/x33" >/dev/null 2>&1
python3 "$AUDIT" "$TMP/x33" "$ROOT" --plan >/dev/null 2>&1 || true
printf '<Project/>\n' > "$TMP/x33/app.csproj"
python3 - "$TMP/x33" <<'PY'
import json, pathlib, sys
f = pathlib.Path(sys.argv[1])/".cypress/coverage.json"; r = json.loads(f.read_text())
r["inventory"] = [
    {"kind": "runtime", "name": "dotnet", "slug": "dotnet", "version": "8.0",
     "significance": "core", "evidence": ["app.csproj:1"]},
    {"kind": "runtime", "name": "dotnet", "slug": "dotnet", "version": "10.0",
     "significance": "core", "evidence": ["app.csproj:1"]},
]
f.write_text(json.dumps(r, indent=2) + "\n")
PY
out33="$(python3 "$AUDIT" "$TMP/x33" "$ROOT" --plan 2>&1)" || true
# ordered as numbers: as strings 10 sorts before 8, and the message then
# reads as though the older major were the newer one
grep -q "NEEDS COMPOSITION dotnet runs majors 8, 10" <<<"$out33" \
    || fail "two majors of one stack did not ask for a child per major, in order"
python3 - "$TMP/x33" <<'PY' || exit 1
import json, pathlib, sys
r = json.loads((pathlib.Path(sys.argv[1])/".cypress/coverage.json").read_text())
paths = [e["path"] for e in r["inventory"][0]["expect"]]
for want in ("nodes/expertise.dotnet.md", "nodes/expertise.dotnet-8.md",
             "nodes/expertise.dotnet-10.md"):
    assert want in paths, (want, paths)
PY

# --- 34. a plant that owes no expertise still goes green ------------------
# A gate that cannot go green on an honest plant is worse than none. Coverage
# is derived per inventory item, so a plant with nothing to be expert about
# carries no expertise obligation at all — there is no absence to establish.
rm -rf "$TMP/x34"; mkdir -p "$TMP/x34"
bash "$ROOT/install.sh" claude-code --project-dir "$TMP/x34" >/dev/null 2>&1
python3 "$AUDIT" "$TMP/x34" "$ROOT" --plan >/dev/null 2>&1 || true
python3 - "$TMP/x34" <<'PY'
import json, pathlib, sys
f = pathlib.Path(sys.argv[1])/".cypress/coverage.json"; r = json.loads(f.read_text())
for c in r["collections"]:
    c.update(status="ABSENT", reason="the source shows no such evidence",
             searched=["src/"], evidence=[], leaves=0)
for a in r["agents"]:
    a.update(status="ABSENT", reason="its collections are absent-with-reason",
             searched=["src/"])
r["inventory"] = [{"kind": "dependency", "name": "left-pad", "version": "1.0",
                   "significance": "incidental", "status": "COVERED",
                   "evidence": ["docs/graph/index.md"]}]
f.write_text(json.dumps(r, indent=2) + "\n")
PY
python3 "$AUDIT" "$TMP/x34" "$ROOT" --plan >/dev/null 2>&1 || true
python3 "$ROOT/tools/graft-audit.py" "$TMP/x34" "$ROOT" --unfilled --rename >/dev/null 2>&1 || true
# the one artifact an incidental dependency owes: its row in the index
python3 - "$TMP/x34" <<'PY'
import json, pathlib, sys
p = pathlib.Path(sys.argv[1]); g = p/"docs/graph"
(g/"libraries").mkdir(parents=True, exist_ok=True)
(g/"libraries/index.md").write_text(
    "# Libraries index\n\n| Library | Version | Page | Used by |\n|---|---|---|---|\n"
    + ("| left-pad | 1.0 | index line only, incidental | src/app.js |\n" * 8))
f = p/".cypress/coverage.json"; r = json.loads(f.read_text())
for c in r["collections"]:
    if c["name"] == "libraries/":
        c.update(status="COVERED", evidence=["docs/graph/libraries/index.md"],
                 leaves=1, reason="", searched=[], blocker="")
f.write_text(json.dumps(r, indent=2) + "\n")
PY
[[ "$(audit_at "$TMP/x34")" == 0 ]] || {
    python3 "$AUDIT" "$TMP/x34" "$ROOT" >&2
    fail "a plant that owes no expertise node could not go green"
}
python3 - "$TMP/x34" <<'PY' || exit 1
import json, pathlib, sys
r = json.loads((pathlib.Path(sys.argv[1])/".cypress/coverage.json").read_text())
assert not any("expertise" in e["path"] for e in r["inventory"][0]["expect"])
PY

# --- 35-37. an expert may declare the expertise it draws on ---------------
# The seam D7 leaves open: agents reach expertise through the ROUTER, so no
# seed agent declares it — but a plant-authored expert is itself a plant
# artifact, and naming the node it reads is a claim the audit can check.
rm -rf "$TMP/x35"; mkdir -p "$TMP/x35"
bash "$ROOT/install.sh" claude-code --project-dir "$TMP/x35" >/dev/null 2>&1
python3 - "$TMP/x35" <<'PY'
import pathlib, sys
p = pathlib.Path(sys.argv[1])
body = "\n\n## Charter\n\n" + ("It owns settlement netting in this project. " * 14) + "\n"
(p/"docs/graph/agents/netting-expert.md").write_text(
    "---\nname: netting-expert\norigin: project\nplant_knowledge:\n"
    "  - expertise.dotnet\n---\n# Netting" + body)
(p/".claude/agents/netting-expert.md").write_text(
    (p/"docs/graph/agents/netting-expert.md").read_text())
PY
python3 "$AUDIT" "$TMP/x35" "$ROOT" --plan >/dev/null 2>&1 || true
python3 - "$TMP/x35" <<'PY'
import json, pathlib, sys
f = pathlib.Path(sys.argv[1])/".cypress/coverage.json"; r = json.loads(f.read_text())
r["experts"] = [{"name": "netting-expert", "status": "COVERED",
                 "motivated_by": ["docs/graph/index.md"], "evidence": [],
                 "reason": "", "searched": [], "blocker": ""}]
f.write_text(json.dumps(r, indent=2) + "\n")
PY
# 36. the node it names does not exist -> DANGLING, not "an empty collection"
out36="$(python3 "$AUDIT" "$TMP/x35" "$ROOT" --agents 2>&1)" || true
grep -q "declares it reads node .expertise.dotnet." <<<"$out36" \
    || fail "an expert naming a node the plant does not carry was accepted"
grep -q "DANGLING" <<<"$out36" || fail "a missing declared node was not DANGLING"
# 37. the node exists but is still the form -> CONTRADICTED
python3 - "$TMP/x35" "$ROOT" <<'PY'
import pathlib, sys
seed = pathlib.Path(sys.argv[2])/"templates/docs/nodes/_expertise.template.md"
(pathlib.Path(sys.argv[1])/"docs/graph/nodes/expertise.dotnet.md").write_text(
    seed.read_text())
PY
out37="$(python3 "$AUDIT" "$TMP/x35" "$ROOT" --agents 2>&1)" || true
grep -q "CONTRADICTED expert netting-expert" <<<"$out37" \
    || fail "an expert reading a node that is still a form was accepted"
# 35. a real node -> the row passes
python3 - "$TMP/x35" <<'PY'
import pathlib, sys
body = "A project-specific applicability fact with its source path. " * 12
(pathlib.Path(sys.argv[1])/"docs/graph/nodes/expertise.dotnet.md").write_text(
    "---\nid: expertise.dotnet\ntier: 2\nkind: expertise\norigin: project\n"
    "title: dotnet applicability\nowns:\n  - dotnet.applicability\n"
    "  - dotnet.composition\nrequires:\nlibraries:\n  - dotnet\n"
    "load_when:\n  - dotnet, csharp\nest_tokens: 120\n---\n\n" + body + "\n")
PY
out35="$(python3 "$AUDIT" "$TMP/x35" "$ROOT" --agents 2>&1)" || true
! grep -qE "(DANGLING|CONTRADICTED) +expert netting-expert" <<<"$out35" \
    || fail "an expert reading a real expertise node was still reported"

# --- 38. an agent needs what a node cannot be -----------------------------
# The staffing default flips: every surface owes a node, so spawning ON TOP
# of one is warranted only by something a node cannot be. Naming which is
# what makes the decision reviewable instead of a preference.
expertise_plant "$TMP/x38" core
python3 - "$TMP/x38" <<'PY'
import json, pathlib, sys
f = pathlib.Path(sys.argv[1])/".cypress/coverage.json"; r = json.loads(f.read_text())
r["inventory"][0]["expert"] = {"warranted": True, "name": "dotnet-expert",
                               "why": "it is important"}
f.write_text(json.dumps(r, indent=2) + "\n")
PY
out38="$(python3 "$AUDIT" "$TMP/x38" "$ROOT" 2>&1)" || true
grep -q "UNSTAFFED" <<<"$out38" \
    || fail "an agent warranted without naming what a node cannot serve passed"
grep -q "tools, model, stance, isolation" <<<"$out38" \
    || fail "the UNSTAFFED message did not name the four spawn triggers"
python3 - "$TMP/x38" <<'PY'
import json, pathlib, sys
f = pathlib.Path(sys.argv[1])/".cypress/coverage.json"; r = json.loads(f.read_text())
r["inventory"][0]["expert"]["needs"] = "isolation"
f.write_text(json.dumps(r, indent=2) + "\n")
PY
out38b="$(python3 "$AUDIT" "$TMP/x38" "$ROOT" 2>&1)" || true
! grep -q 'needs. is' <<<"$out38b" \
    || fail "a staffing decision naming its trigger was still reported"

# --- 39. over-growth is a finding, and what is owed has one home ----------
# An expertise node planned for an item that does not owe one is a routing
# handle for something nobody writes against — the librarian would delete it.
# The judgment asks `planned_artifacts` rather than re-deriving the rule.
expertise_plant "$TMP/x39" incidental dependency
python3 - "$TMP/x39" <<'PY'
import json, pathlib, sys
f = pathlib.Path(sys.argv[1])/".cypress/coverage.json"; r = json.loads(f.read_text())
r["inventory"][0]["expect"] = [
    {"path": "libraries/index.md", "why": "incidental"},
    {"path": "nodes/expertise.dotnet.md", "why": "hand-added over-growth"}]
f.write_text(json.dumps(r, indent=2) + "\n")
PY
out39="$(python3 "$AUDIT" "$TMP/x39" "$ROOT" 2>&1)" || true
grep -q "which this item does not owe" <<<"$out39" \
    || fail "an expertise node planned for an item that owes none was accepted"

# --- 40. an expert's declared read must stand for something ---------------
# The row exists so the one agent authored FOR this project's surface is not
# the only one exempt from the check that asks whether it has anything to
# read. A mistyped collection stands for nothing, so it can be answered
# neither COVERED nor ABSENT — it is a dangling declaration, exactly like a
# node the graph does not carry.
rm -rf "$TMP/x40"; mkdir -p "$TMP/x40"
bash "$ROOT/install.sh" claude-code --project-dir "$TMP/x40" >/dev/null 2>&1
python3 - "$TMP/x40" <<'PY'
import pathlib, sys
p = pathlib.Path(sys.argv[1])
body = "\n\n## Charter\n\n" + ("It owns settlement netting in this project. " * 14) + "\n"
for name, reads in (("typo-expert", "desing/"), ("slashless-expert", "data")):
    (p/f"docs/graph/agents/{name}.md").write_text(
        f"---\nname: {name}\norigin: project\nplant_knowledge:\n"
        f"  - {reads}\n---\n# Expert" + body)
    (p/f".claude/agents/{name}.md").write_text(
        (p/f"docs/graph/agents/{name}.md").read_text())
PY
python3 "$AUDIT" "$TMP/x40" "$ROOT" --plan >/dev/null 2>&1 || true
python3 - "$TMP/x40" <<'PY'
import json, pathlib, sys
f = pathlib.Path(sys.argv[1])/".cypress/coverage.json"; r = json.loads(f.read_text())
for e in r["experts"]:
    e.update(status="COVERED", motivated_by=["docs/graph/index.md"])
f.write_text(json.dumps(r, indent=2) + "\n")
PY
out40="$(python3 "$AUDIT" "$TMP/x40" "$ROOT" --agents 2>&1)" || true
grep -q "declares it reads collection 'desing/'" <<<"$out40" \
    || fail "an expert declaring a collection that does not exist was accepted"
grep -q "declares it reads collection 'data'" <<<"$out40" \
    || fail "an expert declaring a slash-less collection name was accepted"

# --- 41. an authored absence statement is not an unfilled scaffold --------
# The gate over an ABSENT collection exists to catch the seed's own blank form
# sitting in it: a cold agent would read that form's placeholders as facts
# about this project. Classifying by PATH instead of by CONTENT answered a
# different question and made the gate unpassable — a leaf the plant genuinely
# authored, holding exactly what the completeness contract asks for (the
# absence, the paths searched, the candidate considered and excluded), was
# called an unfilled scaffold forever because the seed happens to template that
# path. Worse, the remedy the finding named judges a scaffold by byte-identity,
# so it reported zero and renamed nothing: the only escapes left were deleting
# authored content or renaming a filled leaf to `.unfilled.md`, a false record.
rm -rf "$TMP/x41"; mkdir -p "$TMP/x41"
bash "$ROOT/install.sh" claude-code --project-dir "$TMP/x41" >/dev/null 2>&1
python3 "$AUDIT" "$TMP/x41" "$ROOT" --plan >/dev/null 2>&1 || true
python3 - "$TMP/x41" <<'PY'
import json, pathlib, sys
p = pathlib.Path(sys.argv[1]); g = p/"docs/graph"
# (a) design/README.md is left exactly as the installer placed it.
# (b) legal/index.md is authored: the absence, where it was looked for, and the
#     one candidate considered and excluded.
(g/"legal/index.md").write_text(
    "# Legal\n\n## No regulatory exposure was established\n\n"
    + ("This project holds no personal data and moves no money; the absence "
       "was established by reading every entry point and every persistence "
       "call under src/. " * 6)
    + "\n\n## Considered and excluded\n\n"
    + ("A vendor terms file under vendor/ names an obligation on the vendor "
       "rather than on this project, so it earns no page here. " * 4) + "\n")
# (c) api/README.md is well past the floor and still holds a prompt to its
#     author — a steward who started and stopped.
(g/"api/README.md").write_text(
    "# API\n\n"
    + ("The surface was walked and each finding below carries the source path "
       "it came from. " * 10)
    + "\n\n{{what this collection covers}}\n")
f = p/".cypress/coverage.json"; r = json.loads(f.read_text())
for c in r["collections"]:
    c.update(status="ABSENT", reason="the source shows no such evidence",
             searched=["src/"], evidence=[], leaves=0)
for a in r["agents"]:
    a.update(status="ABSENT", reason="its collections are absent-with-reason",
             searched=["src/"])
r["inventory"] = [{"kind": "domain", "name": "batch reconciliation",
                   "status": "ABSENT", "searched": ["src/"],
                   "reason": "no artifact of its own; the architecture node owns it",
                   "evidence": ["docs/graph/index.md"], "expect": [],
                   "grounding": {"required": False, "sources": []}}]
f.write_text(json.dumps(r, indent=2) + "\n")
PY
out41="$(python3 "$AUDIT" "$TMP/x41" "$ROOT" 2>&1)" || true
# (a) the behaviour that must survive: the seed's own blank form still fails
grep -q "CONTRADICTED collection design/" <<<"$out41" \
    || { printf '%s\n' "$out41" >&2
         fail "an untouched seed scaffold in an ABSENT collection stopped failing"; }
# (b) the defect: an authored leaf is not a scaffold, whatever its path
! grep -q "collection legal/" <<<"$out41" \
    || { printf '%s\n' "$out41" >&2
         fail "an authored leaf was called an unfilled scaffold because the seed templates its path"; }
# (c) a surviving placeholder is a scaffold however many bytes surround it
grep -q "CONTRADICTED collection api/" <<<"$out41" \
    || { printf '%s\n' "$out41" >&2
         fail "a leaf still carrying a template placeholder passed as authored"; }
# a finding names a remedy that can act on the leaf it names: `--unfilled`
# judges by byte-identity, so it belongs to (a) and not to (c).
grep -A1 "CONTRADICTED collection design/" <<<"$out41" | grep -q -- "--unfilled --rename" \
    || fail "the byte-identical scaffold no longer names the remedy that acts on it"
! grep -A1 "CONTRADICTED collection api/" <<<"$out41" | grep -q -- "--unfilled --rename" \
    || fail "a finding prescribed a remedy that cannot act on the leaf it names"
# and the whole point: authoring the absence is a way OUT of the gate. Dispose
# of the two leaves that really are scaffolds and the plant goes green with the
# authored one still in place.
python3 "$ROOT/tools/graft-audit.py" "$TMP/x41" "$ROOT" --unfilled --rename >/dev/null 2>&1 || true
rm -f "$TMP/x41/docs/graph/api/README.md"
[[ "$(audit_at "$TMP/x41")" == 0 ]] || {
    python3 "$AUDIT" "$TMP/x41" "$ROOT" >&2
    fail "a plant that authored its absence statement could not pass the gate"
}
[[ -f "$TMP/x41/docs/graph/legal/index.md" ]] \
    || fail "the authored leaf had to be destroyed for the plant to pass"

# --- 42. the index line an incidental item owes has to be in the index -----
# A real plant shipped `tsx` COVERED with `expect: libraries/index.md` and no
# tsx row in it — the one false COVERED in its inventory, and the audit passed
# it because the index as a whole was substantive. The line is the artifact.
expertise_plant "$TMP/x42" incidental dependency
out42="$(python3 "$AUDIT" "$TMP/x42" "$ROOT" 2>&1)" || true
grep -q "UNGROWN      dependency dotnet" <<<"$out42" \
    || fail "an incidental item with no index row passed"
grep -q "libraries/index.md has no row naming 'dotnet'" <<<"$out42" \
    || fail "the missing index row was not named"
printf '| dotnet | 9.0 | — | build | healthy | MIT | 2026-09-10 |\n' \
    >> "$TMP/x42/docs/graph/libraries/index.md"
out42="$(python3 "$AUDIT" "$TMP/x42" "$ROOT" 2>&1)" || true
! grep -q "UNGROWN      dependency dotnet" <<<"$out42" \
    || fail "an incidental item with its index row was still reported UNGROWN"
# Whole-cell, never substring: a row for a longer sibling is not this item's.
expertise_plant "$TMP/x42b" incidental dependency
printf '| dotnet-tools | 1.0 | — | | | | |\n' >> "$TMP/x42b/docs/graph/libraries/index.md"
out42b="$(python3 "$AUDIT" "$TMP/x42b" "$ROOT" 2>&1)" || true
grep -q "UNGROWN      dependency dotnet" <<<"$out42b" \
    || fail "a row for a longer sibling name passed as the incidental item's own"

# --- 43. a normalized source keeps its raw snapshot, or says why not -------
# grow.md owes three things per retrieved source — raw snapshot, normalized
# copy, index row — and the skill's "when the license permits" was the only
# out. An out nobody has to record is one every scout takes: a real plant
# cited 23 library pages to one retrieval date with not one artifact behind
# it, and the next graft audited a pass it could not re-inspect.
rm -rf "$TMP/x43"; mkdir -p "$TMP/x43"
bash "$ROOT/install.sh" claude-code --project-dir "$TMP/x43" >/dev/null 2>&1
python3 "$AUDIT" "$TMP/x43" "$ROOT" --plan >/dev/null 2>&1 || true
python3 - "$TMP/x43" <<'PY'
import json, pathlib, sys
plant = pathlib.Path(sys.argv[1]); g = plant/"docs/graph"
(g/"sources/normalized/react.md").write_text(
    "# react docs\n\n## Fact\n\n" + ("A retrieved upstream fact with its URL. " * 14) + "\n")
p = plant/".cypress/coverage.json"; r = json.loads(p.read_text())
for c in r["collections"]:
    if c["name"] == "sources/":
        c.update(status="COVERED", leaves=1,
                 evidence=["docs/graph/sources/normalized/react.md"])
p.write_text(json.dumps(r, indent=2) + "\n")
PY
out43="$(python3 "$AUDIT" "$TMP/x43" "$ROOT" 2>&1)" || true
grep -q "UNJUSTIFIED  collection sources/" <<<"$out43" \
    || fail "a normalized source with no raw snapshot and no reason passed"
grep -q "normalized/react.md retains no raw snapshot" <<<"$out43" \
    || fail "the snapshot without provenance was not named"
# A recorded reason is provenance.
python3 - "$TMP/x43" <<'PY'
import pathlib, sys
f = pathlib.Path(sys.argv[1])/"docs/graph/sources/normalized/react.md"
f.write_text("---\nraw: withheld — react.dev terms forbid redistribution; "
             "URL and date are in the index row\n---\n" + f.read_text())
PY
out43="$(python3 "$AUDIT" "$TMP/x43" "$ROOT" 2>&1)" || true
! grep -q "normalized/react.md retains no raw snapshot" <<<"$out43" \
    || fail "a normalized source that recorded why no raw was kept was still reported"
# A `raw:` naming a file that is not there is not provenance either.
sed -i '2s#.*#raw: raw/react-2026-09-10.html#' "$TMP/x43/docs/graph/sources/normalized/react.md"
out43="$(python3 "$AUDIT" "$TMP/x43" "$ROOT" 2>&1)" || true
grep -q 'raw: raw/react-2026-09-10.html`, which does not exist' <<<"$out43" \
    || fail "a raw: line naming a missing snapshot passed"
# The snapshot itself, on disk, is the whole answer.
printf '<html>react</html>\n' > "$TMP/x43/docs/graph/sources/raw/react-2026-09-10.html"
out43="$(python3 "$AUDIT" "$TMP/x43" "$ROOT" 2>&1)" || true
! grep -q "collection sources/" <<<"$out43" \
    || fail "a normalized source with its raw sibling on disk was still reported"

# --- 44. an absence that found something is a redirect, not an absence -----
# A real plant marked ui-ux-designer ABSENT with the design material's real
# paths under product/ in `searched`, then left the agent node pointing at the
# empty design/. The router sent design work there at high confidence; a cold
# session spawned it, read a template, and improvised where it was told not to.
rm -rf "$TMP/x44"; mkdir -p "$TMP/x44"
bash "$ROOT/install.sh" claude-code --project-dir "$TMP/x44" >/dev/null 2>&1
python3 "$AUDIT" "$TMP/x44" "$ROOT" --plan >/dev/null 2>&1 || true
python3 - "$TMP/x44" <<'PY'
import json, pathlib, sys
plant = pathlib.Path(sys.argv[1]); g = plant/"docs/graph"
(g/"product").mkdir(parents=True, exist_ok=True)
(g/"product/design-system.md").write_text(
    "# design system\n\n## Tokens\n\n" + ("A token and its value, with the screen it serves. " * 14) + "\n")
p = plant/".cypress/coverage.json"; r = json.loads(p.read_text())
for a in r["agents"]:
    if a["name"] == "ui-ux-designer":
        a.update(status="ABSENT",
                 reason="the design material was written under product/ and stays there",
                 searched=["docs/graph/design/", "docs/graph/product/design-system.md"])
p.write_text(json.dumps(r, indent=2) + "\n")
PY
out44="$(python3 "$AUDIT" "$TMP/x44" "$ROOT" 2>&1)" || true
grep -q "CONTRADICTED agent ui-ux-designer" <<<"$out44" \
    || fail "an ABSENT agent row that searched a filled graph leaf passed"
grep -q "product/design-system.md' — among the paths it searched — is a filled leaf" <<<"$out44" \
    || fail "the filled leaf the absence found was not named"
grep -q "re-home it" <<<"$out44" || fail "the contradiction did not name the remedy"
# Source paths, a directory, and an untouched scaffold establish an absence.
python3 - "$TMP/x44" <<'PY'
import json, pathlib, sys
p = pathlib.Path(sys.argv[1])/".cypress/coverage.json"; r = json.loads(p.read_text())
for a in r["agents"]:
    if a["name"] == "ui-ux-designer":
        a["searched"] = ["src/", "docs/graph/design/", "docs/graph/design/README.md"]
p.write_text(json.dumps(r, indent=2) + "\n")
PY
out44="$(python3 "$AUDIT" "$TMP/x44" "$ROOT" 2>&1)" || true
! grep -q "CONTRADICTED agent ui-ux-designer" <<<"$out44" \
    || fail "an absence established against source paths and scaffolds was called a contradiction"

# --- 45. an UNKNOWN the delivery never names was filed, not asked ---------
# The seed's answer to "I cannot determine this" is record-and-report, and
# the record is not where anyone reads. A real plant marked legal/ UNKNOWN —
# "the owner's determination, not the graft's" — in a 43 KB JSON, and its
# delivery entry never said the word. The owner came away believing nothing
# had been grown at all.
rm -rf "$TMP/x45"; mkdir -p "$TMP/x45"
bash "$ROOT/install.sh" claude-code --project-dir "$TMP/x45" >/dev/null 2>&1
python3 "$AUDIT" "$TMP/x45" "$ROOT" --plan >/dev/null 2>&1 || true
python3 - "$TMP/x45" <<'PY'
import json, pathlib, sys
p = pathlib.Path(sys.argv[1])/".cypress/coverage.json"; r = json.loads(p.read_text())
for c in r["collections"]:
    if c["name"] == "legal/":
        c.update(status="UNKNOWN",
                 blocker="regulatory applicability is the owner's determination")
p.write_text(json.dumps(r, indent=2) + "\n")
PY
out45="$(python3 "$AUDIT" "$TMP/x45" "$ROOT" 2>&1)" || true
grep -q "SILENT       collection legal/" <<<"$out45" \
    || fail "an UNKNOWN row the changelog never names passed as reported"
grep -q "changelog.md never names it" <<<"$out45" \
    || fail "the silent UNKNOWN did not say where it should have been named"
# SILENT fails the gate; UNKNOWN itself never does.
python3 - "$ROOT" <<'PY'
import importlib.util, pathlib, sys
spec = importlib.util.spec_from_file_location(
    "ga", pathlib.Path(sys.argv[1])/"tools/growth-audit.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
assert m.Finding("SILENT", "x", "y").fatal(), "SILENT must fail the gate"
assert not m.Finding("UNKNOWN", "x", "y").fatal(), "UNKNOWN must not"
PY
# Named in the delivery entry — as a word, not a substring — it is reported.
printf '\n## 2026-09-10 — graft\n\n- `legal/` — UNKNOWN: regulatory applicability is the owner'"'"'s determination; waits on the owner.\n' \
    >> "$TMP/x45/docs/graph/changelog.md"
out45="$(python3 "$AUDIT" "$TMP/x45" "$ROOT" 2>&1)" || true
! grep -q "SILENT" <<<"$out45" || fail "an UNKNOWN named in the changelog was still SILENT"

printf 'growth coverage gate: PASS\n'
