### Slice 14 — Five parsers, one input table (U-31, U-32)

**Tier:** T3.

One responsibility — parse this repo's YAML-subset frontmatter — has **five**
implementations (`agent-lint.py`, `graph-lint.py`, `seed-lint.py`,
`status-register.py`, `growth-audit.py`), plus the router's tokenizer in two.
That contradicts one-home-per-fact at the executable level.

**Why they were not consolidated.** Each of these tools installs into a plant as
a *standalone* file. A shared import would mean installing another file, which
changes the set of files every plant receives — an owner decision, and one not
required by the defect. The doctrine's own list of remedies includes a
**mechanical equivalence test**, which is what landed:
`tests/test_metadata_equivalence.py`, 17 tests, driving all five implementations
over one input table by loading them from disk rather than restating their logic
(a sixth implementation would have been the worst outcome). Proved to be a real
gate by breaking a copy of one parser and watching exactly one test fail.

**Eight divergences found. Two of them matter.**

The five split into a *structured trio* (`agent-lint`, `graph-lint`,
`status-register`) that normalizes scalars, and a *tolerant duo* (`seed-lint`,
`growth-audit`) that captures values with a bare regex and never interprets
them. The trio parses inline lists, strips trailing `# comment`, types integers
and strips quotes; the duo does none of it, and strips only double quotes inside
block lists — so `- "one"` loses its quotes and `- 'two'` keeps them.

- **D-6 — silent truncation.** A `description:` followed by a plain indented
  continuation is a hard `LintError` in `agent-lint` and `graph-lint`, and is
  **silently accepted with the continuation dropped** by `status-register`,
  `growth-audit` and `seed-lint`. The same malformed file is rejected by two
  tools and quietly truncated by three, with no diagnostic. This is the U-27
  defect class — an input the tool could not fully read, reported as fine —
  surviving in a different form.
- **D-8 — the knowledge router never got the fix.** `agent-lint.py` now
  discounts a fragment of a hyphenated compound, so `chain` taken from
  `supply-chain` cannot carry a confident route. `graph-lint.py`'s tokenizer
  regex does not include `-` at all, so it still scores `chain` at full
  strength. The *specialist* router was repaired and the *knowledge* router,
  which is installed into every plant, was not.

> **Corrected 2026-09-15, during the conformance review.** D-8 is wrong as
> written. `graph-lint.py`'s `resolve()` scores through `_split_terms` /
> `_strength`, which DO carry the fragment discount; the tokenizer this record
> describes survives only behind `Node.routable_terms`, which nothing calls.
> `test_router_tokenizers_have_diverged` compared that dead pair against
> agent-lint's live one, so it asserted a divergence the router did not have and
> could never fail. It now asserts convergence on the live path. D-6 is also
> closed: the shared reader refuses a multi-line description, with
> `status-register` the one recorded exception. The record below is left
> standing as what was believed at the time.

**Neither is fixed here, deliberately.** D-8's fix would change node-routing
behaviour for every already-grown plant, and the ledger's own U-36 says
knowledge routing and specialist routing are two problems forced through one
scoring model whose separation is gated on measurement (Track E). Changing the
scorer without measuring the effect on node routing is the anti-pattern
"replace deterministic logic without measured gain". D-6 changes parser
behaviour across three tools that read plant-authored files, where tolerance is
partly deliberate.

Both are therefore **enumerated debt, asserted by name in the test suite** —
`test_router_tokenizers_have_diverged` is a test whose name is the finding — and
the gate registry classifies this suite `evidence`, recording in as many words
that it passes while both are outstanding. That is the same idiom as the legal
edition ledger and the eager-surface exemption: a debt that is counted is not a
green lie; an uncounted one is.

**Open, carried forward:** D-6 and D-8, each with an owner decision attached —
D-8 to U-36's measurement, D-6 to whether the tolerant parsers should report
what they drop.
