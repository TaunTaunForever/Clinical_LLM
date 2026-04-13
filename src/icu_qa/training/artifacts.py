"""Load and summarize fine-tuning artifacts."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    input_path = Path(path)
    records: list[dict[str, Any]] = []
    with input_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))
    return records


def load_supervised_records(path: str | Path) -> list[dict[str, Any]]:
    """Load supervised JSONL fine-tuning records."""

    return _load_jsonl(path)


def load_chat_records(path: str | Path) -> list[dict[str, Any]]:
    """Load chat-style JSONL fine-tuning records."""

    return _load_jsonl(path)


@dataclass(slots=True)
class FineTuneArtifactSummary:
    """Summary statistics for a fine-tuning artifact."""

    num_examples: int
    avg_input_chars: float
    avg_target_chars: float
    complexity_tier_counts: dict[str, int]
    analysis_family_counts: dict[str, int]


def summarize_finetune_records(records: list[dict[str, Any]], format_name: str) -> FineTuneArtifactSummary:
    """Summarize fine-tuning records for sanity-checking."""

    if not records:
        return FineTuneArtifactSummary(
            num_examples=0,
            avg_input_chars=0.0,
            avg_target_chars=0.0,
            complexity_tier_counts={},
            analysis_family_counts={},
        )

    total_input_chars = 0
    total_target_chars = 0
    complexity_tier_counts: dict[str, int] = {}
    analysis_family_counts: dict[str, int] = {}

    for record in records:
        metadata = record.get("metadata", {})
        complexity = str(metadata.get("complexity_tier", "unknown"))
        family = str(metadata.get("analysis_family", "unknown"))
        complexity_tier_counts[complexity] = complexity_tier_counts.get(complexity, 0) + 1
        analysis_family_counts[family] = analysis_family_counts.get(family, 0) + 1

        if format_name == "supervised":
            total_input_chars += len(str(record.get("input_text", "")))
            total_target_chars += len(str(record.get("target_text", "")))
        else:
            messages = record.get("messages", [])
            user_messages = [m for m in messages if m.get("role") == "user"]
            assistant_messages = [m for m in messages if m.get("role") == "assistant"]
            total_input_chars += sum(len(str(m.get("content", ""))) for m in user_messages)
            total_target_chars += sum(len(str(m.get("content", ""))) for m in assistant_messages)

    count = len(records)
    return FineTuneArtifactSummary(
        num_examples=count,
        avg_input_chars=total_input_chars / count,
        avg_target_chars=total_target_chars / count,
        complexity_tier_counts=complexity_tier_counts,
        analysis_family_counts=analysis_family_counts,
    )
