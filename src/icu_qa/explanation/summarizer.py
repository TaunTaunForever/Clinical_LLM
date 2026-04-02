"""Safe explanation scaffolding over computed outputs."""

from __future__ import annotations

import pandas as pd


def summarize_result(result_frame: pd.DataFrame, question: str) -> str:
    """Return a conservative summary using computed outputs only.

    TODO: Replace with a richer explanation layer that still remains
    grounded in the result table.
    """

    if result_frame.empty:
        return (
            "The retrospective dataset query returned no rows for the requested analysis. "
            "No clinical interpretation should be inferred from this result."
        )

    preview = result_frame.head(3).to_dict(orient="records")
    return (
        "This summary is based only on the computed retrospective dataset result. "
        f"For question '{question}', the result contains {len(result_frame)} rows. "
        f"Preview: {preview}."
    )
