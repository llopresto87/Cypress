## 7.35.0 — positive voice: rules say what to do, plants name their models once (2026-09-30)

The owner asked for a seed-wide re-reading of every prompt, to turn "don't do
this" into "do it this way, because", to clear accumulated cruft, and to fix
whatever had gone stale on the way. This release is that pass, plus the tools
that four of the owner's rulings needed.

### What a plant gets

- **Rules in positive voice.** Every protocol, skill, agent charter, method
  node and template, and the agent- and skill-corpus pages, state the
  behavior they want and the reason for it. A bounded role says what it ONLY
  does. A prohibition stays only on a hard boundary (an irreversible act, a
  security, privacy or legal line, a user-sovereign trigger, loop control)
  and names the right move beside it.
  The rule's home is `method.engineering-posture` §8. Meaning is unchanged
  except where a statement was false against the code; the main corrections
  are listed under "Corrected facts" below.
- **A model map.** A plant names its models once, in `docs/graph/models.md`:
  the providers, and the model each host runs for each class and effort.
  Nodes, protocols and briefs name only the class (authoring or
  investigation) and the effort. On Prime Agent the overlay reads the map,
  resolves the selector with `rlm.find_models`, and spawns with
  `rlm.spawn(..., model=..., thinking=<effort>)`; a selector that does not
  resolve stops the spawn, and an unfilled row inherits the parent's model
  and says so in the routing evidence. On opencode, `install.sh opencode`
  writes each agent's `model:` line from the map, and
  `install.sh opencode --check` reports drift. Claude Code reads the class
  alias itself, so the map has no Claude Code column. The Prime Agent
  overlay's version table and its "nearest higher model" fallback are gone.
  `agent-lint.py --lint` rule 6 holds an agent's `model:` to the four aliases
  Claude Code reads: `opus`, `sonnet`, `haiku` and `inherit`
  ([ADR-0022](docs/decisions/adr-0022-the-plant-model-map.md), which
  supersedes ADR-0019 in part).
- **One companion block in every brief.** The spawn id, the routing evidence
  and the handback requirement now travel as a second canonical block,
  `COMPANION`, beside GRAPH DISCIPLINE in
  `templates/prompts/graph-session-bootstrap.md`. Seed-lint holds every copy
  of both blocks byte-identical.
- **Known bugs.** A bug a test uncovered is marked for a fix and the owner is
  told. The test that found it stays unchanged as the bug's only acceptance
  check; the implementer fixes the bug and the same test is re-run, and until
  then the red is declared in the delivery (`test-first.known-bug`).
- **Retractions.** A recorded claim found false is struck through, with a
  dated Correction beside it. `skill.holistic-editing` is the one home of
  that rule, and graft uses it for a plant fact it corrects.
- **The humanizer scope.** The humanizer pass applies to prose a person reads
  (documentation, extensive comments, handoffs and briefs for people,
  ADR and spec bodies). Graph nodes and session records get none, because
  the graph is written for models; `prose-lint.py` stays the floor.
- **Corrected facts**, among others: the orchestrator's cold-repo route goes
  through `protocol.initialize`; `agent-corpus/legal.md` is a pointer to the
  base-roster `agents/14-legal.md`, and its referrers name the agent; SSH
  hardening allows root login by public key and refuses it by password
  (`PermitRootLogin prohibit-password`); the
  `deploy-fleet-on-remote-docker-host` skill-corpus page uses
  `StrictHostKeyChecking=accept-new` with a committed `known_hosts`; the
  skill-corpus release page defines its "release branch".

### What was removed

- The closing prohibition lists ("What you do not do", "Anti-patterns",
  "Common ways to fail", "Forbidden moves", "What stays out of scope"), after
  each rule they carried moved into the section that owns it. The fact key
  `holistic-editing.forbidden-moves` stays; its section is now "Integration
  moves". `skill-corpus/discardme.md` is unchanged this round, and the
  `Anti-patterns` catalogs of `templates/knowledge-graph/_schema.md` and
  `multi-agent-architect` stay, because they are catalogs, not closing
  lists.
- The `KNOWN_BUG_<id>` assertion marker in `protocol.verify-disagreement` and
  every copy of it.
- History narration in doctrine ("until 7.x", "added in", "was split"). A
  sentence that carried a rule's reason now states the reason in the present
  tense; the history stays here, in the changelog.

### The owner's rulings

The round asked the owner ten questions. The answers: the reference pages
keep their walkthroughs and stay current (D1); lint holds the brief
companion aligned (D2); the humanizer's `LICENSE.upstream` names the
doctrine's holder (D3); SSH host keys and root login as above (D4, D5); the
skill-corpus "unsecured lane" is defined as a release branch (D6); known bugs
as above (D7); retractions as above (D8); one model policy for Prime Agent,
Claude Code and opencode, where Prime Agent and opencode may run any
provider (D9); and `templates/knowledge-graph/_schema.md` keeps its
frontmatter house style with two named exceptions (D10).
`agent-corpus/legal.md` stays in place, as a pointer, because no named
go-ahead to delete it was given.

### New checks

- `check_seed_only_stays_home`: `docs/skills/seed-release.md` and
  `tools/prepare-release.py` are never named by `manifest.json` or
  `install.sh`, and the manifest's `tools` map equals what `install.sh`
  places.
- `check_decision_index`: `docs/decisions/index.md` lists every ADR file, and
  every link resolves.
- `check_reference_tables` compares each protocol's `load_when` strings in the
  protocols reference with its frontmatter, and `check_published_counts`
  checks "N protocols" as it checks agents and skills.
- `agent-lint.py --lint` rule 6, above.
- `tools/prepare-release.py` refuses a CHANGELOG entry holding a `## `
  heading that is not a version heading, because the entry would end there.
- `graft-audit.py --unfilled` and `growth-audit.py` report an unfilled model
  map as a disclosed line, not a failure.

### Decisions and specs

- [ADR-0021](docs/decisions/adr-0021-seed-only-procedures-stay-home.md): a
  procedure that runs only on the seed's own tree lives under `docs/skills/`,
  and seed-lint proves it never reaches a plant. Its first procedure is
  `docs/skills/seed-release.md`, the end-of-round release: one documentation
  pass, the gate, the staged notes, the commit, the steward plant's canonize,
  and the tag push on the owner's go-ahead. `CLAUDE.md`'s Release section is
  now a pointer to it.
- [ADR-0022](docs/decisions/adr-0022-the-plant-model-map.md): the model map,
  above. Both ADRs are `proposed`.
- SPEC-0001 gains the model-map contracts: the template is placed once and
  then left to the plant, the opencode projection takes its `model:` line from
  the map or drops it, an unreadable map fails closed, `--check` detects
  opencode drift, and the seed-only files are never placed.
- SPEC-0003's brief-template contract covers the COMPANION block.
- SPEC-0005 (version 0.15) adds `AGENT_DECLARES_MODEL_CLASS`.
- The round's plan of record is `docs/plans/grill-7.35.0-positive-voice.md`.

### How plants pick this up

- **A new plant** gets everything from `install.sh` and the install prompt.
  The model map arrives as a template; growth asks the owner to fill it with
  the other plant facts.
- **An existing plant** gets it by `graft`. The machinery fast-forwards, and
  the model map is placed because it is missing. Until the owner fills it,
  graft reports it as a disclosed line, not a blocker, and every agent runs
  on its caller's model. On opencode, re-run `install.sh opencode` after
  filling the map. A plant agent whose `model:` holds a full model id fails
  rule 6 after the graft; the id belongs in the map, and `haiku` or
  `inherit` keep passing.
- **Skill-corpus copies stay the plant's.** A plant that instantiated
  `deploy-fleet-on-remote-docker-host` or `harden-docker-host` from the skill
  corpus keeps its own copy, and graft does not refresh it. Compare its SSH
  line and its `PermitRootLogin` setting with the corpus page and bring them
  in line.
- **Routing text moved in a few places**, as stale-fact fixes: the
  `verify-disagreement` description and one of its `load_when` lines, the
  `grow` description (its scouts and authors are now named by class,
  investigation and authoring), and the `spec-author` description, which
  now cites `rule.spec`. In several agent, protocol and skill descriptions,
  an all-caps word is now in plain case. A plant that keeps its own route
  golden set may see rows move after the graft.
- **Existing `KNOWN_BUG_<id>` assertions** in a plant's suites are the
  plant's own tests, and graft leaves them in place. When one of those bugs is
  next worked on, follow `test-first.known-bug`.
