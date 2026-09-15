# ADR-0008: a component's justification lives in the component, and the count that judged it is retired

## Status

`accepted` — shipped as **7.16.0** (2026-09-14). Answers the recording half of
HANDOFF Decision C (U-40). It does not supersede
[ADR-0004](adr-0004-pure-graph-architecture.md). Note the scope: `prevents:` is
required of the **seed's own machinery nodes**, by `tests/seed-lint.py`. It is
not added to `REQUIRED_KEYS` in `templates/knowledge-graph/graph-lint.py`, so no
node in any grown plant owes one and no installed plant changes behaviour.

## Date

2026-09-14

## Context

U-40 asked whether anything in the roster of 19 agents, 15 protocols and 14
skills merges or retires. The handoff gathered evidence for it in a section
whose closing paragraph named what a justification owes, per component, before
anyone proposes removing it again: **the responsibility it holds, the failure it
prevents, evidence it has been used, what overlaps it, and its class**
(essential / beneficial / situational / redundant / transitional / obsolete).
Its stated plan was to publish that as a table under `documentation/`.

Two things were wrong with that plan.

**The evidence was measuring the wrong thing.** The section scored each
component by how often its name appears across the method surface and labelled
the low scorers *thin*. Re-derived against routing demand — rows in
`agents/_routes.golden.tsv` that expect that agent — the two columns give
Pearson **r = 0.17** over the 19 agents. They are unrelated, and the reason is
structural rather than noisy: a name-occurrence count measures **how much other
prose has to talk about a component**, which is highest exactly where a boundary
is contested and lowest where it is clean. `devils-advocate` carries seven
golden rows, tied for the most in the roster, and was labelled thin on eight
mentions. Three of the six agents flagged thin sit at or above the roster's
median routing demand.

The column could also not be checked. The section recorded no surface for it,
and an exhaustive search over all 1 023 combinations of ten candidate surfaces
(`core/`, `protocols/`, `skills/`, `agents/`, `templates/`, `docs/`,
`documentation/`, repo-root markdown, `tools/`, `tests/`) reproduces at most
**3 of the 19 counts**. Nobody could re-derive it, so nobody could tell when it
went stale — and two of the golden-row counts beside it, which *can* be checked,
had already drifted inside a single session of editing the corpus they count.

**Publishing the table would have made the roster's fourth home.** The
responsibility already has a home in each node's `title:` and `owns:`; the
overlaps already have one in `peers:`. A `documentation/` page restating them
would join `manifest.json`, the kernel roster line and the reference pages as
another copy to drift — in a repository whose governing rule is one home per
fact, and whose `seed-lint` exists largely to catch exactly that.

## Decision

**Each machinery node carries `prevents:` — the failure its own absence
produces — and the justification table is derived from the nodes on demand,
never published.**

1. `prevents:` is a required key on every machinery node (protocols, skills,
   agents, `core/method/`), enforced by `tests/seed-lint.py`. It is the
   counterfactual, not the charter: what goes wrong **without** this node.
   It was the one item U-40 asked for that was both owed and absent; the other
   four either already had a home or cannot have one here.
2. `python3 tools/roster-justification.py` prints the table, reading every
   column out of the node that owns it.
3. **Evidence of use and class are printed as absent, not guessed.** The only
   honest signal for use is usage, and usage happens in grown plants. Class is a
   conclusion drawn from evidence of use and cannot be sounder than the row above
   it; asserting one per node would ship a guess wearing a taxonomy's authority.
4. The name-occurrence count and the *thin* label derived from it are retired.
   The tool does not print them and will not reintroduce them.

The merge/retire question itself is **not** decided here. It stays open, and the
handoff's own closing paragraph is why: none of what would settle it is
derivable from this repository.

## Consequences

- Every node gained one frontmatter line. Frontmatter is not counted in
  `est_tokens`, which measures the body, so no node's declared budget moved and
  no ceiling was approached.
- The linter can check that a `prevents:` exists, is long enough to name a
  failure, and is not `title:` or `description:` restated in the future tense.
  It **cannot** check that it is true. That is recorded as `seed-lint.py`'s
  semantic false green in `tools/gate-registry.py`, which previously claimed
  the step produced none.
- Writing `prevents:` for all 59 nodes surfaced one real graph defect:
  `protocols/initialize.md` had no `peers:` at all, making it the only machinery
  node with no edges in either direction, in a graph whose router traverses
  edges. Its charter is "delegates unchanged to grow" and that edge did not
  exist. Fixed, with the `documentation/protocols-reference.md` mirror.
- A future component added to the roster must state what breaks without it
  before it can pass the gate. That is the intended cost.

## Alternatives rejected

- **Publish the justification table under `documentation/`**, as the handoff
  proposed. Rejected: a fourth home for the roster, unenforced, and stale on the
  first roster change — which is the failure mode that produced the superseded
  evidence in the first place.
- **Assert a `class:` per node.** Rejected: it is a conclusion, the seed has no
  evidence to draw it from, and a stale taxonomy label is more dangerous than an
  absent one because it looks decided.
- **Keep the name-occurrence count and add a caveat.** Rejected: it had a caveat
  already ("a weak signal, not a verdict") and the *thin* labels were read and
  acted on anyway. A number that is presented is a number that is used.

## Reversibility

**Cheap.** `prevents:` is additive frontmatter; dropping the `seed-lint` check
and deleting the key restores the previous contract with no migration. The tool
is seed-only and placed into no plant, so nothing grown depends on it.
