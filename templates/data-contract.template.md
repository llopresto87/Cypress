<!--
Template: data-contract.template.md
Authored by: data-ml
Lives at: docs/graph/data/data-contracts.md (one section per dataset)
Used: when adding or changing a dataset that other code depends on
Filled by copying this template into the target path and replacing
every <placeholder>. Stable section numbers must not be renumbered;
agents and tooling index into them.
-->

# Data Contract: <name>

## 0. Metadata
- **Dataset:** <canonical name>
- **Status:** draft | active | deprecated
- **Owner:** <agent or team>
- **Date:** YYYY-MM-DD
- **Last reviewed:** YYYY-MM-DD
- **Related spec:** <SPEC-NNNN-*>

## 1. Purpose
Why this dataset exists; who depends on it; what would break if it
went away or went stale.

## 2. Source
Where the data comes from (event stream, table, API, file drop,
scraping pipeline, third party). Cross-link to the upstream's wiki
page in `docs/graph/libraries/` if applicable.

## 3. Schema

```yaml
fields:
  <field>:
    type: <string|number|boolean|timestamp|uuid|...>
    required: <true|false>
    allowed: [<enum if any>]
    description: <one line>
    privacy: public | internal | sensitive | restricted
```

## 4. Quality checks

The assertions that gate ingest. Each one is a runnable check.

| Check | Threshold | Action on failure |
|---|---|---|
| row_count_min  | >= N per day | alert; pause downstream |
| null_rate(<f>) | <= 0.01      | alert; quarantine batch |
| schema_match   | 100%         | reject batch            |
| distribution_drift(<f>) | < N | alert; review           |

## 5. Freshness
- **Expected cadence:** <e.g. hourly, daily>
- **Stale threshold:** <after which downstream alerts>

## 6. Privacy classification
- **Overall classification:** public | internal | sensitive | restricted
- **PII fields:** <list>
- **Retention:** <duration; deletion procedure>
- **Regional restrictions:** <data residency, GDPR, etc.>

## 7. Access rules
- **Reader roles / scopes:**
- **Writer roles / scopes:**
- **Audit:** what is logged on access

## 8. Downstream consumers
- <Consumer 1>: how they use this dataset
- <Consumer 2>: how they use this dataset

Breaking changes to this contract must be coordinated with all
listed consumers and announced via the changelog.

## 9. Failure handling
- **Ingest failure:** what happens (retry, dead-letter, alert)
- **Quality-check failure:** what happens
- **Downstream contract failure:** what happens

## 10. Changelog
- YYYY-MM-DD — created
- YYYY-MM-DD — added field <name>
- YYYY-MM-DD — tightened null_rate threshold to <N>
