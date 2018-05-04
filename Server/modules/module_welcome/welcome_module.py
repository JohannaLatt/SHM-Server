from Server.modules.abstract_mirror_module import AbstractMirrorModule
from Server.utils.enums import MSG_TO_MIRROR_KEYS

import json


class WelcomeModule(AbstractMirrorModule):

    def __init__(self, Messaging):
        super().__init__(Messaging)

    def mirror_started(self):
        super().mirror_started()
        print("[WelcomeModule][info] Mirror is started")
        self.Messaging.send_message(
            MSG_TO_MIRROR_KEYS.STATIC_TEXT.name, json.dumps({"text": "Welcome!", "position": 1}))

    def tracking_started(self):
        super().tracking_started()
        # do nothing with that
        pass

    def tracking_data(self, data):
        super().tracking_data(data)
        # do nothing with that
        pass

    def tracking_lost(self):
        super().tracking_lost()
        # do nothing with that
        pass
