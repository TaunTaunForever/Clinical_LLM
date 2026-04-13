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

For the current sepsis survival dataset, schema-aware prompting should rely on enriched metadata rather than just raw headers. That metadata now includes field descriptions, semantic types, synonyms, supported operations, and derived-field lineage for planner-friendly columns such as `sex_label`, `survival_flag`, and `mortality_flag`.

The codebase now includes a transport-agnostic planner interface so prompt construction, raw model completion, JSON parsing, and schema validation are separated. This makes it easier to swap in a real remote LLM client later without entangling it with validation or execution logic.

The planner layer now includes a bounded repair loop for malformed JSON or schema-invalid plans. When parsing or validation fails, the planner can send the previous output plus a concrete error message back through the same transport and request corrected JSON-only output.

## Version 2

Optionally fine-tune on a semi-synthetic dataset where:

- input is question plus schema context
- target is the gold JSON plan

If fine-tuned, optimize token-level cross-entropy loss and evaluate primarily with task-specific execution-aware metrics.

The repository now supports fine-tuning-ready planner exports in two formats:

- supervised JSONL with `input_text` and `target_text`
- chat-style JSONL with `system`, `user`, and `assistant` messages

In both cases the target is a canonical JSON plan string so the training target is deterministic.

## Phase 5 model decision

The selected base model for the fine-tuned planner is `Qwen/Qwen2.5-3B-Instruct`.

Why this model:

- strong instruction-following behavior
- explicitly positioned for structured outputs and JSON-heavy use cases in its model card
- practical size for adapter-based fine-tuning on older consumer GPUs such as GTX 1080-class hardware
- permissive Apache 2.0 license

The current recommendation is to treat `Qwen/Qwen2.5-3B-Instruct` as the primary Phase 5 model for the first end-to-end training run on available personal hardware.

## Phase 5 training stack

The selected training stack is:

- `transformers` for model/tokenizer loading
- `trl` `SFTTrainer` for supervised fine-tuning
- `peft` with LoRA or QLoRA adapters
- `accelerate` for device/distributed orchestration
- `bitsandbytes` for 4-bit loading when running QLoRA on CUDA hardware

Recommended first training configuration:

- model: `Qwen/Qwen2.5-3B-Instruct`
- method: QLoRA adapter tuning
- training format: supervised JSONL first
- eval format: same canonical JSON target plus exact plan match and slot-level accuracy
- hardware target: one or more older NVIDIA GPUs, with multi-GPU support handled later if needed

Recommended fallback configuration:

- model: `Qwen/Qwen2.5-1.5B-Instruct`
- method: LoRA or QLoRA
- use only if the 3B run is still too expensive or unstable on the target PC

## Risks

- planner drift from allowed schema
- ambiguity in natural-language cohort definitions
- leakage from overfitting to synthetic phrasing

## TODO

- implement the actual training runner around the chosen stack
- define prompt packing budget for schema metadata
- tune and evaluate the repair loop strategy for malformed JSON or unsupported fields
- compare the fine-tuned planner against the deterministic benchmark targets
