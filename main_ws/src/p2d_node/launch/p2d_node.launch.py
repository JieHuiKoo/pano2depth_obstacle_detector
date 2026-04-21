from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():

    pkg_dir = get_package_share_directory('p2d_node')
    params_file = os.path.join(pkg_dir, 'config', 'params.yaml')

    return LaunchDescription([
        Node(
            package='p2d_node',
            executable='p2d_node',
            name='p2d_node',
            parameters=[params_file]
        )
    ])
