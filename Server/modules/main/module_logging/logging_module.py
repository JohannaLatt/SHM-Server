from Server.modules.abstract_mirror_module import AbstractMirrorModule

import logging
from logging.handlers import RotatingFileHandler
import datetime
import os

max_number_of_log_files = 20


class LoggingModule(AbstractMirrorModule):

    def __init__(self, Messaging, queue, User):
        super().__init__(Messaging, queue, User)

        self.delete_old_log_files()

        self.raw_tracking_data_logger = logging.getLogger('Smart-Health-Mirror-Raw-Data')

        now = datetime.datetime.now()
        filename = "logs/{}_raw_tracking_data.log".format(now.strftime('%Y_%m_%d-%H_%M_%S'))
        hdlr = RotatingFileHandler(filename, maxBytes=5*1024*1024)  # max 5 MB

        formatter = logging.Formatter('%(message)s')
        hdlr.setFormatter(formatter)

        self.raw_tracking_data_logger.addHandler(hdlr)

    def user_skeleton_updated(self, user):
        super().user_skeleton_updated(user)
        self.raw_tracking_data_logger.error(user.get_joints())

    def delete_old_log_files(self):
        files = os.listdir('logs/')

        # Filter out hidden files from the system
        files = [x for x in files if not x.startswith(".")]

        if len(files) > (max_number_of_log_files - 1):
            files.sort()   # Oldest will be first
            print("range is 0 to {}".format(len(files) - max_number_of_log_files + 1))
            for i in range(0, (len(files) - max_number_of_log_files + 1)):
                f = os.path.join('logs/', files[i])
                os.remove(f)
