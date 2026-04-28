# Baseline Notes

This file is the single place for baseline-model notes and early model checks that may later support the paper.

## Original Lite-Mono Single-Image Citrus Demo

Date: 2026-04-16

Paper relevance: qualitative baseline / motivation artifact only. This is not a full baseline result.

Purpose: verify that original pretrained Lite-Mono can run on an extracted Citrus RGB frame and produce a full-image disparity visualization.

### Command

The input image was copied out of the dataset folder first so generated outputs do not contaminate extracted dataset artifacts.

```powershell
D:/Conda_Envs/lite-mono/python.exe test_simple.py --load_weights_folder weights/lite-mono --image_path citrus_project/research/generated/lite_mono_single_image_demo/zed_2023-07-18-14-26-49_0_bag_1689715609331936216.png --model lite-mono --no_cuda
```

### Local Generated Files

These files are ignored by git:

- `citrus_project/research/generated/lite_mono_single_image_demo/zed_2023-07-18-14-26-49_0_bag_1689715609331936216.png`
- `citrus_project/research/generated/lite_mono_single_image_demo/zed_2023-07-18-14-26-49_0_bag_1689715609331936216_disp.jpeg`
- `citrus_project/research/generated/lite_mono_single_image_demo/zed_2023-07-18-14-26-49_0_bag_1689715609331936216_disp.npy`

### Interpretation

This run shows that original Lite-Mono can produce a dense prediction on a Citrus RGB image. It starts the baseline milestone, but it does not complete it.

To complete the baseline milestone, the project still needs:

- original Lite-Mono inference on a validation/test split
- evaluation against LiDAR-densified labels and valid masks
- Citrus-specific metrics without KITTI crop assumptions
- runtime, parameter count, and model-size reporting
- qualitative failure-case analysis in vegetation-heavy scenes

### How This Can Appear In The Paper

Use this kind of output later as a qualitative figure only after we generate a proper set of baseline predictions on selected validation/test frames.

Possible paper figure:

- RGB input
- original Lite-Mono prediction
- LiDAR-densified label visualization
- valid mask
- improved model prediction

Do not use the current single-image run as a quantitative result.

## Original Lite-Mono Citrus Evaluator Slice 3 Smoke Metrics

Date: 2026-04-28

Paper relevance: implementation sanity check only. This is not the full baseline result because it uses one validation image.

Purpose: verify that the Citrus evaluator can compare original Lite-Mono predicted depth against LiDAR-densified labels using the valid mask.

### Command

```powershell
D:/Conda_Envs/lite-mono/python.exe citrus_project/milestones/01_original_lite_mono_baseline/evaluate_lite_mono_citrus.py --split val --max_samples 1 --run_model --no_cuda
```

### Sample

- RGB: `extracted_rgbd/zed2i_zed_node_left_image_rect_color/zed_2023-07-18-14-33-03_13_bag_1689715983638853080.png`
- Dense label: `prepared_training_dataset/dense_lidar_npz/zed_2023-07-18-14-33-03_13_bag_1689715983638853080.npz`
- Valid mask: `prepared_training_dataset/dense_lidar_valid_mask_npz/zed_2023-07-18-14-33-03_13_bag_1689715983638853080.npz`

### One-Sample Output

- evaluation mask: 363835 / 921600 pixels, 39.4786%
- label median: 1.917563 m
- raw prediction median: 0.582838 m
- median scale ratio: 3.290044
- raw-scale metrics: `abs_rel=0.7046`, `sq_rel=1.7498`, `rmse=3.9727`, `rmse_log=1.3157`, `a1=0.0010`, `a2=0.0027`, `a3=0.0083`
- median-scaled metrics: `abs_rel=0.1993`, `sq_rel=0.5087`, `rmse=2.9395`, `rmse_log=0.3596`, `a1=0.7054`, `a2=0.8697`, `a3=0.9219`

### Interpretation

The raw-scale metrics are poor because the original pretrained model predicts this Citrus scene much closer than the LiDAR label median. Median scaling substantially improves the threshold metrics, which suggests this one sample has more usable relative depth structure than raw metric scale.

Do not report this as the baseline. The next evaluator slice should aggregate the same metrics over the validation/test split and save reproducible outputs.

## Original Lite-Mono Citrus Evaluator Slice 4 Aggregate Smoke Metrics

Date: 2026-04-28

Paper relevance: implementation sanity check only. This is not the full baseline result because it uses only three validation images and does not save result files yet.

Purpose: verify that the Citrus evaluator can accumulate per-image metric rows and print aggregate raw-scale plus median-scaled metric summaries.

### Command

```powershell
D:/Conda_Envs/lite-mono/python.exe citrus_project/milestones/01_original_lite_mono_baseline/evaluate_lite_mono_citrus.py --split val --max_samples 3 --run_model --summary_only --progress_interval 1 --no_cuda
```

### One Small Aggregate Output

- requested samples: 3
- samples with metrics: 3
- total valid pixels: 1089872
- mean valid fraction: 39.4196%
- median scale ratio: 3.290044
- mean scale ratio: 3.276223
- mean raw-scale metrics: `abs_rel=0.7083`, `sq_rel=1.7740`, `rmse=4.0042`, `rmse_log=1.3373`, `a1=0.0014`, `a2=0.0034`, `a3=0.0098`
- mean median-scaled metrics: `abs_rel=0.2061`, `sq_rel=0.5604`, `rmse=3.0122`, `rmse_log=0.3828`, `a1=0.6978`, `a2=0.8520`, `a3=0.9111`

### Interpretation

The aggregation logic now follows the original Lite-Mono evaluation style: compute metrics per image, then average the image metric rows. This prevents images with more valid LiDAR pixels from dominating the score.

The full validation/test baseline is still pending. The next evaluator slice should save reproducible CSV/JSON outputs before the final full-run numbers are treated as results.

## Original Lite-Mono Citrus Evaluator Slice 5 Saved-Result Smoke Check

Date: 2026-04-28

Paper relevance: implementation sanity check only. This confirms result-file saving works, but it is still only a three-image validation smoke run.

Purpose: verify that the evaluator can save the aggregate summary and per-sample metric rows into the Milestone 1 results folder.

### Command

```powershell
D:/Conda_Envs/lite-mono/python.exe citrus_project/milestones/01_original_lite_mono_baseline/evaluate_lite_mono_citrus.py --split val --max_samples 3 --run_model --summary_only --progress_interval 1 --no_cuda --output_dir citrus_project/milestones/01_original_lite_mono_baseline/results
```

### Local Generated Files

These smoke files are ignored by the Milestone 1 results folder `.gitignore` because they contain `max3` and are not official full-split results:

- `citrus_project/milestones/01_original_lite_mono_baseline/results/val_lite-mono_max3_summary.json`
- `citrus_project/milestones/01_original_lite_mono_baseline/results/val_lite-mono_max3_per_sample.csv`

### Interpretation

The summary JSON stores the aggregate run settings and mean metrics. The per-sample CSV stores one row per evaluated image for later hard/easy sample analysis.

The final baseline should be produced later with `--max_samples 0` on the validation and test splits, ideally when GPU is available.

## Original Lite-Mono Citrus Evaluator Slice 6 Runtime/FPS Smoke Check

Date: 2026-04-28

Paper relevance: timing pipeline sanity check only. This confirms runtime metadata is saved, but it is not a final deployment benchmark.

Purpose: verify that the evaluator records both end-to-end evaluator timing and synchronized model-forward timing in the saved result files.

### Command

```powershell
D:/Conda_Envs/lite-mono/python.exe citrus_project/milestones/01_original_lite_mono_baseline/evaluate_lite_mono_citrus.py --split val --max_samples 3 --run_model --summary_only --progress_interval 1 --output_dir citrus_project/milestones/01_original_lite_mono_baseline/results
```

### GPU Visibility

- CUDA available: yes
- device: NVIDIA GeForce RTX 4060 Laptop GPU

### Smoke Timing Output

For the three-image validation smoke run:

- device: `cuda`
- model load seconds: 6.167
- evaluation loop seconds: 1.556
- total run seconds: 7.800
- metric samples per second: 1.928
- model forward FPS: 2.706

### Interpretation

The first GPU sample includes CUDA warmup overhead, so this small `max3` run should not be used as the paper's FPS result. It only proves that timing fields are now recorded.

The full validation/test run will give a more stable evaluator-level timing estimate, but a dedicated deployment benchmark may still be needed later for a clean robot-runtime/FPS claim.

