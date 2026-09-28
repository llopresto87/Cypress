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


def run_lint(graph_dir: Path, *args: str) -> subprocess.CompletedProcess:
    """Run graph-lint.py against a copy of itself sitting inside graph_dir
    (mirrors the real install, where the tool lives next to index.md/nodes/).
    Extra `args` are passed through, so a caller can exercise a flag."""
    return subprocess.run(
        [sys.executable, str(graph_dir / "graph-lint.py"), *args],
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


class StagedAdoptionTests(unittest.TestCase):
    """A machinery upgrade can install a check the plant has never run, and a
    plant that was green the day before goes red on work nobody has asked it
    for. `--warn` is the staged window: the same findings, printed in full,
    with the exit code held back. The failure this guards against is a quieter
    CHECK being used where a staged EXIT was meant — so both halves are
    asserted, and the findings must be identical between the two modes."""

    def setUp(self):
        self.assertTrue(GRAPH_LINT.exists(), f"missing tool: {GRAPH_LINT}")
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def _unregistered(self) -> Path:
        """A template-shaped library page with no row in the index: the check
        this harvest installed, and the one most likely to be newly red."""
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
        self.assertRegex(out, r"expertise\.serilog\s+\S+\s+composed by .*no task term")

    def test_plan_descent_never_folds(self):
        """Asserts SPEC-0005 DESCENT_TEST_NOW_SEEDS_THE_CHILD.

        Seeding folds prefixes; descent does not. `migrating` is a
        six-character prefix of the child's `migration`, and must not compose
        it — otherwise "migrating the CI runner" drags in schema knowledge.

        The task names `dbcontext`, a WHOLE piece of
        ef-core's `load_when`, which SPEC-0005 promotes on, so ef-core would
        arrive promoted rather than composed. `mapping` is not a whole piece
        (`entity mapping` needs `entity` too), so ef-core is still selected by
        descent and the fold assertion keeps a descended parent."""
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
            "in the orders service, fix the mapping, migrating the runner",
            nodes)
        self.assertIn('composed by expertise.dotnet on "mapping"', out)
        self.assertRegex(out, r"expertise\.ef-migrations\s+\S+\s+composed by .*no task term")

    def test_plan_descends_two_levels_each_on_own_term(self):
        """Asserts SPEC-0005 DESCENT_TEST_NOW_SEEDS_THE_CHILD.

        Recursion falls out of the rule: the child becomes the parent for
        its own children, and each level needs its own specific term.

        `dbcontext` is a whole piece SPEC-0005
        promotes on; the first level descends on `mapping`, which is not."""
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
            "in the orders service, fix the mapping, run the script",
            nodes)
        self.assertIn('composed by expertise.dotnet on "mapping"', out)
        self.assertIn('composed by expertise.ef-core on "script"', out)

    def test_plan_selects_major_by_tfm_token(self):
        """Asserts SPEC-0005 DESCENT_TEST_NOW_SEEDS_THE_CHILD.

        Two majors in play: the unversioned parent composes one child per
        major, and the target-framework token the developer types picks it.

        The task names the subsystem's path glob deliberately. Without it the
        pre-7.5.0 tool SEEDS `expertise.dotnet-10` on this fixture (measured),
        and the assertion below would pass with descent deleted.

        By the `promoted on` arm, `net10.0` is a
        whole piece of dotnet-10's `load_when`, and the child's only own
        standalone term is that token, so no task term can select the major by
        descent without also being a whole piece. The case still asserts the
        major the TFM token selected, now by promotion; dotnet-8 stays out."""
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
        tfm = "net10.0"
        out = self.plan(
            f"in the orders service, editing src/Orders/**, target {tfm}", nodes)
        # The matched term is the WHOLE TFM token. dotnet-10 is an entry here,
        # promoted (SPEC-0005 §6 "Trigger phrase"), so it prints no
        # `composed by`. Its piece `net10.0` is one whole router token, so
        # the suffix naming that piece names the term the task
        # matched, and it must equal the token the task wrote. Half of it
        # (`net10`) selects nothing: that is
        # PromotionTests.test_plan_partial_version_token_does_not_promote.
        line = load_section(out).get("expertise.dotnet-10")
        self.assertIsNotNone(line, f"the TFM token did not select dotnet-10:\n{out}")
        self.assertTrue(line.rstrip().endswith(f'<- promoted on "{tfm}"'),
                        f"dotnet-10 must load promoted on the whole TFM token "
                        f"{tfm!r} the task wrote:\n  {line}")
        self.assertRegex(out, r"expertise\.dotnet-8\s+\S+\s+composed by .*no task term")

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
        """Asserts SPEC-0005 DESCENT_TEST_NOW_SEEDS_THE_CHILD.

        A parent handing over most of a real menu at once says the task or
        the triggers are too generic, and the notice is what makes that
        visible instead of merely expensive. A single-child parent must NOT
        trip it — that is an ordinary descent, not a symptom.

        The task names `retry policy`, a whole piece
        of polly's `load_when` that SPEC-0005 promotes on. `breaker` is polly's
        own term and not a whole piece (`circuit breaker`), so all three
        children are still selected by descent and the count keeps its
        meaning."""
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
                        "breaker", nodes)
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
# SPEC-0005-cycle-economy (docs/specs/), increments 1 and 2 — RED.
#
# Contract map:
#   PromotionTests        -> PLAN_PROMOTES_PHRASE_MATCHED_EXPERTISE and
#                            PROMOTION_FLOODS_LOAD: an expertise node whose
#                            whole trigger PHRASE the task names loads beside
#                            the scored top-3 cut, with a `promoted on` suffix.
#   InferenceTests        -> PLAN_INFERS_EXPERTISE_FROM_NAMED_FILES and its
#                            failure modes (HOSTILE_TASK_LINE,
#                            TASK_LINE_WITHOUT_PATHS, PATTERN_BRACE_SPLIT,
#                            EXTENSIONLESS_BARE_NAME): a path-like task token
#                            matching a `load_when` FILE PATTERN infers the
#                            expertise node, by string matching only.
#   PromotedClosureTests  -> PLAN_PROMOTED_NODE_TAKES_ITS_CLOSURE: requires
#                            and descent run from promoted entries; the §6
#                            suffix precedence.
#   ListedNodeEdgesTests  -> LISTED_NODE_EDGES_REACH, SIBLING_UNREACHABLE_
#                            AFTER_GRAFT, ORPHAN_ISLAND.
#   DelegationRoutingTests-> DELEGATION_LEAVES_ROUTE on a fresh install.
#
# Every method's first docstring line is `Asserts SPEC-0005 <SLUG>.` — the
# form spec-lint credits (SPEC-0005 §10 preamble). A case marked "guard"
# passes on the unmodified tool and is held by a named mutant (plan §10),
# not by an observed red.
#
# Every fixture is measured on the UNMODIFIED tool (graph-lint.py as of
# harvest/7.30.0 0613d09): the expertise node a positive case asserts on is
# NOT in LOAD there, so the case can only pass through promotion or
# inference, never through the scored cut. Each fixture's docstring records
# the measurement.
# ==========================================================================


def plan_output(graph: Path, task: str, *, tool: Path | None = None,
                prelude: str | None = None) -> subprocess.CompletedProcess:
    """Run `--plan TASK` against `graph`. `prelude`, when given, is Python run
    in the same interpreter BEFORE the tool (via runpy) — the only way a
    black-box CLI case can plant a fault inside the tool's own call path."""
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

# SPEC-0005 §6 pins the match to `fnmatch.fnmatchcase(path, pattern.lower())`.
# Replacing it with a raiser is therefore a fault INSIDE inference, reached on
# any task with a path-like token and a file pattern in the graph, and nowhere
# else in `--plan` (the unmodified tool never calls it: measured, this prelude
# leaves its output byte-identical).
_FAULT_TEMPLATE = """
import fnmatch as _fnmatch
class {name}({base}):
    pass
def _raise(*_a, **_k):
    raise {name}("planted by test_graph_lint")
_fnmatch.fnmatchcase = _raise
"""
_FAULT_IN_FNMATCH = _FAULT_TEMPLATE.format(name="InjectedFault", base="RuntimeError")
# A handler narrowed to `except RuntimeError` still
# catches the fault above. This one derives from Exception directly, so only a
# handler as broad as §6 requires ("never raise on any str task") catches it.
_PLAIN_FAULT_IN_FNMATCH = _FAULT_TEMPLATE.format(name="InjectedPlainFault",
                                                 base="Exception")


def load_section(out: str) -> dict:
    """{node id: the whole LOAD line} — the LOAD section only."""
    lines, on = {}, False
    for line in out.splitlines():
        if line.startswith("LOAD ("):
            on = True
            continue
        if on:
            if not line.startswith("  "):
                break
            lines[line.split()[0]] = line
    return lines


def not_loaded_section(out: str) -> set:
    ids, on = set(), False
    for line in out.splitlines():
        if line.startswith("NOT LOADED"):
            on = True
            continue
        if on and line.startswith("  "):
            ids.add(line.split()[0])
    return ids


class _PlanCase(unittest.TestCase):
    """Shared set-up and the one assertion shape every positive case uses:
    the suffix on the node's OWN LOAD line, never bare membership."""

    def setUp(self):
        self.assertTrue(GRAPH_LINT.exists(), f"missing tool: {GRAPH_LINT}")
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

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


# --------------------------------------------------------------------------
# Promotion
# --------------------------------------------------------------------------

def promotion_graph() -> dict:
    """Three non-expertise nodes NAMED `pipeline` whose trigger is the phrase
    `pipeline yaml`, one more non-expertise node carrying the same phrase
    under a neutral name, and the expertise node whose FIRST piece is
    `pipeline yaml` under a neutral name.

    Measured on the unmodified tool, task "pipeline yaml": LOAD is exactly
    platform.pipeline, stack.pipeline and subsystem.pipeline (the name doubles
    their `pipeline` hit, so they take the top-three cut); expertise.ci-config
    and crosscut.release are out."""
    return {
        "root": node_md("root", "root", requires=["subsystem.pipeline"],
                        owns=["root.map"]),
        "subsystem.pipeline": node_md("subsystem.pipeline", "subsystem",
                                      load_when=["pipeline yaml"]),
        "stack.pipeline": node_md("stack.pipeline", "stack",
                                  load_when=["pipeline yaml"]),
        "platform.pipeline": node_md("platform.pipeline", "platform",
                                     load_when=["pipeline yaml"]),
        "crosscut.release": node_md("crosscut.release", "crosscut",
                                    load_when=["pipeline yaml"]),
        "expertise.ci-config": node_md(
            "expertise.ci-config", "expertise", libraries=["ci"],
            load_when=["pipeline yaml, build definitions"]),
    }


class PromotionTests(_PlanCase):

    def test_plan_promotes_expertise_past_the_scored_cut(self):
        """Asserts SPEC-0005 PLAN_PROMOTES_PHRASE_MATCHED_EXPERTISE.

        The Then: the expertise node the scored cut leaves out (measured, see
        `promotion_graph`) loads with `<- promoted on "pipeline yaml"`."""
        out = self.plan(promotion_graph(), "pipeline yaml")
        self.assertLoadSuffix(out, "expertise.ci-config",
                              '<- promoted on "pipeline yaml"', "pipeline yaml")

    def test_plan_partial_phrase_does_not_promote(self):
        """Asserts SPEC-0005 PLAN_PROMOTES_PHRASE_MATCHED_EXPERTISE.

        Guard. A hit is EVERY token of the phrase; one word of `pipeline yaml`
        is not one. Measured on the unmodified tool, task "pipeline": the three
        pipeline-named nodes take the cut and expertise.ci-config is out. Held
        by the mutant "any token instead of every token"."""
        task = "pipeline"
        out = self.plan(promotion_graph(), task)
        self.assertNotIn("expertise.ci-config", load_section(out),
                         f"--plan {task!r} names one word of a two-word "
                         f"phrase and still loaded the node:\n{out}")

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

        Guard, golden over ID sets. No phrase hit and no path-like token:
        LOAD and NOT LOADED are the sets the unmodified tool gives on this
        fixture (captured from it, 0613d09). The existing
        DescentTests.test_plan_without_composes_is_unchanged holds the
        composes-free golden alongside."""
        out = self.plan(promotion_graph(), "tune the pipeline runner")
        self.assertEqual(set(load_section(out)),
                         {"platform.pipeline", "stack.pipeline", "subsystem.pipeline"},
                         out)
        self.assertEqual(not_loaded_section(out), set(), out)

    def test_plan_promotes_one_word_phrase_uncapped(self):
        """Asserts SPEC-0005 PROMOTION_FLOODS_LOAD.

        Five expertise nodes share the one-word phrase `python`; three
        non-expertise nodes named `python` outscore every one of them.
        Measured on the unmodified tool, task "python tooling": LOAD is the
        three decoys, none of the five. The owner's decision is
        that every hit loads, uncapped."""
        nodes = {
            "root": node_md("root", "root", requires=["subsystem.python"],
                            owns=["root.map"]),
            "subsystem.python": node_md("subsystem.python", "subsystem",
                                        load_when=["python tooling"]),
            "stack.python": node_md("stack.python", "stack",
                                    load_when=["python tooling"]),
            "platform.python": node_md("platform.python", "platform",
                                       load_when=["python tooling"]),
        }
        langs = [f"expertise.lang-{c}" for c in "abcde"]
        for nid in langs:
            nodes[nid] = node_md(nid, "expertise", libraries=["python"],
                                 load_when=["python"])
        out = self.plan(nodes, "python tooling")
        for nid in langs:
            with self.subTest(node=nid):
                self.assertLoadSuffix(out, nid, '<- promoted on "python"',
                                      "python tooling")

    # ---- RED and survivor guards --------

    def test_plan_partial_version_token_does_not_promote(self):
        """Asserts SPEC-0005 PLAN_PROMOTES_PHRASE_MATCHED_EXPERTISE.

        A phrase's tokens are the
        router's WHOLE tokens (§6 "Trigger phrase", v0.6), so `net10.0` is one
        token and a task must name all of it. `target net10` names half of it
        and must not promote; `target net10.0` names it whole and does. Decoys
        named `target` over `target net10 net10.0` take the scored cut on both
        tasks."""
        extra = {"expertise.runtime-ten": node_md(
            "expertise.runtime-ten", "expertise", libraries=["runtime"],
            load_when=["net10.0"])}
        nodes = guard_graph(extra, "target net10 net10.0", name="target")
        with self.subTest(task="target net10"):
            out = self.plan(nodes, "target net10")
            line = load_section(out).get("expertise.runtime-ten", "")
            self.assertNotIn(
                "promoted on", line,
                f"half of the version token `net10.0` promoted the node:\n{out}")
        with self.subTest(task="target net10.0"):
            self.assertLoadSuffix(self.plan(nodes, "target net10.0"),
                                  "expertise.runtime-ten",
                                  '<- promoted on "net10.0"', "target net10.0")

    def test_plan_dotted_compound_named_whole_promotes(self):
        """Asserts SPEC-0005 PLAN_PROMOTES_PHRASE_MATCHED_EXPERTISE.

        Guard: the positive twin of the partial-
        version case. `aspnet-core.mvc` is one whole token, and a task naming
        all of it promotes the node. The router never forms the mid-level
        compound `aspnet-core` from the task word, so a rule that also demands
        the phrase's fragments or dotted segments loses this promotion."""
        extra = {"expertise.aspnet-mvc": node_md(
            "expertise.aspnet-mvc", "expertise", libraries=["aspnet"],
            load_when=["aspnet-core.mvc"])}
        task = "upgrade aspnet-core.mvc"
        out = self.plan(guard_graph(extra, task, name="upgrade"), task)
        self.assertLoadSuffix(out, "expertise.aspnet-mvc",
                              '<- promoted on "aspnet-core.mvc"', task)

    def test_plan_phrase_with_a_slash_still_promotes(self):
        """Asserts SPEC-0005 PLAN_PROMOTES_PHRASE_MATCHED_EXPERTISE.

        Guard: a piece holding `/` but also whitespace is a
        phrase, not a pattern: whitespace disqualifies a pattern."""
        extra = {"expertise.delivery": node_md(
            "expertise.delivery", "expertise", libraries=["ci"],
            load_when=["ci/cd pipeline yaml"])}
        task = "ci/cd pipeline yaml"
        out = self.plan(guard_graph(extra, "ci/cd pipeline yaml", name="pipeline"),
                        task)
        self.assertLoadSuffix(out, "expertise.delivery",
                              '<- promoted on "ci/cd pipeline yaml"', task)

    def test_plan_promotion_reports_first_hitting_piece(self):
        """Asserts SPEC-0005 PLAN_PROMOTES_PHRASE_MATCHED_EXPERTISE.

        Guard: the task hits both of ci-config's pieces; the
        suffix names the first in `load_when` order. The pipeline-named
        decoys also carry `build definitions`, so ci-config stays outside
        the scored cut."""
        nodes = promotion_graph()
        for nid in ("subsystem.pipeline", "stack.pipeline", "platform.pipeline"):
            kind = nid.split(".")[0]
            nodes[nid] = node_md(nid, kind,
                                 load_when=["pipeline yaml build definitions"])
        task = "pipeline yaml build definitions"
        self.assertLoadSuffix(self.plan(nodes, task), "expertise.ci-config",
                              '<- promoted on "pipeline yaml"', task)

    def test_plan_short_words_are_not_phrase_tokens(self):
        """Asserts SPEC-0005 PLAN_PROMOTES_PHRASE_MATCHED_EXPERTISE.

        Guard: `go` is under three characters, so it is not a
        token of `go toolchain`, and a task naming only `toolchain` hits."""
        extra = {"expertise.golang": node_md(
            "expertise.golang", "expertise", libraries=["go"],
            load_when=["go toolchain"])}
        task = "toolchain upgrade"
        out = self.plan(guard_graph(extra, "toolchain upgrade", name="toolchain"),
                        task)
        self.assertLoadSuffix(out, "expertise.golang",
                              '<- promoted on "go toolchain"', task)

    def test_plan_stopwords_are_not_phrase_tokens(self):
        """Asserts SPEC-0005 PLAN_PROMOTES_PHRASE_MATCHED_EXPERTISE.

        Guard: `and` is in STOPWORDS, so it is not a token of
        `build and release`; a task naming `release build` hits."""
        extra = {"expertise.shipping": node_md(
            "expertise.shipping", "expertise", libraries=["ci"],
            load_when=["build and release"])}
        task = "release build"
        out = self.plan(guard_graph(extra, "release build", name="release"), task)
        self.assertLoadSuffix(out, "expertise.shipping",
                              '<- promoted on "build and release"', task)

    def test_plan_prefix_fold_does_not_promote(self):
        """Asserts SPEC-0005 PLAN_PROMOTES_PHRASE_MATCHED_EXPERTISE.

        Guard, note N1. `migrating` reaches `migration` only by the six-letter
        prefix fold (strength 1), which is not a hit."""
        extra = {"expertise.schema": node_md(
            "expertise.schema", "expertise", libraries=["db"],
            load_when=["migration tooling"])}
        task = "migrating tooling"
        out = self.plan(guard_graph(extra, "migrating tooling", name="tooling"),
                        task)
        self.assertNotIn("expertise.schema", load_section(out),
                         f"a prefix fold promoted the node:\n{out}")


# --------------------------------------------------------------------------
# Inference
# --------------------------------------------------------------------------

DECOY_VOCABULARY = ("edit bump update web infra main app package json lock tsx "
                    "dockerfile docker terraform output deploy otel yaml wire "
                    "metrics exporter sink")


def decoys(vocabulary: str = DECOY_VOCABULARY, name: str = "workbench") -> dict:
    """Three non-expertise nodes carrying, as whole words, every word the
    inference and closure tasks use. They take the whole scored cut on each
    of those tasks, so an expertise node can load only by promotion or
    inference — a positive case can never pass through the score.
    `vocabulary` and `name` let a fix-batch case supply its own words; a
    `name` the task also uses doubles the decoys' score on it."""
    return {
        f"{kind}.{name}": node_md(f"{kind}.{name}", kind,
                                  load_when=[vocabulary])
        for kind in ("subsystem", "stack", "platform")
    }


def guard_graph(extra: dict, vocabulary: str = DECOY_VOCABULARY,
                name: str = "workbench") -> dict:
    """A root, three decoys over `vocabulary`, and the `extra` nodes."""
    nodes = {"root": node_md("root", "root", requires=[f"subsystem.{name}"],
                             owns=["root.map"])}
    nodes.update(decoys(vocabulary, name))
    nodes.update(extra)
    return nodes


def inference_graph() -> dict:
    """The decoys plus four expertise nodes whose `load_when` holds FILE
    PATTERNS only (SPEC-0005 §4 Given, and the §7 brace and Dockerfile rows).

    Measured on the unmodified tool: on every task these cases run, LOAD is
    the three decoys and none of the four expertise nodes."""
    nodes = {"root": node_md("root", "root", requires=["subsystem.workbench"],
                             owns=["root.map"])}
    nodes.update(decoys())
    nodes.update({
        "expertise.terraform": node_md(
            "expertise.terraform", "expertise", libraries=["terraform"],
            load_when=["*.tf, **/.terraform.lock.hcl"]),
        "expertise.node-js": node_md(
            "expertise.node-js", "expertise", libraries=["node"],
            load_when=["**/package.json, **/package-lock.json"]),
        "expertise.containers": node_md(
            "expertise.containers", "expertise", libraries=["containers"],
            load_when=["**/Dockerfile"]),
        "expertise.frontend": node_md(
            "expertise.frontend", "expertise", libraries=["frontend"],
            load_when=["*.{ts,tsx}"]),
    })
    return nodes


def inferred_lines(out: str) -> dict:
    return {nid: line for nid, line in load_section(out).items()
            if "inferred from" in line}


class InferenceTests(_PlanCase):

    def test_plan_infers_from_extension(self):
        """Asserts SPEC-0005 PLAN_INFERS_EXPERTISE_FROM_NAMED_FILES.

        A pattern with no `/` matches the path's last segment."""
        task = "edit infra/main.tf"
        out = self.plan(inference_graph(), task)
        self.assertLoadSuffix(out, "expertise.terraform",
                              '<- inferred from "infra/main.tf" via "*.tf"', task)

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

    def test_plan_infers_from_bare_manifest(self):
        """Asserts SPEC-0005 PLAN_INFERS_EXPERTISE_FROM_NAMED_FILES.

        `package.json` has no `/` but has an extension, so it is path-like,
        and matches `**/package.json` through the bare-p arm."""
        task = "bump package.json"
        out = self.plan(inference_graph(), task)
        self.assertLoadSuffix(
            out, "expertise.node-js",
            '<- inferred from "package.json" via "**/package.json"', task)

    def test_plan_inferred_path_echo_is_normalized_and_sanitized(self):
        """Asserts SPEC-0005 PLAN_INFERS_EXPERTISE_FROM_NAMED_FILES.

        The Then's `<path>` is the token after §6 stripping and normalization
        (lowercase, one leading `./` removed) and echo sanitizing (cut to 80
        characters plus `…`, anything outside `[a-z0-9_./~+-]` shown as `?`).
        Not a separate §10 row before this spawn; added to §10 in the handback."""
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

    def test_plan_pattern_text_as_words_does_not_promote(self):
        """Asserts SPEC-0005 PLAN_INFERS_EXPERTISE_FROM_NAMED_FILES.

        Guard. A file pattern is never a trigger phrase: a task repeating the
        words of `**/package-lock.json` and `**/.terraform.lock.hcl` promotes
        nothing. Held by the mutant "classify a file pattern as a phrase"."""
        task = "update the package lock json and the terraform lock hcl"
        out = self.plan(inference_graph(), task)
        self.assertNotIn("promoted on", out,
                         f"a file pattern's words promoted a node:\n{out}")

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

        Three outcomes of one failure mode, one subTest each:
        - the token cap: of the path-like tokens, only the first 64 are
          considered — the 64th still infers, the 65th does not;
        - the length skip: a token over 256 characters is skipped, and the
          next path-like token is the one that infers and is echoed;
        - an error inside inference (a raising `fnmatch.fnmatchcase`, planted
          by `_FAULT_IN_FNMATCH`) prints `  ! inference skipped: <class>`
          before LOAD, keeps the scored entries, and exits 0. Two fault
          classes: one under RuntimeError and one directly under Exception,
          so a narrowed handler is caught."""
        junk = [f"a/b{i}" for i in range(64)]
        with self.subTest(case="64th path-like token is considered"):
            task = " ".join(junk[:63] + ["infra/main.tf"])
            out = self.plan(inference_graph(), task)
            self.assertLoadSuffix(out, "expertise.terraform",
                                  '<- inferred from "infra/main.tf" via "*.tf"',
                                  "63 junk paths + infra/main.tf")
        with self.subTest(case="65th path-like token is not"):
            task = " ".join(junk + ["infra/main.tf"])
            out = self.plan(inference_graph(), task)
            self.assertEqual(inferred_lines(out), {},
                             f"a path-like token past the first 64 inferred:\n{out}")
        with self.subTest(case="token over 256 characters is skipped"):
            task = "edit " + "x" * 300 + ".tf infra/main.tf"
            out = self.plan(inference_graph(), task)
            self.assertLoadSuffix(out, "expertise.terraform",
                                  '<- inferred from "infra/main.tf" via "*.tf"',
                                  "a 303-character .tf token, then infra/main.tf")
        for fault, prelude in (("InjectedFault", _FAULT_IN_FNMATCH),
                               ("InjectedPlainFault", _PLAIN_FAULT_IN_FNMATCH)):
          with self.subTest(case=f"an error inside inference ({fault})"):
            g = build_graph(self.tmp, inference_graph())
            r = plan_output(g, "edit infra/main.tf", prelude=prelude)
            out = r.stdout + r.stderr
            self.assertEqual(r.returncode, 0,
                             f"an inference error changed the exit status:\n{out}")
            lines = r.stdout.splitlines()
            notice = next((i for i, l in enumerate(lines)
                           if l.startswith("  ! inference skipped: ")), None)
            load = next((i for i, l in enumerate(lines) if l.startswith("LOAD (")), None)
            self.assertIsNotNone(
                notice, f"no '  ! inference skipped: <exception class>' line "
                        f"after a fault inside inference:\n{out}")
            self.assertIn(fault, lines[notice], lines[notice])
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

    def test_plan_brace_pattern_tail_promotes(self):
        """Asserts SPEC-0005 PATTERN_BRACE_SPLIT.

        `*.{ts,tsx}` splits at the comma into `*.{ts` (a
        pattern that matches nothing) and `tsx}` (a one-token phrase). A task
        naming a `.tsx` path therefore PROMOTES the node on the tail piece;
        promotion outranks inference in the suffix, and the head piece infers
        nothing to outrank."""
        task = "edit web/app.tsx"
        out = self.plan(inference_graph(), task)
        self.assertLoadSuffix(out, "expertise.frontend",
                              '<- promoted on "tsx}"', task)

    def test_plan_bare_dockerfile_infers_nothing(self):
        """Asserts SPEC-0005 EXTENSIONLESS_BARE_NAME.

        Guard. `Dockerfile` with no directory is not path-like. Held by the
        mutant "treat a bare extensionless name as path-like"."""
        out = self.plan(inference_graph(), "edit Dockerfile")
        self.assertEqual(inferred_lines(out), {}, out)

    def test_plan_dotted_dockerfile_infers(self):
        """Asserts SPEC-0005 EXTENSIONLESS_BARE_NAME.

        Written with a directory it is path-like: `./Dockerfile` normalizes to
        `dockerfile` and `docker/Dockerfile` to `docker/dockerfile`; both
        match `**/Dockerfile`, echoed as written."""
        for task, echoed in (("edit ./Dockerfile", "dockerfile"),
                             ("edit docker/Dockerfile", "docker/dockerfile")):
            with self.subTest(task=task):
                out = self.plan(inference_graph(), task)
                self.assertLoadSuffix(
                    out, "expertise.containers",
                    f'<- inferred from "{echoed}" via "**/Dockerfile"', task)

    # ---- survivor guards -------------------

    def test_plan_task_wildcard_never_matches_a_slash_pattern(self):
        """Asserts SPEC-0005 PLAN_INFERS_EXPERTISE_FROM_NAMED_FILES.

        Guard: the pattern `ci/pipeline.yml` keeps its `/`
        and reaches the whole-path arm; the task token `ci/*` is the NAME
        there, never the pattern, so it matches nothing."""
        extra = {"expertise.ci": node_md(
            "expertise.ci", "expertise", libraries=["ci"],
            load_when=["ci/pipeline.yml"])}
        out = self.plan(guard_graph(extra), "edit ci/*")
        self.assertEqual(inferred_lines(out), {},
                         f"task text was used as a pattern on the whole-path arm:\n{out}")

    def test_plan_infers_through_a_slash_pattern(self):
        """Asserts SPEC-0005 PLAN_INFERS_EXPERTISE_FROM_NAMED_FILES.

        Guard, the positive companion: `infra/*.tf` matches the
        whole path `infra/main.tf`."""
        extra = {"expertise.infra": node_md(
            "expertise.infra", "expertise", libraries=["terraform"],
            load_when=["infra/*.tf"])}
        task = "edit infra/main.tf"
        self.assertLoadSuffix(self.plan(guard_graph(extra), task), "expertise.infra",
                              '<- inferred from "infra/main.tf" via "infra/*.tf"', task)

    def test_plan_infers_literal_name_pattern_in_a_subdirectory(self):
        """Asserts SPEC-0005 PLAN_INFERS_EXPERTISE_FROM_NAMED_FILES.

        Guard: a pattern with no `/` matches the path's LAST
        SEGMENT, so a pattern that begins with a literal file name matches it
        in any directory; matched against the whole path it would not.

        The bare piece `requirements.txt` would not serve: under §6 a piece
        with neither `*` nor `/` is a trigger PHRASE (measured: it promotes),
        so the pattern here is `requirements*.txt`."""
        extra = {"expertise.pydeps": node_md(
            "expertise.pydeps", "expertise", libraries=["python"],
            load_when=["requirements*.txt"])}
        task = "bump svc/requirements.txt"
        out = self.plan(guard_graph(extra, DECOY_VOCABULARY + " svc requirements txt"),
                        task)
        self.assertLoadSuffix(
            out, "expertise.pydeps",
            '<- inferred from "svc/requirements.txt" via "requirements*.txt"', task)

    def test_plan_slash_piece_without_star_is_a_pattern(self):
        """Asserts SPEC-0005 PLAN_INFERS_EXPERTISE_FROM_NAMED_FILES.

        Guard: `/` alone marks a pattern: `ci/pipelines.yml`
        holds no `*` and is still a pattern, so the node is inferred, not
        promoted."""
        extra = {"expertise.ci": node_md(
            "expertise.ci", "expertise", libraries=["ci"],
            load_when=["ci/pipelines.yml"])}
        task = "edit ci/pipelines.yml"
        out = self.plan(guard_graph(extra, "edit ci/pipelines.yml pipelines yml",
                                    name="pipelines"), task)
        self.assertLoadSuffix(
            out, "expertise.ci",
            '<- inferred from "ci/pipelines.yml" via "ci/pipelines.yml"', task)

    def test_plan_inference_reports_first_path_in_task_order(self):
        """Asserts SPEC-0005 PLAN_INFERS_EXPERTISE_FROM_NAMED_FILES.

        Guard: two task paths match two of terraform's
        patterns; the suffix names the first PATH in task order, then its
        first matching pattern."""
        task = "edit .terraform.lock.hcl infra/main.tf"
        self.assertLoadSuffix(
            self.plan(inference_graph(), task), "expertise.terraform",
            '<- inferred from ".terraform.lock.hcl" via "**/.terraform.lock.hcl"',
            task)

    def test_plan_backslash_only_token_is_not_path_like(self):
        """Asserts SPEC-0005 PLAN_INFERS_EXPERTISE_FROM_NAMED_FILES.

        Guard: the path-like test runs on the stripped
        token before normalization, and `\\` is outside the extension form,
        so `infra\\main.tf` is not path-like and infers nothing."""
        out = self.plan(inference_graph(), "edit infra\\main.tf")
        self.assertEqual(inferred_lines(out), {}, out)

    def test_plan_long_token_flood_does_not_use_the_cap(self):
        """Asserts SPEC-0005 HOSTILE_TASK_LINE.

        Guard: over-long tokens are skipped BEFORE the
        count, so 64 of them cannot use the cap up."""
        task = " ".join(["x" * 300 + ".tf"] * 64 + ["infra/main.tf"])
        self.assertLoadSuffix(self.plan(inference_graph(), task),
                              "expertise.terraform",
                              '<- inferred from "infra/main.tf" via "*.tf"',
                              "64 over-long .tf tokens, then infra/main.tf")

    def test_plan_cap_counts_only_path_like_tokens(self):
        """Asserts SPEC-0005 HOSTILE_TASK_LINE.

        Guard: the cap is 64 PATH-LIKE tokens; 70 plain words
        before the path do not count against it."""
        task = " ".join([f"word{i}" for i in range(70)] + ["infra/main.tf"])
        self.assertLoadSuffix(self.plan(inference_graph(), task),
                              "expertise.terraform",
                              '<- inferred from "infra/main.tf" via "*.tf"',
                              "70 plain words, then infra/main.tf")

    def test_plan_token_of_exactly_256_is_considered(self):
        """Asserts SPEC-0005 HOSTILE_TASK_LINE.

        Guard: the skip is for tokens LONGER than 256: one of
        exactly 256 characters is considered, one of 257 is not."""
        for length, inferred in ((256, True), (257, False)):
            token = "x" * (length - 3) + ".tf"
            self.assertEqual(len(token), length)
            with self.subTest(length=length):
                out = self.plan(inference_graph(), f"edit {token}")
                self.assertEqual(
                    "expertise.terraform" in inferred_lines(out), inferred,
                    f"a {length}-character token: expected inferred={inferred}:\n{out}")


# --------------------------------------------------------------------------
# Promoted closure
# --------------------------------------------------------------------------

def closure_graph(with_decoys: bool = True) -> dict:
    """expertise.alpha composes expertise.beta; expertise.beta requires alpha,
    composes expertise.gamma, and carries the phrase `metrics exporter` and
    the pattern `**/otel.yaml`; gamma's pieces are `structured logging` and
    `log sink`.

    Measured on the unmodified tool with the decoys, task "wire the metrics
    exporter into the sink": LOAD is the three decoys; alpha, beta and gamma
    are all out. Without the decoys, task "metrics exporter": beta is the top
    scored entry and alpha loads by requires."""
    nodes = {"root": node_md("root", "root", requires=["expertise.alpha"],
                             owns=["root.map"])}
    if with_decoys:
        nodes.update(decoys())
    nodes.update({
        "expertise.alpha": node_md(
            "expertise.alpha", "expertise", composes=["expertise.beta"],
            libraries=["alpha"], load_when=["runtime platform"]),
        "expertise.beta": node_md(
            "expertise.beta", "expertise", requires=["expertise.alpha"],
            composes=["expertise.gamma"], libraries=["alpha"],
            load_when=["metrics exporter, **/otel.yaml"]),
        "expertise.gamma": node_md(
            "expertise.gamma", "expertise", requires=["expertise.beta"],
            libraries=["alpha"], load_when=["structured logging, log sink"]),
    })
    return nodes


class PromotedClosureTests(_PlanCase):
    TASK = "wire the metrics exporter into the sink"

    def test_plan_promoted_node_brings_required_parent(self):
        """Asserts SPEC-0005 PLAN_PROMOTED_NODE_TAKES_ITS_CLOSURE.

        `requires:` runs from a promoted entry as from any entry."""
        out = self.plan(closure_graph(), self.TASK)
        self.assertLoadSuffix(out, "expertise.beta",
                              '<- promoted on "metrics exporter"', self.TASK)
        self.assertIn("expertise.alpha", load_section(out),
                      f"the promoted node's requires: parent did not load:\n{out}")

    def test_plan_promoted_node_descends_to_named_child(self):
        """Asserts SPEC-0005 PLAN_PROMOTED_NODE_TAKES_ITS_CLOSURE.

        The task names `sink`, a term of gamma's that is not
        a whole piece (`log sink` needs `log` too), so gamma is not itself
        promoted and arrives by descent from the promoted beta."""
        out = self.plan(closure_graph(), self.TASK)
        self.assertLoadSuffix(out, "expertise.gamma",
                              '<- composed by expertise.beta on "sink"', self.TASK)

    def test_plan_scored_and_hit_prints_no_suffix(self):
        """Asserts SPEC-0005 PLAN_PROMOTED_NODE_TAKES_ITS_CLOSURE.

        Guard. Precedence rule 1: a node that is both a scored entry and a
        phrase hit prints no suffix. Held by the mutant "a suffix on a scored
        entry"."""
        out = self.plan(closure_graph(with_decoys=False), "metrics exporter")
        line = load_section(out).get("expertise.beta")
        self.assertIsNotNone(line, out)
        self.assertNotIn("<-", line, f"a scored entry printed a suffix:\n  {line}")

    def test_plan_promoted_and_inferred_prints_promotion_only(self):
        """Asserts SPEC-0005 PLAN_PROMOTED_NODE_TAKES_ITS_CLOSURE.

        Precedence rule 2 over 3: beta hits `metrics exporter` AND the task
        names `deploy/otel.yaml`; only the promotion suffix prints."""
        task = "wire the metrics exporter in deploy/otel.yaml"
        out = self.plan(closure_graph(), task)
        self.assertLoadSuffix(out, "expertise.beta",
                              '<- promoted on "metrics exporter"', task)
        self.assertNotIn("inferred from", load_section(out)["expertise.beta"])

    def test_plan_seed_closure_is_accounted_before_promotion(self):
        """Asserts SPEC-0005 PLAN_PROMOTED_NODE_TAKES_ITS_CLOSURE.

        Guard: expertise.cache is reached both by the scored
        seed subsystem.orders's `requires:` and by descent from the promoted
        expertise.metrics (the task names `flush`, cache's own term). The
        scored closure is walked first, so cache is accounted as required,
        with no `composed by` suffix — exactly as before promotion existed."""
        nodes = guard_graph({
            "expertise.metrics": node_md(
                "expertise.metrics", "expertise", composes=["expertise.cache"],
                libraries=["metrics"], load_when=["metrics exporter"]),
            "expertise.cache": node_md(
                "expertise.cache", "expertise", requires=["expertise.metrics"],
                libraries=["metrics"], load_when=["flush interval, cache warmup"]),
        }, "orders service metrics exporter flush", name="orders")
        nodes["subsystem.orders"] = node_md(
            "subsystem.orders", "subsystem", requires=["expertise.cache"],
            load_when=["orders service metrics exporter flush"])
        task = "orders service metrics exporter flush"
        out = self.plan(nodes, task)
        self.assertLoadSuffix(out, "expertise.metrics",
                              '<- promoted on "metrics exporter"', task)
        line = load_section(out).get("expertise.cache")
        self.assertIsNotNone(line, out)
        self.assertNotIn("composed by", line,
                         f"the promoted node's descent accounted a node the "
                         f"scored closure reaches:\n  {line}")


# --------------------------------------------------------------------------
# Reachability through listed nodes' edges
# --------------------------------------------------------------------------

class ListedNodeEdgesTests(unittest.TestCase):

    def setUp(self):
        self.assertTrue(GRAPH_LINT.exists(), f"missing tool: {GRAPH_LINT}")
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def lint(self, *, island: bool) -> subprocess.CompletedProcess:
        """Rooted graph. index.md lists root, subsystem.main and
        subsystem.listed (A). The root reaches subsystem.main only, never A.
        subsystem.hidden (B) is named by no index row and
        reached only by A's `peers:`. With `island`, two unlisted nodes peer
        each other and nothing else reaches them."""
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

        Also covers SIBLING_UNREACHABLE_AFTER_GRAFT: a plant-owned index that
        lists `method.delegation` but not its new siblings is this shape.
        Measured on the unmodified tool: exit 1, `subsystem.hidden:
        unreachable from 'root' and unlisted in index.md`."""
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


# --------------------------------------------------------------------------
# Delegation leaves route on the installed graph
# --------------------------------------------------------------------------

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
    """One fresh install of this seed (as SeedAndPlantCopyAgreeTests builds
    one), shared by every case: the installed router over the installed graph."""

    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.plant = Path(cls._tmp.name) / "plant"
        cls.plant.mkdir(parents=True)
        cls.install = subprocess.run(
            ["bash", str(SEED / "install.sh"), "claude-code",
             "--project-dir", str(cls.plant)],
            capture_output=True, text=True, timeout=300)
        cls.graph = cls.plant / "docs" / "graph"
        cls.nodes = {}
        sys.path.insert(0, str(SEED / "templates" / "knowledge-graph"))
        try:
            import frontmatter as fm
        finally:
            sys.path.pop(0)
        for md in cls.graph.rglob("*.md"):
            text = md.read_text(encoding="utf-8")
            if not text.startswith("---\n"):
                continue
            try:
                meta, _ = fm.parse(text, md)
            except Exception:
                continue
            if isinstance(meta, dict) and meta.get("id"):
                cls.nodes.setdefault(meta["id"], meta)

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def setUp(self):
        self.assertEqual(self.install.returncode, 0,
                         f"install failed:\n{self.install.stdout}\n{self.install.stderr}")

    def sibling(self, nid: str) -> dict:
        meta = self.nodes.get(nid)
        self.assertIsNotNone(
            meta, f"{nid} is not in the installed graph: SPEC-0005 §6 "
                  f"'Delegation leaves' names it as a sibling of the split")
        return meta

    def test_delegation_sibling_routes_on_its_phrase(self):
        """Asserts SPEC-0005 DELEGATION_LEAVES_ROUTE.

        `--plan` on each sibling's representative phrase lists that sibling
        in LOAD."""
        for nid, phrase in DELEGATION_SIBLINGS:
            with self.subTest(sibling=nid):
                self.sibling(nid)
                r = plan_output(self.graph, phrase)
                self.assertEqual(r.returncode, 0, r.stderr)
                self.assertIn(nid, load_section(r.stdout),
                              f"--plan {phrase!r} did not load {nid}:\n{r.stdout}")

    def test_delegation_phrase_is_a_load_when_entry(self):
        """Asserts SPEC-0005 DELEGATION_LEAVES_ROUTE.

        The And: each representative phrase is, verbatim, one of that
        sibling's `load_when` entries."""
        for nid, phrase in DELEGATION_SIBLINGS:
            with self.subTest(sibling=nid):
                meta = self.sibling(nid)
                load_when = meta.get("load_when") or []
                self.assertIn(phrase, load_when,
                              f"{nid}'s load_when does not carry {phrase!r} "
                              f"verbatim: {load_when}")


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
        """`load_when:` is routing. An expertise node may carry `draft-07` or
        `bash 3.2 floor` so that a task naming either routes to it; the node
        asserts nothing about what the project uses.

        This is the guard, not the catch: it is green before the change and
        must stay green after it. A check that scanned the whole frontmatter
        would turn any graph whose expertise nodes route on such keywords red;
        `3.2` is a token today's VERSION_RE already matches — asserted below, so this
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


class PlanEntryPathTests(unittest.TestCase):
    """SPEC-0003 PLAN_ENTRY_NAMES_THE_NODE_FILE (7.32.0, decision 9): `--plan`
    prints each node's file, relative to the plant root, beside its id, so no
    session spends turns finding the file the router already found.

    The fixture is a plant, not a bare graph: the tool sits at
    `<plant>/docs/graph/graph-lint.py` and runs from `<plant>`, as the contract
    says. One machinery node lives at `docs/graph/agents/04-tester.md`, a path
    the id `agent.tester` does not spell, so a path rebuilt from the id as
    `docs/graph/nodes/<id>.md` fails here. Measured against the pre-7.32.0
    tool, this fixture gives three LOAD lines and one NOT LOADED line, each
    `  <id> <text>` with no path."""

    TASK = "write widget ledger tests"

    def setUp(self):
        self.assertTrue(GRAPH_LINT.exists(), f"missing tool: {GRAPH_LINT}")
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

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
        """PLAN_ENTRY_NAMES_THE_NODE_FILE: every entry line under `LOAD (` and
        `NOT LOADED (` is two spaces, the id, whitespace, the node's file path
        relative to the plant root, whitespace, then the text it carried before
        (a LOAD line's title, a NOT LOADED line's reason). The id stays the
        first token, so a parser that reads only the id is unaffected."""
        plant, files, titles = self._plant()
        for rel in files.values():
            self.assertTrue((plant / rel).is_file(), f"harness: fixture file {rel} is missing")
        r = subprocess.run([sys.executable, "docs/graph/graph-lint.py", "--plan", self.TASK],
                           cwd=str(plant), capture_output=True, text=True, timeout=120)
        out = r.stdout
        self.assertEqual(r.returncode, 0, f"--plan exited {r.returncode}:\n{out}\n{r.stderr}")
        entries, section = [], None
        for line in out.splitlines():
            if line.startswith("LOAD ("):
                section = "LOAD"
                continue
            if line.startswith("NOT LOADED ("):
                section = "NOT LOADED"
                continue
            if section and line.startswith("  ") and not line.startswith("  ! "):
                entries.append((section, line))
        load_ids = [l.split()[0] for s, l in entries if s == "LOAD"]
        nl_ids = [l.split()[0] for s, l in entries if s == "NOT LOADED"]
        self.assertEqual(sorted(load_ids), ["agent.tester", "root", "subsystem.alpha"],
                         f"harness: the fixture no longer routes as measured. Output:\n{out}")
        self.assertEqual(nl_ids, ["subsystem.beta"],
                         f"harness: the fixture no longer routes as measured. Output:\n{out}")
        problems = []
        for section, line in entries:
            m = re.match(r"^  (\S+)\s+(\S+)\s+(\S.*)$", line)
            if not m:
                problems.append(f"{section}: {line!r} is not `  <id>  <path>  <text>`")
                continue
            nid, path, rest = m.groups()
            if path != files.get(nid):
                problems.append(f"{section}: {line!r}: second token {path!r}, expected the "
                                f"node's file {files.get(nid)!r}")
                continue
            if section == "LOAD" and not rest.startswith(titles[nid]):
                problems.append(f"{section}: {line!r}: the text after the path is not the "
                                f"title {titles[nid]!r} the line carried before")
            if section == "NOT LOADED" and not rest.startswith("peer of subsystem.alpha"):
                problems.append(f"{section}: {line!r}: the text after the path is not the "
                                f"reason the line carried before")
        self.assertFalse(problems, "PLAN_ENTRY_NAMES_THE_NODE_FILE:\n  "
                         + "\n  ".join(problems) + f"\nOutput:\n{out}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
