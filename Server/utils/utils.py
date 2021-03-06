from numpy import (dot, arccos, linalg, clip, degrees)
import numpy as np


# Math
def unit_vector(vector):
    """ Returns the unit vector of the vector.  """
    return vector / linalg.norm(vector)


def angle_between(v1, v2):
    """ Returns the angle in degrees between vectors 'v1' and 'v2' """
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    return degrees(arccos(clip(dot(v1_u, v2_u), -1.0, 1.0)))


# Skeleton-specific utils
def get_vector_of_bone(joints, bones, bone):
    return (joints[bones[bone][0].name][0] - joints[bones[bone][1].name][0], # x
            joints[bones[bone][0].name][1] - joints[bones[bone][1].name][1], # y
            joints[bones[bone][0].name][2] - joints[bones[bone][1].name][2]) # z


def get_angle_between_bones(joints, bones, bone_a, bone_b):
    vector_a = get_vector_of_bone(joints, bones, bone_a)
    vector_b = get_vector_of_bone(joints, bones, bone_b)
    angle = np.around(angle_between(vector_a, vector_b), decimals=1)
    return angle


# Colors
def get_color_at_angle(angle, angle_min, angle_max, color_low, color_high):
    ''' Returns a color between red and green depending
        on the input angle and the max and min angles.
        Smaller equals right color, bigger wrong. '''

    # Transform the angle to a value between 0 and 1
    if angle < angle_min:
        t = 0
    elif angle > angle_max:
        t = 1
    else:
        t = (angle - angle_min) / (angle_max - angle_min)

    # Calculate the interpolated color
    return lerp_hsv(color_low, color_high, t)


def lerp_hsv(color_a, color_b, t):
    # Hue interpolation
    d = color_b[0] - color_a[0]

    if color_a[0] > color_b[0]:
        # Swap (a.h, b.h)
        h3 = color_b[0]
        color_b = (color_a[0], color_b[1], color_b[2], color_b[3])
        color_a = (h3, color_a[1], color_a[2], color_a[3])

        d = -d;
        t = 1 - t;

    if d > 0.5:  # 180deg
        color_a = (color_a[0] + 1, color_a[1], color_a[2], color_a[3])  # 360deg
        h = (color_a[0] + t * (color_b[0] - color_a[0]) ) % 1 # 360deg

    if d <= 0.5:  # 180deg
        h = color_a[0] + t * d

    return(h,
            color_a[1] + t * (color_b[1]-color_a[1]),  # S
            color_a[2] + t * (color_b[2]-color_a[2]),  # V
            color_a[3] + t * (color_b[3]-color_a[3])   # A
            )
