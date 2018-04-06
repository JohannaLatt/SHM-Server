from abc import ABC, abstractmethod


class AbstractMirrorModule(ABC):

    @abstractmethod
    def __init__(self, mirror_messaging_thread):
        super().__init__()
        self.mirror_messaging_thread = mirror_messaging_thread

    @abstractmethod
    def mirror_started(self):
        pass

    @abstractmethod
    def mirror_tracking_started(self):
        pass

    @abstractmethod
    def mirror_tracking_data(self, data):
        pass

    @abstractmethod
    def mirror_tracking_lost(self):
        pass
