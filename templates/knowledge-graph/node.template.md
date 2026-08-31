<!--
Template: knowledge-graph/node.template.md
Lives at: docs/graph/nodes/<id>.md   (filename MUST equal the id)
Used: one file per node. Copy an existing node in preference to this
when the graph already has peers of the same kind.
Contract: docs/graph/_schema.md — the linter enforces it.
-->
---
id: {{kind}}.{{name}}
tier: 2
kind: {{kind}}
title: {{name}} — one-line description
repo: {{repo-or-path}}          # optional; omit for non-code subjects
owns:                           # fact-keys this node is the SOLE home of
  - {{name}}.responsibility
  - {{name}}.{{fact}}
requires:                       # loaded transitively with this node; keep minimal
  - {{kind}}.{{dependency}}
peers:                          # NOT loaded unless the task crosses into them
  - {{kind}}.{{neighbour}}
libraries:                      # Tier-3 pages this node depends on (optional; omit if none)
  - {{library-name}}
artifacts:                      # graph-relative knowledge leaves to load when needed
  - architecture/{{subject}}.md
  - api/{{contract}}.md
load_when:                      # the phrases a developer would actually type
  - "editing {{repo-or-path}}/**"
  - "{{concept}}, {{synonym}}, {{the phrase}}"
est_tokens: {{honest-estimate}}
---

# {{name}}

## What this is

Two or three sentences. What this subject is and its boundary.

## What you must know

The facts this node `owns`. Terse — bullets, tables, code. No prose
padding. Do not restate a fact another node owns; link to it.

## Sharp edges

What will bite you here. Date each entry when it was discovered.

- **YYYY-MM-DD — <title>:** what bites, what to do instead.

## Where the code is

Concrete paths, not descriptions of paths.

- `{{path/to/thing}}` — <what lives here>

## Neighbours

One line per `peer`: why it exists and when a task should cross to it.

- `{{peer-id}}` — <why> — cross when <condition>.
