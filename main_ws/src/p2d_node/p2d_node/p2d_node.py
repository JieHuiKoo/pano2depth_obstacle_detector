#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image

from ament_index_python.packages import get_package_share_directory
from .da360_loader import DA360Loader
import torch
import os

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

        # ======== Create subscriber ========
        self.image_sub = self.create_subscription(
            Image,
            image_topic,
            self.image_callback,
            10
        )
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

    def image_callback(self, msg):
        self.get_logger().info(
            f"Received image: {msg.width}x{msg.height}, encoding={msg.encoding}"
        )


def main(args=None):
    rclpy.init(args=args)
    node = P2DNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
