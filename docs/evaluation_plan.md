# Evaluation Plan

## Planner evaluation

Measure:

- JSON validity rate
- schema-valid plan rate
- exact plan match
- slot-level accuracy
- safe rejection rate for unsupported questions

## Execution evaluation

Measure:

- execution success rate
- failure-type breakdown
- validator rejection breakdown
- repair success rate
- schema-hint enforcement rate for invalid planner outputs

## End-to-end evaluation

Compare predicted-plan execution results against deterministic ground truth:

- exact table match
- numeric match within tolerance
- ranking correctness

## Robustness evaluation

Measure:

- paraphrase consistency
- ambiguity handling
- clarification behavior
- unsupported-query rejection quality

## Evaluation assets

Primary evaluation data should come from the semi-synthetic generation pipeline, augmented later with manually reviewed challenge cases for ambiguity and safety.

## Current status

The codebase now includes:

- planner parsing and bounded repair-loop support
- schema-aware validation with column-level operation hints
- deterministic execution for filters, grouped aggregations, ranking, and basic cohort comparisons
- end-to-end query flow tests

Full benchmark generation and large-scale evaluation assets remain TODO.
