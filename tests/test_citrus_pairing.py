import importlib.util
import math
import unittest
from pathlib import Path

import numpy as np


def _load_densify_module():
    repo_root = Path(__file__).resolve().parents[1]
    module_path = repo_root / "datasets" / "citrus-farm-dataset" / "densify_lidar.py"
    spec = importlib.util.spec_from_file_location("densify_lidar", module_path)
    module = importlib.util.module_from_spec(spec)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from: {module_path}")
    spec.loader.exec_module(module)
    return module


class PairingPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dld = _load_densify_module()

    def test_find_closest_optimized_falls_back_to_any_session(self):
        lidar_map = [
            (900, "base_2023-07-18-14-26-48_0_bag_900.npz", "0"),
            (1020, "base_2023-07-18-14-26-48_0_bag_1020.npz", "0"),
        ]

        best_file, delta_ns = self.dld.find_closest_optimized(
            target_time=1000,
            target_session="1",
            lidar_map=lidar_map,
            require_same_session=True,
            max_delta_ns=50,
            fallback_to_any_session=True,
        )

        self.assertEqual(best_file, "base_2023-07-18-14-26-48_0_bag_1020.npz")
        self.assertEqual(delta_ns, 20)

    def test_find_closest_optimized_strict_same_session_can_return_none(self):
        lidar_map = [
            (900, "base_2023-07-18-14-26-48_0_bag_900.npz", "0"),
            (1020, "base_2023-07-18-14-26-48_0_bag_1020.npz", "0"),
        ]

        best_file, delta_ns = self.dld.find_closest_optimized(
            target_time=1000,
            target_session="1",
            lidar_map=lidar_map,
            require_same_session=True,
            max_delta_ns=50,
            fallback_to_any_session=False,
        )

        self.assertIsNone(best_file)
        self.assertTrue(math.isinf(delta_ns))

    def test_find_closest_lidar_prefers_same_session_but_can_fallback(self):
        rgb_path = "zed_2023-07-18-14-26-49_1_bag_1000.png"
        lidar_files = [
            "base_2023-07-18-14-26-48_0_bag_900.npz",
            "base_2023-07-18-14-26-48_0_bag_1020.npz",
        ]

        best_file, delta_ns = self.dld.find_closest_lidar(
            rgb_path,
            lidar_files=lidar_files,
            require_same_session=True,
            max_delta_ns=50,
            fallback_to_any_session=True,
        )

        self.assertEqual(best_file, "base_2023-07-18-14-26-48_0_bag_1020.npz")
        self.assertEqual(delta_ns, 20)

    def test_transform_modes_are_available_and_distinct(self):
        prod_rvec, prod_tvec = self.dld.get_lidar_to_zed_transform(
            "production_current"
        )
        exact_rvec, exact_tvec = self.dld.get_lidar_to_zed_transform(
            "exact_lidar_parent_child_inverted"
        )

        self.assertEqual(prod_rvec.shape, (3, 1))
        self.assertEqual(exact_rvec.shape, (3, 1))
        self.assertEqual(prod_tvec.shape, (3,))
        self.assertEqual(exact_tvec.shape, (3,))
        self.assertFalse(np.allclose(prod_tvec, exact_tvec))

        with self.assertRaises(ValueError):
            self.dld.get_lidar_to_zed_transform("not_a_real_mode")


if __name__ == "__main__":
    unittest.main()
