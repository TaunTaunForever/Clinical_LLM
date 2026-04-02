# LLM-Powered ICU/Sepsis Outcomes QA System

This repository contains Phase 1 scaffolding for a portfolio-grade ML engineering project: a hybrid analytics QA system over retrospective ICU/sepsis tabular data.

The product goal is to let a user ask a natural-language analytics question, convert that question into a structured analysis plan, execute the plan deterministically over a local dataset, and optionally summarize the computed result in natural language.

## Why this system exists

Clinical analysts and ML engineers often need a safe way to bridge natural-language questions and reproducible dataset queries. This project is intentionally framed as a retrospective analytics system, not a diagnosis, treatment, or bedside decision tool.

The key design principle is strict separation of responsibilities:

- The LLM handles semantic parsing and structured planning.
- The deterministic analytics engine performs all numeric computation.
- The explanation layer only summarizes computed outputs and must not invent values.

## Phase 1 scope

Phase 1 creates the repository scaffold, architecture docs, planner schema, starter modules, scripts, and initial tests.

Implemented in this phase:

- repository structure and documentation
- typed Python package layout
- plan schema dataclasses and JSON schema contract
- deterministic validator and execution engine scaffold
- local CSV/dataframe loading and preprocessing stubs
- prompt-template scaffolding for a remote planner
- starter evaluation and semi-synthetic data generation utilities
- initial unit tests for core validation and execution behavior

Not implemented yet:

- live remote LLM API integration
- full dataset-specific schema wiring
- robust semi-synthetic generation pipeline
- production UI or service wrapper
- full benchmark set and planner repair loop

Dataset status:

- The scaffold is now wired to the local `s41598-020-73558-3_sepsis_survival_dataset`.
- The configured training dataset is the primary cohort CSV.
- The configured evaluation dataset is the study cohort CSV.
- Preprocessing derives `sex_label`, `survival_flag`, and `mortality_flag` from the raw columns so downstream analytics can use clearer semantics.

## Architecture

The intended demo architecture is hybrid:

1. Remote LLM planner
2. Local schema metadata and prompt construction
3. Local deterministic validator
4. Local deterministic analytics engine over CSV-based ICU/sepsis data
5. Optional explanation layer over computed outputs

The remote planner receives:

- user question
- schema metadata
- allowed operations
- JSON output contract
- few-shot examples

The remote planner must return JSON only. Raw patient rows should never be sent to the model.

## Planner-first, not model-first

The central ML task is:

`natural-language question -> structured JSON analysis plan`

Version 1 uses prompted inference with a pretrained instruction-tuned model. Version 2 may fine-tune on semi-synthetic examples generated from executable plans. Even in later versions, the model remains a planner rather than a calculator.

## Semi-synthetic supervision strategy

This project does not start with manually labeled question-answer pairs. Instead, it uses a semi-synthetic pipeline:

1. Programmatically generate structured plans
2. Execute those plans deterministically on the dataset
3. Generate natural-language questions from those plans
4. Optionally create paraphrases

This yields training and evaluation examples with:

- question
- gold plan
- deterministic result
- optional paraphrases

## Evaluation strategy

The project evaluates at multiple levels:

- planner validity and schema adherence
- execution success and failure types
- end-to-end result agreement with ground truth
- robustness to paraphrases and unsupported requests

See [docs/evaluation_plan.md](/Volumes/Tauntaun/ClinicalQA/docs/evaluation_plan.md) for details.

## Repository layout

- [docs/project_overview.md](/Volumes/Tauntaun/ClinicalQA/docs/project_overview.md)
- [docs/planner_schema.md](/Volumes/Tauntaun/ClinicalQA/docs/planner_schema.md)
- [src/icu_qa/planning/planner.py](/Volumes/Tauntaun/ClinicalQA/src/icu_qa/planning/planner.py)
- [src/icu_qa/planning/validator.py](/Volumes/Tauntaun/ClinicalQA/src/icu_qa/planning/validator.py)
- [src/icu_qa/execution/engine.py](/Volumes/Tauntaun/ClinicalQA/src/icu_qa/execution/engine.py)
- [scripts/run_query.py](/Volumes/Tauntaun/ClinicalQA/scripts/run_query.py)

## Current status

This repository is at Phase 1 scaffold status. The code is intentionally conservative: it implements small deterministic building blocks, leaves explicit TODOs where dataset-specific or API-specific work is required, and avoids claiming behavior that is not yet wired up.

## Next steps

1. Add a real sepsis outcomes CSV and schema metadata.
2. Implement remote planner integration with strict JSON response parsing.
3. Expand execution support for richer comparisons and distributions.
4. Build the semi-synthetic benchmark generation pipeline.
5. Add a simple local demo interface or CLI workflow.
