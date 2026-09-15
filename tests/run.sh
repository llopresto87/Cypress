#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# --- seed integrity, across the WHOLE run -----------------------------------
# Most steps below install the seed into a temp target. An installer bug that
# wrote back into the seed instead of the target would corrupt the repository
# under test, and the gate would still pass: every suite that installs does so
# AFTER the previous suite has already run, so a per-suite before/after guard
# only sees its own window. A mutation appending one line to core/AGENTS.md
# from inside place_kernel() was demonstrated to survive the entire gate that
# way, because the first install corrupted the file eight steps before the one
# suite that checks it took its snapshot.
#
# So the snapshot is taken here, once, over every tracked seed file, and
# compared in an EXIT trap that fires wherever the run ends. This guards the
# whole tree, not just the kernel.
# Digest PATHS AND TYPES, not just regular-file contents. `-type f` was blind
# to symlinks, directories, fifos and mode changes: a mutation adding
# `ln -sfn /etc/passwd "$SEED_ROOT/LEAKED"` inside place_kernel() left the whole
# gate at EXIT=0 with the symlink sitting in the seed afterwards — and
# `install.sh --symlink` is exactly a symlink-writing code path, so that is the
# shape a real bug would take.
_seed_digest() {
    # In python3, not `find -printf` + `sha256sum`. Both are GNU-only: BSD find
    # has no `-printf` primary and macOS ships no `sha256sum`, so on the mac leg
    # of the CI matrix this function failed on its first line — before step 1,
    # under `set -e`, with zero diagnostic. The workflow declares two platforms
    # and one of them was executing no gates at all. python3 is already a hard
    # requirement of every suite here, so it is the portable floor.
    #
    # What is digested, and why each part is here. Every exclusion below was
    # narrowed at least once after something hid behind it:
    #
    # - Type, MODE and path for every entry, because for a hook the mode IS the
    #   payload: `chmod +x .git/hooks/pre-commit.sample` arms a script that was
    #   inert, and a bytes-only digest saw nothing.
    # - The BYTES of every regular file.
    # - The TARGET of every symlink — install.sh --symlink is a symlink-writing
    #   code path, and a hook laid as a link was invisible without this.
    # - Bytecode is excluded where bytecode lives and nowhere else. Pruning
    #   `__pycache__` wholesale made the directory a hiding place
    #   (`tools/__pycache__/notes.md` survived a whole gate); excluding `*.pyc`
    #   by name made the EXTENSION one at any depth (`tools/backdoor.pyc`), and
    #   7.13.1 was "the installer stops shipping its own bytecode", so a stray
    #   .pyc outside __pycache__ is exactly that regression. Only
    #   `__pycache__/*.pyc` churns, so only that is excluded — plus the
    #   `__pycache__` DIRECTORY ENTRY itself, whose first appearance on a clean
    #   checkout otherwise reads as "the gate modified the seed it was testing".
    # - `.git` is digested, minus `objects` and `logs`, which churn on any read.
    #   Its contents, not just its top-level names: a hook-writing bug lands in
    #   `.git/hooks/`. The prunes are anchored to full PATHS — `-name objects`
    #   matched any directory called `objects` at any depth, so
    #   `.git/hooks/logs/evil.sh` was a hiding place, verified.
    # - sha256, not cksum: cksum is a 32-bit affine CRC, so for any desired edit
    #   four filler bytes elsewhere can be solved for to restore it. Two files
    #   with opposite meanings and identical length collided on demand.
    SEED_ROOT_FOR_DIGEST="$ROOT" python3 - <<'PYEOF'
import hashlib, os, sys

root = os.environ["SEED_ROOT_FOR_DIGEST"]
git = os.path.join(root, ".git")
pruned = {os.path.join(git, "objects"), os.path.join(git, "logs")}
out = hashlib.sha256()
entries = []

for base, dirs, files in os.walk(root):
    if base in pruned:
        dirs[:] = []
        continue
    dirs[:] = [d for d in dirs if os.path.join(base, d) not in pruned]
    for name in list(dirs) + files:
        path = os.path.join(base, name)
        rel = os.path.relpath(path, root)
        if os.path.basename(base) == "__pycache__" and name.endswith(".pyc"):
            continue
        if name == "__pycache__" and os.path.isdir(path) and not os.path.islink(path):
            continue
        entries.append((rel, path))

for rel, path in sorted(entries):
    try:
        st = os.lstat(path)
    except OSError:
        continue
    if os.path.islink(path):
        kind, extra = "l", os.readlink(path).encode()
    elif os.path.isdir(path):
        kind, extra = "d", b""
    else:
        kind = "f"
        try:
            with open(path, "rb") as fh:
                extra = hashlib.sha256(fh.read()).digest()
        except OSError:
            extra = b"<unreadable>"
    out.update(f"{kind} {st.st_mode & 0o7777:04o} {rel}\n".encode())
    out.update(extra)

sys.stdout.write(out.hexdigest())
PYEOF
}
SEED_DIGEST_BEFORE="$(_seed_digest)"
_seed_integrity() {
    local rc=$?
    if [[ "$(_seed_digest)" != "$SEED_DIGEST_BEFORE" ]]; then
        echo "FAIL: the gate modified the seed it was testing — a suite wrote" >&2
        echo "      back into $ROOT instead of its temp target. Re-run with" >&2
        echo "      'git status' to see what moved; no suite may touch the seed." >&2
        exit 1
    fi
    exit $rc
}
trap _seed_integrity EXIT
bash "$ROOT/tests/test-unified-graph-install.sh"
bash "$ROOT/tests/test-knowledge-paths.sh"
bash "$ROOT/tests/test-orchestration-entry.sh"
# The entry fork: every way in reaches the protocol that fits the target.
# from-scratch was a complete nine-phase procedure nothing routed to — the
# kernel never named it and /initialize forwarded every repo to grow.
bash "$ROOT/tests/test-entry-paths.sh"
# Brainstorm has two audiences. The seed had one, and it could not finish
# without a user — so CYPRESS deliberating against itself had no home.
python3 "$ROOT/tests/test_brainstorm_modes.py"
# Tool authorship has an author, the rule keeps one home, and the close-out
# still spawns once. The rule home is the dangerous edit of that split.
python3 "$ROOT/tests/test_tool_authorship.py"
# Every machinery node can answer why it is on the roster: `prevents:` present
# and a peer edge to cross. Published as the home for that in two reference
# docs, and until now gated by nothing.
python3 "$ROOT/tools/roster-justification.py" --gaps
bash "$ROOT/tests/test-tier-lanes.sh"
bash "$ROOT/tests/test-graph-artifacts.sh"
bash "$ROOT/tests/test-spec-lint.sh"
# The linter above proves itself against FIXTURES. This runs it over the seed's
# own two specs, which nothing swept: spec-lint resolves its paths from its own
# location, so in the seed it looked for templates/knowledge-graph/specs, printed
# SKIP, and exited 0. The fabricated sign-off this remediation calls its worst
# product could be put straight back with the whole gate green — verified, twice.
# Shape defects are fatal; the uncovered-contract count is a ratchet in
# tests/ratchets.json, and spec-lint refuses a budget looser than the real debt.
# The budget is read on its own line rather than inline, because a step whose
# invocation spans a heredoc is invisible to tools/gate-registry.py.
SPEC_BUDGET="$(python3 -c 'import pathlib,re,sys; print((re.search(r"^SPEC_UNCOVERED_BUDGET = (\d+)", pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"), re.M) or [0,"0"])[1])' "$ROOT/tests/seed-lint.py")"
python3 "$ROOT/templates/knowledge-graph/spec-lint.py" --specs "$ROOT/docs/specs" --root "$ROOT" --uncovered-budget "$SPEC_BUDGET"
bash "$ROOT/tests/test-grill-lint.sh"
bash "$ROOT/tests/test-full-install.sh"
# Destination-placement contract (M2/M3/M7/M9). Discovers the placed file set
# from a real install rather than listing it, so a destination added later is
# held to the same contract without anyone remembering to extend the test.
bash "$ROOT/tests/test-install-placement.sh"
# Persistent plant state (S1-S6): owner decisions survive unrelated installs,
# adapters accumulate, projections stay derived, and the record can never
# contradict the filesystem.
bash "$ROOT/tests/test-plant-state.sh"
# Kernel placement (K1-K6): one body, copy mode isolates, symlink mode is live,
# adapter order is commutative. --symlink used to place the kernel as a frozen
# copy while every sibling was correctly linked.
bash "$ROOT/tests/test-install-kernel-modes.sh"
# Special-character target paths, and proof the seed's own budgets can fail.
# A budget that cannot fail is not a budget.
bash "$ROOT/tests/test-seed-budgets.sh"
# Non-pristine adoption: a target that already has instructions, a partial or
# older install, or a path in the way. The installer used to run the kernel and
# the whole graph scaffold to completion and THEN die on a raw `mkdir: Not a
# directory`, leaving a half-installed target.
bash "$ROOT/tests/test-install-adoption.sh"
bash "$ROOT/tests/test-bound-hook.sh"
bash "$ROOT/tests/test-graft-tools.sh"
bash "$ROOT/tests/test-growth-audit.sh"
bash "$ROOT/tests/test-agnosticism-lint.sh"
bash "$ROOT/tests/test-prose-lint.sh"
# Gate audibility (V5): a linter handed a file it cannot read must name the path
# and the reason and exit non-zero. All three used to `continue` in silence, so
# an unread input was indistinguishable from a clean one.
bash "$ROOT/tests/test-lint-audibility.sh"
bash "$ROOT/tests/test-nested-checkout.sh"
bash "$ROOT/tests/test-tool-help.sh"
bash "$ROOT/tests/test-collected-count.sh"
python3 "$ROOT/tests/test_frontmatter_contract.py"
# test-prose-lint.sh proves the linter works; this holds the seed's own
# front-door prose to it. Until 7.13.0 nothing did, and both files drifted:
# README.md carried committed tool-call residue, DOCUMENTATION.md's roster
# table was missing an agent added seven minor versions earlier, and its two
# halves disagreed with each other about the legal corpus's size.
# documentation/*-reference.md stay out of this gate for now — they use
# per-entry conventions (`Source file:` closers, one rule per entry) that §2
# and §20 read as repeated closers and decoration, and wiring them in before
# that genre question is settled would reward mangling correct reference prose
# to satisfy a meter.
python3 "$ROOT/tools/prose-lint.py" --file "$ROOT/README.md" --file "$ROOT/DOCUMENTATION.md"
bash "$ROOT/tests/test-status-register.sh"
bash "$ROOT/tests/test-status-migrate.sh"
bash "$ROOT/tests/test-seed-lint.sh"
bash "$ROOT/tests/test-legal-lint.sh"
# tool-corpus portability contract: a page that claims `Stability: portable`
# ships code an adopting project runs as-is, so the code must at least compile
# and the two behaviours the pages exist for must actually be demonstrated.
bash "$ROOT/tests/test-tool-corpus.sh"
# graph-lint CLI-contract regression (stdlib unittest — no third-party deps,
# matching graph-lint.py's own rule, so it always runs here).
python3 "$ROOT/tests/test_graph_lint.py"
python3 "$ROOT/integrations/claude-code/agent-lint.py" --lint --dir "$ROOT/agents"
python3 "$ROOT/integrations/claude-code/agent-lint.py" --eval --dir "$ROOT/agents"
# agent-lint CLI-contract regression. Stdlib unittest, like test_graph_lint.py
# beside it: this suite needed third-party pytest until 7.16.0, so run.sh
# probed for it and announced loudly when absent — but announcing is not
# failing, and the gate still exited 0 with a mandatory suite unexecuted. A
# green gate has to mean every required test RAN. Porting it removed the
# question rather than adding an environment requirement, and matches the rule
# every shipped script already follows: no third-party imports.
python3 "$ROOT/tests/test_agent_lint.py"
# Both routers must be reachable by the word forms people actually type. The
# `STEM = 6` fold shipped a comment naming test/tests and node/nodes and handled
# neither, so a third of each router's vocabulary scored zero against its own
# plural. This derives the vocabulary from the ROSTER and the NODE SET on every
# run rather than from a fixture, so it measures the tree that ships, and it
# holds the reviewed stem-collision list — the one risk a stemmer adds.
python3 "$ROOT/tests/test_router_reach.py"
# One responsibility — parse this repo's frontmatter — has five implementations,
# because graph-lint.py, agent-lint.py, status-register.py and friends each
# install into a plant as a STANDALONE file and cannot share an import without
# changing the placed file set. This drives all five over one input table and
# asserts what they agree on, in place of a shared module. Where they genuinely
# differ, the divergence is named in a test rather than papered over.
python3 "$ROOT/tests/test_metadata_equivalence.py"
python3 "$ROOT/tests/seed-lint.py"
# legal-corpus citability contract. seed-lint scans that corpus only for
# leaked host-IPs, pinned CVEs and dangling refs — none of which knows what a
# legal entry is, so the eight-field contract went ungated.
python3 "$ROOT/tests/legal-lint.py"
# The gate's own self-check, last: every step above must declare what it
# asserts, what it READS, and which false green it can still produce. Six
# suites prove a linter works while reading only fixtures — true of the linter,
# silent about the tree it ships. That difference was invisible until something
# recorded it, and a gate added without saying what it can miss is itself a
# defect. Registry entries are refused in both directions: an unclassified step,
# and a classified step that no longer runs.
# The registry's own regression, before the registry runs: its parser shipped
# seeing 4 of 8 invocation spellings while reporting OK, which is the quietest
# false green available — a gate it cannot see is not flagged as unclassified,
# it simply is not there.
# Every budget, threshold and debt ledger in this gate is a plain literal in
# the same file as the check it governs, so loosening one is a two-line edit
# that turns a real violation green — bloat the kernel and raise KERNEL_BUDGET,
# or break a legal page and file its 25 fresh failures as historical debt. The
# recorded values live in tests/ratchets.json; a limit may tighten freely and
# may only loosen by editing that file too, on purpose, in a diff someone reads.
python3 "$ROOT/tools/ratchet-lint.py"
python3 "$ROOT/tests/test_gate_registry.py"
python3 "$ROOT/tools/gate-registry.py" --lint
