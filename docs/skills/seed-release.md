---
name: seed-release
description: Seed-only. The end-of-round release of the CYPRESS seed. One documentation pass brings every mirror, derived figure, walkthrough, reference page, manifest field and the CHANGELOG entry current with the round's changes. Then come the gate, the staged release notes, the commit, the steward plant's canonize close-out, and the tag push on the owner's go-ahead.
id: skill.seed-release
kind: skill
origin: seed-only
owns:
  - seed-release.when
  - seed-release.flow
  - seed-release.doc-surfaces
  - seed-release.dedupe-rule
load_when:
  - "end of a seed round, release the seed, bring the seed documentation current"
  - "update mirrors, derived figures, reference pages, manifest and changelog once"
  - "stage the release notes, prepare-release, tag push"
---

# seed-release

The seed ships a method, and its human docs, manifest and reference pages describe that method. A seed round changes nodes, tools and checks. This procedure brings every surface that describes them current, once, at the end of the round, and then releases the version. It runs in the seed only: `install.sh` reads nothing under `docs/`, and `manifest.json` names neither this file nor `tools/prepare-release.py`, so plants release on their own terms ([ADR-0021](../decisions/adr-0021-seed-only-procedures-stay-home.md)). A plant's own acceptance round is `skill-corpus/release.md`, a different procedure.

## When to apply (`seed-release.when`)

- Every increment of the round is implemented and GREEN, and the round's plan of record shows no open increment.
- Apply it once per round, started by hand. It contains the `tools/prepare-release.py` step, so "run the release" means this procedure.
- A figure or walkthrough that goes stale mid-round waits for this pass. Increments change the doctrine they exist to change; this pass changes everything that describes it.

## Where it runs

Run steps 1 to 6 from the seed tree being released: the round's worktree when the round ran in one, the main checkout otherwise. Run the close-out (step 7) from the steward plant that governs the seed, so its canonize and its roster are in reach. Before step 3, confirm that `docs-librarian` is in that root's harness roster (`delegation.harness-registration`).

## The procedure (`seed-release.flow`)

1. **Fix the range.** The base is the previous release tag, `vPREV` (the `manifest.json` `version` before this round's bump). Run `git diff --name-only vPREV..HEAD`. The changed nodes, tools, checks and installer paths are the doc pass's scope. Hand the list to step 3.
2. **Measure the drift, read-only.** Run `python3 tests/seed-lint.py`. Each drifted mirror prints its `file:line` and the live value. That list, with its count, is the doc pass's worklist. Take every figure from a tool's output.
3. **One documentation pass, one worker.** Route `docs-librarian`. Its write scope is the human docs (README, DOCUMENTATION, INSTALL, `documentation/*`, `integrations/*/README.md`, the `*_PROMPT.md` entry prompts), `manifest.json`, `CHANGELOG.md` and `CLAUDE.md`. The brief carries the range from step 1, the worklist from step 2 and the surface table below. The worker:
   - bumps the version spine first, in one edit: `manifest.json` `version`; the new `CHANGELOG.md` top entry (append-only; use `###` inside it, because `prepare-release.py` ends an entry at the next `## ` line); `Version documented:` in `DOCUMENTATION.md`; `(version X.Y.Z)` in `documentation/README.md`;
   - clears the worklist by setting each figure to the live value its check printed;
   - brings every doc that restates text of a changed node back in line with the node. Doctrine changes count as much as figures: a rewritten rule, a changed voice, a removed or renamed section, a retired mechanism, a corrected stale fact. A retired mechanism leaves every walkthrough that describes it. Find the restatements by searching the human docs for the changed rule's key terms and fact keys, because a walkthrough rarely names its node's file. Each walkthrough keeps its link to its node;
   - confirms that each pointer surface still resolves;
   - reviews each `manifest.json` `role` string against its file's `description:`, and `principles` against the kernel, for every node in the range;
   - catalogs added or removed nodes in `manifest.json`;
   - applies `skills/humanizer` to every human doc it edits, the CHANGELOG entry included. This is the entry's one prose pass: step 5 copies it verbatim. It runs `python3 tools/prose-lint.py --file <f> --against vPREV` on each edited human doc and declares, in its handback, every requirement word it dropped (must, never, may, ...).
   Done when seed-lint is clean and each prose-lint run shows no new strong tell.
4. **Gate.** Run `bash tests/run.sh` from the seed root. Done at exit 0, every step PASS.
5. **Stage the release notes.** Run `python3 tools/prepare-release.py`. It copies the `CHANGELOG.md` entry for the `manifest.json` version, verbatim, into `.github/RELEASE_NOTES.md`, and prints the publish commands; `tests/test_prepare_release.py` holds its extraction and CLI behaviour. Exit 1 is the guard working: no entry, an existing tag, a version that is not semver, or a level-two heading inside the entry that is not a version heading (make it `###`, as step 3 says). The staged file is scaffolding: the next release overwrites it, so it needs no cleanup commit, and a cleanup commit on the default branch would race whatever lands there next.
6. **Commit** the pass and the staged notes together, following the governing plant's commit declaration (`commit_attribution`, `core/method/vcs-posture.md`). The commit stays local. Done when `git status --porcelain` is empty.
7. **Close out through the steward plant's canonize, as written.** One librarian spawn (`protocol.canonize`). The brief forwards the doc pass's handback, the round's session records by path, and the tool and skill candidates. Canonize brings the plant's nodes about the seed current and records the code anchor last, at the commit from step 6; that order keeps the anchor free of release files. A session rooted at the seed alone has no graph, and it records "canonize: no plant graph in this session".
8. **Deliver** (`protocol.deliver`). List every decision that waits on the owner, and print the publish commands from step 5.
9. **Publish only on the owner's explicit go-ahead for this version.** Run `git push`, then `git tag -a vX.Y.Z -m vX.Y.Z && git push origin vX.Y.Z`. Pushing is a publish (`vcs-posture.publish-authorization`). The tag push runs `.github/workflows/release.yml`: it checks the tag against `manifest.json` and runs `gh release create` with the staged file as the body, unedited; `check_workflows` in `tests/seed-lint.py` holds the workflow's shape. It writes no prose of its own, because CI has no access to the judgment `skills/humanizer` and `skill-corpus/discardme.md` require.

## The surfaces (`seed-release.doc-surfaces`)

Each surface is held by the check named here; the check is the home of what it matches. A row held by "this pass" is judgment that no lint can hold, and step 3 covers it.

| Surface | Home | Held by |
|---|---|---|
| `manifest.json` version, catalogs, `tools` map | the bump; the files; `install.sh` placements | `check()`, `check_seed_only_stays_home` |
| CHANGELOG top entry, `.github/RELEASE_NOTES.md` | the entry | `check()`, `prepare-release.py`, `tests/test_prepare_release.py`, `check_workflows` |
| Version, counts and figures in README, DOCUMENTATION, INSTALL, `documentation/*`, `integrations/*/README.md` | the roster, `skills/`, `protocols/`, `check_eager_surface`, `routable_body_figures` | `check_published_figures`, `check_published_counts` |
| Front door anchors, install targets, prose floor | SPEC-0004 | the fd checks; the prose-lint steps for README and DOCUMENTATION |
| Reference frontmatter blocks, triggers, golden rows, `load_when` | node frontmatter, `agents/_routes.golden.tsv` | `check_reference_tables` |
| Kernel roster, anchors, budget | agent frontmatter, `RULE_HOMES` | `check()` |
| GRAPH DISCIPLINE and COMPANION blocks in the briefs | `templates/prompts/graph-session-bootstrap.md` | `check()` byte identity |
| ADR catalog | `docs/decisions/adr-*.md` | `check_decision_index` |
| Walkthroughs in DOCUMENTATION, the references and the READMEs, and any doc that restates a node's rule | each node's body | this pass (step 3) |
| `manifest.json` `role` strings and `principles` | each file's `description:`; the kernel | this pass (step 3) |
| Pointers: CLAUDE.md homes, entry prompts, counts that no check holds | the node or command named in the pointer | this pass (step 3) |
| The steward plant's nodes about the seed | the seed tree | canonize (step 7) |

Out of this pass's scope: `LICENSE` (a legal fact), plant stamps (graft), and routing text (`description:`, `routing_triggers:`, `title:`, `load_when:`), whose home is the node itself.

## One home per fact in the seed's docs (`seed-release.dedupe-rule`)

A doc surface that restates a node's fact is one of three kinds: a mirror held by a check, a file a tool generates, or a pointer to the home (one sentence plus the path, node id or fact key). A walkthrough for people may sit on top of a mirror or a pointer; it links its home, and this pass keeps it current. Add a new restatement as one of the three kinds in the change that adds it. A new mirror enters the surface table above, with its check, in the same change.

## Reference files

- `CLAUDE.md` (Release, Canonical homes, Conventions)
- `tools/prepare-release.py`, `.github/workflows/release.yml`, `tests/test_prepare_release.py`
- `tests/seed-lint.py`, `tools/gate-registry.py`, `tools/prose-lint.py`
- `protocols/canonize.md`, `protocols/deliver.md`, `skills/humanizer/SKILL.md`, `core/method/vcs-posture.md`
