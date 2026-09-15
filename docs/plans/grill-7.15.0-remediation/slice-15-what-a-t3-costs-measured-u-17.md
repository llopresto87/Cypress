### Slice 15 — What a T3 costs, measured (U-17)

**Tier:** T2 (measurement).

The seed had no cost model. Seventeen of nineteen agents are Opus-class, every
T2/T3 unit of doing is a clean-context spawn, and nothing measured what that
buys. One observation now exists, and it is not flattering.

**The task, run twice.** Ledger entry U-27: three linters answer an unreadable
file with a bare `continue`; make them report and fail, and add a test. The same
underlying work, from the same starting commit (`d7588e2`), by the same model
class, in two conditions.

- **Funnel.** A brief carrying the method: the invariant named (V5), the
  red-before-green requirement, style constraints referencing the surrounding
  code, an eight-point verification list, and an explicit file-ownership
  boundary.
- **Baseline.** The defect described in five lines, the three files named, one
  constraint ("standard library"), and "tell me what you changed and how you
  know it works." No method, no invariant, no verification list. Run in an
  isolated git worktree so neither could see the other.

| | funnel | baseline |
|---|---|---|
| tokens | 131 583 | **118 973** |
| tool calls | 72 | **60** |
| wall clock | 12m 40s | **10m 32s** |
| linters fixed | 3 | 3 |
| red-before-green proof | yes, each fix reverted | no |
| new instances of the defect found | 0 | **1** |

**The funnel lost on every axis measured.** It cost 11% more tokens, 20% more
tool calls and 20% more wall clock, and the thing it bought — a documented
red-before-green proof for each fix — is real but was not free.

**And it missed a defect the unguided run found.** The baseline reported a
*fourth* linter with the identical silent skip: `tools/agnosticism-lint.py`,
which is in the gate and is installed into every plant. The ledger named three.
The Phase 0 enumeration found three. The funnel brief said three, and the funnel
agent fixed exactly three and verified exactly three, thoroughly. The unguided
run was not told how many there were, so it looked.

That is the finding, and it is a finding about briefs rather than about tiers: a
brief precise enough to be verifiable is also precise enough to bound the search.
The funnel's own doctrine says a specialist should name the gap rather than fill
it silently — here the gap was outside the brief's frame, and the discipline that
made the work checkable is what kept it there.

The fourth instance is now fixed and pinned in `tests/test-lint-audibility.sh`,
which is how the measurement paid for itself. Its skip had even carried a
rationale — "binary or unreadable: carries no prose" — while the tool's
`DEFAULT_GLOBS` is `("*.md",)`, so the only thing it could skip was a markdown
file it had failed to read. A stale reason reads exactly like a considered one.

**Conditions, stated so the number is not over-read.** One task, one model class,
one pair of runs. The task is small, well-localized and highly specified, which
is the shape that flatters an unguided run: there was no spec to write, no
architectural choice, no cross-file coordination, and the verification was cheap
to invent. A T3 with a real spec contract, several files and a rollback path may
distribute very differently, and this observation does not speak to that. It also
measures cost-to-first-delivery, not cost-to-correct: the baseline's lack of a
red-before-green proof means nobody has shown its three fixes would fail if
reverted, and that debt is not in the token column.

**What it does establish:** the funnel's overhead on narrow, well-specified work
is roughly 10–20%, not a multiple — and a tightly-scoped brief has a measurable
recall cost that no amount of verification rigour inside the brief recovers.

**Not a headline.** One observation, reported with its conditions, in the place
an adopter looking for cost will find it. It is not evidence that the method
helps or hurts in general, and it will not be quoted as either.
