#!/usr/bin/env python3
"""The two routers must be reachable by the word forms people actually type.

Both routers score a task's words against a roster's vocabulary. Both shipped
a `STEM = 6` prefix probe documented as "the singular/plural fold
(test/tests, node/nodes)" — a one-sided test requiring the TASK's term to be at
least six characters and to PREFIX a roster token. A plural never prefixes its
own singular, because it is longer. Every example both comments cite scored 0.

That is not a tuning question. A third of each router's vocabulary could not be
reached by its own plural, and the remainder matched at half strength — enough,
measured, to change which agent a task routes to based on the tense of one word.

This suite derives its numbers from the roster and the node set on every run, so
it measures the tree that ships rather than a fixture. Plan of record:
docs/plans/router-lexical-reach.md.
"""
import importlib.util
import json
import pathlib
import re
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent


def _load(rel, name):
    """Load a router from its SOURCE TEXT, never through the import cache.

    Python validates a `__pycache__` entry on (mtime, size). Editing
    `("ing", 3, 6)` to `("ing", 3, 7)` changes neither, so a stale `.pyc` is
    served as valid and the suite silently measures code that is not in the
    file. That is not hypothetical: it happened while this suite was being
    written, and `ratchet-lint.py` compiles from text for the same reason,
    having caught itself reporting a stale value on its first run.
    """
    path = ROOT / rel
    src = path.read_text(encoding="utf-8")
    mod = importlib.util.module_from_spec(
        importlib.util.spec_from_loader(name, loader=None))
    mod.__file__ = str(path)
    sys.modules[name] = mod          # dataclasses needs the module registered
    exec(compile(src, str(path), "exec"), mod.__dict__)
    return mod


AL = _load("integrations/claude-code/agent-lint.py", "_reach_agent_lint")
GL = _load("templates/knowledge-graph/graph-lint.py", "_reach_graph_lint")
AGENTS = AL.load_agents(ROOT / "agents")

# The examples both STEM comments name, plus the tense pair that changed a route.
FOLD_EXAMPLES = [
    ("nodes", "node"), ("node", "nodes"),
    ("tests", "test"), ("test", "tests"),
    ("orders", "order"), ("order", "orders"),
    ("checked", "check"), ("check", "checked"),
    ("specs", "spec"), ("claims", "claim"), ("risks", "risk"),
    ("audits", "audit"), ("auditing", "audit"),
    ("facts", "fact"), ("graphs", "graph"), ("agents", "agent"),
]


def plural(t):
    if t.endswith("y") and len(t) > 3 and t[-2] not in "aeiou":
        return t[:-1] + "ies"
    if t.endswith(("s", "x", "z", "ch", "sh")):
        return t + "es"
    return t + "s"


def roster_vocab():
    v = set()
    for a in AGENTS:
        n, tr, _d = AL._token_sets(a)
        v |= set(n) | set(tr)
    return {t for t in v
            if t not in AL.STOPWORDS and len(t) > 2 and t.isalpha()
            and not t.endswith("s")}


def load_when_vocab():
    pats = ["protocols/*.md", "skills/*/SKILL.md", "skills/*.md",
            "agents/*.md", "core/method/*.md"]
    v = set()
    for pat in pats:
        for p in sorted(ROOT.glob(pat)):
            text = p.read_text(encoding="utf-8", errors="replace")
            m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
            if not m:
                continue
            blk = re.search(r"^load_when:\s*\n((?:\s*-\s.*\n)+)", m.group(1), re.M)
            if blk:
                for line in re.findall(r'^\s*-\s*"?(.*?)"?\s*$', blk.group(1), re.M):
                    v |= GL._tokens(line)
    return {t for t in v
            if t not in GL.STOPWORDS and len(t) > 2 and t.isalpha()
            and not t.endswith("s")}


class FoldExamples(unittest.TestCase):
    """An inflection must match the word it inflects, at full strength."""

    def test_agent_router_matches_its_documented_examples(self):

        """Asserts SPEC-0002 AN_INFLECTION_MATCHES_THE_WORD_IT_INFLECTS."""
        bad = [(t, k) for t, k in FOLD_EXAMPLES if AL._match(t, {k: 2}) != 2]
        self.assertEqual(bad, [], f"{len(bad)} inflections do not reach their "
                                 f"own base word in agent-lint: {bad}")

    def test_knowledge_router_matches_its_documented_examples(self):

        """Asserts SPEC-0002 AN_INFLECTION_MATCHES_THE_WORD_IT_INFLECTS."""
        bad = [(t, k) for t, k in FOLD_EXAMPLES if GL._match(t, {k}) != 2]
        self.assertEqual(bad, [], f"{len(bad)} inflections do not reach their "
                                 f"own base word in graph-lint: {bad}")


class TenseDoesNotChangeTheRoute(unittest.TestCase):
    """A route that turns on the tense of one word is not a route.

    'our penetration test report needs its citations checked' routed to
    `pentest`; the same sentence with 'check' routed to `devils-advocate`,
    because the trigger word is 'check' and 'checked' scored zero against it.
    """

    PAIRS = [
        ("our penetration test report needs its citations checked",
         "our penetration test report needs its citations check"),
        ("dedupe the knowledge facts so each has one home",
         "dedupe the knowledge fact so each has one home"),
        ("author a graph node for the subsystem",
         "author graph nodes for the subsystem"),
    ]

    def test_inflection_does_not_change_the_top_pick(self):

        """Asserts SPEC-0002 AN_INFLECTION_MATCHES_THE_WORD_IT_INFLECTS."""
        for a, b in self.PAIRS:
            with self.subTest(pair=(a, b)):
                ta = AL.score(AGENTS, a)
                tb = AL.score(AGENTS, b)
                na = ta[0][1].name if ta else None
                nb = tb[0][1].name if tb else None
                self.assertEqual(na, nb,
                                 f"inflection changed the route: {a!r} -> {na}, "
                                 f"{b!r} -> {nb}")


class Reach(unittest.TestCase):
    """No routing vocabulary may be unreachable by its own plural.

    Measured over the tree that ships, not a fixture: 32% of the agent roster's
    singular vocabulary and 39% of the seed's `load_when:` vocabulary scored
    zero against their own plurals when this suite was written.
    """

    def test_every_roster_word_is_reachable_by_its_plural(self):

        """Asserts SPEC-0002 AN_INFLECTION_MATCHES_THE_WORD_IT_INFLECTS."""
        miss = sorted(t for t in roster_vocab() if AL._match(plural(t), {t: 2}) == 0)
        self.assertEqual(miss, [], f"{len(miss)} roster words unreachable by "
                                   f"their own plural, e.g. "
                                   f"{[plural(t) for t in miss[:12]]}")

    def test_every_load_when_word_is_reachable_by_its_plural(self):

        """Asserts SPEC-0002 AN_INFLECTION_MATCHES_THE_WORD_IT_INFLECTS."""
        miss = sorted(t for t in load_when_vocab() if GL._match(plural(t), {t}) == 0)
        self.assertEqual(miss, [], f"{len(miss)} load_when words unreachable by "
                                   f"their own plural, e.g. "
                                   f"{[plural(t) for t in miss[:12]]}")


class StemPrefixInvariant(unittest.TestCase):
    """Both `_match` implementations skip a token whose first three characters
    match none of the term's stems' first three. That is an optimisation, and it
    is only sound while every form `_stems(w)` returns starts with `w[:3]`.

    Asserted over the real vocabulary of both routers AND over a constructed
    table covering every rule, including the irregular map — the rule most
    likely to break it, since an irregular is the one case where the stem is not
    derived from the word by stripping.
    """

    TABLE = ["nodes", "duties", "processes", "caches", "fixes", "routing",
             "planning", "checked", "moved", "repositories", "analyses",
             "criteria", "indices", "matrices", "vertices", "schemata",
             "aliases", "documentation", "bus", "class", "adrs", "api"]

    def _assert(self, words, stems, label):
        bad = [(w, s) for w in words for s in stems(w)
               if s[:3] != w[:3]]
        self.assertEqual(bad, [], f"{label}: {len(bad)} stem(s) do not share "
                                  f"the first three characters of their word, "
                                  f"so the _match prefilter would skip a real "
                                  f"match: {bad[:10]}")

    def test_the_constructed_table_holds_for_both_routers(self):
        self._assert(self.TABLE, AL._stems, "agent-lint table")
        self._assert(self.TABLE, GL._stems, "graph-lint table")

    def test_the_real_vocabulary_holds(self):
        vocab = set()
        for a in AGENTS:
            n, tr, d = AL._token_sets(a)
            vocab |= set(n) | set(tr) | set(d)
        self._assert(sorted(vocab), AL._stems, "roster vocabulary")
        self._assert(sorted(load_when_vocab()), GL._stems, "load_when vocabulary")


class StemCollisions(unittest.TestCase):
    """A stemmer's only real risk is a FALSE merge.

    Reducing `nodes` to `node` widens reach, which is the point. Reducing `rat`
    and `rating` to one stem widens it wrongly, and nothing mechanical tells the
    two apart — `pin`/`pinned` and `rat`/`rating` are the same shape. So the
    reviewed groups live in a fixture, and a group that is not in it fails here
    until a person looks at it and puts it there on purpose. The fixture is the
    review; this test is only what makes skipping the review impossible.
    """

    FIXTURE = ROOT / "tests" / "fixtures" / "router" / "stem-collisions.json"

    @staticmethod
    def _groups(vocab, stems):
        g = {}
        for t in vocab:
            for s in stems(t):
                g.setdefault(s, set()).add(t)
        return {tuple(sorted(v)) for v in g.values() if len(v) > 1}

    def setUp(self):
        self.reviewed = json.loads(self.FIXTURE.read_text(encoding="utf-8"))

    def _check(self, key, observed):
        allowed = {tuple(g) for g in self.reviewed[key]}
        new = sorted(observed - allowed)
        gone = sorted(allowed - observed)
        self.assertEqual(new, [], f"{len(new)} unreviewed stem collision(s) in "
                                  f"{key}: {new} — check each is one word's "
                                  f"inflections, then add it to {self.FIXTURE.name}")
        self.assertEqual(gone, [], f"{len(gone)} reviewed collision(s) in {key} "
                                   f"no longer occur: {gone} — remove them, so "
                                   f"the file stays a review and not a graveyard")

    def test_agent_roster_collisions_are_reviewed(self):

        """Asserts SPEC-0002 A_STEM_COLLISION_IS_REVIEWED_BEFORE_IT_SHIPS."""
        vocab = set()
        for a in AGENTS:
            n, tr, _d = AL._token_sets(a)
            vocab |= set(n) | set(tr)
        self._check("agent_roster", self._groups(vocab, AL._stems))

    def test_load_when_collisions_are_reviewed(self):

        """Asserts SPEC-0002 A_STEM_COLLISION_IS_REVIEWED_BEFORE_IT_SHIPS."""
        vocab = set()
        for pat in ["protocols/*.md", "skills/*/SKILL.md", "skills/*.md",
                    "agents/*.md", "core/method/*.md"]:
            for p in sorted(ROOT.glob(pat)):
                text = p.read_text(encoding="utf-8", errors="replace")
                m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
                if not m:
                    continue
                blk = re.search(r"^load_when:\s*\n((?:\s*-\s.*\n)+)", m.group(1), re.M)
                if blk:
                    for line in re.findall(r'^\s*-\s*"?(.*?)"?\s*$', blk.group(1), re.M):
                        vocab |= GL._tokens(line)
        vocab = {t for t in vocab
                 if t not in GL.STOPWORDS and len(t) > 2 and t.isalpha()}
        self._check("load_when", self._groups(vocab, GL._stems))


def _bless():
    """Rewrite the reviewed-collision fixture from the tree, deliberately.

    `python3 tests/test_router_reach.py --bless`. It lives here rather than in
    a separate script so the file the test reads and the file a person
    regenerates are produced by the same code — a second implementation of the
    derivation is how a review file starts describing a tree that no longer
    exists. Blessing is not reviewing: read the diff.
    """
    groups = StemCollisions._groups
    vocab = set()
    for a in AGENTS:
        n, tr, _d = AL._token_sets(a)
        vocab |= set(n) | set(tr)
    agent_roster = sorted(groups(vocab, AL._stems))

    lw_vocab = set()
    for pat in ["protocols/*.md", "skills/*/SKILL.md", "skills/*.md",
                "agents/*.md", "core/method/*.md"]:
        for p in sorted(ROOT.glob(pat)):
            text = p.read_text(encoding="utf-8", errors="replace")
            m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
            if not m:
                continue
            blk = re.search(r"^load_when:\s*\n((?:\s*-\s.*\n)+)", m.group(1), re.M)
            if blk:
                for line in re.findall(r'^\s*-\s*"?(.*?)"?\s*$', blk.group(1), re.M):
                    lw_vocab |= GL._tokens(line)
    lw_vocab = {t for t in lw_vocab
                if t not in GL.STOPWORDS and len(t) > 2 and t.isalpha()}
    load_when = sorted(groups(lw_vocab, GL._stems))

    path = StemCollisions.FIXTURE
    data = json.loads(path.read_text(encoding="utf-8"))
    data["agent_roster"] = [list(g) for g in agent_roster]
    data["load_when"] = [list(g) for g in load_when]
    path.write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8")
    print(f"blessed {path}: {len(agent_roster)} agent-roster groups, "
          f"{len(load_when)} load_when groups — now read the diff")


if __name__ == "__main__":
    if "--bless" in sys.argv:
        _bless()
    else:
        unittest.main(verbosity=2)
