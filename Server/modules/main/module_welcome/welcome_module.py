from Server.modules.abstract_mirror_module import AbstractMirrorModule
from Server.utils.enums import MSG_TO_MIRROR_KEYS

import json


class WelcomeModule(AbstractMirrorModule):

    def mirror_started(self):
        super().mirror_started()
        print("[WelcomeModule][info] Mirror is started")
        self.Messaging.send_message(
            MSG_TO_MIRROR_KEYS.TEXT.name, json.dumps({
                                        "text": "Welcome!",
                                        "position": {"x": 0, "y": 0},
                                        "font_size": 47,
                                        "halign": "center",
                                        "id": "Welcome",
                                        "animation": {
                                            "fade_in": 1,
                                            "stay": 5,
                                            "fade_out": 3}
                                        }))

    def tracking_started(self):
        super().tracking_started()
        print("[WelcomeModule][info] Tracking")
        self.Messaging.send_message(
            MSG_TO_MIRROR_KEYS.TEXT.name, json.dumps({
                                        "text": "I can see you! :-)",
                                        "position": {"x": 0.5, "y": 0.9},
                                        "id": "Welcome",
                                        "animation": {
                                            "fade_in": 0.5,
                                            "stay": 1,
                                            "fade_out": 0.5}
                                        }))

    def tracking_lost(self):
        super().tracking_lost()
        print("[WelcomeModule][info] Tracking Lost")
        self.Messaging.send_message(
            MSG_TO_MIRROR_KEYS.TEXT.name, json.dumps({
                                        "text": "I lost you :-(",
                                        "position": {"x": 0.5, "y": 0.9},
                                        "id": "Welcome",
                                        "animation": {
                                            "fade_in": 0.5,
                                            "stay": 1,
                                            "fade_out": 0.5}
                                        }))
