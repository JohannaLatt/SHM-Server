from enum import Enum
from Server.utils.read_write_lock import ReadWriteLock


class USER_STATE(Enum):
    NONE = 1
    SQUATTING = 2


class SQUAT_STAGE(Enum):
    NONE = 1
    GOING_DOWN = 2
    GOING_UP = 3


class User():

    def __init__(self):
        self.state = USER_STATE.NONE
        self.exercise_stage = SQUAT_STAGE.NONE
        self.bones = {}
        self.joints = {}

        # Obtain a lock that has to be used to change the user
        self.lock = ReadWriteLock()

    def update_user_state(self, state):
        self.lock.acquire_write()
        self.state = state
        self.lock.release_write()

    def update_exercise_state(self, exercise_stage):
        self.lock.acquire_write()
        self.exercise_stage = exercise_stage
        self.lock.release_write()

    def update_bones(self, bones):
        self.lock.acquire_write()
        self.bones = bones
        self.lock.release_write()

    def update_joints(self, joints):
        self.lock.acquire_write()
        self.joints = joints
        self.lock.release_write()

    def get_user_state(self):
        self.lock.acquire_read()
        result = self.state
        self.lock.release_read()
        return result

    def get_exercise_stage(self):
        self.lock.acquire_read()
        result = self.exercise_stage
        self.lock.release_read()
        return result

    def get_bones(self):
        self.lock.acquire_read()
        result = self.bones
        self.lock.release_read()
        return result

    def get_joints(self):
        self.lock.acquire_read()
        result = self.joints
        self.lock.release_read()
        return result
