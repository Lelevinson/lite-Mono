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
5. The next step is to run the original Lite-Mono baseline properly on Citrus.

## Common Questions

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

Still left:

1. run the original Lite-Mono baseline properly on Citrus
2. collect baseline metrics and failure cases
3. start the adaptation/improvement experiments

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
   - it may still be hurt indirectly if the image has motion blur

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

