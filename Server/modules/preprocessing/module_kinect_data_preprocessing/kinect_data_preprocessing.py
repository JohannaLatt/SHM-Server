from Server.modules.abstract_preprocessing_module import AbstractPreprocessingModule
from Server.utils.mapping import KinectBoneMapping
from Server.utils.enums import KINECT_JOINTS

import json


class KinectDataPreprocessing(AbstractPreprocessingModule):
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
        data = json.loads(data)

        # Remove "ThumbRight", "ThumbLeft", "HandTipRight" and "HandTipLeft"
        # since they are not expected by the User-object
        del data[KINECT_JOINTS.HandTipLeft.name]
        del data[KINECT_JOINTS.HandTipRight.name]
        del data[KINECT_JOINTS.ThumbLeft.name]
        del data[KINECT_JOINTS.ThumbRight.name]

        super().update_user_joints(data)
