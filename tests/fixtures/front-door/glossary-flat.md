## 15. Glossary

- **Seed**: this repository; the shippable product.
- **Plant**: a target project after the seed has been installed and grown into it.
- **Growth**: the one-time process that reads the target's source and builds its
  `docs/graph/`.
- **Kernel**: `core/AGENTS.md`; the one always-loaded bootstrap file.
- **Node**: one unit of graph knowledge; ~one subject; carries routable
  frontmatter.
- **Router**: `docs/graph/index.md`; the Tier-1 index opened first on every task.
- **One home per fact**: every fact lives in exactly one node; everything else
  links.
- **Tier (task)**: T0–T3 risk classification; the unit of process proportionality.
- **Load-tier**: the node `tier:` field; which tier of the graph a node sits in.
- **Model class**: sonnet (read-only) vs opus (authoring); the `model:` field.
- **Specialist**: a member of the shipped roster.
- **Expert**: a role commissioned for a specific project; joins the project's
  roster, never the seed's.
- **Coordinator**: one of the six agents that hold a depth-capped `Task`.
- **Leaf**: a Task-less agent that STOPs and hands back at a domain boundary.
- **Turn**: one spawn → return cycle of a single worker.
- **Handback**: the payload a worker returns exactly once per spawn; carries
  `produced_by` attribution.
- **Steward**: the user acting as project owner (in harvest/graft).
- **Corpus**: harvested, durable, project-agnostic reference material not loaded
  by default.
- **Toolcraft**: the doctrine that recurring operations become durable, cataloged
  tools.

