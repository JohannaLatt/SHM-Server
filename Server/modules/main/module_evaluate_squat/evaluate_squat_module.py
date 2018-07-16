from Server.modules.abstract_mirror_module import AbstractMirrorModule

from Server.user import USER_STATE, SQUAT_STAGE

from Server.utils.enums import MSG_TO_MIRROR_KEYS, KINECT_JOINTS, KINECT_BONES
from Server.utils.utils import angle_between, lerp_hsv, get_angle_between_bones, get_vector_of_bone, get_color_at_angle

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

        # Keep track of UI changes to easily clean them if needed
        self.text_ids = set()
        self.colored_bones = set()
        self.colored_joints = set()

        # Shoulder data
        self.rounded_shoulder_warning_angle = Config.getint('EvaluateSquatModule', 'rounded_shoulder_warning_angle', fallback=20)

        self.text_id_shoulder_1 = "shoulder_evaluation_1"
        self.text_id_shoulder_2 = "shoulder_evaluation_2"

        self.shoulder_left_angle_over_time = deque(maxlen=self.timeseries_length)
        self.shoulder_right_angle_over_time = deque(maxlen=self.timeseries_length)

        # Knee angle data
        self.repetitions_until_check = Config.getint('EvaluateSquatModule', 'repetitions_until_check', fallback=4)
        self.max_knee_angle_for_warning = Config.getint('EvaluateSquatModule', 'max_knee_angle_for_warning', fallback=90)

        self.text_id_knees = "knee_evaluation"
        self.text_id_knees_min_1 = "knee_min_evaluation_1"
        self.text_id_knees_min_2 = "knee_min_evaluation_2"

        self.min_knee_angle_in_current_rep = 180
        self.min_knee_angle_over_time = deque(maxlen=self.repetitions_until_check)

        self.showing_knee_warning = False

        # Looking straight ahead
        self.tilted_sideways_head_min_warning_angle = Config.getint('EvaluateSquatModule', 'tilted_sideways_head_min_warning_angle', fallback=85)
        self.tilted_up_down_head_min_warning_angle = Config.getint('EvaluateSquatModule', 'tilted_up_down_head_min_warning_angle', fallback=85)

        self.text_id_straight_1 = "head_evaluation_1"
        self.text_id_straight_2 = "head_evaluation_2"

        self.head_tilted_up_down_over_time = deque(maxlen=self.timeseries_length)
        self.head_tilted_sideways_over_time = deque(maxlen=self.timeseries_length)

        self.showing_head_warning = False

        # Knees behind toes
        self.knee_behind_toes_tolerance = Config.getint('EvaluateSquatModule', 'knee_behind_toes_tolerance', fallback=20)

        self.text_id_knee_toes_1 = "knee_toes_evaluation_1"
        self.text_id_knee_toes_2 = "knee_toes_evaluation_2"

        self.knee_over_toe_left = deque(maxlen=self.timeseries_length)
        self.knee_over_toe_right = deque(maxlen=self.timeseries_length)

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
            self.show_message_at_position("Your average knee angle is only {}°".format(average_min_knee_angle), self.text_id_knees_min_1, position={"x":-0.02, "y":-0.10}, stay=3)
            self.show_message_at_position("Try and go lower! ", self.text_id_knees_min_2, position={"x":-0.02, "y":-0.16}, stay=3)

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
        self.head_tilted_up_down_over_time.clear()
        self.head_tilted_up_down_over_time.clear()
        self.evaluating = False

    def clean_UI(self):
        for text_ids in self.text_ids.copy():
            self.hide_message_at_position(text_ids)

    def reset_skeleton_color(self):
        for colored_bone in self.colored_bones.copy():
            self.change_joint_or_bone_color('bone', colored_bone, '')

        for colored_joint in self.colored_joints.copy():
            self.change_joint_or_bone_color('joint', colored_joint, '')

    def show_knee_angles(self):
        # Calculate the angle between the thigh and shin
        right_knee_angle = 180 - int(get_angle_between_bones(self.joints, self.bones, KINECT_BONES.ThighRight, KINECT_BONES.ShinRight))
        left_knee_angle = 180 - int(get_angle_between_bones(self.joints, self.bones, KINECT_BONES.ThighLeft, KINECT_BONES.ShinLeft))

        # Sanity check
        if right_knee_angle == 0 or left_knee_angle == 0:
            return

        if right_knee_angle < 130 or left_knee_angle < 130:
            self.showing_knee_warning = True

            # Show angles
            self.show_message_at_joint(str(right_knee_angle) + "°", KINECT_JOINTS.KneeRight.name)
            self.show_message_at_joint(str(left_knee_angle) + "°", KINECT_JOINTS.KneeLeft.name)

            # Show colored feedback
            left_color = get_color_at_angle(left_knee_angle, 70, 130, self.color_correct, self.color_wrong)
            self.change_joint_or_bone_color('joint', KINECT_JOINTS.KneeLeft.name, left_color)

            right_color = get_color_at_angle(right_knee_angle, 70, 130, self.color_correct, self.color_wrong)
            self.change_joint_or_bone_color('joint', KINECT_JOINTS.KneeRight.name, right_color)
        elif self.showing_knee_warning:
            self.showing_knee_warning = False

            self.hide_message_at_joint(KINECT_JOINTS.KneeRight.name)
            self.hide_message_at_joint(KINECT_JOINTS.KneeLeft.name)

            self.change_joint_or_bone_color('joint', KINECT_JOINTS.KneeLeft.name, '')
            self.change_joint_or_bone_color('joint', KINECT_JOINTS.KneeRight.name, '')

        # Save the angle over time
        angle_over_time = np.mean([right_knee_angle, left_knee_angle])
        if angle_over_time < self.min_knee_angle_in_current_rep:
            self.min_knee_angle_in_current_rep = angle_over_time

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

        self.shoulder_right_angle_over_time.append(right_shoulder_angle)
        right_in_front_of_user = self.joints[KINECT_JOINTS.ShoulderRight.name][2] < self.joints[KINECT_JOINTS.SpineShoulder.name][2]
        right_shoulder_okay = False

        if len(self.shoulder_left_angle_over_time) < self.timeseries_length:
            # not enough data yet
            return

        # Left shoulder isn't straight over period of 10 frames - show warning
        if np.mean(np.asarray(self.shoulder_left_angle_over_time)) > self.rounded_shoulder_warning_angle and left_in_front_of_user:
            self.show_message_at_joint(str(left_shoulder_angle) + "°", KINECT_JOINTS.ShoulderLeft.name)

            self.change_joint_or_bone_color('joint', KINECT_JOINTS.SpineShoulder.name, self.color_wrong)
            self.change_joint_or_bone_color('bone', KINECT_BONES.ClavicleLeft.name, self.color_wrong)
            self.change_joint_or_bone_color('joint', KINECT_JOINTS.ShoulderLeft.name, self.color_wrong)

            self.show_shoulder_warning()
        else:
            left_shoulder_okay = True

        # Right shoulder isn't straight over period of 10 frames - show warning
        if np.mean(np.asarray(self.shoulder_right_angle_over_time)) > self.rounded_shoulder_warning_angle and right_in_front_of_user:
            self.show_message_at_joint(str(right_shoulder_angle) + "°", KINECT_JOINTS.ShoulderRight.name)

            self.change_joint_or_bone_color('joint', KINECT_JOINTS.SpineShoulder.name, self.color_wrong)
            self.change_joint_or_bone_color('bone', KINECT_BONES.ClavicleRight.name, self.color_wrong)
            self.change_joint_or_bone_color('joint', KINECT_JOINTS.ShoulderRight.name, self.color_wrong)

            self.show_shoulder_warning()
        else:
            right_shoulder_okay = True

        # Cleanup
        if left_shoulder_okay and right_shoulder_okay and KINECT_JOINTS.SpineShoulder.name in self.colored_joints:
            self.change_joint_or_bone_color('joint', KINECT_JOINTS.SpineShoulder.name, '')

        if left_shoulder_okay and KINECT_BONES.ClavicleLeft.name in self.colored_bones:
            self.hide_message_at_joint(KINECT_JOINTS.ShoulderLeft.name)
            self.change_joint_or_bone_color('bone', KINECT_BONES.ClavicleLeft.name, '')
            self.change_joint_or_bone_color('joint', KINECT_JOINTS.ShoulderLeft.name, '')

        if right_shoulder_okay and KINECT_BONES.ClavicleRight.name in self.colored_bones:
            self.hide_message_at_joint(KINECT_JOINTS.ShoulderRight.name)
            self.change_joint_or_bone_color('bone', KINECT_BONES.ClavicleRight.name, '')
            self.change_joint_or_bone_color('joint', KINECT_JOINTS.ShoulderRight.name, '')

    def show_shoulder_warning(self):
        self.show_message_at_position("Make sure to push your shoulders back,", self.text_id_shoulder_1, position={"x":-0.02, "y":0.33}, stay=3)
        self.show_message_at_position("right now they are rounded!", self.text_id_shoulder_2, position={"x":-0.02, "y":0.27}, stay=3)

    # Check whether the user's knees stay above or behind the toes at all times,
    # i.e. the z-component of the knee is always greater than the toes
    def check_body_behind_toes(self):
        # Left leg
        left_knee_behind_toes = self.joints[KINECT_JOINTS.KneeLeft.name][2] + self.knee_behind_toes_tolerance - self.joints[KINECT_JOINTS.FootLeft.name][2]
        self.knee_over_toe_left.append(True) if left_knee_behind_toes < 0 else self.knee_over_toe_left.append(False)
        left_knee_okay = False

        # Right leg
        right_knee_behind_toes = self.joints[KINECT_JOINTS.KneeRight.name][2] + self.knee_behind_toes_tolerance - self.joints[KINECT_JOINTS.FootRight.name][2]
        self.knee_over_toe_right.append(True) if right_knee_behind_toes < 0 else self.knee_over_toe_right.append(False)
        right_knee_okay = False

        if len(self.knee_over_toe_left) < self.timeseries_length:
            # not enough data yet
            return

        # If 70% of the last frames were wrong knee positions...
        if (self.knee_over_toe_left.count(True)/self.timeseries_length) > 0.7:
            left_leg_color = get_color_at_angle(left_knee_behind_toes, -200, 0, self.color_correct, self.color_wrong)
            self.change_left_leg_color(left_leg_color)

            self.show_knee_toe_warning()
        else:
            left_knee_okay = True

        # If 70% of the last frames were wrong knee positions...
        if (self.knee_over_toe_right.count(True)/self.timeseries_length) > 0.7:
            right_leg_color = get_color_at_angle(right_knee_behind_toes, -200, 0, self.color_correct, self.color_wrong)
            self.change_right_leg_color(right_leg_color)

            self.show_knee_toe_warning()
        else:
            right_knee_okay = True

        # Cleanup
        if left_knee_okay and KINECT_BONES.FootLeft.name in self.colored_bones:
            self.change_left_leg_color('')

        if right_knee_okay and KINECT_BONES.FootRight.name in self.colored_bones:
            self.change_right_leg_color('')

    def show_knee_toe_warning(self):
        self.show_message_at_position("Your knee should not be in front", self.text_id_knee_toes_1, position={"x":-0.02, "y":-0.3}, stay=2)
        self.show_message_at_position("of your toes, try and push your hips further out!", self.text_id_knee_toes_2, position={"x":-0.02, "y":-0.36}, stay=2)

    def change_right_leg_color(self, color):
        self.change_joint_or_bone_color('bone', KINECT_BONES.ShinRight.name, color)
        self.change_joint_or_bone_color('bone', KINECT_BONES.FootRight.name, color)
        self.change_joint_or_bone_color('joint', KINECT_JOINTS.AnkleRight.name, color)
        self.change_joint_or_bone_color('joint', KINECT_JOINTS.FootRight.name, color)

    def change_left_leg_color(self, color):
        self.change_joint_or_bone_color('bone', KINECT_BONES.ShinLeft.name, color)
        self.change_joint_or_bone_color('bone', KINECT_BONES.FootLeft.name, color)
        self.change_joint_or_bone_color('joint', KINECT_JOINTS.AnkleLeft.name, color)
        self.change_joint_or_bone_color('joint', KINECT_JOINTS.FootLeft.name, color)


    # Check whether the user is always facing forward which prevents
    # spine pain and damage.
    # For that, the vector through head and neck ideally has to be
    # perpendicualr to the x-axis (head not tilted sideways) and perpendicular
    # to the z-axis (head not tilted up or down)
    def check_facing_forward(self):
        head_vector = get_vector_of_bone(self.joints, self.bones, KINECT_BONES.Head)

        # Check for x-axis perpendicularity
        x_axis = (1, 0, 0)
        tilted_sideways = self.clean_angle(angle_between(x_axis, head_vector))
        if tilted_sideways < self.tilted_up_down_head_min_warning_angle:
            self.head_tilted_sideways_over_time.append(True)
        else:
            self.head_tilted_sideways_over_time.append(False)

        # Check for z-perpendicularity
        y_axis = (0, 0, 1)
        tilted_up_down = self.clean_angle(angle_between(y_axis, head_vector)) + 10
        if tilted_up_down < self.tilted_up_down_head_min_warning_angle:
            self.head_tilted_up_down_over_time.append(True)
        else:
            self.head_tilted_up_down_over_time.append(False)

        if len(self.head_tilted_sideways_over_time) < self.timeseries_length:
            # not enough data yet
            return

        # If 70% of the last frames were wrong head positions...
        if (self.head_tilted_up_down_over_time.count(True)/self.timeseries_length) > 0.7:
            msg = str(90 - tilted_sideways) + "°"
            self.show_message_at_joint(msg, KINECT_JOINTS.Head.name)

            head_color = get_color_at_angle(90 - tilted_sideways, 0, 90 - self.tilted_sideways_head_min_warning_angle + 5, self.color_correct, self.color_wrong)
            self.set_head_color(head_color)

            if not self.showing_head_warning:
                self.showing_head_warning = True
                self.show_message_at_position("Your head is tilted sideways,", self.text_id_straight_1, position={"x":-0.02, "y":0.46}, stay=2)
                self.show_message_at_position("try and look straight ahead!", self.text_id_straight_2, position={"x":-0.02, "y":0.40}, stay=2)
        elif (self.head_tilted_sideways_over_time.count(True)/self.timeseries_length) > 0.7:
            msg = str(90 - tilted_up_down) + "°"
            self.show_message_at_joint(msg, KINECT_JOINTS.Head.name)

            head_color = get_color_at_angle(90 - tilted_up_down, 0, 90 - self.tilted_up_down_head_min_warning_angle + 5, self.color_correct, self.color_wrong)
            self.set_head_color(head_color)

            if not self.showing_head_warning:
                self.showing_head_warning = True
                direction = "up" if self.joints[KINECT_JOINTS.Head.name][2] > self.joints[KINECT_JOINTS.Neck.name][2] else "down"
                self.show_message_at_position("Your head is tilted {},".format(direction), self.text_id_straight_1, position={"x":-0.02, "y":0.46}, stay=2)
                self.show_message_at_position("try and look straight ahead!", self.text_id_straight_2, position={"x":-0.02, "y":0.40}, stay=2)
        elif self.showing_head_warning:
            self.showing_head_warning = False
            self.hide_message_at_position(self.text_id_straight_1)
            self.hide_message_at_position(self.text_id_straight_2)
            self.hide_message_at_joint(KINECT_JOINTS.Head.name)
            self.set_head_color('')

    def set_head_color(self, color):
        self.change_joint_or_bone_color('joint', KINECT_BONES.Neck.name, color)
        self.change_joint_or_bone_color('joint', KINECT_BONES.Head.name, color)
        self.change_joint_or_bone_color('bone', KINECT_JOINTS.Head.name, color)

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
                 "stay": 10000,
                 "fade_out": 1}
            }))
        self.text_ids.add(joint)

    def hide_message_at_joint(self, joint):
        self.Messaging.send_message(MSG_TO_MIRROR_KEYS.TEXT.name,
            json.dumps({
                "text": "",
                "id": joint,
                "position": joint
            }))
        if joint in self.text_ids:
            self.text_ids.remove(joint)

    def show_message_at_position(self, text, id, position, stay=10000):
        self.Messaging.send_text_to_mirror(text, id=id, position=position, stay=stay, halign="right")
        self.text_ids.add(id)

    def hide_message_at_position(self, id):
        self.Messaging.hide_text_message(id)
        if id in self.text_ids:
            self.text_ids.remove(id)

    def change_joint_or_bone_color(self, type, name, color):
        if type =='joint':
            if color == '' and name in self.colored_joints:
                self.colored_joints.remove(name)
            elif color != '':
                self.colored_joints.add(name)
        elif type =='bone':
            if color == '' and name in self.colored_bones:
                self.colored_bones.remove(name)
            elif color != '':
                self.colored_bones.add(name)

        self.Messaging.send_message(MSG_TO_MIRROR_KEYS.CHANGE_SKELETON_COLOR.name,
            json.dumps({
                "type": type,
                "name": name,
                "color": color
            }))
