#pragma once

#include <rclcpp/rclcpp.hpp>                        // Ros2 C++ client library
#include <sensor_msgs/msg/image.hpp>                // ROS2 message type for images
#include <opencv2/opencv.hpp>                       // OpenCV for image processing

namespace pano_image_publisher {

class PublisherNode : public rclcpp::Node {

public:
    PublisherNode();

private:
    
};

} // namespace pano_image_publisher
