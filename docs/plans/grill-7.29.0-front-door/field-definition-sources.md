# Field-definition sources for the glossary (7.29.0)

The research behind the glossary's Field column, gathered 2026-09-24 for
increment 2 of [the plan](../grill-7.29.0-front-door.md). Each row gives the
field sense in one paraphrased line, the sources behind it and how each source
was reached. The glossary cites from this table and quotes nothing at length. Locations
are given as recorded at retrieval, without a scheme.

Status values:

- **verified**: the page was fetched and read directly on 2026-09-24.
- **secondhand**: the claim comes from search synthesis or a secondary page,
  and the primary text was not opened.
- **unverified**: the source was located and not opened. It supports no claim.
- **not recorded**: no source was sought or found. The glossary says so rather
  than inventing an authority.

| Term | Field sense (paraphrased) | Source | Status |
|---|---|---|---|
| agent | Classical AI: anything that perceives its environment and acts on it. LLM tooling: a system in which the model directs its own process and tool use, as opposed to a fixed code path | Russell and Norvig, *Artificial Intelligence: A Modern Approach*, ch. 2 | secondhand (edition wording differs; page not recorded) |
| | | Anthropic, "Building effective agents", anthropic.com/engineering/building-effective-agents | verified |
| subagent | No pre-LLM sense. A host term: a secondary assistant instance a primary session invokes for a delegated task, with its own context and a summary-only return | Claude Code glossary, code.claude.com/docs/en/glossary | verified |
| | | Claude Code, "Create custom subagents", code.claude.com/docs/en/sub-agents | verified |
| | | OpenCode, "Agents", opencode.ai/docs/agents/ | verified |
| orchestrator | Two senses. Data and CI engineering: the component that runs a workflow definition and tracks task state. Agent patterns: a central model that splits a task at run time, delegates the parts and combines the results | Kestra, "What is an orchestrator?", kestra.io/resources/data/orchestrator | secondhand |
| | | Anthropic, "Building effective agents" (orchestrator-workers) | verified |
| workflow | In the agent-patterns framing, models and tools run along predefined code paths; the contrast is an agent, which picks its path at run time | Anthropic, "Building effective agents" | verified |
| skill | No pre-LLM sense. A folder holding a `SKILL.md` (name and description frontmatter, instruction body, optional resources) that the agent loads on demand | Anthropic, "Agent Skills" overview, platform.claude.com/docs/en/agents-and-tools/agent-skills/overview | verified |
| | | Claude Code glossary | verified |
| | | OpenCode, "Skills", opencode.ai/docs/skills/ | secondhand |
| tool | An action the model can invoke that returns a result it can act on next | Claude Code glossary | verified |
| hook | A user-defined handler that fires at a fixed lifecycle point whatever the model decides; the defining property is that it always fires | Claude Code glossary | verified |
| | | Claude Code, "Automate actions with hooks", code.claude.com/docs/en/hooks-guide | verified |
| system prompt | The instructions given to a model before the conversation, set apart from the user turns that follow. A term of art used operationally, with no formal definition sentence found | Anthropic, "Prompting best practices", platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices | verified (usage only; a definition sentence is not recorded) |
| | | Claude Code, "Create custom subagents" | verified (usage only) |
| kernel | No agent-tooling sense found. The operating-system sense is unrelated. The glossary treats the word as the project's own | none | not recorded |
| context window | The span of tokens a model can attend to in one call, distinct from its training data | Anthropic, Claude platform glossary, platform.claude.com/docs/en/about-claude/glossary | verified |
| | | Claude Code glossary (host overlay) | verified |
| progressive disclosure | UX origin: show the few most important options first and the specialized ones on request. Agent Skills reuses it for context loading: metadata at start, body on trigger, resources on reference | Nielsen, "Progressive Disclosure", Nielsen Norman Group, 2006, nngroup.com/articles/progressive-disclosure/ | verified (one further phrasing attributed to the page is secondhand) |
| | | Anthropic, "Agent Skills" overview | verified |
| knowledge graph | A graph of data meant to accumulate and convey knowledge of the world, with nodes for entities and edges for relations. Its own authors call the definition contested and inclusive | Hogan et al., "Knowledge Graphs", *ACM Computing Surveys* 54(4), 2021; preprint arXiv:2003.02320v6 | verified |
| node | Graph theory: a vertex joined to others by edges; in a knowledge graph, an entity. Covered by the knowledge-graph row; no separate source sought | none | not recorded |
| routing | An agent pattern that classifies an input and sends it to a specialized follow-up rather than treating every input alike | Anthropic, "Building effective agents" | verified |
| specification | States what a system should do apart from how it is built. Specification by example writes it as concrete examples that can run as self-checking tests | Adzic, "Specification by Example, 10 years later", gojko.net/2020/03/17/sbe-10-years.html | verified (the book's own facts are secondhand) |
| | | Fowler, "SpecificationByExample", martinfowler.com/bliki/SpecificationByExample.html | verified (partial) |
| test-first development | A failing test is written before the code that passes it, in a short red, green, refactor cycle | Beck, *Test-Driven Development: By Example*, 2002 | secondhand (book not opened) |
| | | Fowler, "Test Driven Development", martinfowler.com/bliki/TestDrivenDevelopment.html | verified |
| linter | A static-analysis tool that flags errors, style problems and suspect constructs without running the code | Johnson, "Lint, a C Program Checker", Bell Labs CSTR 65, 1978 | secondhand |
| | | SonarSource, "What is a linter?", sonarsource.com/resources/library/linter/ | verified |
| gate | No standard body owns the term; usage is vendor-specific (a quality gate is a set of pass/fail conditions a build must meet). No quality-gate page was fetched | none | not recorded |
| harness | Two unrelated senses. Testing: stubs and drivers that let a component run under test. Agent tooling: the tools, context handling and execution loop that turn a model into an agent | ISTQB glossary, "test harness", glossary.istqb.org | secondhand (page not retrievable) |
| | | Wikipedia, "Test harness" article | verified (its wording only) |
| | | Claude Code glossary, "Agentic harness" | verified |

## Notes for the glossary author

- **harness** carries two live senses that share nothing but the word. The
  glossary names both rather than silently picking one.
- **kernel**, **node** and **gate** have no owning external standard. Their
  Field entries say `not recorded` and point at the seed's own definition.
- **subagent**, **skill** and **hook** are host terms. Their exact behavior
  differs by host, so a Field entry states the common shape only and leaves
  host detail to the host capability matrix (plan §11).
- §1 of the plan lists Copilot and Codex `AGENTS.md` pages among the sources.
  This research reached neither, so no row above cites them.
- One academic source on agent harnesses was found by search and not opened.
  It is left out of the table.
