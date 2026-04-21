#pragma once

#include <rclcpp/rclcpp.hpp>                        // Ros2 C++ client library
#include <sensor_msgs/msg/image.hpp>                // ROS2 message type for images
#include <opencv2/opencv.hpp>                       // OpenCV for image processing

#include "pano_image_publisher/image_loader.hpp"    // Custom image loader class
#include "pano_image_publisher/utils.hpp"           // Utility functions

namespace pano_image_publisher {

class PublisherNode : public rclcpp::Node {

public:
  PublisherNode();

private:
  
  // Methods
  void declare_parameters();
  void load_parameters();
  void start_timer();
  void publish_image();
  void load_images();
  void setup_publisher();

  
  // Params
  std::string folder_path_;
  std::string publish_topic_name_;
  float publish_rate_in_hz_;
  bool loop_;
  bool shuffle_;

  // Timer
  rclcpp::TimerBase::SharedPtr timer_;

  // Publisher
  rclcpp::Publisher<sensor_msgs::msg::Image>::SharedPtr publisher_;

  // Image Variables
  std::vector<cv::Mat> images_;
  size_t current_image_idx_ = 0;
  ImageLoader image_loader_;
};

} // namespace pano_image_publisher
