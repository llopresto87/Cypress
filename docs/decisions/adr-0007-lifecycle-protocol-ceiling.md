# ADR-0007: the cross-project meta-loop answers to a larger ceiling than the rest of the graph

## Status

`accepted` — shipped as **7.16.0** (2026-09-14). Amends the machinery body
ceiling introduced in the same release (`tests/seed-lint.py`,
`check_body_ceiling`). It does not supersede
[ADR-0004](adr-0004-pure-graph-architecture.md): every node is still routable,
still loaded whole, still selected from its `load_when:` triggers.

## Date

2026-09-14

## Context

7.16.0 closed a gap where the seed measured node size without bounding it —
`est_tokens` was checked for honesty and never against a limit, so machinery
could grow indefinitely as long as it declared the growth accurately. An honest
number is not a budget. `MACHINERY_BODY_CEILING = 1000` was set just above the
largest node of the day, as a ratchet rather than a demand to split anything.

That left `protocols/graft.md` at 992 body lines with eight lines of headroom,
and the next edit anyone made to it would fail the gate. The proposal on the
table was to extract its report template to get back under.

Two facts, established while arguing that proposal, changed the question.

**The context cost the ceiling protects against is not paid at this position in
the graph.** The argument for splitting a large node is that a session pays for
material it will not use. But the router selects a node from the `load_when:`
triggers in the index; it never opens a body to decide whether it wants the
body. So `graft.md` is read only by a session that is performing a graft, and
that session needs the procedure. The general ceiling was being applied to three
nodes whose loading pattern it does not describe.

**Procedural completeness in these three is load-bearing for safety.** The
defining defect of this remediation was a graft that destroyed three plant
customizations, left zero backups, and reported *"clean — no plant knowledge
overwritten"* — the verdict inverted from reality because the defect bypassed
the mechanism the audit observes. `graft`, `grow` and `harvest` are the only
protocols that write into a repository the seed does not own. Trimming a
destructive-operation procedure to satisfy a line count trades a data-loss risk
for a token-budget one.

## Decision

`protocols/graft.md`, `protocols/grow.md` and `protocols/harvest.md` answer to
`LIFECYCLE_BODY_CEILING = 2500`. Every other routable node keeps
`MACHINERY_BODY_CEILING = 1000`.

It is a **ceiling and not an exemption**. A governing procedure nobody finishes
reading fails the same way a truncated one does, and "no limit" is how graft
reached 992 lines without anyone deciding it should. 2 500 is roughly 2.5× the
largest of the three, which is the room the reworks they are owed will need, and
it ratchets exactly like every other limit: `tools/ratchet-lint.py` records it,
fails on a raise, and the owner's `--bless` in a diff someone reads is the
signature. Raising it again is a fresh owner decision, not an edit made to fit
new text.

The three are **named, not derived**. They are a closed set fixed by what they
do — carry the seed outward, grow a plant from it, fold lessons back — and no
property of their text distinguishes them, so there is nothing honest to derive
the membership from. A fourth name is an owner decision the same way the number
is, and `ratchet-lint` treats `LIFECYCLE_NODES` as a debt ledger: a name joining
it is reported as loosening.

## Consequences

- The graft report-template extraction becomes **optional tidiness rather than
  remediation**. It remains a reasonable change — a fill-in form reached for
  when writing output does not belong inside a procedure read for its flow —
  but it is no longer forced by a deadline, and it is not a prerequisite for
  anything.
- Three nodes can now grow to 2.5× the general limit. The mitigation is that
  the three-way rework planned alongside this decision spends that room on
  completeness that is currently missing, not on the growth that produced 992.
- A named list is a fact with one home, and lists are what failed three times in
  this remediation. `tests/test-seed-budgets.sh` therefore proves four things
  rather than asserting them: that the general ceiling still binds (probed
  against the largest node it governs, **discovered** rather than named, so it
  keeps binding when that node changes), that the lifecycle ceiling binds, that
  a `LIFECYCLE_NODES` entry matching no node fails loudly instead of silently
  exempting nothing, and that the exemption is real — at a general ceiling below
  every lifecycle node, none of the three may be reported.
- `README.md` states the measured range and both ceilings in one place.

## Alternatives rejected

**Extract the report template and keep one ceiling.** Buys ~64 lines. The next
substantive addition to graft re-opens the same argument, and the argument would
be settled by whatever was easiest to delete rather than by what the procedure
needs.

**Split `graft.md` along its three declared `owns:` facts.** They weigh roughly
50 / 50 / 570 lines (`graft.user-sovereignty`, `graft.pure-graph-mandate`,
`graft.reconcile-flow`), which yields two stubs and a 570-line node — the size
problem intact, plus two new routable files and a changed placed-file set every
grown plant must reconcile.

**Exempt the three outright.** Rejected for the reason in §Decision: it grants
exactly the unbounded growth that produced the situation, and it makes the
limit unfalsifiable, which `tests/test-seed-budgets.sh` exists to prevent.

**Freeze the three at today's measured size, zero slack, like
`EAGER_EXEMPTIONS`.** That idiom is right for debt someone intends to pay down.
These three are not carrying debt to be repaid; they are carrying procedure that
is, if anything, incomplete. A zero-slack freeze would block the rework this
decision is meant to enable.

## Amendment — 2026-09-15: the ratio was wrong, and it binds one node

This section is appended, not edited in. §Decision above still says 2 500 is
"roughly **2.5×** the largest of the three", and §Consequences still says "three
nodes can now grow to 2.5× the general limit". **Both are false**, and were
falsified by the rework this decision exists to enable.

Measured 2026-09-15, counting the body after frontmatter the way
`tests/seed-lint.py` counts it (`body.strip("\n").splitlines()`):

| Node | body lines | against `LIFECYCLE_BODY_CEILING = 2500` | against `MACHINERY_BODY_CEILING = 1000` |
|---|---|---|---|
| `protocols/graft.md` | **1 384** | 55% of it, 1 116 lines of headroom | over — this is the one node the exemption is carrying |
| `protocols/grow.md` | **875** | 35% | **under** |
| `protocols/harvest.md` | **922** | 37% | **under** |

2 500 ÷ 1 384 is **1.8×**, not 2.5×. The 2.5 was true when it was written,
against the 992-line `graft.md` of §Context, and it stayed in this document
through the lifecycle rework that took graft to 1 384. `tests/seed-lint.py`
already carries the corrected figure at `LIFECYCLE_BODY_CEILING`, together with
a note naming this exact drift — which is why the correction belongs here and
not there: a derived multiple written in prose beside the number it derives from
has two homes, and the one that was wrong is the decision document, not the
constant.

Two consequences this amendment records, neither of which reverses the decision:

1. **Two of the three `LIFECYCLE_NODES` currently need no exemption at all.**
   `grow` and `harvest` are both under the general `MACHINERY_BODY_CEILING`, so
   the ceiling this ADR grants binds exactly one node, at 55% of it. The
   decision stands anyway, on §Context's reasoning rather than on arithmetic:
   the three are named and not derived precisely because no property of their
   text distinguishes them, and "currently under the general ceiling" is a
   property of today's text. Striking either name would mean re-deciding the
   membership every time an edit crosses 1 000 lines, which is the derived list
   §Decision rejected.
2. **The mitigation in §Consequences held.** The room was spent on the
   completeness the rework was owed, not on unbounded growth: graft moved from
   992 to 1 384 and is the only node that used the grant. The claim that needed
   correcting was the size of the grant, never what was done with it.

Nothing in the ratchet changes: `python3 tools/ratchet-lint.py --show` reports
`LIFECYCLE_BODY_CEILING` at 2 500, `MACHINERY_BODY_CEILING` at 1 000 and
`LIFECYCLE_NODES` at 3, and raising any of them remains a fresh owner decision.
