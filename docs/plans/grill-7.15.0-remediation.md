# grill — unified remediation and evidence doctrine (7.15.0)

**Status:** all 42 entries dispositioned in §1.3 — 22 closed with a pinning
regression, 13 fixed with none, 7 open. The open seven are all Track E: two
measurements deferred for want of a grown plant (U-36, U-41), one owner decision
(U-34), and four entries with no finding text anywhere in the tree (U-35, U-37,
U-39, and U-38 which keeps only its subject), recorded as gaps in §1.2 rather
than reconstructed.
**Baseline commit:** `d7588e2` (7.15.0)
**Phase 0 executed:** 2026-09-13
**Ledger origin:** four prior analyses (F = stabilization, G = integrity,
R = remediation, E = evidence-driven improvement), all observed at 7.13.1 /
`5f6b3b9`. Per doctrine P9 every entry is re-verified against HEAD below; a
finding that no longer reproduces is closed `superseded` with the
re-verification recorded, never silently dropped.

This file is the authoritative ledger. It is updated at the close of every
slice; a ledger unchanged after an implementation slice is a defect in
the slice.

---

## §0 Baseline record (Phase 0)

Environment: Linux 7.2.3-xanmod1, bash, `python3` present, `pytest` present.
Nothing was modified in Phase 0. Every number below carries the command
that produced it.

### §0.1 Gate composition and result

`bash tests/run.sh` → **EXIT=0 (green on arrival)**. 17 shell suites, then:

| Step | Command | Reads |
|---|---|---|
| prose-lint self-application | `tools/prose-lint.py --file README.md --file DOCUMENTATION.md` | 2 real files |
| graph-lint CLI regression | `python3 tests/test_graph_lint.py` | fixtures (62 tests) |
| agent-lint roster lint | `agent-lint.py --lint --dir agents` | real roster (19 agents) |
| agent-lint eval | `agent-lint.py --eval --dir agents` | real golden corpus |
| agent-lint CLI regression | `pytest tests/test_agent_lint.py` | fixtures (44 passed, 1 skipped) |
| seed-lint | `python3 tests/seed-lint.py` | real seed tree |
| legal-lint | `python3 tests/legal-lint.py` | real corpus (129 entries / 13 pages) |

The one pytest skip is `tests/test_agent_lint.py:770`, guarded on "fewer than
two golden-corpus copies present to compare". In the seed only one copy exists,
so this assertion can never execute here — a V6 concern (a check that cannot
fail in the tree it is run against), not the U-26 runner-absent skip.

### §0.2 Measured context surfaces

| Surface | Measured | Budget enforced against it |
|---|---|---|
| `core/AGENTS.md` kernel | **7 564 bytes** | `KERNEL_BUDGET = 8 000` (`seed-lint.py:35`) — 436 bytes headroom |
| machinery `est_tokens` sum | **126 903** across 59 nodes | **none** |
| largest single node | **12 037** (`protocols/graft.md`) | **none** |
| eager `description:` surface | **27 344 chars (~6 836 tokens)** across 48 nodes | **none** |
| — agents only | 9 373 chars (~2 343 tokens) | none |
| — skills only | 7 620 chars (~1 905 tokens) | none |
| body lines, median / mean | 171 / 203 | — |
| bodies > 500 lines | **3** (graft 932, grow 712, harvest 658) | none (machinery exempt) |
| bodies > 170 lines | **30 of 59** | 170-line ceiling **exempts machinery** (`graph-lint.py:731`) |
| placed file set (`install.sh all`) | **377 files+links, 2 905 315 bytes** | none |

`graph-lint.py:729` checks `est_tokens` for *honesty* (within 2× of measured)
and never for a *ceiling*. This is the precise shape of U-16: every surface the
seed measures, it declines to bound.

### §0.3 Routing baseline

`agent-lint.py --eval` prints: `top-1 accuracy 100.0% (55/55); novel-stack rows
checked: 3` and gates at `≥ 90%`.

Overlap of each golden row's task words against **its own target agent's**
`routing_triggers` + `description` + `name` vocabulary (stopwords removed):

| Overlap class | Rows |
|---|---|
| verbatim subset (100%) | **46** |
| high (≥80%) | 3 |
| partial (50–80%) | 5 |
| low (<50%) — genuinely independent | **1** |
| sentinel (`LOW`) rows | 3 |

Exactly one of 55 scored rows shares less than half its vocabulary with the
agent it is supposed to select. The reported 100% is therefore a
**consistency check**, not a measure of routing ability (doctrine P2 / X1).

**Held-out corpus** (n=20, authored in this session from the real-world
description of each task, without consulting any agent's `routing_triggers`;
tasks and labels recorded in §9 below):

| Metric | Result |
|---|---|
| top-1 correct **and** confident | **4 / 20** |
| abstained (LOW/NONE) | **15 / 20** |
| **confident-and-wrong** | **1 / 20** |

Two observations that change U-14's stated root cause:

1. The confident-wrong row is *not* a near-tie. `"our chain of language-model
   calls loops forever and burns money"` → **HIGH `security`, score 22 vs 4**
   (a 5.5× margin, far past `HIGH_RATIO = 1.5`). Widening the HIGH margin
   would not have prevented it.
2. The cause is token fragmentation of hyphenated triggers. `security` carries
   `"assess the supply-chain and secrets handling risk"`; the tokenizer
   (`[a-z0-9_]+`) splits `supply-chain` into `supply` + `chain`, so `chain`
   scores as a free-standing concept. Reduced counterexample:
   `--route "chain of calls"` → **HIGH `security`, score 18**.

Also recorded: `"we are storing passwords with md5"` → **NONE** (no route at
all), and `"someone can read another customer's invoice by changing the number
in the URL"` → LOW. Two security-critical tasks that the router does not reach,
which the prioritization rule weights above documentation misroutes.

### §0.4 Installer destination set

Every target-writing operation in `install.sh` (1 161 lines), classified.

**Canonical safe writes** — via `place_file` (backs up by `mv`, so the backup
takes the *link object*; skips byte-identical destinations; honours `LINK_MODE`):

`.claude/settings.json`, `.prime/agent/settings.json`, `opencode.json`,
`.github/copilot-instructions.md`, `EXPERT_SEED_INSTALL_PROMPT.md`,
`docs/graph/**` machinery (via `place_tree`), all harness roster/skill
projections (via `project_agents` / `project_skills`),
`docs/graph/{agent-lint,agnosticism-lint,prose-lint,status-register}.py`.

**Create-only writes** — intentional; plant owns the file after first install:

| Line | Destination | Note |
|---|---|---|
| 304 | `docs/graph/<templates/docs leaf>` | guarded `! -e && ! -L`; honours `.unfilled.md` marker |
| 391–394 | `docs/graph/{_schema.md,graph-lint.py,spec-lint.py,grill-lint.py}` | add-if-missing; reconciled by `graft-graph-engine.py` |
| 417 | `docs/graph/index.md` | add-if-missing, then `fill_plant_facts` |

These are copies even under `--symlink`, correctly — a plant-owned file must
not be a link into the seed. They belong in the M9 recorded exception list.

**Unsafe direct destination writes** — bypass `place_file` entirely: no
backup, no identical-check, follow destination symlinks, ignore `--symlink`:

| Line | Destination | Responsible function |
|---|---|---|
| 552 | `.claude/commands/<name>.md`, `.opencode/commands/…`, `.prime/agent/prompts/…` | `generate_slash_commands` (`cat >`) |
| 594 | `.claude/route-hook.py` | `install_claude_code` |
| 597 | `.claude/status-hook.py` | `install_claude_code` |
| 600 | `.claude/bound-hook.py` | `install_claude_code` |
| 605 | `.claude/agent-lint.py` | `install_claude_code` |
| 666 | `.codex/codex-config-snippet.toml` | `install_codex` (`sed > `) |
| 706 | `.github/agents/<name>.agent.md` | `install_github_copilot` (embedded Python `open(dst,"w")`) |
| 762 | `.github/prompts/<name>.prompt.md` | `install_github_copilot` (embedded Python) |
| 789 | `.github/instructions/<name>-skill.instructions.md` | `install_github_copilot` (embedded Python) |
| 816 | `.github/hooks/route-hook.py` | `install_github_copilot` |
| 818 | `.github/hooks/route.json` | `install_github_copilot` |
| 820 | `.github/hooks/status-hook.py` | `install_github_copilot` |
| 822 | `.github/hooks/status.json` | `install_github_copilot` |
| 865 | `.prime/agent/extensions/route-extension.ts` | `install_prime_agent` |
| 868 | `.prime/agent/extensions/status-extension.ts` | `install_prime_agent` |
| 877 | `.prime/agent/APPEND_SYSTEM.md` | `install_prime_agent` |
| 1119 | `.cypress/seed.json` | `write_seed_stamp` (`{…} > "$stamp"`) |

**17 destinations across 6 functions and 4 write idioms** (`cp`, `cat >`,
`sed >`, Python `open(…,"w")`). The prior count of "eleven bare `cp` sites"
understated the class: it counted only the `cp` idiom.

**Kernel writes** — `place_kernel`, its own path (lines 181, 188, 201, 207).
Symlink-safe (each `cp` is guarded `-f && ! -L`, or preceded by `rm -f`), but
see U-04 and U-07.

### §0.5 Audit surface (`tools/graft-audit.py`)

`audit_backups()` (line 304) enumerates `plant.rglob(f"*.bak-{date}-*")` only.
It can therefore observe **exactly what `place_file` and `place_kernel`
produce**, and nothing else. Every destination in the unsafe table above
produces no backup, so it is unobservable by construction.

`is_seed_owned_graph_path()` (line 216) returns False for anything not under
`docs/graph/`. `seed_source_for()` (line 178) maps:

- `CLAUDE.md`, `AGENTS.md`, `.github/copilot-instructions.md` → kernel
- `docs/graph/{protocols,method,agents,skills,templates}/…` and the scaffold tools
- `.claude/`, `.codex/`, `.opencode/`, `.prime/agent/` — **only** the
  `agents/` and `skills/` subpaths

It returns `None` (→ UNMAPPED) for: `.claude/*.py`, `.claude/settings.json`,
`.claude/commands/*`, `.github/hooks/*`, `.github/{agents,prompts,instructions}/*`,
`.prime/agent/extensions/*`, `.prime/agent/APPEND_SYSTEM.md`,
`.prime/agent/prompts/*`, `opencode.json`, `.codex/codex-config-snippet.toml`,
`EXPERT_SEED_INSTALL_PROMPT.md`, `.cypress/seed.json`.

`--help` is rejected as an unknown option (`exit 2`).

### §0.6 Persistent state map (`.cypress/seed.json`)

Written only by `write_seed_stamp`; read back by `stamp_field` (a `sed`
regex over scalar string fields) and by `tools/growth-audit.py`.

| Field | Owner | Meaning | Mutation rule | Preservation |
|---|---|---|---|---|
| `seed` | installer | constant `"cypress"` | rewritten each run | n/a |
| `version` | `manifest.json` | seed version now installed | overwritten from manifest | none needed |
| `installed_at` | installer | UTC timestamp of this run | overwritten | none needed |
| `installed_from` | installer | version the plant advanced off | set to previous `version` only when it differs | preserved on same-version re-run |
| `tools` | owner (accumulating) | space-joined adapter list | **union** of previous + this run, first-seen order | **preserved** ✔ |
| `legal_corpus` | **owner** | `yes` / `no` / `undecided` | this run's flag, else previous, else `undecided` | **preserved on silence** ✔ |
| `legal_jurisdiction` | **owner** | two-letter code or `undecided` | same rule | **preserved on silence** ✔ |
| `agent_projections` | **derived** | per-adapter spawnable path + `verbatim` | recomputed from `tools` via `agent_projection_for` | derived, never stored independently ✔ |

S1/S2/S5 are satisfied at HEAD (verified in §7, U-05). The remaining defects
are S3/S6 (declared state may contradict the filesystem — U-06) and the
write itself (line 1119: not atomic, follows a destination symlink; a
truncated stamp silently reads back as empty fields, which `stamp_field`
cannot distinguish from "never set", collapsing S1).

### §0.7 Gate map

| Check | Asserts | Reads | Auto | Can fail | Unreadable input | Candidate false-green class |
|---|---|---|---|---|---|---|
| 17 shell suites | install/graph/tier behaviour | fixtures + temp installs | via `run.sh` | yes | n/a | scope |
| `prose-lint.py` (gate) | AI-writing tells, fact preservation | **2 real files** (`README`, `DOCUMENTATION`) | yes | yes | **silent `continue`** (`:753`) | coverage (2 of ~340 md) |
| `test_graph_lint.py` | graph-lint CLI contract | fixtures | yes | yes | n/a | representation |
| `agent-lint --lint` | roster frontmatter, `can_delegate == (Task ∈ tools)` | **real roster** | yes | yes | n/a | — |
| `agent-lint --eval` | routing top-1 ≥ 90% | **real, in-sample corpus** | yes | yes | n/a | **self-reference** |
| `test_agent_lint.py` | agent-lint CLI contract | fixtures | yes (pytest present) | yes | n/a | coverage (1 assertion inert) |
| `seed-lint.py` | one-home-per-fact, kernel budget, anchors, node frontmatter | **real seed tree** | yes | yes | — | scope (no eager/body budget) |
| `legal-lint.py` | eight-field citability | **real corpus** | yes | yes | — | — |
| `test-spec-lint.sh` | spec shape | **fixtures only** | yes | yes | — | **scope** (seed compliance unproven) |
| `test-grill-lint.sh` | plan shape | **fixtures only** | yes | yes | — | **scope** |
| `test-graft-tools.sh` | graft audit behaviour | **fixtures only** | yes | yes | — | **scope** |
| `test-growth-audit.sh` | unknown-row disclosure | **fixtures only** | yes | yes | — | **scope** |
| `test-agnosticism-lint.sh` | agnosticism floor | **fixtures only** | yes | yes | — | **scope** |
| `test-status-register.sh` | status vocabulary | **fixtures only** | yes | yes | **silent `continue`** (`:328`) | **scope** |
| `spec-lint.py` on the seed | — | **never run on the seed** | no | — | **silent `continue`** (`:205`) | coverage |
| `route-hook.py` | progressive discovery | plant | per prompt | **no** (`|| true`) | — | informational by design |
| `status-hook.py` | status summary | plant | session start | **no** (`|| true`) | — | informational by design |
| `bound-hook.py` | bounded execution | plant | PreToolUse(Bash) | **yes** (blocking) | — | — |
| `Stop` hook (`produced_by`) | attribution | — | **not wired** | — | — | recorded ADR-0003 decision |
| **repository CI** | — | — | **absent** | — | — | **coverage** |

Six suites are *Enforced (fixtures only)*: they prove the linter works and say
nothing about whether the seed complies. This is doctrine P1 exactly.

### §0.8 Duplication inventory

**Frontmatter / scalar parsing — 5 full implementations + 4 partial:**

| Implementation | Location |
|---|---|
| `parse_frontmatter(text, path)` | `integrations/claude-code/agent-lint.py:165` |
| `parse_frontmatter(text, path)` | `templates/knowledge-graph/graph-lint.py:175` |
| `parse_frontmatter(path)` | `tests/seed-lint.py:147` (+ `frontmatter_block:132`) |
| `parse_frontmatter(text)` | `tools/status-register.py:199` |
| `parse_frontmatter(path)` | `tools/growth-audit.py:369` |
| `frontmatter_has_status(text)` | `tools/status-migrate.py:65` |
| inline regex parse ×3 | `install.sh` embedded Python (lines ~706, ~762, ~789) |
| `stamp_field` (JSON via `sed`) | `install.sh:1052` |

**Mirrored algorithms:** router tokenisation/matching exists in both
`agent-lint.py` (`_tokens`, `_match`, `confidence`) and
`graph-lint.py:738–747` (`_tokens`, `_match`). The `agent-lint.py` *file* is
installed to three locations, but from one source — a generated copy, which
is acceptable. The canonical-block byte-identity in the brief templates is
already lint-enforced (`CLAUDE.md`), so it is not an open synchronisation
comment. U-32's "maintainers instructed to keep algorithms in sync" is
therefore **narrower than stated**: the genuine duplication is the
frontmatter parsers (above) and the router scorer (two copies).

### §0.9 Corpus coverage

| Corpus | Files | Composition |
|---|---|---|
| `library-corpus` | 82 | nuget 22, maven 21, pypi 14, npm 10, container 7, language 5, platform 2 |
| `legal-corpus` | 16 | eu 8, national 3, case-law 1, international 1 |
| `tool-corpus` | 15 | — |
| `skill-corpus` | 12 | — |
| `agent-corpus` | 8 | — |

`nuget + maven = 43 of 82 (52%)` — the library corpus skews to the .NET/Java
estate. The national legal layer carries exactly one jurisdiction: `it`.

### §0.10 Repository CI

**Absent.** No `.github/workflows/`, no CI configuration of any kind. ~4 800
lines of tests and eighteen Python checks run only when someone remembers.

---

## §1 Re-verification table (doctrine P9)

Every entry re-verified against `d7588e2`. `reverified_class` uses the
doctrine's evidence vocabulary. The last column is the status **at
re-verification** and is deliberately not updated as slices land — §1.3 owns the
current disposition, so this table stays a dated record of what Phase 0 found
rather than becoming a second home for closure.

| ID | Prior class | Re-verified class | Command / evidence | Status at re-verification |
|---|---|---|---|---|
| U-01 | Verified | **Verified** | install → append sentinel to 6 files → reinstall: 5 of 6 sentinels destroyed, **0 backups**; `.claude/settings.json` (via `place_file`) correctly kept 1 backup | open |
| U-02 | Verified (class) | **Verified** | pre-created 6 destinations as symlinks to files outside the target; install overwrote **5 referents through the links**; `settings.json` intact | open |
| U-03 | Verified | **Verified** | 3 plant customisations destroyed → `graft-audit.py` reports *"zero backup files — nothing was overwritten"* and *"clean — no plant knowledge overwritten"* | open |
| U-04 | Verified | **Verified** | `--symlink` install: `CLAUDE.md` is a **copy** (K3 violated); 5 destinations are copies (M9); `place_kernel`'s own comment claims "a seed symlink under `--symlink`" | open |
| U-05 | Verified | **Superseded** | `claude-code --legal-corpus yes --legal-jurisdiction it` then `prime-agent --force`: `tools` = `"claude-code prime-agent"`, `legal_corpus` = `yes`, `legal_jurisdiction` = `it`, both projections derived. S1/S2/S5 hold | superseded |
| U-06 | Verified | **Verified** | `--legal-corpus no` over an installed corpus: records `"no"` while **16 pages remain on disk**, exit 0, silent. `-ge` also still present (`install.sh:356`) and its input set counts `.bak-*` | open |
| U-07 | Contradictory | **Verified** | `place_file:121` "`--force` skips the prompt, never the backup"; `place_kernel:200` skips the sibling backup when `$FORCE -eq 1`. `place_file`'s header comment also claims it "prompts otherwise" — it never prompts | open |
| U-08 | Verified | **Verified** | `install.sh:665` `sed "s|…|$PROJECT_DIR|g"` interpolates the path into a `sed` *replacement*; `&` and `\` are replacement metacharacters and `|` is the delimiter | open |
| U-09 | Verified | **Verified** | `install.sh:1000` `install_github_copilot >/dev/null 2>&1 || true`; `mktemp -d` at :984 with no `trap` | open |
| U-10 | Verified | **Verified** | `graft-audit.py --help` → `!! unknown option --help`, exit 2 | open |
| U-11 | **Tentative** | **Verified** | git repo at `outer/child`; `find_lint()` resolved to `outer/docs/graph/graph-lint.py` — crossed the `.git` boundary into an ancestor-controlled script | open |
| U-12 | Asserted | **Asserted** | not yet characterised; Phase 2 | open |
| U-13 | Verified | **Verified, narrowed** | 46 of 55 scored rows are a verbatim vocabulary subset of their own target; exactly 1 row <50%. Held-out: 4/20 confident-correct, 15/20 abstain, 1/20 confident-wrong. **README carries no accuracy claim** and `DOCUMENTATION.md:832` already discloses the in-sample weakness — the live defect is the *instrument* printing an unqualified number and gating ≥90% on that corpus | open |
| U-14 | Strong inference | **Verified, root cause corrected** | the confident-wrong row is a 5.5× margin, not a near-tie; cause is hyphenated-trigger token fragmentation (`supply-chain` → `chain`), reduced case `--route "chain of calls"` → HIGH `security` 18. Widening `HIGH_RATIO` would not fix it | open |
| U-15 | Contradictory | **Verified** | `README.md:258` claims `<500`-line bodies; graft 932 / grow 712 / harvest 658. `graph-lint.py:731` ceiling is 170 and **exempts machinery**, so it binds none of the three | open |
| U-16 | Verified | **Verified** | `est_tokens` honesty-checked within 2× (`graph-lint.py:729`), never bounded. Sum 126 903; largest 12 037; eager `description:` 27 344 chars. Only the kernel (7 564 / 8 000) is budgeted | open |
| U-17 | Verified | **Verified** | no cost model anywhere in the tree; nothing measures a T3 | open |
| U-18 | Contradictory | **Verified** | ADR-0003:38 "Detective (post-hoc)"; `deliver.md:191` "unwired"; Stop hook absent from `settings.json`; yet `README.md:221` "(fail-closed)" and `DOCUMENTATION.md:133,341` "fail-closed". Promotion criterion cannot be met in the seed → stays unwired; restate only | open |
| U-19 | Verified | **Verified** | `README.md:113` "the same `agent-lint.py` CI gate"; no CI exists | open |
| U-20 | Verified | **Verified** | nuget+maven = 52% of `library-corpus`; national legal layer = `it` only | open |
| U-21 | Contradictory | **Strong inference** | rationale/artifact split not yet traced line-by-line; deferred to Phase 6 | open |
| U-22 | Verified | **Verified** | inventory facts repeated across `README`, `DOCUMENTATION`, `manifest.json`, `documentation/*`; `seed-lint.py` cross-checks some numerics but not the full set | open |
| U-23 | Asserted | **Asserted** | front-door length not yet measured against a stated target; last slice | open |
| U-24 | Asserted | **Asserted** | no host capability matrix exists | open |
| U-25 | Verified | **Verified** | no `.github/workflows/`, no CI of any kind | open |
| U-26 | Verified | **Superseded (partly)** | `run.sh:47–56` probes both `python3 -m pytest` and `pytest`, and announces loudly on absence — no longer a *silent* skip. It still does not **fail**, so V1 is unmet. Re-scoped to "strict gate must fail when a required runner is absent" | open |
| U-27 | Verified | **Verified** | `prose-lint.py:753`, `status-register.py:328`, `spec-lint.py:205` — three bare `continue`s, no diagnostic, no exit effect | open |
| U-28 | Verified | **Superseded** | `run.sh:23–27` now records the exemption and its reasoning in prose (genre question for `documentation/*-reference.md`). Coverage is still 2 of ~340 md files — that part folds into U-27/U-30 | superseded |
| U-29 | Verified | **Verified** | no `specs/` directory in the seed | open |
| U-30 | Asserted | **Asserted** | no gate states its false-green class; §0.7 above is the first draft | open |
| U-31 | Strong inference | **Verified** | 5 `parse_frontmatter` implementations + 4 partial (§0.8) | open |
| U-32 | Strong inference | **Verified, narrowed** | genuine duplication is the router scorer (`agent-lint.py` + `graph-lint.py:738`) and the parsers; the "keep in sync" comments the ledger cited are mostly prose uses of "mirror"/"byte-identical", and the brief-template byte-identity is already lint-enforced | open |
| U-33 | Asserted | **Asserted** | no machine-readable gate registry; §0.7 is hand-built | open |
| U-34 | various | **Deferred, stated** (2026-09-15) | semantic adjudication behind the deterministic router; the statement is reconstructed in §1.2 from `docs/specs/SPEC-0002-routing-contract.md:192` and HANDOFF §3.2 | deferred |
| U-35 | various | **Statement lost** (2026-09-15) | §1.2 — no finding text survives anywhere in the tree | deferred |
| U-36 | various | **Deferred** | graph-routing metrics; `§7.4` records the measurement as not taken and names what it needs (HANDOFF:39) | deferred |
| U-37 | various | **Statement lost** (2026-09-15) | §1.2 — no finding text survives anywhere in the tree | deferred |
| U-38 | various | **Statement lost** (2026-09-15) | §1.2 — survives only as the second name in `§2` row 13, which slice 13 delivered without it | deferred |
| U-39 | various | **Statement lost** (2026-09-15) | §1.2 — no finding text survives anywhere in the tree | deferred |
| U-40 | various | **Verified, answered** | roster justification: does anything merge or retire? Answered by `tools/roster-justification.py` and [ADR-0008](../decisions/adr-0008-roster-justification-lives-in-the-node.md); the work it authorized is `docs/plans/unrouted-work.md` | deferred |
| U-41 | various | **Deferred** | institutional memory; `§7.5` records the design, why it was not run, and what would resolve it | deferred |
| U-42 | various | **Verified, measured** | metamorphic stability under five meaning-preserving rewrites — slice 9, with its own caveat that the corpus it was measured over flatters it | deferred |

Those nine rows replace one: `U-34…U-42`, a single line reading "not
re-verified / deferred". A range is not an enumeration. It looks like one, and it
defers and re-verifies members nobody can name — which is how five of the nine
came to be referenced for the length of a remediation without ever being stated.
The five cells dated 2026-09-15 are this expansion's own findings, not Phase 0's;
the rest of the table is untouched. §1.2 is what was behind the shorthand.

### §1.1 Dispositions changed by re-verification

- **U-05 → superseded.** The state reducer's behaviour now matches the target.
- **U-28 → superseded.** The exemption is recorded.
- **U-26 → re-scoped.** No longer silent; still non-failing.
- **U-13 → re-aimed.** The dishonest number lives in the *tool*, not the README.
- **U-14 → root cause replaced.** Margin widening is rejected as the fix; it
  would not have prevented the observed counterexample.
- **U-11 → promoted** from tentative to verified.
- **U-32 → narrowed** to two concrete duplications.
- **U-01/U-02 → widened** from 11 `cp` sites to 17 destinations across 4 idioms.

### §1.2 The five entries this ledger referenced and never stated

Five ids inside the old `U-34…U-42` range have no finding text anywhere in the
tree: no statement, no reopen condition, no owner. Established exhaustively —
`grep -rn 'U-3[45789]' --exclude-dir=.git .` returns, for the whole repository,
three lines about U-34, one line about U-38, and nothing at all for U-35, U-37
and U-39. They existed as endpoints of a range.

**Three of the five entries below are not recovered findings. They are recorded
gaps.** U-34 is reconstructed from evidence the tree still carries and is marked
as such; U-38 keeps its subject and nothing else; U-35, U-37 and U-39 have no
content to recover at all, and each entry's content *is* that the statement was
lost. Nothing here paraphrases a plausible finding into the place where the
original stood. The owner's decision
of 2026-09-15 was to write all five rather than strike the range, on the grounds
that a struck range leaves the same five ids cited in `§2` row 13, in SPEC-0002
and in `agent-lint.py` pointing at nothing.

**U-34 — does the router get a semantic adjudication layer?**
*Reconstructed from evidence, not recovered.* Three surfaces still name it:
`docs/specs/SPEC-0002-routing-contract.md:192` calls it "the deferred U-34
decision" in the paragraph explaining that telling `crop rotation` from `key
rotation` is meaning rather than spelling; SPEC-0002 §11's paraphrase-floor row
resolves by "Track E measurement (U-34)"; and the comment above
`ADVERSARIAL_CONFIDENT_WRONG_BUDGET` in `integrations/claude-code/agent-lint.py`
states the bar. It is the same question as HANDOFF §3.2 Decision D: an LLM
adjudication layer *behind* the deterministic router for ambiguous cases, never
overriding a confident deterministic route, always recording its reasoning.
**Adoption bar:** a measured improvement on held-out and adversarial data. The
two numbers it must move, as HANDOFF §3.2 records them, are confidently correct
4 of 17 on phrasings the router was never given, and confidently wrong 2 of 12
against deliberate baiting. **Status:** open, blocked on that measurement.
**Reopens:** it is already open; it closes only when the layer is measured
against both classes or the owner rejects it in writing. **Owner:** the owner,
as HANDOFF Decision D.

**U-38 — an adoption-related Track E item whose statement is lost.**
*Subject evidenced, content lost.* `§2` row 13 promised it to slice 13
alongside U-12, under the slice title "Non-pristine adoption". Slice 13's
record delivers U-12 — the D1 half-installed target and the D2 silent
restoration — and does not mention U-38 anywhere. So one fact is evidenced:
whatever U-38 asked for, it was scoped to adoption of the installer into a
repository that is not pristine, and it was *not* what slice 13 did. The rest
is unrecorded. **Status:** open, unstated. **Reopens:** if the Track E source
analysis is recovered, or if a non-pristine adoption defect is found that
slice 13's eight cases in `tests/test-install-adoption.sh` do not already
cover — either recovers the entry's subject. Struck at the next ledger review
if neither happens. **Owner:** whoever runs the next adoption slice.

**U-35, U-37, U-39 — statements that did not survive.** *Recorded gaps.* Each
of these was carried into this ledger from one of the four prior analyses
(F = stabilization, G = integrity, R = remediation, E = evidence-driven
improvement, all observed at 7.13.1 / `5f6b3b9`), and none of the four source
documents is in the tree. What is known is the id and the track: Track E, the
evidence-driven set, which is why `§2` row 17 gates them behind slice 12 and
U-17. What is not known is the finding, its class, its counterexample and its
owner. **That is the defect being recorded here**, and it is a defect in this
ledger rather than in the seed: doctrine P9 says a finding that no longer
reproduces is closed `superseded` with the re-verification recorded and never
silently dropped, and a finding that was never *written* is the same failure one
step earlier. A range in an index is not a record. **Status:** open, unstated,
three of them. **Reopens:** each reopens if the Track E source analysis is
recovered — F/G/R/E are named in the ledger origin at the head of this file and
may exist outside the repository — and each is **struck at the next ledger
review if it is not**, with the strike recorded here rather than by deleting the
row. **Owner:** the owner, since only the owner can say whether the source
analyses still exist.

A reader must not read U-35, U-37 or U-39 as restored text, or read U-38 as
anything more than its subject. They carry no finding. They carry the fact that a
finding was referenced, never stated, and is now unrecoverable from this
repository.

### §1.3 Disposition

`§1` re-verified every entry against `d7588e2`, and its Status column then read
`open` for U-01…U-33 through all eighteen slices. Closure lived only in the
eighteen slice records — the authoritative ledger stale, the second home
current, which is the inversion this file exists to prevent. `§1`'s column is
now scoped to the moment it describes and this is the disposition, derived from
those slice records.

Three statuses, and the distinction the first two draw is the whole point of the
table:

- **`closed · pinned`** — the fix is closed *and* a named gate step goes red if
  it is reverted. Reverting the fix breaks the build.
- **`fixed · unpinned`** — the defect is fixed and nothing in `tests/run.sh`
  notices if it comes back. Thirteen entries are in this state. They are not
  written as `closed`, because a fix nobody can regress is a fix with a
  half-life, and calling it closed is the same arithmetic-true,
  rhetorically-false move as `top-1 accuracy 100.0%`.
- **`superseded · pinned`** — §1's re-verification found the defect already gone
  (U-05, U-28), and a later slice added the regression that keeps it gone. Two
  entries, kept distinct from `closed` because nobody fixed them.

| ID | Status | Closed by | Pinning regression |
|---|---|---|---|
| U-01 | closed · pinned | slice 1 | `tests/test-install-placement.sh` M7, over a *discovered* destination set — reverting one `cp` names `.claude/route-hook.py` |
| U-02 | closed · pinned | slice 1 | same suite, M2 (written through a symlink to a file outside the target) |
| U-03 | closed · pinned | slices 1–3 | same suite, M8: zero UNMAPPED backups; `graft-audit.py` exits 1 on UNRESOLVED |
| U-04 | closed · pinned | slices 1–2 | `tests/test-install-kernel-modes.sh` K1–K6; `test-install-placement.sh` M9 for the hooks half |
| U-05 | superseded · pinned | slice 3 | `tests/test-plant-state.sh` S1–S6, including order independence — it was already correct at HEAD and nothing tested it |
| U-06 | closed · pinned | slice 3 | same suite: `yes → no` over a corpus on disk is refused, disk and record untouched |
| U-07 | **fixed · unpinned** | slice 2 | **none.** `--force` means one sentence shared by code, help text and `INSTALL.md`, and `place_kernel` no longer has its own backup branch to diverge — structural, not asserted. Nothing goes red if the branch returns |
| U-08 | closed · pinned | slice 1 | `tests/test-seed-budgets.sh` installs into `a b`, `a&b`, `a[b]`, `a#b` and `a'b` and asserts the literal path substitutes and the TOML parses; `seed-lint.py` `check_install_write_sites` additionally refuses a returning `sed >` in `install_codex` as an unrecorded write site |
| U-09 | **fixed · unpinned** | slice 1 | **none.** `--check` now separates a crashed generator from a stale view, and the run has one temp owner. Both verified by probe; neither asserted |
| U-10 | **fixed · unpinned** | slice 1 | **none.** `graft-audit.py --help` prints its docstring and exits 0. Verified by direct probe; reverting it leaves the full gate green |
| U-11 | **fixed · unpinned** | slice 1 | **none.** The `find_lint()` walk is bounded at the first `.git` or `.cypress/`. Verified both directions by probe; reverting it leaves the full gate green |
| U-12 | closed · pinned | slice 13 | `tests/test-install-adoption.sh` (8 cases); the D1 case asserts the target is still *empty* after the refusal, not merely that the install failed |
| U-13 | closed · pinned | slice 7 | `agent-lint.py --eval`'s own gates — per-class reporting, `PARAPHRASE_MAX_OVERLAP`, `PARAPHRASE_MIN_ROWS`, `CONFIDENT_WRONG_BUDGET` — plus the routing-contract regressions in `tests/test_agent_lint.py` |
| U-14 | closed · pinned | slice 7 | same, via `COMPOUND_FRAGMENT_IS_WEAK_EVIDENCE` in `tests/test_agent_lint.py`; `tests/test_router_reach.py` bounds the vocabulary the fix operates over |
| U-15 | closed · pinned | slice 6 | `seed-lint.py` `check_body_ceiling`; `tests/test-seed-budgets.sh` probes it against the largest node it governs, **discovered** rather than named |
| U-16 | closed · pinned | slice 6 | `seed-lint.py` `check_eager_surface` (`EAGER_BUDGET`, `EAGER_EXEMPTIONS` at zero slack); `tests/test-seed-budgets.sh` |
| U-17 | **fixed · unpinned** | slice 15 | **none, and none is possible.** A measurement is not a behaviour: one funnel/baseline pair, reported with its conditions. Nothing can go red if it is deleted |
| U-18 | **fixed · unpinned** | slice 8 | **none.** README and DOCUMENTATION now carry ADR-0003's detective/post-hoc vocabulary instead of "fail-closed". Prose, checked by no gate — `prose-lint` reads only two files |
| U-19 | **fixed · unpinned** | slice 8 | **none.** The README distinguishes what `install.sh` places from what an adopting project must wire. Prose |
| U-20 | **fixed · unpinned** | slice 17 | **none.** The agnosticism claim is scoped to the machinery. `tools/agnosticism-lint.py` is in the gate but `tests/test-agnosticism-lint.sh` reads fixtures only, so it proves the linter works and says nothing about this claim |
| U-21 | **fixed · unpinned** | slice 17 | **none.** Durable-orientation and version-pinned claims are separated in prose |
| U-22 | closed · pinned | slices 12, 17 | `seed-lint.py`'s manifest comparison, now both ways for `protocols`, `skills` and `templates` — proved by removing one entry. The `legal`-agent omission that slice 17 fixed was not a count and is not covered by it |
| U-23 | **fixed · unpinned** | slice 18 | **none.** The first `install.sh` line moved from README 111 to 38. Nothing asserts where it sits; the README cost table is reproducible from `check_eager_surface`, the *position* is not checked |
| U-24 | **fixed · unpinned** | slice 17 | **none.** `documentation/host-capability-matrix.md` is 12 capabilities × 5 adapters, derived from `install.sh` — but nothing re-derives it, so it drifts the moment an installer changes |
| U-25 | **fixed · unpinned** | slice 8 | **none.** `.github/workflows/gate.yml` runs the strict gate on `ubuntu-latest` and `macos-latest`. No gate step names it: `grep -rn workflows --include=*.py --include=*.sh .` returns nothing, so deleting the workflow leaves `bash tests/run.sh` green. The reviewer's list of unpinned entries did not carry this one, which is the shape of the problem: what would pin it is the thing that runs the gate |
| U-26 | closed · pinned | slice 5 | the gate itself: `run.sh` invokes `tests/test_agent_lint.py` with plain `python3` and the suite is stdlib `unittest`, so a re-introduced third-party import fails the step wherever that package is absent. No assertion names the import |
| U-27 | closed · pinned | slice 4 | `tests/test-lint-audibility.sh`, two cases per linter — and it asserts the *diagnostic names the path*, which is why it caught a revert that still exited 1 by an unrelated route |
| U-28 | superseded · pinned | Phase 0 | `run.sh:23–27` records the exemption in prose; the coverage half folded into U-27/U-30 and is pinned there |
| U-29 | closed · pinned | slice 10 | `seed-lint.py` `check_spec_test_mapping` and `check_spec_rows_name_their_contract` — each §10 row must name the test that asserts it; `tests/test-spec-lint.sh` pins the shape |
| U-30 | closed · pinned | slice 11 | `tools/gate-registry.py --lint`, wired as the gate's last step and failing in both directions — a step with no entry, and an entry for a step that no longer runs. `tests/test_gate_registry.py` |
| U-31 | closed · pinned | slice 14 | `tests/test_metadata_equivalence.py` (17 tests) drives all five implementations off one input table; `seed-lint.py` `check_frontmatter_reader_is_one_reader` |
| U-32 | closed · pinned | slice 14 | same suite; `test_router_tokenizers_have_diverged` now asserts convergence on the path `resolve()` actually uses, and reverting the cap in `graph-lint.py` goes red |
| U-33 | closed · pinned | slice 11 | `tools/gate-registry.py` is derived from `tests/run.sh` rather than maintained, and refuses a step nobody has classified |
| U-34 | open | — | deferred; §1.2 |
| U-35 | open (recorded gap) | — | §1.2 — no statement to close |
| U-36 | open | — | deferred; `§7.4` names what the measurement needs |
| U-37 | open (recorded gap) | — | §1.2 — no statement to close |
| U-38 | open (recorded gap) | — | §1.2 — no statement to close |
| U-39 | open (recorded gap) | — | §1.2 — no statement to close |
| U-40 | closed · pinned | unrouted-work slices 1–4 | `seed-lint.py` `check_prevents_are_distinct` and `tools/roster-justification.py`: the justification lives in the node's own `prevents:`, so it cannot go stale in a summary page ([ADR-0008](../decisions/adr-0008-roster-justification-lives-in-the-node.md)) |
| U-41 | open | — | deferred; `§7.5` names what the measurement needs |
| U-42 | **fixed · unpinned** | slice 9 | **none, and none is possible.** Same shape as U-17: one measurement, 236 transformed tasks, re-runnable against `--route` but asserted by nothing |

**Thirteen entries are `fixed · unpinned`** — U-07, U-09, U-10, U-11, U-17,
U-18, U-19, U-20, U-21, U-23, U-24, U-25 and U-42. Two of those (U-17, U-42) are
measurements, where no regression is possible and the status is descriptive
rather than a debt. The other eleven are behaviour and prose that a future edit
can silently undo, and this table is the only place that says so. A reviewer
confirmed the shape by reverting U-10 and U-11 in place: the full gate stayed
green over both.

Five of the eleven (U-18, U-19, U-20, U-21, U-23) are prose, and prose is
unpinnable here by construction rather than by omission: `prose-lint.py` runs
over two real files in the whole gate, and `§0.7` already classifies that as
`coverage`. Recording them as `fixed` is therefore not an accusation that
somebody skipped a test — it is the honest read of what a green gate covers.
U-24 and U-25 are the two worth a decision: a capability matrix nothing
re-derives, and a CI workflow nothing asserts.

---

## §2 Prioritized slice sequence

Ranked by expected reduction in meaningful failure × scope × recurrence ÷
cost, weighting destructive and security-consequential failure above
documentation failure.

| # | Slice | Tier | Entries | Depends on |
|---|---|---|---|---|
| **1** | **One canonical destination writer** | **T3** | U-01, U-02, U-04(hooks), M1/M2/M7/M9 | — |
| **2** | **Audit totality** | T2 | U-03 | 1 |
| **3** | **Legal state cannot contradict disk** | T3 | U-06, S3/S6 | — |
| 4 | `--force` has one meaning | T2 | U-07, M4 | 1 |
| 5 | Kernel copy/symlink contract | T3 | U-04(kernel), K1–K5 | 1 |
| 6 | Literal Codex path + generated-write safety | T2 | U-08, M5/M6 | 1 |
| 7 | Small installer/tool contracts | T1–T2 | U-09, U-10, U-11 | — |
| 8 | Gate audibility | T2 | U-27, V5 | — |
| 9 | Strict gate cannot skip | T2 | U-26, V1/V2 | — |
| 10 | CI on two platforms | T2 | U-25, V7 | 8, 9 |
| 11 | Budgets and body ceiling | T3 | U-15, U-16, X4/X5 | — |
| 12 | Honest routing metrics | T3 | U-13, U-14, X1/X2/X6 | — |
| 13 | Non-pristine adoption | T3 | U-12, U-38 | 1–6 |
| 14 | Restatement + host matrix | T2 | U-18…U-24 | 11, 12 |
| 15 | Consolidation | T3 | U-31, U-32, U-33 | 8 |
| 16 | Self-specs | T3 | U-29 | 1–6, 12 |
| 17 | Track E (evidence-gated) | T3 | U-34…U-42 | 12, U-17 |

Two rows above are preserved as planned rather than as delivered, and §1.3 is
the record of what actually happened. Row 13 names U-38 beside U-12; slice 13
delivered U-12 and nothing else, because U-38 had no statement to deliver
(§1.2). Row 17's `U-34…U-42` is the range shorthand that let that happen — §1
now enumerates those nine.

Slice 1 is first because it is the only entry whose failure mode is
**silent destruction of data outside the target directory**, it is the
common root of U-01/U-02/U-04(hooks)/M9, and Slice 2 cannot be verified
until the writer produces backups for the audit to classify.

Slice 3 is pulled ahead of the remaining Track A work because it is the
one open entry that makes the seed **record a falsehood** about itself.

## §3 First slice definition

**Slice:** One canonical destination writer.
**Tier:** T3 (spec-bearing: it establishes M1, M2, M5, M6, M7, M9).
**Objective:** every byte `install.sh` places into a target passes through a
single writer that owns destination inspection, identical-content detection,
backup policy, link-object replacement, temporary generation, and diagnostics.

**Counterexample that justifies it:** install; append a comment to
`.claude/route-hook.py`; reinstall. The edit is gone, no `.bak` exists, and
`graft-audit.py` reports *"clean — no plant knowledge overwritten, no
customization buried."* Separately: symlink that destination at a file
outside the target and the install overwrites the outside file.

**Existing structure and the contradiction:** `place_file` already implements
the correct policy and is used for ~15 destinations. 17 further destinations
reach the filesystem through `cp`, `cat >`, `sed >` and Python
`open(…,"w")`. The installer therefore has two placement paths, and the
safety properties documented for the first are claimed for both.

**Target structure:** `place_file` keeps its signature for copy placement;
generated content is written to a temporary file and handed to the same
writer (`place_generated SRC_BYTES DEST` / `place_file` with a temp source),
so generation completes before replacement. Per doctrine P4 the second path
is **removed**, not guarded.

**Invariants established:** M1, M2, M5, M6, M7, M9 (with the create-only
scaffold destinations recorded as the M9 exception list).
**Preserved:** M3 (measured: 377 files, 0 backups on clean reinstall — must
stay 0), K6 (kernel 7 564 bytes, budget unchanged), `tests/run.sh` exit 0.

**Characterizing test (Phase 2, must be red first):** the symlink-destination
attack and recoverability/audit-totality families over the **complete**
destination set from §0.4 — not the four `cp` sites.

**Expected ledger delta:** U-01, U-02 closed with regressions; U-04 partially
closed (hooks); U-03 unblocked.

---

## §4 Open questions for the owner

1. **U-06 disposition.** A recorded `yes → no` transition currently records a
   falsehood. Doctrine forbids silent deletion and offers two paths: reject
   the transition until an explicitly named removal operation is invoked, or
   build that operation now. Recommendation: **reject with a named remedy**
   in this slice, and defer the removal command until asked — it is the
   smaller change and keeps destruction user-sovereign.
2. **U-26 resolution.** Fail the strict gate when `pytest` is absent, or port
   `tests/test_agent_lint.py` to stdlib `unittest`. Recommendation: **port**
   — `tests/test_graph_lint.py` is already stdlib `unittest` for exactly this
   reason, so porting removes the dependency question permanently and makes
   the gate uniform rather than adding an environment requirement.
3. **U-15 satisfaction.** Enforce a machinery body ceiling that graft (932
   lines) exceeds, or narrow the README claim, or split along declared
   `owns:` facts. Splitting `graft.md` is the largest change and touches the
   placed file set; recommendation is **bound + restate** first.

---

## §4.1 Session handoff

`grill-7.15.0-remediation/HANDOFF.md` — written so a cold pickup, or a context
compaction, loses nothing that mattered: current state and how to re-derive it,
the three findings worth carrying in your head, what each review round cost, the
open decisions and their exact state, the U-40 evidence, and the traps that look
like defects and are not.

`grill-7.15.0-remediation/RESUME-PROMPT.md` — the handoff turned into an
instruction rather than a report: the objective, the hard constraints, the
invariants and how each is checked, the five defect classes with their standing
instruction, the review→fix→review phases, the anti-patterns, and the stop
conditions. Paste it as the opening message of a new session and the loop
resumes where it stopped. It restates no fact the handoff owns; it points, and
names the command that derives each number.

## §5 Slice records

Each slice is a file under `grill-7.15.0-remediation/`. This section is
the ledger: what was done, in what order, and where the record of it lives.
No line counts: a number whose only job is to let a reader gauge cost,
and which nothing checks, drifts — this one was wrong for 21 of 22 rows
within a day of being written.
It was one 800-line block until it became the largest thing in a document
that is already read whole — the same failure the slices below were fixing
in `protocols/graft.md`, arriving in the plan that describes the work.

| # | Slice | Record |
|---|---|---|
| 1 | One canonical destination writer | `grill-7.15.0-remediation/slice-01-one-canonical-destination-writer.md` |
| 2 | Kernel placement joins the canonical writer | `grill-7.15.0-remediation/slice-02-kernel-placement-joins-the-canonical-writer.md` |
| 3 | The plant's record cannot contradict its disk | `grill-7.15.0-remediation/slice-03-the-plant-s-record-cannot-contradict-its-disk.md` |
| 4 | Gate audibility (U-27) | `grill-7.15.0-remediation/slice-04-gate-audibility-u-27.md` |
| 5 | A required suite can no longer be absent from a green gate (U-26) | `grill-7.15.0-remediation/slice-05-a-required-suite-can-no-longer-be-absent-from-a-.md` |
| 6 | Every measured surface is bounded (U-15, U-16) | `grill-7.15.0-remediation/slice-06-every-measured-surface-is-bounded-u-15-u-16.md` |
| 7 | The routing metric measures routing (U-13, U-14) | `grill-7.15.0-remediation/slice-07-the-routing-metric-measures-routing-u-13-u-14.md` |
| 8 | The seed runs its own gate (U-25, U-19, U-18) | `grill-7.15.0-remediation/slice-08-the-seed-runs-its-own-gate-u-25-u-19-u-18.md` |
| 9 | Metamorphic stability measured (U-42) | `grill-7.15.0-remediation/slice-09-metamorphic-stability-measured-u-42.md` |
| 10 | The seed specs its own two writing surfaces (U-29) | `grill-7.15.0-remediation/slice-10-the-seed-specs-its-own-two-writing-surfaces-u-29.md` |
| 11 | Every gate declares what it can still miss (U-30, U-33) | `grill-7.15.0-remediation/slice-11-every-gate-declares-what-it-can-still-miss-u-30-.md` |
| 12 | Inventory drift closed at the mechanism (U-22, partial) | `grill-7.15.0-remediation/slice-12-inventory-drift-closed-at-the-mechanism-u-22-par.md` |
| 13 | An install into a real repository (U-12) | `grill-7.15.0-remediation/slice-13-an-install-into-a-real-repository-u-12.md` |
| 14 | Five parsers, one input table (U-31, U-32) | `grill-7.15.0-remediation/slice-14-five-parsers-one-input-table-u-31-u-32.md` |
| 15 | What a T3 costs, measured (U-17) | `grill-7.15.0-remediation/slice-15-what-a-t3-costs-measured-u-17.md` |
| 16 | The preflight's own second home (found while reviewing slice 13) | `grill-7.15.0-remediation/slice-16-the-preflight-s-own-second-home-found-while-revi.md` |
| 17 | What the seed says about itself (U-20, U-21, U-22, U-24) | `grill-7.15.0-remediation/slice-17-what-the-seed-says-about-itself-u-20-u-21-u-22-u.md` |
| 18 | The front door (U-23) | `grill-7.15.0-remediation/slice-18-the-front-door-u-23.md` |

## §6 Review rounds

Four rounds of independent adversarial review, each re-checking the
previous round's fixes and hunting further. Findings per round: 9, 6, 6, 1.
Each round's record is a file; this is the ledger of them.

| Round | What it found | Record |
|---|---|---|
| 1 | what three independent reviewers found | `grill-7.15.0-remediation/review-round-1.md` |
| 2 | verifying the fixes, and what verifying them found | `grill-7.15.0-remediation/review-round-2.md` |
| 3 | and where the loop converged | `grill-7.15.0-remediation/review-round-3.md` |
| 4 | the last structural hole | `grill-7.15.0-remediation/review-round-4.md` |

---

## §7 Final registers

### §7.1 The state model

How a plant's persistent record is produced, in one line:

> **previous stamp + this run's explicit flags + what the run actually placed
> → canonical state → one atomic write.**

Each term does work, and each was a defect before it was a term:

- **previous stamp** — read before the run writes anything, and handed to a JSON
  parser rather than a regex, because a stamp whose single truncated field made
  one value read empty used to reset a recorded decision silently.
- **explicit flags** — only a flag the owner passed changes a decision. Silence
  inherits. Only `undecided` is overwritten by silence.
- **what the run actually placed** — the corpus decision drives placement, not
  merely the record, so a plant that says it carries the corpus gets the corpus
  restored rather than a record that disagrees with its disk.
- **canonical state** — adapters accumulate as a union; `agent_projections` is
  derived from that union and never stored independently; an out-of-domain
  value is repaired to `undecided` and announced rather than propagated.
- **one atomic write** — staged, copied to a sibling of the destination, renamed
  onto it. `rename(2)` replaces the destination *name*, so a stamp symlinked
  outside the target is replaced rather than written through.

### §7.2 The mutation model

> **host-adapter intent → content (a seed file, or generated into one per-run
> staging directory) → one of four named placement operations → the target.**

`place_file` (seed file with a plant twin; backup; honours `--symlink`),
`place_generated` (per-target content; no seed original to link to),
`place_if_missing` (plant-owned after first placement), `place_state` (the
installer's own derived stamp; atomic, no backup, and the single recorded
exception to recoverability). Beneath all four, `ensure_dir` makes a blocked
destination this tool's error at any depth. Above them, a preflight refuses
before the first byte.

One honest exception remains: `place_kernel` still creates the *sibling* kernel
link with `mv`/`rm`/`ln -s` of its own. It is symlink-safe and backed up, and
`place_file` cannot express it (the link is project-local and relative, not a
link to the seed), but "every byte goes through one of four operations" is
false as stated and this is where.

### §7.3 Routing report

Derived 2026-09-15 by `python3 integrations/claude-code/agent-lint.py --eval
--dir agents`, which is the only home for these numbers; the table below is a
transcription of what it printed and goes stale the moment a row or a trigger
moves. Four classes, 96 rows, never averaged — they measure different things.

| Corpus class | n | confident-correct | abstained | confident-wrong | mean overlap |
|---|---|---|---|---|---|
| contract | 61 | 60 | 1 | **0** | 0.96 |
| paraphrase (held out) | 18 | 4 | 14 | **0** | 0.13 |
| **adversarial** (bait phrasings) | 12 | 4 | 5 | **3** | 0.33 |
| unknown-domain | 5 | 5 | 0 | **0** | 0.00 |

**The adversarial class was missing from this table, and it is the class that
carries the failures.** Every confident-wrong route the seed can currently
demonstrate is in it — three of them, printed by name on every gate run:
a threat model for an onboarding screen taken by `ui-ux-designer` at HIGH,
undocumented delegation caps taken by `multi-agent-architect` at HIGH, and a
pentest report's citations taken by `legal` at MEDIUM. Publishing three classes
that all read **0** while a fourth reads **3** is the same shape as the `top-1
accuracy 100.0%` this remediation was convened over: every number true, the
register false.

**Provenance.** The paraphrase rows were authored 2026-09-13 from the real-world
description of each task, before the router was changed, without reading any
agent's `routing_triggers`. One row was later found to be a contract row with
three words appended and was relabelled; the floor moved **down** as a result.
Two independent re-audits, each with a from-scratch overlap measure, found no
further contamination.

**Gated on:** `CONFIDENT_WRONG_BUDGET = 0` outside the adversarial class, and
`ADVERSARIAL_CONFIDENT_WRONG_BUDGET = 3` within it — a *budget*, currently at
zero slack, not a zero. Contract consistency ≥ `EVAL_THRESHOLD = 0.95`, measured
at 98.4% (60/61), and a consistency check rather than accuracy. Paraphrase floor
`PARAPHRASE_FLOOR = 4`, a ratchet. Held-out rows must stay held out:
`PARAPHRASE_MAX_OVERLAP = 0.50` measured **both ways**, no duplicate tasks, no
LOW-expecting row wearing another class, `PARAPHRASE_MIN_ROWS = 15` and
`ADVERSARIAL_MIN_ROWS = 12`. Every one of those limits ratchets; the live values
are `python3 tools/ratchet-lint.py --show`, which is their one home.

**The adversarial budget is 3 because it was raised back to 3**, on the owner's
decision of 2026-09-15, and the reasoning is recorded at the constant in
`integrations/claude-code/agent-lint.py` rather than restated here. In short: the
fall to 2 had been bought by a defect. `down` was the only directional particle
missing from `STOPWORDS`, and a trigger added in the same release made it df=1
vocabulary owned by `docs-librarian`, donating half the score that carried one
adversarial row to its expected target while routing an outage report to the
documentation agent at HIGH. Closing the stopword gap kills the misroute and
returns the class to 3. A 2×2 ablation separated the two changes. This is a
**loosening**, which is why it is the owner's signature and not an edit: the
router is not better than 3, and a limit saying otherwise was a limit bought
with a live misroute.

**Metamorphic stability:** 236 transformed contract tasks across five
meaning-preserving rewrites, zero became confidently wrong (§ slice 9, with its
caveat that stability on a high-overlap corpus is the expected result). Measured
over the 55-row contract corpus of that slice, not the 61 rows above.

**Calibration is NOT measured.** HIGH means "clears FLOOR and leads by 1.5×",
which is a property of the scores and not an observed correctness rate. The
kernel tells briefs to cite the band as evidence, so this gap matters; it is
recorded in SPEC-0002 §11 rather than closed.

### §7.4 Graph report — not measured

Required-node recall, irrelevant load, closure size, paraphrase stability and
wide-descent frequency for the **knowledge** router (`graph-lint.py --plan`) are
**not measured**. Nothing here should be read as covering them.

This paragraph used to add that `graph-lint.py` never received the
compound-fragment fix, "so the knowledge router installed into every plant still
scores `chain` from `supply-chain` at full strength". That was false when it was
written. `resolve()` scores through `_split_terms`/`_strength`, which carry the
fix; the old `_tokens` survives only behind `Node.routable_terms`, which nothing
calls — and `test_router_tokenizers_have_diverged` compared that dead pair
against agent-lint's live one, so it asserted a divergence the router did not
have and could never fail. The test now asserts convergence on the path
`resolve()` uses, and reverting the cap in `graph-lint.py` goes red; before, the
whole 41-gate suite stayed green over it.

Measuring it needs a grown plant with a real graph, which the seed is not.
**Resolves when:** a plant with a populated `docs/graph/` can be scored against
a held-out node-retrieval corpus — U-36, Track E.

### §7.5 Institutional memory — not measured

"Knowledge compounds" is the seed's central longitudinal claim and it is
**untested**. The design (U-41) is: Session A canonizes a fact; Session B, cold
context and different phrasing, must have it routed in; compare rediscovery
time, tool calls and correctness against a baseline that never canonized it.

It was not run. It needs two full sessions against a grown plant and a baseline
arm, which is a larger measurement than anything else in this remediation, and
the seed alone cannot produce it. **Resolves when:** a plant with real session
history exists and both arms can be run. Until then the claim stands on the
architecture's plausibility and not on evidence, and the README should not be
read as saying otherwise.

