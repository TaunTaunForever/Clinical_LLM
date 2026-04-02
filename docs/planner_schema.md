# Planner Schema

## Purpose

The planner must output a structured JSON analysis plan only. The schema exists to constrain supported operations and prevent free-form or partially specified analysis requests from reaching execution.

## Top-level fields

- `intent`: short label for the user goal
- `analysis_type`: supported analysis family
- `select`: columns or derived fields to project
- `filters`: list of filter conditions
- `group_by`: columns used for grouping
- `aggregations`: aggregation specs
- `comparisons`: optional cohort comparison specs
- `order_by`: sort directives
- `limit`: row limit for ranked outputs
- `requires_clarification`: whether the request is too ambiguous to execute safely
- `confidence`: planner self-reported confidence between 0 and 1
- `notes`: optional planner notes for traceability

## Supported aggregations

- `count`
- `mean`
- `median`
- `std`
- `min`
- `max`
- `proportion`
- `mortality_rate`
- `survival_rate`

## Validation expectations

The validator should reject:

- unsupported columns
- unsupported operators
- malformed sort specifications
- invalid aggregation names
- plans that mix incompatible clauses
- plans with missing required fields

## Prompting rules

The planner prompt should:

- include schema metadata only
- require JSON-only output
- forbid unsupported columns
- forbid numerical computation
- ask for clarification when the question is ambiguous

## Phase 1 note

The codebase includes a JSON schema dictionary and typed dataclasses aligned to this document, but real planner API integration is still a TODO.
