from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    teleop_node = Node(
        package='atlas_teleop',
        executable='atlas_teleop_node',
        name='atlas_teleop',
        output='screen',
    )

    return LaunchDescription([
        teleop_node,
    ])