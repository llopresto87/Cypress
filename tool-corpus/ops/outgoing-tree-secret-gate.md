# Tool: outgoing-tree-secret-gate

> Project-agnostic capability notes, kept in the seed's tool corpus
> (`tool-corpus/README.md`). Orientation for a reusable tool, a blueprint: the
> range walk, the per-blob cache and the three rule classes are stack-neutral;
> the encrypted-container marker, the key vocabulary and the reference syntax
> that counts as "not a literal" are what each project fills in.

## 0. Identity

- **Category:** ops
- **Name:** outgoing-tree-secret-gate
- **Language / runtime:** a version-control hook. The reference shape is bash
  (associative arrays need bash 4 or later) over the plain `git` CLI; any
  language that can read ref lines on stdin and call `git` ports it unchanged.
- **Stability:** **blueprint**: the publication gate is proven in practice by
  hook-level tests over synthetic repositories; the staging-gate section (§3.2)
  is lower confidence and untested where it was observed.

## 1. What it does

Two gates on the two moments a secret can leave a working copy, both failing
closed (`core/method/secrets-posture.md` names the pair):

- **Publication gate (the thorough one).** Runs before a push and inspects the
  **full tree of every commit in the outgoing range**, not the diff and not the
  working tree. A plaintext secret that reached history through
  `commit --no-verify`, an amend, or a rebase that reintroduced an old blob
  after the staging gate already ran is still caught, because the tree that
  leaves the machine is what is read.
- **Staging gate (the convenient one).** Runs before a commit over the staged
  paths; a file that must be encrypted and is staged in plaintext is either
  encrypted and re-staged, or the commit is refused (§3.2).

Each outgoing blob is judged by three independent rules:

1. **Encrypted-container rule.** A file whose name says it holds secrets (the
   project's container naming convention) must begin with the encryption
   tool's header marker. Plaintext under that name blocks.
2. **Private-key rule.** No file may contain a raw private-key block (the
   armoured `BEGIN ... PRIVATE KEY` header, in its key-type variants).
3. **Literal-on-secret-key rule.** In configuration-shaped files, a key whose
   name is secret-shaped (§3.1) must carry a reference to the secret store,
   never a literal value.

It **complements a dedicated secret scanner** (`library-corpus/cli/gitleaks.md`)
and never replaces it: the scanner owns provider-token and entropy patterns;
this gate owns the project's own convention ("this kind of file is always
encrypted", "this kind of key is always a reference"), which no generic scanner
knows. `tool-corpus/ops/structured-secret-field-detector.md` is the third
neighbour: it asserts named keys absent inside one artifact's subtree.

## 2. Interface & invocation

Enabled per clone by pointing the VCS at a tracked hooks directory (for git,
`core.hooksPath`), so the hook is versioned and reviewed like code. A fresh
clone is unprotected until that one command runs: say so in the onboarding
node.

**Publication gate input:** the VCS hook protocol, one line per ref on stdin:

```
<local ref> <local sha> <remote ref> <remote sha>
```

- local sha all zeros: a branch deletion; nothing leaves, so skip.
- remote sha all zeros: a new branch; the range is every commit reachable from
  the local sha and **not already on any remote** (`rev-list <local> --not
  --remotes`). Ranging from the default branch instead re-scans or misses
  commits depending on where the branch forked.
- otherwise: `rev-list <remote>..<local>`.

**Output:** per finding, one line with the **rule, the path and the short
commit id**, never the matched value. Exit non-zero on any finding, with a
closing line that says: treat anything that was exposed as compromised and
rotate it, and rewrite the offending commits before pushing again.

## 3. Approach / algorithm

```
for each ref line:
    range = commits leaving the machine (above)
    for commit in range:
        for (mode, type, blob, path) in ls-tree -r commit:
            skip non-blobs (submodule links) and known binary suffixes
            verdict = cache[blob] or judge(blob, path)   # cache by blob id
            if verdict != ok: report(rule, path, commit)
exit 1 if any finding
```

- **Cache verdicts by blob id.** An unchanged file appears in every commit of a
  long range; keyed by content id, it is read once. The cache also makes the
  verdict independent of which commit it was first seen in.
- **Skip oversized blobs for content rules only.** A size ceiling (set it well
  above any real secret file) keeps a large asset from dominating run time;
  the encrypted-container rule still applies to a container file whatever its
  size, because a huge plaintext container is still plaintext.
- **Fail closed on an unusable interpreter.** When the shell is too old for the
  data structures the hook needs, exit non-zero with the fix, never fall
  through to "no findings".

### 3.1 The literal-on-secret-key rule

- **Key match by delimited segment, case-folded.** A key is secret-shaped when
  one of its `_`, `.` or `-`-delimited segments is in the vocabulary
  (`password`, `passwd`, `secret`, `passphrase`, `psk`, `pre_shared_key`,
  `private_key`, `api_key`, `access_key`, `access_token`, `auth_token`,
  `client_secret`, `bearer_token`, and the project's own). Segment matching
  catches `admin_password` and `password_min_length` alike; the **value check**
  then lets the second pass, so the vocabulary can stay broad without false
  positives.
- **A value is safe when it is clearly not a literal credential:** empty or
  quoted-empty; a comment; a template or secret-store reference in the
  project's syntax (one surrounding quote layer stripped first); an explicit
  null or omit token; a boolean or a plain number. Everything else blocks.
- **Reassemble block scalars.** A secret-shaped key whose value is a
  block-scalar indicator (`|`, `>`, with chomping marks) carries its real value
  on the following, more-indented lines. Join them and judge the joined text:
  judging the indicator line alone either blocks every multi-line reference (a
  false positive the hook's users learn to bypass) or passes every multi-line
  literal.
- **Scope by file type.** Apply the rule to configuration-shaped files only
  (YAML, JSON, INI-style, env, properties); prose and code carry the words
  "password" and "secret" legitimately.

### 3.2 The staging gate (encrypt or refuse)

Over the staged added, copied and modified paths whose names match the
container convention: read the **staged** blob (not the file on disk); when its
first line lacks the encryption header,

- if a secret-store password source and the encryption tool are both present,
  encrypt the file and re-stage it;
- otherwise refuse the commit and print the manual encrypt command.

This gate **mutates the index and the working file**, which makes it the
contentious half: encrypting the on-disk file and re-adding it stages the whole
file, including hunks the author had deliberately left unstaged, and the
author's plaintext working copy is gone. Review the staged state after it runs;
a project that dislikes mutation keeps only the refusal branch. The
publication gate is the one that must exist; this one is a convenience.

## 4. Portable vs blueprint

- **Portable (carry over):** range computation from the hook protocol;
  whole-tree-per-commit inspection; per-blob verdict cache; the three rule
  classes; segment-keyed key matching plus value-shape safety; block-scalar
  reassembly; findings that never print a value; fail closed on an unusable
  runtime.
- **Fill in per project:** the container naming convention and the encryption
  tool's header marker; the key vocabulary; the reference syntax that counts as
  safe; the binary suffix list and the size ceiling; the onboarding line that
  enables the hooks directory.

## 5. Pitfalls and sharp edges

- **The fixture must not trip the repository's own scanners.** A test that
  writes a private-key header literally into the test file is itself a finding
  for the dedicated scanner and for this gate. Build the header from string
  parts in the test so no committed file contains it whole.
- **A diff-only gate is the bypass.** Inspecting only the changed lines misses
  a plaintext blob reintroduced by a rebase or carried in an older commit of
  the range; read every outgoing tree.
- **A local hook is advisory to a determined user** (`--no-verify` skips it).
  It is the earliest net, not the only one: keep the dedicated scanner in CI
  and on the server side.
- **A finding means exposure is possible, not proven.** If the commit already
  reached any remote, rotation is owed whatever the rewrite does: history keeps
  the value (`core/method/secrets-posture.md`).
- **Name heuristics miss renamed keys and over-match look-alikes.** Keep the
  vocabulary and the safe-value shapes in one table with a test per entry; a
  false positive is fixed by tightening the value shape, never by dropping the
  key from the vocabulary.

## 6. Tests that cover it

Drive the **real hook** through its real protocol: create a throwaway
repository per test, commit fixtures, pipe a ref line on stdin, assert the exit
code and that the output names rule, path and commit and **never the value**.

Cover: an encrypted container passes and a plaintext one blocks; a private-key
block blocks (header built from parts); a literal on `password` and on a
pre-shared-key name blocks; a secret-store reference passes; a look-alike key
with a numeric value passes; a multi-line reference in a block scalar passes
and a multi-line literal blocks; an offending commit **older** than the range
tip is still caught; a commit already on a remote is not re-scanned; a branch
deletion line is ignored.

- **How to run the tests:** `<the plant's test command for its hook tests>`

## 7. References & neighbours

- **Related tools:** `tool-corpus/ops/structured-secret-field-detector.md`
  (named keys inside one artifact's subtree);
  `tool-corpus/ops/source-default-credential-gate.md` (literal defaults in
  source configuration); `tool-corpus/ops/destructive-command-guard-hook.md`
  (the agent-session hook neighbour);
  `tool-corpus/ops/env-secret-rotation.md` (what a finding leads to).
- **Library:** `library-corpus/cli/gitleaks.md` (the dedicated scanner this
  complements); `library-corpus/cli/git.md` (hooks and `rev-list`).
- **Doctrine:** `core/method/secrets-posture.md` (staging and publication
  gates, history is permanent).
- **Sources:** distilled from practice; no external URL.

## 8. Changelog

- 2026-10-14: created as a blueprint from a publication hook proven by
  hook-level tests over synthetic repositories, and a staging hook observed
  without tests (§3.2 carries that lower confidence).
