import os
from os import pathsep
from pathlib import Path
from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution, PythonExpression
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    atlas_description = get_package_share_directory("atlas_description")
    atlas_bringup = get_package_share_directory("atlas_bringup")
    pkg_ros_gz_sim = get_package_share_directory("ros_gz_sim")

    model_arg = DeclareLaunchArgument(
        name="model",
        default_value=os.path.join(atlas_description, "urdf", "atlas_sim.urdf.xacro"),
        description="Absolute path to robot urdf xacro file"
    )

    world_name_arg = DeclareLaunchArgument(
        name="world_name",
        default_value="empty",
        description="Gazebo world name"
    )

    world_path = PathJoinSubstitution([
        atlas_description,
        "worlds",
        PythonExpression(["'", LaunchConfiguration("world_name"), "' + '.world'"])
    ])

    model_path = str(Path(atlas_description).parent.resolve())
    model_path += pathsep + os.path.join(atlas_description, "meshes")
    model_path += pathsep + str(Path(atlas_bringup).parent.resolve())

    gazebo_resource_path = SetEnvironmentVariable(
        "GZ_SIM_RESOURCE_PATH",
        model_path
    )

    robot_description = ParameterValue(
        Command(["xacro ", LaunchConfiguration("model"), " is_sim:=true"]),
        value_type=str
    )

    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[{
            "robot_description": robot_description,
            "use_sim_time": True
        }]
    )

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, "launch", "gz_sim.launch.py")
        ),
        launch_arguments={
            "gz_args": PythonExpression(["'", world_path, " -v 4 -r'"])
        }.items()
    )

    gz_spawn_entity = Node(
        package="ros_gz_sim",
        executable="create",
        output="screen",
        arguments=[
            "-topic", "robot_description",
            "-name", "atlas",
            "-z", "0.05"  # Slightly elevated spawn position to prevent ground clip on load
        ],
    )

    gz_ros2_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        output="screen",
        arguments=[
            "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock",
            "/imu@sensor_msgs/msg/Imu[gz.msgs.IMU",
            "/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan"
        ],
        remappings=[
            ('/imu', '/imu/out'),
        ]
    )

    return LaunchDescription([
        model_arg,
        world_name_arg,
        gazebo_resource_path,
        robot_state_publisher_node,
        gazebo,
        gz_spawn_entity,
        gz_ros2_bridge
    ])