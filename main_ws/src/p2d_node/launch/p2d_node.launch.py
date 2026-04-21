from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='p2d_node',
            executable='p2d_node',
            name='p2d_node',
            parameters=[{
                'sub_image_topic': '/pano/image_raw'
            }]
        )
    ])
