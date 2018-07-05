from Server.modules.abstract_mirror_module import AbstractMirrorModule
from Server.utils.enums import KINECT_JOINTS
from Server.utils.enums import MSG_TO_MIRROR_KEYS

from Server.user import USER_STATE
from Server.user import SQUAT_STAGE

from Server.utils.utils import get_angle_between_bones

import json
from collections import deque

import numpy as np


class RecognizeSquatModule(AbstractMirrorModule):

    threshold_equal_y_pos = 20     # maximum wiggle room in y to consider two y-positions as the same
    threshold_movement_in_y = None   # minimum distance needed in y to count something as a squat (will be calculated per user)

    timeseries_length = 20
    max_std_x = 40
    max_std_z = 100

    red = (1, 0.2, 0.2, 1)

    def __init__(self, Messaging, queue, User):
        super().__init__(Messaging, queue, User)

        # Save the spine_base and spine_shoulder position for the last 20 frames
        self.pos_spine_base = deque([[0,0,0]] * self.timeseries_length, maxlen=self.timeseries_length)
        self.pos_spine_shoulder = deque([[0,0,0]] * self.timeseries_length, maxlen=self.timeseries_length)

        self.joints = []
        self.bones = []

        self.__reset_variables()

    def __reset_variables(self):
        self.ready_to_squat = False
        self.squatting = False
        self.squat_completed = False
        self.just_finished_squat = False

        self.starting_spine_shoulder_pos = []
        self.starting_spine_base_pos = []

        # Used to check direction (up or down) every frame
        self.last_distance_in_y = 0

        self.repetitions = 0

        self.User.update_user_state_and_stage(USER_STATE.NONE, SQUAT_STAGE.NONE)

    def mirror_started(self):
        super().mirror_started()
        self.__reset_variables()

    def user_skeleton_updated(self, user):
        super().user_skeleton_updated(user)

        # Get the relevant joints and save them
        self.joints = user.get_joints()
        self.bones = user.get_bones()
        spine_shoulder = self.joints[KINECT_JOINTS.SpineShoulder.name]
        spine_base = self.joints[KINECT_JOINTS.SpineBase.name]
        spine_mid = self.joints[KINECT_JOINTS.SpineMid.name]

        self.pos_spine_base.append(spine_base)
        self.pos_spine_shoulder.append(spine_shoulder)

        if self.is_standing_still():

            # Start of a squat-series - get ready for it
            if self.knees_are_straight() and not self.ready_to_squat:
                # Calculate user specific measurements
                if self.threshold_movement_in_y is None:
                    self.threshold_movement_in_y = (spine_shoulder[1] - spine_base[1]) / 5

                # Set initial squat variables
                self.ready_to_squat = True
                self.starting_spine_shoulder_pos = spine_shoulder
                self.starting_spine_base_pos = spine_base


            if self.ready_to_squat:
                # Moving down -> SQUAT STARTED
                if (self.starting_spine_shoulder_pos[1] - spine_shoulder[1]) > self.threshold_movement_in_y:
                    # print("[RecognizeSquatModule][info] Squatting")
                    self.squatting = True
                    self.just_finished_squat = False
                    self.send_to_mirror("squat_text", "Squatting...")
                    self.User.update_user_state_and_stage(USER_STATE.SQUATTING, SQUAT_STAGE.NONE)

                # Determine squat direction
                if self.squatting:
                    current_distance_in_y = self.starting_spine_shoulder_pos[1] - spine_shoulder[1]
                    if (self.last_distance_in_y < current_distance_in_y):
                        self.User.update_user_state_and_stage(USER_STATE.SQUATTING, SQUAT_STAGE.GOING_DOWN)
                    else:
                        self.User.update_user_state_and_stage(USER_STATE.SQUATTING, SQUAT_STAGE.GOING_UP)

                # After moving down, moved back up and knees are straight -> SQUAT COMPLETE
                # print(abs(self.starting_spine_shoulder_pos[1] - spine_shoulder[1]))
                if not self.just_finished_squat and self.squatting and self.knees_are_straight() and abs(self.starting_spine_shoulder_pos[1] - spine_shoulder[1]) < self.threshold_equal_y_pos:
                        self.just_finished_squat = True
                        self.repetitions += 1

                        # Reset squat variables
                        self.starting_spine_shoulder_pos = spine_shoulder
                        self.starting_spine_base_pos = spine_base

                        self.send_to_mirror("squat_repetitions", "Repetitions: {}".format(self.repetitions))

                # Save the current distance to the initial spine position
                self.last_distance_in_y = self.starting_spine_shoulder_pos[1] - spine_shoulder[1]

        elif self.squatting:
            # Walked away
            print("[RecognizeSquatModule][info] Walked away")
            self.repetitions = 0
            self.ready_to_squat = False
            self.squatting = False
            self.standing_straight = False
            self.send_to_mirror("squat_repetitions", "Repetitions: {}".format(self.repetitions), stay=1)
            self.send_to_mirror("squat_text", "Squat failed, you walked - resetting", self.red, stay=1)

            self.User.update_user_state_and_stage(USER_STATE.NONE, SQUAT_STAGE.NONE)

    # Uses time series data of last x frames to determine if the user was
    # standing in place, ie is ready for a squat. More specifically, we look
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
        right_knee_angle = get_angle_between_bones(self.joints, self.bones, "ThighRight", "ShinRight")
        left_knee_angle = get_angle_between_bones(self.joints, self.bones, "ThighLeft", "ShinLeft")

        return  right_knee_angle < 10 and left_knee_angle < 10

    def tracking_lost(self):
        # print("[RecognizeSquatModule][info] Cleaning up")
        super().tracking_lost()
        self.__reset_variables()
        self.send_to_mirror("squat_repetitions", "", stay=0)
        self.send_to_mirror("squat_text", "", stay=0)

    def send_to_mirror(self, id, text, color=(1, 1, 1, 1), stay=10000):
        if id == "squat_text":
            self.Messaging.send_message(MSG_TO_MIRROR_KEYS.TEXT.name,
                json.dumps({
                 "text": text,
                 "id": id,
                 "position": {"x": 0.03, "y": -0.39},
                 "font_size": 30,
                 "color": color,
                 "animation": {
                     "fade_in": 0.3,
                     "stay": stay,
                     "fade_out": 1}
                 }))
        elif id == "squat_repetitions":
            self.Messaging.send_message(MSG_TO_MIRROR_KEYS.TEXT.name,
                json.dumps({
                 "text": "Repetitions: {}".format(self.repetitions),
                 "id": id,
                 "font_size": 30,
                 "position": {"x": 0.03, "y": -0.45},
                 "animation": {
                     "fade_in": 0.5,
                     "stay": stay,
                     "fade_out": 1}
                }))
