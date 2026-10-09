#!/usr/bin/env bash
# test-growth-audit.sh: the coverage gate (tools/growth-audit.py) proves growth
# against a recorded plan, as protocols/grow.md and protocols/graft.md promise.
# Each case pins a false "grown", or an unpassable gate, that shipped for real.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AUDIT="$ROOT/tools/growth-audit.py"
SELF="$ROOT/tests/test-growth-audit.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
. "$ROOT/tests/helpers/plant.sh"

fail() { printf 'test-growth-audit: FAIL — %s\n' "$1" >&2; exit 1; }

# ga <plant> [flags]: run the audit; sets $out (stdout and stderr) and $rc.
ga() { local d="$1"; shift; out="$(python3 "$AUDIT" "$d" "$ROOT" "$@" 2>&1)" && rc=0 || rc=$?; }
has()   { grep -q -- "$1" <<<"$out" || { printf '%s\n' "$out" >&2; fail "$2"; }; }
lacks() { ! grep -q -- "$1" <<<"$out" || { printf '%s\n' "$out" >&2; fail "$2"; }; }
rc_is() { [ "$rc" -eq "$1" ] || { printf '%s\n' "$out" >&2; fail "$2 (exit $rc)"; }; }
plan()   { python3 "$AUDIT" "$1" "$ROOT" --plan >/dev/null 2>&1 || true; }
unfill() { python3 "$ROOT/tools/graft-audit.py" "$1" "$ROOT" --unfilled --rename >/dev/null 2>&1 || true; }

# patch_record <plant> [python]: run python (from $2, else stdin) with the
# record as `r` (None before --plan) and write it back. `g` is docs/graph,
# `seed` the seed root; by/write/body/all_absent/cover are shorthands.
# check_record runs the same without writing (for asserts).
PATCH_PRELUDE='import json, os, pathlib, re, sys
plant = pathlib.Path(sys.argv[1]); g = plant/"docs/graph"; seed = pathlib.Path(sys.argv[2])
f = plant/".cypress/coverage.json"; r = json.loads(f.read_text()) if f.exists() else None
def by(key, name): return next(x for x in r[key] if x["name"] == name)
def write(rel, text):
    p = g/rel; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(text)
def body(words, n=14): return "\n\n" + (words + " ") * n + "\n"
def all_absent():
    for c in r["collections"]:
        c.update(status="ABSENT", reason="the source shows no such evidence",
                 searched=["src/"], evidence=[], leaves=0)
    for a in r["agents"]:
        a.update(status="ABSENT", reason="its collections are absent-with-reason",
                 searched=["src/"])
def cover(name, rel):
    by("collections", name).update(status="COVERED", evidence=[rel], leaves=1,
                                   reason="", searched=[], blocker="")
'
patch_record() {
  local code; if [ $# -ge 2 ]; then code="$2"; else code="$(cat)"; fi
  python3 -c "$PATCH_PRELUDE
$code
if r is not None and not os.environ.get('PATCH_NOWRITE'):
    f.write_text(json.dumps(r, indent=2) + '\n')" "$1" "$ROOT" "${@:3}"
}
check_record() { PATCH_NOWRITE=1 patch_record "$@"; }

# Four bases, built once per run and copied per case:
#   installed  install.sh claude-code          planned  + --plan
#   absent     + every row ABSENT-with-reason  renamed  + --unfilled --rename
build_bases() {
  mkdir -p "$GA_BASES"
  PLANT_CACHE="$GA_BASES/cache" plant_base claude-code
  ln -s "$PLANT_BASE" "$GA_BASES/installed"
  cp -a "$PLANT_BASE" "$GA_BASES/planned"; plan "$GA_BASES/planned"
  cp -a "$GA_BASES/planned" "$GA_BASES/absent"
  patch_record "$GA_BASES/absent" 'all_absent()
r["inventory"] = [{"kind": "domain", "name": "batch etl", "status": "ABSENT",
                   "reason": "no artifact of its own; the architecture node owns it",
                   "searched": ["src/"], "evidence": ["docs/graph/index.md"],
                   "expect": [], "grounding": {"required": False, "sources": []}}]'
  cp -a "$GA_BASES/absent" "$GA_BASES/renamed"; unfill "$GA_BASES/renamed"
}
fixture() { rm -rf "$2"; mkdir -p "$2"; cp -a "$GA_BASES/$1/." "$2/"; }

# --- 1-9 on one plant: no record, --plan, planned artifacts, green, STALE ---
scn_shared() {
local p="$TMP/plant"
fixture installed "$p"
# 1. a plant with no record cannot be called grown
ga "$p"; rc_is 1 "a plant with no coverage record passed the gate"
has "MISSING" "a missing record was not reported as MISSING"
# 2. --plan derives its rows from the SEED, so a new template adds a row everywhere
ga "$p" --plan; rc_is 1 "--plan on an empty inventory should report the empty inventory"
for row in "design/" "tools/" "legal/" "best-practices/" "runbooks/rollback.md"; do
  has "collection $row" "--plan omitted the $row row"
done
for a in ui-ux-designer legal; do has "agent $a" "--plan omitted the $a agent row"; done
has "inventory is empty" "an empty inventory was not called out"
# 3. an inventory item's planned artifacts are checked, one by one
printf '<Project/>\n' > "$p/app.csproj"
patch_record "$p" 'r["inventory"] = [{"kind": "runtime", "name": "dotnet", "version": "9.0",
                   "significance": "core", "evidence": ["app.csproj:1"]}]'
python3 "$AUDIT" "$p" "$ROOT" --plan >/dev/null
ga "$p"; rc_is 1 "an ungrown inventory item passed the gate"
has "UNGROWN" "a missing planned artifact was not reported UNGROWN"
has "libraries/dotnet.md — does not exist" "the missing library page was not named"
has "best-practices/dotnet.md — does not exist" "the missing best-practices page was not named"
has "UNGROUNDED" "a runtime with no retrieved upstream source was not UNGROUNDED"
# 4. a scaffold is not coverage
mkdir -p "$p/docs/graph/libraries"
printf '# dotnet\n\n{{what this library is}}\n' > "$p/docs/graph/libraries/dotnet.md"
ga "$p"
has "HOLLOW" "a page still carrying a template placeholder was not HOLLOW"
has "template placeholder {{what this library is}}" "the placeholder that made the page hollow was not named"
# 5. an absence must be established, not just asserted
patch_record "$p" 'by("collections", "legal/")["status"] = "ABSENT"'
ga "$p"; has "UNJUSTIFIED  collection legal/" "an ABSENT row with no reason was accepted"
# 6. the plant's own files can contradict a COVERED claim
patch_record "$p" 'by("collections", "design/").update(status="COVERED", evidence=[])
by("agents", "ui-ux-designer")["status"] = "COVERED"'
ga "$p"
has "CONTRADICTED collection design/" "design/ claimed COVERED with only a scaffold was accepted"
has "CONTRADICTED agent ui-ux-designer" "ui-ux-designer claimed COVERED with no design material was accepted"
# 7. --agents answers the roster question on its own
ga "$p" --agents; has "agent legal" "--agents did not report the legal row"
! grep -qE "^  [A-Z]+ +collection " <<<"$out" || fail "--agents leaked collection rows"
# 8. a fully grown plant passes (legal corpus answered yes; case 14 is the no)
bash "$ROOT/install.sh" claude-code --project-dir "$p" --legal-corpus yes >/dev/null 2>&1
patch_record "$p" <<'PY'
BODY = "\n## Fact\n\n" + ("A project-specific fact with its source path. " * 14) + "\n"
def leaf(rel): write(rel, f"# {pathlib.Path(rel).stem}\n{BODY}")
for c in r["collections"]:
    rel = c["name"].rstrip("/") + "/overview.md" if c["name"].endswith("/") else c["name"]
    leaf(rel); cover(c["name"], f"docs/graph/{rel}")
for a in r["agents"]:
    a.update(status="COVERED", artifacts=[], reason="", searched=[], blocker="")
write("sources/normalized/dotnet-9-docs.md", "---\nraw: withheld — the upstream license "
      "forbids redistribution; URL and date are in the index row\n---\n# dotnet-9-docs\n" + BODY)
leaf("libraries/dotnet.md"); leaf("best-practices/dotnet.md")
write("nodes/expertise.dotnet.md",
      "---\nid: expertise.dotnet\ntier: 2\nkind: expertise\norigin: project\n"
      "title: dotnet — when this expertise is in play\nowns:\n"
      "  - dotnet.applicability\n  - dotnet.composition\nrequires:\n"
      "libraries:\n  - dotnet\nload_when:\n  - \"dotnet, csharp\"\n"
      "est_tokens: 120\n---\n" + BODY)
for it in r["inventory"]:
    it["status"] = "COVERED"
    it["grounding"]["sources"] = ["docs/graph/sources/normalized/dotnet-9-docs.md"]
    it["expert"] = {"warranted": False, "why": "the expertise node and its "
                    "composition cover it; nothing here needs a different "
                    "tool, model, stance, or isolation"}
PY
ga "$p"; rc_is 0 "a fully grown plant did not pass the gate"
has "coverage complete" "a passing audit did not say so"
# 9. a graft to a newer seed re-opens the record: grafted is not grown
patch_record "$p" 'r["seed_version"] = "0.0.1-old"'
ga "$p"; rc_is 1 "a record planned against an older seed still passed"
has "STALE" "a stale record was not reported STALE"
}

# --- 10-13: every bypass the first cut allowed, on one ungrown plant ---
scn_s9() {
local p="$TMP/s9"
fixture planned "$p"
# 10. a one-byte edit to a seed scaffold once marked a collection COVERED
printf 'x\n' >> "$p/docs/graph/legal/index.md"
printf 'x\n' >> "$p/docs/graph/design/README.md"
patch_record "$p" <<'PY'
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
PY
ga "$p"; [ "$rc" -ne 0 ] || fail "the false-green scenario passed the gate"
has "CONTRADICTED collection design/" "design/ covered by a one-byte edit to the seed's own README passed"
has "CONTRADICTED collection legal/" "legal/ covered by a one-byte edit to the seed's own index passed"
has "CONTRADICTED agent ui-ux-designer" "ui-ux-designer passed with no design material"
has "UNJUSTIFIED  regulatory-exposure gdpr" "an inventory row closed with a bare UNKNOWN and no blocker"
has "a planned artifact with no path" "a planned artifact with no path was skipped silently"
has "UNGROUNDED   framework react" "grounding cited to the sources directory was accepted"
# 11. agent coverage is all-of: a best-practices page does not cover design/
patch_record "$p" 'write("best-practices/react.md", "# react" + body("A normative standard and this project'"'"'s stance against it."))
for a in r["agents"]:
    a["status"] = "COVERED" if a["name"] == "ui-ux-designer" else ""'
ga "$p" --agents
has "CONTRADICTED agent ui-ux-designer" "one best-practices page covered an agent whose design/ is empty"
has "design/ holds no filled leaf" "the audit did not name WHICH declared collection was empty"
# 12. an absolute path is not a claim about this plant
patch_record "$p" 'r["inventory"] = [{"kind": "framework", "name": "react", "status": "COVERED",
                   "evidence": ["/etc/hostname"], "expect": [{"path": "libraries/react.md"}],
                   "grounding": {"required": False, "sources": []}}]'
ga "$p"; has "DANGLING" "an absolute path outside the plant was accepted as evidence"
# 13. a malformed record is named, not a traceback
printf '{"schema": "cypress.coverage/1", "collections": "nope"}\n' > "$p/.cypress/coverage.json"
ga "$p"; rc_is 2 "a malformed record did not exit 2"
}

# absent_gfm <dir> [python on `it`]: the renamed all-ABSENT plant with one
# honest ABSENT framework row `it`, edited by the python before it is stored.
absent_gfm() {
  fixture renamed "$1"
  patch_record "$1" 'it = {"kind": "framework", "name": "gfm", "slug": "gfm",
      "significance": "significant", "status": "ABSENT",
      "reason": "superseded by the markdown row", "searched": ["src/"],
      "evidence": ["docs/graph/index.md"], "expect": [],
      "grounding": {"required": False, "sources": []}}
'"${2:-}"'
r["inventory"] = [it]'
}

# --- 14, 46-51, 66: an honestly-empty plant, and what ABSENT still owes ---
scn_absent() {
local p="$TMP/absent"
fixture absent "$p"
# 14. an honest plant passes by establishing absences once the seed's scaffolds go
ga "$p"
has "still carries the seed's unfilled scaffold" "an ABSENT row over an untouched scaffold did not name it as one"
has "--unfilled --rename" "the scaffold contradiction did not name the remedy"
unfill "$p"
ga "$p"; rc_is 0 "an honestly-empty plant could not pass by establishing its absences"

# 46 (47, 48 folded): an ABSENT row still owes artifacts, grounding and staffing
# SPEC-0001 AUDIT_ABSENT_ROW_STILL_CHECKS_DECLARED_ARTIFACTS AUDIT_ABSENT_ROW_STILL_CHECKS_GROUNDING AUDIT_ABSENT_ROW_STILL_CHECKS_STAFFING
absent_gfm "$TMP/x46" 'it["expect"] = [{"path": "docs/graph/best-practices/gfm.md"}]'
ga "$TMP/x46"; rc_is 1 "an ABSENT row that owes a file it does not have passed the gate"
has "UNGROWN" "an ABSENT row's missing planned artifact was not reported UNGROWN"
has "best-practices/gfm.md — does not exist" "the missing artifact the ABSENT row declared was not named"
mkdir -p "$TMP/x46/docs/graph/best-practices"
printf '# gfm\n\n{{what this best practice is}}\n' > "$TMP/x46/docs/graph/best-practices/gfm.md"
ga "$TMP/x46"
has "HOLLOW" "an ABSENT row's placeholder-only artifact was not reported HOLLOW"
has "best-practices/gfm.md" "the hollow artifact was not named"
absent_gfm "$TMP/x47" 'it["grounding"]["required"] = True'   # 47
ga "$TMP/x47"; rc_is 1 "an ABSENT row that requires grounding it has not got passed the gate"
has "UNGROUNDED" "an ABSENT row requiring grounding and citing nothing was not UNGROUNDED"
has "framework gfm" "the ungrounded row was not named"
# whether an ABSENT row must declare `expect` is the owner's open question (grill §12 row 11)
lacks "BLANK        framework gfm" "an ABSENT row with no expect was made to answer for planned artifacts"
absent_gfm "$TMP/x48" 'it["significance"] = "core"'   # 48: no `expert` key, the question unasked
ga "$TMP/x48"; rc_is 1 "an ABSENT row left the staffing question unasked and passed the gate"
has "UNSTAFFED" "an ABSENT core row that records no staffing decision was not UNSTAFFED"
has "framework gfm" "the unstaffed row was not named"

# 49. an empty inventory is the cheapest green, so it is fatal
# SPEC-0001 AUDIT_EMPTY_INVENTORY_IS_A_FATAL_FINDING
fixture renamed "$TMP/x49"; patch_record "$TMP/x49" 'r["inventory"] = []'
ga "$TMP/x49"; rc_is 1 "a record with an empty inventory passed the gate"
has ".cypress/coverage.json" "the empty-inventory finding did not name the record"
has "inventory" "the empty-inventory finding did not say what was empty"
lacks "coverage complete" "a record holding nothing still summarised as coverage complete"

# 50. an UNKNOWN collection is carried, not dropped
# SPEC-0001 AUDIT_UNKNOWN_COLLECTION_ROW_IS_CARRIED
fixture renamed "$TMP/x50"
# the disclosure below writes changelog.md, so its row is honestly COVERED (SPEC-0001 §11)
patch_record "$TMP/x50" 'by("collections", "legal/").update(status="UNKNOWN",
    blocker="regulatory applicability is the owner'"'"'s determination")
by("collections", "changelog.md").update(status="COVERED",
    reason="the delivery log this growth pass wrote", searched=["src/"], evidence=[], leaves=1)'
cat >> "$TMP/x50/docs/graph/changelog.md" <<'MD'

## 2026-09-16 — growth

- `legal/` — UNKNOWN: regulatory applicability is the owner's determination.
  The collection stays empty until the owner rules on which regimes reach this
  plant. Nothing in the source settles the question, the audit record is not
  where anyone would read it, so it is put here: who decides, and by when.
- Every other collection closed ABSENT, with the paths searched recorded in
  the coverage record. This entry is the plant's own account of what the pass
  established and of the one thing it left open.
MD
ga "$TMP/x50"; rc_is 0 "a disclosed UNKNOWN must be carried, not enforced"
lacks "SILENT" "the UNKNOWN collection was named in the changelog and still reported SILENT"
has "UNKNOWN      collection legal/" "an UNKNOWN collection row produced no UNKNOWN finding"
has "regulatory applicability is the owner's determination" "the UNKNOWN finding did not quote the blocker the row named"
has "coverage complete (1 named blocker(s) carried)" "the carried blocker did not reach the summary count"

# 51. a cited line number has to exist in the file
# SPEC-0001 AUDIT_CITED_LINE_NUMBER_MUST_EXIST
absent_gfm "$TMP/x51" 'it["evidence"] = ["docs/graph/index.md:999999"]'
ga "$TMP/x51"; rc_is 1 "a citation pointing past the end of the file passed the gate"
has "DANGLING" "a citation past the end of a real file was not reported DANGLING"
has "docs/graph/index.md:999999" "the dangling citation was not named"
lines="$(wc -l < "$TMP/x51/docs/graph/index.md" | tr -d ' ')"
has "$lines" "the finding did not state the file's real line count ($lines)"
patch_record "$TMP/x51" 'r["inventory"][0]["evidence"] = ["docs/graph/index.md:1", "docs/graph/index.md"]'
ga "$TMP/x51"; lacks "DANGLING" "an in-range citation or a bare path stopped resolving"

# 66. a reference that does not parse is said not to parse, not called missing
absent_gfm "$TMP/x66" 'it["evidence"] = ["docs/graph/index.md:1 (the note that broke it)"]'
ga "$TMP/x66"
has "is not a path citation" "a reference that does not parse was not reported as one"
has "(the note that broke it)" "the malformed-reference finding did not name the part that did not parse"
lacks "does not exist in the plant" "a malformed citation over a file that exists was called a missing file"
patch_record "$TMP/x66" 'r["inventory"][0]["evidence"] = ["docs/graph/never-written.md"]'
ga "$TMP/x66"; rc_is 1 "a dangling citation passed the gate"
has "does not exist in the plant" "a genuinely missing citation stopped being reported as missing"
lacks "is not a path citation" "a well-formed citation was reported as unparseable"
echo "  an honest ABSENT plant passes, and ABSENT rows still owe what they declare — OK"
}

# the plant's own expert, before --plan. $1 = dir, $2 = name, $3 = what it reads
expert_file() {
  patch_record "$1" 'n, reads = sys.argv[3], sys.argv[4]
t = (f"---\nname: {n}\norigin: project\nplant_knowledge:\n  - {reads}\n---\n# {n}\n\n## Charter"
     + body("It owns settlement netting in this project."))
write(f"agents/{n}.md", t); (plant/".claude/agents"/f"{n}.md").write_text(t)' "$2" "$3"
}

# --- 15-18: an expert is projected, carried, and a real node ---
scn_staff() {
local p="$TMP/staff"
fixture installed "$p"
patch_record "$p" 'write("agents/claims-expert.md", "---\nname: claims-expert\norigin: project\nplant_knowledge:\n  - architecture/\n"
      "---\n# Claims expert\n\n## Charter" + body("It owns claims adjudication in this project.", 12))
(plant/"src").mkdir(exist_ok=True); (plant/"src/Adjudicator.cs").write_text("class Adjudicator {}\n")
write("architecture/claims.md", "# claims" + body("The adjudication pipeline and its rule sources."))'
plan "$p"   # the expert row is derived from the plant's own graph
grep -q "claims-expert" "$p/.cypress/coverage.json" || fail "--plan did not open an expert row for the plant's own expert"
patch_record "$p" 'for e in r["experts"]:
    e.update(status="COVERED", motivated_by=["src/Adjudicator.cs:1"])
r["inventory"] = [{"kind": "domain", "name": "claims adjudication",
                   "status": "COVERED", "evidence": ["src/Adjudicator.cs:1"],
                   "expect": [{"path": "architecture/claims.md", "why": "domain"}],
                   "grounding": {"required": False, "sources": []},
                   "expert": {"warranted": True, "name": "claims-expert",
                              "why": "every rule change touches three layers"}}]'
# 15. an expert never projected is not spawnable
ga "$p" --agents
has "UNGROWN      expert claims-expert" "an expert that reached the graph but no harness passed the gate"
has ".claude/agents/claims-expert.md" "the audit did not name the projection the expert is missing"
has "no claude-code session can spawn it" "the audit did not say why an unprojected expert is not a specialist"
# 16. a projection is a copy, not a second home
cp "$p/docs/graph/agents/claims-expert.md" "$p/.claude/agents/claims-expert.md"
ga "$p" --agents; lacks "expert claims-expert" "a projected expert still drew a finding"
printf 'edited only in the projection\n' >> "$p/.claude/agents/claims-expert.md"
ga "$p" --agents; has "CONTRADICTED expert claims-expert" "a projection edited away from its graph home was accepted"
cp "$p/docs/graph/agents/claims-expert.md" "$p/.claude/agents/claims-expert.md"
# 17. an expert the plant does not carry is staffing on paper
patch_record "$p" 'r["inventory"][0]["expert"]["name"] = "fraud-expert"
r["experts"].append({"name": "fraud-expert", "status": "COVERED",
                     "motivated_by": ["src/Adjudicator.cs:1"], "evidence": [],
                     "reason": "", "searched": [], "blocker": ""})'
ga "$p" --agents
has "UNSTAFFED    expert fraud-expert" "an item staffed with an expert the plant does not carry passed"
has "staffed on paper only" "the paper-staffing finding did not say what was wrong"
# 18. origin: project and plant_knowledge: are what make it the plant's node
patch_record "$p" 'a = g/"agents/claims-expert.md"
a.write_text(a.read_text().replace("origin: project\n", "").replace("plant_knowledge:\n  - architecture/\n", ""))
(plant/".claude/agents/claims-expert.md").write_text(a.read_text())
r["inventory"][0]["expert"]["name"] = "claims-expert"
r["experts"] = [e for e in r["experts"] if e["name"] == "claims-expert"]
for e in r["experts"]:
    e["motivated_by"] = []'
ga "$p" --agents
has "no \`origin: project\`" "an expert indistinguishable from seed machinery was accepted"
has "declares no \`plant_knowledge:\`" "an expert that declares nothing to read was accepted"
has "UNJUSTIFIED  expert claims-expert" "an expert citing nothing that motivated it was accepted"
}

# --- 19. declining to staff is a complete answer, silence is not ---
scn_nostaff() {
local p="$TMP/nostaff"
fixture absent "$p"
mkdir -p "$p/src"; printf 'print(1)\n' > "$p/src/main.py"
patch_record "$p" 'r["inventory"] = [{"kind": "domain", "name": "batch etl", "status": "COVERED",
                   "evidence": ["src/main.py:1"], "expect": [],
                   "grounding": {"required": False, "sources": []},
                   "expert": {"warranted": False}}]'
ga "$p"
has "UNSTAFFED    domain batch etl" "\`warranted: false\` with no reason was accepted as a decision"
has "is a decision, and a decision carries" "the unreasoned decline did not say what was missing"
patch_record "$p" 'it = r["inventory"][0]
it["expert"]["why"] = "ordinary etl; the base roster covers it"
it["expect"] = [{"path": "architecture/etl.md", "why": "domain"},
                {"path": "best-practices/batch-etl.md"}, {"path": "nodes/domain.batch-etl.md"}]
write("architecture/etl.md", "# etl" + body("The batch pipeline and where its stages live."))
write("best-practices/batch-etl.md", "# batch etl" + body("The etl standard and this project'"'"'s stance against it."))
write("nodes/domain.batch-etl.md", "# batch etl" + body("The routing node for the batch-etl domain."))'
unfill "$p"
patch_record "$p" 'cover("architecture/", "docs/graph/architecture/etl.md")
cover("best-practices/", "docs/graph/best-practices/batch-etl.md")'
ga "$p"; rc_is 0 "a plant that honestly declined to staff its domain could not pass"
}

# --- 20-24: the expert arm in the DEFAULT mode grow and graft run ---
scn_dflt() {
local p="$TMP/dflt"
fixture installed "$p"
patch_record "$p" 'write("agents/claims-expert.md", "---\nname: claims-expert\norigin: project\nplant_knowledge:\n  - architecture/\n"
      "---\n# Claims expert\n\n## Charter" + body("It owns claims adjudication in this project.", 12))
(plant/"src").mkdir(exist_ok=True); (plant/"src/A.cs").write_text("class A {}\n")
write("architecture/claims.md", "# claims" + body("The adjudication pipeline and where its stages live."))'
plan "$p"
experts_covered() { patch_record "$p" 'for e in r["experts"]:
    e.update(status="COVERED", motivated_by=["src/A.cs:1"])'; }
experts_covered
# 20. a core item with no `expert` object at all: every pre-staffing plant
patch_record "$p" 'r["inventory"] = [{"kind": "runtime", "name": "dotnet", "significance": "core",
     "status": "COVERED", "evidence": ["src/A.cs:1"], "expect": [{"path": "architecture/claims.md"}],
     "grounding": {"required": False, "sources": []}}]'
ga "$p"
has "UNGROWN      expert claims-expert" "the expert arm does not run in the DEFAULT mode grow and graft use"
has "UNSTAFFED    runtime dotnet" "a core item with no staffing decision at all passed"
has "records no staffing decision" "the unasked staffing question was not named as such"
# 21. a form is not an expert: a brace-stripped agent template
patch_record "$p" 't = (seed/"templates/agent.template.md").read_text().split("-->\n", 1)[1]
t = re.sub(r"\{\{|\}\}", "", t)
write("agents/form-expert.md", t); (plant/".claude/agents/form-expert.md").write_text(t)'
plan "$p"; experts_covered
ga "$p" --agents
has "HOLLOW       expert form-expert" "a filled-in copy of the agent template passed as an expert"
has "inherited from its seed template" "the template copy was not named as inherited content"
rm -f "$p/docs/graph/agents/form-expert.md" "$p/.claude/agents/form-expert.md"
# 22. seed-ness is derived, never self-declared
patch_record "$p" 'write("agents/fraud-expert.md", "---\nname: fraud-expert\norigin: seed\nplant_knowledge:\n  - architecture/\n"
      "---\n# Fraud\n\n## Charter" + body("It owns fraud scoring in this project."))'
ga "$p" --agents; has "expert fraud-expert" "an expert declaring origin: seed made itself invisible to the gate"
rm -f "$p/docs/graph/agents/fraud-expert.md"
# 23. the declared name and the filename have to agree (after an ordering prefix)
patch_record "$p" 'a = g/"agents/claims-expert.md"
a.write_text(a.read_text().replace("name: claims-expert", "name: claims-adjudicator"))
(plant/".claude/agents/claims-expert.md").write_text(a.read_text())'
ga "$p" --agents
has "HOLLOW       expert claims-expert" "a frontmatter name disagreeing with the filename was accepted"
has "only some of them can call" "the name disagreement was not reported as the callability defect it is"
patch_record "$p" 'a = g/"agents/claims-expert.md"
a.write_text(a.read_text().replace("name: claims-adjudicator", "name: claims-expert"))
(plant/".claude/agents/claims-expert.md").write_text(a.read_text())'
# 23b. an ordering prefix is presentation, not identity
patch_record "$p" 'node = ("---\nname: ordered-expert\norigin: project\nplant_knowledge:\n  - architecture/\n---\n"
        "# Ordered expert\n\n## Charter" + body("It owns settlement timing in this project.", 13))
write("agents/20-ordered-expert.md", node); (plant/".claude/agents/20-ordered-expert.md").write_text(node)'
plan "$p"; experts_covered
ga "$p" --agents; lacks "only some of them can call" "a numbered file declaring the name with its prefix off was failed"
# ... and the rule holds of the one roster known to be correct: the seed's own
python3 - "$ROOT" <<'PY' || fail "the name rule does not hold of the seed's own roster"
import importlib.util, pathlib, sys
seed = pathlib.Path(sys.argv[1])
spec = importlib.util.spec_from_file_location("ga", seed/"tools/growth-audit.py")
ga = importlib.util.module_from_spec(spec); spec.loader.exec_module(ga)
files = sorted((seed/"agents").glob("*.md"))
assert files, "the seed carries no agents/ to test the rule against"
bad = [(p.name, n) for p in files
       for n in [str(ga.parse_frontmatter(p).get("name") or "").strip()]
       if n and n != ga.spawn_name(p.stem)]
assert not bad, f"the seed's own roster fails the rule the audit applies: {bad}"
PY
rm -f "$p/docs/graph/agents/20-ordered-expert.md" "$p/.claude/agents/20-ordered-expert.md"
# 24. a stamp with no projection paths must not pass every registration check
patch_record "$p" 's = plant/".cypress/seed.json"; d = json.loads(s.read_text())
d.pop("agent_projections", None); s.write_text(json.dumps(d, indent=2) + "\n")'
ga "$p" --agents; has "STALE        .cypress/seed.json" "a stamp recording no projection paths silently passed every expert"
}

# --- 25-26: the rest of the expert row's promises ---
scn_rows() {
local p="$TMP/rows"
fixture installed "$p"
expert_file "$p" netting-expert design/
plan "$p"
# 25. no row -> MISSING; ABSENT over a live file; a motivation that dangles
patch_record "$p" 'r["experts"] = []'
ga "$p" --agents; has "MISSING      expert netting-expert" "an expert the plant carries with no row in the record passed"
patch_record "$p" 'r["experts"] = [{"name": "netting-expert", "status": "ABSENT", "reason": "not needed",
                  "searched": ["src/"], "motivated_by": [], "evidence": []}]'
ga "$p" --agents; has "CONTRADICTED expert netting-expert" "an expert claimed ABSENT while its file exists was accepted"
patch_record "$p" 'r["experts"] = [{"name": "netting-expert", "status": "COVERED",
                  "motivated_by": ["src/nowhere.cs:1"], "evidence": [],
                  "reason": "", "searched": [], "blocker": ""}]'
ga "$p" --agents
has "DANGLING     expert netting-expert" "an expert motivated by a path that does not exist was accepted"
has "design/ holds nothing this plant wrote" "an expert declaring a collection with nothing in it was accepted"
patch_record "$p" 'r["experts"][0]["motivated_by"] = ["docs/graph/agents/netting-expert.md"]'
ga "$p" --agents; has "cannot be its own evidence" "an expert citing its own agent file as what motivated it passed"
# 26. a staffing decision is a boolean, not a remark
mkdir -p "$p/src"; printf 'class N {}\n' > "$p/src/N.cs"
patch_record "$p" 'r["inventory"] = [{"kind": "domain", "name": "netting", "status": "COVERED",
                   "evidence": ["src/N.cs:1"], "expect": [{"path": "design/x.md"}],
                   "grounding": {"required": False, "sources": []},
                   "expert": {"warranted": "no", "why": "looks fine"}}]'
ga "$p"; has "not true or false" "a staffing decision of \"no\" was read as a decision"
patch_record "$p" 'r["inventory"][0]["expert"] = {"warranted": True, "name": "netting-expert"}'
ga "$p"; has "gives no reason" "an expert warranted with no reason was accepted"
patch_record "$p" 'r["inventory"][0]["expert"] = {"warranted": True, "why": "a recurring shape"}'
ga "$p"; has "warrants a project-specific expert and names none" "a surface warranted an expert, named none, and passed"
}

# --- 27. an untouched copy of a seed agent is a form, not an expert ---
scn_copy() {
local p="$TMP/copy"
fixture installed "$p"
cp "$ROOT/agents/05-security.md" "$p/docs/graph/agents/payments-expert.md"
cp "$ROOT/agents/05-security.md" "$p/.claude/agents/payments-expert.md"
plan "$p"
patch_record "$p" 'for e in r["experts"]:
    e.update(status="COVERED", motivated_by=["docs/graph/index.md"])'
ga "$p" --agents; has "byte-identical to " "a seed agent copied under a new name passed as a project expert"
}

# expertise_plant <dir> <significance> [kind]: a planned plant with one dotnet
# item, re-planned so its expect is derived.
expertise_plant() {
  fixture planned "$1"; printf '<Project/>\n' > "$1/app.csproj"
  patch_record "$1" 'r["inventory"] = [{"kind": sys.argv[4], "name": "dotnet", "version": "9.0",
                   "significance": sys.argv[3], "evidence": ["app.csproj:1"]}]' "$2" "${3:-runtime}"
  plan "$1"
}
planned_paths() { check_record "$1" 'print("\n".join(e["path"] for i in r["inventory"] for e in i.get("expect", [])))'; }

# --- 28 (29, 30 folded): who owes an expertise node, derived from the inventory ---
scn_x28() {
#   significance kind        owes a node
for row in "core runtime yes" "significant dependency yes" "incidental dependency no"; do
  set -- $row
  expertise_plant "$TMP/x28" "$1" "$2"
  if [ "$3" = yes ]; then
    planned_paths "$TMP/x28" | grep -q "nodes/expertise.dotnet.md" || fail "--plan did not derive an expertise node for a $1 $2"
  else   # 30: an incidental dependency keeps only its index line
    planned_paths "$TMP/x28" | grep -q "libraries/index.md" || fail "an incidental dependency lost its index line"
    ! planned_paths "$TMP/x28" | grep -q "expertise" || fail "an incidental dependency was planned an expertise node"
  fi
  if [ "$1" = core ]; then
    ga "$TMP/x28"; has "UNGROWN" "an unwritten expertise node did not fail the gate"
    has "nodes/expertise.dotnet.md — does not exist" "the missing expertise node was not named"
  fi
done
# 30: an incidental item of another kind keeps its pages and grounding, and owes no node
expertise_plant "$TMP/x30b" incidental
check_record "$TMP/x30b" 'it = r["inventory"][0]; paths = [e["path"] for e in it["expect"]]
assert paths == ["libraries/dotnet.md", "best-practices/dotnet.md"], paths
assert it["grounding"]["required"] is True, "incidental non-dependency lost grounding"' || exit 1
}

# --- 31. a filled-in form is not an expertise node ---
scn_x31() {
expertise_plant "$TMP/x31" core
patch_record "$TMP/x31" 'text = (seed/"templates/docs/nodes/_expertise.template.md").read_text()
write("nodes/expertise.dotnet.md", re.sub(r"\{\{([^}]*)\}\}", lambda m: m.group(1).split(",")[0][:24], text, flags=re.S))'
ga "$TMP/x31"
has "nodes/expertise.dotnet.md — holds .* bytes this plant wrote" "a brace-stripped copy of the expertise form passed as a node"
has "inherited from its seed template" "the expertise form's own prose was not named as inherited content"
}

# a substantive expertise.dotnet node; $2 = the frontmatter edge block
EXPERTISE_NODE='"---\nid: expertise.dotnet\ntier: 2\nkind: expertise\norigin: project\n"
    "title: dotnet applicability\nowns:\n  - dotnet.applicability\n"
    "  - dotnet.composition\nrequires:\n" + sys.argv[3] + "load_when:\n  - dotnet, csharp\n"
    "est_tokens: 120\n---\n\n" + "A project-specific applicability fact with its source path. " * 12 + "\n"'

# --- 32. a node that routes to no pin home is not a node ---
scn_x32() {
expertise_plant "$TMP/x32" core
patch_record "$TMP/x32" "write('nodes/expertise.dotnet.md', $EXPERTISE_NODE)" $'artifacts:\n  - best-practices/dotnet.md\n'
ga "$TMP/x32"; has "names no .libraries: dotnet." "an expertise node routing to no pin home passed"
}

# --- 33. two majors compose one child per major, ordered as numbers ---
scn_x33() {
local p="$TMP/x33"
fixture planned "$p"; printf '<Project/>\n' > "$p/app.csproj"
patch_record "$p" 'r["inventory"] = [
    {"kind": "runtime", "name": "dotnet", "slug": "dotnet", "version": v,
     "significance": "core", "evidence": ["app.csproj:1"]} for v in ("8.0", "10.0")]'
ga "$p" --plan
has "NEEDS COMPOSITION dotnet runs majors 8, 10" "two majors of one stack did not ask for a child per major, in order"
check_record "$p" 'paths = [e["path"] for e in r["inventory"][0]["expect"]]
for want in ("nodes/expertise.dotnet.md", "nodes/expertise.dotnet-8.md", "nodes/expertise.dotnet-10.md"):
    assert want in paths, (want, paths)' || exit 1
}

# --- 34. a plant that owes no expertise still goes green ---
scn_x34() {
local p="$TMP/x34"
fixture absent "$p"
patch_record "$p" 'r["inventory"] = [{"kind": "dependency", "name": "left-pad", "version": "1.0",
                   "significance": "incidental", "status": "COVERED", "evidence": ["docs/graph/index.md"]}]'
plan "$p"; unfill "$p"
patch_record "$p" 'write("libraries/index.md", "# Libraries index\n\n| Library | Version | Page | Used by |\n|---|---|---|---|\n"
      + "| left-pad | 1.0 | index line only, incidental | src/app.js |\n" * 8)
cover("libraries/", "docs/graph/libraries/index.md")'
ga "$p"; rc_is 0 "a plant that owes no expertise node could not go green"
check_record "$p" 'assert not any("expertise" in e["path"] for e in r["inventory"][0]["expect"])' || exit 1
}

# --- 35-37. an expert may declare the expertise node it reads ---
scn_x35() {
local p="$TMP/x35"
fixture installed "$p"
expert_file "$p" netting-expert expertise.dotnet
plan "$p"
patch_record "$p" 'r["experts"] = [{"name": "netting-expert", "status": "COVERED",
                  "motivated_by": ["docs/graph/index.md"], "evidence": [],
                  "reason": "", "searched": [], "blocker": ""}]'
# 36. the node it names does not exist -> DANGLING
ga "$p" --agents
has "declares it reads node .expertise.dotnet." "an expert naming a node the plant does not carry was accepted"
has "DANGLING" "a missing declared node was not DANGLING"
# 37. the node is still the form -> CONTRADICTED
cp "$ROOT/templates/docs/nodes/_expertise.template.md" "$p/docs/graph/nodes/expertise.dotnet.md"
ga "$p" --agents; has "CONTRADICTED expert netting-expert" "an expert reading a node that is still a form was accepted"
# 35. a real node -> the row passes
patch_record "$p" "write('nodes/expertise.dotnet.md', $EXPERTISE_NODE)" $'libraries:\n  - dotnet\n'
ga "$p" --agents
lacks "DANGLING  *expert netting-expert" "an expert reading a real expertise node was still reported"
lacks "CONTRADICTED  *expert netting-expert" "an expert reading a real expertise node was still reported"
}

# --- 38. an agent on top of a node needs what a node cannot be ---
scn_x38() {
expertise_plant "$TMP/x38" core
patch_record "$TMP/x38" 'r["inventory"][0]["expert"] = {"warranted": True, "name": "dotnet-expert", "why": "it is important"}'
ga "$TMP/x38"
has "UNSTAFFED" "an agent warranted without naming what a node cannot serve passed"
has "tools, model, stance, isolation" "the UNSTAFFED message did not name the four spawn triggers"
patch_record "$TMP/x38" 'r["inventory"][0]["expert"]["needs"] = "isolation"'
ga "$TMP/x38"; lacks 'needs. is' "a staffing decision naming its trigger was still reported"
}

# --- 39. an expertise node planned for an item that owes none is over-growth ---
scn_x39() {
expertise_plant "$TMP/x39" incidental dependency
patch_record "$TMP/x39" 'r["inventory"][0]["expect"] = [{"path": "libraries/index.md", "why": "incidental"},
    {"path": "nodes/expertise.dotnet.md", "why": "hand-added over-growth"}]'
ga "$TMP/x39"; has "which this item does not owe" "an expertise node planned for an item that owes none was accepted"
}

# --- 40. an expert's declared read must name a real collection ---
scn_x40() {
local p="$TMP/x40"
fixture installed "$p"
expert_file "$p" typo-expert desing/
expert_file "$p" slashless-expert data
plan "$p"
patch_record "$p" 'for e in r["experts"]:
    e.update(status="COVERED", motivated_by=["docs/graph/index.md"])'
ga "$p" --agents
has "declares it reads collection 'desing/'" "an expert declaring a collection that does not exist was accepted"
has "declares it reads collection 'data'" "an expert declaring a slash-less collection name was accepted"
}

# --- 41. an authored absence statement is not an unfilled scaffold ---
scn_x41() {
local p="$TMP/x41"
fixture absent "$p"
# (a) design/README.md untouched; (b) legal/index.md authored; (c) api/README.md
# past the floor and still holding a placeholder
patch_record "$p" 'write("legal/index.md", "# Legal\n\n## No regulatory exposure was established\n\n"
    + ("This project holds no personal data and moves no money; the absence "
       "was established by reading every entry point and every persistence "
       "call under src/. " * 6)
    + "\n\n## Considered and excluded\n\n"
    + ("A vendor terms file under vendor/ names an obligation on the vendor "
       "rather than on this project, so it earns no page here. " * 4) + "\n")
write("api/README.md", "# API\n\n" + ("The surface was walked and each finding below carries the source path "
      "it came from. " * 10) + "\n\n{{what this collection covers}}\n")'
ga "$p"
has "CONTRADICTED collection design/" "an untouched seed scaffold in an ABSENT collection stopped failing"
lacks "collection legal/" "an authored leaf was called an unfilled scaffold because the seed templates its path"
has "CONTRADICTED collection api/" "a leaf still carrying a template placeholder passed as authored"
# the remedy named must act on the leaf: --unfilled judges by byte-identity
grep -A1 "CONTRADICTED collection design/" <<<"$out" | grep -q -- "--unfilled --rename" \
    || fail "the byte-identical scaffold no longer names the remedy that acts on it"
! grep -A1 "CONTRADICTED collection api/" <<<"$out" | grep -q -- "--unfilled --rename" \
    || fail "a finding prescribed a remedy that cannot act on the leaf it names"
unfill "$p"; rm -f "$p/docs/graph/api/README.md"
ga "$p"; rc_is 0 "a plant that authored its absence statement could not pass the gate"
[[ -f "$p/docs/graph/legal/index.md" ]] || fail "the authored leaf had to be destroyed for the plant to pass"
}

# --- 42. the index line an incidental item owes has to be in the index ---
scn_x42() {
expertise_plant "$TMP/x42" incidental dependency
ga "$TMP/x42"
has "UNGROWN      dependency dotnet" "an incidental item with no index row passed"
has "libraries/index.md has no row naming 'dotnet'" "the missing index row was not named"
printf '| dotnet | 9.0 | — | build | healthy | MIT | 2026-09-10 |\n' >> "$TMP/x42/docs/graph/libraries/index.md"
ga "$TMP/x42"; lacks "UNGROWN      dependency dotnet" "an incidental item with its index row was still reported UNGROWN"
# whole-cell, never substring: a row for a longer sibling is not this item's
expertise_plant "$TMP/x42b" incidental dependency
printf '| dotnet-tools | 1.0 | — | | | | |\n' >> "$TMP/x42b/docs/graph/libraries/index.md"
ga "$TMP/x42b"; has "UNGROWN      dependency dotnet" "a row for a longer sibling name passed as the incidental item's own"
}

# --- 43. a normalized source keeps its raw snapshot, or records why not ---
scn_x43() {
local p="$TMP/x43" page="$TMP/x43/docs/graph/sources/normalized/react.md"
fixture planned "$p"
patch_record "$p" 'write("sources/normalized/react.md", "# react docs\n\n## Fact\n\n" + ("A retrieved upstream fact with its URL. " * 14) + "\n")
by("collections", "sources/").update(status="COVERED", leaves=1, evidence=["docs/graph/sources/normalized/react.md"])'
ga "$p"
has "UNJUSTIFIED  collection sources/" "a normalized source with no raw snapshot and no reason passed"
has "normalized/react.md retains no raw snapshot" "the snapshot without provenance was not named"
body43="$(cat "$page")"
printf -- '---\nraw: withheld — react.dev terms forbid redistribution; URL and date are in the index row\n---\n%s\n' "$body43" > "$page"
ga "$p"; lacks "normalized/react.md retains no raw snapshot" "a normalized source that recorded why no raw was kept was still reported"
printf -- '---\nraw: raw/react-2026-09-10.html\n---\n%s\n' "$body43" > "$page"
ga "$p"; has 'raw: raw/react-2026-09-10.html`, which does not exist' "a raw: line naming a missing snapshot passed"
printf '<html>react</html>\n' > "$p/docs/graph/sources/raw/react-2026-09-10.html"
ga "$p"; lacks "collection sources/" "a normalized source with its raw sibling on disk was still reported"
}

# --- 44. an absence whose search found a filled leaf is a redirect ---
scn_x44() {
local p="$TMP/x44"
fixture planned "$p"
patch_record "$p" 'write("product/design-system.md", "# design system\n\n## Tokens\n\n" + ("A token and its value, with the screen it serves. " * 14) + "\n")
by("agents", "ui-ux-designer").update(status="ABSENT",
    reason="the design material was written under product/ and stays there",
    searched=["docs/graph/design/", "docs/graph/product/design-system.md"])'
ga "$p"
has "CONTRADICTED agent ui-ux-designer" "an ABSENT agent row that searched a filled graph leaf passed"
has "product/design-system.md' — among the paths it searched — is a filled leaf" "the filled leaf the absence found was not named"
has "re-home it" "the contradiction did not name the remedy"
patch_record "$p" 'by("agents", "ui-ux-designer")["searched"] = ["src/", "docs/graph/design/", "docs/graph/design/README.md"]'
ga "$p"; lacks "CONTRADICTED agent ui-ux-designer" "an absence established against source paths and scaffolds was called a contradiction"
}

# --- 45. an UNKNOWN the delivery never names was filed, not asked ---
scn_x45() {
local p="$TMP/x45"
fixture planned "$p"
patch_record "$p" 'by("collections", "legal/").update(status="UNKNOWN",
    blocker="regulatory applicability is the owner'"'"'s determination")'
ga "$p"
has "SILENT       collection legal/" "an UNKNOWN row the changelog never names passed as reported"
has "changelog.md never names it" "the silent UNKNOWN did not say where it should have been named"
python3 - "$ROOT" <<'PY'   # SILENT fails the gate; UNKNOWN itself never does
import importlib.util, pathlib, sys
spec = importlib.util.spec_from_file_location("ga", pathlib.Path(sys.argv[1])/"tools/growth-audit.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
assert m.Finding("SILENT", "x", "y").fatal(), "SILENT must fail the gate"
assert not m.Finding("UNKNOWN", "x", "y").fatal(), "UNKNOWN must not"
PY
printf '\n## 2026-09-10 — graft\n\n- `legal/` — UNKNOWN: regulatory applicability is the owner'"'"'s determination; waits on the owner.\n' \
    >> "$p/docs/graph/changelog.md"
ga "$p"; lacks "SILENT" "an UNKNOWN named in the changelog was still SILENT"
}

# $1 = plant dir, $2 = page stem, $3 = the `raw:` value ("" writes no raw key)
raw_page() {
  patch_record "$1" 'stem, val = sys.argv[3], sys.argv[4]
head = f"---\nraw: {val}\n---\n" if val else ""
write(f"sources/normalized/{stem}.md", head + f"\n# {stem} docs\n\n## Fact\n\n" + ("A retrieved upstream fact with its URL. " * 14) + "\n")' "$2" "$3"
}
# raw_case <stem> <raw value> [snapshots on disk...]: one page on a fresh copy
# of the raw base, audited into $out/$rc
raw_case() {
  local stem="$1" val="$2" s; shift 2
  rm -rf "$TMP/raw"; cp -a "$TMP/rawbase" "$TMP/raw"
  raw_page "$TMP/raw" "$stem" "$val"
  for s in "$@"; do printf '<html>%s</html>\n' "$s" > "$TMP/raw/docs/graph/sources/raw/$s"; done
  ga "$TMP/raw"
}

# --- 52 (53-57, 67 folded): a `raw:` line is TESTED, never assumed ---
# Every dangling row plants a same-stem sibling, or it passes for the wrong reason.
scn_rawbase() {
fixture planned "$TMP/rawbase"
patch_record "$TMP/rawbase" '(g/"sources/normalized").mkdir(parents=True, exist_ok=True)
(g/"sources/raw").mkdir(parents=True, exist_ok=True)
by("collections", "sources/").update(status="COVERED", leaves=1, evidence=["docs/graph/sources/normalized/react.md"])'
S=react-2026-09-11.html D=upstream-doc-2026-09-10.html
# 52. a named path that does not resolve is reported, sibling or not
# SPEC-0001 AUDIT_NAMED_RAW_PATH_IS_TESTED_NOT_ASSUMED
raw_case react "raw/$D" "$S"; rc_is 1 "a dangling raw: path behind a stem match passed the gate"
has "UNJUSTIFIED  collection sources/" "a raw: naming a path that does not exist passed because a same-stem sibling was on disk"
has "normalized/react.md" "the page whose raw: named a missing snapshot was not named"
has "$D" "the token that did not resolve was not named"
# 53. a named path that DOES resolve is never reported missing
# SPEC-0001 AUDIT_EXISTING_RAW_PATH_IS_NOT_REPORTED_MISSING
raw_case react "raw/$D" "$D"
lacks "normalized/react.md" "a raw: path that is on disk was reported missing (no stem sibling to save it)"
lacks "does not exist" "the tool asserted a path does not exist without having opened it"
# 54. every token of a multi-token value must resolve
# SPEC-0001 AUDIT_EVERY_NAMED_RAW_PATH_MUST_RESOLVE
raw_case react "raw/$D (the abstract page), raw/upstream-appendix-2026-09-10.html" "$D" "$S"
rc_is 1 "a raw: value with one unresolvable token passed the gate"
has "UNJUSTIFIED  collection sources/" "a multi-token raw: with one broken token passed because the value was not a bare path"
has "upstream-appendix-2026-09-10.html" "the token that did not resolve was not named"
lacks "$D" "the finding named a token that DID resolve"
# 55. a recorded reason is still provenance; with no reason the page is reported
# SPEC-0001 AUDIT_RAW_PROSE_REASON_IS_STILL_ACCEPTED
raw_case react "withheld - the Open Group copyright terms forbid redistribution; posix-spec.html is named in the index row instead"
lacks "normalized/react.md" "a page that recorded WHY no snapshot was kept was reported"
lacks "posix-spec.html" "a filename inside the prose, with no raw/ prefix, was read as a path token and tested"
raw_page "$TMP/raw" react ""; ga "$TMP/raw"
has "normalized/react.md retains no raw snapshot" "the guard is vacuous — this page is not reached by the check at all"
# 56. the sibling scan still satisfies a page that names no path
# SPEC-0001 AUDIT_RAW_SIBLING_SATISFIES_A_PAGE_THAT_NAMES_NO_PATH
raw_case react "" "$S"
lacks "normalized/react.md" "a page naming no path, with its snapshot on disk, was reported"
rm -f "$TMP/raw/docs/graph/sources/raw/$S"; ga "$TMP/raw"
has "normalized/react.md retains no raw snapshot" "the sibling scan is vacuous — the page passes with no snapshot either"
# 57. the finding names the resolved path it tested, so `ls` reproduces it
# SPEC-0001 AUDIT_RAW_FINDING_NAMES_THE_PATH_IT_TESTED
raw_case vue "raw/missing-snapshot-2026-09-10.html" vue-2026-09-11.html
has "UNJUSTIFIED  collection sources/" "the fixture produced no UNJUSTIFIED finding to inspect"
has "docs/graph/sources/raw/missing-snapshot-2026-09-10.html" "the finding did not name the resolved path it opened, only the token and the directory"
resolved="$(grep -F 'normalized/vue.md' <<<"$out" \
            | grep -oE 'docs/graph/sources/raw/[A-Za-z0-9._-]+\.[A-Za-z0-9]{1,5}' | head -1 || true)"
[[ -n "$resolved" ]] || fail "no resolved path could be read out of the finding"
[[ ! -e "$TMP/raw/$resolved" ]] || fail "the finding claimed a path is absent and ls on that same string finds it: $resolved"
# 67. a bare token is opened too, not only a raw/-prefixed one
raw_case vue "upstream-guide-2026-09-10.html" upstream-guide-2026-09-10.html
lacks "normalized/vue.md" "a bare raw: token whose snapshot is on disk was reported missing"
rm -f "$TMP/raw/docs/graph/sources/raw/upstream-guide-2026-09-10.html"; ga "$TMP/raw"
rc_is 1 "a normalized page whose named snapshot is absent passed the gate"
has "docs/graph/sources/raw/upstream-guide-2026-09-10.html" "a bare raw: token naming a snapshot that is not there went unreported"
echo "  a raw: line is resolved token by token, never assumed — OK"
}

# domain_plant <dir>: a planned plant with one domain row as every grown plant
# has it: grounding required:false, and a hand-written expect.
domain_plant() {
  fixture planned "$1"
  patch_record "$1" 'r["inventory"] = [{"kind": "domain", "name": "the widget catalog",
                   "slug": "widget-catalog", "significance": "core",
                   "evidence": ["docs/graph/index.md:1"],
                   "expect": [{"path": "architecture/widget-catalog.md",
                               "why": "hand-written; the tool cannot derive it"}],
                   "grounding": {"required": False, "sources": []},
                   "expert": {"warranted": False, "why": "the docs-librarian already holds it"}}]'
}

# --- 58 (59, 60 folded): --plan migrates a planned record one way only ---
# SPEC-0001 AUDIT_PLAN_RAISES_DOMAIN_GROUNDING AUDIT_PLAN_UNIONS_HANDWRITTEN_EXPECT
scn_x58() {
local p="$TMP/x58"
domain_plant "$p"
# 59: an objective whose record already carries grounding true
# SPEC-0001 AUDIT_PLAN_NEVER_LOWERS_GROUNDING
patch_record "$p" 'r["inventory"].append({"kind": "objective", "name": "O9", "slug": "o9",
    "evidence": ["docs/graph/index.md:1"], "grounded_by": ["widget-catalog"],
    "grounding": {"required": True, "sources": []}})'
plan "$p"
check_record "$p" 'k = {i["kind"]: i for i in r["inventory"]}
assert k["domain"]["grounding"]["required"] is True, ("58: domain grounding not raised", k["domain"]["grounding"])
assert k["objective"]["grounding"]["required"] is True, "59: objective was lowered"
paths = [e["path"] for e in k["domain"]["expect"]]
assert "architecture/widget-catalog.md" in paths, ("60: hand-written path dropped", paths)
assert "best-practices/widget-catalog.md" in paths, ("60: owed page not added", paths)
assert "nodes/domain.widget-catalog.md" in paths, ("60: owed node not added", paths)
assert not any("expertise" in p for p in paths), ("60: domain minted an expertise node", paths)' \
  || fail "--plan did not migrate the domain row one way"
plan "$p"   # 59: a second --plan never lowers the domain it raised
check_record "$p" 'assert r["inventory"][0]["grounding"]["required"] is True' \
  || fail "--plan lowered a grounding it found already true"
}

# --- 61. a domain row owes a grounded best-practices page and its node ---
# SPEC-0001 AUDIT_DOMAIN_ROW_OWES_GROUNDED_PAGE
scn_x61() {
local p="$TMP/x61"
domain_plant "$p"; plan "$p"
patch_record "$p" 'r["inventory"][0]["status"] = "COVERED"'
ga "$p"; rc_is 1 "a domain row owing an ungrounded page passed the gate"
has "best-practices/widget-catalog.md — does not exist" "a domain row that owes a best-practices page did not report it missing"
has "nodes/domain.widget-catalog.md — does not exist" "a domain row that owes its routing node did not report it missing"
has "UNGROUNDED   domain the widget catalog" "a domain row with grounding required and no source was not UNGROUNDED"
}

# the grounded kg domain an objective rests on; `ob` names the objective row
KG_DOMAIN='write("best-practices/kg.md", "# kg" + body("A grounded idea and its retrieved source."))
write("nodes/domain.kg.md", "# kg" + body("The routing node for the kg domain."))
write("sources/normalized/kg.md", "---\nraw: withheld — upstream terms forbid redistribution; URL in the index\n---\n"
      "# kg source" + body("A retrieved upstream fact with its URL."))
r["inventory"] = [
    {"kind": "domain", "name": "kg", "slug": "kg", "significance": "core",
     "status": "COVERED", "evidence": ["docs/graph/index.md:1"],
     "expect": [{"path": "best-practices/kg.md"}, {"path": "nodes/domain.kg.md"}],
     "grounding": {"required": True, "sources": ["docs/graph/sources/normalized/kg.md"]},
     "expert": {"warranted": False, "why": "the librarian holds it"}},
    {"kind": "objective", "name": ob, "slug": ob.lower(), "status": "COVERED",
     "evidence": ["docs/graph/index.md:1"], "grounded_by": ["kg"],
     "expect": [{"path": "plans/objectives.md"}],
     "grounding": {"required": False, "sources": []}}]
write("plans/objectives.md", "# Objectives\n\n## O1. Portability across stack and host"
      + body("The portability objective, derived from executable source."))'

# --- 62-63: an objective's artifact names its row; grounded_by has teeth ---
scn_x62x63() {
local p="$TMP/x62" q="$TMP/x63"
fixture planned "$p"
patch_record "$p" "ob = 'O2'
$KG_DOMAIN"
# 62. one objectives.md serves every row, so it must NAME this one
# SPEC-0001 AUDIT_OBJECTIVE_ARTIFACT_MUST_NAME_THE_ROW
ga "$p"
has "UNGROWN      objective O2" "an objective whose one artifact never names it was not caught"
has "names no section for 'O2'" "the objective's unnamed-row finding did not name the row it missed"
patch_record "$p" 'o = g/"plans/objectives.md"
o.write_text(o.read_text() + "\n## O2. Keep a codebase inside a context window" + body("The context objective, derived from executable source."))'
ga "$p"; lacks "objective O2" "an objective the file DOES name in a section was still reported"
# 63. grounded_by must name a domain row in this record whose grounding is required
# SPEC-0001 AUDIT_OBJECTIVE_GROUNDED_BY_RESOLVES_TO_A_REQUIRED_DOMAIN
rm -rf "$q"; cp -a "$p" "$q"
patch_record "$q" 'by("inventory", "O2").pop("grounded_by", None)'
ga "$q"
has "UNGROUNDED   objective O2" "an objective naming no grounded_by passed"
has "names no .grounded_by." "the missing-grounded_by finding did not say what was missing"
patch_record "$q" 'by("inventory", "O2")["grounded_by"] = ["no-such-domain"]'
ga "$q"; has "no domain row in this record" "grounded_by naming a slug the record does not carry passed"
patch_record "$q" 'by("inventory", "kg")["grounding"]["required"] = False
by("inventory", "O2")["grounded_by"] = ["kg"]'
ga "$q"; has "whose grounding is not required" "grounded_by resting on an ungrounded domain passed"
}

# --- 64. the objective kind goes green, and answers no staffing question ---
# SPEC-0001 AUDIT_OBJECTIVE_IS_NOT_STAFFED
scn_x64() {
local p="$TMP/x64"
fixture absent "$p"
patch_record "$p" "ob = 'O1'
$KG_DOMAIN"
unfill "$p"
patch_record "$p" 'cover("best-practices/", "docs/graph/best-practices/kg.md")
cover("sources/", "docs/graph/sources/normalized/kg.md")
cover("plans/", "docs/graph/plans/objectives.md")'
ga "$p"; rc_is 0 "a plant with a grounded domain and an objective resting on it could not go green"
lacks "UNSTAFFED    objective" "an objective was asked the staffing question its grounded_by domain answers"
has "coverage complete" "the objective plant did not summarise as complete"
}

# --- 65. a row's plan must cover what its kind owes (ADR-0003 residual B) ---
# SPEC-0001 AUDIT_ROW_PLAN_COVERS_WHAT_ITS_KIND_OWES
scn_x65() {
local p="$TMP/x65"
fixture planned "$p"
patch_record "$p" 'write("nodes/domain.kg.md", "# kg\n\n" + ("The routing node for the kg domain. " * 14))
r["inventory"] = [{"kind": "domain", "name": "kg", "slug": "kg", "significance": "core",
                   "status": "COVERED", "evidence": ["docs/graph/index.md:1"],
                   "expect": [{"path": "nodes/domain.kg.md"}],
                   "grounding": {"required": False, "sources": []},
                   "expert": {"warranted": False, "why": "the librarian holds it"}}]'
ga "$p"; rc_is 1 "a row whose plan predates its kind's obligations passed the gate"
has "BLANK        domain kg" "a domain row whose plan omits a path its kind owes was not caught"
has "its plan is missing best-practices/kg.md, which its kind owes" "the stale-plan finding did not name the owed path the plan omits"
plan "$p"
check_record "$p" 'paths = [e["path"] for e in r["inventory"][0]["expect"]]
assert "best-practices/kg.md" in paths, ("--plan did not union the owed path", paths)' || exit 1
ga "$p"; lacks "its plan is missing" "the stale-plan finding survived a --plan that unioned the owed path"
}

# --- 68. an agent's declared collections are answered severally, not jointly ---
scn_x68() {
local p="$TMP/x68" pick agent filled empty
fixture planned "$p"
# the first seed agent declaring two collections; this fixture fills one
pick="$(patch_record "$p" 'import importlib.util
spec = importlib.util.spec_from_file_location("ga", seed/"tools/growth-audit.py")
ga = importlib.util.module_from_spec(spec); spec.loader.exec_module(ga)
name, cols = next((n, [e for e in rd if e.endswith("/")])
                  for n, rd in sorted(ga.required_agents(seed).items())
                  if len([e for e in rd if e.endswith("/")]) >= 2)
write(cols[0] + "authored.md", "# authored\n\n" + ("A fact this project wrote down itself. " * 14))
by("agents", name).update(status="COVERED", evidence=[f"docs/graph/{cols[0]}authored.md"])
print(name); print(cols[0]); print(cols[1])')"
agent="$(sed -n 1p <<<"$pick")"; filled="$(sed -n 2p <<<"$pick")"; empty="$(sed -n 3p <<<"$pick")"
ga "$p" --agents; has "CONTRADICTED agent $agent" "a row claiming COVERED over an empty declared collection was accepted"
# absent_by <python dict expr over the agent's reads `rd`>
absent_by() { patch_record "$p" 'a = by("agents", sys.argv[3]); rd = a["reads"]; F, E = sys.argv[4], sys.argv[5]
a["absent"] = eval(sys.argv[6])' "$agent" "$filled" "$empty" "$1"; ga "$p" --agents; }
absent_by '{e: {"reason": "this project has no such subject", "searched": ["src/"]} for e in rd if e != F}'
lacks "agent $agent" "a row that established its inapplicable collections still could not close"
# it closes a row, so it is not a way past one: each guard, one at a time
absent_by '{E: {"searched": ["src/"]}}'
has "absent by design with no reason" "an absence by design with no reason was accepted"
absent_by '{E: {"reason": "no such subject"}}'
has "absent by design with a reason but no searched paths" "an absence by design naming nowhere it looked was accepted"
absent_by '{F: {"reason": "no such subject", "searched": ["src/"]}}'
has "is one it wrote in" "a collection this plant wrote in was allowed to be absent by design"
absent_by '{"nowhere/": {"reason": "no such subject", "searched": ["src/"]}}'
has "does not declare it reads it" "an absence was accepted for a collection the agent never declared"
absent_by '{e: {"reason": "no such subject", "searched": ["src/"]} for e in rd}'
has "no declaration is left for the coverage to be about" "a row absented every collection it declares and still claimed coverage"
}

scn_x382() {
# X382 SESSION_RECORD_FORM_IS_NOT_A_SCAFFOLD
# Asserts SPEC-0005 SESSION_RECORD_FORM_IS_NOT_A_SCAFFOLD: the placed
# session-record form is a form (excluded by name), so an ABSENT plans/ row
# passes; an untouched seed scaffold without such a name is still named.
local d="$TMP/x382" form="docs/graph/plans/sessions/_session-record.template.md"
fixture absent "$d"
unfill "$d"
cmp -s "$d/$form" "$ROOT/templates/docs/plans/sessions/_session-record.template.md" \
    || fail "X382: the installed plant does not hold the seed's session-record form at $form"
[ -f "$d/docs/graph/plans/grill.unfilled.md" ] && [ ! -e "$d/docs/graph/plans/grill.md" ] \
    || fail "X382: the grill.md scaffold was not renamed to grill.unfilled.md"
mv "$d/docs/graph/runbooks/rollback.unfilled.md" "$d/docs/graph/runbooks/rollback.md" \
    || fail "X382: runbooks/rollback.md was not renamed, so it cannot be put back"
ga "$d"
has "CONTRADICTED collection runbooks/rollback.md" "X382: an untouched rollback.md scaffold in an ABSENT row was not named"
has "still carries the seed's unfilled scaffold (rollback.md)" "X382: an untouched rollback.md scaffold in an ABSENT row was not named"
lacks "_session-record.template.md" "X382: the session-record form was read as an unfilled scaffold of the ABSENT plans/ row"
lacks "collection plans/" "X382: the session-record form was read as an unfilled scaffold of the ABSENT plans/ row"
}

# $1 = file, $2 = a word the leaf is about. A leaf that states a fact.
walk_leaf() {
  mkdir -p "$(dirname "$1")"
  { printf '# %s\n\n' "$2"
    for i in 1 2 3 4 5 6 7 8; do
      printf 'The %s service keeps its ledger in a write-ahead log with nightly compaction.\n' "$2"
    done; } > "$1"
}

# --- walk (three scenarios folded): the walk stays inside THIS plant ---
# A directory holding its own .cypress/seed.json is another plant and a
# symlinked directory another tree; an ordinary subdirectory is still walked.
scn_walk() {
local d="$TMP/walk" o="$TMP/walk-outside"
fixture renamed "$d"
ga "$d"; rc_is 0 "fixture: the all-ABSENT plant does not audit clean before the scenario"
# (a) a nested plant copy
mkdir -p "$d/docs/graph/architecture/plant-copy/.cypress"
cp "$d/.cypress/seed.json" "$d/docs/graph/architecture/plant-copy/.cypress/seed.json"
walk_leaf "$d/docs/graph/architecture/plant-copy/docs/graph/architecture/nestedleaf.md" nestedleaf
# (b) a symlinked directory inside a collection, and a collection that is a symlink
mkdir -p "$o"
walk_leaf "$o/linked/linkedleaf.md" linkedleaf
ln -s "$o/linked" "$d/docs/graph/design/linked"
mv "$d/docs/graph/product" "$o/product"
walk_leaf "$o/product/prodleaf.md" prodleaf
ln -s "$o/product" "$d/docs/graph/product"
ga "$d"
lacks 'nestedleaf\|plant-copy' "a directory holding its own .cypress/seed.json was walked as part of the plant"
lacks "collection architecture/" "a directory holding its own .cypress/seed.json was walked as part of the plant"
lacks 'linkedleaf\|collection design/' "a symlinked directory inside a collection was walked"
lacks 'prodleaf\|collection product/' "a collection directory that is a symlink was walked"
rc_is 0 "a plant whose only extra leaves are in a nested plant or behind symlinks must audit clean"
# (c) guard: an ordinary subdirectory is still walked
walk_leaf "$d/docs/graph/data/sub/plainleaf.md" plainleaf
ga "$d"
has "CONTRADICTED collection data/" "an authored leaf in an ordinary subdirectory of an ABSENT collection was not found"
has "plainleaf.md" "an authored leaf in an ordinary subdirectory of an ABSENT collection was not found"
}

# --- the model map is disclosed, not required (S4, ADR-0022) ---
# A grown plant whose record predates the map: no models.md row, and the map
# still the seed's template. Passing is the plant's configuration choice.
scn_model_map_disclosed() {
local p="$TMP/mapd"
fixture renamed "$p"
ga "$p"; rc_is 0 "setup: the renamed all-ABSENT plant no longer passes, so this case asserts nothing"
rm -f "$p/docs/graph/models.unfilled.md"
cp "$ROOT/templates/docs/models.md" "$p/docs/graph/models.md"
patch_record "$p" 'r["collections"] = [c for c in r["collections"] if c["name"] != "models.md"]'
ga "$p"; rc_is 0 "a grown plant with the template model map and no models.md row failed the gate"
grep -i 'docs/graph/models.md' <<<"$out" | grep -qi 'unfilled' \
  || { printf '%s\n' "$out" >&2; fail "the audit did not name docs/graph/models.md as unfilled"; }
echo "  an unfilled model map is disclosed, not required — OK"
}

# --- 70-71: what the citation reader holds, pinned before it moves (SPEC-0007 §6 "Helper") ---
# CHARACTERIZATION: the citation grammar and cite_problem move into
# tools/source_paths.py; these two readings had no case of their own.
scn_x70() {
# 70. a citation that leaves the plant through a symlink is not inside the plant
local o="$TMP/x70-outside"
mkdir -p "$o"; printf '# elsewhere\n\nA file that sits outside the plant.\n' > "$o/elsewhere.md"
absent_gfm "$TMP/x70" 'it["evidence"] = ["docs/graph/escape/elsewhere.md"]'
ln -s "$o" "$TMP/x70/docs/graph/escape"
ga "$TMP/x70"; rc_is 1 "a citation that leaves the plant through a symlink passed the gate"
has "DANGLING" "a citation resolving outside the plant through a symlink was not DANGLING"
has "'docs/graph/escape/elsewhere.md' does not exist in the plant" "the escaping citation was not named as outside the plant"
# 71. the `:line:col` and `:line-line` suffixes are line citations, checked on their line
absent_gfm "$TMP/x71" 'it["evidence"] = ["docs/graph/index.md:1:5", "docs/graph/index.md:1-2"]'
ga "$TMP/x71"; lacks "DANGLING" "an in-range :line:col or :line-line citation stopped resolving"
patch_record "$TMP/x71" 'r["inventory"][0]["evidence"] = ["docs/graph/index.md:999999:1", "docs/graph/index.md:999998-999999"]'
ga "$TMP/x71"; rc_is 1 "a :line:col or :line-line citation past the end of the file passed the gate"
has "names line 999999 of a file" "a :line:col citation past the end was not checked on its line"
has "names line 999998 of a file" "a :line-line citation past the end was not checked on its first line"
}

# --- 69: grounding the upstream cannot give is declared, and audited as declared ---
# REGRESSION: a row closed UNKNOWN because no public source exists still got
# UNGROUNDED, so the coverage gate blocked on a blocker it had already carried.
scn_x69() {
local p="$TMP/x69"
fixture renamed "$p"
patch_record "$p" 'by("collections", "changelog.md").update(status="COVERED",
    reason="the delivery log this growth pass wrote", searched=["src/"], evidence=[], leaves=1)
r["inventory"] = [{"kind": "domain", "name": "vendor wire protocol",
    "slug": "vendor-wire-protocol", "status": "UNKNOWN",
    "blocker": "no public source exists; the owner holds the only copy",
    "evidence": ["docs/graph/index.md"], "expect": [],
    "grounding": {"required": True, "sources": [],
                  "unavailable": "no public specification exists; the owner holds the only copy"}}]'
cat >> "$p/docs/graph/changelog.md" <<'MD'

## 2026-10-04 — growth

- vendor wire protocol — UNKNOWN: no public source exists for it, so no scout
  can retrieve upstream documentation. The owner holds the only copy and
  decides whether it may be normalized into the graph; until then the domain
  row stays open, and this entry is where the owner reads that it waits on them.
- Every other collection closed ABSENT, with the paths searched recorded in
  the coverage record. This entry is the plant's own account of the pass.
MD
ga "$p"; rc_is 0 "a declared-unavailable grounding on a disclosed UNKNOWN row blocked the gate"
lacks "UNGROUNDED" "a row that declared its grounding unavailable was still UNGROUNDED"
has "grounding declared unavailable: no public specification exists" "the declared reason was not reported"
# an empty declaration declares nothing
patch_record "$p" 'r["inventory"][0]["grounding"]["unavailable"] = "  "'
ga "$p"; rc_is 1 "an empty grounding.unavailable stood in for a reason"
has "UNGROUNDED   domain vendor wire protocol" "an empty declaration was not UNGROUNDED"
# a declaration on a row that is not UNKNOWN is still put to the owner
absent_gfm "$TMP/x69b" 'it["grounding"].update(required=True,
    unavailable="the upstream project took its documentation offline")'
ga "$TMP/x69b"; rc_is 1 "a declared-unavailable grounding the changelog never names passed the gate"
lacks "UNGROUNDED" "a declared-unavailable ABSENT row was still UNGROUNDED"
has "SILENT       framework gfm" "a declared-unavailable grounding was accepted without being disclosed"
}

# --- X468: the source-index build report after the verdicts (SPEC-0007, 8.1.2) ---
# SPEC-0007 GROWTH_AUDIT_PRINTS_THE_BUILD_REPORT SOURCE_INDEX_REPORT_UNAVAILABLE
# The lint runs the seed's tools/source-index.py build from the plant root and
# prints its lines as advice: never a verdict, never the exit code. A build that
# does not answer is one GROWTH_REPORT_FAILED line, nothing of what it wrote.
scn_x468() {
local p="$TMP/x468" c="$TMP/x468-seed"
fixture renamed "$p"
git -C "$p" init -q
git -C "$p" add -A
git -C "$p" -c user.name=t -c user.email=t@example.invalid commit -qm plant
mkdir -p "$c"
tar -C "$ROOT" --exclude=./.git --exclude=__pycache__ --exclude=./.seed-worktrees -cf - . | tar -C "$c" -xf -
python3 - "$p" "$ROOT" "$c" <<'PY' || fail "GROWTH_AUDIT_PRINTS_THE_BUILD_REPORT: the case named above failed"
import json, shutil, subprocess, sys
from pathlib import Path
plant, seed, copy = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
HEAD = 'source index (advice, not a verdict; SPEC-0007 "Build report"):'
FAILED = ("source index: the build did not answer ({why}); run python3 docs/graph/source-index.py build "
          "from the plant root")
NODE = plant / "docs/graph/nodes/subsystem.oldlib.md"
problems = []

def audit(*flags, seed_root=seed):
    r = subprocess.run([sys.executable, str(seed_root / "tools/growth-audit.py"), str(plant), str(seed_root),
                        *flags], capture_output=True, timeout=600)
    return r.returncode, r.stdout, r.stderr

def lines(raw):
    return raw.decode("utf-8", "replace").split("\n")

def report_of(doc):
    """`source_index_report` of the --json document: a key of the document, or
    of the one list item that carries it (§6 names the key, not its place)."""
    if isinstance(doc, dict):
        return doc.get("source_index_report")
    found = [x["source_index_report"] for x in doc if isinstance(x, dict) and "source_index_report" in x]
    return found[0] if len(found) == 1 else None

rc_clean, _, _ = audit()
NODE.write_text("---\nid: subsystem.oldlib\ntier: 2\nkind: subsystem\ntitle: an old library\n"
                "owns: [subsystem.oldlib.core]\nrequires: []\nrepo: old/lib\nload_when: [\"old library\"]\n"
                "est_tokens: 100\n---\n# old library\n")
rc, out, err = audit()
ls = lines(out)
if rc != rc_clean:
    problems.append(f"the report changed the exit code: {rc}, the same run without the node {rc_clean}")
if HEAD not in ls:
    problems.append(f"the lint prints no {HEAD!r} line")
else:
    after = ls[ls.index(HEAD) + 1:]
    rec = [l for l in after if l.startswith("  ") and "repo-unresolved: docs/graph/nodes/subsystem.oldlib.md" in l]
    if not rec:
        problems.append(f"no indented repo-unresolved line follows the head: {after[:12]!r}")
rc, out, _ = audit("--json")
try:
    rep = report_of(json.loads(out))
    if not (isinstance(rep, list) and all(isinstance(x, str) for x in rep)
            and any("repo-unresolved: docs/graph/nodes/subsystem.oldlib.md" in x for x in rep)):
        problems.append(f"--json source_index_report {rep!r} is not the report's lines with the record")
except ValueError:
    problems.append(f"--json printed no JSON document: {out[:300]!r}")
# SOURCE_INDEX_REPORT_UNAVAILABLE, A2: a seed whose tool writes control bytes and markers, then exits 3
(copy / "tools/source-index.py").write_text(
    "import sys\nsys.stdout.write('\\x1b[2J MARK-OUT\\n')\nsys.stderr.write('MARK-ERR \\x1b]0;x\\x07\\n')\n"
    "sys.exit(3)\n")
rc, out, err = audit(seed_root=copy)
both = out + err
if FAILED.format(why="exit 3") not in lines(out):
    problems.append(f"a build exiting 3 does not give {FAILED.format(why='exit 3')!r}")
if rc != rc_clean:
    problems.append(f"a failed build changed the exit code: {rc}, want {rc_clean}: {lines(out)[:8]!r}")
if b"MARK-OUT" in both or b"MARK-ERR" in both:
    problems.append("A2: the build's stdout or stderr was printed")
if b"\x1b" in both or b"\x07" in both:
    problems.append("A2: the lint's output holds a byte 0x1b or 0x07")
_, out, _ = audit("--json", seed_root=copy)
try:
    rep = report_of(json.loads(out))
    if rep != []:
        problems.append(f"after a failed build --json source_index_report is {rep!r}, not []")
except ValueError:
    problems.append(f"--json (failed build) printed no JSON document: {out[:300]!r}")
# last: --plan rewrites the record the runs above read
shutil.rmtree(plant / ".cypress/source-index", ignore_errors=True)
for flag in ("--plan", "--agents"):
    audit(flag)
    if (plant / ".cypress/source-index").exists():
        problems.append(f"{flag} ran a build (.cypress/source-index/ exists after it)")
if problems:
    print("FAIL: X468 GROWTH_AUDIT_PRINTS_THE_BUILD_REPORT; failure SOURCE_INDEX_REPORT_UNAVAILABLE: "
          + " || ".join(problems), file=sys.stderr)
    sys.exit(1)
PY
echo "  the build report follows the verdicts as advice; a failed build is one line — OK"
}

# --- dispatch: `__case scn_<name>` runs ONE scenario; bases come from the parent ---
if [ -z "${GA_BASES:-}" ]; then
  export GA_BASES="$TMP/bases"
  build_bases || fail "could not build the fixture bases"
fi
if [ "${1:-}" = "__case" ]; then
  "$2"
  exit $?
fi

# --- main: one scenario per line, run under the gate pool ---
SCN="$TMP/scenarios"
for s in scn_shared scn_s9 scn_absent scn_staff scn_nostaff scn_dflt scn_rows \
         scn_copy scn_x28 scn_x31 scn_x32 scn_x33 scn_x34 scn_x35 scn_x38 \
         scn_x39 scn_x40 scn_x41 scn_x42 scn_x43 scn_x44 scn_x45 scn_rawbase \
         scn_x58 scn_x61 scn_x62x63 scn_x64 scn_x65 scn_x68 scn_x382 scn_walk \
         scn_model_map_disclosed scn_x69 scn_x70 scn_x468; do
  printf '%s\t%s\n' "$s" "bash \"$SELF\" __case $s" >> "$SCN"
done
rc=0
python3 "$ROOT/tests/gate_pool.py" run "$SCN" || rc=$?
[ "$rc" -eq 0 ] || { echo "test-growth-audit: FAIL" >&2; exit "$rc"; }
printf 'growth coverage gate: PASS\n'
