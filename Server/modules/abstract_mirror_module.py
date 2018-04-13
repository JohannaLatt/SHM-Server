from abc import ABC, abstractmethod


class AbstractMirrorModule(ABC):

    @abstractmethod
    def __init__(self, Messaging):
        super().__init__()
        self.Messaging = Messaging

    @abstractmethod
    def mirror_started(self):
        pass

    @abstractmethod
    def tracking_started(self):
        pass

    @abstractmethod
    def tracking_data(self, data):
        pass

    @abstractmethod
    def tracking_lost(self):
        pass
