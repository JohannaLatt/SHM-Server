from Server.modules.abstract_mirror_module import AbstractMirrorModule


class WelcomeModule(AbstractMirrorModule):

    def __init__(self):
        super().__init__()

    def saySomething(self, string):
        print(string)

    def mirror_started(self):
        super().mirror_started()
        welcome_msg = {'type': 'text', 'location': 'center', 'text': 'Welcome!', 'duration': 5}
        print("YES")
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
