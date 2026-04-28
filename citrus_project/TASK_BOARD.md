# Task Board

Date: 2026-04-28

## Current Project Position

- Milestone 0 is complete through the full dataset build.
- The original Lite-Mono baseline evaluation has now produced full validation/test result files on Citrus.
- The Citrus evaluator entry point now supports Slice 1 data inspection, Slice 2 model inference, Slice 3 valid-mask-aware metrics, Slice 4 aggregate metric summaries, Slice 5 optional result-file saving, Slice 6 runtime/FPS metadata, and Slice 7 model parameter/checkpoint metadata.
- Slice 8 result-interpretation support now selects good/typical/bad validation samples and renders visual panels.
- The first written visual interpretation note now explains the good/typical/bad panels and the main baseline failure pattern.
- Test good/typical/bad visual panels are now generated too.
- The next Milestone 1 choice is whether to build a broader failure taxonomy, add FLOPs/deployment benchmarking, or move into Milestone 2.
- A small curated sample pack is still needed for Friend B's deeper work.

## Ownership

### Main Integrator (User)

Current focus:

1. maintain the core Citrus pipeline and repo-wide integration
2. review and explain the original Lite-Mono full Citrus baseline visuals/results
3. decide whether Milestone 1 needs a broader failure taxonomy or can move to Milestone 2

Near-term outputs:

- baseline result interpretation
- optional broader failure taxonomy
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
2. Baseline evaluation no longer needs final validation/test runs, validation/test visual selection, or first written interpretation; remaining Milestone 1 extras are optional depth, FLOPs, or broader taxonomy.

## Next Review Point

After:

1. the sample pack scaffold is ready for sharing
2. the user decides whether Milestone 1 is sufficient or needs optional extras
3. Friend A has an initial idea shortlist
