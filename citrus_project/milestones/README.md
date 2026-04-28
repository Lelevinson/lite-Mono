# Milestones Workspace

These folders are reserved for milestone-specific work as the project progresses.

Use them to keep new code, experiment helpers, notes, plots, and milestone-scoped artifacts grouped by stage instead of scattering them across the whole repo.

## Folder Map

- `00_dataset_audit/` - dataset construction, calibration checks, label-route validation (complete through full dataset build)
- `01_original_lite_mono_baseline/` - original Lite-Mono baseline runs and evaluation helpers (active; full val/test metrics exist, qualitative review pending)
- `02_citrus_integration/` - Citrus Dataset/DataLoader and evaluation integration
- `03_self_supervised_adaptation/` - self-supervised Citrus fine-tuning/adaptation work
- `04_lightweight_vegetation_improvement/` - lightweight vegetation-focused model/loss improvements
- `05_optional_supervised_or_hybrid/` - optional supervised or hybrid training additions
- `06_paper_package/` - paper tables, figures, writing support, and final packaging

Current milestone state:

- Milestone 0 is complete through the full dataset build.
- Milestone 1 has full original Lite-Mono validation/test metrics; qualitative/failure-case review is the current active next step.

These folders are the intended home for milestone-specific code, notes, helpers, and outputs as each stage becomes active.
