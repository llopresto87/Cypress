# Release

How this project goes from a verified build to running in front of users.
Every step is a named command, callable from CI; a manual step names the
human and the procedure.

## Release-readiness gate (all must hold before releasing)

- **Verification is green** on the exact artifact being released (link the
  `verification.md` increment).
- **A tested, documented rollback path exists** (`rollback.md`) — "deployed"
  and "production-ready" are different claims; only a release with a
  rehearsed reversal is releasable.
- **A rollback point is captured and verified** (data backup / previous
  immutable artifact reference), not assumed.
- **Deliberately excluded** — list what this release leaves out (deferred
  hardening, known limitations), so the gap between config-complete and
  hardened is stated.
- **Evaluations are compared with the checked-in baseline** where behaviour
  is model-driven, and the comparison is linked here the way the
  verification increment is.

## Boundaries and expected non-green outcomes

Written the way `operations.md` writes them. List what this procedure may
not touch and where its credential comes from, then each red it produces
by design with the field that proves it is the designed verdict.

- Off limits: `<environments, hosts, credential groups>`
- Credential: `<source; read in process, never printed>`
- Expected red: `<step>`, designed, proven by `<field or log line>`

## Procedure (named commands)

1. Preflight / readiness check: `<cmd>`
2. Build (produces the immutable artifact): `<cmd>`
3. Migration (with its rollback): `<cmd>`
4. Deploy: `<cmd>`
5. Smoke test: `<cmd>` — deployed system answers on its own health surface
6. Post-release verification: `<cmd>`

**Released bits are the tested bits** (the `reliability` delivery-pipeline
doctrine, applied operationally here). Release re-tags / promotes the exact
artifact that passed verification, pinned by an immutable digest, because a
rebuild or a floating tag forfeits the verification evidence.

## Records

### Release <version / tag> (YYYY-MM-DD)
- Artifact: `<name@digest>`
- Gates: `verification.md` increment `<title>` — PASS
- Rollback point: `<what was captured, where>`
- Outcome: `<result>`

<!-- Append a section per release; past records stay as written. -->
