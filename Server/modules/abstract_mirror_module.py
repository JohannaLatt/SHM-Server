from abc import ABC, abstractmethod

from Server.utils.enums import MSG_FROM_MIRROR_KEYS
from Server.utils.enums import MSG_FROM_KINECT_KEYS


class AbstractMirrorModule(ABC):

    def __init__(self, Messaging, queue):
        super().__init__()
        self.Messaging = Messaging
        self.__queue = queue

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

    def run(self):
        while True:
            item = self.__queue.get()

            if item is None:
                continue

            if item.key == MSG_FROM_MIRROR_KEYS.MIRROR_READY.name:
                self.mirror_started()
            elif item.key == MSG_FROM_KINECT_KEYS.TRACKING_STARTED.name:
                self.tracking_started()
            elif item.key == MSG_FROM_KINECT_KEYS.TRACKING_DATA.name:
                self.tracking_data(item.body)
            elif item.key == MSG_FROM_KINECT_KEYS.TRACKING_LOST.name:
                self.tracking_lost()

            self.__queue.task_done()
