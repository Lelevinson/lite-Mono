# Citrus Farm Dataset Processing Presentation Guide

Purpose: a 4-slide guide for your part of the group presentation. Your teammates can explain the dataset source, download, and extraction. Your part starts after that: checking whether RGB and LiDAR line up, explaining how LiDAR labels are made, and showing the current route decision.

Use simple wording first. Add the technical word only after the simple idea is clear.

## Overall Message

> We already have a working pipeline that can create LiDAR-based depth labels, masks, visuals, and metrics. But the final dataset is not locked yet because label quality is a research decision. We prefer trustworthy labels with holes over fake dense labels.

## Useful Simple Terms

| Technical word | Simple explanation |
|---|---|
| Calibration | Making the camera and LiDAR line up |
| Projection | Drawing LiDAR points on top of the RGB image |
| Transform | The formula used to move LiDAR points into the camera view |
| Sparse LiDAR | LiDAR only gives depth on some scanlines, not every pixel |
| Interpolation | Filling nearby missing pixels using measured LiDAR points |
| Valid mask | A map saying which label pixels we trust |
| Dense model output | The final model's full-image depth prediction |

## Slide 1 - Where My Part Starts

Slide title:

`After Extraction: Can We Trust The Depth Labels?`

Put on the slide:

```text
Raw extracted files:
RGB images + LiDAR scans + ZED depth

My part:
1. Check if LiDAR and camera line up
2. Turn sparse LiDAR into usable depth labels
3. Compare two possible label routes
4. Decide what still needs validation
```

Add this short status box:

```text
Pipeline works: yes
Final dataset locked: not yet
Reason: label quality still needs validation
```

Suggested visual:

Use one RGB image or one overlay image from:

`datasets/citrus-farm-dataset/projection_alignment_audit/overlays/`

Speaker notes:

> My teammates covered how we get the raw data. My part starts after extraction. At this stage, having RGB and LiDAR files is not enough yet. We need to check whether the LiDAR points line up with the camera image, because if the sensors do not line up, the depth labels will be wrong even if the files are downloaded correctly.
>
> So the main question for my part is simple: can we trust the labels we are creating from LiDAR?

Key sentence to remember:

> Correct extraction gives us files. Correct alignment gives us useful labels.

## Slide 2 - Camera and LiDAR Line-Up Check

Slide title:

`Step 1: Make The LiDAR Points Land On The RGB Image`

Put on the slide:

```text
Problem:
The camera sees a 2D image.
LiDAR measures 3D points.

So we need a formula that places LiDAR points onto the image.

If the formula is good:
LiDAR scanlines land on plants, trunks, ground, and road.

If the formula is bad:
LiDAR points become strange bands or miss the scene.
```

Add route names:

```text
Route A = production_current
Route B = exact_lidar_parent_child_inverted
```

Suggested visual:

Use one overlay panel from:

`datasets/citrus-farm-dataset/projection_alignment_audit/overlays/`

Point only to Route A and Route B. Do not spend time on the clearly wrong routes unless asked.

Speaker notes:

> The camera image is flat, but LiDAR points are 3D. So we need a transform, or in simpler words, a line-up formula. This formula tells us where each LiDAR point should appear in the RGB image.
>
> We tested several formula interpretations. Two of them were clearly wrong because the points did not land naturally on the scene. Two looked plausible, so we call them Route A and Route B.
>
> For now, both Route A and Route B are serious candidates. Route B often looks a bit tighter on the plant structure, and the numbers also make it worth keeping.

Simple analogy:

> It is like placing a transparent LiDAR stencil on top of the camera image. If the stencil does not match, the labels cannot be trusted.

## Slide 3 - From Sparse LiDAR To Trustworthy Labels

Slide title:

`Step 2: LiDAR Is Sparse, So We Create Semi-Dense Labels`

Put on the slide:

```text
Sparse LiDAR:
Direct sensor measurements, but only on scanlines.

Interpolation:
Fills nearby missing pixels using nearby LiDAR measurements.

Current safer rule:
Fill only when nearby LiDAR depths agree.
Leave holes when the evidence is uncertain.

Why holes are okay:
Holes mean "do not trust this pixel."
The valid mask tells training/evaluation which pixels to use.
```

Suggested visual:

Use one detail panel from:

`datasets/citrus-farm-dataset/projection_alignment_audit/details_exact_lidar_parent_child_inverted/`

If you crop the panel for the slide, show these three parts:

```text
Sparse LiDAR depth
LiDAR label visual
Valid label mask
```

Speaker notes:

> Raw LiDAR is the most direct measurement, but it is sparse. It does not give depth for every camera pixel. That is why the sparse LiDAR image looks like colored scanlines.
>
> At first, it feels natural to fill all the gaps, but in vegetation this can be dangerous. Leaves, gaps, trunks, and road can be very close in the image but very different in real depth. If interpolation connects them too aggressively, it creates fake surfaces.
>
> So now we use a safer interpolation method. It only fills near real LiDAR support, and it refuses to fill if nearby LiDAR depths disagree too much. This creates more holes, but those holes are honest. They mean we do not have enough evidence for that pixel.
>
> For evaluation or supervised training, we should use the valid mask. The model is judged only where the label is trusted.

Important distinction:

```text
Label image: may have holes, because it is measured evidence.
Model prediction: should be a full depth image.
```

Key sentence to remember:

> We prefer missing labels over fake labels.

## Slide 4 - Current Result And Next Decision

Slide title:

`Current Result: Route B Looks Cleaner, But Final Dataset Is Not Locked`

Put on the slide:

```text
12-sample local_idw audit

Use the screenshot table from:
reports/slide4_route_comparison_table.html
```

Add this final decision box:

```text
Current direction:
Keep Route B as a serious candidate.

Next dataset step:
Run a more time-spread validation probe before full dataset build.
```

Suggested visual:

Use only the metrics table on this slide. Keep the Route A and Route B detail images ready for questions, because Slide 3 already shows the visual examples.

Simple metric explanations to say:

```text
Labeled coverage:
How much of the image gets a trusted LiDAR label.
Higher means more usable label pixels.

Comparison area:
Where both our LiDAR label and ZED depth exist.
This is the area where the checking is possible.

ZED difference:
How far our LiDAR label is from ZED depth.
Lower means the label agrees better with ZED.

Relative difference:
The same difference, but adjusted for distance.
Lower means cleaner agreement.
```

Speaker notes:

> After changing to the safer interpolation, the labels became less dense, but that is expected. It means the method is refusing uncertain pixels.
>
> In the current 12-sample audit, Route A covers more pixels. Route B covers fewer pixels, but where we can compare with ZED depth, Route B has much lower difference.
>
> This does not mean the dataset is final. It means we have a better direction. Before building the full dataset, we should validate on more samples spread across time, not only a small set.

Simple conclusion:

> Route A gives more coverage. Route B looks cleaner. The next step is to validate this trend before locking the final dataset.

## 2-Minute Speaking Script

My part starts after the dataset has already been downloaded and extracted. At that point, we have RGB images, LiDAR scans, and ZED depth files. But raw files alone are not enough. We need to check whether the labels we create from LiDAR are trustworthy.

First, we check whether the camera and LiDAR line up. The camera sees a 2D image, while LiDAR measures 3D points. So we need a formula that places LiDAR points onto the RGB image. If the formula is good, the LiDAR scanlines should land on visible objects like plants, trunks, road, and ground. If it is bad, the points can miss the scene or become strange bands.

We tested several possible line-up formulas. Two were clearly wrong. Two are plausible, so we call them Route A and Route B. Route A is `production_current`, and Route B is `exact_lidar_parent_child_inverted`.

After that, we create labels. Raw LiDAR is sparse, meaning it only gives depth on scanlines, not every pixel. To make it more useful, we fill nearby missing pixels. This is interpolation. But in vegetation, aggressive interpolation is risky because leaves, gaps, trunks, and road can be mixed together. So we changed to a safer method that only fills when nearby LiDAR measurements agree. If the evidence is uncertain, we leave a hole and mark that pixel as invalid.

This is important: the label does not need to be a complete image. The label needs to be trustworthy where it exists. The final depth model will still output a full depth image from RGB, but training and evaluation should only use trusted label pixels.

In the current 12-sample audit, Route A gives more coverage, around 43.31 percent. Route B gives less coverage, around 36.56 percent, but it agrees better with ZED depth. Route B's ZED difference is around 0.194 meters, compared to 0.570 meters for Route A.

So our current conclusion is: Route A gives more labeled pixels, but Route B may be cleaner. We should not lock the final dataset yet. The next step is a more time-spread validation probe before building the full dataset.

## 30-Second Version

My part checks whether the extracted RGB and LiDAR data can produce trustworthy depth labels. First, we verify that LiDAR points line up with the camera image. Then we convert sparse LiDAR scanlines into semi-dense labels, but we avoid filling uncertain vegetation gaps too aggressively. The current safer method creates more holes, but those holes mean the pixel is not trusted. In the current audit, Route A gives more coverage, while Route B agrees better with ZED depth. So Route B is a serious candidate, but we still need a time-spread validation probe before the final dataset build.

## What To Keep Ready For Questions

Keep these ready, but do not put all of them into the main slides:

1. Extra overlay panels from `projection_alignment_audit/overlays/`
2. Extra Route A panels from `projection_alignment_audit/details_production_current/`
3. Extra Route B panels from `projection_alignment_audit/details_exact_lidar_parent_child_inverted/`
4. The audit summary file: `projection_alignment_audit/audit_summary.json`
5. The audit metrics file: `projection_alignment_audit/audit_metrics.csv`

## Main Takeaway

> The pipeline can create LiDAR-based labels, but label quality matters more than making the label look full. A depth model should output a full image, but our labels should only mark pixels we actually trust.
