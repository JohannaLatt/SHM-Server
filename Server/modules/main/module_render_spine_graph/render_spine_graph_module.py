from Server.modules.abstract_main_module import AbstractMainModule

from Server.utils.enums import MSG_TO_MIRROR_KEYS
from Server.user import USER_STATE, EXERCISE

import json
import configparser


class RenderSpineGraphModule(AbstractMainModule):
    ''' Processing Module (ie uses preprocessed internal data) '''
    ''' Takes the spine-data from the preprocessed data and sends it to
        the mirror for rendering '''

    def __init__(self, Messaging, queue, User):
        super().__init__(Messaging, queue, User)
        self.graphs_shown = False

        # Config
        Config = configparser.ConfigParser()
        Config.read('././config/mirror_config.ini')

        self.joint_for_graph = Config.get('RenderSpineGraphModule', 'joint_for_graph', fallback='SpineBase')

    def user_skeleton_updated(self, user):
        super().user_skeleton_updated(user)

        if user.get_user_state() is USER_STATE.EXERCISING and user.get_exercise() is EXERCISE.SQUAT:
            # Send the spine data to the mirror
            joints = user.get_joints()
            spine_base = joints[self.joint_for_graph]

            self.Messaging.send_message(MSG_TO_MIRROR_KEYS.UPDATE_GRAPHS.name, json.dumps(spine_base))
            self.graphs_shown = True
        elif self.graphs_shown:
            self.Messaging.send_message(MSG_TO_MIRROR_KEYS.UPDATE_GRAPHS.name, json.dumps([]))
            self.graphs_shown = False

    def tracking_lost(self):
        super().tracking_lost()
        self.Messaging.send_message(MSG_TO_MIRROR_KEYS.UPDATE_GRAPHS.name, json.dumps([]))
        self.graphs_shown = False
