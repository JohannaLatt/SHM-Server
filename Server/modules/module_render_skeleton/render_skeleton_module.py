from Server.modules.abstract_mirror_module import AbstractMirrorModule
from Server.utils.enums import MSG_TO_MIRROR_KEYS
from Server.utils.mapping import KinectBoneMapping

import json


class RenderSkeletonModule(AbstractMirrorModule):

    def mirror_started(self):
        # do nothing with that
        pass

    def tracking_started(self):
        super().tracking_started()
        print('[RenderSkeletonModule][info] Tracking has started')

    def tracking_data(self, data):
        super().tracking_data(data)
        # print('[RenderSkeletonModule][info] Tracking received: {}'.format(data))

        # Load string as json
        data = json.loads(data)["joint_data"]

        # Reformat the joint data into bone and joint data to send for rendering
        """ Data Structure sent to mirror """
        """
        {
          'Joints':
                {
                'KneeLeft':         [ x, y ,z ],
                'ShoulderRight':    [ x, y ,z ]
           },
          'Bones':
                {
                'ForearmLeft':  { Joints.ShoulderLeft, Joints.ElbowLeft },
                'ShinRight':    { Joints.HipRight, Joints.KneeRight }
            }
        }
        """

        # Joints
        result = {'Joints': {}, 'Bones': {}}
        for joint, joint_data in data.items():
            result['Joints'][joint] = [
                                        joint_data["joint_position"]['x'],
                                        joint_data["joint_position"]['y'],
                                        joint_data["joint_position"]['z']
                                       ]

        # Bones
        result['Bones'] = KinectBoneMapping

        result_str = json.dumps(result)
        self.Messaging.send_message(MSG_TO_MIRROR_KEYS.RENDER_SKELETON.name, result_str)

    def tracking_lost(self):
        super().tracking_lost()
        print('[RenderSkeletonModule][info] Tracking lost')
        self.Messaging.send_message(MSG_TO_MIRROR_KEYS.CLEAR_SKELETON.name, '')
