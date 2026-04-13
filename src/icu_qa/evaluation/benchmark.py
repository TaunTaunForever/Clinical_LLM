"""Benchmark generation, serialization, and reporting helpers."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd

from icu_qa.execution.engine import execute_plan


@dataclass(slots=True)
class BenchmarkExample:
    """One benchmark example for planner or end-to-end evaluation."""

    question: str
    gold_plan: dict[str, Any]
    gold_result: pd.DataFrame | None = None
    paraphrases: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_record(self) -> dict[str, Any]:
        """Serialize a benchmark example to a JSON-friendly record."""

        result_rows: list[dict[str, Any]] | None = None
        if self.gold_result is not None:
            result_rows = self.gold_result.to_dict(orient="records")
        return {
            "question": self.question,
            "gold_plan": self.gold_plan,
            "gold_result": result_rows,
            "paraphrases": self.paraphrases,
            "metadata": self.metadata,
        }

    @classmethod
    def from_record(cls, record: dict[str, Any]) -> "BenchmarkExample":
        """Restore a benchmark example from a serialized record."""

        gold_result = record.get("gold_result")
        return cls(
            question=record["question"],
            gold_plan=record["gold_plan"],
            gold_result=pd.DataFrame(gold_result) if gold_result is not None else None,
            paraphrases=list(record.get("paraphrases", [])),
            metadata=dict(record.get("metadata", {})),
        )


def _plan_specs() -> list[dict[str, Any]]:
    """Return deterministic benchmark plan specifications.

    These starter templates are intentionally narrow and aligned to the
    currently bound sepsis survival dataset.
    """

    return [
        {
            "question": "What is the mortality rate for the full cohort?",
            "paraphrases": [
                "How often did patients die in the cohort?",
                "What share of the cohort had in-hospital mortality?",
                "What fraction of this cohort died before hospital discharge?",
                "How common was in-hospital death overall?",
            ],
            "metadata": {
                "analysis_family": "outcome_rate",
                "template_name": "overall_mortality",
                "complexity_tier": "easy",
            },
            "plan": {
                "intent": "overall_mortality",
                "analysis_type": "outcome_rate",
                "select": ["mortality_rate"],
                "filters": [],
                "group_by": [],
                "aggregations": [
                    {"name": "mortality_rate", "column": "mortality_flag", "alias": "mortality_rate"}
                ],
                "comparisons": [],
                "order_by": [],
                "limit": None,
                "requires_clarification": False,
                "confidence": 1.0,
                "notes": ["Semi-synthetic benchmark template."],
            },
        },
        {
            "question": "What is the survival rate for the full cohort?",
            "paraphrases": [
                "How often did patients survive to hospital outcome?",
                "What share of the cohort survived?",
                "What fraction of the cohort was alive at hospital outcome?",
                "How common was survival overall?",
            ],
            "metadata": {
                "analysis_family": "outcome_rate",
                "template_name": "overall_survival",
                "complexity_tier": "easy",
            },
            "plan": {
                "intent": "overall_survival",
                "analysis_type": "outcome_rate",
                "select": ["survival_rate"],
                "filters": [],
                "group_by": [],
                "aggregations": [
                    {"name": "survival_rate", "column": "survival_flag", "alias": "survival_rate"}
                ],
                "comparisons": [],
                "order_by": [],
                "limit": None,
                "requires_clarification": False,
                "confidence": 1.0,
                "notes": ["Semi-synthetic benchmark template."],
            },
        },
        {
            "question": "What is the mortality rate for female patients?",
            "paraphrases": [
                "Among female patients, what share died?",
                "What is the in-hospital mortality rate for the female cohort?",
                "How often did women in the cohort die in hospital?",
                "What were death outcomes for women?",
            ],
            "metadata": {
                "analysis_family": "filtered_outcome_rate",
                "template_name": "female_mortality",
                "complexity_tier": "medium",
            },
            "plan": {
                "intent": "female_mortality",
                "analysis_type": "outcome_rate",
                "select": ["mortality_rate"],
                "filters": [{"column": "sex_label", "operator": "eq", "value": "female"}],
                "group_by": [],
                "aggregations": [
                    {"name": "mortality_rate", "column": "mortality_flag", "alias": "mortality_rate"}
                ],
                "comparisons": [],
                "order_by": [],
                "limit": None,
                "requires_clarification": False,
                "confidence": 1.0,
                "notes": ["Semi-synthetic benchmark template."],
            },
        },
        {
            "question": "What is the mortality rate for patients aged 65 and older?",
            "paraphrases": [
                "How often did patients age 65+ die in the hospital?",
                "What is the mortality rate among older patients in the cohort?",
                "How severe were outcomes for patients 65 and older?",
                "What share of older patients died before discharge?",
            ],
            "metadata": {
                "analysis_family": "filtered_outcome_rate",
                "template_name": "older_patient_mortality",
                "complexity_tier": "medium",
            },
            "plan": {
                "intent": "older_patient_mortality",
                "analysis_type": "outcome_rate",
                "select": ["mortality_rate"],
                "filters": [{"column": "age_years", "operator": "gte", "value": 65}],
                "group_by": [],
                "aggregations": [
                    {"name": "mortality_rate", "column": "mortality_flag", "alias": "mortality_rate"}
                ],
                "comparisons": [],
                "order_by": [],
                "limit": None,
                "requires_clarification": False,
                "confidence": 1.0,
                "notes": ["Semi-synthetic benchmark template."],
            },
        },
        {
            "question": "What is the mortality rate grouped by sex?",
            "paraphrases": [
                "Show mortality rate for male and female groups.",
                "How does mortality vary by sex group?",
                "Break out death rate by sex.",
                "Show outcomes by sex using mortality rate.",
            ],
            "metadata": {
                "analysis_family": "grouped_outcome_rate",
                "template_name": "mortality_by_sex",
                "complexity_tier": "medium",
            },
            "plan": {
                "intent": "mortality_by_sex",
                "analysis_type": "outcome_rate",
                "select": ["sex_label", "mortality_rate"],
                "filters": [],
                "group_by": ["sex_label"],
                "aggregations": [
                    {"name": "mortality_rate", "column": "mortality_flag", "alias": "mortality_rate"}
                ],
                "comparisons": [],
                "order_by": [{"column": "sex_label", "direction": "asc"}],
                "limit": None,
                "requires_clarification": False,
                "confidence": 1.0,
                "notes": ["Semi-synthetic benchmark template."],
            },
        },
        {
            "question": "How many episodes are there by sex group?",
            "paraphrases": [
                "Count episodes for each sex group.",
                "What is the episode count by sex?",
                "How many cohort records belong to each sex group?",
                "Show the distribution of episodes across sex groups.",
            ],
            "metadata": {
                "analysis_family": "distribution_query",
                "template_name": "episode_count_by_sex",
                "complexity_tier": "medium",
            },
            "plan": {
                "intent": "episode_count_by_sex",
                "analysis_type": "distribution_query",
                "select": ["sex_label", "episode_count"],
                "filters": [],
                "group_by": ["sex_label"],
                "aggregations": [
                    {"name": "count", "column": "episode_number", "alias": "episode_count"}
                ],
                "comparisons": [],
                "order_by": [{"column": "episode_count", "direction": "desc"}],
                "limit": None,
                "requires_clarification": False,
                "confidence": 1.0,
                "notes": ["Semi-synthetic benchmark template."],
            },
        },
        {
            "question": "Which sex group has the highest mortality rate?",
            "paraphrases": [
                "What is the top-risk sex group by mortality?",
                "Rank sex groups by mortality rate and return the top one.",
                "Which sex group did worst on mortality?",
                "Who had the highest death rate by sex group?",
            ],
            "metadata": {
                "analysis_family": "ranking",
                "template_name": "top_mortality_group",
                "complexity_tier": "hard",
            },
            "plan": {
                "intent": "top_mortality_group",
                "analysis_type": "top_risk_groups",
                "select": ["sex_label", "mortality_rate"],
                "filters": [],
                "group_by": ["sex_label"],
                "aggregations": [
                    {"name": "mortality_rate", "column": "mortality_flag", "alias": "mortality_rate"}
                ],
                "comparisons": [],
                "order_by": [{"column": "mortality_rate", "direction": "desc"}],
                "limit": 1,
                "requires_clarification": False,
                "confidence": 1.0,
                "notes": ["Semi-synthetic benchmark template."],
            },
        },
        {
            "question": "Which sex group has the highest survival rate?",
            "paraphrases": [
                "Rank sex groups by survival rate and return the top one.",
                "What sex group has the best survival rate?",
                "Which sex group did best on survival?",
                "Who had the strongest survival outcome by sex group?",
            ],
            "metadata": {
                "analysis_family": "ranking",
                "template_name": "top_survival_group",
                "complexity_tier": "hard",
            },
            "plan": {
                "intent": "top_survival_group",
                "analysis_type": "top_risk_groups",
                "select": ["sex_label", "survival_rate"],
                "filters": [],
                "group_by": ["sex_label"],
                "aggregations": [
                    {"name": "survival_rate", "column": "survival_flag", "alias": "survival_rate"}
                ],
                "comparisons": [],
                "order_by": [{"column": "survival_rate", "direction": "desc"}],
                "limit": 1,
                "requires_clarification": False,
                "confidence": 1.0,
                "notes": ["Semi-synthetic benchmark template."],
            },
        },
        {
            "question": "What is the mean age by sex group?",
            "paraphrases": [
                "Show average age for male and female groups.",
                "How does mean age differ across sex groups?",
                "Break out average age by sex.",
                "What is the age average for each sex group?",
            ],
            "metadata": {
                "analysis_family": "grouped_summary",
                "template_name": "mean_age_by_sex",
                "complexity_tier": "medium",
            },
            "plan": {
                "intent": "mean_age_by_sex",
                "analysis_type": "descriptive_summary",
                "select": ["sex_label", "mean_age_years"],
                "filters": [],
                "group_by": ["sex_label"],
                "aggregations": [
                    {"name": "mean", "column": "age_years", "alias": "mean_age_years"}
                ],
                "comparisons": [],
                "order_by": [{"column": "sex_label", "direction": "asc"}],
                "limit": None,
                "requires_clarification": False,
                "confidence": 1.0,
                "notes": ["Semi-synthetic benchmark template."],
            },
        },
        {
            "question": "What is the median age for the full cohort?",
            "paraphrases": [
                "What is the cohort median age?",
                "Report the median patient age in the dataset.",
                "What is the middle age value for this cohort?",
                "Summarize age with the cohort median.",
            ],
            "metadata": {
                "analysis_family": "descriptive_summary",
                "template_name": "median_age",
                "complexity_tier": "easy",
            },
            "plan": {
                "intent": "median_age",
                "analysis_type": "descriptive_summary",
                "select": ["median_age_years"],
                "filters": [],
                "group_by": [],
                "aggregations": [
                    {"name": "median", "column": "age_years", "alias": "median_age_years"}
                ],
                "comparisons": [],
                "order_by": [],
                "limit": None,
                "requires_clarification": False,
                "confidence": 1.0,
                "notes": ["Semi-synthetic benchmark template."],
            },
        },
        {
            "question": "What is the standard deviation of age in the full cohort?",
            "paraphrases": [
                "How variable is age in the cohort?",
                "Report the age standard deviation for the dataset.",
                "How spread out is age in this cohort?",
                "Summarize age dispersion with standard deviation.",
            ],
            "metadata": {
                "analysis_family": "descriptive_summary",
                "template_name": "age_std",
                "complexity_tier": "easy",
            },
            "plan": {
                "intent": "age_std",
                "analysis_type": "descriptive_summary",
                "select": ["std_age_years"],
                "filters": [],
                "group_by": [],
                "aggregations": [
                    {"name": "std", "column": "age_years", "alias": "std_age_years"}
                ],
                "comparisons": [],
                "order_by": [],
                "limit": None,
                "requires_clarification": False,
                "confidence": 1.0,
                "notes": ["Semi-synthetic benchmark template."],
            },
        },
        {
            "question": "What is the maximum age among female patients?",
            "paraphrases": [
                "Among female patients, what is the highest recorded age?",
                "Report the oldest age in the female cohort.",
                "How old was the oldest woman in the cohort?",
                "What is the maximum female age?",
            ],
            "metadata": {
                "analysis_family": "filtered_summary",
                "template_name": "max_age_female",
                "complexity_tier": "medium",
            },
            "plan": {
                "intent": "max_age_female",
                "analysis_type": "descriptive_summary",
                "select": ["max_age_years"],
                "filters": [{"column": "sex_label", "operator": "eq", "value": "female"}],
                "group_by": [],
                "aggregations": [
                    {"name": "max", "column": "age_years", "alias": "max_age_years"}
                ],
                "comparisons": [],
                "order_by": [],
                "limit": None,
                "requires_clarification": False,
                "confidence": 1.0,
                "notes": ["Semi-synthetic benchmark template."],
            },
        },
        {
            "question": "What proportion of the cohort is female?",
            "paraphrases": [
                "What share of patients are female?",
                "Estimate the female proportion in the cohort.",
                "How much of the cohort is women?",
                "What fraction of the sample is female?",
            ],
            "metadata": {
                "analysis_family": "descriptive_summary",
                "template_name": "female_proportion",
                "complexity_tier": "easy",
            },
            "plan": {
                "intent": "female_proportion",
                "analysis_type": "descriptive_summary",
                "select": ["female_proportion"],
                "filters": [],
                "group_by": [],
                "aggregations": [
                    {"name": "proportion", "column": "sex_0male_1female", "alias": "female_proportion"}
                ],
                "comparisons": [],
                "order_by": [],
                "limit": None,
                "requires_clarification": False,
                "confidence": 1.0,
                "notes": ["Semi-synthetic benchmark template."],
            },
        },
        {
            "question": "Compare mortality rate between male and female cohorts.",
            "paraphrases": [
                "How does male mortality compare with female mortality?",
                "Show the mortality-rate difference between male and female groups.",
                "Compare death rates for men and women.",
                "Who had worse mortality, male or female patients?",
            ],
            "metadata": {
                "analysis_family": "cohort_comparison",
                "template_name": "male_vs_female_mortality",
                "complexity_tier": "hard",
            },
            "plan": {
                "intent": "male_vs_female_mortality",
                "analysis_type": "cohort_comparison",
                "select": [],
                "filters": [],
                "group_by": [],
                "aggregations": [],
                "comparisons": [
                    {
                        "left_filters": [{"column": "sex_label", "operator": "eq", "value": "male"}],
                        "right_filters": [{"column": "sex_label", "operator": "eq", "value": "female"}],
                        "metric": "mortality_rate",
                        "column": "mortality_flag",
                        "left_label": "male",
                        "right_label": "female",
                    }
                ],
                "order_by": [],
                "limit": None,
                "requires_clarification": False,
                "confidence": 1.0,
                "notes": ["Semi-synthetic benchmark template."],
            },
        },
        {
            "question": "Compare mean age between male and female cohorts.",
            "paraphrases": [
                "How does average age differ between male and female groups?",
                "Show the mean-age difference between male and female cohorts.",
                "Compare male and female average ages.",
                "Which sex group is older on average?",
            ],
            "metadata": {
                "analysis_family": "cohort_comparison",
                "template_name": "male_vs_female_mean_age",
                "complexity_tier": "hard",
            },
            "plan": {
                "intent": "male_vs_female_mean_age",
                "analysis_type": "feature_difference",
                "select": [],
                "filters": [],
                "group_by": [],
                "aggregations": [],
                "comparisons": [
                    {
                        "left_filters": [{"column": "sex_label", "operator": "eq", "value": "male"}],
                        "right_filters": [{"column": "sex_label", "operator": "eq", "value": "female"}],
                        "metric": "mean",
                        "column": "age_years",
                        "left_label": "male",
                        "right_label": "female",
                    }
                ],
                "order_by": [],
                "limit": None,
                "requires_clarification": False,
                "confidence": 1.0,
                "notes": ["Semi-synthetic benchmark template."],
            },
        },
        {
            "question": "Compare mortality rate between older patients and younger patients.",
            "paraphrases": [
                "How does mortality differ for patients age 65+ versus under 65?",
                "Show the mortality-rate difference between older and younger cohorts.",
                "Compare death outcomes for older versus younger patients.",
                "Do older patients have worse mortality than younger patients?",
            ],
            "metadata": {
                "analysis_family": "cohort_comparison",
                "template_name": "older_vs_younger_mortality",
                "complexity_tier": "hard",
            },
            "plan": {
                "intent": "older_vs_younger_mortality",
                "analysis_type": "cohort_comparison",
                "select": [],
                "filters": [],
                "group_by": [],
                "aggregations": [],
                "comparisons": [
                    {
                        "left_filters": [{"column": "age_years", "operator": "gte", "value": 65}],
                        "right_filters": [{"column": "age_years", "operator": "lt", "value": 65}],
                        "metric": "mortality_rate",
                        "column": "mortality_flag",
                        "left_label": "age_65_plus",
                        "right_label": "age_under_65",
                    }
                ],
                "order_by": [],
                "limit": None,
                "requires_clarification": False,
                "confidence": 1.0,
                "notes": ["Semi-synthetic benchmark template."],
            },
        },
        {
            "question": "What is the mortality rate for female patients aged 65 and older?",
            "paraphrases": [
                "Among women age 65+, what share died?",
                "What is the death rate for older female patients?",
                "How did older women do on mortality?",
                "What were mortality outcomes for females 65 and above?",
            ],
            "metadata": {
                "analysis_family": "filtered_outcome_rate",
                "template_name": "older_female_mortality",
                "complexity_tier": "hard",
            },
            "plan": {
                "intent": "older_female_mortality",
                "analysis_type": "outcome_rate",
                "select": ["mortality_rate"],
                "filters": [
                    {"column": "sex_label", "operator": "eq", "value": "female"},
                    {"column": "age_years", "operator": "gte", "value": 65},
                ],
                "group_by": [],
                "aggregations": [
                    {"name": "mortality_rate", "column": "mortality_flag", "alias": "mortality_rate"}
                ],
                "comparisons": [],
                "order_by": [],
                "limit": None,
                "requires_clarification": False,
                "confidence": 1.0,
                "notes": ["Semi-synthetic benchmark template."],
            },
        },
        {
            "question": "What is the survival rate by sex among patients aged 65 and older?",
            "paraphrases": [
                "For patients 65+, show survival rate by sex.",
                "How does survival vary by sex in the older cohort?",
                "Among older patients, break out survival by sex group.",
                "Show outcomes by sex for the 65+ cohort using survival rate.",
            ],
            "metadata": {
                "analysis_family": "grouped_outcome_rate",
                "template_name": "older_survival_by_sex",
                "complexity_tier": "hard",
            },
            "plan": {
                "intent": "older_survival_by_sex",
                "analysis_type": "outcome_rate",
                "select": ["sex_label", "survival_rate"],
                "filters": [{"column": "age_years", "operator": "gte", "value": 65}],
                "group_by": ["sex_label"],
                "aggregations": [
                    {"name": "survival_rate", "column": "survival_flag", "alias": "survival_rate"}
                ],
                "comparisons": [],
                "order_by": [{"column": "survival_rate", "direction": "desc"}],
                "limit": None,
                "requires_clarification": False,
                "confidence": 1.0,
                "notes": ["Semi-synthetic benchmark template."],
            },
        },
        {
            "question": "Which sex group has the highest mortality rate among patients aged 65 and older?",
            "paraphrases": [
                "Within the 65+ cohort, which sex group has the worst mortality?",
                "Rank sex groups by mortality among older patients and return the top one.",
                "Among older patients, who did worst by sex on mortality?",
                "Who had the highest death rate by sex in the age 65+ cohort?",
            ],
            "metadata": {
                "analysis_family": "ranking",
                "template_name": "top_mortality_group_older_patients",
                "complexity_tier": "hard",
            },
            "plan": {
                "intent": "top_mortality_group_older_patients",
                "analysis_type": "top_risk_groups",
                "select": ["sex_label", "mortality_rate"],
                "filters": [{"column": "age_years", "operator": "gte", "value": 65}],
                "group_by": ["sex_label"],
                "aggregations": [
                    {"name": "mortality_rate", "column": "mortality_flag", "alias": "mortality_rate"}
                ],
                "comparisons": [],
                "order_by": [{"column": "mortality_rate", "direction": "desc"}],
                "limit": 1,
                "requires_clarification": False,
                "confidence": 1.0,
                "notes": ["Semi-synthetic benchmark template."],
            },
        },
        {
            "question": "Compare mortality rate between older female patients and older male patients.",
            "paraphrases": [
                "How does mortality differ between women 65+ and men 65+?",
                "Compare death rates for older female versus older male patients.",
                "Among patients aged 65+, who had worse mortality by sex?",
                "Show the mortality-rate difference between older women and older men.",
            ],
            "metadata": {
                "analysis_family": "cohort_comparison",
                "template_name": "older_female_vs_older_male_mortality",
                "complexity_tier": "hard",
            },
            "plan": {
                "intent": "older_female_vs_older_male_mortality",
                "analysis_type": "cohort_comparison",
                "select": [],
                "filters": [],
                "group_by": [],
                "aggregations": [],
                "comparisons": [
                    {
                        "left_filters": [
                            {"column": "sex_label", "operator": "eq", "value": "female"},
                            {"column": "age_years", "operator": "gte", "value": 65},
                        ],
                        "right_filters": [
                            {"column": "sex_label", "operator": "eq", "value": "male"},
                            {"column": "age_years", "operator": "gte", "value": 65},
                        ],
                        "metric": "mortality_rate",
                        "column": "mortality_flag",
                        "left_label": "female_65_plus",
                        "right_label": "male_65_plus",
                    }
                ],
                "order_by": [],
                "limit": None,
                "requires_clarification": False,
                "confidence": 1.0,
                "notes": ["Semi-synthetic benchmark template."],
            },
        },
    ]


def generate_paraphrases(
    question: str,
    seed_paraphrases: list[str],
    analysis_family: str,
) -> list[str]:
    """Generate lightweight paraphrase variants around a canonical question.

    This is deterministic template-based augmentation, not model-generated text.
    """

    generated: list[str] = []
    normalized = question.rstrip("?")

    replacements = [
        (r"^What is ", "Report "),
        (r"^How many ", "Count "),
        (r"^Which ", "Identify which "),
        (r"^Compare ", "Show the comparison for "),
    ]
    for pattern, replacement in replacements:
        candidate = re.sub(pattern, replacement, normalized, count=1)
        if candidate != normalized:
            generated.append(candidate + "?")

    if "mortality rate" in normalized:
        generated.append(normalized.replace("mortality rate", "death rate") + "?")
        generated.append(normalized.replace("mortality rate", "in-hospital mortality rate") + "?")
    if "survival rate" in normalized:
        generated.append(normalized.replace("survival rate", "survival proportion") + "?")
    if "grouped by sex" in normalized:
        generated.append(normalized.replace("grouped by sex", "for male and female groups") + "?")
    if analysis_family == "cohort_comparison":
        generated.append("How do these two cohorts differ on the requested metric?")
    if analysis_family == "ranking":
        generated.append("Return the highest-ranked group for this metric.")

    deduped: list[str] = []
    seen = {question}
    for candidate in [*seed_paraphrases, *generated]:
        if candidate not in seen:
            deduped.append(candidate)
            seen.add(candidate)
    return deduped


def generate_benchmark_examples(frame: pd.DataFrame, split_name: str) -> list[BenchmarkExample]:
    """Generate deterministic benchmark examples for a dataset split."""

    examples: list[BenchmarkExample] = []
    for spec in _plan_specs():
        result = execute_plan(frame, spec["plan"])
        paraphrases = generate_paraphrases(
            spec["question"],
            list(spec["paraphrases"]),
            str(spec["metadata"]["analysis_family"]),
        )
        metadata = dict(spec["metadata"])
        plan = spec["plan"]
        filter_count = len(plan.get("filters", []))
        group_by_count = len(plan.get("group_by", []))
        aggregation_count = len(plan.get("aggregations", []))
        comparison_count = len(plan.get("comparisons", []))
        order_by_count = len(plan.get("order_by", []))
        operation_count = (
            filter_count
            + group_by_count
            + aggregation_count
            + comparison_count
            + order_by_count
            + (1 if plan.get("limit") is not None else 0)
        )
        metadata.update(
            {
                "split": split_name,
                "output_rows": len(result.result_frame),
                "input_rows": result.metadata.get("input_rows"),
                "question_length_chars": len(spec["question"]),
                "question_length_words": len(spec["question"].split()),
                "num_paraphrases": len(paraphrases),
                "num_generated_paraphrases": max(0, len(paraphrases) - len(spec["paraphrases"])),
                "num_filters": filter_count,
                "num_group_by": group_by_count,
                "num_aggregations": aggregation_count,
                "num_comparisons": comparison_count,
                "num_order_by": order_by_count,
                "has_limit": plan.get("limit") is not None,
                "operation_count": operation_count,
                "result_columns": list(result.result_frame.columns),
            }
        )
        examples.append(
            BenchmarkExample(
                question=spec["question"],
                gold_plan=plan,
                gold_result=result.result_frame,
                paraphrases=paraphrases,
                metadata=metadata,
            )
        )
    return examples


def save_benchmark_examples(examples: list[BenchmarkExample], path: str | Path) -> None:
    """Write benchmark examples to a JSON file."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    records = [example.to_record() for example in examples]
    output_path.write_text(json.dumps(records, indent=2), encoding="utf-8")


def load_benchmark_examples(path: str | Path) -> list[BenchmarkExample]:
    """Load serialized benchmark examples from a JSON file."""

    input_path = Path(path)
    records = json.loads(input_path.read_text(encoding="utf-8"))
    return [BenchmarkExample.from_record(record) for record in records]


def benchmark_summary(examples: list[BenchmarkExample]) -> dict[str, Any]:
    """Return lightweight summary stats for a benchmark set."""

    family_counts: dict[str, int] = {}
    complexity_counts: dict[str, int] = {}
    total_paraphrases = 0
    total_operation_count = 0
    max_operation_count = 0
    max_filter_count = 0
    for example in examples:
        family = str(example.metadata.get("analysis_family", "unknown"))
        complexity = str(example.metadata.get("complexity_tier", "unknown"))
        family_counts[family] = family_counts.get(family, 0) + 1
        complexity_counts[complexity] = complexity_counts.get(complexity, 0) + 1
        total_paraphrases += len(example.paraphrases)
        operation_count = int(example.metadata.get("operation_count", 0))
        filter_count = int(example.metadata.get("num_filters", 0))
        total_operation_count += operation_count
        max_operation_count = max(max_operation_count, operation_count)
        max_filter_count = max(max_filter_count, filter_count)

    return {
        "num_examples": len(examples),
        "num_paraphrases": total_paraphrases,
        "analysis_family_counts": family_counts,
        "complexity_tier_counts": complexity_counts,
        "avg_paraphrases_per_example": total_paraphrases / len(examples) if examples else 0.0,
        "avg_operation_count": total_operation_count / len(examples) if examples else 0.0,
        "max_operation_count": max_operation_count,
        "max_filter_count": max_filter_count,
    }


def default_benchmark_artifact_path(base_dir: str | Path, split_name: str) -> Path:
    """Return the standard artifact path for a benchmark split."""

    return Path(base_dir) / f"{split_name}_benchmark.json"


def save_split_benchmark_artifacts(
    split_to_examples: dict[str, list[BenchmarkExample]],
    base_dir: str | Path,
) -> dict[str, Path]:
    """Save benchmark artifacts for multiple splits using a standard layout."""

    output_paths: dict[str, Path] = {}
    for split_name, examples in split_to_examples.items():
        output_path = default_benchmark_artifact_path(base_dir, split_name)
        save_benchmark_examples(examples, output_path)
        output_paths[split_name] = output_path
    return output_paths
