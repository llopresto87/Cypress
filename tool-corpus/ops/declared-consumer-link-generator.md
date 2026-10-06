# Tool: declared-consumer-link-generator

> Project-agnostic capability notes, kept in the seed's tool corpus
> (`tool-corpus/README.md`). This page is a **BLUEPRINT**: the closed
> vocabulary, the skip-vs-fail distinction, and the generation discipline are
> portable; the declaration's schema and each consumer's link syntax are
> project-specific and are written per system.

## 0. Identity

- **Category:** ops
- **Name:** declared-consumer-link-generator
- **Language / runtime:** any (a reader for the project's own declaration
  format and for each consumer's link representation)
- **Stability:** **blueprint** — no portable implementation, because the
  declaration schema and the consumer link syntax differ by project. The
  vocabulary and the generation discipline are the value of the page.

## 1. What it does

Two stages built over **one hand-owned declaration** of "which consumer
(pipeline, job, service) consumes which configuration set":

- **The drift-gate stage** — an offline gate that cross-checks each
  consumer's hand-written link configuration against the declaration and
  fails, naming the offender, when they disagree.
- **The generator stage** — the mature form. Once a project outgrows
  hand-maintained links, this stage **derives** each consumer's link set
  *from* the declaration and emits it, so the link a consumer carries is a
  generated fact instead of something a person keeps in sync by hand.

It exists to catch, before anything downstream reads a wrong or missing
link, the recurring drift class where a consumer's wiring and the project's
own declaration of what that consumer needs diverge without warning —
usually because one was edited and the other was not.

## 2. Interface & invocation

```sh
consumer-link-tool \
  --declared <path to the one hand-owned declaration> \
  --root <tree root> \
  {--check | --write | --index} [--accept-link-changes]
```

- **Inputs:** the project's own declaration of consumers and what each one
  needs (the single source of truth); the tree root to resolve consumer
  files under.
- **Drift-gate stage (`--check`, read-only both ways):** compares the
  declaration against each consumer's real, hand-written link block.
- **Generator stage:** `--write` emits or rewrites each consumer's link
  representation from the declaration; `--check` here is a **staleness
  gate** — it exits non-zero when the committed, generated output disagrees
  with what generation would produce right now, and its failure message
  names the regenerate command; `--index` prints the reverse index (which
  consumers a given configuration set feeds) on stdout.
- **Outputs:** stdout for clean runs and for `--index`; stderr for failures,
  each line leading with a **stable marker token** from a **closed
  vocabulary**, so a test can pin the contract without mistaking a
  missing-file exit for a real finding.
- **Exit codes:** a closed vocabulary — **0** clean; **1** reality disagrees
  (a drift finding, a stale generated file, or a refused link-dropping
  write); **2** the declaration itself is malformed or structurally invalid;
  **3** the environment cannot run the tool (a required parser library or
  other dependency is missing). Exit 3 is never a drift verdict: the tool
  probes its dependencies first and stops there, so a missing library can
  never be read as "the links disagree" or as "the links agree". Adding an
  outcome means adding a code, never overloading one.
- **Preconditions:** the dependencies the reader needs are installed (exit 3
  otherwise); the declaration parses; a consumer the declaration names need
  not have a file on disk — that is an honest **skip**, never a failure.

## 3. Approach / algorithm

### One declaration, read by both stages, never re-derived

Both stages read the same hand-owned declaration as their single source of
truth for "who consumes what." Neither stage keeps its own copy of that
knowledge or re-derives it independently — a second, drifting copy of "what
each consumer needs" is exactly the failure this tool exists to prevent, and
it must not reappear inside the tool itself.

Write the declaration from what each consumer reads, never by copying the
current links: a declaration seeded from today's links makes the drift gate
ratify a copy of itself, over-linking included. Key it by consumer (each
pipeline lists the sets it needs), not by configuration set, so a reader sees
at once when a one-container pipeline links many sets. A set that exists
in the store but is linked to no consumer resolves blank at run time and
trips a mandatory-variable check that looks like a missing value.

### Drift-gate stage: closed vocabulary, honest skips

Cross-check the declaration against each named consumer's actual,
hand-written link block. The vocabulary is **closed** — every terminating
path maps to exactly one of the declared codes, with no catch-all — and
every failure line leads with a **stable marker token** naming the failure
class, so a test can assert on the marker instead of parsing prose.

A declared consumer with **no file on disk** is a **skip**, not a failure:
the declaration may legitimately name a consumer whose file has not been
created yet, and reporting that as a defect would punish planning ahead. Test
genericity with a **second, synthetic declaration** — a fixture consumer set
built for the test, not one real consumer's names — to prove the check is
not secretly keyed to a single real consumer's identity.

### Print safety carries over from the read-only auditor

Any sink that prints declared names runs through the **same print-safety
predicate** a live, credentialed auditor over the same kind of store would
use (`ops/declared-variable-existence-auditor.md` names this split): report
names, never values, even though this tool never touches a live credentialed
store at all. The habit is what protects the day this tool grows a mode that
does.

### Generator stage: derive, emit, and refuse to lose a link silently

The mature form treats each consumer's link set as **derived**, never
hand-maintained. `--write` regenerates it from the declaration; a literal,
hand-written link in a consumer file is, once generation exists, **itself
the violation** — the fix is to regenerate, never to hand-edit the generated
output.

- **`--check` is a staleness gate, not the drift gate.** It compares the
  declaration against what generation would emit right now, and its failure
  names the exact regenerate command to run. This is a different comparison
  from the drift-gate stage's "declaration vs. hand-written reality" — once
  generation exists, `--check` is the right gate to wire in, and running the
  older drift check alongside it can report two different, confusing
  answers about the same consumer. The staleness gate holds only while the
  generator is a pure function of the declaration (§5).
- **Emission order is semantic.** Preserve the declaration's own order when
  emitting a consumer's link set, because the consumer format's own
  precedence rule (commonly last-wins for a repeated name) depends on
  written order. Reordering the declaration during emission — even to make
  the output look tidier — changes which value the consumer sees.
- **A write that would drop a link is refused** unless the caller passes an
  explicit accept flag. This is the one guard against an accidental
  narrowing: a declaration edited to remove a name, intentionally or not,
  should require a deliberate second signal before the generator ships that
  narrowing.
- **Never hand-edit a generated file.** Once a file is generator-owned, any
  manual edit to it is lost on the next `--write` and is itself evidence the
  workflow was bypassed.

## 4. Portable vs blueprint

- **Blueprint (the whole page):** the declaration's schema, the syntax of a
  consumer's link block, and the consumer format's own precedence rule are
  project-specific and are written per system.
- **Durable across every implementation:** one hand-owned declaration read by
  both stages; the closed exit-code vocabulary (with exit 3 reserved for a
  missing environment, never drift) and a stable marker token per failure
  line; a planted drift and a gate-script invocation test; the fileless-consumer skip, tested against a synthetic
  second declaration for genericity; the shared print-safety predicate for
  any sink that prints declared names; declaration-order-as-semantic
  emission; the link-drop refusal without an explicit accept flag; never
  hand-editing a generated file.

## 5. Pitfalls and sharp edges

- **A strict line matcher over-reports on legal variants.** A matcher that
  accepts only the canonical form of a link line rejects a legal variant,
  such as an inline trailing comment after the name, and reports drift that
  is not there. That fails safe (a spurious finding, never a hidden one), but
  it still costs a maintainer a false alarm. Record each legal variant the
  matcher rejects until the matcher accepts it. The opposite mistake, a
  substring match over free text, fails unsafe: it reads a comment that
  merely mentions a configuration-set name as a link. Match the structural
  block the consumer format defines.
- **The drift-gate stage answers a different question from a live-store
  audit.** It reads only in-repo declaration and consumer files; it says
  nothing about whether a name the declaration requires exists in a live,
  credentialed store. That is a separate tool's job
  (`ops/declared-variable-existence-auditor.md`).
- **Running both the drift-gate stage and the generator's `--check` on the
  same consumer, once generation exists, can disagree in a confusing way** —
  the drift gate compares declaration-vs-hand-written-reality, `--check`
  compares declaration-vs-what-generation-would-produce. Once a consumer is
  generator-owned, retire the older drift check for it.
- **Only a pure function earns a regenerate-and-diff gate.** Only a
  script-generated artifact gets one; a list an agent seeded is hand-owned,
  and a comparison against a fresh seeding is advisory
  (`core/method/maintenance-contracts.md` §12 owns the three maintenance
  contracts). Check, too, that the script really is pure: a generator that
  carries each list's order and extra names forward from the previous
  artifact, or reads part of its input from a scan outside the declaration,
  cannot be rebuilt from empty. A regenerate-from-scratch diff then fires on a
  clean tree and gets muted, and "delete it and regenerate" is not a
  recovery. Gate such an artifact with narrow invariants that hold on a clean
  tree.
- **Every axis the data model has goes into a generated file's path.** A
  file named by role alone, when the model also has an environment axis, lets
  two environments of one role write one file: the last generation wins and
  both stay valid, so nothing shows the loss. Decide the path before the
  first file is generated, since a later rename touches committed files and
  every include line. `--check` covers every environment's files, never only
  the active one's.
- **A gate that echoes a literal proves nothing.** Before building a
  derivation on a field a spec names, confirm that the field exists and can
  carry the relation's cardinality (one component deployed by several
  consumers is not a per-component scalar). Gate a join between independent
  literals (the ids resolve, and the resolved names equal the consumer's own
  list), never a derivation that reads a literal and reproduces it.
- **A print sink added later that bypasses the shared print-safety
  predicate is a silent regression.** Test every sink, not just the first
  one written.
- **Group order collapsing during emission** (for example, sorting the
  output "for readability") silently changes precedence in any consumer
  format where later entries win. Preserve declaration order exactly.

## 6. Tests that cover it

Cover: a well-formed declaration and matching consumer files pass clean; a
missing dependency exits 3 with its own marker, before any comparison, and
never 0 or 1; a planted drift (a declared link removed from one consumer
file in a fixture) is reported by name, so a clean run cannot be a gate that
checked nothing; a link line carrying a legal variant the matcher rejects is
pinned as a known over-report until the matcher accepts it; a
malformed declaration exits with the structural code; a dangling reference
inside the declaration is caught; drift-gate: a missing link and an extra,
undeclared link each produce their own marker and exit code; a declared
consumer with no file on disk is reported as a skip, never a failure; a
second, synthetic declaration (not the real fixture) proves the check is not
keyed to one consumer's identity; every print path emits names only, never
values; generator: `--write`, `--check`, and `--index` modes each behave per
§2; declaration order is preserved through emission (a reordered declaration
changes the emitted precedence, and the generator's output reflects it
exactly); a write that would drop a link is refused without
`--accept-link-changes` and succeeds with it; a stray hand-written literal
link in a generator-owned file is itself flagged as a violation.

Integration, separately from the unit tests: the project's gate script
actually invokes the tool (a test that reads the gate script and fails if
the call is gone); the gate script passes each declaration or unit to it
explicitly rather than relying on a default; the tool runs end to end inside
that script; and it is clean against the project's real declaration. A gate
no script invokes is a gate that never runs.

- **How to run the tests:** `<the plant's test command for its implementation>`

## 7. References & neighbours

- **Related tools:** `tool-corpus/ops/declared-variable-existence-auditor.md`
  (the live-authority sibling — answers whether a declared name exists in a
  credentialed store, a different question from whether a consumer's
  hand-written or generated link agrees with the declaration; shares the
  names-only print-safety predicate).
- **Sources:** distilled from practice; no external URL.

## 8. Changelog

- 2026-09-26 — created by
  docs-librarian.
- 2026-09-26 — restored exit 3 (environment or dependency missing), the
  planted-drift and gate-script-invocation tests, and the strict line
  matcher lesson.
- 2026-10-05: folded in how a declaration goes wrong at birth (§3), the
  purity precondition of the staleness gate (§3, §5), and the path-axis and
  echo-gate pitfalls (§5), by docs-librarian.
