#!/usr/bin/env bash
# T2's contained lane and its why-record each have exactly one owner node.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
for key in tiers.contained-lane canonize.why-record; do
  owners="$({ grep -rlx "  - $key" "$ROOT"/{core,protocols,skills,agents,templates} 2>/dev/null || true; } | wc -l | tr -d ' ')"
  [ "$owners" -eq 1 ] || { echo "FAIL: $key must be owned exactly once, found $owners owner(s)" >&2; exit 1; }
done
echo "tier lanes: PASS"
