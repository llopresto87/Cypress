### Slice 16 — The preflight's own second home (found while reviewing slice 13)

**Tier:** T2.

The D1 preflight worked from `adapter_dirs()`, a hand-written list of the
directories each adapter creates. That list is a second home for something the
`install_*` functions already know, and it drifted **within the same release
that introduced it**: `.github/hooks` was missing, so a target holding a regular
file at that path still wrote **195 files** and then died on the very raw
`mkdir: Not a directory` the preflight exists to replace.

Patching the list would have fixed the instance and left the class. The list is
incomplete *by construction*: it also does not enumerate the fourteen per-skill
leaves under `.claude/skills/`, and it could not without restating the skill
roster in a second place.

So the contract is layered, and each layer now guarantees something the test
states separately:

- `preflight_destinations()` refuses the **declared** areas before any write —
  nothing on disk, every offending path named at once.
- `ensure_dir()` is the floor under everything else: whatever the list forgets
  still fails with this tool's own error naming the path, instead of a raw shell
  message from three frames inside `place_tree`. Every destination `mkdir -p` in
  the installer now goes through it.

`tests/test-install-adoption.sh` asserts both halves and the list's honesty in
the other direction too — every directory `adapter_dirs()` *declares* must be one
the adapter really creates, or the preflight refuses over paths that do not
matter. A file blocking a declared area writes nothing; a file blocking an
undeclared depth still fails cleanly and names itself.

This is the second time in this remediation that a list of destinations proved
to be the defect rather than the fix — the first was `test-install-placement.sh`,
which is why that suite *discovers* the destination set from a real install
instead of listing it.
