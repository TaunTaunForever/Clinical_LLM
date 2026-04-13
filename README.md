# ClinicalQA

ClinicalQA is an LLM-assisted analytics system for retrospective ICU/sepsis question answering over structured data. A user asks a natural-language question, the planner converts it into a constrained JSON analysis plan, the validator checks that plan against the allowed schema and operations, and the execution engine computes the result locally.

The core design goal is reliability through separation of responsibilities:

- The model plans.
- Deterministic Python code validates.
- Deterministic Python code computes.
- The explanation layer summarizes only computed outputs.

This repository is intentionally built as a retrospective analytics project, not a diagnosis, treatment, causal-inference, or bedside decision-support tool.

## What the system does

ClinicalQA supports questions such as:

- overall mortality or survival rates
- filtered subgroup rates, such as patients age 65 and older
- grouped summaries, such as outcomes by sex
- rankings, such as which group has the highest mortality
- cohort comparisons, such as older versus younger survival
- descriptive summaries, such as mean, median, standard deviation, minimum, and maximum

The system returns:

- planner JSON
- validation status
- computed result table
- grounded text summary of the computed result

## How the LLM works in this project

The model is used as a structured planner, not as a calculator.

Its job is:

`natural-language question -> schema-constrained JSON analysis plan`

That means the model does not:

- compute mortality or survival itself
- perform arithmetic over patient rows
- invent result tables
- decide treatment or diagnosis

Instead, it produces a plan with fields such as:

- `intent`
- `analysis_type`
- `select`
- `filters`
- `group_by`
- `aggregations`
- `comparisons`
- `order_by`
- `limit`
- `requires_clarification`

The plan is then checked by the validator before any execution occurs.

## System architecture

The end-to-end flow is:

1. User asks a question.
2. Planner model generates structured JSON.
3. Validator checks schema compatibility and supported operations.
4. Request guards block unsupported clinical/predictive requests.
5. Execution engine computes the result over local structured data.
6. Explanation layer summarizes only the computed output.
7. GUI displays planner JSON, validation JSON, result table, and text response.

In short:

`question -> planner JSON -> validation -> deterministic execution -> grounded response`

## Why the architecture is split this way

This project is intentionally planner-first rather than chatbot-first.

Key design choices:

- The execution engine is the source of truth for computed values.
- Raw patient rows are not sent to the planner.
- Structured validation is separate from model generation.
- Unsupported requests are rejected deterministically rather than relying only on model behavior.
- Benchmarking measures both raw planner behavior and normalized structured behavior.

This makes the system more inspectable and easier to test than a free-form QA model.

## Data and schema

The repository is wired to the local sepsis survival dataset:

- primary cohort CSV for training-oriented workflows
- study cohort CSV for evaluation-oriented workflows
- validation cohort CSV for held-out workflows

Preprocessing derives planner-friendly columns such as:

- `sex_label`
- `survival_flag`
- `mortality_flag`

These derived fields make it easier for the planner to reason over meaningful concepts instead of raw encoded columns.

## Training and evaluation approach

The project uses semi-synthetic supervision rather than starting from a large manually labeled corpus.

The benchmark and fine-tuning pipeline works like this:

1. Programmatically define executable gold plans.
2. Run those plans deterministically on the dataset.
3. Generate natural-language questions that map to the plans.
4. Add paraphrases and out-of-template variants.
5. Export supervised fine-tuning artifacts.
6. Train a planner adapter model on canonical JSON targets.
7. Evaluate exact-plan match, slot-level accuracy, JSON validity, schema-valid rate, and execution compatibility.

The current benchmark split structure includes:

- canonical questions
- less-literal paraphrases
- out-of-template variants

This is designed to test generalization rather than only template memorization.

## Local model and inference setup

The local planner path uses an adapter on top of:

- `Qwen/Qwen2.5-3B-Instruct`

The training/inference stack includes:

- PyTorch
- Transformers
- TRL
- PEFT / LoRA / QLoRA
- Accelerate / `torchrun`

For interactive local use, the GUI keeps the adapter loaded in memory so the model does not reload on every request.

## Safety boundaries

ClinicalQA is restricted to retrospective structured-data analytics.

The system explicitly blocks:

- patient-specific prediction
- diagnosis requests
- treatment recommendation requests
- causal-inference requests
- bedside decision support

These restrictions are enforced by deterministic request guards in addition to model prompting.

## Repository structure

Important entry points:

- [scripts/run_gui.py](scripts/run_gui.py): local browser GUI with persistent planner model
- [scripts/run_query.py](scripts/run_query.py): CLI query and plan execution
- [scripts/run_training.py](scripts/run_training.py): local adapter training
- [scripts/run_adapter_evaluation.py](scripts/run_adapter_evaluation.py): adapter evaluation over benchmark splits

Important modules:

- [src/icu_qa/planning/planner.py](src/icu_qa/planning/planner.py): planner interfaces and remote transport
- [src/icu_qa/planning/validator.py](src/icu_qa/planning/validator.py): deterministic plan validation
- [src/icu_qa/planning/request_guard.py](src/icu_qa/planning/request_guard.py): unsupported-request blocking
- [src/icu_qa/execution/engine.py](src/icu_qa/execution/engine.py): deterministic execution engine
- [src/icu_qa/evaluation/benchmark.py](src/icu_qa/evaluation/benchmark.py): semi-synthetic benchmark generation
- [src/icu_qa/evaluation/adapter_eval.py](src/icu_qa/evaluation/adapter_eval.py): adapter evaluation and normalization
- [src/icu_qa/inference/adapter_planner.py](src/icu_qa/inference/adapter_planner.py): persistent local adapter planner

Supporting documentation:

- [docs/project_overview.md](docs/project_overview.md)
- [docs/planner_schema.md](docs/planner_schema.md)
- [docs/evaluation_plan.md](docs/evaluation_plan.md)
- [docs/requirements.md](docs/requirements.md)
- [docs/model_development.md](docs/model_development.md)

## Running the project

### 1. Environment

Create and activate a Python environment, then install the project dependencies you want.

Minimal:

```bash
pip install -r requirements.txt
```

Training/inference extras:

```bash
pip install -r requirements-training.txt
```

### 2. Run the local GUI

```bash
./ClinicalQA_venv/bin/python scripts/run_gui.py \
  --checkpoint-dir artifacts/training_runs/planner_qwen25_3b_generalization_variants_epoch6 \
  --split evaluation \
  --host 127.0.0.1 \
  --port 7860 \
  --max-new-tokens 160
```

Then open:

```text
http://127.0.0.1:7860
```

### 3. Run a CLI question

```bash
./ClinicalQA_venv/bin/python scripts/run_query.py \
  --split evaluation \
  --question "What is the mortality rate for the full cohort?" \
  --explain
```

### 4. Run focused tests

```bash
./ClinicalQA_venv/bin/python -m pytest -q
```

## Current capabilities

The repository currently includes:

- deterministic schema-aware validation
- deterministic execution over structured ICU/sepsis data
- semi-synthetic benchmark generation
- fine-tuning artifact export
- local adapter training scripts
- adapter evaluation tooling
- persistent local GUI inference
- deterministic safety guards for unsupported requests

## Known limitations

- Local inference latency is still high on older GTX 1080-class hardware.
- Some complex paraphrases require normalization or additional training coverage.
- Benchmark-aware normalization improves structured output quality, so raw-model behavior and normalized behavior should be interpreted separately.

## Development priorities

Near-term engineering priorities are:

- improve single-question inference latency
- run broader held-out evaluation on expanded benchmark sets
- extend benchmark coverage for harder comparison and ambiguity cases
- keep GUI behavior aligned with deterministic validation and safety boundaries

# LLM-Powered ICU/Sepsis Outcomes QA System

This repository contains a portfolio-grade ML engineering project: a hybrid analytics QA system over retrospective ICU/sepsis tabular data.

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

- full dataset-specific schema wiring
- robust semi-synthetic generation pipeline
- production UI or service wrapper
- full benchmark set

Dataset status:

- The scaffold is now wired to the local `s41598-020-73558-3_sepsis_survival_dataset`.
- The configured training dataset is the primary cohort CSV.
- The configured evaluation dataset is the study cohort CSV.
- Preprocessing derives `sex_label`, `survival_flag`, and `mortality_flag` from the raw columns so downstream analytics can use clearer semantics.

Planner status:

- The structured planner interface is implemented.
- A bounded repair loop is implemented for malformed or schema-invalid planner outputs.
- A live remote planner transport is implemented for OpenAI-compatible chat completion endpoints and is configured through environment variables.
- Deterministic planner-output fixtures are still supported for local testing.
- The chosen Phase 5 fine-tuning target is `Qwen/Qwen2.5-3B-Instruct`.

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

For the portfolio direction of this project, the remote planner is now treated as an optional baseline or fallback. The primary target is a fine-tuned planner model that maps `question + schema context -> JSON plan`.

## Planner-first, not model-first

The central ML task is:

`natural-language question -> structured JSON analysis plan`

Version 1 uses prompted inference with a pretrained instruction-tuned model. Version 2 fine-tunes on semi-synthetic examples generated from executable plans. The selected Phase 5 base model is `Qwen/Qwen2.5-3B-Instruct`, and the planned training stack is Hugging Face `Transformers + TRL SFTTrainer + PEFT LoRA/QLoRA + Accelerate`. Even in later versions, the model remains a planner rather than a calculator.

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

See [docs/evaluation_plan.md](docs/evaluation_plan.md) for details.

## Repository layout

- [docs/project_overview.md](docs/project_overview.md)
- [docs/planner_schema.md](docs/planner_schema.md)
- [training_pc/README.md](training_pc/README.md)
- [src/icu_qa/planning/planner.py](src/icu_qa/planning/planner.py)
- [src/icu_qa/planning/validator.py](src/icu_qa/planning/validator.py)
- [src/icu_qa/execution/engine.py](src/icu_qa/execution/engine.py)
- [scripts/run_query.py](scripts/run_query.py)

