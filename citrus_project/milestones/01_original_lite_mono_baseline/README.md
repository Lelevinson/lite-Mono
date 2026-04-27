# Milestone 1: Original Lite-Mono Baseline

Use this folder for milestone-specific helpers, notes, or experiment files related to:

- original Lite-Mono inference on Citrus
- baseline evaluation scripts/results
- qualitative baseline figures and failure cases

Current status:

- This is the active next milestone.
- A one-image Lite-Mono sanity demo already exists, but full baseline evaluation has not been completed yet.
- The Citrus evaluator entry point has started as `evaluate_lite_mono_citrus.py`.
- Current evaluator slice: data inspection only.
- Model inference is the next evaluator slice.
- Valid-mask-aware metric computation is not implemented yet.

Main input dataset:

- `citrus_project/dataset_workspace/prepared_training_dataset/`

What this milestone should produce:

- baseline inference on Citrus validation/test data
- evaluation against dense LiDAR labels
- valid-mask-aware metrics
- runtime/parameter notes
- qualitative examples and failure cases

Current helper commands:

```powershell
D:/Conda_Envs/lite-mono/python.exe citrus_project/milestones/01_original_lite_mono_baseline/evaluate_lite_mono_citrus.py --split val --max_samples 3
```

Current helper behavior:

- reads the prepared split file
- joins split entries with `metrics/all_samples.csv`
- checks RGB, dense LiDAR label, and valid-mask paths
- prints image size, array shapes, value summaries, valid-pixel count, and pairing diagnostics

Main record files:

- `AGENTS.md`
- `citrus_project/research/baseline_notes.md`
- `citrus_project/TASK_BOARD.md`
