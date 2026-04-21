from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():

    # --- Paths to packages ---
    p2d_pkg = get_package_share_directory('p2d_node')
    pano_pkg = get_package_share_directory('pano_image_publisher')

    # --- Launch: static TF ---
    static_tf_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(p2d_pkg, 'launch', 'static_tf.launch.py')
        )
    )

    # --- Launch: p2d_node ---
    p2d_node_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(p2d_pkg, 'launch', 'p2d_node.launch.py')
        )
    )

    # --- Launch: pano image publisher ---
    pano_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pano_pkg, 'launch', 'pano_image_publisher.launch.py')
        )
    )

    # --- RViz2 with config ---
    rviz_config = os.path.join(p2d_pkg, 'visualisation', 'pointcloud_visualisation.rviz')

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config]
    )

    return LaunchDescription([
        static_tf_launch,
        p2d_node_launch,
        pano_launch,
        rviz
    ])
