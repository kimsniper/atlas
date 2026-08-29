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

#include <algorithm>
#include <chrono>
#include <memory>

#include <geometry_msgs/msg/twist.hpp>
#include <rclcpp/rclcpp.hpp>

#include <fcntl.h>
#include <termios.h>
#include <unistd.h>

using namespace std::chrono_literals;

class AtlasTeleop : public rclcpp::Node
{
public:
    AtlasTeleop()
        : Node("atlas_teleop"), linear_speed_(0.15), angular_speed_(1.0), terminal_restored_(false)
    {
        cmd_vel_pub_ = this->create_publisher<geometry_msgs::msg::Twist>("cmd_vel", 10);

        original_terminal_settings_ = get_terminal_settings();
        original_terminal_flags_ = fcntl(STDIN_FILENO, F_GETFL, 0);

        set_terminal_raw();

        RCLCPP_INFO(this->get_logger(), "ATLAS Keyboard Teleop");
        RCLCPP_INFO(this->get_logger(), "----------------------");
        RCLCPP_INFO(this->get_logger(), "w : forward");
        RCLCPP_INFO(this->get_logger(), "s : backward");
        RCLCPP_INFO(this->get_logger(), "a : rotate left");
        RCLCPP_INFO(this->get_logger(), "d : rotate right");
        RCLCPP_INFO(this->get_logger(), "q : forward + left");
        RCLCPP_INFO(this->get_logger(), "e : forward + right");
        RCLCPP_INFO(this->get_logger(), "z : backward + left");
        RCLCPP_INFO(this->get_logger(), "c : backward + right");
        RCLCPP_INFO(this->get_logger(), "x : stop");
        RCLCPP_INFO(this->get_logger(), "r/f : increase/decrease linear speed");
        RCLCPP_INFO(this->get_logger(), "t/g : increase/decrease angular speed");
        RCLCPP_INFO(this->get_logger(), "CTRL-C : exit");

        timer_ = this->create_wall_timer(50ms, std::bind(&AtlasTeleop::update, this));
    }

    ~AtlasTeleop() { shutdown(); }

    void shutdown()
    {
        if (terminal_restored_)
        {
            return;
        }

        publish_stop();
        restore_terminal();

        terminal_restored_ = true;
    }

private:
    struct termios get_terminal_settings()
    {
        struct termios settings
        {
        };
        tcgetattr(STDIN_FILENO, &settings);
        return settings;
    }

    void set_terminal_raw()
    {
        struct termios raw = original_terminal_settings_;

        raw.c_lflag &= ~(ICANON | ECHO);
        raw.c_cc[VMIN] = 0;
        raw.c_cc[VTIME] = 0;

        tcsetattr(STDIN_FILENO, TCSANOW, &raw);

        fcntl(STDIN_FILENO, F_SETFL, original_terminal_flags_ | O_NONBLOCK);
    }

    void restore_terminal()
    {
        tcsetattr(STDIN_FILENO, TCSANOW, &original_terminal_settings_);

        fcntl(STDIN_FILENO, F_SETFL, original_terminal_flags_);

        tcflush(STDIN_FILENO, TCIFLUSH);
    }

    char read_key()
    {
        char key = 0;

        if (read(STDIN_FILENO, &key, 1) > 0)
        {
            return key;
        }

        return 0;
    }

    void update()
    {
        char key = read_key();

        if (key == 0)
        {
            return;
        }

        geometry_msgs::msg::Twist twist;

        switch (key)
        {
        case 'w':
            twist.linear.x = linear_speed_;
            break;

        case 's':
            twist.linear.x = -linear_speed_;
            break;

        case 'a':
            twist.angular.z = angular_speed_;
            break;

        case 'd':
            twist.angular.z = -angular_speed_;
            break;

        case 'q':
            twist.linear.x = linear_speed_;
            twist.angular.z = angular_speed_;
            break;

        case 'e':
            twist.linear.x = linear_speed_;
            twist.angular.z = -angular_speed_;
            break;

        case 'z':
            twist.linear.x = -linear_speed_;
            twist.angular.z = angular_speed_;
            break;

        case 'c':
            twist.linear.x = -linear_speed_;
            twist.angular.z = -angular_speed_;
            break;

        case 'x':
            break;

        case 'r':
            linear_speed_ += 0.05;
            RCLCPP_INFO(this->get_logger(), "Linear speed: %.2f m/s", linear_speed_);
            return;

        case 'f':
            linear_speed_ = std::max(0.05, linear_speed_ - 0.05);
            RCLCPP_INFO(this->get_logger(), "Linear speed: %.2f m/s", linear_speed_);
            return;

        case 't':
            angular_speed_ += 0.1;
            RCLCPP_INFO(this->get_logger(), "Angular speed: %.2f rad/s", angular_speed_);
            return;

        case 'g':
            angular_speed_ = std::max(0.1, angular_speed_ - 0.1);
            RCLCPP_INFO(this->get_logger(), "Angular speed: %.2f rad/s", angular_speed_);
            return;

        default:
            return;
        }

        cmd_vel_pub_->publish(twist);
    }

    void publish_stop()
    {
        geometry_msgs::msg::Twist stop;
        cmd_vel_pub_->publish(stop);
    }

    rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr cmd_vel_pub_;
    rclcpp::TimerBase::SharedPtr timer_;

    struct termios original_terminal_settings_;
    int original_terminal_flags_;

    double linear_speed_;
    double angular_speed_;
    bool terminal_restored_;
};

int main(int argc, char *argv[])
{
    rclcpp::init(argc, argv);

    auto node = std::make_shared<AtlasTeleop>();

    rclcpp::spin(node);

    node->shutdown();

    node.reset();

    rclcpp::shutdown();

    return 0;
}