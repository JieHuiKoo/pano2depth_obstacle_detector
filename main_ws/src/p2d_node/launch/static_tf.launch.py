from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():

    return LaunchDescription([
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='base_to_camera_tf',
            output='screen',
            arguments=[
                # Translation (x y z)
                '0.0', '0.0', '1.2',
                # Rotation (roll pitch yaw) in radians
                '0.0', '3.14', '1.57',
                # Parent frame, Child frame
                'base_link', 'camera'
            ]
        )
    ])
