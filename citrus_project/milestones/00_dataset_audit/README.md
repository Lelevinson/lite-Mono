# Milestone 0: Dataset Audit

Use this folder for milestone-specific helpers, notes, or experiment files related to:

- dataset construction
- calibration/projection checks
- label-route decisions
- dense-label quality validation

Current status:

- Milestone 0 is complete through the full dataset build.
- The final/default dense-label route is `exact_lidar_parent_child_inverted`.
- The default densification method is `local_idw`.
- The prepared dataset has already been built at:
  - `citrus_project/dataset_workspace/prepared_training_dataset/`

Final built dataset summary:

- total samples: 5282
- train: 4311
- val: 564
- test: 407

Main record files:

- `AGENTS.md`
- `citrus_project/research/dataset_notes.md`
- `citrus_project/dataset_workspace/prepared_training_dataset/metrics/summary.json`

Hand-off to next milestone:

- Milestone 1 is now the active next stage: original Lite-Mono baseline evaluation on the built Citrus split.

Low-storage collaboration support:

- `sample_pack/` is the place for a small shared set of RGB images, label visuals, and lightweight indexing files so teammates can help without downloading the full dataset workspace.
