import argparse
import time

from enum import Enum

import cv2
import numpy as np
import tensorflow as tf
import matplotlib as mpl
mpl.use('TkAgg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from models.nets import vnect_model_bn_folded as vnect_model
import utils.utils as utils

import os

joint_color_code = [[139, 53, 255],
                    [0, 56, 255],
                    [43, 140, 237],
                    [37, 168, 36],
                    [147, 147, 0],
                    [70, 17, 145]]

class Limb(Enum):
    HEAD_TOP = 0
    NECK_CENTER = 1
    SHOULDER_RIGHT = 2
    ELBOW_RIGHT = 3
    WRIST_RIGHT = 4
    SHOULDER_LEFT = 5
    ELBOW_LEFT = 6
    WRIST_LEFT = 7,
    HIP_RIGHT = 8,
    KNEE_RIGHT = 9,
    FOOT_RIGHT = 10,
    HIP_LEFT = 11,
    KNEE_LEFT = 12,
    FOOT_LEFT = 13,
    HIP_CENTER = 14,
    TORSO_CENTER = 15,
    HEAD_MIDDLE = 16,
    FINGERS_RIGHT = 17,
    FINGERS_LEFT = 18,
    TOES_RIGHT = 19,
    TOES_LEFT = 20

# Limb parents of each joint
limb_parents = [    Limb.HEAD_MIDDLE,
                    Limb.TORSO_CENTER,
                    Limb.NECK_CENTER,
                    Limb.SHOULDER_RIGHT,
                    Limb.ELBOW_RIGHT,
                    Limb.NECK_CENTER,
                    Limb.SHOULDER_LEFT,
                    Limb.ELBOW_LEFT,
                    Limb.HIP_CENTER,
                    Limb.HIP_RIGHT,
                    Limb.KNEE_RIGHT,
                    Limb.HIP_CENTER,
                    Limb.HIP_LEFT,
                    Limb.KNEE_LEFT,
                    Limb.HIP_CENTER,
                    Limb.HIP_CENTER,
                    Limb.NECK_CENTER,
                    Limb.WRIST_RIGHT,
                    Limb.WRIST_LEFT,
                    Limb.FOOT_RIGHT,
                    Limb.FOOT_LEFT  ]

# input scales
scales = [1.0, 0.7]

# default params
model_file = os.path.dirname(os.path.abspath(__file__)) + '/models/weights/vnect_tf'
input_size = 368
pool_scale = 8
device = 'cpu'
num_of_joints = 21


def say(something):
    print(something)

def init(model_file = model_file, input_size = input_size, pool_scale = pool_scale, device = device):
    # Use gpu or cpu
    gpu_count = {'GPU':1} if device == 'gpu' else {'GPU':0}

    # Create model
    model_tf = vnect_model.VNect(input_size)

    # Create session
    sess_config = tf.ConfigProto(device_count=gpu_count)
    sess = tf.Session(config=sess_config)

    # Restore weights
    saver = tf.train.Saver()
    saver.restore(sess, model_file)

def process_image(img_path):
    input_batch = []

    # Cut out square in the middle of the image
    sq_img = utils.read_square_image(img_path, '', input_size, 'IMAGE')
    orig_size_input = sq_img.astype(np.float32)

    # Create multi-scale inputs
    for scale in scales:
        resized_img = utils.resize_pad_img(orig_size_input, scale, input_size)
        input_batch.append(resized_img)

    input_batch = np.asarray(input_batch, dtype=np.float32)
    input_batch /= 255.0
    input_batch -= 0.4

    # Inference
    [hm, x_hm, y_hm, z_hm] = sess.run(
        [model_tf.heapmap, model_tf.x_heatmap, model_tf.y_heatmap, model_tf.z_heatmap],
        feed_dict={model_tf.input_holder: input_batch})

    # Average scale outputs
    hm_size = input_size // pool_scale
    hm_avg = np.zeros(shape=(hm_size, hm_size, num_of_joints))
    x_hm_avg = np.zeros(shape=(hm_size, hm_size, num_of_joints))
    y_hm_avg = np.zeros(shape=(hm_size, hm_size, num_of_joints))
    z_hm_avg = np.zeros(shape=(hm_size, hm_size, num_of_joints))
    for i in range(len(scales)):
        rescale = 1.0 / scales[i]
        scaled_hm = cv2.resize(hm[i, :, :, :], (0, 0), fx=rescale, fy=rescale, interpolation=cv2.INTER_LINEAR)
        scaled_x_hm = cv2.resize(x_hm[i, :, :, :], (0, 0), fx=rescale, fy=rescale, interpolation=cv2.INTER_LINEAR)
        scaled_y_hm = cv2.resize(y_hm[i, :, :, :], (0, 0), fx=rescale, fy=rescale, interpolation=cv2.INTER_LINEAR)
        scaled_z_hm = cv2.resize(z_hm[i, :, :, :], (0, 0), fx=rescale, fy=rescale, interpolation=cv2.INTER_LINEAR)
        mid = [scaled_hm.shape[0] // 2, scaled_hm.shape[1] // 2]
        hm_avg += scaled_hm[mid[0] - hm_size // 2: mid[0] + hm_size // 2,
                  mid[1] - hm_size // 2: mid[1] + hm_size // 2, :]
        x_hm_avg += scaled_x_hm[mid[0] - hm_size // 2: mid[0] + hm_size // 2,
                    mid[1] - hm_size // 2: mid[1] + hm_size // 2, :]
        y_hm_avg += scaled_y_hm[mid[0] - hm_size // 2: mid[0] + hm_size // 2,
                    mid[1] - hm_size // 2: mid[1] + hm_size // 2, :]
        z_hm_avg += scaled_z_hm[mid[0] - hm_size // 2: mid[0] + hm_size // 2,
                    mid[1] - hm_size // 2: mid[1] + hm_size // 2, :]
    hm_avg /= len(scales)
    x_hm_avg /= len(scales)
    y_hm_avg /= len(scales)
    z_hm_avg /= len(scales)

    # Get 2d joints
    utils.extract_2d_joint_from_heatmap(hm_avg, input_size, joints_2d)

    # Get 3d joints
    utils.extract_3d_joints_from_heatmap(joints_2d, x_hm_avg, y_hm_avg, z_hm_avg, input_size, joints_3d)

    #print('FPS: {:>2.2f}'.format(1 / (time.time() - t1)))
    print('2D Joints:')
    for joint_num in range(len(joints_2d)):
        print('{}: {}'.format(Limb(joint_num), joints_2d[joint_num]))
