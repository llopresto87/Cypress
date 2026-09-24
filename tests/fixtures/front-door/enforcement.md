## 17. What is enforced, and how
<a id="enforcement"></a>

Each row names one mechanism, the file that implements it, its class in the vocabulary of ADR-0003, and what it can miss. Host differences are recorded in the host capability matrix, which the Detail cell links.

| Mechanism | Artifact | Class | What it can miss | Detail |
|---|---|---|---|---|
| <a id="enf-kernel-load"></a>The harness loads the kernel file at the start of every session | `core/AGENTS.md` | **hard** | A harness that looks for a different file name loads nothing from it | [host capability matrix](documentation/host-capability-matrix.md) |
| <a id="enf-kernel-budget"></a>A byte budget on the kernel file in the test run of this repository | `tests/seed-lint.py` | **soft** | It holds only in this repository's own test run; a project may grow its copy freely | none |
| <a id="enf-tool-allowlist"></a>Each agent file lists the tools its worker may call | `agents/`, `integrations/claude-code/agent-lint.py` | **hard** on hosts that honour per-agent tools; **judgment** under role emulation | A role granted Bash can still write files; role emulation and an omitted `tools:` line both leave the list unread | [host capability matrix](documentation/host-capability-matrix.md) |
| <a id="enf-leaf-cannot-spawn"></a>A leaf agent is given no tool that starts workers | `agents/` | **hard** where the host reads the tool list; **judgment** under role emulation | A spawn tool under another name, role emulation, and an omitted `tools:` line | [host capability matrix](documentation/host-capability-matrix.md) |
| <a id="enf-delegation-frontmatter"></a>Delegation fields in agent frontmatter agree with the tool list | `integrations/claude-code/agent-lint.py` | **soft** | It reads the files, not what a running session does | none |
| <a id="enf-route-hook"></a>A prompt hook adds routing text to the context | `integrations/claude-code/route-hook.py` | **not a control** | It fires and holds nothing; the model may ignore the text | [host capability matrix](documentation/host-capability-matrix.md) |
| <a id="enf-status-hook"></a>A status hook adds the task state to the context | `integrations/claude-code/status-hook.py` | **not a control** | It fires and holds nothing; the model may ignore the text | [host capability matrix](documentation/host-capability-matrix.md) |
| <a id="enf-pre-bash-guard"></a>A command hook matches shell commands against a pattern list | `integrations/claude-code/bound-hook.py` | **hard** for a matched command on a host that fires the hook; **detective** elsewhere | It fails open on input it cannot parse, indirection evades its patterns, and hosts that do not fire the hook get nothing from it | [host capability matrix](documentation/host-capability-matrix.md) |
| <a id="enf-injection-dedup"></a>The route hook skips text it already added in the same session | `integrations/claude-code/route-hook.py` | **soft** | A session that clears its state sees the text again | none |
| <a id="enf-backup-before-replace"></a>The installer keeps a timestamped copy of a differing file before replacing it | `install.sh` | **soft** | The install stamp `.cypress/seed.json` is replaced without a copy | none |
| <a id="enf-plant-files-kept"></a>The installer leaves project files outside its target paths alone | `install.sh` | **soft** | A project file placed at a target path is treated like any other differing file | none |
| <a id="enf-install-preflight"></a>The installer checks every destination before writing anything | `install.sh` | **soft** | A change made after the check and before the write is not seen | none |
| <a id="enf-install-stamp"></a>The installer records what it placed in a stamp file | `install.sh` | **soft** | The stamp says what was placed, not what a later edit changed | none |
| <a id="enf-registration-notice"></a>The installer prints a notice that new workers appear after a new session | `install.sh` | **not a control** | A notice nobody reads changes nothing | [host capability matrix](documentation/host-capability-matrix.md) |
| <a id="enf-graph-lint"></a>The graph linter checks node frontmatter and edges | `templates/knowledge-graph/graph-lint.py` | **soft** | It runs only when someone runs it or wires it into CI | none |
| <a id="enf-spec-lint"></a>The spec linter checks contract shape and test mapping | `templates/knowledge-graph/spec-lint.py` | **soft** | It checks shape and mapping, not whether a contract is right | none |
| <a id="enf-grill-lint"></a>The plan linter checks the plan-of-record sections | `templates/knowledge-graph/grill-lint.py` | **soft** | It checks sections, not the quality of a decision | none |
| <a id="enf-agent-lint"></a>The agent linter checks roster files and routing rows | `integrations/claude-code/agent-lint.py` | **soft** | It checks files, not a live spawn | none |
| <a id="enf-prose-lint"></a>The prose linter flags patterns in reader-facing text | `tools/prose-lint.py` | **soft** | A sentence can be clear to the linter and still wrong | none |
| <a id="enf-agnosticism-lint"></a>The agnosticism linter flags host addresses and home paths | `tools/agnosticism-lint.py` | **soft** | Project names and subtle fingerprints are left to a reviewer | none |
| <a id="enf-status-register"></a>The status register tool checks recorded statuses | `tools/status-register.py` | **soft** | It checks the register, not the work behind it | none |
| <a id="enf-growth-audit"></a>The growth audit lists collections a project has not written | `tools/growth-audit.py` | **detective** | It reports after the pass, and a report nobody reads changes nothing | none |
| <a id="enf-graft-audit"></a>The graft audit lists files that differ from the release | `tools/graft-audit.py` | **detective** | It reports differences; deciding each one stays with the owner | none |
| <a id="enf-tier-classification"></a>The task is classed T0 to T3 before work starts | `core/method/tiers.md` | **judgment** | No tool checks the class chosen | none |
| <a id="enf-protocol-order"></a>Work enters through a named step list in a set order | `protocols/` | **judgment** | No tool checks which step list a session entered | none |
| <a id="enf-spec-before-code"></a>A contract is written before the code it covers | `protocols/specify.md` | **judgment** | No tool checks the order of the two commits | none |
| <a id="enf-test-before-code"></a>A failing test is written before the code it authorizes | `protocols/test-first.md` | **judgment** | No tool watches the test fail first | none |
| <a id="enf-verify-gates"></a>Checks proportional to the change run before it is called done | `protocols/verify.md` | **judgment** | Which checks count as proportional is a call the session makes | none |
| <a id="enf-canonize"></a>Each task ends with one close-out that records what it taught | `protocols/canonize.md` | **judgment** | A close-out can record nothing and still pass | none |
| <a id="enf-attribution"></a>Each handback names the agent that produced it | `templates/prompts/handback-payload.md` | **detective** | A worker can name the wrong producer; the check reads the field only | none |
| <a id="enf-brief-block"></a>Each brief carries the canonical discipline block word for word | `templates/prompts/graph-session-bootstrap.md` | **soft** | The block reaches the worker; whether it follows it is the model's | none |
| <a id="enf-charter-duties"></a>Each agent charter lists what the role does and hands back | `agents/` | **judgment** | A worker may act outside its charter | none |
| <a id="enf-lifecycle-gate-rows"></a>Lifecycle protocols end in checklist rows a named judge signs | `protocols/grow.md` | **judgment** | A signature records a decision, not that the decision was right | none |
| <a id="enf-steward-only"></a>Harvest and graft start only when the owner asks | `protocols/harvest.md` | **judgment** | A session can start one unasked; nothing mechanical sees it | none |
| <a id="enf-seed-gate"></a>The test run of this repository before a release | `tests/run.sh` | **detective** | It covers this repository, never an installed project | none |
| <a id="enf-ratchets"></a>Numeric limits in the test run move only one way | `tests/ratchets.json`, `tools/ratchet-lint.py` | **soft** | Loosening a limit and its lock in one change is visible, not stopped | none |
