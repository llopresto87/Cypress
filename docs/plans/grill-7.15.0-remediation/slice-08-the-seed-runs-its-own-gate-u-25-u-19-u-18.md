### Slice 8 — The seed runs its own gate (U-25, U-19, U-18)

**Tier:** T2. **Invariant:** V7.

There was no CI of any kind. `.github/workflows/gate.yml` runs the strict gate on
`ubuntu-latest` and `macos-latest` with `fail-fast: false`, deliberately on two
platforms because the placement contract is mostly about symlink semantics and
that is where the platforms differ. No `pip install` step, which is the contract
rather than an omission: a gate that needed a package would mean something in the
tree had broken the no-third-party rule.

- **U-19** — README claimed "the same `agent-lint.py` CI gate" while no CI
  existed. It now distinguishes what `install.sh` places (the linter) from what
  an adopting project must wire (running it on push).
- **U-18** — README and DOCUMENTATION called `produced_by` attribution
  *fail-closed*; ADR-0003 classifies it **detective (post-hoc)** and
  `protocols/deliver.md` records the `Stop` hook deliberately unwired. Restated
  in both, propagating ADR-0003's hard/soft/detective vocabulary. **The hook was
  not wired** — its promotion criterion ("until this plant's real deliveries
  carry `produced_by`") cannot be met in the seed, which has no deliveries.
  Fixing the sentence was the correct move; fixing the code to match the sentence
  would have promoted a control to make a README true.

### Verification at this boundary

`bash tests/run.sh` → **EXIT=0**, now 21 shell suites plus the Python gates.
Kernel 7 564 bytes, byte-identical. `tests/test_agent_lint.py`: 53 tests
(45 ported + 8 new routing-contract regressions), runs without `pytest`.

Every fix in slices 4–8 was reverted in place and observed red before being
restored, except the legal-corpus page count, whose limit is recorded in
slice 3.
