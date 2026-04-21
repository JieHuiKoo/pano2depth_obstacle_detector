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

    // Create the publisher
    this->setup_publisher();

    // Start the timer to publish images at the specified rate
    this->start_timer();
  }

  void PublisherNode::declare_parameters() {
    this->declare_parameter<std::string>("folder_path"        , "");            // Default to empty string
    this->declare_parameter<std::string>("publish_topic_name" , "pano_image");  // Default topic name
    this->declare_parameter<float>("publish_rate_in_hz"         , 1.0);             // Default to 1 Hz
    this->declare_parameter<bool>("loop"                      , true);          // Default to loop images
    this->declare_parameter<bool>("shuffle"                   , false);         // Default to not shuffle the image order
  }

  void PublisherNode::load_parameters() {
    this->get_parameter("folder_path"         , this->folder_path_);
    this->get_parameter("publish_topic_name"  , this->publish_topic_name_);
    this->get_parameter("publish_rate_in_hz"  , this->publish_rate_in_hz_);
    this->get_parameter("loop"                , this->loop_);
    this->get_parameter("shuffle"             , this->shuffle_);

    RCLCPP_INFO(
      this->get_logger(), 
      "\n=== Parameters loaded ===\nfolder_path=%s\npublish_topic_name=%s\npublish_rate_in_hz=%f\nloop=%s\nshuffle=%s\n========================",
                folder_path_.c_str(), publish_topic_name_.c_str(), publish_rate_in_hz_, loop_ ? "true" : "false", shuffle_ ? "true" : "false");
  }

  void PublisherNode::start_timer() {
    auto period_ms = std::chrono::milliseconds(static_cast<int>(1000.0 / this->publish_rate_in_hz_));

    // Create a timer that calls the publish_image method at the specified rate
    this->timer_ = this->create_wall_timer(
      period_ms,
      std::bind(&PublisherNode::publish_image, this)
    );

    RCLCPP_INFO(this->get_logger(), "Timer started with a period of %ld ms.", period_ms.count());
  }

  void PublisherNode::publish_image() {
    
    if (this->images_.empty()) {
      RCLCPP_WARN(this->get_logger(), "No images to publish.");
      return;
    }
    
    RCLCPP_INFO(this->get_logger(), "Publishing image!");

    // Get the current image
    const cv::Mat& image = this->images_[this->current_image_idx_];

    // Convert cv::Mat → ROS2 Image
    sensor_msgs::msg::Image msg =
        utils::cv_mat_to_image_msg(image, "bgr8");

    msg.header.stamp = this->now();
    msg.header.frame_id = "camera";

    // Publish the image
    this->publisher_->publish(msg);

    // Update the index for the next image
    this->current_image_idx_++;
    if (this->current_image_idx_ >= this->images_.size()) {
      if (this->loop_) {
        this->current_image_idx_ = 0; // Loop back to first image
      } else {
        RCLCPP_INFO(this->get_logger(), "Reached the end of the image list. Stopping publisher.");
        this->timer_->cancel(); // Stop the timer if not looping
      }
    }
  }

  void PublisherNode::load_images() {
    this->images_ = this->image_loader_.load_images(this->folder_path_);
    if (this->images_.empty()) {
      RCLCPP_WARN(this->get_logger(), "No images loaded from folder: %s", this->folder_path_.c_str());
    } else {
      RCLCPP_INFO(this->get_logger(), "Loaded %zu images from folder: %s", this->images_.size(), this->folder_path_.c_str());
    }
  }

  void PublisherNode::setup_publisher() {
    this->publisher_ = this->create_publisher<sensor_msgs::msg::Image>(this->publish_topic_name_, 10);
    RCLCPP_INFO(this->get_logger(), "Publisher created on topic: %s", this->publish_topic_name_.c_str());
  }
} // namespace pano_image_publisher
