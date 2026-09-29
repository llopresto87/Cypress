#!/usr/bin/env python3
"""Tests for graph-lint.py: the node-graph contract and the `--plan` router.

Each case runs the tool through its CLI against a hermetic temp graph, on the
stdlib alone: `python3 tests/test_graph_lint.py`.
"""

from __future__ import annotations

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
        self.assertIn("LOAD (0 nodes", r.stdout)


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


def plan_section(out: str, header: str) -> dict:
    """{node id: the whole entry line} for the section starting `header`."""
    lines, on = {}, False
    for line in out.splitlines():
        if line.startswith(header):
            on = True
            continue
        if on:
            if not line.startswith("  "):
                break
            if not line.startswith("  ! "):
                lines[line.split()[0]] = line
    return lines


def load_section(out: str) -> dict:
    return plan_section(out, "LOAD (")


def not_loaded_section(out: str) -> set:
    return set(plan_section(out, "NOT LOADED"))


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
    """--plan descends only into the children the task names specifically.
    Each task was measured on the tool without descent: it loads the
    subsystem and the parent, not the child, so seeding alone passes nothing."""

    def plan(self, task, nodes=None, **kw):
        kw.setdefault("libraries", ["dotnet"])
        g = build_graph(self.tmp, nodes or expertise_family(), **kw)
        r = plan_output(g, task)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout

    def test_plan_descends_on_specific_term(self):
        """Asserts SPEC-0005 DESCENT_TEST_NOW_SEEDS_THE_CHILD.

        Rows: a child's own term descends it; family vocabulary does not;
        descent never folds a prefix (`migrating` is not `migration`); each of
        two levels descends on its own term; a target-framework token picks
        the major (by promotion, as it is a whole piece); a child that
        outscores its subsystem is reported as an entry, not as composed."""
        with self.subTest(row="specific term"):
            out = self.plan("in the orders service, fix the mapping")
            self.assertIn('expertise.ef-core', out)
            self.assertIn('composed by expertise.dotnet on "mapping"', out)
        with self.subTest(row="family vocabulary"):
            nodes = expertise_family()
            nodes["expertise.serilog"] = node_md(
                "expertise.serilog", "expertise", requires=["expertise.dotnet"],
                libraries=["dotnet"], owns=["serilog.applicability"],
                load_when=["structured logging, log sink", "dotnet logging"])
            out = self.plan("in the orders service, fix the dotnet mapping", nodes)
            self.assertNotIn("composed by expertise.dotnet on \"dotnet\"", out)
            self.assertRegex(out, r"expertise\.serilog\s+\S+\s+composed by .*no task term")
        with self.subTest(row="never folds"):
            out = self.plan(
                "in the orders service, fix the mapping, migrating the runner",
                with_migrations(expertise_family()))
            self.assertIn('composed by expertise.dotnet on "mapping"', out)
            self.assertRegex(out, r"expertise\.ef-migrations\s+\S+\s+composed by .*no task term")
        with self.subTest(row="two levels"):
            # "script", not "migration": `migration` is in the child's own id,
            # and a node named by the task is seeded, not descended to.
            out = self.plan(
                "in the orders service, fix the mapping, run the script",
                with_migrations(expertise_family()))
            self.assertIn('composed by expertise.dotnet on "mapping"', out)
            self.assertIn('composed by expertise.ef-core on "script"', out)
        with self.subTest(row="major by TFM token"):
            # The path glob keeps dotnet-10 from being seeded by its score.
            tfm = "net10.0"
            out = self.plan(
                f"in the orders service, editing src/Orders/**, target {tfm}",
                with_majors(expertise_family(), (8, 10)))
            line = load_section(out).get("expertise.dotnet-10")
            self.assertIsNotNone(line, f"the TFM token did not select dotnet-10:\n{out}")
            self.assertTrue(line.rstrip().endswith(f'<- promoted on "{tfm}"'),
                            f"dotnet-10 must load promoted on the whole TFM token "
                            f"{tfm!r} the task wrote:\n  {line}")
            self.assertRegex(out, r"expertise\.dotnet-8\s+\S+\s+composed by .*no task term")
        with self.subTest(row="top-scoring seed is an entry"):
            out = self.plan("entity mapping dbcontext orders")
            line = next(l for l in out.splitlines()
                        if l.strip().startswith("expertise.ef-core"))
            self.assertNotIn("composed by", line)

    def test_plan_leaves_the_unnamed_sibling_with_a_reason(self):
        out = self.plan("in the orders service, fix the mapping")
        self.assertRegex(
            out, r"expertise\.serilog\s+\S+\s+composed by expertise\.dotnet; "
                 r"no task term specific to it")

    def test_plan_descends_from_required_node(self):
        """The parent is not a seed here — it arrives through the subsystem's
        `requires`. Descent must work from a node the closure pulled in, which
        is what makes an agent's ordinary task reach library expertise."""
        out = self.plan("in the orders service, add a sink")
        self.assertIn('expertise.serilog', out)
        self.assertIn('composed by expertise.dotnet on "sink"', out)
        self.assertIn("subsystem.orders", out)

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
        self.assertRegex(out, r"subsystem\.billing\s+\S+\s+peer of subsystem\.orders")
        self.assertRegex(out, r"expertise\.serilog\s+\S+\s+composed by .*no task term")

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
# Promotion, inference and promoted closure (SPEC-0005). Each fixture was
# measured on the tool before promotion and inference existed: the expertise
# node a positive row asserts on was not in LOAD, so a row passes only
# through promotion or inference, never through the scored cut.
# --------------------------------------------------------------------------

class _PlanCase(_TmpCase):
    """Positive rows assert the suffix on the node's own LOAD line."""

    def plan(self, nodes: dict, task: str, **kw) -> str:
        g = build_graph(self.tmp, nodes)
        r = plan_output(g, task, **kw)
        self.assertEqual(r.returncode, 0,
                         f"--plan {task!r} exited {r.returncode}:\n{r.stdout}\n{r.stderr}")
        return r.stdout

    def assertLoadSuffix(self, out: str, node_id: str, suffix: str, task: str):
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
    words, so an expertise node loads only by promotion or inference."""
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


# Task "pipeline yaml": LOAD is the three pipeline decoys only.
PROMOTION = {
    "crosscut.release": node_md("crosscut.release", "crosscut",
                                load_when=["pipeline yaml"]),
    **expertise("expertise.ci-config", "pipeline yaml, build definitions", library="ci"),
}


def promotion_graph(vocabulary: str = "pipeline yaml") -> dict:
    return router_graph(PROMOTION, vocabulary, name="pipeline")


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


class PromotionTests(_PlanCase):

    def test_plan_promotes_expertise_past_the_scored_cut(self):
        """Asserts SPEC-0005 PLAN_PROMOTES_PHRASE_MATCHED_EXPERTISE.

        Also asserts SPEC-0005 PROMOTION_FLOODS_LOAD (the one-word-phrase row:
        every hit loads, uncapped). Rows: the base phrase, a one-word phrase
        on five nodes, a whole dotted compound, a phrase holding a slash (a
        phrase, since whitespace disqualifies a pattern), and the first
        hitting piece in `load_when` order."""
        langs = {}
        for c in "abcde":
            langs.update(expertise(f"expertise.lang-{c}", "python", library="python"))
        rows = [
            ("base", promotion_graph(), "pipeline yaml",
             ["expertise.ci-config"], '<- promoted on "pipeline yaml"'),
            ("one-word phrase, uncapped", router_graph(langs, "python tooling", "python"),
             "python tooling", list(langs), '<- promoted on "python"'),
            ("dotted compound", router_graph(expertise("expertise.aspnet-mvc", "aspnet-core.mvc", library="aspnet"),
                                             "upgrade aspnet-core.mvc", "upgrade"),
             "upgrade aspnet-core.mvc", ["expertise.aspnet-mvc"],
             '<- promoted on "aspnet-core.mvc"'),
            ("phrase with a slash", router_graph(expertise("expertise.delivery", "ci/cd pipeline yaml", library="ci"),
                                                 "ci/cd pipeline yaml", "pipeline"),
             "ci/cd pipeline yaml", ["expertise.delivery"],
             '<- promoted on "ci/cd pipeline yaml"'),
            ("first hitting piece", promotion_graph("pipeline yaml build definitions"),
             "pipeline yaml build definitions", ["expertise.ci-config"],
             '<- promoted on "pipeline yaml"'),
        ]
        for label, nodes, task, ids, suffix in rows:
            with self.subTest(row=label):
                out = self.plan(nodes, task)
                for nid in ids:
                    self.assertLoadSuffix(out, nid, suffix, task)

    def test_plan_partial_phrase_does_not_promote(self):
        """Asserts SPEC-0005 PLAN_PROMOTES_PHRASE_MATCHED_EXPERTISE.

        Guard: a hit is EVERY whole router token of the phrase. Rows: one word
        of a two-word phrase; half of the version token `net10.0` (the whole
        token does promote); a prefix fold (`migrating` -> `migration`).
        Words under three characters and stopwords are not tokens, so a task
        without them still hits."""
        net = router_graph(expertise("expertise.runtime-ten", "net10.0", library="runtime"),
                           "target net10 net10.0", "target")
        schema = router_graph(expertise("expertise.schema", "migration tooling", library="db"),
                              "migrating tooling", "tooling")
        # (label, nodes, task, node, expected): a suffix, "absent" from LOAD,
        # or "unpromoted" (in LOAD or not, but never promoted)
        rows = [
            ("one word of the phrase", promotion_graph(), "pipeline",
             "expertise.ci-config", "absent"),
            ("half a version token", net, "target net10",
             "expertise.runtime-ten", "unpromoted"),
            ("whole version token", net, "target net10.0",
             "expertise.runtime-ten", '<- promoted on "net10.0"'),
            ("prefix fold", schema, "migrating tooling", "expertise.schema", "absent"),
            ("short words", router_graph(expertise("expertise.golang", "go toolchain", library="go"),
                                         "toolchain upgrade", "toolchain"),
             "toolchain upgrade", "expertise.golang", '<- promoted on "go toolchain"'),
            ("stopwords", router_graph(expertise("expertise.shipping", "build and release", library="ci"),
                                       "release build", "release"),
             "release build", "expertise.shipping", '<- promoted on "build and release"'),
        ]
        for label, nodes, task, nid, expected in rows:
            with self.subTest(row=label):
                out = self.plan(nodes, task)
                if expected == "absent":
                    self.assertNotIn(nid, load_section(out),
                                     f"--plan {task!r} loaded {nid}:\n{out}")
                elif expected == "unpromoted":
                    self.assertNotIn("promoted on", load_section(out).get(nid, ""),
                                     f"--plan {task!r} promoted {nid}:\n{out}")
                else:
                    self.assertLoadSuffix(out, nid, expected, task)

    def test_plan_full_hit_on_non_expertise_stays_under_the_cut(self):
        """Asserts SPEC-0005 PLAN_PROMOTES_PHRASE_MATCHED_EXPERTISE.

        Guard. crosscut.release hits `pipeline yaml` in full but is not
        `kind: expertise`, so the entry budget binds it as before. Held by the
        mutant "drop the kind: expertise filter"."""
        out = self.plan(promotion_graph(), "pipeline yaml")
        self.assertNotIn("crosscut.release", load_section(out),
                         f"a non-expertise node outside the scored cut loaded:\n{out}")

    def test_plan_without_hit_or_path_is_unchanged(self):
        """Asserts SPEC-0005 PLAN_PROMOTES_PHRASE_MATCHED_EXPERTISE.

        Guard, golden over ID sets: with no phrase hit and no path-like token,
        LOAD and NOT LOADED are the sets the tool gave before promotion."""
        out = self.plan(promotion_graph(), "tune the pipeline runner")
        self.assertEqual(set(load_section(out)),
                         {"platform.pipeline", "stack.pipeline", "subsystem.pipeline"},
                         out)
        self.assertEqual(not_loaded_section(out), set(), out)


class InferenceTests(_PlanCase):

    def test_plan_infers_from_extension(self):
        """Asserts SPEC-0005 PLAN_INFERS_EXPERTISE_FROM_NAMED_FILES.

        Also asserts SPEC-0005 PATTERN_BRACE_SPLIT (the brace-tail row) and
        SPEC-0005 EXTENSIONLESS_BARE_NAME (the Dockerfile rows). A pattern
        with no `/` matches the path's last segment. Rows below name each
        edge; the negative rows infer (or promote) nothing."""
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
            # `*.{ts,tsx}` splits into `*.{ts` (matches nothing) and the
            # one-token phrase `tsx}`, so a .tsx path promotes on the tail
            ("brace-pattern tail", inference_graph(), "edit web/app.tsx",
             "expertise.frontend", '<- promoted on "tsx}"'),
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

        An error inside inference prints `  ! inference skipped: <class>`
        before LOAD, keeps the scored entries, and exits 0."""
        g = build_graph(self.tmp, inference_graph())
        r = plan_output(g, "edit infra/main.tf", prelude=_FAULT_IN_FNMATCH)
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 0,
                         f"an inference error changed the exit status:\n{out}")
        lines = r.stdout.splitlines()
        notice = next((i for i, l in enumerate(lines)
                       if l.startswith("  ! inference skipped: InjectedFault")), None)
        load = next((i for i, l in enumerate(lines) if l.startswith("LOAD (")), None)
        self.assertIsNotNone(notice, f"no inference-skipped notice:\n{out}")
        self.assertIsNotNone(load, out)
        self.assertLess(notice, load, f"the notice must precede LOAD:\n{out}")
        self.assertEqual(
            set(load_section(r.stdout)),
            {"platform.workbench", "stack.workbench", "subsystem.workbench"},
            f"the fallback is the scored entries alone:\n{out}")

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


class PromotedClosureTests(_PlanCase):
    TASK = "wire the metrics exporter into the sink"

    def test_plan_promoted_node_brings_required_parent(self):
        """Asserts SPEC-0005 PLAN_PROMOTED_NODE_TAKES_ITS_CLOSURE.

        `requires:` runs from a promoted entry as from any entry."""
        out = self.plan(router_graph(CLOSURE), self.TASK)
        self.assertLoadSuffix(out, "expertise.beta",
                              '<- promoted on "metrics exporter"', self.TASK)
        self.assertIn("expertise.alpha", load_section(out),
                      f"the promoted node's requires: parent did not load:\n{out}")

    def test_plan_promoted_node_descends_to_named_child(self):
        """Asserts SPEC-0005 PLAN_PROMOTED_NODE_TAKES_ITS_CLOSURE.

        `sink` is gamma's term but not a whole piece, so gamma arrives by
        descent from the promoted beta."""
        out = self.plan(router_graph(CLOSURE), self.TASK)
        self.assertLoadSuffix(out, "expertise.gamma",
                              '<- composed by expertise.beta on "sink"', self.TASK)

    def test_plan_seed_closure_is_accounted_before_promotion(self):
        """Asserts SPEC-0005 PLAN_PROMOTED_NODE_TAKES_ITS_CLOSURE.

        Guard: expertise.cache is reached by the scored seed's `requires:`
        and by descent from the promoted expertise.metrics. The scored closure
        is walked first, so cache prints no `composed by`."""
        task = "orders service metrics exporter flush"
        nodes = router_graph({
            **expertise("expertise.metrics", "metrics exporter", library="metrics",
                        composes=["expertise.cache"]),
            **expertise("expertise.cache", "flush interval, cache warmup",
                        library="metrics", requires=["expertise.metrics"]),
        }, task, name="orders")
        nodes["subsystem.orders"] = node_md("subsystem.orders", "subsystem",
                                            requires=["expertise.cache"], load_when=[task])
        out = self.plan(nodes, task)
        self.assertLoadSuffix(out, "expertise.metrics",
                              '<- promoted on "metrics exporter"', task)
        line = load_section(out).get("expertise.cache")
        self.assertIsNotNone(line, out)
        self.assertNotIn("composed by", line, line)


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
    """SPEC-0003 PLAN_ENTRY_NAMES_THE_NODE_FILE: each `--plan` entry line is
    `  <id>  <path from the plant root>  <text>`. One node lives at
    docs/graph/agents/04-tester.md, a path its id does not spell."""

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
                    load_when=["widget ledger tests"]), encoding="utf-8")
        with (graph / "index.md").open("a", encoding="utf-8") as f:
            f.write("- agent.tester\n")
        files = {
            "root": "docs/graph/nodes/root.md",
            "subsystem.alpha": "docs/graph/nodes/subsystem.alpha.md",
            "subsystem.beta": "docs/graph/nodes/subsystem.beta.md",
            "agent.tester": "docs/graph/agents/04-tester.md",
        }
        titles = {nid: f"{nid} node" for nid in files}
        return plant, files, titles

    def test_plan_entry_names_the_node_file(self):
        """PLAN_ENTRY_NAMES_THE_NODE_FILE: every entry names its node file."""
        plant, files, titles = self._plant()
        r = subprocess.run([sys.executable, "docs/graph/graph-lint.py", "--plan", self.TASK],
                           cwd=str(plant), capture_output=True, text=True, timeout=120)
        out = r.stdout
        self.assertEqual(r.returncode, 0, f"--plan exited {r.returncode}:\n{out}\n{r.stderr}")
        sections = {"LOAD": plan_section(out, "LOAD ("),
                    "NOT LOADED": plan_section(out, "NOT LOADED (")}
        self.assertEqual(sorted(sections["LOAD"]), ["agent.tester", "root", "subsystem.alpha"],
                         f"harness: the fixture no longer routes as measured:\n{out}")
        self.assertEqual(list(sections["NOT LOADED"]), ["subsystem.beta"],
                         f"harness: the fixture no longer routes as measured:\n{out}")
        for section, entries in sections.items():
            for nid, line in entries.items():
                with self.subTest(line=line):
                    m = re.match(r"^  (\S+)\s+(\S+)\s+(\S.*)$", line)
                    self.assertIsNotNone(m, f"{line!r} is not `  <id>  <path>  <text>`")
                    self.assertEqual(m.group(2), files[nid], line)
                    text = titles[nid] if section == "LOAD" else "peer of subsystem.alpha"
                    self.assertTrue(m.group(3).startswith(text), line)


if __name__ == "__main__":
    unittest.main(verbosity=2)
