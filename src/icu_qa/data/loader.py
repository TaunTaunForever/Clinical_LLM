"""Dataset loading utilities."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from icu_qa.config import Settings
from icu_qa.data.preprocessing import preprocess_sepsis_survival_dataset


def load_csv_dataset(path: str | Path) -> pd.DataFrame:
    """Load a local CSV dataset for deterministic analytics."""

    csv_path = Path(path)
    if not csv_path.exists():
        raise FileNotFoundError(f"Dataset not found: {csv_path}")
    return pd.read_csv(csv_path)


def load_default_dataset(settings: Settings | None = None) -> pd.DataFrame:
    """Load and preprocess the configured default evaluation dataset."""

    active_settings = settings or Settings()
    frame = load_csv_dataset(active_settings.resolved_evaluation_data_path())
    return preprocess_sepsis_survival_dataset(frame)


def load_training_dataset(settings: Settings | None = None) -> pd.DataFrame:
    """Load and preprocess the configured training dataset."""

    active_settings = settings or Settings()
    frame = load_csv_dataset(active_settings.resolved_training_data_path())
    return preprocess_sepsis_survival_dataset(frame)


def load_evaluation_dataset(settings: Settings | None = None) -> pd.DataFrame:
    """Load and preprocess the configured evaluation dataset."""

    return load_default_dataset(settings)


def load_heldout_dataset(settings: Settings | None = None) -> pd.DataFrame:
    """Load and preprocess the configured held-out dataset."""

    active_settings = settings or Settings()
    frame = load_csv_dataset(active_settings.resolved_heldout_data_path())
    return preprocess_sepsis_survival_dataset(frame)
