import argparse
import csv
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
from PIL import Image


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def load_npz_array(path: Path) -> np.ndarray:
    with np.load(path) as data:
        if "arr_0" in data.files:
            return data["arr_0"]
        if len(data.files) == 1:
            return data[data.files[0]]
        raise ValueError(f"{path} contains multiple arrays and no arr_0 key: {data.files}")


def load_manifest(csv_path: Path) -> Dict[str, Dict[str, str]]:
    with csv_path.open(newline="", encoding="utf-8") as fp:
        rows = list(csv.DictReader(fp))
    return {row["rgb_rel"]: row for row in rows}


def load_split_pairs(split_path: Path) -> List[Tuple[str, str]]:
    pairs = []
    with split_path.open(encoding="utf-8") as fp:
        for line_number, line in enumerate(fp, start=1):
            parts = line.strip().split()
            if not parts:
                continue
            if len(parts) != 2:
                raise ValueError(
                    f"{split_path}:{line_number} expected 2 columns, got {len(parts)}"
                )
            pairs.append((parts[0], parts[1]))
    return pairs


def finite_stats(values: np.ndarray) -> Dict[str, object]:
    finite = values[np.isfinite(values)]
    if finite.size == 0:
        return {"count": 0, "min": None, "median": None, "max": None}
    return {
        "count": int(finite.size),
        "min": float(np.min(finite)),
        "median": float(np.median(finite)),
        "max": float(np.max(finite)),
    }


def format_stats(stats: Dict[str, object]) -> str:
    if stats["count"] == 0:
        return "count=0, min=n/a, median=n/a, max=n/a"
    return (
        f"count={stats['count']}, "
        f"min={stats['min']:.6f}, "
        f"median={stats['median']:.6f}, "
        f"max={stats['max']:.6f}"
    )


def inspect_sample(
    index: int,
    rgb_rel: str,
    dense_rel: str,
    manifest: Dict[str, Dict[str, str]],
    workspace_dir: Path,
) -> None:
    if rgb_rel not in manifest:
        raise KeyError(f"{rgb_rel} is present in split file but missing from all_samples.csv")

    row = manifest[rgb_rel]
    valid_mask_rel = row["valid_mask_rel"]
    manifest_dense_rel = row["dense_rel"]
    if manifest_dense_rel != dense_rel:
        raise ValueError(
            "Split dense path does not match manifest dense path:\n"
            f"  split:    {dense_rel}\n"
            f"  manifest: {manifest_dense_rel}"
        )

    rgb_path = workspace_dir / rgb_rel
    dense_path = workspace_dir / dense_rel
    valid_mask_path = workspace_dir / valid_mask_rel

    with Image.open(rgb_path) as image:
        rgb_size = image.size

    dense = load_npz_array(dense_path)
    valid_mask = load_npz_array(valid_mask_path)
    valid = (valid_mask > 0) & np.isfinite(dense) & (dense > 0)
    valid_depths = dense[valid]

    print(f"\nSample {index}")
    print(f"  RGB:        {rgb_rel}")
    print(f"  Dense:      {dense_rel}")
    print(f"  Valid mask: {valid_mask_rel}")
    print(f"  RGB size:   width={rgb_size[0]}, height={rgb_size[1]}")
    print(f"  Dense:      shape={dense.shape}, dtype={dense.dtype}")
    print(f"  Mask:       shape={valid_mask.shape}, dtype={valid_mask.dtype}")
    print(f"  Dense all finite stats:   {format_stats(finite_stats(dense))}")
    print(f"  Dense valid-mask stats:   {format_stats(finite_stats(valid_depths))}")
    print(
        "  Valid pixels: "
        f"{int(np.count_nonzero(valid))}/{dense.size} "
        f"({np.count_nonzero(valid) / dense.size:.4%})"
    )
    print(f"  Pair delta ms: {row.get('time_delta_ms', 'n/a')}")
    print(f"  Dense fill ratio from manifest: {row.get('dense_fill_ratio', 'n/a')}")


def parse_args() -> argparse.Namespace:
    default_workspace = repo_root() / "citrus_project" / "dataset_workspace"
    parser = argparse.ArgumentParser(
        description="Inspect Citrus prepared split samples for Lite-Mono baseline evaluation."
    )
    parser.add_argument(
        "--dataset_workspace",
        type=Path,
        default=default_workspace,
        help="Path to citrus_project/dataset_workspace.",
    )
    parser.add_argument(
        "--prepared_name",
        default="prepared_training_dataset",
        help="Prepared dataset folder name inside the dataset workspace.",
    )
    parser.add_argument(
        "--split",
        choices=["train", "val", "test"],
        default="val",
        help="Prepared split to inspect.",
    )
    parser.add_argument(
        "--max_samples",
        type=int,
        default=3,
        help="Number of samples to inspect from the selected split.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    workspace_dir = args.dataset_workspace.resolve()
    prepared_dir = workspace_dir / args.prepared_name
    split_path = prepared_dir / "splits" / f"{args.split}_pairs.txt"
    manifest_path = prepared_dir / "metrics" / "all_samples.csv"

    manifest = load_manifest(manifest_path)
    pairs = load_split_pairs(split_path)
    selected_pairs = pairs[: args.max_samples]

    print("Citrus Lite-Mono baseline evaluator")
    print(f"  Dataset workspace: {workspace_dir}")
    print(f"  Prepared dataset:  {prepared_dir}")
    print(f"  Split:             {args.split}")
    print(f"  Split samples:     {len(pairs)}")
    print(f"  Inspecting:        {len(selected_pairs)}")
    print(f"  Manifest rows:     {len(manifest)}")

    for index, (rgb_rel, dense_rel) in enumerate(selected_pairs, start=1):
        inspect_sample(index, rgb_rel, dense_rel, manifest, workspace_dir)


if __name__ == "__main__":
    main()
