# Milestone 1 Results

This folder is for saved original Lite-Mono Citrus baseline result files.

Expected files from `evaluate_lite_mono_citrus.py`:

- `*_summary.json`
  - one aggregate summary for a run
  - contains split name, run settings, valid-pixel coverage, raw-scale mean metrics, and median-scaled mean metrics
  - contains evaluator timing and synchronized model-forward timing when model inference is enabled
- `*_per_sample.csv`
  - one row per evaluated RGB image
  - useful for finding easy/hard samples and later qualitative failure cases
  - includes per-sample wall time and model-forward timing columns

Smoke-test outputs with `maxN` in the filename are ignored by default because they are not official baseline results.

Final full-split outputs should use:

```powershell
--max_samples 0
```

and should be reviewed before being committed.

Timing note:

- evaluator-loop timing includes image/label loading, model inference, resizing, and metric computation
- model-forward timing is closer to neural-network inference speed, but it is still measured inside this evaluator rather than a dedicated deployment benchmark
- small GPU smoke runs can be distorted by first-sample CUDA warmup overhead
