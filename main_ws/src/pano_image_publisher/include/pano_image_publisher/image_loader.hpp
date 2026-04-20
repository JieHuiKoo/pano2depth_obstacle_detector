#pragma once

#include <string>
#include <vector>
#include <opencv2/opencv.hpp>
#include <filesystem>
#include <iostream>

#include <rclcpp/rclcpp.hpp>                        // Ros2 C++ client library

namespace pano_image_publisher {

class ImageLoader {
  public:
    explicit ImageLoader(rclcpp::Logger logger)
      : logger_(logger) {}
    std::vector<cv::Mat> load_images( const std::string &folder_path);

  private:
    bool is_supported_file(const std::string& file_path);
    rclcpp::Logger logger_;
};
} // namespace pano_image_publisher