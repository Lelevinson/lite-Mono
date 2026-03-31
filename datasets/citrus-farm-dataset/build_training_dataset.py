import argparse
import csv
import json
import os
import random
from typing import Dict, List

import cv2
import numpy as np

import densify_lidar as dld


def to_rel(path: str, root: str) -> str:
    return os.path.relpath(path, root).replace("\\", "/")


def save_csv(path: str, rows: List[Dict[str, object]]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not rows:
        return
    with open(path, "w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_split_file(path: str, items: List[Dict[str, object]]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fp:
        for item in items:
            fp.write(f"{item['rgb_rel']} {item['dense_rel']}\n")


def split_items(
    items: List[Dict[str, object]],
    train_ratio: float,
    val_ratio: float,
    seed: int,
) -> Dict[str, List[Dict[str, object]]]:
    rng = random.Random(seed)
    shuffled = list(items)
    rng.shuffle(shuffled)

    n_total = len(shuffled)
    n_train = int(n_total * train_ratio)
    n_val = int(n_total * val_ratio)
    n_test = n_total - n_train - n_val

    train = shuffled[:n_train]
    val = shuffled[n_train : n_train + n_val]
    test = shuffled[n_train + n_val : n_train + n_val + n_test]

    return {"train": train, "val": val, "test": test}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build train/val/test-ready dense depth dataset from extracted RGB and LiDAR files."
    )
    parser.add_argument(
        "--rgb_dir",
        default="extracted_rgbd/zed2i_zed_node_left_image_rect_color",
        help="Folder with extracted RGB .png files",
    )
    parser.add_argument(
        "--lidar_dir",
        default="extracted_lidar/velodyne_points",
        help="Folder with extracted LiDAR .npz files",
    )
    parser.add_argument(
        "--output_dir",
        default="prepared_training_dataset",
        help="Output dataset folder",
    )
    parser.add_argument(
        "--max_time_delta_sec",
        type=float,
        default=0.5,
        help="Max allowed RGB-LiDAR timestamp gap in seconds",
    )
    parser.add_argument(
        "--require_same_session",
        action="store_true",
        default=True,
        help="Require RGB/LiDAR pair to share same bag segment id",
    )
    parser.add_argument(
        "--allow_cross_session",
        action="store_true",
        help="Disable same-session restriction",
    )
    parser.add_argument(
        "--interpolation_method",
        default="linear",
        choices=["nearest", "linear", "cubic"],
    )
    parser.add_argument("--distance_mask_px", type=int, default=25)
    parser.add_argument("--enable_sparse_morph", action="store_true", default=True)
    parser.add_argument("--sparse_morph_kernel", type=int, default=3)
    parser.add_argument("--sparse_morph_iters", type=int, default=1)
    parser.add_argument("--max_interp_depth_m", type=float, default=28.0)
    parser.add_argument("--clamp_only_interpolated", action="store_true", default=True)
    parser.add_argument(
        "--min_dense_fill_ratio",
        type=float,
        default=0.0,
        help="Drop samples with dense fill ratio below this value",
    )
    parser.add_argument("--train_ratio", type=float, default=0.8)
    parser.add_argument("--val_ratio", type=float, default=0.1)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--max_samples",
        type=int,
        default=0,
        help="Optional cap for debugging (0 means all)",
    )
    args = parser.parse_args()

    if args.allow_cross_session:
        args.require_same_session = False

    script_root = os.path.dirname(os.path.abspath(__file__))
    rgb_dir = os.path.abspath(os.path.join(script_root, args.rgb_dir))
    lidar_dir = os.path.abspath(os.path.join(script_root, args.lidar_dir))
    output_dir = os.path.abspath(os.path.join(script_root, args.output_dir))

    dense_dir = os.path.join(output_dir, "dense_lidar_npz")
    metrics_dir = os.path.join(output_dir, "metrics")
    splits_dir = os.path.join(output_dir, "splits")

    os.makedirs(dense_dir, exist_ok=True)
    os.makedirs(metrics_dir, exist_ok=True)
    os.makedirs(splits_dir, exist_ok=True)

    all_rgb = sorted([f for f in dld.glob.glob(os.path.join(rgb_dir, "*.png"))])
    all_lidar = sorted([f for f in dld.glob.glob(os.path.join(lidar_dir, "*.npz"))])

    if not all_rgb:
        raise SystemExit(f"No RGB files found in {rgb_dir}")
    if not all_lidar:
        raise SystemExit(f"No LiDAR files found in {lidar_dir}")

    dld.validate_timestamp_overlap(all_rgb, all_lidar)

    rvec, tvec = dld.get_lidar_to_zed_transform()
    max_delta_ns = int(args.max_time_delta_sec * 1e9)

    rows: List[Dict[str, object]] = []
    paired = 0
    converted = 0
    skipped_low_fill = 0
    skipped_errors = 0

    for idx, rgb_path in enumerate(all_rgb):
        if args.max_samples > 0 and paired >= args.max_samples:
            break

        lidar_path, delta_ns = dld.find_closest_lidar(
            rgb_path,
            lidar_files=all_lidar,
            require_same_session=args.require_same_session,
            max_delta_ns=max_delta_ns,
        )

        if lidar_path is None:
            continue

        paired += 1

        img_bgr = cv2.imread(rgb_path)
        if img_bgr is None:
            skipped_errors += 1
            continue
        img_shape = (img_bgr.shape[0], img_bgr.shape[1])

        try:
            point_cloud = np.load(lidar_path)["arr_0"]
            dense_depth, debug = dld.project_and_densify(
                point_cloud,
                rvec,
                tvec,
                img_shape=img_shape,
                interpolation_method=args.interpolation_method,
                distance_mask_px=args.distance_mask_px,
                enable_sparse_morph=args.enable_sparse_morph,
                sparse_morph_kernel=args.sparse_morph_kernel,
                sparse_morph_iters=args.sparse_morph_iters,
                max_interp_depth_m=args.max_interp_depth_m,
                clamp_only_interpolated=args.clamp_only_interpolated,
                verbose=False,
                return_extras=True,
            )
        except Exception:
            skipped_errors += 1
            continue

        dense_fill_ratio = float(debug["map_diag"]["dense_fill_ratio"])
        if dense_fill_ratio < args.min_dense_fill_ratio:
            skipped_low_fill += 1
            continue

        base_name = os.path.splitext(os.path.basename(rgb_path))[0]
        dense_path = os.path.join(dense_dir, f"{base_name}.npz")
        np.savez_compressed(dense_path, arr_0=dense_depth)

        row = {
            "rgb_rel": to_rel(rgb_path, script_root),
            "dense_rel": to_rel(dense_path, script_root),
            "lidar_rel": to_rel(lidar_path, script_root),
            "session": dld.extract_session_token(rgb_path),
            "time_delta_ms": round(delta_ns / 1e6, 3),
            "dense_fill_ratio": round(dense_fill_ratio, 6),
            "sparse_fill_ratio": round(
                float(debug["map_diag"]["sparse_fill_ratio"]), 6
            ),
            "valid_ratio": round(float(debug["projection_diag"]["valid_ratio"]), 6),
            "roughness_median": debug["map_diag"]["roughness_median"],
        }
        rows.append(row)
        converted += 1

        if (idx + 1) % 100 == 0:
            print(
                f"Processed {idx + 1}/{len(all_rgb)} RGB files | "
                f"paired={paired}, converted={converted}, "
                f"low_fill_skipped={skipped_low_fill}, errors={skipped_errors}"
            )

    if not rows:
        raise SystemExit("No valid dense samples produced. Try relaxing constraints.")

    split_map = split_items(rows, args.train_ratio, args.val_ratio, args.seed)

    write_split_file(os.path.join(splits_dir, "train_pairs.txt"), split_map["train"])
    write_split_file(os.path.join(splits_dir, "val_pairs.txt"), split_map["val"])
    write_split_file(os.path.join(splits_dir, "test_pairs.txt"), split_map["test"])

    save_csv(os.path.join(metrics_dir, "all_samples.csv"), rows)

    summary = {
        "rgb_dir": to_rel(rgb_dir, script_root),
        "lidar_dir": to_rel(lidar_dir, script_root),
        "output_dir": to_rel(output_dir, script_root),
        "num_rgb_total": len(all_rgb),
        "num_lidar_total": len(all_lidar),
        "num_paired": paired,
        "num_converted": converted,
        "num_skipped_low_fill": skipped_low_fill,
        "num_skipped_errors": skipped_errors,
        "num_train": len(split_map["train"]),
        "num_val": len(split_map["val"]),
        "num_test": len(split_map["test"]),
        "params": {
            "max_time_delta_sec": args.max_time_delta_sec,
            "require_same_session": args.require_same_session,
            "interpolation_method": args.interpolation_method,
            "distance_mask_px": args.distance_mask_px,
            "enable_sparse_morph": args.enable_sparse_morph,
            "sparse_morph_kernel": args.sparse_morph_kernel,
            "sparse_morph_iters": args.sparse_morph_iters,
            "max_interp_depth_m": args.max_interp_depth_m,
            "clamp_only_interpolated": args.clamp_only_interpolated,
            "min_dense_fill_ratio": args.min_dense_fill_ratio,
            "train_ratio": args.train_ratio,
            "val_ratio": args.val_ratio,
            "seed": args.seed,
        },
    }

    with open(os.path.join(metrics_dir, "summary.json"), "w", encoding="utf-8") as fp:
        json.dump(summary, fp, indent=2)

    print("\nBuild complete")
    print(f"  total RGB: {len(all_rgb)}")
    print(f"  paired: {paired}")
    print(f"  converted: {converted}")
    print(
        f"  train/val/test: {len(split_map['train'])}/{len(split_map['val'])}/{len(split_map['test'])}"
    )
    print(f"  outputs: {output_dir}")


if __name__ == "__main__":
    main()
