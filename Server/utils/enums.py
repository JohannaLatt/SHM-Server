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


class MSG_TO_MIRROR_KEYS(Enum):
    TEXT = 1
    RENDER_SKELETON = 2
    CLEAR_SKELETON = 3


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
