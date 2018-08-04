from Server.modules.abstract_mirror_module  import AbstractMirrorModule
from abc import abstractmethod


class AbstractPreprocessingModule(AbstractMirrorModule):

    def tracking_started(self):
        # By default, do nothing with it
        pass

    @abstractmethod
    def tracking_data(self, data):
        # Enforce implementation due to @abstractmethod-decorator
        pass

    def tracking_lost(self):
        # By default, do nothing with it
        pass
