# AGENTS.md

This repository is for a portfolio-grade ML engineering project focused on retrospective ICU/sepsis analytics QA over structured data.

## Working principles

- Preserve modularity. Keep planning, validation, execution, explanation, and evaluation separated.
- Do not fabricate outputs, metrics, model behavior, or dataset characteristics.
- Keep planner output strictly structured and schema-constrained.
- Keep numeric computation deterministic and local.
- Do not let the LLM perform arithmetic or claim to have executed analytics.
- Update docs whenever code or architecture changes.
- Add tests for critical logic, especially schema validation and execution behavior.

## Architecture constraints

- The planner may use a remote LLM, but only as a structured planning service.
- Never send raw patient rows to the planner.
- The execution engine is the source of truth for all computed values.
- The explanation layer may summarize only computed results.
- Do not add diagnosis, treatment recommendation, causal inference, or bedside decision support features to v1.

## Coding expectations

- Prefer small, readable, typed Python modules.
- Make assumptions explicit in code comments or docs.
- Leave `TODO` markers where future implementation is intentionally deferred.
- Keep interfaces deterministic and testable.
- Reject unsupported or ambiguous requests cleanly.

## Documentation expectations

- Keep [README.md](/Volumes/Tauntaun/ClinicalQA/README.md) aligned with actual implementation status.
- Keep schema changes synchronized with [docs/planner_schema.md](/Volumes/Tauntaun/ClinicalQA/docs/planner_schema.md).
- Reflect new supported operations or metrics in [docs/evaluation_plan.md](/Volumes/Tauntaun/ClinicalQA/docs/evaluation_plan.md) and [docs/requirements.md](/Volumes/Tauntaun/ClinicalQA/docs/requirements.md).
