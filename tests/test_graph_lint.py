#!/usr/bin/env python3
"""Tests for graph-lint.py: the node-graph contract and the `--plan` router.

Each case runs the tool through its CLI against a hermetic temp graph, on the
stdlib alone: `python3 tests/test_graph_lint.py`.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent          # <seed>/tests
SEED = HERE.parent
GRAPH_LINT = SEED / "templates" / "knowledge-graph" / "graph-lint.py"

# The tool's shipped config line; a case rewrites it to inject a mapping.
DEFAULT_CONFIG_LINE = "KIND_PREFIX = {}"


def run_lint(graph_dir: Path, *args: str) -> subprocess.CompletedProcess:
    """Run the graph-lint.py copy inside graph_dir, as a plant runs it."""
    return subprocess.run(
        [sys.executable, str(graph_dir / "graph-lint.py"), *args],
        cwd=str(graph_dir),
        capture_output=True,
        text=True,
        timeout=60,
    )


def node_md(node_id: str, kind: str, *, requires=(), owns=None, peers=(),
            composes=(), libraries=(), artifacts=(), load_when=None) -> str:
    """A minimal, schema-valid tier-2 node. `est_tokens` is measured on the
    whole rendered file. The body has more words than any frontmatter this
    helper emits, so the figure stays inside the 2x band either way."""
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
    # The figure is one word whatever its digits. 1.35 is graph-lint.py's
    # own BODY_TOKENS_PER_WORD.
    est = int(len(text.split()) * 1.35)
    return text.replace("est_tokens: 0", f"est_tokens: {est}", 1)


def build_graph(tmp: Path, nodes: dict, *, config_line: str | None = None,
                listed=None, libraries=()) -> Path:
    """Write <tmp>/graph{,N}/ with the tool, its frontmatter reader, index.md
    and nodes/*.md. `nodes` maps id -> text. `listed` narrows the ids index.md
    names (default: all). `libraries` names wiki pages to create."""
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
    (graph / "frontmatter.py").write_text(
        (SEED / "templates" / "knowledge-graph" / "frontmatter.py").read_text(encoding="utf-8"),
        encoding="utf-8")

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


# One fresh install of this seed, shared by the cases that need a plant.
_INSTALL: dict = {}


def setUpModule():
    tmp = tempfile.TemporaryDirectory()
    plant = Path(tmp.name) / "plant"
    plant.mkdir(parents=True)
    r = subprocess.run(["bash", str(SEED / "install.sh"), "claude-code",
                        "--project-dir", str(plant)],
                       capture_output=True, text=True, timeout=300)
    _INSTALL.update(tmp=tmp, plant=plant, result=r)


def tearDownModule():
    _INSTALL["tmp"].cleanup()


def installed_graph(case: unittest.TestCase) -> Path:
    r = _INSTALL["result"]
    case.assertEqual(r.returncode, 0, f"install failed:\n{r.stdout}\n{r.stderr}")
    return _INSTALL["plant"] / "docs" / "graph"


class _TmpCase(unittest.TestCase):
    def setUp(self):
        self.assertTrue(GRAPH_LINT.exists(), f"missing tool: {GRAPH_LINT}")
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)


class KindPrefixTests(_TmpCase):
    def test_identity_mismatched_prefix_fails(self):
        """Default config: an id-prefix equal to the kind passes; any other
        prefix fails with the id/kind schema error."""
        nodes = {
            "root": node_md("root", "root", requires=["subsystem.alpha"]),
            "subsystem.alpha": node_md("subsystem.alpha", "subsystem"),
        }
        r = run_lint(build_graph(self.tmp, nodes))
        self.assertEqual(r.returncode, 0, f"expected clean lint:\n{r.stdout}\n{r.stderr}")
        nodes = {
            "root": node_md("root", "root", requires=["sub.alpha"]),
            "sub.alpha": node_md("sub.alpha", "subsystem"),
        }
        r = run_lint(build_graph(self.tmp, nodes))
        out = r.stdout + r.stderr
        self.assertNotEqual(r.returncode, 0, f"a kind/id mismatch must fail:\n{out}")
        self.assertIn("does not match kind", out, out)
        self.assertIn("sub.alpha", out, out)

    def test_mapped_prefix_mapped_id_passes(self):
        """With subsystem->sub mapped, a node id'd 'sub.alpha' passes."""
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


class MachineryNodeTests(_TmpCase):
    """Machinery nodes live under docs/graph/{protocols,skills,agents,method}/:
    kind matches the directory, an NN- filename prefix is stripped, and a
    pre-growth graph (no root) lints when index.md lists its nodes."""

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
        """The no-root branch: an orphan whose id only prefixes a listed id
        (skill.context vs skill.context-router) is not listed."""
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
        """Two mutually peering orphans do not vouch for each other."""
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
        """A project node and a machinery node sharing one id fail."""
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


class VersionLeakageTests(_TmpCase):
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


class LibraryPageShapeTests(_TmpCase):
    """A page with a `## 0. Pin` heading owes an exact version, a dated
    `Last reviewed` and an index row; a bare fixture page owes nothing."""

    PAGE = (
        "# Library: alpha\n\n## 0. Pin\n\n"
        "| Major | Exact version | Projects / paths | Notes |\n|---|---|---|---|\n"
        "| 2 | {version} | src/ | — |\n\n"
        "- **Name:** alpha\n- **Last reviewed:** {reviewed} by scout\n\n"
        "## 1. Role in this project\n\nWords.\n"
    )

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
        """A page with no `## 0. Pin` is not template-shaped."""
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


class StagedAdoptionTests(_TmpCase):
    """`--warn` prints the same findings and holds the exit code back."""

    def _unregistered(self) -> Path:
        """A template-shaped library page with no row in the index."""
        graph = build_graph(self.tmp, {"root": node_md("root", "root")},
                            libraries=["zamber"])
        (graph / "libraries" / "zamber.md").write_text(
            "# Library: zamber\n\n## 0. Pin\n\n"
            "| Major | Exact version | Projects / paths | Notes |\n|---|---|---|---|\n"
            "| 1 | 1.4.0 | src/ | — |\n\n"
            "- **Name:** zamber\n- **Last reviewed:** 2026-09-09 by scout\n\n"
            "## 1. Role in this project\n\nWords.\n", encoding="utf-8")
        (graph / "libraries" / "index.md").write_text(
            "# Libraries index\n\n| Library | Version | Page | Last reviewed |\n"
            "|---|---|---|---|\n", encoding="utf-8")
        return graph

    def test_default_mode_fails(self):
        graph = self._unregistered()
        r = run_lint(graph)
        out = r.stdout + r.stderr
        self.assertNotEqual(r.returncode, 0, f"the check must fail by default:\n{out}")
        self.assertIn("no row in libraries/index.md", out, out)

    def test_warn_reports_the_same_finding_and_exits_zero(self):
        graph = self._unregistered()
        r = run_lint(graph, "--warn")
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 0, f"--warn must exit 0:\n{out}")
        self.assertIn("no row in libraries/index.md", out,
                      "--warn must PRINT the finding; a staged exit is not a "
                      f"quieter check:\n{out}")
        self.assertIn("reported, not enforced", out, out)

    def test_warn_does_not_invent_a_pass(self):
        """A clean graph under --warn still reports OK, not a warning banner."""
        graph = build_graph(self.tmp, {"root": node_md("root", "root")})
        r = run_lint(graph, "--warn")
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 0, out)
        self.assertIn("graph-lint: OK", out, out)
        self.assertNotIn("reported, not enforced", out, out)


class ArtifactsEdgeTests(_TmpCase):
    def test_missing_artifacts_path_fails(self):
        """An `artifacts:` entry passes while its file exists under the graph
        and fails once the file is gone."""
        nodes = {"root": node_md("root", "root",
                                 artifacts=["architecture/README.md"])}
        graph = build_graph(self.tmp, nodes)
        (graph / "architecture").mkdir()
        (graph / "architecture" / "README.md").write_text("# Architecture\n",
                                                          encoding="utf-8")
        r = run_lint(graph)
        self.assertEqual(r.returncode, 0, f"a present artifact must pass:\n{r.stdout}\n{r.stderr}")
        (graph / "architecture" / "README.md").unlink()
        r = run_lint(graph)
        out = r.stdout + r.stderr
        self.assertNotEqual(r.returncode, 0, f"a missing artifact must fail:\n{out}")
        self.assertIn("artifacts → missing docs/graph/architecture/README.md", out, out)

    def test_symlinked_templates_edge_is_not_an_escape(self):
        """SPEC-0001/SYMLINK_MODE_IS_UNIFORM: under a `--symlink` install the
        graph's `templates/` resolves to the seed, outside the graph. The
        containment test reads the path, so an in-graph edge through the link
        passes, a `../` edge still fails as an escape, and a dangling edge
        through the link still fails as missing."""
        nodes = {
            "root": node_md("root", "root", artifacts=["templates/prompts/brief.md"]),
            "subsystem.out": node_md("subsystem.out", "subsystem", requires=["root"],
                                     artifacts=["../outside.md"]),
            "domain.gone": node_md("domain.gone", "domain", requires=["root"],
                                   artifacts=["templates/prompts/absent.md"]),
        }
        graph = build_graph(self.tmp, nodes)
        (graph / "templates").symlink_to(HERE / "fixtures" / "symlink-artifacts" / "templates",
                                         target_is_directory=True)
        (self.tmp / "outside.md").write_text("# outside\n", encoding="utf-8")
        r = run_lint(graph)
        out = r.stdout + r.stderr
        self.assertNotIn("escapes docs/graph/: 'templates/prompts/brief.md'", out, out)
        self.assertNotIn("missing docs/graph/templates/prompts/brief.md", out, out)
        self.assertIn("subsystem.out: artifacts → path escapes docs/graph/: '../outside.md'", out, out)
        self.assertIn("domain.gone: artifacts → missing docs/graph/templates/prompts/absent.md", out, out)
        self.assertNotIn("domain.gone: artifacts → path escapes", out, out)
        self.assertNotEqual(r.returncode, 0, out)


class LibraryIndexRowBoundaryTests(_TmpCase):
    """An index row is a reference to the page: a markdown link whose target
    is the file, or a table cell that is the page's name. A bare substring
    (a longer sibling's row, a header, prose) is not a row."""

    # A template-shaped page: the pin check is satisfied, so the index row is
    # the only thing under test.
    PAGE = (
        "# Library: {name}\n\n## 0. Pin\n\n"
        "| Major | Exact version | Projects / paths | Notes |\n|---|---|---|---|\n"
        "| 1 | 1.4.0 | src/ | — |\n\n"
        "- **Name:** {name}\n- **Last reviewed:** 2026-09-09 by scout\n\n"
        "## 1. Role in this project\n\nWords.\n"
    )

    def _graph(self, pages: dict, index_body: str) -> Path:
        """`pages` maps a library stem -> True for a template-shaped page or
        False for a bare one (a bare page owes nothing)."""
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
        """Valid row forms register: the page's own row beside a longer
        sibling, a link with other text or target spelling, a named cell with
        no link, a differently cased row, a heading-less index, and a real
        section after a pending one."""
        own = "| zamber | 1.4.0 | [zamber](zamber.md) | 2026-09-09 |\n"
        rows = [
            ("own row beside a longer sibling", {"zamber": True, "zamber-lattice": False},
             self.HEAD + own
             + "| zamber-lattice | 3.1.0 | [zamber-lattice](zamber-lattice.md) | 2026-09-09 |\n"),
            ("named cell without a link", {"zamber": True},
             self.HEAD + "| `zamber` | 1.4.0 | not written yet | 2026-09-09 |\n"),
            ("index with no headings", {"zamber": True}, self.HEAD + own),
            ("section after a pending one", {"zamber": True},
             "# Libraries index\n\n## Pending ingests\n\n"
             + self.TABLE + "| something-else | — | — | — |\n\n"
             + "## Ingested\n\n" + self.TABLE + own),
        ]
        for target in ("zamber.md", "./zamber.md", "<zamber.md>",
                       "libraries/zamber.md", "zamber.md#pin"):
            rows.append((f"link target {target}", {"zamber": True},
                         self.HEAD + f"| the wiki | 1.4.0 | [wiki page]({target}) | 2026-09-09 |\n"))
        for row in ("| Zamber | 1.4.0 | not written yet | 2026-09-09 |",
                    "| the wiki | 1.4.0 | [wiki page](Zamber.md) | 2026-09-09 |"):
            rows.append((f"cased row {row[:12]}", {"zamber": True}, self.HEAD + row + "\n"))
        for label, pages, index_body in rows:
            with self.subTest(row=label):
                r = run_lint(self._graph(pages, index_body))
                self.assertEqual(r.returncode, 0, f"{label} must register:\n{r.stdout}\n{r.stderr}")

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

    def test_a_row_under_a_pending_heading_is_not_registration(self):
        """A row in a pending table records that the page is NOT written."""
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


class ReachabilityBoundaryTests(_TmpCase):
    """An orphan whose id only prefixes a longer index string is not listed."""

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
        """The same for a DOTTED child id (`subsystem.orphan.child`)."""
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
    """Lifecycle status in frontmatter and the router's `plant:` block."""

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

    def test_plant_commented_placeholder_is_not_declared(self):
        # Rule 14: a placeholder followed by an inline YAML comment is still a
        # placeholder, so a grown plant FAILS on it (reviewer increment 4, FIX-2).
        front = self.PLANT.replace("  comment_language: en\n", "  comment_language: <bcp47>  # x\n")
        self.assertNotEqual(front, self.PLANT, "harness: the comment_language line was not rewritten")
        r = run_lint(self._graph(index_front=front, grown_marker=True))
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertIn("plant block not yet declared for comment_language", r.stderr)

    def test_plant_environment_class_is_controlled(self):
        bad = self.PLANT.replace("ephemeral-test", "sorta-prod")
        r = run_lint(self._graph(index_front=bad, grown_marker=True))
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertIn("environment_class 'sorta-prod' not in", r.stderr)


class RootlessPlanTests(unittest.TestCase):
    """`--plan` on a rootless graph with no match exits 0 with an empty LOAD."""

    def test_plan_without_root_and_without_match_does_not_crash(self):
        tmp = Path(tempfile.mkdtemp(prefix="graph-lint-rootless-")); self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        g = build_graph(tmp, {"subsystem.only": node_md("subsystem.only", "subsystem", owns=["only.fact"])})
        # graph without a root: strip the root node build_graph may have added
        for f in (g / "nodes").glob("root.md"):
            f.unlink()
        r = subprocess.run([sys.executable, str(g / "graph-lint.py"), "--plan", "zebra quux nonsense"],
                           cwd=str(g), capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertRegex(r.stdout, r"(?m)^LOAD 0 ~0t$")


# --------------------------------------------------------------------------
# --plan output helpers
# --------------------------------------------------------------------------

def plan_output(graph: Path, task: str, *, tool: Path | None = None,
                prelude: str | None = None) -> subprocess.CompletedProcess:
    """Run `--plan TASK` against `graph`. `prelude` is Python run in the same
    interpreter before the tool, to plant a fault inside its call path."""
    tool = tool or (graph / "graph-lint.py")
    if prelude is None:
        argv = [sys.executable, str(tool), "--plan", task]
    else:
        argv = [sys.executable, "-c", prelude + _RUN_TOOL, str(tool), "--plan", task]
    return subprocess.run(argv, cwd=str(graph), capture_output=True, text=True,
                          timeout=120)


_RUN_TOOL = """
import os as _os, runpy as _runpy, sys as _sys
_tool = _sys.argv[1]
_sys.argv = [_tool] + _sys.argv[2:]
_sys.path.insert(0, _os.path.dirname(_tool))
_runpy.run_path(_tool, run_name="__main__")
"""

# Inference matches with `fnmatch.fnmatchcase` (SPEC-0005 §6), so a raiser in
# its place is a fault inside inference only. The class derives from Exception
# directly, so only a handler as broad as §6 requires catches it.
_FAULT_IN_FNMATCH = """
import fnmatch as _fnmatch
class InjectedFault(Exception):
    pass
def _raise(*_a, **_k):
    raise InjectedFault("planted by test_graph_lint")
_fnmatch.fnmatchcase = _raise
"""


# The compact grammar of `--plan` (SPEC-0003 §6, ADR-0025): notices, the
# LOAD header, one `<id> <path> | <title>[ <- <how>]` line per LOAD node, then
# one `skip` block whose groups list `<id>=<path>` items. No line echoes the task.
LOAD_HEAD = re.compile(r"^LOAD (\d+) ~(\d+)t$")
SKIP_HEAD = "skip (cross only if the task needs it):"
ENTRY_LINE = re.compile(r"^(\S+) (\S+) \| (.*?)(?: <- (.*))?$")
SKIP_GROUP = re.compile(r"^ (peer of|composed by) ([a-z][a-z0-9_.-]*)(, no specific term)?: (\S.*)$")


def load_section(out: str) -> dict:
    """{node id: its whole entry line}, the lines between the LOAD header and
    the skip header, in printed order."""
    lines, on = {}, False
    for line in out.splitlines():
        if LOAD_HEAD.match(line):
            on = True
        elif line == SKIP_HEAD:
            break
        elif on and line:
            lines[line.split(" ", 1)[0]] = line
    return lines


def skip_entries(out: str) -> list:
    """[(id, path, kind, via)] of the skip block, in printed order. A group
    line the grammar does not know is returned as (line, None, None, None),
    so a compare fails on it instead of dropping it."""
    entries, on = [], False
    for line in out.splitlines():
        if line == SKIP_HEAD:
            on = True
            continue
        if not on:
            continue
        m = SKIP_GROUP.match(line)
        if not m:
            entries.append((line, None, None, None))
            continue
        kind = "peer" if m.group(1) == "peer of" else "composed"
        for item in m.group(4).split(" "):
            nid, _, path = item.partition("=")
            entries.append((nid, path or None, kind, m.group(2)))
    return entries


def skipped(out: str) -> dict:
    """{id: (kind, via)} of the skip block."""
    return {nid: (kind, via) for nid, _, kind, via in skip_entries(out)}


def not_loaded_section(out: str) -> set:
    return set(skipped(out))


# --------------------------------------------------------------------------
# The `expertise` kind and the lazy `composes:` edge
# --------------------------------------------------------------------------

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


class ComposesContractTests(_TmpCase):
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
        """A -<digits> slug is legal only under the parent that composes it."""
        ok = expertise_family()
        ok["expertise.dotnet"] = node_md(
            "expertise.dotnet", "expertise",
            composes=["expertise.ef-core", "expertise.serilog", "expertise.dotnet-10"],
            libraries=["dotnet"], owns=["dotnet.applicability"])
        ok["expertise.dotnet-10"] = node_md(
            "expertise.dotnet-10", "expertise", requires=["expertise.dotnet"],
            libraries=["dotnet"], owns=["dotnet-10.applicability"])
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

    def test_shared_sibling_trigger_warns(self):
        """Trigger-overlap warnings: a term two siblings share, or one most of
        the graph carries, warns; a parent's own term and a sub-3-character
        token such as the `0` in `net8.0` do not."""
        with self.subTest(row="shared sibling term"):
            nodes = expertise_family()
            nodes["expertise.serilog"] = node_md(
                "expertise.serilog", "expertise", requires=["expertise.dotnet"],
                libraries=["dotnet"], owns=["serilog.applicability"],
                load_when=["structured logging", "entity mapping"])
            r = self.lint(nodes)
            self.assertIn("is shared with", r.stderr)
        with self.subTest(row="generic child term"):
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
        with self.subTest(row="parent terms do not warn"):
            nodes = with_majors(expertise_family(), (8, 10), children=())
            del nodes["expertise.ef-core"], nodes["expertise.serilog"]
            r = self.lint(nodes)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertNotIn("is shared with", r.stderr)


def with_majors(nodes: dict, majors, children=("expertise.ef-core", "expertise.serilog")) -> dict:
    """The unversioned parent composes `children` plus one child per major,
    each triggered by its target-framework token."""
    nodes["expertise.dotnet"] = node_md(
        "expertise.dotnet", "expertise",
        composes=[*children, *(f"expertise.dotnet-{m}" for m in majors)],
        libraries=["dotnet"], owns=["dotnet.applicability"],
        load_when=["dotnet, csharp", "target framework, runtime"])
    for major in majors:
        nodes[f"expertise.dotnet-{major}"] = node_md(
            f"expertise.dotnet-{major}", "expertise",
            requires=["expertise.dotnet"], libraries=["dotnet"],
            owns=[f"dotnet-{major}.applicability"],
            load_when=[f"net{major}.0, dotnet {major} target"])
    return nodes


def with_migrations(nodes: dict) -> dict:
    """ef-core composes a second-level child, ef-migrations."""
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
    return nodes


class DescentTests(_TmpCase):
    """--plan descends only into the children whose own piece the task holds
    (SPEC-0002 COMPOSED_CHILD_NEEDS_ITS_OWN_PHRASE). A descent row names its
    parent by id, so tier 1 decides the entries and a child loads by descent
    alone, never as a tier-3 phrase entry."""

    def plan(self, task, nodes=None, **kw):
        kw.setdefault("libraries", ["dotnet"])
        g = build_graph(self.tmp, nodes or expertise_family(), **kw)
        r = plan_output(g, task)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout

    def test_plan_descends_on_specific_term(self):
        """Asserts SPEC-0002 COMPOSED_CHILD_NEEDS_ITS_OWN_PHRASE.

        The parent enters by its named id, so tier 1 decides and no phrase
        tier runs: a child loads only by descent. Rows: the child's whole
        piece descends it; family vocabulary (one word of a sibling's piece)
        does not; descent never folds a prefix (`migrating` is not
        `migration`); each of two levels descends on its own whole piece; a
        target-framework token picks the major as `composed`, the other major
        stays skipped; a child whose own phrase the task holds with no named
        parent is an entry (`phrase`), not composed."""
        with self.subTest(row="whole piece"):
            out = self.plan("in expertise.dotnet, fix the entity mapping")
            self.assertIn('composed by expertise.dotnet on "entity mapping"', out)
        with self.subTest(row="family vocabulary"):
            nodes = expertise_family()
            nodes["expertise.serilog"] = node_md(
                "expertise.serilog", "expertise", requires=["expertise.dotnet"],
                libraries=["dotnet"], owns=["serilog.applicability"],
                load_when=["structured logging, log sink", "dotnet logging"])
            out = self.plan("in expertise.dotnet, fix the dotnet entity mapping", nodes)
            self.assertNotIn("expertise.serilog", load_section(out), out)
            self.assertEqual(skipped(out).get("expertise.serilog", ("",))[0], "composed", out)
        with self.subTest(row="never folds"):
            out = self.plan(
                "in expertise.dotnet, fix the entity mapping, migrating the runner",
                with_migrations(expertise_family()))
            self.assertIn('composed by expertise.dotnet on "entity mapping"', out)
            self.assertEqual(skipped(out).get("expertise.ef-migrations", ("",))[0], "composed", out)
        with self.subTest(row="two levels"):
            out = self.plan(
                "in expertise.dotnet, fix the entity mapping and the migration script",
                with_migrations(expertise_family()))
            self.assertIn('composed by expertise.dotnet on "entity mapping"', out)
            self.assertRegex(load_section(out).get("expertise.ef-migrations", ""),
                             r'<- composed by expertise\.ef-core on "[^"]+"$', out)
        with self.subTest(row="major by TFM token"):
            tfm = "net10.0"
            out = self.plan(f"in subsystem.orders, target {tfm}",
                            with_majors(expertise_family(), (8, 10)))
            line = load_section(out).get("expertise.dotnet-10")
            self.assertIsNotNone(line, f"the TFM token did not select dotnet-10:\n{out}")
            self.assertTrue(line.rstrip().endswith(f'<- composed by expertise.dotnet on "{tfm}"'),
                            f"dotnet-10 must load composed on the whole TFM token "
                            f"{tfm!r} the task wrote:\n  {line}")
            self.assertEqual(skipped(out).get("expertise.dotnet-8", ("",))[0], "composed", out)
        with self.subTest(row="a held phrase with no named parent is an entry"):
            out = self.plan("entity mapping dbcontext orders")
            line = load_section(out).get("expertise.ef-core", "")
            self.assertTrue(line.rstrip().endswith('<- phrase "entity mapping"'), out)

    def test_plan_leaves_the_unnamed_sibling_with_a_reason(self):
        out = self.plan("in the orders service, fix the mapping")
        self.assertEqual(skipped(out).get("expertise.serilog"), ("composed", "expertise.dotnet"), out)
        self.assertIn(" composed by expertise.dotnet, no specific term: ", out)

    def test_plan_descends_from_required_node(self):
        """Asserts SPEC-0002 COMPOSED_CHILD_NEEDS_ITS_OWN_PHRASE (descent from a
        parent that loaded through another node's `requires:`).

        The parent is not an entry here: it arrives through the named
        subsystem's `requires`, and the task holds the child's phrase."""
        out = self.plan("in subsystem.orders, add a log sink")
        self.assertIn('composed by expertise.dotnet on "log sink"', out)
        self.assertIn("subsystem.orders", load_section(out), out)

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
        self.assertIn(SKIP_HEAD, out.splitlines())
        self.assertEqual(skipped(out).get("subsystem.billing"), ("peer", "subsystem.orders"), out)
        self.assertEqual(skipped(out).get("expertise.serilog", ("",))[0], "composed", out)

    def test_plan_without_composes_is_unchanged(self):
        """Golden over the resolved ID sets of a graph with no `composes:`,
        captured from the tool before composes existed."""
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
        self.assertEqual(set(load_section(out)), {"subsystem.orders", "stack.dotnet"})
        self.assertEqual(not_loaded_section(out), {"subsystem.billing"})


# --------------------------------------------------------------------------
# Inference (SPEC-0005) and the closure of a phrase entry (SPEC-0002). Each
# inference fixture was measured on the tool before inference existed: the
# expertise node a positive row asserts on was not in LOAD, so a row passes
# only through inference (tier 2 of the SPEC-0002 ladder).
# --------------------------------------------------------------------------

class _PlanCase(_TmpCase):
    """Positive rows assert the suffix on the node's own LOAD line."""

    def plan(self, nodes: dict, task: str, **kw) -> str:
        g = build_graph(self.tmp, nodes)
        r = plan_output(g, task, **kw)
        self.assertEqual(r.returncode, 0,
                         f"--plan {task!r} exited {r.returncode}:\n{r.stdout}\n{r.stderr}")
        return r.stdout

    def plan_doc(self, graph: Path, task: str) -> dict:
        """The `--plan-json` document for `task` over an already built graph."""
        r = subprocess.run([sys.executable, str(graph / "graph-lint.py"), f"--plan-json={task}"],
                           cwd=str(graph), capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0,
                         f"--plan-json={task!r} exited {r.returncode}:\n{r.stdout}\n{r.stderr}")
        return json.loads(r.stdout)

    def assertLoadSuffix(self, out: str, node_id: str, suffix: str, task: str):
        """`suffix` is written as SPEC-0005 states it, `<- inferred from
        "<path>" via "<pattern>"` included. The SPEC-0003 §6 compact grammar
        prints `<- inferred from "<path>"` with no pattern, so the ` via` part
        is cut before the compare (open question Q1 of the increment 2 RED
        report: SPEC-0005 still names the pattern)."""
        suffix = re.sub(r'^(<- inferred from "[^"]*") via "[^"]*"$', r"\1", suffix)
        line = load_section(out).get(node_id)
        self.assertIsNotNone(
            line, f"--plan {task!r}: {node_id} is not in LOAD; expected it with "
                  f"the suffix {suffix!r}. Output:\n{out}")
        self.assertTrue(
            line.rstrip().endswith(suffix),
            f"--plan {task!r}: {node_id}'s LOAD line does not end with "
            f"{suffix!r}:\n  {line}\nOutput:\n{out}")


DECOY_VOCABULARY = ("edit bump update web infra main app package json lock tsx "
                    "dockerfile docker terraform output deploy otel yaml wire "
                    "metrics exporter sink")


def router_graph(extra: dict, vocabulary: str = DECOY_VOCABULARY,
                 name: str = "workbench") -> dict:
    """The one router fixture: a root, three non-expertise decoys named
    `<kind>.<name>` whose trigger is `vocabulary`, and the `extra` nodes. The
    decoys take the whole scored cut on every task a case runs over their
    words, so an expertise node loads only by inference or by a phrase of
    its own."""
    nodes = {"root": node_md("root", "root", requires=[f"subsystem.{name}"],
                             owns=["root.map"])}
    for kind in ("subsystem", "stack", "platform"):
        nodes[f"{kind}.{name}"] = node_md(f"{kind}.{name}", kind,
                                          load_when=[vocabulary])
    nodes.update(extra)
    return nodes


def expertise(nid: str, *load_when: str, library: str, **kw) -> dict:
    return {nid: node_md(nid, "expertise", libraries=[library],
                         load_when=list(load_when), **kw)}


# File patterns only. On every inference task, LOAD is the three decoys.
INFERENCE = {
    **expertise("expertise.terraform", "*.tf, **/.terraform.lock.hcl", library="terraform"),
    **expertise("expertise.node-js", "**/package.json, **/package-lock.json", library="node"),
    **expertise("expertise.containers", "**/Dockerfile", library="containers"),
    **expertise("expertise.frontend", "*.{ts,tsx}", library="frontend"),
}


def inference_graph() -> dict:
    return router_graph(INFERENCE)


def inferred_lines(out: str) -> dict:
    return {nid: line for nid, line in load_section(out).items()
            if "inferred from" in line}


class InferenceTests(_PlanCase):

    def test_plan_infers_from_extension(self):
        """Asserts SPEC-0005 PLAN_INFERS_EXPERTISE_FROM_NAMED_FILES.

        Also asserts SPEC-0005 PATTERN_BRACE_SPLIT (the brace-pattern row) and
        SPEC-0005 EXTENSIONLESS_BARE_NAME (the Dockerfile rows). A pattern
        with no `/` matches the path's last segment. Rows below name each
        edge; the negative rows infer nothing."""
        pydeps = router_graph(expertise("expertise.pydeps", "requirements*.txt", library="python"),
                              DECOY_VOCABULARY + " svc requirements txt")
        ci = router_graph(expertise("expertise.ci", "ci/pipelines.yml", library="ci"),
                          "edit ci/pipelines.yml pipelines yml", "pipelines")
        rows = [
            ("extension", inference_graph(), "edit infra/main.tf", "expertise.terraform",
             '<- inferred from "infra/main.tf" via "*.tf"'),
            # no `/` but an extension: path-like, matched through the bare-p arm
            ("bare manifest", inference_graph(), "bump package.json", "expertise.node-js",
             '<- inferred from "package.json" via "**/package.json"'),
            # a literal-name pattern matches the last segment in any directory
            # (`requirements.txt` alone would be a phrase, so it holds a `*`)
            ("literal name in a subdirectory", pydeps, "bump svc/requirements.txt",
             "expertise.pydeps",
             '<- inferred from "svc/requirements.txt" via "requirements*.txt"'),
            # `/` alone marks a pattern: inferred, not promoted
            ("slash piece without a star", ci, "edit ci/pipelines.yml", "expertise.ci",
             '<- inferred from "ci/pipelines.yml" via "ci/pipelines.yml"'),
            # the first PATH in task order, then its first matching pattern
            ("first path in task order", inference_graph(),
             "edit .terraform.lock.hcl infra/main.tf", "expertise.terraform",
             '<- inferred from ".terraform.lock.hcl" via "**/.terraform.lock.hcl"'),
            ("dotted Dockerfile", inference_graph(), "edit ./Dockerfile",
             "expertise.containers", '<- inferred from "dockerfile" via "**/Dockerfile"'),
            ("Dockerfile in a directory", inference_graph(), "edit docker/Dockerfile",
             "expertise.containers",
             '<- inferred from "docker/dockerfile" via "**/Dockerfile"'),
        ]
        for label, nodes, task, nid, suffix in rows:
            with self.subTest(row=label):
                self.assertLoadSuffix(self.plan(nodes, task), nid, suffix, task)
        negatives = [
            # a bare extensionless name is not path-like
            ("bare Dockerfile", inference_graph(), "edit Dockerfile"),
            # the path-like test runs before `\` folds, and `\` is outside the
            # extension form
            ("backslash-only token", inference_graph(), "edit infra\\main.tf"),
            # the task token is the NAME on the whole-path arm, never the pattern
            ("task wildcard vs a slash pattern",
             router_graph(expertise("expertise.ci", "ci/pipeline.yml", library="ci")),
             "edit ci/*"),
        ]
        for label, nodes, task in negatives:
            with self.subTest(row=label):
                out = self.plan(nodes, task)
                self.assertEqual(inferred_lines(out), {}, out)
        with self.subTest(row="brace pattern"):
            # `*.{ts,tsx}` splits into `*.{ts` (matches nothing) and `tsx}`, a
            # one-token piece that seeds nothing (SPEC-0002 §6)
            task = "edit web/app.tsx"
            out = self.plan(inference_graph(), task)
            self.assertNotIn("expertise.frontend", load_section(out),
                             f"--plan {task!r} loaded the brace-pattern node:\n{out}")
        with self.subTest(row="pattern text as words"):
            out = self.plan(inference_graph(),
                            "update the package lock json and the terraform lock hcl")
            self.assertNotIn("promoted on", out,
                             f"a file pattern's words promoted a node:\n{out}")

    def test_plan_infers_from_nested_lockfile(self):
        """Asserts SPEC-0005 PLAN_INFERS_EXPERTISE_FROM_NAMED_FILES.

        `**/package-lock.json` loses its leading `**/` and matches the path
        through the `*/` + p arm; the echoed pattern is the piece as written."""
        task = "bump web/package-lock.json"
        out = self.plan(inference_graph(), task)
        self.assertLoadSuffix(
            out, "expertise.node-js",
            '<- inferred from "web/package-lock.json" via "**/package-lock.json"',
            task)

    def test_plan_inferred_path_echo_is_normalized_and_sanitized(self):
        """Asserts SPEC-0005 PLAN_INFERS_EXPERTISE_FROM_NAMED_FILES.

        The Then's `<path>` is the token after §6 stripping and normalization
        (lowercase, one leading `./` removed) and echo sanitizing (cut to 80
        characters plus `…`, anything outside `[a-z0-9_./~+-]` shown as `?`)."""
        long_dir = "d" * 90
        cases = [
            ("edit ./Infra/Main.TF", "infra/main.tf"),
            ("edit `infra/main.tf`,", "infra/main.tf"),
            ("edit infra/ma$in.tf", "infra/ma?in.tf"),
            (f"edit {long_dir}/main.tf", "d" * 80 + "…"),
            # the strip repeats until stable
            ("edit (infra/main.tf).", "infra/main.tf"),
            # `\` folds to `/` in a token that is already
            # path-like through its `/`
            ("edit infra/sub\\main.tf", "infra/sub/main.tf"),
        ]
        for task, echoed in cases:
            with self.subTest(task=task[:40]):
                out = self.plan(inference_graph(), task)
                self.assertLoadSuffix(
                    out, "expertise.terraform",
                    f'<- inferred from "{echoed}" via "*.tf"', task)

    def test_plan_task_text_is_never_a_pattern(self):
        """Asserts SPEC-0005 PLAN_INFERS_EXPERTISE_FROM_NAMED_FILES.

        Adversarial. The task token is always the NAME and the piece
        always the PATTERN; nothing touches the filesystem. `*/*` and
        `a-z]*/**` would match `*/package.json` and `*.{ts` if the arguments
        were swapped; `../../nowhere/x.tf` exists nowhere and infers exactly
        as an existing path would; it comes first in task order, so it is the
        one echoed."""
        task = "* */* [a-z]*/** ../../nowhere/x.tf /abs/y.tf"
        out = self.plan(inference_graph(), task)
        self.assertLoadSuffix(out, "expertise.terraform",
                              '<- inferred from "../../nowhere/x.tf" via "*.tf"',
                              task)
        self.assertEqual(set(inferred_lines(out)), {"expertise.terraform"},
                         f"task text was used as a pattern:\n{out}")

    def test_plan_hostile_task_line_never_raises(self):
        """Asserts SPEC-0005 HOSTILE_TASK_LINE.

        An error inside inference prints `! inference skipped: <class>`
        before LOAD, exits 0, and the route goes on to the next tier: LOAD is
        the `--plan-json` LOAD of the same task with its path token removed
        (on this fixture, nothing, with a `no_signal` notice)."""
        g = build_graph(self.tmp, inference_graph())
        r = plan_output(g, "edit infra/main.tf", prelude=_FAULT_IN_FNMATCH)
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 0,
                         f"an inference error changed the exit status:\n{out}")
        lines = r.stdout.splitlines()
        notice = next((i for i, l in enumerate(lines)
                       if l.startswith("! inference skipped: InjectedFault")), None)
        load = next((i for i, l in enumerate(lines) if LOAD_HEAD.match(l)), None)
        self.assertIsNotNone(notice, f"no inference-skipped notice:\n{out}")
        self.assertIsNotNone(load, out)
        self.assertLess(notice, load, f"the notice must precede LOAD:\n{out}")
        without_path = self.plan_doc(g, "edit")
        self.assertEqual(list(load_section(r.stdout)), [e["id"] for e in without_path["load"]],
                         f"the fallback is the route of the task without its path:\n{out}")

    def test_plan_infers_nothing_without_a_path_token(self):
        """Asserts SPEC-0005 TASK_LINE_WITHOUT_PATHS.

        Guard. No path-like token, nothing inferred — including a URL, whose
        `://` token is skipped (§6)."""
        for task in ("terraform plan output",
                     "see https://example.com/infra/main.tf"):
            with self.subTest(task=task):
                out = self.plan(inference_graph(), task)
                self.assertNotIn("inferred from", out, out)

    def test_plan_infers_through_a_slash_pattern(self):
        """Asserts SPEC-0005 PLAN_INFERS_EXPERTISE_FROM_NAMED_FILES.

        Guard: `infra/*.tf` matches the whole path `infra/main.tf`."""
        extra = expertise("expertise.infra", "infra/*.tf", library="terraform")
        task = "edit infra/main.tf"
        self.assertLoadSuffix(self.plan(router_graph(extra), task), "expertise.infra",
                              '<- inferred from "infra/main.tf" via "infra/*.tf"', task)


# expertise.alpha composes beta; beta requires alpha, composes gamma, and
# carries `metrics exporter` and `**/otel.yaml`. On TASK, LOAD was the decoys.
CLOSURE = {
    **expertise("expertise.alpha", "runtime platform", library="alpha",
                composes=["expertise.beta"]),
    **expertise("expertise.beta", "metrics exporter, **/otel.yaml", library="alpha",
                requires=["expertise.alpha"], composes=["expertise.gamma"]),
    **expertise("expertise.gamma", "structured logging, log sink", library="alpha",
                requires=["expertise.beta"]),
}


class PhraseEntryClosureTests(_PlanCase):
    TASK = "wire the metrics exporter into the sink"

    def test_plan_phrase_entry_brings_required_parent(self):
        """Asserts SPEC-0002 GRAPH_ROUTE_PHRASE_LOADS_ITS_NODE (the closure of a
        loaded node always loads with it).

        `requires:` runs from a tier-3 phrase entry as from any entry."""
        out = self.plan(router_graph(CLOSURE), self.TASK)
        self.assertLoadSuffix(out, "expertise.beta", '<- phrase "metrics exporter"', self.TASK)
        self.assertIn("expertise.alpha", load_section(out),
                      f"the phrase entry's requires: parent did not load:\n{out}")

    def test_plan_requires_outranks_composed(self):
        """Asserts SPEC-0002 COMPOSED_CHILD_NEEDS_ITS_OWN_PHRASE (its `requires`
        over `composed` clause; §6 How precedence).

        expertise.cache is required by the phrase entry subsystem.orders and
        is also a composed child of the phrase entry expertise.metrics whose
        one-token piece `flush` the task holds. A node a loaded node requires
        is `requires`, never `composed`, whichever edge the traversal meets
        first."""
        task = "orders service metrics exporter flush"
        nodes = router_graph({
            **expertise("expertise.metrics", "metrics exporter", library="metrics",
                        composes=["expertise.cache"]),
            **expertise("expertise.cache", "flush, cache warmup",
                        library="metrics", requires=["expertise.metrics"]),
        }, "orders pipeline decoy", name="orders")
        nodes["subsystem.orders"] = node_md("subsystem.orders", "subsystem",
                                            requires=["expertise.cache"],
                                            load_when=["orders service"])
        doc = self.plan_doc(build_graph(self.tmp, nodes), task)
        hows = {e["id"]: e["how"] for e in doc["load"]}
        self.assertEqual((hows.get("expertise.metrics") or {}).get("kind"), "phrase", doc)
        self.assertEqual((hows.get("subsystem.orders") or {}).get("kind"), "phrase", doc)
        self.assertEqual((hows.get("expertise.cache") or {}).get("kind"), "requires",
                         f"{task!r}: a required node was reported {hows.get('expertise.cache')!r}")


class ListedNodeEdgesTests(_TmpCase):

    def lint(self, *, island: bool) -> subprocess.CompletedProcess:
        """index.md lists root, subsystem.main and subsystem.listed; root
        reaches main only. subsystem.hidden is reached only by listed's
        `peers:`. `island` adds two unlisted nodes that peer each other."""
        nodes = {
            "root": node_md("root", "root", requires=["subsystem.main"],
                            owns=["root.map"]),
            "subsystem.main": node_md("subsystem.main", "subsystem"),
            "subsystem.listed": node_md("subsystem.listed", "subsystem",
                                        peers=["subsystem.hidden"]),
            "subsystem.hidden": node_md("subsystem.hidden", "subsystem"),
        }
        if island:
            nodes["subsystem.isle-x"] = node_md("subsystem.isle-x", "subsystem",
                                                peers=["subsystem.isle-y"])
            nodes["subsystem.isle-y"] = node_md("subsystem.isle-y", "subsystem",
                                                peers=["subsystem.isle-x"])
        return run_lint(build_graph(
            self.tmp, nodes,
            listed=["root", "subsystem.main", "subsystem.listed"]))

    def test_listed_node_peer_is_reachable(self):
        """Asserts SPEC-0005 LISTED_NODE_EDGES_REACH.

        Also covers SIBLING_UNREACHABLE_AFTER_GRAFT: a plant index that lists
        `method.delegation` but not its new siblings is this shape."""
        r = self.lint(island=False)
        out = r.stdout + r.stderr
        self.assertNotRegex(
            out, r"subsystem\.hidden\b[^\n]*unreachable",
            f"a node reached by a listed node's peers: edge was reported "
            f"unreachable:\n{out}")
        # the fixture is otherwise clean, so the whole lint passes.
        self.assertEqual(r.returncode, 0, out)

    def test_unlisted_peer_island_still_unreachable(self):
        """Asserts SPEC-0005 ORPHAN_ISLAND.

        Guard. Following a LISTED node's edges must not become following
        every node's: two mutually peering, unlisted, unreached nodes are
        each still reported. Held by the mutant "union every node's edges"."""
        r = self.lint(island=True)
        out = r.stdout + r.stderr
        self.assertNotEqual(r.returncode, 0, out)
        for nid in ("subsystem.isle-x", "subsystem.isle-y"):
            with self.subTest(node=nid):
                self.assertRegex(out, re.escape(nid) + r"[^\n]*unreachable", out)


# SPEC-0005 §6 "Delegation leaves", first and last columns.
DELEGATION_SIBLINGS = (
    ("method.delegation", "who should do this, which specialist, which agent"),
    ("method.delegation-model-classes", "sonnet or opus, which model class"),
    ("method.delegation-cycle-economy", "how many increments per spawn, batch size"),
    ("method.delegation-briefs", "spawn a worker, write a delegation brief"),
    ("method.delegation-sequencing",
     "spawn order, parallel or sequential, which spawn waits for which"),
    ("method.delegation-bounds", "delegation depth, allowlist, can this agent spawn"),
)


class DelegationRoutingTests(unittest.TestCase):
    """The installed router over the installed graph."""

    def test_delegation_sibling_routes_on_its_phrase(self):
        """Asserts SPEC-0005 DELEGATION_LEAVES_ROUTE.

        `--plan` on each sibling's representative phrase lists that sibling
        in LOAD."""
        graph = installed_graph(self)
        for nid, phrase in DELEGATION_SIBLINGS:
            with self.subTest(sibling=nid):
                r = plan_output(graph, phrase)
                self.assertEqual(r.returncode, 0, r.stderr)
                self.assertIn(nid, load_section(r.stdout),
                              f"--plan {phrase!r} did not load {nid}:\n{r.stdout}")


# SPEC-0001 version-leakage and budget contracts. Each test's NAME carries the
# contract slug: spec-lint's boundary is `(?<![A-Z0-9_])`, so the name starts
# `test` with no underscore before the slug.

def node_with_frontmatter_key(node_id: str, kind: str, key: str, value: str) -> str:
    """A schema-valid node carrying `key: value` in its frontmatter, with the
    body left saying nothing about any version."""
    text = node_md(node_id, kind)
    if key == "title":
        return text.replace(f"title: {node_id} node", f"title: {value}", 1)
    return text.replace("load_when:", f"{key}: {value}\nload_when:", 1)


class FrontmatterVersionPositionTests(_TmpCase):
    """Where a version token is written decides whether it is an assertion
    or a routing handle."""

    def _lint(self, alpha: str):
        nodes = {
            "root": node_md("root", "root", requires=["subsystem.alpha"]),
            "subsystem.alpha": alpha,
        }
        return run_lint(build_graph(self.tmp, nodes))

    def testGRAPH_LINT_FRONTMATTER_ASSERTION_PIN_IS_A_LEAK(self):
        """A pin in `title:` is a claim the node makes."""
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
        """`load_when:` is routing: a release identifier there is not a leak.
        The fixture is a trap only because VERSION_RE matches `3.2`."""
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
        """A release identifier with no dotted-numeric core is still one.
        `0.29-gfm` is the control VERSION_RE always caught."""
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
        """The same identifier inside a code span quotes a config line."""
        alpha = node_md("subsystem.alpha", "subsystem")
        alpha = alpha.replace(
            "plain words.",
            "plain words. The schema line reads `\"$schema\": draft-07` verbatim.", 1)
        r = self._lint(alpha)
        self.assertEqual(r.returncode, 0,
                         f"a code span must stay exempt:\n{r.stdout}\n{r.stderr}")


class BudgetMeasuresTheWholeFileTests(_TmpCase):
    def testGRAPH_LINT_BUDGET_COUNTS_FRONTMATTER(self):
        """`est_tokens` budgets the whole file a loader reads. A node with 60
        triggers and a short body, `est_tokens` set to the body figure, fails
        and the verdict names the whole-file figure."""
        triggers = [f"routing trigger number {i} for the alpha surface"
                    for i in range(60)]
        alpha = node_md("subsystem.alpha", "subsystem", load_when=triggers)
        head, _, body = alpha.partition("\n---\n\n")
        body_tokens = int(len(body.split()) * 1.35)
        whole_tokens = int(len((head + "\n---\n" + body).split()) * 1.35)
        self.assertGreater(whole_tokens, 2 * body_tokens, "the fixture must separate the two figures")
        alpha = re.sub(r"^est_tokens: \d+$", f"est_tokens: {body_tokens}",
                       alpha, count=1, flags=re.M)
        nodes = {
            "root": node_md("root", "root", requires=["subsystem.alpha"]),
            "subsystem.alpha": alpha,
        }
        r = run_lint(build_graph(self.tmp, nodes))
        out = r.stdout + r.stderr
        self.assertNotEqual(r.returncode, 0, out)
        measured = re.search(r"est_tokens=\d+ but .*?~(\d+)", out)
        self.assertIsNotNone(measured, f"no measured figure in the verdict:\n{out}")
        self.assertEqual(int(measured.group(1)), whole_tokens, out)
        self.assertNotIn("body measures", out, out)


class SeedAndPlantCopyAgreeTests(_TmpCase):
    def testGRAPH_LINT_SEED_COPY_AGREES_WITH_PLANT_COPY(self):
        """The seed copy and the installed copy of graph-lint.py fail one
        leaking fixture with the same exit code and the same, non-empty error
        set. The installed copy is copied beside the fixture because the tool
        lints the graph beside itself."""
        plant_tool = installed_graph(self) / "graph-lint.py"
        self.assertTrue(plant_tool.is_file(), f"no installed graph-lint at {plant_tool}")
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
        plant_copy = graph / "graph-lint-installed.py"
        shutil.copy(plant_tool, plant_copy)

        def verdict(tool: Path):
            r = subprocess.run([sys.executable, str(tool)], cwd=str(graph),
                               capture_output=True, text=True, timeout=60)
            # errors print as `  \u2717 <text>`; warnings are fixture noise
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
        self.assertTrue(seed_errs, "no error line parsed: the comparison would be vacuous")
        self.assertNotEqual(seed_rc, 0, "both copies passed a leaking node")


class FrontmatterPortableTests(_TmpCase):
    """Frontmatter must parse under a strict-YAML loader too: an unquoted
    inner ': ' is read as a nested mapping by a strict host."""

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


class PlanEntryPathTests(_TmpCase):
    """SPEC-0003 PLAN_ENTRY_NAMES_THE_NODE_FILE: `--plan` prints the compact
    grammar of §6. Each LOAD entry is `<id> <path> | <title>`, the path from
    the plant root and the title without its `<slug> — ` prefix; each skipped
    node is `<id>=<path>` in one `skip` group. One node lives at
    docs/graph/agents/04-tester.md, a path its id does not spell, and carries
    a title with its slug prefix."""

    TASK = "write widget ledger tests"

    def _plant(self) -> tuple:
        nodes = {
            "root": node_md("root", "root", load_when=["widget ledger"]),
            "subsystem.alpha": node_md("subsystem.alpha", "subsystem", requires=["root"],
                                       peers=["subsystem.beta"], load_when=["widget ledger"]),
            "subsystem.beta": node_md("subsystem.beta", "subsystem", requires=["root"],
                                      load_when=["sprocket gearing"]),
        }
        built = build_graph(self.tmp, nodes)
        plant = self.tmp / "plant"
        (plant / "docs").mkdir(parents=True)
        graph = plant / "docs" / "graph"
        shutil.move(str(built), str(graph))
        (graph / "agents").mkdir()
        (graph / "agents" / "04-tester.md").write_text(
            node_md("agent.tester", "agent", requires=["root"],
                    load_when=["widget ledger tests"]).replace(
                "title: agent.tester node", "title: tester \u2014 reads the gearbox", 1),
            encoding="utf-8")
        with (graph / "index.md").open("a", encoding="utf-8") as f:
            f.write("- agent.tester\n")
        files = {
            "root": "docs/graph/nodes/root.md",
            "subsystem.alpha": "docs/graph/nodes/subsystem.alpha.md",
            "subsystem.beta": "docs/graph/nodes/subsystem.beta.md",
            "agent.tester": "docs/graph/agents/04-tester.md",
        }
        titles = {nid: f"{nid} node" for nid in files}
        titles["agent.tester"] = "reads the gearbox"
        return plant, files, titles

    def test_plan_entry_names_the_node_file(self):
        """PLAN_ENTRY_NAMES_THE_NODE_FILE: every id is printed with its node file."""
        plant, files, titles = self._plant()
        r = subprocess.run([sys.executable, "docs/graph/graph-lint.py", "--plan", self.TASK],
                           cwd=str(plant), capture_output=True, text=True, timeout=120)
        out = r.stdout
        self.assertEqual(r.returncode, 0, f"--plan exited {r.returncode}:\n{out}\n{r.stderr}")
        lines = out.splitlines()
        self.assertFalse([l for l in lines if l.startswith("task:")], f"a `task:` line:\n{out}")
        self.assertFalse([l for l in lines if re.search(r"\S {2,}|^ {2,}", l)],
                         f"a line is padded with runs of spaces:\n{out}")
        self.assertEqual(len([l for l in lines if LOAD_HEAD.match(l)]), 1,
                         f"no single `LOAD <n> ~<t>t` header:\n{out}")
        load = load_section(out)
        self.assertEqual(sorted(load), ["agent.tester", "root", "subsystem.alpha"],
                         f"harness or grammar: LOAD is not the measured three:\n{out}")
        for nid, line in load.items():
            with self.subTest(line=line):
                m = ENTRY_LINE.match(line)
                self.assertIsNotNone(m, f"{line!r} is not `<id> <path> | <title>`")
                self.assertEqual((m.group(1), m.group(2), m.group(3)),
                                 (nid, files[nid], titles[nid]), line)
        self.assertEqual(lines.count(SKIP_HEAD), 1, f"not one skip block:\n{out}")
        self.assertEqual(skip_entries(out),
                         [("subsystem.beta", files["subsystem.beta"], "peer", "subsystem.alpha")],
                         f"the skip block is not one `peer of` group naming beta=<path>:\n{out}")


# --------------------------------------------------------------------------
# `--plan-json`: the `cypress.plan/1` document (SPEC-0003 §6, ADR-0025)
# --------------------------------------------------------------------------

PLAN_SCHEMA = "cypress.plan/1"
NODE_ID_PATTERN = re.compile(r"^[a-z][a-z0-9_.-]{0,127}$")
RELATIVE_PATH_PATTERN = re.compile(r"^(?!/)(?!.*(^|/)\.\.(/|$))[A-Za-z0-9_./-]+$")
NOTICE_CODES = {"wide_descent", "inference_skipped", "long_task", "no_signal"}
HOW_KINDS = {"scored", "requires", "inferred", "composed", "named_id", "named_path",
             "phrase"}
PLANT_KEYS = {"environment_class", "commit_attribution", "deliverable_language",
              "comment_language"}

# The task set PLAN_JSON_EQUALS_PLAN names, shared with ROUTE_FULL_TEXT_EQUALS_PLAN
# in tests/test-prompt-hooks.sh: (label, which fixture plant, task).
PLAN_TASK_SET = (
    ("notice, peer skipped and composed", "main",
     "fix subsystem.orders: the entity mapping and the log sink"),
    ("a node whose path its id does not spell", "main", "write widget ledger tests"),
    ("loads nothing", "rootless", "zebra quux nonsense"),
    ("an inferred entry", "main", "bump infra/main.tf in the orders service"),
    ("a plant: block in index.md", "planted", "write widget ledger tests"),
)

# The `planted` fixture's index.md frontmatter (SPEC-0003 PLAN_PRINTS_PLANT_BLOCK):
# four distinct values, so a renderer that reorders or drops a fact is caught.
PLANT_FACTS = (("environment_class", "ephemeral-test"), ("commit_attribution", "none"),
               ("deliverable_language", "fr"), ("comment_language", "de"))
PLANT_LINE = "plant: " + " ".join(f"{k}={v}" for k, v in PLANT_FACTS)


def plan_fixture_plant(tmp: Path, which: str = "main") -> Path:
    """A plant whose `docs/graph/` holds the real tool. `main`: the expertise
    family (a wide descent and composed entries on the first task), a peer
    of `subsystem.orders` left unloaded, and `agent.tester` at docs/graph/agents/04-tester.md,
    a path its id does not spell. `rootless`: one node and no root, so a task
    that matches nothing loads nothing. `planted`: `main` with the four
    PLANT_FACTS in a `plant:` block in index.md's frontmatter."""
    plant = tmp / f"plant-{which}"
    if which == "rootless":
        nodes = {"subsystem.only": node_md("subsystem.only", "subsystem", owns=["only.fact"])}
    else:
        nodes = expertise_family(**{
            "subsystem.orders": node_md(
                "subsystem.orders", "subsystem", requires=["expertise.dotnet"],
                owns=["orders.responsibility"], peers=["subsystem.billing"],
                load_when=["orders service", "editing src/Orders/**"]),
            "subsystem.billing": node_md("subsystem.billing", "subsystem", requires=["root"],
                                         load_when=["invoice sprocket gearing"]),
            # file patterns only: loads by inference (`<- inferred from "<path>"`)
            "expertise.terraform": node_md("expertise.terraform", "expertise",
                                           libraries=["terraform"], owns=["terraform.applicability"],
                                           load_when=["*.tf, **/.terraform.lock.hcl"])})
    built = build_graph(tmp, nodes, libraries=["dotnet", "terraform"])
    (plant / "docs").mkdir(parents=True)
    graph = plant / "docs" / "graph"
    shutil.move(str(built), str(graph))
    if which in ("main", "planted"):
        (graph / "agents").mkdir()
        (graph / "agents" / "04-tester.md").write_text(
            node_md("agent.tester", "agent", requires=["root"],
                    load_when=["widget ledger tests"]), encoding="utf-8")
        with (graph / "index.md").open("a", encoding="utf-8") as f:
            f.write("- agent.tester\n")
    if which == "planted":
        idx = graph / "index.md"
        front = "---\nplant:\n" + "".join(f"  {k}: {v}\n" for k, v in PLANT_FACTS) + "---\n"
        idx.write_text(front + idx.read_text(encoding="utf-8"), encoding="utf-8")
    return plant


def run_plant_tool(plant: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "docs/graph/graph-lint.py", *args],
                          cwd=str(plant), capture_output=True, text=True, timeout=120)


def plan_json_problems(doc) -> list:
    """Every way `doc` departs from the §6 `cypress.plan/1` schema."""
    bad = []
    if not isinstance(doc, dict):
        return [f"not a JSON object: {type(doc).__name__}"]
    want = {"schema", "task_sha256", "plant", "notices", "est_tokens", "load", "skip"}
    if set(doc) != want:
        bad.append(f"keys {sorted(doc)} != {sorted(want)}")
    if doc.get("schema") != PLAN_SCHEMA:
        bad.append(f"schema {doc.get('schema')!r}")
    if not (isinstance(doc.get("task_sha256"), str)
            and re.fullmatch(r"[0-9a-f]{64}", doc["task_sha256"])):
        bad.append(f"task_sha256 {doc.get('task_sha256')!r}")
    plant = doc.get("plant")
    if plant is not None and not (isinstance(plant, dict) and set(plant) == PLANT_KEYS
                                  and all(isinstance(v, str) for v in plant.values())):
        bad.append(f"plant {plant!r}")
    est = doc.get("est_tokens")
    if not (isinstance(est, int) and not isinstance(est, bool) and est >= 0):
        bad.append(f"est_tokens {est!r}")
    for n in doc.get("notices") if isinstance(doc.get("notices"), list) else [None]:
        if not (isinstance(n, dict) and set(n) == {"code", "text"}
                and n["code"] in NOTICE_CODES and isinstance(n["text"], str)):
            bad.append(f"notice {n!r}")

    def node_ref(e, keys):
        return (isinstance(e, dict) and set(e) == keys
                and isinstance(e.get("id"), str) and NODE_ID_PATTERN.match(e["id"])
                and isinstance(e.get("path"), str) and RELATIVE_PATH_PATTERN.match(e["path"]))

    load = doc.get("load") if isinstance(doc.get("load"), list) else [None]
    for e in load:
        how = e.get("how") if isinstance(e, dict) else None
        ok = (node_ref(e, {"id", "path", "title", "how"}) and isinstance(e.get("title"), str)
              and isinstance(how, dict) and set(how) == {"kind", "detail", "via"}
              and how["kind"] in HOW_KINDS
              and (how["detail"] is None or isinstance(how["detail"], str))
              and (how["via"] is None or (isinstance(how["via"], str)
                                          and NODE_ID_PATTERN.match(how["via"]))))
        if not ok:
            bad.append(f"load entry {e!r}")
    ids = [e.get("id") for e in load if isinstance(e, dict)]
    if ids != sorted(ids):
        bad.append(f"load not sorted by id: {ids}")
    for e in doc.get("skip") if isinstance(doc.get("skip"), list) else [None]:
        if not (node_ref(e, {"id", "path", "kind", "via"}) and e["kind"] in {"peer", "composed"}
                and isinstance(e.get("via"), str) and NODE_ID_PATTERN.match(e["via"])):
            bad.append(f"skip entry {e!r}")
    return bad


def text_plan(out: str, task: str) -> dict:
    """The compact `--plan` grammar read back into the document's terms:
    notice texts, the LOAD count and token total, LOAD (id, path, how) and
    skipped (id, path, kind, via), each in printed order."""
    lines = out.splitlines()
    notices = [l[len("! "):] for l in lines if l.startswith("! ")]
    m = next((LOAD_HEAD.match(l) for l in lines if LOAD_HEAD.match(l)), None)
    load = []
    for nid, line in load_section(out).items():
        em = ENTRY_LINE.match(line)
        load.append((nid, em.group(2), em.group(4)) if em else (line, None, None))
    return {"notices": notices, "count": m and int(m.group(1)),
            "est_tokens": m and int(m.group(2)), "load": load, "skip": skip_entries(out)}


def how_suffix(how: dict):
    """The text after ` <- ` the §6 grammar prints for a document `how`, or None."""
    kind, detail, via = how["kind"], how["detail"], how["via"]
    if kind == "inferred":
        return f'inferred from "{detail}"'
    if kind == "composed":
        return f'composed by {via} on "{detail}"'
    if kind == "named_path":
        return f'owns "{detail}"'
    if kind == "phrase":
        return f'phrase "{detail}"'
    return None


class PlanJsonTests(_TmpCase):
    """SPEC-0003 PLAN_JSON_*: `graph-lint.py --plan-json=<task>` prints one
    `cypress.plan/1` document (§6) that programs read instead of the text."""

    def plan_json(self, plant: Path, task: str) -> dict:
        r = run_plant_tool(plant, f"--plan-json={task}")
        self.assertEqual(r.returncode, 0,
                         f"--plan-json={task!r} exited {r.returncode}:\n{r.stdout}\n{r.stderr}")
        try:
            return json.loads(r.stdout)
        except ValueError as e:
            self.fail(f"--plan-json={task!r}: stdout is not one JSON object ({e}):\n{r.stdout}")

    def test_plan_json_schema(self):
        """PLAN_JSON_SCHEMA: one JSON object satisfying `cypress.plan/1`. The
        harness task loads, skips a peer and raises a `wide_descent` notice
        (a parent with both its children held)."""
        plant = plan_fixture_plant(self.tmp)
        task = PLAN_TASK_SET[0][2]
        doc = self.plan_json(plant, task)
        self.assertEqual(plan_json_problems(doc), [], f"schema departures in:\n{doc!r}")
        self.assertTrue(doc["load"] and doc["skip"] and doc["notices"],
                        f"harness: the task must load, skip and raise a notice:\n{doc!r}")

    def test_plan_json_carries_no_prompt(self):
        """PLAN_JSON_CARRIES_NO_PROMPT: no field holds the task or its sentinel."""
        plant = plan_fixture_plant(self.tmp)
        sentinel = "zqsentinelnoprompt7731"
        task = PLAN_TASK_SET[0][2] + " " + sentinel
        r = run_plant_tool(plant, f"--plan-json={task}")
        self.assertEqual(r.returncode, 0, f"--plan-json exited {r.returncode}:\n{r.stderr}")
        self.assertNotIn(sentinel, r.stdout, "the task's sentinel reached the document")
        doc = json.loads(r.stdout)

        def strings(v):
            if isinstance(v, str):
                yield v
            elif isinstance(v, dict):
                for x in v.values():
                    yield from strings(x)
            elif isinstance(v, list):
                for x in v:
                    yield from strings(x)
        held = [s for s in strings(doc) if task in s or s == task]
        self.assertEqual(held, [], "a field holds the task")

    def test_plan_json_hash_binds_task(self):
        """PLAN_JSON_HASH_BINDS_TASK: task_sha256 is the SHA-256 of the task's
        UTF-8 bytes exactly as received in argv, line ends included."""
        plant = plan_fixture_plant(self.tmp)
        base = "in the orders service, fix the mapping"
        rows = [("one line", base),
                ("LF", base.replace(", ", "\n")),
                ("CRLF", base.replace(", ", "\r\n")),
                ("lone CR", base.replace(", ", "\r")),
                ("non-ASCII", base + " caf\u00e9 \u65e5\u672c \u00fcber")]
        for label, task in rows:
            with self.subTest(row=label):
                doc = self.plan_json(plant, task)
                self.assertEqual(doc.get("task_sha256"),
                                 hashlib.sha256(task.encode("utf-8")).hexdigest())

    def test_plan_json_equals_plan(self):
        """PLAN_JSON_EQUALS_PLAN: `--plan` and `--plan-json` carry the same
        notices, LOAD (ids, paths, how), skipped (ids, paths, kinds, via), in
        the same order, and the same token total."""
        plants = {w: plan_fixture_plant(self.tmp, w) for w in {w for _, w, _ in PLAN_TASK_SET}}
        seen = {"notice": False, "composed": False, "empty": False}
        for label, which, task in PLAN_TASK_SET:
            with self.subTest(task=label):
                r = run_plant_tool(plants[which], "--plan", task)
                self.assertEqual(r.returncode, 0, r.stderr)
                text = text_plan(r.stdout, task)
                doc = self.plan_json(plants[which], task)
                self.assertEqual(text["notices"], [n["text"] for n in doc["notices"]], "notices")
                self.assertEqual(text["est_tokens"], doc["est_tokens"], "token total")
                self.assertEqual([(i, p) for i, p, _ in text["load"]],
                                 [(e["id"], e["path"]) for e in doc["load"]], "LOAD ids and paths")
                self.assertEqual([h for _, _, h in text["load"]],
                                 [how_suffix(e["how"]) for e in doc["load"]], "LOAD how")
                self.assertEqual(text["skip"],
                                 [(e["id"], e["path"], e["kind"], e["via"]) for e in doc["skip"]],
                                 "skipped ids, paths, kinds and via")
                seen["notice"] |= bool(doc["notices"])
                seen["composed"] |= any(e["how"]["kind"] == "composed" for e in doc["load"])
                seen["empty"] |= not doc["load"]
        self.assertEqual(seen, dict.fromkeys(seen, True),
                         "harness: the task set must hold a notice, a composed entry, and "
                         "a task that loads nothing")


class PlanPlantBlockTests(_TmpCase):
    """SPEC-0003 PLAN_PRINTS_PLANT_BLOCK (ADR-0027): a full `--plan` carries
    the plant's four `plant:` facts on one line before the LOAD line, so a
    session whose first move is the router learns them without opening
    index.md. The hook's full injection equals `--plan` byte for byte
    (ROUTE_FULL_TEXT_EQUALS_PLAN, X168 over the `planted` row of PLAN_TASK_SET)."""

    # The `planted` index.md, one `plant:` line rewritten or dropped: each is
    # an unfilled or partial block, so `--plan` prints no `plant:` line. A
    # placeholder is a value starting `<`, with or without a trailing YAML
    # comment (the template's own frontmatter uses inline `#` comments).
    UNFILLED_BLOCKS = {
        "placeholder": ("  environment_class: ephemeral-test\n",
                        "  environment_class: <ephemeral-test | staging>\n"),
        "placeholder-commented": ("  environment_class: ephemeral-test\n",
                                  "  environment_class: <ephemeral-test | staging>  # x\n"),
        "partial": ("  comment_language: de\n", ""),
    }

    def _plant(self, which: str) -> Path:
        if which not in self.UNFILLED_BLOCKS:
            return plan_fixture_plant(self.tmp, which)
        d = self.tmp / f"case-{which}"
        d.mkdir()
        plant = plan_fixture_plant(d, "planted")
        idx = plant / "docs" / "graph" / "index.md"
        line, repl = self.UNFILLED_BLOCKS[which]
        text = idx.read_text(encoding="utf-8")
        self.assertIn(line, text, "harness: the planted block lacks the line to rewrite")
        idx.write_text(text.replace(line, repl, 1), encoding="utf-8")
        return plant

    def test_plan_prints_plant_block(self):
        task = "write widget ledger tests"
        cases = [("planted", [PLANT_LINE]), ("main", [])] + [(w, []) for w in self.UNFILLED_BLOCKS]
        for which, want in cases:
            with self.subTest(index=which):
                r = run_plant_tool(self._plant(which), "--plan", task)
                self.assertEqual(r.returncode, 0, r.stderr)
                lines = r.stdout.splitlines()
                got = [l for l in lines if l.startswith("plant:")]
                self.assertEqual(got, want, f"`plant:` lines of --plan:\n{r.stdout}")
                load_at = next((i for i, l in enumerate(lines) if LOAD_HEAD.match(l)), None)
                self.assertIsNotNone(load_at, f"harness: no LOAD line in --plan:\n{r.stdout}")
                if want:
                    self.assertLess(lines.index(PLANT_LINE), load_at,
                                    f"the `plant:` line comes after LOAD:\n{r.stdout}")


# --------------------------------------------------------------------------
# `--show <id>...`: the node view after routing (SPEC-0003 §6, ADR-0025)
# --------------------------------------------------------------------------

# The keys §6 does not print: router-only and spawn keys.
SHOW_DROPPED_KEYS = ("load_when", "routing_triggers", "est_tokens", "tier", "kind", "name",
                     "description", "prevents", "tools", "model", "effort", "can_delegate",
                     "max_spawn_depth", "command")
# Node edges print as bare ids; leaf entries resolve to a path from the plant root.
SHOW_EDGE_KEYS = ("owns", "requires", "peers", "composes", "delegates_to")
SHOW_LEAF_KEYS = {"artifacts": "docs/graph/{}", "plant_knowledge": "docs/graph/{}",
                  "libraries": "docs/graph/libraries/{}.md"}
# The keys §6 prints on the `origin:` line, each as `<key>: <value>`.
SHOW_ORIGIN_KEYS = ("origin", "repo", "status", "status_date", "owner", "ends_when", "scope",
                    "reason", "recorded_in", "departs_from")
POINTER_KEYS = {"requires", "peers", "composes", "delegates_to", "artifacts", "libraries",
                "plant_knowledge"}

SHOW_AGENT = """---
name: reviewer
description: Senior reviewer for the widget ledger; reads diffs against the spec.
tools: [Read, Grep, Bash]
model: opus
effort: medium
routing_triggers:
  - "review the widget ledger diff"
can_delegate: false
max_spawn_depth: 1
command: /review-ledger
id: agent.reviewer
tier: 2
kind: agent
origin: seed
title: reviewer \u2014 reads widget ledger diffs against the spec
owns:
  - reviewer.charter
requires: [root]
peers: [agent.tester, subsystem.orders]
delegates_to: [agent.tester]
plant_knowledge:
  - specs/
  - evaluations/
prevents: A diff that lands without a reviewer reading it against the spec.
load_when: ["review the widget ledger diff"]
est_tokens: 300
---

# Reviewer

You review the widget ledger. See `docs/graph/specs/` for the contracts.
"""

# Frontmatter-only leaves: no `artifacts` or `plant_knowledge` entry is named
# in the body, so a view without the header would lose every one of them.
SHOW_DOMAIN = """---
id: domain.provenance
tier: 2
kind: domain
origin: project
repo: vendor/ledger
status: open
status_date: 2026-10-01
owner: ledger-team
ends_when: the audit chain is signed end to end
scope: provenance records of the ledger
reason: the chain is unsigned today
recorded_in: docs/graph/plans/grill.md
title: provenance \u2014 where each ledger record came from
owns: [provenance.chain]
requires: [root]
peers: [subsystem.billing]
artifacts:
  - architecture/provenance.md
  - runbooks/provenance-audit.md
plant_knowledge: [data/]
load_when: ["provenance chain audit"]
est_tokens: 200
---

# Provenance

A record keeps its origin through every hop.\u0020\u0020

```text
---
id: not.a.header
---
```

| hop | carries |
|-----|---------|
| ingest | the source id |
| merge  | both parents\u0020 |

Trailing line with spaces after it.\u0020\u0020\u0020
"""


def show_fixture_plant(tmp: Path) -> Path:
    """The `main` PLAN_* plant plus an agent node at docs/graph/agents/05-reviewer.md
    (a path its id does not spell) carrying every router and spawn key, and
    `domain.provenance`, whose `artifacts` and `plant_knowledge` are named in
    its frontmatter only and whose body holds a fenced block, a table and
    trailing whitespace. Every leaf it names exists."""
    plant = plan_fixture_plant(tmp, "main")
    graph = plant / "docs" / "graph"
    (graph / "agents" / "05-reviewer.md").write_text(SHOW_AGENT, encoding="utf-8")
    (graph / "nodes" / "domain.provenance.md").write_text(SHOW_DOMAIN, encoding="utf-8")
    for leaf in ("architecture/provenance.md", "runbooks/provenance-audit.md"):
        (graph / leaf).parent.mkdir(parents=True, exist_ok=True)
        (graph / leaf).write_text(f"# {leaf}\n", encoding="utf-8")
    for d in ("specs", "evaluations", "data"):
        (graph / d).mkdir(exist_ok=True)
    with (graph / "index.md").open("a", encoding="utf-8") as f:
        f.write("- agent.reviewer\n- domain.provenance\n")
    return plant


def fixture_node_files(plant: Path) -> dict:
    """{id: (path from the plant root, raw text)} for every node file of the plant."""
    graph = plant / "docs" / "graph"
    out = {}
    for p in sorted(list((graph / "nodes").glob("*.md")) + list((graph / "agents").glob("*.md"))):
        text = p.read_text(encoding="utf-8")
        meta, _ = FRONTMATTER.parse(text, p)
        out[meta["id"]] = (p.relative_to(plant).as_posix(), text)
    return out


def _load_frontmatter_reader():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "cypress_frontmatter", SEED / "templates" / "knowledge-graph" / "frontmatter.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


FRONTMATTER = _load_frontmatter_reader()


def show_header(out: str) -> list:
    """The header lines of a one-node `--show`: up to the first blank line."""
    return out.split("\n\n", 1)[0].split("\n")


def body_after_fence(text: str) -> str:
    """The file's bytes after its closing frontmatter fence and the blank line after it."""
    rest = text.split("\n---\n", 1)[1]
    return rest[1:] if rest.startswith("\n") else rest


class ShowTests(_TmpCase):
    """SPEC-0003 SHOW_*: `graph-lint.py --show <id>...` prints each node as a
    §6 header (path, title, every edge and leaf pointer, origin) and its body
    verbatim, without the router and spawn keys."""

    def show(self, plant: Path, *ids: str) -> subprocess.CompletedProcess:
        return run_plant_tool(plant, "--show", *ids)

    def test_show_keeps_every_pointer(self):
        """SHOW_KEEPS_EVERY_POINTER: for every node of the fixture, every value of
        every frontmatter key the view keeps is on its §6 header line, leaves
        resolved to their path; the first line names the node file. The
        expected values are read from the raw file, not listed by hand."""
        plant = show_fixture_plant(self.tmp)
        files = fixture_node_files(plant)
        kinds = set()
        for nid, (path, text) in files.items():
            meta, _ = FRONTMATTER.parse(text, path)
            kinds |= POINTER_KEYS & set(meta)
            with self.subTest(node=nid):
                r = self.show(plant, nid)
                self.assertEqual(r.returncode, 0, f"--show {nid} exited {r.returncode}:\n{r.stderr}")
                head = show_header(r.stdout)
                self.assertTrue(head[0].startswith(f"# {nid} {path}: "),
                                f"the first line does not name {path}: {head[0]!r}")
                by_key = {l.split(": ", 1)[0]: l.split(": ", 1)[1] for l in head[1:] if ": " in l}
                missing = []
                for key, value in meta.items():
                    if key in SHOW_DROPPED_KEYS or key in ("id", "title"):
                        continue
                    values = value if isinstance(value, list) else [value]
                    if key in SHOW_EDGE_KEYS or key in SHOW_LEAF_KEYS:
                        shown = set(by_key.get(key, "").split(", "))
                        form = SHOW_LEAF_KEYS.get(key, "{}")
                        missing += [f"{key}: {form.format(v)}" for v in values
                                    if form.format(v) not in shown]
                    elif key in SHOW_ORIGIN_KEYS:
                        origin = next((l for l in head if l.startswith("origin: ")), "")
                        missing += [f"{key}: {v}" for v in values if f"{key}: {v}" not in origin]
                    else:
                        self.fail(f"harness: fixture key {key!r} of {nid} is in no §6 row")
                self.assertEqual(missing, [], f"pointers in {path} missing from the header:\n"
                                              + "\n".join(head))
                self.assertTrue(r.stdout.endswith(body_after_fence(text)),
                                "the body (and every pointer it names) is not printed")
        self.assertEqual(kinds, POINTER_KEYS, "harness: the fixture must carry every pointer kind")
        _, provenance = files["domain.provenance"]
        body = body_after_fence(provenance)
        self.assertFalse([a for a in ("provenance.md", "provenance-audit.md", "data/") if a in body],
                         "harness: domain.provenance's leaves must be frontmatter-only")

    def test_show_drops_router_and_spawn_keys(self):
        """SHOW_DROPS_ROUTER_AND_SPAWN_KEYS: an agent and an expertise node in one
        call; no header line names a router or spawn key, and one blank line
        separates the first node's body from the second header."""
        plant = show_fixture_plant(self.tmp)
        files = fixture_node_files(plant)
        present = set()
        for nid in ("agent.reviewer", "expertise.dotnet"):
            present |= set(FRONTMATTER.parse(files[nid][1], nid)[0])
        self.assertEqual(present & set(SHOW_DROPPED_KEYS), set(SHOW_DROPPED_KEYS),
                         "harness: the two nodes must carry every dropped key")
        r = self.show(plant, "agent.reviewer", "expertise.dotnet")
        self.assertEqual(r.returncode, 0, f"--show exited {r.returncode}:\n{r.stderr}")
        first_body = body_after_fence(files["agent.reviewer"][1])
        second = "# expertise.dotnet docs/graph/nodes/expertise.dotnet.md: "
        self.assertIn(first_body + "\n" + second, r.stdout,
                      f"not the first body, one blank line, then the second header:\n{r.stdout}")
        self.assertTrue(r.stdout.startswith("# agent.reviewer docs/graph/agents/05-reviewer.md: "),
                        r.stdout[:200])
        heads = show_header(r.stdout) + show_header(r.stdout[r.stdout.index("\n" + second) + 1:])
        named = [(k, l) for l in heads for k in SHOW_DROPPED_KEYS
                 if re.search(rf"(^|\s){re.escape(k)}:", l)]
        self.assertEqual(named, [], "a header line names a router or spawn key")

    def test_show_body_verbatim(self):
        """SHOW_BODY_VERBATIM: after the header and one blank line, the output is
        the file's bytes after the closing fence and its blank line."""
        plant = show_fixture_plant(self.tmp)
        r = self.show(plant, "domain.provenance")
        self.assertEqual(r.returncode, 0, f"--show exited {r.returncode}:\n{r.stderr}")
        head = show_header(r.stdout)
        got = r.stdout[len("\n".join(head)) + 2:]
        self.assertTrue(head[0].startswith("# domain.provenance "), r.stdout[:200])
        self.assertEqual(got, body_after_fence(SHOW_DOMAIN))

    def test_show_unknown_id_fails(self):
        """SHOW_UNKNOWN_ID_FAILS: one unknown id among the asked ones exits 2,
        prints nothing on stdout, and names the unknown id on stderr."""
        plant = show_fixture_plant(self.tmp)
        known = self.show(plant, "root")
        self.assertEqual(known.returncode, 0,
                         f"harness: `--show root` alone must succeed, so the exit below is the "
                         f"unknown id's:\n{known.stderr}")
        r = self.show(plant, "root", "zz.no-such-node")
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertEqual(r.stdout, "")
        self.assertIn("zz.no-such-node", r.stderr)


# --------------------------------------------------------------------------
# The node-router ladder and its gated corpus (SPEC-0002 node router, ADR-0026)
# --------------------------------------------------------------------------

STRONG_TIER_CAP = 3                       # SPEC-0002 §6
NO_SIGNAL_TEXT = "no node matches this task; route a sharper task line, or enter a protocol:"
LONG_TASK_TEXT_RE = re.compile(r"^task too long to route \((\d+) terms\); run --plan on the task line$")
KIND_PREFIX_WORDS = ("domain", "subsystem", "protocol", "skill", "agent", "expertise",
                     "method", "crosscut")
SEED_NODE_CORPUS = SEED / "tests" / "graph-routes.golden.tsv"
CORPUS_CLASSES = ("contract", "paraphrase", "adversarial", "unknown-domain")


def with_repo(text: str, repo: str) -> str:
    """`node_md` text with a `repo:` key; the key is one word, so the token
    figure stays inside the band."""
    return text.replace("\ntier: 2\n", f"\ntier: 2\nrepo: {repo}\n", 1)


def ladder_plant(tmp: Path) -> Path:
    """One plant for every ladder case. Its trigger phrases are disjoint, so a
    case's task reaches exactly the node it is written for:
    - subsystem.ledger / subsystem.payroll: two-word phrases, one rare word each;
    - subsystem.billing (`repo: billsvc/src/payments`) under subsystem.monorepo
      (`repo: billsvc`, a bare repository root that claims no path);
    - subsystem.vendor (`supply-chain`: a compound whose fragment is `chain`);
    - subsystem.exports (`attestation`: a prefix fold of `attesting`);
    - expertise.ci-config (`pipeline yaml`), expertise.containers (`container`),
      expertise.terraform (`*.tf`), and the composing family under
      subsystem.orders (expertise.dotnet composes expertise.serilog, whose
      phrase is `log sink` and whose one-token trigger is `enrichers`);
    - agent.tester at agents/04-tester.md; protocol.review and skill.review
      share the basename `review.md`; protocol.verify is the second protocol."""
    nodes = expertise_family(**{
        "root": node_md("root", "root", requires=[], owns=["root.map"],
                        load_when=["what this project is"]),
        "subsystem.ledger": node_md("subsystem.ledger", "subsystem",
                                    load_when=["ledger reconciliation, nightly posting"]),
        "subsystem.payroll": node_md("subsystem.payroll", "subsystem",
                                     load_when=["payroll batch, salary slips"]),
        "subsystem.monorepo": with_repo(node_md("subsystem.monorepo", "subsystem",
                                                load_when=["monorepo layout"]), "billsvc"),
        "subsystem.billing": with_repo(node_md("subsystem.billing", "subsystem",
                                               load_when=["invoice sprocket gearing"]),
                                       "billsvc/src/payments"),
        "subsystem.vendor": node_md("subsystem.vendor", "subsystem",
                                    load_when=["supply-chain risk review"]),
        "subsystem.exports": node_md("subsystem.exports", "subsystem",
                                     load_when=["attestation bundle export"]),
        "expertise.ci-config": node_md("expertise.ci-config", "expertise", libraries=["ci"],
                                       owns=["ci-config.applicability"],
                                       load_when=["pipeline yaml"]),
        "expertise.containers": node_md("expertise.containers", "expertise",
                                        libraries=["containers"],
                                        owns=["containers.applicability"],
                                        load_when=["container"]),
        "expertise.terraform": node_md("expertise.terraform", "expertise",
                                       libraries=["terraform"], owns=["terraform.applicability"],
                                       load_when=["*.tf"]),
    })
    nodes["expertise.serilog"] = node_md(
        "expertise.serilog", "expertise", requires=["expertise.dotnet"],
        libraries=["dotnet"], owns=["serilog.applicability"],
        load_when=["structured logging, log sink", "enrichers"])
    built = build_graph(tmp, nodes, libraries=["dotnet", "terraform", "ci", "containers"])
    plant = tmp / "plant-ladder"
    (plant / "docs").mkdir(parents=True)
    graph = plant / "docs" / "graph"
    shutil.move(str(built), str(graph))
    machinery = {
        ("agents", "04-tester.md"): node_md("agent.tester", "agent",
                                            load_when=["widget gauge tests"]),
        ("protocols", "review.md"): node_md("protocol.review", "protocol",
                                            load_when=["code review gate"]),
        ("skills", "review.md"): node_md("skill.review", "skill",
                                         load_when=["review checklist technique"]),
        ("protocols", "verify.md"): node_md("protocol.verify", "protocol",
                                            load_when=["gates before done"]),
    }
    with (graph / "index.md").open("a", encoding="utf-8") as f:
        for (d, name), text in machinery.items():
            (graph / d).mkdir(exist_ok=True)
            (graph / d / name).write_text(text, encoding="utf-8")
            f.write(f"- {re.search(r'^id: (.+)$', text, re.M).group(1)}\n")
    return plant


def filler_words(n: int) -> list:
    """`n` distinct four-letter words no node knows: consonants only, so no
    suffix rule and no prefix fold reduces two of them to one term."""
    letters = "bcdfghjklmnpqrtvwxz"
    words = [f"kv{a}{b}" for a in letters for b in letters]
    assert n <= len(words), n
    return words[:n]


def long_task_terms() -> int:
    """`LONG_TASK_TERMS` as the tool defines it (SPEC-0002 §6 names it a
    constant of graph-lint.py, valued at GREEN). None when it is undefined."""
    m = re.search(r"^LONG_TASK_TERMS\s*=\s*(\d+)", GRAPH_LINT.read_text(encoding="utf-8"), re.M)
    return int(m.group(1)) if m else None


def corpus_rows(path: Path) -> list:
    return [line.split("\t") for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")]


def write_corpus(path: Path, rows: list, header: str = "") -> Path:
    path.write_text(header + "".join("\t".join(r) + "\n" for r in rows), encoding="utf-8")
    return path


class NodeRouterLadderTests(_TmpCase):
    """SPEC-0002, node router: the tier ladder, the cap, the phrase rule, the
    lexical guards and the two abstentions, read from `--plan-json`."""

    def setUp(self):
        super().setUp()
        self.plant = ladder_plant(self.tmp)

    def route(self, task: str) -> dict:
        r = run_plant_tool(self.plant, f"--plan-json={task}")
        self.assertEqual(r.returncode, 0,
                         f"--plan-json={task!r} exited {r.returncode}:\n{r.stdout}\n{r.stderr}")
        return json.loads(r.stdout)

    @staticmethod
    def hows(doc: dict) -> dict:
        return {e["id"]: e["how"] for e in doc["load"]}

    def add_nodes(self, nodes: dict):
        """Write `nodes` (id -> text) into this case's plant and list them in
        index.md: a fixture row the shared ladder must not carry."""
        graph = self.plant / "docs" / "graph"
        with (graph / "index.md").open("a", encoding="utf-8") as f:
            for nid, text in nodes.items():
                (graph / "nodes" / f"{nid}.md").write_text(text, encoding="utf-8")
                f.write(f"- {nid}\n")

    def assertLoadedAs(self, doc: dict, node_id: str, kind: str, detail=..., task: str = ""):
        how = self.hows(doc).get(node_id)
        self.assertIsNotNone(how, f"{task!r}: {node_id} not in LOAD:\n{doc['load']!r}")
        self.assertEqual(how["kind"], kind, f"{task!r}: {node_id} loaded as {how!r}")
        if detail is not ...:
            self.assertEqual(how["detail"], detail, f"{task!r}: {node_id} loaded as {how!r}")

    def test_graph_route_named_id_loads_it(self):
        """GRAPH_ROUTE_NAMED_ID_LOADS_IT: an exact dotted id wins; the other
        node's trigger phrase in the same task does not load it. A word equal
        to an id with no `.` (`root`) is no tier-1 hit."""
        task = "fix subsystem.ledger before the payroll batch"
        doc = self.route(task)
        self.assertLoadedAs(doc, "subsystem.ledger", "named_id", task=task)
        self.assertNotIn("subsystem.payroll", self.hows(doc), f"{task!r}: {doc['load']!r}")
        for task in ("root cause of the crash", "a pipe of edges from root to leaf"):
            with self.subTest(task):
                hows = self.hows(self.route(task))
                self.assertEqual([i for i, h in hows.items() if h["kind"] == "named_id"], [],
                                 f"{task!r}: the bare word `root` is no named id: {hows!r}")

    def test_graph_route_named_path_loads_its_owner(self):
        """GRAPH_ROUTE_NAMED_PATH_LOADS_ITS_OWNER: a node file path, a path
        under a non-root `repo:`, an expertise pattern, a unique basename; a
        shared basename and a bare repository root claim nothing."""
        owned = (
            ("node file", "tidy docs/graph/nodes/subsystem.ledger.md",
             "subsystem.ledger", "named_path", "docs/graph/nodes/subsystem.ledger.md"),
            ("repo prefix", "fix billsvc/src/payments/refund.py",
             "subsystem.billing", "named_path", "billsvc/src/payments/refund.py"),
            ("expertise pattern", "bump infra/main.tf",
             "expertise.terraform", "inferred", "infra/main.tf"),
            ("unique basename", "rename 04-tester.md", "agent.tester", "named_path", "04-tester.md"),
        )
        for label, task, nid, kind, detail in owned:
            with self.subTest(label):
                self.assertLoadedAs(self.route(task), nid, kind, detail, task)
        unowned = (
            ("shared basename", "merge review.md", ("protocol.review", "skill.review")),
            ("bare repo root", "fix billsvc/README.md", ("subsystem.monorepo",)),
        )
        for label, task, ids in unowned:
            with self.subTest(label):
                hows = self.hows(self.route(task))
                for nid in ids:
                    self.assertNotEqual((hows.get(nid) or {}).get("kind"), "named_path",
                                        f"{task!r}: {nid} claimed by path: {hows!r}")

    def test_graph_route_phrase_loads_its_node(self):
        """GRAPH_ROUTE_PHRASE_LOADS_ITS_NODE: a contiguous trigger phrase loads
        its node as `phrase`; reordered or interrupted tokens do not. Rows
        moved from SPEC-0005's retired promotion tests: a piece holding a
        slash and a space is a phrase, not a pattern; stopwords drop out of
        the piece and the task alike, so `build release` holds `build and
        release`; `how.detail` is the first held piece in `load_when` order,
        not in task order."""
        task = "regenerate the salary slips"
        self.assertLoadedAs(self.route(task), "subsystem.payroll", "phrase", "salary slips", task)
        for task in ("regenerate the slips salary", "regenerate the salary paper slips"):
            with self.subTest(task):
                how = self.hows(self.route(task)).get("subsystem.payroll") or {}
                self.assertNotEqual(how.get("kind"), "phrase", f"{task!r}: {how!r}")
        self.add_nodes({
            "subsystem.delivery": node_md("subsystem.delivery", "subsystem",
                                          load_when=["ci/cd release train"]),
            "subsystem.shipping": node_md("subsystem.shipping", "subsystem",
                                          load_when=["build and release"]),
            "subsystem.shipyard": node_md("subsystem.shipyard", "subsystem",
                                          load_when=["dock crane, harbor tug"]),
        })
        rows = (
            ("slash and space", "tune the ci/cd release train",
             "subsystem.delivery", "ci/cd release train"),
            ("stopwords, as written", "tune the build and release flow",
             "subsystem.shipping", "build and release"),
            ("stopwords dropped", "tune the build release flow",
             "subsystem.shipping", "build and release"),
            ("first held piece in load_when order", "harbor tug dock crane",
             "subsystem.shipyard", "dock crane"),
        )
        for label, task, nid, detail in rows:
            with self.subTest(label):
                self.assertLoadedAs(self.route(task), nid, "phrase", detail, task)

    def test_strong_tier_over_cap_falls_through(self):
        """STRONG_TIER_OVER_CAP_FALLS_THROUGH: more than STRONG_TIER_CAP named
        ids is no tier-1 hit; the next tier (here a phrase) decides. At the cap
        the ids load as named. Also asserts PHRASE_TIER_FLOODS_LOAD: four
        nodes' phrases in one task load all four, as `phrase`."""
        ids = ["subsystem.ledger", "subsystem.vendor", "subsystem.exports", "subsystem.monorepo"]
        at_cap = " ".join(ids[:STRONG_TIER_CAP]) + " and the salary slips"
        doc = self.route(at_cap)
        for nid in ids[:STRONG_TIER_CAP]:
            self.assertLoadedAs(doc, nid, "named_id", task=at_cap)
        over = " ".join(ids[:STRONG_TIER_CAP + 1]) + " and the salary slips"
        doc = self.route(over)
        self.assertEqual([i for i, h in self.hows(doc).items() if h["kind"] == "named_id"], [],
                         f"{over!r}: {doc['load']!r}")
        self.assertLoadedAs(doc, "subsystem.payroll", "phrase", "salary slips", over)
        with self.subTest("tier 3 is uncapped (PHRASE_TIER_FLOODS_LOAD)"):
            four = ("ledger reconciliation, payroll batch, pipeline yaml, "
                    "attestation bundle export")
            doc = self.route(four)
            for nid in ("subsystem.ledger", "subsystem.payroll", "expertise.ci-config",
                        "subsystem.exports"):
                self.assertLoadedAs(doc, nid, "phrase", task=four)

    def test_promotion_needs_a_contiguous_phrase(self):
        """PROMOTION_NEEDS_A_CONTIGUOUS_PHRASE: the two words apart are no
        phrase hit; the phrase loads the node as `phrase` (tier 3). A trigger piece
        that reduces to one content token seeds its node by no tier, even on
        an equal whole task word. Rows moved from SPEC-0005's retired
        promotion tests: one word of a two-word phrase, half a version token,
        the whole version token `net10.0` (one token), `go toolchain` (one
        token once the short word drops) and a prefix fold load nothing."""
        hit = "edit the pipeline yaml"
        self.assertLoadedAs(self.route(hit), "expertise.ci-config", "phrase", "pipeline yaml", hit)
        # Apart, the two words are two distinct confident terms, so a tier-4
        # `scored` entry stays possible (this contract's And); no phrase hit.
        apart = "edit the yaml for the release pipeline"
        how = self.hows(self.route(apart)).get("expertise.ci-config") or {}
        self.assertNotEqual(how.get("kind"), "phrase", f"{apart!r}: {how!r}")
        self.add_nodes({
            "expertise.runtime-ten": node_md("expertise.runtime-ten", "expertise",
                                             libraries=["ci"], owns=["runtime-ten.applicability"],
                                             load_when=["net10.0"]),
            "expertise.golang": node_md("expertise.golang", "expertise", libraries=["ci"],
                                        owns=["golang.applicability"],
                                        load_when=["go toolchain"]),
            "expertise.schema": node_md("expertise.schema", "expertise", libraries=["ci"],
                                        owns=["schema.applicability"],
                                        load_when=["migration tooling"]),
        })
        rows = (
            ("one word of the phrase", "edit the pipeline", "expertise.ci-config"),
            ("one-token piece, equal whole word", "rebuild the container image",
             "expertise.containers"),
            ("one-token piece, plural", "rebuild the containers image", "expertise.containers"),
            ("one-token piece, inside a compound", "rebuild the multi-container image",
             "expertise.containers"),
            ("half a version token", "target net10", "expertise.runtime-ten"),
            ("whole version token, one token", "target net10.0", "expertise.runtime-ten"),
            ("reduces to one token", "bump the toolchain", "expertise.golang"),
            ("prefix fold", "migrating tooling", "expertise.schema"),
        )
        for label, task, nid in rows:
            with self.subTest(label):
                self.assertNotIn(nid, self.hows(self.route(task)), f"{task!r}")

    def test_composed_child_needs_its_own_phrase(self):
        """COMPOSED_CHILD_NEEDS_ITS_OWN_PHRASE: with the parent loaded (through
        a named id, so tier 1 decides and no phrase tier runs), one word of
        the child's phrase does not compose it; the phrase does. With the
        parent a tier-3 phrase entry, a one-token child piece (`enrichers`)
        composes the child on the equal whole word, not on an inflection
        (from SPEC-0005's retired PLAN_PROMOTED_NODE_TAKES_ITS_CLOSURE: a
        multi-word child phrase the task holds is itself a tier-3 entry)."""
        one = "fix the sink in subsystem.orders"
        doc = self.route(one)
        self.assertIn("expertise.dotnet", self.hows(doc), f"harness: the parent must load:\n{doc!r}")
        self.assertNotIn("expertise.serilog", self.hows(doc), f"{one!r}: {doc['load']!r}")
        whole = "fix the log sink in subsystem.orders"
        self.assertLoadedAs(self.route(whole), "expertise.serilog", "composed", task=whole)
        word = "pin the target framework and the enrichers"
        doc = self.route(word)
        self.assertLoadedAs(doc, "expertise.dotnet", "phrase", "target framework", word)
        self.assertLoadedAs(doc, "expertise.serilog", "composed", "enrichers", word)
        inflected = "pin the target framework and the enricher"
        self.assertNotIn("expertise.serilog", self.hows(self.route(inflected)), inflected)

    def test_punctuation_does_not_change_a_term(self):
        """PUNCTUATION_DOES_NOT_CHANGE_A_TERM: a trailing mark on a task word
        leaves the route as it is without the mark."""
        base = "ledger reconciliation nightly payroll"
        want = self.route(base)
        self.assertTrue(want["load"], f"harness: {base!r} must load something:\n{want!r}")
        for mark in ".,:;?!)":
            with self.subTest(mark=mark):
                got = self.route(base.replace("nightly", "nightly" + mark))
                self.assertEqual((got["load"], got["notices"]), (want["load"], want["notices"]))

    def test_ids_and_paths_are_not_lexical_terms(self):
        """IDS_AND_PATHS_ARE_NOT_LEXICAL_TERMS: kind prefixes and the segments
        of an unowned path match nothing; the route is `no_signal`. This holds
        when a node's `load_when` writes kind words itself: a kind word is no
        term on the task side either."""
        tasks = (" ".join(KIND_PREFIX_WORDS) + " src/payroll/ledger/vendor.py",
                 "the protocol and skill for an agent hook")
        for label, extra in (("ladder", {}), ("a load_when writes kind words", {
                "subsystem.policy": node_md("subsystem.policy", "subsystem",
                                            load_when=["which protocol applies",
                                                       "skill and agent handbook"])})):
            self.add_nodes(extra)
            for task in tasks:
                with self.subTest(label, task=task[:40]):
                    doc = self.route(task)
                    self.assertEqual(doc["load"], [], f"{task!r}")
                    self.assertEqual([n["code"] for n in doc["notices"]], ["no_signal"],
                                     f"{task!r}: {doc!r}")

    def test_one_term_cannot_seed_a_node(self):
        """ONE_TERM_CANNOT_SEED_A_NODE: one distinct confident term, however
        rare, does not load its node lexically; a second one does."""
        one = "the payroll"
        self.assertNotIn("subsystem.payroll", self.hows(self.route(one)), one)
        two = "the salary payroll"
        self.assertLoadedAs(self.route(two), "subsystem.payroll", "scored", task=two)

    def test_compound_fragment_is_weak_evidence(self):
        """COMPOUND_FRAGMENT_IS_WEAK_EVIDENCE (node router): `chain` out of
        `supply-chain` is no confident term, so with one other term it does
        not seed; the compound itself does."""
        frag = "review the chain"
        self.assertNotIn("subsystem.vendor", self.hows(self.route(frag)), frag)
        whole = "review the supply-chain"
        self.assertIn("subsystem.vendor", self.hows(self.route(whole)), whole)

    def test_rarity_amplifies_only_a_confident_match(self):
        """RARITY_AMPLIFIES_ONLY_A_CONFIDENT_MATCH (node router): a rare term
        that reaches one node only by a prefix fold (`attesting` to
        `attestation`) is no confident term, so it cannot be the second."""
        task = "export the attesting"
        self.assertNotIn("subsystem.exports", self.hows(self.route(task)), task)

    def test_no_signal_loads_nothing(self):
        """NO_SIGNAL_LOADS_NOTHING: an unknown-domain task loads nothing, not
        root, with one `no_signal` notice naming the protocol ids, sorted, and
        never `index.md`."""
        task = "what's the weather in Rome tomorrow"
        doc = self.route(task)
        self.assertEqual(doc["load"], [], f"{task!r}: {doc!r}")
        self.assertEqual([n["code"] for n in doc["notices"]], ["no_signal"], f"{doc!r}")
        text = doc["notices"][0]["text"]
        self.assertTrue(text.startswith(NO_SIGNAL_TEXT), text)
        named = re.findall(r"[a-z][a-z0-9_.-]*", text[len(NO_SIGNAL_TEXT):])
        self.assertEqual(named, ["protocol.review", "protocol.verify"], text)
        self.assertNotIn("index.md", text)

    def test_long_task_abstains_with_notice(self):
        """LONG_TASK_ABSTAINS_WITH_NOTICE: over LONG_TASK_TERMS distinct terms,
        a named id included, loads nothing with one `long_task` notice that
        counts them; exactly LONG_TASK_TERMS is routed."""
        cap = long_task_terms()
        self.assertIsNotNone(cap, "graph-lint.py defines no LONG_TASK_TERMS (SPEC-0002 §6)")
        words = filler_words(cap + 1)
        doc = self.route(" ".join(words))
        self.assertEqual(doc["load"], [])
        self.assertEqual([n["code"] for n in doc["notices"]], ["long_task"], f"{doc['notices']!r}")
        m = LONG_TASK_TEXT_RE.match(doc["notices"][0]["text"])
        self.assertIsNotNone(m, doc["notices"][0]["text"])
        self.assertEqual(int(m.group(1)), cap + 1)
        named = self.route(" ".join(words[:cap] + ["subsystem.ledger"]))
        self.assertEqual(named["load"], [], "a named id does not route a long task")
        self.assertEqual([n["code"] for n in named["notices"]], ["long_task"])
        at = self.route(" ".join(words[:cap]))
        self.assertNotIn("long_task", [n["code"] for n in at["notices"]],
                         f"exactly LONG_TASK_TERMS terms must be routed: {at['notices']!r}")

    def test_a_word_every_task_writes_cannot_select_an_agent(self):
        """A_WORD_EVERY_TASK_WRITES_CANNOT_SELECT_AN_AGENT, in both routers: a
        pronoun added to a task, and a pronoun in a trigger, change nothing."""
        pronouns = "we our you your my i us"
        base = "rename 04-tester.md"
        self.assertEqual(self.route(f"{pronouns} {base}")["load"], self.route(base)["load"])
        plant = _INSTALL["plant"]
        installed_graph(self)
        lone = subprocess.run([sys.executable, "docs/graph/agent-lint.py", "--route", pronouns],
                              cwd=str(plant), capture_output=True, text=True, timeout=120)
        self.assertEqual(lone.returncode, 0, lone.stderr)
        self.assertRegex(lone.stdout, r"confidence: (LOW|NONE)",
                         f"agent router: pronouns alone must not select an agent:\n{lone.stdout}")
        doc = json.loads(run_plant_tool(plant, f"--plan-json={pronouns}").stdout)
        self.assertEqual(doc["load"], [], f"node router: pronouns alone load nothing: {doc!r}")


class NodeRouteEvalTests(unittest.TestCase):
    """SPEC-0002 GRAPH_EVAL_GATES_PER_CLASS and the corpus-honesty contracts
    widened to the node router: `graph-lint.py --eval <tsv>` over the graph a
    fresh install places."""

    def setUp(self):
        self.plant = _INSTALL["plant"]
        installed_graph(self)
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def evaluate(self, tsv: Path) -> subprocess.CompletedProcess:
        return run_plant_tool(self.plant, "--eval", str(tsv))

    def corpus_copy(self, rows: list) -> Path:
        return write_corpus(self.tmp / "corpus.tsv", rows)

    def breached_corpus(self) -> Path:
        """A copy of the seed's corpus with one forbidden id added to an
        adversarial row the router loads: GRAPH_ADVERSARIAL_FORBIDDEN_MAX
        breaches on the measured graph."""
        rows = corpus_rows(SEED_NODE_CORPUS)
        bait = next(i for i, row in enumerate(rows) if row[3] == "adversarial")
        doc = json.loads(run_plant_tool(self.plant, f"--plan-json={rows[bait][0]}").stdout)
        loaded = [e["id"] for e in doc["load"]]
        self.assertTrue(loaded, f"harness: the bait row must load something: {rows[bait]!r}")
        rows[bait][2] = ",".join([x for x in rows[bait][2].split(",") if x != "-"] + [loaded[0]])
        return write_corpus(self.tmp / "breached.tsv", rows)

    def test_graph_eval_gates_per_class(self):
        """GRAPH_EVAL_GATES_PER_CLASS: the seed's corpus exits 0 with every
        figure on lines naming its class; one forbidden id added to a row the
        router loads exits 1 naming the breached ratchet. Also asserts
        GRAPH_ROUTE_RATCHET_BREACHED (§7), on the measured graph."""
        self.assertTrue(SEED_NODE_CORPUS.exists(), f"missing corpus: {SEED_NODE_CORPUS}")
        r = self.evaluate(SEED_NODE_CORPUS)
        self.assertEqual(r.returncode, 0, f"--eval exited {r.returncode}:\n{r.stdout}\n{r.stderr}")
        for cls in CORPUS_CLASSES:
            self.assertRegex(r.stdout, rf"(?m)^.*\b{re.escape(cls)}\b.*\d", f"no line for {cls}")
        for label in ("recall", "covered", "mean", "irrelevant", "forbidden", "abstain"):
            self.assertIn(label, r.stdout.lower(), f"--eval prints no {label!r} figure:\n{r.stdout}")
        r = self.evaluate(self.breached_corpus())
        self.assertEqual(r.returncode, 1, f"{r.stdout}\n{r.stderr}")
        self.assertIn("GRAPH_ADVERSARIAL_FORBIDDEN_MAX", r.stdout + r.stderr)

    def test_graph_ratchets_are_keyed_to_their_graph(self):
        """GRAPH_RATCHETS_ARE_KEYED_TO_THEIR_GRAPH: on a graph holding one node
        whose `origin` is not `seed` (a grown plant), a corpus that breaches
        GRAPH_ADVERSARIAL_FORBIDDEN_MAX prints every class figure and one
        digit-free line saying the ratchets are reported and not gated, and
        exits 0; the same corpus on the seed's own graph exits 1 naming the
        ratchet. Also asserts GRAPH_ROUTE_RATCHET_BREACHED (§7, "on any other
        graph the figure prints and the exit status does not change")."""
        breached = self.breached_corpus()
        grown = self.tmp / "grown"
        shutil.copytree(self.plant / "docs", grown / "docs")
        flipped = next(p for p in sorted((grown / "docs" / "graph").rglob("*.md"))
                       if re.search(r"^origin: seed$", p.read_text(encoding="utf-8"), re.M))
        flipped.write_text(re.sub(r"^origin: seed$", "origin: project",
                                  flipped.read_text(encoding="utf-8"), count=1, flags=re.M),
                           encoding="utf-8")
        r = run_plant_tool(grown, "--eval", str(breached))
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 0,
                         f"a GRAPH_* ratchet gated a graph holding {flipped.name} "
                         f"(origin: project):\n{out}")
        for cls in CORPUS_CLASSES:
            self.assertRegex(r.stdout, rf"(?m)^.*\b{re.escape(cls)}\b.*\d", f"no line for {cls}")
        self.assertRegex(r.stdout, r"(?im)^[^\d\n]*\bnot gated\b[^\d\n]*$",
                         f"no digit-free line saying the ratchets are not gated:\n{out}")
        seed = self.evaluate(breached)
        self.assertEqual(seed.returncode, 1, f"{seed.stdout}\n{seed.stderr}")
        self.assertIn("GRAPH_ADVERSARIAL_FORBIDDEN_MAX", seed.stdout + seed.stderr)

    def test_graph_eval_every_number_names_its_corpus(self):
        """EVERY_NUMBER_NAMES_ITS_CORPUS (node router): every line of the
        report that carries a figure names one class, and no line averages
        classes."""
        r = self.evaluate(SEED_NODE_CORPUS)
        self.assertEqual(r.returncode, 0, f"{r.stdout}\n{r.stderr}")
        figured = [l for l in r.stdout.splitlines() if re.search(r"\d", l)]
        self.assertTrue(figured, r.stdout)
        for line in figured:
            named = [c for c in CORPUS_CLASSES if re.search(rf"\b{re.escape(c)}\b", line)]
            self.assertEqual(len(named), 1, f"a figure names {named or 'no class'}: {line!r}")

    def test_graph_held_out_stays_held_out(self):
        """HELD_OUT_STAYS_HELD_OUT (node router): a paraphrase row that copies
        its target's `load_when` fails the gate, naming the row."""
        rows = corpus_rows(SEED_NODE_CORPUS)
        i = next(i for i, row in enumerate(rows) if row[3] == "paraphrase" and row[1] == "method.tiers")
        tiers = (self.plant / "docs" / "graph" / "method" / "tiers.md").read_text(encoding="utf-8")
        trigger = re.search(r"^load_when:\n\s+- \"?([^\"\n]+)", tiers, re.M).group(1)
        rows[i][0] = trigger
        r = self.evaluate(self.corpus_copy(rows))
        self.assertEqual(r.returncode, 1, f"{r.stdout}\n{r.stderr}")
        self.assertIn(trigger, r.stdout + r.stderr)

    def test_graph_vacuous_corpus_is_refused(self):
        """VACUOUS_CORPUS_IS_REFUSED (node router): a corpus where every row
        expects abstention fails closed, saying so. An adversarial row whose
        `forbidden_ids` is `-` (it baits nothing) and an unknown-domain row
        that lists required ids each fail, naming the row."""
        rows = [row for row in corpus_rows(SEED_NODE_CORPUS) if row[3] == "unknown-domain"]
        r = self.evaluate(self.corpus_copy(rows))
        self.assertEqual(r.returncode, 1, f"{r.stdout}\n{r.stderr}")
        self.assertRegex((r.stdout + r.stderr).lower(), r"vacuous")
        for label, cls, col, value in (("bait-free adversarial row", "adversarial", 2, "-"),
                                       ("unknown-domain row with required ids",
                                        "unknown-domain", 1, "method.tiers")):
            with self.subTest(label):
                rows = corpus_rows(SEED_NODE_CORPUS)
                i = next(i for i, row in enumerate(rows)
                         if row[3] == cls and not row[0].startswith("@file:"))
                rows[i][col] = value
                r = self.evaluate(self.corpus_copy(rows))
                self.assertEqual(r.returncode, 1, f"{label}: {r.stdout}\n{r.stderr}")
                self.assertIn(rows[i][0], r.stdout + r.stderr, f"{label}: the row is not named")

    def test_graph_abstention_is_a_correct_outcome(self):
        """ABSTENTION_IS_A_CORRECT_OUTCOME (node router): a paraphrase row
        the router loads nothing for, with `no_signal`, does not fail the gate."""
        task = "kvbc kvbd kvbf"
        doc = json.loads(run_plant_tool(self.plant, f"--plan-json={task}").stdout)
        self.assertEqual([n["code"] for n in doc["notices"]], ["no_signal"],
                         f"harness: the added row must abstain: {doc!r}")
        rows = corpus_rows(SEED_NODE_CORPUS) + [[task, "method.tiers", "-", "paraphrase"]]
        r = self.evaluate(self.corpus_copy(rows))
        self.assertEqual(r.returncode, 0, f"{r.stdout}\n{r.stderr}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
