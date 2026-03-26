import numpy as np
import matplotlib.pyplot as plt

# Replace with the exact filename of ONE of your extracted LiDAR npz files
lidar_file = "extracted_lidar/velodyne_points/base_2023-07-18-14-44-35_2_bag_1689716895552198616.npz"


def verify_pointcloud(file_path):
    print("--- Verifying LiDAR Point Cloud ---")

    # Load the compressed numpy archive
    data = np.load(file_path)["arr_0"]

    print(f"Shape: {data.shape} | Data Type: {data.dtype}")
    print(f"Total laser hits captured: {len(data)}")

    # Extract the X, Y, Z coordinates
    x = data[:, 0]
    y = data[:, 1]
    z = data[:, 2]

    # Create a 3D interactive plot
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection="3d")

    # We skip every 2nd point ([::2]) just so matplotlib doesn't lag your computer
    scatter = ax.scatter(x[::2], y[::2], z[::2], c=z[::2], cmap="viridis", s=1)

    ax.set_title("Raw 3D LiDAR Point Cloud")
    ax.set_xlabel("X (Distance Forward)")
    ax.set_ylabel("Y (Distance Left/Right)")
    ax.set_zlabel("Z (Height)")

    # Lock the view to realistic physical distances (meters)
    ax.set_xlim([0, 15])  # Look 15 meters straight ahead
    ax.set_ylim([-8, 8])  # Look 8 meters left and right
    ax.set_zlim([-1, 3])  # Look from ground level up to 3 meters high

    plt.show()


if __name__ == "__main__":
    verify_pointcloud(lidar_file)
