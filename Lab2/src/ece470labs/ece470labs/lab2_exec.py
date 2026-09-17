#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.executors import SingleThreadedExecutor
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from sensor_msgs.msg import JointState
from ur_msgs.srv import SetIO
from ur_msgs.msg import IOStates
import time
import numpy as np
from math import pi
import sys

SUCTION_THRESHOLD = 2.0


class JointAngles:
    def __init__(self):
        self.name = ["", "", "", "", "", ""]  # could have also done [""] * 6
        self.position = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]


# UR3e home position
home = np.radians([120, -90, 90, -90, -90, 0])

# Hanoi tower location
# Q11 = [120*pi/180.0, -56*pi/180.0, 124*pi/180.0, -158*pi/180.0, -90*pi/180.0, 0*pi/180.0]
# Q12 = [120*pi/180.0, -64*pi/180.0, 123*pi/180.0, -148*pi/180.0, -90*pi/180.0, 0*pi/180.0]
# Q13 = [120*pi/180.0, -72*pi/180.0, 120*pi/180.0, -137*pi/180.0, -90*pi/180.0, 0*pi/180.0]

A_0 = np.radians([137.45, -59.72, 127.27, -158.89, -89.59, 116.82])
A_1 = np.radians([137.49, -68.13, 125.83, -149.03, -89.58, 116.84])
A_2 = np.radians([137.45, -75.50, 123.49, -139.32, -89.57, 116.79])
A_up = np.radians([137.45, -80.50, 123.49, -139.32, -89.57, 116.79])

B_0 = np.radians([164.30, -60.94, 130.87, -161.23, -90.24, 143.67])
B_1 = np.radians([163.60, -70.20, 129.89, -150.98, -90.20, 142.96])
B_2 = np.radians([163.79, -77.81, 126.71, -140.19, -90.20, 143.12])
B_up = np.radians([163.79, -82.81, 126.71, -140.19, -90.20, 143.12])

C_0 = np.radians([188.80, -55.33, 116.77, -152.45, -90.72, 168.18])
C_1 = np.radians([189.42, -62.70, 115.95, -144.24, -90.72, 168.78])
C_2 = np.radians([188.78, -68.63, 112.93, -135.31, -90.70, 168.11])
C_up = np.radians([188.78, -73.63, 112.93, -135.31, -90.70, 168.11])



############## Your Code Start Here ##############
"""
TODO: Initialize Q matrix
"""

Q = [[A_0, A_1, A_2, A_up],
     [B_0, B_1, B_2, B_up],
     [C_0, C_1, C_2, C_up]]

# Q[0] is tower A, Q[1] is tower B, Q[2] is tower C
# Q[0][0] is tower A, height 0 

############### Your Code End Here ###############


class UR3e(Node):
    def __init__(self):
        super().__init__('ur3e')

        # Publishers
        self.trajectory_pub = self.create_publisher(
            JointTrajectory, '/scaled_joint_trajectory_controller/joint_trajectory', 10)

        # Subscribers
        self.joint_state_sub = self.create_subscription(
            JointState, '/joint_states', self.joint_state_callback, 10)

        ############## Your Code Start Here ##############
        # TODO: define a ROS subscriber for gripper input message and corresponding callback function
        # ROS2 gripper input topic: /io_and_status_controller/io_states
        
        self.io_state_sub = self.create_subscription(
            IOStates, '/io_and_status_controller/io_states', self.io_state_callback, 10)
        


        ############### Your Code End Here ###############

        # Service clients
        self.io_client = self.create_client(
            SetIO, '/io_and_status_controller/set_io')
        while not self.io_client.wait_for_service(timeout_sec=2.0):
            self.get_logger().warn('IO service not available, waiting...')

        # State variables
        self.current_joint_state = None
        self.analog_in_0_value = 0
        self.current_JointAngles = JointAngles()
        self.joint_names = [
            'shoulder_pan_joint', 'shoulder_lift_joint', 'elbow_joint',
            'wrist_1_joint', 'wrist_2_joint', 'wrist_3_joint'
        ]  # shoulder_pan_joint is the base rotation joint

    def joint_state_callback(self, msg):
        # Currently only used to check if messages have arrived
        self.current_joint_state = msg
        index_inOrder = 0
        for name in self.joint_names:
            index_outofOrder = msg.name.index(name)
            self.current_JointAngles.name[index_inOrder] = name
            self.current_JointAngles.position[index_inOrder] = msg.position[index_outofOrder]
            index_inOrder = index_inOrder + 1

    def io_state_callback(self, msg):
        ############## Your Code Start Here ##############
        """
        TODO: define a ROS topic callback funtion that 
        receives and stores the state of  the suction cup
        Whenever /io_and_status_controller/io_states 
        publishes this info, this callback function is
        called.
        """

        for io_state in msg.analog_in_states:
            if io_state.pin == 0: # Analog in 0 is suction pressure
                self.analog_in_0_value = io_state.state
                break

    ############### Your Code End Here ###############

    def set_io(self, pin, state):
        req = SetIO.Request()
        req.fun = 1
        req.pin = pin
        req.state = state
        future = self.io_client.call_async(req)
        rclpy.spin_until_future_complete(self, future)
        return future.result()

    def move_arm(self, target):
        if self.current_joint_state is None:
            self.get_logger().error("No joint state received!")
            return False

        V_MAX = 1  # 2.09    # rad/s
        A_MAX = 0.8  # 2.79   # rad/s^2
        MIN_DURATION = 1
        MAX_DURATION = 8.0

        deltas = []
        for i in range(6):
            deltas.append(
                abs(self.current_JointAngles.position[i] - target[i]))

        max_delta = max(deltas)
        t_acc = V_MAX / A_MAX
        d_acc = 0.5 * A_MAX * (t_acc ** 2)
        if max_delta > 2 * d_acc:
            # trapezoidal velocity profile
            t_total = 2 * t_acc + (max_delta - 2 * d_acc) / V_MAX
        else:
            # triangular velocity profile
            t_total = 2 * (max_delta / A_MAX) ** 0.5

        duration = max(MIN_DURATION, min(t_total, MAX_DURATION))

        trajectory_msg = JointTrajectory()
        trajectory_msg.joint_names = self.joint_names

        # Start immediately when the controller receives it
        trajectory_msg.header.stamp.sec = 0
        trajectory_msg.header.stamp.nanosec = 0

        # Anchor point: current measured joint state at t = 0
        p0 = JointTrajectoryPoint()
        p0.positions = self.current_JointAngles.position
        p0.velocities = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]  # starting at rest
        p0.accelerations = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]  # starting at rest
        p0.time_from_start.sec = 0
        p0.time_from_start.nanosec = 0
        trajectory_msg.points.append(p0)

        # Goal point
        p1 = JointTrajectoryPoint()
        p1.positions = target
        # end at rest, 2 point trajectory
        p1.velocities = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        p1.accelerations = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]  # end at rest.
        p1.time_from_start.sec = int(duration)
        p1.time_from_start.nanosec = int((duration - int(duration)) * 1e9)
        trajectory_msg.points.append(p1)

        self.trajectory_pub.publish(trajectory_msg)

        self.get_logger().info(f'Moving to position: {np.degrees(target)}')

        # Wait for movement completion
        start_time = time.time()
        while time.time() - start_time < duration + 2:
            rclpy.spin_once(self, timeout_sec=0.1)

            deltas = []
            for i in range(6):
                deltas.append(
                    abs(self.current_JointAngles.position[i] - target[i]))
            if all(delta < 0.001 for delta in deltas):
                time.sleep(0.25)
                return True
        return False

    def move_block(self, start_tower, start_height, end_tower, end_height):
        global Q

        self.move_arm(home)
        self.move_arm(Q[start_tower][start_height+1])
        self.move_arm(Q[start_tower][start_height])
        self.set_io(0, 1.0)  # Turn on suction

        start_time = time.time()
        while time.time() - start_time < 1.0:
            rclpy.spin_once(self, timeout_sec=0.05)

        if self.analog_in_0_value < SUCTION_THRESHOLD:
            self.get_logger().error("Failed to pick up block at tower " + str(start_tower) + " height " + str(start_height))
            self.set_io(0, 0.0)  # Turn off suction
            return 1
        
        self.move_arm(Q[start_tower][start_height+1])
        
        self.move_arm(home)

        self.move_arm(Q[end_tower][end_height+1])
        self.move_arm(Q[end_tower][end_height])
        self.set_io(0, 0.0)  # Turn off suction

        while time.time() - start_time < 1.0:
            rclpy.spin_once(self, timeout_sec=0.05)
        
        self.move_arm(Q[end_tower][end_height+1])


        return 0

    ############### Your Code End Here ###############


def main(args=None):
    input("Check if the UR3e is in 'Remote' Mode?\n\
    Check if the UR3e is initialized and in 'Normal' state.\n\
    Have you run the ROS2 launch statement?\n\
    If there was an UR3e emergency stop or error, Ctrl-C the ros2 launch and rerun.\n\
    \n\
    Press <Enter> to Continue.")
    rclpy.init(args=args)
    node = UR3e()
    executor = SingleThreadedExecutor()
    executor.add_node(node)

    ############## Your Code Start Here ##############
    # TODO: modify the code below so that program can get user input
    loop_count = 0
    # Wait for initial state updates
    while node.current_joint_state is None:
        executor.spin_once(timeout_sec=0.05)
        node.get_logger().info("Waiting for initial state updates...")
        time.sleep(0.5)

    try:
        # Get user input
        start_tower = int(input("Enter start tower (1, 2, or 3): ")) -1
        end_tower = int(input("Enter end tower (1, 2, or 3): ")) -1
        if start_tower not in [0, 1, 2] or end_tower not in [0, 1, 2]:
            return
        if start_tower == end_tower:
            return
        temp_tower = 3 - start_tower - end_tower
        BOTTOM = 0
        MIDDLE = 1
        TOP = 2
        moves = [(start_tower, TOP, end_tower, BOTTOM),
                 (start_tower, MIDDLE, temp_tower, BOTTOM),
                 (end_tower, BOTTOM, temp_tower, MIDDLE),
                 (start_tower, BOTTOM, end_tower, BOTTOM),
                 (temp_tower, MIDDLE, start_tower, BOTTOM),
                 (temp_tower, BOTTOM, end_tower, MIDDLE),
                 (start_tower, BOTTOM, end_tower, TOP)]
        for i, move in enumerate(moves):
            start_tower, start_height, end_tower, end_height = move
            error = node.move_block(start_tower, start_height, end_tower, end_height)
            if error:
                break
        else:
            node.get_logger().info("Successfully moved the tower!")
            node.move_arm(home)

    except KeyboardInterrupt:
        pass
    finally:
        node.set_io(0, 0.0)  # Turn off suction
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
