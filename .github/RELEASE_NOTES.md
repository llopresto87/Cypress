## 8.1.1 — the gate checkout fetches full history (2026-10-07)

The CI gate cloned the seed without history or tags, so two tests that
read the v7.36.0 engine failed on GitHub since 7.37.0. The gate now
fetches the full history, and seed-lint requires it.

### Gate checkout

- `.github/workflows/gate.yml` fetches full history (`fetch-depth: 0`) on
  checkout, so gate tests can read git history and tags, such as
  `git show v7.36.0:...`.
- `tests/seed-lint.py` requires the full-history checkout, with
  `tests/test-seed-lint.sh` as its RED/GREEN test.
