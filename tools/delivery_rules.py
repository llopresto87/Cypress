#!/usr/bin/env python3
"""Must-reach rules (SPEC-0001 MUST_REACH_RULE_IS_IN_EACH_NAMED_ROLE_PROMPT).

A rule that decides what a role does is worth nothing if the role's loaded
prompt lacks it. MUST_REACH is the table: one row per rule, the sentence that
proves the rule is present, and the roles whose prompt must carry it. Adding a
rule that must always reach a role is one row.

    delivery_rules.py AGENTS_DIR     check the projected agent files in a
                                     directory (a plant's .claude/agents or
                                     .opencode/agents); exit 1 on a miss.

The seed (tests/seed-lint.py) and a plant (install.sh --check) read the same
table, so a plant that recomposes or edits an agent is held to it too.
Stdlib only.
"""
import os
import re
import sys

# The architect slices the plan from the kinds it set at specify, so it is the
# slicing role; the lead carries a two-line pointer, not the rule.
# (rule id, a sentence of the rule that must appear in the loaded prompt,
#  role -> the agent file that carries that role's loaded prompt)
MUST_REACH = [
    ("test-first.proportionate-checks",
     "Nothing to get wrong, no new test.",
     {"architect": "01-architect.md", "tester": "04-tester.md",
      "reviewer": "03-reviewer.md"}),
]


def _norm(text):
    return re.sub(r"\s+", " ", text)


def missing(prompts):
    """prompts: role -> loaded prompt text. Returns (rule id, role) per miss."""
    out = []
    for rule, sentence, roles in MUST_REACH:
        for role in roles:
            text = prompts.get(role)
            if text is None or _norm(sentence) not in _norm(text):
                out.append((rule, role))
    return out


def check_dir(agents_dir):
    """Findings (strings) for a directory of projected agent files."""
    prompts = {}
    for _rule, _sentence, roles in MUST_REACH:
        for role, fname in roles.items():
            p = os.path.join(agents_dir, fname)
            if os.path.isfile(p):
                prompts[role] = open(p, encoding="utf-8").read()
    return [f"{agents_dir}: the loaded prompt of {role} lacks rule {rule}; "
            f"recompose it from its charter (always_loads) or restore the rule's home"
            for rule, role in missing(prompts)]


def main(argv):
    if len(argv) != 2 or argv[1] in ("-h", "--help"):
        print(__doc__)
        return 0 if len(argv) == 2 else 2
    found = check_dir(argv[1])
    for f in found:
        print(f)
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
