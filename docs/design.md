# System Design Note

## System Framing
### Background
Mobile robots need dense perception of the environment it is operating in to naviage around safely.

Robots use sensors such as stereo, Lidar, RGB-D for perception. All these have a field of view, and areas that are not within the field of view are called blind spots.

Blind spots are dangerous for robots, as they may navigate into spots that have:
1. positive obstacles (above ground)
2. negative obstacles (below ground)
3. overhangs
Blindspots are one of the most common causes of navigation failures, collisions and unsafe robot behavior.

Blind spots can be overcome by adding more sensors, but this comes at a monetary cost, as well as compute cos as well as increased calibration complexity and power consumption.

### What this module does, and its value proposition
This module:
1. generates a 360 pointcloud of the robot's surroundings using a panoramic RGB image
2. Based on specified params, splits the pointcloud into:
- near pointcloud, which can help with
  - Navigable area determination in all directions
  - Spotting short obstacles very close to robot
  - Enhanced perception coverage 
- mid pointcloud, which can help with
  - Obstacles further away, can preempt the robot to slow down
- high pointcloud, which can help with
  - Overhangs
  - Features for SLAM (indoors)
3. Transforms the pointcloud frame into a specified frame in params
## ROS 2 Integration Design
![alt text](image.png)
1. python is used for the p2d_node as the libraries and setup dependencies for pytorch is more mature
2. Establishing a tf_static is very important, as sector based signal generation must be in base_link frame
  - This also goes for estimating distance of obstacles from robot. We need to calculate the distance in base_link frame

## Deployment Considerations
1. Avoid publishing full projected pointcloud
  - To reduce latency and reduce network congestion
  - Only nodes that need the full pointcloud can subscribe to the relevant pointcloud
  - Can consider only publishing "low" pointcloud
2. DepthAnything does not produce metric depth, so it is not very reliable to segment based on specific distance thresholds.
  - The absolute scale of the depth is unknown
  - Scale can drift between frames
  - We should only use angle bands, as the vertical angle of each pixel is stable
3. To reduce memory
  - It is unlikely we need to project every single pixel from the depth image
  - Therefore, we can skip some pixels by tuning the stride parameter
  