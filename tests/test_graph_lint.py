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

import re
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


def node_md(node_id: str, kind: str, *, requires=(), owns=None, peers=(),
            composes=(), libraries=(), artifacts=(), load_when=None) -> str:
    """A minimal, schema-valid tier-2 node. `est_tokens` is derived from the
    WHOLE rendered node — frontmatter and body — because the whole file is
    what a loader pays for, which is the figure SPEC-0001 §4
    GRAPH_LINT_BUDGET_COUNTS_FRONTMATTER puts the budget check on.

    The body is deliberately longer, in words, than any frontmatter this
    helper emits. That is load-bearing: the within-2x band is symmetric
    (`measured > 2*est or est > 2*measured`), so a single figure sits in band
    under BOTH measurements only while frontmatter words <= body words. Every
    fixture here therefore lints clean whether the budget proxy counts the
    body alone (today) or the whole file (once the contract above is
    implemented), and no case goes red for a reason its own test never meant
    to assert. Shortening this paragraph, or adding a caller with a
    frontmatter longer than it, breaks that and is the thing to re-check
    first when a clean-fixture case starts failing on est_tokens.

    The optional edge and trigger keys are what the composes/descent cases
    need: `libraries` satisfies an expertise node's depth-edge rule, and
    `load_when` is the vocabulary descent matches a task against."""
    body = (
        f"This node documents the {kind} boundary for testing the lint "
        "contract in a hermetic graph fixture with a handful of plain words. "
        "The paragraph runs on past the point a single sentence would stop "
        "for one reason only, and the docstring above states it: the node "
        "needs more words below the fence than above it, so that one honest "
        "token figure can describe the body and the whole file at once and "
        "stay inside the tolerance either reading of the budget applies. "
        "Nothing else here is meaningful, and no assertion in this suite "
        "reads a word of it."
    )
    owns = owns if owns is not None else [f"{node_id}.overview"]
    load_when = load_when if load_when is not None else [f"work on {node_id}"]
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
    ]
    for key, values in (("peers", peers), ("composes", composes),
                        ("libraries", libraries), ("artifacts", artifacts)):
        if values:
            lines.append(f"{key}:")
            lines.extend(f"  - {v}" for v in values)
    lines += [
        "load_when:",
        *(f"  - {t}" for t in load_when),
        "est_tokens: 0",          # placeholder, substituted below
        "---",
        "",
        body,
        "",
    ]
    text = "\n".join(lines)
    # Counted on the placeholder, substituted after: the figure occupies
    # exactly one whitespace-separated word whatever its digits, so the count
    # taken here is the count of the file that is finally written. 1.35 is
    # graph-lint.py's own BODY_TOKENS_PER_WORD.
    est = int(len(text.split()) * 1.35)
    return text.replace("est_tokens: 0", f"est_tokens: {est}", 1)


def build_graph(tmp: Path, nodes: dict, *, config_line: str | None = None,
                listed=None, libraries=()) -> Path:
    """Materialize a hermetic graph: <tmp>/graph/{graph-lint.py, index.md,
    nodes/*.md}. `nodes` maps node-id -> frontmatter text. `config_line`, when
    given, replaces the tool's default KIND_PREFIX line before it is copied in.

    `listed` chooses which ids index.md names (default: all of them). A node
    left out is reachable only through a real edge, which is the only way a
    reachability case can fail — listing alone satisfies the rule. `libraries`
    names wiki pages to create, for nodes carrying a `libraries:` edge.
    """
    # One graph per call, in its own subdirectory: a test that builds two
    # fixtures (a passing shape and the mutation of it) would otherwise write
    # both into one directory and lint the union of them.
    graph = tmp / "graph"
    n = 1
    while graph.exists():
        n += 1
        graph = tmp / f"graph{n}"
    (graph / "nodes").mkdir(parents=True)

    src = GRAPH_LINT.read_text(encoding="utf-8")
    if config_line is not None:
        assert DEFAULT_CONFIG_LINE in src, (
            f"expected default config line {DEFAULT_CONFIG_LINE!r} in graph-lint.py"
        )
        src = src.replace(DEFAULT_CONFIG_LINE, config_line, 1)
    (graph / "graph-lint.py").write_text(src, encoding="utf-8")
    # ...and the frontmatter reader it imports, beside it. The engine is a
    # standalone script, so the import resolves next to the script: every place
    # the engine TRAVELS has to carry the reader — install.sh does, and so must
    # a fixture that copies the engine into a temp graph.
    (graph / "frontmatter.py").write_text(
        (SEED / "templates" / "knowledge-graph" / "frontmatter.py").read_text(encoding="utf-8"),
        encoding="utf-8")

    # index.md lists every node id by default, so reachability is satisfied
    # regardless of the requires-edges each test chooses; `listed` narrows it.
    named = nodes if listed is None else listed
    (graph / "index.md").write_text(
        "# index\n\n" + "\n".join(f"- {nid}" for nid in named) + "\n",
        encoding="utf-8",
    )
    for nid, text in nodes.items():
        (graph / "nodes" / f"{nid}.md").write_text(text, encoding="utf-8")
    if libraries:
        (graph / "libraries").mkdir(parents=True, exist_ok=True)
        for lib in libraries:
            (graph / "libraries" / f"{lib}.md").write_text(
                f"# {lib}\n\nA wiki page with enough words in it to look like "
                "a real leaf for the fixture.\n", encoding="utf-8")
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

    def test_spec_revision_citation_is_not_a_pin(self):
        """`SPEC-0002 v0.2.0` is a specification revision, not a dependency pin."""
        r = run_lint(self._graph_with_body_suffix("Per SPEC-0002 v0.2.0 AC-3 the drafter emits none."))
        self.assertEqual(r.returncode, 0, f"spec revision must pass:\n{r.stdout}\n{r.stderr}")

    def test_section_reference_is_not_a_pin(self):
        """`\u00a75.4` stays exempt — the lookbehind still shields section refs."""
        r = run_lint(self._graph_with_body_suffix("See \u00a75.4 for the rule."))
        self.assertEqual(r.returncode, 0, f"section ref must pass:\n{r.stdout}\n{r.stderr}")


class LibraryPageShapeTests(unittest.TestCase):
    """A template-shaped library page (one with a `## 0. Pin` heading) owes
    the ingest pass its exit — an exact version in the pin table, a dated
    `Last reviewed`, an index row — while a bare fixture page owes nothing."""

    PAGE = (
        "# Library: alpha\n\n## 0. Pin\n\n"
        "| Major | Exact version | Projects / paths | Notes |\n|---|---|---|---|\n"
        "| 2 | {version} | src/ | — |\n\n"
        "- **Name:** alpha\n- **Last reviewed:** {reviewed} by scout\n\n"
        "## 1. Role in this project\n\nWords.\n"
    )

    def setUp(self):
        self.assertTrue(GRAPH_LINT.exists(), f"missing tool: {GRAPH_LINT}")
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def _graph(self, *, version="2.7.2", reviewed="2026-09-09", index=True) -> Path:
        nodes = {"root": node_md("root", "root")}
        graph = build_graph(self.tmp, nodes, libraries=["alpha"])
        (graph / "libraries" / "alpha.md").write_text(
            self.PAGE.format(version=version, reviewed=reviewed), encoding="utf-8")
        if index:
            (graph / "libraries" / "index.md").write_text(
                "# Libraries\n\n| Library | Version | Page |\n|---|---|---|\n"
                "| alpha | 2.7.2 | alpha.md |\n", encoding="utf-8")
        return graph

    def test_shaped_page_passes(self):
        r = run_lint(self._graph())
        self.assertEqual(r.returncode, 0, f"pinned, dated, indexed page must pass:\n{r.stdout}\n{r.stderr}")

    def test_bare_fixture_page_owes_nothing(self):
        """A page with no `## 0. Pin` is not template-shaped — the fixtures
        every other test builds must keep passing."""
        nodes = {"root": node_md("root", "root")}
        r = run_lint(build_graph(self.tmp, nodes, libraries=["beta"]))
        self.assertEqual(r.returncode, 0, f"bare page must pass:\n{r.stdout}\n{r.stderr}")

    def test_placeholder_version_fails(self):
        r = run_lint(self._graph(version="<exact>"))
        out = r.stdout + r.stderr
        self.assertNotEqual(r.returncode, 0, f"placeholder pin must fail:\n{out}")
        self.assertIn("no exact version", out, out)

    def test_undated_review_fails(self):
        r = run_lint(self._graph(reviewed="YYYY-MM-DD"))
        out = r.stdout + r.stderr
        self.assertNotEqual(r.returncode, 0, f"undated review must fail:\n{out}")
        self.assertIn("Last reviewed", out, out)

    def test_missing_index_row_fails(self):
        graph = self._graph(index=False)
        (graph / "libraries" / "index.md").write_text("# Libraries\n\n| Library | Page |\n|---|---|\n", encoding="utf-8")
        r = run_lint(graph)
        out = r.stdout + r.stderr
        self.assertNotEqual(r.returncode, 0, f"unregistered page must fail:\n{out}")
        self.assertIn("no row in libraries/index.md", out, out)


class LibraryIndexRowBoundaryTests(unittest.TestCase):
    """Regression: the index-row check once asked only whether the page's name
    or stem occurred ANYWHERE in index.md as a bare substring. A short stem is
    a substring of half the file — a longer sibling's row, a column header, a
    sentence of prose — so an unregistered page passed the very gate that
    exists to catch it. The rule is now a *reference* to the page: a markdown
    link whose target is the file, or a table cell that is the page's name.

    Every negative case below passes against the pre-fix tool (RED for the
    right reason: the stem is planted as a substring), and every positive one
    is a shape the close-out librarian actually writes."""

    # A template-shaped page: the pin check is satisfied, so the index row is
    # the only thing under test.
    PAGE = (
        "# Library: {name}\n\n## 0. Pin\n\n"
        "| Major | Exact version | Projects / paths | Notes |\n|---|---|---|---|\n"
        "| 1 | 1.4.0 | src/ | — |\n\n"
        "- **Name:** {name}\n- **Last reviewed:** 2026-09-09 by scout\n\n"
        "## 1. Role in this project\n\nWords.\n"
    )

    def setUp(self):
        self.assertTrue(GRAPH_LINT.exists(), f"missing tool: {GRAPH_LINT}")
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def _graph(self, pages: dict, index_body: str) -> Path:
        """`pages` maps a library stem -> True for a template-shaped page or
        False for a bare one (a bare page owes nothing, so it can stand in for
        the longer sibling whose row is the substring trap)."""
        graph = build_graph(self.tmp, {"root": node_md("root", "root")},
                            libraries=list(pages))
        for stem, shaped in pages.items():
            if shaped:
                (graph / "libraries" / f"{stem}.md").write_text(
                    self.PAGE.format(name=stem), encoding="utf-8")
        (graph / "libraries" / "index.md").write_text(index_body, encoding="utf-8")
        return graph

    TABLE = "| Library | Version | Page | Last reviewed |\n|---|---|---|---|\n"
    HEAD = "# Libraries index\n\n" + TABLE

    def test_substring_of_a_longer_sibling_row_is_not_a_row(self):
        """THE DEFECT: `zamber` has no row, but `zamber-lattice` does, and the
        short stem sits inside the longer one. The bare substring test called
        that registered; a reference test does not."""
        graph = self._graph(
            {"zamber": True, "zamber-lattice": False},
            self.HEAD + "| zamber-lattice | 3.1.0 | [zamber-lattice](zamber-lattice.md) | 2026-09-09 |\n")
        r = run_lint(graph)
        out = r.stdout + r.stderr
        self.assertNotEqual(r.returncode, 0, f"substring of a sibling row must not count:\n{out}")
        self.assertIn("libraries/zamber.md: no row", out, out)

    def test_that_same_page_with_its_own_row_passes(self):
        """The same fixture, the omission repaired — the check must stay usable."""
        graph = self._graph(
            {"zamber": True, "zamber-lattice": False},
            self.HEAD
            + "| zamber | 1.4.0 | [zamber](zamber.md) | 2026-09-09 |\n"
            + "| zamber-lattice | 3.1.0 | [zamber-lattice](zamber-lattice.md) | 2026-09-09 |\n")
        r = run_lint(graph)
        self.assertEqual(r.returncode, 0, f"a genuinely indexed page must pass:\n{r.stdout}\n{r.stderr}")

    def test_substring_of_a_header_or_prose_is_not_a_row(self):
        """`beacon` occurs only in a column header and a sentence of prose."""
        graph = self._graph(
            {"beacon": True},
            "# Libraries index\n\nEach row links to the beacon-style wiki page.\n\n"
            "| Library | beacon notes | Page |\n|---|---|---|\n")
        r = run_lint(graph)
        out = r.stdout + r.stderr
        self.assertNotEqual(r.returncode, 0, f"header/prose mention must not count:\n{out}")
        self.assertIn("libraries/beacon.md: no row", out, out)

    def test_link_with_different_text_still_counts(self):
        """The rule is the link TARGET, not the link text: an index that links
        the page as `[wiki](zamber.md)` — or through the folder — is a row."""
        for target in ("zamber.md", "./zamber.md", "<zamber.md>",
                       "libraries/zamber.md", "zamber.md#pin"):
            with self.subTest(target=target):
                graph = self._graph(
                    {"zamber": True},
                    self.HEAD + f"| the wiki | 1.4.0 | [wiki page]({target}) | 2026-09-09 |\n")
                r = run_lint(graph)
                self.assertEqual(r.returncode, 0,
                                 f"link target {target} must count:\n{r.stdout}\n{r.stderr}")

    def test_named_cell_without_a_link_still_counts(self):
        """An index that names the library in its own cell and links nothing
        is thin, but it is a row — the check must not force a link."""
        graph = self._graph(
            {"zamber": True},
            self.HEAD + "| `zamber` | 1.4.0 | not written yet | 2026-09-09 |\n")
        r = run_lint(graph)
        self.assertEqual(r.returncode, 0, f"named cell must count:\n{r.stdout}\n{r.stderr}")

    def test_a_row_under_a_pending_heading_is_not_registration(self):
        """THE DEFECT, arriving through the structure instead of the string. A
        row in a pending table exists to record that the page has NOT been
        written, so reading it as registration makes the check green on
        precisely the omission it exists to catch — the same failure the
        substring test produced, one level up."""
        for heading in ("## Pending ingests", "## Planned", "## Unwritten",
                        "### Not yet ingested", "## To ingest", "## Backlog",
                        "## TODO"):
            with self.subTest(heading=heading):
                graph = self._graph(
                    {"zamber": True},
                    "# Libraries index\n\n" + heading + "\n\n" + self.TABLE
                    + "| zamber | — | [zamber](zamber.md) | — |\n")
                r = run_lint(graph)
                out = r.stdout + r.stderr
                self.assertNotEqual(r.returncode, 0,
                    f"a row under {heading!r} records the page's ABSENCE:\n{out}")
                self.assertIn("libraries/zamber.md: no row", out, out)

    def test_a_section_after_a_pending_one_registers_again(self):
        """Only the pending sections are skipped. A heading ends the section
        before it, so a real row below one still registers — otherwise the fix
        would turn every index with a backlog into a permanent red."""
        graph = self._graph(
            {"zamber": True},
            "# Libraries index\n\n## Pending ingests\n\n"
            + self.TABLE + "| something-else | — | — | — |\n\n"
            + "## Ingested\n\n" + self.TABLE
            + "| zamber | 1.4.0 | [zamber](zamber.md) | 2026-09-09 |\n")
        r = run_lint(graph)
        self.assertEqual(r.returncode, 0,
            f"a row outside the pending section is still a row:\n{r.stdout}\n{r.stderr}")

    def test_an_index_with_no_headings_registers_as_before(self):
        """The section rule adds a skip, never a requirement. An index that is
        one bare table — which is what the template ships — is unaffected."""
        graph = self._graph(
            {"zamber": True},
            self.HEAD + "| zamber | 1.4.0 | [zamber](zamber.md) | 2026-09-09 |\n")
        r = run_lint(graph)
        self.assertEqual(r.returncode, 0,
            f"a heading-less index must register exactly as before:\n{r.stdout}\n{r.stderr}")

    def test_a_differently_cased_row_still_counts(self):
        """An index is prose a person writes, and a row that titles the library
        the way its own docs do is the same row. Reading it case-sensitively
        reported no row where one plainly existed — the mirror of the substring
        hazard, and equally good at teaching a reader to stop believing the
        check. Both the cell form and the link target fold."""
        for row in ("| Zamber | 1.4.0 | not written yet | 2026-09-09 |",
                    "| the wiki | 1.4.0 | [wiki page](Zamber.md) | 2026-09-09 |"):
            with self.subTest(row=row):
                graph = self._graph({"zamber": True}, self.HEAD + row + "\n")
                r = run_lint(graph)
                self.assertEqual(r.returncode, 0,
                    f"a differently-cased row is the same row:\n{r.stdout}\n{r.stderr}")

    def test_the_pending_vocabulary_is_stated_in_the_schema(self):
        """The linter must not invent the vocabulary it keys on. `_schema.md` is
        what an author reads; a word the tool skips on and the contract never
        names is a rule nobody can follow."""
        src = GRAPH_LINT.read_text(encoding="utf-8")
        m = re.search(r"^PENDING_HEADINGS\s*=\s*\((.*?)\)", src, re.M | re.S)
        self.assertIsNotNone(m, "PENDING_HEADINGS is not a module-level tuple "
                                "in the shipped tool")
        words = re.findall(r'"([^"]+)"', m.group(1))
        self.assertTrue(words,
                        "the tool skips no section, so this check is vacuous")
        low = (GRAPH_LINT.parent / "_schema.md").read_text(
            encoding="utf-8").lower()
        for word in words:
            self.assertIn(word, low,
                f"graph-lint.py skips a section headed {word!r} and "
                f"templates/knowledge-graph/_schema.md never says so")


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


class StatusAndPlantTests(unittest.TestCase):
    """7.0.0: lifecycle status in frontmatter (rules 12–13) and the router's
    `plant:` block (rule 14). Against the pre-7.0.0 tool every negative case
    below passes lint — RED for the right reason — because status was prose
    and `plant:` was unknown."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="graph-lint-status-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    _n = 0

    def _graph(self, extra_nodes: dict | None = None, index_front: str | None = None, grown_marker=False) -> Path:
        # a fresh directory per graph: several tests build two graphs
        self._n += 1
        base = self.tmp / f"g{self._n}"
        base.mkdir()
        nodes = {"root": node_md("root", "root", owns=["root.map"])}
        nodes.update(extra_nodes or {})
        g = build_graph(base, nodes)
        front = index_front or ""
        if grown_marker:
            # `grown: true` in the router frontmatter marks a grown plant
            # (the ledger path is only trusted under a real docs/graph layout)
            front = ("---\ngrown: true\n" + front[4:]) if front.startswith("---\n") else "---\ngrown: true\n---\n"
        if front:
            idx = g / "index.md"
            idx.write_text(front + idx.read_text(encoding="utf-8"), encoding="utf-8")
        return g

    PLANT = ("---\nplant:\n  environment_class: ephemeral-test\n  commit_attribution: none\n"
             "  deliverable_language: en\n  comment_language: en\n---\n")

    def _node_with(self, node_id, kind, front_extra: str, body_extra: str = "") -> str:
        base = node_md(node_id, kind, owns=[f"{node_id}.fact"])
        # inject extra frontmatter lines before the closing '---'
        head, _, rest = base.partition("\n---\n")
        return head + "\n" + front_extra.rstrip("\n") + "\n---\n" + rest + body_extra

    def test_status_vocabulary_is_controlled(self):
        n = self._node_with("subsystem.a", "subsystem", "status: greenish\nstatus_date: 2026-01-01")
        r = run_lint(self._graph({"subsystem.a": n}, self.PLANT))
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertIn("status 'greenish' not in", r.stderr)

    def test_closed_requires_evidence(self):
        n = self._node_with("subsystem.a", "subsystem", "status: closed\nstatus_date: 2026-01-01")
        r = run_lint(self._graph({"subsystem.a": n}, self.PLANT))
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertIn("requires 'status_evidence'", r.stderr)

    def test_open_with_owner_passes(self):
        n = self._node_with("subsystem.a", "subsystem", "status: open\nstatus_date: 2026-01-01\nowner: acme-team")
        r = run_lint(self._graph({"subsystem.a": n}, self.PLANT))
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_body_status_may_not_disagree(self):
        n = self._node_with("subsystem.a", "subsystem", "status: open\nstatus_date: 2026-01-01\nowner: acme",
                            body_extra="\n\n## Status\n\n`closed`\n")
        r = run_lint(self._graph({"subsystem.a": n}, self.PLANT))
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertIn("one home", r.stderr)

    def test_deviation_kind_requires_standing_and_keys(self):
        bad = self._node_with("deviation.host-key", "deviation", "status: open\nstatus_date: 2026-01-01\nowner: acme")
        r = run_lint(self._graph({"deviation.host-key": bad}, self.PLANT))
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertIn("deviation status must be 'standing'", r.stderr)
        good = self._node_with("deviation.host-key", "deviation",
            "status: standing\nstatus_date: 2026-01-01\ndeparts_from: secrets.transport-trust\n"
            "reason: verification hangs first-boot provisioning\nscope: bootstrap only\n"
            "ends_when: fleet configured\nrecorded_in: ADR-0002")
        r = run_lint(self._graph({"deviation.host-key": good}, self.PLANT))
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_plant_block_missing_warns_on_adopted_fails_on_grown(self):
        r = run_lint(self._graph())                      # adopted: no ledger, no grown marker
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("warning: index.md: missing `plant:` block", r.stderr)
        r = run_lint(self._graph(grown_marker=True))     # grown: ledger present
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertIn("missing `plant:` block", r.stderr)

    def test_plant_environment_class_is_controlled(self):
        bad = self.PLANT.replace("ephemeral-test", "sorta-prod")
        r = run_lint(self._graph(index_front=bad, grown_marker=True))
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertIn("environment_class 'sorta-prod' not in", r.stderr)


class RootlessPlanTests(unittest.TestCase):
    """`--plan` on a pre-growth (rootless) graph with a task no node matches
    used to raise KeyError('root'); it must exit 0 with an empty LOAD set."""

    def test_plan_without_root_and_without_match_does_not_crash(self):
        tmp = Path(tempfile.mkdtemp(prefix="graph-lint-rootless-")); self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        g = build_graph(tmp, {"subsystem.only": node_md("subsystem.only", "subsystem", owns=["only.fact"])})
        # graph without a root: strip the root node build_graph may have added
        for f in (g / "nodes").glob("root.md"):
            f.unlink()
        r = subprocess.run([sys.executable, str(g / "graph-lint.py"), "--plan", "zebra quux nonsense"],
                           cwd=str(g), capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("LOAD (0 nodes", r.stdout)



# --------------------------------------------------------------------------
# 7.5.0 — the `expertise` kind and the lazy `composes:` edge.
#
# Contract map:
#   ComposesContractTests  -> the edge's own rules: targets resolve, both ends
#                             are expertise, no self-edge, acyclic on its own
#                             while the requires/composes PAIR is legal, the
#                             child's upward requires is mirrored downward, a
#                             node routes to some depth, a versioned slug
#                             exists only under its unversioned parent.
#   DescentTests           -> what --plan does with it. Every case asserts the
#                             PROVENANCE line or the not-loaded REASON, never
#                             bare membership, and every task is one the
#                             UNMODIFIED tool did not seed the child on (the
#                             wording was measured; see each docstring). A
#                             membership assertion here would pass with the
#                             descent code deleted, because seeding alone
#                             loads a child whose triggers beat the top-3 cut.
# --------------------------------------------------------------------------

EXPERTISE_KINDS_CONFIG = 'KIND_PREFIX = {}'   # expertise ships in KINDS itself


def expertise_family(**overrides) -> dict:
    """The parent/child shape every composes case needs: a subsystem whose
    name dominates a task, the stack expertise it requires, and two library
    expertises the parent composes under triggers of their own."""
    nodes = {
        "root": node_md("root", "root", requires=["subsystem.orders"],
                        owns=["root.map"]),
        "subsystem.orders": node_md(
            "subsystem.orders", "subsystem", requires=["expertise.dotnet"],
            owns=["orders.responsibility"],
            load_when=["orders service", "editing src/Orders/**"]),
        "expertise.dotnet": node_md(
            "expertise.dotnet", "expertise",
            composes=["expertise.ef-core", "expertise.serilog"],
            libraries=["dotnet"], owns=["dotnet.applicability"],
            load_when=["dotnet, csharp", "target framework, runtime"]),
        "expertise.ef-core": node_md(
            "expertise.ef-core", "expertise", requires=["expertise.dotnet"],
            libraries=["dotnet"], owns=["ef-core.applicability"],
            load_when=["entity framework, dbcontext", "entity mapping"]),
        "expertise.serilog": node_md(
            "expertise.serilog", "expertise", requires=["expertise.dotnet"],
            libraries=["dotnet"], owns=["serilog.applicability"],
            load_when=["structured logging, log sink", "enrichers"]),
    }
    nodes.update(overrides)
    return nodes


class ComposesContractTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(GRAPH_LINT.exists(), f"missing tool: {GRAPH_LINT}")
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def lint(self, nodes, **kw):
        kw.setdefault("libraries", ["dotnet"])
        return run_lint(build_graph(self.tmp, nodes, **kw))

    def test_expertise_family_lints_clean(self):
        """The shape every other case mutates is itself valid."""
        r = self.lint(expertise_family())
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_composes_target_must_resolve(self):
        nodes = expertise_family()
        nodes["expertise.dotnet"] = node_md(
            "expertise.dotnet", "expertise",
            composes=["expertise.ef-core", "expertise.serilog", "expertise.ghost"],
            libraries=["dotnet"], owns=["dotnet.applicability"])
        r = self.lint(nodes)
        self.assertEqual(r.returncode, 1)
        self.assertIn("composes → unknown node 'expertise.ghost'", r.stderr)

    def test_composes_self_edge_fails(self):
        nodes = expertise_family()
        nodes["expertise.ef-core"] = node_md(
            "expertise.ef-core", "expertise", requires=["expertise.dotnet"],
            composes=["expertise.ef-core"], libraries=["dotnet"],
            owns=["ef-core.applicability"])
        r = self.lint(nodes)
        self.assertEqual(r.returncode, 1)
        self.assertIn("composes → itself", r.stderr)

    def test_composes_only_between_expertise_nodes(self):
        """A subsystem that wants a stack's depth `requires` its expertise
        node; letting any kind compose makes --plan's result unpredictable."""
        nodes = expertise_family()
        nodes["subsystem.orders"] = node_md(
            "subsystem.orders", "subsystem", requires=["expertise.dotnet"],
            composes=["expertise.ef-core"], owns=["orders.responsibility"])
        r = self.lint(nodes)
        self.assertEqual(r.returncode, 1)
        self.assertIn("composes joins expertise nodes only", r.stderr)

    def test_composes_cycle_fails(self):
        nodes = expertise_family()
        nodes["expertise.ef-core"] = node_md(
            "expertise.ef-core", "expertise", requires=["expertise.dotnet"],
            composes=["expertise.dotnet"], libraries=["dotnet"],
            owns=["ef-core.applicability"])
        r = self.lint(nodes)
        self.assertEqual(r.returncode, 1)
        self.assertIn("composes cycle:", r.stderr)

    def test_requires_composes_pair_is_not_a_cycle(self):
        """`parent composes child` + `child requires parent` is the INTENDED
        shape: the eager edge points up, the lazy one down. Checking the union
        would reject every well-formed family."""
        r = self.lint(expertise_family())
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn("cycle", r.stderr)

    def test_child_requires_parent_needs_reciprocal_composes(self):
        """A child added without touching its parent is the failure the
        downward edge would otherwise allow; lint names the line to add."""
        nodes = expertise_family()
        nodes["expertise.dotnet"] = node_md(
            "expertise.dotnet", "expertise", composes=["expertise.ef-core"],
            libraries=["dotnet"], owns=["dotnet.applicability"])
        r = self.lint(nodes)
        self.assertEqual(r.returncode, 1)
        self.assertIn("does not compose it", r.stderr)
        self.assertIn("expertise.serilog", r.stderr)

    def test_expertise_without_depth_edge_fails(self):
        """It owns applicability and composition only, so with no libraries/
        artifacts edge it routes to nothing."""
        nodes = expertise_family()
        nodes["expertise.serilog"] = node_md(
            "expertise.serilog", "expertise", requires=["expertise.dotnet"],
            owns=["serilog.applicability"])
        r = self.lint(nodes)
        self.assertEqual(r.returncode, 1)
        self.assertIn("routes to nothing", r.stderr)

    def test_versioned_slug_only_as_composed_child(self):
        """A -<digits> slug is legal under the unversioned parent that
        composes it, and nowhere else — the pin's home is libraries/."""
        ok = expertise_family()
        ok["expertise.dotnet"] = node_md(
            "expertise.dotnet", "expertise",
            composes=["expertise.ef-core", "expertise.serilog",
                      "expertise.dotnet-10"],
            libraries=["dotnet"], owns=["dotnet.applicability"],
            load_when=["dotnet, csharp", "target framework, runtime"])
        ok["expertise.dotnet-10"] = node_md(
            "expertise.dotnet-10", "expertise", requires=["expertise.dotnet"],
            libraries=["dotnet"], owns=["dotnet-10.applicability"],
            load_when=["net10.0, dotnet 10 target"])
        r_ok = self.lint(ok)
        self.assertEqual(r_ok.returncode, 0, r_ok.stderr)

        orphan = expertise_family()
        orphan["expertise.orphan-10"] = node_md(
            "expertise.orphan-10", "expertise", requires=["expertise.dotnet"],
            libraries=["dotnet"], owns=["orphan-10.applicability"])
        r = self.lint(orphan)
        self.assertEqual(r.returncode, 1)
        self.assertIn("version-qualified expertise slug", r.stderr)

    def test_reachable_only_through_composes_passes(self):
        """Reachability follows all three edges. The child is deliberately
        UNLISTED in index.md — listing alone satisfies the rule, so a listed
        node could never prove the traversal reads `composes`."""
        nodes = expertise_family()
        listed = [n for n in nodes if n != "expertise.serilog"]
        r = self.lint(nodes, listed=listed)
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_shared_sibling_trigger_warns(self):
        """A term two siblings share is family vocabulary: it belongs on the
        parent, where it cannot descend either of them."""
        nodes = expertise_family()
        nodes["expertise.serilog"] = node_md(
            "expertise.serilog", "expertise", requires=["expertise.dotnet"],
            libraries=["dotnet"], owns=["serilog.applicability"],
            load_when=["structured logging", "entity mapping"])
        r = self.lint(nodes)
        self.assertIn("is shared with", r.stderr)

    def test_composes_target_end_must_be_expertise(self):
        """Rule 15 says BOTH ends. The source-end case uses a subsystem that
        composes; this is the mirror — an expertise node composing something
        that is not one, which a source-only check would let through."""
        nodes = expertise_family()
        nodes["expertise.dotnet"] = node_md(
            "expertise.dotnet", "expertise",
            composes=["expertise.ef-core", "expertise.serilog", "subsystem.orders"],
            libraries=["dotnet"], owns=["dotnet.applicability"])
        r = self.lint(nodes)
        self.assertEqual(r.returncode, 1)
        self.assertIn("composes joins expertise nodes only", r.stderr)
        self.assertIn("composes to subsystem.orders", r.stderr)

    def test_generic_child_trigger_warns(self):
        """A term most of the graph carries cannot say this child is what the
        task is about, so it descends on tasks that are not."""
        nodes = expertise_family()
        nodes["expertise.serilog"] = node_md(
            "expertise.serilog", "expertise", requires=["expertise.dotnet"],
            libraries=["dotnet"], owns=["serilog.applicability"],
            load_when=["structured logging", "pipeline"])
        for i in range(4):
            nodes[f"subsystem.svc{i}"] = node_md(
                f"subsystem.svc{i}", "subsystem", owns=[f"svc{i}.responsibility"],
                load_when=["pipeline"])
        r = self.lint(nodes)
        self.assertIn("too generic", r.stderr)
        self.assertIn("'pipeline'", r.stderr)

    def test_parent_terms_do_not_warn(self):
        """Two things must NOT warn: a term the parent already carries (that
        is what family vocabulary is for), and a sub-3-character token such as
        the `0` in `net8.0`, which no task term can ever match."""
        nodes = expertise_family()
        nodes["expertise.dotnet"] = node_md(
            "expertise.dotnet", "expertise",
            composes=["expertise.dotnet-8", "expertise.dotnet-10"],
            libraries=["dotnet"], owns=["dotnet.applicability"],
            load_when=["dotnet, csharp", "target framework, runtime"])
        for major in (8, 10):
            nodes[f"expertise.dotnet-{major}"] = node_md(
                f"expertise.dotnet-{major}", "expertise",
                requires=["expertise.dotnet"], libraries=["dotnet"],
                owns=[f"dotnet-{major}.applicability"],
                load_when=[f"net{major}.0, dotnet {major} target"])
        del nodes["expertise.ef-core"], nodes["expertise.serilog"]
        r = self.lint(nodes)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn("is shared with", r.stderr)


class DescentTests(unittest.TestCase):
    """--plan descends only into the children the task names specifically.

    Every task below was measured against the UNMODIFIED tool: it loads the
    subsystem and the parent expertise, and NOT the child. That is the only
    regime in which descent decides anything — a task that seeds the child
    directly would pass these assertions with the descent code removed.
    """

    def setUp(self):
        self.assertTrue(GRAPH_LINT.exists(), f"missing tool: {GRAPH_LINT}")
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def plan(self, task, nodes=None, **kw):
        kw.setdefault("libraries", ["dotnet"])
        g = build_graph(self.tmp, nodes or expertise_family(), **kw)
        r = subprocess.run([sys.executable, str(g / "graph-lint.py"), "--plan", task],
                           cwd=str(g), capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout

    def test_plan_descends_on_specific_term(self):
        """`mapping` is ef-core's own word; unmodified LOAD is dotnet+orders."""
        out = self.plan("in the orders service, fix the mapping")
        self.assertIn('expertise.ef-core', out)
        self.assertIn('composed by expertise.dotnet on "mapping"', out)

    def test_plan_leaves_the_unnamed_sibling_with_a_reason(self):
        out = self.plan("in the orders service, fix the mapping")
        self.assertRegex(
            out, r"expertise\.serilog\s+composed by expertise\.dotnet; "
                 r"no task term specific to it")

    def test_plan_descends_from_required_node(self):
        """The parent is not a seed here — it arrives through the subsystem's
        `requires`. Descent must work from a node the closure pulled in, which
        is what makes an agent's ordinary task reach library expertise."""
        out = self.plan("in the orders service, add a sink")
        self.assertIn('expertise.serilog', out)
        self.assertIn('composed by expertise.dotnet on "sink"', out)
        self.assertIn("subsystem.orders", out)

    def test_plan_ignores_family_vocabulary(self):
        """serilog carries the parent's own word `dotnet`. A task naming it
        must NOT descend serilog: family vocabulary sits on the parent by
        construction, so the child's own vocabulary excludes it."""
        nodes = expertise_family()
        nodes["expertise.serilog"] = node_md(
            "expertise.serilog", "expertise", requires=["expertise.dotnet"],
            libraries=["dotnet"], owns=["serilog.applicability"],
            load_when=["structured logging, log sink", "dotnet logging"])
        out = self.plan("in the orders service, fix the dotnet mapping", nodes)
        self.assertNotIn("composed by expertise.dotnet on \"dotnet\"", out)
        self.assertRegex(out, r"expertise\.serilog\s+composed by .*no task term")

    def test_plan_descent_never_folds(self):
        """Seeding folds prefixes; descent does not. `migrating` is a
        six-character prefix of the child's `migration`, and must not compose
        it — otherwise "migrating the CI runner" drags in schema knowledge."""
        nodes = expertise_family()
        nodes["expertise.ef-core"] = node_md(
            "expertise.ef-core", "expertise", requires=["expertise.dotnet"],
            composes=["expertise.ef-migrations"], libraries=["dotnet"],
            owns=["ef-core.applicability"],
            load_when=["entity framework, dbcontext", "entity mapping"])
        nodes["expertise.ef-migrations"] = node_md(
            "expertise.ef-migrations", "expertise",
            requires=["expertise.ef-core"], libraries=["dotnet"],
            owns=["ef-migrations.applicability"],
            load_when=["add a migration, migration script"])
        out = self.plan(
            "in the orders service, editing the dbcontext, migrating the runner",
            nodes)
        self.assertIn('composed by expertise.dotnet on "dbcontext"', out)
        self.assertRegex(out, r"expertise\.ef-migrations\s+composed by .*no task term")

    def test_plan_descends_two_levels_each_on_own_term(self):
        """Recursion falls out of the rule: the child becomes the parent for
        its own children, and each level needs its own specific term."""
        nodes = expertise_family()
        nodes["expertise.ef-core"] = node_md(
            "expertise.ef-core", "expertise", requires=["expertise.dotnet"],
            composes=["expertise.ef-migrations"], libraries=["dotnet"],
            owns=["ef-core.applicability"],
            load_when=["entity framework, dbcontext", "entity mapping"])
        nodes["expertise.ef-migrations"] = node_md(
            "expertise.ef-migrations", "expertise",
            requires=["expertise.ef-core"], libraries=["dotnet"],
            owns=["ef-migrations.applicability"],
            load_when=["add a migration, migration script"])
        # The second-level term is "script", not "migration", and the reason is
        # worth stating: `migration` is a word in the CHILD'S OWN ID
        # (`expertise.ef-migrations`), and a node whose name matches the task is
        # SEEDED, not descended to. That was invisible while an inflection
        # scored half — `migration` reached `migrations` at strength 1, worth 6,
        # under the floor — and became visible the moment inflections scored as
        # the word they inflect, which lifted it to 12 and made the node an
        # entry. The node being found by its own name is the router working;
        # this test is about DESCENT, so it uses a term the child holds in its
        # `load_when` and not in its name.
        out = self.plan(
            "in the orders service, editing the dbcontext, run the script",
            nodes)
        self.assertIn('composed by expertise.dotnet on "dbcontext"', out)
        self.assertIn('composed by expertise.ef-core on "script"', out)

    def test_plan_selects_major_by_tfm_token(self):
        """Two majors in play: the unversioned parent composes one child per
        major, and the target-framework token the developer types picks it.

        The task names the subsystem's path glob deliberately. Without it the
        pre-7.5.0 tool SEEDS `expertise.dotnet-10` on this fixture (measured),
        and the assertion below would pass with descent deleted."""
        nodes = expertise_family()
        nodes["expertise.dotnet"] = node_md(
            "expertise.dotnet", "expertise",
            composes=["expertise.ef-core", "expertise.serilog",
                      "expertise.dotnet-8", "expertise.dotnet-10"],
            libraries=["dotnet"], owns=["dotnet.applicability"],
            load_when=["dotnet, csharp", "target framework, runtime"])
        for major in (8, 10):
            nodes[f"expertise.dotnet-{major}"] = node_md(
                f"expertise.dotnet-{major}", "expertise",
                requires=["expertise.dotnet"], libraries=["dotnet"],
                owns=[f"dotnet-{major}.applicability"],
                load_when=[f"net{major}.0, dotnet {major} target"])
        out = self.plan(
            "in the orders service, editing src/Orders/**, target net10.0", nodes)
        # The WHOLE token, not a piece of it. This read `"net10"` while the
        # load_when says `net10.0`: the router split on `.` and kept both
        # pieces at full strength, so a child could be descended into on half
        # of its own version token — the same shape that let `chain`, taken
        # from `supply-chain`, speak for the security agent. `net10` still
        # matches at the fragment tier, so a task that writes it without the
        # `.0` is not lost; it simply cannot clear the standalone bar descent
        # requires on its own.
        self.assertIn('composed by expertise.dotnet on "net10.0"', out)
        self.assertRegex(out, r"expertise\.dotnet-8\s+composed by .*no task term")

    def test_plan_reports_not_loaded_with_reason(self):
        """Peers and un-composed children share one NOT LOADED section, each
        line carrying why it stayed out."""
        nodes = expertise_family()
        nodes["subsystem.orders"] = node_md(
            "subsystem.orders", "subsystem", requires=["expertise.dotnet"],
            peers=["subsystem.billing"], owns=["orders.responsibility"],
            load_when=["orders service", "editing src/Orders/**"])
        nodes["subsystem.billing"] = node_md(
            "subsystem.billing", "subsystem", owns=["billing.responsibility"],
            load_when=["billing service"])
        out = self.plan("in the orders service, fix the mapping", nodes)
        self.assertIn("NOT LOADED (with the reason", out)
        self.assertRegex(out, r"subsystem\.billing\s+peer of subsystem\.orders")
        self.assertRegex(out, r"expertise\.serilog\s+composed by .*no task term")

    def test_plan_reports_a_top_scoring_seed_as_an_entry(self):
        """A seed is a seed however it is reached. The closure stack is LIFO
        over seeds sorted best-first, so a child that outscores its own
        subsystem is popped through the parent chain — and would be reported
        as composed. The load set would be right and the account of it wrong,
        which is the one thing the provenance line exists to give."""
        out = self.plan("entity mapping dbcontext orders")
        line = next(l for l in out.splitlines()
                    if l.strip().startswith("expertise.ef-core"))
        self.assertNotIn("composed by", line)

    def test_plan_warns_on_wide_descent(self):
        """A parent handing over most of a real menu at once says the task or
        the triggers are too generic, and the notice is what makes that
        visible instead of merely expensive. A single-child parent must NOT
        trip it — that is an ordinary descent, not a symptom."""
        nodes = expertise_family()
        nodes["expertise.dotnet"] = node_md(
            "expertise.dotnet", "expertise",
            composes=["expertise.ef-core", "expertise.serilog", "expertise.polly"],
            libraries=["dotnet"], owns=["dotnet.applicability"],
            load_when=["dotnet, csharp"])
        nodes["expertise.polly"] = node_md(
            "expertise.polly", "expertise", requires=["expertise.dotnet"],
            libraries=["dotnet"], owns=["polly.applicability"],
            load_when=["retry policy, circuit breaker"])
        out = self.plan("in the orders service, the mapping, the sink, the "
                        "retry policy", nodes)
        self.assertIn("wide descent from expertise.dotnet: 3 of 3 children", out)

        narrow = expertise_family()
        narrow["expertise.dotnet"] = node_md(
            "expertise.dotnet", "expertise", composes=["expertise.ef-core"],
            libraries=["dotnet"], owns=["dotnet.applicability"],
            load_when=["dotnet, csharp"])
        del narrow["expertise.serilog"]
        self.assertNotIn("wide descent", self.plan(
            "in the orders service, fix the mapping", narrow))

    def test_plan_without_composes_is_unchanged(self):
        """A graph carrying no `composes:` routes exactly as it did before
        7.5.0. The golden is over the resolved ID SETS, not stdout: the
        printed shape changed on purpose (reasons, provenance), the routing
        did not. Sets captured from the pre-7.5.0 tool on this fixture."""
        nodes = {
            "root": node_md("root", "root", requires=["subsystem.orders"],
                            owns=["root.map"]),
            "subsystem.orders": node_md(
                "subsystem.orders", "subsystem", requires=["stack.dotnet"],
                peers=["subsystem.billing"], owns=["orders.responsibility"],
                load_when=["orders service", "editing src/Orders/**"]),
            "stack.dotnet": node_md("stack.dotnet", "stack",
                                    owns=["dotnet.conventions"]),
            "subsystem.billing": node_md("subsystem.billing", "subsystem",
                                         owns=["billing.responsibility"],
                                         load_when=["billing service"]),
        }
        out = self.plan("in the orders service, fix the mapping", nodes)
        load, not_loaded = [], []
        section = None
        for line in out.splitlines():
            if line.startswith("LOAD ("):
                section = load
            elif line.startswith("NOT LOADED"):
                section = not_loaded
            elif section is not None and line.startswith("  "):
                section.append(line.split()[0])
        self.assertEqual(set(load), {"subsystem.orders", "stack.dotnet"})
        self.assertEqual(set(not_loaded), {"subsystem.billing"})


# ==========================================================================
# SPEC-0001-gate-assertion-floor (docs/graph/specs/), increments 10-12.
#
# The version-leakage rule is "every version FACT lives in libraries/", and
# docs/graph/index.md:66-74 states it with the boundary that makes it
# checkable: a release identifier MAY sit in a node's ROUTING surface as a
# keyword without the node asserting anything. check_version_leakage reads
# `n.body` and nothing else, so the rule holds in the body and evaporates one
# line up; and VERSION_RE wants a dotted-numeric core, so `RFC 8259` in a body
# is a fact nothing sees.
#
# Each test's NAME carries the contract slug. spec-lint.py credits a slug found
# anywhere under Cypress/tests/, comments included, and three contracts once
# went "covered" on a docstring — so the slug goes where the code is. The
# leading `test` with no underscore before the slug is deliberate: spec-lint's
# boundary is `(?<![A-Z0-9_])`, and `test_GRAPH_LINT_...` would not match.
# ==========================================================================


def node_with_frontmatter_key(node_id: str, kind: str, key: str, value: str) -> str:
    """A schema-valid node carrying `key: value` in its frontmatter, with the
    body left saying nothing about any version."""
    text = node_md(node_id, kind)
    if key == "title":
        return text.replace(f"title: {node_id} node", f"title: {value}", 1)
    return text.replace("load_when:", f"{key}: {value}\nload_when:", 1)


class FrontmatterVersionPositionTests(unittest.TestCase):
    """SPEC-0001-gate-assertion-floor §4/§6: where a version token is written
    decides whether it is an assertion or a routing handle."""

    def setUp(self):
        self.assertTrue(GRAPH_LINT.exists(), f"missing tool: {GRAPH_LINT}")
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def _lint(self, alpha: str):
        nodes = {
            "root": node_md("root", "root", requires=["subsystem.alpha"]),
            "subsystem.alpha": alpha,
        }
        return run_lint(build_graph(self.tmp, nodes))

    def testGRAPH_LINT_FRONTMATTER_ASSERTION_PIN_IS_A_LEAK(self):
        """A pin in `title:` is a claim the node is making, and the one-home
        rule does not stop at the frontmatter fence. Moving a body pin up three
        lines is today a way to make the check stop seeing it."""
        alpha = node_with_frontmatter_key(
            "subsystem.alpha", "subsystem", "title",
            "the alpha surface, pinned at 2.7.2")
        r = self._lint(alpha)
        out = r.stdout + r.stderr
        self.assertNotEqual(r.returncode, 0,
                            f"a version pin in an assertion-position "
                            f"frontmatter key must fail:\n{out}")
        self.assertIn("version pin", out, out)
        self.assertIn("subsystem.alpha", out, out)
        self.assertIn("title", out,
                      f"the finding must name the frontmatter key, not a body "
                      f"line:\n{out}")

    def testGRAPH_LINT_LOAD_WHEN_KEYWORD_IS_NOT_A_LEAK(self):
        """`load_when:` is routing. expertise.json carries `draft-07` and
        expertise.bash carries `bash 3.2 floor` so that a task naming either
        routes somewhere; neither node asserts what the project uses.

        This is the guard, not the catch: it is green before the change and
        must stay green after it. A check that scanned the whole frontmatter
        would turn this plant's own graph red on two live nodes, and `3.2` is
        a token today's VERSION_RE already matches — asserted below, so this
        green is a statement about position and not about an empty fixture."""
        src = GRAPH_LINT.read_text(encoding="utf-8")
        version_re = re.compile(
            re.search(r'^VERSION_RE = re\.compile\(r"(.+)"\)$', src,
                      re.M).group(1))
        self.assertTrue(version_re.search("bash 3.2 floor"),
                        "the fixture below is only a trap if VERSION_RE can "
                        "match the token it hides in load_when")

        for value in ('["json, $schema, draft-07"]', '["bash 3.2 floor"]'):
            with self.subTest(load_when=value):
                alpha = node_md("subsystem.alpha", "subsystem")
                alpha = alpha.replace(
                    "load_when:\n  - work on subsystem.alpha",
                    f"load_when: {value}", 1)
                r = self._lint(alpha)
                out = r.stdout + r.stderr
                self.assertNotIn("version pin", out,
                                 f"a release identifier used as a routing "
                                 f"keyword is not a leak:\n{out}")
                self.assertEqual(r.returncode, 0, out)

    def testGRAPH_LINT_NON_DOTTED_RELEASE_IN_BODY_IS_A_LEAK(self):
        """A release identifier with no dotted-numeric core is still a release
        identifier. `draft-07`, `RFC 8259` and `STD 90` are asserted in bodies
        today and nothing sees them.

        `0.29-gfm` is the control: §6 files it under `undotted`, but its
        `0.29` core means VERSION_RE already catches it, so it must be caught
        before and after — it is what tells a reader this test ran at all."""
        for token in ("draft-07", "RFC 8259", "STD 90", "0.29-gfm"):
            with self.subTest(token=token):
                alpha = node_md("subsystem.alpha", "subsystem")
                alpha = alpha.replace(
                    "plain words.", f"plain words. The wire format is {token} here.", 1)
                r = self._lint(alpha)
                out = r.stdout + r.stderr
                self.assertNotEqual(r.returncode, 0,
                                    f"{token!r} asserted in a body is a leak:\n{out}")
                self.assertIn("version pin", out, out)
                self.assertIn(token, out,
                              f"the finding must name the identifier it found:\n{out}")

    def testGRAPH_LINT_NON_DOTTED_RELEASE_IN_A_CODE_SPAN_IS_STILL_EXEMPT(self):
        """The `And` of the contract above: quoting a real config line is not
        restating a fact, so the same identifier inside a code span passes.
        Green before and after — it is the guard on the widened regex."""
        alpha = node_md("subsystem.alpha", "subsystem")
        alpha = alpha.replace(
            "plain words.",
            "plain words. The schema line reads `\"$schema\": draft-07` verbatim.", 1)
        r = self._lint(alpha)
        self.assertEqual(r.returncode, 0,
                         f"a code span must stay exempt:\n{r.stdout}\n{r.stderr}")


class BudgetMeasuresTheWholeFileTests(unittest.TestCase):
    """SPEC-0001-gate-assertion-floor §4 GRAPH_LINT_BUDGET_COUNTS_FRONTMATTER:
    `est_tokens` is the budget for the file a loader reads, and the proxy
    measures the body only. A node can carry a large frontmatter and stay in
    band on a figure that describes less than half of what it costs."""

    def setUp(self):
        self.assertTrue(GRAPH_LINT.exists(), f"missing tool: {GRAPH_LINT}")
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def testGRAPH_LINT_BUDGET_COUNTS_FRONTMATTER(self):
        # A node whose routing surface dwarfs its body: 60 load_when triggers,
        # a short paragraph. Nothing here is malformed; it is simply a file a
        # loader pays several hundred tokens for while `est_tokens` describes
        # the paragraph.
        triggers = [f"routing trigger number {i} for the alpha surface"
                    for i in range(60)]
        alpha = node_md("subsystem.alpha", "subsystem", load_when=triggers)
        head, _, body = alpha.partition("\n---\n\n")
        frontmatter_text = head + "\n---\n"
        body_tokens = int(len(body.split()) * 1.35)
        whole_tokens = int(len((frontmatter_text + body).split()) * 1.35)
        self.assertGreater(whole_tokens, 2 * body_tokens,
                           "the fixture must actually separate the two "
                           "measurements, or this test proves nothing")

        # est_tokens is set to the BODY figure — in band today, out of band the
        # moment the frontmatter a loader reads is counted.
        alpha = re.sub(r"^est_tokens: \d+$", f"est_tokens: {body_tokens}",
                       alpha, count=1, flags=re.M)
        nodes = {
            "root": node_md("root", "root", requires=["subsystem.alpha"]),
            "subsystem.alpha": alpha,
        }
        r = run_lint(build_graph(self.tmp, nodes))
        out = r.stdout + r.stderr
        self.assertNotEqual(
            r.returncode, 0,
            f"est_tokens={body_tokens} describes the body; the file measures "
            f"~{whole_tokens} and must be judged against that:\n{out}")
        measured = re.search(r"est_tokens=\d+ but .*?~(\d+)", out)
        self.assertIsNotNone(measured, f"no measured figure in the verdict:\n{out}")
        self.assertEqual(int(measured.group(1)), whole_tokens,
                         f"the figure compared against est_tokens must be the "
                         f"whole-file one ({whole_tokens}):\n{out}")
        self.assertNotIn(
            "body measures", out,
            "the verdict must not describe a whole-file figure as the body's, "
            "or est_tokens goes on being read as a body-only number")


class SeedAndPlantCopyAgreeTests(unittest.TestCase):
    """SPEC-0001-gate-assertion-floor §4 GRAPH_LINT_SEED_COPY_AGREES_WITH_PLANT_COPY:
    the engine ships twice — templates/knowledge-graph/graph-lint.py, and the
    copy install.sh writes into a plant's docs/graph/. Increment 10 edits one
    of them and increment 12 ports it, so the window in between is exactly when
    the two disagree.

    The contract is behavioural, not byte-level: the two differ today only by a
    line-wrap of KINDS, which is not a failure. And agreement alone is the
    weaker half — two copies that both ignore the rule agree perfectly, which
    is the warning the census hangs on test_metadata_equivalence.py. So the
    fixture tree is one the contracts above say must FAIL, and the assertion is
    that both copies fail it the same way."""

    def setUp(self):
        self.assertTrue(GRAPH_LINT.exists(), f"missing tool: {GRAPH_LINT}")
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def _installed_copy(self) -> Path:
        """The plant-side copy, taken from a disposable install of this seed
        rather than from a path outside the tree under test. A suite that
        resolved its input from the host it happens to sit inside is the defect
        grill.md §12 row 10 is open on; this one stays hermetic."""
        plant = self.tmp / "plant"
        plant.mkdir(parents=True, exist_ok=True)
        r = subprocess.run(["bash", str(SEED / "install.sh"), "claude-code",
                            "--project-dir", str(plant)],
                           capture_output=True, text=True, timeout=300)
        self.assertEqual(r.returncode, 0, f"install failed:\n{r.stdout}\n{r.stderr}")
        copy = plant / "docs" / "graph" / "graph-lint.py"
        self.assertTrue(copy.is_file(), f"no installed graph-lint at {copy}")
        return copy

    def _beside(self, tool: Path, graph: Path, name: str) -> Path:
        """Put `tool` INSIDE `graph` and hand back the path there.

        `graph-lint.py:68` is `HERE = Path(__file__).resolve().parent`: the
        tool lints the graph beside ITSELF and ignores the working directory.
        Running the installed copy where it was installed therefore lints the
        freshly installed plant graph, not the fixture — two engines reading
        two different trees, which is a comparison of nothing. The engine is a
        single self-contained stdlib file, so relocating it is the whole of
        what it takes to point both at one tree; the copy still comes out of
        the disposable install, so the provenance the docstring above argues
        for survives."""
        dest = graph / name
        shutil.copy(tool, dest)
        return dest

    def testGRAPH_LINT_SEED_COPY_AGREES_WITH_PLANT_COPY(self):
        alpha = node_md("subsystem.alpha", "subsystem")
        alpha = alpha.replace(f"title: subsystem.alpha node",
                              "title: the alpha surface, pinned at 2.7.2", 1)
        alpha = alpha.replace("plain words.",
                              "plain words. The wire format is RFC 8259 here.", 1)
        nodes = {
            "root": node_md("root", "root", requires=["subsystem.alpha"]),
            "subsystem.alpha": alpha,
        }
        graph = build_graph(self.tmp, nodes)          # carries the seed copy
        plant_copy = self._beside(self._installed_copy(), graph,
                                  "graph-lint-installed.py")

        def verdict(tool: Path):
            r = subprocess.run([sys.executable, str(tool)], cwd=str(graph),
                               capture_output=True, text=True, timeout=60)
            # graph-lint prints one error per line as `  \u2717 <text>`
            # (graph-lint.py:1174) and one warning as `  ! warning: <text>`
            # (:1170). This filter looked for a leading "-", which no line of
            # either tool has ever carried, so the error-set assertion below
            # compared two empty sets and could not fail. Warnings are left
            # out deliberately: the fixture graph has no `plant:` block and
            # both copies say so, which is noise about the fixture rather
            # than a difference between the engines.
            errs = {ln.strip().lstrip("\u2717").strip()
                    for ln in (r.stdout + r.stderr).splitlines()
                    if ln.strip().startswith("\u2717")}
            return r.returncode, errs

        seed_rc, seed_errs = verdict(graph / "graph-lint.py")
        plant_rc, plant_errs = verdict(plant_copy)

        self.assertEqual(seed_rc, plant_rc,
                         f"the two copies disagree on the exit code: "
                         f"seed={seed_rc} plant={plant_rc}")
        self.assertEqual(seed_errs, plant_errs,
                         f"the two copies disagree on the error set:\n"
                         f"  seed only:  {sorted(seed_errs - plant_errs)}\n"
                         f"  plant only: {sorted(plant_errs - seed_errs)}")
        self.assertTrue(
            seed_errs,
            "both copies exited non-zero and neither printed a line this test "
            "could read as an error. The set comparison above then passes on "
            "two empty sets, which is the vacuous-agreement failure this case "
            "exists to refuse — check the verdict parser against "
            "graph-lint.py's output format before trusting any green here")
        self.assertNotEqual(
            seed_rc, 0,
            "both copies agreed that a node asserting `2.7.2` in `title:` and "
            "`RFC 8259` in its body is clean. Agreement between two copies "
            "that both ignore the rule is agreement about nothing")


class FrontmatterPortableTests(unittest.TestCase):
    """A plant node's frontmatter must parse under a strict-YAML loader too, not
    only the lenient reader. Mirrors seed-lint's check_frontmatter_is_portable_yaml
    so a node authored into a plant by grow, graft or by hand cannot carry an
    inner ': ' that a strict-YAML host (Prime Agent) reads as a nested mapping
    and drops."""

    def setUp(self):
        self.assertTrue(GRAPH_LINT.exists(), f"missing tool: {GRAPH_LINT}")
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def _graph_with_title(self, title_line: str) -> Path:
        node = node_md("subsystem.alpha", "subsystem")
        node = node.replace("title: subsystem.alpha node", title_line)
        nodes = {
            "root": node_md("root", "root", requires=["subsystem.alpha"]),
            "subsystem.alpha": node,
        }
        return build_graph(self.tmp, nodes)

    def test_inner_colon_space_in_title_is_caught(self):
        """An unquoted title carrying an inner ': ' fails the portability check."""
        r = run_lint(self._graph_with_title("title: subsystem.alpha node: the boundary"))
        out = r.stdout + r.stderr
        self.assertNotEqual(r.returncode, 0, f"inner ': ' must fail:\n{out}")
        self.assertIn("strict-YAML loader", out, out)

    def test_reworded_title_passes(self):
        """The same clause reworded to an ASCII dash is on the readers' overlap."""
        r = run_lint(self._graph_with_title("title: subsystem.alpha node - the boundary"))
        self.assertEqual(r.returncode, 0, f"reworded title must pass:\n{r.stdout}\n{r.stderr}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
