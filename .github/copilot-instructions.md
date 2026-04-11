# Copilot instructions for Lite-Mono

## Session startup

- Read `AGENTS.md` first and treat it as the active project context.
- If code, config, pipeline, or experiment settings change, update `AGENTS.md` in the same turn.

## Build, test, and lint commands

### Environment setup

- `conda env create -f environment.yml`
- `conda env create -f environment.cpu.yml`
- `conda env create -f environment.macos.yml`

### Model train/eval/inference (repo root)

- Train: `python train.py --data_path <kitti_data> --model_name <run_name> --num_epochs 30 --batch_size 12 --mypretrain <encoder_pretrain.pth> --lr 0.0001 5e-6 31 0.0001 1e-5 31`
- Evaluate: `python evaluate_depth.py --load_weights_folder <weights_dir> --data_path <kitti_data> --model lite-mono`
- Single test/smoke run: `python test_simple.py --load_weights_folder <weights_dir> --image_path <image_or_folder>`

### Citrus Farm data pipeline (run in `datasets/citrus-farm-dataset`)

1. `python download_citrusfarm_seq_01_lidar.py`
2. `python download_citrusfarm_seq_01_rgb_depth.py`
3. `python extract_left_rgbd_from_raw.py 01_13B_Jackal extracted_rgbd`
4. `python extract_lidar_from_raw.py 01_13B_Jackal extracted_lidar`
5. `python densify_lidar.py`
6. `python build_training_dataset.py`
- Single pipeline smoke run: `python build_training_dataset.py --max_samples 5`

### Lint

- No repository lint command/config is currently defined.

## High-level architecture

### Lite-Mono training stack (KITTI/self-supervised)

- `train.py` parses `LiteMonoOptions` (`options.py`) and runs `Trainer` (`trainer.py`).
- `Trainer` wires:
  - depth branch: `networks.LiteMono` (`networks/depth_encoder.py`) + `networks.DepthDecoder`
  - pose branch (when enabled): `ResnetEncoder` + `PoseDecoder` (or PoseCNN mode)
- Data loading comes from `datasets` package (`MonoDataset`, `KITTIRAWDataset`, `KITTIOdomDataset`) driven by `splits/<split>/train_files.txt` and `val_files.txt`.
- `layers.py` provides core geometry/loss ops used by training (`disp_to_depth`, `BackprojectDepth`, `Project3D`, `SSIM`, smoothness loss).
- Checkpoints are written to `<log_dir>/<model_name>/models/weights_<epoch>/`; encoder checkpoints include `height`, `width`, `use_stereo`, which are read by `test_simple.py` and `evaluate_depth.py`.

### Citrus Farm label-generation stack

- Scripts in `datasets/citrus-farm-dataset/` are a separate data-prep pipeline.
- Download stage: LiDAR base bags are selected by timestamp order; ZED bags are selected by overlap window from chosen base bags.
- Extraction stage: rosbags are decoded into:
  - RGB PNG: `extracted_rgbd/zed2i_zed_node_left_image_rect_color`
  - ZED depth NPZ: `extracted_rgbd/zed2i_zed_node_depth_depth_registered`
  - LiDAR NPZ: `extracted_lidar/velodyne_points`
- Densification stage: `densify_lidar.py` projects LiDAR into ZED image space, interpolates sparse depth, applies distance-transform masking, and emits diagnostics.
- Dataset build stage: `build_training_dataset.py` does parallel pairing/processing and writes:
  - `prepared_training_dataset/dense_lidar_npz/`
  - `prepared_training_dataset/splits/{train,val,test}_pairs.txt`
  - `prepared_training_dataset/metrics/{all_samples.csv,summary.json}`

## Key conventions specific to this repository

- Pairing is two-stage: overlap-window bag filtering first, then nearest timestamp pairing with `max_time_delta_sec` and same-session preference. Never pair by filename order.
- Filename/session contract for Citrus extracts: `<sensor>_<datetime>_<segment>_bag_<timestamp>.<ext>`. Session token (`<segment>`) is used for safer RGB↔LiDAR matching.
- NPZ payload contract: raw depth, LiDAR clouds, and dense labels are stored in `arr_0`; downstream scripts assume this key.
- Training data dictionaries use tuple keys throughout (`("color", frame_id, scale)`, `("color_aug", frame_id, scale)`, `("disp", scale)`, `("cam_T_cam", 0, frame_id)`); preserve this key scheme when extending trainer/model code.
- `frame_ids` must start with `0`; stereo mode appends `"s"` and changes pose-network behavior.
- Current Citrus strategy is self-supervised-first: `depth_gt` is used for monitoring metrics in `trainer.py`, not as primary optimization loss.
- Builder split manifests are `rgb_rel dense_rel` pairs with relative paths normalized to forward slashes.
- Keep terminology consistent:
  - **densed lidar dataset** = LiDAR-derived dense labels in `prepared_training_dataset/dense_lidar_npz`
  - **depth dataset** = extracted ZED depth maps from `/zed2i/zed_node/depth/depth_registered`
