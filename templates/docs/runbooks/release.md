# Release

How this project goes from a verified build to running in front of users.
Every step is a named command, callable from CI; a manual step names the
human and the procedure.

## Release-readiness gate (all must hold before releasing)

- **Verification is green** on the exact artifact being released (link the
  `verification.md` increment).
- **A tested, documented rollback path exists** (`rollback.md`) — "deployed"
  and "production-ready" are different claims; a release with no rehearsed
  reversal is not releasable.
- **A rollback point is captured and verified** (data backup / previous
  immutable artifact reference), not assumed.
- **Deliberately excluded** — list what this release does NOT include
  (deferred hardening, known limitations); shipping config-complete is not the
  same as hardened, and the gap is stated, not implied.

## Procedure (named commands)

1. Preflight / readiness check: `<cmd>`
2. Build (produces the immutable artifact): `<cmd>`
3. Migration (with its rollback): `<cmd>`
4. Deploy: `<cmd>`
5. Smoke test: `<cmd>` — deployed system answers on its own health surface
6. Post-release verification: `<cmd>`

**Released bits are the tested bits** (the `reliability` delivery-pipeline
doctrine, applied operationally here). Release re-tags / promotes the exact
artifact that passed verification — pinned by an immutable digest, not a
floating tag — and never rebuilds at release time; a rebuild forfeits the
verification evidence.

## Records

### Release <version / tag> (YYYY-MM-DD)
- Artifact: `<name@digest>`
- Gates: `verification.md` increment `<title>` — PASS
- Rollback point: `<what was captured, where>`
- Outcome: `<result>`

<!-- Append a section per release. Never rewrite a past release record. -->
