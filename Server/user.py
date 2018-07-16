from Server.utils.enums import MSG_FROM_INTERNAL

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

        self.state = USER_STATE.NONE
        self.exercise = EXERCISE.NONE
        self.exercise_stage = UP_DOWN_EXERCISE_STAGE.NONE
        self.bones = {}
        self.joints = {}

        self.repetitions = 0

        # Obtain a lock that has to be used to change the user
        self.lock = ReadWriteLock()

    def update_user_excercise(self, state, exercise, exercise_stage):
        if state is USER_STATE.NONE:
            self.repetitions = 0

        if exercise != self.exercise:
            self.repetitions = 0

        self.lock.acquire_write()
        self.state = state
        self.exercise = exercise
        self.exercise_stage = exercise_stage
        self.lock.release_write()
        self.Messaging.consume_internal_message(
            MSG_FROM_INTERNAL.USER_EXERCISING_UPDATED.name)

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

    def user_finished_repetition(self):
        self.repetitions += 1
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
        return self.repetitions
