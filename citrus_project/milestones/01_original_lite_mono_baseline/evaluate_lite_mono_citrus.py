import argparse
import csv
import sys
from pathlib import Path
from typing import Callable, Dict, List, NamedTuple, Optional, Tuple

import numpy as np
from PIL import Image


class LiteMonoModel(NamedTuple):
    encoder: object
    depth_decoder: object
    disp_to_depth: Callable
    device: object
    feed_height: int
    feed_width: int
    min_depth: float
    max_depth: float


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


def ensure_repo_imports(root: Path) -> None:
    root_str = str(root)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)


def load_lite_mono_model(
    weights_folder: Path,
    model_name: str,
    no_cuda: bool,
    min_depth: float,
    max_depth: float,
) -> LiteMonoModel:
    import torch

    root = repo_root()
    ensure_repo_imports(root)

    import networks
    from layers import disp_to_depth

    device = torch.device("cuda" if torch.cuda.is_available() and not no_cuda else "cpu")
    encoder_path = weights_folder / "encoder.pth"
    decoder_path = weights_folder / "depth.pth"

    encoder_dict = torch.load(encoder_path, map_location=device)
    decoder_dict = torch.load(decoder_path, map_location=device)
    feed_height = int(encoder_dict["height"])
    feed_width = int(encoder_dict["width"])

    encoder = networks.LiteMono(model=model_name, height=feed_height, width=feed_width)
    encoder.load_state_dict(
        {key: value for key, value in encoder_dict.items() if key in encoder.state_dict()}
    )
    encoder.to(device)
    encoder.eval()

    depth_decoder = networks.DepthDecoder(encoder.num_ch_enc, scales=range(3))
    depth_decoder.load_state_dict(
        {
            key: value
            for key, value in decoder_dict.items()
            if key in depth_decoder.state_dict()
        }
    )
    depth_decoder.to(device)
    depth_decoder.eval()

    return LiteMonoModel(
        encoder=encoder,
        depth_decoder=depth_decoder,
        disp_to_depth=disp_to_depth,
        device=device,
        feed_height=feed_height,
        feed_width=feed_width,
        min_depth=min_depth,
        max_depth=max_depth,
    )


def image_to_input_tensor(image: Image.Image, model: LiteMonoModel):
    import torch
    from torchvision import transforms

    resized = image.resize((model.feed_width, model.feed_height), Image.LANCZOS)
    tensor = transforms.ToTensor()(resized).unsqueeze(0)
    return tensor.to(model.device)


def run_lite_mono_inference(rgb_path: Path, label_shape: Tuple[int, int], model: LiteMonoModel) -> None:
    import torch
    import torch.nn.functional as F

    with Image.open(rgb_path) as image:
        input_image = image.convert("RGB")
        original_width, original_height = input_image.size
        input_tensor = image_to_input_tensor(input_image, model)

    with torch.no_grad():
        features = model.encoder(input_tensor)
        outputs = model.depth_decoder(features)
        raw_disp = outputs[("disp", 0)]
        scaled_disp, depth = model.disp_to_depth(
            raw_disp, model.min_depth, model.max_depth
        )
        depth_resized = F.interpolate(
            depth,
            size=label_shape,
            mode="bilinear",
            align_corners=False,
        )

    raw_disp_np = raw_disp.detach().cpu().numpy()
    scaled_disp_np = scaled_disp.detach().cpu().numpy()
    depth_np = depth.detach().cpu().numpy()
    depth_resized_np = depth_resized.detach().cpu().numpy()

    print("  Model inference:")
    print(
        "    Input tensor: "
        f"shape={tuple(input_tensor.shape)}, "
        f"dtype={input_tensor.dtype}, "
        f"device={input_tensor.device}, "
        f"range={float(input_tensor.min()):.6f}..{float(input_tensor.max()):.6f}"
    )
    print(
        "    Original RGB size: "
        f"width={original_width}, height={original_height}; "
        f"model feed size: width={model.feed_width}, height={model.feed_height}"
    )
    print(
        "    Raw closeness level: "
        f"shape={tuple(raw_disp.shape)}, {format_stats(finite_stats(raw_disp_np))}"
    )
    print(
        "    Scaled disparity:   "
        f"shape={tuple(scaled_disp.shape)}, {format_stats(finite_stats(scaled_disp_np))}"
    )
    print(
        "    Predicted depth:    "
        f"shape={tuple(depth.shape)}, {format_stats(finite_stats(depth_np))}"
    )
    print(
        "    Resized depth:      "
        f"shape={tuple(depth_resized.shape)}, {format_stats(finite_stats(depth_resized_np))}"
    )


def inspect_sample(
    index: int,
    rgb_rel: str,
    dense_rel: str,
    manifest: Dict[str, Dict[str, str]],
    workspace_dir: Path,
    model: Optional[LiteMonoModel],
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
    if model is not None:
        run_lite_mono_inference(rgb_path, dense.shape, model)


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
    parser.add_argument(
        "--run_model",
        action="store_true",
        help="Also run original Lite-Mono inference for the selected samples.",
    )
    parser.add_argument(
        "--weights_folder",
        type=Path,
        default=repo_root() / "weights" / "lite-mono",
        help="Folder containing encoder.pth and depth.pth.",
    )
    parser.add_argument(
        "--model",
        default="lite-mono",
        choices=["lite-mono", "lite-mono-small", "lite-mono-tiny", "lite-mono-8m"],
        help="Lite-Mono model variant that matches the weights.",
    )
    parser.add_argument(
        "--no_cuda",
        action="store_true",
        help="Force CPU inference even if CUDA is available.",
    )
    parser.add_argument(
        "--min_depth",
        type=float,
        default=0.1,
        help="Minimum depth used by Lite-Mono disp_to_depth conversion.",
    )
    parser.add_argument(
        "--max_depth",
        type=float,
        default=100.0,
        help="Maximum depth used by Lite-Mono disp_to_depth conversion.",
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

    model = None
    if args.run_model:
        model = load_lite_mono_model(
            weights_folder=args.weights_folder.resolve(),
            model_name=args.model,
            no_cuda=args.no_cuda,
            min_depth=args.min_depth,
            max_depth=args.max_depth,
        )

    print("Citrus Lite-Mono baseline evaluator")
    print(f"  Dataset workspace: {workspace_dir}")
    print(f"  Prepared dataset:  {prepared_dir}")
    print(f"  Split:             {args.split}")
    print(f"  Split samples:     {len(pairs)}")
    print(f"  Inspecting:        {len(selected_pairs)}")
    print(f"  Manifest rows:     {len(manifest)}")
    print(f"  Model inference:   {'enabled' if model is not None else 'disabled'}")
    if model is not None:
        print(f"  Weights folder:    {args.weights_folder.resolve()}")
        print(f"  Model variant:     {args.model}")
        print(f"  Device:            {model.device}")
        print(f"  Feed size:         width={model.feed_width}, height={model.feed_height}")
        print(f"  Depth range:       {model.min_depth}..{model.max_depth} m")

    for index, (rgb_rel, dense_rel) in enumerate(selected_pairs, start=1):
        inspect_sample(index, rgb_rel, dense_rel, manifest, workspace_dir, model)


if __name__ == "__main__":
    main()
