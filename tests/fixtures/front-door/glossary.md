# Documentation

A synthetic glossary and enforcement table for tests/test-seed-lint.sh.

<a id="glossary"></a>
## 15. Glossary

### plant
<a id="term-plant"></a>
- **Here:** A repository the seed was installed into.
- **Implemented at:** `install.sh`, `protocols/grow.md`. An install produces `.cypress/seed.json` (`write_seed_stamp`).

<a id="enforcement"></a>
## 17. What is enforced, and how

| Mechanism | Artifact | Class |
|---|---|---|
| <a id="enf-backup-before-replace"></a>A replaced file is kept beside itself | `install.sh` (`place_file`) | **hard** |
