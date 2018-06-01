from Server.modules.abstract_mirror_module import AbstractMirrorModule
from Server.utils.enums import KINECT_JOINTS
from Server.utils.enums import MSG_TO_MIRROR_KEYS

import json


class RecognizeSquatModule(AbstractMirrorModule):

    threshold_straight_x = 30
    threshold_straight_z = 70

    threshold_straight_squatting_x = 60

    threshold_in_place_x = 140
    threshold_equal_y_pos = 20
    threshold_movement_in_y = 40

    def __init__(self, Messaging, queue):
        super().__init__(Messaging, queue)
        self.__reset_variables()

    def __reset_variables(self):
        self.squat_started = False
        self.squatting = False
        self.squat_completed = False

        self.starting_spine_shoulder_pos = []
        self.starting_spine_base_pos = []
        self.last_spine_shoulder_pos = []
        self.last_spine_base_pos = []

        self.repetitions = 0

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

        if self.is_upper_body_straight(spine_shoulder, spine_mid, spine_base) and not self.squat_started:
            print("SQUAT STARTED")
            self.squat_started = True
            self.starting_spine_shoulder_pos = spine_shoulder
            self.starting_spine_base_pos = spine_base
            self.last_spine_shoulder_pos = spine_shoulder
            self.last_spine_base_pos = spine_base

        if self.squat_started:
            if self.is_upper_body_straight_during_squat(spine_shoulder, spine_mid, spine_base):
                if (self.starting_spine_shoulder_pos["y"] - spine_shoulder["y"]) > self.threshold_movement_in_y:
                    self.squatting = True
                    self.send_to_mirror("squat_text", "Squatting!! Keep on going!")
                    print("SQUATTING")

                if self.squatting is True and abs(self.starting_spine_shoulder_pos["y"] - spine_shoulder["y"]) < self.threshold_equal_y_pos:
                    # Make sure the person didn't walk/move somewhere else
                    if abs(self.starting_spine_base_pos["x"] - spine_base["x"]) < self.threshold_in_place_x:
                        self.squatting = False
                        self.repetitions += 1
                        print("SQUAT COMPLETE")
                        self.send_to_mirror("squat_repetitions", "Repetitions: {}".format(self.repetitions))

                    else:
                        print("SQUAT FAILED - walked away")
                        self.send_to_mirror("squat_text", "Squat failed, you walked - resetting", 2)
                        self.squatting = False
                        self.squat_started = False
                        self.repetitions = 0
                        self.send_to_mirror("squat_repetitions", "Repetitions: {}".format(self.repetitions), 1)

                self.last_spine_shoulder_pos = spine_shoulder
            else:
                print("SQUAT FAILED - not straight")
                self.send_to_mirror("squat_text", "Squat failed, your back has to be straight - resetting", 2)
                self.squatting = False
                self.squat_started = False
                self.repetitions = 0
                self.send_to_mirror("squat_repetitions", "Repetitions: {}".format(self.repetitions), 1)

        self.last_spine_base = spine_base

    def send_to_mirror(self, id, text, stay=10000):
        if id == "squat_text":
            self.Messaging.send_message(MSG_TO_MIRROR_KEYS.STATIC_TEXT.name,
                json.dumps({
                 "text": text,
                 "id": id,
                 "position": (0.5, 0.8),
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
        print("Not straight")
        return False

    def tracking_lost(self):
        super().tracking_lost()
        self.__reset_variables()
        self.send_to_mirror("squat_repetitions", "", 0)
        self.send_to_mirror("squat_text", "", 0)
