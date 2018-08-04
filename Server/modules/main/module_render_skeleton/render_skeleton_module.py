from Server.modules.abstract_main_module import AbstractMainModule
from Server.utils.enums import MSG_TO_MIRROR_KEYS

import json
from enum import Enum


class RenderSkeletonModule(AbstractMainModule):
    ''' Processing Module (ie uses preprocessed internal data) '''
    ''' Takes the preprocessed data and sends it to the mirror for rendering '''

    def user_skeleton_updated(self, user):
        super().user_skeleton_updated(user)

        # Send the user data to the mirror
        result = {'Joints': user.get_joints(), 'Bones': self.convert_keys(user.get_bones(), self.enum_names)}
        result_str = json.dumps(result)
        self.Messaging.send_message(MSG_TO_MIRROR_KEYS.RENDER_SKELETON.name, result_str)

    def tracking_lost(self):
        super().tracking_lost()
        self.Messaging.send_message(MSG_TO_MIRROR_KEYS.CLEAR_SKELETON.name, '')

    # https://stackoverflow.com/questions/43854335/encoding-python-enum-to-json#
    def convert_keys(self, obj, convert=str):
        if isinstance(obj, list):
            return [self.convert_keys(i, convert) for i in obj]
        if isinstance(obj, Enum):
            return obj.name
        if not isinstance(obj, dict):
            return obj
        return {convert(k): self.convert_keys(v, convert) for k, v in obj.items()}

    def enum_names(self, key):
        if isinstance(key, Enum):
            return key.name
        return str(key)
