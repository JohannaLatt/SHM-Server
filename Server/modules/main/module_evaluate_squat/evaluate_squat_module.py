from Server.modules.abstract_mirror_module import AbstractMirrorModule

from Server.user import USER_STATE, SQUAT_STAGE

from Server.utils.enums import MSG_TO_MIRROR_KEYS, KINECT_JOINTS, KINECT_BONES
from Server.utils.utils import angle_between, lerp_hsv, get_angle_between_bones, get_vector_of_bone

import json
import numpy as np
from collections import deque
import configparser


class EvaluateSquatModule(AbstractMirrorModule):

    timeseries_length = 10

    def __init__(self, Messaging, queue, User):
        super().__init__(Messaging, queue, User)
        self.evaluating = False

        # Config
        Config = configparser.ConfigParser()
        Config.read('././config/mirror_config.ini')

        # Colors
        self.color_wrong = (0, .7, 1, .7)       # red
        self.color_correct = (.33, .7, 1, .7)   # green

        # Shoulder data
        self.text_id_shoulder_1 = "shoulder_evaluation_1"
        self.text_id_shoulder_2 = "shoulder_evaluation_2"
        self.shoulder_left_angle_over_time = deque(maxlen=self.timeseries_length)
        self.shoulder_right_angle_over_time = deque(maxlen=self.timeseries_length)
        self.shoulder_left_warning = False
        self.shoulder_right_warning = False
        self.rounded_shoulder_warning_angle = Config.getint("EvaluateSquatModule", 'rounded_shoulder_warning_angle', fallback=20)

        # Knee angle data
        self.text_id_knees = "knee_evaluation"
        self.text_id_knees_min_1 = "knee_min_evaluation_1"
        self.text_id_knees_min_2 = "knee_min_evaluation_2"
        self.repetitions_until_check = Config.getint("EvaluateSquatModule", 'repetitions_until_check', fallback=4)
        self.max_knee_angle_for_warning = Config.getint("EvaluateSquatModule", 'max_knee_angle_for_warning', fallback=90)
        self.min_knee_angle_in_current_rep = 180
        self.min_knee_angle_over_time = deque(maxlen=self.repetitions_until_check)
        self.show_knee_color_and_angle = False

    def user_skeleton_updated(self, user):
        super().user_skeleton_updated(user)

        # Check if the user is currently doing a squat
        if user.get_user_state() is USER_STATE.SQUATTING:
            self.evaluating = True

            self.joints = user.get_joints()
            self.bones = user.get_bones()

            if len(self.joints) == 0 or len(self.bones) == 0:
                pass   # Data not ready yet

            self.show_knee_angles()
            self.check_straight_shoulders()
            self.check_body_behind_toes()
            self.check_facing_forward()

        elif self.evaluating:
            self.clean_UI()
            self.reset_skeleton_color()
            self.reset_variables()

    def user_finished_repetition(self, user):
        # Save the maximum angle the user reached in this rep
        self.min_knee_angle_over_time.append(self.min_knee_angle_in_current_rep)
        self.min_knee_angle_in_current_rep = 180

        # See if the user continuously does not go low (check that after every
        # x repetitions)
        if user.get_current_repetitions() % self.repetitions_until_check != 0:
            return

        average_min_knee_angle = int(np.mean(np.asarray(self.min_knee_angle_over_time)))
        if average_min_knee_angle > self.max_knee_angle_for_warning:
            self.Messaging.send_text_to_mirror("Your average knee angle is only {}°".format(average_min_knee_angle), self.text_id_knees_min_1, position={"x":-0.02, "y":-0.30}, stay=3, halign="right")
            self.Messaging.send_text_to_mirror("Try and go lower! ", self.text_id_knees_min_2, position={"x":-0.02, "y":-0.36}, stay=3, halign="right")

    def tracking_lost(self):
        print("[EvaluateSquatModule][info] Cleaning up")
        super().tracking_lost()
        self.clean_UI()
        self.reset_skeleton_color()
        self.reset_variables()

    def reset_variables(self):
        self.shoulder_left_angle_over_time.clear()
        self.shoulder_right_angle_over_time.clear()
        self.min_knee_angle_over_time.clear()
        self.min_knee_angle_in_current_rep = 180

    def clean_UI(self):
        self.hide_message_at_joint(KINECT_JOINTS.KneeRight.name)
        self.hide_message_at_joint(KINECT_JOINTS.KneeLeft.name)
        self.hide_message_at_joint(KINECT_JOINTS.ShoulderLeft.name)
        self.hide_message_at_joint(KINECT_JOINTS.ShoulderRight.name)
        self.Messaging.hide_text_message(self.text_id_shoulder_1)
        self.Messaging.hide_text_message(self.text_id_shoulder_2)
        self.Messaging.hide_text_message(self.text_id_knees)
        self.Messaging.hide_text_message(self.text_id_knees_min_1)
        self.Messaging.hide_text_message(self.text_id_knees_min_2)
        self.evaluating = False

    def reset_skeleton_color(self):
        self.change_joint_or_bone_color('bone', KINECT_BONES.ThighLeft.name, '')
        self.change_joint_or_bone_color('bone', KINECT_BONES.ShinLeft.name, '')
        self.change_joint_or_bone_color('joint', KINECT_JOINTS.KneeLeft.name, '')

        self.change_joint_or_bone_color('bone', KINECT_BONES.ThighRight.name, '')
        self.change_joint_or_bone_color('bone', KINECT_BONES.ShinRight.name, '')
        self.change_joint_or_bone_color('joint', KINECT_JOINTS.KneeRight.name, '')

        self.reset_shoulder_color()

    def reset_shoulder_color(self):
        self.change_joint_or_bone_color('joint', KINECT_JOINTS.SpineShoulder.name, '')
        self.change_joint_or_bone_color('bone', KINECT_BONES.ClavicleLeft.name, '')
        self.change_joint_or_bone_color('joint', KINECT_JOINTS.ShoulderLeft.name, '')
        self.change_joint_or_bone_color('bone', KINECT_BONES.ClavicleRight.name, '')
        self.change_joint_or_bone_color('joint', KINECT_JOINTS.ShoulderRight.name, '')

    def show_knee_angles(self):
        # Calculate the angle between the thigh and shin
        right_knee_angle = 180 - int(get_angle_between_bones(self.joints, self.bones, KINECT_BONES.ThighRight, KINECT_BONES.ShinRight))
        left_knee_angle = 180 - int(get_angle_between_bones(self.joints, self.bones, KINECT_BONES.ThighLeft, KINECT_BONES.ShinLeft))

        # Sanity check
        if right_knee_angle == 0 or left_knee_angle == 0:
            return

        if right_knee_angle < 130 or left_knee_angle < 130:
            self.show_knee_color_and_angle = True

            # Show angles
            self.show_message_at_joint(str(right_knee_angle) + "°", KINECT_JOINTS.KneeRight.name)
            self.show_message_at_joint(str(left_knee_angle) + "°", KINECT_JOINTS.KneeLeft.name)

            # Show colored feedback
            left_color = self.get_color_at_knee_angle(left_knee_angle, 70, 130)
            self.change_joint_or_bone_color('bone', KINECT_BONES.ThighLeft.name, left_color)
            self.change_joint_or_bone_color('bone', KINECT_BONES.ShinLeft.name, left_color)
            self.change_joint_or_bone_color('joint', KINECT_JOINTS.KneeLeft.name, left_color)

            right_color = self.get_color_at_knee_angle(right_knee_angle, 70, 130)
            self.change_joint_or_bone_color('bone', KINECT_BONES.ThighRight.name, right_color)
            self.change_joint_or_bone_color('bone', KINECT_BONES.ShinRight.name, right_color)
            self.change_joint_or_bone_color('joint', KINECT_JOINTS.KneeRight.name, right_color)
        elif self.show_knee_color_and_angle:
            self.show_knee_color_and_angle = False

            self.hide_message_at_joint(KINECT_JOINTS.KneeRight.name)
            self.hide_message_at_joint(KINECT_JOINTS.KneeLeft.name)

            self.change_joint_or_bone_color('bone', KINECT_BONES.ThighLeft.name, '')
            self.change_joint_or_bone_color('bone', KINECT_BONES.ShinLeft.name, '')
            self.change_joint_or_bone_color('joint', KINECT_JOINTS.KneeLeft.name, '')
            self.change_joint_or_bone_color('bone', KINECT_BONES.ThighRight.name, '')
            self.change_joint_or_bone_color('bone', KINECT_BONES.ShinRight.name, '')
            self.change_joint_or_bone_color('joint', KINECT_JOINTS.KneeRight.name, '')

        # Save the angle over time
        angle_over_time = np.mean([right_knee_angle, left_knee_angle])
        if angle_over_time < self.min_knee_angle_in_current_rep:
            self.min_knee_angle_in_current_rep = angle_over_time


    def get_color_at_knee_angle(self, angle, angle_min, angle_max):
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
        return lerp_hsv(self.color_correct, self.color_wrong, t)

    # The shoulders should be pushed out and the user shouldn't round his shoulders
    def check_straight_shoulders(self):
        x_axis = (1, 0, 0)

        # Calculate the angle of the left shoulder
        left_shoulder_angle = self.clean_angle(angle_between(x_axis, get_vector_of_bone(self.joints, self.bones, KINECT_BONES.ClavicleLeft)))
        self.shoulder_left_angle_over_time.append(left_shoulder_angle)
        # Find out whether the angle is in front of the use (ie rounded shoulders)
        # or behind the user (ie open shoulders)
        left_in_front_of_user = self.joints[KINECT_JOINTS.ShoulderLeft.name][2] < self.joints[KINECT_JOINTS.SpineShoulder.name][2]
        left_shoulder_okay = False

        # Calculate the angle of the right shoulder
        right_shoulder_angle =  self.clean_angle(angle_between(x_axis, get_vector_of_bone(self.joints, self.bones, KINECT_BONES.ClavicleRight)))
        if right_shoulder_angle > 90:
            right_shoulder_angle = 180 - right_shoulder_angle
        self.shoulder_right_angle_over_time.append(right_shoulder_angle)
        right_in_front_of_user = self.joints[KINECT_JOINTS.ShoulderRight.name][2] < self.joints[KINECT_JOINTS.SpineShoulder.name][2]
        right_shoulder_okay = False

        if len(self.shoulder_left_angle_over_time) < self.timeseries_length:
            # not enough data yet
            return

        if np.mean(np.asarray(self.shoulder_left_angle_over_time)) > self.rounded_shoulder_warning_angle and left_in_front_of_user:
            self.show_message_at_joint(str(left_shoulder_angle) + "°", KINECT_JOINTS.ShoulderLeft.name)

            if not self.shoulder_left_warning:
                self.shoulder_left_warning = True

                # Shoulders aren't straight over period of 10 frames, show color
                self.change_joint_or_bone_color('joint', KINECT_JOINTS.SpineShoulder.name, self.color_wrong)
                self.change_joint_or_bone_color('bone', KINECT_BONES.ClavicleLeft.name, self.color_wrong)
                self.change_joint_or_bone_color('joint', KINECT_JOINTS.ShoulderLeft.name, self.color_wrong)

                self.Messaging.send_text_to_mirror("Make sure to push your shoulders back,", self.text_id_shoulder_1, position={"x":-0.02, "y":0.41}, stay=3, halign="right")
                self.Messaging.send_text_to_mirror("right now they are rounded!", self.text_id_shoulder_2, position={"x":-0.02, "y":0.35}, stay=3, halign="right")
        else:
            left_shoulder_okay = True

        if np.mean(np.asarray(self.shoulder_right_angle_over_time)) > self.rounded_shoulder_warning_angle and right_in_front_of_user:
            self.show_message_at_joint(str(right_shoulder_angle) + "°", KINECT_JOINTS.ShoulderRight.name)

            if not self.shoulder_right_warning:
                self.shoulder_right_warning = True

                # Shoulders aren't straight over period of 10 frames, show color
                self.change_joint_or_bone_color('joint', KINECT_JOINTS.SpineShoulder.name, self.color_wrong)
                self.change_joint_or_bone_color('bone', KINECT_BONES.ClavicleRight.name, self.color_wrong)
                self.change_joint_or_bone_color('joint', KINECT_JOINTS.ShoulderRight.name, self.color_wrong)

                self.Messaging.send_text_to_mirror("Make sure to push your shoulders back,", self.text_id_shoulder_1, position={"x":-0.02, "y":0.41}, stay=3, halign="right")
                self.Messaging.send_text_to_mirror("right now they are rounded!", self.text_id_shoulder_2, position={"x":-0.02, "y":0.35}, stay=3, halign="right")
        else:
            right_shoulder_okay = True

        # Cleanup
        if left_shoulder_okay and right_shoulder_okay and self.shoulder_left_warning and self.shoulder_right_warning:
            if self.shoulder_left_warning and self.shoulder_right_warning:
                self.change_joint_or_bone_color('joint', KINECT_JOINTS.SpineShoulder.name, '')

        if left_shoulder_okay and self.shoulder_left_warning:
            self.hide_message_at_joint(KINECT_JOINTS.ShoulderLeft.name)
            self.change_joint_or_bone_color('bone', KINECT_BONES.ClavicleLeft.name, '')
            self.change_joint_or_bone_color('joint', KINECT_JOINTS.ShoulderLeft.name, '')

        if right_shoulder_okay and self.shoulder_right_warning:
            self.hide_message_at_joint(KINECT_JOINTS.ShoulderRight.name)
            self.change_joint_or_bone_color('bone', KINECT_BONES.ClavicleRight.name, '')
            self.change_joint_or_bone_color('joint', KINECT_JOINTS.ShoulderRight.name, '')

        if left_shoulder_okay:
            self.shoulder_left_warning = False

        if right_shoulder_okay:
            self.shoulder_right_warning = False

    def check_body_behind_toes(self):
        pass

    def check_facing_forward(self):
        pass

    def clean_angle(self, angle):
        if angle > 90:
            angle = 180 - angle
        return int(angle)

    def show_message_at_joint(self, text, joint):
        self.Messaging.send_message(MSG_TO_MIRROR_KEYS.TEXT.name,
            json.dumps({
             "text": text,
             "id": joint,
             "font_size": 30,
             "position": joint,
             "animation": {
                 "fade_in": 0.5,
                 "stay": 1000,
                 "fade_out": 1}
            }))

    def hide_message_at_joint(self, joint):
        self.Messaging.send_message(MSG_TO_MIRROR_KEYS.TEXT.name,
            json.dumps({
                "text": "",
                "id": joint,
                "position": joint
            }))

    def change_joint_or_bone_color(self, type, name, color):
        self.Messaging.send_message(MSG_TO_MIRROR_KEYS.CHANGE_SKELETON_COLOR.name,
            json.dumps({
                "type": type,
                "name": name,
                "color": color
            }))
