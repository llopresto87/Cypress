# CYPRESS Documentation

Human-readable documentation for the CYPRESS seed system (version 6.9.2).

## Start here

- **[../DOCUMENTATION.md](../DOCUMENTATION.md)** — the master guide. Read this
  first. It explains what CYPRESS is, the core mental model, the eight rules, the
  tiers, the knowledge graph, delegation, the reverse loop, install/grow, tests,
  and a glossary.

## Deep-dive references

| File | Covers |
|------|--------|
| **[agents-reference.md](agents-reference.md)** | All 18 specialist agents — per-agent charter, model class, tools, routing triggers, owned facts, edges, and coordinator/leaf status. |
| **[protocols-reference.md](protocols-reference.md)** | All 15 protocols — owned facts, edges, triggers, and a detailed step-by-step walkthrough of each workflow. |
| **[skills-and-templates-reference.md](skills-and-templates-reference.md)** | The 13 skills, the 10 artifact templates, the knowledge-graph node contract and linters, and the 9 delegation/brief templates. |
| **[corpora-and-integrations-reference.md](corpora-and-integrations-reference.md)** | The 5 harvested corpora (library, legal, tool, agent, skill) with inventories, and the 5 tool integrations (Claude Code, Prime Agent, opencode, Codex, GitHub Copilot). |

## Authoritative sources

This documentation is a companion, not the source of truth. When in doubt, read:

- `manifest.json` — the machine-readable catalog of every seed file.
- Each node's own frontmatter (`id`, `owns`, `load_when`, `routing_triggers`).
- `README.md`, `INSTALL.md`, `CHANGELOG.md`.

## License

MIT — see [`../LICENSE`](../LICENSE). Copyright (c) 2026 Luigi Lopresto.
