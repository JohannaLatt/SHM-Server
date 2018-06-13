from Server.modules.abstract_mirror_module import AbstractMirrorModule

from Server.utils.user import USER_STATE
from Server.utils.user import SQUAT_STAGE


class EvaluateSquatModule(AbstractMirrorModule):

    def mirror_started(self):
        super().mirror_started()
        # do nothing with that
        pass

    def tracking_started(self):
        super().tracking_started()
        # do nothing with that
        pass

    def tracking_data(self, data):
        super().tracking_data(data)
        '''
        # Check if the user is currently doing a squat
        if self.User.get_user_state() is USER_STATE.SQUATTING:
            print("Now I can evaluate the squat")
            text = "down"
            if self.User.get_exercise_stage() is SQUAT_STAGE.GOING_UP:
                text = "up"
            print("User is going {}".format(text))
        else:
            print("Now I can't.........")
            '''

    def tracking_lost(self):
        super().tracking_lost()
        # do nothing with that
        pass
