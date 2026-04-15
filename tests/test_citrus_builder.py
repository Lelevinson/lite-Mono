import importlib.util
import sys
import unittest
from pathlib import Path
from unittest import mock

import numpy as np


def _load_builder_module():
    repo_root = Path(__file__).resolve().parents[1]
    module_dir = repo_root / "datasets" / "citrus-farm-dataset"
    module_path = module_dir / "build_training_dataset.py"
    sys.path.insert(0, str(module_dir))
    spec = importlib.util.spec_from_file_location("build_training_dataset", module_path)
    module = importlib.util.module_from_spec(spec)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from: {module_path}")
    spec.loader.exec_module(module)
    return module


class BuilderPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.builder = _load_builder_module()

    def test_time_block_split_keeps_group_together(self):
        items = [
            {
                "rgb_rel": "rgb/zed_2023-07-18-14-26-49_0_bag_1000000000.png",
                "dense_rel": "dense/a.npz",
                "session": "0",
            },
            {
                "rgb_rel": "rgb/zed_2023-07-18-14-26-49_0_bag_1100000000.png",
                "dense_rel": "dense/b.npz",
                "session": "0",
            },
            {
                "rgb_rel": "rgb/zed_2023-07-18-14-26-49_0_bag_70000000000.png",
                "dense_rel": "dense/c.npz",
                "session": "0",
            },
            {
                "rgb_rel": "rgb/zed_2023-07-18-14-26-49_0_bag_130000000000.png",
                "dense_rel": "dense/d.npz",
                "session": "0",
            },
        ]

        split_map = self.builder.split_items(
            items,
            train_ratio=0.5,
            val_ratio=0.25,
            seed=1,
            strategy="time_block",
            time_block_sec=60.0,
        )

        group_to_split = {}
        for split_name, split_items in split_map.items():
            for index, item in enumerate(split_items):
                key = self.builder.split_group_key(
                    item, "time_block", index, time_block_sec=60.0
                )
                if key in group_to_split:
                    self.assertEqual(group_to_split[key], split_name)
                else:
                    group_to_split[key] = split_name

    def test_reused_dense_file_still_returns_manifest_row_and_mask(self):
        root = Path("repo")
        rgb_path = root / "zed_2023-07-18-14-26-49_0_bag_1000.png"
        dense_path = root / "dense_lidar_npz" / "sample.npz"
        mask_path = root / "dense_lidar_valid_mask_npz" / "sample.npz"
        rgb = np.zeros((2, 2, 3), dtype=np.uint8)
        dense = np.array([[1.0, 0.0], [2.0, 0.0]], dtype=np.float32)

        params = {
            "skip_existing": True,
            "min_dense_fill_ratio": 0.0,
            "zed_uint16_scale": 0.001,
            "transform_mode": "exact_lidar_parent_child_inverted",
        }
        with mock.patch.object(self.builder.cv2, "imread", return_value=rgb), \
            mock.patch.object(self.builder.os.path, "exists", return_value=True), \
            mock.patch.object(self.builder, "load_npz_array", return_value=dense), \
            mock.patch.object(self.builder, "save_valid_mask") as save_valid_mask:
            row = self.builder.process_single_sample(
                (
                    str(rgb_path),
                    str(root / "missing_lidar.npz"),
                    25,
                    str(dense_path),
                    str(mask_path),
                    None,
                    None,
                    None,
                    None,
                    params,
                    str(root),
                )
            )

            self.assertIsNotNone(row)
            self.assertTrue(row["reused_existing_dense"])
            self.assertEqual(
                row["transform_mode"], "exact_lidar_parent_child_inverted"
            )
            self.assertEqual(row["dense_fill_ratio"], 0.5)
            self.assertIsNone(row["sparse_fill_ratio"])
            save_valid_mask.assert_called_once()
            called_path, called_depth = save_valid_mask.call_args.args
            self.assertEqual(called_path, str(mask_path))
            np.testing.assert_array_equal(called_depth, dense)

    def test_zed_depth_metrics_compare_overlap(self):
        zed_path = "zed_depth.npz"
        dense = np.array([[1.0, 0.0], [3.0, 4.0]], dtype=np.float32)
        zed = np.array([[1.5, 2.0], [2.0, 4.5]], dtype=np.float32)
        with mock.patch.object(self.builder, "load_npz_array", return_value=zed):
            metrics = self.builder.compute_zed_depth_metrics(
                dense, zed_path, zed_delta_ns=1000000, zed_uint16_scale=0.001
            )

            self.assertEqual(metrics["zed_time_delta_ms"], 1.0)
            self.assertEqual(metrics["zed_lidar_overlap_ratio"], 0.75)
            self.assertEqual(metrics["zed_median_abs_diff_m"], 0.5)


if __name__ == "__main__":
    unittest.main()
