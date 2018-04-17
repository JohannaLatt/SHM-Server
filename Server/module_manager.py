import configparser
import importlib

# Instantiate all modules from the config
modules = []


def initiate_modules(Messaging):
    Config = configparser.ConfigParser()
    Config.read('./config/mirror_config.ini')
    module_config_names = Config.get('General', 'module_names').split(',')
    print("[ModuleManager][info] Module config names: %r" % module_config_names)
    for module_config_name in module_config_names:
        module_path = Config.get(module_config_name.strip(), 'path_name').strip()
        module_class = Config.get(module_config_name.strip(), 'class_name').strip()
        # print("Initiating %r at %r\n" % (module_class, module_path))

        module = importlib.import_module('.modules.' + module_path, package='Server')
        class_ = getattr(module, module_class)
        # print(class_)
        instance = class_(Messaging)
        modules.append(instance)
