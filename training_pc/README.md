# Phase 5 Training PC Setup

This folder collects the PC-side material needed to run Phase 5 fine-tuning for the planner model on a separate machine.

The selected first training target is:

- base model: `Qwen/Qwen2.5-3B-Instruct`
- training method: QLoRA first, with LoRA fallback
- artifact format: supervised JSONL first

## What to copy onto the PC

At minimum, the training machine needs:

- this repository
- the Phase 5 fine-tuning artifacts under `artifacts/finetune/`
  - `training_planner_supervised.jsonl`
  - `evaluation_planner_supervised.jsonl`
  - `heldout_planner_supervised.jsonl`
- optionally the chat-format artifacts if you want to experiment later

## Files in this folder

- `requirements.txt`
  - Python packages to install in the PC training environment
- `setup_checklist.md`
  - system-level prerequisites and local setup notes

## Recommended training machine setup

- OS: Linux preferred
- GPU: NVIDIA GPU(s)
- Python: `3.12`
- virtual environment: required
- storage: prefer a fast internal SSD for checkpoints and logs

## Python environment setup

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip wheel setuptools
python -m pip install -r training_pc/requirements.txt
```

## Pre-flight checks

Check that the GPUs are visible:

```bash
nvidia-smi
```

Check that the training dependencies are importable:

```bash
python scripts/run_training.py \
  --artifact-dir artifacts/finetune \
  --output-dir artifacts/training_runs \
  --check-dependencies-only
```

Check that the fine-tuning artifacts exist:

```bash
python scripts/prepare_phase5_experiment.py \
  --artifact-dir artifacts/finetune \
  --format supervised
```

## Current training status

The repository now includes a training-run scaffold in `scripts/run_training.py`.

Right now it does three useful things:

- validates the standardized training/evaluation/heldout JSONL files
- checks whether required training libraries are installed
- writes a run manifest describing the intended fine-tuning configuration

The actual `TRL SFTTrainer` execution loop is still a TODO. That will be the next Phase 5 implementation step.

## Suggested workflow

1. Export or copy the fine-tuning artifacts into `artifacts/finetune/`.
2. Set up the Python environment with `training_pc/requirements.txt`.
3. Run the dependency and artifact checks.
4. Generate a training manifest with `scripts/run_training.py`.
5. Implement and run the actual training loop on the PC.
