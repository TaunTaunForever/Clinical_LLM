"""Fine-tuning dataset export helpers."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from icu_qa.data.schema import build_sepsis_survival_schema
from icu_qa.evaluation.benchmark import BenchmarkExample
from icu_qa.planning.prompt_templates import build_planner_system_prompt, build_planner_user_prompt

FineTuneFormat = Literal["supervised", "chat"]


@dataclass(slots=True)
class FineTuneExample:
    """One serialized training example for planner fine-tuning."""

    question: str
    target_text: str
    system_prompt: str
    user_prompt: str
    metadata: dict[str, Any]

    def to_supervised_record(self) -> dict[str, Any]:
        """Return a generic supervised fine-tuning record."""

        return {
            "question": self.question,
            "input_text": self.user_prompt,
            "target_text": self.target_text,
            "metadata": self.metadata,
        }

    def to_chat_record(self) -> dict[str, Any]:
        """Return a chat-style fine-tuning record."""

        return {
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": self.user_prompt},
                {"role": "assistant", "content": self.target_text},
            ],
            "metadata": self.metadata,
        }


def canonical_plan_json(plan: dict[str, Any]) -> str:
    """Return a deterministic JSON string for a gold planner target."""

    return json.dumps(plan, sort_keys=True, separators=(",", ":"))


def benchmark_to_finetune_examples(
    examples: list[BenchmarkExample],
    split_name: str,
) -> list[FineTuneExample]:
    """Convert benchmark examples into fine-tuning-ready examples."""

    schema = build_sepsis_survival_schema(split_name=split_name)
    system_prompt = build_planner_system_prompt()
    finetune_examples: list[FineTuneExample] = []

    for example in examples:
        metadata = dict(example.metadata)
        metadata.update(
            {
                "split": split_name,
                "target_format": "json_plan",
            }
        )
        finetune_examples.append(
            FineTuneExample(
                question=example.question,
                target_text=canonical_plan_json(example.gold_plan),
                system_prompt=system_prompt,
                user_prompt=build_planner_user_prompt(example.question, schema=schema),
                metadata=metadata,
            )
        )
    return finetune_examples


def save_finetune_examples_jsonl(
    examples: list[FineTuneExample],
    path: str | Path,
    *,
    format_name: FineTuneFormat,
) -> None:
    """Write fine-tuning examples to JSONL."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        for example in examples:
            if format_name == "supervised":
                record = example.to_supervised_record()
            else:
                record = example.to_chat_record()
            handle.write(json.dumps(record) + "\n")


def default_finetune_artifact_paths(base_dir: str | Path, split_name: str) -> dict[str, Path]:
    """Return standard fine-tuning artifact paths for a split."""

    base_path = Path(base_dir)
    return {
        "supervised": base_path / f"{split_name}_planner_supervised.jsonl",
        "chat": base_path / f"{split_name}_planner_chat.jsonl",
    }


def save_finetune_split_artifacts(
    split_to_examples: dict[str, list[FineTuneExample]],
    base_dir: str | Path,
) -> dict[str, dict[str, Path]]:
    """Save standard fine-tuning artifacts for multiple splits."""

    output_paths: dict[str, dict[str, Path]] = {}
    for split_name, examples in split_to_examples.items():
        split_paths = default_finetune_artifact_paths(base_dir, split_name)
        save_finetune_examples_jsonl(
            examples,
            split_paths["supervised"],
            format_name="supervised",
        )
        save_finetune_examples_jsonl(
            examples,
            split_paths["chat"],
            format_name="chat",
        )
        output_paths[split_name] = split_paths
    return output_paths
