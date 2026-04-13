"""Human-authored challenge set scaffolding."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class ChallengeQuestion:
    """One human-authored challenge question scaffold."""

    question: str
    rationale: str
    expected_behavior: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_record(self) -> dict[str, Any]:
        return {
            "question": self.question,
            "rationale": self.rationale,
            "expected_behavior": self.expected_behavior,
            "metadata": self.metadata,
        }


def default_challenge_set() -> list[ChallengeQuestion]:
    """Return a starter scaffold for future human-authored challenge questions."""

    return [
        ChallengeQuestion(
            question="What happened to older women compared with younger men?",
            rationale="Intentionally mixes age and sex cohorts in a comparison question.",
            expected_behavior=(
                "Either map cleanly to a supported cohort comparison or request clarification "
                "if the comparison framing is too ambiguous."
            ),
            metadata={"status": "placeholder", "challenge_type": "ambiguous_comparison"},
        ),
        ChallengeQuestion(
            question="Show me the sickest subgroup.",
            rationale="Uses unsupported clinical language that is not represented in the dataset.",
            expected_behavior="Reject or request clarification because severity is not defined in the schema.",
            metadata={"status": "placeholder", "challenge_type": "unsupported_semantics"},
        ),
    ]


def save_challenge_set_template(path: str | Path) -> Path:
    """Write a starter human-authored challenge set scaffold."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    records = [challenge.to_record() for challenge in default_challenge_set()]
    output_path.write_text(json.dumps(records, indent=2), encoding="utf-8")
    return output_path


def load_challenge_questions(path: str | Path) -> list[ChallengeQuestion]:
    """Load human-authored challenge questions from JSON."""

    input_path = Path(path)
    records = json.loads(input_path.read_text(encoding="utf-8"))
    return [
        ChallengeQuestion(
            question=record["question"],
            rationale=record["rationale"],
            expected_behavior=record["expected_behavior"],
            metadata=dict(record.get("metadata", {})),
        )
        for record in records
    ]
