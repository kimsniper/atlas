import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration, TextSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():

    use_slam = LaunchConfiguration("use_slam")
    robot_ip = LaunchConfiguration("ip")
    cam_quality = LaunchConfiguration("cam_quality")
    robot_param = LaunchConfiguration("robot_param")

    use_slam_arg = DeclareLaunchArgument(
        "use_slam",
        default_value="false"
    )
    ip_launch_arg = DeclareLaunchArgument(
        "ip",
        default_value=TextSubstitution(text="192.168.254.101")
    )
    cam_quality_launch_arg = DeclareLaunchArgument(
        "cam_quality",
        default_value=TextSubstitution(text="7")
    )
    robot_param_launch_arg = DeclareLaunchArgument(
        "robot_param",
        default_value=TextSubstitution(text="")
    )

    hardware_interface = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory("atlas_hawkbot"),
                "launch",
                "bringup_launch.py"
            )
        ),
        launch_arguments={
            "ip": robot_ip,
            "cam_quality": cam_quality,
            "robot_param": robot_param,
        }.items(),
    )

    atlas_description_dir = get_package_share_directory("atlas_description")
    urdf_file = os.path.join(atlas_description_dir, "urdf", "atlas.urdf.xacro")

    robot_description = ParameterValue(
        Command(["xacro ", urdf_file, " is_sim:=false"]),
        value_type=str
    )

    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        output="screen",
        parameters=[{
            "robot_description": robot_description,
            "use_sim_time": False
        }]
    )

    localization = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory("atlas_localization"),
                "launch",
                "global_localization.launch.py"
            )
        ),
        condition=UnlessCondition(use_slam)
    )

    slam = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory("atlas_mapping"),
                "launch",
                "slam.launch.py"
            )
        ),
        condition=IfCondition(use_slam)
    )

    navigation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory("atlas_navigation"),
                "launch",
                "navigation.launch.py"
            )
        )
    )

    return LaunchDescription([
        use_slam_arg,
        ip_launch_arg,
        cam_quality_launch_arg,
        robot_param_launch_arg,
        hardware_interface,
        robot_state_publisher_node,
        localization,
        slam,
        navigation,
    ])