# Citrus Farm Calibration and Densification Presentation Script (Concise)

Purpose: a 2-3 slide version for the part after raw extraction. Keep download/extraction with teammates and use this script only for calibration, densification, and the dataset-quality decision.

## Main message

> We do not have final depth ground truth yet. First we check whether LiDAR and camera line up, then we turn sparse LiDAR into LiDAR-densified depth labels with valid masks, and finally we decide which route to keep for the full build.

## Plain-Language Glossary

| Technical word | Plain explanation |
|---|---|
| Calibration | Making LiDAR and camera line up |
| Transform | The formula that places LiDAR points on the RGB image |
| Densification | Turning sparse LiDAR into a more image-like depth label |
| Interpolation | Filling nearby missing pixels from measured LiDAR points |
| Valid mask | The pixels we trust for training or evaluation |

Suggested speaking rule:

> Explain the plain meaning first, then mention the technical term.

## Slide 1 - Why Calibration Matters

Title:

`Can We Trust The LiDAR-To-Camera Line-Up?`

Show:

One overlay image from:

`datasets/citrus-farm-dataset/projection_alignment_audit/overlays/`

Say:

> After extraction, the first question is whether LiDAR points land on the correct objects in the RGB image. If calibration is right, the scanlines should follow plants, trunks, and road edges. If calibration is wrong, the points drift or form strange bands. This check matters because every later depth label depends on it.

Short analogy:

> It is like placing a transparent LiDAR stencil over the camera image. The stencil has to match the real scene.

## Slide 2 - How Densification Works

Title:

`From Sparse LiDAR To Dense Depth Labels`

Show:

One detail panel from either route, preferably the same sample for both routes.

Use these visual pieces if space allows:

1. Sparse LiDAR projection
2. LiDAR label visual
3. Valid label mask
4. Support distance, not depth

Say:

> Raw LiDAR is sparse. It only hits some pixels, so it cannot directly act like a full depth image. To make it more usable, we project the points into the camera view and fill nearby missing pixels by interpolation. The result is useful, but it is still derived labels, not perfect ground truth.

Key line:

> Measured pixels are more trustworthy. Interpolated pixels are useful but less trustworthy. Pixels too far from LiDAR support should not be treated as fully trusted.

## Slide 3 - What The Early Probe Says

Title:

`More Coverage Or Cleaner Overlap?`

Show:

| Metric | Route A: production_current | Route B: exact_lidar_parent_child_inverted |
|---|---:|---:|
| Dense fill ratio | 54.1% | 43.9% |
| ZED/LiDAR overlap | 35.6% | 29.8% |
| ZED-vs-LiDAR absolute difference | 0.632 m | 0.206 m |
| ZED-vs-LiDAR relative difference | 37.9% | 8.5% |

Say:

> Route A covers more pixels. Route B is closer to ZED depth where they overlap. So the tradeoff is coverage versus cleaner agreement. We are not locking the final dataset yet. We need professor guidance and a time-spread validation probe before final build.

Close with:

> For paper-facing wording, use "LiDAR-densified depth labels with valid masks," not perfect ground truth.

## If You Only Have 2 Slides

Merge Slide 2 and Slide 3:

1. Calibration check and why it matters
2. Densification plus the early route tradeoff

## Short Speaking Script

My part starts after RGB and LiDAR extraction. First, we check whether the two sensors line up. If the calibration is right, LiDAR points land on plants, trunks, and road areas in the RGB image. If the calibration is wrong, the points drift or form strange bands.

Next, we turn sparse LiDAR into more image-like depth labels. This is called densification. The script fills nearby missing pixels by interpolation, which is useful, but it is still derived data, so we keep valid masks and do not call it perfect ground truth.

The early probe shows a tradeoff. The current route gives more coverage, while the inverted route is closer to ZED depth where they overlap. So the dataset is working, but the final label route is still a decision point.
