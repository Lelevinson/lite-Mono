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

Beginner-friendly interpretation note:

- `citrus_project/milestones/01_original_lite_mono_baseline/visual_interpretation.md`

The interpretation note currently frames the baseline weakness as more than just wrong scale. Wrong scale is present, but even after median scaling the original model still struggles with vegetation geometry, tree/ground boundaries, row gaps, canopy shapes, and smooth monocular priors that do not match LiDAR-supported structure.

The same good/typical/bad panel selection was later generated for the test split, and it showed the same broad behavior pattern: the original model sometimes captures orchard-row layout after scaling, but the typical and bad cases still show smooth-but-wrong geometry around vegetation and row structure.

## Original Lite-Mono Test Visual Selection

Date: 2026-04-29

Paper relevance: qualitative support for the test split. This complements the validation panels and helps show that the visual interpretation is not only a validation-set artifact.

Purpose: choose one good, one typical, and one bad test example from the full per-sample CSV using `median_scaled_a1`, then render visual panels.

### Command

```powershell
D:/Conda_Envs/lite-mono/python.exe citrus_project/milestones/01_original_lite_mono_baseline/analyze_lite_mono_citrus_results.py --split test
```

### Outputs

- `citrus_project/milestones/01_original_lite_mono_baseline/visuals/good_index_0024_median_scaled_a1_0.771.png`
- `citrus_project/milestones/01_original_lite_mono_baseline/visuals/typical_index_0007_median_scaled_a1_0.530.png`
- `citrus_project/milestones/01_original_lite_mono_baseline/visuals/bad_index_0046_median_scaled_a1_0.076.png`
- `citrus_project/milestones/01_original_lite_mono_baseline/visuals/test_lite-mono_median_scaled_a1_selection_summary.json`
- `citrus_project/milestones/01_original_lite_mono_baseline/visuals/test_lite-mono_median_scaled_a1_selection_summary.csv`

### Selected Samples

- good: test index 24, median-scaled `a1=0.7709`, median-scaled `abs_rel=0.1821`, valid fraction `43.17%`
- typical: test index 7, median-scaled `a1=0.5301`, median-scaled `abs_rel=0.3168`, valid fraction `37.86%`
- bad: test index 46, median-scaled `a1=0.0761`, median-scaled `abs_rel=0.6204`, valid fraction `38.22%`

### Interpretation

The test panels reinforce the validation conclusion. The original model can produce a plausible full-image depth map, and in the good case the broad depth layout aligns reasonably after median scaling. But the typical and bad cases still show the central weakness: smooth monocular predictions do not reliably match LiDAR-supported vegetation, tree-row, and ground/canopy geometry.

The next Milestone 1 choice is whether to build a broader failure taxonomy or treat the baseline evidence as sufficient and move to Milestone 2.

## Milestone 3 Early Adaptation Pilot

Date: 2026-05-05

Paper relevance: engineering/pilot evidence only. This is not the final Citrus-adapted baseline and should not be used as a paper result.

Purpose: run a short self-supervised Citrus fine-tuning pilot from the original Lite-Mono depth checkpoint and check whether the saved checkpoint can be evaluated against the untouched baseline on the same validation subset.

### Training Command

```powershell
D:/Conda_Envs/lite-mono/python.exe train.py --dataset citrus --load_weights_folder weights/lite-mono --models_to_load encoder depth --weights_init scratch --batch_size 1 --num_workers 0 --num_epochs 1 --max_train_steps 100 --save_frequency 1 --log_frequency 10 --log_dir citrus_project/milestones/03_self_supervised_adaptation/runs --model_name citrus_ss_finetune_pilot_100steps
```

### Evaluation Command

```powershell
D:/Conda_Envs/lite-mono/python.exe citrus_project/milestones/01_original_lite_mono_baseline/evaluate_lite_mono_citrus.py --split val --max_samples 100 --run_model --summary_only --progress_interval 25 --weights_folder citrus_project/milestones/03_self_supervised_adaptation/runs/citrus_ss_finetune_pilot_100steps/models/weights_0 --output_dir citrus_project/milestones/03_self_supervised_adaptation/runs/citrus_ss_finetune_pilot_100steps/eval_val100
```

### Same-Subset Validation Comparison

First 100 validation samples:

- untouched original baseline median-scaled: `abs_rel=0.3680`, `sq_rel=0.9802`, `rmse=3.4817`, `rmse_log=0.4933`, `a1=0.4807`, `a2=0.6926`, `a3=0.8216`
- 100-step checkpoint median-scaled: `abs_rel=0.4713`, `sq_rel=1.9500`, `rmse=3.4260`, `rmse_log=0.6038`, `a1=0.3998`, `a2=0.6300`, `a3=0.7843`
- untouched original baseline raw-scale: `abs_rel=0.7289`, `sq_rel=2.4188`, `rmse=4.8283`, `rmse_log=1.4808`, `a1=0.0131`, `a2=0.0240`, `a3=0.0399`
- 100-step checkpoint raw-scale: `abs_rel=0.6997`, `sq_rel=2.1040`, `rmse=4.4417`, `rmse_log=1.3506`, `a1=0.0101`, `a2=0.0300`, `a3=0.0960`

### Interpretation

The 100-step pilot shows the training/evaluation path is working and may be shifting the model's raw absolute scale toward the Citrus labels. However, the median-scaled metrics are worse than the untouched baseline on the same first 100 validation samples, so the relative depth structure has not improved yet.

Treat this as a setup signal: the next controlled pilot can test whether more steps, lower learning rate, batch-size changes, or expanded data are needed before declaring a real Milestone 3 adapted baseline.

## Milestone 3 Low-Learning-Rate Pilot

Date: 2026-05-05

Paper relevance: negative pilot evidence only. This run should not be used as an adapted baseline.

Purpose: test whether smaller fine-tuning updates preserve relative depth structure better than the 100-step `lr=1e-4` pilot.

### Training Command

```powershell
D:/Conda_Envs/lite-mono/python.exe train.py --dataset citrus --load_weights_folder weights/lite-mono --models_to_load encoder depth --weights_init scratch --batch_size 1 --num_workers 0 --num_epochs 1 --max_train_steps 500 --save_frequency 1 --log_frequency 50 --lr 0.00001 0.000001 31 0.00001 0.000001 31 --log_dir citrus_project/milestones/03_self_supervised_adaptation/runs --model_name citrus_ss_finetune_pilot_500steps_lr1e-5
```

### Evaluation Command

```powershell
D:/Conda_Envs/lite-mono/python.exe citrus_project/milestones/01_original_lite_mono_baseline/evaluate_lite_mono_citrus.py --split val --max_samples 100 --run_model --summary_only --progress_interval 25 --weights_folder citrus_project/milestones/03_self_supervised_adaptation/runs/citrus_ss_finetune_pilot_500steps_lr1e-5/models/weights_0 --output_dir citrus_project/milestones/03_self_supervised_adaptation/runs/citrus_ss_finetune_pilot_500steps_lr1e-5/eval_val100
```

### Same-Subset Validation Comparison

First 100 validation samples:

- untouched original baseline median-scaled: `abs_rel=0.3680`, `sq_rel=0.9802`, `rmse=3.4817`, `rmse_log=0.4933`, `a1=0.4807`, `a2=0.6926`, `a3=0.8216`
- 500-step low-LR checkpoint median-scaled: `abs_rel=0.4670`, `sq_rel=1.3756`, `rmse=3.9584`, `rmse_log=0.6431`, `a1=0.4340`, `a2=0.6165`, `a3=0.7104`
- untouched original baseline raw-scale: `abs_rel=0.7289`, `sq_rel=2.4188`, `rmse=4.8283`, `rmse_log=1.4808`, `a1=0.0131`, `a2=0.0240`, `a3=0.0399`
- 500-step low-LR checkpoint raw-scale: `abs_rel=0.8391`, `sq_rel=2.9672`, `rmse=5.1609`, `rmse_log=2.0988`, `a1=0.0000`, `a2=0.0004`, `a3=0.0031`

### Interpretation

The 500-step low-learning-rate pilot is worse than the untouched baseline on the first 100 validation samples in both raw-scale and median-scaled metrics. This suggests the current self-supervised adaptation setup should be inspected before running a longer version of the same configuration.

## Milestone 3 Self-Supervised Batch Diagnostics

Date: 2026-05-05

Paper relevance: diagnostic evidence only. This explains why the early pilots should not be scaled up blindly.

Purpose: inspect a few fixed-order Citrus train/validation batches without optimizer updates to check whether the self-supervised photometric objective is aligned with LiDAR-valid depth quality.

### Diagnostic Script

```powershell
D:/Conda_Envs/lite-mono/python.exe citrus_project/milestones/03_self_supervised_adaptation/diagnose_self_supervised_batch.py --name fixed_original_val --weights_folder weights/lite-mono --models_to_load encoder depth --split val --batches 5 --batch_size 1 --num_workers 0 --output_dir citrus_project/milestones/03_self_supervised_adaptation/runs/diagnostics_fixed
```

The same script was also run for the 100-step and 500-step pilot checkpoints on fixed-order train/val batches.

### Main Findings

- The original `weights/lite-mono/` folder has no pose checkpoint files, so the current pilots use scratch pose.
- The current torchvision version breaks the old pose ImageNet-pretrain code path, so `--weights_init pretrained` needs repair or an explicit workaround before serious adaptation.
- Temporal triplets and camera intrinsics look sane, so the first suspects are not frame ordering or K scaling.
- Batch size 4 fits for a one-step CUDA update, so later pilots do not need to stay at batch size 1.
- Fixed-order diagnostics show the pilots can lower photometric loss while worsening LiDAR-valid depth metrics.

### Interpretation

The self-supervised loss is currently too easy to improve without improving the depth labels we care about. The next pilot should control training stability and pose quality before increasing training length. Good candidates are pose initialization/warmup, batch size 4, `--drop_path 0`, BatchNorm handling, and possibly freezing part of the depth model during early pose adaptation.

## Milestone 3 Batch-Size And DropPath Pilot

Date: 2026-05-05

Paper relevance: negative pilot evidence only. This run should not be used as an adapted baseline.

Purpose: test whether a settings-only recipe with batch size 4 and `--drop_path 0` improves training stability while keeping the code path otherwise unchanged.

### Training Command

```powershell
D:/Conda_Envs/lite-mono/python.exe train.py --dataset citrus --load_weights_folder weights/lite-mono --models_to_load encoder depth --weights_init scratch --batch_size 4 --num_workers 0 --num_epochs 1 --max_train_steps 125 --save_frequency 1 --log_frequency 25 --drop_path 0 --log_dir citrus_project/milestones/03_self_supervised_adaptation/runs --model_name citrus_ss_finetune_pilot_bs4_dp0_125steps
```

### Same-Subset Validation Comparison

First 100 validation samples:

- untouched original baseline median-scaled: `abs_rel=0.3680`, `sq_rel=0.9802`, `rmse=3.4817`, `rmse_log=0.4933`, `a1=0.4807`, `a2=0.6926`, `a3=0.8216`
- batch-size-4/drop_path-0 checkpoint median-scaled: `abs_rel=0.8251`, `sq_rel=7.1932`, `rmse=5.8311`, `rmse_log=0.7784`, `a1=0.2108`, `a2=0.4140`, `a3=0.6004`
- untouched original baseline raw-scale: `abs_rel=0.7289`, `sq_rel=2.4188`, `rmse=4.8283`, `rmse_log=1.4808`, `a1=0.0131`, `a2=0.0240`, `a3=0.0399`
- batch-size-4/drop_path-0 checkpoint raw-scale: `abs_rel=0.6906`, `sq_rel=2.0749`, `rmse=3.5818`, `rmse_log=1.1650`, `a1=0.0993`, `a2=0.2054`, `a3=0.3339`

### Interpretation

Batch size 4 and `--drop_path 0` improved raw-scale metrics but made median-scaled relative-depth metrics much worse. This reinforces that raw absolute scale movement is not enough; the current training objective or pose/depth dynamics can damage the relative depth structure we care about.

## Milestone 3 Depth-Freeze Control Smoke

Date: 2026-05-06

Paper relevance: engineering control only. This is not a model-quality result.

Purpose: verify a default-off pose-warmup control before using it in any pilot. The new `--freeze_depth_steps` setting lets pose update while depth optimizer updates are skipped for the first N training steps.

### Smoke Command

```powershell
D:/Conda_Envs/lite-mono/python.exe train.py --dataset citrus --load_weights_folder weights/lite-mono --models_to_load encoder depth --weights_init scratch --batch_size 4 --num_workers 0 --num_epochs 1 --max_train_steps 2 --freeze_depth_steps 2 --save_frequency 1 --log_frequency 1 --drop_path 0 --log_dir citrus_project/milestones/03_self_supervised_adaptation/runs --model_name citrus_ss_freeze_depth_smoke_2steps
```

### Result

- Training ran on CUDA for 2 steps.
- Losses were `0.16873` and `0.15694`.
- Encoder/depth trainable tensors changed `0` versus original `weights/lite-mono`.
- Depth optimizer state stayed empty.
- Pose optimizer state reached step 2.
- Encoder BatchNorm running-stat buffers changed because forward passes still ran in train mode.

### Interpretation

The freeze control behaves as intended. It can be used for a controlled pose-warmup pilot, but it is not by itself evidence of better Citrus adaptation.

## Milestone 3 Pose-Pretrain Compatibility Fix

Date: 2026-05-06

Paper relevance: engineering unblocker only. No Citrus model-quality claim should use this alone.

Purpose: repair the old torchvision pretrained ResNet loading path used by the pose encoder.

### Problem

`networks/resnet_encoder.py` used `torchvision.models.resnet.model_urls`, but the local environment is torch `2.0.1` / torchvision `0.15.2`, where that attribute no longer exists.

### Fix

The ResNet encoder now uses modern torchvision ResNet weight enums when available, while retaining the old `model_urls` fallback for older environments.

### Validation

No training was run for this fix.

- The standard ResNet-18 ImageNet checkpoint was downloaded after approval to `C:/Users/user/.cache/torch/hub/checkpoints/resnet18-f37072fd.pth`.
- `ResnetEncoder(18, True, num_input_images=2)` built and forwarded a fake `[1, 6, 192, 640]` tensor.
- `ResnetEncoder(18, True, num_input_images=1)` built and forwarded a fake `[1, 3, 192, 640]` tensor.
- Both produced expected Lite-Mono pose/depth encoder feature pyramid shapes.

### Interpretation

The pose-pretrain construction crash is fixed at the encoder level. The root trainer smoke below now verifies the repaired path inside `train.py`; after that, a controlled short pilot can compare scratch pose versus pretrained pose.

## Milestone 3 Root Trainer Pretrained-Pose Smoke

Date: 2026-05-06

Paper relevance: engineering smoke only.

Purpose: verify that the repaired pretrained pose route works inside `train.py` with the Citrus DataLoader/trainer path.

### Command

```powershell
D:/Conda_Envs/lite-mono/python.exe train.py --dataset citrus --load_weights_folder weights/lite-mono --models_to_load encoder depth --weights_init pretrained --batch_size 4 --num_workers 0 --num_epochs 1 --max_train_steps 1 --save_frequency 1 --log_frequency 1 --drop_path 0 --log_dir citrus_project/milestones/03_self_supervised_adaptation/runs --model_name citrus_ss_pretrained_pose_smoke_1step
```

### Result

- The 1-step smoke ran on CUDA.
- Logged step-0 loss: `0.16363`.
- Saved milestone-local encoder/depth/pose checkpoints.
- `models/opt.json` records `weights_init=pretrained`.
- Depth optimizer state reached step 1.
- Pose optimizer state reached step 1.

### Interpretation

The root trainer path can now construct and train with ImageNet-pretrained pose ResNet weights. This is still not a quality result; the next comparison needs a short controlled pilot.

## Milestone 3 Pretrained-Pose Depth-Frozen Warmup Pilot

Date: 2026-05-06

Paper relevance: tiny pilot evidence only. This is not a final adapted baseline.

Purpose: check whether pretrained pose can warm up briefly while depth optimizer updates are frozen, without damaging validation depth behavior.

### Training Command

```powershell
D:/Conda_Envs/lite-mono/python.exe train.py --dataset citrus --load_weights_folder weights/lite-mono --models_to_load encoder depth --weights_init pretrained --batch_size 4 --num_workers 0 --num_epochs 1 --max_train_steps 25 --freeze_depth_steps 25 --save_frequency 1 --log_frequency 5 --drop_path 0 --log_dir citrus_project/milestones/03_self_supervised_adaptation/runs --model_name citrus_ss_pretrained_pose_warmup_25steps
```

### Training Result

- CUDA run completed for 25 steps.
- Logged losses at steps 0/5/10/15/20: `0.17810`, `0.13715`, `0.14609`, `0.14938`, `0.14692`.
- Encoder/depth trainable tensors changed `0` versus original `weights/lite-mono`.
- Depth Adam state stayed empty.
- Pose Adam reached step 25.
- Encoder BatchNorm running-stat buffers changed due to train-mode forward passes.

### Same-Subset Validation Comparison

First 100 validation samples:

- untouched original baseline median-scaled: `abs_rel=0.3680`, `sq_rel=0.9802`, `rmse=3.4817`, `rmse_log=0.4933`, `a1=0.4807`, `a2=0.6926`, `a3=0.8216`
- 25-step depth-frozen warmup median-scaled: `abs_rel=0.3777`, `sq_rel=1.2055`, `rmse=3.4646`, `rmse_log=0.4792`, `a1=0.4773`, `a2=0.7158`, `a3=0.8536`
- untouched original baseline raw-scale: `abs_rel=0.7289`, `sq_rel=2.4188`, `rmse=4.8283`, `rmse_log=1.4808`, `a1=0.0131`, `a2=0.0240`, `a3=0.0399`
- 25-step depth-frozen warmup raw-scale: `abs_rel=0.7280`, `sq_rel=2.3298`, `rmse=4.7374`, `rmse_log=1.4305`, `a1=0.0084`, `a2=0.0193`, `a3=0.0379`

### Interpretation

The depth-frozen warmup stayed close to the untouched baseline on first-100 validation metrics. This is encouraging only as a safety signal: it did not damage relative depth badly. It is not yet evidence that adaptation improves Citrus depth, because the trainable depth weights were intentionally frozen.

## Milestone 3 Pretrained-Pose Warmup Then Depth-Update Pilot

Date: 2026-05-06

Paper relevance: tiny pilot evidence only. This is not a final adapted baseline.

Purpose: test whether a short pretrained-pose warmup lets depth update safely afterward.

### Training Command

```powershell
D:/Conda_Envs/lite-mono/python.exe train.py --dataset citrus --load_weights_folder weights/lite-mono --models_to_load encoder depth --weights_init pretrained --batch_size 4 --num_workers 0 --num_epochs 1 --max_train_steps 50 --freeze_depth_steps 25 --save_frequency 1 --log_frequency 10 --drop_path 0 --log_dir citrus_project/milestones/03_self_supervised_adaptation/runs --model_name citrus_ss_pretrained_pose_warmup25_depth25_50steps
```

### Training Result

- CUDA run completed for 50 steps.
- Depth optimizer was frozen for the first 25 steps, then updated for 25 steps.
- Logged losses at steps 0/10/20/30/40: `0.16001`, `0.14923`, `0.16219`, `0.14194`, `0.13426`.
- Encoder and depth decoder trainable tensors changed slightly after depth updates were enabled.
- Depth Adam reached step 25.
- Pose Adam reached step 50.

### Same-Subset Validation Comparison

First 100 validation samples:

- untouched original baseline median-scaled: `abs_rel=0.3680`, `sq_rel=0.9802`, `rmse=3.4817`, `rmse_log=0.4933`, `a1=0.4807`, `a2=0.6926`, `a3=0.8216`
- 50-step warmup-then-depth median-scaled: `abs_rel=0.5766`, `sq_rel=3.2984`, `rmse=4.3728`, `rmse_log=0.6083`, `a1=0.3135`, `a2=0.5977`, `a3=0.7692`
- untouched original baseline raw-scale: `abs_rel=0.7289`, `sq_rel=2.4188`, `rmse=4.8283`, `rmse_log=1.4808`, `a1=0.0131`, `a2=0.0240`, `a3=0.0399`
- 50-step warmup-then-depth raw-scale: `abs_rel=0.4946`, `sq_rel=1.5059`, `rmse=4.0153`, `rmse_log=0.8167`, `a1=0.1872`, `a2=0.3402`, `a3=0.5300`

### Interpretation

The run improved raw-scale metrics but worsened median-scaled relative-depth metrics. This suggests the self-supervised update is strongly changing predicted scale, but it is still damaging the relative depth pattern. Do not scale this recipe directly to a longer run.

## Milestone 3 Low-Depth-LR Warmup Then Depth-Update Pilot

Date: 2026-05-06

Paper relevance: tiny pilot evidence only. This is not a final adapted baseline.

Purpose: test whether reducing depth learning rate protects relative depth structure while keeping the 25-step pose warmup and 25-step depth-update pattern.

### Training Command

```powershell
D:/Conda_Envs/lite-mono/python.exe train.py --dataset citrus --load_weights_folder weights/lite-mono --models_to_load encoder depth --weights_init pretrained --batch_size 4 --num_workers 0 --num_epochs 1 --max_train_steps 50 --freeze_depth_steps 25 --save_frequency 1 --log_frequency 10 --drop_path 0 --lr 0.00001 0.0000005 31 0.0001 0.00001 31 --log_dir citrus_project/milestones/03_self_supervised_adaptation/runs --model_name citrus_ss_pretrained_pose_warmup25_depth25_50steps_depthlr1e-5
```

### Training Result

- CUDA run completed for 50 steps.
- Depth optimizer was frozen for the first 25 steps, then updated for 25 steps.
- Depth LR was `1e-5`; pose LR stayed `1e-4`.
- Logged losses at steps 0/10/20/30/40: `0.13880`, `0.14841`, `0.13287`, `0.14273`, `0.16145`.
- Max depth-side trainable weight movement was about 10x smaller than the normal-depth-LR 50-step pilot.
- Depth Adam reached step 25.
- Pose Adam reached step 50.

### Same-Subset Validation Comparison

First 100 validation samples:

- untouched original baseline median-scaled: `abs_rel=0.3680`, `sq_rel=0.9802`, `rmse=3.4817`, `rmse_log=0.4933`, `a1=0.4807`, `a2=0.6926`, `a3=0.8216`
- low-depth-LR 50-step median-scaled: `abs_rel=0.4271`, `sq_rel=1.1995`, `rmse=3.5924`, `rmse_log=0.5483`, `a1=0.4526`, `a2=0.6394`, `a3=0.7698`
- untouched original baseline raw-scale: `abs_rel=0.7289`, `sq_rel=2.4188`, `rmse=4.8283`, `rmse_log=1.4808`, `a1=0.0131`, `a2=0.0240`, `a3=0.0399`
- low-depth-LR 50-step raw-scale: `abs_rel=0.7790`, `sq_rel=2.6595`, `rmse=4.9690`, `rmse_log=1.7249`, `a1=0.0099`, `a2=0.0172`, `a3=0.0243`

### Interpretation

Lower depth LR alone is not enough. It made the update gentler, but the result still trailed the untouched baseline on both raw and median-scaled first-100 validation metrics.

## Milestone 3 Fixed-Batch Internal Diagnostics

Date: 2026-05-06

Paper relevance: diagnostic evidence only.

Purpose: compare internal training signals on the same fixed train/validation batches after the recent tiny pilots.

### Compared Checkpoints

- original `weights/lite-mono`
- `citrus_ss_pretrained_pose_warmup_25steps`
- `citrus_ss_pretrained_pose_warmup25_depth25_50steps`
- `citrus_ss_pretrained_pose_warmup25_depth25_50steps_depthlr1e-5`

### Validation Batch Summary

Fixed first 5 validation batches:

| checkpoint | photo loss | LiDAR abs_rel | LiDAR a1 | depth median | pose trans |
|---|---:|---:|---:|---:|---:|
| original | 0.170072 | 0.219713 | 0.676611 | 0.540391 | 0.000517 |
| 25-step depth frozen | 0.151223 | 0.231445 | 0.631453 | 0.535836 | 0.007553 |
| 50-step normal depth LR | 0.146895 | 0.430942 | 0.198302 | 1.132429 | 0.007778 |
| 50-step low depth LR | 0.145763 | 0.267062 | 0.542943 | 0.407042 | 0.003881 |

### Interpretation

Photo loss improved in all adapted checkpoints, including checkpoints that worsened depth metrics. The normal-depth-LR run changed predicted depth scale too strongly, while low depth LR reduced the damage but did not beat the untouched baseline. The next recipe should preserve depth structure more explicitly instead of only adjusting learning rate.

## Milestone 3 Depth-Encoder Freeze And Decoder-Only Pilot

Date: 2026-05-06

Paper relevance: tiny pilot evidence only. This is not a final adapted baseline.

Purpose: test whether freezing the pretrained depth encoder and BatchNorm running statistics protects relative depth structure while allowing the depth decoder to adapt.

### Code Change

- Added `--freeze_depth_encoder` to `options.py`.
- `trainer.py` excludes the depth encoder from the depth optimizer when the flag is set.
- `trainer.py` keeps the depth encoder in eval mode during training when the flag is set, preventing BatchNorm running-stat drift.
- The Milestone 3 diagnostic helper now accepts `--freeze_depth_encoder` so decoder-only checkpoints load with the matching optimizer shape.

### Training Command

```powershell
D:/Conda_Envs/lite-mono/python.exe train.py --dataset citrus --load_weights_folder weights/lite-mono --models_to_load encoder depth --weights_init pretrained --batch_size 4 --num_workers 0 --num_epochs 1 --max_train_steps 50 --freeze_depth_steps 25 --freeze_depth_encoder --save_frequency 1 --log_frequency 10 --drop_path 0 --log_dir citrus_project/milestones/03_self_supervised_adaptation/runs --model_name citrus_ss_pretrained_pose_warmup25_decoder25_50steps
```

### Training Result

- CUDA run completed for 50 steps.
- Encoder trainable tensors changed `0`.
- Encoder BatchNorm buffers changed `0`.
- Depth decoder updated for 25 steps.
- Pose updated for 50 steps.

### Same-Subset Validation Comparison

First 100 validation samples:

- untouched original baseline median-scaled: `abs_rel=0.3680`, `sq_rel=0.9802`, `rmse=3.4817`, `rmse_log=0.4933`, `a1=0.4807`, `a2=0.6926`, `a3=0.8216`
- decoder-only 50-step median-scaled: `abs_rel=0.4700`, `sq_rel=1.3546`, `rmse=3.8739`, `rmse_log=0.6242`, `a1=0.4195`, `a2=0.6140`, `a3=0.7202`
- untouched original baseline raw-scale: `abs_rel=0.7289`, `sq_rel=2.4188`, `rmse=4.8283`, `rmse_log=1.4808`, `a1=0.0131`, `a2=0.0240`, `a3=0.0399`
- decoder-only 50-step raw-scale: `abs_rel=0.7373`, `sq_rel=2.5788`, `rmse=4.9783`, `rmse_log=1.6191`, `a1=0.0035`, `a2=0.0133`, `a3=0.0410`

### Interpretation

Freezing encoder and BatchNorm works mechanically, but decoder-only adaptation still worsened the first-100 validation metrics. The failure is not only encoder drift. This suggests the next fix likely needs to address the self-supervised objective, pose/mask behavior, or add an explicit structure-preserving/depth-monitor constraint.

## Milestone 3 Previous-Only Temporal Source Pilot

Date: 2026-05-06

Paper relevance: tiny pilot evidence only. This is not a final adapted baseline.

Purpose: test whether the next temporal source was hurting self-supervised training.

### Diagnostic Motivation

In the 50-step normal-depth-LR validation diagnostics, the next frame had weaker photo margin and higher out-of-bounds warping than the previous frame:

```text
previous margin: 0.006716
next margin:     0.001326
previous OOB:    0.034774
next OOB:        0.073470
```

### Training Command

```powershell
D:/Conda_Envs/lite-mono/python.exe train.py --dataset citrus --load_weights_folder weights/lite-mono --models_to_load encoder depth --weights_init pretrained --batch_size 4 --num_workers 0 --num_epochs 1 --max_train_steps 50 --freeze_depth_steps 25 --save_frequency 1 --log_frequency 10 --drop_path 0 --frame_ids 0 -1 --log_dir citrus_project/milestones/03_self_supervised_adaptation/runs --model_name citrus_ss_prev_only_warmup25_depth25_50steps
```

### Same-Subset Validation Comparison

First 100 validation samples:

- untouched original baseline median-scaled: `abs_rel=0.3680`, `sq_rel=0.9802`, `rmse=3.4817`, `rmse_log=0.4933`, `a1=0.4807`, `a2=0.6926`, `a3=0.8216`
- previous-only 50-step median-scaled: `abs_rel=0.4809`, `sq_rel=1.3094`, `rmse=3.8513`, `rmse_log=0.6302`, `a1=0.3632`, `a2=0.5712`, `a3=0.7016`
- untouched original baseline raw-scale: `abs_rel=0.7289`, `sq_rel=2.4188`, `rmse=4.8283`, `rmse_log=1.4808`, `a1=0.0131`, `a2=0.0240`, `a3=0.0399`
- previous-only 50-step raw-scale: `abs_rel=0.7537`, `sq_rel=2.6378`, `rmse=4.9996`, `rmse_log=1.6835`, `a1=0.0064`, `a2=0.0133`, `a3=0.0331`

### Interpretation

Previous-only training did not improve the result. Dropping the next frame alone is not enough to stabilize self-supervised Citrus adaptation.

## Milestone 3 Loss-Decomposition Diagnostic

Date: 2026-05-06

Paper relevance: diagnostic evidence for why the current self-supervised adapted-baseline recipe is not ready. This is not a proposed new method.

Purpose: separate the existing Lite-Mono self-supervised loss into readable pieces on fixed validation batches.

Saved diagnostic outputs:

```text
citrus_project/milestones/03_self_supervised_adaptation/runs/diagnostics_loss_decomposition_2026-05-06/
```

Fixed first 5 validation batches:

| checkpoint | selected photo | smooth weighted | automask warp frac | reproj min | depth median | LiDAR abs_rel | LiDAR a1 |
|---|---:|---:|---:|---:|---:|---:|---:|
| original depth + pretrained pose init | 0.180666 | 0.000012 | 0.702305 | 0.187102 | 0.540391 | 0.219713 | 0.676611 |
| 25-step depth-frozen warmup | 0.151193 | 0.000014 | 0.450563 | 0.199916 | 0.535836 | 0.231445 | 0.631453 |
| 50-step normal depth LR | 0.146830 | 0.000023 | 0.513703 | 0.188075 | 1.132429 | 0.430942 | 0.198302 |
| 50-step low depth LR | 0.145735 | 0.000012 | 0.517715 | 0.187017 | 0.407042 | 0.267062 | 0.542943 |
| 50-step decoder-only | 0.147996 | 0.000010 | 0.524753 | 0.191255 | 0.491805 | 0.300943 | 0.464280 |
| 50-step previous-only | 0.192904 | 0.000011 | 0.501976 | 0.251292 | 0.507625 | 0.332617 | 0.463598 |

Interpretation:

Smoothness is far too small to explain the failure by itself. In two-source runs, previous-vs-next source selection remains roughly balanced, so temporal direction alone is not the answer. The stronger signal is depth-scale freedom: the adapted checkpoints can lower selected photo loss while moving the predicted depth median in different directions and worsening LiDAR-valid depth quality.

Research takeaway:

The standard self-supervised adaptation objective is currently under-constrained for Citrus. It can improve the image-warping game without improving the depth result that matters for the paper. A Milestone 3 adapted baseline should not be scaled until we either find a conservative standard-control recipe or clearly move structure-preserving changes into the later proposed-method milestone.

## Milestone 3 Pose-Only / Depth-Frozen Controls

Date: 2026-05-06

Paper relevance: diagnostic control evidence only. These controls explain the failure mode; they are not final adapted depth models.

Purpose: isolate whether pose learning, BatchNorm drift, or trainable depth updates are responsible for the bad Milestone 3 pilots.

### Results

Control A: `citrus_ss_pretrained_pose_depthfrozen_50steps`

- depth optimizer frozen for all 50 steps
- encoder trainable tensors changed: `0`
- depth decoder tensors changed: `0`
- encoder BatchNorm buffers changed: `54`
- first-100 median-scaled metrics: `abs_rel=0.3810`, `rmse=3.4595`, `a1=0.4691`
- first-100 raw-scale metrics: `abs_rel=0.7283`, `rmse=4.7322`, `a1=0.0079`

Control B: `citrus_ss_pretrained_pose_depthencoderfrozen_depthfrozen_50steps`

- depth encoder/BatchNorm frozen and depth optimizer frozen for all 50 steps
- encoder tensors changed: `0`
- depth decoder tensors changed: `0`
- first-100 metrics matched the untouched original baseline exactly
- first-100 median-scaled metrics: `abs_rel=0.3680`, `rmse=3.4817`, `a1=0.4807`
- first-100 raw-scale metrics: `abs_rel=0.7289`, `rmse=4.8283`, `a1=0.0131`

### Fixed-Batch Diagnostic Summary

| checkpoint | selected photo | depth median | LiDAR abs_rel | LiDAR a1 |
|---|---:|---:|---:|---:|
| original depth + pretrained pose init | 0.180666 | 0.540391 | 0.219713 | 0.676611 |
| depth frozen 50, BN drift allowed | 0.148836 | 0.533799 | 0.236576 | 0.620472 |
| depth encoder frozen + depth frozen 50 | 0.143025 | 0.540391 | 0.219713 | 0.676611 |
| 50-step normal depth LR | 0.146830 | 1.132429 | 0.430942 | 0.198302 |
| 50-step low depth LR | 0.145735 | 0.407042 | 0.267062 | 0.542943 |
| 50-step decoder-only | 0.147996 | 0.491805 | 0.300943 | 0.464280 |

### Interpretation

Pose-only training can lower photo loss, but pose is not used during RGB-only depth inference. If the depth path is fully frozen, the inference model is unchanged and the metrics are exactly the original baseline. BatchNorm drift alone causes only small metric movement. The larger failures happen when trainable depth parameters update.

Research takeaway:

Milestone 3's core difficulty is not "pose training works or not." The hard part is depth adaptation: the current photo-loss-driven updates can move the depth model in a way that improves image warping but worsens LiDAR-valid Citrus depth.

## Milestone 3 Seeded Warmup-Then-Depth Trajectory

Date: 2026-05-06

Paper relevance: diagnostic trajectory evidence. This helps explain why simply making the same run longer is risky.

Purpose: test whether the degradation appears immediately after depth updates begin.

Shared settings:

- `--seed 0`
- `--weights_init pretrained`
- `--batch_size 4`
- `--drop_path 0`
- `--freeze_depth_steps 25`
- first-100 validation evaluation

First 100 validation samples:

| checkpoint | depth update steps | raw abs_rel | median-scaled abs_rel | median-scaled a1 | median scale ratio |
|---|---:|---:|---:|---:|---:|
| untouched baseline | n/a | 0.7289 | 0.3680 | 0.4807 | 3.944117 |
| seed0 depth0/25 | 0 | 0.7274 | 0.3758 | 0.4797 | 3.885954 |
| seed0 depth5/30 | 5 | 0.6781 | 0.3902 | 0.4484 | 3.400892 |
| seed0 depth15/40 | 15 | 0.6697 | 0.4409 | 0.3908 | 3.271431 |
| seed0 depth25/50 | 25 | 0.7901 | 0.6354 | 0.2280 | 5.559390 |

Fixed-batch diagnostics:

| checkpoint | selected photo | diagnostic depth median |
|---|---:|---:|
| seed0 depth0/25 | 0.150719 | 0.531425 |
| seed0 depth5/30 | 0.148396 | 0.618594 |
| seed0 depth15/40 | 0.147801 | 0.694628 |
| seed0 depth25/50 | 0.150593 | 0.416658 |

Interpretation:

The first few depth updates already show the tradeoff: raw-scale metrics improve, but median-scaled relative-depth quality worsens. By 25 depth-update steps in the seeded trajectory, both raw and median-scaled metrics are poor. This does not prove a much longer run can never recover, but it makes "just train longer with the same recipe" a risky next step.

Research takeaway:

The standard self-supervised adaptation baseline is still not established. If Milestone 3 cannot find a conservative standard-control recipe, this failure mode becomes direct motivation for Milestone 4: an improvement that constrains Citrus adaptation so depth structure does not drift while photo loss improves.

## Milestone 3 Conservative Near-Epoch Probe

Date checked: 2026-05-07

Paper relevance: negative adapted-baseline evidence. This is important because it tests whether a more conservative standard recipe can recover when run longer than the 25-50 step pilots.

Run:

```text
citrus_project/milestones/03_self_supervised_adaptation/runs/citrus_ss_seed0_decoderonly_lowdepthlr_1epoch_1000steps/
```

Recipe:

- original Lite-Mono encoder/depth weights
- pretrained pose initialization
- batch size 4
- seed 0
- drop path 0
- 25-step depth optimizer warmup
- frozen depth encoder and BatchNorm statistics
- depth decoder only after warmup
- low depth learning rate: `1e-5` to `5e-7`
- pose learning rate: `1e-4` to `1e-5`
- 1000-step cap inside one epoch
- 250-step checkpoints

Training status:

- The run finished cleanly on CUDA.
- It stopped at the intended `--max_train_steps=1000` limit.
- Saved checkpoints: `step_250`, `step_500`, `step_750`, `step_1000`, and `weights_0`.
- `step_1000` and `weights_0` are identical for encoder, depth, pose encoder, and pose checkpoint files.

First 100 validation samples:

| checkpoint | raw abs_rel | median-scaled abs_rel | median-scaled a1 | median scale ratio |
|---|---:|---:|---:|---:|
| untouched baseline | 0.7289 | 0.3680 | 0.4807 | 3.944117 |
| conservative step 250 | 0.7331 | 0.4542 | 0.4290 | 4.339389 |
| conservative step 500 | 0.7458 | 0.6325 | 0.2445 | 4.897573 |
| conservative step 750 | 0.7332 | 0.6152 | 0.2366 | 4.618348 |
| conservative final/1000 | 0.7448 | 0.6615 | 0.1827 | 4.860058 |

Interpretation:

The conservative longer probe did not recover. The depth model was already worse than baseline at 250 steps, and by 500-1000 steps the median-scaled relative-depth metrics degraded substantially. This makes a plain standard self-supervised Citrus adaptation baseline look weak under the current recipe family. The result supports treating structure-preserving constraints or a different adaptation objective as a Milestone 4-style improvement rather than silently folding them into Milestone 3.

## Milestone 3 Original-Versus-Adapted Visual Comparison

Date: 2026-05-07

Paper relevance: qualitative support for the negative Milestone 3 adaptation result.

Helper:

```text
citrus_project/milestones/03_self_supervised_adaptation/compare_original_vs_adapted_visuals.py
```

Saved visual outputs:

```text
citrus_project/milestones/03_self_supervised_adaptation/runs/citrus_ss_seed0_decoderonly_lowdepthlr_1epoch_1000steps/visual_compare_original_vs_adapted_val100_weights_0/
```

Selected examples:

| role | index | original median-scaled abs_rel | original median-scaled a1 | adapted median-scaled abs_rel | adapted median-scaled a1 |
|---|---:|---:|---:|---:|---:|
| adapted good | 12 | 0.3424 | 0.5276 | 0.4066 | 0.3181 |
| adapted typical | 36 | 0.4123 | 0.3953 | 0.8670 | 0.1783 |
| adapted bad | 75 | 0.5360 | 0.2625 | 1.0535 | 0.0323 |
| largest drop vs original | 48 | 0.1887 | 0.7302 | 0.4930 | 0.1568 |

Interpretation:

The comparison panels show the adapted checkpoint becoming smoother and less structurally specific than the original baseline. The original model is blurry and imperfect, but after median scaling it still retains some tree/ground/row contrast. The adapted model often replaces that with broader depth bands and weaker object boundaries, increasing error on LiDAR-valid orchard structure. This supports the conclusion that the 1000-step adaptation damaged relative depth structure, not merely absolute scale.

## Milestone 3 No-Color-Augmentation Control

Date: 2026-05-07

Paper relevance: diagnostic training-setting control. This helps distinguish "all conservative settings fail equally" from "some standard settings reduce the drift but still do not solve it."

Run:

```text
citrus_project/milestones/03_self_supervised_adaptation/runs/citrus_ss_seed0_decoderonly_lowdepthlr_noaug_250steps/
```

Recipe:

- original Lite-Mono encoder/depth weights
- pretrained pose initialization
- batch size 4
- seed 0
- drop path 0
- 25-step depth optimizer warmup
- frozen depth encoder and BatchNorm statistics
- depth decoder only after warmup
- low depth learning rate: `1e-5` to `5e-7`
- `--citrus_color_aug_probability 0`
- 250-step cap

Training status:

- Finished cleanly on CUDA.
- Stopped at the intended `--max_train_steps=250` limit.
- `step_250` and `weights_0` are identical for encoder, depth, pose encoder, and pose checkpoint files.

First 100 validation samples:

| checkpoint | raw abs_rel | median-scaled abs_rel | median-scaled a1 | median scale ratio |
|---|---:|---:|---:|---:|
| untouched baseline | 0.7289 | 0.3680 | 0.4807 | 3.944117 |
| conservative 250 with color aug | 0.7331 | 0.4542 | 0.4290 | 4.339389 |
| conservative 250 no color aug | 0.7192 | 0.4108 | 0.4568 | 4.057223 |

Interpretation:

Removing Citrus color augmentation clearly improved the 250-step conservative control compared with the same setting using color augmentation. However, it still did not beat the untouched original baseline on median-scaled relative-depth structure. This suggests color jitter is likely a contributor to the instability, but not the root solution.

## Milestone 3 No-Color-Augmentation 500-Step Control

Date: 2026-05-07

Paper relevance: diagnostic follow-up to the 250-step no-color-augmentation control.

Run:

```text
citrus_project/milestones/03_self_supervised_adaptation/runs/citrus_ss_seed0_decoderonly_lowdepthlr_noaug_500steps/
```

Recipe:

- same conservative decoder-only recipe as the 250-step no-augmentation control
- `--max_train_steps 500`
- `--save_step_frequency 250`
- `--citrus_color_aug_probability 0`

Training status:

- Finished cleanly on CUDA.
- Stopped at the intended `--max_train_steps=500` limit.
- Saved `step_250`, `step_500`, and `weights_0`.
- `step_500` and `weights_0` are identical for encoder, depth, pose encoder, and pose checkpoint files.

First 100 validation samples:

| checkpoint | raw abs_rel | median-scaled abs_rel | median-scaled a1 | median scale ratio |
|---|---:|---:|---:|---:|
| untouched baseline | 0.7289 | 0.3680 | 0.4807 | 3.944117 |
| no color aug, 250 steps | 0.7192 | 0.4108 | 0.4568 | 4.057223 |
| no color aug, 500 steps | 0.7235 | 0.5300 | 0.3513 | 4.322919 |
| color aug, 500 steps | 0.7458 | 0.6325 | 0.2445 | 4.897573 |

Interpretation:

The 500-step no-color-augmentation control confirms that removing color jitter reduces the damage compared with color augmentation, but it does not stabilize the recipe. The no-augmentation run worsened from 250 to 500 steps and still did not beat the untouched baseline on median-scaled relative-depth structure. This supports stopping blind Milestone 3 recipe scaling and moving toward either full-result documentation of the weak adapted baseline or a Milestone 4 method change.

