---
id: crosscut.operator
tier: 2
kind: crosscut
origin: project
title: operator — how this plant's owner works with agents, in the owner's own dated words
owns:
  - operator.working-contract
  - operator.effort-tiers
  - operator.command-vocabulary
  - operator.register
requires:
peers:
  - {{a crosscut.operator-<topic> child, once the node is split; else leave the key empty}}
load_when:
  - "starting any task for the plant owner, how does the owner want this done"
  - "the owner said remember, from now on, always, a standing working rule"
  - "should I ask the owner first, or decide and proceed"
  - "what does the owner mean by {{a recurring verb of theirs}}"
  - "go deep or keep it minimal, how much effort does the owner want"
  - "{{another phrase this owner's tasks start with}}"
est_tokens: {{honest estimate of the body}}
---

<!--
Template: docs/nodes/_operator.template.md
Lives at: docs/graph/nodes/crosscut.operator.md   (filename MUST equal the id)
Used: once per plant, when the owner states a working rule for good
("remember …", "from now on …", "always …") and the rule is about how agents
work with this owner, not about the project. method.stewardship-posture decides
where such a rule goes; this is the node it names. Authored from recorded owner
corrections and instructions only. A rule nobody can quote is not written.
Kind: `crosscut`. The contract spans every subsystem and every task, which is
what the kind means (docs/graph/_schema.md, "Node kinds"), and `crosscut` is in
every plant's graph-lint KINDS, so no plant needs a linter change to carry it.
The leading underscore keeps this blank form out of the linter; the node you
copy it to must not carry one.
-->

# Operator: how the plant owner works with agents

## What this is

The owner's standing working contract: the rules they stated for good about
how agents should work with them. It holds only what the seed does not already
own. Where the seed owns a rule, this node names that home in one line and
adds only what is specific to this owner.

Every rule is authored from something the owner said, and carries the quote.
Style is not inferred from how the owner writes, and a rule is not generalized
beyond what the owner said. When the owner reverses a rule, rewrite the rule
and add the reversing quote as its newest evidence. A reversal is the
requirement moving, not a mistake to argue about.

## Facts this node does not hold

- **Commit attribution, deliverable language, comment language.** These are
  the `plant:` block in `docs/graph/index.md` (`commit_attribution`,
  `deliverable_language`, `comment_language`). Read them there. This node may
  add only what a declaration cannot say, such as what the owner expects of
  prose in that language.
- **Where a "remember …" rule goes, and what harness memory may keep:**
  `method.stewardship-posture`.
- **Risk tiers and the process each one costs:** `method.tiers`.
- **What needs explicit confirmation before a destructive action:** the
  kernel's boundaries. An owner rule here can widen that list, never narrow
  it.
- **How deliverables read, and numbered decisions:** `method.prose-posture`,
  `protocol.deliver` (`deliver.numbered-decisions`).

## Standing rules

One entry per rule, stated as an instruction. The strength tag says how much
evidence stands behind it:

- `canonical`: restated across sessions, in the owner's own words each time.
- `strong`: stated once, with emphasis.
- `contextual`: holds only under a condition, and the entry names it.

### {{The rule, as an instruction}} (`{{canonical | strong | contextual}}`)

{{One short paragraph: what to do, what not to do, and, for a contextual rule,
the condition. Name the seed home if the rule sharpens one.}}

> "{{the owner's words, verbatim, in the language they used}}" ({{YYYY-MM-DD}})

## Effort tiers, in the owner's words

The owner declares effort; agents do not guess it. Record the words the owner
uses for each tier and what each one authorizes.

| Tier | The owner's words | What it authorizes | What it suspends |
|---|---|---|---|
| deep | {{e.g. their phrase for "spend effort now to save later"}} | {{large rewrites, exhaustive search}} | {{the minimal-change default}} |
| default | {{what they say, or "nothing stated"}} | the seed's defaults | nothing |
| minimal | {{their phrase for "shortest correct path" or an emergency}} | {{a minimal diff, skipped ceremony, stated as skipped}} | {{what may be skipped, and what may not}} |

An effort tier never moves the risk tier. "Minimal" shortens the path inside a
tier and does not turn a T3 change into a T2 one (`method.tiers`). {{The
owner's rule when no tier is stated, if they gave one; else "not recorded".}}

## Command vocabulary

What this owner's recurring verbs mean. List a verb only when the evidence
shows it used the same way more than once. For a verb that is not listed, take
the literal meaning or ask. Record which verbs authorize changes and which
authorize only reading, because that is the line agents most often misread.

### `{{verb}}`

- **Means:** {{the outcome the owner expects}}
- **Implies:** {{what comes with it without being said}}
- **Does not mean:** {{the tempting reading that is wrong}}
- **Done when:** {{the state the owner checks}}

> "{{the owner's words}}" ({{YYYY-MM-DD}})

## Register

- **How the owner writes to agents:** {{the register, and anything to read
  through, such as typos or a mix of languages}}. Describe it here; never
  mirror it in deliverables.
- **How the owner wants reports:** {{e.g. pending actions or history,
  classified or flat, where on disk they live}}
- **When the owner wants questions:** {{e.g. many at planning, none during
  execution; batched and short}}

## Splitting this node

When the body nears the graph's size ceiling, split it by topic into
`crosscut.operator-<topic>` children (communication, autonomy, investigation,
implementation, vocabulary). Each child `requires: crosscut.operator` and owns
its topic's fact keys. This node keeps the working contract and the effort
tiers, and names each child under Neighbours.

## Neighbours

- `method.stewardship-posture`: where standing rules go.
- `{{crosscut.operator-<topic>}}`: {{what it holds}}; else remove this line.
