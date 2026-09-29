## 7.32.1 — the install preflight checks the trees it writes, not the whole project (2026-09-29)

`install.sh` refused to run on a plant whose Docker builds had left root-owned
directories under `node_modules/`, `.next/`, a database volume or a nested
checkout. Its preflight walked every directory beneath the project root and
refused if any was unwritable, though the installer never opens those trees. A
graft of such a plant needed a chown that nothing in the seed asked for, or a
copy of the plant to install into.

The preflight now walks only the trees a run writes: `docs/graph`, `.cypress`,
each selected adapter's top directory, and the four `.github` subdirectories the
Copilot adapter uses. The roots come from `adapter_dirs()`, so a new adapter is
covered by its own entry. The guards stay where they matter: a read-only
directory or an escaping symlink inside a written tree still refuses before the
first byte. SPEC-0001 gains `PREFLIGHT_SCOPED_TO_WRITTEN_TREES`, pinned by
`case_unrelated_trees` in `tests/test-install-adoption.sh`, which was red
against the old walk. The spec's changelog records the corrected sentence.
