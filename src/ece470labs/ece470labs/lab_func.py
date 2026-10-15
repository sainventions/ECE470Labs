#!/usr/bin/env python
import numpy as np
from scipy.linalg import expm
from math import pi
import math

"""
Use 'expm' for matrix exponential.
Angles are in radian, distance are in meters.
"""


def Get_MS():
    # =================== Your code starts here ====================#
    # Fill in the correct values for S1~6, as well as the M matrix
    M = np.array([
        [0, -1, 0, .392],
        [0, 0, -1, .432],
        [1, 0, 0, .2155],
        [0, 0, 0, 1],
    ])

    q1 = np.array([[-0.150, 0.150, 0.01]])
    q2 = q1 + np.array([[0.0, 0.120, 0.152]])
    q3 = q2 + np.array([[0.244, 0.0, 0.0]])
    q4 = q3 + np.array([[0.213, -0.093, 0.00]])
    q5 = q4 + np.array([[0.0, 0.104, 0.0]])
    q6 = q5 + np.array([[0.085, 0.0, 0.0]])

    w1 = np.array([[0, 0, 1]])
    w2 = np.array([[0, 1, 0]])
    w3 = np.array([[0, 1, 0]])
    w4 = np.array([[0, 1, 0]])
    w5 = np.array([[1, 0, 0]])
    w6 = np.array([[0, 1, 0]])

    v1 = -np.cross(w1, q1)
    v2 = -np.cross(w2, q2)
    v3 = -np.cross(w3, q3)
    v4 = -np.cross(w4, q4)
    v5 = -np.cross(w5, q5)
    v6 = -np.cross(w6, q6)

    S = np.zeros((6, 6))
    S[:, 0] = np.vstack((w1.T, v1.T)).flatten()
    S[:, 1] = np.vstack((w2.T, v2.T)).flatten()
    S[:, 2] = np.vstack((w3.T, v3.T)).flatten()
    S[:, 3] = np.vstack((w4.T, v4.T)).flatten()
    S[:, 4] = np.vstack((w5.T, v5.T)).flatten()
    S[:, 5] = np.vstack((w6.T, v6.T)).flatten()

    # ==============================================================#
    return M, S


def screw_to_matrix(S, i):
    wx, wy, wz, vx, vy, vz = S[:, i]
    return np.array([
        [0, -wz, wy, vx],
        [wz, 0, -wx, vy],
        [-wy, wx, 0, vz],
        [0, 0, 0, 0]
    ])


"""
Function that calculates encoder numbers for each motor
"""


def lab_fk(theta1, theta2, theta3, theta4, theta5, theta6):

    # Initialize the return_value
    return_value = [None, None, None, None, None, None]

    # =========== Implement joint angle to encoder expressions here ===========
    print("Foward kinematics calculated:\n")

    # =================== Your code starts here ====================#
    M , S = Get_MS()
    S1 = screw_to_matrix(S, 0)
    S2 = screw_to_matrix(S, 1)
    S3 = screw_to_matrix(S, 2)
    S4 = screw_to_matrix(S, 3)
    S5 = screw_to_matrix(S, 4)
    S6 = screw_to_matrix(S, 5)

    T = expm(S1*theta1) @ expm(S2*theta2) @ expm(S3*theta3) @ expm(S4*theta4) @ expm(S5*theta5) @ expm(S6*theta6) @ M
    # ==============================================================#

    print(str(T) + "\n")

    return_value[0] = theta1 + pi
    return_value[1] = theta2
    return_value[2] = theta3
    return_value[3] = theta4 - (0.5*pi)
    return_value[4] = theta5
    return_value[5] = theta6

    return return_value

    """
Function that calculates an elbow up Inverse Kinematic solution for the UR3
"""


def lab_invk(xWgrip, yWgrip, zWgrip, yaw_WgripDegree):
    # =================== Your code starts here ====================#

    theta1 = 0.0
    theta2 = 0.0
    theta3 = 0.0
    theta4 = 0.0
    theta5 = 0.0
    theta6 = 0.0

    # ==============================================================#
    return lab_fk(theta1, theta2, theta3, theta4, theta5, theta6)
