#pragma once

#include <rclcpp/rclcpp.hpp>                        // Ros2 C++ client library
#include <sensor_msgs/msg/image.hpp>                // ROS2 message type for images
#include <opencv2/opencv.hpp>                       // OpenCV for image processing

namespace pano_image_publisher {

class PublisherNode : public rclcpp::Node {

public:
  PublisherNode();

private:
  
  // Methods
  void declare_parameters();
  void load_parameters();
  
  // Params
  std::string folder_path_;
  std::string topic_name_;
  int publish_rate_in_hz_;
  bool loop_;
  bool shuffle_;
};

} // namespace pano_image_publisher
