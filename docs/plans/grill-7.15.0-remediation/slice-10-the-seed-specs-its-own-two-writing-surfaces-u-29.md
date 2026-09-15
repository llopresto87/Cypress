### Slice 10 — The seed specs its own two writing surfaces (U-29)

**Tier:** T3. Kernel §3.1 says code without a spec is in remediation mode, and
the seed had no specs of its own. Two now exist in `docs/specs/`, covering the
two surfaces where the seed either writes into somebody else's repository or
makes a quantitative claim about itself:

- **SPEC-0001-install-placement** — 14 contracts encoding S1–S6, M1–M9, K1–K6,
  each mapped in §10 to a real test case that exists and is green.
- **SPEC-0002-routing-contract** — 11 contracts encoding X1, X2, X6 and
  abstention semantics, each mapped to a named test in `tests/test_agent_lint.py`
  (every name verified present).

Both carry an honest §11. SPEC-0001 records that `PARTIAL_CORPUS` has no
behavioural test because `place_tree` never fails partway; SPEC-0002 records
that the confidence bands are not calibrated per specialist — HIGH is a property
of the scores, not a measured correctness rate — and that the paraphrase floor
is a ratchet rather than a target.

**Recorded exemption (CLAUDE.md).** The corpora are deliberately unspecced: a
corpus page is transcribed knowledge, not behaviour, its contract is its
`_schema.md` plus `legal-lint.py`, and a §4 Given/When/Then over a statute would
restate the statute. The exemption is bounded to the corpora and does not extend
to any code path; a third spec is owed the moment another surface starts writing
into a plant or reporting a number about itself.
