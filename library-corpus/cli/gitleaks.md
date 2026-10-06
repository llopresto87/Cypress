# gitleaks — cli

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a tool, not a record of one
> project's versions. gitleaks arrives as a release binary, a container image or
> a pre-commit hook, not from a project lockfile, so the version that matters is
> the one the hook or pipeline runs: record it with `ingest-library` in the
> project's own page. Several features below arrived inside the v8 line; check
> each against that version.

## What it is
gitleaks (MIT, Go, repository `gitleaks/gitleaks`, home gitleaks.io) finds
secrets such as passwords, API keys and tokens in git history, in files and
directories, and in data piped on stdin. Its engine is a set of regex rules,
each with an optional entropy floor, a keyword pre-filter and allowlists. A
finding carries the matched line, the secret, `RuleID`, `Entropy`, `File`,
`Line`, `Commit`, `Author`, `Email`, `Date` and a `Fingerprint`.

The README is the manual; there is no separate docs site. Maintenance signal:
the maintainer states the project is "feature complete", that new features are
no longer merged and that future releases are security patches only, and names
a successor project. The repository is not archived.

## Install, setup and configuration
- **Channels.** Homebrew, container images (`zricethezav/gitleaks` on Docker
  Hub, `ghcr.io/gitleaks/gitleaks`), release binaries, a source build, a
  pre-commit hook and the `gitleaks-action` GitHub Action. In a container,
  mount the tree to scan and pass `[COMMAND] [OPTIONS] [SOURCE_PATH]`.
- **Config lookup**, first match wins:
  1. `--config`/`-c <file>`;
  2. `GITLEAKS_CONFIG` (a file path);
  3. `GITLEAKS_CONFIG_TOML` (the file content);
  4. `.gitleaks.toml` in the scanned path;
  5. the built-in default config.
- **Replacing versus extending.** A custom config **replaces** the default
  rules unless it says `[extend] useDefault = true`. `[extend] path = "<file>"`
  extends another file instead; the two cannot be combined, and `path` is
  relative to where gitleaks was invoked, not to the base file. Extended rules
  override same-id rules, allowlist arrays are appended (duplicates allowed),
  `disabledRules` drops inherited rules, and extension chains go two deep.
- **Config shape.** `title`, `minVersion` (an older binary warns and may lack
  features), `[extend]`, `[[rules]]` and global `[[allowlists]]`. A rule has
  `id`, `description`, `regex`, `secretGroup` (the capture group the entropy
  check reads), `entropy` (minimum Shannon entropy), `path` (alone, a path-only
  rule; with `regex`, both must match), `keywords`, `tags`, its own
  `[[rules.allowlists]]` and, experimentally, `[[rules.required]]` (composite
  rules with `withinLines`/`withinColumns`). Regexes use Go's engine, which has
  no lookaheads.
- **Allowlist semantics.** A finding is dropped if any allowlist matches.
  Inside one allowlist, `commits`, `paths`, `regexes` and `stopwords` combine
  with OR by default; `condition = "AND"` requires all. `regexTarget` is
  `secret` (default), `match` or `line`. Global allowlists win over rule ones,
  `targetRules` scopes a shared allowlist to named rules, and a listed commit
  is skipped entirely.
- **The default config** is generated, holds a couple of hundred rules, and
  allowlists binary and image extensions, lockfiles and vendored directories
  globally. Its `generic-api-key` rule matches a keyword (access, auth, api,
  credential, creds, key, password, secret, token) near an assignment, quoted
  or unquoted, 10 to 150 characters at entropy 3.5 or more, and allowlists
  placeholders such as `$VAR` and `${VAR}`.
- **Flags and defaults.** `--exit-code` (1); `--redact[=pct]` (100 when given
  bare); `--report-format json|csv|junit|sarif|template` with `--report-path`
  and `--report-template` (Go `text/template` plus sprig); `--baseline-path`;
  `--gitleaks-ignore-path` (`.`); `--ignore-gitleaks-allow`; `--enable-rule`;
  `--max-decode-depth` (0, off); `--max-archive-depth` (0, off);
  `--max-target-megabytes`; `--timeout` (0, none); `--log-level` (info);
  `--verbose`, `--no-banner`, `--no-color`.

## Core API / usage shape
```
gitleaks git [repo]  --log-opts="--all"    # every ref; git log -p, patch by patch
gitleaks git --pre-commit --staged         # what the hook runs
gitleaks dir [path]                        # files, no git (aliases: files, directory)
cat f | gitleaks -v stdin
gitleaks git --redact --report-format sarif --report-path out.sarif
gitleaks git --baseline-path old.json --report-path new.json   # only new findings
```
- **`git` mode** runs `git log -p` and scans the additions in each patch;
  `--log-opts` passes options through (`--all`, `A..B` ranges). No target
  means the current directory.
- **Exit codes.** 0: no leaks. 1: "leaks or error encountered". 126: unknown
  flag. `--exit-code` changes only the code used for leaks.
- **Suppression.** A `gitleaks:allow` comment on the line (disabled by
  `--ignore-gitleaks-allow`), or a **fingerprint** per line in
  `.gitleaksignore` at the repository root (experimental upstream). A history
  fingerprint is `<commit>:<file>:<rule-id>:<line>`. Observed in practice: a
  `dir` scan's fingerprint has no commit part.
- **Baseline.** Any earlier gitleaks report serves as a baseline, redacted
  ones included, so a large old history can be adopted and only new findings
  reported.
- **Encoded secrets and archives.** `--max-decode-depth N` decodes percent,
  hex (32+ chars) and base64 (16+ chars) recursively and tags the finding
  `decoded:<encoding>`; `--max-archive-depth N` opens archives in `dir` and
  `git` mode, joining inner paths with `!`. Both are off by default.

## Idioms & best practices
- **Extend, do not replace.** Start custom configs with
  `[extend] useDefault = true`, then add rules and `disabledRules`.
- **Narrow false positives precisely**: `condition = "AND"` (path and regex
  together), per-rule allowlists, or a shared one with `targetRules`, rather
  than a broad path exclusion.
- **Scan full history with `--redact`.** Raw reports hold the secret in
  `Secret` and `Match`. Observed in practice: keep raw reports out of the
  repository and of build artifacts; untracked raw copies sat one `git add -A`
  away from a push.
- **Suppress only after a ruling.** Observed in practice: add a fingerprint
  only once the owner has ruled the secret rotated or a non-production fake,
  one fingerprint per line with a dated reason. (Upstream shows bare
  fingerprint lines and does not document comment syntax.) Suppressing to
  unblock a release hides a possibly live credential.
- **Rotate first.** Removing the file from HEAD fixes nothing: `git` mode
  still finds it in history and the credential is still valid. Rotate, then
  suppress; history rewriting is not the fix (observed practice).
- **Make the noisy rules quiet, then blocking.** `generic-*` rules match
  identifiers, enum constants and docstrings, and re-report once per commit.
  Observed in practice: unread noise hid real leaks; allowlist (path, regex,
  stopwords) until the output is read, then fail the step on findings.
- **Run the container as the caller** (`--user uid:gid`), or reports land
  root-owned (observed in practice).

## General pitfalls
- **A leak and a crash share exit 1** by default. Set `--exit-code` to another
  value, or gate on the report. Observed in practice: a wrapper that maps any
  non-zero exit to 1 turns the count into a flag; the count lives only in the
  report.
- **A clean scan means no rule matched**, not that no secret exists. Default
  rules read lines, not structure: observed in practice, password hashes in
  JSON exports went unreported until a custom rule was written.
- **Custom-rule blind spots.** Observed in practice: a custom password rule
  that required quoted values missed unquoted dotenv lines. The default
  generic rule accepts both forms.
- **Broad path allowlists hide real secrets.** A path allowlist matching
  `test` also skips real credentials in test tooling. Scans run under different
  configs are not comparable; record which config governed each result.
- **Default allowlists skip** lockfiles, vendored paths and binary files.
- **Fingerprints can move.** Within the v8 line, a fix changed the commit
  reported for secrets that came in through a merge (the introducing commit
  rather than the merge commit), so existing `.gitleaksignore` lines can stop
  matching and findings reappear after an upgrade.
- `useDefault` and `path` in `[extend]` are mutually exclusive; the `extend`
  path resolves from the working directory.
- Decoding and archive traversal are off unless asked for.

## Testing
Upstream gives consumers no test guidance; it ships its own fixtures and
expected reports (JSON, CSV, JUnit, SARIF) under `testdata/`. The pipeline
shapes below were observed in practice:
- fixture-test the gate: a literal credential in a config value is reported,
  a `${VAR}` reference is not (the default generic allowlist covers it), and
  any finding fails the job;
- after a rotation, re-scan as the exit gate and check the finding count, not
  only the exit code;
- when the config changes, re-run on a planted fixture to prove each new rule
  still fires.

## Security defaults
- Without `--redact`, stdout and reports contain the secret. The pre-commit
  hook entries pass `--redact`.
- Scanning needs no network access; decoding and archive scanning are off by
  default.
- `.gitleaksignore` and `gitleaks:allow` are trust points: whoever can edit
  them can silence a finding, so review them like code.
- The scanner's own supply chain: official images on Docker Hub and GHCR,
  binaries on the GitHub releases page.

## Operational behaviour
- No timeout by default; `--max-target-megabytes` skips large files.
- `git` mode cost grows with history size; `--log-opts` ranges and a baseline
  bound it.
- A secret present in several commits yields one finding and one fingerprint
  per commit.
- A config's `minVersion` makes an older binary warn instead of failing.

## Interop
- Pre-commit framework: hook ids `gitleaks`, `gitleaks-docker`,
  `gitleaks-system`; `SKIP=gitleaks` skips it for one commit.
- GitHub Action `gitleaks-action`; SARIF for code-scanning upload, JUnit for CI
  test reports, templates for anything else.
- Complements a file or image scanner that does not read history:
  [`cli/trivy.md`](trivy.md). History operations themselves are on
  [`cli/git.md`](git.md).

## Major lines
One major line, v8, is current; earlier lines are out of scope. Inside v8:
- the `git`, `dir` and `stdin` commands replaced `detect` and `protect`, which
  stay as hidden, deprecated aliases (`detect --source=R` is `git R`;
  `protect --staged` is `git --pre-commit --staged`; `detect --no-git` is
  `dir`; `detect --no-git --pipe` is `stdin`);
- the config grew from one `[rules.allowlist]` and one `[allowlist]` to
  several `[[rules.allowlists]]` and `[[allowlists]]`, `targetRules`,
  `stopwords`, `keywords` and composite rules; old single-table forms still
  load.
Read the release notes for the version in use before relying on a config key.

## Upstream docs
- https://github.com/gitleaks/gitleaks (README is the manual)
- https://github.com/gitleaks/gitleaks/blob/master/config/gitleaks.toml
- https://github.com/gitleaks/gitleaks/blob/master/.pre-commit-hooks.yaml
- https://github.com/gitleaks/gitleaks/releases
