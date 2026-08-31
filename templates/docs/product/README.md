# Product

User-facing requirements, flows, and acceptance criteria. The section
skeletons below are the contract for each file; `product` (the agent)
authors and maintains them.

- `requirements.md` — primary user, problem, outcome, success
  criteria, non-goals, constraints, roadmap. Sections:

  ```markdown
  ## Primary user
  ## User problem (in their words)
  ## Desired outcome
  ## Current workaround
  ## Success criteria (measurable)
  ## Non-goals
  ## Constraints
  ## Risks
  ## Roadmap (priorities beyond the first slice)
  ```

- `user-flows.md` — flow-by-flow walkthrough. Per flow:

  ```markdown
  ## Flow: <name>

  ### Entry point
  ### User intent
  ### System response
  ### Success state
  ### Empty state
  ### Loading state
  ### Error state
  ### Permission state
  ### Recovery path
  ### Accessibility considerations
  ```

- `acceptance-criteria.md` — rolled-up acceptance criteria from
  every active spec, for stakeholder review.
