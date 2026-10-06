# git — cli

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a tool, not a record of one
> project's versions. git arrives from the host's package manager or a base
> image, so the version that matters is the one on the machine that runs the
> command (a developer workstation and a CI agent often differ): record it with
> `ingest-library` in the project's own page and check anything load-bearing
> against that version's manual.

## What it is
git is the distributed version-control system, and it is two tools in one. The
**porcelain** (`status`, `checkout`, `switch`, `commit`, `pull`, `merge`) is
built for a person at a working tree and freely touches HEAD, the index and the
files. The **plumbing** (`rev-parse`, `ls-tree`, `diff-tree`, `cat-file`,
`hash-object`, `update-index`, `write-tree`, `commit-tree`, `merge-base`) reads
and writes objects and refs one small step at a time, with stable output meant
for scripts. git is licensed under the GPL, version 2 only.

This page covers git as something a script or an agent drives: how to inspect a
repository without changing it, how to fetch and build a commit while touching
as little as possible, and the pitfalls that make a careful script wrong. It
does not cover any project's branching model; that is the project's own
decision.

## Install, setup and configuration
- git comes from the operating system's package manager, the platform's
  developer tools, or the base image. `git --version` on the machine that runs
  the script is the version that counts; a distribution's long-term release
  can trail the current manual by many releases.
- **Configuration scopes**, lowest to highest precedence: *system*
  (`$(prefix)/etc/gitconfig`), *global* (`~/.gitconfig` or
  `$XDG_CONFIG_HOME/git/config`), *local* (`$GIT_DIR/config`), *worktree*
  (`$GIT_DIR/config.worktree`), and *command* (`-c key=value`, or the
  `GIT_CONFIG_COUNT`, `GIT_CONFIG_KEY_<n>` and `GIT_CONFIG_VALUE_<n>`
  environment variables). The later scope wins for a single-valued key.
- **Protected configuration** is the system, global and command scopes. Some
  keys, `safe.directory` among them, are honoured only there, because a
  repository's own config is controlled by whoever wrote the repository.
- `GIT_CONFIG_GLOBAL` and `GIT_CONFIG_SYSTEM` point those scopes at other
  files; `GIT_CONFIG_NOSYSTEM=1` skips the system file.
- `include.*` and `includeIf.*` pull in other files. Includes are followed by
  default when git reads all scopes, and not followed when one file is named
  with `--file`.

## Core API / usage shape
```
# Inspect without touching HEAD, the index or the working tree
git rev-parse <rev>                         # resolve a name to an object id
git ls-tree [-r] [-z] <tree-ish> [path]     # list a tree; mode 120000 is a symlink
git show <rev>:<path>                       # read one file as of a commit
git cat-file -p <object>                    # print any object
git diff-tree -r [-z] <tree-ish> <tree-ish> # compare two trees, nothing else
git log -1 --format=%cd <rev>               # committer date of a commit
git log -1 --format=%ct <rev>               # committer date as epoch seconds (UTC)
git merge-base --is-ancestor <a> <b>        # exit 0 if a is an ancestor of b, 1 if not

# Fetch while writing as little as possible
git fetch --no-tags --no-recurse-submodules [--depth=1] [--refmap=] <remote> <ref>
                                            # result lands in FETCH_HEAD

# Build a commit without the working tree
git read-tree <tree-ish>                    # no -u: loads the index, leaves files alone
git hash-object -w --no-filters --stdin     # write a blob exactly as given
git update-index -z --index-info            # stage "mode SP sha SP stage TAB path" lines
                                            # (also takes ls-tree's "mode SP type SP sha TAB path")
git write-tree                              # tree from the index; the index must be fully merged
git commit-tree -p <parent> <tree>          # commit object; message on stdin, or -m (repeatable,
                                            # one paragraph each) or -F

# Read a config file as data
git config --file <path> --no-includes --null --name-only --list

# Per-command configuration and environment
git -c <key>=<value> <command>              # command-scope config, this call only
GIT_OPTIONAL_LOCKS=0                        # skip optional index refreshes (status and kin)
GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1   # hermetic: ignore user and system config
GIT_AUTHOR_NAME / _EMAIL, GIT_COMMITTER_NAME / _EMAIL   # identity for one command
GIT_TERMINAL_PROMPT=0                       # never prompt on the terminal; fail instead
GIT_ASKPASS=<program>                       # run with the prompt as argument; password read from its stdout
GIT_SSH_COMMAND='ssh -i <key> ...'          # ssh command for fetch/push; shell-interpreted, overrides GIT_SSH
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
- **A read-only peek at another branch without checking it out** (git 2.36 or
  newer; see the `core.fsmonitor` pitfall for older releases):
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
- **Read an untrusted config file as data, never through git's normal
  lookup.** `git config --file <path> --no-includes --null --name-only --list`
  lists the keys without following includes, NUL-separated so a hostile value
  cannot forge a line. Newer 2.x releases spell the same call `git config list`;
  `--list` still works.
- **Give a script credentials for one command.** `GIT_ASKPASS` names a program
  that prints the secret, and `GIT_SSH_COMMAND` names the ssh key and options.
  `-c http.<url>.extraHeader="Authorization: Bearer ..."` also works per
  command but puts the token in argv, where `ps` shows it; the
  `GIT_CONFIG_COUNT`/`KEY`/`VALUE` variables set the same key without argv.
  Set `GIT_TERMINAL_PROMPT=0` so a missing credential fails instead of
  waiting for input.
- **Check history completeness per ref, not per repository** (see the shallow
  pitfalls): for each line of `.git/shallow`, `git merge-base --is-ancestor
  <that commit> <ref>` exiting 0 means the ref's history is cut at that commit.
- **Enforce policy on the server, not in client hooks.** Upstream's FAQ says
  the only places a rule can be enforced are the remote (a pre-receive hook)
  or CI; a client hook is the user's to skip.

## General pitfalls
- **`-c core.fsmonitor=false` needs git 2.36 or newer.** The key once held only
  a hook path; the boolean form came later. Releases before 2.36 read `true`
  or `false` as the path of a hook program to run, so on them the flag runs a
  program named `false` instead of turning the monitor off. Check
  `git --version` before relying on the peek above against an untrusted
  repository.
- **A fetch with a remote name also writes remote-tracking refs.** When the
  remote has a configured fetch refspec (every normal clone does), fetching a
  named ref also creates or moves `refs/remotes/<remote>/<ref>`. To write only
  `FETCH_HEAD`, pass an empty `--refmap=` or fetch from a URL instead of the
  remote's name.
- **Each fetch overwrites `FETCH_HEAD`** unless `--append` is given. Read it
  before the next fetch in the same repository.
- **A depth-1 fetch of one ref can truncate another ref's history.** The shallow
  boundary is recorded per commit in `.git/shallow`, not per fetch. If a shallow
  fetch lands on a commit that a fully fetched branch also reaches, that commit
  becomes a boundary and `git log` on the other branch stops there, even though
  the parent objects are still in the object store (observed in practice; the
  manual describes the shallow file but not this interaction). Read anything
  that depends on full history (dates, ancestry, blame) *before* any shallow
  fetch in the same repository.
- **A shallow fetch skips tags, and `--unshallow` is only as deep as the
  source.** `--depth` does not fetch tags for the deepened commits. From a
  shallow source, `--unshallow` fetches only as much history as the source has.
- **`rev-parse --is-shallow-repository` answers for the whole repository.** It
  turns true the moment any ref was ever fetched shallow, including one that
  shares nothing with the branch in question. It cannot tell whether a given
  branch's history is complete; use the per-ref ancestry check above.
- **`--date=format:` is not UTC.** It renders the commit's own recorded offset.
  For a UTC date, set `TZ=UTC` in the environment and use
  `--date=format-local:...`; `format-local` renders in the local zone, which is
  then UTC. Or read `%ct` (or `--date=raw`), epoch seconds that are always
  UTC, and format them yourself.
- **`safe.directory` is honored only from protected configuration** (system,
  global or command scope), never from a repository's own local config, so a
  hostile repository cannot vouch for itself. A `-c safe.directory=<path>` on
  the command line is therefore a legitimate, deliberate override. Use the exact
  path rather than `*`.
- **Repository config and hooks run code.** `core.hooksPath`, `core.fsmonitor`,
  filter drivers and aliases in a repository you did not create can execute
  programs during ordinary commands. Before operating on an untrusted clone,
  disable hooks and the monitor per command with `-c` as in the peek above.
- **A CI checkout can leave the job's token in git config.** A checkout step
  that persists credentials (on by default in some CI checkout actions) writes
  the token into the repository's local config, for example as an
  `http.<url>.extraHeader`, or into a file that config includes. Every later
  fetch or push in the job then authenticates silently, and anything that can
  read the config can read the token. Turn persistence off when later steps do
  not need it.
- **An exit code does not separate "absent" from "broken".** The
  `cat-file` manual promises only a non-zero status; observed in practice,
  `git cat-file -e <rev>:<path>` exits 128 both for a missing path and for a
  mangled revision. The `rev-parse` manual adds that `--verify` accepts a
  well-formed hash whose object does not exist unless `^{commit}` is added. A probe that reads any failure as "absent"
  therefore reports a broken probe as a real negative. Verify the revision on
  its own first (`git rev-parse --verify -q <rev>^{commit}`), then the path;
  pass paths as separate arguments after `--` where the command takes them, and
  run one positive control. In zsh, write `${ref}:path`, not `$ref:path`: a
  colon after a parameter name starts a modifier (`:t`, `:h`, `:u`), and a
  mangled ref was observed even inside double quotes.
- **Plumbing output is stable; porcelain output is not.** Parse `--porcelain`,
  `-z` or plumbing output in scripts. Human-facing output changes between
  releases and with the user's configuration (color, pager, locale).

## Testing
- **Run tests against git hermetically.** Throwaway repositories in a scratch
  directory, with `GIT_CONFIG_GLOBAL=/dev/null` and `GIT_CONFIG_NOSYSTEM=1`, so a
  developer's aliases, hooks path or default branch cannot change the result.
  Set `GIT_AUTHOR_*`, `GIT_COMMITTER_*` and their `_DATE` variables so commit
  ids are reproducible.
- Pass `-b <branch>` to `git init` (or set `init.defaultBranch` with `-c`).
  Never assume the default branch name, which depends on the release and the
  configuration.
- Observed in practice: local read-only plumbing runs with no `HOME` and an
  empty environment (`env -i`), given `-C <repo>` and `-c` for any setting,
  which makes it a clean test harness. The manual does not state this.
- Assert on plumbing output and exit codes (`merge-base --is-ancestor` gives 0
  or 1), never on porcelain text.

## Security defaults
- **Ownership check.** git refuses to read the config of, or run hooks in, a
  repository owned by another user unless the path is listed in
  `safe.directory` in protected configuration. `*` turns the check off
  entirely.
- **Protocol policy.** By default `http`, `https`, `git` and `ssh` are always
  allowed, `ext` is never allowed, and every other protocol, `file` included,
  is allowed only when the user asked for it directly
  (`GIT_PROTOCOL_FROM_USER`). `protocol.<name>.allow` changes one.
- **Object checks are off.** `transfer.fsckObjects` defaults to false; set it
  (or `fetch.fsckObjects`) to reject malformed objects and malicious
  `.gitmodules` content on fetch from an untrusted source.
- **Credentials in URLs.** `transfer.credentialsInUrl` set to `warn` or `die`
  catches a plaintext password in a `remote.<name>.url` (not in `pushurl`).
- **Repository config is code.** See the hooks, fsmonitor and CI-token
  pitfalls above.

## Operational behaviour
- git runs as short-lived processes with no daemon by default. The daemons it
  ships are opt-in: `git daemon`, the credential-cache helper's daemon, and the
  built-in filesystem monitor (Windows and macOS only).
- **Locks.** Commands that write the index or a ref take a lock; an optional
  index refresh by a reader can collide with a writer. `GIT_OPTIONAL_LOCKS=0`
  keeps background readers out of the way.
- **Automatic housekeeping.** Some porcelain commands run `git gc --auto` (or
  `git maintenance run --auto`) when loose objects pass `gc.auto` (default
  6700) or packs pass `gc.autoPackLimit`, and by default detach it into the
  background (`gc.autoDetach`). Set `gc.auto=0` where background repacking
  must not run, such as a repository another process is reading.
- **Shallow and partial clones** trade history for speed; anything that walks
  history (dates, blame, ancestry) is only as good as what was fetched.

## Interop
- **CI checkout steps** decide depth, tags and credential persistence; a
  default shallow checkout breaks anything that reads full history or tags.
- **Credential helpers** (`credential.helper`) store and supply secrets for
  HTTPS; `GIT_ASKPASS` and `core.askPass` serve a script.
- **SSH** is reached through `GIT_SSH_COMMAND`, `core.sshCommand` or
  `GIT_SSH`, interpreted according to `ssh.variant`.
- **Forges** generally name the default branch `main` on repositories they
  create, while git's own default stays `master` until 3.0 unless
  `init.defaultBranch` says otherwise.

## Major lines

### 2.x line
- Feature releases are numbered `2.<n>.0`, and maintenance releases raise the
  third number. Minor releases are not meant to break backward compatibility
  unless a security fix forces it.
- `core.fsmonitor` accepts a boolean only from 2.36; see the pitfall.
- Newer 2.x releases add subcommand forms of `git config` (`list`, `get`,
  `set`) that replace `--list`, `--get` and friends; the old options keep
  working.

### 3.0 line (announced, not released)
- Upstream's breaking-changes document lists, for 3.0: SHA-256 as the default
  object format for new repositories, `reftable` as the default ref storage,
  `main` as the default branch name for new repositories, and Rust as a
  required build dependency.
- Upstream plans to declare the last 2.x release a long-term support release.
- A script that writes into `.git/refs` directly, assumes 40-hex object ids, or
  assumes `master` breaks here; reach refs through `update-ref` and
  `for-each-ref`, and read object ids at their actual length.

## Upstream docs
- Reference manual (every command): https://git-scm.com/docs
- `git fetch` (depth, refmap, FETCH_HEAD): https://git-scm.com/docs/git-fetch
- `git config` (scopes, protected configuration, `safe.directory`,
  `core.hooksPath`, `core.fsmonitor`, `protocol.allow`):
  https://git-scm.com/docs/git-config
- `git` (global options; environment variables incl. `GIT_OPTIONAL_LOCKS`,
  `GIT_INDEX_FILE`, `GIT_ASKPASS`, `GIT_SSH_COMMAND`):
  https://git-scm.com/docs/git
- `git log` (date formats): https://git-scm.com/docs/git-log
- `git cat-file`, `git rev-parse` (existence checks, `^{commit}`):
  https://git-scm.com/docs/git-cat-file, https://git-scm.com/docs/git-rev-parse
- `git update-index`, `git write-tree`, `git commit-tree` (building a commit):
  https://git-scm.com/docs/git-update-index
- Repository layout (the `shallow` file): https://git-scm.com/docs/gitrepository-layout
- FAQ (hooks and policy, credentials): https://git-scm.com/docs/gitfaq
- Breaking changes planned for 3.0: https://git-scm.com/docs/BreakingChanges
- Source: https://github.com/git/git
