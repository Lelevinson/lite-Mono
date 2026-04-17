# Final Label Route Decision

Date: 2026-04-17

Decision: use `exact_lidar_parent_child_inverted` as the default LiDAR-to-ZED transform for final Citrus dense-label generation.

## Evidence Used

### 1. Transform Candidate Audit

Four physically meaningful calibration-chain interpretations were checked:

- `production_current`
- `current_chain_no_invert`
- `exact_lidar_parent_child_direct`
- `exact_lidar_parent_child_inverted`

The two direct/no-invert variants produced clearly wrong vertical projection bands. The remaining plausible routes were:

- Route A: `production_current`
- Route B: `exact_lidar_parent_child_inverted`

### 2. Time-Spread Quantitative Probe

Source:

- `research/dataset_audit/time_spread_metrics_200_summary.md`
- raw CSV: `datasets/citrus-farm-dataset/projection_alignment_audit/time_spread_metrics_200/audit_metrics.csv`

Key result:

- Route A had higher dense fill on 198/200 samples.
- Route B had lower ZED absolute difference on 200/200 samples.
- Route B had lower ZED relative difference on 200/200 samples.

Median route comparison:

| Metric | Route A: production_current | Route B: exact_lidar_parent_child_inverted |
|---|---:|---:|
| Dense fill ratio | 42.46% | 36.63% |
| ZED/LiDAR overlap ratio | 23.13% | 21.25% |
| ZED median absolute difference | 0.538 m | 0.192 m |
| ZED median relative difference | 22.12% | 6.90% |

### 3. Final Visual Spot-Check

Command:

```powershell
D:/Conda_Envs/lite-mono/python.exe datasets/citrus-farm-dataset/audit_projection_alignment.py --max_samples 12 --output_dir projection_alignment_audit/time_spread_visual_12
```

Generated local visual diagnostics:

- `datasets/citrus-farm-dataset/projection_alignment_audit/time_spread_visual_12/overlays/`
- `datasets/citrus-farm-dataset/projection_alignment_audit/time_spread_visual_12/details_production_current/`
- `datasets/citrus-farm-dataset/projection_alignment_audit/time_spread_visual_12/details_exact_lidar_parent_child_inverted/`

Visual result:

- Route B keeps the natural horizontal LiDAR scan structure.
- Route B remains visually plausible across time-spread samples.
- The two rejected transform candidates remain visibly wrong.

## Rationale

`production_current` gives more filled pixels, but label coverage is less important than label correctness. For training and evaluation, lower-coverage labels with a valid mask are preferable to denser labels whose depth values disagree strongly with ZED depth.

The final route therefore prioritizes:

- lower ZED agreement error
- physically plausible overlays
- conservative `local_idw` densification
- valid-mask-aware training/evaluation

## Implementation State

The code default has been changed so the final/default transform is:

```text
exact_lidar_parent_child_inverted
```

`production_current` remains available as an alternate comparison route through `--transform_mode production_current`.

A one-sample smoke build verified that the default builder path uses `exact_lidar_parent_child_inverted`. The throwaway output folder was removed after validation.

## Remaining Heavy Step

The full prepared dataset has not been generated in this cleanup commit because it is a large local artifact. The next full build should use:

```powershell
D:/Conda_Envs/lite-mono/python.exe build_training_dataset.py
```

This should now write the final default route to `prepared_training_dataset/`.
