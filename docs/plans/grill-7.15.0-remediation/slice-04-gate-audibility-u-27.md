### Slice 4 — Gate audibility (U-27)

**Tier:** T2. **Invariant:** V5.

Three linters answered an unreadable input with a bare `continue`: no
diagnostic, no effect on exit status. A file the gate could not read was
indistinguishable from a clean one. Each now names the path and the reason and
routes the fault into the findings list the tool already had, so an unread input
fails the run rather than being absent from it.

Pinned by `tests/test-lint-audibility.sh` (two cases per linter, wired into the
gate). Red-before-green proved by reverting each fix in turn. The spec-lint
revert is the instructive one: it still exited 1 by an unrelated path, and the
test caught it anyway because it asserts the *diagnostic names the path*, not
merely that the exit code is non-zero.
