# AGENTS.md

## Purpose

This file is the shared project context for the Lite-Mono + Citrus Farm research project.
The project is not only a dataset-preparation task: the end goal is a publishable research paper on improving lightweight monocular depth estimation for vegetation-dense citrus/orchard environments, with a pest-killing robot deployment motivation.
All new chats should read this file first.

## Mandatory Context Workflow

1. Read this file before starting any task.
2. Treat this file as source of truth for project status, decisions, and next steps.
3. If any code, config, data pipeline, or experiment setting changes, update this file in the same turn.
4. Do not mark a task complete until this file is updated when required.
5. In every final response, include:
   - Context file updated: Yes
   - Short summary of what was updated in this file
6. If no update is required, include:
   - Context file updated: No
   - Reason no update was required

## Startup Instruction For New Chats

Always read AGENTS.md first, then continue work.
If project changes are made, update AGENTS.md before finishing.

## Project Goal

Publish an improved Lite-Mono-style monocular depth estimation method for vegetation-dense agricultural environments, especially citrus/orchard robot navigation for a lightweight RGB-only pest-killing robot perception stack.

Research objective:

1. Use original Lite-Mono as the lightweight monocular depth baseline.
2. Show and measure the domain gap between urban/KITTI-style Lite-Mono behavior and citrus/orchard scenes.
3. Build a reliable Citrus Farm RGB + depth-label evaluation/training pipeline.
4. Improve Lite-Mono or its training objective for dense vegetation while keeping runtime inference monocular RGB-only and lightweight.
5. Compare original Lite-Mono, Citrus-adapted Lite-Mono, and the proposed improved variant under the same Citrus data budget and splits.

Dataset-preparation objective:

1. Download correctly aligned Citrus Farm ROS bag files.
2. Extract ZED RGB/depth and Velodyne LiDAR point cloud data.
3. Match RGB frames with LiDAR by timestamp.
4. Project and densify LiDAR depth for evaluation labels and optional supervised/hybrid training.
5. Export reproducible train/val/test split manifests, metrics, and quality diagnostics.

## Pipeline Overview

1. Download base (LiDAR) bags.
2. Download zed bags using overlap window from selected base bags.
3. Extract zed RGB and depth from zed bags.
4. Extract LiDAR point clouds from base bags.
5. Audit LiDAR-to-ZED projection alignment on a small sample before trusting dense labels.
6. Densify LiDAR into image-aligned depth.
7. Build train/val/test-ready dataset artifacts.

## Citrus Farm Dataset Source Understanding

Official dataset intent:

1. CitrusFarm is a multimodal agricultural robotics dataset for localization, mapping, and crop monitoring in citrus tree farms.
2. It includes seven sequences from three citrus fields, multiple tree species/growth stages, different planting patterns, and varying daylight conditions.
3. It provides nine sensing modalities: stereo RGB, ZED depth, monochrome, near-infrared, thermal, wheel odometry, LiDAR, IMU, and GPS-RTK.
4. Raw data is released as modality-split ROS bag blocks. The authors state users can play bags from the same folder together and ROS will sequence messages by timestamps.
5. Official tooling includes download_citrusfarm.py and bag2files.py. bag2files.py is a generic extractor to images, PCD, CSV, and text files; it is not a monocular-depth training pipeline.

How our pipeline relates to author intent:

1. Download filtering by folder/modality is consistent with the official download script design.
2. Selecting only Sequence 01, base bags, ZED bags, calibration, and ground truth is a research-scope reduction, not an official fixed split.
3. Extracting `/zed2i/zed_node/left/image_rect_color`, `/zed2i/zed_node/depth/depth_registered`, and `/velodyne_points` is consistent with the official topic list.
4. Saving RGB as PNG and arrays as NPZ differs from the official bag2files.py output format, but it is reasonable for lossless ML preprocessing.
5. Projecting and densifying LiDAR into ZED image space is our own derived-label pipeline. It must be validated; it should not be assumed to be an official Citrus Farm ground-truth product.

## Canonical Script Order

1. datasets/citrus-farm-dataset/download_citrusfarm_seq_01_lidar.py
2. datasets/citrus-farm-dataset/download_citrusfarm_seq_01_rgb_depth.py
3. datasets/citrus-farm-dataset/extract_left_rgbd_from_raw.py
4. datasets/citrus-farm-dataset/extract_lidar_from_raw.py
5. datasets/citrus-farm-dataset/audit_projection_alignment.py
6. datasets/citrus-farm-dataset/densify_lidar.py
7. datasets/citrus-farm-dataset/build_training_dataset.py

## Current Status Snapshot (2026-03-31)

Implemented:

1. Overlap-window bag selection for zed download based on selected base bag time window.
2. Timestamp-ordered base bag selection.
3. Safer RGB-LiDAR pairing and diagnostics in densification flow.
4. Batch builder script to generate dense depth targets and split manifests.
5. Pairing logic now supports same-session preference with optional cross-session fallback under the same max timestamp delta.

Validated:

1. Overlap-window selection behavior was tested against official YAML list.
2. build_training_dataset.py was tested with --max_samples 5 and produced expected outputs.

## Current Dataset Processing Review Verdict (2026-04-15)

High-level verdict:

1. Download and extraction are broadly aligned with the official dataset structure and topic intent.
2. The processing layer that turns RGB + LiDAR into dense monocular depth labels is project-specific and needs stronger validation before paper experiments.
3. The previous code is useful as a prototype, but it should not yet be treated as publication-grade without fixing reproducibility and calibration-quality gates.

Current concerns:

1. The LiDAR-to-ZED transform convention in densify_lidar.py should be independently verified against calibration files and visual overlays.
2. Dense interpolation can create plausible but unsupported depth in vegetation gaps; builder now saves valid masks, but confidence/distance handling still needs visual review.
3. Extracted ZED depth is now available as optional builder sanity-check metrics, but actual full-run statistics have not been reviewed yet.
4. build_training_dataset.py now rebuilds manifest rows for reused dense files, but reused rows only contain full projection/sparse metrics when dense labels are regenerated.

Fixes completed on 2026-04-15:

1. build_training_dataset.py now returns manifest/metrics rows when dense files already exist instead of exiting with "No new samples."
2. Added `--no_skip_existing` so dense outputs can be force-regenerated when build parameters change.
3. Added grouped split support with default `--split_strategy time_block` to reduce adjacent-frame train/val/test leakage; legacy random splitting remains available with `--split_strategy random`.
4. Added `dense_lidar_valid_mask_npz/` outputs so downstream evaluation/training can use a valid-label mask.
5. Added optional nearest ZED-depth sanity-check metrics in `all_samples.csv`.
6. Added regression tests for pairing fallback, grouped split behavior, reused dense manifest rows, and ZED-depth metric computation.
7. Added audit_projection_alignment.py to generate small RGB/LiDAR/ZED projection overlay panels before running full dense dataset generation.
8. Added selectable LiDAR-to-ZED transform modes in densify_lidar.py: `production_current` and `exact_lidar_parent_child_inverted`.
9. build*training_dataset.py now accepts `--transform_mode`; alternate transform runs default to a separate output folder named `prepared_training_dataset*<transform_mode>`unless`--output_dir` is explicitly provided.
10. Builder metrics now record `transform_mode`, and regression tests cover transform availability plus manifest tagging.
11. The default dense-label interpolation is now `local_idw`, a conservative local inverse-distance weighted fill that rejects candidate pixels when nearby LiDAR depths disagree too much. This replaced `linear` grid interpolation as the default because full 2D linear triangulation produced visually implausible surfaces in vegetation scenes.

Manual projection-audit observation (2026-04-15):

1. `production_current` and `exact_lidar_parent_child_inverted` both visually align well with vegetation/scene structure in the generated 3-sample audit.
2. `current_chain_no_invert` and `exact_lidar_parent_child_direct` look clearly wrong; projected points form near-vertical bands and do not land on plants/scene structure.
3. User observed little difference between the two plausible candidates, except `exact_lidar_parent_child_inverted` has slightly narrower purple scanline spacing than `production_current`.
4. Decision for now: keep `production_current` as the active/default densify_lidar transform, but make `exact_lidar_parent_child_inverted` runnable as an alternate comparison dataset because it may concentrate projected LiDAR more tightly on plant structures.
5. The old mixed projection-audit output folder was removed and a clean 12-sample projection audit was regenerated under `projection_alignment_audit/`.
6. User inspected the clean 12-sample audit and judged `production_current` versus `exact_lidar_parent_child_inverted` as mostly tied; the main visible difference remains narrower purple projected scanline spacing in `exact_lidar_parent_child_inverted`.
7. Because the larger visual audit is a tie, keep `production_current` as the default label-generation transform unless later quantitative checks against ZED depth or model-evaluation behavior show a clear advantage for the alternate transform.

Legacy linear metrics probe result (2026-04-15):

1. Generated two 50-sample metrics probes using the older `linear` interpolation method, not full datasets:
   - `prepared_training_dataset_metrics_probe_50/` using `production_current`
   - `prepared_training_dataset_metrics_probe_50_exact/` using `exact_lidar_parent_child_inverted`
2. These probe outputs still exist locally, but they are legacy comparison artifacts now that default dense-label interpolation has changed to `local_idw`.
3. Both probes used the first 50 matched RGB-LiDAR samples, so split validation is not meaningful yet: all 50 samples fall into one time block and therefore train=50, val=0, test=0.
4. `production_current` legacy-linear probe summary:
   - median RGB-LiDAR delta: 39.211 ms
   - median dense fill ratio: 0.541213
   - median sparse fill ratio: 0.009131
   - median valid projected ratio: 0.402153
   - median dense depth: 3.084715 m
   - median ZED/LiDAR overlap ratio: 0.355920
   - median ZED-vs-LiDAR absolute difference: 0.631544 m
   - median ZED-vs-LiDAR relative difference: 0.379210
5. `exact_lidar_parent_child_inverted` legacy-linear probe summary:
   - median RGB-LiDAR delta: 39.211 ms
   - median dense fill ratio: 0.439080
   - median sparse fill ratio: 0.009071
   - median valid projected ratio: 0.399315
   - median dense depth: 3.400844 m
   - median ZED/LiDAR overlap ratio: 0.297551
   - median ZED-vs-LiDAR absolute difference: 0.205901 m
   - median ZED-vs-LiDAR relative difference: 0.084877
6. Initial interpretation from the legacy-linear probe: `exact_lidar_parent_child_inverted` appeared quantitatively closer to ZED depth on overlapping pixels, but produced lower dense fill/overlap. Treat this as old supporting evidence only; current decisions should prioritize `local_idw` audit/probe results.
7. Observed risk in the legacy-linear probe: dense max values remained around 95-109 m because `max_interp_depth_m=28.0` clamped only interpolated pixels while preserving far measured LiDAR points. This may be acceptable for raw labels but should be capped or masked consistently for model evaluation.

## Current local_idw projection audit result (2026-04-15)

1. Regenerated the normal ignored `projection_alignment_audit/` with 12 samples using `interpolation_method=local_idw`.
2. Audit parameters recorded in `projection_alignment_audit/audit_summary.json`:
   - `distance_mask_px=25`
   - `local_idw_k=4`
   - `local_idw_power=2.0`
   - `local_idw_max_depth_spread_m=1.25`
   - `local_idw_max_relative_depth_spread=0.35`
3. 12-sample median result for `production_current`:
   - dense fill ratio: 0.433060
   - ZED/LiDAR overlap ratio: 0.219531
   - ZED-vs-LiDAR absolute difference: 0.569570 m
   - ZED-vs-LiDAR relative difference: 0.278299
4. 12-sample median result for `exact_lidar_parent_child_inverted`:
   - dense fill ratio: 0.365558
   - ZED/LiDAR overlap ratio: 0.214457
   - ZED-vs-LiDAR absolute difference: 0.193937 m
   - ZED-vs-LiDAR relative difference: 0.074806
5. Current interpretation: `local_idw` intentionally creates more holes than linear interpolation because it refuses uncertain fills. This is preferable to fake dense vegetation surfaces for evaluation/training labels.

## Current Local Data Snapshot (2026-04-01)

Observed after recent local script/data changes:

1. Download scope set to one base block (max_blocks=1), with overlap-window zed download yielding 21 zed bag chunks for that base time window.
2. Extracted outputs increased substantially:
   - extracted_rgbd RGB frames: 6047 PNG
   - extracted_rgbd depth dataset: 6049 NPZ
   - extracted_lidar scans: 5235 NPZ
3. Local storage footprint now reflects this larger pull:
   - extracted_rgbd: ~16.42 GB
   - extracted_lidar: ~1.46 GB
4. Unique extracted bag prefixes currently indicate expected ratio:
   - zed prefixes: 21
   - base prefixes: 1
5. Current local workspace does not currently contain extracted_dense_lidar/ or prepared_training_dataset/ outputs (needs rerun if required for next stage).
6. build_training_dataset.py now includes parallel processing and optimized timestamp pairing (find_closest_optimized) for faster conversion runs.

## Important Pairing Rule

Do not pair modalities by filename order only.
Use this two-stage rule:

1. Bag level: overlap-window selection (coarse filtering).
2. Frame level: nearest timestamp matching with max delta and same-session preference, then fallback-to-any-session when enabled.

## Key Data Locations

1. Raw/extracted workspace: datasets/citrus-farm-dataset/
2. Extracted RGB: datasets/citrus-farm-dataset/extracted_rgbd/zed2i_zed_node_left_image_rect_color/
3. Extracted LiDAR: datasets/citrus-farm-dataset/extracted_lidar/velodyne_points/
4. Dense outputs: datasets/citrus-farm-dataset/extracted_dense_lidar/
5. Prepared dataset output: datasets/citrus-farm-dataset/prepared_training_dataset/
6. Projection audit output: datasets/citrus-farm-dataset/projection_alignment_audit/ (generated diagnostics; ignored by git)

## Prepared Dataset Artifacts

Generated by build_training_dataset.py:

1. prepared_training_dataset/dense_lidar_npz/
2. prepared_training_dataset/dense_lidar_valid_mask_npz/
3. prepared_training_dataset/metrics/all_samples.csv
4. prepared_training_dataset/metrics/summary.json
5. prepared_training_dataset/splits/train_pairs.txt
6. prepared_training_dataset/splits/val_pairs.txt
7. prepared_training_dataset/splits/test_pairs.txt

Depth-label storage versus visualization:

1. The actual LiDAR-densified labels are numeric `.npz` arrays, not PNG/JPG images. Each stored value represents depth in meters, and invalid/untrusted pixels are represented as 0 or excluded by the valid mask.
2. The valid masks are numeric `.npz` arrays with 1 for trusted depth pixels and 0 for pixels that should not be scored/trained as valid depth.
3. PNG panels generated by audit_projection_alignment.py or densify_lidar.py are visual diagnostics only. They are useful for human inspection and paper figures, but they are not the source labels used for metric computation.
4. Paper-style depth images should be generated later from numeric predictions and numeric labels using a consistent colormap and depth range.
5. In audit detail panels, "LiDAR label visual (near bright)" is the human-facing depth-label visualization. "Support distance, not depth" is only a confidence/support-distance diagnostic and must not be interpreted as the depth label.
6. In audit detail panels, the "Sparse LiDAR depth" subplot uses display-only brightening and light dilation for visibility. It does not change the sparse LiDAR depth array, dense labels, valid masks, or metrics.
7. Current `projection_alignment_audit/overlays/` panels compare all transform candidates. Current detail panels are split by the two plausible dense-label routes:
   - `projection_alignment_audit/details_production_current/`
   - `projection_alignment_audit/details_exact_lidar_parent_child_inverted/`
     These detail folders provide human-facing dense-label visuals for both candidate routes.

Alternate transform comparison:

1. Running build_training_dataset.py with `--transform_mode exact_lidar_parent_child_inverted` and no explicit `--output_dir` writes to `prepared_training_dataset_exact_lidar_parent_child_inverted/`.
2. Metrics and summary files include `transform_mode` so production-current and alternate-transform dense labels can be compared without relying only on folder names.

## Research Communication Artifacts

Prepared for progress reporting and professor decision alignment:

1. reports/citrus_farm_dataset_processing_presentation.md

Current communication stance:

1. The old reports/professor folder was removed because the research structure is being refreshed.
2. Keep new progress/presentation scripts directly under reports/ unless a clearer report taxonomy is created later.
3. The current dataset-processing presentation guide is a 4-slide version for the user's part only, with fuller slide text and simple speaker notes.
4. Slide 4 should use a clean route-comparison metrics table because Slide 3 already shows projection/detail images.
5. Explain interpolation as a useful initial gap-filling method, not as perfect ground truth. Use "LiDAR-densified depth labels with valid masks" for paper-facing language.

## Core Tunables

Download and pairing:

1. max_blocks in download scripts.
2. max_time_delta_sec for frame-level matching.
3. require_same_session preference.
4. fallback_to_any_session (keep preference behavior but recover coverage when session IDs differ).

Densification quality:

1. transform_mode (`production_current` default; `exact_lidar_parent_child_inverted` for alternate comparison)
2. interpolation_method (`local_idw` default; `linear`, `nearest`, and `cubic` remain available for comparison)
3. distance_mask_px
4. local_idw_k
5. local_idw_power
6. local_idw_max_depth_spread_m
7. local_idw_max_relative_depth_spread
8. enable_sparse_morph
9. sparse_morph_kernel
10. sparse_morph_iters
11. max_interp_depth_m
12. clamp_only_interpolated

Builder filters and split:

1. min_dense_fill_ratio
2. train_ratio / val_ratio / test remainder
3. seed
4. split_strategy (default: time_block; random keeps legacy frame-shuffle behavior)
5. time_block_sec
6. max_zed_depth_delta_sec and zed_uint16_scale for ZED-depth sanity metrics

## Known Risks

1. Bag filename timestamp is chunk start time only, not all frame timestamps inside.
2. base and zed chunk durations differ; exact filename timestamp equality is not expected.
3. Calibration misuse can create projection artifacts that look like interpolation problems.
4. The official dataset does not define our dense LiDAR label generation procedure; this is a derived research artifact and needs documentation.
5. Random frame-level splits can overestimate performance if adjacent frames from the same robot pass appear in different splits.
6. ZED rolling shutter, vegetation motion, lighting shifts, and software timestamp synchronization can all affect RGB/depth/LiDAR alignment.
7. LiDAR-densified labels should be evaluated with valid/support masks; dense pixels far from true LiDAR support should not be blindly trusted.

## Terminology For This Project

Use these names consistently in notes and reports:

1. dense LiDAR labels / LiDAR-densified depth labels: LiDAR-derived dense depth labels produced in prepared_training_dataset/dense_lidar_npz.
2. depth dataset: extracted ZED depth maps produced from /zed2i/zed_node/depth/depth_registered.

Important clarification:

1. Current repository contains LiDAR densification only (densify_lidar.py).
2. There is no implemented ZED-depth densification pipeline in the current scripts.
3. Older notes may say "densed lidar dataset"; prefer "dense LiDAR labels" or "LiDAR-densified depth labels" in new paper-facing text.

## Training Strategy Notes (Research Discussion)

1. Current Lite-Mono training path in this repository is self-supervised RGB photometric optimization.
2. depth_gt is currently used for monitoring metrics/logging in trainer.py, not as the primary optimization loss.
3. Current working preference is self-supervised-first with architecture exploration to reduce over-specialization risk and preserve broader cross-farm deployment potential.
4. Dense LiDAR labels are the preferred supervision source when adding supervised or hybrid training for Citrus Farm.
5. For publication fairness, compare methods under the same Citrus data budget and splits:
   - self-supervised baseline (RGB-only)
   - self-supervised variant with architecture improvements
   - optional stage-2 supervised variant using dense LiDAR labels
   - optional stage-2 hybrid variant (self-supervised + supervised depth)
6. Deployment note: LiDAR is required for label creation during training pipeline only; runtime inference remains RGB-only.
7. Strategy is still discussion-stage and not finalized; professor feedback is pending before locking implementation order.

## Verification Checklist

Before declaring dataset ready:

1. Timestamp overlap exists between extracted RGB and LiDAR.
2. Pairing delta statistics are acceptable.
3. Projection alignment looks correct on random visual samples.
4. Dense fill ratio and roughness metrics are stable across many frames.
5. train/val/test splits are generated and non-empty.
6. LiDAR-to-ZED transform convention is verified using calibration files and overlay panels.
7. Split policy is sequence/block/time-aware enough to avoid adjacent-frame leakage.
8. Existing dense outputs can be rerun or reused without losing split/metrics reproducibility.
9. ZED depth is used at least as a sanity-check reference against LiDAR-derived labels where valid.

## Research Reframing Snapshot (2026-04-15)

Working paper direction:

1. Target contribution should be framed as lightweight monocular depth estimation for vegetation-dense citrus/orchard environments, not as a broad global SOTA monocular depth claim.
2. Lite-Mono remains the main efficiency baseline because it is a compact CVPR 2023 self-supervised monocular depth model originally validated mostly around urban/KITTI-style driving data.
3. The research gap is domain shift: vegetation, repetitive canopy texture, thin branches/leaves, partial occlusion, non-planar ground, lighting variation, and robot-scale agricultural navigation needs.
4. Runtime requirement remains RGB-only monocular inference for a pest-killing robot; LiDAR and ZED depth are offline training/evaluation assets only.
5. Paper-facing terminology should prefer "LiDAR-densified depth labels" or "dense LiDAR depth labels"; legacy project notes may still refer to the "densed lidar dataset" for continuity.

## Codebase Review Snapshot (2026-04-15)

Observed from current repository review:

1. Citrus data preparation is mostly separate from the original Lite-Mono training stack.
2. trainer.py and evaluate_depth.py are still KITTI-centered; no Citrus Dataset class, Citrus evaluation script, or supervised/hybrid depth loss is wired into training yet.
3. Current prepared_training_dataset/ output is absent locally; a fresh full builder run is required before training/evaluation milestones depend on it.
4. build_training_dataset.py now rebuilds manifest rows when dense files already exist and can force-regenerate dense outputs with `--no_skip_existing`.
5. Current builder default uses time-block grouped splitting; paper experiments should still confirm the split does not leak near-duplicate frames across train/val/test.
6. Densification quality must be treated as a first-class validation target before supervised/hybrid training, especially calibration correctness, support masks, fill ratio, and visual projection alignment.
7. The original Lite-Mono code still computes KITTI-shaped monitoring crops in compute_depth_losses; Citrus metrics should use Citrus image geometry and masks instead of KITTI Eigen crop assumptions.

## Proposed Paper Milestones (Quality Targets)

Milestone 0 - Dataset and calibration audit:

1. Regenerate prepared_training_dataset/ from the current extracted RGB/LiDAR data.
2. Produce pairing delta statistics, dense-label quality histograms, and random visual alignment panels.
3. Lock dataset version, build parameters, and split policy.

Milestone 1 - Baseline on Citrus:

1. Run original Lite-Mono pretrained weights on Citrus validation/test frames.
2. Evaluate against LiDAR-densified depth labels with Citrus-specific masks and metrics.
3. Record runtime, parameter count, FLOPs, and failure cases in vegetation-heavy scenes.

Milestone 2 - Citrus training integration:

1. Add a Citrus Dataset/DataLoader path that consumes prepared split manifests.
2. Add Citrus-specific evaluation independent of KITTI crops and file formats.
3. Keep original KITTI behavior available for comparison and regression safety.

Milestone 3 - Self-supervised Citrus adaptation:

1. Train/fine-tune Lite-Mono self-supervised on Citrus RGB sequences under fixed splits.
2. Compare against untouched original Lite-Mono using the same evaluation budget.
3. Analyze whether adaptation improves vegetation geometry without overfitting to one field/session.

Milestone 4 - Lightweight vegetation-focused architecture improvement:

1. Add one clearly motivated lightweight module or loss targeted at vegetation-dense failure modes.
2. Keep parameter/FLOP/runtime changes small enough to support the robot deployment story.
3. Run ablations against original Lite-Mono and self-supervised Citrus adaptation.

Milestone 5 - Optional supervised/hybrid extension:

1. Add LiDAR-densified depth supervision or a hybrid photometric + depth loss.
2. Treat this as stage-2 evidence unless professor feedback changes the paper direction.
3. Compare under the same split and data budget as self-supervised variants.

Milestone 6 - Paper package:

1. Report accuracy, robustness/failure cases, efficiency, and deployment relevance.
2. Include qualitative examples in canopy, aisle, trunk, ground, and high-occlusion scenes.
3. Document dataset construction enough for reproducibility.

## Quick Commands

From datasets/citrus-farm-dataset directory:

Download:

1. D:/Conda_Envs/lite-mono/python.exe download_citrusfarm_seq_01_lidar.py
2. D:/Conda_Envs/lite-mono/python.exe download_citrusfarm_seq_01_rgb_depth.py

Extract:

1. D:/Conda_Envs/lite-mono/python.exe extract_left_rgbd_from_raw.py 01_13B_Jackal extracted_rgbd
2. D:/Conda_Envs/lite-mono/python.exe extract_lidar_from_raw.py 01_13B_Jackal extracted_lidar

Build:

1. D:/Conda_Envs/lite-mono/python.exe build_training_dataset.py
2. Optional debug run: D:/Conda_Envs/lite-mono/python.exe build_training_dataset.py --max_samples 5
3. Alternate transform debug run: D:/Conda_Envs/lite-mono/python.exe build_training_dataset.py --transform_mode exact_lidar_parent_child_inverted --max_samples 5 --no_skip_existing

Audit:

1. D:/Conda_Envs/lite-mono/python.exe audit_projection_alignment.py --max_samples 3
2. Inspect generated overlays/details under projection_alignment_audit/ before trusting LiDAR-densified labels.
3. D:/Conda_Envs/lite-mono/python.exe densify_lidar.py --compare_transform_modes

## Change Log

- 2026-03-31: Created AGENTS.md with mandatory read/update workflow and Citrus pipeline context.
- 2026-03-31: Captured overlap-window pairing policy and prepared dataset artifact contract.
- 2026-03-31: Added terminology contract (densed lidar dataset vs depth dataset), clarified no ZED densification script, and documented research strategy/fair-comparison guidance.
- 2026-03-31: Added professor report package (strategy report, 90-second script, Q&A sheet) under reports/professor for structured advisor feedback.
- 2026-03-31: Updated strategy framing to self-supervised-first (discussion-stage), with supervised/hybrid positioned as optional stage-2 comparisons pending professor feedback; refreshed professor-facing report tone to casual update style.
- 2026-04-01: Updated context paths after citrus-farm-dataset rename pass (extract scripts, densify script, and prepared dense label folder naming).
- 2026-04-01: Synced renamed citrus paths in code artifacts (builder import now uses densify_lidar, builder output uses dense_lidar_npz, and prepared split/metrics manifests now reference dense_lidar_npz consistently).
- 2026-04-01: Added latest local data snapshot after one-base/21-zed pull; captured expanded extracted_rgbd/extracted_lidar counts and storage impact, plus note that prepared outputs are currently not present locally.
- 2026-04-11: Added .github/copilot-instructions.md with verified run commands, cross-file architecture overview, and repository-specific conventions for future Copilot sessions.
- 2026-04-14: Updated densify_lidar/build_training_dataset pairing policy to support same-session preference plus optional any-session fallback within max delta; added CLI toggles and regression tests for fallback behavior.
- 2026-04-15: Added paper-oriented research reframing, codebase review findings, and proposed quality-target milestones for Citrus/Lite-Mono publication planning.
- 2026-04-15: Reworked project context to state the publishable research-paper goal, document official Citrus Farm dataset intent, distinguish author-intended extraction from our derived LiDAR-densified label pipeline, and record dataset-processing quality concerns.
- 2026-04-15: Fixed build_training_dataset reproducibility issues: reused dense outputs now still generate manifest rows, added force-regeneration toggle, time-block grouped splitting, valid-mask artifacts, optional ZED-depth sanity metrics, and regression tests.
- 2026-04-15: Added projection alignment audit script and generated a 3-sample diagnostic audit for manual review; audit outputs are ignored by git.
- 2026-04-15: Recorded manual projection-audit result: production_current and exact_lidar_parent_child_inverted look visually plausible, while the other two transform candidates are clearly wrong; production_current remains active for now.
- 2026-04-15: Integrated exact_lidar_parent_child_inverted as a selectable densification/build transform mode for side-by-side dense-label comparison; alternate builder runs default to a separate prepared_training_dataset_exact_lidar_parent_child_inverted folder.
- 2026-04-15: Removed mixed old projection_alignment_audit outputs and regenerated a clean 12-sample projection alignment audit for manual comparison of production_current versus exact_lidar_parent_child_inverted before full dataset generation.
- 2026-04-15: Recorded user review of the clean 12-sample audit as a visual tie between production_current and exact_lidar_parent_child_inverted; production_current remains the default pending quantitative ZED/model checks.
- 2026-04-15: Clarified that LiDAR-densified labels and valid masks are numeric NPZ artifacts for training/evaluation, while PNG depth panels are human-facing diagnostics or future paper figures.
- 2026-04-15: Updated audit detail visualizations so LiDAR labels include a paper-style inverse-depth view ("near bright") and support-distance maps are clearly labeled as not depth; regenerated the 12-sample audit outputs.
- 2026-04-15: Ran 50-sample metrics probes for production_current and exact_lidar_parent_child_inverted; exact_inverted had much lower ZED-vs-LiDAR median error on overlap but lower dense fill/overlap, so transform choice remains open pending a time-spread probe.
- 2026-04-15: Added reports/professor/citrus_farm_projection_progress_script.md as a digestible presentation script and screen-share guide for explaining overlay checks, LiDAR-densified labels, interpolation risk, and metrics tradeoffs.
- 2026-04-15: Updated audit_projection_alignment.py so 12-sample audit outputs include separate dense-label detail folders for both plausible routes: details_production_current and details_exact_lidar_parent_child_inverted.
- 2026-04-15: Reworked reports/professor/citrus_farm_projection_progress_script.md into a slide-oriented, layman-friendly presentation guide with simpler terms and explicit visual assets to show.
- 2026-04-15: Removed the old reports/professor folder and replaced it with reports/citrus_farm_dataset_processing_presentation.md as the current slide/script guide for explaining calibration/line-up checks, densification, interpolation limits, metrics probes, and why the final dataset is not locked yet.
- 2026-04-15: Added reports/citrus_farm_dataset_processing_presentation_concise.md as a 2-3 slide version focused on calibration, densification, and the early route-selection decision; kept the longer script as a backup for deeper discussion.
- 2026-04-15: Fixed audit sparse-depth subplot visibility in audit_projection_alignment.py by using nearest-neighbor rendering and a non-transparent masked color (black) so projected sparse LiDAR scanlines no longer disappear against white panel backgrounds.
- 2026-04-15: Brightened sparse LiDAR depth scanline colors in audit_projection_alignment.py (display-only) by using a brightened turbo colormap for the sparse-depth subplot so projected lines are easier to see while preserving the same underlying depth values and metrics.
- 2026-04-15: Further enhanced sparse LiDAR depth readability in audit_projection_alignment.py by using percentile-normalized inverse-depth coloring plus light display-only line dilation so sparse scanlines appear visibly brighter/thicker on the black background.
- 2026-04-15: Replaced default dense-label interpolation from global `linear` grid interpolation to conservative `local_idw` in densify_lidar.py, build_training_dataset.py, and audit_projection_alignment.py; local_idw fills near sparse LiDAR support but rejects pixels where nearby measured depths disagree, reducing fake vegetation/ground surfaces at the cost of lower coverage.
- 2026-04-16: Verified AGENTS.md against current workspace after outside edits; marked the 50-sample metrics probes as legacy `linear` artifacts, added the current 12-sample `local_idw` audit metrics, and removed the stale current-artifact reference to the deleted concise presentation guide.
- 2026-04-16: Reworked reports/citrus_farm_dataset_processing_presentation.md into a 4-slide guide for the user's presentation section, with more slide-ready text and simple speaker notes covering line-up checks, sparse-to-semidense labels, valid masks, route metrics, and the next validation step.
- 2026-04-16: Added reports/slide4_route_comparison_table.html as a screenshot-friendly Route A versus Route B metrics table for Slide 4, and updated the presentation guide with simple explanations for each metric.
- 2026-04-16: Removed the temporary Slide 4 HTML screenshot helper after use; kept the slide guide's metric explanations and table guidance.

## Update Template (Append On Future Changes)

Date:
Changed files:
What changed:
Why:
Validation run:
Open risks:
Next step:
