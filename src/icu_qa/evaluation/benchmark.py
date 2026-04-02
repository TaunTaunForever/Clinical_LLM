"""Benchmark example structures and simple runner helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pandas as pd


@dataclass(slots=True)
class BenchmarkExample:
    """One benchmark example for planner or end-to-end evaluation."""

    question: str
    gold_plan: dict[str, Any]
    gold_result: pd.DataFrame | None = None
    paraphrases: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
