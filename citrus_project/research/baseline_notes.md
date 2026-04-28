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

## Original Lite-Mono Citrus Evaluator Slice 7 Parameter/Checkpoint Smoke Check

Date: 2026-04-28

Paper relevance: model-efficiency metadata. These are the parameter and checkpoint-size fields that should accompany the original Lite-Mono baseline.

Purpose: verify that the evaluator records model-size metadata in the terminal and saved summary JSON.

### Command

```powershell
D:/Conda_Envs/lite-mono/python.exe citrus_project/milestones/01_original_lite_mono_baseline/evaluate_lite_mono_citrus.py --split val --max_samples 2 --run_model --summary_only --progress_interval 1 --output_dir citrus_project/milestones/01_original_lite_mono_baseline/results
```

### Model Metadata

- model variant: `lite-mono`
- device in smoke run: `cuda`
- total depth-inference parameters: 3,074,747
- encoder parameters: 2,848,120
- depth-decoder parameters: 226,627
- total checkpoint size: 11.94 MiB

### Interpretation

The parameter count includes the encoder and depth decoder used during RGB-only depth inference. It does not include the training-only pose network.

This metadata is now saved in summary JSON under `model_info`, so final full-split result files can support both accuracy and lightweight-model reporting.

## Original Lite-Mono Full Citrus Validation/Test Baseline

Date: 2026-04-28

Paper relevance: first real quantitative original Lite-Mono baseline on Citrus. This is stronger evidence than the single-image demo and smoke tests because it evaluates the full validation and test splits against LiDAR-densified labels with valid masks.

Purpose: measure how the original pretrained Lite-Mono baseline behaves on the Citrus prepared dataset before any Citrus adaptation or method improvement.

### Commands

Validation:

```powershell
D:/Conda_Envs/lite-mono/python.exe citrus_project/milestones/01_original_lite_mono_baseline/evaluate_lite_mono_citrus.py --split val --max_samples 0 --run_model --summary_only --progress_interval 50 --output_dir citrus_project/milestones/01_original_lite_mono_baseline/results
```

Test:

```powershell
D:/Conda_Envs/lite-mono/python.exe citrus_project/milestones/01_original_lite_mono_baseline/evaluate_lite_mono_citrus.py --split test --max_samples 0 --run_model --summary_only --progress_interval 50 --output_dir citrus_project/milestones/01_original_lite_mono_baseline/results
```

### Saved Files

- `citrus_project/milestones/01_original_lite_mono_baseline/results/val_lite-mono_full_summary.json`
- `citrus_project/milestones/01_original_lite_mono_baseline/results/val_lite-mono_full_per_sample.csv`
- `citrus_project/milestones/01_original_lite_mono_baseline/results/test_lite-mono_full_summary.json`
- `citrus_project/milestones/01_original_lite_mono_baseline/results/test_lite-mono_full_per_sample.csv`

### Run Setup

- model: original pretrained `lite-mono`
- weights: `weights/lite-mono`
- device: `cuda`
- GPU observed: NVIDIA GeForce RTX 4060 Laptop GPU
- input size: 640 x 192
- model depth conversion range: 0.1 m to 100.0 m
- evaluation label cap: 0.001 m to 80.0 m
- averaging rule: compute metrics per image, then average image metrics
- valid-pixel rule: only score pixels where the dense LiDAR label is valid and inside the evaluation depth range

### Validation Result

- samples evaluated: 564 / 564
- total valid pixels: 193,500,201
- mean valid-label coverage: 37.2272%
- median scale ratio: 3.582965
- mean scale ratio: 3.713719
- mean raw-scale metrics: `abs_rel=0.7128`, `sq_rel=2.1823`, `rmse=4.1009`, `rmse_log=1.3642`, `a1=0.0195`, `a2=0.0382`, `a3=0.0669`
- mean median-scaled metrics: `abs_rel=0.4176`, `sq_rel=1.7692`, `rmse=3.1642`, `rmse_log=0.4834`, `a1=0.4629`, `a2=0.7103`, `a3=0.8494`
- total run time: 83.274 s
- model-forward FPS: 28.478

### Test Result

- samples evaluated: 407 / 407
- total valid pixels: 137,729,923
- mean valid-label coverage: 36.7190%
- median scale ratio: 4.374715
- mean scale ratio: 4.067338
- mean raw-scale metrics: `abs_rel=0.7273`, `sq_rel=2.3440`, `rmse=4.4517`, `rmse_log=1.4325`, `a1=0.0149`, `a2=0.0288`, `a3=0.0472`
- mean median-scaled metrics: `abs_rel=0.3836`, `sq_rel=1.5175`, `rmse=3.1451`, `rmse_log=0.4664`, `a1=0.4989`, `a2=0.7264`, `a3=0.8700`
- total run time: 60.805 s
- model-forward FPS: 29.529

### Model Metadata

- total depth-inference parameters: 3,074,747
- encoder parameters: 2,848,120
- depth-decoder parameters: 226,627
- total checkpoint size: about 11.94 MiB
- note: the training-only pose network is not counted because runtime inference is RGB-only

### Interpretation

The raw-scale result is poor: the original pretrained Lite-Mono model predicts Citrus depths at the wrong absolute distance scale. This is expected for monocular depth models trained on a different domain, but it is still important evidence because a robot needs useful distances, not only a pretty depth-shaped image.

Median scaling improves the result by multiplying each predicted depth map so its median valid depth matches the label median. This removes most of the global scale mismatch and asks a narrower question: after scale alignment, does the prediction preserve useful near/far structure? The answer is "partly, but not enough." Median-scaled `a1` is about 0.46 on validation and 0.50 on test, meaning only about half of valid pixels are within the 25% threshold after scale alignment.

The result supports the paper motivation: original lightweight monocular depth transfers imperfectly to vegetation-dense Citrus scenes, so Citrus-specific adaptation or a vegetation-focused improvement is justified.

### Next Use

- Use summary JSON files for baseline result tables.
- Use per-sample CSV files to find easy/hard frames.
- Generate qualitative panels later from selected RGB inputs, predictions, LiDAR labels, and valid masks.
- Treat evaluator timing as a useful first runtime estimate, but use a dedicated benchmark later if the paper needs a clean deployment-speed claim.

## Original Lite-Mono Validation Visual Selection

Date: 2026-04-28

Paper relevance: early qualitative/failure-case support for the original Lite-Mono baseline. These panels are not the final paper figures yet, but they help interpret what the metrics mean in real Citrus images.

Purpose: choose one good, one typical, and one bad validation example from the full per-sample CSV using `median_scaled_a1`, then render visual panels.

### Command

```powershell
D:/Conda_Envs/lite-mono/python.exe citrus_project/milestones/01_original_lite_mono_baseline/analyze_lite_mono_citrus_results.py --split val
```

### Outputs

- `citrus_project/milestones/01_original_lite_mono_baseline/visuals/good_index_0420_median_scaled_a1_0.826.png`
- `citrus_project/milestones/01_original_lite_mono_baseline/visuals/typical_index_0082_median_scaled_a1_0.478.png`
- `citrus_project/milestones/01_original_lite_mono_baseline/visuals/bad_index_0442_median_scaled_a1_0.047.png`
- `citrus_project/milestones/01_original_lite_mono_baseline/visuals/val_lite-mono_median_scaled_a1_selection_summary.json`
- `citrus_project/milestones/01_original_lite_mono_baseline/visuals/val_lite-mono_median_scaled_a1_selection_summary.csv`

### Selected Samples

- good: validation index 420, median-scaled `a1=0.8264`, median-scaled `abs_rel=0.1510`, valid fraction `38.59%`
- typical: validation index 82, median-scaled `a1=0.4784`, median-scaled `abs_rel=0.3405`, valid fraction `31.80%`
- bad: validation index 442, median-scaled `a1=0.0468`, median-scaled `abs_rel=0.7835`, valid fraction `34.71%`

### Interpretation

The visual panels show why the average metric is not enough. A prediction can look smooth and visually plausible while still disagreeing strongly with the LiDAR label in the valid-mask area.

The good sample shows that the original model can sometimes preserve useful relative scene geometry after median scaling. The bad sample shows the failure case we care about: the model produces broad smooth depth regions, but the LiDAR label has different depth structure over vegetation, trunks, ground, and row edges.

The next analysis step should describe these failure patterns in simple words and decide whether to generate the same good/typical/bad panels for the test split.

