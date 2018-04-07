from enum import Enum

class MSG_FROM_MIRROR_KEYS(Enum):
    MIRROR_READY = 1
    MIRROR_TRACKING_STARTED = 2
    MIRROR_TRACKING_DATA = 3
    MIRROR_TRACKING_LOST = 4


class MSG_TO_MIRROR_KEYS(Enum):
    TEXT = 1
