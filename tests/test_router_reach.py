#!/usr/bin/env python3
"""The two routers must be reachable by the word forms people actually type.

Both routers score a task's words against a roster's vocabulary. This suite
derives its vocabulary from the roster and the node set on every run.
"""
import importlib.util
import pathlib
import re
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent


def _load(rel, name):
    """Load from source text: a stale .pyc can match on (mtime, size)."""
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
    """A route that turns on the tense of one word is not a route."""

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
    """No routing vocabulary may be unreachable by its own plural."""

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
    """`_match` skips a token whose first three characters match none of the
    term's stems' first three; sound only while every stem starts with w[:3]."""

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


class RoutersScoreAlike(unittest.TestCase):
    """agent-lint _tokens/_match and graph-lint _split_terms/_strength agree.

    A fragment of a compound (split on -, / or .) is weak evidence (1); a
    standalone word or the whole compound is full strength (2).
    """

    SUPPLY = "assess the supply{}chain and secrets handling risk"
    # (task text, term, strength, routers); "id" scores a node id's own segment.
    ROWS = [
        ("the security review process", "security", 2, "both"),
        ("delegation triggers here", "delegate", 1, "both"),
        (SUPPLY.format("-"), "chain", 1, "both"),
        (SUPPLY.format("/"), "chain", 1, "both"),
        (SUPPLY.format("."), "chain", 1, "both"),
        (SUPPLY.format("-"), "supply-chain", 2, "graph"),
        (SUPPLY.format("/"), "supply/chain", 2, "graph"),
        (SUPPLY.format("."), "supply.chain", 2, "graph"),
        ("expertise.ef-core", "ef-core", 2, "id"),
    ]

    def test_routers_score_alike(self):
        for text, term, want, routers in self.ROWS:
            with self.subTest(text=text, term=term):
                whole, frag = GL._split_terms(text, keep_path_segments=routers == "id")
                self.assertEqual(GL._strength(term, whole, frag), want, "graph-lint")
                if routers == "both":
                    self.assertEqual(AL._match(term, AL._tokens(text)), want,
                                     "agent-lint")


if __name__ == "__main__":
    unittest.main(verbosity=2)
