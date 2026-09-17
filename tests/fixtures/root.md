---
id: root
tier: 2
kind: root
title: Root project map
owns:
  - root.purpose
requires:
peers:
libraries:
artifacts:
  - architecture/README.md
load_when:
  - "orient in this project"
est_tokens: 85
---

# Root

This node owns the project map and routes deeper knowledge.

<!-- est_tokens measures the WHOLE file, frontmatter included, since
SPEC-0001-gate-assertion-floor GRAPH_LINT_BUDGET_COUNTS_FRONTMATTER. It is an
input here, not an assertion; see tests/test-graph-artifacts.sh. -->
