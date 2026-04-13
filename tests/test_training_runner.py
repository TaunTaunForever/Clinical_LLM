from pathlib import Path

import pandas as pd

from icu_qa.evaluation.benchmark import generate_benchmark_examples
from icu_qa.evaluation.finetune import benchmark_to_finetune_examples, save_finetune_split_artifacts
from icu_qa.training.runner import (
    TrainingRunConfig,
    build_training_manifest,
    missing_training_dependencies,
    required_training_dependencies,
    write_training_manifest,
)


def demo_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "age_years": [20, 40, 70, 80],
            "sex_0male_1female": [0, 1, 0, 1],
            "episode_number": [1, 1, 2, 2],
            "hospital_outcome_1alive_0dead": [1, 0, 1, 0],
            "sex_label": ["male", "female", "male", "female"],
            "survival_flag": [1, 0, 1, 0],
            "mortality_flag": [0, 1, 0, 1],
        }
    )


def write_finetune_artifacts(tmp_path: Path) -> Path:
    benchmark_examples = {
        split: generate_benchmark_examples(demo_frame(), split_name=split)
        for split in ("training", "evaluation", "heldout")
    }
    finetune_examples = {
        split: benchmark_to_finetune_examples(examples, split_name=split)
        for split, examples in benchmark_examples.items()
    }
    save_finetune_split_artifacts(finetune_examples, tmp_path)
    return tmp_path


def test_required_training_dependencies_include_bitsandbytes_for_qlora() -> None:
    deps = required_training_dependencies(use_qlora=True)

    assert "torch" in deps
    assert "bitsandbytes" in deps


def test_build_training_manifest_contains_selected_model_and_artifacts(tmp_path: Path) -> None:
    artifact_dir = write_finetune_artifacts(tmp_path / "artifacts")
    config = TrainingRunConfig(
        artifact_dir=artifact_dir,
        output_dir=tmp_path / "runs",
        model_name="Qwen/Qwen2.5-3B-Instruct",
    )

    manifest = build_training_manifest(config)
    assert manifest["model_name"] == "Qwen/Qwen2.5-3B-Instruct"
    assert manifest["artifact_paths"]["training"].endswith("training_planner_supervised.jsonl")
    assert manifest["status"] == "scaffold_only"


def test_write_training_manifest_persists_json(tmp_path: Path) -> None:
    artifact_dir = write_finetune_artifacts(tmp_path / "artifacts")
    config = TrainingRunConfig(
        artifact_dir=artifact_dir,
        output_dir=tmp_path / "runs",
        model_name="Qwen/Qwen2.5-3B-Instruct",
        run_name="demo_run",
    )

    manifest_path = write_training_manifest(config)
    assert manifest_path.name == "training_manifest.json"
    assert manifest_path.exists()


def test_missing_training_dependencies_reports_absent_modules(monkeypatch) -> None:
    def fake_import_module(name: str):
        if name in {"torch", "bitsandbytes"}:
            raise ImportError(name)
        return object()

    monkeypatch.setattr("icu_qa.training.runner.importlib.import_module", fake_import_module)
    missing = missing_training_dependencies(use_qlora=True)

    assert "torch" in missing
    assert "bitsandbytes" in missing
