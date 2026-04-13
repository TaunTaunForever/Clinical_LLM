# Training PC Checklist

## System prerequisites

- Linux preferred for the first training run
- NVIDIA driver installed and working
- CUDA-capable GPU(s) visible through `nvidia-smi`
- Python `3.12`
- `git`
- enough free disk space for:
  - model downloads
  - adapter checkpoints
  - logs
  - cached datasets and tokenizer files

## Python prerequisites

Install the packages in [requirements.txt](requirements.txt).

Recommended bootstrap commands:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip wheel setuptools
python -m pip install -r training_pc/requirements.txt
```

## Repo prerequisites

The PC should have access to:

- the repository source code
- `artifacts/finetune/` with the standardized fine-tuning JSONL files
- the raw dataset only if you also plan to regenerate artifacts there

## Optional but helpful local tools

- `tmux` or `screen` for long-running jobs
- `htop` for CPU/RAM monitoring
- `nvtop` for GPU monitoring

## Optional credentials

- Hugging Face token if you want authenticated model downloads or uploads
- Weights & Biases or another experiment tracker only if you decide to use one later

## First commands to run

Verify GPUs:

```bash
nvidia-smi
```

Verify dependency imports:

```bash
python scripts/run_training.py \
  --artifact-dir artifacts/finetune \
  --output-dir artifacts/training_runs \
  --check-dependencies-only
```

Verify artifact coverage:

```bash
python scripts/prepare_phase5_experiment.py \
  --artifact-dir artifacts/finetune \
  --format supervised
```

Write the first run manifest:

```bash
python scripts/run_training.py \
  --artifact-dir artifacts/finetune \
  --output-dir artifacts/training_runs
```
