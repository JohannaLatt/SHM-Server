import configparser
import importlib
import threading
import queue

from Server.utils.user import User


# Instantiate all modules from the config
class ModuleManager():

    def __init__(self, Messaging):
        self.__module_queues = []
        self.messaging = Messaging

        # Saves the user data during a workout
        self.User = User()

        Config = configparser.ConfigParser()
        Config.read('./config/mirror_config.ini')
        module_config_names = Config.get('General', 'module_names').split(',')
        print("[ModuleManager][info] Initializing modules from config: %r" % module_config_names)

        for module_config_name in module_config_names:
            module_path = Config.get(module_config_name.strip(), 'path_name').strip()
            module_class = Config.get(module_config_name.strip(), 'class_name').strip()

            module = importlib.import_module('.modules.' + module_path, package='Server')
            class_ = getattr(module, module_class)

            # Instantiate class and run it on its own thread and with its own messaging queue
            module_queue = queue.Queue()
            self.__module_queues.append(module_queue)
            instance = class_(Messaging, module_queue, self.User)
            module_thread = threading.Thread(target=instance.run)
            module_thread.daemon = True
            module_thread.start()

        # Continuously listen for messages in the Messaging-module and distribute those to the modules
        listen_to_messages_thread = threading.Thread(target=self.run)
        listen_to_messages_thread.daemon = True
        listen_to_messages_thread.start()

    def run(self):
        while True:
            item = self.messaging.mirror_msg_queue.get()

            if item is None:
                continue

            for module_queue in self.__module_queues:
                module_queue.put(item)

            self.messaging.mirror_msg_queue.task_done()
