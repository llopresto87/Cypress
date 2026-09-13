# Tool: working-tree-snapshot

> Project-agnostic, durable capability notes, folded into the seed by the
> harvest protocol. Orientation for a reusable tool — near drop-in: the module
> below is stdlib-only and the whole contract is two functions.

## 0. Identity

- **Category:** testing
- **Name:** working-tree-snapshot
- **Language / runtime:** python3, **stdlib only** (`subprocess`, `shutil`,
  `pathlib`) — deliberately no parser or config dependency, so it is usable by
  the very tests that assert what happens when a dependency is **absent**
- **Stability:** **portable**, near drop-in — the only thing an adopting project
  changes is how the module is imported and how the repository root is derived

## 1. What it does

One shared function that lists — and optionally copies into a throwaway
directory — exactly the files a version-control working tree **currently
contains**: everything in the index **plus** untracked-but-not-ignored files on
disk.

It exists because the obvious listing is the wrong one. A **tracked-only**
listing is invisible-until-it-isn't: a file added by the change under test but
not yet staged is silently missing from the copy, so a gate run inside that copy
fails for a reason that has nothing to do with what is being tested — a missing
module, a missing fixture, a missing config — and the diagnosis points at the
wrong thing entirely.

The timing is the trap. The failure **cannot appear before the commit**: in the
pre-commit run the file *is* on disk for the outer process, so everything passes;
the red only shows up once someone runs the suite from a working tree where those
files are not yet staged. A suite that is green exactly when it is written and
red afterwards is the worst-shaped failure a gate can have.

The centralizing argument matters as much as the listing. This capability earns a
shared home the moment a second caller needs it, because the hazard is **known**
and repeated anyway: a private copier can carry a comment documenting this exact
trap while three sibling copiers repeat the mistake beside it. A hazard that is
documented at one call site and re-committed at others is not a knowledge
problem; it is a **missing shared function**.

## 2. Interface & invocation

Not a CLI — an importable module, and **keyword-only by design** so that no
caller can flip index-versus-worktree semantics with a positional argument.

```python
list_repo_files(*, include_untracked: bool = True,
                repo_root: Path | None = None) -> list[str]

copy_repo_tree(destination: Path, *, include_untracked: bool = True,
               repo_root: Path | None = None) -> None
```

- **Default is the working tree** — index plus untracked-but-present files, with
  ignore rules still honoured. Listing untracked entries as "paths absent from
  the index" means no path is ever returned twice.
- **`include_untracked=False` restricts to the committed state.** It is an
  explicit, justified opt-out, for the one case where **the committed tree is
  itself the subject** of the test — an inventory gate, a "what does the
  repository claim" assertion, a check that exempts in-flight files as
  uncommitted. Fold untracked files in there and the exemption becomes
  unreachable: the gate quietly changes what it asserts while still passing.
  **Write the reason next to the call**, every time.
- `copy_repo_tree` **skips** listed paths that are not regular files on disk — a
  submodule entry, a path staged for deletion, a directory entry — rather than
  raising. The product is a **runnable tree, not a byte-exact mirror of the
  index**, and that is the right trade for a gate that must execute inside it.
- **Name the file so the test runner does not collect it.** A helper living in a
  test directory under a discovery-matching name gets imported as a test module
  and reported as an empty or broken suite.

## 3. Approach / algorithm

One command answers the whole question, and the flag set is the entire design:

```
list the index  +  list paths absent from the index  -  apply ignore rules
```

Expressed against the usual version-control CLI: ask for cached entries **and**
others, with the standard exclusion rules applied, using a NUL separator so
paths containing spaces, quotes, or newlines survive intact.

```python
"""working_tree_snapshot — list and copy the files the working tree really has.

Default scope is the WORKING TREE (index + untracked-but-not-ignored), because
a tracked-only listing silently omits files added by the change under test.
"""
from __future__ import annotations
import shutil
import subprocess
from pathlib import Path

def _toplevel(start: Path | None = None) -> Path:
    """The working tree's own root, asked of the VCS rather than counted out.

    Deriving it by walking a fixed number of parents up from this file encodes
    where the module happens to sit today, so moving the file silently retargets
    every caller at the wrong tree. Asking the VCS is layout-independent and is
    the same answer a human would get.
    """
    here = Path(start) if start else Path(__file__).resolve().parent
    out = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=here,
                         check=True, capture_output=True, text=True).stdout
    return Path(out.strip())


def list_repo_files(*, include_untracked: bool = True,
                    repo_root: Path | None = None) -> list[str]:
    """Repo-relative paths, NUL-separated internally so odd names survive.

    include_untracked=True  -> index + untracked-but-not-ignored (the DEFAULT,
                               i.e. the honest current state of the tree)
    include_untracked=False -> the index only. Pass this ONLY when the committed
                               tree is itself the subject, and say why at the
                               call site.
    """
    root = Path(repo_root) if repo_root else _toplevel()
    cmd = ["git", "ls-files", "-z", "--cached"]
    if include_untracked:
        cmd += ["--others", "--exclude-standard"]
    out = subprocess.run(cmd, cwd=root, check=True,
                         capture_output=True, text=True).stdout
    return [p for p in out.split("\0") if p]


def copy_repo_tree(destination: Path, *, include_untracked: bool = True,
                   repo_root: Path | None = None) -> None:
    """Copy the listed tree into `destination`, preserving relative layout.

    Non-regular entries (submodules, paths staged for deletion, directory
    entries) are SKIPPED, not raised on: the goal is a runnable tree.
    """
    root = Path(repo_root) if repo_root else _toplevel()
    destination = Path(destination)
    for rel in list_repo_files(include_untracked=include_untracked,
                               repo_root=root):
        src = root / rel
        if not src.is_file():
            continue
        dst = destination / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
```

`check=True` is deliberate: a directory that is not a repository **raises**
rather than returning an empty list. A silent empty listing is precisely the
failure mode this module exists to delete, so it must never be reachable.

## 4. Portable vs blueprint

- **Portable (use as-is):** both signatures, keyword-only; the default-to-working-tree
  rule; the NUL-separated listing; the skip-non-regular-files behaviour; the
  raise-on-not-a-repository posture; the no-third-party-dependency constraint;
  and the root resolution, which asks the VCS for its own top level rather than
  counting parent directories, so the module keeps working when it is moved.
- **Fill in per project:** how the module is imported (its directory may need to
  be on the module search path), and whether any caller works on a tree other
  than the one the module itself lives in — that caller passes `repo_root`.
- **Port note:** in another language the same two functions and the same flag
  semantics carry over unchanged; only the subprocess call is rewritten.

## 5. Pitfalls and sharp edges

- **It becomes sensitive to unignored junk.** Any untracked, un-ignored file — a
  scratch script, an editor backup, an operating-system metadata file — now lands
  in the throwaway tree and can be seen by a gate that sweeps files. This is the
  **honest direction** of the trade: the alternative silently omitted real files,
  which is strictly worse than including real junk. **When it bites, the fix is
  an ignore rule, not a revert to tracked-only.** Be careful with the obvious
  version of that fix: ignore rules do not apply to files that are already
  tracked, so an offending file must be untracked as well as ignored.
- **The opt-out is load-bearing where it is used, and silent where it is
  wrong.** `include_untracked=False` changes what a gate asserts without changing
  whether it passes. Both directions are silent failures, which is why the rule
  is *default to the working tree, switch only when the committed tree is the
  subject, and record the reason inline.*
- **It cannot run against an unpacked archive.** It needs the version-control CLI
  on the path and a real repository; there is no degraded mode, on purpose.
- **A helper in a test directory gets collected as a test.** Keep its filename
  outside the runner's discovery pattern.
- **Indirect coverage is not coverage of its own contract.** Callers exercise it
  on every suite run and would fail if it broke badly, but a subtle regression —
  losing the exclusion rules, dropping the untracked flag — can pass through all
  of them. Give it a test at its own interface; a helper everything depends on
  and nothing tests is the exact shape being removed here.

## 6. Tests that cover it

Cover: with a file present but unstaged, the default listing **includes** it and
`include_untracked=False` **excludes** it; an ignored file is listed by neither;
no path is returned twice when a file is both in the index and on disk; a path
containing a space or a newline survives the listing intact; `copy_repo_tree`
skips a non-regular entry instead of raising and produces a tree the real gate
runs inside; running against a non-repository directory raises rather than
returning an empty list; the whole suite is green with the same set of new files
both staged and unstaged — that equivalence is the regression this exists for.

- **How to run the tests:** `<the plant's test command for its implementation>`

## 7. References & neighbours

- **Related tools:** `tool-corpus/testing/ci-runner-local-simulator.md` (the
  reconstructed environment a copied tree is usually executed inside);
  `tool-corpus/testing/failure-signature-triage.md` (triages the results of the
  gate run inside that tree).
- **Sources:** distilled from harvested plant experience; no external URL.

## 8. Changelog

- 2026-09-13 — created from harvested, generalized capability, by docs-librarian.
