# Milestones

## Phase 1: Scaffold and design

- create repository structure
- define planner schema
- scaffold planner, validator, execution, explanation, and evaluation modules
- add initial tests and scripts
- document architecture and project scope

## Phase 2: Baseline working system

- select and load a concrete ICU/sepsis CSV
- implement enriched schema metadata extraction
- connect a remote planner API baseline
- add strict JSON parsing and bounded repair-loop behavior
- wire question -> plan -> validation -> execution -> result flow
- enforce schema-aware validation rules
- support grouped summaries, ranking, and basic cohort comparisons

## Phase 3: End-to-end demo

- run question -> plan -> validation -> execution -> result flow
- add optional explanation layer
- support a polished CLI or lightweight app wrapper

## Phase 4: Semi-synthetic benchmark

- generate gold plans and executable results
- create question/paraphrase pairs
- implement benchmark runner and reporting

## Phase 5: Fine-tuned planner model

- validate fine-tuning-ready artifacts
- chosen base model: `Qwen/Qwen2.5-3B-Instruct`
- chosen training stack: `Transformers + TRL SFTTrainer + PEFT LoRA/QLoRA + Accelerate`
- train or fine-tune the planner model
- evaluate exact plan match and slot-level accuracy
- compare fine-tuned results against the prompted baseline or deterministic targets
- perform targeted error analysis and iteration
