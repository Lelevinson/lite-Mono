# Milestone 1: Original Lite-Mono Baseline

Use this folder for milestone-specific helpers, notes, or experiment files related to:

- original Lite-Mono inference on Citrus
- baseline evaluation scripts/results
- qualitative baseline figures and failure cases

Current status:

- This is the active next milestone.
- A one-image Lite-Mono sanity demo already exists, but full baseline evaluation has not been completed yet.
- The Citrus evaluator entry point has started as `evaluate_lite_mono_citrus.py`.
- Current evaluator slice: data inspection, optional model inference, valid-mask-aware metric comparison, aggregate metric summaries, and optional result-file saving.
- Runtime reporting, parameter reporting, and final full validation/test runs are not completed yet.

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

```powershell
D:/Conda_Envs/lite-mono/python.exe citrus_project/milestones/01_original_lite_mono_baseline/evaluate_lite_mono_citrus.py --split val --max_samples 1 --run_model --no_cuda
```

```powershell
D:/Conda_Envs/lite-mono/python.exe citrus_project/milestones/01_original_lite_mono_baseline/evaluate_lite_mono_citrus.py --split val --max_samples 0 --run_model --summary_only
```

```powershell
D:/Conda_Envs/lite-mono/python.exe citrus_project/milestones/01_original_lite_mono_baseline/evaluate_lite_mono_citrus.py --split val --max_samples 3 --run_model --summary_only --progress_interval 1 --no_cuda --output_dir citrus_project/milestones/01_original_lite_mono_baseline/results
```

Current helper behavior:

- reads the prepared split file
- joins split entries with `metrics/all_samples.csv`
- checks RGB, dense LiDAR label, and valid-mask paths
- prints image size, array shapes, value summaries, valid-pixel count, and pairing diagnostics
- with `--run_model`, loads `weights/lite-mono`, runs the original model, and prints input tensor, raw closeness level, scaled disparity, predicted depth, and resized depth summaries
- with `--run_model`, also compares predicted depth to dense LiDAR labels on valid-mask pixels and prints raw-scale plus median-scaled depth metrics
- with `--summary_only`, suppresses per-sample detail and prints aggregate metric summaries using per-image metric means
- with `--max_samples 0`, evaluates the full selected split
- with `--output_dir`, saves one aggregate `*_summary.json` file and one `*_per_sample.csv` file

Saved result location:

- `citrus_project/milestones/01_original_lite_mono_baseline/results/`
- `maxN` smoke result files are ignored by default so they are not mistaken for official full-split results

Main record files:

- `AGENTS.md`
- `citrus_project/research/baseline_notes.md`
- `citrus_project/TASK_BOARD.md`
