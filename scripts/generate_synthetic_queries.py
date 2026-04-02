"""Generate starter semi-synthetic query examples."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


def build_seed_examples() -> list[dict[str, object]]:
    """Return a tiny starter set of hand-authored templates.

    TODO: Replace with dataset-driven plan generation and execution.
    """

    return [
        {
            "question": "What is the mortality rate for the full cohort?",
            "plan": {
                "intent": "summarize_mortality",
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
                "notes": ["Seed example for Phase 1."],
            },
        }
    ]


def main() -> None:
    print(json.dumps(build_seed_examples(), indent=2))


if __name__ == "__main__":
    main()
