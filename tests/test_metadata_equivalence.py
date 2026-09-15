#!/usr/bin/env python3
"""test_metadata_equivalence.py — the U-31/U-32 mechanical equivalence gate.

One responsibility — "parse this repo's YAML-subset frontmatter and
interpret its scalars" — has at least five independent implementations in
this seed:

  integrations/claude-code/agent-lint.py      parse_frontmatter + _scalar
  templates/knowledge-graph/graph-lint.py     parse_frontmatter + _scalar
  tests/seed-lint.py                          parse_frontmatter + frontmatter_block
  tools/status-register.py                    parse_frontmatter + _scalar
  tools/growth-audit.py                       parse_frontmatter

Plus a second duplicated responsibility (U-32) — the router's tokenizer and
matcher — living in BOTH agent-lint.py (_tokens/_match/_merge/_terms) and
graph-lint.py (_tokens/_match/_terms).

This is not an oversight. graph-lint.py, spec-lint.py, grill-lint.py,
agent-lint.py, agnosticism-lint.py, prose-lint.py and status-register.py are
each installed into a plant as a STANDALONE file by install.sh. Importing a
shared module would add another file to what install.sh ships every plant —
an owner decision nobody has made. The seed's own doctrine names the
alternative to a sync comment: "one implementation, shared library, generated
copy, or mechanical equivalence test." This file is that test. It does not
unify the five parsers or the two tokenizers — it loads each one BY PATH (so
this file is never a sixth implementation of the same logic) and asserts they
agree on the facts they all claim to extract, so a change to one that quietly
breaks the contract the others hold is caught here instead of on a plant that
happens to hit the gap.

Where two implementations differ in SCOPE only (one takes a path, one takes
text; one returns a body, one doesn't) this file normalizes at the call site.
Where they differ in BEHAVIOR — and several genuinely do — this file asserts
the actual, current behavior of each side and names the divergence in the
test itself, rather than forcing false agreement or quietly picking one side
to treat as ground truth. A comment at each such assertion says why the gap
is allowed to stand for now; it is not a TODO to unify, since unifying is the
one thing this test is here to make unnecessary.

Runs standalone: `python3 tests/test_metadata_equivalence.py`. Stdlib only.
"""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

# --------------------------------------------------------------------------
# Locate the five implementations from this file's own location, the same
# way tests/test_graph_lint.py locates graph-lint.py — no host-specific path.
# --------------------------------------------------------------------------
HERE = Path(__file__).resolve().parent          # <seed>/tests
SEED = HERE.parent                               # the seed root (this repo)

IMPL_PATHS = {
    "agent-lint": SEED / "integrations" / "claude-code" / "agent-lint.py",
    "graph-lint": SEED / "templates" / "knowledge-graph" / "graph-lint.py",
    "seed-lint": SEED / "tests" / "seed-lint.py",
    "status-register": SEED / "tools" / "status-register.py",
    "growth-audit": SEED / "tools" / "growth-audit.py",
}


def _load(name: str, path: Path):
    """Import one implementation BY PATH, without ever running its CLI.

    Every module above is guarded by `if __name__ == "__main__":`, so a plain
    import cannot trigger argument parsing or a main() side effect — verified
    by hand against all five before this test was written. One of them
    (agent-lint.py) defines a @dataclass, and a dataclass decorator looks its
    own module up in sys.modules while it runs; loaded the ordinary way (spec
    + module_from_spec + exec_module, with no sys.modules entry) that lookup
    fails with an opaque AttributeError that has nothing to do with the
    frontmatter logic under test. Registering the module in sys.modules
    before exec_module fixes it — the same trick tests/seed-lint.py's own
    `load_tool` helper uses to import tools/*.py, applied here as a fresh
    module object per implementation to avoid two tools sharing state.
    """
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot build an import spec for {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


IMPL_MODULES: dict = {}
IMPL_ERRORS: dict = {}
for _name, _path in IMPL_PATHS.items():
    try:
        IMPL_MODULES[_name] = _load(_name, _path)
    except Exception as exc:  # noqa: BLE001 - reported by a dedicated test, not swallowed
        IMPL_ERRORS[_name] = f"{type(exc).__name__}: {exc}"


class TestImplementationsAreImportable(unittest.TestCase):
    """Guards the precondition every other test in this file relies on.

    If a future change makes one of the five files fail to import cleanly (a
    stray top-level side effect, a moved class, a syntax error), every test
    below that depends on it would otherwise fail with a confusing "module
    has no attribute X" instead of the real story. This test is the one place
    that says, plainly, which file could not be loaded and why — the report
    the task asked for, not a workaround that reimplements the missing logic.
    """

    def test_all_five_implementations_import(self):
        if IMPL_ERRORS:
            detail = "\n".join(f"  {name}: {msg}" for name, msg in IMPL_ERRORS.items())
            self.fail(
                "the following implementation(s) could not be imported by "
                f"path — see IMPL_ERRORS for detail, this test does not work "
                f"around it:\n{detail}"
            )


def _require(name: str):
    if name in IMPL_ERRORS:
        raise unittest.SkipTest(f"{name} failed to import: {IMPL_ERRORS[name]}")
    return IMPL_MODULES[name]


# --------------------------------------------------------------------------
# Frontmatter fixtures (U-31)
# --------------------------------------------------------------------------


class _TmpNode:
    """A real file on disk holding `text`, for the two implementations
    (growth-audit.py, tests/seed-lint.py) that read frontmatter by Path
    rather than accepting text directly. Also handed to agent-lint.py /
    graph-lint.py as the `path` argument their signature requires, even
    though they parse the `text` argument, not the file — normalizing the
    text-vs-path split at the call site rather than in either tool.
    """

    def __init__(self, text: str):
        fd = tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", dir=str(HERE), delete=False, encoding="utf-8"
        )
        fd.write(text)
        fd.close()
        self.path = Path(fd.name)

    def __enter__(self):
        return self.path

    def __exit__(self, *exc):
        self.path.unlink(missing_ok=True)


def run_all_parsers(text: str) -> dict:
    """Drive every one of the five parse_frontmatter implementations over
    the same input and return {impl_name: (ok, meta_or_reason)}.

    `ok` is normalized across four different ways of reporting "this input
    has no usable frontmatter": agent-lint/graph-lint raise LintError,
    status-register returns None, growth-audit returns {}, and seed-lint
    appends to a module-global `findings` list and returns {}. Normalizing
    that signal is exactly the "differ in scope, not in the parsed facts"
    case the task calls out — the equivalence claim below is about what got
    extracted, not which of four failure conventions reported that nothing
    did. Any implementation that failed to import is skipped here (SkipTest
    surfaces as a skip in that specific fixture, and the dedicated import
    test above still fails the whole run).
    """
    results: dict = {}
    with _TmpNode(text) as path:
        if "agent-lint" not in IMPL_ERRORS:
            al = IMPL_MODULES["agent-lint"]
            try:
                meta, _body = al.parse_frontmatter(text, path)
                results["agent-lint"] = (True, meta)
            except al.LintError as e:
                results["agent-lint"] = (False, str(e))

        if "graph-lint" not in IMPL_ERRORS:
            gl = IMPL_MODULES["graph-lint"]
            try:
                meta, _body = gl.parse_frontmatter(text, path)
                results["graph-lint"] = (True, meta)
            except gl.LintError as e:
                results["graph-lint"] = (False, str(e))

        if "status-register" not in IMPL_ERRORS:
            sr = IMPL_MODULES["status-register"]
            r = sr.parse_frontmatter(text)
            if r is None:
                results["status-register"] = (False, "parse_frontmatter returned None")
            else:
                meta, _lines, _body, _first = r
                results["status-register"] = (True, meta)

        if "growth-audit" not in IMPL_ERRORS:
            ga = IMPL_MODULES["growth-audit"]
            meta = ga.parse_frontmatter(path)
            # growth-audit cannot tell "no frontmatter" apart from "frontmatter
            # present but empty" — both return {}. None of the fixtures below
            # exercise the second case, so {} is read here as the absence
            # signal; that blind spot is real and is exactly the kind of gap
            # this file exists to surface, not paper over.
            if meta == {}:
                results["growth-audit"] = (False, "parse_frontmatter returned {}")
            else:
                results["growth-audit"] = (True, meta)

        if "seed-lint" not in IMPL_ERRORS:
            sl = IMPL_MODULES["seed-lint"]
            sl.findings.clear()
            meta = dict(sl.parse_frontmatter(path))
            had_finding = bool(sl.findings)
            sl.findings.clear()
            meta.pop("_body", None)
            if had_finding:
                results["seed-lint"] = (False, "seed-lint recorded a finding")
            else:
                results["seed-lint"] = (True, meta)

    return results


STRUCTURED = ("agent-lint", "graph-lint", "status-register")   # apply a _scalar-like step
TOLERANT = ("seed-lint", "growth-audit")                        # store raw regex captures
ALL_FIVE = STRUCTURED + TOLERANT


class TestFrontmatterFactsAgree(unittest.TestCase):
    """Cases where all five implementations claim to extract the same fact,
    and disagreeing would mean a plant's linters silently read one file's
    metadata differently depending on which tool asked."""

    def setUp(self):
        for name in ALL_FIVE:
            if name in IMPL_ERRORS:
                self.skipTest(f"{name} failed to import: {IMPL_ERRORS[name]}")

    def test_plain_key_value(self):
        """A bare `key: value` line is the overwhelming common case across
        every roster/manifest/node file in the seed. If the five parsers
        disagreed here, nothing downstream could trust ANY frontmatter read."""
        text = "---\nid: plain.test\ntitle: Plain Value\n---\nbody\n"
        results = run_all_parsers(text)
        for name in ALL_FIVE:
            ok, meta = results[name]
            self.assertTrue(ok, f"{name}: expected a usable frontmatter block")
            self.assertEqual(meta["title"], "Plain Value", name)

    def test_value_containing_a_colon(self):
        """A description or note that itself contains ':' (a ratio, a URL, a
        time) must not truncate at the first colon differently across tools —
        all five split on the FIRST ':' only, so this must round-trip whole."""
        text = "---\nid: colon.test\nnote: ratio 3:1 acceptable\n---\nbody\n"
        results = run_all_parsers(text)
        for name in ALL_FIVE:
            ok, meta = results[name]
            self.assertTrue(ok, name)
            self.assertEqual(meta["note"], "ratio 3:1 acceptable", name)

    def test_empty_value_opens_a_list_without_swallowing_the_next_key(self):
        """`key:` with nothing after the colon means "empty list, items may
        follow" in this YAML subset. The failure this guards: a parser that
        forgets to reset its `current` pointer would fold the NEXT key's
        value into the empty list's items instead of starting a new key."""
        text = "---\nid: empty.test\nnotes:\ntitle: After Empty\n---\nbody\n"
        results = run_all_parsers(text)
        for name in ALL_FIVE:
            ok, meta = results[name]
            self.assertTrue(ok, name)
            self.assertEqual(meta["notes"], [], name)
            self.assertEqual(meta["title"], "After Empty", name)

    def test_indented_block_list_plain_items(self):
        """The `owns:` / `requires:` / `load_when:` shape every graph node
        uses: a key with nothing on its own line, followed by indented
        `- item` lines. This is the single most load-bearing shape in the
        whole seed — every graph-lint contract check depends on it parsing
        identically everywhere."""
        text = "---\nid: list.test\ntags:\n  - alpha\n  - beta\n  - gamma\n---\nbody\n"
        results = run_all_parsers(text)
        for name in ALL_FIVE:
            ok, meta = results[name]
            self.assertTrue(ok, name)
            self.assertEqual(meta["tags"], ["alpha", "beta", "gamma"], name)

    def test_boolean_ish_value_stays_a_string_everywhere(self):
        """`can_delegate: true` is the exact value agent-lint's delegator
        invariant is built on. None of the five parse_frontmatter
        implementations casts it to a real Python bool at parse time — they
        all hand back the literal string 'true' and leave the bool coercion
        to the CALLER (agent-lint's `Agent.can_delegate` property does
        `str(...).strip().lower() == "true"` one layer up). That is a
        genuine point where the five could have diverged on TYPE, so it is
        asserted here rather than assumed: they agree, and they agree by
        agreeing to do nothing clever."""
        text = "---\nid: bool.test\ncan_delegate: true\n---\nbody\n"
        results = run_all_parsers(text)
        for name in ALL_FIVE:
            ok, meta = results[name]
            self.assertTrue(ok, name)
            self.assertEqual(meta["can_delegate"], "true", name)
            self.assertIsInstance(meta["can_delegate"], str, name)


# The readers that now share templates/knowledge-graph/frontmatter.py. This
# list IS the ledger of the consolidation: it grew as each parser converted, and
# every divergence this file used to document is closed for its members.
SHARED = ("agent-lint", "graph-lint", "seed-lint", "growth-audit")
# The one recorded exception, and it is deliberate rather than accidental.
# tools/status-register.py keeps its own reader because (a) its docstring states
# the tolerance as a design choice — "a line that fits neither shape is skipped
# rather than raised, because frontmatter well-formedness is graph-lint's rule,
# not this one's" — and (b) it returns a key→line-number map the shared reader
# does not produce, which it needs to rewrite a status in place. Converting it
# would either break its stated contract or widen the shared reader for one
# caller. Recorded, not silently tolerated.
UNSHARED = ("status-register",)


class TestFrontmatterReadersAgree(unittest.TestCase):
    """Every shape that used to diverge now reads identically across SHARED.

    This class used to be called TestFrontmatterDivergences and its job was to
    DOCUMENT disagreement: `tools: [Read, Write, Task]` split by one reader and
    left as a literal string by four; a trailing `  # comment` stripped by three
    and kept by two; `2` typed as an int by three and a string by two; and a
    description continued on a second line REJECTED by two and SILENTLY
    TRUNCATED by three — losing the continuation with no error, no warning and
    no finding.

    None of that was decided. It is what one small job written seven times
    produces. The readers now share one implementation, so the tests below
    assert agreement and fail if it returns."""

    def _all(self, text):
        results = run_all_parsers(text)
        return {n: results[n] for n in SHARED if n in results}

    def test_inline_bracket_list_reads_the_same_everywhere(self):
        got = self._all("---\nid: inline.test\ntools: [Read, Write, Task]\n---\nbody\n")
        for name, (ok, meta) in got.items():
            self.assertTrue(ok, name)
            self.assertEqual(meta["tools"], ["Read", "Write", "Task"], name)

    def test_trailing_comment_stripped_the_same_everywhere(self):
        got = self._all("---\nid: c.test\nstatus: open  # figure this out later\n---\nbody\n")
        for name, (ok, meta) in got.items():
            self.assertTrue(ok, name)
            self.assertEqual(meta["status"], "open", name)

    def test_integer_typed_the_same_everywhere(self):
        got = self._all("---\nid: i.test\nmax_spawn_depth: 2\n---\nbody\n")
        for name, (ok, meta) in got.items():
            self.assertTrue(ok, name)
            self.assertEqual(meta["max_spawn_depth"], 2, name)
            self.assertIsInstance(meta["max_spawn_depth"], int, name)

    def test_quoted_scalar_unquoted_the_same_everywhere(self):
        got = self._all("---\nid: q.test\ntitle: \"a quoted title\"\n---\nbody\n")
        for name, (ok, meta) in got.items():
            self.assertTrue(ok, name)
            self.assertEqual(meta["title"], "a quoted title", name)

    def test_multiline_description_is_refused_the_same_everywhere(self):
        """The shape that started the consolidation.

        Two readers rejected it and three kept only the first line, dropping the
        continuation silently. `description:` is what the router scores and what
        a session reads to judge relevance, so a node advertised less than it
        said and nobody found out. Every shared reader now REFUSES it, with a
        message telling the author to put the value on one line."""
        text = ("---\nid: multiline.test\n"
                "description: This starts here\n"
                "  and continues indented.\n---\nbody\n")
        got = self._all(text)
        for name, (ok, detail) in got.items():
            self.assertFalse(ok, f"{name} accepted a multi-line description: {detail!r}")
        # The message is asserted only where the reader RAISES. seed-lint routes
        # the same refusal through its own findings collector, so the harness
        # surfaces its wording and not the reader's — refusal is the contract,
        # the sentence is what the author sees when it raises.
        for name in ("agent-lint", "graph-lint"):
            if name in got:
                self.assertIn("one line", str(got[name][1]), name)

    def test_the_unshared_reader_is_named_and_still_tolerant(self):
        """status-register is the recorded exception, so its difference is a
        FACT this file asserts rather than a gap it leaves unstated."""
        results = run_all_parsers(
            "---\nid: multiline.test\ndescription: This starts here\n"
            "  and continues indented.\n---\nbody\n")
        for name in UNSHARED:
            if name not in results:
                continue
            ok, meta = results[name]
            self.assertTrue(ok, f"{name} is documented as tolerant; it refused")
            self.assertEqual(meta["description"], "This starts here", name)


class TestFrontmatterErrorPaths(unittest.TestCase):
    """The two ways a file can have no usable frontmatter at all. All five
    implementations must treat both as 'nothing to extract' even though they
    signal it through four different mechanisms (exception / None / {} /
    a recorded finding) — the normalization `run_all_parsers` performs."""

    def setUp(self):
        for name in ALL_FIVE:
            if name in IMPL_ERRORS:
                self.skipTest(f"{name} failed to import: {IMPL_ERRORS[name]}")

    def test_missing_frontmatter_entirely(self):
        """A file with no leading `---` block at all — the common case of
        someone forgetting frontmatter altogether. Every implementation must
        refuse to fabricate facts out of body prose."""
        text = "no frontmatter here\njust body text\n"
        results = run_all_parsers(text)
        for name in ALL_FIVE:
            ok, _reason = results[name]
            self.assertFalse(ok, f"{name}: should report absent frontmatter")

    def test_unterminated_frontmatter(self):
        """An opening `---` with no closing `---` — a truncated file or a
        forgotten delimiter. agent-lint/graph-lint give this a DIFFERENT
        message than the missing-entirely case ('unterminated' vs 'missing'),
        which the other three cannot do at all (their single regex requires
        both delimiters to match anything, so missing and unterminated
        collapse into the same {} / None / finding). This test only requires
        that every implementation refuses the input; the message-level
        distinction is documented here, not asserted, since three of five
        structurally cannot make it."""
        text = "---\nid: x\ntitle: Unterminated\n"
        results = run_all_parsers(text)
        for name in ALL_FIVE:
            ok, _reason = results[name]
            self.assertFalse(ok, f"{name}: should report unterminated frontmatter")
        # The two that DO distinguish should actually say so, in their own words.
        self.assertIn("unterminated", results["agent-lint"][1].lower())
        self.assertIn("unterminated", results["graph-lint"][1].lower())


# --------------------------------------------------------------------------
# Router tokenizer/matcher (U-32): agent-lint.py vs graph-lint.py
# --------------------------------------------------------------------------


class TestRouterTokenizerEquivalence(unittest.TestCase):
    """agent-lint.py's `_tokens`/`_match` are a documented fork of
    graph-lint.py's own `_tokens`/`_match` (agent-lint's docstring says so:
    "mirror graph-lint.resolve"). Where the fork was meant to preserve
    behavior, this asserts it did. Where agent-lint deliberately improved on
    graph-lint (the hyphen-fragment fix), the improvement is real and graph-
    lint has NOT received it — see test_router_tokenizers_have_diverged."""

    def setUp(self):
        for name in ("agent-lint", "graph-lint"):
            if name in IMPL_ERRORS:
                self.skipTest(f"{name} failed to import: {IMPL_ERRORS[name]}")
        self.al = IMPL_MODULES["agent-lint"]
        self.gl = IMPL_MODULES["graph-lint"]

    def _strength(self, mod, text: str, term: str) -> int:
        return mod._match(term, mod._tokens(text))

    def test_tokens_agree_on_plain_standalone_words(self):
        """A task with no hyphenated compounds anywhere is the common case,
        and both routers must score it identically — this is the floor the
        fork must not have broken."""
        text = "the security review process"
        self.assertEqual(self._strength(self.al, text, "security"), 2)
        self.assertEqual(self._strength(self.gl, text, "security"), 2)

    def test_tokens_agree_on_prefix_fold(self):
        """The STEM=6 singular/plural (and near-miss) fold must line up
        between the two routers for a NON-hyphenated word, or a task that
        matches one router's roster would silently fail to match the
        other's."""
        text = "delegation triggers here"
        self.assertEqual(self._strength(self.al, text, "delegate"), 1)
        self.assertEqual(self._strength(self.gl, text, "delegate"), 1)

    def test_both_routers_discount_a_compound_fragment(self):
        """CONVERGENCE, asserted on the path each router actually scores with.

        This test used to assert the opposite, and passed while being false.
        It compared `_match(term, _tokens(text))` in both files — agent-lint's
        real path, and graph-lint's DEAD one. `graph-lint._tokens` (and its one
        caller, `Node.routable_terms`) has no live caller anywhere in the tree;
        `resolve()` scores through `_split_terms`/`_strength`, which DID receive
        the compound-fragment fix. So the divergence the test named had already
        been closed, in a function the test never called, and its tripwire
        ("if this fires, re-check whether graph-lint.py gained the fix") could
        never fire.

        A test whose name is a finding is a liability once the finding is
        fixed. This one now asserts the property both routers must share, on
        the entry points a plant actually runs: a hyphen fragment is weak
        evidence, so a task about "chain of calls" cannot take the band from a
        trigger that says "supply-chain".
        """
        text = "assess the supply-chain and secrets handling risk"

        agent_strength = self._strength(self.al, text, "chain")
        whole, frag = self.gl._split_terms(text)
        graph_strength = self.gl._strength("chain", whole, frag)

        self.assertEqual(agent_strength, 1,
                         "agent-lint: a fragment of a compound is weak evidence")
        self.assertEqual(graph_strength, 1,
                         "graph-lint: resolve() scores through _split_terms/_strength, "
                         "which caps a hyphen fragment at the near-match tier")
        self.assertEqual(
            agent_strength, graph_strength,
            "the routers have diverged on compound fragments — a plant's graph "
            "router and its agent router would rank the same task differently "
            "against the same vocabulary. Whichever one lost the cap, restore "
            "it; do not relax this assertion.")

        # The whole/fragment split itself, so a future 'fix' that simply stops
        # splitting on hyphens cannot satisfy the equality above by making both
        # sides wrong.
        self.assertIn("supply-chain", whole,
                      "the compound must survive whole, or its owner loses it")
        self.assertIn("chain", frag,
                      "the pieces must be reachable, at the fragment tier")

    def test_every_separator_discounts_its_fragments_in_both_routers(self):
        """The class, not the hyphen.

        The compound-fragment fix discounted `-` and nothing else, while the
        TASK side of the same comparison already split on `-`, `/`, `.` and
        `*`. So the two halves of one comparison disagreed, and a piece of a
        path spoke for the whole: `docs/graph` in `protocol.grow`'s load_when
        made `graph` score exactly like a standalone word, the same shape that
        let `chain` out of `supply-chain` take the band for `agent.security`.
        Measured when this was written: 13 shipped path compounds across
        load_when and routing_triggers, and `node.template.md` ships
        `"editing {{repo-or-path}}/**"`, so every plant is taught to write more.

        A node's own id is the exception and is asserted below: `expertise.
        ef-core` IS `ef-core`, because that is its name rather than somebody
        else's compound.
        """
        for sep in ("-", "/", "."):
            text = f"audit the supply{sep}chain and secrets handling risk"
            with self.subTest(separator=sep):
                self.assertEqual(
                    self._strength(self.al, text, "chain"), 1,
                    f"agent-lint: a fragment split on {sep!r} scores at full "
                    f"strength")
                whole, frag = self.gl._split_terms(text)
                self.assertEqual(
                    self.gl._strength("chain", whole, frag), 1,
                    f"graph-lint: a fragment split on {sep!r} scores at full "
                    f"strength")
                self.assertEqual(
                    self.gl._strength(f"supply{sep}chain", whole, frag), 2,
                    "the compound must still reach its owner whole")

    def test_a_node_id_segment_is_a_name_not_a_fragment(self):
        """`expertise.ef-core` is `ef-core`. Discounting a node's OWN id
        segments would make every expertise child harder to select than the
        task words that name it, which is the opposite of the defect above."""
        whole, frag = self.gl._split_terms("expertise.ef-core", keep_path_segments=True)
        self.assertEqual(self.gl._strength("ef-core", whole, frag), 2,
                         "a node's id segment was demoted to a fragment")

    def test_graph_lints_dead_tokenizer_has_no_live_caller(self):
        """The half of the fix that did NOT land when the scorer's did.

        `resolve()` has two decisions, and 7.16.0 gave the fragment model to
        one of them. Scoring went through `_split_terms`/`_strength`; the
        expertise DESCENT kept reading `Node.triggers`, whose `_tokens` regex
        has no `-` in it, so a child whose `load_when` says `supply-chain` was
        still descended into on the bare term `chain` — and descent requires
        the standalone tier (`== 2`) precisely so that a weak match cannot pull
        an expertise subtree into context.

        Two reviewers adjudicated this fix as landed by reading the scoring
        path. It was landed there and nowhere else, which is why this asserts
        the descent vocabulary directly.
        """
        text = "assess the supply-chain and secrets handling risk"
        whole, frag = self.gl._split_terms(text)

        self.assertEqual(
            self.gl._strength("chain", whole, frag), 1,
            "the descent would fire on a compound fragment: a task saying "
            "`chain` pulls in an expertise whose trigger says `supply-chain`")
        self.assertEqual(
            self.gl._strength("supply-chain", whole, frag), 2,
            "the compound must still reach its owner at full strength")

        # `triggers` is the OLD vocabulary and still has readers (the sibling
        # collision report). This pins that the descent is not one of them.
        src = (SEED / "templates" / "knowledge-graph" / "graph-lint.py").read_text(
            encoding="utf-8")
        descent = src[src.index("kids = [by_id[c] for c in n.get_list(\"composes\")"
                                " if c in by_id]", src.index("def resolve")):]
        descent = descent[:descent.index("return")]
        self.assertNotIn(
            ".triggers", descent,
            "the expertise descent is reading Node.triggers again, which does "
            "not split hyphens — use trigger_terms/_strength so a fragment "
            "cannot clear the standalone tier the descent requires.")


if __name__ == "__main__":
    unittest.main()
