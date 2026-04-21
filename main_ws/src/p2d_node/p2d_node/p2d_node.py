#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image

from ament_index_python.packages import get_package_share_directory
from .da360_loader import DA360Loader
import torch
import os

from cv_bridge import CvBridge
import cv2
import numpy as np

from sensor_msgs.msg import PointCloud2, PointField
from sensor_msgs_py import point_cloud2


class P2DNode(Node):
    def __init__(self):
        super().__init__('p2d_node')

        # Declare parameter for topic name
        self.declare_parameter('sub_image_topic', '/pano/image_raw')
        # self.declare_parameter('model_path', 'models/DA360_base.pth')
        # Load parameter
        image_topic = self.get_parameter('sub_image_topic').value
        # model_path = self.get_parameter('model_path').value

        share_dir = get_package_share_directory('p2d_node')
        model_path = os.path.join(share_dir, 'models', 'DA360_base.pth')

        self.get_logger().info(f"Subscribing to image topic: {image_topic}")

        # ======== Create subscriber/Publishers ========
        self.image_sub = self.create_subscription(
            Image,
            image_topic,
            self.image_callback,
            10
        )

        self.pc_pub = self.create_publisher(PointCloud2, '/pano/pointcloud', 10)
        # ================================

        # ======== Load Model ========
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Load DA360 model
        self.get_logger().info(f"Loading DA360 model from: {model_path}")
        self.da360 = DA360Loader(model_path, self.device)
        self.get_logger().info(
            f"DA360 loaded: {self.da360.height}x{self.da360.width}, device={self.device}"
        )
        # ===========================

        self.bridge = CvBridge()

    def image_callback(self, msg):
        # Convert ROS Image → OpenCV
        cv_img = self.bridge.imgmsg_to_cv2(msg, desired_encoding='rgb8')

        # Resize to model input size
        img = cv2.resize(cv_img, (self.da360.width, self.da360.height))
        img = img.astype(np.float32) / 255.0

        # Convert to tensor: [B, 3, H, W]
        tensor = torch.from_numpy(img).permute(2, 0, 1).unsqueeze(0).to(self.device)

        # Run inference
        with torch.no_grad():
            disp = self.da360.infer(tensor)   # [1, 1, H, W]

        disp_np = disp.squeeze().cpu().numpy()

        self.get_logger().info(
            f"Inference OK — disp min={disp_np.min():.4f}, max={disp_np.max():.4f}"
        )

        depth = 1.0 / (disp_np + 1e-6)  # Avoid division by zero

        # Convert to pointcloud
        points, fields = self.depth_to_pointcloud(depth, cv_img)

        # Create PointCloud2
        pc_msg = point_cloud2.create_cloud(msg.header, fields, points)

        # Publish
        self.pc_pub.publish(pc_msg)
        self.get_logger().info("Published pointcloud")

    def depth_to_pointcloud(self, depth, rgb=None, stride=2):
        # --- Downsample depth (and rgb) BEFORE computing angles ---
        depth = depth[::stride, ::stride]
        h, w = depth.shape

        if rgb is not None:
            rgb = rgb[::stride, ::stride]

        # --- Compute spherical angles ---
        Theta = np.pi - (np.arange(h).reshape(h, 1) + 0.5) * np.pi / h
        Theta = np.repeat(Theta, w, axis=1)

        Phi = (np.arange(w).reshape(1, w) + 0.5) * 2 * np.pi / w - np.pi
        Phi = np.repeat(Phi, h, axis=0)

        # --- Convert to XYZ ---
        X = (depth * np.sin(Theta) * np.sin(Phi)).flatten().astype(np.float32)
        Y = (depth * np.cos(Theta)).flatten().astype(np.float32)
        Z = (depth * np.sin(Theta) * np.cos(Phi)).flatten().astype(np.float32)

        # --- RGB or non-RGB case ---
        if rgb is not None:
            R = rgb[:, :, 0].flatten()
            G = rgb[:, :, 1].flatten()
            B = rgb[:, :, 2].flatten()

            rgb_uint32 = (
                (R.astype(np.uint32) << 16) |
                (G.astype(np.uint32) << 8) |
                B.astype(np.uint32)
            )

            # Structured dtype for ROS2
            dtype = np.dtype([
                ('x', np.float32),
                ('y', np.float32),
                ('z', np.float32),
                ('rgb', np.uint32),
            ])

            points = np.zeros(X.size, dtype=dtype)
            points['x'] = X
            points['y'] = Y
            points['z'] = Z
            points['rgb'] = rgb_uint32

            fields = [
                PointField(name='x', offset=0, datatype=PointField.FLOAT32, count=1),
                PointField(name='y', offset=4, datatype=PointField.FLOAT32, count=1),
                PointField(name='z', offset=8, datatype=PointField.FLOAT32, count=1),
                PointField(name='rgb', offset=12, datatype=PointField.UINT32, count=1),
            ]

        else:
            # XYZ only (simple float32 array)
            points = np.column_stack((X, Y, Z)).astype(np.float32)

            fields = [
                PointField(name='x', offset=0, datatype=PointField.FLOAT32, count=1),
                PointField(name='y', offset=4, datatype=PointField.FLOAT32, count=1),
                PointField(name='z', offset=8, datatype=PointField.FLOAT32, count=1),
            ]

        return points, fields



def main(args=None):
    rclpy.init(args=args)
    node = P2DNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
