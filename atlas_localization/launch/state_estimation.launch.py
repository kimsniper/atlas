from launch import LaunchDescription
from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node
import os

def generate_launch_description():

    static_transform_publisher = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        arguments=["--x", "0", "--y", "0","--z", "0.103",
                   "--qx", "1", "--qy", "0", "--qz", "0", "--qw", "0",
                   "--frame-id", "base_footprint",
                   "--child-frame-id", "imu_link"],
    )

    robot_localization = Node(
        package="robot_localization",
        executable="ekf_node",
        name="ekf_filter_node",
        output="screen",
        parameters=[os.path.join(get_package_share_directory("atlas_localization"), "config", "ekf.yaml")],
    )

    imu_filter = Node(
        package="imu_complementary_filter",
        executable="complementary_filter_node",
        name="complementary_filter_gain_node",
        output="screen",
        parameters=[
            {
                "do_bias_estimation": True,
                "do_adaptive_gain": True,
                "bias_alpha": 0.01,
                "use_mag": False,
                "gain_acc": 0.01,
                "gain_mag": 0.01,
                "publish_tf": False,
                "fixed_frame": "odom",
                "reverse_tf": False,
                "constant_dt": 0.0,
                "orientation_stddev": 0.0,
            }
        ],
        remappings=[
            ("imu/data_raw", "/imu/data_raw"),
            ("imu/data", "/imu/data"),
        ],
    )

    odom_republisher = Node(
        package="atlas_localization",
        executable="odom_republisher",
        output="screen",
    )
    return LaunchDescription([
        static_transform_publisher,
        imu_filter,
        robot_localization,
        odom_republisher,
    ])
