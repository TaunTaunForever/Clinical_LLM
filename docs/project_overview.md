# Project Overview

## Objective

Build a hybrid analytics QA system over retrospective ICU/sepsis tabular data. The user asks a natural-language question, the system converts it into a structured analysis plan, executes that plan locally and deterministically, and returns a grounded result.

## Intended user journey

1. User asks an analytics question such as "What was the mortality rate among septic shock patients grouped by age band?"
2. Planner produces a JSON analysis plan using schema metadata and allowed operations.
3. Validator checks the plan for schema compliance and unsupported requests.
4. Execution engine runs the plan over a local clinical dataset.
5. Optional explanation layer summarizes the returned result table.

## Safety framing

- This is retrospective clinical analytics, not clinical advice.
- The system must not recommend treatment or diagnose disease.
- The explanation layer must avoid causal claims.
- Unsupported questions should be rejected or flagged for clarification.

## Phase 1 deliverable

Phase 1 provides project scaffolding, design docs, typed module boundaries, initial plan validation logic, a deterministic execution prototype, and starter scripts/tests.
