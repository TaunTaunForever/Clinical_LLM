from pathlib import Path

from icu_qa.evaluation.challenges import load_challenge_questions, save_challenge_set_template


def test_save_and_load_challenge_set_template(tmp_path: Path) -> None:
    output_path = tmp_path / "challenge_set.json"
    save_challenge_set_template(output_path)
    challenges = load_challenge_questions(output_path)

    assert len(challenges) >= 2
    assert challenges[0].metadata["status"] == "placeholder"
