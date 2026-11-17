import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def launch_setup(context):
    mode = LaunchConfiguration("mode").perform(context)

    if mode == "simulation":
        launch_file = "simulated_robot.launch.py"
        launch_arguments = {
            "use_slam": LaunchConfiguration("use_slam"),
            "model": LaunchConfiguration("model"),
            "world_name": LaunchConfiguration("world_name"),
        }
    elif mode == "hardware":
        launch_file = "robot.launch.py"
        launch_arguments = {
            "use_slam": LaunchConfiguration("use_slam"),
            "ip": LaunchConfiguration("ip"),
            "cam_quality": LaunchConfiguration("cam_quality"),
            "robot_param": LaunchConfiguration("robot_param"),
        }
    else:
        raise RuntimeError(
            "Invalid mode '{}'. Expected 'simulation' or 'hardware'.".format(mode)
        )

    return [
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(
                    get_package_share_directory("atlas_bringup"),
                    "launch",
                    launch_file,
                )
            ),
            launch_arguments=launch_arguments.items(),
        )
    ]


def generate_launch_description():
    atlas_description = get_package_share_directory("atlas_description")

    return LaunchDescription([
        DeclareLaunchArgument(
            "mode",
            default_value="simulation",
            description="ATLAS operating mode: simulation or hardware",
        ),
        DeclareLaunchArgument(
            "use_slam",
            default_value="false",
        ),
        DeclareLaunchArgument(
            "model",
            default_value=os.path.join(
                atlas_description,
                "urdf",
                "atlas.urdf.xacro",
            ),
        ),
        DeclareLaunchArgument(
            "world_name",
            default_value="empty",
        ),
        DeclareLaunchArgument(
            "ip",
            default_value="192.168.254.101",
        ),
        DeclareLaunchArgument(
            "cam_quality",
            default_value="7",
        ),
        DeclareLaunchArgument(
            "robot_param",
            default_value="",
        ),
        OpaqueFunction(function=launch_setup),
    ])
