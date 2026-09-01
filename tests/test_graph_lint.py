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
        graph = build_graph(self.tmp, {})  # empty nodes/, no root
        self._add_machinery(graph, "method", "tiers.md",
                            node_md("method.tiers", "method"))
        # the shipped index lists every machinery node; reachability is
        # a traversal seeded by the listed ids, so list it here too
        (graph / "index.md").write_text("# index\n\n- method.tiers\n",
                                        encoding="utf-8")
        r = run_lint(graph)
        self.assertEqual(r.returncode, 0,
                         f"pre-growth grace: machinery-only graph must lint:\n{r.stdout}\n{r.stderr}")


    def test_pregrowth_prefix_collision_is_not_listed(self):
        """Regression: the pre-growth (no-root) branch kept the raw substring
        test after 6.9.1 fixed the root branch — an orphan machinery node
        passed whenever its id merely prefixed an unrelated longer id in
        index.md (skill.context vs skill.context-router)."""
        graph = build_graph(self.tmp, {})  # empty nodes/, no root
        self._add_machinery(graph, "skills", "context-router.md",
                            node_md("skill.context-router", "skill"))
        self._add_machinery(graph, "skills", "context.md",
                            node_md("skill.context", "skill"))
        (graph / "index.md").write_text(
            "# index\n\n- skill.context-router\n", encoding="utf-8")
        r = run_lint(graph)
        out = r.stdout + r.stderr
        self.assertNotEqual(r.returncode, 0,
                            f"pre-growth orphan must not ride a prefix:\n{out}")
        self.assertIn("skill.context:", out, out)

    def test_pregrowth_orphan_island_fails(self):
        """Regression: pre-growth reachability once unioned EVERY node's
        outgoing edges into the seen-set, so two mutually-peering ghost
        nodes vouched for each other and a whole orphan island passed."""
        graph = build_graph(self.tmp, {})
        self._add_machinery(graph, "method", "tiers.md",
                            node_md("method.tiers", "method"))
        ghost_a = node_md("skill.ghost-a", "skill").replace(
            "requires:", "peers:\n  - skill.ghost-b\nrequires:")
        ghost_b = node_md("skill.ghost-b", "skill").replace(
            "requires:", "peers:\n  - skill.ghost-a\nrequires:")
        self._add_machinery(graph, "skills", "ghost-a.md", ghost_a)
        self._add_machinery(graph, "skills", "ghost-b.md", ghost_b)
        (graph / "index.md").write_text("# index\n\n- method.tiers\n",
                                        encoding="utf-8")
        r = run_lint(graph)
        out = r.stdout + r.stderr
        self.assertNotEqual(r.returncode, 0,
                            f"a mutually-peering orphan island must fail:\n{out}")
        self.assertIn("skill.ghost-a", out, out)

    def test_duplicate_id_fails(self):
        """Regression: _schema.md rule 2 claims id uniqueness, but nothing
        enforced it — a project node and a machinery node sharing one id both
        passed their filename checks and --plan resolved to whichever file
        was scanned last, silently."""
        nodes = {"root": node_md("root", "root", requires=["protocol.foo"])}
        graph = build_graph(self.tmp, nodes)
        self._add_machinery(graph, "protocols", "foo.md",
                            node_md("protocol.foo", "protocol"))
        (graph / "nodes" / "protocol.foo.md").write_text(
            node_md("protocol.foo", "protocol",
                    owns=["protocol.foo.second-home"]),
            encoding="utf-8")
        r = run_lint(graph)
        out = r.stdout + r.stderr
        self.assertNotEqual(r.returncode, 0, f"duplicate id must fail:\n{out}")
        self.assertIn("declared by 2 files", out, out)

    def test_project_node_still_requires_root(self):
        nodes = {"subsystem.api": node_md("subsystem.api", "subsystem")}
        graph = build_graph(self.tmp, nodes)
        r = run_lint(graph)
        self.assertNotEqual(r.returncode, 0,
                            "a project node with no root must still fail")
        self.assertIn("missing root node", r.stdout + r.stderr)




class VersionLeakageTests(unittest.TestCase):
    """Regression: VERSION_RE's lookbehind excluded any word char — including
    the leading `v` of the standard `vX.Y.Z` spelling — so `v2.7.2` evaded
    check_version_leakage while bare `2.7.2` was caught."""

    def setUp(self):
        self.assertTrue(GRAPH_LINT.exists(), f"missing tool: {GRAPH_LINT}")
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def _graph_with_body_suffix(self, suffix: str) -> Path:
        node = node_md("subsystem.alpha", "subsystem")
        node = node.replace("plain words.", f"plain words. {suffix}")
        nodes = {
            "root": node_md("root", "root", requires=["subsystem.alpha"]),
            "subsystem.alpha": node,
        }
        return build_graph(self.tmp, nodes)

    def test_v_prefixed_semver_is_caught(self):
        """A `v2.7.2` pin in a non-machinery body must fail the leak check."""
        r = run_lint(self._graph_with_body_suffix("Pinned at v2.7.2 today."))
        out = r.stdout + r.stderr
        self.assertNotEqual(r.returncode, 0, f"v-prefixed pin must fail:\n{out}")
        self.assertIn("version pin", out, out)

    def test_section_reference_is_not_a_pin(self):
        """`\u00a75.4` stays exempt — the lookbehind still shields section refs."""
        r = run_lint(self._graph_with_body_suffix("See \u00a75.4 for the rule."))
        self.assertEqual(r.returncode, 0, f"section ref must pass:\n{r.stdout}\n{r.stderr}")


class ReachabilityBoundaryTests(unittest.TestCase):
    """Regression: reachability once used a plain substring test against
    index.md, so an orphan node passed whenever its id merely prefixed an
    unrelated longer string (`subsystem.orphan` vs `subsystem.orphaned-thing`)."""

    def setUp(self):
        self.assertTrue(GRAPH_LINT.exists(), f"missing tool: {GRAPH_LINT}")
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def _graph(self, index_lines: list) -> Path:
        nodes = {
            "root": node_md("root", "root", requires=["subsystem.alpha"]),
            "subsystem.alpha": node_md("subsystem.alpha", "subsystem"),
            "subsystem.orphan": node_md("subsystem.orphan", "subsystem"),
        }
        graph = build_graph(self.tmp, nodes)
        (graph / "index.md").write_text(
            "# index\n\n" + "\n".join(f"- {l}" for l in index_lines) + "\n",
            encoding="utf-8",
        )
        return graph

    def test_prefix_of_longer_string_is_not_listed(self):
        """An orphan whose id only prefixes an unrelated index string fails."""
        r = run_lint(self._graph(["root", "subsystem.alpha", "subsystem.orphaned-thing"]))
        out = r.stdout + r.stderr
        self.assertNotEqual(r.returncode, 0, f"prefix collision must not count:\n{out}")
        self.assertIn("unreachable", out, out)
        self.assertIn("subsystem.orphan", out, out)

    def test_dotted_child_id_is_not_the_parent(self):
        """An orphan whose id only prefixes a DOTTED child id in index.md
        (`subsystem.orphan` vs `subsystem.orphan.child`) fails too — dotted
        ids are this graph's norm, so a bare word-char lookahead was only
        half the fix."""
        r = run_lint(self._graph(["root", "subsystem.alpha", "subsystem.orphan.child"]))
        out = r.stdout + r.stderr
        self.assertNotEqual(r.returncode, 0, f"dotted-child collision must not count:\n{out}")
        self.assertIn("unreachable", out, out)

    def test_exact_listing_still_counts(self):
        """The same orphan listed exactly in index.md passes as before."""
        graph = self._graph(["root", "subsystem.alpha", "subsystem.orphan"])
        res = run_lint(graph)
        self.assertEqual(res.returncode, 0, f"exact listing must pass:\n{res.stdout}\n{res.stderr}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
