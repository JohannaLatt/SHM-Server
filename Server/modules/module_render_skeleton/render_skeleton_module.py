from Server.modules.abstract_mirror_module import AbstractMirrorModule
from Server.utils.enums import MSG_TO_MIRROR_KEYS

import json


class RenderSkeletonModule(AbstractMirrorModule):

    def mirror_started(self):
        # do nothing with that
        pass

    def tracking_started(self):
        super().tracking_started()
        x = "mayve I need to do something"
        print('[RenderSkeletonModule][info] Tracking has started {}'.format(x))

    def tracking_data(self, data):
        super().tracking_data(data)
        # print('[RenderSkeletonModule][info] Tracking received: {}'.format(data))

        # Load string as json
        data = json.loads(data)["joint_data"]

        # Reformat the joint data into bone data to send for rendering
        result = []
        for joint, joint_data in data.items():
            from_p = joint_data["joint_position"]
            to_p = data[joint_data["joint_parent"]]["joint_position"]

            # Format for from a to b: [(ax, ay, az), (bx, by, bz)]
            from_to = []
            from_to.append((from_p["x"], from_p["y"], from_p["z"]))
            from_to.append((to_p["x"], to_p["y"], to_p["z"]))

            # Append to result
            result.append(from_to)

        result_str = json.dumps(result)
        self.Messaging.send_message(MSG_TO_MIRROR_KEYS.RENDER_SKELETON.name, result_str)

    def tracking_lost(self):
        super().tracking_lost()
        print('[RenderSkeletonModule][info] Tracking lost')
        self.Messaging.send_message(MSG_TO_MIRROR_KEYS.CLEAR_SKELETON.name, '')
