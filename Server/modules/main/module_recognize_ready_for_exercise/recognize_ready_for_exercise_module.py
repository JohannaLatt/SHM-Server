from Server.modules.abstract_main_module import AbstractMainModule

from Server.utils.enums import USER_JOINTS, KINECT_BONES
from Server.user import USER_STATE

from Server.utils.utils import get_angle_between_bones

from collections import deque
import numpy as np


class RecognizeReadyForExerciseModule(AbstractMainModule):

    timeseries_length = 20
    max_std_x = 75
    max_std_z = 140

    def __init__(self, Messaging, queue, User):
        super().__init__(Messaging, queue, User)

        # Save the spine_base and spine_shoulder position for the last 20 frames
        self.pos_spine_base = deque([[0,0,0]] * self.timeseries_length, maxlen=self.timeseries_length)
        self.pos_spine_shoulder = deque([[0,0,0]] * self.timeseries_length, maxlen=self.timeseries_length)

        self.joints = []
        self.bones = []

    def user_skeleton_updated(self, user):
        super().user_skeleton_updated(user)

        # Get the relevant joints and save them
        self.joints = user.get_joints()
        self.bones = user.get_bones()
        spine_shoulder = self.joints[USER_JOINTS.SpineShoulder.name]
        spine_base = self.joints[USER_JOINTS.SpineBase.name]

        self.pos_spine_base.append(spine_base)
        self.pos_spine_shoulder.append(spine_shoulder)

        is_standing_still = self.is_standing_still()

        if is_standing_still and self.knees_are_straight() and user.get_user_state() is USER_STATE.NONE:
            self.User.update_state(USER_STATE.READY_TO_EXERCISE)
            self.Messaging.send_text_to_mirror("Go ahead and start exercising!", id="exercise_status_text", position={"x": 0.03, "y": -0.39}, font_size=30, fade_in=0.3, stay=100000, fade_out=1, halign="left")
        elif not is_standing_still and user.get_user_state() is not USER_STATE.NONE:
            self.User.update_state(USER_STATE.NONE)
            self.Messaging.send_text_to_mirror("Please get into position in front of the camera and stand still...", id="exercise_status_text", position={"x": 0.03, "y": -0.39}, stay=10000, halign="left")

    # Uses time series data of last x frames to determine if the user was
    # standing in place, ie is ready for an exercise. More specifically, we look
    # at the standard deviation of the x- and z-position of two spine bones
    # over the last x frames
    def is_standing_still(self):
        std_spine_base_movement = np.std(np.asarray(self.pos_spine_base), axis=0)
        std_spine_shoulder_movement = np.std(np.asarray(self.pos_spine_shoulder), axis=0)

        return (std_spine_base_movement[0] < self.max_std_x
                and std_spine_base_movement[2] < self.max_std_z
                and std_spine_shoulder_movement[0] < self.max_std_x
                and std_spine_shoulder_movement[2] < self.max_std_z)

    def knees_are_straight(self):
        right_knee_angle = get_angle_between_bones(self.joints, self.bones, KINECT_BONES.ThighRight, KINECT_BONES.ShinRight)
        left_knee_angle = get_angle_between_bones(self.joints, self.bones, KINECT_BONES.ThighLeft, KINECT_BONES.ShinLeft)

        return right_knee_angle < 30 and left_knee_angle < 30

    def tracking_lost(self):
        super().tracking_lost()
        self.Messaging.send_text_to_mirror("exercise_status_text", "", stay=0)
