#!/usr/bin/env python3
"""A repeated operation has an author, and the close-out still spawns once.

At d7588e2 `canonize` catalogued "any durable tool **it produced**" and *it* was
never named. `protocols/toolcraft.md` owned the doctrine and declared it "never
spawns separately". So the graph believed tools were being authored and named
nobody who authored them — and in practice the operation got rewritten by hand
each session, which is exactly the failure `rule.toolcraft` exists to prevent,
reproduced inside the node that prevents it.

The fix splits three things that were one node: the RULE (doctrine every
session reads), the AUTHOR (a specialist spawned mid-task), and BOUNDED
EXECUTION (an execution discipline that was only filed there because toolcraft
was the nearest protocol).

The dangerous edit is the rule's home. `seed-lint` enforces the eight `rule.*`
keys in exactly their mapped homes, so this suite checks the invariant that
protects the move rather than restating the map.
"""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEARCH = ("core", "protocols", "skills", "agents", "templates")


def owners_of(fact):
    """Every machinery node whose `owns:` list contains `fact`."""
    out = []
    for d in SEARCH:
        for p in (ROOT / d).rglob("*.md"):
            text = p.read_text(encoding="utf-8", errors="replace")
            if re.search(rf"^\s+-\s+{re.escape(fact)}\s*$", text, re.M):
                out.append(p.relative_to(ROOT).as_posix())
    return out


class TheRuleKeepsExactlyOneHome(unittest.TestCase):
    def test_rule_toolcraft_is_owned_once(self):
        self.assertEqual(len(owners_of("rule.toolcraft")), 1,
                         f"rule.toolcraft owners: {owners_of('rule.toolcraft')}")

    def test_the_linter_map_points_at_that_home(self):
        src = (ROOT / "tests" / "seed-lint.py").read_text(encoding="utf-8")
        m = re.search(r'"rule\.toolcraft":\s*"([^"]+)"', src)
        self.assertIsNotNone(m, "seed-lint.py no longer maps rule.toolcraft")
        self.assertEqual([m.group(1)], owners_of("rule.toolcraft"),
                         "the rule map and the node that owns the fact disagree")

    def test_the_rule_is_not_owned_by_an_agent(self):
        """A kernel rule binds every session.

        Seven of the eight live in protocols and one in a skill. A rule whose
        only home is a specialist's charter is invisible to any session that
        never spawns that specialist — so the doctrine may move, but not into
        `agents/`.
        """
        for home in owners_of("rule.toolcraft"):
            self.assertFalse(home.startswith("agents/"),
                             f"rule.toolcraft lives in {home}; a kernel rule may "
                             f"not have a specialist charter as its only home")


class TheAuthorExists(unittest.TestCase):
    def test_the_tool_smith_is_a_routable_agent(self):
        p = ROOT / "agents" / "tool-smith.md"
        self.assertTrue(p.is_file(), "agents/tool-smith.md does not exist")
        head = p.read_text(encoding="utf-8").split("\n---\n")[0]
        for key in ("routing_triggers", "prevents", "id: agent.tool-smith"):
            self.assertIn(key, head, f"tool-smith is missing {key!r}")

    def test_the_close_out_names_the_producer(self):
        """Naming the agent is not enough — a disclaimer names it too.

        `assertIn("tool-smith", ...)` passed on "No producer is named … (An
        earlier draft proposed a tool-smith; it was dropped.)", which reinstates
        the exact hole this slice closes. So forbid the disclaimers, then
        require the positive statement.
        """
        # THE STRUCTURAL HALF. A prose assertion is invertible: "It is false
        # that the producer is `agent.tool-smith`" contains the required phrase
        # and was demonstrated to pass. A frontmatter edge cannot be negated by
        # inserting words, so the load-bearing check is the edge; the prose
        # check below is kept as a weaker companion, not as the guarantee.
        for node, want in (("protocols/canonize.md", "agent.tool-smith"),
                           ("agents/tool-smith.md", "protocol.canonize")):
            head = (ROOT / node).read_text(encoding="utf-8").split("\n---\n", 1)[0]
            self.assertIsNotNone(
                re.search(rf"^\s+-\s+{re.escape(want)}\s*$", head, re.M),
                f"{node} declares no graph edge to {want} — the mid-task "
                f"authoring -> close-out cataloging handoff is prose on both "
                f"sides and an edge on neither, so the router cannot traverse it")

        text = (ROOT / "protocols" / "canonize.md").read_text(encoding="utf-8")
        low = text.lower()
        for banned in ("no producer is named", "it was dropped",
                       "whoever notices", "an earlier draft proposed"):
            self.assertNotIn(banned, low,
                             f"canonize disclaims its producer ({banned!r})")
        self.assertRegex(
            low, r"the producer is `?agent\.tool-smith`?",
            "canonize must state in those words who produced the tool it "
            "catalogs; merely mentioning the agent has been shown to pass "
            "while the producer is disclaimed")

    def test_the_golden_corpus_routes_to_it(self):
        """Count the ROWS, not the string.

        Deleting all three `…\ttool-smith` rows left the section comment
        `# --- tool-smith ---` behind, which satisfied a substring check while
        the agent became measured by nothing.
        """
        rows = [l for l in (ROOT / "agents" / "_routes.golden.tsv")
                .read_text(encoding="utf-8").splitlines()
                if l.strip() and not l.startswith("#")]
        expecting = [l for l in rows if l.split("\t")[1:2] == ["tool-smith"]]
        self.assertGreaterEqual(
            len(expecting), 3,
            f"only {len(expecting)} golden row(s) expect tool-smith — an agent "
            f"the corpus does not exercise is measured by nothing, and the "
            f"section comment alone is not a measurement")


class TheScopeBoundaryIsStated(unittest.TestCase):
    def test_the_charter_refuses_seed_machinery(self):
        """The boundary is the whole defence against a 'write me a script' route."""
        text = (ROOT / "agents" / "tool-smith.md").read_text(encoding="utf-8").lower()
        # A loose negation regex matched "You do NOT need the SEED's permission
        # to build one" — a sentence asserting the opposite of the boundary.
        for banned in ("do not need the seed", "anywhere in the repository",
                       "linters and graph machinery included",
                       "build whatever tooling is asked"):
            self.assertNotIn(banned, text,
                             f"the charter invites out-of-scope work ({banned!r})")
        self.assertIn("out of scope, and refuse it", text,
                      "the charter has no explicit refusal clause")
        for required in ("linters", "graph tooling", "plant"):
            self.assertIn(required, text,
                          f"the scope boundary no longer names {required!r}")


class TheCloseOutStillSpawnsOnce(unittest.TestCase):
    """Canonize's single-spawn rule is NARROWED to cataloging, never reversed."""

    def test_canonize_still_forbids_a_second_cataloging_spawn(self):
        text = (ROOT / "protocols" / "canonize.md").read_text(encoding="utf-8").lower()
        self.assertTrue(
            re.search(r"no separate toolcraft spawn|there is no separate .{0,30}spawn|spawn the docs-librarian once", text),
            "canonize lost its single-close-out-spawn rule")

    def test_authoring_is_not_a_close_out_step(self):
        text = (ROOT / "protocols" / "canonize.md").read_text(encoding="utf-8").lower()
        # Active voice alone is not the property. "the tool-smith is spawned
        # here, as a second close-out spawn" passed the old check.
        for banned in (r"spawn[s]?\b[^.]{0,60}tool-smith",
                       r"tool-smith[^.]{0,60}\bis spawned\b",
                       r"tool-smith[^.]{0,60}\bspawn(ed)? here\b",
                       r"second close-out spawn"):
            self.assertIsNone(
                re.search(banned, text),
                f"canonize spawns the tool-smith ({banned!r}) — authoring "
                f"happens mid-task, and a second close-out spawn is the "
                f"coordination waste canonize forbids")
        self.assertRegex(text, r"mid-task",
                         "canonize no longer says where authoring happens")


class BoundedExecutionIsRehomed(unittest.TestCase):
    def test_it_is_owned_exactly_once_and_not_by_the_author(self):
        owners = owners_of("toolcraft.bounded-execution")
        self.assertEqual(len(owners), 1, f"owners: {owners}")
        self.assertFalse(owners[0].startswith("agents/"),
                         "bounded execution is an execution discipline every "
                         "session needs, not a specialist's charter")


class TheRetiredProtocolLeavesNoDanglingEdge(unittest.TestCase):
    def test_nothing_points_at_protocol_toolcraft(self):
        bad = []
        for d in SEARCH:
            for p in (ROOT / d).rglob("*.md"):
                if "protocol.toolcraft" in p.read_text(encoding="utf-8", errors="replace"):
                    bad.append(p.relative_to(ROOT).as_posix())
        self.assertEqual(bad, [], f"dangling protocol.toolcraft edge in: {bad}")

    def test_the_manifest_does_not_ship_it(self):
        m = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        files = [e.get("file", "") for v in m.values() if isinstance(v, list)
                 for e in v if isinstance(e, dict)]
        self.assertNotIn("protocols/toolcraft.md", files)


if __name__ == "__main__":
    unittest.main(verbosity=2)
