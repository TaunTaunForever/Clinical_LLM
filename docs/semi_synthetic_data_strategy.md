# Semi-Synthetic Data Strategy

## Goal

Create a scalable benchmark and optional training dataset without relying on a manually labeled corpus of clinical analytics questions.

## Generation flow

1. Programmatically generate valid structured plans.
2. Execute each plan on the local dataset.
3. Generate one or more natural-language questions for the plan.
4. Optionally generate paraphrases for robustness testing.

## Output example structure

- `question`
- `gold_plan`
- `gold_result`
- `paraphrases`
- `metadata`

## Benefits

- deterministic ground truth
- broad operation coverage
- reusable benchmark for planner evaluation
- direct measurement of end-to-end correctness

## Risks

- synthetic language may be narrower than real user phrasing
- plan templates may bias the benchmark toward easier structures

## Mitigations

- add paraphrase generation
- add human-authored challenge questions later
- track performance by question family and complexity

## Phase 1 status

Only starter scaffolding for synthetic query generation is included. The dataset-driven generation loop remains a TODO.
