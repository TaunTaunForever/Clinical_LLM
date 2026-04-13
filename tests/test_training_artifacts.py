from pathlib import Path

import pandas as pd

from icu_qa.evaluation.benchmark import generate_benchmark_examples
from icu_qa.evaluation.finetune import benchmark_to_finetune_examples, save_finetune_split_artifacts
from icu_qa.training.artifacts import load_chat_records, load_supervised_records, summarize_finetune_records
from icu_qa.training.experiment import FineTuneExperimentConfig, validate_experiment_artifacts


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


def test_training_artifact_loader_and_summary_for_supervised(tmp_path: Path) -> None:
    artifact_dir = write_finetune_artifacts(tmp_path)
    records = load_supervised_records(artifact_dir / "training_planner_supervised.jsonl")
    summary = summarize_finetune_records(records, "supervised")

    assert summary.num_examples >= 20
    assert summary.avg_input_chars > 0
    assert "hard" in summary.complexity_tier_counts


def test_training_artifact_loader_and_summary_for_chat(tmp_path: Path) -> None:
    artifact_dir = write_finetune_artifacts(tmp_path)
    records = load_chat_records(artifact_dir / "training_planner_chat.jsonl")
    summary = summarize_finetune_records(records, "chat")

    assert summary.num_examples >= 20
    assert summary.avg_target_chars > 0
    assert "cohort_comparison" in summary.analysis_family_counts


def test_validate_experiment_artifacts_requires_standard_files(tmp_path: Path) -> None:
    artifact_dir = write_finetune_artifacts(tmp_path)
    config = FineTuneExperimentConfig(
        artifact_dir=artifact_dir,
        model_family="test-model",
        format_name="supervised",
    )

    paths = validate_experiment_artifacts(config)
    assert paths["training"].name == "training_planner_supervised.jsonl"
    assert paths["evaluation"].exists()
