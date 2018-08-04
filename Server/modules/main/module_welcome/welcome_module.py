from Server.modules.abstract_main_module import AbstractMainModule

import threading


class WelcomeModule(AbstractMainModule):

    def __init__(self, Messaging, queue, User):
        super().__init__(Messaging, queue, User)

        self.remind_user_timer = None

    def mirror_started(self):
        super().mirror_started()
        print("[WelcomeModule][info] Mirror is started")
        self.Messaging.send_text_to_mirror("Welcome!", id="Welcome", position={"x": 0, "y": 0}, font_size=47, halign="center", fade_in = 1, stay=4, fade_out=1)

        if self.remind_user_timer is not None:
            self.remind_user_timer.cancel()
        self.remind_user_timer = threading.Timer(7, self.motivate_user)
        self.remind_user_timer.start()

    def tracking_started(self):
        super().tracking_started()
        print("[WelcomeModule][info] Tracking")
        if self.remind_user_timer is not None:
            self.remind_user_timer.cancel()
        self.Messaging.send_text_to_mirror("I can see you! :-)", id="Welcome", position={"x": 0, "y": 0.2}, font_size=38, halign="center", fade_in = 0.5, stay=1, fade_out=0.5)

    def tracking_data(self, data):
        super().tracking_data(data)
        if self.remind_user_timer is not None:
            self.remind_user_timer.cancel()

    def tracking_lost(self):
        super().tracking_lost()
        print("[WelcomeModule][info] Tracking Lost")
        if self.remind_user_timer is not None:
            self.remind_user_timer.cancel()
        self.remind_user_timer = threading.Timer(5, self.motivate_user)
        self.remind_user_timer.start()
        self.Messaging.send_text_to_mirror("I lost you :-(", id="Welcome", position={"x": 0, "y": 0.2}, font_size=38, halign="center", fade_in = 0.5, stay=1, fade_out=0.5)

    def motivate_user(self):
        self.Messaging.send_text_to_mirror("Step in front of the mirror to exercise!", id="Welcome", position={"x": 0, "y": 0}, font_size=47, halign="center", fade_in = .5, stay=3, fade_out=.5)
        self.remind_user_timer = threading.Timer(7, self.motivate_user)
        self.remind_user_timer.start()
