from icu_qa.config import Settings


def test_settings_use_primary_for_training_and_study_for_evaluation() -> None:
    settings = Settings()

    assert settings.training_dataset_name == "sepsis_survival_primary_cohort"
    assert settings.evaluation_dataset_name == "sepsis_survival_study_cohort"
    assert settings.heldout_dataset_name == "sepsis_survival_validation_cohort"
    assert settings.resolved_training_data_path().name.endswith("primary_cohort.csv")
    assert settings.resolved_evaluation_data_path().name.endswith("study_cohort.csv")
    assert settings.resolved_heldout_data_path().name.endswith("validation_cohort.csv")
