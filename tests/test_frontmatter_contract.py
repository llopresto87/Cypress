#!/usr/bin/env python3
"""What the one frontmatter reader must DO, not merely that its copies agree.

`seed-lint`'s `check_frontmatter_reader_is_one_reader` holds four
byte-identical copies of `frontmatter.py` identical, and
`test_metadata_equivalence.py` holds the five consumers in agreement with each
other. Both are tautologies about sameness. Mutating all four copies the SAME
wrong way passed every one of the 42 gates, three times over:

  - dropping the nested mapping value, so a `plant:` block read as `{}`
  - widening the comment strip from `"  #"` to `" #"`, so
    `title: fix #42 in the parser` read as `fix`
  - `meta[key] =` -> `meta.setdefault(key, ...)`, so a duplicate key became
    first-wins and `status: draft` beat a later `status: active`

Each is one character or one word, each changes what a plant's metadata means,
and nothing in the tree could tell. Enforcement by sameness is not enforcement
by truth, and this file is the truth half: it asserts the reader's behaviour
against fixtures, so a wrong rule copied four times fails here even though it
satisfies the byte-identity check.

Stdlib unittest; no third-party imports.
"""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

SEED = Path(__file__).resolve().parent.parent
# Every published copy. The point is that they must all behave the same AND be
# right, so each is exercised rather than one standing in for the rest.
COPIES = (
    "templates/knowledge-graph/frontmatter.py",
    "integrations/claude-code/frontmatter.py",
    "tests/frontmatter.py",
    "tools/frontmatter.py",
)


def load(rel: str):
    path = SEED / rel
    spec = importlib.util.spec_from_file_location(f"fm_{rel.replace('/', '_')}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class FrontmatterContract(unittest.TestCase):
    """Each assertion runs against every copy."""

    def setUp(self):
        self.readers = [(rel, load(rel)) for rel in COPIES
                        if (SEED / rel).is_file()]
        self.assertGreaterEqual(
            len(self.readers), 2,
            "fewer than two copies of frontmatter.py found — this suite has "
            "stopped reaching them, and a clean result means nothing")

    def each(self, text):
        for rel, mod in self.readers:
            with self.subTest(copy=rel):
                yield rel, mod, text

    def test_a_nested_mapping_keeps_its_values(self):
        """`docs/graph/index.md`'s `plant:` block is the reason the promoted
        reader gained nesting at all. Dropping the value is invisible to every
        equivalence check, because no Python consumer reads `meta['plant']`
        today — which is exactly why it needs an assertion of its own."""
        text = ("---\nplant:\n  name: acme\n  legal_corpus: yes\n"
                "id: protocol.x\n---\nbody\n")
        for rel, mod, t in self.each(text):
            meta, _ = mod.parse(t, "probe.md")
            self.assertEqual(
                meta.get("plant"), {"name": "acme", "legal_corpus": "yes"},
                f"{rel}: the nested mapping lost its values")

    def test_a_hash_inside_a_value_is_content(self):
        """The comment strip is `"  #"` — TWO spaces — and the difference is a
        title. Widening it to `" #"` turns `fix #42 in the parser` into `fix`,
        silently, in every projection a plant ships."""
        text = "---\ntitle: fix #42 in the parser\n---\nbody\n"
        for rel, mod, t in self.each(text):
            meta, _ = mod.parse(t, "probe.md")
            self.assertEqual(meta.get("title"), "fix #42 in the parser",
                             f"{rel}: a single-space `#` was treated as a comment")

    def test_a_trailing_double_space_comment_is_stripped(self):
        """The other direction, so the assertion above is not satisfied by a
        reader that simply stopped stripping comments."""
        text = "---\ntier: 2  # the contained lane\n---\nbody\n"
        for rel, mod, t in self.each(text):
            meta, _ = mod.parse(t, "probe.md")
            self.assertEqual(meta.get("tier"), 2,
                             f"{rel}: the trailing comment was not stripped")

    def test_a_repeated_key_is_last_wins(self):
        """`meta[key] = ...` vs `meta.setdefault(key, ...)` is one word, and it
        decides which of two `status:` lines a spec is read as carrying."""
        text = "---\nstatus: draft\nstatus: active\n---\nbody\n"
        for rel, mod, t in self.each(text):
            meta, _ = mod.parse(t, "probe.md")
            self.assertEqual(meta.get("status"), "active",
                             f"{rel}: a repeated key became first-wins")

    def test_a_multi_line_value_is_refused(self):
        """The defect the consolidation existed to close: two readers raised
        and three dropped the continuation silently."""
        text = ("---\ndescription: one line\n  and a continuation\n---\nbody\n")
        for rel, mod, t in self.each(text):
            with self.assertRaises(mod.FrontmatterError,
                                   msg=f"{rel}: a continuation line was accepted"):
                mod.parse(t, "probe.md")

    def test_an_unterminated_block_is_refused(self):
        for rel, mod, t in self.each("---\nid: x\nno terminator here\n"):
            with self.assertRaises(mod.FrontmatterError):
                mod.parse(t, "probe.md")

    def test_quoting_protects_a_hash_and_a_bracket(self):
        text = "---\nname: \"a  # b\"\nlist: [one, two]\n---\nbody\n"
        for rel, mod, t in self.each(text):
            meta, _ = mod.parse(t, "probe.md")
            self.assertEqual(meta.get("name"), "a  # b",
                             f"{rel}: a quoted value was comment-stripped")
            self.assertEqual(meta.get("list"), ["one", "two"],
                             f"{rel}: an inline list did not parse")

    def test_integers_are_coerced_and_the_body_survives(self):
        text = "---\nmax_spawn_depth: 2\n---\n# Body\n\ntext\n"
        for rel, mod, t in self.each(text):
            meta, body = mod.parse(t, "probe.md")
            self.assertEqual(meta.get("max_spawn_depth"), 2,
                             f"{rel}: an integer was left as a string — the "
                             f"roster lint checks it as an int")
            self.assertEqual(body, "# Body\n\ntext\n",
                             f"{rel}: the body was altered")

    def test_a_block_list_parses(self):
        text = "---\nowns:\n  - rule.one\n  - rule.two\n---\nbody\n"
        for rel, mod, t in self.each(text):
            meta, _ = mod.parse(t, "probe.md")
            self.assertEqual(meta.get("owns"), ["rule.one", "rule.two"],
                             f"{rel}: a block list did not parse")


if __name__ == "__main__":
    unittest.main(verbosity=1)
