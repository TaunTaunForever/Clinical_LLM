# Requirements

## Functional requirements

The system should:

- accept a natural-language analytics question
- convert that question into a structured JSON plan
- validate the plan against a constrained schema
- execute supported operations deterministically on a local dataset
- return a result table or a clear error
- optionally summarize the computed result without inventing values

## Supported v1 question families

- descriptive summary
- outcome rate
- cohort comparison
- top-risk groups
- feature difference
- distribution query

## Supported v1 operations

- `filter`
- `group_by`
- `aggregate`
- `sort`
- `limit`
- `compare_cohorts`

## Non-functional requirements

- deterministic computation
- local dataset processing
- no raw row transmission to the remote planner
- typed, testable Python modules
- explicit rejection for unsupported plans

## Out of scope for v1

- diagnosis
- treatment recommendations
- bedside decision support
- causal inference claims
- autonomous medical guidance
