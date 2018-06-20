from Server.modules.abstract_mirror_module import AbstractMirrorModule


class Logging(AbstractMirrorModule):

    def mirror_started(self):
        super().mirror_started()
        pass

    def tracking_started(self):
        super().tracking_started()
        pass

    def tracking_data(self, data):
        super().tracking_data(data)
        # do nothing with that
        pass

    def tracking_lost(self):
        pass
