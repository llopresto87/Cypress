### Slice 2 — Kernel placement joins the canonical writer

**Tier:** T3. **Entries:** U-04 (closed), U-07 (closed).

**Counterexample.** `install.sh claude-code --symlink` produced `CLAUDE.md` as
a **regular file**, while every sibling was correctly linked — so a seed kernel
change never reached the plant although the flag promised it would.
`place_kernel`'s own header comment claimed "a seed copy by default, or a seed
symlink under `--symlink`"; the code had no branch that could produce the
second. Separately, its sibling branch read `$FORCE -ne 1`, so `--force` — the
one flag a steward reaches for when re-installing over a customized plant — was
also the flag that destroyed the body it replaced.

**Target structure.** `place_kernel` keeps what is specific to the kernel (it
is loaded on every session, so a divergent body is announced in the kernel's
own terms with the backup named as the recovery path) and delegates *placement*
to `place_file`, which already owns the per-mode identical check, the backup,
and link-object replacement.

**Measured result.** Kernel contracts verified by probe — a sentinel appended
to the seed kernel, then reverted:

| Contract | Result |
|---|---|
| K1/K4 one effective body, reached through both harness filenames | ✔ `AGENTS.md → CLAUDE.md` |
| K2 copy mode isolates the plant from later seed changes | ✔ probe not seen |
| K3 symlink mode reflects seed changes without reinstalling | ✔ probe seen |
| K6 kernel byte size unchanged | ✔ 7 564 bytes, file byte-identical |

**U-07 swept across every surface, not just the code.** `--force` now means
exactly "replace non-interactively; suppress the per-file warning; never skip
the backup", and that one sentence is what `install.sh`'s help text,
`place_file`'s comment, `place_kernel`'s sibling branch, `place_docs_skeleton`'s
comment and `INSTALL.md`'s "What gets backed up" all say. Three of those
previously said `--force` overwrites silently or skips the backup. The help
text also promised "without prompting" for a prompt that never existed —
folklore that had since been *implemented* in the kernel branch.
