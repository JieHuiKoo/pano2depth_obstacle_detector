from launch import LaunchDescription
from launch_ros.actions import Node

import os

cwd = os.getcwd()
parent = os.path.dirname(cwd)
data_path = os.path.join(parent, 'main_ws/src/pano_image_publisher/data/images')

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='pano_image_publisher',
            executable='pano_image_publisher_node',
            name='pano_image_publisher',
            output='screen',
            parameters=[
                {
                    'folder_path': data_path,
                    'publish_topic_name': '/pano/image_raw',
                    'publish_rate_in_hz': 0.1,
                    'loop': True,
                }
            ]
        )
    ])
