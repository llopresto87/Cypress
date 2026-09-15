# Handoff — 7.16.0

**What this is:** the specification still owed, and the decisions already taken
on how to implement it. Nothing else. The narrative of how the work went — the
review rounds, the finding counts, what each round got wrong — is deliberately
not here; the operating doctrine is [`RESUME-PROMPT.md`](RESUME-PROMPT.md) and
the per-slice detail is in the records beside this file.

**Baseline:** HEAD `d7588e2` (7.15.0). All work is **uncommitted** on `main`.
`manifest.json` says 7.16.0; `CHANGELOG.md` carries the entry, written as the
work landed.

---

## 1. State — derive it, do not read it

Every figure below is printed by a command. If this file and the command
disagree, the command is right and this file is a defect.

| Fact | Command |
|---|---|
| gates, what each READS, the false green each can still produce | `python3 tools/gate-registry.py --summary` / `--table` |
| ratcheted limits, and whether any loosened | `python3 tools/ratchet-lint.py --show` |
| routing accuracy per corpus class, never averaged | `python3 integrations/claude-code/agent-lint.py --eval --dir agents` |
| spec shape and contract coverage | `python3 templates/knowledge-graph/spec-lint.py --specs docs/specs --root .` (bare, it reports the honest debt as FAIL; the gate passes `--uncovered-budget`) |
| roster justification, per node, derived | `python3 tools/roster-justification.py` |
| everything | `bash tests/run.sh` — capture its exit code ALONE, then read the log |

---

## 2. The specification still owed

### 2.1 Open, and blocked on something the seed cannot produce

Each needs a **grown plant**. The seed can state the question and not answer it.

| Item | What is owed |
|---|---|
| **U-36** graph-routing metrics | a golden corpus for NODE routing (task → expected node set), the equivalent of `agents/_routes.golden.tsv`. Without it, a change to `graph-lint`'s scoring cannot be graded. |
| **U-41** institutional memory | unmeasured; the README must not imply otherwise |
| roster merge/retire | whether the roster should be 20 agents. Needs usage data: which agents were actually spawned, over real work. `tools/roster-justification.py` derives everything derivable without it. |
| confidence-band calibration | SPEC-0002 §11; unmeasured |
| **Decision D** — semantic adjudication behind the router | see §3.2 |

### 2.2 Known-open, not fixable

- **Prose inversion.** Any free-text assertion is satisfied by its own negation;
  natural-language negation is unbounded. Five survive. Recorded in
  `tools/gate-registry.py`. One of six inversions is caught, and that one is
  bound to table cells. Do not spend a round on this.
- **The knowledge router cannot tell a domain.** `UNKNOWN_DOMAIN_MUST_ABSTAIN`
  is true of the corpus, not of the router: the band is RELATIVE — it says the
  winner beat the runner-up, never that the task belongs to this roster. Three
  separating mechanisms were tried and measured; none works. See §3.3.

### 2.3 Disclosed residuals — true, recorded, not defects to re-find

- `EVAL_THRESHOLD` 0.95 against a measured 0.984: three contract rows of slack,
  deliberate headroom for the df shift an added agent causes. In
  `gate-registry.py`.
- `spec-lint`'s coverage pass matches a slug ANYWHERE under `tests/`, including
  in a comment. Verified: three contracts became "covered" when a docstring
  named them. `seed-lint`'s `check_spec_rows_name_their_contract` is the
  stricter companion — it requires the slug in the test the ROW cites.
- The seed-integrity digest is blind to `.git/objects` and `.git/logs` (pruned
  for churn), mtime-only changes, and `__pycache__/*.pyc`. In
  `gate-registry.py` under `NON_STEP_GUARDS`.
- `PREFLIGHT_REFUSES_BEFORE_WRITING` is scoped to the directories the preflight
  ENUMERATES. A per-skill leaf under `.claude/skills/` is refused late, by
  `ensure_dir`, after writes have landed. Recorded in SPEC-0001 §4.
- The seed's own plans are not linted by `grill-lint` and cannot be: they use
  `## §N` headings, not the plant's `## N.`. Only the ledger invariant is
  checked, by `seed-lint`'s `check_plan_ledgers`.

---

## 3. Decisions

### 3.1 Taken

| # | Decision | How it is implemented |
|---|---|---|
| **A** | `graft.md` keeps its report template | The three lifecycle protocols got their own 2 500-line ceiling ([ADR-0007](../../decisions/adr-0007-lifecycle-protocol-ceiling.md)) and were expanded, not trimmed. |
| **B** | The adversarial budget is 2, not 3 | Repairing the routers' lexical reach moved it from 3 confident-wrong to 2; the budget was ratcheted DOWN to match. Not a judgement accepted on trust — the number fell. |
| **C** | Merge nothing from the roster now | Justification lives per node in `prevents:`, derived by `tools/roster-justification.py`. The merge question itself stays open (§2.1). |
| **E** | A `green` §10 row must cite a test that NAMES its contract | `seed-lint`'s `check_spec_rows_name_their_contract`, with `SPEC_ROW_UNBOUND_BUDGET` as a shrink-only ratchet. Paid to **0**: every §10 row is bound. Coverage went 7/30 → 28/30; the two uncovered are the two rows honestly `pending`. |
| **F** | Mirror `agent-lint`'s fragment model into `graph-lint` | A hyphen fragment scores at most 1, never the full 2. Measured before: 44 hyphenated trigger compounds, 71 fragments matching at full strength, 18 of them taking the rare-term bonus — including `chain` ← `supply-chain`, the 7.15.0 incident verbatim, still live in the router that ships to plants. After: 10. The compound still reaches its owner at full strength. |
| **G** | Raise `PARAPHRASE_FLOOR` 2 → 4 | The floor is what the router achieves; two rows of slack had no defender. Verified: neutering one confident-correct row passes at 2 and fails at 4. |
| **H** | Raise `EVAL_THRESHOLD` 0.90 → 0.95 | Bit at 55 of 61; five contract rows could break green. Now bites at 58. The remaining three rows of slack are disclosed rather than closed (§2.3). |
| **I** | Do not try to fix out-of-domain abstention lexically | Three mechanisms measured, none separates. SPEC-0002's `Except` now records the measurement instead of proposing a remedy that does not work. `--route` prints a NOTE when the absolute score sits at the bottom of the range real tasks occupy — a hint, because the route is advice a model mediates, not a gate. |
| **J** | A multi-line `description:` is REFUSED | Settled by K: the shared reader rejects it, with a message telling the author to put the value on one line. |
| **K** | One frontmatter reader, not eight | `agent-lint`'s reader promoted verbatim + one level of nesting for `plant:`. Five of five real parsers share it; `status-register` is a recorded exception (tolerant by documented design, and it needs a key→line-number map to rewrite in place); `status-migrate`'s is a regex predicate, not a parser. Four byte-identical copies, enforced by `check_frontmatter_reader_is_one_reader`. |
| — | `legal-lint.py` ships into a plant **iff** the legal corpus does | Placed by `place_legal_corpus`, so it travels with the corpus and only then. Until 7.16.0 a plant received `_schema.md` — the contract a corpus page must satisfy — and no instrument to check it. |

### 3.2 Decision D — does the router get a semantic layer? **OPEN**

**What.** LLM adjudication *behind* the deterministic router for ambiguous
cases: never overriding a confident deterministic route, always recording its
reasoning.

**Why it is still open.** Its adoption bar is a measured improvement on
held-out and adversarial data. On phrasings the router was never given it is
confidently correct 4 of 17 and abstains 13 times; against deliberate baiting it
is confidently wrong 2 of 12. Those are the two numbers it must move.

**What strengthened the case.** Decision I: telling `crop rotation` from `key
rotation` is meaning, not spelling, and no lexical rule separates them. That is
an argument, not the measurement D requires.

**How, if taken up.** Adjudication receives task, candidate agents, scores,
contracts, phase and delegation constraints; returns roles, boundary,
confidence, an orchestration flag and rejection reasons. It may never silently
override a confident deterministic route. Gate it on both corpora, before and
after. Adopt only if the adversarial number falls **and** the paraphrase number
rises, with no regression in the contract class.

### 3.3 The commit — **OPEN, the owner's**

`manifest.json` is at 7.16.0 and `CHANGELOG.md` carries the entry. Held all
session on the owner's standing instruction.

What is demonstrably better than 7.15.0, verified by running the same attacks
against both:

| Attack | 7.15.0 | now |
|---|---|---|
| symlinked `--project-dir`, `docs/graph/protocols` → outside | exit 0, **16 files written outside the target** | exit 1, none |
| hardlinked `docs/graph/index.md` | **outside file overwritten** | untouched |
| one truncated field in `.cypress/seed.json` | decision silently reset to `undecided` | refused, record preserved |

---

## 4. Traps — things that look wrong and are not

- **`--force` does NOT suppress the kernel deviation notice or the
  adopted-instruction notice.** Both say something the plant decided is no
  longer in force. Only "backed up existing X" is chatter. A reviewer asked for
  the opposite and was refused.
- **`SINGLE_WRITER` has 10 recorded exceptions and that is not a defect.** They
  are authored writes — the migration note, the sibling kernel link,
  `fill_plant_facts`, `ensure_dir` — and the list is DERIVED from `install.sh`
  on every run, by count as well as by shape. SPEC-0001 §4 names them.
- **`.cypress/seed.json` is the one recorded exception to recoverability** — a
  fresh `installed_at` every run would leave one `.bak` per install for ever.
- **The gate registry classifies itself `semantic`**: it checks a
  classification exists, not that it is true.
- **`ratchet-lint` compiles source from text, never importing it.** Python
  validates its bytecode cache on (mtime, size), and `8_000` / `7_600` are the
  same byte length.
- **Three statuses were tried for the specs and two were wrong.** `active` needs
  a RED that never landed; `draft` silences every check on the spec — verified,
  a full gate EXIT=0 with both specs unchecked. `back-written` is correct and is
  in `LIVE_STATUSES`; `seed-lint` now fails if either spec leaves that set.

---

## 5. Records beside this file

Slice records and review records under `grill-7.15.0-remediation/` — 18 slices,
4 review rounds. `../unrouted-work.md` for the entry fork, the brainstorm split
and `agent.tool-smith`. The operating doctrine for the review loop is
[`RESUME-PROMPT.md`](RESUME-PROMPT.md).
