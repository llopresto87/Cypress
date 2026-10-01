#!/usr/bin/env bash
# graph-route-eval.sh: the node router's corpus gate (SPEC-0002
# GRAPH_EVAL_GATES_PER_CLASS, ADR-0026). The corpus names the graph a fresh
# `install.sh claude-code` places, so the step installs the seed into a temp
# project and runs that plant's graph-lint.py --eval over
# tests/graph-routes.golden.tsv. Each class is reported on its own line and
# gated on graph-lint.py's GRAPH_* ratchets (tests/ratchets.json locks their
# values). They gate here because every node of a fresh install is
# `origin: seed`, the graph they were measured on (MEASURED_GRAPH_ORIGIN).
# The exit code alone does not prove they gated: on a graph with a node of
# another origin graph-lint.py reports them, ungated, and still exits 0. So the
# step also requires the line graph-lint.py prints only when it gated them.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

mkdir -p "$TMP/plant"
bash "$ROOT/install.sh" claude-code --project-dir "$TMP/plant" >"$TMP/install.log" 2>&1 \
  || { echo "graph-route-eval: install.sh failed: $(tail -3 "$TMP/install.log")" >&2; exit 1; }
GATED="graph-lint --eval: OK, every ratchet holds"
status=0
out="$(python3 "$TMP/plant/docs/graph/graph-lint.py" --eval "$ROOT/tests/graph-routes.golden.tsv")" \
  || status=$?
printf '%s\n' "$out"
[ "$status" -eq 0 ] || exit "$status"
grep -qxF "$GATED" <<<"$out" \
  || { echo "graph-route-eval: FAIL, the GRAPH_* ratchets did not gate: no \"$GATED\" line" >&2; exit 1; }
