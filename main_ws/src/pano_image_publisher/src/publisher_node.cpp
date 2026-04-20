#include "pano_image_publisher/publisher_node.hpp"

namespace pano_image_publisher {

    PublisherNode::PublisherNode() : Node("pano_image_publisher_node") {
    RCLCPP_INFO(this->get_logger(), "Publisher node has been started.");
}
} // namespace pano_image_publisher
