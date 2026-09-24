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
# 18b. A green §10 row citing a TOP-LEVEL seed-lint function binds against that
# function's body. The `def` of a top-level function sits under two blank lines,
# and a `^\s*def` match let `\s*` swallow them: the match began on the blank
# line and the scope searched was one newline, so no top-level function could
# bind a green row however plainly it named its slug (found at SPEC-0003 RED;
# BRIEF_TEMPLATES_BYTE_IDENTICAL and PRIME_EAGER_SURFACE_WITHIN_BUDGET were held
# at pending for it). The second half pins the other edge: the slug named only
# in the NEXT function does not bind, so the scope is the body, not the file.
case_spec_row_toplevel_def() {
  local TMP; TMP="$(fresh)"
python3 - "$TMP/tests/seed-lint.py" "$TMP/docs/specs/SPEC-0003-per-prompt-injection.md" <<'PY'
import sys
lint, spec = sys.argv[1], sys.argv[2]
fx = ('\n\ndef zz_row_binding_fixture() -> None:\n'
      '    """Asserts ZZ_PLANTED_TOPLEVEL_SLUG."""\n'
      '    fail("never called")\n')
open(lint, "a", encoding="utf-8").write(fx)
t = open(spec, encoding="utf-8").read()
i = t.index("| UNEXPECTED_EXCEPTION |")
j = t.index("\n", i) + 1
row = "| ZZ_PLANTED_TOPLEVEL_SLUG | zz_row_binding_fixture | tests/seed-lint.py | unit | green |\n"
open(spec, "w", encoding="utf-8").write(t[:j] + row + t[j:])
PY
  # exercises: check_spec_rows_name_their_contract
  lint >/dev/null || {
    echo "[spec-row-toplevel-def] a green row citing a top-level function, under"\
         "blank lines, that names its slug must lint clean" >&2
    lint >&2
    exit 1
  }
  restore tests/seed-lint.py
  restore docs/specs/SPEC-0003-per-prompt-injection.md
python3 - "$TMP/tests/seed-lint.py" "$TMP/docs/specs/SPEC-0003-per-prompt-injection.md" <<'PY'
import sys
lint, spec = sys.argv[1], sys.argv[2]
fx = ('\n\ndef zz_row_binding_fixture() -> None:\n'
      '    """Asserts nothing it names."""\n'
      '    fail("never called")\n'
      '\n\ndef zz_row_binding_neighbour() -> None:\n'
      '    """Asserts ZZ_PLANTED_TOPLEVEL_SLUG."""\n'
      '    fail("never called")\n')
open(lint, "a", encoding="utf-8").write(fx)
t = open(spec, encoding="utf-8").read()
i = t.index("| UNEXPECTED_EXCEPTION |")
j = t.index("\n", i) + 1
row = "| ZZ_PLANTED_TOPLEVEL_SLUG | zz_row_binding_fixture | tests/seed-lint.py | unit | green |\n"
open(spec, "w", encoding="utf-8").write(t[:j] + row + t[j:])
PY
  expect_fail "does not name their contract" "spec-row-toplevel-def-neighbour"
  restore tests/seed-lint.py
  restore docs/specs/SPEC-0003-per-prompt-injection.md
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
# 20. SPEC-0001-gate-assertion-floor SHELL_FLOOR_CLAIM_MATCHES_THE_SHEBANG: a compatibility claim matches the shebang.
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
# 21. ADR-0004 AGNOSTICISM_GATE_SCANS_DOCS_PLANS_TOOLS_INSTALLER: agnosticism scan reaches docs/plans, tools, install.sh, DOC/INSTALL.
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
# 22. ADR-0004 AGNOSTICISM_GATE_SCANS_PY_AND_SH: *.py and *.sh are scanned under a scanned root, not only *.md.
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

# X201 HOOK_TEXT_RESTATES_NO_KERNEL_RULE (SPEC-0003, I-8): the per-prompt hook
# text points at the kernel and restates none of it. A run of four tokens from a
# §0 "The task is…" cell, or a bare tier token, in either hook source fails the
# check. Two plants, one per rule, so both are shown to fire on their own: the
# cell carries no tier token, and the tier token shares no four-token run.
case_x201() {
  local TMP; TMP="$(fresh)"
  printf '\n# %s\n' "change beyond what that holds — architecture, contracts, dependencies, ambiguity" \
    >> "$TMP/integrations/claude-code/route-hook.py"
  # exercises: check_hook_text_restates_no_kernel_rule
  expect_fail "HOOK_TEXT_RESTATES_NO_KERNEL_RULE" "X201-planted-tier-cell"
  restore integrations/claude-code/route-hook.py
  printf '\n// the %s lane\n' "T2" >> "$TMP/integrations/prime-agent/route-extension.ts"
  expect_fail "HOOK_TEXT_RESTATES_NO_KERNEL_RULE" "X201-planted-tier-token"
  restore integrations/prime-agent/route-extension.ts
  echo "  X201 HOOK_TEXT_RESTATES_NO_KERNEL_RULE: a planted §0 cell and a planted T2 each fail the check — OK"
  rm -rf "$TMP"
}
# X202 PRIME_OVERLAY_RESTATES_NO_KERNEL_RULE (SPEC-0003, I-8): the same check
# reaches the `## Surfaced nodes` section of the Prime Agent overlay, and only
# that section. A FIRST MOVE step planted inside it fails; the same step
# planted before the first `## ` heading, outside it, draws no such finding.
# Growing the overlay also moves the published eager figures, so the second
# half asserts the ABSENCE of this finding rather than a clean lint.
case_x202() {
  local TMP out; TMP="$(fresh)"
  local STEP='Name the **2–3 nodes** that match the task; read **only** those (and their `requires:` closure).'
  python3 - "$TMP/integrations/prime-agent/APPEND_SYSTEM.md" "$STEP" inside <<'PY2'
import sys
p, step, where = sys.argv[1], sys.argv[2], sys.argv[3]
lines = open(p, encoding="utf-8").read().split("\n")
heads = [i for i, l in enumerate(lines) if l.rstrip() == "## Surfaced nodes"]
if len(heads) != 1:
    sys.exit(f"X202: the overlay has {len(heads)} `## Surfaced nodes` sections; exactly one is needed to plant into")
at = heads[0] + 1 if where == "inside" else next(i for i, l in enumerate(lines) if l.startswith("## "))
lines[at:at] = ["", step, ""]
open(p, "w", encoding="utf-8").write("\n".join(lines))
PY2
  expect_fail "PRIME_OVERLAY_RESTATES_NO_KERNEL_RULE" "X202-step-inside-section"
  restore integrations/prime-agent/APPEND_SYSTEM.md
  python3 - "$TMP/integrations/prime-agent/APPEND_SYSTEM.md" "$STEP" outside <<'PY2'
import sys
p, step = sys.argv[1], sys.argv[2]
lines = open(p, encoding="utf-8").read().split("\n")
at = next(i for i, l in enumerate(lines) if l.startswith("## "))
lines[at:at] = ["", step, ""]
open(p, "w", encoding="utf-8").write("\n".join(lines))
PY2
  out="$(lint)" || true
  if grep -q "PRIME_OVERLAY_RESTATES_NO_KERNEL_RULE" <<<"$out"; then
    echo "[X202-step-outside-section] a FIRST MOVE step outside the section drew the finding" >&2
    echo "$out" >&2; exit 1
  fi
  restore integrations/prime-agent/APPEND_SYSTEM.md
  echo "  X202 PRIME_OVERLAY_RESTATES_NO_KERNEL_RULE: a FIRST MOVE step fails inside the section, not outside it — OK"
  rm -rf "$TMP"
}
# X203 PRIME_OVERLAY_RESTATES_NO_KERNEL_RULE (SPEC-0003, I-8; review of
# 2deda6a..343445f): renaming the section heading must not switch the check
# off. The overlay copy gets `## Surfaced  nodes` (two spaces) and a planted
# `T2` under it, and seed-lint must fail on its own, naming the slug, rather
# than skip a section it can no longer find.
case_x203() {
  local TMP; TMP="$(fresh)"
  python3 - "$TMP/integrations/prime-agent/APPEND_SYSTEM.md" <<'PY2'
import sys
p = sys.argv[1]
lines = open(p, encoding="utf-8").read().split("\n")
heads = [i for i, l in enumerate(lines) if l.rstrip() == "## Surfaced nodes"]
if len(heads) != 1:
    sys.exit(f"X203: the overlay has {len(heads)} `## Surfaced nodes` sections; exactly one is needed to rename")
lines[heads[0]] = "## Surfaced  nodes"
lines[heads[0] + 1:heads[0] + 1] = ["", "Take the T2 lane for these.", ""]
open(p, "w", encoding="utf-8").write("\n".join(lines))
PY2
  # exercises: check_hook_text_restates_no_kernel_rule
  expect_fail "PRIME_OVERLAY_RESTATES_NO_KERNEL_RULE" "X203-renamed-heading-planted-T2"
  restore integrations/prime-agent/APPEND_SYSTEM.md
  echo "  X203 PRIME_OVERLAY_RESTATES_NO_KERNEL_RULE: a renamed section heading does not switch the check off — OK"
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
# E family (ADR-0009 host tiers): E1-E3 are in test-full-install.sh; E4 is here.
# E4 HOST_TIERS_AGREE (SPEC-0001, ADR-0009): the tier assignment has one home, the
# three arrays in install.sh, and the host matrix publishes it. A published table
# that disagrees with the arrays is a second home drifting. The unmutated tree
# passing is the suite's baseline lint above; this case plants the drift.
caseHOST_TIERS_AGREE() {
  local TMP; TMP="$(fresh)"
python3 - "$TMP/documentation/host-capability-matrix.md" <<'PY'
import re, sys
p = sys.argv[1]
lines = open(p, encoding="utf-8").read().split("\n")
start = next((i for i, l in enumerate(lines)
              if re.match(r"^#+\s.*Support tiers", l)), None)
assert start is not None, ("HOST_TIERS_AGREE: the matrix has no 'Support tiers' "
                           "section to mutate — the fixture has drifted")
level = len(lines[start]) - len(lines[start].lstrip("#"))
end = next((j for j in range(start + 1, len(lines))
            if re.match(r"^#{1,%d}\s" % level, lines[j])), len(lines))
rows = {}
for i in range(start + 1, end):
    if lines[i].lstrip().startswith("|"):
        cells = lines[i].split("|")
        if len(cells) > 3:
            rows[cells[1].strip().strip("`").strip().lower()] = i
assert "supported" in rows and "frozen" in rows, \
    f"HOST_TIERS_AGREE: no supported/frozen rows in the tier table: {sorted(rows)}"
sup = lines[rows["supported"]].split("|")
assert "opencode" in sup[2], f"HOST_TIERS_AGREE: opencode is not in the supported row: {sup[2]!r}"
sup[2] = " " + re.sub(r"`?opencode`?\s*,?\s*", "", sup[2]).strip(" ,") + " "
lines[rows["supported"]] = "|".join(sup)
fro = lines[rows["frozen"]].split("|")
fro[2] = " " + fro[2].strip() + ", `opencode` "
lines[rows["frozen"]] = "|".join(fro)
open(p, "w", encoding="utf-8").write("\n".join(lines))
PY
  # exercises: check_host_tiers
  expect_fail "host-capability-matrix.md" "host-tiers-agree"
  expect_fail "install.sh" "host-tiers-agree (names both files)"
  restore documentation/host-capability-matrix.md

  # (a) review F2: a DUPLICATED tier row. A second `frozen` row listing opencode,
  # inserted above the real one, used to be overwritten by the real row when the
  # table was read into a dict, so the published table said opencode is frozen
  # and supported at once and the lint passed. A tier has one row.
python3 - "$TMP/documentation/host-capability-matrix.md" <<'PY'
import re, sys
p = sys.argv[1]
lines = open(p, encoding="utf-8").read().split("\n")
i = next((i for i, l in enumerate(lines) if re.match(r"^\|\s*`?frozen`?\s*\|", l)), None)
assert i is not None, "HOST_TIERS_AGREE (a): no frozen row to duplicate — the fixture has drifted"
lines.insert(i, "| `frozen` | `opencode` | A duplicated row planted by the test. |")
open(p, "w", encoding="utf-8").write("\n".join(lines))
PY
  # exercises: check_host_tiers
  expect_fail "host-capability-matrix.md.*frozen\|frozen.*host-capability-matrix.md" "host-tiers-duplicate-row"
  restore documentation/host-capability-matrix.md

  # (b) review F2: a host dropped from FROZEN_TOOLS AND from the matrix's frozen
  # row. Arrays and table still agree with each other, and `all` is untouched, so
  # the old three comparisons all pass; but codex is still a tool the dispatch
  # `case` installs, and now sits in no tier. The union of the three arrays must
  # equal the tools install.sh dispatches.
python3 - "$TMP/install.sh" "$TMP/documentation/host-capability-matrix.md" <<'PY'
import re, sys
inst, matrix = sys.argv[1], sys.argv[2]
s = open(inst, encoding="utf-8").read()
s2, n = re.subn(r"(?m)^FROZEN_TOOLS=\(codex github-copilot\)", "FROZEN_TOOLS=(github-copilot)", s)
assert n == 1, "HOST_TIERS_AGREE (b): FROZEN_TOOLS is not (codex github-copilot) — the fixture has drifted"
assert re.search(r"(?m)^\s*codex\)\s+install_codex\s*;;", s2), \
    "HOST_TIERS_AGREE (b): the dispatch no longer installs codex — the fixture has drifted"
open(inst, "w", encoding="utf-8").write(s2)
m = open(matrix, encoding="utf-8").read()
m2, n = re.subn(r"(?m)^(\|\s*`frozen`\s*\|\s*)`codex`,\s*", r"\1", m)
assert n == 1, "HOST_TIERS_AGREE (b): the matrix's frozen row does not start with `codex`, — the fixture has drifted"
open(matrix, "w", encoding="utf-8").write(m2)
PY
  # exercises: check_host_tiers
  expect_fail "codex" "host-tiers-universe (a dispatchable tool in no tier)"
  expect_fail "install.sh" "host-tiers-universe (names install.sh)"
  restore install.sh
  restore documentation/host-capability-matrix.md

  # (c) review F2: the three suites that keep the frozen adapters under
  # regression each carry an EVERY_HOST literal (grill-7.27.0 §4). Nothing held
  # them to the tools install.sh dispatches, so a suite could drop a host and
  # silently stop covering it. Each literal is planted separately, so a check
  # that reads only one of the three files still leaves two of these red.
  local suite
  for suite in tests/test-full-install.sh tests/test-install-placement.sh tests/test-unified-graph-install.sh; do
python3 - "$TMP/$suite" <<'PY'
import re, sys
p = sys.argv[1]
s = open(p, encoding="utf-8").read()
s2, n = re.subn(r'(?m)^EVERY_HOST="claude-code opencode codex github-copilot prime-agent"$',
                'EVERY_HOST="claude-code opencode github-copilot prime-agent"', s)
assert n == 1, f"HOST_TIERS_AGREE (c): {p} has no five-host EVERY_HOST literal — the fixture has drifted"
open(p, "w", encoding="utf-8").write(s2)
PY
    # exercises: check_host_tiers
    expect_fail "$(basename "$suite")" "host-tiers-every-host ($suite)"
    restore "$suite"
  done

  # (d) review m1: an arm the dispatch `case` runs, written in a shape other than
  # `<tool>) install_<tool> ;;`. `cursor) install_cursor || true ;;` dispatches a
  # host that sits in no tier; a line-shaped regex does not see it, and the lint
  # stayed green. The dispatch universe is every label of the `case "$tool"` block.
python3 - "$TMP/install.sh" <<'PY'
import re, sys
p = sys.argv[1]
s = open(p, encoding="utf-8").read()
s2, n = re.subn(r"(?m)^(\s*)(prime-agent\)\s+install_prime_agent\s*;;)",
                r"\1cursor) install_cursor || true ;;\n\1\2", s)
assert n == 1, "HOST_TIERS_AGREE (d): no `prime-agent) install_prime_agent ;;` dispatch arm — the fixture has drifted"
open(p, "w", encoding="utf-8").write(s2)
PY
  # exercises: check_host_tiers
  expect_fail "untiered \['cursor'\]" "host-tiers-dispatch-any-arm-shape"
  restore install.sh

  # (e) review m1: the argument parser's accepted-tool pattern is a third literal
  # list of hosts. A tool it accepts and no tier holds is a host the installer
  # takes on the command line with no maintenance commitment behind it.
python3 - "$TMP/install.sh" <<'PY'
import re, sys
p = sys.argv[1]
s = open(p, encoding="utf-8").read()
s2, n = re.subn(r"(?m)^(\s*claude-code\|opencode\|codex\|github-copilot\|prime-agent\|)(all\)\s*TOOLS\+=)",
                r"\1cursor|\2", s)
assert n == 1, "HOST_TIERS_AGREE (e): the argument parser's tool pattern is not where this mutant expects it — the fixture has drifted"
open(p, "w", encoding="utf-8").write(s2)
PY
  # exercises: check_host_tiers
  expect_fail "argument parser.*cursor" "host-tiers-argparser-accepts-untiered"
  restore install.sh

  # (f) safe direction kept: a quoted dispatch label is not read as a bare tool
  # name; the lint refuses it rather than guessing.
python3 - "$TMP/install.sh" <<'PY'
import re, sys
p = sys.argv[1]
s = open(p, encoding="utf-8").read()
s2, n = re.subn(r"(?m)^(\s*)codex\)(\s+install_codex\s*;;)", r'\1"codex")\2', s)
assert n == 1, "HOST_TIERS_AGREE (f): no `codex) install_codex ;;` dispatch arm — the fixture has drifted"
open(p, "w", encoding="utf-8").write(s2)
PY
  # exercises: check_host_tiers
  expect_fail "install.sh" "host-tiers-quoted-label-refused"
  restore install.sh

  # (g) safe direction kept: an arm whose command sits on the line after its
  # label is the same dispatch, and the tree still lints clean.
python3 - "$TMP/install.sh" <<'PY'
import re, sys
p = sys.argv[1]
s = open(p, encoding="utf-8").read()
s2, n = re.subn(r"(?m)^(\s*)codex\)\s+(install_codex\s*;;)", r"\1codex)\n\1    \2", s)
assert n == 1, "HOST_TIERS_AGREE (g): no `codex) install_codex ;;` dispatch arm — the fixture has drifted"
open(p, "w", encoding="utf-8").write(s2)
PY
  lint >/dev/null || {
    echo "[host-tiers-multiline-arm] a dispatch arm split across two lines must lint clean" >&2
    lint >&2
    exit 1
  }
  restore install.sh
  rm -rf "$TMP"
}

# --- SPEC-0004 front door: the shared fixture helper --------------------------
# Every case_fd_* runs on a hermetic copy with the conforming fixture of
# tests/fixtures/front-door/ laid in (SPEC-0004 §6 "Fixture"): whole-file stubs
# for README.md, INSTALL.md and each integrations/<host>/README.md; patches to
# DOCUMENTATION.md, the three references and the matrix that each assert
# exactly one match, so a drifted base fails the case instead of leaving a patch
# unapplied; {{NAME}} values filled from the copy's own tests/seed-lint.py
# loaded as a module; FRONT_DOOR_PENDING rewritten to the empty set in
# tests/seed-lint.py and in its tests/ratchets.json mirror. Planted line
# positions are computed from the copy, never written as literals.
# Every expectation is anchored: `front-door: <SLUG>: <file>:<line>: ` plus a
# message fragment, and every case except case_fd_check_raised fails when the
# output holds `: RAISED ` (§7 CHECK_RAISED), so a crash cannot pass a case.
# The bash 3.2 floor holds: no bash-4 builtins or case-folding expansions and
# no in-place stream edits; every planted edit goes through the Python helper.
FD_FIX_REL="tests/fixtures/front-door"

fd_py() {  # fd_py <subcommand> <args...>: the one fixture helper
python3 - "$@" <<'PY'
import ast, importlib.util, json, re, shutil, sys
from pathlib import Path

FIX = "tests/fixtures/front-door"
SPEC = "docs/specs/SPEC-0004-front-door.md"
SNAP = FIX + "/.laid"
ADR_RANGE = re.compile(r"(?i)\badr-?\d{4}\s*(?:\.\.|–|—|to|through)\s*(?:adr-?)?\d{4}\b")


def die(msg):
    print(f"fd-fixture: {msg}", file=sys.stderr)
    sys.exit(2)


def read(p):
    return Path(p).read_text(encoding="utf-8")


def write(p, t):
    Path(p).write_text(t, encoding="utf-8")


def sub1(text, old, new, what):
    n = text.count(old)
    if n != 1:
        die(f"{what}: expected exactly one match of {old[:70]!r}, found {n} "
            f"(the base has drifted from the fixture)")
    return text.replace(old, new, 1)


def seedlint(root):
    path = Path(root) / "tests" / "seed-lint.py"
    spec = importlib.util.spec_from_file_location("fd_seedlint_copy", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def values(root):
    """The computed values the fixture prints, taken from the copy's seed-lint."""
    m = seedlint(root)
    surfaces = {}
    m.check_published_eager_figures = lambda s: surfaces.update(s)
    m.check_eager_surface(m.KERNEL.stat().st_size)
    sizes = sorted(len(b.strip("\n").splitlines()) for _l, _f, b in m.machinery_nodes())
    mid = len(sizes) // 2
    median = sizes[mid] if len(sizes) % 2 else (sizes[mid - 1] + sizes[mid]) // 2
    return {
        "EAGER_CLAUDE_CODE": surfaces["claude-code"],
        "LIVE": sorted(set(surfaces.values()) | {m.EAGER_BUDGET}),
        "LARGEST_BODY": sizes[-1],
        "MEDIAN_BODY": median,
        "MACHINERY_BODY_CEILING": m.MACHINERY_BODY_CEILING,
        "LIFECYCLE_BODY_CEILING": m.LIFECYCLE_BODY_CEILING,
        "KERNEL_BUDGET": m.KERNEL_BUDGET,
        "EAGER_BUDGET": m.EAGER_BUDGET,
    }


def fill(text, vals):
    out = re.sub(r"\{\{([A-Z_]+)\}\}", lambda mo: str(vals[mo.group(1)]), text)
    if "{{" in out:
        die("an unfilled {{NAME}} placeholder is left in the fixture")
    return out


def grouped(n):
    return f"{n:,}".replace(",", " ")


def find_lines(text, needle):
    lines = text.splitlines()
    exact = [i for i, l in enumerate(lines, 1) if l == needle]
    return exact if exact else [i for i, l in enumerate(lines, 1) if needle in l]


def one_line(path, needle, nth=None):
    hits = find_lines(read(path), needle)
    if nth is not None:
        if len(hits) < nth:
            die(f"{path}: fewer than {nth} lines hold {needle!r}")
        return hits[nth - 1]
    if len(hits) != 1:
        die(f"{path}: expected one line holding {needle!r}, found {len(hits)}")
    return hits[0]


def replace_region(text, heading, new, required, what):
    lines = text.splitlines(keepends=True)
    at = [i for i, l in enumerate(lines) if l.rstrip("\n") == heading]
    if len(at) > 1:
        die(f"{what}: {heading!r} occurs {len(at)} times")
    if not at:
        if required:
            die(f"{what}: no {heading!r} heading (the base has drifted from the fixture)")
        return text.rstrip("\n") + "\n\n" + new.rstrip("\n") + "\n"
    start = at[0]
    end = next((j for j in range(start + 1, len(lines)) if lines[j].startswith("## ")),
               len(lines))
    tail = "".join(lines[end:])
    body = new.rstrip("\n") + "\n" + ("\n" if tail else "")
    return "".join(lines[:start]) + body + tail


def ledger_nodes(src):
    hits = []
    for node in ast.parse(src).body:
        targets = node.targets if isinstance(node, ast.Assign) else (
            [node.target] if isinstance(node, ast.AnnAssign) else [])
        if any(isinstance(t, ast.Name) and t.id == "FRONT_DOOR_PENDING" for t in targets):
            hits.append(node)
    return hits


def set_ledger(root, members, mirror=True, required=True):
    sl = Path(root) / "tests" / "seed-lint.py"
    src = read(sl)
    hits = ledger_nodes(src)
    if not hits:
        if required:
            die("the copy's tests/seed-lint.py defines no FRONT_DOOR_PENDING "
                "(SPEC-0004 pending ledger not implemented)")
        print("fd-fixture: no FRONT_DOOR_PENDING in the copy's seed-lint; "
              "nothing to empty (SPEC-0004 checks not implemented)", file=sys.stderr)
        return
    if len(hits) != 1:
        die(f"FRONT_DOOR_PENDING is assigned {len(hits)} times at top level")
    node = hits[0]
    lines = src.splitlines(keepends=True)
    lit = ("frozenset({" + ", ".join(repr(x) for x in sorted(members)) + "})"
           if members else "frozenset()")
    lines[node.lineno - 1:node.end_lineno] = [f"FRONT_DOOR_PENDING = {lit}\n"]
    write(sl, "".join(lines))
    if mirror:
        rj = Path(root) / "tests" / "ratchets.json"
        data = json.loads(read(rj))
        if "FRONT_DOOR_PENDING" not in data.get("ratchets", {}):
            die("tests/ratchets.json does not mirror FRONT_DOOR_PENDING")
        data["ratchets"]["FRONT_DOOR_PENDING"] = sorted(members)
        write(rj, json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def spec_cap(root, name):
    text = read(Path(root) / SPEC)
    m = re.findall(rf"(?m)^\| `{name}` \| (\d+) \|", text)
    if len(m) != 1:
        die(f"{SPEC}: expected one §6 row for {name}, found {len(m)}")
    return int(m[0])


def entry_span(lines, term):
    head = [i for i, l in enumerate(lines) if l.rstrip("\n") == f"### {term}"]
    if len(head) != 1:
        die(f"DOCUMENTATION.md: expected one glossary entry '### {term}', found {len(head)}")
    start = head[0]
    end = next((j for j in range(start + 1, len(lines))
                if lines[j].startswith("### ") or lines[j].startswith("## ")), len(lines))
    return start, end


def field_index(lines, term, field):
    start, end = entry_span(lines, term)
    at = [j for j in range(start, end) if lines[j].startswith(f"- **{field}:**")]
    if len(at) != 1:
        die(f"DOCUMENTATION.md: entry {term!r} has {len(at)} {field!r} fields")
    return at[0]


def row_index(lines, rid):
    at = [i for i, l in enumerate(lines) if f'<a id="{rid}"></a>' in l and l.startswith("|")]
    if len(at) != 1:
        die(f"DOCUMENTATION.md: expected one enforcement row {rid!r}, found {len(at)}")
    return at[0]


def version_bind(root, version):
    root = Path(root)
    man = root / "manifest.json"
    t, n = re.subn(r'(?m)^(  "version": ")[^"]*(")', rf"\g<1>{version}\g<2>", read(man))
    if n != 1:
        die(f"manifest.json: expected one top-level version, found {n}")
    write(man, t)
    cl = root / "CHANGELOG.md"
    t, n = re.subn(r"(?m)^(##\s+)\d+\.\d+\.\d+\b", rf"\g<1>{version}", read(cl), count=1)
    if n != 1:
        die("CHANGELOG.md: no '## X.Y.Z' heading to keep in step with the manifest")
    write(cl, t)
    for rel in ("DOCUMENTATION.md", "documentation/README.md"):
        p = root / rel
        t, n = re.subn(r"([Vv]ersion(?: documented)?[:*\s]+\**)\d+\.\d+\.\d+",
                       rf"\g<1>{version}", read(p))
        if n < 1:
            die(f"{rel}: no documented-version pin to keep in step with the manifest")
        write(p, t)


def snapshot(root):
    root = Path(root)
    rels = ["README.md", "INSTALL.md", "DOCUMENTATION.md", "manifest.json", "CHANGELOG.md",
            "tests/seed-lint.py", "tests/ratchets.json", SPEC,
            "templates/knowledge-graph/graph-lint.py"]
    rels += sorted(str(p.relative_to(root)) for p in root.glob("documentation/*.md"))
    rels += sorted(str(p.relative_to(root)) for p in root.glob("integrations/*/README.md"))
    for rel in rels:
        dst = root / SNAP / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(root / rel, dst)


def lay(root):
    root = Path(root)
    fx = root / FIX
    vals = values(root)
    for rel in ("README.md", "INSTALL.md"):
        write(root / rel, fill(read(fx / rel), vals))
    stubs = sorted(p.parent.name for p in (fx / "integrations").glob("*/README.md"))
    hosts = sorted(p.parent.name for p in (root / "integrations").glob("*/README.md"))
    if stubs != hosts:
        die(f"integration README stubs {stubs} do not match the copy's hosts {hosts}")
    for h in hosts:
        write(root / "integrations" / h / "README.md",
              fill(read(fx / "integrations" / h / "README.md"), vals))
    ev = root / "docs" / "plans" / "front-door-evidence.md"
    if ev.exists():
        die(f"{ev.relative_to(root)} already exists in the copy")
    write(ev, read(fx / "evidence.md"))

    doc = read(root / "DOCUMENTATION.md")
    doc = replace_region(doc, "## 15. Glossary", read(fx / "glossary.md"), True, "glossary region")
    doc = replace_region(doc, "## 17. What is enforced, and how", read(fx / "enforcement.md"),
                         False, "enforcement region")
    # From increment 5 the shipped DOCUMENTATION.md holds its own body-figure
    # paragraph, one line opening with the fixture's words; the fixture's
    # replaces it, so a case that edits the fixture's figures leaves no shipped
    # copy behind to satisfy the check.
    body = fill(read(fx / "body-figures.md"), vals)
    shipped = re.findall(r"(?m)^Routable body sizes, computed by .*\n", doc)
    if len(shipped) > 1:
        die(f"DOCUMENTATION.md holds {len(shipped)} body-figure paragraphs, not one")
    if shipped:
        doc = sub1(doc, shipped[0], body, "body-figure paragraph")
    else:
        doc = sub1(doc, "\n## 15. Glossary\n", "\n" + body + "\n## 15. Glossary\n",
                   "body-figure paragraph")
    if ADR_RANGE.search(doc):
        doc = sub1(doc, "The decisions are recorded in `docs/decisions/adr-0001..0008`.",
                   "The decisions are recorded in the decision index, `docs/decisions/index.md`.",
                   "ADR range in §6.4")
        doc = sub1(doc, "  decisions/            adr-0001..0008\n",
                   "  decisions/            ADR records, listed in index.md\n",
                   "ADR range in the layout block")
        if ADR_RANGE.search(doc):
            die("DOCUMENTATION.md holds an ADR range the fixture does not patch")
    write(root / "DOCUMENTATION.md", doc)

    # The shipped references carry their own one-line opener from increment 4
    # on; the fixture's replaces it, as the part headings below accept either
    # level, so a case that deletes the fixture's opener leaves none behind.
    for rel, opener, head in (("documentation/agents-reference.md", "opener-agents.md",
                               r"An agent is\b"),
                              ("documentation/skills-and-templates-reference.md",
                               "opener-skills.md", r"A skill is\b"),
                              ("documentation/protocols-reference.md", "opener-protocols.md",
                               r"A protocol( node)? is\b")):
        lines = read(root / rel).splitlines(keepends=True)
        if not lines or not lines[0].startswith("# "):
            die(f"{rel}: the first line is not its '#' title")
        shipped = (len(lines) > 3 and lines[1] == "\n" and re.match(head, lines[2])
                   and lines[3] == "\n")
        lines[1:3 if shipped else 1] = ["\n", read(fx / opener)]
        write(root / rel, "".join(lines))
    for rel, title in (("documentation/skills-and-templates-reference.md", "Part A — Skills"),
                       ("documentation/skills-and-templates-reference.md",
                        "Part B — Artifact and knowledge-graph templates"),
                       ("documentation/skills-and-templates-reference.md",
                        "Part C — Prompt and brief templates"),
                       ("documentation/protocols-reference.md", "Per-protocol reference")):
        lines = read(root / rel).splitlines(keepends=True)
        at = [i for i, l in enumerate(lines) if l.rstrip("\n") in (f"# {title}", f"## {title}")]
        if len(at) != 1:
            die(f"{rel}: expected one part heading {title!r}, found {len(at)}")
        lines[at[0]] = f"## {title}\n"
        write(root / rel, "".join(lines))

    rel = "documentation/host-capability-matrix.md"
    lines = read(root / rel).splitlines(keepends=True)
    at = [i for i, l in enumerate(lines) if l.startswith("| **mechanically enforced** |")]
    if len(at) != 1:
        die(f"{rel}: expected one '**mechanically enforced**' class-table row, found {len(at)}")
    lines[at[0]] = read(fx / "matrix-row.md")
    write(root / rel, "".join(lines))

    set_ledger(root, [], mirror=True, required=False)
    snapshot(root)


def main(argv):
    cmd, args = argv[0], argv[1:]
    if cmd == "lay":
        lay(args[0])
    elif cmd == "line":                       # FILE NEEDLE [NTH]
        print(one_line(args[0], args[1], int(args[2]) if len(args) > 2 else None))
    elif cmd == "sub":                        # FILE OLD NEW
        write(args[0], sub1(read(args[0]), args[1], args[2], args[0]))
    elif cmd == "sub_re":                     # FILE PATTERN REPL (exactly one match)
        t, n = re.subn(args[1], args[2], read(args[0]))
        if n != 1:
            die(f"{args[0]}: expected one match of /{args[1]}/, found {n}")
        write(args[0], t)
    elif cmd in ("insert_before", "insert_after"):   # FILE NEEDLE TEXT
        path, needle, text = args
        lines = read(path).splitlines(keepends=True)
        i = one_line(path, needle) - 1
        add = text if text.endswith("\n") else text + "\n"
        at = i if cmd == "insert_before" else i + 1
        lines[at:at] = [add]
        write(path, "".join(lines))
    elif cmd == "del_line":                   # FILE NEEDLE
        lines = read(args[0]).splitlines(keepends=True)
        del lines[one_line(args[0], args[1]) - 1]
        write(args[0], "".join(lines))
    elif cmd == "append":                     # FILE TEXT
        t = read(args[0])
        write(args[0], t + ("" if t.endswith("\n") else "\n") + args[1]
              + ("" if args[1].endswith("\n") else "\n"))
    elif cmd == "swap":                       # FILE NEEDLE_A NEEDLE_B: swap two whole lines
        lines = read(args[0]).splitlines(keepends=True)
        a, b = one_line(args[0], args[1]) - 1, one_line(args[0], args[2]) - 1
        lines[a], lines[b] = lines[b], lines[a]
        write(args[0], "".join(lines))
    elif cmd == "push":                       # FILE INSERT_BEFORE MEASURE TARGET
        path, before, measure, target = args[0], args[1], args[2], int(args[3])
        now = one_line(path, measure)
        if now >= target:
            die(f"{path}: {measure!r} already sits at line {now}, not above {target}")
        lines = read(path).splitlines(keepends=True)
        i = one_line(path, before) - 1
        k = target - now
        lines[i:i] = ["Filler line for a planted case.\n"] * (k - 1) + ["\n"]
        write(path, "".join(lines))
        if one_line(path, measure) != target:
            die(f"{path}: push did not land {measure!r} on line {target}")
    elif cmd == "move_block":                 # FILE START_NEEDLE NLINES AFTER_NEEDLE
        path, start, n, after = args[0], args[1], int(args[2]), args[3]
        lines = read(path).splitlines(keepends=True)
        s = one_line(path, start) - 1
        block = lines[s:s + n]
        del lines[s:s + n]
        write(path, "".join(lines))
        a = one_line(path, after)
        lines = read(path).splitlines(keepends=True)
        lines[a:a] = ["\n"] + block
        write(path, "".join(lines))
    elif cmd == "limit":                      # ROOT CONSTANT CAP: the constant, or its cap
        m = seedlint(args[0])
        if hasattr(m, args[1]):
            print(int(getattr(m, args[1])))
        else:
            print(f"fd-fixture: seed-lint defines no {args[1]}; planting past its "
                  f"cap {args[2]} instead", file=sys.stderr)
            print(spec_cap(args[0], args[2]))
    elif cmd == "cap":                        # ROOT CAP
        print(spec_cap(args[0], args[1]))
    elif cmd == "setcap":                     # ROOT CAP VALUE|--remove
        p = Path(args[0]) / SPEC
        pat = rf"(?m)^\| `{args[1]}` \| \d+ \|[^\n]*\n"
        if args[2] == "--remove":
            t, n = re.subn(pat, "", read(p))
        else:
            t, n = re.subn(rf"(?m)^(\| `{args[1]}` \| )\d+( \|)", rf"\g<1>{args[2]}\g<2>", read(p))
        if n != 1:
            die(f"{SPEC}: expected one §6 row for {args[1]}, found {n}")
        write(p, t)
    elif cmd == "setconst":                   # ROOT NAME VALUE: seed-lint and its ratchet, one edit
        root, name, value = Path(args[0]), args[1], int(args[2])
        sl = root / "tests" / "seed-lint.py"
        src = read(sl)
        pat = rf"(?m)^({name}\s*(?::[^=\n]+)?=\s*)[0-9_]+"
        hits = list(re.finditer(pat, src))
        if len(hits) != 1:
            die(f"tests/seed-lint.py: expected one assignment of {name}, found {len(hits)} "
                f"(SPEC-0004 constant not implemented)")
        line = src.count("\n", 0, hits[0].start()) + 1
        write(sl, re.sub(pat, rf"\g<1>{value}", src, count=1))
        rj = root / "tests" / "ratchets.json"
        data = json.loads(read(rj))
        if name not in data.get("ratchets", {}):
            die(f"tests/ratchets.json records no {name}")
        data["ratchets"][name] = value
        write(rj, json.dumps(data, indent=2, ensure_ascii=False) + "\n")
        print(line)
    elif cmd == "ledger":                     # ROOT [--no-mirror] MEMBER...
        mirror = "--no-mirror" not in args[1:]
        set_ledger(args[0], [a for a in args[1:] if a != "--no-mirror"], mirror=mirror)
    elif cmd == "ledger_members":             # ROOT
        m = seedlint(args[0])
        if not hasattr(m, "FRONT_DOOR_PENDING"):
            die("the copy's tests/seed-lint.py defines no FRONT_DOOR_PENDING "
                "(SPEC-0004 pending ledger not implemented)")
        print(" ".join(sorted(m.FRONT_DOOR_PENDING)))
    elif cmd == "bind":                       # ROOT status|version VALUE
        root, what, value = Path(args[0]), args[1], args[2]
        if what == "status":
            p = root / SPEC
            text = read(p)
            fm = re.match(r"^---\n(.*?\n)---\n", text, re.S)
            if not fm:
                die(f"{SPEC}: no frontmatter")
            new_fm, n = re.subn(r"(?m)^status:[^\n]*$", f"status: {value}", fm.group(1))
            if n != 1:
                die(f"{SPEC}: expected one frontmatter status, found {n}")
            write(p, "---\n" + new_fm + "---\n" + text[fm.end():])
        elif what == "version":
            version_bind(root, value)
        else:
            die(f"bind: unknown binding value {what!r}")
    elif cmd == "val":                        # ROOT NAME [--grouped]
        v = values(args[0])[args[1]]
        print(grouped(v) if "--grouped" in args else v)
    elif cmd == "stale":                      # ROOT: a five-digit figure nothing computes
        live = set(values(args[0])["LIVE"])
        v = next(x for x in range(99_999, 10_000, -1) if x not in live)
        print(grouped(v))
    elif cmd == "agent_names":                # ROOT
        names = []
        for p in sorted((Path(args[0]) / "agents").glob("*.md")):
            mo = re.search(r"(?m)^name:\s*(\S+)", read(p))
            if mo:
                names.append(mo.group(1).strip("'\""))
        print(", ".join(f"`{n}`" for n in names))
    elif cmd == "entry_field":                # ROOT TERM FIELD VALUE|--delete
        p = Path(args[0]) / "DOCUMENTATION.md"
        lines = read(p).splitlines(keepends=True)
        i = field_index(lines, args[1], args[2])
        if args[3] == "--delete":
            del lines[i]
        else:
            lines[i] = f"- **{args[2]}:** {args[3]}\n"
        write(p, "".join(lines))
    elif cmd == "entry_line":                 # ROOT TERM [FIELD]
        lines = read(Path(args[0]) / "DOCUMENTATION.md").splitlines(keepends=True)
        print((field_index(lines, args[1], args[2]) if len(args) > 2
               else entry_span(lines, args[1])[0]) + 1)
    elif cmd == "entry_swap":                 # ROOT TERM FIELD_A FIELD_B
        p = Path(args[0]) / "DOCUMENTATION.md"
        lines = read(p).splitlines(keepends=True)
        a, b = field_index(lines, args[1], args[2]), field_index(lines, args[1], args[3])
        lines[a], lines[b] = lines[b], lines[a]
        write(p, "".join(lines))
    elif cmd == "entry_delete":               # ROOT TERM
        p = Path(args[0]) / "DOCUMENTATION.md"
        lines = read(p).splitlines(keepends=True)
        s, e = entry_span(lines, args[1])
        del lines[s:e]
        write(p, "".join(lines))
    elif cmd == "row_sub":                    # ROOT ID OLD NEW (within that row only)
        p = Path(args[0]) / "DOCUMENTATION.md"
        lines = read(p).splitlines(keepends=True)
        i = row_index(lines, args[1])
        lines[i] = sub1(lines[i], args[2], args[3], f"row {args[1]}")
        write(p, "".join(lines))
    elif cmd == "row_line":                   # ROOT ID
        print(row_index(read(Path(args[0]) / "DOCUMENTATION.md").splitlines(keepends=True),
                        args[1]) + 1)
    elif cmd == "row_delete":                 # ROOT ID
        p = Path(args[0]) / "DOCUMENTATION.md"
        lines = read(p).splitlines(keepends=True)
        del lines[row_index(lines, args[1])]
        write(p, "".join(lines))
    elif cmd == "glossary_flat":              # ROOT: the region in its pre-harvest flat form
        p = Path(args[0]) / "DOCUMENTATION.md"
        write(p, replace_region(read(p), "## 15. Glossary",
                                read(Path(args[0]) / FIX / "glossary-flat.md"), True, "glossary"))
    elif cmd == "cut":                        # ROOT: README to its title; DOCUMENTATION without §15 and §17
        root = Path(args[0])
        title = read(root / "README.md").splitlines()[0]
        write(root / "README.md", title + "\n")
        p = root / "DOCUMENTATION.md"
        for heading in ("## 15. Glossary", "## 17. What is enforced, and how"):
            t = replace_region(read(p), heading, "", True, heading)
            write(p, t)
    elif cmd == "inject_raise":               # ROOT FUNC
        p = Path(args[0]) / "tests" / "seed-lint.py"
        lines = read(p).splitlines(keepends=True)
        at = [i for i, l in enumerate(lines) if l.startswith(f"def {args[1]}(")]
        if len(at) != 1:
            die(f"tests/seed-lint.py: expected one 'def {args[1]}(', found {len(at)} "
                f"(the SPEC-0004 check does not exist)")
        j = at[0]
        while not lines[j].rstrip().endswith(":"):
            j += 1
        lines[j + 1:j + 1] = ['    raise RuntimeError("planted")\n']
        write(p, "".join(lines))
    elif cmd == "exemption":                  # ROOT: one EAGER_EXEMPTIONS entry
        p = Path(args[0]) / "tests" / "seed-lint.py"
        t, n = re.subn(r"(?m)^(EAGER_EXEMPTIONS[^\n]*=\s*\{)",
                       r'\1\n    "codex": (99_999, "planted by case_fd_body_home"),', read(p))
        if n != 1:
            die(f"tests/seed-lint.py: expected one EAGER_EXEMPTIONS literal, found {n}")
        write(p, t)
    elif cmd == "unliteral":                  # ROOT VALUE: drop a literal from graph-lint.py
        p = Path(args[0]) / "templates" / "knowledge-graph" / "graph-lint.py"
        t, n = re.subn(rf"(?<![\w.]){args[1]}(?![\w.])", str(int(args[1]) - 1), read(p))
        if n < 1:
            die(f"templates/knowledge-graph/graph-lint.py holds no {args[1]} literal")
        write(p, t)
    elif cmd == "invalid_utf8":               # FILE
        with open(args[0], "ab") as fh:
            fh.write(b"\nundecodable \xff\xfe bytes\n")
    else:
        die(f"unknown subcommand {cmd!r}")


main(sys.argv[1:])
PY
}

# A fresh copy with the conforming fixture laid in. Run inside `$(...)`, where
# bash does not inherit `set -e`, so every failure exits explicitly.
fd_fresh() {
  local d; d="$(fresh)" || exit 1
  fd_py lay "$d" >&2 || exit 1
  printf '%s' "$d"
}
# Re-lay one file as the fixture left it (the snapshot taken after laying).
fd_restore() { cp "$TMP/$FD_FIX_REL/.laid/$1" "$TMP/$1"; }

# The anchored pattern, as an ERE: `front-door: <SLUG>: <file>:<line>: `. With
# no line given the line may be any number; with several, any one of them.
fd_at() {
  local slug="$1" file="$2" alt; shift 2
  file="$(printf '%s' "$file" | sed 's/[.]/\\./g')"
  if [ $# -eq 0 ]; then
    printf 'front-door: %s: %s:[0-9]+: ' "$slug" "$file"
  else
    alt="$(printf '%s|' "$@")"; alt="${alt%|}"
    printf 'front-door: %s: %s:(%s): ' "$slug" "$file" "$alt"
  fi
}
# A planted case lints through the copy's front door only: the copy's own
# tests/seed-lint.py loaded as a module, its front_door_checks() dispatcher run,
# and `findings` printed exactly as main() prints them, exit 1 when any stand.
# Every anchored `front-door: <SLUG>: ` line, PENDING line and RAISED line is
# the same text a full run prints, so no expectation weakens; the rest of
# seed-lint (about 1 s a pass, ~130 passes) is not what these cases plant.
# The cases that prove the wiring through main() (the fixture guard, the
# pending ledger's exit 0, a front-door check running after an earlier check
# raised, and a raised check failing the run) use fd_lint_full instead.
fd_front_door_lint() {
python3 - "$TMP/tests/seed-lint.py" 2>&1 <<'PY'
import importlib.util, sys
from pathlib import Path

path = Path(sys.argv[1])
sys.path.insert(0, str(path.parent))
spec = importlib.util.spec_from_file_location("fd_seedlint_front_door", path)
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)
mod.front_door_checks()
if mod.findings:
    print(f"seed lint: FAIL ({len(mod.findings)} finding(s))")
    for f in mod.findings:
        print(f"  - {f}")
    sys.exit(1)
print("seed lint: PASS")
PY
}
fd_lint() { FD_OUT="$(fd_front_door_lint)" && FD_RC=0 || FD_RC=$?; }
fd_lint_full() { FD_OUT="$(lint)" && FD_RC=0 || FD_RC=$?; }
# Lines of the last run matching the anchored ERE and every fragment. A plain
# fragment is a case-insensitive fixed string; `re:` marks an ERE; `!` marks a
# fixed string the line must NOT hold.
fd_match() {
  local lines f; lines="$(grep -E -- "$1" <<<"$FD_OUT" || true)"; shift
  for f in "$@"; do
    [ -n "$lines" ] || break
    case "$f" in
      re:*) lines="$(grep -E -- "${f#re:}" <<<"$lines" || true)" ;;
      !*)   lines="$(grep -viF -- "${f#!}" <<<"$lines" || true)" ;;
      *)    lines="$(grep -iF -- "$f" <<<"$lines" || true)" ;;
    esac
  done
  printf '%s' "$lines"
}
fd_show() { grep -F 'front-door' <<<"$FD_OUT" >&2 || echo "(no front-door line at all)" >&2; }
fd_refuse_raised() {
  if grep -qF ': RAISED ' <<<"$FD_OUT"; then
    echo "[$1] a front-door check RAISED; a crash cannot satisfy a planted case" >&2
    fd_show; exit 1
  fi
}
fd_expect() {  # LABEL ANCHOR FRAGMENT...: exit 1, no RAISED, and the anchored line
  local label="$1"; shift
  fd_lint
  fd_refuse_raised "$label"
  [ "$FD_RC" -eq 1 ] || { echo "[$label] expected exit 1, got $FD_RC" >&2; fd_show; exit 1; }
  [ -n "$(fd_match "$@")" ] || {
    echo "[$label] missing expected line: /$1/ with: ${*:2}" >&2; fd_show; exit 1; }
}
fd_expect_absent() {  # LABEL ANCHOR FRAGMENT...: a boundary that passes
  local label="$1"; shift
  fd_lint
  fd_refuse_raised "$label"
  [ -z "$(fd_match "$@")" ] || {
    echo "[$label] this plant must pass, and it produced: /$1/ with: ${*:2}" >&2; fd_show; exit 1; }
}
fd_expect_none() {  # LABEL FIXED: no line of the last run holds FIXED
  if grep -qF -- "$2" <<<"$FD_OUT"; then
    echo "[$1] unexpected line holding: $2" >&2; fd_show; exit 1
  fi
}
fd_ratchet_accepts() {  # the refusal must be seed-lint's: ratchet-lint accepts the same copy
  python3 "$TMP/tools/ratchet-lint.py" >/dev/null 2>&1 || {
    echo "[$1] tools/ratchet-lint.py refused the copy; the case needs a copy it accepts" >&2
    python3 "$TMP/tools/ratchet-lint.py" >&2 || true; exit 1; }
}
# SPEC-0004 §6 "Fixture" binding_values: a copy that plants a ledger member
# runs below `implemented` and below FRONT_DOOR_RELEASE unless it plants them.
fd_bind() {
  fd_py bind "$TMP" status "${1:-active}"
  fd_py bind "$TMP" version "${2:-7.28.0}"
}

# --- SPEC-0004 front door: one case per §10 row of the case table ------------
# Each case names its §10 label (X300-X335) and slug beside its plants; the
# `# exercises:` markers bind each check_fd_* to its planted violation.

case_fd_fixture_clean() {
  local TMP; TMP="$(fd_fresh)"
  # X300 (fixture guard, no slug): the conforming fixture yields no front-door
  # line and no RAISED line, and from increment 5, when check_published_body_figures
  # moved to BODY_FIGURE_HOME, seed-lint exits 0 on it (SPEC-0004 §6 clean_case).
  fd_lint_full
  fd_refuse_raised "fd-fixture-clean"
  if grep -qF 'front-door: ' <<<"$FD_OUT"; then
    echo "[fd-fixture-clean] the conforming fixture produced front-door lines" >&2; fd_show; exit 1
  fi
  [ "$FD_RC" -eq 0 ] || { echo "[fd-fixture-clean] expected exit 0, got $FD_RC" >&2; echo "$FD_OUT" >&2; exit 1; }
  rm -rf "$TMP"
}

case_fd_first_screen_order() {
  local TMP L L2 MAXH; TMP="$(fd_fresh)"
  # X301 FIRST_SCREEN_ORDER (a) headings 2 and 3 swapped
  fd_py swap "$TMP/README.md" '## Who it is for and not for' '## What installing does to your repository'
  L="$(fd_py line "$TMP/README.md" '## What installing does to your repository')"
  L2="$(fd_py line "$TMP/README.md" '## Who it is for and not for')"
  # exercises: check_fd_first_screen_order
  fd_expect "fd-first-screen-order (a)" "$(fd_at FIRST_SCREEN_ORDER README.md "$L" "$L2")" 'order'
  fd_restore README.md
  # X301 FIRST_SCREEN_ORDER (b) an extra ## between headings 1 and 2
  fd_py insert_before "$TMP/README.md" '## Who it is for and not for' $'## An extra section\n'
  L="$(fd_py line "$TMP/README.md" '## An extra section')"
  fd_expect "fd-first-screen-order (b)" "$(fd_at FIRST_SCREEN_ORDER README.md "$L")" 'An extra section'
  fd_restore README.md
  # X301 FIRST_SCREEN_ORDER (c) the first ## pushed below FIRST_HEADING_MAX_LINE
  MAXH="$(fd_py limit "$TMP" FIRST_HEADING_MAX_LINE FIRST_HEADING_CAP)"
  fd_py push "$TMP/README.md" '## What CYPRESS is' '## What CYPRESS is' "$((MAXH + 1))"
  fd_expect "fd-first-screen-order (c)" "$(fd_at FIRST_SCREEN_ORDER README.md "$((MAXH + 1))")" 'FIRST_HEADING_MAX_LINE'
  rm -rf "$TMP"
}

case_fd_first_screen_budget() {
  local TMP L MAXS; TMP="$(fd_fresh)"
  # X301 FIRST_SCREEN_ORDER (a) the marker moved below FIRST_SCREEN_MAX_LINES
  MAXS="$(fd_py limit "$TMP" FIRST_SCREEN_MAX_LINES FIRST_SCREEN_CAP)"
  fd_py push "$TMP/README.md" '<!-- first-screen-end -->' '<!-- first-screen-end -->' "$((MAXS + 1))"
  # exercises: check_fd_first_screen_order
  fd_expect "fd-first-screen-budget (a)" "$(fd_at FIRST_SCREEN_ORDER README.md "$((MAXS + 1))")" 'FIRST_SCREEN_MAX_LINES'
  fd_restore README.md
  # X301 FIRST_SCREEN_ORDER (b) the marker duplicated
  fd_py insert_after "$TMP/README.md" '<!-- first-screen-end -->' $'\n<!-- first-screen-end -->'
  L="$(fd_py line "$TMP/README.md" '<!-- first-screen-end -->' 2)"
  fd_expect "fd-first-screen-budget (b)" "$(fd_at FIRST_SCREEN_ORDER README.md "$L")" 'first-screen-end'
  fd_restore README.md
  # X301 FIRST_SCREEN_ORDER (c) the marker removed
  fd_py del_line "$TMP/README.md" '<!-- first-screen-end -->'
  fd_expect "fd-first-screen-budget (c)" "$(fd_at FIRST_SCREEN_ORDER README.md 0)" 'first-screen-end'
  rm -rf "$TMP"
}

case_fd_first_command_line() {
  local TMP L L2 MAXC; TMP="$(fd_fresh)"
  # X301 FIRST_SCREEN_ORDER (a) the first install.sh line pushed below FIRST_COMMAND_LINE
  MAXC="$(fd_py limit "$TMP" FIRST_COMMAND_LINE FIRST_COMMAND_CAP)"
  fd_py push "$TMP/README.md" '```sh' 'bash cypress/install.sh' "$((MAXC + 1))"
  # exercises: check_fd_first_screen_order
  fd_expect "fd-first-command-line (a)" "$(fd_at FIRST_SCREEN_ORDER README.md "$((MAXC + 1))")" 'FIRST_COMMAND_LINE'
  fd_restore README.md
  # X301 FIRST_SCREEN_ORDER (b) the first sh fence moved under ## How it works (AC-2)
  fd_py move_block "$TMP/README.md" '```sh' 4 '## How it works'
  L="$(fd_py line "$TMP/README.md" '```sh')"
  L2="$(fd_py line "$TMP/README.md" 'bash cypress/install.sh')"
  fd_expect "fd-first-command-line (b)" "$(fd_at FIRST_SCREEN_ORDER README.md "$L" "$L2")" 'Try it'
  rm -rf "$TMP"
}

case_fd_what_you_get_heading() {
  local TMP L; TMP="$(fd_fresh)"
  # X301 FIRST_SCREEN_ORDER: `## What you get` appended (AC-3)
  fd_py append "$TMP/README.md" $'\n## What you get\n\nA list of files.'
  L="$(fd_py line "$TMP/README.md" '## What you get')"
  # exercises: check_fd_first_screen_order
  fd_expect "fd-what-you-get" "$(fd_at FIRST_SCREEN_ORDER README.md "$L")" 'What you get'
  rm -rf "$TMP"
}

case_fd_first_screen_caps() {
  local TMP L CAP; TMP="$(fd_fresh)"
  # X334 FIRST_SCREEN_ORDER (e) the FIRST_SCREEN_CAP row removed from the copy's
  # SPEC-0004 §6 constants table: a missing required input
  fd_py setcap "$TMP" FIRST_SCREEN_CAP --remove
  # exercises: check_fd_first_screen_order
  fd_expect "fd-first-screen-caps (e)" "$(fd_at FIRST_SCREEN_ORDER docs/specs/SPEC-0004-front-door.md 0)" 'FIRST_SCREEN_CAP'
  fd_restore docs/specs/SPEC-0004-front-door.md
  # X334 FIRST_SCREEN_ORDER (a) FIRST_SCREEN_MAX_LINES raised to its cap + 1 in
  # tests/seed-lint.py and tests/ratchets.json in one edit; ratchet-lint accepts
  # that copy, so the refusal is seed-lint's (§7 LINE_CEILING_RAISED_PAST_CAP)
  CAP="$(fd_py cap "$TMP" FIRST_SCREEN_CAP)"
  L="$(fd_py setconst "$TMP" FIRST_SCREEN_MAX_LINES "$((CAP + 1))")"
  fd_expect "fd-first-screen-caps (a)" "$(fd_at FIRST_SCREEN_ORDER tests/seed-lint.py "$L")" 'FIRST_SCREEN_MAX_LINES' 'FIRST_SCREEN_CAP'
  fd_ratchet_accepts "fd-first-screen-caps (a)"
  # X334 FIRST_SCREEN_ORDER (d) passes: the same raise after the spec's cap moved first
  fd_py setcap "$TMP" FIRST_SCREEN_CAP "$((CAP + 1))"
  fd_expect_absent "fd-first-screen-caps (d)" "$(fd_at FIRST_SCREEN_ORDER tests/seed-lint.py)"
  fd_restore docs/specs/SPEC-0004-front-door.md; fd_restore tests/seed-lint.py; fd_restore tests/ratchets.json
  # X334 FIRST_SCREEN_ORDER (b) FIRST_HEADING_MAX_LINE raised to its cap + 1
  CAP="$(fd_py cap "$TMP" FIRST_HEADING_CAP)"
  L="$(fd_py setconst "$TMP" FIRST_HEADING_MAX_LINE "$((CAP + 1))")"
  fd_expect "fd-first-screen-caps (b)" "$(fd_at FIRST_SCREEN_ORDER tests/seed-lint.py "$L")" 'FIRST_HEADING_MAX_LINE' 'FIRST_HEADING_CAP'
  fd_ratchet_accepts "fd-first-screen-caps (b)"
  fd_restore tests/seed-lint.py; fd_restore tests/ratchets.json
  # X334 FIRST_SCREEN_ORDER (c) FIRST_COMMAND_LINE raised to its cap + 1
  CAP="$(fd_py cap "$TMP" FIRST_COMMAND_CAP)"
  L="$(fd_py setconst "$TMP" FIRST_COMMAND_LINE "$((CAP + 1))")"
  fd_expect "fd-first-screen-caps (c)" "$(fd_at FIRST_SCREEN_ORDER tests/seed-lint.py "$L")" 'FIRST_COMMAND_LINE' 'FIRST_COMMAND_CAP'
  fd_ratchet_accepts "fd-first-screen-caps (c)"
  rm -rf "$TMP"
}

case_fd_later_sections_order() {
  local TMP L L2; TMP="$(fd_fresh)"
  # X302 FIRST_SCREEN_ORDER (a) headings 7 and 8 swapped
  fd_py swap "$TMP/README.md" '## Why it is built this way' '## What it does not do'
  L="$(fd_py line "$TMP/README.md" '## Why it is built this way')"
  L2="$(fd_py line "$TMP/README.md" '## What it does not do')"
  # exercises: check_fd_first_screen_order
  fd_expect "fd-later-sections (a)" "$(fd_at FIRST_SCREEN_ORDER README.md "$L" "$L2")" 'order'
  fd_restore README.md
  # X302 FIRST_SCREEN_ORDER (b) `## Where to go next` duplicated
  fd_py append "$TMP/README.md" $'\n## Where to go next\n\n- [Install guide](INSTALL.md)'
  L="$(fd_py line "$TMP/README.md" '## Where to go next' 2)"
  fd_expect "fd-later-sections (b)" "$(fd_at FIRST_SCREEN_ORDER README.md "$L")" 'Where to go next'
  fd_restore README.md
  # X302 FIRST_SCREEN_ORDER (c) `## How it works` removed
  fd_py del_line "$TMP/README.md" '## How it works'
  fd_expect "fd-later-sections (c)" "$(fd_at FIRST_SCREEN_ORDER README.md 0)" 'How it works'
  rm -rf "$TMP"
}

case_fd_install_target_paths() {
  local TMP L; TMP="$(fd_fresh)"
  # X303 INSTALL_SECTION_NAMES_TARGET_PATHS (a) the `.cypress/seed.json` token removed (AC-15)
  fd_py sub "$TMP/README.md" 'and the install stamp `.cypress/seed.json`.' 'and the install stamp.'
  fd_py sub "$TMP/README.md" 'the derived install stamp `.cypress/seed.json` (' 'the derived install stamp ('
  # exercises: check_fd_install_section_names_target_paths
  fd_expect "fd-install-target-paths (a)" "$(fd_at INSTALL_SECTION_NAMES_TARGET_PATHS README.md)" '.cypress/seed.json'
  fd_restore README.md
  # X303 INSTALL_SECTION_NAMES_TARGET_PATHS (b) `.cursor/rules/` added (not in install.sh)
  fd_py sub "$TMP/README.md" 'the graph under `docs/graph/`,' 'the graph under `docs/graph/`, the rules under `.cursor/rules/`,'
  L="$(fd_py line "$TMP/README.md" '`.cursor/rules/`')"
  fd_expect "fd-install-target-paths (b)" "$(fd_at INSTALL_SECTION_NAMES_TARGET_PATHS README.md "$L")" '.cursor/rules/'
  fd_restore README.md
  # X303 INSTALL_SECTION_NAMES_TARGET_PATHS (c) the backup unit names no stamp and links no row (AC-16)
  fd_py sub "$TMP/README.md" 'A differing file already in place is kept beside itself as a timestamped copy and then replaced, not merged. The one file replaced without a copy is the derived install stamp `.cypress/seed.json` ([backup before replace](DOCUMENTATION.md#enf-backup-before-replace)).' 'Every file it replaces is left beside itself.'
  fd_expect "fd-install-target-paths (c)" "$(fd_at INSTALL_SECTION_NAMES_TARGET_PATHS README.md)" 'enf-backup-before-replace'
  rm -rf "$TMP"
}

case_fd_install_seed_path() {
  local TMP L; TMP="$(fd_fresh)"
  # X303 INSTALL_SECTION_NAMES_TARGET_PATHS: a seed-source path in the install section (AC-15)
  fd_py sub "$TMP/README.md" 'the graph under `docs/graph/`,' 'the graph under `docs/graph/`, the method under `core/method/`,'
  L="$(fd_py line "$TMP/README.md" '`core/method/`')"
  # exercises: check_fd_install_section_names_target_paths
  fd_expect "fd-install-seed-path" "$(fd_at INSTALL_SECTION_NAMES_TARGET_PATHS README.md "$L")" 'core/'
  rm -rf "$TMP"
}

case_fd_where_next() {
  local TMP L; TMP="$(fd_fresh)"
  # X304 WHERE_NEXT_LINKS_THE_REFERENCES (a) the decision-index link removed (AC-23)
  fd_py del_line "$TMP/README.md" '- [Decision index](docs/decisions/index.md)'
  # exercises: check_fd_where_next_links_the_references
  fd_expect "fd-where-next (a)" "$(fd_at WHERE_NEXT_LINKS_THE_REFERENCES README.md)" 'docs/decisions/index.md'
  fd_restore README.md
  # X304 WHERE_NEXT_LINKS_THE_REFERENCES (b) a fragment that names no anchor
  fd_py sub "$TMP/README.md" '(DOCUMENTATION.md#glossary)' '(DOCUMENTATION.md#glossery)'
  L="$(fd_py line "$TMP/README.md" '#glossery')"
  fd_expect "fd-where-next (b)" "$(fd_at WHERE_NEXT_LINKS_THE_REFERENCES README.md "$L")" 'glossery'
  fd_restore README.md
  # X304 WHERE_NEXT_LINKS_THE_REFERENCES (c) a link to a reference that does not exist (AC-23)
  fd_py insert_after "$TMP/README.md" '- [Install guide](INSTALL.md)' '- [Another reference](documentation/no-such-reference.md)'
  L="$(fd_py line "$TMP/README.md" 'no-such-reference.md')"
  fd_expect "fd-where-next (c)" "$(fd_at WHERE_NEXT_LINKS_THE_REFERENCES README.md "$L")" 'no-such-reference.md'
  rm -rf "$TMP"
}

case_fd_glossary_absent() {
  local TMP; TMP="$(fd_fresh)"
  # X305 GLOSSARY_ENTRY_COMPLETE: the region in its pre-harvest flat-bullet form parses to no entries
  fd_py glossary_flat "$TMP"
  # exercises: check_fd_glossary_entry_complete
  fd_expect "fd-glossary-absent" "$(fd_at GLOSSARY_ENTRY_COMPLETE DOCUMENTATION.md 0)" 'no entries'
  rm -rf "$TMP"
}

case_fd_glossary_fields() {
  local TMP HL; TMP="$(fd_fresh)"
  HL="$(fd_py entry_line "$TMP" plant)"
  # X305 GLOSSARY_ENTRY_COMPLETE (a) `plant` loses its Why field
  fd_py entry_field "$TMP" plant Why --delete
  # exercises: check_fd_glossary_entry_complete
  fd_expect "fd-glossary-fields (a)" "$(fd_at GLOSSARY_ENTRY_COMPLETE DOCUMENTATION.md "$HL")" 'Why'
  fd_restore DOCUMENTATION.md
  # X305 GLOSSARY_ENTRY_COMPLETE (b) Here and Field swapped
  fd_py entry_swap "$TMP" plant Here Field
  fd_expect "fd-glossary-fields (b)" "$(fd_at GLOSSARY_ENTRY_COMPLETE DOCUMENTATION.md "$HL")" 'order'
  fd_restore DOCUMENTATION.md
  # X305 GLOSSARY_ENTRY_COMPLETE (c) a blank line between the headword and its anchor
  fd_py insert_after "$TMP/DOCUMENTATION.md" '### plant' ''
  fd_expect "fd-glossary-fields (c)" "$(fd_at GLOSSARY_ENTRY_COMPLETE DOCUMENTATION.md "$HL")" 'term-plant'
  fd_restore DOCUMENTATION.md
  # X305 GLOSSARY_ENTRY_COMPLETE (d) Forms without the headword
  fd_py entry_field "$TMP" plant Forms 'plants'
  fd_expect "fd-glossary-fields (d)" "$(fd_at GLOSSARY_ENTRY_COMPLETE DOCUMENTATION.md "$HL")" 'Forms'
  rm -rf "$TMP"
}

case_fd_glossary_closed_values() {
  local TMP HL L; TMP="$(fd_fresh)"
  HL="$(fd_py entry_line "$TMP" plant)"
  # X305 GLOSSARY_ENTRY_COMPLETE (a) an Enforcement value outside the class set
  fd_py entry_field "$TMP" plant Enforcement '**mandatory**'
  L="$(fd_py entry_line "$TMP" plant Enforcement)"
  # exercises: check_fd_glossary_entry_complete
  fd_expect "fd-glossary-closed-values (a)" "$(fd_at GLOSSARY_ENTRY_COMPLETE DOCUMENTATION.md "$L" "$HL")" 'mandatory'
  fd_restore DOCUMENTATION.md
  # X305 GLOSSARY_ENTRY_COMPLETE (b) a Divergence value outside the divergence set
  fd_py entry_field "$TMP" plant Divergence '**similar**'
  L="$(fd_py entry_line "$TMP" plant Divergence)"
  fd_expect "fd-glossary-closed-values (b)" "$(fd_at GLOSSARY_ENTRY_COMPLETE DOCUMENTATION.md "$L" "$HL")" 'similar'
  fd_restore DOCUMENTATION.md
  # X305 GLOSSARY_ENTRY_COMPLETE (c) `status: verified` with no URL and no date
  fd_py entry_field "$TMP" plant Field 'a living organism (status: verified)'
  L="$(fd_py entry_line "$TMP" plant Field)"
  fd_expect "fd-glossary-closed-values (c)" "$(fd_at GLOSSARY_ENTRY_COMPLETE DOCUMENTATION.md "$L" "$HL")" 'status: verified'
  fd_restore DOCUMENTATION.md
  # X305 GLOSSARY_ENTRY_COMPLETE (d) a Why that matches no §6 why_rule form
  fd_py entry_field "$TMP" plant Why 'because'
  L="$(fd_py entry_line "$TMP" plant Why)"
  fd_expect "fd-glossary-closed-values (d)" "$(fd_at GLOSSARY_ENTRY_COMPLETE DOCUMENTATION.md "$L" "$HL")" 'Why'
  rm -rf "$TMP"
}

case_fd_glossary_required_term() {
  local TMP; TMP="$(fd_fresh)"
  # X305 GLOSSARY_ENTRY_COMPLETE: the required `tier` entry deleted
  fd_py entry_delete "$TMP" tier
  # exercises: check_fd_glossary_entry_complete
  fd_expect "fd-glossary-required-term" "$(fd_at GLOSSARY_ENTRY_COMPLETE DOCUMENTATION.md 0)" 'tier'
  rm -rf "$TMP"
}

case_fd_glossary_paths() {
  local TMP HL L; TMP="$(fd_fresh)"
  HL="$(fd_py entry_line "$TMP" plant)"
  L="$(fd_py entry_line "$TMP" plant 'Implemented at')"
  # X306 GLOSSARY_PATHS_EXIST (a) a seed path that does not exist
  fd_py entry_field "$TMP" plant 'Implemented at' '`install.sh`, `protocols/grow.md`, `tools/no-such-tool.py`. An install produces `.cypress/seed.json` (`write_seed_stamp`).'
  # exercises: check_fd_glossary_paths_exist
  fd_expect "fd-glossary-paths (a)" "$(fd_at GLOSSARY_PATHS_EXIST DOCUMENTATION.md "$L" "$HL")" 'tools/no-such-tool.py'
  fd_restore DOCUMENTATION.md
  # X306 GLOSSARY_PATHS_EXIST (b) a line suffix past the end of the file
  fd_py entry_field "$TMP" plant 'Implemented at' '`install.sh:999999`, `protocols/grow.md`. An install produces `.cypress/seed.json` (`write_seed_stamp`).'
  fd_expect "fd-glossary-paths (b)" "$(fd_at GLOSSARY_PATHS_EXIST DOCUMENTATION.md "$L" "$HL")" 'install.sh:999999'
  fd_restore DOCUMENTATION.md
  # X306 GLOSSARY_PATHS_EXIST (c) a field with no path that does not begin n/a
  fd_py entry_field "$TMP" plant 'Implemented at' 'the installer and the grow protocol'
  fd_expect "fd-glossary-paths (c)" "$(fd_at GLOSSARY_PATHS_EXIST DOCUMENTATION.md "$L" "$HL")" 'n/a'
  rm -rf "$TMP"
}

case_fd_glossary_install_literal() {
  local TMP HL L; TMP="$(fd_fresh)"
  HL="$(fd_py entry_line "$TMP" plant)"
  L="$(fd_py entry_line "$TMP" plant 'Implemented at')"
  # X306 GLOSSARY_PATHS_EXIST (a) an install target install.sh never names
  fd_py entry_field "$TMP" plant 'Implemented at' '`install.sh`, `protocols/grow.md`. An install produces `.cypress/no-such.json` (`write_seed_stamp`).'
  # exercises: check_fd_glossary_paths_exist
  fd_expect "fd-glossary-install-literal (a)" "$(fd_at GLOSSARY_PATHS_EXIST DOCUMENTATION.md "$L" "$HL")" '.cypress/no-such.json'
  fd_restore DOCUMENTATION.md
  # X306 GLOSSARY_PATHS_EXIST (b) an install function install.sh does not define
  fd_py entry_field "$TMP" plant 'Implemented at' '`install.sh`, `protocols/grow.md`. An install produces `.cypress/seed.json` (`write_nothing`).'
  fd_expect "fd-glossary-install-literal (b)" "$(fd_at GLOSSARY_PATHS_EXIST DOCUMENTATION.md "$L" "$HL")" 'write_nothing'
  rm -rf "$TMP"
}

case_fd_definition_links() {
  local TMP L; TMP="$(fd_fresh)"
  L="$(fd_py entry_line "$TMP" plant Here)"
  # X307 NO_UNLINKED_PROJECT_TERM_IN_DEFINITION (a) `seed` unlinked in the `plant` Here field
  fd_py entry_field "$TMP" plant Here 'A repository after the seed was installed into it and [grown](#term-growth).'
  # exercises: check_fd_no_unlinked_project_term_in_definition
  fd_expect "fd-definition-links (a)" "$(fd_at NO_UNLINKED_PROJECT_TERM_IN_DEFINITION DOCUMENTATION.md "$L")" 'seed'
  fd_restore DOCUMENTATION.md
  # X307 NO_UNLINKED_PROJECT_TERM_IN_DEFINITION (b) `seed` linked to another entry
  fd_py entry_field "$TMP" plant Here 'A repository after the [seed](#term-growth) was installed into it and [grown](#term-growth).'
  fd_expect "fd-definition-links (b)" "$(fd_at NO_UNLINKED_PROJECT_TERM_IN_DEFINITION DOCUMENTATION.md "$L")" 'term-growth'
  rm -rf "$TMP"
}

case_fd_term_linked() {
  local TMP L; TMP="$(fd_fresh)"
  # X308 TERM_LINKED_ON_FIRST_USE (a) an unlinked `plant` before its first linked use
  fd_py insert_before "$TMP/README.md" '## Who it is for and not for' $'Your repository becomes a plant.\n'
  L="$(fd_py line "$TMP/README.md" 'Your repository becomes a plant.')"
  # exercises: check_fd_term_linked_on_first_use
  fd_expect "fd-term-linked (a)" "$(fd_at TERM_LINKED_ON_FIRST_USE README.md "$L")" 'plant'
  fd_restore README.md
  # X308 TERM_LINKED_ON_FIRST_USE (b) the first use links another entry (ANCHOR_DRIFT)
  fd_py sub "$TMP/README.md" '(DOCUMENTATION.md#term-plant)' '(DOCUMENTATION.md#term-graft)'
  L="$(fd_py line "$TMP/README.md" '#term-graft')"
  fd_expect "fd-term-linked (b)" "$(fd_at TERM_LINKED_ON_FIRST_USE README.md "$L")" 'term-graft'
  fd_restore README.md
  # X308 TERM_LINKED_ON_FIRST_USE (c) passes: the first `plant` sits in a code span (§8)
  fd_py insert_before "$TMP/README.md" '## Who it is for and not for' $'Run `plant` checks.\n'
  fd_expect_absent "fd-term-linked (c)" "$(fd_at TERM_LINKED_ON_FIRST_USE README.md)"
  rm -rf "$TMP"
}

case_fd_one_home() {
  local TMP L; TMP="$(fd_fresh)"
  # X309 DEFINITION_HAS_ONE_HOME (a) a near-copy of the `skill` Here sentence in a reference
  fd_py append "$TMP/documentation/agents-reference.md" $'\nA skill is a Markdown procedure that the working session reads into its own context, and it grants no extra tools at all.'
  L="$(fd_py line "$TMP/documentation/agents-reference.md" 'and it grants no extra tools at all.')"
  # exercises: check_fd_definition_has_one_home
  fd_expect "fd-one-home (a)" "$(fd_at DEFINITION_HAS_ONE_HOME documentation/agents-reference.md "$L")" 'skill' 're:[01]\.[0-9]{2}'
  fd_restore documentation/agents-reference.md
  # X309 DEFINITION_HAS_ONE_HOME (b) the same for a short (under five-token) definition
  fd_py entry_field "$TMP" turn Here 'worker spawn and return'
  fd_py append "$TMP/documentation/agents-reference.md" $'\nEach turn is one worker spawn and return.'
  L="$(fd_py line "$TMP/documentation/agents-reference.md" 'Each turn is one worker spawn and return.')"
  fd_expect "fd-one-home (b)" "$(fd_at DEFINITION_HAS_ONE_HOME documentation/agents-reference.md "$L")" 're:(^|[^a-z])turn([^a-z]|$)' 're:[01]\.[0-9]{2}'
  rm -rf "$TMP"
}

case_fd_reference_opener() {
  local TMP L; TMP="$(fd_fresh)"
  # X310 REFERENCE_OPENS_WITH_ITS_DEFINITION (a) the reference opens with no definition (AC-24)
  fd_py del_line "$TMP/documentation/agents-reference.md" 'An agent is a system prompt with frontmatter'
  L="$(fd_py line "$TMP/documentation/agents-reference.md" 'This document describes all')"
  # exercises: check_fd_reference_opens_with_its_definition
  fd_expect "fd-reference-opener (a)" "$(fd_at REFERENCE_OPENS_WITH_ITS_DEFINITION documentation/agents-reference.md "$L")" 'An agent is'
  fd_restore documentation/agents-reference.md
  # X310 REFERENCE_OPENS_WITH_ITS_DEFINITION (b) opener kept, its term-skill link removed
  fd_py sub "$TMP/documentation/agents-reference.md" '[skill entry](../DOCUMENTATION.md#term-skill)' 'skill entry'
  L="$(fd_py line "$TMP/documentation/agents-reference.md" 'An agent is a system prompt with frontmatter')"
  fd_expect "fd-reference-opener (b)" "$(fd_at REFERENCE_OPENS_WITH_ITS_DEFINITION documentation/agents-reference.md "$L")" 'term-skill'
  rm -rf "$TMP"
}

case_fd_enforcement_row() {
  local TMP L; TMP="$(fd_fresh)"
  # X311 ENFORCEMENT_ROW_COMPLETE (a) an empty What it can miss cell (AC-26)
  L="$(fd_py row_line "$TMP" enf-graph-lint)"
  fd_py row_sub "$TMP" enf-graph-lint '| It runs only when someone runs it or wires it into CI |' '|  |'
  # exercises: check_fd_enforcement_row_complete
  fd_expect "fd-enforcement-row (a)" "$(fd_at ENFORCEMENT_ROW_COMPLETE DOCUMENTATION.md "$L")" 'What it can miss'
  fd_restore DOCUMENTATION.md
  # X311 ENFORCEMENT_ROW_COMPLETE (b) a row with no enf- anchor
  fd_py insert_after "$TMP/DOCUMENTATION.md" '<a id="enf-ratchets"></a>' '| An unanchored mechanism | `install.sh` | **soft** | Something it misses | none |'
  L="$(fd_py line "$TMP/DOCUMENTATION.md" '| An unanchored mechanism |')"
  fd_expect "fd-enforcement-row (b)" "$(fd_at ENFORCEMENT_ROW_COMPLETE DOCUMENTATION.md "$L")" 'enf-'
  fd_restore DOCUMENTATION.md
  # X311 ENFORCEMENT_ROW_COMPLETE (c) a Class value outside the class set (AC-26)
  L="$(fd_py row_line "$TMP" enf-spec-lint)"
  fd_py row_sub "$TMP" enf-spec-lint '| **soft** |' '| **strong** |'
  fd_expect "fd-enforcement-row (c)" "$(fd_at ENFORCEMENT_ROW_COMPLETE DOCUMENTATION.md "$L")" 'strong'
  fd_restore DOCUMENTATION.md
  # X311 ENFORCEMENT_ROW_COMPLETE (d) an Artifact that does not resolve
  L="$(fd_py row_line "$TMP" enf-prose-lint)"
  fd_py row_sub "$TMP" enf-prose-lint '`tools/prose-lint.py`' '`tools/no-such.py`'
  fd_expect "fd-enforcement-row (d)" "$(fd_at ENFORCEMENT_ROW_COMPLETE DOCUMENTATION.md "$L")" 'tools/no-such.py'
  fd_restore DOCUMENTATION.md
  # X311 ENFORCEMENT_ROW_COMPLETE (e) a four-cell row
  L="$(fd_py row_line "$TMP" enf-grill-lint)"
  fd_py row_sub "$TMP" enf-grill-lint ' none |' ''
  fd_expect "fd-enforcement-row (e)" "$(fd_at ENFORCEMENT_ROW_COMPLETE DOCUMENTATION.md "$L")" 'cells'
  rm -rf "$TMP"
}

case_fd_enforcement_required_row() {
  local TMP; TMP="$(fd_fresh)"
  # X311 ENFORCEMENT_ROW_COMPLETE: the required enf-spec-before-code row deleted (AC-26)
  fd_py row_delete "$TMP" enf-spec-before-code
  # exercises: check_fd_enforcement_row_complete
  fd_expect "fd-enforcement-required-row" "$(fd_at ENFORCEMENT_ROW_COMPLETE DOCUMENTATION.md 0)" 'enf-spec-before-code'
  rm -rf "$TMP"
}

case_fd_enforcement_row_residuals() {
  local TMP L; TMP="$(fd_fresh)"
  # X329 ENFORCEMENT_ROW_COMPLETE (a) `role emulation` dropped from enf-tool-allowlist's miss cell (AC-26)
  L="$(fd_py row_line "$TMP" enf-tool-allowlist)"
  fd_py row_sub "$TMP" enf-tool-allowlist '; role emulation and an omitted `tools:` line both leave the list unread' '; an omitted `tools:` line leaves the list unread'
  # exercises: check_fd_enforcement_row_complete
  fd_expect "fd-row-residuals (a)" "$(fd_at ENFORCEMENT_ROW_COMPLETE DOCUMENTATION.md "$L")" 'enf-tool-allowlist' 'role emulation'
  fd_restore DOCUMENTATION.md
  # X329 ENFORCEMENT_ROW_COMPLETE (b) enf-leaf-cannot-spawn's Class reduced to **hard**
  L="$(fd_py row_line "$TMP" enf-leaf-cannot-spawn)"
  fd_py row_sub "$TMP" enf-leaf-cannot-spawn '**hard** where the host reads the tool list; **judgment** under role emulation' '**hard**'
  fd_expect "fd-row-residuals (b)" "$(fd_at ENFORCEMENT_ROW_COMPLETE DOCUMENTATION.md "$L")" 'enf-leaf-cannot-spawn' 'weakest class'
  fd_restore DOCUMENTATION.md
  # X329 ENFORCEMENT_ROW_COMPLETE (c) `fails open` dropped from enf-pre-bash-guard
  L="$(fd_py row_line "$TMP" enf-pre-bash-guard)"
  fd_py row_sub "$TMP" enf-pre-bash-guard 'It fails open on input it cannot parse, indirection' 'Indirection'
  fd_expect "fd-row-residuals (c)" "$(fd_at ENFORCEMENT_ROW_COMPLETE DOCUMENTATION.md "$L")" 'enf-pre-bash-guard' 'fail'
  fd_restore DOCUMENTATION.md
  # X329 ENFORCEMENT_ROW_COMPLETE (d) `.cypress/seed.json` dropped from enf-backup-before-replace
  L="$(fd_py row_line "$TMP" enf-backup-before-replace)"
  fd_py row_sub "$TMP" enf-backup-before-replace 'The install stamp `.cypress/seed.json` is replaced without a copy' 'One derived file is replaced without a copy'
  fd_expect "fd-row-residuals (d)" "$(fd_at ENFORCEMENT_ROW_COMPLETE DOCUMENTATION.md "$L")" 'enf-backup-before-replace' '.cypress/seed.json'
  fd_restore DOCUMENTATION.md
  # X329 ENFORCEMENT_ROW_COMPLETE (e) `Bash` dropped from enf-tool-allowlist
  L="$(fd_py row_line "$TMP" enf-tool-allowlist)"
  fd_py row_sub "$TMP" enf-tool-allowlist 'A role granted Bash can' 'A role granted a shell can'
  fd_expect "fd-row-residuals (e)" "$(fd_at ENFORCEMENT_ROW_COMPLETE DOCUMENTATION.md "$L")" 'enf-tool-allowlist' 'Bash'
  fd_restore DOCUMENTATION.md
  # X329 ENFORCEMENT_ROW_COMPLETE (f) a **hard** on enf-pre-bash-guard not scoped to a matched command on a host that fires the hook
  L="$(fd_py row_line "$TMP" enf-pre-bash-guard)"
  fd_py row_sub "$TMP" enf-pre-bash-guard '**hard** for a matched command on a host that fires the hook' '**hard** for every command'
  fd_expect "fd-row-residuals (f)" "$(fd_at ENFORCEMENT_ROW_COMPLETE DOCUMENTATION.md "$L")" 'enf-pre-bash-guard' 'hard'
  rm -rf "$TMP"
}

case_fd_mechanism_traced() {
  local TMP L; TMP="$(fd_fresh)"
  # X312 MECHANISM_CLAIMS_TRACED (a) an unlinked mechanism verb in README (AC-9)
  fd_py insert_before "$TMP/README.md" '## Why it is built this way' $'The gate enforces every spec before code.\n'
  L="$(fd_py line "$TMP/README.md" 'The gate enforces every spec before code.')"
  # exercises: check_fd_mechanism_claims_traced
  fd_expect "fd-mechanism-traced (a)" "$(fd_at MECHANISM_CLAIMS_TRACED README.md "$L")" 'enforces'
  fd_restore README.md
  # X312 MECHANISM_CLAIMS_TRACED (b) the same in INSTALL.md
  fd_py append "$TMP/INSTALL.md" $'\nThe gate enforces every spec before code.'
  L="$(fd_py line "$TMP/INSTALL.md" 'The gate enforces every spec before code.')"
  fd_expect "fd-mechanism-traced (b)" "$(fd_at MECHANISM_CLAIMS_TRACED INSTALL.md "$L")" 'enforces'
  fd_restore INSTALL.md
  # X312 MECHANISM_CLAIMS_TRACED (c) the same in an integration README stub
  fd_py append "$TMP/integrations/claude-code/README.md" $'\nThe gate enforces every spec before code.'
  L="$(fd_py line "$TMP/integrations/claude-code/README.md" 'The gate enforces every spec before code.')"
  fd_expect "fd-mechanism-traced (c)" "$(fd_at MECHANISM_CLAIMS_TRACED integrations/claude-code/README.md "$L")" 'enforces'
  fd_restore integrations/claude-code/README.md
  # X312 MECHANISM_CLAIMS_TRACED (d) the same in the `plant` Here field
  L="$(fd_py entry_line "$TMP" plant Here)"
  fd_py entry_field "$TMP" plant Here 'A repository after the [seed](#term-seed) was installed into it and [grown](#term-growth). The gate enforces every spec before code.'
  fd_expect "fd-mechanism-traced (d)" "$(fd_at MECHANISM_CLAIMS_TRACED DOCUMENTATION.md "$L")" 'enforces'
  fd_restore DOCUMENTATION.md
  # X312 MECHANISM_CLAIMS_TRACED (e) linked to a row that does not exist
  fd_py insert_before "$TMP/README.md" '## Why it is built this way' $'The gate [enforces](DOCUMENTATION.md#enf-no-such-row) every spec before code.\n'
  L="$(fd_py line "$TMP/README.md" '#enf-no-such-row')"
  fd_expect "fd-mechanism-traced (e)" "$(fd_at MECHANISM_CLAIMS_TRACED README.md "$L")" 'enf-no-such-row'
  fd_restore README.md
  # X312 MECHANISM_CLAIMS_TRACED (f) an unlinked `never` in INSTALL.md (AC-9, AC-16)
  fd_py append "$TMP/INSTALL.md" $'\nThe installer never merges a file.'
  L="$(fd_py line "$TMP/INSTALL.md" 'The installer never merges a file.')"
  fd_expect "fd-mechanism-traced (f)" "$(fd_at MECHANISM_CLAIMS_TRACED INSTALL.md "$L")" 'never'
  rm -rf "$TMP"
}

case_fd_mechanism_overclaim() {
  local TMP L KB; TMP="$(fd_fresh)"
  # X312 MECHANISM_CLAIMS_TRACED: "hard" linked only to the soft enf-kernel-budget row (AC-10, §8)
  KB="$(fd_py val "$TMP" KERNEL_BUDGET --grouped)"
  fd_py insert_before "$TMP/README.md" '## Why it is built this way' "The kernel sits under a hard ${KB}-byte [budget](DOCUMENTATION.md#enf-kernel-budget)."$'\n'
  L="$(fd_py line "$TMP/README.md" 'The kernel sits under a hard')"
  # exercises: check_fd_mechanism_claims_traced
  fd_expect "fd-mechanism-overclaim" "$(fd_at MECHANISM_CLAIMS_TRACED README.md "$L")" 'overclaim' 'enf-kernel-budget'
  rm -rf "$TMP"
}

case_fd_mechanism_surfaces() {
  local TMP L L2 L3; TMP="$(fd_fresh)"
  # X330 MECHANISM_CLAIMS_TRACED (a) a strong claim in INSTALL.md linking a row classed hard and judgment
  fd_py append "$TMP/INSTALL.md" $'\nThe harness blocks the tool for a leaf ([allowlist](DOCUMENTATION.md#enf-tool-allowlist)).'
  L="$(fd_py line "$TMP/INSTALL.md" 'The harness blocks the tool for a leaf')"
  # exercises: check_fd_mechanism_claims_traced
  fd_expect "fd-mechanism-surfaces (a)" "$(fd_at MECHANISM_CLAIMS_TRACED INSTALL.md "$L")" 'overclaim' 'judgment'
  fd_restore INSTALL.md
  # X330 MECHANISM_CLAIMS_TRACED (b) README "refuses" linked to a soft row
  fd_py insert_before "$TMP/README.md" '## Why it is built this way' $'The installer refuses a symlinked target ([install preflight](DOCUMENTATION.md#enf-install-preflight)).\n'
  L="$(fd_py line "$TMP/README.md" 'The installer refuses a symlinked target')"
  fd_expect "fd-mechanism-surfaces (b)" "$(fd_at MECHANISM_CLAIMS_TRACED README.md "$L")" 'overclaim'
  fd_restore README.md
  # X330 MECHANISM_CLAIMS_TRACED (c) a glossary Enforcement field says **hard** over a soft row
  fd_py entry_field "$TMP" kernel Enforcement '**hard** ([kernel budget](#enf-kernel-budget))'
  L="$(fd_py entry_line "$TMP" kernel Enforcement)"
  fd_expect "fd-mechanism-surfaces (c)" "$(fd_at MECHANISM_CLAIMS_TRACED DOCUMENTATION.md "$L")" 'hard'
  fd_restore DOCUMENTATION.md
  # X330 MECHANISM_CLAIMS_TRACED (d) a class no linked row's Class cell holds ...
  fd_py entry_field "$TMP" kernel Enforcement '**detective** ([kernel budget](#enf-kernel-budget))'
  L="$(fd_py entry_line "$TMP" kernel Enforcement)"
  fd_expect "fd-mechanism-surfaces (d1)" "$(fd_at MECHANISM_CLAIMS_TRACED DOCUMENTATION.md "$L")" 'detective'
  fd_restore DOCUMENTATION.md
  # ... and a class other than not a control with no enf- link
  fd_py entry_field "$TMP" node Enforcement '**soft**'
  L="$(fd_py entry_line "$TMP" node Enforcement)"
  fd_expect "fd-mechanism-surfaces (d2)" "$(fd_at MECHANISM_CLAIMS_TRACED DOCUMENTATION.md "$L")" 'enf-'
  fd_restore DOCUMENTATION.md
  # X330 MECHANISM_CLAIMS_TRACED (e) a strong claim in the manual outside the glossary linking a soft row
  fd_py insert_after "$TMP/DOCUMENTATION.md" '## 16. Contributing to the seed' $'\nThe installer refuses a symlinked target ([install preflight](#enf-install-preflight)).'
  L="$(fd_py line "$TMP/DOCUMENTATION.md" 'The installer refuses a symlinked target')"
  fd_expect "fd-mechanism-surfaces (e)" "$(fd_at MECHANISM_CLAIMS_TRACED DOCUMENTATION.md "$L")" 'overclaim'
  fd_restore DOCUMENTATION.md
  # X330 MECHANISM_CLAIMS_TRACED (f) README calls enf-pre-bash-guard a security guard (AC-26)
  fd_py insert_before "$TMP/README.md" '## Why it is built this way' $'A shell command meets the security guard first ([command guard](DOCUMENTATION.md#enf-pre-bash-guard)).\n'
  L="$(fd_py line "$TMP/README.md" 'meets the security guard first')"
  fd_expect "fd-mechanism-surfaces (f)" "$(fd_at MECHANISM_CLAIMS_TRACED README.md "$L")" 'enf-pre-bash-guard' 'secur'
  fd_restore README.md
  # X330 MECHANISM_CLAIMS_TRACED (g) `sandbox` in an INSTALL.md unit linking enf-pre-bash-guard
  fd_py append "$TMP/INSTALL.md" $'\nShell commands run in a sandbox ([command guard](DOCUMENTATION.md#enf-pre-bash-guard)).'
  L="$(fd_py line "$TMP/INSTALL.md" 'Shell commands run in a sandbox')"
  fd_expect "fd-mechanism-surfaces (g)" "$(fd_at MECHANISM_CLAIMS_TRACED INSTALL.md "$L")" 'sandbox'
  fd_restore INSTALL.md
  # X330 MECHANISM_CLAIMS_TRACED (h) passes: two negated strong words, and an
  # unlinked strong claim in a reference (§7 STRONG_CLAIM_IN_MANUAL_PROSE)
  fd_py insert_before "$TMP/README.md" '## Why it is built this way' $'No tool blocks code written before its spec ([spec before code](DOCUMENTATION.md#enf-spec-before-code)).\n\nNothing here is hard ([tier classification](DOCUMENTATION.md#enf-tier-classification)).\n'
  fd_py append "$TMP/documentation/agents-reference.md" $'\nThe router blocks a wrong route.'
  L="$(fd_py line "$TMP/README.md" 'No tool blocks code written before its spec')"
  L2="$(fd_py line "$TMP/README.md" 'Nothing here is hard')"
  L3="$(fd_py line "$TMP/documentation/agents-reference.md" 'The router blocks a wrong route.')"
  fd_expect_absent "fd-mechanism-surfaces (h) README" "$(fd_at MECHANISM_CLAIMS_TRACED README.md "$L" "$L2")"
  fd_expect_absent "fd-mechanism-surfaces (h) reference" "$(fd_at MECHANISM_CLAIMS_TRACED documentation/agents-reference.md "$L3")"
  rm -rf "$TMP"
}

case_fd_hook_firing() {
  local TMP L; TMP="$(fd_fresh)"
  # X313 ENFORCEMENT_ROW_COMPLETE (a) enf-route-hook classed **hard** (AC-27)
  L="$(fd_py row_line "$TMP" enf-route-hook)"
  fd_py row_sub "$TMP" enf-route-hook '**not a control**' '**hard**'
  # exercises: check_fd_enforcement_row_complete
  fd_expect "fd-hook-firing (a)" "$(fd_at ENFORCEMENT_ROW_COMPLETE DOCUMENTATION.md "$L")" 'enf-route-hook' 'not a control'
  fd_restore DOCUMENTATION.md
  # X313 ENFORCEMENT_ROW_COMPLETE (b) `not a control` removed from the matrix row's ADR-0003 cell (AC-27, P9)
  L="$(fd_py line "$TMP/documentation/host-capability-matrix.md" '| **mechanically enforced** |')"
  fd_py sub "$TMP/documentation/host-capability-matrix.md" '`hard`; `not a control` for a hook that only injects text |' '`hard` |'
  fd_expect "fd-hook-firing (b)" "$(fd_at ENFORCEMENT_ROW_COMPLETE documentation/host-capability-matrix.md "$L")" 'not a control'
  fd_restore documentation/host-capability-matrix.md
  # X313 ENFORCEMENT_ROW_COMPLETE (c) `injects` removed from that row's Meaning cell
  fd_py sub "$TMP/documentation/host-capability-matrix.md" ' A hook that only injects text into the context fires and holds nothing. |' ' |'
  fd_expect "fd-hook-firing (c)" "$(fd_at ENFORCEMENT_ROW_COMPLETE documentation/host-capability-matrix.md "$L")" 'injects'
  fd_restore documentation/host-capability-matrix.md
  # X313 ENFORCEMENT_ROW_COMPLETE (d) enf-status-hook classed **soft**
  L="$(fd_py row_line "$TMP" enf-status-hook)"
  fd_py row_sub "$TMP" enf-status-hook '**not a control**' '**soft**'
  fd_expect "fd-hook-firing (d)" "$(fd_at ENFORCEMENT_ROW_COMPLETE DOCUMENTATION.md "$L")" 'enf-status-hook' 'not a control'
  rm -rf "$TMP"
}

case_fd_limits_hard_row() {
  local TMP L; TMP="$(fd_fresh)"
  # X314 LIMITS_SECTION_PRESENT (a) a Requested item linking only a hard row (AC-11)
  fd_py insert_after "$TMP/README.md" '(DOCUMENTATION.md#enf-test-before-code)).' '- The kernel file loads at session start ([kernel load](DOCUMENTATION.md#enf-kernel-load)).'
  L="$(fd_py line "$TMP/README.md" '#enf-kernel-load')"
  # exercises: check_fd_limits_section_present
  fd_expect "fd-limits-hard-row (a)" "$(fd_at LIMITS_SECTION_PRESENT README.md "$L")" 'hard'
  fd_restore README.md
  # X314 LIMITS_SECTION_PRESENT (b) a Requested item linking no row (AC-11)
  fd_py insert_after "$TMP/README.md" '(DOCUMENTATION.md#enf-test-before-code)).' '- Reading the plan first is asked of the model.'
  L="$(fd_py line "$TMP/README.md" 'Reading the plan first is asked of the model.')"
  fd_expect "fd-limits-hard-row (b)" "$(fd_at LIMITS_SECTION_PRESENT README.md "$L")" 'enf-'
  rm -rf "$TMP"
}

case_fd_limits_required_rows() {
  local TMP; TMP="$(fd_fresh)"
  # X314 LIMITS_SECTION_PRESENT (a) the enf-test-before-code link dropped (AC-11)
  fd_py sub "$TMP/README.md" '([test before code](DOCUMENTATION.md#enf-test-before-code))' '([checks before done](DOCUMENTATION.md#enf-verify-gates))'
  # exercises: check_fd_limits_section_present
  fd_expect "fd-limits-required-rows (a)" "$(fd_at LIMITS_SECTION_PRESENT README.md)" 'enf-test-before-code'
  fd_restore README.md
  # X314 LIMITS_SECTION_PRESENT (b) the two subsections swapped
  fd_py swap "$TMP/README.md" '### Requested, not enforced' '### Not yet measured'
  fd_expect "fd-limits-required-rows (b)" "$(fd_at LIMITS_SECTION_PRESENT README.md)" 'Requested, not enforced'
  rm -rf "$TMP"
}

case_fd_limits_unmeasured() {
  local TMP L; TMP="$(fd_fresh)"
  # X314 LIMITS_SECTION_PRESENT: a Not-yet-measured item with none of the three phrases
  fd_py insert_after "$TMP/README.md" '- The cost of the one-time setup session: not recorded.' '- Install time on a large monorepo.'
  L="$(fd_py line "$TMP/README.md" 'Install time on a large monorepo.')"
  # exercises: check_fd_limits_section_present
  fd_expect "fd-limits-unmeasured" "$(fd_at LIMITS_SECTION_PRESENT README.md "$L")" 'not measured'
  rm -rf "$TMP"
}

case_fd_catalogs() {
  local TMP NAMES; TMP="$(fd_fresh)"
  # X315 CATALOGS_OUT_OF_README: every agent name in a code span in README (AC-12)
  NAMES="$(fd_py agent_names "$TMP")"
  fd_py insert_before "$TMP/README.md" '## Why it is built this way' "The roster: ${NAMES}."$'\n'
  # exercises: check_fd_catalogs_out_of_readme
  fd_expect "fd-catalogs" "$(fd_at CATALOGS_OUT_OF_README README.md)" 'agents'
  rm -rf "$TMP"
}

case_fd_adr_range() {
  local TMP L; TMP="$(fd_fresh)"
  # X315 CATALOGS_OUT_OF_README: an ADR range in INSTALL.md
  fd_py append "$TMP/INSTALL.md" $'\nThe decisions are ADR-0001 to ADR-0010.'
  L="$(fd_py line "$TMP/INSTALL.md" 'ADR-0001 to ADR-0010')"
  # exercises: check_fd_catalogs_out_of_readme
  fd_expect "fd-adr-range" "$(fd_at CATALOGS_OUT_OF_README INSTALL.md "$L")" 'ADR-0001 to ADR-0010'
  rm -rf "$TMP"
}

case_fd_cost_scope() {
  local TMP L KB; TMP="$(fd_fresh)"
  # X316 COST_FIGURES_SCOPED: a derived limit figure with no scope marker
  KB="$(fd_py val "$TMP" KERNEL_BUDGET --grouped)"
  fd_py insert_after "$TMP/README.md" '| 11% more tokens |' "| ${KB}-byte limit | the size limit for the kernel file |"
  L="$(fd_py line "$TMP/README.md" "| ${KB}-byte limit |")"
  # exercises: check_fd_cost_figures_scoped
  fd_expect "fd-cost-scope" "$(fd_at COST_FIGURES_SCOPED README.md "$L")" 'scope'
  rm -rf "$TMP"
}

case_fd_cost_provenance() {
  local TMP L; TMP="$(fd_fresh)"
  # X316 COST_FIGURES_SCOPED (a) a kernel byte figure nothing derives (AC-13)
  fd_py insert_after "$TMP/README.md" '| 11% more tokens |' '| 7 742 bytes | per session, the kernel file on Claude Code |'
  L="$(fd_py line "$TMP/README.md" '| 7 742 bytes |')"
  # exercises: check_fd_cost_figures_scoped
  fd_expect "fd-cost-provenance (a)" "$(fd_at COST_FIGURES_SCOPED README.md "$L")" '7 742'
  fd_restore README.md
  # X316 COST_FIGURES_SCOPED (b) a range with no evidence link (AC-13)
  fd_py insert_after "$TMP/README.md" '| 11% more tokens |' '| 10 to 20% more tokens | per task, on small tasks |'
  L="$(fd_py line "$TMP/README.md" '| 10 to 20% more tokens |')"
  fd_expect "fd-cost-provenance (b)" "$(fd_at COST_FIGURES_SCOPED README.md "$L")" '20%'
  rm -rf "$TMP"
}

case_fd_cost_measured_derived() {
  local TMP L KB; TMP="$(fd_fresh)"
  # X316 COST_FIGURES_SCOPED (a) a derived budget figure called measured (§7 MEASURED_WORD_ON_A_DERIVED_FIGURE)
  KB="$(fd_py val "$TMP" KERNEL_BUDGET --grouped)"
  fd_py insert_after "$TMP/README.md" '| 11% more tokens |' "| the ${KB}-byte budget | per session, measured |"
  L="$(fd_py line "$TMP/README.md" "| the ${KB}-byte budget |")"
  # exercises: check_fd_cost_figures_scoped
  fd_expect "fd-cost-measured-derived (a)" "$(fd_at COST_FIGURES_SCOPED README.md "$L")" 'measured'
  fd_restore README.md
  # X316 COST_FIGURES_SCOPED (b) the pre-harvest lead-in above the derived row (AC-14)
  fd_py insert_before "$TMP/README.md" '| Figure | What it covers and how it was obtained |' $'The running cost, measured rather than estimated:\n'
  L="$(fd_py line "$TMP/README.md" 'measured rather than estimated')"
  fd_expect "fd-cost-measured-derived (b)" "$(fd_at COST_FIGURES_SCOPED README.md "$L")" 'measured'
  rm -rf "$TMP"
}

case_fd_cost_no_derived() {
  local TMP V; TMP="$(fd_fresh)"
  # X331 COST_FIGURES_SCOPED: the cost section's only derived figure replaced by `not measured`
  V="$(fd_py val "$TMP" EAGER_CLAUDE_CODE)"
  fd_py sub "$TMP/README.md" "| ${V} bytes |" '| not measured |'
  # exercises: check_fd_cost_figures_scoped
  fd_expect "fd-cost-no-derived" "$(fd_at COST_FIGURES_SCOPED README.md 0)" 'derived'
  rm -rf "$TMP"
}

case_fd_measured_evidence() {
  local TMP L; TMP="$(fd_fresh)"
  # X317 COST_FIGURES_SCOPED: a measured range linked to a record holding 11% (§7 EVIDENCE_DISAGREES, AC-13)
  fd_py sub "$TMP/README.md" '| 11% more tokens |' '| 10 to 20% more tokens |'
  L="$(fd_py line "$TMP/README.md" '| 10 to 20% more tokens |')"
  # exercises: check_fd_cost_figures_scoped
  fd_expect "fd-measured-evidence" "$(fd_at COST_FIGURES_SCOPED README.md "$L")" '10%' 'docs/plans/front-door-evidence.md'
  rm -rf "$TMP"
}

case_fd_eager_published() {
  local TMP L S; TMP="$(fd_fresh)"
  S="$(fd_py stale "$TMP")"
  # X318 EAGER_FIGURES_CHECKED_WHEREVER_PUBLISHED (a) an always-loaded figure nothing computes, in a reference (AC-17)
  fd_py append "$TMP/documentation/agents-reference.md" $'\n'"The always-loaded surface is ${S} bytes per session."
  L="$(fd_py line "$TMP/documentation/agents-reference.md" "The always-loaded surface is ${S} bytes")"
  # exercises: check_fd_eager_figures_checked_wherever_published
  fd_expect "fd-eager-published (a)" "$(fd_at EAGER_FIGURES_CHECKED_WHEREVER_PUBLISHED documentation/agents-reference.md "$L")"
  fd_restore documentation/agents-reference.md
  # X318 EAGER_FIGURES_CHECKED_WHEREVER_PUBLISHED (b) the same in INSTALL.md
  fd_py append "$TMP/INSTALL.md" $'\n'"The always-loaded surface is ${S} bytes per session."
  L="$(fd_py line "$TMP/INSTALL.md" "The always-loaded surface is ${S} bytes")"
  fd_expect "fd-eager-published (b)" "$(fd_at EAGER_FIGURES_CHECKED_WHEREVER_PUBLISHED INSTALL.md "$L")"
  fd_restore INSTALL.md
  # X318 EAGER_FIGURES_CHECKED_WHEREVER_PUBLISHED (c) the slug forced into the
  # ledger and a stale figure in README: README is never pending (binding values)
  fd_bind
  fd_py ledger "$TMP" EAGER_FIGURES_CHECKED_WHEREVER_PUBLISHED
  fd_py insert_after "$TMP/README.md" '| 11% more tokens |' "| ${S} bytes | per session on Codex, computed from the installed files |"
  L="$(fd_py line "$TMP/README.md" "| ${S} bytes |")"
  fd_expect "fd-eager-published (c)" "$(fd_at EAGER_FIGURES_CHECKED_WHEREVER_PUBLISHED README.md "$L")"
  fd_expect_none "fd-eager-published (c)" 'front-door: PENDING EAGER_FIGURES_CHECKED_WHEREVER_PUBLISHED'
  rm -rf "$TMP"
}

case_fd_body_home() {
  local TMP L; TMP="$(fd_fresh)"
  # X319 BODY_FIGURES_HAVE_A_REQUIRED_HOME (a) the median dropped from the body-figure paragraph (AC-17)
  fd_py sub_re "$TMP/DOCUMENTATION.md" ' and the median routable body is [0-9]+ lines' ''
  # exercises: check_fd_body_figures_have_a_required_home
  fd_expect "fd-body-home (a)" "$(fd_at BODY_FIGURES_HAVE_A_REQUIRED_HOME DOCUMENTATION.md 0)" 'median'
  fd_restore DOCUMENTATION.md
  # X319 BODY_FIGURES_HAVE_A_REQUIRED_HOME (b) the whole paragraph removed
  fd_py del_line "$TMP/DOCUMENTATION.md" 'Routable body sizes, computed by'
  fd_expect "fd-body-home (b)" "$(fd_at BODY_FIGURES_HAVE_A_REQUIRED_HOME DOCUMENTATION.md 0)" 'largest'
  fd_restore DOCUMENTATION.md
  # X319 BODY_FIGURES_HAVE_A_REQUIRED_HOME (c) "consequently **empty**" in INSTALL.md while an exemption is recorded
  fd_py exemption "$TMP"
  fd_py append "$TMP/INSTALL.md" $'\nEAGER_EXEMPTIONS is consequently **empty**.'
  L="$(fd_py line "$TMP/INSTALL.md" 'is consequently **empty**')"
  fd_expect "fd-body-home (c)" "$(fd_at BODY_FIGURES_HAVE_A_REQUIRED_HOME INSTALL.md "$L")" 'consequently'
  rm -rf "$TMP"
}

case_fd_body_figure_elsewhere() {
  local TMP L; TMP="$(fd_fresh)"
  # X319 BODY_FIGURES_HAVE_A_REQUIRED_HOME: a body line figure outside its home (AC-17)
  fd_py append "$TMP/INSTALL.md" $'\nThe largest body is 1 384 lines.'
  L="$(fd_py line "$TMP/INSTALL.md" 'The largest body is 1 384 lines.')"
  # exercises: check_fd_body_figures_have_a_required_home
  fd_expect "fd-body-figure-elsewhere" "$(fd_at BODY_FIGURES_HAVE_A_REQUIRED_HOME INSTALL.md "$L")" '1 384'
  rm -rf "$TMP"
}

case_fd_body_project_node() {
  local TMP L; TMP="$(fd_fresh)"
  # X332 BODY_FIGURES_HAVE_A_REQUIRED_HOME (b) a project-node figure outside PROJECT_NODE_LINE_FIGURES
  fd_py append "$TMP/documentation/skills-and-templates-reference.md" $'\nThe project-node body ceiling is ~151 lines.'
  L="$(fd_py line "$TMP/documentation/skills-and-templates-reference.md" 'The project-node body ceiling is ~151 lines.')"
  # exercises: check_fd_body_figures_have_a_required_home
  fd_expect "fd-body-project-node (b)" "$(fd_at BODY_FIGURES_HAVE_A_REQUIRED_HOME documentation/skills-and-templates-reference.md "$L")" '151'
  fd_restore documentation/skills-and-templates-reference.md
  # X332 BODY_FIGURES_HAVE_A_REQUIRED_HOME (a) passes: the project-node ceiling, ~150 lines
  fd_py append "$TMP/documentation/skills-and-templates-reference.md" $'\nThe project-node body ceiling is ~150 lines.'
  L="$(fd_py line "$TMP/documentation/skills-and-templates-reference.md" 'The project-node body ceiling is ~150 lines.')"
  fd_expect_absent "fd-body-project-node (a)" "$(fd_at BODY_FIGURES_HAVE_A_REQUIRED_HOME documentation/skills-and-templates-reference.md "$L")"
  fd_restore documentation/skills-and-templates-reference.md
  # X332 BODY_FIGURES_HAVE_A_REQUIRED_HOME (c) the 150 literal gone from graph-lint.py: the exemption cannot outlive it
  fd_py unliteral "$TMP" 150
  fd_expect "fd-body-project-node (c)" "$(fd_at BODY_FIGURES_HAVE_A_REQUIRED_HOME templates/knowledge-graph/graph-lint.py 0)" '150'
  rm -rf "$TMP"
}

case_fd_anchor_resolves() {
  local TMP L; TMP="$(fd_fresh)"
  # X320 FRONT_DOOR_ANCHORS_RESOLVE (a) a term fragment that names no anchor (AC-25)
  fd_py sub "$TMP/README.md" '(DOCUMENTATION.md#term-plant)' '(DOCUMENTATION.md#term-plnat)'
  L="$(fd_py line "$TMP/README.md" '#term-plnat')"
  # exercises: check_fd_front_door_anchors_resolve
  fd_expect "fd-anchor-resolves (a)" "$(fd_at FRONT_DOOR_ANCHORS_RESOLVE README.md "$L")" 'term-plnat'
  fd_restore README.md
  # X320 FRONT_DOOR_ANCHORS_RESOLVE (b) a relative link to a file that does not exist
  fd_py sub "$TMP/README.md" 'lists them with their status.' 'lists them with their status; the [design notes](docs/no-such.md) are older.'
  L="$(fd_py line "$TMP/README.md" '(docs/no-such.md)')"
  fd_expect "fd-anchor-resolves (b)" "$(fd_at FRONT_DOOR_ANCHORS_RESOLVE README.md "$L")" 'docs/no-such.md'
  rm -rf "$TMP"
}

case_fd_anchor_duplicate() {
  local TMP L; TMP="$(fd_fresh)"
  # X320 FRONT_DOOR_ANCHORS_RESOLVE: a second explicit anchor with the id term-plant
  fd_py insert_after "$TMP/DOCUMENTATION.md" '## 16. Contributing to the seed' $'\n<a id="term-plant"></a>'
  L="$(fd_py line "$TMP/DOCUMENTATION.md" '<a id="term-plant"></a>' 2)"
  # exercises: check_fd_front_door_anchors_resolve
  fd_expect "fd-anchor-duplicate" "$(fd_at FRONT_DOOR_ANCHORS_RESOLVE DOCUMENTATION.md "$L")" 'term-plant'
  rm -rf "$TMP"
}

case_fd_headings() {
  local TMP L; TMP="$(fd_fresh)"
  # X321 FRONT_DOOR_HEADINGS_WELL_FORMED (a) #### directly under ## in README
  fd_py insert_after "$TMP/README.md" '## Why it is built this way' $'\n#### A detail'
  L="$(fd_py line "$TMP/README.md" '#### A detail')"
  # exercises: check_fd_front_door_headings_well_formed
  fd_expect "fd-headings (a)" "$(fd_at FRONT_DOOR_HEADINGS_WELL_FORMED README.md "$L")" 'level'
  fd_restore README.md
  # X321 FRONT_DOOR_HEADINGS_WELL_FORMED (b) a second # heading in DOCUMENTATION
  fd_py insert_after "$TMP/DOCUMENTATION.md" '## 16. Contributing to the seed' $'\n# A second title\n'
  L="$(fd_py line "$TMP/DOCUMENTATION.md" '# A second title')"
  fd_expect "fd-headings (b)" "$(fd_at FRONT_DOOR_HEADINGS_WELL_FORMED DOCUMENTATION.md "$L")" 'level-1'
  fd_restore DOCUMENTATION.md
  # X321 FRONT_DOOR_HEADINGS_WELL_FORMED (c) a reference whose first heading is ##
  fd_py sub "$TMP/documentation/agents-reference.md" '# CYPRESS specialist agents' '## CYPRESS specialist agents'
  L="$(fd_py line "$TMP/documentation/agents-reference.md" '## CYPRESS specialist agents')"
  fd_expect "fd-headings (c)" "$(fd_at FRONT_DOOR_HEADINGS_WELL_FORMED documentation/agents-reference.md "$L")" 'level-1'
  rm -rf "$TMP"
}

case_fd_link_text() {
  local TMP L; TMP="$(fd_fresh)"
  # X322 LINK_TEXT_STANDS_ALONE (a) a generic link text in README
  fd_py insert_after "$TMP/README.md" '- [Install guide](INSTALL.md)' '- [here](INSTALL.md)'
  L="$(fd_py line "$TMP/README.md" '- [here](INSTALL.md)')"
  # exercises: check_fd_link_text_stands_alone
  fd_expect "fd-link-text (a)" "$(fd_at LINK_TEXT_STANDS_ALONE README.md "$L")" 'here'
  fd_restore README.md
  # X322 LINK_TEXT_STANDS_ALONE (b) a bare URL as link text in the enforcement region (AC-20)
  L="$(fd_py row_line "$TMP" enf-graph-lint)"
  fd_py row_sub "$TMP" enf-graph-lint ' none |' ' [https://example.org](https://example.org) |'
  fd_expect "fd-link-text (b)" "$(fd_at LINK_TEXT_STANDS_ALONE DOCUMENTATION.md "$L")" 'https://'
  fd_restore DOCUMENTATION.md
  # X322 LINK_TEXT_STANDS_ALONE (c) an empty link text in README
  fd_py insert_after "$TMP/README.md" '- [Install guide](INSTALL.md)' '- [](INSTALL.md)'
  L="$(fd_py line "$TMP/README.md" '- [](INSTALL.md)')"
  fd_expect "fd-link-text (c)" "$(fd_at LINK_TEXT_STANDS_ALONE README.md "$L")" 'empty'
  rm -rf "$TMP"
}

case_fd_table_header() {
  local TMP L; TMP="$(fd_fresh)"
  L="$(fd_py line "$TMP/README.md" '| Figure | What it covers and how it was obtained |')"
  # X323 TABLES_HAVE_HEADER_ROWS (a) a README table whose header cells are all blank (AC-21)
  fd_py sub "$TMP/README.md" '| Figure | What it covers and how it was obtained |' '|  |  |'
  # exercises: check_fd_tables_have_header_rows
  fd_expect "fd-table-header (a)" "$(fd_at TABLES_HAVE_HEADER_ROWS README.md "$L")" 'header'
  fd_restore README.md
  # X323 TABLES_HAVE_HEADER_ROWS (b) a header cell holding only ** (AC-21)
  fd_py sub "$TMP/README.md" '| Figure | What it covers and how it was obtained |' '| ** | What it covers and how it was obtained |'
  fd_expect "fd-table-header (b)" "$(fd_at TABLES_HAVE_HEADER_ROWS README.md "$L")" 'header'
  rm -rf "$TMP"
}

case_fd_pending_stale() {
  local TMP; TMP="$(fd_fresh)"
  # X324 PENDING_LEDGER_HOLDS_ONLY_FAILING_CONTRACTS: a member whose check passes on the conforming fixture
  fd_bind
  fd_py ledger "$TMP" LINK_TEXT_STANDS_ALONE
  # exercises: check_fd_pending_ledger_holds_only_failing_contracts
  fd_expect "fd-pending-stale" "$(fd_at PENDING_LEDGER_HOLDS_ONLY_FAILING_CONTRACTS tests/seed-lint.py)" 'stale pending entry: remove it' 'LINK_TEXT_STANDS_ALONE'
  rm -rf "$TMP"
}

case_fd_pending_unknown_slug() {
  local TMP PL; TMP="$(fd_fresh)"
  PL="$(fd_at PENDING_LEDGER_HOLDS_ONLY_FAILING_CONTRACTS tests/seed-lint.py)"
  fd_bind
  # X324 PENDING_LEDGER_HOLDS_ONLY_FAILING_CONTRACTS (a) a member that is no contract slug
  fd_py ledger "$TMP" NOT_A_CONTRACT
  # exercises: check_fd_pending_ledger_holds_only_failing_contracts
  fd_expect "fd-pending-unknown-slug (a)" "$PL" 'NOT_A_CONTRACT' '!stale pending entry'
  # X324 PENDING_LEDGER_HOLDS_ONLY_FAILING_CONTRACTS (b) the contract's own slug
  fd_py ledger "$TMP" PENDING_LEDGER_HOLDS_ONLY_FAILING_CONTRACTS
  fd_expect "fd-pending-unknown-slug (b)" "$PL" 're:PENDING_LEDGER_HOLDS_ONLY_FAILING_CONTRACTS.*PENDING_LEDGER_HOLDS_ONLY_FAILING_CONTRACTS' '!stale pending entry'
  # X324 PENDING_LEDGER_HOLDS_ONLY_FAILING_CONTRACTS (c) PROSE_FLOOR_HELD_PER_FILE, which seed-lint does not check
  fd_py ledger "$TMP" PROSE_FLOOR_HELD_PER_FILE
  fd_expect "fd-pending-unknown-slug (c)" "$PL" 'PROSE_FLOOR_HELD_PER_FILE' '!stale pending entry'
  # X324 PENDING_LEDGER_HOLDS_ONLY_FAILING_CONTRACTS (d) a genuinely failing member tests/ratchets.json does not mirror
  fd_py ledger "$TMP"
  fd_py ledger "$TMP" --no-mirror LINK_TEXT_STANDS_ALONE
  fd_py insert_after "$TMP/README.md" '- [Install guide](INSTALL.md)' '- [here](INSTALL.md)'
  fd_expect "fd-pending-unknown-slug (d)" "$PL" 'tests/ratchets.json'
  rm -rf "$TMP"
}

case_fd_pending_holds_exit() {
  local TMP MEMBERS M N; TMP="$(fresh)"
  # X324 PENDING_LEDGER_HOLDS_ONLY_FAILING_CONTRACTS, §7 FIXTURE_ONLY_COVERAGE:
  # the real-tree copy, no fixture. (a) ledger intact: exit 0, one PENDING line
  # per member, no stale entry.
  fd_bind
  MEMBERS="$(fd_py ledger_members "$TMP")"
  fd_lint_full
  fd_refuse_raised "fd-pending-holds-exit (a)"
  # exercises: check_fd_pending_ledger_holds_only_failing_contracts
  [ "$FD_RC" -eq 0 ] || { echo "[fd-pending-holds-exit (a)] expected exit 0 with the ledger intact, got $FD_RC" >&2; echo "$FD_OUT" >&2; exit 1; }
  fd_expect_none "fd-pending-holds-exit (a)" 'stale pending entry'
  N="$(grep -cE '^.*front-door: PENDING [A-Z_]+: [0-9]+ finding\(s\); first: ' <<<"$FD_OUT" || true)"
  [ "$N" -eq "$(printf '%s\n' $MEMBERS | grep -c . || true)" ] || {
    echo "[fd-pending-holds-exit (a)] $N PENDING lines for ledger {$MEMBERS}" >&2; fd_show; exit 1; }
  for M in $MEMBERS; do
    [ "$(grep -cE "front-door: PENDING ${M}: [0-9]+ finding\\(s\\); first: " <<<"$FD_OUT" || true)" -eq 1 ] || {
      echo "[fd-pending-holds-exit (a)] not exactly one PENDING line for $M" >&2; fd_show; exit 1; }
  done
  # (b) ledger emptied: exit 1, and a finding line for every former member
  if [ -n "$MEMBERS" ]; then
    fd_py ledger "$TMP"
    fd_lint_full
    fd_refuse_raised "fd-pending-holds-exit (b)"
    [ "$FD_RC" -eq 1 ] || { echo "[fd-pending-holds-exit (b)] expected exit 1 with the ledger emptied, got $FD_RC" >&2; exit 1; }
    for M in $MEMBERS; do
      grep -qE "front-door: ${M}: [^ :]+:[0-9]+: " <<<"$FD_OUT" || {
        echo "[fd-pending-holds-exit (b)] no finding line for former member $M" >&2; fd_show; exit 1; }
    done
  fi
  rm -rf "$TMP"
}

case_fd_pending_implemented() {
  local TMP; TMP="$(fd_fresh)"
  # X333 PENDING_LEDGER_HOLDS_ONLY_FAILING_CONTRACTS, §7 LEDGER_REGROWS_AFTER_IMPLEMENTED (AC-28):
  # the spec `implemented`, a genuinely failing slug re-added to the ledger and
  # its ratchets.json mirror in one edit
  fd_bind implemented 7.28.0
  fd_py ledger "$TMP" LINK_TEXT_STANDS_ALONE
  fd_py insert_after "$TMP/README.md" '- [Install guide](INSTALL.md)' '- [here](INSTALL.md)'
  # exercises: check_fd_pending_ledger_holds_only_failing_contracts
  fd_expect "fd-pending-implemented" "$(fd_at PENDING_LEDGER_HOLDS_ONLY_FAILING_CONTRACTS tests/seed-lint.py)" 'ledger must be empty once SPEC-0004 is implemented'
  fd_ratchet_accepts "fd-pending-implemented"
  rm -rf "$TMP"
}

case_fd_pending_release() {
  local TMP V PL; TMP="$(fd_fresh)"
  PL="$(fd_at PENDING_LEDGER_HOLDS_ONLY_FAILING_CONTRACTS tests/seed-lint.py)"
  # X335 PENDING_LEDGER_HOLDS_ONLY_FAILING_CONTRACTS, §7 RELEASE_WITH_PENDING_LEDGER (AC-28, press P4):
  # spec `active`, one genuinely failing slug pending, the manifest version varied
  fd_py bind "$TMP" status active
  fd_py ledger "$TMP" LINK_TEXT_STANDS_ALONE
  fd_py insert_after "$TMP/README.md" '- [Install guide](INSTALL.md)' '- [here](INSTALL.md)'
  # (a) 7.29.0 and (b) 7.100.0: refused; an integer-tuple comparison, not a string one
  for V in 7.29.0 7.100.0; do
    fd_py bind "$TMP" version "$V"
    # exercises: check_fd_pending_ledger_holds_only_failing_contracts
    fd_expect "fd-pending-release ($V)" "$PL" 'ledger must be empty from 7.29.0'
    fd_expect_none "fd-pending-release ($V)" 'ledger must be empty once'
  done
  # (c) 7.28.0 and (d) 7.9.0 pass: no release refusal and the one PENDING line.
  # Their exit code is evidence only from increment 5 (SPEC-0004 §10).
  for V in 7.28.0 7.9.0; do
    fd_py bind "$TMP" version "$V"
    fd_lint
    fd_refuse_raised "fd-pending-release ($V)"
    fd_expect_none "fd-pending-release ($V)" 'ledger must be empty from'
    [ "$(grep -cF 'front-door: PENDING LINK_TEXT_STANDS_ALONE: ' <<<"$FD_OUT" || true)" -eq 1 ] || {
      echo "[fd-pending-release ($V)] expected exactly one PENDING LINK_TEXT_STANDS_ALONE line" >&2; fd_show; exit 1; }
  done
  rm -rf "$TMP"
}

case_fd_absent_inputs() {
  local TMP ROW SLUG FILE FRAG; TMP="$(fd_fresh)"
  # X326 §7 VACUOUS_PASS_ON_ABSENT_TEXT: README cut to its # title, and
  # DOCUMENTATION without regions 15 and 17. Every slug whose §6 required input
  # is gone reports it at line 0, by name.
  fd_py cut "$TMP"
  fd_lint
  fd_refuse_raised "fd-absent-inputs"
  [ "$FD_RC" -eq 1 ] || { echo "[fd-absent-inputs] expected exit 1, got $FD_RC" >&2; exit 1; }
  for ROW in \
      'FIRST_SCREEN_ORDER|README.md|heading' \
      'INSTALL_SECTION_NAMES_TARGET_PATHS|README.md|What installing does to your repository' \
      'WHERE_NEXT_LINKS_THE_REFERENCES|README.md|Where to go next' \
      'LIMITS_SECTION_PRESENT|README.md|What it does not do' \
      'COST_FIGURES_SCOPED|README.md|What it costs' \
      'GLOSSARY_ENTRY_COMPLETE|DOCUMENTATION.md|glossary' \
      'GLOSSARY_PATHS_EXIST|DOCUMENTATION.md|glossary' \
      'NO_UNLINKED_PROJECT_TERM_IN_DEFINITION|DOCUMENTATION.md|glossary' \
      'TERM_LINKED_ON_FIRST_USE|DOCUMENTATION.md|glossary' \
      'DEFINITION_HAS_ONE_HOME|DOCUMENTATION.md|glossary' \
      'ENFORCEMENT_ROW_COMPLETE|DOCUMENTATION.md|enforcement' \
      'MECHANISM_CLAIMS_TRACED|DOCUMENTATION.md|glossary' \
      'MECHANISM_CLAIMS_TRACED|DOCUMENTATION.md|enforcement' \
      'FRONT_DOOR_ANCHORS_RESOLVE|DOCUMENTATION.md|glossary' \
      'FRONT_DOOR_ANCHORS_RESOLVE|DOCUMENTATION.md|enforcement' \
      'LINK_TEXT_STANDS_ALONE|DOCUMENTATION.md|glossary' \
      'LINK_TEXT_STANDS_ALONE|DOCUMENTATION.md|enforcement' \
      'TABLES_HAVE_HEADER_ROWS|DOCUMENTATION.md|glossary' \
      'TABLES_HAVE_HEADER_ROWS|DOCUMENTATION.md|enforcement'; do
    SLUG="${ROW%%|*}"; FILE="${ROW#*|}"; FRAG="${FILE#*|}"; FILE="${FILE%%|*}"
    [ -n "$(fd_match "$(fd_at "$SLUG" "$FILE" 0)" "$FRAG")" ] || {
      echo "[fd-absent-inputs] no line-0 finding: $SLUG $FILE ($FRAG)" >&2; fd_show; exit 1; }
  done
  rm -rf "$TMP"
}

case_fd_unreadable_input() {
  local TMP SLUG; TMP="$(fd_fresh)"
  # X327 §7 UNREADABLE_INPUT: undecodable bytes in INSTALL.md are a line-0
  # finding under every slug whose check reads INSTALL.md, never a skip. The
  # front-door checks must still run when an earlier seed-lint check raised on
  # the same file.
  fd_py invalid_utf8 "$TMP/INSTALL.md"
  fd_lint_full
  fd_refuse_raised "fd-unreadable-input"
  [ "$FD_RC" -eq 1 ] || { echo "[fd-unreadable-input] expected exit 1, got $FD_RC" >&2; exit 1; }
  for SLUG in DEFINITION_HAS_ONE_HOME MECHANISM_CLAIMS_TRACED CATALOGS_OUT_OF_README \
              EAGER_FIGURES_CHECKED_WHEREVER_PUBLISHED BODY_FIGURES_HAVE_A_REQUIRED_HOME \
              FRONT_DOOR_ANCHORS_RESOLVE; do
    [ -n "$(fd_match "$(fd_at "$SLUG" INSTALL.md 0)" 'UTF-8')" ] || {
      echo "[fd-unreadable-input] no line-0 UTF-8 finding under $SLUG" >&2; fd_show; exit 1; }
  done
  rm -rf "$TMP"
}

case_fd_check_raised() {
  local TMP; TMP="$(fd_fresh)"
  # X328 §7 CHECK_RAISED (AC-28): a check that raises is reported as RAISED and
  # fails the run even while its slug is pending; it is neither stale nor
  # counted. The one case exempt from the `: RAISED ` refusal.
  fd_bind
  fd_py ledger "$TMP" TABLES_HAVE_HEADER_ROWS
  fd_py inject_raise "$TMP" check_fd_tables_have_header_rows
  fd_lint_full
  # exercises: check_fd_tables_have_header_rows
  [ "$FD_RC" -eq 1 ] || { echo "[fd-check-raised] expected exit 1 from a raised pending check, got $FD_RC" >&2; exit 1; }
  grep -qF 'front-door: TABLES_HAVE_HEADER_ROWS: RAISED RuntimeError: planted' <<<"$FD_OUT" || {
    echo "[fd-check-raised] missing: front-door: TABLES_HAVE_HEADER_ROWS: RAISED RuntimeError: planted" >&2; fd_show; exit 1; }
  fd_expect_none "fd-check-raised" 'stale pending entry'
  fd_expect_none "fd-check-raised" 'front-door: PENDING TABLES_HAVE_HEADER_ROWS'
  rm -rf "$TMP"
}

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
for c in case_01 case_02 case_03 case_04 case_05 case_06 case_07 case_08 case_09 case_10 case_11 case_12 case_13 case_14 case_15 case_16 case_17 case_18 case_19 case_20 case_21 case_22 case_23 case_24 case_25 case_26 case_27 case_28 case_29 case_30 case_31 case_32 case_33 case_34 case_35 case_36 case_spec_row_toplevel_def case_37 case_38 case_shell_floor case_agn_docs case_agn_py_sh case_x201 case_x202 case_x203 case_frontmatter_portable caseHOST_TIERS_AGREE \
    case_fd_fixture_clean case_fd_first_screen_order case_fd_first_screen_budget case_fd_first_command_line case_fd_what_you_get_heading case_fd_first_screen_caps case_fd_later_sections_order case_fd_install_target_paths case_fd_install_seed_path case_fd_where_next case_fd_glossary_absent case_fd_glossary_fields case_fd_glossary_closed_values case_fd_glossary_required_term case_fd_glossary_paths case_fd_glossary_install_literal case_fd_definition_links case_fd_term_linked case_fd_one_home case_fd_reference_opener case_fd_enforcement_row case_fd_enforcement_required_row case_fd_enforcement_row_residuals case_fd_mechanism_traced case_fd_mechanism_overclaim case_fd_mechanism_surfaces case_fd_hook_firing case_fd_limits_hard_row case_fd_limits_required_rows case_fd_limits_unmeasured case_fd_catalogs case_fd_adr_range case_fd_cost_scope case_fd_cost_provenance case_fd_cost_measured_derived case_fd_cost_no_derived case_fd_measured_evidence case_fd_eager_published case_fd_body_home case_fd_body_figure_elsewhere case_fd_body_project_node case_fd_anchor_resolves case_fd_anchor_duplicate case_fd_headings case_fd_link_text case_fd_table_header case_fd_pending_stale case_fd_pending_unknown_slug case_fd_pending_holds_exit case_fd_pending_implemented case_fd_pending_release case_fd_absent_inputs case_fd_unreadable_input case_fd_check_raised; do
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
