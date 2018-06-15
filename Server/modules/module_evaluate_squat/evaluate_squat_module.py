from Server.modules.abstract_mirror_module import AbstractMirrorModule

from Server.utils.user import USER_STATE
from Server.utils.enums import MSG_TO_MIRROR_KEYS

import json
from numpy import (dot, arccos, linalg, clip, degrees)
import numpy as np


class EvaluateSquatModule(AbstractMirrorModule):

    def __init__(self, Messaging, queue, User):
        super().__init__(Messaging, queue, User)
        self.evaluating = False

    def mirror_started(self):
        super().mirror_started()
        # do nothing with that
        pass

    def tracking_started(self):
        super().tracking_started()
        # do nothing with that
        pass

    def tracking_data(self, data):
        super().tracking_data(data)

        # Check if the user is currently doing a squat
        if self.User.get_user_state() is USER_STATE.SQUATTING:
            self.evaluating = True

            self.joints = self.User.get_joints()
            self.bones = self.User.get_bones()

            # Calculate the angle between the thigh and shin
            thigh_vector = self.get_vector_of_bone("ThighRight")
            shin_vector = self.get_vector_of_bone("ShinRight")
            knee_angle = np.around(self.angle_between(thigh_vector, shin_vector), decimals=1)
            self.show_message_at_joint(knee_angle, "KneeRight")

            thigh_vector = self.get_vector_of_bone("ThighLeft")
            shin_vector = self.get_vector_of_bone("ShinLeft")
            knee_angle = np.around(self.angle_between(thigh_vector, shin_vector), decimals=1)
            self.show_message_at_joint(knee_angle, "KneeLeft")
        elif self.evaluating:
            self.clean_UI()

    def tracking_lost(self):
        super().tracking_lost()
        self.clean_UI()

    def clean_UI(self):
        self.hide_message_at_joint("KneeRight")
        self.hide_message_at_joint("KneeLeft")
        self.evaluating = False

    def get_vector_of_bone(self, bone):
        return (self.joints[self.bones[bone][0]][0] - self.joints[self.bones[bone][1]][0], # x
                self.joints[self.bones[bone][0]][1] - self.joints[self.bones[bone][1]][1]) # y

    def unit_vector(self, vector):
        """ Returns the unit vector of the vector.  """
        return vector / linalg.norm(vector)

    def angle_between(self, v1, v2):
        """ Returns the angle in degrees between vectors 'v1' and 'v2' """
        v1_u = self.unit_vector(v1)
        v2_u = self.unit_vector(v2)
        return degrees(arccos(clip(dot(v1_u, v2_u), -1.0, 1.0)))

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
