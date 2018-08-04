from Server.modules.abstract_mirror_module import AbstractMirrorModule
from abc import abstractmethod

import numpy as np


class AbstractPreprocessingModule(AbstractMirrorModule):

    data_format_checked = False
    data_format_correct = False

    def tracking_started(self):
        # By default, do nothing with it
        pass

    @abstractmethod
    def tracking_data(self, data):
        # Enforce implementation due to @abstractmethod-decorator
        pass

    def tracking_lost(self):
        # By default, do nothing with it
        pass

    def update_user_joints(self, data):
        if not self.data_format_checked:
            # Check whether the provided joint data equals the expected joint data
            if np.array_equal(self.User.expected_joints, list(data.keys())):
                self.data_format_correct = True
            else:
                print("[AbstractPreprocessingModule][Error] The currently used preprocessing tool does not produce the expected joints - the data is not propagated!")
            self.data_format_checked = True

        if self.data_format_checked and self.data_format_correct:
            self.User.update_joints(data)
