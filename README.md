# pano2depth_obstacle_detector

This is a ros2 pipeline that takes in a panoramic image and publishes pointclouds for environment understanding and obstacle avoidance.

Please see /docs for more info.

Each package also has a readme for more information.

### Instructions to build and run
1. Create a venv
```
cd ~/
python3 -m venv p2d_env
```
2. Install the python dependencies
```
cd main_ws/src/p2d_node/requirements.txt
pip install -r requirements.txt
```
3. Source the ROS setup.bash
```
source /opt/ros/jazzy/setup.bash
```
4. Source the environment you created
```
source ~/p2d_env/bin/activate
```
5. Build the workspace. We want to use the venv so we execute the following.
```
cd main_ws/
python -m colcon build
```
6. Source the setup.bash in the install folder
```
source install/setup.bash
```
7. Install the tf package
```
sudo apt install ros-${ROS_DISTRO}-tf-transformations
```
8. Download ALL 3 DA360 weights from https://drive.google.com/drive/folders/1FMLWZfJ_IPKOa_cEbVqrq8_BRkl3oB_2 
```
put in p2d_node/models
```
9. Launch the pipeline
```
ros2 launch p2d_node p2d_obs_dtctr_pipeline.launch.py
```