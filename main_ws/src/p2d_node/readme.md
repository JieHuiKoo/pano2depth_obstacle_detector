
### What does this node do?
This is a ros2 node that will:
1. Subscribe to a image topic
2. Run inference with a model to get depth image
3. Project to pcl (and also transform to desired frame)
4. Publish pcl

You may change the config params as you see fit in /p2d_node/config
