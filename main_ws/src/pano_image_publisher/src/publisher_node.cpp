#include "pano_image_publisher/publisher_node.hpp"

namespace pano_image_publisher {

  PublisherNode::PublisherNode()
  : Node("pano_image_publisher_node"),
  image_loader_(this->get_logger()) {
      
    RCLCPP_INFO(this->get_logger(), "Node started.");

    // Declare parameters with defaults
    this->declare_parameters();

    // Load the parameters
    this->load_parameters();

    // Load the images
    this->load_images();

    // Start the timer to publish images at the specified rate
    this->start_timer();
  }

  void PublisherNode::declare_parameters() {
    this->declare_parameter<std::string>("folder_path", ""); // Default to empty string
    this->declare_parameter<std::string>("topic_name", "pano_image"); // Default topic name
    this->declare_parameter<int>("publish_rate_in_hz", 1); // Default to 1 Hz
    this->declare_parameter<bool>("loop", true); // Default to loop images
    this->declare_parameter<bool>("shuffle", false); // Default to not shuffle the image order
  }

  void PublisherNode::load_parameters() {
    this->get_parameter("folder_path", folder_path_);
    this->get_parameter("topic_name", topic_name_);
    this->get_parameter("publish_rate_in_hz", publish_rate_in_hz_);
    this->get_parameter("loop", loop_);
    this->get_parameter("shuffle", shuffle_);

    RCLCPP_INFO(
      this->get_logger(), 
      "\n=== Parameters loaded ===\nfolder_path=%s\ntopic_name=%s\npublish_rate_in_hz=%d\nloop=%s\nshuffle=%s\n========================",
                folder_path_.c_str(), topic_name_.c_str(), publish_rate_in_hz_, loop_ ? "true" : "false", shuffle_ ? "true" : "false");
  }

  void PublisherNode::start_timer() {
    auto period_ms = std::chrono::milliseconds(1000 / this->publish_rate_in_hz_);

    // Create a timer that calls the publish_image method at the specified rate
    timer_ = this->create_wall_timer(
      period_ms,
      std::bind(&PublisherNode::publish_image, this)
    );

    RCLCPP_INFO(this->get_logger(), "Timer started with a period of %ld ms.", period_ms.count());
  }

  void PublisherNode::publish_image() {
    // TODO: Implement logic for publishing
    RCLCPP_INFO(this->get_logger(), "Publishing image!");
  void PublisherNode::load_images() {
    this->images_ = this->image_loader_.load_images(this->folder_path_);
    if (this->images_.empty()) {
      RCLCPP_WARN(this->get_logger(), "No images loaded from folder: %s", this->folder_path_.c_str());
    } else {
      RCLCPP_INFO(this->get_logger(), "Loaded %zu images from folder: %s", this->images_.size(), this->folder_path_.c_str());
    }
  }

  void PublisherNode::create_publisher() {
    this->publisher_ = this->create_publisher<sensor_msgs::msg::Image>(this->topic_name_, 10);
    RCLCPP_INFO(this->get_logger(), "Publisher created on topic: %s", this->topic_name_.c_str());
  }
} // namespace pano_image_publisher
