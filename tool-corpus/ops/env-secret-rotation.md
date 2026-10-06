# Tool: env-secret-rotation

> Project-agnostic capability notes, kept in the seed's tool corpus
> (`tool-corpus/README.md`). Orientation for a reusable tool: the safety rails
> and the subcommand shape are portable; adopt them verbatim.

## 0. Identity

- **Category:** ops
- **Name:** env-secret-rotation
- **Language / runtime:** bash + `openssl` (CSPRNG) + `git` (tracking check)
- **Stability:** **portable**: a self-contained script with no project-specific
  wiring

## 1. What it does

Safely rotates secrets held in a `.env`-style file (`KEY=value` lines). It exists
because hand-editing a secret file is where credentials leak: into shell
history, into a git commit, into a truncated file, into terminal scrollback. This
tool makes rotation atomic, order-preserving, and permission-safe, and it refuses
the unsafe cases outright rather than trusting the operator to remember them.

## 2. Interface & invocation

Per-**secret-class** subcommands, because generated and supplied secrets have
different safe input paths:

```sh
rotate.sh generate <KEY> [--bytes N]   # CSPRNG value made locally, written in place
rotate.sh set      <KEY>               # externally-supplied value read from STDIN ONLY
rotate.sh --check                      # report which keys still hold placeholder defaults
```

- **Inputs:** the target key name; for `set`, the secret value **on stdin only**
  (never argv, never an env var, never echoed). The `.env` file path from config.
- **Outputs:** the rewritten file (same path, in place); for `--check`, a report
  **by key NAME only**, never the value, and a non-zero exit if any placeholder
  remains.
- **Preconditions:** the file exists and is **not tracked by git**; write access.

## 3. Approach / algorithm

- **Generated class (`generate`):** draw a value from a CSPRNG
  (`openssl rand -base64 N` / `-hex`), never from `$RANDOM` or a timestamp.
- **Supplied class (`set`):** read the value from **stdin only** (`read -rs` /
  `cat`). Keeping it off argv keeps it out of the process table and shell
  history; not echoing keeps it out of scrollback.
- **Atomic in-place rewrite:** write the new file to a **temp file** created with
  a `trap` cleanup, rewrite the single `KEY=value` line while copying **every
  other line byte-for-byte** (preserve comments, blanks, ordering), then `mv` the
  temp over the original. A crash mid-write never leaves a half-written secret
  file.
- **Permission floor:** after writing, ensure the file mode is **≥ restrictive**,
  with a floor at `600` (owner-only). Never widen it.
- **Refuse tracked files:** if `git ls-files --error-unmatch <file>` succeeds the
  file is tracked: **refuse and exit non-zero**. Rotating a tracked secret file
  commits the secret; the fix is to untrack it first, not to proceed.
- **`--check` mode:** scan for values still equal to known placeholder/template
  sentinels (e.g. `changeme`, `REPLACE_ME`, empty) and report the **key names**
  that still hold them; exit non-zero if any remain, so CI can gate on it.

## 4. Portable vs blueprint

- **Portable (use as-is):** the whole thing: subcommand split, stdin-only input,
  atomic temp+trap+mv rewrite, permission floor, tracked-file refusal, and
  `--check`. This is genuinely stack-neutral (bash + openssl + git).
- **Fill in:** the file path, the list of placeholder sentinels, and which byte
  length each generated secret class needs.

Portable skeleton:

```bash
#!/usr/bin/env bash
set -euo pipefail
# WARNING: never run this under xtrace (set -x): it echoes secret values.
case "$-" in *x*) echo "refusing: set -x leaks secrets" >&2; exit 3;; esac

ENV_FILE="${ENV_FILE:?set path to the .env-style file}"
# Keys a datastore reads only when it initializes an empty data directory,
# e.g. INIT_ONCE_KEYS="DB_PASSWORD DB_ROOT_PASSWORD" (space-separated).
INIT_ONCE_KEYS="${INIT_ONCE_KEYS:-}"

refuse_generate_if_init_once() {   # its value must reach the database first
  case " $INIT_ONCE_KEYS " in *" $1 "*)
    echo "refusing: $1 is on INIT_ONCE_KEYS. Make a value (openssl rand -base64 32)," >&2
    echo "  change it inside the database first, then write it with: rotate.sh set $1" >&2
    exit 2;;
  esac
}

warn_if_init_once() {
  case " $INIT_ONCE_KEYS " in *" $1 "*)
    echo "warning: $1 is applied only when the datastore initializes an empty" >&2
    echo "  data directory. An initialized one keeps the old credential: change it" >&2
    echo "  inside the database first, or re-initialize the data directory." >&2;;
  esac
}

refuse_if_tracked() {
  if git ls-files --error-unmatch "$ENV_FILE" >/dev/null 2>&1; then
    echo "refusing: $ENV_FILE is git-tracked; untrack it first" >&2; exit 2
  fi
}

rewrite_key() {                        # atomic, order-preserving, in place
  local key="$1" val="$2" tmp
  tmp="$(mktemp "${ENV_FILE}.XXXXXX")"; trap 'rm -f "$tmp"' EXIT
  local found=
  while IFS= read -r line || [ -n "$line" ]; do
    if [[ "$line" == "$key="* ]]; then printf '%s=%s\n' "$key" "$val" >> "$tmp"; found=1
    else printf '%s\n' "$line" >> "$tmp"; fi
  done < "$ENV_FILE"
  [ -n "$found" ] || printf '%s=%s\n' "$key" "$val" >> "$tmp"
  chmod 600 "$tmp"; mv "$tmp" "$ENV_FILE"; trap - EXIT
}

case "${1:-}" in
  generate) refuse_if_tracked; refuse_generate_if_init_once "$2"
            rewrite_key "$2" "$(openssl rand -base64 "${BYTES:-32}")";;
  set)      refuse_if_tracked; IFS= read -rs val; echo; rewrite_key "$2" "$val"
            warn_if_init_once "$2";;
  --check)  bad=0
            while IFS='=' read -r k v; do
              case "$k" in ''|'#'*) continue;; esac   # blank and comment lines
              case "$v" in changeme|REPLACE_ME|""|CHANGE_ME) echo "placeholder: $k"; bad=1;; esac
            done < "$ENV_FILE"; [ "$bad" -eq 0 ];;
  *) echo "usage: rotate.sh {generate <KEY>|set <KEY>|--check}" >&2; exit 1;;
esac
```

## 5. Pitfalls and sharp edges

- **`set -x` leaks every secret.** Under xtrace, the shell echoes the values it
  handles. The tool must **refuse to run** if xtrace is on (checked above), and
  the operator must never wrap it in a traced shell.
- **Value on argv leaks it** into the process table and shell history, which is
  why `set` reads stdin only (`core/method/secrets-posture.md` §1).
- **Non-atomic rewrite risks a truncated secret file** if the process dies
  mid-write; the temp+trap+`mv` pattern is not optional.
- **Rotating a git-tracked file commits the secret**: refuse rather than
  proceed.
- **Rotating a datastore credential in the file does nothing to an
  initialized datastore.** The official database images read their credential
  variables only when they initialize an empty data directory; once it holds a
  database the variables are ignored (`library-corpus/container/postgres.md`,
  `library-corpus/container/mysql.md` and `library-corpus/container/mongo.md`,
  "Environment, first start only"). A new value written here meets a database
  that still expects the old one, and the services that read the file fail to
  connect on their next restart. The order that works on a live data
  directory:
  1. change the credential **inside the database** while the old one still
     works (MySQL `ALTER USER '<user>'@'<host>' IDENTIFIED BY ...`;
     PostgreSQL `ALTER ROLE`, or `psql`'s `\password`, which "encrypts it, and
     sends it to the server as an `ALTER ROLE` command" so the new password
     stays out of the history and the server log);
  2. write the same value into the file with `set` (stdin only);
  3. restart or recreate the services that read it.

  Re-initializing the data directory instead also works, and destroys the
  data. List such keys in `INIT_ONCE_KEYS`. The tool then refuses `generate`
  for them, because a value written before step 1 is one the database does not
  know yet, and `set` prints this warning after it writes.
- **`--check` must report names, not values**, or the safety check itself becomes
  a leak (logs, CI output).

## 6. Tests that cover it

Cover: `generate` produces a high-entropy value and preserves all other lines
byte-for-byte; `generate` on a key listed in `INIT_ONCE_KEYS` refuses and
leaves the file unchanged, `set` on such a key prints the re-initialization
warning, and rotating any other key does neither; `--check` skips comment and
blank lines; `set` reads stdin and never appears on argv; a tracked file is
refused; `--check` exits non-zero iff a placeholder remains and prints only key
names; an interrupted rewrite leaves the original intact.

- **How to run the tests:** `<the plant's test command for shell tooling>`

## 7. References & neighbours

- **Related tools:** `tool-corpus/ops/self-signed-tls-cert.md` (another local
  credential-material generator); `tool-corpus/ops/container-deploy-pipeline.md`
  (consumes the rotated secrets at deploy time);
  `tool-corpus/ops/disposable-test-identity-provisioner.md` (the same CSPRNG,
  print-once, owner-only-permission discipline applied to test identities).
- **Library pages:** `library-corpus/container/postgres.md`,
  `library-corpus/container/mysql.md`, `library-corpus/container/mongo.md`
  (which variables apply only on first initialization).
- **Sources:** distilled from practice; PostgreSQL `psql`
  `\password` (<https://www.postgresql.org/docs/current/app-psql.html>).

## 8. Changelog

- 2026-07-16: created by docs-librarian.
- 2026-10-05: enriched by tool-smith: the
  initialize-once datastore credential pitfall with its rotation order, and an
  `INIT_ONCE_KEYS` warning in the skeleton.
- 2026-10-05: review fixes. `generate` refuses a key on `INIT_ONCE_KEYS`,
  because it wrote a value the database did not know yet, against the page's
  own order; `set` keeps the warning. `--check` skips comment and blank lines,
  which it used to report as placeholders.
