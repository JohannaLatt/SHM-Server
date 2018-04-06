import AbstractMirrorModule


class WelcomeModule(AbstractMirrorModule):

    def __init__(self, mirror_messaging_thread):
        super().__init__(self, mirror_messaging_thread)

    def saySomething(self, string):
        print(string)

    def mirror_started(self):
        super().mirror_started()
        welcome_msg = {'type': 'text', 'location': 'center', 'text': 'Welcome!', 'duration': 5}
        self.mirror_messaging_thread.send(welcome_msg)
        pass

    def mirror_tracking_started(self):
        super().mirror_tracking_started()
        # do nothing with that
        pass

    def mirror_tracking_data(self, data):
        super().mirror_tracking_data()
        # do nothing with that
        pass

    def mirror_tracking_lost(self):
        super.mirror_tracking_lost()
        # do nothing with that
        pass
