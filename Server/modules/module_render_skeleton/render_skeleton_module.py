from Server.modules.abstract_mirror_module import AbstractMirrorModule


class RenderSkeletonModule(AbstractMirrorModule):

    def __init__(self, Messaging):
        super().__init__(Messaging)

    def mirror_started(self):
        # do nothing with that
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
