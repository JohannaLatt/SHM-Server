from Server.modules.abstract_mirror_module import AbstractMirrorModule

from Server.user import USER_STATE, SQUAT_STAGE

from Server.utils.enums import MSG_TO_MIRROR_KEYS, KINECT_JOINTS, KINECT_BONES
from Server.utils.utils import angle_between, lerp_hsv, get_angle_between_bones, get_vector_of_bone

import json
import numpy as np
from collections import deque


class EvaluateSquatModule(AbstractMirrorModule):

    timeseries_length = 10

    def __init__(self, Messaging, queue, User):
        super().__init__(Messaging, queue, User)
        self.evaluating = False

        # Colors
        self.color_wrong = (0, .7, 1, .7)       # red
        self.color_correct = (.33, .7, 1, .7)   # green

        # Shoulder data
        self.text_id_shoulder = "shoulder_evaluation"
        self.shoulder_left_angle_over_time = deque(maxlen=self.timeseries_length)
        self.shoulder_right_angle_over_time = deque(maxlen=self.timeseries_length)
        self.shoulder_left_warning = False
        self.shoulder_right_warning = False

    def user_exercising_updated(self, user):
        super().user_exercising_updated(user)

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

    def tracking_lost(self):
        print("[EvaluateSquatModule][info] Cleaning up")
        super().tracking_lost()
        self.clean_UI()
        self.reset_skeleton_color()

    def clean_UI(self):
        self.hide_message_at_joint(KINECT_JOINTS.KneeRight.name)
        self.hide_message_at_joint(KINECT_JOINTS.KneeLeft.name)
        self.hide_message_at_joint(KINECT_JOINTS.ShoulderLeft.name)
        self.hide_message_at_joint(KINECT_JOINTS.ShoulderRight.name)
        self.Messaging.hide_text_message(self.text_id_shoulder)
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
        right_knee_angle = int(get_angle_between_bones(self.joints, self.bones, KINECT_BONES.ThighRight, KINECT_BONES.ShinRight))
        self.show_message_at_joint(str(right_knee_angle) + "°", KINECT_JOINTS.KneeRight.name)

        left_knee_angle = int(get_angle_between_bones(self.joints, self.bones, KINECT_BONES.ThighLeft, KINECT_BONES.ShinLeft))
        self.show_message_at_joint(str(left_knee_angle) + "°", KINECT_JOINTS.KneeLeft.name)

        # Show colored feedback
        left_color = self.get_color_at_knee_angle(left_knee_angle)
        self.change_joint_or_bone_color('bone', KINECT_BONES.ThighLeft.name, left_color)
        self.change_joint_or_bone_color('bone', KINECT_BONES.ShinLeft.name, left_color)
        self.change_joint_or_bone_color('joint', KINECT_JOINTS.KneeLeft.name, left_color)

        right_color = self.get_color_at_knee_angle(right_knee_angle)
        self.change_joint_or_bone_color('bone', KINECT_BONES.ThighRight.name, right_color)
        self.change_joint_or_bone_color('bone', KINECT_BONES.ShinRight.name, right_color)
        self.change_joint_or_bone_color('joint', KINECT_JOINTS.KneeRight.name, right_color)

    def get_color_at_knee_angle(self, angle):
        ''' Returns a color between red and green depending
            on the knee's angle - anything greater than 90 degrees is always
            green '''

        # Transform the angle to a value between 0 and 1, everything above 90
        # is always 1
        t = angle / 90
        if t > 1:
            t = 1

        # Calculate the interpolated color
        return lerp_hsv(self.color_wrong, self.color_correct, t)

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

        if np.mean(np.asarray(self.shoulder_left_angle_over_time)) > 20 and left_in_front_of_user:
            self.show_message_at_joint(str(left_shoulder_angle) + "°", KINECT_JOINTS.ShoulderLeft.name)
            if not self.shoulder_left_warning:
                self.shoulder_left_warning = True

                # Shoulders aren't straight over period of 10 frames, show color
                self.change_joint_or_bone_color('joint', KINECT_JOINTS.SpineShoulder.name, self.color_wrong)
                self.change_joint_or_bone_color('bone', KINECT_BONES.ClavicleLeft.name, self.color_wrong)
                self.change_joint_or_bone_color('joint', KINECT_JOINTS.ShoulderLeft.name, self.color_wrong)

                self.Messaging.send_text_to_mirror("Make sure your shoulders are straight and not rounded!", self.text_id_shoulder, position={"x":0, "y":0.35}, stay=3)
        else:
            left_shoulder_okay = True

        if np.mean(np.asarray(self.shoulder_right_angle_over_time)) > 20 and right_in_front_of_user:
            self.show_message_at_joint(str(right_shoulder_angle) + "°", KINECT_JOINTS.ShoulderRight.name)
            if not self.shoulder_right_warning:
                self.shoulder_right_warning = True

                # Shoulders aren't straight over period of 10 frames, show color
                self.change_joint_or_bone_color('joint', KINECT_JOINTS.SpineShoulder.name, self.color_wrong)
                self.change_joint_or_bone_color('bone', KINECT_BONES.ClavicleRight.name, self.color_wrong)
                self.change_joint_or_bone_color('joint', KINECT_JOINTS.ShoulderRight.name, self.color_wrong)

                self.Messaging.send_text_to_mirror("Make sure your shoulders are straight and not rounded!", self.text_id_shoulder, position={"x":0, "y":0.35}, stay=3)
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
