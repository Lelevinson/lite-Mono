# Task Board

Date: 2026-04-28

## Current Project Position

- Milestone 0 is complete through the full dataset build.
- The next major task is the original Lite-Mono baseline evaluation on Citrus.
- The Citrus evaluator entry point now supports Slice 1 data inspection, Slice 2 model inference, Slice 3 valid-mask-aware metrics, Slice 4 aggregate metric summaries, Slice 5 optional result-file saving, and Slice 6 runtime/FPS metadata.
- A small curated sample pack is still needed for Friend B's deeper work.

## Ownership

### Main Integrator (User)

Current focus:

1. maintain the core Citrus pipeline and repo-wide integration
2. run the original Lite-Mono baseline on the built Citrus split
3. prepare the path into the true Milestone 1 evaluation/metric workflow

Near-term outputs:

- complete baseline evaluation setup beyond the current data-inspection slice
- first baseline metrics/results
- runtime and failure-case notes

### Friend A

Current focus:

1. literature scouting for lightweight monocular depth improvements
2. rank ideas for vegetation-dense scenes
3. identify ideas that are realistic for Milestone 4

Working file:

- `citrus_project/research/literature_tracker.md`

Expected near-term output:

- 5 to 10 candidate ideas with lightweight/risk judgment

### Friend B

Current focus:

1. define scene categories from a small shared sample pack
2. pick representative and difficult example frames
3. prepare qualitative-support notes for later results/paper writing

Working files:

- `citrus_project/research/scene_taxonomy.md`
- `citrus_project/milestones/00_dataset_audit/sample_pack/`

Expected near-term output:

- first-pass scene taxonomy
- example-frame shortlist
- notes on why certain scenes are hard for depth estimation

## Blocked / Waiting

1. Friend B’s deeper work depends on a small curated sample pack being prepared.
2. Baseline evaluation no longer needs an entry-point decision, result-file container, or runtime metadata path, but it still needs final validation/test runs and parameter reporting.

## Next Review Point

After:

1. the sample pack scaffold is ready for sharing
2. the first baseline evaluation attempt is complete
3. Friend A has an initial idea shortlist
