# Paper Shortlist

This file tracks research artifacts that may later become paper tables, figures, or method details.

## Strong Candidates

### Original Lite-Mono Full Citrus Baseline

Evidence notes:

- `citrus_project/research/baseline_notes.md`
- `citrus_project/milestones/01_original_lite_mono_baseline/results/val_lite-mono_full_summary.json`
- `citrus_project/milestones/01_original_lite_mono_baseline/results/test_lite-mono_full_summary.json`

Why it matters:

- Provides the first full validation/test quantitative baseline for original pretrained Lite-Mono on Citrus.
- Supports the domain-gap argument: raw absolute scale is poor and median-scaled scores still leave substantial room for improvement.
- Gives lightweight-model metadata alongside accuracy: 3.075M depth-inference parameters and about 11.94 MiB of checkpoint weights.

Paper section fit:

- Experimental setup
- Baseline results
- Motivation for Citrus adaptation / vegetation-focused improvement
- Efficiency comparison

Current status:

- Full validation and test runs completed on 2026-04-28.
- First validation good/typical/bad visual panels were generated on 2026-04-28 using `median_scaled_a1`.
- Test good/typical/bad visual panels were generated on 2026-04-29 using `median_scaled_a1`.
- First written failure-case interpretation exists in `citrus_project/milestones/01_original_lite_mono_baseline/visual_interpretation.md`.
- Needs a tighter final figure/table design before it is a complete paper package.

### Dataset/Label Route Selection

Evidence notes:

- `citrus_project/research/dataset_notes.md`
- raw metrics: `citrus_project/dataset_workspace/projection_alignment_audit/time_spread_metrics_200/audit_metrics.csv`

Why it matters:

- Shows the LiDAR-to-camera transform route was selected using a time-spread quantitative check.
- Supports the claim that label generation was validated rather than assumed.
- Provides a table-ready comparison between `production_current` and `exact_lidar_parent_child_inverted`.

Paper section fit:

- Dataset construction
- Ground-truth / pseudo-label generation
- Calibration validation

Current status:

- Locked as the final/default dense-label route: `exact_lidar_parent_child_inverted`.
- Full prepared dataset build is now complete with 5282 samples and time-block splits of train=4311, val=564, test=407.

### Final Prepared Dataset Version

Evidence notes:

- `citrus_project/research/dataset_notes.md`
- `citrus_project/dataset_workspace/prepared_training_dataset/metrics/summary.json`

Why it matters:

- Gives the paper a concrete dataset version and split counts instead of only planned counts.
- Supports the reproducibility story around label generation, split policy, and evaluation setup.

Paper section fit:

- Dataset construction
- Experimental setup
- Reproducibility details

Current status:

- Built successfully on 2026-04-23.
- Ready to support Milestone 1 baseline evaluation.

### Conservative Dense Label Generation

Evidence notes:

- `citrus_project/dataset_workspace/densify_lidar.py`
- `citrus_project/research/dataset_notes.md`

Why it matters:

- `local_idw` fills only near LiDAR support and rejects fills when neighboring depths disagree too much.
- This supports a paper-facing argument that sparse vegetation labels should prefer validity masks over visually full but hallucinated labels.

Paper section fit:

- Dataset preprocessing
- Label reliability
- Training/evaluation mask construction

Current status:

- Implemented and tested.
- Needs final parameter lock before full dataset build.

## Early Candidates

### Milestone 3 Self-Supervised Adaptation Instability

Evidence notes:

- `citrus_project/research/baseline_notes.md`
- `citrus_project/milestones/03_self_supervised_adaptation/README.md`
- ignored run outputs under `citrus_project/milestones/03_self_supervised_adaptation/runs/`

Why it matters:

- Shows that a plain self-supervised Citrus adaptation baseline is not automatically better than the untouched original model.
- The conservative 1000-step probe still worsened first-100 validation median-scaled depth quality: final `abs_rel=0.6615`, `a1=0.1827`, versus untouched baseline `abs_rel=0.3680`, `a1=0.4807`.
- Side-by-side visual panels show the adapted checkpoint becoming smoother and less structurally specific than the original baseline on selected validation examples.
- A no-color-augmentation 250-step control improved over the color-augmented 250-step control, but still did not beat the untouched baseline on median-scaled relative-depth metrics.
- Extending the no-color-augmentation control to 500 steps worsened relative-depth metrics again: `abs_rel=0.5300`, `a1=0.3513`.
- This is useful motivation for a Milestone 4 structure-preserving or vegetation-aware improvement, as long as it is presented carefully as negative/diagnostic evidence.

Paper section fit:

- Baseline adaptation results
- Failure analysis
- Motivation for proposed method

Current status:

- Documented as weak/negative adapted-baseline evidence.
- Use carefully: it supports the claim that standard self-supervised Citrus adaptation is not enough under the tested recipe family, rather than claiming all possible adaptation can never work.
- Next paper-facing need is to compare the future Milestone 4 improvement against original Lite-Mono and this documented Milestone 3 failure pattern.
- Visual comparison panels were generated on 2026-05-07 under the Milestone 3 ignored run folder.

### Original Lite-Mono Qualitative Citrus Prediction

Evidence notes:

- `citrus_project/research/baseline_notes.md`
- generated local files under `citrus_project/research/generated/lite_mono_single_image_demo/`

Why it matters:

- Demonstrates original Lite-Mono can run on Citrus RGB frames.
- Useful as an early qualitative baseline/motivation example.

Paper section fit:

- Motivation
- Qualitative baseline comparison
- Failure-case analysis

Current status:

- Single-image sanity demo only.
- Quantitative claims should use the full baseline outputs above, not this demo.
- Still useful as a possible qualitative example source if regenerated consistently with labels and masks.

## Not Paper Evidence Yet

### Completed Presentation Slides

Source:

- removed after presentation cleanup

Why not:

- Useful for explaining progress at the time, but not a primary research artifact.
- Any table/figure from it should be regenerated from raw metrics or tracked research summaries before paper use.

