<!-- The owner decisions D1 to D4 of `docs/plans/grill-8.4.0-opencode-2.md`; its §12 row 1 points here. Kept beside the plan, outside its increment directory, which holds only §9 increments. -->

# Owner decisions D1 to D4: what the opencode round left to the owner

The round that made opencode a first-class host on OpenCode 2 (ADR-0033) left four things to the owner. The owner decided D1 and D2 on 2026-11-10 and set D4 aside; the notes keep the evidence and options as written. Each note gives the finding, the evidence and how it is classed (measured in this round, or read from documentation and not run), the options with their costs, and what would be verified. Nothing here is implemented, no default changed, and no option is adopted by being written down. Further parity differences that need no owner decision are recorded in the host matrix as defects to close: the worker-continuation guard (O7) and the kernel in a compose-mode plant.

## D1. The always-loaded budget and the lead's charter (O8)

- **Finding.** The Claude Code main session plays the orchestrator: its charter and the always-loaded nodes it names ride in an output style, and `EAGER_EXEMPTIONS` records that surface as an owner decision of 2026-11-09. The same text delivered to an opencode main session raises opencode's always-loaded surface past `EAGER_BUDGET`.
- **Evidence.** Measured with `tests/seed-lint.py`'s own functions on this tree: `EAGER_BUDGET` is 41,600 bytes; opencode's surface is 24,207 bytes (kernel, agent descriptions, skill descriptions); the orchestrator's composition is 42,924 bytes; their sum is 67,131 bytes, the figure Claude Code's exemption already records. The orchestrator is installed as a selectable primary agent, `orchestrator`, whose text loads only when a user selects it, so it adds nothing to the surface of a session that does not.
- **Options.** (a) An `EAGER_EXEMPTIONS` entry for opencode at 67,131 bytes, delivered through the plugin to the main session (the host's own coding instructions stay, the user can still switch agent, the kernel loads once). Cost: every opencode session pays 42,924 bytes more, and the ratchet gains a second exemption. (b) A smaller charter for the lead: the charter body without its always-loaded nodes, which the lead reads through the router when it needs them. Cost: the lead and the Claude Code orchestrator then differ. (c) No orchestrator charter on opencode beyond the selectable agent: the user selects it, and the kernel's routing plus the route hook carry the rest. Cost: a parity defect stays open.
- **To verify.** Measure the lead's token use on a task with and without the charter on the same model, and read whether the route hook's text already steers the lead as the charter does.

**Decided.** The owner decided on 2026-11-10 on option (a): an `EAGER_EXEMPTIONS` entry for opencode at 67,131 bytes (SPEC-0001 `OPENCODE_LEAD_PLAYS_THE_ORCHESTRATOR`). Combined with D2 the charter reaches the main session as the default agent's own instructions, so no plugin delivery is added.

## D2. The default agent (O8)

- **Finding.** The only way to make the orchestrator the lead without a plugin is to name it the default agent, which changes the agent every new session starts in.
- **Evidence.** Measured on OpenCode 2.2.6: an agent file with a non-empty body replaces the host's base prompt for that agent, so a default `orchestrator` would run without the host's own coding instructions; a primary agent file with `mode: primary` is selectable from the session without being the default. Documented, not run: the host's `default_agent` setting.
- **Options.** (a) Keep the host's default and ship the orchestrator as a selectable agent (today). (b) Set the orchestrator as the default agent: parity of the lead, at the price of the base prompt and a changed starting point for every user. (c) Set it as the default and compose the host's base prompt text into the charter. Cost: the seed would carry host prompt text it does not own.
- **To verify.** Run a coding task as the default `orchestrator` and as `build`, and compare the tool calls and the result.

**Decided.** The owner decided on 2026-11-10 on option (b): the orchestrator is the default agent (`default_agent` in `opencode.json`). Measured after the decision on OpenCode 2.2.6: the key is accepted with no configuration warning and a new session started in `orchestrator`. The host's base coding prompt does not apply to that agent; `build` keeps it.

## D3. An install step for the plugin

- **Finding.** Not needed. The plugin imports only the host's bundled `@opencode/plugin` and `node:` built-ins, and loaded with no install and no network on OpenCode 2.2.6 (measured). This note records that the decision did not arise.
- **To verify.** The live procedure repeats the load check on each later release (`docs/skills/opencode-live-verification.md`, check 1).

## D4. Prime Agent's missing pre-tool guard (set aside)

- **Finding.** The host matrix records the pre-tool guard as `unsupported` on Prime Agent, a first-class host, while Claude Code and opencode now hold it. The tier rule makes the difference a defect to close.
- **Evidence.** Read in `documentation/host-capability-matrix.md` and `install_prime_agent`, which places the two context cores and their envelopes and no guard. Not investigated here: whether Prime Agent exposes a tool-call hook that can refuse.
- **Options.** (a) Investigate Prime Agent's extension API for a tool-call hook and, if one exists, add a third envelope over `bound-hook.py`. (b) Record it as the host's gap, which the tier rule does not allow without the owner's decision. (c) Leave it open and visible in the matrix.
- **To verify.** Read the host's extension events for one that fires before a tool runs and can return a refusal.

**Set aside.** The owner said on 2026-11-10 to ignore Prime Agent in this round. Nothing here changes it; the matrix keeps the difference as a recorded defect.
