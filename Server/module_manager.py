import configparser
import importlib
import threading


# Instantiate all modules from the config
def initiate_modules(Messaging):
    Config = configparser.ConfigParser()
    Config.read('./config/mirror_config.ini')
    module_config_names = Config.get('General', 'module_names').split(',')
    print("[ModuleManager][info] Module config names: %r" % module_config_names)
    for module_config_name in module_config_names:
        module_path = Config.get(module_config_name.strip(), 'path_name').strip()
        module_class = Config.get(module_config_name.strip(), 'class_name').strip()

        module = importlib.import_module('.modules.' + module_path, package='Server')
        class_ = getattr(module, module_class)

        # Instantiate class and run it on its own thread
        instance = class_(Messaging)
        module_thread = threading.Thread(target=instance.run)
        module_thread.daemon = True
        module_thread.start()
