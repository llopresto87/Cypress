# Tool: registry-digest-resolver

> Project-agnostic, durable capability notes, folded into the seed by the
> harvest protocol. This page is a **BLUEPRINT**: the hop-by-hop verification
> method is portable; the registry's own token and manifest endpoints are
> written against the OCI Distribution Spec surface (widely implemented, but
> not identical in every deployment: a private registry can gate the
> anonymous-token step).

## 0. Identity

- **Category:** ops
- **Name:** registry-digest-resolver
- **Language / runtime:** any (an HTTP client that can send bearer tokens and
  read response headers is the whole requirement — no registry SDK, no
  container runtime)
- **Stability:** **blueprint**: the method is a direct, documented sequence
  of OCI registry HTTP calls, but no portable implementation ships because
  the exact endpoint host and repository-name shape vary per registry
  (`ghcr.io`, `registry-1.docker.io`, a private registry) and per the
  adopting project's own image references.

## 1. What it does

Resolves a container image **tag** to its full set of content addresses
(the index or tag-manifest digest, the platform-specific manifest digest,
and the config-blob digest), using only the registry's own HTTP API, with
**no image pull and no container daemon**. It exists because a pinned image
reference is only as trustworthy as the digest it is checked against, and
computing that digest by pulling the image first (to run `docker image
inspect` or equivalent) both requires a daemon and, critically, reports a
value whose meaning **depends on which image store the daemon uses** (see
§5). This tool answers the same question straight from the registry's
content-addressed API, with no daemon in the loop at all, so the pin can be
verified anywhere an HTTP client can reach the registry: a CI step with no
container runtime, a review, or a pre-merge check.

## 2. Interface & invocation

```sh
registry-digest-resolve \
  --ref <registry>/<repository>:<tag> \
  --platform <os>/<arch>[/<variant>] \
  [--registry-auth <anonymous|token-env-var>] \
  [--cross-check <expected-digest>] \
  [--json]
```

- **Inputs:** a full image reference (registry, repository, tag); the target
  platform (`os/arch`, e.g. `linux/amd64`, or `os/arch/variant`, e.g.
  `linux/arm/v7`); optionally, an already-known
  digest to cross-check against (from a prior observation, a second registry
  API, or a declared pin), never a value to trust instead of computing.
- **Outputs:** the tag-manifest (index) digest; the selected platform
  manifest's own digest; the config-blob digest and its declared
  `os`/`architecture`; a cross-check verdict when `--cross-check` is given.
- **Exit codes:** 0 every hop verified and any cross-check agreed; 1 a hop's
  computed hash did not match its own claimed digest, or a cross-check
  disagreed; 2 usage error or a network/auth failure that prevented
  resolution (never conflated with 1; see §5).
- **Preconditions:** network reach to the registry's token and manifest
  endpoints; no daemon, no pull, no local disk image cache required.

## 3. Approach / algorithm

Every hop is verified against **its own claimed address**, never trusted
because it came from an authenticated response. That is the whole method:

1. **Take an anonymous pull token** from the registry's token endpoint,
   scoped to `pull` on the one repository. Most public registries issue this
   with no credential at all; a private registry substitutes its own
   authenticated token exchange here, unchanged in every later step.
2. **Fetch the manifest by tag**, and check that the response body's own
   sha256 equals the value the registry reports in its
   `Docker-Content-Digest` response header. That hash (not the header alone, and not the tag name)
   is the **index digest** (or, for a single-platform image with no index,
   the tag's own manifest digest directly).
3. **Select the one platform manifest entry** for the requested
   `--platform` from the index's own list. When a variant is given, match
   `os`, `architecture` and `variant` exactly. When no variant is given, take
   the unique entry whose `os` and `architecture` match, whatever its
   variant, and refuse (exit 2, naming the candidates) when there is more
   than one: an index that carries `arm/v6` and `arm/v7` side by side is
   ambiguous for a bare `linux/arm`, and silently picking one pins the wrong
   image. Then **fetch that manifest by its digest** (not by tag). Check that its body's
   sha256 equals the digest it was fetched by. This is the digest a
   containerd-backed daemon's `image inspect` reports for a multi-platform
   tag (see §5); it is not the same value as step 2's index digest.
4. **Fetch the config blob** named in the platform manifest, by its digest,
   and check both that its body's sha256 equals that digest and that its
   declared `os`/`architecture` (and `variant`, when one was requested and
   the config declares it) match what was requested. A config digest
   mismatch or a platform mismatch is a resolution failure, not a warning.

A second, independent source (a different registry's own tag API, or a
previously recorded observation from a real pull) is the natural
cross-check (`--cross-check`), never a substitute for verifying each hop
against its own address first.

## 4. Portable vs blueprint

- **Portable (adopt verbatim):** the four-hop sequence and what each hop
  verifies against; the anonymous-token-first approach; treating a
  cross-check as confirmation, never as the primary evidence; the platform
  selection rule (an exact variant match when a variant is given, the
  unique `os`/`architecture` entry when it is not, and a refusal when that
  entry is ambiguous); the closed distinction between a
  verification failure (exit 1) and a resolution failure (exit 2).
- **Blueprint (write per registry):** the token endpoint's exact host and
  scope-parameter shape; the manifest media types the registry serves
  (`application/vnd.oci.image.index.v1+json` and kin, which can differ by
  registry and by how the image was pushed); how a private registry's
  authenticated token exchange replaces the anonymous-token step.
- **Adopting note:** a registry that serves a single-platform manifest
  directly at the tag (no index layer) collapses steps 2 and 3 into one hop;
  detect this from the manifest's own declared media type rather than
  assuming every tag has an index.

## 5. Pitfalls and sharp edges

- **"The image ID" is not one number: it depends on which store computed
  it.** A daemon backed by the classic graph-driver store reports a pulled
  image's **config digest** as its id; a daemon backed by the containerd
  image store reports **the digest the tag itself points at**, which for a
  multi-platform image is the **index digest**, not the config digest. A pin
  declared against one store's notion of "the image id" reads as a mismatch
  on the other store, with no code change on either side. The daemon
  changed what the same field means. Resolving straight from the registry
  sidesteps the question by naming which digest is which (index, manifest,
  config) instead of relying on a single ambiguous "the id."
- **A registry's own tag listing is not proof of what a tag currently
  points at.** Only a manifest fetch, verified against its own content
  hash, proves that; a cached or stale listing view can lag.
- **Never treat a cross-check's agreement as the reason to skip verifying a
  hop against its own hash.** The cross-check exists to catch a
  registry-side inconsistency between two independent views, not to replace
  the structural guarantee that each fetched object's bytes hash to the
  address it was fetched by.
- **A tag can move.** A digest resolved today is a fact about today; a later
  push to the same tag changes every value this tool reports. Re-run
  whenever the pin is meant to be re-verified, and treat "the same tag now
  resolves differently" as a signal, not noise.
- **An unrecognized manifest media type is a resolution failure, not a
  best-effort guess.** Guessing which bytes are "probably the config blob"
  defeats the entire point of hashing each hop against its own claimed
  address.

## 6. Tests that cover it

Cover, against a fake HTTP transport (no real registry, no network): the
anonymous-token step is attempted first and its absence (a 401 requiring
real auth) is reported as a distinct outcome from a verification failure;
a manifest whose body hash does not match its `Docker-Content-Digest`
header fails closed with the mismatch named; platform selection matches a
given variant exactly (an index with `arm/v6` and `arm/v7` returns the
requested one), takes the unique `os`/`architecture` entry when no variant
is given (including an entry that carries a variant), refuses with the
candidates named when a bare `os/arch` matches more than one entry, and
refuses when nothing matches; a config blob whose hash or declared platform does not match fails
closed; a `--cross-check` agreement and disagreement are both reported
distinctly from a plain resolution; a single-platform tag with no index
layer resolves through the collapsed two-hop path.

- **How to run the tests:** `<the plant's test command for its implementation>`

## 7. References & neighbours

- **Related library page:** `library-corpus/container/docker.md` (the
  image-store-dependent meaning of `docker image inspect --format
  '{{.Id}}'` that this tool exists to sidestep: read there, not restated
  here).
- **Related tools:** `tool-corpus/ops/hashed-lock-closure-check.md` (the
  same discipline: verify a closure independently rather than trusting a
  cached or partial view, applied to a language package manager's lock
  instead of a registry tag).
- **Sources:** the OCI Distribution Specification
  (<https://github.com/opencontainers/distribution-spec/blob/main/spec.md>),
  the registry HTTP API this method drives, including the
  `Docker-Content-Digest` response header; and the OCI Image Format
  Specification (<https://github.com/opencontainers/image-spec>), whose
  `image-index.md`, `manifest.md` and `config.md` define the index,
  manifest and config digest relationships and the `platform` fields
  (`os`, `architecture`, `variant`). Registry hosts and token endpoints are
  not restated here; pin the spec release you build a real client against.

## 8. Changelog

- 2026-09-26 — created from harvested, generalized capability, by
  docs-librarian.
- 2026-09-26 — corrected after review: platform selection takes an optional variant (exact match when given; the unique os/arch entry, or a refusal when ambiguous, when not); OCI spec URLs and the `Docker-Content-Digest` header named.
