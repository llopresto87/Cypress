# Tool: static-config-contract-gate

> Project-agnostic, durable capability notes, folded into the seed by the
> harvest protocol. This page is a **BLUEPRINT**: the enumeration discipline,
> the two operating modes and their distinct blind spots, and the self-check
> idiom are portable; the reader for the artifact's own format, and the native
> resolver command for resolved mode, are written per system.

## 0. Identity

- **Category:** testing
- **Name:** static-config-contract-gate
- **Language / runtime:** any (a reader for the declarative artifact's own
  format; a native resolver binary only for resolved mode, no daemon)
- **Stability:** **blueprint** — no portable implementation, because the
  artifact format and its resolver are different for every system. The
  enumeration, mode split, and self-check discipline are the value of the
  page.

## 1. What it does

A daemon-free gate that asserts named contracts — each one traceable to a
specification clause — over a **declarative configuration artifact**: a
server configuration, an infrastructure manifest, a service definition tree,
anything a system loads and resolves before it runs.

It exists because a configuration artifact is read two ways that both fail
silently. Reading it by eye misses a directive the maintainer meant to be
implicit or inherited. Grepping for an absent token passes on a comment that
merely *mentions* the token. A contract worth gating deserves a program that
reads what the artifact structurally contains, not what a reviewer's eye
happened to notice.

## 2. Interface & invocation

```sh
static-config-contract-gate \
  --config <path to the artifact, or --root for a tree of them> \
  [--resolver '<native resolver command, for resolved mode>'] \
  [--case <named contract id>  ...]
```

- **Inputs:** the artifact path or tree root; an optional native resolver
  command for resolved mode; the named contracts to check, each titled after
  the clause it enforces so the case list alone reconstructs the
  specification.
- **Outputs:** the enumerated **scope-unit census** (§3) printed before any
  case runs; one pass/fail line per case naming its contract; a count.
- **Exit codes:** non-zero on any case failure, **and** non-zero when the
  scope-unit census is empty (the false-green guard — an empty census
  satisfies every case vacuously and must never read as a pass).
- **Preconditions:** the reader can parse the artifact's format for text mode;
  for resolved mode, the native resolver binary runs locally with no daemon
  and no live service.

Treat `--config`/`--root` as public API: it is how a mutant is built outside
the working tree and pointed at, per §3. The same handle proves a RED
satisfiable before any implementation exists: render the *target* shape of
the artifact on a scratch copy, point the gate at it, and confirm every new
case goes green there. A case the target text cannot pass is a gate nobody
can pass, and it is cheaper to learn that before the implementer starts.

## 3. Approach / algorithm

### Enumerate, never assume

The gate reads its **scope units** — the servers, locations, services, or
blocks the contracts are about — from the artifact itself, through a reader
that returns the whole list and **throws when it finds none**. It never works
from a hardcoded list or a count, so a unit added later is automatically in
scope and a wrong path fails loudly instead of passing on zero units checked.

Keep more than one enumerator when contracts genuinely differ in scope: a
narrower enumerator (only the units matching one selection rule) can be
exactly right for a contract that really is about that narrower set, and
**structurally blind** to a contract about *every* unit. The failure mode is
not choosing the wrong enumerator once — it is a case phrased in terms of the
narrow one when the contract it enforces is about the whole set. Name, in
each case, which enumerator it needs and why.

### Two operating modes, two different questions

**Text mode** compares the artifact's own format strings — after stripping
comments, and after resolving any include or inheritance chain the format
supports. This is what to use when the contract is about what the artifact
*declares*.

- Strip comments **before** any assertion by subtraction. A comment often
  names the removed directive, so a naive absence check that scans raw text
  finds the directive inside the comment and reports a pass.
- The reader is a line-scanner, not a full parser, when the format allows it
  (avoiding a parser dependency this way is a deliberate trade, not an
  oversight) — and a line-scanner can break on a legal reshaping of the same
  document (different quoting, different block-vs-flow style, reordered
  keys). State this instead of discovering it later.
- Text mode compares **format strings**, not runtime bytes. It cannot see a
  difference that only appears once the artifact is resolved and rendered —
  for example, a value that is always *set but empty* versus one that is
  *unset*, when both render identically at the format-string level. Never
  cite a text-mode pass for a claim about what the running system emits;
  that claim belongs to a dynamic measurement instead (see §7).

**Resolved mode** asks the artifact's own **native resolver** for the merged,
effective value — never a reimplementation of the merge — and asserts on
that. This is the native-oracle idiom: the resolver is the authority on its
own merge semantics, and a hand-rolled reimplementation is a second,
unvalidated implementation of the thing under test.

- Resolved mode is **structurally incapable of expressing a shape rule**. A
  hardcoded value and a variable reference that defaults to the same value
  resolve identically, so resolved mode can assert *what the value is*, never
  *whether it was written as a literal or as a substitution*. State this
  limit next to any resolved-mode result; a shape prohibition belongs to text
  mode instead.
- The minimal environment resolved mode runs the resolver against supplies a
  placeholder **only** for the fail-closed names it reads out of the artifact
  itself — never a list maintained inside the gate — and then asserts that no
  contract name is among the names needing a placeholder. A dead list inside
  the gate drifts from the artifact the moment either one changes alone.
- Check that every required input exists before any case runs, so a wrong
  path or root fails loudly rather than vacuously passing on a resolver that
  silently produced nothing.

### Self-check group: prove the reader saw something

Run the reader (in whichever mode) against small synthetic artifacts with
known answers, alongside the real cases. Without this group, "the reader saw
nothing wrong" and "the reader saw nothing" are the same sentence, and only
the self-check distinguishes them.

### Version pins as floors, never equalities

A version-pin case asserts `>= <version>`, never `== <version>`. An equality
assertion turns every legitimate upgrade into a gate edit, and editing a gate
to keep it green is the worst habit a gate can teach — the fix belongs in the
pin, not in the contract.

### Encoding independence

A gate that reads and compares text must not depend on the invoking
console's or shell's active code page or locale. A gate that passes on one
console and fails on another is not a gate; read and write the artifact's
declared or assumed encoding explicitly rather than trusting the environment.

### Mutation by copy, and what must survive

The alternate-input handle in §2 is public API precisely so a mutant can be
built **outside** the working tree, on a scratch copy, and pointed at through
that handle — the general procedure is `skill-corpus/mutation-verify.md` §4,
composed by reference here, not restated.

Two results from that procedure are specific to this tool's shape and worth
stating directly:

- **A formatting-only control mutant must survive.** Folding a block form into
  a flow form, reordering keys, changing quote style — none of these should
  ever turn a case red, because none of them changes what the artifact
  declares or resolves to. A gate that dies on these is brittle to any legal
  reshaping, not sensitive to a real regression.
- **A mutant that makes the artifact unparseable is evidence about the
  parser, not about the gate.** When every case dies because the document no
  longer parses, that is not a demonstration of coverage — rule the parse
  failure out (the rebuild corollary in `skill-corpus/mutation-verify.md`
  step 5) before reading anything into the result, and prefer a mutation that
  stays syntactically legal. The one good property it does confirm: an
  unparseable artifact fails the gate loudly with the parser's own message.
- **A mutant beside a floor survives, correctly.** A case that asserts a
  floor (at least these references, unchanged) lets a mutant that *adds* one
  more reference survive. That survival is the floor working as designed, not
  a coverage gap; record it as an expected survivor so nobody later
  "tightens" the floor into an equality.

### The mutation register

The register is the gate's authorization, and three rules keep it honest.

- **Re-derive the register against the landed code.** Mutants drafted
  against the intended text can miss the artifact as actually written: an
  anchor the implementer phrased differently, a block that moved. After the
  implementation lands, rebuild every mutant against that text, keep each
  mutation's intent, and re-run. Only the re-derived result is evidence.
- **Each mutant kills exactly its own contract.** A mutant that turns its
  own case red and leaves every other case green is the result to record. A
  mutant that kills many cases at once says less about any one of them.
- **Claim mutation status per case group, never suite-wide.** When one
  group was mutation-checked and the others were not, the honest record is
  "group X: N killed; other groups: not recorded". A suite-wide "mutation
  verified" on the strength of one group is a claim the evidence does not
  carry.

### Recorded limits: stricter gates, open gaps, orphaned gates

Three facts about a gate belong in its own record, with a date, rather than
in anyone's memory.

- **A gate stricter than its contract is a false-red risk.** If a case
  asserts more than the clause it cites (the whole chain where the contract
  binds one link), a pass still proves the contract, so it is never a false
  green. It will, however, block a legitimate change the contract allows.
  Record the excess and the clause it exceeds. Relaxing it is optional; an
  unrecorded excess is not.
- **A declared coverage gap is left open on purpose.** Where a mutation
  survives because no contract covers that property, the gate adds no case
  for it: a test with no contract behind it is outside the tester's charter,
  and pinning a choice the specification records as unverified would freeze
  it. List each such gap next to the mutant that exposed it, so the gap is
  visible rather than silent.
- **A gate no pipeline invokes is orphaned from CI.** If no pipeline or gate
  script calls it, it runs only when someone remembers. Say so on the gate's
  own page, and record the wire-or-retire decision where the project keeps
  open decisions.

## 4. Portable vs blueprint

- **Blueprint (the whole page):** the artifact reader for a given format, the
  native resolver command, and the contract set itself are written per
  system.
- **Durable across every implementation:** enumerate scope units from the
  artifact and throw on an empty census; keep more than one enumerator when
  contracts genuinely differ in scope; the text-mode / resolved-mode split
  and each mode's declared blind spot; strip comments before a subtraction
  assertion; version pins as floors; encoding independence; the self-check
  group; the target rendered through the alternate-input handle to prove a
  RED satisfiable; formatting-only mutants must survive; an
  unparseable-artifact mutant is ruled out before being read; the mutation
  register re-derived against the landed code and claimed per case group; a
  stricter-than-contract case, a declared coverage gap, and an orphaned gate
  each recorded rather than silently tolerated.

## 5. Pitfalls and sharp edges

- **Citing a text-mode pass for a claim about wire-level or runtime
  behavior.** Text mode compares declarations, not emissions. The claim "this
  is what the system emits" needs a dynamic measurement
  (`ops/config-driven-server-response-harness.md`), never a static one.
- **A resolved-mode case that "passes" for the runner's own environment's
  reason.** A value the artifact builds from an ambient variable of the
  process running the gate (a home directory, a working directory) can
  satisfy the contract only because that variable happens to be set. Empty
  it and the value can still satisfy the case while being wrong. This is not
  fixable at the gate: an assertion that caught it would have to forbid the
  interpolation itself, which is a shape rule the contract does not state.
  Record it as a spec gap and escalate it to the specification owner. Do not
  weaken the assertion, and do not add a shape rule the specification never
  made.
- **A count where an enumeration belongs.** A count-based case passes the day
  a unit is added without the property under test, because the count is
  still coincidentally right. Enumerate; never count.
- **A dead list of "known" names inside the gate**, kept separate from what
  the artifact itself declares, drifts the moment either side changes alone.
  Read the fail-closed names out of the artifact, every run.
- **A printed finding that is not counted.** Wire every finding the gate
  prints into its exit code; the failure this prevents is owned by
  `tool-corpus/ops/layered-config-merge-verifier.md` §5 ("The
  sensitive-token walk reports; it does not understand").

## 6. Tests that cover it

Cover: a synthetic artifact with a known contract violation is caught by the
matching case; the self-check group's synthetic artifacts each produce their
known answer, proving the reader is exercised and not merely present; a
comment naming a removed directive does not cause a false pass; a version
pin case passes on a version above the floor and fails only below it; a
formatting-only reshaping of a passing artifact (block-to-flow, key reorder,
requote) leaves every case green; a mutation that removes the contract
property from the artifact turns exactly the matching case red; an artifact
mutated into an unparseable document fails with the parser's own message and
is excluded from being read as coverage evidence; the register re-derived
against the landed text still kills each mutant on exactly its own case;
the rendered target text passes every new case before implementation begins;
a floor case lets an additive mutant survive; pointing the gate at a
missing or empty root exits non-zero with the empty-census message, never a
vacuous pass; resolved mode's minimal environment supplies a placeholder only
for names the artifact itself declares fail-closed.

- **How to run the tests:** `<the plant's test command for its implementation>`

## 7. References & neighbours

- **Related tools:** `tool-corpus/ops/layered-config-merge-verifier.md`
  (the variable-guard-only analogue: resolves a layered artifact through its
  native resolver and checks guard strength, a narrower question than the
  general named-contract gate here); `tool-corpus/ops/config-driven-server-response-harness.md`
  (the dynamic counterpart — measures what a config-driven binary emits over
  the wire, which is exactly what text mode here cannot see).
- **Procedure:** `skill-corpus/mutation-verify.md` §4 "Mutating an artifact
  the tree must keep: mutate by copy" (composed by reference, not restated).
- **Sources:** distilled from harvested plant experience; no external URL.

## 8. Changelog

- 2026-09-26 — created from harvested, generalized capability, by
  docs-librarian.
- 2026-09-26 — added the mutation register rules (re-derive against landed
  code, per-group status), the satisfiable-RED render, and the recorded
  limits (stricter-than-contract, open coverage gaps, orphaned gates); the
  runner-environment pass now escalates as a spec gap.
