# Original Lite-Mono Single-Image Citrus Demo

Date: 2026-04-16

Paper relevance: qualitative baseline / motivation artifact only. This is not a full baseline result.

Purpose: verify that original pretrained Lite-Mono can run on an extracted Citrus RGB frame and produce a full-image disparity visualization.

## Command

The input image was copied out of the dataset folder first so generated outputs do not contaminate extracted dataset artifacts.

```powershell
D:/Conda_Envs/lite-mono/python.exe test_simple.py --load_weights_folder weights/lite-mono --image_path research/generated/lite_mono_single_image_demo/zed_2023-07-18-14-26-49_0_bag_1689715609331936216.png --model lite-mono --no_cuda
```

## Local Generated Files

These files are ignored by git:

- `research/generated/lite_mono_single_image_demo/zed_2023-07-18-14-26-49_0_bag_1689715609331936216.png`
- `research/generated/lite_mono_single_image_demo/zed_2023-07-18-14-26-49_0_bag_1689715609331936216_disp.jpeg`
- `research/generated/lite_mono_single_image_demo/zed_2023-07-18-14-26-49_0_bag_1689715609331936216_disp.npy`

## Interpretation

This run shows that original Lite-Mono can produce a dense prediction on a Citrus RGB image. It starts the baseline milestone, but it does not complete it.

To complete the baseline milestone, the project still needs:

- original Lite-Mono inference on a validation/test split
- evaluation against LiDAR-densified labels and valid masks
- Citrus-specific metrics without KITTI crop assumptions
- runtime, parameter count, and model-size reporting
- qualitative failure-case analysis in vegetation-heavy scenes

## How This Can Appear In The Paper

Use this kind of output later as a qualitative figure only after we generate a proper set of baseline predictions on selected validation/test frames.

Possible paper figure:

- RGB input
- original Lite-Mono prediction
- LiDAR-densified label visualization
- valid mask
- improved model prediction

Do not use the current single-image run as a quantitative result.

