#!/usr/bin/env python3
"""Regression tests for graph-lint.py's kind→id-prefix schema check.

These accompany the machinery improvement that adds an optional `KIND_PREFIX`
mapping to graph-lint.py's PROJECT CONFIG block. Before the improvement, a
node's id-prefix had to equal its `kind` literally; the improvement lets a
verbose kind live under a terser id namespace while defaulting to the old
identity rule so every existing project lints exactly as before.

Like tests/test_agent_lint.py, each test drives the tool through its public
CLI (`python3 graph-lint.py`) against a hermetic temp graph rather than
importing internals — a public-interface test. Unlike that suite, this one runs
on the stdlib alone (unittest), matching graph-lint.py's own "no third-party
dependencies" rule, so it runs under a bare `python3 tests/test_graph_lint.py`.

Contract map:
  test_identity_*      -> with KIND_PREFIX unset (default {}), a node whose
                          id-prefix equals its kind passes, and a mismatch
                          fails: the old behavior, unchanged.
  test_mapped_prefix_* -> with KIND_PREFIX = {kind: prefix}, a node using the
                          MAPPED prefix passes, and one still using the literal
                          kind prefix fails. This is what the new code enables:
                          run against the pre-improvement tool the mapped node
                          fails (RED for the right reason), because the literal
                          "<kind>." was the only accepted prefix.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# --------------------------------------------------------------------------
# Locate the tool from this test file's own location so the suite is
# project-agnostic and portable — no absolute or host-specific path is baked in.
# --------------------------------------------------------------------------
HERE = Path(__file__).resolve().parent          # <seed>/tests
SEED = HERE.parent                               # the seed root (this repo)
GRAPH_LINT = SEED / "templates" / "knowledge-graph" / "graph-lint.py"

# The default config line the tool ships with; a test rewrites it to inject a
# mapping, exercising the real PROJECT CONFIG mechanism rather than a stub.
DEFAULT_CONFIG_LINE = "KIND_PREFIX = {}"


def run_lint(graph_dir: Path) -> subprocess.CompletedProcess:
    """Run graph-lint.py against a copy of itself sitting inside graph_dir
    (mirrors the real install, where the tool lives next to index.md/nodes/)."""
    return subprocess.run(
        [sys.executable, str(graph_dir / "graph-lint.py")],
        cwd=str(graph_dir),
        capture_output=True,
        text=True,
        timeout=60,
    )


def node_md(node_id: str, kind: str, *, requires=(), owns=None) -> str:
    """A minimal, schema-valid tier-2 node. est_tokens is derived from the body
    word count so the budget check (within-2x) always passes."""
    body = (
        f"This node documents the {kind} boundary for testing the lint "
        "contract in a hermetic graph fixture with a handful of plain words."
    )
    est = int(len(body.split()) * 1.35)
    owns = owns if owns is not None else [f"{node_id}.overview"]
    lines = [
        "---",
        f"id: {node_id}",
        "tier: 2",
        f"kind: {kind}",
        f"title: {node_id} node",
        "owns:",
        *(f"  - {o}" for o in owns),
        "requires:",
        *(f"  - {r}" for r in requires),
        "load_when:",
        f"  - work on {node_id}",
        f"est_tokens: {est}",
        "---",
        "",
        body,
        "",
    ]
    return "\n".join(lines)


def build_graph(tmp: Path, nodes: dict, *, config_line: str | None = None) -> Path:
    """Materialize a hermetic graph: <tmp>/graph/{graph-lint.py, index.md,
    nodes/*.md}. `nodes` maps node-id -> frontmatter text. `config_line`, when
    given, replaces the tool's default KIND_PREFIX line before it is copied in.
    """
    graph = tmp / "graph"
    (graph / "nodes").mkdir(parents=True)

    src = GRAPH_LINT.read_text(encoding="utf-8")
    if config_line is not None:
        assert DEFAULT_CONFIG_LINE in src, (
            f"expected default config line {DEFAULT_CONFIG_LINE!r} in graph-lint.py"
        )
        src = src.replace(DEFAULT_CONFIG_LINE, config_line, 1)
    (graph / "graph-lint.py").write_text(src, encoding="utf-8")

    # index.md lists every node id, so reachability is satisfied regardless of
    # the requires-edges each test chooses.
    (graph / "index.md").write_text(
        "# index\n\n" + "\n".join(f"- {nid}" for nid in nodes) + "\n",
        encoding="utf-8",
    )
    for nid, text in nodes.items():
        (graph / "nodes" / f"{nid}.md").write_text(text, encoding="utf-8")
    return graph


class KindPrefixTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(GRAPH_LINT.exists(), f"missing tool: {GRAPH_LINT}")
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    # -- identity default (KIND_PREFIX = {}): the pre-existing behavior --------

    def test_identity_matching_prefix_passes(self):
        """id-prefix == kind, default config -> lint OK (unchanged behavior)."""
        nodes = {
            "root": node_md("root", "root", requires=["subsystem.alpha"]),
            "subsystem.alpha": node_md("subsystem.alpha", "subsystem"),
        }
        r = run_lint(build_graph(self.tmp, nodes))
        self.assertEqual(r.returncode, 0, f"expected clean lint:\n{r.stdout}\n{r.stderr}")

    def test_identity_mismatched_prefix_fails(self):
        """id-prefix != kind, default config -> the id/kind schema error."""
        nodes = {
            "root": node_md("root", "root", requires=["sub.alpha"]),
            "sub.alpha": node_md("sub.alpha", "subsystem"),
        }
        r = run_lint(build_graph(self.tmp, nodes))
        out = r.stdout + r.stderr
        self.assertNotEqual(r.returncode, 0, f"a kind/id mismatch must fail:\n{out}")
        self.assertIn("does not match kind", out, out)
        self.assertIn("sub.alpha", out, out)

    # -- mapped prefix (KIND_PREFIX = {"subsystem": "sub"}): the new capability --

    def test_mapped_prefix_mapped_id_passes(self):
        """With subsystem->sub mapped, a node id'd 'sub.alpha' passes. This is
        what the improvement enables; the pre-improvement tool rejected it
        because only the literal 'subsystem.' prefix was accepted (RED reason)."""
        nodes = {
            "root": node_md("root", "root", requires=["sub.alpha"]),
            "sub.alpha": node_md("sub.alpha", "subsystem"),
        }
        graph = build_graph(self.tmp, nodes,
                            config_line='KIND_PREFIX = {"subsystem": "sub"}')
        r = run_lint(graph)
        self.assertEqual(r.returncode, 0,
                         f"a mapped-prefix id must pass:\n{r.stdout}\n{r.stderr}")

    def test_mapped_prefix_literal_kind_id_fails(self):
        """With subsystem->sub mapped, the literal 'subsystem.alpha' id no longer
        matches the effective prefix and must fail, reporting the expected 'sub.'
        prefix."""
        nodes = {
            "root": node_md("root", "root", requires=["subsystem.alpha"]),
            "subsystem.alpha": node_md("subsystem.alpha", "subsystem"),
        }
        graph = build_graph(self.tmp, nodes,
                            config_line='KIND_PREFIX = {"subsystem": "sub"}')
        r = run_lint(graph)
        out = r.stdout + r.stderr
        self.assertNotEqual(r.returncode, 0,
                            f"a literal-kind id under a mapping must fail:\n{out}")
        self.assertIn("does not match kind", out, out)
        self.assertIn("'sub.'", out, out)

    def test_unmapped_kind_keeps_identity_under_a_mapping(self):
        """A mapping for one kind leaves other kinds on the identity rule: a
        'stack.*' node still passes when only 'subsystem' is remapped."""
        nodes = {
            "root": node_md("root", "root", requires=["stack.runtime"]),
            "stack.runtime": node_md("stack.runtime", "stack"),
        }
        graph = build_graph(self.tmp, nodes,
                            config_line='KIND_PREFIX = {"subsystem": "sub"}')
        r = run_lint(graph)
        self.assertEqual(r.returncode, 0,
                         f"an unmapped kind must keep identity:\n{r.stdout}\n{r.stderr}")


class MachineryNodeTests(unittest.TestCase):
    """6.0.0: the seed's method surface lives inside the graph as machinery
    nodes under docs/graph/{protocols,skills,agents,method}/. Contract:
    kind must match the directory, filenames keep natural names (id name
    part == stem with any NN- prefix stripped), pre-growth graphs (machinery
    only, no root) lint when index.md lists the nodes, and the line ceiling
    does not apply to machinery bodies."""

    def setUp(self):
        self.assertTrue(GRAPH_LINT.exists(), f"missing tool: {GRAPH_LINT}")
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def _add_machinery(self, graph: Path, dirname: str, filename: str, text: str):
        d = graph / dirname
        d.mkdir(exist_ok=True)
        (d / filename).write_text(text, encoding="utf-8")
        # extend index so reachability lists the machinery id too
        idx = graph / "index.md"
        nid = next(l.split("id: ", 1)[1] for l in text.splitlines() if l.startswith("id: "))
        idx.write_text(idx.read_text(encoding="utf-8") + f"- {nid}\n", encoding="utf-8")

    def test_machinery_node_in_kind_dir_passes(self):
        nodes = {"root": node_md("root", "root")}
        graph = build_graph(self.tmp, nodes)
        self._add_machinery(graph, "protocols", "test-first.md",
                            node_md("protocol.test-first", "protocol"))
        r = run_lint(graph)
        self.assertEqual(r.returncode, 0,
                         f"machinery node must lint in its kind dir:\n{r.stdout}\n{r.stderr}")

    def test_machinery_kind_must_match_directory(self):
        nodes = {"root": node_md("root", "root")}
        graph = build_graph(self.tmp, nodes)
        self._add_machinery(graph, "protocols", "context-router.md",
                            node_md("skill.context-router", "skill"))
        r = run_lint(graph)
        self.assertNotEqual(r.returncode, 0, "kind/dir mismatch must fail")
        self.assertIn("does not match its directory", r.stdout + r.stderr)

    def test_machinery_filename_nn_prefix_is_stripped(self):
        nodes = {"root": node_md("root", "root")}
        graph = build_graph(self.tmp, nodes)
        self._add_machinery(graph, "agents", "00-orchestrator.md",
                            node_md("agent.orchestrator", "agent"))
        r = run_lint(graph)
        self.assertEqual(r.returncode, 0,
                         f"NN- filename prefix must be accepted:\n{r.stdout}\n{r.stderr}")

    def test_pregrowth_machinery_only_graph_lints_without_root(self):
        graph = build_graph(self.tmp, {})  # empty nodes/, index has no ids
        self._add_machinery(graph, "method", "tiers.md",
                            node_md("method.tiers", "method"))
        r = run_lint(graph)
        self.assertEqual(r.returncode, 0,
                         f"pre-growth grace: machinery-only graph must lint:\n{r.stdout}\n{r.stderr}")

    def test_project_node_still_requires_root(self):
        nodes = {"subsystem.api": node_md("subsystem.api", "subsystem")}
        graph = build_graph(self.tmp, nodes)
        r = run_lint(graph)
        self.assertNotEqual(r.returncode, 0,
                            "a project node with no root must still fail")
        self.assertIn("missing root node", r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
