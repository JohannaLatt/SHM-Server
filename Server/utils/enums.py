from enum import Enum


class MSG_FROM_MIRROR_KEYS(Enum):
    MIRROR_READY = 1
    MIRROR_TRACKING_STARTED = 2
    MIRROR_TRACKING_DATA = 3
    MIRROR_TRACKING_LOST = 4


class MSG_FROM_KINECT_KEYS(Enum):
    TRACKING_STARTED = 1
    TRACKING_DATA = 2
    TRACKING_LOST = 3


class MSG_FROM_INTERNAL(Enum):
    USER_SKELETON_UPDATED = 1
    USER_EXERCISING_UPDATED = 2


class MSG_TO_MIRROR_KEYS(Enum):
    TEXT = 1
    RENDER_SKELETON = 2
    CLEAR_SKELETON = 3
    CHANGE_SKELETON_COLOR = 4
    UPDATE_GRAPHS = 5


class KINECT_JOINTS(Enum):
    SpineBase = 1
    SpineMid = 2
    Neck = 3
    Head = 4
    ShoulderLeft = 5
    ElbowLeft = 6
    WristLeft = 7
    HandLeft = 8
    ShoulderRight = 9
    ElbowRight = 10
    WristRight = 11
    HandRight = 12
    HipLeft = 13
    KneeLeft = 14
    AnkleLeft = 15
    FootLeft = 16
    HipRight = 17
    KneeRight = 18
    AnkleRight = 19
    FootRight = 20
    SpineShoulder = 21
    HandTipLeft = 22
    ThumbLeft = 23
    HandTipRight = 24
    ThumbRight = 25

class KINECT_BONES(Enum):
    Head = 0
    Neck = 1
    SpineTop = 2
    SpineBottom = 3
    ClavicleLeft = 4
    UpperArmLeft = 5
    ForearmLeft = 6
    HandLeft = 7
    ClavicleRight = 8
    UpperArmRight = 9
    ForearmRight = 10
    HandRight = 11
    HipLeft = 12
    ThighLeft = 13
    ShinLeft = 14
    FootLeft = 15
    HipRight = 16
    ThighRight = 17
    ShinRight = 18
    FootRight = 19
