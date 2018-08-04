from Server.modules.abstract_main_module import AbstractMainModule

from Server.user import USER_STATE, EXERCISE, UP_DOWN_EXERCISE_STAGE

from Server.utils.enums import USER_JOINTS, KINECT_BONES
from Server.utils.utils import get_angle_between_bones

from collections import deque


class RecognizeSquatModule(AbstractMainModule):

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
        self.last_y_positions = deque(maxlen=self.timeseries_length)

        self.repetitions = 0

    def mirror_started(self):
        super().mirror_started()
        self.__reset_variables()

    def user_state_updated(self, user):
        super().user_state_updated(user)

        if user.get_user_state() is USER_STATE.READY_TO_EXERCISE and not self.ready_to_squat:
            self.joints = user.get_joints()
            self.bones = user.get_bones()

            # Set initial squat variables
            self.starting_spine_shoulder_pos = self.joints[USER_JOINTS.SpineShoulder.name]
            self.starting_spine_base_pos = self.joints[USER_JOINTS.SpineBase.name]

            # Calculate user specific measurements
            if self.threshold_movement_in_y is None:
                self.threshold_movement_in_y = (self.starting_spine_shoulder_pos[1] - self.starting_spine_base_pos[1]) / 5


            self.ready_to_squat = True
        elif user.get_user_state() is USER_STATE.NONE and self.squatting:
            # Walked away
            print("[RecognizeSquatModule][info] Walked away")

            self.ready_to_squat = False
            self.squatting = False

            if self.repetitions > 0:
                self.send_to_mirror("exercise_repetitions", "Repetitions: {}".format(self.repetitions), stay=1)
                self.repetitions = 0

    def user_skeleton_updated(self, user):
        super().user_skeleton_updated(user)

        # Get the relevant joints and save them
        self.joints = user.get_joints()
        self.bones = user.get_bones()
        spine_shoulder = self.joints[USER_JOINTS.SpineShoulder.name]
        spine_base = self.joints[USER_JOINTS.SpineBase.name]
        spine_mid = self.joints[USER_JOINTS.SpineMid.name]

        self.pos_spine_base.append(spine_base)
        self.pos_spine_shoulder.append(spine_shoulder)

        if user.get_user_state() is USER_STATE.READY_TO_EXERCISE or (user.get_user_state() is USER_STATE.EXERCISING and user.get_exercise() is EXERCISE.SQUAT):

            if self.ready_to_squat:
                # Moving down -> SQUAT STARTED
                if (self.starting_spine_shoulder_pos[1] - spine_shoulder[1]) > self.threshold_movement_in_y:
                    # print("[RecognizeSquatModule][info] Squatting")
                    self.squatting = True
                    self.just_finished_squat = False
                    self.send_to_mirror("exercise_status_text", "Squatting...")
                    self.User.update_exercise(EXERCISE.SQUAT)
                    self.User.update_exercise_stage(UP_DOWN_EXERCISE_STAGE.GOING_DOWN)

                # Determine squat direction
                if self.squatting:
                    percent_moved_up = self.percent_moved_up(spine_shoulder[1])
                    if self.User.get_exercise_stage is UP_DOWN_EXERCISE_STAGE.GOING_DOWN and percent_moved_up > 0.7:
                        self.User.update_exercise_stage(UP_DOWN_EXERCISE_STAGE.GOING_UP)
                    elif self.User.get_exercise_stage is UP_DOWN_EXERCISE_STAGE.GOING_UP and percent_moved_up < 0.3:
                        self.User.update_exercise_stage(UP_DOWN_EXERCISE_STAGE.GOING_DOWN)

                # After moving down, moved back up and knees are straight -> SQUAT COMPLETE
                # print(abs(self.starting_spine_shoulder_pos[1] - spine_shoulder[1]))
                if not self.just_finished_squat and self.squatting and self.knees_are_straight() and abs(self.starting_spine_shoulder_pos[1] - spine_shoulder[1]) < self.threshold_equal_y_pos:
                    self.just_finished_squat = True
                    self.repetitions += 1

                    # Reset squat variables
                    self.starting_spine_shoulder_pos = spine_shoulder
                    self.starting_spine_base_pos = spine_base

                    self.send_to_mirror("exercise_repetitions", "Repetitions: {}".format(self.repetitions))
                    self.User.user_finished_repetition()

                # Save the current distance to the initial spine position
                self.last_y_positions.append(spine_shoulder[1])

    def percent_moved_up(self, current_y_pos):
        moved_up = 0
        for y_pos in self.last_y_positions:
            if current_y_pos > y_pos:
                moved_up += 1
        return moved_up / len(self.last_y_positions)

    def knees_are_straight(self):
        right_knee_angle = get_angle_between_bones(self.joints, self.bones, KINECT_BONES.ThighRight, KINECT_BONES.ShinRight)
        left_knee_angle = get_angle_between_bones(self.joints, self.bones, KINECT_BONES.ThighLeft, KINECT_BONES.ShinLeft)

        return  right_knee_angle < 20 and left_knee_angle < 20

    def tracking_lost(self):
        # print("[RecognizeSquatModule][info] Cleaning up")
        super().tracking_lost()
        self.__reset_variables()
        self.send_to_mirror("exercise_repetitions", "", stay=0)
        self.send_to_mirror("exercise_status_text", "", stay=0)

    def send_to_mirror(self, id, text, color=(1, 1, 1, 1), stay=10000):
        if id == "exercise_status_text":
            self.Messaging.send_text_to_mirror(text, id=id, position={"x": 0.03, "y": -0.39}, font_size=30, color=color, fade_in=0.3, stay=stay, fade_out=1, halign="left")
        elif id == "exercise_repetitions":
            self.Messaging.send_text_to_mirror("Repetitions: {}".format(self.repetitions), id=id, position={"x": 0.03, "y": -0.45}, font_size=30, color=color, fade_in=0.5, stay=stay, fade_out=1, halign="left")
