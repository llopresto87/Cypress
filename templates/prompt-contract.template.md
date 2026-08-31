<!--
Template: prompt-contract.template.md
Authored by: data-ml, security
Lives at: docs/graph/prompts/prompt-contracts/PROMPT-NNNN-<slug>.md
Used: on every active LLM/VLM prompt
Filled by copying this template into the target path and replacing
every <placeholder>. Stable section numbers must not be renumbered;
agents and tooling index into them.
-->

# Prompt Contract: <name>

## 0. Metadata
- **ID:** PROMPT-NNNN
- **Status:** draft | active | deprecated
- **Owner:** <agent or person>
- **Date:** YYYY-MM-DD
- **Version:** <semver-ish, bump on prompt change>
- **Related spec:** <SPEC-NNNN-*>
- **Related eval:** docs/graph/evaluations/<task>.md

## 1. Purpose
What the model is being asked to do, in one sentence.

## 2. Model role
The role the model adopts (system message gist).

## 3. Inputs
- **User inputs:**
- **Context sources** (retrieved docs, user data, etc.):
- **System inputs** (date, locale, feature flags):

## 4. Tool permissions
- **Tools the model may call:**
- **Argument validation rules** (deterministic code that runs before
  the tool actually fires):

## 5. Output schema
Structured output format, when applicable.

```yaml
type: object
required: [answer, citations]
fields:
  answer: { type: string }
  citations: { type: array, of: object,
               item: { url: string, snippet: string } }
```

## 6. Validation rules
What deterministic code asserts about the model's output before the
output reaches the user or another tool.

## 7. Refusal or escalation conditions
When the model should refuse, ask for confirmation, or escalate to a
human. Map to spec failure modes.

## 8. Privacy boundaries
- **Sensitive data that may appear in the prompt:**
- **Redaction rules:**
- **Retention** (provider-side and ours):

## 9. Safety boundaries
- **Adversarial inputs we test for:** prompt injection (direct,
  indirect via retrieved content), tool hijacking, data
  exfiltration, jailbreaking, refusal evasion.
- **Controls:** schema validation, allow-listed tools per task,
  human-in-the-loop gates.

## 10. Evaluation cases
Reference to `docs/graph/evaluations/<task>.md`. Minimum coverage:
- Golden-path cases
- Edge cases
- Regression cases from prior failures
- Adversarial prompt-injection cases
- Privacy leakage cases
- Tool-misuse cases
- Hallucination checks
- Latency and cost measurements

## 11. Version history
| Version | Date | Change | Eval delta |
|---|---|---|---|

## 12. Prompt body
The prompt itself, fenced. Treat as code — diffable, reviewable,
testable.

```text
<the actual prompt>
```
