#include <memory>

#include "nav_msgs/msg/odometry.hpp"
#include "rclcpp/rclcpp.hpp"

class OdomRepublisher : public rclcpp::Node
{
public:
    OdomRepublisher() : Node("odom_republisher")
    {
        publisher_ = create_publisher<nav_msgs::msg::Odometry>("/atlas_controller/odom", 10);

        subscription_ = create_subscription<nav_msgs::msg::Odometry>(
            "/odom", 10, std::bind(&OdomRepublisher::odom_callback, this, std::placeholders::_1));
    }

private:
    void odom_callback(const nav_msgs::msg::Odometry::SharedPtr msg)
    {
        msg->header.frame_id = "odom";
        msg->child_frame_id = "base_footprint";
        publisher_->publish(*msg);
    }

    rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr subscription_;
    rclcpp::Publisher<nav_msgs::msg::Odometry>::SharedPtr publisher_;
};

int main(int argc, char *argv[])
{
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<OdomRepublisher>());
    rclcpp::shutdown();
    return 0;
}