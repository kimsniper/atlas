/*
 * Copyright 2026 Mezael Docoy
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     https://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#include <memory>

#include <geometry_msgs/msg/twist.hpp>
#include <geometry_msgs/msg/twist_stamped.hpp>
#include <rclcpp/rclcpp.hpp>

class TwistRelay : public rclcpp::Node
{
public:
  TwistRelay()
  : Node("twist_relay")
  {
    command_pub_ = create_publisher<geometry_msgs::msg::TwistStamped>(
      "/atlas_controller/cmd_vel",
      10);

    command_sub_ = create_subscription<geometry_msgs::msg::Twist>(
      "/cmd_vel",
      10,
      [this](const geometry_msgs::msg::Twist::SharedPtr message)
      {
        geometry_msgs::msg::TwistStamped stamped;
        stamped.header.stamp = get_clock()->now();
        stamped.twist = *message;
        command_pub_->publish(stamped);
      });
  }

private:
  rclcpp::Subscription<geometry_msgs::msg::Twist>::SharedPtr command_sub_;
  rclcpp::Publisher<geometry_msgs::msg::TwistStamped>::SharedPtr command_pub_;
};

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<TwistRelay>());
  rclcpp::shutdown();
  return 0;
}
