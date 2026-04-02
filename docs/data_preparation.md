# Data Preparation

## Phase 1 assumption

The repository is now bound to a local CSV-based sepsis outcomes dataset:

- dataset directory: `s41598-020-73558-3_sepsis_survival_dataset`
- training cohort: `s41598-020-73558-3_sepsis_survival_primary_cohort.csv`
- evaluation cohort: `s41598-020-73558-3_sepsis_survival_study_cohort.csv`
- held-out cohort: `s41598-020-73558-3_sepsis_survival_validation_cohort.csv`

The project now uses the primary cohort for training-oriented workflows and the study cohort for evaluation-oriented workflows.

## Expected workflow

1. Load the configured primary cohort for training data generation workflows or the study cohort for evaluation workflows.
2. Normalize column names deterministically.
3. Derive analysis-friendly fields used by the planner and execution engine.
4. Materialize schema metadata for planner prompting and validator checks.

## Observed dataset profile

The three discovered cohort files are:

- `s41598-020-73558-3_sepsis_survival_primary_cohort.csv` with 110,204 rows
- `s41598-020-73558-3_sepsis_survival_study_cohort.csv` with 19,051 rows
- `s41598-020-73558-3_sepsis_survival_validation_cohort.csv` with 137 rows

All three share four raw columns:

- `age_years`
- `sex_0male_1female`
- `episode_number`
- `hospital_outcome_1alive_0dead`

## Current split

- training split: primary cohort with 110,204 rows
- evaluation split: study cohort with 19,051 rows
- holdout/reference split: validation cohort with 137 rows

## Current dataset characteristics

The current bound dataset supports a narrow but usable subset of analytics fields:

- episode identifier
- age
- binary sex encoding
- hospital outcome

The preprocessing step additionally derives:

- `sex_label`
- `survival_flag`
- `mortality_flag`

## Phase 1 preprocessing goals

- normalize column names
- standardize simple categorical encodings where practical
- preserve raw outcome fields needed for deterministic aggregations
- compute lightweight derived fields only if they are deterministic and documented

For the bound sepsis survival dataset, this currently means:

- mapping `sex_0male_1female` to `sex_label`
- converting `hospital_outcome_1alive_0dead` into `survival_flag`
- deriving `mortality_flag` as `1 - survival_flag`

## TODO

- add richer dataset-specific descriptions for planner prompting
- decide how the validation cohort should be used in later benchmark design
- extend the schema once a dataset with richer ICU variables is added
