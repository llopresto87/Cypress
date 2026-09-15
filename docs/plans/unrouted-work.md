# Work the graph describes and routes to nobody

**Status:** slices 1–4 implemented 2026-09-14. Gate green, no limit loosened by
these slices. The step and limit counts are not restated here — they moved twice
after this line was written, which is what a count in prose does; ask the things
that derive them, `python3 tools/gate-registry.py --summary` and
`python3 tools/ratchet-lint.py --show`. Roster moved 15→14 protocols, 14→15
skills, 19→20 agents.
**Baseline commit:** `d7588e2` (7.15.0), working tree at 7.16.0.
**Authorized by:** the owner, 2026-09-14, in response to the U-40 roster
evaluation ([HANDOFF Decision C](grill-7.15.0-remediation/HANDOFF.md)). Three of
the four slices below revise what that evaluation recommended, and §2 says where
and why.

This file is the authoritative ledger. Each slice is a child file under
`unrouted-work/`; §5 indexes them and `seed-lint.py`'s `check_plan_ledgers`
enforces the bijection.

---

## §1 The finding that makes this one plan and not four

**Four times, the graph describes work and routes it to nobody.**

| # | The work | How the graph describes it | Who it routes to |
|---|---|---|---|
| 1 | starting a new project from the seed | `protocols/from-scratch.md`, nine phases, complete | **nobody** — the kernel never names it; `install.sh` sends every repo to `/initialize`, which forwards to `grow` |
| 2 | deliberating internally, with no user in the loop | — | **nobody** — the only brainstorm the seed has *cannot exit without explicit user confirmation* |
| 3 | authoring a durable tool | `canonize` catalogs "any durable tool **it produced**" | **nobody** — no node is named as the producer |
| 4 | choosing between the empty-repo and existing-code paths | `grow.md:555`, one conditional clause | **nobody** — `initialize`, the adapter the installer points at, forwards unconditionally |

Each is a hole of the same shape: a job the method believes is happening, with
no owner. That is why they are one plan. They are also cheap together and
expensive apart — 1 and 4 are the same route, 2 and 3 each need a node the other
three slices' edits touch anyway (manifest, kernel, references, corpus).

## §2 Where this revises the U-40 evaluation, and why

The roster evaluation recommended retiring `initialize` and reclassifying
`toolcraft` to a skill or method node. Both were judged on structure — size,
owned facts, edges — without asking what the entry surface needs or who does the
work. The owner's reading was better on three of four:

| Evaluation said | Owner said | Who was right, and why |
|---|---|---|
| retire `initialize` (a 230-token alias) | repurpose it as the **fork** | **owner.** It *is* an alias today, but the front door needs a branch and a branch is what an adapter belongs as. Retiring it would have deleted the only node positioned to hold the decision |
| merge `brainstorm` + `brainstorm-socratic` (protocol 400 tokens < skill 650) | split them **by audience** — internal vs user-facing | **owner.** Size is not a boundary. Audience is, and it is the seam the current pair does not draw: both of today's nodes are user-facing |
| reclassify `toolcraft` (doctrine with no flow) | make it an **agent** that authors tools | **owner.** The diagnosis "no flow, therefore not a protocol" was right and the conclusion was too small. A charter with no flow is an agent |
| fold `from-scratch-bootstrap` into `from-scratch` | agreed | — |

## §3 The measurement that shapes slice 1

`from-scratch` **invokes; it does not duplicate.** Against all eleven nodes it
claims to adopt, it restates **1.0%** of its own prose; against `grow`
specifically, **0.0%** — zero identical sentences, zero shared 8-word shingles
out of 1 006. Pointer density is **18%** against `grow`'s 2%.

So there is no content reconciliation anywhere in this plan. Full method in
`unrouted-work/evidence.md`.

The inversion is worth stating because it sets the risk: **the unreachable
protocol is the well-factored one.** The slices below change routes, entry
conditions and ownership. They do not rewrite procedure, and any slice that
starts rewriting `from-scratch`'s phases has gone wrong.

## §4 Budget and hard constraints

| Constraint | Value | Bearing |
|---|---|---|
| `KERNEL_BUDGET` | 8 000 bytes; kernel is at **7 564** → **436 bytes** of headroom | slices 1, 2 and 4 each need a kernel edit; together they must fit |
| the eight `rule.*` homes | a dict in `seed-lint.py`; `rule.toolcraft` → `protocols/toolcraft.md` | slice 4 moves one. Seven live in protocols, one (`rule.knowledge`) in a skill — a non-protocol home is precedent; **no agent owns one** |
| `canonize` single-spawn | "there is no separate toolcraft spawn; a second spawn … would be coordination waste" | slice 4 must **narrow** this to cataloging, never reverse it |
| `MACHINERY_BODY_CEILING` / lifecycle ceiling | 1 000 / 2 500 body lines | no node here comes close |

## §5 The slices

Dependency order. Slice 1 makes the target correct before slice 2 routes to it.

| # | Slice | Record |
|---|---|---|
| 1 | `from-scratch` absorbs its bootstrap and owns its entry | `unrouted-work/slice-01-from-scratch-owns-its-entry.md` |
| 2 | The front door branches | `unrouted-work/slice-02-the-front-door-branches.md` |
| 3 | Brainstorm splits by audience | `unrouted-work/slice-03-brainstorm-splits-by-audience.md` |
| 4 | Tool authorship gets an owner | `unrouted-work/slice-04-tool-authorship-gets-an-owner.md` |

## §6 Evidence

| What | Record |
|---|---|
| delegation-vs-duplication, overlap, pointer density, roster blur | `unrouted-work/evidence.md` |

## §7 What implementation found that the plan did not predict

Both came from adding a 20th agent, and both were fixed at the cause — never by
moving a budget or editing a corpus row.

1. **`keep` is not a routing word.** "we keep writing this same script" took two
   *paraphrase* rows to HIGH `tool-smith`, including "can we **keep** European
   customer records on a server in Virginia". A high-frequency English verb whose
   dominant sense is unrelated to the trigger's sense is a bait the router cannot
   see through. Reworded; paraphrase returned to 4 correct, 0 confident-wrong.

2. **A roster addition reweights every term for everyone.** The word
   `plan-of-record`, sitting incidentally in the new agent's *description*,
   pushed `record` from df=3 to df=4 — across the `weight 2 → weight 1`
   boundary — which cost `architect` two points on an unrelated adversarial row
   and dropped it below `FLOOR = 13`. **`tool-smith` never appeared in that
   ranking at all**; it changed the arithmetic the others are scored by. IDF is
   global. Worth knowing before the 21st agent, and it is the strongest argument
   yet that roster growth has a cost the roster size alone does not show.

3. **A third hand-maintained roster list.** `tests/test_agent_lint.py` held
   `ALL_AGENTS` as a literal set whose own comment said it mirrored `agents/`.
   The new agent passed every gate except that one, which then blamed the golden
   corpus for naming a "non-roster agent" that was on the roster. Now derived,
   with a guard that fails rather than passing vacuously on an empty directory.

## §8 What this plan does not do

- **It does not rewrite `from-scratch`'s phases.** They are well-factored (§3).
  Slice 1 adds an entry section and makes Phase 2 idempotent; it changes no
  phase's owner, adopted node, or exit condition.
- **It does not touch `grow`'s body.** `grow`'s 2% pointer density against the
  core protocols — it names `protocol.verify` zero times while owning its own
  23-row gate table — is the same defect class the lifecycle rework addressed,
  on a different axis. It is **not verified as duplication** and a density figure
  is not a finding. Out of scope, and named here so it is not lost.
- **It merges and retires nothing else.** The U-40 evaluation found the highest
  routing-trigger overlap anywhere in the roster is 0.18, and `prevents:` overlap
  is near zero. Nothing in this roster duplicates anything.
- **It does not answer whether the roster should be 19 agents.** That needs
  usage data from a grown plant. It ends at 20.
