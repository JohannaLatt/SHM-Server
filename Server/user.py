from Server.utils.enums import MSG_FROM_INTERNAL, USER_JOINTS

from enum import Enum
from Server.utils.read_write_lock import ReadWriteLock


class USER_STATE(Enum):
    NONE = 1
    READY_TO_EXERCISE = 3
    EXERCISING = 2


class EXERCISE(Enum):
    NONE = 1
    SQUAT = 2
    BICEPS_CURL = 3


class UP_DOWN_EXERCISE_STAGE(Enum):
    NONE = 1
    GOING_DOWN = 2
    GOING_UP = 3


class User():

    def __init__(self, Messaging):
        self.Messaging = Messaging

        self.expected_joints = [j.name for j in USER_JOINTS]

        self.state = USER_STATE.NONE
        self.exercise = EXERCISE.NONE
        self.exercise_stage = UP_DOWN_EXERCISE_STAGE.NONE
        self.bones = {}
        self.joints = {}

        self.repetitions = 0

        # Obtain a lock that has to be used to change the user
        self.lock = ReadWriteLock()

    def update_state(self, state):
        if state is self.state:
            return

        if state is USER_STATE.NONE or state is USER_STATE.READY_TO_EXERCISE:
            self.update_exercise(EXERCISE.NONE)
            self.update_exercise_stage(UP_DOWN_EXERCISE_STAGE.NONE)

        if state is not USER_STATE.NONE:
            # Only reset the repetitions once a new exercise starts, in case
            # the repetitions of the last exercise are of interest for a module
            self.__set_repetitions(0)

        self.lock.acquire_write()
        self.state = state
        self.lock.release_write()
        self.Messaging.consume_internal_message(
            MSG_FROM_INTERNAL.USER_STATE_UPDATED.name)

    def update_exercise(self, exercise):
        if exercise is not EXERCISE.NONE:
            self.update_state(USER_STATE.EXERCISING)

            if exercise is not self.exercise:
                self.__set_repetitions(0)

        self.lock.acquire_write()
        self.exercise = exercise
        self.lock.release_write()
        self.Messaging.consume_internal_message(
            MSG_FROM_INTERNAL.USER_EXERCISE_UPDATED.name)

    def update_exercise_stage(self, exercise_stage):
        self.lock.acquire_write()
        self.exercise_stage = exercise_stage
        self.lock.release_write()
        self.Messaging.consume_internal_message(
            MSG_FROM_INTERNAL.USER_EXERCISE_STAGE_UPDATED.name)

    def update_bones(self, bones):
        self.lock.acquire_write()
        self.bones = bones
        self.lock.release_write()
        # No need to notify the modules since this only happens once

    def update_joints(self, joints):
        self.lock.acquire_write()
        self.joints = joints
        self.lock.release_write()
        self.Messaging.consume_internal_message(
            MSG_FROM_INTERNAL.USER_SKELETON_UPDATED.name)

    def __set_repetitions(self, repetitions):
        self.lock.acquire_write()
        self.repetitions = repetitions
        self.lock.release_write()

    def user_finished_repetition(self):
        self.lock.acquire_write()
        self.repetitions += 1
        self.lock.release_write()
        self.Messaging.consume_internal_message(
            MSG_FROM_INTERNAL.USER_REPETITION_FINISHED.name)

    def get_user_state(self):
        self.lock.acquire_read()
        result = self.state
        self.lock.release_read()
        return result

    def get_exercise(self):
        self.lock.acquire_read()
        result = self.exercise
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

    def get_current_repetitions(self):
        self.lock.acquire_read()
        result = self.repetitions
        self.lock.release_read()
        return result
