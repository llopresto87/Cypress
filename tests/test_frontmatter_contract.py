#!/usr/bin/env python3
"""What the one frontmatter reader must do, asserted on the canonical copy.

seed-lint FRONTMATTER_COPIES keeps the other copies byte-identical to it.
tools/status-register.py keeps its own tolerant reader; the table at the end
holds it to the same facts. Stdlib unittest.
"""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

SEED = Path(__file__).resolve().parent.parent


def load(rel: str, name: str):
    spec = importlib.util.spec_from_file_location(name, SEED / rel)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


# Loaded at module level: an import failure errors the file.
FM = load("templates/knowledge-graph/frontmatter.py", "_fm_contract")
SR = load("tools/status-register.py", "_fm_status_register")


def parse(text):
    return FM.parse(text, "probe.md")[0]


class FrontmatterContract(unittest.TestCase):

    def test_a_nested_mapping_keeps_its_values(self):
        text = ("---\nplant:\n  name: acme\n  legal_corpus: yes\n"
                "id: protocol.x\n---\nbody\n")
        self.assertEqual(parse(text).get("plant"),
                         {"name": "acme", "legal_corpus": "yes"})

    def test_a_hash_inside_a_value_is_content(self):
        text = "---\ntitle: fix #42 in the parser\n---\nbody\n"
        self.assertEqual(parse(text).get("title"), "fix #42 in the parser")

    def test_a_trailing_double_space_comment_is_stripped(self):
        text = "---\ntier: 2  # the contained lane\n---\nbody\n"
        self.assertEqual(parse(text).get("tier"), 2)

    def test_a_repeated_key_is_last_wins(self):
        text = "---\nstatus: draft\nstatus: active\n---\nbody\n"
        self.assertEqual(parse(text).get("status"), "active")

    def test_a_multi_line_value_is_refused(self):
        text = "---\ndescription: one line\n  and a continuation\n---\nbody\n"
        with self.assertRaises(FM.FrontmatterError):
            parse(text)

    def test_an_unterminated_block_is_refused(self):
        with self.assertRaises(FM.FrontmatterError):
            parse("---\nid: x\nno terminator here\n")

    def test_quoting_protects_a_hash_and_a_bracket(self):
        meta = parse("---\nname: \"a  # b\"\ntitle: \"a quoted title\"\n"
                     "list: [one, two]\n---\nbody\n")
        self.assertEqual(meta.get("name"), "a  # b")
        self.assertEqual(meta.get("title"), "a quoted title")
        self.assertEqual(meta.get("list"), ["one", "two"])

    def test_integers_are_coerced_and_the_body_survives(self):
        meta, body = FM.parse("---\nmax_spawn_depth: 2\n---\n# Body\n\ntext\n",
                              "probe.md")
        self.assertEqual(meta.get("max_spawn_depth"), 2)
        self.assertEqual(body, "# Body\n\ntext\n")

    def test_a_block_list_parses(self):
        text = "---\nowns:\n  - rule.one\n  - rule.two\n---\nbody\n"
        self.assertEqual(parse(text).get("owns"), ["rule.one", "rule.two"])


class StatusRegisterReader(unittest.TestCase):
    """status-register reads what frontmatter.py reads; None where it refuses."""

    ROWS = [
        "---\nid: p\ntitle: Plain Value\n---\nbody\n",
        "---\nid: c\nnote: ratio 3:1 acceptable\n---\nbody\n",
        "---\nid: e\nnotes:\ntitle: After Empty\n---\nbody\n",
        "---\nid: l\ntags:\n  - alpha\n  - beta\n  - gamma\n---\nbody\n",
        "---\nid: b\ncan_delegate: true\n---\nbody\n",
        "no frontmatter here\njust body text\n",
        "---\nid: x\ntitle: Unterminated\n",
    ]

    def test_status_register_reads_like_the_shared_reader(self):
        for text in self.ROWS:
            with self.subTest(text=text):
                try:
                    want = parse(text)
                except FM.FrontmatterError:
                    want = None
                got = SR.parse_frontmatter(text)
                self.assertEqual(got and got[0], want)

    def test_the_unshared_reader_is_named_and_still_tolerant(self):
        got = SR.parse_frontmatter("---\nid: m\ndescription: This starts here\n"
                                   "  and continues indented.\n---\nbody\n")
        self.assertEqual(got[0]["description"], "This starts here")


if __name__ == "__main__":
    unittest.main(verbosity=1)
