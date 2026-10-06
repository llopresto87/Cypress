# Suggested skill: third-party-handover

> Optional procedure: hand a multi-repository system to an outside party in
> two parts. Part A builds a runnable bundle that brings the whole system up
> on one machine with one command and only a container runtime. Part B sweeps,
> strips, archives and verifies the repositories, so nothing internal leaves
> with them. Composes `skill-corpus/release.md` (identifier hygiene and the
> acceptance round), `skill-corpus/vendor-dependency-from-dead-registry.md`
> (dependencies whose registry is gone), `skill-corpus/harden-docker-host.md`
> (preflight on the host that proves the rebuild), `skills/holistic-editing/`
> (editing shipped text), `core/method/vcs-posture.md` (history is never
> rewritten without the owner) and `protocols/verify.md` (a gate asserts
> something; an absence is recorded, not implied). Parameterized by
> `<REPOS>` (the repositories handed over), `<UPSTREAM>` (the upstream ref
> each delivery branch starts from), `<RECIPIENT_OS>` (the systems the
> recipient will run and unpack on), `<SCRATCH_HOST>` (a disposable machine
> for the rebuild proof) and `<SWEEP_TERMS>` (the internal vocabulary to hunt:
> internal names, document-id formats, local path roots, tool traces).

## When to apply

- The system, or part of it, must be delivered to a client, a contractor or
  a new maintainer outside the team, as source plus a way to run it.
- A delivery already made must be refreshed and shipped again.
- Any file is about to leave the team (a document, a README, a commit) and
  must carry no internal reference.

The move this replaces is an ad hoc pass of "zip it up and grep for the
obvious". Each ad hoc pass misses something different: an id format the first
pattern did not cover, a local path hiding in a clone's `FETCH_HEAD`, a
wrapper the recipient cannot open. Part B is ordered so that each miss is
caught by a gate.

Packaging is not a release. An acceptance round with the owner is
`skill-corpus/release.md`; this page builds and checks the package itself.

## Part A: the runnable bundle

The goal is that the recipient runs one command on one machine and gets the
whole system, seeded, with the container runtime as the only prerequisite.

1. **Full clones on a delivery branch.** Ship each repository in `<REPOS>`
   as a full clone, checked out on a dedicated delivery branch that starts at
   `<UPSTREAM>`. Then `git log <UPSTREAM>..HEAD` is the exact delivery diff,
   and the main branch stays untouched in every repository. Delivery changes
   are new commits on that branch, never amended or rebased upstream commits.
2. **Build what no registry serves, from source, inside the image build.**
   An internal library, or one whose registry is gone, is built from source
   at the tag whose version the consumer pins
   (`skill-corpus/vendor-dependency-from-dead-registry.md`), in a build stage
   whose toolchain matches what that library targets. An old library can fail
   to compile on a newer toolchain, so give it its own stage. The recipient
   needs no registry credentials and no private mirror.
3. **One compose project that coexists.** Give the bundle its own compose
   project name and set no `container_name`, so it can run beside the
   recipient's other stacks. Publish only the edge; everything else stays on
   the internal network.
4. **Seed only into empty volumes.** Restore the demo data through the
   datastore images' initialization hooks, which run only when the data
   volume is empty. Healthchecks wait until the seed is loaded, so the
   services start only against seeded data. A `--reset` verb wipes the
   volumes and seeds again. Ship seed files in the form the image can read
   (plain SQL when the image may lack a decompressor). The data is synthetic
   (`skill-corpus/seed-demo-world-for-manual-ui-review.md` for building it).
5. **Turn every outbound integration off.** Disable scheduled imports, mail
   sending to real servers (use a local mail catcher), and calls to partner
   systems, by configuration. Then list what still reaches the internet at
   run time (fonts or scripts from a CDN, push-notification setup, a feed
   baked into a client) and put that list in the hand-over notes.
6. **Generate per-install secrets and certificates on first start.** A
   signing key or a TLS certificate is created when the install has none,
   never shipped in the bundle, so no two installs share a key. A backend that
   admits one browser origin ties that origin to the certificate name.
   Observed in practice: a recipient who opened the bundle from a second
   machine by the host's address got 403 on login until both the configured
   origin and the certificate name were changed to that address, and then
   `localhost` became the rejected origin. Put the two settings side by side
   in the configuration example and in the README, with the steps to switch
   between local and network access. Generate-if-absent ignores a changed
   certificate name, so have the first-start step reissue the certificate
   when its SAN lacks the configured name. Where it cannot, document the
   manual step (usually: remove the certificate volume and redeploy).
7. **One driver per operating system, same verbs.** Provide a driver script
   for each system in `<RECIPIENT_OS>` (a shell script for Linux and macOS, a
   PowerShell script with a `.cmd` wrapper for Windows) with the same verbs:
   up, `--reset`, `--down`, `--status`, `--logs`. Each driver runs a
   preflight (the runtime, Compose v2, the build plugin when the Dockerfiles
   use BuildKit-only features), builds one image at a time, waits for health,
   and ends with a built-in smoke check (the front end answers, a demo login
   succeeds). A driver that was only parse-checked on a system has not run
   there: say so in the notes.
8. **State the host requirements honestly**: the minimum runtime version
   the compose features need, the memory and free disk a full build takes
   (measure the peak during the build; it is far above the final size), the
   ports that must be free, and that internet access is needed for the first
   build only.
9. **Write the recipient's documents in the recipient's language**, and run
   them through the prose skill the team uses. A changes document lists the
   functional changes the delivery carries.

Gate for Part A: on `<SCRATCH_HOST>`, a cold run, a `--reset` followed by a
re-run, and a second run with no build all exit 0, and the smoke check
passes each time. Record which drivers ran and which were only parsed.

## Part B: the repository hand-off sweep

1. **Hold the rules.** Shipped text is edited under `skills/holistic-editing/`
   so the result reads as if it was always written that way. History is never
   rewritten to fix a leak without the owner (`core/method/vcs-posture.md`):
   a leak in old commits is reported to the owner as a decision, with the
   commits named. If the owner accepts it, record the accepted exception.
2. **Sweep broad, then broader.** Search for `<SWEEP_TERMS>` in all of:
   - the working tree of every clone, comments and Dockerfiles included;
   - the full history (`git log -p --all`) and every commit message;
   - the XML inside office documents (`unzip -p <file>.docx
     word/document.xml`), since a plain grep does not see inside them;
   - the clone metadata (`FETCH_HEAD`, `ORIG_HEAD`, reflogs, config), where
     a local path can hide.

   Hunt local path roots, internal document ids written as classes (an ADR
   number, a tier label, a finding id in parentheses, "Decision N"), graph or
   working-document paths, agent and tooling traces, and old product names.
   Gate: a **second, wider** pattern finds zero new hits. A first pattern
   that returns zero proves nothing, because it only finds what its author
   thought of.
3. **Review comment-only cleanups by diff.** Every changed line in a cleanup
   commit must be a comment, a test description or a label. Any code line in
   the diff is a stop: review it as a code change. A display rename touches
   display text only; identifiers, CSS classes, JSON fields, routes and wire
   names are contracts and stay. Re-run the repositories'
   own gates after the cleanup commits.
4. **Prove a from-scratch rebuild** on `<SCRATCH_HOST>` with empty volumes,
   from the cleaned clones (Part A's gate, run again after the cleanup).
   Record what was not re-verified, by name, instead of implying it.
5. **Prove build self-containment.** List, per toolchain, where it resolves
   dependencies from: public registries only, with private artifacts built
   from vendored source (a build-tool mirror that routes every request to
   the public registry is one way). Inventory the binaries shipped in the
   trees (vendor SDK archives, prebuilt libraries) and whether a
   redistribution licence is recorded for each. Record what still calls the
   internet at run time (Part A step 5).
6. **Strip each clone.** Remove the hooks, `FETCH_HEAD` and `ORIG_HEAD`,
   run `git reflog expire --expire=now --all`, then `git gc --prune=now`,
   and delete desktop metadata files (`.DS_Store`, `._*`). Gate: `git fsck
   --full --unreachable` prints nothing. Plain `git fsck` names only the
   dangling tips of what is left, not every unreachable object.
7. **Archive with a checksum.** Build the archive keeping symlinks as links and
   dropping the platform extra fields, which on Unix carry the owner's
   uid/gid and extra file times (with Info-ZIP: `zip -r -y -X <bundle>.zip
   <dir>/`; the permission bits are kept either way), and write its sha256 beside it. If the owner wants the archive
   encrypted, wrap it in a container that the recipient's stock tools open on
   `<RECIPIENT_OS>`, and test that on the target system before sending.
   Observed in practice: the built-in Windows archive handler opened legacy
   zip encryption but not AES-encrypted zip, so AES would force the
   recipient to install a tool. Legacy zip encryption is weak: treat it as a
   guard against casual opening, not as confidentiality. The password goes to
   the recipient out of band and is never written into any file, record or
   message the team keeps.
8. **Extract and verify in a clean directory.** Gate: the sha256 matches;
   the extracted files are byte-identical to the source with permissions
   kept; `git fsck` passes for every clone; a grep of the extracted tree for
   local path roots finds nothing. Regenerate any commit list or manifest
   the package carries if commits changed since it was written: a stale one
   is the usual miss.

## Anti-patterns

- Trusting one search pattern, or searching the tree but not the history,
  the commit messages, the clone metadata and the office documents.
- Rewriting history to remove a leak without the owner's decision.
- A wrapper the recipient's own system cannot open, or a password written
  down anywhere.
- Shipping a driver nobody ran, or a verification list that implies more
  was checked than was.
- Leaving a pending-verification list in the documents the recipient reads:
  record the gaps in the team's own record and in the hand-over notes as
  plain limits.

## Reference files

- `skill-corpus/release.md` (identifier hygiene and the acceptance round)
- `skill-corpus/vendor-dependency-from-dead-registry.md` (Part A step 2)
- `skill-corpus/seed-demo-world-for-manual-ui-review.md` (synthetic seed data)
- `skill-corpus/deploy-fleet-on-remote-docker-host.md` (the serialized build
  and preflight checks the drivers reuse)
- `skills/holistic-editing/`, `core/method/vcs-posture.md`, `protocols/verify.md`
