# File: extract_lidar_from_raw.py
# Pure-Python script to safely extract 3D LiDAR point clouds

import argparse
import os
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader

# Strict topic filtering: extract only the LiDAR topic
LIDAR_TOPIC = "/velodyne_points"
ALLOWED_TOPICS = {LIDAR_TOPIC}


def decode_velodyne_pointcloud(msg):
    """Decode sensor_msgs/PointCloud2 raw bytes into an Nx4 numpy array (X, Y, Z, Intensity)."""
    # Calculate total number of points
    num_points = msg.width * msg.height

    # Read the raw byte array and reshape it so each row is one point (point_step is usually 32 bytes)
    raw_data = np.frombuffer(bytes(msg.data), dtype=np.uint8).reshape(
        num_points, msg.point_step
    )

    # Dynamically find the byte offsets for X, Y, Z, and Intensity from the message metadata
    try:
        x_off = next(f.offset for f in msg.fields if f.name == "x")
        y_off = next(f.offset for f in msg.fields if f.name == "y")
        z_off = next(f.offset for f in msg.fields if f.name == "z")
        i_off = next(f.offset for f in msg.fields if f.name == "intensity")
    except StopIteration:
        raise RuntimeError(
            "PointCloud2 message is missing standard x, y, z, or intensity fields."
        )

    # Slice the exact 4 bytes for each float and convert them into float32 arrays
    x = raw_data[:, x_off : x_off + 4].copy().view(np.float32).flatten()
    y = raw_data[:, y_off : y_off + 4].copy().view(np.float32).flatten()
    z = raw_data[:, z_off : z_off + 4].copy().view(np.float32).flatten()
    intensity = raw_data[:, i_off : i_off + 4].copy().view(np.float32).flatten()

    # Stack them into a clean (N, 4) matrix
    cloud = np.column_stack((x, y, z, intensity))

    # Clean the data: Remove points where the laser shot into the sky and returned NaN
    valid_mask = ~np.isnan(cloud[:, 0])
    return cloud[valid_mask]


def write_pointcloud_npz(msg, output_filepath):
    """Save the 3D point cloud array directly to a compressed npz file."""
    cloud_array = decode_velodyne_pointcloud(msg)
    # Save the Nx4 array as 'arr_0' inside the zip
    np.savez_compressed(f"{output_filepath}.npz", arr_0=cloud_array)


def output_path(output_folder, bag_name, topic, timestamp_ns):
    topic_folder = os.path.join(output_folder, topic.replace("/", "_").strip("_"))
    os.makedirs(topic_folder, exist_ok=True)
    filename_prefix = bag_name.replace(".", "_")
    output_filename = f"{filename_prefix}_{timestamp_ns}"
    return os.path.join(topic_folder, output_filename)


def extract_data_from_bag(bag_path, output_folder):
    with AnyReader([Path(bag_path)]) as reader:
        connections = [
            conn for conn in reader.connections if conn.topic in ALLOWED_TOPICS
        ]

        if not connections:
            print(f"No LiDAR topics found in {os.path.basename(bag_path)}")
            return

        for connection, timestamp_ns, rawdata in reader.messages(
            connections=connections
        ):
            msg = reader.deserialize(rawdata, connection.msgtype)
            out = output_path(
                output_folder,
                os.path.basename(bag_path),
                connection.topic,
                timestamp_ns,
            )

            if connection.topic == LIDAR_TOPIC:
                write_pointcloud_npz(msg, out)


def filter_rosbags(src_folder, prefixes_of_interest):
    rosbags_of_interest = []
    for filename in os.listdir(src_folder):
        for prefix in prefixes_of_interest:
            if filename.startswith(prefix):
                rosbags_of_interest.append(filename)
                break
    return rosbags_of_interest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract LiDAR from rosbags.")
    parser.add_argument("src_folder", help="Source folder containing rosbags")
    parser.add_argument("output_folder", help="Output folder to save extracted data")
    args = parser.parse_args()

    # We only care about the files starting with 'base' (where the LiDAR is stored)
    rosbag_prefixes_of_interest = ["base"]
    rosbags_to_process = filter_rosbags(args.src_folder, rosbag_prefixes_of_interest)
    rosbags_to_process.sort()

    print("Found the following LiDAR bags to process:")
    for bag in rosbags_to_process:
        print(f"  {bag}")

    for bag_name in rosbags_to_process:
        bag_path = os.path.join(args.src_folder, bag_name)
        extract_data_from_bag(bag_path, args.output_folder)
