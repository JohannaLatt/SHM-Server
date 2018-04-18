from Server.modules.abstract_mirror_module import AbstractMirrorModule
from Server.utils.enums import MSG_TO_MIRROR_KEYS

from enum import Enum
import json


class JOINTS(Enum):
    SPINE_BASE = 0
    SPINE_MID = 1
    HEAD = 3
    SHOULDER_LEFT = 4
    ELBOW_LEFT = 5
    WRIST_LEFT = 6
    HAND_LEFT = 7
    SHOULDER_RIGHT = 8
    ELBOW_RIGHT = 9
    WRIST_RIGHT = 10
    HAND_RIGHT = 11
    HIP_LEFT = 12
    KNEE_LEFT = 13
    ANKLE_LEFT = 14
    FOOT_LEFT = 15
    HIP_RIGHT = 16
    KNEE_RIGHT = 17
    ANKLE_RIGHT = 18
    FOOT_RIGHT = 19
    SPINE_SHOULDER = 20
    HAND_TIP_LEFT = 21
    THUMB_LEFT = 22
    HAND_TIP_RIGHT = 23
    THUMB_RIGHT = 24
    NONE = 25


JOINT_PARENTS = {
    JOINTS.SPINE_BASE: JOINTS.NONE,
    JOINTS.SPINE_MID: JOINTS.SPINE_BASE,
    JOINTS.HEAD: JOINTS.SPINE_MID,
    JOINTS.SHOULDER_LEFT: JOINTS.SPINE_SHOULDER,
    JOINTS.ELBOW_LEFT: JOINTS.SHOULDER_LEFT,
    JOINTS.WRIST_LEFT: JOINTS.ELBOW_LEFT,
    JOINTS.HAND_LEFT: JOINTS.WRIST_LEFT,
    JOINTS.SHOULDER_RIGHT: JOINTS.SPINE_SHOULDER,
    JOINTS.ELBOW_RIGHT: JOINTS.SHOULDER_RIGHT,
    JOINTS.WRIST_RIGHT: JOINTS.ELBOW_RIGHT,
    JOINTS.HAND_RIGHT: JOINTS.WRIST_RIGHT,
    JOINTS.HIP_LEFT: JOINTS.SPINE_BASE,
    JOINTS.KNEE_LEFT: JOINTS.HIP_LEFT,
    JOINTS.ANKLE_LEFT: JOINTS.KNEE_LEFT,
    JOINTS.FOOT_LEFT: JOINTS.ANKLE_LEFT,
    JOINTS.HIP_RIGHT: JOINTS.SPINE_BASE,
    JOINTS.KNEE_RIGHT: JOINTS.HIP_RIGHT,
    JOINTS.ANKLE_RIGHT: JOINTS.KNEE_RIGHT,
    JOINTS.FOOT_RIGHT: JOINTS.ANKLE_RIGHT,
    JOINTS.SPINE_SHOULDER: JOINTS.SPINE_MID,
    JOINTS.HAND_TIP_LEFT: JOINTS.HAND_LEFT,
    JOINTS.THUMB_LEFT: JOINTS.HAND_LEFT,
    JOINTS.HAND_TIP_RIGHT: JOINTS.HAND_RIGHT,
    JOINTS.THUMB_RIGHT: JOINTS.HAND_RIGHT,
    JOINTS.NONE: JOINTS.NONE
}


class SAMPLE_JOINTS(Enum):
    HEAD = 1
    NECK = 2
    TORSO = 3
    LEFT_SHOULDER = 4
    LEFT_ELBOW = 5
    RIGHT_SHOULDER = 6
    RIGHT_ELBOW = 7
    LEFT_HIP = 8
    LEFT_KNEE = 9
    RIGHT_HIP = 10
    RIGHT_KNEE = 11
    LEFT_HAND = 12
    RIGHT_HAND = 13
    LEFT_FOOT = 14
    RIGHT_FOOT = 15


SAMPLE_JOINT_PARENTS = {
    'HEAD': 2,
    'NECK': 3,
    'TORSO': 3,
    'LEFT_SHOULDER': 2,
    'LEFT_ELBOW': 4,
    'RIGHT_SHOULDER': 2,
    'RIGHT_ELBOW': 6,
    'LEFT_HIP': 3,
    'LEFT_KNEE': 8,
    'RIGHT_HIP': 3,
    'RIGHT_KNEE': 10,
    'LEFT_HAND': 5,
    'RIGHT_HAND': 7,
    'LEFT_FOOT': 9,
    'RIGHT_FOOT': 11
}


class RenderSkeletonModule(AbstractMirrorModule):

    def __init__(self, Messaging):
        super().__init__(Messaging)

    def mirror_started(self):
        # do nothing with that
        pass

    def tracking_started(self):
        super().tracking_started()
        print('[RenderSkeletonModule][info] Tracking has started')
        pass

    def tracking_data(self, data):
        super().tracking_data(data)

        print('[RenderSkeletonModule][info] Received tracking data {}..'.format(data[0:50]))

        # See http://pr.cs.cornell.edu/humanactivities/data.php for details
        data = data.split(",")

        # Create joints data-structure which is a list of three coordinates
        # that is filled with zeros at first: [[0,0,0][0,0,0][0,0,0]...]
        joints3D = [[0 for x in range(3)] for y in range(len(SAMPLE_JOINTS) + 1)]
        j = 1

        if len(data) != 172:
            print("[RenderSkeletonModule][error] len of skeleton data is {}".format(len(data)))
            return

        for i in range(11, 154, 14):
            #print("{}: {}, {}, {}".format(SAMPLE_JOINTS(j).name, data[i], data[i+1], data[i+2]))
            joints3D[j][0] = data[i]
            joints3D[j][1] = data[i+1]
            joints3D[j][2] = data[i+2]
            j += 1
        for i in range(155, 168, 4):
            #print("{}: {}, {}, {}".format(SAMPLE_JOINTS(j).name, data[i], data[i+1], data[i+2]))
            joints3D[j][0] = data[i]
            joints3D[j][1] = data[i+1]
            joints3D[j][2] = data[i+2]
            j += 1

        # Read the 2D-links from the joint-data for easy rendering
        result = []
        for joint in range(1, len(joints3D)):
            # First get the parent joint (the 'to'-joint)
            parent_joint = SAMPLE_JOINT_PARENTS[SAMPLE_JOINTS(joint).name]

            # Save the result
            # Format for from a to b: [(ax, bx), (ay, by)]
            from_to = []
            from_to.append((joints3D[joint][0], joints3D[parent_joint][0]))
            from_to.append((joints3D[joint][1], joints3D[parent_joint][1]))

            # Append to result
            result.append(from_to)

        result_str = json.dumps(result)
        self.Messaging.send_message(MSG_TO_MIRROR_KEYS.RENDER_SKELETON.name, result_str)

    def tracking_lost(self):
        super().tracking_lost()
        print('[RenderSkeletonModule][info] Tracking lost')
        pass
