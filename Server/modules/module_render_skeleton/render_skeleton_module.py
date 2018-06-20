from Server.modules.abstract_mirror_module import AbstractMirrorModule
from Server.utils.enums import MSG_TO_MIRROR_KEYS

import json


class RenderSkeletonModule(AbstractMirrorModule):
    ''' Processing Module (ie uses preprocessed internal data) '''
    ''' Takes the preprocessed data and sends it to the mirror for rendering '''

    def user_updated(self, user):
        super().user_updated(user)

        # Send the user data to the mirror
        result = {'Joints': user.get_joints(), 'Bones': user.get_bones()}
        result_str = json.dumps(result)

        self.Messaging.send_message(MSG_TO_MIRROR_KEYS.RENDER_SKELETON.name, result_str)

    def tracking_lost(self):
        super().tracking_lost()
        self.Messaging.send_message(MSG_TO_MIRROR_KEYS.CLEAR_SKELETON.name, '')
