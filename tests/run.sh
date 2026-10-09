#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# One concurrency budget for the whole gate; tests/gate_pool.py owns it.
# GATE_JOBS is clamped to [4, 64]; unset, the default is clamp(cpu*2, 8, 64).
# The token pool under GATE_POOL_DIR caps the leaf subprocesses of every
# parallel suite together. It lives in $TMPDIR, outside the seed digest.
GATE_POOL_DIR="$(mktemp -d)"
export GATE_POOL_DIR
export GATE_JOBS="${GATE_JOBS:-}"

# Seed integrity across the whole run: one digest before any step, compared in
# the EXIT trap, so a suite that writes back into the seed fails the gate.
# Digested: type, mode and path of every entry, file bytes (sha256), symlink
# targets, and .git minus objects/ and logs/. Excluded: __pycache__/*.pyc and
# the __pycache__ directory entry. python3, not GNU find/sha256sum, for macOS.
_seed_digest() {
    SEED_ROOT_FOR_DIGEST="$ROOT" python3 - <<'PYEOF'
import hashlib, os, sys

root = os.environ["SEED_ROOT_FOR_DIGEST"]
git = os.path.join(root, ".git")
pruned = {os.path.join(git, "objects"), os.path.join(git, "logs")}
out = hashlib.sha256()
entries = []

for base, dirs, files in os.walk(root):
    if base in pruned:
        dirs[:] = []
        continue
    dirs[:] = [d for d in dirs if os.path.join(base, d) not in pruned]
    for name in list(dirs) + files:
        path = os.path.join(base, name)
        rel = os.path.relpath(path, root)
        if os.path.basename(base) == "__pycache__" and name.endswith(".pyc"):
            continue
        if name == "__pycache__" and os.path.isdir(path) and not os.path.islink(path):
            continue
        entries.append((rel, path))

for rel, path in sorted(entries):
    try:
        st = os.lstat(path)
    except OSError:
        continue
    if os.path.islink(path):
        kind, extra = "l", os.readlink(path).encode()
    elif os.path.isdir(path):
        kind, extra = "d", b""
    else:
        kind = "f"
        try:
            with open(path, "rb") as fh:
                extra = hashlib.sha256(fh.read()).digest()
        except OSError:
            extra = b"<unreadable>"
    out.update(f"{kind} {st.st_mode & 0o7777:04o} {rel}\n".encode())
    out.update(extra)

sys.stdout.write(out.hexdigest())
PYEOF
}
SEED_DIGEST_BEFORE="$(_seed_digest)"
_seed_integrity() {
    local rc=$?
    if [[ "$(_seed_digest)" != "$SEED_DIGEST_BEFORE" ]]; then
        echo "FAIL: the gate modified the seed it was testing — a suite wrote" >&2
        echo "      back into $ROOT instead of its temp target. Re-run with" >&2
        echo "      'git status' to see what moved; no suite may touch the seed." >&2
        exit 1
    fi
    exit $rc
}
trap _seed_integrity EXIT

# Every step is independent (each installing suite works in its own mktemp -d).
# add_step records a command line; tests/run-parallel.py runs them all, prints
# each log grouped, and exits 1 naming every failed step.
STEPS_FILE="$(mktemp)"
add_step() { printf '%q ' "$@" >> "$STEPS_FILE"; printf '\n' >> "$STEPS_FILE"; }

# --- install and plant state (temp installs) --------------------------------
add_step bash "$ROOT/tests/test-full-install.sh"
add_step bash "$ROOT/tests/test-install-placement.sh"
add_step bash "$ROOT/tests/test-plant-state.sh"
add_step bash "$ROOT/tests/test-install-kernel-modes.sh"
add_step bash "$ROOT/tests/test-install-adoption.sh"
add_step bash "$ROOT/tests/test-unified-graph-install.sh"
add_step bash "$ROOT/tests/test-nested-checkout.sh"

# --- linters against planted fixtures ----------------------------------------
# Each proves its linter fires; the real-tree step that pairs with it is named.
add_step bash "$ROOT/tests/test-spec-lint.sh"          # pair: spec-lint.py below
add_step bash "$ROOT/tests/test-grill-lint.sh"         # pair: grill-lint.py below
add_step bash "$ROOT/tests/test-verify-ledger.sh"
add_step bash "$ROOT/tests/test-legal-lint.sh"         # pair: legal-lint.py below
add_step bash "$ROOT/tests/test-agnosticism-lint.sh"   # pair: seed-lint.py below
add_step bash "$ROOT/tests/test-prose-lint.sh"         # pair: prose-lint.py below
add_step bash "$ROOT/tests/test-lint-audibility.sh"
add_step bash "$ROOT/tests/test-ratchet-lint.sh"       # pair: ratchet-lint.py below
add_step bash "$ROOT/tests/test-status-register.sh"
add_step bash "$ROOT/tests/test-session-metrics.sh"
add_step bash "$ROOT/tests/test-status-migrate.sh"
add_step bash "$ROOT/tests/test-graft-tools.sh"
add_step bash "$ROOT/tests/test-growth-audit.sh"
add_step python3 "$ROOT/tests/test_graph_lint.py"

# --- hooks and tools ---------------------------------------------------------
add_step bash "$ROOT/tests/test-bound-hook.sh"
add_step bash "$ROOT/tests/test-prompt-hooks.sh"
add_step bash "$ROOT/tests/test-code-anchor.sh"
add_step bash "$ROOT/tests/test-source-index.sh"
add_step bash "$ROOT/tests/test-tool-help.sh"
add_step bash "$ROOT/tests/test-tool-corpus.sh"
add_step python3 "$ROOT/tests/test_corpus_match.py"
add_step python3 "$ROOT/tests/test_prepare_release.py"
add_step python3 "$ROOT/tests/test_frontmatter_contract.py"
add_step python3 "$ROOT/tests/test_agent_lint.py"
add_step python3 "$ROOT/tests/test_router_reach.py"

# --- the seed's own tree -----------------------------------------------------
add_step bash "$ROOT/tests/test-tier-lanes.sh"
add_step bash "$ROOT/tests/test-seed-lint.sh"
add_step python3 "$ROOT/tests/seed-lint.py"
add_step python3 "$ROOT/tests/legal-lint.py"
add_step python3 "$ROOT/tools/roster-justification.py" --gaps
add_step python3 "$ROOT/integrations/claude-code/agent-lint.py" --lint --dir "$ROOT/agents"
add_step python3 "$ROOT/integrations/claude-code/agent-lint.py" --eval --dir "$ROOT/agents"
# graph-lint.py --eval over the node-route corpus, run in a fresh temp install.
add_step bash "$ROOT/tests/graph-route-eval.sh"
# The budget is read on its own line: a step inside a heredoc is invisible to
# tools/gate-registry.py.
SPEC_BUDGET="$(python3 -c 'import pathlib,re,sys; print((re.search(r"^SPEC_UNCOVERED_BUDGET = (\d+)", pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"), re.M) or [0,"0"])[1])' "$ROOT/tests/seed-lint.py")"
add_step python3 "$ROOT/templates/knowledge-graph/spec-lint.py" --specs "$ROOT/docs/specs" --root "$ROOT" --uncovered-budget "$SPEC_BUDGET"
# Only the active plan is linted; point ACTIVE_PLAN at the next round's plan.
ACTIVE_PLAN="$ROOT/docs/plans/grill-8.1.2-tool-surfacing.md"
add_step python3 "$ROOT/templates/knowledge-graph/grill-lint.py" --plan "$ACTIVE_PLAN" --specs "$ROOT/docs/specs" --decisions "$ROOT/docs/decisions"
# One step per file (SPEC-0004 PROSE_FLOOR_HELD_PER_FILE): the dash allowance is
# a rate. documentation/*-reference.md stay out by a recorded genre decision.
add_step python3 "$ROOT/tools/prose-lint.py" --file "$ROOT/README.md"
add_step python3 "$ROOT/tools/prose-lint.py" --file "$ROOT/DOCUMENTATION.md"
add_step python3 "$ROOT/tools/prose-lint.py" --file "$ROOT/templates/knowledge-graph/_schema.md"
add_step python3 "$ROOT/tools/prose-lint.py" --file "$ROOT/templates/knowledge-graph/index.md"

# --- the gate's own machinery ------------------------------------------------
add_step python3 "$ROOT/tools/ratchet-lint.py"
add_step python3 "$ROOT/tests/test_gate_registry.py"
add_step python3 "$ROOT/tools/gate-registry.py" --lint
add_step python3 "$ROOT/tests/test_run_parallel.py"
add_step python3 "$ROOT/tests/test_gate_pool.py"

# On any failure this returns non-zero and `set -e` fires the EXIT trap.
python3 "$ROOT/tests/run-parallel.py" "$STEPS_FILE"
rm -f "$STEPS_FILE"
