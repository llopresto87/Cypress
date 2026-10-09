# CYPRESS Documentation

Human-readable documentation for the CYPRESS seed system (version 8.1.2).

## Start here

- [../DOCUMENTATION.md](../DOCUMENTATION.md) is the master guide. Read this
  first. It explains what CYPRESS is, the core mental model, the eight rules, the
  tiers, the knowledge graph, delegation, the reverse loop, install/grow, tests,
  and a glossary.

## Feature guides

| File | Covers |
|------|--------|
| [whats-new-8.md](whats-new-8.md) | What 8.0 and 8.1 added, feature by feature, each linked to its guide or reference section. |
| [source-index.md](source-index.md) | Guide to the source index (`docs/graph/source-index.py`, 8.1.0): the queries `build`, `impact`, `affected-tests`, `anchors` and `symbols`, `--history` and `anchors --moved`, how to read an answer, the build report that install, graft and grow print (8.1.2), the cache, the plant config, the `repo:` rule, and when the protocols call it. |
| [corpus-placement.md](corpus-placement.md) | Guide to placing corpus pages (`install.sh --expertise`, 8.0.0): proposing, placing, the record in `.cypress/seed.json`, refresh on later installs, and `--check`. |

## Deep-dive references

| File | Covers |
|------|--------|
| [agents-reference.md](agents-reference.md) | All 20 specialist agents: per-agent charter, model class, tools, routing triggers, owned facts, edges, and coordinator/leaf status. |
| [protocols-reference.md](protocols-reference.md) | All 17 protocols: owned facts, edges, triggers, and a step-by-step walkthrough of each workflow. |
| [skills-and-templates-reference.md](skills-and-templates-reference.md) | The 16 skills, the artifact templates, the knowledge-graph node contract and linters, and the delegation and brief templates. |
| [corpora-and-integrations-reference.md](corpora-and-integrations-reference.md) | The corpora (library, legal, tool, agent, skill) with inventories, and the tool integrations (Claude Code, Prime Agent, opencode, Codex, GitHub Copilot). |
| [host-capability-matrix.md](host-capability-matrix.md) | The same hosts against each capability it tracks (kernel loading, delegation, recursion bound, hooks, tool allowlists, model selection, …). Each cell is classified as mechanically enforced, brief-enforced, degraded, projected, observed, or unsupported, so parity of method and parity of enforcement are tracked apart. |

## Authoritative sources

This documentation is a companion. The source of truth is:

- `manifest.json`: the machine-readable catalog of every seed file.
- Each node's own frontmatter (`id`, `owns`, `load_when`, `routing_triggers`).
- `README.md`, `INSTALL.md`, `CHANGELOG.md`.

## License

MIT. See [`../LICENSE`](../LICENSE). Copyright (c) 2026 Luigi Lopresto.
