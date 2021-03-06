from abc import ABC
from datetime import datetime

from Server.utils.enums import MSG_FROM_MIRROR_KEYS
from Server.utils.enums import MSG_FROM_KINECT_KEYS
from Server.utils.enums import MSG_FROM_INTERNAL


class AbstractMirrorModule(ABC):

    def __init__(self, Messaging, queue, User):
        super().__init__()
        self.Messaging = Messaging
        self.__queue = queue
        self.User = User

        # The maximum allowed age of a message (in seconds) to still process it.
        # This is to avoid having slow modules work on outdated data and fall behind.
        self.max_msg_age = 1

    def mirror_started(self):
        # By default, do nothing with it
        pass

    def tracking_started(self):
        # By default, do nothing with it
        pass

    def tracking_data(self, data):
        # By default, do nothing with it
        pass

    def tracking_lost(self):
        # By default, do nothing with it
        pass

    def user_skeleton_updated(self, user):
        # By default, do nothing with it
        pass

    def user_state_updated(self, user):
        # By default, do nothing with it
        pass

    def user_exercise_updated(self, user):
        # By default, do nothing with it
        pass

    def user_exercise_stage_updated(self, user):
        # By default, do nothing with it
        pass

    def user_finished_repetition(self, user):
        # By default, do nothing with it
        pass

    def run(self):
        while True:
            item = self.__queue.get()

            if item is None or (datetime.now() - item.timestamp).total_seconds() > self.max_msg_age:
                self.__queue.task_done()
                continue

            if item.key == MSG_FROM_MIRROR_KEYS.MIRROR_READY.name:
                self.mirror_started()
            elif item.key == MSG_FROM_KINECT_KEYS.TRACKING_STARTED.name:
                self.tracking_started()
            elif item.key == MSG_FROM_KINECT_KEYS.TRACKING_DATA.name:
                self.tracking_data(item.body)
            elif item.key == MSG_FROM_KINECT_KEYS.TRACKING_LOST.name:
                self.tracking_lost()
            elif item.key == MSG_FROM_INTERNAL.USER_SKELETON_UPDATED.name:
                self.user_skeleton_updated(self.User)
            elif item.key == MSG_FROM_INTERNAL.USER_STATE_UPDATED.name:
                self.user_state_updated(self.User)
            elif item.key == MSG_FROM_INTERNAL.USER_EXERCISE_UPDATED.name:
                self.user_exercise_updated(self.User)
            elif item.key == MSG_FROM_INTERNAL.USER_EXERCISE_STAGE_UPDATED.name:
                self.user_exercise_stage_updated(self.User)
            elif item.key == MSG_FROM_INTERNAL.USER_REPETITION_FINISHED.name:
                self.user_finished_repetition(self.User)

            self.__queue.task_done()
