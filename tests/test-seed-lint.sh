#!/usr/bin/env bash
# test-seed-lint.sh: each kept seed-lint check fires on a planted violation.
# One copy of what seed-lint reads is made once. Each row plants one edit into
# it, runs one check_* in process, and restores the files it touched. A row
# passes when its needle is in a finding the unplanted copy does not print;
# an "absent" row passes when no new finding holds the needle. The real-tree
# `python3 tests/seed-lint.py` step in tests/run.sh is every row's partner.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
. "$ROOT/tests/helpers/lintcase.sh"

mini_tree "$TMP" agent-corpus agents core docs documentation integrations \
  legal-corpus library-corpus protocols skill-corpus skills templates tests \
  tool-corpus tools .github CHANGELOG.md CLAUDE.md DOCUMENTATION.md \
  GRAFT_PROMPT.md INSTALL.md INSTALL_PROMPT.md README.md install.sh manifest.json

python3 - "$TMP" <<'PY'
import importlib.util, json, re, shutil, sys
from pathlib import Path

T = Path(sys.argv[1])
FIX = T / "tests/fixtures/front-door"
touched: dict = {}                     # rel -> original bytes, or None if new


def keep(rel):
    if rel not in touched:
        touched[rel] = (T / rel).read_bytes() if (T / rel).exists() else None


def put(rel, text):
    keep(rel)
    (T / rel).parent.mkdir(parents=True, exist_ok=True)
    (T / rel).write_text(text, encoding="utf-8")


def read(rel):
    return (T / rel).read_text(encoding="utf-8")


def sub(rel, old, new, pattern=False):
    text = read(rel)
    out, n = re.subn(old, new, text, count=1, flags=re.M | re.S) if pattern else \
        (text.replace(old, new, 1), text.count(old))
    assert n, f"plant did not apply: {old!r} not in {rel}"
    put(rel, out)


def append(rel, text):
    put(rel, read(rel) + "\n" + text + "\n")


def drop(rel):
    keep(rel)
    (T / rel).unlink()


def owns(rel, key, add):
    item = f"  - {key}\n"
    sub(rel, "owns:\n", "owns:\n" + item) if add else sub(rel, item, "")


def fixture():
    for src, dst in (("README.md", "README.md"), ("INSTALL.md", "INSTALL.md"),
                     ("glossary.md", "DOCUMENTATION.md")):
        put(dst, (FIX / src).read_text(encoding="utf-8"))


def restore():
    for rel, raw in touched.items():
        if raw is None:
            (T / rel).unlink(missing_ok=True)
        else:
            (T / rel).write_bytes(raw)
    touched.clear()


def module():
    spec = importlib.util.spec_from_file_location("seedlint_case", T / "tests/seed-lint.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def lint(check):
    mod = module()
    try:
        getattr(mod, check)()
    except Exception as e:                       # a crash is a finding, never a pass
        mod.findings.append(f"RAISED {type(e).__name__}: {e}")
    return mod.findings


def surfaces():
    mod = module()
    return mod.eager_surfaces(mod.KERNEL.stat().st_size)


def kernel_sentence():
    t = read("core/AGENTS.md")
    s = re.search(r"Harness\s+memory\s+is\s+not\s+a\s+home:.*?\(`method\.stewardship-posture`\)\.", t, re.S)
    assert s, "plant did not apply: §3.2 holds no session-record sentence"
    put("core/AGENTS.md", t[:s.start()] + t[s.end():])


def unbind_a_row():
    for _spec, slug, test, rel in module()._spec_green_rows():
        if rel.endswith(".py") and re.search(rf"def {test}\b", read(rel)) and slug in read(rel):
            return put(rel, read(rel).replace(slug, "SLUG_REMOVED"))
    raise AssertionError("plant did not apply: no green row binds a Python test")


def oc(cfg):
    put("integrations/opencode/opencode.json", json.dumps(cfg))


def pad(rel, n):
    append(rel, "\n".join(f"padding line {i}" for i in range(n)))


def manifest_tools(add=None, drop=None):
    m = json.loads(read("manifest.json"))
    assert drop is None or drop in m["tools"], f"plant did not apply: {drop} not in manifest.json tools"
    if add:
        m["tools"][add] = "x"
    if drop:
        del m["tools"][drop]
    put("manifest.json", json.dumps(m, indent=2) + "\n")


PLACE_ANCHOR = '    place_file "$SEED_ROOT/tools/code-anchor.py" "$g/code-anchor.py"\n'


# label, check, plant, needle, absent. Labels bound by a spec §10 row keep
# their X/E id (R1); a row folded into another keeps its label beside it.
OC = {"$schema": "https://opencode.ai/config.json", "subagent_depth": 3}
AGN = "leaked host 198.18.7.42 and advisory CVE-2031-99999"
HOME = "Ran it from /home/exampleuser/work."
ROWS = [
    # check(): the inline checks
    ("sovereign-command", "check", lambda: sub("protocols/graft.md", r"^(est_tokens:[^\n]*\n)", r"\1command: true\n", True), "must not declare 'command: true'"),
    ("command-on-skill", "check", lambda: sub("skills/context-router/SKILL.md", r"^(est_tokens:[^\n]*\n)", r"\1command: true\n", True), "protocol-only field"),
    ("dangling-edge", "check", lambda: sub("protocols/verify.md", r"^requires:[ \t]*$", "requires:\n  - protocol.does-not-exist", True), "unknown machinery node"),
    ("requires-cycle", "check", lambda: (sub("protocols/specify.md", r"^requires:[ \t]*$", "requires:\n  - protocol.grill", True),
                                         sub("protocols/grill.md", r"^requires:[ \t]*$", "requires:\n  - protocol.specify", True)), "requires cycle"),
    ("spawn-trace", "check", lambda: put("templates/prompts/investigation-brief.md", read("templates/prompts/investigation-brief.md").replace("spawn_id", "spawnid")), "no spawn_id field"),
    ("version-drift", "check", lambda: sub("manifest.json", r'("version":\s*")\d+\.\d+\.\d+', r"\g<1>0.0.0", True), "version drift"),
    ("kernel-budget", "check", lambda: append("core/AGENTS.md", "<!-- " + "x" * 9000 + " -->"), "-byte budget"),
    ("est-tokens-2x", "check", lambda: sub("protocols/verify.md", r"^est_tokens:\s*\d+", "est_tokens: 20", True), "graph-lint.py would reject this node"),
    ("brief-drift", "check", lambda: sub("templates/prompts/investigation-brief.md", "GRAPH DISCIPLINE", "GRAPH DISCIPLINEX"), "has drifted from the canonical copy"),
    ("dangling-corpus-ref", "check", lambda: append("protocols/harvest.md", "See `legal-corpus/eu/does-not-exist.md`."), "dangling corpus/template reference"),
    ("agn-library-ip", "check", lambda: append("library-corpus/nuget/Npgsql.md", AGN), "leaked host-IP literal"),
    ("agn-legal-cve", "check", lambda: append("legal-corpus/eu/gdpr.md", AGN), "pinned advisory"),
    ("agn-tool-corpus", "check", lambda: append("tool-corpus/testing/http-smoke-suite.md", AGN), "tool-corpus/testing/http-smoke-suite.md"),
    ("agn-agent-corpus", "check", lambda: append("agent-corpus/env-contract-manager.md", AGN), "agent-corpus/env-contract-manager.md"),
    ("agn-skill-corpus", "check", lambda: append("skill-corpus/harden-docker-host.md", AGN), "skill-corpus/harden-docker-host.md"),
    # SPEC-0001 AGNOSTICISM_GATE_SCANS_DOCS_PLANS_TOOLS_INSTALLER AGNOSTICISM_GATE_SCANS_PY_AND_SH
    ("agn-docs-plans", "check", lambda: put("docs/plans/zz-agn.md", HOME), "absolute operator home path"),
    ("agn-install-sh", "check", lambda: append("install.sh", "# " + HOME), "install.sh"),
    ("agn-documentation", "check", lambda: append("DOCUMENTATION.md", HOME), "DOCUMENTATION.md"),
    ("agn-tools-sh", "check", lambda: put("tools/zz-agn.sh", "OUT=/home/exampleuser/out\n"), "tools/zz-agn.sh"),
    # SPEC-0001 HOST_TIERS_AGREE
    ("E4 HOST_TIERS_AGREE all-vs-arrays", "check_host_tiers", lambda: sub("install.sh", "SUPPORTED_TOOLS=(opencode)", "SUPPORTED_TOOLS=()"), "`all` expands to"),
    ("E4 HOST_TIERS_AGREE untiered", "check_host_tiers", lambda: sub("install.sh", "FROZEN_TOOLS=(codex github-copilot)", "FROZEN_TOOLS=(github-copilot)"), "untiered ['codex']"),
    ("single-writer-bypass", "check_install_write_sites", lambda: sub("install.sh", "place_tree() {", 'sneak() {\n    cp "$SEED_ROOT/README.md" "$PROJECT_DIR/SNEAK.md"\n}\nplace_tree() {'), "named placement operations"),
    # SPEC-0001 SEED_ONLY_FILES_NEVER_PLACED (adr-0021). exercises: check_seed_only_stays_home
    ("X393 SEED_ONLY_FILES_NEVER_PLACED manifest names prepare-release", "check_seed_only_stays_home", lambda: manifest_tools(add="tools/prepare-release.py"), ("tools/prepare-release.py", "a seed-only file")),
    ("X394 SEED_ONLY_FILES_NEVER_PLACED installer places a seed doc", "check_seed_only_stays_home", lambda: sub("install.sh", PLACE_ANCHOR,
        PLACE_ANCHOR + '    place_file "$SEED_ROOT/docs/decisions/index.md" "$PROJECT_DIR/docs/graph/decisions-index.md"\n'), "sources a file under $SEED_ROOT/docs"),
    ("X395 SEED_ONLY_FILES_NEVER_PLACED manifest drops a placed tool", "check_seed_only_stays_home", lambda: manifest_tools(drop="tools/code-anchor.py"), "manifest.json"),
    # SPEC-0003 BRIEF_TEMPLATES_BYTE_IDENTICAL, the COMPANION block. exercises: check
    ("X396 BRIEF_TEMPLATES_BYTE_IDENTICAL COMPANION block drift", "check", lambda: sub("templates/prompts/investigation-brief.md",
        r"(COMPANION \(echo each item back in your handback\):\n- Trace )this( spawn\.)", r"\1that\2", True), ("investigation-brief.md", "COMPANION")),
    # the reference's quoted load_when strings follow the frontmatter (D2, seed-release.dedupe-rule). exercises: check_reference_tables
    ("reference-load-when-drift", "check_reference_tables", lambda: sub("documentation/protocols-reference.md",
        r'"record a\s+missing or skipped gate"', '"record a skipped gate"', True), ("load_when", "protocol.verify")),
    ("reference-load-when-rewrapped", "check_reference_tables", lambda: sub("documentation/protocols-reference.md",
        r'"record a\s+missing or skipped gate"', '"record a missing or\n  skipped gate"', True), "load_when", True),
    ("reference-load-when-reordered", "check_reference_tables", lambda: sub("documentation/protocols-reference.md",
        r'"increment done, ready to merge or deploy"; "which gates to\s+run, verification runbook"',
        '"which gates to run, verification runbook"; "increment done, ready to merge or deploy"', True), ("protocol.verify", "other order")),
    # SPEC-0003 HOOK_TEXT_RESTATES_NO_KERNEL_RULE
    ("X201 HOOK_TEXT_RESTATES_NO_KERNEL_RULE text grows", "check_hook_text_restates_no_kernel_rule", lambda: sub(
        "integrations/claude-code/route-hook.py", 'NEW_PREFIX = "', 'NEW_PREFIX = "' + "T2 is a contained change. " * 40), "over HOOK_TEXT_MAX_BYTES"),
    # SPEC-0005: rule homes, leaves, text rules
    ("X347 ADOPTED_RULE_HOMES key owned twice", "check_adopted_rule_homes", lambda: owns("protocols/test-first.md", "test-first.no-lint-only-tests", True), "owned by more than one node"),
    ("X348 ADOPTED_RULE_HOMES key missing", "check_adopted_rule_homes", lambda: owns("skills/test-first/SKILL.md", "test-first.no-lint-only-tests", False), "not owned by skills/test-first/SKILL.md"),
    ("X343 DELEGATION_SPLIT_INTO_SIBLINGS key in the wrong sibling (row of X347)", "check_adopted_rule_homes", lambda: (
        owns("core/method/delegation-briefs.md", "delegation.briefs", False),
        owns("core/method/delegation-sequencing.md", "delegation.briefs", True)), "delegation.briefs: not owned by core/method/delegation-briefs.md"),
    ("X346 DELEGATION_SPLIT_INTO_SIBLINGS registration home", "check_adopted_rule_homes", lambda: owns("core/method/delegation-bounds.md", "delegation.harness-registration", False), "not owned by core/method/delegation-bounds.md"),
    ("X336 LEAF_BODY_CEILING_HELD new oversized leaf", "check_leaf_body_ceiling", lambda: (put("core/method/ce-planted-leaf.md", read("core/method/tiers.md")), pad("core/method/ce-planted-leaf.md", 200)), "core/method/ce-planted-leaf.md: body is"),
    ("X341 SIBLING_OVER_CEILING (row of X336)", "check_leaf_body_ceiling", lambda: pad("protocols/specify.md", 200), "protocols/specify.md: body is"),
    ("body-ceiling", "check_body_ceiling", lambda: (sub("protocols/verify.md", r"^est_tokens:\s*\d+", "est_tokens: 9000", True), pad("protocols/verify.md", 1200)), "machinery ceiling"),
    ("frontmatter-ceiling", "check_body_ceiling", lambda: sub("protocols/canonize.md", r"\A(---\n)", "\\1" + "".join(f"pad_{n}: x\n" for n in range(200)), True), "frontmatter is"),
    ("registration-referrer", "check_text_rules", lambda: put("protocols/grow.md", read("protocols/grow.md").replace("delegation.harness-registration", "x")), "REGISTRATION_POINTER: protocols/grow.md"),
    ("X349 STALE_POINTER", "check_text_rules", lambda: append("protocols/grow.md", "Brief rules: `docs/graph/method/delegation.md` (`delegation.briefs`)."), "delegation.briefs; point at core/method/delegation-briefs.md"),
    ("X350 HANDBACK_CARRIES_EFFORT_AND_EXPERTISE_GAP effort", "check_text_rules", lambda: sub("templates/prompts/handback-payload.md", r"^- effort:[^\n]*\n", "", True), "has 0 lines matching '^- effort:'"),
    ("X351 HANDBACK_CARRIES_EFFORT_AND_EXPERTISE_GAP expertise_gap", "check_text_rules", lambda: sub("templates/prompts/handback-payload.md", r"^- expertise_gap:[^\n]*\n", "", True), "has 0 lines matching '^- expertise_gap:'"),
    ("X352 BOOTSTRAP_STEP2_LOADS_A_MENU reworded", "check_text_rules", lambda: sub("templates/prompts/graph-session-bootstrap.md", "2. Load ONLY the reported nodes", "2. Load every reported node"), "BOOTSTRAP_STEP2_LOADS_A_MENU"),
    ("X352 BOOTSTRAP_STEP2_LOADS_A_MENU case changed", "check_text_rules", lambda: sub("templates/prompts/graph-session-bootstrap.md", "2. Load ONLY the reported nodes", "2. Load only the reported nodes"), "BOOTSTRAP_STEP2_LOADS_A_MENU"),
    ("X353 BOOTSTRAP_STEP2_LOADS_A_MENU re-wrapped passes", "check_text_rules", lambda: sub("templates/prompts/graph-session-bootstrap.md", r"(2\. Load ONLY the reported nodes plus their `requires:` closure\.)\n\s+", r"\1 ", True), "BOOTSTRAP_STEP2_LOADS_A_MENU", True),
    ("X354 ADOPTED_RULES_NOT_PENDING phrase", "check_text_rules", lambda: append("core/method/tiers.md", "This planted rule is pending the owner's confirmation."), "ADOPTED_RULES_NOT_PENDING: core/method/tiers.md"),
    ("X355 ADOPTED_RULES_NOT_PENDING wrapped phrase", "check_text_rules", lambda: append("protocols/grow.md", "This planted rule is Recommended rather\n  than REQUIRED here."), "ADOPTED_RULES_NOT_PENDING: protocols/grow.md"),
    ("X381 KERNEL_POINTS_AT_THE_SESSION_RECORD KERNEL_POINTER_TRIMMED", "check_text_rules", kernel_sentence, "core/AGENTS.md §3.2"),
    ("hook-reach", "check_text_rules", lambda: append("core/method/delegation.md", "Hooks do not reach subagents."), "HOOK_REACH: core/method/delegation.md"),
    ("hook-reach-true-claims", "check_text_rules", lambda: append("core/method/delegation.md",
        "The route hook does not reach a subagent's turn.\nPrompt-injecting hooks do not reach a subagent's turn.\nThe hook does not reach its timeout."), "HOOK_REACH:", True),
    ("knowledge-path-shipped", "check_text_rules", lambda: append("protocols/grow.md", "Write it to `docs/" + "specs/x.md`."), "KNOWLEDGE_PATHS: protocols/grow.md"),
    ("knowledge-path-self", "check_text_rules", lambda: append("CHANGELOG.md", "Moved to docs/" + "tools/x.md."), "KNOWLEDGE_PATHS: CHANGELOG.md"),
    # budgets, config, workflows, readers, run.sh
    ("eager-budget", "check_eager_surface", lambda: sub("agents/01-architect.md", r"^(description:[^\n]*)$", r"\1" + " padding" * 6000, True), "eager surface ["),
    ("opencode-stale-schema", "check_opencode_config", lambda: oc({**OC, "$schema": "https://opencode.ai/config-schema.json"}), "schema must be"),
    ("opencode-invalid-key", "check_opencode_config", lambda: oc({**OC, "agents": {}}), "additionalProperties:false"),
    ("opencode-double-load", "check_opencode_config", lambda: oc({**OC, "instructions": ["AGENTS.md"]}), "kernel would load twice"),
    ("opencode-depth-cap", "check_opencode_config", lambda: oc({**OC, "subagent_depth": 1}), "delegation topology would be capped"),
    ("ci-workflow", "check_workflows", lambda: drop(".github/workflows/gate.yml"), "gate.yml is missing"),
    ("release-workflow", "check_workflows", lambda: sub(".github/workflows/release.yml", "gh release create", "gh release view"), "does not hold `gh release create`"),
    ("reader-drift", "check_frontmatter_reader_is_one_reader", lambda: append("tools/frontmatter.py", "# drifted"), "has drifted from"),
    ("frontmatter-inner-colon", "check_frontmatter_is_portable_yaml", lambda: sub("core/method/prose-posture.md", r"^(title: [^\"'\n][^\n]*)$", r"\1: always", True), "strict-YAML skill loader"),
    ("grant-undeclared", "check_agent_spawn_grants", lambda: sub("agents/02-implementer.md", r"^(tools: \[[^\]\n]*)\]", r"\1, Agent]", True), "agents/02-implementer.md: can_delegate=false"),
    ("tools-omitted", "check_agent_spawn_grants", lambda: sub("agents/02-implementer.md", r"^tools: \[[^\n]*\]\n", "", True), "omits its tools: line"),
    ("run-sh-pipefail", "check_run_sh_shell_contract", lambda: sub("tests/run.sh", "set -euo pipefail\n", "set -eu\n"), "lacks `pipefail`"),
    ("run-sh-nounset", "check_run_sh_shell_contract", lambda: sub("tests/run.sh", "set -euo pipefail\n", "set -eo pipefail\n"), "lacks `-u`"),
    ("run-sh-set-moved", "check_run_sh_shell_contract", lambda: (sub("tests/run.sh", "set -euo pipefail\n", ""),
        sub("tests/run.sh", r"^(add_step [^\n]*\n)", r"\1set -euo pipefail\n", True)), "lacks `-e`"),
    # spec §10 bindings
    ("spec-cites-missing-test", "check_spec_test_mapping", lambda: append("docs/specs/SPEC-0001-install-placement.md",
        "| C | test_this_name_was_never_written | tests/x.py | integration | green |"), "does not exist in tests/"),
    ("spec-row-unbound", "check_spec_rows_name_their_contract", unbind_a_row, "does not name their contract"),
    # reference tables and gate tables
    ("reference-stale-tokens", "check_reference_tables", lambda: sub("documentation/protocols-reference.md", r"^(\| graft \|[^\n]*\| )(\d+)( \|)$", r"\g<1>9790\g<3>", True), "est_tokens 9790, but protocol.graft declares"),
    ("reference-invented-fact", "check_reference_tables", lambda: sub("documentation/protocols-reference.md", "`graft.reversibility` |", "`graft.reversibility`, `graft.invented` |"), "extra ['graft.invented']"),
    ("reference-duplicate-field", "check_reference_tables", lambda: sub("documentation/protocols-reference.md", r"^(- \*\*load_when:\*\*[^\n]*\n)", r"\1\1", True), "is stated 2 times"),
    # docs/decisions/index.md lists every ADR file, and no row points at a missing one. exercises: check_decision_index
    ("decision-index-unlisted", "check_decision_index", lambda: put("docs/decisions/adr-0099-planted.md", read("docs/decisions/adr-0001-mechanical-agent-router.md")), "adr-0099"),
    ("decision-index-dangling", "check_decision_index", lambda: sub("docs/decisions/index.md", r"(^\| \[\d{4}\]\(adr-[^\n]*\n)(?!\| \[\d{4}\])",
        r"\1| [0098](adr-0098-gone.md) | A planted row with no file | accepted | 2026-09-30 | planted | planted |\n", True), "adr-0098"),
    ("gate-dangling-reference", "check_gate_single_home", lambda: append("protocols/grow.md", "See `grow.gate.invented-here` for details."), "which no table row declares"),
    ("plant-root-boundary", "check_canonical_plant_root_boundary", lambda: sub("integrations/claude-code/status-hook.py", r"# --- canonical plant-root boundary ---.*?# --- end canonical plant-root boundary ---\n", "", True), "plant-root boundary"),
    # published figures (SPEC-0004 scope rows X318, X319, X332)
    ("skills-count", "check_published_figures", lambda: append("README.md", "The seed ships 99 skills."), "claims 99 skills"),
    ("protocol-count", "check_published_figures", lambda: append("README.md", "The seed ships 99 protocols."), "claims 99 protocols"),
    ("protocol-count-under", "check_published_figures", lambda: append("README.md", "The seed ships 3 protocols."), "claims 3 protocols"),
    ("agent-count", "check_published_figures", lambda: append("DOCUMENTATION.md", "A team of 99 named specialist agents."), "99 named specialist agents"),
    ("version-pin", "check_published_figures", lambda: sub("documentation/README.md", r"\(version \d+\.\d+\.\d+\)", "(version 0.0.1)", True), "documents version 0.0.1"),
    ("eager-misattributed", "check_published_figures", lambda: append("README.md", f"Claude Code pays {surfaces()['prime-agent']} bytes per session."), "bytes for claude-code"),
    ("X318 EAGER_FIGURES_CHECKED_WHEREVER_PUBLISHED FIGURE_MOVED_WITHOUT_ITS_CHECK reference", "check_published_figures", lambda: append("documentation/agents-reference.md", "The always-loaded surface is 99 111 bytes per session."), "EAGER_FIGURES_CHECKED_WHEREVER_PUBLISHED: documentation/agents-reference.md:"),
    ("X318 EAGER_FIGURES_CHECKED_WHEREVER_PUBLISHED INSTALL.md", "check_published_figures", lambda: append("INSTALL.md", "The always-loaded surface is 99 111 bytes per session."), "EAGER_FIGURES_CHECKED_WHEREVER_PUBLISHED: INSTALL.md:"),
    ("X319 BODY_FIGURES_HAVE_A_REQUIRED_HOME median dropped", "check_published_figures", lambda: sub("DOCUMENTATION.md", r" and the median is [0-9]+ lines", "", True), "matching the median routable body"),
    ("X319 BODY_FIGURES_HAVE_A_REQUIRED_HOME largest moved", "check_published_figures", lambda: pad("protocols/graft.md", 80), "matching the largest routable body"),
    ("X319 BODY_FIGURES_HAVE_A_REQUIRED_HOME figure elsewhere", "check_published_figures", lambda: append("INSTALL.md", "The largest body is 1 384 lines."), "BODY_FIGURES_HAVE_A_REQUIRED_HOME: INSTALL.md:"),
    ("X319 BODY_FIGURES_HAVE_A_REQUIRED_HOME empty claim", "check_published_figures", lambda: (sub("tests/seed-lint.py", "EAGER_EXEMPTIONS: dict[str, tuple[int, str]] = {\n", 'EAGER_EXEMPTIONS: dict[str, tuple[int, str]] = {\n    "codex": (99_999, "planted"),\n'),
        append("INSTALL.md", "EAGER_EXEMPTIONS is consequently **empty**.")), "consequently empty"),
    ("X332 BODY_FIGURES_HAVE_A_REQUIRED_HOME project node 151", "check_published_figures", lambda: append("documentation/skills-and-templates-reference.md", "The project-node body ceiling is ~151 lines."), "'151 lines' outside"),
    ("X332 BODY_FIGURES_HAVE_A_REQUIRED_HOME project node 150 passes", "check_published_figures", lambda: append("documentation/skills-and-templates-reference.md", "The project-node body ceiling is ~150 lines."), "'150 lines' outside", True),
    ("X332 BODY_FIGURES_HAVE_A_REQUIRED_HOME literal gone", "check_published_figures", lambda: put("templates/knowledge-graph/graph-lint.py", re.sub(r"(?<![\w.])150(?![\w.])", "149", read("templates/knowledge-graph/graph-lint.py"))), "holds no 150 literal"),
    # SPEC-0004 front door, on the fixture (X303, X320, X306, X312)
    ("X303 INSTALL_SECTION_NAMES_TARGET_PATHS target missing", "front_door_checks", lambda: (fixture(), sub("README.md", " `.cypress/seed.json` (", " (")), "does not name the target `.cypress/seed.json`"),
    ("X303 INSTALL_SECTION_NAMES_TARGET_PATHS not an install path", "front_door_checks", lambda: (fixture(), sub("README.md", "under `docs/graph/`.", "under `docs/graph/` and `.cursor/rules/`.")), "`.cursor/rules/` does not occur in install.sh"),
    ("X303 INSTALL_SECTION_NAMES_TARGET_PATHS seed-source path", "front_door_checks", lambda: (fixture(), sub("README.md", "under `docs/graph/`.", "under `docs/graph/` and `core/method/`.")), "`core/method/` is a seed-source path"),
    ("X303 INSTALL_SECTION_NAMES_TARGET_PATHS backup unlinked", "front_door_checks", lambda: (fixture(), sub("README.md", " ([backup before replace](DOCUMENTATION.md#enf-backup-before-replace))", "")), "links `DOCUMENTATION.md#enf-backup-before-replace`"),
    ("X320 FRONT_DOOR_ANCHORS_RESOLVE ANCHOR_DRIFT", "front_door_checks", lambda: (fixture(), sub("README.md", "#term-plant)", "#term-plnat)")), "#term-plnat names 0 explicit anchors"),
    ("X320 FRONT_DOOR_ANCHORS_RESOLVE link to no file", "front_door_checks", lambda: (fixture(), sub("README.md", "(INSTALL.md)", "(docs/no-such.md)")), "`docs/no-such.md` does not resolve"),
    ("X320 FRONT_DOOR_ANCHORS_RESOLVE duplicate anchor", "front_door_checks", lambda: (fixture(), append("DOCUMENTATION.md", '<a id="term-plant"></a>')), "anchor id `term-plant` is not unique"),
    ("X306 GLOSSARY_PATHS_EXIST path missing", "front_door_checks", lambda: (fixture(), sub("DOCUMENTATION.md", "`protocols/grow.md`.", "`tools/no-such-tool.py`.")), "`tools/no-such-tool.py` does not resolve"),
    ("X306 GLOSSARY_PATHS_EXIST install literal", "front_door_checks", lambda: (fixture(), sub("DOCUMENTATION.md", "produces `.cypress/seed.json`", "produces `.cypress/no-such.json`")), "`.cypress/no-such.json` does not occur in install.sh"),
    ("X306 GLOSSARY_PATHS_EXIST install function", "front_door_checks", lambda: (fixture(), sub("DOCUMENTATION.md", "`write_seed_stamp`", "`write_nothing`")), "`write_nothing` is not a function install.sh defines"),
    ("X306 GLOSSARY_PATHS_EXIST no path", "front_door_checks", lambda: (fixture(), sub("DOCUMENTATION.md", r"^(- \*\*Implemented at:\*\*).*$", r"\1 the installer.", True)), "does not begin `n/a`"),
    ("X312 MECHANISM_CLAIMS_TRACED artifact missing", "front_door_checks", lambda: (fixture(), sub("DOCUMENTATION.md", "| `install.sh` (`place_file`) |", "| `tools/no-such.sh` |")), "Artifact: `tools/no-such.sh` does not resolve"),
]

# A row whose check is missing, or red on the unplanted copy, fails by name and
# the table runs on (SPEC-0005 ABORTED_STEP_HIDES_CASES): one red baseline never
# hides the rows after it. A needle may be a tuple: one finding holds them all.
baseline: dict = {}
failed = 0
for label, check, plant, needle, *absent in ROWS:
    key = (check, check == "front_door_checks")
    if key not in baseline:
        if key[1]:
            fixture()
        baseline[key] = set(lint(check))
        restore()
    needles = needle if isinstance(needle, tuple) else (needle,)
    if not key[1] and baseline[key]:
        ok, why = False, f"{check} is missing or red on the unplanted copy: {sorted(baseline[key])[:3]}"
    else:
        try:
            plant()
            new = [f for f in lint(check) if f not in baseline[key]]
            hit = [f for f in new if all(n in f for n in needles)]
            ok = not hit if absent else bool(hit)
            why = f"new findings: {new[:3]}" if not ok else ""
        except AssertionError as e:
            ok, why = False, str(e)
    restore()
    print(f"  {label} ({check}) — {'OK' if ok else 'FAIL'}" + (f": {why}" if why else ""))
    failed += not ok
print(f"seed-lint contract: {'FAIL' if failed else 'PASS'} ({len(ROWS) - failed}/{len(ROWS)} rows)")
sys.exit(1 if failed else 0)
PY
