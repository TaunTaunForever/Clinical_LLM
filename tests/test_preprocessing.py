import pandas as pd

from icu_qa.data.preprocessing import preprocess_sepsis_survival_dataset


def test_preprocess_sepsis_survival_dataset_derives_analysis_columns() -> None:
    frame = pd.DataFrame(
        {
            "age_years": [65, 72],
            "sex_0male_1female": [0, 1],
            "episode_number": [1, 2],
            "hospital_outcome_1alive_0dead": [1, 0],
        }
    )

    processed = preprocess_sepsis_survival_dataset(frame)

    assert list(processed["sex_label"]) == ["male", "female"]
    assert list(processed["survival_flag"]) == [1, 0]
    assert list(processed["mortality_flag"]) == [0, 1]
