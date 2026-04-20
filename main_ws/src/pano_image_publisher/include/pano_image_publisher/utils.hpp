#pragma once

#include <algorithm>
#include <random>

#include <opencv2/opencv.hpp>
#include <sensor_msgs/msg/image.hpp>

namespace utils
{
    sensor_msgs::msg::Image cv_mat_to_image_msg(
        const cv::Mat &image,
        const std::string &encoding);

    void shuffle_images(std::vector<cv::Mat> &images);
}
