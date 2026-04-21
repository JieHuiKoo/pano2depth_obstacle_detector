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

from tf2_ros import Buffer, TransformListener
import tf_transformations

class P2DNode(Node):
    def __init__(self):
        super().__init__('p2d_node')

        # ==== Parameter declaration and loading ====
        # Declare
        self.declare_parameter('scale'              , 60.0)
        self.declare_parameter('stride'             , 2)
        self.declare_parameter('ground_thresh_deg'  , 40.0)
        self.declare_parameter('overhead_thresh_deg', 140.0)
        self.declare_parameter('sub_image_topic'    , '/pano/image_raw')
        self.declare_parameter('model_size'         , 'base')
        self.declare_parameter('pub_ground_topic'   , '/pano/pointcloud/ground')
        self.declare_parameter('pub_obstacle_topic' , '/pano/pointcloud/obstacle')
        self.declare_parameter('pub_overhead_topic' , '/pano/pointcloud/overhead')
        self.declare_parameter('output_frame'       , 'base_link')

        # Load
        self.scale               = self.get_parameter('scale'                ).value
        self.stride              = self.get_parameter('stride'               ).value
        self.ground_thresh_deg   = self.get_parameter('ground_thresh_deg'    ).value
        self.overhead_thresh_deg = self.get_parameter('overhead_thresh_deg'  ).value
        self.image_topic         = self.get_parameter('sub_image_topic'      ).value
        self.model_size          = self.get_parameter('model_size'           ).value
        self.ground_topic        = self.get_parameter('pub_ground_topic'     ).value
        self.obstacle_topic      = self.get_parameter('pub_obstacle_topic'   ).value
        self.overhead_topic      = self.get_parameter('pub_overhead_topic'   ).value
        self.output_frame        = self.get_parameter('output_frame'         ).value

        # Print out all loaded parameters
        self.get_logger().info(f"Parameters loaded:")
        self.get_logger().info(f"  scale: {self.scale}")
        self.get_logger().info(f"  stride: {self.stride}")
        self.get_logger().info(f"  ground_thresh_deg: {self.ground_thresh_deg}") 
        self.get_logger().info(f"  overhead_thresh_deg: {self.overhead_thresh_deg}")
        self.get_logger().info(f"  sub_image_topic: {self.image_topic}")
        self.get_logger().info(f"  model_size: {self.model_size}")
        self.get_logger().info(f"  pub_ground_topic: {self.ground_topic}")
        self.get_logger().info(f"  pub_obstacle_topic: {self.obstacle_topic}")
        self.get_logger().info(f"  pub_overhead_topic: {self.overhead_topic}")
        self.get_logger().info(f"  output_frame: {self.output_frame}")

        # Initialise
        share_dir = get_package_share_directory('p2d_node')
        model_path = os.path.join(share_dir, 'models', f'DA360_{self.model_size}.pth')
        self.is_tf_obtained = False
        self.should_transform = False
        self.tf_to_transform_to = None
        # ================================

        # ======== Create subscriber/Publishers ========
        self.get_logger().info(f"Subscribing to image topic: {self.image_topic}")
        self.image_sub = self.create_subscription(
            Image,
            self.image_topic,
            self.image_callback,
            10
        )

        self.pc_ground_pub      = self.create_publisher(PointCloud2, self.ground_topic        , 10)
        self.pc_obs_pub         = self.create_publisher(PointCloud2, self.obstacle_topic      , 10)
        self.pc_overhead_pub    = self.create_publisher(PointCloud2, self.overhead_topic      , 10)

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

        # For openCV
        self.bridge = CvBridge()

        # Set up TF listener
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

    def get_static_transform(self, target_frame, source_frame):
        try:
            if target_frame == source_frame:
                self.is_tf_obtained = True
                self.should_transform = False
                return None  # No transform needed

            tf = self.tf_buffer.lookup_transform(
                target_frame,
                source_frame,
                rclpy.time.Time(),
            )
            self.should_transform = True
            self.is_tf_obtained = True
            return tf
        except Exception as e:
            self.get_logger().error(f"TF lookup failed: {e}")
            return None

    def image_callback(self, msg):
        # Convert ROS Image → OpenCV
        cv_img = self.bridge.imgmsg_to_cv2(msg, desired_encoding='rgb8')

        frame = msg.header.frame_id

        if self.output_frame == frame:
            self.should_transform = False

        if self.should_transform and not self.is_tf_obtained:
            self.tf_to_transform_to = self.get_static_transform(self.output_frame, frame)
            if not self.tf_to_transform_to:
                self.get_logger().error("Failed to obtain static transform")
                return

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
        points_ground, points_obstacle, points_overhead, fields = self.depth_to_pointcloud(
            depth,
            cv_img,
            stride=self.stride,
            scale=self.scale,
            ground_thresh_deg=self.ground_thresh_deg,
            overhead_thresh_deg=self.overhead_thresh_deg,
            should_transform=self.should_transform,
        )

        # Create PointCloud2
        pc_ground_msg = point_cloud2.create_cloud(msg.header, fields, points_ground)
        pc_obstacle_msg = point_cloud2.create_cloud(msg.header, fields, points_obstacle)
        pc_overhead_msg = point_cloud2.create_cloud(msg.header, fields, points_overhead)

        # Publish
        self.pc_ground_pub.publish(pc_ground_msg)
        self.pc_obs_pub.publish(pc_obstacle_msg)
        self.pc_overhead_pub.publish(pc_overhead_msg)
        self.get_logger().info("Published pointclouds")

    def transform_cloud(self, Xf, Yf, Zf):
        """
        Transform a full point cloud using self.tf_to_transform.
        Xf, Yf, Zf are 1D numpy arrays of equal length.
        Returns transformed Xf, Yf, Zf.
        """
        if self.tf_to_transform is None:
            return Xf, Yf, Zf

        # Extract translation
        t = self.tf_to_transform.transform.translation
        tx, ty, tz = t.x, t.y, t.z

        # Extract rotation quaternion
        q = self.tf_to_transform.transform.rotation
        qx, qy, qz, qw = q.x, q.y, q.z, q.w

        # Build 4x4 transform matrix
        T = tf_transformations.quaternion_matrix([qx, qy, qz, qw])
        T[0, 3] = tx
        T[1, 3] = ty
        T[2, 3] = tz

        # Build homogeneous Nx4 matrix
        xyz = np.vstack([Xf, Yf, Zf, np.ones_like(Xf)])

        # Apply transform
        xyz_tf = T @ xyz

        # Extract transformed coordinates
        return xyz_tf[0], xyz_tf[1], xyz_tf[2]


    def depth_to_pointcloud(
        self,
        depth, 
        rgb=None, 
        stride=2, 
        scale=60.0,
        ground_thresh_deg=40.0,
        overhead_thresh_deg=140.0,
        should_transform=False,
        ):
        # --- Downsample depth (and rgb) BEFORE computing angles ---
        depth = depth[::stride, ::stride] * scale
        h, w = depth.shape

        if rgb is not None:
            rgb = rgb[::stride, ::stride]

        # --- Compute spherical angles ---
        Theta = np.pi - (np.arange(h).reshape(h, 1) + 0.5) * np.pi / h
        Theta = np.repeat(Theta, w, axis=1)

        Phi = (np.arange(w).reshape(1, w) + 0.5) * 2 * np.pi / w - np.pi
        Phi = np.repeat(Phi, h, axis=0)

        # --- Convert to XYZ ---
        X = (depth * np.sin(Theta) * np.sin(Phi)).astype(np.float32)
        Y = (depth * np.cos(Theta)).astype(np.float32)
        Z = (depth * np.sin(Theta) * np.cos(Phi)).astype(np.float32)

        # --- Flatten everything ---
        Xf = X.flatten()
        Yf = Y.flatten()
        Zf = Z.flatten()
        Theta_f = Theta.flatten()

        # --- Classification thresholds ---
        # Convert degrees to radians
        ground_thresh   = np.deg2rad(40)     # downward
        overhead_thresh = np.deg2rad(140)    # upward

        ground_mask   = Theta_f < ground_thresh
        overhead_mask = Theta_f > overhead_thresh
        obstacle_mask = ~(ground_mask | overhead_mask)

        # Transform the pointcloud. We transform the whole pointcloud at once
        if should_transform and self.tf_to_transform is not None:
            Xf, Yf, Zf = self.transform_cloud(Xf, Yf, Zf)

        # --- RGB handling ---
        if rgb is not None:
            R = rgb[:, :, 0].flatten().astype(np.uint32)
            G = rgb[:, :, 1].flatten().astype(np.uint32)
            B = rgb[:, :, 2].flatten().astype(np.uint32)

            rgb_uint32 = (R << 16) | (G << 8) | B

            dtype = np.dtype([
                ('x', np.float32),
                ('y', np.float32),
                ('z', np.float32),
                ('rgb', np.uint32),
            ])

            def make_structured(mask):
                pts = np.zeros(mask.sum(), dtype=dtype)
                pts['x'] = Xf[mask]
                pts['y'] = Yf[mask]
                pts['z'] = Zf[mask]
                pts['rgb'] = rgb_uint32[mask]
                return pts

            ground_pts   = make_structured(ground_mask)
            obstacle_pts = make_structured(obstacle_mask)
            overhead_pts = make_structured(overhead_mask)

            fields = [
                PointField(name='x', offset=0, datatype=PointField.FLOAT32, count=1),
                PointField(name='y', offset=4, datatype=PointField.FLOAT32, count=1),
                PointField(name='z', offset=8, datatype=PointField.FLOAT32, count=1),
                PointField(name='rgb', offset=12, datatype=PointField.UINT32, count=1),
            ]

        else:
            # XYZ only
            def make_xyz(mask):
                return np.column_stack((Xf[mask], Yf[mask], Zf[mask])).astype(np.float32)

            ground_pts   = make_xyz(ground_mask)
            obstacle_pts = make_xyz(obstacle_mask)
            overhead_pts = make_xyz(overhead_mask)

            fields = [
                PointField(name='x', offset=0, datatype=PointField.FLOAT32, count=1),
                PointField(name='y', offset=4, datatype=PointField.FLOAT32, count=1),
                PointField(name='z', offset=8, datatype=PointField.FLOAT32, count=1),
            ]

        return ground_pts, obstacle_pts, overhead_pts, fields


def main(args=None):
    rclpy.init(args=args)
    node = P2DNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
