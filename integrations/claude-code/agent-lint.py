#!/usr/bin/env python3
"""agent-lint.py — the mechanical agent-router, roster linter, and eval gate.

The knowledge router (`docs/graph/graph-lint.py --plan`) mechanizes the cheap
decision — which docs to read. This tool mechanizes the expensive one — which
specialist does the work — with the same executable floor, IDF-weighted scoring,
and honesty about being a keyword heuristic rather than an oracle.

It is the agent analog of `graph-lint.py`: it parses the roster's frontmatter,
scores each agent's `routing_triggers` / `name` / `description` against a task,
and returns a ranked list with a confidence band. It also lints the delegation
frontmatter and scores a golden routing corpus as a fail-closed gate.

Install target : docs/graph/agent-lint.py (every harness) + .claude/agent-lint.py (Claude Code projection)
Seed source    : cypress/integrations/claude-code/agent-lint.py
(kept byte-identical). Design of record:
  docs/plans/agent-routing-and-delegation.md  (§4 router, §4.1 schema, §4.3 eval)

Usage:
    python3 agent-lint.py --route "TASK"   # rank specialists + confidence band
    python3 agent-lint.py --lint           # validate roster frontmatter (default)
    python3 agent-lint.py --eval           # score the golden corpus; fail-closed

No third-party dependencies: it must run on a bare python3.
"""

from __future__ import annotations

import argparse
import itertools
import re
import sys
from dataclasses import dataclass
from functools import lru_cache
import importlib.util as _ilu
from pathlib import Path
from pathlib import Path as _Path

# The one frontmatter reader, loaded from beside this file. A COPY sits next to
# every consumer because the linters that ship into plants are standalone files
# with no package to import from; seed-lint enforces byte-identity across them.
_fm_spec = _ilu.spec_from_file_location(
    "cypress_frontmatter", _Path(__file__).resolve().parent / "frontmatter.py")
_frontmatter = _ilu.module_from_spec(_fm_spec)
_fm_spec.loader.exec_module(_frontmatter)


# ----------------------------- CONFIG -------------------------------------
# The router walks up for this directory the way route-hook.py walks up for
# docs/graph/graph-lint.py.
AGENTS_REL = Path(".claude") / "agents"
GOLDEN_NAME = "_routes.golden.tsv"

# Delegation-depth bounds (plan ADR-B): 1 <= max_spawn_depth <= 3.
MIN_DEPTH, MAX_DEPTH = 1, 3

# Confidence-band calibration (plan §4.2 — tunable, calibrated to the golden
# corpus). A single distinctive trigger double-hit scores weight(3)*2*2 = 12; a
# genuine multi-term route scores far higher, while a novel task that only grazes
# one stray trigger word tops out near 12. FLOOR sits in that gap so novel-stack
# tasks fall to LOW (the commission path) and real routes clear it.
FLOOR = 13
HIGH_RATIO = 1.5

# Eval gates, per corpus class. There is deliberately no single combined
# number: the classes measure different things and averaging them produced the
# "100% top-1" headline that hid a corpus written from the triggers it scored.
#
# CONTRACT_THRESHOLD is a CONSISTENCY check on the trigger set, not accuracy.
# Raised 0.90 -> 0.95. At 0.90 the floor bit at 55 of 61, so FIVE contract rows
# could stop routing to their own agent with the gate green — and a contract row
# failing means an agent's own trigger no longer selects it, which is a defect in
# the roster rather than a hard routing case. 0.95 bites at 58, closing most of
# that while leaving the documented headroom for the df shift that adding an
# agent causes. Measured when raised: 0.984 (60 of 61, one abstention).
EVAL_THRESHOLD = 0.95          # the contract-class threshold
# The lowest absolute score any shipped corpus row reaches while banding HIGH.
# Not a gate — a threshold for a note to the reader, because the band is
# relative and says nothing about whether the task belongs to this roster.
LOW_ABSOLUTE = 17
# The paraphrase floor is what the router actually achieves, as a ratchet. It is
# raised deliberately, by improving the router and re-measuring, never by
# editing a row.
#
# 2 of 17 was the honest number when this floor was first set. The lexical-reach
# repair took the router to 4 of 17 with 13 abstentions and the floor stayed at
# 2 for a while, on the reasoning that a floor is a minimum rather than a
# record. That left TWO rows of slack: half of the only class that measures
# generalization could break with ratchet-lint, --eval and the whole gate green.
# It also made the first sentence above false of its own constant. Tightening a
# floor costs nothing WHERE IT WAS MEASURED — no code changes, no behaviour
# change — so the slack had no defender, and 4 is what the router does against
# the roster this floor was measured over: the seed's own, every node of it
# `origin: seed`. It is free there and nowhere else, which is what
# MEASURED_ROSTER_ORIGIN below exists to say.
#
# It moved DOWN from 3 of 18 during review, and the direction is the point: a
# two-way overlap check found that one of the eighteen was the contract row
# "make the failing test pass" with three words appended. It was a trigger copy
# sitting in the held-out set, and it was one of only three rows the number
# rested on. Relabelling it cost a third of the headline. A floor that can only
# be lowered by finding contamination, and only raised by measuring a better
# router, is doing its job in both directions.
PARAPHRASE_FLOOR = 4
# ...and the floor is an ABSOLUTE count, so it has a denominator nobody wrote
# down: the roster it was measured over. Scoring is relative to the set of
# agents being ranked, so every agent a roster gains raises the document
# frequency of ordinary words, lowers every term's weight, and can push a top
# pick that is still CORRECT below the confidence band — where it counts as an
# abstention. Enlarging the roster is what `grow` and `graft` are for, so that
# shift is the mandated path rather than an edge case, and a floor keyed to
# whatever roster is on disk is a penalty for taking it. EVAL_THRESHOLD above
# was set with documented headroom for exactly this shift; this floor was set
# with none, which is the asymmetry the scoping closes.
#
# So the floor is keyed to the roster it was measured against — the one the
# seed ships, every node of it carrying the `origin: seed` ownership marker —
# the same way the class floors above are keyed to a corpus that declares
# classes. On a roster carrying anything else the count is REPORTED and not
# gated on, because a floor measured somewhere else is evidence rather than a
# verdict. Like the `classed` exemption, this one is keyed on the INPUT and is
# therefore reachable by changing it; what closes it for the seed's own roster
# is that the seed's roster is entirely seed-owned, so the gate is always live
# where the number was measured.
MEASURED_ROSTER_ORIGIN = "seed"
# The gate that matters. An abstention costs a session one reasoning step; a
# CONFIDENT wrong answer sends work to the wrong specialist with the band cited
# in the brief as evidence for doing so. Zero, in every class.
CONFIDENT_WRONG_BUDGET = 0
# ...except in the adversarial class, where it is a MEASUREMENT rather than a
# standard. Those rows are built to bait the router: each leans on vocabulary
# belonging to one agent while the work belongs to another. Demanding zero there
# would be demanding that a keyword heuristic resolve meaning, which is the one
# thing it cannot do — and the pressure would land on widening triggers until
# the corpus passes, which makes the router worse everywhere else.
#
# So the number is what the router achieves against deliberate baiting, and it
# may only fall. It is also the number that decides whether semantic
# adjudication (ledger U-34) is worth adopting: a layer that cannot move 2/12
# is not worth its cost, and one that clears it has earned the argument.
# RE-BASELINED 2 -> 3 on review, and the direction needs its reason on record
# because raising a budget is the exact move this repo's ratchet exists to stop.
#
# The 2 was measured over a corpus with three defective rows: one expected the
# wrong agent outright, one was a near-copy of its own target's triggers at 0.60
# overlap (a contract row wearing the adversarial label), and one named an agent
# that scored ZERO on the task — unwinnable rather than adversarial. The first
# was scoring as confident-CORRECT, which means the old 2 was partly produced by
# rewarding the router for taking a bait.
#
# With those rows corrected the honest figure is 3. That is a corrected
# measurement, not a relaxed limit: the instrument was wrong, not the router.
# The distinction matters and cannot be checked mechanically, which is why
# `tests/ratchets.json` has to be edited by hand and why this paragraph exists —
# a reader who does not believe it should re-judge the twelve rows, which is how
# both defective ones were found.
# 7.16.0 ratchets this DOWN to 2, and the fall is a measurement too. Repairing
# the routers' lexical reach — an inflection now scores as the word it inflects,
# and pronouns stopped being scoreable vocabulary — moved the adversarial class
# from 3 confident-wrong and 3 correct to 2 and 5, with paraphrase 2/17 -> 4/17
# and no regression in contract or unknown-domain. Nothing here was tuned to a
# row: see docs/plans/router-lexical-reach.md, which records the two candidate
# variants that would have bought a contract row back at the price of returning
# this number to 3, and why a confident wrong answer is the worse outcome.
#
# And it goes back to 3, on the owner's decision of 2026-09-15, because that
# fall did not survive review. The 2 was bought by a defect: `down` was the only
# directional particle missing from STOPWORDS (with `up`), and a trigger added
# in the same release made it df=1 vocabulary owned by `docs-librarian`. It was
# donating 12 of the 24 points that carried
#   `the delegation caps we agreed are written down nowhere in the graph`
# to its expected target, and simultaneously routing
#   `the checkout page went down for nine minutes ... found out from twitter`
# to the documentation agent at HIGH, 24 against a runner-up of 2. Closing the
# stopword gap kills the misroute and returns this class to 3.
#
# A 2x2 ablation over the same corpus separated the two changes: the roster
# additions moved the class 4 -> 2, the scorer repair 3 -> 2. So the paragraph
# above attributes the fall to the scorer and the measurement does not support
# it. This is a LOOSENING, which the ratchet makes the owner's to sign, and it
# is recorded here rather than absorbed: the router is not better than 3, and a
# limit that says otherwise is a limit bought with a live misroute.
ADVERSARIAL_CONFIDENT_WRONG_BUDGET = 3
# ...and the set it is measured over may not be quietly emptied. Without this,
# deleting the two rows the router fails takes the class to a clean 0 and both
# `--eval` and `ratchet-lint` pass with no trace — a budget that can only fall
# is worthless if the corpus under it can fall too. `PARAPHRASE_MIN_ROWS` exists
# for exactly this reason; the adversarial class shipped without its equivalent.
ADVERSARIAL_MIN_ROWS = 12
# A row claiming to be a paraphrase must not be a near-copy of its target's
# vocabulary. Above this, the label is false and the lint says so — which is
# what makes "authored without reading the triggers" a checkable claim rather
# than a promise in a comment.
#
# 0.50 is measured, not chosen. The seventeen genuine held-out rows top out at
# 0.43; substituting two words in a six-to-nine word trigger — which is how a
# reviewer smuggled four trigger copies past the previous 0.80 — lands at
# 0.67 to 0.71. The gap between those two populations is where the line goes.
#
# It is a floor, not a proof. A lexical measure cannot establish how a sentence
# was written, and a determined author can still paraphrase a trigger from
# memory. What it does is make the cheap attacks fail and force the expensive
# one to be deliberate, which is the most a mechanical check can honestly claim.
# Token overlap above which two golden rows are the same evidence twice. A
# ceiling, so it ratchets down. The duplicate check beside it normalizes only
# case and whitespace, which let `check`/`checking` and `adopt`/`adopting` pass
# at 0.80 and 0.82.
NEAR_DUPLICATE_CEILING = 0.60
# Pairs that are deliberately near-identical and earn it. Both are the
# inflection probes the corpus introduces in its own comment: they measure that
# a routing trigger is reached by its inflected form, which is a real property
# and cannot be measured by a differently-worded task.
# Each entry is the two tasks, lowercased and sorted, joined by " || " — a
# string rather than a frozenset so `ratchet-lint` can serialize it into
# tests/ratchets.json and refuse a fourth pair being added silently.
GRANDFATHERED_NEAR_DUPLICATES = {
    "check the change is integrated and not bolted on || "
    "checking the change is integrated and not bolted on",
    "adopt this project into the docs graph by subsystem boundary || "
    "adopting this project into the docs graph by subsystem boundary",
    # The contaminated paraphrase relabelled to `contract` when the two-way
    # overlap check found it, now sitting beside the row it was derived from.
    "make the failing test pass || make the failing test pass and nothing else",
}
PARAPHRASE_MAX_OVERLAP = 0.50
# The paraphrase set may not be quietly emptied to dodge the floor.
PARAPHRASE_MIN_ROWS = 15

CORPUS_CLASSES = ("contract", "paraphrase", "adversarial", "unknown-domain")

# STEM is the LAST-RESORT prefix fold, not the inflection rule. The inflection
# rule is `_stems()` in the canonical stemmer block below, which reduces both
# sides of the comparison; this only catches long words that share a six-letter
# prefix without sharing a stem (`documentation` / `documented`). Until 7.16.0
# this line read "prefix length for the singular/plural fold (test/tests,
# node/nodes)" and handled neither: the test is one-sided, requiring the TASK's
# word to PREFIX a roster word, and a plural never prefixes its own singular.
STEM = 6

# --- canonical stopwords ---------------------------------------------------
# Byte-identical in agent-lint.py and graph-lint.py; seed-lint's
# check_canonical_router_blocks enforces that.
#
# Filler words that carry no routing signal. The pronouns are here because they
# were NOT, and three shipped triggers already wrote "we" ("review the pull
# request before we merge", "do we need an ingest", "which protocol should we
# enter"). That made `we` a scoreable term at df=3, so every task phrased "we
# need X" paid three agents a weight-2 match for saying "we". A fourth trigger
# writing "our" took it further: df=1 earned the RARE-term bonus, and the task
# "our chain of language-model calls loops forever" routed HIGH to `security`
# on the strength of the word "our". A word every task writes cannot select
# between the agents every task is scored against.
STOPWORDS = frozenset(
    "the and for add new from that this with why how are was not you its "
    "change what where when does did into out about a an of to in on it "
    "over via using use onto off around per which while would could should "
    "want need make made get got run see tell show give take find "
    "there any some someone goes going tells told anyone something "
    "stack whole "
    # `down` and `up` were the only directional particles missing while
    # `out`, `off`, `on`, `onto`, `over` and `around` were all present, and
    # the gap cost the same way the pronouns did: a trigger added in 7.16.0
    # ("record what is not written down") made `down` df=1 scoreable
    # vocabulary owned by ONE agent, so "the checkout page went down for
    # nine minutes and we only found out from twitter" routed HIGH to the
    # documentation agent, score 24 against a runner-up of 2. Third instance
    # of one class -- `our`, then the reflexives, then this -- in the
    # release that closed it twice.
    "down up "
    "i me my mine we us our ours he him his she her hers they them their "
    "theirs your yours "
    # The reflexives were missing while every other person was present, and the
    # gap is not cosmetic: a probe agent carrying "yourself" as a trigger took
    # the whole band on "can you deploy this yourself" — df=1, so the pronoun
    # earned the RARE-term bonus and contributed 12 of 20 points. That is the
    # `our` incident above, reproduced with a reflexive, after the fix that was
    # supposed to close the class.
    "myself ourselves yourself yourselves himself herself itself themselves".split()
)
# --- end canonical stopwords -----------------------------------------------

# The spawn tool is the one tool whose presence is harness-enforced delegation
# capability (plan ADR-C): can_delegate MUST equal (spawn tool in tools). Its
# canonical name is `Agent` and `Task` is its alias; either grants it, bare or
# parenthesized (`Agent(type, …)`, whose type list a subagent definition
# ignores). docs/graph/method/delegation.md records the host mechanism.
SPAWN_TOOLS = ("Agent", "Task")
SPAWN_TOOL_LABEL = "the spawn tool (`Agent`, alias `Task`)"


def grants_spawn(tools) -> bool:
    """Whether a parsed `tools:` value grants the spawn tool.

    `None` is an omitted `tools:` line, and an agent without one inherits every
    tool, the spawn tool included. An entry counts when it is a spawn-tool name
    or starts with one followed by `(`; the prefix test also holds when the
    inline-list split cuts `Agent(a, b)` into `Agent(a` and `b)`. A raw string
    is read as the inline list it spells, so its outer brackets are dropped
    before the split rather than left on the first and last entries."""
    if tools is None:
        return True
    entries = tools.strip().strip("[]").split(",") if isinstance(tools, str) else tools
    for entry in (str(e).strip() for e in entries):
        if entry in SPAWN_TOOLS or entry.startswith(tuple(f"{n}(" for n in SPAWN_TOOLS)):
            return True
    return False


class LintError(Exception):
    pass


# --- frontmatter parsing --------------------------------------------------


@dataclass
class Agent:
    path: Path
    meta: dict
    body: str

    @property
    def name(self) -> str:
        return str(self.meta.get("name", "") or self.path.stem)

    @property
    def model(self) -> str:
        return str(self.meta.get("model", ""))

    @property
    def ident(self) -> str:
        """Human-facing identity for lint messages (stem + declared name)."""
        stem = self.path.stem
        name = str(self.meta.get("name", ""))
        return f"{stem}" if name in ("", stem) else f"{stem} ({name})"

    def get_list(self, key: str) -> list:
        v = self.meta.get(key, [])
        return v if isinstance(v, list) else [v]

    @property
    def tools(self) -> list:
        return [str(t) for t in self.get_list("tools")]

    @property
    def triggers(self) -> list:
        return [str(t) for t in self.get_list("routing_triggers")]

    @property
    def description(self) -> str:
        return str(self.meta.get("description", ""))

    @property
    def origin(self) -> str:
        """The graph's ownership marker: `seed` for a node the seed ships,
        anything else (or nothing) for one a project authored or adopted. The
        roster projections are file copies of docs/graph/agents/, so the marker
        travels with the node and a roster can be asked what it is made of."""
        return str(self.meta.get("origin", "")).strip()

    @property
    def can_delegate(self) -> bool:
        return str(self.meta.get("can_delegate", "")).strip().lower() == "true"

    @property
    def declares_tools(self) -> bool:
        return "tools" in self.meta

    @property
    def can_spawn(self) -> bool:
        return grants_spawn(self.meta.get("tools"))

    @property
    def max_spawn_depth(self):
        return self.meta.get("max_spawn_depth")

    @property
    def delegates_to(self) -> list:
        return [str(d) for d in self.get_list("delegates_to")]

    @property
    def effective_depth(self) -> int:
        """Leaves (can_delegate:false) sit at depth 0 (plan ADR-B)."""
        if not self.can_delegate:
            return 0
        d = self.max_spawn_depth
        return d if isinstance(d, int) else 0


def _scalar(v: str):
    """Parse the small YAML value subset the agent frontmatter permits.

    Extends graph-lint's `_scalar` with inline-list parsing (`[a, b, c]`), the
    form the agent `tools:` (and any inline `routing_triggers`) line uses — the
    parser gap the router must close so the spawn-tool⟺can_delegate rule can be checked.
    """
    v = v.strip()
    # Strip a trailing `  # comment` on unquoted, non-list values only.
    if v[:1] not in "\"'[" and "  #" in v:
        v = v.split("  #", 1)[0].strip()
    if v.startswith("[") and v.endswith("]"):
        inner = v[1:-1].strip()
        if not inner:
            return []
        return [x.strip().strip("\"'") for x in inner.split(",") if x.strip()]
    if v and v[0] in "\"'" and v[-1] == v[0] and len(v) > 1:
        return v[1:-1]
    if re.fullmatch(r"-?\d+", v):
        return int(v)
    return v


def parse_frontmatter(text: str, path: Path):
    """Delegates to the one frontmatter reader (see frontmatter.py).

    This function used to hold its own copy of the parsing rules. Seven
    programs held seven copies, and they disagreed: a description spilling
    onto a second line was rejected by two and silently truncated by three.
    The reader beside this file is this one, promoted verbatim, plus one
    level of nesting for the plant: block.
    """
    try:
        return _frontmatter.parse(text, path)
    except _frontmatter.FrontmatterError as e:
        raise LintError(str(e)) from None


# --- canonical plant-root boundary ---
def _is_plant_root(p) -> bool:
    """True where an upward walk must stop, that directory INCLUDED.

    Unbounded, these walks ascend seven or eight levels from both the cwd and
    the script's own directory and take the first artifact they find. A plant
    checked out inside another checkout therefore used the ANCESTOR's — a file
    the plant does not own, chosen by directory nesting. Reproduced from a git
    repo at `outer/sub/child` with no roster of its own: `agent-lint.py --route`
    returned the ancestor repository's agent at HIGH confidence, score 36, and
    `--lint` printed OK over that foreign roster.

    Callers test their candidate BEFORE calling this, so a plant whose artifact
    sits at its own repo root is still found; only the step BEYOND the root is
    denied.
    """
    return (p / ".git").exists() or (p / ".cypress").is_dir()
# --- end canonical plant-root boundary ---


def find_agents_dir() -> Path | None:
    """Walk up from cwd and the script's own location for a roster.

    Two homes are accepted: `.claude/agents/` (the Claude Code
    projection) and `docs/graph/agents/` (the graph home, present on
    EVERY harness — the kernel mandates `python3
    docs/graph/agent-lint.py --route` on all five tools, so the script
    must resolve a roster on opencode/codex/copilot/prime-agent plants
    that have no .claude/ at all)."""
    starts = [Path.cwd(), Path(__file__).resolve().parent]
    seen = set()
    for start in starts:
        p = start.resolve()
        for _ in range(8):
            if p in seen:
                break
            seen.add(p)
            # the graph home FIRST: a plant-commissioned expert is authored
            # into docs/graph/agents/ (the home) before any projection, and
            # the projection can be stale after a graft
            for rel in (Path("docs/graph/agents"), AGENTS_REL):
                cand = p / rel
                if cand.is_dir():
                    return cand
            if p.name == ".claude" and (p / "agents").is_dir():
                return p / "agents"
            if p.name == "graph" and (p / "agents").is_dir():
                return p / "agents"
            if _is_plant_root(p):
                break
            p = p.parent
    return None


def load_agents(adir: Path) -> list:
    agents = []
    for p in sorted(adir.glob("*.md")):
        if p.name.startswith("_"):
            continue
        meta, body = parse_frontmatter(p.read_text(encoding="utf-8"), p)
        agents.append(Agent(p, meta, body))
    if not agents:
        raise LintError(f"no agent defs found in {adir}")
    return agents


# --- scoring (mirror graph-lint.resolve) ----------------------------------


def _tokens(text: str) -> dict:
    """token -> the match strength this text can offer for it.

    2 for a token that appears on its OWN; 1 for one that appears only as a
    fragment of a hyphenated compound.

    The distinction is load-bearing. Splitting on hyphens and keeping the pieces
    as first-class tokens made `chain`, extracted from `security`'s trigger
    "assess the supply-chain and secrets handling risk", score exactly like a
    standalone word. So "our chain of language-model calls loops forever" routed
    to `security` at HIGH with a 5.5x margin — a confidently wrong answer the
    kernel then tells a brief to cite as evidence. The margin was never the
    problem: `chain` in "supply-chain risk" is simply not `chain` in "chain of
    calls", and a fragment should not be able to speak for the compound it came
    from. It still matches, at the near-match tier, so "supply chain" written
    without the hyphen is not lost.
    """
    strength: dict[str, int] = {}
    for w in re.findall(r"[a-z0-9_]+(?:[-/.][a-z0-9_]+)*", text.lower()):
        strength[w] = 2                      # the whole token, as written
        parts = [p for p in re.split(r"[-/.]", w) if p]
        if len(parts) > 1:
            for part in parts:
                strength.setdefault(part, 1)   # fragment: never upgrades a 2
    return strength


def _merge(*maps: dict) -> dict:
    """Union of token->strength maps, keeping the STRONGEST claim for each
    token. A plain `a | b` would let a fragment in one field silently demote a
    standalone occurrence in another."""
    out: dict[str, int] = {}
    for m in maps:
        for k, v in m.items():
            if v > out.get(k, 0):
                out[k] = v
    return out


# --- canonical stemmer -----------------------------------------------------
# This block is byte-identical in agent-lint.py and graph-lint.py and
# `seed-lint.py`'s check_canonical_router_blocks enforces that. (It read
# `check_stemmer_sync` for a release: a function of that name has never
# existed, in a comment shipped into every plant.) The two routers already
# carried one copied scorer; the copy is why the compound-fragment fix reached
# only one of them, and why a `STEM = 6` fold documented as handling
# "test/tests, node/nodes" handled neither, in both files, for four releases.

# Words whose trailing -s is not a plural, or whose -ed/-ing tail is not an
# inflection. Reducing these merges unrelated routing vocabulary.
STEM_KEEP = frozenset("""
access address always analysis axis basis bias bus business class cross css
devops focus gross https its less loss miss news ops pass plus press process
progress status this
""".split())

# Irregulars the suffix rules cannot reach. Deliberately tiny: every entry is a
# word shape this roster or a plant's node vocabulary actually uses, not a
# general English lexicon, which is a dependency this file may not have.
STEM_IRREGULAR = {
    "analyses": "analysis", "indices": "index", "matrices": "matrix",
    "vertices": "vertex", "criteria": "criterion", "schemas": "schema",
    "schemata": "schema", "aliases": "alias",
}

# INVARIANT, relied on by both `_match` implementations as a prefilter and
# asserted by tests/test_router_reach.py: every form `_stems(w)` returns starts
# with the same three characters as `w`. Every rule here either strips a suffix
# (leaving a prefix), appends `e` to a prefix, swaps a `-ies` tail for `y`, or
# maps an irregular that shares its first three letters. Anything added that
# breaks this makes the prefilter skip a real match, so the test is the price of
# the optimisation.
STEM_PREFIX = 3

# (suffix, characters to drop, minimum word length). First match wins, so the
# longer and more specific endings are listed first.
STEM_RULES = (
    ("ies", 3, 5), ("sses", 2, 6), ("ches", 2, 6), ("shes", 2, 6),
    ("xes", 2, 5), ("ing", 3, 6), ("ed", 2, 5), ("es", 1, 5), ("s", 1, 4),
)


@lru_cache(maxsize=4096)
def _stems(word: str) -> frozenset:
    """The canonical forms of one word, for comparison against another word's.

    A frozenset rather than a string because English drops a silent -e before
    -ing and -ed: `routing` reduces to `rout`, but the word it inflects is
    `route`. Both candidates are returned and a match is a non-empty
    intersection, which keeps this function free of any vocabulary and
    therefore symmetric — the task side and the roster side are reduced by
    exactly the same rule, which the previous one-sided prefix probe was not.
    """
    if word in STEM_IRREGULAR:
        return frozenset({STEM_IRREGULAR[word]})
    if word in STEM_KEEP or len(word) < 4:
        return frozenset({word})
    for suf, cut, minlen in STEM_RULES:
        if word.endswith(suf) and len(word) >= minlen:
            base = word[:-3] + "y" if suf == "ies" else word[:-cut]
            if suf in ("ing", "ed"):
                # Undouble only a base longer than three letters. `planning`
                # reduces to `plann` and must lose the doubled consonant, but
                # `added` reduces to `add`, whose double IS the word — taking it
                # to `ad` is wrong, and it also broke the three-character stem
                # prefix the `_match` prefilter depends on. Same for `ebbed`,
                # `egged`, `adding`.
                if len(base) > 3 and base[-1] == base[-2]:
                    return frozenset({base[:-1]})          # planning -> plan
                return frozenset({base, base + "e"})       # routing -> rout|route
            if suf in ("sses", "ches", "shes", "xes"):
                # -ches is the plural of -ch AND of -che, and nothing in the
                # word says which: batches -> batch, caches -> cache. Offer
                # both rather than guess, the same way -ing does.
                return frozenset({base, word[:-1]})        # batch|batche
            return frozenset({base})
    return frozenset({word})
# --- end canonical stemmer -------------------------------------------------


def _match(term: str, toks: dict) -> int:
    """Match strength: 2 standalone, 1 compound fragment or prefix-fold, 0 none.
    Never substring.

    An inflection scores as the word it inflects (`nodes` on `node`), at that
    token's OWN strength — so a compound fragment stays a fragment and the
    score scale is unchanged. It is not a weaker kind of evidence: `check` and
    `checked` are the same word, and scoring them differently made one route
    turn on the tense of one word.
    """
    direct = toks.get(term, 0)
    if direct:
        return direct
    st = _stems(term)
    # Prefilter on the shared three-character prefix before reducing each token:
    # the stem loop ran for every token of every agent for every term and made
    # routing 2.9x slower. Sound by the STEM_PREFIX invariant above.
    pre = {s[:STEM_PREFIX] for s in st}
    for k, v in toks.items():
        if k[:STEM_PREFIX] in pre and _stems(k) & st:
            return v
    if len(term) >= STEM and any(k.startswith(term[:STEM]) for k in toks):
        return 1
    return 0


def _terms(task: str):
    """Extract match terms as (term -> strength, candidate compounds).

    The second value is adjacent word pairs rejoined with a hyphen. They are
    CANDIDATES rather than terms because whether "from scratch" means the
    compound `from-scratch` depends on the roster, which this function cannot
    see; `score()` keeps the ones the roster actually writes and drops the rest.
    Returning them separately keeps that decision where the evidence is.

    Same rule as `_tokens`, applied to the other side of the comparison: a term
    the task states on its own is worth 2, a term that only appears as a piece
    of a longer compound is worth 1. Without the symmetry the fix is half done —
    `language-model` still offered `model` at full strength, so a task about
    model CALLS kept matching `security`'s "threat model" as if the words were
    the same word.
    """
    out: dict[str, int] = {}
    words = re.findall(r"[a-z0-9_/*.-]+", task.lower())
    for w in words:
        pieces = re.split(r"[/*.-]+", w)
        for part in [w, *pieces]:
            part = part.strip("_")
            if len(part) < 3 or part in STOPWORDS:
                continue
            # the term as written is standalone; a piece of a compound is not
            strong = 2 if part == w or len(pieces) == 1 else 1
            if strong > out.get(part, 0):
                out[part] = strong

    # Adjacent pairs are offered as candidate compounds, and `score()` keeps
    # only the ones the roster actually uses as compounds. Emitting every pair
    # unconditionally invented concepts nobody wrote: "staging cluster" and
    # "transport request" became first-class terms and pulled two tasks to
    # `reliability` at MEDIUM and HIGH, one of them a row that must abstain.
    # A compound counts when the roster knows it, not when two words happen to
    # sit next to each other.
    candidates = set()
    for a, b in zip(words, words[1:]):
        joined = f"{a}-{b}"
        if len(joined) >= 3:
            candidates.add(joined)
    return out, candidates


def _token_sets(agent: Agent):
    name_toks = _tokens(agent.name)
    trig_toks = _tokens(" ".join(agent.triggers))
    desc_toks = _tokens(agent.description)
    return name_toks, trig_toks, desc_toks


def score(agents: list, task: str):
    """Rank agents for a task. IDF-weighted: a term matching many agents is
    generic (low weight); one matching one or two is distinctive (dominates).

    score(agent) = Σ_t weight(t) · max(2·match(name), 2·match(trigger),
    1·match(desc)) — triggers and name are first-class, description is the
    fallback (plan §4.2).
    """
    terms, candidates = _terms(task)
    buckets = {a.name: _token_sets(a) for a in agents}

    # Which hyphenated compounds the roster actually writes. A task that says
    # "from scratch" means the trigger's "from-scratch" and should match it at
    # full strength; a task that says "chain of calls" forms no compound the
    # roster uses, so the fragment discount stands. The difference between those
    # two is the whole point, and it is decided here rather than guessed in the
    # tokenizer, which cannot see the roster.
    # Name and TRIGGERS only — deliberately not descriptions. A description is
    # prose, and prose carries compounds as metaphors: `devils-advocate` writes
    # "load-bearing claim", `pentest` writes "design-time threat models". Reading
    # two adjacent task words as a compound is already an inference; letting a
    # metaphor license it turned "the load bearing situation in the billing
    # module" into a confident route to an adversarial reviewer. The routing
    # vocabulary an agent chose on purpose is its name and its triggers.
    known_compounds = set()
    for _n, _t, _d in buckets.values():
        for tok in (*_n, *_t):
            if "-" in tok:
                known_compounds.add(tok)
    # A bigram is EVIDENCE THIS FUNCTION SYNTHESIZED: the task wrote two words,
    # and we are choosing to read them as the compound the roster uses. That is
    # a weaker thing than a word the task actually wrote, and it gets scored
    # accordingly below — exact matches only, and no rare-term bonus.
    #
    # Both restrictions come from observed misroutes. "design time constants"
    # formed `design-time`, which is a real compound only because `pentest`
    # writes it; the prefix fold then matched it against `security`'s unrelated
    # trigger word "design" and added the 2 points that carried `security` from
    # 12 (below FLOOR) to 14 (above it) — a confident wrong route about config
    # constants. And "multi agent negotiation between chefs, just kidding" rose
    # from MEDIUM to HIGH purely because the synthesized `multi-agent` collected
    # the rare-term multiplier. A compound we inferred should be able to confirm
    # a route; it should not be able to create one.
    bigram_terms = set()
    for cand in candidates:
        if cand in known_compounds and terms.get(cand, 0) < 2:
            terms[cand] = 2
            bigram_terms.add(cand)

    df = {t: 0 for t in terms}
    for name_toks, trig_toks, desc_toks in buckets.values():
        allt = _merge(name_toks, trig_toks, desc_toks)
        for t in terms:
            if _match(t, allt):
                df[t] += 1

    def weight(t: str) -> int:
        d = df.get(t, 0)
        return 3 if d <= 1 else 2 if d <= 3 else 1

    entries = []
    for a in agents:
        name_toks, trig_toks, desc_toks = buckets[a.name]
        s = 0
        for t, ts in terms.items():
            inferred = t in bigram_terms
            # min(): the weaker of the two claims wins, so a match is only as
            # strong as the flimsier side of it. This keeps the score scale
            # unchanged — a standalone term on a standalone token is still 2 —
            # so FLOOR and HIGH_RATIO stay calibrated to the same numbers.
            # An inferred compound matches only where it literally appears;
            # the prefix fold is for words the task really wrote.
            mfn = (lambda term, toks: toks.get(term, 0)) if inferred else _match
            eff = max(
                2 * min(ts, mfn(t, name_toks)),
                2 * min(ts, mfn(t, trig_toks)),
                1 * min(ts, mfn(t, desc_toks)),
            )
            # Distinctiveness amplifies a CONFIDENT match, never a graze. A term
            # that matches only one agent gets weight 3 for being rare — but
            # rarity says nothing about whether the match means anything, and
            # multiplying a compound fragment or a description-only brush by 3
            # is how two incidental words ("chain", "calls") out-voted a whole
            # task. Only a full-strength name or trigger hit (eff == 4) earns
            # the rare-term bonus; weaker evidence is capped.
            w = weight(t) if eff >= 4 else min(weight(t), 2)
            if inferred:
                w = min(w, 2)          # no rare-term bonus for inferred evidence
            s += w * eff
        if s:
            entries.append((s, a))
    entries.sort(key=lambda x: (-x[0], x[1].name))
    return entries


def confidence(entries: list) -> str:
    best = entries[0][0] if entries else 0
    second = entries[1][0] if len(entries) > 1 else 0
    if best == 0:
        return "NONE"
    if best < FLOOR:
        return "LOW"
    if best >= HIGH_RATIO * second:
        return "HIGH"
    return "MEDIUM"


# --- commands -------------------------------------------------------------

BANNER = "Router suggestion is a keyword heuristic — reason over it, not an oracle."


def cmd_route(agents: list, task: str) -> int:
    entries = score(agents, task)
    band = confidence(entries)
    top = entries[0][1].name if entries else None

    print(BANNER)
    print()
    print(f"task: {task}")
    print()
    print(f"ROUTE (ranked, confidence: {band}):")
    for s, a in entries[:5]:
        print(f"  {a.name:<18} {a.model:<6} can_delegate={str(a.can_delegate).lower():<5} score={s}")
    if band in ("HIGH", "MEDIUM"):
        print(f"HINT: cite this in the delegation brief. {band} → top candidate `{top}`"
              f"{'.' if band == 'HIGH' else '; confirm before routing.'}")
        # The band is RELATIVE — it says the winner beat the runner-up, never
        # that the task belongs to this roster at all. "design a crop rotation
        # for the north field" takes HIGH at 16 because `rotation` is a rare
        # word here (secrets posture: compromise means rotation) and nothing on
        # the roster is written for farming. Three ways of separating that
        # lexically were tried and none works — a foreign task collects the same
        # scattered weak matches a real one does. So this is a NOTE to the
        # reader, which is the right instrument: the route is advice a model
        # mediates, not a gate. LOW_ABSOLUTE is the bottom of the shipped
        # corpus's HIGH range; below it, the win is over weak competition.
        if entries and entries[0][0] < LOW_ABSOLUTE:
            print(f"      NOTE: absolute score {entries[0][0]} is at the bottom of the "
                  f"range real tasks score in. The band compares candidates; it "
                  f"cannot tell whether this task is in the roster's domain at "
                  f"all. Check that before citing it.")
        print("      If you override to a different/generic agent, record why "
              "(deliver assertion checks this).")
    else:
        print("HINT: no clear specialist — name the gap before filling it. "
              "Knowledge nobody on the roster is written for is an expertise "
              "node (docs/graph/nodes/_expertise.template.md), which the "
              "router composes into the roster you already have; commission "
              "an expert from templates/agent.template.md only when the work "
              "needs its own tools, model class, stance, or isolation.")
    # This ranks files ON DISK. It cannot see the host's session registry, so
    # it will name a specialist a just-installed session is unable to spawn.
    print("NOTE: fit only, not registration — this reads .claude/agents/ off "
          "disk, not the host's session registry. Preflight the type before "
          "dispatch (docs/graph/method/delegation.md, "
          "delegation.harness-registration).")
    return 0


def _distinctiveness_warnings(agents: list) -> list:
    """Rule 4 (plan §4.1): warn when a trigger token is shared across too many
    agents — a non-distinctive trigger carries no routing signal (the IDF
    analog). Warnings never fail the lint."""
    limit = max(3, len(agents) // 2)
    token_owners: dict = {}
    for a in agents:
        for tok in _tokens(" ".join(a.triggers)):
            if len(tok) < 3 or tok in STOPWORDS:
                continue
            token_owners.setdefault(tok, set()).add(a.name)
    warns = []
    for tok, owners in sorted(token_owners.items()):
        if len(owners) > limit:
            warns.append(f"trigger token {tok!r} shared across {len(owners)} agents "
                         f"(low routing signal): {', '.join(sorted(owners))}")
    return warns


def cmd_lint(agents: list) -> int:
    names = {a.name for a in agents}
    depth_by_name = {a.name: a.effective_depth for a in agents}
    errs = []

    for a in agents:
        # Rule 1: routing_triggers present and non-empty.
        if not a.triggers:
            errs.append(f"{a.ident}: routing_triggers missing or empty (§4.1 rule 1)")

        # Rule 2: can_delegate == (spawn tool in tools). No dormant-but-enabled
        # drift. An omitted tools: line inherits the spawn tool, so "cannot
        # spawn" holds only for an agent that lists its tools.
        if not a.declares_tools:
            errs.append(f"{a.ident}: omits its tools: line, so it inherits every "
                        f"tool, {SPAWN_TOOL_LABEL} included — list the tools it "
                        f"may use (§4.1 rule 2)")
        elif a.can_delegate != a.can_spawn:
            errs.append(
                f"{a.ident}: can_delegate={str(a.can_delegate).lower()} but "
                f"{SPAWN_TOOL_LABEL} {'is' if a.can_spawn else 'is not'} in tools — "
                f"can_delegate must equal (spawn tool ∈ tools) (§4.1 rule 2)"
            )

        # Rule 3: delegation caps present and coherent iff can_delegate.
        if a.can_delegate:
            d = a.max_spawn_depth
            if not isinstance(d, int) or not (MIN_DEPTH <= d <= MAX_DEPTH):
                errs.append(f"{a.ident}: max_spawn_depth must be an int in "
                            f"[{MIN_DEPTH},{MAX_DEPTH}] (got {d!r}) (§4.1 rule 3)")
            if not a.delegates_to:
                errs.append(f"{a.ident}: can_delegate:true requires a non-empty "
                            f"delegates_to allowlist (§4.1 rule 3)")
            for target in a.delegates_to:
                if target not in names:
                    errs.append(f"{a.ident}: delegates_to → unknown agent {target!r}")
                    continue
                if isinstance(d, int) and depth_by_name[target] >= d:
                    errs.append(
                        f"{a.ident}: delegates_to → {target!r} has depth "
                        f"{depth_by_name[target]} ≥ this agent's {d}; the allowlist "
                        f"must name strictly-shallower agents (leaves = 0) (ADR-B)"
                    )
        else:
            if a.max_spawn_depth is not None:
                errs.append(f"{a.ident}: max_spawn_depth is set but can_delegate is "
                            f"false — leaves carry no caps (§4.1 rule 3)")
            if a.delegates_to:
                errs.append(f"{a.ident}: delegates_to is set but can_delegate is "
                            f"false — leaves carry no allowlist (§4.1 rule 3)")

    for w in _distinctiveness_warnings(agents):
        print(f"agent-lint: warning: {w}", file=sys.stderr)

    if errs:
        print(f"agent-lint: {len(errs)} error(s) across {len(agents)} agent(s)\n",
              file=sys.stderr)
        for e in errs:
            print(f"  ✗ {e}", file=sys.stderr)
        return 1

    print(f"agent-lint: OK — {len(agents)} agents, frontmatter and delegation graph valid")
    return 0


def load_golden(adir: Path):
    """Rows as (task, expected, corpus_class). The class column is optional and
    defaults to `contract`, so a corpus written before the split still loads."""
    path = adir / GOLDEN_NAME
    if not path.exists():
        raise LintError(f"missing golden corpus: {path}")
    rows = []
    classed = False
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "\t" not in line:
            continue
        parts = [c.strip() for c in line.split("\t")]
        task, expected = parts[0], parts[1]
        # The class column is optional, so a corpus written before the split
        # still loads. An absent class means `contract`, EXCEPT for a row that
        # expects LOW: that row is unknown-domain by what it asserts, and
        # defaulting it to `contract` would reject every two-column corpus a
        # plant already carries.
        if len(parts) > 2 and parts[2]:
            cls = parts[2]
        else:
            cls = "unknown-domain" if parts[1] == "LOW" else "contract"
        if cls not in CORPUS_CLASSES:
            raise LintError(
                f"{path.name}: unknown corpus class {cls!r} for task {task!r} "
                f"(expected one of {', '.join(sorted(CORPUS_CLASSES))})")
        # A row expecting LOW is `unknown-domain` by definition: it asserts that
        # nothing on the roster fits. Allowing it to wear the `paraphrase` label
        # was the way round PARAPHRASE_MIN_ROWS — pad the held-out set with
        # twelve rows of gibberish expecting LOW, and a corpus with three real
        # paraphrases reports "13 of 15 confident-correct" instead of the honest
        # 2 of 17. That reads as a router generalizing at 87%, which is worse
        # than the shrinking the row floor was written to prevent.
        # Only an EXPLICIT wrong label is refused; the default above is
        # already correct, so a legacy two-column corpus is never penalised
        # for a column it does not have.
        if expected == "LOW" and cls != "unknown-domain" and len(parts) > 2:
            raise LintError(
                f"{path.name}: task {task!r} expects LOW but is labelled "
                f"{cls!r}. A row that expects abstention is unknown-domain; "
                f"labelling it otherwise inflates the class it is filed under")
        if len(parts) > 2 and parts[2]:
            classed = True
        rows.append((task, expected, cls))
    if not rows:
        raise LintError(f"golden corpus is empty: {path}")
    # Distinct tasks, or the row floor counts the same evidence twice. Repeating
    # one genuinely-correct paraphrase twenty times satisfied PARAPHRASE_MIN_ROWS
    # and reported "20 of 20 confident-correct" — a perfect generalization score
    # from a single example, which is a worse lie than the padding it replaced.
    seen: dict[str, int] = {}
    for i, (task, _e, _c) in enumerate(rows):
        key = " ".join(task.lower().split())
        if key in seen:
            raise LintError(
                f"{path.name}: task {task!r} appears more than once (rows "
                f"{seen[key] + 1} and {i + 1}). Every row must be distinct "
                f"evidence; duplicates inflate whichever class they sit in")
        seen[key] = i

    # ...and a NEAR-duplicate does the same thing while passing the test above,
    # which normalizes only case and whitespace. Three pairs sit at 0.62-0.82
    # token overlap in the shipped corpus, so the 61-row contract denominator
    # counts the same evidence twice, three times over.
    #
    # Two of the three are DELIBERATE and stay: `check`/`checking` and
    # `adopt`/`adopting` are the inflection probes the corpus's own comment
    # introduces ("the two real ones are here as ordinary contract rows"), and
    # deleting them would delete real coverage. They are named here rather than
    # tolerated by a loose threshold, so a FOURTH near-duplicate — the actual
    # risk, since padding a class with restatements is exactly the evasion the
    # row floors exist to stop — fails instead of arriving silently.
    for (i, (ta, _ea, ca)), (j, (tb, _eb, cb)) in itertools.combinations(
            list(enumerate(rows)), 2):
        wa = {w for w in re.findall(r"[a-z0-9]+", ta.lower())}
        wb = {w for w in re.findall(r"[a-z0-9]+", tb.lower())}
        if not (wa and wb):
            continue
        score = len(wa & wb) / len(wa | wb)
        if score < NEAR_DUPLICATE_CEILING:
            continue
        # SAME class only. The harm is a class's own denominator counting one
        # piece of evidence twice; a near-duplicate ACROSS classes is a
        # different defect and already has an owner — the two-way overlap check
        # that produces MISLABELLED_PARAPHRASE. Scanning across classes made
        # this fire first and mask it, turning two tests that deliberately
        # plant a restatement into failures naming the wrong check. A
        # wrong-reason RED hides a real check exactly as a wrong-reason green
        # certifies a missing one.
        if ca != cb:
            continue
        pair = " || ".join(sorted((" ".join(ta.lower().split()),
                                   " ".join(tb.lower().split()))))
        if pair in GRANDFATHERED_NEAR_DUPLICATES:
            continue
        raise LintError(
            f"{path.name}: rows {i + 1} and {j + 1} are near-duplicates at "
            f"{score:.0%} token overlap ({ta!r} / {tb!r}), both in "
            f"{ca}/{cb}. A restatement is not new evidence: it inflates its "
            f"class's denominator with the row already there. Reword one into a "
            f"genuinely different task, or record the pair in "
            f"GRANDFATHERED_NEAR_DUPLICATES with the reason it earns its place.")
    # `classed` says whether this corpus uses the class column at all. Every
    # already-grown plant carries a two-column corpus with no paraphrase or
    # adversarial rows, because those classes did not exist when it was written.
    # The minimum-row floors must bite at ZERO for a corpus that declares
    # classes — deleting a whole class was the evasion they exist to stop — and
    # must not fire at all for one that never had them, or upgrading the tool
    # fails every plant in the field.
    return rows, classed


def _content_words(text: str) -> set:
    return {w for w in re.findall(r"[a-z0-9_]+", text.lower())
            if len(w) >= 3 and w not in STOPWORDS}


def _overlap(task: str, agent) -> float:
    """How much of this row is the agent's own words, measured both ways.

    This is the honesty instrument, so it has to survive someone trying to get
    round it. The obvious measure — what fraction of the TASK is the agent's
    vocabulary — is defeated by padding: appending two filler words to a
    verbatim trigger copy drops it from 1.00 to 0.75, under the 0.80 threshold,
    and the copy then counts as a held-out paraphrase.

    So the second measure is how much of the agent's NEAREST TRIGGER the task
    reproduces. Padding cannot lower that: a task containing every content word
    of a trigger has swallowed that trigger whole no matter what else it says.
    The verdict is the larger of the two, because either one being high is
    enough to make the row a copy rather than a paraphrase.
    """
    vocab = _merge(*_token_sets(agent))
    words = _content_words(task)
    if not words:
        return 1.0
    task_side = sum(1 for w in words if w in vocab) / len(words)

    trigger_side = 0.0
    for trig in agent.triggers:
        tw = _content_words(trig)
        if not tw:
            continue
        covered = sum(1 for w in tw if w in words) / len(tw)
        trigger_side = max(trigger_side, covered)
    return max(task_side, trigger_side)


def cmd_eval(agents: list, adir: Path) -> int:
    """Score the golden corpus, per class, and gate on the failure that hurts.

    The old report was one line — "top-1 accuracy 100.0% (55/55)" — over a
    corpus in which 46 of those 55 tasks were written out of the triggers of the
    agent they select. The number was arithmetically true and rhetorically
    false: it reads as "the router is right almost always" when it means "the
    trigger set is self-consistent". Every number printed here therefore names
    the corpus it was computed over, and the classes are never averaged.
    """
    rows, classed = load_golden(adir)
    by_name = {a.name: a for a in agents}
    # The roster the absolute floor was measured over (MEASURED_ROSTER_ORIGIN).
    # `classed` asks whether the corpus is the one the class floors were written
    # for; this asks the same question of the other input the floor depends on.
    measured_roster = bool(agents) and all(
        a.origin == MEASURED_ROSTER_ORIGIN for a in agents)

    # X2: a row may not claim to be a paraphrase while being a near-copy of its
    # target's own vocabulary. Checked before anything is scored, because a
    # mislabelled row corrupts the only class that measures generalization.
    label_faults = []
    for task, expected, cls in rows:
        # Both held-out classes, not just one. `adversarial` rows are supposed
        # to BAIT the router with another agent's vocabulary; a row that instead
        # copies its OWN target's triggers is a contract row wearing the wrong
        # label, and it was invisible because this check asked only about
        # paraphrase. One such row was sitting at 0.60.
        if cls not in ("paraphrase", "adversarial") or expected not in by_name:
            continue
        ov = _overlap(task, by_name[expected])
        if ov > PARAPHRASE_MAX_OVERLAP:
            label_faults.append((task, expected, ov, cls))

    classes: dict[str, dict] = {}
    for task, expected, cls in rows:
        bucket = classes.setdefault(
            cls, {"n": 0, "hit": 0, "abstain": 0, "wrong": 0,
                  "overlap": [], "detail": []})
        bucket["n"] += 1
        entries = score(agents, task)
        band = confidence(entries)
        top = entries[0][1].name if entries else None
        if expected in by_name:
            bucket["overlap"].append(_overlap(task, by_name[expected]))

        if expected == "LOW":
            # Nothing on the roster is written for this. Confidence IS the
            # answer: anything above LOW is the leak.
            if band in ("LOW", "NONE"):
                bucket["hit"] += 1
            else:
                bucket["wrong"] += 1
                bucket["detail"].append(
                    f"leak: {task!r} → {band} (top {top!r}); must be LOW/NONE "
                    f"(commission path)")
            continue

        if band in ("LOW", "NONE"):
            # Abstention. For a contract row that is a defect — the trigger no
            # longer reaches its owner. For a paraphrase row it is the designed
            # outcome of a keyword heuristic with no signal.
            bucket["abstain"] += 1
            if cls == "contract":
                bucket["detail"].append(
                    f"contract row abstained: {task!r} → {band}; expected "
                    f"{expected!r} — its own trigger no longer selects it")
        elif top == expected:
            bucket["hit"] += 1
        else:
            bucket["wrong"] += 1
            bucket["detail"].append(
                f"CONFIDENT-WRONG: {task!r} → {band} {top!r}, expected {expected!r}")

    # Vacuity guard. A corpus of nothing but abstain-expected rows once scored
    # 1.0 from a 0/0 guard and printed "OK — accuracy 100.0%": a fail-closed
    # gate passing on a corpus that asks it to route nothing. What makes the
    # gate non-vacuous is at least one row that actually demands a ROUTE.
    routed = sum(1 for _t, e, _c in rows if e != "LOW")
    if not routed:
        print("agent-lint --eval: FAIL — the corpus asks for zero routes (every "
              "row expects abstention); a 0/0 accuracy gate is vacuous",
              file=sys.stderr)
        return 1
    if not classes.get("contract", {}).get("n"):
        print("agent-lint --eval: FAIL — no contract rows; the trigger set has "
              "no acceptance contract", file=sys.stderr)
        return 1

    print("agent-lint --eval: per-corpus results (never averaged — the classes "
          "measure different things)")
    for cls in CORPUS_CLASSES:
        b = classes.get(cls)
        if not b:
            continue
        ov = (sum(b["overlap"]) / len(b["overlap"])) if b["overlap"] else 0.0
        note = {
            "contract": "consistency check: tasks share their target's vocabulary",
            "paraphrase": "generalization: authored without reading any triggers; "
                          "abstention is a correct outcome",
            "adversarial": "bait phrasings",
            "unknown-domain": "must abstain",
        }[cls]
        print(f"  {cls:<15} n={b['n']:<3} confident-correct={b['hit']:<3} "
              f"abstained={b['abstain']:<3} CONFIDENT-WRONG={b['wrong']:<3} "
              f"mean-overlap-with-target={ov:.2f}")
        print(f"  {'':<15} ({note})")

    for task, expected, ov, cls in label_faults:
        print(f"  ✗ mislabelled {cls}: {task!r} shares {ov*100:.0f}% of its "
              f"vocabulary with {expected!r} — that is a contract row, not a "
              f"{cls}; relabel it rather than counting it as held out",
              file=sys.stderr)
    for cls in CORPUS_CLASSES:
        for line in classes.get(cls, {}).get("detail", []):
            print(f"  ✗ [{cls}] {line}", file=sys.stderr)

    contract = classes["contract"]
    scored = contract["n"]
    acc = contract["hit"] / scored if scored else 1.0
    para = classes.get("paraphrase", {"n": 0, "hit": 0})
    adversarial_wrong = classes.get("adversarial", {}).get("wrong", 0)
    total_wrong = sum(b["wrong"] for cls, b in classes.items() if cls != "adversarial")

    failures = []
    if label_faults:
        # Printed above AND fatal. A diagnostic with no effect on exit status is
        # the same defect this release fixed in three linters: it tells a reader
        # something is wrong and tells the gate everything is fine.
        failures.append(
            f"{len(label_faults)} held-out row(s) are near-copies of their "
            f"target's vocabulary — a held-out set must stay held out")
    if total_wrong > CONFIDENT_WRONG_BUDGET:
        failures.append(
            f"{total_wrong} confident-and-wrong route(s) outside the adversarial "
            f"class, budget {CONFIDENT_WRONG_BUDGET} — a confident wrong answer is "
            f"cited in the delegation brief as evidence for the wrong specialist")
    if adversarial_wrong > ADVERSARIAL_CONFIDENT_WRONG_BUDGET:
        failures.append(
            f"adversarial class: {adversarial_wrong} confident-and-wrong, above the "
            f"recorded {ADVERSARIAL_CONFIDENT_WRONG_BUDGET}. This budget measures how "
            f"far deliberate baiting moves the router; it may only fall. Do NOT widen "
            f"a trigger to clear it — that trades a bait row for worse routing "
            f"everywhere else")
    if acc < EVAL_THRESHOLD:
        failures.append(
            f"contract consistency {acc*100:.1f}% below {EVAL_THRESHOLD*100:.0f}% "
            f"— a trigger no longer selects its own agent")
    # `if n and n < MIN` short-circuits at n == 0, so deleting a class ENTIRELY
    # sailed past the floor that exists to stop it being trimmed. Removing two
    # rows failed; removing all twelve passed clean, with the class simply
    # absent from the report — one data edit, no code change, and the whole
    # signal gone. A minimum-rows check that treats "none" as "nothing to check"
    # is checking the wrong thing: zero is the case it most needs to catch.
    adv = classes.get("adversarial", {"n": 0, "hit": 0})
    if classed and adv["n"] < ADVERSARIAL_MIN_ROWS:
        failures.append(
            f"adversarial set has {adv['n']} rows, below the {ADVERSARIAL_MIN_ROWS} "
            f"minimum — deleting the rows the router fails is not the same as "
            f"the router improving, and deleting all of them is not either")
    if classed and para["n"] < PARAPHRASE_MIN_ROWS:
        failures.append(
            f"paraphrase set has {para['n']} rows, below the {PARAPHRASE_MIN_ROWS} "
            f"minimum — the held-out set may not be emptied to dodge its floor")
    if classed and para["hit"] < PARAPHRASE_FLOOR:
        if measured_roster:
            failures.append(
                f"paraphrase confident-correct {para['hit']} below the recorded floor "
                f"{PARAPHRASE_FLOOR} — raise the floor by improving the router and "
                f"re-measuring, never by editing a row")
        else:
            print(f"  · paraphrase confident-correct {para['hit']}, under the "
                  f"recorded floor {PARAPHRASE_FLOOR}. Reported, not gated: this "
                  f"roster is not the one the floor was measured over, and an "
                  f"absolute count falls as a roster grows without the router "
                  f"getting worse. Re-measure against this roster before reading "
                  f"the number as a regression")

    if failures:
        for f in failures:
            print(f"agent-lint --eval: FAIL — {f}", file=sys.stderr)
        return 1

    print(f"agent-lint --eval: OK — contract consistency {acc*100:.1f}% "
          f"({contract['hit']}/{scored}); paraphrase confident-correct "
          f"{para.get('hit', 0)}/{para.get('n', 0)} with "
          f"{para.get('abstain', 0)} abstentions; zero confident-wrong outside "
          f"the adversarial class, {adversarial_wrong} within it (budget "
          f"{ADVERSARIAL_CONFIDENT_WRONG_BUDGET}); {len(rows)} rows")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--route", metavar="TASK", help="rank specialists for TASK")
    ap.add_argument("--lint", action="store_true", help="validate roster frontmatter")
    ap.add_argument("--eval", action="store_true", help="score the golden corpus (fail-closed)")
    ap.add_argument("--dir", metavar="PATH",
                    help="explicit agents directory (e.g. the seed repo's bare "
                         "agents/); default: walk up for .claude/agents/")
    args = ap.parse_args()

    if args.dir:
        adir = Path(args.dir)
        if not adir.is_dir():
            print(f"FATAL: --dir is not a directory: {adir}", file=sys.stderr)
            return 2
    else:
        adir = find_agents_dir()
    if adir is None:
        print("FATAL: no .claude/agents/ or docs/graph/agents/ roster found by walking up from cwd "
              "or the script location (pass --dir to point at one).\n"
              "  If you are rooted in the SEED repo rather than a plant, that is "
              "expected — the seed ships no roster projection of its own, and a "
              "seed-rooted session can spawn no plant specialist. Re-enter rooted "
              "at the plant (delegation.harness-registration).", file=sys.stderr)
        return 2
    try:
        agents = load_agents(adir)
    except LintError as e:
        print(f"FATAL: {e}", file=sys.stderr)
        return 2

    if args.route is not None:
        return cmd_route(agents, args.route)
    if args.eval:
        try:
            return cmd_eval(agents, adir)
        except LintError as e:
            print(f"FATAL: {e}", file=sys.stderr)
            return 2
    return cmd_lint(agents)


if __name__ == "__main__":
    sys.exit(main())
