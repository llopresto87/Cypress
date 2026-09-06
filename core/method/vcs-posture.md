---
id: method.vcs-posture
tier: 2
kind: method
origin: seed
title: vcs posture — local commits rest, publishing is authorized by the owner, one working tree, plant-declared commit settings
owns:
  - vcs-posture.local-resting-state
  - vcs-posture.publish-authorization
  - vcs-posture.no-worktrees
  - vcs-posture.plant-settings
requires:
peers:
  - method.engineering-posture
  - method.design-posture
  - method.stewardship-posture
  - protocol.deliver
load_when:
  - "should I push this or commit locally"
  - "open a PR, publish the branch, merge to the default branch"
  - "who authorizes a push, a deploy, or lifting a no-change rule"
  - "git worktree, parallel checkout, second clone for the same task"
  - "commit trailer, co-authored-by line, who signs the commit"
  - "which language for code comments or the deliverable"
est_tokens: 1000
---

# VCS posture

How in-flight work rests, who may publish it, how many trees hold it,
and which commit and language facts the plant — not the doctrine —
decides. The kernel's §4 boundaries are the parent rule; this node is
their version-control instance.

## 1. The local commit is the resting state of work

Work on a branch. Commit locally at every verified-green increment —
green by `protocol.verify`'s gates, committed as the last step of the
`protocol.test-first` loop. A local commit is what in-flight work looks
like when nobody is touching it: reversal is a reset to a known-good
state, a handoff points at a sha, and nothing has left the machine.
Green work left uncommitted at session end is a lapse; a red tree left
uncommitted is a lapse with no known-good state to return to.

Parking work is the same discipline seen sideways: record the pin
commit, keep the patch outside the tree, verify the tree is
byte-identical to the pin afterwards, and say where the work went.

## 2. Publishing is a separate authorization — MANDATE

None of the following happens without an **explicit owner authorization,
in the conversation, that names the act**:

- pushing to a shared remote — any branch;
- changing the default branch — by push, merge, rebase, or force;
- deploying;
- lifting a standing no-change rule (a doc-only phase, a frozen module,
  a "do not touch X" instruction).

The authorization is never automatic, never inferred from "the tests are
green", never carried over from an earlier session, and never bundled
into another approval: "go ahead with the fix" authorizes the fix, not
the push; "commit it" authorizes the commit, not the deploy. Writing a
fix and shipping it are two authorizations; when only the first is
granted, the work rests as a local commit and the delivery says so
(`protocol.deliver`).

The kernel §4 names the destructive cases — delete, force-push, drop,
rotate — each needing a confirmation that names the resource. Publishing
has the same shape and the same rule: a pushed commit is as hard to
un-see as a dropped table is to un-drop.

## 3. One working tree, one compounding branch

No git worktrees; no parallel checkouts of the same repository for the
same task; no second clone "to try something". One tree, one branch that
compounds through local commits. State diverges silently between trees —
each looks clean and passes its own gates, and the divergence surfaces
only at merge, where the recovery cost exceeds any parallelism the second
tree bought. Parallel work that a task genuinely needs is serialized at
the commit boundary inside the one tree (`method.delegation` bounds the
workers), never multiplied across trees.

## 4. Attribution and language are plant facts

Who a commit says wrote it, and which human language comments and
deliverables are written in, are facts only the plant's owner can assert.
They are declared **once**, in the `plant:` block of `docs/graph/index.md`:

| key | governs |
|---|---|
| `commit_attribution` | trailers and AI-authorship lines on every commit: `none`, or the exact trailer text |
| `comment_language` | code comments, docstrings, commit messages |
| `deliverable_language` | deliveries, reports, ADRs, anything handed to a human |

Doctrine never assumes these and never restates them — a node that says
"commits carry trailer X" is a second home for a plant fact and lies the
day the owner changes it. Read the block; obey it.

**Undeclared** (an adopted plant before the owner has answered, or no
plant at all): no attribution trailer, and match the language the
surrounding artifact already uses. Do not ask in the middle of a
commit; the ask belongs to grow Phase 1 / adopt-existing.

## Sharp edges

- A harness, hook, or IDE default that appends a `Co-Authored-By`-style
  trailer is an *assumption* about `commit_attribution`. Where the plant
  says `none`, the trailer comes off before the commit lands.
- "Push so CI can run it" is a push. Run the gates locally; a gate that
  exists only in CI is recorded as unexecuted in the delivery, not
  turned into an authorization.
- Opening a pull request publishes the branch: it needs the push
  authorization it implies.

## Neighbours

- `protocol.deliver` — the delivery states what rested locally and what
  was authorized; cross when writing the handoff.
- `method.engineering-posture` — production boundaries and how much
  work a task needs; cross when the question is scope, not publication.
- `method.design-posture` / `method.stewardship-posture` — the other
  postures; cross when the decision is design- or record-shaped.
