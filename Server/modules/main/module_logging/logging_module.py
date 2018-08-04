from Server.modules.abstract_main_module import AbstractMainModule

import logging
from logging.handlers import RotatingFileHandler
import datetime
import os
import json

max_number_of_log_files = 20


class LoggingModule(AbstractMainModule):

    def __init__(self, Messaging, queue, User):
        super().__init__(Messaging, queue, User)

        self.delete_old_log_files()

        self.raw_tracking_data_logger = logging.getLogger('Smart-Health-Mirror-Raw-Data')

        now = datetime.datetime.now()
        filename = "logs/{}_raw_tracking_data.log".format(now.strftime('%Y_%m_%d-%H_%M_%S'))
        hdlr = RotatingFileHandler(filename, maxBytes=5*1024*1024, backupCount=1)  # max 5 MB

        formatter = logging.Formatter('%(message)s')
        hdlr.setFormatter(formatter)

        self.raw_tracking_data_logger.addHandler(hdlr)

    def user_skeleton_updated(self, user):
        super().user_skeleton_updated(user)
        self.raw_tracking_data_logger.error(json.dumps(user.get_joints()))

    def delete_old_log_files(self):
        files = os.listdir('logs/')

        # Filter out hidden files from the system
        files = [x for x in files if not x.startswith(".")]

        if len(files) > (max_number_of_log_files - 1):
            files.sort()   # Oldest will be first
            for i in range(0, (len(files) - max_number_of_log_files + 1)):
                f = os.path.join('logs/', files[i])
                os.remove(f)
