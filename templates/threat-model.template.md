<!--
Template: threat-model.template.md
Authored by: security
Lives at: docs/graph/decisions/threat-model-<feature>.md
Used: whenever a sensitive feature is being designed
Filled by copying this template into the target path and replacing
every <placeholder>. Stable section numbers must not be renumbered;
agents and tooling index into them.
-->

# Threat Model: <feature>

## 0. Metadata
- **Feature:** <name>
- **Related spec:** <SPEC-NNNN-*>
- **Related ADR:** <adr-NNNN-*>
- **Date:** YYYY-MM-DD
- **Owner:** `security`
- **Status:** draft | active | superseded

## 1. Assets
What we are protecting. Tangible (user records, payment data, model
weights, secrets) and intangible (user trust, regulatory standing).

## 2. Actors
- **Legitimate:** end users, admins, integrators, internal services.
- **Adversarial:** unauthenticated attackers, authenticated abusers,
  insiders, supply-chain attackers, scraping bots, model-prompt
  attackers.

For each actor, name the capabilities they bring and the goals they
have.

## 3. Trust boundaries
Where data crosses an authority change. Examples:
- Public internet → load balancer.
- Web tier → service tier.
- Service tier → database.
- Service tier → third-party API.
- Service tier → LLM provider.
- User-uploaded file → parser.
- Retrieved document → model prompt.

## 4. Entry points
Every place data enters the system. Inputs the architecture allows
the attacker to influence.

## 5. Data flows
For each entry point, where does the data go and how does it
transform? Cross-link to spec §6 (Data shapes).

## 6. Abuse cases

For each plausible abuse, the attacker's goal and the path they
would take. Include AI-specific abuses when LLM/VLM is involved:

- Prompt injection (direct from user, indirect via retrieved
  content).
- Tool hijacking (the model is steered to call a tool against the
  user's interest).
- Data exfiltration (the model is asked to leak context, secrets,
  or other users' data).
- Hallucinated authority (the model claims permissions it doesn't
  have).
- Adversarial inputs to vision/audio models.

## 7. Security controls
For each abuse case, the controls that stop it. Each control names
the spec contract or test that proves it works.

| Abuse case | Control | Verification |
|---|---|---|

## 8. Privacy controls
- Minimization (what we don't collect).
- Redaction (what we strip before logging or persisting).
- Retention (when we delete).
- Access (who can see what).

## 9. Detection and logging
- What we log on each abuse case (with redaction).
- What alert fires on what threshold.
- Audit trail completeness.

## 10. Residual risk
What we cannot fully control and why we accept it (or what the
escalation path is if it materializes).

## 11. Verification plan
- Tests added to the suite for each abuse case.
- Scans added to CI (dependency, secret, static analysis).
- AI red-team eval cases added to `docs/graph/evaluations/`.
- Manual review checkpoints.

## 12. Changelog
- YYYY-MM-DD — created
- YYYY-MM-DD — added abuse case <slug> after incident <ref>
