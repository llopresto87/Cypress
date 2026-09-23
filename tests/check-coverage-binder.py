#!/usr/bin/env python3
"""Every seed-lint check is exercised by a planted violation, or declared here.

`tests/test-seed-lint.sh` opens by claiming "every seed-lint check earns a
planted violation here". It did not. Replacing each `check_*()` call in
`tests/seed-lint.py` with `pass` in turn and re-running that suite showed NINE
of thirteen deletions going unnoticed — among them `check_install_write_sites`,
added the same day, whose three reds had been observed once by hand and were
re-observed by nothing.

Nothing compared the two sets, so each new check silently joined the gap. This
binder is what makes the gap cost something: a check added from now on fails
until it is given a violation in that suite or consciously written into
UNPROTECTED with a reason. UNPROTECTED is shrink-only — an entry that gains a
violation must leave the list, or the list stops meaning anything.
"""
import pathlib
import re
import sys

# No planted violation yet. Each is a real gap, not an exemption on merit.
UNPROTECTED = {
    "check_agents_reference":       "roster/reference equivalence; the reference format resists a one-line mutation",
    "check_skills_reference":       "same shape as check_agents_reference",
    "check_reference_second_views": "needs a mutation per view (summary row, edge table, grouping)",
    "check_charter_vocabulary":     "firing it means pushing the roster past CHARTER_VOCAB_DEBT, which the ratchet also guards",
    "check_plan_ledgers":           "needs a planted plan with a broken ledger, which the fixtures do not carry",
}

# Assertions that live inline in `check()` rather than in a named check_*
# function. They are outside this binder's unit — see the note at the end of
# main() — so the number is recorded and ratcheted rather than left implicit.
INLINE_ASSERTION_DEBT = 81   # measured 2026-09-15; shrink-only

# Exercised by a planted violation in tests/test-seed-lint.sh.
COVERED = {
    "check_body_ceiling", "check_eager_surface", "check_gate_single_home",
    "check_protocol_reference", "check_spec_test_mapping", "check_file_endings",
    "check_canonical_router_blocks", "check_prevents_are_distinct",
    "check_install_write_sites",
    "check_spec_rows_name_their_contract",
    "check_frontmatter_reader_is_one_reader",
    "check_canonical_plant_root_boundary",
    "check_ci_workflow",
    "check_release_workflow",
    "check_published_eager_figures",
    "check_published_body_figures",
    "check_shell_floor_claim_matches_the_shebang",
    "check_frontmatter_is_portable_yaml",
    "check_host_tiers",
    "check_hook_text_restates_no_kernel_rule",
}


def main(root: pathlib.Path) -> int:
    # `--help` used to arrive here as a PATH and raise FileNotFoundError
    # on "--help/tests/seed-lint.py". Same class as the three above.
    if "--help" in sys.argv[1:] or "-h" in sys.argv[1:]:
        print(__doc__ or "")
        return 0

    src = (root / "tests" / "seed-lint.py").read_text(encoding="utf-8")
    suite = (root / "tests" / "test-seed-lint.sh").read_text(encoding="utf-8")

    # COVERED must be what the SUITE says, not what this file asserts. It was a
    # hand-maintained list of strings and this binder never opened the suite at
    # all — so adding a no-op check and declaring it COVERED printed
    # "10 exercised" with nothing planted anywhere. The printed number measured
    # this file agreeing with itself.
    # Leading whitespace is allowed. The anchor used to be column 0, which was
    # not a rule anybody wrote down — it was true only because every case in
    # the suite happened to be top-level. The first case written inside a
    # `case<NAME>()` function indented its marker with the code it labels, the
    # binder did not see it, and the check it named read as unprotected. The
    # marker belongs beside the mutation it annotates; where that sits on the
    # line is not this file's business.
    marked = set(re.findall(r"^\s*# exercises: (check_[a-z0-9_]+)$", suite, re.M))
    if marked != COVERED:
        missing = sorted(COVERED - marked)
        extra = sorted(marked - COVERED)
        msg = []
        if missing:
            msg.append("declared COVERED but no `# exercises:` marker in "
                       "tests/test-seed-lint.sh: " + ", ".join(missing))
        if extra:
            msg.append("marked in tests/test-seed-lint.sh but absent from "
                       "COVERED: " + ", ".join(extra))
        print("check-coverage: FAIL — " + "; ".join(msg)
              + ". A planted violation and its claim must name each other.",
              file=sys.stderr)
        return 1
    defined = set(re.findall(r"^def (check_[a-z0-9_]+)\(", src, re.M))
    called = set(re.findall(r"^\s+(check_[a-z0-9_]+)\(", src, re.M))
    live = defined & called

    if len(live) < 10:
        print(f"check-coverage: FAIL — only {len(live)} live checks found in "
              f"seed-lint.py. The binder has stopped parsing it, so a clean "
              f"result here means nothing.", file=sys.stderr)
        return 1

    missing = live - COVERED - set(UNPROTECTED)
    if missing:
        print("check-coverage: FAIL — seed-lint check(s) with neither a planted "
              "violation in tests/test-seed-lint.sh nor a declared exemption: "
              + ", ".join(sorted(missing))
              + ". Plant a violation, or add it to UNPROTECTED with the reason.",
              file=sys.stderr)
        return 1

    stale = (COVERED | set(UNPROTECTED)) - live
    if stale:
        print("check-coverage: FAIL — this file names check(s) seed-lint no "
              "longer runs: " + ", ".join(sorted(stale))
              + ". A declared exemption for a check that does not exist is a "
                "licence nobody revoked.", file=sys.stderr)
        return 1

    # What this binder's unit actually is, said out loud and held.
    #
    # It counts FUNCTIONS named `check_*`, and seed-lint's assertions are not
    # all in them: the bulk live inline in one function named `check()`, which
    # `^def (check_[a-z0-9_]+)\(` cannot match. So the file's opening claim —
    # every check exercised or declared — was true of the named functions and
    # silent about the rest, and adding an inline assertion inside `check()`
    # changed nothing here. The share is reported rather than hidden, and
    # ratcheted: it may improve as assertions move out of `check()` into named
    # checks, never regress.
    fail_sites = re.findall(r"^(\s*)fail\(", src, re.M)
    total_fails = len(fail_sites)
    named_bodies = re.split(r"^def ", src, flags=re.M)
    in_named = sum(len(re.findall(r"^\s*fail\(", b, re.M))
                   for b in named_bodies if b.startswith("check_"))
    inline = total_fails - in_named
    if inline > INLINE_ASSERTION_DEBT:
        print(f"check-coverage: FAIL — {inline} of {total_fails} seed-lint "
              f"assertions are inline in `check()` rather than in a named "
              f"check_* function, over the recorded {INLINE_ASSERTION_DEBT}. "
              f"This binder's unit is the named function, so an assertion added "
              f"inline is exercised by nothing and invisible here. Move it into "
              f"a named check, or lower the debt deliberately.", file=sys.stderr)
        return 1

    print(f"  check coverage: {len(COVERED)} exercised, {len(UNPROTECTED)} "
          f"declared unprotected, {len(live)} live; {inline} of {total_fails} "
          f"assertions inline in check() and outside this binder's unit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(pathlib.Path(sys.argv[1] if len(sys.argv) > 1
                                       else pathlib.Path(__file__).resolve().parent.parent)))
