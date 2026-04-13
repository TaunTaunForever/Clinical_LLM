"""Initialize a human-authored challenge question scaffold."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from icu_qa.evaluation.challenges import save_challenge_set_template


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize a human-authored challenge set scaffold.")
    parser.add_argument(
        "--output-path",
        default="artifacts/challenges/human_authored_challenges.json",
        help="Path to write the challenge set scaffold",
    )
    args = parser.parse_args()

    output_path = save_challenge_set_template(args.output_path)
    print(f"Wrote challenge set scaffold to {output_path.resolve()}")


if __name__ == "__main__":
    main()
