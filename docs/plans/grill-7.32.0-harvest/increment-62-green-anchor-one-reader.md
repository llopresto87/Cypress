<!-- Increment 62 of `docs/plans/grill-7.32.0-harvest.md`; its §9 index row points here. -->

### Increment 62: GREEN: the code-anchor tool reads `repo:` through the one frontmatter reader
- Item: F (class P), a REFACTOR from the cycle 1 ruling pass
- Spec contracts: SPEC-0003/ANCHOR_RECORD_NAMES_EVERY_REPOSITORY (unchanged). Why: `tools/code-anchor.py` carries its own `repo:` reader (`repo_values()` and `REPO_VALUE`), one more reader of node frontmatter beside the byte-identical `frontmatter.py` copies. The placed tool sits in `docs/graph/` beside the placed `frontmatter.py` (`install.sh` places both there), and `tools/frontmatter.py` sits beside the seed's copy, so the same-directory load the other tools use is open to it. With one reader, the anchor governs the repositories the graph's own linters read from the same frontmatter
- Files touched: `tools/code-anchor.py` only: load `frontmatter.py` from the tool's own directory, as the graph linter loads it; `repo_values()` yields each string `repo:` value that `parse_file()` returns, and skips a node the reader refuses, as it skips an unreadable file today; `REPO_VALUE` goes; the docstring says where the reader comes from. No constant, text, Git call or exit path changes
- Tests to write (RED): none: a REFACTOR under increment 7's cases, with increment 56's fixture
- Behavior added: none on a graph `graph-lint.py` accepts, with one named edge: a `repo:` value followed by a comment after one space is read as the reader reads it (it strips a comment only after two spaces), where the tool's own reader cut it
- Gate: `bash tests/test-bound-hook.sh` green, every case in its state; `bash tests/test-tool-help.sh` green; `python3 tests/test_metadata_equivalence.py` green; the line count of `tools/code-anchor.py` falls. The cycle 2 mutation pass over this file runs after this increment
- Rollback path: revert `tools/code-anchor.py`
- Effort: low
- Phase: GREEN
- Depends on: increment 56
