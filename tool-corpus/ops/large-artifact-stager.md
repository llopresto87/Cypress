# Tool: large-artifact-stager

> Project-agnostic, durable capability notes, folded into the seed by the
> harvest protocol. This page is a **BLUEPRINT**: the four idioms are portable
> and are the whole value; the transfer mechanics are written against the
> adopting project's container tool, transport, and host layout.

## 0. Identity

- **Category:** ops
- **Name:** large-artifact-stager
- **Language / runtime:** any (typically a shell driver plus a container build
  and a transport client)
- **Stability:** **blueprint only** — no portable implementation; the value is
  four build-and-transfer idioms and the guarded-root rule

## 1. What it does

Stages heavy binary payloads onto a host that **must already have them** before
the first run of a service that **cannot itself fetch them**.

The situation is common and specific: a service starts, needs a large artifact —
a model, a dataset, an index, a media corpus, a base image layer — and has no
network path to retrieve it, either because the environment is isolated, because
the source requires a credential the service must not hold, or because a
first-run download of that size is not an acceptable start-up cost. Someone must
put the bytes there first, reproducibly, and prove they landed in a state the
consuming account can actually read.

## 2. Interface & invocation

```sh
stage-artifacts \
  --manifest <what to stage, and where each item goes> \
  --target <host or destination selector> \
  --root <the one directory every write must resolve under> \
  [--dry-run]
```

- **Inputs:** a declarative manifest of artifacts and destinations; the target
  selector; the guarded root; credentials for the source, supplied at build time
  and never written into the staged tree.
- **Outputs:** per-artifact transfer result and a post-transfer readability
  verdict for each destination; non-zero on any failed transfer, any unreadable
  destination, or any path that escapes the guarded root.
- **Preconditions:** a container runtime able to **build**; a transport to the
  target; the consuming account's identity known **before** staging, since it is
  what the verification step checks against.

## 3. Approach / algorithm

Four idioms. They are the whole value of the page.

### 1. Build a container for the job; do not use a one-shot run

Build a purpose-made image for the staging job rather than running a generic
image with a pile of setup flags. The reason is a privilege split that a one-shot
run cannot express cleanly:

- **Privileged install steps happen at BUILD time, as root** — package installs,
  client tools, certificate placement, directory creation. They happen once, are
  captured in the image, and are reviewable as part of the build definition.
- **Every actual transfer runs as the INVOKING non-root user.** The process that
  reads source credentials and writes into the destination has no more privilege
  than the person who started it, and the files it creates carry that identity
  rather than root's.

The alternative — a one-shot run that installs as root and then transfers as root
— produces a staged tree owned by root that the consuming service cannot read,
and the discovery happens at the service's first start, on the host, later.

### 2. Content-address the image tag from the build definition

Derive the image tag from a digest of the build definition (and of anything else
that determines the image's contents). A changed definition then **cannot** serve
a stale image under an old name: the tag changes with the content, so the old tag
still names the old image and the new build is addressed by a new one.

Reusing a fixed tag is the quiet version of this bug. The definition changes, the
build is skipped or served from cache, and the staging job runs the previous
image while every log line says the new one.

### 3. Verify readability after every transfer, by the consuming account

After each transfer, check that the written tree is **readable by the account
that will consume it** — not by root, not by the invoking user, but by the
service identity. Check the directory traversal bits along the whole path, not
only the leaf file: a readable file under a directory the account cannot enter is
unreadable in practice, and is the most common way this fails.

Do it **after every transfer**, not once at the end. A single failure mid-run
otherwise leaves a half-staged tree that the final check may still pass on the
parts it samples.

### 4. Validate every touched path against one guarded root — twice

Before any write or delete, prove the path resolves under the one guarded root:

- **lexically** — after normalization, with relative segments and any
  parent-directory traversal resolved, the path must be under the root; and
- **after symlink resolution** — resolve the real path and check again, because
  a symlink planted in the destination tree turns an innocent write into a write
  somewhere else entirely.

Both checks, in that order, on **every** path, including the ones the tool
constructed itself — a path built from a manifest entry is attacker-influenced
input the moment the manifest is editable. A deletion path gets the same
treatment as a write path, and more carefully: staging jobs clean up, and cleanup
is where a root-escaping path does the most damage.

## 4. Portable vs blueprint

- **Blueprint (the whole page):** the build definition, the transport, the
  identity model, and the manifest format are all project-specific.
- **Durable across every implementation:** (a) build-for-the-job with the
  root-at-build / invoking-user-at-transfer split; (b) content-addressed image
  tags derived from the build definition; (c) post-transfer readability
  verification by the consuming account, after **every** transfer; (d)
  double-validated guarded root — lexical **and** symlink-resolved — before any
  write or delete.

## 5. Pitfalls and sharp edges

- **Root-owned staged trees are the default failure.** Everything works, the
  transfer reports success, and the service fails to start much later with a
  permission error that points at the service rather than at staging.
- **A fixed image tag hides a changed build.** Content-address it, or accept that
  some runs use an image nobody can identify afterwards.
- **Checking only the leaf's permissions misses the directory bits.** Traversal
  on every ancestor is part of readability.
- **Lexical path validation alone is not enough, and symlink resolution alone is
  not either.** The first misses a planted symlink; the second can be defeated by
  a path that does not exist yet at check time. Do both, and re-check immediately
  before the operation rather than at manifest-parse time.
- **Credentials must not survive into the staged tree.** They belong to the
  transfer step and to nothing that is written to the destination — not in a
  config file copied alongside, not in a cached credential helper directory that
  happens to sit under the root.
- **Partial staging is a valid outcome and must be reported as one.** Large
  transfers fail halfway. A run that stages most artifacts and stops must exit
  non-zero and name exactly what landed, so a retry is a retry and not a guess.
- **Idempotence is worth designing in.** Staging jobs are re-run after failures;
  re-transferring an artifact already present and readable should be cheap and
  safe, and must not delete the good copy before confirming the replacement.

## 6. Tests that cover it

Cover: a staged tree is readable by the consuming account, including directory
traversal on every ancestor; a transfer performed as root is caught by the
readability check rather than reaching a host; a changed build definition yields
a different image tag, and the old tag still names the old image; a manifest
entry whose destination escapes the guarded root by parent-directory traversal is
refused before any write; a symlink inside the destination that points outside
the root is refused, including when the lexical check alone would pass; a
mid-run transfer failure exits non-zero and names exactly which artifacts landed;
a deletion path outside the root is refused; re-running a completed staging job
is a safe no-op.

- **How to run the tests:** `<the plant's test command for its implementation>`

## 7. References & neighbours

- **Related tools:** `tool-corpus/ops/container-deploy-pipeline.md` (the
  immutable-tag-and-digest discipline this shares, applied to the deployed image
  rather than the staging image); `tool-corpus/testing/ci-runner-local-simulator.md`
  (reconstructs the environment a staging job runs in);
  `tool-corpus/testing/http-smoke-suite.md` (the post-start check that the staged
  artifacts are actually being served).
- **Sources:** distilled from harvested plant experience; no external URL.

## 8. Changelog

- 2026-09-13 — created from harvested, generalized capability, by docs-librarian.
