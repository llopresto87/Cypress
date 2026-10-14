---
stack:
  - library-corpus/maven/playwright
  - library-corpus/npm/playwright-test
  - library-corpus/nuget/Microsoft.Playwright
---
# Tool: sandboxed-browser-test-runner

> Project-agnostic capability notes, kept in the seed's tool corpus
> (`tool-corpus/README.md`). This page is a **BLUEPRINT**: the separation of the
> browser group, the image-by-digest rule, the container hardening posture, the
> deny-by-default origin guard and the outcome table are portable; the image,
> its run flags and the test wiring are the browser library's, on its own
> library page.

## 0. Identity

- **Category:** testing
- **Name:** sandboxed-browser-test-runner
- **Language / runtime:** a shell stage driving a container runtime, plus a
  small fixture in the test code (the origin guard).
- **Stability:** **blueprint**.

## 1. What it does

Runs the project's **real-browser tests** as their own gate stage, in a
separate vendor runner image that carries the browsers, pinned by digest and
run with a hardened container profile, and proves the run touched **nothing
but the application under test**:

- browser tests carry their own tag; the default suite excludes it and only
  this stage runs it;
- the application, the tests and the browser run in **one container**, the
  browser reaching the app on `localhost`, with no published port and no host
  network;
- the browser context **aborts every request to another origin and records
  it**, and the test fixture's close **fails** if anything was aborted. A green
  run is then evidence that no off-origin request left the page;
- after the stage, whatever its outcome, an **orphan check** confirms no test
  infrastructure the run started outlived it.

It exists because browser tests are the suite's widest network and
supply-chain surface: a library that downloads browsers on first use, a vendor
image that runs as root, pages that may load third-party assets. Running them
inside the main build image means downloading binaries at test time with no
recorded checksum; running them without an origin guard means a green run says
nothing about what the page fetched.

## 2. Interface & invocation

```
gate --with-browser [--tests LIST]      # stage `browser`, then `leak`
```

- **Image reference:** read `ref` and `digest` from the project's single
  version/compatibility record (the entry with role `browser-runner`), never
  written into the script. Exactly one such entry, a `sha256:` digest of 64 hex
  characters, and a ref with no `@`; anything else fails the stage with **no
  pull and no run**. There is **no fallback to the tag**.
- **Pull** only when the digest is absent on the host, only in this stage, under
  its own bound.
- **Outcome table:**

| status | when |
|---|---|
| PASS | the runner exited 0, at least one browser test ran (skipped is not ran), none failed |
| FAIL | a failing test; **zero tests ran**; the image not obtainable by digest; the runner could not start; the transport lost |
| TIMEOUT | the stage bound was hit; names the in-flight tests |
| SKIPPED | not requested, or an earlier stage failed; never PASS, recorded as absent |

- **Bounds** (stage seconds, pull seconds, memory, pid limit) are validated
  integers or sizes; a bad value is a usage error.
- **On anything but PASS**, copy back the test reports and the full-page
  screenshots a red case saves (synthetic data only), and say how many files
  came back, including zero.

## 3. Approach / algorithm

**One version, two places.** The browser library and its runner image move
together, or the library does not find the browsers the image ships
(`library-corpus/maven/playwright.md`). The gate tests are the version
matrix's cross-checks (`tool-corpus/ops/resolved-dependency-gate.md` §3.4):
the dependency version, the image tag and the record entry are compared, and
every artifact of the browser library must resolve test-scoped, so neither
the browsers nor the image reach the production artifact.

**Hardened run** (flags are the container runtime's; the browser-specific ones
are on the library page, `library-corpus/maven/playwright.md`):

- `--rm`, a per-lane container name, removed by name before and after;
- an init process; shared memory sized for the browser rather than the host
  IPC namespace, where the project's posture refuses host IPC (the library page
  records upstream's advice and the observed alternative);
- drop all capabilities, `no-new-privileges`, a memory limit and a pid limit;
- a `tmpfs` mounted over the tree's secrets directory, and only the
  environment variables the run needs (the library's skip-browser-download
  switch among them);
- no host network namespace, no published port.

With every capability dropped, a root process loses its override of file
permissions, so a tree synced from a workstation under another uid must be
`chown`ed to the container user first, or the build cannot write its output
directory.

**Origin guard** (test code):

```
context.route("**/*", route ->
    if origin(route.request.url) == appOrigin: route.resume()
    else: aborted.add(route.request.url); route.abort())
fixture.close(): if aborted not empty: fail("off-origin requests: " + aborted)
```

Pair `ignoreHTTPSErrors` for a throwaway local certificate with this guard,
never with a bypass of the page's content-security policy.

**TLS in the app, not in a proxy.** When the session cookie is `Secure` (or
`__Host-` prefixed), the browser drops it over plain HTTP. Start the app with
TLS on a throwaway keystore generated per run (random password, short
validity, `localhost` and `127.0.0.1` in the SAN, in a temp directory, never
in the repository or a log) rather than weakening the cookie for tests or
adding a proxy image.

**Orphan check.** Record the test-infrastructure containers before the stage;
afterwards, report `CLEAN`, `LEAKED <ids>` or `UNKNOWN (<why>)`. A container is
blamed on the run only when it is new and no live reaper of its own session
remains (`tool-corpus/testing/staged-index-commit-gate.md` owns the session
rule).

## 4. Portable vs blueprint

- **Portable:** a separate tagged browser group; the image by digest from one
  record, no tag fallback; the hardened profile; app, tests and browser in one
  container; the origin guard that fails on close; the outcome table with
  zero-tests as FAIL; reports and screenshots copied back on failure; the leak
  check after every outcome; the version-equals-image-tag and test-scope gates.
- **Fill in per project:** the record format and its parser, the test tag and
  profile, the runner command, the bounds (sized from a measured green run, see
  `tool-corpus/testing/long-stage-progress-runner.md`), and the app's TLS start.

## 5. Pitfalls and sharp edges

- **A test container that needs the container-runtime socket** (to start a
  database next to the browser) makes the runner root-equivalent on its host.
  That is a recorded exception to `library-corpus/container/docker-host-hardening.md`,
  not a default: mitigate with digest pinning, synthetic data only, no browser
  egress, a remote bound and per-lane names, and record the residual risk.
- **The vendor image runs browsers as root, which disables the browser
  sandbox** (`library-corpus/maven/playwright.md`). The origin guard and
  first-party synthetic pages are what keep that acceptable.
- **The image's language runtime may differ from the main build's.** Record the
  difference as accepted for this group only.
- **An untagged browser test that leaks into the default suite** tries to
  download browsers. Set the skip-download switch for every test run, so it
  fails instead of fetching hundreds of megabytes.
- **Zero tests ran is not green.** A selection or tag typo produces an exit 0
  with nothing run; count non-skipped tests from the reports.
- **`set -e` with an empty artifacts directory** can end the stage before its
  STAGE line; count files explicitly.

## 6. Tests that cover it

Against stub runtime and transport binaries
(`tool-corpus/testing/remote-stub-fixture.md`): digest resolution fails closed
for a missing, duplicated or malformed entry and never falls back to the tag;
no pull or run without a digest; pull only by `ref@digest`; the hardening flags
present and host IPC absent; each row of the outcome table, including zero
tests and a red run with an empty artifacts directory; screenshots copied
back; TIMEOUT; SKIPPED after an earlier failure; the default suite never runs
the group; the leak check and the summary still printed after a red stage.
In the test code: a page that requests another origin fails the fixture's close.

- **How to run the tests:** `<the plant's test command for its implementation>`

## 7. References & neighbours

- **Library pages (image, flags, version coupling):** `library-corpus/maven/playwright.md`,
  `library-corpus/npm/playwright-test.md`, `library-corpus/nuget/Microsoft.Playwright.md`;
  `library-corpus/container/docker.md`; `library-corpus/container/docker-host-hardening.md`.
- **Related tools:** `tool-corpus/testing/long-stage-progress-runner.md` (the
  streamed log and heartbeat of the stage); `tool-corpus/testing/staged-index-commit-gate.md`
  (the browser group as its own lane, the orphan rule);
  `tool-corpus/ops/image-reference-pin-lint.md` (digest pinning of the images
  the project declares); `tool-corpus/testing/in-network-e2e-harness.md`
  (end-to-end driving inside the deployed stack's network, a different scope).
- **Sources:** distilled from practice; the browser library's Docker guide
  (cited on the library pages).

## 8. Changelog

- 2026-10-14 — created by docs-librarian.
