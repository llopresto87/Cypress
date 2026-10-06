#!/usr/bin/env python3
"""tools/corpus-match.py's own regression (SPEC-0001 §6, selective placement).

The matcher reads a project's manifests and proposes the corpus pages they
match; `install.sh --expertise propose` prints its output and writes nothing.
These cases run it against the synthetic manifests and the synthetic corpus
subset under tests/fixtures/corpus-placement/, never a real plant's, each in a
disposable copy so the fixture is never written.

Stdlib unittest, like every other suite here; no third-party imports.
"""

from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SEED = HERE.parent
TOOL = SEED / "tools" / "corpus-match.py"
FIXTURE = HERE / "fixtures" / "corpus-placement"


def tree_digest(root: Path) -> str:
    out = hashlib.sha256()
    for base, dirs, files in sorted(os.walk(root)):
        dirs.sort()
        for name in sorted(dirs + files):
            path = Path(base) / name
            out.update(str(path.relative_to(root)).encode())
            if path.is_file():
                out.update(path.read_bytes())
    return out.hexdigest()


def run(project: Path, seed: Path = FIXTURE / "seed"):
    return subprocess.run(
        [sys.executable, "-B", str(TOOL), str(project), "--seed", str(seed)],
        capture_output=True, text=True)


class CorpusMatch(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.plant = self.tmp / "plant"
        shutil.copytree(FIXTURE / "plant", self.plant)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_proposes_every_ecosystem_and_its_stack_pages(self):
        """EXPERTISE_PROPOSAL_WRITES_NOTHING: one line per matching page, in the
        §6 form, sorted by id and unique; a skill or tool page names the library
        page its `stack:` matched through; pages no manifest names (a platform
        page, an unmatched library, a stack-neutral tool, a flat skill page) are
        never proposed; the project is byte-identical afterwards."""
        self.assertTrue(TOOL.is_file(), f"{TOOL} does not exist")
        before = tree_digest(self.plant)
        res = run(self.plant)
        self.assertEqual(res.returncode, 0, res.stderr)
        lines = res.stdout.splitlines()
        ids = [ln.split("  ", 1)[0] for ln in lines]
        self.assertEqual(ids, sorted(set(ids)), "lines are not sorted by id and unique")
        expected = {
            "library-corpus/cli/maven": "pom.xml: (present)",
            "library-corpus/container/docker-compose": "docker-compose.yml: (present)",
            "library-corpus/container/swift-cache":
                "docker-compose.yml: registry.example.test/team/swift-cache:7.2@sha256:0000",
            "library-corpus/galaxy/harbor.tools": "ansible/requirements.yml: harbor.tools",
            "library-corpus/language/dotnet": "app/App.csproj: (present)",
            "library-corpus/language/flutter": "mobile/pubspec.yaml: flutter",
            "library-corpus/language/nodejs": "package.json: (present)",
            "library-corpus/language/python": None,
            "library-corpus/language/typescript": "package.json: typescript",
            "library-corpus/maven/lumen-core": "pom.xml: org.example.lumen:lumen-core-starter-web",
            "library-corpus/maven/quarry": "pom.xml: org.example.build:quarry-maven-plugin",
            "library-corpus/maven/tidewater": "pom.xml: io.tidewater:tw-client",
            "library-corpus/npm/orbit-forms": "package.json: @orbit/forms",
            "library-corpus/npm/ripple": "package.json: Ripple",
            "library-corpus/nuget/Fabrikam.Telemetry": "app/App.csproj: fabrikam.telemetry",
            "library-corpus/pub/pebble_store": "mobile/pubspec.yaml: pebble_store",
            "library-corpus/pypi/data-loom": "pyproject.toml: Data.Loom[extra]>=1.2",
            "library-corpus/pypi/swift-cache": "requirements.txt: Swift_Cache>=2.0",
            "skill-corpus/maven/lumen-upgrade": "stack: library-corpus/maven/lumen-core",
            "tool-corpus/ops/orbit-form-linter": "stack: library-corpus/npm/orbit-forms",
        }
        self.assertEqual(set(ids), set(expected), res.stdout)
        by_id = dict(ln.split("  ", 1) for ln in lines)
        for cid, entry in expected.items():
            if entry is not None:
                self.assertEqual(by_id[cid], entry, f"{cid}: {by_id[cid]!r}")
        self.assertRegex(by_id["library-corpus/language/python"],
                         r"^(requirements\.txt|pyproject\.toml): \(present\)$")
        self.assertEqual(tree_digest(self.plant), before, "the matcher wrote into the project")

    def test_unreadable_manifest_is_named_and_skipped(self):
        """EXPERTISE_MANIFEST_UNREADABLE: a package.json that is not JSON and a
        pom.xml that is not UTF-8 are each named on one line with the reason;
        the proposal is made from every other manifest and the run exits 0."""
        (self.plant / "package.json").write_text("{ not json", encoding="utf-8")
        (self.plant / "pom.xml").write_bytes(b"<project>\xff\xfe</project>")
        res = run(self.plant)
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertRegex(res.stderr, r"package\.json.*not valid JSON")
        self.assertRegex(res.stderr, r"pom\.xml.*not UTF-8")
        ids = [ln.split("  ", 1)[0] for ln in res.stdout.splitlines()]
        self.assertIn("library-corpus/pypi/swift-cache", ids)
        self.assertIn("library-corpus/nuget/Fabrikam.Telemetry", ids)
        self.assertNotIn("library-corpus/npm/orbit-forms", ids)
        self.assertNotIn("library-corpus/maven/lumen-core", ids)

    def test_empty_proposal_is_never_silent(self):
        """EXPERTISE_PROPOSAL_WRITES_NOTHING: a project whose manifests match
        nothing gets one line saying so, and exit 0."""
        empty = self.tmp / "empty"
        empty.mkdir()
        (empty / "README.md").write_text("nothing to match\n", encoding="utf-8")
        res = run(empty)
        self.assertEqual(res.returncode, 0, res.stderr)
        lines = res.stdout.splitlines()
        self.assertEqual(len(lines), 1, res.stdout)
        self.assertIn("no corpus page", lines[0])

    def write(self, rel: str, text: str, root: Path = None) -> Path:
        path = (root or self.tmp / "project") / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def proposal(self, project: Path, seed: Path = FIXTURE / "seed") -> dict:
        res = run(project, seed)
        self.assertEqual(res.returncode, 0, res.stderr)
        if "no corpus page" in res.stdout:
            return {}
        return dict(ln.split("  ", 1) for ln in res.stdout.splitlines())

    def test_scratch_copies_and_foreign_dirs_are_not_read(self):
        """EXPERTISE_PROPOSAL_WRITES_NOTHING reads the project's own manifests:
        a scratch directory, a graft backup or snapshot, a `.bak-` copy, a
        virtual environment, a build output, an agent host's own directory, a
        nested plant (its own seed stamp) and a symlinked directory are never walked, so neither their
        pages nor their evidence lines reach the proposal."""
        project = self.tmp / "project"
        self.write("package.json", '{"dependencies": {"ripple": "1"}}')
        npm = lambda name: '{"dependencies": {"%s": "1"}}' % name
        self.write(".tmp/verify-1/package.json", npm("ripple"))
        self.write(".tmp/verify-1/web/package.json", npm("@orbit/forms"))
        self.write(".graft-backup-20260101/requirements.txt", "swift-cache\n")
        self.write(".graft-snapshot-20260101/requirements.txt", "data-loom\n")
        self.write("service.bak-20260101/pom.xml",
                   "<project><dependencies><dependency><artifactId>tw-client</artifactId>"
                   "<groupId>io.tidewater</groupId></dependency></dependencies></project>")
        self.write(".venv-tools/lib/pyproject.toml", '[project]\ndependencies = ["data-loom"]\n')
        self.write("dist/package.json", npm("@orbit/forms"))
        for host in (".opencode", ".claude", ".codex", ".prime/agent"):
            self.write(f"{host}/package.json", npm("@orbit/forms"))
        self.write("copy/.cypress/seed.json", '{"seed": "cypress"}')
        self.write("copy/requirements.txt", "swift-cache\n")
        elsewhere = self.write("pub/pubspec.yaml", "name: other\ndependencies:\n  pebble_store: ^1.0\n",
                               root=self.tmp / "elsewhere")
        os.symlink(elsewhere.parent, project / "linked")
        got = self.proposal(project)
        self.assertEqual(got, {"library-corpus/language/nodejs": "package.json: (present)",
                               "library-corpus/npm/ripple": "package.json: ripple"}, got)

    def test_manifest_rules_propose_their_pages(self):
        """EXPERTISE_PROPOSAL_WRITES_NOTHING, the manifest rules in one small
        project built here, each rule's manifest proposing pages no other one
        does (a page proposed twice keeps the evidence of the first path):
        - maven: a `<family>-starter-<module>` entry proposes the umbrella and the
          module's page, a `<base>-<flavour>-starter-<area>-<store>` entry the page
          of `<base>-<area>-<store>`, and a starter of the coordinates a page names
          as its own in `## What it is` proposes that page;
        - Dockerfile: every stage's FROM image proposes its container, language or
          build-tool page and the file the container-engine page; a stage alias,
          `scratch` and an ARG-named image propose nothing; a variable registry or
          tag does not hide the image; a `Containerfile` is read the same way, and
          a `dotnet/` image proposes the dotnet page;
        - an `azure-pipelines*.yml` proposes the pipeline-schema platform page, and
          a `dotnet-tools.json` the nuget page of each tool it declares."""
        project = self.tmp / "project"
        self.write("x-api/pom.xml", """<project><dependencies>
  <dependency><groupId>org.example.lumen</groupId><artifactId>lumen-cloud-starter-relay</artifactId></dependency>
  <dependency><groupId>org.example.lumen</groupId><artifactId>lumen-boot-starter-data-vault</artifactId></dependency>
  <dependency><groupId>org.example.lumen</groupId><artifactId>lumen-cloud-starter-beacon</artifactId></dependency>
</dependencies></project>""")
        self.write("svc/Dockerfile", """# syntax=docker/dockerfile:1
ARG BASE_IMAGE=quay.example.test/x/unmatched:1
FROM --platform=$BUILDPLATFORM maven:3.9-runtime-base-17 AS build
FROM node:20-alpine as ui
FROM build AS test
FROM ${BASE_IMAGE}
FROM scratch AS empty
from ${REGISTRY}/team/swift-cache:${TAG}
FROM python:3.12-slim
FROM registry.example.test/base/runtime-base:17-jre-alpine@sha256:0000
""")
        self.write("web/Containerfile", "FROM mcr.microsoft.com/dotnet/aspnet:8.0\n")
        self.write("ci/azure-pipelines.release.yml", "trigger: none\nstages: []\n")
        self.write(".config/dotnet-tools.json",
                   '{"version": 1, "tools": {"fabrikam.telemetry": {"version": "1.0.0"}}}')
        lumen = "x-api/pom.xml: org.example.lumen:lumen-"
        self.assertEqual(self.proposal(project), {
            "library-corpus/cli/maven": "svc/Dockerfile: maven:3.9-runtime-base-17",
            "library-corpus/container/docker": "svc/Dockerfile: (present)",
            "library-corpus/container/runtime-base":
                "svc/Dockerfile: registry.example.test/base/runtime-base:17-jre-alpine@sha256:0000",
            "library-corpus/container/swift-cache": "svc/Dockerfile: ${REGISTRY}/team/swift-cache:${TAG}",
            "library-corpus/language/dotnet": "web/Containerfile: mcr.microsoft.com/dotnet/aspnet:8.0",
            "library-corpus/language/nodejs": "svc/Dockerfile: node:20-alpine",
            "library-corpus/language/python": "svc/Dockerfile: python:3.12-slim",
            "library-corpus/maven/beacon-trace": lumen + "cloud-starter-beacon",
            "library-corpus/maven/lumen-cloud": lumen + "cloud-starter-relay",
            "library-corpus/maven/lumen-cloud-relay": lumen + "cloud-starter-relay",
            "library-corpus/maven/lumen-data-vault": lumen + "boot-starter-data-vault",
            "library-corpus/nuget/Fabrikam.Telemetry": ".config/dotnet-tools.json: fabrikam.telemetry",
            "library-corpus/platform/azure-pipelines-yaml": "ci/azure-pipelines.release.yml: (present)",
        })

    # The cases below match against the seed's own library-corpus/, not the
    # fixture subset. The projects are still synthetic and built in the test.

    def proposed_from_seed(self, files: dict) -> dict:
        project = self.tmp / f"seeded-{len(list(self.tmp.iterdir()))}"
        project.mkdir()
        for rel, text in files.items():
            self.write(rel, text, root=project)
        return self.proposal(project, SEED)

    def test_seed_pages_are_proposed_by_their_triggers(self):
        """LANGUAGE_DECLARATION_PROPOSES_ITS_PAGE, OWN_PACKAGE_LIST_PROPOSES_ITS_PAGE
        and PACKAGELESS_PAGE_PROPOSED_BY_ITS_TRIGGER, over the seed's own corpus:
        each row is one project holding one trigger the named page states for
        itself, so a page renamed or a trigger dropped from its text shows here.
        One row per mechanism, not per name a page lists (a list entry is data).
        - java: the Java level declared in a build descriptor, each form a pom.xml
          or a Gradle build sets it by; a pom.xml that sets no level (an
          aggregator) proposes no language/java;
        - dart: a pubspec `environment:` `sdk:` constraint, also beside Flutter;
        - own-package lists: npm/stomp-sockjs, pub/flutter_bloc (both sections);
        - platform pages: proxmox-ve by an Ansible collection and a Python
          requirement, bitbucket-pipelines by its file;
        - scanners: trivy and gitleaks by an official image (compose, CI step), a
          GitHub Action, a config file and a pre-commit hook id."""
        pom = "<project><modelVersion>4.0.0</modelVersion>%s</project>"
        props = pom % "<properties>%s</properties>"
        plugin = pom % ("<build><plugins><plugin><groupId>org.apache.maven.plugins</groupId>"
                        "<artifactId>maven-compiler-plugin</artifactId><configuration>%s"
                        "</configuration></plugin></plugins></build>")
        toolchain = "java {\n    toolchain {\n        languageVersion = JavaLanguageVersion.of(21)\n    }\n}\n"
        compose = "services:\n  scan:\n    image: %s\n"
        action = "on: push\njobs:\n  scan:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: %s\n"
        java, dart = "library-corpus/language/java", "library-corpus/language/dart"
        trivy, gitleaks = "library-corpus/cli/trivy", "library-corpus/cli/gitleaks"
        rows = [  # (page, manifest, text, what the evidence names)
            (java, "pom.xml", props % "<java.version>21</java.version>", "java.version"),
            (java, "pom.xml", props % "<maven.compiler.release>17</maven.compiler.release>",
             "maven.compiler.release"),
            (java, "pom.xml", props % ("<maven.compiler.source>11</maven.compiler.source>"
                                       "<maven.compiler.target>11</maven.compiler.target>"), "maven.compiler."),
            (java, "pom.xml", plugin % "<release>21</release>", "release"),
            (java, "pom.xml", plugin % "<source>1.8</source><target>1.8</target>", "source"),
            (java, "build.gradle", "plugins { id 'java' }\n" + toolchain, "languageVersion"),
            (java, "build.gradle.kts", "plugins { java }\n" + toolchain, "languageVersion"),
            (java, "build.gradle", "java {\n    sourceCompatibility = JavaVersion.VERSION_17\n"
             "    targetCompatibility = JavaVersion.VERSION_17\n}\n", "Compatibility"),
            (dart, "pubspec.yaml", "name: tool\nenvironment:\n  sdk: ^3.4.0\n", "sdk"),
            (dart, "mobile/pubspec.yaml", "name: app\nenvironment:\n  sdk: '>=3.4.0 <4.0.0'\n"
             "dependencies:\n  flutter:\n    sdk: flutter\n", "sdk"),
            ("library-corpus/npm/stomp-sockjs", "web/package.json",
             '{"dependencies": {"@stomp/stompjs": "1"}}', "@stomp/stompjs"),
            ("library-corpus/pub/flutter_bloc", "pubspec.yaml", "name: app\ndependencies:\n  bloc: ^9.0.0\n", "bloc"),
            ("library-corpus/pub/flutter_bloc", "pubspec.yaml",
             "name: app\ndev_dependencies:\n  bloc_test: ^9.0.0\n", "bloc_test"),
            ("library-corpus/platform/proxmox-ve", "ansible/requirements.yml",
             "collections:\n  - name: community.proxmox\n", "community.proxmox"),
            ("library-corpus/platform/proxmox-ve", "requirements.txt", "proxmoxer>=2.0\n", "proxmoxer"),
            ("library-corpus/platform/bitbucket-pipelines", "bitbucket-pipelines.yml",
             "pipelines:\n  default:\n    - step:\n        script:\n          - make test\n", "(present)"),
            (trivy, "compose.yaml", compose % "aquasec/trivy:0.50.0", "aquasec/trivy:0.50.0"),
            (trivy, "bitbucket-pipelines.yml", "pipelines:\n  default:\n    - step:\n"
             "        image: aquasec/trivy:latest\n        script:\n          - trivy fs .\n",
             "aquasec/trivy:latest"),
            (trivy, ".github/workflows/scan.yml", action % "aquasecurity/trivy-action@0.20.0",
             "aquasecurity/trivy-action@0.20.0"),
            (trivy, "trivy.yaml", "severity:\n  - HIGH\n", "(present)"),
            (gitleaks, "docker-compose.yml", compose % "ghcr.io/gitleaks/gitleaks:latest",
             "ghcr.io/gitleaks/gitleaks:latest"),
            (gitleaks, ".github/workflows/scan.yml", action % "gitleaks/gitleaks-action@v2",
             "gitleaks/gitleaks-action@v2"),
            (gitleaks, ".gitleaks.toml", "[extend]\nuseDefault = true\n", "(present)"),
            (gitleaks, ".pre-commit-config.yaml", "repos:\n  - repo: https://github.com/gitleaks/gitleaks\n"
             "    rev: v8.0.0\n    hooks:\n      - id: gitleaks-docker\n", "gitleaks-docker"),
        ]
        for cid, manifest, text, names in rows:
            with self.subTest(f"{cid.rsplit('/', 1)[-1]} via {manifest}: {names}"):
                got = self.proposed_from_seed({manifest: text})
                self.assertIn(cid, got, got)
                where, evidence = got[cid].split(": ", 1)
                self.assertEqual(where, manifest, got[cid])
                self.assertIn(names, evidence, got[cid])
        with self.subTest("dart beside flutter"):
            self.assertIn("library-corpus/language/flutter",
                          self.proposed_from_seed({"m/pubspec.yaml": rows[9][2]}))
        with self.subTest("pom.xml with no language level"):
            got = self.proposed_from_seed({"pom.xml": pom % (
                "<groupId>org.example</groupId><artifactId>parent</artifactId>"
                "<packaging>pom</packaging><modules><module>api</module></modules>")})
            self.assertNotIn(java, got, "a pom.xml that declares no Java level proposed language/java")

    def synthetic_seed(self, pages: dict) -> Path:
        seed = self.tmp / f"seed-{len(list(self.tmp.iterdir()))}"
        for cid, text in pages.items():
            self.write(f"library-corpus/{cid}.md", text, root=seed)
        return seed

    def test_page_matches_the_packages_it_lists_as_its_own_in_any_ecosystem(self):
        """OWN_PACKAGE_LIST_PROPOSES_ITS_PAGE and CITED_PACKAGE_PROPOSES_NOTHING,
        the own-package list (§6): in a page's `## What it is`, a list item that
        opens with a package's registry name in backticks and a colon makes that
        package the page's own, in any key, read the way the key's row reads a
        manifest entry; the evidence names the manifest and the entry. Every
        other mention is a citation and proposes nothing: running prose, an item
        that opens with something else, a later section.

        Over a synthetic corpus built in the test, so the convention is held
        apart from any real page's wording: an npm page lists `@comet/core` and
        `Comet-Rx` (met by `@comet/core` and `comet-rx`), a pypi page lists
        `Loom_Extras` (met by `loom.extras`); the npm page cites `tidal-runtime`
        in prose, `halo-peer` in an item opening with a bold label and
        `later-lib` in a later section, and none of the three proposes it.

        Over the seed's own corpus, the listed packages of npm/stomp-sockjs and
        pub/flutter_bloc are rows of the seed-trigger table below. A package the section cites
        as a dependency, peer or wrapped library proposes nothing (rxjs's
        `tslib`, postcss's `nanoid`, bootstrap's `@popperjs/core`,
        ng2-pdf-viewer's `pdfjs-dist`). The maven own-coordinate form, and its
        known false positive (the MariaDB driver entry
        `org.mariadb.jdbc:mariadb-java-client` proposes maven/mysql-connector-j,
        whose `## What it is` names that driver as the alternative), is §6's
        transitional exception and not asserted here."""
        seed = self.synthetic_seed({
            "npm/comet": "# comet\n\n## What it is\nThe Comet client family. It runs on "
                         "`tidal-runtime`, its one runtime dependency.\n\n"
                         "- `@comet/core`: the client.\n"
                         "- `Comet-Rx`: the client as observables.\n"
                         "- **Peer:** `halo-peer`, which the host app installs.\n\n"
                         "## Interop\n- `later-lib`: a library Comet is often used beside.\n",
            "pypi/loom": "# loom\n\n## What it is\nThe Loom data toolkit.\n\n"
                         "- `Loom_Extras`: optional readers.\n",
        })
        own = [("@comet/core", "package.json", '{"dependencies": {"@comet/core": "1"}}',
                "library-corpus/npm/comet"),
               ("comet-rx", "package.json", '{"devDependencies": {"comet-rx": "1"}}',
                "library-corpus/npm/comet"),
               ("loom.extras", "requirements.txt", "loom.extras>=1.0\n", "library-corpus/pypi/loom")]
        for entry, manifest, text, cid in own:
            with self.subTest(f"listed, synthetic: {entry}"):
                project = self.tmp / f"own-{len(list(self.tmp.iterdir()))}"
                self.write(manifest, text, root=project)
                got = self.proposal(project, seed)
                self.assertEqual(got.get(cid), f"{manifest}: {entry}", got)
        for name in ("tidal-runtime", "halo-peer", "later-lib"):
            with self.subTest(f"cited, synthetic: {name}"):
                project = self.tmp / f"cited-{len(list(self.tmp.iterdir()))}"
                self.write("package.json", '{"dependencies": {"%s": "1"}}' % name, root=project)
                self.assertNotIn("library-corpus/npm/comet", self.proposal(project, seed))
        with self.subTest("a cited dependency is not the page's own"):
            got = self.proposed_from_seed({"package.json": '{"dependencies": {"tslib": "2", '
                                           '"nanoid": "3", "@popperjs/core": "2", "pdfjs-dist": "4"}}'})
            for cid in ("npm/rxjs", "npm/postcss", "npm/bootstrap", "npm/ng2-pdf-viewer"):
                self.assertNotIn(f"library-corpus/{cid}", got, got)


if __name__ == "__main__":
    unittest.main()
