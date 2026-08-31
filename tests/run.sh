#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
bash "$ROOT/tests/test-unified-graph-install.sh"
bash "$ROOT/tests/test-knowledge-paths.sh"
bash "$ROOT/tests/test-orchestration-entry.sh"
bash "$ROOT/tests/test-graph-artifacts.sh"
bash "$ROOT/tests/test-spec-lint.sh"
bash "$ROOT/tests/test-full-install.sh"
bash "$ROOT/tests/test-graft-tools.sh"
bash "$ROOT/tests/test-seed-lint.sh"
bash "$ROOT/tests/test-legal-lint.sh"
# graph-lint CLI-contract regression (stdlib unittest — no third-party deps,
# matching graph-lint.py's own rule, so it always runs here).
python3 "$ROOT/tests/test_graph_lint.py"
python3 "$ROOT/integrations/claude-code/agent-lint.py" --lint --dir "$ROOT/agents"
python3 "$ROOT/integrations/claude-code/agent-lint.py" --eval --dir "$ROOT/agents"
# agent-lint CLI-contract regression needs pytest; run it when present, and say
# so loudly when not — never a silent skip, never a faked green. Probe BOTH
# invocations: `brew install pytest` (and pipx) expose only the `pytest`
# executable in an isolated venv, so `python3 -m pytest` stays unavailable and
# probing it alone would skip a gate that is in fact installed.
if python3 -m pytest --version >/dev/null 2>&1; then
    python3 -m pytest -q "$ROOT/tests/test_agent_lint.py"
elif command -v pytest >/dev/null 2>&1; then
    pytest -q "$ROOT/tests/test_agent_lint.py"
else
    echo "[gate] SKIP tests/test_agent_lint.py — pytest not installed (brew install pytest, or pip install pytest) to run it" >&2
fi
python3 "$ROOT/tests/seed-lint.py"
# legal-corpus citability contract. seed-lint scans that corpus only for
# leaked host-IPs, pinned CVEs and dangling refs — none of which knows what a
# legal entry is, so the eight-field contract went ungated.
python3 "$ROOT/tests/legal-lint.py"
