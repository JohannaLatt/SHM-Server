from numpy import (dot, arccos, linalg, clip, degrees)


# Math
def unit_vector(vector):
    """ Returns the unit vector of the vector.  """
    return vector / linalg.norm(vector)


def angle_between(v1, v2):
    """ Returns the angle in degrees between vectors 'v1' and 'v2' """
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    return degrees(arccos(clip(dot(v1_u, v2_u), -1.0, 1.0)))


# Colors
def lerp_hsv(color_a, color_b, t):
    # Hue interpolation
    d = color_b[0] - color_a[0]

    if color_a[0] > color_b[0]:
        # Swap (a.h, b.h)
        h3 = color_b[0]
        color_b[0] = color_b[0]
        color_a[0] = h3

        d = -d;
        t = 1 - t;

    if d > 0.5:  # 180deg
        color_a[0] = color_a[0] + 1  # 360deg
        h = (color_a[0] + t * (color_b[0] - color_a[0]) ) % 1 # 360deg

    if d <= 0.5:  # 180deg
        h = color_a[0] + t * d

    return(h,
            color_a[1] + t * (color_b[1]-color_a[1]),  # S
            color_a[2] + t * (color_b[2]-color_a[2]),  # V
            color_a[3] + t * (color_b[3]-color_a[3])   # A
            )
