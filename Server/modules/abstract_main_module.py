from Server.modules.abstract_mirror_module import AbstractMirrorModule


class AbstractMainModule(AbstractMirrorModule):

    def mirror_started(self):
        # By default, do nothing with it
        pass

    def user_skeleton_updated(self, user):
        # By default, do nothing with it
        pass

    def user_state_updated(self, user):
        # By default, do nothing with it
        pass

    def user_exercise_updated(self, user):
        # By default, do nothing with it
        pass

    def user_exercise_stage_updated(self, user):
        # By default, do nothing with it
        pass

    def user_finished_repetition(self, user):
        # By default, do nothing with it
        pass
