# Student Q&A

This file is the beginner-friendly companion to `AGENTS.md`.

Use it for recurring questions, simple explanations, and plain-language reminders that help a new student quickly understand the project without reading every code file first.

Keep answers:

1. simple
2. stable
3. tied to the real project folders/scripts
4. short enough to scan quickly

## Project In One Paragraph

We are trying to improve Lite-Mono, a lightweight monocular depth model, so it works better in vegetation-dense agricultural environments. Right now Citrus Farm is our main benchmark because it is a strong available dataset. The robot should eventually use only one RGB camera at runtime, but during research we use LiDAR and ZED depth offline to build and check our labels.

## Current Big Picture

1. We already extracted the raw Citrus data we need.
2. We checked how LiDAR should line up with the RGB camera.
3. We chose the best label-generation route.
4. We already ran the full final dataset build.
5. We already ran the original Lite-Mono baseline properly on Citrus validation/test data.
6. The next major step is Citrus training/evaluation integration, while optional Milestone 1 polish can be deferred.

## Common Questions

### What are some basic image/model words I should know?

Here are the main ones in simple language:

1. `frame`
   - one image from a video or sequence

2. `target frame`
   - the main image we want the model to explain or predict depth for

3. `source frame`
   - a nearby image, such as the previous or next frame, used during self-supervised training

4. `depth`
   - how far a pixel is from the camera

5. `disparity`
   - an inverse-depth-like value
   - larger disparity usually means the point is closer
   - Lite-Mono predicts disparity first and we later convert it into a depth-like output

6. `pose`
   - where the camera is and which direction it is facing
   - when we say `relative pose`, we mean how the camera moved between two frames

7. `translation`
   - the movement part of pose, such as forward, backward, left, or right

8. `rotation`
   - the turning part of pose, such as turning left, right, up, or down

9. `warp` or `reprojection`
   - digitally moving pixels from one frame so they should line up with another frame

10. `loss`
   - the badness score used during training
   - higher loss means the model is doing worse on that training step

11. `metric`
   - the evaluation number we report after comparing prediction against a reference
   - example idea: lower error metric usually means better depth prediction

12. `inference`
   - running the model to get a prediction
   - no training happens here

13. `deployment`
   - using the model in the real robot/system after training is already finished

### What is the difference between training and evaluation?

They are not the same thing.

1. `training`
   - the model is learning
   - it predicts something
   - the code computes a training loss
   - the optimizer updates the model weights

2. `evaluation`
   - the model prediction is checked
   - we compare it against a reference depth target
   - we compute reported numbers such as error metrics
   - the model weights are not updated

Simple summary:

- training = learning
- evaluation = checking

For the original Lite-Mono style:

1. during self-supervised training, nearby RGB frames are used to build the training loss
2. during evaluation, the final depth prediction is compared against a reference depth map

So:

- training loss changes the model
- evaluation metrics do not directly change the model

### What is a "pair"?

A pair means:

1. one RGB image
2. matched with the closest LiDAR scan in time

Pairing is only the matching step. It does not create a new image by itself.

### Is pairing the same thing as projection?

No.

1. Pairing = choose which LiDAR scan belongs to an RGB image.
2. Projection = place the matched 3D LiDAR points onto the 2D RGB image.
3. Densification = fill some nearby missing depth values so the sparse LiDAR becomes a more usable depth label.

### What is a valid mask?

A valid mask is a trust map for the depth label.

1. `1` means this pixel is trusted enough to use.
2. `0` means do not trust or score this pixel.

The mask is not the same thing as densification. Densification creates label values; the mask tells us which values are safe to use.

### Why does the built dataset contain several data types?

Each item has a different job:

1. RGB image = model input
2. raw LiDAR scan = source measurement used to create the label
3. dense LiDAR label = the depth target we evaluate against
4. valid mask = tells us which label pixels are trustworthy
5. ZED depth path/metrics = an extra sanity check, not the main training target

At runtime, the robot still uses only RGB. The extra data types are for offline research, checking, and evaluation.

### What is inside `prepared_training_dataset/`?

It is **not** just a copy of the raw dataset in a new folder.

It is a **derived training/evaluation package** built from the raw RGB + LiDAR + optional ZED-check information.

Main subfolders:

1. `dense_lidar_npz/`
   - one `.npz` file per RGB frame
   - stores the dense LiDAR depth label as a numeric array
   - current sample arrays are `720 x 1280`, `float32`
   - values are depth in meters

2. `dense_lidar_valid_mask_npz/`
   - one `.npz` file per RGB frame
   - stores a `0/1` trust mask for the label
   - current sample arrays are `720 x 1280`, `uint8`
   - `1` means trusted, `0` means do not score/train that pixel as valid depth

3. `metrics/`
   - `all_samples.csv` = one row per built sample, including paths, pairing delta, fill ratio, and ZED sanity-check metrics
   - `summary.json` = overall counts, split counts, and the build parameters that were used

4. `splits/`
   - `train_pairs.txt`
   - `val_pairs.txt`
   - `test_pairs.txt`
   - each line says which RGB image goes with which dense depth label

So the built dataset is more like:

1. original RGB stays in the extracted folder
2. raw LiDAR stays in the extracted folder
3. new dense labels are generated here
4. new valid masks are generated here
5. split/metric files are generated here

In other words:

- raw dataset = original extracted sensor files
- prepared dataset = processed labels + masks + split metadata for experiments

### Why are split files separate from metrics/metadata files?

The split files answer one small question:

- "Which samples belong to train, validation, or test?"

Our current split files are simple pair lists:

```text
RGB path  dense LiDAR label path
```

The richer metadata lives in:

```text
prepared_training_dataset/metrics/all_samples.csv
```

That CSV has extra fields such as:

1. `rgb_rel`
2. `dense_rel`
3. `valid_mask_rel`
4. `lidar_rel`
5. timestamp pairing diagnostics
6. dense-label fill statistics
7. ZED sanity-check metrics

So, for evaluation:

1. the split file tells us which samples to use
2. `all_samples.csv` tells us the extra file paths and quality metadata for those samples

Could this be tidier? Yes.

A future evaluator can make this easier by loading both files and building one internal table like:

```text
split, rgb_path, dense_label_path, valid_mask_path, metadata...
```

But the current structure is still workable and common enough in research code:

1. small split files are easy to inspect and version
2. one full CSV keeps all sample metadata in one place
3. large numeric arrays stay in separate folders

For Milestone 1, we do not need to rebuild the dataset structure first. The Citrus evaluator can treat `all_samples.csv` as the full manifest and the split files as filters for train/val/test membership.

### Which folders are real data and which are testing folders?

Real extracted data:

1. `citrus_project/dataset_workspace/extracted_rgbd/zed2i_zed_node_left_image_rect_color/`
2. `citrus_project/dataset_workspace/extracted_rgbd/zed2i_zed_node_depth_depth_registered/`
3. `citrus_project/dataset_workspace/extracted_lidar/velodyne_points/`

Testing/diagnostic folders:

1. `citrus_project/dataset_workspace/projection_alignment_audit/`

This testing folder helps us compare routes and inspect quality. It is not the final dataset.

### What did the testing stage actually show?

We tested four possible LiDAR-to-camera alignment routes.

Result:

1. two routes were clearly wrong
2. two routes were believable
3. `production_current` gave more filled pixels
4. `exact_lidar_parent_child_inverted` agreed much better with ZED depth
5. after visual checks and a 200-sample metrics probe, we chose `exact_lidar_parent_child_inverted` as the final/default route

### About how many samples do we expect in the final built dataset?

Current local snapshot:

1. about 6047 RGB frames
2. about 6049 ZED depth maps
3. about 5235 LiDAR scans
4. about 5282 matched RGB-LiDAR pairs in the time-spread probe

The full built dataset now has:

1. 5282 samples total
2. 4311 train
3. 564 val
4. 407 test

### What is already done, and what is still left?

Done:

1. extraction
2. timestamp pairing logic
3. projection audit
4. densification-method cleanup
5. final label-route decision
6. full dataset build
7. original Lite-Mono baseline evaluation on Citrus validation/test splits
8. first validation/test good-typical-bad visual interpretation

Still left:

1. optional Milestone 1 polish, such as broader failure taxonomy or cleaner FLOPs/runtime benchmarking
2. start the Citrus integration and adaptation/improvement experiments

### Where do we write things down for later paper use?

Use this simple rule:

1. `citrus_project/research/paper_shortlist.md` = the shortlist of results that may later go into the paper
2. `citrus_project/research/dataset_notes.md` = evidence for dataset-building and label-quality decisions
3. `citrus_project/research/baseline_notes.md` = evidence for original-model and baseline results
4. `citrus_project/research/student_qna.md` = simple explanations for us, not paper evidence
5. `AGENTS.md` = project status, milestones, defaults, and decisions

### Does the full dataset build use GPU?

No.

1. `build_training_dataset.py` uses CPU parallel workers, not GPU inference.
2. It creates dense labels, valid masks, splits, and metrics.
3. Your GPU matters later for model training or model inference, not for this dataset-build step.

### What exactly is a "depth map"?

A depth map is a **2D array of numbers** where each pixel stores a depth value.

So the most important idea is:

1. it is not mainly "a picture"
2. it is mainly **numeric data**
3. each pixel means "how far is this point from the camera?"

It can be saved in different formats depending on the stage:

1. `.npz` or `.npy`
   - best for real numeric depth values
   - good for training, evaluation, and metric computation

2. `.png` or `.jpeg`
   - usually only a visualization
   - good for humans to look at
   - often color-mapped, so it is not the exact training/evaluation data

For our project:

1. the built LiDAR labels are stored as `.npz`
2. the valid masks are stored as `.npz`
3. visual panels are only for inspection/presentation

For the Lite-Mono demo:

1. `*_disp.npy` = numeric model output
2. `*_disp.jpeg` = human-viewable visualization

One more important detail:

- the model may output **disparity** first, not direct metric depth in meters
- disparity is still a depth-like map, but it is not automatically the same as "true depth in meters"
- for fair evaluation, we later need to make sure the model output and our label format are compared in a compatible way

### What is disparity, and how is it different from our LiDAR labels?

Disparity is an inverse-depth value. It is not "meters", but it has a direct mathematical relationship to depth.

In Lite-Mono, the conversion is:

```text
depth = 1 / scaled_disparity
```

So if `scaled_disparity` is bigger, the final depth becomes smaller.

Example values:

| Scaled disparity | Depth calculation | Meaning |
|---:|---:|---|
| `1.0` | `1 / 1.0 = 1.0` | about 1 meter |
| `0.5` | `1 / 0.5 = 2.0` | about 2 meters |
| `0.25` | `1 / 0.25 = 4.0` | about 4 meters |
| `0.1` | `1 / 0.1 = 10.0` | about 10 meters |
| `0.01` | `1 / 0.01 = 100.0` | about 100 meters |

That is the concrete meaning:

- high disparity value = closer
- low disparity value = farther

This is the opposite direction from depth meters:

| Representation | Bigger number means |
|---|---|
| `depth` in meters | farther away |
| `disparity` | closer |

Depth is the direct everyday meaning:

- `depth = how far away this pixel is from the camera`

Scaled disparity is the inverse-style representation:

- `scaled_disparity = 1 / depth`

There is one extra Lite-Mono detail:

1. the raw network output is a normalized value
2. Lite-Mono maps it into a scaled disparity range
3. then it calculates depth with `1 / scaled_disparity`

The names `min_disp` and `max_disp` can feel backwards at first:

1. `min_depth = 0.1 m`
   - the nearest allowed depth
   - this becomes `max_disp = 1 / 0.1 = 10.0`

2. `max_depth = 100.0 m`
   - the farthest allowed depth
   - this becomes `min_disp = 1 / 100.0 = 0.01`

So:

- nearest depth has the biggest disparity
- farthest depth has the smallest disparity

When we report `min`, `median`, and `max`, those are just summaries of a whole image-shaped array:

1. `min`
   - the smallest value anywhere in the predicted map

2. `median`
   - the middle value after sorting all valid pixels
   - useful because it is less affected by extreme pixels than the average

3. `max`
   - the largest value anywhere in the predicted map

In the original `test_simple.py`, the saved `*_disp.npy` file is the scaled disparity output, not the final depth array.

Our Citrus LiDAR labels are different from the model's raw output:

1. `dense_lidar_npz/`
   - stores depth values in meters
   - example meaning: a pixel value around `3.0` means about 3 meters from the camera
   - invalid or untrusted places may be `0` or ignored by the valid mask

2. `dense_lidar_valid_mask_npz/`
   - stores which label pixels should be trusted
   - `1` means use this pixel for scoring/training
   - `0` means ignore this pixel

For Milestone 1, we do not need to change the original Lite-Mono model just because it outputs disparity first.

Instead, the evaluation code should:

1. run Lite-Mono on the RGB image
2. get the predicted disparity
3. convert or invert it into a depth-style prediction
4. resize it to match the `720 x 1280` Citrus label shape
5. compare it with the LiDAR depth label only where the valid mask is `1`

So the change we need is in the evaluation wrapper/script, not in the model architecture.

### What are raw disparity, scaled disparity, predicted depth, and display images?

These are easy to mix up because the code often uses the short name `disp`.

Important: in Lite-Mono code, `disp` usually means `disparity`, not `display`.

There are four different things:

1. Raw model output
   - code idea: `outputs[("disp", 0)]`
   - shape example: `[1, 1, 192, 640]`
   - values are a per-pixel `level of closeness`
   - `0` means the model is pushing that pixel toward the far side of the allowed range
   - `1` means the model is pushing that pixel toward the near side of the allowed range
   - the output is between `0` and `1` because the depth decoder uses a sigmoid at the end
   - not meters
   - not directly compared with LiDAR labels

2. Scaled disparity
   - code idea: `scaled_disp`
   - converts the `0` to `1` closeness level into the inverse-depth range chosen by Lite-Mono
   - made using Lite-Mono's `min_depth=0.1` and `max_depth=100.0`
   - still not depth meters
   - behaves like inverse depth
   - bigger value means closer
   - this is what the original `test_simple.py` saves as `*_disp.npy`

3. Predicted depth
   - code idea: `depth = 1 / scaled_disp`
   - this is the array that can be compared with depth labels after resizing and masking
   - values are depth-like numbers
   - for self-supervised monocular models, the raw meter scale can still be wrong even after conversion
   - median scaling may be used during evaluation to align the prediction scale with the label scale

4. Display image
   - example: `*_disp.jpeg`
   - a colorized picture for humans to look at
   - not used for metric calculation
   - colors are not the exact numeric values

For Milestone 1 evaluation, the important comparison is:

```text
predicted depth array
vs
LiDAR depth label array
only where valid mask = 1
```

We should not compare the JPEG visualization to anything numeric.

### Why does the model use a `0` to `1` closeness level first?

The model uses a bounded output because it is easier and more stable for training.

If the network directly output arbitrary meter values, it could produce strange negative values or huge values while learning. Lite-Mono avoids that by making the decoder output a value between `0` and `1`.

Think of the raw output as a slider for each pixel:

```text
0.0 = far end of the allowed depth range
1.0 = near end of the allowed depth range
```

Then Lite-Mono translates that slider into scaled disparity:

```text
scaled_disp = min_disp + (max_disp - min_disp) * raw_disp
```

Using the original settings:

```text
min_depth = 0.1 m
max_depth = 100.0 m
min_disp = 1 / 100.0 = 0.01
max_disp = 1 / 0.1 = 10.0
```

So:

```text
scaled_disp = 0.01 + (10.0 - 0.01) * raw_disp
depth = 1 / scaled_disp
```

Example:

| Raw closeness level | Scaled disparity | Converted depth |
|---:|---:|---:|
| `0.0` | `0.01` | `100.0 m` |
| `0.1` | `1.009` | `0.991 m` |
| `0.5` | `5.005` | `0.200 m` |
| `1.0` | `10.0` | `0.1 m` |

The numbers are not evenly spaced in meters because the model works in inverse depth. Most of the raw `0` to `1` slider gives more detail to closer ranges.

### What is median scaling?

Median scaling is a simple evaluation-time correction for monocular scale.

The model may predict the right relative layout but the wrong absolute meter scale. Example:

1. LiDAR label median depth: `1.918 m`
2. model predicted median depth: `0.583 m`
3. scale ratio: `1.918 / 0.583 = 3.29`

Then every predicted depth value is multiplied by `3.29` before computing the median-scaled metrics.

So if the model predicted:

```text
0.5 m, 1.0 m, 2.0 m
```

after median scaling it becomes:

```text
1.645 m, 3.29 m, 6.58 m
```

Median scaling is not training. It does not change the model. It is only a way to evaluate whether the depth structure is good after fixing the overall scale.

Why use the median instead of the mean or mode?

1. Median is robust to extreme depth values
   - depth maps can contain a few very large or very wrong values
   - the mean can be pulled strongly by those extremes
   - the median is the middle value, so a few extreme pixels affect it much less

2. Mode is not very useful for continuous depth values
   - depth is usually stored as floating-point numbers such as `1.9175627`
   - exact repeated values may be rare
   - the "most common value" can depend too much on binning choices

3. Median matches common monocular depth evaluation practice
   - self-supervised monocular models often get relative depth structure better than exact meter scale
   - median scaling gives one stable global scale correction per image

Simple example:

```text
predicted depths: 1, 2, 3, 4, 100
```

Mean:

```text
(1 + 2 + 3 + 4 + 100) / 5 = 22
```

Median:

```text
middle value = 3
```

The value `100` pulls the mean far away, but the median stays representative of the center of the normal values.

That is why we should report both:

1. raw-scale metrics
   - checks whether the model already predicts correct meters

2. median-scaled metrics
   - checks whether the relative depth structure is good after scale alignment

### What do the depth metric names mean?

In Slice 3, the evaluator compares two one-dimensional lists of numbers after masking:

1. trusted LiDAR label depths, in meters
2. model predicted depths at the same pixels, also in meters after conversion from disparity

The mask matters because we only score pixels where the LiDAR label is trusted.

The metrics are:

1. `abs_rel`
   - average relative error
   - plain meaning: "on average, how big is the error compared with the true distance?"
   - lower is better

2. `sq_rel`
   - squared relative error
   - plain meaning: "like `abs_rel`, but it punishes large mistakes more strongly"
   - lower is better

3. `rmse`
   - root mean squared error in meters
   - plain meaning: "typical meter-sized error, with large mistakes punished heavily"
   - lower is better

4. `rmse_log`
   - RMSE after taking logarithms of depth
   - plain meaning: "typical ratio-style error instead of raw meter error"
   - lower is better

5. `a1`, `a2`, `a3`
   - accuracy threshold scores
   - plain meaning: "what fraction of pixels are close enough?"
   - higher is better

For the threshold scores, the evaluator checks:

```text
max(label / prediction, prediction / label)
```

If prediction and label are exactly the same, this value is `1.0`.

`a1` counts pixels where the ratio is below `1.25`.
That means prediction is within about 25% of the label.

`a2` uses `1.25^2`.
`a3` uses `1.25^3`.
So `a3` is more forgiving than `a1`.

### How should I read the full Milestone 1 baseline metrics?

The full baseline result has many numbers, but do not try to understand all of them at once.

Read them in this order:

1. `raw-scale metrics`
   - asks: "Did the model predict the correct real-world meter scale directly?"
   - for original Lite-Mono on Citrus, the answer is mostly no
   - validation raw `abs_rel=0.7128` and raw `a1=0.0195`
   - plain meaning: before scale correction, almost no valid pixels are close enough

2. `median-scaled metrics`
   - asks: "If we fix the model's overall scale per image, does the near/far structure look useful?"
   - validation median-scaled `abs_rel=0.4176` and `a1=0.4629`
   - plain meaning: after scale correction, about 46% of valid pixels are within the strict 25% threshold on validation

3. `valid fraction`
   - asks: "How much of the image was actually scored?"
   - validation mean valid fraction is about `37.2%`
   - plain meaning: the LiDAR label does not cover every pixel, so metrics are computed only on trusted label pixels

4. `scale ratio`
   - asks: "How much did median scaling need to multiply the prediction?"
   - validation median scale ratio is about `3.58`
   - plain meaning: the raw model prediction was usually too close, so it needed to be stretched farther before median-scaled scoring

5. `runtime/FPS`
   - asks: "How fast was this evaluator/model path?"
   - validation model-forward FPS was about `28.48`
   - plain meaning: the network part ran around 28 frames per second on the user's RTX 4060 Laptop GPU inside this evaluator

The most beginner-useful pair is usually:

```text
abs_rel = average size of the relative error, lower is better
a1      = fraction of valid pixels within about 25%, higher is better
```

For the current full validation baseline:

```text
raw-scale:      abs_rel=0.7128, a1=0.0195
median-scaled: abs_rel=0.4176, a1=0.4629
```

That tells us:

1. the original pretrained model's absolute meter scale transfers badly to Citrus
2. after scale correction, it has some useful relative structure
3. but the result is still weak enough to justify Citrus adaptation or a vegetation-focused improvement

The other metrics are still useful, but they are supporting details:

1. `sq_rel`
   - emphasizes large relative mistakes more than `abs_rel`

2. `rmse`
   - meter-sized error, but can be dominated by far-depth mistakes

3. `rmse_log`
   - ratio-style error; less dominated by raw meter distance

4. `a2` and `a3`
   - more forgiving versions of `a1`
   - if `a1` is low but `a2`/`a3` are high, the prediction is often directionally close but not precise

For early interpretation, focus on:

```text
raw abs_rel, raw a1, median-scaled abs_rel, median-scaled a1, valid fraction, scale ratio
```

Then use visual panels to understand what those numbers look like in real images.

### How should I read the good/typical/bad visual panels?

The visual panels are there to make the metrics feel less abstract.

Each panel shows:

1. the RGB image
2. the model's raw depth prediction
3. the model's median-scaled depth prediction
4. the LiDAR depth label on valid pixels
5. the valid mask
6. the absolute error after median scaling

For the depth images:

```text
bright/yellow = nearer
dark/purple/black = farther
```

For the error image:

```text
bright = larger mistake
dark = smaller mistake
```

The validation and test examples were selected using `median_scaled_a1`.

The validation examples are:

1. good sample
   - `a1=0.826`
   - most valid pixels are close enough after scale correction

2. typical sample
   - `a1=0.478`
   - close to the middle behavior of the validation split

3. bad sample
   - `a1=0.047`
   - almost no valid pixels are close enough after scale correction

The test examples show the same general spread:

1. good sample
   - `a1=0.771`

2. typical sample
   - `a1=0.530`

3. bad sample
   - `a1=0.076`

The important lesson:

- a smooth-looking depth prediction is not automatically correct
- the model can make a pretty full-image depth map while still disagreeing with LiDAR in the valid-mask region
- this is why we need both metrics and visual panels

For our baseline, the visual panels suggest:

1. the original model sometimes gets the broad orchard layout right
2. it often smooths over vegetation and row structure
3. it can fail badly around trees, ground boundaries, gaps, and canopy shapes

That is the practical meaning of the Citrus domain gap.

### What exact values move through Milestone 1 baseline evaluation?

Here is one real validation sample as an example. This is only an example walkthrough, not an official result.

Sample paths are relative to `citrus_project/dataset_workspace/`:

1. RGB input:
   - `extracted_rgbd/zed2i_zed_node_left_image_rect_color/zed_2023-07-18-14-33-03_13_bag_1689715983638853080.png`

2. LiDAR depth label:
   - `prepared_training_dataset/dense_lidar_npz/zed_2023-07-18-14-33-03_13_bag_1689715983638853080.npz`

3. Valid mask:
   - `prepared_training_dataset/dense_lidar_valid_mask_npz/zed_2023-07-18-14-33-03_13_bag_1689715983638853080.npz`

Step by step:

1. Load RGB image
   - original image size: `1280 x 720`
   - pixel values start as image colors

2. Resize for Lite-Mono
   - model input size from `weights/lite-mono/encoder.pth`: `640 x 192`
   - PyTorch input tensor shape: `[1, 3, 192, 640]`
   - meaning: batch size `1`, RGB channels `3`, height `192`, width `640`
   - tensor values are normalized image values from `0.0` to `1.0`

3. Run the original pretrained model
   - output raw disparity tensor shape: `[1, 1, 192, 640]`
   - meaning: batch size `1`, one predicted map, height `192`, width `640`
   - example raw disparity range for this sample: about `0.036` to `0.573`

4. Convert raw disparity to scaled disparity and depth
   - Lite-Mono constants: `min_depth=0.1`, `max_depth=100.0`
   - `min_disp = 1 / 100.0 = 0.01`
   - `max_disp = 1 / 0.1 = 10.0`
   - conversion: `scaled_disp = 0.01 + (10.0 - 0.01) * raw_disp`
   - conversion: `depth = 1 / scaled_disp`
   - example scaled disparity range: about `0.367` to `5.737`
   - example predicted depth range at model size: about `0.174 m` to `2.723 m`

5. Resize prediction back to Citrus label size
   - resized prediction shape: `720 x 1280`
   - this makes prediction and label line up pixel by pixel

6. Load LiDAR label and valid mask
   - dense label shape: `720 x 1280`
   - dense label values are meters
   - valid mask shape: `720 x 1280`
   - valid mask values mean `1 = use this pixel`, `0 = ignore this pixel`

7. Apply the evaluation mask
   - for this sample, valid pixels after mask and `80 m` cap: `363835`
   - valid fraction: about `39.48%` of image pixels
   - label depth on those valid pixels ranges from about `0.498 m` to `76.073 m`
   - label median depth on those valid pixels is about `1.918 m`

8. Compare prediction to label
   - raw predicted median depth on the same valid pixels: about `0.583 m`
   - label median depth: about `1.918 m`
   - median scale ratio: `1.918 / 0.583 = 3.29`

This is why baseline evaluation usually reports two views:

1. raw-scale result
   - asks whether the model's meter scale already matches the label

2. median-scaled result
   - rescales the prediction by the median ratio first
   - asks whether the predicted depth shape/order is good after scale alignment

Slice 3 one-sample smoke metrics for this same sample:

```text
raw-scale:
abs_rel=0.7046, sq_rel=1.7498, rmse=3.9727, rmse_log=1.3157, a1=0.0010, a2=0.0027, a3=0.0083

median-scaled:
abs_rel=0.1993, sq_rel=0.5087, rmse=2.9395, rmse_log=0.3596, a1=0.7054, a2=0.8697, a3=0.9219
```

This is not the official baseline result because it is only one image. It is mainly a code sanity check showing that:

1. the raw model scale is far too close for this sample
2. the relative depth structure becomes much more reasonable after median scaling

### What does it mean to average metrics over a split?

Slice 3 gives metric numbers for one image.

Slice 4 repeats the same operation for many images:

```text
image 1 -> metric row
image 2 -> metric row
image 3 -> metric row
...
```

Then it averages the metric rows.

This is called a per-image mean:

```text
final abs_rel = average(image_1_abs_rel, image_2_abs_rel, image_3_abs_rel, ...)
```

Why not put all valid pixels from all images into one giant pile?

Because then an image with more valid LiDAR pixels would influence the final score more strongly. The original Lite-Mono evaluator computes one metric row per image and averages those rows, so our Citrus evaluator follows that style.

Simple example:

```text
image 1 abs_rel = 0.20
image 2 abs_rel = 0.40
image 3 abs_rel = 0.30
```

Per-image mean:

```text
(0.20 + 0.40 + 0.30) / 3 = 0.30
```

In the evaluator, `--summary_only` hides the per-image detail and prints the aggregate summary. `--max_samples 0` means "use the whole selected split."

### Why save both summary JSON and per-sample CSV?

The two result files answer different questions.

Summary JSON answers:

```text
What is the overall result of this run?
```

It stores things like:

1. split name
2. number of evaluated samples
3. valid-pixel coverage
4. average raw-scale metrics
5. average median-scaled metrics
6. run settings such as model, depth range, and device

This is the file we would use later for a paper-style result table.

Per-sample CSV answers:

```text
Which individual images were easy or hard?
```

It stores one row per RGB image, including paths and metric values.

This is useful because a single average number does not show failure cases. The CSV lets us sort or inspect samples later, for example:

```text
show me images with high abs_rel
show me images with low a1
show me images with low valid-label coverage
```

Smoke runs such as `max3` are not official results. They only prove that the code path works.

### What does runtime or FPS mean in the evaluator?

Runtime means "how long something took."

FPS means frames per second:

```text
FPS = number of images / seconds
```

The evaluator now records two different timing ideas.

1. Evaluator-loop timing
   - includes image loading
   - includes LiDAR label and mask loading
   - includes model inference
   - includes resizing
   - includes metric computation

This tells us:

```text
how fast this evaluation script processed samples
```

2. Model-forward timing
   - includes the neural network encoder
   - includes the depth decoder
   - includes disparity-to-depth conversion
   - includes resizing prediction to label size

This is closer to:

```text
how fast the model part ran
```

But it is still not a perfect robot deployment benchmark. The evaluator does extra work that a robot may not do, and small GPU smoke runs can be distorted by CUDA warmup.

Simple example:

```text
3 images / 1.5 seconds = 2 FPS
```

That does not mean the final robot system is exactly 2 FPS. It only means this specific evaluator run processed about 2 images per second under those settings.

### What does parameter count mean?

A model parameter is a learned number inside the neural network.

During training, the model changes these numbers to get better.

During inference, the model uses these learned numbers to turn an RGB image into a depth prediction.

Simple mental picture:

```text
RGB image + learned parameters -> predicted depth
```

For the original `lite-mono` depth-inference path we are evaluating:

```text
encoder parameters:       2,848,120
depth decoder parameters:   226,627
total parameters:         3,074,747
```

Plain meaning:

```text
the depth model uses about 3.075 million learned numbers
```

Why does this matter?

Our project cares about lightweight robot deployment. A smaller model usually needs less memory and can be easier to run on robot hardware.

Important detail:

The evaluator counts the encoder and depth decoder used for RGB-only depth inference. It does not include the pose network, because the pose network is used during self-supervised training, not during normal one-image depth inference.

### How does the original Lite-Mono learn depth without direct depth labels?

It mainly learns from nearby RGB frames during self-supervised training.

Simple idea:

1. the model predicts depth for the target frame
2. the pose network predicts how the camera moved between nearby frames
3. using predicted depth + predicted camera motion, the code warps a nearby frame so it should line up with the target frame
4. if the warped image looks similar to the real target image, the loss is lower
5. if it lines up badly, the loss is higher

So the model is learning:

- "predict a depth map that helps nearby frames line up correctly"

This is why nearby frames matter during self-supervised training even when there is no direct depth label.

### What does "pose" mean here?

In this project, pose means the camera's position and viewing direction.

When we say `relative pose`, we mean:

1. how much the camera moved between two frames
2. how much it turned between two frames

So pose is about camera motion between frames, not about the tree's pose or object pose in the general robotics sense.

### Does Lite-Mono use pose during deployment?

Usually no, not in the normal single-image inference path.

For the original runtime story:

1. training uses nearby frames and a pose network
2. normal deployment/inference uses one RGB image and predicts depth from that single image

So:

- pose is important during self-supervised training
- pose is not normally used during the original single-image deployment path

### If speed changes a lot, does pose fully handle that?

Not fully.

During self-supervised training:

1. the pose network helps because it predicts frame-to-frame camera motion
2. this means the method does not assume perfectly constant speed
3. but large motion differences can still make training harder because overlap becomes worse and reprojection becomes noisier

During deployment with one RGB image:

1. pose is not directly used in the normal original Lite-Mono inference path
2. speed can still matter indirectly through motion blur, vibration, or harder image conditions

So the safe summary is:

1. pose partly helps during training
2. pose does not directly solve deployment-time speed effects in the normal single-image runtime path

### Why does the Lite-Mono paper show a whole depth image if our LiDAR labels are still sparse or semi-dense?

Because these are two different things:

1. **model prediction**
2. **label / reference depth**

The model prediction is usually a **full-image output**.
Lite-Mono is a dense monocular depth model, so it predicts one value for almost every pixel in the image.

The LiDAR-based label is different:

1. raw LiDAR is sparse
2. our densification fills some nearby gaps
3. even after densification, the label may still have holes or low-trust areas

So:

- the paper-style colorful depth image is usually the **model's prediction visualization**
- it is not the same thing as the sparse/semi-dense LiDAR label

Why can the model produce a whole image?

Because the model learns visual patterns from RGB:

1. edges
2. texture
3. object shapes
4. scene layout
5. photometric consistency across frames in self-supervised training

So the model is not simply "copying LiDAR points." It is learning to estimate depth everywhere from the image itself.

Simple mental model:

- LiDAR label = partial teacher/reference
- model prediction = full-image estimate

That is why:

1. our label can still be sparse/semi-dense
2. the model output can still look like a full smooth depth image

If we colorize our LiDAR label, it may still look incomplete.
If we colorize the model prediction, it usually looks like a full image because the network predicts a value at nearly every pixel.

### What if the speed between two frames is very different?

This matters mainly during **self-supervised training**, not during single-image inference.

Two cases:

1. **Inference later on one RGB image**
   - frame-to-frame speed does not directly matter
   - the model predicts from one image only
   - pose is not normally used in this original single-image runtime path
   - it may still be hurt indirectly if the image has motion blur or vibration

2. **Training with nearby video frames**
   - yes, very different motion between frames can make training harder
   - if the camera moves too much between two frames, pixel matching becomes less reliable
   - occlusion, blur, and reduced overlap can make the view-synthesis loss less accurate

Did the original Lite-Mono consider this?

Yes, but only in the normal self-supervised way, not with a special "speed-change module."

What the original method does:

1. it predicts the relative camera pose between frames with a pose network
2. it uses nearby frames by default (`[0, -1, 1]`)
3. it inherits Monodepth2-style training tricks:
   - minimum reprojection loss
   - auto-masking

What these help with:

1. the pose network means the method does **not** assume a fixed constant speed
2. minimum reprojection helps when one source frame is less reliable because of occlusion
3. auto-masking helps ignore pixels that break the view-synthesis assumption, such as some motion cases

What it does **not** mean:

- it does not fully solve large motion gaps, motion blur, or highly irregular frame-to-frame changes
- very large frame differences can still reduce training quality

Simple summary:

- Lite-Mono does not require perfectly constant speed
- but self-supervised training works best when neighboring frames still have good visual overlap and reasonable motion between them
- and during normal single-image deployment, speed mainly matters indirectly through image quality, not because pose is being predicted at runtime

### Why does Milestone 2 care about previous and next RGB frames?

Inference and training need different input shapes.

During **inference**, Lite-Mono only needs one RGB image:

```text
current RGB -> predicted depth
```

That is why the Milestone 1 evaluator could run over the full validation/test splits one image at a time.

During **self-supervised training**, Lite-Mono needs nearby frames too:

```text
previous RGB
current RGB
next RGB
```

The model predicts depth for the current RGB image. Then the training code uses the previous/next images to check whether that depth can explain how the scene moved between frames.

Simple mental hook:

- current image = the picture we predict depth for
- previous/next images = nearby pictures used to teach the model through motion
- camera `K` = the camera geometry needed to warp pixels correctly

Why not use any nearby file?

Because using a validation or test image as a training neighbor would leak held-out data into training. That would make later scores less trustworthy.

For Citrus, the safe rule we are checking is:

```text
same split + same session + close timestamp
```

The current Milestone 2 diagnostic found that most Citrus samples can form safe previous/current/next triplets with about 100 ms between neighboring frames.

The current Milestone 2 Dataset can now return either:

1. target-only samples for simple inspection/evaluation plumbing
2. temporal samples with `previous/current/next` RGB frames for self-supervised training plumbing

For training-style samples, the RGB tensors use keys like:

```text
("color", -1, 0)  previous RGB at scale 0
("color",  0, 0)  current RGB at scale 0
("color",  1, 0)  next RGB at scale 0
```

The `0` at the end is the image scale. Scale `0` means the main model input size. Higher scales are smaller versions used by Lite-Mono's multi-scale loss.

### What is the Milestone 2 trainer dry run?

A dry run is a rehearsal, not real training.

For Milestone 2, the dry run checks whether one Citrus training-style batch can pass through the important Lite-Mono training shapes:

1. current RGB goes through the depth model
2. previous/current/next RGB go through the pose path
3. predicted depth plus predicted pose are used to warp nearby frames
4. the code computes a tiny smoke-test reprojection loss

It does **not** update model weights.
It does **not** mean Citrus training is finished.
It also does **not** change root `trainer.py` yet.

Plain meaning:

- the DataLoader now speaks the right basic "language" for Lite-Mono training
- the next careful step is deciding how to wire Citrus into the real trainer without accidentally using KITTI-specific evaluation/cropping assumptions

### What is the Citrus-safe depth-metric guard?

The original Lite-Mono trainer was written around KITTI.

During training, it has a small monitoring step that compares predicted depth with `depth_gt` if ground-truth depth is available. That monitoring step used to assume KITTI geometry:

```text
resize prediction to 375 x 1242
apply the KITTI Eigen crop
compute depth metrics
```

That is fine for KITTI, but wrong for Citrus.

Our Citrus labels are native:

```text
720 x 1280
```

and they also have a `valid_mask`, because not every LiDAR-densified pixel should be trusted.

The new guard adds this rule:

1. KITTI still uses the default `--depth_metric_crop kitti_eigen`
2. Citrus should use `--depth_metric_crop none`
3. if Citrus-shaped labels accidentally try to use the KITTI crop, the code raises a clear error instead of silently computing misleading metrics
4. when `valid_mask` is present, metric logging uses it to ignore invalid pixels

Plain meaning:

- this does not train Citrus yet
- it makes the next training integration safer
- it protects us from reporting wrong monitoring numbers just because the old trainer assumed KITTI image geometry

### Are we using KITTI defaults again when root training says "kitti"?

Not for Citrus training, after the latest Milestone 2 guard.

The original Lite-Mono codebase is KITTI-first, so some option names still mention KITTI. The important question is what happens when we choose:

```text
--dataset citrus
```

The root trainer now resolves Citrus like this:

```text
dataset            = citrus
split              = citrus_prepared
data_path          = citrus_project/dataset_workspace
depth_metric_crop  = none
```

So Citrus does **not** use the KITTI Eigen crop for depth metric logging.

The CLI option is now:

```text
--depth_metric_crop auto
```

Plain meaning:

1. for KITTI, `auto` becomes `kitti_eigen`
2. for Citrus, `auto` becomes `none`
3. if someone explicitly tries `--dataset citrus --depth_metric_crop kitti_eigen`, the trainer rejects it

Why does this matter?

KITTI depth labels are shaped around:

```text
375 x 1242
```

Citrus labels are:

```text
720 x 1280
```

So using the KITTI crop on Citrus would create misleading monitoring numbers. The guard makes that mistake fail early.

Current root smoke result:

1. root `Trainer` loaded Citrus train/val DataLoaders
2. train temporal samples: `4275`
3. validation temporal samples: `560`
4. one CPU batch passed through the normal trainer `process_batch`
5. the photometric loss and depth-monitor number were finite

This is still not a real fine-tuning experiment. It only proves the root trainer can now select Citrus and process one batch without falling back to KITTI metric geometry.

### What does the one-step training smoke prove?

The one-step smoke is the next rehearsal after the dry run.

It checks that the root trainer can do this with one Citrus batch:

```text
load batch
run prediction
compute training loss
run backward pass
update model parameters once
stop
```

This is still **not** a real training experiment.

Why?

Real training means many batches and epochs, saved checkpoints, validation, and later comparison against the original baseline. The one-step smoke only checks that the machinery can move once without breaking.

The latest smoke showed:

1. Citrus train samples loaded through root trainer: `4275`
2. Citrus validation samples loaded through root trainer: `560`
3. `depth_metric_crop` resolved to `none`
4. training loss before the update was finite
5. gradients were finite
6. one encoder parameter changed after the optimizer step

Plain meaning:

- forward pass works
- backward pass works
- optimizer update works
- we still should not treat this as adaptation evidence

The next training-quality detail was color augmentation.
The Citrus loader now supports train-only color augmentation, so during training it can create:

```text
color_aug = a color-jittered version of color
```

Validation still keeps:

```text
color_aug = color
```

That is intentional because validation should be stable and not randomly color-changed.

### What did Citrus color augmentation change?

Original Lite-Mono training uses a color-augmented image tensor called `color_aug`.

Plain meaning:

- `color` = the normal RGB tensor
- `color_aug` = a training-only version with random brightness/contrast/saturation/hue changes

The model predicts depth from `color_aug`, while the photometric comparison still uses the normal color images. This helps the model avoid becoming too dependent on exact lighting and color.

For Citrus, the loader now does this:

1. train split:
   - sometimes applies ColorJitter-style augmentation to `color_aug`
   - uses the same jitter choice for all frames in one temporal sample

2. validation/test split:
   - keeps `color_aug` exactly equal to `color`
   - avoids random validation behavior

The smoke check forced augmentation on and found:

```text
train color_aug difference > 0
validation color_aug difference = 0
```

Plain meaning:

- training augmentation is working
- validation remains stable

### Is Milestone 2 finished?

Milestone 2 core integration is now complete.

What is complete:

1. Citrus Dataset/DataLoader can load prepared split manifests
2. safe previous/current/next temporal triplets are available
3. root trainer can select `--dataset citrus`
4. Citrus automatically uses `depth_metric_crop=none`, not the KITTI crop
5. one root trainer batch can run forward
6. one optimizer step can run backward and update parameters
7. train-only color augmentation works
8. the one-step optimizer smoke also passed on CUDA after the laptop GPU became visible

What is **not** done:

1. no real Citrus fine-tuning experiment has been run yet
2. no useful adapted checkpoint has been produced yet
3. no Milestone 3 comparison against the original baseline has happened yet

So the simple answer is:

```text
Milestone 2 core = finished
Milestone 3 training/adaptation = not started yet
```

Latest GPU smoke:

```text
device = cuda
GPU    = NVIDIA GeForce RTX 4060 Laptop GPU
```

The GPU smoke still does not mean the model is trained. It only proves the one-step training machinery works on the laptop GPU.

### For Milestone 3, are we fine-tuning or training from scratch?

For the main Milestone 3 result, we should fine-tune.

Plain meaning:

- training from scratch = start with random model weights and teach everything from the beginning
- fine-tuning = start from the original Lite-Mono checkpoint, then continue training on Citrus

Why fine-tuning is the main path:

1. Milestone 1 already measured the untouched original Lite-Mono checkpoint on Citrus.
2. Milestone 3 should answer: "How much does normal Citrus self-supervised adaptation help?"
3. Milestone 4 can then answer: "Does our new vegetation-focused idea beat normal Citrus adaptation?"

That gives a fair comparison ladder:

```text
A. original Lite-Mono, no Citrus training
B. original Lite-Mono fine-tuned on Citrus
C. improved model trained with the same Citrus budget
```

If C beats B, the improvement is more convincing because B already received the normal Citrus fine-tuning advantage.

Training from scratch can still be a later optional ablation, but it is not the first main comparison.

### What is `--max_train_steps`?

`--max_train_steps` is a safety brake for training.

Plain meaning:

- `--max_train_steps 0` means "run the normal requested epochs"
- `--max_train_steps 10` means "stop after 10 optimizer updates"

This is useful for Milestone 3 because full training defaults can be large. A smoke run should prove that logging, validation, and saving behave correctly without accidentally starting a long experiment.

Milestone 3 training outputs should go under:

```text
citrus_project/milestones/03_self_supervised_adaptation/runs/
```

The original checkpoint folder:

```text
weights/lite-mono/
```

is only the starting point. Fine-tuning loads those weights into memory and writes new checkpoints somewhere else.

### If training stops, can we continue later?

We tested the basic version of this in the first Milestone 3 smoke.

What happened:

1. A tiny run loaded the original Lite-Mono `encoder` and `depth` weights.
2. It trained for 2 optimizer steps.
3. It saved a new checkpoint under the Milestone 3 `runs/` folder.
4. A second tiny run loaded that saved checkpoint.
5. The second run trained for 1 more optimizer step.

So the basic answer is:

```text
Yes, we can load a saved checkpoint and continue training in a basic way.
```

The saved checkpoint included:

```text
encoder.pth
depth.pth
pose_encoder.pth
pose.pth
adam.pth
adam_pose.pth
```

Plain meaning:

- `encoder.pth` and `depth.pth` are the RGB-to-depth model parts
- `pose_encoder.pth` and `pose.pth` are training helper parts for camera motion
- `adam.pth` and `adam_pose.pth` store optimizer memory, such as momentum-like values

Important limitation:

```text
This is basic continuation, not perfect resume.
```

The current trainer still starts the epoch and step counters from zero when launched again. That means loading a checkpoint can continue learning from the saved weights, but it does not perfectly restore the exact training timeline for logging/scheduler bookkeeping.

For short smoke runs, this is fine. Before a long serious experiment, we should decide whether basic continuation is enough or whether we want a more complete resume feature.

### Does a 10-step smoke run give reliable research results?

No. It gives more reliable **engineering evidence**, not research evidence yet.

What the 10-step smoke proves:

1. the original Lite-Mono depth weights can load
2. Citrus temporal batches can keep flowing through the real trainer
3. validation logging no longer crashes
4. the safety brake can stop at exactly 10 optimizer steps
5. a new checkpoint can be saved in the Milestone 3 folder

What it does not prove:

1. the model adapted well to Citrus
2. validation/test depth metrics improved
3. the checkpoint is useful for the paper

Plain meaning:

```text
10-step smoke = the machinery seems stable enough for the next controlled short run
real Milestone 3 result = needs many more planned steps plus evaluation against the Milestone 1 baseline
```

We also evaluated the 10-step checkpoint on 20 validation samples. It was worse than the untouched original baseline on the same 20 samples.

That is not surprising:

- 10 steps is extremely short
- the pose network starts from scratch in this checkpoint setup
- each step sees only one small batch
- early self-supervised training can wiggle before it helps

So the lesson is:

```text
The checkpoint/evaluation pipeline works.
The 10-step checkpoint is not an improved model.
```

### What did the 100-step pilot teach us?

The 100-step pilot is the first small "direction check."

It trained for 100 optimizer updates, then evaluated the checkpoint on the first 100 validation samples.

The result was mixed:

- raw-scale metrics got better in several places
- median-scaled metrics got worse

Plain meaning:

```text
The model may be moving its absolute depth scale toward Citrus.
But after we remove the scale problem, its relative depth structure is not better yet.
```

Why median-scaled metrics matter here:

Median scaling asks, "If we correct the model's overall depth scale for this image, does the shape/layout of near-vs-far regions look right?"

That is important because a monocular model can easily be wrong by a global scale factor. For example, it may predict the scene is 3 times farther than the LiDAR labels. Median scaling removes that one big scale mistake, then checks whether the depth pattern itself is good.

For the 100-step pilot, the median-scaled `a1` dropped:

```text
untouched baseline: 0.4807
100-step checkpoint: 0.3998
```

So the 100-step checkpoint is not a useful adapted model yet. It only tells us the pilot path works and that the next run needs more thought.

### Did the 500-step lower-learning-rate pilot help?

No.

We tried a smaller learning rate, which means the model changed more gently:

```text
old pilot learning rate: 0.0001
new pilot learning rate: 0.00001
```

The idea was:

```text
Maybe the model got worse because we pushed it too hard.
So try smaller steps for longer.
```

But the first 100 validation samples still got worse than the untouched original baseline.

Plain meaning:

```text
The current self-supervised training setup is not automatically improving Citrus depth yet.
More of the same training is not the best next move.
```

This does **not** mean the project failed. It means the pilot did its job: it warned us before a long run.

The likely next step is to inspect the training setup itself, especially:

- whether the pose network is learning useful camera motion
- whether the photometric loss is being fooled by vegetation movement, repeated leaves, shadows, or occlusion
- whether the model should adapt more slowly, freeze some depth layers, or warm up the pose network
- whether the current dataset is too narrow for the final comparison

### What did the training diagnostics find?

The short answer:

```text
The training loss can get better while the actual depth gets worse.
```

That sounds strange, but it can happen in self-supervised depth.

The model is trained by asking:

```text
Can I warp the previous/next RGB image so it looks like the current RGB image?
```

But our real research question is:

```text
Does the predicted depth match the LiDAR-supported Citrus depth labels?
```

Those are related, but not identical.

The diagnostics found several likely trouble spots:

1. The original Lite-Mono folder has depth weights, but no pose weights.
   - depth starts from the original model
   - pose starts from scratch

2. The code path for ImageNet-pretrained pose currently crashes with the installed torchvision version.
   - so we could not simply turn on normal pose pretraining yet

3. Batch size 1 is risky.
   - the depth encoder and pose encoder use BatchNorm
   - BatchNorm estimates image statistics from the current batch
   - with only one sample, those estimates can be noisy

4. The depth encoder also uses DropPath during training.
   - DropPath randomly skips some paths as regularization
   - this can be helpful in big training
   - it may be too noisy for small careful fine-tuning

5. Batch size 4 fits on the GPU for a one-step update.
   - so we are not forced to stay at batch size 1

Plain meaning:

```text
The data loader is probably not the main problem.
The current training recipe is probably too unstable or too easy to "cheat."
```

Good next experiment ideas are:

- use batch size 4
- set `--drop_path 0`
- fix or replace pose pretraining
- warm up pose before changing depth too much
- freeze some depth layers early so the pretrained depth model is not damaged too quickly

### Did batch size 4 and `drop_path 0` fix the training?

No.

This was a good test because it changed only training settings:

```text
batch size: 1 -> 4
drop_path: 0.2 -> 0
```

Plain meaning:

- batch size 4 gives BatchNorm more examples to estimate image statistics
- `drop_path 0` turns off one source of random training noise

The result:

```text
raw distance numbers got better
relative depth pattern got much worse
```

So the model became better at broad "how far is the whole scene?" behavior, but worse at the important pattern inside the image:

- which tree parts are closer
- which gaps are farther
- where ground/vegetation boundaries sit

That means:

```text
Batch size and DropPath were not the whole problem.
We probably need to control pose/depth training itself.
```

The next idea should focus more on:

- pose pretraining or pose warmup
- freezing depth first so the original depth model is not damaged too quickly
- checking whether photometric loss is "winning" by changing scale instead of learning better geometry

### What does "freeze depth while pose warms up" mean?

In this repo, training has two main parts:

- depth model: looks at one RGB image and predicts per-pixel closeness/depth
- pose model: looks at neighboring frames and predicts how the camera moved between them

Self-supervised training needs both. It asks:

```text
If I know the depth of the current image and the camera motion to the next image,
can I warp the next image so it matches the current image?
```

The risky part is that our current Milestone 3 setup starts with good pretrained depth weights, but scratch pose weights. So at the beginning, pose may be wrong. If pose is wrong, the photo-matching loss can push the depth model in a bad direction.

`--freeze_depth_steps N` means:

```text
For the first N training steps:
  update pose
  do not update the trainable depth weights
```

Example:

```text
--freeze_depth_steps 2
step 0: pose updates, depth weights protected
step 1: pose updates, depth weights protected
step 2 onward: both pose and depth can update
```

This is only a safety lever. It does not guarantee better results. It just lets us test whether the early training damage came from changing depth before pose learned reasonable camera motion.

One subtle detail: BatchNorm running statistics can still change during training-mode forward passes even when trainable depth weights are frozen. That is not the same as optimizer-updating the depth weights, but it can still affect the saved encoder state.

### Was the pose-pretraining problem a PyTorch problem?

It was an old-code-versus-new-library problem.

The pose encoder uses a ResNet from torchvision. Older code loaded pretrained ResNet weights through:

```text
torchvision.models.resnet.model_urls
```

The current local environment uses torchvision `0.15.2`, where that old `model_urls` attribute is gone. So PyTorch was not broken; the Lite-Mono compatibility code was old.

The fix was to use torchvision's newer ResNet weights API while keeping the old path as fallback.

Plain meaning:

```text
Before:
  pose pretraining crashed before training could even start

After:
  pretrained pose ResNet can be built and can process fake input tensors
```

This does not prove training quality improves. It only means we can now fairly test a pose model that starts from ImageNet-pretrained ResNet weights instead of starting fully from scratch.

For our Citrus setup:

- frame `0` is the current RGB image
- frame `-1` is the previous RGB image
- frame `1` is the next RGB image
- pose tries to estimate camera movement between these frames

A pretrained pose encoder may help because it already knows basic visual features like edges and textures. It still does not already know Citrus camera motion; that part must be learned during self-supervised training.

### Why can raw metrics improve while median-scaled metrics get worse?

This happened in a Milestone 3 pilot:

```text
raw-scale got better
median-scaled got worse
```

Plain meaning:

- raw-scale asks: "Are the predicted meter distances close to the LiDAR-label meter distances?"
- median-scaled asks: "If we ignore one big scale mistake, is the inside-image depth pattern good?"

Example:

```text
Image label:
  nearby leaves: 2 m
  background gap: 8 m

Prediction A:
  nearby leaves: 1 m
  background gap: 4 m

Prediction B:
  nearby leaves: 3 m
  background gap: 4 m
```

Prediction A has the wrong absolute scale, but the pattern is right:

```text
background is about 4x farther than leaves
```

Prediction B may have some distances closer in meters, but the pattern is worse:

```text
background is only slightly farther than leaves
```

For a pest-killing robot, both matter eventually, but Milestone 3 is showing a specific risk:

```text
self-supervised training can learn a better overall distance scale
while damaging the relative shape of vegetation in the image
```

That is why we do not accept a pilot just because raw metrics improve. We need the median-scaled/relative-depth metrics to stay healthy too.

### What does "diagnosing training with a magnifying glass" mean?

It means we do not only look at the final validation score. We inspect smaller internal signals on the same fixed batches.

For Milestone 3, the useful internal signals are:

- photo loss: how well warped neighboring images match the current image
- pose translation: how large the predicted camera movement is
- predicted depth median: whether the whole depth map becomes too near or too far
- automask fraction: how many pixels the loss chooses from warped images instead of identity images
- LiDAR-valid metrics: whether predictions match the LiDAR-derived depth labels where labels are valid

In the recent diagnostics, photo loss improved even when LiDAR depth quality got worse.

Plain meaning:

```text
The model can get better at the training game
without getting better at the depth result we care about.
```

That is why the next setting change should protect depth structure more directly, not only chase a lower photo loss.

### What is the difference between freezing the depth encoder and updating the depth decoder?

Lite-Mono's depth side has two main parts:

- encoder: reads the RGB image and creates visual features
- decoder: turns those features into disparity/depth predictions

A simple mental picture:

```text
RGB image -> encoder features -> decoder depth map
```

The encoder is the large pretrained visual-understanding part. If it changes too quickly, the model may forget useful general image structure. It also has BatchNorm running statistics, which can drift during training even if the optimizer does not update weights.

The decoder is smaller. Updating only the decoder is a cautious test:

```text
keep the visual feature extractor stable
only adjust how features become depth
```

In the 50-step decoder-only pilot, this protection worked mechanically:

```text
encoder weights changed: 0
encoder BatchNorm buffers changed: 0
decoder updated: yes
```

But the validation metrics still got worse. That means the problem is not only "the encoder was drifting." The training loss or pose/mask behavior may still be pushing the decoder in a direction that does not improve Citrus depth.

### Is inspecting the loss the same as inventing a new loss?

No.

In Milestone 3, "inspect the loss" means:

```text
look inside the existing Lite-Mono training score
and print the pieces separately
```

It does not mean:

```text
change what the model optimizes
```

Concrete example from this repo:

The normal Lite-Mono self-supervised loss includes:

- photo/reprojection loss: whether a neighboring frame can be warped to look like the current frame
- automask: whether a pixel uses the warped image or ignores it because the unwarped neighbor already looks similar
- smoothness loss: a small regularizer that discourages noisy disparity

The diagnostic helper now reports those pieces separately. That is like reading a dashboard:

```text
speed, fuel, temperature
```

Reading the dashboard does not change how the car drives.

Adding a new loss would be different. For example:

```text
new term: keep the adapted depth close to original Lite-Mono depth unless the image evidence is strong
```

That would change training behavior. If we need that kind of structure-preserving term, it likely belongs to the later proposed-method milestone, not the core Milestone 3 baseline.

Plain Milestone 3 rule:

```text
Diagnostics are allowed.
Changing the objective is a research-method decision.
```

### If pose training lowers photo loss, why does the depth result not improve?

Because the pose network is only a training helper.

During self-supervised training, Lite-Mono uses two jobs:

```text
depth network: predicts depth/disparity from the current RGB image
pose network: predicts how the camera moved between neighboring frames
```

Together, they try to warp a nearby frame so it matches the current frame.

But during final RGB-only depth inference, we only use:

```text
RGB image -> depth encoder/decoder -> depth prediction
```

The pose network is not used.

So if we train only the pose network while keeping the whole depth path frozen, the training photo loss can improve, but the saved depth model is still the same model. That is exactly what the 50-step fully depth-frozen control showed:

```text
encoder changed: 0
depth decoder changed: 0
first-100 validation metrics: exactly the original baseline
```

Plain meaning:

```text
pose-only training can make the training reconstruction game look better,
but it does not create a better depth model for deployment.
```

If BatchNorm in the depth encoder is allowed to drift, the depth result can move a little even when optimizer updates are frozen. But the larger Milestone 3 failures happened when trainable depth parameters updated.

### Could Milestone 3 be failing only because the runs are too short?

It is possible that a longer run could behave differently, so we should not claim "long training can never recover."

But the short trajectory gave an important warning.

In the seeded warmup-then-depth test:

```text
25 steps: pose warmup only, depth updates = 0
30 steps: 5 depth-update steps
40 steps: 15 depth-update steps
50 steps: 25 depth-update steps
```

The pattern was:

```text
0 depth updates:
  close to baseline

5 depth updates:
  raw distance looked better
  relative depth structure already got worse

15 depth updates:
  relative depth got worse again

25 depth updates:
  both raw and relative depth were bad
```

Plain meaning:

```text
The bad direction starts very soon after the depth network is allowed to update.
```

That does not mean we can never run longer. It means a longer run should not be a blind "let it train and hope" run. It would need monitoring, early stopping, or a safer depth-preservation control.

For the paper, this is useful evidence:

```text
standard self-supervised adaptation is unstable on Citrus
```

If Milestone 3 cannot find a stable standard-control baseline, that becomes motivation for Milestone 4's proposed improvement.

### Why not just train from scratch on Citrus?

Training from scratch means the model starts with random weights instead of using the original Lite-Mono knowledge.

Plain version:

```text
fine-tuning: starts from a model that already knows general depth cues
from scratch: starts from almost nothing
```

From-scratch training is possible technically, but it is a much bigger research decision because:

- the current Citrus training split has 4275 temporal samples, which is small compared with the large datasets normally used to train monocular depth models from scratch
- self-supervised depth training can learn shortcuts from photo matching, especially in vegetation, shadows, repeated leaves, and moving exposure conditions
- if the dataset is small, the model may memorize this sequence instead of learning robust orchard depth
- if we later add more Citrus Farm sequences or other agricultural datasets, from-scratch or larger-scale retraining becomes more reasonable

So the safer current logic is:

```text
Milestone 3: test whether standard fine-tuning/adaptation works
Milestone 4: propose a controlled improvement if standard adaptation is weak
Later: consider from-scratch or bigger-data training if dataset scale supports it
```

This does not mean from-scratch is wrong. It means it should be treated as a later experimental branch, not the first answer to the current Milestone 3 instability.

