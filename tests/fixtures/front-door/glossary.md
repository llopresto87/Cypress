## 15. Glossary
<a id="glossary"></a>

Each entry lists the forms of a word, what it means in this repository, what it usually means elsewhere, where it lives, its enforcement class, how far the two meanings diverge, and the record behind it.

### agent
<a id="term-agent"></a>

- **Forms:** agent, agents
- **Here:** A worker with its own system prompt, tool list and model class, started by a session to do one piece of work.
- **Field:** software acting on a user's behalf with some autonomy (field usage; status: not recorded)
- **Implemented at:** `agents/`. An install produces `.claude/agents/` (`project_agents`).
- **Enforcement:** **not a control**
- **Divergence:** **narrower**: here it is always one of the roster files
- **Why:** ADR-0002

### subagent
<a id="term-subagent"></a>

- **Forms:** subagent, subagents
- **Here:** A worker started by another session rather than by the person at the keyboard, running with a context of its own.
- **Field:** a secondary assistant delegated a task by a primary one (host documentation; status: not recorded)
- **Implemented at:** `core/method/delegation.md`
- **Enforcement:** **not a control**
- **Divergence:** **same**
- **Why:** not recorded

### orchestrator
<a id="term-orchestrator"></a>

- **Forms:** orchestrator, orchestrators
- **Here:** The session role that routes work, writes briefs for workers and accepts what they return.
- **Field:** a component coordinating several services or processes (field usage; status: not recorded)
- **Implemented at:** `agents/00-orchestrator.md`
- **Enforcement:** **not a control**
- **Divergence:** **narrower**
- **Why:** ADR-0002

### workflow
<a id="term-workflow"></a>

- **Forms:** workflow, workflows
- **Here:** An ordered list of steps the model reads and carries out itself, written as Markdown files rather than code.
- **Field:** a repeatable sequence of tasks, often run by an engine (field usage; status: not recorded)
- **Implemented at:** `protocols/`
- **Enforcement:** **not a control**
- **Divergence:** **narrower**
- **Why:** not recorded

### skill
<a id="term-skill"></a>

- **Forms:** skill, skills
- **Here:** A skill is a Markdown procedure that the working session reads into its own context, and it grants no extra tools. An [agent](#term-agent) differs, because it runs as a separate worker with a context, tool list and model class of its own.
- **Field:** a packaged capability an assistant can call on (host documentation; status: not recorded)
- **Implemented at:** `skills/`
- **Enforcement:** **not a control**
- **Divergence:** **narrower**
- **Why:** ADR-0004

### tool
<a id="term-tool"></a>

- **Forms:** tool, tools
- **Here:** Two senses: a program the model may call through its harness, and a stdlib script shipped in the `tools/` directory of this repository; README uses the first sense.
- **Field:** a function or program an assistant invokes (host documentation; status: not recorded)
- **Implemented at:** `tools/`
- **Enforcement:** **not a control**
- **Divergence:** **broader**
- **Why:** not recorded

### hook
<a id="term-hook"></a>

- **Forms:** hook, hooks
- **Here:** A script the harness runs on an event such as a new prompt or a shell command; one that only adds text to the context holds nothing.
- **Field:** code run at a named point in another program (field usage; status: not recorded)
- **Implemented at:** `integrations/claude-code/route-hook.py`, `integrations/claude-code/bound-hook.py`
- **Enforcement:** **not a control** for a hook that only adds text ([route hook](#enf-route-hook))
- **Divergence:** **narrower**
- **Why:** ADR-0003

### kernel
<a id="term-kernel"></a>

- **Forms:** kernel, kernels
- **Here:** The one instruction file every session loads before anything else, kept small because each session pays for it.
- **Field:** the core of an operating system (field usage; status: not recorded)
- **Implemented at:** `core/AGENTS.md`. An install produces `CLAUDE.md` (`place_kernel`).
- **Enforcement:** **soft** ([kernel budget](#enf-kernel-budget))
- **Divergence:** **different**
- **Why:** ADR-0010

### context window
<a id="term-context-window"></a>

- **Forms:** context window, context windows
- **Here:** The text a model can attend to in one call, counted in tokens, which every loaded file consumes.
- **Field:** the span of tokens a model processes at once (field usage; status: not recorded)
- **Implemented at:** n/a — a property of the model, not of this repository
- **Enforcement:** **not a control**
- **Divergence:** **same**
- **Why:** not recorded

### progressive disclosure
<a id="term-progressive-disclosure"></a>

- **Forms:** progressive disclosure
- **Here:** Loading only the nodes a task names, and the edges they list, instead of reading the whole graph up front.
- **Field:** showing detail only when a user asks for it (interface design usage; status: not recorded)
- **Implemented at:** `templates/knowledge-graph/graph-lint.py`
- **Enforcement:** **not a control**
- **Divergence:** **narrower**
- **Why:** ADR-0004

### knowledge graph
<a id="term-knowledge-graph"></a>

- **Forms:** knowledge graph, knowledge graphs
- **Here:** The folder of linked Markdown nodes an install places under docs/graph, with a router index read first.
- **Field:** entities and typed relations stored for querying (field usage; status: not recorded)
- **Implemented at:** `templates/knowledge-graph/`. An install produces `docs/graph/` (`place_graph_machinery`).
- **Enforcement:** **not a control**
- **Divergence:** **different**
- **Why:** ADR-0004

### node
<a id="term-node"></a>

- **Forms:** node, nodes
- **Here:** One Markdown file with routing frontmatter that covers a single subject in the graph.
- **Field:** a vertex of a graph (field usage; status: not recorded)
- **Implemented at:** `templates/knowledge-graph/node.template.md`
- **Enforcement:** **not a control**
- **Divergence:** **narrower**
- **Why:** ADR-0004

### router
<a id="term-router"></a>

- **Forms:** router, routers
- **Here:** The index file a session opens first to choose which few nodes to read for the task at hand.
- **Field:** a device forwarding network packets (field usage; status: not recorded)
- **Implemented at:** `templates/knowledge-graph/index.md`
- **Enforcement:** **not a control**
- **Divergence:** **different**
- **Why:** ADR-0001

### routing
<a id="term-routing"></a>

- **Forms:** routing
- **Here:** Choosing, from the index and a task description, which files or which specialist a piece of work goes to.
- **Field:** selecting a path through a network (field usage; status: not recorded)
- **Implemented at:** `templates/knowledge-graph/graph-lint.py`
- **Enforcement:** **not a control**
- **Divergence:** **narrower**
- **Why:** ADR-0001

### specification
<a id="term-specification"></a>

- **Forms:** specification, specifications
- **Here:** A Markdown file under docs/specs that states contracts as Given, When and Then before any code is written.
- **Field:** a precise statement of what a system must do (field usage; status: not recorded)
- **Implemented at:** `templates/spec.template.md`
- **Enforcement:** **not a control**
- **Divergence:** **narrower**
- **Why:** not recorded

### test-first development
<a id="term-test-first"></a>

- **Forms:** test-first development, test-first
- **Here:** Writing a failing test that names a contract, watching it fail, then writing the code that makes it pass.
- **Field:** writing tests ahead of the code they cover (field usage; status: not recorded)
- **Implemented at:** `protocols/test-first.md`
- **Enforcement:** **not a control**
- **Divergence:** **same**
- **Why:** not recorded

### gate
<a id="term-gate"></a>

- **Forms:** gate, gates
- **Here:** Two senses: one step of the test run of this repository, and one row of a protocol checklist that a named judge signs; README uses the first sense.
- **Field:** a checkpoint a change passes before release (field usage; status: not recorded)
- **Implemented at:** `tests/run.sh`
- **Enforcement:** **detective** ([seed test run](#enf-seed-gate))
- **Divergence:** **broader**
- **Why:** ADR-0003

### linter
<a id="term-linter"></a>

- **Forms:** linter, linters
- **Here:** A small stdlib script that reads files and prints findings, and exits non-zero when it finds any.
- **Field:** a static checker for suspicious code or text (field usage; status: not recorded)
- **Implemented at:** `templates/knowledge-graph/graph-lint.py`, `tools/prose-lint.py`
- **Enforcement:** **soft** ([graph lint](#enf-graph-lint))
- **Divergence:** **same**
- **Why:** not recorded

### harness
<a id="term-harness"></a>

- **Forms:** harness, harnesses
- **Here:** Two senses: the coding application that runs the model for you, such as a terminal assistant, and a test harness; README uses the first sense.
- **Field:** the scaffolding that runs a program under test (field usage; status: not recorded)
- **Implemented at:** `integrations/`
- **Enforcement:** **not a control**
- **Divergence:** **different**
- **Why:** ADR-0009

### seed
<a id="term-seed"></a>

- **Forms:** seed, seeds
- **Here:** This repository as a product: the installer, the method files and the scripts that an install copies into a project.
- **Field:** no standard meaning.
- **Implemented at:** `install.sh`, `manifest.json`
- **Enforcement:** **not a control**
- **Divergence:** **no standard meaning**
- **Why:** not recorded

### plant
<a id="term-plant"></a>

- **Forms:** plant, plants
- **Here:** A repository after the [seed](#term-seed) was installed into it and [grown](#term-growth).
- **Field:** no standard meaning.
- **Implemented at:** `install.sh`, `protocols/grow.md`. An install produces `.cypress/seed.json` (`write_seed_stamp`).
- **Enforcement:** **not a control**
- **Divergence:** **no standard meaning**
- **Why:** not recorded

### growth
<a id="term-growth"></a>

- **Forms:** growth
- **Here:** The one-time pass in which a session reads the source of a project and writes its knowledge graph.
- **Field:** no standard meaning.
- **Implemented at:** `protocols/grow.md`
- **Enforcement:** **not a control**
- **Divergence:** **no standard meaning**
- **Why:** not recorded

### graft
<a id="term-graft"></a>

- **Forms:** graft, grafts
- **Here:** Applying a newer release of the method to a project first set up from an older one, decided file by file by its owner.
- **Field:** no standard meaning.
- **Implemented at:** `protocols/graft.md`, `tools/graft-audit.py`
- **Enforcement:** **not a control**
- **Divergence:** **no standard meaning**
- **Why:** not recorded

### harvest
<a id="term-harvest"></a>

- **Forms:** harvest, harvests
- **Here:** Carrying a lesson learned in one project back into this repository, stripped of anything that identifies that project.
- **Field:** no standard meaning.
- **Implemented at:** `protocols/harvest.md`
- **Enforcement:** **not a control**
- **Divergence:** **no standard meaning**
- **Why:** not recorded

### canonize
<a id="term-canonize"></a>

- **Forms:** canonize, canonizes, canonized
- **Here:** Closing a task by writing what it taught into the graph, or by recording that it taught nothing new.
- **Field:** no standard meaning.
- **Implemented at:** `protocols/canonize.md`
- **Enforcement:** **judgment** ([close-out](#enf-canonize))
- **Divergence:** **no standard meaning**
- **Why:** not recorded

### tier
<a id="term-tier"></a>

- **Forms:** tier, tiers
- **Here:** Two senses: the risk class T0 to T3 given to a task, and the load level of a graph node; README uses the first sense.
- **Field:** a level in a ranked arrangement (field usage; status: not recorded)
- **Implemented at:** `core/method/tiers.md`
- **Enforcement:** **judgment** ([tier classification](#enf-tier-classification))
- **Divergence:** **different**
- **Why:** ADR-0006

### protocol
<a id="term-protocol"></a>

- **Forms:** protocol, protocols
- **Here:** A Markdown file that lists the ordered steps and exit checks for one kind of task, entered by name.
- **Field:** a set of rules for exchanging messages (field usage; status: not recorded)
- **Implemented at:** `protocols/`
- **Enforcement:** **not a control**
- **Divergence:** **narrower**
- **Why:** not recorded

### corpus
<a id="term-corpus"></a>

- **Forms:** corpus, corpora
- **Here:** Two senses: a shipped folder of reference pages read only when a task calls for them, and a set of test rows; README uses the first sense.
- **Field:** a body of texts collected for study (field usage; status: not recorded)
- **Implemented at:** `library-corpus/`, `legal-corpus/`
- **Enforcement:** **not a control**
- **Divergence:** **narrower**
- **Why:** not recorded

### handback
<a id="term-handback"></a>

- **Forms:** handback, handbacks
- **Here:** The one message a worker returns when its spawn ends, naming who produced it and what comes next.
- **Field:** a return of control to a previous handler (field usage; status: not recorded)
- **Implemented at:** `templates/prompts/handback-payload.md`
- **Enforcement:** **not a control**
- **Divergence:** **different**
- **Why:** not recorded

### coordinator
<a id="term-coordinator"></a>

- **Forms:** coordinator, coordinators
- **Here:** An agent allowed to start other workers, up to a fixed depth written in its frontmatter.
- **Field:** a person or process that organizes others (field usage; status: not recorded)
- **Implemented at:** `core/method/delegation.md`
- **Enforcement:** **not a control**
- **Divergence:** **narrower**
- **Why:** ADR-0002

### leaf
<a id="term-leaf"></a>

- **Forms:** leaf, leaves
- **Here:** Two senses: an agent that starts no workers and hands back at the edge of its domain, and a file at the bottom of a folder tree; README uses the first sense.
- **Field:** a node with no children in a tree (field usage; status: not recorded)
- **Implemented at:** `agents/`
- **Enforcement:** **judgment** ([leaf spawn bar](#enf-leaf-cannot-spawn))
- **Divergence:** **different**
- **Why:** ADR-0002

### specialist
<a id="term-specialist"></a>

- **Forms:** specialist, specialists
- **Here:** One of the roster agents this repository ships, each with a charter and a routing description.
- **Field:** a person with expertise in one area (field usage; status: not recorded)
- **Implemented at:** `agents/`
- **Enforcement:** **not a control**
- **Divergence:** **narrower**
- **Why:** not recorded

### expert
<a id="term-expert"></a>

- **Forms:** expert, experts
- **Here:** A role written for one project and added to the roster of that project, not to the shipped roster.
- **Field:** a person with deep knowledge of a subject (field usage; status: not recorded)
- **Implemented at:** `templates/agent.template.md`
- **Enforcement:** **not a control**
- **Divergence:** **narrower**
- **Why:** ADR-0005

### steward
<a id="term-steward"></a>

- **Forms:** steward, stewards
- **Here:** The person who owns the project and alone decides the choices that are reserved to them.
- **Field:** a person managing property for another (field usage; status: not recorded)
- **Implemented at:** `core/method/stewardship-posture.md`
- **Enforcement:** **not a control**
- **Divergence:** **narrower**
- **Why:** not recorded

### one home per fact
<a id="term-one-home-per-fact"></a>

- **Forms:** one home per fact
- **Here:** Each fact is written in exactly one file, and every other file that needs it links there.
- **Field:** no standard meaning.
- **Implemented at:** `tests/seed-lint.py`
- **Enforcement:** **not a control**
- **Divergence:** **no standard meaning**
- **Why:** ADR-0004

### turn
<a id="term-turn"></a>

- **Forms:** turn, turns
- **Here:** The span from one worker being started to its handback arriving, counted for a single worker.
- **Field:** one exchange in a conversation with a model (field usage; status: not recorded)
- **Implemented at:** `core/method/delegation.md`
- **Enforcement:** **not a control**
- **Divergence:** **different**
- **Why:** not recorded

### toolcraft
<a id="term-toolcraft"></a>

- **Forms:** toolcraft
- **Here:** The habit of turning an operation that keeps recurring into a tested, cataloged script.
- **Field:** no standard meaning.
- **Implemented at:** `skills/toolcraft/SKILL.md`
- **Enforcement:** **not a control**
- **Divergence:** **no standard meaning**
- **Why:** not recorded

### machinery
<a id="term-machinery"></a>

- **Forms:** machinery
- **Here:** The method files an install places in every project: protocols, skills, agents, templates and core method notes.
- **Field:** no standard meaning.
- **Implemented at:** `core/method/`, `protocols/`
- **Enforcement:** **not a control**
- **Divergence:** **no standard meaning**
- **Why:** ADR-0004

### brief
<a id="term-brief"></a>

- **Forms:** brief, briefs
- **Here:** The prompt a session writes for one worker, carrying the task, its limits and the graph discipline text.
- **Field:** a short set of instructions for a job (field usage; status: not recorded)
- **Implemented at:** `templates/prompts/graph-session-bootstrap.md`
- **Enforcement:** **not a control**
- **Divergence:** **narrower**
- **Why:** not recorded

### reverse loop
<a id="term-reverse-loop"></a>

- **Forms:** reverse loop
- **Here:** The path by which lessons move back out of projects: [canonize](#term-canonize) inside one, then [harvest](#term-harvest) into this repository and [graft](#term-graft) out to others.
- **Field:** no standard meaning.
- **Implemented at:** `protocols/canonize.md`, `protocols/harvest.md`, `protocols/graft.md`
- **Enforcement:** **not a control**
- **Divergence:** **no standard meaning**
- **Why:** not recorded

