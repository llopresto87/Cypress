#!/usr/bin/env bash
# seed-lint contract: the meta-fact linter must FAIL (exit 1, named message)
# on each violation class it claims to guard — not merely pass on good input.
# Mirrors test-spec-lint.sh's plant-a-violation discipline. Without this, a
# logically-inert check would still print PASS and nothing would notice.
#
# Every seed-lint check earns a planted violation here: the command-roster
# guard, the machinery graph-edge validation (resolve + acyclic), the
# miscounted-prose scan, the version single-source check, the corpus
# agnosticism/durability scan (once per shipped corpus root) and its
# dangling-reference arm, the harness-registration home + referrer pair, the
# opencode config contract, and the est_tokens-vs-file budget (whole file,
# frontmatter included, since 2026-09-17) — plus the
#
# PARALLEL: each check runs against its OWN cheap copy of one shared hermetic
# template, so the checks cannot collide and are dispatched concurrently through
# the gate's shared budget (tests/gate_pool.py, $GATE_JOBS / $GATE_POOL_DIR).
# ~60 serial full-tree lints were the floor here; now they run under one clamped
# pool. Every planted violation is byte-for-byte what it was — a fresh copy plus
# a template-sourced restore() is the only structural change, so the gate still
# FAILS on each violation class exactly as before.
set -euo pipefail

ROOT="${ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
SELF="$ROOT/tests/test-seed-lint.sh"

# A fresh, disposable copy of the shared template. seed-lint resolves ROOT from
# its own location, so running $TMP/tests/seed-lint.py lints the copy.
fresh() {
  local d; d="$(mktemp -d)"
  ( cd "$SEEDLINT_TMPL" && tar -cf - . ) | ( cd "$d" && tar -xf - )
  printf '%s' "$d"
}
lint() { python3 "$TMP/tests/seed-lint.py" 2>&1; }
# The copy is disposable, so a restore just re-lays the pristine file from the
# template — same semantics as the old `cp "$ROOT/$1"`, needed by the few checks
# that plant, assert, restore and then assert the file is clean again.
restore() { cp "$SEEDLINT_TMPL/$1" "$TMP/$1"; }

expect_fail() {  # $1=grep-pattern  $2=label
  local out rc
  out="$(lint)" && rc=0 || rc=$?
  [[ $rc -eq 1 ]] || { echo "[$2] expected exit 1, got $rc" >&2; echo "$out" >&2; exit 1; }
  grep -q "$1" <<<"$out" || { echo "[$2] missing expected message: /$1/" >&2; echo "$out" >&2; exit 1; }
}

# --- each check, self-contained on its own fresh copy ------------------------
case_01() {
  local TMP; TMP="$(fresh)"
# 1. A user-sovereign protocol must not declare `command: true`.
python3 - "$TMP/protocols/graft.md" <<'PY'
import re,sys; p=sys.argv[1]; t=open(p).read()
open(p,'w').write(re.sub(r'(?m)^(est_tokens:[^\n]*\n)', r'\1command: true\n', t, count=1))
PY
expect_fail "must not declare 'command: true'" "sovereign-command"
restore protocols/graft.md
  rm -rf "$TMP"
}
case_02() {
  local TMP; TMP="$(fresh)"
# 2. `command:` is a protocol-only field.
python3 - "$TMP/skills/context-router/SKILL.md" <<'PY'
import re,sys; p=sys.argv[1]; t=open(p).read()
open(p,'w').write(re.sub(r'(?m)^(est_tokens:[^\n]*\n)', r'\1command: true\n', t, count=1))
PY
expect_fail "protocol-only field" "command-on-skill"
restore skills/context-router/SKILL.md
  rm -rf "$TMP"
}
case_03() {
  local TMP; TMP="$(fresh)"
# 3. A requires:/peers: edge to a nonexistent node fails to resolve.
python3 - "$TMP/protocols/verify.md" <<'PY'
import re,sys; p=sys.argv[1]; t=open(p).read()
open(p,'w').write(re.sub(r'(?m)^requires:\s*$', 'requires:\n  - protocol.does-not-exist', t, count=1))
PY
expect_fail "unknown machinery node" "dangling-edge"
restore protocols/verify.md
  rm -rf "$TMP"
}
case_04() {
  local TMP; TMP="$(fresh)"
# 4. A cycle in the requires: relation is rejected.
python3 - <<PY
import re
for f,tgt in [("$TMP/protocols/specify.md","protocol.grill"),
              ("$TMP/protocols/grill.md","protocol.specify")]:
    t=open(f).read()
    open(f,'w').write(re.sub(r'(?m)^requires:\s*$', f'requires:\n  - {tgt}', t, count=1))
PY
expect_fail "requires cycle" "requires-cycle"
restore protocols/specify.md
restore protocols/grill.md
  rm -rf "$TMP"
}
case_05() {
  local TMP; TMP="$(fresh)"
# 5. A miscounted skills claim in shipped prose is caught.
printf '\n\nThe seed ships 99 skills.\n' >> "$TMP/README.md"
expect_fail "claims 99 skills" "skills-count"
restore README.md
  rm -rf "$TMP"
}
case_06() {
  local TMP; TMP="$(fresh)"
# 5b. REGRESSION — the qualified "N named specialist agents" phrasing is
# policed too: DOCUMENTATION.md shipped a release saying "17 named
# specialist agents" while the roster had 18, and the first version of
# this scan only matched the bare "N specialist agents" form.
printf '\n\nA team of 99 named specialist agents.\n' >> "$TMP/DOCUMENTATION.md"
expect_fail "99 named specialist agents" "qualified-agent-count"
restore DOCUMENTATION.md
  rm -rf "$TMP"
}
case_07() {
  local TMP; TMP="$(fresh)"
# 5c. REGRESSION — the documentation tree's version pin must match the
# manifest: DOCUMENTATION.md/documentation/README.md sat at 6.8.0 for a
# whole release because no gate read them.
python3 - "$TMP/documentation/README.md" <<'PY'
import sys; p=sys.argv[1]; t=open(p).read()
import re; open(p,"w").write(re.sub(r"\(version \d+\.\d+\.\d+\)", "(version 0.0.1)", t, count=1))
PY
expect_fail "documents version 0.0.1" "doc-tree-version-pin"
restore documentation/README.md
  rm -rf "$TMP"
}
case_08() {
  local TMP; TMP="$(fresh)"
# 5d. The spawn-trace contract: a brief that drops the spawn_id field breaks
# the delegation correlation chain and must fail the lint.
python3 - "$TMP/templates/prompts/investigation-brief.md" <<'PY'
import sys; p=sys.argv[1]; t=open(p).read()
assert "spawn_id" in t
open(p,'w').write(t.replace("spawn_id", "spawnid"))
PY
expect_fail "no spawn_id field" "spawn-trace-contract"
restore templates/prompts/investigation-brief.md
  rm -rf "$TMP"
}
case_09() {
  local TMP; TMP="$(fresh)"
# 6. manifest version and the top CHANGELOG entry must agree.
python3 - "$TMP/manifest.json" <<'PY'
import re,sys; p=sys.argv[1]; t=open(p).read()
open(p,'w').write(re.sub(r'("version":\s*")\d+\.\d+\.\d+(")', r'\g<1>0.0.0\g<2>', t, count=1))
PY
expect_fail "version drift" "version-single-source"
restore manifest.json
  rm -rf "$TMP"
}
case_10() {
  local TMP; TMP="$(fresh)"
# 7. Control: the long-standing kernel-budget guard still bites.
python3 -c "open('$TMP/core/AGENTS.md','a').write('\n<!-- '+'x'*9000+' -->\n')"
expect_fail "exceeds the" "kernel-budget"
restore core/AGENTS.md
  rm -rf "$TMP"
}
case_11() {
  local TMP; TMP="$(fresh)"
# 8. The agnosticism/durability scan reaches EVERY shipped corpus, not just the
# ones it happened to be written for. A corpus added later that nobody adds to
# `agn_roots` is scanned by nothing, and its first leak ships silently — so each
# corpus root is pinned here by planting a violation inside it.
for corpus_probe in \
  "library-corpus/nuget/Npgsql.md" \
  "legal-corpus/eu/gdpr.md" \
  "tool-corpus/testing/http-smoke-suite.md" \
  "agent-corpus/env-contract-manager.md" \
  "skill-corpus/harden-docker-host.md"
do
  [[ -f "$TMP/$corpus_probe" ]] || { echo "[corpus-scan] probe file missing: $corpus_probe" >&2; exit 1; }
  python3 -c "open('$TMP/$corpus_probe','a').write('\nleaked host 198.18.7.42 and advisory CVE-2031-99999\n')"
  expect_fail "leaked host-IP literal" "corpus-scan-ip:${corpus_probe%%/*}"
  expect_fail "pinned advisory" "corpus-scan-cve:${corpus_probe%%/*}"
  restore "$corpus_probe"
done
  rm -rf "$TMP"
}
case_12() {
  local TMP; TMP="$(fresh)"
# 9. A dangling cross-reference into any corpus is caught (the withdraw
# contracts are prose pointers; a stale one silently sends a reader nowhere).
python3 -c "open('$TMP/protocols/harvest.md','a').write('\nSee \`legal-corpus/eu/does-not-exist.md\`.\n')"
expect_fail "dangling corpus/template reference" "dangling-corpus-ref"
restore protocols/harvest.md
  rm -rf "$TMP"
}
case_13() {
  local TMP; TMP="$(fresh)"
# 10. The "installed but not spawnable" rule keeps its single home. Moving or
# dropping it from method.delegation would leave every dispatch/install surface
# pointing at a fact nothing owns.
python3 - "$TMP/core/method/delegation.md" <<'PY'
import sys; p=sys.argv[1]; t=open(p).read()
open(p,'w').write(t.replace("  - delegation.harness-registration\n", "", 1))
PY
expect_fail "does not own 'delegation.harness-registration'" "registration-home"
restore core/method/delegation.md
  rm -rf "$TMP"
}
case_14() {
  local TMP; TMP="$(fresh)"
# 11. A dispatch/install surface that drops the pointer is caught. This is the
# rot mode the fix exists to prevent: the rule stays written in one place while
# the surface that needed it quietly stops mentioning it.
python3 - "$TMP/protocols/grow.md" <<'PY'
import sys; p=sys.argv[1]; t=open(p).read()
open(p,'w').write(t.replace("delegation.harness-registration", "<dropped>"))
PY
expect_fail "never points at 'delegation.harness-registration'" "registration-referrer"
restore protocols/grow.md
  rm -rf "$TMP"
}
case_15() {
  local TMP; TMP="$(fresh)"
# 12. The opencode config contract: a stale $schema URL, a key the upstream
# schema does not accept (additionalProperties:false makes it fatal, not
# cosmetic), a re-declared AGENTS.md (double-loads the kernel), and a
# subagent_depth that silently caps the seed's delegation chain.
oc="integrations/opencode/opencode.json"
write_oc() { python3 - "$TMP/$oc" "$1" <<'PY'
import json,sys; json.dump(json.loads(sys.argv[2]), open(sys.argv[1],'w'), indent=2)
PY
}
write_oc '{"$schema":"https://opencode.ai/config-schema.json","subagent_depth":3}'
expect_fail 'schema must be' "opencode-stale-schema"
write_oc '{"$schema":"https://opencode.ai/config.json","subagent_depth":3,"agents":{"directory":".opencode/agents"}}'
expect_fail "additionalProperties:false" "opencode-invalid-key"
write_oc '{"$schema":"https://opencode.ai/config.json","subagent_depth":3,"instructions":["AGENTS.md"]}'
expect_fail "kernel would load twice" "opencode-double-load"
write_oc '{"$schema":"https://opencode.ai/config.json","subagent_depth":1}'
expect_fail "delegation topology would be capped" "opencode-depth-cap"
restore "$oc"
  rm -rf "$TMP"
}
case_16() {
  local TMP; TMP="$(fresh)"
# 13. A machinery node whose est_tokens is more than 2x off its measured file
# — frontmatter included, the metric graph-lint.py's check_budget uses — would
# be REJECTED by the graph-lint.py the seed itself ships, once installed into a
# plant. The seed never checked its own nodes against that rule, and until
# 2026-09-17 it mirrored the rule against the body alone, which was weaker than
# the thing it mirrored.
python3 - "$TMP/protocols/verify.md" <<'PY'
import re,sys; p=sys.argv[1]; t=open(p).read()
open(p,'w').write(re.sub(r'(?m)^est_tokens:\s*\d+', 'est_tokens: 20', t, count=1))
PY
expect_fail "graph-lint.py would reject this node" "est-tokens-2x"
restore protocols/verify.md
  rm -rf "$TMP"
}
case_17() {
  local TMP; TMP="$(fresh)"
# 14. The body ceiling, the eager-context budget and the spec test-mapping
# check are new in 7.16.0 and had no planted violation here, which contradicts
# this file's own contract ("Every seed-lint check earns a planted violation").
# A check nobody has seen fail is a constant with a function signature.
# est_tokens is bumped with the padding on purpose: without it the est_tokens
# 2x check fires too, and the case would pass for the wrong reason — proving
# only that SOMETHING complained, not that the ceiling did.
python3 -c "
import re, sys
p = sys.argv[1]
t = open(p).read()
t = re.sub(r'(?m)^est_tokens:\s*\d+', 'est_tokens: 9000', t, count=1)
open(p,'w').write(t + chr(10) + chr(10).join('padding line %d' % i for i in range(1200)))
" "$TMP/protocols/verify.md"
expect_fail "machinery ceiling" "body-ceiling"
# exercises: check_body_ceiling
restore protocols/verify.md
  rm -rf "$TMP"
}
case_18() {
  local TMP; TMP="$(fresh)"
# ...and the FRONTMATTER half of the same ceiling. A node is loaded whole, so
# metadata is context: 2 000 frontmatter lines with the body untouched passed
# every one of the 42 gates.
python3 -c "
import pathlib, sys
p = pathlib.Path(sys.argv[1]); t = p.read_text()
i = t.index(chr(10) + '---' + chr(10), 3)
p.write_text(t[:i] + chr(10) + chr(10).join('pad_%d: x' % n for n in range(2000)) + t[i:])
" "$TMP/protocols/canonize.md"
expect_fail "frontmatter is .* lines, over the" "frontmatter-ceiling"
# exercises: check_body_ceiling
restore protocols/canonize.md
  rm -rf "$TMP"
}
case_19() {
  local TMP; TMP="$(fresh)"
# The CI the README says runs this gate: deleting the workflow used to leave
# every one of the 43 steps green.
rm -f "$TMP/.github/workflows/gate.yml"
expect_fail "workflows/gate.yml is missing" "ci-workflow"
# exercises: check_ci_workflow
mkdir -p "$TMP/.github/workflows" && restore .github/workflows/gate.yml
  rm -rf "$TMP"
}
case_20() {
  local TMP; TMP="$(fresh)"
# A published always-loaded figure that drifts from what check_eager_surface
# computes. These moved four times in one release, and the page that prints them
# claimed the gate held them against the computation while nothing did.
python3 -c "
import pathlib, re, sys
p = pathlib.Path(sys.argv[1]); t = p.read_text()
m = re.search(r'(\d{2} \d{3}) B', t)
p.write_text(t.replace(m.group(1), '99 111', 1))
" "$TMP/documentation/host-capability-matrix.md"
expect_fail "always-loaded surface" "published-eager-figure"
# exercises: check_published_eager_figures
restore documentation/host-capability-matrix.md
  rm -rf "$TMP"
}
case_21() {
  local TMP; TMP="$(fresh)"
# A body-size claim in README that the measurement no longer supports. U-15 was
# exactly this — `<500` against a 931-line body — and its fix printed four fresh
# numbers that nothing derived.
python3 -c "
import pathlib, sys
p = pathlib.Path(sys.argv[1])
p.write_text(p.read_text() + chr(10) + chr(10).join('pad %d' % i for i in range(80)))
" "$TMP/protocols/graft.md"
expect_fail "largest routable body" "published-body-figure"
# exercises: check_published_body_figures
restore protocols/graft.md
restore protocols/verify.md
  rm -rf "$TMP"
}
case_22() {
  local TMP; TMP="$(fresh)"
python3 -c "
import re, sys
p = sys.argv[1]
t = open(p).read()
open(p,'w').write(re.sub(r'(?m)^(description:.*)\$', lambda m: m.group(1) + ' padding'*6000, t, count=1))
" "$TMP/agents/01-architect.md"
expect_fail "eager surface" "eager-budget"
# exercises: check_eager_surface
restore agents/01-architect.md
  rm -rf "$TMP"
}
case_23() {
  local TMP; TMP="$(fresh)"
# A spec citing a test nobody wrote — the exact defect that shipped: SPEC-0002
# marked a contract `green` against a name that existed only in its own table.
if [ -d "$TMP/docs/specs" ]; then
  python3 -c "
import pathlib, sys
f = sorted(pathlib.Path(sys.argv[1]).glob('SPEC-*.md'))[0]
f.write_text(f.read_text() + chr(10) + '| C | test_this_name_was_never_written | tests/x.py | integration | green |' + chr(10))
" "$TMP/docs/specs"
  expect_fail "does not exist in tests/" "spec-cites-missing-test"
# exercises: check_spec_test_mapping
  # restore() is `cp` without -r, so name the file rather than the directory.
  restore docs/specs/SPEC-0001-install-placement.md
fi
  rm -rf "$TMP"
}
case_24() {
  local TMP; TMP="$(fresh)"
# The protocol reference restates owns/requires/peers/est_tokens for all fifteen
# protocols by hand. When check_protocol_reference() was written, THIRTEEN of the
# fifteen rows were stale — verify missing eight owned facts, and every
# est_tokens whatever someone last remembered. Both arms are planted here, in
# both directions, because a table check that only notices deletions is half a
# check: an invented fact reads as authoritative to whoever trusts the table.
python3 -c "
import pathlib, re, sys
f = pathlib.Path(sys.argv[1])
t = f.read_text()
t = re.sub(r'^(\| graft \|.*\| )(\d+)( \|)$', r'\g<1>9790\g<3>', t, count=1, flags=re.M)
f.write_text(t)
" "$TMP/documentation/protocols-reference.md"
expect_fail "est_tokens 9790, but protocol.graft declares" "protocol-reference-stale-tokens"
# exercises: check_protocol_reference
restore documentation/protocols-reference.md
  rm -rf "$TMP"
}
case_25() {
  local TMP; TMP="$(fresh)"
python3 -c "
import pathlib, sys
f = pathlib.Path(sys.argv[1])
f.write_text(f.read_text().replace('\`graft.reversibility\` |', '\`graft.reversibility\`, \`graft.invented\` |', 1))
" "$TMP/documentation/protocols-reference.md"
expect_fail "extra \['graft.invented'\]" "protocol-reference-invented-fact"
restore documentation/protocols-reference.md
  rm -rf "$TMP"
}
case_26() {
  local TMP; TMP="$(fresh)"
# check_gate_single_home() shipped with no negative test, and a review then
# found two holes in it: a named-but-missing node passed vacuously (a renamed
# graft.md made the whole check report nothing), and `hard` was still an
# accepted class after ADR-0003's Amendment established that no harness refuses
# a steward in these three protocols. Both arms are planted here, plus the two
# the check was actually written for.
python3 -c "
import pathlib, re, sys
f = pathlib.Path(sys.argv[1])
t = f.read_text()
# flip the first graft gate row's class to \`hard\`
t = re.sub(r'(\n\| \`graft\.gate\.[a-z-]+\`.*\| )(soft|detective|judgment)( \|)',
           r'\g<1>hard\g<3>', t, count=1)
f.write_text(t)
" "$TMP/protocols/graft.md"
expect_fail "declares class .hard" "gate-class-hard-rejected"
# exercises: check_gate_single_home
restore protocols/graft.md
  rm -rf "$TMP"
}
case_27() {
  local TMP; TMP="$(fresh)"
mv "$TMP/protocols/graft.md" "$TMP/protocols/graft-renamed.md"
expect_fail "named in LIFECYCLE_NODES but is not a file" "gate-lifecycle-node-missing"
mv "$TMP/protocols/graft-renamed.md" "$TMP/protocols/graft.md"
  rm -rf "$TMP"
}
case_28() {
  local TMP; TMP="$(fresh)"
python3 -c "
import pathlib, sys
f = pathlib.Path(sys.argv[1])
f.write_text(f.read_text() + chr(10) + 'See \`grow.gate.invented-here\` for details.' + chr(10))
" "$TMP/protocols/grow.md"
expect_fail "which no table row declares" "gate-dangling-reference"
restore protocols/grow.md
  rm -rf "$TMP"
}
case_29() {
  local TMP; TMP="$(fresh)"
# A `judgment` row with no judge. Fifteen of sixteen rows named one in prose
# before the marker existed and the sixteenth read as though it did, so the
# marker is the contract: checkable exactly, no phrase matching.
python3 -c "
import pathlib, sys
f = pathlib.Path(sys.argv[1])
t = f.read_text()
i = t.index('. Judge: ')
j = t.index(' ', t.index('|', i) - 1)
f.write_text(t[:i] + t[t.index('|', i):])
" "$TMP/protocols/grow.md"
expect_fail "names no judge" "gate-judgment-without-judge"
restore protocols/grow.md
  rm -rf "$TMP"
}
case_30() {
  local TMP; TMP="$(fresh)"
# The protocols-reference SECTION arm also had no fixture, which is how a
# duplicated `load_when:` bullet in three sections passed as clean.
python3 -c "
import pathlib, re, sys
f = pathlib.Path(sys.argv[1])
t = f.read_text()
m = re.search(r'^- \*\*load_when:\*\*.*?(?=^- |^$)', t, re.M | re.S)
f.write_text(t[:m.end()] + m.group(0) + t[m.end():])
" "$TMP/documentation/protocols-reference.md"
expect_fail "is stated 2 times" "protocol-reference-duplicate-field"
restore documentation/protocols-reference.md
  rm -rf "$TMP"
}
case_31() {
  local TMP; TMP="$(fresh)"
# 16. Checks that had no planted violation at all. Measured, not assumed: each
# check's call was replaced with `pass` in turn and this suite re-run, and nine
# of thirteen deletions went unnoticed — including check_install_write_sites,
# added the same day. A check nothing would miss is a check nobody is keeping.
python3 -c "
import pathlib, sys
p = pathlib.Path(sys.argv[1]); p.write_text(p.read_text().rstrip(chr(10)))
" "$TMP/protocols/grill.md"
expect_fail "does not end with a newline" "file-endings"
# exercises: check_file_endings
restore protocols/grill.md
  rm -rf "$TMP"
}
case_32() {
  local TMP; TMP="$(fresh)"
python3 -c "
import pathlib, sys
p = pathlib.Path(sys.argv[1])
p.write_text(p.read_text().replace('GRAPH DISCIPLINE', 'GRAPH DISCIPLINEX', 1))
" "$TMP/templates/prompts/investigation-brief.md"
expect_fail "has drifted from the canonical copy" "canonical-block-drift"
# exercises: check_canonical_router_blocks
restore templates/prompts/investigation-brief.md
  rm -rf "$TMP"
}
case_33() {
  local TMP; TMP="$(fresh)"
# One of the three upward walkers loses the plant-root boundary. Byte-identity
# is the only thing holding them together, so dropping it from one file must be
# the loudest possible failure: without it that walker reads an ancestor
# checkout's roster, which agent-lint did at HIGH confidence over a repository
# the plant does not own.
python3 -c "
import pathlib, re, sys
p = pathlib.Path(sys.argv[1])
t = re.sub(r'# --- canonical plant-root boundary ---.*?'
           r'# --- end canonical plant-root boundary ---\n', '',
           p.read_text(), flags=re.S)
p.write_text(t)
" "$TMP/integrations/claude-code/status-hook.py"
expect_fail "plant-root boundary" "plant-root-boundary-drift"
# exercises: check_canonical_plant_root_boundary
restore integrations/claude-code/status-hook.py
  rm -rf "$TMP"
}
case_34() {
  local TMP; TMP="$(fresh)"
# Two nodes claiming the SAME failure. The review brief asked five rounds running
# for a pairwise prevents: sweep 'reported with scores' because nothing did it;
# agent.implementer's line collided three times and returned to its origin.
python3 -c "
import pathlib, re, sys
root = pathlib.Path(sys.argv[1])
src = (root / 'agents/02-implementer.md').read_text()
prev = re.search(r'^prevents:.*\$', src, re.M).group(0)
p = root / 'agents/03-reviewer.md'
p.write_text(re.sub(r'^prevents:.*\$', prev, p.read_text(), count=1, flags=re.M))
" "$TMP"
expect_fail "claim the same failure" "prevents-collision"
# exercises: check_prevents_are_distinct
restore agents/03-reviewer.md
  rm -rf "$TMP"
}
case_35() {
  local TMP; TMP="$(fresh)"
# A write into the target that bypasses the four named placement operations.
python3 -c "
import pathlib, sys
p = pathlib.Path(sys.argv[1]); t = p.read_text()
p.write_text(t.replace('place_tree() {',
    'sneak() {' + chr(10) + '    cp \"\$SEED_ROOT/README.md\" \"\$PROJECT_DIR/SNEAK.md\"' + chr(10) + '}' + chr(10) + 'place_tree() {', 1))
" "$TMP/install.sh"
expect_fail "named placement operations" "single-writer-bypass"
# exercises: check_install_write_sites
restore install.sh
  rm -rf "$TMP"
}
case_36() {
  local TMP; TMP="$(fresh)"
# 18. A green §10 row whose cited test stops naming its contract. The row then
# certifies nothing a reader can check: the test exists, is in the cited file
# and is not skipped, and none of that says it asserts THIS contract. Before the
# binding landed, 48 of 50 green rows were in that state and two linters
# disagreed about 21 contracts with nothing comparing them.
python3 -c "
import pathlib, re, sys
p = pathlib.Path(sys.argv[1])
t = p.read_text()
t2 = re.sub(r'\"\"\"Asserts SPEC-[0-9]+ [A-Z_]+\.\"\"\"\n', '', t, count=1)
assert t2 != t, 'no bound docstring to strip — the fixture has drifted'
p.write_text(t2)
" "$TMP/tests/test_router_reach.py"
# exercises: check_spec_rows_name_their_contract
expect_fail "does not name their contract" "spec-row-unbound"
restore tests/test_router_reach.py
  rm -rf "$TMP"
}
case_37() {
  local TMP; TMP="$(fresh)"
# 19. A copy of the frontmatter reader drifting from the canonical one. It must
# be a COPY — graph-lint, spec-lint, grill-lint and legal-lint ship into plants
# as standalone scripts with no package to import from — so byte-identity is the
# only thing standing between one reader and the seven divergent ones it
# replaced.
python3 -c "
import pathlib, sys
p = pathlib.Path(sys.argv[1])
p.write_text(p.read_text() + '\n# drifted\n')
" "$TMP/tools/frontmatter.py"
# exercises: check_frontmatter_reader_is_one_reader
expect_fail "has drifted from" "frontmatter-reader-drift"
restore tools/frontmatter.py
  rm -rf "$TMP"
}
case_38() {
  local TMP; TMP="$(fresh)"
# The tag-triggered release workflow: deleting it used to leave every other
# check green while CLAUDE.md's Release section and tools/prepare-release.py
# both went on describing a publish pipeline that no longer existed.
rm -f "$TMP/.github/workflows/release.yml"
expect_fail "workflows/release.yml is missing" "release-workflow"
# exercises: check_release_workflow
mkdir -p "$TMP/.github/workflows" && restore .github/workflows/release.yml
  rm -rf "$TMP"
}
# 20. SPEC-0001-gate-assertion-floor: a compatibility claim matches the shebang.
case_shell_floor() {
  local TMP; TMP="$(fresh)"
  # Restore the historical wording in the hermetic copy. The gate must say so.
  python3 - "$TMP/docs/specs/SPEC-0001-install-placement.md" <<'PY'
import sys
p = sys.argv[1]
t = open(p, encoding="utf-8").read()
old = "- **Compatibility:** bash and `python3` only; no third-party imports."
assert old in t, "the corrected §5 line is not where this mutant expects it"
open(p, "w", encoding="utf-8").write(t.replace(
    old,
    "- **Compatibility:** POSIX shell and `python3` only; no third-party imports.",
    1))
PY
  # exercises: check_shell_floor_claim_matches_the_shebang
  expect_fail "POSIX shell floor" "shell-floor-claim"
  restore docs/specs/SPEC-0001-install-placement.md

  # And the shipped text passes. This half is not decoration: §5 still carries
  # the parenthetical "This line claimed a POSIX shell floor until 2026-09-16"
  # and §12 quotes the old wording in full, so a check that greps the file for
  # the phrase turns the tree red on its own correction history. What is
  # forbidden is the CLAIM, not the word.
  lint >/dev/null || {
    echo "[shell-floor-claim] the corrected §5 — which names the bash floor and"\
         "records the old claim in §12 — must lint clean" >&2
    lint >&2
    exit 1
  }
  rm -rf "$TMP"
}
# 21. ADR-0004: agnosticism scan reaches docs/plans, tools, install.sh, DOC/INSTALL.
case_agn_docs() {
  local TMP; TMP="$(fresh)"
  # a dev-plan .md under docs/plans (newly scanned root)
  python3 -c "open('$TMP/docs/plans/scout-01-kernel.md','a').write(chr(10)+'Ran the probe from /home/exampleuser/Cypres_plant and captured the log.'+chr(10))"
  expect_fail "absolute operator home path" "agn-scope-docs-plans"
  restore docs/plans/scout-01-kernel.md
  # install.sh (a newly named top-level file)
  python3 -c "open('$TMP/install.sh','a').write(chr(10)+'# staged under /home/exampleuser/stage'+chr(10))"
  expect_fail "absolute operator home path" "agn-scope-install-sh"
  restore install.sh
  # DOCUMENTATION.md and INSTALL.md (newly named top-level files)
  python3 -c "open('$TMP/DOCUMENTATION.md','a').write(chr(10)+'Built under /home/exampleuser/build.'+chr(10))"
  expect_fail "absolute operator home path" "agn-scope-documentation-md"
  restore DOCUMENTATION.md
  python3 -c "open('$TMP/INSTALL.md','a').write(chr(10)+'Installed to /home/exampleuser/opt.'+chr(10))"
  expect_fail "absolute operator home path" "agn-scope-install-md"
  restore INSTALL.md
  rm -rf "$TMP"
}
# 22. ADR-0004: *.py and *.sh are scanned under a scanned root, not only *.md.
case_agn_py_sh() {
  local TMP; TMP="$(fresh)"
  # a *.py under tools/ (a newly scanned root)
  python3 -c "open('$TMP/tools/prose-lint.py','a').write(chr(10)+'# scratch: /home/exampleuser/scratch'+chr(10))"
  expect_fail "absolute operator home path" "agn-scope-tools-py"
  restore tools/prose-lint.py
  # a *.sh under a scanned root. No *.sh ships under a scanned root today, so the
  # glob's whole value is future files like this one; plant a fresh one to pin it.
  python3 -c "open('$TMP/tools/zz-agn-fixture.sh','w').write('#!/usr/bin/env bash'+chr(10)+'OUT=/home/exampleuser/out'+chr(10))"
  expect_fail "absolute operator home path" "agn-scope-root-sh"
  rm -f "$TMP/tools/zz-agn-fixture.sh"
  rm -rf "$TMP"
}

case_frontmatter_portable() {
  local TMP; TMP="$(fresh)"
  # 23. A shipped node whose unquoted title/description carries an inner ': '.
  # The seed's lenient reader keeps it; a strict-YAML skill loader (Prime Agent)
  # reads it as a nested mapping and drops the whole node. Claude Code's
  # integration uses the lenient reader, so the two hosts diverge silently.
  python3 - "$TMP/core/method/prose-posture.md" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1])
t = p.read_text()
old = "genre outranks generic advice"
new = "genre outranks generic advice: always"
assert old in t, "fixture drifted: prose-posture title tail changed"
p.write_text(t.replace(old, new, 1))
PY
  # exercises: check_frontmatter_is_portable_yaml
  expect_fail "strict-YAML skill loader" "frontmatter-inner-colon"
  restore core/method/prose-posture.md
  rm -rf "$TMP"
}

# --- one-case subcommand, run by the parallel dispatcher ---------------------
if [ "${1:-}" = "__case" ]; then
  "$2"
  exit $?
fi

# --- main: build the template once, dispatch every case in parallel ----------
SEEDLINT_TMPL="$(mktemp -d)"
trap 'rm -rf "$SEEDLINT_TMPL"' EXIT
( cd "$ROOT" && tar --exclude=.git --exclude=__pycache__ --exclude='*.pyc' \
    --exclude=.pytest_cache -cf - . ) | ( cd "$SEEDLINT_TMPL" && tar -xf - )
export SEEDLINT_TMPL ROOT

# 0. Baseline: the pristine template lints clean (once, not once per case).
TMP="$SEEDLINT_TMPL"
lint >/dev/null || { echo "baseline seed-lint did not pass on a clean copy" >&2; exit 1; }

SCN="$(mktemp)"
for c in case_01 case_02 case_03 case_04 case_05 case_06 case_07 case_08 case_09 case_10 case_11 case_12 case_13 case_14 case_15 case_16 case_17 case_18 case_19 case_20 case_21 case_22 case_23 case_24 case_25 case_26 case_27 case_28 case_29 case_30 case_31 case_32 case_33 case_34 case_35 case_36 case_37 case_38 case_shell_floor case_agn_docs case_agn_py_sh case_frontmatter_portable; do
  printf '%s\t%s\n' "$c" "bash \"$SELF\" __case $c" >> "$SCN"
done
rc=0
python3 "$ROOT/tests/gate_pool.py" run "$SCN" || rc=$?
rm -f "$SCN"

# 17. Every check_* in seed-lint.py is exercised above or declared (reads $ROOT).
python3 "$ROOT/tests/check-coverage-binder.py" "$ROOT"

# 15. The template still lints clean (the cases never touch it).
TMP="$SEEDLINT_TMPL"
lint >/dev/null || { echo "seed-lint did not return to PASS after restores" >&2; exit 1; }

[ "$rc" -eq 0 ] || { echo "seed-lint contract: FAIL — a planted violation did not fire" >&2; exit "$rc"; }
printf 'seed-lint contract: PASS\n'
