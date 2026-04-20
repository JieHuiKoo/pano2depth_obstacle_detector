#include "pano_image_publisher/utils.hpp"

namespace utils
{

sensor_msgs::msg::Image cv_mat_to_image_msg(
    const cv::Mat &image,
    const std::string &encoding)
{
    sensor_msgs::msg::Image msg;

    msg.height = image.rows;
    msg.width  = image.cols;
    msg.encoding = encoding;
    msg.is_bigendian = false;
    msg.step = static_cast<sensor_msgs::msg::Image::_step_type>(
        image.step);

    // Copy raw bytes
    msg.data.assign(image.datastart, image.dataend);

    return msg;
}

void shuffle_images(std::vector<cv::Mat> &images)
{
    static std::random_device rd;
    static std::mt19937 gen(rd());
    std::shuffle(images.begin(), images.end(), gen);
}

} // namespace utils
