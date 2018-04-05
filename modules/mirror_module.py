from abc import ABC, abstractmethod


class AbstractMirrorModule(ABC):

    @abstractmethod
    def __init__(self, mirror_messaging_thread):
        super().__init__()
        self.mirror_messaging_thread = mirror_messaging_thread

    @abstractmethod
    def mirror_started():
        pass

    @abstractmethod
    def mirror_tracking_started():
        pass

    @abstractmethod
    def mirror_tracking_data(data):
        pass

    @abstractmethod
    def mirror_tracking_lost():
        pass
