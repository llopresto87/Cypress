# git — cli

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a tool, NOT a version-pinned page. git
> arrives from the host's package manager or a base image, so the version that
> matters is the one on the machine that runs the command (a developer
> workstation and a CI agent often differ): record it with `ingest-library` in
> the project's own page and check anything load-bearing against that version's
> manual.

## What it is
git is the distributed version-control system, and it is two tools in one. The
**porcelain** (`status`, `checkout`, `switch`, `commit`, `pull`, `merge`) is
built for a person at a working tree and freely touches HEAD, the index and the
files. The **plumbing** (`rev-parse`, `ls-tree`, `diff-tree`, `cat-file`,
`hash-object`, `update-index`, `write-tree`, `commit-tree`, `merge-base`) reads
and writes objects and refs one small step at a time, with stable output meant
for scripts.

This page covers git as something a script or an agent drives: how to inspect a
repository without changing it, how to fetch and build a commit while touching
as little as possible, and the pitfalls that make a careful script wrong. It
does not cover any project's branching model; that is the project's own
decision.

## Core API / usage shape
```
# Inspect without touching HEAD, the index or the working tree
git rev-parse <rev>                         # resolve a name to an object id
git ls-tree [-r] [-z] <tree-ish> [path]     # list a tree; mode 120000 is a symlink
git show <rev>:<path>                       # read one file as of a commit
git cat-file -p <object>                    # print any object
git diff-tree -r [-z] <tree-ish> <tree-ish> # compare two trees, nothing else
git log -1 --format=%cd <rev>               # committer date of a commit
git merge-base --is-ancestor <a> <b>        # exit 0 if a is an ancestor of b, 1 if not

# Fetch while writing as little as possible
git fetch --no-tags --no-recurse-submodules [--depth=1] [--refmap=] <remote> <ref>
                                            # result lands in FETCH_HEAD

# Build a commit without the working tree
git read-tree <tree-ish>                    # no -u: loads the index, leaves files alone
git hash-object -w --no-filters --stdin     # write a blob exactly as given
git update-index -z --index-info            # stage "mode SP sha SP stage TAB path" lines
git write-tree                              # tree from the index
git commit-tree -p <parent> <tree>          # commit object; message on stdin

# Per-command configuration and environment
git -c <key>=<value> <command>              # command-scope config, this call only
GIT_OPTIONAL_LOCKS=0                        # skip optional index refreshes (status and kin)
GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1   # hermetic: ignore user and system config
GIT_AUTHOR_NAME / _EMAIL, GIT_COMMITTER_NAME / _EMAIL   # identity for one command
```

## Idioms & best practices
- **Inspection never writes, above all on a checkout someone else is using.** A
  shared or live working tree (a colleague's, a running service's, another
  agent's) belongs to whoever is working in it. To look at another branch, read
  it where it lives: `git show <rev>:<path>`, `git diff <rev1> <rev2> -- <path>`,
  `git log <rev>`, `git ls-tree <rev>`. Never `checkout` or `switch` to look,
  never `stash` to make room, and never `pull` to refresh, because each of those
  changes HEAD, the index or the files under the owner's feet.
- **Even read-only porcelain can write the index.** `git status` refreshes cached
  file metadata in the index when it can take the lock, which is a write, and it
  can collide with another process holding that lock. Set `GIT_OPTIONAL_LOCKS=0`
  for inspection on a tree you do not own, or use plumbing that never takes the
  lock.
- **A read-only peek at another branch without checking it out:**
  ```sh
  git -c core.hooksPath=/dev/null -c core.fsmonitor=false \
      fetch --no-tags --no-recurse-submodules --refmap= --depth=1 <remote> <ref>
  git -c core.hooksPath=/dev/null -c core.fsmonitor=false \
      diff-tree -r <target-tip> FETCH_HEAD
  ```
  Disabling hooks and the filesystem monitor per command keeps a repository's
  own configuration from running code during the peek. The fetch writes
  `FETCH_HEAD` and never a local branch. Read the depth pitfall below before
  using `--depth=1` in a repository whose other refs you also depend on.
- **Build a commit without touching the working tree** when a script must
  produce exactly one commit and must not disturb the files: `read-tree` the
  parent's tree (without `-u`, which would update the files), `hash-object -w
  --no-filters` each new blob (so no attribute-driven filter such as end-of-line
  conversion, `ident` or `working-tree-encoding` rewrites the bytes),
  `update-index --index-info` to stage them, `write-tree`, then `commit-tree -p
  <parent> <tree>`. Point `GIT_INDEX_FILE` at a temporary index file so the
  repository's real index is not replaced either. Set the author and committer
  through the `GIT_AUTHOR_*` and `GIT_COMMITTER_*` variables, which override
  configured identity for that one command.
- **Push only what was built.** A scripted push should name the ref explicitly
  and add `--no-follow-tags --recurse-submodules=no`, so configuration cannot
  make it push tags or submodules it never meant to.
- **Global options go before the subcommand.** `git --no-replace-objects
  --literal-pathspecs <command> ...`: replace refs cannot substitute objects,
  and a path is taken literally rather than as a pattern.
- **Run tests against git hermetically.** Throwaway repositories in a scratch
  directory, with `GIT_CONFIG_GLOBAL=/dev/null` and `GIT_CONFIG_NOSYSTEM=1`, so a
  developer's aliases, hooks path or default branch cannot change the result.
- **Check history completeness per ref, not per repository** (see the shallow
  pitfalls): for each line of `.git/shallow`, `git merge-base --is-ancestor
  <that commit> <ref>` exiting 0 means the ref's history is cut at that commit.

## General pitfalls
- **A fetch with a remote name also writes remote-tracking refs.** When the
  remote has a configured fetch refspec (every normal clone does), fetching a
  named ref also creates or moves `refs/remotes/<remote>/<ref>`. To write only
  `FETCH_HEAD`, pass an empty `--refmap=` or fetch from a URL instead of the
  remote's name.
- **A depth-1 fetch of one ref can truncate another ref's history.** The shallow
  boundary is recorded per commit in `.git/shallow`, not per fetch. If a shallow
  fetch lands on a commit that a fully fetched branch also reaches, that commit
  becomes a boundary and `git log` on the other branch stops there, even though
  the parent objects are still in the object store (observed). Read anything
  that depends on full history (dates, ancestry, blame) *before* any shallow
  fetch in the same repository.
- **`rev-parse --is-shallow-repository` answers for the whole repository.** It
  turns true the moment any ref was ever fetched shallow, including one that
  shares nothing with the branch in question. It cannot tell whether a given
  branch's history is complete; use the per-ref ancestry check above.
- **`--date=format:` is not UTC.** It renders the commit's own recorded offset.
  For a UTC date, set `TZ=UTC` in the environment and use
  `--date=format-local:...`; `format-local` renders in the local zone, which is
  then UTC.
- **`safe.directory` is honored only from protected configuration** (system,
  global or command scope), never from a repository's own local config, so a
  hostile repository cannot vouch for itself. A `-c safe.directory=<path>` on
  the command line is therefore a legitimate, deliberate override. Use the exact
  path rather than `*`.
- **Repository config and hooks run code.** `core.hooksPath`, `core.fsmonitor`,
  filter drivers and aliases in a repository you did not create can execute
  programs during ordinary commands. Before operating on an untrusted clone,
  disable hooks and the monitor per command with `-c` as in the peek above.
- **Plumbing output is stable; porcelain output is not.** Parse `--porcelain`,
  `-z` or plumbing output in scripts. Human-facing output changes between
  releases and with the user's configuration (color, pager, locale).

## Upstream docs
- Reference manual (every command): https://git-scm.com/docs
- `git fetch` (depth, refmap, FETCH_HEAD): https://git-scm.com/docs/git-fetch
- `git config` (scopes, `safe.directory`, `core.hooksPath`, `core.fsmonitor`):
  https://git-scm.com/docs/git-config
- `git` (global options; environment variables incl. `GIT_OPTIONAL_LOCKS`,
  `GIT_INDEX_FILE`):
  https://git-scm.com/docs/git
- `git log` (date formats): https://git-scm.com/docs/git-log
- Repository layout (the `shallow` file): https://git-scm.com/docs/gitrepository-layout
- Source: https://github.com/git/git
