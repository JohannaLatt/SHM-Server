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

JOINT_PARENTS = {
    'SpineBase': 2,
    'SpineMid': 3,
    'Neck': 3,
    'Head': 2,
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
        #print('[RenderSkeletonModule][info] Tracking received: {}'.format(data))

        # Load string as json
        data = json.loads(data)["joint_data"]

        # Reformat the joint data into bone data to send for rendering
        result = []
        for joint, joint_data in data.items():
            from_p = joint_data["joint_position"]
            to_p = data[joint_data["joint_parent"]]["joint_position"]

            # Format for from a to b: [(ax, ay, az), (bx, by, bz)]
            from_to = []
            from_to.append((from_p["x"], from_p["y"], from_p["z"]))
            from_to.append((to_p["x"], to_p["y"], to_p["z"]))

            # Append to result
            result.append(from_to)

        result_str = json.dumps(result)
        self.Messaging.send_message(MSG_TO_MIRROR_KEYS.RENDER_SKELETON.name, result_str)

    def tracking_lost(self):
        super().tracking_lost()
        print('[RenderSkeletonModule][info] Tracking lost')
        self.Messaging.send_message(MSG_TO_MIRROR_KEYS.CLEAR_SKELETON.name, '')
        pass
