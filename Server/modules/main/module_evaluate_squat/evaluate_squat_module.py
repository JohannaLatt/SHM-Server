from Server.modules.abstract_mirror_module import AbstractMirrorModule

from Server.user import USER_STATE, SQUAT_STAGE

from Server.utils.enums import MSG_TO_MIRROR_KEYS, KINECT_JOINTS, KINECT_BONES
from Server.utils.utils import angle_between, lerp_hsv, get_angle_between_bones

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

    def show_knee_angles(self):
        # Calculate the angle between the thigh and shin
        right_knee_angle = get_angle_between_bones(self.joints, self.bones, KINECT_BONES.ThighRight, KINECT_BONES.ShinRight)
        self.show_message_at_joint(right_knee_angle, KINECT_JOINTS.KneeRight.name)

        left_knee_angle = get_angle_between_bones(self.joints, self.bones, KINECT_BONES.ThighLeft, KINECT_BONES.ShinLeft)
        self.show_message_at_joint(left_knee_angle, KINECT_JOINTS.KneeLeft.name)

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

    # The shoulders should be pushed out and the user shouldn't round his neck
    def check_straight_shoulders(self):
        # Calculate the angle between the sholder and the left shoulder
        # right_knee_angle = get_angle_between_bones(self.joints, self.bones, "ThighRight", "ShinRight")
        #self.show_message_at_joint(right_knee_angle, "KneeRight")

        #left_knee_angle = get_angle_between_bones(self.joints, self.bones, "ThighLeft", "ShinLeft")
        #self.show_message_at_joint(left_knee_angle, "KneeLeft")
        pass

    def check_body_behind_toes(self):
        pass

    def check_facing_forward(self):
        pass

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
