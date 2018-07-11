from Server.modules.abstract_mirror_module import AbstractMirrorModule
from Server.utils.enums import MSG_TO_MIRROR_KEYS

import json
import threading


class WelcomeModule(AbstractMirrorModule):

    def mirror_started(self):
        super().mirror_started()
        print("[WelcomeModule][info] Mirror is started")
        self.Messaging.send_text_to_mirror("Welcome!", id="Welcome", position={"x": 0, "y": 0}, font_size=47, halign="center", fade_in = 1, stay=5, fade_out=2)
        self.Messaging.send_text_to_mirror("Step in front of the mirror to exercise", position={"x": 0, "y": -0.07}, font_size=38, halign="center", fade_in = 1, stay=5, fade_out=2)

        self.remind_user_timer = threading.Timer(7, self.motivate_user)
        self.remind_user_timer.start()

    def tracking_started(self):
        super().tracking_started()
        print("[WelcomeModule][info] Tracking")
        self.remind_user_timer.cancel()
        self.Messaging.send_text_to_mirror("I can see you! :-)", id="Welcome", position={"x": 0, "y": 0.2}, font_size=38, halign="center", fade_in = 0.5, stay=1, fade_out=0.5)

    def tracking_lost(self):
        super().tracking_lost()
        print("[WelcomeModule][info] Tracking Lost")
        self.remind_user_timer = threading.Timer(5, self.motivate_user)
        self.remind_user_timer.start()
        self.Messaging.send_text_to_mirror("I lost you :-(", id="Welcome", position={"x": 0, "y": 0.2}, font_size=38, halign="center", fade_in = 0.5, stay=1, fade_out=0.5)

    def motivate_user(self):
        self.Messaging.send_text_to_mirror("Step in front of the mirror to exercise!", id="Welcome", position={"x": 0, "y": 0}, font_size=47, halign="center", fade_in = .5, stay=3, fade_out=.5)
        self.remind_user_timer = threading.Timer(7, self.motivate_user)
        self.remind_user_timer.start()
