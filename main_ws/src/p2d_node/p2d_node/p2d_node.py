#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image


class P2DNode(Node):
    def __init__(self):
        super().__init__('p2d_node')

        # Declare parameter for topic name
        self.declare_parameter('sub_image_topic', '/pano/image_raw')
        
        # Load parameter
        image_topic = self.get_parameter('sub_image_topic').value

        self.get_logger().info(f"Subscribing to image topic: {image_topic}")

        # Create subscriber
        self.image_sub = self.create_subscription(
            Image,
            image_topic,
            self.image_callback,
            10
        )

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
