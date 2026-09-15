#!/usr/bin/env python3
"""Brainstorm has two audiences, and the graph can reach both.

At d7588e2 the seed had one brainstorm and it could not finish without a user:
`brainstorm.entry-and-exit` requires explicit confirmation ("yes", "looks
right"), "not assumed from silence". So CYPRESS generating and comparing
options AGAINST ITSELF — the divergent step before `grill` fills its options
table and before an ADR records a rejected alternative — had no home anywhere.

The seam is real rather than stylistic, and this suite holds it open from both
ends: the socratic mode must keep the user (and now reach them through the
humanizer), and the internal mode must be able to finish without one.
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def node(path):
    text = (ROOT / path).read_text(encoding="utf-8")
    head, body = text[4:text.index("\n---\n", 3)], text[text.index("\n---\n", 3) + 5:]
    fm, cur = {}, None
    for line in head.splitlines():
        if re.match(r"^\s+-\s+", line) and cur:
            fm[cur].append(line.split("-", 1)[1].strip().strip('"'))
            continue
        kv = re.match(r"^([A-Za-z_]+):\s*(.*)$", line)
        if kv:
            k, v = kv.group(1), kv.group(2).strip()
            fm[k] = v if v else []
            cur = None if v else k
    return fm, body


class BothModesExist(unittest.TestCase):
    def test_each_mode_is_a_node(self):
        for p in ("skills/brainstorm-socratic/SKILL.md", "skills/brainstorm-internal/SKILL.md"):
            self.assertTrue((ROOT / p).is_file(), f"{p} is not a node")

    def test_the_protocol_reaches_both(self):
        fm, _ = node("protocols/brainstorm.md")
        edges = set(fm.get("requires", [])) | set(fm.get("peers", []))
        for want in ("skill.brainstorm-socratic", "skill.brainstorm-internal"):
            self.assertIn(want, edges,
                          f"protocol.brainstorm cannot reach {want} — a mode the "
                          f"router cannot traverse to is a mode nobody enters")

    def test_mode_selection_has_exactly_one_home(self):
        homes = [p for p in ROOT.glob("**/*.md")
                 if "brainstorm.mode-selection" in p.read_text(encoding="utf-8", errors="replace")
                 and "docs/plans" not in str(p) and "CHANGELOG" not in p.name]
        owners = [p for p in homes if re.search(r"^\s+-\s+brainstorm\.mode-selection\s*$",
                                                p.read_text(encoding="utf-8"), re.M)]
        self.assertEqual(len(owners), 1,
                         f"brainstorm.mode-selection must be owned exactly once, found {owners}")


class TheSeamIsReal(unittest.TestCase):
    """Characterization: the two modes differ where it matters, not by name."""

    def test_the_socratic_mode_keeps_the_user(self):
        _, body = node("skills/brainstorm-socratic/SKILL.md")
        self.assertTrue("question" in body.lower(),
                        "the socratic mode lost its questioning technique")

    def test_the_internal_mode_can_finish_without_a_user(self):
        """The property is the EXIT, not the vocabulary.

        An earlier version of this test banned the string "ask the user" from
        the internal skill, and failed on the sentence "this mode ... does not
        ask the user". A word ban cannot tell a rule from a cross-reference, so
        it tested the prose instead of the contract. What actually matters is
        that the internal mode's exit does not wait for a person.
        """
        _, body = node("skills/brainstorm-internal/SKILL.md")
        exit_section = body.lower().split("## exit conditions", 1)
        self.assertEqual(len(exit_section), 2,
                         "the internal mode declares no exit conditions")
        tail = exit_section[1]

        # A positive regex for the property is not enough: `without.{0,20}
        # confirmation` matched "Never exit WITHOUT user CONFIRMATION", i.e. the
        # exact inversion, and an adversarial mutation walked through it. The
        # only safe shape here is to forbid the negation FIRST, over the whole
        # section, then require the affirmative.
        for banned in (r"never exit without", r"wait until they approve",
                       r"wait for .{0,30}confirmation", r"the user has confirmed",
                       r"silence is not approval", r"until the owner"):
            self.assertIsNone(
                re.search(banned, tail),
                f"the internal mode's exit waits for a user ({banned!r}) — then "
                f"it is the socratic mode with extra steps")
        self.assertRegex(
            tail, r"no user confirmation is required",
            "the internal mode's exit must say in those words that no user "
            "confirmation is required; anything softer has already been shown "
            "to admit its own negation")

    def test_the_question_cap_is_a_rule_in_one_mode_and_a_reference_in_the_other(self):
        """`nine` may APPEAR in the internal skill; it may not BIND there."""
        _, soc = node("skills/brainstorm-socratic/SKILL.md")
        _, internal = node("skills/brainstorm-internal/SKILL.md")
        self.assertIn("nine", soc.lower(), "the socratic mode lost its question cap")
        method = internal.lower().split("## the method", 1)
        self.assertEqual(len(method), 2, "the internal mode declares no method")
        self.assertIsNone(
            re.search(r"\bnine\b|\b9\b", method[1]),
            "the internal mode's METHOD imposes a question cap — there is nobody "
            "to question, so a cap there is copied machinery, not a rule "
            "(naming it elsewhere to disclaim it is fine)")
        self.assertRegex(
            internal.lower(), r"no cap|no questions",
            "the internal mode never says the cap does not apply to it")


class TheOwnerFacingModeIsReadable(unittest.TestCase):
    def test_socratic_declares_the_humanizer(self):
        fm, _ = node("skills/brainstorm-socratic/SKILL.md")
        edges = set(fm.get("requires", [])) | set(fm.get("peers", []))
        self.assertIn("skill.humanizer", edges,
                      "the one mode that puts a decision in front of a person does "
                      "not declare the skill that makes prose readable")


class TheInternalModeIsHonest(unittest.TestCase):
    def test_it_names_the_strawman_failure(self):
        _, body = node("skills/brainstorm-internal/SKILL.md")
        self.assertTrue(re.search(r"strawmen|strawman|straw man", body.lower()),
                         "a session brainstorming against itself generates one real "
                         "option and two strawmen; the skill that does not name that "
                         "failure does not prevent it")


if __name__ == "__main__":
    unittest.main(verbosity=2)
