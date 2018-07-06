from Server.utils.enums import KINECT_JOINTS, KINECT_BONES

KinectBoneMapping = {
    KINECT_BONES.Head: [KINECT_JOINTS.Neck, KINECT_JOINTS.Head],
    KINECT_BONES.Neck: [KINECT_JOINTS.SpineShoulder, KINECT_JOINTS.Neck],
    KINECT_BONES.SpineTop: [KINECT_JOINTS.SpineMid, KINECT_JOINTS.SpineShoulder],
    KINECT_BONES.SpineBottom: [KINECT_JOINTS.SpineBase, KINECT_JOINTS.SpineMid],
    KINECT_BONES.ClavicleLeft: [KINECT_JOINTS.SpineShoulder, KINECT_JOINTS.ShoulderLeft],
    KINECT_BONES.UpperArmLeft: [KINECT_JOINTS.ShoulderLeft, KINECT_JOINTS.ElbowLeft],
    KINECT_BONES.ForearmLeft: [KINECT_JOINTS.ElbowLeft, KINECT_JOINTS.WristLeft],
    KINECT_BONES.HandLeft: [KINECT_JOINTS.WristLeft, KINECT_JOINTS.HandLeft],
    KINECT_BONES.ClavicleRight: [KINECT_JOINTS.SpineShoulder, KINECT_JOINTS.ShoulderRight],
    KINECT_BONES.UpperArmRight: [KINECT_JOINTS.ShoulderRight, KINECT_JOINTS.ElbowRight],
    KINECT_BONES.ForearmRight: [KINECT_JOINTS.ElbowRight, KINECT_JOINTS.WristRight],
    KINECT_BONES.HandRight: [KINECT_JOINTS.WristRight, KINECT_JOINTS.HandRight],
    KINECT_BONES.HipLeft: [KINECT_JOINTS.SpineBase, KINECT_JOINTS.HipLeft],
    KINECT_BONES.ThighLeft: [KINECT_JOINTS.HipLeft, KINECT_JOINTS.KneeLeft],
    KINECT_BONES.ShinLeft: [KINECT_JOINTS.KneeLeft, KINECT_JOINTS.AnkleLeft],
    KINECT_BONES.FootLeft: [KINECT_JOINTS.AnkleLeft, KINECT_JOINTS.FootLeft],
    KINECT_BONES.HipRight: [KINECT_JOINTS.SpineBase, KINECT_JOINTS.HipRight],
    KINECT_BONES.ThighRight: [KINECT_JOINTS.HipRight, KINECT_JOINTS.KneeRight],
    KINECT_BONES.ShinRight: [KINECT_JOINTS.KneeRight, KINECT_JOINTS.AnkleRight],
    KINECT_BONES.FootRight: [KINECT_JOINTS.AnkleRight, KINECT_JOINTS.FootRight]
}
