#include "pano_image_publisher/image_loader.hpp"

namespace fs = std::filesystem;

namespace pano_image_publisher {
    
  bool ImageLoader::is_supported_file(const std::string& file_path) {
    static const std::vector<std::string> s_supported_extensions = {
      ".jpg",
      ".jpeg",
      ".png",
      ".bmp",
      ".tiff",
    };

    // Get the extension of the file
    auto extension = fs::path(file_path).extension().string();

    // Conver the extension to lower
    std::transform(extension.begin(), extension.end(), extension.begin(), ::tolower);

    // Check if the extension is in the supported list
    for (const auto& ext : s_supported_extensions) {
      if (extension == ext) {
        return true;
      }
    }
    return false;
  }

  std::vector<cv::Mat> ImageLoader::load_images(const std::string &folder_path)
  {
    std::vector<cv::Mat> images;

    if (!fs::exists(folder_path) || !fs::is_directory(folder_path)) {
        RCLCPP_ERROR(this->logger_, "No images loaded from folder: %s", folder_path.c_str());
        return images;
    }

    for (const auto &entry : fs::directory_iterator(folder_path)) {
        if (!entry.is_regular_file())
            continue;

        const std::string filename = entry.path().string();

        if (!this->is_supported_file(filename))
            continue;

        cv::Mat img = cv::imread(filename, cv::IMREAD_COLOR);
        if (img.empty()) {
            RCLCPP_ERROR(this->logger_, "Failed to load image: %s", filename.c_str());
            continue;
        }

        images.push_back(img);
    }

    return images;
}
}
