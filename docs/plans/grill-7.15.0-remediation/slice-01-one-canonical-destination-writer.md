### Slice 1 — One canonical destination writer

**Tier:** T3. **Ledger entries:** U-01, U-02 (closed); U-04 hooks half, U-08,
U-09, U-10, U-11 (closed alongside); U-03 unblocked.

**Counterexample that justified it.** Install; append one comment to
`.claude/route-hook.py`; reinstall. The edit is gone, no `.bak` exists, and
`tools/graft-audit.py` reports *"zero backup files — nothing was overwritten"*
and *"clean — no plant knowledge overwritten, no customization buried."* The
audit's verdict was inverted from reality, because the defect bypassed the
mechanism the audit observes. Separately: symlink that destination at a file
outside the target and the install overwrites the outside file.

**Existing structure and the contradiction.** `place_file` already implemented
the correct policy for ~15 destinations. Seventeen further destinations reached
the filesystem directly through four idioms — `cp` (11), `cat >` (1), `sed >`
(1), Python `open(…,"w")` (3) — expanding to **86 files** in an
`install.sh all`. The installer had two placement paths and claimed the first
one's safety properties for both.

**Target structure.** Three named placement operations, one writer beneath
them:

| Operation | For | Backup | Link mode |
|---|---|---|---|
| `place_file` | a seed file with a plant twin | yes | honours `--symlink` |
| `place_generated` | content generated per target | yes | always a real file (no seed original to link to) |
| `place_if_missing` | add-if-missing, plant-owned thereafter | n/a (never replaces) | always a real file |
| `place_state` | the installer's own derived stamp | **no** (see below) | always a real file |

Generated content is rendered into one per-run `STAGE` directory reclaimed by a
single `trap`, then placed — so generation completes before replacement (M6)
and a failed generation cannot leave a partial destination.

**Measured result.**

| Invariant | Before | After |
|---|---|---|
| M7 destinations replacing a plant edit with no recoverable backup | **86** | **0** |
| M2 destinations written *through* a symlink to a file outside the target | **86** | **0** |
| M3 backups on an identical re-run | 0 | **0** (preserved) |
| M9 non-link copies under `--symlink` outside the exception list | 92 | **0** |
| M8 backups `graft-audit.py` cannot classify | n/a (none produced) | **0** |

**Recorded exceptions, with reasons.** `place_state` is the one M7 exception:
the stamp carries a fresh `installed_at` every run, so it is never
byte-identical and a backup policy would leave one `.bak` per install for ever
— the exact churn `place_file`'s own comment warns buries the audit signal —
and the next stamp is *derived* from this one rather than authored, so a backup
carries no recovery value. It is still replaced atomically (staged, copied to a
sibling, renamed) and still symlink-safe, because `rename(2)` replaces the
destination *name*. `place_generated` and `place_if_missing` are the M9
exceptions: neither has a seed original a link could point at.

**Obsolete structure removed.** The second placement path is gone, not guarded
(doctrine P4). `place_kernel` no longer hand-rolls placement; the five
`|| cp` add-if-missing idioms are one named operation; `--check`'s private
`mktemp -d` is gone in favour of the run's single temp owner, so there is one
temp lifecycle rather than two.

**Characterizing test, red first.** `tests/test-install-placement.sh`
discovers the destination set from a real install rather than listing it — a
hardcoded list is how this class survived, since the installer grew
destinations no list was updated to cover. Observed red at 86/86/92 before the
repair; green after. Reverting one single `cp` turns it red naming exactly
`.claude/route-hook.py`, so it pins the class rather than the instance.

**Closed alongside, each with its own counterexample:**

- **U-08** — the Codex path was substituted through a `sed` *replacement*, where
  `&` expands to the whole match. Independently reproduced: a target named
  `a&b` produced `…/a/abs/path/to/projectb/…` in all 13 `[[skills.config]]`
  entries, silently, exit 0. Now substituted literally in Python with TOML
  escaping. Verified across `a b`, `a&b`, `a[b]`, `a#b`, `a'b`: all five
  substitute the literal path and parse as valid TOML.
- **U-09** — `--check` discarded the generator's stderr, so a generation that
  *crashed* was reported as "Copilot views are STALE": a drift verdict for a
  broken installer. Failure and drift are now distinct, and the error is shown.
- **U-10** — `graft-audit.py --help` exited 2 with "unknown option"; now prints
  its own docstring and exits 0.
- **U-11** — promoted from *tentative* to *verified*, then fixed. The walk
  ascended seven levels from both cwd and the script directory and executed the
  first `graph-lint.py` found; from a git repo at `outer/child` it resolved to
  `outer/docs/graph/graph-lint.py`, an ancestor-controlled script, on every
  prompt. Now bounded at the first `.git` or `.cypress/` — checked *after* the
  candidate test, so a plant whose linter sits at its own root is still found.
  Verified both directions: escape blocked, real plant still resolves.
