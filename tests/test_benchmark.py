from pathlib import Path

import pandas as pd

from icu_qa.evaluation.benchmark import (
    benchmark_summary,
    default_benchmark_artifact_path,
    generate_paraphrases,
    generate_benchmark_examples,
    load_benchmark_examples,
    save_benchmark_examples,
    save_split_benchmark_artifacts,
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


def test_generate_benchmark_examples_returns_executed_examples() -> None:
    examples = generate_benchmark_examples(demo_frame(), split_name="training")

    assert len(examples) >= 20
    assert all(example.gold_result is not None for example in examples)
    assert all(example.metadata["split"] == "training" for example in examples)
    assert all("complexity_tier" in example.metadata for example in examples)
    assert max(len(example.paraphrases) for example in examples) >= 4
    assert any(len(example.gold_plan.get("filters", [])) >= 2 for example in examples)
    assert all("operation_count" in example.metadata for example in examples)
    assert all("question_length_words" in example.metadata for example in examples)
    assert all("result_columns" in example.metadata for example in examples)


def test_benchmark_examples_round_trip_through_json(tmp_path: Path) -> None:
    output_path = tmp_path / "benchmark.json"
    examples = generate_benchmark_examples(demo_frame(), split_name="evaluation")

    save_benchmark_examples(examples, output_path)
    loaded = load_benchmark_examples(output_path)

    assert len(loaded) == len(examples)
    assert loaded[0].question == examples[0].question
    assert loaded[0].gold_result is not None


def test_benchmark_summary_counts_examples_and_paraphrases() -> None:
    summary = benchmark_summary(generate_benchmark_examples(demo_frame(), split_name="heldout"))

    assert summary["num_examples"] >= 20
    assert summary["num_paraphrases"] >= summary["num_examples"] * 2
    assert "outcome_rate" in summary["analysis_family_counts"]
    assert "cohort_comparison" in summary["analysis_family_counts"]
    assert "ranking" in summary["analysis_family_counts"]
    assert "easy" in summary["complexity_tier_counts"]
    assert "medium" in summary["complexity_tier_counts"]
    assert "hard" in summary["complexity_tier_counts"]
    assert summary["avg_operation_count"] > 0
    assert summary["max_operation_count"] >= summary["max_filter_count"]


def test_generate_paraphrases_adds_deterministic_variants() -> None:
    paraphrases = generate_paraphrases(
        "What is the mortality rate for the full cohort?",
        ["How often did patients die in the cohort?"],
        "outcome_rate",
    )

    assert len(paraphrases) >= 2
    assert any("death rate" in candidate or "Report" in candidate for candidate in paraphrases)


def test_default_benchmark_artifact_path_uses_standard_naming() -> None:
    path = default_benchmark_artifact_path("artifacts/benchmarks", "training")
    assert path.as_posix().endswith("artifacts/benchmarks/training_benchmark.json")


def test_save_split_benchmark_artifacts_writes_standardized_files(tmp_path: Path) -> None:
    split_examples = {
        "training": generate_benchmark_examples(demo_frame(), split_name="training"),
        "evaluation": generate_benchmark_examples(demo_frame(), split_name="evaluation"),
        "heldout": generate_benchmark_examples(demo_frame(), split_name="heldout"),
    }

    output_paths = save_split_benchmark_artifacts(split_examples, tmp_path)

    assert set(output_paths) == {"training", "evaluation", "heldout"}
    assert output_paths["training"].name == "training_benchmark.json"
    assert output_paths["evaluation"].exists()
    assert output_paths["heldout"].exists()
