# Task Board

Date: 2026-04-28

## Current Project Position

- Milestone 0 is complete through the full dataset build.
- The original Lite-Mono baseline evaluation has now produced full validation/test result files on Citrus.
- The Citrus evaluator entry point now supports Slice 1 data inspection, Slice 2 model inference, Slice 3 valid-mask-aware metrics, Slice 4 aggregate metric summaries, Slice 5 optional result-file saving, Slice 6 runtime/FPS metadata, and Slice 7 model parameter/checkpoint metadata.
- Slice 8 result-interpretation support now selects good/typical/bad validation samples and renders visual panels.
- The next Milestone 1 work is explaining those visual failure patterns and deciding whether test visuals, FLOPs, or a dedicated deployment-speed benchmark are needed.
- A small curated sample pack is still needed for Friend B's deeper work.

## Ownership

### Main Integrator (User)

Current focus:

1. maintain the core Citrus pipeline and repo-wide integration
2. review and explain the original Lite-Mono full Citrus baseline visuals/results
3. prepare written qualitative/failure-case notes for Milestone 1

Near-term outputs:

- baseline result interpretation
- qualitative example/failure-case explanation from the first good/typical/bad panels
- runtime and possible FLOPs/deployment-benchmark notes

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
2. Baseline evaluation no longer needs final validation/test runs or first validation visual selection, but Milestone 1 still needs written qualitative/failure-case review before it is a complete handoff.

## Next Review Point

After:

1. the sample pack scaffold is ready for sharing
2. the selected baseline visual panels have written interpretation notes
3. Friend A has an initial idea shortlist
