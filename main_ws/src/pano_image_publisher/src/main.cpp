#include <rclcpp/rclcpp.hpp>
#include "pano_image_publisher/publisher_node.hpp"

int main (int argc, char **argv) {
    
    rclcpp::init(argc, argv);
    
    auto node = std::make_shared<pano_image_publisher::PublisherNode>();
    
    rclcpp::spin(node);
    
    rclcpp::shutdown();
    
    return 0;
}
