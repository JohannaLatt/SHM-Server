from Server.modules.abstract_mirror_module import AbstractMirrorModule


class WelcomeModule(AbstractMirrorModule):

    def __init__(self, Messaging):
        super().__init__(Messaging)

    def mirror_started(self):
        super().mirror_started()
        # welcome_msg = {'type': 'text', 'location': 'center', 'text': 'Welcome!', 'duration': 5}
        # print("YES")
        self.Messaging.send_message('TEXT', 'Server has receive the start-up message!')
        pass

    def mirror_tracking_started(self):
        super().mirror_tracking_started()
        # do nothing with that
        pass

    def mirror_tracking_data(self, data):
        super().mirror_tracking_data(data)
        # do nothing with that
        pass

    def mirror_tracking_lost(self):
        super.mirror_tracking_lost()
        # do nothing with that
        pass
