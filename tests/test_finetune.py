import json
from pathlib import Path

import pandas as pd

from icu_qa.evaluation.benchmark import generate_benchmark_examples
from icu_qa.evaluation.finetune import (
    benchmark_to_finetune_examples,
    canonical_plan_json,
    default_finetune_artifact_paths,
    save_finetune_examples_jsonl,
    save_finetune_split_artifacts,
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


def test_canonical_plan_json_is_deterministic() -> None:
    plan = {"b": 1, "a": 2}
    assert canonical_plan_json(plan) == '{"a":2,"b":1}'


def test_benchmark_to_finetune_examples_builds_prompt_and_target() -> None:
    benchmark_examples = generate_benchmark_examples(demo_frame(), split_name="training")
    finetune_examples = benchmark_to_finetune_examples(benchmark_examples, split_name="training")

    assert len(finetune_examples) == len(benchmark_examples)
    assert finetune_examples[0].target_text.startswith("{")
    assert '"question"' in finetune_examples[0].user_prompt
    assert finetune_examples[0].metadata["split"] == "training"


def test_save_finetune_examples_jsonl_writes_records(tmp_path: Path) -> None:
    benchmark_examples = generate_benchmark_examples(demo_frame(), split_name="evaluation")
    finetune_examples = benchmark_to_finetune_examples(benchmark_examples, split_name="evaluation")
    output_path = tmp_path / "evaluation_supervised.jsonl"

    save_finetune_examples_jsonl(finetune_examples, output_path, format_name="supervised")

    lines = output_path.read_text(encoding="utf-8").strip().splitlines()
    first_record = json.loads(lines[0])
    assert first_record["metadata"]["split"] == "evaluation"
    assert "input_text" in first_record
    assert "target_text" in first_record


def test_save_finetune_split_artifacts_writes_chat_and_supervised_files(tmp_path: Path) -> None:
    benchmark_examples = {
        "training": generate_benchmark_examples(demo_frame(), split_name="training"),
        "evaluation": generate_benchmark_examples(demo_frame(), split_name="evaluation"),
        "heldout": generate_benchmark_examples(demo_frame(), split_name="heldout"),
    }
    finetune_examples = {
        split: benchmark_to_finetune_examples(examples, split_name=split)
        for split, examples in benchmark_examples.items()
    }

    output_paths = save_finetune_split_artifacts(finetune_examples, tmp_path)

    assert output_paths["training"]["supervised"].name == "training_planner_supervised.jsonl"
    assert output_paths["training"]["chat"].name == "training_planner_chat.jsonl"
    assert output_paths["evaluation"]["supervised"].exists()
    assert output_paths["heldout"]["chat"].exists()
    assert default_finetune_artifact_paths(tmp_path, "training")["chat"].name.endswith("_planner_chat.jsonl")
