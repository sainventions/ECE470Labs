cd Lab2

ros2 launch ur_robot_driver ur_control.launch.py ur_type:=ur3e robot_ip:=192.168.10.53 headless_mode:=true launch_rviz:=true kinematics_params_file:="Robot8_calibration.yaml"