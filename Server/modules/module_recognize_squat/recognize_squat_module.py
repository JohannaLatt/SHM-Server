from Server.modules.abstract_mirror_module import AbstractMirrorModule
from Server.utils.enums import KINECT_JOINTS
from Server.utils.enums import MSG_TO_MIRROR_KEYS

from Server.utils.user import USER_STATE
from Server.utils.user import SQUAT_STAGE

import json


class RecognizeSquatModule(AbstractMirrorModule):

    threshold_straight_x = 30
    threshold_straight_z = 70

    threshold_straight_squatting_x = 60

    threshold_in_place_x = 250
    threshold_in_place_z = 400
    threshold_equal_y_pos = 20
    threshold_movement_in_y = 80

    def __init__(self, Messaging, queue, User):
        super().__init__(Messaging, queue, User)
        self.__reset_variables()

    def __reset_variables(self):
        self.standing_straight = False
        self.squatting = False
        self.squat_completed = False
        self.just_finished_squat = False

        self.starting_spine_shoulder_pos = []
        self.starting_spine_base_pos = []

        # Used to check direction (up or down) every frame
        self.last_distance_in_y = 0

        self.repetitions = 0

        self.red = (1, 0.2, 0.2, 1)

    def mirror_started(self):
        super().mirror_started()
        # do nothing with that
        pass

    def tracking_started(self):
        super().tracking_started()
        pass

    def tracking_data(self, data):
        super().tracking_data(data)

        data = json.loads(data)["joint_data"]

        # Get the relevant joints
        spine_shoulder = data[KINECT_JOINTS.SpineShoulder.name]["joint_position"]
        spine_base = data[KINECT_JOINTS.SpineBase.name]["joint_position"]
        spine_mid = data[KINECT_JOINTS.SpineMid.name]["joint_position"]

        # Check if READY FOR SQUAT
        if self.is_upper_body_straight(spine_shoulder, spine_mid, spine_base) and not self.standing_straight:
            self.standing_straight = True
            self.starting_spine_shoulder_pos = spine_shoulder
            self.starting_spine_base_pos = spine_base

        if self.standing_straight:
            # Check for walking away
            if (self.squatting and
            (abs(self.starting_spine_base_pos["x"] - spine_base["x"]) > self.threshold_in_place_x or
            abs(self.starting_spine_base_pos["z"] - spine_base["z"]) > self.threshold_in_place_z)):
                self.repetitions = 0
                self.squatting = False
                self.standing_straight = False
                self.send_to_mirror("squat_repetitions", "Repetitions: {}".format(self.repetitions), stay=1)
                self.send_to_mirror("squat_text", "Squat failed, you walked - resetting", self.red, stay=1)

                self.User.update_user_state(USER_STATE.NONE)
                self.User.update_exercise_state(SQUAT_STAGE.NONE)

            # Check for straight back
            elif self.is_upper_body_straight_during_squat(spine_shoulder, spine_mid, spine_base):
                # Moving down -> SQUAT STARTED
                if (self.starting_spine_shoulder_pos["y"] - spine_shoulder["y"]) > self.threshold_movement_in_y:
                    self.squatting = True
                    self.just_finished_squat = False
                    self.send_to_mirror("squat_text", "You are doing squats - keep on going!")
                    self.User.update_user_state(USER_STATE.SQUATTING)

                # Determine squat direction
                if self.squatting:
                    current_distance_in_y = self.starting_spine_shoulder_pos["y"] - spine_shoulder["y"]
                    if (self.last_distance_in_y < current_distance_in_y):
                        self.User.update_exercise_state(SQUAT_STAGE.GOING_DOWN)
                    else:
                        self.User.update_exercise_state(SQUAT_STAGE.GOING_UP)

                # After moving down, moved back up -> SQUAT COMPLETE
                if not self.just_finished_squat and self.squatting and abs(self.starting_spine_shoulder_pos["y"] - spine_shoulder["y"]) < self.threshold_equal_y_pos:
                    self.just_finished_squat = True
                    self.repetitions += 1
                    self.send_to_mirror("squat_repetitions", "Repetitions: {}".format(self.repetitions))

            # SQUAT FAILED
            else:
                self.squatting = False
                self.standing_straight = False
                self.repetitions = 0
                self.send_to_mirror("squat_text", "Squat failed, your back has to be straight - resetting", self.red, stay=1)
                self.send_to_mirror("squat_repetitions", "Repetitions: {}".format(self.repetitions), stay=1)

                self.User.update_user_state(USER_STATE.NONE)
                self.User.update_exercise_state(SQUAT_STAGE.NONE)

            # Save the current distance to the initial spine position
            self.last_distance_in_y = self.starting_spine_shoulder_pos["y"] - spine_shoulder["y"]

    def send_to_mirror(self, id, text, color=(1, 1, 1, 1), stay=10000):
        if id == "squat_text":
            self.Messaging.send_message(MSG_TO_MIRROR_KEYS.STATIC_TEXT.name,
                json.dumps({
                 "text": text,
                 "id": id,
                 "position": (0.5, 0.8),
                 "color": color,
                 "animation": {
                     "fade_in": 0.3,
                     "stay": stay,
                     "fade_out": 1}
                 }))
        elif id == "squat_repetitions":
            self.Messaging.send_message(MSG_TO_MIRROR_KEYS.STATIC_TEXT.name,
                json.dumps({
                 "text": "Repetitions: {}".format(self.repetitions),
                 "id": id,
                 "position": (0.1, 0.1),
                 "animation": {
                     "fade_in": 0.5,
                     "stay": stay,
                     "fade_out": 1}
                }))

    # Checks if the upper body is straight while the user is not moving
    def is_upper_body_straight(self, spine_shoulder, spine_mid, spine_base):
        if (abs(spine_shoulder["x"] - spine_mid["x"]) < self.threshold_straight_x
        and abs(spine_mid["x"] - spine_base["x"]) < self.threshold_straight_x
        and abs(spine_shoulder["z"] - spine_mid["z"]) < self.threshold_straight_z
        and abs(spine_mid["z"] - spine_base["z"]) < self.threshold_straight_z):
            return True
        return False

    # Checks if the upper body stays straight during a squat - has some more
    # wiggle room than is_upper_body_straight since this method is intended
    # to be used DURING a movement (so there is some natural shacking). It also
    # only checks x since z should actually move during a squat.
    def is_upper_body_straight_during_squat(self, spine_shoulder, spine_mid, spine_base):
        if (abs(spine_shoulder["x"] - spine_mid["x"]) < self.threshold_straight_squatting_x
        and abs(spine_mid["x"] - spine_base["x"]) < self.threshold_straight_squatting_x):
            return True
        return False

    def tracking_lost(self):
        super().tracking_lost()
        self.__reset_variables()
        self.send_to_mirror("squat_repetitions", "", 0)
        self.send_to_mirror("squat_text", "", 0)
