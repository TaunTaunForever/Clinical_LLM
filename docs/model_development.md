# Model Development

## Core learning problem

The main ML task is structured prediction:

`question + schema context -> JSON analysis plan`

## Version 1

Use a pretrained instruction-tuned LLM with:

- schema-aware prompting
- JSON-only output contract
- few-shot examples
- strict validation
- optional repair loop

The planner should not compute results. Its job is to choose columns, operations, and analysis structure.

## Version 2

Optionally fine-tune on a semi-synthetic dataset where:

- input is question plus schema context
- target is the gold JSON plan

If fine-tuned, optimize token-level cross-entropy loss and evaluate primarily with task-specific execution-aware metrics.

## Risks

- planner drift from allowed schema
- ambiguity in natural-language cohort definitions
- leakage from overfitting to synthetic phrasing

## TODO

- choose a concrete planner model and API
- define prompt packing budget for schema metadata
- design a repair loop strategy for malformed JSON or unsupported fields
