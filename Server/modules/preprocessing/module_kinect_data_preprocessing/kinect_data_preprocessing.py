from Server.modules.abstract_mirror_module import AbstractMirrorModule
from Server.utils.enums import MSG_TO_MIRROR_KEYS
from Server.utils.enums import MSG_FROM_INTERNAL
from Server.utils.mapping import KinectBoneMapping

import json


class KinectDataPreprocessing(AbstractMirrorModule):
    ''' Pre-processing Module (ie uses tracking data) '''
    ''' Takes the incoming tracking data from a Kinect-device
        and formats it according to the server's expected data model
        saved in the User-object: '''
    '''
    User.Joints:
        {
            'KneeLeft':         [ x, y ,z ],
            'ShoulderRight':    [ x, y ,z ]
        }
    User.Bones':
        {
            'ForearmLeft':  { Joints.ShoulderLeft, Joints.ElbowLeft },
            'ShinRight':    { Joints.HipRight, Joints.KneeRight }
        }
    '''

    def __init__(self, Messaging, queue, User):
        super().__init__(Messaging, queue, User)

        # Save the bone-mapping, we only have to do that once
        self.User.update_bones(KinectBoneMapping)

    def tracking_started(self):
        super().tracking_started()
        print('[KinectDataPreprocessing][info] Tracking has started')

    def tracking_data(self, data):
        super().tracking_data(data)

        # Load string as json
        data = json.loads(data)["joint_data"]

        # Reformat the joint data
        joints = {}
        for joint, joint_data in data.items():
            joints[joint] = [
                            joint_data["joint_position"]['x'],
                            joint_data["joint_position"]['y'],
                            joint_data["joint_position"]['z']
                            ]
        self.User.update_joints(joints)

    def tracking_lost(self):
        super().tracking_lost()
        print('[KinectDataPreprocessing][info] Tracking lost')
        self.Messaging.send_message(MSG_TO_MIRROR_KEYS.CLEAR_SKELETON.name, '')
