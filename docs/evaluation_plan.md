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
- repair success rate if a repair loop is added

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

## Phase 1 status

Only starter metric definitions and benchmark scaffolding are implemented in code. Full benchmark generation remains a TODO.
