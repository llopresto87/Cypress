### Slice 11 — Every gate declares what it can still miss (U-30, U-33)

**Tier:** T2.

`tools/gate-registry.py` is the machine-readable gate registry, and it is
**derived rather than maintained**: `--lint` parses `tests/run.sh` and refuses in
both directions — a step with no entry, and an entry for a step that no longer
runs ("a documented gate that does not run is the plainest false green there
is"). Both directions were proved to fail. It is wired as the gate's last step,
and it classifies itself.

Each gate declares what it asserts, what it **reads**, and the
false-green class it remains exposed to: `coverage`, `scope`, `self-reference`,
`representation`, `evidence`, `semantic`, or `none`.

The measured distribution at the time of writing, which is the finding
(`gate-registry.py --summary` is the live number; the ledger deliberately does
not become a second home for it):

| What they read | Gates |
|---|---|
| fixtures only | **14** |
| the real tree | 11 |
| a temp install | 6 |

| False green still possible | Gates |
|---|---|
| none | 12 |
| **scope** (proves a linter works, says nothing about the shipped tree) | **11** |
| coverage | 2 |
| semantic | 2 |
| evidence | 1 |
| representation | 1 |
| self-reference | 1 |

Phase 0 estimated six fixtures-only suites by reading `run.sh`. Deriving it
mechanically found **fourteen**. "`tests/run.sh` exits 0" and "the seed complies
with everything it checks" are different sentences, and the gap between them is
now a number rather than an impression.

The registry's own entry is classified `semantic`, honestly: it checks that a
classification *exists*, not that it is true. An entry wrongly claiming
`real-tree` passes. The entries are prose an author must keep honest; this gate
only keeps them present and in sync with the runner.
