import os
from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, LaunchConfiguration

from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    atlas_description = get_package_share_directory("atlas_description")

    model_arg = DeclareLaunchArgument(
        name="model",
        default_value=os.path.join(atlas_description, "urdf", "atlas.urdf.xacro"),
        description="Absolute path to robot urdf xacro file"
    )

    rviz_config_arg = DeclareLaunchArgument(
        name="rvizconfig",
        default_value=os.path.join(atlas_description, "rviz", "config.rviz"),
        description="Absolute path to rviz config file"
    )

    robot_description = ParameterValue(
        Command(["xacro ", LaunchConfiguration("model")]),
        value_type=str
    )

    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[{"robot_description": robot_description}]
    )

    joint_state_publisher_gui_node = Node(
        package="joint_state_publisher_gui",
        executable="joint_state_publisher_gui",
        output="screen"
    )

    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="screen",
        arguments=["-d", LaunchConfiguration("rvizconfig")],
    )

    return LaunchDescription([
        model_arg,
        rviz_config_arg,
        joint_state_publisher_gui_node,
        robot_state_publisher_node,
        rviz_node
    ])