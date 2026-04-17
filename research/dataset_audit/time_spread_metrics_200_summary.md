# Time-Spread Metrics Probe Summary

Date: 2026-04-16

Paper relevance: candidate content for the dataset construction / label-quality validation section.

Purpose: compare the two plausible LiDAR-to-camera label routes on a wider, time-spread sample before locking the final dataset route.

Raw output files:

- `datasets/citrus-farm-dataset/projection_alignment_audit/time_spread_metrics_200/audit_metrics.csv`
- `datasets/citrus-farm-dataset/projection_alignment_audit/time_spread_metrics_200/audit_summary.json`

Command:

```powershell
D:/Conda_Envs/lite-mono/python.exe datasets/citrus-farm-dataset/audit_projection_alignment.py --max_samples 200 --metrics_only --output_dir projection_alignment_audit/time_spread_metrics_200
```

## What Was Tested

- 200 RGB-LiDAR pairs selected across 5282 matched pairs.
- Interpolation method: `local_idw`.
- Route A: `production_current`.
- Route B: `exact_lidar_parent_child_inverted`.
- This was a metrics-only run, so it did not generate 200 image panels.

## Timing Quality

| Metric | Median |
|---|---:|
| RGB-LiDAR timestamp difference | 27.874 ms |
| RGB-ZED depth timestamp difference | 12.711 ms |

## Route Comparison

| Metric | Route A: production_current | Route B: exact_lidar_parent_child_inverted | Better direction |
|---|---:|---:|---|
| Dense fill ratio | 42.46% | 36.63% | Higher gives more label coverage |
| ZED/LiDAR overlap ratio | 23.13% | 21.25% | Higher gives more comparison area |
| ZED median absolute difference | 0.538 m | 0.192 m | Lower is closer to ZED |
| ZED median relative difference | 22.12% | 6.90% | Lower is closer to ZED |
| Valid projected ratio | 32.82% | 32.91% | Higher means more projected points land validly |

## Pairwise Result

- Route A had higher dense fill on 198/200 samples.
- Route B had lower ZED absolute difference on 200/200 samples.
- Route B had lower ZED relative difference on 200/200 samples.

## Interpretation

Route A produces more filled label pixels, but Route B agrees much better with ZED depth wherever both labels can be compared.

Decision status:

- `exact_lidar_parent_child_inverted` was selected as the final/default label route after a 12-sample time-spread visual spot-check.
- See `research/dataset_audit/final_label_route_decision.md`.

## How This Can Appear In The Paper

Use as evidence that the final LiDAR-densified label route was selected by a quantitative time-spread audit plus visual spot-checking, not by a single visual example.

Possible paper table:

- route name
- dense fill ratio
- ZED/LiDAR overlap
- median ZED absolute difference
- median ZED relative difference

Possible paper text:

> We evaluated candidate LiDAR-to-camera transform conventions on a time-spread subset of 200 RGB-LiDAR pairs. Although the production-current route yielded higher dense-label coverage, the exact inverted calibration chain had lower ZED agreement error on all paired comparisons. A follow-up visual audit confirmed plausible alignment, so this route was selected for final dense-label generation.
