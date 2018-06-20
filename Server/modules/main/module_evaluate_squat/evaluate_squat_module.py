from Server.modules.abstract_mirror_module import AbstractMirrorModule

from Server.user import USER_STATE

from Server.utils.enums import MSG_TO_MIRROR_KEYS
from Server.utils.utils import angle_between, lerp_hsv

import json
import numpy as np


class EvaluateSquatModule(AbstractMirrorModule):

    def __init__(self, Messaging, queue, User):
        super().__init__(Messaging, queue, User)
        self.evaluating = False

        # Colors
        self.color_wrong = (0, .7, 1, .7)       # red
        self.color_correct = (.33, .7, 1, .7)   # green

    def user_exercising_updated(self, user):
        super().user_exercising_updated(user)

        # Check if the user is currently doing a squat
        if user.get_user_state() is USER_STATE.SQUATTING:
            self.evaluating = True

            self.joints = user.get_joints()
            self.bones = user.get_bones()

            if len(self.joints) == 0 or len(self.bones) == 0:
                pass   # Data not ready yet

            # Calculate the angle between the thigh and shin
            left_thigh_vector = self.get_vector_of_bone("ThighRight")
            left_shin_vector = self.get_vector_of_bone("ShinRight")
            left_knee_angle = np.around(angle_between(left_thigh_vector, left_shin_vector), decimals=1)
            self.show_message_at_joint(left_knee_angle, "KneeRight")

            right_thigh_vector = self.get_vector_of_bone("ThighLeft")
            right_shin_vector = self.get_vector_of_bone("ShinLeft")
            right_knee_angle = np.around(angle_between(right_thigh_vector, right_shin_vector), decimals=1)
            self.show_message_at_joint(right_knee_angle, "KneeLeft")

            # Show colored feedback
            left_color = self.get_color_at_knee_angle(left_knee_angle)
            self.change_joint_or_bone_color('bone', 'ThighLeft', left_color)
            self.change_joint_or_bone_color('bone', 'ShinLeft', left_color)
            self.change_joint_or_bone_color('joint', 'KneeLeft', left_color)

            right_color = self.get_color_at_knee_angle(right_knee_angle)
            self.change_joint_or_bone_color('bone', 'ThighRight', right_color)
            self.change_joint_or_bone_color('bone', 'ShinRight', right_color)
            self.change_joint_or_bone_color('joint', 'KneeRight', right_color)

        elif self.evaluating:
            self.clean_UI()
            self.reset_skeleton_color()

    def tracking_lost(self):
        # print("[EvaluateSquatModule][info] Cleaning up")
        super().tracking_lost()
        self.clean_UI()
        self.reset_skeleton_color()

    def clean_UI(self):
        self.hide_message_at_joint("KneeRight")
        self.hide_message_at_joint("KneeLeft")
        self.evaluating = False

    def reset_skeleton_color(self):
        self.change_joint_or_bone_color('bone', 'ThighLeft', '')
        self.change_joint_or_bone_color('bone', 'ShinLeft', '')
        self.change_joint_or_bone_color('joint', 'KneeLeft', '')

        self.change_joint_or_bone_color('bone', 'ThighRight', '')
        self.change_joint_or_bone_color('bone', 'ShinRight', '')
        self.change_joint_or_bone_color('joint', 'KneeRight', '')

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

    def get_vector_of_bone(self, bone):
        return (self.joints[self.bones[bone][0]][0] - self.joints[self.bones[bone][1]][0], # x
                self.joints[self.bones[bone][0]][1] - self.joints[self.bones[bone][1]][1]) # y

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
