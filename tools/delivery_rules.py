#!/usr/bin/env python3
"""Must-reach and retired sentences (SPEC-0005
MUST_REACH_RULE_IS_IN_EACH_NAMED_ROLE_PROMPT,
FORBIDDEN_SENTENCE_IS_IN_NO_COMPOSED_PROMPT,
FORBIDDEN_SENTENCE_IS_IN_NO_METHOD_SOURCE; SPEC-0001
OPENCODE_CHECK_HOLDS_THE_MUST_REACH_RULES).

A rule that decides what a role does is worth nothing if the role's loaded
prompt lacks it, or if the prompt still carries the sentence it replaced.
MUST_REACH is one table: one row per rule, the sentence that proves the rule is
present, and the roles whose prompt must carry it. FORBIDDEN is the other: one
row per retired sentence, why it was retired, and the roles whose prompt must
not carry it ('any' for every role). Adding either is one row.

    delivery_rules.py AGENTS_DIR     check the projected agent files in a
                                     directory (a plant's .claude/agents or
                                     .opencode/agents); exit 1 on a finding.
    delivery_rules.py --tree ROOT    check the seed's method surface (agents/,
                                     protocols/, skills/, core/, templates/)
                                     for a retired sentence; exit 1 on one.

The seed (tests/test-delivery-rules.sh) and a plant (install.sh --check) read
the same tables, so a plant that recomposes or edits an agent is held to them
too. Matching ignores case and line breaks. Stdlib only.
"""
import os
import re
import sys

# The architect slices the plan from the kinds it set at specify, so it is the
# slicing role; the lead carries a two-line pointer, not the rule.
# (rule id, a sentence of the rule that must appear in the loaded prompt,
#  the roles, by callable name, whose loaded prompt must carry it). A role is
#  found by its callable name on every host: Claude Code keeps the ordering
#  prefix (`04-tester.md`), opencode names the file by the name alone
#  (`tester.md`), so one table serves both projections.)
MUST_REACH = [
    ("test-first.proportionate-checks",
     "Nothing to get wrong, no new test.",
     ("architect", "tester", "reviewer")),
]
# The owner decided on 2026-11-11 that the sentences the 8.5.0 rule replaced
# leave every composed prompt. (retired sentence, why it was retired, the roles
# whose loaded prompt must not carry it, or "any"). Each sentence's wording is
# one no composed prompt and no method node holds after the rewrite.
FORBIDDEN = [
    ("is written only when a failing test asks for it",
     "only logic waits on a failing test; a declarative or presentational "
     "contract is proved by its declared run or review (method.engineering-posture §2)",
     "any"),
    ("the test name names the contract",
     "in a kinds-form spec the §10 Covers cell, not the test's name, links a "
     "test to its contracts (method.engineering-posture §2)",
     "any"),
    ("writes only production files",
     "on the merged path the implementer also writes the test it saw fail "
     "first (delegation.green-self-test)",
     "any"),
    ("the rule loaded above",
     "the always-loaded rule is composed below the charter; name it by "
     "position-free words",
     "any"),
    ("every increment begins with",
     "an increment whose contracts are run or review begins with no failing "
     "test (test-first.proportionate-checks)",
     "any"),
    ("is a separately authorized, RED-gated increment",
     "a run or review contract is authorized by its declared run or review, "
     "not a RED (rule.test-first)",
     "any"),
    ("for each contract in SPEC-0001",
     "test-first runs per increment and each contract by its kind, not a "
     "test per contract (test-first.proportionate-checks)",
     "any"),
]
METHOD_SURFACE = ("agents", "protocols", "skills", "core", "templates")
ORDER_PREFIX = re.compile(r"^\d+-")


def _norm(text):
    return re.sub(r"\s+", " ", text)


def _fold(text):
    return _norm(text).lower()


def missing(prompts):
    """prompts: role -> loaded prompt text. Returns (rule id, role) per miss."""
    out = []
    for rule, sentence, roles in MUST_REACH:
        for role in roles:
            text = prompts.get(role)
            if text is None or _norm(sentence) not in _norm(text):
                out.append((rule, role))
    return out


def forbidden(prompts):
    """prompts: role -> loaded prompt text. Returns (sentence, why, role) per
    retired sentence a role's prompt still carries."""
    out = []
    for sentence, why, roles in FORBIDDEN:
        for role in sorted(prompts):
            if (roles == "any" or role in roles) and _fold(sentence) in _fold(prompts[role]):
                out.append((sentence, why, role))
    return out


def role_files(agents_dir):
    """Callable name -> path for each agent file in the directory; backups and
    underscore files are not agents."""
    out = {}
    names = sorted(os.listdir(agents_dir)) if os.path.isdir(agents_dir) else []
    for fname in names:
        p = os.path.join(agents_dir, fname)
        if fname.endswith(".md") and not fname.startswith("_") and os.path.isfile(p):
            out.setdefault(ORDER_PREFIX.sub("", fname[:-3]), p)
    return out


def check_dir(agents_dir):
    """Findings (strings) for a directory of projected agent files."""
    files = role_files(agents_dir)
    prompts = {role: open(p, encoding="utf-8").read() for role, p in files.items()}
    named = {role for _rule, _sentence, roles in MUST_REACH for role in roles}
    out = [f"{agents_dir}: the loaded prompt of {role} lacks rule {rule}; "
           f"recompose it from its charter (always_loads) or restore the rule's home"
           for rule, role in missing({r: t for r, t in prompts.items() if r in named})]
    out += [f"{agents_dir}: the loaded prompt of {role} carries the retired sentence "
            f"'{sentence}' ({why}); rewrite its home node and recompose"
            for sentence, why, role in forbidden(prompts)]
    return out


def check_tree(root):
    """Findings (strings) for retired sentences in the seed's method surface."""
    out = []
    for top in METHOD_SURFACE:
        for dirpath, dirnames, filenames in os.walk(os.path.join(root, top)):
            dirnames.sort()
            for fname in sorted(filenames):
                path = os.path.join(dirpath, fname)
                try:
                    text = _fold(open(path, encoding="utf-8").read())
                except (UnicodeDecodeError, OSError):
                    continue
                rel = os.path.relpath(path, root)
                out += [f"{rel}: carries the retired sentence '{sentence}' ({why})"
                        for sentence, why, _roles in FORBIDDEN if _fold(sentence) in text]
    return out


def main(argv):
    if len(argv) == 3 and argv[1] == "--tree":
        found = check_tree(argv[2])
    elif len(argv) != 2 or argv[1] in ("-h", "--help"):
        print(__doc__)
        return 0 if len(argv) == 2 else 2
    else:
        found = check_dir(argv[1])
    for f in found:
        print(f)
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
