# Citrus Farm Dataset Processing Presentation Guide

Purpose: slide guide and speaking script for the part after raw dataset download/extraction. It is written for beginner-friendly explanation, so use the plain wording first and technical terms second.

## What This Presentation Covers

Your teammates can cover:

1. Dataset source
2. Downloading ROS bags
3. Extracting RGB, ZED depth, and LiDAR files

Your part can cover:

1. Making LiDAR and camera line up
2. Comparing two possible line-up formulas
3. Creating LiDAR-densified depth labels
4. Explaining interpolation honestly
5. Showing the small dataset-build/metrics probe
6. Asking professor which label policy is better before final build

Short version:

> We are not finished with the final dataset yet. We have a working pipeline and early quality checks, but we still need to choose the better label-generation route and validate it on more time-spread samples.

## Plain-Language Glossary

| Technical word | Plain explanation |
|---|---|
| Calibration | Making LiDAR and camera line up |
| Transform | The formula for putting LiDAR points onto the camera image |
| Projection | Drawing 3D LiDAR points on the 2D RGB image |
| Sparse LiDAR | LiDAR only hits some pixels, like thin scanlines |
| Densification | Turning sparse LiDAR into a more image-like depth label |
| Interpolation | Filling nearby missing pixels by guessing from measured LiDAR points |
| Valid mask | A map of pixels we trust |
| ZED depth | A second depth source used as a sanity check |
| Dense label | The depth label after filling nearby missing pixels |

Suggested speaking rule:

> Explain the plain meaning first, then mention the technical term.

Example:

> First we check whether the LiDAR and camera line up. Technically, this is a calibration or transform check.

## Slide 1 - Where My Part Starts

Title:

`After Extraction: Can We Trust The Depth Labels?`

Show:

```text
RGB images + LiDAR scans
        ↓
Line-up check
        ↓
Sparse-to-dense depth labels
        ↓
Valid masks + metrics
        ↓
Ready candidate dataset, not final yet
```

Say:

> My teammates explained how we get RGB images and LiDAR scans from the Citrus Farm dataset. My part starts after extraction. We need to check whether these sensors line up and whether the depth labels we generate are trustworthy enough for evaluation or training.

## Slide 2 - Why The Line-Up Check Is Needed

Show:

Use a matching overlay image from:

`datasets/citrus-farm-dataset/projection_alignment_audit/overlays/`

Say:

> The camera image is flat, but LiDAR is 3D. So we need a formula that places LiDAR points onto the RGB image. If the formula is good, the LiDAR scanlines should land on visible objects like plants, tree trunks, and road. If it is bad, the scanlines may look like strange vertical bands or miss the scene.

Simple analogy:

> It is like putting a transparent LiDAR stencil over the camera image. We need the stencil to match the real scene.

## Slide 3 - Two Candidate Routes

Title:

`Two Possible Line-Up Formulas`

Show:

Same overlay image. Point only to the two serious candidates:

1. `production_current`
2. `exact_lidar_parent_child_inverted`

Say:

> We tested several formula interpretations. Two were clearly wrong. These two are the serious candidates. Visually, both are plausible. The main difference is that the exact inverted route looks a little tighter or narrower.

Use simple names during presentation:

```text
Route A = production_current
Route B = exact_lidar_parent_child_inverted
```

## Slide 4 - Why LiDAR Is Not Already A Full Depth Image

Show:

Use a detail image from either route and point to the sparse LiDAR panel.

Say:

> LiDAR does not give depth for every camera pixel. It only gives sparse scanlines. So if we directly use raw LiDAR, most pixels have no depth label.

Then:

> To create a more useful label, we fill nearby missing pixels. This is called interpolation. It is useful, but it is still a guess based on nearby measured points.

Important sentence:

> Because of interpolation, we should call these LiDAR-densified depth labels, not perfect ground truth.

## Slide 5 - What Interpolation Means

Show:

Simple drawing or explain verbally:

```text
LiDAR measured here      missing pixels      LiDAR measured here
        ↓                     ↓                    ↓
      3.0 m        guessed from neighbors        3.4 m
```

Say:

> Interpolation means filling the missing pixels between nearby LiDAR hits. If two nearby LiDAR points are around 3 meters away, the script estimates nearby pixels using those values.

Then add the limitation:

> This is not the best possible method. It is an initial working method. It gives us a usable starting point, but for paper quality we need valid masks, sanity checks, and maybe better label-generation settings later.

Very digestible version:

> Measured LiDAR pixels are more trustworthy. Interpolated pixels are useful but less trustworthy. Pixels too far from LiDAR support should not be trusted.

## Slide 6 - Dense Label Route A

Show:

Use the matching sample from:

`datasets/citrus-farm-dataset/projection_alignment_audit/details_production_current/`

Say:

> This is Route A after sparse LiDAR is turned into a denser label. It covers more area, but some of that area may come from interpolation.

Point to:

- `LiDAR label visual`: the human-friendly depth-label picture
- `Valid label mask`: the trusted pixels
- `Support distance, not depth`: not a label; just shows distance from real LiDAR support

## Slide 7 - Dense Label Route B

Show:

Use the same sample number from:

`datasets/citrus-farm-dataset/projection_alignment_audit/details_exact_lidar_parent_child_inverted/`

Say:

> This is Route B. It tends to cover less area, but our early numbers suggest it may be cleaner where it does create labels.

Point out:

> Less coverage is not automatically worse. If the extra coverage comes from uncertain interpolation, cleaner but smaller labels may be better.

## Slide 8 - Small Dataset-Build Probe

Title:

`Early Metrics: More Coverage vs Cleaner Labels`

Show:

| Metric | Route A | Route B |
|---|---:|---:|
| Dense fill ratio | 54.12% | 43.91% |
| ZED/LiDAR overlap | 35.59% | 29.76% |
| ZED-vs-LiDAR difference | 0.632 m | 0.206 m |
| Relative difference | 37.92% | 8.49% |

Say:

> Route A gives labels to more pixels. Route B gives labels to fewer pixels, but where we can compare it with ZED depth, it is much closer.

Plain conclusion:

> Route A gives more labels. Route B may give cleaner labels.

Caution:

> This was only a 50-frame probe from the beginning of the sequence. It is useful evidence, but not enough to lock the final dataset.

## Slide 9 - Is The Dataset Built And Done?

Answer:

> Not yet.

Explain:

> The script can build dataset artifacts: dense labels, valid masks, splits, and metrics. But before the final build, we need to decide which route to use and validate it on time-spread samples, not only the first 50 frames.

Use this status:

```text
Pipeline works: yes
Final dataset locked: no
Best route chosen: not yet
Next dataset task: time-spread validation probe
```

## Slide 10 - Question For Professor

Ask:

> For this paper, should our labels prioritize cleaner but less dense depth, or broader depth labels with more interpolation?

Follow-up questions:

1. Should LiDAR-densified labels be used only for evaluation, or also for supervised/hybrid training?
2. Is the term "LiDAR-densified pseudo-ground truth with valid masks" acceptable?
3. Should ZED depth remain only a sanity check, or become an auxiliary comparison in the paper?
4. Should dataset finalization be the next milestone before model architecture improvements?

## 2-Minute Speaking Script

My teammates covered the dataset download and extraction. My part starts after that, when we have RGB images and LiDAR scans.

The first question is whether the LiDAR and camera line up. The camera image is 2D, while LiDAR is 3D, so we need a formula that draws LiDAR points onto the RGB image. If the formula is good, the LiDAR scanlines should land on plants, trunks, and road areas. If the formula is bad, the points can look like strange vertical lines or miss the scene.

We tested several possible formulas. Two were clearly wrong. Two are plausible, so we call them Route A and Route B. Route A is the current production route. Route B is the exact inverted route.

After choosing a route, we create depth labels. But raw LiDAR is sparse. It only gives scanlines, not a full depth image. So the script fills nearby missing pixels using interpolation. Interpolation means guessing missing values from nearby measured LiDAR points. This is useful, but not perfect, so we should call the result LiDAR-densified depth labels, not perfect ground truth.

We generated visuals for both routes. Route A covers more pixels. Route B covers fewer pixels. Then we ran a small 50-frame dataset-build probe. Route A filled around 54 percent of the image, while Route B filled around 44 percent. But where we can compare with ZED depth, Route B had much lower error: around 0.21 meters instead of 0.63 meters.

So the current tradeoff is clear: Route A gives more coverage, Route B may give cleaner labels. We are not saying the final dataset is done yet. Our proposed next dataset step is a time-spread validation probe, then we can lock the label route and build the final dataset.

## 30-Second Version

After extraction, we checked whether LiDAR and camera line up by drawing LiDAR points on RGB images. Two line-up formulas are plausible. Then we created LiDAR-densified labels for both routes. Because LiDAR is sparse, the script fills nearby missing pixels, so these labels are useful but not perfect ground truth. Route A gives more labeled pixels, while Route B agrees better with ZED depth where they overlap. We want professor feedback on whether to prioritize broader coverage or cleaner labels before the final dataset build.

## What To Put On Slides

Minimum visual set:

1. One overlay image from `overlays/`
2. Same sample from `details_production_current/`
3. Same sample from `details_exact_lidar_parent_child_inverted/`
4. One small metrics table
5. One "next decision" slide

Do not overload the slides with all 12 samples. Keep the extra samples ready only if professor asks.

## Key Message

> The dataset pipeline can now create labels, masks, visuals, and metrics, but interpolation makes label quality a research decision. We should choose the label route carefully before final dataset generation.
