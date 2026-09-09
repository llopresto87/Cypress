---
id: expertise.{{slug}}
tier: 2
kind: expertise
origin: project
title: {{slug}} — when this expertise is in play, and what it composes
owns:
  - {{slug}}.applicability
  - {{slug}}.composition
requires:
  - {{the parent expertise, if this is a sub-expertise; else leave the key empty}}
composes:
  - {{a sub-expertise that applies under a condition of its own; else leave the key empty}}
libraries:
  - {{slug}}                        # the pin home; required for a pinned stack element
artifacts:
  - best-practices/{{slug}}.md      # the standard and this project's stance
load_when:
  - "{{the ≥3-character phrases a developer types when THIS is in play — never the family's words}}"
  - "{{another; a version-qualified child carries the target tokens, e.g. net8.0}}"
est_tokens: {{honest estimate of the body}}
---

<!--
Template: docs/nodes/_expertise.template.md
Lives at: docs/graph/nodes/expertise.<slug>.md   (filename MUST equal the id)
Used: one file per core or significant language, runtime, framework,
dependency, infrastructure component, or datastore the stack inventory
carries (growth-audit plans the path; grow Phase 4 authors it from ledger
§5, §9, §14 and the same retrieved sources as its libraries/ and
best-practices/ leaves). The node owns applicability and composition and
nothing else — it routes to the pin and the standard, it never restates
them. Agents reach it through the router: the brief's task line is what
composes it in, and the Depth section tells each reader which leaf to open.
Contract: docs/graph/_schema.md — "Node kinds" (expertise), "Key semantics"
(composes), rules 15–19. The leading underscore keeps this blank form out of
the linter; the node you copy it to must not carry one.
-->

# {{slug}} — when this expertise is in play

## In play for

{{The work that reaches this expertise in this project: the task shapes, the
subsystems they land in, and what the plant actually builds with it. `load_when`
above carries the trigger words; this tells a reader what they have walked
into.}}

## Do not without

{{What goes wrong when that work is done without this expertise — the specific
damage, named, not a general warning to be careful. This is the applicability
fact the node owns, so it is stated here and nowhere else.}}

## Composition

One line per composed child, naming the condition it applies under. The router
descends only when the task names, exactly, a term the child carries and this
node does not, so a condition written in this node's own family words composes
nothing.

- `expertise.{{child-slug}}` — when {{the condition, in the child's own
  vocabulary: the sub-area the task has to reach}}

{{A node that composes nothing says so in one line — "Nothing: this is a leaf
expertise" — because composition is a fact this node owns and an unanswered
section reads exactly like an unopened one.}}

## Version in play

The pinned major(s) live in `libraries/<slug>.md` §0 — read the pin before
writing anything against this stack. The pins are often old on purpose; the
wiki is authoritative over memory. Behaviour that differs between majors is
recorded there (§5 sharp edges, §6 deprecations), never here. Where this
plant runs more than one major, the composition above lists one child per
major; load the one whose target the task names.

## Depth

API and pins → `libraries/{{slug}}.md` · the standard and this project's
stance → `best-practices/{{slug}}.md` · this project's own conventions →
`stack.{{slug}}`

One line per purpose, so a reader of any identity opens the one leaf its work
needs. Name only leaves this node actually links to, and restate none of them.

## Example

```yaml
---
id: expertise.dotnet
tier: 2
kind: expertise
origin: project
title: dotnet — when .NET expertise is in play, and what it composes
owns:
  - dotnet.applicability
  - dotnet.composition
requires:
composes:
  - expertise.ef-core
  - expertise.serilog
libraries:
  - dotnet
artifacts:
  - best-practices/dotnet.md
load_when:
  - "dotnet, csharp, target framework, nuget package reference"
  - "async await, dependency injection container, hosted service"
est_tokens: 260
---
```

…and the two sections that carry the routing:

> ## Composition
>
> - `expertise.ef-core` — when the task reaches persistence: mapping,
>   DbContext, a query.
> - `expertise.serilog` — when the task reaches structured logging: sinks,
>   enrichers, a log template.
>
> ## Depth
>
> API and pins → `libraries/dotnet.md` · the standard and this project's
> stance → `best-practices/dotnet.md` · this project's own conventions →
> `stack.dotnet`
