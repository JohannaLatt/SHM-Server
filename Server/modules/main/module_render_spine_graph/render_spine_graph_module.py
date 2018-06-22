from Server.modules.abstract_mirror_module import AbstractMirrorModule
from Server.utils.enums import MSG_TO_MIRROR_KEYS, KINECT_JOINTS
from Server.user import USER_STATE

import json


class RenderSpineGraphModule(AbstractMirrorModule):
    ''' Processing Module (ie uses preprocessed internal data) '''
    ''' Takes the spine-data from the preprocessed data and sends it to
        the mirror for rendering '''

    def __init__(self, Messaging, queue, User):
        super().__init__(Messaging, queue, User)
        self.graphs_shown = False

    def user_skeleton_updated(self, user):
        super().user_skeleton_updated(user)

        if user.get_user_state() is USER_STATE.SQUATTING:
            # Send the spine data to the mirror
            joints = user.get_joints()
            spine_base = joints[KINECT_JOINTS.SpineBase.name]

            self.Messaging.send_message(MSG_TO_MIRROR_KEYS.UPDATE_GRAPHS.name, json.dumps(spine_base))
            self.graphs_shown = True
        elif self.graphs_shown:
            self.Messaging.send_message(MSG_TO_MIRROR_KEYS.UPDATE_GRAPHS.name, json.dumps([]))
            self.graphs_shown = False
