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

## Current status

The codebase now includes a first-pass deterministic benchmark generator that:

- instantiates executable plan templates for the bound sepsis survival dataset
- executes each plan locally to produce ground-truth result tables
- attaches one question plus paraphrases per plan
- writes benchmark artifacts to JSON for training, evaluation, or held-out splits
- tags each template with a coarse complexity tier
- records richer per-example metadata such as operation counts and question length
- augments template paraphrases with deterministic paraphrase generation

This is still a starter Phase 4 implementation rather than a full benchmark factory. Coverage is currently narrow and template-driven, but the train/eval/held-out artifact path is now in place.
The current benchmark is still template-driven, but it now includes richer paraphrase variation and several multi-constraint query patterns so the language side is less rigidly repetitive.

Current template coverage now spans:

- overall outcome rates
- filtered outcome rates
- grouped outcome summaries
- distribution-style counts
- ranking queries
- descriptive summaries
- filtered descriptive summaries
- cohort comparisons

The benchmark now also includes:

- multi-constraint filtered analyses such as sex plus age filters
- multi-constraint grouped analyses
- multi-constraint ranked outputs
- multi-constraint cohort comparisons
- less literal paraphrases such as "How did older women do on mortality?" and "Who did worst by sex on mortality?"

Human-authored challenge questions are now scaffolded through a dedicated challenge-set template so manually written robustness cases can be added later without changing the core benchmark pipeline.

Current complexity tiers are:

- `easy` for single-step whole-cohort summaries
- `medium` for filtered or grouped analyses
- `hard` for ranked outputs and cohort comparisons

Benchmark artifacts can now be generated in a standardized split layout:

- `training_benchmark.json`
- `evaluation_benchmark.json`
- `heldout_benchmark.json`

Fine-tuning-ready artifacts can now also be exported in a standardized split layout:

- `training_planner_supervised.jsonl`
- `evaluation_planner_supervised.jsonl`
- `heldout_planner_supervised.jsonl`
- `training_planner_chat.jsonl`
- `evaluation_planner_chat.jsonl`
- `heldout_planner_chat.jsonl`

The per-example metadata now includes fields such as:

- `question_length_chars`
- `question_length_words`
- `num_paraphrases`
- `num_filters`
- `num_group_by`
- `num_aggregations`
- `num_comparisons`
- `num_order_by`
- `has_limit`
- `operation_count`
- `result_columns`

Evaluation reporting can now also bucket planner performance by:

- `analysis_family`
- `complexity_tier`
