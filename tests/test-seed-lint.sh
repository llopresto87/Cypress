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
# opencode config contract, and the est_tokens-vs-body budget — plus the
# long-standing kernel-budget guard as a control.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# Hermetic copy of the seed (seed-lint resolves ROOT from its own location, so
# running $TMP/tests/seed-lint.py lints the copy). Exclude VCS/build cruft.
( cd "$ROOT" && tar --exclude=.git --exclude=__pycache__ --exclude='*.pyc' \
    --exclude=.pytest_cache -cf - . ) | ( cd "$TMP" && tar -xf - )

lint() { python3 "$TMP/tests/seed-lint.py" 2>&1; }
restore() { cp "$ROOT/$1" "$TMP/$1"; }   # revert a planted file from the pristine seed

expect_fail() {  # $1=grep-pattern  $2=label
  local out rc
  out="$(lint)" && rc=0 || rc=$?
  [[ $rc -eq 1 ]] || { echo "[$2] expected exit 1, got $rc" >&2; echo "$out" >&2; exit 1; }
  grep -q "$1" <<<"$out" || { echo "[$2] missing expected message: /$1/" >&2; echo "$out" >&2; exit 1; }
}

# 0. Baseline: the pristine copy lints clean.
lint >/dev/null || { echo "baseline seed-lint did not pass on a clean copy" >&2; exit 1; }

# 1. A user-sovereign protocol must not declare `command: true`.
python3 - "$TMP/protocols/graft.md" <<'PY'
import re,sys; p=sys.argv[1]; t=open(p).read()
open(p,'w').write(re.sub(r'(?m)^(est_tokens:[^\n]*\n)', r'\1command: true\n', t, count=1))
PY
expect_fail "must not declare 'command: true'" "sovereign-command"
restore protocols/graft.md

# 2. `command:` is a protocol-only field.
python3 - "$TMP/skills/context-router/SKILL.md" <<'PY'
import re,sys; p=sys.argv[1]; t=open(p).read()
open(p,'w').write(re.sub(r'(?m)^(est_tokens:[^\n]*\n)', r'\1command: true\n', t, count=1))
PY
expect_fail "protocol-only field" "command-on-skill"
restore skills/context-router/SKILL.md

# 3. A requires:/peers: edge to a nonexistent node fails to resolve.
python3 - "$TMP/protocols/verify.md" <<'PY'
import re,sys; p=sys.argv[1]; t=open(p).read()
open(p,'w').write(re.sub(r'(?m)^requires:\s*$', 'requires:\n  - protocol.does-not-exist', t, count=1))
PY
expect_fail "unknown machinery node" "dangling-edge"
restore protocols/verify.md

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

# 5. A miscounted skills claim in shipped prose is caught.
printf '\n\nThe seed ships 99 skills.\n' >> "$TMP/README.md"
expect_fail "claims 99 skills" "skills-count"
restore README.md

# 5b. REGRESSION — the qualified "N named specialist agents" phrasing is
# policed too: DOCUMENTATION.md shipped a release saying "17 named
# specialist agents" while the roster had 18, and the first version of
# this scan only matched the bare "N specialist agents" form.
printf '\n\nA team of 99 named specialist agents.\n' >> "$TMP/DOCUMENTATION.md"
expect_fail "99 named specialist agents" "qualified-agent-count"
restore DOCUMENTATION.md

# 5c. REGRESSION — the documentation tree's version pin must match the
# manifest: DOCUMENTATION.md/documentation/README.md sat at 6.8.0 for a
# whole release because no gate read them.
python3 - "$TMP/documentation/README.md" <<'PY'
import sys; p=sys.argv[1]; t=open(p).read()
import re; open(p,"w").write(re.sub(r"\(version \d+\.\d+\.\d+\)", "(version 0.0.1)", t, count=1))
PY
expect_fail "documents version 0.0.1" "doc-tree-version-pin"
restore documentation/README.md

# 6. manifest version and the top CHANGELOG entry must agree.
python3 - "$TMP/manifest.json" <<'PY'
import re,sys; p=sys.argv[1]; t=open(p).read()
open(p,'w').write(re.sub(r'("version":\s*")\d+\.\d+\.\d+(")', r'\g<1>0.0.0\g<2>', t, count=1))
PY
expect_fail "version drift" "version-single-source"
restore manifest.json

# 7. Control: the long-standing kernel-budget guard still bites.
python3 -c "open('$TMP/core/AGENTS.md','a').write('\n<!-- '+'x'*9000+' -->\n')"
expect_fail "exceeds the" "kernel-budget"
restore core/AGENTS.md

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

# 9. A dangling cross-reference into any corpus is caught (the withdraw
# contracts are prose pointers; a stale one silently sends a reader nowhere).
python3 -c "open('$TMP/protocols/harvest.md','a').write('\nSee \`legal-corpus/eu/does-not-exist.md\`.\n')"
expect_fail "dangling corpus/template reference" "dangling-corpus-ref"
restore protocols/harvest.md

# 10. The "installed but not spawnable" rule keeps its single home. Moving or
# dropping it from method.delegation would leave every dispatch/install surface
# pointing at a fact nothing owns.
python3 - "$TMP/core/method/delegation.md" <<'PY'
import sys; p=sys.argv[1]; t=open(p).read()
open(p,'w').write(t.replace("  - delegation.harness-registration\n", "", 1))
PY
expect_fail "does not own 'delegation.harness-registration'" "registration-home"
restore core/method/delegation.md

# 11. A dispatch/install surface that drops the pointer is caught. This is the
# rot mode the fix exists to prevent: the rule stays written in one place while
# the surface that needed it quietly stops mentioning it.
python3 - "$TMP/protocols/grow.md" <<'PY'
import sys; p=sys.argv[1]; t=open(p).read()
open(p,'w').write(t.replace("delegation.harness-registration", "<dropped>"))
PY
expect_fail "never points at 'delegation.harness-registration'" "registration-referrer"
restore protocols/grow.md

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

# 13. A machinery node whose est_tokens is more than 2x off its measured body
# would be REJECTED by the graph-lint.py the seed itself ships, once installed
# into a plant. The seed never checked its own nodes against that rule.
python3 - "$TMP/protocols/verify.md" <<'PY'
import re,sys; p=sys.argv[1]; t=open(p).read()
open(p,'w').write(re.sub(r'(?m)^est_tokens:\s*\d+', 'est_tokens: 20', t, count=1))
PY
expect_fail "graph-lint.py would reject this node" "est-tokens-2x"
restore protocols/verify.md

# 14. After all restores, the copy lints clean again.
lint >/dev/null || { echo "seed-lint did not return to PASS after restores" >&2; exit 1; }

printf 'seed-lint contract: PASS\n'
